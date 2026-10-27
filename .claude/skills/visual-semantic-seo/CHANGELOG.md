# Changelog — Visual Semantic SEO Skill

## v3.0.1 (28/09/2026) — Fact-fix website function

- `references/website-function-seo.md`, `references/ecommerce-website-functions.md`: bỏ dẫn US10565267B1 (bài đăng mạng xã hội), US8868565B1 (landing page quảng cáo), US20150234930A1 (tiện ích quảng cáo) làm căn cứ website function; bảng hệ số 1x/5x/10x đổi thành mức ưu tiên kiểm nội bộ; thời lượng kỳ vọng ghi là quy ước thực hành.
- SKILL.md mục Interaction Signals: "broken function" ghi là heuristic, bỏ dẫn US7716225B1 (reasonable surfer, trọng số link).
- Nguồn đối chiếu: wiki nội bộ «Google Leak Decoded» (ngoài repo) (toàn văn patent, fact-check wiki Semantic SEO ngày 27-28/09/2026).

## v3.0 (Jul 2026) — Fact-check + Process + Image-Level Semantics + Design Mode

### Fixed — Patent/leak citations (verified trên nguồn gốc 2026-07-02)

- **US8949242B1 de-attributed**: patent thật = "Semantic document analysis" (change detection per segment), KHÔNG phải centerpiece. Nguồn khái niệm centerpiece = Martin Splitt (Google, 2021) + leak main-content/boilerplate.
- **Bộ patent verified thay thế**: US7421651B2 (visual gaps segmentation), US12393768B2 (LAMPRET — granted 08/2025, typography là model input), US9053177B1 (sitelinks visual location), US11907337B2 (multimodal image classifier), WO2018097872A1 (animated snippets), US7716225B1 (Reasonable Surfer).
- **De-attributed**: US10565267B1 (social feed), US8868565B1 (click duration), US20150234930A1 (Ads) — không phải patent layout.
- **Goldmine factors đổi tên đúng leak**: goldmineReadabilityScore, goldmineHeadingFactor, goldmineSitenameFactor, goldmineSalientTermFactor, goldmineNavboostFactor. **Xóa vboostFactor** (không tồn tại — mis-crop từ slide của goldmineNavboostFactor, verify hexdocs). Reframe: Goldmine = title/snippet selection scoring.
- Bảng interaction weights (5x/10x) → label interpretation (không có nguồn).
- WebFormer ghi đúng chủ: paper Meta (WWW 2022), không phải Google.

### Added

- **PROCESS 7 bước** (Design-in / Audit-fix) — bản đầy đủ + RACI: wiki nội bộ «07-visual-semantic» (ngoài repo).
- **Centerpiece Dial** — rule ≤120 từ là conditional theo vertical (đo từ teardown morethanpanel/sutliffstout).
- **Conversion Layer** — CTA-as-heading (YMYL) / order widget in-card (e-com).
- **Entity Card Skeleton** — "page as database render".
- **Core Principle → Koray 4 Pillars** (Visualization / Verbalization / Contextualization / Commercialization).
- **Image-Level Semantics module** — ImageData (OCR, entity-in-image, h2i/h2c), US11907337B2, visual search fan-out, chain Image URL ≤3 từ → Alt.
- **Design Mode** — luật khi Claude build page (block map trước → approve → HTML; semantic tags; DOM order = visual order; tự chấm checklist + Blur Test).
- Evidence mới: clutterScore, contentEffort.

### Source Material

- 4 research notes Batch 23 (wiki `raw/_ingested/research-2026-07-*`), slides lecture Koray (Lead cung cấp), teardown DOM 4 trang showcase.


## v2.1 (May 2026) — Page-Level Architecture Upgrade

### Added — 3 New Reference Modules

**Page-Level Architecture Modules:**
- `references/hub-spoke-visual-differentiation.md` — 7-element matrix differentiating Hub vs Spoke vs Detail vs Definitional pages. Covers Hero size, CTA count, trust layer count, centerpiece count, templated repetition, FAQ size, divider style. Application examples for morethanpanel/APOHAIR/TAG/GTV.
- `references/funnel-position-visual-mapping.md` — Visual emphasis allocation by TOFU/MOFU/BOFU/Hybrid funnel position. Covers element ratios, CTA style, word density, visual pacing per funnel position. Audit framework included.
- `references/persona-zone-visual-treatment.md` — 6-element spec for distinct persona zones in hybrid pages (color accent, background, imagery, layout density, icons, CTA). 4 persona zone architecture patterns (Sequential / Tabbed / Side-by-Side / Embedded). Distinguishes from dual-audience macro-context pattern.

### Updated — SKILL.md Main File

- New section "Page-Level Architecture Files (NEW v2.1)" in Reference Files
- Added 3 entries to Quick Lookup
- Updated Changelog section

### Source Material

- Reverse-engineering hub-spoke pattern from morethanpanel.com (hub `/` vs spoke `/buy-instagram-followers`)
- Conversation analyzing APOHAIR homepage outline AM v2.1 — identified 3 missing page-level architecture patterns
- Funnel position mapping principles from B2B/B2C visual semantic research

---

## v2.0 (May 2026) — Advanced Patterns Upgrade

### Added — 11 New Reference Modules

**6 Advanced Pattern Modules:**
- `references/hybrid-page-pattern.md` — 22-section master layout for hybrid pages with morethanpanel.com as worked example
- `references/multi-layer-centerpiece.md` — Stacked centerpiece architecture (L1/L2/L3) with spacing rules and decision matrix
- `references/templated-visual-elements.md` — Template repetition for Google's WebFormer pattern detection
- `references/block-chunk-design.md` — Self-contained block rules following Layout-aware Multimodal Document Understanding patent
- `references/dual-audience-macro-context.md` — Same macro-context for 2 personas with phrasing variation
- `references/decorative-semantic-heading.md` — Decorative container vs semantic macro-context separation
- `references/search-journey-compression.md` — 1 URL multi-intent strategy with 7-dimension coverage

**3 Supporting Pattern Modules:**
- `references/real-time-function-validators.md` — Live tickers, counters, calculators
- `references/trust-stacking-hierarchy.md` — 7-layer trust positioning architecture
- `references/multi-tier-pricing-pattern.md` — Pricing card 4 mandatory elements + Best Offer logic

**1 Optimization Module:**
- `references/ranklab-factors.md` — Per-factor optimization for Goldmine final score

### Foundation Files Preserved (v1.0)

All v1.0 reference files retained unchanged:
- `references/centerpiece-annotation.md`
- `references/service-page-visual-template.md`
- `references/ecommerce-page-visual-semantic.md`
- `references/informational-page-visual-semantic.md`
- `references/website-function-seo.md`
- `references/ecommerce-website-functions.md`
- `references/informational-website-functions.md`

### Source Material

- Koray Tuğberk GÜBÜR's event presentation slides (May 2026)
- Reverse-engineering analysis of morethanpanel.com (Koray-built reference template)
- Content Warehouse API leak (May 2024): Goldmine ranking system, RankLab factors
- Google Patents: US8949242B1, US20150234930A1, Layout-aware Multimodal Document Understanding (2023)
- Research papers: TW-BERT, End-to-End Query Term Weighting, WebFormer attention model

---

## v1.0 — Foundation Skill

Initial skill release with:
- Centerpiece annotation framework
- Service page, E-commerce (PLP/PDP), Informational page templates
- Website functions for service, e-commerce, informational pages
- Content weight distribution (Centerpiece 100%, Supporting 60-80%, Sidebar 20-40%, Boilerplate 5-10%)
- Quick checklist (visual hierarchy, functions, content quality)

## Changelog v1.0–v3.6 chuyển từ SKILL.md (27/10/2026)

- **v3.6 (16/07/2026):** Batch 32 (bài Koray SEL "Visual semantics" + 15 nguồn full-text, fact-check 3 vòng — 12 verdicts). (1) Core Principle + Formula v3 `((HD×TC)÷CoR) × Right Visual Annotations` + decision-tree gate (Nayak top ~20-30 đính chính). (2) PROCESS 7→8 bước: Bước 1 mới Query Augmentation Classification (map biến thể → page type/layout/function + prune/merge); Bước 3 nâng thành SERP & Attribute Benchmark (đọc ngược feature→attribute US10445328B2 + category thắng SERP US8498984B1); Bước 7 thêm HTML 2MB + image dimensions + JS bundle; Bước 8 thêm extraction test 400 ký tự. (3) Centerpiece Dial thêm hygiene flow liền mạch (Goodoc Flow/FlowThread + DOJ example; 400 chars label single-source) + case converter +30.5%. (4) Pattern 7 Subdomain Testing (3 lớp grounding) + Pattern 8 Content Type Distribution (2×2 + 4 kỹ thuật + 3 component). (5) Website Functions có consequence: misleading functionality spam policy + US12536233B1 "no product filter" trigger. (6) Bảng patents +4 granted (US9069855B2, US10445328B2, US9916366B1, US12536233B1), US8498984B1 nâng STRONG, bảng riêng patent APPLICATIONS (WO2020033805A1 CEASED, US20240289407A1 PENDING — design intent); fact-notes: LAMPRET không chứa "cards", WebRef ≠ WebFormer. (7) Quick Checklist +6 items; pointer deep-dive `sop/07-visual-semantic-deep-dive.html` (checklist 24 eval). Evidence: wiki Batch 32 (16 source pages + case page + verification page).
- **v3.5 (12/07/2026):** Thêm module E-commerce Build Evals — 12 eval ĐẠT/KHÔNG-ĐẠT (E1-E12) đúc từ 3 vòng build + feedback IndochinaLight: PLP fold budget + không banner hero, sticky=mission tools, card 7 lớp + tag/metafield sync (pattern Rowabi verify 12/07), đơn vị dia. cho US, link placement (informational→blog), review ladder 0/1-14/≥15, sale display Save + counter app-bound, sticky mirror state (không inner-scroll), section heading=entity + sub-line, trust placement (press mid-page, payment logo chính chủ), cart honesty (progress freeship thật + bundle nudge), thank-you timeline made-to-order. Evidence: Build v3 6 trang (home/category/PDP/search/cart/thank-you) trong tài liệu nội bộ «.» (ngoài repo, hỏi Lead)
- **v3.4 (10/07/2026):** Thêm module Service Page Application Playbook — bảng dịch 14 pattern (S1-S14) từ 3 bộ benchmark sang trang dịch vụ (MTM case Thu Cũ + Koray Benchmark #5 · Koray live-sites v3.2 · Amazon v3.3): quote-box + response-time promise, gói per-tier capacity thật, bảng thông số dịch vụ, review-proof trên H1, definition-first blockquote, quy trình ol markup thật, micro-template per service, numeric range đậm, variant enumeration, công cụ sống ≤5 bước tạm-tính-sớm, freebie spoke, use-case tabs theo user attribute, aspect-chip testimonials, recency tĩnh. Kèm khung 14 block thay khung 5 block khi cần bản đầy đủ + counter-signals service (heading adjective, quy trình trong ảnh, số không case, form-only, heading bloat, trust rải ngẫu nhiên). Addendum pointer trong `references/service-page-visual-template.md`. Evidence: tài liệu nội bộ «MTM-iPhone-PLP-Review» (ngoài repo, hỏi Lead) + wiki/syntheses/koray-live-site-patterns-2026.md + indochinalight_PDP-Review_v2.html mục 8.
- **v3.3 (10/07/2026):** Thêm module Marketplace PDP Patterns — 9 pattern + 5 counter-signal từ benchmark Amazon B0CZ3S7S3P (rattan pendant 4.5★/165, Amazon's Choice; Playwright capture desktop 15 slice + mobile 17 slice + DOM facts): isolated buy-box + delivery-date promise, variant self-priced, E-A-V mini table in-fold, identity-first mobile, sticky in-page nav, About benefit-bullets, room-tabs use-case, UGC-as-attribute-layer (Customers say + aspect chips), social-proof recency tĩnh. Counter-signals: title stuffing, 13 H1/0 JSON-LD, attribute rác (Pegasus), sponsored clutter, review gating. Evidence: tài liệu nội bộ «indochinalight_PDP-Review_v2» (ngoài repo, hỏi Lead) mục 8. Pointer thêm ở section E-commerce: Product (PDP).
- **v3.2.2 (09/07/2026):** Làm rõ 2 TRỤC cho tabs/accordion (sau audit Rowabi/Indochinalight PDP). (1) Trục INDEX = content-in-DOM-hay-không: `display:none` nằm trong DOM vẫn **full-weight**, chỉ **JS-reveal-on-click** mới không index → myth "`display:none` bị deweight/bỏ qua" và "accordion > tab vì display:none" đã bác. (2) Trục PROMINENCE = visible-mặc-định-hay-không: content ẩn mặc định (tab display:none HAY accordion collapse — **như nhau**, cơ chế CSS không đổi) không thể là Centerpiece → critical info (giá/lương/spec/answer chunk) phải visible/in-flow, phần phụ mới cho vào accordion. Bảng quyết định + hierarchy build: skill `semantic-html-optimization` mục "Tabs vs Accordion".
- **v3.2.1 (09/07/2026):** Fact-check tabs/accordion — mobile-first index tính TRỌN trọng số cho nội dung ẩn trong tab HAY accordion, không phân biệt 2 dạng (Google MFI Best Practices khuyến nghị chủ động dùng accordion/tab trên mobile; Illyes 2016 "full weight"; điều kiện: nội dung nằm sẵn trong DOM, không phải fetch-on-click). Luật "critical info không nằm trong tabs" GIỮ NGUYÊN — lý do là visual prominence/Centerpiece (nội dung ẩn mặc định không thể là centerpiece), KHÔNG phải vì không được index. Chi tiết + test: skill `semantic-html-optimization` mục "Tabs vs Accordion".
- **v3.2 (07/07/2026):** Thêm module Koray Live-Site Patterns — 11 pattern từ 3 site case-study Koray (sutliffstout legal YMYL, morethanpanel SMM transactional, oscarwylee eyewear PLP) kèm ranking evidence Ahrefs + counter-signals về heading bloat/decay. Evidence: wiki/syntheses/koray-live-site-patterns-2026.md.
- **v3.1 (07/07/2026):** Thêm module VN E-commerce Visual Patterns — 10 pattern benchmark CellphoneS/TGDĐ (carousel placement, flash-sale placement, mobile spec-elevation, condition-as-attribute, FAQ vs UGC-Q&A, entity>commercial weighting, spec 7 nhóm, trade-in service page, homepage heading = entity name, facet definition tooltip) + nguyên tắc Homepage theo Source Context. Evidence: wiki/syntheses/vn-ecommerce-visual-patterns-cps-tgdd-2026.md.
- **v3.0 (Jul 2026):** (1) Fact-fix toàn bộ patent/leak citations — US8949242B1 de-attributed, thay bằng bộ verified (US7421651B2, US12393768B2 LAMPRET, US9053177B1, US11907337B2, WO2018097872A1, US7716225B1); goldmine* prefix đúng tên; xóa vboostFactor (= mis-crop goldmineNavboostFactor); Goldmine reframe thành title/snippet scoring; bảng interaction weights label interpretation. (2) Thêm PROCESS 7 bước (Design-in/Audit-fix) + Centerpiece Dial + Conversion Layer + Entity Card Skeleton (từ teardown morethanpanel + sutliffstout). (3) Core Principle đổi sang Koray 4 Pillars. (4) Module mới Image-Level Semantics (ImageData, US11907337B2, visual search fan-out, chain Image URL→Alt). (5) Design Mode — luật khi agent build page. (6) Thêm clutterScore + contentEffort evidence.
- **v2.1 (May 2026):** Added 3 page-level architecture modules — Hub-Spoke Visual Differentiation (7-element matrix for distinguishing hub vs spoke pages), Funnel Position Visual Mapping (visual emphasis by TOFU/MOFU/BOFU/Hybrid), Persona Zone Visual Treatment (6-element spec for distinct persona zones in hybrid pages).
- **v2.0 (May 2026):** Added 6 advanced patterns (Multi-Layer Centerpiece, Templated Visual Elements, Block Chunk Design, Dual-Audience Macro-context, Decorative-Semantic Heading, Search Journey Compression) + 3 supporting modules (Real-Time Function Validators, Trust Stacking Hierarchy, Multi-Tier Pricing Pattern) + RankLab Factors module. Added Hybrid Page type with morethanpanel.com worked example. Updated Quick Checklist with v2.0 items.
- **v1.0:** Foundation skill with centerpiece annotation, page type templates, website functions.
