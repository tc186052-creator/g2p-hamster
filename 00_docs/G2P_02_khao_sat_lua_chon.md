# G2P 02 — Khảo sát các hướng cho tầng 2 (CHỈ LIỆT KÊ, CHƯA CHỌN)

Ngày soạn: 01/10/2026. Mục đích: nguyên liệu cho buổi phân tích/chọn cùng user.
**Không hướng nào đã được duyệt.** Mọi thư viện nếu chọn dùng phải kiểm tra giấy phép
+ chất lượng thực địa trên corpus của mình trước khi cài.

## Bối cảnh ràng buộc (từ tầng 1 + user)

- Giọng đích: **Bắc chuẩn phát thanh** (đã ngầm định trong prompt trọng tài 9B).
- Đầu vào: IR `ir/0.1` từ tầng 1 — từng token ĐÃ có nhãn route vi/en, cat, kind.
- User đã chốt với tầng 1: **không lệ thuộc thư viện ngoài lỏ lẻo** (vinorm đã bỏ);
  triết lý dự án = luật + từ điển + tiny model. G2P nên giữ triết lý này.
- Tầng 3 CHƯA chọn công nghệ (piper / VITS / StyleTTS…): **định dạng phoneme đầu ra
  của tầng 2 phụ thuộc tầng 3** (mỗi acoustic model ăn một bộ phoneme/phonemizer
  riêng) — cân nhắc chọn tầng 3 TRƯỚC hoặc chọn tầng 2 sao cho dễ map về sau.

## Các hướng đã biết (cần thẩm định khi cân nhắc)

| Hướng | Ghi chú ban đầu | Rủi ro / việc phải làm nếu chọn |
|---|---|---|
| **vPhon** (kirbyj/vPhon, `pip install vPhon`) | Phonetizer vi ra IPA, 3 vùng miềm (Bắc/Trung/Nam); có tư liệu học thuật | Kiểm tra Py3.12 + giấy phép; **không xử lý từ Anh** (route en phải đi nhánh khác); luật cứng khó sửa theo corpus của mình |
| **Viphoneme / Vi_G2P** (v-nhandt21, PyPI `viphoneme`) | Dựa trên vPhon + tri thức âm vị học, raw text → IPA | Cùng rủi ro trên; chất lượng trên văn bản trộn Anh chưa rõ |
| **ViG2P** (hoang1007/vig2p) | Nhị ngữ vi-en, có xử lý viết tắt/acronym | Kiểm tra mô hình/data kèm theo (có phải neural? trọng lượng lớn?), giấy phép |
| **espeak-ng** | Phổ biến, ra IPA, hỗ trợ cả vi lẫn en trong một tool | Là **binary ngoài** — khả năng cao mâu thuẫn định hướng "không thư viện ngoài"; chất lượng vi middling; đọc vi kiểu máy |
| **Tự viết luật vi** (âm đầu/thân/vần/thanh từ chữ vi có dấu) | Chính tả vi rất quy tắc: ~30 âm đầu × ~55 vần × 6 thanh — dựng bảng đọc IPA thuần luật; hợp triết lý dự án; sửa được theo corpus | Công sức ban đầu; từ mượn/tên riêng phải có từ điển riêng; cần phoneme set chuẩn tham chiếu |
| **Hybrid: luật vi tự viết + từ điển latin (en mượn/tên riêng) + tiny model phiên âm en giản lược cho OOV** | Khớp 100% triết lý tầng 1 (luật chắc → từ điển → tiny referee); kiểm soát đầy đủ | Nhiều việc nhất; cần dữ liệu phiên âm để tiny học (từ 9B/espeak sinh teacher data được) |

## Câu hỏi mở để cùng user chốt (khi phân tích)

1. Chọn tầng 3 trước hay sau? (quyết định định dạng phoneme của tầng 2)
2. Bộ phoneme: IPA nguyên bản hay bộ rút gọn theo acoustic model?
3. Chính sách từ Anh OOV: từ điển + luật phiên âm giản lược, hay đánh vần, hay tiny model?
4. Từ không dấu ("khong", "nam") — tầng 1 đã route; tầng 2 đọc theo route, có cần chốt luật riêng?
5. Giấy phép của mọi thư viện cân nhắc.

## Nguồn tra cứu nhanh (01/10/2026)

- vPhon: <https://github.com/kirbyj/vPhon> — pip `vPhon`, IPA 3 vùng miềm
- Viphoneme: <https://github.com/v-nhandt21/Viphoneme> — PyPI `viphoneme`
- ViG2P: <https://github.com/hoang1007/vig2p> — nhị ngữ vi-en, xử lý acronym
