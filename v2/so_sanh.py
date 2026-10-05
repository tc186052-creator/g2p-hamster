#!/usr/bin/env python3
"""so_sanh.py — so sánh G2P v1 (fail-closed) vs v2 (cứu EN: CMU→espeak→spell).

Dùng:
  python3 v2/so_sanh.py --input van_ban.txt            # 1 câu/dòng (hoặc đoạn, tự tách)
  python3 v2/so_sanh.py --parquet data.parquet --n 5000 --procs 22
  python3 v2/so_sanh.py --input van_ban.txt --out thu_muc_xuat

Phân lớp mỗi câu (theo STATE COVERAGE của v2 — KHÔNG phải correctness):
  GIONG          — cả hai OK, profile giống hệt
  LECH           — cả hai complete, profile KHÁC = thay đổi phiên âm (phần
                   lớn do nâng cấp OOV anh: v1 đánh vần → v2 phiên âm).
                   KHÔNG mặc định là tốt hơn — từng câu cần duyệt
  V2_CUU         — v1 TỪ CHỐI cả câu, v2 state=complete (đủ coverage, KHÔNG mất unit)
  V2_CUU_Partial — v1 từ chối, v2 đọc tiếp NHƯNG có unit nội dung bị bỏ → phải duyệt
  V2_Rong        — v1 từ chối, v2 profile rỗng/chỉ dấu câu → KHÔNG tính là cứu
  V2_HONG        — v1 OK nhưng v2 không complete (hồi quy coverage — bắt buộc rà)
  FAIL_CA_HAI    — cả hai cùng từ chối
Mọi câu ≠ GIONG được ghi vào <out>/lech_duyet.tsv để duyệt từng câu, kèm state,
số unit bị bỏ và nguồn cứu. Xuất kèm <out>/ket_qua.json (máy đọc được: toàn bộ
rows, MỖI câu kèm chi_tiet ĐẦY ĐỦ units/dropped/warnings/notes/errs — TSV mới
rút gọn — + fingerprint policy/config espeak). Báo cáo tách: đọc đủ / đọc thiếu /
rỗng, số từ bỏ, fallback theo nguồn. ĐÂY LÀ số ĐỘ PHỦ, không phải độ chính xác
phát âm — muốn kết luận "đọc đúng" cần gold được duyệt hoặc đánh giá nghe.
"""
import argparse
import os
import re
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")   # G2P thuần CPU — chặn
                                                    # tranh chấp GPU gây OOM

SENT_RE = re.compile(r"(?<=[.!?…])\s+")
_KEEP = re.compile(r"[a-zA-Zăâđêôơưà-ỹÀ-Ỹ]")

# state → phân lớp khi v1 TỪ CHỐI (v2 được "cứu" chỉ khi complete thật sự)
_CUU_BY_STATE = {"complete": "V2_CUU", "partial": "V2_CUU_Partial",
                 "empty": "V2_Rong", "rejected": "FAIL_CA_HAI"}


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
    from g2p_v2 import text_to_profile_v2_full
    try:
        p1, e1 = text_to_profile(s)
    except Exception as ex:
        p1, e1 = "", [f"EXC v1: {ex}"]
    try:
        full = text_to_profile_v2_full(s)
    except Exception as ex:
        full = {"state": "empty", "profile": "", "errs": [f"EXC v2: {ex}"],
                "notes": [], "dropped": [], "sources": {}, "warnings": [],
                "units": []}
    if e1:
        cls = _CUU_BY_STATE[full["state"]]
    elif full["state"] != "complete":
        cls = "V2_HONG"          # v1 đọc đủ nhưng v2 không đủ coverage
    elif p1 != full["profile"]:
        cls = "LECH"
    else:
        cls = "GIONG"
    lost = sum(1 for d in full["dropped"] if not d.get("intentional"))
    src = ",".join(f"{k}:{v}" for k, v in sorted(full["sources"].items()))
    # 11 trường hiển thị (TSV rút gọn notes/errs) + chi_tiet ĐẦY ĐỦ cho JSON:
    # notes/warnings/errs/dropped/units nguyên văn, không cắt
    chi_tiet = {"notes": full["notes"], "warnings": full["warnings"],
                "errs": list(full["errs"]), "dropped": full["dropped"],
                "units": full["units"]}
    return (idx, cls, s, p1, "; ".join(e1[:2]), full["profile"],
            "; ".join(full["errs"][:2]), full["state"], lost, src,
            " | ".join(full["notes"][:6]), chi_tiet)


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
    src_cnt = Counter()
    for r in rows:
        for kv in r[9].split(","):
            if kv:
                k, v = kv.rsplit(":", 1)
                src_cnt[k] += int(v)
    lost_total = sum(r[8] for r in rows)
    contract_warn = sum(1 for r in rows if r[11]["warnings"])

    # provenance của TOÀN BỘ lần chạy (worker con kế thừa env sau fork)
    from g2p_v2 import v2_provenance
    prov = v2_provenance()

    out = Path(a.out) if a.out else Path("so_sanh_ket_qua")
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "lech_duyet.tsv", "w", encoding="utf-8") as f:
        f.write("phan_lop\tstt\tcau\tv1_profile\tv1_loi\tv2_profile\tv2_loi"
                "\tv2_state\tunit_bi_bo\tnguon_cuu\tprovenance_v2\n")
        for (idx, cls, s, p1, e1, p2, e2, st, lost, sr, notes, _ct) in rows:
            if cls == "GIONG":
                continue
            f.write(f"{cls}\t{idx + 1}\t{s}\t{p1}\t{e1}\t{p2}\t{e2}"
                    f"\t{st}\t{lost}\t{sr}\t{notes}\n")

    # kết quả MÁY ĐỌC ĐƯỢC: toàn bộ rows + fingerprint/config để kiểm chứng.
    # Mỗi câu lưu ĐẦY ĐỦ units/dropped/warnings/notes/errs (chi_tiet) — bản
    # rút gọn chỉ dành cho TSV hiển thị. Fast-path units là TỪNG read unit
    # thật; entry có "merged": true + "unit_count": N là dòng GỘP tường minh.
    ket_qua = {
        "schema": "so_sanh_ket_qua/0.2",
        "meta": {
            "nguon": src, "so_cau_lay_mau": len(rows), "so_cau_nguon": total,
            "thoi_gian_s": round(time.time() - t0, 1), "procs": a.procs,
            "phan_lop": dict(cnt),
            "unit_bi_bo_phi_chu_y": lost_total,
            "cau_warning_hop_dong_ir": contract_warn,
            "nguon_cuu_unit": dict(src_cnt),
            "provenance_v2": prov,
        },
        "rows": [
            {"stt": idx + 1, "phan_lop": cls, "cau": s, "v1_profile": p1,
             "v1_loi": e1, "v2_profile": p2, "v2_loi": e2, "v2_state": st,
             "unit_bi_bo": lost, "nguon_cuu": sr, "notes_rut_gon": notes,
             "chi_tiet": ct}
            for (idx, cls, s, p1, e1, p2, e2, st, lost, sr, notes, ct) in rows
        ],
    }
    import json as _json
    (out / "ket_qua.json").write_text(
        _json.dumps(ket_qua, ensure_ascii=False, indent=1), encoding="utf-8")

    md = [f"# So sánh G2P v1 vs v2 — {src}", "",
          f"- {len(rows)} câu, {time.time() - t0:.0f}s", "",
          "## Provenance lần chạy", "",
          f"- policy hash: `{prov['policy_hash']}`",
          f"- espeak: {prov['espeak'].get('enabled')} — "
          f"{prov['espeak'].get('version', 'n/a')} (voice {prov['espeak']['voice']})",
          "", "## Phân lớp (coverage — KHÔNG phải correctness phát âm)", "",
          "| Phân lớp | Số câu |", "|---|---|"]
    for cls in ("GIONG", "LECH", "V2_CUU", "V2_CUU_Partial", "V2_Rong",
                "V2_HONG", "FAIL_CA_HAI"):
        md.append(f"| {cls} | {cnt.get(cls, 0)} |")
    md += ["", "`LECH` = thay đổi phiên âm so với v1 — KHÔNG mặc định là tốt "
               "hơn, từng câu cần duyệt.", "",
           "## Nội dung unit", "",
           f"- unit nội dung bị bỏ (phi-chủ-ý), toàn bộ {len(rows)} câu: **{lost_total}**",
           f"- câu có warning hợp đồng IR (per-token không mất unit): {contract_warn}",
           "", "## Nguồn cứu (số unit theo nguồn)", ""]
    for k in ("core", "cmu", "espeak", "spell"):
        if src_cnt.get(k):
            md.append(f"- {k}: {src_cnt[k]}")
    md += ["", f"File duyệt: `lech_duyet.tsv` ({len(rows) - cnt.get('GIONG', 0)} câu — "
               "gồm cả V2_CUU_Partial và V2_Rong) · Kết quả máy đọc được: "
               "`ket_qua.json`", "",
           "LƯU Ý: số liệu này đo ĐỘ PHỦ (đọc đủ/thiếu/rỗng). Muốn kết luận "
           "đọc ĐÚNG cần gold được duyệt hoặc đánh giá nghe."]
    (out / "bao_cao.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("KẾT QUẢ:", dict(cnt))
    print(f"unit bị bỏ (phi-chủ-ý): {lost_total} | nguồn cứu: {dict(src_cnt)}")
    print(f"policy hash: {prov['policy_hash']}")
    print(f"xong: {out / 'lech_duyet.tsv'} + {out / 'ket_qua.json'}")


if __name__ == "__main__":
    main()
