# Nhánh TTFB và cache phía trang

Đọc file này khi CrUX TTFB p75 trên 0,8 s, khi average response time trong GSC Crawl stats trên 300 ms, hoặc khi lượt đầu của khách thật thường miss cache. Nhánh này chỉ đọc: mọi bước đo không đổi option, plugin hay file trên site. Sửa thì theo `checklist-theo-lop.md` lớp 1 và cần duyệt.

Site agency mẫu 21/10/2026 làm nhánh này trong khoảng 6 giờ. Thứ tự dưới đây làm trong khoảng 60 phút.

## 1. Kiểm nguồn field

- Gọi CrUX History API một lần trước. Nếu API trả 403, dùng `loadingExperience` và `originLoadingExperience` trong JSON PSI, rồi ghi giới hạn vào báo cáo.
- CrUX cập nhật theo cửa sổ 28 ngày. Không dùng CrUX để nghiệm thu thay đổi vừa làm.

## 2. Tỉ lệ hit theo thiết bị

1. Lấy 40 URL nhiều khách nhất từ GSC hoặc GA4. Ghi mỗi dòng một path vào `top40.txt`.
2. Chạy `lam_nong.sh` một lượt. Lượt này vừa đo trạng thái cache hiện tại, vừa làm nóng:

   ```bash
   bash "$WPS/scripts/lam_nong.sh" --host https://example.com -f <ev>/top40.txt -o <ev>/hit-truoc.tsv
   ```

3. Đọc dòng tóm tắt của từng bản cache: `đã hit sẵn <n> (<x>%)`. Bản `guest-m` (khách mới, mobile) thấp hơn hẳn `guest-d` nghĩa là làm nóng thiếu bản mobile.
4. Site agency mẫu 21/10: lượt đầu bản mobile hit 5%, bản desktop 95%. Sau khi làm nóng đủ 4 bản và Accept WebP: lượt đầu mobile vào cache ở 39/40 URL.

`lam_nong.sh` chỉ gửi GET, chạy 1 luồng, nghỉ ít nhất 0,5 s giữa các lượt và thử lại lượt lỗi một lần sau 60 s. Mã thoát 2 nghĩa là còn lượt lỗi. Chạy `-n` trước để xem kế hoạch.

## 2b. Nguồn MISS hay gặp

Đọc access log trước khi sửa. Đếm lượt xem HTML theo template và theo tham số query, tách lượt của người, bot và lượt kiểm nội bộ. Rồi kiểm 4 nguồn dưới đây. Mọi việc sửa chạm config sống, nên cần duyệt.

| Nguồn | Cách nhận ra | Cách sửa |
|---|---|---|
| Tham số quảng cáo và tham số Google tạo khoá cache mới: `srsltid`, `gad_source`, `_gl` | Lượt có tham số luôn MISS. Mỗi giá trị khác lại MISS | Thêm tham số vào `cache-drop_qs`. Kiểm robots và canonical bằng `cache_variants.py` sau khi đổi |
| Lưu một sản phẩm, danh mục hoặc thẻ làm purge rộng (mọi sản phẩm hoặc cả site) | Log purge có dòng toàn site sau khi sửa một bài hoặc một term | Purge theo tag của bài hoặc term. Thử bằng một term tạm: tạo, sửa tên, xoá, rồi đọc log purge |
| Làm nóng thiếu template nhiều khách, thường là trang sản phẩm | Danh sách làm nóng không có template đó. Mẫu sitemap của template có tỉ lệ HIT thấp | Cron làm nóng theo sitemap, cả bản mobile và desktop, chạy theo ngưỡng tải của máy |
| Purge hàng loạt chạy chồng lượt làm nóng | Một nhóm URL MISS ở một thiết bị sau đợt purge, thiết bị kia vẫn HIT | Dùng chung một khoá cho purge và lượt làm nóng. Sau purge, làm nóng lại đúng các path đó ở cả 2 thiết bị |

Ca thật ở site bán lẻ mẫu (WooCommerce, shared hosting LiteSpeed), 30/10/2026:

- CrUX TTFB p75 mobile là 1.522 ms. HIT mất 20–35 ms, MISS mất 0,75–1,28 s.
- `srsltid` có trong 24% lượt xem mobile của người, trong 23–30/10.
- Trước 13:41 ngày 30/10, lưu một sản phẩm xoá cache của mọi trang sản phẩm. Danh sách làm nóng có 40 URL và không có trang sản phẩm. Trang sản phẩm chiếm 42% lượt xem mobile.
- Sau khi sửa: URL có tham số trả HIT 22–29 ms. Term tạm có 0 lượt purge toàn site. Lượt làm nóng 23:52 có 1.068/1.068 HIT.
- Purge 537 path chạy chồng lượt làm nóng lúc 21:39. Kết quả: 58 sản phẩm MISS bản desktop tới lượt làm nóng sau. Job quét CSS gọn chỉ làm nóng lại bản mobile.
- Field data chưa đo lại. CrUX cần khoảng 28 ngày, nên mức giảm TTFB p75 chưa xác minh.

## 3. Thời gian dựng trang khi miss

- Đo TTFB của URL có tham số nằm trong `cache-exc_qs` (không vào cache), 5 lượt mỗi URL. Đọc option trước, không thêm tham số mới.
- So với TTFB miss của một site đối chứng cùng server. Site agency mẫu: 0,8–1,3 s khi miss.

## 4. Phần nào làm chậm khi dựng trang

Đo trong tiến trình WP-CLI riêng. Không tắt plugin trên site để đo.

- Plugin: đo thời gian nạp WordPress với và không với `--skip-plugins=<danh sách>`, 5 lần xen kẽ mỗi bên, so trung vị. Lệnh chỉ đổi tiến trình CLI.

  ```bash
  cd /tmp && for i in 1 2 3 4 5; do /usr/bin/time -p <lệnh wp> --path=<root> eval '1;' 2>&1 | grep real; /usr/bin/time -p <lệnh wp> --path=<root> --skip-plugins=<a,b> eval '1;' 2>&1 | grep real; done
  ```

  Site agency mẫu: bỏ một plugin sao lưu bớt 45 ms. Bỏ nhóm plugin cộng sửa plugin đa ngôn ngữ bớt 91 ms.
- Truy vấn SQL: bật `SAVEQUERIES` chỉ trong tiến trình CLI riêng, bằng file nạp qua `--require` định nghĩa hằng. Không sửa `wp-config.php` trên production. Gom `$wpdb->queries` theo hàm gọi. Site agency mẫu: theme chạy 150–428 câu, 51–191 ms mỗi trang.
- Chạy mỗi lúc một tiến trình WP-CLI nặng. VPS ít RAM có thể bị kernel OOM giết tiến trình (`checklist-theo-lop.md` lớp 1).

## 4b. 404 của bot dò quét dựng qua PHP

WordPress dựng trang 404 đầy đủ bằng theme, nên mỗi lượt 404 lạ tốn 0,5–2,8 s PHP. Cache 404 chỉ đỡ khi cùng URL bị gọi lại trong TTL. Bot dò quét gọi mỗi URL vài lần trong nhiều ngày, nên hầu hết lượt đều miss.

1. Lấy đường dẫn ứng viên từ log 7 ngày. Điều kiện: không có query, không đuôi file tĩnh, mọi lượt đều 404, từ 3 lượt và từ 2 IP.
2. Chia nhóm. Chỉ chặn nhóm chắc chắn không phải nội dung:
   - file cấu hình, khoá, bí mật, `.md`, `.php` không tồn tại;
   - route của framework khác (`actuator`, `_next/data`…) và `.well-known` không dùng;
   - route ứng dụng khác (`dashboard`, `admin`, `login`…), khớp cả đoạn path;
   - `<bài>/wp-json/batch/v1`;
   - URL chứa `*`.
3. Không chặn nhóm trông như bài cũ. Nhóm đó cần chọn 301 hay 410 theo `content-inventory-audit`.
4. Viết khối `.htaccess` đặt ngay trước `# BEGIN WordPress`, sau mọi khối bảo mật và khối 301/410 cũ. Mỗi rule có `RewriteCond %{REQUEST_FILENAME} !-f` và `!-d`. Trả `[R=404,L]`.
5. Kiểm trước khi áp:
   - in path của mọi URL công khai (bài, trang, CPT, term, tác giả) bằng WP-CLI, rồi chạy regex của khối trên danh sách đó: phải 0 URL khớp;
   - đếm mã trả về 7 ngày của mọi URL khớp khối, xem mã khác 404 có đến từ file có thật hoặc khối chạy trước không.
6. Áp có backup, restart graceful OpenLiteSpeed (OLS chỉ nạp `.htaccess` khi restart). Kiểm bằng probe dò quét và 60 URL hồi quy.

Site agency mẫu 27/10/2026: 161 đường dẫn, 1.742 lượt mỗi 7 ngày, khoảng 1.369 giây PHP. Sau khối: 1,1–2,8 s còn 13–21 ms. Hồi quy 62/65 URL trả 200, 3 URL giữ mã cũ.

Bot hợp lệ cũng gọi một số file mà site không có. Thêm các path đó vào cùng khối khi log cho thấy mọi lượt đều 404:

- `/ads.txt`, `/.well-known/assetlinks.json` khi site không chạy quảng cáo hay ứng dụng.
- `/page/N/` ở gốc site khi trang chủ không phân trang. Giữ phân trang của chuyên mục và của bản ngôn ngữ khác (kiểm bằng URL có tham số ngôn ngữ).

Site agency mẫu 27/10/2026: các URL này từ 404 sau 1,0–1,2 s còn 404 sau 15–16 ms. Hồi quy 156/156 URL đúng kỳ vọng.

- WordPress 6.8 in `speculationrules` có mẫu `/*`, `/wp-content/*`. Googlebot đọc chuỗi đó như URL và gọi thật, mỗi lượt 404 mất khoảng 1,3 s. Khối trên trả 404 nhanh cho URL chứa `*`, nên không cần tắt prefetch của khách.
- Luồng kiểm nội bộ dùng UA riêng, không dùng UA Googlebot. Log KPI crawl lọc theo IP Google. Site mẫu có 14.177 dòng UA Googlebot đến từ lượt thử nội bộ.

## 4c. Mục tiêu average response time dưới 300 ms

Average response time trong GSC Crawl stats đo lúc Googlebot crawl, chủ yếu từ Mỹ. Page cache ở origin VN chưa đủ để xuống dưới 300 ms, vì mỗi vòng VN–Mỹ mất khoảng 200 ms (`cdn-speed-setup`). Cần cache HTML ở edge.

| Ca | Hạ tầng | Average response time |
|---|---|---|
| Site TMĐT mẫu, 8/2026 → 28/10/2026 | Theme đa năng + WooCommerce, LiteSpeed Cache, Cloudflare Cache Rule "cache full HTML" + rule Bypass đặt dưới | 1.000–1.500 ms → khoảng 250–500 ms (ước lượng từ biểu đồ GSC). Request Googlebot mỗi ngày 1.000–2.500 → 1.500–4.500 |
| Site bán lẻ mẫu, 30/10/2026 | Shared hosting LiteSpeed ở VN, chưa có CDN | 1.360 ms. CrUX TTFB p75 1,46 s |

1. Làm mục 2 và 4b trước. Lượt MISS ở edge vẫn đi về origin, nên origin cần tỉ lệ hit cao và 404 nhanh.
2. Chọn nhánh CDN bằng `cdn-speed-setup`: khách toàn cầu dùng nhánh A (Cloudflare cache HTML, rule Bypass cho admin, đăng nhập, giỏ, thanh toán, cookie thử thách). Khách chủ yếu ở VN dùng nhánh B.
3. Shared hosting: tải máy (`loadavg`) gồm cả site khác trên cùng máy. Đo TTFB miss ở 3 khung giờ khác nhau rồi lấy trung vị. Dừng purge và làm nóng khi tải vượt ngưỡng của site (`luot-lon.md` mục 8). Không chỉnh được OPcache hay MySQL, nên cache ở edge là việc chính.
4. Nghiệm thu bằng GSC Crawl stats 28 ngày sau khi bật. Xuất file (Export) để có số theo ngày. Số đọc từ biểu đồ ghi "ước lượng".

## 5. Ngoài phạm vi skill này

- Cấu hình OPcache, log OOM của kernel, cron làm nóng định kỳ trên VPS là việc cấp server. Shared hosting có crontab của tài khoản thì cron làm nóng thuộc mục 2b, cần duyệt. Ghi số đo và đề xuất vào báo cáo, giao người quản trị server.
- Danh sách tham số bỏ khỏi khoá cache (`cache-drop_qs`) của từng site ghi ở `00-client-context/wp-server.md`.

## 6. Ghi vào báo cáo

| Mục | Ghi |
|---|---|
| Field | TTFB p75 URL và origin, nguồn (CrUX API hay PSI), ngày |
| Hit lượt đầu | Tỉ lệ từng bản cache, trước và sau làm nóng |
| Miss | TTFB miss trung vị, site đối chứng |
| Plugin, SQL | Mức chênh trung vị, số lần đo |
| Đề xuất | Việc, tác động ước tính, rủi ro, rollback, người duyệt |
