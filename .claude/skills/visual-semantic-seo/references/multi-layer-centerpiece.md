# Multi-Layer Centerpiece (v2.0)

**When to use:** Hybrid pages, homepage hubs, multi-intent landing pages where single centerpiece is insufficient.

**Core principle:** A page can have **2-3 centerpieces stacked vertically**, each with supporting blocks between them. Each centerpiece serves a distinct funnel position.

---

## Why Single Centerpiece Fails for Hybrid Pages

The original Centerpiece Annotation framework (Google Patent US8949242B1) describes **single centerpiece** = the area Google identifies as "main content" with 100% ranking weight.

**This works for:**
- Service pages (1 service, 1 conversion goal)
- Product pages (1 product, 1 buy CTA)
- Article pages (1 topic, 1 reader takeaway)

**This breaks for:**
- Homepage hubs serving multiple intents
- Hybrid pages combining e-commerce + informational + service
- Sites with multi-tier conversion funnel (free trial + product purchase + reseller signup)

---

## Multi-Layer Centerpiece Architecture

### Layer 1 — Discovery Centerpiece (Above-the-Fold)

**Position:** Immediately after header, takes full above-the-fold space.

**Goal:** Answer "What is this site/service?" and capture user attention with primary value proposition.

**Required elements:**
- H1 declaring central entity + primary search query coverage
- L0 definition paragraph (40-80 words) — Answer-First
- 4-6 trust attributes (mini-bullets visible without scroll)
- Demonstrative annotation (CEO/team video OR product screenshot)
- Primary CTA (highest-intent action)
- Optional: Inline action form for low-friction capture

**Weight:** 100%

### Layer 2 — Conversion Centerpiece (Mid-Page)

**Position:** After 2-3 supporting blocks (reviews, stats, education).

**Goal:** Convert user who has built initial trust. Compare options for decision.

**Required elements:**
- H2 declaring decision/comparison framing ("Best and Cheapest [Entity]" / "Choose Your [Plan]")
- 3 hero pricing/option cards (templated)
- Each card: clear price + USP list + CTA + reviews count
- Visual differentiation: highlight "Best Offer" or "Most Popular"

**Weight:** 100%

### Layer 3 — Per-Entity Centerpieces (Templated Repeat)

**Position:** After Layer 2 conversion. Multiple instances, one per entity (platform/category/service line).

**Goal:** Deep-dive into specific entity that user expressed interest in.

**Required elements per Layer 3 instance:**
- H2 with entity logo/icon (visual identifier)
- Description paragraph
- Tab navigation (sub-categories within entity)
- Featured products grid
- Multi-tier pricing cards
- "Buy Now" CTAs

**Weight:** 80% per instance (slightly less than primary centerpieces because they're parallel options)

---

## Spacing Rules

### Critical Rule 1: Supporting Block Between Centerpieces

**NEVER stack 2 centerpieces directly.** Require minimum 1 supporting block between Layer 1 and Layer 2.

**Why:** 
- Visually: User needs cognitive break — direct stacking creates "wall of CTAs" feeling
- Semantically: Google needs to detect distinct semantic units
- Behaviorally: Trust must build before second conversion ask

**Required between Layer 1 and Layer 2:**
- Reviews block (multi-source)
- Live stats bar
- Educational explainer (How it Works)
- Trust signals (press, certifications)

### Critical Rule 2: Distinct Visual Treatment

Each centerpiece layer must have **distinct visual treatment** so Google + user identify them as separate units:

| Layer | Visual Treatment Suggestion |
|---|---|
| Layer 1 | Hero background (gradient/image), H1 large (48px+), centered or left-aligned with image right |
| Layer 2 | Lighter background, card-based grid layout, hover states on cards |
| Layer 3 | Logo/icon header for each entity, tab navigation, dense product grid |

### Critical Rule 3: CTA Hierarchy

Centerpiece layers should have **clear CTA hierarchy**:

- Layer 1: Primary CTA (e.g., "Start Free Trial", "Get Quote")
- Layer 2: Comparison CTA (e.g., "Get Started" per option)
- Layer 3: Specific purchase CTA (e.g., "Buy 5K Followers")

If all 3 layers compete for same conversion → user paralysis. Stagger conversion intent.

---

## Decision Matrix: How Many Centerpiece Layers?

| Page Type | Layers Needed | Rationale |
|---|---|---|
| Single-service B2B page | 1 | One entity, one decision |
| Product detail (PDP) | 1 | Single product focus |
| Category page (PLP) | 1 | Browse intent unified |
| Homepage hub (multi-product) | 2-3 | Multi-intent funnel |
| Course landing (multi-tier) | 2 | Pricing tier decision |
| Hair manufacturer homepage | 2-3 | Multi-product line + multi-buyer-tier |
| News/magazine homepage | 1 (per top story) | Editorial focus |

---

## Per-Entity Centerpiece (Layer 3) Detail

When site has multiple parallel entities (4 social platforms, 5 product lines, 6 course modules), Layer 3 should be **templated**:

### Template Slots

```
[Layer 3 — Entity X]
├─ H2: "Best [Entity X] Services" + Logo
├─ Description paragraph (60-100 words)
├─ Tab navigation (sub-types within entity)
├─ Featured products grid (5 products)
│   └─ Each product: name + reviews + price + features + CTA + start time
├─ Multi-tier pricing section
│   └─ Tiers: 1K, 5K, 10K, 50K, 100K, 250K, 500K
└─ Closing image (entity-themed visual)
```

### Repetition Rule

If you have 4 entities, repeat this template 4 times **identically structured**. Google's WebFormer detects pattern after 3+ repetitions and treats site as authoritative for entity type.

**Anti-pattern:** Entity 1 has 5 products, Entity 2 has 3 products, Entity 3 has 7 products. Inconsistent template = pattern not detected.

---

## Application Examples

### morethanpanel.com (Reference Implementation)

| Layer | Section | Implementation |
|---|---|---|
| L1 | Above-fold | H1 "Best SMM Panel" + Definition + Trust + Login form + Free Trial CTA |
| L2 | Pricing comparison | "Best and Cheapest SMM Services" + 3 hero cards (Instagram/TikTok/YouTube) |
| L3 × 4 | Per-platform grids | Instagram grid + TikTok grid + YouTube grid + Facebook grid (templated) |

**Spacing:** Between L1 and L2 — Reviews block + Live stats + How-it-works = 3 supporting blocks
**Spacing:** Between L2 and L3 first instance — None (acceptable since L2 is shorter and L3 instances are parallel)

### APOHAIR Homepage (Application Plan)

| Layer | Section | Implementation |
|---|---|---|
| L1 | Above-fold | H1 "Hair Extension Manufacturer Vietnam" + B2B value props + WhatsApp CTA + Wholesale catalog request form |
| L2 | Pricing comparison | "Wholesale Tier Pricing" + 3 cards (1 kit retail / 10 kits wholesale / 100+ kits OEM) |
| L3 × 4 | Per-product line | Tape-in / Weft / Closures / Frontals (templated) |

**Spacing:** Between L1 and L2 — Manufacturing process video + Quality certifications + Client testimonials = 3 supporting blocks

### TAG Claude A-Z (Application Plan)

| Layer | Section | Implementation |
|---|---|---|
| L1 | Above-fold | H1 "Claude A-Z: AI Workflow for [Audience]" + Outcome promise + Early-bird CTA |
| L2 | Pricing comparison | "Choose Your Path" + 3 cards (Self-paced / Mentorship / Cohort) |
| L3 × 8-10 | Per-module deep-dive | Each module templated section (intro + outcomes + lessons + practice + outcomes) |

---

## Anti-Patterns

❌ **2 centerpieces stacked directly without supporting block** — visual wall, no breathing room
❌ **All centerpieces compete for same conversion** — user paralysis
❌ **Inconsistent Layer 3 templates** — Google fails to learn pattern (see `templated-visual-elements.md`)
❌ **Layer 1 weak (no clear value prop)** — entire page collapses
❌ **Skipping Layer 2 on hybrid page** — direct from discovery to product grid feels jarring
❌ **More than 3 centerpieces** — too many "main" zones dilutes everything
❌ **Layer 1 missing demonstrative annotation** — purely text, no visual anchor

---

## Validation Checklist

When auditing multi-layer centerpiece implementation:

- [ ] Layer 1 above-fold with H1 + Definition + Trust + Primary CTA
- [ ] ≥1 supporting block between Layer 1 and Layer 2
- [ ] Layer 2 has 3 comparison options (not 2, not 4+)
- [ ] Layer 2 cards templated (same structure each)
- [ ] Layer 3 instances templated identically (≥3 repetitions)
- [ ] Each layer has distinct visual treatment
- [ ] CTA hierarchy clear (no competition)
- [ ] Mobile: layers stack appropriately (Layer 2 cards stack vertically)
- [ ] No more than 3 centerpiece layers total

---

## Cross-References

- `centerpiece-annotation.md` — Original single-centerpiece principles
- `hybrid-page-pattern.md` — When multi-layer applies
- `templated-visual-elements.md` — Layer 3 repetition rules
- `multi-tier-pricing-pattern.md` — Layer 2 pricing card design
