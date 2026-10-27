# E-commerce Website Functions - Implementation Guide

## Contents

- [Core Concept](#core-concept)
- [Google Patent References](#google-patent-references)
- [Category Page (PLP) Functions](#category-page-plp-functions)
- [Product Page (PDP) Functions](#product-page-pdp-functions)
- [E-commerce Functions Checklist](#e-commerce-functions-checklist)
- [Analytics Tracking](#analytics-tracking)
- [Intent Match Validation](#intent-match-validation)

## Core Concept

Website Functions for e-commerce validate **transactional intent**. Chức năng giúp trang đáp ứng hành trình mua. Google có đo click trên trang kết quả (NavBoost), nhưng chưa có nguồn cho việc Google chấm từng chức năng trên trang (giả thuyết thực hành).

```
Visual Semantic (Layout) + Website Function (Interactive)
= Intent Validation (giả thuyết thực hành, chưa có nguồn nối trực tiếp với thứ hạng)
```

## Bằng chứng (fact-fix 28/09/2026)

Ba patent từng dẫn ở đây đã bị gỡ ở SKILL.md v3.0 vì không mô tả website function trong tìm kiếm tự nhiên:

- US10565267B1: xếp hạng bài đăng mạng xã hội theo tốc độ tương tác.
- US8868565B1: ngưỡng thời lượng click theo nhóm nội dung, bối cảnh landing page quảng cáo.
- US20150234930A1: tiện ích quảng cáo.

Các con số thời lượng dưới đây là quy ước thực hành.

### Expected Durations (E-commerce, quy ước thực hành)

| Page Type | Expected Duration | User Behavior |
|-----------|-------------------|---------------|
| Category (PLP) | 30-90s | Browse, filter |
| Product (PDP) | 60-180s | Evaluate, compare |
| Cart | 30-60s | Review, edit |
| Checkout | 60-180s | Form filling |

---

## Category Page (PLP) Functions

### 1. Filter & Sort (CRITICAL)

```html
<section class="filters" aria-label="Product filters">
  <!-- Price Filter -->
  <div class="filter-group">
    <label for="filter-price">Price Range</label>
    <select id="filter-price" onchange="filterProducts()">
      <option value="all">All Prices</option>
      <option value="0-5000000">Under 5M VND</option>
      <option value="5000000-15000000">5M - 15M VND</option>
      <option value="15000000-30000000">15M - 30M VND</option>
      <option value="30000000+">Over 30M VND</option>
    </select>
  </div>
  
  <!-- Brand Filter -->
  <div class="filter-group">
    <fieldset>
      <legend>Brand</legend>
      <label><input type="checkbox" name="brand" value="apple"> Apple</label>
      <label><input type="checkbox" name="brand" value="samsung"> Samsung</label>
      <label><input type="checkbox" name="brand" value="xiaomi"> Xiaomi</label>
    </fieldset>
  </div>
  
  <!-- Sort -->
  <div class="sort-group">
    <label for="sort-by">Sort by</label>
    <select id="sort-by" onchange="sortProducts()">
      <option value="popular">Most Popular</option>
      <option value="price-asc">Price: Low to High</option>
      <option value="price-desc">Price: High to Low</option>
      <option value="newest">Newest</option>
      <option value="rating">Highest Rated</option>
    </select>
  </div>
</section>
```

**Google Tracks:**
| Interaction | Type | Weight |
|-------------|------|--------|
| Filter selection | Active | High |
| Multiple filters | Active | Very High |
| Sort change | Active | Medium |
| Filter → Product click | Conversion path | Highest |

### 2. Search Within Category

```html
<div class="category-search">
  <label for="search-products">Search in this category:</label>
  <input 
    type="search" 
    id="search-products"
    placeholder="Search iPhone 16..."
    oninput="searchProducts(this.value)"
  >
</div>
```

### 3. Quick View Modal

```html
<button 
  class="btn-quick-view" 
  onclick="openQuickView('product-123')"
  aria-label="Quick view iPhone 16 Pro Max"
>
  Quick View
</button>

<dialog id="quick-view-modal">
  <article class="product-preview">
    <img src="product.jpg" alt="...">
    <h3>iPhone 16 Pro Max 256GB</h3>
    <p class="price">29,990,000₫</p>
    <button class="add-to-cart">Add to Cart</button>
    <a href="/product/iphone-16-pro-max/">View Full Details</a>
  </article>
</dialog>
```

### 4. Add to Cart (From Grid)

```html
<article class="product-card">
  <img src="..." alt="...">
  <h3>iPhone 16 Pro Max</h3>
  <p class="price">29,990,000₫</p>
  
  <!-- Quick Add to Cart -->
  <button 
    class="btn-add-cart" 
    onclick="addToCart('SKU123')"
    data-product-id="SKU123"
  >
    Add to Cart
  </button>
  
  <!-- Or variant selection required -->
  <a href="/product/iphone-16/" class="btn-select-options">
    Select Options
  </a>
</article>
```

### 5. Compare Products

```html
<div class="compare-widget">
  <h3>Compare (<span id="compare-count">0</span>/4)</h3>
  
  <div class="compare-items" id="compare-list">
    <!-- Dynamically populated -->
  </div>
  
  <button 
    class="btn-compare" 
    onclick="openComparison()"
    disabled
  >
    Compare Now
  </button>
</div>

<!-- On each product card -->
<button 
  class="btn-add-compare" 
  onclick="addToCompare('SKU123')"
  aria-label="Add iPhone 16 to comparison"
>
  + Compare
</button>
```

### 6. Wishlist / Save

```html
<button 
  class="btn-wishlist" 
  onclick="toggleWishlist('SKU123')"
  aria-label="Save iPhone 16 to wishlist"
  aria-pressed="false"
>
  <span class="icon">♡</span>
  <span class="text">Save</span>
</button>
```

### 7. Pagination / Infinite Scroll

```html
<!-- Pagination -->
<nav class="pagination" aria-label="Product pages">
  <a href="?page=1" aria-current="page">1</a>
  <a href="?page=2">2</a>
  <a href="?page=3">3</a>
  <span>...</span>
  <a href="?page=10">10</a>
  <a href="?page=2" rel="next">Next →</a>
</nav>

<!-- OR Load More -->
<button class="btn-load-more" onclick="loadMoreProducts()">
  Load More Products (showing 24 of 156)
</button>
```

---

## Product Page (PDP) Functions

### 1. Add to Cart (PRIMARY CTA)

```html
<section class="purchase-actions">
  <!-- Variant Selection (if applicable) -->
  <div class="variants">
    <fieldset>
      <legend>Storage</legend>
      <label class="variant-option">
        <input type="radio" name="storage" value="256" checked>
        <span>256GB</span>
        <span class="price-diff">29,990,000₫</span>
      </label>
      <label class="variant-option">
        <input type="radio" name="storage" value="512">
        <span>512GB</span>
        <span class="price-diff">+3,000,000₫</span>
      </label>
    </fieldset>
    
    <fieldset>
      <legend>Color</legend>
      <label class="color-option">
        <input type="radio" name="color" value="black" checked>
        <span class="swatch" style="background: #1d1d1d"></span>
        <span>Black Titanium</span>
      </label>
      <!-- More colors -->
    </fieldset>
  </div>
  
  <!-- Quantity -->
  <div class="quantity">
    <label for="qty">Quantity:</label>
    <button onclick="decreaseQty()" aria-label="Decrease quantity">−</button>
    <input type="number" id="qty" value="1" min="1" max="10">
    <button onclick="increaseQty()" aria-label="Increase quantity">+</button>
  </div>
  
  <!-- PRIMARY CTA -->
  <button 
    class="btn-add-cart primary" 
    onclick="addToCart()"
    data-product="iphone-16-pro-max"
  >
    <span class="icon">🛒</span>
    Add to Cart - 29,990,000₫
  </button>
  
  <!-- SECONDARY CTA -->
  <button 
    class="btn-buy-now secondary" 
    onclick="buyNow()"
  >
    Buy Now
  </button>
</section>
```

**Google Tracks:**
| Interaction | Type | Weight |
|-------------|------|--------|
| Variant selection | Active | High |
| Quantity change | Active | Medium |
| Add to Cart click | **Conversion** | Highest |
| Buy Now click | **Conversion** | Highest |

### 2. Image Gallery

```html
<section class="product-gallery">
  <!-- Main Image -->
  <figure class="main-image">
    <img 
      id="main-product-img"
      src="main.jpg" 
      alt="iPhone 16 Pro Max - Front view"
      onclick="openLightbox()"
    >
    <button class="btn-zoom" onclick="openLightbox()" aria-label="Zoom image">
      🔍 Zoom
    </button>
  </figure>
  
  <!-- Thumbnails -->
  <div class="thumbnails" role="tablist">
    <button 
      role="tab" 
      aria-selected="true"
      onclick="changeImage('front.jpg')"
    >
      <img src="front-thumb.jpg" alt="Front view">
    </button>
    <button 
      role="tab"
      onclick="changeImage('back.jpg')"
    >
      <img src="back-thumb.jpg" alt="Back view">
    </button>
    <button 
      role="tab"
      onclick="playVideo('demo.mp4')"
    >
      <img src="video-thumb.jpg" alt="Demo video">
      <span class="play-icon">▶</span>
    </button>
  </div>
  
  <!-- Lightbox -->
  <dialog id="lightbox">
    <button class="close" onclick="closeLightbox()">✕</button>
    <img src="" alt="" id="lightbox-img">
    <nav class="lightbox-nav">
      <button onclick="prevImage()">←</button>
      <button onclick="nextImage()">→</button>
    </nav>
  </dialog>
</section>
```

### 3. Reviews & Ratings

```html
<section class="reviews" id="reviews">
  <h2>Customer Reviews</h2>
  
  <!-- Summary -->
  <div class="review-summary">
    <div class="rating-display">
      <span class="score">4.8</span>
      <span class="stars">★★★★★</span>
      <span class="count">(1,245 reviews)</span>
    </div>
    
    <!-- Rating breakdown -->
    <div class="rating-bars">
      <div class="bar"><span>5★</span><progress value="85" max="100"></progress><span>85%</span></div>
      <div class="bar"><span>4★</span><progress value="10" max="100"></progress><span>10%</span></div>
      <!-- ... -->
    </div>
  </div>
  
  <!-- Filter reviews -->
  <div class="review-filters">
    <button onclick="filterReviews('all')" class="active">All</button>
    <button onclick="filterReviews(5)">5 Stars</button>
    <button onclick="filterReviews(4)">4 Stars</button>
    <button onclick="filterReviews('with-photos')">With Photos</button>
  </div>
  
  <!-- Write Review CTA -->
  <button class="btn-write-review" onclick="openReviewForm()">
    Write a Review
  </button>
  
  <!-- Reviews List -->
  <div class="reviews-list">
    <article class="review">
      <header>
        <span class="stars">★★★★★</span>
        <span class="author">Nguyễn Văn A</span>
        <time>Dec 10, 2025</time>
        <span class="verified">✓ Verified Purchase</span>
      </header>
      <h4>Excellent phone!</h4>
      <p>Review content...</p>
      <div class="review-images">
        <img src="review-photo1.jpg" alt="Customer photo" onclick="openImage(this)">
      </div>
      <footer>
        <button onclick="helpfulReview('rev123')">
          👍 Helpful (24)
        </button>
      </footer>
    </article>
  </div>
  
  <!-- Load more reviews -->
  <button onclick="loadMoreReviews()">Show More Reviews</button>
</section>
```

### 4. Q&A Section

```html
<section class="product-qa" id="qa">
  <h2>Questions & Answers</h2>
  
  <button class="btn-ask" onclick="openQuestionForm()">
    Ask a Question
  </button>
  
  <div class="search-qa">
    <input type="search" placeholder="Search questions..." oninput="searchQA(this.value)">
  </div>
  
  <div class="qa-list">
    <article class="qa-item">
      <h4 class="question">
        <span class="label">Q:</span>
        Does this support eSIM?
      </h4>
      <div class="answer">
        <span class="label">A:</span>
        <p>Yes, iPhone 16 Pro Max supports dual eSIM...</p>
        <span class="answerer">Answered by XTMobile - Official Store</span>
      </div>
    </article>
  </div>
</section>
```

### 5. Stock & Delivery Info

```html
<section class="availability">
  <!-- Stock Status -->
  <div class="stock-status in-stock">
    <span class="icon">✓</span>
    <span>In Stock</span>
    <span class="qty">(15 available)</span>
  </div>
  
  <!-- Delivery Estimate -->
  <div class="delivery">
    <h4>Delivery Options</h4>
    
    <div class="delivery-option">
      <input type="radio" name="delivery" id="standard" checked>
      <label for="standard">
        <strong>Standard Delivery</strong>
        <span>2-3 business days</span>
        <span class="price">Free</span>
      </label>
    </div>
    
    <div class="delivery-option">
      <input type="radio" name="delivery" id="express">
      <label for="express">
        <strong>Express Delivery</strong>
        <span>Next day</span>
        <span class="price">50,000₫</span>
      </label>
    </div>
  </div>
  
  <!-- Store Pickup -->
  <div class="store-pickup">
    <button onclick="checkStoreAvailability()">
      Check Store Availability
    </button>
  </div>
</section>
```

### 6. Sticky Add to Cart (Mobile)

```html
<div class="sticky-cart mobile-only">
  <div class="product-mini">
    <img src="thumb.jpg" alt="...">
    <span class="price">29,990,000₫</span>
  </div>
  <button class="btn-add-cart" onclick="addToCart()">
    Add to Cart
  </button>
</div>
```

---

## E-commerce Functions Checklist

### Category Page (PLP)

| Function | Priority | Status |
|----------|----------|--------|
| Filter by attributes | P1 CRITICAL | [ ] |
| Sort options | P1 CRITICAL | [ ] |
| Search within category | P1 | [ ] |
| Add to Cart (quick) | P1 | [ ] |
| Pagination/Load more | P1 | [ ] |
| Quick View modal | P2 | [ ] |
| Compare products | P2 | [ ] |
| Wishlist/Save | P2 | [ ] |
| Recently viewed | P3 | [ ] |

### Product Page (PDP)

| Function | Priority | Status |
|----------|----------|--------|
| Add to Cart | P1 CRITICAL | [ ] |
| Variant selection | P1 CRITICAL | [ ] |
| Image gallery + zoom | P1 | [ ] |
| Stock status | P1 | [ ] |
| Buy Now | P1 | [ ] |
| Reviews display | P2 | [ ] |
| Write review | P2 | [ ] |
| Q&A section | P2 | [ ] |
| Delivery estimate | P2 | [ ] |
| Store availability | P3 | [ ] |
| Share buttons | P3 | [ ] |
| Sticky cart (mobile) | P3 | [ ] |

---

## Analytics Tracking

```javascript
// Category Page Events
gtag('event', 'filter_products', {
  'event_category': 'ecommerce',
  'filter_type': 'price',
  'filter_value': '5000000-15000000'
});

gtag('event', 'sort_products', {
  'event_category': 'ecommerce',
  'sort_by': 'price-asc'
});

// Product Page Events
gtag('event', 'view_item', {
  'currency': 'VND',
  'value': 29990000,
  'items': [{
    'item_id': 'SKU123',
    'item_name': 'iPhone 16 Pro Max 256GB'
  }]
});

gtag('event', 'add_to_cart', {
  'currency': 'VND',
  'value': 29990000,
  'items': [{
    'item_id': 'SKU123',
    'item_name': 'iPhone 16 Pro Max 256GB',
    'quantity': 1
  }]
});

gtag('event', 'select_item', {
  'item_list_name': 'Category: iPhone',
  'items': [{ 'item_id': 'SKU123' }]
});
```

---

## Intent Match Validation

### ✅ Good: Functions Match Intent

| Page Says | Function Exists | Result |
|-----------|-----------------|--------|
| "156 products" | Working filters | ✅ User can narrow |
| "Add to Cart" | Button works | ✅ User can buy |
| "In Stock" | Real inventory | ✅ User trusts |
| "Customer Reviews" | Can read/write | ✅ User validates |

### ❌ Bad: Functions Missing/Broken

| Page Says | Function Issue | Result |
|-----------|----------------|--------|
| "Filter by Price" | Filter broken | ❌ User leaves |
| "Add to Cart" | Button doesn't work | ❌ Lost sale |
| "Check Store" | No store data | ❌ Intent mismatch |
| "4.8 stars" | No actual reviews | ❌ Trust broken |
