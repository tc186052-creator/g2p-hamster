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

Đọc: **thuần việt và mix đơn giản ~96% khớp từ**; bộ khó thấp hơn do thiết kế (nhồi tên riêng nước ngoài). Ba giới hạn cần biết khi đọc bảng:

1. **Đo END-TO-END** — cả chuỗi G2P + model TTS + giọng; bảng này **chưa cô lập đóng góp riêng của G2P** (muốn cô lập phải so cùng một model TTS với các front-end khác nhau — chưa làm).
2. **Điểm khớp đo qua STT = giả thuyết mạnh về phát âm đúng, không phải chứng minh tuyệt đối**: điểm thấp có thể do TTS đọc lệch *hoặc* do ASR chép sai; riêng các chỗ "từ nghe khác thật" ở bảng dưới cần tai người phân xử.
3. **Tái lập số liệu**: chạy script công khai [`listening_test/verify_roundtrip.py`](listening_test/verify_roundtrip.py) trên dữ liệu trong repo — nó chấm lại từng clip từ transcript đã công bố (cùng phép đo: token NFC, bỏ dấu câu, edit-distance, đáp án tốt nhất giữa verbal_ref và văn bản gốc) và in ra đúng các số trên bảng. Chạy STT bằng engine bất kỳ khác trên các MP3 là so kiểm tra chéo — lệch nhẹ engine-to-engine là bình thường, không phải lỗi phép đo.

### So sánh — nguyên tắc: so tiếng Việt với model đọc được tiếng Việt, so tiếng Anh với model đọc được tiếng Anh

Ba hệ chạy **đúng cùng bộ câu**, mỗi hệ dùng nguyên pipeline + giọng riêng của nó. Bảng tổng hợp 3 mô hình × 4 bộ (chỉ tham khảo — model anh gốc đọc tiếng Việt thua là hiển nhiên, không tính là chiến thắng):

| Bộ | Mô hình | Khớp hoàn toàn (Pho / v3) | TB (Pho / v3) |
|---|---|---|---|
| `vietnamese` | Kokoro gốc (chưa fine-tune) | 1/100 · 1/100 | 29.8% / 23.6% |
| `vietnamese` | Kokoro-Vietnamese (iamdinhthuan) | 60/100 · 62/100 | 95.5% / 95.9% |
| `vietnamese` | Kokoro vi — repo này | 68/100 · 68/100 | 96.4% / 96.8% |
| `english` | Kokoro gốc (chưa fine-tune) | 30/100 · 45/100 | 87.4% / 90.2% |
| `english` | Kokoro-Vietnamese (iamdinhthuan) | 12/100 · 26/100 | 81.4% / 88.9% |
| `english` | Kokoro vi — repo này | 18/100 · 38/100 | 86.4% / 93.3% |
| `mix_easy` | Kokoro gốc (chưa fine-tune) | 1/100 · 0/100 | 37.0% / 24.7% |
| `mix_easy` | Kokoro-Vietnamese (iamdinhthuan) | 52/100 · 51/100 | 88.8% / 88.0% |
| `mix_easy` | Kokoro vi — repo này | 69/100 · 66/100 | 96.0% / 92.4% |
| `mix_hard` | Kokoro gốc (chưa fine-tune) | 2/100 · 0/100 | 48.5% / 31.8% |
| `mix_hard` | Kokoro-Vietnamese (iamdinhthuan) | 13/100 · 19/100 | 83.0% / 85.8% |
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

Đọc công bằng bộ anh: đây là **trao đổi, không phải thắng toàn diện** — af_heart khớp hoàn toàn NHIỀU HƠN (29/100 Pho · 44/100 v3 so với 18/100 · 38/100 của repo này), còn repo này cao hơn ở độ khớp TB. Không tuyên bố "thắng tiếng Anh toàn diện".


Lưu ý chung cho cả 2 solo: so là **toàn hệ** — mỗi hệ dùng cả front-end riêng của nó (repo này dùng G2P v2 trong repo; iamdinhthuan dùng phonemizer vig2p của họ; Kokoro gốc chạy qua G2P v2 của repo khi đọc vi/mix). Bảng đo chất lượng hệ hoàn chỉnh, không tách riêng contribution của từng tầng.

Thư mục audio: [`audio/`](listening_test/audio) (repo này) · [`audio_baseline/`](listening_test/audio_baseline) (Kokoro gốc, giọng khanhlinh1) · [`audio_afheart/`](listening_test/audio_afheart) (Kokoro gốc + giọng anh gốc af_heart) · [`audio_kokoro_vietnamese/`](listening_test/audio_kokoro_vietnamese) (iamdinhthuan) — cùng đánh số, bấm đối chứng trực tiếp.

### Chỗ không khớp — lệch ở đâu, vì sao? (736 chỗ, cả 2 engine)

Dấu câu đã loại khỏi phép so khớp — **không bao giờ là nguyên nhân**. Phân loại dưới đây suy ra **từ text ASR** — là giả thuyết kèm đánh giá độ tin cậy, KHÔNG phải kết luận đã kiểm chứng bằng tai người:

| Loại lệch | Số chỗ | Ví dụ | Tính chất |
|---|---|---|---|
| Chép gần đúng tên riêng | 147 | "Biltmore"→"billmore" | giả thuyết: nhiễu đo — ASR chép tên theo chữ nó biết |
| Liên quan số | 113 | "năm"→"5" | 2 cách viết cùng nội dung |
| Khác dấu/chính tả | 64 | "hóa"/"hoá" (đều chuẩn) | phần lớn vô hại; vài ca "đày"/"đẩy" cần nghe
| ASR bỏ/thừa từ | 48 | ASR bỏ hẳn "gave twelve million dollars" | giả thuyết: ASR sót/thừa khi chép — cần nghe xác nhận |
| **Từ nghe khác thật** | **364** | "ra"→"da", "dốc"→"rốc" | **cần tai người** — ASR nhầm hoặc TTS đọc lệch, chưa phân xử được |

Theo bộ, "từ nghe khác thật": vietnamese 65 · mix_easy 43 · mix_hard 125 · english 131 (tên riêng nước ngoài).

### Ba điểm ưu tiên cho đánh giá nghe (lớp 2 — chờ người duyệt)

1. **Phụ âm đầu d/r**: "ra" nghe như "da" lặp nhiều lần trong 1 clip (`vietnamese` #8) — TTS đọc lệch hay ASR nhầm giọng miền Bắc?
2. **Thanh điệu**: vài ca kiểu "đày"/"đẩy".
3. **Tên riêng nước ngoài** trong `mix_hard`/`english` — 2 engine cùng chép khác nhau và khác cả đáp án.

LƯU Ý: STT ngược đo **độ dễ hiểu** (nghe ra lại đúng chữ), KHÔNG thay thế đánh giá của tai người; **chưa tuyên bố "đọc đúng"** cho đến khi lớp 2 hoàn tất.

### Dữ liệu máy đọc được

- [`listening_test/review_sheet.tsv`](listening_test/review_sheet.tsv) — 400 câu + verbal_ref (văn bản tầng 1 đã verbalize) + kết quả 2 ASR + cột chấm tay (nguồn từng câu: Wikipedia vi/en CC BY-SA, Tatoeba CC BY)
- [`listening_test/asr_roundtrip.csv`](listening_test/asr_roundtrip.csv) — nguyên văn 2 engine đọc lại 400 clip của model repo này
- [`listening_test/asr_roundtrip_all_models.csv`](listening_test/asr_roundtrip_all_models.csv) — transcript + điểm từng clip của **tất cả các model** (ours / kokoro_goc / kokoro_vietnamese / kokoro_goc_afheart — afheart chỉ bộ english)
- [`listening_test/mismatch_analysis.csv`](listening_test/mismatch_analysis.csv) — 736 chỗ lệch, từng chỗ kèm đáp án ↔ text ASR
- [`listening_test/verify_roundtrip.py`](listening_test/verify_roundtrip.py) — script chấm lại toàn bộ từ CSV trên (stdlib, không cần cài gì), in ra bảng khớp với README

### Cấu hình thực nghiệm — provenance của bộ demo

| Thành phần | Giá trị |
|---|---|
| G2P (repo này + Kokoro gốc khi đọc vi/mix) | bản v2 trong repo — policy hash in trong mọi đầu ra; `espeak-ng` opt-in |
| Model TTS — repo này | checkpoint nội bộ `logs/m8_mspk6_s2/epoch_best.pth` (không phát hành weights); voicepack `mspk6/khanhlinh1.pt` (sha256 974a81fbf5d9e3c9…) |
| Model TTS — Kokoro gốc | `kokoro_v1_0_wrapped.pth` (sha256 791e249989b50dcb…) đọc vi/mix bằng voicepack `khanhlinh1` như trên; solo anh dùng giọng native `af_heart.pt` (sha256 0ab5709b8ffab19b…) |
| Model TTS — Kokoro-Vietnamese | HF `contextboxai/Kokoro-Vietnamese` (`kokoro_vi.pth` + voicepack `diem_trinh`, mặc định của thư viện), phonemizer vig2p — pipeline nguyên vẹn của tác giả |
| Render | 24 kHz mono, chunk ≤510 token profile, gộp câu ngắn, siết 0,1s đầu/đuôi nhóm, khử nhiễu 3 lớp (`khu_am`); speed 1.0 |
| STT | faster-whisper `beam_size=5`, `compute_type=float16`; PhoWhisper-large CT2 + Whisper-large-v3; `language=vi` (bộ `english`: `en`) |
| Phép chấm | token NFC lowercase bỏ dấu câu; acc = 1 − edit-distance / độ dài đáp án; đáp án = tốt nhất giữa `verbal_ref` và văn bản gốc; "khớp hoàn toàn" = acc ≥ 0.999 |

Chưa ghi nhận được (nói thẳng là thiếu): revision/commit cụ thể của repo HF `contextboxai/Kokoro-Vietnamese` và của `large-v3` tại thời điểm render — ai tái lập bằng bản hiện tại có thể lệch nhẹ; weights checkpoint của repo này không phát hành (thuộc dự án nội bộ).

