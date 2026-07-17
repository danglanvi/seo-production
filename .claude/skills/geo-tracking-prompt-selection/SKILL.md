---
name: geo-tracking-prompt-selection
description: "GEO (Generative Engine Optimization) prompt selection and tracking framework for optimizing brand visibility on AI search engines (ChatGPT, Perplexity, Gemini, Claude). Use this skill when: (1) Creating GEO tracking prompt lists for clients, (2) Selecting prompts by funnel stage (TOFU/MOFU/BOFU), (3) Building prompt matrices for e-commerce websites, (4) Setting up GEO KPIs and tracking metrics, (5) Advising on GEO strategy for service or e-commerce businesses. Supports both Vietnamese (VN) and English (US) markets."
---

# GEO Tracking & Prompt Selection Skill

Framework for selecting and organizing prompts to track brand visibility on AI search engines.

## Quick Decision: Website Type

First, determine website type to choose the right approach:

| Question | Service/Agency | E-commerce |
|----------|---------------|------------|
| Number of products/services | 1-10 | 50+ |
| User searches by | Brand name | Product name |
| Decision cycle | Long (weeks) | Short (<1 week) |
| **Approach** | Funnel-based (28-40 prompts) | Matrix-based (80-100 prompts) |

## Workflow

### For Service/Agency Websites
1. Identify 1-3 core services
2. List 5-7 competitors
3. Apply funnel allocation: TOFU 15% → MOFU 35% → BOFU 50%
4. Use templates from [prompt-templates.md](references/prompt-templates.md)
5. Set KPIs per [kpis-metrics.md](references/kpis-metrics.md)

### For E-commerce Websites
1. Identify top revenue categories (allocate prompts by revenue %)
2. List 5-7 competitors
3. Build 3-layer matrix: Category × Intent × Price Segment
4. See detailed matrix in [ecommerce-matrix.md](references/ecommerce-matrix.md)
5. Add seasonal prompts (Tết, Black Friday, Product launches)

## Funnel Allocation (Service/Agency)

| Stage | % | Prompts | Focus |
|-------|---|---------|-------|
| **BOFU** | 50% | 15-20 | Comparison, Pricing, Reviews |
| **MOFU** | 35% | 10-15 | Features, Use cases, Top lists |
| **TOFU** | 15% | 3-5 | Educational, Awareness |

## BOFU Prompt Types (Highest Priority)

### 1. Comparison Prompts
```
🇻🇳: "[Brand] vs [Competitor]", "Công ty [X] nào tốt nhất tại [Location]"
🇺🇸: "[Brand] vs [Competitor]", "Best [X] company in [Location]"
```

### 2. Pricing Prompts
```
🇻🇳: "Giá [sản phẩm]", "Chi phí [dịch vụ]", "Báo giá [X]"
🇺🇸: "[Product] pricing", "[Service] cost", "How much does [X] cost"
```

### 3. Trust/Review Prompts
```
🇻🇳: "Đánh giá [Brand]", "[Brand] có uy tín không", "[Brand] lừa đảo hay uy tín"
🇺🇸: "[Brand] reviews", "Is [Brand] legit", "Should I trust [Brand]"
```

## Prompt Formula

```
[Product/Brand] + [Intent Action] + [Modifier]

Examples:
🇻🇳: [iPhone 16 Pro Max] + [mua ở đâu] + [giá tốt nhất TPHCM]
🇺🇸: [iPhone 16 Pro Max] + [where to buy] + [best price HCMC]
```

## KPIs to Commit

| KPI | Description | Target |
|-----|-------------|--------|
| Brand Mention | Times brand appears in AI responses | >60% BOFU prompts |
| AI Citations | Citation count in Semrush/Ahrefs | Increasing trend |
| Share of Voice | % mention vs competitors | >30% SOV |
| Information Accuracy | AI describes brand correctly | >90% accurate |

## References

- **Prompt Templates**: See [prompt-templates.md](references/prompt-templates.md) for complete bilingual templates by industry
- **E-commerce Matrix**: See [ecommerce-matrix.md](references/ecommerce-matrix.md) for Category × Intent × Segment framework
- **KPIs & Metrics**: See [kpis-metrics.md](references/kpis-metrics.md) for detailed tracking setup
- **Checklist**: See [checklist.md](references/checklist.md) for BD consultation checklist

## Red Flags to Avoid

❌ Generic prompts ("What is SEO?") - No conversion value
❌ Too many prompts (>100 service, >150 e-commerce)
❌ Only tracking mention count without context
❌ Not updating prompts for new products/competitors
❌ Promising specific rankings - GEO is not deterministic like SEO

## Best Practices

✅ Focus 50% on BOFU - Highest conversion
✅ Track context type, not just mention count
✅ Monthly iteration - Replace underperformers
✅ Include competitors for benchmarking
✅ Add seasonal prompts for e-commerce
✅ Bilingual prompts for VN + US markets
