#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh bộ test FROZEN công khai (~1.000 câu) cho front-end TTS vi/anh.

Thiết kế tham khảo ý từ cuộc thảo luận benchmark (ViTTS-Bench, đề xuất
"gold reference + frozen set + entity-level + nhiều cách đọc hợp lệ"):

- Câu SYNTHETIC: sinh từ template, GOLD là CÂU ĐẦY ĐỦ đã verbalize,
  VIẾT SẴN theo template — KHÔNG sinh bằng hệ nào cả (không tuning).
  Mỗi câu có NHIỀU cách đọc hợp lệ (gold là danh sách) — ví dụ
  "một nghìn" hoặc "một ngàn" đều đúng.
- Câu REAL: lấy từ dataset_100k.tsv (corpus đối chiếu của dự án), gán
  category bằng regex. Câu real KHÔNG có gold đọc — chỉ đo leakage/drop,
  khách quan 100%.
- Category code-switch lấy nguyên các ví dụ Level 1→6 từ đề xuất benchmark
  (Easy / Interleaved / Dense / Ambiguous / Technical / adversarial).

Định dạng xuất:
  test_set.tsv : idx, split (synthetic|real), category, level, text, source
  gold.jsonl   : {"idx", "category", "gold_readings": [câu đầy đủ…],
                  "en_spans": [..]} — chỉ câu synthetic.

Frozen: file này chỉ chạy MỘT lần để sinh bộ test; sau đó test set không
được sửa (sửa = phải bump version và ghi lý do).
"""
import csv
import gzip
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL = HERE.parent / "listening_test" / "g2p_compare_100k" / "dataset_100k.tsv.gz"
random.seed(20261005)

# ---------------- số → chữ tiếng Việt (dùng để VIẾT GOLD, không phải
# để chạy hệ nào cả) ----------------

_D = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def _3w(n):
    """0..999 → chữ, kiểu 'hai trăm lẻ bảy'."""
    tr, r = divmod(n, 100)
    ch, dv = divmod(r, 10)
    out = []
    if tr:
        out.append(_D[tr] + " trăm")
        if ch == 0 and dv:
            out.append("lẻ")
    if ch == 1:
        out.append("mười")
        if dv == 5:
            out.append("lăm")
        elif dv:
            out.append(_D[dv])
    elif ch:
        out.append(_D[ch] + " mươi")
        if dv == 1:
            out.append("mốt")
        elif dv == 4:
            out.append("tư")
        elif dv == 5:
            out.append("lăm")
        elif dv:
            out.append(_D[dv])
    elif dv and not tr:
        out.append(_D[dv])
    return " ".join(out)


def n2w(n):
    """0..9999."""
    if n < 1000:
        return _3w(n) if n else "không"
    ng, r = divmod(n, 1000)
    s = _D[ng] + " nghìn"
    if r:
        if r < 100:
            s += " không trăm"
            if r:
                s += " lẻ " + _3w(r)
        else:
            s += " " + _3w(r)
    return s


def date_w(d, m, y):
    return [f"ngày {n2w(d)} tháng {n2w(m)} năm {n2w(y)}",
            f"{n2w(d)} tháng {n2w(m)} năm {n2w(y)}"]


def time_w(h, mi=None):
    hh = n2w(h)
    if mi is None or mi == 0:
        return [f"{hh} giờ", f"{hh} giờ không"]
    mm = n2w(mi)
    return [f"{hh} giờ {mm}", f"{hh} giờ lẻ {mm}" if mi < 10 else f"{hh} giờ {mm}"]


def dec_w(s):
    """'3,5' → 'ba phẩy năm'."""
    a, b = s.split(",")
    return f"{n2w(int(a))} phẩy " + " ".join(_D[int(c)] for c in b)


def money_w(s):
    """'250.000đ' → 'hai trăm năm mươi nghìn đồng'."""
    digits = re.sub(r"\D", "", s)
    n = int(digits)
    if n >= 1000:
        ng, r = divmod(n, 1000)
        head = f"{n2w(ng)} nghìn"
        return f"{head} {n2w(r)} đồng" if r else f"{head} đồng"
    return f"{n2w(n)} đồng"


def money_big_w(s):
    """'1.250.000' → 'một triệu hai trăm năm mươi nghìn' (thang tỷ/triệu/
    nghìn — v2, sinh gold cho tiền ≥ 7 chữ số; KHÔNG dùng để chạy hệ nào)."""
    n = int(re.sub(r"\D", "", s))
    parts = []
    for scale, word in ((10 ** 9, "tỷ"), (10 ** 6, "triệu"), (10 ** 3, "nghìn")):
        if n >= scale:
            q, n = divmod(n, scale)
            parts.append(f"{n2w(q)} {word}")
    if n:
        if parts and n < 100:
            parts.append("không trăm lẻ " + _3w(n))
        else:
            parts.append(_3w(n))
    return " ".join(parts)


ROWS = []


def add(cat, level, text, gold=None, spans=None):
    ROWS.append({"category": cat, "level": level, "text": text,
                 "gold_readings": gold or [], "en_spans": spans or []})


def family(cat, level, templates, values, readings, fixup=None, spans=None,
           gold_templates=None):
    """templates/format/values; gold = gold_template.format(cách đọc).

    readings[v] = danh sách cách đọc CỦA CÁI GIÁ TRỊ; gold câu đầy đủ =
    gold_templates.format(đọc) (mặc định dùng templates — nhưng khi câu
    test có ký hiệu cần verbalize như "12%", template gold phải tách riêng
    để không lòi "phần trăm%"). fixup(t) chỉnh các chữ số còn lại trong
    gold (vd 'phím 1' → 'phím một'); câu test giữ nguyên."""
    gts = gold_templates or templates
    for v in values:
        for t, gt in zip(templates, gts):
            text = t.format(v)          # câu test GIỮ NGUYÊN chữ số
            gold = [gt.format(r) for r in readings[v]]
            if fixup:                   # fixup chỉ áp lên gold
                gold = [fixup(g) for g in gold]
            add(cat, level, text, gold, spans)


# ---------------- SYNTHETIC ----------------

TIME_V = [(13, 0), (8, 30), (9, None), (14, 45), (21, 5), (7, 15),
          (16, 30), (23, 50), (6, None), (10, None), (18, 20), (11, 55)]
TIME_T = ["Cuộc họp bắt đầu lúc {} tại phòng họp số 3.",
          "Chương trình phát sóng lúc {} trên kênh truyền hình quốc gia.",
          "Tàu rời bến lúc {}, hành khách nên có mặt sớm ba mươi phút.",
          "Sự kiện khai mạc lúc {} tại Nhà hát Lớn."]
family("time", "easy", TIME_T, [f"{h}h" if mi is None else f"{h}h{mi:02d}"
                                for h, mi in TIME_V],
       {f"{h}h" if mi is None else f"{h}h{mi:02d}": time_w(h, mi)
        for h, mi in TIME_V})

DATE_V = [(5, 10, 2026), (31, 5, 1946), (1, 1, 2025), (28, 2, 2024),
          (15, 8, 2023), (9, 11, 2007)]
DATE_T = ["Hóa đơn được lập ngày {} tại chi nhánh Quận 1.",
          "Sự kiện lịch sử đó diễn ra vào ngày {}.",
          "Kỳ sát hạch bắt đầu từ ngày {}.",
          "Báo cáo tài chính phải nộp trước ngày {}.",
          "Chương trình bế mạc vào lúc 11h00 ngày {}."]


def _date_fix(t):
    # template cuối có sẵn '11h00' — verbalize cả nó trong gold
    return t.replace("11h00", "mười một giờ")


family("date", "easy", DATE_T, [f"{d:02d}/{m:02d}/{y}" for d, m, y in DATE_V],
       {f"{d:02d}/{m:02d}/{y}":
        [r.removeprefix("ngày ") for r in date_w(d, m, y)]
        for d, m, y in DATE_V},
       fixup=_date_fix)

PCT_V = ["3,5", "12", "0,5", "150", "45,25", "68", "1,5", "99,9", "33",
         "7,75"]
PCT_W = {v: ([dec_w(v) + " phần trăm"] if "," in v
             else [n2w(int(v)) + " phần trăm"])
         for v in PCT_V}
PCT_W["45,25"] = ["bốn mươi lăm phẩy hai mươi lăm phần trăm",
                  "bốn mươi lăm phẩy hai lăm phần trăm"]
PCT_T = ["Doanh thu quý này tăng {}% so với cùng kỳ.",
         "Pin còn {}% sau ba ngày sử dụng.",
         "Tỷ lệ hoàn thành đạt {}% trong tháng.",
         "Lãi suất tiết kiệm lên tới {}% một năm.",
         "Khoảng {}% người dùng chọn gói trả phí."]
PCT_T_GOLD = [t.replace("{}%", "{}") for t in PCT_T]
family("percent", "easy", PCT_T, PCT_V, PCT_W, gold_templates=PCT_T_GOLD)

MONEY_V = ["250.000đ", "1,2 triệu đồng", "99.000 VNĐ", "2 tỷ",
           "750 nghìn đồng", "15.500đ", "1,5 tỷ"]


def money_read(v):
    def head_w(h):
        return dec_w(h) if "," in h else n2w(int(h))
    if "triệu" in v:
        return [head_w(v.split(" ")[0]) + " triệu đồng"]
    if "tỷ" in v:
        return [head_w(v.split(" ")[0]) + " tỷ",
                head_w(v.split(" ")[0]) + " tỉ"]
    if "nghìn đồng" in v:
        n = int(re.sub(r"\D", "", v))
        return [n2w(n) + " nghìn đồng"]
    r = money_w(v)
    if "VNĐ" in v:
        return [r, r.replace("đồng", "v n đ")]
    return [r]


family("currency", "easy",
       ["Gói cước này có giá {} mỗi tháng.",
        "Tổng ngân sách dự kiến cho dự án là {}.",
        "Khách hàng đã thanh toán {} ngay tại quầy.",
        "Chi phí sửa chữa ước tính {}."],
       MONEY_V, {v: money_read(v) for v in MONEY_V})

# v2: tiền ≥ 7 chữ số — LƯU Ý sinh sau khối nhân bản tiền tố (bên dưới)
# để KHÔNG đụng luồng random: mọi câu/gold v1 giữ nguyên từng ký tự.
# Lớp này bị thiếu ở v1; lỗi đọc "1.000.000đ" thành "một chấm không chấm
# không đồng" của 0.2.1 đáng lẽ bị MÁY bắt chứ không phải bị người ngoài.
BIG_MONEY_V = ["1.000.000đ", "5.000.000 đồng", "1.250.000đ",
               "33.990.000 VNĐ", "1000000đ", "1 000 000 đồng",
               "1.000.000.000 đồng", "12.500.000 đồng", "4.999.999đ"]


def big_money_read(v):
    r = money_big_w(re.match(r"[\d .,]+", v).group(0).strip())
    if "VNĐ" in v:
        return [r + " đồng", r + " v n đ"]
    if "tỷ" in r:
        return [r + " đồng", r.replace("tỷ", "tỉ") + " đồng"]
    return [r + " đồng"]

UNIT_V = [("12 km", ["mười hai ki lô mét", "mười hai cây số"]),
          ("3,5 km", [dec_w("3,5") + " ki lô mét", dec_w("3,5") + " cây số"]),
          ("5 kg", ["năm ki lô gam"]),
          ("120 km/h", ["một trăm hai mươi ki lô mét một giờ"]),
          ("2 lít", ["hai lít"]),
          ("37 độ C", ["ba mươi bảy độ xê", "ba mươi bảy độ"]),
          ("500 MB", ["năm trăm em bai"]),
          ("12 GB", ["mười hai gi bai", "mười hai gi ga bai"])]
family("units", "easy",
       ["Quãng đường còn lại khoảng {}.",
        "Sản phẩm này nặng đúng {}, phù hợp mang theo máy bay.",
        "Thiết bị hỗ trợ dung lượng {}.",
        "Băng tải chạy tối đa {}."],
       [v for v, _ in UNIT_V], {v: w for v, w in UNIT_V})

PHONE_V = ["19006800", "0987654321", "18006963", "0241234567"]


def _phone_fix(t):
    return t.replace("phím 1 ", "phím một ")


family("phone", "easy",
       ["Hotline của tổng đài là {}, nhấn phím 1 để gặp tổng đài viên.",
        "Anh ấy để lại số {}, gọi lại bất cứ lúc nào.",
        "Số điện thoại đặt vé: {}."],
       PHONE_V,
       {v: [" ".join(_D[int(c)] for c in v)] for v in PHONE_V},
       fixup=_phone_fix)

family("email_url", "technical",
       ["Liên hệ support@example.com để được hỗ trợ.",
        "Gửi hồ sơ về email hotro@congty.vn trước hạn."],
       [""], {"": []})
add("email_url", "technical",
    "Truy cập https://example.com/docs để xem tài liệu.")
add("email_url", "technical",
    "Trang chủ của dự án là github.com/tc186052-creator.")
add("email_url", "technical", "Địa chỉ IP của server nội bộ là 10.0.0.1.")
add("email_url", "technical",
    "Mã lỗi HTTP 404 xuất hiện khi truy cập liên kết cũ.")

ACRO_V = [("HĐQT", ["hội đồng quản trị", "hờ đê quy tê"]),
          ("TP.HCM", ["thành phố Hồ Chí Minh", "tê pê hồ chí minh"]),
          ("NXB", ["nhà xuất bản", "ên xê bê"]),
          ("GS.TS", ["giáo sư tiến sĩ", "gờ sờ tê sờ"]),
          ("THPT", ["trung học phổ thông", "tê hờ pê tê"]),
          ("ĐT Việt Nam", ["đội tuyển Việt Nam", "đê tê Việt Nam"])]
ACRO_T = ["{} công bố kế hoạch kinh doanh quý 4.",
          "Đại diện {} xác nhận thông tin trên.",
          "Văn phòng {} đóng cửa vào cuối tuần."]


def _acro_fix(t):
    return t.replace("quý 4.", "quý tư.")


family("acronyms", "easy", ACRO_T, [v for v, _ in ACRO_V],
       {v: w for v, w in ACRO_V}, fixup=_acro_fix)
for v, w in ACRO_V:
    add("acronyms", "easy",
        f"Ngày 05/10, {v} có thông báo chính thức.",
        [f"ngày năm tháng mười, {x} có thông báo chính thức."
         for x in w])

# ---- code-switch Level 1→6: nguyên ví dụ từ đề xuất benchmark ----
add("code_switch", "L1", "Tôi dùng ChatGPT.", None, ["ChatGPT"])
add("code_switch", "L1", "Tôi code bằng Python.", None, ["code", "Python"])
add("code_switch", "L1", "Google vừa cập nhật Android.", None,
    ["Google", "Android"])
add("code_switch", "L1",
    "Tôi đang dùng ChatGPT để viết code Python cho project này.", None,
    ["ChatGPT", "code", "Python", "project"])
add("code_switch", "L2", "Tôi dùng ChatGPT để debug đoạn Python này.",
    None, ["ChatGPT", "debug", "Python"])
add("code_switch", "L2", "Anh ấy đang deploy model lên server.",
    None, ["deploy", "model", "server"])
add("code_switch", "L2", "Team sẽ review PR vào chiều nay.",
    None, ["Team", "review", "PR"])
add("code_switch", "L2",
    "Sếp gửi email cho team và yêu cầu review PR trước khi release.",
    None, ["email", "team", "review", "PR", "release"])
add("code_switch", "L3",
    "Tôi dùng Python với PyTorch để fine-tune model trên CUDA rồi deploy bằng Docker.",
    None, ["Python", "PyTorch", "fine-tune", "model", "CUDA", "deploy",
           "Docker"])
add("code_switch", "L3",
    "Startup dùng Kubernetes để scale hệ thống microservices lên AWS.",
    None, ["Startup", "Kubernetes", "scale", "microservices", "AWS"])
add("code_switch", "L4", "Anh ấy nói tôi cần check lại account.",
    None, ["check", "account"])
add("code_switch", "L4", "Tôi sẽ test service trước khi release.",
    None, ["test", "service", "release"])
add("code_switch", "L4", "Mai chúng ta meeting ở office.",
    None, ["meeting", "office"])
add("code_switch", "L4",
    "Cô ấy bắt đầu job mới sau khi nghỉ maternity leave.",
    None, ["job", "maternity leave"])
add("code_switch", "L4",
    "Đội tuyển ghi bàn ở phút bù giờ nhờ penalty bằng tay.", None,
    ["penalty"])
add("code_switch", "L5",
    "CPU load lên 85%, GPU memory khoảng 12 GB và API latency là 43 ms.",
    ["CPU load lên tám lăm phần trăm, GPU memory khoảng mười hai gi bai "
     "và API latency là bốn ba mi li giây.",
     "CPU load lên tám mươi lăm phần trăm, GPU memory khoảng mười hai "
     "gi ga bai và API latency là bốn mươi ba mi li giây."],
    ["CPU", "GPU", "API"])
add("code_switch", "L5",
    "Model đạt accuracy 97,8% trên tập test 10.000 câu.",
    ["Model đạt accuracy chín bảy phẩy tám phần trăm trên tập test "
     "mười nghìn câu.",
     "Model đạt accuracy chín mươi bảy phẩy tám phần trăm trên tập test "
     "một vạn câu."],
    ["Model", "accuracy", "test"])
add("code_switch", "L5",
    "Tốc độ upload chỉ đạt 25 Mbps trong khi gói quảng cáo là 300 Mbps.",
    ["Tốc độ upload chỉ đạt hai lăm em e p e s trong khi gói quảng cáo "
     "là ba trăm em e p e s.",
     "Tốc độ upload chỉ đạt hai mươi lăm megabit một giây trong khi gói "
     "quảng cáo là ba trăm megabit một giây."],
    ["upload", "Mbps"])
add("code_switch", "L6",
    "OpenAI GPT-5.6 API v1.2 chạy trên server H100 80GB.",
    None, ["OpenAI", "GPT", "API", "H100"])
add("code_switch", "L6",
    "Ngày 05/10/2026 tôi deploy v2.1.0-beta lên AWS us-east-1.",
    None, ["deploy", "AWS"])
add("code_switch", "L6",
    "Email support@example.com lúc 14h30, mã đơn ORD-2026-001.",
    None, ["Email"])
add("code_switch", "L6",
    "Từ 13h00 - 14h00 cùng ngày sẽ là hoạt động đón khách mời.",
    ["Từ mười ba giờ, mười bốn giờ cùng ngày sẽ là hoạt động đón khách mời.",
     "Từ mười ba giờ đến mười bốn giờ cùng ngày sẽ là hoạt động đón khách mời."])
add("code_switch", "L6",
    "Nâng cấp lên phiên bản 2.1.0 mất khoảng 45 phút downtime.",
    ["Nâng cấp lên phiên bản hai chấm một chấm không mất khoảng bốn lăm "
     "phút downtime.",
     "Nâng cấp lên phiên bản hai phẩy một phẩy không mất khoảng bốn "
     "mươi lăm phút downtime."],
    ["downtime"])
add("code_switch", "L6",
    "Deadline dự án là 28/02/2025, budget còn lại 15%.",
    ["Deadline dự án là ngày hai mươi tám tháng hai năm hai nghìn không "
     "trăm hai mươi lăm, budget còn lại mười lăm phần trăm."],
    ["Deadline", "budget"])
# biến thể CS có số (gold a-priori) để tăng mẫu chấm khớp đọc
family("code_switch", "L2",
       ["Tôi hẹn call với team lúc {} để review sprint này."],
       ["9h30", "15h45", "20h"],
       {v: time_w(*[int(x) for x in v.replace("h", " ").split()])[0:2]
        for v in ["9h30", "15h45", "20h"]},
       spans=["call", "team", "review", "sprint"])
family("code_switch", "L2",
       ["Sprint review và planning sẽ diễn ra ngày {}."],
       ["12/03/2026", "07/12/2027"],
       {v: date_w(int(v[:2]), int(v[3:5]), int(v[6:10])) for v in
        ["12/03/2026", "07/12/2027"]},
       spans=["Sprint", "review", "planning"])
family("code_switch", "L5",
       ["Server hiện tại chạy ổn định ở mức {} CPU với 8 GB RAM."],
       ["2,5%", "48%"],
       {"2,5%": ["hai phẩy năm phần trăm"], "48%": ["bốn mươi tám phần trăm"]},
       fixup=lambda t: t.replace("8 GB", "tám gi bai"),
       spans=["Server", "CPU", "GB", "RAM"])

# ---- adversarial ----
ADV = [
    ("Phiên bản v2.1.0-beta đã được triển khai lên máy chủ nội bộ.",
     ["Phiên bản v hai chấm một chấm không beta đã được triển khai lên "
      "máy chủ nội bộ.",
      "Phiên bản v hai phẩy một phẩy không beta đã được triển khai lên "
      "máy chủ nội bộ."]),
    ("Chuyến bay VN-A356 khởi hành lúc 05h40 từ sân bay Tân Sơn Nhất.",
     ["Chuyến bay v n ê a ba lăm sáu khởi hành lúc "
      + w + " từ sân bay Tân Sơn Nhất." for w in time_w(5, 40)]),
    ("Cửa hàng mở cửa từ 7h đến 22h tất cả các ngày trong tuần.",
     ["Cửa hàng mở cửa từ " + a + " đến " + b +
      " tất cả các ngày trong tuần."
      for a in time_w(7, None) for b in time_w(22, None)][:2]),
    ("Đường dây nóng tiếp nhận trong giờ hành chính từ 8h00 đến 17h30.",
     ["Đường dây nóng tiếp nhận trong giờ hành chính từ " + a + " đến "
      + b + "." for a in time_w(8, 0) for b in time_w(17, 30)][:2]),
    ("Mã giảm giá giảm 50% cho đơn hàng trên 500.000đ.",
     ["Mã giảm giá giảm năm mươi phần trăm cho đơn hàng trên "
      + money_w("500.000đ") + "."]),
    ("Tỷ giá hôm nay: 1 USD = 25.450đ.",
     ["Tỷ giá hôm nay: một USD bằng " + money_w("25.450đ") + "."]),
    ("Xe máy biển số 51K-123.45 bị lập biên bản lúc 16h20.",
     None),
    ("Sổ đỏ cấp ngày 12/07/1998, diện tích 120,5 m2.",
     ["Sổ đỏ cấp " + w + ", diện tích " + dec_w("120,5") + " mét vuông."
      for w in date_w(12, 7, 1998)]),
    ("Kỳ hạn gửi tiết kiệm 6 tháng, lãi suất 5,6% một năm.",
     ["Kỳ hạn gửi tiết kiệm " + n2w(6) + " tháng, lãi suất "
      + dec_w("5,6") + " phần trăm một năm."]),
    ("Cập nhật bản vá 1.2.3.4 vào 2h sáng nay.",
     ["Cập nhật bản vá một chấm hai chấm ba chấm bốn vào " + w +
      " sáng nay." for w in time_w(2, None)]),
    ("Khoảng cách từ Trái Đất tới Mặt Trời khoảng 149,6 triệu km.",
     ["Khoảng cách từ Trái Đất tới Mặt Trời khoảng " + dec_w("149,6") +
      " triệu ki lô mét."]),
    ("Thuốc uống ngày 2 lần, mỗi lần 1 viên sau ăn 30 phút.",
     ["Thuốc uống ngày " + n2w(2) + " lần, mỗi lần " + n2w(1) +
      " viên sau ăn " + n2w(30) + " phút."]),
    ("Phim chiếu rạp từ 21h00, giá vé 120.000đ mỗi suất.",
     ["Phim chiếu rạp từ " + w + ", giá vé " + money_w("120.000đ") +
      " mỗi suất." for w in time_w(21, 0)]),
    ("Hợp đồng số 2026/HD-015 có hiệu lực từ ngày 01/04/2026.",
     None),
    ("Bệnh nhân 45 tuổi, số điện thoại 0912345678, khám lúc 9h15.",
     ["Bệnh nhân " + n2w(45) + " tuổi, số điện thoại "
      + " ".join(_D[int(c)] for c in "0912345678")
      + ", khám lúc " + time_w(9, 15)[0] + "."]),
]
for row in ADV:
    if row[1] is None:
        add("adversarial", "adversarial", row[0])
    else:
        add("adversarial", "adversarial", row[0], row[1])

# nhân bản synthetic (thêm tiền tố ngữ cảnh, gold đổi tương ứng)
extra = [r for r in ROWS if r["gold_readings"]]
random.shuffle(extra)
for r in extra[:140]:
    pre = random.choice(["Hôm qua, ", "Theo thông báo mới, ",
                         "Anh cho biết: ", "Theo đề án, ",
                         "Riêng trong tháng này, "])
    t2 = pre + r["text"][0].lower() + r["text"][1:]
    g2 = [pre + g[0].lower() + g[1:] for g in r["gold_readings"]]
    add(r["category"], r["level"], t2, g2, r["en_spans"])

# v2: family big_money sinh TẠI ĐÂY (sau nhân bản, trước SYN) — không
# đụng luồng random nên mọi câu/gold khác giữ nguyên như v1
family("currency", "big_money",
       ["Đơn hàng này có giá {} đã bao gồm phí vận chuyển.",
        "Doanh thu công ty đạt {} trong quý vừa rồi.",
        "Chị ấy dành dụm được {} sau hai năm làm việc.",
        "Khoản đầu tư ban đầu chiếm {}."],
       BIG_MONEY_V, {v: big_money_read(v) for v in BIG_MONEY_V})

SYN = list(ROWS)
print(f"synthetic: {len(SYN)} câu "
      f"({sum(1 for r in SYN if r['gold_readings'])} có gold)")

# ---------------- REAL — corpus, gán category bằng regex ----------------

RE_PCT = re.compile(r"\d+\s*%")
RE_DATE = re.compile(r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b")
RE_TIME = re.compile(r"\b\d{1,2}h\d{0,2}\b")
RE_MONEY = re.compile(r"\d+[.,]?\d*\s*(triệu|tỷ|nghìn đồng)|"
                      r"\d{1,3}(\.\d{3})+\s*(đ|VNĐ)")
RE_UNIT = re.compile(r"\d+\s?(km|kg|GB|MB|cm|mm|m2|ha)\b")
RE_MAIL = re.compile(r"[\w.]+@[\w.]+|https?://|\bwww\.")
RE_VER = re.compile(r"\bv?\d+\.\d+(\.\d+)*\b")
RE_ACRO = re.compile(r"\b[A-ZĐ]{2,}(?:[.\-][A-ZĐ]{2,})*\b")
RE_DIG = re.compile(r"\d")
RE_LATIN = re.compile(r"\b[A-Za-z]{2,}\b")

rows = []
with gzip.open(REAL, "rt", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        t = (r.get("text") or "").strip()
        if t and 30 <= len(t) <= 220:
            rows.append((r.get("lang") or "?", t))

random.shuffle(rows)
BUDGET = {"time": 60, "date": 60, "percent": 40, "currency": 40,
          "units": 30, "email_url": 20, "adversarial": 20,
          "acronyms": 120, "code_switch": 100, "numbers": 80,
          "foreign_names": 40, "loanwords": 30}
got = {k: 0 for k in BUDGET}
REAL_ROWS = []
for lang, t in rows:
    if len(REAL_ROWS) >= 700:
        break
    if RE_VER.search(t):
        cat = "adversarial"
    elif RE_MAIL.search(t):
        cat = "email_url"
    elif RE_TIME.search(t):
        cat = "time"
    elif RE_DATE.search(t):
        cat = "date"
    elif RE_PCT.search(t):
        cat = "percent"
    elif RE_MONEY.search(t):
        cat = "currency"
    elif RE_UNIT.search(t):
        cat = "units"
    elif lang == "en":
        cat = "foreign_names"
    elif lang == "mixed" and RE_LATIN.search(t):
        cat = "code_switch"
    elif lang == "mixed":
        cat = "loanwords"
    elif RE_ACRO.search(t):
        cat = "acronyms"
    elif RE_DIG.search(t):
        cat = "numbers"
    else:
        continue
    if got[cat] >= BUDGET[cat]:
        continue
    got[cat] += 1
    REAL_ROWS.append((cat, t))

print(f"real: {len(REAL_ROWS)} câu — "
      + ", ".join(f"{k}={v}" for k, v in sorted(got.items()) if v))

# ---------------- ghi file ----------------
ALL = [("synthetic", r["category"], r["level"], r["text"],
        "template (gold viết tay a-priori)") for r in SYN] + \
      [("real", cat, "-", t, "dataset_100k.tsv") for cat, t in REAL_ROWS]

with open(HERE / "test_set.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["idx", "split", "category", "level", "text", "source"])
    for i, (sp, cat, lv, t, src) in enumerate(ALL):
        w.writerow([i, sp, cat, lv, t, src])

with open(HERE / "gold.jsonl", "w", encoding="utf-8") as f:
    for i, (sp, cat, lv, t, src) in enumerate(ALL):
        if sp == "synthetic":
            r = SYN[i]
            f.write(json.dumps({"idx": i, "category": cat,
                                "gold_readings": r["gold_readings"],
                                "en_spans": r["en_spans"]},
                               ensure_ascii=False) + "\n")

# Frozen versioning: sửa test set = bắt buộc bump version + ghi lý do.
FROZEN_META = {
    "frozen_version": 2,
    "seed": 20261005,
    "date": "2026-10-05",
    "changes": [
        {"from": 1, "to": 2,
         "reason": "thêm level 'currency/big_money' (9 giá trị tiền ≥ 7 chữ"
                   " số × 4 template = 36 câu synthetic) — lớp dữ liệu bị"
                   " thiếu ở v1, lỗi đọc '1.000.000đ' thành 'một chấm không"
                   " chấm không đồng' của wheel 0.2.1 do đánh giá độc lập"
                   " 2026-10 phát hiện; mọi câu/gold khác GIỮ NGUYÊN."},
    ],
}
with open(HERE / "frozen_meta.json", "w", encoding="utf-8") as f:
    json.dump(FROZEN_META, f, ensure_ascii=False, indent=2)

print(f"TỔNG: {len(ALL)} câu → test_set.tsv + gold.jsonl (frozen v{FROZEN_META['frozen_version']})")
