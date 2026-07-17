# Job Site SEO Gap Analysis

Detailed framework for analyzing Job Portal competitors (TopCV, CareerViet, VietnamWorks, Vieclam24h, etc.)

## Page Type Classification

### Category Pages (Job Listings)

| Category Type | URL Pattern Examples | Typical Traffic Share |
|---------------|---------------------|----------------------|
| Industry/Sector | `/viec-lam-it/`, `/jobs/banking/` | 15-25% |
| Role/Function | `/viec-lam-ke-toan/`, `/jobs/developer/` | 20-30% |
| Province/City | `/viec-lam-tai-ho-chi-minh/` | 10-20% |
| District | `/viec-lam-quan-1/`, `/jobs/district/` | 3-8% |
| Experience Level | `/viec-lam-fresher/`, `/senior-jobs/` | 3-5% |
| Work Type | `/remote-jobs/`, `/part-time/` | 5-10% |
| Salary Range | `/luong-tren-20-trieu/` | 2-5% |
| Industry + Location | `/it-ho-chi-minh/` | 8-15% |

### Product/Detail Pages

| Detail Type | URL Pattern Examples | Typical Traffic Share |
|-------------|---------------------|----------------------|
| Job Posting | `/job/123456/`, `/tin-tuyen-dung/` | 0.1-2% |
| Company Profile | `/company/abc/`, `/nha-tuyen-dung/` | 10-20% |
| Similar Jobs | `/viec-lam-tuong-tu/` | 5-10% |

### Tools & Features

| Tool Type | Examples | Benchmark Traffic |
|-----------|----------|-------------------|
| CV Builder | CV templates, resume maker | 10-30% (TopCV) |
| Salary Calculator | Gross-Net calculator | 1-3% |
| Career Assessment | MBTI, skill test | 2-5% |
| Job Alerts | Email subscription | 0.5-1% |

## Benchmark Metrics (Vietnam Market 2024-2025)

| Metric | TopCV (Leader) | Industry Average |
|--------|----------------|------------------|
| Total Traffic | 1.5M+ | 400-600K |
| Category % | 45-55% | 40-55% |
| Company Pages | 15,000+ | 5,000-10,000 |
| Company Traffic % | 15-20% | 10-20% |
| Job Posting % | 1-3% | 0.1-1% |
| Tools % | 25-35% | 0-15% |
| Province Pages | 60+ | 50-70 |
| District Pages | 50-200 | 0-50 |

## Gap Analysis Templates

### Category Gap Analysis

```
For each category type, calculate:

1. Coverage Gap
   - Your pages: X
   - Benchmark pages: Y
   - Gap: (Y - X) / Y × 100%

2. Traffic Gap
   - Your traffic: A
   - Benchmark traffic: B
   - Gap: (B - A) / B × 100%

3. Efficiency Gap
   - Your traffic/page: A / X
   - Benchmark traffic/page: B / Y
   - Compare ratios

4. Priority
   - If Coverage Gap > 50% AND Traffic Gap > 70%: P0
   - If Traffic Gap > 50%: P1
   - If Coverage Gap > 30%: P2
   - Else: P3
```

### Location Coverage Matrix

```
Province Matrix:
| Province | Your Traffic | Benchmark | Gap | Priority |
|----------|-------------|-----------|-----|----------|
| HCM      | X           | Y         | Z%  | P?       |
| Hà Nội   | X           | Y         | Z%  | P?       |
| ...      | ...         | ...       | ... | ...      |

District Analysis (for major cities):
- HCM: 24 districts → check coverage
- Hà Nội: 30+ districts → check coverage
- Đà Nẵng: 8 districts → check coverage
```

### Industry Coverage Analysis

```
Industry Gap Table:
| Industry | Your Traffic | Your % | Benchmark | Gap |
|----------|-------------|--------|-----------|-----|
| IT/Tech  | X           | Y%     | Z         | W%  |
| Banking  | X           | Y%     | Z         | W%  |
| ...      | ...         | ...    | ...       | ... |

Key Industries to Track:
1. IT/Technology
2. Banking/Finance
3. Sales/Marketing
4. HR/Admin
5. Manufacturing
6. Logistics
7. Education
8. Healthcare
9. F&B/Hospitality
10. Real Estate
```

## Strategy Recommendations Template

### Quick Wins (1-4 weeks)
- Add Salary Calculator tool (+5-20K traffic potential)
- Create missing industry category pages
- Implement JobPosting schema markup
- Internal linking optimization

### Medium Term (1-3 months)
- Build CV Builder tool (+50-150K traffic potential)
- Scale company pages to benchmark level
- Create district-level pages for major cities
- Industry + Location combination pages

### Long Term (3-6 months)
- Full province coverage
- Career assessment tools
- Comprehensive company profile enhancement
- Content hub for each major industry

## Schema Markup Checklist

### JobPosting Schema (Required)
```json
{
  "@type": "JobPosting",
  "title": "Required",
  "description": "Required",
  "datePosted": "Required",
  "validThrough": "Recommended",
  "employmentType": "Recommended",
  "hiringOrganization": "Required",
  "jobLocation": "Required",
  "baseSalary": "Recommended"
}
```

### Organization Schema (Company Pages)
```json
{
  "@type": "Organization",
  "name": "Required",
  "url": "Required",
  "logo": "Recommended",
  "description": "Recommended",
  "numberOfEmployees": "Recommended",
  "address": "Recommended"
}
```

## Dashboard Metrics for Job Sites

### Executive Summary Cards
1. Total Traffic vs Benchmark
2. Category Coverage %
3. Company Pages Count
4. Tools Traffic %

### Charts to Include
1. Pie: Traffic distribution by page type
2. Bar: Industry coverage comparison
3. Bar: Location coverage comparison (negative = gap)
4. Radar: Category structure comparison
5. Line: Traffic projection (if implementing strategy)

### Tables to Include
1. Top 10 categories by traffic gap
2. Top provinces/cities by gap
3. Top industries by gap
4. Company page scale comparison
