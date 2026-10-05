# -*- coding: utf-8 -*-
"""test_cmu_en.py — kiểm fase C: CMUdict pin → EnSyllable master (nhánh en).

Kiểm:
  G1 pin: verify_pin() qua bản thật; provenance bản sao hỏng → SystemExit.
  G2 phủ: selfcheck() — mọi ký hiệu ARPABET trong dict có đường map; tên chữ map được.
  G3 gold từ: chuỗi master ID + stress pin literal (theo đúng bảng map).
  G4 syllabify maxonset_v1: cắt đúng các ca đối chiếu.
  G5 policy: OOV → spell có cấu trúc; ký tự không tên được liệt kê; no_nucleus.
  G6 record + profile: validate() sạch; transform_en đúng shape; conformance 178.
  G7 fingerprint: en_policy_hash ổn định; mutation sandbox (đổi map / bỏ map /
     hỏng pin) → hash ĐỔI + selfcheck/pin bắt được; khôi phục → về baseline.
  G8 artifact coverage: provenance khớp module + TSV; corpus có content-pin
     đã kiểm tại lần chạy (không chép hash lịch sử — C16-02).
  G9 phân loại miss (C16-02): ascii a-z tách riêng khỏi unicode alphabetic;
     qqz spell TRỌN; á/ít có ký tự unsupported; chữ số/dấu vào nhóm đúng.

Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/test_cmu_en.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unicodedata as U
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = sys.executable

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail and not ok else ""))


def main():
    import cmu_en as C
    from profiles import ProfileResult, transform_en, check_conformance
    import profiles as P

    # G1 — pin
    prov = C.verify_pin()
    check("G1 verify_pin qua bản thật", prov["sha256"].startswith("81917843")
          and prov["revision_commit"].startswith("7479086"))

    # G2 — phủ toàn bộ ký hiệu dict + tên chữ
    errs = C.selfcheck()
    check("G2 selfcheck: mọi ký hiệu ARPABET dict + tên chữ map được", errs == [],
          f"{errs[:5]}")

    # G3 — gold từ (pin literal; stress ở mức record)
    gold_flat = {
        "the": ("PHONE_DH", "PHONE_SCHWA"),
        "cat": ("PHONE_K", "PHONE_AE", "PHONE_T"),
        "hello": ("PHONE_H", "PHONE_SCHWA", "PHONE_L", "PHONE_OW"),
        "strengths": ("PHONE_S", "PHONE_T", "PHONE_R", "PHONE_OPEN_E",
                      "PHONE_NG", "PHONE_K", "PHONE_THETA", "PHONE_S"),
        "queue": ("PHONE_K", "PHONE_J", "PHONE_U"),
        "tom": ("PHONE_T", "PHONE_AA", "PHONE_M"),
    }
    cmu = C.load_cmu()
    for w, want in gold_flat.items():
        r = C.pronounce(w, cmu)
        check(f"G3 gold flat {w!r}", r.status == "ok" and C.flat_ids(r) == want,
              f"{r.status} {C.flat_ids(r)}")

    # record: dict pin — mục từ ĐẦU (verb R AH0 K AO1 R D) là mặc định; biến thể
    # (2) noun R EH1 K ER0 D giữ làm alternate (phát âm nào là mặc định của fase D)
    r = C.pronounce("record", cmu)
    s = r.syllables
    check("G3 record mặc định = entry đầu (verb): syl0 SCHWA unstressed",
          len(s) == 2 and s[0].onset == ("PHONE_R",)
          and s[0].nucleus == "PHONE_SCHWA" and s[0].stress == "",
          f"{s}")
    check("G3 record: syl1 AO1 primary, coda (R,D)",
          s[1].nucleus == "PHONE_OPEN_O" and s[1].stress == "STRESS_PRIMARY"
          and s[1].coda == ("PHONE_R", "PHONE_D"))
    check("G3 record: biến thể (2) noun EH1+ER0 tồn tại (3 entries pin)",
          len(cmu["record"]) == 3 and "EH1" in cmu["record"][1]
          and "ER0" in cmu["record"][1])
    r = C.pronounce("about", cmu)    # AH0 B AW1 T
    check("G3 about: AH0→SCHWA unstressed, AW1→PHONE_AU primary",
          r.syllables[0].nucleus == "PHONE_SCHWA" and r.syllables[0].stress == ""
          and r.syllables[1].nucleus == "PHONE_AU"
          and r.syllables[1].stress == "STRESS_PRIMARY")
    r = C.pronounce("her", cmu)      # HH ER1
    check("G3 her: ER1→PHONE_ER_STRESS", r.syllables[0].nucleus == "PHONE_ER_STRESS")
    r = C.pronounce("but", cmu)      # B AH1 T
    check("G3 but: AH1→PHONE_AH (không SCHWA)", r.syllables[0].nucleus == "PHONE_AH")

    # G4 — syllabify (maxonset_v1: run ≥2 → đầu vào coda trước, phần còn onset sau)
    r = C.pronounce("matrix", cmu)   # M EY1 T R IH0 K S
    check("G4 matrix: 2 âm tiết, run (T,R) cắt T→coda1, onset syl2=(R)",
          len(r.syllables) == 2 and r.syllables[0].coda == ("PHONE_T",)
          and r.syllables[1].onset == ("PHONE_R",)
          and r.syllables[1].nucleus == "PHONE_IH")
    r = C.pronounce("texts", cmu)    # T EH1 K S T S
    check("G4 texts: coda (K,S,T,S) sau nguyên âm cuối",
          r.syllables[0].coda == ("PHONE_K", "PHONE_S", "PHONE_T", "PHONE_S"))
    r = C.pronounce("inspire", cmu)  # IH2 N S P AY1 R
    check("G4 inspire: coda N — onset (S,P)",
          r.syllables[0].coda == ("PHONE_N",)
          and r.syllables[1].onset == ("PHONE_S", "PHONE_P"))

    # G5 — policy OOV/spell/no_nucleus
    assert "qqz" not in cmu
    r = C.pronounce("qqz", cmu)
    check("G5 qqz OOV → spell, 0 ký tự unsupported",
          r.status == "spell" and r.unsupported_chars == ()
          and [g[0].source_graphemes for g in r.spell_syllables] == ["q", "q", "z"])
    r = C.pronounce("zxq9", cmu)
    check("G5 zxq9: '9' liệt kê unsupported, không bịa tên",
          r.status == "spell" and r.unsupported_chars == ("9",))
    r = C.pronounce("hmm", cmu)
    check("G5 hmm → no_nucleus (không bịa nucleus)",
          r.status == "no_nucleus" and C.flat_ids(r) == () and r.reason)
    r = C.pronounce("zxq9", cmu)
    flat = C.flat_ids(r)
    check("G5 spell flat: z=(Z,I) x=(OPEN_E,K,S) q=(K,J,U)",
          flat == ("PHONE_Z", "PHONE_I", "PHONE_OPEN_E", "PHONE_K", "PHONE_S",
                   "PHONE_K", "PHONE_J", "PHONE_U"), f"{flat}")

    # G6 — record validate + profile conformance (I2)
    by_id = {r["id"]: r for r in __import__("inventory").load()}
    bad = []
    conf_chars, _n = P.load_vocab178()
    conf_bad = []
    for w in list(gold_flat) + ["record", "about", "her", "but", "matrix",
                                "inspire", "texts"]:
        r = C.pronounce(w, cmu)
        for syl in r.syllables:
            e = syl.validate(by_id)
            if e:
                bad.append((w, e))
            res = transform_en(syl, by_id)
            if res.errors:
                bad.append((w, res.errors))
            conf_bad += [f"{w}:{c!r}" for c in res.text if c not in conf_chars]
    check("G6 mọi gold record validate + transform_en không lỗi", bad == [],
          f"{bad[:3]}")
    check("G6 mọi gold text thuộc vocab 178", conf_bad == [], f"{conf_bad[:5]}")

    # G7 — fingerprint + mutation sandbox (phương pháp test_scope_policy)
    base_hash = C.en_policy_hash()
    check("G7 en_policy_hash tính được từ bản thật",
          len(base_hash) == 64 and base_hash == C.en_policy_hash())

    src = (HERE / "cmu_en.py").read_text(encoding="utf-8")
    anchor_aa = '    "AA": "PHONE_AA",\n'
    anchor_ao = '    "AO": "PHONE_OPEN_O",\n'
    assert src.count(anchor_aa) == 1 and src.count(anchor_ao) == 1

    def build_sandbox(td: Path) -> Path:
        g2p = td / "01_g2p"
        g2p.mkdir(exist_ok=True)
        for f in ("cmu_en.py", "inventory.py", "profiles.py"):
            shutil.copyfile(HERE / f, g2p / f)
        (td / "03_vendor" / "cmudict").mkdir(parents=True, exist_ok=True)
        for f in ("cmudict.dict", "cmudict_provenance.json", "LICENSE"):
            shutil.copyfile(ROOT / "03_vendor" / "cmudict" / f,
                            td / "03_vendor" / "cmudict" / f)
        (td / "02_data").mkdir(exist_ok=True)
        shutil.copyfile(ROOT / "02_data" / "inventory_ham.tsv",
                        td / "02_data" / "inventory_ham.tsv")
        return g2p

    DRIVER = '''# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, "01_g2p")
import cmu_en as C
mode = sys.argv[1]
if mode == "hash":
    print(C.en_policy_hash())
elif mode == "selfcheck":
    print(json.dumps(C.selfcheck()))
elif mode == "pronounce":
    print(json.dumps(list(C.flat_ids(C.pronounce(sys.argv[2])))))
elif mode == "pin":
    C.verify_pin()
'''

    def run(g2p: Path, mode: str, word=None):
        (g2p / "_mutation_driver.py").write_text(DRIVER, encoding="utf-8")
        args = [PY, "-B", "01_g2p/_mutation_driver.py", mode]
        if word:
            args.append(word)
        return subprocess.run(args, cwd=g2p.parent, capture_output=True,
                              text=True, env={"PYTHONDONTWRITEBYTECODE": "1",
                                              "PATH": "/usr/bin:/bin"})

    with tempfile.TemporaryDirectory(prefix="cmu_mutation_") as td:
        td = Path(td)
        g2p = build_sandbox(td)
        r = run(g2p, "hash")
        check("G7 sandbox baseline exit 0", r.returncode == 0, r.stderr[-200:])
        base_sb = r.stdout.strip()

        # M1 đổi đích map AA→AE: hash ĐỔI; pronounce 'tom' lộ PHONE_AE
        g2p = build_sandbox(td)
        f = g2p / "cmu_en.py"
        f.write_text(src.replace(anchor_aa, '    "AA": "PHONE_AE",\n'),
                     encoding="utf-8")
        h = run(g2p, "hash").stdout.strip()
        flat = json.loads(run(g2p, "pronounce", "tom").stdout)
        check("G7 M1 AA→AE: en_policy_hash ĐỔI", h != base_sb)
        check("G7 M1 AA→AE: 'tom' bị map sai thành PHONE_AE (hash là cửa bắt)",
              "PHONE_AE" in flat, f"{flat}")

        # M2 bỏ map AO: selfcheck đỏ + hash đổi
        g2p = build_sandbox(td)
        f = g2p / "cmu_en.py"
        f.write_text(src.replace(anchor_ao, ""), encoding="utf-8")
        h = run(g2p, "hash").stdout.strip()
        sc = json.loads(run(g2p, "selfcheck").stdout)
        check("G7 M2 bỏ AO: selfcheck báo nguyên âm không map",
              any("AO" in e for e in sc), f"{sc[:3]}")
        check("G7 M2 bỏ AO: en_policy_hash ĐỔI", h != base_sb)

        # M3 hỏng pin provenance (sha lệch): verify_pin SystemExit
        g2p = build_sandbox(td)
        pj = g2p.parent / "03_vendor" / "cmudict" / "cmudict_provenance.json"
        prov_copy = json.loads(pj.read_text(encoding="utf-8"))
        prov_copy["sha256"] = "0" * 64
        pj.write_text(json.dumps(prov_copy), encoding="utf-8")
        r = run(g2p, "pin")
        check("G7 M3 pin hỏng: SystemExit (không âm thầm dùng dict khác)",
              r.returncode != 0 and "lệch pin" in r.stderr, r.stderr[-150:])

        # khôi phục
        g2p = build_sandbox(td)
        check("G7 khôi phục: en_policy_hash về baseline",
              run(g2p, "hash").stdout.strip() == base_sb)

    # G8 — artifact coverage pin khớp module
    import cmu_coverage as COV
    prov_cov = json.loads(
        (ROOT / "02_data" / "en_branch" / "en_coverage_provenance.json")
        .read_text(encoding="utf-8"))
    tsv = ROOT / "02_data" / "en_branch" / "en_coverage.tsv"
    import hashlib
    check("G8 coverage provenance: en_policy_hash khớp module",
          prov_cov["en_policy_hash"] == C.en_policy_hash())
    check("G8 coverage provenance: tsv_sha256 khớp file",
          prov_cov["tsv_sha256"] == hashlib.sha256(tsv.read_bytes()).hexdigest())
    rows = [ln.split("\t") for ln in tsv.read_text(encoding="utf-8")
            .splitlines() if ln and not ln.startswith("@@")]
    c = prov_cov["counts"]
    check("G8 coverage: n_unique khớp số dòng TSV, in_cmu khớp cờ",
          len(rows) == c["n_unique"]
          and sum(1 for r in rows if r[2] == "1") == c["n_unique_in_cmu"])
    check("G8 coverage: freq tổng khớp provenance",
          sum(int(r[1]) for r in rows) == c["n_nonempty_tokens"])

    # G8b — corpus content-pin + taxonomy (C16-02)
    corpus = prov_cov["corpus"]
    pin_prov = json.loads((ROOT / "02_data" / "core_domain" /
                           "core_domain_provenance.json")
                          .read_text(encoding="utf-8"))
    pin_sha = next(s["sha256"] for s in pin_prov["source"]
                   if s["path"].endswith("corpus_ir_1M.jsonl.gz"))
    check("G8 corpus: provenance ghi content-pin corpus ĐÃ KIỂM tại lần chạy "
          "(khớp pin core_domain, không phải hash lịch sử chép tay)",
          corpus.get("sha256_verified_at_run") == pin_sha
          and "pin_source" in corpus)
    miss_keys = ("has_digit", "ascii_alpha_oov", "unicode_alpha_oov", "not_alpha")
    check("G8 taxonomy: 4 nhóm miss hiện diện và tổng unique = n_unique",
          all(c[f"n_unique_{k}"] >= 0 for k in miss_keys)
          and c["n_unique_in_cmu"] + sum(c[f"n_unique_{k}"] for k in miss_keys)
          == c["n_unique"])
    check("G8 taxonomy: freq chia đúng mẫu số token KHÔNG RỖNG (C16-02.1)",
          c["n_nonempty_tokens"] == c["n_en_tokens"] - c["n_empty_dropped"]
          and c["n_freq_in_cmu"] + sum(c[f"freq_{k}"] for k in miss_keys)
          == c["n_nonempty_tokens"])
    check("G8 taxonomy: spell-complete = đúng nhóm ascii a-z",
          c["n_unique_spell_complete_oov"] == c["n_unique_ascii_alpha_oov"]
          and c["freq_spell_complete_oov"] == c["freq_ascii_alpha_oov"])
    check("G8 nhãn: dictionary hit ≠ phát âm hoàn tất (no_nucleus được đếm)",
          "no_nucleus" in c.get("label_hit", "")
          and c["n_unique_no_nucleus_in_cmu"] >= 1)

    # G9 — phân loại miss + khả năng spell (probe reviewer v16 §5.1)
    check("G9 qqz → ascii_alpha_oov (thuần a-z)",
          COV.classify_miss("qqz") == "ascii_alpha_oov")
    r_qqz = C.pronounce("qqz")
    check("G9 qqz spell TRỌN token (unsupported_chars rỗng)",
          r_qqz.status == "spell" and r_qqz.unsupported_chars == ()
          and C.flat_ids(r_qqz), f"{r_qqz!r}")
    check("G9 á → unicode_alpha_oov (isalpha nhưng ngoài a-z)",
          COV.classify_miss("á") == "unicode_alpha_oov")
    r_a = C.pronounce("á")
    check("G9 á: không bịa âm tiết spell — unsupported_chars chứa 'á'",
          r_a.status == "spell" and not r_a.spell_syllables
          and "á" in r_a.unsupported_chars, f"{r_a!r}")
    check("G9 í → unicode_alpha_oov; 'ít' chỉ có tên chữ t",
          COV.classify_miss("ít") == "unicode_alpha_oov"
          and "PHONE_T" in set(C.flat_ids(C.pronounce("ít")))
          and "í" in C.pronounce("ít").unsupported_chars)
    check("G9 '12ab' → has_digit; 'a-b' → not_alpha",
          COV.classify_miss("12ab") == "has_digit"
          and COV.classify_miss("a-b") == "not_alpha")
    check("G9 hit no_nucleus vẫn trả no_nucleus (không biến thành ok)",
          C.pronounce("hmm").status == "no_nucleus")


    n_fail = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"cmu_en fase C: {len(CHECKS) - n_fail} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
