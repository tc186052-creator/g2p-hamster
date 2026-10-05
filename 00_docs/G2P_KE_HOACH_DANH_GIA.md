# TẦNG 2 — G2P: KẾ HOẠCH THIẾT KẾ & TÀI LIỆU ĐÁNH GIÁ

- **Ngày**: 01/10/2026 — **bản 5** (bản vá vòng duyệt 3: I3-MASTER/PROFILE, coda tắc sắc/nặng, ER stress, đối lập mức chuỗi âm tiết, diễn giải A0 trung thực; Phụ lục C)
- **Trạng thái**: **HƯỚNG KIẾN TRÚC ĐÃ DUYỆT — BẢN VÁ 5 ÁP XONG.** Triển khai: A1 (inventory+audit PASS), A2 (vocab 178 pin), A3 (profiles.py + 52 test khóa + [V] so chuỗi frontend gốc 100% mũi tên đúng trên 2.547 âm tiết thật — `02_data/profiles/kokoro178_tone_pinned.md`; profile chốt NGANG không mũi tên, loss thêm ɝ→ɚ). A0 vá 10 lỗ bảng, chạy lại: (a) 1.133 · (b) 698/27,8k. A4 xong (fold_vi 698 entry, uncertain 321, prior nhóm (b) đúng 68,5% trên strip-eval 20k mẫu). A0–A4 hoàn tất — mốc kế: code review, rồi fase B (bảng vần + audit đơn ánh + gold-dev), C, D, E, F.
- **Người đọc**: chủ dự án + người đánh giá ngoài — tài liệu tự chứa
- **Vị trí**: `02_hamster_G2P/` — tầng 2 trong chuỗi 4 tầng

Quy ước: `→` = "được đọc thành"; ô đánh dấu **[B]** = dự thảo, khóa bằng gold/đối chứng ở fase B;
**[V]** = cần xác minh thực nghiệm trước khi chốt (ghi đích xác minh). Ví dụ tài liệu: **render tự động từ fixture ĐÃ DUYỆT** — output của implementation KHÔNG
tự phong thành đáp án gold; regression `.expected` có thể sinh bằng code nhưng diff phải
được người duyệt trước khi khóa; gold do người duyệt độc lập (bài học: 3 vòng ví dụ viết
tay đều bị bắt lỗi).

---

## 0. Hướng dẫn đọc

- Hiểu việc làm: mục 1–3. Thiết kế: mục 4 (soi nhất 4.2, 4.6, 4.8, 4.9, 4.10), 7, 8, 9.
- Người đã đọc bản 3: đọc Phụ lục B trước (liệt kê từng góp ý vòng 2 + chỗ đã sửa).
- Con số đều có nguồn. Số A0 hiện tại là **sơ bộ** (parser vỏ tối thiểu — 4.8.1).

---

## 1. BỐI CẢNH DỰ ÁN

### 1.1. Sản phẩm hướng tới

Hệ TTS **vi + en + mix** tự chủ: văn bản thô → chuỗi đọc → phoneme → acoustic model → âm thanh.
Ưu tiên đọc kiểu phát thanh, xử lý văn bản thực tế.

### 1.2. Kiến trúc 4 tầng

```
[1] CHUẨN HÓA (01_tiny_model)      ✅ hoàn thiện — bàn giao read_string + IR
[2] G2P (02_hamster_G2P)           ◀── tài liệu này
[3] ACOUSTIC MODEL                 ⬜ viết lại Kokoro (nền StyleTTS2), vocab SINH TỪ tầng 2
[4] AUDIO OUT                      ⬜
```

Hợp đồng tầng: tầng sau ăn đầu ra chuẩn tầng trước, **không sửa lại câu**.

### 1.3. Triết lý (chủ dự án chốt)

Luật + từ điển + tiny model tự làm chủ; thư viện ngoài chỉ đối chiếu (vinorm đã bỏ 30/09).
Mọi thay đổi qua gate: test khóa + đối chứng (snapshot chỉ khi sửa chủ đích).
**Dữ liệu test không đem train** — phân tách build/dev/gold/regression ở 4.11.

### 1.4. Tầng 1 đã đạt (bằng chứng)

| Hạng mục | Bằng chứng |
|---|---|
| Pipeline `t0`, IR `ir/0.1` | `01_tiny_model/02_rules/t0/` |
| Test + đối chứng | 44 unit tests OK, 316 câu đối chứng OK |
| tiny1 (route), tiny2-MC (57,5M) | `03_model/`, mode auto |
| Corpus bạc | 1.000.000 câu, 0 exception kỹ thuật, 22,7M token; + supplement ≈0,2M (tổng ≈1,2M) |
| Trọng tài 9B | duyet_v8: oke 65,3% / 867 cần xử lý (7.3) |
| Phân bố | câu vi 588.512 / mixed 227.421 / en 184.067; token route vi 19,4M / en 3,3M |

---

## 2. NHIỆM VỤ CỦA TẦNG 2

### 2.1. G2P là gì

Đổi chữ viết thành chuỗi token phát âm (semantic ID + hiển thị IPA) cho acoustic model.

```
"trường"  →  PHONE_TR PHONE_ƯƠ PHONE_NG + TONE_HUYEN      # hiển thị: ʈʂ ɨə ŋ 2
"browser" →  PHONE_B PHONE_R PHONE_AU PHONE_Z PHONE_ER    # hiển thị: b ɹ aʊ z əɹ
```

### 2.2. Phạm vi

**LÀM**: IR tầng 1 → theo `route` + `cat`/`read` từng token → token phoneme (câu + từng đơn
vị đọc + tone + stress + break), kèm provenance (`source`, `fallback_reason`, span).

**KHÔNG LÀM**:
- Đọc số/ngày/tiền/đơn vị/viết tắt — tầng 1 đã verbalize trong `verbal`.
- Quyết từ nào en/vi — tầng 1 đã gán `route`.
- Sửa câu, thêm bớt ngắt — dùng `break`/`intonation` tầng 1 (biệt lệ được cấp phép ở 4.10.3).
- **Nối âm / biến âm qua ranh giới từ** (coarticulation/sandhi) — đọc rời từng đơn vị là
  chấp nhận được cho giọng phát thanh ở giai đoạn này.
- **Không đụng token âm tiết hợp lệ nguyên dạng** (chính sách bảo toàn fold — 4.8).

**Đặc thù corpus**: 40.305 token latin route-vi (594.639 lần gặp trong mẫu 200k câu; A0 quét
đầy đủ 1M — số sơ bộ tại `02_data/fold/a0_ket_qua.json`). Phần lớn là âm tiết hợp lệ nguyên
dạng / tên riêng / từ lạ — phải phân loại 3 nhóm TRƯỚC khi thiết kế fold (4.8.1).

---

## 3. ĐẦU VÀO — HỢP ĐỒNG TỪ TẦNG 1

Nguồn sự thật: `t0/pipeline.py::normalize()`, schema `ir/0.1`.

**Nguồn sự thật cho G2P = `tokens[]`** (`verbal` + `break` + `intonation` + `route` + `cat`
+ `read`); `read_string` chỉ để hiển thị/đối chiếu.

```json
{
  "text": "Doanh thu Q3 tăng 12.5%",
  "sent_lang": "vi",
  "tokens": [
    {"i":0, "surface":"Doanh", "cat":"word",   "route":"vi", "read":"word", "verbal":"Doanh", "break":null},
    {"i":2, "surface":"Q3",     "cat":"abbr",  "route":"vi", "read":"word", "verbal":"quý ba", "break":null},
    {"i":4, "surface":"12.5%",  "cat":"number","route":"vi", "verbal":"mười hai phẩy năm phần trăm", "break":"major"}
  ],
  "read_string": "Doanh thu quý ba tăng mười hai phẩy năm phần trăm."
}
```
(Ví dụ RÚT GỌN — bỏ token "thu", "tăng"; không phải IR đầy đủ.)

Quy tắc tiêu thụ:
1. Mỗi token: đọc `verbal` (nhiều từ → nhiều đơn vị đọc), giữ liên kết `i` về token gốc;
   `route` áp cho toàn bộ phần mở rộng.
2. **`read="spell"`**: nếu `verbal` khác `surface` (tầng 1 đã verbalize thành chuỗi chữ —
   vd "êm xê") → G2P đọc `verbal` như từ thường; nếu `verbal` rỗng/bằng `surface` → gõ chữ
   `surface` theo bảng chữ cái của route. (Chốt — tránh đánh vần hai lần cho 120k acronym.)
3. `punct` → không phoneme, góp break (4.10.2).
4. **Kiểm hợp đồng bằng canonical renderer**: hàm `render_tokens_to_read_string(tokens[])`
   (ghép `verbal` + cách serialize punct theo đúng một quy tắc, định nghĩa ở fase D, khóa
   bằng đối chứng) — render từ `tokens[]` rồi so với `read_string`; khác nhau =
   `contract_error` (đếm, báo cáo, đẩy về tầng 1 — không tự chữa).
5. Hai biệt lệ được cấp phép (đều ghi `fallback_reason`): spell khi en-OOV không chắc (4.7.4);
   fold nhóm (b) (4.8). Đây là nhiệm vụ được ủy quyền, không phải "sửa câu".

Phân bố `cat` corpus 1M: word 19,6M · punct 2,45M · number 467k · acronym 120k · abbr 73k ·
unit 44k · symbol 33k · date 28k · url 17k · slang 8,7k · money 8,3k · time 3k · phone 1,6k ·
email 156.

---

## 4. KIẾN TRÚC THIẾT KẾ

### 4.1. Sơ đồ dòng xử lý

```
IR tầng 1 (tokens[]: verbal/route/cat/read/break)
   │  (kiểm hợp đồng: render_tokens_to_read_string == read_string?)
   ├─ route=vi, parse trọn theo 4.6 ──► vi_syllable ──► vi_rules ──► token master ──┐
   ├─ route=vi, KHÔNG parse trọn ──► exceptions_vi → fold nhóm (b) → spell          │
   │                                                        (state machine 4.6.7)  │
   ├─ route=en ──► exceptions_en → CMUdict → morphological candidate → en_rules     │
   │                                                          → spell (4.7.4)      │
   ├─ read=spell ──► spell (bảng tên chữ, 3.2) ─────────────────────────────────────┤
   ├─ punct ──► không phoneme + break → CONTROL token ──────────────────────────────┤
   ▼                                                                                 ▼
              MASTER TOKEN STREAM (ham/0.1 — semantic ID; 4.2)
                                                                                 │
              profile transform (nhận thức cấu trúc — 4.9)
                 ├─► kokoro178 (debug adapter)   ├─► emit_vocab_config.py   ├─► debug_ipa
```
(Chỉ MỘT luồng fallback duy nhất, thứ tự cố định, có trạng thái kết thúc — 4.6.7.)

### 4.2. Master `ham/0.1` — token có ID ngữ nghĩa

**Triết lý**: master có **một ID duy nhất cho mỗi đơn vị phát âm mà acoustic model được phép
học**; Unicode/IPA chỉ là một cách hiển thị/export. Đơn vị nhiều code point (`tʰ`, `aʊ`,
`ʈʂ`, `əː`) là **1 token**.

```text
MASTER INVENTORY ham/0.1
├── SEGMENT   (âm đoạn — PHONE_*)
├── PROSODY   (TONE_* vi; STRESS_PRIMARY/SECONDARY en — token gắn âm tiết/nucleus)
└── CONTROL   (PUNCT_* từ break — thứ duy nhất được serialize thành ký tự cho model)
```

- **Ranh giới từ/âm tiết/ràng buộc nguồn = structural metadata** trong record (không phải
  token trong vocabulary cho acoustic ăn): `source_token_id`, `read_unit_index`,
  `syllable_index`. Chỉ PUNCT_* là control token xuất hiện trong stream.
- **Tone** = token prosody gắn đúng 1 âm tiết; **field `tone` trong record là nguồn sự
  thật**, stream được sinh TỪ field (một hướng, không sửa 2 nơi).
- **Stress en** gắn vào **nucleus mang trọng âm** (không cần syllabifier đầy đủ — 4.7.2).
- Artifact fase A: `inventory_schema.md` — định nghĩa entry: semantic ID (ổn định, không tái
  sử dụng) · Unicode repr · loại (segment/prosody/control) · quy tắc thêm token mới +
  migration + versioning (hash; train/infer cùng phiên bản).

**Bảng `required_contrasts` (độc lập với bảng luật — được duyệt riêng)**: cặp đối lập mà
master bắt buộc phân biệt ID: `tr/ch` (ʈʂ/c) · `s/x` (ʂ/s) · `d/gi/r` (z/ʝ/ʐ) · **`a/ă`**
(a dài / a ngắn — 2 ID PHONE_A / PHONE_A_SHORT; cặp tối tiểu tam/tăm, nam/năm) · `e/ê` ·
`o/ô/ơ` · `u/ư` · `â/ơ` · **`d/đ` (z/ɗ)** · 6 thanh · en `θ`≠vi `tʰ` · en `ʒ`≠vi `ʐ` · `ʌ`≠`ə` (AH1 vs AH0).
Mở: `ə` vi-â vs schwa en chung ID hay tách — **[B]** quyết bằng collision-audit + gold.
**Đối lập mức CHUỖI ÂM TIẾT (bắt buộc, không chỉ thành phần)**: `tai≠tay` (ai=aːj, ay=aj) ·
`cao≠cau` (ao=aːw, au=aw) · `mác≠mách` (ac=aːk, ach=ăjk) · `an≠anh` (an=aːn, anh=ăjŋ [B]).
Bảng thành phần (4.6.4/4.6.5) chỉ là mô tả; ánh xạ thực thi quyết bởi **toàn bộ mẫu vần có
điều kiện** — chữ coda quyết chất lượng nucleus (a trước i/o = dài, trước y/u = ngắn;
ch sau a/e = chèn glide j).

**Collision-audit — 6 điều** (chạy fase A, chạy lại mỗi lần sửa bảng): (1) mỗi ID → 1 nghĩa;
(2) mỗi Unicode repr khai báo → đúng 1 ID (2 ID cùng repr phải có cờ `intent_shared` — chỉ
là **ghi chú chủ đích thiết kế**; chia sẻ embedding do tầng 3 quyết theo ID, cùng ID mới cùng
embedding); (3) không symbol ma; (4) prosody/control không được là segment; (5) không segment
nào là digit; (6) mọi cặp trong `required_contrasts` phân biệt được ở master; **(7) đơn ánh thực thi**:
sinh toàn bộ âm tiết hợp lệ → master → gom theo chuỗi đầu ra — nhóm >1 chính tả phải nằm
trong danh sách va chạm chủ đích (vd i/y cùng ID); cặp trùng ngoài danh sách = FAIL.
Giới hạn (trung thực): audit bắt xung đột **đã mô hình hóa**; tính đúng âm vị học do gold.

### 4.3. Tư tưởng đảo chiều

> G2P là nguồn sự thật âm vị: model tương lai ăn theo G2P (vocab sinh từ master bằng
> `emit_vocab_config.py` — ID ổn định + hash + migration), không phải G2P bám model có sẵn.
> Kokoro = **debug adapter** (nghe thử qua checkpoint đã release). Thêm token mới không đụng ai.

### 4.4. Quyết định đã chốt cùng chủ dự án

| Quyết định | Lựa chọn |
|---|---|
| Hướng làm | Lai, tự viết lõi; thư viện ngoài chỉ đối chiếu |
| Định dạng | Master token-ID riêng; không bị vocab Kokoro kéo |
| En OOV | Đọc được thì đọc; không chắc mới spell (state machine 4.7.4) |
| Giọng vi | Bảng âm vị theo config `VI_DIALECT` (mặc định **`vi_chinh_ta`** — inventory bám chính tả, hệ thanh Bắc; tên cũ `vi_bac_tach` bị loại vì gây kỳ vọng sai: Hà Nội nhập tr/ch, s/x) — **[B]**, 7.4 |
| Chống lưng | Chuẩn hóa tầng 1 + corpus 1,2M |

### 4.5. Sự kiện kỹ thuật từ khảo sát (tra 01/10/2026, pin revision khi dùng)

1. Kokoro tokenize **từng ký tự** (`vocab.get(p)`, ký tự lạ bị bỏ âm thầm) — chỉ áp cho chuỗi
   ĐÃ serialize qua profile; master không chịu ràng buộc này.
2. Config.json hai bản (hexgrad base, contextboxai vi) **giống hệt**: `n_token=178`, bảng
   vocab **114 mục**, ID max 177. Diễn đạt đúng: "profile tương thích vocab Kokoro
   (n_token=178)". Cùng token space chứng minh **khả năng mã hóa**, không tự chứng minh đọc đúng.
3. Adapter Kokoro-VN là **biến đổi cấu trúc** (chèn ˈ, tone → mũi tên trước âm cuối, thêm
   glottal cho ngã/nặng, cleanup) — không phải bảng tra 1-1. Chi tiết 4.9.
4. vig2p: fallback nhiều tầng tương tự thiết kế mình → **công cụ tìm bất đồng**, không oracle.
5. **Cảnh báo quy ước thanh**: bảng digit↔mũi tên trong `improve_phoneme.md` KHÔNG khớp thứ
   tự digit trong source vig2p. Không map digit→digit — đi qua **tên thanh** + xác minh thực
   nghiệm (4.9.3). Pin revision mọi nguồn.

---

### 4.6. NHÁNH TIẾNG VIỆT

Mô hình âm tiết: **(thanh) + [âm đầu] + [glide] + [vần chính] + [âm cuối]** — parser trả về
record có cấu trúc. `strip_tone_marks()` chỉ bỏ dấu thanh, **giữ nguyên ă â ê ô ơ ư đ** (chữ,
không phải dấu thanh).

#### 4.6.1. Thanh điệu — namespace theo TÊN

| Tên thanh | Master ID | Digit hiển thị | Kokoro arrow (dự kiến — **[V]** chờ xác minh 4.9.3) |
|---|---|---|---|
| ngang | TONE_NGANG | 1 | → |
| huyền | TONE_HUYEN | 2 | ↘ |
| sắc | TONE_SAC | 3 | ↗ |
| hỏi | TONE_HOI | 4 | ↓ |
| ngã | TONE_NGA | 5 | ʔ↗ |
| nặng | TONE_NANG | 6 | ʔ↓ |

- Digit chỉ hiển thị; mọi chuyển đổi qua **tên thanh**. **Ngã/nặng mang ʔ; hỏi = ↓ không ʔ** —
  nhất quán toàn văn, chờ xác minh [V].
- Test khóa: `ma / mà / má / mả / mã / mạ` → 6 chuỗi khác nhau đúng vị trí; ca sắc/nặng với
  âm cuối tắc (4.6.5).

#### 4.6.2. Âm đầu (onset) **[B]**

| Chính tả | IPA (hiển thị) | Ví dụ |
|---|---|---|
| b | ɓ | bò → ɓ ɔ TONE_HUYEN |
| c, k | k | cá → k a SAC |
| ch | c | chân → c ə n NGANG |
| d | z | da → z a NGANG |
| **đ** | **ɗ** | đi → ɗ i NGANG (ID riêng, khác d→z — đối lập d/đ vào required_contrasts) |
| gi + vần nguyên âm | ʝ | gia → ʝ a NGANG |
| gi + vần bắt đầu bằng i ("gì/gìn/giêng") | [B] | mặc định ʝ i; đọc thật Hanoi /zi/ — chốt bằng gold + dialect policy; `source_graphemes` giữ "gi" để adapter tái hiện nếu cần |
| g, gh | ɣ | ga / ghi |
| h | h | hoa → h w a NGANG |
| kh | x | khê → x e NGANG |
| l, m, n | l, m, n | la, ma, na |
| nh | ɲ | nhã |
| ng, ngh | ŋ | nga, nghe |
| ph | f | pha |
| p (hiếm: "pơ") | p | từ điển ngoại lệ |
| qu | k + glide w | qua → k w a NGANG |
| r | ʐ | ra |
| s | ʂ | sa |
| t | t | ta |
| th | tʰ (1 token) | tha |
| tr | ʈʂ (1 token) | tra |
| v | v | va |
| x | s | xa |
| ∅ | — | ăn, yến |

Longest-match 3→1. **7.4**: mặc định tách bạch; gộp kiểu đời thường = sửa bảng config
(nhiều dòng, không phải 4 — vì đụng gold/adapter); lý do chọn tách: **thiên lệch về phía
tách** — nhãn tách cho 2 âm giống nhau chỉ tốn chút dữ liệu, nhãn gộp cho 2 âm khác nhau làm
hỏng model. Chốt cuối theo audio train tầng 3.

#### 4.6.3. Glide — parser theo MẪU vần có điều kiện, không chuỗi bước tham lam **[B]**

Vần = (G) + (N) + (C) với G ∈ {∅, w}: **w chỉ được viết bằng o/u ĐỨNG TRƯỚC nguyên âm khác**;
j/y và o/u đứng SAU vần là âm cuối. Mẫu ưu tiên longest-match của CẢ cụm vần (VD "uyên" =
w+iə+n khớp nguyên cụm trước khi thử "u"+"ên"). Phân tích chuẩn: `mùa` = m + **uə** (KHÔNG glide w); `cửa` = k + **ɨə** — cặp w+a chỉ là
`qua/hoa`. Ca xung đột bắt buộc vào đối chứng: `yến/yêu` vs `ến/uyên` · `khuya` (w+ia) vs
`quyện` (w+iə+n) · `qua/hoa` (w+a) vs `mùa/mua` (uə).

#### 4.6.4. Vần chính (nucleus) **[B]**

| Chính tả | ID/hiển thị | Ghi chú |
|---|---|---|
| a | PHONE_A = aː (dài) | **tách khỏi ă — đối lập bắt buộc** (tam/tăm) |
| ă | PHONE_A_SHORT = a | ngắn |
| â | ə | ngắn |
| ơ | əː (1 token) | dài |
| e / ê | ɛ / e | |
| i, y | i | cùng 1 ID (không đối lập) |
| o / ô / u / ư | ɔ / o / u / ɨ | |
| iê/ia/ya | iə (1 token) | |
| ươ/ưa | ɨə (1 token) | |
| uô/ua | uə (1 token) | không cần glide riêng (mùa, mua, lúa) |
| uy | w+i | glide + nucleus |
| Bảng đủ ~55 vần: fase B sinh tổ hợp + duyệt + khóa | | |

#### 4.6.5. Âm cuối (coda) **[B]**

| Chính tả | IPA | Ví dụ |
|---|---|---|
| ∅ | — | ma |
| -i/-y | j | mai → m a j · hồi |
| -o/-u | w | cao → k a w · khâu |
| -m / -n | m / n | năm, nền |
| -nh | ɲ | anh? **[B]** — "anh/ênh/inh" có đọc thật Hanoi kiểu glide (aɪŋ/ɛɲ) — chốt bằng gold; mặc định bảng: a+ɲ |
| -ng | ŋ | tang |
| -c/-ch | k (cùng ID) | mác, mách |
| **-p/-t** | p / t — **thuộc LÕI** (hộp, đẹp, một, hát — không phải "mượn") | |

**Ràng buộc coda tắc × thanh (luật lõi chuẩn)**: coda {p,t,c,ch} × tone ∈ {TONE_SAC,
TONE_NANG} (học, hộc, hót, lột). Cấm ngã/ngang/huyền; **hỏi+tắc ("hóc", "lỏch") không thuộc
lõi chuẩn phát thanh** — xử lý bằng `exceptions_vi.tsv` (policy ngoại lệ), KHÔNG mở luật lõi.
Phân biệt 2 bộ lọc: (1) hợp lệ cấu trúc âm tiết; (2) có trong từ vựng/ứng viên chấp nhận —
không dùng (1) để tuyên bố (2). Kiểm ở E2-B; bộ lọc fold dùng CẢ HAI (hoc → học/hộc/hốc).

#### 4.6.6. Thuật toán tách (pseudo-code)

```
parse_syllable(word):
    (base, tone_name) = strip_tone_marks(word)     # bỏ dấu thanh, giữ ăâêôơưđ
    onset = longest_match(ONSETS, base)            # 4.6.2
    nếu onset == "qu": glide w ngầm; remainder = phần sau "qu"
    rhyme = match_rhyme(remainder)                 # mẫu (G)+N+(C) 4.6.3-4.6.5, longest cụm
    kiểm ràng buộc coda tắc × thanh (4.6.5)
    nếu không khớp hết → KHÔNG hợp lệ nguyên dạng → state machine 4.6.7
    return record {onset, glide, nucleus, coda, tone, source_graphemes}
```
Tính đúng: (a) mọi tổ hợp sinh từ bảng parse trọn (script fase B); (b) bảng `required_contrasts`
phân biệt được; (c) 100% corpus parse hoặc rơi fallback có provenance (E2).

#### 4.6.7. STATE MACHINE fallback (duy nhất, thứ tự cố định, không vòng lặp)

```
parse trọn (vi_rules) → [thất bại] exceptions_vi.tsv → [không có] fold nhóm (b) (4.8)
    → [không ứng viên] SPELL (4.7.5) — kết thúc
```
Trạng thái đơn vị đọc: `ok | fallback | silent | contract_error`.
Token rỗng → `contract_error` (không spell được). Nhánh "đọc latin kiểu vi" **BỎ khỏi v1**
(đã từng là nhánh không định nghĩa — thay bằng spell).

---

### 4.7. NHÁNH TIẾNG ANH

#### 4.7.1. Chính sách phát âm

- **Giọng đích: General American (US)** — nhất quán CMUdict (xấp xỉ phát âm, có biến thể).
- **Rhotic**: giữ ɹ/ɚ. **Stress**: primary + secondary từ CMUdict; không tự reduce thêm.
- **Nhiều biến thể CMUdict** (read/lead): chọn **biến thể mặc định theo thứ tự file** (không
  gọi là "phổ biến nhất" — chưa có thống kê); cờ `homograph_risk`; báo cáo riêng E2/E3.
  Nâng cấp sau: bảng ưu tiên top-N từ đồng tự.

#### 4.7.2. ARPAbet → master (đủ 39, CÓ stress digit) **[B]**

AA→ɑ · AE→æ · **AH0→ə, AH1/AH2→ʌ** · AO→ɔ · AW→aʊ · AY→aɪ · EH→ɛ · **ER0→ɚ · ER1/ER2→ɝ (kèm STRESS token)** ·
EY→eɪ · IH→ɪ · IY→i · OW→oʊ · OY→ɔɪ · UH→ʊ · UW→u · B b · CH tʃ · D d · DH ð · F f · G ɡ ·
HH h · JH dʒ · K k · L l · M m · N n · NG ŋ · P p · R ɹ · S s · SH ʃ · T t · TH θ · V v ·
W w · Y j · Z z · ZH ʒ · `1`→STRESS_PRIMARY · `2`→STRESS_SECONDARY.
Nguyên âm đôi/triphthong = 1 token. **Stress gắn vào NUCLEUS mang dấu** (không cần syllabifier
đầy đủ ở v1; record giữ cấu trúc syllable để adapter quyết cách serialize).

#### 4.7.3. Morphological variant = CANDIDATE GENERATOR, không phải phát âm hoàn chỉnh

```
exceptions_en (override, TRƯỚC lookup) → CMU exact
    → morphological: tìm root (bỏ -s/-es/-ed/-ing/-ly bằng luật CÓ ĐIỀU KIỆN ĐỦ:
      /s,z,ɪz/ của -s; /t,d,ɪd/ của -ed; phục hồi e; gấp đôi phụ âm; đổi y→i)
      + phát âm hậu tố TÁI DỰNG + validate → dùng
    → en_rules (4.7.4) → spell
```
Cấm: strip suffix rồi lấy nguyên pronunciation root làm output (mất âm hậu tố: asked, cats,
wanted, running). Hình thái ngoài bộ luật → đánh dấu chưa hỗ trợ → spell.
`en_rules` là **đặc tả còn mở** — hoàn tất fase C; state machine 4.7.4 chỉ là bộ kiểm thất
bại, không phải thuật toán G2P.

#### 4.7.4. Khi nào "không chắc" → spell (bộ kiểm thất bại hình thức, không phải thước đo đúng)

Cụm phụ âm không hợp lệ / token toàn phụ âm / ký tự lạ / dài >20 → spell + `fallback_reason`.
(Chứng minh: đầu ra "có vẻ hợp cấu trúc" ≠ đọc đúng từ — chất lượng do gold đo.)

#### 4.7.5. Spell: bảng tên chữ cái en (A→eɪ…) + vi (a, bê, xê, đê…) **[B]** chốt fase B.

---

### 4.8. FOLD KHÔNG DẤU — chính sách bảo toàn

#### 4.8.1. Phân loại 3 nhóm (A0 = SƠ BỘ, chạy lại sau B khi parser chuẩn)

| Nhóm | Định nghĩa | Chính sách |
|---|---|---|
| **(a) hợp lệ nguyên dạng** | parse trọn theo 4.6 | đọc nguyên dạng, **KHÔNG đụng** — cấm biến "cho"→"chó", "roi"→"rồi" |
| **(b) chỉ hợp lệ khi thêm dấu** | không parse nguyên dạng, ≥1 ứng viên có dấu hợp lệ | fold theo prior; lưu mọi ứng viên + tỉ lệ |
| **(c) không phải âm tiết vi** | không ứng viên hợp lệ | state machine 4.6.7 (→ spell); **đếm giao CMUdict = nghi lỗi route, xuất danh sách báo tầng 1** |

Số A0 sơ bộ (validator vỏ) — quét đủ **1.000.000 câu**: ASCII route-vi **101.308 unique /
2.865.586 lần** → **(a) 1.060 / 2.065.684 (72% lần gặp)** · **(b) 653 / 26.343 (0,9%)** ·
**(c) 99.595 / 773.559 (27%)** — 634k lần viết hoa (**đặc trưng chữ viết, chưa phải nhãn
"tên riêng"**). Shadow: từ (a) có ứng viên có dấu cùng fold_key tần suất cao hơn — tổng
**788.252 lần ≈ 4,8% của 16.563.317 word tokens route-vi** (mẫu số ghi rõ; 2,87M ASCII là
14,7% route-vi — phần lớn từ vốn không dấu chuẩn: ba, hai, thu, nam…). Mỗi cột tách bạch:
surface_freq(ASCII) vs candidate_freq(có dấu, corpus build) — top: co 1,1k/có 285,8k ·
va 824/và 227,9k · cua 733/của 224,7k · la 3,6k/là 195,3k · khong 150/không 133,3k.
**788k là CẬN TRÊN "số lần có nguy cơ đa nghĩa theo prior", KHÔNG phải số lỗi của chính sách
bảo toàn**. A0-ext đã đo phân tầng theo câu: **777.101/788.252 lần bóng nằm trong câu CÓ từ
có dấu** (đa nghĩa theo prior — "nam" có thể đúng là "nam") và chỉ **11.151 lần trong câu
toàn ASCII** (văn mất dấu thật — nguy cơ cao). Vẫn là phân tầng nguy cơ, CHƯA phải nhãn
đúng/sai (vd "con" 37k lần trong câu có dấu nhưng đa số thật sự là "con") — nhãn thật dùng
cách strip dấu câu có dấu → so với gốc (việc của A4/fase B, tách khỏi corpus đếm tần suất). **Policy nhóm (c) viết hoa = quyết định [B] của chủ dự án**
(en-rules có kiểm soát / đọc-vi-luật-chặt / spell — chốt bằng nghe thử gold-dev); (b)∩CMUdict
= danh sách nghi vấn, không tự đổi route. Chi tiết: `02_data/fold/`. Số CUỐI chạy lại sau
fase B. A0 không dùng để khóa đầu tư.

#### 4.8.2. Từ điển fold (nhóm b) — metadata + bất biến

```text
surface   candidate   global_freq   ambiguous   chosen_by
truong    trường      12345         1           freq_prior
nguoi     người       9000          3           freq_prior
nguoi     nguội       1200          3           freq_prior
nguoi     ngươi       300           3           freq_prior
```

- **Bất biến ứng viên: `fold_key(candidate) == fold_key(surface)`**, với fold_key = NFC →
  lowercase → đ→d → bỏ dấu thanh → ă→a â→a ê→e ô→o ơ→o ư→u. (Bắt được lỗi "nguoi→ngôi"
  vì fold_key("ngôi")="ngoi" ≠ "nguoi".)
- Tần suất **chỉ đếm từ token CÓ DẤU** (tránh tự tham chiếu).
- Đánh giá trên **gold tách riêng**, không phải corpus dựng bảng.
- Chạy corpus ghi `uncertain_folds.log`: top1-top2 chênh <20% — nguyên liệu tiny model sau.

#### 4.8.3. Nâng cấp v1.5 (sau khi có số đo): n-gram + Viterbi trên ứng viên — gồm cả **cờ
cấp câu** (câu nhiều token nhóm (b) liên tiếp = tín hiệu "văn không dấu"). Ghi rõ: chế độ
**khôi phục văn bản mất dấu riêng, chỉ kích hoạt khi được ủy quyền**; KHÔNG thuộc cam kết
bảo toàn v1.

**Đo lường trung thực**: "tỉ lệ **rewrite nhóm (a)** = 0 theo thiết kế". Chất lượng phân
nhóm (parser có loại nhầm đúng→sai?) và chất lượng phát âm = đo riêng trên gold. "Hỏng từ
vốn đúng = 0" tuyệt đối là khẳng định quá rộng — không dùng.

---

### 4.9. PROFILE `kokoro178` — adapter nhận thức cấu trúc

Nhận record âm tiết có cấu trúc (onset/glide/nucleus/coda/tone), thực hiện **transform**:

1. Segment map: ɓ→b · ɗ→d · ʐ→ʒ · tʰ→θ · ɨ→[V] ɨ hoặc ɯ · əː→ə+ː · PHONE_AU→a+ʊ ·
   token còn lại gần giữ. **Các cặp bị gộp khai báo tường minh trong `loss_report`** (kokoro178
   là export MẤT THÔNG TIN có chủ đích — ɓ/ɗ, ʐ/ʒ, tʰ/θ trùng âm en).
2. Tone transform: TONE_* → mũi tên chèn **TRƯỚC âm cuối**; ngã/nặng thêm `ʔ` — transformation,
   không phải rename (bảng 4.6.1, chờ [V]).
3. Chèn ˈ trước nucleus chính.
4. Cleanup theo frontend. 5. Serialize → kiểm **từng ký tự thuộc 114 mục** (n_token 178).

**Ba bất biến thay round-trip** (round-trip qua export lossy là bất khả thi — bỏ):

```text
I1 master serialization round-trip : master record → canonical encoding → master record (giữ trọn)
I2 profile determinism + conformance: cùng master + cùng profile version → cùng chuỗi;
   conformance = output đúng spec profile (mọi ký tự thuộc vocab, tone đúng vị trí)
I3-MASTER : mọi cặp required_contrasts phân biệt được trong ham/0.1 (audit điều 6)
I3-PROFILE: chỉ các cặp trong profile_required_contrasts (mỗi profile khai báo riêng)
   bắt buộc còn phân biệt sau transform; master contrast bị gộp phải nằm trong loss_report
   (kokoro178 documented loss: tʰ=θ, ʐ=ʒ, ɓ=b, ɗ=d)
```
Traceability qua **sidecar** `source_master_id` theo từng đơn vị — không yêu cầu inverse.

**4.9.3. Xác minh [V] — thứ tự đúng (rẻ trước, đắt sau)**:
1. **So CHUỖI trước**: chạy frontend gốc (vig2p + adapter, pin revision) trên toàn bộ âm tiết
   hợp lệ → diff với profile của mình → diff gom nhóm. Rẻ, không cần audio, chỉ ra ngay chỗ
   checkpoint bị đưa ra ngoài phân phối train.
2. ID thực tế đưa vào model (inspect token ids).
3. Nghe `ma/mà/má/mả/mã/mạ` + cặp tối tiểu — **bằng chứng debug bổ sung, không phải oracle**.
   Nếu checkpoint cho thấy bảng digit đã học đảo chỗ → kết luận là "chưa xác minh được
   adapter cho đối lập này", KHÔNG ép đổi master theo checkpoint (master theo gold).

**E6 nghe thử A/B**: (i) vig2p→checkpoint vs (ii) mình→profile→checkpoint — khoanh vùng;
cả hai có thể cùng dính lỗi checkpoint.

---

### 4.10. SCHEMA ĐẦU RA `g2p/0.1`

```json
{
  "schema": "g2p/0.1",
  "inventory": "ham/0.1", "inventory_hash": "sha256:…",
  "dialect": "vi_chinh_ta", "profile": "kokoro178",
  "text": "Doanh thu Q3 tăng 12.5%",
  "tokens": [
    {"i": 0, "surface": "Doanh", "route": "vi",
     "units": [{"read_unit_index": 0, "verbal": "Doanh",
                "phonemes": ["PHONE_Z", "PHONE_W", "PHONE_A", "PHONE_NH"],
                "tone": "TONE_NGANG", "master_token_span": [0, 5],
                "source": "vi_rules", "fallback_reason": null}],
     "break": null, "intonation": null}
  ],
  "coverage": {"ok": true, "by_source": {"vi_rules": 8, "cmudict": 2, "exceptions": 0,
               "fold": 0, "spell": 0}, "contract_errors": []},
  "warnings": []
}
```

- `master_token_span [start,end)` = index trong **master token stream chuẩn**, phủ TẤT CẢ
  token đơn vị phát ra gồm segment + prosody (Doanh = 4 segment + TONE_NGANG = [0,5));
  không phải offset ký tự; `profile_char_span` tùy chọn thuộc export.
- Traceability: `source_token_id` (chính là `i`) + `read_unit_index` + `syllable_index` (trong
  record). Khi WAV sai: token nào → nhánh nào → luật nào → profile nào.
- Trạng thái đơn vị: `ok | fallback | silent | contract_error` (4.6.7); E2 yêu cầu phoneme
  không rỗng cho **đơn vị có phát âm** — punct là `silent`, token rỗng là `contract_error`.
- **`tone` field là nguồn, stream sinh từ field** (một hướng).

**Break — bảng tổng hợp (chốt fase A, khóa đối chứng)**:

| Tình huống tại ranh giới | Kết quả |
|---|---|
| chỉ token TRƯỚC có break | dùng break đó |
| chỉ token punct SAU có break | dùng break đó |
| cả hai cùng giá trị | 1 break (không nhân đôi) |
| hai giá trị xung đột (break của token trước ≠ break của punct) | **contract_error** (đẩy tầng 1) |
| chuỗi nhiều dấu câu liên tiếp (vd `,.`, `.)`) | 1 break theo thứ tự mạnh `… — ! ? . ; : ,`; còn lại silent — không phải contract_error |

Serialize: break + intonation + loại dấu → PUNCT_PERIOD / PUNCT_QUESTION / PUNCT_EXCLAIM /
PUNCT_COMMA / … (major+rising→question; major+cảm thán→exclaim; còn lại theo loại dấu).

**4.10.1. Nguồn sự thật**: chuỗi dựng từ `tokens[]`; khác `read_string` qua canonical
renderer = `contract_error` (3.4). Case-folding nội bộ cho tra từ điển, không đổi dữ liệu.
**4.10.2. Break là sự kiện ranh giới** — mỗi ranh giới đúng 1 lần, không tự sinh pause mới.
**4.10.3. Biệt lệ được cấp phép**: spell en-OOV; fold nhóm (b) — có `fallback_reason`.

---

### 4.11. ĐỐI CHỨNG, GOLD & PHÂN TÁCH DỮ LIỆU

#### 4.11.1. Phân tách

```text
build    : tần suất fold, sinh tổ hợp
dev      : chọn luật/chính sách (cặp tối tiểu, nhóm khó)
gold-dev : mở — khảo sát baseline, CHỐT NGƯỠNG, lặp sửa luật
gold-test: NIÊM PHONG — chạy 1 lần mỗi bản phát hành để nghiệm thu (không chọn gì trên đó)
regression: đối chứng khóa (anti-tái diễn) + corpus 1,2M (stress/integrity)
```
Đối chứng lập trình viên xem thường xuyên = **regression**, không gọi held-out. Khi lấy ca
gold-test thất bại để sửa luật → ghi nhận tái sử dụng, duy trì tập độc lập mới. Nhãn gold
do NGƯỜI viết TRƯỚC khi xem output hệ (ít nhất cho nhóm fold/homograph, kèm ngữ cảnh câu).
Báo cáo gold luôn kèm **số mẫu từng nhóm** (vi/en/mix × thanh/âm đoạn/trọng âm/spell/fold).

#### 4.11.2. Gold set

- 300–1.000 đơn vị đọc, người nghe kiểm tay (tư vấn: Wiktionary IPA Hà Nội, vPhon hanoi —
  KHÔNG phải đáp án).
- Phủ bắt buộc: 6 thanh (ma/mà/má/mả/mã/mạ) · tam/tăm (a/ă) · tr/ch · s/x · d/gi/r (kèm
  gì/dì) · n/ng · c/t · gi/ghi/quy · ươ/ươi/uya · iê/uô · -nh/-ng · -p/-t coda tắc × sắc/nặng ·
  không dấu đa nghĩa (a)+(b) CÓ NGỮ CẢNH · en: stress, diphthong, homograph-risk, OOV-luật,
  hình thái, spell.
- **Kỳ vọng theo capability contract của version** (không chấm v1 bằng khả năng v1.5):
  expected_v1 nhóm (a) = **preserve nguyên dạng + thanh ngang**; nhóm (b) = **ứng viên fold
  được chọn**; FUTURE_CONTEXT_GOLD (khôi phục theo ngữ cảnh) tách riêng — chỉ nghiệm thu v1.5+.
- Đo: lỗi âm đoạn / lỗi thanh / lỗi trọng âm / exact-match. **Ngưỡng chốt trên gold-dev SAU
  baseline, TRƯỚC tối ưu; nghiệm thu trên gold-test.**

#### 4.11.3. Đối chứng khóa (~300 ca, 2 cột master + kokoro178): tổ hợp sinh từ bảng + từ
thật + ~30 cặp tối tiểu (sa/xa, sông/xông, gia/da/ra, tam/tăm, thu/thù, được/dứt…).

---

### 4.12. VÍ DỤ END-TO-END — **BẢNG MINH HỌA, CHƯA KIỂM BỞI CODE** (sẽ thay bằng render từ fixture duyệt)

Hiển thị: `aː` = PHONE_A (dài — chữ "a"); `a` = PHONE_A_SHORT (ngắn — chữ "ă"); chất lượng
nucleus do mẫu vần quyết: ba/hai = aː, tăng/năm/trăm = a ngắn, anh/oanh = ă+j+ŋ **[B]**.

**Câu 1 (vi)** — `"Doanh thu quý ba tăng mười hai phẩy năm phần trăm."`

| Từ | Thanh | Âm đầu | Glide | Vần | Âm cuối | Master (hiển thị) |
|---|---|---|---|---|---|---|
| Doanh | ngang | d→z | o→w | a(ngắn) | anh=ă+j+ŋ **[B]** | z w a j ŋ 1 |
| thu | ngang | th→tʰ | — | u | — | tʰ u 1 |
| quý | **sắc** | qu→k | w | y→i | — | k w i 3 |
| ba | ngang | b→ɓ | — | aː | — | ɓ aː 1 |
| tăng | ngang | t | — | a | ng→ŋ | t a ŋ 1 |
| mười | huyền | m | — | ươi→ɨə | i→j | m ɨə j 2 |
| hai | ngang | h | — | aː | i→j | h aː j 1 |
| phẩy | **hỏi** | ph→f | — | â→ə | y→j | f ə j 4 |
| năm | ngang | n | — | a | m | n a m 1 |
| phần | **huyền** | ph→f | — | â→ə | n | f ə n 2 |
| trăm | ngang | tr→ʈʂ | — | a | m | ʈʂ a m 1 |

**Câu 2 (mix)** — `"anh dùng Chrome trên Mac."`: anh → a j ŋ 1 **[B]** (ăjŋ) · dùng → z u ŋ 2 ·
Chrome → ˈk ɹ oʊ m (cmudict, STRESS_PRIMARY trên OW) · **trên → ʈʂ e n 1** (ê→e, coda n) ·
Mac → m æ k.

**Câu 3 (không dấu — giới hạn chính sách được nói THẲNG)** — `"ban vao deadline roi"`:
`ban`, `vao`, `roi` đều parse trọn → **nhóm (a), đọc nguyên dạng thanh ngang**: ɓ aː n 1 ·
v aː w 1 (vần ao = dài) · **ʐ ɔ j 1** (o không dấu = ɔ; "rồi" mới là ʐ o j 2) ·
deadline → ˈd ɛ d l aɪ n (cmudict, EH1 + AY2). Hệ v1 **không khôi phục** "bạn/vào/đã/rồi"
— trade-off chủ đích (không sửa nhầm > khôi phục đúng). Tín hiệu "cả câu văn không dấu" là
cờ cấp câu cho v1.5 (4.8.3), không phải v1.

### 4.13. Collision-audit — 6 điều, 4.2.

---

## 5. KẾ HOẠCH THỰC HIỆN

| Fase | Bước con | Trạng thái |
|---|---|---|
| **A** | A0 phân loại 3 nhóm (**SƠ BỘ** — validator vỏ; số cuối sau B) · A1 inventory + schema + audit 6 điều · A2 curl 2 config.json (114 mục) + pin + SHA256 · A3 profiles.py + test_coda_tone_mapper + **so chuỗi vig2p toàn âm tiết [V]** · A4 fold nhóm (b) + uncertain log | **A0 đã chạy**; A1+ chờ phê duyệt |
| **B** | B1 vi_syllable (record) · B2 vi_rules · B3 sinh tổ hợp + parse trọn · B4 spell vi · B5 gold-dev + ngưỡng · B6 (tùy chọn) n-gram fold | chờ |
| **C** | C1 CMUdict 0.7b (SHA256) · C2 en_lexicon · C3 en_rules + kiểm thất bại · C4 coverage 37.689 (A0 quét đầy đủ sẽ cho con số tốt hơn) · C5 giao nhóm (c)∩CMU → báo tầng 1 | chờ |
| **D** | D1 g2p.py (g2p/0.1 + canonical renderer) · D2 spell.py · D3 emit_vocab_config · D4 demo | chờ |
| **E** | 6 gate mục 8 | chờ |
| **F** | G2P_03 + README ×2 + báo cáo | chờ |

---

## 6. TÀI NGUYÊN

- **Trong máy**: corpus 1M (structure `rec["ir"]["tokens"]`) + supplement; G2P_01 data
  (top-300/500 của mẫu 200k — A0 quét lại đầy đủ); đối chứng tầng 1; duyet_v8.
- **Tải thêm (pin + SHA256)**: CMUdict 0.7b file raw; config.json ×2; vig2p/vPhon (đối chiếu;
  Py3.12 hỏng → môi trường riêng xuất kết quả tĩnh, KHÔNG hạ gate).
- **Phần cứng**: RTX 3080 12GB; `05_TTS/venv` Py3.12; venv vLLM cho 9B; checkpoint contextboxai
  chỉ dùng debug.
- **Con người**: agent làm; chủ dự án duyệt (đặc tả này, gold-dev ngưỡng, top fold đa nghĩa,
  spell, E4/E6); reviewer ngoài phản hồi 4.2/4.6/4.8/4.9/4.10, 7, 8.

---

## 7. NỢ KỸ THUẬT CÓ KIỂM SOÁT

| # | Nợ | Gate/số đo | Dự kiến đóng |
|---|---|---|---|
| 1 | Fold nhóm (b) chọn sai | A0 sơ bộ → số cuối sau B; gold đo tỉ lệ chọn sai; **rewrite nhóm (a) = 0 theo thiết kế** (chất lượng phân nhóm đo riêng) | tiny model khôi phục dấu (ăn uncertain log) |
| 2 | CMUdict coverage + tên riêng lạ | C4 báo %từ/%lần gặp + homograph-risk | tiny model en-OOV |
| 3 | Xung đột symbol vi∩en | audit 6 điều + required_contrasts (tự động) | mô hình hóa xong; tính đúng do gold |
| 4 | Chuỗi vào còn HOA/`- / "` | renderer phát hiện lệch; **A0-ext đã đo: 24.380/16.563.317 word tokens (0,15%) có ký tự đặc biệt trong `verbal`** — top: `.` 8,3k · digits ~19k · `-` 3,2k · `,` 2,7k · `&` 2k · `²` 1,8k | policy ngắn chốt fase A (map/bỏ/contract_error) |
| 5 | vig2p Py3.12 | môi trường riêng + kết quả tĩnh | — |

7.2. "0 exception" corpus = 0 crash kỹ thuật ≠ 0 lỗi ngôn ngữ (gold/judge đo chất lượng).
7.3. 867 cần xử lý tầng 1: ảnh hưởng tầng 2 giới hạn (route đã chốt); triage song song.
7.4. `VI_DIALECT = vi_chinh_ta` **[B]** — nếu audio train sau không phân biệt tr/ch, s/x →
sửa bảng config + chạy lại E3/gold. Chi phí không chỉ "4 dòng": đụng gold + adapter + data
tiền xử lý — được ghi nhận từ đầu.

---

## 8. TIÊU CHÍ THÀNH CÔNG (6 gate)

| Gate | Kiểm tra |
|---|---|
| **E1 — cấu trúc & hợp đồng** | unit + đối chứng khóa + token alignment (span khớp stream) + **3 bất biến I1-I3 (4.9)** + OOD/torture (token 100×"A", "TRTRTR", token rỗng → trạng thái đúng, không crash, không cạn RAM) |
| **E2 — corpus 1,2M (2 lớp)** | **E2-A toàn vẹn**: 100% câu, 0 crash, **mọi đơn vị `ok`/`fallback` xác định có phát âm đều có phoneme hợp lệ không rỗng**, 0 ký tự ngoài vocab 114, contract_errors được đếm/không im lặng, deterministic, **tỉ lệ spell trên token word có ngưỡng báo cáo (tách viết hoa/không)** · **E2-B hợp lệ âm vị**: output đúng grammar vi_syllable (tổ hợp hợp lệ + **coda tắc chỉ sắc/nặng**), tone gắn đúng 1 âm tiết, stress en trên nucleus, CONTROL không lọt stream segment · báo cáo tỉ lệ theo source × vi/en/mix |
| **E3 — gold** | gold-dev chốt ngưỡng sau baseline; gold-test nghiệm thu; đo lỗi âm đoạn/thanh/trọng âm/exact tách vi/en/mix; vig2p/vPhon = công cụ tìm bất đồng (diff gom nhóm, giải thích được), không oracle, không hard-gate % |
| **E4 — differential** | 9B + diff ngoài để phát hiện outlier/nhóm lỗi; người phân xử; judge không chấm phoneme |
| **E5 — tái lập & hiệu năng** | cùng code + data version (SHA256 CMUdict/fold/exceptions/inventory/profile) → byte-identical; throughput: **≥2.000 câu/phút/worker CPU** (ghi worker/RAM/cache) |
| **E6 — adapter & tai** | inspect token IDs; nghe A/B; WAV = **bằng chứng debug bổ sung, không phải oracle** |

---

## 9. RỦI RO & GIẢM THIỂU

| Rủi ro | Giảm thiểu |
|---|---|
| Fold chọn sai nhóm (b) | số đo, gold có ngữ cảnh, uncertain log, tiny model sau |
| Parser loại nhầm đúng→(b)/(c) | tổ hợp sinh (nhất quán nội bộ) + gold tuyển độc lập (độ đầy đủ) |
| Âm vị tách bạch lệch audio tương lai | config + 7.4 |
| Map thanh sang Kokoro sai chiều | theo tên thanh + so chuỗi toàn âm tiết [V] + test ma/mà/má/mả/mã/mạ |
| En OOV đọc ngớ ngẩn | state machine 4.7.4; spell có lý do |
| Homograph en | biến thể mặc định theo thứ tự file + cờ + báo cáo riêng |
| Hình thái en mất âm hậu tố | candidate generator + tái dựng hậu tố (4.7.3) |
| Rò rỉ test | phân tách 4.11.1; gold-test niêm phong |
| Judge 9B làm oracle | E3/E4 tách vai |
| Checkpoint debug quyết định master | 4.9.3: master theo gold; checkpoint chỉ đưa ra "chưa xác minh được" |

---

## 10. LINK THAM KHẢO (pin revision khi dùng — A2)

- Kokoro-Vietnamese: <https://github.com/iamdinhthuan/Kokoro-Vietnamese> · checkpoint:
  <https://huggingface.co/contextboxai/Kokoro-Vietnamese>
- Kokoro gốc: <https://github.com/hexgrad/kokoro> · <https://huggingface.co/hexgrad/Kokoro-82M>
- StyleTTS2: <https://github.com/yl4579/StyleTTS2> · kokoro-tts CLI: <https://github.com/nazdridoy/kokoro-tts> · misaki: <https://github.com/hexgrad/misaki>
- vig2p: <https://github.com/hoang1007/vig2p> · vPhon: <https://github.com/kirbyj/vPhon> · Viphoneme: <https://github.com/v-nhandt21/Viphoneme> · espeak-ng: <https://github.com/espeak-ng/espeak-ng>
- CMUdict 0.7b (file raw + SHA256): <https://github.com/cmusphinx/cmudict> · ghi chú xấp xỉ:
  <https://cmusphinx.github.io/2014/11/cmudict-0-7b-update/>
- IPA chart: <https://www.internationalphoneticassociation.org/IPAcharts/IPA_chart_2021.html> · âm vị học vi: <https://en.wikipedia.org/wiki/Vietnamese_phonology>
- Nội bộ: `G2P_00/01(+data)/02` cùng thư mục · báo cáo tầng 1: `01_tiny_model/00_docs/reports/2026-10-01_bao_cao_qua_dem.md`

---

## 11. TRẠNG THÁI & ARTIFACT

Đã có: docs + đặc tả bản 4 + **kết quả A0 sơ bộ** (`02_data/fold/`). Chưa có code G2P.
Cây thư mục như bản 3 + `02_data/fold/` (a0_ket_qua.json, a0_groups.tsv, a0_ambiguous_top.tsv).

---

## 12. RÀNG BUỘC AN TOÀN (bất biến)

1. Dữ liệu test không đem train (4.11.1). 2. Không copy model Qwen/Kokoro vào 06_models;
   không xóa `qwen3_5_9b_base`. 3. Không xóa/sửa dữ liệu ngoài `05_TTS/`. 4. Kill bằng PID.
   5. Gemma API bỏ (nếu dùng lại kèm UA curl/8.5.0). 6. Không đụng tầng 1 ngoài tiêu thụ IR
   (lệch hợp đồng → contract_errors). 7. Pin revision + checksum + giấy phép mọi dữ liệu
  /frontend đối chiếu.

---

## PHỤ LỤC A — NHẬT KÝ VÒNG 1 (bản 2 → 3)

28 điểm sửa theo phản biện vòng 1 (semantic token-ID; E2-A/B; gold độc lập; fold 3 nhóm;
EN policy; provenance; checksum; phân tách dữ liệu; sửa ví dụ "trường" sai; "178 symbol" →
114 mục/n_token 178; tokens[] là nguồn sự thật; sandhi KHÔNG LÀM; …) — chi tiết giữ trong
lịch sử phiên, các mục tương ứng đã có trong bản 4.

## PHỤ LỤC B — NHẬT KÝ VÒNG 2 (bản 3 → 4)

| # | Góp ý | Sửa ở |
|---|---|---|
| 1 | E1 round-trip qua profile lossy bất khả thi (ɓ→b, tʰ→θ trùng âm en) | 4.9: 3 bất biến I1-I3 + sidecar source_master_id; E1 đổi |
| 2 | EN morphology strip suffix lấy phát âm root là sai (asked/cats) | 4.7.3: candidate generator + tái dựng hậu tố có điều kiện |
| 3 | EN stress cần cấu trúc syllable trước serializer | 4.7.2: stress gắn nucleus; record syllable-structured cả vi lẫn en |
| 4 | Contract "khớp" chưa định nghĩa | 3.4 + 4.10.1: canonical renderer `render_tokens_to_read_string` |
| 5 | "Biến thể đầu = phổ biến nhất" không có bằng chứng | 4.7.1: "mặc định theo thứ tự file" |
| 6 | Boundary là metadata hay token? | 4.2: metadata; chỉ PUNCT_* là control token |
| 7 | VI_DIALECT giữ [B] | 4.4 + 7.4 (thêm lý do thiên lệch về phía tách) |
| 8 | Thiếu **đ** trong bảng onset | 4.6.2: đ→ɗ, ID riêng |
| 9 | "chân" thiếu âm cuối | 4.6.2: c ə n NGANG |
| 10 | trường dùng ʈ vs ʈʂ không nhất quán | 2.1 + 4.6.2: PHONE_TR = ʈʂ toàn văn |
| 11 | -p/-t ghi "mượn" là sai (hộp, đẹp, một, hát) | 4.6.5: thuộc lõi + luật coda tắc × thanh |
| 12 | "phẩy" ghi sắc | 4.12: hỏi (4) |
| 13 | "phần" ghi ngang | 4.12: huyền (2) |
| 14 | "trên → ʈʂ əː j" sai | 4.12: ʈʂ e n 1 |
| 15 | "anh → ɑ ŋ" lệch -nh→ɲ | 4.12: ɑ ɲ 1 [B] (ghi ca đặc biệt anh/ênh/inh) |
| 16 | "roi/vao" xếp nhóm (b) trái chính sách | 4.12 câu 3: nhóm (a), đọc nguyên dạng, nói thẳng giới hạn + cờ cấp câu v1.5 |
| 17 | "nguoi→ngôi" trái fold_key | 4.8.2: bất biến fold_key; ví dụ người/nguội/ngươi |
| 18 | "ngã/hỏi thêm ʔ" mâu thuẫn bảng | 4.5.3/4.9.2: ngã/nặng mang ʔ; hỏi = ↓; nhất quán + [V] |
| 19 | AH0→ʌ sai (AH0 = schwa) | 4.7.2: AH0→ə; ER mọi stress→ɚ |
| 20 | JSON `[PHONE_Z,…]` không hợp lệ; span [0,9] mập mờ | 4.10: ID dạng chuỗi; master_token_span [start,end) index stream |
| 21 | "gì → z i" mâu thuẫn gi→ʝ + audit d/gi/r | 4.6.2: gì → ʝ i [B] theo dialect policy; source_graphemes giữ "gi"; gold chốt |
| 22 | a/ă gộp mất đối lập (tam/tăm) | 4.6.4: 2 ID PHONE_A/PHONE_A_SHORT; required_contrasts thêm nguyên âm |
| 23 | Glide 2 quy tắc tham lan mâu thuẫn vần đôi | 4.6.3: parser mẫu có điều kiện, longest cụm vần; ca xung đột vào đối chứng |
| 24 | Xác minh checkpoint: "so mel" không đủ; nghe có thể quy lỗi giọng | 4.9.3: thứ tự đúng — so chuỗi toàn âm tiết trước → inspect IDs → nghe (bằng chứng bổ sung) |
| 25 | spell áp surface hay verbal? | 3.2: verbal≠surface → đọc verbal như word; rỗng/bằng → spell surface |
| 26 | Nhóm (c) có thể là từ en gán nhầm route | 4.8.1 (c) + C5: đếm giao CMUdict, danh sách báo tầng 1 |
| 27 | Coda tắc × thanh là ràng buộc miễn phí | 4.6.5 + E2-B + bộ lọc fold |
| 28 | gold-dev/gold-test; ngưỡng không chọn trên test | 4.11.1/4.11.2 |
| 29 | A0 phụ thuộc parser B | 4.8.1: A0 = sơ bộ, số cuối sau B |
| 30 | fallback nhiều luồng (fallback_latin không định nghĩa) | 4.6.7: một state machine; bỏ fallback_latin |
| 31 | "hỏng từ vốn đúng = 0" quá rộng | 4.8.3: "rewrite nhóm (a) = 0 theo thiết kế"; chất lượng phân nhóm đo riêng |
| 32 | Viterbi v1.5 đảo chính sách bảo toàn | 4.8.3: chế độ riêng, chỉ khi được ủy quyền |
| 33 | Token rỗng không spell được; trạng thái thiếu | 4.6.7 + 4.10: ok/fallback/silent/contract_error |
| 34 | Break chưa có bảng tổng hợp; major không tự chọn dấu | 4.10: bảng tổng hợp + map theo loại dấu/intonation |
| 35 | Tone 2 nơi sự thật | 4.2/4.10: field là nguồn, stream sinh từ field |
| 36 | Collision-audit: cùng ID mới cùng embedding | 4.2: intent_shared chỉ là ghi chú |
| 37 | Kiểm parser bằng bảng chỉ là nhất quán nội bộ | 4.11.2 + risk: gold tuyển độc lập |
| 38 | Lỗi gõ: khớt, khudi, Alone, "lựa anything", xấp xĩ, tách bặt, "SPACE? không dùng" | đã sửa toàn văn ("tách bạch") |

---

## PHỤ LỤC C — NHẬT KÝ VÒNG 3 (bản 4 → 5)

| # | Góp ý | Sửa ở |
|---|---|---|
| 1 | Luật hỏi+tắc sai — lõi chuẩn chỉ sắc/nặng; lỏch/hóc → exceptions | 4.6.5 + A0 script |
| 2 | I3 mâu thuẫn profile lossy | 4.9: I3-MASTER / I3-PROFILE + loss_report |
| 3 | tai/tay, cao/cau, mác/mách gộp chuỗi | 4.2: đối lập mức chuỗi + mẫu vần có điều kiện + audit điều 7 (đơn ánh) |
| 4 | mùa = uə không phải w+a; bỏ điều kiện "sau w" | 4.6.3, 4.6.4 |
| 5 | Display lệch inventory (ba/hai aː, roi ɔ, anh ăjŋ, stress thiếu) | 4.12 + ghi chú hiển thị |
| 6 | Ví dụ viết tay tiếp tục sai → đánh dấu "minh họa chưa kiểm" | 4.12 + quy ước đầu tài liệu |
| 7 | ER mọi stress bỏ mất ɚ/ɝ | 4.7.2: ER0→ɚ, ER1/2→ɝ |
| 8 | required_contrasts thiếu d/đ | 4.2 |
| 9 | Gold chấm v1 bằng capability v1.5 | 4.11.2: expected_v1 theo nhóm + FUTURE_CONTEXT_GOLD |
| 10 | Shadow diễn giải quá mức; top ≠ tổng; mẫu số mập mờ | 4.8.1: cột tách bạch, mẫu số ghi rõ, CẬN TRÊN, đo theo câu + nhãn strip-dấu (A0-ext) |
| 11 | (b) toàn từ nghi en (cup/top/hot) | 4.8.1: (b)∩CMUdict danh sách nghi vấn |
| 12 | (c) viết hoa 634k lần → spell mọi thứ | policy [B] của chủ dự án + E2-A ngưỡng spell-rate |
| 13 | "có viết hoa" ≠ "tên riêng" | 4.8.1: ghi là đặc trưng chữ viết |
| 14 | Thứ tự exceptions_en/CMU mâu thuẫn | 4.7.3: exceptions trước |
| 15 | en_rules chưa đặc tả | 4.7.3: "đặc tả còn mở, fase C" |
| 16 | E2-A bỏ lọt ok-rỗng | E2-A |
| 17 | span chưa rõ prosody; [0,4) sai | 4.10: [0,5) + định nghĩa phủ prosody |
| 18 | break hàng xung đột/chuỗi dấu chồng nhau | 4.10: tách hai tình huống |
| 19 | vi_bac_tach gây hiểu nhầm | 4.4/7.4/schema: `vi_chinh_ta` |
| 20 | Nợ #4 đóng sớm | 7.1: A0-ext histogram verbal |
| 21 | Chống tự xác nhận ví dụ/snapshot | quy ước đầu tài liệu |

---

*Hết tài liệu. Các ô [B]/[V] + mục 4.2/4.8/4.9/4.10/8 là chỗ cần phản hồi nhất. Ví dụ tài
liệu render từ fixture đã duyệt; output hệ không tự phong là gold.*
