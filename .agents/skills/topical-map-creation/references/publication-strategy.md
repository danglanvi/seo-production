# Publication Strategy Guide

## Fundamental Principle

```
Publication Order Matters:
Publishing x, y, z ≠ Publishing z, y, x
```

Different order creates different:
- Query path recognition
- Historical data accumulation
- Contextual association in index

## Initial Launch Strategy

### The 20-30 Article Batch

**Day 1 Actions**:
1. Publish 20-30 high quality articles simultaneously
2. Feature them on homepage
3. Create internal links between them
4. Submit sitemap to Google Search Console

**Purpose**:
- Create reaction from search engine
- Signal: "This website has quality content"
- Invite crawlers to look deeper

### Pre-Launch Cleanup
Before publishing batch:
1. Delete unnecessary content
2. Merge corporate pages (privacy, about, contact) into single multi-layer page
3. Reduce total URL count
4. Increase value per page
5. Decrease cost per page

## Frequency Scaling Pattern

### Phase Model

| Phase | Articles | Frequency | Focus |
|-------|----------|-----------|-------|
| Launch | 20-30 | Same day | Quality nodes, Core Section |
| Establishment | 5-10 | 1/week | Core Section expansion |
| Growth | 20-30 | 2-3/week | Mix Core + Outer |
| Acceleration | 35+ | 5/day | Full topical map |
| Configuration | Updates | Ongoing | Review and update all |

### Configuration Phase
After completing topical map:
1. Check ranking data
2. Identify underperforming articles
3. Update content quality
4. Adjust internal links
5. Improve weak areas
6. Start from beginning again

## Competitor Frequency Analysis

### Process
1. **Extract competitor sitemaps**
2. **Check last modification dates**
3. **Aggregate data** (Python/Pandas recommended)
4. **Calculate their frequency**
5. **Go ABOVE their frequency**

### Example Analysis
```python
# Conceptual approach
competitor_urls = extract_sitemap("competitor.com")
for url in competitor_urls:
    modification_date = get_last_modified(url)
    
# Aggregate by week/month
# Calculate: articles per week/month
# Your target: Competitor frequency + 20-50%
```

### When You Can't Beat Frequency
If competitor publishes 100/week and you can only do 10/week:
- Go DEEPER instead of wider
- Focus on quality over quantity
- Target less competitive attributes

## Patternless Publishing

### Why Avoid Patterns?
- Fixed schedules signal automation
- Predictable = manipulable
- Natural sites don't follow rigid patterns

### How to Be Patternless
```
❌ Pattern:
Monday: 2 articles, 9am
Wednesday: 2 articles, 9am
Friday: 2 articles, 9am

✓ Patternless:
Week 1: Mon(3), Thu(1), Sat(4)
Week 2: Tue(2), Wed(3), Fri(1), Sun(2)
Week 3: Mon(5), Fri(3)
```

### Variables to Vary
- Day of week
- Time of day
- Number of articles
- Gap between publications

## Historical Data Building

### First: Impressions
```
Publish → Index → Impressions increase (first signal)
```

### Then: Clicks
```
Impressions → Rankings improve → Clicks increase (second signal)
```

### Timeline Expectation
- Impressions: Days to weeks
- Clicks: Weeks to months
- Ranking stability: Months

## Core Algorithm Update Timing

### When to Publish
- During "flat" algorithmic periods
- When rankings are stable
- Not during active Core Updates

### When to Pause/Reduce
- During Core Algorithm Updates
- When unexpected fluctuations occur
- During major Google announcements

### After Core Update
```
Positive impact → Accelerate publishing
Negative impact → Analyze, adjust, then resume
Neutral → Continue as planned
```

## Quality vs Quantity Balance

### Not Everything Must Be High Quality
```
Quality Nodes: 10-20% of content
- Detailed, comprehensive
- Core Section focus
- Homepage featured

Standard Nodes: 60-70% of content
- Good quality
- Covers topical map
- Proper structure

Basic Coverage: 10-20% of content
- Brief coverage acceptable
- Outer Section mostly
- Historical data purpose
```

### Quality Node Timing
1. **Early**: Publish Quality Nodes in initial batch
2. **Throughout**: Maintain quality node presence
3. **Updates**: Regularly refresh Quality Nodes

## Starting Point Strategy

### Option A: Start with Core Section (Standard)
```
Week 1-2: Core Quality Nodes
Week 3-4: Core Standard Nodes
Week 5-6: Add Outer Section
Week 7+: Balance and expand
```

**When to use**: Competitive enough to rank Core topics, clear monetization focus.

### Option B: Start with Outer Section (Ignitor)
```
Week 1-2: Easy-to-rank Outer topics
Week 3-4: Build impressions
Week 5-6: Start Core Section
Week 7+: Transfer authority to Core
```

**When to use**: Core Section too competitive, need historical data first.

### OscarWylee Example
```
Phase 1: "Face Shapes" articles (Outer) → Easy to rank
Phase 2: Impressions increase
Phase 3: "Eye Health" articles (Core) → Harder queries
Phase 4: Clicks increase
Phase 5: Authority transfer to "Glasses" (Core)
```

## Content Type Sequencing

### Within Same Day
If publishing multiple articles same day:
```
1. Root article first
2. Related Seed articles
3. Node articles
```

### Cross-Section Balance
```
Week 1: 70% Core, 30% Outer
Week 2: 60% Core, 40% Outer
Week 3: 50% Core, 50% Outer
Week 4+: Based on performance data
```

## Trending Topics Integration

### When to Publish Trending Content
- As soon as trend identified
- Before peak (not after)
- Connected to Central Entity

### How to Integrate
```
Trending: "AI in [Industry]"
Connect to: Central Entity
Link to: Core Section
Purpose: Capture traffic, transfer authority
```

### Google Discover Opportunity
- Popular/entertainment topics
- Timely content
- High-quality images
- Increases historical data

## A/B Testing Publication

### What to Test
- Batch size (20 vs 30 vs 50)
- Frequency (daily vs weekly)
- Timing (morning vs evening)
- Order (Core first vs Outer first)

### Measurement
- Impressions increase rate
- Crawl rate from log files
- Time to first ranking
- Click-through improvement

## Publication Checklist

### Pre-Publication
- [ ] Content meets quality standards
- [ ] Internal links justified
- [ ] Images optimized
- [ ] Schema markup added
- [ ] No duplicate content

### Publication Day
- [ ] Publish articles
- [ ] Feature on homepage (if Quality Node)
- [ ] Add to sitemap
- [ ] Submit to GSC (if important)
- [ ] Social signals (optional)

### Post-Publication
- [ ] Monitor indexing
- [ ] Track impressions
- [ ] Note initial rankings
- [ ] Plan next batch

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Publishing 1 article in 1M URL site | Won't be noticed | Batch publishing |
| Fixed schedule | Pattern detection | Vary timing |
| Only Core Section | Slow historical data | Mix in Outer Section |
| No homepage features | Quality not visible | Feature Quality Nodes |
| Ignoring competitor frequency | Being outpaced | Match or exceed |
| Publishing during Core Updates | Unstable results | Wait for stability |
