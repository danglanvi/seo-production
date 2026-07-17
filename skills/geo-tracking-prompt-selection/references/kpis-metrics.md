# GEO KPIs & Metrics Tracking

## Core KPIs to Commit

| KPI | Description | Target | Tracking Frequency |
|-----|-------------|--------|-------------------|
| **Brand Mention** | Times brand appears in AI responses | >60% BOFU prompts | Daily |
| **AI Citations** | Citation count (Semrush/Ahrefs AI features) | Increasing trend | Weekly |
| **Share of Voice** | % mention vs competitors | >30% SOV | Monthly |
| **Information Accuracy** | AI describes brand correctly | >90% accurate | Monthly |

## Detailed Metrics

### 1. Brand Mention Metrics

**What to track:**
- Mention count per prompt
- Mention count trend over time
- Mention by AI platform (ChatGPT, Perplexity, Gemini, Claude)

**How to measure:**
```
Mention Rate = (Prompts with brand mention / Total prompts) × 100

Target by funnel:
- BOFU: >60%
- MOFU: >40%
- TOFU: >20%
```

### 2. AI Citations

**What to track:**
- Number of AI citations in Semrush/Ahrefs
- Citation sources (which pages get cited)
- Citation growth rate

**How to measure:**
- Semrush: Position Tracking → AI Overviews
- Ahrefs: Site Explorer → AI Citations (if available)
- Manual: Run prompts, note source citations

### 3. Share of Voice (SOV)

**What to track:**
- Brand mentions vs competitor mentions
- SOV by category/topic
- SOV trend over time

**How to measure:**
```
SOV = (Brand mentions / Total mentions including competitors) × 100

Example:
- Your brand: 15 mentions
- Competitor A: 12 mentions
- Competitor B: 8 mentions
- Competitor C: 5 mentions
- Total: 40 mentions
- Your SOV: 15/40 = 37.5%
```

### 4. Information Accuracy

**What to track:**
- Correct product/service descriptions
- Correct pricing (for e-commerce)
- Correct contact/location info
- Absence of negative misinformation

**How to measure:**
```
Accuracy Rate = (Accurate responses / Total responses with brand info) × 100

Check for:
✓ Product names correct
✓ Service descriptions accurate
✓ Pricing current (±5%)
✓ No false claims
✓ No competitor confusion
```

## Secondary Metrics

### Context Type Distribution

Track HOW brand is mentioned:

| Context Type | Description | Value |
|--------------|-------------|-------|
| **Recommendation** | AI recommends brand | High |
| **Comparison** | Brand in comparison list | Medium |
| **Information** | Neutral mention | Low |
| **Negative** | Critical mention | Alert |

**Target distribution:**
- Recommendation: >50%
- Comparison: 30-40%
- Information: <20%
- Negative: <5%

### Position in Response

When brand appears in lists:

| Position | Impact |
|----------|--------|
| #1-3 | High visibility |
| #4-7 | Medium visibility |
| #8+ | Low visibility |

**Target:** Top 3 position in >60% of list responses

### Competitor Tracking

Track same metrics for 5-7 competitors:
- Mention frequency
- Position
- Context type
- Accuracy

**Benchmark:** Your brand should outperform average competitor metrics

## Tracking Schedule

### Daily
- [ ] Run top 20 BOFU prompts
- [ ] Log mention counts
- [ ] Note any alerts (negative mentions, inaccuracies)

### Weekly
- [ ] Run full prompt list (all categories)
- [ ] Update mention rate trends
- [ ] Check competitor changes
- [ ] Identify content → citation wins

### Monthly
- [ ] Calculate Share of Voice
- [ ] Audit information accuracy
- [ ] Review context type distribution
- [ ] Generate monthly report
- [ ] Update/replace underperforming prompts

## Tools for Tracking

### Recommended Platforms

| Tool | Use Case | Key Features |
|------|----------|--------------|
| **Promptmonitor** | Comprehensive GEO | 250+ prompts, multi-model, competitor benchmarking |
| **SE Ranking** | AI visibility | Multi-platform, sentiment analysis |
| **AIClicks.io** | Cross-platform | Brand vs competitor, source identification |
| **Semrush** | AI citations | Position tracking with AI Overviews |

### DIY Tracking (Google Sheets)

**Tab 1: Prompt List**
| Prompt ID | Category | Intent | Prompt VN | Prompt EN |

**Tab 2: Daily Tracking**
| Date | Prompt ID | ChatGPT | Perplexity | Gemini | Claude | Notes |

**Tab 3: Monthly Summary**
| Month | Mention Rate | SOV | Accuracy | Top Performer | Underperformer |

## Reporting Template

### Monthly GEO Report Structure

```
1. Executive Summary
   - Overall mention rate: X%
   - SOV: X% (vs X% last month)
   - Key wins this month

2. Metrics Dashboard
   - Brand Mention: X% (target: 60%)
   - AI Citations: X (trend: ↑/↓)
   - Share of Voice: X%
   - Accuracy: X%

3. By Funnel Stage
   - BOFU: X% mention rate
   - MOFU: X% mention rate
   - TOFU: X% mention rate

4. Competitor Analysis
   - Brand vs Competitor A: X% vs Y%
   - Brand vs Competitor B: X% vs Y%

5. Top Performing Prompts
   - Prompt 1: X% mention rate
   - Prompt 2: X% mention rate

6. Underperforming Prompts (to replace)
   - Prompt X: 0% mention rate
   - Prompt Y: 10% mention rate

7. Recommendations
   - Content optimization needed for [topic]
   - New prompts to add: [list]
   - Prompts to retire: [list]

8. Next Month Focus
   - Priority actions
   - Seasonal considerations
```

## Alert Thresholds

Set up alerts for:

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Mention rate drop | >20% decrease week-over-week | Investigate immediately |
| Negative mention | Any negative context | Review and address |
| Inaccurate info | Critical misinformation | Urgent content update |
| Competitor surge | Competitor SOV >50% | Competitive analysis |
| New competitor | New brand appearing frequently | Add to tracking |
