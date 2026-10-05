#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cli.py — giao diện dòng lệnh của G2P hamster.

Dùng:
  python cli.py "Xin chào, hôm nay trời đẹp quá!"
  python cli.py "Tôi dùng cue nhé." --mode strict
  python cli.py --v1 "Xin chào"                    # bản v1 fail-closed
  python cli.py --file van_ban.txt --out ketqua.json
"""
import argparse
import json
import sys
from pathlib import Path



def main() -> int:
    ap = argparse.ArgumentParser(
        description="G2P hamster — text → chuỗi phôn vị kokoro178")
    ap.add_argument("text", nargs="*",
                    help="câu cần chuyển (không có thì đọc stdin)")
    ap.add_argument("--v1", action="store_true",
                    help="bản v1 fail-closed (mặc định: v2 cứu từng từ)")
    ap.add_argument("--mode", choices=["best_effort", "strict"],
                    default="best_effort",
                    help="v2: best_effort cho render, strict cho prep train")
    ap.add_argument("--policy", default=None,
                    help="strict_policy v2, vd cmu,spell (mặc định: cmu,spell)")
    ap.add_argument("--file",
                    help="chuyển cả file text (mỗi dòng 1 câu)")
    ap.add_argument("--out", help="ghi kết quả JSON ra file")
    a = ap.parse_args()

    texts: list[str] = []
    if a.file:
        texts = [ln.strip() for ln in
                 Path(a.file).read_text(encoding="utf-8").splitlines()
                 if ln.strip()]
    elif a.text:
        texts = [" ".join(a.text)]
    else:
        texts = [ln.strip() for ln in sys.stdin.read().splitlines()
                 if ln.strip()]
    if not texts:
        ap.error("cần text, --file hoặc stdin")

    if not a.v1:
        # espeak-ng là nguồn cứu phiên âm anh của v2. Thiếu nó từ anh OOV vẫn
        # được đọc (vi hóa) NHƯNG không có cảnh báo ở thư viện — cảnh báo ở
        # đây, đúng 1 lần, trừ khi user TẮT tường minh bằng ESPEAK_NG_BIN="".
        import os
        if os.environ.get("ESPEAK_NG_BIN", None) is None:
            from .g2p_v2 import _espeak_bin
            if _espeak_bin() is None:
                print("!! chưa cài espeak-ng — từ tiếng Anh ngoài từ điển sẽ "
                      "được đọc kiểu vi hóa thay vì phiên âm chuẩn. Cài: "
                      "sudo apt install espeak-ng  (hoặc ./install.sh)",
                      file=sys.stderr)

    if a.v1:
        from .g2p_v1 import text_to_profile

        def run(s):
            p, errs = text_to_profile(s)
            return {"profile": p, "errs": errs}
    else:
        from .g2p_v2 import text_to_profile_v2_full
        policy = None
        if a.policy:
            names = frozenset(t.strip() for t in a.policy.split(",")
                              if t.strip())
            policy = names

        def run(s):
            return text_to_profile_v2_full(s, mode=a.mode,
                                           strict_policy=policy)

    results = []
    for s in texts:
        r = run(s)
        r["text"] = s
        results.append(r)
    payload = results[0] if (len(results) == 1 and not a.file) else results
    out = json.dumps(payload, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(out + "\n", encoding="utf-8")
        print(f"đã ghi {a.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
