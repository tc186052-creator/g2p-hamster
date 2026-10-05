# Đề bài phiên chấm E4 — 9B judge (MÙ)

## Bằng chứng phiên
- Bộ judge: `fase_e_judge_set.jsonl` — sha256 `b8743e90544ad1d7…` (đóng băng;
  đổi bộ = phiên mới, version hoá).
- Số item: 500 · seed xáo A/B: 20261002 · sinh bởi
  `fase_e_judge_sample.py prepare` (nit v23-01: session đã strip
  status/verbal — judge chỉ thấy surface + route + A/B).
- Model chấm: ______ (ghi rõ model + revision + quantization trước khi chạy).
- Ngày + người cùng chủ dự án: ______.

## Luật chấm (bắt buộc đọc cho judge)
1. Judge thấy mỗi token ở dạng: bề mặt + route + 2 phương án đọc `A`/`B`
   (ký hiệu kokoro mũi tên). Judge KHÔNG biết phương án nào do hệ nào sinh.
2. **Quy ước dấu nhấn (phiên v2):** dấu nhấn `ˈ` `ˌ` ĐÃ BỎ khỏi CẢ HAI phương án trước khi trình bày — đúng quy ước so sánh E3 đã khai báo (tool gắn stress cả âm tiết vi, hệ mình không gắn). Nếu vẫn thấy ký tự lạ, bỏ qua — không chấm.
3. Judge KHÔNG chấm phoneme-level đúng/sai tuyệt đối — chỉ chọn phương án
   ĐỌC TỰ NHIÊN / HỢP LÝ hơn cho tiếng Việt (route en: đọc tiếng Anh hợp lý).
4. Mỗi item ĐÚNG 1 quyết trong `{A, B, hoa, ca_hai_sai, khong_du_tin}`
   + lý do ngắn (1 câu). Điền vào trường `verdict` / `reason` của
   `fase_e_judge_session.jsonl`.
5. Không sửa trường nào khác của session JSONL. Phiếu thiếu verdict hoặc
   verdict ngoài enum sẽ bị loại khi tổng hợp.
6. File `fase_e_judge_session_key.json` là KHOA — không cho judge xem.
7. Sau phiên: chủ dự án chạy `fase_e_judge_sample.py spotcheck --n 20`
   và kiểm tay ≥20 phiếu ngẫu nhiên (chống ảo giác hàng loạt).
