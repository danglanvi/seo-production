# Templated Visual Elements (v2.0)

**When to use:** Multi-entity sections (services, categories, courses, modules) where the same visual structure repeats across entities.

**Core principle:** Google's WebFormer attention model trains on **patterned data** (DOM-tree, layout, images). Repeating the same template ≥3 times trains Google to recognize the page type and entity-attribute structure.

---

## The Foundation: Why Templates Work

From Koray's event slide and the WebFormer paper:

> "Transformers are trained for any 'patterned data' including images, or DOM-tree, and layout."

> "Google looks for 'templated [structures]' [in] visual elements in web pages."

When Google's crawler encounters:
- Section A: H2 "Instagram Services" + logo + tab nav + product grid
- Section B: H2 "TikTok Services" + logo + tab nav + product grid
- Section C: H2 "YouTube Services" + logo + tab nav + product grid

It learns: "This site has a template for [Platform] Services with [logo] [tab nav] [product grid]." Future crawls of new platform sections inherit this learned pattern → faster indexing + higher confidence ranking.

---

## The 5 Critical Template Slots

Every templated section must have these 5 slots filled consistently:

| Slot | Purpose | Examples |
|---|---|---|
| **1. Section heading** | Entity name declaration | H2: "Best Instagram Panel Services" |
| **2. Visual identifier** | Brand/category recognition | Platform logo, product photo, icon |
| **3. Body content** | Entity description | Paragraph 60-100 words |
| **4. Functional element** | Interaction option | Tab navigation, filter, dropdown |
| **5. CTA** | Conversion path | "Order", "Buy Now", "Get Started" button |

If any slot is missing or inconsistent across instances → template not detected.

---

## Repetition Requirements

### Minimum Repetitions

- **3 instances minimum** for Google to detect pattern
- **5+ instances ideal** for maximum learning signal
- Same template applied across **same site** for stronger signal (cross-page pattern reinforcement)

### Consistency Requirements

Each repetition must have:

| Element | Consistency Requirement |
|---|---|
| Heading format | Same level (all H2 or all H3), same syntax pattern ("Best [X] Services" or "[X] Panel" — pick one) |
| Visual identifier | Same type (all logos OR all icons OR all photos) |
| Body word count | Within ±20% of average (e.g., 80 words ±16) |
| Functional element | Same type (all tab nav OR all filter — pick one) |
| CTA text | Same wording or close variations ("Order" vs "Buy Now" — pick one and use throughout) |

---

## Pattern Recognition Across Page Types

### Page Type 1: E-commerce Multi-Category

```
[Section 1 - Instagram]                [Section 2 - TikTok]
├─ H2 + Instagram logo                 ├─ H2 + TikTok logo
├─ Description (80 words)              ├─ Description (75 words)
├─ Tab: Followers/Likes/Views          ├─ Tab: Followers/Likes
├─ 5 product cards                     ├─ 5 product cards
└─ Multi-tier pricing                  └─ Multi-tier pricing

[Section 3 - YouTube]                  [Section 4 - Facebook]
├─ H2 + YouTube logo                   ├─ H2 + Facebook logo
├─ Description (78 words)              ├─ Description (82 words)
├─ Tab: Subscribers/Views              ├─ Tab: Likes/Comments
├─ 5 product cards                     ├─ 5 product cards
└─ Multi-tier pricing                  └─ Multi-tier pricing
```

**Pattern detected after Section 3.** Google now expects new sections to follow this template.

### Page Type 2: Service Portfolio

```
[Service 1 - SEO]                      [Service 2 - Content]
├─ H2 + SEO icon                       ├─ H2 + Content icon
├─ Description (90 words)              ├─ Description (85 words)
├─ Process steps (5)                   ├─ Process steps (5)
├─ Case study card                     ├─ Case study card
└─ "Get Quote" CTA                     └─ "Get Quote" CTA

[Service 3 - GEO]                      [Service 4 - PPC]
├─ H2 + GEO icon                       ├─ H2 + PPC icon
├─ Description (88 words)              ├─ Description (87 words)
├─ Process steps (5)                   ├─ Process steps (5)
├─ Case study card                     ├─ Case study card
└─ "Get Quote" CTA                     └─ "Get Quote" CTA
```

### Page Type 3: Course Modules

```
[Module 1]                             [Module 2]
├─ H2 + Module number badge            ├─ H2 + Module number badge
├─ Outcomes list (3 items)             ├─ Outcomes list (3 items)
├─ Video thumbnail                     ├─ Video thumbnail
├─ Lesson count + duration             ├─ Lesson count + duration
└─ "Preview" link                      └─ "Preview" link

[Module 3]                             [Module N]
├─ H2 + Module number badge            ├─ ...
├─ Outcomes list (3 items)
├─ Video thumbnail
├─ Lesson count + duration
└─ "Preview" link
```

### Page Type 4: Listicle / Numbered Advantages

```
[Advantage 1]                          [Advantage 2]
├─ H4: "1. [Advantage Title]"          ├─ H4: "2. [Advantage Title]"
├─ Paragraph (50-70 words)             ├─ Paragraph (50-70 words)
└─ Inline CTA: "Grow Smarter"          └─ Inline CTA: "Grow Smarter"

... continues for 12 advantages
```

This is morethanpanel's "Advantages of Using an SMM Panel" 12-list pattern.

---

## Cross-Page Templated Consistency

The strongest signal: **same template across entire site for same page type**.

Example for GTV agency site:
- All service detail pages (SEO, Content, GEO, PPC) use the **same** layout template
- All client case study pages use the **same** layout template
- All blog post pages use the **same** layout template

When Google crawls the site:
- "Service detail page" pattern detected with strong signal
- "Case study page" pattern detected
- "Blog post" pattern detected

Each new page added to site inherits the pattern signal → faster ranking, higher topical authority.

---

## Application Examples

### APOHAIR Product Lines

**Templated Section per Product Line:**

```
[Tape-In Hair Extensions]              [Weft Hair Extensions]
├─ H2: "Tape-In Extensions" + photo    ├─ H2: "Weft Extensions" + photo
├─ Description: B2B specs (90 words)   ├─ Description: B2B specs (88 words)
├─ Tab: Length/Color/Texture           ├─ Tab: Length/Color/Texture
├─ Specs table (15 SKUs)               ├─ Specs table (12 SKUs)
├─ Wholesale tier pricing              ├─ Wholesale tier pricing
└─ "Request Quote" CTA                 └─ "Request Quote" CTA

[Closures]                             [Frontals]
├─ Same template structure             ├─ Same template structure
```

### GTV Service Pages Cross-Site

**Templated Layout for All 4 Services:**

Each service page (Semantic SEO, GEO, Content, AI Automation) uses identical structure:
1. Hero with service H1 + outcome statement
2. Centerpiece: Methodology overview
3. Process steps (5-step uniform)
4. Case studies (3 client cards uniform)
5. Pricing tiers (3-card uniform)
6. FAQ (decorative-semantic separated)
7. Final CTA

After deploying 4 service pages with same template → Google detects "GTV service detail page" pattern.

### TAG Course Module Pages

**Templated Module Detail Page (8-10 modules):**

Each module page (Module 1: Foundations, Module 2: Workflows, ..., Module 10: Advanced) uses:
1. Module header with number badge
2. Outcomes list (3 items)
3. Lesson grid (templated lesson cards)
4. Practice exercise section
5. Resources downloadable
6. "Continue to Next Module" CTA

---

## Audit: How to Check Template Compliance

### Visual Audit (Manual)

Lay 3 sections side-by-side. Ask:
- [ ] Heading hierarchy identical?
- [ ] Visual identifier slot present in all?
- [ ] Body content within ±20% word count?
- [ ] Functional element same type in all?
- [ ] CTA wording consistent?

If ANY answer is NO → template broken, Google fails to learn pattern.

### DOM Audit (Technical)

Check that each section has:
- Same wrapper class (e.g., `<section class="entity-block">`)
- Same heading tag and class (e.g., `<h2 class="entity-heading">`)
- Same image/logo wrapper (e.g., `<div class="entity-logo">`)
- Same CTA button class (e.g., `<button class="entity-cta">`)

Inconsistent class names = inconsistent DOM = pattern not detected.

---

## Anti-Patterns

❌ **Inconsistent slot count** — Section 1 has 4 slots, Section 2 has 6 slots
❌ **Mixed visual identifier types** — Some sections have logos, others have generic icons
❌ **Word count drift** — Description varies from 30 to 200 words across sections
❌ **CTA text drift** — "Buy Now" in Section 1, "Order Today" in Section 2, "Get Yours" in Section 3
❌ **Heading syntax variation** — "Best Instagram Services" vs "TikTok Panel Solutions" vs "YouTube Marketing"
❌ **Functional element inconsistency** — Tab nav in some, filter in others
❌ **Less than 3 repetitions** — Pattern below detection threshold
❌ **Cross-page template drift** — Different layout for service pages on same site

---

## Validation Checklist

For multi-entity sections:

- [ ] Pattern repeated ≥3 times (5+ ideal)
- [ ] All 5 critical slots filled in every instance
- [ ] Heading format consistent (same syntax pattern)
- [ ] Visual identifier consistent (same type)
- [ ] Body word count within ±20% across instances
- [ ] Functional element same type across instances
- [ ] CTA text consistent or close variations
- [ ] DOM classes consistent for technical pattern detection
- [ ] Cross-page consistency (if site has multiple page types using template)
- [ ] No drift in last instance (often the weakest as designers fatigue)

---

## Cross-References

- `hybrid-page-pattern.md` — When templates apply (Layer 3 per-entity centerpieces)
- `multi-layer-centerpiece.md` — Layer 3 templated centerpiece detail
- `block-chunk-design.md` — Each templated section as self-contained block
- `multi-tier-pricing-pattern.md` — Pricing tier templates within product sections
