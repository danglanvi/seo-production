# Chế độ audit đầu workstream

File này ghi cách chạy cổng ở mốc đầu của một workstream web, trước khi sửa giao diện, theme hay nội dung hàng loạt. Chế độ này đo mọi lớp trên mẫu template, trình vấn đề lớn, và ghi phần còn lại vào backlog. Chế độ kiểm sau ghi (mặc định) chỉ trả lời "lần ghi vừa rồi có làm hỏng gì không".

Lỗi đã gặp: site agency mẫu 18/10/2026, Claude thấy lỗi UX và semantic HTML trong lúc làm, nhưng xếp hết vào giai đoạn sau và không báo. Người duyệt so với đề xuất của một agent khác và phải hỏi lại. Dựng audit bù mất 20 phút.

## Danh sách URL

- Lấy 1 URL cho mỗi template, cộng trang có form, trang có slider và cặp ngôn ngữ nếu site có bản dịch.
- Không lấy cả sitemap. Lỗi theo template lặp trên mọi trang cùng template.
- Khai khối `interact` đủ: `menu_toggle`, `sliders`, `changed_selectors` (link thân bài, nút, link menu, link footer), `kit_button_colors`, `pairs`, `landmarks`.

## 6 lớp đo

| Lớp | Đo bằng | Ghi chú |
|---|---|---|
| 1. Landmark và semantic HTML | Hạng mục 14e; `truoc_production.py controls` | Đếm trên DOM đã render, không dùng regex trên HTML thô. |
| 2. Tràn ngang | Hạng mục 1 với `widths` 360, 390, 768, 800, 900, 1024, 1366 và `--cache both` | Các mốc 768, 800, 900 hay có lỗi giữa hai breakpoint. |
| 3. Axe | Hạng mục 2 | Ghi phiên bản và sha256 của `axe.min.js` vào báo cáo, để lượt sau so cùng bản axe. |
| 4. PageSpeed 5 category | Skill `wp-pagespeed` | Cổng này không đo tốc độ. |
| 5. Điều khiển | Hạng mục 13a (hamburger vô hình); `controls` (`div` có onclick, menu `href="#"`, link và nút không tên); luật axe `link-name`, `button-name` | Lỗi điều khiển chặn người dùng bàn phím và crawler. |
| 6. Trạng thái | Hạng mục 13c | Ép `:hover`, `:visited`, `:focus`, `:active` bằng CDP. |

Lệnh mẫu:

```bash
python3 -E skills/web-qa-gate/scripts/qa_gate.py run --config <ev>/qa.json --out <ev>/audit-dau-<YYYYMMDD-HHMM> --cache both --tabs 3
python3 -E skills/web-qa-gate/scripts/truoc_production.py controls <ev>/audit-dau-<YYYYMMDD-HHMM>
python3 -E skills/web-qa-gate/scripts/truoc_production.py skeleton <ev>/audit-dau-<YYYYMMDD-HHMM>
shasum -a 256 ~/.cache/web-qa-gate/axe.min.js
```

Site nhiều template: chạy `--plan` trước để xem số lượt đo. Danh sách dài: dùng `--sample` cho lượt rà nhanh, nhưng kết luận của audit lấy từ lượt đủ URL.

## Trình kết quả

1. Đo hết 6 lớp. Không bỏ lớp nào vì lớp đó "thuộc giai đoạn sau".
2. Xếp mỗi phát hiện vào "vấn đề lớn" hoặc "vấn đề nhỏ" theo bảng dưới.
3. Trình vấn đề lớn trước, kèm số đo và ảnh, kể cả khi việc sửa nằm ngoài giai đoạn hiện tại.
4. Ghi vấn đề nhỏ vào backlog của workstream. Mỗi dòng có lớp, template, số trang bị, số đo.
5. Nếu dự án có luật trình riêng trong `00-client-context/`, áp luật đó.

| Vấn đề lớn | Vấn đề nhỏ |
|---|---|
| Chặn điều hướng hoặc chuyển đổi: menu mobile, form, CTA chính, slider chính | Lỗi chỉ ở một trang |
| Chặn index hoặc hiển thị trên Google: noindex, canonical sai, mã 4xx hay 5xx, `main` hoặc h1 sai | Lệch thẩm mỹ không chặn thao tác |
| Lặp trên mọi trang của một template | WARN chưa xác nhận bằng ảnh |
| Axe mức critical hoặc serious; tràn ngang ở bề rộng mobile | |

Mỗi vấn đề ghi: lớp, template, số trang bị, số đo, đường dẫn ảnh, giai đoạn dự kiến sửa. Skill này không sửa. Lỗi giao diện sửa theo skill `wp-ui-fix`.

Bẫy:

- `controls` báo cả onclick có chủ ý, ví dụ link mà site cố ý ẩn khỏi crawler bằng JS. Ghi lý do một lần trong backlog, không báo lại ở mỗi lượt. Lượt thử 25/10 trên HTML đã lưu của site agency mẫu: 8/8 trang có 10–15 phần tử onclick loại này.
- `controls` đọc HTML server. Link và nút không tên trong HTML server vẫn có thể được JS gắn tên sau khi tải. Axe trên DOM đã render là phép đo chặn.
