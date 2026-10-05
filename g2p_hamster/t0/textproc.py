"""Dọn text + tokenize: NFC, policy ký tự, tách token, tách chữ dính, camelCase."""
import html
import re
import unicodedata

from . import dicts

# camelCase: tách khi 2+ ký tự thường đứng trước 1 ký tự hoa ("nhQuang" -> "nh Quang").
# Dùng isupper() chứ không regex range — dải Unicode vi úp lẫn hoa/thường.


def _camel_split(core: str):
    for i in range(2, len(core)):
        if core[i].isupper() and core[i - 1].islower() and core[i - 2].islower():
            return [core[:i]] + _camel_split(core[i:])
    return [core]

# Dấu câu tách ra thành token riêng khi đứng đầu/cuối một chunk
_EDGE_PUNCT = set(".,!?;:\"'`“”‘’()[]{}<>«»…–—*•|/\\^~=_+«»¡¿")

ABBREV_DOT = {"tp", "ts", "gs", "pgs", "bs", "tt", "th", "đt", "mr", "ms", "dr", "vs",
              "e.g", "i.e", "etc", "đh", "pgs", "ht", "ct", "ubnd",
              "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept",
              "oct", "nov", "dec",
              "p", "q", "tx"}   # đơn vị hành chính: phường/quận/thị xã (không "h" — đè unit "17h", không "x" — trùng biến toán)


def apply_policy_char(c: str):
    """Trả về (keep, replacement, action) cho một ký tự."""
    return dicts.apply_policy_char(c)


MOJIBAKE_FALLBACK = {
    "\u00e2\u20ac\u201d": "\u2014",   # em-dash mojibake
    "\u00e2\u20ac\u201c": "\u201c",
    "\u00e2\u20ac\u02dc": "\u2018",
    "\u00e2\u20ac\u2122": "\u2019",
    "\u00e2\u20ac\u2013": "\u2013",
    "\u00c2\u00a0": " ",
}

_TRANS_TABLE = None  # dict ký tự -> replacement, dựng 1 lần từ policy (str.translate = C-speed)


def _trans():
    global _TRANS_TABLE
    if _TRANS_TABLE is None:
        table = {ord("\t"): " ", ord("\n"): " ", ord("\r"): " "}
        for ch, (action, target) in dicts.char_policy().items():
            if action == "normalize":
                table[ord(ch)] = target
            elif action in ("drop", "drop_log"):
                table[ord(ch)] = None
            # keep/read: không entry -> giữ nguyên
        _TRANS_TABLE = table
    return _TRANS_TABLE


def clean(text: str):
    """Trả về (text_sạch, list_reason_log). Deterministic. str.translate thay vòng lặp per-char."""
    logs = []
    text = html.unescape(text)
    try:
        import ftfy
        text = ftfy.fix_text(text)   # sửa mojibake: â€” -> —, Ã¤ -> ä ...
    except ImportError:
        for bad, good in MOJIBAKE_FALLBACK.items():
            if bad in text:
                text = text.replace(bad, good)
    text = unicodedata.normalize("NFC", text)
    # "..." (3 chấm) -> "…" một ký tự: policy giữ "…", khỏi bị gộp thành 1 chấm gãy câu
    text = re.sub(r"\.{3,}", "…", text)
    # "+/-" -> "±" một ký tự, đọc "cộng trừ"
    text = text.replace("+/-", "±")
    # chữ*chữ ("E*Trade") -> khoảng trắng; dấu * trang trí giữa chữ là nhiễu
    text = re.sub(r"(?<=[A-Za-zà-ỹĐ])\*(?=[A-Za-zà-ỹĐ])", " ", text)
    # gạch ngang dài giữa 2 số ("1895–1984") -> gạch thường để nhận diện khoảng năm
    text = re.sub(r"(?<=\d)\s*[–—]\s*(?=\d)", "-", text)
    # thẻ HTML dính từ nguồn ("<p>", "<a href=...>", "</b>") — dữ liệu web bẩn, bỏ nguyên
    text = re.sub(r"</?[a-zA-Z][a-zA-Z0-9]{0,10}(?:\s[^>\n]{0,400})?/?>", " ", text)
    # contraction gõ thiếu nháy ("dont", "cant"...) -> trả nháy; bỏ qua dạng mơ hồ
    # (im/ive/id/ill/lets trùng từ thật hoặc viết tắt ID)
    _NO_APOS = {"dont": "don't", "cant": "can't", "didnt": "didn't",
                "doesnt": "doesn't", "isnt": "isn't", "arent": "aren't", "wasnt": "wasn't",
                "werent": "weren't", "havent": "haven't", "hasnt": "hasn't", "hadnt": "hadn't",
                "couldnt": "couldn't", "shouldnt": "shouldn't", "wouldnt": "wouldn't",
                "thats": "that's", "whats": "what's", "theres": "there's", "heres": "here's",
                "youre": "you're", "youve": "you've", "theyre": "they're", "theyve": "they've",
                "weve": "we've", "shes": "she's", "hes": "he's"}
    def _reapos(m):
        w = m.group(1)
        r = _NO_APOS[w.lower()]
        return r[0].upper() + r[1:] if w[0].isupper() else r
    text = re.sub(r"\b(" + "|".join(_NO_APOS) + r")\b", _reapos, text, flags=re.I)
    # nháy đơn GIỮA từ ("he'll", "o'clock") -> U+02BC để khỏi bị policy xóa ("he'll" thành "hell")
    text = re.sub(r"(?<=[A-Za-zà-ỹĐ])['’ʼ](?=[A-Za-zà-ỹĐ])", "\u02bc", text)
    dropped = [c for c in set(text) if _trans().get(ord(c), c) is None]
    for c in dropped:
        logs.append(f"drop_log:{c!r}")
    text = text.translate(_trans())
    text = re.sub(r"[ \u00a0]{2,}", " ", text).strip()
    return text, logs


def split_sentences(text: str):
    """Tách câu abbrev-aware. Input thường đã là 1 câu (corpus), hàm cho input tùy ý."""
    sents, cur = [], []
    toks = text.split(" ")
    for i, t in enumerate(toks):
        cur.append(t)
        stripped = t.rstrip(".!?…").lower().rstrip(".")
        is_abbrev = (t.lower().rstrip(".") in ABBREV_DOT) or (len(t.rstrip(".!?…")) == 1 and t[-1] == ".")
        if t and t[-1] in ".!?…" and not is_abbrev and i + 1 < len(toks):
            nxt = toks[i + 1]
            if nxt[:1].isupper() or nxt[:1] in "\"'“‘([":
                sents.append(" ".join(cur))
                cur = []
    if cur:
        sents.append(" ".join(cur))
    return sents


def _emit_punct(s: str, toks):
    for c in s:
        kept, repl, _ = apply_policy_char(c)
        if kept:
            toks.append({"surface": repl, "cat": "punct"})


def tokenize(text: str):
    """text đã clean -> list dict token thô {'surface', 'cat': 'raw'|'punct'}.

    Quy tắc:
    - email/url/đam đîn cũng tách nguyên chunk (không xé dấu @ . /)
    - chunk số+đơn vị dính ("25tr","5kg") tách thành số + đơn vị
    - "30-odd" tách gạch nối khi có chữ; "2021-2022" giữ nguyên
    - ALL-CAPS <=5 -> giữ (phân loại sau); camelCase tách
    """
    toks = []
    # chữ dính scheme ("reviewhttps://...") -> tách đôi để URL được nhận diện
    text = re.sub(r"([A-Za-zà-ỹĐđ])(https?://)", r"\1 \2", text)
    for chunk in text.split(" "):
        if not chunk:
            continue
        low = chunk.lower().rstrip(".!?…,;:").strip()
        if "@" in chunk and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", chunk):
            toks.append({"surface": chunk, "cat": "raw"})
            continue
        # viết tắt dính ("TP.Tuy" khớp nhánh URL bên dưới vì trông như "xx.yy")
        # -> chặn ở đây cho _split_core tách
        if re.match(r"^[A-ZĐ]{1,6}\.", chunk) and chunk.rstrip(".!?…,;:").split(".", 1)[0].lower() in ABBREV_DOT:
            pass
        elif (re.fullmatch(r"(https?://[\w\-]+(/[^\s]*)?|(https?://)?(www\.)?[a-z0-9\-]+(\.[a-z0-9\-]{2,})+(/[^\s]*)?)", chunk, re.I)
                and re.search(r"[a-zA-Z]", chunk) and not re.fullmatch(r"[\d.,]+", chunk)
                and not re.fullmatch(r"\d+(?:[.,]\d+)+[A-Za-z]{1,4}", chunk)):   # "1.5M", "2.3M" là số+đơn vị, không phải domain
            toks.append({"surface": chunk, "cat": "raw"})
            continue
        # ngôn ngữ lập trình ("C++", "C#") — chặn TRƯỚC edge-strip kẻo "+" bị gọt
        if re.fullmatch(r"[A-Za-z](\+\+|#|--)", chunk):
            toks.append({"surface": chunk, "cat": "raw"})
            continue
        # tiền tệ kèm hậu tố chữ ("$1.5B", "$2,000") — giữ nguyên 1 token kẻo B/M bị xé khỏi số
        core_like = chunk.strip("".join(_EDGE_PUNCT))
        if re.fullmatch(r"[$€£¥]\d{1,12}(?:[.,]\d+)?[BMKbmk]?", core_like):
            toks.append({"surface": core_like, "cat": "raw"})
            continue
        # tách dấu câu đầu/cuối
        i, j = 0, len(chunk)
        while i < j and chunk[i] in _EDGE_PUNCT:
            i += 1
        while j > i and chunk[j - 1] in _EDGE_PUNCT:
            j -= 1
        if i:
            _emit_punct(chunk[:i], toks)
        core = chunk[i:j]
        if core:
            toks.extend(_split_core(core))
        if j < len(chunk):
            _emit_punct(chunk[j:], toks)
    # gộp dấu lặp "!!!" thành một token
    merged = []
    for t in toks:
        if merged and t["cat"] == "punct" and merged[-1]["cat"] == "punct" \
                and set(t["surface"]) == set(merged[-1]["surface"]) and len(t["surface"]) == 1:
            continue
        merged.append(t)
    return merged


_UNIT_SUFFIX_RE = re.compile(r"^(\d{1,12}([.,]\d+)?)((?:°?[a-zđ°C]{1,4}){1,2})$", re.I)


def _split_core(core: str):
    toks = []
    # ngôn ngữ lập trình dính dấu ("C++", "C#", "C--") -> giữ nguyên 1 token
    if re.fullmatch(r"[A-Za-z]\+\+|[A-Za-z]#[A-Za-z0-9]*|[A-Za-z](?:\+\+|--)", core):
        toks.append({"surface": core, "cat": "raw"})
        return toks
    # viết tắt dính tên riêng ("TP.Đà Nẵng" thành 1 chunk) -> tách "TP." + "Đà"
    m_abbr_glued = re.match(r"^([A-ZĐ]{1,6}\.)((?:[A-ZĐ][\wà-ỹĐ]*)|(?:[\wà-ỹđ]+))$", core)
    if m_abbr_glued and m_abbr_glued.group(1).rstrip(".").lower() in ABBREV_DOT:
        toks.append({"surface": m_abbr_glued.group(1), "cat": "raw"})
        toks.extend(_split_core(m_abbr_glued.group(2)))
        return toks
    # phiên bản "v1.4", "v2.0" — giữ nguyên 1 token kẻo số bị kế thừa route của chữ "v"
    if re.fullmatch(r"[vV]\d+(?:\.\d+)+", core):
        toks.append({"surface": core, "cat": "raw"})
        return toks
    # chữ bị kiểm duyệt chèn dấu vào giữa ("gi.ết", "ch/ặt", "đ.a'nh") -> gỡ dấu, nối lại.
    # Chỉ nối khi kết quả là MỘT âm tiết vi có thật ("vấn/hỗ" là gạch phân cách, không đụng).
    # Riêng toàn-ASCII + nháy đơn là rút gọn tiếng Anh ("he'll") -> không đụng
    if (re.fullmatch(r"[a-zà-ỹđ]{1,3}([./\'’ʼ][a-zà-ỹđ]{1,3}){1,6}", core)
            and core.lower() not in dicts.units()
            and core.lower() not in ABBREV_DOT):
        ascii_apos = all(ord(c) < 128 for c in core if c.isalpha() and c not in "'’ʼ") \
            and any(j in core for j in "'’ʼ")   # U+02BC là chữ cái (Lm) -> phải loại riêng
        joined = re.sub(r"[./\'’ʼ]", "", core)
        if not ascii_apos and (joined == core or dicts.fold(joined) in dicts.syllables_vi()):
            toks.append({"surface": joined, "cat": "raw"})
            toks[-1]["review_hint"] = "censor_join"
            return toks
    # "%" luôn tách thành symbol; "/" tách khi chunk không phải date/url
    if "%" in core:
        for part in re.split(r"(%)", core):
            if part == "%":
                toks.append({"surface": "%", "cat": "symbol"})
            elif part:
                toks.extend(_split_core(part))
        return toks
    if "/" in core and not re.fullmatch(r"\d{1,2}/\d{1,2}(/\d{2,4})?|\d{1,2}/\d{4}|\d{1,2}-\d{1,2}/\d{1,2}", core) \
            and not re.fullmatch(r"(https?://)?[\w\-]+(\.[\w\-]+)+(/[^\s]*)?", core, re.I) \
            and not re.fullmatch(r"https?://[\w\-]+(/[^\s]*)?", core, re.I) \
            and not re.fullmatch(r"((https?://)?(www\.)?)?[\w\-]+(\.[\w\-]+)+(/[^\s]*)?", core, re.I) \
            and core.lower() not in dicts.units():
        for part in re.split(r"(/)", core):
            if part == "/":
                toks.append({"surface": "/", "cat": "punct"})
            elif part:
                toks.extend(_split_core(part))
        return toks
    # ranh giới chữ-số dính nhau ("Đức13:38" -> "Đức" + "13:38") hoặc có "(" ")" giữa từ
    # ("Fax:(84-511" -> "Fax:" "(" "84-511"); giữ nguyên dạng thời gian "9h30"
    if (re.search(r"[A-Za-zà-ỹĐ]\d|\d[A-Za-zà-ỹĐ]|[()]", core)
            and not re.fullmatch(r"\d{1,2}h\d{0,2}p?", core, re.I)
            and not (_UNIT_SUFFIX_RE.match(core) and not re.fullmatch(r"\d{1,2}[A-Z]{1,2}", core))):
        parts2, cur, prev = [], "", ""
        for c in core:
            # cắt ranh giới chữ-số và tại "(" ")" giữa từ ("Fax:(84-511)" -> "Fax:" "(" "84-511" ")")
            if cur and (c in "()" or prev in "()"
                        or (prev.isalpha() and c.isdigit()) or (prev.isdigit() and c.isalpha())):
                parts2.append(cur)
                cur = ""
            cur += c
            prev = c
        if cur:
            parts2.append(cur)
        for part in parts2:
            toks.append({"surface": part, "cat": "raw"})
        return toks
    # "3D" "4K" -> số + chữ cái đọc riêng
    if re.fullmatch(r"\d{1,2}[A-Za-z]{1,2}", core):
        m2 = re.match(r"(\d{1,2})([A-Za-z]{1,2})", core)
        toks.append({"surface": m2.group(1), "cat": "raw"})
        toks.append({"surface": m2.group(2), "cat": "raw"})
        return toks
    m = _UNIT_SUFFIX_RE.match(core)
    if m and not (m.group(3).lower() == "s" and len(m.group(1)) == 4) \
            and (m.group(3).lower() in dicts.units() or m.group(3).lower() in ("phut", "p", "h", "gb", "mb", "kb", "tb", "ms", "mbps", "s", "m", "kw", "hz")):
        toks.append({"surface": m.group(1), "cat": "raw"})
        toks.append({"surface": m.group(3), "cat": "raw"})
        return toks
    # gạch nối có chữ -> tách; cả hai bên đều số -> giữ
    if "-" in core and not re.fullmatch(r"[\d.,\-/]+", core):
        for part in re.split(r"(-)", core):
            if part == "-":
                toks.append({"surface": "-", "cat": "punct", "glue": True})
            elif part:
                toks.extend(_split_core(part))
        return toks
    if re.search(r"[A-Za-z]", core):
        parts = _camel_split(core)
        if len(parts) > 1 and not re.match(r"^[a-zà-ỹ][A-ZÀ-Ỹ]", core):
            for part in parts:
                toks.append({"surface": part, "cat": "raw"})
            return toks
    toks.append({"surface": core, "cat": "raw"})
    return toks
