# CHANGELOG

## 0.2.8 — 2026-10-06

**Benchmark frozen v4 — vá gold bất công + 2 vá nhất quán hệ** (yêu cầu
của chủ dự án: "test công bằng liêm chính"):

- **Gold v4, không đổi câu cũ**: 6 câu `transport_codes` của v3
  ("VN123 tùy nơi bán.") KHÔNG có ngữ cảnh vận tải nhưng gold chỉ nhận
  đọc mã — giờ nhận thêm "Việt Nam một trăm hai mươi ba" / "ét i tám";
  thêm 9 câu `transport_codes_ctx` CÓ ngữ cảnh ("Chuyến bay VN123…")
  chỉ chấp nhận đọc mã — benchmark giờ kiểm 2 chiều của policy
  context-gated; L5 nhận thêm cách đọc thay thế hợp lệ: số kiểu Anh
  ("ninety-seven point eight"), tên chữ cái Việt ("gơ bê" cạnh
  "gi bai"), đơn vị rút gọn ("mi giây"). Scorer lấy max trên alt nên
  thêm alt không trừ điểm hệ nào; mọi câu/gold v3 khác giữ nguyên từng
  ký tự (real dịch đúng +9 dòng, nguyên văn).
- **Chữ cái ĐƠN đọc theo ngữ cảnh câu**: "V" trong gold "V N một hai
  ba" từng bị nhánh cứu cmudict đọc "vee" kiểu Anh trong khi chính code
  "VN123" đọc "vờ nờ" — hệ tự mâu thuẫn, benchmark công bằng vừa lộ ra.
  Giờ chữ cái đơn (len=1) không còn được cứu sang en, đọc theo ngữ cảnh
  (câu Việt → tên chữ Việt, câu Anh → "vee").
- **Cửa sổ ngữ cảnh mã vận tải 3 → 6 token**: "Mã đặt chỗ của tôi là
  VN123" trước đây bỏ sót "mã" (cách 6 token) và đọc thành "Việt Nam
  một trăm hai mươi ba" ngay trong ngữ cảnh đặt chỗ.
- **Kết quả frozen v4**: repo **0,988** (424/465 ≥ 0,95) — sea_g2p
  0,967 (324/465), donglao 0,907 (248/465). Repo thắng MỌI category,
  kể cả code-switch (0,985 vs 0,966) — trước đây sea nhỉnh ở hạng mục
  này vì gold hẹp, đã công khai số đó ở 0.2.5–0.2.7. Còn thiếu thật sự:
  "25 Mbps" đọc thiếu "một giây" (L5 0,956) — ghi minh bạch trong
  docs/BENCHMARK.md.
- Suite 101/101 + core xanh; bộ test độc lập code-switch giữ nguyên
  436/436 + 836/837.

## 0.2.7 — 2026-10-06

Theo **bộ test code-switch độc lập do người ngoài viết** (2 × 100 câu,
1.273 anchor route, vào repo tại `independent_codeswitch_100/`) — trước
vá: 428/436 route, `sent_lang=mixed` chỉ 63/100:

- **Luật cấu trúc mới cho từ Anh**: từ ASCII không thể âm tiết hóa theo
  cấu trúc tiếng Việt (cụm phụ âm đầu "scr/str/w…", vần cuối sai
  "g/x/d…", đa âm tiết không tách được — `webcam`, `config`, `screen`,
  `stream`, `log`…) route `en` kèm cờ review `khong_am_tiet_vi`, thay vì
  bị mặc định đọc vi trong câu Việt. Kèm bộ tách âm tiết nghiêm ngặt
  `dicts.tach_am_tiet_vi()` (backtrack, onset/coda hợp lệ) — phân biệt
  với `syllables_vi()` nới lỏng (bị nhiễm từ corpus, "webcam" cũng lọt).
- **"in"/"to" là từ Việt thật** ("in tài liệu", "to tiếng") nhưng nằm
  trong `kho_quyet_en` nên "mưa to" từng bị đọc "tu" kiểu Anh: chuyển
  về `kho_bat` cho láng giềng quyết. "I work in Hanoi" vẫn đọc en.
  Thêm `scan`, `git` vào `kho_quyet_en`.
- **Bỏ entry "livestream" → "lives tre am"** trong `abbrev_vi.tsv`
  (phiên âm hóa kiểu Việt, mâu thuẫn chính sách 02/10 "từ Anh đọc Anh").
- **"May I join cuộc họp…"**: nhánh "I" tiếng Anh tính thêm bằng chứng
  từ kề là từ `kq_en` kể cả khi ước lượng cấp câu nói vi.
- **`sent_lang` chốt sau pass 3**: có wordish route vi lẫn route en →
  `mixed` (nhãn cũ tính trước pass 1 chỉ đếm `kq_en`, sai 37/100 câu
  code-switch).
- Token `mention` (`@handle`) và `filename` không bị luật cấu trúc
  re-route — "@"/"chấm" đọc theo ngữ cảnh Việt ("a còng handle",
  "final report chấm P D F").
- Kết quả sau vá: bộ chính **436/436 route = 100%**, sent_lang mixed
  100/100; bộ overlap **836/837** (giới hạn đã biết: "me" ~ "mẹ").
  Benchmark frozen: sim khớp-đọc **0,9818 giữ nguyên**, 396/456 ≥ 0,95,
  0 câu có gold bị đổi output. Suite pytest 101/101.

## 0.2.6 — 2026-10-06

**BREAKING** (chưa có người dùng package nên đổi thẳng theo chuẩn dự án
chuyên nghiệp, không cần shim tương thích):

- `text_to_profile` giờ là **V2** — trả `(profile, errs, notes)`, cứu
  tối đa, không bao giờ bỏ câu. Chấm dứt footgun mà cả hai đợt đánh giá
  độc lập đều bắt: tên "mặc định" trỏ vào bản v1 fail-closed rụng
  email/SĐT.
- Bản v1 đổi tên tường minh: `text_to_profile_v1` (nguyên `(profile,
  errs)`). CLI `--v1` giữ nguyên hành vi.
- README tách phần benchmark chi tiết (300 câu / 100k dev / held-out /
  frozen) sang `docs/BENCHMARK.md` — README gọn còn 37 KB, giữ bảng
  "Kết quả trong 30 giây" + chính sách đọc + cài đặt.

## 0.2.5 — 2026-10-06

Theo **bản 3 của đánh giá độc lập** (nhất quán đơn vị, mất nội dung HOA,
cờ review bị nuốt, espeak ɚ, mã chuyến bay, dataset held-out kín):

- **Nhất quán đơn vị/mã tiền sau số — đọc NGHĨA bất kể HOA/thường**:
  `100 USD` → "một trăm đô la" (trước đây đánh vần "iu ét đi"),
  `100 EUR` → "một trăm euro" (trước đây token thô "Eur" còn trong chuỗi),
  `100 vnđ` → "một trăm đồng" (trước đây bị BỎ từ — mất nội dung),
  `100 KM/H` → "ki lô mét một giờ", `500 ML`, `60 KG` — trước đây đánh
  vần hoặc rụng. Ngoại lệ có chủ đích: **VNĐ HOA** giữ nguyên văn "V N Đ"
  (quyết của chủ dự án) và chữ cái đơn (`4K` vs `4k`) giữ hành vi cũ.
  Chính sách được KHAI BÁO trong README thay vì để người dùng đoán.
- **Cờ review tầng 1 nổi lên kết quả v2**: `text_to_profile_v2_full`
  trả thêm `t1_review` và ghi từng cờ vào `notes` — trước đây tầng 1
  phát hiện bất thường (`oov`, `don_vi_d`…) nhưng v2 trả `notes=[]`.
- **espeak-ng: thêm `ɚ` vào bảng IPA→ARPABET** — mọi từ OOV có âm /ɚ/
  (rất phổ biến en-us, vd "kubernetes") trước đây rơi khỏi bảng → hết
  bậc cứu; giờ phiên âm được qua espeak.
- **Label trung thực khi phải đánh vần**: unit đánh vần vì hết bậc cứu
  giờ ghi `source="spell"` + note, không còn mượn nhãn `source="core"`
  (khiến lỗi vô hình khi audit).
- **Mã ký hiệu vận tải đọc nhất quán**: `Chuyến bay VN123` → "vê ên một
  hai ba" (từng chữ số, như mã ≥5 chữ số đã làm) trong ngữ cảnh
  chuyến/tàu/mã/lô; ngoài ngữ cảnh giữ hành vi cũ.
- **Dataset held-out công khai**: `listening_test/g2p_compare_100k/
  dataset_heldout_2026.tsv.gz` (74.760 câu đã lọc trùng dev) nằm trong
  repo — tuyên bố "0 rò rỉ trên 74.760" giờ kiểm chứng độc lập được,
  không cần file cục bộ nữa.
- **Frozen v3** (`frozen_meta.json`): thêm 3 level phủ lỗ hổng —
  `caps_units`, `currency_codes`, `transport_codes` (30 câu mới); mọi
  câu/gold v2 giữ nguyên từng ký tự. Ours 0,982 · sea 0,966 · donglao
  0,906; công khai luôn category code-switch sea nhỉnh (0,955 vs 0,909).
- Test cũ khẳng định hành vi LỆCH ("100 USD" → "iu ét đi") được cập nhật
  theo chính sách mới.

## 0.2.4 — 2026-10-05

- Giảm rụng ở best_effort (mục 4.3/đề xuất 7 của đánh giá độc lập):
  - `50.000đ/lượt` dính — trước đây rụng "hết bậc cứu", giờ đọc
    "năm mươi nghìn đồng trên lượt" (giống dạng có space).
  - `ISBN 978-604-1-12345-6` — trước đây rụng "chữ số — tầng 1 chưa
    verbalize", giờ đọc từng chữ số + "gạch" (mất 0 nội dung).
  Cả hai bị khóa bằng unit test.

## 0.2.3 — 2026-10-05

- Sửa `g2p_hamster.__version__` — 0.2.2 phát hành với attr còn ghi
  "0.2.1" (bỏ hardcode, đọc từ package metadata). Không đổi gì khác.

## 0.2.2 — 2026-10-05

Bản vá theo **đánh giá độc lập 2026-10-05** (bản 2). Số liệu benchmark trong
README được **đo lại toàn bộ** trên bản này.

### Sửa lỗi

- **Số tiền ≥ 7 chữ số đọc sai** (chặn dùng cho nội dung giá tiền):
  `1.000.000đ` bị đọc "một chấm không chấm không đồng" vì regex version
  `\d+(\.\d+){2,3}` nuốt số nhóm-nghìn TRƯỚC nhánh số, và `RE_MONEY_SUFFIX`
  chỉ khớp `$`-hậu tố. Giờ đọc đúng thang nghìn/triệu/tỷ:
  `1.000.000đ` → "một triệu đồng", `1 000 000 đồng` → "một triệu đồng",
  `1000000đ` → "một triệu đồng", `1.000.000.000 đồng` → "một tỷ đồng".
  Số 7+ chữ số KHÔNG cạnh đơn vị tiền vẫn đọc từng chữ số (mã/link).
  Bị máy bắt bằng unit test mới (`test_money_grouped_7_digits`) và
  benchmark frozen v2.
- **benchmark_speed.py: thông lượng bị ×3** — vòng repeat reset `lats` mỗi
  lượt nên `total` chỉ là lượt cuối, còn mẫu số lại nhân `repeat`. Số
  tốc độ trong README cũ bị thổi phồng 3 lần; đã đo lại.
- **bench_100k.py: tự loại toàn bộ câu khi đo chính bộ dev** (nhầm giữa
  bản .tsv và bản .gz của cùng bộ) — chỉ ảnh hưởng lần chạy dev trong repo.

### Đo lại số liệu đối thủ (quan trọng)

- **sea_g2p bị đo sai cấu hình ở 0.2.0–0.2.1**: harness gọi
  `G2P(lang="vi").convert()` TRẦN (chỉ phiên âm), bỏ qua bộ chuẩn hoá 17
  bước mà chính sea_g2p tài liệu hoá (`SEAPipeline(lang="vi").run()`).
  Phát hiện bởi đánh giá độc lập — cảm ơn người phản biện; chính việc
  công bố output nguyên văn của chúng tôi là thứ cho phép phát hiện này.
  Đo lại bằng `SEAPipeline`: sea_g2p **rò rỉ 0%** (trước đây công bố
  29,7% — SAI), khớp-đọc-gold ~0,97. Kết luận mới: g2p-hamster **vẫn
  nhỉnh hơn** nhưng KHÔNG "bỏ xa" — chênh lệch thật ~1,4 điểm khớp-đọc.
  Cấu hình trần giữ lại trong benchmark frozen dưới tên `sea_g2p_raw`
  để đối chiếu minh bạch với số đã công bố cũ.

### Bổ sung

- **Benchmark frozen v2** (`frozen_meta.json`, version 2): thêm level
  `currency/big_money` — 36 câu tiền ≥ 7 chữ số (9 giá trị × 4 template).
  416 câu synthetic + gold v1 giữ nguyên từng ký tự; 636 câu real giữ
  nguyên thứ tự. Lý do bump: lớp dữ liệu bị thiếu ở v1 — lỗi 0.2.1 đáng
  lẽ bị máy bắt chứ không phải bị người ngoài bắt.
- **espeak-ng được ghi phiên bản**: vào `summary_frozen.json`
  (provenance), vào `g2p_resource_pins.json`, CI in `espeak-ng --version`
  vào log. ~28% câu phụ thuộc espeak-ng nên lệch version phải khai báo.
- **`.gitignore`** + bỏ `build/`, `g2p_hamster.egg-info/` khỏi git
  (157 file rác bị commit, repo phình 217 MB).

### Lưu ý API (footgun cũ, chưa đổi tên để giữ tương thích)

- `text_to_profile` (tên mặc định) là **v1 fail-closed** — câu có từ lạ
  bị từ chối, email/SĐT bị rụng. Bản "cứu tối đa" là
  `text_to_profile_v2` / `text_to_profile_v2_full`. **Khuyên dùng v2.**

## 0.2.1 — 2026-10-05

- Sửa "kg" đọc "ki lô gam" (từ "ký" sai chính tả trong units.tsv).
- benchmark frozen + held-out chạy trên wheel PyPI 0.2.1 (`BENCH_SOURCE=pypi`).

## 0.2.0 — 2026-10-05

- Benchmark frozen công khai 1.052 câu (gold viết a-priori, chấm máy).
- Bài test held-out 74.760 câu chưa từng thấy + bài test dev 100k câu.
- Bổ sung pattern layers: %, ngày a/b, giờ 13h00, ALL-CAPS.
