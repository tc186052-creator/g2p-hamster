#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g2p_v2.py — BẢN G2P v2 (thử nghiệm so sánh với bản cũ, lệnh chủ dự án
05/10): đường vi thua 4 bậc → CỨU TỪNG TỪ theo bậc an toàn, KHÔNG BAO GIỜ
bỏ cả câu. Tiên đề chủ dự án: cấm đọc sai (không bịa phôn vị), mất câu là tệ
nhất, đọc sai là tệ thứ hai ⇒ mọi phôn vị cứu về đều từ NGUỒN CHÍNH THỨC,
ghi provenance đầy đủ.

Bậc cứu cho 1 từ không đọc được (route vi thua / route en OOV):
  1. CMUdict (126k, pin) — phiên âm chính thức US.
  2. espeak-ng en-us (đã cài /usr/bin/espeak-ng) — quy tắc chính tả anh phủ
     MỌI chuỗi chữ latin; IPA → ARPABET → EnSyllable → chuỗi 178.
  3. spell tên chữ (từ ≤4 chữ) — như cơ chế cũ.
  4. hụt → bỏ TỪ đó (không bỏ câu), ghi vào notes để chủ dự án duyệt vá dict.

KHÔNG đụng: g2p.py / vi_rules.py / vi_syllable.py / tầng 1 (đóng băng).
Scope QD57 (từ cấm phát âm) VẪN GIỮ NGUYÊN — không cứu, chỉ bỏ từ + ghi notes.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G2P_DIR = ROOT / "01_g2p"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(G2P_DIR))

from t0.pipeline import normalize as t1_normalize  # noqa: E402
import g2p as G  # noqa: E402
import cmu_en as C  # noqa: E402
from profiles import EnSyllable, transform_en, load_vocab178  # noqa: E402

PUNCT_EMIT = {",", ".", "!", "?", ";", ":"}   # dấu câu giữ lại cho prosody
_ESPEAK_BIN_ENV = "ESPEAK_NG_BIN"
_VOCAB178: set | None = None


def _vocab178() -> set:
    global _VOCAB178
    if _VOCAB178 is None:
        chars, _n = load_vocab178()
        _VOCAB178 = chars
    return _VOCAB178


def _espeak_bin() -> str:
    import shutil
    return os.environ.get(_ESPEAK_BIN_ENV) or shutil.which("espeak-ng") or "espeak-ng"

# ---------------------------------------------------------------- IPA → ARPABET
# Nguồn: espeak-ng voice en-us, --ipa --sep=" " (mỗi phone 1 token, stress ˈ/ˌ
# đằng trước, độ dài ː). Map về ARPABET (phoneset CMUdict) rồi đi đúng đường
# syllabify() của cmu_en — không tự chế phôn vị, chỉ đổi KÝ HIỆU.
_ESPEAK_VOWELS = {
    "aɪ": "AY", "aʊ": "AW", "ɔɪ": "OY", "eɪ": "EY", "oʊ": "OW",
    "ɑ": "AA", "æ": "AE", "ɔ": "AO", "ʌ": "AH", "ə": "AH", "ɐ": "AH",
    "ɛ": "EH", "ɜ": "ER", "ɝ": "ER", "ɪ": "IH", "i": "IY",
    "ʊ": "UH", "u": "UW", "o": "OW", "e": "EY",
    # nguyên âm + r (r-colored): core của token đuôi ɹ/r — ER đã bao h r-color
    "ɪr": "IH", "ir": "IH", "ɛr": "EH", "ɔr": "AO", "ʊr": "UH",
    "ɑr": "AA", "ær": "AE", "ʌr": "AH", "ər": "ER", "ɜr": "ER",
    "aɪr": "AY", "aʊr": "AW", "ɔɪr": "OY", "eɪr": "EY", "oʊr": "OW",
    "ʊə": "UH", "iə": "IH", "eə": "EH", "ɔə": "AO", "ɜː": "ER",
}
_ESPEAK_CONS = {
    "b": "B", "d": "D", "f": "F", "ɡ": "G", "g": "G", "h": "HH",
    "j": "Y", "k": "K", "l": "L", "m": "M", "n": "N", "p": "P",
    "r": "R", "ɹ": "R", "ɾ": "T", "s": "S", "t": "T", "v": "V",
    "w": "W", "z": "Z", "ð": "DH", "θ": "TH", "ŋ": "NG",
    "ʃ": "SH", "ʒ": "ZH", "tʃ": "CH", "dʒ": "JH", "x": "K",
}
# âm tiết phụ l̩ n̩ m̩ → chèn schwa trước để có nucleus (syllabic consonant)
_ESPEAK_SYLLABIC = {"l": "L", "n": "N", "m": "M", "ɹ": "R", "r": "R"}
_SYLLABIC_MARK = "\u0329"

# tách token: ghép đôi có nghĩa trước, lẻ ký tự sau
_ESPEAK_SPLIT = re.compile(r"tʃ|dʒ|aɪr|aʊr|ɔɪr|eɪr|oʊr|aɪ|aʊ|ɔɪ|eɪ|oʊ|.")


def espeak_arpabet(word: str):
    """1 từ anh → list phone ARPABET (stress digit gắn vowel) | None nếu hụt."""
    w = re.sub(r"[^a-zA-Z']", "", word)
    if not w:
        return None
    try:
        r = subprocess.run([_espeak_bin(), "-q", "-v", "en-us", "--ipa",
                            "--sep= ", w], capture_output=True, text=True,
                           timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = r.stdout.strip()
    if not out:
        return None
    # syllabic consonant: l̩ → əl (chèn schwa để có nucleus, CMU cũng vậy)
    out = re.sub(r"([" + "".join(_ESPEAK_SYLLABIC) + r"])\u0329",
                 lambda m: "ə" + m.group(1), out)
    phones, stress_next = [], "0"
    for tok in out.split():
        if "ˈ" in tok:
            stress_next = "1"
        elif "ˌ" in tok:
            stress_next = "2"
        tok = tok.replace("ˈ", "").replace("ˌ", "").replace("ː", "")
        if not tok:
            continue
        for seg in _ESPEAK_SPLIT.findall(tok):
            if seg in _ESPEAK_VOWELS:
                phones.append(_ESPEAK_VOWELS[seg] + stress_next)
                stress_next = "0"
            elif seg.endswith(("ɹ", "r")) and seg[:-1] in _ESPEAK_VOWELS:
                phones.append(_ESPEAK_VOWELS[seg[:-1]] + stress_next)
                if _ESPEAK_VOWELS[seg[:-1]] != "ER":   # ER đã bao h r-color
                    phones.append("R")
                stress_next = "0"
            elif seg in _ESPEAK_CONS:
                phones.append(_ESPEAK_CONS[seg])
            elif seg in _ESPEAK_SYLLABIC:
                phones.extend(["AH0", _ESPEAK_SYLLABIC[seg]])
            # ký hiệu lạ → KHÔNG bỏ im lặng: trả None (fail-closed nguồn này)
            else:
                return None
    return phones or None


def rescue_syllables(word: str):
    """1 từ → (list[EnSyllable], nguồn) | (None, lý do). Bậc 1 CMU → 2 espeak
    → 3 spell tên chữ (≤4 chữ)."""
    w = word.strip().lower()
    # 1) CMUdict — phiên âm chính thức (snapshot đã kiểm pin, cache 1 lần/process)
    res = C.pronounce(w, cmu=G._cmu_snapshot())
    if res.status == "ok":
        return list(res.syllables), "cmu"
    # từ có chữ số → KHÔNG cứu (đọc "seventeen;" là bịa; việc verbalize là
    # của tầng 1) — hụt thì bỏ từ
    if any(ch.isdigit() for ch in w):
        return None, "chữ số"
    # 2) espeak-ng — quy tắc chính tả anh
    phones = espeak_arpabet(w)
    if phones:
        try:
            return [EnSyllable(onset=on, nucleus=nuc, coda=co, stress=st,
                               source_graphemes=word, stress_state="resolved")
                    for on, nuc, co, st in C.syllabify(phones)], "espeak"
        except ValueError:
            pass
    # 3) spell tên chữ — chỉ từ ngắn để người nghe chịu được
    if len(w) <= 4 and all(ch in C.LETTER_NAMES for ch in w):
        syls = []
        for ch in w:
            for on, nuc, co, st in C.syllabify(C.LETTER_NAMES[ch]):
                syls.append(EnSyllable(onset=on, nucleus=nuc, coda=co, stress=st,
                                       source_graphemes=ch,
                                       stress_state="resolved"))
        return syls, "spell"
    return None, "hết bậc cứu"


# khoảng trắng/ký tự ẩn của wiki phá tokenizer tầng 1 (dính từ: "của\xa0New"
# thành 1 token) — chuẩn hóa TRƯỚC khi vào tầng 1; đây là vệ sinh văn bản,
# không phải sửa tầng 1
# soft hyphen NẰM TRONG từ wiki ("n\u00ad\u00adước") ⇒ XÓA (None), không
# đổi thành space — space sẽ xé từ thành hai
_WS_FIX = str.maketrans({"\u00ad": None,
                         **{c: " " for c in
                            "\u00a0\u2007\u202f\u2009\u200a\u2002\u2003"
                            "\u2004\u2005\u2006\u2008\u200b\u200c\u3000"
                            "\u200e\u200f\u000b\u000c"}})


def _unit_profile_text(w, rec, by_id):
    """1 read unit → (profile text, lý do). Đi đúng cơ chế g2p_token nguyên
    bản (scope → parse → fold → spell). Route hụt thì THỬ ROUTE KIA trước
    (quy tắc chủ dự án 05/10: "không chắc thì xem có phải tiếng việt không,
    không thì nó là anh" — và ngược lại). scope QD57 = DỪNG TUYỆT ĐỐI."""
    cat = rec.get("cat") or "word"
    read = rec.get("read") or "word"
    route = rec.get("route") or "vi"

    def attempt(rt):
        # i=0 hợp lệ (i=-1 bị g2p_token coi là contract error và chặn profile)
        tok = {"i": 0, "surface": w, "cat": cat, "route": rt, "read": read,
               "verbal": w}
        g = G.g2p_token(tok)
        if g.status in G.NO_PRONOUNCE:
            return None, g.status
        if g.status == "spell" and not g.read_complete:
            return None, "spell_lửng"
        pd = G._profile_json(g, by_id)
        if pd.get("errors"):
            return None, "profile_err"
        return pd.get("text", ""), g.status

    txt, why = attempt(route)
    if txt and why != "spell":
        return txt, why
    spell_fb = txt if why == "spell" else None   # đánh vần chữ — phương án CUỐI
    if why in ("scope_excluded", "unknown_route"):
        return None, why                     # luật cấm / route hỏng — không lách
    other = "en" if route == "vi" else "vi"
    txt2, why2 = attempt(other)
    if txt2 and why2 != "spell":
        return txt2, why2
    if txt2 and why2 == "spell" and spell_fb is None:
        spell_fb = txt2
    if spell_fb:
        return spell_fb, "spell"             # caller sẽ thử CMU/espeak trước khi dùng
    return None, why


def _rescue_record(rec, by_id, notes):
    """Record → chuỗi profile. Record đọc tốt giữ nguyên profile (giống hệt
    v1). Record hụt: đi từng unit — unit đọc được giữ đọc đúng (tiếng Việt
    KHÔNG BAO GIỜ bị đưa qua espeak — tiên đề chủ dự án), chỉ unit thật sự
    hụt mới cứu theo bậc; hụt hết thì bỏ TỪ, không bỏ câu."""
    st = rec.get("status")
    pd = rec.get("profile_debug") or {}
    if st == "spell" and rec.get("master", {}).get("read_units"):
        fb = (rec["master"]["read_units"][0].get("detail", {})
              .get("fallback_reason") or "")
        if not fb.startswith("oov"):
            return pd.get("text", "") or None
    elif st not in ("unresolved", "no_nucleus"):
        if not pd.get("errors"):
            return pd.get("text", "") or None
    pieces = []
    for u in rec.get("master", {}).get("read_units", []):
        w = (u.get("text") or "").strip()
        if not w:
            continue
        w_c = w.strip(".,;:!?…\"'()")    # dấu câu dính đuôi verbal không thuộc từ
        txt, why = _unit_profile_text(w_c, rec, by_id)
        if txt and why != "spell":
            pieces.append(txt)
            continue
        if txt and why == "spell":
            # v1 đánh vần từng chữ — v2 thử phiên âm thật (CMU/espeak) trước
            syls, src = rescue_syllables(w_c)
            if syls:
                tf_txt, bad = "", False
                for syl in syls:
                    tf = transform_en(syl, by_id)
                    if tf.errors:
                        bad = True
                        break
                    tf_txt += tf.text
                if not bad:
                    notes.append(f"nâng cấp '{w}' từ {src} (v1 đánh vần chữ): {tf_txt}")
                    pieces.append(tf_txt)
                    continue
            pieces.append(txt)               # hụt → giữ đánh vần (tốt hơn câm)
            continue
        if why == "scope_excluded":
            notes.append(f"bỏ từ '{w}' (scope QD57 cấm phát âm — không cứu)")
            continue
        if any(ch.isdigit() for ch in w):
            # chữ số/tổ hợp số là việc verbalize của tầng 1 — cứu là đọc sai
            notes.append(f"bỏ từ '{w}' (chữ số — tầng 1 chưa verbalize)")
            continue
        syls, src = rescue_syllables(w)
        if syls is None:
            notes.append(f"bỏ từ '{w}' ({src}) — câu vẫn đọc tiếp")
            continue
        tf_txt, bad = "", False
        for syl in syls:
            tf = transform_en(syl, by_id)
            if tf.errors:
                bad = True
                break
            tf_txt += tf.text
        if bad:
            notes.append(f"bỏ từ '{w}' (map 178 lỗi) — câu vẫn đọc tiếp")
            continue
        notes.append(f"cứu '{w}' từ {src}: {tf_txt}")
        pieces.append(tf_txt)
    return " ".join(pieces) if pieces else None


def text_to_profile_v2(text: str):
    """Bản v2 — cùng đầu ra (profile, errs) của text_to_profile, kèm notes.

    KHÔNG BAO GIỜ bỏ câu vì từ lạ: từ hở được cứu theo bậc hoặc bị bỏ TỪ,
    câu đọc tiếp. errs chỉ còn lại lỗi hợp đồng thật sự (hiếm).
    """
    by_id = G._by_id()
    ir = t1_normalize(text.translate(_WS_FIX))
    out = G.g2p_stream(ir)
    parts, errs, notes = [], [], []
    if out.get("contract_errors"):
        # lỗi hợp đồng IR (vd read_string lệch dãy do token dính NBSP) — chỉ
        # là kiểm kiểm-chéo của tầng 1, KHÔNG ảnh hưởng phát âm từng token:
        # v2 xử lý per-token, KHÔNG bỏ câu vì nó
        notes.append("IR lệch hợp đồng (" + out["contract_errors"][0][:60]
                     + "…) — xử lý per-token, câu vẫn đọc")
    for rec in out.get("records", []):
        st = rec.get("status")
        surf = rec.get("surface", "")
        if st == "control":
            if surf in PUNCT_EMIT and all(c in _vocab178() for c in surf):
                parts.append(("punct", surf))
            continue
        if st == "not_word":
            notes.append(f"bỏ token deferred '{surf}'")
            continue
        if st == "scope_excluded":
            notes.append(f"bỏ từ '{surf}' (scope QD57 cấm phát âm — không cứu)")
            continue
        if rec.get("contract_errors") or rec.get("validation"):
            errs.append(f"tok[{rec.get('i')}:{surf[:20]}] "
                        f"{(rec.get('validation') or rec.get('contract_errors'))[0]}")
            continue
        txt = _rescue_record(rec, by_id, notes)
        if txt:
            parts.append(("word", txt))
    pieces = []
    for kind, t in parts:
        if not pieces:
            pieces.append(t)
        elif kind == "punct":
            pieces.append(t)
        else:
            pieces.append(" " + t)
    return "".join(pieces), errs, notes


if __name__ == "__main__":
    for line in sys.argv[1:] or ["Đã lo lắng thì cứ thừa nhận, cần gì phải "
                                 "tsundere vòng vo tam quốc thế chứ?"]:
        prof, errs, notes = text_to_profile_v2(line)
        print("PROFILE:", prof)
        print("errs:", errs)
        for n in notes:
            print("  •", n)
