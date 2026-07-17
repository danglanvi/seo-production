---
type: sop
status: stable
last_updated: 2026-04-20
master: "[[sources/sop-topical-map-vincent-v1]]"
related:
  - "[[Layer 1 Topical Map]]"
  - "[[Topical Map]]"
  - "[[sources/sop-topical-map-vincent-v1]]"
  - "[[Lexical AI Prompt Templates]]"
  - "[[Lexical Audit Checklist 20]]"
  - "[[skills/seo-topical-map]]"
  - "[[Document Design Template]]"
  - "[[Vastness-Depth-Momentum]]"
  - "[[GEO]]"
tags: [sop, project-delivery, topical-map, 23-step]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/01-topical-map.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# SOP 01 — Xây Topical Map (23-step Vincent Do v1.0)

> **Master procedural source:** [[sources/sop-topical-map-vincent-v1]] (Vincent Do, GTV, Jan 2026).
> **Conceptual summary:** [[Layer 1 Topical Map]] (6-step roll-up) + [[Topical Map]] (5-component).
> File này là **operational wrapper**: timeline, deliverable, checklist. Không replicate lý thuyết — drill vào source page khi cần chi tiết.

## Delivery target

- Topical Map v1 trong **5-10 ngày làm việc** (tuỳ niche size). Simple niche (iPhone repair local): 2-3 ngày. Complex niche (enterprise SaaS): 10 ngày.
- Không phải 1-2 ngày như version cũ — SOP v1 nặng research layer (Phase 1-3 ≈ 40% effort).

## Pre-conditions (Client Discovery — Phần 2 source)

Collect **9 client questions** trước khi kickoff. 3 buckets:

**Business:**
1. Sản phẩm/dịch vụ gì?
2. Website chủ yếu về topic gì?
3. Main purpose của website?
4. Kiếm tiền từ traffic như thế nào?

**Audience:**
5. Target audience là ai?
6. Main goal của họ trên website?
7. Specific challenges trước khi tìm giải pháp?

**Competition:**
8. Top 3-5 online competitors?
9. USP — khác biệt với competition?

Thêm: GSC/Ahrefs access (≥1 nguồn), brand assets, existing content inventory nếu có.

## Phase Roadmap (23 steps / 6 phases)

### Phase 1 — Foundation Research (Bước 1-6) — ~15% effort
- **Bước 1:** Buyer Persona (demographics + psychographics + behavioral) → 2-3 personas. See [[Buyer Persona]].
- **Bước 2:** [[Source Context]] — 1 câu định nghĩa.
- **Bước 3:** [[Central Entity]] — verify via Wikipedia; single/type/multiple.
- **Bước 4:** [[Central Search Intent]] = Source Context × Central Entity; predicate expansion.
- **Bước 5:** [[Core Section]] — main attribute + derived attributes.
- **Bước 6:** [[Outer Section]] — minor attributes; internal link to Core.

### Phase 2 — Deep Research (Bước 7) — ~25% effort
- 7.1 Research Knowledge / Contextual Domains / [[Contextual Layers]].
- 7.2 [[Query Network]] semantics (patterns, paths, correlative/sequential).
- 7.3 Manual Research (Wikipedia, Wikidata, InfraNodus, SERP features).
- 7.4 Ontology + Taxonomy (multi-LLM).
- 7.5 Elements gather — Entities, Attributes, Nouns, Verbs, Relationships.
- 7.6 [[Lexical Semantics]] (10 relations) + other word relations (Acronyms, Capitonyms, etc.).

### Phase 3 — Topic Generation (Bước 8) — ~15% effort
- 8.1 Competitor Topical Coverage (Ahrefs Top Pages, sitemaps).
- 8.2 Token Insertion Methodology — 8 distribution patterns.
- 8.3 Databases (Kaggle / Google Dataset Search / Data.gov).
- 8.4 Manual topic generation (stakeholder interviews).
- 8.5 Predicate/Verb × Noun/Attribute sequences.
- 8.6 Best Noun-Predicate relationships (Sequence Modeling).

### Phase 4 — Query Processing (Bước 9-11) — ~15% effort
- **Bước 9** Filter: 3-criteria (Relevance × Prominence × Popularity) + Trending factor. RPP Score = (R×2) × (P×1) × (LOG(Pop+1)×2).
- **Bước 10** Cluster: SERP similarity threshold 3. Tools: Keyword Cupid / Keyword Insights.
- **Bước 11** [[Vastness-Depth-Momentum]] balance — 2/3 mandatory, Momentum mandatory.

### Phase 5 — Topical Map Completion (Bước 12-20) — ~20% effort
- **Bước 12** Raw TM via [[Lexical Semantics]] (Hypernym → Hyponyms).
- **Bước 13** [[Quality Nodes]] — 3-5 showcase pages linked from homepage.
- **Bước 14** [[Trending Nodes]] — connect to Core Section.
- **Bước 15** Title Tags + ONE Macro Context/page (Golden Rule).
- **Bước 16** [[URL Slugs]] (Core flat vs Outer deeper; Root/Seeds/Nodes).
- **Bước 17** [[Descriptions]] (Meta descriptions).
- **Bước 18** Image URL slugs.
- **Bước 19** Image alt texts.
- **Bước 20** Connect Core ↔ Outer; signals flow toward Core.

### Phase 6 — Publication Strategy (Bước 21-23) — ~10% effort
- **Bước 21** [[Publication Frequency]] — Momentum + Patternless + 5-phase pattern (Day 1: 20-30 bulk → weekly rhythm → 3-5/day scale-up → full coverage → Config).
- **Bước 22** [[Document Design Template]] — Macro 75% + Bridge + Micro 25%.
- **Bước 23** [[Content Brief]] → [[Article Methodology]] (see [[sop/02-content-brief]]).

## GEO Optimization Layer (apply throughout Bước 15-23)

Từ Phần 4 source. See [[GEO]] page đã update.

- **Gate #1 (Title + Meta):** Bước 15 + 17 output must align with user intents; no vague titles.
- **Gate #2 (Speed <2s TTFB):** Bước 13 Quality Nodes prioritize speed optimization. Core Web Vitals pass.
- **Gate #3 (Chunk + Scoring):** Bước 22 mandate L0 (Answer-First) cho mọi H2/H3. Bước 23 embed [[E-A-V Framework]] statements.
- **Layer priorities:** L0 Critical, L1-L2 High, L3 Medium, L4-L6 Lower. See [[Contextual Layers#GEO Priority]].

## Definition of Done

- [ ] 2-3 Buyer Personas documented với goals + challenges + search behavior.
- [ ] Source Context + Central Entity (Wikipedia-verified) + Central Search Intent locked.
- [ ] Core Section với Main Attribute + ≥3 derived attributes.
- [ ] Outer Section với minor attributes + internal link plan to Core.
- [ ] Deep research artifacts: Ontology diagram, Lexical Semantics table (10 relations × ≥5 items), Query Semantics patterns.
- [ ] Token Insertion queries (≥500 raw) → filtered via RPP (≥50 final topics).
- [ ] SERP-clustered topic groups.
- [ ] V-D-M assessment matrix (can go wider/deeper/faster — Momentum mandatory).
- [ ] Raw TM → Processed TM: Title + URL + Meta + Image URL + Alt per page.
- [ ] ≥3 Quality Nodes + ≥2 Trending Nodes identified.
- [ ] Core ↔ Outer internal link map (signals flow to Core).
- [ ] Publication calendar (Phase 1-5 pattern) + competitor momentum benchmark.
- [ ] Document Design Template per page type.
- [ ] Content Briefs drafted cho top 20 pages (apply L0 mandatory + E-A-V).
- [ ] GEO audit: Gate #1/#2/#3 checklist pass cho Quality Nodes.

## 6 Golden Rules (Phần 5 checklist)

1. **Momentum mandatory** — không có Momentum, không đạt Topical Authority.
2. **ONE Macro Context per page** — focus chính duy nhất.
3. **L0 (Answer-First) MANDATORY** — mọi H2/H3.
4. **Internal signals flow to Core Section** — Outer luôn support Core.
5. **Quality over Quantity** — fewer stronger pages.
6. **Publishing Order Matters** — X → Y → Z ≠ Z → Y → X.

## Common Pitfalls (Phần 6 source — 16 anti-patterns)

**Concept (4):** Keyword clusters ≠ TM · Ignore Source Context · Volume-only filter · Breaking contextual boundaries.
**Structure (4):** Insufficient Core depth · Missing Quality/Trending nodes · No semantic connections · Multiple Macro Contexts/page.
**Execution (4):** Publish during BCAU · Fixed pattern · No updates · Ignore competitor momentum.
**GEO (4):** No L0 · Slow page (>2s) · Title/Meta misaligned · Tracking GEO như traditional SEO.

## Audit Cycle

- Run checkpoint 1-4 of [[Lexical Audit Checklist 20]] ngay sau Bước 20.
- Weekly GSC impression audit post-publish.
- Full [[Content Configuration]] re-audit every **6-9 months** with **≥15% content changes**.

## Deliverables

1. Topical Map spreadsheet (Processed — Title + URL + Meta + Section + Node Type per page).
2. Publication calendar (Phase 1-5 timeline).
3. Document Design Templates (per page type).
4. Content Brief samples (≥5 representative pages).
5. Internal linking map (graph visualization).
6. GEO audit report.

## Stakeholder Presentation

Deck format: V-D-M positioning, competitor gap, Core/Outer structure visual, Quality Node showcase, publication timeline, first 90-day quick wins.

## Related SOPs / Skills

- [[sop/02-content-brief]] — after Bước 23.
- [[sop/03-internal-linking]] — complement Bước 20.
- [[sop/05-audit-checklist]] — ongoing.
- Skill `/seo-topical-map` — auto-generate TM draft.
- Skill `/seo-brief` — auto-generate brief.
