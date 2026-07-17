# Prompt Templates for SEO Gap Analysis

Các prompt templates để sử dụng khi upload dữ liệu Ahrefs Top Pages vào Claude.

---

## 1. FULL WEBSITE ANALYSIS (Single Competitor)

### Prompt Template

```
Phân tích SEO gaps cho [TÊN WEBSITE CLIENT] dựa trên dữ liệu Ahrefs Top Pages đính kèm.

**Loại website:** [Job Site / E-commerce / Service / Informational]

**Dữ liệu đính kèm:**
- File 1: [tên_file_client.csv] - Dữ liệu client
- File 2: [tên_file_competitor.csv] - Dữ liệu competitor (benchmark)

**Yêu cầu phân tích:**
1. Phân loại URLs theo page type (Category, Product/Detail, Blog, Tools, Homepage)
2. Tính traffic distribution % cho mỗi loại
3. So sánh với competitor và tính Gap %
4. Identify Critical/High/Medium gaps
5. Tạo dashboard React với biểu đồ:
   - Executive Summary (4 metrics chính)
   - Pie chart: Traffic distribution
   - Bar chart: Gap analysis by segment
   - Radar chart: Structure comparison
   - Strategy roadmap

**Output mong muốn:**
- Dashboard React artifact
- Bảng tổng hợp gaps với priority
- Action plan theo phases
```

### Ví dụ thực tế

```
Phân tích SEO gaps cho CareerViet dựa trên dữ liệu Ahrefs Top Pages đính kèm.

**Loại website:** Job Site

**Dữ liệu đính kèm:**
- careerviet_top_pages.csv - Dữ liệu client
- topcv_top_pages.csv - Dữ liệu TopCV (benchmark)

**Yêu cầu phân tích:**
1. Phân loại URLs theo page type (Category Jobs, Company Pages, Job Postings, Blog, Tools)
2. Tính traffic distribution % cho mỗi loại
3. So sánh với TopCV và tính Gap %
4. Identify Critical/High/Medium gaps
5. Tạo dashboard React với GTV branding

**Focus đặc biệt:**
- Location coverage (tỉnh/thành, quận/huyện)
- Industry coverage
- Tools traffic (CV Builder, Salary Calculator)
```

---

## 2. CATEGORY PAGES ONLY ANALYSIS

### Prompt Template

```
Phân tích SEO gaps cho CATEGORY PAGES của [TÊN WEBSITE].

**Loại website:** [Job Site / E-commerce / Service / Informational]

**Dữ liệu đính kèm:** [tên_file.csv] - Chỉ chứa Category/Listing pages

**Yêu cầu phân tích:**
1. Phân loại category types:
   - [Job Site]: Industry, Role, Location (Province/District), Experience Level
   - [E-commerce]: Main Category, Subcategory, Brand, Attribute, Price Range
   - [Service]: Service Type, Industry, Location
   - [Informational]: Topic Hub, Tag, Author Archive

2. Tính metrics:
   - Traffic per category type
   - Number of pages per type
   - Traffic/URL efficiency
   - Coverage completeness

3. So sánh với benchmark (nếu có)

4. Tạo visualizations:
   - Pie chart: Category type distribution
   - Bar chart: Top categories by traffic
   - Bar chart: Category gaps vs competitor
   - Table: Missing categories

**Output:** Dashboard React + Gap summary table + Recommendations
```

### Ví dụ - Job Site Category

```
Phân tích Category Pages của CareerViet vs TopCV.

**Dữ liệu:**
- careerviet_category_only.csv
- topcv_category_only.csv (benchmark)

**Focus:**
1. Location coverage:
   - Bao nhiêu tỉnh/thành?
   - Có district pages không?
   - Traffic per province

2. Industry coverage:
   - Top industries by traffic
   - Missing industries vs competitor

3. Role/Function coverage:
   - Top roles by traffic
   - Industry + Location combinations

**Output:** Dashboard với location map, industry breakdown, gap analysis
```

### Ví dụ - E-commerce Category

```
Phân tích Category Pages (PLP) của [Tên Shop] vs Shopee/Tiki.

**Dữ liệu:**
- client_plp_pages.csv
- competitor_plp_pages.csv

**Focus:**
1. Taxonomy depth:
   - Main categories coverage
   - Subcategory completeness
   - Attribute-filtered pages

2. Brand pages coverage

3. Price range pages

**Output:** Dashboard với taxonomy tree, brand coverage, filter pages gaps
```

---

## 3. PRODUCT/DETAIL PAGES ANALYSIS

### Prompt Template

```
Phân tích SEO gaps cho PRODUCT/DETAIL PAGES của [TÊN WEBSITE].

**Loại website:** [Job Site / E-commerce / Service / Informational]

**Dữ liệu đính kèm:** [tên_file.csv] - Chỉ chứa Detail pages

**Page types to analyze:**
- [Job Site]: Job Postings, Company Profiles, Similar Jobs
- [E-commerce]: Product Pages (PDP), Brand Pages, Review Pages
- [Service]: Service Detail, Case Studies, Portfolio
- [Informational]: Articles, Author Pages

**Metrics cần tính:**
1. Total pages count vs competitor
2. Traffic per page efficiency
3. Schema markup coverage (estimate from URL patterns)
4. Top performing pages

**Output:** 
- Scale gap analysis
- Efficiency comparison
- Schema checklist
- Scaling recommendations
```

### Ví dụ - Job Site Detail Pages

```
Phân tích Company Pages và Job Postings của CareerViet.

**Dữ liệu:**
- careerviet_company_pages.csv
- careerviet_job_postings.csv
- topcv_company_pages.csv (benchmark)

**Focus:**
1. Company Pages:
   - Total count vs TopCV
   - Traffic per company page
   - Top companies by traffic

2. Job Postings:
   - Total indexed jobs
   - Traffic efficiency
   - Schema implementation gaps

**Output:** Dashboard với company scale gap, job posting analysis
```

---

## 4. BLOG/CONTENT ANALYSIS

### Prompt Template

```
Phân tích SEO gaps cho BLOG CONTENT của [TÊN WEBSITE].

**Loại website:** [Job Site / E-commerce / Service / Informational]

**Dữ liệu đính kèm:** [tên_file.csv] - Chỉ chứa Blog/Article pages

**Yêu cầu phân tích:**

1. **Topical Relevance Analysis:**
   - Phân loại mỗi bài theo độ liên quan với core business:
     - CORE: Trực tiếp liên quan
     - ADJACENT: Liên quan nhưng không phải core
     - TANGENT: Trend-chasing, loosely related
     - IRRELEVANT: Không liên quan
   - Tính Relevance Ratio = (CORE + ADJACENT) / Total

2. **Content Type Distribution:**
   - How-To guides
   - Listicles (Top X, Best Y)
   - Reviews/Comparisons
   - News/Updates
   - Definitions (X là gì?)

3. **Traffic Analysis:**
   - Top articles by traffic
   - Traffic by topic cluster
   - Traffic by content type

4. **Gap vs Competitor:**
   - Missing topics
   - Underperforming topics
   - Content format gaps

**Output:** Dashboard với relevance breakdown, topic coverage, recommendations
```

### Ví dụ - Job Site Blog

```
Phân tích Blog Content của CareerViet vs TopCV.

**Dữ liệu:**
- careerviet_blog.csv
- topcv_blog.csv (benchmark)

**Focus:**
1. Relevance Ratio:
   - Bao nhiêu % bài viết về career/jobs?
   - Bao nhiêu % trend-chasing (12 cung, phong thủy...)?

2. Topic Coverage:
   - CV/Resume tips
   - Interview skills
   - Career advice
   - Industry insights
   - Salary/compensation

3. Content Quality Signals:
   - Avg. estimated word count (từ traffic patterns)
   - Author bylines present?

**Output:** Dashboard với relevance pie chart, topic gaps, pivot recommendations
```

---

## 5. MULTI-COMPETITOR COMPARISON

### Prompt Template

```
So sánh SEO performance của [CLIENT] với [N] competitors.

**Competitors:**
1. [Competitor 1] - Benchmark/Leader
2. [Competitor 2]
3. [Competitor 3]
...

**Dữ liệu đính kèm:**
- client_data.csv
- competitor1_data.csv
- competitor2_data.csv
- competitor3_data.csv

**Yêu cầu phân tích:**

1. **Overall Ranking:**
   - Total traffic ranking
   - Traffic efficiency ranking
   - Category structure score

2. **Per-Segment Comparison:**
   - Category pages: coverage, traffic, efficiency
   - Detail pages: scale, traffic
   - Blog: relevance, coverage
   - Tools: traffic contribution

3. **Strengths & Weaknesses Matrix:**
   - Mỗi competitor giỏi gì?
   - Client mạnh ở đâu?
   - Learn từ ai cho segment nào?

4. **Competitive Position:**
   - Client đứng thứ mấy overall?
   - Gap với #1 là bao nhiêu?
   - Realistic target position?

**Output:** 
- Comprehensive comparison dashboard
- Ranking table
- SWOT-style matrix
- Strategy recommendations per competitor
```

### Ví dụ - 4 Job Sites

```
So sánh CareerViet với 3 competitors trong thị trường Job Site Vietnam.

**Competitors:**
1. TopCV (Benchmark - #1)
2. VietnamWorks
3. Vieclam24h

**Dữ liệu:**
- careerviet_full.csv
- topcv_full.csv
- vietnamworks_full.csv
- vieclam24h_full.csv

**Focus đặc biệt:**
1. Job Listing segment (Category + Job Posts + Company)
2. Blog segment (riêng)
3. Tools segment

**Output:**
- 4-site comparison dashboard
- Ranking by segment
- "Learn from" recommendations
- 6-month roadmap để cải thiện position
```

---

## 6. PITCHING DASHBOARD CREATION

### Prompt Template

```
Tạo Pitching Dashboard cho client [TÊN CLIENT] để present SEO gaps và strategy.

**Context:**
- Client industry: [Industry]
- Website type: [Job Site / E-commerce / Service / Informational]
- Meeting type: [Initial pitch / Strategy review / Quarterly report]

**Dữ liệu đã phân tích:** [Reference previous analysis hoặc attach data]

**Dashboard Requirements:**

1. **Executive Summary Slide:**
   - 4 key metrics với traffic light colors
   - Overall gap % vs benchmark
   - One-line verdict

2. **Gap Analysis Section:**
   - Visual: Radar chart comparing structure
   - Visual: Bar chart showing gaps by segment
   - Table: Top 5 critical gaps với priority

3. **Opportunity Section:**
   - Traffic potential if gaps fixed
   - Quick wins list (1-4 weeks)
   - Major initiatives (1-6 months)

4. **Roadmap Section:**
   - Phase-based action plan
   - Timeline với milestones
   - Expected traffic projection chart

5. **Investment/ROI Section (optional):**
   - Effort estimates
   - Expected returns
   - Timeline to results

**Branding:**
- Colors: GTV palette (Primary: #00CCFF, Accent: #850DBA)
- Style: Professional, data-driven, minimal text
- Tone: Confident but not aggressive

**Output:** React dashboard artifact ready for screenshare/presentation
```

---

## 7. QUICK ANALYSIS PROMPTS

### Nhanh - Traffic Distribution

```
Phân tích traffic distribution cho [tên_file.csv]:
- Phân loại URLs theo page type
- Tính % traffic mỗi loại
- So sánh với benchmark [40-60% category, 5-20% product, 15-30% blog]
- Highlight anomalies
```

### Nhanh - Location Coverage

```
Phân tích location coverage từ [tên_file.csv]:
- List tất cả provinces/cities có pages
- Traffic per location
- Identify missing locations vs [danh sách 63 tỉnh/thành]
- Top/Bottom performers
```

### Nhanh - Top Performers

```
Từ [tên_file.csv], identify:
- Top 20 pages by traffic
- Pattern analysis: Loại content nào perform tốt nhất?
- Keyword patterns trong top performers
- Recommendations dựa trên top performers
```

### Nhanh - Gap Identification

```
So sánh [client.csv] vs [competitor.csv]:
- Tìm categories có ở competitor mà client không có
- Tìm categories client có nhưng traffic thấp hơn >50%
- Prioritize gaps theo traffic potential
- Output: Gap table với Priority column
```

---

## 8. DATA PREPARATION NOTES

### Ahrefs Export Settings

Khi export từ Ahrefs Top Pages, ensure:
- Columns: URL, Traffic, Keywords, Top Keyword, Position
- Sort by: Traffic (descending)
- Limit: 10,000-50,000 rows recommended
- Format: CSV

### Data Cleaning Notes

Trước khi upload, có thể:
- Remove duplicate URLs
- Remove URLs với traffic = 0
- Separate by subdomain nếu cần (blog.domain.com vs domain.com)

### Naming Convention

Suggested file naming:
```
[client]_[segment]_[date].csv

Examples:
- careerviet_full_2025jan.csv
- careerviet_joblisting_2025jan.csv
- careerviet_blog_2025jan.csv
- topcv_benchmark_2025jan.csv
```

---

## 9. FOLLOW-UP PROMPTS

### Sau khi có dashboard, có thể hỏi thêm:

```
Drill down vào [segment cụ thể]:
- Phân tích chi tiết hơn cho [Industry/Location/Category]
- So sánh subcategories
- Identify micro-gaps
```

```
Tạo action plan chi tiết cho Phase [X]:
- Breakdown tasks
- Resource estimates
- Timeline với dependencies
- Success metrics
```

```
Export analysis thành [format]:
- Word document report
- PowerPoint slides
- Excel với data tables
- Notion-friendly markdown
```

```
Simulate traffic projection:
- Nếu fix [specific gaps], traffic tăng bao nhiêu?
- Timeline để đạt [target traffic]
- ROI calculation
```
