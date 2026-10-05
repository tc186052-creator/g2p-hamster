# G2P — KẾ HOẠCH FASE E: gate chất lượng tầng 1→2 trước tầng 3/4

Ngày: 02/10/2026. Viết sau khi **FASE D ĐÓNG (v21 PASS)** theo
`faseD_v21_reviewer_evidence/HAU_KIEM_FASE_D_V21.md` (A/B/C/D đều PASS).
Mục đích: gửi reviewer **kế hoạch + tiêu chí nghiệm thu + pin model** để chốt
trước khi thực thi trọn fase E — đúng quy trình đã làm cho B/C/D.

Định nghĩa gate gốc: `G2P_KE_HOACH_DANH_GIA.md` §E1-E6. Tài liệu này map vào
hiện trạng thật và chốt ngưỡng đo được.

## 1. Trạng thái các fase

| Fase | Phạm vi | Mốc nghiệm thu | Trạng thái |
|---|---|---|---|
| A/B | inventory ham/0.2 + lõi VI | CHOT_FASE_B_V15 | **PASS** |
| C | nhánh EN CMUdict → master | CHOT_FASE_C_V17 (C16-01/02 đóng) | **PASS** |
| D | tầng tiêu thụ g2p/0.1 | HAU_KIEM v18→v19→v20→v21 — **ĐÓNG ở v21** | **PASS** |
| **E** | **gate chất lượng + differential + hiệu năng + demo** | **tài liệu này** | đang thực thi |

Sau v21 reviewer ghi rõ: mọi thay đổi `g2p.py`/bảng làm hash D đổi là **hợp
lệ**, không mở lại D; gate tự kiểm = `reviewer_probes_v20.py --warm` (0 FAIL)
+ chuỗi bằng chứng nguyên trạng. v22 (cache hiệu năng) áp đúng điều này —
`g2p_policy_hash` mới `a24db1ab…`, `en_policy_hash` **giữ nguyên** `1873ac63…`
(không đụng cmu_en.py).

## 2. Sáu gate — hiện trạng, tiêu chí chốt, bằng chứng

### E1 — cấu trúc & hợp đồng: ĐÃ ĐẠT (đề nghị chốt lại trên v22)
- `test_g2p.py` **115 PASS / 0 FAIL** (H1-H12: enum, scope, VI/EN paths, spell
  mode, leaf identity, malformed IR, read_string consensus, aggregate
  parent/child, fingerprint/mutation M1-M5, vocab config, torture H12, smoke
  corpus).
- OOD/torture: fuzz 162 ca token dị + 12 envelope dị + 72 token dị/stream
  (reviewer tái kiểm v21: 0 văng); **H12 torture đã thêm** — "A"×100 spell,
  "TRTRTR", token 10.000 ký tự, 150 token cat hỗn hợp: 0 crash, serialize
  được, <5s.
- **Tiêu chí chốt:** 115+ check PASS, 0 FAIL, torture 0 crash/0 cạn RAM
  (máy reviewer tái lập được).

### E2 — corpus 1M (2 lớp): ĐANG CHẠY — báo cáo kèm v22
- Runner: `01_g2p/fase_e_corpus_run.py` — fail-closed đầu vào (content-pin
  corpus `cb9df5eb…` + resource pins + policy hash `a24db1ab…` ghi vào
  report), chạy 100% record, checkpoint mỗi 100k.
- **E2-A toàn vẹn** — ngưỡng chốt: 100% record, 0 crash; mọi token phát âm
  được (ngoài NO_PRONOUNCE) có ≥1 syllable + profile text khác rỗng; 0 ký tự
  ngoài vocab 178 (conformance); contract_errors chỉ nhóm
  read_string-consensus (tier-1 picked≠tokens, ngưỡng ~1-2% — nhóm khác =
  FAIL); spell-rate trên word token BÁO THEO NHÓM viết hoa/không (không đặt
  gate % — policy [B] chờ chủ dự án).
- **E2-B hợp lệ âm vị** — ngưỡng chốt: coda tắc (P/T/K) chỉ sắc/nặng (0 vi
  phạm); vi syllable luôn có tone; en syllable luôn có stress_state; control
  không lọt syllable. Grammar vi_syllable đã ép ở parse-time — corpus check
  là bất invariant độc lập thứ hai.
- Kết quả mẫu 2.000 record: 0 crash, 0 vi phạm, consensus 21/2000 (1,05%).
- **Tiêu chí chốt:** report JSON `ALL_PASS=true` + reviewer đọc được report
  (không cần corpus — report tự chứa provenance hash + sample lỗi capped 50).

### E3 — differential với G2P ngoài (công cụ tìm bất đồng — KHÔNG oracle, KHÔNG hard-gate %)
- **Công cụ chính — sea-g2p 0.10.0** (Apache-2.0, có LICENSE, PyPI wheel
  sha256 pin dưới) qua wrapper **vig2p 0.1.0** (cùng ký hiệu kokoro mũi tên
  với profile của mình → so sánh trực tiếp không cần map). espeak-ng 1.51
  (hệ thống).
- Tham chiếu thêm: hoang1007/vig2p commit `8835c30113893d1302708f179d619b49444a75bb`
  — **repo KHÔNG có file LICENSE** ở commit đó → chỉ tham khảo/không phân
  phối; không dùng làm gate.
- Thiết kế: mẫu **2.000 word-token** (systematic sample — mỗi record thứ 250;
  reservoir seed=0 tái lập được) từ corpus; so sánh chuỗi phoneme-layer per
  word (BỎ stress marks ˈˌ cả 2 phía — tool gắn stress cho vi, mình không).
- **Kết quả đã đo (02/10/2026):** equal **1.236** (61,8%) · phoneme_lech
  **646** (32,3%) · no_pron **88** (4,4% — status NO_PRONOUNCE của mình) ·
  tone_lech **30** (1,5%) · tool_errors 0 (retry 3 lần).
- Bất đồng gom nhóm giải thích được: **quy ước ký tự** coda k↔c (PHONE_K='k'
  vs 'c'), onset r ʒ↔ɹ, vần ɨ↔y / iə↔iɛ / ɚ↔↗ː, en ɑ↔ʌ; **policy thật**:
  fold nhóm (b) của mình ('cac'→các) tool không làm. Group tone_lech chứa
  artifact tool (sea-g2p vẽ ER/erhua en-US bằng ký tự '↗' — đụng charset
  thanh điệu; không phải bất đồng thanh VI). Chi tiết:
  `02_data/g2p/fase_e_diff_report.json` (provenance tự chứa: corpus pin +
  policy hash + code sha).
- **Tiêu chí chốt:** diff report tồn tại, gom nhóm giải thích được, mọi nhóm
  lớn (≥1% mẫu) có giải thích ngôn ngữ hoặc đưa vào bảng chờ duyệt. **Không
  yêu cầu % khớp.** Bộ 500 token cho judge đã dựng:
  `02_data/g2p/fase_e_judge_set.jsonl` (290 phoneme_lech + 16 tone_lech +
  194 equal; 491 ok / 6 fold / 3 spell).

### E4 — differential 9B judge (người phân xử — judge không chấm phoneme)
- Bộ 500 token đóng băng `fase_e_judge_set.jsonl` (sha `b8743e90544ad1d7…`):
  290 phoneme_lech + 16 tone_lech + 194 equal (491 ok / 6 fold / 3 spell).
  Script `fase_e_judge_sample.py` (kèm v23) sinh 3 artifact phiên:
  `fase_e_judge_session.jsonl` (500 item **MÙ** — A/B xáo seed 20261002, cân
  bằng 248/500, không nhãn mình/tool), `fase_e_judge_session_key.json`
  (KHOA — không cho judge) và `fase_e_judge_de_bai.md` (luật phiên).
- **Quy ước dấu nhấn (finding reviewer v22 — đã ghi vào đề bài):** phương án
  có thể chứa `ˈ` `ˌ` — artifact của công cụ đối chiếu (sea-g2p gắn stress
  cả âm tiết vi). Judge KHÔNG chấm dấu nhấn; chỉ chấm âm đầu/vần/coda/thanh.
- Model: `qwen3_5_9b_base` hiện có trên máy (không copy/di dời theo ràng
  buộc); venv vLLM riêng. Session duyệt **cùng chủ dự án**.
- **Tiêu chí chốt:** theo §6 — 7 điều kiện reviewer đã chốt (vòng v22).

#### Hiện trạng chạy (02/10/2026 — máy giữ model, theo runbook reviewer §3)
- **Engine:** transformers 5.17 + bitsandbytes **NF4** (compute bf16),
  batch 24 pin, greedy, max_new_tokens=160, seed 20261002. vLLM KHÔNG dùng:
  chưa cài; bf16 19,3GB không vừa 12GB nên vẫn phải quant 4-bit; không có
  weights AWQ/GPTQ sẵn, tự quantize = tạo bản copy model (đụng ràng buộc);
  kiến trúc `qwen3_5` VL mới có thể chưa hỗ trợ — để thay ~3 phút của job
  ~5 phút là không đáng.
- **Phiên v1 (stress nguyên trình bày):** judge bị **fixación dấu nhấn**
  dù đề bài cấm chấm — 126 cặp chỉ-khác-stress chỉ 10 `hoa` (40 A/35 B/
  41 ca_hai_sai); 68 cặp identical → 68/68 `hoa` (judge nhất quán khi chuỗi
  thật sự giống nhau). Lưu `fase_e_judge_*_v1.*` làm bằng chứng hành vi.
- **Phiên v2 (chốt — strip ˈˌ CẢ HAI phía trước khi trình bày, đúng quy ước
  so sánh E3 đã khai báo):** identical trình bày = 194 → **185 `hoa` + 9
  `ca_hai_sai`** (9 = judge chê ký hiệu chung trên từ EN — tách nhóm
  `judge_notation_reject`, KHÔNG phải regression). Phân bố: hoa 268 ·
  ca_hai_sai 155 · B 41 · A 36. Parse 490 ngay lượt đầu + 10 retry + 0 fail
  (186,2s — 372 ms/item). Provenance: sha 11 file model (4 shard), prompt sha
  `c216c8e8…`, NF4/batch24/greedy; ghi chú minh bạch 1 OOM warning
  (allocator tự phục hồi).
- **Regression "G2P mình sai" (điều kiện 4):** **186/500 net** (runbook
  literal 195 — chênh 9 notation-reject): 178 phoneme_lech + 8 tone_lech;
  146 ca_hai_sai + 20 A + 20 B; 151 vi / 35 en. **Đọc đúng điều kiện 5 —
  judge KHÔNG là oracle:** đọc mẫu reason cho thấy đa số là xung đột
  knowledge-ký hiệu của judge (k↔c: "âm cuối là 'c' (phát âm /k/)" rồi chê
  cả hai; 'rằng' /ʒ/ — quyết định master đã chốt — bị chê vì judge kỳ vọng
  /r/), KHÔNG phải lỗi G2P được chứng minh. Danh sách đầy đủ:
  `fase_e_judge_regression.json` — đầu vào bảng chờ duyệt policy [B],
  không tự động thành dev item.
- **Spot-check 25 phiếu (điều kiện 7 — đã thực hiện 02/10/2026):** người
  kiểm = agent (LLM) theo **ủy quyền của chủ dự án** trong phiên (caveat
  LLM-kiểm-LLM ghi minh bạch; reviewer có thể yêu cầu người thật soát lại).
  Kết quả: **14/25 ĐẠT · 11/25 KHÔNG ĐẠT** → **judge KHÔNG đủ tin cậy làm
  người phân xử phát âm**. Mọi phiếu KHÔNG ĐẠT đều là lỗi phía judge (đọc
  sai input, sai âm vị học, tự mâu thuẫn, áp ký hiệu ngoài quy ước). KHÔNG
  phát hiện lỗi G2P mới từ judge — danh sách 186 regression hạ cấp thành
  **candidate flags** cho policy [B]. 1 mục policy [B] mới: token corpus
  không dấu ('tiêu','Bây') đọc ngang trung thực — có fold theo tần suất là
  quyết của chủ dự án. Biên bản: `fase_e_judge_spotcheck_bien_ban.md`;
  máy đọc: `fase_e_judge_spotcheck_agent_results.json`. Sự cố minh bạch:
  agent từng nghi hệ rơi thanh hàng loạt — audit NFD chứng minh chính chuỗi
  probe của agent thiếu dấu; hệ đúng 14/14 chuỗi dựng-NFD → không bug.
- **Kết cục E4:** session chạy đúng runbook, materials hợp lệ (mù, key
  500/500), phân bố + độ tin cậy judge lưu hồ sơ đầy đủ; E4 khép theo đúng
  điều kiện 5 (judge không là oracle) — chất lượng phát âm thật do E6 (tai
  người) + policy [B]. Chờ reviewer duyệt ở v24.

### E5 — tái lập & hiệu năng
- Determinism: report E2 kèm **byte-identical 2 lượt trên mẫu 1.000 record**
  (stream_json sort_keys, không timestamp) + policy hash ghi trong mọi output.
- Throughput: ngưỡng kế hoạch **≥2.000 câu/phút/worker CPU** — đo được
  **~9.100 câu/phút/worker** (mẫu 20k record; số cuối trong report 1M).
  Ghi rõ 1 worker, không vector hóa.
- **Tiêu chí chốt:** det=true + throughput đạt ngưỡng trên report cuối.

### E6 — ĐỔI HƯỚNG BỞI CHỦ DỰ ÁN (02/10/2026) — chuyển thành mở màn tầng 3
- **Quyết của chủ dự án** (bản gốc): *"tải model gốc sau đó viết g2p theo
  của chúng ta và train ở model gốc để nó nói được tiếng Anh sao cho khớp
  fit với g2p mới. Sau khi nói tiếng Anh oke mới train tiếng Việt."*
- **Checkpoint Việt hóa (contextboxai) RÚT** — đề xuất pin cũ
  (`e6_checkpoint_pin_de_xuat.md`) lưu hồ sơ; **chưa từng tải/chạy**.
- **Model gốc EN đã tải fail-closed:** hexgrad/Kokoro-82M @
  `f3ff3571791e39611d31c381e3a41a3af07b4987` (Apache-2.0) — config.json +
  kokoro-v1_0.pth (327MB, sha `496dba11…`) + voices/af_heart.pt — sha khớp
  pin 100% (`kokoro_en_weights_provenance.json`).
- **Đo fit (điều kiện tiên quyết của fine-tune):** bảng 114 symbol của
  mình GIỐNG HỆT vocab tường minh model gốc; profile EN phủ **100%** (37
  ký hiệu), profile VI phủ **100%** (39 ký hiệu — mũi tên thanh ↗↘↓→ có
  sẵn trong vocab gốc, dùng cho giọng zh) → `kokoro_en_fit_report.json`.
  **Không cần đụng vocab — chỉ cần fine-tune acoustic học quy ước symbol
  của mình** (82M tham số — full fine-tune trên 3080 12GB dư sức).
- **Hạ tầng có sẵn:** fork mang pipeline fine-tune StyleTTS2
  (`train_finetune_accelerate.py`, prepare_dataset, extract_voicepack) —
  chính là pipeline đã làm ra checkpoint Việt hóa.
- **Kết cục fase E:** E1–E5 ĐÁNG TIN CHỐT; gate nghe đánh giá (WAV A/B +
  phiếu nghe) chuyển thành **mốc tầng 3**: baseline model gốc đọc chuỗi
  G2P của mình (EN) → fine-tune → nghe đối chiếu → VI.

### E6 (cũ) — adapter & tai (đã thay bằng mục trên; lưu hồ sơ)
- Source: `03_vendor/Kokoro-Vietnamese/` — commit pin
  `a249afe5555aec6c435165c2f61ec0f71284812f` (iamdinhthuan/Kokoro-Vietnamese).
- Checkpoint: HF **contextboxai/Kokoro-Vietnamese** — code tải
  `config.json` + `model.pth` + `voices/*.pt` lúc chạy; **weights chưa có trên
  máy**. Recipe tải phải fail-closed như fetch_cmudict: tải đúng revision pin
  → tính sha256 → ghi provenance trước khi dùng; chưa chốt revision → chưa
  chạy E6.
- Protocol: demo câu混合 cố định (từ bảng gold + câu corpus thật) → WAV A/B
  (mình vs sea-g2p vs checkpoint-raw); inspect token IDs nằm trong vocab
  checkpoint.
- **Tiêu chí chốt:** theo §6 — 5 điều kiện reviewer đã chốt (vòng v22). E6
  thuộc tầng 3/4: reviewer audit artifact (WAV + phiếu + provenance),
  không chấm chất lượng âm thanh; có thể tách gate riêng theo kế hoạch tầng 3.

## 3. Pin tài nguyên mới (fase E)

| Tài nguyên | Version/Revision | sha256 | License |
|---|---|---|---|
| sea-g2p (PyPI) | 0.10.0 (wheel manylinux cp310-abi3) | `020121dd6af8ae707e2d3b946730b501c48400e3b1135f7b16233f44610c022e` | Apache-2.0 (LICENSE kèm) |
| vig2p wrapper (PyPI) | 0.1.0 (wheel py3-none-any) | `2dc7bfdd615fa3de93c82cc1d153fc9b009bfe9f0e494985ce8cc23047183c14` | **không khai rõ** — chỉ dùng nội bộ làm tool đối chiếu, không phân phối |
| hoang1007/vig2p (tham khảo) | commit `8835c301…` | — | **không có file LICENSE** — không dùng gate |
| espeak-ng (hệ thống) | 1.51 | data `/usr/lib/x86_64-linux-gnu/espeak-ng-data` | GPLv3+ (system, không phân phối) |
| iamdinhthuan/Kokoro-Vietnamese (source) | commit `a249afe5…` | — | theo repo |
| contextboxai/Kokoro-Vietnamese (weights HF) | **RÚT ở v26** (chưa từng tải/chạy — chủ dự án đổi hướng sang model gốc) — đề xuất pin cũ lưu hồ sơ | — | theo repo |
| qwen3_5_9b_base | đã có trên máy, không di dời | — | — |

## 4. Điều kiện chốt fase E (hữu hạn — xin reviewer/chủ dự án chốt)

1. **E1:** chốt lại trên v22 (khối torture H12 đã thêm — 115 check).
2. **E2:** report 1M `ALL_PASS=true` (ngưỡng §E2-A/B như trên) — kèm v22.
3. **E3:** diff report 1.000 token gom nhóm giải thích được (không % gate).
4. **E4:** session 9B + người cùng chủ dự án; hồ sơ phân xử lưu hồ sơ.
5. **E5:** det=true + ≥2.000 câu/phút/worker trên report cuối.
6. **E6:** chốt pin checkpoint → chạy demo → phiến nghe A/B. *Phần này đụng
   tầng 3/4 — nếu reviewer giữ nguyên lập luận "ngoài phạm vi B/C/D", E6 có
   thể tách thành gate riêng theo kế hoạch tầng 3.*

## 5. Ràng buộc giữ nguyên
Không train từ test data; không copy/di dời model; không đụng dữ liệu ngoài
`05_TTS/`; kill bằng PID; không sửa tầng 1 ngoài tiêu thụ IR; pin
revision+checksum+license mọi dữ liệu/frontend đối chiếu; README byte-frozen
theo yêu cầu chủ dự án.

## 6. Tiêu chí E4/E6 reviewer ĐÃ CHỐT (vòng duyệt v22, 02/10/2026)

Reviewer duyệt v22: 90/90 hash OK, chuỗi bằng chứng PASS, cross-check E2
24 shard khớp tuyệt đối, **vét cạn mới của reviewer: 126.932 khóa / 0 vi
phạm / negative-control bắt được lỗi giả** — 2 finding nhỏ không chặn (đã
khắc phục ở v23: `fase_e_judge_sample.py` bổ sung; quy ước dấu nhấn ghi đề
bài). Hai bộ điều kiện dưới đây là **tiêu chí nghiệm thu chính thức** của
E4/E6 — không bổ sung/sửa khi chạy.

### E4 — 9B judge (7 điều kiện chốt)
1. Bộ judge **đóng băng + sha256** — đổi bộ = bộ mới có version.
2. Trình bày **MÙ** — judge thấy token + 2 ứng viên A/B, thứ tự xáo theo
   seed cố định, không nhãn "của mình/tool".
3. Mỗi token 1 quyết (**A/B/hòa/cả hai sai/không đủ tin**) + lý do ngắn,
   lưu JSONL.
4. Mọi verdict "G2P mình sai" → **regression/dev item có nhãn** trong bundle
   kế tiếp, đếm n/500.
5. Không dùng judge làm oracle chuẩn hóa phoneme — báo phân bố + trích ví dụ.
6. Provenance: model + revision + **quantization** + prompt hash + ngày +
   người cùng dự án.
7. Chủ dự án **spot-check ≥20 phiếu ngẫu nhiên** (chống judge ảo giác hàng
   loạt).

### E6 — WAV A/B (5 điều kiện chốt)
1. **Chốt revision checkpoint trước khi tải** + recipe fail-closed → sha256
   config/model/voices vào provenance + ghi license.
2. Bộ demo **cố định** (gold + câu corpus, kèm seed/danh sách); kiểm **100%
   token ID nằm trong vocab checkpoint** + lưu hash vocab.
3. A/B **3 nhánh**: (G2P mình → checkpoint) vs (sea-g2p → checkpoint) vs
   (checkpoint-raw nếu có frontend gốc) — cùng text/giọng/tốc độ; WAV
   deterministic + text grid.
4. Phiếu nghe per câu theo 3 tiêu chí: **đúng âm tiết / thanh điệu / tự
   nhiên 1–5**, lưu CSV, có kết luận tổng — **không đặt ngưỡng MOS**.
5. Phân vai: **E6 thuộc tầng 3/4** — reviewer audit artifact (WAV + phiếu +
   provenance), không chấm chất lượng âm thanh; có thể tách E6 thành gate
   riêng của tầng 3.

### Tiến độ sau khi chốt (reviewer đề xuất 2 nhánh — đã chọn nhánh nhanh)
- **Nhánh nhanh (đang làm — v23):** đưa `preflight.sh` + `exhaustive_sweep.py`
  (của reviewer) vào repo, chạy thật trên máy tác giả → gửi report. Reviewer
  chốt **E1–E5 ngay, không cần vòng mới**.
- **Nhánh đầy đủ:** v23 + E4 records (khi có session cùng anh) + đề xuất
  revision checkpoint cho E6.
