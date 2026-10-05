# Điều 7 — realization-collision report (fase B, vòng 6.1)

**Status: PASS**

**Phạm vi:** Audit trên MIỀN ỨNG VIÊN có chứng thực trong corpus phiên bản b920363a160b…, ngưỡng tần suất 2 — KHÔNG là xác nhận toàn bộ miền chính tả lõi tiếng Việt; thu hẹp gate không đồng nghĩa giải quyết ngôn ngữ các nhóm ngoài gate (được lưu dấu đầy đủ trong trace_files).

Sinh 27210 dạng (attested 6801 · ext 13299 · stress 7110) → nhóm GATE (≥2 attested): **83** — approved 45 · excluded_v1 38 · proposal 0 · identity 0 · unexplained 0
Nhóm ext (miền mở rộng, không gate — lưu dấu đầy đủ trong dieu7_ext_groups.jsonl): 5010 · stress-only (lưu dấu trong dieu7_stress_groups.jsonl): 1557
Kiểm core độc lập (accept/reject): 27+18 từ — 0 lỗi · căn cứ miền (regression attestation): 20+6 — 0 lỗi
Pin hành vi miền: domain_config_hash 8d46700fd03ffde123a53b3d571fa29e81bbb69dbfdfe623ba333962113e02d8

Pin policy duyệt exact fixture: approval_policy_hash 46659a0c165e7e711e236af84760bfc615c43997531995bad617486217a097a4 (45 fixture; approved_scope=core_spellings)

Pin scope-exclusion QD57-2026-10-02 (38 nhóm excluded_v1; ledger sha256 1930c63ccd231cf3…; chủ dự án chấp thuận 02/10 — excluded ≠ approved)

Kiểm ranh giới scope (R14-01): 39 excluded + 37 protected member qua boundary exact NFC+lower giữ dấu (exact/UPPER/NFD) — 0 lỗi · scope_policy_hash 3ea6fa8d5827beff… (R14-02)

## approved:EXACT_FIXTURE — 45 nhóm (vd: ỉ, ì, i, í)

## excluded_v1:MR-CODA-CH-C — 3 nhóm (vd: chếc, níc, tíc)

## excluded_v1:MR-CODA-I-Y — 1 nhóm (vd: âi)

## excluded_v1:MR-CODA-O-U — 19 nhóm (vd: eo, io, beo, bio)

## excluded_v1:MR-CODA-O-U+MR-ONSET-C-K — 1 nhóm (vd: cấo)

## excluded_v1:MR-I-Y — 7 nhóm (vd: ĩ, iên, iểu, di)

## excluded_v1:MR-ONSET-C-K+MR-QU-K-GLIDE — 1 nhóm (vd: cuới)

## excluded_v1:MR-ONSET-C-K+MR-QU-K-GLIDE+MR-UE-UÊ — 1 nhóm (vd: cue)

## excluded_v1:MR-UE-UÊ — 5 nhóm (vd: hue, sue, tue, thue)

## Đối chứng đối lập (tai≠tay, tui≠tuy…): 21 OK, 0 FAIL