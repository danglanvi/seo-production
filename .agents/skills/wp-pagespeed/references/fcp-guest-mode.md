# FCP mobile dồn một mốc và LiteSpeed Guest Mode

Đọc file này khi FCP observed của PSI mobile dồn quanh một mốc ở nhiều template, và site bật LiteSpeed Guest Mode. Kiểm cả bẫy script nạp font ở `checklist-theo-lop.md` lớp 4, vì bẫy đó cho cùng dấu hiệu.

## Dấu hiệu

- FCP observed mobile dừng quanh một mốc ở nhiều lượt và nhiều template. Site agency mẫu 19/10/2026: 2.342–2.460 ms ở trang chủ và trang dịch vụ.
- Trong `network-requests`, file CSS gộp tải xong sớm (0,4–0,7 s), nhưng khung hình đầu vẽ muộn.
- Trang không có critical CSS. File CSS gộp lớn chặn hiển thị trong `<head>` (site agency mẫu: khoảng 1,4 MB).
- Desktop không bị, vì CPU không bị giới hạn.

## Chẩn đoán

1. Ghi trace Chrome ở chế độ mô phỏng mobile (CPU x4, 4G chậm). Bật category `viz`, `cc` và `devtools.timeline` qua CDP `Tracing.start`.
2. Đếm event `ThrottleUndrawnFrames` và số lần Chrome từ chối `BeginFrame`. Đo khoảng `requestAnimationFrame` ngừng chạy.
3. Kết luận cổng FCP khi Chrome hoãn commit khung đầu tới lúc parse xong CSS. Site agency mẫu: `ThrottleUndrawnFrames` 402–2.304 ms, 98 lần từ chối `BeginFrame`, rAF ngừng 1.405–2.406 ms.

Những thứ đã thử và không chữa được cổng này:

- Bật critical CSS hoặc nạp CSS gộp bằng `media="print"`. Hai cách này chuyển cổng sang TBT: parse 1,4 MB CSS sau FCP thành long task, TBT lab 1,8–2,6 s.
- Gỡ video ẩn. Video ẩn có `preload="metadata"` vẫn tải nhiều phản hồi 206 lớn, nhưng gỡ video không đổi điểm. Đặt `preload="none"` để bớt byte, không coi đó là bản sửa FCP.

## Phương án đã chạy (cần duyệt riêng)

- Filter `litespeed_buffer_after` trong mu-plugin hiệu năng của site. Chỉ áp cho UA mobile, chỉ ở template đã chọn, chỉ khi trang chưa có critical CSS.
- Filter chuyển thẻ CSS gộp và các `<style>` sau nó xuống ngay sau `<body>`. Sau khối đó, filter thêm một `<script> </script>` rỗng để parser chờ CSS, nên khách không thấy nội dung chưa có CSS.
- Giữ nguyên trang ở các ca sau:
  - Sau thẻ CSS đầu tiên có script thường (bản HTML ngoài Guest Mode).
  - Regex trả NULL hoặc lỗi.
  - `<head>` có `<noscript` hoặc `<!--`.
- Bỏ qua chữ `<style` nằm trong nội dung `<script>` (ví dụ JSON-LD).

Đánh đổi phải trình chủ site: khi mở trang từ trang khác trên Chrome, khách mới thấy màn trắng từ lúc commit tới khi CSS về. Lab đo 2,1–2,4 s ở CPU x4 và 4G chậm.

Kiểm trước khi giữ:

1. So bố cục 390 px trước và sau bằng `shot.mjs`. Chặn `guest.vary.php` như PSI.
2. Đo PSI 3 lượt cho mọi template đã áp. Rút template nào có CLS tăng. Site agency mẫu 20/10: một trong 3 trang có CLS 0 → 0,035 nên đã rút khỏi danh sách.
3. Ghi lệnh rollback về `v0` trước khi ghi production.

Staging thường không bật Guest Mode, nên không đo được cổng này trên staging. A/B trên production bằng bản HTML tĩnh (`do-dac.md` mục 3).

## Loại trừ JS của Guest Mode

- Guest Mode dùng danh sách loại trừ JS riêng: option `optm-gm_js_exc` (filter `litespeed_optm_gm_js_exc`).
- Danh sách Delay JS thường (`optm-js_defer_exc`) không áp cho Guest Mode. Script nằm sai danh sách vẫn bị trễ ở lượt xem đầu, kể cả loader GTM hoãn.
- Kiểm cấu hình đã xuất (chỉ đọc):

  ```bash
  for k in guest optm-js_defer optm-js_defer_exc optm-gm_js_exc; do printf '%s\t' "$k"; <lệnh wp> option get "litespeed.conf.$k" --format=json; done > <ev>/ls-conf.tsv
  python3 -I "$WPS/scripts/ls_exclusions_check.py" --conf <ev>/ls-conf.tsv --script gtm-delay-loader
  ```

- Dòng cuối `LS_EXCL ok` là đạt. `LS_EXCL fail` kèm tên script còn thiếu ở danh sách đang có hiệu lực.

## Khách mới bị tải lại trang (guest.vary.php)

Cách sửa này đổi hành vi cache của cả site, nên cần người duyệt đồng ý trước khi ghi production.

Dấu hiệu:

- Khách mới nhận bản guest, rồi JS gọi `guest.vary.php`. File này trả `{"reload":"yes"}` kèm cookie `_lscache_vary`, nên trang reload.
- Bản sau reload nặng hơn bản guest mà PSI đo. Site agency mẫu 26/10/2026, một trang dịch vụ mobile: bản sau reload 713 KB và 73 script, bản guest 475 KB và 45 script.
- Kiểm bằng Chrome: đếm số lần tải document của một URL. Kết quả 2 là có lỗi này.

Cách sửa đã chạy trên production (site agency mẫu 26/10/2026):

1. Tạo file tĩnh `wp-content/<tên>-guest-vary.json` chứa `[]`.
2. Thêm khối rewrite vào `.htaccess`, đặt trước `# BEGIN LSCACHE`. Khối đưa `guest.vary.php` sang file tĩnh, trừ UA của cron làm nóng:

   ```apache
   <IfModule mod_rewrite.c>
   RewriteEngine On
   RewriteCond %{HTTP_USER_AGENT} !<UA làm nóng>
   RewriteRule ^wp-content/plugins/litespeed-cache/guest\.vary\.php$ /wp-content/<tên>-guest-vary.json [L]
   </IfModule>
   ```

   - Cron làm nóng cần cookie vary để làm nóng bản sau reload. Nếu thiếu điều kiện UA, cron mất cookie.
   - OpenLiteSpeed chỉ nạp `.htaccess` mới sau restart graceful, kể cả khi đặt `autoLoadHtaccess 1`. Restart theo khoá bảo trì của site.
3. Cài `templates/guest-tap.php` vào `wp-content/mu-plugins/`. Bản guest hoãn JS tới lần tương tác đầu, nên lần chạm đầu vào nút menu mobile bị mất. Mẫu nhớ cú chạm đó và bấm lại khi LiteSpeed phát `DOMContentLiteSpeedLoaded`. Đổi `WPS_GUEST_TAP_SEL` theo nút menu của theme. Test: `scripts/tests/test_guest_tap.py`.
4. Purge các URL cần có script mới, rồi làm nóng. Trang cache cũ chưa có script tới khi hết TTL hoặc tới lần purge sau.

Chạy QA bằng Chrome trên production trước khi áp. Chặn DNS của host đo lường.

- Chạy mỗi URL mẫu ở 2 bản, mobile và desktop: bản guest và bản sau reload. Site mẫu: 4 URL, 16 lượt.
- Tạo bản guest bằng cách chặn `*guest.vary.php*`, nên trang không reload. Cách chặn này giống `--block-vary` của `lh_local.mjs`. Bản sau reload thì không chặn.
- So chức năng: submenu desktop, accordion, gõ form, link `tel:`, lần chạm đầu vào menu mobile.
- Chấm ảnh bằng Jev `ui-visual`. Site mẫu: 48 ảnh, 0,0045 USD. Chỉ cờ xuất hiện ở bản guest mà không xuất hiện ở bản sau reload là lỗi của thay đổi.

Kiểm sau khi áp:

| Kiểm | Đạt |
|---|---|
| `guest.vary.php` với UA trình duyệt | `[]`, không có cookie |
| `guest.vary.php` với UA làm nóng | reload và cookie như trước |
| Số lần tải document mỗi URL | 1 |
| Lần chạm đầu vào menu mobile trên bản guest | menu mở |
| Robots, canonical bản Googlebot smartphone; md5 CSS gộp | không đổi |
| 5xx từ giờ restart | 0 |

Bẫy đã gặp: ngay sau restart, UA làm nóng nhận `[]` ở khoảng 2/27 lượt. Script làm nóng nên thử lấy cookie 3 lần.

Rollback:

1. Xoá khối `.htaccess`, rồi restart graceful.
2. Chuyển `guest-tap.php` ra khỏi `wp-content/mu-plugins/` vào thư mục cách ly.
3. Purge các URL đã chạm.
4. Giữ file tĩnh `wp-content/<tên>-guest-vary.json` (nội dung `[]`, tạo ở bước 1 của cách sửa). Khi không có rule nào trỏ tới, file này vô hại.
