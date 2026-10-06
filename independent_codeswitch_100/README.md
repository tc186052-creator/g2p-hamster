# Bộ test VI–EN code-switch độc lập — 2 × 100 câu

Bộ này được tạo độc lập với benchmark phoneme (`benchmark_frozen/`) để rà một câu hỏi hẹp:

> **Router của `g2p-hamster` có gán đúng ngôn ngữ (route `vi`/`en`) cho từng token trong câu code-switch hay không?**

Không dùng gold IPA, không đưa gold qua chính G2P để so edit-distance — chấm trực tiếp trên IR tầng 0: `text -> normalize() -> tokens[].route`, so với nhãn anchor viết tay trước.

## Nội dung

| File | Nội dung |
|---|---|
| `cases.jsonl` | 100 câu chính, 10 nhóm × 10 câu, 436 anchor (205 VI, 231 EN) |
| `cases_overlap_100.jsonl` | 100 câu "từ chồng lấn" (in, may, no, to, a, me…), 837 anchor — nguồn: bộ độc lập 2 |
| `run_independent.py` | runner thuần stdlib: gọi `g2p_hamster.t0.normalize()`, so `route` với anchor, exit code 0/1 |
| `baseline_report.json` / `baseline_report_overlap.json` | trace đầy đủ lần chạy gần nhất |

Anchor `confidence=medium` là các từ có thể bị coi là từ vay mượn, cách đọc phụ thuộc policy; runner báo riêng high/medium.

## Chạy

```bash
python3 independent_codeswitch_100/run_independent.py
python3 independent_codeswitch_100/run_independent.py --data independent_codeswitch_100/cases_overlap_100.jsonl
python3 independent_codeswitch_100/run_independent.py --json-out report.json   # lưu trace
```

## Kết quả hiện tại (sau các bản vá route 05/10/2026)

| Bộ | Route accuracy | Câu đạt toàn bộ anchor | sent_lang |
|---|---|---|---|
| Chính (`cases.jsonl`) | **436/436 = 100%** | 100/100 | mixed 100/100 |
| Overlap (`cases_overlap_100.jsonl`) | **836/837 = 99,88%** (sai duy nhất 1 anchor medium) | 97/100 | không chấm |

Trước khi vá, bộ chính chạy trên checkout `0d1f641` cho 428/436 (98,17%) và `sent_lang=mixed` chỉ 63/100.

## Các lỗi router mà bộ test bắt được và đã vá

1. **Từ Anh không dấu bị kéo về vi** (`webcam`, `config`, `screen`, `stream`, `log`, `livestream`): thêm vào `detect.assign_routes` một luật cấu trúc — từ ASCII **không thể âm tiết hóa theo cấu trúc tiếng Việt** (cụm phụ âm đầu "scr/str/w…", vần cuối sai "g/x/d…", đa âm tiết không tách được) thì route `en`, cờ review `khong_am_tiet_vi`. `t0/dicts.py` có bộ tách âm tiết nghiêm ngặt `tach_am_tiet_vi()` (backtrack, onset/coda hợp lệ) — phân biệt với `syllables_vi()` nới lỏng dùng để lọc corpus.
2. **"in"/"to" là từ Việt thật** ("in tài liệu", "to tiếng") nhưng nằm trong `kho_quyet_en` nên bị đọc Anh cả trong câu Việt: chuyển về `kho_bat` để láng giềng quyết — "Tôi đang in tài liệu" đọc vi, "I work in Hanoi" đọc en. Thêm `scan`, `git` vào `kho_quyet_en` (không phải từ Việt).
3. **"livestream" đọc "lives tre am"** (entry cũ trong `abbrev_vi.tsv`, phiên âm hóa kiểu Việt) — mâu thuẫn với chính sách chốt 02/10 "từ Anh đọc Anh, không phiên âm hóa": đã bỏ entry, giờ đọc nhánh Anh.
4. **"May I join cuộc họp…"**: nhánh "I" tiếng Anh chỉ chạy khi ước lượng sent pass-0 ≠ vi; giờ tính thêm bằng chứng từ kề là từ `kq_en`.
5. **`sent_lang` dán nhãn sai 37/100 câu**: nhãn cũ tính trước pass 1, chỉ đếm từ `kq_en`, nên câu có từ en nhờ cmudict/cấu trúc bị coi là vi thuần. Giờ chốt lại nhãn sau pass 3: có cả wordish route vi lẫn route en → `mixed`.

## Giới hạn đã biết

- Overlap `OV097` "Anh gửi **me** file đó được không?" — "me" trùng fold của "mẹ", láng giềng trái là vi nên router chọn vi; nhãn en được giữ ở mức `medium` như một giới hạn ghi nhận.
- Acronym ALL-CAPS (`API`, `GPU`, `TTS`) trong câu Việt route `vi` theo chính sách repo ("acronym hỏi theo câu") — nhãn anchor đã chỉnh theo chính sách này, không phải lỗi.
- Đây là **bài kiểm tra routing**, không phải kiểm định phát âm: route đúng không bảo đảm phát âm cuối đúng.
