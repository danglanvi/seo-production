# Query Processing: Filtering, Scoring & Clustering

## Three Filtering Criteria

| Criteria | Definition | Question to Ask | Weight |
|----------|------------|-----------------|--------|
| **Relevance** | Connection to Source Context/monetization | "Does this query relate to how we make money?" | High (×2) |
| **Prominence** | Importance to entity definition | "Can Central Entity be defined without this attribute?" | Medium (×1) |
| **Popularity** | Search volume and demand | "How many people search for this?" | LOG(×2) |

---

## Attribute Prominence Examples

**Central Entity: Germany**

| Attribute | Prominence | Reason |
|-----------|------------|--------|
| Population | HIGH | Germany cannot be defined without population |
| Area | HIGH | Geographic size is definitional |
| Capital | HIGH | Berlin is part of Germany's identity |
| German League | LOW | Germany exists without football league |

**Central Entity: iPhone**

| Attribute | Prominence | Reason |
|-----------|------------|--------|
| Screen | HIGH | iPhone cannot exist without screen |
| Battery | HIGH | Power is essential to function |
| Camera | HIGH | Key feature of modern iPhones |
| Headphone Jack | LOW | Modern iPhones exist without it |

---

## RPP Score Formula

```
RPP Score = (Relevance × 2) × (Prominence × 1) × (LOG(Popularity + 1) × 2)
```

### Scoring Scale

**Relevance (1-10)**:
- 10: Directly leads to conversion/monetization
- 7-9: Strongly related to Core Section
- 4-6: Related to Outer Section
- 1-3: Loosely connected to Central Entity

**Prominence (1-10)**:
- 10: Entity cannot be defined without this attribute
- 7-9: Major defining characteristic
- 4-6: Common but not essential attribute
- 1-3: Minor or rare attribute

**Popularity**: Raw search volume (monthly)

### Example Calculation

**Query**: "iPhone screen repair" (iPhone Repair Source Context)

| Factor | Score |
|--------|-------|
| Relevance | 9 (direct service) |
| Prominence | 10 (screen essential) |
| Popularity | 12,000/month |

```
RPP = (9 × 2) × (10 × 1) × (LOG(12001) × 2)
RPP = 18 × 10 × 8.16 = 1,468.8
```

**Query**: "iPhone ringtone download" → RPP = 93.6 (Low relevance=2, Low prominence=3)

**Decision**: Prioritize "iPhone screen repair" (1,468.8) >> "iPhone ringtone download" (93.6)

---

## Trending Factor

When two queries have equal RPP scores:
- Check Google Trends for both queries
- Prioritize the one with upward trend
- Trending = higher crawl priority + Google Discover potential

**Tools**: Google Trends, Glimpse (meetglimpse.com), Exploding Topics

---

## SERP-Based Query Clustering

### Method
**Threshold = 3**: If 3+ top search results for two queries are identical → queries have same intent → cluster together.

### Why It Works
Google has determined user intent through millions of searches. Similar SERPs = same user intent = same page can satisfy both.

### Manual Review Process
1. Review SERPs for each unclustered query
2. Check titles and meta descriptions of ranking pages
3. Decide: Add to existing cluster OR create separate page

### Tools
- Keyword Cupid (keywordcupid.com)
- Key Clusters (keyclusters.com)
- Keyword Insights (keywordinsights.ai)
- SEO Utils (seoutils.app)

---

## Page Creation Decision Framework

| Scenario | Decision | Reason |
|----------|----------|--------|
| Queries have same SERP (3+ overlap) | Single page | Same user intent |
| Queries have different SERP | Separate pages | Different intent |
| Low volume, related to high volume | Single page | Consolidate authority |
| High volume, unique intent | Dedicated page | Capture full demand |

**Principle**: Create fewer, stronger pages with more value (Information + Action).

---

## Prioritization Matrix

### By RPP Score + Section

| RPP Score | Core Section | Outer Section |
|-----------|--------------|---------------|
| 1000+ | Priority 1 | Priority 2 |
| 500-999 | Priority 2 | Priority 3 |
| 100-499 | Priority 3 | Priority 4 |
| <100 | Evaluate for merge | Low priority/skip |

### Attribute Filtration Decision

| Combination | Section | Priority |
|-------------|---------|----------|
| High Prominence + High Popularity + High Relevance | Core | 1 |
| High Popularity + Low Relevance | Outer | 3 |
| High Relevance + Low Popularity | Core (Strategic) | 2 |
| Low all three | Skip | - |

---

## Workflow Summary

1. **Export all queries** from Token Insertion + Competitor Analysis
2. **Score each query** using RPP formula
3. **Sort by RPP score** (highest to lowest)
4. **Run SERP clustering** on top 50-100 queries
5. **Review clusters** manually for accuracy
6. **Assign to sections** (Core vs Outer)
7. **Prioritize within sections** based on RPP + strategic value
8. **Identify Quality Node candidates** (highest RPP in Core)
9. **Identify Trending Node opportunities** (high trend + connects to Core)


## Token Insertion Methodology (moved từ SKILL.md v2.0 — skill-creator trim)

Với 2-word Central Entity (vd "Mail Merge"), sinh queries theo 10 distribution patterns:

```
Optional Token + [1st Word]
Optional Token + [1st Word] + Optional Token
[1st Word] + Optional Token
Optional Token + [2nd Word]
Optional Token + [2nd Word] + Optional Token
[2nd Word] + Optional Token
Optional Token + [Both Words]
Optional Token + [Both Words] + Optional Token
[Both Words] + Optional Token
[1st Word] + Optional Token + [2nd Word]
```

Ví dụ "Mail Merge": "how to mail merge" · "mail merge in Word" · "birthday mail" (không có demand cho "Birthday Mail Merge" → focus "Birthday Mail").
