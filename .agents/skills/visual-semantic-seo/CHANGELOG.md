# Changelog — Visual Semantic SEO Skill

## v3.0 (Jul 2026) — Fact-check + Process + Image-Level Semantics + Design Mode

### Fixed — Patent/leak citations (verified trên nguồn gốc 2026-07-02)

- **US8949242B1 de-attributed**: patent thật = "Semantic document analysis" (change detection per segment), KHÔNG phải centerpiece. Nguồn khái niệm centerpiece = Martin Splitt (Google, 2021) + leak main-content/boilerplate.
- **Bộ patent verified thay thế**: US7421651B2 (visual gaps segmentation), US12393768B2 (LAMPRET — granted 08/2025, typography là model input), US9053177B1 (sitelinks visual location), US11907337B2 (multimodal image classifier), WO2018097872A1 (animated snippets), US7716225B1 (Reasonable Surfer).
- **De-attributed**: US10565267B1 (social feed), US8868565B1 (click duration), US20150234930A1 (Ads) — không phải patent layout.
- **Goldmine factors đổi tên đúng leak**: goldmineReadabilityScore, goldmineHeadingFactor, goldmineSitenameFactor, goldmineSalientTermFactor, goldmineNavboostFactor. **Xóa vboostFactor** (không tồn tại — mis-crop từ slide của goldmineNavboostFactor, verify hexdocs). Reframe: Goldmine = title/snippet selection scoring.
- Bảng interaction weights (5x/10x) → label interpretation (không có nguồn).
- WebFormer ghi đúng chủ: paper Meta (WWW 2022), không phải Google.

### Added

- **PROCESS 7 bước** (Design-in / Audit-fix) — bản đầy đủ + RACI: `Knowledge/Semantic SEO A - Z/sop/07-visual-semantic.md`.
- **Centerpiece Dial** — rule ≤120 từ là conditional theo vertical (đo từ teardown morethanpanel/sutliffstout).
- **Conversion Layer** — CTA-as-heading (YMYL) / order widget in-card (e-com).
- **Entity Card Skeleton** — "page as database render".
- **Core Principle → Koray 4 Pillars** (Visualization / Verbalization / Contextualization / Commercialization).
- **Image-Level Semantics module** — ImageData (OCR, entity-in-image, h2i/h2c), US11907337B2, visual search fan-out, chain Image URL ≤3 từ → Alt.
- **Design Mode** — luật khi Claude build page (block map trước → approve → HTML; semantic tags; DOM order = visual order; tự chấm checklist + Blur Test).
- Evidence mới: clutterScore, contentEffort.

### Source Material

- 4 research notes Batch 23 (wiki `raw/_ingested/research-2026-07-*`), slides lecture Koray (Vincent cung cấp), teardown DOM 4 trang showcase.


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
