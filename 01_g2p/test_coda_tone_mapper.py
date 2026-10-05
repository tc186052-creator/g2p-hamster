# -*- coding: utf-8 -*-
"""test_coda_tone_mapper.py — test KHÓA transform thanh điệu profile kokoro178 (A3, 4.9).

Chạy:  ../venv/bin/python 01_g2p/test_coda_tone_mapper.py
       (hoặc python3 bất kỳ — chỉ dùng stdlib)

Khóa theo đặc tả 4.6.1 + 4.9 (bản vá 5) + [V] 01/10/2026 (kokoro178_tone_pinned.md):
  - ma/mà/má/mả/mã/mạ → 6 chuỗi KHÁC NHAU, arrow đúng vị trí; NGANG không arrow [V]
  - arrow chèn TRƯỚC âm cuối: có coda → trước coda; không coda → sau nucleus
  - ngã/nặng mang ʔ; hỏi = ↓ KHÔNG ʔ
  - sắc/nặng với âm cuối tắc (mác/mạch/mạn/mạt)
  - documented loss (ɓ→b, ɗ→d, ʐ→ʒ, tʰ→θ, ɝ→ɚ) kích hoạt + ghi loss_report
  - I2: determinism + conformance (mọi ký tự thuộc vocab 178) + report toàn segment
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profiles import (  # noqa: E402
    ViSyllable, EnSyllable, transform_vi, transform_en,
    check_conformance, profile_conformance_report,
)

PASS, FAIL = 0, []


def check(name, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(f"{name}: {detail}")


def s(on, nuc, coda=(), tone="TONE_NGANG"):
    return ViSyllable(onset=tuple(on), nucleus=nuc, coda=tuple(coda), tone=tone)


BY = lambda: None  # noqa: E731  (transform tự load)

# ---------- 1) bộ ma × 6 thanh → 6 chuỗi khác nhau, đúng vị trí ----------
MA_NUC = "PHONE_A_LONG"      # "ma" — a mở = aː (4.6.4)
ma_syllables = {
    "TONE_NGANG": "maː",
    "TONE_HUYEN": "maː↘",
    "TONE_SAC":   "maː↗",
    "TONE_HOI":   "maː↓",
    "TONE_NGA":   "maːʔ↗",
    "TONE_NANG":  "maːʔ↓",
}
outs = {}
for tone, expect in ma_syllables.items():
    r = transform_vi(s(("PHONE_M",), MA_NUC, (), tone))
    check(f"ma×{tone} không lỗi", not r.errors, r.errors)
    outs[tone] = r.text
    check(f"ma×{tone} = {expect}", r.text == expect, f"nhận {r.text!r}")
check("6 thanh → 6 chuỗi khác nhau", len(set(outs.values())) == 6, outs)

# ---------- 2) arrow TRƯỚC coda ----------
r = transform_vi(s(("PHONE_M",), "PHONE_A_LONG", ("PHONE_K",), "TONE_SAC"))   # mác
check("mác → maː↗k", r.text == "maː↗k", r.text)
# A3-04: record dưới đây SYNTHETIC (A_SHORT+K+sắc — cấu trúc 'mắc' theo phân tích
# ắ=SẮC), không phải từ 'mạch' (mạch có coda ch → nucleus OPEN_E theo đề xuất ach).
r = transform_vi(s(("PHONE_M",), "PHONE_A_SHORT", ("PHONE_K",), "TONE_SAC"))
check("synthetic A_SHORT+K+sắc → ma↗k", r.text == "ma↗k", r.text)
check("A_SHORT ≠ A_LONG sau transform (đối lập aː/a giữ)", r.text != "maː↗k", r.text)
r = transform_vi(s(("PHONE_M",), "PHONE_A_LONG", ("PHONE_N",), "TONE_NANG"))  # mạn
check("mạn → maːʔ↓n (ʔ↓ trước coda n)", r.text == "maːʔ↓n", r.text)
r = transform_vi(s(("PHONE_M",), "PHONE_A_LONG", ("PHONE_N",), "TONE_SAC"))   # màn→sắc
check("mán → maː↗n", r.text == "maː↗n", r.text)

# ---------- 3) hỏi KHÔNG ʔ; ngã/nặng CÓ ʔ ----------
check("mả không ʔ", "ʔ" not in outs["TONE_HOI"], outs["TONE_HOI"])
check("mã có ʔ", "ʔ" in outs["TONE_NGA"], outs["TONE_NGA"])
check("mạ có ʔ", "ʔ" in outs["TONE_NANG"], outs["TONE_NANG"])
r = transform_vi(s(("PHONE_H",), "PHONE_OPEN_O", (), "TONE_HOI"))   # hỏ
check("hỏ → hɔ↓ (không ʔ)", r.text == "hɔ↓", r.text)

# ---------- 4) documented loss + loss_report ----------
r = transform_vi(s(("PHONE_D_IMP",), "PHONE_I", (), "TONE_NGANG"))  # đi
check("đi → di (ɗ→d; ngang không arrow)", r.text == "di", r.text)
check("loss ghi PHONE_D_IMP", ("PHONE_D_IMP", "ɗ", "d") in r.loss, r.loss)
r = transform_vi(s(("PHONE_TH",), "PHONE_A_LONG", (), "TONE_HUYEN"))  # thà
check("thà → θaː↘ (tʰ→θ; a mở = aː)", r.text == "θaː↘", r.text)
check("loss ghi PHONE_TH", ("PHONE_TH", "tʰ", "θ") in r.loss, r.loss)
r = transform_vi(s(("PHONE_R_VI",), "PHONE_I", (), "TONE_NGANG"))   # ri
check("ri → ʒi (ʐ→ʒ)", r.text == "ʒi", r.text)
check("loss ghi PHONE_R_VI", ("PHONE_R_VI", "ʐ", "ʒ") in r.loss, r.loss)
r = transform_vi(s(("PHONE_B_IMP",), "PHONE_OPEN_O", (), "TONE_HUYEN"))  # bò
check("bò → bɔ↘ (ɓ→b)", r.text == "bɔ↘", r.text)
check("loss ghi PHONE_B_IMP", ("PHONE_B_IMP", "ɓ", "b") in r.loss, r.loss)

# ---------- 5) serialize đa code point + không loss nhầm ----------
r = transform_vi(s(("PHONE_TR",), "PHONE_A_LONG", ("PHONE_J",), "TONE_NGANG"))  # trai
check("trai → ʈʂaːj (ngang không arrow; coda j cuối)", r.text == "ʈʂaːj", r.text)
check("trai không loss", not r.loss, r.loss)
# A3-04: từ thật đi qua PARSER/reference, không tự dựng record rồi gắn nhãn từ
from vi_syllable import parse as vi_parse  # noqa: E402
for w, expect in (("tiếng", "tiə↗ŋ"), ("tiên", "tiən"), ("mắc", "ma↗k"),
                  ("quốc", "kwo↗k")):
    rec = vi_parse(w)
    r = transform_vi(rec)
    check(f"từ thật {w!r} qua parser → {expect}", r.text == expect,
          f"got {r.text!r} errors={r.errors}")
# synthetic cùng cấu trúc (onset N thường — KHÔNG phải từ 'nhiên' thật: nhiên có PHONE_NH)
r = transform_vi(ViSyllable(onset=("PHONE_N",), nucleus="PHONE_I_SCHWA",
                            coda=("PHONE_NG",), tone="TONE_HUYEN"))
check("synthetic N+I_SCHWA+NG → niə↘ŋ", r.text == "niə↘ŋ", r.text)
r = transform_vi(ViSyllable(onset=("PHONE_K", "PHONE_W"),
                            nucleus="PHONE_A_LONG", tone="TONE_NGANG"))  # qua (k+w)
check("qua → kwaː", r.text == "kwaː", r.text)

# ---------- 6) En: ˈ trước nucleus ----------
r = transform_en(EnSyllable(onset=("PHONE_K",), nucleus="PHONE_AE",
                            coda=("PHONE_T",), stress="STRESS_PRIMARY"))  # cat
check("en cat → kˈæt", r.text == "kˈæt", r.text)
r = transform_en(EnSyllable(onset=("PHONE_B",), nucleus="PHONE_SCHWA",
                            coda=(), stress=""))  # a unstressed
check("en unstressed không ˈ", r.text == "bə", r.text)

# ---------- 7) I2: determinism ----------
a1 = transform_vi(s(("PHONE_TR",), "PHONE_A_LONG", ("PHONE_K",), "TONE_NANG"))
a2 = transform_vi(s(("PHONE_TR",), "PHONE_A_LONG", ("PHONE_K",), "TONE_NANG"))
check("I2 determinism (2 lần chạy bằng nhau)",
      (a1.text, a1.sidecar, a1.loss) == (a2.text, a2.sidecar, a2.loss), "")

# ---------- 8) record sai → errors, không crash ----------
r = transform_vi(ViSyllable(onset=(), nucleus="PHONE_KHONGCO", tone="TONE_NGANG"))
check("ID lạ → errors", bool(r.errors) and not r.text, r.errors)
r = transform_vi(ViSyllable(onset=(), nucleus="PHONE_A_LONG", tone="TONE_9"))
check("tone lạ → errors", bool(r.errors), r.errors)
r = transform_vi(ViSyllable(onset=(), nucleus="PHONE_A_LONG", coda=("PHONE_N", "PHONE_M"),
                            tone="TONE_NGANG"))
check("coda 2 segment → errors", bool(r.errors), r.errors)

# ---------- 9) conformance toàn bộ segment ham/0.1 ----------
errs, n_entries = profile_conformance_report()
check(f"conformance toàn segment (vocab {n_entries} mục)", not errs, errs)
for t in outs.values():
    check(f"conformance chuỗi {t!r}", not check_conformance(t), check_conformance(t))
for t in ("maː↗k", "ʈʂaːj", "kˈæt", "maːʔ↓n", "hɔ↓"):
    check(f"conformance chuỗi {t!r}", not check_conformance(t), check_conformance(t))

# ---------- 10) sidecar = ĐƠN VỊ PROFILE THỰC TẾ trong text (A3-02) ----------
for w in ("thà", "bò", "đi", "mác", "trai"):
    rec = vi_parse(w)
    r = transform_vi(rec)
    joined = "".join(s for s, _ in r.sidecar)
    check(f"sidecar {w!r} ghép lại = text", joined == r.text,
          f"text={r.text!r} sidecar={joined!r}")
    # mọi ký tự sidecar thuộc vocab (sidecar là chuỗi profile, không phải master repr)
    check(f"sidecar {w!r} conformance", not check_conformance(joined), joined)
r = transform_vi(s(("PHONE_TH",), "PHONE_A_LONG", (), "TONE_HUYEN"))
check("sidecar θ (sau loss map) cho PHONE_TH", ("θ", "PHONE_TH") in r.sidecar, r.sidecar)
check("loss report vẫn giữ master repr tʰ", ("PHONE_TH", "tʰ", "θ") in r.loss, r.loss)

# ---------- 11) enum state ĐÓNG (A3-03) ----------
by_id = {row["id"]: row for row in __import__("inventory").load()}
r = transform_vi(ViSyllable(onset=("PHONE_M",), nucleus="PHONE_A_LONG",
                            tone="TONE_NGANG", tone_state="unresovled"))  # gõ sai
check("tone_state lạ ('unresovled') → errors", bool(r.errors) and not r.text, r.errors)
v = ViSyllable(onset=("PHONE_M",), nucleus="PHONE_A_LONG",
               tone="TONE_NGANG", tone_state="unresovled")
check("validate tone_state lạ → FAIL", bool(v.validate(by_id)), v.validate(by_id))
e = EnSyllable(onset=("PHONE_B",), nucleus="PHONE_IH", stress_state="unresovled")
check("validate stress_state lạ → FAIL", bool(e.validate(by_id)), e.validate(by_id))
for st in ("diacritic", "policy", "fold"):
    v = ViSyllable(onset=("PHONE_M",), nucleus="PHONE_A_LONG", tone="TONE_HUYEN",
                   tone_state=st)
    check(f"tone_state hợp lệ {st!r} → validate OK", not v.validate(by_id),
          v.validate(by_id))

# ---------- tổng ----------
print(f"kokoro178 tone/coda mapper: {PASS} PASS, {len(FAIL)} FAIL")
for f in FAIL:
    print(f"  FAIL  {f}")
sys.exit(1 if FAIL else 0)
