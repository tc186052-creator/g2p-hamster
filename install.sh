#!/usr/bin/env bash
# Cài môi trường cho g2p-hamster.
#
# Lõi G2P thuần Python stdlib — KHÔNG cần pip cài gì.
# Việc duy nhất đáng cài: espeak-ng — nguồn cứu phiên âm tiếng Anh của bản
# v2 (từ anh ngoài CMUdict). Thiếu espeak thì từ đó vẫn được đọc (kiểu vi
# hóa) nhưng là suy diễn, không phải phiên âm chuẩn.
set -e
cd "$(dirname "$0")"

if command -v espeak-ng >/dev/null 2>&1; then
    echo "espeak-ng: đã có ($(espeak-ng --version 2>/dev/null | head -1))"
elif command -v apt-get >/dev/null 2>&1; then
    echo "espeak-ng: chưa có — cài qua apt…"
    if [ "$(id -u)" = "0" ]; then
        apt-get install -y espeak-ng
    else
        sudo apt-get install -y espeak-ng
    fi
else
    echo "!! không thấy apt-get để tự cài. Cài espeak-ng theo cách của hệ"
    echo "   thống rồi chạy lại (xem README — mục Cài đặt)."
    exit 1
fi

python3 - <<'PY'
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "01_g2p")
sys.path.insert(0, "v2")
from g2p_v2 import text_to_profile_v2_full
r = text_to_profile_v2_full("Xin chào, hello world!")
assert r["profile"] and r["state"] == "complete", "G2P chạy hỏng"
print("Kiểm tra nhanh G2P: OK —", r["profile"][:48], "…")
PY

echo "Cài xong. Thử ngay:"
echo '  python3 cli.py "HLV của HAGL họp HĐQT tại TP.HCM."'
