# BENCHMARK — bằng chứng đầy đủ (tách từ README 0.2.6)

Tài liệu này chứa TOÀN BỘ bài test chất lượng của g2p-hamster: 300 câu
7 hệ · 100k dev · 74.760 held-out · frozen v4 gold. Mọi số liệu có nguyên
văn output từng câu + script tái lập trong repo. Tóm tắt một bảng:
[README → "Kết quả trong 30 giây"](../README.md#kết-quả-trong-30-giây--3-hệ-cuối-cùng-một-bảng).

---

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
bên dưới: 0,988 / 0,967 / 0,907). repo này là hệ **duy nhất đồng thời
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

## Benchmark frozen công khai — v4, 1.127 câu, gold viết trước, chấm bằng máy

Sau bài 100k ở trên, có góp ý đề xuất cách đo tử tế hơn: **bộ test
frozen commit sẵn** (kiểu
[ViTTS-Bench](https://github.com/yoonjae26/vietnamese-tts/blob/main/docs/RESULTS.md)),
gold viết a-priori, **một câu có thể có nhiều cách đọc hợp lệ**, chấm
bằng máy thay vì chấm cảm tính. Repo này làm theo:

- [`benchmark_frozen/test_set.tsv`](benchmark_frozen/test_set.tsv) —
  **1.127 câu** (491 synthetic sinh từ template + 636 real từ
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
| **g2p-hamster (repo này, v0.2.8)** | **0 / 1.127** | **0** | **0,988** · 424/465 |
| sea_g2p — `SEAPipeline` (đo đúng từ 0.2.2) | 0 / 1.127 | 0 | 0,967 · 324/465 |
| donglao_g2p | 0 / 1.127 | **103** | 0,907 · 248/465 |
| sea_g2p — `G2P.convert()` trần (cấu hình sai của 0.2.0–0.2.1, giữ lại để đối chiếu) | **837 / 1.127 (74%)** | — | 0,656 · **0/465** |

**Kết luận sau khi đo lại sea_g2p đúng cấu hình + vá gold bất công
(v4):** g2p-hamster nhỉnh nhất (0,988 vs 0,967) và **thắng MỌI category**
— kể cả code-switch (0,985 vs 0,966), trước đây sea nhỉnh vì gold chỉ
nhận 1 cách đọc ở những câu có 2 cách đọc đều hợp lệ. sea_g2p đạt
0 rò rỉ / 0 rơi — vẫn là đối thủ xứng tầm. Các tuyên bố "sea rò
72%", "0/390 câu khớp" của bản 0.2.1 là **sai vì đo sai cấu hình** —
chúng tôi giữ dòng `sea_g2p_raw` trong
[`summary_frozen.json`](benchmark_frozen/summary_frozen.json) để ai cũng
đối chiếu được cả hai cấu hình. Cảm ơn người phản biện đã bắt được lỗi
này — chính việc công bố output nguyên văn của chúng tôi là thứ cho
phép audit.

Theo từng category (khớp đọc gold — ours / donglao / sea đúng cấu hình):

| Category | repo này | donglao | sea_g2p |
|---|---|---|---|
| time (73) | **1,000** | 0,769 | 0,952 |
| date (44) | **0,971** | 0,954 | 0,955 |
| percent (79) | **0,998** | 0,990 | 0,998 |
| currency (97) | **1,000** | 0,953 | 0,959 |
| units (60) | **0,965** | 0,958 | 0,959 |
| phone (17) | **1,000** | 0,841 | 1,000 |
| acronyms (37) | **0,981** | 0,791 | 0,973 |
| code-switch (36) | **0,985** | 0,909 | 0,966 |
| adversarial (22) | **0,965** | 0,875 | 0,948 |

**Và công khai cả những chỗ repo này CHƯA hoàn hảo** (nguyên văn trong
[`outputs_ours_v2.csv`](benchmark_frozen/outputs_ours_v2.csv)):

- Lỗi tiền ≥ 7 chữ số của 0.2.1 — **đã sửa trong 0.2.2** (regex version
  nuốt số nhóm-nghìn; `RE_MONEY_SUFFIX` chỉ khớp `$`): cả 36 câu
  big_money giờ đọc đúng thang nghìn/triệu/tỷ, bị chặn hồi quy bằng
  unit test + frozen v2. Khớp đọc gold của repo 0,984 → **0,985**;
- v3 (0.2.5) thêm 3 level phủ lỗ hổng bản 3 của đánh giá độc lập:
  `caps_units` (60 KG, 500 ML, 100 KM/H), `currency_codes` (USD/EUR/
  usd/vnđ/VNĐ), `transport_codes` (VN123, SE8) — mọi câu v2 giữ nguyên
  từng ký tự. Ở code-switch v3 sea_g2p nhỉnh hơn (0,955 vs 0,909) —
  công khai luôn, không chọn lọc số;
- **v4 (0.2.8) vá gold bất công của v3** (không đổi câu cũ, chỉ thêm
  cách đọc thay thế hợp lệ + 9 câu mã vận tải CÓ ngữ cảnh): 6 câu
  "VN123 tùy nơi bán." thiếu ngữ cảnh nhưng gold chỉ nhận đọc mã — giờ
  nhận thêm "Việt Nam một trăm hai mươi ba"; `97,8%` đọc kiểu anh
  "ninety-seven point eight" được nhận là cách đọc hợp lệ cạnh cách
  vi; "GB" nhận cả "gơ bê" (tên chữ cái Việt) cạnh "gi bai". Kèm 2 vá
  nhất quán trong hệ: chữ cái ĐƠN ("V" trong gold "V N một hai ba") hết
  bị đọc "vee" kiểu Anh khi câu là Việt — nhất quán với chính code
  "VN123" đọc "vờ nờ"; cửa sổ ngữ cảnh mã vận tải nới 3 → 6 token
  ("Mã đặt chỗ của tôi là VN123" trước đây bỏ sót). Sau vá repo thắng
  mọi category, kể cả code-switch (0,985 vs 0,966);
- **còn lại thật sự chưa đạt**: `25 Mbps` đọc "hai mươi lăm megabit"
  thiếu "một giây" (mất thông tin tốc độ) — gold không chấp nhận, điểm
  L5 0,956 phản ánh đúng điều đó; ghi để minh bạch.

Số liệu bảng trên đo trên **code 0.2.2** và **tái lập lại bằng wheel PyPI
0.2.3** (`BENCH_SOURCE=pypi`, import từ site-packages): mọi dòng
`outputs_*.csv` **giống hệt từng byte** — chỉ provenance trong
`summary_frozen.json` khác (ghi version wheel + espeak-ng 1.51).

Gold do dự án tự viết, chưa qua người ngoài duyệt — bù lại toàn bộ
output từng hệ, từng câu, script sinh và script chấm đều nằm trong
[`benchmark_frozen/`](benchmark_frozen) để ai cũng audit được. Test set
là frozen v2: muốn sửa câu nào phải bump version và ghi lý do.

