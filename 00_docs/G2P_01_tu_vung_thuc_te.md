# G2P 01 — Từ vựng thực tế tầng 2 phải đọc được

Ngày: 01/10/2026. Nguồn: mẫu 200.000 câu từ corpus silver 1M (bản 01/10).
Dữ liệu thô: `G2P_01_tu_vung_data.json` (top 500 latin-en, top 300 latin-vi theo tần suất).

## Con số tổng

| Nhóm | Số token unique | Tổng lần xuất hiện | Ghi chú |
|---|---|---|---|
| latin, route **en** | 37.689 | 576.252 | tiếng Anh thật + tên riêng + tech terms |
| latin, route **vi** | 40.305 | 594.639 | **chủ yếu là TIẾNG VIỆT KHÔNG DẤU** |
| vi có dấu, luật không chắc (OOV/kho bắt) | nhỏ (đang đo lại) | — | tần suất thấp |

## Điểm mấu chốt cho thiết kế G2P

1. **Latin route-vi ≈ tiếng Việt không dấu**: top đầu là `trong, cho, khi, anh, ra, sau,
   nam, theo, gia, con, quan…` — G2P KHỂ dạng "latin → vi" phải phiên âm tiếng Việt.
   Hai biện pháp tự nhiên: (a) từ điển fold → âm có dấu (fold "trong" = "trong" — từ
   không dấu trùng từ có dấu sau khi bỏ dấu, tra ngược theo tần suất); (b) luật phụ âm
   đầu/vần đọc theo cách vi. Đây là đặc thù lớn của corpus (tin tức vi lẫn latin).
2. **Latin route-en là tiếng Anh thật** ở các câu en/mixed: top = function words
   (`the, to, and, of…`) + tên riêng (Tom…) — cần phát âm en. Nhánh en nên là từ điển
   từ phổ biến + luật phiên âm giản lược; tail 37k phần lớn là tên riêng hiếm
   (đọc sai mức độ chấp nhận được ban đầu, có thể thay bằng tiny model sau).
3. **Tail dài**: 37k+40k unique nhưng tần suất giảm mạnh — từ điển ~3-5k entry đầu
   phủ phần lớn lần xuất hiện (đã kèm data trong JSON để tính độ phủ chính xác).

## Việc đề xuất khi chọn thiết kế (CHƯA làm)

- Tính đường cong độ phủ (top-k entry phủ bao nhiêu % lần gặp) từ JSON này.
- Đối chiếu top latin-en với từ điển en sẵn có của phương án G2P được chọn.
