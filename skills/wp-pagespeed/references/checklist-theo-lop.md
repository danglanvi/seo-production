# Checklist 7 lớp tối ưu

Đọc file này ở Bước 3–4. Mỗi lớp gồm: dấu hiệu trong số đo, cách sửa (ưu tiên code tự viết), số đã đo trên 2 site thật 10/2026, bẫy, rollback. Thứ tự lớp là thứ tự nên làm khi chưa có lý do khác.

Mẫu mã: `$WPS/templates/mu-plugin-lcp-priority.php` (ưu tiên ảnh LCP). Script nằm ở `$WPS/scripts/`. Các lớp khác viết thành một mu-plugin hiệu năng riêng của site, chia phần theo lớp: TTL ngắn, font, bỏ thư viện trùng, critical CSS theo template, `srcset` cho ảnh theme. Lưu bản đã chạy vào evidence của đợt.

Mỗi mu-plugin chạy trên filter của LiteSpeed (`litespeed_buffer_before` hoặc `litespeed_buffer_after`). Tắt mu-plugin bằng cách chuyển file ra khỏi `mu-plugins/` rồi purge. Không xoá file.

## Lớp 1 — cache và TTFB

- Dấu hiệu: TTFB lab trên 0,8 s, CrUX TTFB p75 trên 0,8 s, header `x-litespeed-cache: miss` ở lượt thứ hai.
- Kiểm: `curl -s -o /dev/null -w '%{http_code} %{time_starttransfer}\n' -H 'User-Agent: <UA>' <url>` 2 lần, xem header cache.
- Sửa: TTL page cache dài (site mẫu: 1 → 7 ngày). Trang có giá, đếm ngược hoặc WooCommerce giữ TTL 1 ngày bằng mu-plugin. Cache 1 năm cho file có tên băm (`wp-content/litespeed/`, font).
- Bẫy:
  - LiteSpeed Guest Mode trễ mọi JS ở lượt xem đầu, kể cả GTM. UA Lighthouse nằm trong danh sách Guest Mode, nên lab đo đúng bản khách mới nhận.
  - Guest Mode dùng danh sách loại trừ JS riêng: `optm-gm_js_exc` (filter `litespeed_optm_gm_js_exc`), không phải `optm-js_defer_exc`. Kiểm bằng `ls_exclusions_check.py` (`fcp-guest-mode.md`).
  - FCP mobile dồn một mốc ở site bật Guest Mode mà trang chưa có critical CSS: đọc `fcp-guest-mode.md`.
  - CrUX TTFB p75 trên 0,8 s hoặc lượt đầu của khách thường miss: nhánh chỉ đọc ở `ttfb-cache-trang.md`.
  - Crawler LiteSpeed tốn CPU của host dùng chung. Không bật khi chưa đo tải.
  - Đổi PHP version là thay đổi lớn. Thử trên staging trước.
  - Cache trình duyệt 1 năm cho mọi file tĩnh (khối `expires` của vhost OpenLiteSpeed) chỉ an toàn khi CSS, JS có `?ver=` đổi theo nội dung (theme tự viết: `filemtime`). Ảnh, font không có version: đổi nội dung thì đổi tên file. Ghi luật này vào hồ sơ site.
  - Option `purge-post_all=1` (quy tắc tự purge "All pages") làm mỗi lần lưu một bài xoá cache toàn site. Site agency mẫu 21/10: kho cache ghi mới 20.509 file trong 24 giờ, và 5 URL vừa làm nóng lúc 16:27 trở lại miss lúc 16:43. Đặt 0 khi chủ site duyệt, rồi kiểm các quy tắc `purge-post_*` còn lại vẫn purge trang chủ và chuyên mục.
- Biến thể cache: LiteSpeed tách một URL thành tối đa 8 bản. Một lần purge theo URL xoá cả 8 bản.
  - Khách mới hoặc khách quay lại (cookie `_lscache_vary` của Guest Mode).
  - Desktop hoặc mobile (vary `ismobile`).
  - Có hoặc không có WebP: khối rewrite WebP trong `.htaccess` đặt `vary=+webp` khi `Accept` có `image/webp`, hoặc khi UA là Safari, Firefox đời mới. Trình duyệt thật luôn vào bản webp. Googlebot và crawler gửi `Accept: */*`, nên vào bản plain.
- Làm nóng cache sau mỗi đợt purge:
  - Gửi header của Chrome thật: UA Chrome, `Accept` có `image/webp`, `Accept-Language`. curl mặc định gửi `Accept: */*`, nên chỉ làm nóng bản plain và khách thật vẫn miss.
  - Làm nóng cả desktop lẫn mobile, cả khách mới lẫn khách quay lại (lấy cookie bằng POST `wp-content/plugins/litespeed-cache/guest.vary.php`). Thêm bản plain cho bot. Chạy 1 luồng, nghỉ 0,5 s giữa các lượt.
  - Script: `bash "$WPS/scripts/lam_nong.sh" --host https://example.com <path vừa purge> ... -W both`. Không có path thì script làm nóng mọi URL trong sitemap. Chỉ làm nóng toàn site sau purge toàn site. Chạy `-n` trước để xem kế hoạch.
  - Site agency mẫu 21/10: lane nội bộ chỉ làm nóng bằng UA desktop, nên lượt đầu của khách mobile hit 5%, desktop hit 95%. Sau khi làm nóng đủ biến thể: lượt đầu mobile vào cache ở 39/40 URL nhiều khách nhất.
  - Kiểm sau khi làm nóng: `scripts/cache_variants.py` cho robots, canonical và nhãn cache ở 5 biến thể.
  - Site chặn hoặc thay `guest.vary.php` (khách ẩn danh không tải lại trang, site agency mẫu 26/10): script không lấy được cookie của bản khách quay lại. Chạy `-V guest-d,guest-m -W both`. Bản khách quay lại để cron trên server làm nóng.
- Googlebot smartphone dùng chung bản cache với khách mobile gửi `Accept: */*`. Site agency mẫu 27/10: 66/66 path trỏ cùng file CSS gộp. Tối ưu nào chỉ áp cho bản WebP thì Googlebot không nhận.
- CDN đứng trước origin (skill `cdn-speed-setup`):
  - CDN có thể chỉ tách HTML theo thiết bị, không theo `Accept`. Bunny 27/10: vary WebP chỉ áp cho ảnh, và không ghi đè được header `Accept` bằng edge rule (API trả 400). Bản HTML ở edge là bản của lượt đầu sau purge, rồi trả cho mọi người.
  - Hệ quả: mọi thay đổi HTML theo biến thể (CSS gọn, critical CSS) phải áp cho cả bản WebP lẫn bản plain. Nếu chưa áp được, purge CDN theo URL rồi làm nóng ngay bằng Accept có `image/webp`, đủ UA desktop và mobile.
  - Purge Bunny theo URL: gọi mặc định, không thêm `exactPath=true`. Tham số đó chỉ xoá bản desktop. URL kết thúc bằng `/` được thêm ký tự đại diện, nên purge `/muc/` có thể xoá cả bài con. Sau purge, kiểm header `cdn-cachedat` bằng cả 2 UA: giờ lưu phải sau giờ purge.
- Đo bản miss bằng tham số nằm trong `cache-exc_qs` (không vào cache). Tham số lạ khác vẫn tạo một bản cache mới với TTL đầy đủ, làm phình kho cache. Không dùng `utm_*`, `fbclid`, `gclid` (`do-dac.md` mục 2).
- Giảm miss cache, đã chạy trên production site agency mẫu 26–27/10/2026:
  - Đọc `x-litespeed-cache-control` của trang chính. Trang không có form hay nonce riêng mà nhận `private` thường do option LiteSpeed đặt tay (danh sách private, không cache). Bỏ URL khỏi các option đó. Site mẫu: một bài 685 ms mỗi lượt Googlebot, sau đó 9–12 ms từ lượt 2.
  - Thêm URL phân trang chuyên mục (`/<chuyên mục>/page/N/`) vào danh sách làm nóng. Site mẫu: 11/11 URL trượt, sau đó 11/11 trúng.
  - Chạy làm nóng trong 5 phút sau purge toàn site: cron dò vài bài mốc, thấy trượt thì làm nóng ngay. Site mẫu: Googlebot trượt cache HTML 40,8% (78/191) trước cron, 3,7% (8/219) sau cron.
  - Sitemap: cache 1 ngày và purge sitemap khi bài đăng, sửa hoặc rời trạng thái publish (mu-plugin). Bỏ `create_term` khỏi `purge-hook_all`. Giữ `edit_terms`, `delete_term` khi breadcrumb của mọi bài hiện tên chuyên mục.
- Giữ tên file CSS gộp ổn định. LiteSpeed đặt tên file gộp bằng md5 nội dung. Khối `<style>` inline đổi theo bài làm các bài cùng template nhận file gộp khác nhau.
  - Loại các khối đó khỏi file gộp bằng `optm-css_exc`. Mẫu bắt đầu bằng `^` so khớp đầu chuỗi thẻ, ví dụ `^<style id="wp-block-`. Tìm khối đổi theo bài bằng cách so HTML của 2 bài cùng template.
  - Site mẫu, production 26/10: 37 → 15 file gộp trên 32 trang mẫu. PSI mobile không xấu hơn.
  - Không đặt `optm-css_comb_ext_inl=0`. Option này đưa cả CSS từ domain khác ra khỏi file gộp, nên CSS nạp cuối body đè CSS theme. Staging site mẫu: trang blog lệch bố cục 218 px, LCP chuyên mục +584 và +848 ms.
  - Mọi thay đổi nguồn CSS gộp đổi md5 file gộp. Site đã có CSS gọn thì map mất hiệu lực tới khi tái tạo. Site mẫu 27/10, lượt gộp Font Awesome: 66 path dùng file gộp trong 44 phút. Đọc `wp-ucss` trước khi đổi.
- Object cache (Redis, Memcached), khi `wp_using_ext_object_cache()` trả true:
  - Ghi bằng WP API (`update_post_meta`, `update_option`, `wp_update_post`) thì cache tự cập nhật.
  - Ghi SQL thô vào posts, postmeta, options, terms thì gọi thêm `clean_post_cache($id)` hoặc `wp_cache_delete($tên, 'options')`. Không có cách khác thì `wp cache flush`. LiteSpeed Cache 7.9.1 ghi key không hết hạn, nên dữ liệu cũ hiện tới khi flush.
  - Xoá object cache trước, purge URL sau.
  - Chỉ `FLUSHDB` đúng DB của site. Không `FLUSHALL` khi Redis dùng chung cho nhiều site.
  - Chạy WP-CLI bằng đúng bản PHP của web (có `redis.so`). PHP CLI thiếu extension thì drop-in tự tắt, và lệnh ghi không xoá key trong Redis.
  - Sau khi chép DB production sang staging, chạy `wp cache flush` trên staging nếu staging bật object cache.
  - Rollback nhanh bằng cách đổi tên drop-in vẫn để option `object` bằng 1. Lần kế tiếp plugin lưu cài đặt, drop-in được tạo lại. Tắt hẳn bằng option, rồi mới gỡ gói PHP.
- Server OpenLiteSpeed và RAM:
  - `lswsctrl restart` (graceful) không thay tiến trình mẹ lsphp đang giữ socket. Đổi `LSAPI_CHILDREN` hay `LSAPI_MAX_IDLE` trong vhost chỉ có hiệu lực khi mẹ cũ thoát. Sau restart, chờ lúc vhost không có request PHP (3 mẫu liên tiếp), rồi `kill -TERM` mẹ cũ của đúng vhost đó. OpenLiteSpeed tự dựng mẹ mới ở request kế. Kiểm `.rtreport` (`CMAXCONN`) của mẹ mới.
  - Nhận tiến trình mẹ bằng socket của vhost, không bằng `cwd`. Mẹ và con rảnh có `cwd` là thư mục lsphp. Chỉ con đang xử lý request mới có `cwd` là thư mục site.
  - Kernel OOM có thể giết mysqld khi nhiều lsphp cùng chạy. Site agency mẫu 21/10 lúc 14:05: 83 tiến trình lsphp, mysqld bị giết. WP-CLI quét DB lớn chiếm 1,9–2,2 GB mỗi tiến trình; 19/10 kernel giết 8 tiến trình WP-CLI chạy song song.
  - Chạy WP-CLI theo lô với `-d memory_limit=512M`, mỗi lúc một tiến trình nặng. Crawl nội bộ tối đa 2 luồng.
  - Cách đã chạy khi chủ site duyệt: swap 2 GB, `OOMScoreAdjust` cho mysqld (`oom_score` 752 → 152), `LSAPI_CHILDREN` 20 → 10, gom vào một lần restart.
- Rollback: đặt lại option TTL rồi purge.

## Lớp 2 — ảnh LCP

- Dấu hiệu: phần tử LCP là ảnh, pha "load delay" lớn, ảnh LCP có `loading="lazy"` hoặc ưu tiên thấp.
- Sửa: bỏ lazy-load và gắn `fetchpriority="high"` cho đúng ảnh LCP của từng template. Dùng `templates/mu-plugin-lcp-priority.php`. Chỉ đánh dấu một ảnh mỗi trang.
- Ảnh hero khác nhau giữa mobile và desktop: chọn theo thiết bị bằng cùng điều kiện với vary `ismobile` của cache.
- Ảnh đầu bài viết: chọn ảnh ưu tiên theo toạ độ y đo bằng Chrome, không đoán bằng số ký tự giữa `</h1>` và ảnh.
  - Đo y của ảnh đầu bài ở mobile 412×823, DPR 1,75, chặn tracking. Đặt ngưỡng của mu-plugin từ số đo của mọi bài có ảnh ưu tiên, kèm khoảng an toàn về phía giữ ưu tiên.
  - Site agency mẫu 27/10/2026: ngưỡng 450 ký tự bỏ ưu tiên 4/136 bài có ảnh trên y 800 px. Đo 136 bài: ảnh trên y 800 px có tối đa 649 ký tự, nên ngưỡng mới là 700. Kiểm độc lập bắt lỗi này.
  - Khi bỏ ưu tiên một ảnh, xoá mọi `fetchpriority="high"` trong thẻ. Nội dung bài có thể đã ghi sẵn thuộc tính này, nên thẻ có 2 lần thuộc tính.
- Trang có bản sao hero cho desktop trong cùng HTML (thẻ `<img>` ẩn trên mobile, ví dụ class `show4desk`): đổi URL ảnh của thẻ mobile mà không đổi bản sao thì mobile tải 2 file. Thẻ ẩn bằng CSS vẫn tải nếu không lazy. Trên mobile, cho mọi thẻ cùng ảnh hero dùng chung một URL mới. Sau khi đổi, đo byte ảnh hero từng trang. Site agency mẫu 24/10: trang dịch vụ HCM và HN tăng từ 68 KB lên 110 KB ở bản v1; bản v2 dùng chung URL thì chỉ tải 1 file.
- Ảnh nền CSS không nhận `fetchpriority`. Đổi sang thẻ `<img>` hoặc thêm `<link rel="preload" as="image">` cho đúng file.
- Nén ảnh giữ URL: PNG bằng pngquant chất lượng 72–92, JPG chất lượng 82. Chỉ giữ bản mới khi cùng kích thước, nhỏ hơn ít nhất 15% và PSNR ≥34 dB. Site mẫu: 24 ảnh từ 13,9 MB xuống 4,4 MB.
- Rollback: chuyển mu-plugin ra ngoài. Ảnh gốc giữ trong backup, ghi đè lại bằng `cat >` để giữ owner.

## Lớp 3 — WebP và `srcset`

- Dấu hiệu: PSI báo "Serve images in next-gen formats" hoặc "Properly size images". `shot.mjs` ghi số ảnh WebP thấp.
- WebP:
  1. Sinh `<ảnh>.<đuôi>.webp` bằng `scripts/webp_gen.py` trên bản sao của `uploads/`. Ảnh gốc không đổi.
  2. Tải bản WebP lên server, giữ owner của web server.
  3. Bật thay URL trong HTML của LiteSpeed (`img_optm-webp`) nếu có.
  4. Thêm rewrite theo `Accept: image/webp` bằng `scripts/htaccess_webp.py add`. Rewrite phủ cả ảnh nền trong CSS.
- Site mẫu: 60.213 file, 2,5 GB còn 0,89 GB. Dung lượng trang giảm 20–55%.
- `srcset`: theme in thẳng URL ảnh gốc thì thêm `srcset` từ metadata của attachment (filter output buffer của plugin cache, đọc `wp_get_attachment_metadata`). Chỉ dùng cỡ cùng tỉ lệ.
- Đo bề rộng hiển thị trước khi đổi `srcset` hoặc `sizes`:

  ```bash
  node "$WPS/scripts/img_display_width.mjs" --url <URL> --expect '<chuỗi trong title>' --out <ev>/img-w.json --apply
  python3 -I "$WPS/scripts/img_width_report.py" <ev>/img-w.json
  ```

  Script đo ở 360, 412, 768, 1024, 1366, 1920 px, không bật cờ `mobile` của CDP. Báo cáo xếp ảnh thừa (file lớn hơn cần ở mọi viewport), thừa một phần và mờ. Chạy thêm `--dpr 2` cho màn hình nét.
- PSI báo ảnh hero "lớn hơn cỡ hiển thị" ở desktop: chạy thêm `--widths` dày ở khoảng PSI dùng (ví dụ 1180, 1280, 1330, 1366). Tạo bản đúng cỡ hiển thị đo được và thêm vào `srcset`.
  - Thêm cỡ mới cho mọi attachment trỏ cùng file ảnh. Theme có thể lấy ảnh từ nhiều trường ACF, mỗi trường một attachment.
  - Không tạo bản rộng hơn file gốc. Bản đó là ảnh phóng to, không nét hơn.
  - Site agency mẫu 27/10/2026, production: ảnh hero hiển thị 446 px ở khung 1180–1366. Mục "phân phối hình ảnh" của PSI desktop từ 37,4 KiB còn 4,2 KiB.
- PSI vẫn báo "tăng hệ số nén" sau khi đúng cỡ: mục tiêu của PSI xấp xỉ số điểm ảnh hiển thị chia 6 byte (khớp 40 ảnh của site mẫu 27/10). PSI hết báo khi file nhỏ hơn mục tiêu cộng 5 KiB. Ví dụ ảnh 446×417: mục tiêu 30.997 B, file phải dưới 36.117 B.
  - Ảnh có kênh alpha: đo SSIM trên màu nền thật của vị trí ảnh. Site mẫu: SSIM 0,9737 trên nền thật, nhưng 0,9616 trên nền đen hoặc trắng.
- Insight "Improve image delivery" (Lighthouse 12+) so cỡ file với cỡ hiển thị CSS, không nhân DPR. Ảnh 300 px hiển thị 210 px vẫn bị báo thừa, dù DPR 1,75 cần khoảng 370 px.
  - Không thu ảnh về cỡ CSS chỉ để hết cờ. Ảnh sẽ mờ trên máy DPR 2–3.
  - Nén lại file, rồi thêm cỡ `srcset` trung gian khi bề rộng hiển thị × 1,75 rơi vào khoảng trống lớn giữa 2 cỡ có sẵn. Site bán lẻ mẫu 31/10/2026: thumb danh mục hiển thị 199 px tải bản 600 px, vì `srcset` chỉ có 300w và 600w. Thêm bản 360w, mục ảnh trang chủ của PSI mobile từ 51 KiB còn 19 KiB.
  - Thêm cỡ cho một attachment: tạo `<tên>-<w>x<h>.<đuôi>` và bản `.webp` cạnh nó, rồi thêm vào mảng `sizes` của `_wp_attachment_metadata` bằng `update_post_meta`. Không gọi `wp_update_attachment_metadata`, vì plugin tối ưu ảnh (LiteSpeed) móc vào hook đó và có thể gửi ảnh đi tối ưu lại. Backup meta trước. Kiểm bằng `wp_get_attachment_image_srcset`.
- Sinh bản ảnh nhẹ cho đúng ảnh trang dùng (logo dải chạy, cỡ 400/560/720w, avatar 96w):

  ```bash
  python3 "$WPS/scripts/img_variants.py" --html <trang.html> --map /wp-content/uploads/<thư mục>/=<thư mục local> [--apply --out-html <trang-moi.html>]
  ```

  Không có `--apply` thì script chỉ in kế hoạch. Script chỉ giữ bản mới khi nhỏ hơn bản gốc, không đổi `sizes`, không ghi đè ảnh có sẵn. Cần Pillow, nên chạy không có `-I`.
- Bẫy:
  - Với `srcset` dạng `w`, kích thước nội tại của ảnh bằng giá trị `sizes`. Ảnh không có `width`/`height` trong CSS sẽ hiện đúng bằng `sizes`: lần thử `sizes="100px"` trên site mẫu 1 làm logo nhỏ đi và header thấp hơn. Chỉ đổi `sizes` khi CSS đặt kích thước cho ảnh (`height` cố định, hoặc `max-width:100%` và `sizes` không nhỏ hơn bề rộng hiển thị), và đã đo bề rộng ở 360–1920 px. Không thoả thì bỏ cỡ lớn khỏi `srcset`.
  - Không tự thêm `width`/`height` cho mọi ảnh. CSS của theme thiếu `height:auto` thì ảnh bị méo.
  - Ảnh màn hình đầu hiển thị khoảng 350 px trên mobile: PSI giả lập DPR 1,75, chỉ cần ảnh rộng khoảng 610 px. Thêm bản 640w vào `srcset`, giữ ảnh gốc cho DPR cao. Đo bề rộng hiển thị ở 390, 600, 768, 1024, 1440 px trước khi viết `sizes`. Site mẫu 2: ảnh LCP hub 47 KB còn 23 KB trên mobile.
  - Hero có `sizes` theo bề rộng màn hình (`92vw`, `calc(100vw - 40px)`): ở 412 px, DPR 1,75 trình duyệt cần 651–663 px, bản 600/640w không đủ nên tải bản gốc 900–1000 px. Thêm bản 720w vào `srcset`. Site mẫu 2: ảnh hero landing 70–95 KB còn 28–43 KB trên PSI mobile.
  - Logo trong dải chạy ngang hoặc lưới logo: file 214–600 px cho chỗ cao 26–44 px, mỗi logo thừa 12–15 KB. Sinh bản WebP cao gấp 2 lần chiều cao CSS lớn nhất (site mẫu 2: 88 px), sửa `width`/`height` theo tỉ lệ. Logo header theme: `srcset` 2 bản (DPR 2 và 3) với `sizes` bằng bề rộng hiển thị.
  - Ảnh trong thân bài: `sizes` mặc định của WordPress là `(max-width: 1200px) 100vw, 1200px`, nên desktop tải bản 1200 px cho cột chữ 720 px. Đo bề rộng cột ở 360–1920 px, rồi đặt `sizes` bằng filter `wp_calculate_image_sizes` cho `is_singular('post')`. Filter chỉ tác động ảnh chưa có `sizes` (ảnh của theme truyền `sizes` riêng thì giữ).
  - Ảnh đại diện PNG/JPG nặng: tạo attachment WebP mới cùng kích thước, tên có ngữ cảnh (`cwebp -q 86 -m 6 -sharp_yuv`), đặt làm ảnh đại diện. WordPress tự sinh cỡ con bằng WebP. Ghim `rank_math_facebook_image(_id)` vào attachment cũ để thẻ chia sẻ không đổi. Script: `scripts/featured_webp.sh`. Kiểm bài còn trả 200 trước khi làm (site mẫu 2: 12/13 bài ảnh nặng đã 301 sang newsletter, chỉ 1 bài cần sửa: 944 KB PNG còn 48,6 KB).
  - Lightbox đọc `img.currentSrc` sẽ mở bản nhỏ trong `srcset`. Sửa lightbox đọc `img.src` (ảnh gốc) trước khi thêm `srcset`.
  - Ảnh LCP mobile: không ép `sizes` nhỏ (ví dụ `(max-width: 768px) 1px`) để mọi điện thoại tải bản nhỏ nhất. Máy DPR 3 nhận ảnh thiếu pixel và mờ. Bản trong `srcset` phải đạt khoảng cỡ hiển thị × 2 khi nguồn đủ lớn. Site agency mẫu 05/11/2026: ảnh hero 358 px CSS tải bản 570 px, người duyệt báo mờ; dựng lại bản 786 px từ ảnh gốc, ảnh LCP +36 KB.
  - Không ghi đè ảnh gốc trong `uploads/` khi nén, và không sinh WebP từ ảnh đã nén. Site agency mẫu: đợt nén ép PNG gốc về 256 màu, WebP và ảnh LCP sinh sau đó bị nén chồng. Cách chẩn đoán và sửa: `image-seo-optimize` `references/anh-mo-sau-nen.md`.
  - Đo pixel ảnh: `naturalWidth` của ảnh có `srcset` dạng `w` đã chia density (file 1536 px báo 390). Lấy pixel thật bằng `new Image()` với `img.currentSrc`.
- Thuộc tính lặp trong `<img>` (`loading` hai lần): sửa ở một bộ lọc output chạy cuối (`litespeed_buffer_after`, ưu tiên cao), giữ thuộc tính đầu vì trình duyệt chỉ đọc thuộc tính đầu. Không vá từng ảnh theo ID trang. Staging không chạy tối ưu LiteSpeed thì thử hàm lọc trực tiếp trên HTML production đã lưu: số thẻ lặp về 0, giá trị đầu giữ nguyên, phần còn lại khớp byte. Site agency mẫu 05/11/2026: 16 thẻ × 4 biến thể trên 5 URL về 0; trang không lặp giữ nguyên byte.
  - OpenLiteSpeed giữ kết quả rewrite khoảng 1 giây. Chỉ trình duyệt rất cũ bị ảnh hưởng.
  - Nếu CDN (Cloudflare) cache ảnh, bật cache theo `Accept` ở CDN hoặc tắt rewrite cho host đó. OpenLiteSpeed bỏ qua lệnh `Header` trong `.htaccess`.
  - Thêm block `.htaccess` trên OpenLiteSpeed cần restart. Gom vào một lần restart.
- Rollback: `htaccess_webp.py remove` rồi restart. File WebP chuyển vào quarantine, không xoá.

## Lớp 4 — font

- Dấu hiệu:
  - Font chiếm trên 200 KB mỗi trang, file TTF, nhiều weight không dùng, `fontmap.mjs` thấy font hệ thống ở chữ chính, CLS do đổi font.
  - FCP observed của PSI dồn quanh một mốc ở mọi template (site mẫu 2: 2,3–2,5 s), trong khi main thread rảnh. Kiểm script nạp font trong `<head>` (bẫy đầu tiên dưới đây).
- Sửa:
  - Tự host WOFF2 subset latin + vietnamese. Chỉ giữ weight đang dùng. Font biến thiên gom nhiều weight vào một file.
  - Font của Google Fonts: tải bằng `scripts/gfonts_selfhost.py`. Script giữ subset, `unicode-range` và thứ tự rule như CSS của Google. Khai `font-weight` đúng độ đậm trang từng xin Google. Trang xin 1 độ đậm thì khai 1 giá trị.
  - So hiển thị trước và sau bằng `scripts/font_same.mjs`. Script so bề rộng chữ, khung phần tử và chiều cao trang. Chỉ giữ thay đổi khi kết quả là GIỐNG.
  - `font-display: swap`. Mặc định không preload font. Site đang preload thì A/B bỏ preload trên PSI trước khi giữ.
  - Một nguồn font cho cả site. Bỏ link Google Fonts thêm trong `header.php` hoặc plugin. Chưa tự host được thì nạp CSS Google Fonts bằng `media="print"` + `onload`, kèm `<noscript>`.
  - Trang cần hoãn hẳn Google Fonts (thường đi cùng hoãn GTM): nạp CSS font sau FCP. Dùng `PerformanceObserver` loại `paint` (`buffered: true`) cộng hẹn giờ 3 s, nạp một lần ở mốc đến trước. Không chờ sự kiện `load`: site agency mẫu 22/10, bản chờ `load` có 3/9 lượt FCP trên 2,5 s. Đặt `<meta charset>` ở đầu `<head>`, trước mọi script.
  - Font dự phòng có số đo: `python3 "$WPS/scripts/fallback_faces.py" --family "<Họ>" --web "<latin.woff2>,<vi.woff2>@400" --web "<latin-700.woff2>,<vi-700.woff2>@700" --sample <chữ trang thật.txt>`. Script in `@font-face` "<Họ> Fallback" có `size-adjust`, `ascent-override`, `descent-override`. Thêm `--out-dir <dir> --apply` để ghi CSS và `localtest.html` (trang kiểm `local()` nào khớp). Cần fontTools và brotli, nên chạy không có `-I`. Số này là điểm xuất phát. Hiệu chuẩn trên PSI theo `cls-chi-psi-thay.md`.
  - Font Awesome: chỉ giữ icon site dùng. `fa_subset/collect_icons.py` quét HTML, theme, dữ liệu Elementor ra danh sách icon. `fa_subset/build_fa.py` cắt font, sinh CSS tách `unicode-range`: trang tải bản cắt, icon ngoài bản cắt tự tải bản đầy đủ. Không có `--apply` thì hai script chỉ in báo cáo. Đổi `--stamp` khi nội dung đổi, vì file font cache 1 năm. Đo lại kích thước trước khi giữ.
- Đổi font hoặc cỡ chữ toàn site: thẩm mỹ quan trọng ngang số đo. Làm đủ 4 bước trước khi hỏi người duyệt chọn phương án:
  1. Chạy `fallback_faces.py`, thêm face dự phòng trước lượt A/B đầu tiên.
  2. Chụp so sánh 3 cột: hiện tại, đề xuất, site mẫu người duyệt chọn làm chuẩn. Chụp cả lúc đang tải (chỉ có face dự phòng) và lúc font đã về.
  3. Đo CLS và PSI mobile, desktop.
  4. Đưa câu hỏi A/B kèm ảnh và số đo vào trang chờ quyết.
  - Lỗi đã gặp ở site agency mẫu: font mới làm CLS mobile tăng 0 → 0,27 ở trang dịch vụ (18/10), một vòng A/B mất khoảng 60 phút. Ngày 20/10, người duyệt chọn `font-display: optional` từ câu hỏi chưa kèm số CLS. Đo sau đó còn CLS 0,19, nên phải hỏi lại.
- Số đã đo:
  - Site mẫu 1: TTF 77–81 KB mỗi file thành WOFF2 20–24 KB. Font mỗi trang trước đó là 484–1.172 KB.
  - Site mẫu 2: tự host font và in CSS theme vào `<head>` đưa FCP mô phỏng từ khoảng 1,3 s xuống khoảng 0,35 s.
  - Site mẫu 2, sau khi đổi theme: script nạp font gọi `document.fonts.load()` trong `<head>`. Chuyển lệnh này ra sau frame đầu thì A/B trên PSI tăng 60 → 94 (landing) và 70 → 91 (trang chủ). Trung vị mobile 11 template tăng 66 → 83.
  - Site mẫu 2: tự host Roboto thay Google Fonts ở 2 landing. A/B bằng bản HTML tĩnh tăng 68,5 → 85. Đo thật trên một landing tăng 62 → 92 mobile.
- Bẫy:
  - Không gọi `document.fonts.load()` trong `<head>` trước frame đầu. Chrome của PSI (HeadlessChrome 153) coi font nạp bằng API này là tài nguyên chặn hiển thị. Gọi sau `requestAnimationFrame` rồi `setTimeout(0)`. Chrome trên máy không tái hiện được độ trễ này, nên phải A/B trên PSI (`do-dac.md` mục 3).
  - Font biến thiên tự host phải còn bảng `STAT`. Nếu thiếu `STAT`, Safari và WebKit không áp độ đậm, còn Chrome vẫn hiện đúng. Sau mỗi lần cắt subset hoặc cắt trục, chạy lệnh dưới cho từng file. Sau đó chụp WebKit ở mọi độ đậm trang dùng (`npx playwright install webkit` nếu máy chưa có).

    ```bash
    python3 -c "import sys; from fontTools.ttLib import TTFont; f=TTFont(sys.argv[1]); print(sys.argv[1], 'THIẾU STAT' if 'fvar' in f and 'STAT' not in f else 'đạt')" <file.woff2>
    ```

    Lỗi đã gặp ở site bán lẻ mẫu 30/10/2026: file Google Sans Flex tự host (vi-latin, giữ trục `wght`) thiếu `STAT` và lên production lúc 01:30. Người duyệt thấy chữ mờ trên Safari lúc 17:07, nên phải hotfix bằng bản có `STAT`. Lệnh trên báo "THIẾU STAT" ở file lỗi và "đạt" ở file sửa.
  - Preload font trong `<head>` làm Chrome chờ font trước lần vẽ đầu: A/B ở site mẫu 2 (18/10/2026) cho LCP mô phỏng chậm thêm 0,8 s ở trang có LCP là chữ. Không preload font. Site agency mẫu 24/10, preload Montserrat cho `/website/` kể cả `fetchpriority="low"`: CLS 0,0993 → 0, nhưng FCP lab chậm 0,4–0,7 s tuỳ nhóm máy PSI (trung vị 1,09 → 1,80 s, 11/12 lượt), nên đã trả lại.
  - Font dự phòng khai `local('Arial')` kèm `size-adjust`. Máy đo PSI (HeadlessChrome trên Linux, đo 18/10/2026) khớp được `local('Arial')`, `local('Liberation Sans')`, `local('FreeSans')`, `local('NotoSans-Regular')`; không khớp `local('Roboto')`, `local('DejaVu Sans')`, `local('Arimo')`. Điện thoại Android thật không có Arial, chỉ có Roboto.
    - Thêm `local('Liberation Sans'),local('LiberationSans')` cho Linux thật và một họ dự phòng thứ hai dùng `local('Roboto')` cho Android, số đo tính riêng, đặt ngay sau họ Arial trong `font-family`.
    - Tính `size-adjust`, `ascent-override`, `descent-override` bằng fontTools (`fallback_faces.py`): bề rộng trung bình của chuỗi tiếng Việt thật (bỏ dấu) chia cho bề rộng của font dự phòng. Số lý thuyết lệch 1–3% so với số tối ưu trên PSI, và một số cho mọi bề rộng màn hình có thể không đủ (`cls-chi-psi-thay.md`).
    - Kiểm `local()` nào khớp trên máy PSI: đưa lên một trang thử khai mỗi tên một `@font-face` có fallback monospace, đo bề rộng chữ, chạy PSI, xem ảnh `final-screenshot` trong JSON. Không kết luận từ `font-family` thường: Chrome trên Linux nhận cả font thay thế tương đương.
    - CLS còn lại khi chữ trong đoạn đổi dòng lúc font thật thay font dự phòng: Chrome tính chữ đổi dòng là dịch chuyển, kể cả khi số dòng không đổi. Linux làm tròn bề rộng chữ theo pixel, nên Mac không tái hiện. Site mẫu 2: `p.lead` 0,086 trước và sau khi thêm Liberation, Roboto. Xem filmstrip `screenshot-thumbnails` để phân biệt với dịch chuyển bố cục.
    - Kiểm CLS trên PSI, không chỉ trên Mac.
    - Kết quả A/B trên PSI ở site mẫu 2 (18/10/2026), 5 trang × 3 lượt × 2 thiết bị:
      - Máy PSI khớp cả tên bold: `local('Arial Bold')`, `Arial-BoldMT`, `Liberation Sans Bold`, `LiberationSans-Bold`, `FreeSans Bold`. Không khớp `Noto Sans Bold`, `DejaVu Sans Bold`, `Roboto Bold`, `Arimo Bold`.
      - Chia face dự phòng theo từng độ đậm (6 dải, số đo tính lại bằng fontTools): CLS không đổi (0,086 → 0,086 và 0,08 → 0,081). Mac thì giảm (0,071 → 0,012). Không giữ.
      - Preload font của H1 và đoạn dẫn: CLS 0,08 → 0, nhưng LCP mô phỏng 1,5 → 2,3 s, điểm 98 → 95 ở trang có LCP là đoạn chữ. Không giữ.
      - `font-display: optional` triệt CLS ở landing nhưng không đổi trang dùng theme vẽ frame đầu bằng font dự phòng rồi gắn class đổi font (dịch chuyển do class, không do font về trễ). Lần xem đầu hiện font dự phòng, nên cần chủ site duyệt.
      - CLS dưới 0,1 do chữ đổi dòng khi đổi font: ghi vào báo cáo là giới hạn đã đo, không thử tiếp các cách trên.
  - `font-display: optional` cho font thân bài, chạy thật trên production site agency mẫu (21/10/2026), đã rollback:
    - CLS desktop bài viết 0,0996 → 0,0006, điểm 83 → 97.
    - Mobile tụt: 5/9 lượt PSI rơi vào chế độ FCP 2,1 s, vì Lantern coi font `optional` là chặn vẽ chữ. Điểm trung vị 3 lượt 99 → 94. LCP trung vị 3,2 s so với 1,46 s của bản cũ.
    - Khách mở trang trong tab mới thấy font dự phòng, kể cả khi font đã nằm trong cache đĩa.
    - `optional` không kín CLS khi CSS gộp nạp trễ khai thêm `@font-face` cùng họ: Chrome áp font đã tải. Mô phỏng PSI mobile 430 px: CLS 0,19.
    - Kết luận: không dùng `optional` cho font thân bài khi chưa A/B trên PSI cả mobile lẫn desktop.
  - LiteSpeed `optm-css_font_display=1` ép `font-display: swap` vào mọi `@font-face` trong HTML và CSS gộp. Sửa riêng file CSS font không đủ. Muốn giữ giá trị khác mà không đổi option: khối font inline có `data-no-optimize="1"`, không chép khối font vào critical CSS, và filter `litespeed_buffer_after` trả lại giá trị sau bước tối ưu.
  - Grep mọi stack font trong CSS của trang, kể cả biến CSS và CSS lấy từ landing gốc: `grep -o '"<web font>",system-ui'`. Stack rơi thẳng từ web font xuống `system-ui` thì chữ chờ font hiện bằng font hệ thống. Mac dùng San Francisco gần bề rộng web font. Máy Linux của PSI dùng font rộng hơn nhiều. Site mẫu 2, trang thanh toán AAM: Mac đo 0,03, PSI đo 0,24–0,28. Chèn face dự phòng có `size-adjust` của theme vào sau web font (vá ở bước build nếu CSS lấy từ nguồn khác): PSI còn 0,012.
  - `unicode-range` chồng nhau (ă, đ, ơ, ư nằm trong cả subset `vietnamese` lẫn `latin-ext`): trình duyệt chọn face khai báo sau. Khai `vietnamese` sau `latin-ext` thì trang tiếng Việt không tải file latin-ext. Site mẫu 2: bớt 1 file, 24 KB ở 3 trang, ảnh chụp lệch 0,0%.
  - Google trả file tĩnh nhỏ hơn khi URL chỉ xin 1 độ đậm (Roboto 800 latin 16 KB, bản biến thiên 36 KB). Trang chỉ dùng 1 độ đậm thì tải riêng URL đó.
  - Chữ "đ" nằm ở subset latin-ext của Google Fonts. Subset tự cắt phải gồm U+0110, U+0111.
  - Customizer › Additional CSS hoặc critical CSS có thể chứa `font-family … !important`. Đổi font thì sửa cả các chỗ đó.
  - Kiểm dấu tiếng Việt (ă, ơ, ư, ệ, ỗ, ữ, đ) ở mọi weight sau khi đổi.
- Rollback: khôi phục meta hoặc file CSS font từ backup. File WOFF2 để lại không ảnh hưởng.

## Lớp 5 — CSS chặn hiển thị

- Dấu hiệu: FCP mobile trên 1,8 s, PSI báo "Eliminate render-blocking resources" hoặc "Reduce unused CSS", CSS inline lớn trong `<head>`.
- Sửa theo thứ tự:
  1. Plugin in CSS lớn vào `<head>` thì chuyển ra file (site mẫu: Max Mega Menu `css=fs`, HTML giảm khoảng 189 KB).
  2. Gộp CSS ngoài và inline bằng LiteSpeed. Chụp lại để kiểm thứ tự cascade.
  3. Critical CSS theo template bằng `scripts/ccss_gen.mjs`. Chèn `<style>` trước file CSS gộp. Nạp file gộp bằng `media="print"` + `onload`, kèm `<noscript>`.
  4. Cắt CSS không dùng (UCSS) khi file gộp lớn hơn khoảng 100 KB brotli hoặc vẫn gây TBT. Dùng skill `wp-ucss`: CSS gọn theo file gộp, kiểm computed style từng trạng thái giao diện, chỉ đổi link ở path đã kiểm. Site agency mẫu 26–27/10: file gộp 1,41 MB (174 KB brotli) còn 28–50 KB brotli. PSI mobile trung vị 3 lượt của 7 template từ 94 lên 98; trang chủ LCP 2,9 → 2,3 s, FCP 2,0 → 1,4 s.
  5. Có CSS gọn thì dựng critical CSS từ CSS gọn, không từ file gộp. Đọc bảng "Đã A/B và không áp" trước: critical 85–113 KB dựng từ CSS gọn đã xấu hơn ở 5/6 trang.
- Critical CSS bắt buộc A/B từng template: đo `perf_probe.mjs` có và không có critical CSS, cùng PSI. Site mẫu: 5/11 template chậm hơn và đã tắt (trang chủ, tuyển dụng, dịch vụ, blog, giới thiệu desktop).
- Bẫy:
  - Lấy CSS đầu vào từ CSSOM của Chrome, không lấy text gốc. Text gốc có đoạn lỗi cú pháp, penthouse sửa và đưa quy tắc Chrome đã bỏ vào critical CSS.
  - Không dùng `rel="preload" as="style"` cho file gộp. Chrome tải preload với ưu tiên cao nhất, Lighthouse vẫn tính file đó chặn FCP.
  - Bỏ `@import` khỏi critical CSS inline.
  - File gộp lớn vẫn phải parse sau FCP. Lighthouse tính phần đó vào TBT.
  - Icon font có thể hiện ô vuông vài trăm ms khi chỉ có critical CSS. Không thêm `@font-face` icon vào critical CSS nếu file font nặng.
  - LiteSpeed bật "CSS Combine External and Inline" (`optm-css_comb_ext_inl` = 1) gom cả `<style>` inline in ở `wp_head` vào file gộp tải async. Nếu `@font-face` của font chữ chính nằm trong `<style>` đó, lần vẽ đầu chỉ có critical CSS nên chữ hiện bằng font hệ thống, rồi đổi dòng khi file gộp tải xong. Site mẫu: H1 bài viết 2 dòng thành 3 dòng, CLS desktop 0,35. Sửa: nối `@font-face` và biến font vào đầu critical CSS qua filter của mu-plugin, dùng chung hàm sinh CSS với `wp_head`. Kiểm: chặn `*.css` trong Chrome rồi so khung phần tử với bản đủ CSS; chỉ còn khác chiều cao phần dưới màn hình đầu.
  - Dựng lại critical CSS sau mỗi lần đổi font, header hoặc tắt plugin dựng trang. Site mẫu: critical CSS dựng trước đợt đổi font làm header co 19 px khi file gộp tải xong, CLS desktop 0,53.
  - Critical CSS kèm file gộp 1,48 MB nạp async: FCP giảm nhưng TBT tăng khoảng 244 ms vì Chrome parse file lớn sau FCP. Site agency mẫu 26/10 đã trả lại bản này. Làm CSS gọn trước, rồi mới xét critical CSS.
  - Critical CSS thiếu quy tắc ẩn của `.screen-reader-text` làm link "skip to content" hiện ra trong lần vẽ đầu, rồi biến mất: CLS 0,026–0,028. Desktop thiếu quy tắc của menu thả xuống thì menu con hiện ra trong lần vẽ đầu. Kiểm bằng cách so khung phần tử giữa bản "chỉ critical CSS" và bản đủ CSS trong 1,5 màn hình (`ccss_gap.mjs` của `wp-ucss`).
- Rollback: chuyển thư mục critical CSS ra ngoài. Mu-plugin thấy thiếu file thì giữ HTML cũ.
- Trang dài, `mainthread-work-breakdown` của PSI báo `styleLayout` từ 500 ms: thêm `content-visibility:auto` cho section từ thứ 3 trở đi.
  - `contain-intrinsic-size: auto <chiều cao>`: lấy chiều cao trung bình đo thật của section, tách mobile và desktop. Site mẫu 2: landing mobile ~2.600 px, desktop ~1.600 px. Ước tính 900 px làm chiều cao trang lệch 50%.
  - Lấy chiều cao content-box (trừ padding và border), vì padding của section vẫn tính thêm ngoài `contain-intrinsic-size`. Đo khi đã gỡ khối CSS `content-visibility` khỏi trang.
  - Kiểm: chiều cao trang lúc tải, trước khi cuộn, bằng chiều cao sau khi cuộn hết (lệch tối đa vài px).
  - Đo lại mỗi khi DOM của section đổi (bỏ khối, thẻ gọn hơn, khối ẩn theo hạn).
  - Site bán lẻ mẫu 31/10/2026: bản đầu lấy chiều cao gồm padding, trang chủ dài thêm 660 px (mobile) và 800 px (desktop) trước khi cuộn tới.
  - Kiểm phần tử `position:fixed` (thanh giá, nút nổi) nằm ngoài section. Section có `content-visibility` trở thành khung chứa của phần tử fixed bên trong.
  - Bẫy: nhảy tới `#mục` bị lệch vì section phía trên còn mang chiều cao ước tính. Khi người xem bấm link `#mục` hoặc mở URL có `#`, gắn một class trên `<html>` để tắt `content-visibility` trước khi trình duyệt cuộn (listener `click` ở capture phase).
  - Chrome headless không chạy cuộn mượt ổn định, nên không dùng bài thử bấm link trong headless để kết luận lệch hay đúng. So vị trí mục sau khi tắt class với bản production.
  - Bẫy: axe của PSI không vẽ được section chưa hiện. Kết quả là báo nhầm tương phản ở section nền tối và bỏ sót lỗi thật. Cách kiểm và sửa: `agentic-browsing.md` mục 3.

## Lớp 5b — chi phí render của theme

Rà lớp này trước khi nghiệm thu, kể cả khi điểm đã cao. Site mẫu 2 (18/10/2026): agent định nghiệm thu ở trung vị mobile 85. Người duyệt chỉ ra việc còn ở tầng theme. Sau đợt rà theme (bảng dưới) và hoãn GTM đã duyệt (lớp 7), điểm mobile đạt 97–100.

Đo trước:

```bash
python3 -I "$WPS/scripts/psi_con_tru.py" <ev>/psi-<mốc> --mt
grep -rnoE 'backdrop-filter|will-change|@import' <thư mục theme> --include='*.css' | cut -d: -f1 | sort | uniq -c
```

Trả lời từng câu. Câu nào "có" thì ghi việc sửa vào plan, hoặc ghi lý do giữ vào bảng "Phần còn trừ điểm".

| Câu hỏi kiểm | Cách sửa | Số đã đo (site mẫu 2) |
|---|---|---|
| `styleLayout` mobile từ 500 ms ở trang dài? | `content-visibility` cho section từ thứ 3 (lớp 5) | 645 → 197 ms, trang chủ 360 → 138 ms |
| Header hoặc thanh cố định dùng `backdrop-filter` trên nền gần như đặc? | Nền đặc, bỏ blur | 23 chỗ `backdrop-filter`. Header nền 96–97% trắng, blur gần như không thấy |
| `will-change` khai cố định cho nhiều phần tử? | Chỉ giữ cho phần tử đang chuyển động | |
| CSS có `@import`? | Nối vào file gốc hoặc dùng `<link>`. `@import` tạo chuỗi request nối tiếp | |
| CSS của plugin form (Contact Form 7…) nạp ở mọi trang, hoặc nạp bằng file chặn hiển thị? | Chỉ nạp ở trang có form. File nhỏ thì in thẳng vào `<head>` | CSS CF7 3 KB in vào `<head>`: trang Liên hệ hết tài nguyên chặn hiển thị |
| Chưa có speculation rules phù hợp? | `prefetch` mức `moderate` (WordPress mặc định `conservative`). Không prerender. Loại trang thanh toán, cảm ơn | |
| Có `preconnect`, `dns-prefetch` tới host mà trang không dùng? | Gỡ thẻ hint theo từng trang bằng mu-plugin. Giữ host còn xuất hiện trong HTML ngoài thẻ hint, hoặc trong CSS, JS local của trang | Site agency mẫu 27/10, production: A/B PSI "không đổi" ở 4/4 trang × thiết bị. Lighthouse nêu host thừa 4 → 1. Lợi ích tối đa khoảng 50 ms |
| Font, ảnh, CSS, JS có cache trình duyệt dưới 1 năm (`max-age`, `ExpiresByType`)? | Lớp 1, kèm luật đổi tên file | 7 ngày → 1 năm |
| Script đọc layout ngay khi nạp trang (PSI báo `forced-reflow`)? | Lớp 6 | 73 ms ở thanh tiến độ cuộn |
| Khối khuyến mãi có hạn (Flash Deal, đồng hồ đếm ngược) vẫn in khi đã hết hạn? | Template không in khối khi hết hạn. Đọc ngày bằng múi giờ của site. Đặt TTL cache trang bằng số giây còn lại (`litespeed_control_set_ttl`), để trang tự làm mới đúng lúc hết hạn | Site bán lẻ mẫu 31/10/2026: khối đã hết hạn vẫn in 2 dãy thẻ sản phẩm |
| Trang dài có thẻ lặp nặng (thẻ sản phẩm có nút, nhãn thông số)? | Bản thẻ gọn chỉ ở trang đó, kèm công tắc tắt bằng file. Kiểm các template khác bằng HTML không qua cache. Kiểm lượt nạp AJAX vẫn trả thẻ đầy đủ | Site bán lẻ mẫu 31/10/2026: trang chủ 2.960 → 2.331 phần tử DOM, 3 template khác không đổi |

Rollback: mỗi việc ghi file đã sửa và bản backup. Speculation rules và CSS form trả lại bằng cách gỡ filter đã thêm.

## Lớp 6 — JS

- Dấu hiệu: TBT cao, long task trong `--detail`, thư viện nạp 2 lần, request 404/410 cho file JS hoặc CSS.
- Trước khi sửa JS, trace long task theo hàm cho các template có TBT cao, cả 2 thiết bị:

  ```bash
  node "$WPS/scripts/trace_fn.mjs" --url <URL sạch> --dev mobile --cpu 4 --runs 3 --expect '<chuỗi trong title>' --out <ev>/trace-<tên>-m.json
  ```

  - Script in từng long task trên 50 ms, lệnh gọi JS từ 8 ms kèm tên hàm, file, dòng, và thời gian layout bên trong. Trường `nguon` là `js` hoặc `layout`.
  - Chỉ sửa file JS có lệnh gọi trong long task. Task chỉ có `layout` là chi phí của HTML và CSS: xét lớp 4 (font về nhiều đợt) và lớp 5 (CSS gộp lớn).
  - Template còn dùng file CSS gộp đầy đủ thì làm `wp-ucss` trước khi sửa JS.
  - Site agency mẫu 27/10/2026 (WordPress, LiteSpeed Delay JS): bên thứ ba chặn 0 ms trong lượt đo. Long task JS duy nhất là hàm khởi tạo slider (50–87 ms, CPU 4x). Một script sửa lỗi lazy-load bị nghi trước đó có 0 lệnh gọi từ 8 ms ở 6 trang × 2 thiết bị, nên không sửa. Một template mobile dùng file CSS gộp đầy đủ sau đợt đổi DOM có TBT trung vị 281,5 ms, toàn bộ là layout.
- Sửa:
  - Script đồng bộ còn lại ở cuối `body` (ví dụ `wp-includes/js/dist/hooks.min.js`) làm PSI báo chuỗi phụ thuộc mạng. Thêm `defer` bằng filter output buffer, chỉ khi mọi script dùng nó đã `defer` và đứng sau.
    - Giải mã các script `src="data:text/javascript;base64,…"` mà plugin cache tạo từ script inline. Kiểm không có lệnh đồng bộ nào gọi `wp.hooks` hoặc `wp.i18n`.
    - Site bán lẻ mẫu 31/10/2026: trang chủ, PSI hết báo chuỗi `hooks.min.js` 375 ms, 0 lỗi JS ở 8 lượt Chrome.
  - Bỏ thư viện trùng trong HTML bằng mu-plugin. Giữ bản nạp sau cùng để cascade không đổi. Site mẫu: jQuery 3.6.0 trùng jQuery của WordPress, Slick 2 nguồn, Bootstrap 2 lần, Font Awesome 5 và 7.
  - Bỏ thẻ trỏ tới file không tồn tại trong thư mục theme.
  - Delay JS: phân loại script bằng Jev `asset-delay`, chỉ dùng nhãn từ 0,7. Loại `render_critical` và `early_interaction` khỏi danh sách delay.
- Bẫy:
  - Bỏ bản jQuery trùng có thể làm slider khởi tạo 2 lần. Site mẫu giữ nguyên JS ở 2 template dịch vụ vì lý do này. Luôn chạy `shot.mjs` với `--vis` cho slider và menu.
  - Script tự tải thư viện từ CDN sau vài giây (ví dụ script khởi tạo slider của theme) tạo long task. Chỉ giữ ở trang có phần tử cần nó.
  - PSI báo `forced-reflow`: tìm code đọc `scrollHeight`, `offsetTop`, `getBoundingClientRect` ngay khi nạp trang. Ví dụ thanh tiến độ cuộn gọi `draw()` lúc nạp (73 ms). Chỉ vẽ khi trang đã cuộn sẵn (`if (scrollY) requestAnimationFrame(draw)`). Nếu PSI vẫn báo (26–44 ms, sự kiện cuộn vẫn xảy ra trong lúc ghi trace): tính chiều cao trang trong `ResizeObserver` (chạy sau layout, không ép layout), `draw()` chỉ đọc `scrollY`. Giữ nhánh tính một lần cho trình duyệt không có `ResizeObserver`.
  - Trang đổi bố cục theo dữ liệu bằng JS `defer` (trang thanh toán ẩn khối QR khi không có đơn, trang cảm ơn đổi trạng thái): JS chạy sau lần vẽ đầu nên cả khối co lại. PSI luôn mở trang không có dữ liệu. Site mẫu 2: CLS mobile 0,92 ở 3 trang thanh toán.
    1. In một script đồng bộ nhỏ trong `<head>` (chỉ ở trang có phần tử của trạng thái đó), đọc dữ liệu theo đúng điều kiện của JS trang, gắn class lên `<html>`. CSS theo class ẩn hoặc hiện khối bằng `!important` (thắng `[hidden]{display:none !important}`).
    2. Chữ đổi theo trạng thái (H1, lời chào): `MutationObserver` điền ngay khi phần tử đứng sau đã có trong DOM, tức phần tử cần điền đã parse xong.
    3. Lấy tên khoá storage và regex mã từ chính file JS của trang (PHP đọc file, regex chặt). Không đọc được thì không in gì. Site mẫu 2: 2 trong 3 trang dùng khoá `tagOrder`, trang còn lại dùng `aamOrder`. Bản đầu viết cứng một khoá nên đã ẩn khối QR của khách có đơn thật trên staging.
    4. Đo từng nhánh bằng `scripts/cls_trace.mjs`: không dữ liệu, có dữ liệu (`--session`), dữ liệu của trang khác, chế độ demo. Mọi nhánh phải hiện đúng khối và CLS dưới 0,05. Site mẫu 2: 0,92 → 0,03 (không đơn), 0,0015–0,03 (có đơn).
    5. Chặn tracking khi đo, không chặn ảnh chức năng: chặn ảnh QR làm ảnh lỗi, JS ẩn ảnh và tạo shift giả 0,066.
  - JS lấy từ nguồn dùng chung của entity khác: vá ở bước build của site mình, không sửa file nguồn.
  - Plugin mục lục Fixed TOC (`ftwp`) in mục lục ở trạng thái `ftwp-hidden-state` (`position:fixed`, chiều cao 0 trong luồng trang). JS đưa mục lục vào luồng trang sau 0,6–1,3 s nên nội dung bên dưới nhảy. Desktop mục lục mở sẵn (300–800 px), mobile thu gọn (57 px). Site mẫu: CLS desktop 0,04–0,07 ở bài có mục lục trên màn hình đầu. Sửa bằng CSS giữ chỗ đúng trạng thái sau JS: `#ftwp-container-outer.ftwp-in-post #ftwp-container.ftwp-hidden-state{position:static;opacity:1;visibility:visible;z-index:auto}`, và ẩn `#ftwp-list` ở ≤768 px (đọc `mobileMaxWidth`, `contentsColexpInitMobile` trong `fixedtocOption` của trang). Plugin khác có trạng thái chờ JS tương tự: so khung phần tử khi tắt JS và khi bật JS.
  - Thử CSS sửa CLS trước khi deploy: chèn `<style>` vào HTML qua CDP `Fetch.enable` (giai đoạn Response) rồi đo layout shift. `Page.addScriptToEvaluateOnNewDocument` chạy trước khi có `document.documentElement`, nên style chèn bằng cách này không áp ở lần vẽ đầu và cho kết quả sai.
  - Link neo trong trang (`#contact`, nút "Liên hệ") dừng sai đích khi có Delay JS: lần chạm đầu nạp JS của theme, slider khác của theme khởi tạo và trang co lại sau khi trình duyệt đã tính vị trí cuộn. Site agency mẫu 28/10/2026: trang dịch vụ desktop co 6.838–9.264 px, link dừng sai 12/24 lượt (quá đích tới 2.479 px).
    1. Đo trước: bấm link ở load + 0, 0,3, 1, 5 s và bấm nút ở hero. Đạt khi dừng trong ±200 px quanh đích. Đo chiều cao trang trước và sau lần chạm đầu để biết khối nào co.
    2. Sửa bằng hàm theo dõi trong một script có sẵn: khi khách bấm link `#…` cùng trang, nếu trang đứng yên mà đích lệch quá 150 px thì cuộn lại đích, tối đa 3 lần trong 6 s, dừng ngay khi khách tự cuộn. Site mẫu: 37/37 lượt chèn thử và 17/17 lượt production đạt, CLS khi vào thẳng đích 0–0,019.
    3. Đặt hàm này ở script in trên mọi trang có link neo. Site mẫu đặt trong script chỉ in ở trang có slider, nên một trang không có slider vẫn dừng quá đích 1.877–4.398 px.
- Rollback: khôi phục bản mu-plugin trước đó từ backup.

## Lớp 7 — bên thứ ba và tracking

Đổi container, sửa sự kiện GA4 hay Ads, hoặc cài loader hoãn GTM: làm theo skill `wp-gtm-tracking`. Mục này giữ phần đánh đổi tốc độ.

- Dấu hiệu: GTM, Pixel, Hotjar, chat widget, YouTube embed chiếm TBT hoặc byte lớn.
- PSI báo `gtag/js?id=AW-…` 2 lần, một bản có `&cx=c`: thư viện Ads nạp trùng. Sửa theo `wp-gtm-tracking`, `kiem-va-ap.md` mục 8. Đo TBT và LCP trước và sau, vì gỡ sai bản có thể làm TBT tăng.
- Không cho script bên thứ ba bắt đầu sớm hơn mốc hoãn đã A/B. Lantern tính mọi script bắt đầu trước LCP quan sát vào LCP mô phỏng. LCP quan sát của PSI mobile thường 2,3–2,6 s vì cổng vẽ, nên script ở load + 1,4 s vẫn lọt vào. Site bán lẻ mẫu 31/10/2026: thư viện AW 147 KB nạp sớm 600 ms, LCP mô phỏng 2,2 → 3,7–3,85 s ở 3/6 lượt. Kiểm bằng `networkRequestTime` của script so với `observedLargestContentfulPaint`.
- Không tự sửa. Đổi thời điểm nạp tracking là đổi dữ liệu đo lường. Người duyệt đồng ý từng mục.
- Đề xuất được phép: tải chậm YouTube embed bằng ảnh thumbnail, gỡ site Hotjar không dùng, rà tag trùng trong GTM.
- Ảnh thumbnail YouTube: dùng `https://i.ytimg.com/vi_webp/<id>/maxresdefault.webp` (khoảng 60 KB), không dùng `vi/<id>/maxresdefault.jpg` (khoảng 165 KB). Nếu video thiếu bản maxres, bản WebP trả 404 và bản JPEG trả ảnh xám 120px. Cho JS đổi về `hqdefault`, rồi về JPEG. Kiểm trong `onload` bằng `naturalWidth < 200`, không chỉ trong `onerror`. Ảnh xám 120px trả mã 404 kèm thân ảnh hợp lệ, nên trình duyệt chạy `onload` và `onerror` không chạy (site agency mẫu, 19/10/2026). Ví dụ: file block PHP và JS trong theme của một site mẫu khác, 18/10/2026.
- Trước khi đề xuất trễ GTM: đối chiếu pageview GA4 với số phiên, vì khách không tương tác có thể không được ghi.
- Kiểm kê container trước khi đề xuất: `python3 -I "$WPS/scripts/gtm_inventory.py" --url <trang>`. Script đọc `gtm.js` công khai và in số tag theo loại, sự kiện GA4, sự kiện Pixel, trình nghe click, cùng hệ quả nếu hoãn.
- Khi người duyệt hỏi "hoãn GTM có mất gì", trả lời theo bảng sau:

| Cách nạp | Dữ liệu mất | Điểm PSI |
|---|---|---|
| Giữ nguyên | Không | TBT giữ nguyên |
| Hoãn đến khi người xem tương tác | Pageview và PageView Pixel của lượt thoát ngay. LPV của Meta. Cú click link đầu tiên, vì trình nghe `__lcl` chưa chạy (loader mẫu từ v1.12 tái phát `gtm.linkClick`, trừ link mở cùng tab). gclid, fbclid khi người xem chuyển trang trước khi GTM chạy | Tăng nhiều nhất. Site mẫu 2: bản bỏ GTM có TBT 0 |
| Hoãn theo thời gian ngắn (2–3 s sau load) | Chỉ lượt xem rất ngắn | Không tăng. Site mẫu 2: hoãn 2 s, Lighthouse vẫn ghi đủ GTM, gtag, Pixel ở 12/12 lượt, TBT 200–500 ms |
| Thao tác đầu tiên hoặc X s sau load, X lớn hơn lúc Lighthouse dừng ghi | Lượt xem không thao tác và thoát trước X s | Như hoãn đến khi tương tác. Site mẫu 2: X = 4 s cho TBT = 0 ở 12/12 lượt, điểm mobile 97–100. Chọn 5 s |

- Lighthouse 13.5 dừng ghi trace sau khi đủ 4 điều kiện: FCP + 1 s, load + 1 s, mạng yên 1 s, rồi CPU yên khoảng 1,3 s. Trace không thể dừng trước load + 2,3 s. Site mẫu 2 đo được load + 2,3 đến 3,1 s. Script chạy trước lúc trace dừng thì bị tính đủ vào TBT (Lantern bỏ qua độ trễ của timer).
- Chọn X = max(`observedTraceEnd` − `observedLoad`) của 3–5 lượt PSI khi đã hoãn GTM, cộng 1,5–2 s. Lấy 2 số này ở `audits.metrics.details.items[0]`. Không dùng `requestIdleCallback`: callback thường chạy ngay sau load, vẫn trong trace.
- Lighthouse không gửi sự kiện chuột, chạm, phím hay cuộn trong lúc ghi trace. Loader nghe `pointerdown`, `touchstart`, `keydown`, `wheel`, `scroll`, `mousemove` (`passive`), nạp `gtm.js` một lần.
- Khởi tạo `dataLayer` và đẩy `gtm.start` ngay trong `<head>`, để sự kiện đẩy vào trước khi GTM chạy vẫn được xử lý.
- URL có `gclid`, `gbraid`, `wbraid`, `fbclid`, `ttclid`, `utm_*` thì nạp ngay: giữ nguồn quảng cáo và LPV của Meta. PSI không đo các URL này nên điểm không đổi.
- LiteSpeed Cache "Delay JS" chỉ nạp script khi có tương tác, không có hẹn giờ. Muốn có hẹn giờ: loại loader khỏi Delay JS (`optm-js_defer_exc`) và dùng loader riêng. Site bật Guest Mode: loại thêm khỏi `optm-gm_js_exc`. Kiểm cả hai danh sách bằng `ls_exclusions_check.py --script gtm-delay-loader` (`fcp-guest-mode.md`).
- Không kiểm loader bằng script tự cuộn trang trước `--eval` (ví dụ `cdp.mjs` của workstream cũ, không có trong skill): sự kiện `scroll` làm loader chạy sớm. Dùng bản không cuộn khi đo mốc giờ. Chặn domain GTM, Facebook bằng `--host-resolver-rules` để bài thử không gửi hit thật.
- Mẫu cài được cho site khác: `templates/gtm-delay-loader.php` (mu-plugin, 3 hằng số, `data-no-optimize` cho LiteSpeed). Kiểm sau khi cài: `node scripts/gtm_delay_check.mjs --url <trang> [--now-url <trang cảm ơn>]`. Script chặn domain tracking, không cuộn, thử 4 trường hợp: không thao tác, phím Shift, URL có `utm_`, trang chuyển đổi. Bản gốc chạy trên production site mẫu 2: `inc/gtm.php` của theme (A/B ở `evidence-pagespeed-dot-a-2026-10-18/psi-ab-gtm/`).
- Loader tái phát click link. Khách bấm link (Zalo, `tel:`, `mailto:`) ở thao tác đầu, trước khi `gtm.js` chạy xong. Bộ nghe Link Click của GTM chưa cài, nên click đó mất. Loại sự kiện này thường là chuyển đổi chính. Mẫu từ v1.12 ghi lại tối đa 5 link bị bấm trong lúc chờ, rồi đẩy `gtm.linkClick` vào `dataLayer` khi `gtm.js` nạp xong. Site agency mẫu 22/10: bản không tái phát mất click Zalo đầu tiên trên trang đào tạo.
  - Giới hạn: link mở cùng tab làm trang rời đi trước khi `gtm.js` nạp, nên không tái phát được. Trigger "All Elements" dùng `gtm.click`, loader không tái phát sự kiện này. Ghi cả hai giới hạn vào bảng "hoãn GTM có mất gì" khi trình duyệt.
  - Site đã cài mẫu v1.11 trở về trước: cài lại mẫu mới.
- Kiểm event thật sau khi cài (staging hoặc bản thử): ghi lại request tới GA4, Ads, Pixel nhưng chặn gửi, che mã đo lường khi lưu evidence. Xác nhận đủ `page_view`, click chuyển đổi, conversion Ads, Pixel. Chờ ít nhất 8 s sau thao tác: event click của GA4 đến sau khoảng 5 s (site agency mẫu 22/10).
- Mọi cách hoãn đều giữ GTM tải ngay ở trang thanh toán và trang cảm ơn. Đơn ghi phía server (form, cổng thanh toán) không bị ảnh hưởng.
- Trang thanh toán, cảm ơn giữ GTM nạp ngay thì TBT còn lại đến từ tracking. Site mẫu 2: Meta Pixel (`fbevents.js` + `signals/config`) 330–510 ms, `gtag/js` của GA4 140–290 ms, `gtm.js` 60–170 ms, JS riêng của trang 5–19 ms. Điểm mobile 81–94 sau khi sửa CLS. Không còn việc gì ở phía trang. Ghi vào báo cáo 3 lựa chọn cho người duyệt: giữ nguyên (trang thường `noindex`, điểm chỉ là số lab), hoãn GTM cả ở trang này (sự kiện đẩy vào `dataLayer` trước vẫn được xử lý, chỉ mất khi khách rời trang trước khi GTM nạp), hoặc sửa container (Pixel bắn theo sự kiện thay vì mọi trang).
- CrUX đã đạt thì đề xuất giữ nguyên, vì lợi ích chủ yếu là điểm lab. Site mẫu 2: GTM, gtag và Pixel nặng khoảng 570 KB, TBT mobile 221–588 ms. Người duyệt giữ nguyên lúc đầu, rồi duyệt hoãn 5 s khi muốn tối đa điểm PSI.

## Đã A/B và không áp

Đọc bảng này trước khi đề xuất một việc trong cột đầu. Nếu site mới có cùng điều kiện, ghi số ở đây vào plan và chỉ thử khi có lý do mới. Số là PSI mobile lab, trung vị nhiều lượt, site agency mẫu 26–27/10/2026 (OLS, LiteSpeed Cache, Guest Mode). Hàng có ghi "lab staging" dùng Lighthouse local trên staging, không phải PSI.

| Việc | Điều kiện | Kết quả A/B | Xét lại khi |
|---|---|---|---|
| Critical CSS dựng từ file gộp (lớp 5) | File CSS gộp 1,4 MB, chưa có CSS gọn | FCP −0,9 s, LCP −0,5 đến −1,2 s, nhưng TBT +0,6 đến +1,2 s, điểm −13 đến −18 ở 3/4 template | Đã có CSS gọn: xem hàng dưới |
| Critical CSS dựng từ CSS gọn (lớp 5) | CSS gọn chặn render đã chạy, điểm mobile 96–100. Critical dựng ra 85–113 KB mỗi trang | 96 lượt PSI, 6 trang × 2 thiết bị: 5/6 trang "xấu hơn" ở ít nhất 1 thiết bị. TBT +36 đến +178 ms, LCP tới +525 ms | Chưa có ngưỡng cỡ critical đã đo. Chỉ thử lại khi critical nhỏ hơn nhiều so với 85 KB, A/B từng template |
| Face dự phòng `local()` + `size-adjust` cho chữ đậm (lớp 4) | CLS lab 0,05–0,07 do H1 đổi số dòng khi web font về; field CLS = 0 | LCP mô phỏng +225–633 ms ở 5 bài; 1 trang nhãn "xấu hơn" | Field CLS p75 vượt 0,1 |
| Preload font `fetchpriority="low"` (lớp 4) | Trang chủ, trang dịch vụ, bài GEO | Xấu hơn ở cả 3 | Không xét lại ở trang không có CLS do font |
| Như trên, giữ ở 1 bài pillar | CLS lab 0,118 do font | Giữ: CLS 0,118 → 0, điểm 94,5 → 97. Đổi lại: lần vẽ đầu muộn ở 22/22 lượt, LCP +189 ms | Có cách sửa CLS không làm vẽ đầu muộn |
| Đưa script inline ra file ngoài (lớp 6) | KPI có tỉ lệ HTML trong lượt Googlebot | HTML nhẹ 9–11 KB, nhưng bot tải thêm file JS, ngược KPI | KPI không có mục crawl |
| Beacon RUM bằng mu-plugin (lớp 7) | Trang dịch vụ mobile | LCP +225 ms, nhiễu A/A 150 ms | Gắn qua tag GTM nạp sau tương tác |
| Gộp jQuery + thư viện slider thành 1 file (lớp 6) | Mục tiêu bớt request cho Googlebot | Một long task 92–142 ms thay cho các task 29–30 ms. TBT trang chủ trung vị 11 → 31 ms. Đã trả lại | Có cách tách khởi tạo slider ra ngoài khung đo |
| `content-visibility:auto` từ section thứ 3 (lớp 5) | Trang dịch vụ, trừ footer có phần tử `position:fixed` | Trace local CPU 4x giảm, PSI không xác nhận: TBT desktop 15,25 → 16,5 ms, mobile 0 → 1,75 ms (8 lượt) | `styleLayout` mobile từ 500 ms |
| Nạp font web sau FCP 1 s, kèm face dự phòng hiệu chỉnh trên Chrome Mac (lớp 4) | Font đang preload + `swap`, CLS 0 | LCP −270 đến −750 ms ở 5/5 trang, nhưng CLS trang chủ 0 → 0,285 (điểm 97 → 84), bài pillar 0 → 0,118 (8 lượt). Lab Mac không thấy CLS này | Có face dự phòng khớp máy PSI (`cls-chi-psi-thay.md`) |
| Nạp `@font-face` sau sự kiện `load` (lớp 4) | Như trên, lab staging, 5 trang × 5 lượt | LCP lab giảm gần bằng bản nạp sau FCP, nhưng ở 4G chậm chữ hiện bằng font dự phòng khoảng 8,7 s (bản preload khoảng 0,4 s) | Không xét lại. Dùng mốc sau FCP nếu cần hoãn font |
| `font-display: optional` + gỡ preload font (lớp 4) | Như trên, PSI 5 lượt mỗi nhánh | CLS về 0 ở 5/5 trang, nhưng FCP +550 ms ở 2 trang. LCP giảm từ 200 ms chỉ ở 1/5 trang | Kèm kết quả production 21/10 ở lớp 4 |
| Cắt trục `wght` của font biến thiên còn dải đang dùng nhiều (lớp 4) | Font biến thiên 1 file, lab staging | −12,7 KB, LCP trong nhiễu. Chữ 300 ở 4 khối đổi nét | Font chiếm phần lớn byte trang |
| Preload ảnh nền CSS là phần tử LCP (lớp 2) | LCP chờ lần vẽ đầu (FCP 2,4 s), không chờ ảnh | Ảnh về sớm 0,4 s, LCP 3.004 → 2.988 ms (ngưỡng 150 ms) | FCP đã giảm, LCP chờ ảnh |
| Tắt gộp CSS (`guest_optm=0` + `optm-css_comb=0`) (lớp 5) | Staging | LCP +364 và +856 ms. `guest_optm=1` vẫn ép gộp CSS cho khách chưa có cookie, gồm bot | Không xét lại khi còn Guest Mode |
| Hoãn khởi tạo slider tới khi slider vào khung nhìn (lớp 6) | TBT các template có slider đã dưới 200 ms | TBT trang chủ mobile 36,8 → 25,0 ms, desktop trong vùng nhiễu. Link neo quá form 1.372–2.439 px, CLS 0,057–0,395 khi nhảy tới slider. Đã trả lại | Có CSS in trong HTML giữ đúng chiều cao slider ở mọi mốc màn hình, và slider khác của theme không làm trang co |
