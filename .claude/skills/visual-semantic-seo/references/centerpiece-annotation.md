# Centerpiece Annotation - Implementation Guide

## What is Centerpiece Annotation?

Centerpiece annotation is Google's method of **identifying and weighting the main content** on a webpage. Google doesn't process all content equally—it uses visual and structural signals to determine what's most important.

## Google's 4-Step Process

### Step 1: DOM Tree Analysis
```
Google examines HTML structure:
- Which elements are largest? (font-size, padding)
- Which elements are positioned first? (DOM order)
- What's the nesting depth? (hierarchy)
```

### Step 2: Layout Tree Evaluation
```
Google evaluates visual rendering:
- Position: Top of page? Above fold?
- Size: How much screen space?
- Prominence: Color contrast? Borders?
- Visual weight: Bold? Large font?
```

### Step 3: NLP Processing
```
Google reads text content:
- Topic identification from headings
- Entity extraction from paragraphs
- Intent matching from keywords
```

### Step 4: Content Weighting
```
Final classification:
- CENTERPIECE: Main topic → 100% weight
- SUPPORTING: Related info → 60-80% weight
- BOILERPLATE: Navigation, footer → 5-10% weight
- SIDEBAR: Aside content → 20-40% weight
```

## Implementation for Service Pages

### Above the Fold (Centerpiece Signal)

```html
<header class="site-header">
  <!-- Minimal: 5-10% weight -->
  <nav>...</nav>
</header>

<main>
  <section class="hero">
    <!-- CENTERPIECE SIGNALS: -->
    <h1>Dịch Vụ SEO Chuyên Nghiệp</h1>  <!-- Large, prominent -->
    <p class="subtitle">Tăng traffic 200-300%</p>  <!-- Supporting text -->
    <button class="cta-primary">Yêu Cầu Tư Vấn</button>  <!-- Action -->
  </section>
```

### Main Content Structure

```html
  <!-- CENTERPIECE: 100% weight -->
  <section id="value" class="main-centerpiece">
    <h2>SEO Mang Lại Gì Cho Doanh Nghiệp?</h2>
    <p>Content explaining value...</p>
    
    <h3>Tăng Organic Traffic</h3>
    <p>Details...</p>
    
    <h3>Cải Thiện Brand Authority</h3>
    <p>Details...</p>
  </section>
  
  <section id="services" class="main-centerpiece">
    <h2>Dịch Vụ Chúng Tôi Cung Cấp</h2>
    <article class="service">
      <h3>Semantic SEO Audit</h3>
      <p>Details...</p>
    </article>
  </section>
  
  <!-- SUPPORTING: 60-80% weight -->
  <section id="process" class="supporting">
    <h2>Quy Trình Làm Việc</h2>
    ...
  </section>
  
  <section id="case-studies" class="supporting">
    <h2>Khách Hàng Thành Công</h2>
    ...
  </section>
</main>

<!-- SIDEBAR: 20-40% weight -->
<aside>
  <h2>Resources</h2>
  ...
</aside>

<!-- BOILERPLATE: 5-10% weight -->
<footer>...</footer>
```

## Visual Weight Signals

### Typography Weight
| Element | Font Size | Weight | Google Signal |
|---------|-----------|--------|---------------|
| H1 | 36-48px | Bold | CENTERPIECE title |
| H2 | 28-32px | Semi-bold | Main sections |
| H3 | 22-24px | Normal | Sub-sections |
| Body | 16px | Normal | Content |

### Position Weight
| Position | Weight Signal | Example |
|----------|---------------|---------|
| Above fold | Highest | H1, CTA, intro |
| First 25% | High | Main sections |
| Middle 50% | Medium | Supporting |
| Bottom 25% | Low | FAQ, footer |

### Space Weight
| Space Usage | Signal |
|-------------|--------|
| >50% page | Centerpiece |
| 20-30% page | Supporting |
| <10% page | Boilerplate |

## Common Mistakes

### ❌ Mistake 1: Banner Larger Than Content
```
[HUGE IMAGE BANNER - 70% of viewport]
[Small content below fold]

→ Google thinks: Centerpiece = Image (meaningless)
```

### ❌ Mistake 2: Sidebar More Prominent
```
[Main content (60%)]  |  [SIDEBAR (40%) with big cards]

→ Google confused about centerpiece
```

### ❌ Mistake 3: H1 Hidden/Small
```
<p class="label">Services</p>
<h1 style="font-size: 14px">Our SEO Services</h1>

→ H1 not recognized as centerpiece
```

### ✅ Correct: Clear Hierarchy
```
<h1 style="font-size: 48px; font-weight: bold">
  Dịch Vụ SEO Chuyên Nghiệp
</h1>
[Main content prominent, above fold]
[Supporting below]
[Sidebar minimal]
```

## Measurement & Validation

### Check Centerpiece Clarity
1. Screenshot page at 1440px width
2. Blur screenshot at 50% intensity
3. Can you identify main topic from blur?
4. YES = Good centerpiece signals
5. NO = Improve visual hierarchy

### Check Content Weight
1. Calculate % of viewport for each section
2. Main topic should be >50%
3. Supporting should be 20-30%
4. Boilerplate <10%

### Check Above Fold
1. Load page (desktop + mobile)
2. What's visible without scrolling?
3. Must include: H1, intro, CTA
4. Must NOT: Only images, only navigation

## Koray's $205K Case Study Principles

From the legal services homepage case:

1. **Single page, multiple intents** - Visual structure supported semantic clustering
2. **Balanced content formats** - Factual + Opinionated + Structured + Prose
3. **Clear centerpiece** - Main offer visually dominant
4. **Supporting context** - Related content below
5. **Function validation** - CTAs working, forms functional

Result: $205,000 organic traffic value from ONE homepage.
