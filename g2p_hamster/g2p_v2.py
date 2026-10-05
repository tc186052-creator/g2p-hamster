#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g2p_v2.py — BẢN G2P v2 (thử nghiệm so sánh với bản cũ, lệnh chủ dự án
05/10): đường vi thua 4 bậc → CỨU TỪNG TỪ theo bậc an toàn, KHÔNG BAO GIỜ
bỏ cả câu. Tiên đề chủ dự án: cấm bịa phôn vị ngoài inventory, mất câu là tệ
nhất, đọc sai là tệ thứ hai ⇒ mọi phôn vị cứu về đều từ NGUỒN CÓ PROVENANCE,
không âm thầm rơi nội dung.

BA THUỘC TÍNH RIÊNG BIỆT (phân biệt tường minh — không trộn):
  1. Không tạo symbol ngoài inventory — đảm bảo bởi mapping + validation 178.
  2. Không mất nội dung mà không báo — đảm bảo bởi state/dropped trong kết quả
     có cấu trúc (text_to_profile_v2_full).
  3. Phát âm đúng — KHÔNG bảo đảm bằng cơ chế; chỉ kết luận được bằng gold đã
     duyệt hoặc đánh giá nghe. `complete` nghĩa ĐỦ COVERAGE, không nghĩa đúng.

Bậc cứu cho 1 từ không đọc được (route vi thua / route en OOV):
  1. CMUdict (126k, pin) — phiên âm tra từ điển.
  2. espeak-ng en-us (rule engine) — SUY DIỄN quy tắc chính tả anh phủ mọi
     chuỗi chữ latin; IPA → ARPABET → EnSyllable → chuỗi 178. Mapping tường
     minh, âm lạ → fail-closed; NHƯNG đây là suy diễn, không phải phiên âm
     chính thức — luôn ghi nguồn "espeak" vào provenance để duyệt.
  3. spell tên chữ (từ ≤4 chữ) — như cơ chế cũ.
  4. hụt → bỏ TỪ đó (không bỏ câu), báo vào `dropped` + notes để chủ duyệt.

KHÔNG đụng: g2p.py / vi_rules.py / vi_syllable.py / tầng 1 (đóng băng).
Scope QD57 (từ cấm phát âm) VẪN GIỮ NGUYÊN — không cứu, chỉ bỏ từ + báo.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from .t0.pipeline import normalize as t1_normalize  # noqa: E402
from .core import g2p as G  # noqa: E402
from .core import cmu_en as C  # noqa: E402
from .core.profiles import EnSyllable, transform_en, load_vocab178  # noqa: E402

PUNCT_EMIT = {",", ".", "!", "?", ";", ":"}   # dấu câu giữ lại cho prosody
_ESPEAK_BIN_ENV = "ESPEAK_NG_BIN"       # đặt thành "" để TẮT hẳn nguồn espeak
_ESPEAK_TIMEOUT_ENV = "ESPEAK_NG_TIMEOUT"   # giây, mặc định 10
_VOCAB178: set | None = None

# strict: nguồn cứu ĐƯỢC CHẤP NHẬN cho dữ liệu train. "core" luôn được (đường
# v1 nguyên bản: ok/fold/spell-acronym). Mặc định nhận CMUdict + spell tên chữ
# (đọc chữ là hành vi đọc thật, v1 có sẵn); espeak là suy diễn quy tắc CHƯA
# được duyệt ⇒ phải opt-in tường minh: strict_policy={"cmu","spell","espeak"}.
DEFAULT_STRICT_POLICY = frozenset({"cmu", "spell"})

# strict: lỗi hợp đồng IR (contract_ok=False) ⇒ TỪ CHỐI câu, TRỪ các loại
# lỗi có trong allowlist này. Allowlist theo TÊN LOẠI (đối chiếu qua bảng
# regex _CONTRACT_KIND_RES bên dưới) — KHÔNG BAO GIỜ miễn toàn bộ
# contract_errors. Mặc định RỖNG: chưa có loại nào được chứng minh an toàn
# (không mất unit). Muốn miễn một loại, phải (1) thêm regex nhận diện loại
# đó vào _CONTRACT_KIND_RES, (2) thêm tên loại vào đây kèm bằng chứng.
STRICT_CONTRACT_ALLOWLIST: frozenset = frozenset()

# tên loại lỗi hợp đồng → regex nhận diện trong thông điệp lỗi của tầng 1.
# Thông điệp lỗi là văn bản tự do — đây là bản ánh xạ DUY NHẤT từ tên loại
# sang thông điệp, nên phải giữ chặt với message của check_contract().
_CONTRACT_KIND_RES = {
    # ví dụ (CHƯA được miễn — chỉ minh họa cách thêm):
    # "i_lech_day": re.compile(r"không liên tiếp"),
}

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

# input espeak CHỈ nhận chữ latin + nháy đơn — ngoài phạm vi thì TỪ CHỐI
# (fail-closed), KHÔNG xóa ký tự âm thầm rồi phát âm một từ khác ("café" ∉
# phạm vi → None, không biến thành "caf")
_ESPEAK_INPUT_RE = re.compile(r"[A-Za-z']+")


def _vocab178() -> set:
    global _VOCAB178
    if _VOCAB178 is None:
        chars, _n = load_vocab178()
        _VOCAB178 = chars
    return _VOCAB178


def _espeak_bin() -> str | None:
    """Đường dẫn espeak-ng. Env đặt thành "" = TẮT hẳn nguồn này (trả None)."""
    b = os.environ.get(_ESPEAK_BIN_ENV)
    if b is not None:
        return b or None
    import shutil
    return shutil.which("espeak-ng") or None


def _espeak_timeout() -> float:
    try:
        return float(os.environ.get(_ESPEAK_TIMEOUT_ENV, "10"))
    except ValueError:
        return 10.0


def espeak_arpabet(word: str):
    """1 từ anh → list phone ARPABET (stress digit gắn vowel) | None nếu hụt.

    Fail-closed: input ngoài [A-Za-z'] bị TỪ CHỐI (không xóa ký tự âm thầm),
    binary thiếu/timeout/returncode≠0/stdout rỗng/âm lạ → None."""
    if not _ESPEAK_INPUT_RE.fullmatch(word):
        return None
    bin_ = _espeak_bin()
    if not bin_:
        return None
    try:
        r = subprocess.run([bin_, "-q", "-v", "en-us", "--ipa",
                            "--sep= ", word], capture_output=True, text=True,
                           timeout=_espeak_timeout())
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
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
    # 1) CMUdict — phiên âm tra từ điển (snapshot đã kiểm pin, cache 1 lần/process)
    res = C.pronounce(w, cmu=G._cmu_snapshot())
    if res.status == "ok":
        return list(res.syllables), "cmu"
    # từ có chữ số → KHÔNG cứu (đọc "seventeen;" là bịa; việc verbalize là
    # của tầng 1) — hụt thì bỏ từ
    if any(ch.isdigit() for ch in w):
        return None, "chữ số"
    # 2) espeak-ng — quy tắc chính tả anh (suy diễn, có provenance)
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
    """Record → (chuỗi profile, trace). Record đọc tốt giữ nguyên profile
    (giống hệt v1, nguồn "core"). Record hụt: đi từng unit — unit đọc được
    giữ đọc đúng (tiếng Việt KHÔNG BAO GIỜ bị đưa qua espeak — tiên đề chủ
    dự án), chỉ unit thật sự hụt mới cứu theo bậc; hụt hết thì bỏ TỪ, không
    bỏ câu. trace: mỗi unit 1 dòng {word, outcome, source, reason}; fast
    path record đọc tốt được MỞ RA thành từng read unit (_fast_trace) — chỉ
    khi không có read_units mới xuất 1 dòng gộp có merged=true + unit_count."""
    trace = []
    st = rec.get("status")
    pd = rec.get("profile_debug") or {}
    if st == "spell" and rec.get("master", {}).get("read_units"):
        fb = (rec["master"]["read_units"][0].get("detail", {})
              .get("fallback_reason") or "")
        # fb từ lõi là "OOV cmu — …" (HOA) — .lower() bắt buộc; thiếu nó làm
        # đường nâng cấp CMU/espeak thành dead code (bug có từ bản gốc)
        if not fb.lower().startswith("oov"):
            return pd.get("text", "") or None, _fast_trace(rec)
    elif st not in ("unresolved", "no_nucleus"):
        if not pd.get("errors"):
            return pd.get("text", "") or None, _fast_trace(rec)
    pieces = []
    for u in rec.get("master", {}).get("read_units", []):
        w = (u.get("text") or "").strip()
        if not w:
            continue
        w_c = w.strip(".,;:!?…\"'()")    # dấu câu dính đuôi verbal không thuộc từ
        txt, why = _unit_profile_text(w_c, rec, by_id)
        if txt and why != "spell":
            pieces.append(txt)
            trace.append({"word": w_c, "outcome": "read", "source": "core",
                          "read_complete": True})
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
                    trace.append({"word": w_c, "outcome": "upgraded",
                                  "source": src, "read_complete": True})
                    continue
            pieces.append(txt)               # hụt → giữ đánh vần (tốt hơn câm)
            trace.append({"word": w_c, "outcome": "read", "source": "core",
                          "read_complete": True})
            continue
        if why == "scope_excluded":
            notes.append(f"bỏ từ '{w}' (scope QD57 cấm phát âm — không cứu)")
            # scope là TỪ NỘI DUNG bị policy cấm — vẫn là mất coverage
            # (best_effort partial / strict rejected), intentional chỉ dành
            # cho icon/biểu tượng không có gì để đọc
            trace.append({"word": w_c, "outcome": "dropped",
                          "reason": "scope QD57 cấm phát âm",
                          "read_complete": False})
            continue
        if any(ch.isdigit() for ch in w):
            # chữ số/tổ hợp số là việc verbalize của tầng 1 — cứu là đọc sai
            notes.append(f"bỏ từ '{w}' (chữ số — tầng 1 chưa verbalize)")
            trace.append({"word": w_c, "outcome": "dropped",
                          "reason": "chữ số — tầng 1 chưa verbalize",
                          "read_complete": False})
            continue
        if not any(ch.isalpha() for ch in w):
            # biểu tượng/emoji — KHÔNG có chữ để đọc, v1 cũng không phát âm
            # (icon/deferred): drop CHỦ Ý, không phải mất nội dung do v2
            notes.append(f"bỏ '{w}' (biểu tượng không phát âm — v1 cũng bỏ)")
            trace.append({"word": w_c, "outcome": "dropped",
                          "reason": "biểu tượng/icon không phát âm",
                          "read_complete": False, "intentional": True})
            continue
        syls, src = rescue_syllables(w)
        if syls is None:
            notes.append(f"bỏ từ '{w}' ({src}) — câu vẫn đọc tiếp")
            trace.append({"word": w_c, "outcome": "dropped", "reason": src,
                          "read_complete": False})
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
            trace.append({"word": w_c, "outcome": "dropped", "reason": "map 178 lỗi",
                          "read_complete": False})
            continue
        notes.append(f"cứu '{w}' từ {src}: {tf_txt}")
        pieces.append(tf_txt)
        trace.append({"word": w_c, "outcome": "read", "source": src,
                      "read_complete": True})
    return (" ".join(pieces) if pieces else None), trace


def _contract_kinds(msgs) -> set:
    """Thông điệp contract error → tập TÊN LOẠI. Loại không nhận diện được
    trả về là 'khác:…' — không bao giờ khớp allowlist ⇒ strict luôn từ chối
    (không có lỗ hổng "lỗi lạ được miễn")."""
    kinds = set()
    for m in msgs:
        for kind, rx in _CONTRACT_KIND_RES.items():
            if rx.search(m):
                kinds.add(kind)
                break
        else:
            kinds.add("khác:" + m[:40])
    return kinds


def _fast_trace(rec) -> list:
    """Fast path record đọc tốt → trace. MỞ RA THÀNH TỪNG read unit theo
    master.read_units — không mạo danh 1 record gộp là trace per-unit; chỉ
    khi record không có read_units mới xuất 1 DÒNG GỘP tường minh có
    "merged": true + "unit_count": N."""
    rus = rec.get("master", {}).get("read_units") or []
    out = []
    for u in rus:
        w = (u.get("text") or "").strip()
        if not w:
            continue
        out.append({"word": w.strip(".,;:!?…\"'()"), "outcome": "read",
                    "source": "core", "read_complete": True})
    if out:
        return out
    return [{"word": rec.get("surface", ""), "outcome": "read",
             "source": "core", "read_complete": True,
             "merged": True, "unit_count": max(1, len(rus))}]


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- provenance
def _espeak_meta() -> dict:
    """Cấu hình espeak hiệu lực: binary, VERSION (probe), voice, options.
    Cache PHỤ THUỘC env — đổi ESPEAK_NG_BIN/ESPEAK_NG_TIMEOUT là probe lại,
    không trả metadata cũ."""
    global _ESPEAK_META, _ESPEAK_META_KEY
    import shutil
    bin_env = os.environ.get(_ESPEAK_BIN_ENV)
    key = (bin_env, os.environ.get(_ESPEAK_TIMEOUT_ENV),
           shutil.which("espeak-ng") if bin_env is None else None)
    if _ESPEAK_META is not None and _ESPEAK_META_KEY == key:
        return _ESPEAK_META
    meta = {"voice": "en-us", "options": ["-q", "--ipa", "--sep= "]}
    bin_ = _espeak_bin()
    if not bin_:
        meta["enabled"] = False
    else:
        meta["enabled"] = True
        meta["binary"] = bin_
        try:
            r = subprocess.run([bin_, "--version"], capture_output=True,
                               text=True, timeout=_espeak_timeout())
            ver = (r.stdout or r.stderr).strip().splitlines()
            meta["version"] = ver[0] if ver else f"returncode={r.returncode}"
        except (OSError, subprocess.TimeoutExpired) as ex:
            meta["version"] = f"probe lỗi: {type(ex).__name__}"
    _ESPEAK_META = meta
    _ESPEAK_META_KEY = key
    return meta


_ESPEAK_META: dict | None = None
_ESPEAK_META_KEY: tuple | None = None
_POLICY_HASH: str | None = None


def v2_policy_hash() -> str:
    """Fingerprint POLICY/CODE/MAPPING của v2: CODE wrapper (sha256 file này),
    mọi bảng mapping espeak, WS fix, PUNCT_EMIT, bậc cứu, strict policy mặc
    định + g2p_policy_hash của lõi. Đổi bất kỳ cái nào (và mọi mutation đổi
    hành vi) phải làm hash này đổi."""
    global _POLICY_HASH
    if _POLICY_HASH is None:
        payload = {
            "schema": "g2p_v2_policy/0.3",
            "code_sha256_v2": _sha256_file(Path(__file__).resolve()),
            "espeak_vowels": _ESPEAK_VOWELS,
            "espeak_cons": _ESPEAK_CONS,
            "espeak_syllabic": _ESPEAK_SYLLABIC,
            "espeak_input_re": _ESPEAK_INPUT_RE.pattern,
            "espeak_split": _ESPEAK_SPLIT.pattern,
            "ws_fix": {str(k): v for k, v in sorted(_WS_FIX.items())},
            "punct_emit": sorted(PUNCT_EMIT),
            "ladder": ["core", "cmu", "espeak", "spell"],
            "default_strict_policy": sorted(DEFAULT_STRICT_POLICY),
            "strict_contract_allowlist": sorted(STRICT_CONTRACT_ALLOWLIST),
            "core_g2p_policy_hash": G.g2p_policy_hash(),
        }
        h = hashlib.sha256(json.dumps(payload, sort_keys=True,
                                      ensure_ascii=False).encode()).hexdigest()
        _POLICY_HASH = "g2p_v2_policy_" + h[:16]
    return _POLICY_HASH


def v2_provenance() -> dict:
    """Provenance đầy đủ của đường v2: policy hash + cấu hình espeak hiệu lực."""
    return {"policy_hash": v2_policy_hash(), "espeak": dict(_espeak_meta())}


def text_to_profile_v2_full(text: str, mode: str = "best_effort",
                            strict_policy: frozenset | set | None = None) -> dict:
    """G2P v2 — kết quả CÓ CẤU TRÚC (schema g2p_v2_result/0.1).

    mode:
      "best_effort" (mặc định, cho render) — câu luôn đọc tiếp; từ hụt bị bỏ
        TỪ và báo tường minh trong `dropped`/`notes`.
      "strict" (cho prep dữ liệu train) — từ chối cả câu (state="rejected",
        profile="") nếu mất nội dung bất kỳ (không phải drop chủ ý), nếu có
        unit được cứu bằng nguồn ngoài strict_policy, nếu IR lệch hợp đồng
        (contract_ok=False — MẶC ĐỊNH TỪ CHỐI; chỉ loại lỗi có tên trong
        STRICT_CONTRACT_ALLOWLIST mới được miễn), hoặc nếu profile rỗng
        trong khi câu có nội dung cần đọc. LƯU Ý: strict chỉ là BỘ LỌC KỸ
        THUẬT cho prep dữ liệu train — strict pass KHÔNG phải chứng nhận
        phiên âm đúng; chỉ bảo đảm đủ coverage + nguồn theo policy.

    state (coverage, KHÔNG phải correctness):
      complete — mọi unit nội dung được đọc, không mất unit nào (kể cả từ bị
                 scope QD57 cấm phát âm — đó vẫn là mất coverage), profile có
                 nội dung (≥1 từ). LƯU Ý: best_effort vẫn có thể complete dù
                 contract_ok=False — lỗi hợp đồng IR chỉ là warning, coverage
                 không mất; strict thì MẶC ĐỊNH TỪ CHỐI trường hợp đó
                 (chỉ loại lỗi tường minh trong STRICT_CONTRACT_ALLOWLIST
                 mới được miễn).
      partial  — câu vẫn đọc nhưng có unit nội dung bị bỏ (scope QD57, chữ
                 số chưa verbalize, từ ngoài phạm vi, validation).
      empty    — profile không còn unit nội dung nào (chỉ dấu câu/rỗng) dù
                 câu CÓ nội dung cần đọc — KHÔNG được tính là cứu thành công.
      rejected — chỉ ở strict: vi phạm policy.
    units — trace TỪNG read unit {word, outcome(read|upgraded|dropped),
                 source, read_complete[, reason][, intentional]}. Fast path
                 (record đọc tốt nguồn core) được MỞ RA thành từng read unit
                 theo master.read_units; chỉ khi record không có read_units
                 mới xuất 1 DÒNG GỘP tường minh ("merged": true +
                 "unit_count": N) — không bao giờ gọi record gộp là
                 trace per-unit.
    """
    if mode not in ("best_effort", "strict"):
        raise ValueError(f"mode không hợp lệ: {mode!r}")
    policy = frozenset(strict_policy) if strict_policy is not None \
        else DEFAULT_STRICT_POLICY
    bad_policy = policy - {"core", "cmu", "espeak", "spell"}
    if bad_policy:
        raise ValueError(f"strict_policy có nguồn lạ: {sorted(bad_policy)}")

    by_id = G._by_id()
    ir = t1_normalize(text.translate(_WS_FIX))
    out = G.g2p_stream(ir)
    parts, errs, notes, warnings = [], [], [], []
    dropped, sources, units = [], Counter(), []
    contract_ok = True
    if out.get("contract_errors"):
        # lỗi hợp đồng IR (vd read_string lệch dãy do token dính NBSP) — chỉ
        # là kiểm kiểm-chéo của tầng 1, KHÔNG ảnh hưởng phát âm từng token:
        # v2 xử lý per-token, KHÔNG bỏ câu vì nó. Ghi warning, không hạ state.
        contract_ok = False
        warnings.append("IR lệch hợp đồng (" + out["contract_errors"][0][:60]
                        + "…) — xử lý per-token, không mất unit")
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
            # icon/deferred — v1 (NGUỒN "core") cũng bỏ nguyên vẹn: drop chủ ý
            notes.append(f"bỏ token deferred '{surf}'")
            dropped.append({"word": surf, "reason": "icon/deferred (v1 bỏ giống hệt)",
                            "intentional": True})
            units.append({"word": surf, "outcome": "dropped", "source": None,
                          "read_complete": False,
                          "reason": "icon/deferred (v1 bỏ giống hệt)"})
            continue
        if st == "scope_excluded":
            notes.append(f"bỏ từ '{surf}' (scope QD57 cấm phát âm — không cứu)")
            # scope là TỪ NỘI DUNG bị policy cấm phát âm: giữ lệnh cấm, NHƯNG
            # vẫn là mất coverage (best_effort → partial, strict → rejected).
            # intentional=True chỉ dành cho icon/biểu tượng (không có gì để đọc)
            dropped.append({"word": surf, "reason": "scope QD57 cấm phát âm",
                            "intentional": False})
            units.append({"word": surf, "outcome": "dropped", "source": None,
                          "read_complete": False, "reason": "scope QD57"})
            continue
        if rec.get("contract_errors") or rec.get("validation"):
            msg = (rec.get("validation") or rec.get("contract_errors"))[0]
            errs.append(f"tok[{rec.get('i')}:{surf[:20]}] {msg}")
            dropped.append({"word": surf, "reason": f"validation: {msg}",
                            "intentional": False})
            units.append({"word": surf, "outcome": "dropped", "source": None,
                          "read_complete": False, "reason": f"validation: {msg}"})
            continue
        txt, trace = _rescue_record(rec, by_id, notes)
        for t in trace:
            units.append({k: t[k] for k in t})
            if t["outcome"] in ("read", "upgraded"):
                sources[t["source"]] += t.get("unit_count", 1)
            else:
                dropped.append({"word": t["word"], "reason": t.get("reason", "?"),
                                "intentional": t.get("intentional", False)})
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
    profile = "".join(pieces)
    word_pieces = sum(1 for k, _ in parts if k == "word")

    # state theo COVERAGE
    lost = [d for d in dropped if not d["intentional"]]
    if profile and word_pieces > 0 and not lost and not errs:
        state = "complete"
    elif profile and word_pieces > 0:
        state = "partial"
    else:
        state = "empty"

    if mode == "strict":
        # "core" = đường v1 nguyên bản, LUÔN được phép bất kể policy
        bad_src = sorted(set(sources) - policy - {"core"})
        # IR lệch hợp đồng: chỉ miễn các LOẠI lỗi tường minh trong allowlist
        # (mặc định rỗng) — không miễn toàn bộ contract_errors
        bad_contract = sorted(_contract_kinds(out.get("contract_errors", []))
                              - STRICT_CONTRACT_ALLOWLIST) if not contract_ok else []
        if bad_src or bad_contract or lost or state == "empty":
            why = []
            if bad_contract:
                why.append("IR lệch hợp đồng: " + "; ".join(bad_contract[:2]))
            if lost:
                why.append(f"mất {len(lost)} unit nội dung: "
                           + ", ".join("'" + d["word"] + "'" for d in lost[:3]))
            if bad_src:
                why.append("nguồn cứu ngoài policy: " + ", ".join(bad_src))
            if state == "empty":
                why.append("profile rỗng trong khi câu có nội dung")
            errs.append("strict: " + "; ".join(why))
            state = "rejected"
            profile = ""

    return {
        "schema": "g2p_v2_result/0.3",
        "mode": mode,
        "state": state,
        "profile": profile,
        "errs": errs,
        "notes": notes,
        "warnings": warnings,
        "contract_ok": contract_ok,
        "dropped": dropped,
        "units": units,
        "sources": dict(sources),
        "strict_policy": sorted(policy),
        "provenance": v2_provenance(),
    }


def text_to_profile_v2(text: str):
    """API CŨ (giữ tương thích): trả (profile, errs, notes) như trước.
    Muốn kết quả có cấu trúc (state/dropped/sources/provenance) hãy dùng
    text_to_profile_v2_full."""
    r = text_to_profile_v2_full(text)
    return r["profile"], r["errs"], r["notes"]


if __name__ == "__main__":
    for line in sys.argv[1:] or ["Đã lo lắng thì cứ thừa nhận, cần gì phải "
                                 "tsundere vòng vo tam quốc thế chứ?"]:
        r = text_to_profile_v2_full(line)
        print("PROFILE:", r["profile"])
        print("state:", r["state"], "| sources:", r["sources"],
              "| dropped:", r["dropped"])
        print("provenance:", json.dumps(r["provenance"], ensure_ascii=False))
        for n in r["notes"]:
            print("  •", n)
