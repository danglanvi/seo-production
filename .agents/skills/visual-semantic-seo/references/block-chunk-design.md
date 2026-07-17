# Block Chunk Design (v2.0)

## Contents

- [The Foundation: Layout-Aware Multimodal Document Understanding (2023)](#the-foundation-layout-aware-multimodal-document-understanding-2023)
- [The 5 Elements of a Self-Contained Block](#the-5-elements-of-a-self-contained-block)
- [Block Boundary Rules](#block-boundary-rules)
- [Block Metadata: BLK_ATTR Usage](#block-metadata-blk_attr-usage)
- [Sub-Block Internal Structure](#sub-block-internal-structure)
- [Multi-Block Pages: Higher-Level Transformer Optimization](#multi-block-pages-higher-level-transformer-optimization)
- [Mobile Block Adaptation](#mobile-block-adaptation)
- [Application Examples](#application-examples)
- [Audit: Block Self-Containment Check](#audit-block-self-containment-check)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

**When to use:** Optimizing any page for Layout-aware Multimodal Document Understanding. Critical for hybrid pages, long content, multi-section landing pages.

**Core principle:** Google chunks documents into self-contained BLK units. Each block must have **5 elements** + visual boundary so Google's lower-level and higher-level transformers can process correctly.

---

## The Foundation: Layout-Aware Multimodal Document Understanding (2023)

From the Google patent shown in Koray's slide:

```
1202 ORIGIN → Tokenized into BLK11, BLK21, BLK12, BLK22, BLKMN
1204 BLK_ATTR = FONT-SIZE + IS BOLD? + IS ITALIC? + IS UNDERLINE?
1206 HIGHER (BLOCK)-LEVEL TRANSFORMER (block relationships)
1208 LOWER-LEVEL TRANSFORMER (intra-block content)
1210 BLOCK SEGMENT IDS, MODALITY IDS
1216 (B) HIERARCHICAL ARCHITECTURE
```

**Translation:**
- Google reads page as **discrete blocks** (BLK), not continuous prose
- Each block has **metadata** (font-size, bold/italic/underline state)
- **Lower-level transformer** processes content WITHIN each block
- **Higher-level transformer** processes RELATIONSHIPS between blocks
- Wrong block boundaries → both transformers fail → ranking signal weak

---

## The 5 Elements of a Self-Contained Block

Every meaningful section (typically each H2 with content) should have these 5 elements:

| # | Element | Purpose | Examples |
|---|---|---|---|
| 1 | **Heading** | Block boundary marker for higher-level transformer | H2, H3 |
| 2 | **L0 Answer** | Direct answer in first 2-3 sentences (Answer-First) | "X is Y because Z." |
| 3 | **Body content** | Detailed explanation/elaboration | Paragraph, list, table |
| 4 | **Visual element** | Multimodal signal | Image, icon, diagram, chart |
| 5 | **Functional element** | Interactive/action element | CTA, tab, link-out, anchor |

**Rule:** A block needs ≥4/5 elements to be considered self-contained.

---

## Block Boundary Rules

### Visual Divider Requirements

Google detects block boundaries through visual cues:

| Cue Type | Implementation |
|---|---|
| **Whitespace/Padding** | Min 48px desktop, 24px mobile between blocks |
| **Background change** | Alternating subtle background tints |
| **Border/Divider line** | Thin horizontal rule between blocks |
| **Container wrap** | Card/box around block content |
| **Icon/Number prefix** | Block number or icon before heading |

At least 2 of these cues should be present for unambiguous boundary detection.

### Heading Hierarchy as Block Markers

Heading levels create implicit block hierarchy:

```
H1 = Document boundary
H2 = Major block boundary
H3 = Sub-block boundary within H2's block
H4 = Sub-sub-block within H3's block
```

When higher-level transformer processes blocks, it groups H3s under their parent H2.

**Anti-pattern:** Skipping levels (H2 → H4 with no H3) confuses block grouping.

---

## Block Metadata: BLK_ATTR Usage

The patent explicitly mentions Google reads:
- `FONT-SIZE`
- `IS BOLD?`
- `IS ITALIC?`
- `IS UNDERLINE?`

These are signals, not decorations. Use them semantically.

### Bold (`IS BOLD?`)

**Use bold for:**
- Key terms / salient terms (the 2-3 terms important for the article)
- Entity names
- Numerical values that matter (prices, percentages, dates)

**Don't bold for:**
- Random emphasis
- Decoration
- Whole sentences (defeats the signal)

**Example:**
> The **APOHAIR factory** in Vietnam produces over **5,000 hair extension kits per month**, with a defect rate below **0.3%**.

Three bolded items: entity name, key metric, quality metric. Each is a salient signal.

### Italic (`IS ITALIC?`)

**Use italic for:**
- Definitions / first-time term introduction
- Quotes from authority sources
- Named publications, books, foreign terms

**Don't italic for:**
- Random emphasis (use bold instead)
- Whole paragraphs

**Example:**
> *Topical Authority* is defined as Historical Data × Topical Coverage. Koray Tuğberk uses this formula to determine ranking potential.

### Underline (`IS UNDERLINE?`)

**Use underline ONLY for:**
- Hyperlinks (anchor text)

**Don't underline for:**
- Emphasis (use bold)
- Decoration

If underline appears on non-link text, Google's transformer expects a link and gets confused.

---

## Sub-Block Internal Structure

Within each block (especially long-form blocks 200+ words), structure for Lower-level Transformer:

### Pattern A: Definition + Mechanism + Application

```
[Block Start]
H2: "How Does X Work?"

L0 Answer (40-60 words)
"X works by [mechanism summary]. The process involves [3 key steps]."

Body content:
- Sub-paragraph 1: Definition expansion (60-80 words)
- Sub-paragraph 2: Mechanism detail (80-100 words)
- Sub-paragraph 3: Application example (50-70 words)

Visual element: Process diagram

Functional element: "Learn more" link OR inline "Try it" CTA

[Block End — clear visual boundary]
```

### Pattern B: List/Enumeration

```
[Block Start]
H2: "Best Features of X"

L0 Answer (30-40 words)
"X offers [N] features that [benefit summary]."

Body content:
- List item 1: Bold feature name + description (30-50 words)
- List item 2: Bold feature name + description
- ... 
- List item N: Bold feature name + description

Visual element: Icon for each list item OR feature comparison table

Functional element: "Compare All Features" CTA

[Block End — clear visual boundary]
```

### Pattern C: Q&A / FAQ Block

```
[Block Start]
H2: "What is X?"

L0 Answer (40-50 words)
Direct definition answer.

Body content:
- Expanded explanation (80-100 words)
- Edge cases or exceptions
- Comparison with related terms

Visual element: Optional infographic

Functional element: Anchor link to related FAQ OR contact form

[Block End — clear visual boundary]
```

---

## Multi-Block Pages: Higher-Level Transformer Optimization

When page has 10+ blocks, the **Higher-Level Transformer** evaluates relationships:

### Sequence Logic

Blocks should follow logical flow:
- Concept → Mechanism → Application → Comparison → Action (PQ Pathway)
- Or: What → Why → How → When → Who → Where

### Topical Coherence

All blocks should reinforce **same macro-context** (page topic). Off-topic blocks weaken vboostFactor.

### Internal Linking Between Blocks

Use anchor links to connect related blocks:
- Block 3 mentions a concept → link to Block 7 where concept is defined deeply
- Higher-level transformer uses these as signal of internal coherence

### Block Weight Distribution

Following Content Weight Distribution:
- Centerpiece blocks: 100% weight
- Main content blocks: 60-80%
- Supplementary blocks: 20-40%
- Boilerplate (header/footer): 5-10%

Higher-level transformer reads weights to determine page priorities.

---

## Mobile Block Adaptation

Blocks must work on mobile too. Considerations:

| Element | Desktop | Mobile |
|---|---|---|
| Block padding | 48px+ | 24px+ |
| Heading size | 32-48px H1, 24-28px H2 | 28-36px H1, 20-24px H2 |
| Visual element | Side-by-side with text | Stack above text |
| Multi-column block | 2-3 columns | Single column |
| CTA position | Inline with block | Often pinned to bottom |

**Critical mobile rule:** Mobile bottom nav (persistent action ID) doesn't break block boundaries — it floats above blocks, doesn't interrupt them.

---

## Application Examples

### APOHAIR Homepage Block Structure

| Block | Heading | 5 Elements Check |
|---|---|---|
| 1 (Centerpiece L1) | "Hair Extension Manufacturer Vietnam" | ✅ All 5 (H1 + L0 + body + factory image + WhatsApp CTA) |
| 2 (Trust strip) | (boilerplate, no H2) | Skip — boilerplate exception |
| 3 (Manufacturing process) | "How OEM Manufacturing Works" | ✅ All 5 (H2 + L0 + 5-step + diagram + "Request Quote") |
| 4 (Wholesale tiers) | "Wholesale Tier Pricing" | ✅ All 5 (H2 + L0 + 3 cards + photos + "Order Now") |
| 5 (Tape-In product line) | "Tape-In Hair Extensions" | ✅ All 5 (H2 + L0 + specs + photo + "Quote") |
| 6 (Weft product line) | "Weft Hair Extensions" | ✅ All 5 (templated same as #5) |
| 7 (Closures) | Templated | ✅ All 5 |
| 8 (Frontals) | Templated | ✅ All 5 |
| 9 (Quality certifications) | "Quality & Certifications" | ✅ All 5 (H2 + L0 + cert badges + photos + "View Cert") |
| 10 (FAQ) | "Câu hỏi thường gặp" (decorative) | Skip — decorative container, real blocks below |
| 11+ (FAQ macro-contexts) | Each H2 = real macro-context | ✅ All 4-5 each |

### TAG Course Landing Block Structure

| Block | Heading | 5 Elements Check |
|---|---|---|
| 1 (Centerpiece L1) | "Claude A-Z: AI Workflow Mastery" | ✅ All 5 |
| 2 (Reviews) | "What Students Say" | ✅ All 5 |
| 3 (Outcomes) | "What You'll Master" | ✅ All 5 |
| 4 (Centerpiece L2) | "Choose Your Path" | ✅ All 5 (3 pricing cards) |
| 5-14 (Module pages) | "Module N: [Topic]" templated | ✅ All 5 each |
| 15 (Mentor profiles) | "Your Instructors" | ✅ All 5 |
| 16 (FAQ) | "Frequently Asked Questions" (decorative) | Skip — real blocks below |

---

## Audit: Block Self-Containment Check

For each H2 block, score:

| Element | Present? | Notes |
|---|---|---|
| Heading | ☐ Yes / ☐ No | H2 or H3? |
| L0 Answer (within first 2-3 sentences) | ☐ Yes / ☐ No | Direct answer or background prose? |
| Body content | ☐ Yes / ☐ No | Sufficient depth (50+ words)? |
| Visual element | ☐ Yes / ☐ No | Image, diagram, icon? |
| Functional element | ☐ Yes / ☐ No | CTA, link, interaction? |

**Scoring:**
- 5/5 → Excellent self-containment
- 4/5 → Acceptable (1 element optional)
- 3/5 → Needs improvement (2 elements missing)
- ≤2/5 → Block broken, redesign needed

### BLK_ATTR Audit

For each block, check metadata usage:
- Bold: Used semantically (key terms only)? ☐
- Italic: Used for definitions/quotes only? ☐
- Underline: Used ONLY on links? ☐
- Font-size hierarchy: H1 > H2 > H3 > body? ☐

---

## Anti-Patterns

❌ **Block has heading but no L0** — Background prose before answer = block fails Answer-First
❌ **Block has L0 but no visual** — Pure text block weaker than multimodal
❌ **Visual element placed mid-block awkwardly** — Should anchor block, not interrupt
❌ **CTA missing from conversion-relevant block** — User reaches end with no action option
❌ **Bold used for decoration** — Random bolding dilutes salient term signal
❌ **Italic used for emphasis instead of bold** — Wrong semantic signal
❌ **Underline on non-link text** — Confuses transformer expecting link
❌ **No visual divider between blocks** — Boundaries unclear
❌ **Padding too tight (<24px)** — Blocks blend into each other
❌ **Block fragments across viewport** — User scrolls mid-block content broken visually

---

## Validation Checklist

For page-level block design:

- [ ] Every H2 block has ≥4/5 elements
- [ ] Visual divider between every block (whitespace + background OR border)
- [ ] Padding minimum 48px desktop, 24px mobile
- [ ] No skipped heading levels (H2 → H4)
- [ ] Bold used semantically (key terms only)
- [ ] Italic for definitions/quotes only
- [ ] Underline ONLY on links
- [ ] Font-size hierarchy clear (H1 > H2 > H3 > body)
- [ ] Mobile blocks adapt (single-column, larger padding)
- [ ] Higher-level transformer flow logical (PQ pathway or what/why/how)
- [ ] Internal anchor links between related blocks (where applicable)

---

## Cross-References

- `hybrid-page-pattern.md` — Hybrid pages have many blocks, design crucial
- `multi-layer-centerpiece.md` — Centerpieces are blocks too
- `templated-visual-elements.md` — Templated blocks must each pass self-containment
- `decorative-semantic-heading.md` — Decorative blocks (FAQ container) different rules
