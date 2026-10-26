---
name: visual-semantic-seo
description: "Thiết kế, audit và so sánh Visual Semantic SEO: page layout, visual hierarchy, centerpiece, above-the-fold, component mapping, entity cards, image semantics, FAQ/tabs, trust/pricing blocks, PDP, service page, local page. Use when: 'visual semantic', 'page layout SEO', 'wireframe', 'centerpiece', 'audit layout [URL]'."
---

# Visual Semantic SEO (v3.7.1)

Optimize content layout, visual hierarchy, website functions, image-level semantics, and patterned visual elements following Koray Tuğberk's framework, verified Google patents, and Content Warehouse API leak insights.

> **v3.0 fact-check note:** mọi patent/leak citation trong skill này đã được verify lại 2026-07-02 trên nguồn gốc (patents.google.com + hexdocs). Chi tiết + verdicts: wiki nội bộ «research-2026-07-visual-semantics-verification» (ngoài repo, hỏi Lead/Vincent). KHÔNG cite US8949242B1 làm "centerpiece patent" (misattribution); KHÔNG dùng tên `vboostFactor` (không tồn tại — đúng là `goldmineNavboostFactor`).

---

## Core Principle — Koray's 4 Pillars (2026)

**"Layout is a signal of the two things Google cares about most: the human effort behind a page, and the page's function."** — Koray

| Pillar | Meaning |
|---|---|
| **Visualization** | Visual hierarchy + segmentation cho MỌI attribute của entity |
| **Verbalization** | Word order khớp targeted query; definitive answer ≤120 từ (conditional — xem Centerpiece Dial) |
| **Content Contextualization** | Mọi block bám macro context; không block mồ côi |
| **Commercialization** | Pricing + business signals rõ; "triple-connection: context – service – fee" |

### Topical Authority Formula v3 + Decision-Tree Gate (v3.6)

`((Historical Data × Topical Coverage) ÷ Cost of Retrieval) × Right Visual Annotations`

Right Visual Annotations là **hệ số nhân có thể về 0** (Koray SEL 07/2026 — label: framework extension, không phải công thức Google công bố). Ranking vận hành như decision tree: sai centerpiece/annotation ở vòng đầu → các hệ đánh giá đắt tiền phía sau không bao giờ chạy. Đọc chính xác Nayak (DOJ): hệ đắt (RankBrain-like) chỉ chạy trên **top ~20-30 theo base signals** — KHÔNG phải "cần ≥1 click". Hard gates 2025-26: HTML limit **2MB** + deindexing diện rộng 12/2025; leak: truncate + predict quality từ initial signals. → Thứ tự can thiệp: (1) annotation/centerpiece → (2) CoR → (3) Coverage × HD.

Google evaluates through (evidence verified 2026-07, cập nhật v3.6):
- **Visual gap segmentation** → US7421651B2: segment trang theo white space khi RENDER, suy ra hierarchy
- **Typography as model input** → US12393768B2 (LAMPRET): font-size (0-10) + bold/italic/underline per block
- **Centerpiece annotation** → main content vs boilerplate (Martin Splitt statements + leak + QRG — KHÔNG phải US8949242B1)
- **Link visual location** → US9053177B1 (sitelinks) + US7716225B1 (Reasonable Surfer: prominence + topical cluster match)
- **Image understanding from pixels** → US11907337B2 + leak `ImageData` (OCR, entity detection, `h2i`/`h2c` hover signals)
- **Function Validation** → interactive elements match intent
- **Block Chunking** → self-contained chunks ("bytes become vectors" — layout quyết định vectorization)
- **Clutter & Effort** → leak `clutterScore` (phạt nhiễu site-level) + `contentEffort` (LLM ước lượng effort)
- **Goldmine title factors** → `goldmineReadabilityScore`, `goldmineHeadingFactor`, `goldmineSitenameFactor`, `goldmineSalientTermFactor`, `goldmineNavboostFactor` (title/snippet selection scoring)
- **Pseudo-rendering → chunk tree** → US9069855B2 (Zunger 2015): 1-pass render → quasi-DOM → merge node "gần nhau + tương thích" thành semantically distinct regions; hạ boilerplate. Flow liền mạch: leak `GoodocSemanticLabel` `Flow`/`FlowThread` (scope OCR/PDF — web-side analogy)
- **SERP theo attribute + category** → US10445328B2 (entity type → property schema → presentation: Location→map, số đo→chart, năm→timeline, gallery; "best" = soft property chấm co-occurrence) + US8498984B1 (điểm cấp category bằng position-CTR curve, cap per loại — cùng họ Twiddler `max_total`, nguồn 2018 leak KHÔNG phải DOJ)
- **Function là consequence thật** → US12536233B1 (granted 01/2026): landing page score vượt ngưỡng → chèn link AI-generated page; ví dụ đích danh: trang "does not have a filter for products"

---

## Content Weight Distribution

```
Centerpiece (Main Topic)     = 100% weight
Supporting Content           = 60-80% weight
Sidebar (Aside)              = 20-40% weight
Boilerplate (Header/Footer)  = 5-10% weight
```

For **hybrid pages**, multiple centerpieces may stack with supporting blocks between them. See `references/multi-layer-centerpiece.md`.

---

## PROCESS — 8 bước triển khai (v3.7)

> Bản đầy đủ có RACI + training: wiki nội bộ «07-visual-semantic» (ngoài repo, hỏi Lead/Vincent) (v2.0 — đã renumber 8 bước) + deep-dive trực quan: `sop/07-visual-semantic-deep-dive.html`. 2 chế độ: **Design-in** (trang mới, Bước 0-8) / **Audit-fix** (trang có sẵn — vào Bước 8, quay lại bước fail). Vị trí pipeline: giữa Layer 2 Outline AM và Layer 4 Onpage (Koray: topical map → document architecture → mockup → Figma). v3.6 thêm Bước 1 + nâng Bước 3; v3.7 nâng Bước 1 thành QDP Gate + output Query Augmentation Map.

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'chrome?,playwright?,firecrawl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

| Bước | Việc | Output |
|---|---|---|
| **0. Input Gate** | Nhận từ Topical Map + Outline AM: entity-attribute, page type, funnel, persona, CSI, kết quả QDP/QDH/QDS. Không có Outline AM → không vào | — |
| **1. Query Augmentation & QDP Gate** *(nâng cấp v3.7)* | (a) Liệt kê biến thể **augmented** của query gốc (experience / local / price / instructional / so sánh…) — soi PAA + `search_model_queries` (ChatGPT DevTools) khi có. (b) **QDP Gate 4 tiêu chí** cho từng biến thể: high demand · different entities · low similarity (WEIGHTED — theo term nặng, không phải string) · has pattern; **≥3/4 → page riêng**, không đạt → QDH (heading) / QDS (sentence) / **component** (table/list/form/calculator/filter). Rubric canonical: `keyword-topic-url-mapping/references/qdp-gate.md`. (c) Map biến thể giữ lại → page type + layout + function (experience→forum subdomain, local→directory/info cards, price→FS paragraph+cards, instructional→guide); prune/merge phần thừa (CoR ↓, PageRank cô đặc). (d) **Weighted-term rule**: term nặng nhất của query = subject của triples + vocabulary chính của heading/annotations (Bendersky/Najork). Grounding: US9916366B1 + Stateful Chat + Query Fan-Out + US6658423B1 | **Query Augmentation Map 4 cột** (augmented queries → visual component → triples S-P-O → named entities) + verdict QDP/QDH/QDS/component per biến thể — template: `references/query-augmentation-map.md` |
| **2. Page Function & Centerpiece** | Chốt function (info/commercial/transactional/mixed); Centerpiece spec 1 câu; mixed intent → liệt kê CẢ 2 bộ elements above-fold; chọn Centerpiece Dial (bảng dưới); **định nghĩa ~400 ký tự đầu sau H1 sẽ nói gì**. *Local (v3.7):* location-service pair quan trọng nhất target từ HOMEPAGE (PageRank + crawl cao nhất); homepage phải có contextual bridges → quality nodes | Function Statement + Centerpiece spec + above-fold element list |
| **3. SERP & Attribute Benchmark** *(nâng cấp v3.6)* | Chụp above-fold top 5-10; ghi block/thứ tự/trust/functions/format thắng; **đọc NGƯỢC SERP features → attribute nào được ưu tiên cho entity type** (US10445328B2: property→map/chart/timeline/gallery) + **category nào thắng SERP** (listicle/PLP/video — US8498984B1); xác định design archetype vertical → match trước, differentiate sau | Bảng benchmark + attribute-priority + archetype notes |
| **4. Block Architecture** | Mỗi attribute = 1 HTML section (hotel-card); thiết kế **entity card skeleton** instantiate ≥3 lần; mỗi block 5 slots (heading + L0 40-75 từ + body + visual + function); zone weights (Centerpiece 100 / Supporting 60-80 / Supplementary 40 / Boilerplate 5-10) + RQ border; **conversion layer** spec (bảng dưới); data-heavy → bảng Attribute\|Value; list >50-100 items → Tiered Prominence | **Block map** (text-level mockup) — hoặc **annotated wireframe HTML** khi user cần bản trình bày/phân tích (Wireframe Mode, `references/wireframe-spec.md`) + component library note |
| **5. Visual Asset Layer** | Mỗi key block 1 visual cạnh text; ảnh độc bản chứa đúng entity, OCR-legible (chữ trong ảnh ≥30px, contrast đủ — benchmark tham khảo); chain Image URL ≤3 từ → Alt = verbalized expansion; featured image alt = short H1; ImageObject + primaryImageOfPage; video companion cho core topics | Visual spec per block |
| **6. Design Implementation** | Typography theo LAMPRET (H1 36px+, size giảm theo cấp); **DOM order = visual order**; caption/nhãn KỀ ảnh/số liệu (block local connections); above-fold identity; semantic HTML thật; không giấu critical info trong tabs; mobile giữ identity | Figma/build khớp block map |
| **7. Technical Verification** | **HTML <2MB** · CLS (dimensions set — WRS không fetch ảnh khi có width/height) · TTFB <2s · **JS bundle tách stable/changing** · metadata (title/canonical/schema) trong initial HTML, nhất quán pre/post-render · clutter check (`clutterScore`) · featured image indexed (`src:`) · JSON-LD đúng page type · mobile = desktop identity | Checklist pass/fail |
| **8. Validation Loop** | **Extraction test: view-source ~400 ký tự đầu sau H1 liền mạch (không share/inject chen)** · Blur Test (desktop + mobile) · effort/replicability review (`contentEffort`) · chunk extraction test (từng H2 tự đứng, trả lời 1 fan-out variant) · function test (mọi function claim đều thật) · SERP/AI check (title rewrite? GSC image data; AIO citations). Fail → quay lại bước đó | Audit report, lặp theo quý |

> Checklist thao tác 24 eval (nhóm A-F, có nhãn nguồn per eval): `sop/07-visual-semantic-deep-dive.html` mục CHECKLIST.

### Centerpiece Dial (rule ≤120 từ là CONDITIONAL — teardown 2026-07)

| Page type | Đoạn sau H1 | Evidence |
|---|---|---|
| Commercial hub | Definition ≤120 từ, answer-first, nén dual-audience | morethanpanel home: 114 từ |
| Transactional spoke | Answer-first + giá bằng text; được phép >120 | morethanpanel/buy-instagram-likes: 245 từ |
| YMYL / service money page | Mini-article: definition → authority → hard stats in-line → benefits enumeration "…are listed below" | sutliffstout home 226 từ, uber 485 từ |

**Hygiene chung mọi dial (v3.6):** ~400 ký tự đầu sau H1 phải là **một flow liền mạch trong DOM** — share buttons/newsletter/related-inject đặt ngoài `<article>` hoặc sau đoạn mở (grounding: leak Goodoc Flow/FlowThread + DOJ share-button example; con số 400 = single-source từ bài SEL Koray, cơ chế flow thì verified). Evidence sức nặng centerpiece: case converter 100k pages — đưa calculator từ cuối trang lên top = +30.5% clicks / +98.6% impressions (số Koray tự công bố; caveat CTR −34%).

### Conversion Layer (lớp riêng, interleave vào content — KHÔNG dồn 1 CTA cuối trang)

| Vertical | Pattern | Evidence |
|---|---|---|
| YMYL / service | **CTA-as-heading**: question H3 + tel: sau MỖI entity card | sutliffstout ×18/×16 |
| E-com / self-serve | Order widget/login form NHÚNG trong card + above-fold | morethanpanel variant cards |

### Entity Card Skeleton ("page as database render")

Đơn vị thiết kế không phải "section" mà là **skeleton attribute cố định × instantiate per entity**. Ví dụ đã đo: sutliffstout 18 injury cards (H3 injury → H4 Symptoms/Settlement Factors/Documentation → H5 Claim Impact/Defense/Legal) + 25 bảng `Attribute|Value` per neighborhood; trang sibling = re-instantiate cùng template với value đổi theo entity context. Case: `wiki/cases/koray-visual-semantics-showcase-2026.md`.

---

## Page Type Selection

Choose the right pattern based on page intent and complexity:

| Page Type | When to Use | Reference File |
|---|---|---|
| Service page | Single-service B2B, lead generation | `service-page-visual-template.md` |
| E-commerce Category (PLP) | Product listing with filters | `ecommerce-page-visual-semantic.md` |
| E-commerce Product (PDP) | Single product detail | `ecommerce-page-visual-semantic.md` |
| Encyclopedia / A-Z list | Reference content, comprehensive listings | `informational-page-visual-semantic.md` |
| How-To / Tutorial | Step-by-step instructional | `informational-page-visual-semantic.md` |
| **Hybrid (e-com + info + service)** | **Homepage hub, multi-intent landing** | **`hybrid-page-pattern.md` (NEW v2.0)** |
| **Local Entity Pages (NEW v3.7)** | **Store/office location page, specialist person page, city/service local landing** | **`local-entity-page-patterns.md`** |

---

## Visual Structure by Page Type

### Service Pages (Single Centerpiece)
```
[HEADER 5-10%] → [HERO: H1+CTA above fold] → [CENTERPIECE 100%: Benefits→Services] → [SUPPORTING 60%: Process→Case Studies] → [FOOTER 5-10%]
```
→ Bản đầy đủ 14 block + bảng dịch pattern thương mại sang dịch vụ: **Service Page Application Playbook (v3.4)** cuối skill.

### E-commerce: Category (PLP)
```
[HEADER 5-10%] → [CENTERPIECE 100%: H1+Filters+Product Grid] → [SUPPORTING 40%: Category SEO text] → [SIDEBAR 30%: Filters] → [FOOTER 5-10%]
```

### E-commerce: Product (PDP)
```
[HEADER 5-10%] → [CENTERPIECE 100%: Image+Info+Add to Cart] → [SUPPORTING 60%: Specs+Reviews] → [SUPPLEMENTARY 40%: Related+Q&A] → [FOOTER 5-10%]
```
→ Chi tiết pattern thương mại cho PDP: **Marketplace PDP Patterns (v3.3)** cuối skill + VN pattern #3 (mobile spec-elevation, sticky buy-bar).

### Informational: Encyclopedia/A-Z
```
[HEADER+Alphabet Nav 10%] → [CENTERPIECE 100%: H1+Stats+Featured] → [MAIN 80%: Category sections] → [SUPPORTING 40%: CTA+Resources] → [SIDEBAR 30%: TOC] → [FOOTER 5-10%]
```

### Informational: How-To/Tutorial
```
[HEADER 5-10%] → [CENTERPIECE 100%: H1+Time+Overview] → [MAIN 100%: Numbered steps] → [SUPPORTING 60%: Troubleshooting] → [SIDEBAR 20%: Progress tracker] → [FOOTER 5-10%]
```

### Hybrid Page (NEW v2.0 — multi-centerpiece pattern)
```
[HEADER 5%] 
→ [CENTERPIECE L1 100%: H1 + Definition + Trust + Inline Action]
→ [TRUST STRIP 5%: Press logos]
→ [SUPPORTING 60%: Multi-source reviews (Video + Customer + Platform)]
→ [LIVE STATS 60%: Real-time counters]
→ [EDUCATIONAL 60%: How-it-works + Steps]
→ [CENTERPIECE L2 100%: Pricing comparison cards]
→ [PRODUCT GRID per Entity 80%: Templated platform sections]
→ [INTERACTIVE FUNCTION 100%: Calculator/Tool]
→ [SUPPORTING 40%: Team + Newsletter]
→ [PQ ENCYCLOPEDIA 60%: 15-20 PQ in tabs (decorative-semantic separated)]
→ [FOOTER 5%]
```

→ Full guide: `references/hybrid-page-pattern.md` (with morethanpanel.com worked example)

---

## Advanced Patterns (NEW v2.0)

These 6 patterns are derived from Koray's event slides + Content Warehouse API leak + reverse-engineering Koray-built sites. Apply when applicable to page type.

### Pattern 1: Multi-Layer Centerpiece
Hybrid pages need 2-3 centerpieces stacked with supporting blocks between them. Single centerpiece is incorrect for homepage hubs and multi-intent landings. → `references/multi-layer-centerpiece.md` (đọc kèm fact-fix v3.0 — file này còn cite US8949242B1 theo cách cũ)

### Pattern 2: Templated Visual Elements
Transformers train trên "patterned data" gồm images, DOM-tree, layout (Koray slide; structure-aware parsing evidence: WebFormer — paper **Meta**, WWW 2022; phía Google: US12393768B2). Repeat the same template ≥3 times across same page type so pattern học được (entity-attribute-value structure). → `references/templated-visual-elements.md` (đọc kèm fact-fix v3.0)

### Pattern 3: Block Chunk Self-Containment
Documents được chunk thành self-contained block units — evidence: **LAMPRET / US12393768B2** (block position + block attributes; "BLK" là ký hiệu trong paper/patent, việc chạy production là interpretation). Each block needs 5 elements: heading + L0 answer + body + visual + functional element. → `references/block-chunk-design.md` (đọc kèm fact-fix v3.0)

### Pattern 4: Dual-Audience Macro-context Reinforcement
Same macro-context, different contextual vector for 2 personas. Reinforces topic 2x without cannibalizing. Used by morethanpanel for "How does SMM Panel Work?" (end user) + "How SMM Panels Work?" (reseller). → `references/dual-audience-macro-context.md`

### Pattern 5: Decorative-Semantic Heading Separation
"FAQ", "Resources", "Learn More" are decorative containers. Real macro-contexts inside should be H2 (cùng cấp), not H3 nested under decorative H2. → `references/decorative-semantic-heading.md`

### Pattern 6: Search Journey Compression
1 URL covers full search journey (Awareness → Decision → Purchase) when DR < 30 or query overlap is high. Cover 7 dimensions of central entity. → `references/search-journey-compression.md`

### Pattern 7: Subdomain Testing — re-evaluation trigger (NEW v3.6)
Khi domain nghi bị đè bởi historical/domain-level signals (không được re-evaluate vì search engine tránh chạy hệ đắt): move content + **functional components** sang subdomain = cho Google lý do reprocess layout/document trên "trang giấy sạch". 3 lớp grounding: case lexinter + Pricelisto (thêm purchase/compare/review functions → thoát HCS-era filter) · Guide chính chủ ("subdomains sometimes treated as separate sites when deemed relevant") · WO2020033805A1 (representation sinh được từ subdomain riêng — ⚠️ application CEASED, design intent). Điều kiện: chỉ khi nghi domain-level suppression + đo trước/sau bằng GSC property riêng; không phải default.

### Pattern 8: Content Type Distribution (NEW v3.6)
Phân phối loại content theo query augmented — 2 trục **factual/opinionated × structured/unstructured** (factual→expertise, opinionated→experience, structured→attributes, unstructured→definitions/processes), thao tác bằng 4 kỹ thuật khớp 4 Pillars: Visualization · Commercialization · Contextualization · Verbalization. 3 component đã thấy chạy thật: **Q&A opinion block** (đổi nền màu tách factual/opinion) · **preceding-question component** (reframe câu hỏi, chuyển dần factual→opinion) · **horizontal tab phân phối internal links** tới related headings (content sẵn trong DOM).

**Forum subdomain route (v3.7):** khi factual/how-to guides "can't exceed thresholds" cho **opinionated/experience query-terms** ("How do I fix…", "What do I do for error code X?") → route sang **forum subdomain + forum structured data** (forum pages index dễ hơn cho opinionated formats). Routing đầy đủ theo query type: experience→forum subdomain · near-me→structured info cards · price→FS-catching paragraph + cards · how-to→informational page; chọn 1-2 template bind nhau theo demand + query network — KHÔNG mở đủ 4 loại cho mọi city/occupation (case Central Europe, SEL local 07/2026).

---

## Supporting Patterns (NEW v2.0)

### Live Function Validators
Live tickers, counters, calculators serve as semantic intent validation. (⚠️ v3.0 fact-fix: mapping cũ sang "vboostFactor" + US20150234930A1 đã bị de-attribute — field không tồn tại, patent là của Ads. Grounding hợp lệ: US7716225B1 model hóa link/function selection probability + leak `contentEffort` — interactive tools là effort signal.) → `references/real-time-function-validators.md` (đọc kèm fact-fix này)

### Trust Stacking Hierarchy
7-layer trust positioning from above-fold to pre-footer. Each layer has specific position requirement. → `references/trust-stacking-hierarchy.md`

### Multi-Tier Pricing Pattern
Pricing card with 4 mandatory elements + Best Offer badge positioning + tier sequencing logic. → `references/multi-tier-pricing-pattern.md`

---

## Website Functions by Intent

> **v3.6 — function giờ có consequence thật:** (1) "misleading functionality" là spam policy chính thức — function giả (nút so sánh không so sánh) = spam; (2) US12536233B1 (granted 01/2026): landing page thiếu function cơ bản là **named trigger** để Google chèn AI-generated page thay thế trải nghiệm — ví dụ nguyên văn patent: trang *"does not have a filter for products"*. Audit function TRƯỚC, text sau.

### Service Pages
- Primary CTA (Request Consultation)
- Contact Form
- Phone/Chat
- Pricing Selection

### E-commerce
- Filter & Sort (Critical)
- Add to Cart (Critical)
- Variant Selection
- Reviews/Ratings
- Compare Products
- Wishlist

### Informational
- Alphabet/Category Navigation (Critical)
- Search Within Content (Critical)
- Filter by Type
- Save/Bookmark Entries
- Compare Entries
- Newsletter Signup
- Quiz/Knowledge Test
- Downloadable Resources

### Hybrid (NEW v2.0)
- Inline Login Form (above-fold)
- Live Notification Widget
- Real-time Counter Bar
- Interactive Price Calculator
- Multi-tab FAQ Encyclopedia
- Persistent Mobile Bottom Nav

---

## Goldmine Title Factor Optimization (v3.0 — renamed từ "RankLab Factor Optimization")

From Content Warehouse API leak (May 2024), module `QualityPreviewRanklabTitle` — các factor chấm **title candidates cho title link/snippet selection** (`goldminePageScore`), KHÔNG phải "final ranking score". Guidance giữ nguyên vì vẫn hợp lý cho heading/title hygiene:

| Factor (tên đúng trong leak) | How to Optimize |
|---|---|
| `goldmineReadabilityScore` | Title candidate dễ đọc: ngắn, S-V-O, không nuke word. Factor này chấm title candidate, không chấm thân bài. Flesch chỉ đo tiếng Anh |
| `goldmineHeadingFactor` + `goldmineHeaderIsH1` | H1 contains exact target query, H2 carries semantic variations, H1 ≤4 entities, no number stuffing; heading phải render thật |
| `goldmineSitenameFactor` | Tên site trong title candidate (dạng "Tiêu đề - Brand"), một tên gọi thống nhất. Factor chấm title candidate, không đếm số lần nhắc brand trong bài |
| `goldmineSalientTermFactor` | Identify 2-3 salient terms per article, repeat strategically across heading + body |
| `goldmineNavboostFactor` | Boost feature signal cho `goldmine_page_score` — hexdocs không có description riêng; "liên quan click signals" là suy luận từ tên Navboost (interpretation). ⚠️ v2.1 ghi sai thành "vboostFactor" — mis-crop từ slide; field đó không tồn tại |
| `goldmineGeometryFactor` + `widthFraction` | Title/heading không tràn width gây truncate khi render |

→ Detailed implementation: `references/ranklab-factors.md` (đọc kèm fact-fix này)

---

## Interaction Signals (⚠️ interpretation — không có nguồn cho con số)

Bảng weight cũ (click 5x, conversion 10x…) KHÔNG tìm được backing trong patent/leak nào — giữ ý niệm định tính: active interactions với functions (click, form fill, filter) validate page function; broken function làm mất chuyển đổi (heuristic thực hành; chưa có patent hay thuộc tính leak nói chức năng hỏng bị trừ điểm. US7716225B1 là patent reasonable surfer về trọng số link theo xác suất click, không nói về chức năng trang; fact-fix 28/09/2026).

**Formula: Visual Semantic (Layout) + Website Function (Interactive) + Block Chunking (Self-Contained Units) + Image-Level Semantics = Semantic Intent Validation**

---

## Image-Level Semantics (NEW v3.0 — nửa còn thiếu của "visual")

Layout là một nửa; nửa kia là **pixels**. Evidence: leak `ImageData` + US11907337B2 + visual search fan-out (Google 09/2025).

| Cơ chế | Field/Nguồn | Rule thực hành |
|---|---|---|
| Máy classify ảnh từ pixels, không cần alt | US11907337B2 (granted 02/2024) | Ảnh phải CHỨA đúng entity — stock generic sai chủ đề = topical noise alt không cứu được |
| Chữ trong ảnh bị OCR đọc | `ocrTaser`, `ocrTextboxes` | Text in-image chính xác, legible; số liệu chính lặp lại trong figcaption/body text |
| Entity trong ảnh map sang KG | `imageRegions`, `multibangKgEntities` | Chủ thể trung tâm rõ, phản ánh trong alt |
| Hover behavior được đo | `h2i`, `h2c`, `clickMagnetScore` | Thumbnail distinctive, không clickbait; ≥1200px cho feature candidates |
| Ảnh đại diện SERP chọn theo prominence + persistence | WO2018097872A1 | Ảnh key: ổn định (không random rotate), prominent, đúng aspect ratio |
| 1 ảnh → nhiều query ngầm | Visual search fan-out (09/2025) | Ảnh giàu chi tiết liên quan (primary + secondary objects đúng chủ đề) |
| Aesthetic/quality scoring | `nimaVq`/`nimaAva` | Ảnh chất lượng cao, đủ sáng, composition sạch |

**Chain on-page (Koray):** Title → URL → Description → **Image URL ≤3 từ** → **Alt = verbalized expansion của Image URL** (không câu hoàn chỉnh, dùng "and" + context terms; core section = alt dài/giàu hơn). Featured image: alt = short H1, đặt ngay cạnh H1, PHẢI indexed (check `src:https://…`). Ảnh độc bản + brand watermark = effort signal (`contentEffort`) + Information Gain. Video companion cho core topics: transcript + chapters + `VideoObject` — YouTube = 18% AIO citations.

---

## Design Mode — dùng skill khi agent BUILD page (NEW v3.0)

Khi được yêu cầu thiết kế/build layout (HTML mockup, wireframe, landing page, Figma spec), skill này là LUẬT thiết kế. Trình tự bắt buộc:

1. **Hỏi/nhận input Bước 0-2** (entity, page type, function, persona; nếu có nhiều query variation → chạy nhanh Bước 1 classification) — thiếu thì hỏi, không giả định.
2. **Xuất Block map trước, HTML sau** — block map theo format: `[BLOCK n | zone weight % | heading (level) | L0 answer | visual slot | function slot | CTA slot]`. Chờ approve block map rồi mới code.
3. **HTML output phải:** semantic tags (`<main><article><section><aside>`), heading hierarchy đúng cấp + font-size giảm dần (H1 36px+), DOM order = visual order, `ul/ol/table` thật, mọi `<img>` có width/height + alt theo chain, form/CTA đặt đúng conversion layer spec, critical info không nằm trong tab ẩn.
4. **Tự chấm trước khi trả:** chạy Quick Checklist (dưới) + mô phỏng Blur Test (block nào chiếm viewport 1? H1 có dominant không?).
5. Kèm 1 đoạn giải thích zone weights đã gán — để designer/dev giữ đúng khi implement thật.

---

## Wireframe Mode — annotated wireframe 3 chế độ (NEW v3.7)

Khi user cần **wireframe annotation** (dạng "PAGE LAYOUT SEMANTICS" — canvas tối, rail Macro/Micro Context trái, block page giữa, callout đánh số phải, legend màu theo zone) thay vì block map text hoặc HTML thật. Spec đầy đủ + template: `references/wireframe-spec.md`. Ba chế độ:

| Mode | Input | Output |
|---|---|---|
| **BUILD** | Query Augmentation Map (Bước 1) + block architecture (Bước 4) | Wireframe HTML mới: mỗi dòng của Map = 1 block + 1 callout giải thích chức năng semantic (component, augmented queries phục vụ, triples, entities) |
| **ANALYZE** | URL / screenshot / HTML của trang CÓ SẴN (mình hoặc đối thủ) | Reverse-engineer thành wireframe + annotate: zone weights, centerpiece, function inventory, augmented query mỗi block đang trả lời, gap (block thiếu / query chưa có component) |
| **COMPARE** | 2 trang cùng page type | Diff matrix theo dimension (hub architecture / H1 naming / spatial proof / NAP / commerce / review / conversion…): verdict **A≠B** (chiến lược khác) / **A=B** (skeleton chung) / **A!** / **B!** (chỉ 1 bên có) + **Convergence Verdict** cuối |

Rules chung: đặt placeholder `{Brand}`, `{Doctor Name}`… cho mọi tên thật (trừ khi user yêu cầu đích danh); footer ghi "illustrative example content"; mỗi wireframe ≤12 block + ≤12 callout (vượt → tách trang); màu zone cố định theo legend trong spec (Macro=teal, Micro=vàng, Transaction/Closure=tím, Evidence=vàng nhạt, Neutral=xám). Wireframe là **artifact phân tích/thuyết trình** — không thay thế HTML build thật (Design Mode).

---

## Quick Checklist

### Visual Hierarchy
- [ ] H1 largest (36px+), prominent, above fold
- [ ] H1 ≤4 entities, no number stuffing, no CTA words
- [ ] Centerpiece gets 60%+ page space *(lưu ý đơn vị: đây là % DIỆN TÍCH trang — khác với zone WEIGHT 100/60-80/40 ở Content Weight Distribution)*
- [ ] Supporting content 20-30% page space
- [ ] Boilerplate under 10%
- [ ] Sidebar not more prominent than main

### Multi-Layer Centerpiece (NEW v2.0 — for hybrid pages)
- [ ] ≥1 supporting block between 2 centerpieces (NEVER stack directly)
- [ ] Each centerpiece serves distinct funnel stage
- [ ] Per-entity templated centerpiece (each platform/category has own template)

### Templated Visual Elements (NEW v2.0)
- [ ] Same page type uses same master template
- [ ] Template repeated ≥3 times for pattern detection
- [ ] 5 critical slots per template (heading + L0 answer + body + visual + functional; CTA thuộc Conversion Layer riêng — chuẩn hóa v3.0)

### Block Chunk Design (NEW v2.0)
- [ ] Each H2 block has ≥4/5 elements (heading + L0 + body + visual + functional)
- [ ] Visual divider/spacing min 48px desktop, 24px mobile
- [ ] Bold/italic/underline used semantically (not decoration)

### Decorative-Semantic Heading (NEW v2.0)
- [ ] "FAQ", "Resources", "Learn More" treated as decorative
- [ ] Real macro-contexts at H2 level (not nested H3 under decorative)
- [ ] Tab navigation has H2 anchor per cluster

### Query → Page Type & Extraction (NEW v3.6)
- [ ] Biến thể query augmented đã map → page type/layout/function; biến thể thừa prune/merge; trang build đúng category thắng SERP
- [ ] Attribute chính trình bày đúng format máy map (giá→bảng, năm→timeline, bộ sưu tập→gallery, "best"→khối review)
- [ ] View-source: ~400 ký tự đầu sau H1 liền mạch — không share/inject/nav chen giữa
- [ ] HTML <2MB; mọi img có width/height; metadata trong initial HTML nhất quán pre/post-render

### Functions
- [ ] Primary CTA working and prominent
- [ ] Mọi function trang claim đều THẬT (không misleading functionality); trang commercial đủ function điều hướng cơ bản (filter…)
- [ ] Forms/filters functional
- [ ] Live function present (notification/counter/calculator) for hybrid pages
- [ ] Mobile-friendly interactions
- [ ] Mobile persistent action ID (bottom fixed nav)

### Trust Stack (NEW v2.0)
- [ ] Layer 1: Search engine reviews badge above-fold
- [ ] Layer 2: Press logo strip
- [ ] Layer 3: Video reviews with name + role
- [ ] Layer 4: Multi-platform review badges
- [ ] Layer 5: Verified customer reviews
- [ ] Layer 6: Live stats bar
- [ ] Layer 7: Team member profiles

### Goldmine Title/Heading Hygiene (renamed v3.0 — scope: title/snippet selection, không phải general ranking)
- [ ] Salient terms (2-3) identified per article
- [ ] Tên brand thống nhất trong title candidate (không đếm số lần nhắc trong bài)
- [ ] Heading factor: H1 exact query, H2 variations, heading render thật (headerIsH1)
- [ ] Title candidate ngắn, dễ đọc (Flesch chỉ áp trang tiếng Anh)
- [ ] Title/heading không tràn width gây truncate (geometry/widthFraction)
- [ ] Vertical consistency: no off-topic content (generic advice — grounding vboostFactor cũ đã bị gỡ)

---

## Related Google Patents (verified 2026-07-02)

| Patent | Focus | Verdict |
|--------|-------|---------|
| **US7421651B2** (từ US20060149775A1, Egnor) | Document segmentation based on visual gaps — segment theo white space khi render | STRONG |
| **US12393768B2** (LAMPRET, granted 08/2025) | Layout-aware multimodal pretraining — font-size/bold/italic/underline per block là model input | STRONG |
| **US9053177B1** (Minkoo Seo) | Sitelinks based on visual location — link chấm theo tọa độ X/Y render | STRONG |
| **US11907337B2** (granted 02/2024) | Multimodal image classifier — đọc ảnh từ pixels, không cần alt | STRONG |
| **WO2018097872A1/EP3529714B1** | Animated snippets — chọn ảnh theo prominence + persistence | STRONG |
| **US7716225B1** (Reasonable Surfer, Dean) | Link value theo prominence + topical cluster match | MODERATE |
| **US8498984B1** (Hwang/Seo, 2013) | Categorization of search results — chấm điểm cấp CATEGORY bằng position-CTR curve (37.3%/12.9%/10.1%…), cap per category → format phải khớp category thắng SERP | STRONG (đọc full-text v3.6) |
| **US9069855B2** (Zunger, granted 2015 — NEW v3.6) | Pseudo-rendering 1 pass → quasi-DOM → **chunk tree**: merge node "gần nhau + tương thích" thành semantically distinct regions; hạ boilerplate | STRONG |
| **US10445328B2** (granted 2019, active — NEW v3.6) | Search result ranking & presentation: entity type → ranked property schema → presentation technique (map/chart/timeline/gallery); soft properties chấm co-occurrence | STRONG (cho SERP-feature benchmark) |
| **US9916366B1** (Bharat/Shukla, granted 2018 — NEW v3.6) | Query Augmentation: query perform tốt + synthetic queries (anchor text lặp đủ ngưỡng = query gắn thẳng document); long click vs reversion | STRONG (cho Bước 1) |
| **US12536233B1** (granted 01/2026 — NEW v3.6) | AI-generated content page: landing page score vượt ngưỡng (trang kém — vd không có product filter) → chèn AI page | STRONG (cho function argument) |
| US8949242B1 | "Semantic document analysis" — change detection per segment. ⚠️ KHÔNG phải centerpiece patent (từng bị cite sai ở v2.x) | historical note |

**Patent applications — chưa cấp, đọc như DESIGN INTENT, phân loại riêng (v3.6, quyết định Vincent 07/2026):**
- **WO2020033805A1** (Website representation vector — **CEASED**): site → vector ~100 chiều (text+images+links, KHÔNG có layout input); tier expert/apprentice/layperson per knowledge domain; site mới classify bằng dot-product với composite vector; representation sinh được từ subdomain.
- **US20240289407A1** (Search with stateful chat — **PENDING**): user state đa lượt; LLM sinh synthetic queries; response linkify về source "verify claim" (mục tiêu GEO).

**De-attributed** (v2.x cite sai, không phải patent layout): US10565267B1 (social feed quality), US8868565B1 (click duration calibration), US20150234930A1 (Ads functional extensions). WebFormer = paper **Meta-led** (WWW 2022, 1 đồng tác giả Google — vì thế xuất hiện trên research.google), không phải "Google's Web Page Transformer"; **WebRef ≠ WebFormer** (Webref = hệ entity annotation trong leak). ⚠️ US12393768B2 (LAMPRET) KHÔNG chứa chữ "cards" — "structured information cards" là diễn giải Koray, dùng như design pattern thì được nhưng đừng cite là patent text. Fact-check đầy đủ: `wiki/sources/research-2026-07-sel-visual-semantics-verification.md` (12 verdicts).

---

## Reference Files

> ⚠️ **v3.0 blanket caveat:** các file trong `references/` viết ở v1.0-v2.1 và CHƯA được fact-fix từng dòng — một số còn cite US8949242B1/US10565267B1/US8868565B1/US20150234930A1/"vboostFactor"/"Google WebFormer" theo cách cũ. Khi mâu thuẫn với SKILL.md: **SKILL.md (v3.0, verified) là nguồn đúng**; bảng patent chuẩn ở section "Related Google Patents (verified 2026-07-02)". Đã fact-fix phần dẫn patent trong `website-function-seo.md` và `ecommerce-website-functions.md` (28/09/2026); các reference khác vẫn là backlog.

Chỉ đọc reference đúng với task hiện tại:

| Nhu cầu | Reference |
|---|---|
| Centerpiece một trang | `references/centerpiece-annotation.md` |
| Service layout + CTA/form | `references/service-page-visual-template.md` + `references/website-function-seo.md` |
| PLP/PDP + filter/cart/review | `references/ecommerce-page-visual-semantic.md` + `references/ecommerce-website-functions.md` |
| Encyclopedia/tutorial + search/bookmark/compare | `references/informational-page-visual-semantic.md` + `references/informational-website-functions.md` |
| Homepage hub hoặc multi-intent | `references/hybrid-page-pattern.md` + `references/multi-layer-centerpiece.md` + `references/templated-visual-elements.md` |
| Layout-aware chunks, đa persona, FAQ/tabs | `references/block-chunk-design.md` + `references/dual-audience-macro-context.md` + `references/decorative-semantic-heading.md` |
| Nén search journey, live function | `references/search-journey-compression.md` + `references/real-time-function-validators.md` |
| Trust, pricing, title/snippet factors | `references/trust-stacking-hierarchy.md` + `references/multi-tier-pricing-pattern.md` + `references/ranklab-factors.md` |
| Hub/spoke, funnel, persona zones | `references/hub-spoke-visual-differentiation.md` + `references/funnel-position-visual-mapping.md` + `references/persona-zone-visual-treatment.md` |
| Query → component/triples | `references/query-augmentation-map.md` |
| Wireframe BUILD/ANALYZE/COMPARE | `references/wireframe-spec.md` |
| Store/office/specialist/local | `references/local-entity-page-patterns.md` |
| QDP chưa có verdict | `keyword-topic-url-mapping/references/qdp-gate.md` của skill `keyword-topic-url-mapping` |

---

## Cross-Skill Integration

This skill integrates with:
- **`semantic-outline-methodology`** — Outline AM should specify visual semantic per heading (centerpiece position, block chunk elements, templated section identification, live function spec)
- **`semantic-content-writing`** — Content writing must follow Goldmine factors (readability, salient terms, brand mention)
- **`topical-map-creation`** — Topical map planning should account for hybrid vs split URL strategy (search journey compression + QDP/QDH/QDS decision)
- **`keyword-topic-url-mapping`** — QDP Gate rubric canonical tại `references/qdp-gate.md` của skill đó; Bước 1 skill này CONSUME verdict (hoặc tự chấm khi chưa có)
- **`local-seo-audit` / `map-pack-intelligence`** — local entity pages build theo `local-entity-page-patterns.md`; 2 skill kia audit/đo, skill này thiết kế
- **`sop/07-visual-semantic.md`** (Knowledge wiki) — bản training đầy đủ của PROCESS 7 bước, kèm RACI + trade-offs
- **Wiki evidence base** — `wiki/sources/research-2026-07-visual-semantics-verification.md` (patent verdicts v3.0) + `wiki/sources/research-2026-07-sel-visual-semantics-verification.md` (12 verdicts Batch 32) + `wiki/cases/koray-visual-semantics-showcase-2026.md` (teardown 4 trang) + `wiki/cases/visual-semantics-sel-cases-2026.md` (5 case SEL)
- **Deep-dive trực quan** — wiki nội bộ «07-visual-semantic-deep-dive» (ngoài repo, hỏi Lead/Vincent): giải thích cơ chế + PROCESS 8 bước + block map template + checklist 24 eval tương tác

---

## Benchmark and service application patterns

Khi áp dụng cho e-commerce, marketplace hoặc service page, đọc [references/benchmark-and-service-patterns.md](references/benchmark-and-service-patterns.md). File này chứa benchmark VN, Koray live-site patterns, Amazon PDP và khung 14 block service page.

## E-commerce Build Evals (NEW v3.5 — đúc từ 3 vòng build IndochinaLight, 07/2026)

Checklist ĐẠT/KHÔNG-ĐẠT khi build hoặc review PLP · PDP · Home · Search · Cart · Thank-you. Mỗi mục là một quyết định đã được Vincent duyệt qua vòng feedback thật — evidence: tài liệu nội bộ «indochinalight_Build-*_v3» (ngoài repo, hỏi Lead/Vincent) + Figma checklist sheet.

| # | Eval | Rule ĐẠT |
|---|---|---|
| E1 | **PLP fold budget** | Hàng sản phẩm đầu ≤ ~600px desktop / ≤1.5 màn mobile. Sub-nav = chip-thumbnail compact 1 hàng, KHÔNG tile to trước grid. PLP không banner hero — feature image đi qua `og:image` + `CollectionPage.image`. |
| E2 | **Sticky = mission tools** | Sticky toolbar chỉ chứa công cụ của mission hiện tại (Filter · count · Sort · active chips). Link điều hướng ra ngoài scope (sub/sibling collection) = wayfinding at entry, để tĩnh, không sticky theo. |
| E3 | **Card 7 lớp + attribute** | Badge label thật → 1 room-tag primary (multi-room ở data layer bằng tag/metafield `room:* fit:* ceiling:* label:*` — 1 nguồn render card + PDP room-fit + automated collection, pattern Rowabi) → attr line `n sizes · X″–Y″ dia. · weave` → giá From + gạch + %off thật → rating + swatch. Swatch = `<button>` đổi ảnh variant (không navigate, tap ≥44px). |
| E4 | **Đơn vị theo locale audience** | US: inch + "dia." — KHÔNG dùng ký hiệu Ø (user phổ thông US không đọc được). cm chỉ nằm phụ trong bảng specs. |
| E5 | **Link placement PLP** | Đầu trang = đi SÂU (children/facet-landing của chính category); cuối trang = đi NGANG/LÊN (sibling + parent). Section informational (ideas/guides) PHẢI link bài blog/blog category thật — không link collection. |
| E6 | **Review display ladder** | 0 review = ẨN khối rating (không show ★0); 1–14 = summary + list DỌC + "Show all N"; ≥15 = histogram 5→1 clickable (=filter) + photo strip + aspect chips có số đếm thật + sort đầy đủ. Histogram phải khớp aggregate thật. |
| E7 | **Sale display** | Label "Save X%" (không "Discount"), không countdown/fake urgency; khi sale, sticky rail + mobile bar cũng hiện giá mới + gạch + badge. Social-proof counter (viewed/bought) chỉ khi bind data app thật. |
| E8 | **Sticky mirror state** | 2-pane scroll: KHÔNG inner-scroll; position:sticky theo pha. Khối buy > viewport → mini-rail mirror ĐỦ state (thumb theo màu + variant line + qty + giá) — user không bao giờ phải cuộn ngược để mua. |
| E9 | **Section heading = entity** | H2 section = tên entity/danh mục thật + 1 dòng sub-context dưới heading. Home = hub RỘNG (cấp 1 + style/room tiles); category = hub SÂU (không lặp style-tiles to). "New arrivals" chỉ tồn tại khi có nhịp hàng mới thật. |
| E10 | **Trust placement** | Press logos = dải mỏng "As seen in" GIỮA trang cạnh Story/About, grayscale muted — không đặt dưới hero. Payment = logo SVG chính chủ ~24px muted trong `<ul aria-label>`, không khối payment to, không text pill. |
| E11 | **Cart honesty** | Progress bar tới ngưỡng freeship THẬT + bundle nudge theo số item thật trong giỏ + copy-code chip; variant line đầy đủ trên line item; express buttons; "shipping calculated at checkout". |
| E12 | **Thank-you = trust moment** | Made-to-order bắt buộc có delivery timeline visual đặt kỳ vọng lead time (Placed → Production Xd → Delivery Yd) + What's next; không upsell nặng. |

**Cách dùng:** build xong chấm 12 eval; mục KHÔNG-ĐẠT phải có lý do được duyệt. Khi review design của team, cite số eval (E1-E12) thay vì diễn giải lại.

## Changelog

- **v3.7.1 (2026-10-19):** goldmine factor chấm title candidate, không chấm thân bài: bỏ Flesch ≥60 cho trang tiếng Việt, bỏ quota nhắc brand 5-7 lần, ghi rõ field `vboostFactor` không có trong leak; funnel mapping bỏ số từ cố định theo funnel (TOFU 5000-10000); xoá ví dụ số liệu GTV không có nguồn trong `ranklab-factors.md`.
- **v3.7 (24/07/2026):** Batch 37 (bài Koray SEL "How semantics and topical authority improve local SEO" 22/07 + 7 wireframe style-reference). (1) Bước 1 nâng thành **Query Augmentation & QDP Gate**: 4 tiêu chí ≥3/4 (demand/entities/similarity-WEIGHTED/pattern) → page, không đạt → QDH/QDS/component (table/form/calculator/filter); weighted-term rule (term nặng nhất = subject của triples — Bendersky/Najork); output đổi thành **Query Augmentation Map 4 cột** (queries→component→triples→entities). (2) **Wireframe Mode** 3 chế độ BUILD/ANALYZE/COMPARE + `references/wireframe-spec.md` (format PAGE LAYOUT SEMANTICS: rail macro/micro, callout đánh số, legend zone, diff matrix A≠B/A=B/A!/B!). (3) Archetype mới **Local Entity Pages** + `references/local-entity-page-patterns.md` (geo utility bar, NAP GBP field parity, landmark grounding, breadcrumb sibling switcher, 2 transaction modes, review acquisition loop, anti-doorway localization, store-entity skeleton). (4) Pattern 8 + forum subdomain route cho opinionated/experience queries + routing 4 query types. (5) Bước 2 thêm rule local: homepage target location-service pair #1 + contextual bridges → quality nodes. (6) `references/query-augmentation-map.md` (worked example rehab 12 dòng). Cross-skill: QDP gate canonical ở `keyword-topic-url-mapping/references/qdp-gate.md`. Evidence: wiki Batch 37 ([[sources/local-seo-topical-authority-sel-koray]] + [[Local SEO]] + [[cases/local-seo-sel-cases-2026]] + [[QDP-QDH-QDS]] →stable).
- **v3.6 (16/07/2026):** Batch 32 (bài Koray SEL "Visual semantics" + 15 nguồn full-text, fact-check 3 vòng — 12 verdicts). (1) Core Principle + Formula v3 `((HD×TC)÷CoR) × Right Visual Annotations` + decision-tree gate (Nayak top ~20-30 đính chính). (2) PROCESS 7→8 bước: Bước 1 mới Query Augmentation Classification (map biến thể → page type/layout/function + prune/merge); Bước 3 nâng thành SERP & Attribute Benchmark (đọc ngược feature→attribute US10445328B2 + category thắng SERP US8498984B1); Bước 7 thêm HTML 2MB + image dimensions + JS bundle; Bước 8 thêm extraction test 400 ký tự. (3) Centerpiece Dial thêm hygiene flow liền mạch (Goodoc Flow/FlowThread + DOJ example; 400 chars label single-source) + case converter +30.5%. (4) Pattern 7 Subdomain Testing (3 lớp grounding) + Pattern 8 Content Type Distribution (2×2 + 4 kỹ thuật + 3 component). (5) Website Functions có consequence: misleading functionality spam policy + US12536233B1 "no product filter" trigger. (6) Bảng patents +4 granted (US9069855B2, US10445328B2, US9916366B1, US12536233B1), US8498984B1 nâng STRONG, bảng riêng patent APPLICATIONS (WO2020033805A1 CEASED, US20240289407A1 PENDING — design intent); fact-notes: LAMPRET không chứa "cards", WebRef ≠ WebFormer. (7) Quick Checklist +6 items; pointer deep-dive `sop/07-visual-semantic-deep-dive.html` (checklist 24 eval). Evidence: wiki Batch 32 (16 source pages + case page + verification page).
- **v3.5 (12/07/2026):** Thêm module E-commerce Build Evals — 12 eval ĐẠT/KHÔNG-ĐẠT (E1-E12) đúc từ 3 vòng build + feedback IndochinaLight: PLP fold budget + không banner hero, sticky=mission tools, card 7 lớp + tag/metafield sync (pattern Rowabi verify 12/07), đơn vị dia. cho US, link placement (informational→blog), review ladder 0/1-14/≥15, sale display Save + counter app-bound, sticky mirror state (không inner-scroll), section heading=entity + sub-line, trust placement (press mid-page, payment logo chính chủ), cart honesty (progress freeship thật + bundle nudge), thank-you timeline made-to-order. Evidence: Build v3 6 trang (home/category/PDP/search/cart/thank-you) trong tài liệu nội bộ «.» (ngoài repo, hỏi Lead/Vincent)
- **v3.4 (10/07/2026):** Thêm module Service Page Application Playbook — bảng dịch 14 pattern (S1-S14) từ 3 bộ benchmark sang trang dịch vụ (MTM case Thu Cũ + Koray Benchmark #5 · Koray live-sites v3.2 · Amazon v3.3): quote-box + response-time promise, gói per-tier capacity thật, bảng thông số dịch vụ, review-proof trên H1, definition-first blockquote, quy trình ol markup thật, micro-template per service, numeric range đậm, variant enumeration, công cụ sống ≤5 bước tạm-tính-sớm, freebie spoke, use-case tabs theo user attribute, aspect-chip testimonials, recency tĩnh. Kèm khung 14 block thay khung 5 block khi cần bản đầy đủ + counter-signals service (heading adjective, quy trình trong ảnh, số không case, form-only, heading bloat, trust rải ngẫu nhiên). Addendum pointer trong `references/service-page-visual-template.md`. Evidence: tài liệu nội bộ «MTM-iPhone-PLP-Review» (ngoài repo, hỏi Lead/Vincent) + wiki/syntheses/koray-live-site-patterns-2026.md + indochinalight_PDP-Review_v2.html mục 8.
- **v3.3 (10/07/2026):** Thêm module Marketplace PDP Patterns — 9 pattern + 5 counter-signal từ benchmark Amazon B0CZ3S7S3P (rattan pendant 4.5★/165, Amazon's Choice; Playwright capture desktop 15 slice + mobile 17 slice + DOM facts): isolated buy-box + delivery-date promise, variant self-priced, E-A-V mini table in-fold, identity-first mobile, sticky in-page nav, About benefit-bullets, room-tabs use-case, UGC-as-attribute-layer (Customers say + aspect chips), social-proof recency tĩnh. Counter-signals: title stuffing, 13 H1/0 JSON-LD, attribute rác (Pegasus), sponsored clutter, review gating. Evidence: tài liệu nội bộ «indochinalight_PDP-Review_v2» (ngoài repo, hỏi Lead/Vincent) mục 8. Pointer thêm ở section E-commerce: Product (PDP).
- **v3.2.2 (09/07/2026):** Làm rõ 2 TRỤC cho tabs/accordion (sau audit Rowabi/Indochinalight PDP). (1) Trục INDEX = content-in-DOM-hay-không: `display:none` nằm trong DOM vẫn **full-weight**, chỉ **JS-reveal-on-click** mới không index → myth "`display:none` bị deweight/bỏ qua" và "accordion > tab vì display:none" đã bác. (2) Trục PROMINENCE = visible-mặc-định-hay-không: content ẩn mặc định (tab display:none HAY accordion collapse — **như nhau**, cơ chế CSS không đổi) không thể là Centerpiece → critical info (giá/lương/spec/answer chunk) phải visible/in-flow, phần phụ mới cho vào accordion. Bảng quyết định + hierarchy build: skill `semantic-html-optimization` mục "Tabs vs Accordion".
- **v3.2.1 (09/07/2026):** Fact-check tabs/accordion — mobile-first index tính TRỌN trọng số cho nội dung ẩn trong tab HAY accordion, không phân biệt 2 dạng (Google MFI Best Practices khuyến nghị chủ động dùng accordion/tab trên mobile; Illyes 2016 "full weight"; điều kiện: nội dung nằm sẵn trong DOM, không phải fetch-on-click). Luật "critical info không nằm trong tabs" GIỮ NGUYÊN — lý do là visual prominence/Centerpiece (nội dung ẩn mặc định không thể là centerpiece), KHÔNG phải vì không được index. Chi tiết + test: skill `semantic-html-optimization` mục "Tabs vs Accordion".
- **v3.2 (07/07/2026):** Thêm module Koray Live-Site Patterns — 11 pattern từ 3 site case-study Koray (sutliffstout legal YMYL, morethanpanel SMM transactional, oscarwylee eyewear PLP) kèm ranking evidence Ahrefs + counter-signals về heading bloat/decay. Evidence: wiki/syntheses/koray-live-site-patterns-2026.md.
- **v3.1 (07/07/2026):** Thêm module VN E-commerce Visual Patterns — 10 pattern benchmark CellphoneS/TGDĐ (carousel placement, flash-sale placement, mobile spec-elevation, condition-as-attribute, FAQ vs UGC-Q&A, entity>commercial weighting, spec 7 nhóm, trade-in service page, homepage heading = entity name, facet definition tooltip) + nguyên tắc Homepage theo Source Context. Evidence: wiki/syntheses/vn-ecommerce-visual-patterns-cps-tgdd-2026.md.
- **v3.0 (Jul 2026):** (1) Fact-fix toàn bộ patent/leak citations — US8949242B1 de-attributed, thay bằng bộ verified (US7421651B2, US12393768B2 LAMPRET, US9053177B1, US11907337B2, WO2018097872A1, US7716225B1); goldmine* prefix đúng tên; xóa vboostFactor (= mis-crop goldmineNavboostFactor); Goldmine reframe thành title/snippet scoring; bảng interaction weights label interpretation. (2) Thêm PROCESS 7 bước (Design-in/Audit-fix) + Centerpiece Dial + Conversion Layer + Entity Card Skeleton (từ teardown morethanpanel + sutliffstout). (3) Core Principle đổi sang Koray 4 Pillars. (4) Module mới Image-Level Semantics (ImageData, US11907337B2, visual search fan-out, chain Image URL→Alt). (5) Design Mode — luật khi agent build page. (6) Thêm clutterScore + contentEffort evidence.
- **v2.1 (May 2026):** Added 3 page-level architecture modules — Hub-Spoke Visual Differentiation (7-element matrix for distinguishing hub vs spoke pages), Funnel Position Visual Mapping (visual emphasis by TOFU/MOFU/BOFU/Hybrid), Persona Zone Visual Treatment (6-element spec for distinct persona zones in hybrid pages).
- **v2.0 (May 2026):** Added 6 advanced patterns (Multi-Layer Centerpiece, Templated Visual Elements, Block Chunk Design, Dual-Audience Macro-context, Decorative-Semantic Heading, Search Journey Compression) + 3 supporting modules (Real-Time Function Validators, Trust Stacking Hierarchy, Multi-Tier Pricing Pattern) + RankLab Factors module. Added Hybrid Page type with morethanpanel.com worked example. Updated Quick Checklist with v2.0 items.
- **v1.0:** Foundation skill with centerpiece annotation, page type templates, website functions.
