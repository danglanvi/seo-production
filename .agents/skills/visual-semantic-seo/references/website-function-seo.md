# Website Function & SEO - Semantic Intent Validation

## Core Concept

**Website Function ≠ Visual Semantic**

Nhưng cả hai kết hợp = **Semantic Intent Validation**

| Aspect | Visual Semantic | Website Function |
|--------|-----------------|------------------|
| Definition | Layout, hierarchy, prominence | Interactive elements (buttons, forms) |
| Bằng chứng | Martin Splitt (Google) về centerpiece; patent US7421651B2 (tách khối theo khoảng trắng thị giác) | Chưa có patent hay thuộc tính leak trực tiếp; heuristic thực hành (fact-fix 28/09/2026) |
| Purpose | Identify centerpiece | Validate user intent match |
| Evaluation | Annotation systems | Engagement tracking |

## How Google Tracks Website Functions

### Về patent từng dẫn ở đây (fact-fix 28/09/2026)

US10565267B1 ("Determining a quality score for a content item") xếp hạng bài đăng trong stream mạng xã hội theo tốc độ tương tác ở hai khung thời gian, có trọng số theo loại tương tác. Patent không nói về trang web, không có khái niệm "chức năng hỏng", không có hệ số 5x hay 10x. Không dùng patent này làm căn cứ cho website function.

Ý niệm định tính vẫn giữ: tương tác chủ động (bấm nút, điền form, lọc) cho thấy trang làm được việc người dùng cần; chức năng hỏng làm mất chuyển đổi.

### Interaction Types

| Type | Examples | Mức ưu tiên kiểm (quy ước nội bộ) |
|------|----------|--------|
| **Passive** | View, scroll, pause | Thấp |
| **Active** | Click button, fill form | Cao |
| **Conversion** | Submit, purchase | Cao nhất |

Mức ưu tiên là quy ước để chọn chức năng cần kiểm trước, không phải trọng số của Google.

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

## Thời lượng kỳ vọng theo loại trang (quy ước thực hành)

US8868565B1 từng được dẫn ở đây: patent đặt ngưỡng click ngắn và click dài riêng cho từng nhóm nội dung, trong bối cảnh landing page quảng cáo, và không đưa ra các con số dưới đây. Bảng là quy ước để đọc số liệu GA4, không phải ngưỡng của Google.

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

## Tiện ích chức năng trên trang dịch vụ (checklist thực hành)

US20150234930A1 từng được dẫn ở đây là patent về tiện ích quảng cáo, không mô tả cách tìm kiếm tự nhiên chấm trang. Ba câu hỏi dưới đây là checklist kiểm của GTV:

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
  (giả thuyết thực hành: chưa có nguồn Google nối trực tiếp chức năng trang với thứ hạng)
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
