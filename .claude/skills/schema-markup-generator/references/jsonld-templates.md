# JSON-LD Templates theo Page Type

Template đầy đủ cho 8 page types v1 của `schema-markup-generator`. Mọi template dùng `@id` convention: `{domain}/#organization`, `{author-url}/#person` — reference cross-block, không nhân bản node.

🔴 Nhắc lại giới hạn: schema ✗ AI-citation lever (DiD 1.885 trang, Ahrefs 05/2026) — ✓ rich results / entity understanding / voice. Không dùng template nào dưới đây với lời hứa "tăng AI citation".

## Mục lục (TOC)

1. [Trạng thái rich results 07/2026 — bảng tra nhanh](#0-trạng-thái-rich-results-072026)
2. [Organization — homepage / Entity Home](#1-organization)
3. [LocalBusiness](#2-localbusiness)
4. [Person / Author + ProfilePage](#3-person--author--profilepage)
5. [Article / BlogPosting](#4-article--blogposting)
6. [Product (PDP)](#5-product-pdp)
7. [ItemList (PCP / Best List)](#6-itemlist-pcp--best-list)
8. [Service (Service Landing Page)](#7-service)
9. [Breadcrumb](#8-breadcrumb)
10. [Phụ lục A — Deprecated / không dùng](#phụ-lục-a--deprecated--không-dùng)
11. [Phụ lục B — Validate workflow](#phụ-lục-b--validate-workflow)

---

## 0. Trạng thái rich results 07/2026

Nguồn: Google Search Central — search gallery (last updated 2026-06-15): https://developers.google.com/search/docs/appearance/structured-data/search-gallery + changelog: https://developers.google.com/search/updates. 25 features còn hỗ trợ:

Article, Breadcrumb, Carousel (chỉ kèm Recipe/Course list/Restaurant/Movie), Course list, Dataset, Discussion forum, Education Q&A, Employer aggregate rating, Event, Image metadata, Job posting, Local business, Math solver, Movie, Organization, Product, Profile page, Q&A, Recipe, Review snippet, Software app, Speakable, Subscription & paywalled content, Vacation rental, Video.

| Type trong skill này | Rich result? | Ghi chú |
|---|---|---|
| Organization | ✅ (Knowledge Panel / attribution elements) | Khối đầy đủ đặt ở Entity Home (About page nếu có, homepage nếu không) |
| LocalBusiness | ✅ Local business | Kèm GBP |
| ProfilePage (+ Person) | ✅ Profile page | Author bio page |
| Article / BlogPosting | ✅ Article | |
| Product | ✅ Product / merchant listing | + Certification (Google thêm 10/2024, thay EnergyConsumptionDetails từ 04/2025 — developers.google.com/search/updates#certifications) |
| ItemList | ⚠️ Carousel CHỈ kèm Recipe/Course/Restaurant/Movie — KHÔNG có Product | PCP: rendering per card đến từ Product markup (merchant listing), không phải ItemList carousel |
| Service | ❌ không có rich result riêng | Vẫn có giá trị entity understanding — validate bằng validator.schema.org |
| Breadcrumb | ✅ Breadcrumb | |
| FAQPage | ❌ **CHẤM DỨT 07/05/2026** | Xem Phụ lục A |
| HowTo | ❌ deprecated 09/2023 | Xem Phụ lục A |

Format bắt buộc mọi template: JSON-LD trong `<script type="application/ld+json">`, đặt `<head>` hoặc `<body>`; Google đọc được JSON-LD inject bằng JS nhưng khuyến nghị server-side render.

---

## 1. Organization

**Vị trí:** khai đầy đủ 1 LẦN duy nhất tại **Entity Home** — thường là About page cho Organization (entity-home-checklist.md mục 1); site chưa có Entity Home riêng → homepage. Mọi trang khác — kể cả homepage khi Entity Home là About page — chỉ reference `{domain}/#organization`. Đây là node gốc của entity graph.

⚠️ **founder/author chưa có bio page:** nhúng inline Person (không `@id`) trong field `founder` — nâng cấp thành reference `{author-url}/#person` khi bio page ra đời; không bịa URL page chưa tồn tại.

| Nhóm | Fields |
|---|---|
| Required (skill này) | `@id`, `name`, `url`, `logo`, `sameAs` |
| Recommended (Google) | `legalName`, `address`, `contactPoint`, `description`, `foundingDate`, business identifiers: `iso6523Code`, `naics`, `duns`, `vatID`, `taxID` |

Business identifiers feed Knowledge Panel + attribution visual elements (Google Search Central — Organization markup).

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Tên Brand",
  "legalName": "Công ty TNHH ...",
  "url": "https://example.com/",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png"
  },
  "description": "Định nghĩa entity — khớp definitive answer trên Entity Home.",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "...",
    "addressLocality": "...",
    "addressRegion": "...",
    "postalCode": "...",
    "addressCountry": "VN"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+84-...",
    "contactType": "customer service"
  },
  "vatID": "<MST — nếu có thật>",
  "sameAs": [
    "https://vi.wikipedia.org/wiki/<chỉ khi ĐÃ Wikipedia Verify>",
    "https://www.wikidata.org/wiki/Q<chỉ khi QID thật>",
    "https://www.linkedin.com/company/...",
    "https://www.facebook.com/...",
    "https://www.youtube.com/@..."
  ]
}
</script>
```

⚠️ `sameAs`: URI unambiguous theo schema.org — Wikipedia page, Wikidata entity URI, official social profiles. KHÔNG bịa entry nào; thiếu thì để array ngắn.

---

## 2. LocalBusiness

**Vị trí:** homepage hoặc trang location. Chọn subtype sát nhất (Restaurant, Dentist, LegalService, Store… — tra schema.org trước khi dùng); không có subtype khớp → giữ `LocalBusiness`.

| Nhóm | Fields |
|---|---|
| Required | `@id`, `name`, `address` (NAP), `url` |
| Recommended | `telephone`, `openingHoursSpecification`, `geo`, `hasMap`, `priceRange`, `image`, `sameAs` (kèm GBP URL) |

🔴 NAP (Name-Address-Phone) trong schema phải consistent 100% với GBP + footer + mọi citation (sop/04).

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://example.com/#organization",
  "name": "Tên khớp GBP",
  "url": "https://example.com/",
  "image": "https://example.com/storefront.jpg",
  "telephone": "+84-...",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "...",
    "addressLocality": "...",
    "addressRegion": "...",
    "postalCode": "...",
    "addressCountry": "VN"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 10.7,
    "longitude": 106.7
  },
  "hasMap": "https://maps.google.com/?cid=...",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "08:00",
      "closes": "17:30"
    }
  ],
  "sameAs": [
    "https://www.google.com/maps/place/<GBP URL>",
    "https://www.facebook.com/..."
  ]
}
</script>
```

---

## 3. Person / Author + ProfilePage

**Vị trí:** author bio page. ProfilePage nằm trong gallery hiện hành — đúng type cho trang giới thiệu 1 person affiliated với site, với `mainEntity` là Person.

Vì sao quan trọng ([[Authorship]]): Article + named author + sameAs → author entity resolve được cross-site (author vectors tracked riêng khỏi website vectors); AI-era working belief (Indig 06/2026): named author thắng brand byline. Author có nhiều tên/cách phát âm → sameAs càng quan trọng cho reconciliation.

| Nhóm | Fields |
|---|---|
| Required | Person: `@id`, `name`, `url`, `sameAs`; ProfilePage: `mainEntity`, `dateModified` |
| Recommended | `jobTitle`, `worksFor` → `#organization`, `knowsAbout`, `image`, `alumniOf` |

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ProfilePage",
  "dateModified": "2026-07-07",
  "mainEntity": {
    "@type": "Person",
    "@id": "https://example.com/author/nguyen-van-a/#person",
    "name": "Nguyễn Văn A",
    "url": "https://example.com/author/nguyen-van-a/",
    "image": "https://example.com/authors/nguyen-van-a.jpg",
    "jobTitle": "Head of SEO",
    "worksFor": { "@id": "https://example.com/#organization" },
    "knowsAbout": ["Semantic SEO", "Topical Authority", "Entity SEO"],
    "sameAs": [
      "https://www.linkedin.com/in/...",
      "https://x.com/...",
      "https://scholar.google.com/citations?user=<nếu có>",
      "https://www.wikidata.org/wiki/Q<chỉ khi thật>"
    ]
  }
}
</script>
```

⚠️ `knowsAbout` phải khớp topical footprint thật của author (bài đã publish) — không nhồi topic chưa từng viết. Person schema đi cùng authentic main content creator signal ([[Algorithmic Authorship]] — stylometry consistency), không thay được nó.

---

## 4. Article / BlogPosting

**Vị trí:** mọi bài blog/article. `author` và `publisher` REFERENCE node qua `@id` — không khai lại đầy đủ.

| Nhóm | Fields |
|---|---|
| Required | `headline`, `author` → `#person`, `datePublished`, `image` |
| Recommended | `dateModified` (THẬT — không fake freshness), `publisher` → `#organization`, `description`, `mainEntityOfPage` |

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://example.com/bai-viet/" },
  "headline": "Khớp H1/title hiển thị",
  "description": "Khớp meta description / đoạn mở bài.",
  "image": [
    "https://example.com/img/cover-16x9.jpg",
    "https://example.com/img/cover-4x3.jpg",
    "https://example.com/img/cover-1x1.jpg"
  ],
  "datePublished": "2026-05-02",
  "dateModified": "2026-07-01",
  "author": { "@id": "https://example.com/author/nguyen-van-a/#person" },
  "publisher": { "@id": "https://example.com/#organization" }
}
</script>
```

Case study cho Service page → dùng `Article` hoặc `Report`. ⚠️ "CaseStudy" KHÔNG tồn tại trong schema.org (guideline nội bộ Service Landing Page ghi sai — cần lint).

---

## 5. Product (PDP)

🔴 Chuẩn GTV ([[Product Detail Page]]): Product schema đủ **4 field: `aggregateRating` + `review` + `offers` + `availability`** = **GTV completeness benchmark** — thiếu field = ít nguyên liệu render cạnh tranh hơn, KHÔNG phải fail eligibility. ⚠️ Phân biệt với **Google required** (official, 2026-07-13 — LINT-2026-009): Product *snippet* required = `name` + MỘT trong `review`/`aggregateRating`/`offers`; `availability` chỉ recommended trong Offer; *Merchant listing* (trang bán trực tiếp) có bộ requirements riêng — không trộn 2 sets (developers.google.com/search/docs/appearance/structured-data/product-snippet). Tất cả field khai phải có visible counterpart trên page — rating không hiển thị / review không tồn tại = spam risk, khi đó BỎ field chứ không bịa.

| Nhóm | Fields |
|---|---|
| Google required (Product snippet) | `name` + 1 trong: `review` / `aggregateRating` / `offers` |
| GTV completeness benchmark (4-field) | `aggregateRating`, `review`, `offers` (kèm `price`), `offers.availability` |
| Recommended | `image` array nhiều ảnh (Google chọn theo SERP layout), `sku`, `gtin`/`mpn`, `brand` → `#organization`, `description`, `hasCertification` (merchant listings — Google thêm 10/2024, thay EnergyConsumptionDetails từ 04/2025) |

HTML đi kèm (tham chiếu, không phải việc của skill này): `<article itemscope itemtype="https://schema.org/Product">` — xem `semantic-html-optimization`.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Tên sản phẩm khớp H1",
  "image": [
    "https://example.com/p/sp-1x1.jpg",
    "https://example.com/p/sp-4x3.jpg",
    "https://example.com/p/sp-16x9.jpg"
  ],
  "description": "Khớp mô tả hiển thị.",
  "sku": "SKU-001",
  "brand": { "@id": "https://example.com/#organization" },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.7,
    "reviewCount": 132
  },
  "review": [
    {
      "@type": "Review",
      "author": { "@type": "Person", "name": "Tên reviewer thật" },
      "datePublished": "2026-06-20",
      "reviewRating": { "@type": "Rating", "ratingValue": 5 },
      "reviewBody": "Trích review hiển thị trên page."
    }
  ],
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/san-pham/",
    "priceCurrency": "VND",
    "price": 1250000,
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2026-12-31"
  }
}
</script>
```

---

## 6. ItemList (PCP / Best List)

**PCP** ([[Product Category Page]]): ItemList = tín hiệu summary page / entity understanding cho danh mục — KHÔNG phải carousel play. Carousel rich result chỉ áp dụng khi ItemList kèm Recipe/Course/Restaurant/Movie (gallery Google); Product không nằm trong danh sách đó. SERP rendering của từng product card (giá, rating — chiếm vertical space, thống trị back-scroll khi SERP có AIO) đến từ **Product/merchant-listing markup per card**, mỗi card trên page = `<article>` + Product schema. ⚠️ Wiki [[Product Category Page]] ghi "ItemList schema → Google render product carousel" — claim cần verify lại với gallery, đã note lint.

**Best List** ([[Best List Page]]): Article + ItemList + `dateModified` THẬT. Điều kiện dùng: cadence refresh ≥1 lần/quý (79,1% cited lists update trong năm). Không có quy trình refresh → không markup `dateModified` cho có. (Spec này là suy luận hợp lý — chưa có nguồn GTV/Koray riêng, flag khi dùng.)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Tên danh mục / danh sách khớp H1",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "url": "https://example.com/san-pham-1/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "url": "https://example.com/san-pham-2/"
    }
  ]
}
</script>
```

PCP full-detail variant: mỗi `ListItem.item` = Product block (name, image, offers) khi card hiển thị đủ giá + availability. Best List: xuất kèm block Article (mục 4) trên cùng page, `dateModified` = lần refresh thật gần nhất.

---

## 7. Service

**Vị trí:** Service Landing Page ([[Service Landing Page]]) — 1 Service block per offering, mỗi offering nằm trong `<article>` riêng trên HTML. ❌ Không có rich result riêng → validate bằng validator.schema.org, đừng tìm nó trong Rich Results Test.

| Nhóm | Fields |
|---|---|
| Required | `name`, `provider` → `#organization`, `serviceType` |
| Recommended | `areaServed`, `description`, `hasOfferCatalog` (gói/pricing tiers nếu hiển thị), `url` |

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Dịch vụ SEO tổng thể",
  "serviceType": "SEO Agency Service",
  "url": "https://example.com/dich-vu-seo/",
  "description": "Khớp mô tả offering hiển thị.",
  "provider": { "@id": "https://example.com/#organization" },
  "areaServed": { "@type": "Country", "name": "Vietnam" },
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Gói dịch vụ",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": { "@type": "Service", "name": "Gói Growth" }
      }
    ]
  }
}
</script>
```

Case study section trên Service page → Article/Report (mục 4), KHÔNG "CaseStudy".

---

## 8. Breadcrumb

**Vị trí:** mọi page type có hierarchy. Khớp breadcrumb hiển thị trên page.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Trang chủ", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Danh mục", "item": "https://example.com/danh-muc/" },
    { "@type": "ListItem", "position": 3, "name": "Trang hiện tại" }
  ]
}
</script>
```

Item cuối (trang hiện tại) không cần `item` URL.

---

## Phụ lục A — Deprecated / không dùng

Nguồn verify: Google Search Central changelog — https://developers.google.com/search/updates (FAQ chấm dứt 07/05/2026, HowTo 09/2023, Certification 10/2024) + gallery — https://developers.google.com/search/docs/appearance/structured-data/search-gallery.

| Type | Trạng thái | Hành xử của skill |
|---|---|---|
| **FAQPage** | Rich result **chấm dứt hoàn toàn 07/05/2026** (trước đó từ 08/2023 chỉ còn government/health). Rich Results Test gỡ FAQ support 06/2026; Search Console API gỡ FAQ 08/2026. Markup để lại không gây hại nhưng không còn bất kỳ rich result nào. | User yêu cầu → xuất kèm cảnh báo bắt buộc: "Không còn rich result; giá trị machine-readability là unproven — cân nhắc bỏ." Không đề xuất chủ động. |
| **HowTo** | Rich result bị bỏ hoàn toàn từ 09/2023. Guideline nội bộ How-To Page (12/2025) ghi "Use HowTo JSON-LD" — LỖI THỜI, skill override. | Giữ phần HTML semantic của guideline (`<ol>` + `<time datetime>`); HowTo JSON-LD hạ xuống optional/no-rich-result, mặc định không xuất. |
| **CaseStudy** | KHÔNG tồn tại trong schema.org — chưa bao giờ là type hợp lệ. | Thay bằng Article hoặc Report. Note lint cho Service Landing Page.md. |
| **Speakable** | Còn trong gallery nhưng **chỉ news** (beta). | Không dùng cho client agency/e-commerce/service thông thường. |
| VideoObject / Event / JobPosting / Recipe | Còn hỗ trợ nhưng ngoài scope v1 (chưa có page-type framework nội bộ tương ứng). | Cần thì tra Google Search Central trực tiếp, không improvise. |

## Phụ lục B — Validate workflow

1. **Rich Results Test** — https://search.google.com/test/rich-results
   - Dùng cho: Article, Product, LocalBusiness, ProfilePage, Breadcrumb, ItemList/carousel, Organization.
   - Kiểm tra: eligibility rich result Google + lỗi required fields.
   - ⚠️ Từ 06/2026 tool này KHÔNG còn test FAQ — không phải bug.
2. **Schema Markup Validator** — https://validator.schema.org
   - Dùng cho: types không có rich result (Service, Person standalone, sameAs graph) + kiểm tra cú pháp schema.org thuần + kiểm tra `@id` references resolve đúng.
3. **Sau deploy:**
   - GSC → Enhancements: theo dõi impressions/errors per feature.
   - Kiểm tra render: URL Inspection → rendered HTML có chứa block JSON-LD (đặc biệt khi inject bằng JS — khuyến nghị chuyển server-side).
   - Không build tooling đọc FAQ report qua Search Console API (gỡ 08/2026).
4. **DIY test hiệu quả với AI visibility** (khi client hỏi): 5-10 treated pages có citation baseline + 5-10 controls tương đương → chỉ thêm schema → so sánh sau 30+ ngày. Kỳ vọng đúng theo DiD Ahrefs 05/2026: không tăng AI citations; theo dõi rich results/CTR thay vì citation.
