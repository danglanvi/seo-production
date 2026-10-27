# Nhận khách mới: quyền server và dữ liệu Google

Đọc khi dự án cần vào hosting của khách (SSH, WP-CLI) hoặc đọc GSC, GA4 bằng tài khoản khác tài khoản chính của Lead. Quy trình rút từ lượt nhận site khách WooCommerce trên shared hosting cPanel ngày 27/10/2026. Kết quả lượt đó: SSH bằng khoá riêng, WP-CLI đủ quyền admin, rà bảo mật, tốc độ và crawl chỉ đọc trong cùng ngày.

## 1. Secret của khách

1. Tạo một file secret riêng cho khách trong thư mục secret của máy, ngoài repo: `<nhà cung cấp>_<slug>_credentials_<YYYY-MM-DD>.env`. Workspace đầy đủ dùng `.agent-secrets/`. Đặt quyền 600.
2. Agent điền sẵn các trường không bí mật: URL panel, user, host, IP, nameserver, cổng SSH.
3. Người dùng tự dán mật khẩu từ ghi chú gốc. Agent không gõ lại mật khẩu đọc từ ảnh: ký tự dễ nhầm (`l`/`I`, `0`/`O`), và cPanel khoá IP sau vài lần đăng nhập hỏng.
4. Không ghi mật khẩu, khoá hay token vào repo instance, báo cáo hay chat. Hồ sơ `wp-server.md` chỉ ghi tên file secret và tên biến.

## 2. SSH bằng khoá riêng

1. Tạo khoá riêng cho khách: `ssh-keygen -q -t ed25519 -N '' -C '<người hoặc agent>-<slug>-<ngày>' -f <thư mục secret>/<nhà cung cấp>-<slug>_ssh_ed25519`, rồi `chmod 600`.
2. cPanel: đăng nhập bằng phiên (`/login/?login_only=1` trả `security_token`), gọi API2 module `SSH`: `importkey` với khoá công khai, rồi `authkey` với `action=authorize`. Đăng xuất và xoá file cookie ngay sau đó. Panel khác hoặc VPS: Lead thêm khoá công khai vào `authorized_keys` của user được cấp.
3. Thử kết nối không mật khẩu: `ssh -i <khoá> -p <cổng> -o BatchMode=yes <user>@<host> 'id; wp --info | head -3'`. Nhà cung cấp có thể dùng cổng khác 22. Ví dụ site mẫu 27/10/2026: cổng 2210, shell `/bin/bash`.
4. Ghi alias, cổng, đường dẫn khoá và lệnh WP-CLI vào `00-client-context/wp-server.md`.

## 3. Đo quyền trước khi chọn skill

Chạy chỉ đọc và ghi kết quả vào `wp-server.md`:

| Quyền | Lệnh kiểm | Nếu thiếu |
|---|---|---|
| root, sudo | `sudo -n true` | Bỏ việc cấp server của `wp-host-optimize` và `wp-security-hardening`. Việc cấu hình web server, PHP, firewall: gửi yêu cầu cho nhà cung cấp |
| Ghi `/etc` | `touch /etc/x` | Như trên |
| WP-CLI quyền admin | `wp user list --role=administrator --field=user_login` | Dùng đường REST hoặc kit đăng bài |
| Dump DB | `mysqldump --no-data <db> > /dev/null` | Backup bằng công cụ của panel |
| Ghi `public_html`, `.htaccess`, `wp-config.php` | `test -w .htaccess` | Chỉ rà, không sửa |
| Cron | `crontab -l` | WP-Cron giữ qua HTTP |
| Access log | `ls ~/access-logs ~/logs` | `seo-logfile-analysis` thiếu dữ liệu: xin log từ nhà cung cấp |

Shared hosting thường có WP-CLI, dump DB, ghi file và cron, nhưng không có root. Rà bảo mật vẫn chạy đủ phần cấp site, gồm `tim_file_lo.sh` của `wp-security-hardening`.

## 4. GSC và GA4 bằng tài khoản Google khác

GSC và GA4 của khách thường cấp cho một tài khoản Google khác tài khoản chính của Lead.

- `gws` dùng một thư mục cấu hình cho mỗi tài khoản: đặt `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-<tên>` và `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`. Chạy `gws auth status` trước mỗi lượt gọi, vì tên thư mục có thể không khớp tài khoản đã đăng nhập.
- OAuth client và tài khoản đăng nhập tách nhau. Project chứa OAuth client chỉ cần bật API (Search Console API, Analytics Data API, Analytics Admin API) và màn hình đồng ý. Tài khoản đăng nhập không cần quyền trên project.
- App OAuth ở chế độ In production, loại External: mọi tài khoản Google đăng nhập được. Không bấm "Back to testing": refresh token của mọi người dùng client đó hết hạn sau 7 ngày. Không bấm "Make internal".
- Bước bấm "Cho phép" trên trình duyệt do người giữ tài khoản làm. Agent không đăng nhập thay.
- Công cụ GSC có cache token dùng chung (`tools/gsc/gsc.sh` lưu ở `~/.cache/gsc-cli/`): xoá cache trước và sau khi đổi tài khoản, nếu không sẽ gọi nhầm tài khoản.
- Đối chiếu property GA4 với measurement ID trong HTML trang chủ trước khi lấy số. Lỗi đã gặp 27/10/2026: tài khoản thấy property cũ có 0 phiên trong 90 ngày, còn site gửi dữ liệu về property khác.
- Ghi tài khoản nào đọc được property nào vào `00-client-context/` của instance, không ghi token.

## 5. Kiểm trước khi bắt đầu việc

- [ ] File secret quyền 600, nằm ngoài repo.
- [ ] SSH bằng khoá chạy được với `BatchMode=yes`.
- [ ] `wp-server.md` có bảng quyền ở mục 3 và mục tầng cache 2b.
- [ ] Tài khoản Google đọc được đúng property GSC và GA4 đang nhận dữ liệu.
