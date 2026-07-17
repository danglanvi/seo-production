# Search Journey Compression (v2.0)

## Contents

- [The Two Strategies](#the-two-strategies)
- [Decision Matrix: Compress vs Split](#decision-matrix-compress-vs-split)
- [The 7-Dimension Coverage Requirement (For Compression)](#the-7-dimension-coverage-requirement-for-compression)
- [Audit: 7-Dimension Coverage](#audit-7-dimension-coverage)
- [AI Search (GEO) Implications](#ai-search-geo-implications)
- [Application Examples](#application-examples)
- [Common Mistakes](#common-mistakes)
- [Validation Checklist](#validation-checklist)
- [Decision Framework Quick Reference](#decision-framework-quick-reference)
- [Cross-References](#cross-references)

**When to use:** Deciding whether to cover full search journey (Awareness → Decision → Purchase) in 1 URL, or split across multiple URLs.

**Core principle:** Compression makes sense for low DR sites with high query overlap and conversion focus. Split makes sense for high DR sites with distinct intent per stage and deep coverage requirements.

---

## The Two Strategies

### Strategy A: Search Journey Compression (1 URL)

```
1 URL = Cover full search journey
├─ Awareness content (definitions, basics)
├─ Consideration content (how it works, options)
├─ Decision content (comparison, criteria)
├─ Action content (pricing, packages, CTA)
└─ Post-purchase content (FAQ, support)
```

**Used by:** morethanpanel.com, many SaaS landing pages, multi-intent homepage hubs

**Result:** 1 URL ranks for 50-100 keywords across journey stages

### Strategy B: Search Journey Split (Multi URL)

```
Multiple URLs, each covering 1 stage:
├─ /what-is-x.html (Awareness)
├─ /how-x-works.html (Consideration)
├─ /best-x-options.html (Comparison)
├─ /x-pricing.html (Decision)
└─ /buy-x.html (Action)
```

**Used by:** Established sites with high DR, comprehensive content coverage

**Result:** Each URL ranks deep for specific stage queries

---

## Decision Matrix: Compress vs Split

| Factor | Compress (1 URL) | Split (Multi URL) |
|---|---|---|
| **Site DR** | < 30 | > 50 |
| **Topical authority** | Building | Established |
| **Query overlap** | High (≥70%) | Low (<40%) |
| **Conversion focus** | Direct (info → purchase) | Multi-touch journey |
| **Content budget** | Limited | Abundant |
| **Page type** | Homepage hub, central node | Article cluster |
| **Audience size per stage** | Small but focused | Large, distinct |
| **AI Search citation goal** | High (extractable answers) | Variable |

### When to Compress

Apply compression when ALL apply:
- Site DR < 30 (need to maximize per-URL ranking)
- Queries have high overlap (similar intent variations)
- Page is a **central hub** of topical map
- User expected to convert quickly (not multi-session)
- Content team is small (can't sustain 10 URLs)

### When to Split

Apply split when ALL apply:
- Site DR > 50 (each URL can rank independently)
- Distinct intent per journey stage
- Topical authority building strategy (cover deep per topic)
- User journey expected to be multi-session
- Content team can produce dedicated content per URL

---

## The 7-Dimension Coverage Requirement (For Compression)

If compressing 1 URL, must cover **7 dimensions** of the central entity:

### Dimension 1: Definition

**Question:** What is the entity?

**Implementation:**
- Centerpiece L1 above-fold
- 40-80 word definition paragraph
- Answer-First L0 structure

### Dimension 2: Process / Mechanism

**Question:** How does it work?

**Implementation:**
- "How does X Work?" H2 section
- Visual steps (5-7 numbered)
- Embedded video tutorial

### Dimension 3: Attributes / Benefits

**Question:** What are the benefits / features?

**Implementation:**
- "Advantages of X" or "Why Use X" H3/H4 list
- 8-12 numbered attributes
- Each attribute: H4 + paragraph + inline CTA

### Dimension 4: Variations / Types

**Question:** What kinds / types exist?

**Implementation:**
- "Types of X" or per-entity sections
- Templated visual elements (see `templated-visual-elements.md`)
- 4+ types/variations covered

### Dimension 5: Use Cases / Personas

**Question:** Who uses it / for what?

**Implementation:**
- "Use cases for X" or "Who should use X"
- Persona cards or user journey examples
- 3-5 distinct use cases

### Dimension 6: Comparison & Evaluation

**Question:** How to choose / compare?

**Implementation:**
- "How to Choose the Best X" H2 section
- Comparison criteria list
- Red flags / what to avoid

### Dimension 7: Edge Cases

**Question:** When to use / when to avoid?

**Implementation:**
- "When does X provide value?" H2
- "When to avoid X" H2
- Edge case scenarios

---

## Audit: 7-Dimension Coverage

For pages applying compression, audit each dimension:

| Dimension | Present? | Quality | Word Count |
|---|---|---|---|
| 1. Definition | ☐ | ☐ Strong / ☐ Weak | ___ |
| 2. Process | ☐ | ☐ Strong / ☐ Weak | ___ |
| 3. Attributes | ☐ | ☐ Strong / ☐ Weak | ___ |
| 4. Variations | ☐ | ☐ Strong / ☐ Weak | ___ |
| 5. Use cases | ☐ | ☐ Strong / ☐ Weak | ___ |
| 6. Comparison | ☐ | ☐ Strong / ☐ Weak | ___ |
| 7. Edge cases | ☐ | ☐ Strong / ☐ Weak | ___ |

**Pass threshold:** ≥6/7 dimensions present with strong quality.

If <6 dimensions → either expand the page or reconsider compression strategy.

---

## AI Search (GEO) Implications

For 2026 search landscape, compression has additional benefits:

### Extractable Answer Blocks

Each H2 + L0 paragraph in the compressed URL can be **extracted by AI search engines** (ChatGPT, Perplexity, Gemini, Claude AI Search) for citation.

User asks ChatGPT: "What are the advantages of using an SMM panel?"
→ ChatGPT scrapes morethanpanel
→ Finds H3 "Advantages of Using an SMM Panel"
→ Extracts 12 H4 + paragraphs as answer
→ Cites morethanpanel.com

If page were thin / split → AI can't extract enough content → no citation.

### Multi-Query AI Coverage

Compressed page covers multiple AI queries:
- "What is SMM panel" → extract Definition section
- "How does SMM panel work" → extract Process section
- "Best SMM panels" → extract Comparison section
- "When to use SMM panel" → extract Edge case section

Each extraction = potential AI citation = brand exposure.

---

## Application Examples

### morethanpanel.com (Compression Implementation)

Page covers all 7 dimensions:

| Dimension | Section in morethanpanel |
|---|---|
| 1. Definition | Centerpiece L1 + paragraph (~50 words) |
| 2. Process | "How does SMM Panel Work?" 5-step + video |
| 3. Attributes | "Advantages of Using SMM Panel" 12 H4 list |
| 4. Variations | Instagram + TikTok + YouTube + Facebook templated sections |
| 5. Use cases | "How SMM Panel can help you make money" PQ + reseller section |
| 6. Comparison | "How to Choose the Best SMM Panel" + Red Flags + Test Before Buy |
| 7. Edge cases | "When provides real value" + "When to avoid" + "Balance organic/paid" |

**Pass: 7/7 strong coverage** → ranks for ~80 keywords from 1 URL

### APOHAIR Compression Strategy

If APOHAIR DR < 40 (likely true for younger B2B site):

| Dimension | APOHAIR Implementation |
|---|---|
| 1. Definition | Hero: "Hair Extension Manufacturer Vietnam — Wholesale & OEM" |
| 2. Process | "How OEM Manufacturing Works" + "How Wholesale Distribution Works" (dual-audience) |
| 3. Attributes | "Why APOHAIR" 12-point advantage list (manufacturing capability, quality, pricing, MOQ flexibility, etc.) |
| 4. Variations | Tape-In + Weft + Closures + Frontals templated product line sections |
| 5. Use cases | Use cases for: Salon owners + Distributors + Brand owners (private label) + Online retailers |
| 6. Comparison | "How to Choose Your Hair Manufacturer" + Red flags (cheap manufacturers, fake claims) |
| 7. Edge cases | "When OEM is right for you" + "When wholesale is better" + Volume thresholds |

### TAG Course Compression Strategy

For TAG Claude A-Z (newer site, smaller DR):

| Dimension | TAG Implementation |
|---|---|
| 1. Definition | "Claude A-Z: Master AI Workflow" + course description |
| 2. Process | "How the Course Works" + "How Mentorship Works" (dual-audience) |
| 3. Attributes | 10 outcomes you'll achieve |
| 4. Variations | 8-10 modules templated (Foundations / Workflows / etc.) |
| 5. Use cases | For developers + For marketers + For founders + For team training |
| 6. Comparison | "How to Choose Your Path" (Self-paced vs Mentorship vs Cohort) |
| 7. Edge cases | "When this course is for you" + "When other courses might fit better" + Prerequisites |

### GTV Service Page (Partial Compression)

GTV has higher DR for SEO services → can do **partial compression**:
- Compress on service page (cover 6 dimensions)
- Split into separate articles for deep dive (e.g., "What is Semantic SEO" as separate article for awareness query)

| Dimension | GTV Implementation | Compression? |
|---|---|---|
| 1. Definition | Brief on service page | Compressed |
| 2. Process | "How Semantic SEO Service Works" + "How Methodology Works" (dual-audience) | Compressed |
| 3. Attributes | "Why Semantic SEO Beats Traditional SEO" | Compressed |
| 4. Variations | (skip — service is unified) | N/A |
| 5. Use cases | Client tier examples (SME, Mid-market, Enterprise) | Compressed |
| 6. Comparison | "Why GTV vs Other Agencies" | Compressed |
| 7. Edge cases | "When Semantic SEO Works Best" | Compressed |
| Awareness ("What is Semantic SEO") | Separate article | Split |
| Awareness ("Topical Authority Explained") | Separate article | Split |

---

## Common Mistakes

### Mistake 1: Compressing Without DR Foundation

Site DR < 20 attempting to rank multi-keyword from 1 URL → both fails: too competitive for any single keyword + spread thin across many.

**Fix:** Build DR first via backlinks. Or split content into focused URLs.

### Mistake 2: Splitting When Should Compress

Site DR < 30 with 10 thin articles, each 800 words, none ranking. Site has no topical authority.

**Fix:** Consolidate 10 articles into 1 comprehensive 5000-word URL. Compression strategy.

### Mistake 3: Compression Without 7 Dimensions

Site compresses but only covers 3-4 dimensions → Google sees partial coverage → no topical authority signal.

**Fix:** Audit, identify gaps, expand to ≥6/7 dimensions.

### Mistake 4: Compression on Wrong Page Type

Compressing on a leaf product detail page (PDP) → confuses purchase intent.

**Fix:** Compression is for **central hub pages** (homepage, primary service page, category landing). Not for leaves.

### Mistake 5: Missing AI Citation Optimization

Compressed page is wall-of-text without clear answer blocks → AI can't extract → no citation.

**Fix:** Every H2 has L0 Answer-First structure. Each section is extractable as standalone answer.

---

## Validation Checklist

For pages applying compression:

- [ ] Site DR appropriate for compression strategy (<30 or hybrid)
- [ ] Page is central hub (not leaf node)
- [ ] All 7 dimensions covered (≥6 strong)
- [ ] Each dimension has dedicated H2 section
- [ ] L0 Answer-First in each section (AI extractable)
- [ ] Each section follows block chunk self-containment
- [ ] Templated sections for variations dimension
- [ ] Dual-audience pattern if applicable
- [ ] Decorative-semantic separation in FAQ
- [ ] Word count adequate (3000+ for full coverage)
- [ ] Schema markup (Article; ⚠️ FAQPage/HowTo KHÔNG còn rich result — FAQ chấm dứt 07/05/2026, HowTo retire 09/2023; không dùng như lever — 2026-07-13)

---

## Decision Framework Quick Reference

```
START
  │
  ▼
Site DR > 50?
  │
  YES ──→ SPLIT strategy (multi-URL per stage)
  │
  NO
  │
  ▼
Page is central hub?
  │
  NO ──→ Use page-type-specific pattern (PLP/PDP/Service)
  │
  YES
  │
  ▼
Query overlap ≥ 70%?
  │
  NO ──→ SPLIT strategy
  │
  YES
  │
  ▼
Can cover 7 dimensions with quality?
  │
  NO ──→ Build content team capacity, then revisit
  │
  YES
  │
  ▼
COMPRESSION strategy (1 URL multi-intent)
```

---

## Cross-References

- `hybrid-page-pattern.md` — Hybrid pages typically use compression
- `multi-layer-centerpiece.md` — Multi-centerpiece supports compression
- `decorative-semantic-heading.md` — FAQ encyclopedia is dimension 7 implementation
- `templated-visual-elements.md` — Variations dimension uses templates
- `dual-audience-macro-context.md` — Process dimension can use dual-audience
- `ranklab-factors.md` — Compression must still optimize RankLab factors
