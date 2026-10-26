# Phối hợp model: Jev, EmbeddingGemma và model mạnh hơn

Đọc file này trước khi gọi model. Kiến trúc 5 lớp, 10 luật vận hành và bảng ngưỡng nằm ở `tools/ai-assist/README.md` mục 2–4. File này chỉ ghi phần riêng của PageSpeed.

## 1. Hợp đồng chung

- Model chỉ gán nhãn hoặc so khớp. Model không gọi lệnh trên server và không tự kích hoạt thay đổi.
- Luật tất định chạy trước: số đo PSI, `perf_probe.mjs`, `shot_cmp.py`, regex trên HTML. Chỉ gọi model cho phần luật tất định chưa trả lời được.
- Claude (lớp 4) đọc mọi mục dưới ngưỡng và mọi mục sắp dẫn tới thay đổi trên server.
- Mỗi lượt Jev có `--budget`. Báo cáo ghi tổng chi phí.
- Gửi qua Jev chỉ dữ liệu trang công khai: đoạn đầu script, URL tài nguyên, ảnh chụp trang. Không gửi cookie, header Basic Auth, HTML trang đã đăng nhập, dữ liệu form.

## 2. Việc của từng model

| Việc | Model | Input | Ngưỡng hiện hành | Khi nào dùng |
|---|---|---|---|---|
| Gom URL theo template | EmbeddingGemma `emb.py cluster` | Khung HTML đã bỏ chữ | Chưa có ngưỡng chung, hiệu chuẩn theo site | DB không cho biết template |
| Tìm trang lệch template | EmbeddingGemma `emb.py nn` | Khung HTML của URL đại diện và URL cần kiểm | Hiệu chuẩn theo site | Site có nhiều trang dựng tay |
| Gom vấn đề lặp giữa nhiều URL | EmbeddingGemma `emb.py cluster` | Chuỗi mô tả vấn đề của PSI (audit id + phần tử) | Hiệu chuẩn theo site | Trên 30 URL, cần gom nguyên nhân chung |
| Phân loại script cho delay JS | Jev `asset-delay` | Mỗi thẻ script một dòng | Từ 0,7 | Lớp 6 |
| Soát ảnh chụp sau khi sửa | Jev `ui-visual` | Ảnh từng màn hình, không chụp cả trang dài | Câu có/không từ 0,7 thì Claude xem ảnh | `shot_cmp.py` báo lệch điểm ảnh lớn, hoặc trên 20 ảnh cần xem |

- Dạng input của `asset-delay`: mỗi thẻ `<script>` của trang đại diện là một dòng. `state` gồm `page_type` (tên template), `handle` (thuộc tính `id`), `src` (rỗng nếu inline), `attributes`, `size_kb`, `inline_excerpt` (đoạn đầu mã inline). Đặt `id` dạng `<page_type>|<thứ tự>|<src hoặc đoạn đầu mã>`.
- Lệnh chạy Jev và EmbeddingGemma: `tools/ai-assist/README.md` mục 5.
- Dưới ngưỡng `asset-delay`, Claude tự xếp. Lượt hiệu chuẩn 10/2026: `slick.min.js` nhận nhãn sai dưới ngưỡng.
- Jev đề xuất `delay_safe` cho GTM và Hotjar là đúng về kỹ thuật. Việc đổi vẫn cần người duyệt đồng ý (lớp 7).

## 3. Không dùng model cho việc sau

- Quyết định giữ hay bỏ critical CSS. Số đo A/B quyết định.
- Đọc điểm PSI hoặc so trung vị. Script làm việc này chính xác hơn.
- Quyết định A/B khi PSI nhiễu. `psi_decide.py` trả nhãn theo ngưỡng đặt trước.
- Lập bảng phần còn trừ điểm. `psi_con_tru.py` đọc trọng số audit từ JSON.
- Tìm thư viện nạp trùng. Regex trên HTML tìm đủ và không tốn tiền.
- Chọn ảnh LCP. Lighthouse trả phần tử LCP trong JSON.

## 4. Thay bằng model mạnh hơn

Khi có embedding mạnh hơn EmbeddingGemma 2 hoặc phiên bản Jev mới:

1. Chạy lại bộ mẫu hiệu chuẩn bằng model mới. Bộ mẫu là các dòng đã có nhãn Claude duyệt, lưu trong evidence của đợt trước (`asset-delay`: bảng script và vai trò; `ui-visual`: ảnh trước và sau sửa kèm tóm tắt lỗi). Ghi đường dẫn bộ mẫu vào `wp-server.md`.
2. So nhãn của model mới với nhãn Claude đã duyệt. Chọn ngưỡng mà mọi mục đạt ngưỡng đều đúng.
3. Ghi ngưỡng mới, phiên bản rubric và ngày vào `tools/ai-assist/README.md` mục 4.
4. Chỉ đổi `jev.py` hoặc `emb.py` sau khi bước 1–3 xong. Ghim tên model trong script.

Model sinh văn bản mạnh (ví dụ Claude Opus) có thể nhận thêm việc đề xuất:

- Đọc tóm tắt `psi_table.py --detail` của mọi template và đề xuất nhóm nguyên nhân chung.
- Đề xuất danh sách selector giữ lại khi cắt CSS không dùng (UCSS).

Đầu ra của các việc này là đề xuất. `perf_probe.mjs` và `shot_cmp.py` kiểm từng đề xuất trước khi giữ.
