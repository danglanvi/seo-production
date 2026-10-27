# Hybrid Page Pattern (v2.0)

**When to use:** Homepage hubs, multi-intent landing pages, central node của topical map serve nhiều buyer personas trong 1 URL.

**Core principle:** Hybrid page = E-commerce + Informational + Service combined. Cần multi-layer centerpiece, templated repetition, full search journey coverage.

---

## When This Pattern Applies

Apply hybrid page pattern when:
- Page là **central hub** của topical map
- Site monetize qua **multiple paths** (subscription + per-product + reseller)
- Audience có **multiple personas** với intent overlap (≥80%)
- DR < 50 (cần compress journey để rank multi-keyword với 1 URL)
- Conversion + education hybrid goal

**Don't apply when:**
- Single-intent service page → use Service pattern
- Single product detail → use PDP pattern
- Single category browse → use PLP pattern

---

## The 22-Section Master Layout

Based on reverse-engineering morethanpanel.com (Koray-built template):

```
[1] HEADER (5%) — Logo + Lang switch + Nav + Sign-in/Register
[2] CENTERPIECE L1 (100%) — Above-the-fold:
    - Trust strip (Search engine reviews badge — Google 4.8/5)
    - H1: Entity declaration with primary search query
    - Definition paragraph (~50 words) — Answer-First L0
    - 6 trust attributes (3 visible columns × 2 rows)
    - Demonstrative annotation (CEO/team video + product image)
    - Social proof: "Trusted By +X" + Primary CTA
    - Live notification widget
    - Inline action form (Login or Lead Capture)
[3] BRAND CREDIBILITY STRIP (5%) — Press logo strip horizontal scroll
[4] SUPPORTING — Reviews Block (60%):
    - H2: "Best [Entity] Reviews"
    - Description paragraph
    - Tab navigation: Video Reviews | Customer Reviews | Platform Reviews
    - 4 video reviewer cards với name + role
    - Platform badges: Google | ProductHunt | G2 | SourceForge
[5] LIVE STATS BAR (60%) — 6 real-time metrics:
    - Total orders/transactions completed
    - Frequency indicator (e.g., "0.07 sec — order frequency")
    - User count
    - Output delivered (likes/views/leads)
    - Starting price
    - Total services/products
[6] EDUCATIONAL — H2 #1 (60%):
    - "How does [Entity] Work?" (singular, end-user audience)
    - 5-step process cards (Register → Add Funds → Choose → Place → Receive)
    - Embedded video tutorial
[7] SUPPORTING — Advantages (60%):
    - H3: "Advantages of Using [Entity]"
    - 12 advantages, mỗi cái H4 + paragraph + inline CTA
    - Apply Templated Visual Elements pattern
[8] EDUCATIONAL — Order Process (60%):
    - H2: "How to Place a [Entity] Order?"
    - 7 numbered steps
    - PQ embedded: "How can [Entity] help make money?"
    - PQ embedded: "How to track order progress?"
[9] CENTERPIECE L2 (100%) — Pricing comparison:
    - H2: "Best and Cheapest [Entity] Services"
    - 3 hero pricing cards (top platforms/categories)
    - Each card: Starting price + USP list + CTA + Reviews count
[10-13] PRODUCT GRIDS (80%) — Templated repeat per Entity:
    - Instagram / TikTok / YouTube / Facebook (or equivalent)
    - Each grid: H2 logo + Description + Tab nav + Featured products
    - Multi-tier pricing (1K, 5K, 10K, 50K, 100K, 250K, 500K)
    - Apply Multi-Tier Pricing Pattern
[14] EDUCATIONAL — H2 #2 (60%):
    - "How [Entity] Work?" (plural, reseller/developer audience)
    - 6 conceptual mechanisms (System architecture)
    - Tab navigation: API Order | Payment & Billing
    - DUAL-AUDIENCE MACRO-CONTEXT REINFORCEMENT pattern
[15] PRICE CALCULATOR (100%) — Interactive function:
    - Platform select → Service select → Quantity select
    - Live price calculation
    - CTA "Purchase" / "Order Now"
[16] RESELLER/B2B CTA BANNER (40%):
    - Secondary persona invitation
    - "Free Register" or equivalent
[17] EDUCATIONAL — Cost Factors (60%):
    - H3: "Cost Factors for [Entity] Services"
    - 8 factor bullets
[18] TEAM SECTION (40%):
    - H2: "Best [Entity] Specialists"
    - 5 team member cards: photo + name + role + bio
[19] NEWSLETTER (20%):
    - Subscribe form
[20] FAQ — Multi-tab Encyclopedia (60%):
    - H2: "Frequently Asked Questions" (DECORATIVE)
    - Tab navigation: 4 topic clusters
    - Each tab has multiple H2 (real macro-contexts)
    - DECORATIVE-SEMANTIC SEPARATION pattern
[21] FOOTER (5-10%) — Services | Sign up | Sign in
[22] MOBILE PERSISTENT NAV (mobile only) — Bottom fixed nav
```

---

## Worked Example: morethanpanel.com

morethanpanel.com is a Koray-built template demonstrating all 6 advanced patterns. Outline mapping:

| Section | Pattern Applied | Reference |
|---|---|---|
| Centerpiece L1 (above-fold) | Multi-Layer Centerpiece (L1) + Trust Stacking (Layers 1-2) | `multi-layer-centerpiece.md` + `trust-stacking-hierarchy.md` |
| Reviews block (Section 4) | Trust Stacking (Layers 3-5) | `trust-stacking-hierarchy.md` |
| Live stats bar (Section 5) | Real-Time Function Validators + Trust Stacking (Layer 6) | `real-time-function-validators.md` |
| H2 "How does SMM Panel Work?" (Section 6) | Dual-Audience pattern (audience #1: end user) | `dual-audience-macro-context.md` |
| Advantages 12-list (Section 7) | Templated Visual Elements + Search Journey Compression | `templated-visual-elements.md` + `search-journey-compression.md` |
| Centerpiece L2 (Pricing — Section 9) | Multi-Layer Centerpiece (L2) + Multi-Tier Pricing | `multi-layer-centerpiece.md` + `multi-tier-pricing-pattern.md` |
| Product grids 4 platforms (Sections 10-13) | Templated Visual Elements + Block Chunk Design | `templated-visual-elements.md` + `block-chunk-design.md` |
| H2 "How SMM Panels Work?" (Section 14) | Dual-Audience pattern (audience #2: reseller) | `dual-audience-macro-context.md` |
| Price Calculator (Section 15) | Real-Time Function Validators (Calculator type) | `real-time-function-validators.md` |
| Team section (Section 18) | Trust Stacking (Layer 7) | `trust-stacking-hierarchy.md` |
| FAQ multi-tab (Section 20) | Decorative-Semantic Heading + Search Journey Compression | `decorative-semantic-heading.md` |

---

## Implementation Checklist

### Pre-design
- [ ] Identify central entity of site
- [ ] List 2-3 buyer personas with intent overlap analysis
- [ ] Map central entity → 7 dimension coverage requirement
- [ ] Decide compress (1 URL) vs split (multi URL) — see `search-journey-compression.md`

### Design phase
- [ ] Plan 2-3 centerpiece zones with supporting blocks between
- [ ] Define 1 master template for repeated sections (per platform/category)
- [ ] Identify dual-audience H2 pair if applicable
- [ ] Plan 7-layer trust positioning
- [ ] Spec live function (1 minimum: notification or counter)

### Build phase
- [ ] H1 ≤4 entities, no number stuffing
- [ ] Each H2 block has ≥4/5 elements (heading + L0 + body + visual + functional)
- [ ] FAQ section uses Decorative-Semantic Separation
- [ ] Mobile bottom persistent nav implemented
- [ ] Templated sections repeat ≥3 times consistently

### Audit phase
- [ ] Run all 7 v2.0 checklists from main SKILL.md
- [ ] Verify no centerpiece stacking (≥1 supporting block between)
- [ ] Verify dual-audience H2 has distinct visual treatment
- [ ] Verify decorative H2 not nesting real macro-contexts as H3
- [ ] Verify RankLab factors optimization

---

## Application to sample projects (ví dụ)

### APOHAIR Homepage (B2B Hair Manufacturing)

**Hybrid page applicability:** YES — site has 3 personas (OEM brand owner, wholesaler, end retailer)

**Key adaptations:**
- Centerpiece L1: "Hair Extension Manufacturer Vietnam" + Manufacturing authority + WhatsApp CTA
- Centerpiece L2: Multi-tier wholesale pricing (1 kit / 10 kits / 100 kits / OEM)
- Templated sections: Tape-in / Weft / Closures / Frontals (4 product lines)
- Dual-audience H2: "How OEM Manufacturing Works?" + "How Hair Wholesale Distribution Works?"
- Live function: Production capacity counter ("X kits manufactured this month")
- Trust stack: Certificates + Reviews + Press + Client logos + Factory video + Specs + Team

### TAG Claude A-Z Course Landing

**Hybrid page applicability:** YES — site has 2 personas (individual learner, team training buyer)

**Key adaptations:**
- Centerpiece L1: Course definition + outcome promise + early-bird CTA
- Centerpiece L2: Module pricing tiers (Self-paced / Mentorship / Cohort)
- Templated sections: 8-10 modules, each with consistent visual template
- Dual-audience H2: "How is the Claude A-Z Course Structured?" + "How Claude A-Z Mentorship Works?"
- Live function: Countdown to next cohort + spots remaining counter
- FAQ: 15-20 PQ in 4 tabs (Prerequisites | Curriculum | Outcomes | Logistics)

### GTV Service Page Semantic SEO

**Hybrid page applicability:** PARTIAL — single primary persona but with depth/breadth need

**Key adaptations:**
- Single centerpiece (service page pattern primary)
- BUT include templated case study sections (Vinamilk / Bamboo / Kotex consistent template)
- Dual-audience H2: "How Semantic SEO Service Works?" (decision maker) + "How GTV's Semantic SEO Methodology Works?" (specialist)
- Live function: Real-time client traffic dashboard widget (anonymized)

---

## Anti-Patterns

❌ **Stacking 2 centerpieces directly without supporting block between** — dilutes attention
❌ **Inconsistent templates across product/service sections** — Google fails to learn pattern
❌ **Nesting real macro-contexts as H3 under decorative H2** — kills featured snippet potential
❌ **Same phrasing for dual-audience H2** — cannibalization risk
❌ **No live function on hybrid page** — missing semantic intent signal
❌ **Trust signals scattered randomly** — fails to build cumulative trust impression
❌ **Single-tier pricing on hybrid page** — misses comparison engagement opportunity
❌ **Skipping search journey dimensions** — Google sees partial topical coverage

---

## Cross-References

- `multi-layer-centerpiece.md` — Centerpiece L1/L2/L3 detail
- `templated-visual-elements.md` — Template repetition rules
- `block-chunk-design.md` — Per-section block structure
- `dual-audience-macro-context.md` — H2 pair design
- `decorative-semantic-heading.md` — FAQ/tab handling
- `search-journey-compression.md` — Compress vs split decision
- `real-time-function-validators.md` — Live function spec
- `trust-stacking-hierarchy.md` — 7-layer trust position
- `multi-tier-pricing-pattern.md` — Pricing card design
- `ranklab-factors.md` — RankLab optimization
