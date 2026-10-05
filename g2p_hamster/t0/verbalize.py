"""Verbalize: (category, route, giá trị, ngữ cảnh) -> chuỗi đọc. Không có model nào ở đây."""
import re

from . import dicts
from .numbers import (EN_MONTHS, VI_MONTHS, en_cardinal, en_digits, en_year,
                      number_to_words, vi_cardinal, vi_digits)
from .detect import roman_value

SYM_READ = {
    "%": ("phần trăm", "percent"), "&": ("và", "and"), "+": ("cộng", "plus"),
    "=": ("bằng", "equals"), "#": ("dấu thăng", "hash"), "@": ("a còng", "at"),
    "°": ("độ", "degrees"), "/": ("gạch chéo", "slash"), "\\": ("gạch ngược", "backslash"),
    "|": ("vạch dọc", "pipe"), "~": ("dấu ngã", "tilde"), "^": ("dấu mũ", "caret"),
    "<": ("bé hơn", "less than"), ">": ("lớn hơn", "greater than"),
    "$": ("đô la", "dollars"), "€": ("euro", "euros"), "£": ("bảng anh", "pounds"),
    "¥": ("yên", "yen"), "₫": ("đồng", "dong"), "±": ("cộng trừ", "plus or minus"),
}
CURRENCY_OF = {"$": "usd", "€": "eur", "£": "gbp", "¥": "jpy", "₫": "vnd"}
KNOWN_DOMAINS = {"gmail", "yahoo", "hotmail", "outlook", "icloud", "com", "vn", "net", "org",
                 "edu", "gov", "info", "biz"}
VOWELS = set("aeiou")


def _decimal_part(dec: str, route: str) -> str:
    if route == "vi":
        return " ".join(vi_digits(d) for d in dec)
    return " ".join(en_digits(d) for d in dec)


def _read_side(x: str, route: str) -> str:
    """Đọc 1 vế khoảng số, giữ phần thập phân: '139,5' -> 'một trăm ba mươi chín phẩy năm'.
    vi: dấu phẩy là thập phân; en: dấu chấm là thập phân (phẩy là nhóm nghìn).
    Riêng vi: "8.5" kiểu tech (chấm + 1-2 chữ số) vẫn là thập phân, KHÔNG phải nhóm nghìn."""
    if route == "vi":
        m_dot = re.fullmatch(r"(\d{1,9})\.(\d{1,2})", x)
        if m_dot:
            x = f"{m_dot.group(1)},{m_dot.group(2)}"
    sep = "," if route == "vi" else "."
    m = re.fullmatch(r"(\d{1,9})" + re.escape(sep) + r"(\d+)", x)
    if not m:
        return x if route == "en" else number_to_words(x.replace(".", ""), route)
    joiner = " phẩy " if route == "vi" else " point "
    return number_to_words(m.group(1), route) + joiner + _decimal_part(m.group(2), route)


def _vi_interval(a: str, b: str, route: str = "vi") -> str:
    joiner = " đến " if route == "vi" else " to "
    if route == "vi":
        # "8.5" kiểu tech (chấm + 1-2 số) là thập phân; "440.000" là nhóm nghìn -> giữ
        a = re.sub(r"(\d)\.(\d{1,2})(?!\d)", r"\1,\2", a)
        b = re.sub(r"(\d)\.(\d{1,2})(?!\d)", r"\1,\2", b)
    sep = "," if route == "vi" else "."
    if sep in a or sep in b:
        return _read_side(a, route) + joiner + _read_side(b, route)
    a = a.replace(".", "").replace(",", "")   # "440.000-740.000" -> số trần
    b = b.replace(".", "").replace(",", "")
    return f"{number_to_words(a, route)}{joiner}{number_to_words(b, route)}"


def _vi_score(a: str, b: str) -> str:
    # kiểu bình luận viên: hòa "2-2" -> "hai đều"; lệch "2-1" -> "hai, một";
    # b=0 đọc không dấu phẩy ("một không") kẻo nghe thành "một, không cho..."
    if a == b:
        return f"{vi_digits(a)} đều"
    if b == "0":
        return f"{vi_digits(a)} không"
    # b ≥ 10 đọc tròn số ("88-85" -> "tám tám, tám mươi lăm"), 1 chữ thì gõ
    b_w = number_to_words(b, "vi") if len(b) >= 2 else vi_digits(b)
    return f"{vi_digits(a)}, {b_w}"


CONTRACTIONS = {"'re": "are", "'m": "am", "'ll": "will", "'ve": "have", "n't": "not"}

_ORD_SPECIAL = {1: "first", 2: "second", 3: "third", 5: "fifth", 8: "eighth",
                9: "ninth", 12: "twelfth", 20: "twentieth", 30: "thirtieth"}


def en_day_ordinal(n: int) -> str:
    """"Feb. 13" -> "thirteenth" (ngày trong tháng đọc thứ tự)."""
    if n in _ORD_SPECIAL:
        return _ORD_SPECIAL[n]
    if n < 20:
        return number_to_words(str(n), "en") + "th"   # fourth, sixth, tenth, thirteenth
    tens = {2: "twenty", 3: "thirty"}[n // 10]
    return tens + "-" + _ORD_SPECIAL.get(n % 10, number_to_words(str(n % 10), "en") + "th")


_CONTRACTION_SPECIAL = {"can't": "cannot", "won't": "will not", "shan't": "shall not"}


def _expand_contractions(s: str) -> str:
    out = s.replace("\u02bc", "'")
    low = out.lower()
    if low in _CONTRACTION_SPECIAL:   # "can't" -> suffix "n't" ăn mất n của "can" ("ca not")
        return _CONTRACTION_SPECIAL[low]
    for suffix, full in CONTRACTIONS.items():
        if out.lower().endswith(suffix):
            out = out[: -len(suffix)] + " " + full
            break
    return out


def _verbal_date(t, route: str, prev: str) -> str:
    surface = t["surface"]
    kind = t.get("kind", "dmy")
    if kind == "dmy_hyphen":
        surface = surface.replace("-", "/")
        kind = "dmy"
    if kind == "dm_dot":
        surface = surface.replace(".", "/")
        kind = "dm"
    if kind == "dm_hyphen":
        surface = surface.replace("-", "/")
        kind = "dm"
    if kind == "dmy_dot":
        surface = surface.replace(".", "/")
        kind = "dmy"
    try:
        parts = surface.split("/")
    except Exception:
        return surface
    route_v = route or "vi"
    if route_v == "vi":
        if kind == "dmy" and len(parts) == 3:
            d, m, y = parts
            if not (1 <= int(m) <= 12):
                return " trên ".join(number_to_words(x, "vi") for x in parts)
            y4 = y if len(y) == 4 else ("19" + y if len(y) == 2 else y)
            base = f"{number_to_words(d, 'vi')} tháng {VI_MONTHS[int(m) - 1]} năm {vi_cardinal(int(y4))}"
            return base if prev in ("ngày", "mùng", "vào") else f"ngày {base}"
        if kind == "my" and len(parts) == 2:
            m, y = parts
            return f"{VI_MONTHS[int(m) - 1]} năm {vi_cardinal(int(y))}"
        if kind == "dm" and len(parts) == 2:
            d, m = parts
            if prev == "vòng":   # "vòng 1/16" -> "một phần mười sáu" (phân số, không phải ngày)
                return f"{number_to_words(d, 'vi')} phần {number_to_words(m, 'vi')}"
            base = f"{number_to_words(d, 'vi')} tháng {VI_MONTHS[int(m) - 1]}"
            if kind.startswith("dm") and (prev in ("ngày", "mùng", "vào") or "." in surface):
                return base
            return base if prev in ("ngày", "mùng", "vào") else f"ngày {base}"
        if kind == "range_dm":
            a, b, m_ = t["groups"]
            if 1 <= int(m_) <= 12:
                return (f"{number_to_words(a, 'vi')} đến {number_to_words(b, 'vi')} "
                        f"tháng {VI_MONTHS[int(m_) - 1]}")
            return " ".join(vi_digits(p) for p in f"{a}/{b}/{m_}".split("/"))   # lưới an toàn
        if kind == "my_span" and "/" in surface:
            m_, y = surface.split("/")
            if 1 <= int(m_) <= 12:
                return f"tháng {VI_MONTHS[int(m_) - 1]} năm {vi_cardinal(int(y))}"
            return surface   # lưới an toàn: tháng ngoài 1-12 -> giữ nguyên, không crash
        if kind == "slash_digits" and len(parts) == 2:
            if prev == "vòng":   # "vòng 1/16" -> "một phần mười sáu"
                return f"{number_to_words(parts[0], 'vi')} phần {number_to_words(parts[1], 'vi')}"
            joiner = " trên " if route == "vi" else " over "
            return (number_to_words(parts[0], route) + joiner + number_to_words(parts[1], route))
    else:
        if kind == "range_dm":
            a, b, m_ = t["groups"]   # "24-26/9" trong câu en -> "24 to 26 September"
            try:
                return f"{en_cardinal(int(a))} to {en_cardinal(int(b))} {EN_MONTHS[int(m_) - 1]}"
            except Exception:
                return surface
        if len(parts) == 3:
            a, b, y = parts
            if int(a) <= 12 and int(b) > 12:
                m, d = int(a), int(b)
            else:
                d, m = int(a), int(b)
            y4 = y if len(y) == 4 else ("19" + y if len(y) == 2 else y)
            try:
                return f"{EN_MONTHS[m - 1]} {en_cardinal(d)} {en_year(int(y4))}"
            except Exception:
                return surface
        if len(parts) == 2:
            a, b = parts
            if not (a.isdigit() and b.isdigit()):
                return surface   # lưới an toàn: "24-26" chưa gỡ gạch -> giữ nguyên, không crash
            if int(a) <= 12:
                return f"{EN_MONTHS[int(a) - 1]} {en_cardinal(int(b))}"
            return f"{en_cardinal(int(a))} {EN_MONTHS[int(b) - 1]}"
    return surface


def _verbal_time(surface: str, kind: str, groups, route: str) -> str:
    route_v = route or "vi"
    if kind == "h":
        h, mm, p = groups
        h = int(h)
        mm = int(mm) if mm else None
        vi = route_v == "vi"
        words = []
        words.append(number_to_words(str(h), "vi" if vi else "en"))
        words.append("giờ" if vi else "hours" if mm else "o'clock")
        if mm:
            words.append(number_to_words(str(mm), "vi" if vi else "en"))
            if p:
                words.append("phút" if vi else "minutes")
        elif p:
            words.append("phút" if vi else "minutes")
        return " ".join(words)
    h, mm, _colon_sec, _s2, ampm = groups
    sec = _s2   # group 4 = số giây; group 3 là ":55" nguyên cụm
    if route_v == "vi":
        out = f"{number_to_words(h, 'vi')} giờ"
        if int(mm):
            out += f" {number_to_words(mm, 'vi')}" + (" phút" if sec else "")
        elif sec:
            out += " không phút"
        if sec:
            out += f" {number_to_words(sec, 'vi')} giây"
        if ampm:
            out += " " + ("sáng" if ampm.lower() == "am" else "chiều")
        return out
    out = f"{number_to_words(h, 'en')} {number_to_words(mm, 'en')}"
    if sec:
        out += f" {number_to_words(sec, 'en')} seconds"
    if ampm:
        out += " " + ("a m" if ampm.lower() == "am" else "p m")
    return out


def _verbal_email(surface: str, route: str) -> str:
    route_v = route or "vi"
    at = "a còng" if route_v == "vi" else "at"
    dot = "chấm" if route_v == "vi" else "dot"
    def piece(p: str) -> str:
        out = []
        for run in re.findall(r"\d+|\D+", p):
            if run.isdigit():
                out.append(vi_digits(run) if route_v == "vi" else en_digits(run))
            elif run in (".", "_", "-"):
                out.append({"-": "gạch" if route_v == "vi" else "dash",
                            "_": "gạch dưới" if route_v == "vi" else "underscore"}.get(run, dot))
            else:
                out.append(run)
        return " ".join(x for x in out if x)
    try:
        local, dom = surface.rsplit("@", 1)
    except ValueError:
        return surface
    parts = [piece(local), at]
    for seg in re.split(r"([.\-_])", dom):
        if seg in (".", "-", "_"):
            parts.append(dot if seg == "." else piece(seg))
        elif seg:
            parts.append(seg if seg.lower() in KNOWN_DOMAINS else piece(seg))
    return " ".join(parts)


def _verbal_url(surface: str, route: str) -> str:
    route_v = route or "vi"
    dot = "chấm" if route_v == "vi" else "dot"
    slash = "gạch chéo" if route_v == "vi" else "slash"
    # bỏ hẳn scheme khi đọc — người nghe chỉ cần "w w w chấm ..." ("https://" là nhiễu)
    m_scheme = re.match(r"^(https?)://", surface, flags=re.I)
    if m_scheme:
        surface = surface[m_scheme.end():]
    scheme = ""
    s = surface
    parts = []
    for seg in re.split(r"([./\-_])", s):
        if seg in (".", "/", "-", "_"):
            parts.append(dot if seg == "." else slash if seg == "/" else
                         ("gạch" if route_v == "vi" else "dash") if seg == "-" else
                         ("gạch dưới" if route_v == "vi" else "underscore"))
        elif seg.lower() in ("www",):
            parts.append("w w w")
        elif seg.lower() in KNOWN_DOMAINS:
            parts.append(seg)
        elif seg:
            out = []
            for run in re.findall(r"\d+|\D+", seg):
                if run.isdigit():
                    out.append(vi_digits(run) if route_v == "vi" else en_digits(run))
                else:
                    out.append(run)
            parts.append(" ".join(out))
    return (scheme + " ".join(p for p in parts if p)).strip()


def _verbal_money_prefix(sym: str, num: str, route: str) -> str:
    route_v = route or "vi"
    mult = ""
    m = re.fullmatch(r"(\d{1,12}(?:[.,]\d+)?)([BMKbmk])", num)
    if m:   # "$1.5B" -> "một phẩy năm tỷ đô la"
        num = m.group(1)
        suf = m.group(2).upper()
        if route_v == "vi":
            mult = {"B": " tỷ", "M": " triệu", "K": " nghìn"}[suf]
        else:
            mult = {"B": " billion", "M": " million", "K": " thousand"}[suf]
    unit = dicts.units().get(CURRENCY_OF.get(sym, "usd"), ("đô la", "dollars", "money"))
    words = number_to_words(num, route_v)
    return f"{words}{mult} {unit[0] if route_v == 'vi' else unit[1]}"


def verbal_token(t, prev_surface: str = "") -> str:
    """Trả về chuỗi đọc cho token đã detect. '' = không đọc (vẫn có break/prosody)."""
    cat, route = t["cat"], t.get("route") or "vi"
    s = t["surface"]
    if cat == "punct":
        # giữ dấu đã chuẩn hóa trong chuỗi đọc — user cần thấy dấu để kiểm soát ngắt nghỉ
        PUNCT_KEEP = set(".,;:!?…-()/")
        return s if s in PUNCT_KEEP else ""
    if cat == "symbol":
        vi_s, en_s = SYM_READ.get(s, (s, s))
        return vi_s if route == "vi" else en_s
    if cat == "number":
        kind = t.get("kind", "cardinal")
        if kind == "roman":
            return number_to_words(str(roman_value(t["groups"][0])), route)
        if kind == "ordinal":
            num, suffix = t["groups"]
            en_ord = {1: "st", 2: "nd", 3: "rd"}.get(int(num) % 10 if int(num) % 100 not in (11, 12, 13) else 0, "th")
            if route == "vi":
                return f"thứ {number_to_words(num, 'vi')}"
            words = number_to_words(num, "en")
            en_word = {1: "first", 2: "second", 3: "third"}.get(
                int(num) % 10 if int(num) % 100 not in (11, 12, 13) else 0,
                {"first": words + "th"}.get("first", words + "th"))
            special = {1: "first", 2: "second", 3: "third", 5: "fifth", 8: "eighth", 9: "ninth", 12: "twelfth"}
            last_two = int(num) % 100
            if last_two in (11, 12, 13):
                en_word = words + "th"
            elif int(num) % 10 in special and int(num) > 10:
                en_word = special[int(num) % 10]
            elif int(num) == 1:
                en_word = "first"
            else:
                base = words
                en_word = special.get(int(num), base + en_ord)
            return en_word
        if kind == "score":
            a, b = re.split(r"[-/]", s)   # "2-1" lẫn "2/1"
            return _vi_score(a, b) if route == "vi" else f"{en_digits(a)} {en_digits(b)}"
        if kind == "slash_digits":   # "3/4" -> "ba trên bốn" (trang/slide), en "slash"
            a, b = s.split("/")
            joiner = " trên " if route == "vi" else " slash "
            return number_to_words(a, route) + joiner + number_to_words(b, route)
        if kind == "compound_rate":   # "4.2L/100km" -> "bốn phẩy hai lít trên một trăm ki lô mét"
            n1, u1, n2, u2 = t["groups"]

            def _u(x):
                e = dicts.units().get(x.lower())
                return (e[0] if route == "vi" else e[1]) if e else x

            joiner = " trên " if route == "vi" else " per "
            left = _read_side(n1.replace(".", ",") if route == "vi" else n1, route)
            right = _read_side(n2.replace(".", ",") if route == "vi" else n2, route)
            return f"{left} {_u(u1)}{joiner}{right} {_u(u2)}"
        if kind == "slash_plain":   # "18/0", "93/2026", "9/0/21", "05/47/81" -> từng chữ số
            return " ".join((vi_digits if route == "vi" else en_digits)(p)
                            for p in s.split("/"))
        if kind == "decade_suffix":   # en "in his 50s" -> "fifties"
            w = en_cardinal(int(t["groups"][0]))
            return (w[:-1] + "ies") if w.endswith("y") else w + "s"
        if kind == "decade":   # "1980s" -> "nineteen eighties" (thập kỷ en)
            base = en_year(int(s.rstrip("sS")) // 10 * 10)
            if base.endswith("y"):
                base = base[:-1] + "ies"   # eighty -> eighties
                return base
            return base + "s"
        if kind == "plus":
            a, b = t["groups"]
            joiner = " cộng " if route == "vi" else " plus "
            return number_to_words(a, route) + joiner + number_to_words(b, route)
        if kind == "fraction":
            a, b = s.split("/")
            b_w = "tư" if b == "4" else number_to_words(b, "vi")   # "1/4" -> "một phần tư"
            return f"{number_to_words(a, 'vi')} phần {b_w}"
        if kind == "neg_decimal":
            a = t["groups"][0]
            m = re.fullmatch(r"(\d+)[.,](\d+)", a)
            if m:
                joiner = " phẩy " if route == "vi" else " point "
                body = number_to_words(m.group(1), route) + joiner + _decimal_part(m.group(2), route)
            else:
                body = number_to_words(a, route)
            return ("âm " if route == "vi" else "minus ") + body
        if kind == "version":   # "2.4.1" -> "hai chấm bốn chấm một";
                                # "2.4.0-rc1" -> "..., r c một";
                                # "2.1.0-beta" -> "..., bê ta"
            base, suf, num = s, "", ""
            m_suf = re.search(r"-(rc|beta|alpha|dev|snapshot)(\d*)$", s, re.I)
            if m_suf:
                base, suf, num = (s[: m_suf.start()], m_suf.group(1).lower(),
                                  m_suf.group(2))
            joiner = " chấm " if route == "vi" else " point "
            out = joiner.join(number_to_words(p, route) for p in base.split("."))
            if m_suf:
                suf_rd = {"rc": ", r c", "beta": ", bê ta" if route == "vi"
                          else ", beta",
                          "alpha": ", an pha" if route == "vi"
                          else ", alpha",
                          "dev": ", đét" if route == "vi" else ", dev",
                          "snapshot": ", s náp sọt" if route == "vi"
                          else ", snapshot"}[suf]
                rd = (vi_digits(num) if route == "vi" else en_digits(num)) \
                    if num else ""
                out += suf_rd + ((" " + rd) if rd else "")
            return out
        if kind == "ver":   # "v1.4" -> "v một phẩy bốn" (vi); "v one point four" (en)
            joiner = " phẩy " if route == "vi" else " point "
            return "v " + joiner.join(number_to_words(p, route) for p in t["groups"][0].split("."))
        if kind == "slash_decimals":   # "4.8/5.0" -> "bốn phẩy tám trên năm"
            a, b = s.split("/")
            mb = re.fullmatch(r"(\d+)[.,](\d+)", b)
            if mb and set(mb.group(2)) == {"0"}:
                right = number_to_words(mb.group(1), route)   # "5.0" -> "năm"
            else:
                right = _read_side(b.replace(".", ",") if route == "vi" else b, route)
            joiner = " trên " if route == "vi" else " out of "
            return _read_side(a.replace(".", ",") if route == "vi" else a, route) + joiner + right
        if kind == "interval":
            a, b = s.split("-")
            if route != "vi" and re.fullmatch(r"(1[4-9]|20)\d{2}", a) \
                    and re.fullmatch(r"(1[4-9]|20)\d{2}", b):
                return f"{en_year(int(a))} to {en_year(int(b))}"   # "(1895-1984)" kiểu cặp năm
            return _vi_interval(a, b) if route == "vi" else f"{number_to_words(a, 'en')} to {number_to_words(b, 'en')}"
        if kind == "year":
            return number_to_words(s, route, "year")
        if kind == "cardinal" and s.isdigit() and len(s) >= 7:
            # số dài 7+ chữ số là ID (link, mã bài đăng) -> đọc từng chữ số, không đọc "mười chín triệu..."
            return vi_digits(s) if route == "vi" else en_digits(s)
        if kind == "en_day":
            return en_day_ordinal(int(s))
        if kind == "digits":
            return vi_digits(s) if route == "vi" else en_digits(s)
        return number_to_words(s, route, "cardinal")
    if cat == "money":
        if t.get("kind") == "prefix":
            return _verbal_money_prefix(s[0], s[1:], route)
        if t.get("kind") == "suffix":
            return _verbal_money_prefix("$", s[:-1], route)
        return number_to_words(s, route)
    if cat == "date":
        return _verbal_date(t, route, prev_surface.lower())
    if cat == "time":
        return _verbal_time(s, t.get("kind", "colon"), t.get("groups"), route)
    if cat == "phone":
        groups = re.split(r"[\s.\-]+", s.strip())
        return " , ".join(vi_digits(g) if route == "vi" else en_digits(g) for g in groups)
    if cat == "email":
        return _verbal_email(s, route)
    if cat == "url":
        return _verbal_url(s, route)
    if cat == "abbr":
        if t.get("kind") == "quarter":
            return "quý" if route == "vi" else "q"
        if t.get("kind") == "qu":
            return dicts.abbrev().get("q", ("quận", ""))[0]
        fl = s.rstrip(".").lower()
        if fl in dicts.abbrev():
            return dicts.abbrev()[fl][0]
        return " ".join(list(s.rstrip(".").upper()))
    if cat == "acronym":
        return " ".join(list(s.upper()))
    if cat == "slang":
        entry = dicts.slang().get(s.lower())
        return entry[0] if entry else s
    if cat == "unit":
        if t.get("kind") == "million":
            return "triệu" if route == "vi" else "million"
        if t.get("kind") == "p_res":
            return "pờ"   # "720p" độ phân giải
        u = dicts.units().get(s.lower())
        if u:
            return u[0] if route == "vi" else u[1]
        return s
    if cat == "pm_am":
        w = t["groups"][0]
        if route == "vi":
            return "chiều" if w == "pm" else "sáng"
        return "p m" if w == "pm" else "a m"
    if cat == "icon":
        concept = dicts.ICONS.get(s) or dicts.ICONS.get(s.lower())
        if concept:
            vi_s, en_s = dicts.ICON_READ[concept]
            return vi_s if route == "vi" else en_s
        return ""
    # word
    if t.get("kind") == "mention":   # "@handle" -> "a còng handle" / "at handle"
        handle = re.sub(r"_+", " ", t["groups"][0])
        return ("a còng " if route == "vi" else "at ") + handle
    if t.get("kind") == "filename":   # "2_final.pdf" -> "hai final chấm P D F"
        base, ext = t["groups"]
        parts = []
        for p in base.split("_"):
            parts.append(number_to_words(p, route) if p.isdigit() else p)
        dot = "chấm" if route == "vi" else "dot"
        return f"{' '.join(parts)} {dot} {' '.join(ext.upper())}"
    if re.fullmatch(r"[A-Za-z]\+\+", s):
        return f"{s[0]} cộng cộng"
    if re.fullmatch(r"[A-Za-z]#", s):
        return f"{s[0]} thăng"
    if "_" in s:   # snake_case ("report_v", "user_id") — gạch nối không đọc, tách từ
        return s.replace("_", " ")
    if t.get("_shout") or t.get("_caps_word"):
        return s.capitalize()
    if route == "en" and ("'" in s or "\u02bc" in s):
        return _expand_contractions(s)
    return s
