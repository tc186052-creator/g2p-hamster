# TẦNG 3 — KẾ HOẠCH: Acoustic (fine-tune Kokoro-82M gốc theo G2P mới)

Ngày: 02/10/2026. Viết sau khi **FASE E KHÉP Ở E1–E5** (PHAN_QUYET_V26 —
reviewer xác nhận kèm 4 điều kiện chuyển tiếp §2, nhúng ở mục 5).
**PHAN_QUYET_V27A: KẾ HOẠCH PHÊ CHUẨN kèm 3 điểm điều chỉnh B1/B2/B3 —
đã hợp nhất vào bản này (v0.2).** Quyết định mở màn của chủ dự án
(02/10/2026, bản gốc): *"tải model gốc sau đó viết g2p theo của chúng ta và
train ở model gốc để nó nói được tiếng Anh sao cho khớp fit với g2p mới.
Sau khi nói tiếng Anh oke mới train tiếng Việt."*
Bổ sung 02/10 (v27A + lệnh train): *"Tôi cần train trước với 3 epoch, base EN
dữ liệu để train ở <workspace>/05_data/01_data_1/en … theo
kinh nghiệm nhiều lần train của tôi thì batch 2 là tối ưu, không bị OOM."*

## 1. Đọc nhanh (3 phút)

- **Model base:** hexgrad/Kokoro-82M @ `f3ff3571791e39611d31c381e3a41a3af07b4987`
  — ĐÃ tải fail-closed, pin ĐÃ PHÊ CHUẨN reviewer (PHAN_QUYET_V26 §3).
- **Fit đã đo và kiểm chéo:** 114 symbol == vocab tường minh model gốc,
  **114/114 ID trùng khít** (embedding row khớp thẳng, không remap); profile
  EN phủ 100% (38 ký hiệu — toàn bộ cmudict), VI phủ 100% (39 ký hiệu) —
  `kokoro_en_fit_report.json` v0.2.
  → **Không đụng vocab; chỉ fine-tune acoustic học quy ước symbol của mình.**
- **Data train EN (v27A B1): DÙNG DATA NHÀ** — `05_data/01_data_1/en`
  (1.760 wav / 3,0005 h / 24 kHz mono PCM16 / một giọng af_heart do chính
  Kokoro EN gốc sinh) — **KHÔNG cần LibriTTS-R giai đoạn này.**
- **Hạ tầng có sẵn:** pipeline StyleTTS2 của fork
  (`03_vendor/Kokoro-Vietnamese` @ `a249afe5…`) + **recipe cũ đã chạy thành
  công** (`04_kokoro_tts/06_train`, venv `04_kokoro_tts/00_env/.venv`,
  torch 2.14.0+cu130) — batch 2 đã được đo OOM-ladder: batch 3/4/6 OOM,
  batch 2 đỉnh 11,1 GiB, 97% GPU (probe_ladder_b2).
- **GPU:** 3080 12GB — 82M tham số full fine-tune dư sức (reviewer xác nhận).

## 2. Hợp đồng đầu vào từ tầng 2 (bất biến — tầng 3 KHÔNG được sửa)

- `g2p/0.1` (stream_json) + `profile_debug.text` (kokoro178) — sort_keys,
  deterministic; policy hash `a24db1ab…`; schema `schema_g2p_0.1.md`.
- Profile VI: tone mũi tên `↗`=sắc, `↘`=huyền, `↓`=hỏi, ngã=`ʔ↗`, nặng=`ʔ↓`
  (`→` không phát sinh) — **bảng chuẩn** (Nit v26-04 đã sửa từ v27).
- Tầng 3 tiêu thụ IR/profile, KHÔNG sửa tầng 1/2; mọi phát hiện lỗi tầng 1/2
  → regression/dev item có nhãn → vòng mới (như B/C/D/E đã làm).

## 3. Milestones (mỗi mốc: làm gì → tiêu chí nghiệm thu đo được)

### T3-A — Hạ tầng suy luận + baseline WAV (EN) — gộp vào render của T3-C
- Nạp `kokoro-v1_0.pth` + `voices/af_heart.pt` (pin đã phê chuẩn); adapter
  sinh WAV TỪ chuỗi profile của mình (KHÔNG qua misaki/espeak) theo **đường
  chuẩn Kokoro**: `model(phonemes, voicepack[n-1], speed)` — bài học recipe cũ:
  KHÔNG extract voicepack từ checkpoint (style_encoder khởi tạo ngẫu nhiên khi
  fine-tune → voicepack rác; duration ngắn 15–20% là dấu hiệu sai đường).
- Bộ demo cố định: 20 câu EN đóng băng (`06_train_t3/demo/demo_sentences.txt`,
  sha trong provenance).
- **Tiêu chí chốt:** (a) WAV phát được 24kHz; (b) 100% token ID ∈ vocab 178
  (kiểm lại mỗi lần chạy); (c) provenance đầy đủ; (d) baseline WAV lưu làm
  nhánh A/B "trước fine-tune".

### T3-B — Manifest data nhà (v27A B2 — ĐÃ LÀM 02/10)
- **Nguồn:** data EN nhà (đường dẫn + quy mô + format + sha256 từng nguồn +
  nguồn gốc/consent) — `06_train_t3/data/en3h/manifest_t3b.json`
  (schema hamster.tang3.data_manifest/0.1).
- **Re-G2P toàn bộ transcript bằng pipeline mình** (`prep_en3h.py`: tầng 1 →
  IR → g2p_stream → nối profile_debug.text): 1.733/1.760 câu đạt chuẩn
  (27 câu quarantine vì từ OOV route-vi `unresolved` — hành vi an toàn đúng
  thiết kế; liệt kê + lý do trong `quarantine.txt`); token hóa lossless đối
  chiếu bảng 178 của fork (0 ký tự lạ); 2,945 h đo được; chia train/val seed
  20261002 (1.673/60).
- **Quy ước text tầng 3 (v2, 02/10 — do chủ dự án bắt được bằng tai):** chuỗi
  profile phải **join các từ bằng space (ID 16 vocab 178) và giữ dấu câu
  `, . ! ? ; :` từ IR** — predictor gốc (đóng băng stage-1) học trên text có
  space/dấu câu; quy ước v1 (nối liền) cho audio nhanh/lướt (t04: 3s vs misaki
  5s). Lượt train v1 (base nạp đúng, text v1) lưu `logs/en3h_t3c_s1_v1_nospace/`,
  demo v1 đã xóa; lượt v2 là lượt hiện hành. Ghi chú cho tầng 2: **đây là quy
  ước CONSUMER khi nối profile per-token thành câu** — profile_debug.text của
  từng token không đổi; nếu sau này muốn chuẩn hóa ở tầng 2 (emit space/dấu câu
  trong adapter) thì đi qua vòng review riêng.
- **Ranh giới train/test:** bộ này do chủ dự án chỉ định LÀM TRAIN; corpus_ir_1M
  (test-only) KHÔNG đem đi train (bất biến giữ nguyên).
- **Ghi chú tương lai (Nit LibriTTS hạ cấp thành ghi chú theo v27A §B1):** nếu
  sau này muốn mở rộng EN, repo đúng là `mythicinfinity/libritts_r`
  (CC-BY-4.0, không gated) hoặc openslr.org/141 — **không phải**
  `openslr/libritts-r` (bản v26 viết sai, repo không tồn tại).
- **Recipe cũ:** nếu bộ data trùng bộ từng train VI-10h — mang recipe theo
  (đã mang: `en_only_3ep.yml` + run_stage.sh + OOM-ladder measurements của
  `04_kokoro_tts/06_train` — cùng khuôn stage-1, cùng venv).

### T3-C — Fine-tune EN + gate nghe (ĐANG CHẠY 02/10)
- **Stage-1** `train_first.py` (fork, không sửa) — config
  `06_train_t3/configs/en3h_t3c_stage1.yml`: batch 2 (chủ dự án + OOM-ladder
  recipe cũ), **3 epoch** (phép thu của chủ dự án: "ổn = 90% thành công"),
  save mỗi epoch để nghe phân hóa; base = bản pinned (bọc `{"net": …}` 1 lần
  — `pretrained/kokoro_v1_0_wrapped.pth`, weights byte-cùng-nguồn bản pinned).
- Chạy `python train_first.py` TRỰC TIẾP (không `accelerate launch`): launch
  CLI nạp `mixed_precision: bf16` từ default_config của máy → decoder iSTFTNet
  chết ở phép complex (`mul_cuda BComplex32`, torch 2.14); python trực tiếp =
  fp32 thuần — đúng recipe cũ đã chạy thành công.
- **Gate nghe — mang nguyên 4 điều kiện §2 PHAN_QUYET_V26 + v27A B3:** bộ demo
  cố định + seed; A/B (baseline model gốc → / fine-tune từng epoch) cùng
  text/giọng/tốc độ; phiếu CSV per câu (đúng âm tiết / tự nhiên 1–5; thanh
  điệu N/A cho EN); không đặt ngưỡng MOS; kiểm 100% token ID ∈ vocab. Người
  nghe: chủ dự án. Objective kèm theo: mel loss theo step, gate thời lượng
  per câu so với base (ngắn hơn 0,5% → FAIL — dấu hiệu sai đường render).
- **Tiêu chí chốt:** phiếu nghe có kết luận + mọi "sai" thành regression/dev
  item có nhãn (khuôn E4); checkpoint + provenance + phiếu vào bundle.

### T3-D — Train mix EN-VI (~10h data nhà — v27A B3)

> **KẾT QUẢ 02/10 (đã chạy xong — cùng ngày với T3-C):** chủ dự án chỉ đạo
> dùng bộ mix nhà `syn_mix_*` (audio `05_data/…/norm/vi/`, −26 dBFS), KHÔNG
> LibriTTS-R, và **train tiếp từ checkpoint T3-C** ("nó quen với G2P mới
> rồi"). Trước khi train: phát hiện lỗ hổng route tầng 1 (từ EN trong câu
> mix bị route VI → G2P chối → 95,9% câu có token thiếu) → hồ sơ bằng chứng
> `06_train_t3/data/mix3/HO_SO_LOI_ROUTE_MIX.md` → chủ dự án xác nhận bằng
> tai → vá tầng 1 (branch cmudict + pass 2/3 skip `cmudict_en`, có backup +
> 44/44 tests + 315/316 đối chứng, 0 hồi quy mới) → re-G2P đạt **2.129 câu /
> 5,4488h (61,9% sau cách ly — phần cách ly là câu đặc tên riêng ngoại)**.
> Train: batch 2, 3 epoch, chuyển giao đủ 13/13 module từ T3-C;
> **val [0.204 → 0.188 → 0.182]** (T3-C kết thúc ở 0.209; khởi điểm Mel 0,46
> so với 0,84 của T3-C — chuyển giao ấm đúng như dự kiến). Demo nghe thử:
> `06_train_t3/demo/demo_t3d/` — 5 nhánh (t3c/mix_ep1-3) × 2 voicepack
> (vi=diem_trinh, en=af_heart) × 20 câu = 160 wav, **8/8 GATE OK** (lệch
> thời lượng 0,0% là đúng kỳ vọng — stage-1 đóng băng predictor), hướng dẫn
> `demo_t3d/NGHE_THU.md`, sha `demo_t3d/wav_sha256.txt`. Replay EN không
> đưa vào train list (chỉ mix) — chống quên dựa vào 3 epoch ngắn + câu EN
> thuần trong demo (t09/10/15/17/19) làm kiểm không-quên; nếu nghe thấy lệch
> → thêm replay EN ở lượt sau.

- **Đầu vào:** bộ mix EN-VI nhà (~10h; chủ dự án từng train VI 10h cho chất
  lượng tốt). GHI RÕ tỉ lệ EN:VI trong mix; **giữ replay EN** để không quên
  ngược; **eval CẢ HAI ngôn ngữ trong lúc train**; nếu còn **checkpoint
  VI-10h cũ** → dùng làm nhánh tham chiếu A/B tiếng Việt.
- Gate nghe VI 3 tiêu chí đầy đủ: đúng âm tiết / thanh điệu / tự nhiên 1–5
  — khớp bộ tiêu chí gate E6 cũ (PHAN_QUYET_V26 §2.1); coda tắc chỉ sắc/nặng
  nghe đúng.
- **Tiêu chí chốt:** như T3-C + thanh điệu.

### T3-E — Báo cáo tầng 3 + đóng
- Báo cáo buổi làm kèm số liệu mọi gate; cập nhật README **chỉ khi chủ dự
  án yêu cầu** (README byte-frozen theo ràng buộc hiện hành).

#### T3-E diễn biến 03/10 (lượt nghiêm túc mix5 19,3h)
- **Stage-1 DỪNG SỚM theo lệnh chủ dự án** lúc epoch 7/10 (04:15): "stop với
  stage 1, giữ checkpoint đó và chuyển qua stage 2 để tôi nghe thử 1 2 3
  epoch". Checkpoint giữ: `logs/t3e_mix5_s1/epoch_latest.pth` = epoch 6 hoàn
  chỉnh, val Mel **0,177** (chuỗi [0.198, 0.191, 0.187, 0.181, 0.177, 0.177]);
  đã backup `ssd_samsung/backup_t3_ckpt/t3e_s1_epoch_latest.pth`. Kill bằng
  PID (1468645) đúng luật.
- **Demo dọn lại theo lệnh chủ dự án** ("xóa demo loạn, đặt tên 01_ 02_…"):
  cây mới `06_train_t3/demo/` = `01_base_kokoro_goc` (base gốc), `02_t3c_en3h`,
  `03_t3d_mix3`, `04_t3e_s1_chot` (epoch 6, render GPU, 4/4 GATE OK), sau này
  thêm `05–07_t3e_s2_ep1..3`; guide duy nhất `00_NGHE_THU.md`; sha256 160 wav
  trong `wav_sha256.txt`. ĐÃ XÓA: base, base_misaki, ep1–3, demo_t3d, demo_t3e,
  phieu_nghe_t3c, render_summary cũ (demo superseded — luật dự án).
- **Stage-2 nghe thử 3 epoch** đang chạy: config `t3e_mix5_s2_cap16.yml` +
  `launch_t3e_s2.sh`, base = stage-1 epoch_latest (cơ chế recipe cũ
  first_stage_path + ignore_modules, predictor_encoder=deepcopy(style_encoder),
  8 module nạp ấm). List cap16 ≤16s (`prep_cap16.py`: giữ 9.228/9.283 câu =
  18,66h — recipe cũ OOM câu 22s batch 2). `joint_epoch: 3` ⇒ cả 3 epoch pha
  pre-joint: train predictor/bert (đúng chỗ sửa nhịp "việt như anh"), decoder
  giữ nguyên. Đã tắt `set_detect_anomaly` (debug-only, bật lại T3_ANOMALY=1).
  Smoke 59 câu 1 epoch PASS trước launch (29 step, ckpt step 10/20 keep-2,
  epoch_latest/best ghi đúng).
- Watcher nền `watch_s2_render.sh`: sau mỗi epoch render demo 05/06/07 bằng
  CPU (GPU bận train), GATE so với 02_t3c_en3h.
- **Ep1 stage-2 xong 05:07 (val 0,244)**, demo `05_t3e_s2_ep1` render OK sau
  khi vá 1 lỗi nạp checkpoint (state_dict stage-2 có tiền tố `module.` vì
  train_second bọc MyDataParallel trước khi lưu — render_t3.py strip prefix,
  strict=True). **GATE: 20/20 câu NGẮN hơn t3c, trung bình −13,5% (vi) /
  −15,9% (en)** — kỳ vọng của pha pre-joint: predictor siết nhịp từ kiểu
  EN-base (đọc kéo) về kiểu data; ngưỡng GATE 0,5% là của stage-1 (predictor
  đóng băng), ở stage-2 chỉ mang nghĩa thông tin. RMS ≈0,05 — audio khỏe.
  Rủi ro ghi nhận: EN replay mỏng (2,9h) nên nhịp EN cũng co — chờ chủ dự án
  nghe 05/en vs 04/en.

## 4. Pin tài nguyên

| Tài nguyên | Version/Revision | sha256 | License | Trạng thái |
|---|---|---|---|---|
| hexgrad/Kokoro-82M (base EN) | `f3ff3571791e39611d31c381e3a41a3af07b4987` | `496dba118d1a58f5…` (pth) | Apache-2.0 | **ĐÃ TẢI, pin phê chuẩn v26** |
| voices/af_heart.pt | cùng revision | `0ab5709b8ffab19b…` | Apache-2.0 | ĐÃ TẢI |
| Data EN nhà (train T3-C) | `05_data/01_data_1/en` — manifest `data/en3h/manifest_t3b.json` | metadata.txt sha trong manifest | tự tổng hợp (audio synth af_heart) | **ĐÃ MANIFEST 02/10** |
| Data mix nhà (train T3-D) | `syn_mix_*` từ `tts_dataset_30k_wav.txt`, audio `norm/vi/` — manifest `data/mix3/manifest_t3b_mix.json` | manifest sha | tự tổng hợp (data nhà, chỉ ĐỌC) | **ĐÃ MANIFEST 02/10 — 2.129 câu / 5,4488h sau vá route** |
| Checkpoint T3-C | `logs/en3h_t3c_s1/first_stage.pth` | sha trong `run_info.json` | train từ base pin | **ĐÃ XONG 02/10 — val 0.209** |
| Checkpoint T3-D | `logs/mix3_t3d_s1/first_stage.pth` (+ epoch_1st_0000{0,1,2}.pth) | sha trong `run_info.json` | train từ T3-C | **ĐÃ XONG 02/10 — val 0.182** |
| Patch tầng 1 route cmudict | `01_tiny_model/02_rules/t0/` (+dicts 126.052 từ) | backup `02_rules/backups/t0_bak_20261002_205827/` | — | **ĐÃ VÁ 02/10** — `00_docs/07_PATCH_CMUDICT_ROUTE_20261002.md` |
| Fork Kokoro-Vietnamese (pipeline) | commit `a249afe5555aec6c435165c2f61ec0f71284812f` | — | theo repo | đã pin từ trước |
| Recipe cũ + venv train | `04_kokoro_tts/06_train` + `00_env/.venv` (torch 2.14.0+cu130) | — | — | tham chiếu |
| LibriTTS-R (tương lai nếu mở rộng EN) | repo đúng `mythicinfinity/libritts_r` (v27A §B1) — pin lúc tải | — | CC-BY-4.0 | ghi chú, không chặn |
| contextboxai/Kokoro-Vietnamese | **RÚT ở v26** | — | — | lưu hồ sơ |

## 5. 4 điều kiện chuyển tiếp từ PHAN_QUYET_V26 §2 (bắt buộc mang theo)

1. Gate nghe giữ đủ bộ tiêu chí cũ: bộ demo cố định + seed, A/B cùng
   text/giọng/tốc độ, phiếu CSV per câu (đúng âm tiết / thanh điệu / tự nhiên
   1–5), không ngưỡng MOS, kiểm 100% token ID ∈ vocab. → nhúng T3-A/C/D.
2. Thứ tự EN trước rồi VI — milestone rõ ràng. → T3-B/C rồi T3-D.
3. 2 quyết treo KHÔNG RƠI: `spell_vi seed` + policy [B] (spell-rate + token
   'tiêu'/'Bây' đọc ngang) — liệt kê ở mục 6. **v27A: cần xong trước khi
   re-G2P text VI ở T3-D (không chặn T3-A→C).**
4. Mọi artifact tầng 3 theo khuôn bundle B/C/D/E (pin + hash + provenance) —
   reviewer audit như thường lệ.

## 6. Chờ chủ dự án (không rơi)

1. **Nguồn data audio tiếng Việt / bộ mix 10h** (T3-D) — **ĐÃ QUYẾT 02/10
   (chủ dự án): dùng bộ mix nhà `syn_mix_*` + audio `norm/vi/` ngay cho lượt
   đầu (5,45h dùng được sau vá); phần VI-10h cũ / mở rộng 10h để lượt sau nếu
   nghe thử chưa đủ.**
2. `spell_vi seed` — decision pending từ fase B.
3. Policy [B]: spell-rate word-token + token không dấu ('tiêu'/'Bây') đọc
   ngang trung thực — có fold tần suất hay không. (27 câu quarantine EN 02/10
   là thêm dữ liệu cho quyết này — từ OOV EN route-vi.)

## 7. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Catastrophic forgetting khi fine-tune | T3-D: giữ replay EN + eval cả 2 ngôn ngữ trong lúc train (v27A B3) |
| Data EN 3h ít → overfit | 3 epoch là phép thu; gate nghe per epoch + early-stop; checkpoint mỗi epoch |
| Frontend gốc (misaki) chênh lệch nhánh A/B | A/B theo v27A: baseline gốc vs fine-tune, CÙNG text pipeline G2P hamster |
| Token mới nghe sai dù ID hợp lệ | đúng trọng tâm fine-tune; regression list theo khuôn E4 |
| GPU OOM khi train | batch 2 (OOM-ladder recipe cũ: 11,1 GiB đỉnh); expandable_segments |
| Label noise (misaki đọc khác tầng-1: số năm "1906", route-vi từ ASCII) | ước tính nhỏ; nếu gate nghe bắt được từ hỏng → regression item có nhãn, lọc data vòng sau |

## 8. Ràng buộc giữ nguyên

Test data không train (bộ EN nhà = TRAIN theo chỉ định chủ dự án; corpus_ir_1M
test-only); không copy/di dời model (`06_models` bất động; weights Kokoro ở
`03_vendor/kokoro_en_weights/` — bản bọc `{"net"}` nằm ở `06_train_t3/pretrained/`
là artifact dẫn xuất có provenance); không đụng dữ liệu ngoài `05_TTS/`
(data nhà chỉ ĐỌC); kill bằng PID; pin revision + checksum + license mọi thứ
tải về; README byte-frozen.
