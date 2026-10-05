# -*- coding: utf-8 -*-
"""emit_vocab_config.py — sinh vocab config cho acoustic frontend TỪ master
inventory (tư tưởng đảo chiều "model ăn theo G2P", đặc tả 4.8/4.9; fase D).

Output: 02_data/g2p/vocab_config_from_master.tsv + provenance JSON.
  - segment : unicode repr master (kokoro178 loss map được KHÔNG áp dụng —
              vocab config từ master GIỮ nguyên semantic ID/repr; loss chỉ
              xảy ra ở profile export, không ở vocab config).
  - prosody : TONE_* (đơn vị digit hiển thị 1-6) và STRESS_* (repr).
  - control : PUNCT_*.
  - meta    : dòng @@ ghi pin (inventory sha256, hash file, thời gian).

Reproducible: chạy lại trên cùng inventory → byte giống nhau. Inventory pin
lệch (ai sửa inventory_ham.tsv) → provenance ghi hash mới, KHÔNG tự chấp nhận
(verify qua inventory.selfcheck chạy trong load()).

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/emit_vocab_config.py
"""
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from g2p_hamster.core import inventory  # noqa: E402

ROOT = HERE.parent
OUT_DIR = ROOT / "02_data" / "g2p"


def main():
    rows = inventory.load()
    # Gate fail-closed (hậu kiểm v18 — ghi chú emitter): cam kết "selfcheck
    # bên trong" phải là kiểm thật — chạy ĐẦY ĐỦ audit điều 1-6 (trùng
    # semantic_id, trùng repr, lớp, …) TRƯỚC khi ghi; FAIL → không ghi file.
    errs, _warns = inventory.audit(rows)
    if errs:
        for e in errs:
            print(f"[emit_vocab_config] inventory audit FAIL: {e}",
                  file=sys.stderr)
        raise SystemExit("[emit_vocab_config] inventory audit không PASS — "
                         "KHÔNG ghi vocab config")
    inv_sha = hashlib.sha256((ROOT / "02_data" / "inventory_ham.tsv")
                             .read_bytes()).hexdigest()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tsv = OUT_DIR / "vocab_config_from_master.tsv"

    lines = [f"@@ vocab_config_from_master ham/0.2 — sinh từ "
             f"02_data/inventory_ham.tsv sha256={inv_sha} (master GIỮ nguyên "
             f"repr; loss kokoro178 chỉ ở profile export, không ở vocab)",
             "@@ cột: loai<TAB>semantic_id<TAB>unicode<TAB>ghi_chu_nguon"]
    for r in rows:
        lines.append(f"{r['loai']}\t{r['id']}\t{r['unicode']}\t")
    body = "\n".join(lines) + "\n"

    prov = {
        "artifact": "02_data/g2p/vocab_config_from_master.tsv",
        "date": str(date.today()),
        "generator": "01_g2p/emit_vocab_config.py",
        "inventory": {"path": "02_data/inventory_ham.tsv", "sha256": inv_sha,
                      "n_entries": len(rows)},
        "note": ("vocab sinh TỪ master (đảo chiều) — frontend Kokoro viết lại "
                 "dùng vocab này; kokoro178 tạm thời vẫn là adapter debug có "
                 "loss khai báo (SEGMENT_MAP_KOKORO178)"),
        "counts": {loai: sum(1 for r in rows if r["loai"] == loai)
                   for loai in ("segment", "prosody", "control")},
        "tsv_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }
    tsv.write_text(body, encoding="utf-8")
    (OUT_DIR / "vocab_config_provenance.json").write_text(
        json.dumps(prov, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK {tsv} — {len(rows)} entries "
          f"({prov['counts']['segment']} segment / "
          f"{prov['counts']['prosody']} prosody / "
          f"{prov['counts']['control']} control)")


if __name__ == "__main__":
    main()
