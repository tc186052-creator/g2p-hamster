"""Pipeline T0: text -> IR. Deterministic, không randomness, không model lớn.

Dùng:  from t0 import normalize, Config
       ir = normalize("một câu", Config())
       ir["read_string"]  -> chuỗi đọc; ir["tokens"] -> IR token theo spec 0.1
"""
import re
from dataclasses import dataclass, field

from . import dicts, detect, textproc, verbalize

BREAK = {".": "major", "!": "major", "?": "major", "…": "major", ",": "minor",
         ";": "minor", ":": "minor", "-": "minor"}

# dấu câu nào được GIỮ trong chuỗi đọc (đã chuẩn hóa) — quyết định "giữ dấu nào, mapping như nào":
#   , ; : . ! ? … - " ' ( ) /  -> giữ nguyên dạng chuẩn
#   ( ) giữ để nhìn ranh giới ý; mọi dấu khác (theo char_policy) đã bị normalize/drop từ clean()
PUNCT_KEEP = set('.,;:!?…-()/')   # bo nhay don/kep roi: chi gay nhieu

# cặp xưng hô có "/" giữa: đọc bỏ dấu ("/" không phải "trên"): "Anh/chị vui lòng" -> "anh chị"
_XUNG_HO = {"anh", "chị", "em", "bạn", "ông", "bà", "mình", "chú", "cô", "dì",
            "cậu", "tôi", "họ", "ta", "chúng ta"}


@dataclass
class Config:
    icon_policy: str = "remove"          # remove | read
    default_route: str = "vi"
    en_year_style: str = "pair"          # pair | cardinal
    flags: dict = field(default_factory=dict)


def normalize(text: str, config: Config | None = None) -> dict:
    """T0 chuẩn hóa LUẬT THUẦN — deterministic hoàn toàn, cùng đầu vào luôn ra
    cùng IR. (Máy trọng tài tiny đã bỏ khỏi bản open-source: luật + bảng từ
    điển là đủ cho nhánh G2P; token mơ hồ vẫn kèm trường `review` để tầng sau
    truy vết và chốt bằng từ điển.)"""
    return _rules_normalize(text, config or Config())


def _rules_normalize(text: str, config: Config) -> dict:
    config = config or Config()
    clean, logs = textproc.clean(text)
    raw_toks = textproc.tokenize(clean)
    toks = [t for t in detect.detect(raw_toks, config) if t["cat"] != "skip"]
    toks = detect.assign_routes(toks, config)

    tokens, reviews, read_parts = [], [], []
    nospace_next = False
    prev_surface = ""
    for i, t in enumerate(toks):
        verbal = verbalize.verbal_token(t, prev_surface)
        if t["cat"] == "punct" and t["surface"] == "/" and verbal == "/":
            # tỉ suất "đồng/cổ phần" -> đọc "trên"; đầu/cuối câu hoặc kề punct -> im lặng
            pc = toks[i - 1]["cat"] if i else ""
            nc = toks[i + 1]["cat"] if i + 1 < len(toks) else ""
            if "acronym" in (pc, nc):
                verbal = ""   # "HIV/AIDS", "A/B testing", "P/E" -> gõ chữ, không đọc "trên"
            elif (pc == "word" and nc == "word" and i > 0 and i + 1 < len(toks)
                    and toks[i - 1]["surface"][:1].isupper()
                    and toks[i + 1]["surface"][:1].isupper()):
                verbal = ""   # "Axure/Fireworks" danh sách tên riêng -> ngắt im lặng
            elif (pc == "word" and nc == "word"
                    and toks[i - 1]["surface"].lower() in _XUNG_HO
                    and toks[i + 1]["surface"].lower() in _XUNG_HO):
                verbal = ""   # "Anh/chị vui lòng" -> "anh chị", không đọc "trên"
            elif pc in ("word", "abbr", "unit", "number", "money") and nc in ("word", "abbr", "unit", "number", "money"):
                if pc == "number" and nc == "number":
                    # "1750/1754" hai số thuần: en đọc "slash", vi giữ "trên"
                    verbal = "slash" if t.get("route") == "en" else "trên"
                else:
                    # "mg/dl" tiếng Anh -> "per"; tiếng Việt -> "trên" — slash cũng phải hỏi ngôn ngữ
                    verbal = "per" if t.get("route") == "en" else "trên"
        if t["surface"].upper() == "CP" and i >= 2 and t["cat"] in ("abbr", "acronym", "word") \
                and toks[i - 1]["surface"] == "-" and toks[i - 2]["surface"].upper().rstrip(".") == "NĐ":
            verbal = "chính phủ"   # "72/2015/NĐ-CP" -> CP là CHÍNH PHỦ, không phải cổ phần
        # "$100 million" -> "one hundred million dollars" (từ chỉ bậc đứng TRƯỚC đơn vị)
        if t["cat"] == "money" and i + 1 < len(toks):
            nxt = toks[i + 1]["surface"].lower().rstrip(".,;:")
            num = re.sub(r"\D", "", t["surface"])
            if num and nxt in ("million", "billion", "trillion") and t.get("route") == "en":
                verbal = f"{verbalize.number_to_words(num, 'en')} {nxt} dollars"
                t["_swallow_next"] = True
            elif num and nxt in ("triệu", "tỷ", "nghìn tỷ"):
                verbal = f"{verbalize.number_to_words(num, 'vi')} {nxt} đô la"
                t["_swallow_next"] = True
        if i > 0 and toks[i - 1].get("_swallow_next"):
            verbal = ""   # "million"/"triệu" đã nằm trong câu đọc của token tiền ở trước
        if t["surface"] == "#" and (i == 0 or i + 1 >= len(toks)):
            verbal = ""   # "#" đầu/cuối câu (đánh dấu đoạn hát) -> bỏ, không đọc "dấu thăng"
        # dấu chấm ngay sau viết tắt (GS. TP. p.m.) là chấm của viết tắt — bỏ, không phải ngắt câu
        if (t["cat"] == "punct" and t["surface"] == "." and i > 0
                and toks[i - 1]["cat"] in ("abbr", "pm_am")):
            # pm_am: chỉ nuốt khi còn chữ phía sau (chấm là remainder của "p.m.");
            # chấm cuối câu giữ nguyên để không mất ngắt nghỉ
            if toks[i - 1]["cat"] == "abbr" or (
                    i + 1 < len(toks) and toks[i + 1]["cat"] != "punct"):
                verbal = ""
        if t["cat"] == "icon" and config.icon_policy == "remove":
            verbal = ""
        entry = {
            "i": i,
            "surface": t["surface"],
            "cat": t["cat"] if t["cat"] != "symbol" else ("number" if t.get("_pct") else "symbol"),
            "origin": t.get("origin", "neu"),
            "route": t.get("route", config.default_route),
            "read": t.get("read", "word"),
            "verbal": verbal,
            "group": -1,
            "break": BREAK.get(t["surface"]) if t["cat"] == "punct" else None,
            "review": t.get("review"),
        }
        if t["cat"] == "punct" and t["surface"] == "?":
            entry["intonation"] = "rising"
        if t.get("_pct"):
            entry["verbal"] = verbal  # số giữ verbal; % là token riêng
        if entry["verbal"] == "" and entry["cat"] == "punct" and t["surface"] == "." \
                and i > 0 and toks[i - 1]["cat"] in ("abbr", "pm_am"):
            entry["break"] = None
        tokens.append(entry)
        if t.get("review"):
            reviews.append({"i": i, "surface": t["surface"], "reason": t["review"]})
        # gạch nối nằm trong một từ ("V-League") dính sát 2 bên; gạch độc lập
        # giữa các từ ("Hòa Khánh - Hầm") giữ dấu + break minor như nguồn
        if t["cat"] == "punct" and t["surface"] == "-" and t.get("glue") and read_parts:
            read_parts[-1] += "-"
            nospace_next = True
        elif verbal:
            if nospace_next and read_parts:
                read_parts[-1] += verbal
            else:
                read_parts.append(verbal)
            nospace_next = False
        prev_surface = t["surface"]

    # nối số + %: "9,1" "%" -> đọc liền "chín phẩy một phần trăm"
    read_string = _join_read(read_parts)
    return {
        "schema": "ir/0.1",
        "text": text,
        "clean": clean,
        "sent_lang": toks[0].get("sent_lang", "mixed") if toks else "mixed",
        "tokens": tokens,
        "review": reviews,
        "logs": logs,
        "read_string": read_string,
    }


def _join_read(parts):
    """Nối verbal thành chuỗi đọc: dấu câu dính sát từ như văn bản thường."""
    s = " ".join(x for x in parts if x)
    s = re.sub(r"\s+([,.;:!?…%)])", r"\1", s)   # dấu dính sát từ trước
    s = re.sub(r"\(\s+", "(", s)                  # "(" dính từ sau
    s = re.sub(r"\s+/", "/", s)                   # "/" dính 2 bên (tỉ suất)
    s = re.sub(r"/\s+", "/", s)
    return re.sub(r" +", " ", s).strip()


