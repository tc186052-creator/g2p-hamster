#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chạy bộ test FROZEN (test_set.tsv) qua 3 hệ + chấm điểm.

Vì cả 3 hệ đều xuất ra PHÔN VỊ (không phải văn bản), "exact match với
gold text" không áp dụng được trực tiếp. Thay vào đó:

- LEAKAGE: câu còn chữ số đứng độc lập trong chuỗi ra (chưa verbalize).
- DROP: câu có mẫu giờ `13h00` mà con số biến mất (chữ `h` đứng độc lập).
- KHỚP ĐỌC GOLD (chỉ câu synthetic, gold viết tay a-priori): chạy hệ trên
  câu gốc VÀ trên từng cách đọc gold (danh sách cách đọc hợp lệ — "một
  nghìn" hoặc "một ngàn" đều đúng), so khoảng cách edit trong CHÍNH
  không gian phôn vị của hệ đó. sim = 1 − lev/max(len), điểm câu = max
  theo các cách đọc gold. sim = 1 ⟺ hệ đọc đúng như một cách đọc gold.
  Không cần map IPA chéo giữa các hệ → công bằng tuyệt đối.

Đa luồng thoải mái — bài này KHÔNG đo tốc độ.
Xuất: outputs_<hệ>.csv + summary_frozen.json.
"""
import csv
import os
import json
import multiprocessing as mp
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STANDALONE_DIGIT = re.compile(r"\b\d+\b")
ISO_H = re.compile(r"\bh\b")
TIME_PAT = re.compile(r"\b\d{1,2}h\d{0,2}\b")
STRIP = re.compile(r"[\s.,:;!?()\"'`„“”…\-–—/|ˈˌ]")
NPROC = min(24, (mp.cpu_count() or 4))


def load_tests():
    rows = []
    with open(HERE / "test_set.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows.append(r)
    gold = {}
    with open(HERE / "gold.jsonl", encoding="utf-8") as f:
        for ln in f:
            d = json.loads(ln)
            gold[int(d["idx"])] = d
    return rows, gold


def lev(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def canon(s):
    return STRIP.sub("", s)


# ---------------- worker ----------------

_TOOL = None


def _init(tool):
    global _TOOL
    # BENCH_SOURCE=pypi → đo đúng gói g2p-hamster đã cài trong môi trường
    # (wheel PyPI), KHÔNG băm path repo vào; mặc định "repo" dùng code
    # trong repo để phát triển.
    if os.environ.get("BENCH_SOURCE", "repo") != "pypi":
        sys.path.insert(0, str(HERE.parent))
    if tool == "ours_v2":
        from g2p_hamster.g2p_v2 import text_to_profile_v2_full

        def run(s):
            return text_to_profile_v2_full(s)["profile"]
    elif tool == "sea_g2p":
        from sea_g2p import G2P
        g = G2P(lang="vi")

        def run(s):
            return g.convert(s)
    elif tool == "donglao_g2p":
        from donglao_g2p import Pipeline
        p = Pipeline()

        def run(s):
            return p.phonemize(s)
    else:
        raise SystemExit(f"hệ không rõ: {tool}")
    _TOOL = run


def _one(arg):
    key, text = arg
    try:
        out = _TOOL(text)
        out = "" if out is None else str(out)
        status = "ok" if out.strip() else "empty"
    except Exception as e:
        out, status = f"{type(e).__name__}: {e}", "error"
    return key, out, status


def run_tool(tool, jobs):
    t0 = time.perf_counter()
    res = {}
    with mp.Pool(NPROC, initializer=_init, initargs=(tool,)) as pool:
        for key, out, status in pool.imap_unordered(_one, jobs, chunksize=8):
            res[key] = (out, status)
    print(f"  [{tool}] {len(jobs)} lần gọi trong "
          f"{time.perf_counter() - t0:.0f}s")
    return res


def main():
    tests, gold = load_tests()
    # workload: mỗi câu + mỗi cách đọc gold
    jobs = [(("t", int(r["idx"])), r["text"]) for r in tests]
    for idx, g in gold.items():
        for k, alt in enumerate(g.get("gold_readings") or []):
            jobs.append((("g", idx, k), alt))

    summary = {"n": len(tests), "n_gold": len(gold),
               "date": time.strftime("%Y-%m-%d %H:%M %Z"),
               "systems": {}}
    for tool in ("ours_v2", "sea_g2p", "donglao_g2p"):
        print(f"=== {tool} ===", flush=True)
        res = run_tool(tool, jobs)
        per_cat = {}
        sim_sum, sim_n, sim_ge95 = 0.0, 0, 0
        sim_bad = []
        rows_out = []
        for r in tests:
            idx = int(r["idx"])
            cat = r["category"]
            out, status = res[("t", idx)]
            leak = bool(STANDALONE_DIGIT.search(out))
            drop = bool(TIME_PAT.search(r["text"]) and ISO_H.search(out))
            sim = None
            g = gold.get(idx)
            alts = g.get("gold_readings") if g else None
            if alts:
                base = canon(out)
                best, best_alt = 0.0, ""
                for k, alt in enumerate(alts):
                    a_out, a_status = res[("g", idx, k)]
                    a = canon(a_out)
                    if not a:
                        continue
                    s = max(0.0, 1.0 - lev(base, a) / max(len(base), len(a)))
                    if s > best:
                        best, best_alt = s, alt
                sim = round(best, 4)
                sim_sum += sim
                sim_n += 1
                sim_ge95 += sim >= 0.95
                if sim < 0.9 and len(sim_bad) < 25:
                    sim_bad.append({"idx": idx, "text": r["text"],
                                    "best_alt": best_alt, "sim": sim,
                                    "out": out[:160]})
            d = per_cat.setdefault(cat, {"n": 0, "leak": 0, "drop": 0,
                                         "error": 0, "empty": 0,
                                         "match_n": 0, "match_sum": 0.0,
                                         "match_ge95": 0})
            d["n"] += 1
            d["leak"] += leak
            d["drop"] += drop
            d["error"] += status == "error"
            d["empty"] += status == "empty"
            if sim is not None:
                d["match_n"] += 1
                d["match_sum"] += sim
                d["match_ge95"] += sim >= 0.95
            rows_out.append([idx, cat, r["text"], out, status, leak, drop,
                             sim])
        for cat, d in per_cat.items():
            if d["match_n"]:
                d["match_mean"] = round(d["match_sum"] / d["match_n"], 4)
            del d["match_sum"]
        tot = {"n": len(tests),
               "leak": sum(d["leak"] for d in per_cat.values()),
               "drop": sum(d["drop"] for d in per_cat.values()),
               "error": sum(d["error"] for d in per_cat.values()),
               "empty": sum(d["empty"] for d in per_cat.values()),
               "match_n": sim_n,
               "match_mean": round(sim_sum / sim_n, 4) if sim_n else None,
               "match_ge95": sim_ge95}
        summary["systems"][tool] = {"per_cat": per_cat, "total": tot,
                                    "match_worst": sim_bad}
        print(f"  leak {tot['leak']}/{tot['n']} | drop {tot['drop']} | "
              f"khớp-đọc {tot['match_mean']} (≥0.95: {sim_ge95}/{sim_n}) "
              f"| error {tot['error']} empty {tot['empty']}")
        with open(HERE / f"outputs_{tool}.csv", "w", encoding="utf-8",
                  newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["idx", "category", "text", "output", "status",
                        "leak", "drop", "match_sim"])
            w.writerows(rows_out)
    with open(HERE / "summary_frozen.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("Ghi summary_frozen.json + outputs_*.csv")


if __name__ == "__main__":
    main()
