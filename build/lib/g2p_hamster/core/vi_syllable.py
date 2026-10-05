# -*- coding: utf-8 -*-
"""vi_syllable.py — parser chữ → record ViSyllable (fase B).

parse() là HÀM THUẦN: mỗi chính tả hợp lệ → đúng 1 record (master IDs ham/0.1).
Chính tả không phân tích được → ParseError (caller quyết spell/deferred — fase D).

Trạng thái thanh điệu ở MỨC RECORD (schema §4/3.3 — không bao giờ "âm thầm"):
  "diacritic" — tone đọc từ dấu, nguồn sự thật;
  "policy"    — chữ không dấu đọc nguyên dạng = TONE_NGANG (chính sách bảo toàn
                đã duyệt ở A4; KHÔNG phải mặc định câm);
  "fold"      — skeleton phân giải bằng fold_vi.tsv (prior tần suất);
  "unresolved" — chưa có cơ sở: transform profile TỪ CHỐI serialize (phải phân
                 giải trước), không được âm thầm unstressed/ngang.
"""
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from . import inventory  # noqa: E402
from .profiles import ViSyllable  # noqa: E402
from . import vi_rules as R  # noqa: E402


class ParseError(ValueError):
    """Chính tả không parse được thành âm tiết vi (caller quyết spell)."""


def parse(text):
    """Chính tả 1 âm tiết → ViSyllable. Ném ParseError nếu không phân tích được.

    F05 (vòng 4): HÀM THUẦN — KHÔNG nhận fold. parse chỉ phân tích chính tả đã
    chọn; resolver fold (chọn ứng viên có dấu, fase D) là lớp gọi riêng, provenance
    "fold" do resolver gắn. Một tham số fold tùy chọn ở đây sẽ âm thầm sửa cả âm
    tiết hợp lệ nhóm (a) (vd nam) và phá cam kết bảo toàn — đã tách.
    """
    s = unicodedata.normalize("NFC", text.strip().lower())
    skeleton, ti = R.strip_tone(s)
    if skeleton is None:
        raise ParseError(f"quá 1 dấu thanh: {text!r}")
    p = R.parse_skeleton(skeleton)
    if p is None:
        raise ParseError(f"không parse được: {text!r} (skeleton {skeleton!r})")
    onset, glide_letter, form, tail = p
    if ti != 1:
        tone, tone_state = R.TONE_BY_INDEX[ti], "diacritic"
    else:
        tone, tone_state = "TONE_NGANG", "policy"   # chính sách đọc nguyên dạng (A4)
    onset_ids, glide_ids, nuc, coda_id, flags = R.record_parts(onset, glide_letter, form, tail)
    if tail and coda_id is None:
        raise ParseError(f"tail lạ {tail!r}: {text!r}")
    # luật lõi 4.6.5: coda tắc (p/t/k) chỉ đi với sắc/nặng — chữ không dấu + tắc
    # KHÔNG phải âm tiết chuẩn ("mach") → ParseError; nhánh fold (ỦY QUYỀN, có hợp
    # đồng riêng) mới được chọn ứng viên có dấu và phát âm theo ứng viên đó.
    if coda_id in ("PHONE_P", "PHONE_T", "PHONE_K") and tone not in ("TONE_SAC", "TONE_NANG"):
        raise ParseError(f"coda tắc yêu cầu sắc/nặng, nhận {tone} — {text!r} "
                         f"không phải âm tiết chuẩn (nhánh fold/spell phải xử lý)")
    syl = ViSyllable(onset=onset_ids, glide=glide_ids, nucleus=nuc,
                     coda=(coda_id,) if coda_id else (), tone=tone,
                     tone_state=tone_state, source_graphemes=text,
                     flags=frozenset(flags))
    return syl


def skeleton_of(text):
    """→ (skeleton, tone_index) — dùng cho collision matcher (không raise)."""
    return R.strip_tone(unicodedata.normalize("NFC", text.strip().lower()))


def parse_word(text):
    """Tách theo ký tự không phải chữ vi; mỗi token → record hoặc None (spell).

    Token là chuỗi ký tự chữ liên tiếp (category L). KHÔNG có fold — token không
    parse được trả None cho spell/fold path của fase D.
    """
    out, cur = [], ""
    for ch in unicodedata.normalize("NFC", text.lower()):
        if unicodedata.category(ch).startswith("L"):
            cur += ch
        elif cur:
            try:
                out.append((cur, parse(cur)))
            except ParseError:
                out.append((cur, None))
            cur = ""
    if cur:
        try:
            out.append((cur, parse(cur)))
        except ParseError:
            out.append((cur, None))
    return out
