# -*- coding: utf-8 -*-
"""vi_rules.py — bảng luật chữ → master ID cho tiếng Việt (fase B, đặc tả 4.6).

Bảng nguồn: A0/a3 (đã [V] pin với frontend gốc trên 2.547 âm tiết thật, 100% mũi tên)
+ vá 3 lỗ phát hiện khi rà lại:
  - vần "uya" mở (khuya) và "ue" (Huế) — a3 parse hụt;
  - iê/yê/uô/ươ bắt buộc có coda (bare = ia/ya/ua/ưa) — nếu không sẽ sinh nhóm
    collision giả {"kia","kiê"} thay vì chặn chính tả không tồn tại;
  - dấu hỏi = U+0309 (a3 dùng \u0302 để render — chỉ đúng cho so-mũi-tên, KHÔNG
    đúng roundtrip chính tả).

Cell [B] (chỉ CHẤT phiên âm chi tiết — việc bảo toàn đối lập KHÔNG là [B]):
  - nguyên âm "ach" → PHONE_OPEN_E_PREVELAR (ham/0.2 — ràng buộc giữ đối
    lập 10 cặp ach/ec: quyết reviewer v11 §4; encoding: lựa chọn tác giả v12 — sách/Séc, mách/méc có
    đối chiếu mục từ độc lập, 8 cặp còn lại là policy bảo toàn lớp vần; trước
    đây là PHONE_OPEN_E /ɛk/ đề xuất chưa duyệt — đã bị bác cùng MR-ACH-EC);
    chất IPA chi tiết (mức prevelar [k̟]…) vẫn chờ E6;
  - "anh" → PHONE_A_LONG + PHONE_NH (phân tích /ɛŋ/ như ach sẽ cân nhắc cùng gold —
    đối lập an≠anh được bảo toàn ở cả hai phân tích);
  - coda "nh" sau nguyên âm sau → PHONE_NH (mặc định), dù thực phát [ŋ];
  - "qu" + ô (quốc) → K,W,PHONE_O theo convention frontend gốc, dù mô tả chuẩn
    đọc [kuək] (U_SCHWA) — chờ E6 nghe thử.
KHÔNG còn mở: "uâ" (glide w + â, vd suất) vs "uô/ua" (U_SCHWA, vd suốt) —
KHÁC nhau theo giọng đích (duyệt 02/10/2026): suất ≠ suốt, không gộp.
Vá 02/10/2026: "khoét" có É (vần oet) — vá W_OK["Ê"] thêm "t" ngày 01/10 là SAI
BẢNG, đã revert.

Vá vòng 4 (02/10/2026, theo báo cáo kiểm code của reviewer — F01/F02/F03/F07):
  - F01 "uy" là COMPOSITE (glide w + i): tuy = T+W+I, KHÔNG phải u+y coda → tui ≠ tuy.
    Ưu tiên nhánh glide khi vần bắt đầu "uy" (chỉ riêng tổ hợp này — KHÔNG đảo thứ tự
    toàn bảng). "ui" vẫn là u + coda j (tui, múi, đui).
  - F02 onset "gi" → PHONE_GI (ID riêng, dialect policy gộp gi/d áp ở tầng dialect,
    KHÔNG dùng PHONE_GH). Chữ i của "gi": thuộc onset khi theo nguyên âm thường
    (gia = GI+a, giọng = GI+o), là NGUYÊN ÂM khi đứng một mình (gì = GI+i) hoặc khi
    "gi" + ê (thành phần của vần iê: giêng/giết = GI + I_SCHWA — phục hồi nguyên âm đôi).
  - F03 NUC_OK["Uə"] thêm coda m (buồm, muỗm); W_OK["I"] thêm w (khuỷu = uy + offglide u).
  - F07 B_QU_O sửa thành ("qu","ô") — cờ [B] gắn đúng ca quốc (quọt là o thường, không cờ).

File này là NGUỒN SỰ THẬT mới; a3 giữ bản sao riêng để pin [V] (không sửa a3).
"""
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inventory  # noqa: E402

# ---------------------------------------------------------------- thanh điệu
# bảng nguồn a0: hỏi = hook above (U+0309), ngã = tilde, nặng = dot below
_TONE_CHARS = {}
for _base, _marks in {
    "a": "àáảãạ", "ă": "ằắẳẵặ", "â": "ầấẩẫậ", "e": "èéẻẽẹ", "ê": "ềếểễệ",
    "i": "ìíỉĩị", "o": "òóỏõọ", "ô": "ồốổỗộ", "ơ": "ờớởỡợ", "u": "ùúủũụ",
    "ư": "ừứửữự", "y": "ỳýỷỹỵ",
}.items():
    for _ti, _m in enumerate(_marks):
        _TONE_CHARS[_m] = (_base, _ti + 2)      # 2=huyền 3=sắc 4=hỏi 5=ngã 6=nặng

TONE_BY_INDEX = {1: "TONE_NGANG", 2: "TONE_HUYEN", 3: "TONE_SAC", 4: "TONE_HOI",
                 5: "TONE_NGA", 6: "TONE_NANG"}
TONE_MARK = {"TONE_NGANG": "", "TONE_HUYEN": "\u0300", "TONE_SAC": "\u0301",
             "TONE_HOI": "\u0309", "TONE_NGA": "\u0303", "TONE_NANG": "\u0323"}

_TUC = {"p", "t", "k"}          # coda tắc (p/t/k từ c,ch,k) → chỉ sắc/nặng


def strip_tone(s):
    """→ (skeleton giữ ăâêôơưđ, tone_index) hoặc (None, None) nếu >1 dấu thanh."""
    tone = 1
    out = []
    for ch in unicodedata.normalize("NFC", s):
        if ch in _TONE_CHARS:
            if tone != 1:
                return None, None
            b, t = _TONE_CHARS[ch]
            tone = t
            out.append(b)
        elif ch == "đ" or ch == "Đ":
            out.append("đ")
        else:
            out.append(ch)
    return "".join(out), tone


# ---------------------------------------------------------------- bảng vần
ONSETS = ["ngh", "ch", "gh", "gi", "kh", "ng", "nh", "ph", "qu", "th", "tr",
          "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s",
          "t", "v", "x", ""]

FORMS = ["iê", "yê", "ia", "ya", "ươ", "ưa", "uô", "ua",
         "a", "ă", "â", "e", "ê", "i", "y", "o", "ô", "ơ", "u", "ư"]

# bare syllable: iê/yê/uô/ươ luôn có coda; ia/ya/ưa/ua chỉ viết KHÔng coda
# (có coda → iê/yê/ươ/uâ-glide/uô). "ua"+coda không chính tả ("xuất" là uâ glide).
FORM_REQUIRES_TAIL = {"iê", "yê", "uô", "ươ"}
FORM_BARE_ONLY = {"ia", "ya", "ưa", "ua"}

# (form) → nucleus class (như A0)
NUC_ID = {"iê": "Iə", "yê": "Iə", "ia": "Iə", "ya": "Iə",
          "ươ": "Ưə", "ưa": "Ưə", "uô": "Uə", "ua": "Uə",
          "a": "A", "ă": "Ă", "â": "Â", "e": "E", "ê": "Ê", "i": "I", "y": "I",
          "o": "O", "ô": "Ô", "ơ": "Ơ", "u": "U", "ư": "Ư"}

# coda hợp lệ theo nucleus: G = ∅
NUC_OK = {
    "A":  {"", "j", "w", "m", "n", "ŋ", "ɲ", "k", "t", "p"},
    "Ă":  {"", "m", "n", "ŋ", "k", "t", "p"},
    "Â":  {"", "j", "w", "m", "n", "ŋ", "k", "t", "p"},
    "E":  {"", "w", "m", "n", "ŋ", "k", "t", "p"},
    "Ê":  {"", "w", "m", "n", "ɲ", "k", "t", "p"},
    "I":  {"", "w", "m", "n", "ɲ", "k", "t", "p"},
    "O":  {"", "j", "m", "n", "ŋ", "k", "t", "p"},
    "Ô":  {"", "j", "m", "n", "ŋ", "k", "t", "p"},
    "Ơ":  {"", "j", "m", "n", "k", "t", "p"},
    "U":  {"", "j", "m", "n", "ŋ", "k", "t", "p"},
    "Ư":  {"", "j", "w", "m", "n", "ŋ", "k", "t", "p"},
    "Iə": {"", "w", "m", "n", "ŋ", "ɲ", "k", "t", "p"},
    "Ưə": {"", "j", "w", "m", "n", "ŋ", "k", "t", "p"},
    "Uə": {"", "j", "m", "n", "ŋ", "k", "t", "p"},   # +m (F03): buồm, muỗm
}

# G = w (glide o/u TRƯỚC nguyên âm; qu tiêu thụ w) — vá: Iə thêm "" cho "uya"
W_OK = {
    "A":  {"", "j", "w", "n", "ŋ", "ɲ", "k", "t"},
    "Ă":  {"n", "ŋ", "k", "t"},
    "Â":  {"", "j", "n", "t"},
    "E":  {"", "n", "t"},
    "Ê":  {"", "n", "k"},   # "khoét" là É (oet), không phải ê — đã revert vá sai 01/10
    "I":  {"", "w", "ɲ", "t", "p"},   # +w (F03): khuỷu = uy (glide w+i) + offglide u
    "Ô":  {"j", "n", "ŋ", "k", "t", "p"},
    "Ơ":  {"", "j", "w"},
    "Ư":  {""},
    "Iə": {"", "n", "t"},
    "O":  {"j", "m", "n", "ŋ", "k", "t", "p"},
}

# tail chính tả → coda rút gọn
CODA_MAP = {"": "", "i": "j", "y": "j", "o": "w", "u": "w", "m": "m", "n": "n",
            "p": "p", "t": "t", "k": "k", "ng": "ŋ", "nh": "ɲ", "c": "k", "ch": "k"}

# ---------------------------------------------------------------- chữ → master ID
ONSET_ID = {"b": ("PHONE_B_IMP",), "c": ("PHONE_K",), "k": ("PHONE_K",),
            "ch": ("PHONE_C",), "d": ("PHONE_Z",), "đ": ("PHONE_D_IMP",),
            "g": ("PHONE_GH",), "gh": ("PHONE_GH",), "gi": ("PHONE_GI",),
            "h": ("PHONE_H",), "kh": ("PHONE_KH",), "l": ("PHONE_L",),
            "m": ("PHONE_M",), "n": ("PHONE_N",), "nh": ("PHONE_NH",),
            "ng": ("PHONE_NG",), "ngh": ("PHONE_NG",), "ph": ("PHONE_F",),
            "p": ("PHONE_P",), "r": ("PHONE_R_VI",), "s": ("PHONE_S_RETRO",),
            "t": ("PHONE_T",), "th": ("PHONE_TH",), "tr": ("PHONE_TR",),
            "v": ("PHONE_V",), "x": ("PHONE_S",), "qu": ("PHONE_K",), "": ()}

TAIL_ID = {"": None, "i": "PHONE_J", "y": "PHONE_J", "o": "PHONE_W", "u": "PHONE_W",
           "m": "PHONE_M", "n": "PHONE_N", "ng": "PHONE_NG", "nh": "PHONE_NH",
           "c": "PHONE_K", "ch": "PHONE_K", "k": "PHONE_K", "p": "PHONE_P",
           "t": "PHONE_T"}

BASE_NUC = {"a": "PHONE_A_LONG", "ă": "PHONE_A_SHORT", "â": "PHONE_SCHWA",
            "e": "PHONE_OPEN_E", "ê": "PHONE_E", "i": "PHONE_I", "y": "PHONE_I",
            "o": "PHONE_OPEN_O", "ô": "PHONE_O", "ơ": "PHONE_SCHWA_LONG",
            "u": "PHONE_U", "ư": "PHONE_UHORN", "iê": "PHONE_I_SCHWA",
            "yê": "PHONE_I_SCHWA", "ia": "PHONE_I_SCHWA", "ya": "PHONE_I_SCHWA",
            "ươ": "PHONE_UHORN_SCHWA", "ưa": "PHONE_UHORN_SCHWA",
            "uô": "PHONE_U_SCHWA", "ua": "PHONE_U_SCHWA"}

# vần điều kiện (đối chứng tai/tay, cao/cau); cell [B] gắn cờ ở B_CELLS
# "ach" → PHONE_OPEN_E_PREVELAR (ham/0.2): ràng buộc giữ đối lập 10 cặp
# ach/ec từ quyết reviewer v11; encoding ở nucleus là lựa chọn tác giả v12 (sách/Séc có đối chiếu mục từ [sajk̟̚] vs
# [sɛk̚]); trước đây là PHONE_OPEN_E (đề xuất /ɛk/ chưa duyệt — đã bị bác cùng
# MR-ACH-EC, rút khỏi catalog).
COND_NUC = {("a", "y"): "PHONE_A_SHORT",    # ay = aj (ngắn)
            ("a", "u"): "PHONE_A_SHORT",    # au = aw (ngắn)
            ("a", "ch"): "PHONE_OPEN_E_PREVELAR"}   # ach = ɛ-prevelar + k (ham/0.2)

# cell [B]: chỉ CHẤT phiên âm chi tiết, không phải việc bảo toàn đối lập
B_CELLS = {("a", "nh"), ("a", "ch"), ("e", "nh"), ("i", "nh"), ("o", "nh"),
           ("ô", "nh"), ("u", "nh"), ("ư", "nh"), ("ơ", "nh"), ("â", "nh"),
           ("ă", "nh")}
# "qu" + ô → convention frontend ([kwok]) khác mô tả chuẩn [kuək] — [B] riêng
# (F07: key theo FORM sau parse — quốc có form "ô"; quọt là o thường, KHÔNG cờ)
B_QU_O = ("qu", "ô")

# composite (glide_letter + form) → (glide ID, nucleus ID) — vá: thêm "ue", "uya" có sẵn
GLIDE_FORMS = {"oa": ("PHONE_W", "PHONE_A_LONG"), "oă": ("PHONE_W", "PHONE_A_SHORT"),
               "oê": ("PHONE_W", "PHONE_E"), "oe": ("PHONE_W", "PHONE_OPEN_E"),
               "uâ": ("PHONE_W", "PHONE_SCHWA"), "uê": ("PHONE_W", "PHONE_E"),
               "ue": ("PHONE_W", "PHONE_E"), "uơ": ("PHONE_W", "PHONE_SCHWA_LONG"),
               "uy": ("PHONE_W", "PHONE_I"), "uya": ("PHONE_W", "PHONE_I_SCHWA"),
               "uyê": ("PHONE_W", "PHONE_I_SCHWA")}

# composite chỉ hợp lệ KHI CÓ coda ("oê" mở không phải chính tả; "khoét" ✓)
GLIDE_REQUIRES_TAIL = {"oê"}

_GLI = "aăâeêioôơuưy"


def parse_rhyme(rest, wmode):
    """rest sau onset → (form, tail) hoặc None. wmode: glide w đã tiêu thụ."""
    allowed = W_OK if wmode else NUC_OK
    for form in FORMS:
        if not rest.startswith(form):
            continue
        if form in FORM_REQUIRES_TAIL and len(rest) == len(form):
            continue
        if form in FORM_BARE_ONLY and len(rest) > len(form):
            continue
        tail = rest[len(form):]
        if tail not in CODA_MAP:
            continue
        nuc = NUC_ID[form]
        if nuc in allowed and CODA_MAP[tail] in allowed[nuc]:
            return form, tail
    return None


def parse_skeleton(skeleton):
    """skeleton (đã strip tone) → (onset, glide_letter, form, tail) hoặc None.

    glide_letter ∈ {"", "o", "u"}; onset "qu" chứa sẵn glide (glide_letter="").

    F01 (vòng 4): vần bắt đầu "uy" → ƯU TIÊN composite glide (tuy = T+W+I),
    KHÔNG rơi vào u + coda y (tui ≠ tuy). Chỉ tổ hợp "uy" — không đảo thứ tự bảng.
    F02 (vòng 4): onset "gi" → PHONE_GI; chữ i của gi: nguyên âm khi đứng một mình
    (gì), thành phần vần iê khi "gi"+ê (giêng/giết), thuộc onset khi theo nguyên âm
    khác (gia = GI+a, giọng = GI+o).
    """
    for onset in ONSETS:
        if not skeleton.startswith(onset):
            continue
        rest = skeleton[len(onset):]
        if onset == "gi":
            if not rest:
                rhyme = "i"                  # "gì" /zi/ — i là nguyên âm
            elif rest[0] == "ê":
                rhyme = "i" + rest           # gi+ê → vần iê (giêng, giết = /ziə/)
            elif rest[0] == "i" and len(rest) > 1 and rest[1] in _GLI:
                rhyme = rest[1:]             # hiếm: i viết đôi (gi + i…)
            elif rest[0] not in _GLI:
                rhyme = "i" + rest           # i dùng chung: gìn (g,ì,n) = GI+I+N
            else:
                rhyme = rest                 # i thuộc onset: gia = GI+a, giọng = GI+o
            r = parse_rhyme(rhyme, False)
            if r:
                return onset, "", r[0], r[1]
            continue
        if not rest:
            continue
        if onset == "qu":
            if rest[0] not in _GLI:
                continue
            r = parse_rhyme(rest, True)
            if r:
                return onset, "", r[0], r[1]
            continue
        if rest.startswith("uy"):
            # F01: "uy" luôn composite glide w+i — bỏ nhánh trực tiếp (u + coda y)
            r = parse_rhyme(rest[1:], True)
            if r:
                comp = "u" + r[0]
                if comp in GLIDE_REQUIRES_TAIL and not r[1]:
                    r = None
                elif comp not in GLIDE_FORMS:
                    r = None
            if r:
                return onset, "u", r[0], r[1]
            continue                          # không quay lại nhánh u+y (F01)
        r = parse_rhyme(rest, False)
        if r:
            return onset, "", r[0], r[1]
        if rest[0] in "ou" and len(rest) > 1 and rest[1] in _GLI:
            r = parse_rhyme(rest[1:], True)
            if r:
                comp = rest[0] + r[0]
                if comp in GLIDE_REQUIRES_TAIL and not r[1]:
                    continue
                if comp not in GLIDE_FORMS:
                    continue        # composite không khai báo — không phải chính tả
                return onset, rest[0], r[0], r[1]
    return None


def record_parts(onset, glide_letter, form, tail):
    """(onset, glide_letter, form, tail) → (onset_ids, glide_ids, nucleus, coda_id, flags)."""
    flags = set()
    if (form, tail) in B_CELLS:
        flags.add("B:" + form + "+" + (tail or "∅"))
    if onset == "qu":
        if B_QU_O[1] == form:
            flags.add("B:qu+ô")
        nuc = COND_NUC.get((form, tail), BASE_NUC[form])
        return ONSET_ID[onset], ("PHONE_W",), nuc, TAIL_ID[tail], flags
    comp = glide_letter + form
    if glide_letter:
        if comp not in GLIDE_FORMS:
            raise AssertionError(f"composite glide không khai báo: {comp!r}")
        g, nuc = GLIDE_FORMS[comp]
        nuc = COND_NUC.get((form, tail), nuc)
        return ONSET_ID[onset], (g,), nuc, TAIL_ID[tail], flags
    nuc = COND_NUC.get((form, tail), BASE_NUC[form])
    return ONSET_ID[onset], (), nuc, TAIL_ID[tail], flags


# ---------------------------------------------------------------- đặt dấu + render
def place_mark(glide_letter, form, mark):
    """Trả về glide+form có dấu thanh theo luật chính tả.

    glide_letter="o"/"u" cho glide; onset "qu" truyền glide_letter="" (u đã trong onset).
    """
    comp = glide_letter + form
    if not mark:
        return comp
    glen = len(glide_letter)
    if "ơ" in form:                                  # ơ/ươ/uơ → dấu trên ơ
        idx = glen + form.index("ơ")
    elif comp in {"uya", "uyê"}:                     # khuya/khuyên → dấu trên âm cuối/ê
        idx = 2
    elif form in {"ia", "ya", "ua", "ưa"}:           # mía/múa/mưa → dấu trên âm đầu
        idx = glen
    elif len(form) >= 2:                             # iê/yê/uô/êu/ô… → âm thứ hai
        idx = glen + 1
    else:
        idx = glen
    return comp[:idx] + comp[idx] + mark + comp[idx + 1:]


def render_parts(onset, glide_letter, form, tail, tone_id):
    """(phần parse) → chính tả có dấu. Đảo ngược đúng của parse_skeleton+strip_tone.

    V5-02: nhánh gi (F02) trả form "i"/"iê" trong đó chữ i ĐẦU là chữ i DÙNG CHUNG
    với onset "gi" (gìn = g,ì,n; giết = gi+êt) — renderer không được viết lại thành
    "giìn"/"giiết": bỏ chữ i cuối của onset trước khi nối form."""
    mark = TONE_MARK[tone_id]
    if onset == "gi" and form in ("i", "iê") and not glide_letter:
        onset = onset[:-1]
    return onset + place_mark(glide_letter, form, mark) + tail


# ---------------------------------------------------------------- spell vi (seed)
SPELL_TSV = HERE.parent / "02_data" / "spell_vi.tsv"


def load_spell():
    """letter → list âm tiết (seed fase B; fase D ghép vào spell.py tổng)."""
    table = {}
    for ln in SPELL_TSV.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        letter, syls = ln.split("\t")
        table[letter.strip()] = syls.strip().split()
    return table
