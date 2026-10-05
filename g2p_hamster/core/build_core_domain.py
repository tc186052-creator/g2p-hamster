# -*- coding: utf-8 -*-
"""build_core_domain.py — căn cứ ĐỘC LẬP cho miền gate điều 7 (vòng 6.2).

Vấn đề reviewer: is_core() chỉ kiểm ngữ cảnh rời rạc — "câi/mấi/bêo" vẫn được gắn
core dù không phải chính tả lõi. Yêu cầu: căn cứ miền có NGUỒN + PHIÊN BẢN, độc lập
với output parser.

Giải pháp: thống kê tần suất dạng token từ corpus IR tầng 1 (đã verify 0 lỗi ở tầng 1
— NGUỒN ngoài G2P, không sinh từ bảng luật của parser). Artifact:
  02_data/core_domain/vi_syllable_vocab.tsv       (dạng token NFC lower <TAB> freq)
  02_data/core_domain/core_domain_provenance.json (nguồn, sha256, phương pháp, field)

ĐẶT TÊN (theo phản hồi reviewer vòng 6.1 — nguồn độc lập ≠ nhãn ngôn ngữ độc lập):
bảng này là "dạng token" (token xuất hiện trong corpus), KHÔNG phải "âm tiết chuẩn"
— không có bước thẩm định chính tả riêng. Attestation chỉ dùng để XÁC ĐỊNH MIỀN
ĐÁNH GIÁ (attested_gate_domain), KHÔNG thay xác nhận chính tả lõi.

VÒNG 6.2 (R61-01 — lỗi builder trước: tách theo SỐ DẤU THANH, không phải phân tích
âm tiết; "lựchọc" bị cắt thành "lựch"+"ọc" rồi đếm nhầm "lựch" thành attestation):
ĐƠN VỊ ĐẾM = TOKEN NGUYÊN DẠNG. Mỗi token cat=word route=vi toàn chữ được đếm
CHÍNH XÁC 1 LẦN theo verbal đã NFC+lower+strip — KHÔNG tách, KHÔNG sinh mảnh,
KHÔNG dùng strip_tone/parse. Số tần suất trong bảng là tần suất LITERAL của dạng
token đó trong corpus. Token dính chữ nhiều âm tiết (vd "họctập") được đếm nguyên
dạng "họctập" — không đóng góp vào bất kỳ âm tiết thành phần nào. Builder do đó
KHÔN import parser G2P nữa (độc lập cả về code).

NGUỒN = CHỈ corpus chính `corpus_ir_1M.jsonl.gz` (1.000.000 records theo
stats_1M.json). Supplement `corpus_ir_1M_supplement.jsonl.gz` (108 records tag
date/number/abbr — bộ edge-case tầng 1) bị LOẠI để nguồn attestation là một bộ
duy nhất đã verify; đã kiểm supplement KHÔNG chứa từ chẩn đoán gold (mắc/khắc/
muỗm/khuỷu/khoét/giết/buồm/tuy/thúy/coến/cuến/yên/gii/câi/bêo — 0 hit).

Audit điều 7 dùng bảng ĐÃ PIN này (không đọc corpus 600MB) — attested_gate_domain =
is_core(ngữ cảnh) ∩ attested(freq >= ATTEST_MIN_FREQ). Dạng core-ngữ-cảnh nhưng
không attested → lớp "ext" (extended_or_unattested_domain — miền mở rộng/thử
nghiệm, không gate). Các nhóm bị đưa ra ngoài gate vẫn được xuất đầy đủ trong
collision/ để truy vết (không mất dấu collision chưa giải quyết).

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/build_core_domain.py
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

CORPUS = [
    Path(os.environ.get("G2P_CORPUS_DIR", "/nonexistent") + "/"
         "corpus_ir_1M.jsonl.gz"),
]
SUPPLEMENT = Path(
    "<workspace>/02_project/05_TTS/01_tiny_model/01_data/silver/"
    "corpus_ir_1M_supplement.jsonl.gz")
OUT_DIR = HERE.parent / "02_data" / "core_domain"
CORPUS_TAG = ("tier1_silver_1M chính (stats_1M.json: 1.000.000 records, 22.723.901 "
              "tokens, 0 exceptions) — supplement 108 records edge-case LOẠI khỏi "
              "nguồn attestation")


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_word_letters(s):
    return all(U.category(c).startswith("L") for c in s) if s else False


def _prov_path(p):
    """Đường dẫn trong provenance: tương đối nếu nằm trong dự án, tuyệt đối nếu
    ngoài (corpus tổng hợp/đầu ra thử — không được làm crash builder)."""
    try:
        return str(p.relative_to(HERE.parent.parent.parent))
    except ValueError:
        return str(p)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    freq = Counter()
    stat = {"records": 0, "tokens_vi_word": 0, "tokens_nonletters": 0,
            "tokens_counted": 0}
    for path in CORPUS:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                stat["records"] += 1
                for tok in rec["ir"]["tokens"]:
                    if tok.get("cat") != "word" or tok.get("route") != "vi":
                        continue
                    stat["tokens_vi_word"] += 1
                    w = U.normalize("NFC", tok.get("verbal") or "").lower().strip()
                    if not is_word_letters(w):
                        stat["tokens_nonletters"] += 1
                        continue
                    # vòng 6.2: đếm TOKEN NGUYÊN DẠNG — không tách, không suy diễn
                    freq[w] += 1
                    stat["tokens_counted"] += 1

    tsv = OUT_DIR / "vi_syllable_vocab.tsv"
    rows = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("# dạng token nguyên dạng NFC-lower<TAB>tần suất literal — nguồn "
                "corpus IR tầng 1\n")
        f.write(f"# nguồn: {CORPUS_TAG}\n")
        f.write(f"# sinh: build_core_domain.py — {date.today().isoformat()}\n")
        f.write("# vòng 6.2: KHÔNG tách token — mỗi dòng là 1 dạng token xuất hiện "
                "nguyên vẹn trong corpus\n")
        for s, n in rows:
            f.write(f"{s}\t{n}\n")

    # kiểm supplement: có chứa từ chẩn đoán gold/diagnostic không (khai trong provenance)
    diag = ["mắc", "khắc", "mách", "muỗm", "khuỷu", "khoét", "giết", "buồm", "tuy",
            "thúy", "coến", "cuến", "yên", "gii", "câi", "bêo"]
    sup_diag_hits, sup_records, sup_srcs = {}, 0, set()
    with gzip.open(SUPPLEMENT, "rt", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            sup_records += 1
            sup_srcs.add(rec.get("source"))
            for tok in rec["ir"]["tokens"]:
                if tok.get("cat") == "word":
                    w = (tok.get("verbal") or "").lower()
                    if w in diag:
                        sup_diag_hits[w] = sup_diag_hits.get(w, 0) + 1

    prov = {
        "artifact": "02_data/core_domain/vi_syllable_vocab.tsv",
        "sha256_vocab": hashlib.sha256(tsv.read_bytes()).hexdigest(),
        "n_unique_token_forms": len(rows),
        "n_token_occurrences": stat["tokens_counted"],
        "unit": "dạng token NGUYÊN DẠNG (verbal NFC+lower+strip, toàn chữ) — tần "
                "suất LITERAL từng token trong corpus; KHÔNG phải 'âm tiết chuẩn đã "
                "thẩm định' và KHÔNG chứa mảnh tách suy diễn",
        "field_spec": {
            "record": "ir/0.1 — ir.tokens[]",
            "token_filter": "cat == 'word' AND route == 'vi'",
            "text": "verbal",
            "normalization": "NFC + lowercase + strip",
            "letters_only": "mọi ký tự thuộc category Unicode L*",
            "frequency_unit": "token nguyên dạng — mỗi occurrence token đếm đúng 1 "
                              "lần; KHÔNG tách âm tiết, KHÔNG dùng strip_tone/parse",
            "no_split_note": "vòng 6.2 (R61-01): bỏ hẳn bước tách của vòng trước — "
                             "token dính chữ nhiều âm tiết (vd 'họctập') được đếm "
                             "nguyên dạng và không đóng góp cho âm tiết thành phần",
        },
        "source": [{"path": _prov_path(p), "sha256": sha256_of(p)} for p in CORPUS],
        "corpus_tag": CORPUS_TAG,
        "supplement_exclusion": {
            "path": _prov_path(SUPPLEMENT),
            "sha256": sha256_of(SUPPLEMENT),
            "records": sup_records,
            "sources": sorted(sup_srcs),
            "why": "bộ edge-case tầng 1 (tag date/number/abbr) — LOẠI để nguồn "
                   "attestation là một bộ duy nhất đã verify",
            "gold_diagnostic_word_hits": sup_diag_hits,
        },
        "method": "token cat=word route=vi → verbal NFC lower strip → đếm literal "
                  "nguyên dạng. Builder KHÔNG import parser G2P. Bảng XUẤT THÔ "
                  "không lọc theo parser.",
        "stats": stat,
        "built": date.today().isoformat(),
    }
    (OUT_DIR / "core_domain_provenance.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"n_unique": len(rows), **stat,
                      "sup_gold_hits": sup_diag_hits}, ensure_ascii=False))
    for w in ["cây", "câi", "mấy", "mấi", "bêu", "bêo", "buâi", "buây", "iên",
              "yên", "lý", "lí", "ký", "kí", "ách", "éc", "muỗm", "khuỷu",
              "yếm", "tay", "quay", "que", "quê", "hue", "huê", "lựch", "họct",
              "thànhph", "lựchọc", "họctập"]:
        print(f"  {w}\t{freq.get(w, 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
