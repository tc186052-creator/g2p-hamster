# kokoro178_tone_pinned.md — KẾT QUẢ [V] thanh điệu + so chuỗi frontend gốc (A3)

Ngày: 01/10/2026. Trạng thái: **[V] ĐÃ XÁC MINH ở mức nguồn (so chuỗi, chưa nghe audio)** —
bước 1+2 của 4.9.3; bước 3 (nghe ma/mà/… qua checkpoint) còn dành cho E6.

## 1. Nguồn đã pin

| Nguồn | Pin | SHA256/ghi chú |
|---|---|---|
| PyPI `vig2p` | **0.1.0** | `vig2p/core.py` = `c8861388c411869ecad3b8565729d6c5287a7a8cc2fd6159d3793ac41239a7fe`. **KHÔNG phải** clone GitHub hoang1007/vig2p (8835c30) — bản PyPI chứa `VietnameseG2P` + `VI_FIXUPS` mà pipeline iamdinhthuan dùng thật |
| PyPI `sea-g2p` | **0.10.0** | backend G2P **thật sự** của pipeline: `vig2p 0.1.0` chỉ là vỏ bọc `sea_g2p.SEAPipeline(lang="vi")` + bảng `VI_FIXUPS` |
| GitHub iamdinhthuan/Kokoro-Vietnamese | `a249afe5555aec6c435165c2f61ec0f71284812f` | `improve_phoneme.md` (mô tả adapter) + code thật `src/vig2p`/`scripts/prepare_vietnamese_dataset.py` |
| GitHub hoang1007/vig2p | `8835c30113893d1302708f179d619b49444a75bb` | chỉ tham khảo; frontend vi thuần luật, digit KHÁC (sắc=5, ngã=3) — không dùng làm chuẩn convention |
| venv đối chiếu | `03_vendor/venv_vig2p` | pip freeze: cmudict 1.1.3, phonemizer 3.4.0, sea-g2p 0.10.0, vig2p 0.1.0 (espeak-ng hệ thống 1.51) |

**Cảnh báo digit được xác nhận bằng nguồn**: bảng digit↔mũi tên trong `improve_phoneme.md`
(3→↗, 5→ʔ↗) chỉ đúng khi ghép với digit nguồn sea-g2p (sắc=`ɜ`, ngã=`5`). Digit của
hoang1007/vig2p GitHub là NGƯỢC (sắc=5, ngã=3) — map digit→digit qua 2 nguồn này sẽ hoán
đổi sắc/ngã. Master của ta namespace theo TÊN nên miễn nhiễm; profile map theo tên.

## 2. Chuỗi transform thật của checkpoint (kết luận nguồn)

```text
chữ vi → sea-g2p 0.10.0 (thanh = digit: 1 ngang, 2 huyền, ɜ sắc, 4 hỏi, 5 ngã, 6 nặng;
         chèn ˈ/ˌ trước nucleus; đơn vị như "t̪", "tʃ", "e-", "yə") 
       → VI_FIXUPS (vig2p 0.1.0): tʃ→ʧ, e-→æ, 1/7→→, 2→↘, 3/ɜ→↗, 4→↓, 5→ʔ↗, 6→ʔ↓,
         ɗ/đ→d, ʐ→ʒ, t→θ (context "th"), s→ʂ (context "s"), z→ʝ (context "gi")
       → stream train checkpoint
```

## 3. Kết quả [V] — so chuỗi trên âm tiết THẬT (top tần suất corpus 1M)

Công cụ: `06_tools/a3b_so_chuoi_am_tiet_that.py`; dữ liệu `02_data/profiles/a3_am_tiet_that_top5000.tsv`.

| Số đo | Kết quả |
|---|---|
| Âm tiết thật có dấu (top 5000) | 2.561 (11.585.825 lần xuất hiện) |
| Bảng ứng viên parse được | 2.547 (99,45%) |
| **Mũi tên + ʔ ngã/nặng + VỊ TRÍ trước coda** | **2.547/2.547 = 100%** (kể cả theo tần suất) |
| Output frontend có ký tự ngoài vocab 178 | 0 |
| Output profile ta có ký tự ngoài vocab 178 | 0 |
| 14 âm chưa parse | từ ngoại lai (café, pokémon, fiancé, josé, beyoncé, maría, lópez, gardaí, axít) + biến thể chính tả ư+ô=ươ (nhuộm) + 2 lỗ bảng nhỏ (khuếch: ê+ch; buồm: ơ+m; tuýp: y+p) — xử lý ở fase B (bảng vần đầy đủ + exceptions) |

Trên ma trận cấu trúc (25.782 tổ hợp onset×vần×thanh, `a3_diff_tong.tsv`): chỉ dùng được
để chẩn đoán — 46,7% output frontend có space vì frontend tự nhào nặn âm tiết KHÔNG phải
từ thật (xác nhận đúng cảnh báo "2 bộ lọc" 4.6.5). Bài học: [V] chỉ có ý nghĩa trên phân
phối thật, không trên tổ hợp cấu trúc thuần.

### Quyết định profile từ [V]

1. **NGANG = KHÔNG mũi tên** (đổi từ dự kiến "→"): trên 1.500 âm tiết ngang thật, 98,6%
   tần suất frontend KHÔNG đánh dấu (chỉ quirk vần "âu" — câu/đâu/lâu/sâu — có `→` nội
   tại frontend). Master giữ nguyên TONE_NGANG là prosody token; chỉ profile đổi.
2. **Bảng 4.6.1 phần còn lại CHÍNH XÁC**: huyền↘ · sắc↗ · hỏi↓ (không ʔ) · ngãʔ↗ · nặngʔ↓
   — 100% trên 2.547 ca thật, đúng vị trí TRƯỚC coda.
3. Loss map thêm **ɝ→ɚ** (vocab 178 không có ɝ) ngoài 4 loss đã ghi (ɓ→b, ɗ→d, ʐ→ʒ, tʰ→θ).

## 4. Khác biệt quy ước giữa frontend gốc và master ham/0.1 (để fase B/E6 xử lý)

| Chủ đề | Frontend gốc (checkpoint học) | Master ta (đã duyệt) | Xử lý |
|---|---|---|---|
| coda -ch | `ʧ` (mạch = m æ ʔ↓ ʧ) | PHONE_K (k) | Giữ master; ghi loss/convention vào profile? → quyết ở E6 nghe thử; hiện profile xuất k |
| "anh/ênh/inh" | æ/e/i + ɲ (e-→æ) | aː+ɲ / e+ɲ / i+ɲ (mặc định [B]) | Đã [B] chờ gold; checkpoint dùng æ — đưa vào gold-dev |
| "ach" | æ + c | ă (A_SHORT) + k [B: có thể +j] | Đối lập mác/mách giữ được cả 2; chốt ở fase B |
| "ây" | ə+**ɪ** (quirk, khác "ay"=a+j) | ə+j | Quirk frontend; giữ master |
| ư | `y` (tường = t y ə ↘ ŋ) | PHONE_UHORN (ɨ) | Profile map ɨ→y? — checkpoint học `y`+`ə`; quyết ở E6 |
| Stress | ˈ/ˌ chèn TRƯỚC nucleus trên MỌI âm tiết vi | vi không có stress token | Profile nên chèn ˈ để in-distribution → quyết ở E6 (cờ config) |
| Language-ID | âm tiết trông như từ Anh đứng LẦN NHUẬN bị đọc kiểu Anh (ban→bˈæn) | route đến từ tầng 1, không tự đoán | Khác biệt CÓ CHỦ ĐÍCH — ưu điểm thiết kế của ta |
| ngang quirk | vần "âu" có `→`, còn lại không | TONE_NGANG token | Profile: không arrow (mục 3.1) |

## 5. Cập nhật số liệu A0 (vá 6 lỗ bảng phát hiện qua [V])

`a0_phan_loai_latin_vi.py` vá 10 lỗ: `_CodaMap`+k · `_NUC_OK["Ưə"]`+n · `_W_OK["Â"]`+j ·
`_W_OK["I"]`+t,p · `_W_OK["Ă"]`+t · `_W_OK["Ơ"]`+"" · `_W_OK["Ê"]`+ch · `_W_OK["Ơ"]`+w ·
`_W_OK["O"]` cả khối (được/trước/quốc) — các từ thật trước giờ bị rớt cấu trúc. Chạy lại
01/10/2026 (số cuối):

| Nhóm | Trước vá (làm tròn, báo cáo 01/10 sớm) | Sau vá (01/10, bảng đã vá) |
|---|---|---|
| (a) đọc nguyên dạng | ~1.060 unique / ~2,07M lần | **1.133 / 2.067.245** |
| (b) fold theo prior | ~653 / ~26k | **698 / 27.823** |
| (c) không phải âm tiết vi | ~99.6k / ~774k | **99.477 / 770.518** |
| shadow (cận trên nguy cơ đa nghĩa) | 788.252 | 788.252 |

Số cũ trong G2P_KE_HOACH_DANH_GIA 4.8 được thay bằng số này ở lần cập nhật tài liệu kế
tiếp; bản chất kết luận không đổi.

## 7. A4 — từ điển fold nhóm (b) + tự đánh giá strip-dấu (01/10/2026)

Artifact (`02_data/fold/`): `fold_vi.tsv` (698 entry, prior tần suất corpus, bất biến
fold_key 0 vi phạm) · `uncertain_folds.log` (321 cặp top1-top2 chênh <20% — nguyên liệu
tiny model v1.5) · `tan_suat_am_tiet.tsv` (124.628 âm tiết + tần suất — dùng chung fase B)
· `a4_danh_gia_strip.json`.

Tự đánh giá "miễn phí nhãn" (20.000 mẫu có dấu từ corpus build, mô phỏng input ASCII bằng
fold_key, seed 20261001 — **KHÔNG phải gold**, gold-dev làm ở fase B theo 4.11):

| Bucket | Số | Ghi chú |
|---|---|---|
| (a) đọc nguyên dạng | 14.740 (73,7%) | trong đó 7.865 giữ nguyên âm đoạn; phần còn lại gộp ăâêôơư — đặc tính văn mất dấu, không phải lỗi |
| (b) prior chọn đúng từ gốc | 3.598 | **độ chính xác prior trong nhóm (b) = 68,5%** — phần 31,5% là đúng loại đa nghĩa mà uncertain_folds đo; nâng bằng ngữ cảnh (v1.5) + tiny model, không đổi policy v1 |
| sai / rơi spell | 1.658 | gồm cả form strip rơi (c) vì lỗ bảng vần — fase B bảng vần đầy đủ sẽ giảm |

Phát hiện thêm từ A4: generator ứng viên đặt dấu thanh sai vị trí nguyên âm ở vần 2
nguyên âm ("việt" → "víêt") — khi dựng vi_rules fase B phải dùng luật đặt dấu chuẩn
(đã cài trong `a3_so_chuoi_frontend.py:place_mark`).

## 6. Việc còn treo sau [V]

- Fase B: bảng vần đầy đủ (bổ sung ê+ch, ơ+m, y+p, biến thể ư+ô=ươ) + audit đơn ánh điều 7
  + gold-dev — sẽ giải các cell [B] (anh/ach) và bảng quy ước mục 4.
- E6: nghe A/B để quyết 3 convention còn mở của profile: coda -ch (k vs ʧ), ư (ɨ vs y),
  chèn ˈ cho vi (có/không).
