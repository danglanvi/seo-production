# Nhánh A: proxy Cloudflare toàn site (khách ngoài VN hoặc toàn cầu)

Nạp ở bước 2–4 khi chọn nhánh A. Các bước dưới dựng từ cấu hình T1 đã chạy và kiểm trên một site VN qua tên thử (26/10/2026). Cache Rule HTML đã có một ca thật trên site TMĐT mẫu khách quốc tế (30/10/2026, bước 2).

## 1. Điều kiện

- Khách chính ngoài VN, hoặc origin ở Mỹ hay châu Âu.
- SSL Full (strict), TLS tối thiểu 1.2.
- Origin giữ kết nối ≥ 60 giây (keep-alive), để edge tái dùng kết nối.

## 2. Cấu hình (API hoặc dashboard)

1. Backup ruleset `http_request_cache_settings`, `bot_management`, tiered cache vào `backup/v1/`. Ghi một lệnh trả lại cho mỗi mục.
2. Cache Rule HTML theo host, chỉ GET/HEAD, query rỗng. Không áp cho `/wp-admin`, `/wp-json`, `*.php`. Không áp khi có cookie `wordpress_logged_in_`, `wordpress_sec_`, `_lscache_vary`, `wp-postpass_`, `comment_author_`, `wp-settings-`, `wfwaf-authcookie`, `wordfence_verifiedHuman`. Edge TTL theo origin.
   - API từ chối `edge_ttl.default` khi mode là `respect_origin`.
   - Cách làm tách rule (ca thật site TMĐT mẫu 30/10/2026): rule "Cache full HTML" cho mọi request, Eligible for cache, Edge TTL ghi đè header origin; sau đó các rule Bypass cho admin, đăng nhập, giỏ hàng, thanh toán và cookie thử thách `cf_clearance`, `__cf_bm`. Cloudflare chạy mọi rule khớp theo thứ tự, rule sau ghi đè rule trước. Đặt rule Bypass dưới rule cache. `__cf_bm` có ở nhiều khách thật khi bật Bot Management, nên kiểm tỉ lệ HIT sau khi bật.
   - Header origin của ca thật: `Cache-Control: public, max-age=0, s-maxage=604800, stale-while-revalidate=86400`. Edge giữ 7 ngày, trình duyệt luôn hỏi lại, nên nội dung mới lên ngay sau purge.
3. Rule riêng `cache_by_device_type` nếu theme in HTML khác cho mobile và desktop.
4. Ảnh png/jpg: Cloudflare mặc định cache theo đuôi file, kể cả khi không có Cache Rule. Nếu origin đổi ảnh theo header `Accept` (WebP Express), thêm rule `cache: false` cho png/jpg, hoặc sửa để origin trả URL webp riêng.
5. Smart Tiered Cache: bật (miễn phí). Argo (Smart Shield + Argo): từ 5 USD + theo GB, chỉ bật khi đo thấy trạm trượt cache nhiều.
6. Bot Fight Mode và JS detections chèn script vào HTML. Tắt nếu cần HTML giống origin. Ghi rõ đây là đổi bảo mật cho mọi tên đang proxy.
7. APO cho WordPress mặc định xung đột với LiteSpeed Cache. Site TMĐT mẫu (30/10/2026) chạy được APO cùng LiteSpeed Cache sau khi tắt Guest Mode và Guest Optimization của LiteSpeed. Nếu cần bật cả hai, tắt 2 tính năng đó trước, rồi kiểm theo mục 3.
8. Bật proxy (đám mây cam) cho apex và www trong giờ thấp điểm. Trả lại: tắt proxy.

## 3. Kiểm

- So HTML qua edge với đi thẳng origin (md5 sau khi bỏ nonce và comment cache) trên ≥ 12 URL.
- Request có cookie giả phải BYPASS.
- Trang tĩnh trả `cf-cache-status: HIT`. Trang giỏ hàng trả `DYNAMIC` hoặc `BYPASS`.
- Không có trang thử thách hay `challenge-platform` trong HTML.
- 404 và 410 BYPASS nếu origin cấm cache.
- TTFB theo vùng bằng `scripts/geo_verify.py`.
- Googlebot UA không nhận trang thử thách.
