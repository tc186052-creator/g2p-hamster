# -*- coding: utf-8 -*-
"""fetch_cmudict.py — recipe tái lập cây vendor CMUdict từ đầu (C16-01).

Tải đúng 2 file tại commit đã pin, kiểm SHA-256 đối chiếu
cmudict_provenance.json — lệch → SystemExit, KHÔNG ghi file sai.
Không tự sửa provenance: provenance là bản pin của tác giả, script chỉ
KIỂM tra (tải lại không được phép tự nâng revision).

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 03_vendor/cmudict/fetch_cmudict.py
       (thêm --force để ghi đè file đã có)
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROV = HERE / "cmudict_provenance.json"

# Pin duy nhất — phải khớp "revision_commit" trong cmudict_provenance.json.
COMMIT = "74790861f652b15e4ac49015a90074ad62a27690"
FILES = {
    "cmudict.dict":
        f"https://raw.githubusercontent.com/cmusphinx/cmudict/{COMMIT}/cmudict.dict",
    "LICENSE":
        f"https://raw.githubusercontent.com/cmusphinx/cmudict/{COMMIT}/LICENSE",
}
UA = "curl/8.5.0"  # UA thô — GitHub raw cần UA không phải python-urllib


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    prov = json.loads(PROV.read_text(encoding="utf-8"))
    rev = prov["revision_commit"].split()[0]
    if rev != COMMIT:
        raise SystemExit(f"provenance pin revision {rev} ≠ recipe {COMMIT} — "
                         f"tắt lệch pin, không tải")
    expected = {"cmudict.dict": prov["sha256"],
                "LICENSE": prov["license_sha256"]}
    rc = 0
    for name, url in FILES.items():
        dest = HERE / name
        if dest.exists() and "--force" not in sys.argv:
            got = sha256_bytes(dest.read_bytes())
            if got == expected[name]:
                print(f"OK (đã có, hash khớp pin): {name} {got[:12]}…")
                continue
            print(f"LECH PIN: {name} {got[:12]}… ≠ {expected[name][:12]}… "
                  f"— dùng --force để tải lại", file=sys.stderr)
            rc = 1
            continue
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        got = sha256_bytes(data)
        if got != expected[name]:
            raise SystemExit(f"{name} tải về lệch pin: {got} ≠ {expected[name]} "
                             f"— KHÔNG ghi file")
        dest.write_bytes(data)
        print(f"OK (tải + khớp pin): {name} {got[:12]}… ({len(data):,} bytes)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
