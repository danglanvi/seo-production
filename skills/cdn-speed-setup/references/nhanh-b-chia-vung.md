# Nhánh B: chia vùng cho site VN (O7b: Bunny DNS + CNAME flattening, DNS vẫn ở Cloudflare)

Nạp ở bước 3–4 khi Lead chọn O7b. Đã chạy thật trên một site VN (WordPress, OpenLiteSpeed, VPS ở VN) ngày 26/10/2026. O4 (Load Balancing) chưa chạy thật. Phần O4 ở §6 chỉ là hướng dẫn từ tài liệu.

## 1. Sơ đồ

- Apex `example.com` (Cloudflare, DNS-only) là CNAME tới `geo.<tên ủy quyền>`. Cloudflare làm phẳng CNAME ở apex.
- `<tên ủy quyền>` có NS trỏ sang Bunny DNS (`kiki.bunny.net`, `coco.bunny.net`). Tên ủy quyền có thể nằm trong chính zone của site, ví dụ `cdn-geo.example.com`.
- Zone Bunny DNS có bản ghi script `geo` dùng `templates/geo-dns-script.js`. Bản ghi `whoami` (TXT) dùng cùng script để chẩn đoán.
- Script trả:
  - Châu Á: A về IP origin.
  - Vùng khác: `PullZoneRecord` của pull zone. Pull zone bật Origin Shield ở Mỹ.
- `www` là A về IP origin (DNS-only). Nếu `www` đang là CNAME về apex, đổi trước bằng `cdn_dns_switch.py pin-a`. Nếu không đổi, `www` đi theo CDN và redirect www → apex chạy qua Mỹ.

## 2. Dựng pull zone (chưa chạm apex)

1. Tạo pull zone:
   - Origin `https://<IP origin>`, Host header là domain.
   - Không dùng origin `https://<domain>`. Sau khi đổi apex, domain trỏ lại CDN và tạo vòng lặp.
   - Tắt TLS 1.0 và 1.1.
2. Thêm hostname domain:
   - Chép chứng chỉ của origin lên Bunny (`/addCertificate`, cert và key dạng base64).
   - Bật Force SSL.
   - Ghi ngày hết hạn chứng chỉ vào HANDOFF. Đồng bộ lại trước khi chứng chỉ origin gia hạn.
3. Bật `UseStaleWhileOffline`, `UseStaleWhileUpdating`, `OriginRetries` 1. Bật Origin Shield ở trạm gần Googlebot (Mỹ, ví dụ Chicago "IL").
4. Edge rule (Bunny giới hạn 5 pattern mỗi trigger; cần nhiều hơn thì tách trigger):
   - Bypass: `/wp-admin`, `/wp-json`, `*.php`.
   - Bypass khi có cookie WordPress (`wordpress_logged_in_`, `wordpress_sec_`, `wp-postpass_`, `comment_author_`, `woocommerce_`).
   - Bypass URL có query, **trừ file tĩnh**. Cách làm: TriggerMatchingType 1 (all), thêm 2 trigger URL MatchNone cho css/js/woff/ttf/svg và png/jpg/jpeg/webp/gif. Nếu thiếu 2 trigger này, CSS/JS `?ver=` BYPASS (site VN: 80,8% lượt).
   - HTML không có Cache-Control: lưu edge 1 ngày (OverrideCacheTime 86400).
   - robots.txt, `/feed/`: 1 giờ.
   - Sitemap `*.xml`: 1 ngày, chỉ mã 200. Purge sitemap khi đăng hoặc sửa bài (`origin-sau-cdn.md` §3).
   - Ảnh uploads: 30 ngày, chỉ mã 200, 206, 304 (§2b).
   - Edge rule không đặt được header `Accept` hay `Accept-Encoding` gửi lên origin. Bunny trả 400 "Header name is reserved".
   - Chặn `xmlrpc.php`, `wp-login.php` (BlockRequest). Ghi chú: admin ở nước ngoài phải dùng VPN VN để đăng nhập.
   - `X-Robots-Tag: noindex` cho hostname `*.b-cdn.net`, để tên thử không bị index.
5. Cache trình duyệt:
   - Khi origin không gửi Cache-Control (thường là HTML), Bunny đặt max-age bằng thời gian lưu edge. Đặt `CacheControlPublicMaxAgeOverride` của zone (ví dụ 600 giây).
   - Thiết lập zone này đè lên mọi file, kể cả CSS/JS tên md5 mà origin gửi max-age 1 năm. Thêm edge rule loại 16 (Override Browser Cache Time), giá trị `-1`, điều kiện Request URL theo đuôi file tĩnh: `*.css`, `*.js`, font, ảnh, `*.svg`, `*.ico`. Giá trị -1 trả đúng Cache-Control của origin. Edge rule thắng thiết lập zone.
   - Điều kiện Request URL không xét query string: `*.css` khớp `x.css?ver=1`, còn `*ver=*` không khớp. Lọc theo query thì dùng điều kiện loại 6 (Query String).
   - Bunny gắn header trình duyệt lúc trả, nên bản đang lưu ở edge nhận header mới ngay, không cần purge.
   - Kiểm: so Cache-Control ở origin và qua edge cho HTML, CSS/JS md5, ảnh uploads, JS theme. Site VN: file tĩnh nhận 600 giây trong khoảng 21:21–23:38 ngày 26/10/2026, trước khi có rule này.
   - Bản v1.0 ghi edge rule 16 không đổi được cache trình duyệt của HTML. Ghi chú đó sai: lượt thử 26/10/2026 23:36 cho thấy rule 16 đổi được cả HTML.
6. Kiểm trên `*.b-cdn.net` theo `do-va-kiem.md` §2: SEO trùng, cookie bypass, TTFB lượt đầu và lượt lặp.

## 2b. Edge rule theo mã: 301, 404, 410, 5xx

Đã chạy trên production của site agency mẫu ngày 27/10/2026, kiểm độc lập đạt.

- Bunny chỉ lưu 301 và 410 khi pull zone bật `CacheErrorResponses`. Khi tắt, edge rule đặt thời gian cache cho 301 và 410 không có tác dụng. 404 vẫn theo edge rule.
- Khi bật `CacheErrorResponses`:
  - 301 và 410 nằm ở edge khoảng 5 giây. Sau đó Bunny trả bản cũ (`STALE`) và lấy bản mới ở nền. Edge rule không đổi được mức 5 giây.
  - 404 nhận thời gian của edge rule.
  - Header trình duyệt của 404 và 410 thành `public, max-age=5`.
  - Mã lỗi không có rule chặn được lưu ngay, kể cả 5xx (đã thử mã 507).
- Đặt điều kiện mã (trigger StatusCode) cho mọi rule thời gian cache. Rule chỉ theo URL giữ cả 404 và 5xx. Ví dụ: rule ảnh 30 ngày chỉ áp cho 200, 206, 304.
- Thêm một rule chặn: mọi mã ngoài danh sách được lưu (200, 203, 204, 206, 301, 304, 404, 410) nhận thời gian cache 0. Dùng danh sách mã được lưu, không dùng danh sách mã cấm.
- Rule giữ 301, 404, 410 ở edge 1 ngày: trừ URL có query, `*.php`, `/wp-admin`, `/wp-json`, `/wp-content/` và cookie đăng nhập. 404 trong `/wp-content/uploads/` (không query) dùng rule riêng.
- Không bật `FollowRedirects`. Thiết lập này trả nội dung trang đích tại URL cũ, nên tạo trang trùng.
- Bài mới hoặc ảnh mới ở URL đang 404 phải được purge. Mu-plugin đưa URL vào hàng đợi purge (`origin-sau-cdn.md` §3).
- Kiểm:
  - Lượt 2 của URL mẫu 301, 410, 404 qua trạm Mỹ trả `cdn-cache: HIT`. Mã và Location đúng.
  - Origin thử trả 5xx: mọi lượt qua edge là MISS.
  - Sau khi sửa rule, lập danh sách URL đã lưu sai bằng log CDN. Purge URL nào có thể quay lại 200.

## 3. Dựng DNS chia vùng (chưa chạm apex)

1. Tạo zone Bunny DNS cho tên ủy quyền. Thêm NS ở Cloudflare (2 bản ghi NS, DNS-only).
2. Tạo script DNS trong Bunny, gắn vào bản ghi `geo` và `whoami`.
3. Gửi code bằng `scripts/bunny_geo_script.py`. Chạy thử trước, sau đó dùng `--backup` và `--apply`.
4. Kiểm bằng `dig geo.<tên ủy quyền> @kiki.bunny.net` với ECS châu Á và ECS Mỹ. Kiểm `whoami` để xem script thấy quốc gia và trạm nào.
5. Mã vùng trong script:
   - `ASIA` là mã quốc gia.
   - `ASIA_SZ` là mã trạm Bunny DNS nhận câu hỏi (`serverZone` = RegionCode của API `/region`).
   - Lấy mã trạm từ API `/region`, không đoán.
   - Chạy `python3 -B scripts/tests/test_cdn.py` sau mỗi lần sửa danh sách. Test bắt va chạm mã: trạm Los Angeles có mã "LA", trùng mã quốc gia Lào.

## 4. Đổi apex (Lead duyệt riêng, giờ thấp điểm)

1. `cdn_dns_switch.py backup` cho apex và www. Lưu IP origin vào file `~/.cm/<site>.origin` chmod 600.
2. Nếu www là CNAME về apex: `cdn_dns_switch.py pin-a --name www.<domain>`. Chạy thử trước, sau đó `--apply`.
3. `cdn_dns_switch.py switch --target geo.<tên ủy quyền>`. Chạy thử trước, sau đó `--apply`.
   - Script dùng batch API (xoá và tạo trong một lệnh).
   - Không xoá A rồi mới tạo CNAME. Khoảng NODATA bị resolver cache tới 30 phút.
4. Kiểm ngay bằng `geo_verify.py`: VN nhận ORIGIN, Mỹ nhận CDN, HTTP 200.
5. Làm nóng cache ngay bằng `warm.py --images`.
6. Ghi `rollback.md`: lệnh `unswitch --apply`, thời gian trả lại khoảng 60 giây (TTL 60).

## 5. Giới hạn đã đo

- Cloudflare tra địa chỉ thay khách khi làm phẳng CNAME, và không gửi ECS. Script chỉ thấy IP máy tra của Cloudflare.
- Script chỉ xét quốc gia: 4/120 lượt hỏi từ Mac ở VN nhận CDN (3,3%).
- Script xét thêm `serverZone`, với danh sách trạm châu Á đầy đủ:
  - Globalping VN: 40/40 lượt nhận origin, 8 ASN.
  - Trước khi đủ danh sách: 165/168 lượt nhận origin. Cả 3 lượt sai ở AS7602, qua 8.8.8.8 và resolver của probe.
- Bunny DNS trả lời cho cả khách VN. Nếu tài khoản Bunny bị khoá (hết tiền), domain mất phân giải với mọi khách. Nạp tiền trước khi đổi apex, và đặt giám sát.

## 6. O4: Load Balancing Cloudflare (chưa chạy thật)

- Cloudflare Load Balancing gói Basic cộng Traffic Steering (khoảng 15 USD/tháng), chế độ DNS-only (đám mây xám).
- Pool 1: origin (IP VPS). Pool 2: CDN (CNAME pull zone).
- Geo steering: VN và các nước châu Á vào pool 1, vùng khác vào pool 2.
- LB xét IP resolver hoặc ECS của khách, nên tránh được giới hạn §5.
- Health check bật cho cả 2 pool. Fallback pool là origin.
