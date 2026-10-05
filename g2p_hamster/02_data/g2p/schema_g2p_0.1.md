# schema_g2p_0.1.md — schema output tầng G2P `g2p/0.1` (fase D, v21)

Ngày: 02/10/2026 (v21 sau HAU_KIEM_FASE_D_V20 — đóng D20-01/02/03 + khai báo
D20-04/05; v20 đã đóng §3.1-3.4, §4, §5.1/§5.2; v19 đã đóng D18-01).
Định nghĩa record output của `01_g2p/g2p.py` — tầng 2 tiêu thụ IR `ir/0.1`
(theo `00_docs/G2P_00_hop_dong_dau_vao.md`, KHÔNG sửa tầng 1), sinh record
master `ham/0.2` và chuỗi profile kokoro178 (adapter DEBUG riêng).

## 1. Envelope output (mỗi lần chạy)

| Trường | Ý nghĩa |
|---|---|
| `schema` | "g2p/0.1" |
| `inventory_hash` | sha256 raw bytes TSV master — bắt buộc trong MỌI output (inventory_schema §7) |
| `inventory_contract_hash` | sha256 TSV + REQUIRED_CONTRASTS + SHARED_UNICODE_REPR + MERGE_RULES (inventory_schema §7) |
| `g2p_policy_hash` | fingerprint tầng D (xem §6, v0.2) — mutation consumer/fold/spell/ledger/cmu_en → ĐỔI |
| `resource_snapshot` | sha256 của SNAPSHOT fold/spell/cmudict thực sự hiệu lực (cache-aware — identity định danh đúng snapshot đang dùng); MỌI giá trị là **str sha256** (D20-01 — bảng đã parse không phải identity), fold/spell khớp pin trong `g2p_resource_pins.json` |
| `resource_override` | (chỉ khi fold_tab test-override) {test_only: true, fold_override_sha256, note} — output thử nghiệm KHÔNG được hiểu là theo pin mặc định |
| `versions` | profile (kokoro178/0.2) · dialect (chứa GIÁ TRỊ pin domain) · lexicon · fold · `b_c_dependencies` = {en_policy_hash, domain_config_hash, scope_policy_hash, approval_policy_hash} — identity mang phụ thuộc B/C hiệu lực |
| `contract_errors` | lỗi shape/version/field của envelope IR + đồng thuận read_string (rỗng = sạch) |
| `records` | list record token (§2) |

## 2. record token (mỗi token IR)

| Trường | Ý nghĩa |
|---|---|
| `i, surface, cat, route, verbal` | nguyên dạng IR — g2p không sửa |
| `read, break, intonation, origin` | nguyên dạng IR — ĐƯỢC TIÊU THỤ/GIỮ (D18-02) |
| `status` | enum ĐÓNG 9 giá trị (§3) |
| `read_complete` | đã đọc ĐỦ token — False ⇒ tầng sau KHÔNG được coi output là đủ |
| `unsupported_chars` | ký tự chưa có tên chữ — không bao giờ bị câm |
| `errors` / `contract_errors` | lỗi tường minh |
| `validation` | kết quả invariant tương quan tại serialize (rỗng = sạch) |
| `detail` | provenance scope/fold/reason |
| `master.read_units[]` | record master ĐẦY ĐỦ (§4) — nguồn sự thật cho tầng 3 |
| `profile_debug` | adapter kokoro178 — debug_only=True, KHÔNG thay thế master |

## 3. status enum ĐÓNG + `read_complete`

| status | Điều kiện | read_complete |
|---|---|---|
| `ok` | mọi unit đọc được (VI parse / EN key dict) | true |
| `fold` | ≥1 unit VI nhóm (b) ASCII phân giải bằng pin `fold_vi.tsv`; tone_state="fold" | true |
| `spell` | unit OOV đọc theo tên chữ (VI seed — quy ước CHỜ DUYỆT; EN `LETTER_NAMES` đã C duyệt) | true **chỉ khi** unsupported rỗng |
| `no_nucleus` | EN key dict không nguyên âm (hmm…) | false |
| `scope_excluded` | unit (input HOẶC ứng viên fold) thuộc QD57 — kiểm TRƯỚC đường phát âm VÀ re-check sau fold (D18-01); không lách sang protected partner hay spell | false |
| `unresolved` | verbal rỗng / không parse + ngoài fold/spell / spell không sinh reading nào | false |
| `not_word` | cat chưa có đường tiêu thụ (icon) — deferred tường minh | false |
| `unknown_route` | route lạ trên cat tiêu thụ — fail loud | false |
| `control` | punct — im lặng, GIỮ `break`/`intonation` cho tầng sau (hợp đồng §3.2) | false |

**Tiêu thụ cat** (D18-02): cat≠word KHÔNG đồng nghĩa bỏ qua — number/abbr/
acronym/unit/date/money/… tầng 1 đã điền `verbal` dạng từ ⇒ g2p tách theo dấu
cách thành read unit và đọc theo `route` (không tự normalization lại, không tự
suy cách đọc mới). cat=punct → `control`.

## 4. record master `master.read_units[]`

Mỗi unit: `text` (nguyên dạng) · `read_unit_index` · `source_token_id` ·
`status` · `read_complete` · `unsupported_chars` · `detail` ·
`syllables[]` với `syllable_index` + `lang` (vi: onset/glide/nucleus/coda/
tone/tone_state/flags; en: onset/nucleus/coda/stress/stress_state) +
`source_graphemes` (inventory_schema §5 — liên kết nguồn là structural
metadata, KHÔNG rebuild master từ unicode profile).

## 5. Invariant (D18-03 — validate + serializer)

- **Unit:** status cấm phát âm ⇒ KHÔNG syllables, read_complete=False
  (fault injection gắn syllables vào unit scope_excluded bị BẮT).
- **Token roll-up nhất quán:** status cấm phát âm ⇒ ≥1 unit cùng nhóm;
  read_complete=False. ok/fold/spell ⇒ mọi unit pronounceable.
- **spell:** unsupported khác rỗng ⇒ read_complete=False; spell KHÔNG sinh
  reading nào ⇒ unresolved (không phải "một phần của không có gì").
- **ok/fold** không được có unsupported_chars.
- **Serializer:** chạy validate trước; mọi record lỗi hoặc status cấm phát âm
  → profile_debug text rỗng + errors; master vẫn xuất kèm trạng thái để truy vết.

## 6. Fingerprint tầng D (D18-04)

`g2p_policy_hash` = sha256{schema "g2p_policy/0.2", code_sha256(g2p.py),
**fold_tsv, spell_tsv** (D20-05: tên khóa payload — trong `resource_snapshot`
output chúng mang hậu tố `_sha256`), cmudict_sha256, scope_ledger_sha256,
inventory_hash, inventory_contract_hash, **b_c_dependencies** = {en_policy_hash,
domain_config_hash, scope_policy_hash, approval_policy_hash}, profile_version,
g2p_schema_version}.

- Mutation bảng fold / spell / consumer / ledger / inventory / cmu_en → hash
  ĐỔI; khôi phục → baseline (test H9: M1 fold mach→mách, M2 bỏ re-check scope
  ứng viên, M3 pins hỏng, M4 cmu_en AA→AE).
- `load_fold()`/`load_spell_vi()` KIỂM SHA đối chiếu
  `02_data/g2p/g2p_resource_pins.json` — lệch → SystemExit (fail-closed;
  mutation bảng không âm thầm ăn theo output).
- Snapshot cache (D20-01): warm cache giữ {tab, sha256} đã kiểm pin cho CẢ
  fold và spell; `g2p_policy_hash()` là hàm thuần theo cấu hình — cold == warm
  trong cùng process; mutation đĩa SAU warm-load không làm lệch identity khỏi
  reading đang dùng (test H9-M5 thật cho cả hai bảng).
- Snapshot cache mở rộng (v22, hiệu năng cho corpus 1M — fase E): cmu dict
  nạp **1 lần/process** (`C.load_cmu()` có verify_pin trong đó; `pronounce`
  nhận `cmu=` snapshot), `_cmudict_sha` + b_c_dependencies (attestation/
  ledger tĩnh trong lần chạy) memo cùng khuôn — identity = snapshot đang
  dùng, giá trị identical với gọi lại từng lần. `cmu_en.py` KHÔNG đổi →
  `en_policy_hash` giữ nguyên; `g2p_policy_hash` đổi theo code g2p.py
  (baseline mới `a24db1ab…` — chấp nhận theo điều kiện chốt D v21 §5).
- Nguồn bảng fold: `02_data/fold/fold_provenance.md` — khai THỰC phần xác
  minh được và phần không còn hồ sơ (builder A0 đã mất), không bịa lịch sử.
- `fold_tab` override chỉ cho test — production dùng pin; provenance bảng
  thay thế thuộc caller.
- spell_vi: `approval_status = seed_pending_owner` trong pins — C duyệt 26
  tên chữ US KHÔNG tự động phê duyệt bảng VI.

## 7. Tính chất bắt buộc

- **Deterministic (I2):** hàm thuần + bảng pin — cùng envelope → cùng byte
  output (stream_json sort_keys).
- **Không đụng tầng 1:** không sửa verbal/surface/cat/route/read/break, không
  ghép/tách token, không thêm pause.
- **Fail loud:** contract lỗi → contract_errors + CLI exit 1; route lạ →
  unknown_route; pin lệch → SystemExit.

## 8. Bổ sung v20 (hậu kiểm HAU_KIEM_FASE_D_V19)

- **`read="spell"` được THỰC THI** (không chỉ lưu): route=en → per-letter
  `LETTER_NAMES` (26 tên chữ US, C chấp nhận v16) — "US" → U-S (you-ess),
  "A" → EY + STRESS_PRIMARY (không tra từ "us"/SCHWA từ điển); ký tự ngoài
  bảng → `unsupported_chars`, spell trọn mới complete. route=vi → tier-1 đã
  spell-out trong verbal (vd email) — giữ đường từ; unit đơn chữ đi seed
  spell_vi (TRẠNG THÁI CHỜ DUYỆT — không tự duyệt seed qua dispatch).
- **`read_unit_index` phân biệt từng unit** trong token (hết trùng 0,0);
  leaf identity = (source_token_id, read_unit_index, syllable_index) duy nhất.
- **Malformed IR → lỗi cấu trúc**: envelope null/[], tokens[null], cat=[],
  break:{} — type guard TRƯỚC membership/dispatch; CLI JSON null → exit 1
  dạng JSON contract_errors, không traceback.
- **read_string đối chiếu theo ranh giới nội dung**: dãy MẢNH CHỮ-SỐ
  (tách tại mọi ký tự không chữ/số, biến thể nháy chuẩn hóa) theo thứ tự —
  bất khả tri quy tắc gắn dấu câu của renderer tầng 1 (vd "Jerry-Đường"),
  nhưng bắt ĐỦ thừa/thiếu/sai thứ tự từ vựng ("nam thêm"/"xnam"/"namnam")
  và read_string rỗng khi có reading. Trên corpus thật còn ~1,2% envelope
  read_string (picked) ≠ tokens — consensus BÁO đúng (contract_errors),
  không phải lỗi g2p.
- **Aggregate parent/child**: status/read_complete/unsupported_chars của
  parent PHẢI khớp giá trị derive từ units — parent tuyên bố đủ khi child
  còn thiếu (fault injection) bị validate BẮT và serializer TỪ CHỐI. Debug
  partial reading hợp lệ vẫn được phép (không cấm).

## 9. Bổ sung v21 (hậu kiểm HAU_KIEM_FASE_D_V20)

- **D20-01 — identity resource luôn str sha256:** cache spell chuyển khuôn
  fold ({tab, sha256} đã kiểm pin); `effective_resource_shas()` /
  `resource_snapshot` chỉ trả str sha256; `g2p_policy_hash()` cold == warm
  trong cùng process (regression test H8 + H9-M5).
- **D20-02 — route guard nhánh spell:** `read="spell"` với route ngoài
  {vi, en} → `unknown_route` fail-loud, ĐỐI XỨNG nhánh từ — không đọc im
  lặng theo đường vi (test 4 ca {neu, jp} × {word, spell}).
- **D20-04a — vi-spell delegate tier-1 (khai báo + fixture thật):** tier-1
  spell-out trong `verbal` cho email route=vi `read="spell"` — hành vi vi-spell
  phụ thuộc verbal tầng 1, ngoài phạm vi bundle cũ. Fixture verbal TẦNG 1 THẬT
  kèm theo: `02_data/g2p/fixture_tier1_email_spell.json` (chụp 02/10/2026,
  `ir_sha256` tự khai, chỉ ĐỌC IR không sửa tầng 1) — D giữ đường từ,
  `vuhoanplus`/`gmail` → unresolved tường minh (không bịa, không spell-out lại
  ở tầng 2), envelope tier-1 qua contract sạch.
- **D20-04b — quy ước case của read_string consensus (khai báo):** so sánh
  mảnh CHỮ-HOA/THƯỜNG NGUYÊN VĂN (case-sensitive) — tier-1 giữ nguyên văn case
  giữa `verbal` và `read_string` render, nên so nguyên văn là quy tắc thực của
  IR và bắt được lệch case thật. Số đo ~1,2% envelope picked≠tokens trên
  corpus đã tính theo quy ước này. (Phương án case-fold bị loại để không nuốt
  lệch case thật.)
- **D20-05 — đếm delta v19→v20 là 6 sửa / 53 không đổi** (0 mới); chữ "7 sửa/
  52 không đổi" ở brief/header/reference_diff v20 là lỗi đếm văn bản — 6 tên
  file liệt kê đúng đủ; bundle cũ giữ nguyên byte, cải chính ghi tại
  reference_diff v21.
