# RankLab Factors (v2.0)

## Contents

- [The Foundation: Goldmine Final Score](#the-foundation-goldmine-final-score)
- [Factor 1: `readabilityScore`](#factor-1-readabilityscore)
- [Factor 2: `headingFactor`](#factor-2-headingfactor)
- [Factor 3: `siteNameFactor`](#factor-3-sitenamefactor)
- [Factor 4: `salientTermFactor`](#factor-4-salienttermfactor)
- [Factor 5: `vboostFactor`](#factor-5-vboostfactor)
- [Goldmine Final Score: Combined Optimization](#goldmine-final-score-combined-optimization)
- [Application Examples](#application-examples)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

**When to use:** Optimizing any content for the Goldmine final score (Google's ranking decision system from Content Warehouse API leak May 2024).

**Core principle:** RankLab is Google's End-to-End Ranking Framework that evaluates 5 critical factors. Each factor has specific optimization tactics.

---

## The Foundation: Goldmine Final Score

From Koray's slide on RankLab:

> "RankLab is an End to End Ranking Framework to Construct a Decision-tree"

The framework evaluates content through multiple factors and combines them into `goldminefin[al score]`. Critical factors highlighted in Koray's analysis:

| Factor | Field Name | What It Measures |
|---|---|---|
| Readability | `readabilityScore` | How easy content is to read |
| Heading | `headingFactor` | How well headings match queries |
| Site Name | `siteNameFactor` | Brand mention quality and frequency |
| Salient Term | `salientTermFactor` | Identification and reinforcement of key terms |
| Vertical Boost | `vboostFactor` | Whether content stays in claimed vertical |

Each factor must be optimized individually. The Goldmine score is the combined evaluation.

---

## Factor 1: `readabilityScore`

### What Google Measures

- Flesch Reading Ease score
- Average sentence length
- Complex word ratio
- Sentence structure variety (burstiness)
- Passive vs active voice ratio

### Optimization Tactics

**Sentence structure:**
- Use S-V-O (Subject-Verb-Object) construction primarily
- Average sentence length: 12-18 words
- Vary sentence lengths (burstiness): mix 5-word, 12-word, 25-word sentences
- Avoid run-on sentences (>30 words)

**Vocabulary:**
- Avoid "nuke words" — generic AI-typical vocabulary that signals low quality
- Replace abstract with concrete (specific numbers, names, examples)
- Use industry-specific terminology naturally (not stuffed)

**Voice:**
- Active voice ≥80% of sentences
- Passive voice acceptable for technical/scientific content (research findings)
- Direct address ("you", "your") for engagement

**Flesch Reading Ease target:**
- Consumer content: ≥60 (8th grade reading level)
- B2B/Technical: ≥50 (high school)
- Academic/Research: ≥40 (college)

### Example: Before vs After

**Before (low readabilityScore):**
> "The implementation of semantic SEO methodologies, particularly those derived from the work of Koray Tuğberk GÜBÜR, necessitates a comprehensive understanding of various interconnected frameworks including topical authority, contextual layers, and entity-attribute-value relationships."

Sentence: 38 words. Passive. Abstract. Flesch ~25.

**After (high readabilityScore):**
> "Semantic SEO works through three frameworks: Topical Authority, Contextual Layers, and EAV. Koray Tuğberk built this system. Most teams implement it wrong because they skip foundational steps."

3 sentences: 11 + 5 + 13 words. Active. Specific names. Flesch ~70.

### Audit Checklist

- [ ] Avg sentence length 12-18 words
- [ ] Sentence length variation (burstiness present)
- [ ] Active voice ≥80%
- [ ] No nuke words (use brand-specific blacklist)
- [ ] Flesch Reading Ease meets target
- [ ] Specific over abstract
- [ ] No run-on sentences (>30 words)

---

## Factor 2: `headingFactor`

### What Google Measures

- H1 contains exact target query
- H2 carries semantic variations
- Heading hierarchy is logical (H1 → H2 → H3)
- Heading entity count
- Heading-content alignment (does content match heading?)

### Optimization Tactics

**H1 design:**
- Include exact target query in H1
- ≤4 entities in H1
- No number stuffing ("5 Best", "Top 10")
- No CTA words ("Buy Now", "Discover")
- Reflect macro-context

**H2 design:**
- Semantic variations of target query
- Cover sub-topics (PQ Pathway: Concept → Mechanism → Application → Comparison → Action)
- Each H2 reflects a real macro-context (not decorative)
- Natural language questions or declarative statements

**H3 design:**
- Sub-attributes within H2 macro-context
- Same hyponym chain (don't switch from "Cách" to "Kiểu" mid-page)
- Specific over generic

**Hierarchy enforcement:**
- No skipping levels (H2 → H4 without H3)
- One H1 per page
- H2 and below can repeat freely

### Example: Before vs After

**Before (low headingFactor):**
- H1: "5 Best SEO Strategies in 2026 (You Won't Believe #3!)"
- H2: "Welcome to Our Guide"
- H3: "What is SEO?"

H1 has 6 entities (5 + Best + SEO + Strategies + 2026 + #3) + CTA word + number stuff.
H2 is decorative ("Welcome").
H3 should be H2 (real macro-context).

**After (high headingFactor):**
- H1: "Semantic SEO Strategies for 2026"
- H2: "What is Semantic SEO?"
- H2: "How Semantic SEO Differs from Traditional SEO"
- H2: "How to Implement Semantic SEO"

H1 has 4 entities. No CTA. Reflects macro-context.
H2s are real macro-contexts with semantic variations.

### Audit Checklist

- [ ] H1 contains exact target query
- [ ] H1 ≤4 entities
- [ ] H1 no number stuffing
- [ ] H1 no CTA words
- [ ] H2s carry semantic variations
- [ ] No decorative H2 with real macro-context demoted to H3
- [ ] Heading hierarchy logical (no level skipping)
- [ ] One H1 per page
- [ ] Heading-content alignment (subordinate text matches heading type)

---

## Factor 3: `siteNameFactor`

### What Google Measures

- Brand name mention frequency in content
- Natural vs forced placement
- Brand mentioned in early content (centerpiece zone)
- Brand entity recognition signals (combined with knowledge graph)

### Optimization Tactics

**Mention frequency:**
- 5-7 brand mentions per article (1500-3000 word article)
- Scale up for longer content (1 mention per 300-400 words)
- Don't stuff (≥10 mentions per 1000 words feels spammy)

**Placement strategy:**
- 1 mention in introduction (Centerpiece L1)
- 2-3 mentions in main content
- 1 mention in conclusion or final CTA section
- Optional: 1 mention in author byline

**Natural integration:**
- Use brand name in context: "GTV's methodology emphasizes..."
- Vary phrasing: "GTV", "GTV SEO", "the GTV team", "our agency"
- Avoid robotic placement ("In this article, GTV will explain...")

**Entity strengthening:**
- Link brand mentions to authoritative pages (about, founder bio)
- Use Schema.org `Organization` markup
- Consistent brand name across content (don't alternate "GTV" and "G.T.V.")

### Example: Before vs After

**Before (poor siteNameFactor):**
> Article about Semantic SEO mentions the brand once at the bottom: "Contact GTV SEO for help."

Brand entity weak. Just CTA placement.

**After (strong siteNameFactor):**
> "Semantic SEO works through three frameworks: Topical Authority, Contextual Layers, and EAV. **GTV's methodology** combines these with proprietary RPP scoring to rank Vietnamese enterprise content...
> 
> [later] **The GTV team** implements this for clients like Vinamilk and Bamboo Airways...
> 
> [later] **At GTV SEO**, we've measured 40-60% organic traffic lift within 6 months...
> 
> [later] **GTV's** approach differs from traditional SEO agencies because..."

Brand entity reinforced 4-5 times naturally throughout content.

### Audit Checklist

- [ ] Brand mentioned 5-7 times per article
- [ ] First mention in centerpiece zone
- [ ] Mentions distributed throughout content (not clustered)
- [ ] Phrasing varied
- [ ] Schema.org Organization markup present
- [ ] Consistent brand name (not abbreviation drift)
- [ ] Author byline includes brand affiliation

---

## Factor 4: `salientTermFactor`

### What Google Measures

- Identification of 2-3 key terms in article
- Reinforcement frequency of salient terms
- Strategic placement (heading, opening, closing)
- Co-occurrence with related entities

### Optimization Tactics

**Identifying salient terms:**

For each article, identify 2-3 salient terms:
- Term 1: Primary entity (main topic of article)
- Term 2: Critical attribute or related entity
- Term 3: Differentiator (what makes your angle unique)

Example for "Semantic SEO Methodology" article:
- Term 1: Semantic SEO (primary entity)
- Term 2: Topical Authority (critical attribute)
- Term 3: Koray's framework (differentiator)

**Reinforcement strategy:**

| Position | Salient Term Usage |
|---|---|
| H1 | Term 1 always present |
| H2 | Term 1 in 50%+ of H2s, Term 2 in 30%+ |
| First paragraph | All 3 salient terms |
| Centerpiece zone | Repeat Term 1 every 100 words |
| Body content | Term 1: 1 per 200 words; Term 2: 1 per 400 words |
| Conclusion | All 3 salient terms |

**Bold strategically:**
- Bold Term 1 on first appearance per H2 section
- Bold critical phrases including salient terms
- Don't bold every occurrence (defeats signal)

### Example: Before vs After

**Before (weak salientTermFactor):**

Article is about "Topical Authority" but mentions term only 4 times in 2000-word article. "Authority" mentioned 30+ times generically. No strategic reinforcement.

**After (strong salientTermFactor):**

Article identifies 3 salient terms:
1. **Topical Authority** (primary)
2. **Semantic Content Network** (related entity)
3. **EAV Framework** (mechanism)

- H1: "How to Build Topical Authority Through Semantic Content Networks"
- H2: "What is Topical Authority?" (Term 1)
- H2: "Building a Semantic Content Network" (Term 2)
- H2: "EAV Framework Implementation" (Term 3)
- Term 1 mentioned 12 times (1 per 150 words)
- Term 2 mentioned 8 times
- Term 3 mentioned 6 times
- Strategic bold on first appearance per section

### Audit Checklist

- [ ] 2-3 salient terms identified per article
- [ ] Term 1 in H1
- [ ] Term 1 in 50%+ of H2s
- [ ] All 3 salient terms in first paragraph
- [ ] Reinforcement frequency appropriate (not stuffed)
- [ ] Strategic bold on first appearance per section
- [ ] All 3 salient terms in conclusion

---

## Factor 5: `vboostFactor`

### What Google Measures

- Vertical/topical consistency of content
- Off-topic tangent presence
- Site's overall vertical signal
- Live function presence reinforcing vertical

### Optimization Tactics

**Vertical consistency:**

For SEO agency site (GTV vertical = SEO/marketing):
- ✅ Content about SEO, content marketing, GEO, AI search
- ✅ Adjacent verticals: web analytics, conversion optimization, brand strategy
- ❌ Off-topic: cooking recipes, travel guides, fashion

**Per-article consistency:**

Each article should stay in vertical:
- Article on Semantic SEO → don't tangent into general AI ethics
- Article on hair manufacturing → don't tangent into general beauty trends
- Article on AI courses → don't tangent into general education theory

**Site-wide vertical signal:**

- 90%+ of content in primary vertical
- 10% can be adjacent (related verticals)
- 0% should be unrelated (kills vboostFactor)

**Live function reinforcement:**

Live functions reinforce vertical (see `real-time-function-validators.md`):
- SEO agency: live client traffic dashboard
- Hair manufacturer: live production capacity
- Course platform: live cohort countdown
- E-commerce: live stock indicator

These functions prove the site is actively operating in the claimed vertical.

### Example: vboostFactor Issues

**Site with weak vboostFactor:**

GTV SEO agency site has:
- 60% SEO content
- 20% general business advice
- 10% tech reviews
- 10% personal lifestyle

Mixed vertical signal → Google uncertain about authority claim.

**Site with strong vboostFactor:**

GTV SEO agency site has:
- 80% SEO/Semantic SEO content (primary vertical)
- 10% AI/GEO content (adjacent vertical)
- 5% Vietnamese marketing case studies (regional adjacent)
- 5% client wins/announcements
- 0% off-topic

Strong vertical signal + live client traffic dashboard = high vboostFactor.

### Audit Checklist

- [ ] 90%+ content in primary vertical
- [ ] 0% truly off-topic content
- [ ] Each article stays focused (no tangent into unrelated verticals)
- [ ] Site has live function reinforcing vertical
- [ ] Author bios link to vertical-relevant credentials
- [ ] Internal linking primarily within vertical
- [ ] External links to authoritative vertical sources

---

## Goldmine Final Score: Combined Optimization

The 5 factors combine into the final ranking score. Optimizing one factor without others = uneven results.

### Priority Order for Improvement

If auditing existing content, prioritize:

1. **`headingFactor`** — Easy wins, structural changes possible
2. **`readabilityScore`** — Re-write tactics applicable to existing prose
3. **`salientTermFactor`** — Strategic term reinforcement
4. **`siteNameFactor`** — Add brand mentions throughout
5. **`vboostFactor`** — Long-term vertical consistency

### Combined Audit Template

For any article, score each factor:

| Factor | Score (1-10) | Notes | Priority |
|---|---|---|---|
| `readabilityScore` | __ | | |
| `headingFactor` | __ | | |
| `siteNameFactor` | __ | | |
| `salientTermFactor` | __ | | |
| `vboostFactor` | __ | | |
| **Average** | __ | | |

**Pass threshold:** Average ≥7/10 across all factors.

---

## Application Examples

### morethanpanel.com (Reference)

| Factor | Implementation |
|---|---|
| readabilityScore | Short sentences, S-V-O, factual claims |
| headingFactor | H1 "Best SMM Panel: Cheapest and Easiest Social Media Panel" — exact query + variation |
| siteNameFactor | "Morethanpanel" mentioned throughout reviews, stats, calculator |
| salientTermFactor | "SMM Panel" (Term 1), "Social Media Marketing" (Term 2), "Reseller" (Term 3) |
| vboostFactor | 100% SMM/social media content + live counters + price calculator reinforce vertical |

### APOHAIR Application

| Factor | Implementation Strategy |
|---|---|
| readabilityScore | B2B-friendly: avg 15 words/sentence, technical precision allowed |
| headingFactor | H1 "Hair Extension Manufacturer Vietnam — OEM & Wholesale" + exact target queries in H2 |
| siteNameFactor | "APOHAIR" 5-7 mentions per page, factory location, certifications |
| salientTermFactor | "Hair Extension Manufacturer" (Term 1), "Vietnam OEM" (Term 2), "Wholesale Distribution" (Term 3) |
| vboostFactor | 100% hair manufacturing/B2B content + live production capacity + factory video |

### TAG Course Application

| Factor | Implementation Strategy |
|---|---|
| readabilityScore | Casual expert tone, mind/bạn register, avg 14 words/sentence |
| headingFactor | H1 "Claude A-Z: AI Workflow Mastery for [Audience]" + exact query coverage |
| siteNameFactor | "The AI Growth"/"TAG"/"Claude A-Z" 5-7 mentions per landing page |
| salientTermFactor | "Claude A-Z" (Term 1), "AI Workflow" (Term 2), "Vietnamese Professional Mentorship" (Term 3) |
| vboostFactor | 100% AI/automation/Claude content + live cohort countdown + student dashboard previews |

### GTV Service Page Application

| Factor | Implementation Strategy |
|---|---|
| readabilityScore | Professional consultative, B2B technical, avg 16 words/sentence |
| headingFactor | H1 "Semantic SEO Service for Vietnamese Enterprise" + variations in H2 |
| siteNameFactor | "GTV"/"GTV SEO"/"GTV team" 5-7 natural mentions |
| salientTermFactor | "Semantic SEO" (Term 1), "Topical Authority" (Term 2), "GTV Methodology" (Term 3) |
| vboostFactor | 100% SEO/marketing content + live client traffic widget + case study videos |

---

## Anti-Patterns

❌ **Optimizing 1 factor while ignoring others** — Uneven Goldmine score
❌ **Stuffing salient terms** — Triggers spam filters, lowers readabilityScore
❌ **Stuffing brand name** — Lowers siteNameFactor (natural integration > frequency)
❌ **H1 packed with keywords** — Lowers headingFactor (≤4 entities rule)
❌ **Off-topic tangents** — Kills vboostFactor
❌ **Generic prose** ("In today's digital landscape...") — Lowers readabilityScore
❌ **Missing brand name in centerpiece** — Weak first impression for siteNameFactor
❌ **Salient terms only in heading, not body** — Reinforcement weak

---

## Validation Checklist

For RankLab optimization:

- [ ] readabilityScore: Flesch ≥60, avg sentence ≤18 words, S-V-O dominant
- [ ] headingFactor: H1 exact query + ≤4 entities + no number stuffing
- [ ] siteNameFactor: Brand mentioned 5-7 times naturally
- [ ] salientTermFactor: 2-3 salient terms identified + strategic reinforcement
- [ ] vboostFactor: 90%+ in-vertical content + live function present
- [ ] Combined audit average ≥7/10
- [ ] No anti-patterns present

---

## Cross-References

- `block-chunk-design.md` — Block design supports headingFactor + readabilityScore
- `decorative-semantic-heading.md` — Decorative-semantic separation improves headingFactor
- `real-time-function-validators.md` — Live functions reinforce vboostFactor
- `multi-layer-centerpiece.md` — Centerpiece zones critical for siteNameFactor + salientTermFactor
- `templated-visual-elements.md` — Templated patterns reinforce vboostFactor through consistency
