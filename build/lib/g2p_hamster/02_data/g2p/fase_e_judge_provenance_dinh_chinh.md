# ĐÍNH CHÍNH hồ sơ phiên E4 — Nit v24-02 (reviewer, vòng v24)

Áp dụng cho CẢ `fase_e_judge_provenance_v1.json` và
`fase_e_judge_provenance.json` (phiên v2):

> Chuỗi `"batch=12"` trong trường `decoding` là **literal lỗi thời của
> runner** (bản template trước khi tăng batch), được ghi nguyên vào provenance.
> **Batch thực thi = 24** — hằng số `BATCH = 24` (dòng 156 runner, vòng lặp
> chia lô theo `BATCH`); khớp ghi chú OOM ("batch 24 sát trần 12GB") và
> header bundle v24.

Vì runbook pin "đổi batch = phiên khác", đính chính minh bạch thay vì sửa lén
file provenance của phiên (bảo toàn tính toàn vẹn bằng chứng — số liệu phiên
không bị ảnh hưởng: greedy per-item bất biến theo lô; mọi phân bố, 186
regression, spot-check đều được reviewer tái lập độc lập khớp).

Runner đã sửa sang nội suy `batch={BATCH}` từ v25 — provenance sinh sau này
sẽ tự mang đúng số.

Truy vết sha runner: provenance v1/v2 ghi `09832d36…` — ĐÚNG là bản đã sinh
hai phiên (chứa literal cũ); bản hiện hành sau sửa = `2a1f642c…` (nội suy
batch={BATCH}, manifest v25). Hai sha nối tiếp hợp lệ, không mâu thuẫn.

— 02/10/2026, theo PHAN_QUYET_E4_V24.md §3 (bổ sung truy vết sha theo gợi ý PHAN_QUYET v25 §2)

## Bổ sung — Nit v26-04: bảng thanh trong PROMPT của judge runner SAI so với hệ thật

Các phiên E4 v1/v2 đã chạy với PROMPT_TEMPLATE dạy judge bảng thanh **sai**:
"`↘=hỏi, ↓=ngã, →=nặng`". Hệ thật (TONE_TO_ARROW — khớp dữ liệu phiên):
`↗`=sắc · `↘`=huyền · `↓`=hỏi · ngã = `ʔ↗` · nặng = `ʔ↓` · `→` KHÔNG bao giờ
phát sinh. Judge bị "dạy sai bảng" — một phần giải thích vì sao nó lẫn thanh
(giải thích thêm, KHÔNG đảo kết luận E4: mọi flag giữ nguyên dạng candidate
cho policy [B]). File PROMPT_TEMPLATE đã sửa từ v27; provenance sha prompt
`c216c8e8…` của phiên cũ giữ nguyên (bằng chứng đúng như đã chạy).

— 02/10/2026, theo PHAN_QUYET_V26.md §5 (v26-04)
