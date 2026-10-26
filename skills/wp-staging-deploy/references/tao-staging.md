# Tạo staging mới trên server OpenLiteSpeed (aaPanel)

Làm một lần cho mỗi site. Các bước dưới gom từ lần dựng staging ngày 17/10/2026. Chạy bằng root trên server. Secret sinh trên server và lưu ở file quyền 600. Không in secret ra terminal hay log.

## Các bước

1. Dừng nếu thư mục staging đã có dữ liệu.
2. Sinh mật khẩu DB và mật khẩu Basic Auth bằng `openssl rand`. Ghi vào `/root/stg-<site>-secrets.env` (600).
3. Chép file site bằng `tar`. Bỏ các thư mục: `wp-content/litespeed`, `wflogs`, `logs`, `upgrade*`, `ai1wm-backups`, `cache`, `maintenance`, file `.user.ini`, `wordfence-waf.php`.
4. Tạo DB và user riêng cho staging. Dump DB production rồi import vào DB staging.
5. Sửa `wp-config.php` của staging:
   - DB riêng và salt mới.
   - `WP_HOME`, `WP_SITEURL` là URL staging.
   - `WP_ENVIRONMENT_TYPE` là `staging`.
   - `WP_CACHE` là `false`. Bật `DISABLE_WP_CRON` và `AUTOMATIC_UPDATER_DISABLED`.
6. Chép `scripts/zz-staging-safety.php` vào `wp-content/mu-plugins/`. Plugin này chặn email, đặt noindex, chặn robots và tắt cache LiteSpeed.
7. Tạo vhost OLS:
   - File định nghĩa và file chi tiết.
   - Basic Auth bằng realm có `htpasswd` trong thư mục mà user `www` đọc được (750 root:www).
   - Header `X-Robots-Tag: noindex, nofollow`.
   - SSL tự ký 30 ngày.
   - Thêm dòng `map` vào listener 80 và 443.
8. Restart OLS. Kiểm staging trả 401 khi không có Basic Auth và trả noindex khi có.
9. Ghi URL staging vào `/root/.stg_home`. Script khác đọc URL từ file này để không in host ra log.

## Gỡ staging

1. Xoá 2 dòng `map` của staging trong listener 80 và 443.
2. Xoá file vhost, file chi tiết, file SSL và thư mục `htpasswd`.
3. Restart OLS.
4. Drop DB staging, rồi xoá thư mục site staging.

## Bẫy

- Nếu `uploads` của staging là bind mount của production, chạy `mount --make-private` trước khi mount con. Mount con dưới bind mount shared sẽ lan sang production (sự cố 18/10/2026).
- Worker OLS chạy bằng `www`. File `htpasswd` để trong `/root` thì OLS không đọc được.
- Staging không có cache LiteSpeed. Phần sửa tốc độ có thể không thấy tác dụng trên staging: kiểm thêm trên production bằng URL có tham số riêng trước khi purge.
