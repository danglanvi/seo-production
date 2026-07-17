# Persona Zone Visual Treatment (v2.1)

## Contents

- [Why Persona Zones Matter](#why-persona-zones-matter)
- [Distinguishing Persona Zone vs Dual-Audience Macro-Context](#distinguishing-persona-zone-vs-dual-audience-macro-context)
- [The 6-Element Persona Zone Visual Spec](#the-6-element-persona-zone-visual-spec)
- [Element 1 — Color Accent](#element-1-color-accent)
- [Element 2 — Background Treatment](#element-2-background-treatment)
- [Element 3 — Imagery Type](#element-3-imagery-type)
- [Element 4 — Layout Density](#element-4-layout-density)
- [Element 5 — Icon Set / Illustrations](#element-5-icon-set-illustrations)
- [Element 6 — CTA Wording + Style](#element-6-cta-wording-style)
- [Persona Zone Architecture Patterns](#persona-zone-architecture-patterns)
- [Application Examples](#application-examples)
- [Persona Zone Design Rules](#persona-zone-design-rules)
- [Visual Pacing Across Persona Zones](#visual-pacing-across-persona-zones)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

**When to use:** Hybrid pages serving 2+ distinct buyer personas with intent overlap. Each persona needs identifiable "zone" within the page so user feels content speaks to them specifically.

**Core principle:** Same page, multiple personas, distinct visual zones. Each zone has signature visual cue that lets target persona identify "this section is for me" within 3 seconds of scrolling into view.

---

## Why Persona Zones Matter

Hybrid pages serve multiple personas. Without persona zones:

1. **Generic content feels like nothing** — trying to speak to everyone speaks to no one
2. **High-value persona buries** — small buyer content same visual weight as enterprise content
3. **User skips relevant section** — without visual cue, user misses content meant for them

**Solution:** Allocate distinct visual treatment per persona, allowing scan-and-identify within page flow.

---

## Distinguishing Persona Zone vs Dual-Audience Macro-Context

These are **related but distinct** patterns:

| Pattern | Focus | Implementation |
|---|---|---|
| **Dual-Audience Macro-context** | Same TOPIC, 2 personas | 2 H2 with phrasing variation explaining same concept |
| **Persona Zone Visual Treatment** | Same PAGE, 2-3+ personas with distinct sections | Distinct visual zones per persona throughout page |

**Combine them:** Persona zones can include dual-audience H2 pairs as sub-elements.

---

## The 6-Element Persona Zone Visual Spec

Each persona zone should differentiate across these 6 elements:

| Element | Purpose | Example variations |
|---|---|---|
| **1. Color accent** | Instant visual identification | Brand primary / secondary / tertiary |
| **2. Background treatment** | Section-level distinction | White / tinted / patterned |
| **3. Imagery type** | Persona-specific scene | Salon photo / warehouse / brand packaging |
| **4. Layout density** | Content depth signal | Dense (data-heavy) / spacious (lifestyle) |
| **5. Icon set / illustrations** | Persona-specific symbology | Storefront / truck / luxury packaging |
| **6. CTA wording + style** | Action specific to persona | "Order Sample" / "Get Quote" / "Discuss OEM" |

---

## Element 1 — Color Accent

### Pattern: Persona-Color Mapping

Assign brand color variant to each persona:

```
Brand primary (e.g., Apohair blue):
  → Persona A (small/individual buyer — salon owner)
  → Background: white with primary color accents

Brand secondary (e.g., warm teal):
  → Persona B (mid buyer — distributor)
  → Background: light teal tint with secondary accents

Brand tertiary (e.g., gold/premium):
  → Persona C (high-tier — brand owner / OEM)
  → Background: dark with gold accents (premium feel)
```

### Implementation

- Section header underline color = persona color
- Card border / icon color = persona color
- CTA button color = persona color
- Section background: subtle tint of persona color OR white-with-accent

**Anti-pattern:** Using random colors not connected to brand system → confuses brand identity.

---

## Element 2 — Background Treatment

### Pattern: Visual Texture Per Persona

```
Persona A (Salon owner — entry buyer):
  Background: Plain white OR very subtle gray
  Texture: Clean, accessible, friendly
  Mood: Approachable

Persona B (Distributor — operations buyer):
  Background: Light-tinted (cool blue/gray)
  Texture: Slight grid pattern OR data-style
  Mood: Professional, organized

Persona C (OEM/Brand owner — premium buyer):
  Background: Dark with subtle gradient
  Texture: Sophisticated, minimal
  Mood: Premium, exclusive
```

### Visual Section Boundary

Use background change to signal "you've entered a different persona zone":

```
[Persona A zone — white BG]
   ↓
[Bridge section — neutral]
   ↓
[Persona B zone — light tinted BG]
   ↓
[Bridge section — neutral]
   ↓
[Persona C zone — dark premium BG]
```

---

## Element 3 — Imagery Type

### Pattern: Persona-Lifestyle Imagery

Each persona zone uses photography matching their world:

```
Persona A (Salon owner):
  Imagery: Salon environment, customer chair, hair styling action
  Tone: Warm, action-oriented, individual scale

Persona B (Distributor):
  Imagery: Warehouse, logistics, multi-region shipping, B2B meeting
  Tone: Operational, scale, multi-stakeholder

Persona C (OEM/Brand owner):
  Imagery: Custom packaging, branded products on shelves, manufacturing line for private label
  Tone: Premium, brand-focused, customization
```

### Photo Sourcing Rule

- Real photography from clients in each persona category (with permission)
- Avoid stock photos that feel generic
- Each photo should make target persona think "that's my world"

**Anti-pattern:** Same hero image across all persona zones — fails differentiation entirely.

---

## Element 4 — Layout Density

### Pattern: Density Reflects Buyer Sophistication

```
Persona A (Entry buyer):
  Density: Spacious, lifestyle-focused
  Content blocks: Larger padding, more whitespace
  Information depth: Moderate (not overwhelming)
  Example: 2-3 talking points per block, with photo

Persona B (Mid buyer):
  Density: Medium, data-balanced
  Content blocks: Standard padding, organized grid
  Information depth: Comprehensive (operational data)
  Example: Tables, comparison matrices, specs

Persona C (Sophisticated buyer):
  Density: Dense, capability-focused
  Content blocks: Tighter padding, technical specs
  Information depth: Deep (technical capabilities)
  Example: Capability matrices, white-label specs, ROI calculations
```

---

## Element 5 — Icon Set / Illustrations

### Pattern: Persona-Symbology

```
Persona A icons:
  - Storefront / Salon chair
  - Single product
  - Personal handshake
  - Customer

Persona B icons:
  - Warehouse / Truck
  - Multi-region map
  - Network nodes
  - Logistics chain

Persona C icons:
  - Custom packaging
  - Branded product display
  - Production line
  - White-label customization
```

### Icon Style Consistency

Even with persona-specific symbols, maintain:
- Same line weight across all icons
- Same color rules (per persona)
- Same level of detail
- Same visual style (line / filled / 3D)

---

## Element 6 — CTA Wording + Style

### Pattern: Persona-Specific Action Language

```
Persona A CTA:
  Primary: "Request Sample" / "Order Trial Pack"
  Secondary: "Talk to Salon Specialist"
  Style: Friendly, low-commitment

Persona B CTA:
  Primary: "Get Wholesale Quote" / "Explore Distribution Program"
  Secondary: "Schedule Distribution Call"
  Style: Operational, clear-value

Persona C CTA:
  Primary: "Discuss OEM Project" / "Request Capability Brief"
  Secondary: "Speak with OEM Strategist"
  Style: Strategic, capability-focused
```

### CTA Visual Style Per Persona

- Persona A: Filled button, brand primary color, friendly icon
- Persona B: Outlined OR filled button, brand secondary, operational icon
- Persona C: Filled button, premium color (gold/dark), sophisticated icon

---

## Persona Zone Architecture Patterns

### Pattern 1: Sequential Zones (Most Common)

```
[Zone for Persona A — first]
[Bridge section — neutral]
[Zone for Persona B — second]
[Bridge section — neutral]
[Zone for Persona C — third]
```

**When to use:** When personas have natural progression (small buyer → mid buyer → enterprise) OR when each persona has clear "graduation path"

**Real estate split:** 33% / 33% / 33% OR weighted by persona priority

### Pattern 2: Tabbed Zones (Compact)

```
[Hero section]

[Tab navigation: For Salon | For Distributors | For OEM Brands]

[Selected tab content — full width, distinct styling per tab]

[Common sections below tabs]
```

**When to use:** When user needs to self-select persona quickly without scrolling

**Risk:** SEO concern — tabs hide content from initial render. Solution: Use CSS show/hide, ensure all content in DOM. See `decorative-semantic-heading.md` for tab navigation rules.

### Pattern 3: Side-by-Side Comparison Zone (Decision-Oriented)

```
[3-column layout]
[Persona A column]    [Persona B column]    [Persona C column]
"For Salons"          "For Distributors"    "For Brand Owners"
[features list]       [features list]       [features list]
[CTA per persona]     [CTA per persona]     [CTA per persona]
```

**When to use:** When user is comparing which persona path to take OR when offering tier upgrade visualization

### Pattern 4: Embedded Persona Cards (Lightweight)

```
[Generic content section]

[Embedded persona row: 3 cards horizontal]
"Are you a salon owner?"   "Distributor?"   "Brand owner?"
[Brief value prop]         [Brief value prop] [Brief value prop]
[CTA per persona]          [CTA per persona]  [CTA per persona]

[Continue generic content]
```

**When to use:** When generic content dominant, persona personalization secondary

---

## Application Examples

### APOHAIR Homepage — 3 Persona Zones (Sequential Pattern)

**Persona A Zone — Salon Owner (entry buyer)**
- Position: After hero, around S6 product lines
- Color accent: Brand primary (warm tone)
- Background: White with subtle accent
- Imagery: Salon environment, hair styling action
- Layout: Spacious, photo-heavy
- Icons: Salon chair, single product, personal service
- CTA: "Request Sample (200g MOQ)"

**Persona B Zone — Distributor (mid buyer)**
- Position: Around S9 wholesale program
- Color accent: Secondary professional tone
- Background: Light-tinted
- Imagery: Warehouse, multi-region shipping, container
- Layout: Medium density, table-organized
- Icons: Truck, network, logistics
- CTA: "Get Wholesale Distribution Quote"

**Persona C Zone — OEM/Brand Owner (premium buyer)**
- Position: Around S11 OEM/ODM
- Color accent: Premium tone (deeper / gold)
- Background: Dark with gradient
- Imagery: Custom packaging, branded display, private-label samples
- Layout: Dense, capability-focused
- Icons: Custom packaging, branded display, manufacturing
- CTA: "Discuss OEM Project"

### morethanpanel.com — 2 Persona Zones (Embedded Pattern)

**Persona A Zone — End-User Buyer**
- Position: Educational H2 "How does SMM Panel Work?" — end-user view
- Format: 5 visual steps with friendly icons
- Embedded: Video tutorial
- Bright friendly visual treatment

**Persona B Zone — Reseller / Developer**
- Position: H2 "How SMM Panels Work?" — reseller view
- Format: 6 conceptual mechanisms + tabs
- Embedded: API + Payment tabs (technical)
- More technical visual treatment

Plus: Reseller CTA banner ("SMM Panel for Resellers: Grow Your Business with Morethanpanel!") — dedicated zone for B2B persona.

### TAG Course Landing — 2 Persona Zones (Tabbed Pattern)

**Tab Navigation Zone:**
```
[For Individual Learners] | [For Team Training Buyers]
```

**Persona A Tab — Individual Learner**
- Layout: Self-paced enrollment focus
- Pricing: Self-paced / Mentorship tiers
- Testimonials: Individual graduates
- CTA: "Start Self-Paced" / "Enroll in Mentorship"

**Persona B Tab — Team Training Buyer**
- Layout: Cohort + custom team programs
- Pricing: Per-team scaling tiers
- Testimonials: HR managers / Team leads
- CTA: "Schedule Team Consultation"

### GTV Service Page — 3 Persona Zones (Side-by-Side Comparison)

```
[3-column comparison]
"For SME"           "For Mid-Market"      "For Enterprise"
[features list]     [features list]       [features list]
[Quick start]       [Custom proposal]     [Strategic engagement]
[CTA: Request Audit][CTA: Schedule Call]  [CTA: Book Strategy Session]
```

---

## Persona Zone Design Rules

### Rule 1 — Each Zone Self-Contained

Each persona zone must have its own:
- Section heading (entity declaration for persona)
- Body content (persona-specific value prop)
- Visual element (persona-appropriate imagery/icon)
- CTA (persona-specific action)

If user enters a persona zone via direct link / scroll, they must be able to act without scrolling outside that zone.

### Rule 2 — Bridge Sections Between Persona Zones

Don't transition directly from Persona A zone to Persona B zone. Insert bridge section:

```
[Persona A zone — white BG, salon imagery]
   ↓
[Bridge — neutral content like trust stats or testimonial mix]
   ↓
[Persona B zone — light tinted BG, distribution imagery]
```

Bridge prevents jarring visual transitions and provides visual rest.

### Rule 3 — Consistent Brand DNA

Despite persona differentiation, all zones must share:
- Same brand logo
- Same primary brand color (used differently per persona)
- Same typography family
- Same overall page structure

User must feel "same brand, different message for me" — not "different brands stitched together".

### Rule 4 — Size Allocation Reflects Strategic Priority

Don't equally weight all persona zones:

```
If 60% revenue from Persona B (distributor):
  → 40% page real estate to Persona B zone
  → 30% to Persona A zone (volume buyer)
  → 30% to Persona C zone (premium prospects)
```

Strategic priority should reflect in section size + above-fold positioning.

### Rule 5 — Cross-Reference Between Zones

Allow user to discover other personas:

- Persona A zone might mention: "Scaling beyond 100 bundles? → See Distributor program below"
- Persona B zone might mention: "Launching your own brand? → See OEM program below"

This recognizes user might evolve OR doesn't fit cleanly into one persona.

---

## Visual Pacing Across Persona Zones

When user scrolls through a hybrid page with multiple persona zones:

```
[Hero — universal authority] (white)
↓
[Trust strip — universal] (light gray)
↓
[Persona A zone] (white + brand primary)
↓
[Bridge — testimonial mix] (white)
↓
[Persona B zone] (light tinted + brand secondary)
↓
[Bridge — stats bar] (medium tinted)
↓
[Persona C zone] (dark + premium accent)
↓
[Universal FAQ] (white)
↓
[Final CTA — universal] (brand primary)
```

This creates **visual rhythm** with light-medium-dark progression matching persona sophistication.

---

## Anti-Patterns

❌ **No visual differentiation between persona sections** — all zones look identical, defeats purpose
❌ **Random colors not connected to brand** — breaks brand identity
❌ **Same imagery across all persona zones** — generic feel, no persona signal
❌ **Direct transition Persona A → Persona B without bridge** — jarring visual experience
❌ **Equal weight to all personas regardless of strategic priority** — wastes real estate
❌ **No cross-reference between zones** — user feels stuck in their persona, no upgrade path
❌ **Persona zones in tabs WITHOUT proper SEO setup** — content hidden from crawler
❌ **Single CTA repeated in every zone** — defeats persona-specific action language
❌ **Stock photos in persona zones** — fails authenticity test

---

## Validation Checklist

For each hybrid page with persona zones:

- [ ] 2-3 personas identified with distinct zones
- [ ] Each zone has distinct color accent
- [ ] Each zone has distinct background treatment
- [ ] Each zone has persona-specific imagery
- [ ] Each zone has appropriate layout density
- [ ] Each zone has persona-specific icon set
- [ ] Each zone has persona-specific CTA wording + style
- [ ] Bridge sections between persona zones
- [ ] Brand DNA consistent across zones
- [ ] Size allocation reflects strategic priority
- [ ] Cross-references between zones present
- [ ] Visual pacing creates rhythm (not jarring)

---

## Cross-References

- `dual-audience-macro-context.md` — Related but distinct (H2 phrasing pattern)
- `hybrid-page-pattern.md` — Hybrid page architecture
- `hub-spoke-visual-differentiation.md` — Tier-based visual differentiation
- `funnel-position-visual-mapping.md` — Funnel-based visual emphasis
- `multi-tier-pricing-pattern.md` — Pricing zones can be persona-specific
- `templated-visual-elements.md` — Each persona zone may use templated section
