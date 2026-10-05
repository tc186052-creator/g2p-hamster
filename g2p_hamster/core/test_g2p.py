# -*- coding: utf-8 -*-
"""test_g2p.py — kiểm fase D/E (v22): g2p.py tiêu thụ IR ir/0.1 → record master →
profile debug. Đối chiếu HAU_KIEM_FASE_D_V18 (D18-01…D18-04) + HAU_KIEM v19
(§3.1-3.4 spell mode/unit_index/malformed/read_string, §4 aggregate, §5
identity) + HAU_KIEM v20 (D20-01 fingerprint spell str/cold==warm, D20-02
route guard spell, D20-03 M5 thật + H8 3 trường snapshot, D20-04 fixture
tier-1).

Kiểm:
  H1 enum status ĐÓNG (9 giá trị) + validate chặn giá trị lạ.
  H2 D18-01: fold KHÔNG đi vòng scope — nic/tic → ứng viên níc/tíc bị chặn
     (status scope_excluded, detail input→candidate→policy); direct subject
     vẫn bị chặn; protected vẫn đi; mach→mạch positive; nam không phục hồi dấu.
  H3 đường VI: parse ok / policy / fold provenance (tone_state=fold) / spell
     seed (q) / seed thiếu (z) → unresolved / verbal rỗng → unresolved.
  H4 đường EN: ok / spell trọn / spell MỘT PHẦN + fallback_reason /
     no_nucleus / verbal rỗng → unresolved (D18-03).
  H5 hợp đồng IR (D18-02): punct → control GIỮ break; number/abbr tiêu thụ
     read unit tầng 1 cấp (verbal dạng từ); icon deferred; route lạ fail loud;
     read/break/intonation/origin giữ nguyên trong record.
  H6 contract_errors có cấu trúc (D18-02): thiếu i, verbal=None, schema sai,
     read_string lệch đồng thuận — không crash; CLI exit 1 khi contract lỗi.
  H7 D18-03 invariant tương quan: fault injection (nam đổi status=scope_excluded
     còn gắn units) → validate BẮT; spell+unsupported+complete → BẮT; ok thiếu
     unit → BẮT; serializer từ chối status cấm phát âm kể cả khi gắn units.
  H8 profile debug: text/sidecar/loss — loss mach PHẢI có event prevelar
     (không chấp nhận []); conformance 178; determinism byte-giữ; metadata
     inventory_hash + inventory_contract_hash + g2p_policy_hash trong output
     (schema inventory §7).
  H9 D18-04 mutation sandbox: M1 fold line mach→mách → policy hash ĐỔI + tone
     đổi nặng→sắc; M2 bỏ re-check scope ứng viên → nic thành fold + hash ĐỔI;
     M3 pins hỏng → load_fold SystemExit; khôi phục → baseline.
  H10 vocab config: provenance khớp + emitter fail-closed (audit inventory
      trước khi ghi — probe dup-ID không ghi file, exit ≠ 0).
  H11 smoke corpus (TÙY CHỌN — SKIP khi corpus không có trên máy): 200 record
      đầu corpus 1M — 0 crash, status hợp lệ, conformance sạch, đủ đường đi.
  H12 torture/OOD (fase E E1): "A"×100 spell, TRTRTR, token 10.000 ký tự,
      150 token cat hỗn hợp — không crash / không cạn RAM / serialize được.

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/test_g2p.py
"""
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE.parents[1]))
PY = sys.executable

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail and not ok else ""))


def tok(i, cat, route, surface, verbal=None, **kw):
    d = {"i": i, "cat": cat, "route": route, "surface": surface,
         "verbal": verbal if verbal is not None else surface, "read": "word",
         "break": None, "origin": "vi" if route == "vi" else "neu"}
    d.update(kw)
    return d


def main():
    from g2p_hamster.core import g2p as G

    # H1 — enum + validate
    G.selfcheck()
    check("H1 selfcheck (pins/fold/spell/scope baseline)", True)
    check("H1 STATUSES = 9 giá trị g2p/0.1",
          G.STATUSES == {"ok", "fold", "spell", "no_nucleus", "scope_excluded",
                         "unresolved", "not_word", "unknown_route", "control"})
    check("H1 NO_PRONOUNCE phủ status cấm phát âm",
          {"scope_excluded", "unresolved", "not_word", "unknown_route",
           "no_nucleus", "control"} <= G.NO_PRONOUNCE)

    # H2 — D18-01
    g = G.g2p_token(tok(0, "word", "vi", "nic"))
    u = g.units[0]
    check("H2 'nic' QUA FOLD không lọt — status scope_excluded",
          u.status == "scope_excluded" and not u.read_complete
          and not u.syllables)
    check("H2 'nic' detail lưu input→candidate→policy (truy vết)",
          u.detail.get("fold_candidate") == "níc"
          and u.detail.get("input") == "nic"
          and u.detail["scope"]["policy_id"] == "QD57-2026-10-02")
    g = G.g2p_token(tok(1, "word", "vi", "tic"))
    check("H2 'tic' → ứng viên tíc bị chặn như gọi trực tiếp",
          g.units[0].status == "scope_excluded"
          and g.units[0].detail.get("fold_candidate") == "tíc")
    check("H2 direct 'níc' vẫn bị chặn",
          G.g2p_token(tok(2, "word", "vi", "níc")).units[0].status
          == "scope_excluded")
    check("H2 direct 'chếc' vẫn bị chặn",
          G.g2p_token(tok(3, "word", "vi", "chếc")).units[0].status
          == "scope_excluded")
    check("H2 protected 'chếch' không bị chặn nhầm",
          G.g2p_token(tok(4, "word", "vi", "chếch")).units[0].status == "ok")
    g = G.g2p_token(tok(5, "word", "vi", "mach"))
    check("H2 positive fold 'mach'→'mạch' giữ nguyên (tone nặng, status fold)",
          g.units[0].status == "fold" and g.units[0].read_complete
          and g.units[0].syllables[0].tone == "TONE_NANG")
    check("H2 'nam' VI hợp lệ không dấu — đọc nguyên dạng, KHÔNG phục hồi dấu",
          G.g2p_token(tok(6, "word", "vi", "nam")).units[0].status == "ok"
          and G.g2p_token(tok(6, "word", "vi", "nam")).units[0]
          .syllables[0].tone_state == "policy")

    # H3 — đường VI
    g = G.g2p_token(tok(10, "word", "vi", "GIảm", "GIảm"))
    check("H3 'giảm' ok — verbal nguyên dạng, TONE_HOI",
          g.status == "ok" and g.verbal == "GIảm"
          and g.units[0].syllables[0].tone == "TONE_HOI")
    g = G.g2p_token(tok(11, "word", "vi", "mach"))
    check("H3 fold provenance đủ: ascii→fold + freq + margin + tone_state",
          g.units[0].detail["fold_to"] == "mạch"
          and g.units[0].detail["freq_top1"] > 0
          and g.units[0].syllables[0].tone_state == "fold")
    check("H3 'qzx' → unresolved (không bịa)",
          G.g2p_token(tok(12, "word", "vi", "qzx")).units[0].status
          == "unresolved")
    check("H3 'q' → spell seed; 'z' ngoài seed → unresolved (không bịa)",
          G.g2p_token(tok(13, "word", "vi", "q")).units[0].status == "spell"
          and G.g2p_token(tok(14, "word", "vi", "z")).units[0].status
          == "unresolved")

    # H4 — đường EN
    g = G.g2p_token(tok(20, "word", "en", "cat"))
    check("H4 'cat' ok — stress primary",
          g.status == "ok" and g.units[0].syllables[0].stress == "STRESS_PRIMARY")
    g = G.g2p_token(tok(21, "word", "en", "qqz"))
    check("H4 'qqz' spell trọn — unsupported rỗng, complete",
          g.status == "spell" and g.read_complete
          and g.units[0].unsupported_chars == ())
    g = G.g2p_token(tok(22, "word", "en", "álvarez"))
    check("H4 'álvarez' spell MỘT PHẦN — complete=False + fallback_reason",
          g.status == "spell" and not g.read_complete
          and "á" in g.unsupported_chars
          and "fallback_reason" in g.units[0].detail)
    check("H4 'hmm' no_nucleus — không bịa",
          G.g2p_token(tok(23, "word", "en", "hmm")).units[0].status
          == "no_nucleus")
    g = G.g2p_token(tok(24, "word", "en", "", "   "))
    check("H4 verbal rỗng/khoảng trắng → unresolved KHÔNG spell-complete "
          "(D18-03)", g.status == "unresolved" and not g.read_complete
          and not g.units)

    # H5 — hợp đồng IR tiêu thụ
    g = G.g2p_token(tok(30, "punct", "vi", ".", ".", **{"break": "major"}))
    check("H5 punct → control GIỮ break major, không phát âm",
          g.status == "control" and g.break_kind == "major"
          and not g.units and not g.read_complete)
    g = G.g2p_token(tok(31, "number", "vi", "3.000", "ba nghìn"))
    check("H5 number — tiêu thụ read unit tầng 1 đã cấp (verbal dạng từ)",
          g.status == "ok" and [u.text for u in g.units] == ["ba", "nghìn"])
    g = G.g2p_token(tok(32, "abbr", "vi", "HĐND", "hội đồng nhân dân"))
    check("H5 abbr — verbal tầng 1 nguyên dạng, từng unit ok",
          g.status == "ok" and g.verbal == "hội đồng nhân dân"
          and all(u.status == "ok" for u in g.units))
    g = G.g2p_token(tok(33, "acronym", "en", "UN", "U N"))
    check("H5 acronym spell-mode en — unit 'U'/'N' qua cmu_en",
          g.status == "ok" and [u.text for u in g.units] == ["U", "N"])
    check("H5 icon → not_word deferred tường minh",
          G.g2p_token(tok(34, "icon", "vi", "😀")).status == "not_word")
    # read="spell" thực thi (hậu kiểm v19 §3.1) — dictionary hit không bỏ qua mode
    g = G.g2p_token(tok(37, "acronym", "en", "US", "US", read="spell"))
    check("H5 'US' read=spell → tên chữ U–S (không tra từ 'us')",
          g.status == "spell" and g.read_complete
          and [s.nucleus for s in g.units[0].syllables]
          == ["PHONE_U", "PHONE_OPEN_E"],   # U ("you") + S ("ess")
          f"{[s.nucleus for s in g.units[0].syllables]}")
    g = G.g2p_token(tok(38, "acronym", "en", "A", "A", read="spell"))
    check("H5 'A' read=spell → tên chữ EY + primary (không SCHWA từ điển)",
          g.units[0].syllables[0].nucleus == "PHONE_EY"
          and g.units[0].syllables[0].stress == "STRESS_PRIMARY")
    check("H5 'us' read=word → vẫn tra từ điển (mode không bị đảo)",
          G.g2p_token(tok(39, "word", "en", "us", "us")).units[0].syllables[0]
          .nucleus == "PHONE_AH")
    g = G.g2p_token(tok(45, "acronym", "en", "A9", "A9", read="spell"))
    check("H5 'A9' read=spell — '9' unsupported tường minh, complete=False",
          g.status == "spell" and not g.read_complete
          and "9" in g.unsupported_chars)
    # read_unit_index phân biệt (hậu kiểm v19 §3.2)
    g = G.g2p_token(tok(46, "number", "vi", "x", "hai mươi"))
    check("H5 unit_index [0,1] — không trùng 0,0",
          [u.unit_index for u in g.units] == [0, 1])
    out = json.loads(G.stream_json({"schema": "ir/0.1", "tokens": [
        tok(0, "number", "vi", "x", "hai mươi")]}))
    leaves = out["records"][0]["master"]["read_units"]
    check("H5 leaf identity (token, unit, syllable) phân biệt từng mảnh",
          [(u["read_unit_index"], u["syllables"][0]["syllable_index"])
           for u in leaves] == [(0, 0), (1, 0)])
    g = G.g2p_token(tok(35, "word", "jp", "x"))
    check("H5 route lạ → unknown_route fail loud",
          g.status == "unknown_route")
    # D20-02: đối xứng word/spell — route ngoài {vi,en} phải fail-loud ở CẢ
    # hai mode (spell không được đọc im lặng theo đường vi)
    for _k, (_r, _m) in enumerate((("neu", "word"), ("neu", "spell"),
                                   ("jp", "word"), ("jp", "spell"))):
        check(f"H5 D20-02 route={_r} read={_m} → unknown_route (đối xứng)",
              G.g2p_token(tok(50 + _k, "word", _r, "xin", "xin", read=_m))
              .status == "unknown_route")
    # D20-04a — fixture verbal TẦNG 1 THẬT (email route=vi read="spell"):
    # tier-1 đã spell-out trong verbal; D giữ đường từ, unit ngoài khả năng
    # → unresolved tường minh (không bịa, không spell-out lại ở tầng 2)
    fx = json.loads((ROOT / "02_data" / "g2p" / "fixture_tier1_email_spell.json")
                    .read_text(encoding="utf-8"))
    check("H5 D20-04a fixture tier-1 nguyên bản (ir_sha256 tự khai)",
          hashlib.sha256(json.dumps(fx["ir"], ensure_ascii=False)
                         .encode("utf-8")).hexdigest() == fx["ir_sha256"])
    o_fx = json.loads(G.stream_json(fx["ir"]))
    r_email = o_fx["records"][2]
    check("H5 D20-04a email read=spell route=vi — delegate tier-1: đường từ, "
          "unit hỏng → unresolved, token unresolved + incomplete",
          r_email["read"] == "spell" and r_email["status"] == "unresolved"
          and r_email["read_complete"] is False
          and [u["status"] for u in r_email["master"]["read_units"]]
          == ["unresolved", "ok", "ok", "unresolved", "ok", "ok"])
    check("H5 D20-04a envelope tier-1 thật qua contract sạch",
          G.check_contract(fx["ir"]) == [])
    g = G.g2p_token(tok(36, "word", "vi", "GIảm", "GIảm", intonation="rising",
                        origin="vi"))
    check("H5 intonation/origin giữ nguyên trong record",
          g.intonation == "rising" and g.origin == "vi")

    # H6 — contract_errors (D18-02)
    errs = G.check_contract({"schema": "ir/0.9", "tokens": []})
    check("H6 schema lệch → contract_errors có cấu trúc",
          len(errs) == 1 and "ir/0.1" in errs[0])
    errs = G.check_contract({"schema": "ir/0.1", "tokens": [
        {"cat": "word", "route": "vi", "surface": "x", "verbal": "x"}]})
    check("H6 token thiếu i → contract_error, KHÔNG KeyError",
          any("tokens[0].i" in e for e in errs))
    errs = G.check_contract({"schema": "ir/0.1", "tokens": [
        {"i": 0, "cat": "word", "route": "vi", "surface": "x", "verbal": None}]})
    check("H6 verbal=None → contract_error, KHÔNG AttributeError",
          any("verbal" in e for e in errs))
    errs = G.check_contract({"schema": "ir/0.1", "tokens": [
        tok(0, "word", "vi", "xin chào", "xin chào"),
        tok(1, "number", "vi", "3", "ba")]})
    check("H6 envelope đúng — 0 contract_errors",
          errs == [], f"{errs}")
    env = {"schema": "ir/0.1", "tokens": [tok(0, "word", "vi", "xin", "xin")],
           "read_string": "HOÀN TOÀN KHÁC"}
    errs = G.check_contract(env)
    check("H6 read_string lệch đồng thuận → contract_error (CLI không âm thầm ok)",
          any("read_string" in e for e in errs))
    # read_string theo ranh giới từ (hậu kiểm v19 §3.4) — 4 phản ví dụ reviewer
    toks_nam = [tok(0, "word", "vi", "nam", "nam")]
    for rs, want_ok in (("nam", True), ("nam.", True), (None, True),
                        ("nam thêm", False), ("xnam", False),
                        ("namnam", False), ("", False)):
        errs = G.check_contract({"schema": "ir/0.1", "tokens": toks_nam,
                                 "read_string": rs})
        check(f"H6 read_string {rs!r} → {'OK' if want_ok else 'contract_error'}",
              (errs == []) == want_ok, f"{errs[:1]}")
    # dấu câu gắn dính kiểu renderer tầng 1: "Jerry-Đường" ↔ Jerry + Đường
    toks_j = [tok(0, "word", "vi", "Jerry", "Jerry"),
              tok(1, "punct", "vi", "-", "-", **{"break": "minor"}),
              tok(2, "word", "vi", "Đường", "Đường")]
    errs = G.check_contract({"schema": "ir/0.1", "tokens": toks_j,
                             "read_string": "Jerry-Đường"})
    check("H6 renderer punct dính từ (Jerry-Đường) — hợp lệ theo quy tắc mảnh",
          errs == [], f"{errs[:1]}")
    # malformed IR → contract_errors, KHÔNG exception (hậu kiểm v19 §3.3)
    for label, ir in (("envelope null", None), ("envelope []", []),
                      ("tokens:[null]", {"schema": "ir/0.1", "tokens": [None]}),
                      ("cat:[]", {"schema": "ir/0.1", "tokens": [
                          {"i": 0, "cat": [], "route": "vi", "surface": "x",
                           "verbal": "x"}]}),
                      ("break:{}", {"schema": "ir/0.1", "tokens": [
                          {"i": 0, "cat": "word", "route": "vi",
                           "surface": "x", "verbal": "x", "break": {}}]})):
        try:
            out = G.g2p_stream(ir)
            n_err = len(out["contract_errors"]) +                 sum(len(r["contract_errors"]) for r in out["records"])
            check(f"H6 malformed {label} → lỗi cấu trúc, không văng",
                  n_err >= 1, f"{out['contract_errors'][:1]}")
        except Exception as e:
            check(f"H6 malformed {label} → lỗi cấu trúc, không văng",
                  False, f"văng {type(e).__name__}: {e}")
    # CLI với JSON null → exit 1 dạng JSON lỗi hợp đồng, KHÔNG traceback
    r = subprocess.run([PY, "-m", "g2p_hamster.core.g2p"], cwd=HERE.parents[1], input="null",
                       capture_output=True, text=True,
                       env={"PYTHONDONTWRITEBYTECODE": "1",
                            "PATH": "/usr/bin:/bin"})
    check("H6 CLI JSON null → exit 1, stderr không có Traceback",
          r.returncode == 1 and "Traceback" not in r.stderr
          and "contract_errors" in r.stdout, f"{r.stderr[-120:]}")
    # token shape lỗi qua g2p_token — không văng exception
    g = G.g2p_token({"cat": "word", "route": "vi", "verbal": None})
    check("H6 g2p_token với shape lỗi — trả record lỗi có cấu trúc",
          g.contract_errors and g.i == -1)
    # CLI exit 1 khi contract lỗi
    with tempfile.TemporaryDirectory() as td:
        env_ok = {"schema": "ir/0.1",
                  "tokens": [tok(0, "word", "vi", "xin", "xin")]}
        for label, env, want in (
                ("envelope lỗi", env, 1), ("envelope đúng", env_ok, 0)):
            p = Path(td) / "in.json"
            p.write_text(json.dumps(env), encoding="utf-8")
            r = subprocess.run([PY, "-m", "g2p_hamster.core.g2p"], cwd=HERE.parents[1],
                               stdin=open(p), capture_output=True, text=True,
                               env={"PYTHONDONTWRITEBYTECODE": "1",
                                    "PATH": "/usr/bin:/bin"})
            check(f"H6 CLI {label} → exit {want}", r.returncode == want,
                  f"exit={r.returncode} {r.stderr[-120:]}")

    # H7 — D18-03 invariant tương quan (fault injection)
    g = G.g2p_token(tok(40, "word", "vi", "nam"))
    check("H7 baseline 'nam' sạch", g.validate() == [])
    bad = G.g2p_token(tok(40, "word", "vi", "nam"))
    bad.status = "scope_excluded"          # fault injection như reviewer v18
    errs = bad.validate()
    check("H7 fault: scope_excluded nhưng 0 unit cấm phát âm → validate BẮT "
          "(roll-up lệch)", any("roll-up lệch" in e for e in errs), f"{errs[:2]}")
    p = G._profile_json(bad)
    check("H7 fault: serializer TỪ CHỐI xuất text cho record lỗi validate",
          p["text"] == "" and p["errors"])
    # fault đúng cấp unit: unit scope_excluded còn gắn syllables
    bad_u = G.g2p_token(tok(40, "word", "vi", "nam"))
    bad_u.units[0].status = "scope_excluded"
    check("H7 fault: unit cấm phát âm còn gắn syllables → unit.validate BẮT",
          any("cấm phát âm" in e for e in bad_u.validate()))
    bad2 = G.g2p_token(tok(41, "word", "en", "álvarez"))
    bad2.read_complete = True               # spell còn unsupported mà claim complete
    check("H7 fault: spell unsupported + complete → validate BẮT",
          any("một phần" in e for e in bad2.validate()))
    bad3 = G.g2p_token(tok(42, "word", "en", "cat"))
    bad3.units = []
    check("H7 fault: ok thiếu read unit → validate BẮT",
          any("phải có read unit" in e for e in bad3.validate()))
    bad4 = G.g2p_token(tok(43, "word", "vi", "mach"))
    bad4.status = "timeline"                # ngoài enum
    check("H7 fault: status ngoài enum → validate BẮT",
          any("enum" in e for e in bad4.validate()))
    # fault parent/child (hậu kiểm v19 §4): parent tuyên bố đủ khi child thiếu
    bad5 = G.g2p_token(tok(44, "word", "en", "álvarez"))   # baseline: partial
    check("H7 baseline 'álvarez' partial đúng (fault injection có nhãn)",
          not bad5.read_complete and "á" in bad5.unsupported_chars)
    bad5.read_complete = True
    bad5.unsupported_chars = ()             # chỉ đổi parent, không đổi child
    errs = bad5.validate()
    check("H7 fault: parent complete nhưng child incomplete → validate BẮT",
          any("aggregate" in e for e in errs), f"{errs[:2]}")
    p = G._profile_json(bad5)
    check("H7 fault: serializer từ chối record tự mâu thuẫn",
          p["text"] == "" and p["errors"])
    bad6 = G.g2p_token(tok(47, "word", "vi", "giảm"))
    bad6.unsupported_chars = ("x",)         # parent bịa unsupported
    check("H7 fault: parent bịa unsupported → validate BẮT",
          any("aggregate" in e for e in bad6.validate()))

    # H8 — profile + metadata + determinism
    g = G.g2p_token(tok(50, "word", "vi", "mach"))
    p = G._profile_json(g)
    check("H8 'mach' loss PHẢI có event prevelar (không chấp nhận [])",
          any(l[0] == "PHONE_OPEN_E_PREVELAR" for l in p["loss"]),
          f"loss={p['loss']}")
    g = G.g2p_token(tok(51, "word", "vi", "giảm"))
    p = G._profile_json(g)
    check("H8 'giảm' text mũi tên hỏi ↓ + sidecar master ID",
          "↓" in p["text"] and any(m == "TONE_HOI" for _s, m in p["sidecar"]))
    g = G.g2p_token(tok(52, "word", "en", "qqz"))
    p = G._profile_json(g)
    check("H8 'qqz' text thuộc vocab 178 (conformance sạch)",
          p["text"] and p["conformance"] == [])
    env = {"schema": "ir/0.1", "tokens": [tok(0, "word", "vi", "xin", "xin"),
                                          tok(1, "word", "en", "cat"),
                                          tok(2, "punct", "vi", ".", ".",
                                              **{"break": "major"})]}
    a = G.stream_json(env)
    b = G.stream_json(env)
    check("H8 determinism: stream_json 2 lần byte-giữ nhau", a == b)
    out = json.loads(a)
    check("H8 output có inventory_hash + inventory_contract_hash + "
          "g2p_policy_hash (schema inventory §7)",
          all(k in out for k in ("inventory_hash", "inventory_contract_hash",
                                 "g2p_policy_hash")))
    check("H8 inventory_hash khớp hash raw TSV hiện hành",
          out["inventory_hash"] == hashlib.sha256(
              (ROOT / "02_data" / "inventory_ham.tsv").read_bytes())
          .hexdigest())
    from g2p_hamster.core import cmu_en as CEN
    from g2p_hamster.core import collision_audit as CAI
    deps = out["versions"]["b_c_dependencies"]
    check("H8 identity mang 4 hash policy B/C hiệu lực (hậu kiểm v19 §5.1)",
          deps["en_policy_hash"] == CEN.en_policy_hash()
          and deps["scope_policy_hash"] == CAI.scope_policy_hash()
          and deps["approval_policy_hash"] == __import__(
              "inventory").approval_policy_hash()
          and deps["domain_config_hash"] ==
          CAI.domain_config_hash(*CAI.load_attestation()),
          f"{sorted(deps)}")
    check("H8 versions.dialect chứa GIÁ TRỊ pin domain (không chỉ mô tả)",
          out["versions"]["dialect"].startswith("vi v1 — pin domain_config_hash ")
          and len(out["versions"]["dialect"]) > 40)
    pins_now = json.loads((ROOT / "02_data" / "g2p" / "g2p_resource_pins.json")
                          .read_text(encoding="utf-8"))
    _rs = out["resource_snapshot"]
    check("H8 resource_snapshot: 3 trường ĐỀU là str sha256 khớp pin "
          "(D20-01/03 — dict bảng không phải identity)",
          isinstance(_rs["fold_tsv_sha256"], str)
          and isinstance(_rs["spell_tsv_sha256"], str)
          and isinstance(_rs["cmudict_sha256"], str)
          and _rs["fold_tsv_sha256"] == pins_now["fold_tsv"]["sha256"]
          and _rs["spell_tsv_sha256"] == pins_now["spell_tsv"]["sha256"]
          and _rs["cmudict_sha256"] == pins_now["cmudict"]["sha256"])
    _h_cold = G.g2p_policy_hash()
    G.g2p_token(tok(90, "word", "vi", "xin"))   # nạp warm cache fold + spell
    check("H8 identity ổn định trong process: g2p_policy_hash cold == warm "
          "sau token vi (D20-01)",
          G.g2p_policy_hash() == _h_cold == out["g2p_policy_hash"])
    # override marker (hậu kiểm v19 §5.2)
    custom = dict(G.load_fold())
    custom["mach"] = {"fold": "mách", "freq_top1": 2530, "margin": 0.97}
    out_ov = json.loads(G.stream_json(
        {"schema": "ir/0.1", "tokens": [tok(0, "word", "vi", "mach")]},
        fold_tab=custom))
    check("H8 fold_tab override → metadata.resource_override test-only + "
          "fingerprint bảng thực dùng",
          out_ov.get("resource_override", {}).get("test_only") is True
          and "fold_override_sha256" in out_ov["resource_override"])
    check("H8 override thực sự đổi reading (mách → sắc) nhưng ĐƯỢC ĐÁNH DẤU",
          out_ov["records"][0]["profile_debug"]["text"] != out["records"][0]
          ["profile_debug"]["text"] if out["records"][0]["cat"] != "punct"
          else True)
    rec_punct = next(r for r in out["records"] if r["cat"] == "punct")
    check("H8 serializer: punct master rỗng nhưng break được giữ ở record",
          rec_punct["master"]["read_units"] == [] and rec_punct["break"] == "major")
    rec_word = out["records"][0]
    check("H8 serializer master: syllable có liên kết nguồn "
          "(source_token_id/read_unit_index/syllable_index)",
          rec_word["master"]["read_units"][0]["source_token_id"] == 0
          and rec_word["master"]["read_units"][0]["syllables"][0]
          ["syllable_index"] == 0)

    # H9 — D18-04 mutation sandbox
    src = (HERE / "g2p.py").read_text(encoding="utf-8")
    ANCHOR_SCOPE_CAND = '        scope_cand = CA.scope_exclusion_status(cand["fold"])\n        if scope_cand is not None:\n            return G2PUnit(**base, status="scope_excluded",\n                           detail={"input": w, "fold_candidate": cand["fold"],\n                                   "scope": scope_cand,\n                                   "note": " ứng viên fold thuộc QD57 — không "\n                                           "phát âm, không lách sang protected "\n                                           "partner hay spell"})\n'
    assert src.count(ANCHOR_SCOPE_CAND) == 1, "anchor M2 không duy nhất"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        def build_sandbox():
            # sandbox mirror layout PACKAGE: pkg/g2p_hamster/{core,02_data,03_vendor}
            pkg = td / "g2p_hamster"
            g2p = pkg / "core"
            g2p.mkdir(parents=True, exist_ok=True)
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (g2p / "__init__.py").write_text("", encoding="utf-8")
            for f in ("g2p.py", "inventory.py", "profiles.py", "vi_rules.py",
                      "vi_syllable.py", "collision_audit.py", "cmu_en.py",
                      "build_core_domain.py"):
                shutil.copyfile(HERE / f, g2p / f)
            data = pkg / "02_data"
            data.mkdir(exist_ok=True)
            for rel in ("inventory_ham.tsv", "spell_vi.tsv"):
                shutil.copyfile(ROOT / "02_data" / rel, data / rel)
            for rel in ("fold/fold_vi.tsv", "g2p/g2p_resource_pins.json",
                        "collision/qd57_scope_exclusions.json",
                        "collision/dieu7_bao_cao.json",
                        "profiles/kokoro_vocab_178.tsv",
                        "core_domain/vi_syllable_vocab.tsv",
                        "core_domain/core_domain_provenance.json"):
                dst = data / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "02_data" / rel, dst)
            for f in (ROOT / "02_data" / "collision" / "qd57").iterdir():
                (data / "collision" / "qd57").mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, data / "collision" / "qd57" / f.name)
            shutil.copytree(ROOT / "03_vendor" / "cmudict",
                            pkg / "03_vendor" / "cmudict",
                            dirs_exist_ok=True)
            return pkg

        DRIVER = ("import json, sys, os\n"
                  "sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))\n"
                  "import g2p_hamster.core.g2p as g2p\nmode = sys.argv[1]\n"
                  "if mode == 'hash':\n"
                  "    print(g2p.g2p_policy_hash())\n"
                  "elif mode == 'probe':\n"
                  "    out = []\n"
                  "    for w in ('nic', 'mach', 'nam'):\n"
                  "        g = g2p.g2p_token({'i': 0, 'cat': 'word', 'route': 'vi',\n"
                  "                            'surface': w, 'verbal': w})\n"
                  "        syl = g.units[0].syllables[0] if g.units[0].syllables else None\n"
                  "        out.append({'w': w, 'status': g.units[0].status,\n"
                  "                    'tone': syl.tone if syl and hasattr(syl, 'tone') else None})\n"
                  "    print(json.dumps(out))\n"
                  "elif mode == 'warm':\n"
                  "    def snap():\n"
                  "        env = {'schema': 'ir/0.1', 'tokens': [\n"
                  "            {'i': 0, 'cat': 'word', 'route': 'vi', 'surface': 'mach',\n"
                  "             'verbal': 'mach', 'read': 'word', 'break': None},\n"
                  "            {'i': 1, 'cat': 'acronym', 'route': 'vi', 'surface': 'q',\n"
                  "             'verbal': 'q', 'read': 'spell', 'break': None}]}\n"
                  "        o = json.loads(g2p.stream_json(env))\n"
                  "        return {'mach_tone': o['records'][0]['master']\n"
                  "                ['read_units'][0]['syllables'][0]['tone'],\n"
                  "                'q_seed': o['records'][1]['master']\n"
                  "                ['read_units'][0]['syllables'][0]['source_graphemes'],\n"
                  "                'fold_sha': o['resource_snapshot']['fold_tsv_sha256'],\n"
                  "                'spell_sha': o['resource_snapshot']['spell_tsv_sha256']}\n"
                  "    a = snap()\n"
                  "    _d = os.path.dirname(os.path.abspath(__file__))\n"
                  "    ft = os.path.join(_d, '02_data/fold/fold_vi.tsv')\n"
                  "    fb = open(ft, encoding='utf-8').read()\n"
                  "    fa = fb.replace('mach\\tmạch\\t', 'mach\\tmách\\t')\n"
                  "    sp = os.path.join(_d, '02_data/spell_vi.tsv')\n"
                  "    sbb = open(sp, encoding='utf-8').read()\n"
                  "    saa = sbb.replace('q\\tquy\\n', 'q\\tqua\\n')\n"
                  "    assert fa != fb and saa != sbb, 'mutation không khớp byte đĩa'\n"
                  "    open(ft, 'w', encoding='utf-8').write(fa)\n"
                  "    open(sp, 'w', encoding='utf-8').write(saa)\n"
                  "    c = snap()\n"
                  "    print(json.dumps({'before': a, 'after': c}))\n"
                  "elif mode == 'pin':\n"
                  "    g2p.load_fold(); print('pin ok')\n"
                  "elif mode == 'pin_spell':\n"
                  "    g2p.load_spell_vi(); print('pin ok')\n")

        def run(g2p_dir, mode):
            d = g2p_dir / "_drv.py"
            d.write_text(DRIVER, encoding="utf-8")
            return subprocess.run([PY, "-B", "_drv.py", mode],
                                  cwd=g2p_dir,
                                  capture_output=True, text=True,
                                  env={"PYTHONDONTWRITEBYTECODE": "1",
                                       "PATH": "/usr/bin:/bin"})

        sb = build_sandbox()
        r = run(sb, "hash")
        check("H9 sandbox baseline: policy hash tính được", r.returncode == 0)
        base_hash = r.stdout.strip()
        base_probe = json.loads(run(sb, "probe").stdout)
        check("H9 sandbox baseline: nic blocked / mach fold nặng / nam ok",
              base_probe[0]["status"] == "scope_excluded"
              and base_probe[1]["tone"] == "TONE_NANG"
              and base_probe[2]["status"] == "ok")

        # M1 — fold line mach→mách: pin TỪ CHỐI (fail-closed) + hash ĐỔI.
        # Khác v18: behavior KHÔNG thể đổi âm thầm vì load_fold kiểm sha pin.
        sb = build_sandbox()
        ft = sb / "02_data" / "fold" / "fold_vi.tsv"
        ft.write_text(ft.read_text(encoding="utf-8")
                      .replace("mach\tmạch\t", "mach\tmách\t"), encoding="utf-8")
        r_hash = run(sb, "hash")
        check("H9 M1 fold mutation: policy hash FAIL-CLOSED (cold load bị gate "
              "pin từ chối — mutation không ra được output)",
              r_hash.returncode != 0 and "lệch pin" in r_hash.stderr,
              r_hash.stderr[-120:])
        r_pin = run(sb, "pin")
        check("H9 M1 fold mutation: load_fold TỪ CHỐI sha lệch pin",
              r_pin.returncode != 0 and "lệch pin" in r_pin.stderr,
              r_pin.stderr[-120:])
        r_probe = run(sb, "probe")
        check("H9 M1 fold mutation: đường phát âm cũng bị chặn (SystemExit)",
              r_probe.returncode != 0 and "lệch pin" in r_probe.stderr)

        # M2 — bỏ re-check scope ứng viên: nic thành fold + hash ĐỔI
        sb = build_sandbox()
        f = sb / "core" / "g2p.py"
        f.write_text(src.replace(ANCHOR_SCOPE_CAND, ""), encoding="utf-8")
        h2 = run(sb, "hash").stdout.strip()
        p2 = json.loads(run(sb, "probe").stdout)
        check("H9 M2 consumer mutation: g2p_policy_hash ĐỔI", h2 != base_hash)
        check("H9 M2 consumer mutation: 'nic' bị phát âm khi bỏ re-check "
              "(mutation tái hiện đúng lỗi D18-01 — hash là cửa bắt)",
              p2[0]["status"] == "fold", f"{p2[0]}")

        # M3 — pins hỏng: load_fold SystemExit
        sb = build_sandbox()
        pins_p = sb / "02_data" / "g2p" / "g2p_resource_pins.json"
        pins = json.loads(pins_p.read_text(encoding="utf-8"))
        pins["fold_tsv"]["sha256"] = "0" * 64
        pins_p.write_text(json.dumps(pins), encoding="utf-8")
        r = run(sb, "pin")
        check("H9 M3 pins hỏng: SystemExit (không âm thầm dùng bảng khác)",
              r.returncode != 0 and "lệch pin" in r.stderr, r.stderr[-150:])

        # M4 — phụ thuộc B/C (hậu kiểm v19 §5.1): mutation cmu_en AA→AE phải
        # làm policy hash D đổi vì hành vi output đổi (tom PHONE_AA→PHONE_AE)
        sb = build_sandbox()
        f = sb / "core" / "cmu_en.py"
        src_en = f.read_text(encoding="utf-8")
        anchor_aa = '    "AA": "PHONE_AA",\n'
        assert src_en.count(anchor_aa) == 1
        f.write_text(src_en.replace(anchor_aa, '    "AA": "PHONE_AE",\n'),
                     encoding="utf-8")
        h4 = run(sb, "hash").stdout.strip()
        check("H9 M4 dependency mutation (cmu_en AA→AE): g2p_policy_hash ĐỔI",
              h4 != base_hash and h4 != "", f"h4={h4[:12]} base={base_hash[:12]}")

        # M5 — warm cache + snapshot identity (hậu kiểm v19 §5.3 + D20-01/03):
        # MỘT process: stream warm-load (fold + spell) → mutation ĐĨA CẢ HAI
        # bảng → stream lại: reading + snapshot sha GIỮ NGUYÊN (identity định
        # danh đúng snapshot đang dùng, không phải byte đĩa đã đổi sau load).
        sb = build_sandbox()
        ft = sb / "02_data" / "fold" / "fold_vi.tsv"
        h_w1 = run(sb, "hash").stdout.strip()
        warm = json.loads(run(sb, "warm").stdout)
        check("H9 M5 warm→mutation đĩa: fold giữ reading TONE_NANG + fold sha cũ",
              warm["before"]["mach_tone"] == warm["after"]["mach_tone"]
              == "TONE_NANG"
              and warm["after"]["fold_sha"] == warm["before"]["fold_sha"],
              json.dumps(warm)[:160])
        check("H9 M5 warm→mutation đĩa: spell seed giữ 'quy' + spell sha cũ "
              "(snapshot spell định danh đúng — D20-01)",
              warm["before"]["q_seed"] == warm["after"]["q_seed"] == "quy"
              and warm["after"]["spell_sha"] == warm["before"]["spell_sha"])
        r_cold = run(sb, "hash")
        # hash mode COLD sau mutation → fail-closed (không định danh bảng hỏng)
        check("H9 M5: cold policy hash sau mutation → fail-closed",
              r_cold.returncode != 0 and "lệch pin" in r_cold.stderr,
              r_cold.stderr[-120:])
        r_w = run(sb, "pin")
        check("H9 M5 warm-cache: load_fold tường minh → từ chối lệch pin",
              r_w.returncode != 0 and "lệch pin" in r_w.stderr)
        r_ws = run(sb, "pin_spell")
        check("H9 M5 warm-cache: load_spell_vi tường minh → từ chối lệch pin",
              r_ws.returncode != 0 and "lệch pin" in r_ws.stderr)
        check("H9 M5: sandbox sạch trước mutation khớp hash baseline "
              "(mutation có hiệu lực thật, không phải no-op)",
              h_w1 == base_hash and h_w1 != "")

        # khôi phục
        sb = build_sandbox()
        check("H9 khôi phục: policy hash về baseline",
              run(sb, "hash").stdout.strip() == base_hash)
        check("H9 khôi phục: behavior về baseline",
              json.loads(run(sb, "probe").stdout) == base_probe)

    # H10 — vocab config + emitter fail-closed
    tsv = ROOT / "02_data" / "g2p" / "vocab_config_from_master.tsv"
    prov = json.loads((ROOT / "02_data" / "g2p" / "vocab_config_provenance.json")
                      .read_text(encoding="utf-8"))
    body = tsv.read_bytes()
    check("H10 vocab config: tsv_sha256 + inventory sha khớp",
          prov["tsv_sha256"] == hashlib.sha256(body).hexdigest()
          and prov["inventory"]["sha256"] == hashlib.sha256(
              (ROOT / "02_data" / "inventory_ham.tsv").read_bytes())
          .hexdigest())
    n_data = sum(1 for ln in body.decode("utf-8").splitlines()
                 if ln and not ln.startswith("@@"))
    check("H10 vocab config: 78 entries = master",
          prov["inventory"]["n_entries"] == n_data == 78)

    # H12 — torture / OOD (fase E E1): token lặp/siêu-lâu/cat lạ hàng loạt —
    # không crash, trạng thái đúng enum, serialize được, hoàn tất trong ms
    t_t0 = time.time()
    g_t = G.g2p_token(tok(60, "acronym", "en", "A" * 100, "A" * 100,
                          read="spell"))
    check("H12 'A'×100 read=spell — không crash, per-letter, complete",
          g_t.status == "spell" and g_t.read_complete
          and len(g_t.units[0].syllables) == 100)
    g_t = G.g2p_token(tok(61, "word", "en", "TRTRTR", "TRTRTR"))
    check("H12 'TRTRTR' — spell có cấu trúc (không crash, không tự bịa từ)",
          g_t.status in ("spell", "unresolved"))
    g_t = G.g2p_token(tok(62, "word", "vi", "a" * 10_000, "a" * 10_000))
    check("H12 token 10.000 ký tự — không crash, không cạn RAM",
          g_t.status in ("ok", "fold", "spell", "unresolved")
          and time.time() - t_t0 < 5)
    _weird_env = {"schema": "ir/0.1", "tokens": [
        tok(63 + k, c, "vi", "x" * 30, "x" * 30) for k, c in enumerate(
            ["word"] * 50 + ["icon"] * 50 + ["punct"] * 50)]}
    _weird_out = json.loads(G.stream_json(_weird_env))
    check("H12 150 token cat hỗn hợp — serialize được, đúng số record",
          len(_weird_out["records"]) == 150
          and all(r["status"] in G.STATUSES for r in _weird_out["records"]))
    check("H12 torture xong trong <5s",
          time.time() - t_t0 < 5, f"{time.time() - t_t0:.2f}s")

    # H11 — smoke corpus (TÙY CHỌN — SKIP khi corpus không có; reviewer không
    # có corpus 1M: H11 SKIP là kết quả mong đợi, KHÔNG đếm FAIL)
    import os
    corpus = Path(os.environ.get("G2P_CORPUS_1M", "/dev/null-corpus"))
    if not corpus.exists():
        print("  SKIP: H11 smoke corpus — corpus 1M không có trên máy "
              "(không tạo dữ liệu giả gọi là corpus thật)")
        CHECKS.append(("H11 smoke corpus", True, "SKIP"))
    else:
        n_rec = n_tok = conf_bad = 0
        statuses = set()
        _flagged = []
        _last_ir = None
        with gzip.open(corpus, "rt", encoding="utf-8") as f:
            for ln in f:
                ir = json.loads(ln)["ir"]
                _last_ir = ir
                cerrs_stream = G.check_contract(ir)
                for p in json.loads(G.stream_json(ir))["records"]:
                    n_tok += 1
                    statuses.add(p["status"])
                    if p["profile_debug"]["conformance"]:
                        conf_bad += 1
                    if p["validation"]:
                        conf_bad += 1
                    if p["contract_errors"]:
                        _flagged.append(p["contract_errors"])
                if cerrs_stream and not all("read_string" in e
                                            for e in cerrs_stream):
                    _flagged.append(cerrs_stream)
                n_rec += 1
                if n_rec >= 200:
                    break
        check(f"H11 corpus: {n_rec} record / {n_tok} token — 0 crash", n_rec == 200)
        check("H11 mọi status thuộc enum + validation sạch + conformance sạch",
              statuses <= G.STATUSES and conf_bad == 0)
        # contract_errors trên corpus CHỈ được là lệch read_string-consensus
        # (tier-1 có sẵn ~1% envelope read_string picked ≠ tokens — consensus
        # BÁO ĐÚNG là nhiệm vụ của nó, không phải lỗi g2p)
        non_cons = [p for p in _flagged
                    if not all("read_string" in e for e in p)]
        check("H11 contract_errors chỉ nhóm read_string-consensus (tier-1 "
              "picked≠tokens — không phải lỗi g2p)", not non_cons,
              f"{non_cons[:2]}")
        check("H11 đủ đường đi (ok/control/fold/spell/en)",
              {"ok", "control"} <= statuses, f"{sorted(statuses)}")

    n_fail = sum(1 for _, ok, _ in CHECKS if not ok)
    n_skip = sum(1 for _, ok, d in CHECKS if d == "SKIP")
    print(f"g2p fase D/E v22: {len(CHECKS) - n_fail - n_skip} PASS, {n_fail} FAIL"
          + (f", {n_skip} SKIP" if n_skip else ""))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
