# Website Function & SEO - Semantic Intent Validation

## Core Concept

**Website Function ≠ Visual Semantic**

Nhưng cả hai kết hợp = **Semantic Intent Validation**

| Aspect | Visual Semantic | Website Function |
|--------|-----------------|------------------|
| Definition | Layout, hierarchy, prominence | Interactive elements (buttons, forms) |
| Google Patent | US8949242B1 | US10565267B1, US20150234930A1 |
| Purpose | Identify centerpiece | Validate user intent match |
| Evaluation | Annotation systems | Engagement tracking |

## How Google Tracks Website Functions

### Google Patent US10565267B1 - Quality Score

```python
Quality_Score = function(
    recentness_score,
    affinity_score,
    popularity_score
)

Popularity_Score = function(
    total_interaction_count,
    recent_interaction_count,
    interaction_types  # passive vs active
)
```

### Interaction Types

| Type | Examples | Weight |
|------|----------|--------|
| **Passive** | View, scroll, pause | Low (1x) |
| **Active** | Click button, fill form | High (5x) |
| **Conversion** | Submit, purchase | Highest (10x) |

## Required Website Functions (Service Pages)

### 1. Primary CTA (Above Fold)

```html
<section class="hero">
  <h1>Dịch Vụ SEO Chuyên Nghiệp</h1>
  <p>Tăng traffic 200-300%...</p>
  
  <!-- PRIMARY CTA - REQUIRED -->
  <button class="cta-primary" onclick="requestConsultation()">
    Yêu Cầu Tư Vấn Miễn Phí
  </button>
</section>
```

**Why:**
- Visual semantic: Prominent above fold
- User engagement: Click = active interaction
- Intent match: Page says "services" → User can "request"

### 2. Secondary CTA (Phone/Chat)

```html
<p>
  Hoặc gọi: 
  <a href="tel:+84901234567" class="cta-phone">
    +84 901 234 567
  </a>
</p>

<button class="cta-chat" onclick="openChat()">
  Chat ngay
</button>
```

**Why:**
- Multiple conversion paths
- Mobile users prefer phone
- Immediate assistance option

### 3. Contact Form (Lead Capture)

```html
<form id="contact-form" method="POST" action="/api/contact">
  <label for="email">Email:</label>
  <input type="email" id="email" name="email" required>
  
  <label for="phone">Điện thoại:</label>
  <input type="tel" id="phone" name="phone" required>
  
  <label for="message">Nhu cầu:</label>
  <textarea id="message" name="message" required></textarea>
  
  <button type="submit">Gửi Yêu Cầu</button>
</form>
```

**Google tracks:**
- Form field focus → Interaction
- Form field input → Active interaction
- Form submission → Conversion (highest weight)

### 4. Pricing/Plan Selection

```html
<section class="pricing">
  <h2>Gói Giá</h2>
  
  <div class="pricing-tier">
    <h3>Gói Starter</h3>
    <p><strong>2,000,000 VNĐ/tháng</strong></p>
    <button class="select-plan" data-plan="starter">
      Chọn Gói Này
    </button>
  </div>
  
  <div class="pricing-tier">
    <h3>Gói Professional</h3>
    <p><strong>5,000,000 VNĐ/tháng</strong></p>
    <button class="select-plan" data-plan="professional">
      Chọn Gói Này
    </button>
  </div>
</section>
```

**Google tracks:**
- Which tier gets most clicks
- Pricing page engagement
- Plan selection conversion

### 5. Analytics Tracking

```javascript
// Track CTA clicks
document.querySelectorAll('.cta-primary').forEach(btn => {
  btn.addEventListener('click', () => {
    gtag('event', 'request_consultation', {
      'event_category': 'engagement',
      'event_label': 'primary_cta'
    });
  });
});

// Track form submissions
document.getElementById('contact-form').addEventListener('submit', () => {
  gtag('event', 'form_submission', {
    'event_category': 'conversion',
    'event_label': 'contact_form'
  });
});
```

## Intent Match Scenarios

### ✅ Good: Function Matches Intent

```
Page says: "Dịch Vụ SEO - Yêu Cầu Tư Vấn"
Function exists: Working "Request Consultation" button
User action: Clicks button → Form opens
Result: Intent match ✓ → Quality score boost
```

### ❌ Bad: Function Broken

```
Page says: "Dịch Vụ SEO - Yêu Cầu Tư Vấn"
Function: Button exists but onclick="null" (broken)
User action: Clicks button → Nothing happens → Leave
Result: Intent mismatch ✗ → Quality score drop
```

### ❌ Bad: Function Missing

```
Page says: "Dịch Vụ SEO - Liên Hệ Ngay"
Function: No contact form, no CTA button
User action: Can't take action → Leave
Result: Intent mismatch ✗ → Bounce signal
```

## Google Patent US8868565B1 - Click Duration

Google calibrates expected click duration by content type:

| Page Type | Expected Duration | Signal |
|-----------|-------------------|--------|
| Contact page | Short (15-30s) | Quick action |
| Product page | Long (60-120s) | Research |
| Article | Long (120-300s) | Reading |
| Checkout | Long (60-180s) | Form filling |

### Implications

- If user clicks CTA → stays on form 30s+ → Positive
- If user clicks CTA → leaves immediately → Negative
- Match expected duration for page type

## Google Patent US20150234930A1 - Functional Extensions

Google evaluates landing pages for:

1. **Extension rendered?** - Technical correctness
2. **User click on extension?** - Intent match
3. **Action completed?** - Semantic relevance

### Service Page Functional Extensions

```html
<!-- Functional Extension: Click-to-call -->
<a href="tel:+84901234567" class="click-to-call">
  Gọi ngay: +84 901 234 567
</a>

<!-- Functional Extension: Form -->
<form class="lead-form">
  <!-- Form fields -->
</form>

<!-- Functional Extension: Pricing action -->
<button class="pricing-select">Chọn gói</button>
```

## Combination: Visual + Function

```
Visual Semantic (Layout)
  + Website Function (Interactive)
  = Semantic Relevance (Intent validation)
  = Quality Score
  = Ranking Position
```

### Matrix

| Visual | Function | Result |
|--------|----------|--------|
| ✅ Good layout | ✅ Working buttons | ✅ High ranking |
| ✅ Good layout | ❌ Broken buttons | ❌ Low ranking |
| ❌ Bad layout | ✅ Working buttons | ⚠️ Medium ranking |
| ❌ Bad layout | ❌ Broken buttons | ❌ Very low ranking |

## Implementation Checklist

### Primary Functions
- [ ] Primary CTA button visible above fold
- [ ] CTA is clickable and functional
- [ ] CTA text clear ("Yêu Cầu Tư Vấn" not "Click Here")
- [ ] CTA contrasting color for visibility

### Secondary Functions
- [ ] Phone number as tel: link
- [ ] Chat option available
- [ ] Alternative contact method

### Forms
- [ ] Form renders correctly
- [ ] All fields functional
- [ ] Submit button works
- [ ] Confirmation after submit

### Tracking
- [ ] Analytics tracking installed
- [ ] CTA click events tracked
- [ ] Form submission events tracked
- [ ] Goal/conversion tracking active

### Mobile
- [ ] All functions work on mobile
- [ ] Touch targets adequate size (44px+)
- [ ] Forms mobile-friendly
- [ ] Click-to-call works
