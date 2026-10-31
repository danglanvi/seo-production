# Kiểm hit, dựng container, áp và theo dõi

Đọc ở Bước 1, 3, 5 và 6 của `SKILL.md`. Nguồn: site bán lẻ mẫu (WooCommerce, plugin Google Listings & Ads, shared hosting LiteSpeed), 28–30/10/2026, và site agency mẫu (WordPress, theme riêng), 22/10/2026.

## 1. Kiểm hit thật mà không gửi hit ra ngoài

Dùng cách này cho Bước 1 (hiện trạng), Bước 3 (preview) và Bước 5 (sau áp).

1. Mở Chrome headless qua CDP. Bật `Fetch.enable` với mẫu chặn ở bảng dưới. Trả mọi request khớp mẫu bằng `Fetch.fulfillRequest` mã 204, rồi giải mã tham số hit.
2. Thêm lớp chặn DNS: `--host-resolver-rules="MAP www.google-analytics.com ~NOTFOUND, MAP analytics.google.com ~NOTFOUND, MAP stats.g.doubleclick.net ~NOTFOUND, MAP www.googleadservices.com ~NOTFOUND, MAP www.facebook.com ~NOTFOUND, MAP analytics.tiktok.com ~NOTFOUND"`.
3. Chạy selftest trước mỗi lượt: gửi 10 hit giả bằng `fetch`, `sendBeacon`, POST và `Image` tới các host trên. Lượt chỉ chạy tiếp khi cả 10 hit bị chặn.
4. Kiểm lọt: request khớp mẫu hit mà không đi qua `Fetch` trong 1,5 s là hit lọt. Dừng lượt ngay và ghi URL đã che.
5. Che chuỗi nhạy cảm trước khi ghi file: `gtm_auth`, `gtm_preview`, `gtm_cookies_win`, số hotline, email.

Mẫu chặn (Fetch):

```text
*/g/collect*  */ccm/collect*  */collect?*  *googleadservices.com/*  *google.com/pagead/*  *www.google.com/rmkt/*
*.doubleclick.net/*  *facebook.com/tr*  *analytics.tiktok.com/*  *google.com.vn/pagead/*  *google.com.vn/rmkt/*
*google.com.vn/ccm/*  *google.com/ccm/*  *google.com/ads/*  *google.com.vn/ads/*  *google-analytics.com/*
*analytics.google.com/*  *googlesyndication.com/pagead/*  */measurement/conversion*  */pagead/viewthroughconversion/*
*/pagead/1p-*  *graph.facebook.com/*  *tr.snapchat.com/*  *px.ads.linkedin.com/*
```

- Bắt buộc chặn `www.google.com/g/collect` và `www.google.com/rmkt/collect`. Nguồn lỗi: site bán lẻ mẫu 30/10/2026 05:49–05:59, bộ chặn thiếu hai đường dẫn này nên khoảng 48 `page_view` GA4 và 26 hit remarketing Ads lọt ra Google. Ghi annotation GA4 cho khung giờ lọt.
- Kiểm preview container chưa publish: trả request `gtm.js?id=<container đang chạy>` bằng nội dung `gtm.js` preview của workspace (`gtm_api.py preview-url`). Nội dung đúng phải chứa `QUICK_PREVIEW` và ID container mới. Giữ URL preview trong file 0600 ngoài repo.
- Kiểm biến thể "đã gỡ gtag gắn thẳng": `Fetch.failRequest` đúng URL `gtag/js?id=G-…` (không có `&cx=`). Bản do Google tag trong GTM nạp có `&cx=` nên vẫn chạy.
- Kiểm sau publish: bỏ bước thay `gtm.js` (chế độ LIVE), hit vẫn trả 204 tại máy.
- Không cuộn trang trong lượt đo mốc giờ. Sự kiện `scroll` làm loader nạp GTM sớm.

Bảng ca mẫu cho site bán hàng (sửa theo measurement plan của site):

| # | Ca | Kỳ vọng |
|---|---|---|
| C1 | Trang chủ, danh mục, bài, liên hệ | 1 `page_view` có `page_type` đúng |
| C2 | Trang sản phẩm | 1 `page_view` + 1 `view_item` có item |
| C3 | Bấm `tel:` khi GTM đã nạp | 1 `click_to_call`, `position` đúng |
| C4 | Bấm `tel:` trước khi GTM nạp (loader hoãn) | Loader đẩy lại `gtm.linkClick`, có 1 `click_to_call` |
| C5 | Bấm Zalo | 1 `click_zalo`, `position` đúng |
| C6 | Thêm vào giỏ | 1 `add_to_cart` có item |
| C7 | Checkout có giỏ | 1 `begin_checkout` có item |
| C8 | Đẩy `ga4_purchase` giả có `debug_mode` | 1 `purchase` có `transaction_id`, `value`, `currency` |
| C9 | Phát sự kiện gửi form thành công giả | 1 `generate_lead` có `form_id` |

## 2. Khối dựng container

| Loại | Cấu hình | Lý do |
|---|---|---|
| Google tag | Trigger Initialization – All Pages. Tham số cấu hình `page_type` = biến dataLayer | GA4 nhận `page_type` ở mọi event. Không phải lặp tham số ở từng tag |
| Tag GA4 thương mại | GA4 Event, "Send ecommerce data" nguồn Data Layer. Trigger Custom Event `ga4_<tên>`. Tag gửi tên chuẩn (`view_item`…) | Xem mục 4 |
| Tag lead | Trigger Custom Event `generate_lead`, chỉ đẩy sau khi gửi form thành công | Không dùng `form_start` làm lead |
| Click gọi, Zalo | Trigger Just Links: `tel:` và regex `^https?://(oa\.)?zalo\.me/`, không chờ tag. Biến `position` dạng Regex table trên Click Classes | Loader tái phát `gtm.linkClick` có `gtm.element`, `gtm.elementUrl`, `gtm.elementClasses` |
| Tag tên cũ | Giữ song song 14 ngày rồi tạm dừng | Báo cáo cũ không đứt số liệu |
| Consent mode | Chỉ thêm khi site có CMP hoặc banner | Site mẫu không có banner, 1,03% phiên ở EEA, UK, CH; plugin Ads đã khai `consent default` |
| Enhanced conversions | Không bật khi chưa có chính sách dữ liệu cá nhân được duyệt | Cần đẩy email hoặc số điện thoại đã băm |

Dựng bằng GTM API trong workspace mới. Chạy `quick_preview`, đạt khi `compilerError` = false. Không publish ở bước dựng.

## 3. Plugin Google Listings & Ads (GLA)

Hành vi đọc trong code plugin ở site mẫu 30/10/2026:

- Plugin in `gtag/js?id=AW-…` ở `wp_head` ưu tiên 999999. `view_item` ở `woocommerce_after_single_product`. Conversion `purchase` ở `woocommerce_before_thankyou`.
- Theme không truyền `$order` cho `checkout/thankyou.php` thì hook trang cảm ơn không chạy. Mu-plugin dataLayer phải gọi bù hook này một lần.
- Snippet conversion không xét trạng thái đơn hay cổng thanh toán. Site mẫu: 13 đơn có cờ `_gla_tracked=1` trong 7 ngày, 8 đơn đi qua cổng sandbox. Đơn chờ thanh toán (`on-hold`) cũng thành conversion.
- `value` gồm phí vận chuyển. `item_id` có dạng `gla_<ID>` khớp feed Merchant Center.
- Callback là closure, nên `remove_action` không gỡ được.

Cách sửa đã chạy: thêm callback ưu tiên 1 trên `woocommerce_before_thankyou`. Callback đánh `_gla_tracked=1` cho đơn không đạt luật `purchase` (chưa trả, sandbox, lỗi, huỷ, nháp), kèm một meta riêng để đếm đơn bị chặn. Plugin thấy cờ thì bỏ qua. Thử 9 loại đơn giả trước khi áp. Giới hạn: đơn trả sau qua IPN không thành conversion Ads.

Không thêm tag Ads conversion trong GTM khi plugin còn bắn. Mỗi đơn sẽ đi 2 lần với 2 giá trị khác nhau.

## 4. Tiền tố `ga4_` cho sự kiện thương mại

GTM coi lệnh `gtag('event','view_item',{send_to:…})` của plugin là Custom Event cùng tên. Trigger Custom Event `view_item` bắn 2 lần, GA4 nhận thêm item `gla_<ID>` không có tiền tệ. Nguồn lỗi: site mẫu 30/10/2026, preview lượt 1 đạt 7/9 ca, `view_item` và `add_to_cart` đôi.

- Mu-plugin đẩy `ga4_view_item`, `ga4_view_item_list`, `ga4_add_to_cart`, `ga4_begin_checkout`, `ga4_purchase`. Trigger nghe tên mới, tag gửi tên chuẩn.
- `generate_lead` giữ tên khi không plugin nào phát tên này.
- Đặt mu-plugin đổi tên trước, rồi mới publish container. Publish trước thì trang chưa đổi tên mất sự kiện thương mại.
- Listener `DOMContentLoaded` trong mu-plugin dùng `{once:true}`. Nguồn lỗi: site mẫu 30/10/2026, plugin đánh giá phát lại `DOMContentLoaded` sau ajax, handler gắn 2 lần, `add_to_cart` đẩy đôi.

## 5. Chọn N giây hoãn

- N tính từ sự kiện `load`, hoặc sớm hơn khi khách tương tác. Ghi rõ mốc tính trong trang quyết.
- A/B tĩnh bằng `psi_ab.py` của `wp-pagespeed`: mỗi nhánh 6 lượt PSI mobile, xen kẽ trong cùng khung giờ, ngưỡng ghi trước (site mẫu: +3 điểm trung vị).
- Site mẫu 30/10/2026, trung vị 6 lượt: trang chủ 1 s = 65, 2 s = 70,5; trang sản phẩm 1 s = 76,5, 2 s = 85. Với 1 s, tag tải trước mốc LCP, LCP mô phỏng trang chủ lên 7,4–8,3 s ở 3/6 lượt.
- Site mẫu thử 1,5 s theo yêu cầu người duyệt, 2 đợt × 6 lượt: trang chủ 80 so với 82,5, trang sản phẩm 78,5 so với 89. Người duyệt chọn lại 2 s.
- Phần dữ liệu có thể mất: phiên rời trang trong N giây sau `load` mà không chạm, cuộn hay gõ phím. Phiên có `utm_`, `gclid`, `fbclid` nạp GTM ngay, dùng làm nhóm đối chứng ở Bước 6.

## 6. Thứ tự áp và rollback

1. Lấy khoá mu-plugin, khoá purge và khoá `css_src_lockdir` (đổi snippet làm đổi DOM `<head>`). Ghi file phối hợp nếu có phiên khác chạy trên site.
2. Backup option snippet (`ihaf_insert_header`, `ihaf_insert_body` hoặc option của plugin chèn code), option plugin Ads, danh sách mu-plugin. Ghi sha256 vào `~/Backups/<site>/<ngày>/`.
3. Đặt mu-plugin dataLayer bản đổi tên. Đặt loader. Chạy `php -l` trên server, ghi sha256.
4. `gtm_api.py version`, rồi `gtm_api.py publish`.
5. Đổi snippet sang container mới, giữ dạng inline chuẩn. Gỡ gtag G gắn thẳng.
6. Chạy `wp eval 'gtvd_gtm_verify("GTM-…","G-…");'`. Transient phải có `ok=1`.
7. Purge HTML theo URL, lô tối đa 12, rồi làm nóng. Không Purge All. Trang chưa purge vẫn chạy container cũ với tên sự kiện cũ, không đếm đôi.
8. Kiểm trên site sống theo mục 1 (chế độ LIVE). Đi tới cổng thanh toán, không trả tiền.
9. Ghi annotation GA4: mốc áp, N giây, và khung giờ hit lọt nếu có.
10. Đo PSI cùng lô thay đổi của phiên tốc độ (`wp-pagespeed`, `luot-lon.md`).

Rollback theo thứ tự ngược: khôi phục option từ backup, chép lại mu-plugin cũ, chép lại loader cũ, publish lại version cũ của container, purge theo lô. Đổi tên loader thành `.off` chỉ khi lỗi nằm ở loader.

## 7. Theo dõi 7 ngày

| Ngày | Việc |
|---|---|
| +1 | Mục 1–3 |
| +3 | Mục 1–4 |
| +7 | Mục 1–6, viết kết luận, báo người duyệt |
| +14 | Tạm dừng tag tên cũ, publish |

1. Mỗi sự kiện thương mại và lead có số > 0 theo ngày (GA4 Data API). Một sự kiện bằng 0 hai ngày liền thì chạy lại kiểm hit ở chế độ LIVE.
2. `purchase` khớp đơn thật theo `transaction_id`. Chỉ đếm số, không in mã đơn hay thông tin khách.
3. Conversion Ads chỉ có đơn đạt luật: đếm đơn có meta chặn và đơn được gửi.
4. Mất dữ liệu do hoãn: so `sessions` và `page_view` theo kênh 7 ngày trước và sau. Organic hoặc Direct giảm hơn 10% mà Search Console không giảm click tương ứng thì báo người duyệt kèm số.
5. Không đếm đôi: tỉ lệ `page_view` / `session_start` không tăng. `add_to_cart` không vượt số lượt thêm giỏ của WooCommerce.
6. PSI bộ URL đại diện một lần, so với bảng sau áp.

## 8. Bẫy đã gặp

- Loader v1.1 chỉ hoãn thẻ AW khi option còn gtag G. Sau khi gỡ gtag G khỏi option, AW tải thẳng. Nguồn lỗi: site mẫu 30/10/2026 09:02. Mẫu hiện tại hoãn AW khi `drop` đúng hoặc option không còn gtag G (harness ca `nog`).
- Giữ gtag G gắn thẳng thì không hoãn được AW: `gtag.js` của G tự nạp `gtag/js?id=AW` khi thấy lệnh config AW (đo ở site mẫu: AW tải lúc 348 ms).
- Thư viện AW nạp 2 lần: loader nạp thẻ AW của plugin cùng lúc với GTM. Google tag trong GTM xử lý lệnh `config AW` trong dataLayer chung trước khi bản của plugin kịp đăng ký, nên tự nạp thêm `gtag/js?id=AW-…&cx=c`. Container không cần có tag Ads. Cách nhận: danh sách request có cả `id=AW-…` và `id=AW-…&cx=c`, `window.google_tag_manager` có khoá `AW-…`. Site bán lẻ mẫu 31/10/2026: trùng ở 3/4 lượt Chrome, mỗi lượt thừa 147 KB, PSI desktop có thêm long task 50–70 ms.
  - Không sửa bằng cách để Google tag tự nạp AW (bỏ thẻ của plugin). Một bản `cx=c` gánh hết việc thành 1 task 104–166 ms. PSI desktop tụt từ trung vị 99,5 xuống 97, TBT tăng khoảng 60 ms (loader v1.3 của site mẫu, chạy 18 phút rồi thay).
  - Không nạp AW sớm hơn GTM. Loader v1.4 của site mẫu nạp AW ở mốc hẹn giờ − 600 ms. Ở 3/6 lượt PSI mobile, AW bắt đầu trước LCP quan sát, nên Lantern tính 147 KB của AW vào LCP mô phỏng: LCP 2,2 → 3,7–3,85 s, trung vị trang chủ mobile 91 → 84,5. Kiểm bằng `networkRequestTime` của AW so với `observedLargestContentfulPaint` trong `audits.metrics`.
  - Cách đúng (mẫu hiện tại, v1.5 của site mẫu): nạp thẻ AW của plugin và `gtm.js` cùng một mốc, cả hai `async=false`. Trình duyệt tải song song và thực thi theo thứ tự chèn, AW trước `gtm.js`. Google tag thấy AW đã đăng ký nên không nạp lại. Dự phòng: 4 s sau khi `gtm.js` nạp mà chưa có khoá AW thì nạp lại thẻ của plugin. Site mẫu: AW 1 lần, AW và GTM cùng lúc ~2,1 s, hit Ads và GA4 không đổi ở 4 trang sống.
- A/B thẻ tag bằng `Network.setBlockedURLs`: mẫu chặn khớp theo tiền tố, nên chặn `…/gtag/js?id=AW-…` cũng chặn luôn bản `…&cx=c`. Muốn bỏ một thẻ khỏi trang, trả HTML đã sửa qua `Fetch.fulfillRequest` cho đúng URL tài liệu. Site mẫu 31/10/2026: bản B đầu tiên chặn cả hai thư viện, 0 hit Ads, kết luận sai.
- Hit GA4 mang `em` dù dataLayer không có PII: GA4 tự phát hiện email ở chân trang, mọi khách cùng một mã băm. Việc tắt nằm trong cài đặt Google tag của GA4, cần người có quyền Editor quyết.
- Cổng thanh toán quay về site thành nguồn referral mới. Đề xuất loại trừ domain cổng trong GA4, để người duyệt quyết.
- Cổng thanh toán để chế độ sandbox trên site thật làm đơn giả thành conversion. Ghi thành việc nghiệp vụ, không sửa trong GTM.
- Quota GTM API khoảng 15 lượt mỗi phút mỗi user. `gtm_api.py` chờ 4,5 s giữa các lượt gọi và thử lại khi gặp 429.
