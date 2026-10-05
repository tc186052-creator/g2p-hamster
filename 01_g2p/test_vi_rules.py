# -*- coding: utf-8 -*-
"""test_vi_rules.py — nghiệm thu fase B (schema §6 acceptance 3.1-3.3 + đặc tả 4.6).

Khối test:
  A. fixtures đối lập phải KHÁC chuỗi master (tai≠tay, cao≠cau, mác≠mách, an≠anh,
     nam≠năm, tam≠tăm + bổ sung) — bảo toàn đối lập mức chuỗi, không qua spell.
  B. fixtures đồng âm phải CÙNG chuỗi + được MR giải thích trọn vẹn.
  C. roundtrip render↔parse trên toàn bộ không gian sinh + ví dụ chính tả thật.
  D. matcher MERGE_RULES: giải thích đúng; CẮT PHẦT chỉ-phần (lí/lín) → FAIL.
  E. tone_state/stress_state unresolved — transform profile TỪ CHỐI (schema §4/3.3).
  F. spell seed + audit static.
Chạy: 03_vendor/venv_vig2p/bin/python 01_g2p/test_vi_rules.py
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inventory  # noqa: E402
import vi_rules as R  # noqa: E402
import vi_syllable  # noqa: E402
from vi_syllable import parse, parse_word, ParseError, skeleton_of  # noqa: E402
from profiles import ViSyllable, EnSyllable, transform_vi, transform_en  # noqa: E402
from collision_audit import enumerate_syllables, id_sequence  # noqa: E402

_PASS = _FAIL = 0


def check(name, cond, detail=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL: {name} {detail}")


def seq_of(text, tone=None):
    sk, ti = R.strip_tone(text)
    p = R.parse_skeleton(sk)
    assert p, f"parse lỗi: {text!r}"
    tone = tone or R.TONE_BY_INDEX[ti]
    return id_sequence(p, tone)


# ---------------------------------------------------------------- A. đối lập
CONTRAST_PAIRS = [
    ("tai", "tay"), ("cao", "cau"), ("mác", "mách"), ("khắc", "khác"), ("an", "anh"),
    ("nam", "năm"), ("tam", "tăm"), ("suất", "suốt"), ("que", "quê"),
    # bổ sung cùng họ đối lập
    ("mai", "may"), ("khao", "khau"), ("lạc", "lắc"), ("en", "ên"),
    ("ô", "ơi"), ("khô", "kho"), ("sao", "sau"), ("reo", "rêu"),
    ("dìa", "dia"), ("mưa", "mơ"), ("khu", "khư"), ("xuất", "xứt"),
    # ba vần: bảo toàn BA chiều (duyệt 02/10 — bắt buộc, không phải [B])
    ("mách", "mắc"), ("khách", "khắc"),
    # vòng 4 (F01): uy composite vs ui coda — cặp bị MR-I-Y che trước đây
    ("tui", "tuy"), ("thúi", "thúy"), ("huy", "hu"), ("khui", "khuy"),
]


def test_contrasts():
    for a, b in CONTRAST_PAIRS:
        check(f"đối lập {a} ≠ {b}", seq_of(a) != seq_of(b))


# ---------------------------------------------------------------- B. đồng âm + rule
# VÒNG 4: KHÔNG còn rule approved=true ở tầng matcher (MR-I-Y bị hạ cờ sau khi
# matcher global che lỗi thật tui/tuy) — mọi fixture đồng âm rơi vào lớp ĐỀ XUẤT.
MERGE_PAIRS = {}
PROPOSED_MERGE_PAIRS = {
    "MR-I-Y": [("kí", "ký"), ("tí", "tý"), ("mía", "m\u00fda"),
               ("qui", "quy"), ("in", "yn"), ("lí", "lý")],
    "MR-ONSET-GH-G": [("ge", "ghe"), ("nga", "ngha")],
    "MR-ONSET-C-K": [("ca", "ka"), ("c\u00ea", "k\u00ea")],
    "MR-CODA-CH-C": [("ích", "íc")],
    "MR-CODA-O-U": [("ưu", "ưo")],
    "MR-CODA-I-Y": [("ây", "âi")],
    "MR-UE-UÊ": [("kue", "ku\u00ea")],
    "MR-GLIDE-O-U": [("co\u1ebfn", "cu\u1ebfn")],   # oê/uê cùng tail n → cùng chuỗi W,E
    "MR-QU-K-GLIDE": [("kuy", "quy")],   # qua/koa KHÔNG còn nối (V5-04) — kuy/quy
}


def test_merges():
    for rule_id, pairs in MERGE_PAIRS.items():
        for a, b in pairs:
            sa, sb = seq_of(a), seq_of(b)
            check(f"đồng âm {a} = {b}", sa == sb, f"{sa} vs {sb}")
            skels = sorted({skeleton_of(x)[0] for x in (a, b)})
            check(f"{a} = {b} giải thích bởi {rule_id}",
                  rule_id in (inventory.explain_collision(skels) or ()))


def test_proposed_rules():
    """Rule approved=false: chỉ ghi nhận hành vi matcher — KHÔNG phải nghiệm thu."""
    for rule_id, pairs in PROPOSED_MERGE_PAIRS.items():
        for a, b in pairs:
            skels = sorted({skeleton_of(x)[0] for x in (a, b)})
            check(f"[đề xuất, chưa duyệt] {a}/{b} hiện được {rule_id} giải thích",
                  rule_id in (inventory.explain_collision(skels) or ()))
    # tui ≠ tuy (F01): KHÔNG còn đồng âm, KHÔNG được rule nào giải thích
    check("tui ≠ tuy (F01 — đã sửa parser)",
          seq_of("tui") != seq_of("tuy"))
    check("tui/tuy KHÔNG được giải thích bởi rule nào",
          inventory.explain_collision(["tui", "tuy"]) is None)
    # ộk là ca ngoại lai (coda k ngoài lõi) — rule ch/c KHÔNG tự giải thích c↔k
    check("ộch/ộk KHÔNG được giải thích (c≠k ở coda)",
          inventory.explain_collision(["ộch", "ộk"]) is None)
    # đối lập que/quê không được rule đề xuất che (khác chuỗi → matcher không chạy)
    check("que ≠ quê (rule đề xuất không đụng)",
          seq_of("que") != seq_of("quê"))


# ---------------------------------------------------------------- D. matcher probe
# V5-03: tên RIÊNG cho từng test — hai hàm cùng tên trước đây làm probe vòng 4 bị
# định nghĩa đè (runner chỉ chạy bản sau). Runner có kiểm tên trùng ở __main__.
def test_matcher_negative_probes():
    """Probe reviewer vòng 4 (§4/F04) + vòng 5 (V5-04): matcher structural + guard
    record KHÔNG được giải thích các cặp ngoài scope — kiểm trên cùng API probe."""
    probes_none = [
        ["tai", "tay"],      # i/y rule KHÔNG đụng coda (A_SHORT vs A_LONG)
        ["quai", "quay"],    # như trên
        ["ac", "ak"],        # rule onset KHÔNG đụng coda c/k
        ["ke", "kê"],        # composite rule KHÔNG đụng bare (không glide)
        ["que", "quê"],      # qu-branch glide_letter='' → composite không áp
        ["khoa", "khua"],    # CÙNG onset kh, khác vần oa/ua (sửa văn bản vòng 5)
        ["li", "lin"],       # rơi coda không được che (acceptance 3.2)
        ["ách", "ắc"],       # khác nucleus (a vs ă) — required contrast
        ["cao", "cau"],      # V5-04: tail o→u đổi nucleus (COND_NUC) — engine chặn
        ["kue", "que"],      # V5-04: k:u→qu đổi nucleus E vs OPEN_E — engine chặn
        ["qua", "koa"],      # V5-04: nối qua 'kua' không phải chính tả — chặn
    ]
    for pair in probes_none:
        check(f"{pair[0]}/{pair[1]} KHÔNG được giải thích",
              inventory.explain_collision(pair) is None)
    # bio/byo/biu/byu cần HỢP 2 matcher structural (form i/y × tail o/u)
    got = inventory.explain_collision(["bio", "byo", "biu", "byu"])
    check("bio/byo/biu/byu giải thích bởi hợp 2 rule",
          got is not None and set(got) == {"MR-I-Y", "MR-CODA-O-U"}, f"{got}")
    # tiered (§5.4): thử approved trước — hiện 0 rule approved → tier proposal
    tier, rules = inventory.explain_collision_tiered(["li", "ly"])
    check("tiered li/ly → proposal (0 rule approved)", tier == "proposal", f"{tier}")
    tier2, _ = inventory.explain_collision_tiered(["tui", "tuy"])
    check("tiered tui/tuy → unexplained (cặp khác chuỗi, không phải collision)",
          tier2 == "unexplained")
    # V5-04: identity tier — hai chính tả parse về CÙNG parts (gi/gii) không cần rule
    tier3, rules3 = inventory.explain_collision_tiered(["gi", "gii"])
    check("tiered gi/gii → identity (parts vốn giống, không phải merge)",
          tier3 == "identity" and rules3 == (), f"{tier3},{rules3}")


# ---------------------------------------------------------------- C. roundtrip
REAL_WORDS = {
    "tỏi": ("PHONE_T", (), "PHONE_OPEN_O", "PHONE_J", "TONE_HOI"),
    "quốc": ("PHONE_K", ("PHONE_W",), "PHONE_O", "PHONE_K", "TONE_SAC"),
    "khuya": ("PHONE_KH", ("PHONE_W",), "PHONE_I_SCHWA", None, "TONE_NGANG"),
    "khuyên": ("PHONE_KH", ("PHONE_W",), "PHONE_I_SCHWA", "PHONE_N", "TONE_NGANG"),
    "xoáy": ("PHONE_S", ("PHONE_W",), "PHONE_A_SHORT", "PHONE_J", "TONE_SAC"),
    "mưa": ("PHONE_M", (), "PHONE_UHORN_SCHWA", None, "TONE_NGANG"),
    "tươi": ("PHONE_T", (), "PHONE_UHORN_SCHWA", "PHONE_J", "TONE_NGANG"),
    "mu\u00f4i": ("PHONE_M", (), "PHONE_U_SCHWA", "PHONE_J", "TONE_NGANG"),
    "má": ("PHONE_M", (), "PHONE_A_LONG", None, "TONE_SAC"),
    "mã": ("PHONE_M", (), "PHONE_A_LONG", None, "TONE_NGA"),
    "mạ": ("PHONE_M", (), "PHONE_A_LONG", None, "TONE_NANG"),
    "trưởng": ("PHONE_TR", (), "PHONE_UHORN_SCHWA", "PHONE_NG", "TONE_HOI"),
    "xuất": ("PHONE_S", ("PHONE_W",), "PHONE_SCHWA", "PHONE_T", "TONE_SAC"),
    "kỹ": ("PHONE_K", (), "PHONE_I", None, "TONE_NGA"),
    "Huế": ("PHONE_H", ("PHONE_W",), "PHONE_E", None, "TONE_SAC"),
    "nghe": ("PHONE_NG", (), "PHONE_OPEN_E", None, "TONE_NGANG"),
    "ưu": (None, (), "PHONE_UHORN", "PHONE_W", "TONE_NGANG"),
    "kho\u00e9t": ("PHONE_KH", ("PHONE_W",), "PHONE_OPEN_E", "PHONE_T", "TONE_SAC"),
    # vòng 4 (F01): uy composite vs ui coda
    "tuy": ("PHONE_T", ("PHONE_W",), "PHONE_I", None, "TONE_NGANG"),
    "tui": ("PHONE_T", (), "PHONE_U", "PHONE_J", "TONE_NGANG"),
    "thúy": ("PHONE_TH", ("PHONE_W",), "PHONE_I", None, "TONE_SAC"),
    "thúi": ("PHONE_TH", (), "PHONE_U", "PHONE_J", "TONE_SAC"),
    "huy": ("PHONE_H", ("PHONE_W",), "PHONE_I", None, "TONE_NGANG"),
    # vòng 4 (F02): onset gi
    "gì": ("PHONE_GI", (), "PHONE_I", None, "TONE_HUYEN"),
    "gìn": ("PHONE_GI", (), "PHONE_I", "PHONE_N", "TONE_HUYEN"),
    "gi\u00eang": ("PHONE_GI", (), "PHONE_I_SCHWA", "PHONE_NG", "TONE_NGANG"),
    "gi\u1ebft": ("PHONE_GI", (), "PHONE_I_SCHWA", "PHONE_T", "TONE_SAC"),
    "gia": ("PHONE_GI", (), "PHONE_A_LONG", None, "TONE_NGANG"),
    "gi\u1ecdng": ("PHONE_GI", (), "PHONE_OPEN_O", "PHONE_NG", "TONE_NANG"),
    # vòng 4 (F03): vần lõi trước bị loại
    "bu\u1ed3m": ("PHONE_B_IMP", (), "PHONE_U_SCHWA", "PHONE_M", "TONE_HUYEN"),
    "mu\u1ed7m": ("PHONE_M", (), "PHONE_U_SCHWA", "PHONE_M", "TONE_NGA"),
    "khu\u1ef7u": ("PHONE_KH", ("PHONE_W",), "PHONE_I", "PHONE_W", "TONE_HOI"),
}


def test_real_words():
    for w, exp in REAL_WORDS.items():
        rec = parse(w)
        on, gl, nuc, coda = rec.onset, rec.glide, rec.nucleus, (rec.coda[0] if rec.coda else None)
        got = (on[0] if on else None, gl or (), nuc, coda, rec.tone)
        want = (exp[0], exp[1], exp[2], exp[3], exp[4])
        check(f"parse {w!r}", got == want, f"got={got} want={want}")
        # tone_state: có dấu trong chữ gốc → diacritic; không dấu → policy ngang
        want_state = "diacritic" if R.strip_tone(w.lower())[1] != 1 else "policy"
        check(f"{w!r} tone_state {want_state}", rec.tone_state == want_state,
              f"got {rec.tone_state}")


def test_roundtrip():
    combos = enumerate_syllables()
    check("không gian sinh > 1000 combo", len(combos) > 1000, f"n={len(combos)}")
    bad = []
    for item in combos:
        parts, tone = item[:4], item[4]
        spelling = R.render_parts(*parts, tone)
        sk, ti = R.strip_tone(spelling)
        p = R.parse_skeleton(sk)
        if p != parts or R.TONE_BY_INDEX[ti] != tone:
            bad.append((parts, spelling))
        # profile conformance: record hợp lệ + chuỗi profile không lỗi
        seq = id_sequence(parts, tone)
        for mid in seq[:-1]:
            if not any(r["id"] == mid for r in inventory.load_cached()):
                bad.append((parts, f"ID lạ {mid}"))
    check("roundtrip toàn không gian sinh", not bad, f"vd {bad[:3]}")


# ---------------------------------------------------------------- D2. public parser
def test_public_parser_contract():
    """Vòng 4 (§5.1 — reviewer): đối chứng đối lập phải đi qua PUBLIC parse()
    (record + validation), không chỉ parse_skeleton nội bộ. So CHUỖI ĐẦY ĐỦ gồm
    tone (dìa/dia chỉ khác tone là đúng thiết kế — tone là trục riêng); kiểm
    SEGMENT-bỏ-tone làm riêng trên bộ SEGMENT_ONLY_PAIRS."""
    for a, b in CONTRAST_PAIRS:
        ra, rb = parse(a), parse(b)
        full_a = tuple(ra.onset) + tuple(ra.glide) + (ra.nucleus,) + tuple(ra.coda) \
            + (ra.tone,)
        full_b = tuple(rb.onset) + tuple(rb.glide) + (rb.nucleus,) + tuple(rb.coda) \
            + (rb.tone,)
        check(f"public parse đối lập {a} ≠ {b}", full_a != full_b,
              f"{full_a} vs {full_b}")
    SEGMENT_ONLY_PAIRS = [
        ("mác", "mách"), ("mách", "mắc"), ("mác", "mắc"),
        ("tai", "tay"), ("cao", "cau"), ("que", "quê"),
        ("tui", "tuy"), ("thúi", "thúy"), ("suất", "suốt"),
    ]
    for a, b in SEGMENT_ONLY_PAIRS:
        ra, rb = parse(a), parse(b)
        seg_a = tuple(ra.onset) + tuple(ra.glide) + (ra.nucleus,) + tuple(ra.coda)
        seg_b = tuple(rb.onset) + tuple(rb.glide) + (rb.nucleus,) + tuple(rb.coda)
        check(f"public parse segment {a} ≠ {b} (bỏ tone)", seg_a != seg_b,
              f"{seg_a} vs {seg_b}")
    # F05: parse() là hàm thuần — KHÔNG còn tham số fold âm thầm sửa âm tiết hợp lệ
    import inspect
    sig = inspect.signature(parse)
    check("parse() không còn tham số fold", "fold" not in sig.parameters,
          str(sig))
    rec = parse("trong")
    check("trong → policy ngang (không fold)", rec.tone_state == "policy")


# ---------------------------------------------------------------- D. matcher cắt phần
def test_matcher_negative():
    # 3.2: rule i/y KHÔNG được che lỗi rơi coda (lí/lín)
    check("lí/lín KHÔNG được giải thích",
          inventory.explain_collision(["li", "lin"]) is None)
    # khác coda m/n
    check("kim/kin KHÔNG được giải thích (k≠c rule không áp)",
          inventory.explain_collision(["kim", "kin"]) is None)
    # group tích 2 chiều biến thể cần HỢP matcher
    check("bio/byo/biu/byu giải thích bởi hợp 2 rule",
          inventory.explain_collision(["bio", "byo", "biu", "byu"]) is not None)
    # "ách" = "ắc" (khác a/ă — required contrast) KHÔNG được giải thích
    check("ách/ắc KHÔNG được giải thích",
          inventory.explain_collision(["ách", "ắc"]) is None)


# ---------------------------------------------------------------- E. unresolved (§4/3.3)
def test_unresolved():
    by_id = {r["id"]: r for r in inventory.load()}
    v = ViSyllable(onset=("PHONE_M",), nucleus="PHONE_A_LONG",
                   tone="", tone_state="unresolved")
    check("validate unresolved vi OK", not v.validate(by_id))
    res = transform_vi(v, by_id)
    check("transform_vi TỪ CHỐI unresolved", bool(res.errors))
    v2 = ViSyllable(onset=("PHONE_M",), nucleus="PHONE_A_LONG",
                    tone="TONE_NGANG", tone_state="unresolved")
    check("unresolved + tone → validate FAIL", bool(v2.validate(by_id)))
    e = EnSyllable(onset=("PHONE_B",), nucleus="PHONE_IH", stress="",
                   stress_state="unresolved")
    check("validate unresolved en OK", not e.validate(by_id))
    res2 = transform_en(e, by_id)
    check("transform_en TỪ CHỐI unresolved", bool(res2.errors))
    e2 = EnSyllable(onset=("PHONE_B",), nucleus="PHONE_IH",
                    stress="STRESS_PRIMARY", stress_state="unresolved")
    check("unresolved + stress → validate FAIL", bool(e2.validate(by_id)))
    # policy: chữ không dấu (giữ horn hợp lệ) đọc nguyên dạng — tường minh "policy"
    rec = parse("trong")
    check("trong → policy ngang", rec.tone_state == "policy" and rec.tone == "TONE_NGANG")
    # TUC (4.6.5): coda tắc chỉ sắc/nặng — "mach" không phải âm tiết chuẩn → ParseError
    # (nhánh fold ỦY QUỀN mới được chọn ứng viên; parser không tự phục hồi thanh)
    try:
        parse("mach")
        check("mach phải ParseError (TUC)", False)
    except ParseError:
        check("mach phải ParseError (TUC)", True)
    # ASCII trùng fold ("truong" = trưởng) KHÔNG parse được — đúng: thuộc fold/spell
    try:
        parse("truong")
        check("truong ASCII phải ParseError", False)
    except ParseError:
        check("truong ASCII phải ParseError", True)


# ---------------------------------------------------------------- E2. core + status (vòng 5)
def test_core_domain():
    """V5-01: kiểm ĐỘC LẬP miền core — từ thật phải thuộc core, tổ hợp ngoài chính
    tả phải bị loại (accept/reject tường minh, KHÔNG lấy output generator làm đáp án)."""
    from collision_audit import (is_core, CORE_ACCEPT, CORE_REJECT,
                                 core_acceptance_check)
    for w in CORE_ACCEPT:
        p = R.parse_skeleton(R.strip_tone(w)[0])
        check(f"core accept {w!r}", p is not None and is_core(p), f"parts={p}")
    for w in CORE_REJECT:
        p = R.parse_skeleton(R.strip_tone(w)[0])
        check(f"core reject {w!r}", p is not None and not is_core(p), f"parts={p}")
    check("core_acceptance_check() 0 lỗi", core_acceptance_check() == [])


def test_compute_status():
    """V5-05: status tính MỘT NƠI từ mọi điều kiện lỗi — contrast/core/domain fail
    đưa thẳng về FAIL, không bị proposal 'nuốt'."""
    from collision_audit import compute_status
    check("contrast fail → FAIL", compute_status(0, 0, [("ma", "ma", None)], []) == "FAIL")
    check("core fail → FAIL", compute_status(0, 0, [], [("x", "lỗi")]) == "FAIL")
    check("unexplained → FAIL", compute_status(3, 0, [], []) == "FAIL")
    check("domain fail → FAIL (vòng 6)",
          compute_status(0, 0, [], [], [("gii", "lỗi")]) == "FAIL")
    check("domain fail + proposal → FAIL",
          compute_status(0, 5, [], [], [("gii", "lỗi")]) == "FAIL")
    check("proposal → PENDING_APPROVAL",
          compute_status(0, 5, [], []) == "PENDING_APPROVAL")
    check("sạch → PASS", compute_status(0, 0, [], []) == "PASS")
    check("contrast fail + proposal → FAIL (không nuốt)",
          compute_status(0, 5, [("ma", "ma", None)], []) == "FAIL")


# ---------------------------------------------------------------- E3. căn cứ miền attestation (vòng 6)
def test_core_domain_attestation():
    """Vòng 6 §9.1: core = is_core(ngữ cảnh) ∩ attestation corpus tầng 1. Ca reviewer
    câi/mấi/bêo phải rớt khỏi core (lớp ext), từ thật cây/mấy/bêu giữ core; bảng
    pin phải khớp hash provenance; regression miền 0 lỗi; gate chỉ nhận nhóm
    ≥2 core-attested (ây/âi… không còn nhóm ext-only đòi duyệt)."""
    from collision_audit import (load_attestation, attest_class, ATTEST_MIN_FREQ,
                                 domain_regression_check, domain_config_hash,
                                 build_groups, is_core, load_scope_exclusions)
    import unicodedata as U
    vocab, prov = load_attestation()
    check("vocab attestation > 100.000 dạng token", len(vocab) > 100_000,
          f"n={len(vocab)}")
    check("provenance có nguồn + sha256 corpus",
          bool(prov.get("source")) and all(s.get("sha256") for s in prov["source"]))
    check("provenance khai unit 'dạng token' (không phải âm tiết thẩm định)",
          "dạng token" in prov.get("unit", ""))
    check("provenance khai supplement bị loại + 0 hit từ chẩn đoán",
          prov.get("supplement_exclusion", {}).get("sha256")
          and prov["supplement_exclusion"].get("gold_diagnostic_word_hits") == {})
    dh = domain_config_hash(vocab, prov)
    check("domain_config_hash 64-hex ổn định",
          len(dh) == 64 and dh == domain_config_hash(vocab, prov))

    def cls(w):
        sk, ti = R.strip_tone(w)
        return attest_class(R.parse_skeleton(sk), R.TONE_BY_INDEX[ti], vocab)

    for w in ["cây", "mấy", "bêu", "tay", "lý", "kỹ", "sỹ", "quy", "thuê"]:
        check(f"attested core: {w!r}", cls(w) == "core")
    for w in ["câi", "mấi", "bêo", "buâi", "buây"]:
        check(f"ext (không attested): {w!r}", cls(w) == "ext",
              f"is_core={is_core(R.parse_skeleton(R.strip_tone(w)[0]))}")
    for w in ["nge", "ngê", "coa", "koa", "tym"]:
        check(f"stress (ngoài ngữ cảnh): {w!r}", cls(w) == "stress")
    check("domain_regression_check() 0 lỗi", domain_regression_check(vocab) == [])

    # phân bucket: gate chỉ ≥2 core-attested; nhóm ext không vào gate
    combos = enumerate_syllables()
    _q, exclusions = load_scope_exclusions()
    sel = [c for c in combos if U.normalize("NFC", R.render_parts(
        *c[:4], c[4])).lower() in {"sĩ", "sỹ", "ây", "âi", "cây", "câi",
                                   "nge", "nghe", "ka", "ca"}]
    gate, ext, stress, _ = build_groups(sel, vocab, exclusions)
    gate_pairs = {tuple(sorted(g["core_spellings"])): g for g in gate}
    check("sĩ/sỹ vào gate, duyệt EXACT_FIXTURE (vòng 6.3 — không qua matcher rộng)",
          ("sĩ", "sỹ") in gate_pairs
          and gate_pairs[("sĩ", "sỹ")]["rule"] == "EXACT_FIXTURE"
          and gate_pairs[("sĩ", "sỹ")].get("exact_fixture") is True)
    check("ây/âi vào gate theo dữ liệu, tier excluded_v1 (QD57 — không duyệt coda i/y)",
          ("âi", "ây") in gate_pairs
          and gate_pairs[("âi", "ây")]["tier"] == "excluded_v1"
          and gate_pairs[("âi", "ây")]["rule"] == "MR-CODA-I-Y"
          and gate_pairs[("âi", "ây")]["scope_exclusion"]["subject"]
          and gate_pairs[("âi", "ây")]["scope_exclusion"]["protected"])
    check("gate entry có freq từng spelling",
          all(g.get("core_freqs", {}).get(s, 0) >= ATTEST_MIN_FREQ
              for g in gate for s in g["core_spellings"]))
    ext_all = {s for g in ext for s in g["ext_spellings"]}
    check("cây/câi nhóm ext (câi không attested — không đòi duyệt đồng âm)",
          "câi" in ext_all)
    gate_spellings = {s for g in gate for s in g["core_spellings"]}
    check("không spelling ext nào lọt gate", not (ext_all & gate_spellings))
    stress_all = {s for g in stress for s in g["spellings"]}
    check("nge/ka vẫn stress không gate", {"nge", "ka"} <= stress_all)

    # vòng 6.2 (R61-01): đơn vị đếm là TOKEN NGUYÊN DẠNG — provenance phải khai rõ
    check("provenance unit khai 'token NGUYÊN DẠNG' + KHÔNG tách",
          "NGUYÊN DẠNG" in prov.get("unit", "")
          and "KHÔNG tách" in prov["field_spec"].get("frequency_unit", ""))
    check("provenance stats không còn trường tách (bỏ tokens_split/skipped)",
          "tokens_split" not in prov.get("stats", {})
          and "tokens_skipped" not in prov.get("stats", {}))


def test_builder_literal_counting():
    """Vòng 6.2 R61-01: builder phải đếm TOKEN NGUYÊN DẠNG — corpus tổng hợp chỉ
    chứa 'lựchọc' (không có token literal 'lựch') KHÔNG được sinh ra freq 'lựch'
    (lỗi cũ: tách theo số dấu thanh → 'lựch'+'ọc' → gate giả lực/lựch)."""
    import gzip as _gzip
    import json as _json
    import tempfile
    import build_core_domain as B
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        words = (["lựchọc"] * 2 + ["lực"] * 2 + ["họctập"] * 2 + ["thànhphố"])
        recs = [{"source": "SYNTHETIC_TEST_FIXTURE_KHONG_PHAI_CORPUS",
                 "ir": {"tokens": [{"cat": "word", "route": "vi",
                                    "verbal": w}]}} for w in words]
        recs.append({"source": "SYNTHETIC_TEST_FIXTURE_KHONG_PHAI_CORPUS",
                     "ir": {"tokens": [{"cat": "word", "route": "en",
                                        "verbal": "english"},
                                       {"cat": "punct", "route": "vi",
                                        "verbal": "."}]}})
        main_gz = td / "synthetic.jsonl.gz"
        with _gzip.open(main_gz, "wt", encoding="utf-8") as f:
            for r in recs:
                f.write(_json.dumps(r, ensure_ascii=False) + "\n")
        sup_gz = td / "sup.jsonl.gz"
        with _gzip.open(sup_gz, "wt", encoding="utf-8") as f:
            f.write("")
        old = B.CORPUS, B.SUPPLEMENT, B.OUT_DIR
        try:
            B.CORPUS = [main_gz]
            B.SUPPLEMENT = sup_gz
            B.OUT_DIR = td / "out"
            rc = B.main()
            vocab = {}
            for line in (td / "out" / "vi_syllable_vocab.tsv") \
                    .read_text(encoding="utf-8").splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                w, n = line.split("\t")
                vocab[w] = int(n)
        finally:
            B.CORPUS, B.SUPPLEMENT, B.OUT_DIR = old
        check("synthetic builder chạy xong", rc == 0)
        check("token nguyên dạng được đếm literal đúng",
              vocab.get("lựchọc") == 2 and vocab.get("lực") == 2
              and vocab.get("họctập") == 2 and vocab.get("thànhphố") == 1)
        for fake in ("lựch", "ọc", "họct", "ập", "thànhph", "ố"):
            check(f"KHÔNG tự sinh mảnh {fake!r}", fake not in vocab)
        check("token route=en không lọt bảng", "english" not in vocab)


def test_domain_hash_covers_classifier():
    """Vòng 6.2 R61-02: domain_config_hash phải phủ HÀNH VI classifier — mutation
    bảng is_core (như probe reviewer: CORE_ONSET_FIRST['k'].add('a')) hoặc đổi
    ngưỡng/list regression đều phải làm hash ĐỔI. Hash 2 lần liên tiếp phải giống."""
    from collision_audit import (load_attestation, domain_config_hash,
                                 attest_class, ATTEST_MIN_FREQ, CORE_ONSET_FIRST)
    import unicodedata as U
    import vi_rules as _R
    vocab, prov = load_attestation()

    def cls_ka(v):
        return attest_class(("k", "", "a", ""), "TONE_NGANG", v)

    h0 = domain_config_hash(vocab, prov)
    check("hash ổn định 2 lần gọi", h0 == domain_config_hash(vocab, prov))
    check("ka stress trước mutation", cls_ka(vocab) == "stress")

    old_set = CORE_ONSET_FIRST["k"].copy()
    try:
        CORE_ONSET_FIRST["k"].add("a")
        h1 = domain_config_hash(vocab, prov)
        check("mutation bảng classifier → hash ĐỔI (R61-02)",
              h1 != h0 and cls_ka(vocab) == "core")
    finally:
        CORE_ONSET_FIRST["k"] = old_set
    check("restore bảng → hash về giá trị gốc",
          domain_config_hash(vocab, prov) == h0 and cls_ka(vocab) == "stress")

    import collision_audit as _C
    old_min = _C.ATTEST_MIN_FREQ
    try:
        _C.ATTEST_MIN_FREQ = 99
        check("đổi ATTEST_MIN_FREQ → hash ĐỔI",
              domain_config_hash(vocab, prov) != h0)
    finally:
        _C.ATTEST_MIN_FREQ = old_min
    old_not = _C.DOMAIN_MUST_NOT[:]
    try:
        _C.DOMAIN_MUST_NOT.append("lý")
        check("đổi DOMAIN_MUST_NOT → hash ĐỔI",
              domain_config_hash(vocab, prov) != h0)
    finally:
        _C.DOMAIN_MUST_NOT[:] = old_not
    check("ngưỡng/list restore → hash gốc", domain_config_hash(vocab, prov) == h0)
    _ = U, _R  # giữ import dùng cho probe mở rộng


def test_reviewer_iy_fixtures():
    """Vòng 6.1+6.3+QD57: reviewer XÁC NHẬN 26 cặp i/y + 19 cặp duyệt mới QD57
    (2026-10-02, chủ dự án chấp thuận) ở MỨC FIXTURE — expected record VIẾT TƯỜNG
    MINH trước (không lấy output parser làm đáp án), khớp APPROVED_EXACT_FIXTURES
    trong inventory. Giới hạn duyệt: chỉ các cặp đầy đủ dấu này ở chế độ đọc từ VI
    nguyên dạng, KHÔNG suy rộng thành matcher rộng; 19 cặp mới KHÔNG áp cho tên
    chữ/spelling/viết tắt/phát âm nguyên ngữ tên ngoại."""
    fixtures = [
        (["kí", "ký"], ["PHONE_K"], [], "PHONE_I", [], "TONE_SAC"),
        (["lí", "lý"], ["PHONE_L"], [], "PHONE_I", [], "TONE_SAC"),
        (["kì", "kỳ"], ["PHONE_K"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["kĩ", "kỹ"], ["PHONE_K"], [], "PHONE_I", [], "TONE_NGA"),
        (["mĩ", "mỹ"], ["PHONE_M"], [], "PHONE_I", [], "TONE_NGA"),
        (["sĩ", "sỹ"], ["PHONE_S_RETRO"], [], "PHONE_I", [], "TONE_NGA"),
        (["tỉ", "tỷ"], ["PHONE_T"], [], "PHONE_I", [], "TONE_HOI"),
        (["qui", "quy"], ["PHONE_K"], ["PHONE_W"], "PHONE_I", [], "TONE_NGANG"),
        # 18 fixture bổ sung — quyết reviewer v11 (2026-10-02 §5.2)
        (["hi", "hy"], ["PHONE_H"], [], "PHONE_I", [], "TONE_NGANG"),
        (["hỉ", "hỷ"], ["PHONE_H"], [], "PHONE_I", [], "TONE_HOI"),
        (["kỉ", "kỷ"], ["PHONE_K"], [], "PHONE_I", [], "TONE_HOI"),
        (["li", "ly"], ["PHONE_L"], [], "PHONE_I", [], "TONE_NGANG"),
        (["mì", "mỳ"], ["PHONE_M"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["tí", "tý"], ["PHONE_T"], [], "PHONE_I", [], "TONE_SAC"),
        (["hí", "hý"], ["PHONE_H"], [], "PHONE_I", [], "TONE_SAC"),
        (["kị", "kỵ"], ["PHONE_K"], [], "PHONE_I", [], "TONE_NANG"),
        (["lì", "lỳ"], ["PHONE_L"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["quì", "quỳ"], ["PHONE_K"], ["PHONE_W"], "PHONE_I", [], "TONE_HUYEN"),
        (["quí", "quý"], ["PHONE_K"], ["PHONE_W"], "PHONE_I", [], "TONE_SAC"),
        (["quĩ", "quỹ"], ["PHONE_K"], ["PHONE_W"], "PHONE_I", [], "TONE_NGA"),
        (["quỉ", "quỷ"], ["PHONE_K"], ["PHONE_W"], "PHONE_I", [], "TONE_HOI"),
        (["ti", "ty"], ["PHONE_T"], [], "PHONE_I", [], "TONE_NGANG"),
        (["tì", "tỳ"], ["PHONE_T"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["tị", "tỵ"], ["PHONE_T"], [], "PHONE_I", [], "TONE_NANG"),
        (["ì", "ỳ"], [], [], "PHONE_I", [], "TONE_HUYEN"),
        (["ỉ", "ỷ"], [], [], "PHONE_I", [], "TONE_HOI"),
        # 19 fixture duyệt mới — QD57-2026-10-02 (hồ sơ pin 02_data/collision/qd57/:
        # 19_fixture_moi.json; 38/38 dạng khớp parser theo kiem_record_19_fixture)
        (["hì", "hỳ"], ["PHONE_H"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["i", "y"], [], [], "PHONE_I", [], "TONE_NGANG"),
        (["iêng", "yêng"], [], [], "PHONE_I_SCHWA", ["PHONE_NG"], "TONE_NGANG"),
        (["ki", "ky"], ["PHONE_K"], [], "PHONE_I", [], "TONE_NGANG"),
        (["lị", "lỵ"], ["PHONE_L"], [], "PHONE_I", [], "TONE_NANG"),
        (["mi", "my"], ["PHONE_M"], [], "PHONE_I", [], "TONE_NGANG"),
        (["mỉ", "mỷ"], ["PHONE_M"], [], "PHONE_I", [], "TONE_HOI"),
        (["mị", "mỵ"], ["PHONE_M"], [], "PHONE_I", [], "TONE_NANG"),
        (["ni", "ny"], ["PHONE_N"], [], "PHONE_I", [], "TONE_NGANG"),
        (["rì", "rỳ"], ["PHONE_R_VI"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["si", "sy"], ["PHONE_S_RETRO"], [], "PHONE_I", [], "TONE_NGANG"),
        (["sì", "sỳ"], ["PHONE_S_RETRO"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["thi", "thy"], ["PHONE_TH"], [], "PHONE_I", [], "TONE_NGANG"),
        (["thì", "thỳ"], ["PHONE_TH"], [], "PHONE_I", [], "TONE_HUYEN"),
        (["vi", "vy"], ["PHONE_V"], [], "PHONE_I", [], "TONE_NGANG"),
        (["vĩ", "vỹ"], ["PHONE_V"], [], "PHONE_I", [], "TONE_NGA"),
        (["vị", "vỵ"], ["PHONE_V"], [], "PHONE_I", [], "TONE_NANG"),
        (["xi", "xy"], ["PHONE_S"], [], "PHONE_I", [], "TONE_NGANG"),
        (["í", "ý"], [], [], "PHONE_I", [], "TONE_SAC"),
    ]
    check("tổng fixture = 26 cũ + 19 QD57 = 45",
          len(fixtures) == 45, f"n={len(fixtures)}")
    for words, onset, glide, nuc, coda, tone in fixtures:
        for w in words:
            s = parse(w)
            got = (list(s.onset), list(s.glide), s.nucleus, list(s.coda), s.tone)
            exp = (onset, glide, nuc, coda, tone)
            check(f"fixture reviewer {w!r} = {onset}{'+' + glide[0] if glide else ''}"
                  f"+{nuc}+{tone}", got == exp, f"got={got}")


def test_exact_fixture_approval_scope():
    """Vòng 6.3 (reviewer v11 §3/§6.2): approval phải EXACT — đúng cặp đầy đủ dấu
    + đúng tone + record khớp; negative tests cho cặp ngoài allowlist, sai tone,
    nhóm chứa thêm thành viên; NFD phải normalize về NFC rồi mới khớp (positive).
    MR-I-Y.approved vẫn False — flag rộng sẽ nâng 52 nhóm (probe reviewer v11)."""
    import unicodedata as U2
    from inventory import (explain_exact_fixture, APPROVED_EXACT_FIXTURES,
                           MERGE_RULES, WITHDRAWN_RULES)
    check("catalog có đúng 45 exact fixture (26 + 19 QD57)",
          len(APPROVED_EXACT_FIXTURES) == 45, f"n={len(APPROVED_EXACT_FIXTURES)}")
    check("MR-I-Y vẫn approved=False (không bật flag rộng)",
          next(r for r in MERGE_RULES if r["rule_id"] == "MR-I-Y")["approved"]
          is False)
    check("MR-ACH-EC đã rút khỏi catalog (withdrawn — quyết v11 §4)",
          all(r["rule_id"] != "MR-ACH-EC" for r in MERGE_RULES)
          and any(r["rule_id"] == "MR-ACH-EC" for r in WITHDRAWN_RULES))

    check("positive: nhóm kí/ký TONE_SAC được duyệt exact",
          explain_exact_fixture({"kí", "ký"}, "TONE_SAC") == "EXACT_FIXTURE")
    check("positive: NFD normalize về NFC vẫn khớp (không phải bỏ dấu)",
          explain_exact_fixture({U2.normalize("NFD", "kí"), "ký"},
                                "TONE_SAC") == "EXACT_FIXTURE")
    check("positive: cặp không onset ì/ỳ được duyệt",
          explain_exact_fixture({"ì", "ỳ"}, "TONE_HUYEN") == "EXACT_FIXTURE")
    check("positive QD57: ki/ky được duyệt (QD57 §6.4 — negative cũ chuyển positive)",
          explain_exact_fixture({"ki", "ky"}, "TONE_NGANG") == "EXACT_FIXTURE")
    check("positive QD57: iêng/yêng (nucleus I_SCHWA, coda NG) được duyệt",
          explain_exact_fixture({"iêng", "yêng"}, "TONE_NGANG") == "EXACT_FIXTURE")
    check("negative QD57: cặp chưa duyệt di/dy (excluded_v1) không qua fixture",
          explain_exact_fixture({"di", "dy"}, "TONE_NGANG") is None)
    # Lớp fixture hoạt động trên NFC-lower (thiết kế): 'I'/'NY' hoa normalize về
    # dạng thường — lệnh cấm đọc chữ cái/viết tắt/EN là scope VI-word ở tầng route/
    # mode (QD57 §2.1), KHÔNG thuộc dict fixture này; ở đây chỉ kiểm cặp chữ hoa
    # trùng nhau không tạo nhóm mới.
    check("negative: hai spelling normalize về một dạng không tạo nhóm được duyệt",
          explain_exact_fixture({"NY", "ny"}, "TONE_NGANG") is None)
    check("negative: sai tone (ký/kĩ) không được duyệt",
          explain_exact_fixture({"ký", "kĩ"}, "TONE_NGA") is None
          and explain_exact_fixture({"ký", "kĩ"}, "TONE_SAC") is None)
    check("negative: sai tone cặp QD57 (thì/thỳ khác ngang) không được duyệt",
          explain_exact_fixture({"thì", "thỳ"}, "TONE_NGANG") is None)
    check("negative: nhóm chứa thêm thành viên không được duyệt (superset guard)",
          explain_exact_fixture({"kí", "ký", "kỳ"}, "TONE_SAC") is None)
    check("negative: một mình một từ không phải nhóm (len≠2)",
          explain_exact_fixture({"ký"}, "TONE_SAC") is None)

    # 10 cặp ach/ec là ĐỐI LẬP bắt buộc ở master (ham/0.2) — kiểm qua id_sequence
    def seg_seq(w):
        sk, ti = R.strip_tone(w)
        return id_sequence(R.parse_skeleton(sk), R.TONE_BY_INDEX[ti])
    for a, b in [("sách", "séc"), ("mách", "méc"), ("bách", "béc"),
                 ("hách", "héc"), ("mạch", "mẹc"), ("tách", "téc"),
                 ("vách", "véc"), ("xách", "xéc"), ("ách", "éc"), ("ạch", "ẹc")]:
        check(f"đối lập mới {a}≠{b} (ham/0.2)", seg_seq(a) != seg_seq(b),
              f"{seg_seq(a)} == {seg_seq(b)}")


def test_approval_fingerprint_and_profile_loss():
    """Vòng 6.3 hậu kiểm (R12-01 + R12-02):
    R12-01 — approval_policy_hash phải phủ catalog exact fixture (runtime): bỏ
    fixture trong RAM → hash ĐỔI và counts 26→25; deterministic khi giữ nguyên.
    R12-02 — profile kokoro178 phải KHAI loss khi collapse PHONE_OPEN_E_PREVELAR:
    mách/méc khác master, export có thể giống, nhưng loss của ID mới phải được ghi."""
    from inventory import (approval_policy_hash, APPROVED_EXACT_FIXTURES,
                           explain_exact_fixture)
    from profiles import transform_vi
    import collision_audit as _C

    h0 = approval_policy_hash()
    check("approval_policy_hash 64-hex, deterministic",
          len(h0) == 64 and h0 == approval_policy_hash())

    original = APPROVED_EXACT_FIXTURES[:]
    try:
        APPROVED_EXACT_FIXTURES[:] = [
            f for f in original if f[0] != "kí"]  # bỏ kí/ký in RAM
        h1 = approval_policy_hash()
        check("mutation catalog → approval_policy_hash ĐỔI (R12-01)", h1 != h0)
        combos = enumerate_syllables()
        vocab, prov = _C.load_attestation()
        _q, exclusions = _C.load_scope_exclusions()
        gate, _, _, _ = _C.build_groups(combos, vocab, exclusions)
        n_app = sum(1 for g in gate if g["tier"] == "approved")
        n_excl = sum(1 for g in gate if g["tier"] == "excluded_v1")
        n_prop = sum(1 for g in gate if g["tier"] == "proposal")
        check("mutation catalog → gate 45→44 approved, kí/ký rơi về proposal",
              n_app == 44 and n_excl == 38 and n_prop == 1,
              f"app={n_app} excl={n_excl} prop={n_prop}")
    finally:
        APPROVED_EXACT_FIXTURES[:] = original
    check("restore catalog → hash gốc + kí/ký được duyệt lại",
          approval_policy_hash() == h0
          and explain_exact_fixture(["kí", "ký"], "TONE_SAC") == "EXACT_FIXTURE")

    # R12-02: loss event cho collapse của ID mới
    by_id = None
    r_mach = transform_vi(parse("mách"))
    r_mec = transform_vi(parse("méc"))
    check("master khác nhau cho mách/méc (ham/0.2)",
          (r_mach.sidecar and r_mec.sidecar
           and any(m == "PHONE_OPEN_E_PREVELAR" for _, m in r_mach.sidecar)))
    check("kokoro178 export khai loss của PHONE_OPEN_E_PREVELAR (R12-02)",
          any(x[0] == "PHONE_OPEN_E_PREVELAR" for x in r_mach.loss),
          f"loss={r_mach.loss}")
    check("export có thể trùng (lossy đã chấp thuận) nhưng loss KHÔNG rỗng",
          r_mach.loss != [])
    r_sach = transform_vi(parse("sách"))
    check("sách cũng ghi loss của ID mới",
          any(x[0] == "PHONE_OPEN_E_PREVELAR" for x in r_sach.loss))


def test_qd57_scope_exclusions():
    """QD57-2026-10-02 (reviewer phán quyết per-group, chủ dự án chấp thuận 02/10):
    38 nhóm excluded_v1 đúng đối tượng — ledger pin bằng sha256, subject bị giới
    hạn còn phía protected KHÔNG bị loại (thuê không kéo theo thue, beo/meo/suê/
    xuê/tiu không bị coi mất dấu), master giữ đối lập quới≠cưới (QD57 §6.5),
    status/counts report tách candidate domain vs accepted v1 scope."""
    import collision_audit as _C
    qd57, exclusions = _C.load_scope_exclusions()
    check("ledger QD57 pin đủ 38 giới hạn", len(exclusions) == 38)
    check("policy_id QD57-2026-10-02", qd57["policy_id"] == "QD57-2026-10-02")
    check("owner approval được ghi trong ledger",
          qd57["owner_approval"].get("date") == "2026-10-02"
          and "chấp thuận" in qd57["owner_approval"].get("note", ""))
    check("scope cấm tên chữ/viết tắt/phát âm nguyên ngữ/phục hồi dấu",
          all(k in qd57["scope"] for k in
              ("NOT letter naming", "abbreviation", "accent restoration")))

    def st(w):
        return _C.scope_exclusion_status(w)

    check("subject bị giới hạn: keu/thue/cuới/siu-alias trả trạng thái có cấu trúc",
          st("keu")["status"] == "scope_excluded_v1"
          and st("thue")["status"] == "scope_excluded_v1"
          and st("cuới")["status"] == "scope_excluded_v1"
          and st("bio")["status"] == "scope_excluded_v1")
    check("protected KHÔNG bị loại: keo/thuê/beo/meo/suê/xuê/tiu/siu → None",
          all(st(w) is None for w in
              ["keo", "thuê", "beo", "meo", "suê", "xuê", "tiu", "siu"]))
    check("từ ngoài ledger → None", st("trèo") is None and st("kêu") is None)
    check("NFC-lower: 'Siu' được xem như 'siu' (protected)", st("Siu") is None)

    # QD57 §6.5: quới KHÔNG thành cưới — master đã phân biệt, không bị policy phá
    def seg(w):
        sk, ti = R.strip_tone(w)
        return id_sequence(R.parse_skeleton(sk), R.TONE_BY_INDEX[ti])
    check("đối lập quới≠cưới giữ nguyên ở master (QD57 §6.5)",
          seg("quới") != seg("cưới"))

    # report gắn pin + thống kê tách riêng
    rep = json.loads((_C.HERE.parent / "02_data" / "collision" / "dieu7_bao_cao.json")
                     .read_text(encoding="utf-8"))
    check("report: 83 gate = 45 approved + 38 excluded_v1 + 0 proposal",
          rep["n_gate_groups_core"] == 83 and rep["n_gate_approved"] == 45
          and rep["n_gate_excluded_v1"] == 38 and rep["n_gate_proposal"] == 0)
    check("report pin ledger sha256 khớp file runtime",
          rep["scope_exclusions_v1"]["ledger_sha256"]
          == hashlib.sha256(_C.QD57_EXCLUSIONS.read_bytes()).hexdigest())
    check("report pin source ledger QD57 (hồ sơ reviewer)",
          rep["scope_exclusions_v1"]["source_ledger_sha256"]
          == hashlib.sha256((_C.HERE.parent / "02_data" / "collision" / "qd57" /
                             "ledger_57_quyet_dinh.json").read_bytes()).hexdigest())
    check("approval_policy_hash ĐỔI khỏi catalog 26 cũ (QD57 §6.3)",
          not rep["approval_exact_fixture"]["approval_policy_hash"]
          .startswith("6eee24db")
          and rep["approval_exact_fixture"]["n_approved_fixtures"] == 45)
    check("excluded KHÔNG có exact_fixture=True",
          all(g.get("exact_fixture") is False for g in rep["gate_groups"]
              if g["tier"] == "excluded_v1"))


def test_qd57_boundary_exact():
    """Vòng 6.5 (R14-01, hậu kiểm v14 §6.1): boundary scope v1 EXACT trên thành viên
    máy đọc — đủ 39 excluded member trả 'scope_excluded_v1' đúng pair, 37 protected
    member trả None; cùng kết quả với uppercase/NFD; ba dạng từng lọt vì là chuỗi
    con của phía protected (chếc⊂chếch, níc⊂ních, tíc⊂tích) nay bị chặn đúng; consumer
    mô phỏng (kiểm scope TRƯỚC, chỉ parse/export khi None) phải dừng cả ba."""
    import unicodedata as U
    import collision_audit as _C
    _, exclusions = _C.load_scope_exclusions()
    n_exc = n_prot = 0
    bad = []
    for pair, e in sorted(exclusions.items()):
        exc, prot = _C._member_sets(e)
        for m in sorted(exc | prot):
            expect_excluded = m in exc
            for v in (m, m.upper(), U.normalize("NFD", m)):
                st = _C.scope_exclusion_status(v)
                if expect_excluded and (st is None
                                        or st["status"] != "scope_excluded_v1"
                                        or st["pair"] != list(pair)):
                    bad.append((v, st))
                if not expect_excluded and st is not None:
                    bad.append((v, st))
            n_exc += expect_excluded
            n_prot += not expect_excluded
    check("boundary exact: đủ 39 excluded member trả trạng thái có cấu trúc",
          n_exc == 39 and not bad, str(bad[:3]))
    check("boundary exact: đủ 37 protected member trả None (uppercase/NFD cùng kết quả)",
          n_prot == 37 and not bad)
    # tue/tuê: ledger giới hạn CẢ HAI phía (QD57 — 'cách dùng chưa xác nhận')
    check("tue và tuê CẢ HAI trả scope_excluded_v1 (ledger không có protected side)",
          _C.scope_exclusion_status("tue")["status"] == "scope_excluded_v1"
          and _C.scope_exclusion_status("tuê")["status"] == "scope_excluded_v1")
    # ba dạng từng lọt vì là chuỗi con của phía protected (probe v14: 73/76)
    check("chếc/níc/tíc bị chặn đúng (chuỗi con của chếch/ních/tích không còn lọt)",
          all(_C.scope_exclusion_status(w)["status"] == "scope_excluded_v1"
              for w in ("chếc", "níc", "tíc"))
          and all(_C.scope_exclusion_status(w) is None
                  for w in ("chếch", "ních", "tích")))
    # consumer mô phỏng đúng cách dùng tín hiệu: kiểm scope trước, chỉ parse/export
    # khi None (probe v14 — consumer cũ để ba dạng đi tiếp, ra ce↗k/ni↗k/ti↗k)
    def consumer(w):
        return None if _C.scope_exclusion_status(w) else f"parse({w})"
    check("consumer kiểm-scope-trước dừng chếc/níc/tíc, cho chếch/ních/tích đi tiếp",
          all(consumer(w) is None for w in ("chếc", "níc", "tíc"))
          and all(consumer(w) is not None for w in ("chếch", "ních", "tích")))
    # report gắn boundary + fingerprint scope
    rep = json.loads((_C.HERE.parent / "02_data" / "collision" / "dieu7_bao_cao.json")
                     .read_text(encoding="utf-8"))
    sc = rep["scope_exclusions_v1"]
    check("report: boundary_check 0 lỗi với 39+37 member",
          sc["boundary_check"]["fail"] == []
          and sc["n_excluded_members"] == 39 and sc["n_protected_members"] == 37)
    check("report: scope_policy_hash khớp module đang chạy (R14-02)",
          sc["scope_policy_hash"] == _C.scope_policy_hash())
    check("report: expected_members_source pin khớp đáp án reviewer",
          sc["expected_members_source"]["sha256"]
          == hashlib.sha256(_C.QD57_EXPECTED_MEMBERS.read_bytes()).hexdigest())


def test_trace_locator_original_index():
    import trace_vocab_members as T
    """Vòng 6.2 T62-01: token_index trong gate_member_trace phải là index GỐC
    trong ir.tokens[] (kể cả punct/token en phía trước), không phải index sau
    lọc — probe synthetic: punct[0], en[1], 'lực'[2] → trace phải ghi 2."""
    import contextlib
    import gzip as _gzip
    import io
    import json as _json
    import tempfile
    import collision_audit as _C
    
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        recs = [{"source": "SYNTHETIC_TEST_FIXTURE_KHONG_PHAI_CORPUS",
                 "ir": {"tokens": [
                     {"cat": "punct", "route": "vi", "verbal": ","},
                     {"cat": "word", "route": "en", "verbal": "Example"},
                     {"cat": "word", "route": "vi", "verbal": "lực"}]}}]
        gz = td / "main.jsonl.gz"
        with _gzip.open(gz, "wt", encoding="utf-8") as f:
            for r in recs:
                f.write(_json.dumps(r, ensure_ascii=False) + "\n")
        rep_dir = td / "02_data" / "collision"
        rep_dir.mkdir(parents=True)
        (rep_dir / "dieu7_bao_cao.json").write_text(_json.dumps(
            {"gate_groups": [{"core_spellings": ["lực"], "ext_spellings": []}]},
            ensure_ascii=False), encoding="utf-8")
        old = T.HERE, T.OUT, T.CORPUS, _C.load_attestation
        try:
            T.HERE = td / "01_g2p"  # trace đọc report tại HERE.parent/02_data/collision
            T.OUT = td / "trace.jsonl"
            T.CORPUS = [gz]
            _C.load_attestation = lambda: (
                {"lực": 1}, {"source": [{"sha256": "0" * 64}]})
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = T.main()
            d = _json.loads(T.OUT.read_text(encoding="utf-8")
                            .splitlines()[0])  # JSONL: 1 dòng = 1 dạng
        finally:
            T.HERE, T.OUT, T.CORPUS, _C.load_attestation = old
        check("trace synthetic chạy xong", rc == 0)
        check("trace locator ghi index GỐC ir.tokens (lực → 2, T62-01)",
              d["form"] == "lực" and d["examples"][0]["token_index"] == 2,
              f"got={d['examples'][0]}")
        check("trace raw_verbal giữ nguyên dạng gốc",
              d["examples"][0]["raw_verbal"] == "lực")
        check("trace ngữ cảnh từ ir.tokens nguyên bản (kể cả punct/en)",
              d["examples"][0]["context"] == ", Example lực",
              f"got={d['examples'][0]['context']!r}")
        check("trace đếm vẫn khớp TSV", d["freq_tsv"] == 1
              and d["n_occurrences_in_corpus"] == 1)


def test_renderer_roundtrip():
    """V5-02: hai chiều word → parts → render → parse trên TỪ THẬT (họ gi từng bị
    renderer viết lặp i thành giìn/giiết). Spelling render ra phải đúng chính tả
    canonical của từ và parse lại ra cùng record phát âm."""
    import unicodedata
    words = ["gì", "gìn", "giêng", "giết", "gia", "giọng", "giỗ", "tuy", "tui",
             "buồm", "muỗm", "khuỷu", "quyên", "quyết", "quyền", "quốc", "mây",
             "cây", "đấy", "khuya", "khoét", "nghe", "yên", "yếu", "xuất"]
    bad = []
    for w in words:
        sk, ti = R.strip_tone(w)
        p = R.parse_skeleton(sk)
        spelling = unicodedata.normalize("NFC", R.render_parts(*p, R.TONE_BY_INDEX[ti]))
        sk2, ti2 = R.strip_tone(spelling)
        p2 = R.parse_skeleton(sk2)
        if p2 != p or ti2 != ti or spelling != unicodedata.normalize("NFC", w):
            bad.append((w, spelling, p, p2))
            continue
        rec1, rec2 = parse(w), parse(spelling)
        if (rec1.onset, rec1.glide, rec1.nucleus, rec1.coda, rec1.tone) != \
                (rec2.onset, rec2.glide, rec2.nucleus, rec2.coda, rec2.tone):
            bad.append((w, spelling, "record lệch"))
    check("render hai chiều từ thật (gồm họ gi — V5-02)", not bad, f"vd {bad[:3]}")


# ---------------------------------------------------------------- F. spell + word
def test_spell_and_word():
    sp = R.load_spell()
    check("spell seed ≥ 20 chữ", len(sp) >= 20, f"n={len(sp)}")
    for letter, syls in sp.items():
        for s in syls:
            try:
                parse(s)
                ok = True
            except ParseError:
                ok = False
            check(f"spell {letter} → {s!r} parse được", ok)
    w = parse_word("tôi đi học")
    check("parse_word 3 token", [t for t, _ in w] == ["tôi", "đi", "học"])
    check("tôi record OK", w[0][1] is not None and w[2][1] is not None)
    w2 = parse_word(" Flickr 2019 ")
    check("token không parse → None (spell path)", w2[0][1] is None)


def test_static_inventory():
    rows = inventory.load()
    errs, _ = inventory.audit(rows)
    static = [e for e in errs if not e.startswith("[7]")]
    check("audit static (điều 1-6) PASS", not static, str(static[:2]))


if __name__ == "__main__":
    # V5-03: tự kiểm tên test trùng — Python ghi đè định nghĩa sau lên định nghĩa
    # trước âm thầm (lỗi tổ chức test đã tái hiện ở vòng 5: hai test_matcher_negative).
    import ast as _ast
    _tree = _ast.parse(Path(__file__).read_text(encoding="utf-8"))
    _names = [n.name for n in _tree.body
              if isinstance(n, _ast.FunctionDef) and n.name.startswith("test_")]
    _dups = sorted({n for n in _names if _names.count(n) > 1})
    if _dups:
        print(f"  FAIL: tên test trùng (bản sau ghi đè bản trước): {_dups}")
        sys.exit(1)
    _ROWS = inventory.load()
    inventory.load_cached = lambda: _ROWS
    for t in (test_contrasts, test_merges, test_proposed_rules,
              test_matcher_negative_probes, test_real_words, test_roundtrip,
              test_matcher_negative, test_public_parser_contract, test_core_domain,
              test_compute_status, test_core_domain_attestation,
              test_builder_literal_counting, test_domain_hash_covers_classifier,
              test_reviewer_iy_fixtures, test_qd57_scope_exclusions,
              test_qd57_boundary_exact,
              test_trace_locator_original_index,
              test_exact_fixture_approval_scope,
              test_approval_fingerprint_and_profile_loss,
              test_renderer_roundtrip, test_unresolved,
              test_spell_and_word, test_static_inventory):
        t()
    print(f"vi_rules/vi_syllable: {_PASS} PASS, {_FAIL} FAIL")
    sys.exit(1 if _FAIL else 0)
