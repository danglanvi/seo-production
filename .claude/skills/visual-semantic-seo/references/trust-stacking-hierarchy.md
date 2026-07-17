# Trust Stacking Hierarchy (v2.0)

## Contents

- [The 7-Layer Trust Stack](#the-7-layer-trust-stack)
- [Layer 1: Search Engine Reviews Badge (Above-Fold)](#layer-1-search-engine-reviews-badge-above-fold)
- [Layer 2: Press Logo Strip (Boilerplate-Adjacent)](#layer-2-press-logo-strip-boilerplate-adjacent)
- [Layer 3: Video Reviews with Name + Role (Early Supporting)](#layer-3-video-reviews-with-name-role-early-supporting)
- [Layer 4: Multi-Platform Review Badges (Mid Supporting)](#layer-4-multi-platform-review-badges-mid-supporting)
- [Layer 5: Verified Customer Reviews (Late Supporting)](#layer-5-verified-customer-reviews-late-supporting)
- [Layer 6: Live Stats Bar (Between Centerpieces)](#layer-6-live-stats-bar-between-centerpieces)
- [Layer 7: Team Member Profiles (Pre-Footer)](#layer-7-team-member-profiles-pre-footer)
- [Anti-Patterns](#anti-patterns)
- [Application Examples](#application-examples)
- [Audit: Trust Stack Compliance](#audit-trust-stack-compliance)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

**When to use:** Hybrid pages, conversion-focused landing pages, e-commerce sites where building trust is critical for conversion.

**Core principle:** Trust signals must be **layered in specific positions** to build cumulative trust impression. Random placement = no compounding effect.

---

## The 7-Layer Trust Stack

Each layer has a specific position requirement. Combined, they create cumulative trust signal that user perceives subconsciously across the page scroll.

| Layer | Position | Element |
|---|---|---|
| **1** | Above-fold (top centerpiece) | Search engine reviews badge |
| **2** | Boilerplate-adjacent (just below hero) | Press logo strip |
| **3** | Early supporting (after first centerpiece) | Video reviews with name + role |
| **4** | Mid supporting (between centerpieces) | Multi-platform review badges |
| **5** | Late supporting (after pricing) | Verified customer reviews |
| **6** | Between centerpieces or supporting | Live stats bar |
| **7** | Pre-footer | Team member profiles |

---

## Layer 1: Search Engine Reviews Badge (Above-Fold)

**Position:** Above the H1 OR immediately after H1, in the centerpiece L1 zone.

**Purpose:** Establish immediate credibility from a trusted third party (Google, Trustpilot).

**Implementation:**
```
┌─────────────────────────────────┐
│  ⭐⭐⭐⭐⭐                          │
│  Google Reviews                  │
│  Excellent 4.8 out of 5         │
└─────────────────────────────────┘
```

**Specs:**
- Show platform logo (Google / Trustpilot / etc.)
- Display rating prominently
- Total review count visible
- Link to actual review platform

**Examples:**
- morethanpanel: "Excellent 4.8 out of 5" Google Reviews badge
- B2B: "5.0 ⭐ on Clutch (47 reviews)"
- E-commerce: "4.7 ⭐ on Trustpilot (1,247 reviews)"

**Anti-pattern:** Generic star rating without platform attribution → not verifiable

---

## Layer 2: Press Logo Strip (Boilerplate-Adjacent)

**Position:** Just below hero section, before first major content block.

**Purpose:** Borrow credibility from established media outlets that mention/feature the brand.

**Implementation:**
```
[Press logos horizontal scroll or static row]
[Logo 1]  [Logo 2]  [Logo 3]  [Logo 4]  [Logo 5]
```

**Specs:**
- 5-8 logos visible
- Logos in grayscale (muted, not screaming for attention)
- Optional: "As featured in" caption
- Hover state showing publication name

**Examples:**
- morethanpanel: AZ Big Media, Big News Network, The Frisky, APSense, USAWIRE, Startup.info, Ecommerce Fastlane
- B2B agency: TechCrunch, Inc., Forbes, Entrepreneur, Bloomberg
- DTC brand: Vogue, Allure, Elle, Glamour, Refinery29

**Anti-pattern:** Made-up press logos or barely-relevant blogs masquerading as press

---

## Layer 3: Video Reviews with Name + Role (Early Supporting)

**Position:** First major supporting block after Centerpiece L1 (before pricing).

**Purpose:** Human face + voice = highest-trust testimonial format.

**Implementation:**
```
[H2: "What Customers Say"]
[Description paragraph]
[Tab nav: Video Reviews | Customer Reviews | Platform Reviews]

[Video card 1]   [Video card 2]   [Video card 3]   [Video card 4]
Kate             Angelina         David            Emma
Influencer       Makeup Artist    Business Owner   Tiktoker
4.8 ⭐           4.9 ⭐           4.6 ⭐           4.7 ⭐
[7 March]        [14 March]       [9 May]          [28 February]
```

**Specs:**
- 4-6 video reviewer cards visible
- Each card: thumbnail with play button + name + role + date + rating
- Click to play video (modal or inline)
- Optional: review text snippet below name

**Quality checks:**
- Real people with verifiable identity (LinkedIn, Instagram)
- Diverse roles representing target audience
- Recent dates (within 6 months ideal)
- Video quality professional but not over-produced

**Anti-pattern:** Stock photos labeled as customers → trust collapse if discovered

---

## Layer 4: Multi-Platform Review Badges (Mid Supporting)

**Position:** Between centerpieces, often within reviews section as alternative tab.

**Purpose:** Show site is verified across multiple review platforms (not just one).

**Implementation:**
```
[Tab nav: Google | Product Hunt | G2 | SourceForge]

[Selected: Google tab]
4.8 ⭐ (1,549 Reviews)
[Leave a Review button]

[Sample reviews scrolling carousel]
"Delivers on all promises..." — NM, 12/10/2025 ✓ Verified
"From regular to automatic..." — NP, 03/09/2025 ✓ Verified
"Unbeatable service..." — DR, 21/11/2025 ✓ Verified
```

**Specs:**
- 3-4 platform tabs (Google + 2-3 others relevant to industry)
- Per tab: aggregate rating + total reviews + sample reviews + "Leave a Review" CTA
- Verified badge per review
- Date stamps recent

**Industry-specific platforms:**
- B2B SaaS: G2, Capterra, Trustpilot, Software Advice
- E-commerce: Trustpilot, Yotpo, Bazaarvoice
- Local services: Google Business, Yelp, BBB
- Tech tools: Product Hunt, AlternativeTo, Slant
- Agencies: Clutch, GoodFirms, DesignRush

---

## Layer 5: Verified Customer Reviews (Late Supporting)

**Position:** After pricing centerpiece, before final conversion CTA.

**Purpose:** Address last-minute purchase doubts with depth + diversity of customer voices.

**Implementation:**
```
[Per category aggregate: 4.8 (1,549 reviews) | 4.3 (402 reviews) | 4.6 (344 reviews)]

[Review cards grid — multiple per category]
[Review 1]
"After reading all the positive reviews, I gave Morethanpanel a try. They really deliver what they promise..."
NM • Natalia M. ✓ Verified • 12/10/2025

[Review 2]
"I have used Morethanpanel to boost my TikTok likes with their regular packages..."
NP • Niko P. ✓ Verified • 03/09/2025

[More reviews — pagination or infinite scroll]
```

**Specs:**
- 6-12 reviews visible at minimum (more accessible via load-more)
- Each review: title (short) + body text + initials + name + date + verified badge
- Multiple ratings categorized (per product, per service)
- Reviews recent (within 12 months)
- Mix of detailed (3+ sentences) and brief (1 sentence) reviews

**Quality checks:**
- Verified badge from external system (not just brand-generated)
- Diverse review lengths (real reviewers vary)
- Mix of 4-star and 5-star (all 5-star looks fake)
- Specific details mentioned (real reviewers reference specific features)

---

## Layer 6: Live Stats Bar (Between Centerpieces)

**Position:** Between Centerpiece L1 and L2, OR as supporting block.

**Purpose:** Hard numbers showing scale of operation = trust through proof of magnitude.

**Implementation:**
```
[Live stats bar — 4-6 metrics, large numbers]
18,488,523        0.07 Sec       279,057       121,501,390
Order completed   Order frequency   Users         Likes delivered

$0.01/1K          6,085
Starting price    Total Services
```

**Specs:**
- 4-6 hero metrics displayed
- Large number font (32-48px)
- Small label below number
- Optional: tooltip explaining metric
- Optional: live increment (see `real-time-function-validators.md`)

**Metric selection:**
- Volume metrics (orders, users, products served)
- Frequency metrics (orders per minute, transactions per second)
- Cumulative metrics (total delivered, total customers)
- Range metrics (starting price, longest running)
- Coverage metrics (countries, integrations, languages)

**Anti-pattern:** Inflated/fake numbers → trust damage if customer asks how to verify

---

## Layer 7: Team Member Profiles (Pre-Footer)

**Position:** Near footer, after main content but before final navigation.

**Purpose:** Humanize the brand. Show real people behind the company.

**Implementation:**
```
[H2: "Meet Our Team" / "Specialists"]

[Team grid — 5-8 team member cards]
[Photo]      [Photo]      [Photo]      [Photo]      [Photo]
Efe Onsoy    Martell      Lonnie       Jai          Bailey
Founder      Admin        Marketing    Operations   Customer
                          Manager      Manager      Relations
[Bio]        [Bio]        [Bio]        [Bio]        [Bio]
```

**Specs:**
- Real headshot photos (not avatars, not stock photos)
- Name + role + 1-2 sentence bio
- Optional: LinkedIn link, expertise tags
- 5-8 team members visible (full team if smaller, key roles if larger)

**Strategic team selection:**
- Founder/CEO (vision)
- Operations/Tech lead (execution)
- Marketing manager (visibility)
- Customer success (support promise)
- Subject matter expert (credibility)

**Anti-pattern:** Stock photos with fake names → discovered easily via reverse image search

---

## Anti-Patterns

❌ **Random trust signal placement** — Reviews scattered without strategic position
❌ **Single trust layer (only Layer 5)** — Reviews exist but no other trust signals
❌ **Layer 1 missing on hybrid page** — No above-fold trust = high bounce rate
❌ **Stock photos in Layer 7** — Easily discoverable as fake
❌ **Generic team bios** ("Passionate about results") — No actual person behind it
❌ **Outdated reviews** (Layer 5) — All from 2 years ago = site looks abandoned
❌ **Press logos that don't link to actual coverage** (Layer 2) — Verifiable on click reveals fake
❌ **Inflated stats** (Layer 6) — 100x real numbers undermines credibility
❌ **All trust signals concentrated in one section** — No cumulative scrolling effect

---

## Application Examples

### morethanpanel.com (Reference Implementation)

| Layer | Implementation | Position |
|---|---|---|
| 1 | Google Reviews 4.8 badge | Above H1 in centerpiece L1 |
| 2 | 7 press logos (AZ Big Media, Big News Network, The Frisky, etc.) | Just below hero |
| 3 | 4 video reviewer cards (Kate, Angelina, David, Emma) | First supporting after L1 |
| 4 | Tab nav: Google + Product Hunt + G2 + SourceForge with reviews | Within reviews section |
| 5 | 4 categories of verified reviews (Auto/Regular/Bulk/Custom) | After product grid sections |
| 6 | 6-metric live stats bar (18.4M orders, 0.07s, 279K users, etc.) | Between centerpieces |
| 7 | 5 team member profile cards (Efe Onsoy, Martell, Lonnie, Jai, Bailey) | Pre-footer |

**All 7 layers present** — reference implementation.

### APOHAIR Application

| Layer | Implementation | Position |
|---|---|---|
| 1 | Google Business Reviews badge OR industry verification (Alibaba Trade Assurance) | Above-fold |
| 2 | Industry press: Sourcing Journal, Beauty Independent, Vietnam Briefing, Hair & Beauty | Below hero |
| 3 | Video tour of factory + customer testimonials from B2B clients | Early supporting |
| 4 | Verification badges: SGS, ISO, BSCI compliance | Mid section |
| 5 | Verified buyer reviews per product line (Tape-In / Weft / etc.) | After product grids |
| 6 | Live stats: kits manufactured, container shipments, countries served | Between centerpieces |
| 7 | Factory team + Quality control team + Sales team profiles | Pre-footer |

### TAG Course Application

| Layer | Implementation | Position |
|---|---|---|
| 1 | Course platform badge (Udemy 4.9 / direct testimonial 5.0) | Above-fold |
| 2 | "As featured in" — TechCrunch Vietnam, ICTNews, Vinasa, AI4VN | Below hero |
| 3 | Video testimonials from 4 graduates with name + role + company | Early supporting |
| 4 | Tab: Course platform reviews + Google + LinkedIn endorsements | Mid section |
| 5 | Written reviews per module (Module 1: 47 reviews, Module 2: 38 reviews, etc.) | After pricing |
| 6 | Live stats: students graduated, avg rating, lifetime hours of content | Between centerpieces |
| 7 | Vincent Do + co-instructor + mentors + alumni success team | Pre-footer |

### GTV Service Page Application

| Layer | Implementation | Position |
|---|---|---|
| 1 | Clutch 5.0 OR Google Business 5.0 badge | Above-fold |
| 2 | "Trusted by" — Vinamilk, Bamboo Airways, Kotex, CareerViet, Apolat | Below hero |
| 3 | Video case studies from CMOs of GTV clients | Early supporting |
| 4 | Tab: Clutch + Google + DesignRush + Vietnamese marketing platforms | Mid section |
| 5 | Detailed client testimonials per service line | After pricing |
| 6 | Live stats: clients served, organic traffic delivered, articles published | Between centerpieces |
| 7 | Vincent Do + Account leads + SEO team + Content team | Pre-footer |

---

## Audit: Trust Stack Compliance

For each page, check each layer:

| Layer | Present? | Quality | Position Correct? |
|---|---|---|---|
| 1. Search engine reviews | ☐ | ☐ Strong / ☐ Weak | ☐ |
| 2. Press logo strip | ☐ | ☐ Strong / ☐ Weak | ☐ |
| 3. Video reviews | ☐ | ☐ Strong / ☐ Weak | ☐ |
| 4. Multi-platform badges | ☐ | ☐ Strong / ☐ Weak | ☐ |
| 5. Verified customer reviews | ☐ | ☐ Strong / ☐ Weak | ☐ |
| 6. Live stats bar | ☐ | ☐ Strong / ☐ Weak | ☐ |
| 7. Team member profiles | ☐ | ☐ Strong / ☐ Weak | ☐ |

**Pass thresholds:**
- Hybrid page / homepage hub: ≥6/7 layers
- Service page: ≥5/7 layers
- E-commerce category: ≥4/7 layers
- E-commerce product detail: ≥4/7 layers
- Article / blog post: ≥3/7 layers (different priorities)

---

## Validation Checklist

For trust stack implementation:

- [ ] Layer 1 present above-fold
- [ ] Layer 2 just below hero
- [ ] Layer 3 in early supporting position
- [ ] Layer 4 in mid section
- [ ] Layer 5 after pricing
- [ ] Layer 6 between centerpieces
- [ ] Layer 7 pre-footer
- [ ] No layer-skipping (e.g., Layer 1 + Layer 7 only with nothing between)
- [ ] All trust signals authentic (real photos, real reviews, real numbers)
- [ ] Recent dates on reviews (within 12 months)
- [ ] Mobile: all 7 layers still visible (may stack differently)
- [ ] Verified badges where applicable (real verification system)

---

## Cross-References

- `hybrid-page-pattern.md` — Hybrid pages need full 7-layer stack
- `multi-layer-centerpiece.md` — Trust stack interleaves with centerpieces
- `real-time-function-validators.md` — Layer 6 live stats are also live functions
- `block-chunk-design.md` — Each trust layer is a self-contained block
