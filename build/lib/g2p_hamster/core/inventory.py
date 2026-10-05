# -*- coding: utf-8 -*-
"""inventory.py — loader + collision-audit cho master inventory `ham/0.2`
(vòng 6.3: thêm PHONE_OPEN_E_PREVELAR; lịch sử ham/0.1 giữ trong provenance).

Audit 7 điều (inventory_schema.md bản 2.1 — duyệt mức thiết kế, nghiệm thu bằng test):
  1. mỗi semantic_id → đúng 1 nghĩa (ID unique, không trùng)
  2. trùng unicode repr giữa ≥2 ID → FAIL trừ khi nhóm ID là tập con của một nhóm
     SHARED_UNICODE_REPR (định dạng theo nhóm: unicode + ids + reason)
  3. không symbol ma: mọi ID được nhãn bảng thuộc tập hợp lệ (segment/prosody/control)
  4. prosody/control không được là segment (tách lớp)
  5. segment KHÔNG chứa code point nhóm Unicode Number nào (category N — từng code point)
  6. mọi cặp required_contrasts tồn tại + khác ID (khác unicode KHÔNG là tiêu chí)
  7. audit va chạm phát âm (realization-collision): gom theo chuỗi semantic ID GỒM prosody;
     nhóm >1 chính tả phải được MERGE_RULES có phạm vi giải thích ĐẦY ĐỦ — hook, fase B

Trạng thái output tách tĩnh/thực thi: điều 1-6 PASS ≠ 7/7 — điều 7 NOT_RUN tới fase B.
Giới hạn trung thực: audit bắt xung đột ĐÃ MÔ HÌNH HÓA; tính đúng âm vị học do gold set
+ fixtures đảm bảo, không phải do audit.
"""
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TSV = HERE / "02_data" / "inventory_ham.tsv"

LOAI_OK = {"segment", "prosody", "control"}
TONE_IDS = {"TONE_NGANG", "TONE_HUYEN", "TONE_SAC", "TONE_HOI", "TONE_NGA", "TONE_NANG"}
STRESS_IDS = {"STRESS_PRIMARY", "STRESS_SECONDARY"}

# Bảng required_contrasts — duyệt ĐỘC LẬP với bảng luật (đặc tả 4.2); sửa bảng này = sửa spec
REQUIRED_CONTRASTS = [
    ("PHONE_TR", "PHONE_C"),          # tr/ch
    ("PHONE_S_RETRO", "PHONE_S"),     # s/x
    ("PHONE_Z", "PHONE_GI"),          # d/gi
    ("PHONE_Z", "PHONE_R_VI"),        # d/r
    ("PHONE_GI", "PHONE_R_VI"),       # gi/r
    ("PHONE_Z", "PHONE_D_IMP"),       # d/đ
    ("PHONE_A_LONG", "PHONE_A_SHORT"),# a/ă (tam/tăm)
    ("PHONE_OPEN_E", "PHONE_E"),      # e/ê
    ("PHONE_OPEN_O", "PHONE_O"),      # o/ô
    ("PHONE_OPEN_O", "PHONE_SCHWA_LONG"),  # o/ơ
    ("PHONE_U", "PHONE_UHORN"),       # u/ư
    ("PHONE_SCHWA", "PHONE_SCHWA_LONG"),   # â/ơ
    ("TONE_NGANG", "TONE_HUYEN"), ("TONE_NGANG", "TONE_SAC"), ("TONE_NGANG", "TONE_HOI"),
    ("TONE_NGANG", "TONE_NGA"), ("TONE_NGANG", "TONE_NANG"),
    ("TONE_HUYEN", "TONE_SAC"), ("TONE_HUYEN", "TONE_HOI"), ("TONE_HUYEN", "TONE_NGA"),
    ("TONE_HUYEN", "TONE_NANG"), ("TONE_SAC", "TONE_HOI"), ("TONE_SAC", "TONE_NGA"),
    ("TONE_SAC", "TONE_NANG"), ("TONE_HOI", "TONE_NGA"), ("TONE_HOI", "TONE_NANG"),
    ("TONE_NGA", "TONE_NANG"),
    ("PHONE_THETA", "PHONE_TH"),      # en θ ≠ vi tʰ
    ("PHONE_ZH", "PHONE_R_VI"),       # en ʒ ≠ vi ʐ
    ("PHONE_AH", "PHONE_SCHWA"),      # ʌ ≠ ə (AH1 vs AH0)
]
# đối lập mức CHUỖI ÂM TIẾT (tai≠tay…) — kiểm bằng generator âm tiết (điều 7)
# 02/10/2026 người duyệt KHÔNG chấp thuận bỏ "mác≠mách": ba đối lập mác≠mách≠mắc
# (và khác≠khách≠khắc) bắt buộc ở mức master. VÒNG 6.3 (ràng buộc từ quyết reviewer v11
# 2026-10-02 §4; encoding: lựa chọn tác giả v12): BIỂU DIỄN ach ĐỔI — vần 'ach' → PHONE_OPEN_E_PREVELAR (ham/0.2),
# KHÔNG còn = 'ec'; 10 cặp ach/ec dưới đây là đối lập BẮT BUỘC ở mức segment
# (2 cặp có đối chiếu mục từ độc lập: sách/Séc, mách/méc; 8 cặp còn lại là
# policy mặc định bảo toàn LỚP VẦN — chưa thẩm định audio từng cặp).
SYLLABLE_LEVEL_CONTRASTS = [
    ("tai", "tay"), ("cao", "cau"), ("mác", "mách"), ("khắc", "khác"),
    ("an", "anh"), ("nam", "năm"), ("tam", "tăm"), ("suất", "suốt"), ("que", "quê"),
    # vòng 4 (F01): uy composite vs ui coda — lỗi thật đã bị MR-I-Y che trước đây
    ("tui", "tuy"), ("thúi", "thúy"),
    # vòng 6.3 (reviewer v11 §4.2-4.3): ach/ec giữ đối lập ở master mặc định
    ("sách", "séc"), ("mách", "méc"), ("bách", "béc"), ("hách", "héc"),
    ("mạch", "mẹc"), ("tách", "téc"), ("vách", "véc"), ("xách", "xéc"),
    ("ách", "éc"), ("ạch", "ẹc"),
]

# Allowlist trùng unicode repr — schema bản 2.1 (điều 2), định dạng THEO NHÓM:
#   {"unicode": "ə", "ids": ["PHONE_SCHWA_VI", "PHONE_SCHWA_EN"], "reason": "..."}
# Nhóm trùng thực tế phải là TẬP CON của một nhóm khai báo cùng unicode
# (nhóm 3 ID chỉ cần 1 entry; khai 1 cặp mà có ID thứ 3 cùng repr → FAIL).
# CẤM sửa IPA cho khác đi chỉ để vượt audit.
SHARED_UNICODE_REPR = [
    {"unicode": "ɛ",
     "ids": ["PHONE_OPEN_E", "PHONE_OPEN_E_PREVELAR"],
     "reason": "cùng ký hiệu IPA ɛ nhưng HAI category riêng — vần 'ach' có tiếp "
               "xúc prevelar trước coda k (ràng buộc giữ đối lập: quyết reviewer "
               "v11 2026-10-02; encoding: lựa chọn tác giả v12 — duyệt có điều "
               "kiện hậu kiểm v12 §3.1; Kirby 2011 tr.383-384). ham/0.2: thêm "
               "ID mới, PHONE_OPEN_E bất biến, không đụng en EH."},
]

# Va chạm chủ đích — MERGE_RULES có phạm vi (schema bản 2, thay INTENTIONAL_MERGES cũ):
#   level "segment": các ID là một acoustic category chủ đích (không đối lập)
#   level "syllable": các cặp chính tả khác nhau cho CÙNG chuỗi master — hợp lệ
# "matcher" = trường MÁY KIỂM để audit điều 7 tự phán một nhóm collision có được giải
#   thích trọn vẹn không (acceptance 3.2). VÒNG 4 (F04 — báo cáo reviewer): matcher
#   chạy trên PARSED PARTS (onset, glide_letter, form, tail) từ vi_rules.parse_skeleton,
#   KHÔNG còn global replace trên skeleton — replace toàn cục không kiểm vai trò chữ
#   (của onset rule đụng coda ac/ak, của glide rule đụng ke/kê) và đã che lỗi thật
#   tui/tuy qua MR-I-Y. Kind (áp ĐÚNG thành phần, biên thành phần giữ nguyên):
#     role_alt        {"role": "onset|glide|form|tail", "alt": {k: k'}} — thay MỘT
#                     thành phần nếu khớp key (key dài trước)
#     composite_alt   {"alt": {glide+form: glide'+form'}} — chỉ khi CÓ glide
#     onset_glide_alt {"alt": {"onset:glide": [onset', glide']}} — cấu trúc
#                     onset+glide (vd "k:u" → ["qu",""]; qu là chính tả chuẩn)
#     rhyme_alt       {"alt": {"form:tail": "form':tail'"}} — vần+coda cùng lúc (ach↔ec)
#   Rule không có matcher không tham gia phán điều 7.
# "approved" = TRẠNG THÁI DUYỆT (yêu cầu người duyệt 02/10/2026): true = có dấu vết
#   duyệt tường minh cho SCOPE/matcher cụ thể; false = đề xuất — KHÔNG được làm gate
#   nghiệm thu. Vòng 4: MR-I-Y bị HẠ CỜ (matcher global che lỗi tui/tuy — F01/F04);
#   KHÔNG còn rule nào approved=true ở tầng matcher. explain_collision_tiered thử
#   approved trước, rồi proposal — không bao giờ tự nâng proposal thành approved.
# Quy trình khi generator gặp nhóm trùng: xuất báo cáo → người duyệt → thêm rule
# CÓ PHẠM VI. CẤM tự bơm toàn bộ nhóm trùng (audit luôn xanh = vô nghĩa).
MERGE_RULES = [
    {
        "rule_id": "MR-I-Y",
        "level": "segment",
        "ids": ["PHONE_I", "PHONE_J"],
        "matcher": {"kind": "role_alt", "role": "form",
                    "alt": {"y": "i", "ya": "ia", "yê": "iê"}},
        "approved": False,
        "approved_basis": "HẠ CỜ 02/10/2026 vòng 4 (reviewer F01/F04): matcher global "
                          "replace letter_alt trước đây đã giải thích collision SAI THẬT "
                          "tui/tuy (lỗi parser F01 được rule 'đã duyệt' + regression che). "
                          "Danh mục INTENTIONAL_MERGES={PHONE_I} của đặc tả vẫn là nguồn "
                          "chỉ đích category, nhưng SCOPE matcher phải được duyệt lại "
                          "riêng: matcher role='form' hiện chỉ đụng nguyên âm (không coda "
                          "— tai/tay, quai/quay không bị giải thích), chờ duyệt phạm vi "
                          "hẹp (lí/lý, kí/ký) sau khi gold mở rộng + test âm pass.",
        "scope": "chữ 'i' và 'y' là một acoustic category ở VỊ TRÍ NGUYÊN ÂM (form): "
                 "nucleus → PHONE_I. KHÔNG đụng coda (tail i/y → PHONE_J là ánh xạ "
                 "CODA_MAP, không phải rule này) và không đụng chữ trong onset.",
        "fixtures": ["kí = ký", "tí = tý", "qui = quy", "lí = lý"],
    },
    {
        "rule_id": "MR-ONSET-GH-G",
        "level": "segment",
        "ids": ["PHONE_GH", "PHONE_NG"],
        "matcher": {"kind": "role_alt", "role": "onset", "alt": {"ngh": "ng", "gh": "g"}},
        "approved": False,
        "approved_basis": "Nguồn: bảng chữ→ID A1 (gh→PHONE_GH, ngh→PHONE_NG). Duyệt "
                          "inventory KHÔNG tự động duyệt rule. Vòng 4: fixtures cũ "
                          "ga/gha, nga/ngha nằm NGOÀI chính tả lõi (gh/ngh chỉ trước "
                          "e,ê,i,y — miền core đã siết) — rule chỉ còn ý nghĩa ở lớp "
                          "stress-test; chờ duyệt nếu xuất hiện nhóm core thật.",
        "scope": "biến thể chính tả onset gh/ngh = g/ng cùng PHONE_GH/PHONE_NG — CHỈ "
                 "onset, không đụng chữ c/k ở vị trí khác",
        "fixtures": ["[stress] ga = gha", "[stress] nga = ngha"],
    },
    {
        "rule_id": "MR-ONSET-C-K",
        "level": "segment",
        "ids": ["PHONE_K"],
        "matcher": {"kind": "role_alt", "role": "onset", "alt": {"c": "k"}},
        "approved": False,
        "approved_basis": "Nguồn: bảng chữ→ID A1 (c/k onset → PHONE_K). Vòng 4: matcher "
                          "role='onset' KHÔNG còn phán nhóm coda (ac/ak — probe reviewer) "
                          "và miền core đã siết k-onset bổ túc trước e,ê,i,y nên hầu hết "
                          "nhóm c/k rơi lớp stress. Chờ duyệt phạm vi.",
        "scope": "onset 'c' và 'k' cùng PHONE_K — CHỈ onset. Chính tả lõi: c/k BỔ TÚC "
                 "(c trước a,ă,â,o,ô,ơ,u,ư; k trước e,ê,i,y) nên nhóm core thực tế hiếm",
        "fixtures": ["[stress] ca = ka"],
    },
    {
        "rule_id": "MR-CODA-CH-C",
        "level": "segment",
        "ids": ["PHONE_K"],
        "matcher": {"kind": "role_alt", "role": "tail", "alt": {"ch": "c"}},
        "approved": False,
        "approved_basis": "Nguồn: inventory note A1 'vi c/ch coda cũng PHONE_K' + yêu cầu "
                          "duyệt 02/10 (đối lập bảo toàn ở NGUYÊN ÂM). Chờ duyệt rule "
                          "cùng xem từng cặp cụ thể; không kế thừa A1. Vòng 4: 'ộk' là "
                          "ca ngoại lai (coda k không chính tả lõi — rớt core), fixture "
                          "chỉ giữ cặp core.",
        "scope": "coda chính tả 'ch' và 'c' cùng PHONE_K — CHỈ tail; khác biệt palatal "
                 "hóa [c]~[k] không mô hình hóa; đối lập nơi coda gộp phải bảo toàn ở "
                 "phần còn lại của vần (ach = PHONE_OPEN_E, xem COND_NUC/vi_rules)",
        "fixtures": ["ích = íc"],
    },
    {
        "rule_id": "MR-CODA-O-U",
        "level": "segment",
        "ids": ["PHONE_W"],
        "matcher": {"kind": "role_alt", "role": "tail", "alt": {"o": "u"}},
        "approved": False,
        "approved_basis": "Nguồn: inventory A1 (PHONE_W = glide o/u). Duyệt inventory "
                          "≠ duyệt rule; chờ duyệt phạm vi. Vòng 4/5: reviewer yêu cầu "
                          "test cao/cau — KHÔNG được giải thích: engine bảo toàn record "
                          "chặn tail o→u khi COND_NUC (a,u) đổi nucleus (A_LONG→A_SHORT). "
                          "Fixture 'kẻo = kêu' đã BỎ (vòng 5): không phải cặp đồng âm "
                          "(khác thanh hỏi/ngang) — không làm bằng chứng rule.",
        "scope": "coda 'o' và 'u' cùng PHONE_W khi giữ nguyên vần còn lại (ưu = ưo) — "
                 "'cao'≠'cau' nhờ NGUYÊN ÂM (COND_NUC), không nhờ coda",
        "fixtures": ["ưu = ưo"],
    },
    {
        "rule_id": "MR-CODA-I-Y",
        "level": "segment",
        "ids": ["PHONE_J"],
        "matcher": {"kind": "role_alt", "role": "tail", "alt": {"y": "i"}},
        "approved": False,
        "approved_basis": "ĐỀ XUẤT vòng 5 — lộ ra sau khi core nhận ây (V5-01): coda "
                          "chính tả 'i' và 'y' cùng PHONE_J (CODA_MAP) nên âi = ây là "
                          "collision thật, trước đây bị che vì ây bị phân nhầm stress. "
                          "Engine bảo toàn record TỰ CHẶN y→i sau form 'a' (COND_NUC "
                          "(a,y)=A_SHORT — tai≠tay, quai≠quay vẫn giữ). Chờ duyệt phạm vi.",
        "scope": "coda 'y' = 'i' cùng PHONE_J khi nucleus KHÔNG đổi (âi/ây, oi/oy nếu "
                 "gặp) — KHÔNG đụng form (ký=ký là MR-I-Y), KHÔNG áp được sau 'a' vì "
                 "ay = /aj/ ngắn (engine chặn từng bước, không phải khai báo ở đây)",
        "fixtures": ["ây = âi"],
    },
    {
        "rule_id": "MR-GLIDE-O-U",
        "level": "segment",
        "ids": ["PHONE_W"],
        "matcher": {"kind": "role_alt", "role": "glide", "alt": {"o": "u"}},
        "approved": False,
        "approved_basis": "ĐỀ XUẤT fase B — chờ duyệt bằng test âm thực tế và scope cụ "
                          "thể. Vòng 4/5 sửa fixtures: 'khoa = khua' SAI — hai từ này "
                          "CÙNG onset kh, khác vần oa/ua (nucleus A_LONG vs U_SCHWA — "
                          "vòng trước ghi nhầm 'khác onset k/kh'); '[stress] hoa = hua' "
                          "cũng bỏ — 'hua' parse là bare ua (U_SCHWA), không composite. "
                          "Cặp thật của rule: composite oê/uê cùng coda (coến/cuến).",
        "scope": "chữ glide 'o' và 'u' cùng PHONE_W khi composite sau onset VÀ cả hai "
                 "composite được khai cùng nucleus (oê/uê = W+PHONE_E) — CHỈ thành "
                 "phần glide; bước đổi glide phải bảo toàn record (engine vòng 5)",
        "fixtures": ["coến = cuến (oê/uê cùng tail n → cùng chuỗi W,E)"],
    },
    {
        "rule_id": "MR-UE-UÊ",
        "level": "segment",
        "ids": ["PHONE_E"],
        "matcher": {"kind": "composite_alt", "alt": {"ue": "uê"}},
        "approved": False,
        "approved_basis": "ĐỀ XUẤT fase B — chờ duyệt. Vòng 4: matcher composite_alt chỉ "
                          "áp khi CÓ glide (probe reviewer: ke/kê không glide → không bị "
                          "giải thích; que/quê qua nhánh qu cũng glide_letter='' → không "
                          "bị giải thích). Fixture cũ 'Huế = thuê' sai (khác tone/onset "
                          "— không phải đồng âm) đã bỏ.",
        "scope": "chính tả composite 'ue' = 'uê' sau glide w (hue/thuê/kue) cùng chuỗi "
                 "W+PHONE_E — bare e/ê (không glide) KHÔNG thuộc rule",
        "fixtures": ["hue = huê (cùng chuỗi W,E)", "kue = kuê"],
    },
    {
        "rule_id": "MR-QU-K-GLIDE",
        "level": "segment",
        "ids": ["PHONE_K", "PHONE_W"],
        "matcher": {"kind": "onset_glide_alt", "alt": {"k:u": ["qu", ""]}},
        "approved": False,
        "approved_basis": "ĐỀ XUẤT fase B — chờ duyệt. Vòng 4/5: fixture cũ 'qua = "
                          "khoa' SAI (qu→PHONE_K còn khoa là PHONE_KH — probe reviewer). "
                          "Hướng canonicalize k+glide-u → qu (qu là chính tả chuẩn). "
                          "Vòng 5: engine bảo toàn record CHẶN k:u→qu trên kue/que "
                          "(nucleus GLIDE_FORMS 'ue' = PHONE_E ≠ BASE_NUC 'e' = "
                          "PHONE_OPEN_E ở nhánh qu — khác nguyên âm, phải khác chuỗi); "
                          "qua/koa cũng KHÔNG còn được nối (bước trung gian 'kua' không "
                          "phải chính tả). Cặp còn trong scope: kuy/quy (cùng K,W,I).",
        "scope": "'qu' = PHONE_K + glide PHONE_W — cấu trúc onset 'qu'+glide rỗng ↔ "
                 "onset 'k'+glide 'u', CHỈ khi nucleus không đổi (uy ↔ qu+y; các nhánh "
                 "uê/e chọn nucleus khác nhau nên bị engine chặn)",
        "fixtures": ["[stress] kuy = quy (cùng chuỗi K,W,I)"],
    },
]

# Rule đã RÚT KHỎI danh mục thực thi (giữ lịch sử — yêu cầu reviewer vòng 4: loại khỏi
# catalog, không giữ như merge đang chờ hợp thức hóa).
WITHDRAWN_RULES = [
    {
        "rule_id": "MR-tai-tay",
        "withdrawn": "02/10/2026 vòng 4 (đề xuất vòng 3 bị từ chối)",
        "reason": "Yêu cầu lịch sử là ĐỐI LẬP BẮT BUỘC tai ≠ tay, không phải cơ sở duyệt "
                  "rule fold gộp phát âm; rule nếu áp còn PHÁ đối lập (COND_NUC "
                  "(a,y)=A_SHORT làm tay ≠ tai ở segment). Không có matcher, chưa từng "
                  "tham gia phán điều 7.",
    },
    {
        "rule_id": "MR-ACH-EC",
        "withdrawn": "02/10/2026 vòng 6.3 (reviewer v11 §4.2-4.4: KHÔNG DUYỆT — "
                     "không treo như proposal chờ nghe model)",
        "reason": "Có căn cứ độc lập phân biệt sách/Séc và mách/méc (phiên âm mục từ "
                  "[sajk̟̚˧˦] vs [sɛk̚˧˦]; Kirby 2011 tr.383-384 — hiện thực prevelar, "
                  "không suy 'ch có thể phân tích /k/' thành đồng nhất toàn vần). "
                  "ham/0.2: vần 'ach' → PHONE_OPEN_E_PREVELAR — 10 cặp ach/ec (sách/séc, "
                  "mách/méc, bách/béc, hách/héc, mạch/mẹc, tách/téc, vách/véc, xách/xéc, "
                  "ách/éc, ạch/ẹc) là ĐỐI LẬP ở master mặc định (2 cặp có đối chiếu mục "
                  "từ, 8 cặp policy bảo toàn lớp vần — chưa thẩm định audio từng cặp). "
                  "Biểu diễn dùng cho acoustic phải giữ thông tin phân biệt; audio sinh "
                  "từ pipeline gộp hai record không thể là chứng cứ đồng âm độc lập.",
    },
]


# ---------------------- Approval EXACT FIXTURE (vòng 6.3, reviewer v11 §3) ----------
# Quyết reviewer v11 2026-10-02: duyệt ĐÚNG 26 cặp i/y ở MỨC FIXTURE — phép so sánh
# NFC/lowercase KHÔNG được biến thành bỏ dấu thanh; không suy rộng sang cặp khác
# thanh, ya/ia, yê/iê, đọc chữ cái, hay toàn bộ matcher MR-I-Y (flag rộng vẫn False —
# probe reviewer: bật flag sẽ nâng 52 nhóm, 26 ngoài bộ 26). Expected record viết
# tường minh bởi reviewer (approved_exact_fixtures_v11.json), đã khớp parser.
APPROVED_EXACT_FIXTURES = [
    # (word_1, word_2, onset, glide, nucleus, coda, tone, origin)
    ("kí", "ký", "PHONE_K", [], "PHONE_I", [], "TONE_SAC", "vòng 6.1 xác nhận"),
    ("lí", "lý", "PHONE_L", [], "PHONE_I", [], "TONE_SAC", "vòng 6.1 xác nhận"),
    ("kì", "kỳ", "PHONE_K", [], "PHONE_I", [], "TONE_HUYEN", "vòng 6.1 xác nhận"),
    ("kĩ", "kỹ", "PHONE_K", [], "PHONE_I", [], "TONE_NGA", "vòng 6.1 xác nhận"),
    ("mĩ", "mỹ", "PHONE_M", [], "PHONE_I", [], "TONE_NGA", "vòng 6.1 xác nhận"),
    ("sĩ", "sỹ", "PHONE_S_RETRO", [], "PHONE_I", [], "TONE_NGA", "vòng 6.1 xác nhận"),
    ("tỉ", "tỷ", "PHONE_T", [], "PHONE_I", [], "TONE_HOI", "vòng 6.1 xác nhận"),
    ("qui", "quy", "PHONE_K", ["PHONE_W"], "PHONE_I", [], "TONE_NGANG",
     "vòng 6.1 xác nhận"),
    ("hi", "hy", "PHONE_H", [], "PHONE_I", [], "TONE_NGANG", "v11 fixture mới"),
    ("hỉ", "hỷ", "PHONE_H", [], "PHONE_I", [], "TONE_HOI", "v11 fixture mới"),
    ("kỉ", "kỷ", "PHONE_K", [], "PHONE_I", [], "TONE_HOI", "v11 fixture mới"),
    ("li", "ly", "PHONE_L", [], "PHONE_I", [], "TONE_NGANG", "v11 fixture mới"),
    ("mì", "mỳ", "PHONE_M", [], "PHONE_I", [], "TONE_HUYEN", "v11 fixture mới"),
    ("tí", "tý", "PHONE_T", [], "PHONE_I", [], "TONE_SAC", "v11 fixture mới"),
    ("hí", "hý", "PHONE_H", [], "PHONE_I", [], "TONE_SAC", "v11 fixture mới"),
    ("kị", "kỵ", "PHONE_K", [], "PHONE_I", [], "TONE_NANG", "v11 fixture mới"),
    ("lì", "lỳ", "PHONE_L", [], "PHONE_I", [], "TONE_HUYEN", "v11 fixture mới"),
    ("quì", "quỳ", "PHONE_K", ["PHONE_W"], "PHONE_I", [], "TONE_HUYEN",
     "v11 fixture mới"),
    ("quí", "quý", "PHONE_K", ["PHONE_W"], "PHONE_I", [], "TONE_SAC",
     "v11 fixture mới"),
    ("quĩ", "quỹ", "PHONE_K", ["PHONE_W"], "PHONE_I", [], "TONE_NGA",
     "v11 fixture mới"),
    ("quỉ", "quỷ", "PHONE_K", ["PHONE_W"], "PHONE_I", [], "TONE_HOI",
     "v11 fixture mới"),
    ("ti", "ty", "PHONE_T", [], "PHONE_I", [], "TONE_NGANG", "v11 fixture mới"),
    ("tì", "tỳ", "PHONE_T", [], "PHONE_I", [], "TONE_HUYEN", "v11 fixture mới"),
    ("tị", "tỵ", "PHONE_T", [], "PHONE_I", [], "TONE_NANG", "v11 fixture mới"),
    ("ì", "ỳ", None, [], "PHONE_I", [], "TONE_HUYEN", "v11 fixture mới"),
    ("ỉ", "ỷ", None, [], "PHONE_I", [], "TONE_HOI", "v11 fixture mới"),
    # QD57-2026-10-02: 19 cặp duyệt MỚI (reviewer phán quyết, chủ dự án chấp thuận
    # phạm vi 02/10) — chế độ đọc VI-word nguyên dạng (chính âm tiết đã viết, giữ
    # thanh), KHÔNG áp cho tên chữ/spelling/viết tắt/phát âm nguyên ngữ tên ngoại.
    # Expected record pin: 02_data/collision/qd57/19_fixture_moi.json (38/38 khớp).
    ("hì", "hỳ", "PHONE_H", [], "PHONE_I", [], "TONE_HUYEN", "QD57-2026-10-02"),
    ("i", "y", None, [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("iêng", "yêng", None, [], "PHONE_I_SCHWA", ["PHONE_NG"], "TONE_NGANG",
     "QD57-2026-10-02"),
    ("ki", "ky", "PHONE_K", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("lị", "lỵ", "PHONE_L", [], "PHONE_I", [], "TONE_NANG", "QD57-2026-10-02"),
    ("mi", "my", "PHONE_M", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("mỉ", "mỷ", "PHONE_M", [], "PHONE_I", [], "TONE_HOI", "QD57-2026-10-02"),
    ("mị", "mỵ", "PHONE_M", [], "PHONE_I", [], "TONE_NANG", "QD57-2026-10-02"),
    ("ni", "ny", "PHONE_N", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("rì", "rỳ", "PHONE_R_VI", [], "PHONE_I", [], "TONE_HUYEN", "QD57-2026-10-02"),
    ("si", "sy", "PHONE_S_RETRO", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("sì", "sỳ", "PHONE_S_RETRO", [], "PHONE_I", [], "TONE_HUYEN", "QD57-2026-10-02"),
    ("thi", "thy", "PHONE_TH", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("thì", "thỳ", "PHONE_TH", [], "PHONE_I", [], "TONE_HUYEN", "QD57-2026-10-02"),
    ("vi", "vy", "PHONE_V", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("vĩ", "vỹ", "PHONE_V", [], "PHONE_I", [], "TONE_NGA", "QD57-2026-10-02"),
    ("vị", "vỵ", "PHONE_V", [], "PHONE_I", [], "TONE_NANG", "QD57-2026-10-02"),
    ("xi", "xy", "PHONE_S", [], "PHONE_I", [], "TONE_NGANG", "QD57-2026-10-02"),
    ("í", "ý", None, [], "PHONE_I", [], "TONE_SAC", "QD57-2026-10-02"),
]


def explain_exact_fixture(spellings, tone):
    """Duyệt hẹp ở MỨC NHÓM (vòng 6.3, reviewer v11 §3): trả 'EXACT_FIXTURE' khi
    TẤT CẢ điều kiện thỏa — ngược lại None (nhóm vẫn là proposal):
      1. tập spelling của nhóm (NFC-lower, GIỮ DẤU THANH) == tập 2 từ của MỘT
         fixture — nhóm chứa thêm thành viên nào thì KHÔNG duyệt;
      2. tone của nhóm == tone của fixture (so exact — không strip rồi suy rộng);
      3. record parse của TỪNG từ khớp expected record viết tường minh.
    Phạm vi đọc: chữ VI đầy đủ dấu (route/mode do tầng 1 cấp) — approval KHÔNG áp
    cho đọc chữ cái i/y, đọc EN, hay suy ra từ cặp khác thanh (probe reviewer:
    'ký/kĩ' không được 'kí/ký' che; NFD phải normalize về NFC rồi mới so)."""
    import unicodedata as _U
    from . import vi_rules as R
    norm = sorted(_U.normalize("NFC", s).lower() for s in spellings)
    if len(norm) != 2:
        return None
    for w1, w2, on, gl, nuc, coda, t, _origin in APPROVED_EXACT_FIXTURES:
        if norm != sorted([_U.normalize("NFC", w1).lower(),
                           _U.normalize("NFC", w2).lower()]):
            continue
        if tone != t:
            continue
        for w in (w1, w2):
            sk, ti = R.strip_tone(w)
            p = R.parse_skeleton(sk)
            if p is None or R.TONE_BY_INDEX[ti] != tone:
                return None
            on_ids, gl_ids, nuc_id, coda_id, _flags = R.record_parts(*p)
            if list(on_ids) != ([on] if on else []) or list(gl_ids) != list(gl):
                return None
            if nuc_id != nuc or coda_id != (coda[0] if coda else None):
                return None
        return "EXACT_FIXTURE"
    return None


def approval_policy_hash():
    """R12-01 (reviewer v12 §5): pin HÀNH VI policy approval exact fixture —
    inventory_contract_hash và domain_config_hash KHÔNG phủ catalog này. Hash gộp:
    (1) điều kiện scope của policy; (2) nguồn quyết định (phân biệt ràng buộc v11
    với encoding v12); (3) catalog RUNTIME đầy đủ (cặp + expected record + origin
    — mutation in-memory bỏ/thêm/đổi fixture → hash đổi); (4) source hash helper.
    Deterministic khi policy giữ nguyên."""
    import inspect
    payload = {
        "policy": "EXACT_FIXTURE v1 — duyệt ở MỨC NHÓM: tập spelling (NFC-lower "
                  "GIỮ dấu thanh) == tập 2 từ của đúng 1 fixture; tone so exact; "
                  "record parse từng từ khớp expected; nhóm superset/sai tone/"
                  "ngoài allowlist không được duyệt; chế độ đọc VI (route/mode do "
                  "tầng 1 cấp) — không áp cho đọc chữ cái/EN",
        "decision_source": "ràng buộc giữ đối lập + phê duyệt fixture: quyết "
                           "reviewer v11 (2026-10-02, quyet_dinh_95_nhom_v11.csv / "
                           "approved_exact_fixtures_v11.json — 8 cặp vòng 6.1 + 18 "
                           "cặp mới §5.2); tên ID/kỹ thuật duyệt mức nhóm: lựa chọn "
                           "tác giả v12, được duyệt có điều kiện ở hậu kiểm v12 §3; "
                           "+19 cặp duyệt mới: QD57-2026-10-02 (reviewer phán quyết "
                           "per-group, hồ sơ pin 02_data/collision/qd57/) — chủ dự "
                           "án chấp thuận phạm vi 02/10/2026; scope VI-word nguyên "
                           "dạng, không tên chữ/viết tắt/tên ngoại nguyên ngữ",
        "fixtures": [list(f) for f in APPROVED_EXACT_FIXTURES],
        "helper_source_sha256": hashlib.sha256(
            inspect.getsource(explain_exact_fixture).encode("utf-8")).hexdigest(),
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        .encode("utf-8")).hexdigest()


def load():
    rows = []
    raw = TSV.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise AssertionError("TSV không được có BOM (schema §8)")
    lines = raw.decode("utf-8").splitlines()
    for ln in lines:
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = ln.split("\t")
        assert len(parts) == 5, f"dòng sai định dạng (cần 5 cột): {ln!r}"
        sid, loai, uni, desc, notes = (p.strip() for p in parts)
        assert all(p != "" for p in (sid, loai, uni, desc)), \
            f"4 cột đầu bắt buộc khác rỗng: {ln!r}"
        for p in parts:
            assert not any(unicodedata.category(ch).startswith("C")
                           for ch in p), f"ký tự điều khiển trong field: {ln!r}"
        rows.append({
            "id": unicodedata.normalize("NFC", sid),
            "loai": loai,
            "unicode": unicodedata.normalize("NFC", uni),
            "desc": desc,
            "notes": unicodedata.normalize("NFC", notes),
        })
    return rows


def sha256_of_tsv():
    return hashlib.sha256(TSV.read_bytes()).hexdigest()


def contract_hash():
    """Fingerprint behavior của A1 (schema §7): TSV raw bytes + 3 bảng machine semantics.

    inventory_hash một mình KHÔNG đủ — đổi REQUIRED_CONTRASTS/SHARED_UNICODE_REPR/
    MERGE_RULES mà giữ nguyên TSV vẫn phải đổi hash. Serialization canonical: JSON
    sort_keys, ensure_ascii=False, separator chặt.
    """
    payload = {
        "tsv_sha256": sha256_of_tsv(),
        "required_contrasts": REQUIRED_CONTRASTS,
        "shared_unicode_repr": SHARED_UNICODE_REPR,
        "merge_rules": MERGE_RULES,
    }
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# ------------------------------------------------------- matcher MERGE_RULES (điều 7)
# VÒNG 4 (F04): matcher áp lên PARSED PARTS (onset, glide_letter, form, tail) —
# mỗi kind chỉ đụng thành phần được khai, biên thành phần giữ nguyên theo cấu trúc
# (không còn global replace + hoán vị trên skeleton để vượt giao thoa c/ch/c/k).
# VÒNG 5 (V5-04): áp matcher KHÔNG còn đủ để hợp thức hóa — mỗi bước áp trong
# _explain_parts phải (a) biến đổi được, (b) parts sau biến đổi là chính tả HỢP LỆ
# (render canonical → parse ngược ra đúng parts), (c) BẢO TOÀN record phát âm
# (record4 trước == sau). Nhờ (c): cao/cau bị CHẶN (COND_NUC đổi nucleus khi tail
# u sau a), kue/que bị CHẶN (GLIDE_FORMS['ue']=E ≠ BASE_NUC[e]=OPEN_E ở nhánh qu).
def _record4(parts):
    """parts → (onset_ids, glide_ids, nucleus, coda) hoặc None nếu composite không
    khai báo (parts không thể là chính tả thật)."""
    from . import vi_rules as R
    try:
        on, gl, nuc, coda, _ = R.record_parts(*parts)
    except AssertionError:
        return None
    return (tuple(on), tuple(gl), nuc, coda)


def _wellformed(parts):
    """parts là một chính tả HỢP LỆ không: render canonical (NGANG) → parse ngược
    phải ra đúng parts. Chặn nối qua trạng thái trung gian không phải chính tả
    (vd 'kua' giữa qua/koa — vòng 5)."""
    from . import vi_rules as R
    spelling = R.render_parts(*parts, "TONE_NGANG")
    return R.parse_skeleton(spelling) == parts


def _apply_matcher(parts, matcher):
    kind, alt = matcher["kind"], matcher["alt"]
    on, gl, form, tail = parts
    if kind == "role_alt":
        role = matcher["role"]
        keys = sorted(alt, key=len, reverse=True)
        if role == "onset":
            for k in keys:
                if on == k:
                    return (alt[k], gl, form, tail)
        elif role == "glide":
            for k in keys:
                if gl == k:
                    return (on, alt[k], form, tail)
        elif role == "form":
            for k in keys:
                if form == k:
                    return (on, gl, alt[k], tail)
        elif role == "tail":
            for k in keys:
                if tail == k:
                    return (on, gl, form, alt[k])
        else:
            raise ValueError(f"matcher role lạ: {role!r}")
        return parts
    if kind == "composite_alt":          # composite glide+form — chỉ khi CÓ glide
        if not gl:
            return parts
        for k in sorted(alt, key=len, reverse=True):
            if gl + form == k:
                new = alt[k]
                return (on, new[0], new[1:], tail)
        return parts
    if kind == "onset_glide_alt":        # cấu trúc onset:glide — "k:u" → ["qu",""]
        key = f"{on}:{gl}"
        if key in alt:
            o2, g2 = alt[key]
            return (o2, g2, form, tail)
        return parts
    if kind == "rhyme_alt":              # vần+coda cùng lúc: "a:ch" → "e:c"
        key = form + ":" + tail
        for k in sorted(alt, key=len, reverse=True):
            if key == k:
                f2, t2 = alt[k].split(":")
                return (on, gl, f2, t2)
        return parts
    raise ValueError(f"matcher kind lạ: {kind!r}")


def _parse_parts(skeletons):
    """skeleton → list parsed parts; None nếu có thành phần không parse được."""
    from . import vi_rules as R
    parts = []
    for s in skeletons:
        p = R.parse_skeleton(s)
        if p is None:
            return None
        parts.append(p)
    return parts


def _canonicalize(parts, matchers):
    """Canonical hóa MỘT bộ parts bằng worklist XÁC ĐỊNH (V5-04): quét catalog theo
    thứ tự khai báo, áp rule ĐẦU TIÊN mà bước áp hợp lệ, rồi quét lại từ đầu tới
    khi không còn rule nào áp được (fixpoint — KHÔNG hoán vị, KHÔNG backtracking).
    Bước áp hợp lệ = (a) biến đổi được gì, (b) _wellformed, (c) _record4 bảo toàn.
    Mọi matcher đều một chiều (key→value) nên fixpoint có hạn. Trả (parts, set rule)."""
    t, applied = parts, set()
    for _ in range(10):                       # cap phòng thủ; fixpoint thực tế ≤ 4 bước
        changed = False
        for rid, m in matchers:
            t2 = _apply_matcher(t, m)
            if t2 == t:
                continue                      # (a) rule không đụng parts này
            if not _wellformed(t2) or _record4(t2) != _record4(t):
                continue                      # (b)/(c) bước không hợp lệ — bỏ qua
            t, applied, changed = t2, applied | {rid}, True
            break                             # quét lại từ đầu (ưu tiên index thấp)
        if not changed:
            return t, applied
    return t, applied


def _explain_parts(parts, rules):
    """'Trọn vẹn' = mọi parts canonical hóa về MỘT normal form bằng _canonicalize
    (worklist theo thứ tự catalog — V5-04). Hợp lệ → tuple(rule_id ĐÃ ÁP THỰC SỰ
    theo trace gộp); thất bại → None. Mọi parts ĐÃ giống nhau từ đầu → ("IDENTITY",)
    — hai chính tả cùng parse, không cần rule merge (chuyện chọn chính tả chuẩn thuộc
    renderer, không thuộc điều 7). Không bao giờ che khác biệt ngoài subs (lí/lín)."""
    from . import vi_rules as R
    if len(set(parts)) == 1:
        return ("IDENTITY",)
    matchers = [(r["rule_id"], r["matcher"]) for r in rules if r.get("matcher")]
    if any(_record4(p) is None for p in parts):
        return None
    canon, applied_all = set(), set()
    for p in parts:
        t, applied = _canonicalize(p, matchers)
        canon.add(t)
        applied_all |= applied
    if len(canon) == 1 and applied_all:
        return tuple(sorted(applied_all))
    return None


def explain_collision(skeletons, rules=None):
    """Nhóm collision (list skeleton đã strip dấu) được giải thích trọn vẹn không?
    → tuple(rule_id) ("IDENTITY" nếu mọi parts vốn giống) hoặc None. Skeleton
    KHÔNG parse được → None (không đoán). Full catalog (mọi rule) — dùng
    explain_collision_tiered cho phân tầng duyệt."""
    parts = _parse_parts(skeletons)
    if parts is None:
        return None
    rules = rules if rules is not None else MERGE_RULES
    return _explain_parts(parts, rules)


def explain_collision_tiered(skeletons):
    """Phân tầng lời giải (reviewer vòng 4 §5.4, mở rộng vòng 5): trả
    (tier, tuple(rule_id)); tier ∈ {"identity", "approved", "proposal",
    "unexplained"}. "identity" = mọi parts vốn giống nhau (không cần rule, benign).
    Thử CHỈ rule approved trước, rồi toàn bộ proposal — không tự nâng proposal
    thành approved vì tìm được đường canonicalization."""
    parts = _parse_parts(skeletons)
    if parts is None:
        return "unexplained", None
    if len(set(parts)) == 1:
        return "identity", ()
    approved = [r for r in MERGE_RULES if r.get("approved")]
    if approved:
        r = _explain_parts(parts, approved)
        if r:
            return "approved", r
    r = _explain_parts(parts, MERGE_RULES)
    if r:
        return "proposal", r
    return "unexplained", None


def audit(rows, generator_hook=None):
    errs, warns = [], []

    # (1) ID unique
    ids = [r["id"] for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errs.append(f"[1] semantic_id trùng: {sorted(dup)}")

    # (2) trùng unicode repr → FAIL trừ khi nhóm thực tế ⊆ một nhóm SHARED_UNICODE_REPR
    by_uni = {}
    for r in rows:
        by_uni.setdefault(r["unicode"], []).append(r["id"])
    all_ids = set(ids)
    for g in SHARED_UNICODE_REPR:
        gids = g["ids"]
        if len(set(gids)) < 2:
            errs.append(f"[2] nhóm allowlist {g['unicode']!r} cần ≥2 id phân biệt: {gids}")
        for gid in gids:
            if gid not in all_ids:
                errs.append(f"[2] allowlist nhắc id không tồn tại: {gid!r}")
    for uni, sids in by_uni.items():
        if len(sids) > 1:
            covered = any(set(sids) <= set(g["ids"]) and g["unicode"] == uni
                          for g in SHARED_UNICODE_REPR)
            if not covered:
                errs.append(f"[2] unicode {uni!r} dùng bởi {len(sids)} ID {sorted(sids)} "
                            f"mà nhóm không nằm trọn trong SHARED_UNICODE_REPR")

    # (3) mọi ID thuộc lớp hợp lệ + (4) tách lớp đúng vị trí + F08: namespace khép
    NAMESPACE = {"segment": ("PHONE_",), "prosody": ("TONE_", "STRESS_"),
                 "control": ("PUNCT_",)}
    for r in rows:
        if r["loai"] not in LOAI_OK:
            errs.append(f"[3] {r['id']}: loai lạ {r['loai']!r}")
            continue
        # F08 (vòng 4): prefix phải thuộc namespace của loai — prefix lạ bị BÁC
        # (trước đây chỉ kiểm "nếu bắt đầu bằng X thì loai phải là Y", chưa bác
        # prefix lạ kiểu UNRECOGNIZED_ID — probe reviewer)
        if not r["id"].startswith(NAMESPACE[r["loai"]]):
            errs.append(f"[3] {r['id']}: prefix ngoài namespace loai={r['loai']!r} "
                        f"(cho phép {NAMESPACE[r['loai']]})")
        if r["id"].startswith(("TONE_", "STRESS_")) and r["loai"] != "prosody":
            errs.append(f"[4] {r['id']} là prosody nhưng loai={r['loai']}")
        if r["id"].startswith("PUNCT_") and r["loai"] != "control":
            errs.append(f"[4] {r['id']} là control nhưng loai={r['loai']}")
        if r["id"].startswith("PHONE_") and r["loai"] != "segment":
            errs.append(f"[4] {r['id']} là segment nhưng loai={r['loai']}")
        # bộ 6 tone + 2 stress phải đủ
    missing_tones = TONE_IDS - set(ids)
    if missing_tones:
        errs.append(f"[3] thiếu tone: {sorted(missing_tones)}")
    missing_stress = STRESS_IDS - set(ids)
    if missing_stress:
        errs.append(f"[3] thiếu stress: {sorted(missing_stress)}")
    for need in ("PUNCT_PERIOD", "PUNCT_COMMA", "PUNCT_QUESTION", "PUNCT_EXCLAIM"):
        if need not in ids:
            errs.append(f"[3] thiếu control: {need}")

    # (5) segment KHÔNG chứa code point nhóm Unicode Number (category N) — từng code point
    for r in rows:
        if r["loai"] == "segment":
            bad = sorted({ch for ch in r["unicode"]
                          if unicodedata.category(ch).startswith("N")})
            if bad:
                errs.append(f"[5] segment {r['id']} chứa code point số "
                            f"{bad} trong unicode: {r['unicode']!r}")

    # (6) required_contrasts tồn tại + khác ID — khác unicode KHÔNG là tiêu chí
    # (schema bản 2: 2 ID khác nhau được cùng repr; bảo toàn đối lập qua luật kiểm ở fase B)
    by_id = {r["id"]: r for r in rows}
    for a, b in REQUIRED_CONTRASTS:
        if a not in by_id or b not in by_id:
            errs.append(f"[6] required_contrast thiếu ID: {a} / {b}")
            continue
        if a == b:
            errs.append(f"[6] required_contrast trùng ID: {a}")

    # (7) audit va chạm phát âm (realization-collision) — hook generator (fase B);
    #     khóa gom = chuỗi semantic ID GỒM prosody; nhóm trùng phải khớp MERGE_RULES
    if generator_hook is not None:
        errs.extend(generator_hook(by_id))
    else:
        warns.append("[7] realization-collision — NOT_RUN tại file này; chạy "
                     "01_g2p/collision_audit.py (fase B): hiện hành vòng 6.5 — "
                     "83 nhóm gate = 45 approved (exact fixture: 26 v11 + 19 "
                     "QD57) + 38 excluded_v1 + 0 unresolved → PASS; 0 rule "
                     "approved ở tầng matcher (9 rule đề xuất; MR-ACH-EC "
                     "withdrawn); cặp kiểm: "
                     f"{SYLLABLE_LEVEL_CONTRASTS}")

    return errs, warns


def main():
    rows = load()
    errs, warns = audit(rows)
    n_seg = sum(1 for r in rows if r["loai"] == "segment")
    n_pro = sum(1 for r in rows if r["loai"] == "prosody")
    n_ctl = sum(1 for r in rows if r["loai"] == "control")
    print(f"inventory ham/0.2: {len(rows)} entries "
          f"(segment {n_seg} · prosody {n_pro} · control {n_ctl})")
    print(f"sha256(inventory_ham.tsv) = {sha256_of_tsv()}  (raw bytes — hash artifact)")
    print(f"inventory_contract_hash    = {contract_hash()}  (TSV + 3 bảng semantics)")
    for w in warns:
        print(f"  NOTE  {w}")
    static_errs = [e for e in errs if not e.startswith("[7]")]
    coll_errs = [e for e in errs if e.startswith("[7]")]
    if static_errs:
        print(f"  Static inventory audit (điều 1-6): FAIL — {len(static_errs)} lỗi:")
        for e in static_errs:
            print(f"    {e}")
    else:
        print("  Static inventory audit (điều 1-6): PASS")
    if coll_errs:
        print(f"  Realization-collision audit (điều 7): FAIL — {len(coll_errs)} lỗi")
        for e in coll_errs:
            print(f"    {e}")
    if errs:
        sys.exit(1)


if __name__ == "__main__":
    main()
