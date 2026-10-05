#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bài test 100.000 câu thật — CHẤT LƯỢNG normalization VI/EN code-switch,
KHÔNG đo tốc độ (yêu cầu của chủ dự án: "ko cần test tốc độ nữa nên ko cần
công bằng về phần tốc độ, đa luồng bla bla").

Dữ liệu: dataset_100k.tsv — 100.000 câu thật (52.000 vi / 33.000 en /
14.999 mixed) — chính là corpus đối chiếu của dự án.

Hệ tham gia (3, đúng yêu cầu):
  - ours_v2     : g2p-hamster (repo này), in-process qua multiprocessing
  - sea_g2p     : pip install sea_g2p → G2P(lang='vi').convert  (cấu hình
                  giống bộ so sánh 300 câu)
  - donglao_g2p : pip install donglao_g2p → Pipeline().phonemize

Chỉ số (không cần tham chiếu, khách quan 100%):
  - "số rò rỉ": câu có CHỮ SỐ ĐỨNG ĐỘC LẬP sót trong chuỗi ra
    (\b\d+\b — chữ số làm thanh điệu gắn vào âm tiết "toj1", "mot6" KHÔNG
    tính, đó là ký hiệu phiên âm chứ không phải nội dung chưa verbalize).
    Chữ số chưa verbalize → acoustic model không đọc được → normalization
    thất bại. Đây là chỉ số "ăn thua" của TN VI/EN code-switch.
  - error: hệ ném exception; empty: chuỗi ra rỗng.

Kết quả: summary_100k.json + outputs_<hệ>.csv.gz (nguyên văn từng câu) +
vi_du_le_<hệ>.txt (mẫu câu rò rỉ để đối chiếu công khai).
"""
import csv
import gzip
import json
import multiprocessing as mp
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "dataset_100k.tsv.gz"      # bản nén đi kèm repo
if not DATA.exists():
    DATA = Path("/home/hseomymyi9/01_project/dataset_100k.tsv")
STANDALONE_DIGIT = re.compile(r"\b\d+\b")
NPROC = min(24, (mp.cpu_count() or 4))


def load_rows(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    rows = []
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = (r.get("text") or "").strip()
            if t:
                rows.append((r.get("lang") or "?", t))
    return rows


def digits_left(s):
    return STANDALONE_DIGIT.search(s) is not None


# ---------------- worker ----------------

_TOOL = None


def _init(tool):
    global _TOOL
    # BENCH_SOURCE=pypi → đo đúng gói g2p-hamster đã cài trong môi trường
    # (wheel PyPI), KHÔNG băm path repo vào; mặc định "repo" dùng code
    # trong repo để phát triển.
    if os.environ.get("BENCH_SOURCE", "repo") != "pypi":
        sys.path.insert(0, str(HERE.parent.parent))
    if tool == "ours_v2":
        from g2p_hamster.g2p_v2 import text_to_profile_v2_full

        def run(s):
            return text_to_profile_v2_full(s)["profile"]
    elif tool == "sea_g2p":
        # 0.2.2: đo ĐÚNG usage mà sea_g2p tài liệu hoá — SEAPipeline.run()
        # gồm cả bộ chuẩn hoá 17 bước của nó (bản trước dùng G2P.convert()
        # trần, tắt normalizer — sai cấu hình, phát hiện bởi đánh giá
        # độc lập 2026-10 và được vá tại đây)
        from sea_g2p import SEAPipeline
        p = SEAPipeline(lang="vi")

        def run(s):
            return p.run(s)
    elif tool == "donglao_g2p":
        from donglao_g2p import Pipeline
        p = Pipeline()

        def run(s):
            return p.phonemize(s)
    else:
        raise SystemExit(f"hệ không rõ: {tool}")
    _TOOL = run


def _one(arg):
    idx, lang, text = arg
    try:
        out = _TOOL(text)
        out = "" if out is None else str(out)
        status = "ok" if out.strip() else "empty"
    except Exception as e:
        out, status = f"{type(e).__name__}: {e}", "error"
    return (idx, lang, text, out, status, digits_left(out))


def run_tool(tool, rows):
    t0 = time.perf_counter()
    results = [None] * len(rows)
    with mp.Pool(NPROC, initializer=_init, initargs=(tool,)) as pool:
        done = 0
        for idx, lang, text, out, status, leak in pool.imap_unordered(
                _one, ((i, lg, t) for i, (lg, t) in enumerate(rows)),
                chunksize=200):
            results[idx] = (idx, lang, text, out, status, leak)
            done += 1
            if done % 20000 == 0:
                print(f"  [{tool}] {done}/{len(rows)} "
                      f"({time.perf_counter() - t0:.0f}s)", flush=True)
    dt = time.perf_counter() - t0
    print(f"  [{tool}] xong {len(rows)} câu trong {dt:.0f}s "
          f"(thông lượng {len(rows) / dt:.0f} câu/s — KHÔNG là chỉ số "
          f"của bài này)", flush=True)
    return results


def summarize(tool, results, dt):
    per = {}
    for _, lang, _, out, status, leak in results:
        d = per.setdefault(lang, {"n": 0, "leak": 0, "error": 0, "empty": 0})
        d["n"] += 1
        d["leak"] += leak
        d["error"] += status == "error"
        d["empty"] += status == "empty"
    total = {"n": len(results),
             "leak": sum(1 for r in results if r[5]),
             "error": sum(1 for r in results if r[4] == "error"),
             "empty": sum(1 for r in results if r[4] == "empty")}
    return {"tool": tool, "per_lang": per, "total": total}


def dump_outputs(tool, results):
    path = HERE / f"outputs_{tool}.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["idx", "lang", "text", "output", "status", "digit_leak"])
        for r in results:
            w.writerow(r)
    # mẫu câu rò rỉ (tối đa 25/lang) để đối chiếu công khai
    seen = {}
    with open(HERE / f"vi_du_le_{tool}.txt", "w", encoding="utf-8") as f:
        for idx, lang, text, out, status, leak in results:
            if leak and len(seen.get(lang, [])) < 25:
                seen.setdefault(lang, []).append(1)
                f.write(f"[{lang}] {text}\n  → {out}\n\n")
    return path


def main():
    # dataset có thể truyền qua argv (vd bộ held-out khác bộ phát triển);
    # khi dataset KHÁC bộ gốc (dataset_100k.tsv / bản gz đi kèm repo),
    # tự loại các câu trùng — chỉ đo trên phần mới tuyệt đối (held-out
    # thuần). Bộ gốc thì KHÔNG loại (nó là chính nó).
    path = (Path(sys.argv[1]) if len(sys.argv) > 1 else DATA).resolve()
    rows = load_rows(path)
    held_out_excluded = 0
    dev_paths = {DATA.resolve(),
                 Path("/home/hseomymyi9/01_project/dataset_100k.tsv").resolve()}
    old_path = Path("/home/hseomymyi9/01_project/dataset_100k.tsv")
    if path not in dev_paths and old_path.exists():
        old_texts = {t for _, t in load_rows(old_path)}
        before = len(rows)
        rows = [(lg, t) for lg, t in rows if t not in old_texts]
        held_out_excluded = before - len(rows)
    print(f"Dataset: {path} → {len(rows)} câu "
          + (f"(loại {held_out_excluded} câu trùng bộ cũ — held-out thuần) "
             if held_out_excluded else "")
          + f"({sum(1 for lg, _ in rows if lg == 'vi')} vi / "
          f"{sum(1 for lg, _ in rows if lg == 'en')} en / "
          f"{sum(1 for lg, _ in rows if lg == 'mixed')} mixed)", flush=True)
    summary = {"dataset": str(path), "n": len(rows),
               "held_out_excluded": held_out_excluded,
               "source": "wheel PyPI" if os.environ.get(
                   "BENCH_SOURCE") == "pypi" else "repo",
               "nproc": NPROC, "date": time.strftime("%Y-%m-%d %H:%M %Z"),
               "metric": "digit_leak = chữ số độc lập sót trong chuỗi ra",
                   "speed_note": "KHÔNG đo tốc độ trong bài này; "
                   "thông lượng chỉ ghi log để biết thời gian chạy"}
    for tool in ("ours_v2", "sea_g2p", "donglao_g2p"):
        print(f"=== {tool} ===", flush=True)
        t0 = time.perf_counter()
        results = run_tool(tool, rows)
        dt = time.perf_counter() - t0
        summary[tool] = summarize(tool, results, dt)
        p = dump_outputs(tool, results)
        s = summary[tool]
        print(f"  tổng: {s['total']['n']} câu, rò rỉ {s['total']['leak']} "
              f"({100 * s['total']['leak'] / s['total']['n']:.2f}%), "
              f"error {s['total']['error']}, empty {s['total']['empty']}")
        for lg, d in sorted(s["per_lang"].items()):
            print(f"  {lg:6s}: {d['n']:6d} câu, rò rỉ {d['leak']:6d} "
                  f"({100 * d['leak'] / d['n']:.2f}%)", flush=True)
        print(f"  outputs: {p.name}", flush=True)
    (HERE / "summary_100k.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Ghi summary_100k.json", flush=True)


if __name__ == "__main__":
    main()
