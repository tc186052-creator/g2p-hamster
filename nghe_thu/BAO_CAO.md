# Báo cáo bộ nghe thử 4×100 câu — kết quả lớp 1 (STT ngược kép)

Cập nhật: lần 1 (chưa có kết quả lớp 2 — người nghe).

## 1. Mục đích và phạm vi

Minh chứng công khai cho chất lượng đọc của chuỗi text‑to‑speech tiếng Việt:
**text → G2P (luật + từ điển, provenance từng từ) → TTS kiến trúc Kokoro
(checkpoint nội bộ ứng viên, giọng A)**. Audio do chuỗi trên tự sinh 100%.

Bộ câu gồm **4 nhóm × 100 câu = 400 clip** (24 kHz mono PCM16, tổng 42 phút):

| Bộ | Nguồn câu | Đặc điểm |
|---|---|---|
| `thuan_viet` | Wikipedia tiếng Việt | không có từ latin ≥3 chữ (tối đa đơn vị 2 chữ kiểu "km") |
| `thuan_anh` | Wikipedia tiếng Anh | câu ASCII thuần |
| `mix_de` | Wikipedia tiếng Việt / Tatoeba | vi pha 1–2 từ latin |
| `mix_kho` | Wikipedia tiếng Việt | vi pha ≥3 từ latin / tên riêng nước ngoài |

## 2. Phương pháp kiểm chứng — 2 lớp

- **Lớp 1 (tự động, có thể tái lập):** mỗi WAV được **hai mô hình ASR độc
  lập** — PhoWhisper‑large (VinAI) và Whisper‑large‑v3 (OpenAI) — nghe lại,
  so với văn bản thực tế được đọc (số/ngày đã verbalize thành chữ; mỗi
  engine được so với dạng tham chiếu tốt nhất cho chính nó).
- **Lớp 2 (người nghe):** chấm theo `duyet.tsv`. Tiêu chí **đọc đúng**: mọi
  từ nội dung được phát âm, không từ nào đọc sai. Kết quả lớp 2 sẽ cập nhật
  trong báo cáo này.

Dấu câu được loại khỏi phép so khớp nên **không bao giờ là nguyên nhân lệch**.

## 3. Kết quả lớp 1

| Bộ | Khớp hoàn toàn (Pho) | Khớp hoàn toàn (v3) | ≥95% từ khớp (Pho / v3) | Độ khớp TB (Pho / v3) |
|---|---|---|---|---|
| `thuan_viet` | 68/100 | 68/100 | 71 / 74 | 96,4% / 96,8% |
| `thuan_anh` | 18/100 | 38/100 | 29 / 54 | 86,4% / 93,3% |
| `mix_de` | 69/100 | 66/100 | 78 / 66 | 96,0% / 92,4% |
| `mix_kho` | 24/100 | 39/100 | 40 / 49 | 88,7% / 92,4% |

Đọc: **bộ thuần việt và mix đơn giản đạt ~96% khớp trung bình** — 2/3 câu
nghe ra lại đúng 100% từng từ. Bộ khó thấp hơn là do thiết kế (nhồi tên
riêng nước ngoài). Kết quả ai cũng tái lập được bằng cách chạy STT bất kỳ
trên các WAV trong repo.

## 4. Chỗ không khớp — lệch ở đâu, vì sao?

Toàn bộ 736 chỗ lệch (cả 2 engine, 400 clip) được so **từng từ** và phân
loại trong `phan_tich_lech.csv`:

| Loại lệch | Số chỗ | Tính chất |
|---|---|---|
| Chép gần đúng tên riêng | 147 | ASR chép tên theo chữ nghe được ("Biltmore"→"billmore") — nhiễu đo, không thể quy lỗi TTS |
| Liên quan số | 113 | ASR ghi "5", đáp án "năm" — 2 cách viết cùng nội dung |
| Khác dấu/chính tả dấu | 64 | Cùng chữ cái gốc, khác dấu ("hóa"/"hoá" là 2 cách viết chuẩn); vài ca kiểu "đày"/"đẩy" cần nghe |
| ASR bỏ/thừa từ | 48 | Lỗi của chính ASR (bỏ hẳn cả cụm "gave twelve million dollars") |
| **Từ nghe khác thật** | **364** | Cần tai người: ASR nhầm hoặc TTS đọc lệch |

**Theo bộ:** `thuan_viet` chỉ còn 65 chỗ "từ nghe khác thật" trên 100 câu;
phần lớn số còn lại thuộc `thuan_anh` (131) và `mix_kho` (125) — tập trung
quanh tên riêng nước ngoài, đúng thiết kế của hai bộ này.

## 5. Điểm cần tai người quyết định (hạng mục ưu tiên lớp 2)

1. **Phụ âm đầu d/r**: có chỗ ASR nghe "ra" thành "da" lặp nhiều lần trong
   1 clip (`thuan_viet` #8) — cần xác định TTS đọc lệch hay ASR nhầm giọng
   miền Bắc.
2. **Thanh điệu**: vài ca kiểu "đày"/"đẩy" — ASR ghi dấu khác.
3. **Tên riêng nước ngoài** trong `mix_kho` / `thuan_anh`: 2 engine cùng
   chép khác nhau và khác cả đáp án — chỉ tai người phán được.

## 6. Kết luận hiện tại

- Lớp 1 cho thấy chuỗi đọc đủ và ổn định ở mức **~93–97% khớp từ** trên
  văn bản vi; phần lệch có thể giải thích được chiếm đa số, phần thật sự
  cần tai người còn ~364 chỗ/400 clip — đã chỉ đích danh từng chỗ.
- **Chưa tuyên bố "đọc đúng"** cho đến khi lớp 2 hoàn tất — đúng nguyên
  tắc: STT ngược đo độ dễ hiểu, không thay thế đánh giá của tai người.

## 7. Nguồn & giấy phép

- Câu trích Wikipedia tiếng Việt / tiếng Anh (CC BY‑SA), Tatoeba (CC BY),
  web tiếng Việt (trích dẫn 1 câu, ghi nguồn từng câu trong `duyet.tsv`).
- Audio và bảng trong repo phát hành CC BY‑SA 4.0.
- ASR: PhoWhisper (MIT), Whisper (MIT).
