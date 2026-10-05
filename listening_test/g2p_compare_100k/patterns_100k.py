#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""patterns_100k.py — chéo mẫu normalization trên output đã sinh bởi
bench_100k.py (outputs_<sys>.csv.gz + summary_100k.json).

Sinh summary_heldout_patterns.json (khi summary_100k.json là held-out)
hoặc summary_code_switch.json (khi là dev) — cùng thư mục với outputs.

Các mẫu:
  percent   — câu gốc có `\d+%`   : bad = output còn chữ số độc lập
  a_b       — câu gốc có `\d+/\d+` : bad = output còn chữ số độc lập
  acro_caps — câu gốc có ALL-CAPS ≥2 chữ: bad = output còn chữ HOA liền ≥2
  time_h    — câu gốc có `\d{1,2}h\d{0,2}`: bad = output MẤT số (có `h`
              độc lập) — rơi âm thầm, nguy hiểm hơn rò rỉ.

Định nghĩa "chữ số độc lập" = regex \b\d+\b trên chuỗi ra (chữ số làm
thanh điệu gắn âm tiết như toj1/mot6 KHÔNG tính — đó là ký hiệu phiên âm
của từng hệ). Chỉ đếm dòng status=ok.
"""
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RE_PCT = re.compile(r"\d+\s*%".replace("\\", "\\"))
RE_AB = re.compile(r"\b\d+/\d+\b")
RE_CAPS = re.compile(r"\b[A-ZĐ]{2,}\b")
RE_TIME = re.compile(r"\b\d{1,2}h\d{0,2}\b", re.I)
DIGIT = re.compile(r"\b\d+\b")
ISO_H = re.compile(r"\bh\b")
CAPS_OUT = re.compile(r"\b[A-ZĐ]{2,}\b")
TEXT_ONLY = {"vietnormalizer"}


def load_texts(dataset):
    opener = gzip.open if str(dataset).endswith(".gz") else open
    texts = {}
    with opener(dataset, "rt", encoding="utf-8", newline="") as f:
        import csv
        for r in csv.DictReader(f, delimiter="\t"):
            t = (r.get("text") or "").strip()
            if t:
                texts[t] = r.get("lang") or "?"
    return texts


def main():
    summary = json.loads((HERE / "summary_100k.json").read_text(encoding="utf-8"))
    dataset = Path(summary["dataset"])
    texts = load_texts(dataset)
    held_out = bool(summary.get("held_out_excluded"))
    out = {}
    for tool in ("ours_v2", "sea_g2p", "donglao_g2p"):
        p = HERE / f"outputs_{tool}.csv.gz"
        cats = {"percent": [0, 0], "a_b": [0, 0], "acro_caps": [0, 0],
                "time_h": [0, 0]}
        with gzip.open(p, "rt", encoding="utf-8", newline="") as f:
            import csv
            for r in csv.DictReader(f, delimiter="\t"):
                if r.get("status") != "ok":
                    continue
                src = r["text"].strip()
                o = r["output"] or ""
                if src not in texts:
                    continue
                for cat, rx in (("percent", RE_PCT), ("a_b", RE_AB),
                                ("acro_caps", RE_CAPS), ("time_h", RE_TIME)):
                    if rx.search(src):
                        cats[cat][0] += 1
                        if cat == "acro_caps":
                            # hệ ra VĂN BẢN giữ nguyên chữ HOA là đúng;
                            # hệ ra phôn vị còn chữ HOA liền ≥2 là sót
                            bad = (tool not in TEXT_ONLY
                                   and CAPS_OUT.search(o))
                        elif cat == "time_h":
                            bad = bool(ISO_H.search(o))
                        else:
                            bad = bool(DIGIT.search(o))
                        if bad:
                            cats[cat][1] += 1
        out[tool] = {k: {"n": v[0], "bad": v[1]} for k, v in cats.items()}
    name = "summary_heldout_patterns.json" if held_out \
        else "summary_code_switch.json"
    (HERE / name).write_text(
        json.dumps({"dataset": str(dataset), "n": summary["n"],
                    "digit_leak_def": r"regex \b\d+\b trên chuỗi ra; "
                    "chỉ đếm status=ok; time_h bad = mất số (h độc lập)",
                    "systems": out}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"→ {name}")
    for tool, cats in out.items():
        print(f"  {tool:12} " + "  ".join(
            f"{k}={v['bad']}/{v['n']}" for k, v in cats.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
