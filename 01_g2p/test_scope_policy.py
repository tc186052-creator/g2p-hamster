# -*- coding: utf-8 -*-
"""test_scope_policy.py — probe mutation cho policy scope v1 (vòng 6.5, hậu kiểm
v14 §6.2/§6.3: R14-01 + R14-02). Phương pháp như reviewer_probes_v14: mutation
trên BẢN SAO RIÊNG trong thư mục tạm (cây 01_g2p/02_data tối thiểu), chạy
subprocess import mới — không đụng production, không ghi đè report thật.

Kiểm:
  T1 baseline: audit nguyên bản exit 0; boundary 39 excluded + 37 protected, 0 lỗi.
  T2 audit bắt lỗi boundary (§6.2):
     - M1 cho subject đi qua (chèn `if w == "thue": return None`) → FAIL exit≠0;
     - M2 chặn nhầm protected (chèn trả excluded cho "thuê") → FAIL exit≠0;
     - M3 đổi DỮ LIỆU ledger bản sao (swap excluded/protected của beo/beu) → FAIL.
  T3 fingerprint nhạy (§6.3): scope_policy_hash VÀ domain_config_hash ĐỔI ở
     M1/M2/M3 so với baseline; khôi phục nguyên bản → về đúng giá trị baseline.

Exit 0 = tất cả probe đạt. Chạy:
  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/test_scope_policy.py
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = sys.executable

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail and not ok else ""))


ANCHOR = '    w = U.normalize("NFC", word).lower()\n'
MUT_PASS_THROUGH = ANCHOR + '    if w == "thue":\n        return None\n'
MUT_BLOCK_PROTECTED = ANCHOR + (
    '    if w == "thuê":\n'
    '        return {"status": "scope_excluded_v1", "policy_id": "MUTATION",\n'
    '                "pair": ["thue", "thuê"], "subject": "mutation probe",\n'
    '                "protected": "mutation probe", "reason": "mutation probe"}\n')


def build_sandbox(td: Path) -> Path:
    """Cây tối thiểu để collision_audit chạy: module + dữ liệu pin (copy hoặc
    symlink — chỉ ĐỌC; report mutated ghi vào sandbox, không đụng production)."""
    g2p = td / "01_g2p"
    g2p.mkdir(exist_ok=True)
    for f in ("collision_audit.py", "inventory.py", "vi_rules.py", "vi_syllable.py",
              "build_core_domain.py"):
        shutil.copyfile(HERE / f, g2p / f)
    data = td / "02_data"
    (data / "collision" / "qd57").mkdir(parents=True, exist_ok=True)
    (data / "core_domain").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "02_data" / "collision" / "qd57_scope_exclusions.json",
                    data / "collision" / "qd57_scope_exclusions.json")
    for f in (ROOT / "02_data" / "collision" / "qd57").iterdir():
        shutil.copyfile(f, data / "collision" / "qd57" / f.name)
    for f in ("vi_syllable_vocab.tsv", "core_domain_provenance.json"):
        shutil.copyfile(ROOT / "02_data" / "core_domain" / f,
                        data / "core_domain" / f)
    return g2p


DRIVER = '''# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, "01_g2p")
import collision_audit as C
mode = sys.argv[1]
if mode == "hash":
    vocab, prov = C.load_attestation()
    print(json.dumps({"scope_policy_hash": C.scope_policy_hash(),
                      "domain_config_hash": C.domain_config_hash(vocab, prov)}))
else:  # "audit"
    sys.exit(C.main())
'''


def run_driver(g2p: Path, mode: str):
    driver = g2p / "_mutation_driver.py"
    driver.write_text(DRIVER, encoding="utf-8")
    env_python = [PY, "-B", "01_g2p/_mutation_driver.py", mode]
    return subprocess.run(env_python, cwd=g2p.parent, capture_output=True,
                          text=True, env={"PYTHONDONTWRITEBYTECODE": "1",
                                          "PATH": "/usr/bin:/bin"})


def run_audit(g2p: Path):
    return run_driver(g2p, "audit")


def hashes(g2p: Path):
    r = run_driver(g2p, "hash")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def main():
    src = (HERE / "collision_audit.py").read_text(encoding="utf-8")
    assert src.count(ANCHOR) == 1, "anchor mutation không duy nhất"

    with tempfile.TemporaryDirectory(prefix="scope_mutation_") as td:
        td = Path(td)

        # T1 baseline
        g2p = build_sandbox(td)
        r = run_audit(g2p)
        check("T1: audit nguyên bản exit 0", r.returncode == 0,
              f"exit={r.returncode} {r.stdout[-300:]} {r.stderr[-200:]}")
        check("T1: stdout báo 39 excluded + 37 protected, 0 lỗi",
              "39 excluded + 37 protected member, exact/UPPER/NFD, 0 lỗi"
              in r.stdout)
        base = hashes(g2p)

        # T2/T3 — các mutation
        mutations = [
            ("M1 subject đi qua (thue→None)", MUT_PASS_THROUGH, None),
            ("M2 protected bị chặn nhầm (thuê→excluded)", MUT_BLOCK_PROTECTED, None),
            ("M3 ledger bản sao đổi thành viên (swap beo/beu)", None,
             "ledger_swap"),
        ]
        for name, mut_src, ledger_mut in mutations:
            g2p = build_sandbox(td)
            target = g2p / "collision_audit.py"
            if mut_src is not None:
                target.write_text(src.replace(ANCHOR, mut_src), encoding="utf-8")
            if ledger_mut == "ledger_swap":
                lp = g2p.parent / "02_data" / "collision" / "qd57_scope_exclusions.json"
                led = json.loads(lp.read_text(encoding="utf-8"))
                for e in led["exclusions"]:
                    if set(e["pair"]) == {"beo", "beu"}:
                        e["excluded_members"], e["protected_members"] = \
                            e["protected_members"], e["excluded_members"]
                lp.write_text(json.dumps(led, ensure_ascii=False, indent=1) + "\n",
                              encoding="utf-8")
            r = run_audit(g2p)
            check(f"T2 {name}: audit KHÔNG PASS (exit≠0)", r.returncode == 1,
                  f"exit={r.returncode} {r.stdout[-200:]} {r.stderr[-200:]}")
            if ledger_mut:
                # ledger lệch đáp án pin bị load_scope_exclusions chặn trước
                # (SystemExit) — audit không bao giờ PASS trên ledger hỏng
                check(f"T2 {name}: bị chặn bởi validator ledger (lệch đáp án pin)",
                      "lệch đáp án pin" in r.stderr)
            else:
                check(f"T2 {name}: lý do FAIL là ranh giới scope",
                      "ranh giới scope sai" in r.stdout)
            h = hashes(g2p)
            check(f"T3 {name}: scope_policy_hash ĐỔI",
                  h["scope_policy_hash"] != base["scope_policy_hash"])
            check(f"T3 {name}: domain_config_hash ĐỔI",
                  h["domain_config_hash"] != base["domain_config_hash"])

        # T3 khôi phục → về giá trị baseline
        g2p = build_sandbox(td)
        h = hashes(g2p)
        check("T3 khôi phục: scope_policy_hash về giá trị baseline",
              h["scope_policy_hash"] == base["scope_policy_hash"])
        check("T3 khôi phục: domain_config_hash về giá trị baseline",
              h["domain_config_hash"] == base["domain_config_hash"])

    n_fail = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"scope_policy mutation probes: "
          f"{len(CHECKS) - n_fail} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
