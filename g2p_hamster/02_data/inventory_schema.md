# inventory_schema.md — schema của một entry inventory `ham/0.1`

Ngày: 01/10/2026. **Bản 2** — áp dụng phản hồi vòng duyệt schema (4 điểm bắt buộc + 6 thay
đổi tối thiểu). Bản 1 bị phản đối freeze vì 2 lỗi logic schema: (1) `unicode` vừa bị tuyên
bố "không phải danh tính" vừa bị audit ép thành khóa duy nhất; (2) versioning bắt đổi
unicode của ID cũ phải tạo ID mới — trái triết lý mục 1.

Nguồn sự thật: `02_data/inventory_ham.tsv` + loader/audit `01_g2p/inventory.py`.
Đặc tả 4.2 (`G2P_KE_HOACH_DANH_GIA.md` bản 5). Chốt TRƯỚC khi viết `vi_rules.py`.

## 1. Hai lớp danh tính — hiệu chỉnh cốt lõi của bản 2

```text
1. Semantic ID (PHONE_*, TONE_*, STRESS_*, PUNCT_*) — DANH TÍNH.
   - Bất biến về NGHĨA: không đổi nghĩa, không tái sử dụng sau khi xóa.
   - Đây là thứ acoustic model tương lai học embedding.
2. Unicode repr — BIỂU DIỄN, không phải khóa.
   - Nhiều code point được (ʈʂ, tʰ, aː, əː, iə…) = 1 token.
   - **Đổi notation hoặc sửa repr cho đúng với nghĩa đã được định nghĩa không tạo ID mới,
     nếu phạm vi phát âm của ID không thay đổi. Nếu thay đổi phạm vi phát âm được phép học,
     PHẢI tạo semantic ID mới và ngừng dùng ID cũ theo quy trình migration** — đổi repr
     không được trở thành đường vòng để đổi nghĩa ID.
   - Hai ID KHÁC nhau CÓ THỂ cùng repr nếu cặp đó nằm trong allowlist đã duyệt
     (vd PHONE_SCHWA_VI / PHONE_SCHWA_EN cùng hiện `ə` khi tách [B]).
     Trùng repr KHÔNG khai báo → audit FAIL (điều 2).
   - CẤM sửa IPA cho khác đi chỉ để vượt audit.
```

Hệ quả: `unicode` không còn là điều kiện correctness của đối lập. Đối lập được bảo toàn bởi
đôi khác **semantic_id** + luật phát âm dùng đúng ID (kiểm riêng — điều 6/7 và fixtures fase B).

## 2. Định nghĩa một entry (1 dòng TSV, 5 cột)

| Cột | Ý nghĩa | Quy tắc |
|---|---|---|
| `semantic_id` | danh tính | `PHONE_*` (segment) · `TONE_*`/`STRESS_*` (prosody) · `PUNCT_*` (control); unique toàn bảng, không tái sử dụng |
| `loai` | lớp | `segment` \| `prosody` \| `control` — phải khớp tiền tố ID (audit điều 3-4) |
| `unicode` | hiển thị IPA | nhiều code point được; segment không chứa code point số nào (điều 5); trùng giữa 2 ID chỉ hợp lệ khi nằm trong allowlist `SHARED_UNICODE_REPR` (điều 2) |
| `sound_desc` | mô tả âm (ASCII) | để tra cứu, không dùng bởi code |
| `notes` | **CHỈ cho người đọc** | không chứa semantics máy đọc; xem §3 |

**Machine semantics KHÔNG nằm trong `notes`** — nằm ở cấu trúc có kiểm trong code:

- `REQUIRED_CONTRASTS` (bảng đối lập bắt buộc) — `01_g2p/inventory.py`.
- `MERGE_RULES` (các merge chủ đích CÓ PHẠM VI, thay cho `INTENTIONAL_MERGES` cũ) — §6.
- Loss map của profile — `SEGMENT_MAP_KOKORO178` / `TONE_TO_ARROW` trong `01_g2p/profiles.py`.

`notes` chỉ ghi nguồn dùng, giải thích cho người; nội dung máy-đọc kiểu `shared:`/`loss:` trong
notes hiện có là di sản mô tả, audit KHÔNG parse notes.

## 3. Quy tắc chia sẻ và đối lập (diễn đạt lại)

- **Cùng acoustic-phonetic category CHỦ ĐÍCH → chung 1 ID** (vd vi `x` + en `S` = `PHONE_S`;
  vi `â` + en `AH0` = `PHONE_SCHWA` [B]) — cùng embedding khi train, tiết kiệm dữ liệu.
  Tiêu chí là *quyết định acoustic category*, không phải "IPA nhìn giống nhau".
- **Cần được model phân biệt → ID khác, DÙ repr có thể giống** (vd nếu tách
  PHONE_SCHWA_VI/EN cùng hiện `ə`). Ngược lại vi `s`=ʂ ≠ en `sh`=ʃ, vi `th`=tʰ ≠ en `th`=θ.
  Danh sách bắt buộc: `REQUIRED_CONTRASTS` — duyệt ĐỘC LẬP với bảng luật; sửa bảng = sửa đặc tả.
- **Đối lập mức CHUỖI ÂM TIẾT** (`tai≠tay`, `cao≠cau`, `mác≠mách`, `an≠anh`) — không kiểm
  được bằng ID thành phần; kiểm bằng điều 7 + fixtures fase B.
- Chia sẻ embedding do tầng 3 quyết **theo ID**; cùng ID mới cùng embedding.
- **Quyết định chia sẻ ID là một annotation/design decision — phải có bằng chứng lưu vết:**
  artifact `02_data/inventory_provenance.json` ghi nguồn của mỗi ID chia sẻ
  (vd `PHONE_S`: vi `x` + en `S`; `PHONE_I`: vi `i` + vi `y`) kèm lý do + mốc duyệt, để
  reviewer hỏi "tại sao hai âm này dùng chung embedding?" có tài liệu trả lời, không phải
  nhớ từ lịch sử chat.

## 4. Prosody là token hay feature? — CHỐT: token

- `TONE_*` là token prosody gắn đúng 1 âm tiết; **field `tone` trong record là nguồn sự
  thật**, stream sinh TỪ field (một hướng).
- `STRESS_PRIMARY` = primary tường minh; `STRESS_SECONDARY` = secondary tường minh;
  **KHÔNG có `STRESS_*` nào gắn = unstressed** — quy ước này là định nghĩa, không để người
  implement `en_lexicon.py` tự quyết. **Phạm vi áp dụng:** chỉ cho đầu ra ĐÃ xác định được
  stress. Đầu vào chưa xác định stress (vd OOV chờ spell) KHÔNG được âm thầm coi là
  "mọi nucleus unstressed" — record/pipeline phải ghi trạng thái chưa giải quyết và xử lý
  theo policy (fallback hoặc chuyển spell). Không cần token `STRESS_UNKNOWN`; phân biệt ở
  mức record để lỗi "quên phát stress" không trông giống kết quả hợp lệ.
- Tone/stress KHÔNG được xuất hiện kiểu segment (điều 3-4); segment KHÔNG được chứa code
  point số (điều 5).

## 5. Control và phạm vi serialize (sửa tiêu đề cũ)

- Trong **master stream**: chỉ `PUNCT_*` là control token đi vào luồng cho model; ranh giới
  từ/âm tiết và liên kết nguồn (`source_token_id`, `read_unit_index`, `syllable_index`) là
  **structural metadata** — không phải vocabulary token.
- Khi **export profile** (vd kokoro178): segment, prosody VÀ control đều được serialize thành
  chuỗi ký tự theo spec của profile đó. "Không phải vocabulary token" không đồng nghĩa
  "model tuyệt đối không được dùng metadata" — quyết định dùng boundary metadata làm đầu vào
  phụ của tầng 3 ghi riêng, không nằm trong schema này.

## 6. Audit va chạm (collision audit) — 7 điều (đổi tên điều 7)

Chạy: `venv/bin/python 01_g2p/inventory.py` (mỗi lần sửa TSV). Giới hạn trung thực: audit bắt
xung đột **đã mô hình hóa**; tính đúng âm vị học do gold set + fixtures đảm bảo.

| Điều | Kiểm tra |
|---|---|
| 1 | semantic_id unique |
| 2 | trùng unicode repr giữa ≥2 ID → FAIL **trừ** khi nhóm ID thực tế là tập con của một nhóm khai báo trong allowlist `SHARED_UNICODE_REPR` (định dạng THEO NHÓM: `{unicode, ids[], reason}` — không phải cặp; nhóm 3 ID chỉ cần 1 entry). Allowlist tự kiểm: mọi id tồn tại, mỗi nhóm ≥2 id phân biệt |
| 3 | mọi ID thuộc lớp hợp lệ; đủ 6 tone, 2 stress, control bắt buộc |
| 4 | tách lớp khớp tiền tố (PHONE/TONE/STRESS/PUNCT) |
| 5 | segment KHÔNG chứa code point thuộc nhóm Unicode Number nào (predicate: `unicodedata.category(ch)[0] == "N"` — bắt cả `a1`, số ngoài ASCII, ½) |
| 6 | mọi cặp `REQUIRED_CONTRASTS`: cả hai ID tồn tại, khác ID, đúng lớp. **Khác unicode KHÔNG còn là tiêu chí** (đã bỏ — bảo toàn đối lập qua luật là bài kiểm riêng ở fase B: fixtures đối lập phải đi qua vi_rules, không lách spell/fallback, đầu ra khác nhau, đối chiếu reference độc lập) |
| 7 | **audit va chạm phát âm (realization-collision)** — KHÔNG phải "đơn ánh": generator sinh âm tiết → master → gom theo **khóa = chuỗi semantic ID GỒM prosody** (segment + tone + stress; không phải chuỗi IPA hiển thị, nếu không `ma/mà` bị gom nhầm). Trước khi gom: NFC normalize, chốt chính sách hoa/thường, pin dialect + version luật. Nhóm >1 chính tả hợp lệ phải khớp một rule trong `MERGE_RULES` CÓ PHẠM VI, nếu không FAIL (hook — chạy từ fase B) |

**`MERGE_RULES`** thay `INTENTIONAL_MERGES = {"PHONE_I"}` cũ (quá rộng, không chỉ ra phạm vi).
Mỗi rule: `rule_id` · `level` (segment \| syllable) · `matcher` (**trường máy kiểm**, xem dưới)
· phạm vi chính tả/ngữ cảnh · lý do · fixture minh họa. Quy trình khi generator gặp nhóm
trùng: xuất báo cáo → người duyệt → thêm rule có phạm vi. **CẤM tự bơm toàn bộ nhóm trùng
vào allowlist** (audit luôn xanh = vô nghĩa).
Generator từ bảng luật chỉ kiểm được miền đã mô hình hóa — bộ từ/gold độc lập vẫn cần thiết.

**`matcher` (bổ sung fase B — điều 7 kiểm tự động):** mọi skeleton của nhóm collision,
qua canonical hóa của matcher, phải gộp về MỘT chuỗi — mới tính "giải thích trọn vẹn".
Kind: `letter_alt` (thay ký tự mọi vị trí) · `seq_alt` (thay chuỗi) · `tail_alt` (chỉ coda).
`explain_collision` cho phép HỢP tối đa 4 matcher (biến thể độc lập cùng lúc, vd
`bio/byo/biu/byu` = i↔y × o↔u) — nhưng không bao giờ che được khác biệt ngoài các subs đã
khai (rơi coda `lí`/`lín` → FAIL, đã khóa bằng test âm tính). Matcher chạy trên skeleton
đã strip dấu thanh.

**Điều kiện nghiệm thu implementation (khóa bằng test khi fase B chạy generator):**

1. Nhóm trùng repr ≥3 ID: chỉ một cặp được duyệt là KHÔNG đủ — mọi cặp không thứ tự trong
   nhóm phải được allowlist phủ (thực thi bằng kiểm tập con nhóm, xem điều 2).
2. `MERGE_RULES` phải **giải thích đầy đủ** khác biệt giữa các chính tả trong nhóm collision,
   không chỉ khớp một phần: rule segment-level (vd i/y) KHÔNG tự động miễn kiểm toàn âm tiết
   — nếu lỗi rơi coda khiến `lí`/`lín` trùng đầu ra, rule i/y không được che lỗi đó.
   Nhóm collision chỉ PASS khi khác biệt được giải thích trọn vẹn bởi các rule đã duyệt.
3. "Không có stress = unstressed" chỉ áp cho đầu ra đã xác định stress (xem §4) — test phải
   phân biệt "unstressed hợp lệ" với "chưa xử lý stress".

## 7. Versioning, token_id registry, fingerprint (cho tầng 3)

**Hai trục version tách bạch:**

- `semantic_version` (**ham/0.1**):
  - Bump khi **thêm ID, ngừng dùng ID, hoặc thay đổi `REQUIRED_CONTRASTS`**.
  - Nếu cần một nghĩa khác: **tạo ID mới, deprecate ID cũ và ghi migration**.
  - Không phiên bản nào được phép gán lại nghĩa cho semantic_id đã cấp.
  - "Xóa" = loại khỏi active inventory; **lịch sử registry không bao giờ xóa**.
- `representation_revision` (vd `rep/1`): bump khi đổi unicode repr hay notation hiển thị
  KHÔNG đổi nghĩa (theo điều kiện phạm vi phát âm ở §1). Hash đổi → pipeline re-run,
  nhưng ID (embedding identity) bất biến.

**Registry `semantic_id → model_token_id` (bổ sung bắt buộc):**

- Mapping được LƯU và version hóa (file riêng, không phải cột TSV; sinh ở fase D
  `emit_vocab_config.py`).
- KHÔNG đánh số theo thứ tự dòng TSV hay alphabet; thêm dòng KHÔNG được làm dịch chuyển
  token_id của các token cũ.
- token_id đã cấp không tái sử dụng; token ngừng dùng giữ làm tombstone trong registry.
- Mọi thay đổi mapping phải có migration ghi rõ.

**Fingerprint hai lớp cho reproducibility:**

- `inventory_hash` (sha256 **raw bytes** TSV) — một mình KHÔNG đủ: behavior audit còn phụ thuộc
  `REQUIRED_CONTRASTS` + `SHARED_UNICODE_REPR` + `MERGE_RULES` nằm ngoài TSV. Đổi 1 trong 3
  bảng đó mà giữ nguyên TSV vẫn được cùng `inventory_hash` nhưng behavior khác.
- `inventory_contract_hash` (sha256 canonical serialization của **TSV + 3 bảng machine
  semantics**) — đây là fingerprint behavior của A1. Cả hai hash ghi vào mọi đầu ra
  `g2p/0.1` + report E5. Ba bảng này nằm trong code có kiểm (`inventory.py`) — sửa chúng
  PHẢI đi qua commit được review, không sửa ngoài dấu vết tái lập.
- Fingerprint đầy đủ còn kèm: rules version, dialect config, lexicon version, profile version.
- Với acoustic artifact: thêm **`registry_hash`** (sha256 registry `semantic_id →
  model_token_id`) — cùng inventory chưa tự bảo đảm cùng mapping số; kiểm riêng khi phát
  integer IDs hoặc nạp checkpoint.

**Namespace token (ranh giới với tầng 3):** `model_token_id` của inventory CHỈ dành cho các
semantic_id thuộc `ham/0.1`. Special token riêng của architecture tầng 3 (PAD, BOS, EOS,
MASK…) nằm trong **namespace khác** và KHÔNG được đưa vào inventory hay registry — không có
chuyện `PHONE_A → 17`, `PAD → 18` rồi ai đó tưởng PAD là thành phần của `ham/0.1`.

## 8. Đặc tả TSV tối thiểu

- UTF-8, KHÔNG BOM; dòng comment bắt đầu `#`; đúng 5 cột mỗi dòng dữ liệu.
- Cột `notes` được rỗng; 4 cột còn lại bắt buộc khác rỗng.
- Cấm tab/newline bên trong field (tab là dấu phân cách); cấm ký tự điều khiển khác.
- Unicode normalization: **NFC áp dụng tại loader** (`inventory.py`) — mọi phép so sánh
  downstream dùng form đã normalize; hash tính trên **raw bytes** (hash artifact ≠ nội dung
  đã normalize, ghi rõ trong output).

## 9. Báo cáo trạng thái audit — tách tĩnh/thực thi

Không báo "7/7 PASS" khi điều 7 chỉ là hook. Output chuẩn:

```text
Static inventory audit (điều 1-6): PASS
Realization-collision audit (điều 7): NOT_RUN — requires fase B generator
```

## 10. Trạng thái hiện tại (fase B implement xong, nghiệm thu âm vị CHƯA xong — 02/10/2026)

- **Schema được duyệt ở mức THIẾT KẾ** (vòng duyệt bản 2): dùng làm nền triển khai A1/B,
  không cần vòng redesign nữa. Việc nghiệm thu implementation tách riêng bằng test
  (§6 — điều kiện nghiệm thu). Duyệt schema KHÔNG đồng nghĩa duyệt 77 entry hay chất lượng G2P.
- 77 entries (segment 61 · prosody 8 · control 8). Ô mở trong data: `PHONE_SCHWA` chung/tách
  [B] — **audit không thể tự quyết thay lựa chọn âm vị này**; phải chốt trước khi khóa
  inventory dùng cho dữ liệu train acoustic; không được âm thầm coi là đã duyệt để train.
- `SHARED_UNICODE_REPR` hiện rỗng (chưa có cặp trùng repr), định dạng theo nhóm.
- **Trạng thái điều 7 (khung của người duyệt; cập nhật vòng 5 — 02/10/2026, theo báo
  cáo review v5 V5-01…05 + A3-01…04):**
  - Static inventory audit (điều 1-6): PASS — namespace validator giữ từ vòng 4 (F08).
  - Unit/regression tests: PASS (**265 check vi_rules** — vòng 5 thêm test tên riêng
    cho từng khối + **tự kiểm AST tên test trùng** [V5-03]; **74 test profile** — thêm
    sidecar/export, enum state, từ thật qua parser; 52 test cũ giữ từ fase A).
  - Realization-collision: **PENDING_APPROVAL** (exit 2) — **27.210 dạng** sinh bằng
    render canonical rồi parse ngược (V5-02), **core 20.100 / stress 7.110** theo
    `is_core` NGỮ CẢNH (V5-01: yê chỉ khi không onset hoặc sau qu; ây nhận coda y;
    ng mất e/ê — ngh phụ trách; c/k+glide-o viết qu ở lõi). Nhóm GATE (≥2 core):
    **2.776 — approved 0 · proposal 2.776 · identity 0 · unexplained 0**; 3.868 nhóm
    stress-only không gate. 11/11 cặp đối lập phân biệt. **Kiểm core độc lập
    accept/reject tường minh: 27 từ thật nhận + 18 tổ hợp loại, 0 lỗi** — sai → FAIL.
  - **Vòng 5 (theo review v5):**
    - V5-02 renderer: chữ i dùng chung của nhánh gi KHÔNG còn được viết lặp
      (`render_parts("gi","","i","n") = "gìn"`, không "giìn"; giết giữ nguyên —
      trước đây "giiết" parse lại mất I_SCHWA); generator sinh spelling canonical
      (gì/gìn/giêng/giết vào miền, "gii"/"giin" biến mất); test hai chiều
      word→parts→render→parse trên 25 từ thật.
    - V5-01 core: `CORE_ACCEPT`/`CORE_REJECT` + `core_acceptance_check()` — kiểm
      accept/reject ĐỘC LẬP (không lấy output generator làm đáp án), vi phạm → FAIL.
    - V5-04 matcher: **worklist fixpoint theo thứ tự catalog** (không hoán vị, không
      backtracking); mỗi bước áp phải (a) biến đổi được, (b) **wellformed** (render
      canonical → parse ngược ra đúng parts — chặn nối qua "kua" giữa qua/koa),
      (c) **bảo toàn record phát âm** (chặn cao/cau qua COND_NUC, kue/que qua
      E≠OPEN_E); tier mới **identity** (parts vốn giống — gi/gii, không cần rule);
      trace chỉ ghi rule thực sự áp. Rule mới đề xuất **MR-CODA-I-Y** (coda y=i cùng
      PHONE_J — âi=ây; engine tự chặn y→i sau form "a" giữ tai≠tay) — tổng **10 rule
      đề xuất, 0 approved**; fixtures sửa: "khoa/khua cùng onset kh khác vần oa/ua"
      (sửa văn bản sai vòng 4), bỏ "kẻo=kêu" (khác thanh — không phải fixture đồng âm),
      MR-QU-K-GLIDE fixture đổi thành kuy=quy (qua/koa không còn nối được).
    - V5-05 status: `compute_status()` MỘT NƠI từ mọi điều kiện lỗi (contrast_fail/
      core_fail → FAIL bất kể proposal) — dùng chung JSON/Markdown/stdout/exit code;
      mutation-test cho nhánh contrast_fail ở unit test.
    - A3: sidecar lưu **đơn vị profile thực tế** (sau loss map — thà: text θaː↘ =
      sidecar; master repr tʰ còn traceable qua loss_report) [A3-02]; **enum đóng**
      TONE_STATES/STRESS_STATES — state gõ sai bị validate chặn [A3-03]; test synthetic
      đặt nhãn đúng, từ thật đi qua `parse()` [A3-04]; **kokoro_vocab_178.tsv pinned**
      (sha256 `3dec592f…c31b`) đóng gói kèm [A3-01].
  - Fase B: **chưa nghiệm thu âm vị** — gold-dev 45 từ 0 bất đồng (không đổi ở vòng 5);
    chờ duyệt 10 rule đề xuất trên matcher structural + xác nhận miền core.
  - **Vòng 4 (theo báo cáo kiểm code reviewer — patch F01-F08):**
    - F01 parser: `uy` là composite glide w+i (`tuy` = T+W+I ≠ `tui` = T+U+J) — lỗi
      thật trước đây bị MR-I-Y "đã duyệt" che (reference + regression cùng bảo vệ sai).
    - F02 parser: onset `gi` → **PHONE_GI** (không PHONE_GH); chữ i dùng chung
      onset+nguyên âm (`gìn` = GI+I+N), `gi+ê` → vần iê (giêng/giết = GI+I_SCHWA).
    - F03 parser: `Uə`+m (buồm, muỗm); uy+offglide u (khuỷu) — từ lõi không đẩy spell.
    - F04 matcher: **matcher structural trên parsed parts** (role_alt/composite_alt/
      onset_glide_alt/rhyme_alt) thay global replace; **MR-I-Y bị HẠ CỜ approved**
      (đã che lỗi tui/tuy), **MR-tai-tay rút khỏi catalog thực thi** (WITHDRAWN_RULES);
      **0 rule approved ở tầng matcher**; explain phân tầng approved→proposal→
      unexplained (§5.4). Hướng canonicalize qu là `k+u → qu` — hướng ngược lại kết
      hợp UE-UÊ sẽ giải thích sai que/quê.
    - F05: `parse()` là hàm thuần, **KHÔNG còn tham số fold** — resolver fold là lớp
      gọi riêng (fase D); nam không thể bị fold sửa âm thầm.
    - F07: cờ `[B]` qu+ô gắn đúng `quốc` (key theo form "ô"); quọt (o thường) không cờ.
    - F08: namespace validator (trên).
- Fase B: **chưa nghiệm thu âm vị** — gold-dev 45 từ 0 bất đồng (vòng 4: gi/gì/gìn/
    giêng/giếng/giết/giọng/giỗ; tui/tuy/thúi/thúy/huy/duy; buồm/muỗm/khuỷu; kiểm đối
    lập trên RECORD parser, không còn reference tự so reference); chờ duyệt 10 rule
    đề xuất + xác nhận miền core.
- **Quyết định đã duyệt 02/10/2026 (áp vào bảng):**
  - KHÔI PHỤC fixture `mác≠mách`; ba đối lập `mác≠mách≠mắc` và `khác≠khách≠khắc`
    **bắt buộc** ở mức master (yêu cầu được duyệt). Phân tích vần `ach = /ɛk/`
    (PHONE_OPEN_E) là **ĐỀ XUẤT đáp ứng yêu cầu đó** — KHÔNG ghi là "đã duyệt toàn
    miền biểu diễn" (vòng 4: bỏ câu nói duyệt đã duyệt phân tích); coda ch/c cùng
    PHONE_K (A1) — đối lập nằm ở nguyên âm. `khắc≠khác` là fixture bổ sung.
    **Vòng 2:** `mắc`/`khắc` là thanh SẮC (ắ; mặc/khặc mới là nặng) — lần trước
    reference bị đổi sang nặng là đổi đáp theo hệ, đã khôi phục; kiểm segment-bỏ-tone;
    bộ `ke/que`, `kê/quê`, `que/quê` (que = K + W(glide) + OPEN_E — "que mất glide"
    là lỗi diễn giải, parser/reference đúng).
  - `suất ≠ suốt` KHÔNG phải ô mở: `uâ` = glide w + â; `uô` = nucleus U_SCHWA — khác chuỗi, chốt.
  - `khoét` có **é** (vần oet) — vá `W_OK["Ê"]` ngày 01/10 là SAI BẢNG, đã revert.
  - Parser KHÔNG tự phục hồi thanh: `mach` (không dấu + coda tắc) = ParseError;
    nhánh fold ủy quyền mới được chọn ứng viên (vòng 4: tách hẳn khỏi parse()).
  - Mỗi MERGE_RULES có `approved` + `approved_basis` (dấu vết duyệt cụ thể); duyệt
    inventory A1 KHÔNG tự động duyệt rule ngôn ngữ học; **không chấp thuận** "hệ quả
    trực tiếp của một phân tích nên được merge" — MR-ACH-EC giữ false, xét duyệt phải
    xem từng cặp cụ thể (thuần Việt vs mượn/tượng thanh) + bằng chứng phát âm độc lập.
- Fingerprint: `inventory_hash` (raw bytes) + `inventory_contract_hash` (TSV + 3 bảng
  machine semantics; hiện `817d74be…d8d2` — vòng 6 sửa lỗi trình bày đuôi hash,
  vòng trước viết nhầm `f1d2`) — cả hai in bởi `inventory.py`.

### 10.1 Cập nhật vòng 6 (02/10/2026 — reviewer chấp nhận bản vá kỹ thuật, chưa nghiệm thu B)

- **Căn cứ miền core độc lập (§9.1 review vòng 6):** `is_core()` ngữ cảnh một mình
  KHÔNG đủ ("câi/mấi/bêo" lọt). Core = is_core(ngữ cảnh) **∩ attestation(freq≥2)**
  trong `02_data/core_domain/vi_syllable_vocab.tsv` — 124.934 âm tiết trích corpus
  IR tầng 1 (nguồn ngoài G2P; sha256 corpus + artifact trong
  `core_domain_provenance.json`; sinh bằng `build_core_domain.py`, không lọc theo
  parser). Lớp mới **ext** = core-ngữ-cảnh nhưng không attested — miền mở rộng,
  KHÔNG gate, KHÔNG đòi duyệt đồng âm. Kiểm regression miền: DOMAIN_MUST_ATTEST
  (cây/mấy/bêu/tay/lý/kỹ/sĩ/kỳ/mỹ/ích/ưu/muỗm/khuỷu/yếm/que/quê/hue/huê/yên) +
  DOMAIN_MUST_NOT (câi/mấi/bêo/buâi/buây/gii) — vi phạm → FAIL.
- **Điều 7 (vòng 6):** 27.210 dạng = core-attested 6.901 · ext 13.199 · stress
  7.110 → nhóm GATE (≥2 core-attested) **98 = 0 approved + 98 proposal + 0
  identity + 0 unexplained** · nhóm ext 4.978 · stress-only 1.568 · 11/11 đối
  lập · PENDING_APPROVAL (exit 2). Gate co từ 2.776 (vòng 5) về 98 nhóm chính tả
  thật — phạm vi hữu hạn minh bạch để xét duyệt scope rule. Độ nhạy ngưỡng: 65
  nhóm @min_freq=5, 51 @min_freq=10. Markdown điều 7 có dòng `Status:` tổng thể
  (§8.1); hash trình bày sửa `f1d2`→`d8d2` (§8.2).
- **Scope 10 rule (§9.2):** đối tượng gate attested + freq từng thành viên + đề
  xuất từng rule trong `02_data/core_domain/rule_scope_vong6.md` — MR-I-Y 52 nhóm
  (mạnh nhất; nhánh ya→ia không còn nhóm attested), MR-CODA-O-U 19, MR-ACH-EC 11
  (vẫn chờ bằng chứng phát âm E6), MR-CODA-CH-C 6 / MR-UE-UÊ 5 (nửa thành viên
  biên), MR-CODA-I-Y 1 (âi/ây freq 2/14 — đề xuất KHÔNG duyệt), MR-ONSET-GH-G /
  MR-ONSET-C-K / MR-QU-K-GLIDE 0 nhóm riêng (chỉ compose). **KHÔNG rule nào bật
  approved** — quyết thuộc reviewer trên bảng scope.
- Tests: `test_vi_rules.py` 295 PASS (thêm `test_core_domain_attestation` —
  classification, hash pin, bucket gate/ext/stress); gold-dev 45 từ 0 bất đồng
  (reference KHÔNG đổi); static PASS; profile 74 PASS. Snapshot v7 trong
  `reference_diff.md`.

### 10.2 Cập nhật vòng 6.1 (02/10/2026 — attestation = lớp bằng chứng, không thay thẩm định chính tả)

Phản hồi reviewer trên nhật ký v7: chấp nhận attestation làm lớp bằng chứng và cách
giới hạn miền đánh giá; KHÔNG chấp nhận dùng attestation thay xác nhận chính tả lõi.
Năm điều chỉnh, đúng 5 điểm reviewer nêu sẽ kiểm:

1. **Tên gọi:** "124.932 **dạng token**" (từ corpus), không "âm tiết chuẩn đã thẩm
   định" — nguồn độc lập ≠ nhãn ngôn ngữ độc lập. Kết luận giới hạn: *"audit trên
   miền ứng viên có chứng thực trong corpus phiên bản pin `5105d872…`, ngưỡng tần
   suất 2"* — ghi tường minh trong `domain_scope_statement` của report.
2. **Nguồn:** chỉ corpus chính `corpus_ir_1M.jsonl.gz` (1.000.000 records); loại
   supplement edge-case 108 records (sha256 + kiểm 0 hit từ chẩn đoán gold khai
   trong `core_domain_provenance.json` kèm `field_spec` chi tiết cách đếm:
   cat=word, route=vi, verbal, NFC+lower, tách tham lam).
3. **Truy vết nhóm ngoài gate:** `dieu7_ext_groups.jsonl` (4.978 nhóm) +
   `dieu7_stress_groups.jsonl` (1.568 nhóm) — xuất ĐẦY ĐỦ, không mất dấu collision
   chưa giải quyết; thu hẹp gate 2.776→98 không được diễn giải thành giải quyết
   ngôn ngữ.
4. **Pin hành vi:** `domain_config_hash` = `1170b911…01d33` (sha256 gộp TSV pin +
   builder + ngưỡng freq≥2 + list regression) — bù cho `inventory_contract_hash`
   vốn không đại diện hành vi miền audit.
5. **Tần suất không chứng minh đồng âm** — đồng âm vẫn là claim của bảng record,
   chờ duyệt scope (`rule_scope_vong6.md`); freq≥2 KHÔNG trở thành quy tắc chính tả.

Số điều 7 không đổi: 98 nhóm gate = 0 approved + 98 proposal + 0 identity + 0
unexplained → PENDING_APPROVAL (exit 2). Tests `test_vi_rules.py` **298 PASS**.
Snapshot v8 trong `reference_diff.md`.

### 10.3 Cập nhật vòng 6.2 (02/10/2026 — sửa R61-01/02/03: đếm literal, hash phủ classifier, scope doc sinh tự động)

Review trên source/artifact thật của gói v8 (23/23 hash khớp, tái lập được 98 nhóm)
tìm ra ba lỗi mới — sửa tập trung builder → fingerprint → scope doc, không đụng
G2P/gold/ca đã đóng:

1. **R61-01 (cao):** builder tách token theo số dấu thanh (`strip_tone` không kiểm
   cấu trúc âm tiết) → `họctập` thành `họct`+`ập`, corpus tổng hợp `lựchọc`×2 sinh
   freq `lựch`=2 giả và đùn vào gate. Sửa: đơn vị đếm = **token nguyên dạng literal**
   (verbal NFC+lower+strip, toàn chữ — mỗi occurrence đếm 1 lần, KHÔNG tách, KHÔNG
   dùng strip_tone/parse; builder không import parser). Rebuild: `lựch`,
   `ếc`, `họct`, `thànhph` có tần suất literal = 0; `lệc` 2→1 (dưới ngưỡng) — ba
   nhóm lực/lựch, lệc/lệch, ếc/ếch rời gate (lẹc là cách viết khác, không thuộc
   nhóm cũ — hậu kiểm vòng 6.2); `lựchọc`/`họctập` được đếm nguyên dạng. Fixture synthetic trong `test_vi_rules.py` chặn hồi quy.
2. **R61-02 (TB):** `domain_config_hash` cũ chỉ chứa chuỗi mô tả classifier —
   mutation `CORE_ONSET_FIRST['k'].add('a')` đổi gate 98→107 mà hash không đổi.
   Sửa: hash gộp **snapshot RUNTIME** của `CORE_ONSET_FIRST`/`CORE_TAILS` (đọc từ
   module đang chạy) + sha256 source `is_core`/`attest_class`/
   `enumerate_syllables`/`build_groups` + sha256 module `vi_rules.py`/`vi_syllable.py`
   (miền sinh). Mutation in-memory hay sửa code đều làm hash đổi — có test.
3. **R61-03 (TB):** scope doc có số liệu gõ tay lệch artifact (`cảo/cấu` thay vì
   `cấo/cấu`; "ich/ic = I_SCHWA" trong khi JSON là PHONE_I; freq stale; "compose
   cần ≥2 rule" sai vì `cấo/cấu` giải thích được bằng MR-CODA-O-U đơn lẻ). Sửa:
   `01_g2p/gen_rule_scope.py` **sinh tự động** `rule_scope_vong6.md` từ
   `dieu7_bao_cao.json` + bảng pin — mọi số liệu (thành viên, freq, seq record,
   rule trace, sensitivity) đọc trực tiếp từ artifact; nhận xét tác giả ở mục
   riêng. Câu compose sửa thành "trace dùng nhiều rule — CHƯA chứng minh tập tối
   thiểu".

Bổ sung: `01_g2p/trace_vocab_members.py` → `02_data/collision/gate_member_trace.jsonl`
(210 dạng gate: record locator, token index, verbal raw, ngữ cảnh ±3 token, đếm
literal khớp TSV 100%) — trace nguồn gọn theo yêu cầu reviewer §8.4. 8 cặp i/y
reviewer xác nhận (kí/ký, lí/lý, kì/kỳ, kĩ/kỹ, mĩ/mỹ, sĩ/sỹ, tỉ/tỷ, qui/quy) được
đưa vào `test_vi_rules.py` ở MỨC FIXTURE (expected record viết tường minh, không
suy rộng thành matcher rộng).

Số điều 7 sau rebuild literal: **95 nhóm gate** = 0 approved + 95 proposal + 0
identity + 0 unexplained → PENDING_APPROVAL (exit 2) — báo trung thực theo dữ
liệu, không giữ số 98. `domain_config_hash` mới `5d0e89f5…87ad2`. Tests
`test_vi_rules.py` **332 PASS**. Snapshot v9 trong `reference_diff.md`.

### 10.4 Hậu kiểm vòng 6.2 (02/10/2026 — T62-01 + chỉnh chú thích; vòng vá kỹ thuật CHỐT)

Review v9 chấp nhận bản sửa R61-01/02/03 (builder literal, fingerprint, scope doc
sinh tự động — tái lập 95 nhóm, 332/74 PASS). Hai chỉnh nhỏ còn lại, không mở lại
lỗi đã đóng:

1. **T62-01:** `gate_member_trace.jsonl` ghi `token_index` theo danh sách ĐÃ LỌC
   (cat=word route=vi) thay vì index gốc trong `ir.tokens[]` — tra ngược sẽ trúng
   token khác. Sửa: `trace_vocab_members.py` enumerate `ir.tokens[]` nguyên bản,
   lọc trong vòng lặp, ghi index gốc; ngữ cảnh cũng dựng từ `ir.tokens[]` nguyên
   bản; field `token_index_scope` khai rõ phạm vi. Phép đếm KHÔNG đổi — freq vẫn
   khớp TSV 100%. Test hồi quy `test_trace_locator_original_index` (punct[0] +
   en[1] + 'lực'[2] → trace ghi 2).
2. **Chỉnh chú thích:** ghi chú "lựch, lẹc, ếc … freq literal = 0" nhầm lẹc/lệc —
   đúng theo bảng: `lựch`=0, `ếc`=0, `lệc` 2→1 (dưới ngưỡng, không phải 0; `lẹc`
   không thuộc nhóm cũ nào). Ba nhóm rời gate: lực/lựch, lệc/lệch, ếc/ếch.
   `gen_rule_scope.py` giờ đọc các con số trong chú thích từ bảng pin ngay lúc
   sinh (không gõ cứng).

Trạng thái: **vòng vá kỹ thuật CHỐT** — các lỗi V5/A3/R61 giữ trạng thái đóng.
Việc tiếp theo là quyết định NGÔN NGỮ có phạm vi trên 95 nhóm (ưu tiên các cặp từ
thật: ach/ec, coda-ch/c), KHÔNG tiếp tục sửa builder hay chỉnh ngưỡng để giảm gate.
Số điều 7 không đổi: 95 nhóm → PENDING_APPROVAL (exit 2).

### 10.5 Cập nhật vòng 6.3 (02/10/2026 — áp quyết reviewer v11: ham/0.2, lớp EXACT_FIXTURE, withdrawn MR-ACH-EC)

Review v11 ra phán quyết cụ thể cho đủ 95 nhóm: 26 ALLOW_EXACT_VI_FIXTURE · 10
DO_NOT_MERGE_PRESERVE_CONTRAST · 59 INSUFFICIENT_EVIDENCE (không gọi noise, không
chuyển stress-technical đồng loạt). Triển khai:

1. **ham/0.1 → ham/0.2 (thay đổi thiết kế có phiên bản):** thêm ID
   `PHONE_OPEN_E_PREVELAR` (segment, ɛ — vần 'ach'); `PHONE_OPEN_E` BẤT BIẾN;
   `SHARED_UNICODE_REPR` khai nhóm shared ɛ; registry ổn định, test EN không đổi.
   `COND_NUC[("a","ch")]` → ID mới. Gold-dev: mách/khách cập nhật theo (nguồn
   quyết ghi trong note). Lý do: đối chiếu mục từ độc lập sách [sajk̟̚] vs Séc
   [sɛk̚] + Kirby (2011) tr.383-384 — không suy "ch có thể là /k/" thành đồng nhất
   toàn vần ach/ec.
2. **10 cặp ach/ec = ĐỐI LẬP bắt buộc** trong `SYLLABLE_LEVEL_CONTRASTS` (sách/séc,
   mách/méc có đối chiếu mục từ; 8 cặp còn lại là policy mặc định bảo toàn lớp
   vần — chưa thẩm định audio từng cặp). 12 nhóm collision ach/ec (11 solo +
   cạch/kẹc) hết collision do thay đổi biểu diễn.
3. **MR-ACH-EC → WITHDRAWN_RULES** (v11 §4.4: KHÔNG DUYỆT — không treo như
   proposal chỉ chờ nghe model; audio sinh từ pipeline gộp hai record không là
   chứng cứ đồng âm độc lập).
4. **Lớp duyệt EXACT_FIXTURE (v11 §3):** `APPROVED_EXACT_FIXTURES` (26 cặp — 8
   vòng 6.1 + 18 mới v11 §5.2, expected record viết tường minh) +
   `inventory.explain_exact_fixture()` duyệt ở MỨC NHÓM: đúng cặp NFC-lower GIỮ
   dấu thanh + đúng tone + record từng từ khớp; nhóm superset/sai tone/ngoài
   allowlist KHÔNG được duyệt. `MR-I-Y.approved` giữ False (probe v11: bật flag
   sẽ nâng 52 nhóm — 26 ngoài bộ 26). Negative tests trong `test_vi_rules.py`.
5. **`gen_decision_doc.py` chỉ trình bày ledger** quyết reviewer (v11 §6.1 —
   không tự kết luận theo tên rule); helper dấu thanh chỉ nhận 5 dấu thanh
   (huyền/sắc/ngã/hỏi/nặng — v11 §5.4).

Số điều 7: **83 nhóm gate = 26 approved (EXACT_FIXTURE) + 57 proposal
(insufficient evidence) → PENDING_APPROVAL (exit 2)** — còn 57 nhóm là phần
ngôn ngữ chưa đủ bằng chứng, quyết từng nhóm thuộc người duyệt; không đổi định
nghĩa PASS để bỏ qua. Fase C tạm dừng theo yêu cầu v11 §1 (CMUdict đã pin, chưa dùng).

### 10.6 Hậu kiểm v12 → vòng 6.3.1 (02/10/2026 — R12-01 fingerprint approval + R12-02 loss profile + đồng bộ metadata)

Hậu kiểm v12 chấp nhận phần cốt lõi (26 exact fixture, 10 đối lập ach/ec, withdrawn
MR-ACH-EC, phương án nucleus riêng duyệt CÓ ĐIỀU KIỆN), tái hiện hai lỗi tích hợp:

1. **R12-01:** bảng `APPROVED_EXACT_FIXTURES` nằm ngoài cả hai hash đang có
   (mutation bỏ kí/ký → 26/57 thành 25/58 mà hash không đổi). Sửa: thêm
   **`inventory.approval_policy_hash()`** — sha256 gộp điều kiện scope policy +
   nguồn quyết (phân biệt ràng buộc v11 / encoding v12) + catalog RUNTIME đầy đủ
   (cặp, expected record, origin) + source hash helper. Report điều 7 có mục
   `approval_exact_fixture` (hash + n=26 + approved_scope=core_spellings).
   Regression: mutation catalog → hash ĐỔI và gate 26→25; restore → hash gốc.
2. **R12-02:** profile kokoro178 collapse `PHONE_OPEN_E_PREVELAR` về category ɛ
   mà không khai loss. Sửa: `SEGMENT_MAP_KOKORO178["PHONE_OPEN_E_PREVELAR"] = "ɛ"`
   — loss event ghi khi dùng (loss chứa (ID, ɛ, ɛ) — mất đối lập SEMANTIC, kể cả
   khi unicode nhìn như không đổi); profile revision → **kokoro178/0.2**. Regression:
   mách/méc, sách/séc — master khác, export có thể giống (lossy đã chấp thuận),
   loss phải được ghi; sidecar vẫn giữ master ID riêng. Nếu profile sau này tuyên
   bố bắt buộc giữ đối lập này thì phải báo không hỗ trợ, không export im lặng.

Đồng bộ metadata (§7 báo cáo hậu kiểm): inventory in/đọc **ham/0.2** (lịch sử
ham/0.1 giữ trong provenance); `semantic_version` = "ham/0.2" máy đọc + note
riêng; `phase_b_audit.result` cập nhật bằng report v12 (83 = 26 + 57) và snapshot
cũ đưa vào `history`; phân biệt nguồn: ràng buộc giữ đối lập = quyết reviewer
v11 §4, encoding (tên ID, mức nucleus) = lựa chọn tác giả v12 duyệt có điều kiện.

Điều 7 không đổi về số: **83 nhóm = 26 approved + 57 proposal → PENDING_APPROVAL
(exit 2)**. Tests **401 PASS**. Fase C tiếp tục tạm dừng.

### 10.7 QD57-2026-10-02 — quyết định ngôn ngữ 57 nhóm đã áp (vòng 6.4)

Reviewer phán quyết per-group (hồ sơ pin `02_data/collision/qd57/`), chủ dự án
chấp thuận phạm vi cùng ngày:

- **19 fixture exact duyệt mới** (tổng **45 = 26 + 19**) — scope "VI-word nguyên
  dạng": chính âm tiết đã viết theo vi_chinh_ta, giữ thanh; KHÔNG áp cho tên chữ,
  spelling, viết tắt (ny = người yêu), English I/my, phát âm nguyên ngữ tên ngoại.
  Expected record pin trong `qd57/19_fixture_moi.json` (38/38 khớp parser v13).
  ki/ky nay là positive (test negative cũ đã đổi). Rì/rỳ (PHONE_R_VI), iêng/yêng
  (I_SCHWA + NG), si/sì giữ PHONE_S_RETRO, xi/xy giữ PHONE_S.
- **38 nhóm excluded_v1** — KHÔNG duyệt merge, KHÔNG phải approved, KHÔNG phải
  tuyên bố noise: giới hạn bảo đảm đọc v1 ĐÚNG ĐỐI TƯỢNG (subject), phía
  `protected` không bị loại (beo/meo/suê/xuê/tiu/thuê/quới…). Ledger runtime
  `02_data/collision/qd57_scope_exclusions.json` (sha256 pin trong
  domain_config_hash); ranh giới contract: không tự phục hồi dấu, không đổi route,
  không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường
  được phép → trả trạng thái không hỗ trợ có cấu trúc. Word-level:
  `collision_audit.scope_exclusion_status()`. 5 nhóm rút khỏi bucket dự thảo
  (chếc/chếch, iên/yên, iểu/yểu, tíc/tích, ĩ/ỹ) nằm trong 38.
- Audit: gate **83 = 45 approved + 38 excluded_v1 + 0 unresolved → PASS (exit 0)**
  với thống kê tách candidate domain / accepted v1 scope; `approval_policy_hash`
  đổi khỏi `6eee24db…` (catalog 45 + decision_source QD57). Master không đổi
  (ham/0.2); đối lập quới≠cưới đã có ở master và được kiểm giữ nguyên.
- Bộ kiểm sau QD57: **458 test VI · 74 profile · 45 gold-dev · static PASS ·
  21/21 đối chứng**.

### 10.8 vòng 6.5 — R14-01/R14-02 (hậu kiểm v14): boundary scope EXACT + fingerprint logic scope

Lưu ý đọc: các mục trước 10.7 giữ số liệu LỊCH SỬ của từng vòng (PENDING_APPROVAL,
26 cặp…) — KHÔNG phải trạng thái hiện hành; hiện hành là 10.7 + mục này.

- **R14-01** (`collision_audit.py`): `scope_exclusion_status()` so khớp EXACT
  NFC+lower GIỮ dấu thanh trên thành viên máy đọc `excluded_members`/
  `protected_members` trong ledger (pin từ đáp án reviewer
  `qd57/scope_expected_members_qd57.json`, sha256 `376c018b…`) — hết lỗi tìm
  chuỗi con trong văn xuôi `protected` (chếc⊂chếch, níc⊂ních, tíc⊂tích từng lọt).
  39 subject → trạng thái có cấu trúc; 37 protected → None; uppercase/NFD cùng
  kết quả; tue/tuê cả hai phía excluded. `load_scope_exclusions()` validate
  thành viên phủ đúng pair + cross-check đáp án pin (lệch → SystemExit).
- **Kiểm boundary trong audit** (`scope_boundary_check()`): đủ 76 thành viên qua
  API thực chạy; lệch → FAIL exit≠0 — hết PASS dựa riêng vào nhãn ledger
  (`compute_status` nhận `scope_fail`).
- **R14-02**: `scope_policy_hash()` = ledger bytes + đáp án thành viên pin +
  source hash `_member_sets`/`load_scope_exclusions`/`scope_exclusion_status`/
  `scope_boundary_check`; ghi vào report (`scope_exclusions_v1.scope_policy_hash`)
  và gộp vào `domain_config_hash`. Mutation probe `01_g2p/test_scope_policy.py`
  (bản sao sandbox, subprocess): M1 subject đi qua / M2 protected bị chặn /
  M3 đổi ledger → audit KHÔNG PASS + hash đổi; khôi phục → hash về cũ; **16/16 PASS**.
- Renderer đồng bộ (hậu kiểm v14 §5): `gen_decision_doc.py` + `gen_rule_scope.py`
  sinh lại theo report hiện hành (45 approved + 38 excluded_v1 + 12 dissolved +
  0 pending; bảng rule vòng 6.2 giữ nhãn lịch sử); provenance
  `merge_rules_approved_note` sửa "26 cặp" → 45 exact + 38 excluded_v1.
- Bộ kiểm sau vòng 6.5: **466 test VI · 74 profile · 16 mutation probe · 45
  gold-dev · static PASS · 21/21 đối chứng · audit PASS exit 0**.

## 11. Fase C — nhánh en: CMUdict pin → master (ngay sau CHOT_FASE_B_V15)

Lưu ý đọc: mục 11 bổ sung NHÁNH en, không đổi bất kỳ điều gì ở mục 10 (VI hiện
hành): master ham/0.2, `domain_config_hash` `8d46700f…`, `approval_policy_hash`
`46659a0c…`, audit 83 nhóm — tất cả giữ nguyên.

- **Nguồn pin:** `03_vendor/cmudict/cmudict.dict` sha256 `81917843…`, commit
  `7479086`, BSD-2 (`cmudict_provenance.json`); loader `cmu_en.verify_pin()`
  kiểm sha lúc nạp — lệch pin → SystemExit (fail-closed).
- **Map ARPABET → master** (`01_g2p/cmu_en.py`): 15 nguyên âm + 24 phụ âm của
  dict (69 token gồm stress digit) phủ hết qua `VOWEL_MAP`/`CONSONANT_MAP` +
  rule AH0→PHONE_SCHWA / AH1-2→PHONE_AH · ER0→PHONE_ER / ER1-2→PHONE_ER_STRESS
  (A3 vòng 3). Stress digit 1/2/0 → STRESS_PRIMARY/SECONDARY/unstressed.
  `selfcheck()` quét mọi ký hiệu trong dict — thiếu map báo lỗi (probe M2).
- **Record:** `pronounce(word)` → `EnWordResult`: status `ok` (list[EnSyllable]
  qua `syllabify` maxonset_v1 — heuristic cắt âm tiết, chuỗi master phẳng không
  đổi theo cách cắt), `spell` (OOV → tên chữ a-z từ `LETTER_NAMES` pin; ký tự
  không tên liệt kê `unsupported_chars`, không âm thầm bỏ), `no_nucleus`
  (hmm/psst — không bịa nucleus). Mục từ đa biến thể: entry ĐẦU là mặc định
  (vd record verb R AH0 K AO1 R D), alternate giữ trong loader.
- **Fingerprint (R14-02 discipline):** `en_policy_hash` = sha256{cmudict_sha,
  arpabet_map, letter_names, syllabify_rule, code_sha256(cmu_en.py)} — đổi
  bảng/luật/code → đổi; khôi phục → về baseline. Mutation probe
  `test_cmu_en.py` G7: M1 đổi đích map AA→AE (hash đổi), M2 bỏ AO (selfcheck
  đỏ + hash đổi), M3 provenance pin hỏng (SystemExit); khôi phục về baseline.
- **Coverage route-en** (`cmu_coverage.py` → `02_data/en_branch/`): token
  literal NGUYÊN DẠNG (cat=word route=en, NFC+lower+strip; 1.851 token rỗng
  bị loại có đếm) — mẫu số tần suất = 3.040.018 token KHÔNG RỖNG.
  **93.589 unique → 50.504 dictionary hit = 53,96% unique / 96,56% freq**
  (nhãn "dictionary hit" — gồm 7 key no_nucleus như shh/hmm, KHÔNG đồng nghĩa
  phát âm hoàn tất). Miss tách 4 nhóm (hậu kiểm v16 C16-02): ascii_alpha_oov
  33.851 unique / 59.038 freq = 1,94% (nhóm DUY NHẤT spell trọn token bằng
  tên chữ a-z), unicode_alpha_oov 620 / 3.213 = 0,11% (có ký tự ngoài a-z →
  không đảm bảo spell trọn — vào unsupported_chars), has_digit 3.088 / 6.894
  = 0,23%, not_alpha 5.526 / 35.478 = 1,17%. TSV pin header prefix `@@`
  (token thật có dạng bắt đầu `#`). Số khảo sát cũ 58,3%/97,9% đo bằng đơn vị
  khác không tái lập — không dùng đối chiếu; con số "alpha_oov 34.471 /
  0,66%" của v16 gộp nhầm hai nhóm alphabetic và sai mẫu số — đã sửa.
- **Content-pin corpus (C16-02):** `cmu_coverage.py` tính sha256 corpus tại
  MỖI lần chạy (stream) và đối chiếu pin trong
  `core_domain_provenance.json` (`cb9df5eb…`) — lệch → SystemExit; hash đã
  kiểm ghi `corpus.sha256_verified_at_run` + `corpus.pin_source` trong
  `en_coverage_provenance.json` (không chép hash lịch sử).
- **Recipe tái lập vendor (C16-01):** `03_vendor/cmudict/fetch_cmudict.py`
  tải đúng 2 file (dict + LICENSE) tại commit pin `7479086`, kiểm sha256
  đối chiếu `cmudict_provenance.json` trước khi ghi — lệch pin không ghi
  file; provenance không bao giờ bị script tự sửa/nâng revision.
- **Profile:** EnSyllable qua `transform_en` (ˈ/ˌ trước nucleus) — gold words
  conformance vocab 178 (I2).
- **Bộ kiểm fase C:** `test_cmu_en.py` **47/47 PASS** (thêm G8 corpus-pin +
  taxonomy, G9 phân loại miss qqz/á/ít/digit — C16-02); VI không đổi: 466 test
  VI · 74 profile · 16 mutation probe · 45 gold-dev · static PASS · audit
  PASS exit 0.

## 12. Fase D — tầng tiêu thụ g2p/0.1 (v21 sau HAU_KIEM_FASE_D_V20)

Lưu ý đọc: mục 12 bổ sung TẦNG TIÊU THỤ, không đổi master (ham/0.2) hay bất kỳ
policy nào của mục 10-11: domain/scope/approval/en_policy hash giữ nguyên.

- **Lõi:** `01_g2p/g2p.py` — envelope IR ir/0.1 → record g2p/0.1 (schema
  `02_data/g2p/schema_g2p_0.1.md`). Tiêu thụ đủ hợp đồng
  `00_docs/G2P_00_hop_dong_dau_vao.md`: verbal/route/cat/read/break/intonation/
  origin giữ nguyên; punct → `control` im lặng giữ break; number/abbr/unit…
  tiêu thụ read unit tầng 1 đã cấp; contract check shape/version/field +
  read_string theo ranh giới mảnh chữ-số (bắt thừa/thiếu/sai thứ tự; bất khả
  tri punct renderer tầng 1) → `contract_errors`; malformed IR (null/[]/
  tokens[null]/cat[]/break{}) → lỗi cấu trúc, CLI exit 1 JSON không traceback.
- **`read="spell"` được thực thi** (v19 §3.1 + v20 D20-02): en → per-letter
  LETTER_NAMES ("US"→you-ess, "A"→EY primary — dictionary hit không bỏ qua
  mode); route ngoài {vi,en} → `unknown_route` fail-loud ĐỐI XỨNG cả hai mode
  word/spell; vi → tier-1 đã spell-out, unit đơn chữ đi seed spell_vi (chờ
  duyệt). Delegate tier-1 chứng minh bằng fixture verbal THẬT
  `02_data/g2p/fixture_tier1_email_spell.json` (email read=spell route=vi —
  ir_sha256 tự khai; unit ngoài khả năng → unresolved, không bịa).
- **Serializer master:** `master.read_units[]` record đầy đủ + leaf identity
  (source_token_id, read_unit_index — PHÂN BIỆT từng unit, syllable_index);
  profile kokoro178 = nhánh profile_debug (debug_only).
- **D18-01 (ĐÓNG v19):** scope kiểm input + ứng viên fold (nic/tic chặn).
- **Invariant (D18-03 + v19 §4):** unit cấm phát âm ⇒ không syllables;
  aggregate parent/child — status/read_complete/unsupported_chars parent
  PHẢI khớp derive từ units (fault "parent complete, child incomplete" bị
  BẮT + serializer TỪ CHỐI); spell không sinh reading ⇒ unresolved.
- **Fingerprint (D18-04 + v19 §5 + v20 D20-01):** `g2p_policy_hash` v0.2 =
  code g2p + snapshot fold/spell (cache-aware) + cmudict + scope ledger +
  inventory hashes + **b_c_dependencies (4 hash B/C hiệu lực — mutation
  cmu_en đổi hash D)**; snapshot cache khuôn {tab, sha256} đã kiểm pin cho
  CẢ fold và spell — mọi giá trị identity là **str sha256** (không phải bảng
  đã parse), `g2p_policy_hash()` cold == warm trong cùng process; mutation
  đĩa sau warm-load không lệch identity khỏi reading đang dùng (H9-M5 thật
  cả hai bảng); override test-only bắt buộc đánh dấu `resource_override`;
  load_fold/load_spell_vi kiểm sha pins fail-closed. Nguồn fold khai thực
  `02_data/fold/fold_provenance.md`; spell_vi = seed_pending_owner.
- **Vocab từ master:** emit_vocab_config.py 78 entry — inventory.audit()
  trước khi ghi (fail-closed, dup-ID probe không ghi).
- **Bộ kiểm fase D/E:** `test_g2p.py` **115 PASS / 0 FAIL** trên máy có corpus
  (111 PASS + 1 SKIP H11 khi thiếu corpus; v22 thêm: H8 3 trường snapshot
  str==pin + cold==warm, H5 4 ca route×mode đối xứng, H5 D20-04a fixture
  tier-1 3 check, H9-M5 thật warm→mutation→stream lại cả fold và spell, H12
  torture: "A"×100 spell / TRTRTR / token 10.000 ký tự / 150 token cat hỗn
  hợp — 0 crash, serialize được, <5s).
  H11 smoke corpus tùy chọn — SKIP tường minh khi thiếu corpus;
  contract_errors trên corpus chỉ được là nhóm read_string-consensus ~1,2%
  envelope tier-1 picked≠tokens (quy ước case nguyên văn — schema §9) —
  consensus báo đúng. VI không đổi: 466 · 74 · 16 · 45 gold-dev · static
  PASS · audit exit 0 · test_cmu_en 47/47 · 8 artifact tái sinh byte-giữ.

**v23 — preflight + vét cạn (script reviewer adopt, chạy thật máy tác giả):**
`preflight.sh` (gốc repo) + `01_g2p/exhaustive_sweep.py` của reviewer —
byte-chính xác (sha `8b8b821d…` / `3d7617fd…`). Preflight = 10 kiểm tra
song song 1 lệnh (chuỗi B/C/D + test_g2p + vét cạn + probe reviewer) —
**10/10 PASS trong 3s** trên i9-12900K 16 worker (probe = bộ v20, mới nhất
nhận được). Vét cạn toàn không gian khóa tầng 2, không lấy mẫu:
**126.932 khóa / 0 vi phạm / 0,65s / identity_stable** (698 fold + 28 spell
+ 76 scope×3 + 78 inventory + 126.052 cmudict; policy hash a24db1ab…
trước==sau). E4 chuẩn bị xong: `fase_e_judge_sample.py` sinh phiên chấm
mù 500 item (seed 20261002, A/B cân bằng 248/500, khóa riêng, đề bài ghi
quy ước dấu nhấn ˈˌ — judge không chấm). Tiêu chí E4 (7 điều) + E6 (5 điều)
reviewer chốt lưu §6 kế hoạch E. Còn: E4 session cùng chủ dự án, E6 pin
revision checkpoint.

**v24 — E4 chạy thật + spot-check (judge không đủ tin cậy — lưu hồ sơ):**
Phiên 9B theo runbook reviewer: NF4/batch24/greedy/seed 20261002, provenance
sha 11 file model + prompt sha; 2 phiên (v1 stress nguyên — judge fixación
dấu nhấn, lưu *_v1; v2 strip ˈˌ cả 2 phía theo quy ước E3 — chốt). v2: hoa
268 / ca_hai_sai 155 / B 41 / A 36; parse 490+10+0 (đính chính v25 — số 485+15+0 dán nhầm từ phiên v1); regression 186/500 net
→ **candidate flags** sau spot-check. Spot-check 25 phiếu bởi agent (LLM)
theo ủy quyền chủ dự án (caveat minh bạch): **14/25 ĐẠT · 11/25 KHÔNG ĐẠT →
judge KHÔNG đủ tin cậy làm người phân xử**; mọi phiếu KHÔNG ĐẠT là lỗi phía
judge; không phát hiện lỗi G2P mới (đúng điều kiện 5). Bằng chứng: identity
25/25, CMUdict 4/4, NFD audit (chuỗi probe tự dựng của agent thiếu dấu — hệ
đúng 14/14 chuỗi NFD → không bug thanh). Policy [B] thêm 1 mục: token
không dấu ('tiêu','Bây') đọc ngang — fold chờ chủ dự án. E6: đề xuất pin
`9f210d62…` (Apache-2.0, sha LFS đủ) chờ chốt.

**v25 — PHÁN QUYẾT E4 ĐẠT/khép (reviewer tái lập độc lập 7/7 điều kiện); 2 đính chính văn bản:** Nit v24-01 (số parse v2 đúng = 490/10/0/186,2s — 485/15/0/210s là số v1 dán nhầm); Nit v24-02 (literal 'batch=12' trong provenance = template lỗi — batch thực thi 24; runner nội suy từ v25; provenance phiên KHÔNG sửa lén — đính chính tại fase_e_judge_provenance_dinh_chinh.md). E6: reviewer verify sống HF — pin 9f210d62… khớp 100% size+LFS sha; chờ chủ dự án chốt revision/giọng/license.
