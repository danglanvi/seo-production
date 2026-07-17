# Internal Linking Guide

> ⚠️ **Phạm vi file này (note 2026-07-07):** đây là lớp **PLANNING-TIME** — dùng khi thiết kế link architecture trong topical map. Luật **EXECUTION** (anchor 6 rules, position rules, threshold, link plan, Rule 59-60, Link-less Connection) có canonical owner là skill **`internal-linking`** (root `skills/internal-linking/`) — khi 2 bên lệch nhau, skill đó thắng. Không bổ sung luật execution mới vào file này.

## Core Philosophy

### Purpose of Internal Links
1. Increase search engine confidence during crawl and index
2. Increase crawl frequency
3. Increase relevance to webpage for specific topic
4. Pass PageRank
5. Use relevant anchor text to signal topic relevance

### Fundamental Principle
```
Linking everywhere from everywhere = Linking nowhere
```
Search engine must find contextually relevant crawl path that aligns with query relevance.

## Link Justification Method

### Pre-Link Context Building
Before placing an internal link, mention anchor text phrases 1-5 times in previous headings/paragraphs.

```
❌ Wrong:
"Learn more about [pH testing methods]."
(No prior mention of pH testing)

✓ Correct:
"pH testing is crucial for water quality assessment. Various pH testing 
approaches exist for different scenarios. Understanding pH testing 
fundamentals helps you choose the right method. Learn more about 
[pH testing methods]."
(Anchor mentioned 3 times before link)
```

### Why Justify Links?
- Creates contextual flow
- Increases clickability
- Passes more relevance
- Search engine understands link purpose

## Link Placement Rules

### Main Content Rules

| Position | Rule | Reason |
|----------|------|--------|
| First 9-10 headings | Minimal to NO links | Main content focus, no distraction |
| First word of paragraph | NEVER link | Poor extraction point |
| Top of Main Content | Only Source Context links | Most important position |
| Bottom of Main Content | More links allowed | Less relevance passed here |

### Supplementary Content Rules
- Bulk of internal links here
- Less distance between links
- Lower heading levels (H3, H4)
- Less PageRank passed per link

### Boilerplate Content
- Minimize links
- If over 150 links in boilerplate, search engine ignores internal links
- Clean navigation, not spam

## PageRank Distribution

### Limited Link Budget
```
Page with 20 outgoing links:
- Each link receives 1/20 of PageRank
- Too many links = diluted value

Page with 5 outgoing links:
- Each link receives 1/5 of PageRank
- More value per link
```

### Strategic Distribution

| Link Type | Quantity | PageRank |
|-----------|----------|----------|
| To Core Section | Few (2-3) | High per link |
| To Outer Section | More (5-7) | Medium per link |
| To Boilerplate | Minimal | Low per link |

## Anchor Text Strategy

### Rules
1. **Frequency limit**: Don't use same anchor text > 3 times site-wide
2. **Variation**: Change word order or use synonyms
3. **Alignment**: Anchor text + Title tag of target page must match
4. **Length**: Keep short (NOT 7+ words)
5. **Naturalness**: Avoid exact-match spam

### Anchor Text Variations
```
Target: "German Student Visa Guide"

Variations:
- "student visa in Germany"
- "German student visa"
- "visa for German students"
- "studying in Germany visa"
```

### Annotation Text Technique
Use weaker anchor text but surround with target phrases:

```
"The process for obtaining a German student visa involves several steps. 
Understanding student visa requirements helps applicants prepare properly. 
For detailed information, see our [comprehensive visa guide]."

- Anchor: "comprehensive visa guide" (weak/generic)
- Annotation: "German student visa", "student visa requirements" (target phrases around anchor)
```

## Reciprocal Linking

### Not Always Required
```
Page A → Page B (link)
Page B → Page A (NOT required)
```

### When to Skip Reciprocal
- Page A already ranks well (doesn't need PageRank boost)
- Avoiding link pattern detection
- Page B needs more support than Page A

### When to Use Reciprocal
- Both pages support each other contextually
- Building cluster authority
- Related topics that naturally reference each other

## Internal Link Conflict

### What is Conflict?
When internal link context doesn't match target page.

### Consequences
- Search engine may not crawl target
- Devalues the webpage
- Signals manipulation

### Prevention
```
❌ Conflict:
Anchor: "healthy breakfast recipes"
Target: Article about "German visa requirements"

✓ No Conflict:
Anchor: "visa application documents"
Target: Article about "German visa requirements"
```

## Link Position by Heading Level

### H2 Links
- Most prominent
- Most PageRank passed
- Use sparingly (1-2 max)

### H3 Links
- Medium prominence
- Medium PageRank
- More flexibility (2-4)

### H4+ Links
- Lower prominence
- Less PageRank
- Can use more (5+)

## Contextual Connection Pattern

### Distance Strategy
```
Main Content:
H2 - No link
  Content paragraph
H3 - No link
  Content paragraph
H4 - Possible link (to Source Context)
  Content paragraph
H2 - No link
  Content paragraph
...
H2 (Near bottom) - Link allowed
  Content paragraph with [internal link]

Supplementary:
H3 - Multiple links
  [link 1] and [link 2]
H4 - Multiple links
  [link 3], [link 4], [link 5]
```

### Why Distance Matters
- Increases clickability
- Shows importance/prominence to search engine
- More distance in Main Content = more valuable link

## A/B Testing Internal Links

### Log File Analysis Method
1. Take log files
2. Link pages from everywhere
3. Check if target pages get crawled
4. If not crawled → Search engine ignores internal links
5. Adjust strategy

### What to Test
- Link quantity per page
- Link position in content
- Anchor text variations
- Reciprocal vs one-way links

## Special Cases

### New Websites
- Use competitor's internal linking structure initially
- Not too similar (not duplicator)
- Not too different (need consensus)
- Diverge as you grow

### After Ranking
```
If article already ranks well:
- Remove unnecessary links to it
- Focus PageRank on struggling pages
- Don't waste link equity
```

### No Query Demand
If link target has no query demand:
- Don't over-link to it
- Use for contextual support only
- Minimal PageRank investment

## Link-Less Connections

### Definition
Connections through entity relationships, not hyperlinks.

### How It Works
- Same entities mentioned across pages
- Search engine understands relationship
- No explicit link needed

### When to Use
- Strong entity co-occurrence
- Obvious contextual relationship
- Avoiding over-linking

## Quality Nodes Internal Linking

### Links TO Quality Nodes
- From homepage
- From multiple seeds
- From related outer section articles
- High prominence positions

### Links FROM Quality Nodes
- To Core Section (primary)
- To related Seeds
- Minimal external links
- All links justified

## Outer to Core Linking Pattern

### Standard Pattern
```
Outer Article (bottom):
- Internal link to most relevant Core article
- Internal link to Root article
- Optional: Internal link to related Outer article
```

### Contextual Bridge First
```
Outer Article:
1. Main Content (no links)
2. Contextual Bridge section
3. Supplementary Content
   └── Link to Core Section HERE
```

## Common Mistakes to Avoid

| Mistake | Problem | Solution |
|---------|---------|----------|
| Linking from first word | Poor extraction | Link mid-paragraph |
| Same anchor 10+ times | Spam signal | Max 3 uses per anchor |
| 150+ links per page | All links ignored | Reduce to <50 content links |
| No context before link | Unjustified link | Mention anchor 1-5 times first |
| Linking everywhere | Diluted PageRank | Strategic, limited links |
| Fixed linking pattern | Manipulation signal | Vary positions and quantity |
