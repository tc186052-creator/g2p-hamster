# Bảng phạm vi merge rule — gói quyết định ngôn ngữ (vòng 6.2)

> **CẬP NHẬT vòng 6.5 (hậu kiểm v14 §5): QD57-2026-10-02 ĐÃ ÁP — 83 nhóm gate = 45 approved (exact fixture) + 38 excluded_v1 + 0 proposal → PASS (exit 0). Bảng rule dưới đây GIỮ LÀM BỐI CẢNH LỊCH SỬ (câu hỏi duyệt per-rule đã hết hiệu lực — quyết hiện hành theo NHÓM nằm ở ledger QD57 `02_data/collision/qd57_scope_exclusions.json` + `de_xuat_quyet_dinh_95nhom.md` + `dieu7_bao_cao.json`).**
> Bảng này SINH TỰ ĐỘNG bởi `01_g2p/gen_rule_scope.py` từ artifact đã pin (`dieu7_bao_cao.json` + bảng attestation + audit module) — mọi số liệu (thành viên, tần suất, seq record, rule trace, sensitivity) đọc trực tiếp từ artifact; nhận xét/đề xuất của tác giả nằm ở mục riêng mỗi rule, không nhúng số liệu tay (sửa R61-03 của reviewer).

## Căn cứ miền

- Nguồn: corpus IR tầng 1 (sha256 trong `core_domain_provenance.json`) — độc lập với parser G2P; builder KHÔNG import parser.
- Đơn vị đếm: **dạng token NGUYÊN DẠNG (verbal NFC+lower+strip, toàn chữ) — tần suất LITERAL từng token trong corpus; KHÔNG phải 'âm tiết chuẩn đã thẩm định' và KHÔNG chứa mảnh tách suy diễn** — vòng 6.2 đã bỏ bước tách token (R61-01): sau rebuild literal, `lựch`, `ếc`, `họct`, `thànhph` có frequency literal = 0; riêng `lệc` còn 1 lượt literal và nhóm lệc/lệch rời gate vì dưới ngưỡng 2 (chú thích v10 gõ nhầm lẹc/lệc — đã sửa; frequency xem bảng pin và mục MR-CODA-CH-C).
- Bảng pin: 124,971 dạng token / 16,538,824 occurrence; sha256_vocab `b920363a160b…`.
- Ngưỡng `ATTEST_MIN_FREQ=2`. Độ nhạy (thông tin, chỉ liệt kê): gate = 83 nhóm @min_freq=2, 56 nhóm @min_freq=5, 46 nhóm @min_freq=10.
- Kết quả phân lớp: 27,210 dạng sinh = core-attested 6,801 · ext 13,299 (miền mở rộng, không gate) · stress 7,110.
- Gate: **83 nhóm** (approved 45 · excluded_v1 38 · proposal 0 · identity 0 · unexplained 0) — toàn bộ từ cặp chính tả attested literal. Số nhóm thay đổi theo dữ liệu là ĐÚNG — không giữ số vòng trước (98 → 95 sau rebuild literal).
- Pin hành vi miền: `domain_config_hash` `8d46700fd03ffde123a53b3d571fa29e81bbb69dbfdfe623ba333962113e02d8` — phủ runtime classifier + source hash (R61-02).
- Giới hạn đã khai: attestation ≠ nghĩa từ; tần suất không chứng minh hai dạng cùng phát âm; từ hiếm thật có thể bị xếp ext (bảo thủ — thu hẹp gate). Ca reviewer câi/mấi/bêo/buâi/buây + gii → DOMAIN_MUST_NOT regression (vi phạm → FAIL).

## Fixture reviewer đã xác nhận (vòng 6.1)

8 cặp i/y hẹp được reviewer xác nhận ở MỨC FIXTURE (expected record viết tường minh, không lấy output parser làm đáp án): `kí/ký`, `lí/lý`, `kì/kỳ`, `kĩ/kỹ`, `mĩ/mỹ`, `sĩ/sỹ`, `tỉ/tỷ`, `qui/quy`. Đã thêm vào `test_vi_rules.py` như dev/regression fixture. **Giới hạn duyệt:** không bao gồm toàn bộ danh sách nhóm, `ya/ia`, `yê/iê`, tên riêng/noise, hay mọi thanh khác cùng skeleton; không biến thành `approved=true` cho matcher rộng.

## MR-I-Y — 7 nhóm gate
- Scope matcher hiện tại: role_alt trên form: {y→i, ya→ia, yê→iê}
- seq record: PHONE_D_IMP → PHONE_I → TONE_NGANG
- seq record: PHONE_I → TONE_NGA
- seq record: PHONE_I_SCHWA → PHONE_N → TONE_NGANG
- seq record: PHONE_I_SCHWA → PHONE_W → TONE_HOI
- seq record: PHONE_NH → PHONE_I → TONE_SAC
- seq record: PHONE_S → PHONE_I → TONE_HOI
- seq record: PHONE_Z → PHONE_I → TONE_NGANG
- Thành viên (freq literal, sinh từ JSON):
  - di/dy: di[6655], dy[5] — thành viên biên (freq≤5)
  - nhí/nhý: nhí[328], nhý[5] — thành viên biên (freq≤5)
  - iên/yên: yên[3469], iên[3] — thành viên biên (freq≤5)
  - đi/đy: đi[38741], đy[3] — thành viên biên (freq≤5)
  - iểu/yểu: yểu[32], iểu[2] — thành viên biên (freq≤5)
  - xỉ/xỷ: xỉ[436], xỷ[2] — thành viên biên (freq≤5)
  - ĩ/ỹ: ĩ[47], ỹ[2] — thành viên biên (freq≤5)
- Nhận xét/đề xuất tác giả: Reviewer vòng 6.1 đã XÁC NHẬN 8 cặp fixture hẹp (kí/ký, lí/lý, kì/kỳ, kĩ/kỹ, mĩ/mỹ, sĩ/sỹ, tỉ/tỷ, qui/quy) ở mức fixture — KHÔNG suy rộng thành duyệt toàn matcher hay cả danh sách nhóm. Đề xuất tác giả: scope hẹp alt y→i (nucleus), bỏ ya→ia; nhánh yê→iê tách rule con riêng.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-CODA-O-U — 19 nhóm gate
- Scope matcher hiện tại: role_alt trên tail: {o→u}
- seq record: PHONE_B_IMP → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_B_IMP → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_B_IMP → PHONE_SCHWA → PHONE_W → TONE_NGANG
- seq record: PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_K → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_L → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_M → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_M → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_N → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_P → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_R_VI → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_R_VI → PHONE_I → PHONE_W → TONE_SAC
- seq record: PHONE_S_RETRO → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_S_RETRO → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_T → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_T → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- seq record: PHONE_Z → PHONE_I → PHONE_W → TONE_NGANG
- seq record: PHONE_Z → PHONE_OPEN_E → PHONE_W → TONE_NGANG
- Thành viên (freq literal, sinh từ JSON):
  - neo/neu: neo[301], neu[34]
  - teo/teu: teo[92], teu[21]
  - mio/miu: miu[50], mio[16]
  - rio/riu: rio[161], riu[15]
  - io/iu: iu[15], io[12]
  - río/ríu: río[13], ríu[12]
  - sio/siu: siu[32], sio[10]
  - eo/eu: eo[434], eu[9]
  - tio/tiu: tio[13], tiu[8]
  - deo/deu: deo[7], deu[7]
  - dio/diu: dio[16], diu[4] — thành viên biên (freq≤5)
  - pio/piu: pio[12], piu[4] — thành viên biên (freq≤5)
  - seo/seu: seo[1776], seu[4] — thành viên biên (freq≤5)
  - beo/beu: beo[23], beu[3] — thành viên biên (freq≤5)
  - keo/keu: keo[257], keu[3] — thành viên biên (freq≤5)
  - leo/leu: leo[1009], leu[3] — thành viên biên (freq≤5)
  - bio/biu: bio[57], biu[2] — thành viên biên (freq≤5)
  - bâo/bâu: bâu[8], bâo[2] — thành viên biên (freq≤5)
  - meo/meu: meo[34], meu[2] — thành viên biên (freq≤5)
- Nhận xét/đề xuất tác giả: cao/cau vẫn bị COND_NUC chặn (đối chứng 11/11). Nhóm cũ 'ưu = ưo' không còn là nhóm gate. Đề xuất: chỉ xét nhóm attested, thành viên loan/noise (bio, pio, mio…) cần reviewer loại/nhận tường minh. Không duyệt 'lõi chắc' chỉ từ tần suất.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-ACH-EC — 0 nhóm gate
- Scope matcher hiện tại: ĐÃ RÚT khỏi catalog (withdrawn vòng 6.3 — trước đây: rhyme_alt {a:ch → e:c})
- Không có nhóm gate nào (danh sách rỗng sinh từ JSON).
- Nhận xét/đề xuất tác giả: Quyết reviewer v11 §4.2-4.4 (2026-10-02): KHÔNG DUYỆT — có căn cứ độc lập phân biệt sách/Séc, mách/méc (phiên âm mục từ; Kirby 2011 tr.383-384); ham/0.2 biểu diễn vần 'ach' = ɛ-prevelar + k, 10 cặp ach/ec là ĐỐI LẬP bắt buộc ở master; không treo như proposal chờ nghe model.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-CODA-CH-C — 3 nhóm gate
- Scope matcher hiện tại: role_alt trên tail: {ch→c}
- seq record: PHONE_C → PHONE_E → PHONE_K → TONE_SAC
- seq record: PHONE_N → PHONE_I → PHONE_K → TONE_SAC
- seq record: PHONE_T → PHONE_I → PHONE_K → TONE_SAC
- Thành viên (freq literal, sinh từ JSON):
  - tíc/tích: tích[14352], tíc[7]
  - chếc/chếch: chếch[11], chếc[3] — thành viên biên (freq≤5)
  - níc/ních: ních[11], níc[2] — thành viên biên (freq≤5)
- Nhận xét/đề xuất tác giả: Sau rebuild literal (vòng 6.2), ba nhóm rời gate do thành viên xuống dưới ngưỡng — số đọc trực tiếp từ bảng pin (chú thích vòng trước gõ nhầm lẹc/lệc, đã sửa theo đúng bảng): lực/lựch (lựch freq literal = 0), lệc/lệch (lệc freq literal = 1 — dưới ngưỡng, KHÔNG phải 0; lẹc là cách viết khác, không thuộc nhóm cũ), ếc/ếch (ếc freq literal = 0). Nhóm còn lại vẫn pending về phạm vi và biểu diễn phát âm (nucleus xem ở seq record từng nhóm); chờ E6.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-UE-UÊ — 5 nhóm gate
- Scope matcher hiện tại: composite_alt: {ue→uê}
- seq record: PHONE_H → PHONE_W → PHONE_E → TONE_NGANG
- seq record: PHONE_S → PHONE_W → PHONE_E → TONE_NGANG
- seq record: PHONE_S_RETRO → PHONE_W → PHONE_E → TONE_NGANG
- seq record: PHONE_T → PHONE_W → PHONE_E → TONE_NGANG
- seq record: PHONE_TH → PHONE_W → PHONE_E → TONE_NGANG
- Thành viên (freq literal, sinh từ JSON):
  - hue/huê: huê[30], hue[17]
  - thue/thuê: thuê[3152], thue[17]
  - sue/suê: sue[60], suê[8]
  - xue/xuê: xuê[6], xue[4] — thành viên biên (freq≤5)
  - tue/tuê: tue[6], tuê[2] — thành viên biên (freq≤5)
- Nhận xét/đề xuất tác giả: Matcher không được thành nguồn hợp thức hóa đổi dấu — attestation đưa dữ liệu, QUYẾT thuộc reviewer. Đề xuất: giữ pending.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-CODA-I-Y — 1 nhóm gate
- Scope matcher hiện tại: role_alt trên tail: {y→i}
- seq record: PHONE_SCHWA → PHONE_J → TONE_NGANG
- Thành viên (freq literal, sinh từ JSON):
  - âi/ây: ây[14], âi[2] — thành viên biên (freq≤5)
- Nhận xét/đề xuất tác giả: Đề xuất KHÔNG duyệt từ nhóm âi/ây (freq biên); giữ stress-technical hoặc rút.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-ONSET-GH-G — 0 nhóm gate
- Scope matcher hiện tại: role_alt trên onset: {ngh→ng, gh→g}
- Không có nhóm gate nào (danh sách rỗng sinh từ JSON).
- Nhận xét/đề xuất tác giả: Không có nhóm gate — không đòi duyệt merge core chỉ để giữ test stress.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-ONSET-C-K — 0 nhóm gate
- Scope matcher hiện tại: role_alt trên onset: {c→k}
- Không có nhóm gate nào (danh sách rỗng sinh từ JSON).
- Nhận xét/đề xuất tác giả: Stress-technical riêng; các nhóm compose xét theo nhóm chủ (rule đầu trong trace).
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-QU-K-GLIDE — 0 nhóm gate
- Scope matcher hiện tại: onset_glide_alt: {k:u → qu}
- Không có nhóm gate nào (danh sách rỗng sinh từ JSON).
- Nhận xét/đề xuất tác giả: Chỉ còn nhóm compose biên (cuới/quới, cue/quê) — đề xuất giữ pending.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## MR-GLIDE-O-U — 0 nhóm gate
- Scope matcher hiện tại: (stress catalog — không thấy trong gate hiện tại)
- Không có nhóm gate nào (danh sách rỗng sinh từ JSON).
- Nhận xét/đề xuất tác giả: Không cần nâng approved chỉ vì có trong catalog stress.
- **Câu hỏi duyệt:** scope này có được duyệt trên đối tượng đã liệt kê không? Thành viên biên (freq≤5) nhận/loại tường minh?

## Nhóm compose (trace dùng nhiều rule — CHƯA chứng minh tập tối thiểu)

Engine deterministic theo catalog và ghi CÁC RULE THỰC SỰ ÁP; điều đó không đồng nghĩa tập rule đó là tối thiểu (vd cấo/cấu được giải thích bởi MR-CODA-O-U đơn lẻ — R61-03.3). Câu đúng là 'trace dùng nhiều rule':

| Nhóm | Rule trace | freq | seq record |
|---|---|---|---|
| cue/quê | MR-ONSET-C-K+MR-QU-K-GLIDE+MR-UE-UÊ | 17/2174 | PHONE_K → PHONE_W → PHONE_E → TONE_NGANG |
| cuới/quới | MR-ONSET-C-K+MR-QU-K-GLIDE | 2/21 | PHONE_K → PHONE_W → PHONE_SCHWA_LONG → PHONE_J → TONE_SAC |
| cấo/cấu | MR-CODA-O-U+MR-ONSET-C-K | 2/3143 | PHONE_K → PHONE_SCHWA → PHONE_W → TONE_SAC |

## Điều 7 hiện hành (cập nhật vòng 6.5 — đọc trực tiếp từ report)

- 83 nhóm gate = 45 approved (exact fixture: 26 v11 + 19 QD57) + 38 excluded_v1 (QD57) + 0 proposal + 0 identity + 0 unexplained → **PASS** (exit 0).
- Ranh giới scope v1 (R14-01): 39 excluded member + 37 protected member qua boundary exact NFC+lower giữ dấu (exact/UPPER/NFD) — 0 lỗi; `scope_policy_hash` `3ea6fa8d5827beff9e06fec091b3f59d8eab32496f93d9d9935806e5f7a8e131` (R14-02); mutation probe `01_g2p/test_scope_policy.py` 16/16 PASS.
- Reference gold-dev KHÔNG đổi (45 từ, 0 bất đồng); không đụng ca đã đóng V5-01…05/A3-01…04.

## 38 nhóm excluded_v1 (QD57-2026-10-02 — KHÔNG duyệt merge)

Trình bày từ report; quyết định chi tiết theo nhóm xem `de_xuat_quyet_dinh_95nhom.md` và ledger pin.

| Nhóm | subject | protected | thành viên excluded | thành viên protected |
|---|---|---|---|---|
| beo/beu | beu | beo | beu | beo |
| bio/biu | bio đọc như một âm tiết VI theo alias io→iu | biu | bio | biu |
| bâo/bâu | bâo | bâu | bâo | bâu |
| chếc/chếch | chếc | chếch | chếc | chếch |
| cue/quê | cue đọc VI theo alias tới quê | quê | cue | quê |
| cuới/quới | cuới | quới | cuới | quới |
| cấo/cấu | cấo | cấu | cấo | cấu |
| deo/deu | deu | deo | deu | deo |
| di/dy | dy trong các cách dùng chưa xác nhận | di | dy | di |
| dio/diu | dio đọc một âm tiết VI theo alias io→iu | diu | dio | diu |
| eo/eu | eu trong cách dùng chưa xác nhận | eo | eu | eo |
| hue/huê | hue | huê | hue | huê |
| io/iu | io đọc một âm tiết VI theo alias io→iu | iu | io | iu |
| iên/yên | iên | yên | iên | yên |
| iểu/yểu | iểu | yểu | iểu | yểu |
| keo/keu | keu | keo | keu | keo |
| leo/leu | leu | leo | leu | leo |
| meo/meu | meu | meo | meu | meo |
| mio/miu | mio đọc một âm tiết VI theo alias io→iu | miu | mio | miu |
| neo/neu | neu | neo | neu | neo |
| nhí/nhý | nhý trong dữ liệu mã hóa hỏng | nhí | nhý | nhí |
| níc/ních | níc thuộc phiên âm chưa được chốt | ních | níc | ních |
| pio/piu | pio đọc một âm tiết VI theo alias io→iu | piu | pio | piu |
| rio/riu | rio đọc một âm tiết VI theo alias io→iu | riu | rio | riu |
| río/ríu | río đọc như âm tiết VI có thanh sắc | ríu | río | ríu |
| seo/seu | cách đọc tên ngoại/viết tắt trong seo/seu; đặc biệt alias seu→seo | seo trong chế độ đọc VI nguyên dạng | seu | seo |
| sio/siu | sio trong tên ngoại/ký hiệu và alias sio→siu | siu trong chế độ đọc VI nguyên dạng | sio | siu |
| sue/suê | sue đọc như một âm tiết VI bằng alias ue→uê | suê | sue | suê |
| teo/teu | teu trong các cách dùng chưa xác nhận | teo | teu | teo |
| thue/thuê | thue | thuê | thue | thuê |
| tio/tiu | tio trong tên ngoại/ký hiệu và alias tio→tiu | tiu | tio | tiu |
| tue/tuê | tue;tuê trong các cách dùng chưa xác nhận | không cấp thêm xác nhận từ mới cho hai dạng này | tue, tuê | — |
| tíc/tích | tíc trong nhóm phiên âm/biến thể chưa được xác nhận | tích | tíc | tích |
| xue/xuê | xue đọc VI qua alias ue→uê | xuê | xue | xuê |
| xỉ/xỷ | xỷ trong các cách dùng chưa xác nhận | xỉ | xỷ | xỉ |
| âi/ây | âi | ây | âi | ây |
| đi/đy | đy trong các cách dùng chưa xác nhận | đi | đy | đi |
| ĩ/ỹ | ỹ dạng token tách rời | ĩ | ỹ | ĩ |
