# Site chồng nhiều plugin tối ưu (LiteSpeed Cache, Perfmatters, plugin của host, Cloudflare APO)

Đọc ở Bước 3–4 khi site bật từ 2 plugin tối ưu trở lên, hoặc dùng theme đa năng có WooCommerce.

Nguồn: nhật ký tối ưu của SEO Lead dự án trên site TMĐT mẫu (theme đa năng + WooCommerce, khoảng 150 request mỗi trang), giai đoạn 1 cuối 9/2026 và giai đoạn 2 ngày 27–30/10/2026. Kết quả trang chủ, 1 lượt PSI đại diện:
- Mobile 61 → 96 điểm. LCP mobile 10,1 s → 1,5 s.
- INP lab (CPU chậm 4 lần) nhóm danh mục: 448 ms → 104–128 ms.
- Điểm mobile dao động 5–10 điểm giữa các lượt.

## 1. Mỗi việc một plugin

- Đọc HTML live để biết cài đặt nào thật sự có hiệu lực. Ca đã gặp: phần của Perfmatters bị bọc trong `<noscript>`, nên Delay và Async không có tác dụng.
- Giao cache cho LiteSpeed hoặc Cloudflare. Giao CSS và JS cho đúng một plugin. Tắt tính năng trùng ở plugin còn lại: Critical CSS, Delay CSS, Lazyload ảnh.
- Lỗi đã gặp:
  - Script lazyload của plugin host giữ ảnh LCP lại 4 giây.
  - Used CSS bị tải 2 bản: 157 KB của Perfmatters và 155 KB bản LiteSpeed minify lại. Loại file used CSS khỏi CSS Minify của LiteSpeed.
- Cloudflare đã cache HTML (APO hoặc Cache Rule): tắt Guest Mode và Guest Optimization của LiteSpeed. Lý do: khách mới bị tải trang 2 lần (`fcp-guest-mode.md`). Ở site mẫu, việc này giảm LCP mobile nhiều nhất trong mọi hạng mục.

## 2. Used CSS theo loại trang

- Perfmatters tạo used CSS theo loại trang (front, tax, product…) từ một trang mẫu. Trang cùng loại nhưng khác template sẽ thiếu style. Site mẫu: hero vỡ, CLS desktop trang danh mục 0,52–1,03.
- Safelist và Excluded Selectors không giữ được mọi class. Chèn CSS bố cục quan trọng (lưới, hero) vào Custom CSS của theme. Site mẫu chèn 3,3 KB CSS trích từ CSS của theme. Sub-cate desktop tăng 66 → 97, CLS về 0,001.
- Đặt Stylesheet Behavior là Async, không đặt Delay. Delay chỉ nạp CSS đầy đủ khi khách chạm hoặc di chuột, nên hero vỡ tới lúc tương tác.
- Sau mỗi lần đổi: Clear Used CSS, purge, mở lại các trang chính.

## 3. JavaScript và tracking

- Bật Defer JavaScript thì bật kèm Include Inline Scripts. Chỉ defer script ngoài sẽ gây lỗi `jQuery is not defined`, hỏng select2 và nút Read more. Kiểm chức năng trên mọi loại trang sau khi bật.
- Delay tracking tới lần tương tác: đặt từ khoá theo chuỗi có trong đoạn inline. Clarity dùng `clarity.ms/tag`, không dùng `clarity.js`.
- Xoá thẻ GA mẫu chưa thay ID (`G-XXXXXXX`). Thẻ này tải 153 KB vô ích. Giữ hàm `gtag` và khối consent default.
- Banner cookie gọi `sendGtag()` trong `requestAnimationFrame` làm chậm khung hình phản hồi (INP). Đổi thành `requestAnimationFrame(function () { setTimeout(sendGtag, 0); })`. Kiểm consent default và update vẫn đủ trong dataLayer.
- LiteSpeed Localize Resources có thể lưu hỏng file bên thứ ba. Ca đã gặp: `fbevents.js` trả chữ "Not supported", gây lỗi cú pháp. Bỏ file đó khỏi danh sách Localization.

## 4. Ảnh trong menu và slider

- WordPress tự gắn `fetchpriority="high"` cho ảnh lớn đầu tiên trong HTML, kể cả ảnh ẩn trong mega menu. Kiểm mỗi trang chỉ còn một ảnh `fetchpriority="high"`.
- Ảnh trong menu: đặt `loading="lazy"`, `sizes` theo bề rộng hiển thị, `src` là bản nhỏ. Cách làm: bật cờ trong filter `wp_nav_menu_objects`, tắt cờ trong `wp_nav_menu_items`, đổi thuộc tính trong `wp_get_attachment_image_attributes` khi cờ bật. Mẫu cài được: `templates/menu-image-lazy.php`.
- Script theme (`imagesLoaded`, slider khởi tạo ngay) có thể ép tải ảnh ẩn. Site mẫu giảm ảnh tải sớm 1.247 KB → 208 KB nhưng PSI chỉ tăng 1–3 điểm. Xếp việc này ưu tiên thấp, lợi chủ yếu cho mạng yếu.

## 5. Đo và kết luận

- Đo cả bản có cache và bản không cache. Khách thật đa số nhận bản cache.
- Đợi 1–2 phút sau purge và mở trang một lần trước khi đo.
- Không kết luận từ một lần đo. Site mẫu rút lại 3 kết luận sau khi đo lặp:
  - 682 hiệu ứng CSS làm chậm.
  - Lớp preload CSS gây tải ảnh.
  - INP 2,8 s. Số này sai vì lượt đo headless chạm vào chữ tĩnh.
- INP: lấy các nhóm URL trong báo cáo Core Web Vitals của GSC. Đo lab với CPU chậm 4 lần trên URL đại diện của mỗi nhóm.
- Section có DOM rất lớn (site mẫu: 2.580 thẻ, 519 ảnh) làm INP sát ngưỡng. Chỉ dựng phần đầu, dựng phần còn lại khi khách bấm "Xem thêm". Việc này cần dev sửa template.
- Sau khi sửa INP hoặc CLS: bấm Validate Fix trong GSC. Trạng thái chuyển Good sau khoảng 28 ngày dữ liệu thật.
- Trang nặng: điểm mobile 90+ đến chủ yếu từ việc bỏ reload và dọn chồng chéo plugin. Phần còn lại cần giảm DOM, HTML và số file CSS, JS ở cấp template.

## 6. Bẫy khi sửa qua wp-admin

- Không dùng chú thích nhiều dòng trong CSS dán vào Custom CSS. Mất dòng chứa `*/` thì cả khối CSS phía sau thành chú thích, không báo lỗi. Sau khi dán, đếm `/*` và `*/` trên HTML live.
- Sửa CSS hoặc JS của theme con thì tăng tham số `ver`. CDN cache file tĩnh 1 năm theo tham số này.
- Preload font chỉ khi đã A/B (`checklist-theo-lop.md` lớp 4). Thẻ preload font phải có `crossorigin`. Thiếu thuộc tính này, trình duyệt tải font 2 lần.
- Console báo 503 ở file chunk mà theme gắn `rel="prefetch"`: CDN từ chối một phần request tải trước. Khi trang cần file thật, file tải lại với mã 200. Không cần sửa.

## 7. Hỗ trợ tiếp cận

Đọc khi PSI Accessibility dưới 90.

- Lỗi trọng số cao đã gặp:
  - `role="table"` thiếu `role="row"`.
  - Link icon, nút slider và nút danh mục không có tên.
  - Ô select thiếu nhãn.
  - Ảnh thiếu alt.
  - Chữ không đủ tương phản.
- Sửa bằng CSS tương phản và một script nhỏ gắn `aria-label`. Script dùng MutationObserver để gắn nhãn cho phần tử tạo muộn. Mẫu: `templates/a11y-ten-phan-tu.js` (nhãn vi hoặc en theo `<html lang>`, link mạng xã hội, Zalo, `tel:`, nút slider, select, vùng `aria-hidden`). Sửa tên phần tử trong template trước. Script chỉ là lớp vá ở trình duyệt.
- Site mẫu tăng 80–83 → 99–100 khi chạy thử. Thứ tự heading để nguyên vì liên quan cấu trúc SEO.
