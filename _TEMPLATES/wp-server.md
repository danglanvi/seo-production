# Hồ sơ máy chủ WordPress — {{CLIENT}}

> Clone file này thành `00-client-context/wp-server.md` khi dự án có quyền vào server của site. Skill `wp-pagespeed`, `wp-security-hardening`, `wp-content-review-apply` đọc file này trước lệnh đầu tiên.
>
> **Không ghi** mật khẩu, key, token, slug đăng nhập ẩn, IP nhạy cảm, host staging bí mật. Các giá trị đó nằm trong `.agent-secrets/.env` của máy (đã gitignore). File này chỉ ghi **tên biến**.

## 1. Truy cập

| Mục | Giá trị |
|---|---|
| Domain production | {{example.vn}} |
| SSH alias (trong `~/.ssh/config` của máy) | {{site-vps}} |
| User SSH | {{root / user riêng}} |
| Web root | {{/www/wwwroot/example.vn}} |
| Lệnh WP-CLI (đủ tiền tố) | {{sudo -u www HOME=/tmp/wpcli-home /usr/local/lsws/lsphp83/bin/php /usr/local/bin/wp}} |
| Tên biến secret dùng cho site | {{PAGESPEED_API_KEY, OPENROUTER_JEV_API_KEY, STG_BASIC_AUTH…}} |
| Người duyệt thay đổi trên site | {{SEO Lead Project / chủ site}} |
| Ai đăng nhập wp-admin khi cần | {{người vận hành, agent dùng tab Chrome đã đăng nhập}} |

## 2. Stack

| Mục | Giá trị |
|---|---|
| OS, panel | {{Ubuntu 24.04, aaPanel 8}} |
| Web server | {{OpenLiteSpeed / Apache / Nginx}} |
| PHP | {{8.3}} |
| Plugin cache | {{LiteSpeed Cache / WP Rocket / không}} |
| Plugin SEO | {{Rank Math / Yoast}} (biến năm: {{%currentyear%}}) |
| Plugin redirect | {{Rank Math Redirections / Redirection}} |
| Đa ngôn ngữ | {{WPML / Polylang / không}} |
| Builder, field | {{Elementor Pro, ACF Pro}} |
| Plugin bảo mật | {{Wordfence, plugin ẩn trang đăng nhập}} |
| Site khác cùng server | {{số site, có thuộc dự án không}} |

## 2b. Tầng cache sau khi ghi

Skill ghi nội dung (`wp-content-review-apply`, `wp-dang-bai`, `semantic-html-optimization`) đọc mục này sau mỗi lượt ghi.

| Tầng | Giá trị |
|---|---|
| Page cache trên server | {{LiteSpeed Cache; option purge-post_all = 0/1}} |
| Object cache | {{Redis DB số mấy / không}} |
| Cache phụ thuộc nội dung | {{nhóm cache hay transient do mu-plugin, theme dựng từ nội dung và chỉ làm mới qua save_post / không có}}. Có thì `apply.php` giữ `wp_cache_flush()`, không chạy `FLUSH=0` |
| CDN giữ HTML | {{không / có: nhà cung cấp, vùng khách đi qua CDN, TTL HTML ở edge}} |
| CDN tự purge khi bài đổi | {{có: mu-plugin nào / không}} |
| Lệnh purge CDN theo URL | {{ví dụ: python3 -I skills/wp-ucss/scripts/bunny_purge.py <paths.txt> --site <site.json> --apply --warm}} |
| Header giờ lưu ở edge | {{ví dụ: cdn-cachedat, giờ UTC}} |
| CSS gọn theo path | {{không / có: file map, lệnh regen cho danh sách path, file phối hợp khi lane khác giữ khoá}} |
| Biến thể cần làm nóng | {{desktop, mobile, bản WebP, bản bot}} |

## 3. Staging

| Mục | Giá trị |
|---|---|
| Có staging | {{có / không}} |
| Cách vào | {{subdomain có Basic Auth / tunnel SSH + host-resolver-rules}} |
| Tên biến Basic Auth | {{STG_BASIC_AUTH}} |
| Cookie chọn theme (nếu có) | {{tên cookie}} |
| Ghi chú | {{staging noindex, chưa bật page cache…}} |

## 4. Nơi lưu

| Mục | Giá trị |
|---|---|
| Backup (ngoài repo) | `~/Backups/{{host}}/<YYYY-MM-DD>/<đợt>-pre/` |
| Quarantine trên server | `/root/{{site}}-offweb-<YYYY-MM-DD>/` |
| Trang duyệt nội dung (artifact) | {{link claude.ai/artifact/…}} |
| Evidence PageSpeed | `03-audits/technical/pagespeed-<YYYY-MM-DD>/` |
| Evidence bảo mật | `03-audits/technical/security-<YYYY-MM>/` |
| Đợt ghi nội dung | `06-onpage-internal-link/apply-<YYYY-MM-DD>/` |
| Bộ mẫu hiệu chuẩn model của site | {{đường dẫn evidence có nhãn Claude}} |

## 5. Luật riêng của site

- {{Ví dụ: giờ thấp điểm được restart, kênh báo khi site lỗi, mục nào luôn hỏi trước}}

## 6. Bẫy đã gặp

- {{Ví dụ: chạy WP-CLI từ /tmp; plugin X ghi đè option Y; theme in H1 cứng ở template Z}}

## 7. Lịch sử đợt

| Ngày | Đợt | Skill | Kết quả | Evidence |
|---|---|---|---|---|
| {{YYYY-MM-DD}} | {{rà bảo mật}} | {{wp-security-hardening}} | {{tóm tắt}} | {{đường dẫn}} |
