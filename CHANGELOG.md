# CHANGELOG

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
