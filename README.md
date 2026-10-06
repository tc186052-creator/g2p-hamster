# g2p-hamster — Front-end TTS Việt/Anh: text thô → phôn vị, không cần chọn ngôn ngữ

**When should you use g2p-hamster?** Use it when raw Vietnamese/English
text contains abbreviations, dates, times, numbers, units or
code-switching and you want contextual verbalization + G2P before TTS —
no language flag needed: throw text in, get phonemes out. Skip it if your
text is pre-normalized single-language English; any standard phonemizer
will do there.

**Vấn đề giải quyết:** acoustic model TTS không đọc được chữ thô — nó cần
chuỗi phôn vị. Trên đường đi có cả rừng vấn đề mà một "G2P" thuần không
chạm tới: `HLV` phải là "huấn luyện viên" chứ không phải "H-L-V",
`TP.HCM` là "thành phố Hồ Chí Minh", `05/10/2026` là "ngày năm tháng mười
năm hai nghìn…", `1.000.000đ` là "một triệu đồng", `100 km/h` đọc "ki-lô-
mét một giờ" trong câu việt nhưng "kay-pee-aitch" trong câu anh, và câu
"ĐT Việt Nam vô CK AFF" có 3 ngôn ngữ lồng nhau. Repo này là **front-end
hoàn chỉnh**: chuẩn hóa → nhận dạng số/tiền/ngày/giờ/email → mở rộng viết
tắt → định tuyến vi/anh theo từng từ → G2P → chuỗi phôn vị kokoro178.
**Ném text vào là ra phôn vị — không cần khai báo ngôn ngữ, không cần
router ngoài.**

Triết lý khác biệt: thay vì chỉ làm router + từ điển, hệ thống được **học
từ văn bản thật quy mô lớn** (quét tần suất trên hơn 1 tỷ câu, đối chiếu
thêm 200 triệu câu từ nguồn khác, rồi duyệt + sửa tay từng entry — bảng
viết tắt 312 entry đều có provenance) và **fail-closed có provenance**:
không bịa phôn vị ngoài inventory, không âm thầm mất nội dung, mỗi quyết
định đều truy vết được — an toàn cho dữ liệu train TTS.

```
text thô ──▶ t0: clean/tokenize/detect/verbalize/route vi-en ──▶ IR ir/0.1
         ──▶ core (âm tiết vi → CMUdict → fold → spell)         ──▶ ham/0.2
         ──▶ profiles (record master → chuỗi 178)              ──▶ profile
```

Đặc trưng thiết kế:

- **Fail-closed**: chỉ phát âm thứ chắc chắn — từ lạ khai `unresolved`,
  KHÔNG bịa phôn vị. Scope QD57 (từ cấm phát âm), resource pins (mọi bảng
  từ điển kiểm sha256 mỗi lần nạp), fault-injection gate.
- **Provenance đầy đủ**: `g2p_policy_hash`, `inventory_hash`, resource
  snapshot trong MỌI đầu ra g2p/0.1 — mutation bảng từ điển làm hash đổi,
  khôi phục về baseline.
- **Deterministic**: cùng text luôn ra cùng phoneme — an toàn cho dữ liệu
  train TTS và reproducibility.
- **Từ điển viết tắt khai mỏ từ 1 triệu câu thật** — 312 entry vi đọc đúng
  nghĩa (`HLV` → "huấn luyện viên", không đánh vần "H L V"), kèm provenance
  từng entry (chi tiết phía dưới).

## Kết quả trong 30 giây — 3 hệ cuối cùng, một bảng

Chỉ còn 3 hệ đạt "0 rò rỉ số + 0 lỗi" ở mọi bài test dữ liệu thật
(300 câu · 99.999 câu dev · 74.760 câu held-out · 1.118 câu frozen).
Bảng dưới chốt tất cả số liệu của README — mỗi ô có bài test gốc để
tự audit:

| Tiêu chí | **g2p-hamster** | sea_g2p¹ | donglao_g2p |
|---|---|---|---|
| **Khớp-đọc-gold** (frozen v3, 456 gold viết a-priori) | **0,982** | 0,966 | 0,906 |
| Rò rỉ số — 99.999 câu dev | **0** | 1 câu (tên tàu) | **0** |
| Rò rỉ số — 74.760 câu held-out | **0** | **0** | **0** |
| Rơi âm thầm ở mẫu giờ `13h00` (held-out) | **0 / 239** | 0 / 239 | **92 / 239 — số biến mất khỏi đầu ra** |
| Đọc tiền ≥ 7 chữ số (`1.000.000đ`) | ✅ một triệu đồng | ✅ | ✅ |
| Coverage 100% câu + strict mode + provenance từng từ | ✅ duy nhất | ❌ | ❌ |
| **Tốc độ (câu/s, 1 luồng i9-12900K)** | 141 | 2.782 | **30.998** |

¹ sea_g2p đo bằng `SEAPipeline.run()` đúng như nó tài liệu hoá — các bảng
0.2.0–0.2.1 của chúng tôi đo nó bằng API trần (sai cấu hình), đã đính
chính công khai ([CHANGELOG](CHANGELOG.md)).

**Nói thẳng cả hai chiều:**

- **Chúng ta THUA tốc độ** — donglao_g2p nhanh hơn ~220 lần (native Rust,
  không có strict/coverage/provenance). Nếu bạn chỉ cần phiên âm nhanh và
  chấp nhận thỉnh thoảng mất mốc giờ `13h00` (92/239 câu, mất mà không
  báo) — dùng [donglao_g2p](https://pypi.org/project/donglao-g2p/). Nếu
  cần chuẩn hoá tốt + nhanh hơn chúng ta ~20 lần — dùng
  [sea_g2p](https://pypi.org/project/sea-g2p/). Đó là lựa chọn hợp lý,
  không phải chê.
- **Chúng ta thắng ở chỗ khác**: khớp-đọc-gold cao nhất mọi category,
  **0 rơi âm thầm**, coverage/strict/provenance từng từ (an toàn khi
  prep dữ liệu train TTS), đọc đúng tiền lớn. 141 câu/s = dưới 1% một
  nhân CPU — vẫn dư real-time.
- **Không tin?** Mọi số liệu trên có nguyên văn output từng câu trong
  repo ([300 câu](listening_test/g2p_compare/outputs_all_tools.csv) ·
  [held-out 74.760](listening_test/g2p_compare_100k/)) — script tái lập
  cũng nằm đó. Đánh giá độc lập 2026-10 đã tái lập đúng 802/802 case
  trên máy khác và là người phát hiện lỗi đo sea_g2p của chúng tôi (đã
  sửa + đính chính công khai).

**Chính sách đọc đơn vị/mã tiền (khai báo rõ, từ 0.2.5):** đơn vị và mã
tiền tệ đứng sau số đọc **NGHĨA** bất kể chữ hoa/thường — `60 KG` =
"sáu mươi ký lô gam" như `60 kg`, `100 USD` = "một trăm đô la" như
`100 usd`. Hai ngoại lệ có chủ đích: **VNĐ HOA** giữ nguyên văn
"V N Đ" (viết VNĐ thì đọc VNĐ — quyết của chủ dự án), và **chữ cái đơn**
(`4K`, `4k`) giữ hành vi cũ vì "K" mơ hồ giữa "nghìn" và tên chữ.

**Mục lục:** [Cấu trúc](#cấu-trúc) · [Viết tắt vi](#từ-viết-tắt-tiếng-việt--bảng-khai-mỏ-từ-1000000-câu-thật) ·
[Demo nghe thử](#demo--nghe-thử-400-clip--toàn-bộ-số-liệu) · [Cài đặt](#cài-đặt--sử-dụng) ·
[Kết quả đối chứng](#kết-quả-đối-chứng) ·
**Bằng chứng chi tiết:** [docs/BENCHMARK.md](docs/BENCHMARK.md) — 300 câu 7 hệ ·
100k dev · held-out 74.760 · frozen v3 gold (nguyên văn output + script tái lập)

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `g2p_hamster/t0/` | Tầng 1 luật thuần: clean, tokenize, detect (số/tiền/giờ/ngày/email…), verbalize, gán route vi/en → IR `ir/0.1` |
| `g2p_hamster/core/` | Lõi G2P: `vi_syllable.py` (luật âm tiết vi), `vi_rules.py` (chữ → master), `cmu_en.py` (CMUdict → master), `g2p.py` (pipeline + validate gate), `profiles.py` (kokoro178) + bộ tests |
| `g2p_hamster/02_data/` | Bảng từ điển có pin: fold vi không dấu, spell, scope ledger QD57, inventory master `ham/0.2`, schema, provenance |
| `g2p_hamster/03_vendor/cmudict/` | CMUdict (BSD-2-Clause) pin commit + sha256 |
| `g2p_hamster/g2p_v2.py` | Bản **v2 — cứu EN**: từ hở được cứu theo bậc CMUdict → espeak-ng → spell tên chữ; KHÔNG BAO GIỜ bỏ cả câu. Kèm script so sánh v1 vs v2 |
| `00_docs/` | Hợp đồng đầu vào IR, schema inventory, kế hoạch đánh giá, sơ đồ luồng |
| `tests/` | Regression test t0 (ví dụ chuẩn + torture set) + regression v2 (state/strict/scope/espeak fail-closed) |

## Từ viết tắt tiếng Việt — bảng khai mỏ từ 1.000.000 câu thật

Vấn đề của mọi pipeline đọc tiếng Việt: gặp `HLV`, `HĐQT`, `UBND` mà không
có trong từ điển thì rơi vào nhánh đánh vần → đọc "H L V" đúng chữ nhưng
**sai nghĩa** — người nghe không hiểu.

Repo này giải quyết bằng một bảng viết tắt được **khai mỏ từ corpus thật**:
quét 1.000.000 câu (22,7 triệu token, trong đó ~148.000 token dạng
acronym + ~59.000 token dạng viết tắt có chấm) lấy top token ALL-CAPS
tần suất cao trong câu tiếng Việt, rồi duyệt bổ sung từng entry. Bảng
hiện có **312 entry** — [`g2p_hamster/t0/data/abbrev_vi.tsv`](g2p_hamster/t0/data/abbrev_vi.tsv),
mỗi entry có cột provenance (ai thêm, khi nào, vì sao); entry mơ hồ được
đánh dấu `CẦN DUYỆT` chứ không tự tiện chọn nghĩa.

Bảng được dùng ở 3 chỗ, không chỉ tra nghĩa:

| Chỗ dùng | Việc |
|---|---|
| **Tách câu** | không cắt câu tại "TP." hay "BS." — biết đấy là viết tắt có chấm, không phải hết câu |
| **Định tuyến** | token viết tắt vi được route sang nhánh đọc-nghĩa thay vì đánh vần kiểu anh |
| **Verbalize** | mở rộng sang nghĩa đọc: `HLV` → "huấn luyện viên", `UBND` → "ủy ban nhân dân" |

Ví dụ chạy thật (CLI, output là chuỗi phôn vị được model đọc):

```text
"HLV của HAGL họp HĐQT tại TP.HCM."
→ chuỗi phôn vị của: huấn-luyện-viên của Hoàng-Anh-Gia-Lai họp hội-đồng-quản-trị tại thành-phố Hồ-Chí-Minh
```

Trong khi Kokoro gốc gặp câu này chỉ có thể đánh vần từng chữ hoặc bỏ.

Ca khó hơn — vẫn chạy thật qua CLI (viết tắt có chấm, lồng số, cùng chữ
nhưng đọc khác theo ngữ cảnh):

| Câu | Hệ thống đọc |
|---|---|
| `GS.TS Nguyễn Văn A` | giáo sư tiến sĩ (viết tắt chồng nhau vẫn tách đúng) |
| `CMND của P.5 chuyển về TT từ 8h00` | chứng-minh-nhân-dân · phường năm · 8 giờ |
| `ĐT Việt Nam vô CK AFF 2-2` | **đội tuyển** Việt Nam · chung kết · đọc chữ AFF · hai-hai |
| `NXB Giáo dục phát hành SGK, BGDĐT duyệt` | nhà-xuất-bản · sách-giáo-khoa · bộ-giáo-dục-đào-tạo |
| `ThS. Trần B điều trị tại BV Bạch Mai theo QĐ của BCH` | thạc sĩ · bệnh viện · quyết định · ban chấp hành |

Ranh giới trung thực: viết tắt KHÔNG có trong bảng thì **đánh vần từng
chữ** chứ không đoán (vd `SGTGT` → "S-G-T-G-T") — đoán sai người nghe
nghe ra ngay, đánh vần thì người nghe còn hiểu; viết tắt đa nghĩa (`TT`,
`ĐT`) chọn nghĩa theo ngữ cảnh nhưng có thể chọn khác ý bạn.

Đơn vị, ngày giờ, ký hiệu — đọc theo ngữ cảnh, **tự phân biệt vi/anh**:
`100 km/h` trong câu việt → "một trăm ki-lô-mét một giờ", trong câu anh →
"one hundred kay-pee-aitch"; `05/10/2026` → "ngày năm tháng mười năm hai
nghìn không trăm hai mươi sáu"; `10:30` → "mười giờ ba mươi";
`1.000.000đ` → "một triệu đồng"; `50%` → "năm mươi phần trăm";
`25°C` → "hai mươi lăm độ xê"; `2k` → "hai nghìn"; `9h30` → "chín giờ ba
mươi"; `admin@site.com` → "admin a-còng site chấm com"; số điện thoại đọc
từng chữ số. Dấu `/` được xử theo ngữ cảnh: ngày tháng (05/10), đơn vị
(km/h), tỷ số (2-2) — mỗi dạng một cách đọc, không nhồi chung.

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


## Cài đặt & sử dụng

**Cài đặt** — Python 3.11+, **lõi G2P chỉ cần thư viện chuẩn (stdlib),
không cài gì thêm**:

```bash
# cách 1 — cài như một package (khuyên dùng):
pip install g2p-hamster            # nếu đã lên PyPI
# hoặc từ nguồn:
git clone https://github.com/tc186052-creator/g2p-hamster && cd g2p-hamster
pip install .                      # cài + lệnh `g2p-hamster`

# cách 2 — chạy ngay không cài:
./install.sh                       # tự cài espeak-ng nếu thiếu + kiểm tra nhanh
python3 cli.py "HLV của HAGL họp HĐQT tại TP.HCM."
```

**Dùng sau khi cài:**

```bash
g2p-hamster "Tôi chạy 100 km/h ngày 05/10/2026."        # CLI
g2p-hamster --file van_ban.txt --out ketqua.json        # cả file
```

```python
from g2p_hamster import text_to_profile_v2_full
r = text_to_profile_v2_full("HLV của HAGL họp HĐQT tại TP.HCM.")
print(r["profile"], r["state"])
```

**HTTP API / Docker** (nhúng vào hệ khác, không cần Python cùng máy):

```bash
python3 -m g2p_hamster.serve --port 8080       # hoặc: docker build -t g2p-hamster . && docker run -p 8080:8080 g2p-hamster
curl -s localhost:8080/g2p -d '{"text":"HLV của HAGL họp HĐQT tại TP.HCM."}'
curl -s localhost:8080/health
```

`install.sh` làm đúng 2 việc: cài `espeak-ng` qua apt nếu chưa có, rồi
chạy 1 câu kiểm tra. Không muốn chạy script thì làm tay:
`sudo apt install espeak-ng` (espeak-ng là nguồn cứu phiên âm anh của v2 —
**thiếu nó, từ anh ngoài CMUdict vẫn được đọc kiểu vi hóa nhưng không
chuẩn**; CLI sẽ cảnh báo nếu phát hiện thiếu; đặt `ESPEAK_NG_BIN=""` để
tắt hẳn nguồn này tường minh).

Không có `requirements.txt` runtime vì không cần: toàn bộ lõi thuần
stdlib (torch/numpy chỉ dùng ở demo TTS và train — ngoài phạm vi repo).
Tái lập phần **đánh giá STT ngược** mới cần thêm:
`pip install -r listening_test/requirements_eval.txt` (faster-whisper);
so sánh 7 hệ G2P ở trên có cài đặt từng tool ngay đầu
[`run_g2p_comparison.py`](listening_test/g2p_compare/run_g2p_comparison.py).

**Cách 1 — dòng lệnh** (`cli.py`):

```bash
python cli.py "Xin chào, hôm nay trời đẹp quá!"          # v2 best_effort
python cli.py "Tôi dùng cue nhé." --mode strict          # strict: từ chối mất từ
python cli.py "Xin chào" --v1                            # bản v1 fail-closed
python cli.py --file van_ban.txt --out ketqua.json       # cả file, 1 câu/dòng
```

**Cách 2 — Python API:**

```python
from g2p_hamster import text_to_profile_v2_full

r = text_to_profile_v2_full("Xin chào, hôm nay trời đẹp quá!")
print(r["profile"])   # sin caː↘w, hom naj ʈʂəː↘j dɛʔ↓p kwaː↗!
print(r["state"])     # complete | partial | empty | rejected (đo coverage)
```

Hàm trả về `(profile, errs)` / `(profile, errs, notes)` — lưu ý khác nhau
giữa bản (đều import được trực tiếp từ `g2p_hamster`):

- `from g2p_hamster import text_to_profile_v2_full` → dict đầy đủ (state,
  dropped, units, sources, t1_review…) — **KHUYÊN DÙNG**
- `from g2p_hamster import text_to_profile` → `(profile, errs, notes)` —
  **từ 0.2.6 là V2** (bản cứu tối đa, không bao giờ bỏ câu)
- `from g2p_hamster import text_to_profile_v1` → `(profile, errs)` — bản
  fail-closed cũ, tên tường minh (chỉ dùng khi CẦN từ chối câu có từ lạ
  cho prep dữ liệu train)

> **Lịch sử:** trước 0.2.6 `text_to_profile` trỏ vào v1 fail-closed —
> footgun mà cả hai đợt đánh giá độc lập đều bắt. Chưa có người dùng
> package nên 0.2.6 đổi thẳng: tên mặc định giờ là v2, v1 đổi tên rõ.

**Chạy test:** `python -m unittest discover -s tests -t .` (101/101).
Ngoài ra có **bộ test code-switch độc lập do người ngoài viết**
(2 × 100 câu, 1.273 anchor route, không dùng gold IPA): sau 0.2.7 đạt
436/436 + 836/837 — xem
[`independent_codeswitch_100/README.md`](independent_codeswitch_100/README.md).

**Tái lập kiểm chứng STT ngược** — có 2 mức khác nhau, đừng lẫn:

1. **Chấm lại đúng phép đo** (không cần cài/chạy gì): transcript + điểm
   từng clip của mọi model đã công bố trong
   [`listening_test/asr_roundtrip_all_models.csv`](listening_test/asr_roundtrip_all_models.csv);
   chạy `python3 listening_test/verify_roundtrip.py` (thuần stdlib) — nó
   chấm lại từng clip và in ra bảng khớp với README, kết quả lần chạy
   chuẩn: `ĐẠT` (mọi điểm tái lập được).
2. **So kiểm tra chéo bằng engine ASR bất kỳ** (cần `pip install
   faster-whisper`, GPU/CPU đủ RAM): tự chạy STT trên các MP3 trong repo
   và so với cột `sentence` + `verbal_ref` trong `review_sheet.tsv` —
   điểm số có thể lệch nhẹ giữa engine/chế độ decode, đó là bình thường;
   đây là kiểm tra chéo độc lập chứ không phải tái lập đúng phép đo.

```python
from faster_whisper import WhisperModel
m = WhisperModel("large-v3")
segs, _ = m.transcribe("listening_test/audio/vietnamese/001_vietnamese.mp3",
                       beam_size=5, language="vi")
print(" ".join(s.text for s in segs))
```

## Ứng dụng — ngoài train TTS thì dùng làm gì?

| Ứng dụng | Cách dùng | Ai cần |
|---|---|---|
| **1. Chuẩn bị dữ liệu train TTS** (chính) | quét corpus qua `--mode strict`: chỉ giữ câu đủ coverage + nguồn cứu theo policy → không có clip câm/mất từ trong tập train | đội train TTS |
| **2. Front-end vận hành TTS** | `text → phoneme` deterministic (cùng text = cùng profile, kèm policy hash) — cắm trước bất kỳ acoustic model nào nhận vocab kokoro178 | hệ đọc sách, news reader |
| **3. Chuẩn hóa văn bản đọc** | tầng t0 verbalize **số/tiền/ngày/giờ/email/viết tắt** thành chữ đọc: "1.000.000đ" → "một triệu đồng", "HLV" → "huấn luyện viên" — dùng độc lập, không cần TTS | chatbot, IVR, thông báo tự động |
| **4. Đo độ khó corpus trước khi thu âm/thu mua data** | quét corpus, đếm tỷ lệ complete/partial/empty, từ OOV, từ scope QD57 → biết trước chất lượng dữ liệu và cần thu bổ sung gì | PM dữ liệu, thu mua giọng |
| **5. Tra/kiểm tra phát âm từng từ** | "histidin" đọc gì? từ nào sẽ bị đánh vần? — công cụ QA cho biên tập viên nội dung đọc | biên tập, QC nội dung |
| **6. Nghiên cứu/đối chiếu G2P** | provenance hash + trace từng unit → so với vig2p/espeak, audit được từng quyết định | nghiên cứu |

**Chất lượng đặc trưng:** deterministic (cùng text luôn ra cùng phoneme —
an toàn cho dữ liệu train và reproducibility), fail-closed (không bịa phôn
vị ngoài inventory, không âm thầm rơi nội dung), 88/88 regression test,
provenance trong mọi đầu ra. **Ranh giới trung thực:** G2P bảo đảm *đọc
đủ* (coverage) và *không bịa*; "đọc ĐÚNG" chỉ kết luận được bằng gold đã
duyệt hoặc đánh giá nghe — xem bộ minh chứng 400 clip phía trên.

## Bản v2 — cứu EN (mặc định từ 0.2.6, `text_to_profile` trỏ vào đây)

Bản v1 fail-closed tuyệt đối: câu chứa một từ không đọc được là bị loại
cả câu. `g2p_hamster/g2p_v2.py` giữ tiên đề **cấm bịa phôn vị ngoài inventory**
nhưng không bao giờ bỏ câu nữa — từ hở được cứu theo bậc, mỗi lần cứu đều
ghi provenance:

1. **Thử route ngược lại** — từ việt parse được thì đọc việt, không đẩy qua anh (và ngược lại)
2. **CMUdict** (135k entry, pin) — phiên âm tra từ điển
3. **espeak-ng** — SUY DIỄN quy tắc chính tả anh (IPA → ARPABET → master).
   Mapping tường minh, âm lạ fail-closed — NHƯNG đây là suy diễn, không
   phải phiên âm chính thức; luôn ghi nguồn `espeak` để duyệt
4. **Spell tên chữ** — phương án cuối cho từ ≤4 chữ
5. Hụt hết → bỏ TỪ đó (không bỏ câu), báo tường minh vào `dropped`

Ba thuộc tính RIÊNG BIỆT — không trộn: (1) không tạo symbol ngoài
inventory — do mapping + validation; (2) không mất nội dung mà không
báo — do `state`/`dropped`; (3) phát âm đúng — KHÔNG bảo đảm bằng cơ chế,
chỉ kết luận được bằng gold đã duyệt hoặc đánh giá nghe. `complete` nghĩa
ĐỦ COVERAGE, không nghĩa đọc đúng.

**Kết quả có cấu trúc** (`text_to_profile_v2_full`):

```python
r = text_to_profile_v2_full(text)
r["state"]     # complete | partial | empty | rejected (đo COVERAGE)
r["profile"]   # chuỗi phôn vị
r["dropped"]   # từng unit bị bỏ: {word, reason, intentional}
r["units"]     # trace TỪNG read unit: {word, outcome, source, read_complete, reason?}
               # (record đọc tốt trên fast path được MỞ RA thành từng unit;
               #  dòng gộp tường minh chỉ khi record không có read_units:
               #  "merged": true + "unit_count": N)
r["sources"]   # {"core": n, "cmu": n, "espeak": n, "spell": n} — đếm theo unit
r["strict_policy"]  # policy strict thực tế của lần gọi này
r["provenance"]  # policy hash (sha256 code v2 + mapping + pin lõi) + espeak version/voice/options
```

`text_to_profile_v2(text)` giữ nguyên API cũ `(profile, errs, notes)`.

**strict / best_effort**:

- `mode="best_effort"` (mặc định, cho **render**): câu luôn đọc tiếp, từ
  hụt bị bỏ TỪ và báo tường minh.
- `mode="strict"` (cho **prep dữ liệu train**): từ chối cả câu
  (`state="rejected"`) nếu mất unit nội dung — **kể cả từ bị scope QD57
  cấm phát âm** (giữ lệnh cấm, nhưng bỏ một từ nội dung vẫn là mất
  coverage; `intentional` chỉ miễn icon/biểu tượng không có gì để đọc),
  nếu unit được cứu bằng nguồn ngoài `strict_policy` (mặc định nhận
  `cmu` + `spell`; **espeak phải opt-in** vì là suy diễn chưa duyệt),
  nếu IR lệch hợp đồng (`contract_ok=False`) — chỉ loại lỗi tường minh
  trong `STRICT_CONTRACT_ALLOWLIST` mới được miễn (mặc định RỖNG; miễn
  theo TÊN LOẠI lỗi, không miễn toàn bộ contract_errors), hoặc
  nếu profile rỗng dù câu có nội dung. Lưu ý: strict bảo đảm đủ coverage
  + nguồn theo policy, KHÔNG bảo đảm phát âm đúng.

Môi trường: `ESPEAK_NG_BIN=""` tắt hẳn nguồn espeak; `ESPEAK_NG_TIMEOUT`
(số giây, mặc định 10). Input espeak ngoài `[A-Za-z']` bị TỪ CHỐI (không
xóa ký tự âm thầm rồi phát âm từ khác). Chuẩn hóa NBSP/ký tự ẩn trước khi
vào tầng 1; soft hyphen nằm trong từ bị xóa; từ có chữ số không được cứu
(verbalize là việc của tầng 1).

```bash
python3 -m g2p_hamster.g2p_v2 "Trong hóa sinh học, H là ký hiệu của histidin."
# • nâng cấp 'histidin' từ espeak: hˈɪstɪdˌɪn

# so sánh v1 vs v2 trên văn bản của bạn (đa tiến trình)
python3 -m g2p_hamster.so_sanh --input van_ban.txt --procs 22
```

## Kết quả đối chứng

Tổng **815 case test, 0 fail** (0.2.7 — thêm test đơn vị HOA, mã tiền,
mã chuyến bay, t1_review, label spell, API mặc định v2, và 5 test định
tuyến code-switch từ bộ test độc lập). Bảng đầy đủ, kèm các benchmark dữ liệu thật phía trên:

| Bộ test | Kết quả |
|---|---|
| t0 regression — tokenize/detect/verbalize + route code-switch (đã tách tiny2) | 46/46 test OK |
| CLI smoke | 4/4 test OK |
| G2P v2 (state/strict/contract/scope/espeak mock + thật) | 49/49 test OK |
| Báo cáo trung thực v2 (t1_review → notes, label spell) | 2/2 test OK |
| G2P fase D/E (`test_g2p.py`) | 111 PASS, 0 FAIL |
| vi_rules/vi_syllable | 466 PASS, 0 FAIL |
| scope_policy mutation probes | 16 PASS, 0 FAIL |
| cmu_en fase C | 47 PASS, 0 FAIL |
| tone/coda mapper kokoro178 | 74 PASS, 0 FAIL |
| Benchmark frozen v3 — 1.118 câu, gold viết a-priori | ours 0 leak / 0 drop / **0,982** khớp-đọc-gold |
| Bài test 100k dev + 74.760 câu held-out | 0 leak / 0 drop (nguyên văn output trong repo) |
| Kiểm chứng STT ngược 400 clip (`verify_roundtrip.py`) | ĐẠT — mọi điểm công bố tái lập được |

Ngoài unit test, mức bảo đảm thật của dự án nằm ở các **benchmark dữ
liệu thật** (300 câu 7-hệ · 99.999 câu dev · 74.760 câu held-out · 1.118
câu frozen gold) — toàn bộ script + nguyên văn output từng câu nằm
trong repo để ai cũng audit được. Đánh giá độc lập 2026-10 đã tái lập
đúng 802/802 case của 0.2.1 trên máy khác và xác nhận held-out không
trùng dev (0 câu).

So sánh v1 vs v2 trên 5.000 câu Wikipedia tiếng Việt (metric theo
COVERAGE — KHÔNG phải độ chính xác phát âm): 60,4% giống hệt v1 · 20,5%
đọc khác v1 = THAY ĐỔI PHIÊN ÂM (phần lớn do nâng cấp OOV anh: v1 đánh
vần từng chữ → v2 phiên âm thật — KHÔNG mặc định là tốt hơn, từng câu
cần duyệt) · 9,9% v1 bỏ câu / v2 đủ coverage · 7,3% v1 bỏ câu / v2 đọc
thiếu (đã báo) · 0,2% cả hai hụt · 1,6% v1 đủ mà v2 đọc thiếu (chủ yếu
markup wiki và từ có dấu ngoài phạm vi — từng câu nằm trong
`lech_duyet.tsv`). Mỗi lần chạy xuất kèm `ket_qua.json` (máy đọc được:
toàn bộ rows, MỖI câu kèm `chi_tiet` đầy đủ units/dropped/warnings/notes/
errs — bản TSV mới rút gọn — + policy hash + version/config espeak) để
kiểm chứng. Số
liệu này đo đọc đủ/thiếu/rỗng; muốn kết luận đọc ĐÚNG cần gold được
duyệt hoặc đánh giá nghe.

## License

- Code + bảng từ điển tự soạn: **Apache-2.0**
- `g2p_hamster/03_vendor/cmudict/`: BSD-2-Clause (giữ nguyên LICENSE)
- Wiki sentences dùng làm dữ liệu test: CC BY-SA 3.0 (nguồn Wikimedia)
