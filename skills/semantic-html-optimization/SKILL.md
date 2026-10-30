---
name: semantic-html-optimization
description: "Semantic HTML cho SEO và AI: dựng template trang dịch vụ, landing; audit cấu trúc HTML theo mẫu template; sửa trên site WordPress đang chạy (main, article, aside, time, heading giả, b/i). Dùng khi tạo template, audit HTML hoặc sửa semantic HTML hàng loạt."
metadata:
  version: "1.3"
---

# Semantic HTML Optimization

Optimize HTML structure for SEO and AI discoverability. Semantic HTML là **retrieval hygiene** (máy parse đúng ranh giới chunk, landmark, thứ tự đọc) — không có nghiên cứu nào gắn một con số citation với semantic HTML.

## Overview

Skill này cung cấp kiến thức về tối ưu Semantic HTML cho SEO và AI discoverability. Semantic HTML không phải là ranking factor trực tiếp, nhưng giúp Google và LLMs (ChatGPT, Claude, Perplexity) hiểu cấu trúc và ý nghĩa của content.

**Core Insight (sửa 29/08/2026 — gỡ claim "90% ChatGPT citations" không nguồn):** giá trị chắc chắn của semantic HTML = accessibility, parsing robustness, logical landmarks, ranh giới chunk rõ cho máy cắt passage, maintainability. **Cái làm nên AI citation là kiến trúc passage bên trong HTML** (câu đầu = answer, chunk tự đứng, heading = câu hỏi thật, facts kiểm chứng — AX1-AX6 trong `sop/08-onpage-checklist.md`, GE-16…GE-27 trong `sop/06-self-checklist/tier-1-geo.md`; skill vận hành: `geo-content-optimization`). HTML tốt là điều kiện cần để passage đó được máy đọc đúng, không phải nguyên nhân được cite. Google official: không có yêu cầu HTML/markup đặc biệt cho AI features (developers.google.com/search/docs/fundamentals/ai-optimization-guide).

🔴 **Schema ≠ AI-citation lever.** Causal test DiD Ahrefs 1.885 trang (05/2026): thêm JSON-LD KHÔNG tăng AI citation (AI Mode +2,4% · ChatGPT +2,2% ≈ 0). Schema vẫn đáng làm cho **rich results / entity (Knowledge Graph) / rendering** — việc của `schema-markup-generator` (xem giới hạn ghi ngay đầu skill đó), không tính điểm GEO. FAQ rich result đã chấm dứt 07/05/2026 → FAQ **content** trên trang vẫn giữ (answer-first 40-60 từ), FAQPage schema không còn lý do citation lẫn rich result.

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
6. Sửa semantic HTML trên site WordPress đang chạy: theme và heading giả trong bài (`references/ap-site-wordpress.md`)

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
- `references/ap-site-wordpress.md` - Audit theo mẫu template, sửa theme, heading giả trong bài, cache sau khi ghi, phối hợp lane
- `references/ap-site-woocommerce.md` - Site WooCommerce hoặc theme riêng: phạm vi đủ template, số đo html-validate và `deep_audit.py`, 24 mẫu sửa (PDP, giá, lưới, so sánh, giỏ, thanh toán, phân trang, mô tả danh mục), bẫy CSS và object cache, báo cáo có ảnh vị trí

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'curl,firecrawl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Sau đó rà theo mục Checklist bên dưới.

### Nhánh site WordPress đang chạy

Dùng khi sửa trên site có quyền server. Đọc `references/ap-site-wordpress.md` trước lệnh đầu tiên. Site WooCommerce hoặc theme riêng: đọc thêm `references/ap-site-woocommerce.md`.

1. Audit chỉ đọc: `python3 -I skills/semantic-html-optimization/scripts/semantic_audit.py --base https://<domain> chon.tsv <thư mục html> audit_truoc.csv`. Audit sâu và số đo trước/sau: `scripts/deep_audit.py` và `scripts/html_validate.sh` (`ap-site-woocommerce.md` mục 2). Phạm vi gồm mọi template, kể cả PDP, bài, chuyên mục blog, giỏ, thanh toán, và khối nội dung trong template (mô tả danh mục, mô tả PDP, FAQ).
2. Tìm gốc lỗi trong template, đưa câu cần quyết lên trang duyệt.
3. Sửa theme qua staging (`wp-staging-deploy`), đo trước và sau ở 1366 px và 390 px.
4. Heading giả: quét sau `wpautop` bằng `scripts/scan_heading_gia.php`, Jev `semantic-role`, ghi bằng `wp-content-review-apply`.
5. Sau khi ghi: tầng cache, regen CSS gọn cho path đổi DOM, đo lại bằng `semantic_audit.py`.

### Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code | `semantic_audit.py`, `deep_audit.py`, `html_validate.sh`, `scan_heading_gia.php`, đếm nhảy cấp, so trước và sau | Dùng. Mọi số đếm lấy từ script |
| Jev | Task `semantic-role`: đoạn chữ đậm đứng riêng là heading, bước, câu dẫn hay nhãn bảng. Task `ui-visual` so ảnh trước và sau | Dùng. Gán nhãn tay 20 mẫu trước khi xem điểm. Ngưỡng 0,7 và 0,3 ở `references/ap-site-wordpress.md` mục 3 |
| EmbeddingGemma 2 | Gom chữ đậm lặp giữa các bài | Không dùng. Đếm chữ trùng nguyên văn đủ để tách phần layout |
| Claude | Đọc đoạn Jev cho 0,3–0,69, chọn cấp heading, quyết luật giữ, đọc ảnh Jev gắn cờ | Dùng |

### Tự phản biện trước khi trình

Chấm plan sửa và lô ops theo checklist dưới. Mục chưa đạt thì sửa, hoặc ghi lý do bỏ.

Bản tốt nhất phải có:
- [ ] Gốc lỗi nằm ở template thì sửa template, không sửa từng trang. Nguồn lỗi: audit đầu 27/10/2026 đề xuất sửa theo trang, agent kiểm lại thấy 20 file theme phủ cả site.
- [ ] Heading giả quét sau `wpautop`, không quét chuỗi thô. Nguồn lỗi: lần quét đầu sót 142 đoạn ở 48 bài.
- [ ] Rubric Jev có 20 mẫu gán tay trước khi xem điểm, và đoạn 0,3–0,69 có Claude đọc. Nguồn lỗi: người duyệt nhắc dùng Jev cho audit, 27/10/2026 17:13.
- [ ] Shim CSS đo trên staging trước khi phát hành, 0 phần tử lệch quá 1 px. Nguồn lỗi: shim bản đề xuất đổi chữ đậm 800 thành 700 và lệch chiều cao 15–35 px.
- [ ] Danh sách path đổi DOM đã gửi cho bước regen CSS gọn và purge CDN. Nguồn lỗi: đợt 27/10/2026 phải phối hợp tay với lane tốc độ, chuỗi ghi dừng ở bước CDN.
- [ ] Audit phủ mọi template và khối nội dung trong template (mô tả danh mục, mô tả PDP, FAQ). Mỗi việc trình kèm ảnh vị trí trên giao diện và code trước/sau. Nguồn lỗi: site bán lẻ mẫu 29/10/2026, lượt đầu sót PDP, bài và chuyên mục blog. Người duyệt nhắc lúc 23:00 và 23:20, và hỏi lúc 22:07 vì chưa hình dung được chỗ chèn thẻ.

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

### ✅ AI-readable HTML (retrieval hygiene — điều kiện cần, không phải lever citation)
- [ ] Clear heading hierarchy — heading tổ tiên có nghĩa (không "Tổng quan"/"Kết luận" rỗng): máy gắn heading cha vào chunk như metadata (`includeAncestorHeadings`, Google Cloud docs)
- [ ] `<article>` blocks có thể extract riêng (ranh giới chunk tự đứng)
- [ ] `<time>` cho dates
- [ ] `<strong>` cho key terms (accessibility/semantic emphasis — không có evidence tăng citation)
- [ ] `<figure>/<figcaption>` cho images
- [ ] Passage bên trong đã qua G-BÀI (GE-16…GE-19) — việc của content, HTML chỉ giữ ranh giới

### 🟡 Rich results / entity — KHÔNG phải citation lever (làm riêng, không tính điểm GEO)
- [ ] Schema.org JSON-LD theo page type → `schema-markup-generator` (Organization/Person + `sameAs` cho Entity Home; Product/Article/ItemList cho rich results). Causal DiD Ahrefs 1.885 trang 05/2026: schema ≈ 0 tác động AI citation.
- [ ] KHÔNG thêm FAQPage schema để "được AI cite" — FAQ rich result chấm dứt 07/05/2026; FAQ content answer-first trên trang vẫn giữ.

## Key Insight

> **John Mueller (Google):** "Semantic HTML helps understand a page, but it's NOT a direct ranking factor. Google treats `<section>`, `<article>`, and `<div>` the SAME way. What matters is CLEAR STRUCTURE."

**Tuy nhiên:** Semantic HTML giúp máy cắt passage đúng ranh giới và giữ context (heading tổ tiên đi kèm chunk) — đó là giá trị thật, đo được ở tầng parsing. Claim "90% ChatGPT citations từ well-structured pages" từng nằm ở đây **không có nguồn** và đã gỡ 29/08/2026; số citation có nguồn nằm ở `geo-content-optimization/references/geo-levers-map.md` §5.

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

Fact-check myth "Google đọc accordion nhưng không đọc tab" / "`display:none` bị bỏ qua" (phát sinh khi review site khách mẫu và audit 2 trang sản phẩm thương mại điện tử, 07/2026). **Tách 2 TRỤC độc lập — gộp chúng là gốc rễ mọi hiểu nhầm:**

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

---

## Changelog

- **v1.3 (2026-10-30):** nhánh WooCommerce và theme riêng: `references/ap-site-woocommerce.md` (phạm vi đủ template, số đo, 24 mẫu sửa, 12 bẫy, việc giao team, báo cáo có ảnh vị trí). Script mới: `scripts/deep_audit.py` (hơn 60 chỉ số landmark, heading, form, nút, bảng, ngày, breadcrumb; chạy bằng `-B` vì bs4 ở user site-packages) kèm `tests/test_deep_audit.py` 3 ca; `scripts/html_validate.sh` + `htmlvalidate-config.json` + `hv_strip.py` (ghi JSON ra file tạm vì Node cắt stdout qua pipe). Nhánh WordPress bước 1 thêm audit sâu và phạm vi. Tự phản biện thêm 1 mục. Nguồn: site bán lẻ mẫu 29–30/10/2026, 94 việc qua 8 lane, html-validate toàn site 13.761 → 5.912, 0 Fatal mới, 0 mã 5xx.
- **v1.2 (2026-10-27):** nhánh site WordPress đang chạy. `references/ap-site-wordpress.md`; `scripts/semantic_audit.py` (audit theo mẫu template, test 3 ca), `scripts/scan_heading_gia.php` (quét heading giả sau `wpautop`); Phân việc model với Jev `semantic-role`; Tự phản biện 5 mục. Description viết lại tiếng Việt. Nguồn: đợt semantic HTML site agency mẫu 27/10/2026 (95 URL audit, 17 file theme, 436 op trên 109 bài, verify lệch 0). Phần đề xuất `section`/`article` cho trang core và đổi `b`/`i` ở template chưa xong lúc ghi bản này.
- **v1.1 (2026-08-29):** gỡ claim không nguồn "90% ChatGPT citations từ well-structured pages" (5 chỗ: SKILL.md ×3, `references/heading-hierarchy.md`, `references/ai-optimization.md`); tách Schema.org/FAQ schema ra khỏi danh sách "LLM ưu tiên cite" thành block **"Rich results / entity — KHÔNG phải citation lever"** trỏ `schema-markup-generator` (causal DiD Ahrefs 1.885 trang 05/2026 ≈ 0; FAQ rich result chấm dứt 07/05/2026); Core Insight viết lại: semantic HTML = retrieval hygiene, citation = kiến trúc passage (AX1-AX6 / GE-16…GE-27); thêm rule heading tổ tiên có nghĩa (`includeAncestorHeadings`). Nguồn: FINDINGS 22/08/2026 §6b + `tier-1-geo.md` v2.0 guardrail 2. Vincent duyệt 29/08.
- **v1.0 (07/2026):** bản gốc + các bổ sung 09-16/07/2026 (centerpiece hygiene, HTML budget, LAMPRET, tabs/accordion, heading patterns e-commerce VN, Koray live-site).
