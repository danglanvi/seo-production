# AI/LLM Optimization với Semantic HTML

> 🔴 **Re-label 2026-07-13 (P0 remediation, LINT-2026-008):** Mọi % weight trong file này = **thang ưu tiên biên tập nội bộ GTV** (`practitioner_framework`), KHÔNG phải trọng số Google/LLM công bố. Các claim "AI extracts/ignores/prefers element X" = `hypothesis` trừ khi có citation cụ thể. Giá trị chắc chắn của semantic HTML: accessibility, parsing robustness, logical landmarks, maintainability. Google official: không có yêu cầu HTML/markup đặc biệt cho AI features (ai-optimization-guide).


## Core Insight

> Semantic HTML là **điều kiện cần** để máy cắt passage đúng ranh giới — không phải nguyên nhân được cite. *(Câu "90% of ChatGPT citations come from well-structured pages" từng ở đây không có nguồn — gỡ 29/08/2026.)*

Cái có evidence (nội bộ, nguồn + tháng trong `geo-content-optimization/references/geo-levers-map.md` §5): AI engines cite passage **tự đứng** (chunk cắt rời vẫn đủ entity + context + claim), **câu đầu sau heading = answer**, **heading khớp câu hỏi con** của user, facts kiểm chứng + cite nguồn. HTML giúp 4 việc đó bằng:
1. Clear heading structure (H1 → H2 → H3) — heading tổ tiên đi kèm chunk như metadata (`includeAncestorHeadings`), heading rỗng nghĩa làm mất lợi thế
2. Semantic HTML elements (`<article>`, `<section>`) — ranh giới chunk rõ
3. Clean, extractable content blocks — in-flow, không share-button/inject cắt ngang, DOM order = visual order

🔴 **Structured data (Schema.org) KHÔNG nằm trong danh sách này.** Causal DiD Ahrefs 1.885 trang (05/2026): thêm schema ≈ 0 tác động AI citation. Schema = rich results / entity / rendering → `schema-markup-generator`.

## How AI Systems Read Your Content

### 1. Content Chunking

AI systems chia content thành "chunks" dựa trên HTML structure:

```
Page Content
├── Chunk 1: H1 + intro paragraph
├── Chunk 2: H2 "Benefits" + all H3s under it
├── Chunk 3: H2 "Services" + all H3s under it
├── Chunk 4: H2 "Process" + all H3s under it
└── Chunk 5: H2 "FAQ" + Q&A pairs
```

**Better structure = Better chunks = Better citations**

### 2. Article Extraction

AI đặc biệt chú ý đến `<article>` elements:

```html
<!-- AI extracts this as standalone unit -->
<article>
  <h3>SEO Audit Service</h3>
  <p>Description of SEO audit...</p>
  <ul>
    <li>Technical analysis</li>
    <li>Content audit</li>
    <li>Competitor research</li>
  </ul>
</article>
```

Khi user hỏi "What's included in SEO audit?", AI sẽ:
1. Tìm relevant `<article>` block
2. Extract và cite trực tiếp
3. Link back to your page

### 3. Heading-Based Topic Identification

```html
<h2>Semantic SEO là gì?</h2>
<p>Semantic SEO là phương pháp tối ưu...</p>
```

AI sử dụng H2/H3 như "topic identifiers":
- Query: "What is semantic SEO?"
- AI finds: `<h2>Semantic SEO là gì?</h2>`
- Extracts: Following paragraph
- Cites: Your page

## Optimization Strategies

### Strategy 1: Clear, Descriptive Headings

**❌ Generic headings (AI ignores):**
```html
<h2>Overview</h2>
<h2>Details</h2>
<h2>More Information</h2>
```

**✅ Descriptive headings (AI finds & cites):**
```html
<h2>Semantic SEO: Định Nghĩa và Lợi Ích</h2>
<h2>5 Bước Triển Khai Semantic SEO</h2>
<h2>Case Study: +200% Traffic với Semantic SEO</h2>
```

### Strategy 2: Question-Based H2/H3s

AI models được train để trả lời questions. Use Q&A format:

```html
<h2>Semantic SEO là gì?</h2>
<p>Semantic SEO là phương pháp tối ưu nội dung dựa trên ý nghĩa và ngữ cảnh, 
thay vì chỉ tập trung vào keywords đơn lẻ.</p>

<h3>Tại sao Semantic SEO quan trọng?</h3>
<p>Semantic SEO quan trọng vì Google đã chuyển từ keyword matching 
sang understanding intent...</p>

<h3>Làm thế nào để triển khai Semantic SEO?</h3>
<p>Có 5 bước chính:</p>
<ol>
  <li>Entity mapping</li>
  <li>Topical authority building</li>
  ...
</ol>
```

### Strategy 3: Article Blocks for Services/Products

Mỗi service/product nên là `<article>` riêng:

```html
<section id="services">
  <h2>Dịch Vụ SEO</h2>
  
  <article class="service" itemscope itemtype="https://schema.org/Service">
    <h3 itemprop="name">SEO Audit</h3>
    <p itemprop="description">
      Dịch vụ SEO Audit phân tích toàn diện website của bạn, 
      bao gồm technical issues, content gaps, và competitor analysis.
    </p>
    <ul>
      <li>Phân tích 200+ technical factors</li>
      <li>Content gap analysis</li>
      <li>Competitor benchmarking</li>
    </ul>
    <span itemprop="areaServed">Vietnam</span>
  </article>
  
  <article class="service" itemscope itemtype="https://schema.org/Service">
    <h3 itemprop="name">Link Building</h3>
    <p itemprop="description">
      Xây dựng backlinks chất lượng cao từ các domain có authority...
    </p>
  </article>
</section>
```

### Strategy 4: Time-Stamped Content

AI ưu tiên fresh content. Always use `<time>`:

```html
<article>
  <header>
    <h1>Hướng Dẫn SEO 2025</h1>
    <p>Published: <time datetime="2025-01-15">January 15, 2025</time></p>
    <p>Updated: <time datetime="2025-12-14">December 14, 2025</time></p>
  </header>
  ...
</article>
```

### Strategy 5: Semantic Emphasis for Key Points

Use `<strong>` cho important facts AI should extract:

```html
<p>
  Theo nghiên cứu, <strong>90% traffic từ Google đến từ top 3 kết quả</strong>. 
  Điều này có nghĩa ranking ở vị trí 4-10 chỉ nhận được 
  <strong>khoảng 10% tổng click</strong>.
</p>
```

AI will extract: "90% traffic từ Google đến từ top 3 kết quả"

### Strategy 6: Figure + Caption for Visual Data

```html
<figure>
  <img src="seo-roi-chart.png" alt="SEO ROI comparison chart">
  <figcaption>
    <strong>SEO ROI so với các kênh khác:</strong> 
    SEO mang lại ROI trung bình 748%, cao hơn PPC (200%) 
    và Social Media (150%).
  </figcaption>
</figure>
```

AI can cite the figcaption for data-driven answers.

### Strategy 7: Structured Lists

AI loves structured lists for "how-to" and "what are" queries:

```html
<h3>5 Bước Triển Khai Semantic SEO</h3>
<ol>
  <li><strong>Entity Mapping</strong> - Xác định entities chính</li>
  <li><strong>Topical Authority</strong> - Xây dựng content clusters</li>
  <li><strong>Internal Linking</strong> - Liên kết semantic</li>
  <li><strong>Schema Markup</strong> - Structured data</li>
  <li><strong>Content Optimization</strong> - Optimize cho NLP</li>
</ol>
```

## Complete AI-Optimized Page Template

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Semantic SEO: Hướng Dẫn Toàn Diện 2025 | SEO Expert</title>
  <meta name="description" content="Hướng dẫn chi tiết về Semantic SEO: 
    định nghĩa, lợi ích, và 5 bước triển khai hiệu quả.">
  
  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Semantic SEO: Hướng Dẫn Toàn Diện 2025",
    "datePublished": "2025-01-15",
    "dateModified": "2025-12-14",
    "author": {
      "@type": "Organization",
      "name": "SEO Expert"
    }
  }
  </script>
</head>

<body>
  <header>
    <nav aria-label="Primary">
      <a href="/">Home</a>
      <a href="/blog">Blog</a>
      <a href="/services">Services</a>
    </nav>
  </header>

  <main>
    <article itemscope itemtype="https://schema.org/Article">
      <header>
        <h1 itemprop="headline">Semantic SEO: Hướng Dẫn Toàn Diện 2025</h1>
        <p>
          Published: <time datetime="2025-01-15" itemprop="datePublished">15/01/2025</time>
          | Updated: <time datetime="2025-12-14" itemprop="dateModified">14/12/2025</time>
        </p>
      </header>

      <!-- AI-friendly intro -->
      <section id="intro">
        <p itemprop="description">
          <strong>Semantic SEO</strong> là phương pháp tối ưu nội dung dựa trên 
          ý nghĩa và ngữ cảnh, giúp Google hiểu content của bạn tốt hơn. 
          Bài viết này hướng dẫn chi tiết cách triển khai Semantic SEO 
          để tăng ranking và traffic.
        </p>
      </section>

      <!-- Question-based H2 for AI -->
      <section id="what-is">
        <h2>Semantic SEO là gì?</h2>
        <p>
          Semantic SEO là chiến lược tối ưu content dựa trên 
          <strong>entities</strong>, <strong>topics</strong>, và 
          <strong>contextual relationships</strong>, thay vì chỉ keywords.
        </p>
        
        <h3>Khác biệt với Traditional SEO</h3>
        <p>
          Traditional SEO tập trung vào keyword density và exact match. 
          Semantic SEO tập trung vào <strong>meaning</strong> và 
          <strong>user intent</strong>.
        </p>
      </section>

      <!-- List-based section for AI extraction -->
      <section id="benefits">
        <h2>5 Lợi Ích của Semantic SEO</h2>
        <ol>
          <li><strong>Ranking cho nhiều variations</strong> - Không chỉ exact keywords</li>
          <li><strong>Featured snippets</strong> - Google hiểu content tốt hơn</li>
          <li><strong>Voice search</strong> - Optimized cho natural language</li>
          <li><strong>AI citations</strong> - LLMs prefer semantic content</li>
          <li><strong>Sustainable rankings</strong> - Không bị ảnh hưởng bởi algorithm updates</li>
        </ol>
      </section>

      <!-- How-to section with steps -->
      <section id="how-to">
        <h2>Cách Triển Khai Semantic SEO</h2>
        
        <section>
          <h3>Bước 1: Entity Mapping</h3>
          <p>Xác định entities chính liên quan đến topic...</p>
        </section>
        
        <section>
          <h3>Bước 2: Build Topical Authority</h3>
          <p>Tạo comprehensive content coverage...</p>
        </section>
        
        <section>
          <h3>Bước 3: Internal Linking</h3>
          <p>Liên kết các related topics...</p>
        </section>
      </section>

      <!-- Data with figure -->
      <section id="data">
        <h2>Data: Semantic SEO Hiệu Quả Như Thế Nào?</h2>
        <figure>
          <img src="semantic-seo-results.png" alt="Semantic SEO traffic increase">
          <figcaption>
            <strong>Case study:</strong> Website áp dụng Semantic SEO 
            tăng <strong>200-300% organic traffic</strong> trong 6 tháng.
          </figcaption>
        </figure>
      </section>

      <!-- FAQ section — FAQ content giữ (answer-first 40-60 từ), KHÔNG FAQPage schema:
           FAQ rich result chấm dứt 07/05/2026; schema ≈ 0 tác động AI citation (DiD Ahrefs 05/2026) -->
      <section id="faq">
        <h2>Câu Hỏi Thường Gặp</h2>
        
        <article>
          <h3>Semantic SEO mất bao lâu để có kết quả?</h3>
          <p>
            Thường thấy kết quả sau <strong>3-6 tháng</strong>, 
            phụ thuộc vào độ cạnh tranh và chất lượng implementation.
          </p>
        </article>
        
        <article>
          <h3>Semantic SEO có thay thế technical SEO không?</h3>
          <p>
            Không. Semantic SEO <strong>bổ sung</strong> cho technical SEO, 
            không thay thế. Cả hai đều cần thiết.
          </p>
        </article>
      </section>

      <footer>
        <p>Author: <span itemprop="author">SEO Expert Team</span></p>
      </footer>
    </article>
  </main>

  <footer>
    <p>&copy; 2025 SEO Expert</p>
  </footer>
</body>
</html>
```

## Checklist: AI-Ready Content

### ✅ Structure
- [ ] Clear H1 → H2 → H3 hierarchy
- [ ] Descriptive headings (not generic)
- [ ] Question-based H2/H3s where appropriate
- [ ] `<article>` for self-contained content
- [ ] `<section>` for thematic groups

### ✅ Semantic Elements
- [ ] `<main>` wrapping primary content
- [ ] `<time>` for dates
- [ ] `<figure>` + `<figcaption>` for images/data
- [ ] `<strong>` for key facts
- [ ] `<em>` for emphasis

### 🟡 Structured Data — rich results / entity, KHÔNG tính vào AI-citation
- [ ] Schema.org JSON-LD theo page type (Article, Product, Service, Organization/Person + `sameAs`) → sinh bằng `schema-markup-generator`; làm vì rich results + entity understanding, không vì citation (DiD Ahrefs 1.885 trang 05/2026 ≈ 0)
- [ ] KHÔNG FAQPage schema (rich result chấm dứt 07/05/2026) — FAQ content answer-first trên trang vẫn giữ

### ✅ Content Format
- [ ] Intro paragraph summarizing main points
- [ ] Numbered/bulleted lists for steps/benefits
- [ ] Tables for comparisons
- [ ] Clear, extractable key facts
- [ ] Updated timestamps

## Result

When optimized correctly (`hypothesis` — cơ chế parsing đã verify, tác động citation chưa có số riêng cho HTML):
- **Google:** Better understanding → chunk/passage đúng ranh giới → Featured snippets / AIO passage
- **ChatGPT:** Clear structure → passage tự đứng được lift đúng → điều kiện cần cho citation
- **Claude:** Semantic tags → Context understanding → Accurate answers
- **Perplexity:** Structure + passage tự đứng → Source linking → Traffic *(bỏ "Schema" khỏi chuỗi này 29/08/2026 — schema ≈ 0 tác động citation)*

**HTML sạch chỉ mở cửa; cái được cite là passage bên trong** — kiến trúc passage chấm theo GE-16…GE-27 (`sop/06-self-checklist/tier-1-geo.md`), audit bằng `geo-content-optimization`.
