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

**Mục lục:** [Cấu trúc](#cấu-trúc) · [7 hệ trên 300 câu](#so-sánh-7-hệ-g2pfront-end-trên-cùng-300-câu-thật) ·
[Held-out 74.760](#bài-test-held-out-74760-câu-chưa-từng-thấy-chạy-trên-gói-pypi-đã-phát-hành) ·
[100k dev](#bài-test-100k-bộ-phát-triển-làm-trước-khi-có-held-out) ·
[Frozen v2 + gold](#benchmark-frozen-công-khai--v2-1088-câu-gold-viết-trước-chấm-bằng-máy) ·
[Demo nghe thử](#demo--nghe-thử-400-clip--toàn-bộ-số-liệu) ·
[Cài đặt](#cài-đặt--sử-dụng) · [Kết quả đối chứng (803 test)](#kết-quả-đối-chứng)

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

## So sánh 7 hệ G2P/front-end trên cùng 300 câu thật

Chạy **cùng 300 câu** (100 vi + 100 anh + 100 mix — đúng các câu trong
`listening_test`, nguồn từng câu công khai) qua các công cụ public:
[donglao_g2p](https://pypi.org/project/donglao-g2p/),
[sea_g2p](https://pypi.org/project/sea-g2p/),
[vietnormalizer](https://pypi.org/project/vietnormalizer/),
[vig2p](https://github.com/hoang1007/vig2p),
[vPhon](https://github.com/kirbyj/vPhon),
[viphoneme](https://github.com/v-nhandt21/Viphoneme),
espeak-ng. KHÔNG có TTS — so đúng phép đo text → phôn vị + tốc độ 1
luồng (i9-12900K). Script + nguyên văn output từng hệ, từng câu:
[`listening_test/g2p_compare/`](listening_test/g2p_compare) — tự chạy lại
được bằng `run_g2p_comparison.py`.

> **Đính chính 0.2.2:** ở bản 0.2.0–0.2.1 chúng tôi đo sea_g2p bằng
> `G2P(lang="vi").convert()` **trần** (chỉ phiên âm, tắt bộ chuẩn hoá của
> nó) — **sai cấu hình**, phát hiện bởi đánh giá độc lập 2026-10. Bảng
> dưới đo lại bằng đúng cách sea_g2p tài liệu hoá:
> `SEAPipeline(lang="vi").run()` (normalizer 17 bước + G2P). Kết luận
> thay đổi: sea_g2p chuẩn hoá số/ngày **tốt**, không còn "rò rỉ" —
> khoảng cách với repo này co lại còn ~1,4 điểm khớp-đọc-gold (bảng
> frozen bên dưới). Số cũ của vietnormalizer/vig2p/viphoneme giữ nguyên
> vì 3 công cụ này không cài được trên máy đo lại 2026-10 (ghi rõ trong
> [`summary.csv`](listening_test/g2p_compare/summary.csv)).

| Hệ | Loại ra | Chạy OK | Câu/s | Số còn "rò rỉ" | Ghi chú |
|---|---|---|---|---|---|
| donglao_g2p | phôn vị | 100% | **30998** | 0% | wheel native (Rust) — nhanh nhất, nhưng rơi số ở mẫu giờ (bên dưới) |
| sea_g2p | phôn vị | 100% | 2782 | **0%** | đo bằng `SEAPipeline.run()` (0.2.0–0.2.1 đo trần → sai) |
| vietnormalizer | văn bản chuẩn hóa | 100% | 515 | 0% | ra chữ đã chuẩn hóa, **chưa phải phôn vị** — số lần đo cũ |
| vig2p | phôn vị | **55%** | 2812 | 0% | lỗi 45% câu — số lần đo cũ |
| vPhon | phôn vị | 100% | 43951 | **28,3%** | chuyển từng từ, không verbalize: `100` → `[100]` |
| espeak_ng | phôn vị | 99,3% | 69 | 0% | câu vi nhiều số → IPA sai bét |
| viphoneme | phôn vị | 100% | 26 | 0% | đầy đủ nhưng chậm nhất + chỉ chạy Python <3.12 — số lần đo cũ |
| **g2p (repo này)** | phôn vị | **100%** | 141 | **0%** | 100% coverage, 0 nội dung rơi, provenance từng từ |

"Số rò rỉ" = câu có chữ số **đứng độc lập** còn sót trong chuỗi ra
(regex `\b\d+\b` — "100", "09/11/2007" chưa verbalize → acoustic model
không đọc được; chữ số làm thanh điệu gắn vào âm tiết (`toj1`, `mot6`)
là ký hiệu phiên âm của từng hệ, không tính). Chỉ đếm dòng `status=ok`
— dòng lỗi/rỗng không được tính vào tử số lẫn mẫu số. Một câu đối chiếu
thẳng (nguyên văn trong CSV, `mix_easy` #48 — "Đại hội bế mạc vào lúc
11h00 ngày 09/11/2007 tại Tp."):

| Hệ | Xử lý câu này thế nào |
|---|---|
| **repo này** | "mười một giờ, ngày chín tháng mười một, năm hai nghìn không trăm lẻ bảy, thành phố" — trọn vẹn |
| sea_g2p (SEAPipeline) | đọc trọn ngày/giờ/năm — "mười một giờ không, ngày chín tháng mười một, năm hai nghìn không trăm lẻ bảy…" |
| donglao_g2p | "lúc **h** ngày chín tháng mười một…" — **mất "11" giờ**, sót "tp." |
| vPhon | `[11h00] [09/11/2007]` — số giữ nguyên, không verbalize |
| espeak_ng | "the stroke letter-one-i-aitch…" — câu vi thành rác IPA |

Nói thẳng: về **tốc độ thuần**, donglao_g2p nhanh hơn repo này ~220 lần
(mã native, không có strict/coverage/provenance) — repo này 141 câu/s
vẫn dư real-time (dưới 1% một nhân CPU). Về **chất lượng**, sea_g2p
đo đúng cấu hình là đối thủ xứng tầm: 0% rò rỉ, đọc trọn ngày/giờ —
điểm còn phân hóa là **rơi âm thầm** (donglao mất số ở ~44% câu có
mẫu giờ `13h00`, bảng 100k bên dưới) và **khớp-đọc-gold** (bảng frozen
bên dưới: 0,982 / 0,966 / 0,906). repo này là hệ **duy nhất đồng thời
đạt 100% coverage + 0 số rò rỉ + 0 rơi + provenance từng từ + chế độ
strict cho dữ liệu train**. Không đồng ý bảng trên? Mở
[`outputs_all_tools.csv`](listening_test/g2p_compare/outputs_all_tools.csv)
ra tự chấm — output gốc từng hệ, từng câu đều nằm đó.

Tốc độ riêng từng đường của repo (đo trên 400 câu listening_test, script
[`benchmark_speed.py`](benchmark_speed.py) — **đo lại 0.2.2** vì bản cũ
tính thông lượng bị ×3 do vòng repeat reset mẫu thời gian):

| Đường | Câu/s | p50 | p95 |
|---|---|---|---|
| v2 (mặc định, cứu từng từ) | 113 | 6,2 ms | 26 ms |
| v1 (fail-closed) | 194 | 4,8 ms | 10 ms |
| espeak-ng (tham khảo) | 56 | 16,9 ms | 29 ms |

## Bài test HELD-OUT: 74.760 câu CHƯA TỪNG THẤY, chạy trên gói PyPI đã phát hành

Sau khi phát hành v0.2.1, bài 100k được làm lại đúng quy trình:
**một là**, chạy trên **bộ test KHÁC** bộ đã dùng khi phát triển;
**hai là**, chạy trên **đúng wheel đã phát hành trên PyPI** chứ không
phải code trong repo — không ai có cớ nói "test gói cũ" hay "test data
tuyển trước".

**Bộ test khác như nào** (minh bạch đầy đủ):

| | Bộ phát triển (bài 100k bên dưới) | **Bộ held-out (bài này)** |
|---|---|---|
| File | `dataset_100k.tsv` | `dataset_heldout_2026.tsv.gz` — **CÔNG KHAI trong repo** (74.760 câu đã lọc trùng, tải về là chạy được) |
| Nguồn | wiki + báo vi/anh (lấy trước) | **tin tức + wiki 2026**: vie_news_2026 (39.589) · eng_news_2026 (24.059) · eng_wiki_2026 (13.213) · vie_wiki_2026 (10.669) |
| Số câu | 99.999 | 87.530 → **lọc còn 74.760 câu mới tuyệt đối** (loại 12.770 câu trùng bộ phát triển) |
| Phân bố | 52.000 vi · 33.000 anh · 15.000 mix (15%) | 24.112 vi · 33.650 anh · **16.998 mix (22,7%)** — nhiều mix hơn hẳn |

**Gói được đo**: `pip install g2p-hamster==0.2.3` (wheel PyPI, import từ
site-packages — tái lập 2026-10-05, output **giống hệt từng byte** như
khi chạy code repo). Tái lập:

```bash
pip install g2p-hamster==0.2.3 sea_g2p donglao-g2p
BENCH_SOURCE=pypi python3 listening_test/g2p_compare_100k/bench_100k.py \
    listening_test/g2p_compare_100k/dataset_heldout_2026.tsv.gz
python3 listening_test/g2p_compare_100k/patterns_100k.py   # chéo mẫu từ output đã sinh
```

> **Đính chính 0.2.2**: sea_g2p trong bảng 0.2.1 dưới đây bị đo sai cấu
> hình (G2P.convert() trần, tắt normalizer của nó). Đo lại bằng
> `SEAPipeline(lang="vi").run()`: sea_g2p rò rỉ **0%** — bảng đúng là:

Kết quả (cùng phép đo: số rò rỉ / số bị rơi / lỗi — không đo tốc độ;
"chữ số độc lập" = regex `\b\d+\b`, chỉ đếm dòng `status=ok`):

| Hệ | Rò rỉ số | vi | anh | mix | Lỗi/rỗng | Rơi số ở mẫu giờ `13h00` |
|---|---|---|---|---|---|---|
| **g2p-hamster v0.2.3 (wheel PyPI)** | **0 / 74.760** | 0,00% | 0,00% | 0,00% | 0 | **0 / 239** |
| donglao_g2p | 0 / 74.760 | 0,00% | 0,00% | 0,00% | 0 | **92 / 239 (38,5%)** |
| sea_g2p (SEAPipeline — đo đúng từ 0.2.2) | **0 / 74.760** | 0,00% | 0,00% | 0,00% | 0 | 0 / 239 |

Ba hệ đều đạt **0% rò rỉ** trên held-out khi sea_g2p được cấu hình đúng
— bài test này không còn phân hóa ba hệ bằng chỉ số rò rỉ. Phân mẫu
(2.656 câu có `a/b`, 1.603 câu có `33%`, 14.337 câu có ALL-CAPS,
[`summary_heldout_patterns.json`](listening_test/g2p_compare_100k/summary_heldout_patterns.json)):
cả ba hệ đều 0 lỗi ở ba mẫu đó; chỉ số còn phân hóa là **rơi âm thầm ở
mẫu giờ**: donglao_g2p mất mốc giờ ở 92/239 câu (38,5%) — chữ số biến
mất khỏi đầu ra, nguy hiểm hơn rò rỉ vì không phát hiện được. Nguyên
văn 74.760 output từng hệ nằm trong
[`outputs_*.csv.gz`](listening_test/g2p_compare_100k/).

**Bảng 0.2.1 cũ — GIỮ LẠI để minh bạch (sai vì sea bị tắt normalizer):**

| Hệ (đo 0.2.1, sea sai cấu hình) | Rò rỉ số |
|---|---|
| g2p-hamster v0.2.1 (wheel PyPI) | 0 / 74.760 |
| donglao_g2p | 0 / 74.760 |
| sea_g2p (G2P.convert() trần) | 28.629 / 74.760 (38,29%) |

## Bài test 100k (bộ phát triển, làm trước khi có held-out)

Có ý kiến cho rằng phía normalization VI/EN code-switch repo này thua
sea_g2p. Thôi thì lấy **99.999 câu thật** (52.000 vi · 33.000 anh ·
14.999 mix —
[`dataset_100k.tsv.gz`](listening_test/g2p_compare_100k/dataset_100k.tsv.gz),
chính là corpus
đối chiếu của dự án; 31.456 câu trong đó có chữ số) và chạy 3 hệ qua
cùng một phép đo chất lượng, **không đo tốc độ** (tốc độ đã có bảng
trên; bài này chỉ trả lời câu hỏi "ai verbalize số/ngày/giờ/code-switch
tốt hơn"):
[`listening_test/g2p_compare_100k/`](listening_test/g2p_compare_100k) —
script + **nguyên văn output từng hệ, từng câu** (`outputs_*.csv.gz`) +
summary, tự chạy lại được bằng `bench_100k.py`.

Hai chỉ số khách quan, không cần người chấm:

- **Số rò rỉ** — câu còn chữ số đứng độc lập trong chuỗi ra (regex
  `\b\d+\b`; `13`, `00`, `2026` chưa verbalize → acoustic model không
  đọc được). Chỉ đếm dòng `status=ok`.
- **Số bị rơi** — chữ số **biến mất khỏi đầu ra** (đọc thiếu nội dung
  một cách âm thầm — nguy hiểm hơn rò rỉ vì khó phát hiện).

> **Đính chính 0.2.2**: sea_g2p ở 0.2.0–0.2.1 bị đo sai cấu hình
> (`G2P.convert()` trần, tắt normalizer của nó). Bảng dưới đo lại bằng
> `SEAPipeline(lang="vi").run()` — số "30.665 câu rò rỉ" cũ của sea là
> SAI, số đúng gần như 0.

| Hệ | Rò rỉ số (toàn corpus) | vi | anh | mix | Lỗi / rỗng | Rơi số ở mẫu giờ `13h00` |
|---|---|---|---|---|---|---|
| **g2p-hamster (repo này)** | **0 / 99.999 (0,00%)** | 0,00% | 0,00% | 0,00% | 1 rỗng¹ | **0 / 259** |
| donglao_g2p | 0 / 99.999 (0,00%) | 0,00% | 0,00% | 0,00% | 0 | **114 / 259 (44,0%)** |
| sea_g2p (SEAPipeline — đo đúng từ 0.2.2) | **1 / 99.999 (0,00%)** | 0,00% | 0,00% | 0,01% | 0 | 0 / 259 |

¹ Câu 88974 là tiếng Ba Tư (dữ liệu Wikipedia), repo này trả về rỗng —
công khai nguyên văn trong CSV, không giấu.

Câu duy nhất sea_g2p rò rỉ là tên tàu biển `LA-99095-TS` — nó đọc
"99 095" giữ nguyên mã (tìm nguyên văn trong output dev bằng lệnh tái
lập bên trên; held-out thì sea rò **0** câu). Nói công bằng: sea_g2p
dùng đúng pipeline là đối thủ mạnh — bài 100k
không còn phân hóa bằng rò rỉ; điểm còn lại của nó hụt là ở benchmark
frozen (khớp-đọc-gold, bảng bên dưới).

Đọc bảng: donglao_g2p **đáng khen** — nó verbalize được phần lớn số
(ngày/tháng/năm/phần trăm), 0% rò rỉ. Nhưng nó có kiểu lỗi khác tệ hơn:
**rơi mất con số** ở mẫu giờ. Ví dụ nguyên văn (cùng một câu trong CSV):

| Câu | Hệ | Đầu ra |
|---|---|---|
| "Từ 13h00 - 14h00 cùng ngày…" | **repo này** | "mười ba giờ, mười bốn giờ cùng ngày…" |
| | donglao_g2p | "tɯ2 **h, h** kuŋ2 ŋaj2…" — **cả hai mốc giờ biến mất** |
| "anh dành 1,5 tiếng tập thể dục" | **repo này** | "một **phẩy** năm" (đúng) |
| | donglao_g2p | "một **phần** năm" (sai nghĩa — 1/5 thay vì 1,5) |

Chia nhỏ theo từng mẫu normalization (đếm từ chính `outputs_*.csv.gz` —
script + số liệu trong
[`summary_code_switch.json`](listening_test/g2p_compare_100k/summary_code_switch.json),
sinh lại bằng `patterns_100k.py`):

| Mẫu normalization | g2p-hamster | donglao_g2p | sea_g2p (SEAPipeline) |
|---|---|---|---|
| Câu có `33%` — 2.263 câu | **0% lỗi** | 0% lỗi | **0% lỗi** |
| Câu có `09/11` — 3.026 câu | **0% lỗi** | 0% lỗi | **1/3.026** (tên tàu LA-99095-TS) |
| Câu có `13h00` — 259 câu | **0 rơi** | **114 rơi (44,0%)** — số biến mất âm thầm | 0 rơi |
| Viết tắt ALL-CAPS — 18.584 câu | không sót chữ HOA | không sót | không sót |

Ba hệ hiện đều qua các mẫu normalization phổ biến; chỉ số phân hóa là
**rơi âm thầm ở mẫu giờ** (donglao) và chất lượng phiên âm chi tiết
(frozen benchmark). Output nguyên văn từng hệ của **bài held-out** nằm
trong `outputs_*.csv.gz` (bộ dev không commit nguyên văn để khỏi phình
repo — sinh lại bằng `bench_100k.py` không đối số, lệnh ở trên); mở ra
tự chấm, kể cả câu repo này rỗng.

## Benchmark frozen công khai — v3, 1.118 câu, gold viết trước, chấm bằng máy

Sau bài 100k ở trên, có góp ý đề xuất cách đo tử tế hơn: **bộ test
frozen commit sẵn** (kiểu
[ViTTS-Bench](https://github.com/yoonjae26/vietnamese-tts/blob/main/docs/RESULTS.md)),
gold viết a-priori, **một câu có thể có nhiều cách đọc hợp lệ**, chấm
bằng máy thay vì chấm cảm tính. Repo này làm theo:

- [`benchmark_frozen/test_set.tsv`](benchmark_frozen/test_set.tsv) —
  **1.118 câu** (482 synthetic sinh từ template + 636 real từ
  `dataset_100k`), 12 category: time, date, percent, currency (gồm
  **big_money** v2), units, phone, email/URL, acronyms, **code-switch
  Level 1→6** (Easy → Interleaved → Dense → Ambiguous → Technical →
  adversarial — các câu "OpenAI GPT-5.6 API v1.2…" lấy nguyên từ đề
  xuất), numbers, foreign_names, loanwords.
- [`benchmark_frozen/gold.jsonl`](benchmark_frozen/gold.jsonl) — 426 câu
  synthetic có gold là **câu đầy đủ đã verbalize, viết theo template
  trước khi chạy chấm**, mỗi câu cho phép nhiều cách đọc ("một nghìn
  **hoặc** một ngàn" đều đúng).
- [`benchmark_frozen/frozen_meta.json`](benchmark_frozen/frozen_meta.json)
  — version + lý do mỗi lần sửa test set. **v2** (2026-10-05) thêm
  36 câu `currency/big_money` (tiền ≥ 7 chữ số: "1.000.000đ",
  "1 000 000 đồng", "1.000.000.000 đồng"…) — lớp dữ liệu bị thiếu ở v1;
  lỗi đọc "1.000.000đ" thành "một chấm không chấm không đồng" của wheel
  0.2.1 do **đánh giá độc lập** phát hiện, đáng lẽ máy phải bắt được
  bằng lớp này. Mọi câu/gold khác của v1 giữ nguyên từng ký tự (416
  synthetic + 636 real, thứ tự không đổi).
- Cách chấm (vì cả 3 hệ đều xuất **phôn vị**, không thể so string với
  gold text): chạy hệ trên câu gốc **và** trên từng câu gold, so edit
  distance trong **chính không gian phôn vị của hệ đó** — không map IPA
  chéo giữa các hệ, công bằng tuyệt đối. sim = 1 ⟺ hệ đọc đúng như một
  cách đọc gold. 0 ⟺ đọc khác hoàn toàn.

| Hệ | Leakage (còn số) | Drop giờ (`13h00` → mất số) | Khớp đọc gold (mean / số câu ≥0.95) |
|---|---|---|---|
| **g2p-hamster (repo này, v0.2.5)** | **0 / 1.118** | **0** | **0,982** · 396/456 |
| sea_g2p — `SEAPipeline` (đo đúng từ 0.2.2) | 0 / 1.118 | 0 | 0,966 · 315/456 |
| donglao_g2p | 0 / 1.118 | **103** | 0,906 · 240/456 |
| sea_g2p — `G2P.convert()` trần (cấu hình sai của 0.2.0–0.2.1, giữ lại để đối chiếu) | **828 / 1.118 (74%)** | — | 0,657 · **0/456** |

**Kết luận sau khi đo lại sea_g2p đúng cấu hình:** g2p-hamster vẫn
nhỉnh nhất (0,982 vs 0,966) nhưng **không "bỏ xa"** — chênh lệch thật
~1,3 điểm khớp-đọc, sea_g2p đạt 0 rò rỉ / 0 rơi. Các tuyên bố "sea rò
72%", "0/390 câu khớp" của bản 0.2.1 là **sai vì đo sai cấu hình** —
chúng tôi giữ dòng `sea_g2p_raw` trong
[`summary_frozen.json`](benchmark_frozen/summary_frozen.json) để ai cũng
đối chiếu được cả hai cấu hình. Cảm ơn người phản biện đã bắt được lỗi
này — chính việc công bố output nguyên văn của chúng tôi là thứ cho
phép audit.

Theo từng category (khớp đọc gold — ours / donglao / sea đúng cấu hình):

| Category | repo này | donglao | sea_g2p |
|---|---|---|---|
| time (133) | **1,000** | 0,769 | 0,952 |
| date (104) | **0,971** | 0,954 | 0,955 |
| percent (119) | **0,998** | 0,990 | 0,998 |
| currency (142) | **0,987** | 0,953 | 0,959 |
| units (92) | **0,971** | 0,958 | 0,959 |
| phone (17) | **1,000** | 0,841 | 1,000 |
| acronyms (157) | **0,981** | 0,792 | 0,973 |
| code-switch (150) | 0,909 | 0,886 | **0,955** |
| adversarial (44) | **0,971** | 0,875 | 0,947 |

**Và công khai cả những chỗ repo này CHƯA hoàn hảo** (nguyên văn trong
[`outputs_ours_v2.csv`](benchmark_frozen/outputs_ours_v2.csv)):

- Lỗi tiền ≥ 7 chữ số của 0.2.1 — **đã sửa trong 0.2.2** (regex version
  nuốt số nhóm-nghìn; `RE_MONEY_SUFFIX` chỉ khớp `$`): cả 36 câu
  big_money giờ đọc đúng thang nghìn/triệu/tỷ, bị chặn hồi quy bằng
  unit test + frozen v2. Khớp đọc gold của repo 0,984 → **0,985**;
- v3 (0.2.5) thêm 3 level phủ lỗ hổng bản 3 của đánh giá độc lập:
  `caps_units` (60 KG, 500 ML, 100 KM/H), `currency_codes` (USD/EUR/
  usd/vnđ/VNĐ), `transport_codes` (VN123, SE8) — 30 câu mới, mọi câu v2
  giữ nguyên từng ký tự. Ở code-switch sea_g2p nhỉnh hơn (0,955 vs
  0,909) — công khai luôn, không chọn lọc số;
- `97,8%` trong câu mix được đọc kiểu anh "ninety-seven point eight" —
  có chủ đích hay lỗi, để người nghe quyết;
- một phần điểm trừ là gold hẹp: `12 GB` đọc "gờ-bê" (cách đọc phổ
  biến) nhưng gold chỉ chấp nhận "gi bai" — ghi để minh bạch.

Số liệu bảng trên đo trên **code 0.2.2** và **tái lập lại bằng wheel PyPI
0.2.3** (`BENCH_SOURCE=pypi`, import từ site-packages): mọi dòng
`outputs_*.csv` **giống hệt từng byte** — chỉ provenance trong
`summary_frozen.json` khác (ghi version wheel + espeak-ng 1.51).

Gold do dự án tự viết, chưa qua người ngoài duyệt — bù lại toàn bộ
output từng hệ, từng câu, script sinh và script chấm đều nằm trong
[`benchmark_frozen/`](benchmark_frozen) để ai cũng audit được. Test set
là frozen v2: muốn sửa câu nào phải bump version và ghi lý do.

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

- `from g2p_hamster import text_to_profile_v2_full` → dict đầy đủ — **KHUYÊN DÙNG**
- `from g2p_hamster import text_to_profile_v2` → `(profile, errs, notes)`
- `from g2p_hamster import text_to_profile` (v1) → `(profile, errs)`

> ⚠️ **Footgun API (giữ để tương thích, đổi tên sẽ vỡ người dùng cũ):**
> `text_to_profile` — tên "mặc định" nghe như bản chuẩn — lại là
> **v1 fail-closed**: câu có từ lạ bị TỪ CHỐI, email/SĐT bị rụng khỏi
> chuỗi phôn vị (chỉ báo trong `errs`). Bản cứu tối đa, không bao giờ bỏ
> câu là `text_to_profile_v2` / `_v2_full`. Dùng v1 chỉ khi bạn cần
> fail-closed cho prep dữ liệu train.

**Chạy test:** `python -m unittest discover -s tests -t .` (88/88).

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

## Bản v2 — cứu EN (nâng cấp khuyến nghị)

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

Tổng **809 case test, 0 fail** (0.2.5 — thêm test đơn vị HOA, mã tiền,
mã chuyến bay, t1_review, label spell). Bảng đầy đủ, kèm các benchmark dữ liệu thật phía trên:

| Bộ test | Kết quả |
|---|---|
| t0 regression — tokenize/detect/verbalize (đã tách tiny2) | 41/41 test OK |
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
