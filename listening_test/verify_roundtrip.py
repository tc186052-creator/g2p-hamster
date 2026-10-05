#!/usr/bin/env python3
"""Chấm lại toàn bộ số liệu STT ngược trên README — TỪ DỮ LIỆU CÔNG KHAI
trong repo, KHÔNG cần chạy model TTS hay ASR nào.

Ngữ pháp phép đo (giống hệt lúc chấm gốc):
  - token: NFC, lowercase, bỏ dấu câu, tách khoảng trắng
  - acc  = 1 − edit_distance(đáp án, transcript) / số token đáp án
  - đáp án = TỐT NHẤT giữa hai cách viết: `verbal_ref` (văn bản tầng 1 đã
    verbalize — thứ model thực sự đọc) và văn bản gốc
  - "khớp hoàn toàn" = acc ≥ 0.999;  "≥95%" = acc ≥ 0.95

Dữ liệu vào (cùng thư mục):
  - review_sheet.tsv                → câu + verbal_ref (đáp án)
  - asr_roundtrip_all_models.csv    → transcript + điểm từng clip, từng model

Cách chạy:  python3 verify_roundtrip.py
Kết quả:    bảng model × suite (khớp hoàn toàn / ≥95% / TB Pho & v3)
            + kiểm tra consistency với cột điểm đã công bố trong CSV.
"""
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
SUITES = ("vietnamese", "english", "mix_easy", "mix_hard")
MODELS = ("ours", "kokoro_goc", "kokoro_vietnamese", "kokoro_goc_afheart")


def tokens(s: str):
    return PUNCT.sub(" ", unicodedata.normalize("NFC", s).lower()).split()


def edit_dist(a, b):
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            cur = dp[j]
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
            prev = cur
    return dp[len(b)]


def acc(ref_t, hyp_t):
    if not ref_t:
        return 1.0
    return max(0.0, 1.0 - edit_dist(ref_t, hyp_t) / len(ref_t))


def main() -> int:
    # đáp án
    refs = {}
    with open(HERE / "review_sheet.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            refs[(r["suite"], int(r["stt"]))] = r
    if not refs:
        print("!! review_sheet.tsv trống"); return 1

    # transcript công bố
    rows = []
    with open(HERE / "asr_roundtrip_all_models.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    if not rows:
        print("!! asr_roundtrip_all_models.csv trống"); return 1

    bad = 0
    stats = defaultdict(lambda: [0, 0, 0, 0, 0.0, 0.0])  # khop_p, khop_v3,
    for r in rows:                                       # >=95 p/v3, tb p/v3
        key = (r["suite"], int(r["stt"]))
        if key not in refs:
            print(f"!! {key} không có trong review_sheet.tsv"); bad += 1
            continue
        ref = refs[key]
        ans = [tokens(ref.get("verbal_ref", "")), tokens(ref["sentence"])]
        ans = [a for a in ans if a]
        for eng, tcol, acol in (("pho", "transcript_pho", "match_pho_pct"),
                                ("v3", "transcript_v3", "match_v3_pct")):
            a = max(acc(t, tokens(r[tcol])) for t in ans) if ans else 0.0
            pub = float(r[acol])
            if abs(pub - a * 100) > 0.06:   # chênh lệch làm tròn tối đa
                print(f"!! {r['model']}/{key}/{eng}: CSV ghi {pub}% "
                      f"nhưng chấm lại {a*100:.1f}%"); bad += 1
            s = stats[(r["model"], r["suite"])]
            if a >= 0.999:
                s[0 if eng == "pho" else 1] += 1
            if a >= 0.95:
                s[2 if eng == "pho" else 3] += 1
            s[4 if eng == "pho" else 5] += a * 100

    print(f"{'model':22} {'suite':11} "
          f"{'khop (Pho)':>11} {'khop (v3)':>10} "
          f"{'>=95% (Pho/v3)':>15} {'TB% (Pho/v3)':>14}")
    for m in MODELS:
        for su in SUITES:
            s = stats.get((m, su))
            if not s:
                continue
            print(f"{m:22} {su:11} {s[0]:>8}/100 {s[1]:>7}/100 "
                  f"{s[2]:>7} / {s[3]:<6} {s[4]/100:>6.1f} / {s[5]/100:.1f}")
    if bad:
        print(f"\nKHÔNG ĐẠT: {bad} chỗ chấm lại không khớp điểm công bố")
        return 1
    print("\nĐẠT: mọi điểm công bố trong CSV đều tái lập được bằng script này")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
