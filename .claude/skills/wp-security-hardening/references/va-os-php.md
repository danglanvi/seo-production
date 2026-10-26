# Vá OS và vá PHP theo advisory

Đọc file này khi vá gói hệ điều hành hoặc vá PHP sau một advisory. Quy trình lấy từ 2 lần chạy thật trên VPS Ubuntu, aaPanel, OpenLiteSpeed: vá OS ngày 16/10/2026, vá PHP ngày 22/10/2026. Fact riêng của từng host (phiên bản, đường dẫn đã đổi) ghi ở `00-client-context/wp-server.md`, không ghi ở đây.

Mọi lệnh cần root. Backup theo Bước 0 của SKILL.md trước khi vá. Reboot và restart web server chỉ trong giờ thấp điểm hoặc khi người duyệt cho phép.

## 1. Vá OS (Ubuntu, Debian)

1. Chạy `apt-get update` trước khi đếm gói. Một lượt vá 10/2026 đếm bằng danh sách cũ ra 75 gói, đếm lại sau `update` ra 281 gói, trong đó 210 gói bảo mật.

   ```bash
   apt-get update
   apt list --upgradable 2>/dev/null | grep -c upgradable
   apt list --upgradable 2>/dev/null | grep -c -- '-security'
   ```

2. Ghi `uname -r` và danh sách gói sẽ nâng vào thư mục evidence.
3. Chạy apt qua `systemd-run`. Khi openssh hoặc systemd nâng cấp, SSH từ chối kết nối khoảng 40 giây. Apt chạy trong unit riêng nên không chết theo phiên SSH.

   ```bash
   systemd-run --unit=os-patch-$(date +%Y%m%d) --wait --collect \
     --setenv=DEBIAN_FRONTEND=noninteractive \
     apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold upgrade
   journalctl -u os-patch-<ngày> --no-pager | tail -50
   ```

4. aaPanel dùng MariaDB riêng, gói MariaDB của Ubuntu có thể va với bản đó:
   - `mariadb-common` lỗi cấu hình khi thiếu `/etc/mysql`. aaPanel có thể đã đổi tên thư mục này thành `/etc/mysql.bak`. Tạo `/etc/mysql/mariadb.cnf` chỉ chứa comment. Kiểm hash của `mysqld --print-defaults` giống nhau trước và sau.
   - `mariadb-client` ghi đè link `/usr/bin/mysql`, `mysqldump`, `mysqlcheck` của aaPanel. Khôi phục 3 link về bản của aaPanel. Giữ link bằng `dpkg-divert --local --divert /usr/bin/<tên>.distrib --add /usr/bin/<tên>` cho từng file. Kiểm bằng `readlink -f /usr/bin/mysqldump`.
5. Giữ kernel cũ trong GRUB. Không chạy `apt autoremove` trước khi kernel mới chạy ổn.
6. Reboot. `systemctl reboot` có thể mất khoảng 40 giây mới tắt máy, trong lúc đó SSH vẫn trả kết quả của hệ thống cũ. Chờ `uname -r` trả kernel mới rồi mới kiểm.
7. Kiểm: mọi site trả 200, web server và MySQL chạy, `persistence.sh` không có mục mới, error log không có fatal.

## 2. Vá PHP trên OpenLiteSpeed

1. Lập bảng site → handler PHP. Đọc `extprocessor` và `scripthandler` trong vhost của từng site, và handler mặc định của server:

   ```bash
   grep -HE '^\s*(path|add)\s' /www/server/panel/vhost/openlitespeed/detail/*.conf
   ls -l /usr/local/lsws/fcgi-bin/lsphp
   for p in $(pgrep -x lsphp); do readlink /proc/$p/exe; done | sort | uniq -c
   ```

   Ghi cả vhost `default` và phpMyAdmin. Ngày 22/10, handler mặc định trên một host trỏ tới PHP 5.6.
2. Xác minh bản vá cho từng binary: `apt-cache policy lsphp83 lsphp74`, rồi đọc changelog của gói. Nếu changelog không ghi mã CVE, ghi "chưa xác minh trực tiếp" vào báo cáo. Ghi thêm biện pháp giảm thiểu đang có, ví dụ file ini tắt tính năng bị ảnh hưởng.
3. Với mỗi site còn chạy bản chưa xác minh, thử chuyển sang bản đã vá. Chạy WP-CLI bằng cả hai binary và so kết quả. Chạy bằng user của web server:

   ```bash
   sudo -u www HOME=/tmp/wpcli-home /usr/local/lsws/lsphp83/bin/php /usr/local/bin/wp \
     --path=<root> eval 'echo PHP_VERSION, " ", count(get_option("active_plugins")), PHP_EOL;'
   ```

   Lệnh lỗi fatal hoặc số plugin khác nhau: giữ binary cũ, ghi lý do.
4. Trước khi chuyển, chỉnh `php.ini` của binary mới khớp binary cũ: `disable_functions`, `memory_limit`, giới hạn upload, socket MySQL, OPcache riêng của site.
5. Đổi PHP của site trong panel, hoặc sửa vhost theo `references/ap-config-song.md`. Việc này cần người duyệt.
6. `lswsctrl restart` không khởi động lại tiến trình `lsphp` chạy tách. Sau restart, dừng tiến trình cũ bằng `pkill -x lsphp`. Kiểm lại `readlink /proc/<pid>/exe` trỏ tới binary mới.
7. Kiểm: mọi site trả 200, error log không có fatal, `stderr.log` không có dòng lỗi mới.

## 3. Việc cấp server cần duyệt riêng

Các việc sau ảnh hưởng mọi site trên server. Đưa vào danh sách chờ duyệt, kèm lệnh làm và lệnh rollback. Không làm khi chưa có duyệt, kể cả khi việc có vẻ an toàn. Ngày 22/10, một agent tự đổi handler mặc định và tự tắt php-fpm ngoài 4 đề xuất đã duyệt.

| Việc | Lệnh làm | Rollback |
|---|---|---|
| Trỏ handler mặc định `fcgi-bin/lsphp` sang bản đã vá | `ln -sfn /usr/local/lsws/lsphp83/bin/lsphp /usr/local/lsws/fcgi-bin/lsphp` | Trỏ lại đích cũ đã ghi ở bước 2.1 |
| Tắt php-fpm của aaPanel khi không web server nào dùng | `systemctl stop php-fpm-<ver>`, `update-rc.d php-fpm-<ver> disable` | `update-rc.d php-fpm-<ver> enable`, `systemctl start php-fpm-<ver>` |
