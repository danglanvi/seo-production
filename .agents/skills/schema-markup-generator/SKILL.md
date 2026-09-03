---
name: schema-markup-generator
description: "Sinh JSON-LD structured data hoàn chỉnh theo page type (Organization, LocalBusiness, Person/Author, Article, Product, ItemList, Service, Breadcrumb) + thiết kế Entity Home (About page schema, sameAs Wikipedia/Wikidata/socials, NAP) + Author entity (Person + ProfilePage) — layer G."
metadata:
  version: "1.0.1"
---

# Schema Markup Generator — JSON-LD theo page type + Entity Home + Author entity

Sinh khối JSON-LD dán được cho từng page type, thiết kế Entity Home schema (Organization/Person + sameAs + NAP) và Author entity (Person + ProfilePage), nối tất cả thành 1 entity graph qua `@id`. Đứng SAU content và HTML đã có (downstream của `semantic-content-writing` + `semantic-html-optimization`); output của skill này là input cho developer/CMS deploy.

> 🔴 **Giới hạn phải nói rõ với mọi client ngay từ đầu:** bằng chứng causal DiD 1.885 trang (Ahrefs 05/2026) cho thấy thêm JSON-LD **KHÔNG tăng AI citations** (AI Mode +2,4%, ChatGPT +2,2% — không phân biệt được với 0; AIO −4,6% — significant nhưng nhỏ, không quy được cho schema). Schema là lever cho: **rich results / SERP rendering** (second impression khi SERP có AIO), **entity recognition / Knowledge Graph** (Organization/Person + sameAs), **voice** (Speakable — chỉ news), và **Bing/Copilot understanding** (tầng index). Không hơn. Nguồn: [[sources/schema-ai-citations-did-ahrefs]].

## Phân vai

| Việc | Skill |
|---|---|
| Generate JSON-LD theo page type + Entity Home design + Author entity + validate workflow | ✅ Skill này |
| HTML semantic container (`<main>/<article>/<section>`, heading hierarchy, element weights) | `semantic-html-optimization` — schema **mô tả** entity, HTML **cấu trúc** content; skill này xuất block JSON-LD độc lập, không rewrite HTML |
| Nội dung E-A-V trong body text (definitive answers, writing rules) | `semantic-content-writing` / `-ca` — skill này chỉ ĐỌC content để map triples vào JSON-LD, không viết/sửa text |
| Audit onpage tổng (OP1-OP55) | `seo-onpage` — schema chỉ là 1 mục trong audit đó; skill này generate + validate, không chấm điểm page |
| Entity strategy off-site (Wikipedia creation, social activity, GBP ops) | [[Brand Entitization Playbook]] (wiki synthesis) — skill này chỉ xuất checklist + sameAs slots |
| ImageObject bulk / media schema chi tiết | `image-seo-optimize` — skill này chỉ nhúng image array trong Product/Article |

## Input

**Required:**
- `$PAGE_TYPE` — 1 trong 8 type v1: Organization (Entity Home/homepage), LocalBusiness, Person/Author (+ ProfilePage), Article/BlogPosting, Product (PDP), ItemList (PCP/Best List), Service, Breadcrumb. Nếu user mô tả page mà không nêu type → suy từ page-type framework (PDP/PCP/Service Landing/Best List) rồi confirm ở Bước 0.
- `$CONTENT` — nội dung THẬT của page (schema phải khớp visible content 1:1 — xem Gate #2).

**Optional:**
- `$URL` — URL page live (để scrape visible content + kiểm tra schema hiện có).
- `$ENTITY_INFO` — thông tin Central Entity: tên chính thức, legalName, NAP, social profiles, Wikipedia/Wikidata (nếu có), logo URL, author list.
- `$DOMAIN` — để sinh `@id` convention (`{domain}/#organization`).

**Path detection ($CONTENT):**
- **Path A (ưu tiên):** `$URL` → scrape bằng web fetch hoặc Firecrawl → lấy visible content + JSON-LD hiện có trong `<head>/<body>`.
- **Path B:** user đưa file HTML/markdown local → đọc trực tiếp. ⚠️ File local là clip/tóm tắt (không phải HTML live) → output BẮT BUỘC thêm dòng "đối chiếu live page trước deploy" ở mục 6 — Gate #2 đòi schema khớp visible content live 1:1.
- **Path C (đường lùi cuối, không cần MCP):** user paste nội dung page + mô tả các block hiển thị (rating có hiển thị không? review có thật không? giá bao nhiêu?). Skill luôn chạy được với Path C.

## Workflow

### Bước 0 — Scope gate + eligibility check (BẮT BUỘC, chờ xác nhận)

1. Confirm `$PAGE_TYPE` + entity đích (Organization hay Person? brand nào?) + scope: chỉ 1 page, hay full Entity Home design (nhiều block + checklist)?
2. **Rich-result eligibility check** — đối chiếu type với gallery Google hiện hành (25 features, cập nhật 06/2026 — bảng đầy đủ ở [references/jsonld-templates.md](references/jsonld-templates.md)):
   - ✅ Còn rich result: Article, Breadcrumb, Product, Organization, LocalBusiness, ProfilePage, ItemList (carousel — chỉ kèm Recipe/Course/Restaurant/Movie), Review snippet…
   - ❌ **FAQ: rich result CHẤM DỨT HOÀN TOÀN 07/05/2026** (kể cả government/health; Rich Results Test đã gỡ FAQ support 06/2026, Search Console API gỡ 08/2026).
   - ❌ **HowTo: deprecated từ 09/2023.**
   - 🔴 User yêu cầu FAQPage/HowTo → KHÔNG từ chối, nhưng xuất kèm cảnh báo bắt buộc: "Không còn bất kỳ rich result nào; giá trị machine-readability còn lại là **unproven** — khuyến nghị cân nhắc bỏ." Ghi đè 2 guideline nội bộ lỗi thời: [[How-To Page]] còn ghi "Use HowTo JSON-LD" (12/2025) và Open Question FAQ trong [[Structured Data]].
3. Nếu cần scrape/search (Path A, Wikipedia Verify) → báo số call dự kiến, chờ user xác nhận rồi mới chạy.

### Bước 1 — Thu thập visible content

Theo Path A/B/C. Trích các dữ kiện được phép markup: headline, author byline, ngày publish/modified thật, giá, availability, rating/review **có hiển thị trên page**, NAP, danh sách items. Dữ kiện không hiển thị → KHÔNG vào schema (Gate #2). Nếu page đã có JSON-LD → diff với content, flag mismatch.

### Bước 2 — Entity verification (khi output có Organization/Person)

1. **Wikipedia Verify** (SOP v1 Bước 3, [[Central Entity]]): search `"[Central Entity] Wikipedia"` — có trang riêng → high probability entity đã trong Knowledge Graph → được đưa Wikipedia URL + Wikidata QID vào sameAs.
2. Không có trang Wikipedia/Wikidata thật → **KHÔNG bịa** URI/QID; sameAs chỉ gồm social profiles chính thức đã verify với user. Bịa QID = phá entity reconciliation.
2b. **Chạy offline / không có web search** → bỏ qua Wikipedia Verify, KHÔNG đưa URL chưa verify vào block; toàn bộ sameAs slots ghi vào mục 6 output dạng "Pending — verify trước deploy".
3. Thu sameAs slots: Wikipedia, Wikidata (`https://www.wikidata.org/wiki/Qxxx`), LinkedIn, X, Facebook, YouTube, GBP URL (LocalBusiness), Google Scholar (author). Google đọc social links trong Organization schema → feed Knowledge Panel ([[Brand Entitization Playbook]]).

### Bước 3 — Map E-A-V triples → chọn template

- Từ `$CONTENT` + `$ENTITY_INFO`, liệt kê triples Entity-Attribute-Value cần củng cố (Google KG lưu entity dạng triples — [[E-A-V Framework]]); mỗi property JSON-LD = 1 triple.
- Lấy template đúng type từ [references/jsonld-templates.md](references/jsonld-templates.md) — required/recommended fields per type. Ngưỡng cứng theo page-type framework GTV:
  - **PDP:** Product đủ **4 field: aggregateRating + review + offers + availability** = `GTV completeness benchmark`, KHÔNG phải Google required (làm rõ 2026-07-13 — LINT-2026-009: Product **snippet** required = `name` + 1 trong review/aggregateRating/offers; `availability` chỉ là recommended trong Offer; **Merchant listing** có bộ requirements riêng — không trộn 2 eligibility sets); thiếu field = ít nguyên liệu render hơn competitor, không phải fail eligibility. KHÔNG bịa review/rating để đủ 4. Image array nhiều ảnh; Certification nếu áp dụng (Google thêm 10/2024, thay EnergyConsumptionDetails từ 04/2025). Source: developers.google.com/search/docs/appearance/structured-data/product-snippet
  - **PCP:** ItemList (tín hiệu summary page/entity understanding) + Product markup per card — rendering product card đến từ merchant listing per card, KHÔNG phải ItemList carousel (carousel chỉ áp dụng Recipe/Course/Restaurant/Movie) ([[Product Category Page]] — claim carousel trong wiki cần lint).
  - **Best List:** Article + ItemList + `dateModified` THẬT — chỉ hợp lệ nếu quy trình refresh ≥1 lần/quý tồn tại ([[Best List Page]]).
  - **Service Landing:** 1 Service block per offering, provider→`#organization` ([[Service Landing Page]]). ⚠️ "CaseStudy" KHÔNG tồn tại trong schema.org — case study dùng Article/Report.
  - **Author bio page:** ProfilePage + mainEntity: Person ([[Authorship]] — Article schema + named author + sameAs → author entity resolve được cross-site).
- Type/property lạ → check schema.org trước khi xuất, không phát minh type.

### Bước 4 — Generate JSON-LD với @id graph

- Format: JSON-LD trong `<script type="application/ld+json">` (format Google khuyến nghị; đặt `<head>` hoặc `<body>`, ưu tiên server-side render).
- 🔴 **1 entity = 1 `@id`:** `{domain}/#organization` cho Organization, `{author-url}/#person` cho mỗi author. Mọi block khác (Article.publisher, Article.author, Service.provider, Product.brand) **reference** node qua `@id` — không nhân bản Organization đầy đủ mỗi trang.
- 🔴 **Vị trí khối Organization đầy đủ = Entity Home** (thường là About page cho Organization — [references/entity-home-checklist.md](references/entity-home-checklist.md) mục 1; site chưa có Entity Home riêng → dùng homepage). Mọi trang khác — **kể cả homepage khi Entity Home là About page** — chỉ reference `{domain}/#organization`. Nội dung khối: logo, legalName, address, contactPoint, business identifiers (iso6523Code, naics, vatID, taxID…), sameAs array.
- Điền 100% giá trị từ visible content đã thu ở Bước 1; field thiếu data thật → bỏ field, không điền placeholder giả. Riêng field **Required** thiếu data đã-verify (vd logo/sameAs khi chạy offline): vẫn xuất block hợp lệ, liệt kê field vào bảng **"Pending slots"** ở mục 6 của output kèm cách verify — không bỏ im lặng.

### Bước 5 — Validate instructions

Xuất kèm 2-tool workflow (chi tiết Phụ lục B của references):
1. **Rich Results Test** (search.google.com/test/rich-results) — cho types còn rich result (eligibility).
2. **Schema Markup Validator** (validator.schema.org) — cho types không có rich result (Organization sameAs graph, Service, Person) + kiểm tra cú pháp thuần.
3. Sau deploy: theo dõi GSC Enhancements. ⚠️ Không build tooling đọc FAQ report — Search Console API gỡ FAQ 08/2026.

### Bước 6 — Entity Home checklist (chỉ khi scope là Entity Home / Author entity)

Chạy [references/entity-home-checklist.md](references/entity-home-checklist.md) (bám `sop/04-entity-optimization.md` + [[Brand Entitization Playbook]]): Entity Home canonical, schema đúng type Central Entity, sameAs verify, NAP consistent, E-A-V coverage trên page, @id graph, off-site corroboration. Frame kỳ vọng: **Knowledge Panel 3-6 tháng**, phụ thuộc corroboration off-site — schema chỉ là 1 trong các feeds vào KG ([[Knowledge Graph]]: Entity Home, Wikipedia, Wikidata, structured data, SERP consensus).

## Output

File: tài liệu nội bộ «<project>_Schema-JSONLD_v1» (ngoài repo, hỏi Lead/Vincent) (tăng `_v2` nếu trùng). Task wiki nội bộ → trả trực tiếp trong chat.

```markdown
# Schema Markup — <page/entity> (<PAGE_TYPE>)
Ngày: YYYY-MM-DD | Domain: <domain> | Scope: <1 page | Entity Home | Author entity>

## 0. Giới hạn hiệu quả (bắt buộc — không cắt khi gửi client)
Schema KHÔNG tăng AI citations (DiD 1.885 trang, Ahrefs 05/2026: AI Mode +2,4%, ChatGPT +2,2% — không phân biệt được với 0; AIO −4,6% — significant nhưng nhỏ, không quy được cho schema).
Giá trị thật: rich results/SERP rendering, entity understanding (KG), voice, Bing/Copilot understanding.
Rich result eligibility của type này: <✅ còn / ❌ deprecated + cảnh báo>

## 1. Khối JSON-LD (dán vào <head> hoặc <body>)
​```html
<script type="application/ld+json">
{ ... }
</script>
​```

## 2. Mapping schema ↔ visible content
| Property | Giá trị | Vị trí trên page (bằng chứng hiển thị) |
|---|---|---|

## 3. @id graph
- <node>#organization ← referenced by: <blocks>
- <node>#person ← referenced by: <blocks>

## 4. Validate
- [ ] Rich Results Test: <URL test> — expect: <feature>
- [ ] Schema Markup Validator: <types không rich result>
- [ ] GSC Enhancements sau deploy

## 5. Entity Home checklist (nếu scope Entity Home — theo references/entity-home-checklist.md)
- [ ] ...

## 6. Không làm / cần quyết định
- <field bỏ vì không có visible content | sameAs chưa verify | FAQ/HowTo warning nếu có>
```

## Behavior Gates

1. **Think Before** — Bước 0 là gate cứng: chưa confirm page type + scope + eligibility thì chưa generate. Nhiều entity (GTV client nào? Person hay Organization?) → hỏi, không tự chọn.
2. **Evidence** — mọi con số/claim truy được về nguồn + ngày: DiD Ahrefs 05/2026 ([[sources/schema-ai-citations-did-ahrefs]]); FAQ deprecated 07/05/2026, HowTo 09/2023 (Google Search Central changelog: https://developers.google.com/search/updates; gallery 25 features: https://developers.google.com/search/docs/appearance/structured-data/search-gallery); ρ≈0,03 Suski 1M SERPs ([[Structured Data]]); Knowledge Panel 3-6 tháng (`sop/04-entity-optimization.md`). Correlation "cited pages có schema 3x (53%)" là **confound** — không dùng làm luận cứ bán schema. Mọi giá trị trong JSON-LD truy được về visible content (bảng mapping mục 2 của output là bắt buộc).
3. **Surgical** — chỉ xuất block JSON-LD + hướng dẫn; không rewrite HTML, không sửa content, không tự chạy off-site tactic. Phát hiện lỗi wiki liên quan (CaseStudy trong [[Service Landing Page]], HowTo trong [[How-To Page]], "ItemList → product carousel" trong [[Product Category Page]]) → note 1 câu cho lint, không tự sửa wiki giữa task.
4. **Goal-driven** — mục tiêu là entity understanding + rich results đúng kỳ vọng, không phải "càng nhiều schema càng tốt". Client muốn bằng chứng schema có tác dụng với AI visibility → đề xuất DIY test protocol: 5-10 treated pages có citation baseline + 5-10 controls tương đương, chỉ thêm schema, so sánh sau 30+ ngày ([[sources/schema-ai-citations-did-ahrefs]]).

## Anti-patterns

- ❌ Claim "schema tăng khả năng được AI trích dẫn" / "GEO boost" trong bất kỳ output nào cho client — bị cấm tuyệt đối bởi Gate #2 + evidence DiD.
- ❌ Claim chiều ngược lại "schema vô dụng với AI" cho page invisible — study chỉ đo pages ĐÃ visible; page mới có lọt retrieval pool nhờ schema không là câu hỏi mở, không claim theo cả 2 hướng.
- ❌ Markup rating/review/giá không hiển thị trên page (spam policy risk — schema khớp visible content 1:1).
- ❌ Sinh FAQPage/HowTo như rich-result play; làm theo guideline nội bộ lỗi thời mà không cảnh báo.
- ❌ Bịa Wikipedia URL / Wikidata QID cho sameAs khi chưa chạy Wikipedia Verify.
- ❌ Hứa Knowledge Panel như deliverable chắc chắn hoặc trước 3-6 tháng.
- ❌ Dùng type không tồn tại (CaseStudy) hoặc property chưa check với schema.org.
- ❌ Nhân bản block Organization đầy đủ trên mọi trang thay vì reference `@id` — tạo duplicate entity nodes.
- ❌ Tự đề xuất tự-submit Wikidata item cho brand nhỏ — chưa có SOP nội bộ về notability risk, cần Vincent duyệt trước.

## References & wiki

- [references/jsonld-templates.md](references/jsonld-templates.md) — template JSON-LD đầy đủ 8 page types + bảng required/recommended + phụ lục deprecated + validate workflow.
- [references/entity-home-checklist.md](references/entity-home-checklist.md) — checklist Entity Home + Author entity + off-site corroboration + verification.
- SOP: `sop/04-entity-optimization.md` (on-site/off-site entity checklist, Knowledge Panel timeline).
- Wiki: [[Structured Data]] · [[sources/schema-ai-citations-did-ahrefs]] · [[Entity Home]] · [[E-A-V Framework]] · [[Central Entity]] · [[Knowledge Graph]] · [[Brand Entitization Playbook]] · [[Authorship]] · [[Algorithmic Authorship]] · [[Product Detail Page]] · [[Product Category Page]] · [[Best List Page]] · [[Service Landing Page]] · [[How-To Page]]

## Changelog

- **v1.0.1 (2026-07-07):** vá theo spot-run Entity Home GTV — chốt luật vị trí (major): khối Organization đầy đủ khai tại Entity Home (About page nếu có, homepage nếu không), homepage chỉ reference `@id` — đồng bộ SKILL.md + jsonld-templates + entity-home-checklist; thêm hành xử Required-field thiếu data verified (bảng Pending slots, không bỏ im lặng); nhánh offline cho Wikipedia Verify (sameAs pending); cảnh báo Path B file clip cũ (bắt buộc dòng đối chiếu live trước deploy); note founder inline Person khi chưa có bio page.
- **v1.0 (2026-07-07):** khởi tạo — nền: DiD study Ahrefs 05/2026 (schema ✗ AI-citation lever), Google Search Central gallery 06/2026 (25 features; FAQ chấm dứt 05/2026, HowTo 2023), sop/04-entity-optimization, page-type frameworks GTV (PDP 4-field, PCP ItemList, Service per-offering), Entity Home (Jason Barnard) + E-A-V + Brand Entitization Playbook; 8 page types v1, @id graph convention.
