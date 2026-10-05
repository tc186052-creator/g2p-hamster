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

## Cài đặt & chạy

```bash
# không cần cài gì thêm — chỉ Python 3.11+; espeak-ng (tuỳ chọn, cho v2)
sudo apt install espeak-ng   # hoặc brew install espeak-ng

python3 -c "
import sys; sys.path.insert(0, 'v2')
from g2p_v1 import text_to_profile
p, errs = text_to_profile('Xin chào, hôm nay trời đẹp quá!')
print(p)
# → sin caː↘w, hom naj ʈʂəː↘j dɛʔ↓p kwaː↗!
"
```

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
r["sources"]   # {"core": n, "cmu": n, "espeak": n, "spell": n}
r["provenance"]  # policy hash (code+mapping+pin lõi) + espeak version/voice/options
```

`text_to_profile_v2(text)` giữ nguyên API cũ `(profile, errs, notes)`.

**strict / best_effort**:

- `mode="best_effort"` (mặc định, cho **render**): câu luôn đọc tiếp, từ
  hụt bị bỏ TỪ và báo tường minh.
- `mode="strict"` (cho **prep dữ liệu train**): từ chối cả câu
  (`state="rejected"`) nếu mất unit nội dung, nếu unit được cứu bằng nguồn
  ngoài `strict_policy` (mặc định nhận `cmu` + `spell`; **espeak phải
  opt-in** vì là suy diễn chưa duyệt), hoặc nếu profile rỗng dù câu có
  nội dung. Lưu ý: strict bảo đảm đủ coverage + nguồn theo policy,
  KHÔNG bảo đảm phát âm đúng.

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
| G2P v2 (state/strict/scope/espeak mock + thật) | 37/37 test OK |
| G2P fase D/E (`test_g2p.py`) | 111 PASS, 0 FAIL |
| vi_rules/vi_syllable | 466 PASS, 0 FAIL |
| scope_policy mutation probes | 16 PASS, 0 FAIL |
| cmu_en fase C | 47 PASS, 0 FAIL |
| tone/coda mapper kokoro178 | 74 PASS, 0 FAIL |

So sánh v1 vs v2 trên 5.000 câu Wikipedia tiếng Việt (metric theo
COVERAGE — KHÔNG phải độ chính xác phát âm): 60,4% giống hệt v1 · 9,9%
v1 bỏ câu / v2 đủ coverage · 7,3% v1 bỏ câu / v2 đọc thiếu (đã báo) ·
0,2% cả hai hụt · 1,6% v1 đủ mà v2 đọc thiếu (chủ yếu markup wiki và từ
có dấu ngoài phạm vi — từng câu nằm trong `lech_duyet.tsv`) · 20,5% đọc
khác v1 do nâng cấp OOV anh (v1 đánh vần từng chữ → v2 phiên âm thật).
Số liệu này đo đọc đủ/thiếu/rỗng; muốn kết luận đọc ĐÚNG cần gold được
duyệt hoặc đánh giá nghe.

## License

- Code + bảng từ điển tự soạn: **Apache-2.0**
- `03_vendor/cmudict/`: BSD-2-Clause (giữ nguyên LICENSE)
- Wiki sentences dùng làm dữ liệu test: CC BY-SA 3.0 (nguồn Wikimedia)
