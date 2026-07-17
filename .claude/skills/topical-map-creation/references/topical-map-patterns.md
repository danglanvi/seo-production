# Topical Map Patterns & Examples

## Contents

- [5 Components Template](#5-components-template)
- [Real Case Examples](#real-case-examples)
- [Entity-Attribute Pair Processing](#entity-attribute-pair-processing)
- [Context Augmentation Pattern](#context-augmentation-pattern)
- [Lexical Semantics Pattern](#lexical-semantics-pattern)
- [Query Dilemma Resolution Pattern](#query-dilemma-resolution-pattern)
- [Document Template Pattern](#document-template-pattern)
- [SCN Hierarchy Pattern](#scn-hierarchy-pattern)
- [Contextual Bridge Pattern](#contextual-bridge-pattern)
- [Core/Outer Connection Pattern](#coreouter-connection-pattern)
- [Raw Topical Map Template](#raw-topical-map-template)
- [Processed Topical Map Template](#processed-topical-map-template)

## 5 Components Template

```markdown
## Site: [Domain]
- **Source Context**: [How you make money]
- **Central Entity**: [What site is about]
- **Central Search Intent**: [Predicate/Verb + Entity]
- **Core Section**: [Monetization-focused topics]
- **Outer Section**: [Historical data topics]
```

## Real Case Examples

### vizem.net (Visa Consultancy)
```
Source Context: German Visa Consultancy
Central Entity: Germany + Visa
Central Search Intent: Know/Go + Germany
Core Section: Types of German Visas (Transit, Student, Tourist, Work...)
Outer Section: Residence Permit, Citizenship, Immigration, Consulate, Religion, Language School
```

### gymdesk.com (Gym Management Software)
```
Source Context: Trainer and Gym Management Software
Central Entity: Gym, Personal Trainer, Sport Branches
Central Search Intent: Opening and Managing a Gym Digitally; Finding a Personal Trainer
Core Section: Open a Gym, Manage a Gym
Outer Section: Martial Arts, Learning Athletism
```

### welzo.com (Health Encyclopedia)
```
Source Context: Health Encyclopedia and Telehealth Service
Central Entity: Health Problems and Solutions
Central Search Intent: Find a Correct (Diagnosis/Treatment/Drug/Doctor)
Core Section: Health Types (Women's/Men's/Sexual Health...) and Problems
Outer Section: Drug Encyclopedia, Immunity
```

### mangolanguages.com (Language Learning App)
```
Source Context: Language Learning App
Central Entity: Language and Linguistics
Central Search Intent: Learn (Speaking, Listening, Singing, Reading, Writing, Asking, Answering, Dreaming) in X Language
Core Section: European/Asian/African Language + Literature, Grammar, Art
Outer Section: Language Origin, Language History, Language Translation, Language Dictionary
```

**Strategy Note**: Created 2 topical maps (Language-specific + General Linguistics) then merged them.

### oscarwylee.com.au (Optometrist/Glasses)
```
Source Context: Optometrist and Glasses eCommerce
Central Entity: Eye Health and Glasses
Central Search Intent: Find Optometrist for Glasses
Core Section: Eye Health, Optometrist Appointments
Outer Section: Lenses, Frames, Hinges, Face Shapes
```

**Strategy Note**: Started with Outer Section (Face Shapes) as ignitor—impressions first, clicks followed.

### yamm.com (Email Merge Software)
```
Source Context: Email Merge Software
Central Entity: Mail Merge
Central Search Intent: Send Bulk Emails for Email Marketing
Core Section: Email Marketing and Email Types
Outer Section: Email Servers, Email Components, Email Services (Yahoo, Gmail...)
```

**Strategy Note**: Used Token Insertion for "Mail" + "Merge" to get all word distributions.

## Entity-Attribute Pair Processing

### Order of Processing
1. **Unique attributes first**: Differentiating qualifiers
2. **Root attributes**: Accuracy and comprehensiveness
3. **Rare attributes**: Qualification and signification

### Title Tag Generation Pattern
```
Entity: [Entity]
Attribute: [Attribute]
Title: [Number] [Adjective] [Attribute] of [Entity]: [Qualifier 1], [Qualifier 2], [Qualifier 3]

Example:
Entity: Water
Attribute: Benefits
Title: 20 Health Benefits of Drinking Water: Physical, Psychological, Nutritional
```

### URL Structure Pattern
```
Core: /[entity]/[main-attribute]
Outer: /[entity]/[secondary]/[tertiary]

Example:
Core: /germany/visa
Outer: /germany/life/culture
```

## Context Augmentation Pattern

### Step 1: Identify Predicate Entailments
```
Predicate "Learn" entails:
- Speaking
- Listening
- Singing
- Reading
- Writing
- Asking
- Answering
- Dreaming
```

### Step 2: Get Nouns for Each Entailment
```
What can you "Listen" in [Language]?
- Story
- Movie
- Podcast
- Song
- Conversation
```

### Step 3: Connect to Query Networks
```
"Listen English Story" → Query exists
"Listen English Podcast" → Query exists
"Learn English Dreaming" → No query (skip or different approach)
```

## Lexical Semantics Pattern

### Hypernym/Hyponym Distribution
```
Hypernym (Category): Email Types
├── Hyponym 1: Newsletter Mail
├── Hyponym 2: Birthday Mail
├── Hyponym 3: Welcome Mail
├── Hyponym 4: Discount Mail
└── Hyponym 5: Survey Mail
```

### Page Creation Decision
```
"Birthday Mail Merge" → No query candidate → DON'T create page
"Birthday Mail" → Query exists → CREATE page
└── Link to "Mail Merge" at bottom
```

## Query Dilemma Resolution Pattern

### When Query is Ambiguous
```
Query: "Email Generator"
Meaning 1: Generate email addresses
Meaning 2: Generate email text

Solution:
- TOP of page: Most probable meaning (Email Address Generator)
- BOTTOM of page: Second meaning (Email Text Generator)
- Link both to appropriate tools/pages
```

## Document Template Pattern

### Same Entity Type = Same Template
```
Entity Type: [Mail Type]
Template Structure:
1. How-To content (top)
2. Instruction List
3. Types/Templates
4. Internal link to Mail Merge (bottom)
```

### Template Modification by Attribute
```
"Newsletter Mail":
- Focus: Subscription, Format, Design
- Include: Template examples

"Survey Mail":
- Focus: Engagement, Response Rate
- Include: Template + Questions examples

"Birthday Mail":
- Focus: Personalization, Timing
- Include: Template + Greeting examples
```

## SCN Hierarchy Pattern

### Three Levels
```
Root → Seed → Node

Root: Main topic hub (linked from homepage)
Seed: Sub-categorization of root
Node: Individual articles
```

### Connection Rules
```
Nodes → link to → Seed
Seed → link to → Root
Root → link to → Homepage
Cross-links between related Seeds
```

### Example Structure
```
Homepage
└── Root: "German Visa Guide" (Core)
    ├── Seed: "Tourist Visa"
    │   ├── Node: "Tourist Visa Requirements"
    │   ├── Node: "Tourist Visa Application"
    │   └── Node: "Tourist Visa Processing Time"
    ├── Seed: "Student Visa"
    │   ├── Node: "Student Visa Requirements"
    │   └── Node: "Student Visa Documents"
    └── Seed: "Work Visa"
        ├── Node: "Work Visa Types"
        └── Node: "Blue Card Germany"

└── Root: "Life in Germany" (Outer)
    ├── Seed: "German Culture"
    │   └── Node: "German Traditions"
    └── Seed: "German Language"
        └── Node: "German Language Schools"
```

## Contextual Bridge Pattern

### Position in Document
```
Main Content (9-10 headings)
    ↓
[Contextual Bridge] ← Takes context from Main Entity to Source Context
    ↓
Supplementary Content
    ↓
Internal Links to Core Section
```

### Example
```
Article: "Newsletter Mail"
- Main Content: How to write newsletter
- Bridge: "How Newsletter Fits in Email Marketing Strategy"
- Supplementary: Link to "Mail Merge" and "Email Types"
```

### When NOT to Use Bridge
- Not enough query demand for bridge topic
- Article too short
- Direct connection obvious without bridge

## Core/Outer Connection Pattern

### Outer Section → Core Section Linking
```
Outer Article: "Face Shapes for Glasses"
├── Main Content about face shapes
├── Bridge: "How Face Shape Affects Glasses Selection"
└── Internal Link: → "Best Glasses Types" (Core)
                   → "Optometrist Appointments" (Core)
```

### Attribute Hierarchy in Outer
```
Most important attribute of Outer → Links to most important node of Core
Second attribute → Links to second important node

Example:
"German Drinks & Cuisine" (Outer) → "Tourist Visa" (Core) [food culture relevant to tourists]
"German Universities" (Outer) → "Student Visa" (Core) [education relevant to students]
```

## Raw Topical Map Template

```markdown
# Raw Topical Map: [Central Entity]

## Core Section (Source Context: [Source])
| Entity | Attribute | Priority |
|--------|-----------|----------|
| [Entity] | [Main Attr 1] | 1 |
| [Entity] | [Main Attr 2] | 2 |
| [Entity] | [Main Attr 3] | 3 |

## Outer Section (Historical Data)
| Entity | Attribute | Priority |
|--------|-----------|----------|
| [Entity] | [Minor Attr 1] | 4 |
| [Entity] | [Minor Attr 2] | 5 |

## Word Combinations (Token Insertion)
- [Word 1] + [Token]
- [Token] + [Word 1]
- [Word 1] + [Token] + [Word 2]
...
```

## Processed Topical Map Template

```markdown
# Processed Topical Map: [Central Entity]

## Core Section
| Title Tag | URL | Macro Context | Priority |
|-----------|-----|---------------|----------|
| [Title 1] | /entity/attr1 | [Context] | 1 |
| [Title 2] | /entity/attr2 | [Context] | 2 |

## Outer Section
| Title Tag | URL | Macro Context | Links to Core |
|-----------|-----|---------------|---------------|
| [Title 3] | /entity/outer/attr3 | [Context] | [Core Article] |

## Quality Nodes
- [ ] [Title 1] - Homepage featured
- [ ] [Title 2] - Homepage featured

## Trending Nodes
- [ ] [Trending Topic 1] - Links to [Core Article]
```


## Case Studies Summary (moved từ SKILL.md v2.0 — skill-creator trim)

| Site | Strategy | Key Insight |
|------|----------|-------------|
| MangoLanguages | 2 topical maps merged (Language + Linguistics) | Context Augmentation: "Learn" entails Speaking, Listening, etc. |
| Nasdaq | 2 separate topical maps, 800 articles, no backlinks | Brand search provides natural advantage |
| OscarWylee | Started with Outer Section (Face Shapes) | Outer as ignitor for re-ranking |
| MailMerge | Token insertion, mail types focus | No query for "Birthday Mail Merge" → focus on "Birthday Mail" |
| GymDesk | Redefined website to connect query network | Create connection from search language to natural language |
