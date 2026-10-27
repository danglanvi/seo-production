# Tài khoản team và 2FA bắt buộc (nhánh D)

Quy trình đã chạy thật ngày 27/10/2026 trên 2 site WordPress (VPS aaPanel, OpenLiteSpeed): staging rồi production, bộ kiểm 25/25, 26/26, 30/30, 30/30. Mẫu ở `templates/tai-khoan-team/`, bộ kiểm `scripts/team_accounts_check.py`.

## 1. Lead quyết trước khi dựng

| Câu hỏi | Mặc định đã dùng |
|---|---|
| Tác giả hiển thị của bài team | Một tài khoản team, ví dụ "<Brand> Team". Bài của role team tự đứng tên tài khoản này |
| Team đăng thẳng hay qua duyệt | Đăng thẳng |
| Cấu trúc tài khoản | Lead hoặc chủ site là Administrator. Một SEO Leader. Nhiều Người đăng bài do SEO Leader tạo |
| Hộp thư nhận mã 2FA của tài khoản dùng chung | Một hộp thư có người theo dõi hằng ngày. Hộp thư không ai đọc thì người đăng nhập không nhận được mã |
| Tài khoản `admin` hoặc tên dễ đoán | Đổi tên đăng nhập và email |

## 2. Hai role của mẫu

| Role | Làm được | Không làm được |
|---|---|---|
| `seo_leader` (SEO Leader) | Quyền Editor, Rank Math trừ Role Manager và `.htaccess`, tạo và xoá tài khoản Người đăng bài | Plugin, theme, cài đặt site, tài khoản admin |
| `team_writer` (Người đăng bài) | Viết, đăng thẳng, sửa mọi bài đứng tên team, tải ảnh, title và meta Rank Math | Page, bài đứng tên người khác, `unfiltered_html` (không chèn được `<script>`) |

Người thật tạo bài được ghi ở meta `_team_writer`, vì tác giả hiển thị là tài khoản team.

## 3. Các bước

1. Backup bảng `users`, `usermeta`, `options` và thư mục `mu-plugins`, qua `verify_backup.sh`.
2. Cài plugin Two Factor từ wordpress.org trên staging. Kiểm checksum: `wp plugin verify-checksums two-factor`.
3. Dựng mu-plugin từ `team-accounts.php.tpl`: thay `{{BYLINE_ID}}`, `{{BYLINE_NAME}}`, `{{NGAY_DUYET}}`. Chạy `php -l`.
4. Chép mu-plugin lên staging. Tạo mã dự phòng cho từng admin: `Two_Factor_Backup_Codes::get_instance()->generate_codes( $user )`. Lưu mã vào `.agent-secrets/<site>-2fa-backup.txt`, chmod 600.
5. Chạy bộ kiểm trên staging: `python3 -I skills/wp-security-hardening/scripts/team_accounts_check.py --cfg <site-stg.json> --http --rest --out <ev>/test_<site>-stg.txt`. Cấu hình mẫu ở đầu script. Staging có Basic Auth thì bỏ `--rest`.
6. Mọi dòng PASS thì lên production cùng các bước 2–4, rồi chạy bộ kiểm production. Bộ kiểm production chỉ tạo bài nháp rồi xoá. Bài publish sẽ kích hoạt purge CDN, sitemap và ping.
7. Thu hồi app password cũ không còn dùng. Gọi thử app password của pipeline còn giữ: phải trả 200 sau khi bật 2FA.
8. Kiểm `stderr.log` của web server không có lỗi PHP mới. Trang chủ và blog trả 200.
9. Cập nhật sổ truy cập theo mục 4.

## 4. Sổ truy cập giao cho người dùng

- Sổ nằm trong `.agent-secrets/`, chmod 600. Mở cho người dùng bằng app trên máy (TextEdit). Không in nội dung ra chat.
- Lấy URL đăng nhập từ cấu hình đang chạy, không lấy từ file credentials cũ. Plugin ẩn đăng nhập lưu slug trong option, ví dụ `whl_page`. Thử URL trả 200 và có form đăng nhập trước khi giao. Lỗi đã gặp 27/10/2026: sổ lấy URL từ file ngày 16/10, trong khi slug đã đổi ngày 17/10 và 20/10, người dùng không đăng nhập được.
- Mỗi site một khối, theo thứ tự: URL đăng nhập, tên đăng nhập, mật khẩu, email nhận mã 2FA, vị trí file mã dự phòng. Panel hosting để khối riêng bên dưới.
- Cấp app password cho từng người, tên dạng `<Tên> - <máy>`. File gửi riêng một người đặt tên `chia-se_<người>_<site>_<ngày>.txt`.

## 5. Bẫy

- Two Factor bắt chờ tăng dần sau mỗi mã sai. Nhập mã đúng ngay sau mã sai vẫn bị từ chối. Bộ kiểm chờ 5 giây.
- `Two_Factor_Backup_Codes::generate_codes()` là hàm instance: gọi qua `get_instance()`.
- App password vẫn chạy khi tài khoản bật 2FA. REST bằng mật khẩu đăng nhập phải trả 401.
- Web không đọc được `mu-plugins/` khi site đã chặn theo checklist hardening. Asset của mu-plugin đặt ở thư mục riêng trong `wp-content/`.
- Staging chỉ vào qua tunnel SSH thì đặt `base` là `http://127.0.0.1:<cổng>` và `host_header` là host staging.
- Tài khoản dùng làm byline đang là Administrator: đề xuất hạ xuống Author và khoá đăng nhập. Lead quyết.
- Tên đăng nhập trùng slug tác giả công khai (`/author/<tên>/`) lộ tên đăng nhập. Đổi tên đăng nhập, giữ slug tác giả.
