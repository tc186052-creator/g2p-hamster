"""Số → chữ đọc: tiếng Việt, tiếng Anh, digit mode, năm, thập phân.

Tất cả hàm thuần (pure), deterministic.
"""
import re

VI_DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
EN_DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
EN_SMALL = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
            "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
            "eighteen", "nineteen"]
EN_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
EN_GROUPS = [(10 ** 12, "trillion"), (10 ** 9, "billion"), (10 ** 6, "million"),
             (10 ** 3, "thousand")]

INT_RE = re.compile(r"^\d{1,12}$")


# ---------------------------------------------------------------- vi
def _vi_under_100(n: int) -> str:
    if n < 10:
        return VI_DIGITS[n]
    tens, unit = divmod(n, 10)
    if tens == 1:
        if unit == 0:
            return "mười"
        if unit == 5:
            return "mười lăm"
        return f"mười {VI_DIGITS[unit]}"
    base = f"{VI_DIGITS[tens]} mươi"
    if unit == 0:
        return base
    if unit == 1:
        return f"{base} mốt"
    if unit == 5:
        return f"{base} lăm"
    return f"{base} {VI_DIGITS[unit]}"


def _vi_under_1000(n: int) -> str:
    if n < 100:
        return _vi_under_100(n)
    h, rest = divmod(n, 100)
    s = f"{VI_DIGITS[h]} trăm"
    if rest == 0:
        return s
    if rest < 10:
        return f"{s} lẻ {VI_DIGITS[rest]}"
    return f"{s} {_vi_under_100(rest)}"


def vi_cardinal(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + vi_cardinal(-n)
    if n >= 10 ** 15:   # quá nhóm cao nhất "nghìn tỷ" (tối đa 999·10^12) — nhóm đầu
        return vi_digits(str(n))   # q = n//10^12 >= 1000 làm _vi_under_1000 IndexError
    parts = []
    spoken = False
    for value, name in ((10 ** 12, "nghìn tỷ"), (10 ** 9, "tỷ"), (10 ** 6, "triệu"),
                        (10 ** 3, "nghìn")):
        if n >= value:
            q, n = divmod(n, value)
            # luật "không trăm" chỉ áp dụng cho nhóm sau nhóm đầu tiên
            parts.append(f"{(_vi_group(q) if spoken else _vi_under_1000(q))} {name}")
            spoken = True
    if n:
        parts.append(_vi_group_tail(n) if spoken else _vi_under_1000(n))
    return " ".join(parts)


def _vi_group(q: int) -> str:
    """Nhóm trăm giữa câu: hàng trăm = 0 thì đọc 'không trăm'."""
    if q >= 100:
        return _vi_under_1000(q)
    if q >= 10:
        return f"không trăm {_vi_under_100(q)}"
    return f"không trăm lẻ {VI_DIGITS[q]}"


def _vi_group_tail(n: int) -> str:
    """Phần đuôi sau nhóm lớn nhất: 2021 -> 'không trăm hai mươi mốt'."""
    if n >= 100:
        return _vi_under_1000(n)
    if n >= 10:
        return f"không trăm {_vi_under_100(n)}"
    return f"không trăm lẻ {VI_DIGITS[n]}"


def vi_digits(s: str) -> str:
    return " ".join(VI_DIGITS[int(c)] for c in s if c.isdigit())


def vi_decimal(int_part: str, frac_part: str) -> str:
    return f"{vi_cardinal(int(int_part))} phẩy {' '.join(VI_DIGITS[int(c)] for c in frac_part)}"


VI_MONTHS = ["một", "hai", "ba", "tư", "năm", "sáu", "bảy", "tám", "chín", "mười",
             "mười một", "mười hai"]


# ---------------------------------------------------------------- en
def _en_under_100(n: int) -> str:
    if n < 20:
        return EN_SMALL[n]
    tens, unit = divmod(n, 10)
    return EN_TENS[tens] + (" " + EN_SMALL[unit] if unit else "")


def _en_under_1000(n: int) -> str:
    if n < 100:
        return _en_under_100(n)
    h, rest = divmod(n, 100)
    s = f"{EN_SMALL[h]} hundred"
    if rest:
        s += " " + _en_under_100(rest)
    return s


def en_cardinal(n: int) -> str:
    if n == 0:
        return "zero"
    if n < 0:
        return "minus " + en_cardinal(-n)
    if n >= 10 ** 15:   # q = n//10^12 >= 1000: _en_under_1000 đọc sai ("ten hundred
        return en_digits(str(n))   # trillion") hoặc IndexError (>= 10^16)
    parts = []
    for value, name in EN_GROUPS:
        if n >= value:
            q, n = divmod(n, value)
            parts.append(f"{_en_under_1000(q)} {name}")
    if n:
        parts.append(_en_under_1000(n))
    return " ".join(parts)


def en_digits(s: str) -> str:
    return " ".join(EN_DIGITS[int(c)] for c in s if c.isdigit())


def en_decimal(int_part: str, frac_part: str) -> str:
    return f"{en_cardinal(int(int_part))} point {' '.join(EN_DIGITS[int(c)] for c in frac_part)}"


def en_year(n: int) -> str:
    """Đọc năm kiểu en: 1990 -> nineteen ninety; 2005 -> two thousand five; 2021 -> twenty twenty one."""
    if n < 1000:
        return en_cardinal(n)
    if n == 2000:
        return "two thousand"
    h, tail = divmod(n, 100)
    if tail == 0:
        return f"{_en_under_100(h)} hundred"
    if n < 2000 or n >= 2010:
        return f"{_en_under_100(h)} {_en_under_100(tail)}"
    return en_cardinal(n)  # 2000..2009: two thousand five


EN_MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
             "september", "october", "november", "december"]


# ---------------------------------------------------------------- parse helpers
def split_number(s: str, route: str):
    """Tách chuỗi số thành (int_part, frac_part) hoặc ('group', int) theo route + locale.

    vi: '.' ngăn cách nghìn (1.335 -> group), ',' hoặc '.' thập phân (1,59 / 1.21 -> decimal)
    en: ',' ngăn cách nghìn (1,335 -> group), '.' thập phân (3.14 -> decimal)
    Trả về ('group', int) | ('dec', int_part, frac) | ('plain', int) | None nếu không hợp lệ.
    """
    s = s.replace(" ", "")
    if not re.fullmatch(r"\d{1,3}([.,]\d+)+|\d+", s):
        return None
    if "." in s and "," in s:
        # "28,650.170" / "1,004.080.000": nhóm CUỐI là thập phân, mọi nhóm trước là nghìn
        pieces = re.split(r"[.,]", s)
        if len(pieces) >= 3 and all(len(p) == 3 for p in pieces[1:-1]) and len(pieces[0]) <= 3:
            return ("dec", "".join(pieces[:-1]), pieces[-1])
        return None
    if "." in s or "," in s:
        sep = "." if "." in s else ","
        pieces = s.split(sep)
        if route == "vi" and sep == "." and all(len(p) == 3 for p in pieces[1:]) and len(pieces[0]) <= 3:
            return ("group", int(s.replace(".", "")))
        if route == "en" and sep == "," and all(len(p) == 3 for p in pieces[1:]) and len(pieces[0]) <= 3:
            return ("group", int(s.replace(",", "")))
        if route == "vi" and sep == "," and len(pieces) == 2 \
                and len(pieces[0]) <= 3 and len(pieces[1]) == 3:
            return ("group", int(s.replace(",", "")))   # "3,281" = ba nghìn hai trăm...
        if len(pieces) == 2 and 0 < len(pieces[1]) <= 8:
            return ("dec", pieces[0], pieces[1])
        return None
    return ("plain", int(s))


def number_to_words(s: str, route: str, kind: str = "cardinal") -> str:
    """kind: cardinal | decimal | digits | year."""
    if route == "vi":
        if kind == "digits":
            return vi_digits(s)
        r = split_number(s, "vi")
        if r is None:
            return vi_digits(re.sub(r"\D", "", s))
        if r[0] == "dec":
            return vi_decimal(r[1], r[2])
        n = r[1]
        if kind == "year":
            return vi_cardinal(n)
        return vi_cardinal(n)
    else:
        if kind == "digits":
            return en_digits(s)
        r = split_number(s, "en")
        if r is None:
            return en_digits(re.sub(r"\D", "", s))
        if r[0] == "dec":
            return en_decimal(r[1], r[2])
        n = r[1]
        if kind == "year":
            return en_year(n)
        return en_cardinal(n)
