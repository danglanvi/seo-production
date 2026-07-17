---
name: semantic-html-optimization
description: Semantic HTML optimization for SEO and AI/LLM discoverability. Use when (1) Creating HTML templates for service pages or landing pages, (2) Auditing HTML structure of websites, (3) Optimizing HTML for AI/LLM citations from ChatGPT, Claude, Perplexity, (4) Implementing proper heading hierarchy with H1, H2, H3, (5) Deciding when to use article vs section elements, (6) Adding semantic elements like main, aside, time, figure, (7) Implementing Schema.org markup with semantic HTML, (8) Centerpiece extraction hygiene — main content flow liền mạch, share buttons/inject không cắt đoạn mở, (9) HTML budget 2MB + DOM order = visual order + rendering notes (image dimensions, JS bundle, metadata trong initial HTML). Triggers include HTML structure, heading hierarchy, semantic tags, article vs section, main content wrapper, AI-readable HTML, LLM optimization, centerpiece extraction, flow, HTML size.
---

# Semantic HTML Optimization

Optimize HTML structure for SEO and AI discoverability. 90% of ChatGPT citations come from well-structured pages.

## Overview

Skill này cung cấp kiến thức về tối ưu Semantic HTML cho SEO và AI discoverability. Semantic HTML không phải là ranking factor trực tiếp, nhưng giúp Google và LLMs (ChatGPT, Claude, Perplexity) hiểu cấu trúc và ý nghĩa của content.

**Core Insight:** 90% citations từ ChatGPT đến từ các trang có cấu trúc HTML tốt với heading hierarchy rõ ràng.

## When to Use This Skill

**Trigger phrases:**
- "Cấu trúc HTML chuẩn SEO"
- "Semantic HTML elements"
- "Heading hierarchy"
- "H1, H2, H3 structure"
- "Article vs section"
- "Main content wrapper"
- "HTML5 semantic tags"
- "AI-readable HTML"
- "LLM optimization"
- "Schema markup với HTML"

**Use cases:**
1. Tạo template HTML cho trang dịch vụ, landing page
2. Audit cấu trúc HTML của website
3. Tối ưu HTML cho AI/LLM citations
4. Hướng dẫn heading hierarchy chuẩn
5. Xác định khi nào dùng `<article>` vs `<section>`

## Core Principles

### 1. The Magazine/Newspaper Analogy

Semantic HTML giống như cấu trúc một tờ tạp chí:

| Element | Analogy | Purpose |
|---------|---------|---------|
| `<html>` | Tòa soạn | Toàn bộ website |
| `<head>` | Phòng biên tập | Metadata (không visible) |
| `<body>` | Số tạp chí | Tất cả content visible |
| `<header>` | Bìa tạp chí | Logo, navigation |
| `<nav>` | Mục lục | Site navigation |
| `<main>` | Nội dung chính | Primary content (only 1!) |
| `<article>` | Bài báo riêng lẻ | Self-contained content |
| `<section>` | Phần/Chapter | Thematic grouping |
| `<aside>` | Box chú thích bên lề | Related/tangential info |
| `<footer>` | Trang cuối | Copyright, contact |
| `<h1>-<h6>` | Đề mục bài | Content hierarchy |
| `<figure>/<figcaption>` | Hình + chú thích | Media with context |
| `<time>` | Ngày xuất bản | Date markup |
| `<strong>/<em>` | Nhấn mạnh | Semantic emphasis |

### 2. Content Weighting by Element — GTV editorial heuristic

> 🔴 **Re-label 2026-07-13 (LINT-2026-008):** % trong bảng = **thang ưu tiên biên tập nội bộ GTV** (`practitioner_framework`) — KHÔNG phải trọng số Google/LLM công bố; không có evidence "AI extracts `<article>` wholesale" hay "`<strong>` tăng citation". Giá trị chắc chắn của semantic HTML: accessibility, parsing robustness, logical landmarks, maintainability. Google official: không có yêu cầu HTML đặc biệt cho AI features (developers.google.com/search/docs/fundamentals/ai-optimization-guide).

| Element | Ưu tiên biên tập (heuristic) | Vai trò cấu trúc |
|---------|---------------|----------------|
| `<h1>` | **100%** | Main topic identifier |
| `<h2>` | **80-100%** | Topic clustering |
| `<h3>` | **60-80%** | Sub-topic detail |
| `<main>` | **100%** | Primary content landmark |
| `<article>` | **80-100%** | Self-contained unit (dễ parse; "AI extracts standalone" = hypothesis) |
| `<section>` | **60-100%** | Topic clustering |
| `<header>/<footer>` | **5-10%** | Boilerplate |
| `<nav>` | **5-10%** | Site structure only |
| `<aside>` | **20-40%** | Supplementary (không phải primary) |
| `<strong>/<em>` | **60-80%** | Semantic emphasis (accessibility; ranking/citation boost = hypothesis) |
| `<time>` | High | Machine-readable timestamp |
| `<figure>/<figcaption>` | **60-80%** | Image context |

### 3. Golden Rules

**Rule 1: Only 1 `<h1>` per page**
```html
✅ <h1>Dịch Vụ SEO Chuyên Nghiệp</h1>
❌ <h1>SEO</h1> ... <h1>Services</h1>
```

**Rule 2: Never skip heading levels**
```html
✅ H1 → H2 → H3 → H4
❌ H1 → H3 (skipped H2!)
❌ H1 → H4 (skipped H2, H3!)
```

**Rule 3: Only 1 `<main>` per page**
```html
✅ <body><header>...</header><main>...</main><footer>...</footer></body>
❌ <body><main>Part 1</main><main>Part 2</main></body>
```

**Rule 4: `<article>` = Self-contained, can be republished**
- Blog post ✅
- Service card ✅
- Case study ✅
- Single FAQ question (maybe)

**Rule 5: `<section>` = Thematic grouping, needs context**
- Services section (groups multiple articles)
- Process section (groups steps)
- Testimonials section

**Rule 6: Use `<strong>/<em>` not `<b>/<i>`**
```html
✅ <p>Công ty có <strong>10+ năm</strong> kinh nghiệm</p>
❌ <p>Công ty có <b>10+ năm</b> kinh nghiệm</p>
```

## Quick Reference

### Standard Service Page Structure

```html
<body>
  <header>
    <nav aria-label="Primary">...</nav>
  </header>
  
  <main>
    <article>
      <header>
        <h1>Dịch Vụ SEO Chuyên Nghiệp</h1>
      </header>
      
      <section id="benefits">
        <h2>Lợi Ích</h2>
        <section><h3>Tăng Traffic</h3>...</section>
        <section><h3>Brand Authority</h3>...</section>
      </section>
      
      <section id="services">
        <h2>Dịch Vụ</h2>
        <article><h3>SEO Audit</h3>...</article>
        <article><h3>Link Building</h3>...</article>
      </section>
      
      <section id="process">
        <h2>Quy Trình</h2>
        <section><h3>Bước 1</h3>...</section>
        <section><h3>Bước 2</h3>...</section>
      </section>
      
      <footer>
        <time datetime="2025-12-14">14/12/2025</time>
      </footer>
    </article>
  </main>
  
  <aside>
    <h2>Related Resources</h2>
  </aside>
  
  <footer>© 2025</footer>
</body>
```

### Google/AI Understanding of Structure

(% = heuristic biên tập GTV, xem re-label note mục 2)

```
Page Structure (mental model — landmarks):
├─ HEADER (boilerplate, weight 5-10%)
├─ MAIN (primary content, weight 100%)
│  └─ ARTICLE (self-contained)
│     ├─ SECTION: Benefits (H2) - Centerpiece
│     │  └─ SECTION: Individual benefits (H3)
│     ├─ SECTION: Services (H2) - Centerpiece
│     │  └─ ARTICLE: Individual services (H3)
│     ├─ SECTION: Process (H2) - Supporting
│     │  └─ SECTION: Steps (H3)
│     └─ FOOTER: Metadata
├─ ASIDE (optional, weight 20-40%)
└─ FOOTER (boilerplate, weight 5-10%)
```

## Related References

For detailed implementation guides, see:
- `references/semantic-elements-guide.md` - Chi tiết từng element
- `references/heading-hierarchy.md` - Hướng dẫn heading structure
- `references/ai-optimization.md` - Tối ưu cho LLM citations

## Checklist

### ✅ Heading Structure
- [ ] 1 H1 duy nhất, ở trên cùng
- [ ] H1 chứa keyword chính
- [ ] H2 = main topics (3-5 per page)
- [ ] H3 = details (2-3 per H2)
- [ ] Không skip heading levels

### ✅ Semantic HTML
- [ ] Dùng `<main>` cho primary content
- [ ] Dùng `<article>` cho self-contained content
- [ ] Dùng `<section>` cho thematic grouping
- [ ] `<header>/<footer>` cho boilerplate
- [ ] Replace `<div>` với semantic tags

### ✅ AI Optimization
- [ ] Clear heading hierarchy
- [ ] `<article>` blocks có thể extract riêng
- [ ] `<time>` cho dates
- [ ] `<strong>` cho key terms
- [ ] `<figure>/<figcaption>` cho images
- [ ] Schema.org JSON-LD markup

## Key Insight

> **John Mueller (Google):** "Semantic HTML helps understand a page, but it's NOT a direct ranking factor. Google treats `<section>`, `<article>`, and `<div>` the SAME way. What matters is CLEAR STRUCTURE."

**Tuy nhiên:** Semantic HTML giúp AI/LLMs hiểu content tốt hơn → 90% ChatGPT citations từ well-structured pages.

---

## Centerpiece Extraction Hygiene — flow liền mạch (bổ sung 16/07/2026)

Máy trích **centerpiece annotation** chủ yếu từ phần mở đầu main content — và đọc content theo **chuỗi block liền mạch** (leak `GoodocSemanticLabel`: `Flow`/`FlowThread` — "indexing may want to deal with the FlowThreads one after the other"; web-side: chunk tree US9069855B2 merge node "gần nhau + tương thích"). Block lạ chen giữa làm gãy flow — ví dụ từ tài liệu DOJ theo bài SEL Koray: chuỗi share buttons "FacebookEmailTwitterGoogle+…" chen giữa câu mở đầu khiến centerpiece bị trích thành rác ("Every Contextless Word cause to lose Relevance"; con số ~400 ký tự = single-source, cơ chế flow thì verified).

**Rules:**
1. ~400 ký tự đầu sau H1 = **một flow liền mạch trong DOM** — không share buttons, newsletter box, related-inject, quảng cáo chen giữa.
2. Share/social/inject đặt **ngoài `<article>`** hoặc sau đoạn mở đầu; boilerplate đứng ngoài main content flow (máy detect boilerplate bằng pattern lặp cross-page — Splitt).
3. Widget bên thứ ba (chat, popup mount point) không mount vào giữa `<main>`.
4. **Test:** view-source (không phải DevTools đã render), đọc từ H1 — 400 ký tự tiếp theo có từ nào "contextless" không?

## HTML Budget (bổ sung 16/07/2026)

Google hạ giới hạn HTML **2MB**/file (kèm deindexing diện rộng sau core update 12/2025) — HTML size giờ là hard gate, không chỉ hygiene. Kết hợp counter-signal sẵn có (catalog render thành nghìn heading): giữ DOM gọn vì [[Cost of Retrieval]] — leak cho thấy Google truncate document + predict quality từ initial signals; những gì quan trọng phải xuất hiện SỚM trong HTML.

## DOM order = Visual order + Adjacency (grounding LAMPRET, bổ sung 16/07/2026)

Patent US12393768B2 (LAMPRET, granted 08/2025) cho các rule cấu trúc một cơ chế cụ thể: máy cắt trang thành block (14 loại: header/paragraph/list/table/image/caption…), **sort theo trục Y rồi X**, và được train chuyên biệt để phát hiện **block sai thứ tự** (block-ordering prediction — objective quan trọng nhất theo ablation); quan hệ **kề nhau** giữa block được embed riêng (block local connections).

- **DOM order = visual order** — không dùng CSS (order/flex-direction/absolute) đảo thứ tự đọc.
- **Caption KỀ ảnh** (`<figure><img><figcaption>`), nhãn kề số liệu — adjacency mang nghĩa.
- **Block thuần loại**: bảng = `<table>` thật (leak Goodoc annotate bảng tới từng cell), enumeration = `<ol>`, heading = thẻ heading thật (không `<strong>` giả heading — tokenizer gán sai block type).
- **`<body>` vs `<main>` vs `<article>` vs `<section>` — test tự-đứng:** `<body>` = mọi thứ render (không mang nghĩa cấu trúc); `<main>` = landmark vị trí nội dung chính CỦA TRANG (1/trang, loại boilerplate); `<article>` = đơn vị **tự đứng** — cắt khỏi trang vẫn trọn nghĩa (bài viết, product card, review, entity card — lồng nhau được); `<section>` = chương/mục theo chủ đề của một tổng thể, không tự đứng, cần heading. Trang dịch vụ: cả bài = 1 `<article>` trong `<main>`; "Lợi ích"/"Quy trình" = `<section>` bên trong; mỗi card dịch vụ con/review = `<article>` lồng. Ranh giới `<article>` = tín hiệu self-contained chunk (Mueller caveat giữ nguyên: không phải ranking factor trực tiếp — giá trị là ranh giới chunk rõ cho máy parse).

## Verbalization & Rendering Notes (bổ sung 16/07/2026)

- **Verbalization rule:** thông tin quan trọng chỉ tồn tại trong pixel/JS/canvas (số trong ảnh, kết quả calculator, giá trong banner) phải có **bản HTML text tương đương** — máy OCR được nhưng markup thật vẫn là nguồn chính (case CellphoneS: quy trình trong ảnh banner không thay được `<ol>`).
- **Rendering (Splitt first-hand, Duda 2021):** rendering là async — metadata quan trọng (title/canonical/schema/structured data) đặt trong **initial HTML** được nhặt ngay sau crawl, và phải **nhất quán pre/post-render** (JS đổi title/canonical = "layer of chaos"); mọi `<img>` có width/height (WRS không fetch ảnh khi có dimensions); JS tách bundle **ổn định/hay đổi** để crawler cache được; analytics/fonts bị WRS skip — không cần tối ưu cho rendering; KHÔNG nạp content chính bằng JS-on-click (không index).

---

## Tabs vs Accordion vs Nội dung ẩn (Mobile-first) — 09/07/2026 (rev 2)

Fact-check myth "Google đọc accordion nhưng không đọc tab" / "`display:none` bị bỏ qua" (phát sinh khi review CareerViet + audit Rowabi/Indochinalight PDP). **Tách 2 TRỤC độc lập — gộp chúng là gốc rễ mọi hiểu nhầm:**

**TRỤC 1 — Có được INDEX không?** → quyết định bởi *nội dung có nằm trong DOM đã render không*, KHÔNG bởi tab-hay-accordion.
- Nằm sẵn trong HTML/DOM (kể cả `display:none`) → **index đủ, full weight**. Nguồn: Illyes 2016 *"content hidden for UX should have full weight"*; Google MFI Best Practices *khuyến nghị* "moving content into accordions or tabs to save space"; Google nhiều lần: `display:none` trong tab/accordion **không bị phạt** ở mobile-first; Mueller đính chính "myth of hidden tab content" (SEJ).
- Click-mới-nạp-bằng-JS (XHR/inject on click) → **KHÔNG index**. Đây mới là lỗi thật, dính cả tab lẫn accordion (Fresh Egg/Google: content revealed by JS không được index). Test: fetch HTML đầu (View Source/curl) + rendered HTML trong URL Inspection — content có mặt chưa.
- ⟹ `display:none` KHÔNG phải thủ phạm; thủ phạm là **JS-reveal-on-click**.

**TRỤC 2 — Có thể là CENTERPIECE không (visual prominence)?** → quyết định bởi *có hiển thị mặc định (được vẽ ra) không*.
- Ẩn mặc định — dù tab `display:none` HAY accordion `height:0`/collapse — đều **visual weight thấp, không thể là Centerpiece** (mô hình layout-aware đọc theo viewport render). Cơ chế CSS không đổi điều này → 2 dạng **tương đương** trên trục prominence.

**Bảng quyết định:**

| Kiểu dựng | Index? | Centerpiece-able? | Heading thật? | Mobile UX |
|---|---|---|---|---|
| `<section>` luôn hiển thị + nav = anchor jump-link | ✅ | ✅ | ✅ | ✅ **tốt nhất** |
| Tab/Accordion, content **nằm sẵn DOM** (display:none / collapse) | ✅ full weight | ❌ (ẩn mặc định) | tùy code | 🟡 tab khó dùng mobile |
| Tab/Accordion **JS nạp khi click** | ❌ | ❌ | — | — **tránh** |

**Thứ tự ưu tiên khi build:**
1. 🥇 Content quan trọng (spec/E-A-V, FAQ, answer chunk, thông tin định nghĩa "trang nói về gì") → **luôn in-flow**, mỗi cụm `<section>` + `<h2>/<h3>` thật, nav = anchor jump-link → thắng cả 2 trục.
2. 🥈 Bắt buộc gom gọn (mobile) → accordion/tab với content **sẵn trong DOM** (index đủ) — nhưng đừng nhét thông tin quyết định vào đây (không là Centerpiece).
3. ❌ Tránh: tab/accordion nạp content bằng JS khi click.

**Heading thật, không `<strong>`:** tab-nav/accordion-header hay bị code thành `<strong>`/`<div>` → mất tầng heading. Mỗi tab/panel = `<section>` có `<h2>/<h3>` thật; tab-nav chỉ là anchor jump-link.

**Kỹ thuật:** `<details>/<summary>` = accordion mà content vẫn trong DOM (index đủ); `hidden="until-found"` (Chromium) cho find-in-page/scroll-to-text tự mở nội dung ẩn. (Nguồn gốc myth: thời desktop-first trước 2018 nội dung ẩn bị discounted — hết hiệu lực từ khi mobile-first.)

**⚠️ Đính chính myth (đừng lặp):** "`display:none` bị Google deweight/bỏ qua" = **SAI** — display:none nằm trong DOM vẫn full-weight. Đừng nhầm `display:none` (OK cho index) với **JS-reveal-on-click** (cái thật sự không index).

**Ứng dụng:** mobile parity — SEO text/FAQ/taxonomy THU GỌN bằng accordion thay vì cắt bỏ; centerpiece + attribute quyết định (giá, lương, CTA info) phải visible mặc định.

---

## Heading Patterns — E-commerce VN (bổ sung 07/2026, benchmark CellphoneS + TGDĐ)

Verified qua crawl heading structure 6 URL (homepage, PLP tổng, thu-cũ ×2 site):

1. **Homepage: H2 = tên entity danh mục.** CellphoneS homepage dùng chuỗi H2 sạch: "Điện thoại" → "Máy tính bảng" → "Laptop" → … → "Hàng cũ". KHÔNG đặt adjective marketing vào heading ("Laptop chất lượng", "PC đỉnh cao" ❌) — adjective xuống sub-line; heading phải match query/entity.
2. **PLP tổng (category hub): taxonomy H2 đa trục.** CellphoneS /mobile: H2 "Phân loại theo tính năng" (H3 Feature phone/Smartphone) → H2 "theo hệ điều hành" (H3 Android/iOS) → H2 "theo nhu cầu" (H3 Gaming/Chụp ảnh/AI/Pin trâu/5G/Gập) → H2 "Các thương hiệu" (H3 per brand) → H2 "Kinh nghiệm chọn mua" (H3 per tiêu chí) → H2 "Mua ở đâu". Mỗi H3 = 1 entity con, link xuống PLP tương ứng (hub→spoke).
3. **Service page (thu cũ): definition-first + process list.** H2 "X là gì?" với định nghĩa trong `<blockquote>` → H2 quy trình với `<ol>` HTML thật (không chỉ text trong ảnh banner — OCR đọc được nhưng không thay được markup) → H3 per loại sản phẩm/brand có internal link sang spoke URL.
4. **Card title = heading render thật.** TGDĐ dùng H3 = tên sản phẩm trên card listing. Card nên là `<article>` với heading cấp nhất quán; không nhảy cấp; 1 H1/trang.
5. **Facet definition trong UI.** Chip phân loại theo nhu cầu kèm tooltip định nghĩa spec tối thiểu (TGDĐ) — điều kiện membership của taxonomy hiển thị cho cả user lẫn máy.
6. **Zone mapping cho e-commerce:** `<main>` duy nhất; mỗi section danh mục = `<section>` có heading; product card = `<article>`; carousel cá nhân hoá + tin tức = `<aside>`; DOM order = visual order.

---

## Koray Live-Site Markup Patterns (bổ sung 07/2026 — sutliffstout · morethanpanel · oscarwylee)

Verified qua crawl HTML thô 9 URL (mobile UA) + đối chiếu ranking Ahrefs:

1. **Question heading đủ 6 tầng.** Cây heading dùng H1→H5 CÓ NGHĨA: H2 câu hỏi đại diện → H3 câu hỏi phụ → H4/H5 micro-template lặp per entity (injury nào cũng đúng bộ Common Symptoms / Settlement Value Factors / Required Documentation). Đừng dừng ở H2-H3 khi content có chiều sâu attribute.
2. **Definition trong `<blockquote>`.** MoreThanPanel dùng 11 blockquote/trang cho các đoạn định nghĩa — markup tách "câu trả lời tuyệt đối" khỏi văn xuôi (answer chunk trích xuất được).
3. **Zone mapping money page dày:** sutliffstout homepage `main=1, section=16, article=22, aside=5` — mỗi review, mỗi injury card là `<article>` tự đứng; sidebar/CTA phụ vào `<aside>`. So sánh nhiều chiều dùng `<table>` thật (trang rideshare: 26 table).
4. **`<ol>` cho enumeration có thứ tự.** Oscar Wylee nhét 12-14 ordered list trong SEO text PLP (materials 1-7, bước chọn kính) — enumeration = ol, không phải ul, khi thứ tự/số đếm mang nghĩa.
5. **Schema graph theo archetype:** legal YMYL = `LegalService + City + GeoCoordinates + Person(per attorney) + FAQPage + HowTo + Speakable + AggregateRating`; service-commerce = `Product + AggregateOffer + AggregateRating + Review + FAQPage + BreadcrumbList`; PLP oscarwylee chỉ có `WebSite` (gap của họ — đừng bắt chước, PLP nên có `ItemList/CollectionPage`).
6. **Counter-signal:** đừng render catalog thành heading (morethanpanel `/pricing`: 4.355 H5 + `noindex`) — item catalog thuộc về `<table>`/`<li>`, heading chỉ dành cho node có nghĩa trong content tree.
