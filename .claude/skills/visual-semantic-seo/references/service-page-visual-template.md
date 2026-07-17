# Service Page Visual Semantic Template

## Contents

- [Complete HTML Structure](#complete-html-structure)
- [Visual Weight Guide](#visual-weight-guide)
- [CSS Recommendations](#css-recommendations)

## Complete HTML Structure

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dịch Vụ SEO Chuyên Nghiệp | Tăng Traffic 200-300% | Company</title>
  <meta name="description" content="Dịch vụ SEO toàn diện giúp tăng traffic...">
  
  <!-- Schema.org Structured Data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Dịch Vụ SEO Chuyên Nghiệp",
    "description": "Dịch vụ SEO toàn diện...",
    "provider": {
      "@type": "Organization",
      "name": "Company Name"
    },
    "areaServed": "Vietnam",
    "offers": {
      "@type": "Offer",
      "price": "5000000",
      "priceCurrency": "VND"
    }
  }
  </script>
</head>

<body>
  <!-- ============================================
       HEADER - Boilerplate (Weight: 5-10%)
       ============================================ -->
  <header class="site-header">
    <nav aria-label="Primary navigation">
      <a href="/" class="logo">Company</a>
      <ul class="nav-menu">
        <li><a href="/">Trang chủ</a></li>
        <li><a href="/services" aria-current="page">Dịch vụ</a></li>
        <li><a href="/blog">Blog</a></li>
        <li><a href="/contact">Liên hệ</a></li>
      </ul>
    </nav>
  </header>

  <!-- ============================================
       MAIN - Primary Content (Weight: 100%)
       ============================================ -->
  <main>
    <article itemscope itemtype="https://schema.org/Service">
      
      <!-- HERO SECTION - Above the Fold -->
      <header class="hero">
        <h1 itemprop="name">Dịch Vụ SEO Chuyên Nghiệp - Tăng Traffic 200-300%</h1>
        <p class="subtitle" itemprop="description">
          Giải pháp SEO toàn diện dựa trên Semantic SEO & Topical Authority
        </p>
        
        <!-- PRIMARY CTA - Critical for function -->
        <button class="cta-primary" onclick="openConsultationForm()">
          Yêu Cầu Tư Vấn Miễn Phí
        </button>
        
        <!-- SECONDARY CTA -->
        <p class="cta-secondary">
          Hoặc gọi: <a href="tel:+84901234567">+84 901 234 567</a>
        </p>
      </header>

      <!-- ============================================
           CENTERPIECE SECTION 1: VALUE/BENEFITS
           (Weight: 100%, Centerpiece content)
           ============================================ -->
      <section id="benefits" class="centerpiece">
        <h2>SEO & GEO Mang Lại Gì Cho Doanh Nghiệp?</h2>
        
        <section>
          <h3>Tăng Organic Traffic & Revenue</h3>
          <p>
            <strong>+200-300% traffic</strong> trong 6 tháng đầu tiên. 
            Organic traffic = Khách hàng chất lượng cao, không cần trả 
            tiền quảng cáo lâu dài.
          </p>
        </section>
        
        <section>
          <h3>Xây Dựng Brand Authority</h3>
          <p>
            Ranking top Google = Google tin tưởng bạn → Khách hàng tin tưởng. 
            <strong>70% người dùng</strong> chỉ click vào top 3 kết quả.
          </p>
        </section>
        
        <section>
          <h3>ROI Lâu Dài & Cost Efficiency</h3>
          <p>
            Organic cost/click thấp hơn Paid Ads <strong>70%</strong>. 
            Đầu tư một lần, hưởng lợi lâu dài.
          </p>
        </section>
      </section>

      <!-- ============================================
           CENTERPIECE SECTION 2: SERVICES
           (Weight: 100%, Centerpiece content)
           ============================================ -->
      <section id="services" class="centerpiece">
        <h2>Dịch Vụ SEO & GEO Chúng Tôi Cung Cấp</h2>
        
        <article class="service-card" itemscope itemtype="https://schema.org/Service">
          <h3 itemprop="name">1. Semantic SEO Audit & Strategy</h3>
          <p itemprop="description">
            Phân tích toàn diện website theo framework Semantic SEO. 
            Entity mapping, knowledge graph analysis, topical gap identification.
          </p>
        </article>
        
        <article class="service-card" itemscope itemtype="https://schema.org/Service">
          <h3 itemprop="name">2. Topical Authority Building</h3>
          <p itemprop="description">
            Xây dựng Semantic Content Network với Topical Map. 
            Coverage toàn diện để trở thành authority trong ngành.
          </p>
        </article>
        
        <article class="service-card" itemscope itemtype="https://schema.org/Service">
          <h3 itemprop="name">3. Technical SEO & Content Structure</h3>
          <p itemprop="description">
            Visual semantic optimization, heading hierarchy, schema markup. 
            Giảm Cost of Retrieval cho Google.
          </p>
        </article>
        
        <article class="service-card" itemscope itemtype="https://schema.org/Service">
          <h3 itemprop="name">4. Link Building & Authority Scaling</h3>
          <p itemprop="description">
            Semantic-aware link strategy. Contextual backlinks từ 
            relevant sources trong industry.
          </p>
        </article>
      </section>

      <!-- ============================================
           SUPPORTING SECTION 1: PROCESS
           (Weight: 60-80%, Supporting content)
           ============================================ -->
      <section id="process" class="supporting">
        <h2>Quy Trình Làm Việc</h2>
        
        <section>
          <h3>Bước 1: Audit & Analysis</h3>
          <p>
            Phân tích toàn diện hiện trạng website. Technical audit, 
            content gap analysis, competitor analysis.
          </p>
        </section>
        
        <section>
          <h3>Bước 2: Strategy Development</h3>
          <p>
            Xây dựng Topical Map và Semantic Content Network strategy 
            phù hợp với business goals.
          </p>
        </section>
        
        <section>
          <h3>Bước 3: Implementation</h3>
          <p>
            Triển khai content, technical optimization, link building 
            theo timeline và priority.
          </p>
        </section>
        
        <section>
          <h3>Bước 4: Monitoring & Optimization</h3>
          <p>
            Tracking performance, monthly reporting, continuous 
            optimization dựa trên data.
          </p>
        </section>
      </section>

      <!-- ============================================
           SUPPORTING SECTION 2: CASE STUDIES
           (Weight: 60-80%, Supporting content)
           ============================================ -->
      <section id="case-studies" class="supporting">
        <h2>Khách Hàng Thành Công</h2>
        
        <article class="case-study">
          <h3>Case Study 1: E-Commerce Fashion</h3>
          <p>
            <strong>+250% organic traffic</strong> trong 6 tháng. 
            Revenue từ organic tăng gấp 3 lần.
          </p>
        </article>
        
        <article class="case-study">
          <h3>Case Study 2: SaaS B2B</h3>
          <p>
            <strong>Top 3 Google</strong> cho 50+ keywords chính. 
            Lead generation tăng 180%.
          </p>
        </article>
      </section>

      <!-- ============================================
           SUPPORTING SECTION 3: PRICING
           (Weight: 60-80%, Supporting content)
           ============================================ -->
      <section id="pricing" class="supporting">
        <h2>Gói Giá & Đăng Ký</h2>
        
        <div class="pricing-tier">
          <h3>Gói Starter</h3>
          <p class="price">
            <strong>2,000,000 VNĐ/tháng</strong>
          </p>
          <ul>
            <li>SEO Audit cơ bản</li>
            <li>5 bài content/tháng</li>
            <li>Monthly report</li>
          </ul>
          <button class="select-plan" data-plan="starter">
            Chọn Gói Này
          </button>
        </div>
        
        <div class="pricing-tier featured">
          <h3>Gói Professional</h3>
          <p class="price">
            <strong>5,000,000 VNĐ/tháng</strong>
          </p>
          <ul>
            <li>Full Semantic SEO Audit</li>
            <li>15 bài content/tháng</li>
            <li>Link building</li>
            <li>Weekly report</li>
          </ul>
          <button class="select-plan" data-plan="professional">
            Chọn Gói Này
          </button>
        </div>
        
        <div class="pricing-tier">
          <h3>Gói Enterprise</h3>
          <p class="price">
            <strong>Liên hệ</strong>
          </p>
          <ul>
            <li>Custom strategy</li>
            <li>Unlimited content</li>
            <li>Dedicated account manager</li>
          </ul>
          <button class="select-plan" data-plan="enterprise">
            Liên Hệ Tư Vấn
          </button>
        </div>
      </section>

      <!-- ============================================
           CTA FINAL - Conversion push
           ============================================ -->
      <section id="cta-final" class="cta-section">
        <h2>Sẵn Sàng Tăng Traffic?</h2>
        <p>Đăng ký tư vấn miễn phí ngay hôm nay.</p>
        
        <button class="cta-primary" onclick="openConsultationForm()">
          Yêu Cầu Tư Vấn Hôm Nay
        </button>
        
        <button class="cta-chat" onclick="openChat()">
          Chat Với Chúng Tôi
        </button>
      </section>

      <!-- Article Footer -->
      <footer class="article-footer">
        <p>
          Cập nhật: 
          <time datetime="2025-12-14">14/12/2025</time>
        </p>
      </footer>
      
    </article>
  </main>

  <!-- ============================================
       ASIDE - Sidebar (Weight: 20-40%)
       Optional - Keep minimal
       ============================================ -->
  <aside>
    <h2>Tài Liệu Hữu Ích</h2>
    <ul>
      <li><a href="/blog/semantic-seo">Semantic SEO là gì?</a></li>
      <li><a href="/blog/topical-authority">Topical Authority Guide</a></li>
    </ul>
  </aside>

  <!-- ============================================
       FOOTER - Boilerplate (Weight: 5-10%)
       ============================================ -->
  <footer class="site-footer">
    <p>&copy; 2025 Company. All rights reserved.</p>
    <nav>
      <a href="/privacy">Privacy Policy</a>
      <a href="/terms">Terms of Service</a>
    </nav>
  </footer>

  <!-- ============================================
       CONTACT FORM MODAL
       ============================================ -->
  <div id="consultation-modal" class="modal" hidden>
    <form id="consultation-form" method="POST" action="/api/consultation">
      <h2>Yêu Cầu Tư Vấn Miễn Phí</h2>
      
      <label for="name">Họ tên:</label>
      <input type="text" id="name" name="name" required>
      
      <label for="email">Email:</label>
      <input type="email" id="email" name="email" required>
      
      <label for="phone">Điện thoại:</label>
      <input type="tel" id="phone" name="phone" required>
      
      <label for="website">Website:</label>
      <input type="url" id="website" name="website">
      
      <label for="message">Nhu cầu:</label>
      <textarea id="message" name="message" required></textarea>
      
      <button type="submit">Gửi Yêu Cầu</button>
    </form>
  </div>

  <!-- ============================================
       ANALYTICS TRACKING
       ============================================ -->
  <script>
    // Primary CTA tracking
    document.querySelectorAll('.cta-primary').forEach(btn => {
      btn.addEventListener('click', () => {
        gtag('event', 'cta_click', {
          'event_category': 'engagement',
          'event_label': 'primary_cta'
        });
      });
    });
    
    // Form submission tracking
    document.getElementById('consultation-form')?.addEventListener('submit', () => {
      gtag('event', 'form_submit', {
        'event_category': 'conversion',
        'event_label': 'consultation_form'
      });
    });
    
    // Plan selection tracking
    document.querySelectorAll('.select-plan').forEach(btn => {
      btn.addEventListener('click', (e) => {
        gtag('event', 'plan_select', {
          'event_category': 'engagement',
          'event_label': e.target.dataset.plan
        });
      });
    });
  </script>
</body>
</html>
```

## Visual Weight Guide

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (5-10%)                                             │
│  Logo + Navigation                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  HERO - Above the Fold                                │  │
│  │  H1: Dịch Vụ SEO (48px, bold)                        │  │
│  │  Subtitle                                             │  │
│  │  [CTA BUTTON] (prominent)                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  CENTERPIECE 1: Benefits (100%)                       │  │
│  │  H2: SEO Mang Lại Gì? (32px)                         │  │
│  │    H3: Traffic (24px)                                 │  │
│  │    H3: Authority                                      │  │
│  │    H3: ROI                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  CENTERPIECE 2: Services (100%)                       │  │
│  │  H2: Dịch Vụ Cung Cấp                                │  │
│  │    [Service cards with H3]                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SUPPORTING: Process (60-80%)                         │  │
│  │  H2: Quy Trình                                        │  │
│  │    H3: Steps...                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SUPPORTING: Case Studies (60-80%)                    │  │
│  │  SUPPORTING: Pricing (60-80%)                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐  ┌─────────────────────────────────┐  │
│  │  ASIDE (20-40%)  │  │  CTA FINAL                      │  │
│  │  Resources       │  │  [Final conversion push]        │  │
│  └──────────────────┘  └─────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  FOOTER (5-10%)                                             │
│  Copyright, links                                           │
└─────────────────────────────────────────────────────────────┘
```

## CSS Recommendations

```css
/* Heading Hierarchy */
h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
}

h2 {
  font-size: 32px;
  font-weight: 600;
  margin-top: 48px;
  margin-bottom: 24px;
}

h3 {
  font-size: 24px;
  font-weight: 500;
  margin-top: 32px;
  margin-bottom: 16px;
}

/* CTA Prominence */
.cta-primary {
  background-color: #2563eb;
  color: white;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.cta-primary:hover {
  background-color: #1d4ed8;
}

/* Centerpiece sections */
.centerpiece {
  padding: 48px 0;
  border-bottom: 1px solid #e5e7eb;
}

/* Supporting sections */
.supporting {
  padding: 32px 0;
  background-color: #f9fafb;
}

/* Sidebar de-emphasis */
aside {
  font-size: 14px;
  color: #6b7280;
  max-width: 300px;
}

/* Header/Footer minimalism */
.site-header,
.site-footer {
  padding: 16px 0;
  font-size: 14px;
}
```

---

## v3.4 Addendum — Service Page Application Playbook (07/2026)

Template HTML phía trên là khung nền (v1.0). Từ v3.4, khi build service page dùng **khung 14 block** trong SKILL.md mục "Service Page Application Playbook" — dịch từ 3 bộ benchmark (MTM Thu Cũ · Koray live-sites · Amazon PDP). Delta so với template này:

1. **Hero:** thêm rating badge (điểm + số review + logo Google) sát H1 — Trust L1; CTA giữ nguyên.
2. **Sau hero, TRƯỚC Benefits:** chèn (a) definition-first "Dịch vụ X là gì?" trong `<blockquote>` 40-75 từ; (b) **quote-box cô lập** (giá from · response-time promise "báo giá trong 24h" · slot thật · trust ledger 4 dòng); (c) **bảng thông số dịch vụ** E-A-V (deliverables · SLA · timeline · người thực hiện · hình thức); (d) trust strip logo báo chí/khách (Trust L2).
3. **Services section:** mỗi `<article>` service con áp micro-template heading cố định *Phù hợp với ai / Deliverables / Timeline / Giá from / Kết quả đo được* (lặp ≥3 lần).
4. **Thêm mới giữa Process và Case Studies:** use-case tabs theo ngành/tình huống khách (RQ "hợp ai?") + **công cụ sống** (calculator/estimator ≤5 bước, kết quả tạm tính hiện từ bước 2-3, mobile bottom-sheet) — form thu lead không thay được công cụ.
5. **Case studies:** numeric range in đậm + schema **Article** (không dùng type "CaseStudy" — không tồn tại trên schema.org).
6. **Pricing tiers:** thêm capacity thật per gói ("Nhận thêm 2 dự án tháng này") — không countdown ảo.
7. **Testimonials:** nén thành aspect chips kèm tần suất + video có tên thật/role (Trust L3-L5); thêm 1 dòng stats recency "N dự án quý này" (L6); team profiles pre-footer (L7).
8. **Mobile:** anchor chips (Quy trình · Bảng giá · Case study · FAQ · Reviews) + sticky CTA header.

Counter-signals + bảng dịch đầy đủ S1-S14: xem SKILL.md. Trust positions: `trust-stacking-hierarchy.md`. Pricing card: `multi-tier-pricing-pattern.md`. Function evidence: `real-time-function-validators.md`.
