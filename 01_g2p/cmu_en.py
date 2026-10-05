# -*- coding: utf-8 -*-
"""cmu_en.py — nhánh en fase C: CMUdict pin → record EnSyllable (master ham/0.2).

NGUỒN: `03_vendor/cmudict/cmudict.dict` — pin bằng sha256 + commit trong
`cmudict_provenance.json` (BSD-2; cmusphinx kế thừa CMUdict 0.7b, phoneset
ARPAbet US). Loader KIỂM TRA sha256 lúc nạp — lệch pin → SystemExit (fail-closed,
không âm thầm dùng bản khác).

ĐÚNG SHAPE: mỗi từ → list[EnSyllable] (profiles.EnSyllable — onset/nucleus/coda
master ID, stress STRESS_PRIMARY/SECONDARY/""). Stress là PROSODY gắn nucleus
(4.7.2). Đây là LỚP LEXICON — không quyết route, không đụng tầng 1, không đọc
câu (g2p.py tổng hợp là fase D).

PHẠM VI (hợp đồng fase C — cùng ranh giới QD57 §5):
  - tra từ nguyên dạng (lowercase exact) trong dict — KHÔNG tự phục hồi dấu/cách
    viết, KHÔNG suy rộng lemma/hình thái nếu dict không có;
  - OOV → spell theo policy đã chốt "đọc được thì đọc, không chắc mới spell":
    TỪNG CHỮ CÁI a-z đọc tên chữ (bảng LETTER_NAMES pin — quy ước, chờ duyệt
    cùng anh như spell_vi seed); ký tự khác (chữ số, dấu) KHÔNG tên → liệt kê
    có cấu trúc, caller fase D quyết (không âm thầm bỏ);
  - mục từ dict KHÔNG có nucleus nguyên âm (hmm, psst, shh…) → status
    "no_nucleus" có cấu trúc — KHÔNG bịa nucleus.

SYLLABIFICATION (maxonset_v1 — heuristic debug cho record; chuỗi master phẳng
KHÔNG đổi theo cách cắt): nguyên âm mở âm tiết mới; phụ âm đơn giữa 2 nguyên âm
→ onset của âm tiết SAU (maximal onset); run ≥2 → phụ âm ĐẦU vào coda âm tiết
TRƯỚC, phần còn lại vào onset sau; run sau nguyên âm cuối → coda; run trước
nguyên âm đầu → onset. Không có bảng cluster — cắt máy móc, ghi rõ ở đây.

FINGERPRINT (bài học R14-02): `en_policy_hash` = sha256 JSON{cmudict_sha,
arpabet_map, letter_names, syllabify_rule, code_sha256} — đổi bảng map, bảng
tên chữ, luật cắt hay code module → hash đổi; khôi phục → về baseline.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inventory  # noqa: E402
from profiles import EnSyllable  # noqa: E402

CMU_DIR = HERE.parent / "03_vendor" / "cmudict"
CMU_DICT = CMU_DIR / "cmudict.dict"
CMU_PROVENANCE = CMU_DIR / "cmudict_provenance.json"

SYLLABIFY_RULE = "maxonset_v1"

# ---------------------------------------------------------------- bảng ARPABET → master
# Nguyên âm: key = ký hiệu KHÔNG stress; AH và ER phân theo stress (A3: ER0→ɚ,
# ER1/2→ɝ — quyết vòng 3; AH0→ə SCHWA, AH1/2→ʌ — required_contrast với SCHWA).
VOWEL_MAP = {
    "AA": "PHONE_AA",
    "AE": "PHONE_AE",
    "AO": "PHONE_OPEN_O",
    "AW": "PHONE_AU",
    "AY": "PHONE_AI",
    "EH": "PHONE_OPEN_E",
    "EY": "PHONE_EY",
    "IH": "PHONE_IH",
    "IY": "PHONE_I",
    "OW": "PHONE_OW",
    "OY": "PHONE_OY",
    "UH": "PHONE_UH",
    "UW": "PHONE_U",
    # AH/ER xử riêng trong _nucleus() vì phụ thuộc stress digit
}
STRESS_MAP = {"0": "", "1": "STRESS_PRIMARY", "2": "STRESS_SECONDARY"}

CONSONANT_MAP = {
    "B": "PHONE_B",
    "CH": "PHONE_TSH",
    "D": "PHONE_D",
    "DH": "PHONE_DH",
    "F": "PHONE_F",
    "G": "PHONE_G_HARD",
    "HH": "PHONE_H",
    "JH": "PHONE_DZH",
    "K": "PHONE_K",
    "L": "PHONE_L",
    "M": "PHONE_M",
    "N": "PHONE_N",
    "NG": "PHONE_NG",
    "P": "PHONE_P",
    "R": "PHONE_R",
    "S": "PHONE_S",
    "SH": "PHONE_SH",
    "T": "PHONE_T",
    "TH": "PHONE_THETA",
    "V": "PHONE_V",
    "W": "PHONE_W",
    "Y": "PHONE_J",
    "Z": "PHONE_Z",
    "ZH": "PHONE_ZH",
}

# Tên chữ cái a-z (US convention) — pin literal tại đây, nguồn quy ước chứ không
# phải dữ liệu train; qua đúng bảng ARPABET→master phía trên (không đường tắt).
LETTER_NAMES = {
    "a": ("EY1",),            "b": ("B", "IY1"),        "c": ("S", "IY1"),
    "d": ("D", "IY1"),        "e": ("IY1",),            "f": ("EH1", "F"),
    "g": ("JH", "IY1"),       "h": ("EY1", "CH"),       "i": ("AY1",),
    "j": ("JH", "EY1"),       "k": ("K", "EY1"),        "l": ("EH1", "L"),
    "m": ("EH1", "M"),        "n": ("EH1", "N"),        "o": ("OW1",),
    "p": ("P", "IY1"),        "q": ("K", "Y", "UW1"),   "r": ("AA1", "R"),
    "s": ("EH1", "S"),        "t": ("T", "IY1"),        "u": ("Y", "UW1"),
    "v": ("V", "IY1"),        "w": ("D", "AH1", "B", "AH0", "L", "Y", "UW1"),
    "x": ("EH1", "K", "S"),   "y": ("W", "AY1"),        "z": ("Z", "IY1"),
}

_VOWEL_RE = re.compile(r"^(AA|AE|AH|AO|AW|AY|EH|ER|EY|IH|IY|OW|OY|UH|UW)([012])$")


def _nucleus(base, stress_digit):
    """(ký hiệu nguyên âm, digit) → master ID nucleus (AH/ER phân theo stress)."""
    if base == "AH":
        return "PHONE_SCHWA" if stress_digit == "0" else "PHONE_AH"
    if base == "ER":
        return "PHONE_ER" if stress_digit == "0" else "PHONE_ER_STRESS"
    return VOWEL_MAP[base]


def _cmudict_sha():
    return hashlib.sha256(CMU_DICT.read_bytes()).hexdigest()


def verify_pin():
    """sha256 dict + LICENSE phải khớp cmudict_provenance.json — lệch → SystemExit."""
    prov = json.loads(CMU_PROVENANCE.read_text(encoding="utf-8"))
    errs = []
    if _cmudict_sha() != prov["sha256"]:
        errs.append(f"sha256 cmudict.dict lệch pin: {_cmudict_sha()[:12]}… ≠ "
                    f"{prov['sha256'][:12]}…")
    lic = CMU_DIR / "LICENSE"
    if hashlib.sha256(lic.read_bytes()).hexdigest() != prov["license_sha256"]:
        errs.append("sha256 LICENSE lệch pin")
    if errs:
        raise SystemExit("cmu_en: " + "; ".join(errs))
    return prov


def load_cmu():
    """Dict pin → {key_lower: (phones_tuple, …)} — giữ thứ tự biến thể (mặc định = đầu).

    Định dạng dòng: `key PH0 PH1 …` (có thể kèm chú thích sau '#');
    biến thể `key(2)`; dòng ';;;' là comment. Key đã lowercase (dict gốc lower).
    """
    verify_pin()
    d = {}
    with CMU_DICT.open(encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith(";;;"):
                continue
            if "#" in ln:
                ln = ln[: ln.index("#")].strip()
            parts = ln.split()
            if len(parts) < 2:
                continue
            key = parts[0].lower()
            m = re.match(r"^(.*?)\((\d+)\)$", key)
            if m:
                key = m.group(1)
            d.setdefault(key, []).append(tuple(parts[1:]))
    return {k: tuple(v) for k, v in d.items()}


def syllabify(phones):
    """chuỗi phone ARPABET → list[(onset_ids, nucleus_id, coda_ids, stress)].

    maxonset_v1 — xem docstring. Ném ValueError nếu không có nguyên âm.
    """
    units = []          # mỗi nguyên âm: {"onset": [ids], "nuc": id, "stress": str}
    pending = []        # phụ âm đang chờ (ids)
    for p in phones:
        m = _VOWEL_RE.match(p)
        if m:
            base, dig = m.group(1), m.group(2)
            if units:
                # phụ âm giữa 2 nguyên âm: 1 → onset sau; ≥2 → đầu vào coda trước
                if len(pending) >= 2:
                    units[-1]["coda"].append(pending[0])
                    pending = pending[1:]
            units.append({"onset": list(pending), "nuc": _nucleus(base, dig),
                          "stress": STRESS_MAP[dig], "coda": []})
            pending = []
        else:
            mid = CONSONANT_MAP.get(p)
            if mid is None:
                raise ValueError(f"ký hiệu ARPABET lạ: {p!r}")
            pending.append(mid)
    if not units:
        raise ValueError("không có nguyên âm (no_nucleus)")
    units[-1]["coda"].extend(pending)   # phụ âm cuối từ → coda âm tiết cuối
    return [(tuple(u["onset"]), u["nuc"], tuple(u["coda"]), u["stress"])
            for u in units]


class EnWordResult:
    """Kết quả có cấu trúc cho 1 token en — fase D tiêu thụ, không đoán hộ."""

    __slots__ = ("status", "word", "syllables", "spell_syllables",
                 "unsupported_chars", "reason")

    def __init__(self, status, word, syllables=(), spell_syllables=(),
                 unsupported_chars=(), reason=""):
        self.status = status              # ok | spell | no_nucleus
        self.word = word
        self.syllables = tuple(syllables)
        self.spell_syllables = tuple(spell_syllables)  # list[list[EnSyllable]] theo chữ
        self.unsupported_chars = tuple(unsupported_chars)
        self.reason = reason

    def __repr__(self):
        return (f"EnWordResult({self.status!r}, {self.word!r}, "
                f"n_syl={len(self.syllables)}, n_spell={len(self.spell_syllables)}, "
                f"unsupported={self.unsupported_chars!r})")


def pronounce(word, cmu=None):
    """Token en nguyên dạng → EnWordResult theo policy fase C.

    - có trong dict & có nguyên âm → status "ok";
    - có trong dict nhưng không nguyên âm (hmm/psst…) → "no_nucleus" (không bịa);
    - OOV → "spell": mỗi chữ a-z → tên chữ (EnSyllable riêng); ký tự khác được
      LIỆT KÊ trong unsupported_chars (không âm thầm bỏ).
    """
    cmu = cmu if cmu is not None else load_cmu()
    w = word.strip().lower()
    entries = cmu.get(w)
    if entries:
        try:
            recs = [EnSyllable(onset=on, nucleus=nuc, coda=co, stress=st,
                               source_graphemes=word, stress_state="resolved")
                    for on, nuc, co, st in syllabify(entries[0])]
            return EnWordResult("ok", word, syllables=recs)
        except ValueError as e:
            return EnWordResult("no_nucleus", word, reason=str(e))
    # OOV → spell
    spell, unsupported = [], []
    for ch in w:
        if ch in LETTER_NAMES:
            try:
                recs = [EnSyllable(onset=on, nucleus=nuc, coda=co, stress=st,
                                   source_graphemes=ch, stress_state="resolved")
                        for on, nuc, co, st in syllabify(LETTER_NAMES[ch])]
            except ValueError:
                unsupported.append(ch)
                continue
            spell.append(recs)
        else:
            unsupported.append(ch)
    reason = ("OOV cmu — spell tên chữ; " if spell else "OOV cmu — ") + (
        f"ký tự không có tên: {list(dict.fromkeys(unsupported))}"
        if unsupported else "đủ chữ a-z")
    return EnWordResult("spell", word, spell_syllables=spell,
                        unsupported_chars=tuple(unsupported), reason=reason)


def flat_ids(result):
    """EnWordResult → chuỗi master ID phẳng (ok: các âm tiết; spell: theo chữ)."""
    out = []
    if result.status == "ok":
        for s in result.syllables:
            out.extend(s.onset)
            out.append(s.nucleus)
            out.extend(s.coda)
    elif result.status == "spell":
        for grp in result.spell_syllables:
            for s in grp:
                out.extend(s.onset)
                out.append(s.nucleus)
                out.extend(s.coda)
    return tuple(out)


def en_policy_hash():
    """Fingerprint policy en (R14-02 discipline): dữ liệu pin + bảng + luật + code."""
    parts = {
        "cmudict_sha256": _cmudict_sha(),
        "arpabet_map": {"vowels": dict(sorted(VOWEL_MAP.items())),
                        "consonants": dict(sorted(CONSONANT_MAP.items())),
                        "ah_stress": {"0": "PHONE_SCHWA", "1-2": "PHONE_AH"},
                        "er_stress": {"0": "PHONE_ER", "1-2": "PHONE_ER_STRESS"},
                        "stress_digits": dict(sorted(STRESS_MAP.items()))},
        "letter_names": dict(sorted(LETTER_NAMES.items())),
        "syllabify_rule": SYLLABIFY_RULE,
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    blob = json.dumps(parts, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def selfcheck(cmu=None):
    """Mọi ký hiệu ARPABET trong dict phải có đường map; tên chữ phải map được.

    Trả list lỗi (rỗng = PASS) — chạy trong coverage + test; mutation bảng map
    phải làm cái này đỏ + en_policy_hash đổi (probe R14-02-style).
    """
    cmu = cmu if cmu is not None else load_cmu()
    errs = []
    seen = set()
    for variants in cmu.values():
        for phones in variants:
            for p in phones:
                seen.add(p)
    for p in sorted(seen):
        m = _VOWEL_RE.match(p)
        if m:
            try:
                _nucleus(m.group(1), m.group(2))
            except KeyError:
                errs.append(f"nguyên âm không map: {p}")
        elif p not in CONSONANT_MAP:
            errs.append(f"phụ âm không map: {p}")
    by_id = {r["id"] for r in inventory.load()}
    for letter, phones in sorted(LETTER_NAMES.items()):
        try:
            for on, nuc, co, _st in syllabify(phones):
                for mid in on + co + (nuc,):
                    if mid not in by_id:
                        errs.append(f"tên chữ {letter!r}: ID lạ {mid}")
        except (ValueError, KeyError) as e:
            errs.append(f"tên chữ {letter!r}: {e}")
    return errs
