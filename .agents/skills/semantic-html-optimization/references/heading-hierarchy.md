# Heading Hierarchy Guide - H1, H2, H3 Structure for SEO & AI

> 🔴 **Re-label 2026-07-13 (P0 remediation, LINT-2026-008):** Mọi % weight trong file này = **thang ưu tiên biên tập nội bộ GTV** (`practitioner_framework`), KHÔNG phải trọng số Google/LLM công bố. Các claim "AI extracts/ignores/prefers element X" = `hypothesis` trừ khi có citation cụ thể. Giá trị chắc chắn của semantic HTML: accessibility, parsing robustness, logical landmarks, maintainability. Google official: không có yêu cầu HTML/markup đặc biệt cho AI features (ai-optimization-guide).


## Core Principle

Heading hierarchy là yếu tố quan trọng NHẤT cho SEO và AI discoverability. 90% ChatGPT citations đến từ các trang có heading structure rõ ràng.

## The Rules

### Rule 1: Only ONE H1 Per Page

```html
✅ ĐÚNG:
<h1>Dịch Vụ SEO Chuyên Nghiệp</h1>
<h2>Lợi Ích</h2>
<h2>Dịch Vụ</h2>

❌ SAI:
<h1>SEO</h1>
<p>Content...</p>
<h1>Dịch Vụ</h1>  <!-- Multiple H1! -->
<p>More content...</p>
```

**Why:** H1 = Page topic. Multiple H1s confuse Google about main topic.

### Rule 2: Never Skip Heading Levels

```html
✅ ĐÚNG:
<h1>Dịch Vụ SEO</h1>
  <h2>Lợi Ích</h2>
    <h3>Tăng Traffic</h3>
    <h3>Brand Authority</h3>
  <h2>Dịch Vụ</h2>
    <h3>SEO Audit</h3>
    <h3>Link Building</h3>

❌ SAI (Skipping):
<h1>Dịch Vụ SEO</h1>
  <h3>Tăng Traffic</h3>  <!-- H2 bị skip! -->
  <h2>Dịch Vụ</h2>
  <h4>Details</h4>  <!-- H3 bị skip! -->
```

**Why:** Skipping levels breaks hierarchy logic. Google/AI can't understand relationship.

### Rule 3: Each H2/H3 Must Have Content Below

```html
✅ ĐÚNG:
<h2>Dịch Vụ SEO Audit</h2>
<p>Chúng tôi cung cấp dịch vụ audit toàn diện...</p>
<h3>Quy Trình Audit</h3>
<p>Quy trình gồm 5 bước...</p>

❌ SAI (Empty heading):
<h2>Dịch Vụ SEO Audit</h2>
<h3>Quy Trình</h3>  <!-- No content under H2! -->
<p>Details...</p>
```

**Why:** Empty headings = confusing structure.

## Weight Distribution

| Level | Weight | Role | Count per Page |
|-------|--------|------|----------------|
| H1 | **100%** | Page title | Exactly 1 |
| H2 | **80-100%** | Main sections | 3-7 |
| H3 | **60-80%** | Sub-sections | 2-4 per H2 |
| H4 | **40-60%** | Details | Optional, minimal |
| H5-H6 | **20-40%** | Rare | Avoid if possible |

## Standard Heading Structure

### Service Page

```
H1: Dịch Vụ SEO Chuyên Nghiệp - Tăng Traffic 200-300%
│
├── H2: Tại Sao Cần SEO? (Benefits/Value - Centerpiece)
│   ├── H3: Tăng Organic Traffic
│   ├── H3: Cải Thiện Brand Authority
│   └── H3: ROI Lâu Dài
│
├── H2: Dịch Vụ Chúng Tôi Cung Cấp (Services - Centerpiece)
│   ├── H3: 1. Semantic SEO Audit
│   ├── H3: 2. On-Page Optimization
│   ├── H3: 3. Link Building
│   └── H3: 4. Technical SEO
│
├── H2: Quy Trình Làm Việc (Process - Supporting)
│   ├── H3: Bước 1: Audit & Analysis
│   ├── H3: Bước 2: Strategy Development
│   ├── H3: Bước 3: Implementation
│   └── H3: Bước 4: Monitoring
│
├── H2: Khách Hàng Thành Công (Case Studies - Supporting)
│   ├── H3: Case Study 1: E-Commerce
│   └── H3: Case Study 2: SaaS
│
├── H2: Câu Hỏi Thường Gặp (FAQ - Supporting)
│   ├── H3: SEO mất bao lâu?
│   └── H3: Chi phí bao nhiêu?
│
└── H2: Liên Hệ Tư Vấn (CTA - Final)
```

### Blog Post

```
H1: Hướng Dẫn SEO 2025: 10 Chiến Lược Hiệu Quả
│
├── H2: Giới Thiệu
│
├── H2: 1. Semantic SEO
│   ├── H3: Semantic SEO là gì?
│   └── H3: Cách triển khai
│
├── H2: 2. Topical Authority
│   ├── H3: Tại sao quan trọng?
│   └── H3: Xây dựng như thế nào?
│
├── H2: 3. Technical SEO
│   ├── H3: Core Web Vitals
│   └── H3: Mobile-First
│
... (strategies 4-10)
│
├── H2: Kết Luận
│
└── H2: FAQ
    ├── H3: Question 1
    └── H3: Question 2
```

### E-Commerce Product Page

```
H1: [Product Name] - [Key Benefit]
│
├── H2: Mô Tả Sản Phẩm
│
├── H2: Tính Năng Nổi Bật
│   ├── H3: Tính năng 1
│   ├── H3: Tính năng 2
│   └── H3: Tính năng 3
│
├── H2: Thông Số Kỹ Thuật
│
├── H2: Đánh Giá Khách Hàng
│   ├── H3: Review 1
│   └── H3: Review 2
│
├── H2: Câu Hỏi Thường Gặp
│
└── H2: Sản Phẩm Liên Quan
```

## Common Mistakes

### ❌ Mistake 1: Using Headings for Styling

```html
❌ SAI:
<h3>Small notice text</h3>  <!-- Using H3 for small text -->
<h2>Large decorative text</h2>  <!-- Using H2 for design -->

✅ ĐÚNG:
<p class="notice">Small notice text</p>
<p class="large-text">Large decorative text</p>
```

**Fix:** Use CSS for styling, not heading levels.

### ❌ Mistake 2: Multiple H1s (with CSS)

```html
❌ SAI:
<h1 class="hero-title">Welcome</h1>
<h1 class="page-title">Services</h1>

✅ ĐÚNG:
<div class="hero-title">Welcome</div>
<h1 class="page-title">Services</h1>
```

### ❌ Mistake 3: Breaking Hierarchy Mid-Page

```html
❌ SAI:
<h1>Services</h1>
<h2>SEO</h2>
<h3>Benefits</h3>
<h2>PPC</h2>
<h4>Details</h4>  <!-- Should be H3! -->
<h1>About Us</h1>  <!-- Second H1! -->

✅ ĐÚNG:
<h1>Services</h1>
<h2>SEO</h2>
<h3>Benefits</h3>
<h2>PPC</h2>
<h3>Details</h3>
<!-- About Us should be separate page or H2 -->
```

### ❌ Mistake 4: Too Many H2s Without Content

```html
❌ SAI:
<h2>Section 1</h2>
<h2>Section 2</h2>  <!-- No content between! -->
<h2>Section 3</h2>
<p>Content here...</p>

✅ ĐÚNG:
<h2>Section 1</h2>
<p>Content for section 1...</p>
<h2>Section 2</h2>
<p>Content for section 2...</p>
```

## HTML Implementation

### Full Example

```html
<main>
  <article>
    <header>
      <h1>Dịch Vụ SEO Chuyên Nghiệp - Tăng Traffic 200-300%</h1>
      <p class="subtitle">Giải pháp toàn diện cho doanh nghiệp</p>
    </header>
    
    <!-- Centerpiece Section 1 -->
    <section id="benefits">
      <h2>Tại Sao Doanh Nghiệp Cần SEO?</h2>
      <p>SEO mang lại nhiều lợi ích...</p>
      
      <section>
        <h3>Tăng Organic Traffic</h3>
        <p>+200-300% traffic trong 6 tháng...</p>
      </section>
      
      <section>
        <h3>Cải Thiện Brand Authority</h3>
        <p>Google trust = Customer trust...</p>
      </section>
      
      <section>
        <h3>ROI Lâu Dài</h3>
        <p>Chi phí thấp hơn Ads...</p>
      </section>
    </section>
    
    <!-- Centerpiece Section 2 -->
    <section id="services">
      <h2>Dịch Vụ SEO Chúng Tôi Cung Cấp</h2>
      <p>Các dịch vụ chính:</p>
      
      <article class="service">
        <h3>1. Semantic SEO Audit</h3>
        <p>Phân tích toàn diện...</p>
      </article>
      
      <article class="service">
        <h3>2. On-Page Optimization</h3>
        <p>Tối ưu nội dung...</p>
      </article>
      
      <article class="service">
        <h3>3. Link Building</h3>
        <p>Xây dựng backlinks...</p>
      </article>
    </section>
    
    <!-- Supporting Section -->
    <section id="process">
      <h2>Quy Trình Làm Việc</h2>
      <p>Quy trình 5 bước:</p>
      
      <section>
        <h3>Bước 1: Audit</h3>
        <p>Phân tích hiện trạng...</p>
      </section>
      
      <section>
        <h3>Bước 2: Strategy</h3>
        <p>Xây dựng chiến lược...</p>
      </section>
    </section>
    
    <!-- Supporting Section -->
    <section id="case-studies">
      <h2>Khách Hàng Thành Công</h2>
      
      <article class="case-study">
        <h3>Case Study: E-Commerce</h3>
        <p>+200% traffic, +150% revenue...</p>
      </article>
    </section>
  </article>
</main>
```

## Google/AI Understanding

When Google/AI reads the above structure:

```
Page Topic: "Dịch Vụ SEO Chuyên Nghiệp" (H1)
├── Sub-topic: "Tại Sao Cần SEO?" (H2)
│   ├── Detail: "Tăng Traffic" (H3)
│   ├── Detail: "Brand Authority" (H3)
│   └── Detail: "ROI" (H3)
├── Sub-topic: "Dịch Vụ" (H2)
│   ├── Detail: "SEO Audit" (H3)
│   ├── Detail: "On-Page" (H3)
│   └── Detail: "Link Building" (H3)
├── Sub-topic: "Quy Trình" (H2)
│   └── Details... (H3)
└── Sub-topic: "Case Studies" (H2)
    └── Details... (H3)
```

**Result:** Clear outline → Google understands → Better ranking + AI citations

## Checklist

- [ ] Only 1 H1 per page
- [ ] H1 contains primary keyword
- [ ] H2s represent main sections (3-7 per page)
- [ ] H3s are sub-topics of H2s (2-4 per H2)
- [ ] No skipping levels (H1→H2→H3)
- [ ] Each heading has content below it
- [ ] Headings are descriptive (not generic like "Section 1")
- [ ] Headings follow logical order
- [ ] No headings used purely for styling
