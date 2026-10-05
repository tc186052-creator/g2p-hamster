# -*- coding: utf-8 -*-
"""g2p.py — lõi pipeline G2P (fase D, v19): token IR ir/0.1 → record master
ham/0.2 → chuỗi profile kokoro178 (adapter debug).

Hợp đồng đầu vào `00_docs/G2P_00_hop_dong_dau_vao.md` (ir/0.1, nguồn sự thật
tầng 1 `pipeline.py`): G2P ăn `tokens[]` NGUYÊN XI — verbal/route/cat/read/
break/intonation — KHÔNG sửa câu, KHÔNG tự normalization lại, KHÔNG tự suy
route mới. "Không đọc số" = không tự làm lại normalization tầng 1; phần đọc
tầng 1 ĐÃ cấp (verbal dạng từ của number/abbr/unit…) vẫn được tiêu thụ.

Tiêu thụ (hậu kiểm v18 D18-02):
  cat=punct      → status "control": im lặng, GIỮ break/intonation cho tầng sau.
  cat=icon/khác  → "not_word" deferred tường minh.
  còn lại        → verbal là chuỗi read unit (tách dấu cách) — từng unit đi
                   đường route (vi: parse/fold/spell theo âm tiết; en: cmu_en).
  read/break/intonation/origin được giữ trong record output.

Hợp đồng đã duyệt (B §6 + v16 §1 + v17 §6 + v18 §3-6):
  1. VI: scope_exclusion_status() trên INPUT và trên ỨNG VIÊN FOLD (D18-01 —
     fallback không được tạo đường vòng qua subject QD57 đã loại; "nic"→"níc"
     bị chặn như gọi trực tiếp "níc"). Sau fold/spell không lách bằng protected
     partner hay spell.
  2. VI: parse thuần (F05) → fold nhóm (b) theo pin fold_vi.tsv (tone_state=
     "fold", provenance trong detail) → spell seed spell_vi.tsv (quy ước CHỜ
     DUYỆT — pins ghi rõ trạng thái) → unresolved không bịa.
  3. EN: ok / spell (unsupported_chars) / no_nucleus — spell lưu fallback_reason
     (D18-02); verbal rỗng/không phải chuỗi → contract error + unresolved
     (D18-03), KHÔNG bao giờ spell→complete từ input rỗng.
  4. Contract check (D18-02): schema/shape/field + đồng thuận read_string →
     contract_errors có cấu trúc; không crash KeyError/AttributeError.
  5. Serializer master (D18-02): output g2p/0.1 giữ RECORD (onset/glide/
     nucleus/coda/tone/stress + state) với liên kết nguồn source_token_id /
     read_unit_index / syllable_index (schema inventory §5); profile kokoro178
     là NHÁNH DEBUG riêng — không thay thế master.
  6. Invariant (D18-03): validate() kiểm TƯƠNG QUAN status↔records↔
     read_complete↔unsupported↔state; to_profile CHẠY VALIDATE và từ chối
     serialize mọi status cấm phát âm kể cả khi bị gắn syllables (fault
     injection không lọt).
  7. Fingerprint (D18-04): g2p_policy_hash = sha256{code(g2p.py), fold_tsv,
     spell_tsv, cmudict, scope ledger, inventory_hash, inventory_contract_hash,
     profile version} — mutation bảng fold/consumer → hash ĐỔI; khôi phục →
     baseline. load_fold()/load_spell() KIỂM SHA đối chiếu resource pins
     (02_data/g2p/g2p_resource_pins.json) — lệch → SystemExit, fail-closed.

Fingerprint bắt buộc trong mọi đầu ra g2p/0.1 (schema inventory §7):
  inventory_hash + inventory_contract_hash + g2p_policy_hash + versions.

Output record g2p/0.1 (02_data/g2p/schema_g2p_0.1.md): `G2PToken` (in-memory,
syllables là dataclass) và `token_json()` / `stream_json()` (serializer master
+ metadata). Self-test: 01_g2p/test_g2p.py
"""
import dataclasses
import hashlib
import json
import sys
import unicodedata as U
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from . import inventory  # noqa: E402
from . import collision_audit as CA  # noqa: E402
from . import cmu_en as C  # noqa: E402
from . import vi_rules as R  # noqa: E402
from . import vi_syllable as VS  # noqa: E402
from .profiles import (ViSyllable, EnSyllable, transform_vi, transform_en,  # noqa: E402
                      check_conformance, load_vocab178, PROFILE_VERSION)

ROOT = HERE.parent
FOLD_TSV = ROOT / "02_data" / "fold" / "fold_vi.tsv"
SPELL_TSV = ROOT / "02_data" / "spell_vi.tsv"
RESOURCE_PINS = ROOT / "02_data" / "g2p" / "g2p_resource_pins.json"
G2P_SCHEMA_VERSION = "g2p/0.1"

# status enum ĐÓNG (g2p/0.1) — giá trị lạ bị validate chặn
STATUSES = {"ok", "fold", "spell", "no_nucleus", "scope_excluded",
            "unresolved", "not_word", "unknown_route", "control"}
# status KHÔNG ĐƯỢC phát âm — serializer phải từ chối kể cả khi có syllables
NO_PRONOUNCE = {"scope_excluded", "unresolved", "not_word", "unknown_route",
                "no_nucleus", "control"}
# cat enum theo hợp đồng đầu vào (ir/0.1) — cat ngoài tập này = contract error
IR_CATS = {"word", "punct", "number", "abbr", "acronym", "unit", "date",
           "time", "money", "symbol", "url", "email", "phone", "pm_am",
           "slang", "icon"}
DEFERRED_CATS = {"icon"}   # chưa có đường tiêu thụ — deferred tường minh
IR_READS = {"word", "spell"}
IR_BREAKS = {None, "major", "minor"}


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def resource_pins():
    return json.loads(RESOURCE_PINS.read_text(encoding="utf-8"))


def _verify_resource_pins():
    """Fail-closed: mọi tài nguyên hiệu lực của D phải khớp pin — lệch →
    SystemExit (mutation bảng fold/spell/ledger không được âm thầm ăn theo)."""
    pins = resource_pins()
    checks = {"fold_tsv": FOLD_TSV, "spell_tsv": SPELL_TSV}
    errs = []
    for key, path in checks.items():
        got = sha256_file(path)
        if got != pins[key]["sha256"]:
            errs.append(f"{key} lệch pin: {got[:12]}… ≠ {pins[key]['sha256'][:12]}…")
    if _cmudict_sha_snapshot() != pins["cmudict"]["sha256"]:
        errs.append("cmudict lệch pin resource")
    ledger = ROOT / "02_data" / "collision" / "qd57_scope_exclusions.json"
    if sha256_file(ledger) != pins["scope_ledger"]["sha256"]:
        errs.append("scope ledger lệch pin resource")
    if errs:
        raise SystemExit("[g2p] resource pins: " + "; ".join(errs))
    return pins


def g2p_policy_hash():
    """Fingerprint policy tầng D (D18-04): consumer + SNAPSHOT tài nguyên hiệu
    lực + hash inventory + CÁC HASH POLICY B/C HIỆU LỰC (hậu kiểm v19 §5.1 —
    mutation cmu_en phải làm hash D đổi vì hành vi output đổi)."""
    payload = {
        "schema": "g2p_policy/0.2",
        "code_sha256_g2p": sha256_file(HERE / "g2p.py"),
        **effective_resource_shas(),
        "cmudict_sha256": _cmudict_sha_snapshot(),
        "scope_ledger_sha256": sha256_file(
            ROOT / "02_data" / "collision" / "qd57_scope_exclusions.json"),
        "inventory_hash": inventory.sha256_of_tsv(),
        "inventory_contract_hash": inventory.contract_hash(),
        "b_c_dependencies": _b_c_dependencies(),
        "profile_version": PROFILE_VERSION,
        "g2p_schema_version": G2P_SCHEMA_VERSION,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def output_metadata(resource_override=None):
    """Metadata bắt buộc trong MỌI đầu ra g2p/0.1 (inventory_schema §7).
    identity mang giá trị pin B/C thực (hậu kiểm v19 §5.1) + sha snapshot tài
    nguyên hiệu lực (§5.3). resource_override ≠ None ⇒ đánh dấu test-only."""
    deps = _b_c_dependencies()
    md = {"schema": G2P_SCHEMA_VERSION,
          "inventory_hash": inventory.sha256_of_tsv(),
          "inventory_contract_hash": inventory.contract_hash(),
          "g2p_policy_hash": g2p_policy_hash(),
          "resource_snapshot": {"fold_tsv_sha256":
                                effective_resource_shas()["fold_tsv"],
                                "spell_tsv_sha256":
                                effective_resource_shas()["spell_tsv"],
                                "cmudict_sha256": _cmudict_sha_snapshot()},
          "versions": {"profile": PROFILE_VERSION,
                       "dialect": "vi v1 — pin domain_config_hash "
                                  + deps["domain_config_hash"][:12] + "…",
                       "lexicon": {"cmudict_sha256": _cmudict_sha_snapshot(),
                                   "spell_vi": "seed — quy ước tên chữ VI, "
                                               "TRẠNG THÁI CHỜ DUYỆT"},
                       "fold": "fold_vi nhánh (b) ASCII route-vi — prior "
                               "tần suất corpus, pin qua resource pins",
                       "b_c_dependencies": deps}}
    if resource_override is not None:
        md["resource_override"] = resource_override   # test-only — KHÔNG phải pin mặc định
    return md


def load_fold():
    """ascii → dict fold (nhóm b, prior tần suất). KIỂM SHA pin trước (D18-04)."""
    _verify_resource_pins()
    out = {}
    for ln in FOLD_TSV.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        ascii_w, fold, freq, margin, _n = ln.split("\t")
        out[ascii_w] = {"fold": fold, "freq_top1": int(freq),
                        "margin": float(margin)}
    return out


def load_spell_vi():
    """letter → list âm tiết (seed spell_vi — QUY ƯỚC CHỜ DUYỆT, pins ghi trạng
    thái). KIỂM SHA pin trước."""
    _verify_resource_pins()
    return R.load_spell()


# ---------------------------------------------------------------- record

@dataclass
class G2PToken:
    """Record output g2p/0.1 cho MỘT token IR — truy vết đủ, status tường minh."""
    i: int
    surface: str
    cat: str
    route: str
    verbal: str
    read: str = ""              # ir/0.1 nguyên dạng (D18-02)
    break_kind: str = ""        # break ir/0.1: "" | major | minor (giữ nguyên)
    intonation: str = ""        # ir/0.1 nguyên dạng
    origin: str = ""            # ir/0.1 nguyên dạng
    status: str = "unresolved"  # thuộc STATUSES
    units: list = field(default_factory=list)   # list[G2PUnit] — read unit
    unsupported_chars: tuple = ()
    read_complete: bool = False
    errors: list = field(default_factory=list)
    contract_errors: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    def validate(self):
        """Invariant tương quan (D18-03): status ↔ records ↔ read_complete ↔
        unsupported ↔ state. Trả list lỗi; rỗng = hợp lệ."""
        errs = list(self.errors) + list(self.contract_errors)
        if self.status not in STATUSES:
            errs.append(f"status {self.status!r} không thuộc enum đóng "
                        f"{sorted(STATUSES)}")
            return errs
        n_units = len(self.units)
        # aggregate parent/child (hậu kiểm v19 §4): parent PHẢI khớp giá trị
        # derive từ units — parent tuyên bố đủ khi child còn thiếu bị BẮT
        if n_units:
            agg_status, agg_complete, agg_unsup = _aggregate(self.units)
            if self.status != agg_status:
                errs.append(f"status {self.status!r} lệch roll-up từ units "
                            f"(derive {agg_status!r}) — aggregate mâu thuẫn")
            if self.read_complete != agg_complete:
                errs.append(f"read_complete={self.read_complete!r} lệch "
                            f"aggregate từ units (derive {agg_complete!r}) — "
                            f"parent không được tuyên bố đủ khi child còn thiếu")
            if tuple(self.unsupported_chars) != agg_unsup:
                errs.append(f"unsupported_chars {self.unsupported_chars!r} lệch "
                            f"aggregate từ units (derive {agg_unsup!r})")
        if self.status in NO_PRONOUNCE:
            # roll-up nhất quán: status cấm phát âm phải đến từ ít nhất 1 unit
            # cùng nhóm (hoặc token không có unit); record phát âm bị cấm ở CẤP
            # UNIT (unit NO_PRONOUNCE → không syllables — fault injection bị bắt
            # tại unit.validate). Unit pronounceable trong token cấm phát âm là
            # traceability một phần HỢP LỆ — read_complete=False là cửa bắt.
            if n_units and not any(u.status in NO_PRONOUNCE for u in self.units):
                errs.append(f"status {self.status!r} nhưng không có unit nào "
                            f"thuộc nhóm cấm phát âm — roll-up lệch")
            if self.read_complete:
                errs.append(f"status {self.status!r} cấm phát âm nhưng "
                            f"read_complete=True")
        else:  # ok / fold / spell
            if not n_units:
                errs.append(f"status {self.status!r} phải có read unit")
            else:
                for u in self.units:
                    if u.status in NO_PRONOUNCE:
                        errs.append(f"status {self.status!r} nhưng unit "
                                    f"{u.unit_index} {u.status!r} — roll-up lệch")
            if self.status in ("ok", "fold") and self.unsupported_chars:
                errs.append("ok/fold không được có unsupported_chars")
            if self.status == "spell":
                if self.unsupported_chars and self.read_complete:
                    errs.append("spell còn ký tự chưa hỗ trợ nhưng "
                                "read_complete=True — không coi một phần là đủ")
                if not self.unsupported_chars and not self.read_complete:
                    errs.append("spell trọn ký tự nhưng read_complete=False")
        for u in self.units:
            errs.extend(u.validate())
        return errs


@dataclass
class G2PUnit:
    """1 read unit (một từ/âm tiết của verbal) + record master tương ứng."""
    text: str                       # unit nguyên dạng (không sửa)
    unit_index: int
    status: str = "unresolved"
    syllables: list = field(default_factory=list)  # [ViSyllable|EnSyllable]
    unsupported_chars: tuple = ()
    read_complete: bool = False
    detail: dict = field(default_factory=dict)

    def validate(self):
        errs = []
        if self.status not in STATUSES:
            errs.append(f"unit status {self.status!r} ngoài enum")
            return errs
        if self.status in NO_PRONOUNCE:
            if self.syllables:
                errs.append(f"unit {self.unit_index} status {self.status!r} "
                            f"cấm phát âm nhưng có record")
            if self.read_complete:
                errs.append(f"unit {self.unit_index} status {self.status!r} "
                            f"nhưng read_complete=True")
        elif not self.syllables:
            errs.append(f"unit {self.unit_index} status {self.status!r} "
                        f"thiếu record")
        for syl in self.syllables:
            errs.extend(syl.validate(_by_id()))
        return errs


INVENTORY_BY_ID = None      # nạp lười (cache inventory by id)


def _by_id():
    global INVENTORY_BY_ID
    if INVENTORY_BY_ID is None:
        INVENTORY_BY_ID = {r["id"]: r for r in inventory.load()}
    return INVENTORY_BY_ID


# ---------------------------------------------------------------- contract

def check_contract(ir):
    """Kiểm shape/version/field envelope IR (D18-02) → list contract_errors.
    Không văng exception — lỗi trả về có cấu trúc."""
    errs = []
    if not isinstance(ir, dict):
        return ["ir phải là dict, nhận " + type(ir).__name__]
    if ir.get("schema") != "ir/0.1":
        errs.append(f"schema ir/0.1 expected, nhận {ir.get('schema')!r}")
    toks = ir.get("tokens")
    if not isinstance(toks, list):
        errs.append("ir.tokens phải là list")
        return errs
    rs = ir.get("read_string")
    if rs is not None and not isinstance(rs, str):
        errs.append("ir.read_string phải là str hoặc null")
    prev_i = None
    for pos, t in enumerate(toks):
        if not isinstance(t, dict):
            errs.append(f"tokens[{pos}] phải là dict")
            continue
        i = t.get("i")
        if not isinstance(i, int) or isinstance(i, bool):
            errs.append(f"tokens[{pos}].i phải là int, nhận {i!r}")
        elif prev_i is not None and i != prev_i + 1:
            errs.append(f"tokens[{pos}].i không liên tiếp: {prev_i} → {i}")
        else:
            prev_i = i
        c = t.get("cat")
        if not isinstance(c, str) or c not in IR_CATS:
            errs.append(f"tokens[{pos}].cat lạ: {c!r}")
        r_ = t.get("route")
        if not isinstance(r_, str) or r_ not in ("vi", "en", "neu"):
            errs.append(f"tokens[{pos}].route lạ: {r_!r}")
        rd = t.get("read")
        if not isinstance(rd, str) or rd not in IR_READS:
            errs.append(f"tokens[{pos}].read lạ: {rd!r}")
        b = t.get("break")
        if b is not None and (not isinstance(b, str) or b not in ("major", "minor")):
            errs.append(f"tokens[{pos}].break lạ: {b!r}")
        if not isinstance(t.get("surface"), str) or \
                not isinstance(t.get("verbal"), str):
            errs.append(f"tokens[{pos}] surface/verbal phải là str "
                        f"(verbal={t.get('verbal')!r})")
    errs.extend(_read_string_consensus(rs, toks))
    return errs


# Quy tắc tương đương read_string (hậu kiểm v19 §3.4): tầng 1 render dấu câu
# với quy tắc gắn-dính riêng (vd "Jerry" + "-" + "Đường" → "Jerry-Đường";
# "trăm" + "." → "trăm."). Đối chiếu theo DÃY MẢNH CHỮ-SỐ (tách tại mọi ký tự
# không chữ/số) theo thứ tự — bất khả tri vị trí dấu câu, nhưng vẫn bắt ĐỦ:
# nội dung từ vựng thừa/thiếu/sai thứ tự (vd "nam thêm", "xnam", "namnam") đều
# FAIL; read_string rỗng trong khi có reading FAIL.
import re as _re

_FRAG_SPLIT = _re.compile(r"[^\w]+", _re.UNICODE)


_APOSTROPHES = str.maketrans({"’": "'", "ʼ": "'", "‘": "'", "`": "'",
                              "´": "'"})


def _words_normalized(text):
    """Chuỗi → list mảnh chữ-số (renderer-agnostic). Biến thể nháy ('’ʼ´`)
    chuẩn hóa về ASCII ' — corpus read_string giữ nguyên dấu gốc tầng 1
    (vd "itʼs") trong khi verbal đã ASCII hóa ("it's")."""
    return [w for w in _FRAG_SPLIT.split(str(text).translate(_APOSTROPHES))
            if w]


def _read_string_consensus(rs, toks):
    """Đối chiếu read_string theo RANH GIỚI TỪ (hậu kiểm v19 §3.4): dãy từ
    reading của token KHÔNG punct phải KHỚP ĐÚNG dãy từ của read_string —
    không substring, không thừa/thiếu nội dung từ vựng. read_string=null được
    phép (tầng 1 có thể không cấp); read_string RỖNG được cấp trong khi token
    có reading → contract_error (không dùng rỗng để bỏ qua mâu thuẫn)."""
    expected = []
    for t in toks:
        if not isinstance(t, dict) or t.get("cat") == "punct":
            continue
        v = t.get("verbal")
        if isinstance(v, str):
            expected.extend(_words_normalized(v))
    if rs is None:
        return []                      # hợp lệ — tầng 1 không cấp
    if not isinstance(rs, str):
        return ["ir.read_string phải là str hoặc null"]
    got = _words_normalized(rs)
    if not expected:
        return []                      # không có reading để đối chiếu
    if not got:
        return ["read_string rỗng trong khi tokens có reading "
                f"({len(expected)} từ) — mâu thuẫn không được bỏ qua"]
    if got != expected:
        # lỗi đầu tiên để truy vết (không dàn cả dãy cho dài dòng)
        k = next((i for i, (a, b) in enumerate(zip(got, expected)) if a != b),
                 None)
        if k is None or len(got) != len(expected):
            return [f"read_string lệch dãy từ: expected {len(expected)} từ "
                    f"{expected[:6]}…, got {len(got)} từ {got[:6]}…"]
        return [f"read_string lệch tại từ #{k}: expected {expected[k]!r}, "
                f"got {got[k]!r}"]
    return []


# ---------------------------------------------------------------- đường VI

def _en_spell_unit(w, verbal, unit_index):
    """read="spell" route=en — ĐỌC THEO TÊN CHỮ (hậu kiểm v19 §3.1: dictionary
    hit KHÔNG được bỏ qua mode). Mỗi ký tự → LETTER_NAMES (C đã duyệt 26 chữ
    US); ký tự ngoài bảng → unsupported_chars tường minh."""
    base = dict(text=verbal, unit_index=unit_index)
    if not w:
        return G2PUnit(**base, detail={"reason": "verbal unit rỗng"})
    syls, unsupported = [], []
    for ch in w:
        if ch in C.LETTER_NAMES:
            syls.extend(EnSyllable(onset=on, nucleus=nuc, coda=co, stress=st,
                                   source_graphemes=ch,
                                   stress_state="resolved")
                        for on, nuc, co, st in C.syllabify(C.LETTER_NAMES[ch]))
        elif ch not in unsupported:
            unsupported.append(ch)
    if not syls:
        return G2PUnit(**base, unsupported_chars=tuple(unsupported),
                       detail={"fallback_reason":
                               "read=spell nhưng không có ký tự nào có tên"})
    return G2PUnit(**base, status="spell", syllables=syls,
                   unsupported_chars=tuple(unsupported),
                   read_complete=not unsupported,
                   detail={"fallback_reason": "read=spell — đọc theo bảng "
                          "26 tên chữ US (C chấp nhận v16)"})


def _vi_unit(w, verbal, unit_index, fold_tab, spell_vi):
    """1 read unit VI → G2PUnit (scope input → parse → fold + scope ứng viên →
    spell → unresolved)."""
    base = dict(text=verbal, unit_index=unit_index)
    if not w:
        return G2PUnit(**base, detail={"reason": "verbal unit rỗng"})
    scope = CA.scope_exclusion_status(w)
    if scope is not None:
        return G2PUnit(**base, status="scope_excluded", detail={"scope": scope})
    try:
        syl = VS.parse(w)
        return G2PUnit(**base, status="ok", syllables=[syl], read_complete=True)
    except VS.ParseError as e:
        reason = str(e)
    # fold — chỉ nhóm (b) ASCII route-vi theo pin; RE-CHECK scope ứng viên
    # (D18-01: fallback không được tạo đường vòng qua subject đã loại)
    if all("a" <= ch <= "z" for ch in w) and w in fold_tab:
        cand = fold_tab[w]
        scope_cand = CA.scope_exclusion_status(cand["fold"])
        if scope_cand is not None:
            return G2PUnit(**base, status="scope_excluded",
                           detail={"input": w, "fold_candidate": cand["fold"],
                                   "scope": scope_cand,
                                   "note": " ứng viên fold thuộc QD57 — không "
                                           "phát âm, không lách sang protected "
                                           "partner hay spell"})
        try:
            syl = VS.parse(cand["fold"])
        except VS.ParseError:
            return G2PUnit(**base,
                           detail={"reason": reason,
                                   "fold_candidate_lỗi": cand["fold"]})
        syl = dataclasses.replace(syl, tone_state="fold", source_graphemes=verbal)
        return G2PUnit(**base, status="fold", syllables=[syl],
                       read_complete=True,
                       detail={"fold_ascii": w, "fold_to": cand["fold"],
                               "freq_top1": cand["freq_top1"],
                               "margin": cand["margin"]})
    # spell vi — seed tên chữ (quy ước chờ duyệt); input 1 ký tự, subject =
    # chính input đã qua scope ở trên — không tạo subject mới
    if len(w) == 1 and w in spell_vi:
        syls = [VS.parse(s) for s in spell_vi[w]]
        return G2PUnit(**base, status="spell", syllables=syls,
                       read_complete=True)
    return G2PUnit(**base, detail={"reason": reason})


def _en_unit(w, verbal, unit_index):
    """1 read unit EN → G2PUnit (cmu_en; verbal rỗng → unresolved — D18-03)."""
    base = dict(text=verbal, unit_index=unit_index)
    if not w:
        return G2PUnit(**base, detail={"reason": "verbal unit rỗng"})
    res = C.pronounce(w, cmu=_cmu_snapshot())
    if res.status == "ok":
        return G2PUnit(**base, status="ok", syllables=list(res.syllables),
                       read_complete=True)
    if res.status == "spell":
        if not res.spell_syllables:
            # không có ký tự nào đọc được (vd "Ả", "1-2-2-4") — spell rỗng
            # KHÔNG phải một phần reading: unresolved + unsupported tường minh
            return G2PUnit(**base, status="unresolved",
                           unsupported_chars=tuple(res.unsupported_chars),
                           detail={"fallback_reason": res.reason or
                                   "oov — không có key cmudict",
                                   "reason": "spell không sinh reading: mọi "
                                             "ký tự ngoài bảng tên chữ"})
        complete = not res.unsupported_chars
        # fallback_reason: provenance quyết định spelling (D18-02)
        return G2PUnit(**base, status="spell",
                       syllables=[s for grp in res.spell_syllables for s in grp],
                       unsupported_chars=tuple(res.unsupported_chars),
                       read_complete=complete,
                       detail={"fallback_reason": res.reason or "oov — "
                               "không có key cmudict, đọc theo tên chữ"})
    return G2PUnit(**base, status="no_nucleus",
                   detail={"reason": res.reason})


# ---------------------------------------------------------------- token

def _type_guard(tok):
    """Guard TRƯỚC mọi membership/.get — giá trị không hợp lệ (list/dict/null)
    phải thành contract_error có cấu trúc, không TypeError (hậu kiểm v19 §3.3)."""
    errs = []
    t = tok if isinstance(tok, dict) else {}
    if not isinstance(tok, dict):
        errs.append(f"token phải là dict, nhận {type(tok).__name__}")
    cat = t.get("cat")
    if not isinstance(cat, str) or cat not in IR_CATS:
        errs.append(f"cat lạ: {cat!r}")
    route = t.get("route")
    if not isinstance(route, str) or route not in ("vi", "en", "neu"):
        errs.append(f"route lạ: {route!r}")
    rd = t.get("read")
    if not isinstance(rd, str) or rd not in IR_READS:
        errs.append(f"read lạ: {rd!r}")
    brk = t.get("break")
    if brk is not None and (not isinstance(brk, str) or brk not in ("major", "minor")):
        errs.append(f"break lạ: {brk!r}")
    return t, errs


def _aggregate(units):
    """Derive (status, read_complete, unsupported) TỪ units (hậu kiểm v19 §4) —
    parent không được tự tuyên bố đủ khi child còn thiếu."""
    if not units:
        return "unresolved", False, ()
    status = _roll_up(units)
    complete = all(u.read_complete for u in units)
    unsup = _unsupported(units)
    return status, complete, unsup


def g2p_token(tok, fold_tab=None):
    """1 token IR dict → G2PToken. Không sửa verbal/route/cat/read/break.
    Lỗi shape → contract_errors có cấu trúc, không KeyError/AttributeError/
    TypeError (guard type TRƯỚC membership — hậu kiểm v19 §3.3)."""
    fold_tab = _fold_tab_with_pin(fold_tab)
    tok, errs = _type_guard(tok)
    cat = tok.get("cat")
    route = tok.get("route")
    verbal = tok.get("verbal")
    if not isinstance(verbal, str):
        errs.append(f"verbal phải là str, nhận {verbal!r}")
        verbal = ""
    brk = tok.get("break")
    base = dict(i=tok.get("i") if isinstance(tok.get("i"), int)
                and not isinstance(tok.get("i"), bool) else -1,
                surface=tok.get("surface") if isinstance(tok.get("surface"), str)
                else "",
                cat=cat if isinstance(cat, str) else "",
                route=route if isinstance(route, str) else "",
                verbal=verbal,
                read=tok.get("read") if isinstance(tok.get("read"), str)
                and tok.get("read") in IR_READS else "",
                break_kind=brk if brk is None or
                (isinstance(brk, str) and brk in ("major", "minor")) else "",
                intonation=tok.get("intonation") if
                isinstance(tok.get("intonation"), str) else "",
                origin=tok.get("origin") if
                isinstance(tok.get("origin"), str) else "",
                contract_errors=errs)
    if base["i"] == -1:
        base["contract_errors"] = base["contract_errors"] + [
            f"token.i phải là int, nhận {tok.get('i')!r}"]

    if cat == "punct":
        # hợp đồng §3.2: punct → im lặng, CHỈ giữ break (D18-02)
        return G2PToken(status="control", read_complete=False, **base)
    if not isinstance(cat, str) or cat not in IR_CATS or cat in DEFERRED_CATS:
        # icon/… deferred tường minh; cat lạ đã ghi contract_errors ở trên
        return G2PToken(status="not_word", read_complete=False, **base)

    # read="spell" — chế độ đọc do tầng 1 chỉ định, PHẢI được thực thi
    # (hậu kiểm v19 §3.1; dictionary hit không phải quyền bỏ qua mode):
    #   en → per-letter LETTER_NAMES (26 tên chữ US, C chấp nhận v16);
    #   vi → tier-1 đã spell-out trong verbal (vd email) — giữ đường từ;
    #        unit đơn chữ đi seed spell_vi (TRẠNG THÁI CHỜ DUYỆT — không tự
    #        duyệt seed qua dispatch).
    if base["read"] == "spell":
        if route == "en":
            units = [_en_spell_unit(_norm(u), u, k)
                     for k, u in enumerate(verbal.split())]
            st, comp, unsup = _aggregate(units)
            return G2PToken(status=st, read_complete=comp, **base, units=units,
                            unsupported_chars=unsup)
        if route != "vi":
            # D20-02: nhánh spell đối xứng nhánh từ — route ngoài {vi,en} phải
            # fail-loud unknown_route, không đọc im lặng theo đường vi.
            return G2PToken(status="unknown_route", read_complete=False, **base)
        # route vi: đường từ (tier-1 đã spell-out); unit đơn chữ → seed spell
        units = [_vi_unit(_norm(u), u, k, fold_tab, _spell_vi())
                 for k, u in enumerate(verbal.split())]
        st, comp, unsup = _aggregate(units)
        return G2PToken(status=st, read_complete=comp, **base, units=units,
                        unsupported_chars=unsup)

    if route == "vi":
        units = [_vi_unit(_norm(u), u, k, fold_tab, _spell_vi())
                 for k, u in enumerate(verbal.split())]
        st, comp, unsup = _aggregate(units)
        return G2PToken(status=st, read_complete=comp, **base, units=units,
                        unsupported_chars=unsup)
    if route == "en":
        units = [_en_unit(_norm(u), u, k) for k, u in enumerate(verbal.split())]
        st, comp, unsup = _aggregate(units)
        return G2PToken(status=st, read_complete=comp, **base, units=units,
                        unsupported_chars=unsup)
    return G2PToken(status="unknown_route", read_complete=False, **base)


# Warm cache giữ SNAPSHOT ĐÃ KIỂM pin (tab + sha256 tính lúc nạp) — identity
# của output phải định danh đúng snapshot này (D18-04 §5.3: mutation đĩa sau
# warm-load không được làm lệch metadata khỏi reading đang dùng).
_FOLD_TAB_CACHE = None    # {"tab": dict, "sha256": str} | None
_SPELL_VI_CACHE = None    # {"tab": dict, "sha256": str} | None
_CMU_SNAPSHOT = None      # dict load_cmu — nạp pin 1 LẦN/process (fase E:
                          # 1M corpus không thể re-parse 126k entry mỗi từ)
_CMUDICT_SHA_CACHE = None  # str — sha snapshot cmudict đang dùng
_BC_DEPS_CACHE = None     # dict 4 hash B/C — attestation/ledger đọc 1 lần/process


def _cmu_snapshot():
    global _CMU_SNAPSHOT
    if _CMU_SNAPSHOT is None:
        _CMU_SNAPSHOT = C.load_cmu()   # verify_pin bên trong (1 lần)
    return _CMU_SNAPSHOT


def _cmudict_sha_snapshot():
    """sha của snapshot cmudict ĐANG DÙNG (khuôn M5: identity định danh đúng
    snapshot, không re-hash 3,6 MB mỗi record; cold = hash đĩa)."""
    global _CMUDICT_SHA_CACHE
    if _CMUDICT_SHA_CACHE is None:
        _CMUDICT_SHA_CACHE = C._cmudict_sha()
    return _CMUDICT_SHA_CACHE


def _b_c_dependencies():
    """4 hash policy B/C hiệu lực — attestation/ledger tĩnh trong lần chạy,
    đọc 1 lần/process (value-identical với gọi lại từng lần)."""
    global _BC_DEPS_CACHE
    if _BC_DEPS_CACHE is None:
        _BC_DEPS_CACHE = {
            "en_policy_hash": C.en_policy_hash(),
            "domain_config_hash": CA.domain_config_hash(*CA.load_attestation()),
            "scope_policy_hash": CA.scope_policy_hash(),
            "approval_policy_hash": inventory.approval_policy_hash(),
        }
    return dict(_BC_DEPS_CACHE)


def _fold_tab_with_pin(fold_tab):
    """fold_tab tùy chỉnh CHỈ test (D18-04 §5.2: serializer phải đánh dấu
    override — xem g2p_stream.resource_override). Production dùng snapshot pin."""
    global _FOLD_TAB_CACHE
    if fold_tab is not None:
        return fold_tab
    if _FOLD_TAB_CACHE is None:
        _FOLD_TAB_CACHE = {"tab": load_fold(),
                           "sha256": sha256_file(FOLD_TSV)}   # đã qua pin check
    return _FOLD_TAB_CACHE["tab"]


def _spell_vi():
    global _SPELL_VI_CACHE
    if _SPELL_VI_CACHE is None:
        _SPELL_VI_CACHE = {"tab": load_spell_vi(),
                           "sha256": sha256_file(SPELL_TSV)}   # đã qua pin check
    return _SPELL_VI_CACHE["tab"]


def effective_resource_shas():
    """SHA của SNAPSHOT thực sự hiệu lực (cache-aware) — identity output định
    danh đúng tài nguyên đang dùng, không phải byte đĩa có thể đã đổi.
    D20-01: cả hai giá trị LUÔN là str sha256 (bảng đã parse không phải identity;
    cold == warm vì cùng một snapshot đã kiểm pin)."""
    if _FOLD_TAB_CACHE is not None:
        fold_sha = _FOLD_TAB_CACHE["sha256"]
    else:
        _verify_resource_pins()
        fold_sha = sha256_file(FOLD_TSV)
    if _SPELL_VI_CACHE is not None:
        spell_sha = _SPELL_VI_CACHE["sha256"]
    else:
        _verify_resource_pins()
        spell_sha = sha256_file(SPELL_TSV)
    return {"fold_tsv": fold_sha, "spell_tsv": spell_sha}


def _norm(t):
    return U.normalize("NFC", t.strip().lower())


def _roll_up(units):
    """Trạng thái token = xấu nhất theo thang: control < ok < fold < spell <
    no_nucleus < scope_excluded < unresolved < not_word < unknown_route."""
    if not units:
        return "unresolved"
    order = ["control", "ok", "fold", "spell", "no_nucleus", "scope_excluded",
             "unresolved", "not_word", "unknown_route"]
    return max((u.status for u in units), key=order.index)


def _unsupported(units):
    out = []
    for u in units:
        for ch in u.unsupported_chars:
            if ch not in out:
                out.append(ch)
    return tuple(out)


def g2p_tokens(tokens, fold_tab=None):
    """list token IR → list G2PToken (thứ tự giữ nguyên)."""
    return [g2p_token(t, fold_tab) for t in tokens]


# ---------------------------------------------------------------- serializer

def unit_json(unit, token_i, by_id=None):
    """G2PUnit → dict master có liên kết nguồn (inventory_schema §5:
    source_token_id / read_unit_index / syllable_index là structural metadata)."""
    by_id = by_id or _by_id()
    syls = []
    for k, syl in enumerate(unit.syllables):
        rec = {"syllable_index": k}
        if isinstance(syl, ViSyllable):
            rec["lang"] = "vi"
            rec.update(onset=list(syl.onset), glide=list(syl.glide),
                       nucleus=syl.nucleus, coda=list(syl.coda),
                       tone=syl.tone, tone_state=syl.tone_state,
                       source_graphemes=syl.source_graphemes,
                       flags=sorted(syl.flags))
        else:
            rec["lang"] = "en"
            rec.update(onset=list(syl.onset), nucleus=syl.nucleus,
                       coda=list(syl.coda), stress=syl.stress,
                       stress_state=syl.stress_state,
                       source_graphemes=syl.source_graphemes)
        syls.append(rec)
    return {"text": unit.text, "read_unit_index": unit.unit_index,
            "source_token_id": token_i, "status": unit.status,
            "read_complete": unit.read_complete,
            "unsupported_chars": list(unit.unsupported_chars),
            "detail": unit.detail, "syllables": syls}


def token_json(g, by_id=None):
    """G2PToken → dict g2p/0.1: master record ĐẦY ĐỦ + profile debug riêng."""
    errs = g.validate()
    p = _profile_json(g, by_id)          # nhánh debug — không thay thế master
    return {"i": g.i, "surface": g.surface, "cat": g.cat, "route": g.route,
            "verbal": g.verbal, "read": g.read, "break": g.break_kind,
            "intonation": g.intonation, "origin": g.origin,
            "status": g.status, "read_complete": g.read_complete,
            "unsupported_chars": list(g.unsupported_chars),
            "errors": sorted(set(g.errors)),
            "contract_errors": sorted(set(g.contract_errors)),
            "validation": errs,
            "detail": g.detail,
            "master": {"read_units": [unit_json(u, g.i, by_id) for u in g.units]},
            "profile_debug": p}


def _profile_json(g, by_id=None):
    """Adapter debug kokoro178 — NHÁNH RIÊNG, validate gate (D18-03): status
    cấm phát âm KHÔNG serialize kể cả khi bị gắn syllables."""
    by_id = by_id or _by_id()
    out = {"adapter": PROFILE_VERSION, "text": "", "sidecar": [], "loss": [],
           "errors": [], "unsupported_chars": list(g.unsupported_chars),
           "conformance": [], "debug_only": True}
    if g.status in NO_PRONOUNCE:
        out["errors"].append(f"status {g.status!r} cấm phát âm — không profile "
                             f"hóa (fault injection không lọt)")
        return out
    if g.validate():
        out["errors"].extend(g.validate())
        return out
    chars, _n = load_vocab178()
    for u in g.units:
        for syl in u.syllables:
            tf = transform_vi(syl, by_id) if isinstance(syl, ViSyllable) \
                else transform_en(syl, by_id)
            out["errors"].extend(tf.errors)
            out["text"] += tf.text
            out["sidecar"].extend(tf.sidecar)
            out["loss"].extend(tf.loss)
    if not out["errors"]:
        out["conformance"] = check_conformance(out["text"], chars)
    return out


def g2p_stream(ir, fold_tab=None, by_id=None):
    """Envelope IR → dict g2p/0.1: metadata hash bắt buộc (schema inventory §7)
    + records + contract_errors tổng. Malformed envelope (null/[]/tokens[null])
    → contract_errors có cấu trúc, KHÔNG traceback (hậu kiểm v19 §3.3).
    fold_tab override → metadata.resource_override đánh dấu test-only kèm
    fingerprint bảng thực dùng (hậu kiểm v19 §5.2)."""
    by_id = by_id or _by_id()
    cerrs = check_contract(ir)
    override_md = None
    if fold_tab is not None:
        override_md = {"test_only": True,
                       "fold_override_sha256": hashlib.sha256(
                           json.dumps(sorted(fold_tab.items()), sort_keys=True,
                                      ensure_ascii=False)
                           .encode("utf-8")).hexdigest(),
                       "note": "output KHÔNG theo pin fold mặc định — chỉ "
                               "phục vụ test, provenance thuộc caller"}
    fold_tab = _fold_tab_with_pin(fold_tab)
    toks = ir.get("tokens", []) if isinstance(ir, dict) and \
        isinstance(ir.get("tokens"), list) else []
    recs = []
    for t in toks:
        if not isinstance(t, dict):
            recs.append(token_json(G2PToken(
                i=-1, surface="", cat="", route="", verbal="",
                status="unresolved", read_complete=False,
                contract_errors=[f"tokens phải là dict, nhận "
                                 f"{type(t).__name__}"]), by_id))
            continue
        recs.append(token_json(g2p_token(t, fold_tab), by_id))
    out = output_metadata(resource_override=override_md)
    out.update({"contract_errors": cerrs, "records": recs})
    return out


def stream_json(ir, fold_tab=None, by_id=None, pretty=False):
    """g2p_stream → JSON bytes (deterministic, sort_keys)."""
    return json.dumps(g2p_stream(ir, fold_tab, by_id), sort_keys=True,
                      ensure_ascii=False, indent=1 if pretty else None)


# ---------------------------------------------------------------- self-check

def selfcheck():
    """Bất biến nhanh: pins khớp, fold/spell load được, scope baseline đúng."""
    pins = _verify_resource_pins()
    assert pins["spell_tsv"]["approval_status"] == "seed_pending_owner"
    ft = load_fold()
    assert ft["chat"]["fold"] == "chất"
    assert "a" in _spell_vi()
    assert CA.scope_exclusion_status("níc") is not None
    assert CA.scope_exclusion_status("thuê") is None
    return True


if __name__ == "__main__":
    # CLI: stdin = envelope IR (1 JSON) → stdout g2p/0.1 JSON; contract_errors
    # → exit 1 dạng JSON lỗi hợp đồng, KHÔNG traceback (hậu kiểm v19 §3.3)
    try:
        selfcheck()
        blob = sys.stdin.read()
        if not blob.strip():
            print("stdin rỗng — cần envelope IR", file=sys.stderr)
            sys.exit(2)
    except SystemExit:
        raise
    except Exception as e:                      # pin/env fail → stderr rõ
        print(json.dumps({"contract_errors": [f"env/pin: {e}"], "records": []},
                         ensure_ascii=False))
        sys.exit(1)
    try:
        ir = json.loads(blob)
    except json.JSONDecodeError as e:
        print(json.dumps({"contract_errors": [f"stdin không phải JSON: {e}"],
                          "records": []}, ensure_ascii=False))
        sys.exit(1)
    out = g2p_stream(ir)
    print(json.dumps(out, sort_keys=True, ensure_ascii=False))
    sys.exit(1 if out["contract_errors"] or any(r["contract_errors"] or
             r["validation"] for r in out["records"]) else 0)
