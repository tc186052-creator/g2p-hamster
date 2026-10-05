# BIÊN BẢN SPOT-CHECK E4 — ĐÃ KIỂM (điều kiện 7 §6) — 14/25 ĐẠT

- Phiên: v2 (stress-stripped) · 500 item · parse: first 490 / retry 10 / fail 0
- Model: `<workspace>/06_models/qwen/qwen3_5_9b_base` · quant: bitsandbytes NF4, compute bf16 (VRAM 12GB runbook) · prompt sha `c216c8e84cd47457…`
- Session sha256: `3d377cfd12773bc4…` · ngày: 2026-10-02
- **Người kiểm: agent ZCode (LLM) theo ỦY QUYỀN của chủ dự án** (chỉ đạo trực tiếp
  trong phiên: "bạn tự cử agent đi làm, bạn cx là llm mà").
- **Caveat minh bạch:** LLM kiểm LLM (GLM kiểm qwen3_5_9b) — có nguy cơ lệch
  cùng hệ. Reviewer có thể yêu cầu người thật soát lại 25 phiếu (~30–45 phút);
  kết quả agent là pre-screen chi tiết, kèm bằng chứng máy được: identity check
  25/25 qua production stream, CMUdict 4/4 cho từ EN, NFD audit chuỗi probe.

## Kết luận tổng

1. **Judge KHÔNG đủ tin cậy làm người phân xử phát âm: 14/25 (56%) phiếu
   chấp nhận được, 11/25 KHÔNG ĐẠT.** Mọi phiếu KHÔNG ĐẠT đều là lỗi phía
   judge: đọc sai input (tuyên thiếu dấu khi dấu hiện hữu — e4-0301, e4-0080),
   sai âm vị học ('ây' phải là /aj/ — e4-0189; 'c không đi kèm aː' — e4-0113),
   tự mâu thuẫn (e4-0293, e4-0046), áp ký hiệu ngoài quy ước rồi tuyên hệ sai
   (e4-0297, e4-0121, e4-0043), hoặc bịa cấu trúc (e4-0439 'dấu hỏi và ngã
   trùng lặp' trên cặp chỉ có một dấu).
2. **KHÔNG phát hiện lỗi G2P mới từ judge.** Danh sách 186 regressionnet
   hạ cấp thành CANDIDATE FLAGS — đầu vào bảng policy [B], không phải lỗi
   được chứng minh (đúng điều kiện 5: judge không là oracle).
3. **1 mục vào policy [B] cho chủ dự án:** token corpus không dấu ('tiêu',
   'Bây') được hệ đọc ngang trung thực theo token; có fold theo tần suất
   ('tiêu'→sắc, 'Bây'→huyền) hay không là quyết của chủ dự án.
4. **Sự cố quá trình kiểm (minh bạch):** agent ban đầu nghi hệ rơi thanh
   hàng loạt (10/30 probe) — audit NFD cho thấy chính chuỗi probe của agent
   thiếu/sai dấu; hệ đọc đúng 14/14 chuỗi dựng-NFD tường minh. **Không có bug
   thanh điệu.** (Và đúng minh họa lý do tồn tại của tầng 2: LLM cũng gõ sai
   dấu tiếng Việt.)

## 25 phiếu chi tiết

| # | item | từ | route | nhóm | verdict judge | KIỂM | lý do kiểm (agent) |
|---|---|---|---|---|---|---|---|
| 1 | e4-0445 | ty | vi | equal | hoa | **ĐẠT** | cặp identical 'ti' — hoa là verdict đúng |
| 2 | e4-0169 | doanh | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | tiền đề judge sai: 'thiếu âm đầu /d/' (z = d miền Bắc — quy ước master chốt) và 'thiếu n cuối' (ɲ chính là 'nh'); verdict dựa trên claim sai |
| 3 | e4-0121 | chuẩn | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | judge đọc 'c' như [k] rồi tuyên cả hai sai âm đầu; c = [c] (palatal) là IPA chuẩn cho 'ch' theo quy ước master đã chốt |
| 4 | e4-0402 | member | en | equal | hoa | **ĐẠT** | identical + khớp CMUdict (M EH1 M B ER0 → mɛmbɚ) |
| 5 | e4-0412 | ngần | vi | equal | hoa | **ĐẠT** | cặp identical — hoa đúng |
| 6 | e4-0293 | rằng | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | lý do tự mâu thuẫn ('âm đầu là /r/ (IPA là ʒ hoặc r)' rồi tuyên ʒ sai); ʒ (Bắc) và ɹ (tool) đều là lựa chọn phương ngữ hợp lệ — không phải 'cả hai sai' |
| 7 | e4-0294 | a | en | phoneme_lech | hoa | **ĐẠT** | ə/ɐ đều hợp lệ cho article 'a' unstressed — hoa hợp lý |
| 8 | e4-0494 | thần | vi | equal | hoa | **ĐẠT** | identical — đúng; judge gọi ↘ là 'hỏi' (thật ra huyền) — nhãn tên thanh sai, verdict không ảnh hưởng |
| 9 | e4-0301 | Chien | vi | tone_lech | ca_hai_sai | **KHÔNG ĐẠT** | judge tuyên cả hai 'thiếu dấu sắc' trong khi A chứa ↗ rõ ràng (ciə↗n) — ảo giác đọc input |
| 10 | e4-0266 | thương | vi | phoneme_lech | hoa | **ĐẠT (yếu)** | hoa trung lập; khác biệt vần thật (ɨə↔y) bị bỏ qua nhưng không tuyên sai điều gì |
| 11 | e4-0047 | biệt | vi | phoneme_lech | hoa | **ĐẠT** | iə↔iɛ là cùng nguyên âm đôi [iə̯] — lý do 'biến thể ký hiệu' đúng ngôn ngữ học |
| 12 | e4-0439 | học | vi | equal | ca_hai_sai | **KHÔNG ĐẠT** | trên cặp identical, lý do 'có dấu hỏi và ngã trùng lặp' là bịa (chỉ có ↓); 'học' là nặng không phải ngã; reading hɔʔ↓k là chuẩn của hệ |
| 13 | e4-0050 | những | vi | phoneme_lech | hoa | **ĐẠT (yếu)** | hoa chấp nhận được; lý do lộn (gọi sắc là 'hỏi', lập luận phương ngữ y/ɨ lỏng lẻo) |
| 14 | e4-0297 | tục | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | judge áp ký hiệu riêng (đòi '→' cho nặng) rồi tuyên hệ sai — chê ký hiệu chuẩn đã khai báo, không phân xử phát âm; coda k↔c là quy ước đã ghi |
| 15 | e4-0046 | chuyện | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | tự mâu thuẫn: nêu dạng đúng '/cwiəʔn/' trùng phương án A (ciə/ɛ) rồi vẫn tuyên cả hai sai |
| 16 | e4-0043 | chào | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | đọc 'c' như [k] và tuyên 'đọc thành ca' — sai; caː↘w là rendering chuẩn 'chào' theo quy ước master |
| 17 | e4-0063 | Chính | vi | phoneme_lech | hoa | **ĐẠT** | nhận đúng c/ʧ đều chấp nhận được — hoa hợp lý (nhất quán ngược với các phiếu 12/21/16 của chính nó) |
| 18 | e4-0401 | granting | en | equal | hoa | **ĐẠT** | identical + khớp CMUdict (G R AE1 N T IH0 NG) |
| 19 | e4-0309 | in | en | equal | hoa | **ĐẠT** | identical ɪn, khớp CMUdict IH0 N |
| 20 | e4-0080 | tiền | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | judge tuyên hai phương án 'thanh ngang' trong khi ↘ hiện hữu trong cả hai; tiền là huyền đã mark ↘ — đọc sai input |
| 21 | e4-0002 | tiêu | vi | phoneme_lech | hoa | **ĐẠT (yếu)** | hoa chấp nhận được với cặp gần-identical; lý do chứa ảo giác (tuyên có 'thanh hỏi ↘' khi chuỗi không có mũi tên). Ghi chú hệ thống: token corpus 'tiêu' là NGANG (không dấu) — hệ đọc trung thực; fold 'tiêu'→sắc thuộc policy [B] chờ chủ dự án, không phải lỗi phiên |
| 22 | e4-0189 | Bây | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | judge sai âm vị học: tuyên vần phải /aj/ (đúng là [əj] cho 'ây') và 'thiếu dấu ngang' (ngang không mang mũi tên theo thiết kế); bəj đúng với token 'Bây' |
| 23 | e4-0187 | kiên | vi | phoneme_lech | A | **ĐẠT** | chọn A (bên mình) đúng: kiən chuẩn hơn iɛn cho 'kiên' |
| 24 | e4-0113 | cảnh | vi | phoneme_lech | ca_hai_sai | **KHÔNG ĐẠT** | lý do phi lý ('c không đi kèm nguyên âm aː' — chính là cấu trúc cảnh/cả); cảnh là hỏi, judge gọi ngã |
| 25 | e4-0460 | về | vi | equal | hoa | **ĐẠT** | identical — đúng (judge gọi ↘ 'hỏi' thay vì huyền — không ảnh hưởng verdict) |

## Chữ ký

- Kiểm máy bởi: agent ZCode (LLM) — 2026-10-02
- Xác nhận của chủ dự án (nếu reviewer yêu cầu người thật soát lại): ______________

→ E4 khép theo điều kiện 5: judge = công cụ tìm bất đồng, KHÔNG oracle;
  hồ sơ phân xử lưu đầy đủ (session + raw log + provenance + regression flags + biên bản này).