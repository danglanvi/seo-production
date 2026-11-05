# Origin sau khi có CDN: IP thật, làm nóng, purge, chứng chỉ, giám sát, tiền

Nạp ở bước 5 của SKILL.md. Mục "chưa thử" là việc chưa chạy thật trên site nào (26/10/2026).

## 1. IP thật của khách ở origin

- Sau khi đổi apex, mọi request ngoài châu Á đến origin từ IP trạm CDN. Wordfence, giới hạn tần suất và log origin thấy IP CDN nếu origin không tin header `X-Forwarded-For`.
- Lấy danh sách IP trạm từ nhà CDN:
  - Bunny: `https://bunnycdn.com/api/system/edgeserverlist` (IPv4) và `/ipv6`.
  - Cloudflare: `https://www.cloudflare.com/ips-v4`.
- Chỉ khai IP trạm thật sự gọi về origin. Lấy danh sách này từ log origin của 1–3 ngày sau khi đổi apex. Origin Shield làm số IP này nhỏ (site VN: 18 IP).
- Khai đúng từng IP. Không gộp thành /24: máy khác trong cùng dải sẽ giả được IP khách.
- OpenLiteSpeed:
  - `useIpInProxyHeader 2`, danh sách tin cậy dạng `a.b.c.dT`.
  - OLS 1.8.1 không nhận `/32T`.
  - OLS tự thêm dải Cloudflare và QUIC.cloud.
  - Sửa cấu hình OLS cần restart. Restart chỉ khi phiên giữ server đồng ý và Lead duyệt giờ.
- Kiểm:
  - `REMOTE_ADDR` trong PHP là IP khách thật khi đi qua CDN.
  - Header XFF giả gửi thẳng từ IP không tin bị bỏ qua.
- Làm mới danh sách hằng tháng.
- Wordfence: `wfConfig::set` qua `wp eval-file` không lưu được (site VN, 26/10/2026). Nếu web server đã đặt `REMOTE_ADDR` đúng, để Wordfence đọc `REMOTE_ADDR`.

## 2. Làm nóng cache

- Chạy `scripts/warm.py --images` ngay sau khi đổi apex. Nhịp tối đa 1 request/giây.
- HTML lưu edge 1 ngày, nên cron làm nóng phải chạy hằng ngày (chưa thử).
- Ảnh thường chiếm phần lớn lượt Googlebot. Site VN: ảnh 57%, trúng cache 1,6–1,8% khi chưa làm nóng ảnh.
- Làm nóng theo image sitemap hoặc theo ảnh trong HTML.
- Làm nóng mọi ảnh mỗi ngày, kể cả khi TTL là 30 ngày. Bunny xoá bản lưu của ảnh ít dùng sau 1–4 ngày. Site VN 01/11/2026: ảnh Googlebot MISS 106/334 lượt, 92 lượt là ảnh trong HTML làm nóng 25 ngày/lần. Ảnh làm nóng trong ngày: MISS 6/195.
- Nếu origin đổi ảnh theo header `Accept` (WebP Express): làm nóng 2 biến thể Accept, hoặc sửa để origin trả URL webp riêng.
- Nếu origin đổi HTML theo `Accept` (LiteSpeed WebP replacement): Bunny không tách cache HTML theo WebP. Vary WebP chỉ áp cho jpg, jpeg, webp, png, gif. Lượt đầu tiên sau purge quyết định bản HTML lưu ở shield. Làm nóng ngay sau purge bằng Accept có `image/webp`, cả UA desktop và mobile. Edge rule không đặt được header Accept: Bunny báo tên header dành riêng. Sửa gốc ở origin (site VN, 27/10/2026).
  - `scripts/warm.py` từ v1.2 gửi HTML với Accept như Chrome, có `image/webp` (`--accept`). Bản trước dùng Accept mặc định của curl (`*/*`), nên lượt làm nóng đầu có thể lưu bản không WebP.
- Làm nóng đúng biến thể cache. Bunny tách biến thể theo loại file (site agency mẫu, 27/10/2026):
  - Ảnh: tách theo Accept có `image/webp`, không tách theo mobile/desktop.
  - CSS và `*.xml`: tách theo mobile/desktop, không tách theo WebP.
  - UA `Googlebot/2.1` (compatible, không có chữ Mobile) rơi vào bản desktop. Googlebot tải sitemap bằng UA này.
  - Vì vậy: làm nóng sitemap bằng UA desktop. Lấy danh sách CSS từ HTML ở edge (bản bot nhận), làm nóng cả 2 bản. Ảnh Googlebot/2.1 đã tải thì làm nóng thêm bản WebP.
- Làm nóng đúng trạm bot dùng. Đọc cột trạm (edge) trong log CDN của Googlebot. Site VN 26–27/10/2026: 85/85 lượt Googlebot web vào cùng một trạm ở Mỹ.
  - Tìm IP trạm: `dig +short @8.8.8.8 <zone>.b-cdn.net A +subnet=<dải ECS ở vùng của trạm>`. Gửi request bằng `curl --resolve <domain>:443:<IP trạm>`.
  - `warm.py --ecs <dải>` làm việc này. Sau purge theo URL, dùng `wp-ucss/scripts/bunny_purge.py --warm` với `cdn_warm_ecs` trong site.json.
  - Dải ECS là dải IP công khai ở vùng đó, không phải IP khách. Không ghi IP trạm vào báo cáo.

## 3. Purge khi sửa bài

- Không có purge: khách ngoài vùng origin thấy bản cũ tới hết thời gian lưu edge.
- Cách đã chạy trên site agency mẫu (27/10/2026): mu-plugin đưa URL vào hàng đợi khi lưu bài, đổi trạng thái hay xoá bài; cron đọc hàng đợi, gọi API purge rồi làm nóng.
  - URL bài, trang chủ, trang blog, chuyên mục, thẻ, tác giả.
  - Sitemap index, sitemap của loại bài, sitemap của taxonomy.
  - Ảnh mới (hook `add_attachment` và filter `wp_generate_attachment_metadata`): file gốc, mọi cỡ, bản `.webp`. Một ảnh 7 cỡ cho 12 URL.
- Thử trên staging trước khi đưa lên production. Uploads của staging chỉ đọc thì gọi hook trên ảnh có sẵn.
- Sau purge, chờ 30 giây rồi mới làm nóng. Purge tới trạm Mỹ chậm 10–20 giây dù gọi `async=false`, nên lượt làm nóng sớm hơn bị purge muộn xoá (đo 2 lần, 27/10/2026).
- Không purge toàn site, trừ khi Lead duyệt.
- Bunny purge theo URL (đo 27/10/2026, zone bật vary mobile):
  - Gọi `POST /purge?url=<URL>&async=false`, không thêm `exactPath=true`. `exactPath=true` chỉ xoá bản desktop, bản mobile còn lại.
  - URL kết thúc bằng "/": Bunny thêm ký tự đại diện, nên trang con dưới path đó có thể cũng bị xoá. Purge "/" không xoá cả zone.
  - Sau purge, kiểm header `cdn-cachedat` bằng UA desktop và UA mobile. Header ghi giờ UTC, dạng `10/26/2026 17:15:55`. Giờ lưu phải sau giờ purge.
  - Script purge rồi làm nóng ngay bằng Accept WebP, 2 UA, có kiểm `cdn-cachedat`: `wp-ucss/scripts/bunny_purge.py --warm` (đọc `cdn_host`, `cdn_warm_ecs` trong site.json). Script này làm nóng 1 giây sau purge, sớm hơn mức chờ 30 giây ở trên. Sau 30 giây, kiểm lại `cdn-cachedat` ở 2 UA; nếu MISS thì chạy lại `warm.py` cho các URL đó. Một lần purge "/" ngày 26/10/2026 không xoá bản mobile ở một máy edge, nhưng chưa rõ nguyên nhân.

## 4. Chứng chỉ

- Nhánh B dùng chứng chỉ chép từ origin. Ghi ngày hết hạn vào HANDOFF.
- Đồng bộ lại trước khi chứng chỉ origin gia hạn. Let's Encrypt gia hạn khoảng 30 ngày trước hạn.
- Cách khác (chưa thử): để nhà CDN cấp chứng chỉ riêng. Cách này cần xác minh tên qua HTTP, và có thể vướng khi apex chia vùng.

## 5. Giám sát

Dùng `scripts/cdn_monitor.py`, cấu hình theo `templates/cdn-monitor.example.json`. Chạy thật từ 26/10/2026 trên một máy Mac luôn bật, bằng launchd.

- Mỗi 5 phút (3 request tới production, cách nhau ít nhất 1,1 giây):
  - DNS của domain qua resolver hệ thống, 1.1.1.1 và 8.8.8.8, từ máy giám sát ở VN. Nghiêm trọng khi cả 3 không có câu trả lời. Cảnh báo khi một resolver không trả lời, hoặc khi có resolver trả IP CDN.
  - NS Cloudflare của zone trả IP cho apex. Lỗi ở đây là lỗi làm phẳng CNAME.
  - Hai NS của nhà CDN trả lời tên chia vùng. Script tra IP của NS qua 1.1.1.1, không qua router.
  - HTTP 200 khi gọi thẳng origin.
  - Qua trạm CDN ở Mỹ (IP trạm tra qua 8.8.8.8 với ECS dải Mỹ): trang chủ trả 200, và URL có query (`?cdn-monitor=1`, đi xuyên tới origin vì rule bypass query) trả 200. Header `server` phải là của nhà CDN.
  - Nếu máy giám sát không nhận phản hồi (mã 0), script gọi lại trang qua HTTP từ 3 probe Globalping ở Mỹ. Script chỉ tính lỗi khi đa số probe cũng lỗi. Đường quốc tế từ máy ở VN tới trạm Mỹ rớt vào giờ cao điểm. Site VN 28/10–02/11/2026: 20 vòng mã 0, log Bunny không có request của giám sát, cùng lúc Googlebot vẫn nhận 200. Thiếu quota Globalping thì giữ kết quả lỗi. Trạm trả mã lỗi thật (ví dụ 503) thì script báo ngay, không đo lại.
- Mỗi giờ:
  - Globalping: 5 probe ở Mỹ không được nhận IP origin; 6 probe ở VN không được nhận IP CDN. Bỏ lượt khi quota thấp, thử lại sau 15 phút.
  - Tài khoản CDN: bị khoá là nghiêm trọng. API lỗi là cảnh báo, không kèm lệnh trả DNS. Tiền sắp cạn chỉ báo ban ngày, nhắc lại sau 24 giờ.
- Mỗi ngày, lúc 8 giờ:
  - Số ngày còn lại của chứng chỉ trên CDN.
  - Tin "giám sát vẫn chạy": số vòng hôm qua so với dự kiến (288), số vòng mất mạng, số phút gián đoạn, mục lỗi. Thiếu quá 20% vòng thì tin đổi thành cảnh báo. Sáng nào không có tin này, giám sát đã dừng.
- Kiểm mỗi vòng báo khi lỗi 2 vòng liền, hoặc 3 trong 6 vòng gần nhất (bắt lỗi chập chờn). Hồi phục sau 2 vòng đạt liền. Kiểm theo lịch báo ngay lần lỗi đầu. Nhắc lại sau 2 giờ nếu vẫn lỗi.
- Gửi tin lỗi thì vòng sau gửi lại. Một kiểm lỗi nội bộ không làm mất cảnh báo của kiểm khác.
- Máy giám sát ngủ hoặc tắt quá 15 phút: khi chạy lại, script gửi tin "gián đoạn N phút". Mạng máy giám sát mất từ 3 vòng: khi có lại, script gửi tin "mất mạng N phút".
- Lệnh trả DNS chỉ kèm theo lỗi phía DNS hoặc CDN. Khi chỉ origin lỗi, tin ghi "kiểm VPS trước, chưa nên trả DNS", vì CDN còn bản lưu.
- Mặc định chỉ báo. Chỉ cho tự trả DNS khi Lead chọn rõ, vì trả DNS là sửa config sống.
- Máy giám sát phải thức 24/7 và tự đăng nhập sau mất điện. LaunchAgent chỉ chạy khi user đã đăng nhập. FileVault chặn tự đăng nhập. Kiểm `pmset -g` và `fdesetup status` trước khi chọn máy. Máy đặt ngủ khi rảnh: thêm LaunchAgent chạy `/usr/bin/caffeinate -s` (RunAtLoad, KeepAlive), không cần sudo, gỡ bằng `launchctl bootout`. Kiểm bằng `pmset -g assertions` thấy `PreventSystemSleep 1`.
- Cài: `python3 scripts/cdn_monitor.py install --config <site>.json`, chạy thử trước, rồi thêm `--apply`. Gỡ: `uninstall --apply`. Xem trạng thái: `status`.

## 6. Tiền và tài khoản

- Nạp tiền trước khi đổi apex. Ở nhánh B, nhà CDN trả lời DNS cho mọi khách. Tài khoản bị khoá thì domain mất phân giải.
- Đổi API key sau đợt dựng nếu key đã dán vào chat hoặc file.
- Xoá, thêm thành viên, token và 2FA trong tài khoản nhà CDN: Lead tự làm.

## 7. Bảo mật

- Nhánh B: apex DNS-only, không có WAF và bot rule của Cloudflare. Trước khi đổi cũng vậy.
- Đường qua CDN: chặn `xmlrpc.php`, `wp-login.php` ở edge.
- WAF của nhà CDN (Bunny Shield): Lead quyết, có phí.
- Origin vẫn giữ Wordfence hoặc tường lửa của server.

## 8. Nén Brotli

- Bunny tự nén gzip, Brotli hoặc Zstandard theo `Accept-Encoding` của client. Pull zone không có công tắc Brotli.
- Không bật Brotli ở origin OpenLiteSpeed cho HTML động: OLS chỉ nén gzip loại này (`wp-host-optimize/references/danh-muc-viec.md`).
- Kiểm: gọi 10 URL HTML qua trạm CDN với `Accept-Encoding: br` và với `gzip`. Header `content-encoding: br` phải có ở mọi URL. So byte hai bản.
