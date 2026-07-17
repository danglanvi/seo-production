# E-commerce Page Visual Semantic - Implementation Guide

## Contents

- [Page Types in E-commerce](#page-types-in-e-commerce)
- [Category Page (Product Listing Page - PLP)](#category-page-product-listing-page---plp)
- [Product Page (PDP)](#product-page-pdp)
- [Collection/Curated List Page](#collectioncurated-list-page)
- [E-commerce Visual Semantic Checklist](#e-commerce-visual-semantic-checklist)
- [Schema.org for E-commerce Visual Semantic](#schemaorg-for-e-commerce-visual-semantic)

## Page Types in E-commerce

| Page Type | Primary Intent | Centerpiece Focus |
|-----------|---------------|-------------------|
| **Category Page (PLP)** | Browse, Compare | Product grid + filters |
| **Product Page (PDP)** | Evaluate, Buy | Product info + CTA |
| **Collection/List Page** | Discover | Curated product showcase |
| **Brand Page** | Learn, Trust | Brand story + products |

---

## Category Page (Product Listing Page - PLP)

### Centerpiece Annotation

```
[HEADER - 5-10% weight]
  Navigation + Search

[ABOVE FOLD - CENTERPIECE SIGNALS]
  H1: Category Name (e.g., "iPhone 16 Pro Max")
  Breadcrumb: Home > Phones > Apple > iPhone 16
  
  [FILTER BAR - Prominent]
  Price | Storage | Color | Condition
  
  [PRODUCT COUNT]
  "Showing 24 of 156 products"

[MAIN CONTENT - 100% weight]
  [PRODUCT GRID]
  ├─ Product Card 1 (Image + Name + Price + Rating)
  ├─ Product Card 2
  └─ Product Card N
  
  [PAGINATION / LOAD MORE]

[SUPPORTING - 60-80% weight]
  Category Description (SEO text)
  Buying Guide link
  Related Categories

[SIDEBAR - 20-40% weight]
  Refinement filters (desktop)
  Recently viewed
  Compare widget

[FOOTER - 5-10% weight]
```

### Visual Weight Distribution

| Element | Weight | Size/Position |
|---------|--------|---------------|
| H1 Category | 100% | 32px+, top of main |
| Filter bar | 80% | Prominent, sticky |
| Product grid | 100% | 60-70% viewport |
| Product cards | Equal | Uniform grid |
| SEO text | 40% | Below products, collapsed |
| Sidebar filters | 30% | Narrow, left side |

### HTML Structure

```html
<main>
  <header class="category-header">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement">Home</li>
        <li itemprop="itemListElement">Phones</li>
        <li itemprop="itemListElement" aria-current="page">iPhone 16</li>
      </ol>
    </nav>
    
    <h1>iPhone 16 Pro Max</h1>
    <p class="product-count">156 products available</p>
  </header>
  
  <section class="filters" aria-label="Product filters">
    <div class="filter-group">
      <label>Price Range</label>
      <select>...</select>
    </div>
    <!-- More filters -->
  </section>
  
  <section class="product-grid" aria-label="Products">
    <article class="product-card" itemscope itemtype="https://schema.org/Product">
      <img itemprop="image" src="..." alt="iPhone 16 Pro Max 256GB Black">
      <h2 itemprop="name">iPhone 16 Pro Max 256GB</h2>
      <div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
        <span itemprop="price">29,990,000</span>
        <span itemprop="priceCurrency">VND</span>
      </div>
      <div class="rating" itemprop="aggregateRating">★★★★☆ (245)</div>
      <button class="add-to-cart">Add to Cart</button>
    </article>
    <!-- More products -->
  </section>
  
  <section class="category-description">
    <h2>About iPhone 16 Pro Max</h2>
    <p>SEO content about category...</p>
  </section>
</main>

<aside class="sidebar">
  <section class="compare-widget">
    <h3>Compare Products (0/3)</h3>
  </section>
</aside>
```

### Common Mistakes - Category Pages

| Mistake | Problem | Fix |
|---------|---------|-----|
| SEO text above products | Pushes centerpiece down | Move below or collapse |
| Too many filters visible | Overwhelms, dilutes focus | Progressive disclosure |
| Product cards inconsistent | No clear grid pattern | Uniform card design |
| H1 not category name | Centerpiece mismatch | H1 = exact category |
| Banner larger than grid | Wrong centerpiece | Minimize banner |

---

## Product Page (PDP)

### Centerpiece Annotation

```
[HEADER - 5-10%]

[ABOVE FOLD - CENTERPIECE - 100% weight]
  ┌─────────────────────────────────────────────┐
  │ [PRODUCT GALLERY]  │  [PRODUCT INFO]        │
  │ - Main image       │  - H1: Product name    │
  │ - Thumbnails       │  - Price (prominent)   │
  │ - Zoom/video       │  - Rating + reviews    │
  │                    │  - Key specs           │
  │                    │  - [ADD TO CART] ←CTA  │
  │                    │  - Stock status        │
  └─────────────────────────────────────────────┘

[SUPPORTING - 60-80% weight]
  Product Description (expandable)
  Specifications Table
  Related Products
  Customer Reviews

[SUPPLEMENTARY - 40% weight]
  Q&A / FAQ
  Shipping info
  Return policy
  Recently viewed

[FOOTER - 5-10%]
```

### Visual Weight - Product Page

| Element | Weight | Why |
|---------|--------|-----|
| Product Image | 100% | Visual centerpiece |
| H1 Product Name | 100% | Topic identification |
| Price | 100% | Primary decision factor |
| Add to Cart | 100% | Conversion action |
| Specs summary | 80% | Decision support |
| Full description | 60% | Supporting detail |
| Reviews | 60% | Social proof |
| Related products | 40% | Cross-sell (secondary) |

### HTML Structure

```html
<main itemscope itemtype="https://schema.org/Product">
  <article class="product-detail">
    <!-- Breadcrumb -->
    <nav class="breadcrumb">...</nav>
    
    <div class="product-primary">
      <!-- Gallery - CENTERPIECE -->
      <section class="product-gallery">
        <figure>
          <img itemprop="image" src="main.jpg" alt="iPhone 16 Pro Max - Front view">
          <figcaption>iPhone 16 Pro Max in Black Titanium</figcaption>
        </figure>
        <div class="thumbnails">...</div>
      </section>
      
      <!-- Info - CENTERPIECE -->
      <section class="product-info">
        <h1 itemprop="name">iPhone 16 Pro Max 256GB Black Titanium</h1>
        
        <div class="rating" itemprop="aggregateRating" itemscope itemtype="https://schema.org/AggregateRating">
          <span itemprop="ratingValue">4.8</span>/5
          (<span itemprop="reviewCount">1,245</span> reviews)
        </div>
        
        <div class="price" itemprop="offers" itemscope itemtype="https://schema.org/Offer">
          <strong itemprop="price">29,990,000</strong>
          <span itemprop="priceCurrency">VND</span>
          <link itemprop="availability" href="https://schema.org/InStock">
          <span class="stock">In Stock</span>
        </div>
        
        <!-- Key specs - Quick reference -->
        <dl class="key-specs">
          <dt>Storage</dt><dd>256GB</dd>
          <dt>Display</dt><dd>6.9" Super Retina XDR</dd>
          <dt>Chip</dt><dd>A18 Pro</dd>
        </dl>
        
        <!-- Variants -->
        <div class="variants">
          <fieldset>
            <legend>Storage</legend>
            <label><input type="radio" name="storage" value="256"> 256GB</label>
            <label><input type="radio" name="storage" value="512"> 512GB</label>
            <label><input type="radio" name="storage" value="1024"> 1TB</label>
          </fieldset>
        </div>
        
        <!-- PRIMARY CTA -->
        <button class="btn-add-cart" type="button">
          Add to Cart - 29,990,000₫
        </button>
        
        <button class="btn-buy-now" type="button">
          Buy Now
        </button>
      </section>
    </div>
    
    <!-- SUPPORTING CONTENT -->
    <section class="product-description" itemprop="description">
      <h2>Product Description</h2>
      <div class="description-content">
        <p>Full description...</p>
      </div>
    </section>
    
    <section class="specifications">
      <h2>Specifications</h2>
      <table class="spec-table">
        <caption>iPhone 16 Pro Max Technical Specifications</caption>
        <tbody>
          <tr><th scope="row">Display</th><td>6.9" OLED, 2868x1320</td></tr>
          <tr><th scope="row">Processor</th><td>A18 Pro, 6-core</td></tr>
          <!-- More specs -->
        </tbody>
      </table>
    </section>
    
    <section class="reviews" id="reviews">
      <h2>Customer Reviews</h2>
      <!-- Review content -->
    </section>
  </article>
  
  <!-- Related Products - SUPPLEMENTARY -->
  <section class="related-products">
    <h2>You May Also Like</h2>
    <div class="product-carousel">...</div>
  </section>
</main>
```

### Above-the-Fold Checklist (PDP)

- [ ] H1 product name visible
- [ ] Main product image visible (not cropped)
- [ ] Price clearly displayed
- [ ] Add to Cart button visible
- [ ] Key specs/variants visible
- [ ] Rating visible (if available)
- [ ] Stock status visible

---

## Collection/Curated List Page

### Use Cases
- "Best Gaming Phones 2025"
- "Top 10 Budget Laptops"
- "Editor's Pick: Headphones"

### Centerpiece Structure

```
[ABOVE FOLD]
  H1: "Best Gaming Phones 2025" (List title)
  Intro: Summary + selection criteria
  Quick comparison table (Top 3)

[MAIN CONTENT - CENTERPIECE]
  [PRODUCT 1] ← Numbered, ranked
  - Image + Name + Key differentiator
  - Why it's #1
  - Pros/Cons
  - Price + Buy CTA
  
  [PRODUCT 2]
  ...
  
  [COMPARISON TABLE]
  All products side-by-side

[SUPPORTING]
  Buying Guide
  FAQ
  Methodology

[SUPPLEMENTARY]
  Related lists
  Newsletter signup
```

### Visual Weight - Collection Page

| Element | Weight | Reasoning |
|---------|--------|-----------|
| H1 List Title | 100% | Centerpiece identifier |
| #1 Product | 100% | Most important recommendation |
| #2-3 Products | 80% | Top picks |
| #4+ Products | 60% | Additional options |
| Comparison table | 80% | Decision support |
| Buying guide | 40% | Supporting education |

---

## E-commerce Visual Semantic Checklist

### Category Pages
- [ ] H1 = Category name (exact match)
- [ ] Filter bar prominent, functional
- [ ] Product grid = visual centerpiece
- [ ] Product cards uniform
- [ ] SEO text below/collapsed
- [ ] Clear product count
- [ ] Pagination/load more working

### Product Pages
- [ ] Product image = largest element
- [ ] H1 = Full product name
- [ ] Price = prominent, above fold
- [ ] Add to Cart = visible, above fold
- [ ] Key specs visible without scroll
- [ ] Reviews accessible (not hidden)
- [ ] Related products = lower prominence

### Collection Pages
- [ ] H1 = List title with context
- [ ] #1 pick = most prominent
- [ ] Clear ranking/numbering
- [ ] Comparison table included
- [ ] Each product has CTA
- [ ] Selection criteria explained

---

## Schema.org for E-commerce Visual Semantic

### Product Schema (PDP)
```json
{
  "@type": "Product",
  "name": "iPhone 16 Pro Max 256GB",
  "image": "product-image.jpg",
  "offers": {
    "@type": "Offer",
    "price": "29990000",
    "priceCurrency": "VND",
    "availability": "InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "1245"
  }
}
```

### ItemList Schema (Collection)
```json
{
  "@type": "ItemList",
  "name": "Best Gaming Phones 2025",
  "numberOfItems": 10,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Product",
        "name": "ROG Phone 8 Pro"
      }
    }
  ]
}
```
