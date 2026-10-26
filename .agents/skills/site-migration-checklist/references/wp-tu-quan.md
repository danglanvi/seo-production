# Thực thi migration trên WordPress tự quản

Đọc file này khi đổi theme, đưa trang HTML tĩnh vào WordPress, hoặc đổi cấu trúc URL trên site có quyền SSH và WP-CLI. Nội dung rút từ một lần đổi theme và đưa 13 trang landing tĩnh vào WordPress (VPS, OpenLiteSpeed, LiteSpeed Cache, Rank Math, 10/2026). Hồ sơ server của dự án: `00-client-context/wp-server.md`.

## 1. Trước khi chuyển

- Dựng staging cùng server và cùng bộ plugin. Staging chưa có DNS công khai thì dùng `curl --resolve` và Basic Auth lấy từ `.agent-secrets/`.
- So danh sách plugin đang bật của staging với production (`wp plugin list --status=active --field=name` ở cả 2 bên, `diff`). Plugin chỉ bật ở production thì bật trên staging trước khi duyệt giao diện. Site mẫu: Fixed TOC tắt trên staging, bật trên production. Lỗi mục lục thô chỉ lộ sau cutover.
- Viết lệnh rollback của từng bước trước khi chạy. Ghi vào `HANDOFF.md` của đợt.
- Backup về máy làm việc: lập danh sách file sẽ ghi đè, rồi `tar` qua SSH. Lưu bản cũ của trang và meta sẽ đổi thành JSON trước khi ghi.
- Chụp baseline của mọi URL: status, title, meta description, canonical, og:image, loại schema. Dùng `seo-drift-tracker` mode baseline.

## 2. Đưa trang HTML tĩnh vào WordPress mà giữ URL

1. Converter đọc gói tĩnh và tách thành:
   - nội dung trang (`post_content`);
   - CSS, JS của trang (vào theme);
   - ảnh (vào `uploads/<thư mục>/`, đặt tên có ngữ cảnh theo `image-seo-optimize` Mode D);
   - meta SEO: title, description, OG, schema riêng;
   - bảng 301 cho URL ảnh và trang cũ.
2. Template trang riêng in nội dung thô: không qua `wpautop`, không nạp CSS, JS không cần.
3. Writer ghi trang bằng `wp eval-file`:
   - Tạo hoặc cập nhật trang theo đường dẫn, đúng trang cha.
   - Ghi `post_content` bằng `$wpdb`. WP-CLI chạy không có quyền `unfiltered_html`, nên `wp_update_post` lọc mất SVG và form.
   - Lưu mã hash của nội dung đã ghi. Lần sau, trang đã sửa trong wp-admin (hash khác) thì bỏ qua, trừ khi có cờ `force`.
4. Kiểm schema sau khi ghi. Rank Math có hành vi riêng: `schema-markup-generator` → `references/rank-math-wp.md`.
5. Thư mục tĩnh còn ở web root thì server phục vụ file tĩnh trước, WordPress không thấy trang. Bước switch là chuyển thư mục tĩnh ra khỏi web root.

## 3. Switch có rollback tự động

1. Chuyển thư mục tĩnh ra ngoài web root, vào thư mục backup.
2. Graceful restart web server: `lswsctrl restart` (OpenLiteSpeed).
3. Curl mọi URL trong danh sách. URL nào khác 200 thì chuyển thư mục về ngay và restart lại.
4. Không xoá thư mục cũ. Giữ ở backup đến khi field data ổn định.

OpenLiteSpeed giữ luật `.htaccess` của một thư mục trong bộ nhớ đến lần restart sau, kể cả khi thư mục đã chuyển đi. Site mẫu có `.htaccess` với `RewriteEngine Off` trong thư mục tĩnh. Sau khi chuyển thư mục, 13 trang trả 404 của server khoảng 3,5 phút, đến khi restart.

## 4. Kiểm trong giờ đầu sau khi chuyển

- Mọi URL trả 200. Title, meta description, canonical đúng.
- og:image trả 200 và đúng ảnh. Schema có đủ loại cần có (ví dụ Course, FAQPage, BreadcrumbList) và không còn node thừa (Article, Person mồ côi).
- URL ảnh và URL trang cũ 301 về URL mới trong một bước.
- Sitemap có URL mới.
- Form: kiểm tự động khi đã chặn endpoint (Apps Script, GTM, GA), để không tạo lead thật. Lead thật do người vận hành gửi thử.
- Không có lỗi JS trên mobile và desktop. Tốc độ đo bằng PSI theo `wp-pagespeed`. Staging không thay được PSI.
- Trang đổi ảnh OG: nhắc người vận hành chạy Facebook Sharing Debugger.
- Plugin hiển thị ở front-end (chấm sao, nút chia sẻ, mục lục, popup): theme mới có thể không nạp CSS, JS của plugin và để lại chữ lẻ. Grep HTML của trang bài tìm class hoặc chuỗi của từng plugin như vậy. Plugin hết chức năng thì tắt theo `wp-security-hardening` (checklist mục 4).
  - Kiểm bằng DOM, không chỉ bằng ảnh chụp: phần tử của plugin có `display` khác `none` và chiều cao lớn hơn 0 là đang hiện. Site mẫu: Fixed TOC chèn nút rỗng và danh sách mục lục cao 200–420 px vào mọi bài. Plugin còn bọc nội dung trong `div#ftwp-postcontent`, nên bộ xử lý nội dung của theme không tìm thấy sapo và mục. Theme mới gỡ markup này khi hiển thị.
- Nội dung cũ có thẻ `<style>` dán trong bài: CSS này áp lên cả trang mới (site mẫu: mọi link thành #00c2ff, chữ 20px, 51 lỗi tương phản ở 1 bài). Quét `post_content` tìm `<style`, `<script`, ảnh hotlink từ domain ngoài. Theme bỏ `<style>` khi hiển thị, ảnh hỏng gỡ khỏi bài có backup.

## 5. Sau khi ổn định

- Chuyển theme cũ và plugin chỉ theme cũ dùng (page builder, ACF của theme) khỏi `wp-content` của production, vào quarantine có `MANIFEST.txt`. Staging giữ bộ cũ để rollback. Option và meta vẫn trong DB.
- Ghi trong hướng dẫn rollback: lấy lại thư mục nào từ quarantine, chạy lại `chown`, theme con nào là bản đúng.

## 6. Bẫy đã gặp

- Upload lại gói tĩnh vào web root sau khi switch sẽ che trang WordPress lần nữa. Ghi luật này vào hướng dẫn deploy của trang.
- Alt và caption của bản tĩnh có thể bị mã hoá 2 lần (`&amp;amp;`). Kiểm chuỗi này sau khi convert.
- Trang con không có og:image riêng (thanh toán, cảm ơn) thì lấy ảnh OG của trang cha.
