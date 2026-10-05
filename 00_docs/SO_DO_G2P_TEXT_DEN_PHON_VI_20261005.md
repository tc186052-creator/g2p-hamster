# SƠ ĐỒ LUỒNG G2P — từ văn bản đến phôn vị (xuất 05/10/2026)

Tài liệu trực quan hóa **đúng trạng thái đang chạy**, mọi chặng ghi kèm file
thực sự trong máy. Kèm ví dụ chạy sống 2 dòng trong `demo/test.txt`.

---

## 1. Bức tranh 3 tầng

```
 VĂN BẢN
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 1 — t0 (02_rules/t0/pipeline.py, hàm normalize)                │
│  "chuẩn hóa + quyết định ĐỌC gì" → sinh token IR ir/0.1             │
└─────────────────────────────────────────────────────────────────────┘
    │  tokens[]: i, surface, cat, route, read, verbal, break, intonation
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 2 — G2P hamster (02_hamster_G2P/01_g2p/g2p.py, hàm g2p_stream) │
│  "verbal → CHUỖI PHÔN VỊ master ham" → profile kokoro178            │
└─────────────────────────────────────────────────────────────────────┘
    │  (profile, errs)  — errs ≠ rỗng ⇒ CẢ CÂU bị loại (điểm mất câu)
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 3 — TTS (06_train_t3/scripts/tts_file.py → model Kokoro m8)    │
│  gộp câu, synth theo voicepack, cắt/khử nhiễu → WAV                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tầng 1 — t0: text → token IR

```
text ("Tạ Côi cứng đờ… \"Yư Dạng!\"")
   │
   ├─▶ [1] textproc.clean — NFC, bỏ ký tự lạ, chuẩn hóa dấu câu, tách emoji/icon
   │
   ├─▶ [2] textproc.tokenize — tách word / punct / số
   │
   ├─▶ [3] detect.detect — PHÂN LOẠI cat + SINH verbal (phần ĐỌC):
   │        cat ∈ {word, abbr, acronym, number, money, time, date, unit,
   │                phone, pm_am, url, email, punct, icon, …}
   │        tra các bảng từ điển (t0/dicts.py):
   │          • abbrev_vi.tsv  → verbal là TỪ CHỐT (yư→ư, bad→bét,
   │                             tsundere→tùn đờ rê, vali→va li …)
   │          • kho_quyet_vi   → từ vi không dấu đa nghĩa, chốt đọc
   │          • EN dict top-500 + từ điển đọc vi hóa
   │        số/money/time/unit → verbalize (12 → "mười hai", "$5" → "năm đô la")
   │        cat=mơ hồ (kho_bat / oov / acronym) → tiny2 trọng tài
   │          (CHỈ khi câu có token số/tiền/giờ/năm/đơn vị — gate 03/10)
   │
   ├─▶ [4] assign_routes — gán route cho từng token: vi | en | neu
   │        (EN khi token là từ EN có trong dict/CMUdict, hoặc cả câu sent=en)
   │
   └─▶ [5] xuất IR ir/0.1 (schema đóng băng, hợp đồng G2P_00_hop_dong_dau_vao.md)
            token: {i, surface, cat, route, read, verbal, break, intonation, origin}
            read_string: chuỗi đọc ghép (dấu dính sát từ)
```

**Nguyên tắc hợp đồng**: G2P nhận token NGUYÊN XI — không sửa câu, không tự
normalization lại, không tự suy route mới.

---

## 3. Tầng 2 — G2P: token IR → phôn vị (01_g2p/g2p.py `g2p_stream`)

Mỗi token đi một nhánh:

```
token IR
   │
   ├─ cat = punct ──────────▶ status=CONTROL — im lặng, chỉ giữ break/intonation
   │                          (dấu , . ! ? : được phát LẠI ở bước join cuối)
   │
   ├─ cat = icon / lạ ──────▶ status=NOT_WORD — deferred tường minh
   │
   ├─ read = spell ─────────▶ đọc theo tên chữ:
   │        route=en → 26 tên chữ US (cmu_en.LETTER_NAMES) từng ký tự
   │        route=vi  → tier-1 đã spell-out trong verbal (vd email)
   │
   ├─ route = en ───────────▶ mỗi read unit (tách verbal theo dấu cách):
   │        cmu_en.pronounce — tra CMUdict (~126k entry)
   │          hit            → status=ok
   │        miss → spell theo tên chữ (lưu fallback_reason)
   │        không nucleus  → no_nucleus
   │
   └─ route = vi ───────────▶ mỗi read unit, TƯỜNG LUẬT THEO BẬC:
            (1) scope QD57 (02_data/collision/qd57_scope_exclusions.json
                — ledger từ CẤM phát âm)          → scope_excluded
            (2) VS.parse (vi_syllable.py — luật âm tiết vi:
                onset/glide/vần/coda/thanh)        → ok
            (3) fold_vi.tsv (02_data/fold/ — từ ASCII không dấu, đoán theo
                tần suất corpus, pin sha256; re-check scope ứng viên) → fold
            (4) spell_vi.tsv (02_data/spell_vi.tsv — đơn chữ, seed chờ duyệt) → spell
            (5) hết đường                        → UNRESOLVED ★điểm gãy
```

Sau khi mọi token có status:

```
roll-up: status của token = XẤU NHẤT trong các unit của nó
   thang: control < ok < fold < spell < no_nucleus <
          scope_excluded < UNRESOLVED < not_word < unknown_route

VALIDATE GATE (g2p.py D18-03): status thuộc nhóm CẤM PHÁT ÂM
   {scope_excluded, unresolved, not_word, unknown_route, no_nucleus, control}
   ⇒ KHÔNG serialize profile — kể cả bị gắn syllables (fault injection không lọt)

transform kokoro178 (01_g2p/profiles.py): record master ham
   (onset/glide/nucleus/coda/tone) → chuỗi ký tự thuộc bảng 178 của Kokoro
   ⇒ profile_debug.text của từng token
```

---

## 4. Bước nối cuối — text_to_profile (06_train_t3/scripts/prep_en3h.py)

```
profile từng token + dấu câu
   │  • punct trong {, . ! ? ; :} → phát lại surface (ID 1-6 vocab 178)
   │  • join kiểu misaki: SPACE giữa các từ, dấu câu DÍNH SÁT từ trước
   │    (v2 02/10 — predictor model gốc học trên text có space + dấu câu;
   │     nối liền ⇒ đọc nhanh/lướt ~40%)
   ▼
(profile, errs)
   │
   ├─ errs = []  ──▶ TẦNG 3 synth
   │
   └─ errs ≠ [] ──★ ĐIỂM MẤT CÂU ★
        tts_file.py: thử GỘP với câu kế (pend merge-retry v2 — 05/10,
        không giết câu kế) → vẫn lỗi ⇒ BỎ CẢ CÂU, ghi vào ghi_chu.
        Cùng cơ chế ở các script prep_*: câu lỗi vào quarantine,
        KHÔNG vào tập train.
```

### Ba chốt fail-closed của tầng 2 (điểm có thể "gãy" hiện tại)
| # | Chốt | Vị trí | Hành vi |
|---|------|--------|---------|
| 1 | Âm tiết ngoài luật + không có trong mọi bảng | `g2p.py _vi_unit` | status `unresolved` → cả câu bị caller bỏ |
| 2 | Scope QD57 | `collision_audit.py` | từ trong ledger cấm → không phát âm, không lách |
| 3 | Resource pins | `g2p.py _verify_resource_pins` | fold/spell/cmu/ledger lệch sha ⇒ SystemExit, không chạy lệch |

→ Chốt 1 là nguyên nhân "hở một từ mất nguyên câu" anh vừa phát hiện.
Chốt 2-3 là chủ ý an toàn (cấm bịa phát âm, cấm chạy đè lên bảng bị sửa).

---

## 5. Ví dụ chạy sống (từ `demo/test.txt`)

### Dòng 65: `Đã lo lắng thì cứ thừa nhận, cần gì phải tsundere vòng vo tam quốc thế chứ?`

```
T1: tok[0..6]  word vi "Đã lở lắng thì cứ thừa nhận" (nguyên dạng)
    tok[7]     punct ','  break=minor
    tok[11]    word vi "tsundere" — abbrev dict → verbal "tùn đờ rê" (TỪ CHỐT)
    tok[18]    punct '?'  break=major  intonation=rising
G2P: rec[0..6]  ok   → daːʔ↗ lɔ la↗ŋ θi↘ kɨ↗ θɨə↘ ɲəʔ↓n
     rec[7]     control (phát lại "," ở bước join)
     rec[11]    ok   → tu↘ndəː↘ʒe   (3 âm tiết "tùn đờ rê" qua luật vi)
     rec[18]    control → "?" + rising
PROFILE: daːʔ↗ lɔ la↗ŋ θi↘ kɨ↗ θɨə↘ ɲəʔ↓n, kə↘n ʝi↘ faː↓j tu↘ndəː↘ʒe vɔ↘ŋ vɔ taːm kwo↗k θe↗ cɨ↗?
errs: []   → synth
```

### Dòng 92: `Tôi vịnh vali, ngồi co ro trước cửa nhà Tạ Côi.`

```
T1: tok[2] abbr vi "vali" — abbrev dict → verbal "va li"
G2P: rec[2] ok → vaːli  (2 âm tiết "va"+"li" nối thành liên âm vaːli — 1 token)
     rec[3] control → ","
PROFILE: toj viʔ↓ɲ vaːli, ŋo↘j kɔ ʒɔ ʈʂɨə↗k kɨə↓ ɲaː↘ taːʔ↓ koj.
errs: []   → synth
```

### Trước khi vá — dòng 76 từng gãy thế này:
```
T1: "Yư Dạng" — "Yư" KHÔNG phải âm tiết vi hợp lệ (y+ư trơn ngoài bảng)
G2P: tok "Yư" → (1) không scope, (2) VS.parse FAIL (ngoài inventory),
     (3) không trong fold_vi, (4) không đơn chữ ⇒ UNRESOLVED
     ⇒ status token = unresolved ⇒ profile_debug.errors ≠ []
     ⇒ errs ≠ [] ⇒ CẢ CÂU BỊ BỎ (mất "Tạ Côi cứng đờ trong chốc lát…")
Vá hiện tại: abbrev_vi.tsv "yư→ư" — quyết định ĐỌC GÌ thuộc tầng 1,
không phải việc G2P bịa phôn vị. (vá 04/10, có ghi nguồn [VA 04/10/2026])
```

---

## 6. Bảng kê file thật trong luồng

| Chặng | File | Vai trò |
|-------|------|---------|
| T1 clean/tokenize | `02_rules/t0/textproc.py` | NFC, ký tự lạ, tách token |
| T1 detect | `02_rules/t0/detect.py` | cat + verbal + route |
| T1 từ điển abbrev | `02_rules/t0/data/abbrev_vi.tsv` | yư→ư, bad→bét, vali→va li… |
| T1 kho chốt | `02_rules/t0/data/kho_quyet_vi` | từ vi không dấu đa nghĩa |
| T1 trọng tài | `02_rules/t0/tiny2_mc.py` | mơ hồ số/tiền/giờ… |
| IR contract | `02_hamster_G2P/00_docs/G2P_00_hop_dong_dau_vao.md` | schema ir/0.1 |
| G2P lõi | `01_g2p/g2p.py` | g2p_stream, validate gate, roll-up |
| Luật âm tiết | `01_g2p/vi_syllable.py` (ĐÓNG BĂNG) | parse onset/vần/coda/thanh |
| Master vi | `01_g2p/vi_rules.py` (ĐÓNG BĂNG) | chữ → record ham |
| Ledger cấm | `02_data/collision/qd57_scope_exclusions.json` | scope QD57 |
| Fold | `02_data/fold/fold_vi.tsv` | ASCII → có dấu (prior tần suất) |
| Spell vi | `02_data/spell_vi.tsv` | tên chữ (seed chờ duyệt) |
| EN | `01_g2p/cmu_en.py` + CMUdict | ~126k entry, spell tên chữ |
| Profile 178 | `01_g2p/profiles.py` + vocab 178 | record ham → chuỗi Kokoro |
| Nối cuối | `06_train_t3/scripts/prep_en3h.py` `text_to_profile` | join misaki |
| Caller TTS | `06_train_t3/scripts/tts_file.py` | gộp câu, drop câu lỗi, synth |

> Bảng phôn vị để đối soát từng dòng: `06_train_t3/demo/bang_phon_vi_test_20261005.md`
> (script xuất: `06_train_t3/scripts/bang_phon_vi_test.py`).
