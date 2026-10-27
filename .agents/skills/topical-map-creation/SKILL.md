---
name: topical-map-creation
description: "Create topical maps for semantic content networks following Koray's topical authority framework + AI-search era layer (2026). Use when: (1) Consulting clients to gather business/audience information, (2) Building website content architecture."
metadata:
  version: "2.3"
---

# Topical Map Creation (v2.3)

> Pipeline Koray gốc + AI-Search Era Layer (query fan-out, QDP/QDH/QDS, Surround Sound, quality gate, KPI shift) + Layer 1 Lexical module (GTV), chèn vào đúng phase. Evidence: wiki `sources/research-2026-07-topical-map-ai-era.md`.

## Overview

A Topical Map merges Search Language to Natural Language—a communication strategy with search engines to decrease risk and cost of retrieval while increasing relevance and responsiveness to achieve the "Ranking State of Topical Authority".

## Topical Authority Formula

```
Topical Authority = Historical Data × Topical Coverage / Cost of Retrieval
```

- **Historical Data**: User sessions, queries, interactions, impressions, clicks over time (reflects 6+ months past performance)
- **Topical Coverage**: Breadth (vastness) and depth of topic coverage
- **Cost of Retrieval**: How cheap/easy for Google to crawl, understand, and evaluate

## 3 Pillars of Topical Authority

| Pillar | Description | Action |
|--------|-------------|--------|
| **Vastness (Width)** | Wide topical map connecting everything | Cover more related topics |
| **Depth** | Deep coverage of key attributes | Go deeper on important attributes |
| **Momentum (Frequency)** | Publishing consistency | Publish more, faster |

**Rule**: Need at least 2/3 pillars. Momentum is MANDATORY.
- If you can't go wider, you must go deeper
- If you can't go deeper, you must go faster

## Components & Ratios (v2.0 fix — theo wiki đã chốt)

- Topical map có **6 main components**: Source Context · Central Search Intent · Central Entity · Core Section · Outer Section · **Root** (independent hub, connect to most important things — v1 skill thiếu Root).
- **Ratio page count: Core : Outer = 30-40% : 60-70%** (Lead confirm 2026-04-20). Đừng nhầm với ratio per-page Main Content : Supplementary = 60-80% : 20-40%.
- **Cost of Retrieval là map-level design criterion**: dedup node gần trùng, semantic consistency site-wide — mục tiêu giành "Representative Source" per cluster (Koray 09/2025: engines fingerprint documents, cluster theo quality score, gán 1 representative document per cluster).

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Claude | Discovery, Source Context, Central Entity, chia Core/Outer, verdict QDP, quality gate publish/merge/skip | dùng |
| Code (skill `serp-clustering`) | Gom keyword theo ma trận SERP-overlap ở Step 10 | dùng khi có SERP data: ngưỡng gộp phải khai báo và tất định |
| EmbeddingGemma 2 (skill `topical-focus`) | Dedup node gần trùng, gán node dự kiến vào cụm trước khi chốt map | tuỳ chọn: chỉ xếp cặp gần trùng để Claude đọc, không tự gộp node |
| Jev | Chấm RPP hàng loạt | không dùng: chưa có rubric RPP đã hiệu chuẩn |
| GLM Flash | Trích câu | không dùng: skill không trích câu hàng loạt |

---

## CONSULTING WORKFLOW: 6 PHASES

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'ahrefs?,dataforseo?,firecrawl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `ahrefs`: Step 8.1 dùng export Top Pages người vận hành gửi.
- Thiếu `dataforseo`: Step 10 gom cụm bằng SERP lấy qua Firecrawl hoặc bằng export người vận hành gửi.

### Phase 1: Client Discovery & Foundation (Steps 1-6)

#### Client Discovery Questions

Hỏi đủ 9 câu về business, khách hàng mục tiêu và đối thủ trong `references/consulting-questions.md` trước Step 1.

#### Step 1: Research Target Audience & Buyer Personas

Build 2-3 buyer personas with:
- **Demographics**: Age, gender, income, education, occupation, location
- **Psychographics**: Lifestyle, values, interests, attitudes
- **Behavioral**: Online behavior, purchasing habits, interaction patterns

**Output**: 2-3 detailed buyer personas with goals, challenges, preferred content types.

#### Step 2: Identify Source Context

Answer three core questions:
1. "Why are you covering this topic?"
2. "How do you monetize?"
3. "Why should you exist in the SERP?"

**Warning**: If covering topic just to chase traffic → will lose it eventually.

**Output**: 1 clear Source Context definition (e.g., "Contract Management Software")

#### Step 3: Identify Central Entity

**Definition**: What the website is mainly about - appears in ALL articles site-wide.

**Verification**: Search "[Central Entity] Wikipedia" - Google likely recognizes it if Wikipedia has a dedicated page.

**Types**:
- Single defined entity (e.g., Mail Merge)
- Common entity type (e.g., Country, Health Problems)
- Multiple entities (e.g., Country + Visa)

**Output**: 1-3 Central Entities verified.

#### Step 4: Identify Central Search Intent

**Formula**: Central Search Intent = Source Context × Central Entity

Focus on augmentation of predicates/verbs and noun combinations.

**Context Augmentation Method**:
```
Predicate "Learn" entails:
→ Speaking → Conversation, Dialogue, Pronunciation
→ Listening → Podcast, Music, Audiobook
→ Reading → Story, Book, Article
→ Writing → Letter, Essay, Email
```

Connect predicates + entailments + nouns → Query Networks.

**Output**: Clear Central Search Intent statement.

#### Step 5: Determine Core Section

**Formula**: Core Section = Source Context × Central Search Intent

**Characteristics**:
- Where monetization happens
- Where ranking signals flow
- Flatter URL structure (closer to homepage)
- Contains Quality Nodes
- Receives most internal links from Outer Section

**Process**:
1. Identify Main Attribute from Source Context
2. Identify Derived Attributes (e.g., Quality → Durability, Charge Time, Maintenance)
3. Densify Core Section for comprehensive coverage

**Output**: Core Section structure with main topics and derived attributes.

#### Step 6: Determine Outer Section

**Formula**: Outer Section = Central Entity + Predicates (not source context)

**Characteristics**:
- Improves Historical Data (impressions, clicks)
- Increases topical relevance
- Brief coverage acceptable
- Deeper URL structure
- Links back to Core Section

**Ignitor Strategy**: When Core Section too competitive → Start with easy-to-rank Outer topics (e.g., OscarWylee started with "Face Shapes"), transfer authority to Core later.

**Output**: Outer Section structure with supporting topics.

---

### Phase 2: Deep Research (Step 7)

#### 7.1 Knowledge Domains & Contextual Layers

**Knowledge Domains**: Specific queries, entities, layout designs, search patterns, user segments related to a field.

**Contextual Domains**: Entity with specific contextual angle to process.

**Contextual Layers**: Multiple levels of meaning within a contextual domain.

**Distinguishing Example**:
- Different Knowledge Domains: "Books" vs "Games" for children's sleep issues
- Different Contextual Domains: "Insomnia" vs "Anxiety" for same entity "helpful fruits"
- Different Contextual Layers: Severity level (mild/severe) and age (under/over 6)

#### 7.2 Query Semantics Understanding

- **Search Query Patterns**: Common patterns in Knowledge Domain
- **Query Path**: Sequence of queries in search session
- **Correlative Queries**: Queries frequently searched together

#### 7.3 Manual Research Tools

- Search Engines (Google/Bing/DuckDuckGo) - Autocomplete, People Also Ask, Related Searches
- Image Search, YouTube Search, Pinterest Search
- Forums (Reddit, Quora), Videos, Courses, PDFs, Books

#### 7.4 Ontology & Taxonomy Development

Develop ontology for main site concepts and entities, model taxonomy, properties, and relationships.

**Example Taxonomy** (iPhone Repair):
```
iPhone Repair (Root)
├── Hardware Repair
│   ├── Screen Repair (LCD, OLED)
│   ├── Battery Repair
│   └── Component Repair (Camera, Speaker, Port)
├── Software Repair
│   ├── iOS Issues
│   ├── Data Recovery
│   └── Jailbreak Issues
└── Accessories
```

#### 7.5 Gather Central Entity Elements

- **Entities**: All related entities connected to Central Entity
- **Attributes**: Properties or characteristics that describe entity
- **Nouns**: Nouns commonly associated with Central Entity
- **Verbs**: Verbs frequently associated with Central Entity
- **Relationships**: Map relationships between entities (has, is, uses, creates, manages)

**Word Relations**: Synonyms, Antonyms, Hypernyms, Hyponyms, Meronyms, Holonyms

#### 7.6 Layer 1 Lexical Module (v2.0 — GTV overlay, từ wiki [[Layer 1 Topical Map]])

Gather đủ **8 loại lexical relations** cho Central Entity, mỗi loại quyết định một cấu trúc map:

| Loại | Câu hỏi | Dùng để |
|------|---------|---------|
| Synonym | Còn gọi là gì? | **Merge rule**: 2 query có synonymous central entity → merge 1 page (chống cannibalization) |
| Antonym | Đối lập là gì? | **Antonym Bridge**: mỗi macro context có 1 antonym context làm supplementary (Benefits↔Risks, How-to↔Mistakes, Best-X↔When-X-fails) |
| Hypernym | Là loại của cái gì? | Parent topic, broader link |
| Hyponym | Các loại cụ thể? | **Go wide** = nhiều co-hyponym → mỗi cái 1 pillar |
| Holonym | Là phần của cái gì? | Parent concept link |
| Meronym | Có những phần nào? | **Go deep** = meronym → H3 trong pillar |
| Troponym | Cách thức hành động? | How-to variations |
| Entailment | Hệ quả logic? | YMYL chain of reasoning |

**Cross-lingual mapping** (multi-market VN + global): map lexical 2 thị trường đúng nuance — KHÔNG dùng Google Translate.

---

### Phase 3: Topic Generation (Step 8)

#### 8.1 Analyze Competitor Topical Coverage

1. Find authoritative sources (search main keywords, check backlinks)
2. Scrape competitor sitemaps
3. Export Ahrefs Top Pages report (URLs, Titles, Traffic Share, Top Keyword, Volume, Position)

#### 8.2 Token Insertion Methodology

Với Central Entity 2 từ (vd "Mail Merge"): sinh đủ 10 distribution patterns (Optional Token trước/sau/giữa từng từ và cả cụm). **Full 10 patterns + ví dụ: `references/query-processing.md` (section Token Insertion)**.

**Tools**: Ahrefs, Semrush Keyword Magic Tool, Google Keyword Planner

#### 8.3 Gather Predicates/Verbs & Noun Sequences

List all actions, noun associations, and attribute sequences related to Central Entity. Always bring context back to Central Entity and Central Search Intent.

---

### Phase 4: Query Processing (Steps 9-11)

#### Step 9: Filter Queries

**Three Filtering Criteria**:

| Criteria | Question | Weight |
|----------|----------|--------|
| **Prominence** | Can entity be defined without this attribute? | High |
| **Popularity** | Search volume for attribute? | Medium |
| **Relevance** | Connection to monetization? | High |

**RPP Score Formula** (Optional):
```
RPP Score = (Relevance × 2) × (Prominence × 1) × (LOG(Popularity + 1) × 2)
```

**Trending Factor**: When two queries have equal search demand, prioritize the trending one.

See `references/query-processing.md` for detailed scoring examples.

#### Step 10: Cluster Queries

**SERP-Based Clustering Method**:
- Threshold = 3: If 3+ top results for both queries are same → cluster together
- Same SERP results = same user intent

**Index Construction Principle**: Create fewer, stronger pages with more value (Information + Action).

**Tools**: Keyword Cupid, Key Clusters, Keyword Insights, SEO Utils

Có thể verify cụm bằng skill `serp-clustering` (ma trận SERP-overlap + tier data, ngưỡng khai báo) trước khi chốt cluster.

#### Step 10b: Query Fan-Out Coverage Check

AI Mode/AIO tách 1 query thành nhiều synthetic sub-queries (Google công bố kỹ thuật query fan-out tại I/O 05/2025). **Số sub-query tuyệt đối đổi theo phiên bản model — không neo** (sửa 29/08/2026: bỏ "~8-12"); cái ổn định là **~90% fan-out gom được vào ≤4 cluster** và chỉ ~27% sub-query lặp lại giữa các lần chạy (Batch 40, 08/2026) → map theo cluster. Chỉ ~38% AIO citations đến từ top-10 (Ahrefs 01/2026) → bề mặt retrieval rộng hơn ranking; trang rank cho nhiều sub-query cùng lúc có xác suất cite cao hơn (+161%, Surfer — C).

1. Với mỗi representative query của cluster: sinh fan-out set bằng skill **`geo-fanout-research`** (8 lens: định nghĩa · cách làm · so sánh · chi phí · đối tượng · rủi ro · thay thế · địa phương/thời điểm + evidence PAA/related/AIO; gom cluster ≤4, chấm ổn định ≥2/3 lần chạy) hoặc LLM/Qforia nếu chạy nhanh.
2. Đối chiếu map: **cluster** nào chưa có node/heading phụ trách → ghi gap (đơn vị là cluster, không phải từng sub-query).
3. **Coverage ở cấp network, focus ở cấp page** (Indig 815k pairs): 1 cluster cần 1 passage/heading tự đứng Ở ĐÂU ĐÓ trong network — KHÔNG nhồi mọi cluster vào 1 page; cluster khác Central Search Intent → page riêng (Step 10c QDP).
4. Không chase từng synthetic query (non-deterministic) — chỉ dùng để tìm coverage gap; date-stamp model version khi lưu cluster map.

#### Step 10c: QDP/QDH/QDS Decision (v2.0 — Koray SOP)

Mỗi gap/cluster → quyết định mức: **Page / Heading / Sentence**. 4 tiêu chí: (1) different entities, (2) high search demand, (3) recognizable query pattern, (4) low similarity to existing queries. **≥3/4 → Page riêng** (Google sẽ construct index mới theo index size + vocabulary uniformity + PageRank; similarity = 1/4 phiếu, không veto — verdict 01/08/2026, chi tiết `keyword-topic-url-mapping/references/qdp-gate.md`). 2/4 → Heading (giữ query template + L0 answer để thăng cấp sau). ≤1/4 → Sentence (implied attribute).

> **Rubric CANONICAL (v2.1 — 07/2026):** `keyword-topic-url-mapping/references/qdp-gate.md` — bản đầy đủ có cách chấm operational per tiêu chí (similarity = WEIGHTED theo term nặng, proxy SERP-overlap; pattern gần như luôn pass — đừng để nó một mình quyết), mức 4 mới **Component** (table/calculator/filter — 1 component trả cả query family), và nhánh document-cluster (vocabulary uniformity). Nguồn public: bài SEL local 22/07/2026 (`wiki/sources/local-seo-topical-authority-sel-koray.md`).

**Quality gate per node**: output RPP = **publish / merge / skip** + breadth cap — overclustering vào tangential topics gây core-update loss (case HubSpot — Kevin Indig); hòa với nguyên tắc Koray "no search demand → incorporate vào brief existing".

#### Step 11: Consider Vastness - Depth - Momentum

Re-evaluate 3 pillars:
- Can you go wider?
- Can you go deeper?
- Can you go faster?

**Strategy**: Create wide Topical Map → Connect everything → Go deep for specific Main Attribute and Context

---

### Phase 5: Topical Map Completion (Steps 12-20)

#### Step 12: Complete Raw Topical Map

**Raw Topical Map** = Entity-Attribute pairs only (no title tags yet)

**Lexical Semantics Distribution**:
1. Identify Hypernym (e.g., "Email Types")
2. List Hyponyms (Newsletter Mail, Birthday Mail, Welcome Mail, etc.)
3. Distribute to Raw Topical Map

**Query Dilemma Resolution**: When query is ambiguous (e.g., "Email Generator" = address OR text?):
- Prioritize most probable context at TOP
- Address second candidate at BOTTOM
- Link both appropriately

#### Step 13: Determine Quality Nodes

**Definition**: Most important articles that prove quality to search engines.

**Characteristics**:
- Extremely long and detailed
- Closest to homepage, linked from homepage
- Core Section priority
- Target competitive queries
- Include various content types (text, images, infographics, videos)

**Purpose**: Force search engine to recognize quality → crawl deeper → reassess site authority.

#### Step 14: Include Trending Nodes

**Definition**: Topics currently popular among users.

**Purpose**: Higher crawl prioritization, increase Historical Data, Google Discover traffic potential.

**Rule**: Trending Nodes MUST connect to Core Section to transfer authority signals.

**Tools**: Google Trends, Glimpse, Exploding Topics

#### Step 14b: Video Nodes + Corroboration Nodes

**Video/YouTube nodes cho Core Section topics**: YouTube mentions = tín hiệu AI visibility mạnh nhất (r=0.737, Ahrefs 12/2025); 18% AIO citations = YouTube. Text-only map bỏ trống 1/5 bề mặt citation. Mỗi Quality Node nên có video companion (transcript + chapters + VideoObject).

**Corroboration nodes (Surround Sound — Koray 09/2025)**: off-site mentions/references per core entity là COMPONENT của map, không phải PR việc phụ — branded web mentions = correlate #1 với AI visibility (hơn backlinks ~3:1). Sub-map per core entity: YouTube video, LinkedIn posts (domain cited #2), guest/PR pages, profiles. ⚠️ Platform mix volatile (ChatGPT bỏ ưu tiên Reddit/Wikipedia đột ngột 09/2025) → distributed bets, không all-in 1 platform. ⚠️ KHÔNG dùng tactic dynamic rendering prompt-injection theo user-agent (cloaking-adjacent).

**Ma trận loại nguồn off-site (bổ sung 29/08/2026 — map vào GE-28…GE-32 `tier-1-geo.md`, chạy chung chiến dịch offsite G4, không tách ngân sách):**

| Loại nguồn | Vai trò trong map | Evidence + nhãn | Lưu ý 08/2026 |
|---|---|---|---|
| **Listicle / best-of bên thứ ba** | Có mặt ở **1/3 đầu** danh sách đang được cite trong ngách; giữ info cập nhật (danh sách cũ feed AI thông tin sai) | Ahrefs 75k brand 12/2025: branded mentions r 0,66-0,71 (B) | ⚠ **Cửa sổ đang khép:** ChatGPT 5.6 cắt citation listicle **−50,5%** (Peec AI qua Lily Ray 20/08/2026 — secondhand, **C**); cite ≠ recommend (chỉ 43% citation kèm recommend, Ahrefs 07/2026 F) |
| **Review platform / directory ngành** | Entity confirmation + rating consistency | GE-30 | Rating/NAP/E-A-V phải khớp site chính chủ |
| **PR / báo ngành đang rank** | Corroboration cho claim + facts của brand | Branded web mentions r 0,66-0,71 (B) | Ưu tiên bài **đang rank** cho query ngách, không PR rời |
| **YouTube (video companion)** | Tín hiệu mạnh nhất: r **0,737** (Ahrefs 12/2025, B); 18% AIO citations = YouTube | GE-29 | Transcript + chapters + VideoObject; 1 video/Quality Node |
| **UGC / forum** (Reddit EN; Voz/Tinhte/nhóm FB VN) | Thí nghiệm có đo — ROI đảo chiều theo engine + thời điểm (Reddit #1 Gemini app 29,2% · ChatGPT <1% từ 08/2026) | GE-31 (**giả thuyết**, chưa có data VN) | Không bán như tactic đã chứng minh |
| **Owned truth pages** (about/pricing/FAQ/docs) | Nguồn sự thật để fan-out `site:` verify (64% fan-out có `site:`, Nectiv 08/2026) | GE-11 (gate G-ENT) | Không phải off-site nhưng là điều kiện để off-site có tác dụng |

**Rule nhất quán facts:** cùng **tên entity · số liệu · giá · năm thành lập · USP** ở mọi nguồn (site, GBP, LinkedIn, listicle, PR, video description) — lệch nhau là lý do AI "not confident" và không cite; register facts brand 1 trang, refresh khi đổi.

#### Step 15: Create Title Tags & Determine Macro Contexts

**Golden Rule**: ONE Macro Context (one main focus) per web page.

**Title Tag Methodologies**:
| Method | Pattern | Example |
|--------|---------|---------|
| H1 as Question | [Question]? | How to Make a Mail Merge? |
| H1 as Statement | [Definitive Statement] | Best Email Marketing Templates for 2024 |
| H1 with Numbers | [Number] [Adjective] [Noun] | 20 Health Benefits of Drinking Water |
| H1 with Qualifiers | [Entity]: [Qualifier 1], [Qualifier 2] | German Visas: Types, Requirements, Application |

#### Step 16: Determine URL Slugs

**Core Section**: Flatter structure (closer to homepage)
```
/germany/visa/study
/germany/visa/work
```

**Outer Section**: Deeper structure
```
/germany/life/culture/religion
/germany/life/language/schools
```

**Principle**: URLs reflect content hierarchy and contextual crawl pathways.

#### Step 17-19: Write Meta Descriptions, Image URLs & Alt Texts

- Meta descriptions: Include main keywords + unique value proposition
- Image URLs: Include main keywords
- Alt texts: Describe images accurately, enhance topicality

#### Step 20: Connect & Finalize Core and Outer Sections

1. Ensure all Outer Section pages link to relevant Core Section pages
2. Verify Quality Nodes are linked from homepage
3. Check internal link distribution follows rules
4. Validate URL structure reflects hierarchy

See `references/internal-linking-guide.md` for complete linking rules.

---

### Phase 6: Publication Strategy (Step 21)

#### Initial Launch Strategy

1. Publish 20-30 high quality articles on SAME DAY
2. Put them on homepage (force crawler attention)
3. Prove quality content exists
4. Invite crawlers to look deeper

**Note**: Scale based on existing site size - 20 articles on 1,000-page site won't attract attention.

#### Continuous Publishing Strategy

```
Phase 1: 20-30 articles (Day 1) - Bulk publish
Phase 2: 1 article/week - Establish rhythm
Phase 3: 3-5 articles/day - Scale up
Phase 4: Complete topical map - Full coverage
Phase 5: Configuration - Update everything (every 6-9 months, 15%+ changes)
```

#### Competitor Momentum Analysis

1. Take competitor sitemaps
2. Check last modification dates
3. Calculate their frequency
4. Go ABOVE their frequency

#### Patternless Publishing

- No fixed schedule
- Vary: times, quantities, days
- Avoid being predictable to algorithms

See `references/publication-strategy.md` for detailed frequency patterns.

---

## Tự phản biện trước khi trình

Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Map có đủ 6 component, gồm Root. Nguồn lỗi: bản v1 của skill thiếu Root, sửa ở v2.0.
- [ ] Số trang Core : Outer nằm trong 30–40% : 60–70%, không nhầm với tỷ lệ Main : Supplementary trong một trang. Nguồn lỗi: hai tỷ lệ bị lẫn trước bản chốt 20/04/2026.
- [ ] Mỗi gap hoặc cluster có verdict QDP (page, heading, sentence hoặc component), và mỗi node có verdict publish, merge hoặc skip. Nguồn lỗi: case HubSpot overcluster vào topic xa, mất traffic sau core update (Kevin Indig).
- [ ] Gap fan-out tính theo cluster ≤4, không in số sub-query tuyệt đối, có ghi ngày và model version. Nguồn lỗi: trần "~8-12 sub-queries" hết hạn theo model, bỏ ngày 29/08/2026.
- [ ] Mọi node Outer và Trending có link về Core Section, và Quality Node có link từ homepage. Nguồn: Step 14, Step 20 và `references/internal-linking-guide.md`.
- [ ] Ma trận nguồn off-site có nhãn evidence cho từng dòng, và dòng listicle có cảnh báo −50,5%. Nguồn: Peec AI qua Lily Ray 20/08/2026, secondhand, nhãn C.

---

## GEO/AI SEARCH OPTIMIZATION

Pipeline 7 tầng của ChatGPT Search, lớp AI Mode và AI Overviews, luật brief GEO: `references/geo-ai-search.md`. Đọc khi map cần tối ưu cho câu trả lời AI.

---

## Case Studies

5 case chuẩn (MangoLanguages, Nasdaq, OscarWylee, MailMerge, GymDesk) + key insight từng case: **`references/topical-map-patterns.md` (section Case Studies Summary)**. Đọc khi cần chọn strategy pattern (merge 2 maps / outer-as-ignitor / token insertion / query network redefine).

---

## Reference Files

- `references/consulting-questions.md` - Complete client discovery questions framework
- `references/query-processing.md` - RPP scoring formula and clustering methods
- `references/topical-map-patterns.md` - Entity-attribute patterns and case study examples (⚠️ file còn ghi "5 Components" — thiếu Root; theo SKILL.md v2.0: 6 components)
- `references/internal-linking-guide.md` - Complete internal linking rules
- `references/publication-strategy.md` - Publishing frequency and timing patterns
- `references/geo-ai-search.md` - Pipeline ChatGPT Search, lớp AI Mode/AIO, luật brief GEO
- Wiki evidence base: wiki nội bộ «research-2026-07-topical-map-ai-era» (ngoài repo, hỏi Lead) (delta list 15 items + debates) · `wiki/concepts/frameworks/QDP-QDH-QDS.md` · `wiki/concepts/frameworks/Surround Sound.md`
- Phân vai: gom nhóm keyword bằng SERP evidence (overlap matrix, ngưỡng, chain-merge) → skill `serp-clustering` (DATA layer)

---

## Changelog

- **v2.3 (2026-10-27):** hợp nhất bản root 27/10/2026: lấy cách viết gọn của root (dòng mở đầu, bỏ thẻ "(v2.0)"/"(v2.1)" ở Components, Step 10, 10b, quality gate, 14b). Thêm khối chuẩn của skill: `metadata.version`, Phân việc model, Bước 0 kiểm tool, Tự phản biện 6 mục. Giữ phần client-neutral của SP (wiki ngoài repo hỏi Lead, không trỏ đường dẫn ngoài repo).
- **v2.2 (2026-08-29, Lead duyệt 29/08 — Đợt 3, FINDINGS 22/08 §6-B/D):** Step 10b bỏ trần "~8-12 sub-queries" (hết hạn theo model) → **map theo cluster ≤4** (~90% gom, ~27% ổn định), sinh bằng skill mới `geo-fanout-research`, gap tính theo cluster, +161% (C), date-stamp model; Step 14b thêm **ma trận loại nguồn off-site** (listicle ⚠ −50,5% ChatGPT 5.6 C · review · PR đang rank · YouTube 0,737 · UGC VN giả thuyết · owned truth pages) map GE-28…32 + **rule nhất quán facts** ở mọi nguồn.
- **v2.1 (2026-07-19):** route gom nhóm keyword bằng SERP evidence → skill `serp-clustering` (dòng Phân vai ở Reference Files + câu verify ở Step 10). Không đổi pipeline.
- **v2.0 (Jul 2026):** (1) Components & Ratios fix — thêm Root (component thứ 6), ratio Core:Outer = 30-40%:60-70%, Cost of Retrieval làm map-level criterion. (2) Layer 1 Lexical Module (GTV) — 8 lexical relations, merge rule, antonym bridge, cross-lingual. (3) Step 10b Query Fan-Out Coverage Check. (4) Step 10c QDP/QDH/QDS + quality gate publish/merge/skip (chống overclustering). (5) Step 14b Video Nodes + Corroboration Nodes (Surround Sound). (6) AI Mode/AIO layer — KPI shift (LLM citations, Topic Share), GEO brief rules (citations/quotes/stats), micro-semantics pass, map refresh định kỳ. Nguồn: Batch 23 research (wiki).
- **v1.0:** Koray classic 6-phase / 21-step process + GEO ChatGPT pipeline + case studies.
