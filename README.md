# g2p-hamster — G2P tiếng Việt cho TTS

Grapheme-to-phoneme (G2P) **deterministic, fail-closed, có provenance** cho
pipeline TTS Việt/Anh/mix — lớp thân ở tầng 2: nhận token IR chuẩn `ir/0.1`
từ tầng 1 (t0), xuất record master `ham/0.2` + chuỗi profile `kokoro178`
(vocab 178 ký tự của Kokoro).

```
text ──▶ t0 (luật: clean/tokenize/detect/verbalize/route) ──▶ IR ir/0.1
      ──▶ 01_g2p (âm tiết vi → CMUdict → fold → spell)      ──▶ ham/0.2
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

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `t0/` | Tầng 1 luật thuần: clean, tokenize, detect (số/tiền/giờ/ngày/email…), verbalize, gán route vi/en → IR `ir/0.1` |
| `01_g2p/` | Lõi G2P: `vi_syllable.py` (luật âm tiết vi), `vi_rules.py` (chữ → master), `cmu_en.py` (CMUdict → master), `g2p.py` (pipeline + validate gate), `profiles.py` (kokoro178) + bộ tests |
| `02_data/` | Bảng từ điển có pin: fold vi không dấu, spell, scope ledger QD57, inventory master `ham/0.2`, schema, provenance |
| `03_vendor/cmudict/` | CMUdict (BSD-2-Clause) pin commit + sha256 |
| `v2/` | Bản **v2 — cứu EN**: từ hở được cứu theo bậc CMUdict → espeak-ng → spell tên chữ; KHÔNG BAO GIỜ bỏ cả câu. Kèm script so sánh v1 vs v2 |
| `00_docs/` | Hợp đồng đầu vào IR, schema inventory, kế hoạch đánh giá, sơ đồ luồng |
| `tests/` | Regression test t0 (ví dụ chuẩn + torture set) + regression v2 (state/strict/scope/espeak fail-closed) |

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

## Cài đặt & sử dụng

**Cài đặt** — Python 3.11+:

```bash
git clone https://github.com/tc186052-creator/g2p-hamster && cd g2p-hamster
pip install -r requirements.txt        # torch + numpy (verbalize số/ngày)
sudo apt install espeak-ng             # tuỳ chọn — nguồn cứu espeak của v2
```

**Cách 1 — dòng lệnh** (`cli.py`):

```bash
python cli.py "Xin chào, hôm nay trời đẹp quá!"          # v2 best_effort
python cli.py "Tôi dùng cue nhé." --mode strict          # strict: từ chối mất từ
python cli.py "Xin chào" --v1                            # bản v1 fail-closed
python cli.py --file van_ban.txt --out ketqua.json       # cả file, 1 câu/dòng
```

**Cách 2 — Python API:**

```python
import sys; sys.path.insert(0, 'v2')
from g2p_v2 import text_to_profile_v2_full

r = text_to_profile_v2_full("Xin chào, hôm nay trời đẹp quá!")
print(r["profile"])   # sin caː↘w, hom naj ʈʂəː↘j dɛʔ↓p kwaː↗!
print(r["state"])     # complete | partial | empty | rejected (đo coverage)
```

API cũ `text_to_profile_v2(text)` / `text_to_profile(text)` trả
`(profile, errs, notes)` — caller hiện có chạy nguyên không cần sửa.

**Chạy test:** `python -m unittest discover -s tests -t .` (84/84).

**Tái lập kiểm chứng STT ngược** (trang trên): KHÔNG cần tải/khởi chạy
bất kỳ model TTS nào — 400 clip của cả 3 mô hình đã nằm sẵn trong repo.
Chỉ cần `pip install faster-whisper` rồi:

```python
from faster_whisper import WhisperModel
m = WhisperModel("large-v3")
segs, _ = m.transcribe("listening_test/audio/vietnamese/001_vietnamese.mp3",
                       language="vi", beam_size=5)
print(" ".join(s.text for s in segs))
# so với cột `sentence` trong listening_test/review_sheet.tsv
```

Việc render 3 mô hình (Kokoro gốc / Kokoro-Vietnamese của
iamdinhthuan / Kokoro vi của repo này) đã được chúng tôi thực hiện với
**cùng câu, cùng điều kiện** và xuất đủ audio để đối chiếu trực tiếp.

## Ứng dụng — ngoài train TTS thì dùng làm gì?

| Ứng dụng | Cách dùng | Ai cần |
|---|---|---|
| **1. Chuẩn bị dữ liệu train TTS** (chính) | quét corpus qua `--mode strict`: chỉ giữ câu đủ coverage + nguồn cứu theo policy → không có clip câm/mất từ trong tập train | đội train TTS |
| **2. Front-end vận hành TTS** | `text → phoneme` deterministic (cùng text = cùng profile, kèm policy hash) — cắm trước bất kỳ acoustic model nào nhận vocab kokoro178 | hệ đọc sách, news reader |
| **3. Chuẩn hóa văn bản đọc** | tầng t0 verbalize **số/tiền/ngày/giờ/email** thành chữ đọc: "1.000.000đ" → "một triệu đồng" — dùng độc lập, không cần TTS | chatbot, IVR, thông báo tự động |
| **4. Đo độ khó corpus trước khi thu âm/thu mua data** | quét corpus, đếm tỷ lệ complete/partial/empty, từ OOV, từ scope QD57 → biết trước chất lượng dữ liệu và cần thu bổ sung gì | PM dữ liệu, thu mua giọng |
| **5. Tra/kiểm tra phát âm từng từ** | "histidin" đọc gì? từ nào sẽ bị đánh vần? — công cụ QA cho biên tập viên nội dung đọc | biên tập, QC nội dung |
| **6. Nghiên cứu/đối chiếu G2P** | provenance hash + trace từng unit → so với vig2p/espeak, audit được từng quyết định | nghiên cứu |

**Chất lượng đặc trưng:** deterministic (cùng text luôn ra cùng phoneme —
an toàn cho dữ liệu train và reproducibility), fail-closed (không bịa phôn
vị ngoài inventory, không âm thầm rơi nội dung), 84/84 regression test,
provenance trong mọi đầu ra. **Ranh giới trung thực:** G2P bảo đảm *đọc
đủ* (coverage) và *không bịa*; "đọc ĐÚNG" chỉ kết luận được bằng gold đã
duyệt hoặc đánh giá nghe — xem bộ minh chứng 400 clip phía trên.

## Bản v2 — cứu EN (nâng cấp khuyến nghị)

Bản v1 fail-closed tuyệt đối: câu chứa một từ không đọc được là bị loại
cả câu. `v2/g2p_v2.py` giữ tiên đề **cấm bịa phôn vị ngoài inventory**
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
python3 v2/g2p_v2.py "Trong hóa sinh học, H là ký hiệu của histidin."
# • nâng cấp 'histidin' từ espeak: hˈɪstɪdˌɪn

# so sánh v1 vs v2 trên văn bản của bạn (đa tiến trình)
python3 v2/so_sanh.py --input van_ban.txt --procs 22
```

## Kết quả đối chứng

| Bộ test | Kết quả |
|---|---|
| t0 regression (đã tách tiny2) | 37/37 test OK |
| G2P v2 (state/strict/contract/scope/espeak mock + thật) | 47/47 test OK |
| G2P fase D/E (`test_g2p.py`) | 111 PASS, 0 FAIL |
| vi_rules/vi_syllable | 466 PASS, 0 FAIL |
| scope_policy mutation probes | 16 PASS, 0 FAIL |
| cmu_en fase C | 47 PASS, 0 FAIL |
| tone/coda mapper kokoro178 | 74 PASS, 0 FAIL |

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
- `03_vendor/cmudict/`: BSD-2-Clause (giữ nguyên LICENSE)
- Wiki sentences dùng làm dữ liệu test: CC BY-SA 3.0 (nguồn Wikimedia)
