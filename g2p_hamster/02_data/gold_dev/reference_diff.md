# Nhật ký sửa reference gold-dev — phân biệt sửa-lỗi-gõ với đổi-đáp-theo-hệ

> **Trạng thái của tài liệu này: NHẬT KÝ TÁI DỰNG; CHƯA ĐỐI CHIẾU ĐẦY ĐỦ VỚI SNAPSHOT
> CÁC PHIÊN BẢN CŨ** (nhãn theo yêu cầu người duyệt 02/10 vòng 3). Không còn file cũ
> trong workspace nên các mục v1–v3 dưới đây là tái lập từ ghi chú, KHÔNG phải bằng
> chứng lịch sử — nhận định "v1 không có lỗi parser" cũng chưa thể xác nhận chỉ bằng
> nhật ký này. Từ v4 bắt đầu lưu snapshot hash; source của sự thật cho reference
> hiện tại là `01_g2p/gold_dev_check.py` (bảng REFERENCE) và TSV do nó sinh ra.

## v1 — 01/10/2026 (lần đầu; tái dựng)

- 26 từ chẩn đoán theo bảng fixture của người duyệt. Lỗi của TÔI (người viết reference):
  `s` ghi PHONE_S thay vì PHONE_S_RETRO; `khoét` ghi onset K thay vì KH; `mắc`/`khắc`
  gán tone TONE_NANG trong khi ký tự gõ là `ắ` (SẮC) — parser trả SẮC, tôi kết luận
  sai là "parser/lỗi gõ" thay vì xem lại reference.
- 4 bất đồng → tất cả là lỗi reference, KHÔNG có lỗi parser trong nhóm này
  (tái dựng — chưa có snapshot v1 để đối chiếu).

## v2 — 01/10/2026 (SUY DIỄN SAI — đã khôi phục)

- Sau "sửa", tôi đổi ký tự `mắc`/`khắc` sang `ặ` (NẶNG) cho khớp kỳ vọng nặng —
  **đây là kiểu đổi-đáp-theo-hệ bị cấm**: `ắ` (sắc) và `ặ` (nặng) là HAI chữ khác
  nhau; fixture `mắc`/`khắc` đích là thanh SẮC để ba chuỗi kiểm khác nhau ở
  SEGMENT, không phải nhờ tone.
- Đồng thời vá `W_OK["Ê"]` thêm coda t để "khoét"(ê) parse được — **sai bảng**
  (người duyệt xác nhận 02/10: khoét có É, vần oet).

## v3 — 02/10/2026 vòng 1 (sửa theo duyệt)

- Khôi phục `khoét` = é (vần `oe`), revert vá `W_OK["Ê"]` — sửa lỗi bảng, hợp lệ.
- Nhưng giữ nhầm `mắc`/`khắc` = nặng (diễn giải trong báo cáo cũng sai: "gõ nhầm
  sắc thay vì nặng" — NGƯỢC lại; mắc/khắc là SẮC, mặc/khặc mới là nặng).

## v4 — 02/10/2026 vòng 2 (hiện tại, sửa theo duyệt vòng 2)

- `mắc` = `m\u1eafc` (ắ, U+1EAF) + **TONE_SAC**; `khắc` = `kh\u1eafc` + **TONE_SAC** —
  khôi phục đúng fixture. Ba từ `mác/mách/mắc` và `khác/khách/khắc` đều SẮC.
- Thêm kiểm **segment-bỏ-tone** (`SEGMENT_CONTRAST_SETS`): các bộ đối lập phải phân
  biệt được ở mức segment IDs, nếu hai chuỗi chỉ khác nhờ tone thì báo bất đồng.
- Thêm bộ kiểm `ke/que`, `kê/quê`, `que/quê` với expectation ĐẦY ĐỦ gồm glide:
  `que = K + W(glide) + OPEN_E + NGANG`, `quê = K + W + E + NGANG`, `ke = K + OPEN_E`
  (không glide), `kê = K + E` (không glide).
- Sửa lại nhận xét trong báo cáo gửi duyệt: "que mất glide" là lỗi DIỄN GIẢI của
  tôi trong tin nhắn — parser và reference từ đầu đã có PHONE_W cho que
  (kiểm: `gold_dev_check.py` hàng que, cột glide = PHONE_W).

## Tổng kết phân loại

| Thay đổi | Loại | Trạng thái |
|---|---|---|
| s→PHONE_S_RETRO, khoét→KH (v1) | sửa lỗi gõ reference | hợp lệ |
| mắc/khắc nặng (v2) | **đổi đáp theo hệ** | ĐÃ KHÔI PHỤC sang sắc (v4) |
| W_OK["Ê"] + "t" (v2) | **sửa sai bảng** cho test xanh | ĐÃ REVERT (v3) |
| khoét = é (v3) | sửa theo duyệt (người duyệt có cơ sở độc lập) | hợp lệ |
| mắc/khắc = SẮC + kiểm segment-bỏ-tone (v4) | sửa theo duyệt vòng 2 | hợp lệ |
| ke/que/kê/quê full expectation (v4) | bổ sung bộ kiểm theo yêu cầu | hợp lệ |

## v4.1 — 02/10/2026 vòng 3 (theo duyệt)

- Gỡ duyệt `MR-tai-tay` (approved=false trong `01_g2p/inventory.py`): yêu cầu lịch sử
  là đối lập bắt buộc tai ≠ tay, không phải cơ sở duyệt rule fold. Không đụng reference
  TSV — kiểm tai≠tay vẫn đi qua `SYLLABLE_LEVEL_CONTRASTS` + `SEGMENT_CONTRAST_SETS`
  (phân biệt nhờ COND_NUC A_SHORT, không nhờ rule fold nào).

## v5 — 02/10/2026 vòng 4 (mở rộng theo báo cáo kiểm code reviewer)

Reference MỞ RỘNG 28 → 45 từ, viết TRƯỚC khi chạy parser (cùng nguyên tắc v1):

- **gi-family (F02):** gì (GI+I), gìn (GI+I+N — chữ i của "gi" DÙNG CHUNG onset và
  nguyên âm: "gìn" = g,ì,n 3 ký tự), giêng/giếng/giết (gi+ê → vần iê = GI+I_SCHWA —
  phục hồi nguyên âm đôi mất trước vá), gia (i thuộc onset → A_LONG, KHÔNG phải
  ia/I_SCHWA), giọng (OPEN_O+NG), giỗ (PHONE_O, ngã).
- **uy/ui (F01):** tui (u+coda j) ≠ tuy (glide w+i); thúi≠thúy; huy; duy (PHONE_Z).
- **vần lõi (F03):** buồm (Uə+m, ồ U+1ED3 = HUYEN theo codepoint), muỗm (Uə+m, ngã),
  khuỷu (uy composite + offglide u; chất thực phát chờ E6).
- Thêm bộ đối lập segment-bỏ-tone: (tui,tuy), (thúi,thúy).
- **Kiểm đối lập trên RECORD PARSER** (public parse()) — vòng cũ so reference với
  reference (self-check); giờ giữ self-check riêng + thêm gate record (§5.2 reviewer).
- Lỗi reference bị checker bắt trong vòng này: `buồm` ghi PHONE_B thay vì
  **PHONE_B_IMP** (A1) — sửa reference, hợp lệ.
- Wording: bỏ nói "duyệt 02/10" cho phân tích ach=/ɛk — chỉ yêu cầu BẢO TOÀN ba đối
  lập được duyệt; lựa chọn biểu diễn toàn miền là đề xuất chờ kiểm chứng.

## v6 — 02/10/2026 vòng 5 (review v5: V5-01…05 + A3-01…04)

**Reference gold KHÔNG đổi** — vòng này chỉ sửa code (renderer gi, core classifier,
matcher engine, runner test, profile sidecar/enum). Các ghi nhận liên quan reference:

- Gold checker vẫn 45 từ / 0 bất đồng trên parser đã vá renderer — các hàng gi
  (gì/gìn/giêng/giết…) giữ nguyên, KHÔNG sửa reference cho khớp renderer (đúng
  yêu cầu "không sửa reference gi vừa đúng để phù hợp renderer sai").
- Kiểm hai chiều MỚI ở unit test: word → parts → render → parse phải ra cùng record
  trên 25 từ thật gồm cả họ gi (`test_renderer_roundtrip`) — renderer trước đây
  viết "giìn"/"giiết" bị bắt bởi test này.
- Kiểm miền core MỚI tường minh (V5-01): 27 từ thật phải thuộc core
  (yên/yến/quyên/quyết/mây/cây/đấy/nghe/buồm/gìn/giết/tuy/…), 18 tổ hợp phải bị
  loại (nge/ngê/ghá/cê/ka/mỹa/ak/tym/tyên/coa/koa/…); sai → FAIL trong collision
  audit (mục `core_acceptance` của dieu7_bao_cao.json).

## Snapshot hash v4 (đã thay bởi v5 — giữ làm lịch sử)

```
b96520c046a1ed5d5179637247509f512bb4d619960377bc7eebae1ff5fdef01  01_g2p/vi_rules.py
ed311ca90cf2ed0ba9b0f4302885449ac14477056e27116fd04328f3b2fcdbc8  01_g2p/vi_syllable.py
e418ebe04740687a818020fb52997500f472b90d8d2820688ae042ba1a8b50cd  01_g2p/inventory.py
fd4a7324fdf66044f399a323c07b9ea8964ad56a7d082fa7cc8646e4572b4398  01_g2p/collision_audit.py
37654541258c6b83c58ac9d4972fcc9c96fd0c78a1d7689b647036d7ed50030d  01_g2p/test_vi_rules.py
ff65d76a23b194a513f9e563790f6dfd3c1b3400fd4e46a0c75cc92a08ac577f  01_g2p/gold_dev_check.py
390825c6f2d2fe7b2b67553d0671fda61b2a6918593a6d8a468702c08a14aabe  02_data/gold_dev/gold_vi_reference.tsv
7a4003d53f7df92f9246536990f3d3024cd5b2dc87cd548427a543a53956cecf  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
```

## Snapshot hash v5 (vòng 4 — đã bị v6 thay; reviewer đã kiểm bản này và báo V5-01…05)

```
0d037a571277ac0628bf21d93dd42bbca10b7d4ce5682e34fe5e88deb105c3f7  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
e5fff7231fe5e01b90b14a0bd60199f95ca31e254b265fc19bcac01f51f5668d  01_g2p/inventory.py
4cda2773b83673e843ed9c6f6d69b5f2eef61c6271a46ee7ce151ddf011bb902  01_g2p/collision_audit.py
431916e1f5703c2d02964e180eb7ab5c4046deba5d99ac72158ed2f814d1c0b1  01_g2p/test_vi_rules.py
11cbe3008aab138df69e59e8aaedaa79821130e6e566c702a65bf0aa6b66635e  01_g2p/gold_dev_check.py
99634416ebc685e22e7bbe5226d25ffbec2cad603a34df26a9501aecc13b6b75  01_g2p/profiles.py
aa8872e6be6f7fdc5aceb8f5f2ebe62f454f1716077b6c8b555c64a70238325e  01_g2p/test_coda_tone_mapper.py
09301d4a4abb9b81e05a5a982c173821ac1622101564180604cd08f0d461f25c  02_data/gold_dev/gold_vi_reference.tsv
69fc813542a4b64f2fbdec0c9b0c501d73bf0dae2d9852c5177a8d22be00100e  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
```

## v7 — 02/10/2026 vòng 6 (căn cứ miền core attestation — review vòng 6 §9)

Reference gold **KHÔNG đổi** — vòng này không đụng REFERENCE, chỉ thêm căn cứ miền
độc lập cho điều 7 (reviewer: "căn cứ miền core... có nguồn và phiên bản"):

- `02_data/core_domain/vi_syllable_vocab.tsv` (MỚI, pin): 124.934 âm tiết tần suất
  từ corpus IR tầng 1 (`corpus_ir_1M.jsonl.gz` + supplement — NGUỒN ngoài G2P,
  sha256 trong `core_domain_provenance.json`); sinh bằng `build_core_domain.py`,
  KHÔNG lọc theo parser.
- `collision_audit.py`: core = is_core(ngữ cảnh) ∩ attested(freq≥2); lớp **ext**
  (core-ngữ-cảnh nhưng không attested — miền mở rộng, KHÔNG gate, KHÔNG đòi duyệt
  đồng âm); gate chỉ còn nhóm ≥2 core-attested: 2.776 → **98 nhóm**; domain
  regression (câi/mấi/bêo/buâi/buây/gii phải ngoài core-attested; cây/mấy/bêu…
  phải core) — vi phạm → FAIL; markdown có dòng **Status:** tổng thể (§8.1).
- README/schema sửa đuôi hash trình bày `817d74be…f1d2` → `817d74be…d8d2` (§8.2 —
  hash runtime không đổi, xác nhận bằng chính inventory.py in ra).
- `rule_scope_vong6.md` (MỚI): bảng đối tượng gate attested + freq từng thành viên
  + đề xuất scope từng rule cho người duyệt — KHÔNG rule nào bật approved.

## Snapshot hash v6 (vòng 5 — đã bị v7 thay; reviewer đã kiểm bản này: chấp nhận
## bản vá kỹ thuật, chưa nghiệm thu B)

```
7657a5b379356fb3afa06ec8267169e3e2f17fd6c32fd200f3dec3e87c870f83  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
a55210523de35dd51e3d76e389bd396dff2765334b82f42af9f31fef0a7f1415  01_g2p/inventory.py
e87402d753b92804a433d52fc759872a0186958c683784214bd8616996249729  01_g2p/collision_audit.py
d0391b1e1642d148ba9a7f0a5b7db1d6b834b15e85c460506b30dc00bbe0136e  01_g2p/test_vi_rules.py
11cbe3008aab138df69e59e8aaedaa79821130e6e566c702a65bf0aa6b66635e  01_g2p/gold_dev_check.py
3c36268ebf5b8f1129201f8ad65149cbe4e82fb7ebfd03da87c6a6400337af25  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
09301d4a4abb9b81e05a5a982c173821ac1622101564180604cd08f0d461f25c  02_data/gold_dev/gold_vi_reference.tsv
eaf4df552aea6e1f0d8c4b5059792f8641521f6dcb7b7509a0b0c81d42a7fcbf  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
```

## v8 — 02/10/2026 vòng 6.1 (attestation = lớp bằng chứng, không thay thẩm định chính tả)

Reference gold **KHÔNG đổi**. Điều chỉnh theo 5 điểm reviewer nêu trên nhật ký v7:

- Tên gọi "dạng token" (124.932) — kết quả chỉ dừng ở "audit trên miền ứng viên có
  chứng thực corpus phiên bản pin, ngưỡng tần suất 2"; `domain_scope_statement`
  ghi tường minh trong report điều 7.
- Nguồn attestation = chỉ corpus chính 1M; supplement edge-case 108 records LOẠI
  (sha256 + kiểm 0 hit từ chẩn đoán gold trong provenance; `field_spec` chi tiết).
- Nhóm ngoài gate lưu dấu ĐẦY ĐỦ: `dieu7_ext_groups.jsonl` + 
  `dieu7_stress_groups.jsonl` — thu hẹp gate ≠ giải quyết ngôn ngữ.
- `domain_config_hash` pin hành vi miền (TSV + builder + ngưỡng + list regression).
- Số gate không đổi (98); tests 295 → 298 PASS (thêm 3 kiểm provenance/pin).

## Snapshot hash v7 (vòng 6 — đã bị v8 thay; reviewer chưa kiểm trực tiếp bản này)

```
7657a5b379356fb3afa06ec8267169e3e2f17fd6c32fd200f3dec3e87c870f83  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
a55210523de35dd51e3d76e389bd396dff2765334b82f42af9f31fef0a7f1415  01_g2p/inventory.py
d123754bc5b2f193d75f8e96542560c9af7fb305a997037c30dbb37af4c02c25  01_g2p/collision_audit.py
1ac6bb5aeeb6c520904d54df5c7cc38dd98dfa1c1cbe05c7c66a59731c424047  01_g2p/test_vi_rules.py
11cbe3008aab138df69e59e8aaedaa79821130e6e566c702a65bf0aa6b66635e  01_g2p/gold_dev_check.py
3c36268ebf5b8f1129201f8ad65149cbe4e82fb7ebfd03da87c6a6400337af25  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
a52822d823ec03d0f28ed753409fbb59074c9ffaa29ace4c7ab0d9abb0740711  01_g2p/build_core_domain.py
09301d4a4abb9b81e05a5a982c173821ac1622101564180604cd08f0d461f25c  02_data/gold_dev/gold_vi_reference.tsv
47c50928222a39d6b7d704b5ac295edacd56848b8b14af4982bb8c2ffbf8dfea  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
66a7a6873fa977dbfb064076cbd69cdd6206a72e5085e8c4ea01d9ea185000de  02_data/core_domain/vi_syllable_vocab.tsv
55144be932bfbd8bfaeb0a50226e5e82284e03b29fc8e3363892d5b4eb0e6efd  02_data/core_domain/core_domain_provenance.json
2bcd01d454466fa4f1a087204abcd489e7c772861421e7010ec4e030da6e94e6  02_data/core_domain/rule_scope_vong6.md
```

## v9 — 02/10/2026 vòng 6.2 (sửa R61-01/02/03: đếm literal, hash phủ classifier, scope doc sinh tự động)

Review trên source/artifact thật của gói v8: 23/23 hash khớp, tái lập được 98 nhóm,
nhưng phát hiện ba lỗi — sửa tập trung theo đúng bước reviewer chỉ (builder →
fingerprint → scope doc), không đụng G2P/gold/ca đã đóng:

- **R61-01 (cao):** builder tách token theo số dấu thanh (không phải phân tích âm
  tiết) — corpus tổng hợp `lựchọc`×2 sinh freq `lựch`=2 giả, đùn gate lực/lựch.
  Sửa: đếm **token nguyên dạng literal** (không tách, không strip_tone/parse,
  builder không import parser). Rebuild: `lựch`, `ếc`, `họct`,
  `thànhph` = 0 literal; `lệc` 2→1 (dưới ngưỡng) — ba nhóm lực/lựch, lệc/lệch,
  ếc/ếch rời gate (chú thích v9 gõ nhầm lẹc/lệc — đã sửa). Fixture synthetic chặn
  hồi quy trong `test_vi_rules.py`.
- **R61-02 (TB):** `domain_config_hash` không phủ classifier (mutation bảng → gate
  98→107, hash giữ nguyên). Sửa: hash gộp snapshot RUNTIME của
  CORE_ONSET_FIRST/CORE_TAILS + source hash các hàm phân lớp + hash module
  vi_rules/vi_syllable. Test xác nhận mutation → hash đổi.
- **R61-03 (TB):** scope doc lệch artifact (`cảo/cấu` thay vì `cấo/cấu`; "I_SCHWA"
  thay vì PHONE_I; freq stale; "compose cần ≥2 rule" sai). Sửa: `gen_rule_scope.py`
  sinh tự động `rule_scope_vong6.md` từ JSON pin — hết số liệu tay; câu compose
  thành "trace dùng nhiều rule — chưa chứng minh tập tối thiểu".
- Thêm `trace_vocab_members.py` → `gate_member_trace.jsonl` (210 dạng gate: record
  locator + ngữ cảnh ±3 token; đếm khớp TSV 100%).
- 8 cặp i/y reviewer XÁC NHẬN (kí/ký, lí/lý, kì/kỳ, kĩ/kỹ, mĩ/mỹ, sĩ/sỹ, tỉ/tỷ,
  qui/quy) vào `test_vi_rules.py` ở mức fixture, expected record viết tường minh.
- Số gate sau rebuild literal: **95** = 0 approved + 95 proposal + 0 identity +
  0 unexplained (báo trung thực, không giữ 98) · ext 4.997 · stress-only 1.552 ·
  PENDING_APPROVAL (exit 2); `domain_config_hash` mới `5d0e89f5…87ad2`; tests
  **332 PASS**; gold-dev 45 từ 0 bất đồng (reference KHÔNG đổi).

## Snapshot hash v8 (vòng 6.1 — đã bị v9 thay; reviewer đã kiểm bản này: tái lập được 98 nhóm, phát hiện R61-01/02/03)

```
7657a5b379356fb3afa06ec8267169e3e2f17fd6c32fd200f3dec3e87c870f83  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
a55210523de35dd51e3d76e389bd396dff2765334b82f42af9f31fef0a7f1415  01_g2p/inventory.py
27e3d3fba62c1d58b2fe38475b02c08abadc416b7d8df9377abd5aa8690026d5  01_g2p/collision_audit.py
d2e321e0a892287ad6f8f11f8750436308064527ea7902d0ae9c00d94e9817a4  01_g2p/test_vi_rules.py
11cbe3008aab138df69e59e8aaedaa79821130e6e566c702a65bf0aa6b66635e  01_g2p/gold_dev_check.py
3c36268ebf5b8f1129201f8ad65149cbe4e82fb7ebfd03da87c6a6400337af25  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
f357d5f16ffaae3639aeb799032575836f1a9e6872c1b474e3bec0725d179982  01_g2p/build_core_domain.py
09301d4a4abb9b81e05a5a982c173821ac1622101564180604cd08f0d461f25c  02_data/gold_dev/gold_vi_reference.tsv
90d082eaf5e4abccbe546f3c089e326d74f2f6c5f24308946a70500610fae7df  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
5105d872b597bb6ff10e4a5746c062815546313e42a89e8d6f88419695dc589f  02_data/core_domain/vi_syllable_vocab.tsv
b216768c414cb26795140e9eb88cee028384bd7a7ed8bc3cb283d9b781610624  02_data/core_domain/core_domain_provenance.json
a6f44117d7f4deab5e73be3640f341e0f5f1eca2df7a3ffa3144ba68414acf48  02_data/core_domain/rule_scope_vong6.md
f5c9b2d71bebca055c1c2d0ff07fa4e294deeea3bbfd187fcf64eec8a1de14b0  02_data/collision/dieu7_ext_groups.jsonl
2f0c019fe2d469757b35f245e0addfc7d5933cbfb6af07014b3e12a0ca8f3d71  02_data/collision/dieu7_stress_groups.jsonl
```

## Snapshot hash v9 (vòng 6.2 — đã bị v10 thay; reviewer đã kiểm: chấp nhận R61-01/02/03, chốt vòng vá kỹ thuật)

```
7657a5b379356fb3afa06ec8267169e3e2f17fd6c32fd200f3dec3e87c870f83  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
a55210523de35dd51e3d76e389bd396dff2765334b82f42af9f31fef0a7f1415  01_g2p/inventory.py
1ce1a9c26fb83375d495042b05ace2db92f4a5cbe90eda5014456dc8f6a093c6  01_g2p/collision_audit.py
1743beaa5f56bc45033b23058c51ec3c272067a3867b8066a480ee8ff420c697  01_g2p/test_vi_rules.py
11cbe3008aab138df69e59e8aaedaa79821130e6e566c702a65bf0aa6b66635e  01_g2p/gold_dev_check.py
3c36268ebf5b8f1129201f8ad65149cbe4e82fb7ebfd03da87c6a6400337af25  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
57fcf0c8286c7d45d370c05b49a5ff40d0278e89606b03c1e4442ddc9df010f9  01_g2p/gen_rule_scope.py
ff1aeea946b711b0561d002eb7fe6028cc2dcecbb5ed9513a6e3df73a5cdd7bf  01_g2p/trace_vocab_members.py
09301d4a4abb9b81e05a5a982c173821ac1622101564180604cd08f0d461f25c  02_data/gold_dev/gold_vi_reference.tsv
46731ae357af0291e2dcacf1b6714ada6807664dff5859b2892874cd5f4c268d  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
bf6042ea6ef3196b7119da93249b5549a35aa08c7d172a3beaae304f7c0705ca  02_data/core_domain/rule_scope_vong6.md
ce50d7477e77d28ff57f7662164009ec5b18ada98a610dd4e9c6a33b94915fb8  02_data/collision/dieu7_ext_groups.jsonl
3c58124e7713ca09cda507a67d79a27f5d3d7b4df7d4e78e6c69ff2ed76988c0  02_data/collision/dieu7_stress_groups.jsonl
902e7279b523da0191f862b18b8a4df1faf33ea80304c760f1c46751ac36b649  02_data/collision/gate_member_trace.jsonl
```

## v10 — 02/10/2026 vòng 6.2 hậu kiểm (T62-01 + chỉnh chú thích — vòng vá kỹ thuật CHỐT)

Review v9: **chấp nhận bản sửa R61-01/02/03** (builder literal — replay cũ→mới khớp
toàn bộ 124.932 key; fingerprint bắt được mọi mutation probe; scope doc sinh lại
khớp từng byte). **Vòng vá kỹ thuật chốt**; điều 7 giữ PENDING_APPROVAL. Hai chỉnh
nhỏ, không mở lại lỗi đã đóng:

- **T62-01:** `gate_member_trace.jsonl` ghi `token_index` theo danh sách đã lọc
  thay vì index gốc trong `ir.tokens[]`. Sửa: `trace_vocab_members.py` enumerate
  `ir.tokens[]` nguyên bản, lọc trong vòng lặp, ghi index gốc; ngữ cảnh dựng từ
  `ir.tokens[]` nguyên bản; field `token_index_scope` khai phạm vi. Phép đếm
  KHÔNG đổi — freq vẫn khớp TSV 100%. Test hồi quy
  `test_trace_locator_original_index` (punct[0] + en[1] + 'lực'[2] → trace ghi 2).
- **Chỉnh chú thích lệc/lẹc:** chú thích trước ghi "lựch, lẹc, ếc … = 0 literal"
  — đúng theo bảng: `lựch`=0, `ếc`=0, `lệc` 2→1 (dưới ngưỡng, không phải 0;
  `lẹc` không thuộc nhóm cũ nào). Ba nhóm rời gate: lực/lựch, lệc/lệch, ếc/ếch.
  `gen_rule_scope.py` đọc các con số chú thích từ bảng pin lúc sinh (không gõ cứng).

Tests **337 PASS** (332 + 5 locator); gold 45/0; static PASS; profile 74 PASS;
audit 95 nhóm → PENDING_APPROVAL (exit 2). Bước tiếp theo là quyết định NGÔN NGỮ
có phạm vi trên 95 nhóm (ưu tiên cặp từ thật: ach/ec, coda-ch/c), không sửa builder
hay chỉnh ngưỡng.

## Snapshot hash v10 (vòng 6.2 hậu kiểm — đã bị v12 thay; reviewer đã hậu kiểm: đóng T62-01, chốt mốc kỹ thuật)

```
7657a5b379356fb3afa06ec8267169e3e2f17fd6c32fd200f3dec3e87c870f83  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
a55210523de35dd51e3d76e389bd396dff2765334b82f42af9f31fef0a7f1415  01_g2p/inventory.py
1ce1a9c26fb83375d495042b05ace2db92f4a5cbe90eda5014456dc8f6a093c6  01_g2p/collision_audit.py
8e896eaba18b47f6d978621cf96708ff689f2ceb1c06a652ac810f54b38980b2  01_g2p/test_vi_rules.py
11cbe3008aab138df69e59e8aaedaa79821130e6e566c702a65bf0aa6b66635e  01_g2p/gold_dev_check.py
3c36268ebf5b8f1129201f8ad65149cbe4e82fb7ebfd03da87c6a6400337af25  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
a04cea27eee635e612facb1efa37b9e66297905632df10bba906354a8f3d0c3b  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
09301d4a4abb9b81e05a5a982c173821ac1622101564180604cd08f0d461f25c  02_data/gold_dev/gold_vi_reference.tsv
46731ae357af0291e2dcacf1b6714ada6807664dff5859b2892874cd5f4c268d  02_data/collision/dieu7_bao_cao.json
95a6d14284b5e8dd8aad6a4f81ee8da53038d3edb93ac51d161979c9592185fa  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
d8d6be449f029371da44d17b704e807c7e15abadcaba78426bad77e6db1d7ef7  02_data/core_domain/rule_scope_vong6.md
ce50d7477e77d28ff57f7662164009ec5b18ada98a610dd4e9c6a33b94915fb8  02_data/collision/dieu7_ext_groups.jsonl
3c58124e7713ca09cda507a67d79a27f5d3d7b4df7d4e78e6c69ff2ed76988c0  02_data/collision/dieu7_stress_groups.jsonl
3bf502fb21c982e6d3c10531960019467a68fd26e40d6288242a0c2a3fc9686b  02_data/collision/gate_member_trace.jsonl
```

## v12 — 02/10/2026 vòng 6.3 (áp quyết reviewer v11: ham/0.2 + lớp EXACT_FIXTURE + withdrawn MR-ACH-EC)

Reviewer v11 ra phán quyết cụ thể cho đủ 95 nhóm — triển khai đúng scope, không
mở lại lỗi đã đóng:

- **ham/0.2 (thay đổi thiết kế có phiên bản):** thêm `PHONE_OPEN_E_PREVELAR`
  (segment ɛ — vần 'ach'); `PHONE_OPEN_E` bất biến; `SHARED_UNICODE_REPR` khai
  nhóm shared ɛ; registry ổn định, test EN không đổi. Gold-dev mách/khách cập
  nhật theo (nguồn quyết ghi trong note — không "làm lại reference theo output":
  nguồn là quyết reviewer v11 §4).
- **10 cặp ach/ec = đối lập bắt buộc** (`SYLLABLE_LEVEL_CONTRASTS`): sách/séc,
  mách/méc (đối chiếu mục từ độc lập [sajk̟̚] vs [sɛk̚]) + 8 cặp policy bảo toàn
  lớp vần (chưa thẩm định audio từng cặp).
- **`MR-ACH-EC` → withdrawn** (v11 §4.4: KHÔNG DUYỆT — không treo như proposal
  chờ nghe model).
- **Lớp duyệt EXACT_FIXTURE:** 26 cặp i/y đầy đủ dấu (8 cũ + 18 mới v11 §5.2);
  `explain_exact_fixture` duyệt ở mức nhóm — đúng cặp NFC-lower giữ tone + đúng
  tone + record khớp expected; negative tests: ki/ky, sai tone (ký/kĩ), superset,
  1 từ. `MR-I-Y.approved` vẫn False (probe v11: flag rộng nâng 52 nhóm).
- **`gen_decision_doc.py` trình bày ledger reviewer** (không tự kết luận theo tên
  rule — v11 §6.1); helper dấu thanh chỉ nhận 5 dấu thanh (v11 §5.4).
- Kết quả: **83 nhóm gate = 26 approved (EXACT_FIXTURE) + 57 proposal
  (insufficient evidence) → PENDING_APPROVAL (exit 2)**; 12 nhóm ach/ec hết
  collision do thay đổi biểu diễn; tests **393 PASS**; gold 45/0; static PASS;
  profile 74 PASS. Fase C tạm dừng theo yêu cầu v11 §1.

## Snapshot hash v12 (vòng 6.3 — đã bị v13 thay; reviewer đã hậu kiểm: chấp nhận lõi, tái hiện R12-01/02)

```
a40522023143ba2d0bc5e88875ebd34e62fc90f507cbc709a03f08a1684db88c  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1c4cf3cce788a3845d933b566dcf7dd29a401938fde76d7efeac75a742d14130  01_g2p/inventory.py
f5584c9e5f0aa794220aa1c65bafeca36a3f235fde4022c2b01bf5730ef3c686  01_g2p/collision_audit.py
49799feee2e777b664ed499510cdcc5263f02e165f6b80753a4ceb5bd160a940  01_g2p/test_vi_rules.py
e39faf59968c2a81bb17b0411642046b3dd295be34cc01642a6a7c7c7891b82d  01_g2p/gold_dev_check.py
3c36268ebf5b8f1129201f8ad65149cbe4e82fb7ebfd03da87c6a6400337af25  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
017bc23710b2f51a5b802256a2856f7f074cb19de0cd35ce6e96f45eff3c4a86  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
b31d92a9514056d2338ba1c83f65f36c7781a8d6a7381c5ea45cf44506fb532a  01_g2p/gen_decision_doc.py
54091fd2eee023b1e18cd493fe002514d998243bf176a9ba4c48b4696cc23281  02_data/gold_dev/gold_vi_reference.tsv
59213cabe99326c0ca3bcf5dbaf23740927acc55c9b0e945890689adb141d472  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
cf87ee4f8d0b5168d81ac61ba8bb94df2a37b10a5355c6ddf64d59cc21c1a0ef  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
0e8bd736028f0fd96a37fbc85406b009daa4b5d223a96272ab9e02bb494eac1f  02_data/core_domain/rule_scope_vong6.md
1e3f4f5a4f433163ce1990a5b9cc38ef77ff7f2c8949062843762b075f6bcf4f  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
08ae120bcdded47564443cc3b9ada762a2425d234ab771a40e28ac2ac3df35fb  02_data/inventory_provenance.json
58b0cad30ecec61ea8001e86d6a3b6fc98df2cfc4c2ce70ed62d92ebfc7a8c20  02_data/inventory_schema.md
03698d29ed9dba5371e976e071cac51ed21a1c330f730c1bad41ebe409c9ce11  README.md
```

## v13 — 02/10/2026 vòng 6.3.1 (sửa R12-01 fingerprint approval + R12-02 loss profile + đồng bộ metadata)

Hậu kiểm v12: chấp nhận lõi (26 exact fixture, 10 đối lập ach/ec, withdrawn
MR-ACH-EC, nucleus category duyệt có điều kiện); hai lỗi tích hợp mới đã sửa:

- **R12-01:** `APPROVED_EXACT_FIXTURES` nằm ngoài cả `inventory_contract_hash`
  lẫn `domain_config_hash` (mutation bỏ kí/ký: 26/57 → 25/58, hash không đổi).
  Sửa: **`inventory.approval_policy_hash()`** — gộp điều kiện scope policy +
  nguồn quyết (phân biệt v11/v12) + catalog RUNTIME (cặp + expected record +
  origin) + source hash helper. Report điều 7 có mục `approval_exact_fixture`.
  Regression: mutation → hash ĐỔI + gate 26→25; restore → hash gốc.
- **R12-02:** kokoro178 collapse `PHONE_OPEN_E_PREVELAR` về ɛ mà `loss=[]`.
  Sửa: khai map trong `SEGMENT_MAP_KOKORO178` — loss event khi dùng (mất đối lập
  SEMANTIC kể cả unicode ɛ→ɛ); profile revision → **kokoro178/0.2**. Regression:
  mách/méc, sách/séc — master khác, export có thể giống, loss phải ghi; sidecar
  vẫn giữ master ID. Không đổi nghĩa ID cũ, không thêm ký tự ngoài vocab 178.
- **Metadata (§7):** inventory in/đọc ham/0.2; `semantic_version`="ham/0.2" máy
  đọc + note riêng; `phase_b_audit.result` cập nhật (83 = 26 + 57) + snapshot cũ
  vào `history`; phân biệt nguồn: ràng buộc giữ đối lập = v11 §4, encoding =
  lựa chọn tác giả v12 (duyệt có điều kiện).

Kết quả: tests **401 PASS**; gold 45/0; static PASS; profile 74 PASS; điều 7
giữ **83 = 26 approved + 57 proposal → PENDING_APPROVAL (exit 2)**.

## Snapshot hash v13 (hiện tại — sau vòng 6.3.1, sửa R12-01/02 + metadata)

```
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
9ea02e83d9d79d3efba8469d89eaac91c18fca137db92ff612e0eb8e731c4c02  01_g2p/inventory.py
fdcc8042f2f9011a8875b1038ccb632ca23dc30a3d90365505032d024eccfebf  01_g2p/collision_audit.py
8bdf125b2f93b6fd3041a99b7f962a726cafe8d6f34f9784a595919c4b4830f0  01_g2p/test_vi_rules.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
017bc23710b2f51a5b802256a2856f7f074cb19de0cd35ce6e96f45eff3c4a86  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
b31d92a9514056d2338ba1c83f65f36c7781a8d6a7381c5ea45cf44506fb532a  01_g2p/gen_decision_doc.py
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
29c12483b5c2aaade0abc608f54cc9400a4c7d9866f6b9a7cfa49372c0dfd445  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
9fd0cd44aa6d0691c69c325cc677aa6e76dd0de143b229fad9df5ef14d589f75  02_data/core_domain/rule_scope_vong6.md
1e3f4f5a4f433163ce1990a5b9cc38ef77ff7f2c8949062843762b075f6bcf4f  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
ccde3996ea518cb0e466dfd16ca0c79dccbeb85503df65f6b340ca232652d357  02_data/inventory_provenance.json
63718d1674f1517428d816fc811fd24898eb3565c937e8746266b6c112697892  02_data/inventory_schema.md
9889e2b973bc7c8a53de10d804fe04464448176bbf8e0ad34843139cfa7f052e  README.md
```

(hash của chính `reference_diff.md` và của ZIP không tự liệt kê được — lấy từ tin
nhắn gửi kèm gói.)

## v14 — 02/10/2026 vòng 6.4 (QD57-2026-10-02 áp vào runtime: 19 fixture mới + 38 excluded_v1)

Reviewer phán quyết per-group (QD57-2026-10-02, hồ sơ pin `02_data/collision/qd57/`);
chủ dự án chấp thuận phạm vi 19+38. Áp một lượt:

- **19 fixture exact mới** (tổng **45 = 26 + 19**) — scope VI-word nguyên dạng; 3
  nhóm chuyển sang duyệt (rì/rỳ, iêng/yêng, thì/thỳ), 5 nhóm rút khỏi bucket dự
  thảo (chếc/chếch, iên/yên, iểu/yểu, tíc/tích, ĩ/ỹ). ki/ky: negative cũ →
  **positive** (QD57 §6.4). `approval_policy_hash` đổi:
  `6eee24db…` → **`46659a0c…`** (catalog 45 + decision_source QD57).
- **38 nhóm excluded_v1** — ledger runtime `02_data/collision/qd57_scope_exclusions.json`
  (sha256 `b0394cd5…`), pin trong domain_config_hash: `5d0e89f5…(v11) → 6b9fcc95…(v13)
  → **`2ca687ab…`**. Ranh giới contract (không phục hồi dấu/đổi route/ghép tách token;
  protected không bị loại) + `collision_audit.scope_exclusion_status()` cho fase D.
- Audit: **PASS exit 0** — gate 83 = 45 approved + 38 excluded_v1 + 0 unresolved,
  thống kê candidate domain / accepted v1 scope tách riêng trong report
  (`scope_exclusions_v1`). Master ham/0.2 không đổi; quới≠cưới giữ nguyên (test).
- Bộ kiểm: **458 test VI** (từ 401 — thêm kiểm QD57) · 74 profile · 45 gold-dev ·
  static PASS · 21/21 đối chứng. provenance `phase_b_audit.result` cập nhật + history.
- Bảng dự thảo `bang_quyet_dinh_57nhom.md` gắn banner SUPERSEDED (lịch sử).

## Snapshot hash v14 (hiện tại — sau vòng 6.4, QD57 đã áp)

```
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
3041b8cea6d550440bfb2dba3a42052e7ca2be906fa66570839dbc866ceb3b99  01_g2p/collision_audit.py
619d8b699dcd313a4a603b3a2f57198bd4141cd655f49b06c8fe54bb50007bc1  01_g2p/inventory.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
2bced4d8ddebea4fb00f9e6b3f9cd2dc9990421852189ab647950fc7f636775a  01_g2p/test_vi_rules.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
017bc23710b2f51a5b802256a2856f7f074cb19de0cd35ce6e96f45eff3c4a86  01_g2p/gen_rule_scope.py
b31d92a9514056d2338ba1c83f65f36c7781a8d6a7381c5ea45cf44506fb532a  01_g2p/gen_decision_doc.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
dc9c68301178806175560854a8eb3ee373bc6812c49bf17cfc9789bf5142237d  01_g2p/gen_final_decision_table.py
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
b1c973614e1c5814c44f0ce9b2939347935524473e14a5eb9b0792bc4ffd5bf3  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
b0394cd5b05cc7f805e81e5549f04ca88c852046de8b2803ffcb513fd1d4efb4  02_data/collision/qd57_scope_exclusions.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
fe0577dfb7f557f336945067af4467377217c5a31c717e94a30ca0758f47ef11  02_data/collision/qd57/manifest.json
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
9fd0cd44aa6d0691c69c325cc677aa6e76dd0de143b229fad9df5ef14d589f75  02_data/core_domain/rule_scope_vong6.md
1e3f4f5a4f433163ce1990a5b9cc38ef77ff7f2c8949062843762b075f6bcf4f  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
20a56070ef318ebce9236dc93f44e5fc88771b32bbb1d9e6856458e6443ddc1e  02_data/inventory_provenance.json
8542dbc21331839b1e9bb115aa5d73276ee055c833dc26b334ffec82b6b459a1  02_data/inventory_schema.md
8e0de0000144e695c349c734a7df1edc23520e548e9faef56311c73641d8ef45  README.md
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

### Erratum sau v14 (02/10 — vòng 6.4.1)

Rà soát hậu đóng gói phát hiện `inventory_provenance.json` →
`phase_b_audit.core_domain_basis.domain_config_hash` trong bundle v14 còn giá trị
v13 `6b9fcc95…` (đồng bộ chạy TRƯỚC khi vòng 6.4 thêm ledger
`qd57_scope_exclusions.json` vào hash), trong khi `dieu7_bao_cao.json` cùng
bundle đã là `2ca687ab…`. Đã sửa trên đĩa (trường chính → `2ca687ab…`, kèm
history vòng 6.4.1 + ghi ERRATUM trong note; chuỗi:
`5d0e89f5…`(v11, giữ ở `domain_config_hash_vong6_3`) → `6b9fcc95…`(v13) →
`2ca687ab…`(hiện hành)). **Không đổi kết quả audit** — chỉ metadata. Bundle v14
như đã gửi giữ nguyên (sha256 `78c15058…`); snapshot v14 phía trên giữ hash
as-shipped `20a56070…` cho `inventory_provenance.json`, bản đã sửa trên đĩa:
`198074c1753d1e4a2123201a81d8f5540e63b454878222ea8ea4a15f4a9b7e7f`. Sửa này
theo kèm bundle kế tiếp (v15+).

## v15 — 02/10/2026 vòng 6.5 (sửa R14-01/R14-02 theo hậu kiểm v14 §6 + doc sync §5)

Đáp ứng đủ 4 điều kiện đóng của hậu kiểm v14 (không thêm nghiên cứu ngôn ngữ):

- **R14-01 (§6.1)**: ledger `qd57_scope_exclusions.json` thêm thành viên máy đọc
  `excluded_members`/`protected_members` (39 excluded + 37 protected, exact NFC+lower
  GIỮ dấu) — pin byte-exact từ đáp án reviewer
  `qd57/scope_expected_members_qd57.json` (sha256 `376c018b…`, file pin MỚI trong gói);
  `load_scope_exclusions()` validate thành viên phủ đúng pair + cross-check đáp án pin;
  `scope_exclusion_status()` so EXACT (hết lỗi chuỗi con chếc⊂chếch/níc⊂ních/tíc⊂tích);
  uppercase/NFD cùng kết quả; tue/tuê cả hai phía excluded. Văn xuôi
  subject/protected/reason giữ nguyên để người đọc.
- **§6.2 — audit bắt lỗi boundary**: `scope_boundary_check()` trong `collision_audit.py`
  chạy đủ 76 thành viên qua API thực chạy (exact/UPPER/NFD); lệch → FAIL exit≠0
  (`compute_status` nhận `scope_fail`). Test mutation MỚI `01_g2p/test_scope_policy.py`
  (sandbox + subprocess): M1 subject đi qua / M2 protected bị chặn / M3 đổi ledger →
  audit KHÔNG PASS + `scope_policy_hash` và `domain_config_hash` ĐỔI; khôi phục → về
  baseline; **16/16 PASS**.
- **R14-02 (§6.3)**: `scope_policy_hash()` = ledger bytes + đáp án pin + source hash
  `_member_sets`/`load_scope_exclusions`/`scope_exclusion_status`/`scope_boundary_check`;
  ghi trong report (`scope_exclusions_v1.scope_policy_hash` = `3ea6fa8d…`) và gộp vào
  `domain_config_hash` (`2ca687ab…` → `8d46700f…`). Cơ chế exact fixture R12-01 không đụng.
- **§5 — doc sync**: `gen_decision_doc.py` (thêm tier EXCLUDED-V1 QD57 + members, 45+38+12+0)
  và `gen_rule_scope.py` (banner QD57 đã áp + bảng 38 nhóm excluded_v1 + Điều 7 hiện hành)
  sinh lại; provenance `merge_rules_approved_note` "26 cặp" → 45 exact + 38 excluded_v1;
  NOTE [7] log static trong `inventory.py` cập nhật; `inventory_schema.md` thêm mục 10.8;
  provenance đồng bộ hash + history vòng 6.5 (`domain_config_hash` `8d46700f…`,
  `scope_policy_hash` `3ea6fa8d…`).
- **Giữ nguyên (§6.4)**: QD57 19+38; catalog 45 fixture/90 record; 21 đối chứng; raw 83
  nhóm + trace; các ca đóng đến v13; master ham/0.2; R12-01 không mở lại.
- Chuỗi bằng chứng v15: static PASS · **466 test VI** (thêm `test_qd57_boundary_exact`:
  boundary exact 39/37, consumer mô phỏng dừng chếc/níc/tíc) · **16 probe mutation** ·
  74 profile · 45 gold-dev · audit **PASS exit 0** (boundary 0 lỗi, 21/21 đối chứng).

## Snapshot hash v15 (hiện tại — sau vòng 6.5)

```
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
a72b3610eaad2a06ff4944bf408138241da5025bb86efacf16adbd554a996c1d  01_g2p/gen_decision_doc.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
005a430301e250d02d6feaa59685cbf3e5da401a22b3ee14f3aac65523c2a8c1  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
bd62db0830cb3e2502d68a36d815b52cab8cf07d197f13b77986e600c2d0241d  02_data/inventory_provenance.json
66c05dbf01915222cd58b0af4e28ced76d8edb209b14369413ffba5a36417529  02_data/inventory_schema.md
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v16 — 02/10/2026 fase C (nhánh en: CMUdict pin → master) ngay sau CHOT_FASE_B_V15

Reviewer chốt B-v1 PASS (R14-01/R14-02 đóng) trong `review_faseB_v15/CHOT_FASE_B_V15.md`;
đường sửa duy nhất được yêu cầu (ghi chú biên tập §5) đã áp: câu số liệu probe cũ
trong `de_xuat_quyet_dinh_95nhom.md` nay gắn nhãn rõ "snapshot lịch sử v11, KHÔNG
phải kết quả probe các vòng sau" — sửa ở generator `gen_decision_doc.py`, tái sinh
diff đúng 1 dòng, idempotent.

Fase C bổ sung nhánh en KHÔNG đụng VI: master ham/0.2, `domain_config_hash`
`8d46700f…`, `approval_policy_hash` `46659a0c…`, `scope_policy_hash` `3ea6fa8d…`,
audit 83 nhóm = 45 approved + 38 excluded_v1 — tất cả giữ nguyên.

- `01_g2p/cmu_en.py` (MỚI): ARPABET 39 âm → master (AH0→SCHWA/AH1-2→AH,
  ER0→ER/ER1-2→ER_STRESS); `pronounce()` → EnWordResult {ok | spell | no_nucleus};
  syllabify maxonset_v1; OOV → spell tên chữ (LETTER_NAMES pin, ký tự không tên
  liệt kê có cấu trúc); pin cmudict sha256 `81917843…` verify lúc nạp (lệch →
  SystemExit); `en_policy_hash` `1873ac63…` = cmudict sha + bảng map + tên chữ +
  luật cắt + code sha (R14-02 discipline); `selfcheck()` phủ mọi ký hiệu dict.
- `01_g2p/cmu_coverage.py` + `02_data/en_branch/en_coverage.{tsv,_provenance.json}`
  (MỚI): coverage route-en full corpus 1M, token literal nguyên dạng — 93.589
  unique → 50.504 in-cmu = **54,0% unique / 96,6% freq**; miss: alpha_oov 34.471
  unique / 62.251 freq (nhánh spell), not_alpha 5.526, has_digit 3.088, rỗng 1.851.
  TSV header prefix `@@` (token thật có dạng bắt đầu `#`). Số cũ 58,3%/97,9%:
  khảo sát đơn vị khác không tái lập — không dùng đối chiếu.
- `01_g2p/test_cmu_en.py` (MỚI): **35/35 PASS** — pin, selfcheck, gold từ pin
  literal, syllabify, policy spell/no_nucleus, validate + transform_en +
  conformance 178, mutation sandbox G7 (M1 đổi đích map / M2 bỏ map / M3 pin hỏng
  → hash đổi hoặc chặn; khôi phục về baseline), G8 khớp provenance coverage.
- Ghi chú biên tập §5 CHOT: `gen_decision_doc.py` + `de_xuat_quyet_dinh_95nhom.md`
  (1 dòng); `inventory_provenance.json` (history fase C); `inventory_schema.md`
  (mục 11). README ĐÓNG BĂNG theo chỉ đạo chủ dự án — trạng thái trong README là
  thời điểm v15, không phản ánh CHOT v15/fase C.
- Bộ kiểm sau fase C: static PASS · **466 test VI · 74 profile · 16 mutation probe
  scope · 35 test fase C · 45 gold-dev · audit PASS exit 0** (boundary 0 lỗi,
  scope_policy_hash giữ `3ea6fa8d…`).

## Snapshot hash v16 (lịch sử — giai đoạn fase C gửi reviewer)

```
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
44cb8adc1d3f4ad8d5c70e73a32b0f944ed14499c950038e9e57a221c813765b  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
bc2b2d623262ce1ee61346e1b6645ff6968a60e940044dac9212b4edf5f4c36e  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
528018ae7336d130101ea6dd80ec4b6520a0d8e3675c2a3cf088ccd7d5e4f8ba  02_data/inventory_schema.md
92d3e9516452d40ba59c8ccc3243e7c66af98b18b5ec92c0fa7df4b92abec050  02_data/inventory_provenance.json
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
46f8ebd6571f0500ef04687f25f1cbbcdccdd381e0b219ccba4d2efc6272911b  01_g2p/cmu_coverage.py
b0b4ae9d9141d6180ebaf62fa578388c316d0dc385f2bd67df08067ad9890205  01_g2p/test_cmu_en.py
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
909853c3b5546236edb7ed692e4f71ba0b0ecc8ff7d988d5c85e59e5bc8f4f46  02_data/en_branch/en_coverage_provenance.json
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v17 — 02/10/2026 hậu kiểm HAU_KIEM_FASE_C_V16 (đóng C16-01/C16-02 + biên tập §6)

- **C16-01 (vendor bàn giao đủ):** v16 thiếu `cmudict_provenance.json`,
  `LICENSE` và đường tải tái lập trong bundle (file có sẵn trên máy, lỗi đóng
  gói). v17: `cmudict_provenance.json` + `LICENSE` nhét thẳng vào bundle;
  `03_vendor/cmudict/fetch_cmudict.py` tải đúng 2 file tại commit pin
  `7479086…` và kiểm sha256 đối chiếu provenance trước khi ghi (lệch pin →
  SystemExit, không ghi; script không bao giờ tự sửa provenance). cmudict.dict
  3,6MB không nhét — reviewer đối chiếu được qua recipe + hash pin
  `81917843…`. `test_cmu_en.py` chạy được bằng đúng hồ sơ bàn giao (không cần
  metadata reviewer dựng thay).
- **C16-02 (coverage taxonomy + mẫu số + corpus content-pin):**
  `cmu_coverage.py` tách miss 4 nhóm qua `classify_miss()` (test được):
  ascii_alpha_oov 33.851 unique / 59.038 freq = **1,94%** (nhóm DUY NHẤT spell
  trọn token bằng bảng a-z; qqz spell trọn), unicode_alpha_oov 620 / 3.213 =
  0,11% (á/ít — ký tự ngoài a-z vào `unsupported_chars`, KHÔNG đảm bảo spell
  trọn), has_digit 3.088 / 6.894 = 0,23%, not_alpha 5.526 / 35.478 = 1,17%.
  Mẫu số tần suất sửa thành 3.040.018 token KHÔNG RỖNG (con số "0,66%" v16 sai
  mẫu số). 50.504 = dictionary hit 53,96% unique / 96,56% freq — nhãn hit
  KHÔNG đồng nghĩa phát âm hoàn tất; 7 key no_nucleus trong hit được đếm tường
  minh. Corpus content-pin: sha256 corpus TÍNH tại mỗi lần chạy, đối chiếu pin
  `core_domain_provenance.json` (`cb9df5eb…`) — lệch → SystemExit; ghi
  `corpus.sha256_verified_at_run` + `pin_source` (không chép hash lịch sử).
  Regression mới: G8 corpus-pin/taxonomy, G9 qqz/á/ít/12ab/a-b/no_nucleus.
- **Biên tập v16 §6:** bỏ hẳn con số probe "52 nhóm, 45 ngoài bộ 45" khỏi
  `gen_decision_doc.py` (đúng câu gợi ý của reviewer) — doc regen, phần còn
  lại giữ nguyên.
- **Giữ nguyên phần đã đạt:** map 39 phone + stress, bảng 26 tên chữ,
  alternate/no_nucleus, mọi hash B; `en_policy_hash` giữ `1873ac63…`
  (cmu_en.py không đổi); en_coverage.tsv byte-giữ (in_cmu không đổi);
  466 VI · 74 profile · 16 scope mutation · 45 gold-dev · static PASS ·
  audit PASS exit 0 · test_cmu_en **47/47 PASS**.
- **Phân loại thay đổi v16→v17:** 3 mới (fetch_cmudict.py,
  cmudict_provenance.json, LICENSE) + 8 thay đổi (cmu_coverage.py,
  test_cmu_en.py, gen_decision_doc.py, de_xuat_quyet_dinh_95nhom.md,
  inventory_provenance.json, inventory_schema.md,
  en_coverage_provenance.json, reference_diff.md) + 38 không đổi (trong đó
  en_coverage.tsv byte-giữ).

## Snapshot hash v17 (lịch sử — sau hậu kiểm C16)

```
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
58693d4a7899336a7fea3499a93ca5bab6bcfc570d6217a1bdc0e8afc2ec8c2a  02_data/inventory_schema.md
fdc765800efbc92543b5953f70639c272fdcbb2efde59cb6ef4309340675e2b8  02_data/inventory_provenance.json
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v18 — 02/10/2026 fase D (tầng tiêu thụ g2p/0.1; ngay sau CHOT_FASE_C_V17)

- **Lõi `01_g2p/g2p.py`:** token IR ir/0.1 → `G2PToken` (schema
  `02_data/g2p/schema_g2p_0.1.md`). KHÔNG sửa tầng 1, KHÔNG đọc số, KHÔNG
  quyết route, KHÔNG sửa câu. Status enum ĐÓNG 8 giá trị (ok / fold / spell /
  no_nucleus / scope_excluded / unresolved / not_word / unknown_route) +
  `read_complete` tường minh — spell EN còn `unsupported_chars` →
  read_complete=False (không coi một phần là đọc đủ — hợp đồng v16 §5.1).
- **VI đúng thứ tự hợp đồng:** scope_exclusion_status() TRƯỚC đường phát âm
  được bảo đảm ("chếc" parse được vẫn scope_excluded — probe H2) → parse
  thuần (F05) → fold nhóm (b) theo pin `fold_vi.tsv` (tone_state="fold",
  detail ghi ascii→fold + freq_top1 + margin) → spell seed `spell_vi.tsv`
  (quy ước chờ duyệt — seed thiếu chữ 'z' → unresolved tường minh, không bịa)
  → unresolved.
- **EN:** `cmu_en.pronounce()` map 1-1 ok / spell / no_nucleus; verbal/cat/
  route giữ nguyên dạng tầng 1 cấp.
- **Profile (I2):** `to_profile` qua transform_vi/en; tone_state unresolved
  TỪ CHỐI serialize; conformance vocab 178 kiểm từng ký tự; loss map khai
  báo khi kích hoạt (vd PHONE_OPEN_E_PREVELAR trong 'mach'→'mạch').
- **Vocab từ master (đảo chiều):** `emit_vocab_config.py` →
  `02_data/g2p/vocab_config_from_master.tsv` 78 entry (62 segment / 8 prosody
  / 8 control) giữ nguyên repr master + `vocab_config_provenance.json`
  (inventory sha, tsv sha); chạy lại idempotent.
- **Không đổi policy:** domain/scope/approval/en_policy hash giữ nguyên từ
  v17 (fase D chỉ là tầng tiêu thụ — không đổi master, không đổi QD57, không
  đổi map CMUdict).
- **Bộ kiểm:** `test_g2p.py` **38/38 PASS** — scope-trước-parse, fold
  provenance, spell partial, not_word/unknown_route fail loud, determinism
  byte-giữ (I2), 200 record đầu corpus thật 0 crash + conformance sạch +
  đủ đường đi, vocab config tái lập khớp provenance.
- **Chuỗi bằng chứng v18:** static PASS · 466 VI · 74 profile · 16 scope
  mutation · 45 gold-dev · audit PASS exit 0 · test_cmu_en 47/47 ·
  test_g2p 38/38.
- **Phân loại thay đổi v17→v18:** 7 mới trong bundle (g2p.py,
  emit_vocab_config.py, test_g2p.py, schema_g2p_0.1.md,
  vocab_config_from_master.tsv, vocab_config_provenance.json, và
  fold_vi.tsv — pin fold fase A0 có sẵn trên máy, v18 đưa vào bundle vì
  g2p.py tiêu thụ) + 3 thay đổi (inventory_provenance.json,
  inventory_schema.md, reference_diff.md) + 45 không đổi.

## Snapshot hash v18 (lịch sử — CHƯA đạt hậu kiểm)

```
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
dfbefa8d8826da9da9001a2f477fe465131951d31b649e3b6b417c6b0d59aa3d  02_data/inventory_schema.md
eb9bb043e759fc7738d5bbfe1cc307834b0834b4b86f9a31e2378b7f5e2f08b1  02_data/inventory_provenance.json
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
1b126ee1edc76cd74d70e63fda1271841bccc75fc563ee03f27ece888929b387  01_g2p/g2p.py
5d41c6e7ffe0986d04422cae975c2fb9d9ef8e6009859b7fecaee55735090ba1  01_g2p/emit_vocab_config.py
2db722710a0cec14f6b9cf546cd22875b6b0081e5d53b79f3c0f5efc55ab6bb6  01_g2p/test_g2p.py
3c3ef7f40a85240eadfb03023055f249265efd449ca7ad3e09925b422284e1c6  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v19 — 02/10/2026 sửa D theo HAU_KIEM_FASE_D_V18 (đóng D18-01…D18-04)

- **D18-01 (fold đi vòng scope — ĐÓNG):** `_vi_unit` re-check
  `scope_exclusion_status()` trên ỨNG VIÊN FOLD trước khi phát âm:
  `nic`→`níc`, `tic`→`tíc` (2 ứng viên QD57 trong 698 dòng) →
  status scope_excluded, detail lưu input→candidate→policy; KHÔNG lách sang
  protected partner hay spell. Regression H2 (nic/tic/direct subject/
  protected/mach positive/nam không phục hồi dấu).
- **D18-02 (hợp đồng IR + master JSON — ĐÓNG):**
  (a) tiêu thụ đủ `00_docs/G2P_00_hop_dong_dau_vao.md` (file NÀY GIỜ ĐƯỢC
  KÈM TRONG BUNDLE): read/break/intonation/origin giữ nguyên trong record;
  punct → status `control` im lặng GIỮ break (hợp đồng §3.2); number/abbr/
  acronym/unit… tầng 1 đã điền verbal dạng từ ⇒ tách read unit theo dấu cách
  và đọc theo route (không tự normalization lại — "không đọc số" đúng nghĩa);
  contract check shape/version/field (schema ir/0.1, i liên tiếp, cat/route/
  read/break enum, surface/verbal str) + đồng thuận read_string →
  `contract_errors` có cấu trúc; CLI exit 1 khi contract lỗi (không âm thầm
  xuất ok); verbal None/thiếu i không còn KeyError/AttributeError.
  (b) serializer master `master.read_units[]` giữ record ĐẦY ĐỦ
  (onset/glide/nucleus/coda/tone/tone_state/stress/stress_state/
  source_graphemes/flags) + liên kết nguồn source_token_id/read_unit_index/
  syllable_index (inventory_schema §5); profile kokoro178 tách thành nhánh
  `profile_debug` (debug_only=true) — không thay thế master; en spell lưu
  `fallback_reason`.
- **D18-03 (invariant — ĐÓNG):** validate tương quan: unit cấm phát âm ⇒
  KHÔNG syllables + read_complete=False; token roll-up nhất quán (status cấm
  phát âm ⇒ ≥1 unit cùng nhóm; ok/fold/spell ⇒ mọi unit pronounceable); spell
  còn unsupported ⇒ read_complete=False; spell không sinh reading nào (vd
  'Ả', '1-2-2-4') ⇒ unresolved; en verbal rỗng ⇒ unresolved. Serializer chạy
  validate trước — fault injection (nam đổi scope_excluded còn gắn record)
  bị BẮT ở unit.validate + bị TỪ CHỐI ở profile_debug. Test bỏ check 'or
  True'; loss 'mach' PHẢI có event prevelar (không chấp nhận []); H8 smoke
  corpus tách thành H11 TÙY CHỌN — SKIP tường minh khi thiếu corpus, không
  tạo dữ liệu giả.
- **D18-04 (fingerprint D + pin tài nguyên — ĐÓNG):** `g2p_policy_hash`
  (schema g2p_policy/0.1) = sha256{code g2p.py, fold_tsv, spell_tsv, cmudict,
  scope ledger, inventory_hash, inventory_contract_hash, profile version} —
  mutation fold line mach→mách (M1) hoặc bỏ re-check scope ứng viên (M2) →
  hash ĐỔI, khôi phục → baseline; M3 pins hỏng → SystemExit.
  `load_fold()`/`load_spell_vi()` KIỂM SHA đối chiếu
  `02_data/g2p/g2p_resource_pins.json` — fail-closed (mutation bảng KHÔNG âm
  thầm ăn theo output — khác v18). Nguồn fold khai THỰC:
  `02_data/fold/fold_provenance.md` (698 dòng = nhóm (b) a0_ket_qua.json;
  builder script phiên A0 không còn — phần không xác minh được khai rõ,
  không bịa). spell_vi = seed_pending_owner trong pins. Mọi đầu ra g2p/0.1
  có inventory_hash + inventory_contract_hash + g2p_policy_hash + versions
  (inventory_schema §7). Emitter chạy `inventory.audit()` điều 1-6 trước khi
  ghi — dup-ID probe không ghi file, exit ≠ 0.
- **Không đổi policy B/C:** 4 hash giữ nguyên; không mở lại QD57/19/38.
- **Chuỗi bằng chứng v19:** static PASS · 466 VI · 74 profile · 16 scope
  mutation · 45 gold-dev · audit PASS exit 0 · test_cmu_en 47/47 ·
  test_g2p **65 PASS / 0 FAIL**.
- **Phân loại thay đổi v18→v19:** 3 mới trong bundle (g2p_resource_pins.json,
  fold_provenance.md, G2P_00_hop_dong_dau_vao.md) + 7 thay đổi (g2p.py,
  emit_vocab_config.py, test_g2p.py, schema_g2p_0.1.md,
  inventory_provenance.json, inventory_schema.md, reference_diff.md) +
  49 không đổi.

## Snapshot hash v19 (lịch sử — D18-01 đóng, §3-5 còn mở)

```
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
9f6d5b475b3b8818b96187ad4314b7d097b6455336d29219781bfbc685ce412b  02_data/inventory_schema.md
4fc21cf7a3a528b10fd31297542d5a4620ec688bba70a0277646d9f5c8243eda  02_data/inventory_provenance.json
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
f593d65caa3ea70aee3aebb85a6d97b22e1b91831650919d3ab47092f753788d  01_g2p/g2p.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
7034313e82a8012bf9122358c10f7d7f7f151bad0fb436a24ef30ae6d0707df7  01_g2p/test_g2p.py
100382e020385694252277766b5b60982d4b68ea28867f825f40bbe01b5e704a  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v20 — 02/10/2026 sửa D theo HAU_KIEM_FASE_D_V19 (đóng §3.1-3.4, §4, §5)

- **§3.1 — read="spell" được THỰC THI (không chỉ lưu):** route=en →
  per-letter LETTER_NAMES: "US" (acronym spell) → U-S (you-ess, PHONE_U +
  PHONE_OPEN_E), "A" → EY + STRESS_PRIMARY (không tra từ "us"/SCHWA từ điển —
  dictionary hit không phải quyền bỏ qua mode); ký tự ngoài bảng →
  unsupported_chars (vd "A9" → complete=False, unsupported "9"). route=vi →
  tier-1 đã spell-out trong verbal (vd email) — giữ đường từ; unit đơn chữ
  đi seed spell_vi (TRẠNG THÁI CHỜ DUYỆT — không tự duyệt seed qua dispatch).
  Regression: cả acronym liền chữ lẫn 1 chữ có word-pronunciation khác
  letter-name.
- **§3.2 — read_unit_index phân biệt từng unit:** hết trùng 0,0 ("hai mươi"
  → [0,1]); leaf identity = (source_token_id, read_unit_index,
  syllable_index) duy nhất, kiểm cả VI/EN.
- **§3.3 — malformed IR thành lỗi cấu trúc:** type guard TRƯỚC mọi
  membership/dispatch: envelope null/[], tokens[null], cat:[], break:{} →
  contract_errors có cấu trúc; CLI JSON null → exit 1 dạng JSON
  contract_errors, KHÔNG traceback.
- **§3.4 — read_string đối chiếu thật:** dãy MẢNH CHỮ-SỐ (tách tại mọi ký tự
  không chữ/số; biến thể nháy chuẩn hóa) theo thứ tự — bất khả tri quy tắc
  gắn dấu câu của renderer tầng 1 (hồ sơ `_join_read`:
  "Jerry"+"-"+"Đường" → "Jerry-Đường"; "trăm"+"." → "trăm.") nhưng bắt ĐỦ
  thừa/thiếu/sai thứ tự từ vựng ("nam thêm"/"xnam"/"namnam") và read_string
  rỗng khi có reading. Trên 1000 envelope corpus thật còn ~1,2% lệch
  read_string (picked) ≠ tokens — consensus BÁO ĐÚNG (contract_errors; đó là
  nhiệm vụ của nó, không phải lỗi g2p; test H11 chấp nhận chỉ nhóm này).
- **§4 — aggregate parent/child:** status/read_complete/unsupported_chars
  parent PHẢI khớp derive từ units (`_aggregate`); fault "álvarez parent
  complete còn child incomplete/unsupported" → validate BẮT + serializer
  TỪ CHỐI; parent bịa unsupported → BẮT. Debug partial reading hợp lệ vẫn
  được phép (không cấm).
- **§5 — identity phản ánh cấu hình thực chạy:** `g2p_policy_hash` v0.2
  mang **b_c_dependencies** (en_policy_hash, domain_config_hash,
  scope_policy_hash, approval_policy_hash — mutation cmu_en AA→AE làm hash
  D ĐỔI: probe M4); `resource_snapshot` = sha SNAPSHOT cache-aware đang dùng
  (warm-load → mutation đĩa → hash/snapshot GIỮ đúng snapshot đang dùng;
  cold load sau mutation → pin fail-closed: M1/M5); `versions.dialect` chứa
  GIÁ TRỊ pin domain; fold_tab test-override bắt buộc đánh dấu
  `resource_override` {test_only, fold_override_sha256} — output thử nghiệm
  không thể bị hiểu là theo pin mặc định (M2 bỏ re-check scope vẫn đổi hash
  — consumer mutation).
- **Không đổi policy B/C:** 4 hash giữ nguyên (đối chiếu sau sửa).
- **Chuỗi bằng chứng v20:** static PASS · 466 VI · 74 profile · 16 scope
  mutation · 45 gold-dev · audit PASS exit 0 · test_cmu_en 47/47 ·
  test_g2p **98 PASS / 0 FAIL**.
- **Phân loại thay đổi v19→v20:** 0 mới + **6 thay đổi** (g2p.py,
  test_g2p.py, schema_g2p_0.1.md, inventory_provenance.json,
  inventory_schema.md, reference_diff.md — vocab emitter không đổi) +
  **53 không đổi**. *(Cải chính v21 — D20-05: bản v20 ghi nhầm "7 thay đổi +
  52 không đổi"; đếm SHA thực tế v19→v20 là 6/53, sáu tên file nêu trên khớp
  đủ. Bundle v20 giữ nguyên byte — cải chỉ ghi tại đây và schema §9.)*

## Snapshot hash v20 (hiện tại — fase D v20)

```
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
282139756810a76bedea088db6dbed4e3556811f910546720f4ce8d4e10b864b  02_data/inventory_schema.md
3e21b38dc8f745dfec4f32dfc1d825af998c8baaf3e83c77dbcbfcba0ada6f38  02_data/inventory_provenance.json
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
a6b373188f9115fbbf031e6e7b38cf8723d69d5ee35f14964fd2737c587312d3  01_g2p/g2p.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
ceb1fbe6e41a9a86e1f3654422a0472f1c7763da2b938c45b4a2b69fe3625bef  01_g2p/test_g2p.py
275ebc309a22074bad4c7e172d2395e4d77cd73b6f7d32bb5cecc85e8ec3f3ec  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v21 — 02/10/2026 sửa D theo HAU_KIEM_FASE_D_V20 (đóng D20-01/02/03 + khai báo D20-04/05)

- **D20-01 (regression v20 — fingerprint spell):** cache spell chuyển khuôn
  fold — `_SPELL_VI_CACHE = {"tab", "sha256"}` đã kiểm pin;
  `effective_resource_shas()`/`resource_snapshot` CHỈ trả **str sha256** (hết
  dict bảng); `g2p_policy_hash()` cold == warm trong cùng process. Baseline
  hash D đổi một lần nữa (e4977605… — code_sha256 đổi, chấp nhận theo phán
  quyết v20 §D20-01).
- **D20-02:** route guard nhánh `read="spell"` — route ngoài {vi,en} →
  `unknown_route` fail-loud, ĐỐI XỨNG nhánh từ (4 ca neu/jp × word/spell).
- **D20-03 (độ phủ test):** H8 phủ đủ 3 trường `resource_snapshot` (type str
  + giá trị == pin); H9-M5 THẬT — một process: stream warm (fold + spell) →
  mutation ĐĨA cả hai bảng → stream lại GIỮ reading + snapshot sha; cold load
  tường minh fail-closed (load_fold + load_spell_vi); bỏ mode "hash2" không
  tồn tại; thêm check cold==warm (D20-01).
- **D20-04a (delegate tier-1 — khai báo + fixture thật):** fixture verbal
  TẦNG 1 THẬT `02_data/g2p/fixture_tier1_email_spell.json` — email route=vi
  `read="spell"` chụp 02/10/2026 từ `pipeline.normalize` (ir_sha256
  03db282e… tự khai; chỉ ĐỌC IR tầng 1, không sửa tầng 1). D giữ đường từ;
  `vuhoanplus`/`gmail` → unresolved tường minh (không bịa, không spell-out
  lại ở tầng 2); envelope tier-1 qua contract sạch. Regression 3 check.
- **D20-04b (khai báo quy ước case):** read_string consensus so mảnh NGUYÊN
  VĂN (case-sensitive) — tier-1 giữ nguyên văn case giữa `verbal` và
  `read_string` render; số đo ~1,2% picked≠tokens đã theo quy ước này; khai
  tại schema §9. (Case-fold bị loại để không nuốt lệch case thật.)
- **D20-05 (cải chính đếm):** delta v19→v20 thực đo là **6 sửa / 53 không
  đổi** (0 mới) — bản v20 ghi nhầm "7/52"; cải chính ghi tại mục v20 ở trên
  (dấu *(Cải chính v21)*), schema §9; bundle cũ giữ nguyên byte. Đồng bộ tên
  khóa payload §6 (fold_tsv/spell_tsv) với `resource_snapshot` (*_sha256).
- **Không đổi policy B/C:** 4 hash giữ nguyên. Giữ nguyên mọi phần đã đóng:
  D18-01, emitter gate, §3.2-3.4, §4, §5.1/§5.2, 8 artifact byte-giữ.
- **Chuỗi bằng chứng v21:** static PASS · 466 VI · 74 profile · 16 scope
  mutation · 45 gold-dev · audit PASS exit 0 · test_cmu_en 47/47 · test_g2p
  **110 PASS / 0 FAIL** (máy có corpus; máy thiếu corpus: 106 PASS + 1 SKIP
  H11) · 8 artifact tái sinh **byte-giữ** · probe reviewer v20
  (`faseD_v20_reviewer_evidence/reviewer_probes_v20.py`) chạy lại trên cây
  v21: **toàn PASS** (5 check FAIL của v20 đều xanh).
- **Phân loại thay đổi v20→v21:** 1 mới (fixture_tier1_email_spell.json) +
  6 thay đổi (g2p.py, test_g2p.py, schema_g2p_0.1.md,
  inventory_provenance.json, inventory_schema.md, reference_diff.md) +
  53 không đổi = 60 file.

## Snapshot hash v21 (hiện tại — fase D v21)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
469a3170e023a264fb788a89edaf6bedc711962d5a67288fdaf89f11dec6ce52  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
53f0ebd05e96fe6b718411eb98cd43a8f78d145d7d9bd5d61238d4cf6938c94a  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
b0ee11c40f9934df829bd0302c155b0c04fd093be447177c8e90adc2615a524e  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
2d666b4406c156f3b1fcde281919e7adf5f91ec449bfd1881315e4fcaf478acc  02_data/inventory_provenance.json
34b2bec88ff905cd96f9e05c031166f0bce77d9b8b775529c49cc48d353ecf6d  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v22 — 02/10/2026 fase E mở màn (D đã ĐÓNG v21; cache hiệu năng + gate E1/E2/E3/E5)

- **Bối cảnh:** FASE D ĐÓNG (HAU_KIEM_FASE_D_V21 — 4 điều kiện §4-v20 đạt,
  D20-04 đóng bằng fixture tầng 1 thật, không thoái trào). A/B/C/D = PASS.
- **Cache hiệu năng tầng D (chuẩn bị corpus full):** cmu dict nạp **1 lần/
  process** — `pronounce(w, cmu=)` nhận snapshot `_cmu_snapshot()` (verify_pin
  bên trong); `_cmudict_sha` + `b_c_dependencies` (attestation/ledger tĩnh
  trong lần chạy) memo cùng khuôn M5 — identity = snapshot đang dùng, giá trị
  identical với gọi lại từng lần. **cmu_en.py KHÔNG đổi byte** →
  `en_policy_hash` giữ nguyên `1873ac63…`; `g2p_policy_hash` baseline mới
  **`a24db1ab…`** (code g2p.py đổi — hợp lệ theo điều kiện chốt D v21 §5).
  Lý do: load_cmu cũ re-parse 126k entryCMUdict cho MỖI từ EN (đo profile:
  ~2,2s/record) — corpus 1M không thể chạy.
- **E1 — torture H12 thêm 6 check:** "A"×100 spell (per-letter, complete),
  "TRTRTR", token 10.000 ký tự, 150 token cat hỗn hợp — 0 crash, serialize
  được, <5s. `test_g2p.py` **115 PASS / 0 FAIL** (máy có corpus; thiếu corpus:
  111 PASS + 1 SKIP). Chuỗi cũ nguyên: 466/74/16/45/47/audit 0. Probe reviewer
  v20 chạy lại toàn PASS.
- **E2 — corpus 1M FULL (E2-A + E2-B):** `01_g2p/fase_e_corpus_run.py` —
  fail-closed đầu vào (content-pin corpus `cb9df5eb…` khớp pin
  core_domain_provenance + resource pins trước khi đếm), 24 worker song song
  (line % 24), merge tổng hợp:
  - **1.000.000 record / 22.853.017 token — 0 crash.**
  - E2-A: 0 token phát-âm-được thiếu syllable; 0 profile rỗng; 0 conformance;
    0 validation; contract_errors **12.231 record (1,22%) — 100% nhóm
    read_string-consensus** (khớp khai báo ~1,2%; nhóm OTHER = 0).
  - E2-B: 0 vi phạm coda tắc-sắc/nặng; 0 vi syllable thiếu tone; 0 en
    syllable thiếu stress; 0 control lọt syllable.
  - Status: ok 19.354.093 · control 2.452.284 · unresolved 861.431 ·
    spell 159.965 · fold 24.613 · scope_excluded 578 · no_nucleus 35 ·
    not_word 18. Route: vi 19.242.498 · en 3.610.519. sent_lang: vi 588.442 ·
    en 187.496 · mixed 224.062. Spell trên word token **0,49%**
    (viết hoa 70.413 / thường 24.893 — không đặt gate %, policy [B] chờ).
  - **Gate tổng: ALL_PASS=true.** Report: `02_data/g2p/fase_e_corpus_1M_report.json`.
- **E5 — determinism + hiệu năng:** stream_json byte-identical mẫu 1.000
  record ×2 lượt; **4.233 câu/phút/worker** (sum-CPU, 24 worker bị tranh chấp
  băng thông) — đối chứng tuần tự: 153 rec/s ≈ 9.200 câu/phút/worker.
  Ngưỡng kế hoạch ≥2.000 — **ĐẠT**. Wall-clock toàn corpus: 602s.
- **E3 — differential sea-g2p 0.10.0 (Apache-2.0) qua wrapper vig2p 0.1.0**
  (cùng ký hiệu kokoro mũi tên — so trực tiếp, BỎ stress marks 2 phía):
  mẫu 2.000 word-token (systematic 1/250 record, reservoir seed=0):
  **equal 1.236 · phoneme_lech 646 · no_pron 88 · tone_lech 30**, tool error 0.
  Bất đồng gom nhóm giải thích được: quy ước ký tự (coda k↔c, r ʒ↔ɹ, vần
  ɨ↔y/iə↔iɛ/ɚ↔↗ː, en ɑ↔ʌ) + policy thật (fold nhóm b của mình — 'cac'→các —
  tool không làm); group tone_lech chủ yếu artifact ER→'↗' của tool.
  Report + bộ judge 500 token: `fase_e_diff_report.json` /
  `fase_e_judge_set.jsonl`. **Không oracle, không gate %.**
- **Kế hoạch fase E + pin:** `00_docs/G2P_KE_HOACH_FASE_E.md` — pin sea-g2p
  0.10.0 (wheel sha), vig2p 0.1.0 (không license rõ — chỉ tool nội bộ),
  hoang1007/vig2p @ 8835c301 (không LICENSE — tham khảo), espeak-ng 1.51,
  checkpoint contextboxai/Kokoro-Vietnamese (source commit a249afe5…;
  weights chưa tải — recipe fail-closed khi tải đầu tiên). Xin chốt tiêu chí
  E4 (9B judge ~500 token cùng chủ dự án) và E6 (WAV A/B) trước khi chạy.
- **Phân loại thay đổi v21→v22 (SHA đo lúc đóng gói):** 30 mới — 6 file
  code/report/plan (fase_e_corpus_run.py, fase_e_diff_sample.py,
  G2P_KE_HOACH_FASE_E.md, fase_e_corpus_1M_report.json,
  fase_e_diff_report.json, fase_e_judge_set.jsonl) + 24 shard stats —
  và 6 sửa (g2p.py, test_g2p.py, schema_g2p_0.1.md,
  inventory_provenance.json, inventory_schema.md, reference_diff.md) +
  54 không đổi = 90 file.

## Snapshot hash v22 (hiện tại — fase E mở màn)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
17e20df810de02d5f2ddc2fe3d65ad638d5b68ce079bdb4fba6847071d7e967c  00_docs/G2P_KE_HOACH_FASE_E.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
0b43b578f97897649879f279b6ac890d9085e921519a5417325f55a28f6f8096  01_g2p/fase_e_corpus_run.py
a4de2b9b66c9cb4242a1d520371614d43b037e11ec353c2121a35817b5d3fa51  01_g2p/fase_e_diff_sample.py
ecdfdf0d43eff8f5e0b5da8ca8ed2e181399075b84b48785748b99328d7b6193  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
45b0b2cdf3cf2c8a43cb5a27c6f0f1dc4b5e71f171a6325bbe00355c8ab2c536  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
190993829c550046f9d7cdbbb6b9bd29ee91d6a70b72e8be8554e602859ba91d  02_data/g2p/fase_e_corpus_1M_report.json
295d80ddfdf03122cf36fc018662521df53c973fc522f82b1cc7e861c3236197  02_data/g2p/fase_e_corpus_1M_shard0.json
beb2e0023bab8c0f83235623e13624054729437ad60c5c9b66740489b9022476  02_data/g2p/fase_e_corpus_1M_shard1.json
a27b9e26dd6fbd3f992bc653bc305fc42794f4e13cc8b505f841803a5148868b  02_data/g2p/fase_e_corpus_1M_shard10.json
464d61e1480f23156fc096f044057f0a0d4cd6043ce199284b6ef125fc397e4e  02_data/g2p/fase_e_corpus_1M_shard11.json
04009cc8848c7c5ed3ca68ca0b03ec128f8241ffc2398b143c51b4b54bfd6112  02_data/g2p/fase_e_corpus_1M_shard12.json
cc0abf3d48c88352b050bfcc45d64ef7a027ca988623d526fbb9703dd8a26f5f  02_data/g2p/fase_e_corpus_1M_shard13.json
fdde6c9dd94341de9dff7e9d690a7a0f60a83f1575d7c8fb768fa2c47079e8a6  02_data/g2p/fase_e_corpus_1M_shard14.json
d673c413298e9b0cfaa3cc611dd105c5b1531649032afbddcf2c0087d2326c45  02_data/g2p/fase_e_corpus_1M_shard15.json
6c2f1e615dc2e1d838d763920db0a6ca56c712b2050db67e05efca9e3a339f7c  02_data/g2p/fase_e_corpus_1M_shard16.json
cc8172559f86d330add7ed408eb2809fcf2ec5a8d3efcb66b8a24a84bcab4e11  02_data/g2p/fase_e_corpus_1M_shard17.json
21cc8b578804d5983d17a502dcb1f32a29409d18ae2479ba54de4328714d95b9  02_data/g2p/fase_e_corpus_1M_shard18.json
20f22dd5cd50d323e67329fedec4549aefaa96f5dc5d31fe5f198df15a6c3644  02_data/g2p/fase_e_corpus_1M_shard19.json
a5acf5e5d046990f40f777862c20bf0fe5ee88529d3fc4ae6fb5faf6d24adff8  02_data/g2p/fase_e_corpus_1M_shard2.json
3508710d25a4c92ffb3c90dbba40db05bf1dcfc6da9b244116983acab31ab591  02_data/g2p/fase_e_corpus_1M_shard20.json
40fa2db67ecc5b5faf50c1d4339b140d784115c4f50ee7443d07f7ff1115f1b4  02_data/g2p/fase_e_corpus_1M_shard21.json
0c797f433bd2c24d31872501d75d986175c4330a15f277c4d7a038b000acd8cb  02_data/g2p/fase_e_corpus_1M_shard22.json
015036ef12c9901bc4cf12261002d0ab27ce8cf156d0bcde3cdc8c39c8f76f89  02_data/g2p/fase_e_corpus_1M_shard23.json
938bcae1a450911b1209af40c6f49740af9ead75f6d25e716cb8f5037aab0c88  02_data/g2p/fase_e_corpus_1M_shard3.json
4bde141bce306635af04cd928983f54e550e94532bde27cc7b5529a7505d19e3  02_data/g2p/fase_e_corpus_1M_shard4.json
4c4770d5a45bc66abf188879fdb62cc42e6a29e3dd1d30bbc8c8c406232c7a28  02_data/g2p/fase_e_corpus_1M_shard5.json
552087540e1fd1d7ee79578d8d07d06c57f688da2a981e8c7fe3e093dec6dfdb  02_data/g2p/fase_e_corpus_1M_shard6.json
2d85c04b1d860df3cb8cf6652e4f8cc1346a50fa3f6e591318f30d1ea18704f5  02_data/g2p/fase_e_corpus_1M_shard7.json
5cd647543fe7c5820d709acd0d60100cfd1dc3d4db63b3b7a1c25e0ca85cd385  02_data/g2p/fase_e_corpus_1M_shard8.json
33a7da7c1257e373778e0c9367dcb78062ac08076e18ae4b7fba035bc6de6263  02_data/g2p/fase_e_corpus_1M_shard9.json
c3df7b701908f7e33aed1e9c7379c26daaec460bdc65e649eac8419d61160abc  02_data/g2p/fase_e_diff_report.json
b8743e90544ad1d7160f24a801bbf4a71f5c220302090c8cbf180b999292f8d2  02_data/g2p/fase_e_judge_set.jsonl
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
0d4b3c89533e7a933586da65afd98dfb2997c86fa06da2a17471e8652c797306  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
2a28adc66edb78bbefeeaf1a51b94c44e169546b5a0619509cecaf11978e6727  02_data/inventory_provenance.json
a1a0d8da4bd005f7fce958eda7181449fc01790f520e4755339e8d8f75409a74  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v23 — 02/10/2026 preflight + vét cạn (nhánh nhanh reviewer; đóng finding E4-prep)

- **Bối cảnh:** reviewer duyệt v22 (90/90 hash OK, delta khớp khai báo,
  probe trên cây v22 toàn PASS, cross-check E2 độc lập 24 shard khớp tuyệt
  đối, E3/judge-set nhất quán, E5 vượt ngưỡng) và **chốt tiêu chí E4
  (7 điều kiện) + E6 (5 điều kiện)** — lưu chính thức tại
  `G2P_KE_HOACH_FASE_E.md` §6. Reviewer tự chạy vét cạn trên cây v22:
  126.932 khóa / 0 vi phạm / negative-control bắt được lỗi giả. 2 finding
  nhỏ không chặn → đóng ở v23.
- **ADOPT script reviewer (byte-chính xác, sha ghi provenance):**
  `01_g2p/exhaustive_sweep.py` — vét cạn toàn không gian khóa tầng 2
  KHÔNG lấy mẫu (mọi dòng fold + mọi ký tự spell + mọi member scope ×3
  dạng + mọi entry inventory + MỌI key cmudict) + bất biến danh tính
  trước–sau; `preflight.sh` — gate tự kiểm 1 lệnh trước khi đóng gói
  (10 kiểm tra song song, chống oversubscription thread).
- **Chạy thật máy tác giả (i9-12900K, 16 worker):** preflight **10/10 PASS
  trong 3s** (inventory · vi_rules 466 · scope 16 · coda 74 · gold-dev 45 ·
  collision audit exit 0 · cmu_en 47 · test_g2p 115 · vét cạn · probe
  reviewer v20 — bộ mới nhất nhận được). Vét cạn: **126.932 khóa / 0 vi
  phạm / 0,65s / identity_stable=true** (policy hash `a24db1ab…` trước==sau;
  reviewer cùng kết quả 1,84s trên 2 core). Bằng chứng kèm bundle:
  `02_data/g2p/preflight_v23.log` + `preflight_summary.json` +
  `exhaustive_sweep_report.json`.
- **Finding (a) đóng — `fase_e_judge_sample.py` THẬT** (plan §E4 hứa "kèm
  v22" nhưng thiếu): mode `prepare` sinh phiên chấm mù E4 đúng 7 điều kiện
  reviewer — `fase_e_judge_session.jsonl` (500 item, A/B xáo per-item seed
  20261002, cân bằng 248/500, **đã kiểm không lọt nhãn**
  group/my_text/tool_text), `fase_e_judge_session_key.json` (KHÓA — không
  cho judge), `fase_e_judge_de_bai.md` (luật phiên + provenance). Bộ judge
  đóng băng sha `b8743e90544ad1d7…`. Mode `spotcheck` phục vụ điều kiện 7
  (≥20 phiếu ngẫu nhiên kèm khóa đối chiếu).
- **Finding (b) đóng — quy ước dấu nhấn:** `tool_text` có thể chứa `ˈ` `ˌ`
  (sea-g2p gắn stress cả âm tiết vi — artifact tool). Ghi trong đề bài phiên
  (luật 2: judge KHÔNG chấm dấu nhấn) + kế hoạch E §E4.
- **Còn mở (chờ chủ dự án):** E4 — session 9B cùng anh (materials sẵn sàng:
  `python3 01_g2p/fase_e_judge_sample.py prepare` đã chạy, chỉ cần điền
  model/revision/quantization vào đề bài rồi chấm); E6 — chốt revision
  checkpoint contextboxai/Kokoro-Vietnamese → recipe fail-closed → demo
  A/B. Reviewer chốt E1–E5 khi nhận bundle này (nhánh nhanh — không cần
  vòng mới).
- **Phân loại thay đổi v22→v23 (SHA đo lúc đóng gói):** 9 mới (preflight.sh,
  exhaustive_sweep.py, fase_e_judge_sample.py, fase_e_judge_session.jsonl,
  fase_e_judge_session_key.json, fase_e_judge_de_bai.md,
  exhaustive_sweep_report.json, preflight_v23.log, preflight_summary.json)
  + 4 sửa (G2P_KE_HOACH_FASE_E.md, inventory_provenance.json,
  inventory_schema.md, reference_diff.md) + 86 không đổi = 99 file.

## Snapshot hash v23 (hiện tại — preflight + vét cạn; E4 materials sẵn)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
2a97015901d88bd9ff2dc90c3ddcf187bea6d331cb7254a52ac02012d08ddb84  00_docs/G2P_KE_HOACH_FASE_E.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
3d7617fd40641f9ab4da13ce7e6e43fef9d7f4227da1f0f320b0ad2857dc3564  01_g2p/exhaustive_sweep.py
0b43b578f97897649879f279b6ac890d9085e921519a5417325f55a28f6f8096  01_g2p/fase_e_corpus_run.py
a4de2b9b66c9cb4242a1d520371614d43b037e11ec353c2121a35817b5d3fa51  01_g2p/fase_e_diff_sample.py
7814151994ca9619552f08a70d379e4f54f4fd8099e2cc7d6e3afad60ef6b39e  01_g2p/fase_e_judge_sample.py
ecdfdf0d43eff8f5e0b5da8ca8ed2e181399075b84b48785748b99328d7b6193  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
45b0b2cdf3cf2c8a43cb5a27c6f0f1dc4b5e71f171a6325bbe00355c8ab2c536  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
ba2ffe4fbb371a0d6e5c2a60127d86e08ec601b35a47abc3fcb0a816bb184075  02_data/g2p/exhaustive_sweep_report.json
190993829c550046f9d7cdbbb6b9bd29ee91d6a70b72e8be8554e602859ba91d  02_data/g2p/fase_e_corpus_1M_report.json
295d80ddfdf03122cf36fc018662521df53c973fc522f82b1cc7e861c3236197  02_data/g2p/fase_e_corpus_1M_shard0.json
beb2e0023bab8c0f83235623e13624054729437ad60c5c9b66740489b9022476  02_data/g2p/fase_e_corpus_1M_shard1.json
a27b9e26dd6fbd3f992bc653bc305fc42794f4e13cc8b505f841803a5148868b  02_data/g2p/fase_e_corpus_1M_shard10.json
464d61e1480f23156fc096f044057f0a0d4cd6043ce199284b6ef125fc397e4e  02_data/g2p/fase_e_corpus_1M_shard11.json
04009cc8848c7c5ed3ca68ca0b03ec128f8241ffc2398b143c51b4b54bfd6112  02_data/g2p/fase_e_corpus_1M_shard12.json
cc0abf3d48c88352b050bfcc45d64ef7a027ca988623d526fbb9703dd8a26f5f  02_data/g2p/fase_e_corpus_1M_shard13.json
fdde6c9dd94341de9dff7e9d690a7a0f60a83f1575d7c8fb768fa2c47079e8a6  02_data/g2p/fase_e_corpus_1M_shard14.json
d673c413298e9b0cfaa3cc611dd105c5b1531649032afbddcf2c0087d2326c45  02_data/g2p/fase_e_corpus_1M_shard15.json
6c2f1e615dc2e1d838d763920db0a6ca56c712b2050db67e05efca9e3a339f7c  02_data/g2p/fase_e_corpus_1M_shard16.json
cc8172559f86d330add7ed408eb2809fcf2ec5a8d3efcb66b8a24a84bcab4e11  02_data/g2p/fase_e_corpus_1M_shard17.json
21cc8b578804d5983d17a502dcb1f32a29409d18ae2479ba54de4328714d95b9  02_data/g2p/fase_e_corpus_1M_shard18.json
20f22dd5cd50d323e67329fedec4549aefaa96f5dc5d31fe5f198df15a6c3644  02_data/g2p/fase_e_corpus_1M_shard19.json
a5acf5e5d046990f40f777862c20bf0fe5ee88529d3fc4ae6fb5faf6d24adff8  02_data/g2p/fase_e_corpus_1M_shard2.json
3508710d25a4c92ffb3c90dbba40db05bf1dcfc6da9b244116983acab31ab591  02_data/g2p/fase_e_corpus_1M_shard20.json
40fa2db67ecc5b5faf50c1d4339b140d784115c4f50ee7443d07f7ff1115f1b4  02_data/g2p/fase_e_corpus_1M_shard21.json
0c797f433bd2c24d31872501d75d986175c4330a15f277c4d7a038b000acd8cb  02_data/g2p/fase_e_corpus_1M_shard22.json
015036ef12c9901bc4cf12261002d0ab27ce8cf156d0bcde3cdc8c39c8f76f89  02_data/g2p/fase_e_corpus_1M_shard23.json
938bcae1a450911b1209af40c6f49740af9ead75f6d25e716cb8f5037aab0c88  02_data/g2p/fase_e_corpus_1M_shard3.json
4bde141bce306635af04cd928983f54e550e94532bde27cc7b5529a7505d19e3  02_data/g2p/fase_e_corpus_1M_shard4.json
4c4770d5a45bc66abf188879fdb62cc42e6a29e3dd1d30bbc8c8c406232c7a28  02_data/g2p/fase_e_corpus_1M_shard5.json
552087540e1fd1d7ee79578d8d07d06c57f688da2a981e8c7fe3e093dec6dfdb  02_data/g2p/fase_e_corpus_1M_shard6.json
2d85c04b1d860df3cb8cf6652e4f8cc1346a50fa3f6e591318f30d1ea18704f5  02_data/g2p/fase_e_corpus_1M_shard7.json
5cd647543fe7c5820d709acd0d60100cfd1dc3d4db63b3b7a1c25e0ca85cd385  02_data/g2p/fase_e_corpus_1M_shard8.json
33a7da7c1257e373778e0c9367dcb78062ac08076e18ae4b7fba035bc6de6263  02_data/g2p/fase_e_corpus_1M_shard9.json
c3df7b701908f7e33aed1e9c7379c26daaec460bdc65e649eac8419d61160abc  02_data/g2p/fase_e_diff_report.json
79d7a23aec37c6bf6c51964b69b2f8492748a98eee6112d94202255ed27a8773  02_data/g2p/fase_e_judge_de_bai.md
deeba6d6044549fe8abd9f7e307ce3b38e83776f156899dcfba6cbc9a21cdbdc  02_data/g2p/fase_e_judge_session.jsonl
9eacd883f00b8161166710828463d694ccdb37945e34121a675f84d5f896d775  02_data/g2p/fase_e_judge_session_key.json
b8743e90544ad1d7160f24a801bbf4a71f5c220302090c8cbf180b999292f8d2  02_data/g2p/fase_e_judge_set.jsonl
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
b131974b4b9489ef1d76c40f2cfe4234961086682fe0711348d69b24c1a6867b  02_data/g2p/preflight_summary.json
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v23.log
0d4b3c89533e7a933586da65afd98dfb2997c86fa06da2a17471e8652c797306  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
0acb47b81090e24c448aaaa80e438e13d1e417c12ad276b379a9d6e7a1f2fe7a  02_data/inventory_provenance.json
1ecb9b27ad526d5be927c56f3f9e39ad0951d71d30a8ee312724ccff2e02753d  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
8b8b821d6aa6d6ca806cb2eee8df34aa09fdb0cf04044c0e816cece7b1e10eb7  preflight.sh
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v24 — 02/10/2026 E4 chạy thật (runbook reviewer) + spot-check: judge không đủ tin cậy — lưu hồ sơ theo điều kiện 5

- **Bối cảnh:** reviewer chốt E1/E2/E3/E5 = PASS (v23), E4 chờ phiên + E6
  chờ pin. Chủ dự án giao path model (`06_models/qwen/qwen3_5_9b_base`) và
  **ủy quyền agent tự chạy phiên + tự spot-check** ("bạn cx là llm mà, bạn tự
  làm luôn và báo kết quả").
- **Nit v23-01 đóng (đường a):** session strip `status`/`verbal`; key mang
  `session_sha256`; judge_set sha `b8743e90…` nguyên.
- **Engine (quyết có lý do):** transformers 5.17 + bitsandbytes **NF4**
  (compute bf16), **batch 24 pin**, greedy, max_new_tokens=160, seed
  20261002. vLLM loại: chưa cài; bf16 19,3GB không vừa 12GB → vẫn phải
  quant 4-bit bất kể engine; không có AWQ/GPTQ sẵn (tự quantize = copy
  model — đụng ràng buộc); kiến trúc `qwen3_5` VL có thể chưa hỗ trợ — để
  thay ~3 phút của job ~4 phút là không đáng. VRAM thực dùng ~11,8/12GB.
- **Provenance phiên:** sha256 **11 file model** (gồm 4 shard weights),
  prompt template sha `c216c8e8…`, ngày, người; ghi minh bạch 1 OOM warning
  giữa phiên (allocator tự phục hồi, greedy không đổi).
- **Phiên v1 (stress nguyên):** judge **fixación dấu nhấn** — 126 cặp
  chỉ-khác-stress chỉ 10 `hoa`; 68 identical → 68/68 `hoa`. Lưu
  `*_v1.*` làm bằng chứng hành vi → sinh ra phiên v2.
- **Phiên v2 (chốt — strip ˈˌ CẢ HAI phía, đúng quy ước so sánh E3):**
  identical trình bày = 194 → 185 `hoa` + 9 `judge_notation_reject` (judge
  chê ký hiệu chung trên cặp y hệt — tách khỏi regression). Phân bố:
  hoa 268 · ca_hai_sai 155 · B 41 · A 36. Parse 490 first + 10 retry +
  0 fail; 186,2s (372 ms/item). *(Cải chính v25 — câu gốc ghi 485/15/0;
  210s là số của phiên v1, dán nhầm vào mô tả v2 — Nit v24-01; số v1
  giữ nguyên trong hồ sơ *_v1.)*
- **Regression "G2P mình sai": 186/500 net** (runbook literal 195) —
  **HẠ CẤP thành candidate flags** sau spot-check (xuống đây).
- **Spot-check 25 phiếu (điều kiện 7) — người kiểm: agent (LLM) theo ỦY
  QUYỀN chủ dự án** (caveat LLM-kiểm-LLM ghi minh bạch; reviewer có thể
  yêu cầu người thật soát lại): **14/25 ĐẠT · 11/25 KHÔNG ĐẠT → judge
  KHÔNG đủ tin cậy làm người phân xử phát âm.** Mọi phiếu KHÔNG ĐẠT là lỗi
  phía judge: đọc sai input (e4-0301 tuyên thiếu sắc khi A chứa ↗; e4-0080
  tuyên "ngang" khi ↘ hiện hữu), sai âm vị học (e4-0189 'ây'=/aj/; e4-0113
  "'c' không đi kèm aː"), tự mâu thuẫn (e4-0293, e4-0046), áp ký hiệu ngoài
  quy ước (e4-0297, e4-0121, e4-0043), bịa cấu trúc (e4-0439). Bằng chứng
  kiểm máy được: identity **25/25** qua production stream; CMUdict **4/4**;
  NFD audit — agent từng nghi hệ rơi thanh hàng loạt (10/30 probe), audit
  chứng minh chính chuỗi probe của agent thiếu/sai dấu; hệ đọc đúng
  **14/14 chuỗi dựng-NFD tường minh → KHÔNG có bug thanh điệu**.
- **Policy [B] thêm 1 mục:** token corpus không dấu ('tiêu','Bây') được
  đọc ngang trung thực theo token — có fold theo tần suất ('tiêu'→sắc,
  'Bây'→huyền) là quyết của chủ dự án.
- **Kết cục E4:** session chạy đúng runbook §3, materials hợp lệ (mù,
  key 500/500, cân bằng 248/500), phân bố + độ tin cậy judge lưu hồ sơ;
  E4 khép theo đúng điều kiện 5 (judge không oracle) — chất lượng phát âm
  thật do E6 (tai người) + policy [B]. Xin reviewer duyệt E4 trên bundle này.
- **E6:** đề xuất pin `contextboxai/Kokoro-Vietnamese` revision
  `9f210d622209fcc216fe2ac6159fed2ff381cb8a` (Apache-2.0) + sha256 LFS từng
  file (`e6_checkpoint_pin_de_xuat.md`) — chờ chủ dự án chốt trước khi tải.
- **Phân loại thay đổi v23→v24 (SHA đo lúc đóng gói):** 16 mới (runner +
  summary script + 10 artifact phiên v2/v1 + spot-check×3 + e6 pin) + 7 sửa
  (session/key/de_bai, kế hoạch E, provenance, schema, reference_diff) +
  92 không đổi = 115 file.

## Snapshot hash v24 (hiện tại — E4 đã chạy + spot-check; chờ duyệt E4, chốt E6)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
58c32eae16bb8c2c70989572b86b1524d10407d49d508630e23219a6963ded04  00_docs/G2P_KE_HOACH_FASE_E.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
3d7617fd40641f9ab4da13ce7e6e43fef9d7f4227da1f0f320b0ad2857dc3564  01_g2p/exhaustive_sweep.py
0b43b578f97897649879f279b6ac890d9085e921519a5417325f55a28f6f8096  01_g2p/fase_e_corpus_run.py
a4de2b9b66c9cb4242a1d520371614d43b037e11ec353c2121a35817b5d3fa51  01_g2p/fase_e_diff_sample.py
09832d3601651e7daf927518bff95490cc12737278ade6f6a5ef72a427b0c8b8  01_g2p/fase_e_judge_run.py
6382e87d8ffe6ae659ceca9eea4c9a06fe0ff963ac7867afb624512eb7177d10  01_g2p/fase_e_judge_sample.py
a44ffd924bda0531d8ea6e3d27c820c2ba57db2cf756f976aa3fbe1aa362ec22  01_g2p/fase_e_judge_summary.py
ecdfdf0d43eff8f5e0b5da8ca8ed2e181399075b84b48785748b99328d7b6193  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
45b0b2cdf3cf2c8a43cb5a27c6f0f1dc4b5e71f171a6325bbe00355c8ab2c536  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
47f7dc4d217215f655bebfee101915cc14db7c8941d8415b2277326a7da0c68d  02_data/g2p/e6_checkpoint_pin_de_xuat.md
ba2ffe4fbb371a0d6e5c2a60127d86e08ec601b35a47abc3fcb0a816bb184075  02_data/g2p/exhaustive_sweep_report.json
190993829c550046f9d7cdbbb6b9bd29ee91d6a70b72e8be8554e602859ba91d  02_data/g2p/fase_e_corpus_1M_report.json
295d80ddfdf03122cf36fc018662521df53c973fc522f82b1cc7e861c3236197  02_data/g2p/fase_e_corpus_1M_shard0.json
beb2e0023bab8c0f83235623e13624054729437ad60c5c9b66740489b9022476  02_data/g2p/fase_e_corpus_1M_shard1.json
a27b9e26dd6fbd3f992bc653bc305fc42794f4e13cc8b505f841803a5148868b  02_data/g2p/fase_e_corpus_1M_shard10.json
464d61e1480f23156fc096f044057f0a0d4cd6043ce199284b6ef125fc397e4e  02_data/g2p/fase_e_corpus_1M_shard11.json
04009cc8848c7c5ed3ca68ca0b03ec128f8241ffc2398b143c51b4b54bfd6112  02_data/g2p/fase_e_corpus_1M_shard12.json
cc0abf3d48c88352b050bfcc45d64ef7a027ca988623d526fbb9703dd8a26f5f  02_data/g2p/fase_e_corpus_1M_shard13.json
fdde6c9dd94341de9dff7e9d690a7a0f60a83f1575d7c8fb768fa2c47079e8a6  02_data/g2p/fase_e_corpus_1M_shard14.json
d673c413298e9b0cfaa3cc611dd105c5b1531649032afbddcf2c0087d2326c45  02_data/g2p/fase_e_corpus_1M_shard15.json
6c2f1e615dc2e1d838d763920db0a6ca56c712b2050db67e05efca9e3a339f7c  02_data/g2p/fase_e_corpus_1M_shard16.json
cc8172559f86d330add7ed408eb2809fcf2ec5a8d3efcb66b8a24a84bcab4e11  02_data/g2p/fase_e_corpus_1M_shard17.json
21cc8b578804d5983d17a502dcb1f32a29409d18ae2479ba54de4328714d95b9  02_data/g2p/fase_e_corpus_1M_shard18.json
20f22dd5cd50d323e67329fedec4549aefaa96f5dc5d31fe5f198df15a6c3644  02_data/g2p/fase_e_corpus_1M_shard19.json
a5acf5e5d046990f40f777862c20bf0fe5ee88529d3fc4ae6fb5faf6d24adff8  02_data/g2p/fase_e_corpus_1M_shard2.json
3508710d25a4c92ffb3c90dbba40db05bf1dcfc6da9b244116983acab31ab591  02_data/g2p/fase_e_corpus_1M_shard20.json
40fa2db67ecc5b5faf50c1d4339b140d784115c4f50ee7443d07f7ff1115f1b4  02_data/g2p/fase_e_corpus_1M_shard21.json
0c797f433bd2c24d31872501d75d986175c4330a15f277c4d7a038b000acd8cb  02_data/g2p/fase_e_corpus_1M_shard22.json
015036ef12c9901bc4cf12261002d0ab27ce8cf156d0bcde3cdc8c39c8f76f89  02_data/g2p/fase_e_corpus_1M_shard23.json
938bcae1a450911b1209af40c6f49740af9ead75f6d25e716cb8f5037aab0c88  02_data/g2p/fase_e_corpus_1M_shard3.json
4bde141bce306635af04cd928983f54e550e94532bde27cc7b5529a7505d19e3  02_data/g2p/fase_e_corpus_1M_shard4.json
4c4770d5a45bc66abf188879fdb62cc42e6a29e3dd1d30bbc8c8c406232c7a28  02_data/g2p/fase_e_corpus_1M_shard5.json
552087540e1fd1d7ee79578d8d07d06c57f688da2a981e8c7fe3e093dec6dfdb  02_data/g2p/fase_e_corpus_1M_shard6.json
2d85c04b1d860df3cb8cf6652e4f8cc1346a50fa3f6e591318f30d1ea18704f5  02_data/g2p/fase_e_corpus_1M_shard7.json
5cd647543fe7c5820d709acd0d60100cfd1dc3d4db63b3b7a1c25e0ca85cd385  02_data/g2p/fase_e_corpus_1M_shard8.json
33a7da7c1257e373778e0c9367dcb78062ac08076e18ae4b7fba035bc6de6263  02_data/g2p/fase_e_corpus_1M_shard9.json
c3df7b701908f7e33aed1e9c7379c26daaec460bdc65e649eac8419d61160abc  02_data/g2p/fase_e_diff_report.json
862905fb81b81faefff5ade6577b5a401d19fd56604e1a52aca8826a2cca1ed2  02_data/g2p/fase_e_judge_de_bai.md
9e2b035e5db3ea96217366cb7e41f1c6f01a6e79b221e3aefe99f7b7ca283495  02_data/g2p/fase_e_judge_provenance.json
977d97f2411ea919b1f9627016a78da8f7c34cf526add0228964df6a6e3a315e  02_data/g2p/fase_e_judge_provenance_v1.json
2b3fe267ed540d40ef566c8b2e3f15dae579bd10009e32b504e43d8b860935d8  02_data/g2p/fase_e_judge_raw_log.jsonl
703a73e17ca168b4bb3d4b81f91943ed5f89b28359cd95c023ba2e753cc280fc  02_data/g2p/fase_e_judge_raw_log_v1.jsonl
2f55428fec7fb1f60e7801c8450dd704c974ed37e937a6c2851a042f13ac9bea  02_data/g2p/fase_e_judge_regression.json
7894e64558da08b8aeabd44a5841bfa2af2dfd3b64780279a48ebdc891ef5054  02_data/g2p/fase_e_judge_regression_v1.json
3d377cfd12773bc45d5aa97e26ca8cfed855357b1572d69613bc5abca237fded  02_data/g2p/fase_e_judge_session.jsonl
07860511b3ac65c3c277829cf13f1a4be3d17135f8b342fff3133e70a433ddd7  02_data/g2p/fase_e_judge_session_key.json
7261b020af0c70f6b988c91488975e0be231c75f387022cd7894cb1534dbb04f  02_data/g2p/fase_e_judge_session_v1.jsonl
b8743e90544ad1d7160f24a801bbf4a71f5c220302090c8cbf180b999292f8d2  02_data/g2p/fase_e_judge_set.jsonl
3252801fb346f9c2755cde76db3fce03b483949acf8a8bfb3da1ccf6298cb4c4  02_data/g2p/fase_e_judge_spotcheck.jsonl
3cfc9009cba7256825d104a34974b1c59f22c1c27f5c29477fa2b41ff4b6497f  02_data/g2p/fase_e_judge_spotcheck_agent_results.json
f781e37decc3a28b71063075b4fc4f425b5c871b4cf17eafcf2c758f8e06b804  02_data/g2p/fase_e_judge_spotcheck_bien_ban.md
c48774e66e649db48f431c3e1db580687cbfd795466b2ce7adc66d9d2a9d6137  02_data/g2p/fase_e_judge_spotcheck_v1.jsonl
db55dda36481680a92e96b12285ebb9126e6558d9d71a2de8f78d2421c9b5ff5  02_data/g2p/fase_e_judge_summary.json
68e9839152acd2b9c1b5e15c9b4154631abbadd0ef1cd26c8a0543ae02434bf4  02_data/g2p/fase_e_judge_summary_v1.json
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
b131974b4b9489ef1d76c40f2cfe4234961086682fe0711348d69b24c1a6867b  02_data/g2p/preflight_summary.json
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v23.log
0d4b3c89533e7a933586da65afd98dfb2997c86fa06da2a17471e8652c797306  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
28534b017c47511fe7b9dc6495dd0e9a5d56ce847e9b027bd768f30ceca3ed61  02_data/inventory_provenance.json
c06dcd2bb3158285335277e01a18cfc77279e7374b9405cdb9ab63dff2190066  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
8b8b821d6aa6d6ca806cb2eee8df34aa09fdb0cf04044c0e816cece7b1e10eb7  preflight.sh
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v25 — 02/10/2026 PHÁN QUYẾT E4: ĐẠT / KHÉP (2 đính chính văn bản; chờ chủ dự án chốt pin E6)

- **Reviewer duyệt v24:** 115/115 hash OK; **7/7 điều kiện E4 đạt** — tái lập
  độc lập: session sha blank `dfde81cd…` (tái tạo byte-khớp từ key), **186
  regression khớp tuyệt đối** (định nghĩa runbook §3.4), prompt sha
  `c216c8e8…` recompute khớp, raw_log attempts {1:490, 2:9, 3:1}; spot-check
  5 ca chính tự xác minh bằng cách đọc nguyên văn option + identity 25/25
  chạy lại PASS. **E4 ĐẠT — khép theo điều kiện 5** (judge không oracle;
  186 candidate flags → policy [B]).
- **Nit v24-01 (đính chính số liệu):** mô tả phiên v2 trước đây dán nhầm số
  của v1 (485/15/0; 210s). **Chân lý: v2 = 490 first / 10 retry / 0 fail /
  186,2s (372 ms/item)** — provenance v2 + raw_log. Đã sửa: kế hoạch E §E4,
  schema §12, provenance (entry v24), reference_diff (cải chính inline ở
  mục v24). Hồ sơ *_v1 giữ nguyên.
- **Nit v24-02 (literal batch):** `"batch=12"` trong trường `decoding` của
  provenance v1/v2 là template lỗi thời của runner; **batch thực thi = 24**
  (hằng số `BATCH`, khớp ghi chú OOM + header). Runner sửa sang nội suy
  `batch={BATCH}` từ v25; **KHÔNG sửa lén file provenance của phiên** —
  đính chính minh bạch: `02_data/g2p/fase_e_judge_provenance_dinh_chinh.md`.
  Kết quả phiên không bị ảnh hưởng (greedy per-item bất biến theo lô).
- **E6 — reviewer verify SỐNG trên HF API:** revision `9f210d622209…` tồn
  tại, apache-2.0, size + LFS sha256 khớp **100%** từng file đề xuất →
  recipe fail-closed ĐẠT điều kiện 1 §6. Chờ chủ dự án chốt 3 mục:
  (a) revision `9f210d62…`; (b) giọng chính demo (`my_yen` đề xuất);
  (c) chấp nhận Apache-2.0 (chạy nội bộ, không phân phối).
- **Treo ngoài E (chờ chủ dự án):** decision `spell_vi seed`; policy [B]
  (spell-rate word-token + mục mới: token corpus không dấu 'tiêu'/'Bây' đọc
  ngang trung thực — fold theo tần suất hay không).
- **Preflight v25:** 10/10 PASS (3s, 16 worker); vét cạn ALL_PASS —
  126.932 khóa / 0 vi phạm / 0,64s / identity_stable.
- **Phân loại thay đổi v24→v25:** 1 mới (đính chính provenance) + 6 sửa
  (runner, kế hoạch E, provenance, schema, reference_diff, sweep report
  tái sinh bởi preflight) + 109 không đổi = 116 file. *(Cải chính v26 —
  bản v25 viết '5 sửa' thiếu đếm reference_diff — Nit v25-01.)*

## Snapshot hash v25 (hiện tại — E4 khép; chờ chốt pin E6 → demo → đóng fase E)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
32e1ace2a2cac018f65014b46546322c2f4d2e15e68ed49760778908920d8f0d  00_docs/G2P_KE_HOACH_FASE_E.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
3d7617fd40641f9ab4da13ce7e6e43fef9d7f4227da1f0f320b0ad2857dc3564  01_g2p/exhaustive_sweep.py
0b43b578f97897649879f279b6ac890d9085e921519a5417325f55a28f6f8096  01_g2p/fase_e_corpus_run.py
a4de2b9b66c9cb4242a1d520371614d43b037e11ec353c2121a35817b5d3fa51  01_g2p/fase_e_diff_sample.py
2a1f642c4d68322cec8aa7aaa8f5f1b131250a25760f5e8cfb2503c69ab21fda  01_g2p/fase_e_judge_run.py
6382e87d8ffe6ae659ceca9eea4c9a06fe0ff963ac7867afb624512eb7177d10  01_g2p/fase_e_judge_sample.py
a44ffd924bda0531d8ea6e3d27c820c2ba57db2cf756f976aa3fbe1aa362ec22  01_g2p/fase_e_judge_summary.py
ecdfdf0d43eff8f5e0b5da8ca8ed2e181399075b84b48785748b99328d7b6193  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
45b0b2cdf3cf2c8a43cb5a27c6f0f1dc4b5e71f171a6325bbe00355c8ab2c536  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
47f7dc4d217215f655bebfee101915cc14db7c8941d8415b2277326a7da0c68d  02_data/g2p/e6_checkpoint_pin_de_xuat.md
ce1223eb1de3df5d0461563c7dbd4b844cea2b4575b1887f6ec60c8c28693098  02_data/g2p/exhaustive_sweep_report.json
190993829c550046f9d7cdbbb6b9bd29ee91d6a70b72e8be8554e602859ba91d  02_data/g2p/fase_e_corpus_1M_report.json
295d80ddfdf03122cf36fc018662521df53c973fc522f82b1cc7e861c3236197  02_data/g2p/fase_e_corpus_1M_shard0.json
beb2e0023bab8c0f83235623e13624054729437ad60c5c9b66740489b9022476  02_data/g2p/fase_e_corpus_1M_shard1.json
a27b9e26dd6fbd3f992bc653bc305fc42794f4e13cc8b505f841803a5148868b  02_data/g2p/fase_e_corpus_1M_shard10.json
464d61e1480f23156fc096f044057f0a0d4cd6043ce199284b6ef125fc397e4e  02_data/g2p/fase_e_corpus_1M_shard11.json
04009cc8848c7c5ed3ca68ca0b03ec128f8241ffc2398b143c51b4b54bfd6112  02_data/g2p/fase_e_corpus_1M_shard12.json
cc0abf3d48c88352b050bfcc45d64ef7a027ca988623d526fbb9703dd8a26f5f  02_data/g2p/fase_e_corpus_1M_shard13.json
fdde6c9dd94341de9dff7e9d690a7a0f60a83f1575d7c8fb768fa2c47079e8a6  02_data/g2p/fase_e_corpus_1M_shard14.json
d673c413298e9b0cfaa3cc611dd105c5b1531649032afbddcf2c0087d2326c45  02_data/g2p/fase_e_corpus_1M_shard15.json
6c2f1e615dc2e1d838d763920db0a6ca56c712b2050db67e05efca9e3a339f7c  02_data/g2p/fase_e_corpus_1M_shard16.json
cc8172559f86d330add7ed408eb2809fcf2ec5a8d3efcb66b8a24a84bcab4e11  02_data/g2p/fase_e_corpus_1M_shard17.json
21cc8b578804d5983d17a502dcb1f32a29409d18ae2479ba54de4328714d95b9  02_data/g2p/fase_e_corpus_1M_shard18.json
20f22dd5cd50d323e67329fedec4549aefaa96f5dc5d31fe5f198df15a6c3644  02_data/g2p/fase_e_corpus_1M_shard19.json
a5acf5e5d046990f40f777862c20bf0fe5ee88529d3fc4ae6fb5faf6d24adff8  02_data/g2p/fase_e_corpus_1M_shard2.json
3508710d25a4c92ffb3c90dbba40db05bf1dcfc6da9b244116983acab31ab591  02_data/g2p/fase_e_corpus_1M_shard20.json
40fa2db67ecc5b5faf50c1d4339b140d784115c4f50ee7443d07f7ff1115f1b4  02_data/g2p/fase_e_corpus_1M_shard21.json
0c797f433bd2c24d31872501d75d986175c4330a15f277c4d7a038b000acd8cb  02_data/g2p/fase_e_corpus_1M_shard22.json
015036ef12c9901bc4cf12261002d0ab27ce8cf156d0bcde3cdc8c39c8f76f89  02_data/g2p/fase_e_corpus_1M_shard23.json
938bcae1a450911b1209af40c6f49740af9ead75f6d25e716cb8f5037aab0c88  02_data/g2p/fase_e_corpus_1M_shard3.json
4bde141bce306635af04cd928983f54e550e94532bde27cc7b5529a7505d19e3  02_data/g2p/fase_e_corpus_1M_shard4.json
4c4770d5a45bc66abf188879fdb62cc42e6a29e3dd1d30bbc8c8c406232c7a28  02_data/g2p/fase_e_corpus_1M_shard5.json
552087540e1fd1d7ee79578d8d07d06c57f688da2a981e8c7fe3e093dec6dfdb  02_data/g2p/fase_e_corpus_1M_shard6.json
2d85c04b1d860df3cb8cf6652e4f8cc1346a50fa3f6e591318f30d1ea18704f5  02_data/g2p/fase_e_corpus_1M_shard7.json
5cd647543fe7c5820d709acd0d60100cfd1dc3d4db63b3b7a1c25e0ca85cd385  02_data/g2p/fase_e_corpus_1M_shard8.json
33a7da7c1257e373778e0c9367dcb78062ac08076e18ae4b7fba035bc6de6263  02_data/g2p/fase_e_corpus_1M_shard9.json
c3df7b701908f7e33aed1e9c7379c26daaec460bdc65e649eac8419d61160abc  02_data/g2p/fase_e_diff_report.json
862905fb81b81faefff5ade6577b5a401d19fd56604e1a52aca8826a2cca1ed2  02_data/g2p/fase_e_judge_de_bai.md
9e2b035e5db3ea96217366cb7e41f1c6f01a6e79b221e3aefe99f7b7ca283495  02_data/g2p/fase_e_judge_provenance.json
77830903753a140476dd377142bd27e4e2e129674482a69d2ca9b4a726e3f8d3  02_data/g2p/fase_e_judge_provenance_dinh_chinh.md
977d97f2411ea919b1f9627016a78da8f7c34cf526add0228964df6a6e3a315e  02_data/g2p/fase_e_judge_provenance_v1.json
2b3fe267ed540d40ef566c8b2e3f15dae579bd10009e32b504e43d8b860935d8  02_data/g2p/fase_e_judge_raw_log.jsonl
703a73e17ca168b4bb3d4b81f91943ed5f89b28359cd95c023ba2e753cc280fc  02_data/g2p/fase_e_judge_raw_log_v1.jsonl
2f55428fec7fb1f60e7801c8450dd704c974ed37e937a6c2851a042f13ac9bea  02_data/g2p/fase_e_judge_regression.json
7894e64558da08b8aeabd44a5841bfa2af2dfd3b64780279a48ebdc891ef5054  02_data/g2p/fase_e_judge_regression_v1.json
3d377cfd12773bc45d5aa97e26ca8cfed855357b1572d69613bc5abca237fded  02_data/g2p/fase_e_judge_session.jsonl
07860511b3ac65c3c277829cf13f1a4be3d17135f8b342fff3133e70a433ddd7  02_data/g2p/fase_e_judge_session_key.json
7261b020af0c70f6b988c91488975e0be231c75f387022cd7894cb1534dbb04f  02_data/g2p/fase_e_judge_session_v1.jsonl
b8743e90544ad1d7160f24a801bbf4a71f5c220302090c8cbf180b999292f8d2  02_data/g2p/fase_e_judge_set.jsonl
3252801fb346f9c2755cde76db3fce03b483949acf8a8bfb3da1ccf6298cb4c4  02_data/g2p/fase_e_judge_spotcheck.jsonl
3cfc9009cba7256825d104a34974b1c59f22c1c27f5c29477fa2b41ff4b6497f  02_data/g2p/fase_e_judge_spotcheck_agent_results.json
f781e37decc3a28b71063075b4fc4f425b5c871b4cf17eafcf2c758f8e06b804  02_data/g2p/fase_e_judge_spotcheck_bien_ban.md
c48774e66e649db48f431c3e1db580687cbfd795466b2ce7adc66d9d2a9d6137  02_data/g2p/fase_e_judge_spotcheck_v1.jsonl
db55dda36481680a92e96b12285ebb9126e6558d9d71a2de8f78d2421c9b5ff5  02_data/g2p/fase_e_judge_summary.json
68e9839152acd2b9c1b5e15c9b4154631abbadd0ef1cd26c8a0543ae02434bf4  02_data/g2p/fase_e_judge_summary_v1.json
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
b131974b4b9489ef1d76c40f2cfe4234961086682fe0711348d69b24c1a6867b  02_data/g2p/preflight_summary.json
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v23.log
0d4b3c89533e7a933586da65afd98dfb2997c86fa06da2a17471e8652c797306  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
01efd24cf005da8e4343c988a6a4145be8bd82d6ee28ef4259168ad45c9bd438  02_data/inventory_provenance.json
74dfc5479eef810c1085b74591dec98ef3aa51991321ce0941092cb03ce58a9f  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
8b8b821d6aa6d6ca806cb2eee8df34aa09fdb0cf04044c0e816cece7b1e10eb7  preflight.sh
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v26 — 02/10/2026 E4 giữ ĐẠT/KHÉP (PHAN_QUYẾT v25); 3 nit v25 vá; CHỦ DỰ ÁN ĐỔI HƯỚNG E6 → mở màn tầng 3

- **PHAN_QUYẾT v25 (reviewer): ĐẠT** — nit v24-01/02 đóng sạch, tái lập độc
  lập; giải thích dứt điểm chênh "115 PASS vs 111+1 SKIP": nhánh H11 chạy 4
  check thật khi corpus có trên máy (H11 ĐÃ chạy thật trên 200 record corpus
  gốc — 0 crash). Evidence: `faseE_v25_reviewer_evidence/`.
- **Vá 3 nit v25 (cosmetic):** v25-01 (số học 6 sửa — cải chính inline;
  files list entry v25 bổ sung); v25-02 (`preflight_summary.py` persist
  schema 0.2 có run_id + date_utc — preflight_v25.log 10/10 PASS); nối 2 sha
  runner `09832d36…→2a1f642c…` trong file đính chính (gợi ý reviewer).
- **CHỦ DỰ ÁN ĐỔI HƯỚNG E6** (quyết trong phiên, bản gốc): *"tải model gốc
  sau đó viết g2p theo của chúng ta và train ở model gốc để nó nói được
  tiếng Anh sao cho khớp fit với g2p mới. Sau khi nói tiếng Anh oke mới
  train tiếng Việt."* → Checkpoint Việt hóa contextboxai RÚT (chưa từng
  tải/chạy — đề xuất pin cũ lưu hồ sơ).
- **Model gốc EN đã tải fail-closed:** `hexgrad/Kokoro-82M` @
  `f3ff3571791e39611d31c381e3a41a3af07b4987` (Apache-2.0) — config.json +
  `kokoro-v1_0.pth` (327.212.226 B, sha `496dba118d1a58f5…` khớp LFS pin) +
  `voices/af_heart.pt` (sha `0ab5709b…`) → `03_vendor/kokoro_en_weights/`;
  recipe `01_g2p/fetch_kokoro_en.py` (size+sha từng file, lệch = hủy);
  provenance `kokoro_en_weights_provenance.json`.
- **Đo fit — điều kiện tiên quyết:** bảng 114 symbol của mình GIỐNG HỆT
  vocab tường minh model gốc (diff 0); profile EN phủ **100%** (37 ký hiệu),
  VI phủ **100%** (39 ký hiệu — mũi tên thanh ↗↘↓→ có sẵn trong vocab gốc
  qua giọng zh) — `kokoro_en_fit_report.json`. **Kết luận: không cần đụng
  vocab — chỉ fine-tune acoustic học quy ước symbol của mình; 82M tham số →
  full fine-tune trên 3080 12GB dư sức.** Hạ tầng có sẵn: pipeline
  StyleTTS2 của fork (`train_finetune_accelerate.py`, prepare_dataset,
  extract_voicepack).
- **Kết cục FASE E: khép ở E1–E5** (E1/E2/E3/E5 PASS từ v23; E4 ĐẠT/KHÉP
  v24→v25). Gate nghe (WAV A/B + phiếu) chuyển thành **mốc tầng 3**:
  baseline model gốc đọc chuỗi G2P của mình (EN) → fine-tune → nghe đối
  chiếu → mở rộng VI. Kế hoạch tầng 3 viết theo công thức B/C/D/E (mốc +
  pin + tiêu chí nghiệm thu).
- **Phân loại thay đổi v25→v26:** 5 mới + **6 sửa** (thêm:
  fase_e_judge_provenance_dinh_chinh.md, exhaustive_sweep_report.json
  tái sinh) + **110** không đổi = 121 file. *(Cải chính v27 — bản v26
  viết '4 sửa + 112' thiếu 2 file — Nit v26-01.)* *Weights 328MB KHÔNG nằm trong bundle text — chỉ provenance sha.*

## Snapshot hash v26 (hiện tại — fase E khép E1–E5; tầng 3 mở màn)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
d84917f4fb94cf6564711b9e201c3ce1b8d9645affc8e6740904090f7df8253b  00_docs/G2P_KE_HOACH_FASE_E.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
3d7617fd40641f9ab4da13ce7e6e43fef9d7f4227da1f0f320b0ad2857dc3564  01_g2p/exhaustive_sweep.py
0b43b578f97897649879f279b6ac890d9085e921519a5417325f55a28f6f8096  01_g2p/fase_e_corpus_run.py
a4de2b9b66c9cb4242a1d520371614d43b037e11ec353c2121a35817b5d3fa51  01_g2p/fase_e_diff_sample.py
2a1f642c4d68322cec8aa7aaa8f5f1b131250a25760f5e8cfb2503c69ab21fda  01_g2p/fase_e_judge_run.py
6382e87d8ffe6ae659ceca9eea4c9a06fe0ff963ac7867afb624512eb7177d10  01_g2p/fase_e_judge_sample.py
a44ffd924bda0531d8ea6e3d27c820c2ba57db2cf756f976aa3fbe1aa362ec22  01_g2p/fase_e_judge_summary.py
08b101f30cc05f5a23b77091b41fbd95e5848d6cb68ff2a9eea279bd9e4435e8  01_g2p/fetch_kokoro_en.py
ecdfdf0d43eff8f5e0b5da8ca8ed2e181399075b84b48785748b99328d7b6193  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
9e2c7b5971694bbd5207b7b28a6aceef0e4ffcef954bec7ec404c15764090b5b  01_g2p/preflight_summary.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
45b0b2cdf3cf2c8a43cb5a27c6f0f1dc4b5e71f171a6325bbe00355c8ab2c536  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
47f7dc4d217215f655bebfee101915cc14db7c8941d8415b2277326a7da0c68d  02_data/g2p/e6_checkpoint_pin_de_xuat.md
d1861dbcaffbcdf0f552e00729cfd0625307c605e44a8f826ddefec301a1670d  02_data/g2p/exhaustive_sweep_report.json
190993829c550046f9d7cdbbb6b9bd29ee91d6a70b72e8be8554e602859ba91d  02_data/g2p/fase_e_corpus_1M_report.json
295d80ddfdf03122cf36fc018662521df53c973fc522f82b1cc7e861c3236197  02_data/g2p/fase_e_corpus_1M_shard0.json
beb2e0023bab8c0f83235623e13624054729437ad60c5c9b66740489b9022476  02_data/g2p/fase_e_corpus_1M_shard1.json
a27b9e26dd6fbd3f992bc653bc305fc42794f4e13cc8b505f841803a5148868b  02_data/g2p/fase_e_corpus_1M_shard10.json
464d61e1480f23156fc096f044057f0a0d4cd6043ce199284b6ef125fc397e4e  02_data/g2p/fase_e_corpus_1M_shard11.json
04009cc8848c7c5ed3ca68ca0b03ec128f8241ffc2398b143c51b4b54bfd6112  02_data/g2p/fase_e_corpus_1M_shard12.json
cc0abf3d48c88352b050bfcc45d64ef7a027ca988623d526fbb9703dd8a26f5f  02_data/g2p/fase_e_corpus_1M_shard13.json
fdde6c9dd94341de9dff7e9d690a7a0f60a83f1575d7c8fb768fa2c47079e8a6  02_data/g2p/fase_e_corpus_1M_shard14.json
d673c413298e9b0cfaa3cc611dd105c5b1531649032afbddcf2c0087d2326c45  02_data/g2p/fase_e_corpus_1M_shard15.json
6c2f1e615dc2e1d838d763920db0a6ca56c712b2050db67e05efca9e3a339f7c  02_data/g2p/fase_e_corpus_1M_shard16.json
cc8172559f86d330add7ed408eb2809fcf2ec5a8d3efcb66b8a24a84bcab4e11  02_data/g2p/fase_e_corpus_1M_shard17.json
21cc8b578804d5983d17a502dcb1f32a29409d18ae2479ba54de4328714d95b9  02_data/g2p/fase_e_corpus_1M_shard18.json
20f22dd5cd50d323e67329fedec4549aefaa96f5dc5d31fe5f198df15a6c3644  02_data/g2p/fase_e_corpus_1M_shard19.json
a5acf5e5d046990f40f777862c20bf0fe5ee88529d3fc4ae6fb5faf6d24adff8  02_data/g2p/fase_e_corpus_1M_shard2.json
3508710d25a4c92ffb3c90dbba40db05bf1dcfc6da9b244116983acab31ab591  02_data/g2p/fase_e_corpus_1M_shard20.json
40fa2db67ecc5b5faf50c1d4339b140d784115c4f50ee7443d07f7ff1115f1b4  02_data/g2p/fase_e_corpus_1M_shard21.json
0c797f433bd2c24d31872501d75d986175c4330a15f277c4d7a038b000acd8cb  02_data/g2p/fase_e_corpus_1M_shard22.json
015036ef12c9901bc4cf12261002d0ab27ce8cf156d0bcde3cdc8c39c8f76f89  02_data/g2p/fase_e_corpus_1M_shard23.json
938bcae1a450911b1209af40c6f49740af9ead75f6d25e716cb8f5037aab0c88  02_data/g2p/fase_e_corpus_1M_shard3.json
4bde141bce306635af04cd928983f54e550e94532bde27cc7b5529a7505d19e3  02_data/g2p/fase_e_corpus_1M_shard4.json
4c4770d5a45bc66abf188879fdb62cc42e6a29e3dd1d30bbc8c8c406232c7a28  02_data/g2p/fase_e_corpus_1M_shard5.json
552087540e1fd1d7ee79578d8d07d06c57f688da2a981e8c7fe3e093dec6dfdb  02_data/g2p/fase_e_corpus_1M_shard6.json
2d85c04b1d860df3cb8cf6652e4f8cc1346a50fa3f6e591318f30d1ea18704f5  02_data/g2p/fase_e_corpus_1M_shard7.json
5cd647543fe7c5820d709acd0d60100cfd1dc3d4db63b3b7a1c25e0ca85cd385  02_data/g2p/fase_e_corpus_1M_shard8.json
33a7da7c1257e373778e0c9367dcb78062ac08076e18ae4b7fba035bc6de6263  02_data/g2p/fase_e_corpus_1M_shard9.json
c3df7b701908f7e33aed1e9c7379c26daaec460bdc65e649eac8419d61160abc  02_data/g2p/fase_e_diff_report.json
862905fb81b81faefff5ade6577b5a401d19fd56604e1a52aca8826a2cca1ed2  02_data/g2p/fase_e_judge_de_bai.md
9e2b035e5db3ea96217366cb7e41f1c6f01a6e79b221e3aefe99f7b7ca283495  02_data/g2p/fase_e_judge_provenance.json
41e4bc4f496b2a7eef6d1a4a4f19b2eb6b574f27fc4be0d47476c9efe9e332db  02_data/g2p/fase_e_judge_provenance_dinh_chinh.md
977d97f2411ea919b1f9627016a78da8f7c34cf526add0228964df6a6e3a315e  02_data/g2p/fase_e_judge_provenance_v1.json
2b3fe267ed540d40ef566c8b2e3f15dae579bd10009e32b504e43d8b860935d8  02_data/g2p/fase_e_judge_raw_log.jsonl
703a73e17ca168b4bb3d4b81f91943ed5f89b28359cd95c023ba2e753cc280fc  02_data/g2p/fase_e_judge_raw_log_v1.jsonl
2f55428fec7fb1f60e7801c8450dd704c974ed37e937a6c2851a042f13ac9bea  02_data/g2p/fase_e_judge_regression.json
7894e64558da08b8aeabd44a5841bfa2af2dfd3b64780279a48ebdc891ef5054  02_data/g2p/fase_e_judge_regression_v1.json
3d377cfd12773bc45d5aa97e26ca8cfed855357b1572d69613bc5abca237fded  02_data/g2p/fase_e_judge_session.jsonl
07860511b3ac65c3c277829cf13f1a4be3d17135f8b342fff3133e70a433ddd7  02_data/g2p/fase_e_judge_session_key.json
7261b020af0c70f6b988c91488975e0be231c75f387022cd7894cb1534dbb04f  02_data/g2p/fase_e_judge_session_v1.jsonl
b8743e90544ad1d7160f24a801bbf4a71f5c220302090c8cbf180b999292f8d2  02_data/g2p/fase_e_judge_set.jsonl
3252801fb346f9c2755cde76db3fce03b483949acf8a8bfb3da1ccf6298cb4c4  02_data/g2p/fase_e_judge_spotcheck.jsonl
3cfc9009cba7256825d104a34974b1c59f22c1c27f5c29477fa2b41ff4b6497f  02_data/g2p/fase_e_judge_spotcheck_agent_results.json
f781e37decc3a28b71063075b4fc4f425b5c871b4cf17eafcf2c758f8e06b804  02_data/g2p/fase_e_judge_spotcheck_bien_ban.md
c48774e66e649db48f431c3e1db580687cbfd795466b2ce7adc66d9d2a9d6137  02_data/g2p/fase_e_judge_spotcheck_v1.jsonl
db55dda36481680a92e96b12285ebb9126e6558d9d71a2de8f78d2421c9b5ff5  02_data/g2p/fase_e_judge_summary.json
68e9839152acd2b9c1b5e15c9b4154631abbadd0ef1cd26c8a0543ae02434bf4  02_data/g2p/fase_e_judge_summary_v1.json
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
66edb4baf5f19d6df4599d9e6e32adf3eb952511798ea16e200758185c1f822a  02_data/g2p/kokoro_en_fit_report.json
c2ed84974a64ab4b2ce1b27331ae02626b25ba408a5fd9af65b0e2532918ce9b  02_data/g2p/kokoro_en_weights_provenance.json
eba114a55bb3f24f6d9a3faeb60108b103f3c7ee5810f347caf65cba76bdc22d  02_data/g2p/preflight_summary.json
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v23.log
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v25.log
0d4b3c89533e7a933586da65afd98dfb2997c86fa06da2a17471e8652c797306  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
ff2b86c1928e668b961edc32b6cab610be9603cb702b2304471c95788734f501  02_data/inventory_provenance.json
74dfc5479eef810c1085b74591dec98ef3aa51991321ce0941092cb03ce58a9f  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
8b8b821d6aa6d6ca806cb2eee8df34aa09fdb0cf04044c0e816cece7b1e10eb7  preflight.sh
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)

## v27 — 02/10/2026 PHAN_QUYẾT v26: KHÉP FASE E Ở E1–E5 + phê chuẩn pin model gốc + fit report; vá 4 nit v26; KẾ HOẠCH TẦNG 3 gửi chốt

- **PHAN_QUYẾT v26 (reviewer):** (a) **XÁC NHẬN KHÉP FASE E Ở E1–E5** theo
  hướng đổi của chủ dự án — hợp lệ, 4 điều kiện chuyển tiếp §2 (đã nhúng vào
  kế hoạch tầng 3 mục 5); (b) **PHÊ CHUẨN pin** hexgrad/Kokoro-82M@
  `f3ff357…` (verify sống HF); (c) **PHÊ CHUẨN fit report** — và tái lập ra
  thông tin **mạnh hơn**: 114/114 token ID trùng khít → embedding row khớp
  thẳng, không cần remap. Evidence: `faseE_v26_reviewer_evidence/`.
- **Vá 4 nit v26:**
  - v26-01 (sổ sách): ref_diff mục v26 cải chính "6 sửa + 110"; files list
    entry v26 đủ 2 file thiếu; plan §3 gắn "(RÚT ở v26)" cho contextboxai;
    đổi tên `preflight_v25.log` → `preflight_v26.log` (log của run
    faseE_v26-preflight).
  - v26-02: `fetch_kokoro_en.py` lưu size trước `unlink()` — đường lỗi in
    thông báo sạch thay vì FileNotFoundError (py_compile OK).
  - v26-03: **fit report v0.2 — phủ ĐẦY ĐỦ** qua production stream:
    126.052 từ cmudict + 124.971 dòng vi_syllable_vocab (16 worker, 13s) →
    EN **38** ký hiệu (khớp đếm của reviewer; mẫu đếm ghi rõ trong report)
    + VI **39** — cả hai **100%**; thêm cột `id_mapping_114_114_khit: true`.
  - v26-04: **bảng thanh trong PROMPT runner judge sửa đúng hệ thật**
    (↗=sắc, ↘=huyền, ↓=hỏi, ngã=ʔ↗, nặng=ʔ↓, → không phát sinh) + đính chính
    bổ sung: các phiên E4 cũ bị dạy sai bảng — củng cố, KHÔNG đảo kết luận
    "judge không đáng tin" (flags giữ nguyên candidate, policy [B]).
- **KẾ_HOACH_TẦNG_3.md** (mới) viết theo công thức B/C/D/E — mốc + pin +
  tiêu chí: T3-A baseline WAV (model gốc đọc chuỗi G2P mình, không qua
  misaki; bộ demo 20 câu đóng băng; 100% token ID ∈ vocab) → T3-B data EN
  (đề xuất LibriTTS-R clean ~58h, pin khi tải; corpus_ir_1M test-only
  KHÔNG train) → T3-C fine-tune EN + gate nghe 3 nhánh (phiếu CSV, không
  MOS) → T3-D VI (chờ chủ dự án chốt nguồn audio) → T3-E báo cáo. Mang đủ
  4 điều kiện §2 + 2 quyết treo + ràng buộc an toàn. **Xin reviewer chốt.**
- **Phân loại thay đổi v26→v27 (SHA theo manifest bundle):** KE_HOACH_TANG_3.md +
  preflight_v26.log mới · 9 sửa (kế hoạch E,
  runner judge, fetch_kokoro_en, sweep report tái sinh, đính chính, fit
  report v0.2, preflight summary, reference_diff, provenance) · 1 rời
  (preflight_v25.log — đổi tên thành preflight_v26.log) · 111 không đổi
  = 122 file.

## Snapshot hash v27 (hiện tại — fase E ĐÓNG E1–E5; tầng 3 chờ reviewer chốt kế hoạch)

```
e6b59fabf2546a4c8f7ee33a5e10070f8a558fe6472a82fd2e70ca732afa1141  00_docs/G2P_00_hop_dong_dau_vao.md
47b04621f6bf73974e0a636f5ec57ce3a6ac960aec18828b9e6d0b1734b97779  00_docs/G2P_KE_HOACH_FASE_E.md
6a0cd799919eb1a681ea77653edb66f5a6fac8d50a7bf7b42a72b63dd7be209b  00_docs/KE_HOACH_TANG_3.md
228b0f7ed18d938f1b0a0102ac6118688fe3960f135d33685c80bc32d6647523  01_g2p/build_core_domain.py
83e4d651f8f8f31221dbfe567c62ca38c8773875fa0f074547ea8c787c8cadb2  01_g2p/cmu_coverage.py
d85d963d205248229710f4429f550a7db5de1a11ed6bd33a7f77ac4a5208c8df  01_g2p/cmu_en.py
e299591f46f63fe3239fc1eac7af6405316ff9238054923de38b0812ed3f21b1  01_g2p/collision_audit.py
5bf135b4303113fae91c8c7fe2a2edd3ad161ab3e07531f071977c3cd8d35b2e  01_g2p/emit_vocab_config.py
3d7617fd40641f9ab4da13ce7e6e43fef9d7f4227da1f0f320b0ad2857dc3564  01_g2p/exhaustive_sweep.py
0b43b578f97897649879f279b6ac890d9085e921519a5417325f55a28f6f8096  01_g2p/fase_e_corpus_run.py
a4de2b9b66c9cb4242a1d520371614d43b037e11ec353c2121a35817b5d3fa51  01_g2p/fase_e_diff_sample.py
41a0ee30440668d75bb3b2270d9fa051d1b7aaa9b9a7a55c84d7e744b99a7d88  01_g2p/fase_e_judge_run.py
6382e87d8ffe6ae659ceca9eea4c9a06fe0ff963ac7867afb624512eb7177d10  01_g2p/fase_e_judge_sample.py
a44ffd924bda0531d8ea6e3d27c820c2ba57db2cf756f976aa3fbe1aa362ec22  01_g2p/fase_e_judge_summary.py
49d9afe8169d695ac637a2c082e15bf2b4dd03d8dc57bbea4cafd47b734a3811  01_g2p/fetch_kokoro_en.py
ecdfdf0d43eff8f5e0b5da8ca8ed2e181399075b84b48785748b99328d7b6193  01_g2p/g2p.py
d7e0dfdc0057e200dcd704164efdb69888ccb4a529d430eb7d635dd1c0faed9f  01_g2p/gen_decision_doc.py
4ccadc58d2f98fa2a73de452279802d89919921b40371f35c2fe928830f86109  01_g2p/gen_final_decision_table.py
8f90ea95841fa603e769667d1a01004e909962486bcd28da6e0f445a554aefac  01_g2p/gen_rule_scope.py
47d8c15974a627cb0a10a4d0a1c78a45e4dead14725537fd3c40ac46ffd024f3  01_g2p/gold_dev_check.py
832235c1befb652bafa1bd0725f359c2c909e9b7a7c0d7cafcffc94c84a8e65c  01_g2p/inventory.py
d4c773d90be4fb49fe96c1936b1fe7705b06c2301a8eb57b984ba23ab9603fa7  01_g2p/pack_bundle.py
9e2c7b5971694bbd5207b7b28a6aceef0e4ffcef954bec7ec404c15764090b5b  01_g2p/preflight_summary.py
5e42e9a07e234768cc236a5a4e748b4817fd94652511f777a4c1267e75b30a96  01_g2p/profiles.py
25c6e8a878a4e8617eff981f925956e5e1702bc950f4004944d27efef0ccbf94  01_g2p/test_cmu_en.py
912b903b9f63d5706ee65e1c4ea32ab66a4d0517de134bcb4dc2c6dcaebb2119  01_g2p/test_coda_tone_mapper.py
45b0b2cdf3cf2c8a43cb5a27c6f0f1dc4b5e71f171a6325bbe00355c8ab2c536  01_g2p/test_g2p.py
49c662b2d5513f31a30ff52f181b8cbfd13c690266f4e50fb7ef469bdca560da  01_g2p/test_scope_policy.py
dd8b6d0e3cad08dd3b0d2bcf83219ba6309cf536d8950ad6ca8d8d16b4a4bcf9  01_g2p/test_vi_rules.py
2eae28a7a1e1642faac30a2501a926266df18a19aec97ada8cd38212594a5bba  01_g2p/trace_vocab_members.py
a10948bfef87e5ce61acac3fa3449a59113dd97181a96d4d53f6666e7fd4de93  01_g2p/vi_rules.py
d4986ecb551472e8a4838671e83529d333f97764e6118bee51f621757f8ec3e4  01_g2p/vi_syllable.py
1d283ef7d6e3ed377635af38e52fae877f79a71fa327845645d04b0812753f64  02_data/collision/dieu7_bao_cao.json
e059267e8d0934d6dfa4e3d4612cc03fa7909b617eb424660dbebaaf952204ae  02_data/collision/dieu7_ext_groups.jsonl
fbad9f38b583ffc856d2ab4faef49172d7d547aba4d91b9b57f749632efe977c  02_data/collision/dieu7_stress_groups.jsonl
b9f214cac5010c8b0d2f2bff2d330aeadbbc6e82a832b1bae5682661597adced  02_data/collision/gate_member_trace.jsonl
c31c840021653987da0b14cac6867db27621ea451d31972a5b9964e2bff0454e  02_data/collision/qd57/19_fixture_moi.json
a67200c55e45879d696f5a9662404f6983e1728f5be2a5f98b14dbf8c650f0fe  02_data/collision/qd57/PHAN_QUYET_57_NHOM.md
64491e5e8fbd87377ff15e80ceee78da6fa0a404a6dd44fc82eefdaae6b4b619  02_data/collision/qd57/PHU_LUC_57_NHOM.md
a1b51acaceddf150c956eb7c9eb013225f57eeff332d0f900fccaa579efb0cef  02_data/collision/qd57/kiem_record_19_fixture.json
8e704ba90951d32db12435c466c53631b4cdd810ebcc25800cbb14d4a297bc08  02_data/collision/qd57/ledger_57_quyet_dinh.csv
c86056791fa33297fe5b1f13b9054631d684e62299baa8c51d82bb5495b5968d  02_data/collision/qd57/ledger_57_quyet_dinh.json
4ff4c72bd94151ee0b3e708ac7f7ad120cd9ff6f20b0bdcf3823034f6c9c24fd  02_data/collision/qd57/manifest.json
376c018ba482e5f8f872bb0c0ff2d7f3143ad19b8f54858bc2be56281cfdc6c7  02_data/collision/qd57/scope_expected_members_qd57.json
1930c63ccd231cf3c77347b27c92eea1c12674404f7724f29f57044ae0539472  02_data/collision/qd57_scope_exclusions.json
30d42f8d9cd9a81dfb6eabe7109e2b4cd786bf9a56cdf0f491aec17cf8d92cda  02_data/core_domain/bang_quyet_dinh_57nhom.md
ef10f03e809fc9d9007b5755f4907a05e638918dd2b39e882887b11777adb0bb  02_data/core_domain/core_domain_provenance.json
fb21a697a81b9ec35c07cb555ac044e752a5ad6ad64219eaeb3bcaab2018ec88  02_data/core_domain/de_xuat_quyet_dinh_95nhom.md
181e3389387400e954fc1e70fa587f0a893e9ef076cf6efc3b5c3b2b82c33838  02_data/core_domain/rule_scope_vong6.md
b920363a160bff573e208ed028816fa6400c36c983fa190963b98e8bce2ba1a8  02_data/core_domain/vi_syllable_vocab.tsv
13852f3521a86678e528cd6750e013936f00d667bae7248d47103ed39ad77495  02_data/en_branch/en_coverage.tsv
e8651c9a5fb043d7a7b4ba2196b35a388f4ff182fc0f340950f1f74d1960c16c  02_data/en_branch/en_coverage_provenance.json
9ff6fc8e7fc6a1fc2cf6293c899dc1248d9e829a90f6ce5ce27c61a4dc01d8b5  02_data/fold/fold_provenance.md
69d778e3ba22f508ac7384bac4ecc88f9e982ebe91e1702d692897c7371b615b  02_data/fold/fold_vi.tsv
47f7dc4d217215f655bebfee101915cc14db7c8941d8415b2277326a7da0c68d  02_data/g2p/e6_checkpoint_pin_de_xuat.md
ab0a1717b30ec2f093302916f74880f2d457991c1224cf749f97bed7bf8131bd  02_data/g2p/exhaustive_sweep_report.json
190993829c550046f9d7cdbbb6b9bd29ee91d6a70b72e8be8554e602859ba91d  02_data/g2p/fase_e_corpus_1M_report.json
295d80ddfdf03122cf36fc018662521df53c973fc522f82b1cc7e861c3236197  02_data/g2p/fase_e_corpus_1M_shard0.json
beb2e0023bab8c0f83235623e13624054729437ad60c5c9b66740489b9022476  02_data/g2p/fase_e_corpus_1M_shard1.json
a27b9e26dd6fbd3f992bc653bc305fc42794f4e13cc8b505f841803a5148868b  02_data/g2p/fase_e_corpus_1M_shard10.json
464d61e1480f23156fc096f044057f0a0d4cd6043ce199284b6ef125fc397e4e  02_data/g2p/fase_e_corpus_1M_shard11.json
04009cc8848c7c5ed3ca68ca0b03ec128f8241ffc2398b143c51b4b54bfd6112  02_data/g2p/fase_e_corpus_1M_shard12.json
cc0abf3d48c88352b050bfcc45d64ef7a027ca988623d526fbb9703dd8a26f5f  02_data/g2p/fase_e_corpus_1M_shard13.json
fdde6c9dd94341de9dff7e9d690a7a0f60a83f1575d7c8fb768fa2c47079e8a6  02_data/g2p/fase_e_corpus_1M_shard14.json
d673c413298e9b0cfaa3cc611dd105c5b1531649032afbddcf2c0087d2326c45  02_data/g2p/fase_e_corpus_1M_shard15.json
6c2f1e615dc2e1d838d763920db0a6ca56c712b2050db67e05efca9e3a339f7c  02_data/g2p/fase_e_corpus_1M_shard16.json
cc8172559f86d330add7ed408eb2809fcf2ec5a8d3efcb66b8a24a84bcab4e11  02_data/g2p/fase_e_corpus_1M_shard17.json
21cc8b578804d5983d17a502dcb1f32a29409d18ae2479ba54de4328714d95b9  02_data/g2p/fase_e_corpus_1M_shard18.json
20f22dd5cd50d323e67329fedec4549aefaa96f5dc5d31fe5f198df15a6c3644  02_data/g2p/fase_e_corpus_1M_shard19.json
a5acf5e5d046990f40f777862c20bf0fe5ee88529d3fc4ae6fb5faf6d24adff8  02_data/g2p/fase_e_corpus_1M_shard2.json
3508710d25a4c92ffb3c90dbba40db05bf1dcfc6da9b244116983acab31ab591  02_data/g2p/fase_e_corpus_1M_shard20.json
40fa2db67ecc5b5faf50c1d4339b140d784115c4f50ee7443d07f7ff1115f1b4  02_data/g2p/fase_e_corpus_1M_shard21.json
0c797f433bd2c24d31872501d75d986175c4330a15f277c4d7a038b000acd8cb  02_data/g2p/fase_e_corpus_1M_shard22.json
015036ef12c9901bc4cf12261002d0ab27ce8cf156d0bcde3cdc8c39c8f76f89  02_data/g2p/fase_e_corpus_1M_shard23.json
938bcae1a450911b1209af40c6f49740af9ead75f6d25e716cb8f5037aab0c88  02_data/g2p/fase_e_corpus_1M_shard3.json
4bde141bce306635af04cd928983f54e550e94532bde27cc7b5529a7505d19e3  02_data/g2p/fase_e_corpus_1M_shard4.json
4c4770d5a45bc66abf188879fdb62cc42e6a29e3dd1d30bbc8c8c406232c7a28  02_data/g2p/fase_e_corpus_1M_shard5.json
552087540e1fd1d7ee79578d8d07d06c57f688da2a981e8c7fe3e093dec6dfdb  02_data/g2p/fase_e_corpus_1M_shard6.json
2d85c04b1d860df3cb8cf6652e4f8cc1346a50fa3f6e591318f30d1ea18704f5  02_data/g2p/fase_e_corpus_1M_shard7.json
5cd647543fe7c5820d709acd0d60100cfd1dc3d4db63b3b7a1c25e0ca85cd385  02_data/g2p/fase_e_corpus_1M_shard8.json
33a7da7c1257e373778e0c9367dcb78062ac08076e18ae4b7fba035bc6de6263  02_data/g2p/fase_e_corpus_1M_shard9.json
c3df7b701908f7e33aed1e9c7379c26daaec460bdc65e649eac8419d61160abc  02_data/g2p/fase_e_diff_report.json
862905fb81b81faefff5ade6577b5a401d19fd56604e1a52aca8826a2cca1ed2  02_data/g2p/fase_e_judge_de_bai.md
9e2b035e5db3ea96217366cb7e41f1c6f01a6e79b221e3aefe99f7b7ca283495  02_data/g2p/fase_e_judge_provenance.json
2e3a6b92c23ea3e36a49c2f0f3dd637bd22137de447727c4ce5989528f2de850  02_data/g2p/fase_e_judge_provenance_dinh_chinh.md
977d97f2411ea919b1f9627016a78da8f7c34cf526add0228964df6a6e3a315e  02_data/g2p/fase_e_judge_provenance_v1.json
2b3fe267ed540d40ef566c8b2e3f15dae579bd10009e32b504e43d8b860935d8  02_data/g2p/fase_e_judge_raw_log.jsonl
703a73e17ca168b4bb3d4b81f91943ed5f89b28359cd95c023ba2e753cc280fc  02_data/g2p/fase_e_judge_raw_log_v1.jsonl
2f55428fec7fb1f60e7801c8450dd704c974ed37e937a6c2851a042f13ac9bea  02_data/g2p/fase_e_judge_regression.json
7894e64558da08b8aeabd44a5841bfa2af2dfd3b64780279a48ebdc891ef5054  02_data/g2p/fase_e_judge_regression_v1.json
3d377cfd12773bc45d5aa97e26ca8cfed855357b1572d69613bc5abca237fded  02_data/g2p/fase_e_judge_session.jsonl
07860511b3ac65c3c277829cf13f1a4be3d17135f8b342fff3133e70a433ddd7  02_data/g2p/fase_e_judge_session_key.json
7261b020af0c70f6b988c91488975e0be231c75f387022cd7894cb1534dbb04f  02_data/g2p/fase_e_judge_session_v1.jsonl
b8743e90544ad1d7160f24a801bbf4a71f5c220302090c8cbf180b999292f8d2  02_data/g2p/fase_e_judge_set.jsonl
3252801fb346f9c2755cde76db3fce03b483949acf8a8bfb3da1ccf6298cb4c4  02_data/g2p/fase_e_judge_spotcheck.jsonl
3cfc9009cba7256825d104a34974b1c59f22c1c27f5c29477fa2b41ff4b6497f  02_data/g2p/fase_e_judge_spotcheck_agent_results.json
f781e37decc3a28b71063075b4fc4f425b5c871b4cf17eafcf2c758f8e06b804  02_data/g2p/fase_e_judge_spotcheck_bien_ban.md
c48774e66e649db48f431c3e1db580687cbfd795466b2ce7adc66d9d2a9d6137  02_data/g2p/fase_e_judge_spotcheck_v1.jsonl
db55dda36481680a92e96b12285ebb9126e6558d9d71a2de8f78d2421c9b5ff5  02_data/g2p/fase_e_judge_summary.json
68e9839152acd2b9c1b5e15c9b4154631abbadd0ef1cd26c8a0543ae02434bf4  02_data/g2p/fase_e_judge_summary_v1.json
b67040223e8ec5cf0322f07d3540959afce9a5ac3af87e836d4be9007457e227  02_data/g2p/fixture_tier1_email_spell.json
9cf154c926bb26f0bf32b1e27ba35a66addbee846bc10ad8fb6af7ff49a5f8d1  02_data/g2p/g2p_resource_pins.json
932c375d5542a93a53ecf16ea7f05ebc90dcf087d337bb9b3be12a3418accadb  02_data/g2p/kokoro_en_fit_report.json
c2ed84974a64ab4b2ce1b27331ae02626b25ba408a5fd9af65b0e2532918ce9b  02_data/g2p/kokoro_en_weights_provenance.json
de3e4eb7884c1f950a157448fc267146cd02fd260969b1f9b583a4e6369409a8  02_data/g2p/preflight_summary.json
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v23.log
d4ef0c6201d78bd1855f59d81ae7e2355ab7b5db79f13659ef2c9757129660eb  02_data/g2p/preflight_v26.log
0d4b3c89533e7a933586da65afd98dfb2997c86fa06da2a17471e8652c797306  02_data/g2p/schema_g2p_0.1.md
bdc952aaea9ce6f172a62d760176da179072e0dbea179db6db88b0b17fba9529  02_data/g2p/vocab_config_from_master.tsv
7e9e7ca6a0abee23d6a83560629c54478347a895ee9602980108c92386222dbd  02_data/g2p/vocab_config_provenance.json
55b244526abd03b1cc09320ecc0656730b03d6d15ff90337d39fcc003c85e222  02_data/gold_dev/gold_vi_reference.tsv
f63586e8f4bdd7f0aad0e3050d58c2c89e3b7416a36c7d73d15b1a21e5f712bf  02_data/inventory_ham.tsv
e6c171567b4e4af6b1bdcdb9cd920787a5b52fc2b7cf62eace1cba7c312a9028  02_data/inventory_provenance.json
74dfc5479eef810c1085b74591dec98ef3aa51991321ce0941092cb03ce58a9f  02_data/inventory_schema.md
3dec592fe8d5233980e0827bb6fbe51ced7ddaa8daa647d8e068dc72a23cb31b  02_data/profiles/kokoro_vocab_178.tsv
60910db1b4119634c40a8cb8f269b7fdbff9c110205ae725330ca8a42e9f4979  02_data/spell_vi.tsv
bd4ce8e44170a5f9f481310ca85c51de3c4f851a65e679b40e603b143bd3542a  03_vendor/cmudict/LICENSE
2e9db15e3a6f31ad2b55819995cc70eef9df3b162110f1cae19f2d8125752e46  03_vendor/cmudict/cmudict_provenance.json
b3b3d2386b97bfd1980619871e735198bf56060b09af7b3c0ae950af7f140f96  03_vendor/cmudict/fetch_cmudict.py
490505be1e9c9cd6d65426935a7808effd46b68c8ead43ce346b1f87a08eb56d  README.md
8b8b821d6aa6d6ca806cb2eee8df34aa09fdb0cf04044c0e816cece7b1e10eb7  preflight.sh
```

(hash của chính `reference_diff.md` và của bundle không tự liệt kê được — lấy từ
tin nhắn gửi kèm gói.)
