#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""So sánh các G2P/front-end tiếng Việt–Anh trên CÙNG 300 câu thật
(100 vi + 100 anh + 100 mix — 500 câu mix được lấy từ 2 bộ mix_easy +
mix_hard của listening_test). KHÔNG có TTS ở đây: đo (1) hệ chạy được hay
không, (2) tốc độ câu/s trên 1 luồng, (3) TỶ LỆ "số rò rỉ" — câu có chữ số
còn sót trong chuỗi ra (chữ số chưa được verbalize → acoustic model không
đọc được), và (4) NGUYÊN VĂN đầu ra từng câu để ai cũng xem được.

Các hệ tham gia + cài đặt:
  - ours_v2        : G2P v2 của repo này (chạy in-process)
  - donglao_g2p    : pip install donglao_g2p   → Pipeline().phonemize
  - sea_g2p        : pip install sea_g2p       → G2P(lang='vi').convert
  - vietnormalizer : pip install vietnormalizer → VietnameseNormalizer
                     (đầu ra là VĂN BẢN chuẩn hóa, không phải phôn vị —
                     ghi vào cột kind)
  - vig2p          : pip install cmudict phonemizer rồi cài từ nguồn
                     (github.com/hoang1007/vig2p) → vig2p.vi.vig2p
  - vphon          : git clone https://github.com/kirbyj/vPhon rồi đặt
                     VPHON_PATH=… (chuyển từng từ, không verbalize số)
  - viphoneme      : CẦN Python <3.12 (dùng module imp đã bị xóa).
                     pip install viphoneme vinorm underthesea eng_to_ipa.
                     Script tự gọi lại chính nó bằng python3.10 làm worker.
  - espeak_ng      : binary `espeak-ng -q --ipa` (1 lần gọi / câu)

Cách chạy:  python3 run_g2p_comparison.py [thư_mục_xuất]
Kết quả   : outputs_all_tools.csv (nguyên văn từng câu, từng hệ)
            + summary.csv (tốc độ, tỷ lệ lỗi, tỷ lệ số rò rỉ)
Máy đo ghi trong summary.csv. Mọi hệ đều đo CÙNG cách: 10 câu warm-up,
rồi 1 vòng qua 300 câu tính thời gian từng câu.
"""
import csv
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE / "test_300_sentences.tsv"
# "số rò rỉ" = chữ số ĐỨNG ĐỘC LẬP trong chuỗi ra ("100", "2026", "05/10")
# — chữ số làm thanh điệu gắn vào âm tiết ("toj1", "mot6") KHÔNG tính,
# vì đó là ký hiệu của hệ phiên âm chứ không phải nội dung chưa verbalize.
STANDALONE_DIGIT = re.compile(r"\b\d+\b")


def load_tests():
    rows = []
    with open(TESTS, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows.append(r)
    if not rows:
        raise SystemExit("không đọc được test_300_sentences.tsv")
    return rows


def timed(runner, sents):
    """trả (lats_ms, outs) — 10 câu warm-up; lỗi → status + ms=nan"""
    for s in sents[:10]:
        try:
            runner(s)
        except Exception:
            pass
    lats, outs = [], []
    for s in sents:
        t0 = time.perf_counter()
        try:
            o = runner(s)
            st = "ok" if o and str(o).strip() else "empty"
        except Exception as e:
            o, st = f"{type(e).__name__}: {e}", "error"
        lats.append((time.perf_counter() - t0) * 1000.0)
        outs.append((o, st))
    return lats, outs


def digits_left(s):
    return STANDALONE_DIGIT.search(str(s)) is not None


# ---------------- các hệ ----------------

def make_ours():
    repo = HERE.parent.parent
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "01_g2p"))
    sys.path.insert(0, str(repo / "v2"))
    from g2p_v2 import text_to_profile_v2_full

    def run(s):
        return text_to_profile_v2_full(s)["profile"]
    return "g2p (repo này)", "phoneme", run


def make_donglao():
    from donglao_g2p import Pipeline
    p = Pipeline()
    return "donglao_g2p", "phoneme", p.phonemize


def make_sea():
    from sea_g2p import G2P
    g = G2P(lang="vi")
    return "sea_g2p", "phoneme", g.convert


def make_vn():
    from vietnormalizer import VietnameseNormalizer
    v = VietnameseNormalizer()
    return "vietnormalizer", "text", v.normalize


def make_vig2p():
    from vig2p.vi import vig2p as fn
    return "vig2p", "phoneme", fn


def make_vphon():
    base = Path(os.environ.get("VPHON_PATH", "/tmp/vPhon"))
    sys.path.insert(0, str(base))
    from vPhon import convert

    def run(s):
        parts = []
        for w in s.split():
            r = convert(w, "n", 0, 0, 0, 0, 0, " ")
            parts.append(" ".join(r) if isinstance(r, list) else str(r))
        return " ".join(parts)
    return "vPhon", "phoneme", run


def make_espeak():
    import shutil
    if not shutil.which("espeak-ng"):
        raise RuntimeError("espeak-ng chưa cài")

    def run(s):
        r = subprocess.run(["espeak-ng", "-q", "--ipa", s],
                           capture_output=True, text=True)
        return r.stdout.strip()
    return "espeak_ng", "phoneme", run


VIPHONEME_WORKER = """
import json, sys
from viphoneme import vi2IPA
while True:
    line = sys.stdin.readline()
    if not line:
        break
    try:
        out = str(vi2IPA(line.rstrip("\\n")))
    except Exception as e:
        out = "ERROR " + type(e).__name__
    sys.stdout.write(json.dumps(out) + "\\n")
    sys.stdout.flush()
"""


def find_viphoneme_python():
    """Python chạy được viphoneme (<3.12 vì dùng module imp đã bị xóa)."""
    cand = os.environ.get("VIPHONEME_PYTHON")
    cands = ([cand] if cand else []) + ["python3.10", "python3.11"]
    for c in cands:
        p = subprocess.run([c, "-c", "import viphoneme"],
                           capture_output=True, text=True)
        if p.returncode == 0:
            return c
    return None


def make_viphoneme():
    if sys.version_info < (3, 12):
        from viphoneme import vi2IPA
        return "viphoneme", "phoneme", (lambda s: str(vi2IPA(s)))
    py = find_viphoneme_python()
    if py is None:
        raise RuntimeError("cần python3.10/3.11 với viphoneme đã cài "
                           "(hoặc đặt VIPHONEME_PYTHON=…)")
    proc = subprocess.Popen([py, str(Path(__file__).resolve()),
                             "--viphoneme-worker"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            text=True)

    def run(s):
        import json
        proc.stdin.write(s + "\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())
    return "viphoneme", "phoneme", run


MAKERS = {"ours": make_ours, "donglao_g2p": make_donglao,
          "sea_g2p": make_sea, "vietnormalizer": make_vn,
          "vig2p": make_vig2p, "vphon": make_vphon,
          "espeak_ng": make_espeak, "viphoneme": make_viphoneme}


def run_one_tool(key):
    """Chạy 1 tool → (name, kind, out_rows, sum_row). Dùng ở chế độ
    subprocess (--tool) để nhiều tool chạy ĐỒNG THỜI trên nhiều core —
    tốc độ vẫn đo tuần tự trong tiến trình của tool nên công bằng."""
    name, kind, fn = MAKERS[key]()
    sents = load_tests()
    lats, outs = timed(fn, [r["sentence"] for r in sents])
    n = len(outs)
    ok = sum(1 for o, st in outs if st == "ok")
    err = sum(1 for o, st in outs if st == "error")
    dig = sum(1 for o, st in outs if st == "ok" and digits_left(o))
    tot = sum(l for l, (o, st) in zip(lats, outs) if st == "ok") / 1000
    sps = ok / tot if tot > 0 else 0.0
    sum_row = {"tool": name, "kind": kind, "status": "ok", "error": "",
               "sents_per_s": f"{sps:.1f}",
               "p50_ms": f"{statistics.median(lats):.1f}",
               "p95_ms": f"{sorted(lats)[int(0.95 * (n - 1))]:.1f}",
               "ok_pct": f"{100 * ok / n:.1f}",
               "error_pct": f"{100 * err / n:.1f}",
               "digit_left_pct": f"{100 * dig / n:.1f}",
               "cpu": cpu_name()}
    out_rows = [{"tool": name, "kind": kind, "group": r["group"],
                 "suite": r["suite"], "stt": r["stt"],
                 "sentence": r["sentence"], "status": st,
                 "ms": f"{lat:.1f}", "output": str(o)}
                for r, (o, st), lat in zip(sents, outs, lats)]
    return out_rows, sum_row


def main_parallel():
    """Spawn mỗi tool 1 tiến trình (--tool KEY), chạy đồng thời, gộp kết quả."""
    import json
    keys = list(MAKERS)
    procs = {k: subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--tool", k],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for k in keys}
    all_out, all_sum = [], []
    for k, p in procs.items():
        so, se = p.communicate()
        if p.returncode != 0:
            err = (se or "").strip().splitlines()[-1] if se.strip() else "?"
            all_sum.append({"tool": k, "kind": "", "status": "install-fail",
                            "error": err, "sents_per_s": "", "p50_ms": "",
                            "p95_ms": "", "ok_pct": "", "error_pct": "",
                            "digit_left_pct": "", "cpu": cpu_name()})
            print(f"{k}: KHÔNG CHẠY ĐƯỢC — {err}")
            continue
        payload = json.loads(so)
        all_out += payload["out"]
        all_sum.append(payload["sum"])
        print(f"{payload['sum']['tool']}: ok {payload['sum']['ok_pct']}% · "
              f"{payload['sum']['sents_per_s']} câu/s · số rò rỉ "
              f"{payload['sum']['digit_left_pct']}%")
    order = {"vi": 0, "en": 1, "mix": 2}
    all_out.sort(key=lambda r: (r["tool"], order[r["group"]],
                                int(r["stt"])))
    with open(HERE / "outputs_all_tools.csv", "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_out[0].keys()))
        w.writeheader()
        w.writerows(all_out)
    with open(HERE / "summary.csv", "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_sum[0].keys()))
        w.writeheader()
        w.writerows(all_sum)
    print("xong:", HERE / "outputs_all_tools.csv", HERE / "summary.csv")
    return 0


def main() -> int:
    import json
    if "--viphoneme-worker" in sys.argv:
        exec(VIPHONEME_WORKER)
        return 0
    if "--tool" in sys.argv:
        key = sys.argv[sys.argv.index("--tool") + 1]
        out_rows, sum_row = run_one_tool(key)
        print(json.dumps({"out": out_rows, "sum": sum_row},
                         ensure_ascii=False))
        return 0
    return main_parallel()


def cpu_name():
    try:
        for ln in Path("/proc/cpuinfo").read_text().splitlines():
            if ln.startswith("model name"):
                return ln.split(":", 1)[1].strip()
    except OSError:
        pass
    return "?"


if __name__ == "__main__":
    raise SystemExit(main())
