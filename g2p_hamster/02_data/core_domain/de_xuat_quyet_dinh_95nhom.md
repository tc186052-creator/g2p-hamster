# Kênh quyết định ngôn ngữ — trạng thái sau QD57-2026-10-02 (vòng 6.4 áp, vòng 6.5 đồng bộ renderer)

> **Trạng thái: trình bày LEDGER quyết định của reviewer (QD57-2026-10-02 + v11, đã áp vào runtime) — generator KHÔNG tự kết luận ngôn ngữ theo tên rule (v11 §6.1).**

- Áp dụng: master **ham/0.2** (không đổi); lớp duyệt **EXACT_FIXTURE** 45 cặp (26 v11 + 19 QD57, `approval_policy_hash` pin); **38 nhóm excluded_v1** theo QD57 (ledger `02_data/collision/qd57_scope_exclusions.json`, thành viên máy đọc pin từ đáp án reviewer — R14-01); 10 cặp ach/ec thêm vào `SYLLABLE_LEVEL_CONTRASTS` (v11 §4).
- Kết quả điều 7: 83 nhóm gate = **45 approved** (exact fixture) + **38 excluded_v1** (QD57 — KHÔNG approved) + 0 proposal → **PASS** (exit 0 — scope v1 đã khai trọn bộ 57; excluded ≠ approved).

## 45 nhóm duyệt exact fixture (26 v11 + 19 QD57)

Phạm vi reviewer v11 §3 + QD57: đúng cặp ĐẦY ĐỦ DẤU, đúng tone, record khớp expected; chế độ đọc từ VI nguyên dạng — KHÔNG áp cho tên chữ, spelling, viết tắt, English I/my, phát âm nguyên ngữ tên ngoài; KHÔNG suy rộng sang cặp khác thanh, ya/ia, yê/iê, hay toàn matcher (flag rộng MR-I-Y vẫn False — các probe lịch sử không đại diện cho policy 45 exact hiện hành).

### hi/hy — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: hy[2826], hi[890]
- thành viên không có dấu thanh viết ra: hi, hy (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'hi': “…là ngôi sao hi vọng của em…”
- trace 'hi': “…Hà Say Hi Day một…”
- trace 'hy': “…nhiều khán giả hy vọng cặp đôi…”
- trace 'hy': “…, trong lòng hy vọng cơn ác…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### hì/hỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: hì[18], hỳ[3]
- trace 'hì': “…chuyện với mi hì ?…”
- trace 'hì': “…đồng nghiệp phải hì hục giặt tay…”
- trace 'hỳ': “…ở bản Nà Hỳ ba xuất hiện…”
- trace 'hỳ': “…Không có gì hỳ hỳ .…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### hí/hý — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: hí[53], hý[26]
- trace 'hí': “…Hí Óngtính,ph£ ikhông ?…”
- trace 'hí': “…, Hayagriva cũng hí vang , báo…”
- trace 'hý': “…đi thăm hú hý với các dì…”
- trace 'hý': “…vẽ theo lối hý họa .…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### hỉ/hỷ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: hỷ[77], hỉ[33]
- trace 'hỉ': “…có việc đại hỉ thì vô cùng…”
- trace 'hỉ': “…chữ ngũ hỉ , liền…”
- trace 'hỷ': “…con cũng là hỷ sự ,…”
- trace 'hỷ': “…, nhất hỷ chặn tam tai…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### i/y — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: y[7234], i[3959]
- thành viên không có dấu thanh viết ra: i, y (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'i': “…I did a presentation…”
- trace 'i': “…You and I đều đạt…”
- trace 'y': “…đồng xúc tiến Y tế Singapore (…”
- trace 'y': “…trông gần như y hệt cái cô…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### iêng/yêng — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: iêng[4], yêng[2]
- thành viên không có dấu thanh viết ra: iêng, yêng (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'iêng': “…hộ chiếu của Iêng Xary , cấp…”
- trace 'iêng': “…khám phá nét iêng của các dòng…”
- trace 'yêng': “…Các yêng hùng trả đũa…”
- trace 'yêng': “…lại nổi máu yêng hung nữa rồi…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### ki/ky — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ki[663], ky[79]
- thành viên không có dấu thanh viết ra: ki, ky (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'ki': “…- Song Joong Ki trong khuôn khổ…”
- trace 'ki': “…cạnh Song Joong Ki , Kang Ha…”
- trace 'ky': “…những người phải ky cóp mới đủ…”
- trace 'ky': “…Dang ky nguyen vong xet…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### kì/kỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: kỳ[18278], kì[1599]
- trace 'kì': “…cạnh bàn thắng kì vọng ( một phẩy năm bốn…”
- trace 'kì': “…đang tham dự kì thi Olympic Toán…”
- trace 'kỳ': “…êm xê Kỳ Duyên gợi cảm…”
- trace 'kỳ': “…ảnh , êm xê Kỳ Duyên hội ngộ…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### kí/ký — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ký[8964], kí[471]
- trace 'kí': “…quyết định ấn kí và công bố…”
- trace 'kí': “…Em bé đăng kí học mẹ cũng…”
- trace 'ký': “…mới đây đã ký văn bản về…”
- trace 'ký': “…, Ban Thư ký Hội Liên hiệp…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### kĩ/kỹ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: kỹ[6588], kĩ[646]
- trace 'kĩ': “…- địa kĩ thuật hệ khí…”
- trace 'kĩ': “…tập trung vào kĩ năng của bạn…”
- trace 'kỹ': “…trình Hướng dẫn Kỹ năng của Intel…”
- trace 'kỹ': “…cho hàng trăm kỹ năng bằng ngôn…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### kỉ/kỷ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: kỷ[5644], kỉ[502]
- trace 'kỉ': “…nhạc đường phố kỉ niệm ngày truyền…”
- trace 'kỉ': “…, phá vỡ kỉ lục về số…”
- trace 'kỷ': “…trong năm thập kỷ tiếp theo và…”
- trace 'kỷ': “…Từ thế kỷ mười tám , đạo…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### kị/kỵ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: kỵ[469], kị[112]
- trace 'kị': “…là đối thủ kị giơ của Việt…”
- trace 'kị': “…Những điều cấm kị khi dùng lò…”
- trace 'kỵ': “…ghét , đố kỵ ?…”
- trace 'kỵ': “…ki lô mét từ Đồng Kỵ đến khu lưu…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### li/ly — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ly[2508], li[540]
- thành viên không có dấu thanh viết ra: li, ly (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'li': “…is blocked and Li gets a step…”
- trace 'li': “…luật Bec nu li cho một ống…”
- trace 'ly': “…cho mình một ly trà trái cây…”
- trace 'ly': “…trước mặt là ly whisky sóng sánh…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### lì/lỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: lì[118], lỳ[25]
- trace 'lì': “…tận nơi trao lì xì và chúc…”
- trace 'lì': “…dai dẳng , lì đòn hơn và…”
- trace 'lỳ': “…đường nhựa phẳng lỳ , đột nhiên…”
- trace 'lỳ': “…thuộc dạng vua lỳ , giải thích…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### lí/lý — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: lý[25497], lí[801]
- trace 'lí': “…gần đây vì lí do sức khỏe…”
- trace 'lí': “…cũng khá hợp lí , chỉ cần…”
- trace 'lý': “…của ba trăm hai mươi đại lý từ bốn mươi chín tỉnh…”
- trace 'lý': “…danh chín mươi sáu đại lý xuất sắc với…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### lị/lỵ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: lỵ[109], lị[19]
- trace 'lị': “…trà ổi xá lị tươi và Trà…”
- trace 'lị': “…có việc gì lị dị lại khổ…”
- trace 'lỵ': “…Huyện lỵ tại trấn Tường…”
- trace 'lỵ': “…, chứng kiết lỵ , bệnh phong…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### mi/my — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: mi[940], my[711]
- thành viên không có dấu thanh viết ra: mi, my (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'mi': “…xếch , đẩy mi mắt dưới lên…”
- trace 'mi': “…: áo sơ mi và chân váy…”
- trace 'my': “…tốt , Hoàng My phải theo chế…”
- trace 'my': “…Rollout ( My Business )…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### mì/mỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: mì[770], mỳ[169]
- trace 'mì': “…một ổ bánh mì dài , rỗng…”
- trace 'mì': “…Lúa mì là từ Kansas…”
- trace 'mỳ': “…muốn lại ăn mỳ Ý tối nay…”
- trace 'mỳ': “…cơm và bánh mỳ .…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### mĩ/mỹ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: mỹ[14936], mĩ[193]
- trace 'mĩ': “…vẽ đẹp của Mĩ thuật dân tộc…”
- trace 'mĩ': “…bảo tồn nền mĩ thuật đậm đà…”
- trace 'mỹ': “…Việt Nam tại Mỹ tăng liên tiếp…”
- trace 'mỹ': “…nhất ở châu Mỹ lúc đó .…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### mỉ/mỷ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: mỉ[166], mỷ[5]
- trace 'mỉ': “…ghi chép tỉ mỉ không ngừng nghỉ…”
- trace 'mỉ': “…nghiên cứu tỉ mỉ , nhưng kết…”
- trace 'mỷ': “…là sự tỷ mỷ , không bỏ…”
- trace 'mỷ': “…bừa nên chị Mỷ đem trâu xuống…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### mị/mỵ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: mị[81], mỵ[11]
- trace 'mị': “…Tề mị hiệp phu nội…”
- trace 'mị': “…dịu dàng thùy mị hơn chút nào…”
- trace 'mỵ': “…Ông Mỵ cho biết ,…”
- trace 'mỵ': “…gái vua là Mỵ Châu lại cùng…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### ni/ny — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ni[206], ny[69]
- thành viên không có dấu thanh viết ra: ni, ny (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'ni': “…đồng Chăm Bà ni và Bà Chăm…”
- trace 'ni': “…Ngô Diễm Ni hai mươi chín tuổi ,…”
- trace 'ny': “…nhận hai gói ny - lông nuốt…”
- trace 'ny': “…Nguyễn , vai Ny cũng là một…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### qui/quy — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: quy[13465], qui[265]
- thành viên không có dấu thanh viết ra: qui, quy (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'qui': “…dự án có qui mô lớn ,…”
- trace 'qui': “…nước với việc qui hoạch vùng chuyên…”
- trace 'quy': “…yêu cầu cấp quy chế tiểu bang…”
- trace 'quy': “…Chính phủ cũng quy định , sẽ…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### quì/quỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: quỳ[208], quì[3]
- trace 'quì': “…Diễn lúc ở Quì Lăng , lúc…”
- trace 'quì': “…Argentina đã quì gối trước Ả…”
- trace 'quỳ': “…sát cửa nhà quỳ , một đêm…”
- trace 'quỳ': “…người đàn bà quỳ giữa cửa ,…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### quí/quý — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: quý[7599], quí[160]
- trace 'quí': “…đề xuất của quí vị và các…”
- trace 'quí': “…Kính thưa quí vị , chào…”
- trace 'quý': “…sàng phục vụ Quý khách và tạo…”
- trace 'quý': “…và tạo cho Quý khách một cảm…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### quĩ/quỹ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: quỹ[2533], quĩ[10]
- trace 'quĩ': “…, đang trong quĩ đạo vòng quanh…”
- trace 'quĩ': “…sáu mặt phẳng quĩ đạo đã sắp…”
- trace 'quỹ': “…phiếu của các quỹ chỉ cao hơn…”
- trace 'quỹ': “…nghiên cứu của Quỹ Nghiên cứu chính…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### quỉ/quỷ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: quỷ[876], quỉ[19]
- trace 'quỉ': “…Chẳng biết điều quỉ quái gì đã…”
- trace 'quỉ': “…Cái quỉ gì thế này…”
- trace 'quỷ': “…hạng Anh , Quỷ đỏ đã gây…”
- trace 'quỷ': “…đều nghĩ là quỷ nên không ai…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### rì/rỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: rì[28], rỳ[2]
- trace 'rì': “…cho huyện Na Rì đó là cơ…”
- trace 'rì': “…thảm cỏ xanh rì , hồ Dầu…”
- trace 'rỳ': “…nghỉ dưỡng Gò Rỳ - Gò Đình…”
- trace 'rỳ': “…, xóm Lũng Rỳ , xã Tổng…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### si/sy — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: si[207], sy[8]
- thành viên không có dấu thanh viết ra: si, sy (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'si': “…tôi copy nguyên si , hình trong…”
- trace 'si': “…king amphoe ) Si Nakhon được thành…”
- trace 'sy': “…cả Chánh và Sy cùng tham gia…”
- trace 'sy': “…helped that Abou Sy , Daizo Horikoshi…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### sì/sỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: sì[15], sỳ[2]
- trace 'sì': “…đàn dơi đen sì con nào con…”
- trace 'sì': “…thân thể đen sì là do bộ…”
- trace 'sỳ': “…Riệc , xóm Sỳ , xóm Cỏ…”
- trace 'sỳ': “…) do bà Sỳ Cún Lìn (…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### sĩ/sỹ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: sĩ[13399], sỹ[1207]
- trace 'sĩ': “…và bằng thạc sĩ Quản trị Kinh…”
- trace 'sĩ': “…mười chiến sĩ Hòn Khoai…”
- trace 'sỹ': “…nghĩa đấy bác sỹ .…”
- trace 'sỹ': “…Theo Bác sỹ Lương Văn Năm…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### thi/thy — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: thi[15541], thy[134]
- thành viên không có dấu thanh viết ra: thi, thy (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'thi': “…Facebooker Ha Mai Thi Nguyen chia sẻ…”
- trace 'thi': “…của P S G đang thi đấu thăng hoa…”
- trace 'thy': “…Quách Mai Thy được đánh giá…”
- trace 'thy': “…Bảo Thy sống sung sướng…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### thì/thỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: thì[30608], thỳ[5]
- trace 'thì': “…có chẩn đoán thì không được .…”
- trace 'thì': “…- Cảnh sát thì lại nghĩ tôi…”
- trace 'thỳ': “…ở Trường Y thỳ sao ?…”
- trace 'thỳ': “…tiếng kém thỳ đi bốc sagawa…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### ti/ty — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ty[16190], ti[378]
- thành viên không có dấu thanh viết ra: ti, ty (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'ti': “…bao giờ tự ti vì ngoại hình…”
- trace 'ti': “…mặc cảm tự ti , xấu hổ…”
- trace 'ty': “…Công ty cổ phần Fecon…”
- trace 'ty': “…, các công ty lớn trên thế…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### tì/tỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: tỳ[109], tì[84]
- trace 'tì': “…và ba nhóc tì tất bật chuẩn…”
- trace 'tì': “…Thùy liền tù tì sinh em bé…”
- trace 'tỳ': “…man đẹp không tỳ vết thôi .…”
- trace 'tỳ': “…gắn ra lắm tỳ vết nhưng chứ…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### tí/tý — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: tí[471], tý[179]
- trace 'tí': “…Bình tĩnh một tí đi mà .…”
- trace 'tí': “…đầu đũa một tí và có màu…”
- trace 'tý': “…Theo ông Tý , các cụ…”
- trace 'tý': “…con , cái Tý bị mua với…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### tỉ/tỷ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: tỷ[6067], tỉ[2714]
- trace 'tỉ': “…, ghi chép tỉ mỉ không ngừng…”
- trace 'tỉ': “…Tỉ trọng trong G D P…”
- trace 'tỷ': “…Hà Nội mở tỷ số cũng như…”
- trace 'tỷ': “…cũng như nâng tỷ số lên ba không…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### tị/tỵ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: tị[312], tỵ[154]
- trace 'tị': “…phải ghen tị với thân…”
- trace 'tị': “…sống trong trại tị nạn ở Schimatari…”
- trace 'tỵ': “…tục phải ghen tỵ với Mai Dora…”
- trace 'tỵ': “…dân làng ghen tỵ với thành công…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### vi/vy — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: vi[7214], vy[410]
- thành viên không có dấu thanh viết ra: vi, vy (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'vi': “…động của hành vi bắt nạt qua…”
- trace 'vi': “…vĩ mô và vi mô .…”
- trace 'vy': “…Nguyễn Thị Quỳnh Vy ( lớp ngày mười tháng một…”
- trace 'vy': “…thể chỉ cần Vy cựa mình là…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### vĩ/vỹ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: vĩ[1228], vỹ[67]
- trace 'vĩ': “…cả ở tầm vĩ mô và vi…”
- trace 'vĩ': “…ấy là một vĩ nhân .…”
- trace 'vỹ': “…đẹp , kỳ vỹ của vùng Tây…”
- trace 'vỹ': “…vợ chồng Lâm Vỹ Dạ - Hứa…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### vị/vỵ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: vị[19496], vỵ[4]
- trace 'vị': “…số giữa đơn vị đứng đầu và…”
- trace 'vị': “…từ những đơn vị kinh doanh ,…”
- trace 'vỵ': “…Vương và đường Vỵ Xuyên .…”
- trace 'vỵ': “…Nguyên Vỵ có niềm đam…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### xi/xy — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: xi[553], xy[128]
- thành viên không có dấu thanh viết ra: xi, xy (thanh ngang hợp lệ — không tự coi là mất dấu/lỗi)
- trace 'xi': “…xăng dầu , xi măng … đều…”
- trace 'xi': “…đổ bê tông xi măng ; tỷ…”
- trace 'xy': “…bốn triệu người Xy - ri phải…”
- trace 'xy': “…, thở ô xy qua mặt nạ…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### ì/ỳ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ì[60], ỳ[11]
- trace 'ì': “…Tôi không ì vì luôn khát…”
- trace 'ì': “…là khá ì ạch ,…”
- trace 'ỳ': “…doanh nghiệp chây ỳ , không ít…”
- trace 'ỳ': “…tạo ra sức ỳ lớn trong các…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### í/ý — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ý[18681], í[26]
- trace 'í': “…, i , í , gì ,…”
- trace 'í': “…bánh mì luôn í : ba Bánh…”
- trace 'ý': “…điểm đáng chú ý trong xếp hạng…”
- trace 'ý': “…Nhưng gây chú ý hơn cả là…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

### ỉ/ỷ — [APPROVED-EXACT] rule trace: EXACT_FIXTURE
- freq literal: ỉ[47], ỷ[45]
- trace 'ỉ': “…bị đau âm ỉ hoặc đau phía…”
- trace 'ỉ': “…Căng thẳng âm ỉ từ lâu giữa…”
- trace 'ỷ': “…quan cấp dưới ỷ lại và giảm…”
- trace 'ỷ': “…sinh ra tính ỷ lại .…”
- Quyết/đánh giá reviewer: duyệt mức fixture (origin trong inventory.APPROVED_EXACT_FIXTURES: 8 cặp vòng 6.1 + 18 cặp mới v11 §5.2 + 19 cặp QD57-2026-10-02).

## 38 nhóm excluded_v1 theo QD57-2026-10-02 (KHÔNG duyệt merge — đúng đối tượng, giữ protected)

### beo/beu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: beo[23], beu[3]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): beu
- protected (KHÔNG bị quyết định này loại): beo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded beu · protected beo
- Lý do ledger: beu là BeU trong ba ngữ cảnh nhãn hiệu. Beo là dạng Việt hợp lệ (con beo), không mặc định béo thiếu dấu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### bio/biu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: bio[57], biu[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): bio đọc như một âm tiết VI theo alias io→iu
- protected (KHÔNG bị quyết định này loại): biu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded bio · protected biu
- Lý do ledger: bio trong tên Bio/nhãn BioNTech/bio-diesel; biu cũng có tên ngoại. Không bảo đảm phát âm nguyên ngữ của bên nào, không tuyên bố vần iu không hợp lệ.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### bâo/bâu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: bâu[8], bâo[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): bâo
- protected (KHÔNG bị quyết định này loại): bâu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded bâo · protected bâu
- Lý do ledger: Dạng âo không được nhận làm biến thể chính tả của âu ở v1; chưa chốt token nguồn, không tự thay bằng bâu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### chếc/chếch — [EXCLUDED-V1 QD57] rule trace: MR-CODA-CH-C
- freq literal: chếch[11], chếc[3]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): chếc
- protected (KHÔNG bị quyết định này loại): chếch
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded chếc · protected chếch
- Lý do ledger: chếc tàu/chếc xe; không có căn cứ cho từ chiếc không i mang nghĩa vật đếm. Không mặc định sửa thành chiếc, không duyệt ch/c.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### cue/quê — [EXCLUDED-V1 QD57] rule trace: MR-ONSET-C-K+MR-QU-K-GLIDE+MR-UE-UÊ
- freq literal: quê[2174], cue[17]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): cue đọc VI theo alias tới quê
- protected (KHÔNG bị quyết định này loại): quê
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded cue · protected quê
- Lý do ledger: Không cấp quan hệ cue=quê; cue/tên ngoại cần cách đọc theo contract. Không tự đổi route sang EN.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### cuới/quới — [EXCLUDED-V1 QD57] rule trace: MR-ONSET-C-K+MR-QU-K-GLIDE
- freq literal: quới[21], cuới[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): cuới
- protected (KHÔNG bị quyết định này loại): quới
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded cuới · protected quới
- Lý do ledger: cuới trong đám cuới; quới trong Bình Quới/Tân Quới. KHÔNG khẳng định quới đồng âm cưới: master hiện đã phân biệt cưới/quới. Không tự phục hồi cuới thành cưới.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### cấo/cấu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U+MR-ONSET-C-K
- freq literal: cấu[3143], cấo[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): cấo
- protected (KHÔNG bị quyết định này loại): cấu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded cấo · protected cấu
- Lý do ledger: Chưa có căn cứ nhận cấo làm biến thể của cấu; lỗi khả nghi không cho phép tự sửa.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### deo/deu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: deo[7], deu[7]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): deu
- protected (KHÔNG bị quyết định này loại): deo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded deu · protected deo
- Lý do ledger: deu trộn văn bản mất dấu và token ngoại; deo có deo dẻo trong trace. Không suy hai bên đều hỏng hoặc đều là token ngoại.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### di/dy — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: di[6655], dy[5]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): dy trong các cách dùng chưa xác nhận
- protected (KHÔNG bị quyết định này loại): di
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded dy · protected di
- Lý do ledger: Dy có ngữ cảnh viết tắt/tên ngoại/lỗi; không có cơ sở duyệt toàn nhóm như biến thể di. Không dùng quy tắc d cấm y để phủ nhận mọi tên riêng.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### dio/diu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: dio[16], diu[4]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): dio đọc một âm tiết VI theo alias io→iu
- protected (KHÔNG bị quyết định này loại): diu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded dio · protected diu
- Lý do ledger: Dio là tên ngoại trong mẫu; diu có tên/viết tắt. Rime iu tự nó hợp lệ; không tự thêm dấu huyền vào diu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### eo/eu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: eo[434], eu[9]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): eu trong cách dùng chưa xác nhận
- protected (KHÔNG bị quyết định này loại): eo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded eu · protected eo
- Lý do ledger: eu có Eu, EU và câu ngoại; không suy có một từ Việt tương đương eo, không mặc định eu=êu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### hue/huê — [EXCLUDED-V1 QD57] rule trace: MR-UE-UÊ
- freq literal: huê[30], hue[17]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): hue
- protected (KHÔNG bị quyết định này loại): huê
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded hue · protected huê
- Lý do ledger: hue có thể thuộc mất dấu/tên ngoại; chưa cấp phục hồi. Huê khác Huế ở thanh; giữ huê, không giải thích huê bằng Huế.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### io/iu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: iu[15], io[12]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): io đọc một âm tiết VI theo alias io→iu
- protected (KHÔNG bị quyết định này loại): iu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded io · protected iu
- Lý do ledger: Không có cơ sở nhận io là biến thể Việt của iu; không loại iu hoặc khẳng định mọi occurrence iu đều là từ chuẩn.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### iên/yên — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: yên[3469], iên[3]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): iên
- protected (KHÔNG bị quyết định này loại): yên
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded iên · protected yên
- Lý do ledger: iên kết, Iên bàn, iên phòng: gợi mất/nhầm phụ âm đầu. Không lấy quy tắc iê/yê trong thiên/yên để nhận các token lỗi này. Vần yên kết thúc n, không phải ng.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### iểu/yểu — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: yểu[32], iểu[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): iểu
- protected (KHÔNG bị quyết định này loại): yểu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded iểu · protected yểu
- Lý do ledger: cớm iểu truyền thống; iểu diễn: có dấu hiệu mất phụ âm đầu. Không chọn hộ kiểu/biểu/yểu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### keo/keu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: keo[257], keu[3]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): keu
- protected (KHÔNG bị quyết định này loại): keo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded keu · protected keo
- Lý do ledger: keu goi gợi kêu gọi trong mẫu; đó không phải keo. Chỉ nhánh fold đã được ủy quyền mới được chọn ứng viên, không do quyết định loại trừ này.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### leo/leu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: leo[1009], leu[3]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): leu
- protected (KHÔNG bị quyết định này loại): leo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded leu · protected leo
- Lý do ledger: Mẫu leu-enkephalin, Saint-Leu, Chamkar Leu; không có căn cứ nói leu chắc chắn là lêu thiếu dấu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### meo/meu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: meo[34], meu[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): meu
- protected (KHÔNG bị quyết định này loại): meo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded meu · protected meo
- Lý do ledger: meu trong Exhibit Meu, sur-Meu; giữ meo hợp lệ (meo meo/mốc meo), không dùng tần suất thấp để loại meo.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### mio/miu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: miu[50], mio[16]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): mio đọc một âm tiết VI theo alias io→iu
- protected (KHÔNG bị quyết định này loại): miu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded mio · protected miu
- Lý do ledger: Mio là tên/nhãn trong trace; không suy đồng âm với miu. Tên ngoại có thể nhiều âm tiết; không tự phân tách token ở G2P.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### neo/neu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: neo[301], neu[34]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): neu
- protected (KHÔNG bị quyết định này loại): neo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded neu · protected neo
- Lý do ledger: neu trộn văn bản không dấu Neu ban... và địa danh Neu-Breisach. Không gọi mọi neu là tiếng Đức hoặc phục hồi tất cả thành nếu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### nhí/nhý — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: nhí[328], nhý[5]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): nhý trong dữ liệu mã hóa hỏng
- protected (KHÔNG bị quyết định này loại): nhí
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded nhý · protected nhí
- Lý do ledger: nhý xuất hiện cùng chuỗi mojibake như nhý mong ði. Không có căn cứ nói nhý chỉ là lỗi của nhỉ/nhị; không sửa mã hóa trong G2P.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### níc/ních — [EXCLUDED-V1 QD57] rule trace: MR-CODA-CH-C
- freq literal: ních[11], níc[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): níc thuộc phiên âm chưa được chốt
- protected (KHÔNG bị quyết định này loại): ních
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded níc · protected ních
- Lý do ledger: Hai mẫu Téc-Níc/Kô-níc, không phải bằng chứng níc không tồn tại hoặc lỗi nịch. Chưa duyệt cách đọc của phân đoạn phiên âm này như alias của ních.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### pio/piu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: pio[12], piu[4]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): pio đọc một âm tiết VI theo alias io→iu
- protected (KHÔNG bị quyết định này loại): piu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded pio · protected piu
- Lý do ledger: Pio trong tên người nước ngoài; không suy tương đương piu. Không phủ nhận lớp âm tiết/biểu cảm piu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### rio/riu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: rio[161], riu[15]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): rio đọc một âm tiết VI theo alias io→iu
- protected (KHÔNG bị quyết định này loại): riu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded rio · protected riu
- Lý do ledger: Rio trong tên địa danh/tên ngoại. Giữ cách đọc VI của riu; không chứng nhận tên khách sạn Riu nguyên ngữ chỉ từ dạng chữ.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### río/ríu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: río[13], ríu[12]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): río đọc như âm tiết VI có thanh sắc
- protected (KHÔNG bị quyết định này loại): ríu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded río · protected ríu
- Lý do ledger: Río Grande/Río Muni có trong trace; đây là chữ ngoại có dấu nhấn, không phải bằng chứng một token Việt bị gõ sai.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### seo/seu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: seo[1776], seu[4]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): cách đọc tên ngoại/viết tắt trong seo/seu; đặc biệt alias seu→seo
- protected (KHÔNG bị quyết định này loại): seo trong chế độ đọc VI nguyên dạng
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded seu · protected seo
- Lý do ledger: seo chủ yếu Park Hang-seo; seu có La Seu/Lee Seu. Không lấy cách đọc tên Hàn hay tên ngoại làm chứng cứ cho coda w Việt, không sửa seo thành sẹo.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### sio/siu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: siu[32], sio[10]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): sio trong tên ngoại/ký hiệu và alias sio→siu
- protected (KHÔNG bị quyết định này loại): siu trong chế độ đọc VI nguyên dạng
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded sio · protected siu
- Lý do ledger: SiO là công thức trong một số mẫu; Siu Black/Siu Pui là tên thật. Không nói Siu là tiếng lóng hoặc cả hai không có vần chuẩn.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### sue/suê — [EXCLUDED-V1 QD57] rule trace: MR-UE-UÊ
- freq literal: sue[60], suê[8]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): sue đọc như một âm tiết VI bằng alias ue→uê
- protected (KHÔNG bị quyết định này loại): suê
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded sue · protected suê
- Lý do ledger: Sue trong Eugène Sue/Mina Sue/Sue Storm, không chỉ động từ tiếng Anh. Suê có sum suê/Cư Suê ngay trong trace; không loại vì không rõ từ thật.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### teo/teu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: teo[92], teu[21]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): teu trong các cách dùng chưa xác nhận
- protected (KHÔNG bị quyết định này loại): teo
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded teu · protected teo
- Lý do ledger: Mẫu Teu là đơn vị vận tải TEU. Không có cơ sở phục hồi teu thành têu.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### thue/thuê — [EXCLUDED-V1 QD57] rule trace: MR-UE-UÊ
- freq literal: thuê[3152], thue[17]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): thue
- protected (KHÔNG bị quyết định này loại): thuê
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded thue · protected thuê
- Lý do ledger: tron thue, chi cuc thue, thue xuat nhap khau gợi thuế, không phải thuê. Đây là nhận xét chứng cứ, không phải lệnh tự sửa thành thuế.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### tio/tiu — [EXCLUDED-V1 QD57] rule trace: MR-CODA-O-U
- freq literal: tio[13], tiu[8]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): tio trong tên ngoại/ký hiệu và alias tio→tiu
- protected (KHÔNG bị quyết định này loại): tiu
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded tio · protected tiu
- Lý do ledger: TiO/các tên ngoại ở phía tio; tiu có tiu nghỉu là từ Việt rõ. Không tuyên bố cả hai không hợp lệ.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### tue/tuê — [EXCLUDED-V1 QD57] rule trace: MR-UE-UÊ
- freq literal: tue[6], tuê[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): tue;tuê trong các cách dùng chưa xác nhận
- protected (KHÔNG bị quyết định này loại): không cấp thêm xác nhận từ mới cho hai dạng này
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded tue, tuê · protected (không có — cả hai phía thuộc cách dùng chưa xác nhận)
- Lý do ledger: tue trộn tri tue với Tue ngày trong tuần; tuê có trí tuê. Không dùng ví dụ tuê miên chưa có căn cứ; không tự phục hồi thành tuệ.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### tíc/tích — [EXCLUDED-V1 QD57] rule trace: MR-CODA-CH-C
- freq literal: tích[14352], tíc[7]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): tíc trong nhóm phiên âm/biến thể chưa được xác nhận
- protected (KHÔNG bị quyết định này loại): tích
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded tíc · protected tích
- Lý do ledger: Trộn logis-tíc, Gô-tíc, tíc tắc và lỗi mã hóa. Không kết luận chúng đều là một từ chuẩn hoặc duyệt ch/c; cách đọc nguyên ngữ/Việt hóa chưa thuộc bảo đảm v1 này.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### xue/xuê — [EXCLUDED-V1 QD57] rule trace: MR-UE-UÊ
- freq literal: xuê[6], xue[4]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): xue đọc VI qua alias ue→uê
- protected (KHÔNG bị quyết định này loại): xuê
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded xue · protected xuê
- Lý do ledger: Xue Ming/Li Xue là tên trong trace; xuê có xum xuê. Không giải thích xuê là tiếng lóng của xui.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### xỉ/xỷ — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: xỉ[436], xỷ[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): xỷ trong các cách dùng chưa xác nhận
- protected (KHÔNG bị quyết định này loại): xỉ
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded xỷ · protected xỉ
- Lý do ledger: xấp xỷ và xỷ lý có khả năng tương ứng với các từ khác nhau. Không cấp alias xỷ=xỉ cho toàn nhóm, không tự sửa xỷ thành xử.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### âi/ây — [EXCLUDED-V1 QD57] rule trace: MR-CODA-I-Y
- freq literal: ây[14], âi[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): âi
- protected (KHÔNG bị quyết định này loại): ây
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded âi · protected ây
- Lý do ledger: Hai mẫu âi nằm trong chuỗi mã hóa hỏng. Không dùng chúng để duyệt coda i/y; không tự phục hồi cả âi/ây thành ấy.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### đi/đy — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: đi[38741], đy[3]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): đy trong các cách dùng chưa xác nhận
- protected (KHÔNG bị quyết định này loại): đi
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded đy · protected đi
- Lý do ledger: Trộn Đy là, Ô-Đy-Sê, gồi đàng goàng đy. Không đủ cơ sở một phép đy→đi chung cho mọi occurrence; không tự chọn đi/đây hay cách đọc tên phiên âm.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

### ĩ/ỹ — [EXCLUDED-V1 QD57] rule trace: MR-I-Y
- freq literal: ĩ[47], ỹ[2]
- subject (bị giới hạn, KHÔNG bảo đảm cách đọc v1): ỹ dạng token tách rời
- protected (KHÔNG bị quyết định này loại): ĩ
- thành viên máy đọc (exact NFC+lower giữ dấu — R14-01): excluded ỹ · protected ĩ
- Lý do ledger: Hai mẫu là s ỹ quan, s ỹ mới: dấu hiệu tách hỏng sĩ/sỹ. Không ghép token hoặc tự xóa/thêm ranh giới.
- Ranh giới contract (QD57 §4): không tự phục hồi dấu, không đổi route, không ghép/tách token, fold/spell chỉ khi contract ủy quyền; khi không có đường được phép → trả trạng thái không hỗ trợ có cấu trúc (collision_audit.scope_exclusion_status).

## 12 nhóm ach/ec đã diễn giải bằng thay đổi biểu diễn (ham/0.2 — hết collision)

- sách/séc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- mách/méc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- bách/béc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- hách/héc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- mạch/mẹc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- tách/téc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- vách/véc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- xách/xéc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- ách/éc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- ạch/ẹc — DO_NOT_MERGE_PRESERVE_CONTRAST — vần 'ach' giờ PHONE_OPEN_E_PREVELAR, hai dạng khác chuỗi segment ở master mặc định (ham/0.2).
- thách/théc — INSUFFICIENT_EVIDENCE — hết collision do ham/0.2 (vần 'ach' ≠ 'ec'); quyết định từng từ/cách đọc vẫn còn mở khi xét ngoài miền collision.
- cạch/kẹc — INSUFFICIENT_EVIDENCE — hết collision do ham/0.2 (vần 'ach' ≠ 'ec'); quyết định từng từ/cách đọc vẫn còn mở khi xét ngoài miền collision.

## 0 nhóm pending

QD57-2026-10-02 đã quyết hết 57 nhóm treo từ v11 (19 duyệt exact + 38 excluded_v1).
