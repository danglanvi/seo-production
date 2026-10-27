# Luật bài web khi xuất bản

Luật chung cho bài blog. Luật riêng của từng site nằm trong `luat_rieng` của profile và thắng luật chung khi hai luật vênh nhau.

## Cấu trúc

- Đúng một H1. `md_to_html.py` đặt H1 trong `header.hd`. WordPress hiển thị tiêu đề bài làm H1, nên `wp_publish.py` bỏ `header.hd` khỏi thân bài.
- Đoạn đầu (class `lead`) trả lời thẳng câu hỏi của H1 trong 2–3 câu.
- Mỗi H2 có một hình, bảng hoặc khối bấm. Hình bổ sung cho chữ, không thay chữ.
- Bảng nằm trong `<div class="tbl wide">` để cuộn ngang trên điện thoại thay vì làm tràn trang.
- FAQ dùng H3 cho từng câu hỏi. Câu trả lời đầu tiên trả lời thẳng.

## Link

- Link nội bộ đặt ở câu có ngữ cảnh khớp trang đích. Anchor tả trang đích, không dùng "tại đây".
- Link tới bài chưa đăng: bỏ thẻ `<a>`, giữ chữ, ghi vào `link-cho.md`. Khi bài đích lên, thêm link rồi chạy lại `wp_publish.py push`.
- Link đích chuyển hướng: trỏ thẳng URL cuối.
- Link ra ngoài theo `link_ngoai` của profile. Khi là `chu-thich`, mỗi nguồn có một số `[n]` có tooltip tên nguồn, và mục nguồn cuối bài ghi URL dạng chữ.
- Không đặt link trong H1, H2.

## Brand

- Chữ ký thương hiệu (`chu_ky`) đúng một lần, sau kết luận hoặc CTA, trước mục nguồn.
- Không nhắc brand trong `brand_khac`. Không dùng social proof, client hay học viên của brand khác.
- Không tự thêm cam kết hoàn tiền hoặc bảo đảm kết quả.
- Case có số liệu của khách: che tên và domain khi luật site yêu cầu. Che bằng khối màu đặc, không làm mờ.

## Meta

- `meta_title` dùng làm SEO title. Đo pixel bằng `serp_pixel.py` khi repo có. Không có script thì giữ dưới 60 ký tự.
- `meta_description` dưới 160 ký tự, chứa keyword chính, nói người đọc nhận được gì.
- `url_slug` ngắn, không dấu, chứa keyword chính. Slug tự sinh từ H1 thường quá dài.
- Một chuyên mục chính. Không tạo chuyên mục hay thẻ mới khi chưa hỏi SEO Leader.

## Tốc độ

- Ảnh có `width`, `height`, `loading="lazy"`, `decoding="async"`. `chen_media.py` tự thêm.
- Sơ đồ dùng SVG inline 2 bản (desktop và điện thoại), không dùng ảnh PNG có chữ.
- Video YouTube dùng facade: ảnh xem trước, iframe chỉ tạo khi bấm.
- Không nhúng font, thư viện JS hay CSS framework riêng cho một bài.
