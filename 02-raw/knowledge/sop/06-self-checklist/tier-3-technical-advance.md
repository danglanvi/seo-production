---
type: sop
status: stable
last_updated: 2026-06-26
tags: [sop, technical-seo, audit, crawl, core-web-vitals, page-speed]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/tier-3-technical-advance.md` ngày 2026-07-17.
> Bản chưng cất — đã lược evidence/theory; bản đầy đủ ở kho gốc.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# SOP 06 — Tier 3: Technical Advance Checklist

> Checklist technical nâng cao (Koray-based). Mỗi hạng mục có **tiêu chí ĐẠT đo được** + tool kiểm — tick ✅ theo cột Tiêu chí ĐẠT.
> Mọi ngưỡng technical quy về một câu hỏi gốc: *Search Engine tốn bao nhiêu "effort" để fetch + parse + hiểu + rank trang này?* (Cost of Retrieval). CoR thấp = SE ưu tiên rank.

---

## 0. Cách đọc GSC Crawl Stats (đọc trước khi audit)

> `Search Console → Settings → Crawl stats`. Đây là "bảng tổng sức khỏe crawl" của site. 3 panel đầu là **3 checkpoint bắt buộc** (mục 2.1–2.3 bên dưới).

| Panel trong GSC | Nó cho biết điều gì | Ngưỡng GTV |
|---|---|---|
| **Average response time (ms)** | Server trả byte đầu tiên nhanh hay chậm. Chậm = Googlebot crawl được ít trang hơn / dễ timeout. | **< 200ms** (tốt) — **< 350ms** (tối thiểu chấp nhận). > 500ms = cờ đỏ. |
| **By response** | Phân bố mã trả về (200, 304, 3xx, 4xx, 5xx) Googlebot nhận. | Chủ yếu **200 + 304**. 4xx/5xx phải < 1%. 304 cao là dấu hiệu *tốt* (xem 2.2). |
| **By file type** | Crawl budget đang đổ vào loại tài nguyên nào (HTML, Image, CSS, JS, Other). | **HTML là tỷ trọng "việc thật"**. Nếu Image/Other nuốt phần lớn → đang lãng phí budget (xem 2.3). |
| **By purpose** | `Refresh` (crawl lại trang cũ) vs `Discovery` (tìm trang mới). | Site trưởng thành: Refresh cao là bình thường. Discovery ~0 kéo dài + đang publish nhiều = trang mới không được phát hiện → soi internal link + sitemap. |
| **By Googlebot type** | Image / Smartphone / Desktop / Page resource load. | Smartphone phải là chủ đạo cho việc crawl HTML (mobile-first indexing). Image cao là bình thường nếu site nhiều ảnh. |

> **Lưu ý cách đọc:** đây là dữ liệu *toàn site theo loại request*, không phải per-URL. Site đã ổn định có 304 nhiều hoặc "Other" file type cao là bình thường — đừng nhầm "304 nhiều = lỗi". Phần cần soi là **200 cho HTML** và **bất kỳ 4xx/5xx nào**.

---

## 1. Setup công cụ (làm 1 lần khi nhận dự án)

| # | Hạng mục | Tiêu chí ĐẠT |
|---|---|---|
| 1.1 | **Google Search Console** | Đã verify domain property (không chỉ URL prefix); cả http→https, www & non-www đều add. |
| 1.2 | **GA4** | Đã gắn, data flowing, loại bỏ internal traffic. |
| 1.3 | **RankMath** (hoặc tương đương) | Cài + cấu hình title/meta/schema mặc định; sitemap bật. |
| 1.4 | **TOC** (Table of Contents) | Plugin/section TOC hoạt động trên bài dài (hỗ trợ jump-link + passage indexing). |
| 1.5 | **Insert Header and Footer** | Có cơ chế chèn script header/footer (GSC verify, schema custom, tracking) mà không sửa theme core. |

---

## 2. Crawl & Index Health *(3 checkpoint GSC)*

> 3 mục dưới đọc thẳng từ GSC Crawl Stats (mục 0) — thước đo khách quan cho Cost of Retrieval của site, **trước** khi đi sửa từng kỹ thuật.

| # | Hạng mục | Tiêu chí ĐẠT / Cách kiểm tra |
|---|---|---|
| 2.1 | **Average Response Time < 200ms** | GSC Crawl Stats → Average response time **< 200ms** (mục tiêu) hoặc **< 350ms** (tối thiểu). > 500ms kéo dài → kiểm hosting, TTFB, query DB, thiếu cache/CDN. |
| 2.2 | **By Response chủ yếu là 200 (và 304)** | Tổng **200 + 304 ≥ ~95%**. **4xx < 1%**, **5xx ~0%**. Soi list trang trả 404/410/5xx → fix hoặc redirect. 301 lác đác OK; 301 hàng loạt = có redirect chain cần dọn. (304 = bot không tải lại trang không đổi → *tiết kiệm* crawl budget, không phải lỗi.) |
| 2.3 | **By File Type chủ yếu là HTML** | HTML là tỷ trọng chính của phần crawl nội dung. Nếu Image/Other áp đảo bất thường → chặn tài nguyên không cần qua robots.txt, gộp/cache CSS-JS, audit ảnh thừa. *(Site nội dung/blog: ráng HTML chiếm ưu thế; ecom/media nhiều ảnh: chấp nhận Image cao hơn.)* |
| 2.4 | **Discovery không tắc** | By purpose: có Discovery khi đang publish; trang mới index trong 24–48h (URL Inspection). Nếu không → internal link tới trang mới + submit sitemap. |
| 2.5 | **Index sạch (không bloat)** | GSC Pages: số trang indexed khớp số trang *muốn* rank. Trang thin/duplicate/parameter → noindex + dọn internal link. |

---

## 3. Tốc độ tải trang & Cost of Retrieval

> Mọi mục dưới đây đều nhằm hạ Cost of Retrieval: làm trang nhẹ hơn, tải nhanh hơn, để byte quan trọng tới trình duyệt (và bot) sớm nhất.

| # | Hạng mục | Tiêu chí ĐẠT / Cách kiểm tra |
|---|---|---|
| 3.1 | **Minify HTML** | HTML mỗi trang gọn (mục tiêu tham chiếu: ~15KB). Kiểm: View Source / build tool đã minify. |
| 3.2 | **Tái cấu trúc CSS & JS (gỡ "code spaghetti")** | Giảm *số lượng* file CSS/JS mỗi trang; mỗi file có mục đích rõ; không CSS/JS chết. |
| 3.3 | **CSS/JS dùng chung toàn site để cache được** | Có file CSS dùng chung site-wide (vd `headfoot.css`) + file riêng theo nhóm template (blog / category / product). Cache header bật (xem 4.6). |
| 3.4 | **Nén văn bản server-side bằng Brotli** | Response header `content-encoding: br` cho HTML/CSS/JS. Fallback Gzip cho client cũ. Kiểm: DevTools → Network → Response Headers. |
| 3.5 | **Dùng HTTP/2 (hoặc HTTP/3)** | Site chạy HTTP/2+. Kiểm: DevTools → Network → cột Protocol = `h2`/`h3`. *(Cẩn trọng HTTP/2 Server Push: push nhiều phản tác dụng, không cache được; Push đã bị nhiều trình duyệt deprecate → ưu tiên `preload` ở 3.6.)* |
| 3.6 | **Thứ tự tải tài nguyên & ưu tiên (preload)** | `<link rel="preload">` cho: ảnh LCP, CSS header, font chính, JS chức năng — đặt đầu `<head>`, *trước* các stylesheet thường. |
| 3.7 | **Preconnect cho tracker bên thứ 3** | `<link rel="preconnect">` cho domain analytics/ads/font bên ngoài thật sự dùng. Không preconnect tràn lan (mỗi connection tốn tài nguyên). |
| 3.8 | **Defer các tracker bên thứ 3 không liên quan nội dung** | Tracker/pixel/chat widget gắn `defer`. *Lưu ý:* (a) defer JS chính có thể làm chậm "khởi tạo" của nó; (b) defer quá nhiều → dồn xử lý gây nghẽn CPU lúc tải xong. Cân đối, không defer file JS chức năng quan trọng nhất. |
| 3.9 | **Async cho JS nội dung/chức năng chính** | Chỉ async file JS chính tập trung vào nội dung/chức năng (vd `main.js`). Không async lung tung gây race condition. |
| 3.10 | **Tránh xung đột Content-Type giữa Response Header & file HTML** | `Content-Type: text/html; charset=utf-8` đúng cho trang HTML; không lệch MIME. Kiểm: DevTools → Network → Headers. |
| 3.11 | **Web App Manifest** | Có `manifest.json` hợp lệ (name, icons, theme_color). Kiểm: DevTools → Application → Manifest. |

### Tối ưu hình ảnh (nhánh của tốc độ)

| # | Hạng mục | Tiêu chí ĐẠT / Cách kiểm tra |
|---|---|---|
| 3.12 | **Định dạng AVIF (image capping)** | Ảnh chính dùng `.avif` (fallback WebP/JPG qua `<picture>`). Xuất ở 1x (image capping — 1 pixel/điểm ảnh); dùng thuật toán resample tốt (Nearest/Bilinear). |
| 3.13 | **Lazy-load bằng Intersection Observer** | Ảnh dưới fold lazy-load qua Intersection Observer (kiểm soát tốt hơn attribute `loading="lazy"` cũ). Ảnh trong màn hình đầu (LCP) **không** lazy-load. |
| 3.14 | **`srcset` (responsive images)** | `<img srcset>` + `sizes` cho ảnh nội dung chính. |
| 3.15 | **Metadata ảnh: dùng IPTC, không EXIF** | Ảnh quan trọng có IPTC (title/description/owner/license). Bỏ EXIF nặng/không cần. Cố định ảnh ~600px giúp cân bằng performance mobile & desktop. |
| 3.16 | **Placeholder ảnh (LQIP) — có lưu ý** | Dùng placeholder nhẹ. **Lưu ý:** placeholder bằng JS có thể *không hiện ảnh* với Googlebot khi nó không render JS → ảnh quan trọng cho SEO nên có nguồn trong HTML (`<img src>`/`<picture>`), không phụ thuộc hoàn toàn JS. |
| 3.17 | **Image Sitemap + Structured Data + Representative Image** | Có image sitemap (hoặc ảnh trong sitemap chính); schema `ImageObject`/Article image; mỗi trang có 1 ảnh đại diện rõ ràng (gắn với centerpiece). |

---

## 4. Tối ưu HTML

| # | Hạng mục | Tiêu chí ĐẠT / Cách kiểm tra |
|---|---|---|
| 4.1 | **Semantic HTML** | Tuân **6 Golden Rules**: 1 `<h1>`/trang; không skip cấp heading; 1 `<main>`/trang; `<article>` self-contained; `<section>` có heading chủ đề; `<strong>`/`<em>` (semantic) thay `<b>`/`<i>` (chỉ visual). |
| 4.2 | **Giảm lỗi HTML (HTML normalization)** | Validate qua W3C Validator; sửa lỗi nghiêm trọng (thẻ chưa đóng, nested sai, duplicate id). HTML lỗi đẩy trình duyệt vào "quirks mode". |
| 4.3 | **Giảm kích thước DOM** | DOM < ~1.500 node (Lighthouse cảnh báo nếu vượt). Gợi ý: phân tích DOM trung bình của đối thủ để đặt mục tiêu. |
| 4.4 | **Giảm số lượng & kích thước font** | Dùng Woff2; gộp variant bằng variable font (bold/italic/regular → 1 file); tối thiểu số font-family. > 5 file font = tác động đáng kể. |
| 4.5 | **Xử lý FOUT / FOIT** | Preload font chính + `font-display: swap` trong CSS. |
| 4.6 | **Browser-side caching cho tài nguyên tĩnh** | HTTP header `Cache-Control: max-age=...` + `ETag` cho tài nguyên tĩnh (CSS, JS, font, ảnh). Kiểm: DevTools → Network → Headers. |
| 4.7 | **Website Accessibility** | Alt text cho ảnh nội dung; ARIA khi cần; tab order hợp lý; contrast đạt; heading hierarchy đúng. |

---

## 5. Core Web Vitals

> Phần này **trùng nhiều** với mục 3–4 (đó là chủ ý). Ở đây gom theo *từng metric* để audit nhanh; chỗ nào đã làm ở trên thì trỏ ngược, không lặp lại thao tác.

### 5.1 LCP (Largest Contentful Paint) — mục tiêu < 2.5s
| Việc | Ghi chú |
|---|---|
| Hosting hiệu năng cao | Nền tảng của TTFB thấp (→ mục 2.1). |
| CDN | Phục vụ tài nguyên từ edge gần user. |
| Tối ưu CSS/JS | Gỡ CSS/JS không dùng; minify; defer (→ 3.2, 3.8). |
| Preload phần tử LCP | Preload ảnh/heading hero (→ 3.6). |

### 5.2 INP (Interaction to Next Paint) — *thay thế FID từ 03/2024*; mục tiêu < 200ms
| Việc | Ghi chú |
|---|---|
| Gỡ plugin không dùng | Bớt JS chạy nền → main thread rảnh hơn. |
| Theme/framework nhẹ | Vd WordPress: framework nhẹ (Genesis...) thay theme nặng. |
| Giảm JS long-task | Chia nhỏ task dài; defer/async đúng chỗ (→ 3.8–3.9). |

> *Ghi chú:* Google đã thay FID bằng **INP** từ tháng 03/2024 — các việc tối ưu giữ nguyên, chỉ đổi tên metric.

### 5.3 CLS (Cumulative Layout Shift) — mục tiêu < 0.1
| Việc | Ghi chú |
|---|---|
| Cập nhật PHP mới nhất | Hiệu năng nền tảng. |
| Đặt `width`/`height` (hoặc `aspect-ratio`) cho ảnh & video | Trình duyệt chừa sẵn chỗ → không nhảy layout (→ 3.16 placeholder). |
| Preload font | Tránh FOUT/FOIT gây dịch chữ (→ 4.5). |

---

## 6. Web Design & Visual Semantics

> Nhóm này về cách Google *nhìn* layout trang để hiểu khối nào quan trọng.

| # | Hạng mục | Tiêu chí ĐẠT / Cách kiểm tra |
|---|---|---|
| 6.1 | **Web Design (representation vectors)** | Style component nhất quán; phân loại trang rõ (homepage / product / blog); layout có hệ thống, không tạp. |
| 6.2 | **Read Time Calculation** | Đặt câu trả lời + entity chính ở đầu (above-the-fold + đầu mỗi section) → answer-first. |
| 6.3 | **Visual Segmentation theo gap & text block** | Các khối nối tiếp theo thứ bậc & hài hòa; không để khoảng trống rời rạc; mỗi khối là "khối visual hoàn chỉnh". |
| 6.4 | **VIPS (Vision-based Page Segmentation)** | Khối trên cùng (centerpiece) tải nhanh + nói đúng chủ đề trang. Validate bằng **Blur Test**: blur screenshot 1440px → vẫn đoán đúng chủ đề chính = ĐẠT. |
| 6.5 | **LIFT Model** | Trang có hierarchy rõ, 1 intent chủ đạo; layout dẫn hướng intent đó. Ref: widerfunnel.com/conversion-optimization-framework. |
| 6.6 | **Tối ưu logfile (Kibana + ElasticSearch)** | Có dashboard log (Kibana/ELK hoặc tool tương đương); theo dõi bot hit theo URL group, status code, tần suất. |

---

## 7. Chuyển dịch HTTPS

| # | Hạng mục | Tiêu chí ĐẠT |
|---|---|---|
| 7.1 | Secure content không lỗi | Không mixed content (HTTP asset trên trang HTTPS). |
| 7.2 | Server key còn hạn & đủ mạnh | SSL cert chưa hết hạn; key không yếu (≥ 2048-bit RSA / ECDSA). |
| 7.3 | Site đã có SSL | Toàn site phục vụ qua HTTPS. |
| 7.4 | HTTP → HTTPS redirect | Bản không an toàn 301 về bản HTTPS (không để truy cập song song). |
| 7.5 | Canonical trỏ đúng bản HTTPS | Trang HTTPS có canonical self-referential về chính nó (HTTPS). |
| 7.6 | Disavow file đã cập nhật cho HTTPS | (Nếu có disavow) đã submit lại cho property HTTPS. |
| 7.7 | Bản HTTPS không bị chặn | Robots/firewall không chặn HTTPS. |
| 7.8 | GSC đã chuyển sang HTTPS | Property/settings trong GSC dùng bản HTTPS. |
| 7.9 | Hreflang cập nhật cho HTTPS | Thẻ hreflang trỏ URL HTTPS. |
| 7.10 | Certificate đăng ký đúng host | Cert khớp tên host/phiên bản (không sai SAN/CN). |
| 7.11 | www vs non-www thống nhất + redirect | Chọn 1 bản chuẩn, bản còn lại 301 về. |
| 7.12 | Không truy cập được cả http & https song song | Chỉ 1 bản canonical phục vụ 200, còn lại redirect. |

---

## 8. Sitemap

| # | Hạng mục | Tiêu chí ĐẠT |
|---|---|---|
| 8.1 | Có XML sitemap | Tồn tại + truy cập được. |
| 8.2 | Sitemap đã submit (bản HTTPS) | Submit trong GSC (và Bing nếu áp dụng), dùng URL HTTPS. |
| 8.3 | Sitemap không lỗi XML | Validate, không lỗi cú pháp/encoding. |
| 8.4 | Chỉ chứa URL 200 | Không có trang 3xx/4xx/5xx trong sitemap. |
| 8.5 | Chỉ chứa URL canonical | Không liệt non-canonical / noindex. |
| 8.6 | URL trong sitemap không bị block | Không bị robots.txt chặn. |
| 8.7 | Dung lượng hợp lệ | ≤ 50.000 URL / ≤ 50MB mỗi file; lớn hơn → chia + dùng sitemap index. |
| 8.8 | Tổ chức ngăn nắp & đầy đủ | Tách theo loại: post, page, category, product, (sitemap đặc thù ngành). Không thiếu loại. |

---

## 9. Robots.txt

| # | Hạng mục | Tiêu chí ĐẠT |
|---|---|---|
| 9.1 | Có file robots.txt | Tồn tại tại root, trả 200. |
| 9.2 | Bản HTTPS có robots.txt | Không thiếu ở bản HTTPS. |
| 9.3 | Chặn URL quản trị | Disallow trang admin/login. |
| 9.4 | Khai báo sitemap trong robots.txt | Dòng `Sitemap:` trỏ sitemap index. |
| 9.5 | Robots.txt không lỗi | Cú pháp đúng; không vô tình chặn tài nguyên/trang cần crawl (CSS/JS cần cho render **không** được chặn). |

---

## 10. International (hreflang)

| # | Hạng mục | Tiêu chí ĐẠT |
|---|---|---|
| 10.1 | Không trộn dịch lẫn lộn | Mỗi URL 1 ngôn ngữ nhất quán, không pha. |
| 10.2 | hreflang & canonical dùng đúng | Canonical self-referential per bản; hreflang không mâu thuẫn canonical. |
| 10.3 | Không thiếu link hreflang | Mọi bản ngôn ngữ liên kết chéo đầy đủ. |
| 10.4 | Có self-referential hreflang | Mỗi trang trỏ hreflang về chính nó. |
| 10.5 | Giá trị hreflang đúng | Đúng mã ngôn ngữ-vùng (ISO 639-1 + 3166-1, vd `en-us`). |
| 10.6 | URL trong hreflang hợp lệ | Trỏ URL 200, canonical, HTTPS. |
| 10.7 | Không trùng phiên bản cùng ngôn ngữ | Không nhiều URL cùng ngôn ngữ cạnh tranh. |
| 10.8 | Ngôn ngữ khai trong HTML | `<html lang="...">` đúng. |
| 10.9 | Có link theo quốc gia cụ thể | Phiên bản quốc tế liên kết theo country-specific khi cần. |
