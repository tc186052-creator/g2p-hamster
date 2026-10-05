"""test_cli.py — kiểm tra cli.py bằng subprocess (không import trong process).

Chạy:  python3 -m unittest tests.test_cli -v
Case: chạy mặc định · strict --policy cmu,spell · policy lạ báo lỗi rõ ·
--file/--out xuất JSON đọc được.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "cli.py"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))


class TestCli(unittest.TestCase):

    def test_chay_mac_dinh_tra_json_day_du(self):
        r = run_cli("Xin chào, hôm nay trời đẹp quá!")
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["state"], "complete")
        self.assertTrue(d["profile"])
        self.assertIn("schema", d)

    def test_strict_voi_policy_hop_le(self):
        # policy cmu,spell phải được nhận (đúng kiểu tên nguồn)
        r = run_cli("Xin chào, hôm nay trời đẹp quá!", "--mode", "strict",
                    "--policy", "cmu,spell")
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["state"], "complete")
        self.assertEqual(d["strict_policy"], ["cmu", "spell"])
        # câu mất từ → strict từ chối
        r2 = run_cli("Tôi dùng cue nhé.", "--mode", "strict",
                     "--policy", "cmu,spell")
        d2 = json.loads(r2.stdout)
        self.assertEqual(d2["state"], "rejected")

    def test_policy_la_bao_loi_ro_rang(self):
        r = run_cli("Xin chào", "--mode", "strict", "--policy", "blah_blah")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("nguồn lạ", r.stderr + r.stdout)

    def test_file_va_out_xuat_json_doc_duoc(self):
        with tempfile.TemporaryDirectory() as td:
            inp = Path(td) / "van_ban.txt"
            out = Path(td) / "ket_qua.json"
            inp.write_text("Xin chào.\nHôm nay trời đẹp quá!\n",
                           encoding="utf-8")
            r = run_cli("--file", str(inp), "--out", str(out))
            self.assertEqual(r.returncode, 0, r.stderr)
            d = json.loads(out.read_text(encoding="utf-8"))
            self.assertIsInstance(d, list)
            self.assertEqual(len(d), 2)
            for row in d:
                self.assertIn("profile", row)
                self.assertIn("text", row)


if __name__ == "__main__":
    unittest.main()
