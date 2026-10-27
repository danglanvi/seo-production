# Danh mục việc đã chạy thật

Mỗi dòng là một việc đã áp trên VPS site agency mẫu 24–27/10/2026 (aaPanel, OpenLiteSpeed, lsphp 8.3, MySQL 5.7, Redis 7). Cột "Đo được" là số 48 giờ hoặc số tức thời có ghi rõ. Số 7 ngày: chờ đo 04/11/2026. Trước khi đưa việc vào plan, đo mốc theo `references/do-moc.md` và đọc giá trị live của mọi khoá sẽ đổi.

## 1. Chia đợt

| Đợt | Loại việc | Khi nào | Duyệt |
|---|---|---|---|
| 0 | Luật lane: giới hạn tải do chính agent gây ra | Ngay | Không cần |
| 1 | Không dừng dịch vụ, trả lại bằng 1 lệnh. Tối đa 2 lần restart graceful OLS: một cho staging, một cho production | Ban ngày | Lead duyệt cả gói |
| 2a | Config sống cần restart MySQL hoặc OLS | 02:00–03:00, khi không có khoá lane | Lead duyệt |
| 2b | Vá OS, reboot | Một đêm riêng, không gộp việc khác | Lead duyệt, có backup ngoài máy |
| 3 | Đụng site khách cùng server, xoá dữ liệu, CDN | Mỗi site một ngày, theo dõi 24 giờ | Lead duyệt từng việc, báo khách trước |

## 2. Đợt 0: luật lane

Agent và lane của agent là một nguồn tải. Site mẫu: 99 phút chạm trần PHP mỗi tuần do lane, 1 lần OOM do 8 tiến trình WP-CLI (mỗi tiến trình 1,8–2,2 GB).

- Production tối đa 2 request đồng thời và 1 request/giây. Crawler (Screaming Frog) 2 luồng, tối đa 2 URL/giây.
- Tối đa 2 tiến trình WP-CLI cùng lúc trên một server. Giữ khe bằng `flock` (`/tmp/wpcli-slot-1.lock`, `/tmp/wpcli-slot-2.lock`). Mặc định `-d memory_limit=512M`.
- Purge theo URL, tối đa 12 path mỗi lệnh. Không purge toàn site. Không lấy dòng "thành công" của `wp litespeed-purge url` làm bằng chứng: lệnh báo thành công mà trang vẫn `hit` ở cả OLS 1.8.1 và 1.9.4 (27/10/2026). Kiểm header cache sau khi purge qua hook `litespeed_purge_url`, hoặc kiểm md5 nội dung đã đổi. Không dùng `wp litespeed-option set`, vì lệnh đó purge toàn site: ghi option bằng SQL rồi `wp_cache_delete`.
- Audit SQL chạy trên bản dump hoặc staging. Không quét `LIKE` trên `postmeta` production.
- Không chạy backup, crawl và đồng bộ staging cùng lúc.
- Đo TTFB trượt cache tối đa 5 URL × 5 lượt mỗi lần.
- Gửi luật trực tiếp cho lane đang chạy. Workflow đang chạy không đọc lại HANDOFF.

## 3. Trước PHP (OLS, `.htaccess`, robots)

| Việc | Cách làm | Đo được | Trả lại |
|---|---|---|---|
| Khối chặn trước PHP | Mẫu ở mục 3.1. Đặt sau các khối có sẵn, trước `# BEGIN WordPress`. Staging trước | 32/32 đường dẫn dò từ 230–1.383 ms về 403/404 trong 6–10 ms. Luật R1–R6 từ 3.019 về 31 PHP/ngày (48 giờ) | `sed -i '/^# BEGIN <tên khối>/,/^# END <tên khối>/d' .htaccess` rồi restart graceful. Không chép đè cả file |
| `robots.txt` chặn bot SEO phụ | Thêm nhóm `Disallow: /` cho PetalBot, AwarioBot, DotBot, MJ12bot, SERankingBacklinksBot, BLEXBot, DataForSeoBot, Barkrowler, SeekportBot, serpstatbot, Baiduspider, Sogou. Giữ nguyên nhóm cũ. Kiểm bằng Protego: bot tìm kiếm và bot AI vẫn Allow | Mốc 359–380 PHP/ngày của 12 bot. Bot cần 1–2 ngày mới tuân | Cắt file về độ dài cũ khi phần đầu còn đúng md5 |
| Basic Auth cho site không công khai (bản EN chưa ra mắt, site thử) | Realm OLS ở context `/`. Thêm context `/.well-known/acme-challenge/` không realm để gia hạn cert. File mật khẩu ngoài docroot | Request vào site 991 trong 11 giờ → 13 trong 34 phút. Pool ngủ, trả ~107 MB OPcache | Xoá khối realm và context acme, restart |
| Cache sitemap | Thêm `sitemap_index.xml 3600` và `-sitemap 3600` vào `litespeed.conf.cache-force_uri` bằng SQL | Lượt 2: hit 15–17 ms (trước 188–236 ms) | Ghi lại chuỗi cũ, purge sitemap |
| Cache trang 404 | `litespeed.conf.cache-ttl_status` = `["404 86400","500 600"]`. Mu-plugin purge tag `HTTP.404` khi đăng bài, đổi slug, khôi phục bài, lưu redirect | Nhắm nhóm IP quét gọi đường dẫn 404 không đuôi (`/graphql`, `/admin`…), mỗi lượt 1,4 s PHP | Đặt lại `404 3600`, gỡ dòng purge |
| Redirect của plugin SEO sang rule tĩnh | Xuất danh sách redirect đang bật, đánh dấu nguồn đã có rule tĩnh trong `.htaccess`, chuyển nguồn exact còn lại thành rule tĩnh theo lô. Giữ redirect regex trong plugin | Hàm redirect của Rank Math tốn 15,2 ms ở 24/24 lượt đo, mỗi request PHP. Site mẫu: 191/548 nguồn đã tĩnh, 340 nguồn exact chưa chuyển | Xoá khối rule theo dòng `BEGIN`/`END` |
| Giới hạn request động theo IP (`dynReqPerSec`) | Chỉ áp khi đủ 4 điều kiện: tách đỉnh request/giây của bot thật theo dải IP công bố, đo đỉnh của IP văn phòng (trình soạn Elementor sinh hàng chục request/giây), đo IP site khách và callback thanh toán, thêm IP văn phòng vào danh sách tin cậy. Thử từ một máy khác, không thử từ IP văn phòng | Chưa áp ở site mẫu | `dynReqPerSec 0`, restart |

Bot đã cân nhắc và không chặn: Googlebot, Bingbot, AhrefsBot, SemrushBot, Cốc Cốc, DuckDuckBot, Applebot, Amazonbot, mọi bot AI (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, PerplexityBot, Bytespider, LinkupBot, ShapBot). Trước khi thêm UA vào R6, mở trang chính thức của UA. Nếu trang ghi mục đích tìm kiếm hay AI, bỏ UA đó.

### 3.1 Mẫu khối chặn trước PHP

```apache
# BEGIN chặn trước PHP <ngày>
# R1: file .php không tồn tại.
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule \.php$ - [F,L,NC]
# R3: wp-login.php gọi thẳng khi khách chưa đăng nhập. Chỉ dùng khi site đã ẩn trang đăng nhập.
RewriteCond %{HTTP_COOKIE} !wordpress_logged_in_ [NC]
RewriteRule ^wp-login\.php$ - [F,L,NC]
RewriteCond %{HTTP_COOKIE} !wordpress_logged_in_ [NC]
RewriteRule ^wp-admin/?$ - [F,L,NC]
# R2: dò user và batch REST khi chưa đăng nhập. Bỏ qua header Authorization (application password).
RewriteCond %{HTTP_COOKIE} !wordpress_logged_in_ [NC]
RewriteCond %{HTTP:Authorization} ^$
RewriteRule ^wp-json/(wp/v2/users|batch/v1) - [F,L,NC]
RewriteCond %{HTTP_COOKIE} !wordpress_logged_in_ [NC]
RewriteCond %{HTTP:Authorization} ^$
RewriteCond %{QUERY_STRING} (^|&)(author=[0-9]|rest_route=/?(wp/v2/users|batch)) [NC]
RewriteRule ^ - [F,L]
# R5: POST vào trang chủ từ thư viện script.
RewriteCond %{REQUEST_METHOD} POST
RewriteCond %{HTTP_USER_AGENT} (aiohttp|python-requests|Go-http-client) [NC]
RewriteRule ^$ - [F,L]
# R6: bot rác bỏ qua robots. Không có bot AI, máy tìm kiếm, AhrefsBot.
RewriteCond %{HTTP_USER_AGENT} (<UA 1>|<UA 2>) [NC]
RewriteRule ^ - [F,L]
# R4: file tĩnh không tồn tại, ngoài uploads và thư mục cache. OLS trả 404 tĩnh.
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !^/wp-content/(uploads|litespeed)/ [NC]
RewriteRule \.(png|jpe?g|gif|webp|avif|svg|ico|bmp|css|js|mjs|map|woff2?|ttf|otf|eot|mp4|webm|mp3|pdf|zip|rar|gz|7z|tar|tgz|sql|bak|old|swp|log|ini|env|toml|ya?ml|sh)$ - [L,NC]
# END chặn trước PHP <ngày>
```

- R4 không có `txt`, `xml`, `json`: `llms.txt`, sitemap, khoá IndexNow, `.well-known` có thể do PHP sinh.
- Trước khi ghi: kiểm redirect của plugin SEO và plugin Redirection không có nguồn đuôi `.php` hay đuôi trong R4.
- Phép thử trên staging: đăng nhập qua slug ẩn, đăng xuất, quên mật khẩu, 2FA, lưu trang builder, gửi form, `/wp-json/` 200, REST bằng application password 200, sitemap 200, `llms.txt` 200, 30 URL và asset của chúng 200, đường dẫn dò trả 403/404 dưới 50 ms.

## 4. PHP

| Việc | Cách làm | Đo được | Trả lại |
|---|---|---|---|
| WP-Cron sang cron hệ thống | `define('DISABLE_WP_CRON', true);` và `/etc/cron.d/<site>-wp-cron`: `1-59/5 * * * * www mkdir -p /tmp/wpcli-home && HOME=/tmp/wpcli-home flock -n /tmp/wpcron-<site>.lock nice -n 10 <php> -d memory_limit=512M <wp> --path=<path> cron event run --due-now --quiet`. Thử lệnh bằng tay trước. Thử bài hẹn giờ trên staging. Lệch phút giữa các site | `doing_wp_cron` 1.492/ngày → 0. Bài hẹn giờ trễ 2 phút 24 giây trên staging | Xoá dòng `define` và file cron.d |
| Giữ tiến trình PHP sống lâu | `env LSAPI_PGRP_MAX_IDLE=3600` trong khối `extprocessor` của vhost. Restart, rồi dừng tiến trình cha `lsphp` của pool. Kiểm `/proc/<pid cha>/environ` | TTFB request đầu sau khoảng nhàn 2.466 → 735 ms (48 giờ). Tốn thêm tối đa ~150 MB lúc đêm | Xoá dòng env, restart, dừng cha |
| Trần PHP mỗi pool | Hạ `maxConns` và `LSAPI_CHILDREN` cùng một số trong khối `extprocessor`. Tổng trần × RAM mỗi tiến trình + mysqld + OPcache phải dưới RAM. Site khách: báo khách trước. Pool ít dùng (site thử, phpMyAdmin) hạ về 3. Giữ staging bằng production nếu cần A/B PSI | Trần tổng 90 → 45 tiến trình theo plan. OOM của site mẫu ngày 20/10 do 1 IP quét lấp đầy pool trần 20 | Chép lại `detail/*.conf`, restart, dừng cha |
| Wordfence low resource scan | `wfConfig::set('lowResourceScansEnabled', 1)` sau khi lưu giá trị cũ | Scan chiếm 17% PHP-giây của site trước khi đổi | Đặt lại giá trị cũ |
| Bớt việc PHP ở mỗi trang (mu-plugin) | Gỡ callback không cần ở trang đó với độ ưu tiên `PHP_INT_MIN`: gỡ ở độ ưu tiên 1 không có tác dụng khi lớp đo profiler đã bọc callback. Cache mảnh template trong Redis, khoá gồm file, tham số, ID bài, ngôn ngữ và số phiên bản, để nội dung đổi thì khoá cũ tự hết hiệu lực. So HTML trước và sau trên 6 trang, đã chuẩn hoá nonce, token và giờ | TTFB origin giảm 157 ms (A/B 6 lượt). HTML giống bản cũ 6/6 trang. 0 5xx trên 388 request | Chuyển mu-plugin vào quarantine |
| Gỡ plugin không dùng | Tắt, chuyển thư mục vào quarantine trên staging rồi production. Render-diff 10 trang trước khi gỡ | Popup Maker: HTML không đổi, 0 5xx trên 3.712 request | Chuyển thư mục về, bật lại |

Không làm: tăng trần PHP khi đỉnh do IP quét (trần cao hơn chỉ tốn RAM); bật crawler LSCache (thêm PHP liên tục); `opcache.validate_timestamps=0` khi lane còn sửa code.

## 5. MySQL

| Việc | Cách làm | Đo được | Trả lại |
|---|---|---|---|
| Biến đổi động | `SET GLOBAL key_buffer_size=64M, query_cache_size=0, tmp_table_size=32M, max_heap_table_size=32M, table_definition_cache=1000`. Backup `my.cnf`, ghi cùng giá trị vào `[mysqld]` | mysqld RSS + swap 1.224 → 1.142 MB tức thời | `SET GLOBAL` giá trị cũ, chép lại `my.cnf` |
| Tắt `performance_schema`, giới hạn arena malloc | Dump bảng digest về máy trước. `performance_schema = OFF`. Drop-in `/etc/systemd/system/mysqld.service.d/malloc.conf` với `Environment=MALLOC_ARENA_MAX=2`. `daemon-reload`, restart một lần | Áp 27/10/2026 02:34. Số RSS 1 ngày: chờ đo | Xoá dòng và drop-in, `daemon-reload`, restart |
| Bảo vệ mysqld khỏi OOM | `OOMScoreAdjust=-900` trong drop-in. Khi OOM, kernel giết PHP trước | Kiểm `/proc/<pid>/oom_score_adj` | Xoá dòng |
| Index cho bảng lớn trên staging | `ALTER TABLE wp_postmeta ADD INDEX <tên> (meta_key(32), meta_value(64)), ALGORITHM=INPLACE, LOCK=NONE;` lúc 01:00–02:00. Đếm index bằng `SHOW INDEX` theo tên, không đếm theo số cột | `EXPLAIN` 1.695 dòng → 1. Truy vấn 22–133 ms → 0,3–1,0 ms. ALTER ~5 giây mỗi DB | `DROP INDEX` |

Bẫy:

- Cron kiểm dịch vụ của panel có thể gọi `systemctl restart mysql` khi unit đang `activating`. Tạm tắt dòng cron đó trong lúc restart, bật lại khi mọi site trả 200.
- Sau mọi lần restart MySQL (cron, nút panel, reboot), kiểm `environ` có `MALLOC_ARENA_MAX=2` và `oom_score_adj` là -900. Nút restart của aaPanel đi qua systemd, nên drop-in vẫn áp.
- Không tăng `innodb_buffer_pool_size` khi hit trên 99,9%. Không hạ `max_connections` để tiết kiệm RAM: kết nối không cấp RAM trước.

## 6. Redis

| Việc | Cách làm | Đo được | Trả lại |
|---|---|---|---|
| Tắt RDB save khi Redis chỉ làm object cache | `CONFIG SET save ""`, ghi `save ""` vào `redis.conf` | Bỏ ~99 lần fork và ~1,5 GB ghi ổ mỗi ngày | `CONFIG SET save "900 1 300 10 60 10000"` |
| Đổi mật khẩu không restart | `ACL SETUSER default >mới` (cả hai mật khẩu cùng hợp lệ) → ghi option object cache của staging rồi production, file `.litespeed_conf.dat`, xoá key `alloptions` → `ACL SETUSER default <cũ` → ghi `requirepass` vào `redis.conf` | 0 gián đoạn, `keyspace_hits` tăng đều | Thêm lại mật khẩu cũ bằng `ACL SETUSER` |

Kiểm số DB object cache của staging khác production trước khi bật object cache cho staging. Lỗi đã gặp 27/10/2026: option của staging trỏ cùng DB với production.

## 7. Ổ đĩa

| Việc | Đo được |
|---|---|
| Nén log lỗi MySQL lớn bằng `nice -n 19 ionice -c3 gzip -1`; cron nén log OLS mỗi giờ; logrotate `btmp` hằng tuần, giữ 4, nén; tắt `WP_DEBUG_LOG` ở staging khi không lane | `df /` 85% → 81% (−2,24 GB) trong 30 phút |
| CSS gộp của LSCache: `add_filter('litespeed_url_file_expired_days', fn() => 8);` | Không dùng số dưới 7. Lượt trượt cache đánh dấu file của URL sạch hết hạn, nên với 3 ngày, bản cache 7 ngày trỏ tới file đã xoá. Đếm 404 dưới `/wp-content/litespeed/css/` mỗi ngày trong 10 ngày |
| Backup cũ, file tạm của OLS, journald `SystemMaxUse=100M`, kernel cũ | Chỉ xoá sau khi chép về máy agent và kiểm sha256. Gỡ kernel cũ bằng `apt-get purge` đúng tên gói, không dùng `autoremove` |

## 8. Bản OLS và cấu hình server

- Nâng OLS cài từ tarball của panel: dùng gói chính thức, kiểm sha256, chạy `install.sh` ở chế độ upgrade khi server đang chạy. Bản 1.9.4 gửi SIGUSR1, nên đây là restart graceful. Không dùng `lsup.sh`: script đó dừng hẳn OLS và xoá `/tmp/lshttpd`. Installer giữ `httpd_config.conf`. Site mẫu 27/10/2026: 0 5xx, md5 cấu hình không đổi.
- Trước khi nâng, chạy sandbox A/B 2 bản OLS trên loopback, trong mount namespace riêng, với bản sao `.htaccess` của site. OLS đổi sang PCRE2 từ 1.9.1, nên regex trong `.htaccess` có thể đổi kết quả. Site mẫu: 710 dòng Rewrite, sandbox lệch 6–8 path do 403 ngẫu nhiên, bản cũ cũng gặp.
- Nâng OLS làm mất cache LSCache cũ. Lượt đầu mỗi trang mất 0,76–1,14 s. Làm nóng các path công khai, mỗi path 2 biến thể (desktop, mobile), theo luật lane.
- Viết script hạ bản trước khi nâng và chạy DRY. Giữ khoá server tới khi trang chính đã `hit` sau làm nóng, rồi mới nhả khoá.
- Tắt WebAdmin OLS khi không dùng: `disableWebAdmin 1` trong `httpd_config.conf`, rồi `lswsctrl reload`. Kiểm panel không gọi cổng 7080.
- OLS không nén Brotli cho HTML động và trang LSCache, chỉ gzip. Không đưa việc này vào plan.
- Mọi restart OLS nạp mọi thay đổi cấu hình đang chờ của mọi vhost. Trước restart, liệt kê file cấu hình (`httpd_config.conf`, vhost `*.conf`, `.htaccess`) sửa sau lần OLS khởi động gần nhất cộng 10 giây. Có file như vậy thì hỏi lane đã sửa file đó trước khi restart.

## 9. Script đợt đêm

Đợt 2a của site mẫu chạy bằng một script có:

- Cổng trước mỗi bước: không khoá lạ, RAM khả dụng ≥ 500 MB, load 1 phút < 6, không file cấu hình chờ áp.
- Kiểm chữ cũ trước khi ghi. Giá trị live khác lúc chuẩn bị thì không ghi.
- Kiểm sau mỗi bước: mọi site 200 ở hai lượt cách 15 giây, 0 5xx mới, robots và canonical bản Googlebot smartphone không đổi.
- Bước lỗi thì tự trả lại bước đó và dừng các bước sau.
- DRY in diff sẽ ghi và thử lệnh trả lại, không ghi gì.
- Harness thay `ssh`, `curl` bằng bản giả để chạy nhánh ghi qua các ca lỗi trước đêm chạy thật. Site mẫu: 9 ca.
