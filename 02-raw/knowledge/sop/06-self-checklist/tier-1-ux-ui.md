---
type: sop
tier: 1
phase: ux-ui
last_updated: 2026-07-19
source_file: "raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/Content/Tiêu chuẩn Content Category & Product UXUI - (PSP) GTV SEO.xlsx"
items_count: 18
related:
  - "[[Website Functions]]"
  - "[[Faceted Navigation]]"
  - "[[URL SEO]]"
  - "[[Core Web Vitals]]"
  - "[[Product Detail Page]]"
  - "[[Product Category Page]]"
tags: [sop, tier-1, ux-ui, wireframe, design-review, self-checklist]
---

# Tier 1 — Self-Checklist: UX & UI (UX-01…UX-18)

> **Khi dùng:** 2 thời điểm — (1) **duyệt wireframe T2** (cùng đợt cấu trúc website), (2) **review landing/CRO T8-T10** khi tối ưu trang thương mại đã có traffic.
> **Số items:** 18. **Scoring:** Self Score /18 → Self %. Review 3 tầng như các checklist Tier 1 khác.
> **Nguồn chính:** `Tiêu chuẩn Content Category & Product UXUI - (PSP) GTV SEO.xlsx` (~2024) + section UX-UI của `Checklist triển khai cấu trúc website.xlsx` (2020) — chắt lọc + modernize (mobile-first, review ladder, perceived speed, accessibility là phần MỚI). Cột **Nguồn** ghi rõ legacy / mới.
> **Ranh giới:** layout semantic (centerpiece, hierarchy, block, ảnh) → `tier-1-visual-semantic.md` · conversion elements (CTA hệ thống, tracking, funnel) → `tier-1-cro-conversion.md` · kiến trúc URL/index → `tier-1-structure-website.md` · deliverable wireframe trước khi gửi khách → `gate-structure-wireframe.md`.

## 🔴 P0 Gate — 5 items PHẢI pass

| Gate | Item | Điều kiện |
|---|---|---|
| G1 | UX-01 | Mobile-first: mọi template không vỡ layout ở breakpoint chuẩn |
| G2 | UX-04 | Menu ≤2 tầng chạm tới mọi URL SEO chính |
| G3 | UX-07 | Category có filter/sort đúng chuẩn thị trường |
| G4 | UX-11 | Product/Service có buy-box / quote-box đủ yếu tố + CTA chính |
| G5 | UX-15 | Click-to-call / Zalo hiện diện (thị trường VN) |

---

## Phần A — Mobile-first (MỚI — legacy 2020 chỉ ghi "kiểm tra bản di động")

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| UX-01 | 🔴 **Breakpoint chuẩn, không vỡ layout** | Mọi template (home, category, product, service, blog) render đúng ở breakpoint đã chốt cho dự án (tối thiểu: 1 mobile ~375-430px, 1 tablet ~768-780px, 1 desktop ≥1280px); không tràn ngang, không element chồng nhau; wireframe phải có BẢN MOBILE riêng, không chỉ desktop | Legacy (Ecom 4.0 "ưu tiên bản di động") + MỚI |
| UX-02 | **Tap target + spacing** | Mọi element bấm được (nút, link, filter chip, swatch) tap area ≥44px, khoảng cách đủ để không bấm nhầm; hover-only interaction (tooltip, dropdown hover) phải có equivalent cho touch | MỚI |
| UX-03 | **Font size đọc được** | Body text ≥16px mobile (không bắt zoom); line-height ≥1.4; không đoạn text nào render dưới 12px (kể cả caption, breadcrumb) | MỚI |

## Phần B — Navigation

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| UX-04 | 🔴 **Menu ≤2 tầng tới URL SEO** | Mọi URL SEO chính (danh mục core, trang dịch vụ) reachable từ menu trong ≤2 tầng; bố cục menu chốt rõ tầng nào show ra (mega menu / dropdown); menu chọn lọc — không nhồi mọi URL | Legacy (cấu trúc 2020 R19: "cấu trúc menu — tầng nào show trên menu") |
| UX-05 | **Breadcrumb mọi template con** | Category / sub-cate / product / service / blog đều có breadcrumb clickable, khớp cấu trúc tầng; vị trí nhất quán đầu trang (schema BreadcrumbList check ở `tier-1-structure-website.md` ST-13) | Legacy (UXUI xlsx: breadcrumb có mặt ở cả 4 page types) |
| UX-06 | **Search nếu site lớn** | Site >~50 sản phẩm hoặc >100 bài: có search box vị trí dễ thấy (header), có gợi ý/autocomplete nếu e-com; site nhỏ được phép bỏ | MỚI (chuẩn hóa từ "chức năng đặc trưng thị trường" 2020 R15) |

## Phần C — Category page UX (nguồn chính: UXUI xlsx mục Category)

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| UX-07 | 🔴 **Filter / Sort đúng chuẩn thị trường** | Bộ lọc + sắp xếp theo giá, tính năng đúng chuẩn benchmark thị trường của ngành (soi đối thủ mạnh nhất); attribute demand thấp nằm ở FILTER, không thành danh mục riêng (quyết định index của facet → ST-12); filter hoạt động thật, không misleading | Legacy (UXUI: "bộ lọc sắp xếp giá, tính năng" + Ecom 2.0/5.0) |
| UX-08 | **Product box đủ thông tin + trạng thái chọn** | Box sản phẩm trong grid hiển thị đủ: ảnh, tên, giá (+ giá gạch nếu sale), trạng thái/rating nếu có; hiệu ứng chọn/hover rõ (user biết đang tương tác với item nào); link đến sub-cate + category cùng cấp hiện diện trên trang | Legacy (UXUI: box sp tổng quan, hiệu ứng chọn sản phẩm, link sub-cate/cùng cấp) |
| UX-09 | **Số SP/trang + pagination chuẩn SEO** | Số sản phẩm mỗi trang hợp lý theo benchmark ngành (thường 20-40); phân trang có page links crawlable (`<a href>` thật) — không infinite-scroll-only / load-more-only; trang phân trang giữ filter state rõ ràng cho user | Legacy (UXUI: phân trang) + MỚI (chuẩn SEO — chi tiết canonical ở ST-11) |
| UX-10 | **Content danh mục + blog bổ trợ không phá UX** | Đoạn content danh mục (intro đầu + mô tả) và khối blog bổ trợ có vị trí không đẩy product grid xuống quá sâu (hàng sản phẩm đầu trong ~1 màn hình); blog bổ trợ custom-link được | Legacy (UXUI: content danh mục, blog bổ trợ custom link; Ecom 2.0 "đoạn text giới thiệu ở đầu") |

## Phần D — Product / Service page UX (nguồn chính: UXUI xlsx mục Sản phẩm + Service)

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| UX-11 | 🔴 **Buy-box / Quote-box đủ yếu tố + CTA chính** | Product: khối mua hàng gom đủ — giá, giá giảm, tình trạng kho, mã SP, CTA chính — trong 1 vùng nhìn thấy ngay; Service: quote-box/form + hotline thay vai trò buy-box. CTA chính duy nhất, nổi bật nhất trang (hệ CTA site-wide → CR-03) | Legacy (UXUI: giá/mã/tình trạng + CTA; Service: CTA form) |
| UX-12 | **Gallery ảnh: slide + zoom** | Ảnh sản phẩm dạng slide nhiều ảnh, có zoom; ≥1 ảnh unique không lấy từ nhà cung cấp (yêu cầu semantic của ảnh → VS-12) | Legacy (UXUI: hình ảnh slide, zoom; Ecom 6.0 "tối thiểu 1 hình unique") |
| UX-13 | **Thông tin đủ E-A-V** | Trang đủ các khối: mô tả ngắn → thông số chi tiết (bảng spec) → content mô tả + chính sách mua hàng đặc thù → thông tin hỗ trợ theo thị trường (bảo quản, quy trình, xác thực…); mỗi spec là 1 bộ Entity-Attribute-Value đo được, không mô tả sáo rỗng | Legacy (UXUI: mô tả ngắn, thông số chi tiết, content mô tả, thông tin hỗ trợ KH) + wiki [[E-A-V Framework]] |
| UX-14 | **Social proof hiển thị đúng ladder** | Đánh giá + hỏi đáp có mặt; hiển thị theo review ladder: 0 review = ẨN khối rating (không show ★0), ít review = list dọc, nhiều review = tổng hợp + filter; số liệu thật — không fake counter | Legacy (UXUI: đánh giá, hỏi đáp) + MỚI (ladder — skill visual-semantic-seo E6) |

## Phần E — Form UX

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| UX-15 | 🔴 **Click-to-call / Zalo cho VN** | Thị trường VN: nút gọi + Zalo (± Messenger) truy cập được từ mọi trang thương mại (header hoặc floating có phân cấp — xem CR-03); số hotline bấm gọi được trên mobile (`tel:`) | Legacy (UXUI: thông tin liên hệ hotline) + MỚI |
| UX-16 | **Form field tối thiểu + validation** | Form lấy đúng field tối thiểu cần cho bước sau (thường ≤4: tên, SĐT, ± email, ± nhu cầu); validation inline báo lỗi ngay tại field, message rõ; submit xong có phản hồi thành công rõ ràng | MỚI (modernize từ "CTA Form" trong UXUI xlsx) |

## Phần F — Tốc độ cảm nhận + Accessibility (MỚI)

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| UX-17 | **Skeleton / lazy-load hợp lý** | Lazy-load áp cho ảnh/khối DƯỚI fold; ảnh hero/LCP KHÔNG lazy (loading eager + width/height đặt trước — không CLS); vùng chờ data có skeleton/placeholder thay vì nhảy layout; đo thật ở `tier-3-technical-advance.md` (CWV) | MỚI — wiki [[Core Web Vitals]] |
| UX-18 | **Accessibility cơ bản** | Text contrast ≥4.5:1 (large text ≥3:1); focus state nhìn thấy được khi tab; ảnh nội dung có alt (chuẩn alt semantic → VS-13); mọi form field có label/placeholder rõ | MỚI |

---

## Quy trình tick

1. **T2 wireframe:** designer/SEO tick UX-01→UX-18 trên wireframe từng template → fix → mới trình khách (deliverable đủ/thiếu check ở `gate-structure-wireframe.md`).
2. **T8-T10 CRO:** tick lại trên trang live cho landing thương mại được chọn, chạy song song Phần B của `tier-1-cro-conversion.md`.
3. Item fail → note Self Note (lý do + plan fix); 5 items 🔴 fail bất kỳ → KHÔNG trình duyệt.
4. Mâu thuẫn giữa chuẩn UX và chuẩn layout semantic → ưu tiên xử theo `sop/07-visual-semantic.md` Phần D (trade-offs), quyết định theo dự án và ghi lại lý do.
