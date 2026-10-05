# TÀI LIỆU NỀN — BỘ PHÂN LOẠI TỪ VI/EN (route), PHỤC VỤ THIẾT KẾ LẠI

Ngày: 03/10/2026. Đối tượng đọc: người/agent MỚI sẽ **thiết kế lại bộ phân loại
từ tiếng Việt / tiếng Anh** trong pipeline TTS. Tài liệu tự chứa, không cần
ngữ cảnh phiên làm việc cũ. Số liệu thí nghiệm đều là thực đo ngày 03/10/2026,
có lệnh chạy lại ở mục 13.

**Phạm vi theo lệnh chủ dự án (03/10):** chỉ CẢI TỔ phần PHÂN LOẠI. G2P
(tầng 2) và cách train acoustic (tầng 3) hiện được đánh giá là ổn, giữ nguyên —
nội dung chúng chỉ được nêu ở mức cần hiểu để bộ phân loại đấu nối đúng.

Mọi đường dẫn tuyệt đối tính từ `<workspace>/` (ghi `T1 = 02_project/05_TTS/01_tiny_model`, `G2P = 02_project/05_TTS/02_hamster_G2P`).

---

## 1. Bộ phân loại nằm ở đâu trong chuỗi TTS

```
Text thô (VI pha EN, ví dụ "Tuần này team mình chạy deadline…")
   │
   ▼  TẦNG 1 — chuẩn hóa + PHÂN LOẠI (T1/02_rules/t0/)   ← ĐỐI TƯỢNG CẢI TỔ
   │    tokenize → đọc số/tiền/giờ/ngày → PHÂN LOẠI từng từ: route = "vi"|"en"
   ▼  IR (schema ir/0.1): mỗi token có {surface, cat, route, review}
   │
   ▼  TẦNG 2 — G2P hamster (G2P/01_g2p/) — GIỮ NGUYÊN
   │    route vi → quy tắc âm tiết VI; route en → CMUdict→master
   │    token 'unresolved' → CẤM PHÁT ÂM (không sinh phoneme)
   ▼  chuỗi phoneme (profile 178 symbol)
   │
   ▼  TẦNG 3 — fine-tune Kokoro-82M — GIỮ NGUYÊN  → WAV 24 kHz
```

Vì sao phân loại quan trọng: route quyết định cách G2P đọc từ đó. Route sai
→ phoneme sai → model phát âm sai. Ví dụ thực tế 03/10: từ "KPI" trong câu
VI bị route vi → G2P đánh vần tên chữ Việt `kaːpəː↘i` → model đọc "ka pờ i"
thay vì "kây pi ai" — chính là sự việc mở đầu cuộc cải tổ.

---

## 2. Luồng phân loại hiện tại (chi tiết từng bước)

Mã chính: `T1/02_rules/t0/detect.py::assign_routes` (bắt đầu dòng 538).
Đầu vào: list token đã tách (cat ∈ word/abbr/acronym/slang + số + dấu câu).
Đầu ra: mỗi token có `origin`, `route`, `review` (nhãn vì sao được quyết).

**Pass 0 — đo ngôn ngữ câu (`sent_lang`, dòng 133):** đếm từ có dấu tiếng Việt
→ `vi` / `en` / `mixed`. Đoán theo đa số.

**Pass 1 — quyết định "chắc chắn" (dòng 549–585), theo đúng thứ tự:**

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | cat = slang | vi |
| 2 | **từ có dấu tiếng Việt** (`has_diacritic`) | vi |
| 3 | fold (bỏ dấu) ∈ `kho_quyet_vi` (chỉ khi cat ≠ acronym) | vi |
| 4 | fold ∈ `kho_quyet_en` | en |
| 5 | cat = word ∧ ASCII ∧ **không** là âm tiết VI hợp lệ ∧ (∈ cmudict ∨ viết hoa chữ cái đầu) | en (vá 02/10, review=`cmudict_en`) |
| 6 | **cat = acronym** (viết hoa 2–6 chữ) | route = ngôn ngữ CÂU (review=`acronym_spell`) |
| 7 | fold ∈ `kho_bat` (từ mù) | route = None → chờ pass 2/tiny1 |
| 8 | fold ∈ `syllables_vi` | vi (trừ "a"/"i" đặc biệt trong câu EN) |
| 9 | còn lại (OOV) | theo ngôn ngữ câu (review=`oov`) |

**Pass 2 — láng giềng:** token còn route=None nhận route của từ gần nhất đã
quyết (bỏ qua nguồn là token nhánh cmudict vá 02/10 — chống kéo số/ký hiệu
theo sai). Vẫn không được → ngôn ngữ câu.

**Pass 3 — tiny1** (`tiny_route.predict_routes`): model nhìn ngữ cảnh ký tự
toàn câu, phán vi/en cho phần còn lại. Hỏng/tiếu → lùi heuristic.

**tiny2** (không nằm trong pass route): `pipeline.py` sinh ≥2 ỨNG VIÊN CHUỖI
ĐỌC cho câu (đảo route/l styles, biến thể dấu), tiny2 xếp hạng — chỉ dùng cho
đọc số/tiền/giờ/năm, giữ reading luật khi tiny2 không tự tin (margin).

---

## 3. Có những code phân loại nào (toàn bộ, kèm vai trò)

Đều nằm trong `T1/02_rules/t0/` — thuần Python, không framework:

| File | Vai trò phân loại | Hàm chính đáng đọc |
|---|---|---|
| `detect.py` | **Trái tim phân loại**: gán cat + route | `assign_routes` (dòng 538), `is_caps`, `caps_kind`, `has_diacritic`, `sent_lang`, `roman_value` |
| `dicts.py` | Nạp + cache các kho từ điển; hàm `fold` (bỏ dấu chuẩn Unicode) | `kho_bat()`, `kho_quyet_vi/en()`, `kho_en_cmudict()`, `syllables_vi()`, `slang()`, `abbrev()`, `char_policy()`, `fold()` |
| `textproc.py` | Tiền xử lý ký tự, HTML, chuẩn Unicode | — |
| `verbalize.py` | Đọc các span (số/tiền/giờ/ngày) thành chuỗi đọc | `verbal_*` |
| `numbers.py` | Regex nhận diện số/version/tỉ số/khoảng | — |
| `pipeline.py` | Điều phối: normalize() → IR; gọi tiny2 trọng tài; sinh ứng viên | `normalize`, `_rules_normalize`, `_swap_candidates` |
| `tiny_route.py` | **tiny1** — runtime model phán vi/en theo ngữ cảnh | `predict_routes(surfaces)` |
| `tiny2_mc.py` | **tiny2** — runtime model xếp hạng ứng viên đọc | `rank(question, candidates)` |

**Không dùng thư viện bên ngoài nào cho phân loại.** Chỉ stdlib Python
(`re`, `csv`, `unicodedata`, `html`, `functools`, `pathlib`, `threading`) và
`torch` cho 2 tiny model. Không langid/underthesea/pyphen/espeak gì cả — mọi
"từ điển" là file dữ liệu tự nạp (mục 4). CMUdict là FILE DỮ LIỆU tải về
(BSD-2, pin `03_vendor/cmudict/cmudict.dict`, sha `81917843c7…`), không phải thư viện.

**Tests hiện hành:** `T1/04_eval/tests/test_t0.py` (44 tests) + bộ đối chứng
316 ca (`build_doichung.py` / `regression_doichung.py`). Vá 02/10 (nhánh
cmudict) chạy lại 44/44 PASS, 315/316 đối chứng, 0 hồi quy mới.

---

## 4. "Trong kho" có gì — bảng đầy đủ các kho (data: `T1/02_rules/t0/data/`)

| Kho (file) | Số dòng | Nguồn | Vai trò trong luồng | Ví dụ đầu file |
|---|---|---|---|---|
| `kho_bat.txt` | 7.031 | tự tổng hợp trong dự án | từ MÙ — có khả năng là VI hoặc EN → không quyết cứng, chờ láng giềng/tiny1; G2P chốt `unresolved` nếu vẫn mù | `aa aaa aap` |
| `kho_quyet_vi.txt` | 1.441 | tự tổng hợp (tần suất corpus, so nhóm có dấu/không dấu) | từ/tên riêng đọc kiểu VIỆT, quyết cứng route=vi (trừ ALL-CAPS — dòng 561 có chặn) | `abbank abe abramovich` |
| `kho_quyet_en.txt` | 4.625 | tự tổng hợp | từ EN phổ thông quyết cứng route=en | `abandon abandoned abilities` |
| `kho_en_cmudict.txt` | **126.052** | **CMUdict 0.4** (BSD-2), pin sha `81917843c7…`, sinh 02/10/2026, lowercase, gỡ hậu tố (2)/(3) | từ điển EN chính — nhánh vá 02/10: từ ASCII không phải âm tiết VI + có trong đây → en | `'bout 'cause 'course` |
| `syllables_vi.txt` | 37.101 | sinh từ bảng âm tiết VI (regex `_SYLL_RE` trong dicts.py lọc lại) | tập ÂM TIẾT VI HỢP LỆ — "từ điển Việt" theo kiểu quy tắc: từ ASCII có trong đây → coi là từ VI có thể bỏ dấu | `a aa aaa` |
| `words_en.txt` | 80.656 | bổ trợ (danh sách từ EN) | tham khảo, chưa tham gia assign_routes | `a aa aaa` |
| `spell_exceptions.txt` | 26 | tự viết | acronym ALL-CAPS GÕ TỪNG CHỮ, không đọc như từ | (comment + danh sách) |
| `slang_vi.tsv` / `abbrev_vi.tsv` / `units.tsv` | 16 / 107 / 37 | tự viết | slang VI; viết tắt VI ("TP"→"thành phố"); đơn vị đo | — |
| `char_policy.tsv` | 289 | tự viết | policy đọc ký tự lạ/ký hiệu theo route | — |

**Điểm chết đã biết trong kho:** từ `team` hiện diện ĐỒNG THỜI trong
`kho_bat`, `syllables_vi` và `kho_en_cmudict` — thứ tự pass 1 quyết định nó
thành sao (kho_bat ở #7 sau syllables #8? không — syllables nằm ở #8 SAU
kho_bat #7, nên team bị bắt ở #7 → chờ tiny/heuristic) — ví dụ điển hình
vì sao THỨ TỰ các kho quan trọng ngang NỘI DUNG kho.

---

## 5. tiny1 — được huấn luyện từ gì, đầu vào/đầu ra là gì

**Kiến trúc (`tiny_route.py::_build`, nguồn gốc `T1/03_model/train_tiny.py`):**
CharTagger — Embedding ký tự 256d + position 320 + TransformerEncoder 4 lớp
(4 heads, ff 1024, norm_first) → mean-pool theo span từng token → head tuyến
tính 2 lớp = ["vi", "en"].

| Hạng mục | Giá trị |
|---|---|
| Đầu vào | list surface TOÀN BỘ token của câu (dưới 320 ký tự; **chuỗi bị `.lower()` — mất chữ hoa!**) |
| Đầu ra | với MỖI token: (route "vi"/"en", xác suất softmax) |
| Dữ liệu train | corpus `T1/01_data/silver/corpus_ir_1M.jsonl.gz` — 1,2M câu đã qua t0 (text + IR tokens); shuffle seed 7, test 2% |
| Nhãn train | 2 nguồn: (1) token KHÔNG có review → nhãn LUẬT của t0 (`label_of` dòng 146); (2) token CÓ review (flagged) → tra bảng TEACHER theo khóa (câu, từ); không khớp → **mask, không học** |
| Teacher | Qwen 2B chạy vLLM (`T1/06_tools/teacher_route.py`) gán vi/en cho token flagged — 34.249 nhãn (`01_data/teacher/gold3k_route.jsonl` 4.245 + `silver30k_route.jsonl` 30.004); phân bố en 31.948 / vi 2.093; **riêng token HOA 2–6 chữ: en 1.849 / vi 169** |
| Hyper | 2 epoch, batch 128, AdamW lr 3e-4 wd 0.01, vocab ký tự min_freq 3 |
| Model file | `T1/03_model/tiny_v6/tiny_v1.pt` (các bản v1–v6 lưu theo thư mục, dùng bản v6) |
| Gói role thiết kế | "agent nhỏ chạy local sàng lọc" — chỉ được hỏi token MỜ HỒ, hỏng thì lùi heuristic |

---

## 6. tiny2 — được huấn luyện từ gì, đầu vào/đầu ra là gì

**Kiến trúc (`tiny2_mc.py::_build`, nguồn `T1/06_tools/train_tiny2_mc.py`):**
MCRanker — Embedding 768d + TransformerEncoder 8 lớp (8 heads, ff 3072,
max 560) → mean-pool → score 1 chiều; softmax QUA CÁC ỨNG VIÊN (không phải qua nhãn).

| Hạng mục | Giá trị |
|---|---|
| Đầu vào | (câu gốc + ký tự phân cách `␟` + MỘT chuỗi ứng viên đọc) × N ứng viên |
| Đầu ra | xác suất softmax N ứng viên — chọn ứng viên nào "tự nhiên nhất" |
| Dữ liệu train | `build_mc_data.py` sinh: mỗi câu {q, gold, negs[≥2]}; câu từ corpus silver 1M + cặp TRƯỚC/SAU được judge 9B duyệt (duyet_v*) |
| Ứng viên SAI 3 nguồn | (A) chạy t0 với config LÀM CHÉO (đảo default_route, đảo kiểu năm en/vi); (B) regex biến thể gold (phẩy→chấm, phần trăm→percent, trên→per, đến→to, bỏ "phần trăm"); (C) nguyên văn KHÔNG chuẩn hóa số/ngày ("lười") |
| Phạm vi được train | readings phụ thuộc route: SỐ, TIỀN, GIỜ, NĂM, đơn vị — **KHÔNG có acronym/từ vựng thông thường** |
| Hyper | như tiny1 (2 epoch, batch 128, AdamW 3e-4) |
| Model file | `T1/03_model/tiny2_mc/tiny2.pt` |
| Cách dùng trong pipeline | chỉ trọng tài ứng viên ĐỌC cho số/tiền/giờ/năm; đổi sang ứng viên khác chỉ khi tiny2 tự tin về margin |

---

## 7. Vì sao nó phân loại sai — 3 cơ chế gốc (có bằng chứng thực nghiệm)

**Cơ chế 1 — nhánh acronym đi tắt khỏi mọi từ điển (`detect.py` pass 1 #6).**
Token viết hoa 2–6 chữ bị `is_caps` gán `cat=acronym` (dòng 35–37, 458–469)
TRƯỚC khi tới nhánh cmudict #5 — nhánh này lại chỉ áp dụng cho `cat="word"`.
→ "KPI" không bao giờ được tra CMUdict hay kho nào; nhận route = ngôn ngữ câu
(review `acronym_spell`) → trong câu VI → G2P đánh vần tên chữ VI.
Ngược lại "COVID"/"ASEAN" đi được nhánh en chỉ vì "-" đuôi/cấu trúc câu khiến
chúng không rơi vào cat=acronym (`caps_word`) — may mắn, không phải thiết kế.
"WHO" đúng vì tình cờ nằm trong `kho_quyet_en`.

**Cơ chế 2 — tiny1 bị mù chữ hoa.** `train_tiny.py` dòng 61 và
`tiny_route.py` (runtime) đều `surface.lower()` → "KPI" ≡ "kpi". Tín hiệu
mạnh nhất để nhận acronym (VIẾT HOA) bị xóa trước khi vào model. Trong ngữ
cảnh VI, model chỉ còn suy "từ ASCII lạ giữa câu Việt ≈ tên riêng kiểu
Canada/Biden → vi" — và thang nhãn train nghiêng vi vì BIỂN từ có dấu (nhãn
luật, nguồn 1) áp đảo số ít nhãn teacher (nguồn 2).

**Cơ chế 3 — nhãn teacher có sự thật nhưng không truyền được.** Teacher Qwen
ĐÃ gán đúng 91% token HOA → en (1.849/2.022), nhưng (a) teacher chỉ gán cho
token flagged trong pool corpus cũ, (b) lúc train, token acronym_spell trong
câu mới không khớp khóa (câu, từ) → bị MASK, (c) tín hiệu hoa/thường bị xóa
(cơ chế 2) nên kiểu mẫu "caps→en" không có cách nào biểu diễn. Kết quả:
tri thức đúng trong data, model vẫn học ra hành vi sai.

**Thí nghiệm đối chứng 03/10 (CPU, lệnh chạy lại ở mục 13):**

| Từ | tiny1 phán | tin | Kỳ vọng | Từ | tiny1 phán | tin | Kỳ vọng |
|---|---|---|---|---|---|---|---|
| KPI | vi ✗ | 99,8% | en | WHO | **en ✓** | 93,9% | en |
| CEO | vi ✗ | 99,0% | en | công ty | vi ✓ | 100% | vi |
| GDP | vi ✗ | 100% | en | nhanh | vi ✓ | 100% | vi |
| DNA | vi ✗ | 99,7% | en | Canada | vi ✓ | 99,0% | vi (đọc kiểu Việt) |
| EU / TTS / USD / HTML / LHQ | vi ✗ | 96–100% | en | Biden | vi ✓ | 55,0% | vi |
| TNHH / TTXVN / HLV | vi (mù) | 100% | cần duyệt | | | | |
| COVID | vi ✗ | 76,8% | en | deadline | vi ✗ | 91,7% | en |
| wifi | vi ✗ | 73,0% | en | team | vi ✗ | 79,9% | en |

tiny2 (rank 3 ứng viên "giữ nguyên / vần chữ VI / vần chữ Anh"): KPI → "kây
pi ai" 75%; DNA → kiểu Anh 100%; LHQ → giữ nguyên 92% (hợp lý: từ Việt);
WHO → kiểu Anh 99% (quá Anh hóa — người Việt thường nói "vờ-hờ-ô");
CEO/USD/COVID/deadline không kết luận được. **Kết luận: tiny2 có cảm giác
ngôn ngữ nhưng ngoài phạm vi train (chỉ số/tiền/giờ) — chỉ dùng làm phiếu
tham khảo, không phải phán quyết.**

---

## 8. Quy mô nhu cầu phân loại trong data thật (đo 03/10 trên list train mix5 9.283 câu)

- 77,4% câu có ≥1 token ASCII ≥3 chữ; tổng ~30.844 token — trung bình 3,3 token/câu.
- Acronym viết hoa 2–6 chữ: **418 loại / 962 lần xuất hiện**; route hiện tại:
  en 137 loại/310 lần (nhờ may mắn hoặc kho quyết), **vi 281 loại/652 lần (68%)** —
  chính là phần nhãn G2P lệch với audio (audio đọc kiểu người Việt/OmniVoice).
- Data train gồm 3 nguồn audio: giọng người thật (pilot) 5.170 câu/10,18h,
  OmniVoice clone 2.558 câu/7h, af_heart EN 1.673 câu/2,9h — từ EN trong câu
  VI được audio đọc KIỂU VIỆT HÓA trong khi nhãn là CMUdict kiểu Anh (thiết kế
  có chủ ý, ghi trong manifest `G2P/06_train_t3/data/mix3/manifest_t3b_mix.json`).
- 1.567/9.177 câu (17,1%) bị cách ly khi re-G2P vì có token G2P từ chối —
  phần lớn do phân loại không chốt được (tên riêng ngoại).

---

## 9. Khung 4 loại của chủ dự án (03/10 — giữ nguyên ý, input thiết kế)

> Chia làm 4 loại: **(1) Chắc chắn Anh** (ví dụ bắt đầu bằng z, w) —
> **(2) Chắc chắn Việt** (ví dụ có dấu) — **(3) Tra từ điển** (tra ĐỒNG THỜI
> cả từ điển Anh lẫn Việt; "làm sao có từ điển này") — **(4) Từ điển không
> có thì phải làm sao nữa.**

Ánh xạ vào cơ chế hiện có:

| Loại chủ dự án | Cơ chế hiện có | Tình trạng |
|---|---|---|
| (2) Chắc chắn Việt — có dấu | pass 1 #2 `has_diacritic → vi` | **ĐÃ CÓ**, hoạt động đúng 100% trong thí nghiệm |
| (3) Tra từ điển cả Anh lẫn Việt | #3 `kho_quyet_vi` → #4 `kho_quyet_en` → #5 cmudict (chỉ cat=word) | **CÓ nhưng THỨ TỰ/LỚP PHỦ sai**: acronym (#6) đi tắt khỏi #4/#5; VI tra bằng quy tắc âm tiết (#8) hơn là danh sách từ |
| (1) Chắc chắn Anh (z, w…) | KHÔNG TỒN TẠI | cần thêm heuristic ký tự (chú ý từ slang VI có z/f/j: "zô", "jz"… nên đặt cẩn trọng) |
| (4) Từ điển không có → ? | #7 kho_bat → láng giềng → tiny1 → G2P `unresolved` cấm phát âm | **KÊNH ĐÃ CÓ nhưng tiny1 hiện hỏng** (mục 7) — hoặc sửa tiny1 hoặc thay cơ chế |

---

## 10. Câu hỏi thiết kế bộ phân loại mới phải trả lời

1. Thứ tự và độ phủ của 4 loại: heuristic ký tự (loại 1) đặt trước hay sau có-dấu (loại 2)?
2. Từ điển EN (CMUdict 126k) có áp cho token viết hoa không (bỏ chặn cat=acronym)?
   Acronym tra bằng gì (CMUdict có mục viết hoa riêng)? Cần bảng đọc acronym
   riêng (EN letters / VI letters / đọc trọn) do chủ dự án duyệt không?
3. Chữ hoa phải được PRESERVE vào tiny model (bỏ `.lower()` hoặc thêm feature
   is_caps) — retrain tiny1 với 1.849 nhãn teacher HOA sẵn có, hay bỏ tiny1?
4. Con đường cho loại (4): kho_bat → tiny (sửa) → teacher Qwen/9B cho token mới
   → `unresolved` cấm phát âm. Độ tin tối thiểu để chấp nhận phán của model?
5. Kho triple-membership (`team` ∈ 3 kho): phân cấp kho theo thứ tự ưu tiên
   tường minh (vd kho_bat > kho_quyet > syllables) hay làm sạch kho?
6. Đầu ra mới có cần NHÃN MỞ RỘNG ngoài vi/en không (vd `vi_letters`/`en_letters`
   cho acronym, `number`, `unit`…) để G2P không phải đoán lại?
7. Tiêu chí nghiệm thu: giữ 44 tests + 316 đối chứng làm Regression, thêm bộ
   test acronym (418 loại thực tế từ data) + bộ thí nghiệm mục 7 làm gate?

---

## 11. Luật dự án liên quan (bắt buộc giữ khi thiết kế lại)

1. Sửa tầng 1: bắt buộc **backup** toàn thư mục (mẫu: `T1/02_rules/backups/t0_bak_20261002_205827/`)
   + tests PASS + đối chứng không hồi quy; không âm thầm đổi hành vi token khác.
2. Dữ liệu test không đem đi train (corpus 1,2M là test-only).
3. Không xóa/sửa dữ liệu ngoài `05_TTS/`; kill tiến trình bằng PID.
4. Tải tài nguyên ngoài: pin revision + checksum + license (CMUdict = BSD-2).
5. Docs sync sau mỗi vòng; bundle tạo mới không ghi đè.
6. Quyết định ĐỌC (cách phát âm từng từ khó) thuộc quyền chủ dự án —
   đưa vào bảng duyệt, không tự quyết trong code.

---

## 12. Ngữ cảnh tối thiểu về G2P + acoustic (đã ổn, chỉ để đấu nối)

- G2P ăn IR {surface, cat, route, review}; route vi → quy tắc âm tiết
  (37.101 vần hợp lệ), route en → CMUdict→master; token không chắc →
  `unresolved` → CẤM PHÁT ÂM (không sinh phoneme — fault-injection guard).
  Bảng đánh vần chữ hiện là seed tên chữ VI (`G2P/02_data/spell_vi.tsv`,
  thiếu s/f/j/w/z) — nguồn của lỗi "ka pờ i"; việc bổ sung bảng tên chữ EN /
  bảng acronym là việc tầng 2, chờ thiết kế bộ phân loại xong.
- Acoustic: fine-tune Kokoro-82M (StyleTTS2 fork, pin commit `a249afe5`),
  2 stage, batch 2, cap16, ckpt cuộn 2000-step/keep-2; checkpoint 5 module;
  KHÔNG extract voicepack từ checkpoint; render dùng voicepack thật
  (vi = diem_trinh.pt, en = af_heart.pt). Chi tiết đầy đủ:
  `G2P/00_docs/KE_HOACH_TANG_3.md` (mục T3-A…T3-E + pin tài nguyên mục 4).

---

## 13. Chạy lại thí nghiệm + tài liệu liên quan

**Thí nghiệm tiny1** (CPU, không đụng GPU):
```bash
cd <workspace>/02_project/05_TTS && T0_TINY_DEVICE=cpu \
  02_project/04_kokoro_tts/00_env/.venv/bin/python - <<'EOF'
import sys, re
sys.path.insert(0, "01_tiny_model/02_rules")
from t0.tiny_route import predict_routes
for sent, target in [("KPI của công ty cao","KPI"), ("WHO khuyến cáo","WHO"),
                     ("deadline công việc dồn","deadline"), ("công ty cao","công")]:
    toks = re.findall(r"[A-Za-zĐđÀ-ỹ0-9-]+", sent)
    r, p = predict_routes(toks)[toks.index(target)]
    print(f"{target:10s} {r} {p*100:.1f}%")
EOF
```
**Thí nghiệm route tầng 1:** thay `predict_routes` bằng
`t0.pipeline.normalize("Công ty KPI và đội ngũ.")` rồi in token
{cat, route, review} — thấy trực tiếp nhánh nào quyết.
**Thí nghiệm tiny2:** `from t0.tiny2_mc import rank; rank(q, [ứng viên1, 2, 3])`.
**Đếm acronym trong data train:** script ngày 03/10 — regex `\b[A-Z]{2,6}\b`
trên metadata `05_data/01_data_1/tts_dataset_30k_wav.txt` giới hạn ở
`G2P/06_train_t3/data/mix5/train_list.txt`, sau đó chạy `normalize()` từng loại.

| Chủ đề | Tài liệu |
|---|---|
| Spec tầng 1 gốc | `T1/00_docs/01_spec_thiet_ke.md` |
| Hồ sơ vá route cmudict 02/10 | `T1/00_docs/07_PATCH_CMUDICT_ROUTE_20261002.md` |
| Kế hoạch tầng 3 (ngữ cảnh) | `G2P/00_docs/KE_HOACH_TANG_3.md` |
| Đánh giá tầng 2 tự chứa | `G2P/00_docs/G2P_KE_HOACH_DANH_GIA.md` |
| Mô tả bộ data nhà (nguồn, nhịp đọc) | `05_data/01_data_1/readme.txt` |
| Provenance CMUdict | `G2P/03_vendor/cmudict/cmudict_provenance.json` |
