# Decorative-Semantic Heading Separation (v2.0)

## Contents

- [The Problem with Conventional FAQ Structure](#the-problem-with-conventional-faq-structure)
- [The Correct Structure](#the-correct-structure)
- [How to Identify Decorative vs Semantic](#how-to-identify-decorative-vs-semantic)
- [Why Decorative Heading Still Exists](#why-decorative-heading-still-exists)
- [Tab Navigation Pattern](#tab-navigation-pattern)
- [Application Examples](#application-examples)
- [Audit: How to Check Existing Pages](#audit-how-to-check-existing-pages)
- [Common Misclassification Examples](#common-misclassification-examples)
- [Anti-Patterns](#anti-patterns)
- [HTML5 Compliance](#html5-compliance)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

**When to use:** FAQ sections, Resources, Learn More hubs, tab navigation containers, anywhere a heading exists for UX/visual purposes vs semantic meaning.

**Core principle:** "FAQ", "Resources", "Learn More" are **decorative containers**. Real macro-contexts inside should be **H2 (cùng cấp với decorative)**, not H3 nested under decorative H2.

---

## The Problem with Conventional FAQ Structure

Most SEO practitioners structure FAQ like this:

```
H2: Frequently Asked Questions
├─ H3: What is X?
├─ H3: How does X work?
├─ H3: Why use X?
└─ H3: When to choose X?
```

**This is wrong.** Here's why:

### Reason 1: "FAQ" has no semantic meaning

"Frequently Asked Questions" doesn't relate to your central entity. It tells Google "this section contains questions" — but Google already knows that from the question heading text. The FAQ label is for **UX**, not semantics.

### Reason 2: Real macro-contexts get demoted to H3

"What is X?", "How does X work?", "Why use X?" are **standalone macro-contexts** with independent search demand. Putting them as H3 under decorative H2 demotes their ranking signal.

### Reason 3: Featured snippet algorithm prefers H2

Google's featured snippet algorithm gives **higher priority to H2-level questions** than H3-level questions. Demoting real questions to H3 reduces snippet capture potential.

### Reason 4: Tab navigation needs H2 anchors

If FAQ uses tab navigation (e.g., 4 tabs: Safety / Choose / Growth / AI), each tab content cluster needs its own **H2 anchor** so Google identifies cluster boundaries.

---

## The Correct Structure

```
H2: Frequently Asked Questions (DECORATIVE — keep for UX)

H2: What is X? (REAL macro-context)
├─ H3: Definition explained
├─ H3: Types of X
└─ H3: Common misconceptions

H2: How does X work? (REAL macro-context)
├─ H3: Mechanism step 1
├─ H3: Mechanism step 2
└─ H3: Edge cases

H2: Why use X? (REAL macro-context)
├─ H3: Benefit 1
├─ H3: Benefit 2
└─ H3: Comparison vs alternatives

H2: When to choose X? (REAL macro-context)
├─ H3: Best scenarios
├─ H3: When to avoid
└─ H3: Decision framework
```

All real macro-contexts at H2 level, **same level as the decorative "Frequently Asked Questions" container**.

---

## How to Identify Decorative vs Semantic

### The 2-Question Test

For any heading, ask:

1. **Does this heading have search demand independently?**
2. **Does this heading reflect a macro-context of central entity?**

| Both YES | One YES, one NO | Both NO |
|---|---|---|
| **REAL macro-context** — keep as H2 | **Borderline** — depends on context | **DECORATIVE** — keep as H2 if needed for UX, but move real content to H2 below |

### Examples

| Heading | Q1 (Search demand?) | Q2 (Macro-context?) | Verdict |
|---|---|---|---|
| "What are the legal considerations for SMM services?" | YES | YES | **REAL macro-context** |
| "Frequently Asked Questions" | NO | NO | **DECORATIVE** |
| "How to Choose the Best SMM Panel?" | YES | YES | **REAL macro-context** |
| "Resources" | NO | NO | **DECORATIVE** |
| "Learn More About Hair Manufacturing" | NO | YES (tangential) | **DECORATIVE / borderline** |
| "Hair Manufacturing Process Explained" | YES | YES | **REAL macro-context** |
| "Quick Links" | NO | NO | **DECORATIVE** |
| "Why Choose APOHAIR?" | YES | YES | **REAL macro-context** |

---

## Why Decorative Heading Still Exists

### 1. UX Convention

Users scan pages following familiar patterns. "FAQ" near the bottom of a page is **expected** — removing it confuses users.

Solution: Keep "FAQ" as decorative H2, but design real macro-contexts below as H2 too.

### 2. Schema.org FAQPage Markup

> ⚠️ **Schema note (2026-07-13, LINT-2026-010):** FAQPage rich result đã chấm dứt 07/05/2026 (HowTo retire 09/2023) — markup dưới đây KHÔNG còn là rich-result lever và không có evidence giúp PAA/AI parsing (DiD Ahrefs: schema ≠ AI-citation lever). Giá trị còn lại của cấu trúc này: container semantic + FAQ content hiển thị trên trang (content mới là thứ có giá trị). Đồng bộ stance với skill `schema-markup-generator`.

Sites using `FAQPage` and `Question` schema need a container element. The decorative H2 serves this:

```html
<section itemscope itemtype="https://schema.org/FAQPage">
  <h2>Frequently Asked Questions</h2>  <!-- decorative container -->
  
  <h2 itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
    <span itemprop="name">What are the Legal Considerations?</span>
  </h2>
  <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
    <span itemprop="text">[answer content]</span>
  </div>
  
  <h2 itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
    <span itemprop="name">How to Choose the Best Provider?</span>
  </h2>
  ...
</section>
```

### 3. Anchor Link / Jump Navigation

URL fragments like `#faq` jump to the section. The decorative H2 serves as the anchor target.

### 4. Visual Section Break

Decorative H2 creates a visual divider between page sections (e.g., between Product Grids and FAQ). Maintains scannable layout.

---

## Tab Navigation Pattern

When FAQ uses tabs, each tab content cluster needs its own H2:

```
H2: Frequently Asked Questions (DECORATIVE)
[Tab navigation: Safety | Choose | Growth | AI]

[Tab 1 — Safety SELECTED, others hidden via CSS/JS]
H2: What are the Legal Considerations? (REAL — anchor for Tab 1)
├─ H3: How to Use Safely
├─ H3: Benefits
└─ H3: Drawbacks

[Tab 2 — Click to reveal]
H2: How to Choose the Best Provider? (REAL — anchor for Tab 2)
├─ H3: Best Features
├─ H3: Red Flags
└─ H3: Test Before Buy

[Tab 3 — Click to reveal]
H2: How to Maximize Growth with X? (REAL — anchor for Tab 3)
├─ H3: Strategy components
├─ H3: Metrics to track
└─ H3: Common pitfalls

[Tab 4 — Click to reveal]
H2: How Will AI Reshape X? (REAL — anchor for Tab 4)
├─ H3: AI improvements
├─ H3: Regulation impact
└─ H3: Future outlook
```

**Why each tab needs its own H2 anchor:**
- Google renders all tab content (even hidden via CSS) as part of DOM
- Each tab cluster ranks independently for its query
- Without H2 anchor, Google can't identify cluster boundary
- User clicks tab → H2 anchor scrolls into view (UX)

---

## Application Examples

### morethanpanel.com (Reference)

Real implementation:

```
H1: Best SMM Panel: Cheapest and Easiest Social Media Panel

[Multiple H2 sections covering reviews, stats, advantages, pricing, products...]

H2: Frequently Asked Questions (DECORATIVE)
[Tab nav: Safety and Benefits | Choose an SMM | Growth | AI SMM Services]

H2: What are the Legal Considerations for SMM Services?  ← REAL
├─ H3: How to Use an SMM Panel Safely?
├─ H3: What are the Benefits of Using an SMM Panel?
└─ H3: What are the Drawbacks of Using an SMM Panel?

H2: How to Choose the Best SMM Panel?  ← REAL
├─ H3: What are the Best Features of SMM Panels?
├─ H3: What are the Red Flags When Selecting?
└─ H3: How to Test an SMM Panel Before Buying?

H2: What should users know before using an SMM panel?  ← REAL
├─ H3: Basic requirements
├─ H3: How to find reliable suppliers
├─ H3: Strategize for organic growth
└─ H3: Challenges without SMM

H2: What future technologies will shape SMM panels?  ← REAL
├─ H3: AI accuracy improvements
├─ H3: Regulations impact
├─ H3: When provides real value
├─ H3: When to avoid
└─ H3: Balance organic + paid
```

10+ H2 in this section, all at same level as the decorative "FAQ" container.

### APOHAIR FAQ Application

```
H2: Câu hỏi thường gặp về Apohair (DECORATIVE)
[Tab nav optional: Manufacturing | Pricing | Shipping | Quality]

H2: Where Does Apohair Manufacture Hair Extensions? (REAL)
├─ H3: Vietnam Manufacturing Process
├─ H3: Factory Capacity and Capabilities
└─ H3: Quality Control Standards

H2: How is Apohair Pricing Structured? (REAL)
├─ H3: MOQ Tiers
├─ H3: Wholesale vs OEM Rates
└─ H3: Volume Discount Schedule

H2: How Does International Shipping Work? (REAL)
├─ H3: Shipping Methods Available
├─ H3: Delivery Time by Region
└─ H3: Customs and Documentation

H2: How is Hair Quality Verified at Apohair? (REAL)
├─ H3: Source Material Verification
├─ H3: Manufacturing Quality Checks
└─ H3: Pre-Shipment Inspection
```

### TAG Course FAQ Application

```
H2: Frequently Asked Questions (DECORATIVE)

H2: How is the Claude A-Z Course Structured? (REAL)
├─ H3: Module Sequence
├─ H3: Time Commitment
└─ H3: Self-paced vs Cohort Options

H2: What are the Prerequisites for Claude A-Z? (REAL)
├─ H3: Technical Requirements
├─ H3: Prior Knowledge Needed
└─ H3: Tools You'll Need

H2: What Certification Do Claude A-Z Students Receive? (REAL)
├─ H3: Certificate Type
├─ H3: Verification Process
└─ H3: LinkedIn Integration

H2: How Does the Claude A-Z Mentorship Program Work? (REAL)
├─ H3: Mentor Matching
├─ H3: Office Hours Schedule
└─ H3: Project Review Process
```

---

## Audit: How to Check Existing Pages

### Step 1 — Inventory Headings

List all H2 and H3 in the page.

### Step 2 — Apply 2-Question Test

For each heading:
- Search demand independently? (use Keyword Planner / Ahrefs)
- Macro-context of central entity?

### Step 3 — Identify Misclassified Headings

Find H3s that should be H2s (passed 2-question test but currently demoted).

### Step 4 — Check Decorative Wrappers

Find H2s that are decorative (failed 2-question test) and verify real content below them is at H2 level.

### Step 5 — Restructure

Move misclassified H3s to H2 level. Keep decorative H2 if useful for UX.

---

## Common Misclassification Examples

### Example 1: Encyclopedia Pages

**Wrong:**
```
H2: Types of Hair Extensions
├─ H3: Tape-In Extensions
├─ H3: Weft Extensions
├─ H3: Clip-In Extensions
└─ H3: Fusion Extensions
```

If "Tape-In Extensions" has 8K monthly searches → it's a **real macro-context**, not a sub-attribute. Should be H2.

**Right:**
```
H2: Types of Hair Extensions (decorative — overview anchor)

H2: Tape-In Hair Extensions (real — has search demand)
├─ H3: Application process
├─ H3: Maintenance
└─ H3: Pros and cons

H2: Weft Hair Extensions (real — has search demand)
├─ H3: ...

H2: Clip-In Hair Extensions (real — has search demand)
├─ H3: ...
```

### Example 2: Service Categories

**Wrong:**
```
H2: Our Services
├─ H3: Semantic SEO
├─ H3: Content Marketing
├─ H3: GEO Optimization
└─ H3: AI Automation
```

Each service has independent search demand → real macro-contexts.

**Right:**
```
H2: Our Services (decorative anchor)

H2: Semantic SEO Services (real)
├─ H3: ...

H2: Content Marketing Services (real)
├─ H3: ...

H2: GEO Optimization Services (real)
├─ H3: ...

H2: AI Automation Services (real)
├─ H3: ...
```

### Example 3: Resource Hubs

**Wrong:**
```
H2: Resources
├─ H3: Blog
├─ H3: Case Studies
├─ H3: White Papers
└─ H3: Webinars
```

These are content type categories — likely have search demand if branded.

**Right:**
```
H2: Resources (decorative)

H2: Blog Articles (real if site has content marketing intent)
[content...]

H2: Case Studies (real for B2B)
[content...]

H2: White Papers (real for B2B)
[content...]
```

---

## Anti-Patterns

❌ **All real macro-contexts demoted to H3 under decorative H2** — Most common error
❌ **Skipping decorative wrapper entirely** — Loses UX convention
❌ **Decorative H2 placed too prominently** — Visual weight wrong (FAQ shouldn't compete with main content centerpiece)
❌ **Multiple decorative H2s stacked** — "FAQ" + "Resources" + "Learn More" without real content between → page feels empty
❌ **Tab navigation without H2 anchors per cluster** — Google can't identify cluster boundaries
❌ **Generic "Information" or "Details" decorative wrapper** — Too vague, doesn't help UX
❌ **HTML5 outline algorithm violations** — Multiple H1s, incorrect nesting

---

## HTML5 Compliance

Multiple H2s at same level is **fully HTML5 compliant**. The HTML5 spec allows this:

```html
<body>
  <h1>Page Title</h1>
  <h2>Section A</h2>
  <h2>Section B</h2>
  <h2>Section C (decorative)</h2>
  <h2>Section D (real, same level as C)</h2>
</body>
```

The outline algorithm flattens this correctly. Google has handled this since 2018.

**Rule:** Only **one H1** per page. H2 and below can repeat freely.

---

## Validation Checklist

For pages with FAQ, Resources, or similar sections:

- [ ] Identified all decorative wrapper headings
- [ ] Applied 2-question test to all H2/H3
- [ ] Real macro-contexts at H2 level (same as decorative)
- [ ] No real macro-contexts demoted to H3 under decorative H2
- [ ] Tab navigation has H2 anchor per cluster
- [ ] (Optional — FAQ rich result đã chấm dứt 07/05/2026, không còn là lever) nếu vẫn giữ FAQPage markup: dùng real H2s as `Question` items, khớp visible content
- [ ] Decorative H2 visual weight appropriate (not overpowering)
- [ ] Page has single H1
- [ ] Featured snippet potential preserved (real questions at H2)

---

## Cross-References

- `hybrid-page-pattern.md` — FAQ encyclopedia is part of hybrid page pattern
- `dual-audience-macro-context.md` — Different from this pattern (intentional duplication for audiences)
- `block-chunk-design.md` — Each real macro-context H2 must be self-contained block
- `search-journey-compression.md` — FAQ encyclopedia supports compression strategy
