# fold_provenance.md — nguồn của `02_data/fold/fold_vi.tsv` (khai THỰC, không bịa)

Yêu cầu hậu kiểm v18 D18-04: khai nguồn thực và chính sách chọn của bảng fold.
File này phân tách rõ **đã xác minh được** với **không còn hồ sơ**.

## Những gì xác minh được từ artifact còn lưu

- Artifact: `02_data/fold/fold_vi.tsv` — 698 dòng dữ liệu, cột
  `ascii · fold · freq_top1 · margin · n_candidates`, header comment 2 dòng.
  Pin byte: sha256 ghi trong `02_data/g2p/g2p_resource_pins.json`
  (key `fold_tsv`) — runtime `load_fold()` kiểm sha trước khi dùng, lệch →
  SystemExit.
- Nguồn đếm/phân nhóm: `02_data/fold/a0_ket_qua.json` (nguồn corpus
  `05_TTS/01_tiny_model/01_data/silver/corpus_ir_1M.jsonl.gz` sha
  `cb9df5eb…`, 1.000.000 câu, so_token_word_vi 16.563.317; nhóm
  ascii route-vi: (a) 1.133 unique — đọc nguyên dạng hợp lệ, (b) 698 unique —
  NHÓM NÀY LÀ BẢNG FOLD (698 dòng = đúng 698 unique nhóm b), (c) 99.477
  unique — không phải ascii thuần). Kèm `a0_ambiguous_top.tsv` (form, freq,
  ung_vien — danh sách ứng viên có dấu), `a0_shadow_theo_cau.tsv`,
  `a4_danh_gia_strip.json`, `uncertain_folds.log`.
- Chính sách chọn quan sát được TỪ DATA: mỗi dòng ascii chỉ có 1 fold duy nhất
  = 1 ứng viên trong `ung_vien` của a0_ambiguous_top; `n_candidates` = số ứng
  viên; `freq_top1` = tần suất corpus của ứng viên được chọn;
  `margin` ∈ (0,1] = tỉ trọng top-1 trong tổng tần suất các ứng viên
  (diễn giải từ dữ liệu: vd `top` margin 0,5159 với 6 ứng viên).

## Những gì KHÔNG còn hồ sơ (khai trung thực)

- Script builder tạo `fold_vi.tsv` ở vòng A0 (01/10/2026) **không còn trong
  cây** (phiên làm A0 dọn artifact script, chỉ giữ output + số liệu). Vì vậy
  KHÔNG tự chép lại "builder = script X". Lần tái sinh tiếp theo (nếu có) phải
  viết builder mới có commit + chạy lại toàn bộ và so byte.

## Chính sách sử dụng (hợp đồng đã duyệt)

- Chỉ áp cho nhóm (b) ASCII route-vi KHÔNG parse được — giữ quyền fold nhóm b,
  KHÔNG mở rộng sang subject QD57 đã loại: g2p re-check
  `scope_exclusion_status()` trên ứng viên fold trước khi phát âm (D18-01).
- Pin runtime: `g2p_resource_pins.json` + `g2p_policy_hash()` — mutation bảng
  → hash D đổi + load_fold từ chối (sha lệch).
- Bảng KHÔNG phải "phục hồi dấu": tone_state của record sinh ra = "fold",
  provenance ascii→fold + freq_top1 + margin ghi trong detail từng unit.
