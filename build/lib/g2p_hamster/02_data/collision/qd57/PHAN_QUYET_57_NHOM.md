# Phán quyết tổng hợp 57 nhóm — không cần thêm bản dự thảo

**Mã quyết định: QD57-2026-10-02.**

Căn cứ: bảng dự thảo 21/36 vừa gửi; report và toàn bộ ví dụ trace của 57 nhóm trong gói v13 đã xác minh. Các ca kỹ thuật đóng ở v13 giữ nguyên. Không sửa source production, không mở lại R12-01/R12-02.

## 1. Quyết định cuối của reviewer đối với bản dự thảo

**Không duyệt nguyên trạng phương án 21/36. Thay bằng:**

| Phán quyết | Số nhóm |
|---|---:|
| **Duyệt mới, exact fixture trong chế độ đọc âm tiết/từ VI nguyên dạng** | **19** |
| **Không duyệt merge; đề xuất giới hạn bảo đảm v1 theo đúng đối tượng được chỉ rõ** | **38** |
| Tổng | **57** |

19 là phán quyết phát âm mới, không phải quyền suy rộng từ A1 hay 26 fixture cũ. 38 là giới hạn sản phẩm được đề xuất có điều kiện, **không phải kết luận tất cả là từ sai/noise**, cũng không phải 38 cặp đã được chứng minh không đồng âm.

Việc giảm phạm vi hỗ trợ v1 cần chủ dự án chấp thuận trước khi áp dụng. Reviewer chấp nhận **thiết kế giới hạn ở §4**, không chấp nhận chỉ gắn tier để bỏ qua việc xử lý đầu vào. Chưa áp các quyết định này vào runtime: bản v13 vẫn là 26 approved / 57 proposal.

Không yêu cầu dựng thêm bảng ngôn ngữ. Danh sách máy đọc và căn cứ cho **từng nhóm** đã có trong `ledger_57_quyet_dinh.csv` và `PHU_LUC_57_NHOM.md`.

## 2. Scope chính xác của 19 fixture được duyệt

### 2.1 Ý nghĩa của approval

Đọc **chính âm tiết đã viết**, theo `vi_chinh_ta`, trong chế độ VI-word do contract tầng trước xác định; giữ đầy đủ dấu thanh và chữ gốc. Đây là phán quyết về cách đọc theo chính tả Việt, **không chứng nhận cách phát âm nguyên ngữ của mọi người/địa danh trùng tên**.

Không áp cho:

- tên chữ cái, đọc spelling, biến/ký hiệu hoặc phép đọc viết tắt;
- English `I`, `my`, tên ngoại giữ cách đọc nguyên ngữ;
- `ny` mang nghĩa viết tắt *người yêu*, `NY`, hoặc bất kỳ phép mở rộng viết tắt nào;
- phục hồi dấu, chữa lỗi chữ/mã hóa, thay ngữ nghĩa hoặc thay route;
- một nhóm chứa thêm thành viên ngoài đúng cặp được duyệt.

Nếu chế độ đọc không đáp ứng scope, không được viện dẫn fixture để hợp thức hóa. Không tự tạo mode mới hoặc ghi đè quyết định tầng 1.

Sự tồn tại của một biến thể viết có cách đọc rõ **không đồng nghĩa** biến thể ấy là chính tả chuẩn dùng trong sách giáo khoa. Tên riêng cũng không bị loại chỉ vì không nằm trong một “danh sách phụ âm được viết y”. Điều 9 Quyết định 1989/QĐ-BGDĐT phân biệt cách viết âm i thông thường với việc giữ đúng tên riêng, nêu các ví dụ Vy, Vi, Vỹ, Thy. Đây là căn cứ hỗ trợ phân loại chữ viết, không phải tự động cấp approval cho toàn matcher. [1](https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1989-QD-BGDDT-2018-quy-dinh-chinh-ta-Chuong-trinh-sach-giao-khoa-giao-duc-pho-thong-445355.aspx?anchor=dieu_9)

### 2.2 Danh sách và expected record

Mọi cặp dưới đây có glide rỗng. Coda rỗng trừ iêng/yêng. Ký hiệu ∅ nghĩa là không có onset/coda, không thêm một PHONE glottal mới.

| Cặp được duyệt mới | Onset | Nucleus | Coda | Tone | Căn cứ/ngữ cảnh chính |
|---|---|---|---|---|---|
| hì/hỳ | PHONE_H | PHONE_I | ∅ | TONE_HUYEN | hì; hỳ hỳ/Nà Hỳ |
| i/y | ∅ | PHONE_I | ∅ | TONE_NGANG | Đọc âm tiết VI nguyên dạng /i/; tuyệt đối không English I hoặc tên chữ |
| ki/ky | PHONE_K | PHONE_I | ∅ | TONE_NGANG | Cách đọc VI /ki/; ky cóp, không suy từ kí/ký |
| lị/lỵ | PHONE_L | PHONE_I | ∅ | TONE_NANG | tỉnh lị/tỉnh lỵ; trấn lị/huyện lỵ |
| mi/my | PHONE_M | PHONE_I | ∅ | TONE_NGANG | mi, tên My đọc theo chữ Việt; không English my |
| mỉ/mỷ | PHONE_M | PHONE_I | ∅ | TONE_HOI | tỉ mỉ/tỷ mỷ và tên Mỷ; không chứng nhận chuẩn biên tập |
| mị/mỵ | PHONE_M | PHONE_I | ∅ | TONE_NANG | thùy mị, Mỵ Châu |
| ni/ny | PHONE_N | PHONE_I | ∅ | TONE_NGANG | ni/ny-lông, tên Ny đọc VI; không mở rộng ny thành người yêu |
| si/sy | PHONE_S_RETRO | PHONE_I | ∅ | TONE_NGANG | si, tên Sy khi đọc theo chữ Việt |
| sì/sỳ | PHONE_S_RETRO | PHONE_I | ∅ | TONE_HUYEN | đen sì, tên Sỳ trong trace |
| thi/thy | PHONE_TH | PHONE_I | ∅ | TONE_NGANG | thi, tên Thy |
| vi/vy | PHONE_V | PHONE_I | ∅ | TONE_NGANG | vi, tên Vy |
| vĩ/vỹ | PHONE_V | PHONE_I | ∅ | TONE_NGA | vĩ, tên Vỹ; không gọi vỹ đại là chuẩn phổ thông |
| vị/vỵ | PHONE_V | PHONE_I | ∅ | TONE_NANG | vị, các tên Vỵ trong trace |
| xi/xy | PHONE_S | PHONE_I | ∅ | TONE_NGANG | xi măng, ô xy, xy lanh theo cách đọc VI |
| í/ý | ∅ | PHONE_I | ∅ | TONE_SAC | âm tiết/thán từ VI /i/ sắc, không sửa ý nghĩa |
| **rì/rỳ** | PHONE_R_VI | PHONE_I | ∅ | TONE_HUYEN | rì, Gò Rỳ/Lũng Rỳ |
| **iêng/yêng** | ∅ | PHONE_I_SCHWA | PHONE_NG | TONE_NGANG | Iêng Xary/yêng hùng; cách đọc vần /iəŋ/ |
| **thì/thỳ** | PHONE_TH | PHONE_I | ∅ | TONE_HUYEN | thì và biến thể viết phi chuẩn thỳ trong câu VI |

Ba dòng cuối được **chuyển từ bucket B dự thảo sang duyệt hẹp**. Không có căn cứ loại rỳ chỉ vì tần suất 2 hoặc loại thỳ chỉ vì chữ y sau th. Với iêng/yêng, các tài liệu dạy đọc cũng nhận diện hai dạng vần này; kết hợp ngữ cảnh Iêng/yêng trong trace, tôi duyệt **đúng cặp thanh ngang**, không duyệt yê/iê toàn miền. [1](https://www.vietjack.com/giao-an-tieng-viet-1/bai-83-ieng-yeng-iec-cd.jsp) [3](https://sachgiai.com/Van-hoc/bang-am-van-tieng-viet-theo-chuong-trinh-giao-duc-cong-nghe-va-sach-cai-cach-giao-duc-10458.html)

**Không nhập IPA giản lược sai vào master:** si/sy và sì/sỳ giữ `PHONE_S_RETRO`; xi/xy giữ `PHONE_S`. thi/thy, thì/thỳ giữ `PHONE_TH`, không phải T+H. Quyết định này không gộp s/x hay thay dialect policy.

Expected records được viết tường minh trong `19_fixture_moi.json`. Đã đối chiếu 38 dạng: **38/38 khớp parser v13**. Đây là xác nhận implementation đáp ứng kỳ vọng, không dùng output trùng nhau làm nguồn để tự sinh approval.

## 3. Năm nhóm phải rút khỏi bucket A dự thảo

| Nhóm | Phán quyết và căn cứ thực tế |
|---|---|
| **chếc/chếch** | Không duyệt. Trace là *chếc tàu*, *chếc xe*, *chếc dòi*; chưa có căn cứ cho một từ chếc mang nghĩa vật đếm. Không dùng “hai chếc chén” để chứng minh; không tự sửa thành chiếc. |
| **iên/yên** | Không duyệt nhóm này. *iên kết*, *Iên bàn*, *iên phòng* gợi mất/nhầm phụ âm đầu. Không đưa các lỗi ấy thành biến thể từ chuẩn bằng quy tắc viết iê/yê. **yên có coda /n/, không phải /ŋ/** như bản nháp. |
| **iểu/yểu** | Không duyệt. *cớm iểu truyền thống*, *iểu diễn* có dấu hiệu mất phụ âm đầu. Quy tắc đọc vần không xác nhận ý định của token hỏng, không được chọn hộ kiểu/biểu/yểu. |
| **tíc/tích** | Chưa cấp approval merge cho cả nhóm. Trace trộn logis-tíc, Gô-tíc, tíc tắc và lỗi mã hóa. Trong phạm vi v1 giới hạn, cách đọc các dạng phiên âm này chưa được bảo đảm; không suy ch/c toàn miền. Không khẳng định tíc và tích chắc chắn khác âm. |
| **ĩ/ỹ** | Không duyệt. Cả hai ví dụ của ỹ là *s ỹ quan*, *s ỹ mới*: dấu hiệu tách token hỏng. Giữ ĩ; không tự ghép s+ỹ hoặc sửa ranh giới IR. |

Các cách dùng như *tíc tắc* có thể được bổ sung bằng scope từ vựng cụ thể sau; việc không đưa vào bảo đảm v1 không phải phán quyết rằng chúng không tồn tại.

## 4. Scope v1 cho 38 nhóm còn lại — được phép giới hạn, không được giấu lỗi

### 4.1 Đơn vị bị giới hạn phải được chỉ rõ

Reviewer chấp nhận về mặt thiết kế việc **không bảo đảm các alias/cách đọc chưa xác nhận trong bảng phụ lục** ở v1. Đó không phải lệnh cấm cả hai từ trong mỗi cặp, không loại mọi tên riêng/từ mượn, không khẳng định mọi token ngoài phạm vi là sai chính tả.

Ví dụ:

- Giới hạn beu/BeU như alias của beo; **không loại beo**, không sửa thành béo.
- Giới hạn thue chưa phân giải; **không loại thuê** và không mặc định thue=thuê.
- Giới hạn cuới chưa phân giải; **không loại Quới**, không sửa Quới thành cưới.
- Giới hạn alias tio→tiu, sio→siu; **không loại tiu trong tiu nghỉu, Siu trong tên Siu Black**.
- Giới hạn hue/sue/xue chưa xác nhận như âm tiết VI qua alias ue→uê; **không loại huê/suê/xuê**.

Cột `not_excluded_by_this_decision` trong ledger có nghĩa **quyết định này không loại bên đó**, không phải chứng nhận phát âm nguyên ngữ của mọi tên ngoại trùng chuỗi chữ.

### 4.2 Không được suy tác vụ sửa input từ nhãn ngoài phạm vi

- **Không tự phục hồi dấu:** nhận xét thue trong *tron thue* gợi thuế không phải lệnh thue→thuế; cuới trong *đám cuới* không cấp lệnh cuới→cưới.
- **Không tự đổi route:** token ngoại không mặc nhiên là EN. Nếu IR đã chọn route/mode khác, giữ nguyên; nếu có mismatch, trả thông tin lỗi/không hỗ trợ theo contract, không sửa IR.
- **Không tự ghép/tách token**, sửa mã hóa hoặc mở rộng viết tắt.
- Chỉ dùng fold/spell khi **đã được contract ủy quyền cho đúng trường hợp**, có provenance/fallback_reason theo thiết kế. Không lấy nhãn `out_of_scope_v1` làm một giấy phép fold/spell mới cho cả danh sách.
- Khi không có đường xử lý được phép, phải trả trạng thái không hỗ trợ/chưa phân giải/lỗi có cấu trúc theo contract; không lặng lẽ phát âm theo record chưa được nhận rồi báo đã hỗ trợ v1.

Không đặt thêm tên enum/API ở báo cáo này. Dùng đúng các trạng thái và đường xử lý đã được thiết kế cho pipeline.

### 4.3 Điều kiện để một nhóm được ra khỏi active gate v1

Phải có **đủ**:

1. Chủ dự án chấp thuận phạm vi giới hạn được chỉ rõ trong ledger.
2. Giữ nhóm ứng viên gốc, tần suất, trace và lý do loại trừ; không sửa TSV/min_freq để mất nhóm.
3. Có ranh giới thực thi/contract để những cách dùng bị loại không được xuất như pronunciation đã bảo đảm của v1. Chỉ đổi tier trong audit chưa đủ.
4. Đối tác hợp lệ không bị kéo vào nhánh fold/spell/reject chỉ vì nằm cùng nhóm cũ.
5. Báo cáo tách **candidate domain** và **accepted v1 scope**, thống kê approved/excluded/unresolved riêng. Chỉ PASS đối với scope đã khai và kiểm đủ; không viết “mọi 83 nhóm đã đồng âm”.

Nếu chưa có một trong các điều kiện trên, giữ trạng thái `scope_exclusion_proposed`/chưa áp, **không gọi là đã giải phóng gate**. Đây là tiêu chí áp quyết định đã nêu, không mở lại lỗi kỹ thuật cũ.

## 5. Những căn cứ sai cần thay bằng trace có sẵn

Các sửa dưới đây đã được ghi theo từng hàng trong phụ lục, không yêu cầu tác giả nghiên cứu lại để dựng bản nháp khác:

| Bản nháp nói | Căn cứ đúng trong hồ sơ / cách sửa |
|---|---|
| beu không chuẩn, beo nghi béo | BeU là nhãn hiệu trong mẫu; beo là dạng hợp lệ. Không mặc định mất thanh. |
| ni/ny vì ny=người yêu cùng đọc ni | Không dùng lập luận đó. Approval chỉ cho đọc âm tiết VI nguyên dạng như ny-lông/tên Ny; loại phép mở rộng viết tắt khỏi scope. |
| rỳ không có từ thật | Có Gò Rỳ/Lũng Rỳ; duyệt cách đọc Việt hẹp, không phủ nhận tên riêng. |
| níc không tồn tại, nghi lỗi nịch | Có Téc-Níc/Kô-níc. Vấn đề là cách đọc phiên âm chưa chốt, không phải không tồn tại. |
| leu là lêu thiếu dấu | Trace có leu-enkephalin, Saint-Leu, Chamkar Leu; không được chọn lêu thay tất cả. |
| neu là token ngoại | Trộn *Neu ban...* với Neu-Breisach. Không có một cách xử lý cho tất cả. |
| río không có từ thật | Có Río Muni/Río Grande; dấu nhấn chữ ngoại không phải tự động là thanh sắc Việt. |
| suê không rõ từ thật | Có *sum suê*, Cư Suê ngay trong trace. |
| teo/teu vì teu=têu | Mẫu Teu là đơn vị vận tải TEU. Không có cơ sở phục hồi thành têu. |
| thue=thuê | Mẫu *tron thue*, *chi cuc thue*, *thue xuat nhap khau* gợi **thuế**; vẫn không tự phục hồi. |
| tio/tiu đều không có vần chuẩn | Có **tiu nghỉu**; TiO ở phía còn lại là ký hiệu trong một số mẫu. |
| xuê là tiếng lóng của xui | Có **xum xuê** trong trace; Xue nằm trong tên người. |
| quới đồng âm cưới | **Không đúng trong profile đang xét.** Master hiện đã phân biệt hai dạng này, xem dưới. |

```text
quới → PHONE_K + PHONE_W + PHONE_SCHWA_LONG + PHONE_J + TONE_SAC
cưới → PHONE_K + PHONE_UHORN_SCHWA           + PHONE_J + TONE_SAC
```

Đã kiểm trực tiếp hai record hiện hành. Không cần đổi master để đạt đối lập này; cần tránh một policy fold/loại trừ mới phá nó.

Thay câu “ach/ec là ca phá đối lập duy nhất” bằng: **“Trong phạm vi các quyết định ở bảng này, chưa yêu cầu thêm một thay đổi master; các đối lập đã khóa tiếp tục phải giữ.”** Việc không cấp approval cho một alias không chứng minh toàn bộ phần còn lại của ngôn ngữ không có đối lập khác.

## 6. Cách áp dụng — một lượt triển khai quyết định, rồi hậu kiểm cuối

Nếu chủ dự án chấp thuận phạm vi giới hạn ở §4:

1. Thêm **19 exact fixtures** với expected records trong JSON đính kèm. Tổng fixture reviewer duyệt sẽ là **45 = 26 cũ + 19 mới**. Matcher rộng vẫn `approved=False`.
2. Áp **38 quyết định giới hạn** theo đối tượng cụ thể và ranh giới contract, không blacklist cả cặp hoặc mọi token ngoại.
3. Pin catalog/scope/ledger và logic tiêu thụ. **Nếu thêm 19 vào catalog exact hiện hành, `approval_policy_hash` phải đổi**; không giữ mặc định `6eee24…`. Chỉ có thể giữ hash của catalog 26 cũ nếu thực sự không đổi catalog ấy và toàn bộ policy mới nằm ở một ledger/helper khác được hash riêng, được report ràng buộc đầy đủ.
4. Cập nhật test theo thay đổi được duyệt: **ki/ky nay là positive**, không còn là negative ngoài allowlist. Giữ negative bằng cặp chưa duyệt, sai tone, superset và record drift. Cập nhật count/version có nhật ký; không sửa expected chỉ vì code hiện cho output đó.
5. Chạy các bộ kiểm cũ và kiểm ranh giới scope mới; tối thiểu chứng minh Quới không thành cưới, thuê không bị loại cùng thue, beo/meo/suê/xuê/tiu không bị coi mất dấu chỉ vì không có dấu thanh viết ra, spelling/abbreviation/EN không thừa hưởng approval VI-word.
6. Giữ đủ số liệu gốc để có thể giải trình **83 nhóm ứng viên → 45 approved trong scope + 38 loại trừ có căn cứ**, nếu mọi điều kiện đã đạt. Nếu còn trường hợp chưa đạt boundary, báo unresolved đúng số; không đặt trước PASS.

Hai nhóm thách/théc, cạch/kẹc ngoài collision vẫn giữ lịch sử lexical mở, không tính thành approval mới và không đưa ngược thành blocker collision đã giải quyết.

**Không cần thêm bản dự thảo ngôn ngữ.** Bước tiếp theo là chủ dự án xác nhận phạm vi 19/38 đã hiệu chỉnh, áp chính xác ledger/boundary và gửi kết quả nghiệm thu cuối. Không cần làm lại builder, trace hay thay cấu trúc master đã chấp nhận.

## 7. Hồ sơ đính kèm và giới hạn

- `ledger_57_quyet_dinh.csv` / `.json`: đủ 57 nhóm, decision, đối tượng giới hạn, phía không bị loại, lý do, tần suất và toàn bộ ví dụ trace có sẵn cho mỗi thành viên.
- `PHU_LUC_57_NHOM.md`: phiên bản dễ đọc theo từng nhóm.
- `19_fixture_moi.json`: expected records và scope.
- `kiem_record_19_fixture.json`: 38/38 dạng khớp parser v13.
- `lap_ledger_review.py`: danh sách quyết định/expected viết tường minh; chỉ sinh hồ sơ reviewer và kiểm record, không sửa production.

Không nghe audio, không xác nhận phát âm nguyên ngữ của mọi tên, không tái xác thực corpus gốc. Nguồn ngôn ngữ bổ sung ở §2 hỗ trợ phạm vi chính tả/đọc vần; phán quyết exact là nhận định có scope của reviewer, không được tự động sinh chỉ từ luật chính tả hoặc từ output parser.
