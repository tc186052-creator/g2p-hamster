## Demo — nghe thử 400 clip + toàn bộ số liệu

**Nghe: bấm vào clip → trang GitHub → Download raw → tải về nghe ngay** (GitHub không phát audio trực tiếp được — mọi repo đều vậy). 400 clip MP3 (4 bộ × 100 câu, 42 phút, 24 kHz, ~14MB) render bằng đúng G2P này, mỗi clip được **2 engine STT độc lập** (PhoWhisper-large của VinAI + Whisper-large-v3 của OpenAI) nghe ngược lại để kiểm chứng.

| Bộ | Số clip | Nội dung | Thời lượng |
|---|---|---|---|
| [`vietnamese`](listening_test/audio/vietnamese) | 100 | thuần tiếng Việt (tối đa đơn vị 2 chữ kiểu "km") | 8 phút |
| [`english`](listening_test/audio/english) | 100 | thuần tiếng Anh (Wikipedia tiếng Anh) | 16 phút |
| [`mix_easy`](listening_test/audio/mix_easy) | 100 | vi pha 1–2 từ latin đơn giản | 6 phút |
| [`mix_hard`](listening_test/audio/mix_hard) | 100 | vi pha ≥3 từ latin / tên riêng nước ngoài | 11 phút |

Vài clip mẫu — bấm là tải:

| Clip | Đọc câu | Whisper-v3 nghe lại |
|---|---|---|
| [▶ vietnamese #027](listening_test/audio/vietnamese/027_vietnamese.mp3) | Hình tứ giác với độ dài các cạnh a, b, c, d mà có diện tích . | ✅ khớp 100% |
| [▶ english #060](listening_test/audio/english/060_english.mp3) | The passageway is also accessible from the stairs at the rear of the auditorium. | ✅ khớp 100% |
| [▶ mix_easy #003](listening_test/audio/mix_easy/003_mix_easy.mp3) | Chúng tôi dự định sẽ chiến đấu đến cùng. | ✅ khớp 100% |
| [▶ mix_hard #046](listening_test/audio/mix_hard/046_mix_hard.mp3) | Các nguồn cũ khác bao gồm Nihon Ryōiki (810–824) và Wamyō Ruijushō (k. | khớp v3 50% |

### Kết quả kiểm chứng STT ngược (độ khớp với văn bản được đọc)

| Bộ | Khớp hoàn toàn (PhoWhisper) | Khớp hoàn toàn (Whisper-v3) | ≥95% từ khớp (Pho / v3) | Độ khớp TB (Pho / v3) |
|---|---|---|---|---|
| `vietnamese` | 68/100 | 68/100 | 71 / 74 | 96.4% / 96.8% |
| `english` | 18/100 | 38/100 | 29 / 54 | 86.4% / 93.3% |
| `mix_easy` | 69/100 | 66/100 | 78 / 66 | 96.0% / 92.4% |
| `mix_hard` | 24/100 | 39/100 | 40 / 49 | 88.7% / 92.4% |

Đọc: **thuần việt và mix đơn giản ~96% khớp từ**; bộ khó thấp hơn do thiết kế (nhồi tên riêng nước ngoài). Kết quả ai cũng tái lập được bằng cách chạy STT bất kỳ trên các MP3 trong repo.

### So sánh — nguyên tắc: so tiếng Việt với model đọc được tiếng Việt, so tiếng Anh với model đọc được tiếng Anh

Ba hệ chạy **đúng cùng bộ câu**, mỗi hệ dùng nguyên pipeline + giọng riêng của nó. Bảng tổng hợp 3 mô hình × 4 bộ (chỉ tham khảo — model anh gốc đọc tiếng Việt thua là hiển nhiên, không tính là chiến thắng):

| Bộ | Mô hình | Khớp hoàn toàn (Pho / v3) | TB (Pho / v3) |
|---|---|---|---|
| `vietnamese` | Kokoro gốc (chưa fine-tune) | 1/100 · 1/100 | 29.8% / 23.6% |
| `vietnamese` | Kokoro-Vietnamese (iamdinhthuan) | 60/100 · 62/100 | 95.5% / 95.9% |
| `vietnamese` | Kokoro vi — repo này | 68/100 · 68/100 | 96.4% / 96.8% |
| `english` | Kokoro gốc (chưa fine-tune) | 30/100 · 45/100 | 87.4% / 90.2% |
| `english` | Kokoro-Vietnamese (iamdinhthuan) | 12/100 · 26/100 | 81.3% / 88.8% |
| `english` | Kokoro vi — repo này | 18/100 · 38/100 | 86.4% / 93.3% |
| `mix_easy` | Kokoro gốc (chưa fine-tune) | 1/100 · 0/100 | 37.0% / 24.7% |
| `mix_easy` | Kokoro-Vietnamese (iamdinhthuan) | 51/100 · 50/100 | 88.6% / 87.8% |
| `mix_easy` | Kokoro vi — repo này | 69/100 · 66/100 | 96.0% / 92.4% |
| `mix_hard` | Kokoro gốc (chưa fine-tune) | 2/100 · 0/100 | 48.5% / 31.8% |
| `mix_hard` | Kokoro-Vietnamese (iamdinhthuan) | 13/100 · 19/100 | 82.7% / 85.8% |
| `mix_hard` | Kokoro vi — repo này | 24/100 · 39/100 | 88.7% / 92.4% |

#### 🇻🇳 Solo thuần tiếng Việt — chỉ giữa 2 model đọc được tiếng Việt

(Kokoro gốc loại khỏi cuộc — model tiếng Anh, không đọc được tiếng Việt: 1/100)

| Mô hình | Khớp hoàn toàn (Pho / v3) | TB (Pho / v3) |
|---|---|---|
| Kokoro-Vietnamese (iamdinhthuan) | 60/100 · 62/100 | 95.5% / 95.9% |
| Kokoro vi — repo này ⭐ | 68/100 · 68/100 | 96.4% / 96.8% |

#### 🇬🇧 Solo thuần tiếng Anh — Kokoro gốc với GIỌNG ANH GỐC af_heart (cho model anh cơ hội tốt nhất), không ép giọng vi

(Kokoro-Vietnamese không phải model anh: 12/100 · 26/100)

| Mô hình | Khớp hoàn toàn (Pho / v3) | TB (Pho / v3) |
|---|---|---|
| Kokoro gốc + af_heart (giọng native) | 29/100 · 44/100 | 86.2% / 89.7% |
| Kokoro vi — repo này ⭐ | 18/100 · 38/100 | 86.4% / 93.3% |

Thư mục audio: [`audio/`](listening_test/audio) (repo này) · [`audio_baseline/`](listening_test/audio_baseline) (Kokoro gốc, giọng khanhlinh1) · [`audio_afheart/`](listening_test/audio_afheart) (Kokoro gốc + giọng anh gốc af_heart) · [`audio_kokoro_vietnamese/`](listening_test/audio_kokoro_vietnamese) (iamdinhthuan) — cùng đánh số, bấm đối chứng trực tiếp.

### Chỗ không khớp — lệch ở đâu, vì sao? (736 chỗ, cả 2 engine)

Dấu câu đã loại khỏi phép so khớp — **không bao giờ là nguyên nhân**:

| Loại lệch | Số chỗ | Ví dụ | Tính chất |
|---|---|---|---|
| Chép gần đúng tên riêng | 147 | "Biltmore"→"billmore" | nhiễu đo — ASR chép tên theo chữ nó biết |
| Liên quan số | 113 | "năm"→"5" | 2 cách viết cùng nội dung |
| Khác dấu/chính tả | 64 | "hóa"/"hoá" (đều chuẩn) | phần lớn vô hại; vài ca "đày"/"đẩy" cần nghe |
| ASR bỏ/thừa từ | 48 | ASR bỏ hẳn "gave twelve million dollars" | lỗi của ASR |
| **Từ nghe khác thật** | **364** | "ra"→"da", "dốc"→"rốc" | **cần tai người** — ASR nhầm hoặc TTS đọc lệch |

Theo bộ, "từ nghe khác thật": vietnamese 65 · mix_easy 43 · mix_hard 125 · english 131 (tên riêng nước ngoài).

### Ba điểm ưu tiên cho đánh giá nghe (lớp 2 — chờ người duyệt)

1. **Phụ âm đầu d/r**: "ra" nghe như "da" lặp nhiều lần trong 1 clip (`vietnamese` #8) — TTS đọc lệch hay ASR nhầm giọng miền Bắc?
2. **Thanh điệu**: vài ca kiểu "đày"/"đẩy".
3. **Tên riêng nước ngoài** trong `mix_hard`/`english` — 2 engine cùng chép khác nhau và khác cả đáp án.

LƯU Ý: STT ngược đo **độ dễ hiểu** (nghe ra lại đúng chữ), KHÔNG thay thế đánh giá của tai người; **chưa tuyên bố "đọc đúng"** cho đến khi lớp 2 hoàn tất.

### Dữ liệu máy đọc được

- [`listening_test/review_sheet.tsv`](listening_test/review_sheet.tsv) — 400 câu + kết quả 2 ASR + cột chấm tay (nguồn từng câu: Wikipedia vi/en CC BY-SA, Tatoeba CC BY)
- [`listening_test/asr_roundtrip.csv`](listening_test/asr_roundtrip.csv) — nguyên văn 2 engine đọc lại 400 clip
- [`listening_test/mismatch_analysis.csv`](listening_test/mismatch_analysis.csv) — 736 chỗ lệch, từng chỗ kèm đáp án ↔ text ASR
