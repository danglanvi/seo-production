# Checklist hardening theo lớp

Đọc file này ở Bước 4. Mỗi mục có cách làm, cách kiểm và rollback. Cột "Duyệt" ghi mục nào cần người duyệt đồng ý riêng, ngoài phạm vi chung của đợt.

## 0. Lệnh theo stack

| Việc | OpenLiteSpeed (aaPanel, CyberPanel) | Apache (cPanel, DirectAdmin) | Nginx |
|---|---|---|---|
| Rule chặn đường dẫn | `.htaccess`, chỉ phần rewrite có tác dụng | `.htaccess` (`RewriteRule`, `<Files>`) | Khối `location` trong server block |
| Header bảo mật | `extraHeaders` trong khối `context /` của vhost | `Header set` trong `.htaccess` hoặc vhost | `add_header` trong server block |
| Áp cấu hình | `lswsctrl restart` (gom thay đổi vào một lần) | Không cần restart với `.htaccess` | `nginx -t` rồi `systemctl reload nginx` |
| User chạy PHP | `www` (aaPanel) hoặc user của site | User cPanel của site | `www-data` hoặc user pool PHP-FPM |
| Log web | `/www/wwwlogs/` (aaPanel) | `~/logs/`, `/var/log/apache2/` | `/var/log/nginx/` |

Ghi stack và đường dẫn thật của site vào `00-client-context/wp-server.md`.

## 1. Web server

| Mục | Cách làm | Kiểm | Duyệt |
|---|---|---|---|
| Chặn PHP trong uploads, languages, upgrade | `RewriteRule ^wp-content/(uploads\|languages\|upgrade\|upgrade-temp-backup)/.*\.(php[0-9]?\|phtml\|phar\|pht)(/.*)?$ - [F,L,NC]`. Cửa hậu đã gặp trong `languages` (10/2026). File dịch `.l10n.php` vẫn nạp qua filesystem | Path `.php`, `.PHP`, `.php/a` ở 3 thư mục trả 403. 404 hoặc 410 nghĩa là rule chưa có: theme đang trả lời | Không |
| Chặn XML-RPC | `RewriteRule ^xmlrpc\.php$ - [F]` | GET, POST `system.listMethods` trả 403 | Không, sau khi grep plugin dùng XML-RPC (Jetpack, app di động) |
| Chặn file nhạy cảm | `^wp-config`, `\.(bak\|old\|orig\|sql\|tar\|tgz\|gz\|7z\|swp\|log)$`, `^\.user\.ini$`, `readme\.html`, `license\.txt` → 403 | `exposure_check.sh` | Không |
| Chặn log plugin | `^wp-content/uploads/(wc-logs\|woocommerce_uploads)/` → 403 | Tải file Woo vẫn chạy (Woo dùng PHP đọc file) | Không |
| Chặn thư mục mu-plugin | `RewriteRule ^wp-content/mu-plugins/ - [F,L]`. Trước đó grep HTML các trang: không có URL nào trỏ vào `mu-plugins/` | File JSON, PHP trong mu-plugin trả 403, trang vẫn 200 | Không |
| Chặn `wp-activate.php`, `wp-signup.php` khi site không có thành viên | Rule 403/404, hoặc mu-plugin trả 404 | Không còn 302 sang slug đăng nhập | Không |
| Header bảo mật | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` theo dòng "Header" ở mục 0 | `curl -sI` trên HTML, file tĩnh, 301, 403 | Restart web server: giờ thấp điểm |
| HSTS | `Strict-Transport-Security "max-age=31536000"` ở `extraHeaders` của vhost, tăng `max-age` dần theo `references/ap-config-song.md` mục 3. Thêm `includeSubDomains` chỉ khi mọi subdomain có HTTPS | `curl -sI` | Có |

- Áp khối rule bằng `scripts/apply_server_block.sh` theo `references/ap-config-song.md` mục 2. Script đặt khối đầu `.htaccess`, bọc bằng dòng BEGIN và END kèm ngày, backup bản cũ ngoài web root và sinh `rollback.sh`.
- aaPanel có thể ghi lại file vhost khi đổi PHP hoặc cấu hình trong panel. Sau mỗi lần đổi, kiểm lại header.
- Sau khi sửa: áp cấu hình theo mục 0, rồi `sitecheck.sh`.
- Mã 410 chỉ dành cho URL trong danh sách bỏ đã duyệt. URL ngẫu nhiên, URL gõ sai và link hỏng trả 404. Nếu theme trả 410 cho path lạ, báo `technical-seo-audit`. Luật trả mã nằm ở dòng Status hygiene trong Bảng ngưỡng của `skills/seo-logfile-analysis/SKILL.md` (v1.3).

## 2. `wp-config.php` và PHP

| Mục | Cách làm | Kiểm |
|---|---|---|
| Chặn sửa file trong admin | `define('DISALLOW_FILE_EDIT', true);` | Menu Theme File Editor biến mất |
| Quyền file | `chmod 640`, owner là user chạy PHP | `stat -c '%a %U'` |
| Salt | 8 khoá + `WP_CACHE_KEY_SALT`, mỗi site riêng | So với backup: khác hết. Huỷ session admin |
| `WP_DEBUG` | Tắt trên production, không define 2 lần | Không có notice trong log mỗi request |
| `disable_functions` | `exec, system, passthru, shell_exec, proc_open, popen` | `php -i` của bản PHP chạy site |
| `open_basedir` | Webroot + `/tmp` cho từng vhost | Như trên |
| `.user.ini` | Khoá bất biến (`chattr +i`), chặn truy cập từ web | `exposure_check.sh` |

## 3. WordPress (mu-plugin bảo mật)

Mẫu: `templates/mu-plugin-security.php`. Mu-plugin chạy cả khi đổi theme hoặc tắt plugin. Chép vào `wp-content/mu-plugins/`, kiểm `php -l` trên server trước, rồi `sitecheck.sh`.

- Chặn đăng ký và đặt `default_role` = `subscriber`, kể cả khi option bị đổi.
- Tắt XML-RPC, pingback, trackback ở mức ứng dụng.
- Khách không liệt kê được user: REST `/wp/v2/users` (filter priority 99, vì ACF Pro xoá kết quả filter chạy trước nó), `?author=`, `?author_name=`, oEmbed, sitemap user.
- Ẩn version: thẻ generator, tham số `ver=` (thay bằng mã băm).
- Khách vào `wp-admin`, `wp-signup.php`, `wp-activate.php` nhận 404, không redirect ra slug đăng nhập ẩn.
- Form và bình luận: ô bẫy, giới hạn số lần gửi theo IP. Giới hạn theo `REMOTE_ADDR` sai khi bật proxy (Cloudflare) mà chưa cấu hình IP thật ở web server.
- Bỏ `unfiltered_html` cho người không phải admin, sau khi thử pipeline content dùng role Editor.
- Site có chức năng thành viên (WooCommerce tài khoản, khoá học): tắt phần chặn đăng ký và `wp-signup.php` trong mẫu.

## 4. Plugin và core

- Cập nhật core minor ngay. Major và PHP major: làm trên staging trước, ghi rollback.
- Mỗi plugin: so version với wordpress.org, tra CVE trên Wordfence Intelligence hoặc WPScan, ghi bản cuối còn hỗ trợ core đang chạy.
- Plugin bị wordpress.org đóng, plugin không licence: ghi rủi ro, đề xuất thay bằng code tự viết hoặc gỡ.
- Wordfence (nếu dùng): bật firewall chế độ bảo vệ, Extended Protection qua `auto_prepend_file` ở vhost, quét plugin và theme, email cảnh báo về hộp thư có người đọc. Kiểm `loginSec_disableApplicationPasswords` sau khi bật, vì pipeline REST dùng app password.
- Pipeline content dùng user Editor + application password, không dùng Administrator.
- Plugin còn bật nhưng hết chức năng, thường gặp sau khi đổi theme: tắt plugin, giữ dữ liệu trong DB. Đổi giao diện nên cần người duyệt. Ví dụ đã gặp: theme mới không nạp CSS, JS của plugin chấm sao, dưới bài chỉ còn dòng chữ "2.4/5 - (408 bình chọn)".
  1. Grep theme và mu-plugin tìm hàm, shortcode của plugin. Nếu theme gọi hàm của plugin, tắt plugin sẽ gây lỗi fatal.
  2. Lưu `wp option get active_plugins --format=json` vào thư mục backup.
  3. `wp plugin deactivate <slug>`, rồi purge cache.
  4. Kiểm: trang bài trả 200, HTML không còn chuỗi hoặc class của plugin, error log không có fatal.
  5. Rollback: `wp plugin activate <slug>`.
- Theme, plugin không dùng: chuyển khỏi `wp-content` vào quarantine, kèm `MANIFEST.txt` ghi đường dẫn gốc. Code PHP nằm trong `wp-content` vẫn gọi được từ web. Giữ một theme mặc định làm dự phòng. Staging giữ bộ cũ để rollback.

## 5. Đăng nhập

| Mục | Cách làm | Duyệt |
|---|---|---|
| Slug đăng nhập ẩn | Chuỗi ngẫu nhiên, lưu trong `.agent-secrets/`. Chặn mọi đường dẫn tiết lộ slug | Có (đổi slug ảnh hưởng người dùng) |
| 2FA admin | Mỗi admin tự quét QR, lưu recovery code. Đủ admin thì bật bắt buộc | Có |
| Slug tác giả | Khác tên đăng nhập | Có |
| Khoá sau số lần sai | Tối đa 5 lần | Có |
| Admin thừa | Liệt kê, chủ site quyết | Có |

## 6. Server

| Mục | Cách làm | Kiểm | Duyệt |
|---|---|---|---|
| SSH | `/etc/ssh/sshd_config.d/01-hardening.conf`: `PermitRootLogin prohibit-password`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `MaxAuthTries 3`, `X11Forwarding no`. Kiểm dòng `Include` đứng trước `PermitRootLogin yes` | `sshd -t`, `sshd -T`; đăng nhập bằng mật khẩu bị từ chối; terminal panel vẫn vào bằng key | Không, nếu giữ phiên SSH đang mở khi đổi |
| Firewall | Mặc định chặn vào. Chỉ mở 22, 80, 443, cổng panel. Đồng bộ bảng firewall của panel | `nc -z` từ ngoài | Có khi đóng cổng đang dùng |
| Panel hosting | 2FA, BasicAuth, giới hạn IP nếu có IP tĩnh, tắt API không dùng, cập nhật | Panel trả 200 với UA trình duyệt | Có |
| FTP | Tắt FTP nếu không dùng. Dùng SFTP chỉ key, chroot theo thư mục site | Cổng 21 đóng | Có |
| MySQL, trang quản trị web server | Bind 127.0.0.1 | `ss -tlnp` | Có (restart MySQL) |
| Vá OS, vá PHP | Theo `references/va-os-php.md`: `apt-get update` trước khi đếm gói, apt qua `systemd-run`, bảng site → handler PHP | `uname -r` là kernel mới, các site 200, `readlink /proc/<pid lsphp>/exe` là binary đã vá | Reboot: giờ thấp điểm. Đổi handler mặc định, tắt php-fpm: có |
| Tự cài bản vá | `unattended-upgrades` cho nguồn security | `APT::Periodic::Unattended-Upgrade "1"` | Có |
| Log | Tăng thời gian lưu log web, syslog, journald bền | Cấu hình logrotate | Không |
| Backup tự động | Mẫu `templates/backup-tu-dong/`: DB mỗi ngày 14 slot, file mỗi tuần 2 slot, slot mới ghi đè slot cũ nên script không xoá file. Server không có `zstd` thì script nén bằng `gzip`. Máy làm việc kéo bản ngoài server bằng `backup_pull.sh`: dùng rsync, server không có rsync thì kéo bằng tar qua SSH. Đặt lịch trên Mac chạy liên tục bằng `cai-lich-pull-mac.command` (launchd) | Chạy tay 1 lần: `scripts/verify_backup.sh` đạt trên bản DB và bản file (dump có "Dump completed", đủ số bảng, nén đọc được); `LAST_OK_db` mới | Có |

Hosting dùng chung (không có root): bỏ mục 6 và các dòng cần vhost. Ghi giới hạn vào báo cáo và đề xuất việc cho nhà cung cấp hosting.

## 7. Bẫy đã gặp

- OpenLiteSpeed bỏ qua `Header set` trong `.htaccess`. Thêm block `.htaccess` mới cần restart.
- OpenLiteSpeed: một `context` mới trong vhost (ví dụ `context /llms.txt` để thêm charset) không kế thừa `extraHeaders` của `context /`, cũng không kế thừa Basic Auth của staging. Chép lại header bảo mật (nosniff, HSTS…) và `realm`, `authName`, `required valid-user` vào context mới. Kiểm bằng `curl -sI` trên đúng URL đó, ở cả production và staging (staging phải trả 401 khi không có mật khẩu). Restart sau khi sửa vhost.
- aaPanel 8.0.6: `class/tools.py` che `tools.py`. Script `import tools` có thể ghi mật khẩu panel sai định dạng.
- `files.DeleteDir` của aaPanel lỗi khi gọi ngoài request web. `DeleteSite` giữ thư mục site.
- SFTP chroot với UID 1000 cần `RemoveIPC=no` cho logind. `userdel` user trùng UID dùng `-f`, không dùng `-r`.
- WP-CLI chạy bằng root làm WordPress chọn FTP và lỗi fatal. Chạy bằng user của web server, `cd /tmp` trước.
- Bật Wordfence có thể đặt `loginSec_disableApplicationPasswords` = 1, làm hỏng pipeline REST.
- aaPanel: `/etc/my.cnf` không có `bind-address`, MariaDB nghe `0.0.0.0` dù firewall chặn. Thêm `bind-address = 127.0.0.1` dưới `[mysqld]`, restart, kiểm `ss -tlnp`. WordPress dùng `localhost` (socket) nên không đổi gì.
- pure-ftpd của aaPanel là script init.d: tắt bằng `systemctl stop pure-ftpd` và `update-rc.d pure-ftpd disable`. Bật lại: `update-rc.d pure-ftpd enable`.
- `tar` trả mã 1 khi file đổi lúc đang đọc (Wordfence, cache). Script có `set -o pipefail` phải coi mã 1 là đạt, nếu không bản backup tuần không bao giờ hoàn tất.
- File plist của launchd là XML. Đường dẫn có dấu `&` (ví dụ tên thư mục workspace) phải viết thành `&amp;`, nếu không `launchctl` từ chối nạp. Mẫu `cai-lich-pull-mac.command` đã thoát ký tự và chạy `plutil -lint`.
- `rsync -a` chép mode thư mục của server về máy. Thư mục mode 600 (root vẫn đọc được) làm user thường không mở được thư mục đích, rsync báo `fstatat: Permission denied` (26/10/2026). Bản v1.7.1 dùng `rsync -rlt` rồi `chmod`. openrsync của macOS không có `--chmod`.
- `backup_pull.sh` bản trước v1.7 chỉ dùng `date -j` (chỉ có trên macOS) và báo thành công dù server không có `rsync` (18/10/2026). Bản v1.7 thử `date -d` rồi `date -j`, thoát 1 khi kéo lỗi.
- `mysqldump` thiếu `--no-tablespaces` báo lỗi khi user WordPress không có quyền PROCESS (gặp 3 lần, 10/2026). Server không có `zstd` mà script vẫn nén bằng `zstd` ra file 0 byte (16/10/2026): chạy `scripts/preflight_remote.sh` trước.
- `wp db export` gọi `mysqldump` qua `proc_open`. PHP CLI chặn `proc_open` trong `disable_functions` thì lệnh hỏng: dump bằng `mysqldump` qua SSH.
- Panel: 2FA, BasicAuth, giới hạn IP cần mật khẩu, mã OTP và có thể khoá người khác đang dùng panel. Để chủ site làm, agent chỉ kiểm chứng chỉ panel và ghi việc cần làm.
- `systemctl reboot` có thể mất khoảng 40 giây mới tắt máy. Chờ kernel mới trong `uname -r` rồi mới kiểm.
- Theme có URL dự phòng trỏ tới site phụ. Grep domain site phụ trước khi xoá site đó.
- Plugin ẩn trang đăng nhập (ví dụ WPS Hide Login) vẫn để `wp-activate.php` redirect ra slug ẩn. Kiểm bằng `exposure_check.sh`.
