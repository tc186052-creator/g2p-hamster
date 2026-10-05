# G2P 00 — Hợp đồng đầu vào: IR từ tầng 1 → tầng 2

Ngày: 01/10/2026. Nguồn sự thật: `01_tiny_model/02_rules/t0/pipeline.py` (schema `ir/0.1`).
**Tầng 2 ăn đầu ra này nguyên xi, không sửa lại câu** (nguyên tắc hợp đồng các tầng).

## 1. Cách lấy đầu ra tầng 1

```bash
cd 01_tiny_model && ../venv/bin/python -c "
import sys; sys.path.insert(0,'02_rules')
from t0 import pipeline, Config
import json; print(json.dumps(pipeline.normalize('Doanh thu Q3 tăng 12.5%', Config()), ensure_ascii=False, indent=1))"
```

Runtime mặc định đã có tiny2-MC ở chế độ auto (tắt: `T0_TINY2=off`).
Corpus silver 1M build theo luật thuần: `01_tiny_model/01_data/silver/corpus_ir_1M.jsonl.gz`.

## 2. Cấu trúc IR (schema `ir/0.1`)

```json
{
 "schema": "ir/0.1",
 "text": "Doanh thu Q3 tăng 12.5%",
 "clean": "…",                       // văn bản sau clean() — tham khảo
 "sent_lang": "vi",                  // vi | en | mixed
 "tokens": [ …dưới đây… ],
 "review": [ {"i":…, "surface":…, "reason":…} ],   // token luật không chắc — nơi G2P cần cẩn trọng
 "logs": […],
 "read_string": "Doanh thu quý ba tăng mười hai phẩy năm phần trăm."
}
```

Mỗi token:

| Trường | Ý nghĩa | Giá trị gặp |
|---|---|---|
| `i` | chỉ số thứ tự | |
| `surface` | văn bản gốc của token | |
| `cat` | loại token | word, punct, number, abbr, acronym, unit, date, time, money, symbol, url, email, phone, slang, pm_am, icon |
| `origin` | nguồn quyết định route | vi / en / neu (trung tính) |
| `route` | **ngôn ngữ đọc** — G2P bắt buộc theo đây | vi / en |
| `read` | chế độ đọc | "word" mặc định, "spell" (gõ chữ)… |
| `verbal` | chuỗi đọc đã điền của token (tầng 1 sinh) | |
| `break` | ngắt nghỉ | major (. ! ? …) / minor (, ; : -) / null |
| `intonation` | "rising" cho `?` | |
| `review` | cờ luật không chắc | oov, kho_bat, kho_bat_heuristic, kho_bat_tiny, acronym_spell, caps_word, don_vi_d… |

Phân bố `cat` trên toàn corpus 1M (24,3M token, corpus silver hiện hành): word ~19,6M ·
punct ~2,5M · number ~464k · acronym ~119k · abbr ~72k · unit ~35k · symbol ~33k ·
date ~29k · slang ~7,2k · url ~9,3k · money ~8,7k · time ~3,1k · phone ~1,6k · email ~156.
(Chi tiết: `01_tiny_model/01_data/review/split_stats.json`.)

## 3. Điều tầng 2 phải bảo đảm

1. **Theo `route` từng token**: vi → phoneme vi; en → phoneme en. Không phiên âm chéo.
2. **`cat` quyết cách đọc**: `abbr`/`acronym` với `read="spell"` → gõ từng chữ (chữ theo
   phoneme bảng chữ cái của route); `word` → đọc như từ; punct → im lặng, chỉ giữ `break`.
3. **Nhịp/ngắt**: giữ `break`/`intonation` của tầng 1 — không chèn/xóa ngắt tùy tiện.
4. **Token `review` không rỗng** = chỗ luật không chắc — tầng 2 làm đúng nhiệm vụ (đọc
   theo route/cat cho tới), KHÔNG tự sáng tạo lại câu.
5. Token en (route en) thường là tiếng Anh chuẩn (kho en) hoặc OOV latin — danh sách
   từ latin tần suất cao để thiết kế nhánh en xem `G2P_01_tu_vung_thuc_te.md`.

## 4. Đầu ra của tầng 2 (chưa chốt — sẽ quyết cùng user)

- Mỗi token → chuỗi phoneme + (tuỳ chọn) thanh điệu riêng cho vi; định dạng IPA hay
  bộ phoneme rút gọn **phụ thuộc tầng 3 chọn acoustic model nào** (piper/VITS ăn
  phonemizer khác nhau) — xem `G2P_02_khao_sat_lua_chon.md`, câu hỏi mở #1-#2.
