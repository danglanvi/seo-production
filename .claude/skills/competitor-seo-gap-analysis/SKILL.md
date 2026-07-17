---
name: competitor-seo-gap-analysis
description: "Analyze competitor SEO gaps across Category, Product/Detail, and Blog pages for multiple website types (Job Sites, E-commerce, Service, Informational). Use when: (1) Analyzing competitor traffic distribution and URL structure, (2) Identifying content gaps in Category/PLP pages, (3) Auditing Product/Detail/Job Posting page performance, (4) Comparing Blog content quality and topical coverage, (5) Creating competitive SEO dashboards for client pitching, (6) Building SEO strategy recommendations from gap analysis, (7) Benchmarking against industry leaders, (8) Planning content scaling priorities. Triggers: 'phân tích đối thủ', 'competitor analysis', 'SEO gap analysis', 'so sánh đối thủ', 'content gap', 'category analysis', 'product page audit', 'blog audit', 'competitive benchmark', 'SEO strategy planning', 'pitching dashboard'."
---

# Competitor SEO Gap Analysis

Systematic framework for analyzing SEO gaps across Category, Product/Detail, and Blog pages. Applicable to Job Sites, E-commerce, Service Sites, and Informational Sites.

## Core Framework: 3-Layer Analysis

```
Layer 1: CATEGORY PAGES (PLP/Listing)
├── URL structure & taxonomy
├── Traffic distribution by category type
├── Geographic/Location coverage
├── Industry/Vertical coverage
└── Tools/Features traffic

Layer 2: PRODUCT/DETAIL PAGES (PDP/Posting)
├── Individual item pages (jobs, products, services)
├── Company/Brand pages
├── Schema markup implementation
└── Internal linking efficiency

Layer 3: BLOG/CONTENT PAGES
├── Topical coverage & authority
├── Content quality & relevance ratio
├── Traffic distribution by topic
└── E-E-A-T signals
```

## Universal Metrics Framework

### Traffic Distribution Matrix

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Category % | Category Traffic ÷ Total Traffic | 40-60% ideal |
| Product/Detail % | Detail Pages Traffic ÷ Total Traffic | 5-20% ideal |
| Blog % | Blog Traffic ÷ Total Traffic | 15-30% ideal |
| Tools % | Tools Traffic ÷ Total Traffic | 5-15% (if applicable) |
| Homepage % | Homepage Traffic ÷ Total Traffic | 10-25% ideal |

### Efficiency Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Traffic/URL | Total Traffic ÷ Total URLs | Higher = more efficient |
| Category Traffic/URL | Category Traffic ÷ Category URLs | Target: 50-150 |
| Product Traffic/URL | Product Traffic ÷ Product URLs | Target: 5-20 |
| Blog Traffic/URL | Blog Traffic ÷ Blog URLs | Target: 100-500 |

### Gap Calculation

```
Gap % = ((Target Value - Current Value) ÷ Target Value) × 100
Priority = If Gap > 80%: CRITICAL, > 50%: HIGH, > 30%: MEDIUM, else LOW
```

---

## Analysis Workflow

### Step 1: Data Collection & Classification

Classify URLs into page types based on URL patterns and content:

```python
# Universal URL Classification Patterns
classification_patterns = {
    'category': ['/category/', '/c/', '/danh-muc/', '/viec-lam/', '/jobs/', 
                 '/products/', '/san-pham/', '/dich-vu/', '/services/'],
    'location': ['/location/', '/dia-diem/', '/tinh/', '/province/', '/city/', 
                 '/district/', '/quan/', '/huyen/'],
    'product_detail': ['/p/', '/product/', '/job/', '/tin/', '/chi-tiet/', 
                       '/detail/', '/item/'],
    'company': ['/company/', '/cong-ty/', '/employer/', '/nha-tuyen-dung/', 
                '/brand/', '/thuong-hieu/'],
    'blog': ['/blog/', '/bai-viet/', '/tin-tuc/', '/news/', '/article/', 
             '/guide/', '/huong-dan/'],
    'tools': ['/tools/', '/cong-cu/', '/calculator/', '/builder/', '/generator/']
}
```

### Step 2: Calculate Distribution Metrics

For each competitor and client, calculate:

1. **Absolute metrics**: Total traffic, total URLs, traffic by page type
2. **Relative metrics**: % distribution, traffic per URL efficiency
3. **Gap metrics**: Difference vs benchmark/leader

### Step 3: Deep-Dive Analysis by Layer

See reference files for detailed analysis by website type:
- `references/job-site-analysis.md` - Job portals (TopCV, CareerViet, etc.)
- `references/ecommerce-analysis.md` - E-commerce sites (Shopee, Tiki, etc.)
- `references/service-site-analysis.md` - Service businesses (agencies, SaaS)
- `references/informational-site-analysis.md` - Content/media sites

### Step 4: Identify Priority Gaps

Use RPP-style scoring (adapted from Topical Map Creation):

```
Gap Priority Score = Relevance × Prominence × Potential

Relevance (1-3): Connection to core business/monetization
Prominence (1-3): Visibility in search/industry
Potential (1-3): Estimated traffic gain if fixed
```

### Step 5: Generate Strategy Recommendations

Map gaps to actionable strategies with:
- Timeline (Quick Win: 1-4 weeks, Medium: 1-3 months, Long: 3-6 months)
- Effort level (Low, Medium, High)
- Expected impact (traffic gain estimate)

---

## Category Page Analysis Framework

### Category Type Taxonomy

| Website Type | Primary Categories | Secondary Categories | Tertiary Categories |
|--------------|-------------------|---------------------|-------------------|
| **Job Site** | Industry, Role/Function | Location (Province) | Location (District), Experience Level |
| **E-commerce** | Product Category | Brand, Price Range | Attributes (Size, Color) |
| **Service** | Service Type | Location | Specialization |
| **Informational** | Topic/Subject | Content Type | Audience Segment |

### Category Metrics to Track

1. **Coverage metrics**
   - Number of category pages vs competitors
   - Geographic coverage (provinces, districts)
   - Industry/vertical coverage depth

2. **Traffic metrics**
   - Traffic per category type
   - Top performing categories
   - Underperforming vs competitors

3. **Structure metrics**
   - URL depth (flatter = better for Core)
   - Internal linking density
   - Subcategory completeness

### Category Gap Identification

```
Category Gap Types:
├── MISSING: Category exists in competitor, not in client
├── UNDERPERFORMING: Category exists but traffic gap > 50%
├── STRUCTURAL: Category structure differs (e.g., no district pages)
└── DEPTH: Less subcategories/attributes than competitor
```

---

## Product/Detail Page Analysis Framework

### Detail Page Types by Website

| Website Type | Primary Detail | Secondary Detail | Supporting Pages |
|--------------|---------------|-----------------|-----------------|
| **Job Site** | Job Posting | Company Profile | Similar Jobs |
| **E-commerce** | Product Page (PDP) | Brand Page | Reviews, Compare |
| **Service** | Service Detail | Case Study | Portfolio |
| **Informational** | Article | Author Profile | Related Content |

### Detail Page Metrics

1. **Scale metrics**
   - Total detail pages vs competitors
   - Growth rate (if historical data available)

2. **Quality metrics**
   - Schema markup implementation
   - Content completeness score
   - User engagement signals

3. **Efficiency metrics**
   - Traffic per detail page
   - Conversion path optimization

### Detail Page Gap Identification

```
Detail Gap Types:
├── SCALE: Fewer pages than competitor (e.g., company pages)
├── SCHEMA: Missing structured data (JobPosting, Product, LocalBusiness)
├── QUALITY: Lower content quality/completeness
└── LINKING: Poor internal linking from categories
```

---

## Blog/Content Analysis Framework

### Content Quality Assessment

| Quality Signal | What to Measure | Target |
|----------------|-----------------|--------|
| **Topical Relevance** | % content related to core business | > 60% |
| **E-E-A-T Signals** | Author bylines, citations, expertise | Present |
| **Content Depth** | Average word count, comprehensiveness | 1500+ words |
| **Freshness** | Update frequency, recency | Regular updates |

### Blog Gap Identification

```
Blog Gap Types:
├── RELEVANCE: Low % of topically relevant content
├── COVERAGE: Missing key topics competitors cover
├── QUALITY: Lower depth/comprehensiveness
├── AUTHORITY: Missing E-E-A-T signals
└── FRESHNESS: Outdated content
```

---

## Dashboard Creation Guidelines

### Visual Elements for Pitching

1. **Executive Summary Banner**
   - 4 key metrics with color-coded performance (green/yellow/red)
   - Overall gap percentage vs benchmark

2. **Gap Analysis Charts**
   - Radar chart: Category structure comparison
   - Bar chart: Traffic gaps by segment (negative = gap)
   - Pie charts: Distribution comparison

3. **Priority Matrix**
   - Scatter or ranked list: Impact vs Effort
   - Color-coded by priority (P0/P1/P2/P3)

4. **Strategy Roadmap**
   - Phase-based action plan (Phase 1, 2, 3...)
   - Timeline with milestones
   - Expected traffic projection

### Dashboard Color Coding

```
GTV Branding Colors:
- Primary: #00CCFF (cyan)
- Secondary: #4DA6E8 (light blue)
- Tertiary: #7A7FD1 (purple-blue)
- Quaternary: #A758BA (purple)
- Accent: #850DBA (deep purple)
- Positive: #00CC99 (green)
- Negative: #FF6B6B (red)
- Warning: #FFB347 (orange)

Traffic/Performance Indicators:
- Gap > 80%: #FF6B6B (CRITICAL)
- Gap 50-80%: #FFB347 (HIGH)
- Gap 30-50%: #00CCFF (MEDIUM)
- Gap < 30%: #00CC99 (OK)
```

---

## Quick Checklists

### Pre-Analysis Checklist
- [ ] Collect competitor URL data (Ahrefs/Semrush export)
- [ ] Classify URLs by page type
- [ ] Calculate total traffic and distribution
- [ ] Identify benchmark competitor

### Category Analysis Checklist
- [ ] Map category taxonomy
- [ ] Calculate coverage gaps
- [ ] Identify missing category types
- [ ] Analyze location coverage (if applicable)
- [ ] Assess category page efficiency

### Detail Page Checklist
- [ ] Count total detail pages
- [ ] Check schema implementation
- [ ] Calculate traffic efficiency
- [ ] Identify scale gaps
- [ ] Assess internal linking

### Blog Analysis Checklist
- [ ] Calculate relevance ratio
- [ ] Map topical coverage
- [ ] Identify missing topics
- [ ] Assess E-E-A-T signals
- [ ] Check content freshness

### Strategy Output Checklist
- [ ] Prioritize gaps (Critical/High/Medium/Low)
- [ ] Create phased roadmap
- [ ] Estimate traffic potential
- [ ] Define quick wins vs long-term
- [ ] Generate dashboard visuals

---

## Reference Files

| Topic | File |
|-------|------|
| Job Site Analysis | `references/job-site-analysis.md` |
| E-commerce Analysis | `references/ecommerce-analysis.md` |
| Service Site Analysis | `references/service-site-analysis.md` |
| Informational Site Analysis | `references/informational-analysis.md` |
| Dashboard React Components | `references/dashboard-components.md` |
| **Prompt Templates** | `references/prompt-templates.md` |

## Prompt Templates Quick Reference

When user uploads Ahrefs data, use appropriate prompt pattern:

| Analysis Type | When to Use |
|--------------|-------------|
| Full Website | Complete site analysis vs competitor |
| Category Only | Focus on listing/PLP pages |
| Detail Only | Focus on PDP/Job Posts/Company pages |
| Blog Only | Content quality and relevance analysis |
| Multi-Competitor | 3+ sites comparison |
| Pitching Dashboard | Client presentation ready output |

See `references/prompt-templates.md` for complete templates with examples.

---

## Integration with Other Skills

- **Visual Semantic SEO**: Use page type structures when analyzing visual hierarchy gaps
- **Topical Map Creation**: Apply Core/Outer section framework to content gaps
- **Semantic Content Audit**: Use 45-point checklist for blog quality gaps
- **GTV Proposal Branding**: Apply color scheme for dashboard creation
