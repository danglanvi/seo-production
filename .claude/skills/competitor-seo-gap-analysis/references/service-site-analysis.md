# Service Site SEO Gap Analysis

Detailed framework for analyzing Service Business competitors (agencies, SaaS, professional services, consultancies, etc.)

## Page Type Classification

### Category Pages (Service Listings)

| Category Type | URL Pattern Examples | Typical Traffic Share |
|---------------|---------------------|----------------------|
| Service Category | `/dich-vu-seo/`, `/services/marketing/` | 25-40% |
| Industry/Vertical | `/seo-cho-ecommerce/`, `/for/healthcare/` | 10-20% |
| Location | `/dich-vu-seo-hcm/`, `/seo-agency-hanoi/` | 10-25% |
| Solution | `/giai-phap-tang-truong/`, `/solutions/` | 5-15% |
| Package/Tier | `/goi-seo-co-ban/`, `/pricing/` | 5-10% |
| Use Case | `/seo-cho-startup/`, `/for-enterprise/` | 5-10% |

### Detail Pages

| Detail Type | URL Pattern Examples | Typical Traffic Share |
|-------------|---------------------|----------------------|
| Service Detail | `/dich-vu/seo-tong-the/` | 10-20% |
| Case Study | `/case-study/abc-client/` | 3-8% |
| Portfolio | `/portfolio/project-x/` | 2-5% |
| Team/About | `/team/`, `/ve-chung-toi/` | 3-5% |
| Client Page | `/khach-hang/vinamilk/` | 1-3% |

### Content Pages

| Page Type | Examples | Traffic Share |
|-----------|----------|---------------|
| Blog | Thought leadership, guides, tutorials | 20-40% |
| Resource | Ebooks, whitepapers, templates | 5-15% |
| Tools | Calculators, audit tools, generators | 5-20% |
| FAQ/Help | Support, knowledge base | 2-5% |
| Homepage | Main homepage | 10-20% |

## Benchmark Metrics (Service Business)

### By Business Type

| Metric | Digital Agency | SaaS | Professional Services |
|--------|---------------|------|----------------------|
| Total Traffic | 50K-500K | 100K-5M | 20K-200K |
| Service Pages % | 25-40% | 15-30% | 30-45% |
| Location Pages % | 10-25% | 5-15% | 15-30% |
| Blog % | 25-40% | 30-50% | 20-35% |
| Tools % | 5-20% | 10-25% | 2-10% |

### Service Page Efficiency

| Metric | Excellent | Good | Poor |
|--------|-----------|------|------|
| Traffic/Service Page | >1000 | 300-1000 | <300 |
| Conversion Rate | >3% | 1-3% | <1% |
| Time on Page | >3 min | 1-3 min | <1 min |

## Gap Analysis Templates

### Service Coverage Gap

```
Service Taxonomy:

Main Services
├── Your coverage: X service pages
├── Competitor coverage: Y service pages
└── Gap: Missing services list

Service + Industry Combinations
├── Your coverage: X combination pages
├── Competitor coverage: Y combination pages
└── Gap: Missing combinations

Service + Location
├── Your coverage: X location pages
├── Competitor coverage: Y location pages
└── Gap: Missing location variants
```

### Location Coverage Analysis

```
Local SEO Gap Matrix:
| City/Region | Your Pages | Competitor | Gap | Priority |
|-------------|-----------|------------|-----|----------|
| HCM | X | Y | Z% | P? |
| Hà Nội | X | Y | Z% | P? |
| Đà Nẵng | X | Y | Z% | P? |
| ... | ... | ... | ... | ... |

For each location, check:
- Dedicated service + location page exists?
- LocalBusiness schema implemented?
- Google Business Profile linked?
- Location-specific case studies?
```

### Case Study/Portfolio Gap

```
Case Study Coverage:
| Industry | Your Case Studies | Competitor | Gap |
|----------|------------------|------------|-----|
| E-commerce | X | Y | Z |
| SaaS | X | Y | Z |
| Healthcare | X | Y | Z |
| ... | ... | ... | ... |

Case Study Quality Metrics:
- Avg. word count
- Data/metrics included?
- Client testimonial included?
- Before/after visuals?
```

## Visual Semantic Integration

### Service Page Structure

```
[HEADER 5-10%]
→ [HERO above fold: H1 + Primary CTA + Trust badges]
→ [CENTERPIECE 40%: Benefits + Features]
→ [SUPPORTING 30%: Process/How it works]
→ [PROOF 15%: Case studies + Testimonials]
→ [CTA SECTION 5%: Secondary CTA + Contact form]
→ [FOOTER 5-10%]
```

### Case Study Structure

```
[HEADER 5-10%]
→ [HERO: Client name + Industry + Key metric]
→ [CENTERPIECE: Challenge → Solution → Results]
→ [SUPPORTING: Process details + Screenshots]
→ [CTA: Similar project? Contact us]
→ [FOOTER 5-10%]
```

## Schema Markup Checklist

### Service Schema

```json
{
  "@type": "Service",
  "serviceType": "Required",
  "provider": {
    "@type": "Organization",
    "name": "Required",
    "url": "Required"
  },
  "areaServed": "Recommended",
  "description": "Recommended",
  "offers": {
    "@type": "Offer",
    "price": "Recommended if applicable"
  }
}
```

### LocalBusiness Schema (Location Pages)

```json
{
  "@type": "LocalBusiness",
  "name": "Required",
  "address": "Required",
  "telephone": "Required",
  "openingHours": "Recommended",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "Recommended",
    "longitude": "Recommended"
  },
  "areaServed": "Recommended"
}
```

### ProfessionalService Schema

```json
{
  "@type": "ProfessionalService",
  "name": "Required",
  "description": "Required",
  "priceRange": "Recommended",
  "areaServed": "Required",
  "hasOfferCatalog": "Recommended"
}
```

## Strategy Recommendations Template

### Quick Wins (1-4 weeks)
- Create missing service + location pages
- Add case study summaries to service pages
- Implement Service/LocalBusiness schema
- Optimize service page titles with location

### Medium Term (1-3 months)
- Build industry-specific service pages
- Create comprehensive case studies
- Add ROI calculator or audit tools
- Develop FAQ section for each service

### Long Term (3-6 months)
- Full location coverage (all target cities)
- Industry hub pages with resources
- Thought leadership blog series
- Client success story video content

## Dashboard Metrics for Service Sites

### Executive Summary Cards
1. Total Organic Traffic vs Benchmark
2. Service Page Coverage
3. Location Page Coverage
4. Case Study Count

### Charts to Include
1. Pie: Traffic by page type
2. Bar: Service category traffic gap
3. Bar: Location coverage comparison
4. Radar: Content type comparison (blog, tools, resources)
5. Funnel: Visitor → Lead conversion path

### Key Tables
1. Missing service + location combinations
2. Industry vertical gaps
3. Case study coverage by industry
4. Blog topic gaps vs competitor

## B2B Specific Considerations

### Lead Generation Focus

```
Conversion Path Analysis:
- Homepage → Service → Contact: X%
- Blog → Service → Contact: Y%
- Blog → Resource → Service → Contact: Z%

Compare with competitors:
- Do they have gated content?
- What tools do they offer?
- How prominent is their CTA?
```

### Trust Signal Gap

```
Trust Signals to Compare:
| Signal | Your Site | Competitor | Gap |
|--------|-----------|------------|-----|
| Client Logos | X | Y | - |
| Case Studies | X | Y | - |
| Awards/Certifications | X | Y | - |
| Team Page | Yes/No | Yes/No | - |
| Reviews/Testimonials | X | Y | - |
| Media Mentions | X | Y | - |
```
