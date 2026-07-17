# E-commerce SEO Gap Analysis

Detailed framework for analyzing E-commerce competitors (Shopee, Tiki, Lazada, specialty stores, etc.)

## Page Type Classification

### Category Pages (PLP - Product Listing Pages)

| Category Type | URL Pattern Examples | Typical Traffic Share |
|---------------|---------------------|----------------------|
| Main Category | `/dien-thoai/`, `/thoi-trang/` | 20-35% |
| Subcategory | `/dien-thoai/iphone/` | 15-25% |
| Brand | `/thuong-hieu/samsung/` | 10-20% |
| Attribute Filtered | `/ao-thun-mau-den/` | 5-10% |
| Price Range | `/dien-thoai-duoi-5-trieu/` | 3-8% |
| Sale/Promotion | `/flash-sale/`, `/khuyen-mai/` | 5-15% |
| Collection | `/bo-suu-tap-mua-he/` | 2-5% |

### Product Detail Pages (PDP)

| Detail Type | URL Pattern Examples | Typical Traffic Share |
|-------------|---------------------|----------------------|
| Product Page | `/p/iphone-15-pro-max/` | 15-30% |
| Brand Page | `/store/apple/` | 5-15% |
| Review Aggregate | `/danh-gia/san-pham/` | 2-5% |
| Compare Page | `/so-sanh/iphone-samsung/` | 1-3% |

### Supporting Pages

| Page Type | Examples | Traffic Share |
|-----------|----------|---------------|
| Blog/Guides | Buying guides, reviews, how-to | 10-25% |
| Tools | Price tracker, compare, wishlist | 2-5% |
| Account | Order tracking, wishlist | 1-3% |
| Homepage | Main homepage | 5-15% |

## Benchmark Metrics (E-commerce Vietnam)

### Large Marketplaces (Shopee, Lazada, Tiki)

| Metric | Marketplace Leader | Specialty Store |
|--------|-------------------|-----------------|
| Total Traffic | 50M+ | 500K-5M |
| Category % | 30-45% | 35-50% |
| Product Page % | 20-35% | 20-40% |
| Brand/Store % | 5-15% | 5-15% |
| Blog % | 5-15% | 10-25% |

### Category Page Efficiency

| Metric | Excellent | Good | Poor |
|--------|-----------|------|------|
| Traffic/Category URL | >500 | 100-500 | <100 |
| Products/Category | 50-200 | 20-50 | <20 |
| Avg. Depth (URL levels) | 2-3 | 3-4 | >4 |

## Gap Analysis Templates

### Category Taxonomy Gap

```
Taxonomy Depth Comparison:

Level 1 (Main Category)
├── Your coverage: X categories
├── Competitor coverage: Y categories
└── Gap: Missing categories list

Level 2 (Subcategory)
├── Your coverage: X subcategories
├── Competitor coverage: Y subcategories
└── Gap: Missing subcategories list

Level 3 (Attribute/Filter)
├── Your coverage: X attribute pages
├── Competitor coverage: Y attribute pages
└── Gap: Missing attribute combinations
```

### Product Page Analysis

```
Product Page Metrics:
| Metric | Your Site | Competitor | Gap |
|--------|-----------|------------|-----|
| Total Product Pages | X | Y | Z% |
| Avg. Traffic/Product | A | B | C% |
| Schema Coverage | D% | E% | F% |
| Review Integration | Yes/No | Yes/No | - |
| Related Products | Yes/No | Yes/No | - |
```

### Brand/Store Page Gap

```
Brand Coverage:
| Brand | Your Traffic | Competitor | Gap | Priority |
|-------|-------------|------------|-----|----------|
| Apple | X | Y | Z% | P? |
| Samsung | X | Y | Z% | P? |
| ... | ... | ... | ... | ... |

Store Page Metrics:
- Number of brand/store pages
- Avg. traffic per brand page
- Brand page completeness (logo, description, products)
```

## Visual Semantic Integration

### Category Page (PLP) Structure

```
[HEADER 5-10%] 
→ [H1 + Breadcrumb above fold]
→ [SIDEBAR 20-30%: Filters (Price, Brand, Attribute)]
→ [CENTERPIECE 60%: Product Grid]
→ [SUPPORTING 10%: Category SEO text, FAQ]
→ [FOOTER 5-10%]
```

### Product Page (PDP) Structure

```
[HEADER 5-10%]
→ [CENTERPIECE 60%: Product Image + Info + Add to Cart]
→ [SUPPORTING 30%: Specs, Reviews, Related]
→ [SUPPLEMENTARY 10%: Recently Viewed, Cross-sell]
→ [FOOTER 5-10%]
```

## Schema Markup Checklist

### Product Schema (Required)

```json
{
  "@type": "Product",
  "name": "Required",
  "description": "Required",
  "image": "Required",
  "brand": "Recommended",
  "offers": {
    "@type": "Offer",
    "price": "Required",
    "priceCurrency": "Required",
    "availability": "Required",
    "seller": "Recommended"
  },
  "aggregateRating": "Recommended",
  "review": "Recommended"
}
```

### BreadcrumbList Schema

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"position": 1, "name": "Home", "item": "/"},
    {"position": 2, "name": "Category", "item": "/category/"},
    {"position": 3, "name": "Product", "item": "/product/"}
  ]
}
```

### FAQPage Schema (Category Pages)

```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Câu hỏi 1?",
      "acceptedAnswer": {"@type": "Answer", "text": "Trả lời 1"}
    }
  ]
}
```

## Strategy Recommendations Template

### Quick Wins (1-4 weeks)
- Implement Product schema on all PDPs
- Add FAQ section to top category pages
- Create missing main category pages
- Optimize category page titles/meta

### Medium Term (1-3 months)
- Build attribute-filtered category pages
- Create brand landing pages
- Add buying guides for top categories
- Implement compare functionality

### Long Term (3-6 months)
- Full taxonomy expansion
- Review aggregation system
- Price tracking tools
- Comprehensive brand/store pages

## Dashboard Metrics for E-commerce

### Executive Summary Cards
1. Total Organic Traffic vs Benchmark
2. Category Pages Count & Coverage
3. Product Pages with Schema %
4. Blog Traffic Contribution

### Charts to Include
1. Pie: Traffic by page type (Category/Product/Blog/Other)
2. Bar: Top 10 category traffic gap
3. Bar: Brand/Store page coverage
4. Radar: Taxonomy depth comparison
5. Table: Product page schema audit

### Key Tables
1. Top categories by traffic gap
2. Missing brand pages
3. Attribute combinations to create
4. Blog topic gaps vs competitor
