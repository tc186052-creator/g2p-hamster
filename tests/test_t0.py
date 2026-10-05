"""Regression test T0 — 4 ví dụ chuẩn trong 00_docs/02_vi_du_minh_hoa.md + torture set.

Chạy: cd 01_tiny_model && python3 -m unittest discover -s 04_eval/tests -v
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from g2p_hamster.t0 import Config, normalize  # noqa: E402
from g2p_hamster.t0.numbers import en_year, vi_cardinal  # noqa: E402


def ir(text, **cfg):
    return normalize(text, Config(**cfg))


def routes_of(result):
    return [(t["surface"], t["route"]) for t in result["tokens"]]


class TestDocExamples(unittest.TestCase):
    """4 ví dụ chuẩn — lệch một ô là đỏ."""

    def test_vd1_so_ngay_vi(self):
        r = ir("tính từ ngày 29/4/2021 cho đến nay là hơn 1,59 triệu ca, trong đó có 1.335 ca tử vong.")
        self.assertEqual(r["read_string"],
                         "tính từ ngày hai mươi chín tháng tư năm hai nghìn không trăm hai mươi mốt cho đến nay "
                         "là hơn một phẩy năm chín triệu ca, trong đó có một nghìn ba trăm ba mươi lăm ca tử vong.")
        self.assertEqual(r["sent_lang"], "vi")
        self.assertEqual(r["review"], [])
        cats = {t["surface"]: t["cat"] for t in r["tokens"]}
        self.assertEqual(cats["29/4/2021"], "date")
        self.assertEqual(cats["1,59"], "number")
        self.assertEqual(cats["1.335"], "number")

    def test_vd2_kho_bat_vi_context(self):
        r = ir("Bạn Long đang học team building ở công ty, còn Chi thì xem phim.")
        rt = dict(routes_of(r))
        self.assertEqual(rt["Long"], "vi")
        # [VA 03/10/2026] team: vi -> en (CHÍNH SÁCH MỚI CỦA CHỦ DỰ ÁN: "Anh thì ra
        # anh" — 5 luật đọc 03/10, xem VERIFY_R3.md). Cũ: kho_bat -> vi. team ∈
        # cmudict + ngữ cảnh VI vẫn đọc Anh theo luật 1; audio data đọc "tiim" khớp.
        self.assertEqual(rt["team"], "en")
        # [VA 02/10/2026] building: vi -> en (CHỐT CHỦ ĐÍCH, có bằng chứng).
        # Cũ: kho_bat -> tiny1 -> vi. Vấn đề: "building" đa âm tiết EN, vi_rules
        # không parse được -> route vi làm G2P unresolved (mù phát âm).
        # Audio TTS (bộ syn_mix) đọc lớp từ này kiểu Anh (~80/20, không phiên âm
        # hóa — chủ dự án nghe xác nhận 02/10/2026 + lệnh "cứ đi, có backup").
        # Nhánh cmudict (detect.assign_routes) route từ EN đa âm tiết — không
        # phải 1 âm tiết VI hợp lệ — về en. Âm tiết VI hợp lệ ("Long", "team")
        # GIỮ nguyên vi. Hồ sơ: 02_hamster_G2P/06_train_t3/data/mix3/
        # HO_SO_LOI_ROUTE_MIX.md; backup: 02_rules/backups/t0_bak_20261002_*.
        self.assertEqual(rt["building"], "en")
        self.assertEqual(rt["Chi"], "vi")
        rev = {x["surface"] for x in r["review"]}
        self.assertIn("Long", rev)   # kho bắt -> cờ review, model sau này quyết
        # [VA 03/10/2026] team KHÔNG còn cờ: theo 5 luật đọc của chủ dự án
        # ("Anh thì ra anh"), team được quyết CỨNG bởi kho_quyet_en (nguồn rõ,
        # conf 1.0 — đúng nguyên tắc "bảng quyết không cần cờ" của thiết kế).
        self.assertNotIn("team", rev)

    def test_vd3_long_en_context(self):
        r = ir("Đừng lo, as long as you cố gắng thì mọi thứ sẽ ổn.")
        rt = dict(routes_of(r))
        self.assertEqual(rt["long"], "en")
        self.assertEqual(rt["as"], "en")
        self.assertEqual(rt["you"], "en")

    def test_vd4_check_flow_t0_default(self):
        r = ir("mùa giải 2021-2022 có 34 vòng đấu.")
        self.assertIn("hai nghìn không trăm hai mươi mốt đến hai nghìn không trăm hai mươi hai", r["read_string"])
        self.assertIn("ba mươi bốn", r["read_string"])


class TestNumbers(unittest.TestCase):
    def test_vi_cardinal(self):
        cases = {0: "không", 5: "năm", 10: "mười", 11: "mười một", 15: "mười lăm",
                 21: "hai mươi mốt", 25: "hai mươi lăm", 100: "một trăm",
                 101: "một trăm lẻ một", 105: "một trăm lẻ năm", 110: "một trăm mười",
                 335: "ba trăm ba mươi lăm", 1000: "một nghìn",
                 1335: "một nghìn ba trăm ba mươi lăm", 2021: "hai nghìn không trăm hai mươi mốt",
                 159: "một trăm năm mươi chín", 1000000: "một triệu"}
        for n, expected in cases.items():
            self.assertEqual(vi_cardinal(n), expected, f"n={n}")

    def test_en_year(self):
        self.assertEqual(en_year(1990), "nineteen ninety")
        self.assertEqual(en_year(2005), "two thousand five")
        self.assertEqual(en_year(2021), "twenty twenty one")
        self.assertEqual(en_year(2000), "two thousand")


class TestTorture(unittest.TestCase):
    def test_phone_groups(self):
        r = ir("Gọi 0901 234 567 qua Zalo nhé")
        self.assertIn("không chín không một, hai ba bốn, năm sáu bảy", r["read_string"])
        self.assertEqual(r["tokens"][1]["cat"], "phone")

    def test_email(self):
        r = ir("liên hệ abc@gmail.com nhé")
        self.assertEqual(r["tokens"][2]["cat"], "email")
        self.assertEqual(r["tokens"][2]["read"], "spell")
        self.assertIn("abc a còng gmail chấm com", r["read_string"])

    def test_url(self):
        r = ir("vào https://vnexpress.net/thoi-su xem")
        self.assertIn("vnexpress chấm net gạch chéo", r["read_string"])

    def test_percent(self):
        r = ir("tỷ lệ 9,1%")
        self.assertIn("chín phẩy một phần trăm", r["read_string"])

    def test_money_prefix_and_unit_glued(self):
        r = ir("giá $5 và 25tr")
        self.assertIn("năm đô la", r["read_string"])
        self.assertIn("hai mươi lăm triệu", r["read_string"])

    def test_time_vi_en(self):
        self.assertIn("chín giờ ba mươi phút", ir("lúc 9h30p")["read_string"])
        self.assertIn("nine thirty", ir("The meeting is at 9:30")["read_string"])

    def test_year_style(self):
        self.assertIn("một nghìn chín trăm chín mươi", ir("năm 1990")["read_string"])
        self.assertIn("nineteen ninety", ir("the year 1990")["read_string"])

    def test_slang_and_abbrev(self):
        r = ir("ko biết đc đâu, GS. Nguyễn Văn A ở TP. HCM")
        self.assertIn("không biết được đâu, giáo sư", r["read_string"])
        self.assertIn("thành phố", r["read_string"])
        self.assertIn("Hồ Chí Minh", r["read_string"])

    def test_icon_remove_and_read(self):
        base = "hôm nay buồn quá T_T"
        self.assertEqual(ir(base)["read_string"], "hôm nay buồn quá")
        r2 = ir(base, icon_policy="read")
        self.assertEqual(r2["read_string"], "hôm nay buồn quá khóc")

    def test_score_vs_interval(self):
        self.assertIn("hai, một", ir("Man United vừa đánh bại Arsenal 2-1")["read_string"])
        self.assertIn("mười đến mười lăm", ir("từ 10-15 người")["read_string"])

    def test_glue_and_camel(self):
        r = ir("OutlookĐể sử dụng")
        self.assertIn("Outlook Để", r["read_string"])
        r2 = ir("dùng iPhone 15 Pro Max")
        self.assertIn("iPhone", r2["read_string"])
        # [VA 03/10/2026] "mười lăm" -> "fifteen": hệ quả chính sách mới "Anh thì ra
        # anh" (Pro/Max -> en kéo ngữ cảnh số sang en). Đã báo chủ dự án; nếu muốn
        # số LUÔN đọc Việt sẽ thêm luật riêng, không thuộc 5 luật này.
        self.assertIn("fifteen", r2["read_string"])

    def test_caps_not_acronym_trap(self):
        """'đó'/'Để' là từ thường vi — KHÔNG được đọc đánh vần."""
        for w in ("trong đó có", "Outlook Để"):
            pass
        r = ir("trong đó có một người")
        self.assertNotIn("Đ Ó", r["read_string"])
        self.assertIn("trong đó có", r["read_string"])
        r2 = ir("Để làm việc này")
        self.assertIn("Để làm", r2["read_string"])

    def test_acronym_spell(self):
        r = ir("tổ chức UNESCO mới nhất")
        self.assertIn("U N E S C O", r["read_string"])

    def test_vi_acronyms_expand(self):
        self.assertIn("huấn luyện viên", ir("HLV Tite nói.")["read_string"])
        self.assertIn("cổ động viên", ir("CĐV MU reo hò.")["read_string"])
        self.assertIn("hội đồng quản trị", ir("HĐQT họp.")["read_string"])
        self.assertIn("Thế chiến hai", ir("Thế chiến II kết thúc.")["read_string"])
        # [VA 03/10/2026] USD → spell_en ("iu ét đi") theo duyệt chủ dự án 03/10
        # (chọn spell_en, bỏ expand "đô la Mỹ") — áp cho cả sau số
        self.assertIn("một trăm iu ét đi", ir("tôi nộp 100 USD")["read_string"])
        self.assertIn("hai mươi lăm triệu", ir("giá 25tr")["read_string"])

    def test_vi_acronyms_round2(self):
        self.assertIn("thứ mười ba", ir("Đại hội lần thứ XIII của Đảng.")["read_string"])
        self.assertIn("nghệ danh Lona", ir("nghệ danh LONA nổi tiếng.")["read_string"])
        self.assertIn("Covid", ir("he said về COVID.")["read_string"])
        self.assertIn("Tờ Khai Không Có Chữ Ký", ir("TỜ KHAI KHÔNG CÓ CHỮ KÝ,")["read_string"])
        self.assertIn("an toàn thông tin", ir("lĩnh vực ATTT (KISIA).")["read_string"])
        self.assertIn("U N E S C O", ir("tổ chức UNESCO mới nhất.")["read_string"])

    def test_censored_words(self):
        self.assertIn("bị đanh đập", ir("bị đ.a'nh đập.")["read_string"])  # dấu thanh không khôi phục được
        self.assertIn("giết người chặt chém", ir("gi.ết người ch/ặt ch/ém.")["read_string"])

    def test_alnum_3d_4k(self):
        self.assertIn("ba D", ir("đồ họa 3D sắc nét.")["read_string"])
        self.assertIn("bốn K", ir("màn hình 4K.")["read_string"])
        self.assertIn("bốn nghìn", ir("giá 4k.")["read_string"])

    def test_slash_reading(self):
        self.assertIn("đồng trên cổ phần", ir("48.400 đồng/cổ phần.")["read_string"])
        self.assertIn("ki lô mét một giờ", ir("xe chạy 60 km/h.")["read_string"])

    def test_time_pm_am(self):
        self.assertIn("mười ba giờ ba mươi tám chiều", ir("Đức13:38 PM tối nay.")["read_string"])

    def test_date_dot_and_range(self):
        self.assertIn("ngày ba tháng bảy", ir("hôm nay (ngày 3.7).")["read_string"])
        self.assertIn("ba đến chín tháng mười hai", ir("từ 3-9/12.")["read_string"])
        self.assertIn("tháng ba năm hai nghìn không trăm hai mươi hai", ir("quý 3/2022 tăng.")["read_string"])
        self.assertIn("ngày ba mươi mốt tháng mười", ir("hết 31-10.")["read_string"])

    def test_us_not_url(self):
        self.assertIn("U.S.", ir("chỉ số U.S. Economic Index.")["read_string"])

    def test_no_orphan_tokens(self):
        r = ir("mọi 0901 234 567 token @gmail phải có đường đọc!")
        for t in r["tokens"]:
            self.assertIsNotNone(t["route"], f"token mồ côi: {t}")

    def test_deterministic(self):
        s = "1,59 triệu ca 0901 234 567 abc@gmail.com long Man United 2-1"
        self.assertEqual(ir(s)["read_string"], ir(s)["read_string"])

    def test_invisible_chars_dropped(self):
        r = ir("hôm\u200bnay sạch\u200f sẽ")
        self.assertEqual(r["read_string"], "hôm nay sạch sẽ")

    def test_torture_file(self):
        path = ROOT / "tests" / "torture.txt"
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            result = normalize(line)  # chỉ yêu cầu: không crash, token nào cũng có route
            for t in result["tokens"]:
                self.assertIn(t["route"], ("vi", "en"), f"{line!r} -> {t}")


class TestGapGroups(unittest.TestCase):
    """Nhóm gaps sửa đợt 01/10 — mỗi nhóm một test, khóa không cho tụt lại."""

    def test_unit_after_slash(self):
        # "s" sau gạch là đơn vị -> "giây", gạch đọc theo ngôn ngữ unit (không "per s")
        self.assertIn("events trên giây", ir("tốc độ xử lý 1000 events/s.")["read_string"])
        self.assertIn("mb trên giây", ir("chạy 100 mb/s.")["read_string"])
        self.assertIn("mét trên giây", ir("đo 9.8 m/s.")["read_string"])

    def test_fraction_signal_words(self):
        # từ tín hiệu liều lượng chặn đọc NGÀY ("uống 1/4" không phải ngày 1 tháng 4)
        self.assertIn("uống một phần tư viên thuốc", ir("uống 1/4 viên thuốc mỗi sáng.")["read_string"])
        self.assertIn("chia một phần hai số hàng", ir("chia 1/2 số hàng cho đại lý.")["read_string"])
        self.assertIn("giảm một phần hai", ir("giảm 1/2 giá còn 200k.")["read_string"])

    def test_mention_handle(self):
        self.assertIn("a còng handle", ir("inbox theo @handle nhé.")["read_string"])
        self.assertIn("a còng quoc minh", ir("nhắc anh @quoc_minh nhé.")["read_string"])

    def test_version_rc_suffix(self):
        # "-rc1" phải đọc trọn, không bỏ lửng
        self.assertIn("ba chấm hai chấm không, r c một", ir("bản v3.2.0-rc1 hôm nay.")["read_string"])
        self.assertIn("hai chấm bốn chấm không, r c hai", ir("phát hành 2.4.0-rc2.")["read_string"])

    def test_filename_ext(self):
        # tên file: đọc từng khúc + "chấm P D F", không giữ nguyên raw
        self.assertIn("report v hai final chấm P D F", ir("tải file report_v2_final.pdf về máy.")["read_string"])
        self.assertIn("final report chấm D O C X", ir("gửi kèm final_report.docx.")["read_string"])

    def test_familiar_acronym_mc(self):
        # viết tắt quen miệng có trong abbrev dict -> đọc theo entry, không gõ M C
        self.assertIn("êm xê", ir("nam MC dõi theo.")["read_string"])


    def test_money_grouped_7_digits(self):
        # tiền ≥ 7 chữ số: đọc thang nghìn/triệu/tỷ, KHÔNG "chấm" KHÔNG đọc-ID
        for text, want in [
            ("Giá 1.000.000đ", "một triệu đồng"),
            ("Tôi có 5.000.000 đồng", "năm triệu đồng"),
            ("Thu về 1.250.000đ mỗi tháng", "một triệu hai trăm năm mươi nghìn đồng"),
            ("Mã 1000000đ", "một triệu đồng"),
            ("Tổng 1 000 000 đồng", "một triệu đồng"),
            ("Ngân sách 1.000.000.000 đồng", "một tỷ đồng"),
            ("Lương 12.500.000 đồng", "mười hai triệu năm trăm nghìn đồng"),
        ]:
            got = ir(text)["read_string"]
            self.assertIn(want, got, f"{text!r} -> {got!r}")
        # không đụng ID thật và các dạng đã đọc đúng
        self.assertIn("chín tám bảy sáu năm bốn ba", ir("Mã đơn 9876543")["read_string"])
        self.assertIn("hai chấm bốn chấm một", ir("Phiên bản 2.4.1")["read_string"])
        self.assertIn("chín mươi chín nghìn đồng", ir("Giá 99.000 đồng")["read_string"])



    def test_slash_unit_glued_and_isbn(self):
        # mục 4.3 đánh giá độc lập: đ/lượt và ISBN không được rụng âm thầm
        self.assertIn("năm mươi nghìn đồng trên lượt", ir("Vé vào cửa 50.000đ/lượt.")["read_string"])
        self.assertIn("một trăm nghìn đồng trên lượt khách", ir("Giá 100.000 đ/lượt khách.")["read_string"])
        self.assertIn("đồng trên cái", ir("Vé 50.000 đ/cái.")["read_string"])
        r = ir("ISBN 978-604-1-12345-6 là mã sách.")["read_string"]
        self.assertIn("chín bảy tám gạch sáu không bốn gạch một", r)
        # không giẫm các dạng đã đọc đúng
        self.assertIn("một đến hai triệu đồng", ir("1-2 triệu đồng.")["read_string"])
        self.assertIn("hai, một", ir("tỉ số 2-1.")["read_string"])



if __name__ == "__main__":
    unittest.main()
