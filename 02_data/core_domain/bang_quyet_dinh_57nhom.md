> **[SUPERSEDED 02/10/2026]** Đã bị thay bằng quyết định chính thức QD57-2026-10-02 (hồ sơ pin 02_data/collision/qd57/; áp runtime vòng 6.4 — inventory_schema §10.7). File dưới là bản dự thảo gốc.

# Bảng quyết định tổng hợp 57 nhóm gate pending — **DỰ THẢO per-group, chờ duyệt**

- Ngày: 02/10/2026 (vòng 6.4 — sau hậu kiểm v13; kỹ thuật đã đóng ở v13, giữ nguyên).
- Nguồn: `02_data/collision/dieu7_bao_cao.json` — report trạng thái `PENDING_APPROVAL`, 26 approved + 57 proposal; tần suất đọc trực tiếp từ report, không tính lại.
- Nguyên tắc theo chỉ đạo chủ dự án: quyết **từng nhóm**; cơ sở là bằng chứng chính tả/từ vựng cụ thể — KHÔNG duyệt đồng âm chỉ từ quyết định A1, coda cùng loại hoặc output parser trùng nhau. Không tự phục hồi dấu (token thiếu dấu → miền fold theo contract đã duyệt). Không đổi route tầng 1. Từ mượn/token ngoại xét theo từng token, không loại đồng loạt.
- Trạng thái: **đề xuất** — chưa áp approval hay tier out_of_scope_v1 vào audit cho tới khi bảng được duyệt; gửi reviewer quyết một lượt, không kèm gói kiểm code mới.

## Tổng hợp

| Đề xuất | Số nhóm | Ý nghĩa |
|---|---:|---|
| DUYỆT_HẸP | 21 | hai chính tả trong nhóm đọc như nhau là ĐÚNG — duyệt hẹp theo cặp, scope chỉ hai chính tả nêu tên, không mở thành rule rộng |
| NGOÀI_PHẠM_VI_V1 | 36 | không phải cặp đồng âm cần quyết ở gate (một phía là token lỗi/thiếu dấu/ngoại) — token xử theo contract đã duyệt (fold/spell/route), không tuyên bố gì về chính tả chuẩn |
| GIỮ_PHÂN_BIỆT | 0 | không có nhóm nào cần đổi biểu diễn master — ca phá đối lớp duy nhất (ach/ec) đã xử lý ở vòng 6.3 bằng PHONE_OPEN_E_PREVELAR |

## A. DUYỆT_HẸP (21 nhóm)

- **chếc/chếch** (`MR-CODA-CH-C`) — tần suất: chếc:3, chếch:11
  - Cơ sở: cả hai từ thật khác nghĩa nhưng ĐỒNG ÂM thật: "chếch" (nghiêng), "chếc" (hai chếc chén) — coda ch đọc /k̟/ như c (quyết A1 đã duyệt + phiên âm chuẩn final-ch); đồng âm ở mức âm tiết là đúng
- **hì/hỳ** (`MR-I-Y`) — tần suất: hì:18, hỳ:3
  - Cơ sở: h thuộc danh sách viết y (hỷ, hy sinh); "hì" (hì hì) và "hỳ" đều chính tả hợp lệ, cùng đọc /hi/ huyền
- **i/y** (`MR-I-Y`) — tần suất: i:3959, y:7234
  - Cơ sở: cả hai là chữ/từ thật cùng đọc /i/ (y hoặc i đầu âm tiết theo quy tắc chính tả) — cặp gốc của danh sách fixture đã duyệt vòng 6.3
- **iên/yên** (`MR-I-Y`) — tần suất: iên:3, yên:3469
  - Cơ sở: hai chính tả của cùng vần /iəŋ/ theo quy tắc vị trí (đầu tiết viết y: yên/yến; sau phụ âm viết i: điền/thiên)
- **iểu/yểu** (`MR-I-Y`) — tần suất: iểu:2, yểu:32
  - Cơ sở: vần /iəw/ là một vần chuẩn duy nhất (kiểu, tiểu, yểu điệu đều từ thật); "iểu" đứng riêng tần suất thấp nhưng cùng vần hợp lệ — duyệt ở mức cách đọc; nếu reviewer thấy chưa đủ, nhóm này có thể rút sang ngoài phạm vi mà không ảnh hưởng phần còn lại
- **ki/ky** (`MR-I-Y`) — tần suất: ki:663, ky:79
  - Cơ sở: k thuộc danh sách viết y (ký/kỹ); gold đã pin fixture kí=ký được duyệt vòng 6.3 — cặp này cùng bản chất
- **lị/lỵ** (`MR-I-Y`) — tần suất: lị:19, lỵ:109
  - Cơ sở: cả hai dùng thật ("ma lị" — chính tả lưu hành cả hai dạng lị/lỵ); cùng đọc /li/ nặng — biến thể chính tả cùng từ
- **mi/my** (`MR-I-Y`) — tần suất: mi:940, my:711
  - Cơ sở: m thuộc danh sách viết y (mỹ, mỵ); cả hai cùng đọc /mi/
- **mỉ/mỷ** (`MR-I-Y`) — tần suất: mỉ:166, mỷ:5
  - Cơ sở: m thuộc danh sách viết y; "mỷ" biến thể chính tả của "mỉ"
- **mị/mỵ** (`MR-I-Y`) — tần suất: mị:81, mỵ:11
  - Cơ sở: m thuộc danh sách viết y; cả hai dùng thật ("Mỵ" tên riêng Hán-Việt: Mỵ Nương; "mị" từ thật phổ biến); cùng đọc /mi/ nặng
- **ni/ny** (`MR-I-Y`) — tần suất: ni:206, ny:69
  - Cơ sở: cả hai dùng thật trong văn viết hiện đại: "ny" tiếng lóng phổ biến (người yêu), "ni" dùng trong tên riêng; cùng đọc /ni/ — chấp nhận theo cách đọc, không tuyên bố "ny" là chính tả chuẩn
- **si/sy** (`MR-I-Y`) — tần suất: si:207, sy:8
  - Cơ sở: s thuộc danh sách viết y (sĩ/sỹ); cùng đọc /si/
- **sì/sỳ** (`MR-I-Y`) — tần suất: sì:15, sỳ:2
  - Cơ sở: cả hai thật: "sì" (sì hơi), "sỳ" ("sỳ sụp" từ tượng thanh); cùng đọc /si/ huyền
- **thi/thy** (`MR-I-Y`) — tần suất: thi:15541, thy:134
  - Cơ sở: "thy" chủ yếu là tên riêng phổ biến (Thy), đọc /thi/ như "thi"; quyết ở mức cách đọc âm tiết, không xác minh nghĩa từng tên
- **tíc/tích** (`MR-CODA-CH-C`) — tần suất: tíc:7, tích:14352
  - Cơ sở: cả hai từ thật: "tíc" (tíc tách), "tích" (lịch sử); đồng âm /tik/ thật cùng cơ sở coda ch/c trên
- **vi/vy** (`MR-I-Y`) — tần suất: vi:7214, vy:410
  - Cơ sở: v thuộc danh sách viết y; cả hai thật ("vi" (vi khuẩn, vi tế), "vy" tên riêng phổ biến); cùng đọc /vi/
- **vĩ/vỹ** (`MR-I-Y`) — tần suất: vĩ:1228, vỹ:67
  - Cơ sở: cả hai cùng dùng thật cho một từ: "vĩ đại"/"vỹ đại" đều được chữ viết chấp nhận — biến thể chính tả chuẩn
- **vị/vỵ** (`MR-I-Y`) — tần suất: vị:19496, vỵ:4
  - Cơ sở: v thuộc danh sách viết y; "vị" rất phổ biến; "vỵ" chính tả hợp lệ theo quy tắc v+y, cùng đọc /vi/ nặng
- **xi/xy** (`MR-I-Y`) — tần suất: xi:553, xy:128
  - Cơ sở: x thuộc danh sách viết y; "xy" chuẩn trong từ Hán-Việt (xy-lô, xy-lanh); cùng đọc /si/
- **í/ý** (`MR-I-Y`) — tần suất: í:26, ý:18681
  - Cơ sở: cả hai thật: "ý" rất phổ biến, "í" ("í ẹo"); cùng đọc /i/ sắc
- **ĩ/ỹ** (`MR-I-Y`) — tần suất: ĩ:47, ỹ:2
  - Cơ sở: cả hai chính tả hợp lệ (ỹ đầu âm tiết), cùng đọc /ĩ/; tần suất thấp nhưng là nguyên âm đơn không có nghĩa riêng cần bảo toàn

## B. NGOÀI_PHẠM_VI_V1 (36 nhóm)

Mỗi nhóm dưới đây có **một phía không phải âm tiết vi cần quyết đồng âm**: dạng thiếu dấu của vần KHÁC (keu=kêu, leu=lêu, teu=têu, thue=thuê, cuới=cưới — lưu ý hai phía của nhóm thường là HAI VẦN KHÁC NHAU, chỉ va nhau vì token thiếu dấu đi vào gate vi), dạng lỗi chính tả, hoặc token ngoại. Xử lý đúng contract: token thiếu dấu → nhánh fold ỦY QUỀN đã duyệt; token ngoại → route, không quyết ở gate vi. KHÔNG tự phục hồi dấu ở tầng gate.

- **beo/beu** (`MR-CODA-O-U`) — tần suất: beo:23, beu:3
  - Lý do: "beu" không phải vần chuẩn; "beo" nghi "béo" thiếu dấu (miền fold) — không quyết đồng âm, token xử theo contract
- **bio/biu** (`MR-CODA-O-U`) — tần suất: bio:57, biu:2
  - Lý do: "bio" token ngoại (tiền tố quốc tế bio-); "biu" không phải vần chuẩn — token ngoại xử theo route/contract, không quyết ở gate
- **bâo/bâu** (`MR-CODA-O-U`) — tần suất: bâo:2, bâu:8
  - Lý do: "bâu" vần chuẩn (âu); "bâo" không phải vần chuẩn — nghi lỗi gõ; token xử theo contract
- **cue/quê** (`MR-ONSET-C-K+MR-QU-K-GLIDE+MR-UE-UÊ`) — tần suất: cue:17, quê:2174
  - Lý do: "cue" token ngoại (tiếng anh) — KHÔNG phải "quê" thiếu dấu (thiếu dấu của "quê" là "que"); token ngoại xử theo route/contract, "quê" đọc chuẩn không bị ảnh hưởng
- **cuới/quới** (`MR-ONSET-C-K+MR-QU-K-GLIDE`) — tần suất: cuới:2, quới:21
  - Lý do: "quới" là từ thật ("trời quới" — cách viết phương ngữ của "quý") và đồng âm với "cưới"; "cuới" là "cưới" thiếu dấu — thuộc miền fold đã duyệt; không tự phục hồi dấu ở gate
- **cấo/cấu** (`MR-CODA-O-U+MR-ONSET-C-K`) — tần suất: cấo:2, cấu:3143
  - Lý do: "cấu" rất phổ biến; "cấo" không phải vần chuẩn — nghi lỗi gõ của "cấu"; token xử theo contract
- **deo/deu** (`MR-CODA-O-U`) — tần suất: deo:7, deu:7
  - Lý do: "deu" không phải vần chuẩn; "deo" nghi dạng thiếu dấu/token lỗi — cả hai phía không đủ bằng chứng lexical; token xử theo contract
- **di/dy** (`MR-I-Y`) — tần suất: di:6655, dy:5
  - Lý do: "dy" không theo quy tắc chính tả (sau d viết i, d không thuộc danh sách y) — nghi token lỗi/ngoại; phía "di" đọc chuẩn không bị ảnh hưởng; token xử theo contract fold/spell
- **dio/diu** (`MR-CODA-O-U`) — tần suất: dio:16, diu:4
  - Lý do: cả hai không phải vần chuẩn ("diu" nghi "dìu" thiếu dấu — miền fold); token xử theo contract
- **eo/eu** (`MR-CODA-O-U`) — tần suất: eo:434, eu:9
  - Lý do: "eo" vần chuẩn; "eu" KHÔNG phải vần chuẩn (vần /ew/ viết "êu") — nghi lỗi/token lạ; không có cặp tối thiểu từ thật nào bị phá
- **hue/huê** (`MR-UE-UÊ`) — tần suất: hue:17, huê:30
  - Lý do: "huê" thật (Huế, tên riêng); "hue" là thiếu dấu hoặc token ngoại (hue = màu sắc tiếng anh) — miền fold/route, không tự phục hồi dấu
- **io/iu** (`MR-CODA-O-U`) — tần suất: io:12, iu:15
  - Lý do: "iu" vần chuẩn (liu ríu); "io" không phải vần chuẩn — nghi lỗi/token lạ; token xử theo contract
- **iêng/yêng** (`MR-I-Y`) — tần suất: iêng:4, yêng:2
  - Lý do: cả hai tần suất rất thấp (4/2) và không có từ thật phổ biến để đối chứng nghĩa; chính tả có thể hợp lệ nhưng duyệt đồng âm ở v1 không cần thiết — token xử theo contract
- **keo/keu** (`MR-CODA-O-U`) — tần suất: keo:257, keu:3
  - Lý do: "keo" thật; "keu" là "kêu" thiếu dấu (ê→e) — thuộc miền fold ĐÃ DUYỆT (nhánh ỦY QUỀN chọn ứng viên), không tự phục hồi dấu ở gate; lưu ý "kêu" /kew/ ≠ "keo" /kɛw/ nên đây KHÔNG phải đồng âm thật
- **leo/leu** (`MR-CODA-O-U`) — tần suất: leo:1009, leu:3
  - Lý do: "leo" thật; "leu" là "lêu" thiếu dấu — miền fold; "lêu" /lew/ ≠ "leo" /lɛw/
- **meo/meu** (`MR-CODA-O-U`) — tần suất: meo:34, meu:2
  - Lý do: "meu" không phải vần chuẩn; "meo" (meo meo) tần suất thấp — không đủ bằng chứng; token xử theo contract
- **mio/miu** (`MR-CODA-O-U`) — tần suất: mio:16, miu:50
  - Lý do: "miu" từ tượng thanh thật (miu miu); "mio" token nghi ngoại/không chuẩn — token xử theo contract
- **neo/neu** (`MR-CODA-O-U`) — tần suất: neo:301, neu:34
  - Lý do: "neo" thật (neo xe); "neu" token ngoại (đức/anh) — token ngoại xử theo route/contract
- **nhí/nhý** (`MR-I-Y`) — tần suất: nhí:328, nhý:5
  - Lý do: "nh" không thuộc danh sách viết y — "nhý" nghi lỗi gõ (của "nhỉ"/"nhị"); không quyết đồng âm, token xử theo contract
- **níc/ních** (`MR-CODA-CH-C`) — tần suất: níc:2, ních:11
  - Lý do: "níc" không có từ thật (tần suất 2, nghi lỗi của "nịch"/"ní"); "ních" thật nhưng duyệt đồng âm cần phía còn lại có bằng chứng — token xử theo contract
- **pio/piu** (`MR-CODA-O-U`) — tần suất: pio:12, piu:4
  - Lý do: "piu" tượng thanh (piu piu); "pio" không phải vần chuẩn — token xử theo contract
- **rio/riu** (`MR-CODA-O-U`) — tần suất: rio:161, riu:15
  - Lý do: "riu" thật (liu ríu); "rio" token ngoại (tên địa danh) — token ngoại xử theo route/contract
- **rì/rỳ** (`MR-I-Y`) — tần suất: rì:28, rỳ:2
  - Lý do: "r" không thuộc danh sách viết y — "rỳ" không có từ thật, nghi lỗi; token xử theo contract
- **río/ríu** (`MR-CODA-O-U`) — tần suất: río:13, ríu:12
  - Lý do: "ríu" thật (chim ríu); "río" không có từ thật — nghi lỗi; token xử theo contract
- **seo/seu** (`MR-CODA-O-U`) — tần suất: seo:1776, seu:4
  - Lý do: "seo" (seo sàng; "sẹo" thiếu dấu) dùng thật; "seu" không phải vần chuẩn — token xử theo contract
- **sio/siu** (`MR-CODA-O-U`) — tần suất: sio:10, siu:32
  - Lý do: cả hai không phải vần chuẩn tiếng Việt ("siu" nghi tiếng lóng/không dấu) — token xử theo contract
- **sue/suê** (`MR-UE-UÊ`) — tần suất: sue:60, suê:8
  - Lý do: "sue" token ngoại (động từ tiếng anh); "suê" tần suất thấp không rõ từ thật — token xử theo contract
- **teo/teu** (`MR-CODA-O-U`) — tần suất: teo:92, teu:21
  - Lý do: "teo" thật (teo giống); "teu" là "têu" thiếu dấu — miền fold; "têu" /tew/ ≠ "teo" /tɛw/
- **thue/thuê** (`MR-UE-UÊ`) — tần suất: thue:17, thuê:3152
  - Lý do: "thuê" rất phổ biến; "thue" là "thuê" thiếu dấu — miền fold đã duyệt, không tự phục hồi dấu ở gate
- **thì/thỳ** (`MR-I-Y`) — tần suất: thì:30608, thỳ:5
  - Lý do: "th" không thuộc danh sách viết y (danh sách: h,k,l,m,s,v,x) — "thỳ" không có từ thật phổ biến, nghi lỗi; token xử theo contract
- **tio/tiu** (`MR-CODA-O-U`) — tần suất: tio:13, tiu:8
  - Lý do: cả hai không phải vần chuẩn tiếng Việt — token xử theo contract
- **tue/tuê** (`MR-UE-UÊ`) — tần suất: tue:6, tuê:2
  - Lý do: "tuê" ("tuê miên") dùng thật nhưng tần suất thấp; "tue" thiếu dấu/token ngoại — token xử theo contract
- **xue/xuê** (`MR-UE-UÊ`) — tần suất: xue:4, xuê:6
  - Lý do: "xuê" tiếng lóng (xui) dùng thật; "xue" thiếu dấu/token ngoại — token xử theo contract
- **xỉ/xỷ** (`MR-I-Y`) — tần suất: xỉ:436, xỷ:2
  - Lý do: "xỷ" không có từ thật phổ biến (tần suất 2) dù x thuộc danh sách — không đủ bằng chứng lexical để duyệt; token xử theo contract
- **âi/ây** (`MR-CODA-I-Y`) — tần suất: âi:2, ây:14
  - Lý do: "âi" không phải vần chuẩn tiếng Việt (tần suất 2, nghi lỗi của "ây"/"ai"); token xử theo contract fold/spell
- **đi/đy** (`MR-I-Y`) — tần suất: đi:38741, đy:3
  - Lý do: "đ" không thuộc danh sách viết y — "đy" là cách viết phương ngôn/không chuẩn của "đi"; thuộc miền fold, token xử theo contract

## Còn mở ngoài bảng (giữ nguyên trạng thái, không chặn)

- `thách/théc`, `cạch/kẹc`: hết collision nhờ ham/0.2 (PHONE_OPEN_E_PREVELAR) nhưng câu hỏi từ vựng/cách đọc vẫn mở — theo hậu kiểm v13 §6, không tính thành approval mới, không đưa ngược lại thành blocker.
- Chính sách phiên âm từ mượn: ngoài phạm vi v1; từng token ngoại trong bảng trên chỉ được ghi nhận là token ngoại (có cơ sở riêng), không tạo tiền lệ "loại mọi từ mượn".
- Token en đi vào gate vi (bio, cue, neu, rio, sue…): vấn đề route tầng 1 — chỉ ghi nhận, không đổi route theo chỉ đạo.

## Cách áp dụng khi bảng được duyệt

1. Áp ledger quyết định **từng nhóm** vào provenance, pin bằng decision hash phủ toàn bộ ledger + scope từng quyết định + source hash helper (nguyên lý R12-01; approval_policy_hash hiện hành `6eee24db48c65299…` giữ nguyên). Mọi rule rộng vẫn `approved=False`.
2. Nhóm NGOÀI_PHẠM_VI_V1 được gate ghi tier riêng (không phải approved — không mở đường cho matcher rộng); nhóm DUYỆT_HẸP ghi quyết duyệt hẹp theo đúng hai chính tả nêu tên.
3. Chạy lại chuỗi đầy đủ (inventory static · 401 test VI · 74 profile · 45 gold-dev · collision_audit); status audit đổi theo kết quả thực tế, không đặt trước. Đồng bộ tài liệu (schema §10, README, reference_diff) rồi mới đóng gói bundle nghiệm thu.
