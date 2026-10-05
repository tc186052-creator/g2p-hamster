# -*- coding: utf-8 -*-
"""trace_vocab_members.py — trace nguồn GỌN cho thành viên gate (reviewer vòng 6.1 §8.4).

Với từng dạng token trong nhóm gate (core_spellings + ext_spellings), quét corpus
IR pin và ghi tối đa 5 vị trí xuất hiện: record locator (số dòng trong .gz), token
index, verbal RAW, dạng chuẩn hóa, ngữ cảnh ±3 token. Tần suấtliteral trong TSV
kèm theo để đối chiếu (đếm LITERAL — vòng 6.2, không có mảnh suy diễn).

Output: 02_data/collision/gate_member_trace.jsonl (mỗi dòng 1 dạng token).
KHÔNG gửi cả corpus — trace này đủ để reviewer xác định nguồn từng lượt đếm.

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/trace_vocab_members.py
"""
import gzip
import hashlib
import json
import sys
import unicodedata as U
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import collision_audit as C  # noqa: E402
from build_core_domain import CORPUS  # noqa: E402  (nguồn pin, cùng builder)

OUT = HERE.parent / "02_data" / "collision" / "gate_member_trace.jsonl"
MAX_EXAMPLES = 5
CTX = 3


def main():
    report = json.loads((HERE.parent / "02_data" / "collision" /
                         "dieu7_bao_cao.json").read_text(encoding="utf-8"))
    vocab, prov = C.load_attestation()
    forms = set()
    for g in report["gate_groups"]:
        forms.update(g["core_spellings"])
        forms.update(g["ext_spellings"])

    src_sha = prov["source"][0]["sha256"][:12]
    hits = {f: [] for f in forms}
    n_occ = {f: 0 for f in forms}
    for path in CORPUS:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                rec = json.loads(line)
                ir_toks = rec["ir"]["tokens"]
                # T62-01 (review vòng 6.2): token_index phải là index GỐC trong
                # ir.tokens[] — enumerate danh sách gốc, lọc trong vòng lặp; ngữ
                # cảnh cũng dựng từ danh sách gốc (kể cả punct/en) để tra ngược
                # đúng vị trí. Bộ lọc chỉ quyết định CÓ đếm hay không — phép đếm
                # không đổi so với TSV.
                all_verbs = [t.get("verbal") or "" for t in ir_toks]
                for i, tok in enumerate(ir_toks):
                    if tok.get("cat") != "word" or tok.get("route") != "vi":
                        continue
                    tv = all_verbs[i]
                    w = U.normalize("NFC", tv).lower().strip()
                    if w in hits:
                        n_occ[w] += 1
                        if len(hits[w]) < MAX_EXAMPLES:
                            lo = max(0, i - CTX)
                            hits[w].append({
                                "record_line": line_no,
                                "token_index": i,
                                "raw_verbal": tv,
                                "normalized": w,
                                "context": " ".join(
                                    x for x in all_verbs[lo:i + CTX + 1] if x),
                            })

    with open(OUT, "w", encoding="utf-8") as f:
        for w in sorted(hits):
            f.write(json.dumps({
                "form": w,
                "freq_tsv": vocab.get(w, 0),
                "n_occurrences_in_corpus": n_occ[w],
                "counting": "literal token nguyên dạng (vòng 6.2) — không có mảnh "
                            "tách suy diễn",
                "token_index_scope": "index GỐC trong ir.tokens[] (T62-01 — kể cả "
                                     "punct/token không phải vi-word); context là "
                                     "verbal của ir.tokens[] nguyên bản",
                "source_sha256_12": src_sha,
                "examples": hits[w],
            }, ensure_ascii=False) + "\n")
    missing = sorted(w for w in forms if n_occ[w] == 0)
    print(f"trace {len(forms)} dạng gate → {OUT}; "
          f"{len(missing)} dạng không gặp trong corpus (freq literal < ngưỡng hoặc "
          f"ext): {missing[:10]}{'…' if len(missing) > 10 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
