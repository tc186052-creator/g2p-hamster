#!/usr/bin/env python3
"""so_sanh.py — so sánh G2P v1 (fail-closed) vs v2 (cứu EN: CMU→espeak→spell).

Dùng:
  python3 v2/so_sanh.py --input van_ban.txt            # 1 câu/dòng (hoặc đoạn, tự tách)
  python3 v2/so_sanh.py --parquet data.parquet --n 5000 --procs 22
  python3 v2/so_sanh.py --input van_ban.txt --out thu_muc_xuat

Phân lớp mỗi câu:
  GIONG       — cả hai OK, profile giống hệt
  LECH        — cả hai OK, profile khác (vd OOV anh: v1 đánh vần chữ, v2 espeak)
  V2_CUU      — v1 TỪ CHỐI cả câu, v2 cứu được
  V2_HONG     — v1 OK nhưng v2 lỗi (hồi quy — bắt buộc rà)
  FAIL_CA_HAI — cả hai cùng từ chối
Mọi câu ≠ GIONG được ghi vào <out>/lech_duyet.tsv để duyệt từng câu.
"""
import argparse
import re
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

SENT_RE = re.compile(r"(?<=[.!?…])\s+")
_KEEP = re.compile(r"[a-zA-Zăâđêôơưà-ỹÀ-Ỹ]")


def split_sentences(text: str):
    out = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        for s in SENT_RE.split(ln):
            s = s.strip()
            if 10 <= len(s) <= 400 and _KEEP.search(s):
                out.append(s)
    return out


def load_parquet(path: str, n: int):
    import pyarrow.parquet as pq
    t = pq.read_table(path, columns=["text"])
    sents = split_sentences("\n".join(t.column("text").to_pylist()))
    step = max(1, len(sents) // n)
    return sents[::step][:n], len(sents)


def worker(job):
    idx, s = job
    from g2p_v1 import text_to_profile
    from g2p_v2 import text_to_profile_v2
    try:
        p1, e1 = text_to_profile(s)
    except Exception as ex:
        p1, e1 = "", [f"EXC v1: {ex}"]
    try:
        p2, e2, notes = text_to_profile_v2(s)
    except Exception as ex:
        p2, e2, notes = "", [f"EXC v2: {ex}"], []
    if e1:
        cls = "V2_CUU" if not e2 else "FAIL_CA_HAI"
    elif e2:
        cls = "V2_HONG"
    elif p1 != p2:
        cls = "LECH"
    else:
        cls = "GIONG"
    return (idx, cls, s, p1, "; ".join(e1[:2]), p2, "; ".join(e2[:2]),
            " | ".join(notes[:6]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="file .txt văn bản (tự tách câu)")
    ap.add_argument("--parquet", help="file .parquet có cột 'text' (wiki)")
    ap.add_argument("--n", type=int, default=5000, help="số câu lấy mẫu")
    ap.add_argument("--procs", type=int, default=22, help="số tiến trình")
    ap.add_argument("--out", default=None, help="thư mục xuất kết quả")
    a = ap.parse_args()
    if not (a.input or a.parquet):
        ap.error("cần --input hoặc --parquet")

    if a.parquet:
        sents, total = load_parquet(a.parquet, a.n)
        src = a.parquet
    else:
        sents = split_sentences(Path(a.input).read_text(encoding="utf-8"))
        total = len(sents)
        src = a.input
    print(f"nguồn: {src} — {total} câu, chạy {len(sents)} câu "
          f"({a.procs} tiến trình)")

    t0 = time.time()
    rows = []
    with Pool(a.procs) as pool:
        for k, row in enumerate(pool.imap_unordered(worker,
                                                    enumerate(sents), 32)):
            rows.append(row)
            if (k + 1) % 500 == 0:
                el = time.time() - t0
                print(f"  {k + 1}/{len(sents)} — {el:.0f}s "
                      f"({(k + 1) / el:.0f} câu/s)", flush=True)
    rows.sort(key=lambda r: r[0])
    cnt = Counter(r[1] for r in rows)

    out = Path(a.out) if a.out else Path("so_sanh_ket_qua")
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "lech_duyet.tsv", "w", encoding="utf-8") as f:
        f.write("phan_lop\tstt\tcau\tv1_profile\tv1_loi\tv2_profile\tv2_loi"
                "\tprovenance_v2\n")
        for idx, cls, s, p1, e1, p2, e2, notes in rows:
            if cls == "GIONG":
                continue
            f.write(f"{cls}\t{idx + 1}\t{s}\t{p1}\t{e1}\t{p2}\t{e2}\t{notes}\n")

    md = [f"# So sánh G2P v1 vs v2 — {src}", "",
          f"- {len(rows)} câu, {time.time() - t0:.0f}s", "",
          "| Phân lớp | Số câu |", "|---|---|"]
    for cls in ("GIONG", "LECH", "V2_CUU", "V2_HONG", "FAIL_CA_HAI"):
        md.append(f"| {cls} | {cnt.get(cls, 0)} |")
    md += ["", f"File duyệt: `lech_duyet.tsv` ({len(rows) - cnt.get('GIONG', 0)} câu)"]
    (out / "bao_cao.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("KẾT QUẢ:", dict(cnt))
    print(f"xong: {out / 'lech_duyet.tsv'}")


if __name__ == "__main__":
    main()
