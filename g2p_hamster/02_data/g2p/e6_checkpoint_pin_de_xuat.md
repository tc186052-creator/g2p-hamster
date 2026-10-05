# E6 — ĐỀ XUẤT PIN CHECKPOINT (chờ chủ dự án chốt trước khi tải)

Ngày: 2026-10-02. Theo điều kiện 1 §6 kế hoạch E: **chốt revision TRƯỚC khi
tải** + recipe fail-closed. Đề xuất dưới đây là bản để anh chốt — chưa tải
gì, chưa chạy E6.

## Đề xuất pin

| Hạng mục | Giá trị |
|---|---|
| Weights (checkpoint) | **contextboxai/Kokoro-Vietnamese** |
| Revision (commit) | **`9f210d622209fcc216fe2ac6159fed2ff381cb8a`** |
| License | **Apache-2.0** (khai trên HF) |
| Repo status | không gated · last-modified 2026-06-27 (ổn định ~3 tháng) |
| Code chạy (đã pin từ trước) | `03_vendor/Kokoro-Vietnamese/` — commit `a249afe5555aec6c435165c2f61ec0f71284812f` (iamdinhthuan/Kokoro-Vietnamese) |

Lý do chọn repo này: checkpoint VI duy nhất trong kế hoạch đã khảo sát
(kokoro-style, 82M tham số, có voicepack tiếng Việt); license rõ; khớp
profile kokoro178 mình đã dựng.

## File + sha256 kỳ vọng (LFS oid = sha256 nội dung — đối chiếu sau tải)

Tải ở revision pin qua URL dạng
`https://huggingface.co/contextboxai/Kokoro-Vietnamese/resolve/<revision>/<path>`
— sau tải bắt buộc `sha256sum` khớp bảng dưới, lệch 1 byte = HỦY + dừng
(fail-closed).

**Bắt buộc cho demo (tối thiểu ~328 MB):**

| File | Size | sha256 kỳ vọng |
|---|---|---|
| `config.json` | 2.351 B | (nhỏ — ghi lại giá trị tải về) |
| `kokoro_vi.pth` | 327.224.779 B | `22976e6ac41d6ed9528376f80b33dc2bf171c0ce9cb2c619d21961c15e701fb7` |
| `voices.json` | 1.276 B | (nhỏ — ghi lại giá trị tải về) |
| `voicepacks/my_yen.pt` | 523.746 B | `3edb2f25286b94de9053e123dc45278834925c60b5d2779dde32424a836fd1d7` |

**Tùy chọn giọng thứ 2 cho A/B nghe (mỗi file ~0,5 MB):**
`voicepacks/thanh_dat.pt` `4d30926a819d95a19c7677feee5164314a96c8635ec6ff806398faf0395d6418` ·
`voicepacks/mai_linh.pt` `d8f12f7931618f884705486663951f486001e65aa4ee48633ab086995b57292d`

**Không tải ở demo (ghi trong provenance là "đã pin, không dùng"):**
`kokoro_vi.onnx` (325.731.953 B, `da191277f58633649a9c0d2ae8012e80ef57ea8e2a56e30323c0f7df1ca29087`)
— bản ONNX trùng tham số .pth; 13 voicepack còn lại.

## Recipe fail-closed (khung — viết code khi anh chốt)

1. Tạo `03_vendor/kokoro_vi_weights/` — tải ĐÚNG revision trên, từng file.
2. `sha256sum` từng file → so bảng kỳ vọng → lệch = hủy toàn bộ, không ghi
   provenance, không chạy.
3. Ghi `02_data/g2p/e6_weights_provenance.json`: revision + bảng
   {file, size, sha256 đo được, ngày tải, license} + hash vocab checkpoint.
4. Chỉ sau bước 3 mới chạy demo A/B (5 điều kiện §6: bộ demo cố định, kiểm
   100% token ID ∈ vocab checkpoint, 3 nhánh, phiếu nghe CSV, không MOS).

## Anh cần chốt

- [ ] Chấp nhận revision `9f210d62…` (hoặc chỉ revision khác nếu anh muốn).
- [ ] Giọng chính demo: `my_yen` (đề xuất) / `mai_linh` / `thanh_dat`.
- [ ] Chấp nhận Apache-2.0 cho weights (không phân phối lại — chỉ chạy nội bộ).
