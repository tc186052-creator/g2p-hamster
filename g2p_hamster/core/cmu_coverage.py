# -*- coding: utf-8 -*-
"""cmu_coverage.py — đo coverage CMUdict trên token route=en của corpus IR 1M (fase C).

KỶ LUẬT ĐẾM (giống build_core_domain — R61-01): ĐƠN VỊ = TOKEN NGUYÊN DẠNG
(cat=word, route=en; NFC + lower + strip; KHÔNG tách, KHÔNG sinh mảnh). Token
rỗng sau strip bị loại và ĐẾM RÕ vào `n_empty` (không âm thầm). Mỗi unique token
đếm 1 dòng trong TSV kèm tần suất literal + cờ in_cmu (tra exact key cmu_en).

Phân loại lý do trượt (hậu kiểm v16 C16-02 — tách ASCII a-z khỏi Unicode
alphabetic, vì LETTER_NAMES chỉ phủ a-z nên KHÔNG phải alphabetic OOV nào
cũng spell trọn token; phân loại qua classify_miss để test được):
  has_digit          — có chữ số
  ascii_alpha_oov    — thuần a-z (spell TRỌN token bằng tên chữ)
  unicode_alpha_oov  — isalpha nhưng có ký tự ngoài a-z (chỉ những chữ có tên
                       mới được spell; ký tự còn lại vào unsupported_chars)
  not_alpha          — còn lại (dấu, ký tự đặc biệt…)

CONTENT-PIN corpus (C16-02.3): sha256 file corpus được TÍNH tại mỗi lần chạy
(stream) và đối chiếu pin đã khai trong core_domain_provenance.json — lệch →
SystemExit; hash đã kiểm + nguồn pin ghi tường minh vào provenance coverage.

NHÃN KẾT QUẢ: in_cmu = "dictionary hit" (exact key), KHÔNG đồng nghĩa phát âm
hoàn tất — hit gồm cả entry no_nucleus (shh, mm, hmm… API trả no_nucleus).
Số "spell-complete" riêng được đếm cho nhóm OOV: chỉ ascii_alpha_oov đảm bảo
spell trọn token.

Output (pin, tái lập được):
  02_data/en_branch/en_coverage.tsv            token<TAB>freq<TAB>in_cmu
  02_data/en_branch/en_coverage_provenance.json (nguồn, sha, phương pháp, hash)

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/cmu_coverage.py
"""
import gzip
import hashlib
import json
import sys
import unicodedata as U
from collections import Counter
from datetime import date
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from g2p_hamster.core import cmu_en as C  # noqa: E402

ROOT = HERE.parent
CORPUS = Path(os.environ.get("G2P_CORPUS_DIR", "/nonexistent") + "/"
              "01_data/silver/corpus_ir_1M.jsonl.gz")
CORPUS_PIN_FILE = ROOT / "02_data" / "core_domain" / "core_domain_provenance.json"
OUT_DIR = ROOT / "02_data" / "en_branch"
CORPUS_TAG = ("tier1_silver_1M chính (stats_1M.json: 1.000.000 records, "
              "22.723.901 tokens) — nguồn attestation duy nhất đã verify; "
              "supplement bị LOẠI như build_core_domain")


def norm_token(t):
    return U.normalize("NFC", t.strip().lower())


def sha256_stream(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def classify_miss(w):
    """Token OOV (đã qua norm_token) → một trong: has_digit / ascii_alpha_oov /
    unicode_alpha_oov / not_alpha. ASCII a–z tách RIÊNG vì chỉ nhóm này spell
    trọn token bằng LETTER_NAMES (hậu kiểm v16 C16-02)."""
    if any(ch.isdigit() for ch in w):
        return "has_digit"
    if w.isalpha():
        if all("a" <= ch <= "z" for ch in w):
            return "ascii_alpha_oov"
        return "unicode_alpha_oov"
    return "not_alpha"


def verify_corpus_pin():
    """Hash corpus tại lần chạy này phải khớp pin trong core_domain_provenance
    (nguồn VI đã khai cùng file) — không chép hash lịch sử (C16-02)."""
    pin = json.loads(CORPUS_PIN_FILE.read_text(encoding="utf-8"))
    expected = next(s["sha256"] for s in pin["source"]
                    if s["path"].endswith("corpus_ir_1M.jsonl.gz"))
    got = sha256_stream(CORPUS)
    if got != expected:
        raise SystemExit(f"[cmu_coverage] corpus lệch pin: {got[:12]}… ≠ "
                         f"{expected[:12]}… (pin {CORPUS_PIN_FILE})")
    return got, str(CORPUS_PIN_FILE.relative_to(ROOT))


def main():
    cmu = C.load_cmu()
    corpus_sha, corpus_pin_src = verify_corpus_pin()
    freq = Counter()
    n_records = n_en_tokens = n_empty = 0
    with gzip.open(CORPUS, "rt", encoding="utf-8") as f:
        for ln in f:
            n_records += 1
            for t in json.loads(ln).get("ir", {}).get("tokens", []):
                if t.get("cat") != "word" or t.get("route") != "en":
                    continue
                n_en_tokens += 1
                w = norm_token(t.get("verbal", ""))
                if not w:
                    n_empty += 1
                    continue
                freq[w] += 1

    miss_keys = ("has_digit", "ascii_alpha_oov", "unicode_alpha_oov", "not_alpha")
    rows, why = [], {k: Counter() for k in miss_keys}
    n_in = 0
    for w, c in freq.items():
        hit = w in cmu
        if hit:
            n_in += 1
        else:
            why[classify_miss(w)][w] = c
        rows.append((w, c, hit))
    rows.sort(key=lambda x: (-x[1], x[0]))

    # no_nucleus trong tập hit — minh bạch "dictionary hit ≠ phát âm hoàn tất".
    # Đếm trực tiếp trên tuple phones của entry mặc định (KHÔNG qua pronounce
    # từng từ — quá chậm trên 50k hit): entry không có phone nguyên âm nào.
    def _has_vowel(phones):
        for p in phones:
            base = p.rstrip("012")
            if base in C.VOWEL_MAP or base in ("AH", "ER"):
                return True
        return False

    n_nucleus_less = sum(1 for w in freq if w in cmu
                         and not _has_vowel(cmu[w][0]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tsv = OUT_DIR / "en_coverage.tsv"
    # Header dùng prefix '@@' (KHÔNG '#') vì token en thật có dạng bắt đầu bằng
    # '#' (HTML entity '#273;…') — tránh lọc nhầm khi đọc máy.
    tsv.write_text("@@ cmu_coverage fase C — token en NGUYÊN DẠNG (NFC+lower+strip); "
                   "in_cmu = exact key trong cmudict pin; token CÓ THỂ bắt đầu '#'\n"
                   + "".join(f"{w}\t{c}\t{1 if hit else 0}\n"
                             for w, c, hit in rows), encoding="utf-8")

    n_unique = len(rows)
    total_freq = sum(c for _w, c, _h in rows)          # = token không rỗng
    freq_in = sum(c for _w, c, h in rows if h)
    pct = lambda a, b: round(100 * a / b, 4) if b else 0.0
    counts = {"n_records": n_records, "n_en_tokens": n_en_tokens,
              "n_empty_dropped": n_empty,
              "n_nonempty_tokens": total_freq,
              "n_unique": n_unique,
              "n_unique_in_cmu": n_in,
              "pct_unique_in_cmu": pct(n_in, n_unique),
              "n_freq_in_cmu": freq_in,
              "pct_freq_in_cmu": pct(freq_in, total_freq),
              "n_unique_no_nucleus_in_cmu": n_nucleus_less,
              "label_hit": ("dictionary hit (exact key) — KHÔNG đồng nghĩa "
                            "phát âm hoàn tất: no_nucleus trả status riêng"),
              }
    for k in miss_keys:
        counts[f"n_unique_{k}"] = len(why[k])
        counts[f"freq_{k}"] = sum(why[k].values())
        counts[f"pct_freq_{k}"] = pct(sum(why[k].values()), total_freq)
    # OOV spell trọn token = đúng nhóm ascii a-z (LETTER_NAMES phủ a-z)
    counts["n_unique_spell_complete_oov"] = counts["n_unique_ascii_alpha_oov"]
    counts["freq_spell_complete_oov"] = counts["freq_ascii_alpha_oov"]
    counts["pct_freq_spell_complete_oov"] = counts["pct_freq_ascii_alpha_oov"]

    prov = {
        "artifact": "02_data/en_branch/en_coverage.tsv",
        "date": str(date.today()),
        "corpus": {"path": str(CORPUS),
                   "tag": CORPUS_TAG,
                   "sha256_verified_at_run": corpus_sha,
                   "pin_source": corpus_pin_src,
                   "n_records_seen": n_records},
        "method": ("token literal nguyên dạng (cat=word route=en, NFC+lower+strip), "
                   "không tách; exact lookup key cmudict pin (cmu_en.load_cmu, "
                   "verify sha256); biến thể (2) gộp về 1 key; đơn vị đếm tần suất "
                   "= token nguyên dạng; miss tách ascii a-z (spell trọn) khỏi "
                   "unicode alphabetic (không đảm bảo spell trọn) — C16-02"),
        "cmudict": {"sha256": C._cmudict_sha(),
                    "provenance": "03_vendor/cmudict/cmudict_provenance.json",
                    "n_keys_lowercased": len(cmu)},
        "en_policy_hash": C.en_policy_hash(),
        "counts": counts,
        "code_sha256": {"cmu_en.py": hashlib.sha256(
                            (HERE / "cmu_en.py").read_bytes()).hexdigest(),
                        "cmu_coverage.py": hashlib.sha256(
                            Path(__file__).read_bytes()).hexdigest()},
        "tsv_sha256": hashlib.sha256(tsv.read_bytes()).hexdigest(),
    }
    (OUT_DIR / "en_coverage_provenance.json").write_text(
        json.dumps(prov, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"records={n_records:,} en_tokens={n_en_tokens:,} "
          f"unique={n_unique:,} in_cmu={n_in:,} "
          f"({counts['pct_unique_in_cmu']}% unique / "
          f"{counts['pct_freq_in_cmu']}% freq)")
    for k in miss_keys:
        print(f"  miss {k:18s}: unique={len(why[k]):,} "
              f"freq={sum(why[k].values()):,} "
              f"({counts[f'pct_freq_{k}']}% freq)")
    print(f"  no_nucleus trong hit: {n_nucleus_less}")
    print(f"OK {tsv}")


if __name__ == "__main__":
    main()
