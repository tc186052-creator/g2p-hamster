"""Từ điển T0: kho quyết (vi/en), kho bắt, slang, viết tắt, đơn vị, icon, policy ký tự."""
import csv
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data"

# một âm tiết tiếng Việt: phụ âm đầu + MỘT vùng nguyên âm + phụ âm cuối (t/ng/nh/ch/m/n/p/c)
_SYLL_RE = re.compile(r"[bcdfghjklmnpqrstvxzđ]*"
                      r"[aeiouyàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]+"
                      r"(?:nh|ch|ng|[cmnptgdx])?")


@lru_cache(maxsize=1)
def _lines(name: str) -> tuple:
    return tuple((DATA / name).read_text(encoding="utf-8").split())


@lru_cache(maxsize=1)
def _tsv(name: str) -> tuple:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    return tuple(tuple(r) for r in rows[1:] if r and r[0])


@lru_cache(maxsize=1)
def kho_bat() -> frozenset:
    return frozenset(_lines("kho_bat.txt"))


@lru_cache(maxsize=1)
def kho_quyet_vi() -> frozenset:
    # lọc cấu trúc giống syllables: chặn từ tiếng Anh/thương hiệu nhiễm vào từ corpus
    # ("rating", "album", "acer"...) — kq_vi được check TRƯỚC kq_en nên nhiễm là nghiêm trọng
    return frozenset(w for w in _lines("kho_quyet_vi.txt")
                     if w and all(_SYLL_RE.fullmatch(part) for part in w.split()))


@lru_cache(maxsize=1)
def kho_quyet_en() -> frozenset:
    return frozenset(_lines("kho_quyet_en.txt"))


@lru_cache(maxsize=1)
def kho_en_cmudict() -> frozenset:
    """Từ điển EN mở rộng 126.052 từ — sinh từ cmudict 0.7b pin của tầng 2
    (02_hamster_G2P/03_vendor/cmudict). Xem provenance cùng thư mục data/
    (kho_en_cmudict_GHI_CHU.md) và hồ sơ lỗi route:
    02_hamster_G2P/06_train_t3/data/mix3/HO_SO_LOI_ROUTE_MIX.md.
    KHÔNG có trong kq_en (4.625 từ 'chắc chắn') — dùng làm NHÁNH TRA CỨU:
    chỉ chốt route en khi từ KHÔNG phải âm tiết VI hợp lệ (xem detect.assign_routes)."""
    return frozenset(_lines("kho_en_cmudict.txt"))


@lru_cache(maxsize=1)
def syllables_vi() -> frozenset:
    # lọc cấu trúc: chặn từ đa âm tiết nhiễm vào từ corpus ("author", "hauser", "german")
    return frozenset(s for s in _lines("syllables_vi.txt") if _SYLL_RE.fullmatch(s))


@lru_cache(maxsize=1)
def slang() -> dict:
    return {r[0]: (r[1], r[2] if len(r) > 2 else "") for r in _tsv("slang_vi.tsv")}


@lru_cache(maxsize=1)
def abbrev() -> dict:
    return {r[0].lower(): (r[1], r[2] if len(r) > 2 else "") for r in _tsv("abbrev_vi.tsv")}


@lru_cache(maxsize=1)
def units() -> dict:
    """key -> (verbal_vi, verbal_en, kind)."""
    return {r[0].lower(): (r[1], r[2], r[3] if len(r) > 3 else "unit") for r in _tsv("units.tsv")}


@lru_cache(maxsize=1)
def spell_exceptions() -> frozenset:
    """Acronym ALL-CAPS phải gõ từng chữ (detect.caps_kind). File cho phép dòng # chú thích."""
    return frozenset(
        l.split()[0] for l in (DATA / "spell_exceptions.txt").read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.startswith("#"))


@lru_cache(maxsize=1)
def char_policy() -> dict:
    """char -> (action, target). action: keep|read|drop|drop_log|normalize."""
    out = {}
    for r in _tsv("char_policy.tsv"):
        ch, action = r[0], r[4]
        if action.startswith("normalize:"):
            out[ch] = ("normalize", action.split(":", 1)[1].strip("'\""))
        else:
            out[ch] = (action, "")
    return out


def apply_policy_char(c: str):
    """Trả về (keep, replacement, action). Ký tự ngoài bảng: chữ/số/khoảng trắng = keep."""
    entry = char_policy().get(c)
    if entry is None:
        if c.isalnum() or c == " ":
            return True, c, "keep"
        return False, "", "drop_log"
    action, target = entry
    if action == "normalize":
        return True, target, action
    if action in ("keep", "read"):
        return True, c, action
    return False, "", action  # drop | drop_log


# ---- icon/emoticon: surface -> khái niệm (cột đọc vi/en nằm trong ICON_READ) ----
ICON_READ = {
    "laugh": ("cười", "laughs"),
    "cry": ("khóc", "crying"),
    "love": ("yêu", "love"),
    "skeptical": ("á à", "hmm"),
    "sad": ("buồn", "sad"),
    "angry": ("tức giận", "angry"),
}
ICONS = {
    "=))": "laugh", "=)": "laugh", ":))": "laugh", ":)": "laugh", ":d": "laugh", "xd": "laugh",
    "😂": "laugh", "😄": "laugh", "🙂": "laugh", "🤣": "laugh",
    "=((": "cry", ":((": "cry", "T_T": "cry", "T.T": "cry", ":'(": "cry",
    "😭": "cry", "😢": "cry", "☹": "sad", ":(": "sad",
    "<3": "love", "❤": "love", "❤️": "love", "💕": "love",
    ":/": "skeptical", ":3": "skeptical", "🤨": "skeptical",
    ">:(": "angry", "😡": "angry",
}


def fold(s: str) -> str:
    """Bỏ dấu thanh (giết -> giet) và quy đ -> d (file âm tiết lưu dạng này).
    Nằm ở dicts vì textproc và detect cùng dùng, detect import textproc
    nên không thể đặt ngược lại."""
    import unicodedata
    return ("".join(c for c in unicodedata.normalize("NFD", s)
                    if not unicodedata.combining(c))
            .replace("đ", "d").replace("Đ", "D"))
