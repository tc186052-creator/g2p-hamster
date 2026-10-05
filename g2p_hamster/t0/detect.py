"""Phát hiện span (email/url/phone/date/time/money/number/abbr) + LID + gán route."""
import re

from . import dicts, textproc
from .textproc import ABBREV_DOT

VI_MARKS = set("ăâêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵđĐ")

RE_URL = re.compile(r"^(https?://[a-z0-9\-]+(/[^\s]*)?|(https?://)?(www\.)?[a-z0-9\-]+(\.[a-z0-9\-]{2,})+(:\d+)?(/[^\s]*)?)$", re.I)
RE_URL_SHORT_FAKE = re.compile(r"^[a-z]{1,4}\.[a-z]{1,4}$", re.I)   # "Sr.TE" — đoạn quá ngắn, không phải domain
KNOWN_TLDS = {"com", "net", "org", "vn", "edu", "gov", "info", "biz", "gl", "ly",
              "io", "ai", "co", "uk", "jp", "kr", "de", "fr", "ru", "tv", "me"}
RE_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
RE_PHONE_TOK = re.compile(r"^\+?\d[\d\s.\-]*$")
RE_DATE_YMD = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
RE_DATE_MY = re.compile(r"^\d{1,2}/\d{4}$")
RE_DATE_DM = re.compile(r"^\d{1,2}/\d{1,2}$")
RE_TIME_H = re.compile(r"^(\d{1,2})h(\d{0,2})(p?)$", re.I)
RE_TIME_COLON = re.compile(r"^(\d{1,2}):(\d{2})(:(\d{2}))?(am|pm)?$", re.I)
RE_INTERVAL = re.compile(r"^(\d{1,4})-(\d{1,4})$")
RE_INTERVAL_GROUPED = re.compile(r"^\d{1,3}(?:[.,]\d+)?-\d{1,3}(?:[.,]\d+)?$")   # 440.000-740.000, 139,5-143,5, 7,6-9
RE_DATE_HYPHEN = re.compile(r"^\d{1,2}-\d{1,2}-\d{2,4}$")
RE_DATE_DOT = re.compile(r"^(\d{1,2})\.(\d{1,2})(\.(\d{2,4}))?$")
RE_DATE_HYPHEN_DM = re.compile(r"^(\d{1,2})-(\d{1,2})$")
RE_DATE_RANGE = re.compile(r"^(\d{1,2})-(\d{1,2})/(\d{1,2})$")
RE_NUM_GROUP = re.compile(r"^\d{1,3}([.,]\d{3})+$")
RE_NUM_DEC = re.compile(r"^\d+[.,]\d+$")
RE_NUM_MIXED = re.compile(r"^\d{1,3}([.,]\d{3})+[.,]\d{1,6}$")
RE_NUM_PLAIN = re.compile(r"^\d+$")
RE_ORDINAL = re.compile(r"^(\d{1,4})(st|nd|rd|th)$", re.I)
RE_MONEY_PREFIX = re.compile(r"^[$€£¥](\d{1,12}([.,]\d+)?)([BMKbmk])?$")
RE_MONEY_SUFFIX = re.compile(r"^(\d{1,3}(?:[.,] ?\d{3})+|\d{1,15})( ?đồng| ?đ|vnđ|vnd|\$)$",
                             re.I)
RE_ABBR_DOT = re.compile(r"^([A-Za-zÀ-ỹĐđ]+)\.$")
def is_caps(s: str) -> bool:
    """ALL-CAPS 2-6 ký tự (đúng nghĩa hoa, không đụng chữ thường vi như 'đó')."""
    return 2 <= len(s) <= 6 and s.isalpha() and s == s.upper()


RE_ROMAN = re.compile(r"^[IVXLCDM]{2,}$")
_ROMAN_VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_value(s: str):
    """Chuỗi roman hợp lệ -> giá trị; ngược lại None. Round-trip để chặn MIX/DI giả roman."""
    total, prev = 0, 0
    for c in reversed(s):
        v = _ROMAN_VAL[c]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    def canon(n):
        out = ""
        for value, sym in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
                           (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
                           (5, "V"), (4, "IV"), (1, "I")):
            while n >= value:
                out += sym
                n -= value
        return out
    return total if canon(total) == s else None


SPELL_EXCEPTIONS = {"UNESCO", "UNICEF", "IELTS", "HIV", "GDP", "CEO", "CFO", "CTO", "AEW",
                    "ODA", "FDI", "IMF", "WTO", "ADB", "JICA", "NGO", "API", "SEO",
                    "AQI", "OLED", "LLM", "CRM", "CPI", "ESOP"}
# phiên bản data file (02_rules/t0/data/spell_exceptions.txt) — nguồn chung cho detect + tools
SPELL_EXCEPTIONS = dicts.spell_exceptions() or SPELL_EXCEPTIONS
# từ viết tắt đọc được như từ thường (không gõ từng chữ)
PRONOUNCE_ACRONYM = {"SMART", "GPS", "GIS"}

# tháng Anh: viết tắt + đầy đủ — dùng cho "Feb. 13" -> "February thirteenth"
EN_MONTH_WORDS = {"january", "february", "march", "april", "may", "june", "july",
                  "august", "september", "october", "november", "december",
                  "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept",
                  "oct", "nov", "dec"}
# viết tắt mở được ngay cả trong câu en (tháng + hậu tố công ty)
EN_OK_ABBREV = EN_MONTH_WORDS | {"inc", "llc", "ltd", "corp"}
# từ đứng trước số 3 chữ số -> đó là MÃ vật liệu/máy ("inox 430" đọc "bốn ba không")
MODEL_NUM_WORDS = {"inox", "thep", "model", "seri", "series", "ma"}


def caps_kind(s: str) -> str:
    """Phân loại ALL-CAPS: shouting-vi | word (đọc được) | roman | spell."""
    if any(c.casefold() in VI_MARKS and c != "Đ" for c in s):
        return "shouting_vi"          # TỜ, KHÔNG... -> chữ viết hoa than phèn, đọc như từ thường
    if s.upper() in SPELL_EXCEPTIONS:
        return "spell"
    if s in PRONOUNCE_ACRONYM:
        return "word"
    if RE_ROMAN.match(s):
        v = roman_value(s)
        if v is not None and 2 <= v <= 100:
            return "roman"            # XIII, IV, IX... (xét TRƯỚC 'word' vì I/V là nguyên âm)
    letters = [c for c in s if c.isalpha()]
    vowels = sum(1 for c in letters if c.lower() in "aeiouy")
    if len(letters) >= 3 and vowels >= 2 and vowels / len(letters) >= 0.4:
        return "word"                 # COVID, LONA, NASA... đọc được như từ thường
    return "spell"                    # SSO, IELTS, ATTT...

MONEY_UNIT_WORDS = {"usd", "eur", "vnd", "đồng", "đ", "bảng", "yên", "usd."}
FOOTBALL = {"tỉ", "thắng", "thua", "bại", "hạ", "hoà", "hòa", "đánh bại", "win", "beat"}
# fold() không gỡ được "đ" (U+0111) -> phải kèm cả biến thể "đau".
# CỤM "dẫn trước"/"tỷ số" khớp dạng bigram trên chuỗi window — từ đơn "dẫn" va chạm "dân số"
FOOTBALL_FOLD = {"ti", "ty", "thang", "thua", "bai", "ha", "hoa", "dau", "đau",
                 "danh bai", "win", "beat"}
FOOTBALL_BIGRAM = {"dan truoc", "đan truoc", "ti so", "ty so"}
YEAR_WORDS = {"năm", "vào", "since", "in", "year", "the"}
# "1/4" đứng cạnh những từ này -> phân số, không phải ngày 1 tháng 4
FRACTION_CTX_WORDS = {"con", "chiem", "hoan thanh", "trong", "cua", "gan",
                      "khoang", "hon", "chi", "toan", "so luong", "phan", "it",
                      "het", "ngon", "ngan", "khau", "khau tru",
                      # từ tín hiệu liều lượng/phân bổ ("uống 1/4 viên thuốc",
                      # "chia 1/2 số hàng", "bơm 1/3 bình", "giảm 1/2 giá") — không phải ngày
                      "uong", "chia", "bom", "pha", "lieu", "moi", "lan",
                      "giam", "tang", "chiet khau"}
DATE_CTX_WORDS = {"ngay", "mung", "thang", "nam", "vao", "duong", "am", "tu",
                  "den", "lich"}
# từ en kế trước "50s" -> thập kỷ ("in his 50s", "the late 90s")
EN_DECADE_CTX = {"his", "her", "the", "their", "its", "in", "late", "early",
                 "since", "by", "during", "age", "aged"}


def has_diacritic(s: str) -> bool:
    return any(c in VI_MARKS for c in s)


import functools

from .dicts import fold   # fold (bỏ dấu) đã chuyển về dicts — giữ tên ở đây cho compat
fold = functools.lru_cache(maxsize=200000)(fold)


def sent_lang(word_surfaces) -> str:
    n_vi = sum(1 for t in word_surfaces if has_diacritic(t))
    kq_en, kq_vi = dicts.kho_quyet_en(), dicts.kho_quyet_vi()
    n_en = sum(1 for t in word_surfaces if fold(t).lower() in kq_en and fold(t).lower() not in kq_vi)
    if n_vi and n_en:
        return "mixed"
    if n_vi:
        return "vi"
    if n_en:
        return "en"
    # toàn ASCII, không từ khóa nào: đếm từ LẠ (không phải âm tiết vi) —
    # "Gayelord Hauser author" không có từ điển nào nhận -> phải là tiếng Anh,
    # không được mặc định đọc vi ("author" thành "au-tơ" kiểu vi)
    if re.search(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", " ".join(word_surfaces)):
        return "mixed"   # câu CJK — không áp heuristic tiếng Anh
    syll = dicts.syllables_vi()
    wordish = [t for t in word_surfaces if re.search(r"[A-Za-zà-ỹđĐ]", t)]
    n_unknown = sum(1 for t in wordish
                    if fold(t).lower() not in syll and fold(t).lower() not in kq_vi)
    if wordish and n_unknown >= max(2, (len(wordish) + 1) // 2):
        return "en"
    return "mixed"


def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s)


def detect(spans_in, config):
    """spans_in: list dict token thô từ tokenize(). Trả về list dict token có cat + meta detect.

    Chỉ phân loại category + gắn cờ; verbal + route do verbalize/pipeline làm tiếp.
    """
    toks = [dict(t, cat=t.get("cat", "raw"), review=None) for t in spans_in]
    n = len(toks)
    low = [t["surface"].lower() for t in toks]
    sent = sent_lang([t["surface"] for t in toks if t["cat"] in WORDISH + ("raw",)])

    def mark(i, cat, **kw):
        toks[i].update(kw, cat=cat)

    # 1) email / url (token nguyên vẹn từ tokenizer)
    for i, t in enumerate(toks):
        if t["cat"] == "raw":
            s = t["surface"]
            if RE_EMAIL.match(s):
                mark(i, "email", read="spell")
            elif RE_URL.match(s) and re.search(r"[a-zA-Z]", s) \
                    and not (RE_URL_SHORT_FAKE.match(s)
                             and s.rsplit(".", 1)[-1].lower() not in KNOWN_TLDS) \
                    and not (s[0].isdigit() and not s.lower().startswith(("http", "www"))):
                # "4.2L/100km" trông như domain nhưng là đơn vị ghép số — để nhánh sau đọc
                mark(i, "url", read="spell")

    # 2) phone: chuỗi token digits+seps liền kề, tổng 9-11 số (12-13 nếu đầu 84 = mã nước),
    #    bắt 0/+84; nhận cả mã vùng trong ngoặc "(84-511)"
    RE_PHONE_PAREN = re.compile(r"^\(\+?\d{2,4}([\-\s]?\d{1,4})?\)$")
    i = 0
    while i < n:
        s_i = toks[i]["surface"]
        if toks[i]["cat"] == "raw" and (RE_PHONE_TOK.match(s_i) or RE_PHONE_PAREN.match(s_i)) \
                and _digits_only(s_i):
            j, parts, last_part = i, [], i
            while j < n:
                t = toks[j]
                if t["cat"] == "raw" \
                        and (RE_PHONE_TOK.match(t["surface"]) or RE_PHONE_PAREN.match(t["surface"])) \
                        and _digits_only(t["surface"]):
                    parts.append(re.sub(r"[()]", "", t["surface"]))
                    last_part = j
                    j += 1
                elif t["cat"] == "punct" and t["surface"] in "()" and j > i:
                    j += 1               # cầu qua "(" ")" giữa các nhóm số, không skip nó
                else:
                    break
            joined = " ".join(parts)
            digits = _digits_only(joined)
            is_phone = ((9 <= len(digits) <= 11
                         and (digits.startswith("0") or joined.startswith("+84")))
                        or (12 <= len(digits) <= 13 and digits.startswith("84")))
            if is_phone:
                for k in range(i, last_part + 1):
                    if toks[k]["cat"] == "raw":
                        toks[k]["cat"] = "skip"
                mark(i, "phone", surface=joined, _span=(i, last_part))
                i = last_part + 1
            else:
                i = j
        else:
            i += 1

    for i, t in enumerate(toks):
        if t["cat"] != "raw":
            continue
        s = t["surface"]
        low_ = s.lower()
        prev_low = low[i - 1] if i else ""
        next_low = low[i + 1] if i + 1 < n else ""

        # 2b) @handle ("@keantoan", "@quoc_minh") -> "a còng ..." / "at ..."
        # (email đã xử lý ở mục 1; đây là mention không có domain)
        if re.fullmatch(r"@([A-Za-z0-9_.]{2,30})", s):
            mark(i, "word", kind="mention", groups=(s[1:],))
            continue
        # 2c) tên file có đuôi ("2_final.pdf", "bai_tap.docx") -> đọc từng khúc + "chấm p d f"
        if re.fullmatch(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*\.(?:"
                        r"pdf|docx?|xlsx?|pptx?|csv|txt|zip|rar|7z|mp[34]|avi|mkv|mov|"
                        r"jpe?g|png|gif|html?|apk|exe|msi|iso|epub|key)", s, re.I):
            base, ext = s.rsplit(".", 1)
            mark(i, "word", kind="filename", groups=(base, ext.lower()))
            continue

        # 3) date
        # số nhóm nghìn "5.000.000", "99.000", "1.000.000.000" — mọi nhóm
        # sau đều đúng 3 chữ số → là SỐ, phải xét TRƯỚC version (regex
        # version \d+(\.\d+){2,3} khớp luôn "5.000.000"!)
        if RE_NUM_GROUP.match(s):
            mark(i, "number", kind="cardinal", _pct=(next_low == "%"))
            continue
        # nhóm số cách space "1 000 000" (ít gặp, nhưng tokenizer giữ
        # nguyên thành 1 token) — đọc là một số, không đọc từng nhóm
        m_spacegrp = re.fullmatch(r"\d{1,3}( \d{3})+", s)
        if m_spacegrp:
            mark(i, "number", kind="cardinal", _pct=(next_low == "%"))
            continue
        # "1 000 000 đồng" — tokenizer tách space nên tới đây thành nhiều
        # token; gộp lại thành MỘT số khi ngay sau là đơn vị tiền
        if re.fullmatch(r"\d{1,3}", s):
            j = i + 1
            while j < n and toks[j]["cat"] == "raw" \
                    and re.fullmatch(r"\d{3}", toks[j]["surface"]):
                j += 1
            if j > i + 1 and j < n \
                    and toks[j]["surface"].lower() in ("đ", "đồng", "vnđ", "vnd"):
                joined = "".join(toks[k]["surface"] for k in range(i, j))
                for k in range(i + 1, j):
                    toks[k]["cat"] = "skip"
                mark(i, "number", kind="cardinal", surface=joined, _money_adj=True)
                continue
        # version phần mềm "2.4.1", "2.4.1-rc2", "2.1.0-beta", "1.0.0-alpha2"
        # (3-4 nhóm số chấm nhau + hậu tố rc/beta/alpha/dev/snapshot,
        # không đứng sau từ ngày)
        if re.fullmatch(r"\d+(\.\d+){2,3}(-(?:[rR][cC]|beta|alpha|dev|snapshot)\d*)?",
                        s, re.I) and prev_low not in ("ngày", "mùng", "vào"):
            mark(i, "number", kind="version", route="en" if sent == "en" else "vi")
            continue
        # "v1.4", "v2.0" -> "v một phẩy bốn" (trong câu Việt, không lật en theo chữ "v")
        m_ver = re.fullmatch(r"[vV](\d+(?:\.\d+)+)", s)
        if m_ver:
            mark(i, "number", kind="ver", groups=(m_ver.group(1),),
                 route="en" if sent == "en" else "vi")
            continue
        # điểm số thập phân "4.8/5.0"
        if re.fullmatch(r"\d+[.,]\d+/\d+[.,]\d+", s):
            mark(i, "number", kind="slash_decimals")
            continue
        # đơn vị ghép "4.2L/100km", "10km/L" -> "bốn phẩy hai lít trên một trăm ki lô mét"
        m_cr = re.fullmatch(r"(\d+(?:[.,]\d+)?)([a-zđ°]{1,6})/(\d+(?:[.,]\d+)?)([a-zđ]{1,6})", s, re.I)
        if m_cr:
            mark(i, "number", kind="compound_rate", groups=m_cr.groups(),
                 route="en" if sent == "en" else "vi")
            continue
        m_dot = RE_DATE_DOT.match(s)
        if m_dot and (prev_low in ("ngày", "mùng", "vào")
                      or (i >= 2 and low[i - 1] in ("(", "ngày")
                          and (low[i - 2] == "ngày" or (low[i - 1] == "(" and low[i - 2] == "(")))):
            d, m_ = int(m_dot.group(1)), int(m_dot.group(2))
            if 1 <= d <= 31 and 1 <= m_ <= 12:
                mark(i, "date", kind="dmy_dot" if m_dot.group(3) else "dm_dot",
                     groups=m_dot.groups())
                continue
        m_hdm = RE_DATE_HYPHEN_DM.match(s)
        if m_hdm:
            a, b = int(m_hdm.group(1)), int(m_hdm.group(2))
            is_duong_lich = (next_low == "dương" and i + 2 < n and low[i + 2].startswith("lịch"))
            if (a > 12 >= b and 1 <= b) or is_duong_lich:   # "31-10" hoặc "6-2 dương lịch"
                mark(i, "date", kind="dm_hyphen", groups=m_hdm.groups())
                continue
        if RE_DATE_YMD.match(s):
            parts = s.split("/")
            if len(parts) == 3 and 1 <= int(parts[1]) <= 12:
                mark(i, "date", kind="dmy")
                continue
            mark(i, "number", kind="slash_plain")
            continue
        if RE_DATE_MY.match(s) and prev_low == "tháng":
            mark(i, "date", kind="my")
            continue
        m_dm = RE_DATE_DM.match(s)
        if m_dm and prev_low in ("ngày", "mùng", "ngày,"):
            mark(i, "date", kind="dm")
            continue
        if RE_DATE_MY.match(s) and re.fullmatch(r"\d{1,2}/(19|20)\d{2}", s) \
                and 1 <= int(s.split("/")[0]) <= 12:   # "93/2026" là số văn bản, KHÔNG phải tháng 93
            mark(i, "date", kind="my_span")
            continue
        if RE_DATE_MY.match(s) and prev_low == "số":
            mark(i, "number", kind="slash_plain")   # "số 93/2026" -> "chín ba hai không hai sáu" (digits)
            continue
        if m_dm:
            a_s, b_s = s.split("/")
            a, b = int(a_s), int(b_s)
            window = [fold(w) for w in low[max(0, i - 3):i] + low[i + 1:i + 4]]
            window_str = " ".join(window)
            is_score = (any(w in window for w in FOOTBALL_FOLD)
                        or any(bb in window_str for bb in FOOTBALL_BIGRAM))
            frac_hit = any(w in window for w in FRACTION_CTX_WORDS if " " not in w) \
                or any(w in window_str for w in FRACTION_CTX_WORDS if " " in w)
            date_hit = any(w in window for w in DATE_CTX_WORDS)
            if is_score:
                mark(i, "number", kind="score")   # "tỉ số 2/1" -> "hai, một" (không phải ngày!)
            elif (prev_low == "vòng" or "vong" in window) and 1 <= a < b:
                mark(i, "number", kind="fraction")   # "vòng 1/16", "vòng loại 1/4"
            elif a < b and frac_hit and not date_hit:
                mark(i, "number", kind="fraction")   # "Chỉ còn 1/4 số hàng", "hoàn thành 1/4 công việc"
            elif prev_low in ("trang", "slide", "bước") and a <= b:
                mark(i, "number", kind="slash_digits")   # "trang 3/4" -> "ba trên bốn", không phải ngày
            elif 1 <= a <= 31 and 1 <= b <= 12:
                mark(i, "date", kind="dm", review=None)
            else:
                mark(i, "number", kind="slash_plain")   # "18/0" mác thép, mã lạ -> đọc từng chữ số
            continue
        # 4) time
        m_plus = re.fullmatch(r"(\d{1,4})\+(\d{1,4})", s)
        if m_plus:   # "90+1" phút bù giờ bóng đá, "2+2" phép cộng
            mark(i, "number", kind="plus", groups=m_plus.groups())
            continue
        m = RE_TIME_H.match(s)
        if m:
            mark(i, "time", kind="h", groups=m.groups())
            continue
        m = RE_TIME_COLON.match(s)
        if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
            mark(i, "time", kind="colon", groups=m.groups())
            continue
        # 5) date kiểu gạch nối 28-11-2015 (trước khi nhầm interval)
        if RE_DATE_HYPHEN.match(s):
            mark(i, "date", kind="dmy_hyphen")
            continue
        # 5b) khoảng ngày "3-9/12" -> ba đến chín tháng mười hai
        m = RE_DATE_RANGE.match(s)
        if m:
            if 1 <= int(m.group(3)) <= 12:
                mark(i, "date", kind="range_dm", groups=m.groups())
            else:   # "1-5/33" mã quầy/địa chỉ -> đọc từng chữ số, không phải tháng 33
                mark(i, "number", kind="slash_plain",
                     surface=s.replace("-", "/"))
            continue
        # 6) interval / tỉ số (so khớp đã bỏ dấu — "tỷ" và "tỉ" là một)
        # "vòng 1/16" -> phân số "một phần mười sáu", không phải tỉ số/khoảng
        if prev_low == "vòng" and re.fullmatch(r"\d{1,2}/\d{1,2}", s):
            a_s, b_s = s.split("/")
            if 1 <= int(a_s) < int(b_s):
                mark(i, "number", kind="fraction")
                continue
        m = RE_INTERVAL.match(s)
        if m:
            window = [fold(w) for w in low[max(0, i - 3):i] + low[i + 1:i + 4]]
            window_str = " ".join(window)
            is_score = (any(w in window for w in FOOTBALL_FOLD)
                        or any(b in window_str for b in FOOTBALL_BIGRAM))
            mark(i, "number", kind="score" if is_score else "interval")
            continue
        # 6a) khoảng số nhóm "440.000-740.000" (tiền, số lượng)
        if RE_INTERVAL_GROUPED.match(s):
            mark(i, "number", kind="interval")
            continue
        # 6) money có ký hiệu
        if RE_MONEY_PREFIX.match(s):
            mark(i, "money", kind="prefix")
            continue
        m_money = RE_MONEY_SUFFIX.match(s)
        if m_money:
            mark(i, "money", kind="suffix",
                 groups=(m_money.group(1), m_money.group(2).strip()))
            continue
        # số âm "-3.2"
        m_neg = re.fullmatch(r"-(\d+(?:[.,]\d+)?)", s)
        if m_neg:
            mark(i, "number", kind="neg_decimal", groups=(m_neg.group(1),))
            continue
        # 6b) số thứ tự 10th, 21st
        m = RE_ORDINAL.match(s)
        if m:
            mark(i, "number", kind="ordinal", groups=m.groups())
            continue
        # 7) number thường (năm nếu ngữ cảnh 'năm'; ngày en nếu đứng sau tháng "Feb. 13")
        m_decade = re.fullmatch(r"(1[4-9]\d\d|20\d\d)s", s, re.I)
        if m_decade and sent == "en":   # "the late 1980s" -> "the late nineteen eighties"
            mark(i, "number", kind="decade")
            continue
        if RE_NUM_GROUP.match(s) or RE_NUM_DEC.match(s) or RE_NUM_MIXED.match(s) or RE_NUM_PLAIN.match(s):
            k = i - 1
            while k >= 0 and low[k] == ".":
                k -= 1                    # "Feb." -> tokenizer tách "Feb" + "."; bỏ chấm khi tìm tháng
            prev_word = low[k].rstrip(".") if k >= 0 else ""
            is_year = (prev_low in YEAR_WORDS or prev_word in EN_MONTH_WORDS) \
                and RE_NUM_PLAIN.match(s) and len(s) == 4
            is_en_day = (not is_year and RE_NUM_PLAIN.match(s) and s.isdigit()
                         and 1 <= int(s) <= 31 and prev_word in EN_MONTH_WORDS)
            is_model = (not is_year and not is_en_day and RE_NUM_PLAIN.match(s)
                        and len(s) == 3 and fold(prev_word) in MODEL_NUM_WORDS)
            kind = ("year" if is_year else "en_day" if is_en_day
                    else "digits" if is_model else "cardinal")
            # số 7+ chữ số đứng cạnh đơn vị tiền ("1000000đ" -> tokenizer
            # tách "đ" riêng) là SỐ TIỀN, không phải mã/link -> đọc thang
            # nghìn/triệu/tỷ, không đọc từng chữ số
            is_money_adj = (kind == "cardinal" and s.isdigit() and len(s) >= 7
                            and next_low in ("đ", "đồng", "vnđ", "vnd"))
            mark(i, "number", kind=kind, _pct=(next_low == "%"),
                 _money_adj=is_money_adj)
            continue
        # 7b) đơn vị/tiền tệ đứng sau số ("100 USD") — xét trước ALL-CAPS
        # "in his 50s" (en): số 1-2 chữ + s là THẬP KỶ, không phải giây
        if low_ == "s" and i > 0 and toks[i - 1].get("cat") == "number" \
                and re.fullmatch(r"\d{1,2}", toks[i - 1]["surface"]) \
                and (sent == "en" or (i > 1 and low[i - 2] in EN_DECADE_CTX)):
            toks[i - 1]["cat"] = "skip"   # "50" bị nuốt, chỉ "s" đọc "fifties"
            mark(i, "number", kind="decade_suffix", groups=(toks[i - 1]["surface"],))
            continue
        if (low_ in dicts.units()
                and (not t["surface"].isupper() or low_ in ("mbps", "°c"))
                and i > 0 and toks[i - 1].get("cat") == "number"):
            mark(i, "unit", origin="neu", route="en" if sent == "en" else "vi")
            if low_ == "đ":
                t["review"] = "don_vi_d"   # "1đ" = đồng (giá) hay điểm (thi)? -> rà tay
            continue
        # 8) viết tắt có chấm (TP.) hoặc all-caps (ĐT, HCM, UBND)
        # chữ cái đơn kề "/" ("P/E", "M/F") -> gõ chữ, không đọc thành từ Việt ("phường")
        if len(s) == 1 and s.isascii() and s.isalpha() and s.isupper() \
                and i > 0 and toks[i - 1].get("surface") == "/":
            mark(i, "acronym")
            continue
        if len(s) == 1 and s.isascii() and s.isalpha() and s.isupper() \
                and i + 1 < n and toks[i + 1].get("surface") == "/":
            mark(i, "acronym")
            continue
        # "Q3" -> mặc định "quý ba"; chỉ đọc "quận" khi ngữ cảnh ĐỊA CHỈ quanh nó
        if s.upper() == "Q" and i + 1 < n and low[i + 1] in ("1", "2", "3", "4"):
            win_q = [fold(w) for w in low[max(0, i - 4):i] + low[i + 2:i + 5]]
            winq_str = " ".join(win_q)
            dia_chi = (any(w in win_q for w in ("tp", "quan", "phuong", "duong", "hcm", "hanoi",
                                                "khuc", "kcn", "dia chi", "thi xa", "thi tran"))
                       or any(b in winq_str for b in ("quan ", "phuong ")))
            mark(i, "abbr", kind="qu" if dia_chi else "quarter")
            continue
        # "M" HOA ngay sau số ("1.5M câu") -> triệu; "5m" thường thì mét (qua units)
        if s == "M" and i > 0 and toks[i - 1].get("cat") == "number":
            mark(i, "unit", kind="million", route="en" if sent == "en" else "vi")
            continue
        # "720p" độ phân giải: số 3-4 chữ + p -> đọc "pờ", KHÔNG phải "5p" = 5 phút
        if low_ == "p" and i > 0 and toks[i - 1].get("cat") == "number" \
                and re.fullmatch(r"\d{3,4}", toks[i - 1]["surface"]):
            mark(i, "unit", kind="p_res", route="en" if sent == "en" else "vi")
            continue
        m = RE_ABBR_DOT.match(s)
        if m and m.group(1).lower() in ABBREV_DOT:
            mark(i, "abbr", _consume_dot=True)
            continue
        if is_caps(s):
            kind = caps_kind(s)
            if kind == "shouting_vi":
                mark(i, "word", origin="vi", route="vi", _shout=True)
                continue
            if low_ in dicts.abbrev() and (sent != "en" or low_ in EN_OK_ABBREV):
                mark(i, "abbr")
                continue
            if kind == "word":
                mark(i, "word", _caps_word=True, review="caps_word")
                continue
            if kind == "roman":
                mark(i, "number", kind="roman", groups=[s])
                continue
            mark(i, "acronym" if not (sent != "en" and False) else "abbr")
            continue
        if low_ in dicts.abbrev() and (sent != "en" or low_ in EN_OK_ABBREV):
            mark(i, "abbr")
            continue
        # 10) còn lại: symbol có luật đọc / punct / slang / icon / word
        if s in ("-",):
            mark(i, "punct")
            continue
        if s in ("&", "+", "=", "@", "#", "°", "<", ">", "|", "~", "^", "\\") or s in "$€£¥₫":
            mark(i, "symbol")
            continue
        if low_ in dicts.slang() and not (
                len(low_) == 1 and i > 0 and toks[i - 1].get("cat") == "number") \
                and not (len(s) == 1 and s.isupper()) \
                and not (low_ == "e" and next_low.startswith("rằng")) \
                and not (low_ == "e" and i + 1 < n and toks[i + 1].get("surface") == "-"):   # "e-commerce", không phải "e" = "em"
            mark(i, "slang")
        elif s in dicts.ICONS or s.lower() in {k.lower() for k in dicts.ICONS}:
            mark(i, "icon")
        else:
            mark(i, "word")

    # 8b) merge "3/2022" -> date tháng/năm (số 1-12 + / + năm 19xx|20xx)
    i = 0
    while i < len(toks) - 2:
        a, slash, b = toks[i], toks[i + 1], toks[i + 2]
        if (a["cat"] == "number" and a.get("kind") == "cardinal" and a["surface"].isdigit()
                and 1 <= int(a["surface"]) <= 12 and slash["cat"] == "punct" and slash["surface"] == "/"
                and b["cat"] == "number" and re.fullmatch(r"(19|20)\d{2}", b["surface"])):
            for k in (i + 1, i + 2):
                toks[k]["cat"] = "skip"
            mark(i, "date", kind="my_span", surface=f"{a['surface']}/{b['surface']}")
            i += 3
            continue
        i += 1

    # 8c) PM/AM (cả "p.m", "a.m.") đứng sau time/số giờ -> "chiều"/"sáng" (vi), "p m"/"a m" (en)
    for i, t in enumerate(toks):
        pm = re.sub(r"\.$", "", t["surface"].lower())
        if t["cat"] in ("word", "acronym", "abbr") and pm in ("pm", "am", "p.m", "a.m") \
                and i > 0 and toks[i - 1]["cat"] in ("time", "number"):
            mark(i, "pm_am", groups=["pm" if pm.startswith("p") else "am"],
                 origin="neu", route="en" if sent == "en" else "vi")

    # 9) % đi kèm số -> symbol đọc; money đơn vị kề
    for i, t in enumerate(toks):
        if t["cat"] == "punct" and t["surface"] == "%" and i > 0 and toks[i - 1]["cat"] == "number":
            t["cat"] = "symbol"
    # 9b) đơn vị sau gạch chéo ("events/s", "mb/s", "km/s") -> unit ("giây"…),
    #     không để rơi thành OOV đọc "per s"
    for i, t in enumerate(toks):
        if i >= 2 and t["cat"] in ("raw", "word") and t["surface"].lower() in dicts.units() \
                and toks[i - 1]["cat"] == "punct" and toks[i - 1]["surface"] == "/" \
                and toks[i - 2]["cat"] in ("number", "word", "abbr", "acronym", "unit"):
            left = toks[i - 2]
            rt = left.get("route") if left.get("route") in ("vi", "en") else None
            rt = rt or ("en" if sent == "en" else "vi")
            mark(i, "unit", origin="neu", route=rt)
            # cụm "X/Y" là một nhóm_rate: gạch đọc theo ngôn ngữ của unit ("trên giây"),
            # không theo láng giềng trái ("events" en -> "per giây" lệch hai bên)
            toks[i - 1]["route"] = rt
    return [t for t in toks if t["cat"] != "skip"]


# ---------------------------------------------------------------- route
WORDISH = ("word", "abbr", "acronym", "slang")


def assign_routes(toks, config):
    """Gán origin + route cho word token. Số/punct/symbol -> origin=neu, route kế thừa."""
    kq_vi, kq_en, kbat = dicts.kho_quyet_vi(), dicts.kho_quyet_en(), dicts.kho_bat()
    syll = dicts.syllables_vi()
    cmu = dicts.kho_en_cmudict()
    n = len(toks)

    # pass 0: câu
    if not toks:
        return toks
    word_surfs = [t["surface"] for t in toks if t["cat"] in WORDISH + ("raw",)]
    sent = sent_lang(word_surfs)
    toks[0]["sent_lang"] = sent

    # pass 1: quyết định chắc chắn
    for pi, t in enumerate(toks):
        if t["cat"] in WORDISH:
            s = t["surface"]
            fl = fold(s).lower()
            if t["cat"] == "slang":
                t["origin"], t["route"] = "vi", "vi"
            elif has_diacritic(s):
                t["origin"], t["route"] = "vi", "vi"
            elif fl in kq_vi and t["cat"] != "acronym":
                # ALL-CAPS ("IP") không được kq_vi chốt — acronym phải hỏi theo câu
                t["origin"], t["route"] = "vi", "vi"
            elif fl in kq_en:
                t["origin"], t["route"] = "en", "en"
            elif t["cat"] == "word" and s.isascii() and fl not in syll \
                    and (fl in cmu or (len(s) > 1 and s[:1].isupper())):
                # [VA 02/10/2026] NHÁNH TRA CỨU cmudict + tên riêng — vá nhóm lỗi
                # "từ EN trong câu VI bị kéo về vi" (kho_bat/tiny1 phán sai, hoặc
                # kế thừa sent_lang): audio syn_mix đọc các từ này kiểu Anh
                # (~80/20, không phiên âm hóa — chủ dự án xác nhận 02/10).
                # Điều kiện chặn: KHÔNG phải 1 âm tiết VI hợp lệ ("la","ba","san"
                #… giữ nguyên) + cat word (không đụng abbr/acronym/slang) +
                # không nằm kq_vi (nhánh trên đã xử trước).
                # Flag review "cmudict_en": pass 2/3 KHÔNG dùng token này làm
                # nguồn kế thừa cho token trung tính (số/ký hiệu vẫn đọc vi theo
                # láng giềng cũ — "Arsenal 2-1" -> "hai, một"), nhưng word token
                # vẫn route en. Hồ sơ: 02_hamster_G2P/06_train_t3/data/mix3/
                #   HO_SO_LOI_ROUTE_MIX.md, sim_fix_route.py (syn_mix 4,1%->73,5%).
                t["origin"], t["route"] = "en", "en"
                t["review"] = t.get("review") or "cmudict_en"
            elif t["cat"] == "acronym":
                t["origin"] = "neu"
                t["route"] = "vi" if sent == "vi" else sent if sent != "mixed" else config.default_route
                t["review"] = t.get("review") or "acronym_spell"
            elif fl in kbat:
                t["route"] = None  # chờ model / heuristic
                t["review"] = "kho_bat"
            elif fl in syll:
                # mạo từ tiếng Anh "a" trong câu en/mixed — không phải "a" tiếng Việt
                if fl == "a" and sent != "vi":
                    t["origin"], t["route"] = "en", "en"
                # "i" trước một từ không-thể-là-âm-tiết-Việt ("i dont know") là I tiếng Anh
                elif fl == "i" and sent != "vi":
                    for j in range(pi + 1, min(pi + 3, n)):
                        nt = toks[j]
                        if nt["cat"] not in WORDISH:
                            break
                        nf = fold(nt["surface"]).lower()
                        if has_diacritic(nt["surface"]):
                            break
                        if nf not in syll and nf not in kq_vi:
                            t["origin"], t["route"] = "en", "en"
                            break
                if t.get("route") is None:
                    t["origin"], t["route"] = "vi", "vi"
            else:
                if sent == "mixed":
                    t["route"] = None   # pass 2 hỏi láng giềng ("dont" cạnh "know" -> en)
                else:
                    t["origin"] = "en"
                    t["route"] = "en" if sent == "en" else config.default_route
                t["review"] = "oov"
    # pass 2+: heuristic cho kho bắt — láng giềng đã quyết gần nhất.
    # [VA 02/10/2026] bỏ qua nguồn láng giềng là token do nhánh cmudict route en
    # (review "cmudict_en") — các token này MỚI en, không được kéo số/ký hiệu
    # trung tính theo ("Arsenal 2-1" giữ "hai, một"); từ en CŨ (kq_en…) vẫn là
    # nguồn kế thừa như trước ("December 25, 2014" vẫn đọc en trong câu mixed).
    changed = True
    while changed:
        changed = False
        for i, t in enumerate(toks):
            if t["cat"] not in WORDISH or t.get("route") is not None:
                continue
            pick = None
            for d in range(1, n):
                for j in (i - d, i + d):
                    if 0 <= j < n and toks[j]["cat"] in WORDISH \
                            and toks[j].get("route") in ("vi", "en") \
                            and toks[j].get("review") != "cmudict_en":
                        pick = toks[j]["route"]
                        break
                if pick:
                    break
            if pick is None:
                pick = sent if sent != "mixed" else config.default_route
            t["route"] = pick
            t["origin"] = pick
            t["review"] = t.get("review") or "kho_bat_heuristic"
            changed = True

    # pass 3: token trung tính kế thừa route của láng giềng wordish gần nhất (trái ưu tiên),
    # hết đường thì route câu; không review. [VA 02/10/2026] bỏ qua nguồn là
    # token "cmudict_en" (xem pass 2).
    for i, t in enumerate(toks):
        if t.get("route") is not None:
            continue
        pick = None
        for d in range(1, n):
            for j in (i - d, i + d):
                if 0 <= j < n and toks[j]["cat"] in WORDISH \
                        and toks[j].get("route") in ("vi", "en") \
                        and toks[j].get("review") != "cmudict_en":
                    pick = toks[j]["route"]
                    break
            if pick:
                break
        t["route"] = pick or (sent if sent != "mixed" else config.default_route)
        t.setdefault("origin", "neu" if t["cat"] not in WORDISH else t["route"])
    # pass 3.5: câu thuần Anh — số/đơn vị/ngày/giờ đọc theo tiếng Anh, kể cả khi
    # từ kề bị syll-dict kéo sang vi ("Hauser (1895-1984)" trong câu en)
    if sent == "en":
        for i, t in enumerate(toks):
            if t["cat"] in ("number", "unit", "pm_am", "money", "time", "date") \
                    and t.get("route") == "vi":
                near = [toks[j] for d in (1, 2) for j in (i - d, i + d)
                        if 0 <= j < n and toks[j]["cat"] in WORDISH]
                if near and any(x.get("route") == "en" for x in near) \
                        and not any(has_diacritic(x["surface"]) for x in near):
                    t["route"] = "en"
                    if t["cat"] == "number" and t.get("kind") in ("", "cardinal") \
                            and re.fullmatch(r"(1[4-9]|20)\d{2}", t["surface"]):
                        t["kind"] = "year"   # "1750" trong câu en -> "seventeen fifty"
    # [VA 02/10/2026] KHÔNG thêm pass flip số/ký hiệu về vi ở đây: v1 của patch
    # đã thử và PHÁ VỠ các đoạn EN cố ý trong câu mixed (ngày "December 25, 2014",
    # "11 point one zero in" — chuẩn khóa đọc EN). Cơ chế đúng là nguồn-skip ở
    # pass 2/3: từ en MỚI (cmudict_en) không kéo láng giềng trung tính.
    return toks
