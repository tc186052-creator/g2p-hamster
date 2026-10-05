#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""benchmark_speed.py — đo tốc độ front-end (text → phôn vị) trên 400 câu
thật trong listening_test/review_sheet.tsv.

Đo 3 đường, cùng bộ câu:
  1. v2 (mặc định)   — cứu từng từ theo bậc CMUdict → espeak-ng → spell
  2. v1 (fail-closed) — câu có từ lạ bị từ chối (đo cho biết, % câu bị loại)
  3. espeak-ng        — baseline tham khảo: gọi binary per-câu (sử dụng thật
                        của espeak khi làm G2P; bao gồm chi phí subprocess)

Thuần stdlib, không cần cài gì thêm. Kết quả phụ thuộc máy — ghi rõ CPU
khi trích số vào README.
"""
import csv
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPEAT = 3


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = max(0, min(len(xs) - 1, round(q * (len(xs) - 1))))
    return xs[k]


def cpu_name():
    try:
        for ln in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if ln.startswith("model name"):
                return ln.split(":", 1)[1].strip()
    except OSError:
        pass
    return "?"


def bench(fn, sents, repeat=REPEAT):
    for s in sents[:20]:
        fn(s)
    lats, chars = [], 0
    for _ in range(repeat):
        lats = []
        chars = 0
        for s in sents:
            t0 = time.perf_counter()
            fn(s)
            lats.append((time.perf_counter() - t0) * 1000.0)
            chars += len(s)
    total = sum(lats) / 1000.0  # ms → s
    return {"sents_per_s": len(sents) * repeat / total,
            "chars_per_s": chars * repeat / total,
            "lat": lats}


def espeak_g2p(s):
    r = subprocess.run(["espeak-ng", "-q", "--ipa", s],
                       capture_output=True, text=True)
    return r.stdout


def main() -> int:
    sents = []
    with open(HERE / "listening_test" / "review_sheet.tsv",
              encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("sentence"):
                sents.append(r["sentence"])
    if not sents:
        print("!! không đọc được review_sheet.tsv"); return 1
    print(f"{len(sents)} câu (4 bộ × 100, từ listening_test) · "
          f"repeat {REPEAT} · CPU: {cpu_name()}")
    print(f"{'đường':18} {'câu/s':>8} {'ký tự/s':>9} "
          f"{'p50 ms':>8} {'p95 ms':>8} ghi chú")

    sys.path.insert(0, str(HERE / "01_g2p"))
    sys.path.insert(0, str(HERE / "v2"))

    from g2p_v2 import text_to_profile_v2_full as v2_full
    r = bench(v2_full, sents)
    print(f"{'v2 (mặc định)':18} {r['sents_per_s']:>8.0f} "
          f"{r['chars_per_s']:>9.0f} {pct(r['lat'], .5):>8.1f} "
          f"{pct(r['lat'], .95):>8.1f} cứu từng từ (cmu→espeak→spell)")

    from g2p_v1 import text_to_profile as v1
    n_reject = sum(1 for s in sents if v1(s)[1])
    r = bench(v1, sents)
    print(f"{'v1 (fail-closed)':18} {r['sents_per_s']:>8.0f} "
          f"{r['chars_per_s']:>9.0f} {pct(r['lat'], .5):>8.1f} "
          f"{pct(r['lat'], .95):>8.1f} từ chối {n_reject}/{len(sents)} câu "
          f"có từ lạ")

    import shutil
    if shutil.which("espeak-ng"):
        r = bench(espeak_g2p, sents)
        print(f"{'espeak-ng (tham khảo)':18} {r['sents_per_s']:>8.0f} "
              f"{r['chars_per_s']:>9.0f} {pct(r['lat'], .5):>8.1f} "
              f"{pct(r['lat'], .95):>8.1f} 1 lần gọi binary/câu")
    else:
        print("espeak-ng: chưa cài — bỏ qua baseline này")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
