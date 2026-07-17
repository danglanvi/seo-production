# Multi-Tier Pricing Pattern (v2.0)

## Contents

- [The 4 Mandatory Elements per Pricing Card](#the-4-mandatory-elements-per-pricing-card)
- ["Best Offer" Badge Positioning](#best-offer-badge-positioning)
- [Tier Sequencing Logic](#tier-sequencing-logic)
- [Mobile Responsive Pattern](#mobile-responsive-pattern)
- [Schema Markup](#schema-markup)
- [Application Examples](#application-examples)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

**When to use:** Conversion-focused pages with multi-tier pricing — e-commerce categories, hybrid pages, course landings, B2B service tiers, SaaS pricing.

**Core principle:** Pricing card visual semantic must include 4 mandatory elements + strategic "Best Offer" badge positioning + tier sequencing logic that drives conversion.

---

## The 4 Mandatory Elements per Pricing Card

Every pricing tier card must display ALL 4 elements clearly:

### Element 1: Original Price (Anchor)

**Purpose:** Establish reference price so user perceives value.

**Implementation:**
- Display original/list price with strikethrough
- Position above or beside the discounted price
- Smaller font than current price (suggests "old" anchor)
- Color: muted gray

**Example:**
```
~~$2.40~~
$1.24
```

### Element 2: Discounted/Current Price

**Purpose:** The actual amount user pays. Most prominent element.

**Implementation:**
- Largest font in the card (28-48px)
- Bold weight
- Brand primary color
- Currency symbol clearly visible
- Per-unit clarification ("per 1K", "per month", "one-time")

**Example:**
```
$1.24
per 1,000 followers
```

### Element 3: Quantity / Tier Specification

**Purpose:** Tell user exactly what they get for the price.

**Implementation:**
- Clear quantity ("1,000 followers", "10 sessions", "5 mentor calls")
- Time period if applicable ("per month", "lifetime access")
- Position: below price, smaller font (14-16px)
- Color: secondary text color

**Example:**
```
1,000 Instagram Followers
Delivery: 0-6 hours
```

### Element 4: Savings Callout

**Purpose:** Quantify the deal so user perceives concrete benefit.

**Implementation:**
- "Save $X" or "X% off" badge
- Position: top-right corner of card OR below price
- Color: contrast accent (red/orange for urgency, green for savings)
- Size: 12-14px, bold

**Example:**
```
[Save 48%] (badge top-right)
OR
$0.86 saved (text below price)
```

---

## "Best Offer" Badge Positioning

### The Conversion Psychology

Users scanning pricing tiers naturally look for "the right choice" — they want guidance. The "Best Offer" badge serves as that guidance.

### Optimal Position: Tier #2 or Tier #3 of 5

In a 5-tier pricing structure (e.g., 1K / 5K / 10K / 50K / 100K), the "Best Offer" badge typically goes on:
- **Tier #2** (5K) for budget-conscious markets
- **Tier #3** (10K) for value-conscious markets

This is because:
- Tier #1 feels too small (commitment phobia)
- Tier #5 feels too expensive (budget concern)
- Middle tiers feel "smart choice"

### Visual Implementation

```
┌────────────┐   ┌────────────┐   ┌────────────┐
│            │   │ ★ BEST     │   │            │
│  Tier 1    │   │  OFFER     │   │  Tier 3    │
│            │   │            │   │            │
│  ~~$5~~    │   │  ~~$15~~   │   │  ~~$30~~   │
│  $4.20     │   │  $11.99    │   │  $24.50    │
│  1K        │   │  5K        │   │  10K       │
│  Save 16%  │   │  Save 20%  │   │  Save 18%  │
└────────────┘   └────────────┘   └────────────┘
                  [highlighted    
                   border/bg]    
```

The "Best Offer" tier should also have:
- Distinct visual treatment (border accent, slightly larger card, background tint)
- "Most Popular" or "Recommended" optional sub-label
- Stronger CTA button (filled vs outlined)

---

## Tier Sequencing Logic

### Optimal Tier Count: 5-7 tiers

**Why 5-7:**
- 3 tiers: too few options, feels limiting
- 4 tiers: forces designer choice between budget vs premium balance
- **5-7 tiers: sweet spot** — gives user real choice, fits visual layout
- 8+ tiers: choice paralysis, harder to scan

### Standard Tier Sequence Example

For e-commerce volume tiers:
- Tier 1: 1,000 (entry, low commitment)
- Tier 2: 5,000 (smart starter)
- Tier 3: 10,000 (BEST OFFER — middle value)
- Tier 4: 50,000 (volume buyer)
- Tier 5: 100,000 (power user)
- Tier 6: 250,000 (enterprise lite)
- Tier 7: 500,000 (enterprise)

### Standard Tier Sequence Example (Service)

For B2B service tiers:
- Tier 1: Self-service (lowest commitment)
- Tier 2: Starter (small team)
- Tier 3: Professional (BEST OFFER — most teams)
- Tier 4: Business (mid-market)
- Tier 5: Enterprise (custom)

### Standard Tier Sequence Example (Course)

For course tiers:
- Tier 1: Self-paced (cheapest, async)
- Tier 2: Mentorship (BEST OFFER — best value)
- Tier 3: Cohort (premium, most expensive)

For courses, 3 tiers is acceptable because the structural difference is significant (delivery method changes).

---

## Mobile Responsive Pattern

### Stack Order on Mobile

When pricing cards stack vertically on mobile, place the "Best Offer" tier **at the top**:

```
[Mobile View]
┌────────────────┐
│ ★ BEST OFFER   │
│ Tier 3 (10K)   │
│ $24.50         │
└────────────────┘

┌────────────────┐
│ Tier 2 (5K)    │
│ $11.99         │
└────────────────┘

┌────────────────┐
│ Tier 1 (1K)    │
│ $4.20          │
└────────────────┘

[More tiers below...]
```

**Rationale:** On mobile, user sees first card → "Best Offer" highlighted → less scrolling to discover the recommended tier.

### Mobile Card Spacing

- Vertical gap between cards: 16-24px
- Card internal padding: 20-32px
- Touch-friendly CTA buttons (min 44px tap target)

---

## Schema Markup

### Product + Offer Markup

For e-commerce pricing tiers:

```html
<div itemscope itemtype="https://schema.org/Product">
  <h3 itemprop="name">1,000 Instagram Followers</h3>
  
  <div itemscope itemprop="offers" itemtype="https://schema.org/Offer">
    <span itemprop="priceCurrency" content="USD">$</span>
    <span itemprop="price" content="1.24">1.24</span>
    <link itemprop="availability" href="https://schema.org/InStock"/>
    <meta itemprop="priceValidUntil" content="2026-12-31"/>
  </div>
  
  <div itemprop="aggregateRating" itemscope itemtype="https://schema.org/AggregateRating">
    <span itemprop="ratingValue">4.8</span>
    <span itemprop="reviewCount">1549</span>
  </div>
</div>
```

### Service + Offer Markup

For service tiers:

```html
<div itemscope itemtype="https://schema.org/Service">
  <h3 itemprop="name">Semantic SEO Professional</h3>
  
  <div itemscope itemprop="offers" itemtype="https://schema.org/Offer">
    <span itemprop="priceCurrency" content="USD">$</span>
    <span itemprop="price" content="2500">2,500</span>
    <span itemprop="priceSpecification">per month</span>
  </div>
</div>
```

---

## Application Examples

### morethanpanel.com (Reference Implementation)

**Tier Structure (per platform):**

For Instagram followers:
- 100 followers — $0.43
- 500 followers — $0.65
- 1,000 followers — $1.24 ← BEST OFFER
- 5,000 followers — $6.20
- 10,000 followers — $12.40
- 50,000 followers — $61.99
- 100,000 followers — $123.99
- 250,000 followers — $289.99
- 500,000 followers — $499.99

**4 Elements present:**
- Original price: ~~$2.40~~ shown above current
- Discounted price: $1.24 (large, bold)
- Quantity: "1,000 Instagram Followers — Delivery 0-6 hours"
- Savings callout: "Save 48%" badge

**"Best Offer" positioning:** Typically on 1,000 or 5,000 tier (entry-level conversion friendly)

### APOHAIR Wholesale Tier Implementation

**Tier Structure:**

```
Tier 1: Sample (1 kit) — $35/kit
Tier 2: Retail (5-10 kits) — $28/kit
Tier 3: Wholesale (10-50 kits) — $22/kit ← BEST OFFER
Tier 4: Bulk (50-200 kits) — $18/kit
Tier 5: OEM Volume (200+ kits) — $15/kit + customization
```

**Per card:**
- Original price: ~~$35~~ (anchor)
- Tier price: $22 (current)
- Quantity: "10-50 kits per order"
- Savings: "Save 37%"
- BEST OFFER on Tier 3 (wholesale typical for distributors)

### TAG Course Tier Implementation

**Tier Structure:**

```
Tier 1: Self-Paced — 4,997,000 VND (existing course price)
Tier 2: Mentorship — 9,997,000 VND ← BEST OFFER
Tier 3: Cohort + Certification — 16,679,000 VND
```

**Per card:**
- Original price: List price (anchor)
- Tier price: Current promo
- Quantity: "Lifetime access" / "12 weeks mentorship" / "8 weeks cohort"
- Savings: Percent off
- BEST OFFER on Tier 2 (most balance of price + delivery quality)

### GTV Service Tier Implementation

**Tier Structure:**

```
Tier 1: Audit (One-time) — $1,500
Tier 2: Starter SEO (3-month) — $2,500/mo
Tier 3: Professional SEO (6-month) — $3,500/mo ← BEST OFFER
Tier 4: Enterprise (Custom) — Contact for quote
```

**Per card:**
- Original price: ~~$4,500~~ (for retainer pricing if discounted)
- Tier price: Per-month investment
- Quantity: "Includes X articles, Y backlinks, Z hours consultation"
- Savings: "Save 22%" badge
- BEST OFFER on Tier 3 (most clients land here)

---

## Anti-Patterns

❌ **Single tier (no comparison)** — Misses comparison engagement opportunity
❌ **3 tiers when 5-7 would help** — Forces over-simplification of options
❌ **No "Best Offer" badge** — User has no guidance, defaults to cheapest
❌ **Best Offer on extreme tier** (Tier 1 or last) — Doesn't drive middle-tier conversion
❌ **Missing original price anchor** — User has no reference for value perception
❌ **Vague quantity** ("More features", "Premium") — Should be specific
❌ **Hidden total cost** — "$1.24" alone without "/1K followers" confuses users
❌ **Mobile cards too tall** — Each card needs scroll to see → users abandon
❌ **No CTA differentiation per tier** — All buttons same → "Best Offer" CTA should be more prominent
❌ **Best Offer changes on every page reload** — Manipulative testing damages trust

---

## Validation Checklist

For pricing tier implementation:

- [ ] All 4 mandatory elements present (original + current + quantity + savings)
- [ ] 5-7 tiers (3 if structurally distinct service tiers)
- [ ] "Best Offer" badge on Tier #2 or #3 of 5 (or Tier #2 of 3)
- [ ] Best Offer tier has distinct visual treatment
- [ ] Best Offer tier CTA more prominent (filled button vs outlined)
- [ ] Mobile: cards stack with Best Offer at top
- [ ] Schema markup (Product/Service + Offer) implemented
- [ ] Original price anchor visible (with strikethrough)
- [ ] Quantity unit clear ("per 1K", "per month", "lifetime")
- [ ] Savings callout uses concrete number/percentage
- [ ] Tap targets ≥44px on mobile

---

## Cross-References

- `multi-layer-centerpiece.md` — Pricing centerpiece is Layer 2 in multi-layer architecture
- `hybrid-page-pattern.md` — Hybrid pages always include pricing tiers
- `templated-visual-elements.md` — Pricing cards within product sections must be templated
- `real-time-function-validators.md` — Live "spots remaining" complements pricing cards
- `trust-stacking-hierarchy.md` — Reviews near pricing build trust for conversion
