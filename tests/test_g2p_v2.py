"""test_g2p_v2.py — regression v2: state coverage, strict/best_effort, scope,
espeak fail-closed (mock + thật), provenance, API cũ.

Chạy:  python3 -m unittest tests.test_g2p_v2 -v
(Nhánh mock espeak KHÔNG đụng espeak thật; test thật chỉ chạy khi máy có
espeak-ng và được tách riêng lớp TestEspeakThat.)
"""
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from g2p_hamster import g2p_v2 as gv2  # noqa: E402
from g2p_hamster.g2p_v1 import text_to_profile  # noqa: E402
from g2p_hamster.g2p_v2 import (espeak_arpabet, text_to_profile_v2,  # noqa: E402
                                text_to_profile_v2_full, v2_policy_hash,
                                v2_provenance)


def reset_caches():
    """Module cache của v2 phải Reset khi env/mock đổi trong test."""
    gv2._ESPEAK_META = None
    gv2._POLICY_HASH = None


class EnvCase(unittest.TestCase):
    """Case đụng env biến + cache — lưu/phục hồi sạch sẽ."""

    def setUp(self):
        self._env = {k: os.environ.get(k)
                     for k in (gv2._ESPEAK_BIN_ENV, gv2._ESPEAK_TIMEOUT_ENV)}
        reset_caches()

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        reset_caches()

    def fake_espeak(self, script: str) -> str:
        """Binary giả trong tmp — script shell in ra stdout rồi exit theo mã."""
        d = tempfile.mkdtemp(prefix="fake_espeak_")
        p = Path(d) / "espeak-ng"
        p.write_text("#!/bin/sh\n" + script + "\n")
        p.chmod(p.stat().st_mode | stat.S_IEXEC)
        os.environ[gv2._ESPEAK_BIN_ENV] = str(p)
        return str(p)


class TestAPITuongThich(unittest.TestCase):
    """API cũ (profile, errs, notes) phải nguyên vẹn cho caller hiện có."""

    def test_tuple_3_phan_tu_khop_full(self):
        s = "Xin chào thế giới, hôm nay trời đẹp."
        tup = text_to_profile_v2(s)
        full = text_to_profile_v2_full(s)
        self.assertIsInstance(tup, tuple)
        self.assertEqual(len(tup), 3)
        self.assertEqual(tup[0], full["profile"])
        self.assertEqual(tup[1], full["errs"])
        self.assertEqual(tup[2], full["notes"])

    def test_schema_va_truong_bat_buoc(self):
        r = text_to_profile_v2_full("xin chào")
        for k in ("schema", "mode", "state", "profile", "errs", "notes",
                  "warnings", "dropped", "units", "sources",
                  "strict_policy", "provenance"):
            self.assertIn(k, r)
        self.assertEqual(r["schema"], "g2p_v2_result/0.3")
        self.assertIn("cmu", r["strict_policy"])   # "core" luôn ngầm được phép

    def test_units_trace_co_read_complete(self):
        # trace từng unit — đã đọc phải có read_complete=True, bị bỏ = False
        r = text_to_profile_v2_full("Xin chào thế giới.")
        self.assertTrue(r["units"])
        for u in r["units"]:
            self.assertIn("read_complete", u)
            self.assertEqual(u["read_complete"], u["outcome"] in
                             ("read", "upgraded"))
        # đơn vị thống nhất: tổng sources == số UNIT đã đọc (mỗi entry là 1
        # read unit thật; entry gộp tường minh khai báo unit_count)
        n_read = sum(u.get("unit_count", 1) for u in r["units"]
                     if u["outcome"] in ("read", "upgraded"))
        self.assertEqual(sum(r["sources"].values()), n_read)

    def test_units_fast_path_mo_rong_tung_read_unit(self):
        # fast path record đọc tốt phải MỞ RA thành từng read unit — câu vi
        # sạch không được có dòng gộp (merged) mạo danh trace per-unit
        r = text_to_profile_v2_full("Xin chào thế giới, hôm nay trời đẹp.")
        self.assertTrue(r["units"])
        for u in r["units"]:
            self.assertNotIn("merged", u)
        self.assertEqual(sum(r["sources"].values()), len(r["units"]))

    def test_mode_la_loai_doc_lap(self):
        # best_effort mặc định KHÔNG đụng strict mặc định
        r = text_to_profile_v2_full("xin chào")
        self.assertEqual(r["mode"], "best_effort")
        with self.assertRaises(ValueError):
            text_to_profile_v2_full("xin chào", mode="khac")
        with self.assertRaises(ValueError):
            text_to_profile_v2_full("xin chào", strict_policy={"từđộitrờitrời"})


class TestStateCoverage(unittest.TestCase):
    """state đo COVERAGE: complete/partial/empty — không phải correctness."""

    def test_cau_vi_sach_se_complete(self):
        r = text_to_profile_v2_full("Xin chào thế giới, hôm nay trời đẹp.")
        self.assertEqual(r["state"], "complete")
        self.assertEqual(r["dropped"], [])
        self.assertEqual(set(r["sources"]), {"core"})

    def test_bo_mot_tu_canh_bao_partial(self):
        r = text_to_profile_v2_full("Café đã hết.")
        self.assertEqual(r["state"], "partial")
        lost = [d for d in r["dropped"] if not d["intentional"]]
        self.assertEqual([d["word"] for d in lost], ["Café"])
        self.assertIn("Café", r["notes"][0])   # không âm thầm

    def test_mat_het_noi_dung_chi_con_dau_cau_la_empty(self):
        # profile chỉ còn dấu câu trong khi có nội dung cần đọc → KHÔNG
        # được tính cứu thành công (empty)
        r = text_to_profile_v2_full("Café, café!")
        self.assertEqual(r["state"], "empty")
        self.assertEqual(r["profile"], ",!")
        lost = [d for d in r["dropped"] if not d["intentional"]]
        self.assertEqual(len(lost), 2)

    def test_profile_rong_dung_empty(self):
        r = text_to_profile_v2_full("Café")
        self.assertEqual(r["state"], "empty")
        self.assertEqual(r["profile"], "")

    def test_bieu_tuong_la_drop_chu_y_khong_ha_state(self):
        # emoji/icon không có gì để đọc, v1 cũng bỏ → intentional, complete
        r = text_to_profile_v2_full("Tôi thích 🎉 lắm.")
        self.assertEqual(r["state"], "complete")
        self.assertEqual(len(r["dropped"]), 1)
        self.assertTrue(r["dropped"][0]["intentional"])

    def test_token_validation_chan_la_mat_noi_dung(self):
        # token bị chặn bởi validation phải rơi vào dropped (phi-chủ-ý),
        # không biến mất không báo
        r = text_to_profile_v2_full("xin chào")
        for d in r["dropped"]:
            self.assertFalse(d["reason"].startswith("validation"))

    def test_nbsp_va_soft_hyphen_trong_tu(self):
        # wiki hazard: NBSP dính từ, soft hyphen NẰM TRONG từ phải xóa
        r1 = text_to_profile_v2_full("của\u00a0New York đấy.")
        self.assertEqual(r1["state"], "complete")
        self.assertNotIn("espeak", r1["sources"])   # 'của' KHÔNG bị kéo qua espeak
        self.assertIn("kuə", r1["profile"])         # 'của' đọc vi
        p_nuoc = text_to_profile_v2_full("nước")["profile"]
        r2 = text_to_profile_v2_full("n\u00ad\u00adước")
        self.assertEqual(r2["state"], "complete")
        self.assertEqual(r2["profile"], p_nuoc)     # xé từ là hồi quy

    def test_so_tien_ngay_t1_verbalize_xong_complete(self):
        r = text_to_profile_v2_full("Tổng cộng 1.335 đồng, ngày 29/4/2021 nhé.")
        self.assertEqual(r["state"], "complete")
        self.assertFalse(any("chữ số" in d["reason"] for d in r["dropped"]))

    def test_viet_anh_mixed(self):
        r = text_to_profile_v2_full("Tôi tải file report_v2_final.pdf về máy.")
        self.assertEqual(r["state"], "complete")


class TestRegressionV1OK(unittest.TestCase):
    """Bất biến coverage: v1 đọc đủ (errs rỗng) ⇒ v2 complete + profile GIỐNG
    HỆT v1. v1 đủ mà v2 mất từ = hồi quy coverage — đỏ."""

    CORPUS = [
        "tính từ ngày 29/4/2021 cho đến nay là hơn 1,59 triệu ca.",
        "Bạn Long đang học team building ở công ty, còn Chi thì xem phim.",
        "Xin chào thế giới, hôm nay trời đẹp!",
        "Doanh thu Q3 tăng 12,5 phần trăm so với cùng kỳ.",
        "gặp lúc 8pm nhé, phòng họp B.",
        "The show starts at 7:30 p.m. tonight.",
        "nam MC dõi theo chương trình.",
    ]

    def test_v1_ok_implies_v2_complete_giong_he_t(self):
        for s in self.CORPUS:
            with self.subTest(cau=s):
                p1, e1 = text_to_profile(s)
                r2 = text_to_profile_v2_full(s)
                self.assertEqual(e1, [], "corpus phải là câu v1 đọc đủ")
                self.assertEqual(r2["state"], "complete")
                self.assertEqual(r2["profile"], p1,
                                 "v2 phải giữ nguyên profile v1 khi v1 đủ")
                self.assertEqual([d for d in r2["dropped"]
                                  if not d["intentional"]], [])

    def test_v1_khong_ok_thi_khong_ap_dung_bat_bien(self):
        # câu v1 từ chối (Café) — bất biến không cover, v2 phải partial
        p1, e1 = text_to_profile("Café đã hết.")
        self.assertTrue(e1)
        self.assertEqual(text_to_profile_v2_full("Café đã hết.")["state"],
                         "partial")

    def test_v1_tu_choi_v2_cu_du_la_cuu_that_su(self):
        # "report_v2_final.pdf": v1 từ chối cả câu (unresolved), v2 cứu đủ
        # coverage qua spell tên chữ → đúng nghĩa V2_CUU
        p1, e1 = text_to_profile("tải file report_v2_final.pdf về máy.")
        self.assertTrue(e1)
        r2 = text_to_profile_v2_full("tải file report_v2_final.pdf về máy.")
        self.assertEqual(r2["state"], "complete")
        self.assertEqual([d for d in r2["dropped"] if not d["intentional"]], [])


class TestStrictBestEffort(EnvCase):
    """strict cho prep train: từ chối mất nội dung + nguồn ngoài policy.
    best_effort cho render: luôn đọc tiếp, chỉ báo. Test espeak dùng MOCK —
    không phụ thuộc espeak thật trên máy (offline-safe)."""

    def _mock_espeak(self):
        """Giả espeak_arpabet trả phiên âm cố định cho từ OOV."""
        return mock.patch.object(
            gv2, "espeak_arpabet",
            return_value=["K", "W", "IH0", "Z", "EY1", "SH", "AH0", "S"])

    def test_strict_cau_sach_se_complete(self):
        r = text_to_profile_v2_full("Xin chào thế giới.", mode="strict")
        self.assertEqual(r["state"], "complete")
        self.assertTrue(r["profile"])

    def test_strict_tu_choi_khi_mat_noi_dung(self):
        r = text_to_profile_v2_full("Café đã hết.", mode="strict")
        self.assertEqual(r["state"], "rejected")
        self.assertEqual(r["profile"], "")
        self.assertTrue(any(e.startswith("strict:") for e in r["errs"]))
        self.assertIn("mất", r["errs"][0])

    def test_strict_mac_dinh_choi_espeak(self):
        # OOV anh: best_effort nâng cấp espeak; strict mặc định từ chối vì
        # espeak là suy diễn quy tắc chưa duyệt; opt-in tường minh thì qua
        s = "The quizzacious thing."
        with self._mock_espeak():
            rb = text_to_profile_v2_full(s)
            self.assertEqual(rb["state"], "complete")
            self.assertIn("espeak", rb["sources"])
            self.assertIn("kwɪz", rb["profile"])   # phát âm thật, không đánh vần
            rs = text_to_profile_v2_full(s, mode="strict")
            self.assertEqual(rs["state"], "rejected")
            self.assertIn("espeak", rs["errs"][0])
            rs2 = text_to_profile_v2_full(s, mode="strict",
                                          strict_policy={"cmu", "spell", "espeak"})
            self.assertEqual(rs2["state"], "complete")

    def test_strict_tu_choi_empty(self):
        r = text_to_profile_v2_full("Café", mode="strict")
        self.assertEqual(r["state"], "rejected")
        self.assertIn("rỗng", r["errs"][0])

    def test_strict_cho_phep_icon_khong_tu_choi(self):
        # icon/biểu tượng là drop CHỦ Ý (không có gì để đọc) — strict không từ chối
        r2 = text_to_profile_v2_full("Tôi thích 🎉 lắm.", mode="strict")
        self.assertEqual(r2["state"], "complete")


class TestStrictContractHopDong(EnvCase):
    """Fault injection: IR lệch hợp đồng (contract_ok=False) — strict PHẢI
    từ chối; chỉ loại lỗi tường minh trong STRICT_CONTRACT_ALLOWLIST mới
    được miễn, không miễn toàn bộ contract_errors."""

    def _inject_contract_errors(self, msgs):
        """Bơm contract_errors cấp stream vào output của g2p_stream thật."""
        real = gv2.G.g2p_stream

        def fake(ir):
            out = real(ir)
            out["contract_errors"] = (list(out.get("contract_errors", []))
                                      + list(msgs))
            return out
        return mock.patch.object(gv2.G, "g2p_stream", fake)

    def test_strict_tu_choi_khi_contract_ok_false(self):
        with self._inject_contract_errors(
                ["tokens[3].i không liên tiếp: 5 → 7"]):
            r = text_to_profile_v2_full("Xin chào thế giới.", mode="strict")
        self.assertFalse(r["contract_ok"])
        self.assertEqual(r["state"], "rejected")
        self.assertEqual(r["profile"], "")
        self.assertIn("hợp đồng", r["errs"][-1])

    def test_best_effort_van_complete_va_bao_warning(self):
        # hành vi render KHÔNG đổi: câu vẫn đọc, chỉ thêm warning
        with self._inject_contract_errors(
                ["tokens[3].i không liên tiếp: 5 → 7"]):
            r = text_to_profile_v2_full("Xin chào thế giới.")
        self.assertFalse(r["contract_ok"])
        self.assertTrue(r["warnings"])
        self.assertEqual(r["state"], "complete")

    def test_allowlist_theo_loai_loi_mien_dung_loai_do(self):
        kinds = {"i_lech_day": re.compile(r"không liên tiếp")}
        with mock.patch.object(gv2, "_CONTRACT_KIND_RES", kinds), \
             mock.patch.object(gv2, "STRICT_CONTRACT_ALLOWLIST",
                               frozenset({"i_lech_day"})), \
             self._inject_contract_errors(
                 ["tokens[3].i không liên tiếp: 5 → 7"]):
            r = text_to_profile_v2_full("Xin chào thế giới.", mode="strict")
        self.assertEqual(r["state"], "complete")

    def test_loi_la_khong_duoc_mien_du_allowlist_co_noi_dung(self):
        # lỗi không nhận diện được loại → luôn từ chối, kể cả khi allowlist
        # đang có loại khác — không có lỗ hổng "lỗi lạ được miễn"
        kinds = {"i_lech_day": re.compile(r"không liên tiếp")}
        with mock.patch.object(gv2, "_CONTRACT_KIND_RES", kinds), \
             mock.patch.object(gv2, "STRICT_CONTRACT_ALLOWLIST",
                               frozenset({"i_lech_day"})), \
             self._inject_contract_errors(["lỗi hoàn toàn lạ không nhận diện"]):
            r = text_to_profile_v2_full("Xin chào thế giới.", mode="strict")
        self.assertEqual(r["state"], "rejected")
        self.assertEqual(r["profile"], "")

    def test_policy_hash_doi_khi_allowlist_doi(self):
        h1 = v2_policy_hash()
        with mock.patch.object(gv2, "STRICT_CONTRACT_ALLOWLIST",
                               frozenset({"i_lech_day"})):
            gv2._POLICY_HASH = None
            h2 = v2_policy_hash()
        self.assertNotEqual(h1, h2)


class TestScopeKhongLach(unittest.TestCase):
    """Scope QD57: từ cấm phát âm KHÔNG được cứu qua route kia hay espeak —
    NHƯNG bỏ một từ nội dung vẫn là MẤT COVERAGE: best_effort → partial,
    strict → rejected (intentional=True không miễn mọi loại mất nội dung)."""

    def test_cue_scope_bi_bo_co_bao_khong_cuu(self):
        r = text_to_profile_v2_full("Tôi dùng cue nhé.")
        self.assertEqual(r["state"], "partial")   # mất 1 từ nội dung
        drops = [d for d in r["dropped"] if d["word"] == "cue"]
        self.assertEqual(len(drops), 1)
        self.assertIn("scope", drops[0]["reason"])
        self.assertFalse(drops[0]["intentional"])  # vẫn là mất nội dung
        self.assertEqual(set(r["sources"]), {"core"})   # không nguồn cứu ngoài

    def test_cue_scope_strict_tu_choi(self):
        r = text_to_profile_v2_full("Tôi dùng cue nhé.", mode="strict")
        self.assertEqual(r["state"], "rejected")
        self.assertIn("cue", r["errs"][0])
        self.assertEqual(r["profile"], "")

    def test_scope_best_effort_cung_khong_phat_am(self):
        r = text_to_profile_v2_full("Tôi dùng cue nhé.")
        self.assertNotIn("kjuː", r["profile"])   # không đọc "cue" kiểu anh


class TestProvenance(EnvCase):
    """Fingerprint v2 phủ policy/code/mapping + cấu hình espeak."""

    def test_hash_on_dinh_goi_nhieu_lan(self):
        self.assertEqual(v2_policy_hash(), v2_policy_hash())
        self.assertEqual(v2_provenance(), v2_provenance())

    def test_hash_doi_khi_mapping_doi(self):
        h1 = v2_policy_hash()
        old = gv2._ESPEAK_VOWELS["ɑ"]
        try:
            gv2._ESPEAK_VOWELS["ɑ"] = "XX_MUTED"
            gv2._POLICY_HASH = None
            h2 = v2_policy_hash()
        finally:
            gv2._ESPEAK_VOWELS["ɑ"] = old
            gv2._POLICY_HASH = None
        self.assertNotEqual(h1, h2)

    def test_hash_doi_khi_strict_policy_mac_dinh_doi(self):
        h1 = v2_policy_hash()
        old = gv2.DEFAULT_STRICT_POLICY
        try:
            gv2.DEFAULT_STRICT_POLICY = frozenset({"cmu"})
            gv2._POLICY_HASH = None
            h2 = v2_policy_hash()
        finally:
            gv2.DEFAULT_STRICT_POLICY = old
            gv2._POLICY_HASH = None
        self.assertNotEqual(h1, h2)

    def test_provenance_ke_cau_hinh_espeak_hieu_luc(self):
        p = v2_provenance()
        self.assertIn("policy_hash", p)
        es = p["espeak"]
        self.assertIn("enabled", es)
        if es["enabled"]:
            self.assertIn("version", es)          # không chỉ đường dẫn binary
            self.assertTrue(es["version"])
            self.assertEqual(es["voice"], "en-us")
            self.assertIn("--ipa", es["options"])

    def test_espeak_that_co_version_trong_provenance(self):
        # máy này có espeak-ng thật — provenance phải bắt được version
        if not gv2._espeak_bin():
            self.skipTest("máy không có espeak-ng")
        p = v2_provenance()
        self.assertIn("eSpeak NG", p["espeak"]["version"])

    def test_espeak_meta_khong_stale_khi_env_doi(self):
        # đổi env GIỮA phiên làm việc (không reset cache tay) phải probe lại
        if not gv2._espeak_bin():
            self.skipTest("máy không có espeak-ng")
        p1 = v2_provenance()
        self.assertTrue(p1["espeak"]["enabled"])
        os.environ[gv2._ESPEAK_BIN_ENV] = ""          # tắt nguồn — không reset tay
        p2 = v2_provenance()
        self.assertFalse(p2["espeak"]["enabled"])
        os.environ.pop(gv2._ESPEAK_BIN_ENV, None)     # bật lại — probe lại
        p3 = v2_provenance()
        self.assertTrue(p3["espeak"]["enabled"])

    def test_strict_policy_thuc_te_trong_ket_qua(self):
        r1 = text_to_profile_v2_full("xin chào")
        self.assertEqual(r1["strict_policy"], sorted(gv2.DEFAULT_STRICT_POLICY))
        r2 = text_to_profile_v2_full("xin chào", mode="strict",
                                     strict_policy={"cmu", "espeak"})
        self.assertEqual(r2["strict_policy"], ["cmu", "espeak"])


class TestEspeakFailClosed(EnvCase):
    """Nguồn espeak fail-closed: thiếu binary, timeout, returncode≠0, IPA lạ,
    input ngoài phạm vi — không âm thầm xóa ký tự rồi phát âm từ khác."""

    def test_input_ngoai_pham_vi_bi_tu_choi_khong_go_espeak(self):
        # "café" có é — phải TỪ CHỐI, không biến thành "caf" rồi phát âm
        with mock.patch.object(gv2.subprocess, "run",
                               side_effect=AssertionError("không được gọi")):
            self.assertIsNone(espeak_arpabet("café"))
            self.assertIsNone(espeak_arpabet("naïve"))
            self.assertIsNone(espeak_arpabet("wei rd"))   # khoảng trắng

    def test_thieu_binary_tra_none(self):
        os.environ[gv2._ESPEAK_BIN_ENV] = "/khong/ton/tai/espeak-ng"
        self.assertIsNone(espeak_arpabet("cats"))

    def test_returncode_loi_tra_none_ke_ca_co_stdout(self):
        self.fake_espeak('echo "k ˈæ t s"; exit 3')
        self.assertIsNone(espeak_arpabet("cats"))

    def test_timeout_tra_none(self):
        os.environ[gv2._ESPEAK_TIMEOUT_ENV] = "0.3"
        self.fake_espeak('sleep 2; echo "k ˈæ t s"')
        self.assertIsNone(espeak_arpabet("cats"))

    def test_ipa_la_fail_closed_khong_am_tham_xoa(self):
        # ʘ (bilabial click) không có trong mapping → None, không bỏ ký tự
        self.fake_espeak('echo "k ʘ ˈæ t s"')
        self.assertIsNone(espeak_arpabet("cats"))

    def test_stdout_rong_tra_none(self):
        self.fake_espeak('exit 0')
        self.assertIsNone(espeak_arpabet("cats"))

    def test_env_rong_tat_nguon_espeak(self):
        os.environ[gv2._ESPEAK_BIN_ENV] = ""
        self.assertIsNone(gv2._espeak_bin())
        self.assertIsNone(espeak_arpabet("cats"))
        self.assertFalse(v2_provenance()["espeak"]["enabled"])

    def test_oov_voi_espeak_tat_thi_roi_ve_spell_hoac_drop(self):
        os.environ[gv2._ESPEAK_BIN_ENV] = ""
        r = text_to_profile_v2_full("The quizzacious thing.")
        self.assertEqual(r["state"], "complete")   # spell tên chữ là nguồn core
        self.assertNotIn("espeak", r["sources"])


class TestEspeakThat(unittest.TestCase):
    """Integration với espeak-ng THẬT — tách khỏi mock, skip nếu thiếu."""

    def setUp(self):
        if not gv2._espeak_bin():
            self.skipTest("máy không có espeak-ng")

    def test_tu_thong_thuong(self):
        phones = espeak_arpabet("cats")
        self.assertIsNotNone(phones)
        self.assertIn("AE1", phones)

    def test_xuyen_qua_rescue_co_nguon(self):
        syls, src = gv2.rescue_syllables("quizzacious")
        self.assertIn(src, ("cmu", "espeak"))
        self.assertTrue(syls)


if __name__ == "__main__":
    unittest.main()
