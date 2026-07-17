# Informational Site SEO Gap Analysis

Detailed framework for analyzing Content/Media/Informational competitors (news sites, wikis, educational portals, affiliate sites, etc.)

## Page Type Classification

### Category/Hub Pages

| Category Type | URL Pattern Examples | Typical Traffic Share |
|---------------|---------------------|----------------------|
| Topic Hub | `/chu-de/suc-khoe/`, `/topics/health/` | 15-25% |
| A-Z Index | `/tu-dien/`, `/glossary/` | 5-15% |
| Tag/Taxonomy | `/tag/covid/`, `/category/finance/` | 10-20% |
| Author Archive | `/tac-gia/nguyen-van-a/` | 2-5% |
| Date Archive | `/2024/01/`, `/archive/` | 1-3% |
| Collection | `/bo-suu-tap/`, `/series/` | 3-8% |

### Content/Article Pages

| Content Type | URL Pattern Examples | Typical Traffic Share |
|--------------|---------------------|----------------------|
| Standard Article | `/bai-viet/ten-bai/` | 40-60% |
| How-To Guide | `/huong-dan/cach-lam/` | 10-20% |
| Listicle | `/top-10-x/`, `/danh-sach/` | 10-20% |
| Review | `/danh-gia/san-pham/` | 5-15% |
| News | `/tin-tuc/su-kien/` | 10-25% |
| Comparison | `/so-sanh/a-vs-b/` | 3-8% |
| Definition | `/la-gi/`, `/dinh-nghia/` | 5-10% |

### Supporting Pages

| Page Type | Examples | Traffic Share |
|-----------|----------|---------------|
| Tools | Calculators, converters, generators | 5-20% |
| Resources | Downloads, templates, checklists | 2-10% |
| About/Team | About us, editorial team | 1-3% |
| Contact | Contact, contribute | <1% |
| Homepage | Main homepage | 5-15% |

## Benchmark Metrics (Informational Sites)

### By Site Type

| Metric | News/Media | Wiki/Encyclopedia | Affiliate/Review | Educational |
|--------|-----------|-------------------|------------------|-------------|
| Total Traffic | 1M-100M | 500K-50M | 100K-10M | 50K-5M |
| Article % | 50-70% | 60-80% | 50-70% | 40-60% |
| Hub/Category % | 15-25% | 10-20% | 10-20% | 20-30% |
| Tools % | 2-10% | 5-15% | 5-20% | 10-25% |
| Author Pages % | 2-5% | 1-3% | 1-3% | 3-8% |

### Content Efficiency

| Metric | Excellent | Good | Poor |
|--------|-----------|------|------|
| Traffic/Article | >500 | 100-500 | <100 |
| Avg. Word Count | >2000 | 1000-2000 | <1000 |
| Time on Page | >4 min | 2-4 min | <2 min |
| Pages/Session | >2.5 | 1.5-2.5 | <1.5 |

## Gap Analysis Templates

### Topical Coverage Gap

```
Topic Taxonomy Analysis:

Main Topics
├── Your coverage: X topic hubs
├── Competitor coverage: Y topic hubs
└── Gap: Missing topics list

Subtopics (per main topic)
├── Your articles: X
├── Competitor articles: Y
└── Coverage ratio: X/Y × 100%

Content Format Distribution:
| Format | Your % | Competitor % | Gap |
|--------|--------|--------------|-----|
| How-To | X% | Y% | Z% |
| Listicle | X% | Y% | Z% |
| Review | X% | Y% | Z% |
| Definition | X% | Y% | Z% |
| News | X% | Y% | Z% |
```

### Content Quality Gap

```
Quality Metrics Comparison:
| Metric | Your Site | Competitor | Gap |
|--------|-----------|------------|-----|
| Avg. Word Count | X | Y | Z% |
| Images/Article | X | Y | Z% |
| Internal Links/Article | X | Y | Z% |
| External Links/Article | X | Y | Z% |
| Author Byline | X% | Y% | Z% |
| Last Updated Date | X% | Y% | Z% |
| Expert Quotes | X% | Y% | Z% |
```

### Topical Relevance Analysis

Adapted from Blog analysis framework:

```
Relevance Ratio = (Topically Relevant Articles ÷ Total Articles) × 100%

Categorize each article:
- CORE: Directly related to main topic/business
- ADJACENT: Related but not core
- TANGENT: Loosely related, trend-chasing
- IRRELEVANT: No relation to core topic

Target: CORE + ADJACENT ≥ 60%
Warning: TANGENT + IRRELEVANT > 40% indicates topic drift
```

## Visual Semantic Integration

### Hub Page Structure (Encyclopedia/A-Z)

```
[HEADER + Alphabet Nav 10%]
→ [CENTERPIECE: H1 + Stats + Featured Articles]
→ [MAIN 70%: Category Sections with article grids]
→ [SIDEBAR 15%: TOC + Search + Popular]
→ [SUPPORTING 10%: Newsletter + Resources]
→ [FOOTER 5-10%]
```

### Article Page Structure

```
[HEADER 5-10%]
→ [HERO: H1 + Author + Date + Reading Time]
→ [TOC Sidebar 10%: Sticky navigation]
→ [CENTERPIECE 60%: Article content]
→ [SUPPORTING 15%: Related articles]
→ [AUTHOR BIO 5%: E-E-A-T signal]
→ [COMMENTS/CTA 5%]
→ [FOOTER 5-10%]
```

### How-To/Tutorial Structure

```
[HEADER 5-10%]
→ [HERO: H1 + Time estimate + Difficulty + Tools needed]
→ [PROGRESS TRACKER Sidebar]
→ [CENTERPIECE: Numbered steps with visuals]
→ [SUPPORTING: Troubleshooting, FAQ]
→ [RELATED: Next steps, related guides]
→ [FOOTER 5-10%]
```

## Schema Markup Checklist

### Article Schema

```json
{
  "@type": "Article",
  "headline": "Required",
  "author": {
    "@type": "Person",
    "name": "Required",
    "url": "Recommended"
  },
  "datePublished": "Required",
  "dateModified": "Recommended",
  "publisher": "Required",
  "image": "Recommended",
  "mainEntityOfPage": "Recommended"
}
```

### HowTo Schema

```json
{
  "@type": "HowTo",
  "name": "Required",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Required",
      "text": "Required",
      "image": "Recommended"
    }
  ],
  "totalTime": "Recommended",
  "tool": "If applicable",
  "supply": "If applicable"
}
```

### FAQPage Schema

```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Required",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Required"
      }
    }
  ]
}
```

### BreadcrumbList Schema

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"position": 1, "name": "Home", "item": "/"},
    {"position": 2, "name": "Topic", "item": "/topic/"},
    {"position": 3, "name": "Article", "item": "/article/"}
  ]
}
```

## E-E-A-T Gap Analysis

```
E-E-A-T Signal Comparison:
| Signal | Your Site | Competitor | Gap |
|--------|-----------|------------|-----|
| Author Bylines | X% | Y% | - |
| Author Bio Pages | X | Y | - |
| Expert Credentials | X% | Y% | - |
| Citations/Sources | X/article | Y/article | - |
| Last Updated Dates | X% | Y% | - |
| Editorial Policy | Yes/No | Yes/No | - |
| Contact Info | Yes/No | Yes/No | - |
| About/Team Page | Yes/No | Yes/No | - |
| Reviews/Testimonials | X | Y | - |
```

## Strategy Recommendations Template

### Quick Wins (1-4 weeks)
- Add author bylines to all articles
- Implement Article schema
- Add "Last Updated" dates
- Create missing topic hub pages

### Medium Term (1-3 months)
- Build comprehensive author bio pages
- Add expert quotes/citations to articles
- Create glossary/definition pages for key terms
- Develop tools/calculators for the niche

### Long Term (3-6 months)
- Full topical coverage for core topics
- Video content integration
- Interactive tools and resources
- Original research/data studies

## Dashboard Metrics for Informational Sites

### Executive Summary Cards
1. Total Organic Traffic vs Benchmark
2. Topical Coverage % vs Competitor
3. Content Quality Score (avg. word count, E-E-A-T)
4. Tools/Interactive Content Traffic

### Charts to Include
1. Pie: Traffic by content type
2. Bar: Topic coverage gap
3. Bar: Content format distribution
4. Radar: E-E-A-T signals comparison
5. Line: Publishing frequency comparison

### Key Tables
1. Missing topic hubs
2. Underperforming content formats
3. E-E-A-T signal gaps
4. Top articles by traffic gap
5. Tools/features to add
