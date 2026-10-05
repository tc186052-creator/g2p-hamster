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
| `tests/` | Regression test t0 (44 ca: ví dụ chuẩn + torture set) |

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
cả câu. `v2/g2p_v2.py` giữ tiên đề **cấm bịa phát âm** nhưng không bao giờ
bỏ câu nữa — từ hở được cứu theo bậc, mỗi lần cứu đều ghi provenance:

1. **Thử route ngược lại** — từ việt parse được thì đọc việt, không đẩy qua anh (và ngược lại)
2. **CMUdict** (135k entry, pin) — phiên âm chính thức US
3. **espeak-ng** — quy tắc chính tả anh phủ mọi chuỗi chữ latin (IPA → ARPABET → master)
4. **Spell tên chữ** — phương án cuối cho từ ≤4 chữ
5. Hụt hết → bỏ TỪ đó (không bỏ câu), ghi vào notes

Chuẩn hóa NBSP/ký tự ẩn trước khi vào tầng 1, từ có chữ số không được cứu
(verbalize là việc của tầng 1).

```bash
python3 v2/g2p_v2.py "Trong hóa sinh học, H là ký hiệu của histidin."
# • cứu 'histidin' từ espeak: hˈɪstɪdˌɪn

# so sánh v1 vs v2 trên văn bản của bạn (đa tiến trình)
python3 v2/so_sanh.py --input van_ban.txt --procs 22
```

## Kết quả đối chứng

| Bộ test | Kết quả |
|---|---|
| t0 regression (đã tách tiny2) | 37/37 test OK |
| G2P fase D/E (`test_g2p.py`) | 111 PASS, 0 FAIL |
| vi_rules/vi_syllable | 466 PASS, 0 FAIL |
| scope_policy mutation probes | 16 PASS, 0 FAIL |
| cmu_en fase C | 47 PASS, 0 FAIL |
| tone/coda mapper kokoro178 | 74 PASS, 0 FAIL |

So sánh v1 vs v2 trên 5.000 câu Wikipedia tiếng Việt: **75,9% giống hệt ·
24% v1 bỏ câu / v2 đọc được · 0 câu cả hai cùng từ chối · 0 hồi quy**.

## License

- Code + bảng từ điển tự soạn: **Apache-2.0**
- `03_vendor/cmudict/`: BSD-2-Clause (giữ nguyên LICENSE)
- Wiki sentences dùng làm dữ liệu test: CC BY-SA 3.0 (nguồn Wikimedia)
