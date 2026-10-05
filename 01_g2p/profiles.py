# -*- coding: utf-8 -*-
"""profiles.py — khung profile export (A3, đặc tả 4.9).

Profile = adapter NHẬN THỨC CẤU TRÚC từ record âm tiết (onset/glide/nucleus/coda/tone,
tất cả là master ID ham/0.2) ra chuỗi cho một acoustic frontend cụ thể.

Profile `kokoro178` (debug adapter cho checkpoint Kokoro n_token=178):
  1. Segment map MẤT THÔNG TIN CÓ CHỦ ĐÍCH (loss_report):
       ɓ→b · ɗ→d · ʐ→ʒ · tʰ→θ · ɝ→ɚ (vocab 178 không có ɝ — phát hiện A3)
     token khác giữ nguyên unicode (đơn vị nhiều code point serialized thành từng ký tự).
  2. Tone transform: TONE_* → mũi tên chèn TRƯỚC âm cuối (coda nếu có, không thì sau
     nucleus); ngã/nặng thêm ʔ; NGANG không đánh dấu [V] (bảng 4.6.1 + pin doc).
  3. En: chèn ˈ/ˌ TRƯỚC nucleus theo stress.
  4. Cleanup theo frontend (hook — hiện identity).
  5. Conformance: TỪNG KÝ TỰ output phải thuộc 114 mục vocab (n_token 178).

Bất biến thay round-trip (4.9): I2 (determinism + conformance) và I3-PROFILE
(loss chỉ được phép trên profile_required_contrasts — kiểm ở E1, fase E).

Đầu vào là RECORD — parser chữ→record là vi_rules (fase B), không thuộc file này.
"""
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "01_g2p"))
import inventory  # noqa: E402

PROFILE_NAME = "kokoro178"
PROFILE_VERSION = "kokoro178/0.2"   # 0.2 vòng 6.3: khai loss PHONE_OPEN_E_PREVELAR (R12-02)
VOCAB_TSV = HERE / "02_data" / "profiles" / "kokoro_vocab_178.tsv"

# ---------------------------------------------------------------- record đầu vào


@dataclass(frozen=True)
class ViSyllable:
    """Record âm tiết vi — master IDs (ham/0.2). tone bắt buộc trừ khi unresolved."""
    onset: tuple = ()      # tuple[str] — segment IDs, vd ("PHONE_TR",) / ("PHONE_N","PHONE_GH")
    glide: tuple = ()      # tuple[str] — PHONE_W/PHONE_J đứng TRƯỚC nucleus (4.6.3)
    nucleus: str = ""      # 1 segment ID (đơn âm, dài hay diphthong gộp: PHONE_U_SCHWA…)
    coda: tuple = ()       # tuple[str] — tối đa 1 segment (cấu trúc vi)
    tone: str = ""         # TONE_* bắt buộc trừ khi tone_state="unresolved" (schema §4)
    source_graphemes: str = ""  # chữ gốc — traceability, không serialize
    tone_state: str = "resolved"  # thuộc TONE_STATES — enum ĐÓNG, giá trị lạ bị chặn
    flags: frozenset = frozenset()  # cờ [B] cell — metadata, không serialize

    def validate(self, by_id):
        errs = []
        if self.tone_state not in TONE_STATES:
            errs.append(f"tone_state {self.tone_state!r} không thuộc enum đóng "
                        f"{sorted(TONE_STATES)} (A3-03)")
        if not self.nucleus:
            errs.append("thiếu nucleus")
        for mid in self.onset + self.glide + self.coda + (self.nucleus,):
            if mid not in by_id:
                errs.append(f"ID lạ: {mid!r}")
            elif by_id[mid]["loai"] != "segment":
                errs.append(f"{mid} không phải segment")
        if self.tone_state == "unresolved":
            if self.tone:
                errs.append("tone_state=unresolved nhưng vẫn gắn tone — cấm (schema §4)")
        elif self.tone not in inventory.TONE_IDS:
            errs.append(f"tone {self.tone!r} không thuộc TONE_IDS")
        if len(self.coda) > 1:
            errs.append(f"vi coda tối đa 1 segment, nhận {self.coda}")
        return errs


@dataclass(frozen=True)
class EnSyllable:
    """Record âm tiết en — stress là PROSODY token gắn nucleus (4.7.2)."""
    onset: tuple = ()
    nucleus: str = ""
    coda: tuple = ()
    stress: str = ""       # STRESS_PRIMARY / STRESS_SECONDARY / "" (unstressed)
    source_graphemes: str = ""
    stress_state: str = "resolved"  # thuộc STRESS_STATES — enum ĐÓNG (A3-03); "không
    #                       STRESS_*" = unstressed CHỈ khi output đã resolve stress;
    #                       unresolved phải được ghi ở mức record, không âm thầm.

    def validate(self, by_id):
        errs = []
        if self.stress_state not in STRESS_STATES:
            errs.append(f"stress_state {self.stress_state!r} không thuộc enum đóng "
                        f"{sorted(STRESS_STATES)} (A3-03)")
        if not self.nucleus:
            errs.append("thiếu nucleus")
        for mid in self.onset + self.coda + (self.nucleus,):
            if mid not in by_id:
                errs.append(f"ID lạ: {mid!r}")
            elif by_id[mid]["loai"] != "segment":
                errs.append(f"{mid} không phải segment")
        if self.stress and self.stress not in inventory.STRESS_IDS:
            errs.append(f"stress {self.stress!r} không thuộc STRESS_IDS")
        if self.stress_state == "unresolved" and self.stress:
            errs.append("stress_state=unresolved nhưng vẫn gắn stress — cấm (schema §4)")
        return errs


# ---------------------------------------------------------------- bảng transform

# master_id → chuỗi profile. CHỈ các ID bị map (documented loss, 4.9.1).
# ɝ→ɚ phát hiện A3: vocab 178 không có ɝ (对比 kokoro_vocab_178.tsv).
# PHONE_OPEN_E_PREVELAR (R12-02, vòng 6.3): vocab 178 không có category riêng cho
# vần ach-prevelar — export COLLAPSE về category ɛ của kokoro178. Đây là khai báo
# mất đối lập SEMANTIC (mách/méc cùng "mɛ↗k" trong chuỗi export, dù unicode nhìn
# như ɛ→ɛ): master giữ đối lập (ham/0.2), profile kokoro178 KHÔNG; loss event ghi
# khi dùng; sidecar vẫn giữ master ID riêng để truy vết.
SEGMENT_MAP_KOKORO178 = {
    "PHONE_B_IMP": "b",       # ɓ→b
    "PHONE_D_IMP": "d",       # ɗ→d
    "PHONE_R_VI": "ʒ",        # ʐ→ʒ
    "PHONE_TH": "θ",          # tʰ→θ
    "PHONE_ER_STRESS": "ɚ",   # ɝ→ɚ
    "PHONE_OPEN_E_PREVELAR": "ɛ",  # vần ach → category ɛ — MẤT đối lập ach/ec (R12-02)
}

# Tên thanh → chuỗi mũi tên chèn (bảng 4.6.1; digit chỉ hiển thị, KHÔNG map digit→digit)
# [V] đã xác minh 01/10/2026 (kokoro178_tone_pinned.md): convention checkpoint = NGANG
# KHÔNG đánh dấu (frontend gốc bỏ arrow cho ngang trên 98.6% tần suất — chỉ quirk "âu").
TONE_TO_ARROW = {
    "TONE_NGANG": "",
    "TONE_HUYEN": "↘",
    "TONE_SAC": "↗",
    "TONE_HOI": "↓",
    "TONE_NGA": "ʔ↗",     # ngã mang glottal
    "TONE_NANG": "ʔ↓",    # nặng mang glottal
}

STRESS_TO_MARK = {"STRESS_PRIMARY": "ˈ", "STRESS_SECONDARY": "ˌ"}

# Enum ĐÓNG cho state (A3-03): giá trị ngoài tập (vd gõ sai 'unresovled') bị validate
# chặn — KHÔNG được coi "mọi chuỗi khác 'unresolved'" là resolved.
TONE_STATES = {"resolved", "diacritic", "policy", "fold", "unresolved"}
STRESS_STATES = {"resolved", "unresolved"}


@dataclass
class ProfileResult:
    profile: str
    text: str = ""
    sidecar: list = field(default_factory=list)  # [(đơn vị_profile, master_id)] — traceability
    loss: list = field(default_factory=list)     # [(master_id, từ, thành)] loss đã kích hoạt
    errors: list = field(default_factory=list)


def _by_id():
    return {r["id"]: r for r in inventory.load()}


def _seg_str(mid, by_id):
    """master ID → chuỗi profile (mặc định = unicode; map loss nếu có)."""
    if mid in SEGMENT_MAP_KOKORO178:
        return SEGMENT_MAP_KOKORO178[mid]
    return by_id[mid]["unicode"]


# ---------------------------------------------------------------- transform


def transform_vi(syl, by_id=None):
    """kokoro178: record vi → chuỗi. Arrow chèn TRƯỚC âm cuối (coda nếu có)."""
    by_id = by_id or _by_id()
    res = ProfileResult(profile=PROFILE_VERSION)
    errs = syl.validate(by_id)
    if errs:
        res.errors.extend(errs)
        return res
    if syl.tone_state == "unresolved":
        res.errors.append("tone chưa phân giải (schema §4) — phân giải bằng dấu/fold/trì hoãn, "
                          "không được serialize âm thầm như ngang")
        return res

    segs = list(syl.onset) + list(syl.glide) + [syl.nucleus]
    # A3-02: sidecar chứa ĐƠN VỊ PROFILE THỰC TẾ trong text (sau loss map) — không
    # phải master repr (trước đây tʰ/θ lệch offset: thà text=θaː↘ sidecar=tʰaː↘).
    # Master repr vẫn traceable qua res.loss (mọi ID bị map đều được ghi).
    text_parts = [_seg_str(m, by_id) for m in segs]
    side = [(s, m) for s, m in zip(text_parts, segs)]

    if syl.coda:
        coda_str = _seg_str(syl.coda[0], by_id)
        text_parts.append(TONE_TO_ARROW[syl.tone])    # arrow TRƯỚC coda
        text_parts.append(coda_str)
        side.append((TONE_TO_ARROW[syl.tone], syl.tone))
        side.append((coda_str, syl.coda[0]))
    else:
        text_parts.append(TONE_TO_ARROW[syl.tone])    # không coda: arrow sau nucleus
        side.append((TONE_TO_ARROW[syl.tone], syl.tone))
    res.text = "".join(text_parts)

    for mid in set(SEGMENT_MAP_KOKORO178) & (set(syl.onset + syl.glide + syl.coda + (syl.nucleus,))):
        res.loss.append((mid, by_id[mid]["unicode"], SEGMENT_MAP_KOKORO178[mid]))
    res.sidecar = side
    return res


def transform_en(syl, by_id=None):
    """kokoro178: record en → chuỗi. ˈ/ˌ chèn TRƯỚC nucleus (4.9.3)."""
    by_id = by_id or _by_id()
    res = ProfileResult(profile=PROFILE_VERSION)
    errs = syl.validate(by_id)
    if errs:
        res.errors.extend(errs)
        return res
    if syl.stress_state == "unresolved":
        res.errors.append("stress chưa phân giải (schema §4/3.3) — phân giải bằng lexicon/law "
                          "trước, không được serialize âm thầm như unstressed")
        return res

    parts, side = [], []
    for m in syl.onset:
        s = _seg_str(m, by_id)
        parts.append(s)
        side.append((s, m))
    if syl.stress:
        mark = STRESS_TO_MARK[syl.stress]
        parts.append(mark)
        side.append((mark, syl.stress))
    s = _seg_str(syl.nucleus, by_id)
    parts.append(s)
    side.append((s, syl.nucleus))
    for m in syl.coda:
        s = _seg_str(m, by_id)
        parts.append(s)
        side.append((s, m))
    res.text = "".join(parts)
    for mid in set(SEGMENT_MAP_KOKORO178) & (set(syl.onset + syl.coda + (syl.nucleus,))):
        res.loss.append((mid, by_id[mid]["unicode"], SEGMENT_MAP_KOKORO178[mid]))
    res.sidecar = side
    return res


def cleanup(text):
    """Hook cleanup theo frontend — hiện identity (4.9.4)."""
    return text


# ---------------------------------------------------------------- conformance (I2)


def load_vocab178():
    """Trả về (set ký tự, n_entries) từ kokoro_vocab_178.tsv. Ký tự space là entry hợp lệ."""
    chars, n = set(), 0
    for ln in VOCAB_TSV.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = ln.split("\t")
        assert len(parts) >= 3, f"dòng sai định dạng: {ln!r}"
        chars |= set(parts[0])          # symbol có thể nhiều ký tự (nếu có) — lấy hết
        n += 1
    return chars, n


def check_conformance(text, chars=None):
    """Mọi ký tự phải thuộc vocab 178. Trả về list lỗi (rỗng = PASS)."""
    if chars is None:
        chars, _ = load_vocab178()
    return [f"ký tự lạ {c!r} (U+{ord(c):04X}) không thuộc vocab 178"
            for c in text if c not in chars]


def profile_conformance_report():
    """Toàn bộ segment ham/0.2 qua map → mọi ký tự phải thuộc vocab 178 (chạy lúc import test)."""
    by_id = {r["id"]: r for r in inventory.load()}
    chars, n = load_vocab178()
    errs = []
    for r in by_id.values():
        if r["loai"] != "segment":
            continue
        s = _seg_str(r["id"], by_id)
        bad = [c for c in s if c not in chars]
        if bad:
            errs.append(f"{r['id']} ({r['unicode']!r} → {s!r}): ký tự lạ {bad}")
    return errs, n
