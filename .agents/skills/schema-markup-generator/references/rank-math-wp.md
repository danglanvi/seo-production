# Rank Math trên WordPress: hành vi cần biết khi thêm schema riêng

Đọc file này ở Bước 4–5 khi site dùng Rank Math. Các hành vi dưới đây đã kiểm trên một site WordPress 10/2026, khi thêm schema Course, FAQPage, BreadcrumbList cho trang landing.

- Rank Math in một khối JSON-LD `@graph` cho mỗi trang. Thêm hoặc sửa node bằng filter `rank_math/json_ld` với ưu tiên cao (ví dụ 999). Không in thêm một thẻ JSON-LD thứ hai có `@id` trùng với graph của Rank Math.
- Trang có schema riêng thì bỏ node Article mặc định trong filter. Node này có `@id` kết thúc bằng `#richSnippet`.
- Gộp các trường WebPage riêng vào node `#webpage` có sẵn. Không tạo thêm node WebPage thứ hai.
- Rank Math tự bỏ node Person tác giả khi không còn node nào trỏ tới (`remove_person_entity`). Bỏ Article thì Person tác giả thường mất theo. Cần giữ Person thì để một node còn lại trỏ tới nó.
- `primaryImageOfPage` lấy ảnh đại diện (featured image). Trang không có ảnh đại diện thì Rank Math lấy ảnh đầu tiên trong nội dung. Ảnh đó có thể là đường dẫn tương đối hoặc ảnh GIF base64 giữ chỗ của lazy-load. Đặt ảnh đại diện bằng ảnh OG.
- Rank Math chỉ đọc ảnh OG theo ID attachment (meta `rank_math_facebook_image_id`). File ảnh nằm ngoài thư viện Media thì đăng ký làm attachment trước, rồi ghi ID vào meta này.
- Staging dùng domain production trong `@id` của node gộp thì kết quả staging có thể khác production. Kiểm schema cuối cùng trên production.
