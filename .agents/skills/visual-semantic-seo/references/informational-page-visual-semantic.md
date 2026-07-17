# Informational Page Visual Semantic - Implementation Guide

## Contents

- [Page Types in Informational/Educational Sites](#page-types-in-informationaleducational-sites)
- [Encyclopedia / A-Z List Page](#encyclopedia-a-z-list-page)
- [How-To / Tutorial Page](#how-to-tutorial-page)
- [Glossary / Definition Page](#glossary-definition-page)
- [Informational Page Visual Semantic Checklist](#informational-page-visual-semantic-checklist)
- [Schema.org for Informational Pages](#schemaorg-for-informational-pages)

## Page Types in Informational/Educational Sites

| Page Type | Primary Intent | Centerpiece Focus |
|-----------|---------------|-------------------|
| **Encyclopedia/A-Z List** | Browse, Discover | Entity list + individual entries |
| **How-To/Tutorial** | Learn process | Step-by-step guide |
| **Glossary/Definition** | Understand term | Definition + context |
| **Comparison Article** | Compare options | Comparison table + analysis |
| **Long-form Educational** | Deep learning | Structured content hierarchy |

---

## Encyclopedia / A-Z List Page

### Example: "Animals That Start With A" (Animal Pedia)

### Centerpiece Annotation

```
[HEADER - 5-10% weight]
  Navigation + Alphabet bar (A-Z)

[ABOVE FOLD - CENTERPIECE SIGNALS]
  H1: "Animals That Start With A" 
  Author + Fact-checker + Date (E-E-A-T)
  General Summary (Extractive + Abstractive)
  Quick Stats: "200+ animals | 99 Mammals | 22 Reptiles"
  
  [FUNCTIONAL ELEMENTS]
  Search: "Find an animal..."
  Filter: [All] [Mammals] [Reptiles] [Birds]

[MAIN CONTENT - 100% weight]
  [FEATURED SECTION - Highest prominence]
  H2: "Most Popular Animals Starting with A"
  Jump-link table (Top 19)
  
  [ENTITY ENTRIES - Centerpiece]
  ├─ H3: 1. Alpaca
  │  ├─ Image + Caption
  │  ├─ Quick Facts Table
  │  └─ Description paragraphs
  ├─ H3: 2. Ass (Donkey)
  └─ ... more entries

  [CATEGORY SECTIONS]
  H2: Mammals That Start With A
  H2: Reptiles That Start With A
  H2: Birds That Start With A

[SUPPORTING - 60% weight]
  Conservation CTA
  Related A-Z pages
  Educational resources

[SIDEBAR - 20-40% weight]
  Table of Contents (sticky)
  Newsletter signup
  Quick navigation

[FOOTER - 5-10%]
```

### Visual Weight Distribution

| Element | Weight | Position/Size |
|---------|--------|---------------|
| H1 Page Title | 100% | 36px+, top |
| Alphabet Navigation | 80% | Sticky, prominent |
| Search/Filter | 80% | Above entries |
| Featured Section | 100% | First main section |
| Individual Entries | 80-100% | Uniform cards |
| Entry Images | 60% | Consistent size |
| Quick Facts Tables | 80% | Structured data |
| Category Headings | 80% | Clear dividers |
| TOC Sidebar | 30% | Narrow, sticky |

### HTML Structure

```html
<body>
  <header>
    <nav class="main-nav">...</nav>
    
    <!-- ALPHABET NAVIGATION - Educational site signature -->
    <nav class="alphabet-nav" aria-label="Browse by letter">
      <ul>
        <li><a href="/animals-a/" class="active" aria-current="page">A</a></li>
        <li><a href="/animals-b/">B</a></li>
        <!-- ... Z -->
      </ul>
    </nav>
  </header>
  
  <main>
    <article itemscope itemtype="https://schema.org/Article">
      <!-- ABOVE FOLD -->
      <header class="article-header">
        <h1 itemprop="headline">Animals That Start With A</h1>
        
        <!-- E-E-A-T Signals -->
        <div class="meta">
          <span itemprop="author">By Lucia Nguyen</span>
          <span>Fact-checked by Ph.D. Hoàng Xuân Quang</span>
          <time itemprop="dateModified" datetime="2025-12-13">Dec 13, 2025</time>
        </div>
        
        <!-- GENERAL SUMMARY -->
        <div class="introduction" itemprop="description">
          <p><strong>Animals that start with A</strong> include over 200 species 
          across mammals, reptiles, birds, amphibians, and invertebrates.</p>
          <!-- Extractive + Abstractive summary -->
        </div>
        
        <!-- QUICK STATS -->
        <div class="quick-stats">
          <span class="stat"><strong>200+</strong> Animals</span>
          <span class="stat"><strong>99</strong> Mammals</span>
          <span class="stat"><strong>22</strong> Reptiles</span>
          <span class="stat"><strong>23</strong> Birds</span>
        </div>
      </header>
      
      <!-- FUNCTIONAL ELEMENTS -->
      <section class="tools">
        <div class="search-box">
          <label for="animal-search">Find an animal:</label>
          <input type="search" id="animal-search" placeholder="Search by name...">
        </div>
        
        <div class="filters">
          <button class="filter active" data-filter="all">All (200+)</button>
          <button class="filter" data-filter="mammal">Mammals (99)</button>
          <button class="filter" data-filter="reptile">Reptiles (22)</button>
          <button class="filter" data-filter="bird">Birds (23)</button>
        </div>
      </section>
      
      <!-- FEATURED SECTION - CENTERPIECE -->
      <section id="most-popular" aria-labelledby="popular-heading">
        <h2 id="popular-heading">Most Popular Animals That Start With A</h2>
        
        <p>The 19 most searched animals beginning with A, featuring diverse 
        species from the Alpaca to the Axolotl.</p>
        
        <!-- Jump-link table -->
        <table class="jump-links">
          <caption>Quick Navigation - Most Popular Animals</caption>
          <tbody>
            <tr>
              <td><a href="#alpaca">Alpaca</a></td>
              <td><a href="#ass">Ass</a></td>
              <td><a href="#ants">Ants</a></td>
            </tr>
            <!-- More rows -->
          </tbody>
        </table>
        
        <!-- INDIVIDUAL ENTRIES -->
        <article id="alpaca" class="animal-entry" 
                 itemscope itemtype="https://schema.org/Thing">
          <header>
            <h3 itemprop="name">1. Alpaca</h3>
            <div class="entry-actions">
              <button class="btn-save" aria-label="Save Alpaca">♡ Save</button>
              <button class="btn-share" aria-label="Share">Share</button>
            </div>
          </header>
          
          <figure>
            <img itemprop="image" 
                 src="alpaca.jpg" 
                 alt="Three alpacas with soft wool standing in Andes Mountains grassland">
            <figcaption>Alpacas thrive in the high-altitude grasslands of the Andes Mountains</figcaption>
          </figure>
          
          <table class="quick-facts">
            <caption>Alpaca (Vicugna pacos) Quick Facts</caption>
            <thead>
              <tr>
                <th scope="col">Attribute</th>
                <th scope="col">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Scientific Name</th>
                <td itemprop="alternateName">Vicugna pacos</td>
              </tr>
              <tr>
                <th scope="row">Classification</th>
                <td>Mammal (Family Camelidae)</td>
              </tr>
              <tr>
                <th scope="row">Size</th>
                <td>32-39 inches (81-99 cm) at shoulder</td>
              </tr>
              <tr>
                <th scope="row">Weight</th>
                <td>121-143 lbs (55-65 kg)</td>
              </tr>
              <tr>
                <th scope="row">Lifespan</th>
                <td>15-20 years</td>
              </tr>
              <tr>
                <th scope="row">Habitat</th>
                <td>High-altitude grasslands, Andes Mountains, South America</td>
              </tr>
              <tr>
                <th scope="row">Diet</th>
                <td>Herbivore (grasses, hay, vegetation)</td>
              </tr>
              <tr>
                <th scope="row">Conservation</th>
                <td>Domesticated</td>
              </tr>
              <tr>
                <th scope="row">Notable Feature</th>
                <td>Hypoallergenic wool, 22 natural colors</td>
              </tr>
            </tbody>
          </table>
          
          <div itemprop="description">
            <p><strong>Alpaca</strong> (<em>Vicugna pacos</em>), a member of the 
            Camelidae family, lives in high-altitude grasslands and plains of the 
            Andes Mountains in South America...</p>
          </div>
        </article>
        
        <!-- More animal entries... -->
      </section>
      
      <!-- CATEGORY SECTIONS -->
      <section id="mammals" aria-labelledby="mammals-heading">
        <h2 id="mammals-heading">Mammals That Start With A</h2>
        <!-- Mammal entries -->
      </section>
      
      <section id="reptiles" aria-labelledby="reptiles-heading">
        <h2 id="reptiles-heading">Reptiles That Start With A</h2>
        <!-- Reptile entries -->
      </section>
      
      <!-- SUPPORTING CONTENT -->
      <section class="conservation-cta">
        <h2>Help Protect These Animals</h2>
        <p>5 species on this page are endangered. Support conservation efforts.</p>
        <a href="/conservation/" class="btn-donate">Learn More</a>
      </section>
      
    </article>
  </main>
  
  <!-- SIDEBAR -->
  <aside class="sidebar">
    <nav class="toc" aria-label="Table of Contents">
      <h2>On This Page</h2>
      <ul>
        <li><a href="#most-popular">Most Popular (19)</a></li>
        <li><a href="#mammals">Mammals (99)</a></li>
        <li><a href="#reptiles">Reptiles (22)</a></li>
        <li><a href="#birds">Birds (23)</a></li>
      </ul>
    </nav>
    
    <div class="newsletter">
      <h3>Get Animal Updates</h3>
      <form>
        <input type="email" placeholder="Your email">
        <button type="submit">Subscribe</button>
      </form>
    </div>
  </aside>
  
  <footer>...</footer>
</body>
```

### Visual Semantic for Large Lists

**Problem:** 200+ items with equal weight → No centerpiece signal

**Solution: Tiered Visual Prominence**

```
TIER 1: Featured/Most Popular (1-19)
├─ Large images (400x300)
├─ Full quick facts table
├─ Complete description
├─ All interactive elements
└─ Visual weight: 100%

TIER 2: Category entries (20-99)
├─ Medium images (300x200)
├─ Condensed quick facts
├─ Shorter description
└─ Visual weight: 80%

TIER 3: Extended entries (100+)
├─ Small images or thumbnails
├─ Minimal facts (expandable)
├─ Brief description
├─ "Read more" link to individual page
└─ Visual weight: 60%
```

---

## How-To / Tutorial Page

### Centerpiece Structure

```
[ABOVE FOLD]
  H1: "How to [Action] [Object]"
  Time estimate: "15 min read | 5 steps"
  Difficulty: "Beginner"
  Quick summary: What you'll learn

[MAIN CONTENT - CENTERPIECE]
  [OVERVIEW]
  What + Why + Prerequisites
  
  [STEP-BY-STEP - Highest weight]
  H2: Step 1: [Action]
  - Instructions
  - Image/video
  - Tips/warnings
  
  H2: Step 2: [Action]
  ...
  
  [RESULT]
  What success looks like
  Troubleshooting

[SUPPORTING]
  Related tutorials
  FAQ
  Comments

[SIDEBAR]
  Progress tracker
  Jump to step
  Materials list
```

### Visual Weight - Tutorial

| Element | Weight | Reasoning |
|---------|--------|-----------|
| H1 + Overview | 100% | Centerpiece identifier |
| Step numbers | 100% | Clear progression |
| Step images | 80% | Visual learning |
| Instructions | 100% | Core content |
| Tips/warnings | 60% | Supporting |
| Related tutorials | 30% | Secondary navigation |

### HTML Structure

```html
<!-- ⚠️ HowTo rich result retire 09/2023 — markup minh họa cấu trúc, không phải lever (2026-07-13) -->
<article itemscope itemtype="https://schema.org/HowTo">
  <header>
    <h1 itemprop="name">How to Train a Puppy to Sit</h1>
    
    <div class="meta">
      <span itemprop="totalTime">PT15M</span> 15 minutes
      <span class="difficulty">Beginner</span>
      <span itemprop="tool">Treats, Clicker (optional)</span>
    </div>
    
    <p itemprop="description">Learn to teach your puppy the "sit" command 
    using positive reinforcement in 5 simple steps.</p>
  </header>
  
  <section class="steps">
    <div class="step" itemprop="step" itemscope itemtype="https://schema.org/HowToStep">
      <h2>
        <span class="step-number">1</span>
        <span itemprop="name">Get Your Puppy's Attention</span>
      </h2>
      
      <div itemprop="text">
        <p>Hold a treat close to your puppy's nose...</p>
      </div>
      
      <figure itemprop="image">
        <img src="step1.jpg" alt="Hand holding treat near puppy's nose">
        <figcaption>Position the treat at nose level</figcaption>
      </figure>
      
      <div class="tip">
        <strong>Tip:</strong> Use small, soft treats for quick consumption.
      </div>
    </div>
    
    <!-- More steps -->
  </section>
  
  <section class="result">
    <h2>Expected Result</h2>
    <p>After 5-10 repetitions, your puppy should begin sitting on command...</p>
  </section>
</article>
```

---

## Glossary / Definition Page

### Centerpiece Structure

```
[ABOVE FOLD]
  H1: "[Term]: Definition and Meaning"
  Quick definition (1-2 sentences)
  Pronunciation (if applicable)

[MAIN CONTENT - CENTERPIECE]
  [DEFINITION - Highest weight]
  Full definition with context
  
  [EXPLANATION]
  How it works / Why it matters
  
  [EXAMPLES]
  3+ concrete examples
  
  [RELATED TERMS]
  Connected concepts

[SUPPORTING]
  Usage in sentences
  History/etymology
  FAQ

[SIDEBAR]
  Related definitions
  Alphabet navigation
```

### HTML Structure

```html
<article itemscope itemtype="https://schema.org/DefinedTerm">
  <header>
    <h1>
      <span itemprop="name">Topical Authority</span>: 
      Definition and SEO Meaning
    </h1>
    
    <p class="quick-definition" itemprop="description">
      <strong>Topical Authority</strong> is a website's demonstrated expertise 
      and comprehensive coverage of a specific subject area, measured by 
      search engines through content depth, quality, and semantic relationships.
    </p>
  </header>
  
  <section class="full-definition">
    <h2>What is Topical Authority?</h2>
    <p itemprop="termDescription">Full explanation...</p>
  </section>
  
  <section class="examples">
    <h2>Examples of Topical Authority</h2>
    <ol>
      <li>Example 1...</li>
      <li>Example 2...</li>
      <li>Example 3...</li>
    </ol>
  </section>
  
  <section class="related-terms">
    <h2>Related Terms</h2>
    <ul>
      <li><a href="/glossary/semantic-seo/">Semantic SEO</a></li>
      <li><a href="/glossary/e-e-a-t/">E-E-A-T</a></li>
    </ul>
  </section>
</article>
```

---

## Informational Page Visual Semantic Checklist

### Encyclopedia / A-Z Pages
- [ ] H1 = exact topic (e.g., "Animals That Start With A")
- [ ] Quick stats visible above fold
- [ ] Featured/Most Popular section = highest prominence
- [ ] Individual entries have uniform structure
- [ ] Images consistent size within tiers
- [ ] Quick facts tables for structured data
- [ ] Category sections clearly separated
- [ ] Alphabet/category navigation prominent
- [ ] Search/filter functional

### How-To Pages
- [ ] H1 = "How to [Action] [Object]"
- [ ] Time/difficulty visible above fold
- [ ] Steps numbered prominently
- [ ] Each step has image/visual
- [ ] Progress trackable
- [ ] Result section shows success

### Glossary Pages
- [ ] H1 = "[Term]: Definition"
- [ ] Quick definition above fold
- [ ] Full explanation follows
- [ ] 3+ examples provided
- [ ] Related terms linked
- [ ] Alphabet navigation available

---

## Schema.org for Informational Pages

### A-Z List Schema
```json
{
  "@type": "Article",
  "headline": "Animals That Start With A",
  "author": {"@type": "Person", "name": "Lucia Nguyen"},
  "mainEntity": {
    "@type": "ItemList",
    "numberOfItems": 200,
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "item": {
          "@type": "Thing",
          "name": "Alpaca",
          "alternateName": "Vicugna pacos"
        }
      }
    ]
  }
}
```

### HowTo Schema

> ⚠️ **Deprecated làm lever (2026-07-13):** HowTo rich result retire 09/2023 — markup này không còn tạo rich result và không có evidence giúp AI parsing. Giữ example chỉ làm tư liệu cấu trúc; ưu tiên step content hiển thị rõ trên trang.
```json
{
  "@type": "HowTo",
  "name": "How to Train a Puppy to Sit",
  "totalTime": "PT15M",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Get Your Puppy's Attention",
      "text": "Instructions...",
      "image": "step1.jpg"
    }
  ]
}
```

### DefinedTerm Schema
```json
{
  "@type": "DefinedTerm",
  "name": "Topical Authority",
  "description": "A website's demonstrated expertise...",
  "inDefinedTermSet": {
    "@type": "DefinedTermSet",
    "name": "SEO Glossary"
  }
}
```
