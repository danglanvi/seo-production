# Semantic HTML Elements - Hướng Dẫn Chi Tiết

> 🔴 **Re-label 2026-07-13 (P0 remediation, LINT-2026-008):** Mọi % weight trong file này = **thang ưu tiên biên tập nội bộ GTV** (`practitioner_framework`), KHÔNG phải trọng số Google/LLM công bố. Các claim "AI extracts/ignores/prefers element X" = `hypothesis` trừ khi có citation cụ thể. Giá trị chắc chắn của semantic HTML: accessibility, parsing robustness, logical landmarks, maintainability. Google official: không có yêu cầu HTML/markup đặc biệt cho AI features (ai-optimization-guide).


## 1. `<header>` - Header Element

### Khi Nào Dùng
- Logo & site name ở đầu trang
- Main navigation menu
- Hero section/banner

### Code Examples

**❌ SAI:**
```html
<div class="header">
  <div class="logo">SEO VN</div>
  <div class="nav">
    <a href="/">Home</a>
  </div>
</div>
```

**✅ ĐÚNG:**
```html
<header>
  <a href="/" class="logo">SEO VN</a>
  <nav aria-label="Primary navigation">
    <a href="/">Trang Chủ</a>
    <a href="/services">Dịch Vụ</a>
    <a href="/blog">Blog</a>
  </nav>
</header>
```

### Google/AI Impact
- Weight: **5-10%** (boilerplate - deweighted)
- Google hiểu: "Đây là site header, không phải content chính"
- AI: "Navigation structure exists"

---

## 2. `<nav>` - Navigation Element

### Khi Nào Dùng
- **Primary navigation** (main menu)
- Breadcrumb navigation
- Footer navigation
- **KHÔNG dùng cho:** Mọi group of links

### Code Examples

**❌ SAI:**
```html
<nav>
  <a href="/product1">Product 1</a>
  <a href="/product2">Product 2</a>
  <!-- Quá nhiều links trong nav → confuse -->
</nav>
```

**✅ ĐÚNG:**
```html
<!-- Primary navigation -->
<nav aria-label="Primary navigation">
  <a href="/">Home</a>
  <a href="/services">Services</a>
  <a href="/blog">Blog</a>
  <a href="/contact">Contact</a>
</nav>

<!-- Breadcrumb (secondary nav) -->
<nav aria-label="Breadcrumb">
  <a href="/">Home</a> › 
  <a href="/services">Services</a> › 
  <span>SEO</span>
</nav>
```

### Google/AI Impact
- Weight: **5-10%** (site structure)
- Multiple navs? Dùng `aria-label` để phân biệt
- AI understands site hierarchy

---

## 3. `<main>` - Main Content Container

### Khi Nào Dùng
- **Chỉ 1 `<main>` per page** (CRITICAL!)
- Wrap tất cả primary content
- Không nest `<main>` trong extra `<div>`

### Code Examples

**❌ SAI:**
```html
<body>
  <header>...</header>
  <div class="main-wrapper">
    <div class="content">
      <h1>Title</h1>
      <p>Content...</p>
    </div>
  </div>
  <footer>...</footer>
</body>
```

**✅ ĐÚNG:**
```html
<body>
  <header>...</header>
  
  <main>
    <article>
      <h1>Title</h1>
      <p>Content...</p>
    </article>
  </main>
  
  <footer>...</footer>
</body>
```

### Google/AI Impact
- Weight: **100%** (Google focuses analysis here)
- **Only ONE per page** (multiple confuses algorithms)
- AI uses `<main>` to extract primary text for citations

---

## 4. `<article>` - Article Element

### Khi Nào Dùng
- Blog post, news article
- **Service description** (standalone)
- **Case study** (can be removed & still make sense)
- Product card
- Comment, forum post
- Anything **self-contained & reusable**

### Test: "Can I republish this content independently?"
- Yes → `<article>`
- No → `<section>`

### Code Examples

**❌ SAI:**
```html
<div class="service">
  <h2>SEO Service</h2>
  <p>Description...</p>
</div>
```

**✅ ĐÚNG:**
```html
<article class="service" itemscope itemtype="https://schema.org/Service">
  <h2 itemprop="name">SEO Service</h2>
  <p itemprop="description">Description...</p>
  <span itemprop="areaServed">Vietnam</span>
</article>
```

### Google/AI Impact
- Weight: **80-100%**
- **AI extracts `<article>` blocks** for summaries/citations
- Pairs naturally with Schema.org markup
- Can be nested inside `<section>`

---

## 5. `<section>` - Section Element

### Khi Nào Dùng
- **Thematic grouping** của content liên quan
- Services section (groups multiple services)
- Process section (groups steps)
- Testimonials section
- **Cần context** từ surrounding content

### Test: "Does this content make sense on its own?"
- Yes → `<article>`
- No (needs context) → `<section>`

### Code Examples

**❌ SAI:**
```html
<div class="services">
  <h2>Our Services</h2>
  <div class="service">SEO</div>
  <div class="service">PPC</div>
</div>
```

**✅ ĐÚNG:**
```html
<section id="services">
  <h2>Our Services</h2>
  <article class="service">
    <h3>SEO</h3>
    <p>...</p>
  </article>
  <article class="service">
    <h3>PPC</h3>
    <p>...</p>
  </article>
</section>
```

### Google/AI Impact
- Weight: **60-100%** (depends on nesting)
- Helps AI understand topic clustering
- Groups related `<article>` elements

---

## 6. `<aside>` - Aside Element

### Khi Nào Dùng
- Sidebar content
- Related links/posts
- "Fun fact" boxes
- Supplementary information
- Content that **can be removed** without affecting main content

### Code Examples

**❌ SAI:**
```html
<div class="sidebar">
  <h2>Related Posts</h2>
  <a href="/post1">Post 1</a>
</div>
```

**✅ ĐÚNG:**
```html
<aside>
  <h2>Related Resources</h2>
  <ul>
    <li><a href="/blog/seo-guide">SEO Guide</a></li>
    <li><a href="/blog/keyword-research">Keyword Research</a></li>
  </ul>
</aside>
```

### Google/AI Impact
- Weight: **20-40%** (deweighted - not primary)
- Google understands: "This is supplementary"
- AI ignores `<aside>` when extracting main answers

---

## 7. `<footer>` - Footer Element

### Khi Nào Dùng
- Site footer (copyright, contact)
- Article footer (author, date, tags)
- Section footer

### Code Examples

**Site footer:**
```html
<footer>
  <p>&copy; 2025 SEO VN. All rights reserved.</p>
  <nav aria-label="Footer navigation">
    <a href="/privacy">Privacy</a>
    <a href="/terms">Terms</a>
  </nav>
</footer>
```

**Article footer:**
```html
<article>
  <header>
    <h1>SEO Guide</h1>
  </header>
  <p>Content...</p>
  <footer>
    <p>By: <span class="author">John Doe</span></p>
    <p>Published: <time datetime="2025-12-14">14/12/2025</time></p>
  </footer>
</article>
```

### Google/AI Impact
- Weight: **5-10%** (boilerplate)
- Google knows: "This is standard footer info"
- AI uses article footer for metadata (author, date)

---

## 8. `<time>` - Time Element

### Khi Nào Dùng
- Publication date
- Last updated date
- Event dates

### Code Examples

**❌ SAI:**
```html
<p>Published on: December 14, 2025</p>
```

**✅ ĐÚNG:**
```html
<p>Published: <time datetime="2025-12-14">December 14, 2025</time></p>

<!-- With time -->
<p>Updated: <time datetime="2025-12-14T18:30:00Z">14/12/2025 18:30 UTC</time></p>

<!-- Duration -->
<p>Reading time: <time datetime="PT5M">5 minutes</time></p>
```

### Google/AI Impact
- Enables **rich snippets** (date in search results)
- Voice search understands dates
- Google knows content freshness
- AI extracts publication date accurately

---

## 9. `<figure>` & `<figcaption>` - Media with Caption

### Khi Nào Dùng
- Image + description/caption
- Diagram + explanation
- Chart + label
- Video + transcript summary

### Code Examples

**❌ SAI:**
```html
<img src="process.png" alt="Our process">
<p>Step 1: Audit and analysis...</p>
```

**✅ ĐÚNG:**
```html
<figure>
  <img src="process.png" alt="Our 5-step SEO process diagram">
  <figcaption>
    Our SEO process includes: Audit, Strategy, Implementation, Monitoring, and Optimization.
  </figcaption>
</figure>
```

### Google/AI Impact
- Weight: **60-80%**
- **Pairs image with semantic meaning**
- AI understands image context
- Improves image search indexing
- Can be extracted as a unit by LLMs

---

## 10. `<strong>` & `<em>` - Semantic Emphasis

### Sự Khác Biệt

| Element | Meaning | Visual | Use Case |
|---------|---------|--------|----------|
| `<strong>` | Importance/seriousness | Bold | Key facts, warnings |
| `<em>` | Emphasis/stress | Italic | Tone, pronunciation |
| `<b>` | Visual bold only | Bold | No semantic meaning |
| `<i>` | Visual italic only | Italic | No semantic meaning |

### Code Examples

**❌ SAI (old HTML4 style):**
```html
<p>Our company has <b>10 years</b> of experience.</p>
<p>We <i>truly believe</i> in quality.</p>
```

**✅ ĐÚNG (HTML5 semantic):**
```html
<p>Our company has <strong>10+ years</strong> of experience in SEO.</p>
<p>We <em>truly believe</em> in semantic SEO.</p>
```

### Google/AI Impact
- Weight: **60-80%**
- Google & LLMs understand semantic importance
- AI uses `<strong>` to identify key points
- Better for accessibility (screen readers)
- `<strong>` terms get slightly boosted in context understanding

---

## Summary: When to Use What

| If you need... | Use... |
|----------------|--------|
| Site header | `<header>` |
| Main navigation | `<nav>` |
| Primary content wrapper | `<main>` (only 1!) |
| Self-contained content | `<article>` |
| Thematic grouping | `<section>` |
| Sidebar/supplementary | `<aside>` |
| Footer info | `<footer>` |
| Dates | `<time>` |
| Image + caption | `<figure>` + `<figcaption>` |
| Important text | `<strong>` |
| Emphasized text | `<em>` |
