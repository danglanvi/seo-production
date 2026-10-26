# Đổi tên ảnh đã đăng trên site

Đọc file này khi chạy Mode D. Mode D dùng khi ảnh đã lên web với tên thiếu ngữ cảnh (`lac-hong.webp`, `IMG_2034.jpg`, `anh-1.png`). Mục tiêu là đổi sang tên có ngữ cảnh mà không làm vỡ ảnh trong trang, link ngoài, ảnh tìm kiếm và ảnh chia sẻ mạng xã hội.

Site mẫu 10/2026 (WordPress, OpenLiteSpeed): 271 file ở 16 trang đổi tên, 284 URL cũ 301 về tên mới. Sau khi đổi, các trang không còn link ảnh vỡ.

## 1. Quy tắc tên

- Ghép tên theo thứ tự: loại ảnh (nếu có), entity viết đủ, ngữ cảnh. Ví dụ: `logo-dai-hoc-lac-hong.webp`, `<ten-nguoi>-giang-vien-chan-dung.webp`, `<ten-nguoi>-talkshow-dai-hoc-hoa-sen-hoi-truong.webp`.
- Viết đủ tên riêng. Viết `dai-hoc-lac-hong`, không viết `lac-hong` hay `dhlh`. Tên riêng nhiều tiếng tính là một cụm trong ngưỡng 3–5 cụm của Bước 3.
- Không dấu, chữ thường, nối bằng gạch ngang, giữ đuôi file.
- Dùng số thứ tự chỉ cho chuỗi ảnh cùng ngữ cảnh: `-01`, `-02`.
- Hai file cũ không được ra cùng một tên mới. Script đổi tên phải dừng khi gặp trùng.

## 2. Quy trình trên site có quyền server

1. Kiểm kê mọi chỗ dùng ảnh:
   - Nội dung trang (`post_content`).
   - Meta: ảnh OG, ảnh đại diện, trường ACF hoặc Elementor.
   - CSS (`background-image`), file theme, schema JSON-LD.
   - Nguồn build, nếu trang dựng từ file nguồn. Sửa ở nguồn build. Nếu chỉ sửa DB, lần build sau đưa tên cũ trở lại.
2. Lập bảng `URL cũ → URL mới` dạng JSON. Đường dẫn tính từ web root, ví dụ `"/wp-content/uploads/a/lac-hong.webp": "/wp-content/uploads/a/logo-dai-hoc-lac-hong.webp"`.
3. Chép file sang tên mới. Giữ file tên cũ tại chỗ đến khi kiểm xong.
4. Sửa mọi chỗ dùng ảnh sang tên mới. Deploy lên staging rồi kiểm.
5. Cài 301 bằng `templates/mu-plugin-301-anh.php` và bảng JSON. Mu-plugin chỉ redirect khi URL cũ trả 404. Không viết hàng trăm dòng redirect trong `.htaccess`.
6. Kiểm server chuyển request file thiếu trong `uploads/` vào WordPress. Cách kiểm: tạm đổi tên một file thử, rồi `curl -sI` URL đó. Kết quả phải là 404 của theme, không phải 404 của server. Nếu server tự trả 404, thêm rule `!-f` chuyển vào `index.php` (OpenLiteSpeed cần restart sau khi sửa `.htaccess`).
7. Deploy production và purge cache.
8. Cách ly file tên cũ bằng `scripts/anh_cach_ly.sh <ssh alias> <web root> <bảng JSON> cach-ly`. Script chỉ chuyển file cũ khi file mới đã có. Lệnh trả lại: `... tra-lai`. Không xoá file.
9. Kiểm sau khi cách ly:
   - Mọi URL mới trả 200.
   - Lấy mẫu URL cũ: phải 301 về URL mới, URL mới trả 200.
   - HTML các trang không còn tên cũ: `curl -s <trang> | grep -c <tên cũ>` ra 0.
   - Ảnh OG và ảnh đại diện trỏ đúng file mới.
10. Ảnh OG đổi tên: nhắc người vận hành chạy Facebook Sharing Debugger cho các URL bị ảnh hưởng, để mạng xã hội lấy ảnh mới.

## 3. Ảnh trong thư viện Media của WordPress

- WordPress lưu file của attachment trong meta `_wp_attached_file` và các cỡ con trong `_wp_attachment_metadata`. Đổi tên một attachment phải đổi file gốc, mọi cỡ con và 2 meta này cùng lúc.
- Cách ít rủi ro hơn: tải ảnh lên thành attachment mới với tên mới, thay mọi chỗ dùng, rồi 301 URL file cũ theo mục 2.
- Rank Math đọc ảnh OG theo ID attachment. Ảnh OG mới phải là attachment, và meta OG phải trỏ đúng ID mới.

## 4. Bẫy đã gặp

- Script build sinh lại tên cũ. Site mẫu cho bước build đổi tên bằng một bảng map, nên nguồn giữ tên cũ mà output mang tên mới.
- Ảnh nền trong CSS dễ sót. Grep cả file CSS và chuỗi `url(`.
- Ảnh trong thư mục tĩnh có `.htaccess` riêng: OpenLiteSpeed giữ luật của thư mục đến lần restart sau, kể cả khi thư mục đã chuyển đi.
- Cache trang còn HTML cũ: purge sau mỗi lần deploy.
