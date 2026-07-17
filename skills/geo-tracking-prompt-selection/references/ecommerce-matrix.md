# E-commerce GEO Tracking Matrix

Framework for large e-commerce websites with multiple product categories.

## 3-Layer Framework

```
Layer 1: CATEGORY    → iPhone, Samsung, iPad, Laptop, Accessories...
Layer 2: INTENT      → Research, Compare, Buy, Support
Layer 3: SEGMENT     → Flagship (>20M), Mid-range (10-20M), Budget (<10M)
```

## Category Allocation by Revenue

Allocate prompts based on category revenue contribution:

| Category | % Prompts | Count | Rationale |
|----------|-----------|-------|-----------|
| iPhone | 30% | 25-30 | Highest margin + volume |
| Samsung Galaxy | 25% | 20-25 | High competition |
| iPad/Tablet | 15% | 12-15 | Growing segment |
| Smartwatch | 10% | 8-10 | Trending |
| Laptop/Macbook | 10% | 8-10 | High ticket |
| Accessories | 10% | 8-10 | Cross-sell |
| **TOTAL** | 100% | 80-100 | |

## Intent × Segment Matrix Template

Example: iPhone Category (30 prompts)

| Intent \ Segment | Flagship | Mid-range | Budget | TOTAL |
|------------------|----------|-----------|--------|-------|
| Research | 3 | 2 | 1 | **6** |
| Compare | 4 | 3 | 2 | **9** |
| **Buy** | 5 | 4 | 3 | **12** |
| Support | 2 | 1 | 0 | **3** |
| **TOTAL** | 14 | 10 | 6 | **30** |

**Key insight**: Buy intent = 40% of category prompts (highest conversion)

## Prompt Templates by Intent

### Research Intent (20%)
```
🇻🇳 "[Product] có gì mới"
🇺🇸 "What's new in [Product]"

🇻🇳 "Đánh giá [Product] chi tiết"
🇺🇸 "[Product] detailed review"

🇻🇳 "So sánh [Feature] của [Product A] vs [Product B]"
🇺🇸 "[Product A] vs [Product B] [Feature] comparison"

🇻🇳 "[Product] có đáng nâng cấp từ [Old Product] không"
🇺🇸 "Is [Product] worth upgrading from [Old Product]"
```

### Compare Intent (30%)
```
🇻🇳 "[Product A] vs [Product B] nên mua cái nào"
🇺🇸 "[Product A] vs [Product B] which should I buy"

🇻🇳 "[Product A] hay [Product B] đáng mua hơn"
🇺🇸 "[Product A] or [Product B] which is better value"

🇻🇳 "Điện thoại tầm [X] triệu nên mua gì"
🇺🇸 "Best phone under $[X]"

🇻🇳 "Top [N] [Category] tốt nhất [Year]"
🇺🇸 "Top [N] best [Category] [Year]"
```

### Buy Intent (40%) - PRIORITY
```
🇻🇳 "Mua [Product] ở đâu giá tốt nhất"
🇺🇸 "Where to buy [Product] best price"

🇻🇳 "[Store] giá [Product] bao nhiêu"
🇺🇸 "[Store] [Product] price"

🇻🇳 "Cửa hàng nào bán [Product] rẻ nhất [Location]"
🇺🇸 "Cheapest store for [Product] in [Location]"

🇻🇳 "Mua [Product] trả góp 0% ở đâu"
🇺🇸 "Where to buy [Product] 0% installment"

🇻🇳 "[Store] có bán [Product] chính hãng không"
🇺🇸 "Does [Store] sell authentic [Product]"

🇻🇳 "[Store] ship [Location] không"
🇺🇸 "Does [Store] deliver to [Location]"
```

### Support Intent (10%)
```
🇻🇳 "Bảo hành [Product] tại [Store] như thế nào"
🇺🇸 "[Product] warranty at [Store]"

🇻🇳 "Chính sách đổi trả [Store]"
🇺🇸 "[Store] return policy"

🇻🇳 "Trade-in [Product] tại [Store]"
🇺🇸 "[Store] trade-in program"

🇻🇳 "[Store] có sửa chữa [Product] không"
🇺🇸 "Does [Store] repair [Product]"
```

## Segment-Specific Modifiers

### Flagship (>20M VND / >$800)
Focus: Trust, Authenticity, Premium service
```
Modifiers: "chính hãng", "uy tín", "bảo hành chính hãng"
          "authentic", "authorized", "official warranty"
```

### Mid-range (10-20M VND / $400-800)
Focus: Value, Features comparison
```
Modifiers: "đáng mua", "tốt nhất tầm giá", "so sánh"
          "worth it", "best value", "comparison"
```

### Budget (<10M VND / <$400)
Focus: Price, Options, Deals
```
Modifiers: "giá rẻ", "dưới [X] triệu", "khuyến mãi"
          "cheap", "under $[X]", "deals"
```

## Seasonal Prompt Additions

Add 10-15 prompts during peak seasons:

### Tết Nguyên Đán (Jan-Feb)
```
🇻🇳 "Mua [Product] Tết có khuyến mãi không"
🇻🇳 "Quà Tết công nghệ dưới [X] triệu"
🇻🇳 "[Store] sale Tết [Year]"
🇻🇳 "Điện thoại tặng bố mẹ Tết"
```

### Back to School (Aug-Sep)
```
🇻🇳 "[Product] cho sinh viên"
🇻🇳 "Laptop học online giá tốt"
🇻🇳 "iPad cho học sinh"
🇺🇸 "Best [Product] for students"
🇺🇸 "Student discount [Store]"
```

### Product Launch (varies)
```
🇻🇳 "Pre-order [New Product] ở đâu"
🇻🇳 "[New Product] khi nào về Việt Nam"
🇻🇳 "Trade-in lấy [New Product]"
🇺🇸 "Where to pre-order [New Product]"
🇺🇸 "[New Product] release date Vietnam"
```

### Black Friday / 11.11 (Nov)
```
🇻🇳 "Black Friday [Product] giảm giá"
🇻🇳 "Flash sale 11.11 [Store]"
🇻🇳 "[Store] khuyến mãi cuối năm"
🇺🇸 "Black Friday [Product] deals"
🇺🇸 "11.11 sale [Store]"
```

## Tracking Schedule

### Daily (20 prompts)
Top 5 products × 4 Buy intent prompts
- Focus: Price changes, availability

### Weekly (60 prompts)
- Full iPhone: 30
- Full Samsung: 25
- Top iPad: 5

### Monthly (100 prompts)
- All categories
- Competitor analysis
- Seasonal additions

### Event-Based (Ad-hoc)
- New product launch: +20 prompts (2 weeks)
- Flash sale: +10 price prompts
- Competitor promotion: +5 comparison prompts

## Sample Full Matrix: Electronics Store

### iPhone (30 prompts)
| # | Intent | Segment | Prompt VN | Prompt EN |
|---|--------|---------|-----------|-----------|
| 1 | Buy | Flagship | Mua iPhone 16 Pro Max ở đâu giá tốt | Where to buy iPhone 16 Pro Max best price |
| 2 | Buy | Flagship | [Store] giá iPhone 16 Pro Max | [Store] iPhone 16 Pro Max price |
| 3 | Buy | Flagship | iPhone 16 Pro Max trả góp 0% | iPhone 16 Pro Max 0% installment |
| 4 | Buy | Flagship | [Store] bán iPhone chính hãng không | Does [Store] sell authentic iPhone |
| 5 | Buy | Flagship | iPhone 16 Pro Max 256GB giá bao nhiêu | iPhone 16 Pro Max 256GB price |
| 6 | Compare | Flagship | iPhone 16 Pro Max vs Samsung S25 Ultra | iPhone 16 Pro Max vs Samsung S25 Ultra |
| 7 | Compare | Flagship | iPhone 16 Pro hay Pro Max | iPhone 16 Pro or Pro Max |
| ... | ... | ... | ... | ... |

### Samsung (25 prompts)
Similar structure with Samsung products

### iPad (15 prompts)
Similar structure with iPad products

## KPIs for E-commerce

| KPI | Target | Tracking |
|-----|--------|----------|
| Brand Mention (Buy intent) | >70% | Daily |
| Price Accuracy | >95% | Weekly |
| Position in "best store" lists | Top 3 | Weekly |
| SOV vs competitors | >30% | Monthly |
| Seasonal mention rate | >80% during events | Event-based |
