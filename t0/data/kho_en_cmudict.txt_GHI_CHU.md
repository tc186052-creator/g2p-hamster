# kho_en_cmudict.txt — GHI CHU PROVENANCE
- Sinh: 02/10/2026 bởi agent (phiên G2P/tầng 3), theo lệnh chủ dự án "cứ đi, tạo bản sao backup".
- Nguồn: 02_hamster_G2P/03_vendor/cmudict/cmudict.dict (pin của dự án, BSD-2 — xem
  02_hamster_G2P/03_vendor/cmudict/cmudict_provenance.json)
- sha256 nguồn: 81917843c7f44ce2b094ac63873c2c7a4cf802040792c455ba3ca406891c3d22
- Số từ: 126052 (lowercase, đã gỡ hậu tố (2)/(3) biến thể phát âm)
- Đích dùng: t0/dicts.py kho_en_cmudict() → t0/detect.py assign_routes nhánh tra cứu
  ("từ EN theo cmudict + không phải âm tiết VI hợp lệ → route en").
- Vá nhóm lỗi: từ EN trong câu VI bị route vi → G2P unresolved (96% câu syn_mix).
- Bằng chứng + giả lập: 02_hamster_G2P/06_train_t3/data/mix3/HO_SO_LOI_ROUTE_MIX.md
- Cổng đã chạy: xem 02_rules/backups/t0_bak_* (backup trước khi sửa) + nhật ký
  regression trong 04_eval.
