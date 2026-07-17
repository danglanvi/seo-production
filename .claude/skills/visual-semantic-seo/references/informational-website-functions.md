# Informational Website Functions - Implementation Guide

## Contents

- [Core Concept](#core-concept)
- [Intent Types by Page](#intent-types-by-page)
- [Encyclopedia / A-Z List Functions](#encyclopedia-a-z-list-functions)
- [Educational Engagement Functions](#educational-engagement-functions)
- [How-To / Tutorial Functions](#how-to-tutorial-functions)
- [Glossary / Definition Functions](#glossary-definition-functions)
- [Informational Functions Checklist](#informational-functions-checklist)
- [Analytics Tracking](#analytics-tracking)
- [Intent Match Validation](#intent-match-validation)

## Core Concept

Website Functions for informational sites validate **educational/discovery intent**. Google tracks interactions to determine if users successfully find, learn, and engage with content.

```
Visual Semantic (Layout) + Website Function (Interactive)
= Intent Validation = Quality Score = Ranking
```

## Intent Types by Page

| Page Type | Primary Intent | Success Metric |
|-----------|---------------|----------------|
| Encyclopedia/A-Z | Browse, Discover | Pages/session, time |
| How-To/Tutorial | Learn process | Completion rate |
| Glossary | Understand term | Quick answer found |
| Comparison | Compare options | Decision made |
| Long-form Article | Deep learning | Read time, scroll depth |

### Expected Durations (Informational)

| Page Type | Expected Duration | User Behavior |
|-----------|-------------------|---------------|
| A-Z List (200+ items) | 120-300s | Browse multiple entries |
| Individual entry | 30-60s | Quick reference |
| Tutorial | 180-600s | Follow steps |
| Definition | 15-45s | Quick answer |
| Comparison | 120-240s | Evaluate options |

---

## Encyclopedia / A-Z List Functions

### 1. Alphabet Navigation (CRITICAL)

```html
<nav class="alphabet-nav" aria-label="Browse animals by letter">
  <ul>
    <li><a href="/animals-a/" class="active" aria-current="page">A</a></li>
    <li><a href="/animals-b/">B</a></li>
    <li><a href="/animals-c/">C</a></li>
    <!-- ... through Z -->
    <li><a href="/animals-0-9/">0-9</a></li>
  </ul>
</nav>
```

**Google Tracks:**
| Interaction | Type | Weight |
|-------------|------|--------|
| Click letter | Active | High (5x) |
| Navigate A→B→C | Sequential | Excellent engagement |
| Return to letter | Active | Topic interest confirmed |

**Placement:** Sticky header or prominent above-fold

### 2. Search Within Content

```html
<div class="content-search">
  <label for="search-animals">Find an animal:</label>
  <input 
    type="search" 
    id="search-animals"
    placeholder="Search by name (e.g., Alpaca, Axolotl...)"
    oninput="searchEntries(this.value)"
    autocomplete="off"
  >
  
  <!-- Search suggestions dropdown -->
  <div id="search-suggestions" class="suggestions-dropdown" role="listbox">
    <!-- Dynamically populated -->
  </div>
</div>
```

**Features:**
- Autocomplete suggestions
- Highlight matching text
- Show entry count: "Found 5 animals matching 'al'"

### 3. Filter by Category/Classification

```html
<section class="filters" aria-label="Filter animals">
  <div class="filter-buttons">
    <button 
      class="filter-btn active" 
      data-filter="all"
      onclick="filterEntries('all')"
      aria-pressed="true"
    >
      All (200+)
    </button>
    <button 
      class="filter-btn" 
      data-filter="mammal"
      onclick="filterEntries('mammal')"
      aria-pressed="false"
    >
      Mammals (99)
    </button>
    <button 
      class="filter-btn" 
      data-filter="reptile"
      onclick="filterEntries('reptile')"
    >
      Reptiles (22)
    </button>
    <button 
      class="filter-btn" 
      data-filter="bird"
      onclick="filterEntries('bird')"
    >
      Birds (23)
    </button>
    <button 
      class="filter-btn" 
      data-filter="endangered"
      onclick="filterEntries('endangered')"
    >
      🔴 Endangered
    </button>
  </div>
  
  <!-- Active filters display -->
  <div class="active-filters" id="active-filters">
    <span>Showing: <strong>Mammals (99)</strong></span>
    <button onclick="clearFilters()">Clear all</button>
  </div>
</section>
```

### 4. Table of Contents / Jump Links

```html
<nav class="toc" aria-label="Table of Contents">
  <h2>On This Page</h2>
  
  <details open>
    <summary>Most Popular (19)</summary>
    <ul>
      <li><a href="#alpaca">Alpaca</a></li>
      <li><a href="#alligator">Alligator</a></li>
      <li><a href="#axolotl">Axolotl</a></li>
      <!-- ... -->
    </ul>
  </details>
  
  <details>
    <summary>Mammals (99)</summary>
    <ul>
      <li><a href="#aardvark">Aardvark</a></li>
      <!-- ... -->
    </ul>
  </details>
  
  <details>
    <summary>Reptiles (22)</summary>
    <ul><!-- ... --></ul>
  </details>
</nav>
```

**Behavior:**
- Sticky on desktop (sidebar)
- Collapsible on mobile
- Highlight current section on scroll

### 5. Save / Bookmark Entries

```html
<article class="entry" id="alpaca">
  <header>
    <h3>1. Alpaca</h3>
    
    <div class="entry-actions">
      <button 
        class="btn-save" 
        onclick="toggleSave('alpaca')"
        aria-label="Save Alpaca to favorites"
        aria-pressed="false"
      >
        <span class="icon">♡</span>
        <span class="text">Save</span>
      </button>
    </div>
  </header>
  <!-- Entry content -->
</article>

<!-- Saved Items Panel -->
<aside class="saved-panel" id="saved-panel">
  <header>
    <h2>My Saved Animals (<span id="saved-count">0</span>)</h2>
    <button onclick="closeSavedPanel()" aria-label="Close">✕</button>
  </header>
  
  <ul id="saved-list">
    <!-- Dynamically populated -->
  </ul>
  
  <footer>
    <button onclick="shareList()">Share My List</button>
    <button onclick="downloadList()">Download PDF</button>
    <button onclick="clearList()">Clear All</button>
  </footer>
</aside>

<!-- Floating trigger -->
<button 
  class="btn-saved-trigger" 
  onclick="openSavedPanel()"
  aria-label="View saved animals"
>
  ♡ <span id="saved-badge">0</span>
</button>
```

### 6. Share Functions (Per Entry)

```html
<div class="share-entry">
  <span class="label">Share:</span>
  
  <button 
    onclick="shareEntry('alpaca', 'facebook')" 
    aria-label="Share Alpaca on Facebook"
    class="share-btn facebook"
  >
    <span class="icon">f</span>
  </button>
  
  <button 
    onclick="shareEntry('alpaca', 'twitter')"
    aria-label="Share on Twitter"
    class="share-btn twitter"
  >
    <span class="icon">𝕏</span>
  </button>
  
  <button 
    onclick="shareEntry('alpaca', 'pinterest')"
    aria-label="Pin this image"
    class="share-btn pinterest"
  >
    <span class="icon">P</span>
  </button>
  
  <button 
    onclick="copyLink('alpaca')"
    aria-label="Copy link"
    class="share-btn link"
  >
    <span class="icon">🔗</span>
  </button>
</div>
```

### 7. Compare Entries

```html
<div class="compare-feature">
  <div class="compare-header">
    <h3>Compare Animals</h3>
    <span class="compare-count">(<span id="compare-count">0</span>/3 selected)</span>
  </div>
  
  <div class="compare-selected" id="compare-selected">
    <!-- Dynamically populated with selected items -->
  </div>
  
  <button 
    class="btn-compare" 
    onclick="showComparison()"
    disabled
    id="btn-compare"
  >
    Compare Now
  </button>
</div>

<!-- Add to Compare button on each entry -->
<button 
  class="btn-add-compare" 
  onclick="addToCompare('alpaca')"
  data-entry="alpaca"
>
  + Compare
</button>

<!-- Comparison Modal -->
<dialog id="comparison-modal">
  <header>
    <h2>Animal Comparison</h2>
    <button onclick="closeComparison()">✕</button>
  </header>
  
  <table class="comparison-table">
    <thead>
      <tr>
        <th>Attribute</th>
        <th>Alpaca</th>
        <th>Llama</th>
        <th>Vicuña</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">Scientific Name</th>
        <td>Vicugna pacos</td>
        <td>Lama glama</td>
        <td>Vicugna vicugna</td>
      </tr>
      <tr>
        <th scope="row">Size</th>
        <td>32-39 inches</td>
        <td>42-46 inches</td>
        <td>30-36 inches</td>
      </tr>
      <!-- More rows -->
    </tbody>
  </table>
  
  <footer>
    <button onclick="shareComparison()">Share Comparison</button>
    <button onclick="downloadComparison()">Download PDF</button>
  </footer>
</dialog>
```

### 8. Quick Facts Toggle (Mobile)

```html
<article class="entry" id="alpaca">
  <h3>1. Alpaca</h3>
  
  <!-- Image always visible -->
  <figure>
    <img src="alpaca.jpg" alt="...">
  </figure>
  
  <!-- Quick facts - collapsible on mobile -->
  <details class="quick-facts-toggle" open>
    <summary>Quick Facts</summary>
    <table class="quick-facts">
      <!-- Table content -->
    </table>
  </details>
  
  <!-- Description - collapsible on mobile for long lists -->
  <details class="description-toggle">
    <summary>Full Description</summary>
    <div class="description">
      <p>...</p>
    </div>
  </details>
</article>
```

---

## Educational Engagement Functions

### 9. Newsletter Signup

```html
<aside class="newsletter-cta">
  <h3>🐾 Love Animals?</h3>
  <p>Join <strong>10,000+ animal lovers</strong> for weekly wildlife facts and conservation news.</p>
  
  <form id="newsletter-form" action="/api/subscribe" method="POST">
    <label for="email" class="sr-only">Email address</label>
    <input 
      type="email" 
      id="email"
      name="email" 
      placeholder="your@email.com"
      required
    >
    <button type="submit">Subscribe Free</button>
  </form>
  
  <p class="privacy">No spam. Unsubscribe anytime.</p>
</aside>
```

**Placement Options:**
- After "Most Popular" section (high engagement point)
- Sticky sidebar (desktop)
- After 5th entry (inline)
- Before footer (final CTA)

### 10. Quiz / Knowledge Test

```html
<aside class="quiz-cta">
  <h3>🧠 Test Your Knowledge!</h3>
  <p>How well do you know animals starting with A?</p>
  
  <div class="quiz-stats">
    <span><strong>2,500</strong> people took this quiz</span>
    <span>Average score: <strong>7/10</strong></span>
  </div>
  
  <button class="btn-quiz" onclick="startQuiz('animals-a')">
    Take the Quiz (10 questions)
  </button>
</aside>

<!-- Quiz Modal -->
<dialog id="quiz-modal">
  <header>
    <h2>Animals A-Z Quiz</h2>
    <span class="progress">Question <span id="q-num">1</span>/10</span>
  </header>
  
  <div class="quiz-content">
    <p class="question" id="question">
      What is the scientific name for Alpaca?
    </p>
    
    <div class="options">
      <label>
        <input type="radio" name="answer" value="a">
        <span>Lama glama</span>
      </label>
      <label>
        <input type="radio" name="answer" value="b">
        <span>Vicugna pacos</span>
      </label>
      <label>
        <input type="radio" name="answer" value="c">
        <span>Camelus bactrianus</span>
      </label>
    </div>
  </div>
  
  <footer>
    <button onclick="submitAnswer()">Next Question</button>
  </footer>
</dialog>
```

### 11. Downloadable Resources

```html
<section class="resources">
  <h3>📥 Free Resources</h3>
  
  <div class="resource-list">
    <a href="/downloads/animals-a-flashcards.pdf" class="resource-item" download>
      <span class="icon">📄</span>
      <span class="info">
        <strong>Flashcards</strong>
        <span>PDF • 2.4 MB</span>
      </span>
      <span class="action">Download</span>
    </a>
    
    <a href="/downloads/animals-a-coloring.pdf" class="resource-item" download>
      <span class="icon">🎨</span>
      <span class="info">
        <strong>Coloring Pages</strong>
        <span>PDF • 5.1 MB</span>
      </span>
      <span class="action">Download</span>
    </a>
    
    <a href="/downloads/animals-a-poster.pdf" class="resource-item" download>
      <span class="icon">🖼️</span>
      <span class="info">
        <strong>Classroom Poster</strong>
        <span>PDF • 8.3 MB</span>
      </span>
      <span class="action">Download</span>
    </a>
  </div>
</section>
```

### 12. Conservation CTA (Mission-Aligned)

```html
<section class="conservation-cta">
  <h2>🌍 Help Protect These Animals</h2>
  
  <div class="endangered-highlight">
    <p><strong>5 species</strong> on this page are endangered:</p>
    <ul>
      <li><a href="#axolotl">Axolotl</a> - Critically Endangered</li>
      <li><a href="#african-wild-dog">African Wild Dog</a> - Endangered</li>
      <!-- ... -->
    </ul>
  </div>
  
  <p>Your support helps fund conservation research and habitat protection.</p>
  
  <div class="donation-options">
    <button onclick="donate(10)" class="donate-btn">
      $10 - Protect 1 acre
    </button>
    <button onclick="donate(25)" class="donate-btn featured">
      $25 - Fund research
    </button>
    <button onclick="donate(50)" class="donate-btn">
      $50 - Sponsor an animal
    </button>
  </div>
  
  <a href="/conservation/" class="learn-more">
    Learn about our conservation partners →
  </a>
</section>
```

---

## How-To / Tutorial Functions

### 13. Progress Tracker

```html
<nav class="tutorial-progress" aria-label="Tutorial progress">
  <ol>
    <li class="completed" aria-current="false">
      <a href="#step-1">1. Gather Materials</a>
      <span class="status">✓</span>
    </li>
    <li class="current" aria-current="step">
      <a href="#step-2">2. Prepare Ingredients</a>
      <span class="status">●</span>
    </li>
    <li class="upcoming">
      <a href="#step-3">3. Mix Together</a>
    </li>
    <li class="upcoming">
      <a href="#step-4">4. Bake</a>
    </li>
    <li class="upcoming">
      <a href="#step-5">5. Serve</a>
    </li>
  </ol>
  
  <div class="progress-bar">
    <div class="progress-fill" style="width: 40%"></div>
  </div>
  <span class="progress-text">Step 2 of 5</span>
</nav>
```

### 14. Step Completion Checkboxes

```html
<section class="step" id="step-1">
  <header>
    <input 
      type="checkbox" 
      id="complete-step-1"
      onchange="markStepComplete(1, this.checked)"
    >
    <label for="complete-step-1">
      <h2><span class="step-num">1</span> Gather Materials</h2>
    </label>
  </header>
  
  <div class="step-content">
    <p>Instructions...</p>
    
    <!-- Checklist within step -->
    <ul class="checklist">
      <li>
        <input type="checkbox" id="item-1">
        <label for="item-1">2 cups flour</label>
      </li>
      <li>
        <input type="checkbox" id="item-2">
        <label for="item-2">1 cup sugar</label>
      </li>
    </ul>
  </div>
</section>
```

### 15. Print-Friendly Version

```html
<div class="tutorial-actions">
  <button onclick="window.print()" class="btn-print">
    🖨️ Print Tutorial
  </button>
  
  <button onclick="downloadPDF()" class="btn-download">
    📄 Download PDF
  </button>
</div>
```

---

## Glossary / Definition Functions

### 16. Quick Copy Definition

```html
<article class="definition">
  <h1>Topical Authority</h1>
  
  <div class="quick-definition">
    <p id="def-text">
      <strong>Topical Authority</strong> is a website's demonstrated expertise...
    </p>
    
    <button 
      onclick="copyDefinition()" 
      class="btn-copy"
      aria-label="Copy definition"
    >
      📋 Copy
    </button>
  </div>
</article>
```

### 17. Related Terms Navigation

```html
<nav class="related-terms">
  <h2>Related Terms</h2>
  
  <ul>
    <li>
      <a href="/glossary/semantic-seo/">
        <strong>Semantic SEO</strong>
        <span>Optimizing for meaning and context</span>
      </a>
    </li>
    <li>
      <a href="/glossary/e-e-a-t/">
        <strong>E-E-A-T</strong>
        <span>Experience, Expertise, Authority, Trust</span>
      </a>
    </li>
  </ul>
</nav>
```

---

## Informational Functions Checklist

### Encyclopedia / A-Z Pages

| Function | Priority | Status |
|----------|----------|--------|
| Alphabet navigation | P1 CRITICAL | [ ] |
| Search within content | P1 CRITICAL | [ ] |
| Filter by category | P1 CRITICAL | [ ] |
| Table of Contents | P1 | [ ] |
| Save/Bookmark entries | P2 | [ ] |
| Share per entry | P2 | [ ] |
| Compare entries | P2 | [ ] |
| Newsletter signup | P2 | [ ] |
| Quiz feature | P3 | [ ] |
| Downloadable resources | P3 | [ ] |
| Conservation CTA | P3 | [ ] |

### How-To / Tutorial Pages

| Function | Priority | Status |
|----------|----------|--------|
| Step progress tracker | P1 | [ ] |
| Jump to step | P1 | [ ] |
| Step completion checkbox | P2 | [ ] |
| Print-friendly version | P2 | [ ] |
| Materials checklist | P2 | [ ] |
| Video for each step | P3 | [ ] |
| Comments/Questions | P3 | [ ] |

### Glossary Pages

| Function | Priority | Status |
|----------|----------|--------|
| Quick copy definition | P1 | [ ] |
| Alphabet navigation | P1 | [ ] |
| Search terms | P1 | [ ] |
| Related terms | P2 | [ ] |
| Use in sentence | P3 | [ ] |

---

## Analytics Tracking

```javascript
// Entry views (scroll tracking)
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      gtag('event', 'view_entry', {
        'event_category': 'engagement',
        'entry_id': entry.target.id,
        'entry_name': entry.target.dataset.name
      });
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.entry').forEach(el => observer.observe(el));

// Filter usage
function filterEntries(category) {
  gtag('event', 'filter_content', {
    'event_category': 'engagement',
    'filter_type': 'category',
    'filter_value': category
  });
}

// Save to favorites
function toggleSave(entryId) {
  gtag('event', 'save_entry', {
    'event_category': 'engagement',
    'entry_id': entryId
  });
}

// Newsletter signup
document.getElementById('newsletter-form').addEventListener('submit', () => {
  gtag('event', 'newsletter_signup', {
    'event_category': 'conversion',
    'page_type': 'encyclopedia'
  });
});

// Quiz completion
function completeQuiz(score, total) {
  gtag('event', 'quiz_complete', {
    'event_category': 'engagement',
    'score': score,
    'total_questions': total,
    'percentage': (score/total * 100).toFixed(0)
  });
}

// Resource download
function downloadResource(resourceName) {
  gtag('event', 'download_resource', {
    'event_category': 'conversion',
    'resource_name': resourceName
  });
}
```

---

## Intent Match Validation

### ✅ Good: Functions Match Intent

| Page Says | Function Exists | Result |
|-----------|-----------------|--------|
| "200+ Animals" | Search + Filter | ✅ User can find |
| "Browse A-Z" | Alphabet nav works | ✅ User can explore |
| "Save favorites" | Bookmark functional | ✅ User can keep |
| "Compare" | Comparison works | ✅ User can evaluate |
| "Download" | PDF generates | ✅ User gets resource |

### ❌ Bad: Functions Missing/Broken

| Page Says | Function Issue | Result |
|-----------|----------------|--------|
| "Search animals" | Search broken | ❌ User can't find |
| "Filter by type" | Filter not working | ❌ User frustrated |
| "Take quiz" | Quiz errors | ❌ Engagement lost |
| "Subscribe" | Form broken | ❌ Lead lost |
