# Redirect Mapping Method — 1-1 theo relevance, at scale

Phương pháp lập redirect map cho migration. Dùng ở bước PRE 1.4 của [migration-checklist-full.md](migration-checklist-full.md#14-redirect-mapping).

## Nguyên tắc

1. **Map 1-1 theo relevance** — mỗi URL cũ → đúng 1 URL mới tương đương nhất về nội dung/intent. ❌ Cấm bulk redirect về homepage hoặc trang không liên quan — Google coi như soft-404 (Google site-move doc; Siteimprove).
2. **Cơ chế signal:** 301 "transfer canonical effect + PageRank, remove from index" (Ranking Signal Consolidation wiki) — map đúng relevance thì signal truyền trọn; map sai thì signal loãng hoặc mất.
3. **Pages không giá trị → 410, KHÔNG redirect.** Pages zero-CTR / zero organic keywords nhiều tháng không được map 1-1 sang site mới — đừng chở index pollution qua nhà mới (Index Pollution wiki; 4 methods trong Ranking Signal Consolidation).
4. **Loại redirect:** 301/308 server-side. 302/307 phải convert (Status Codes wiki — Koray case >1.500 redirects convert).

## Priority tiers (thứ tự làm map)

| Tier | Tiêu chí | Cách xử lý |
|---|---|---|
| 1 | Pages có **organic traffic** (GSC/GA benchmark) | Map thủ công hoặc auto + 🔴 human review 100% |
| 2 | Pages có **backlinks** (Ahrefs pages-by-backlinks) — kể cả không còn traffic | Map thủ công; check cả backlinks trỏ về pages chưa có trong map (Aleyda) |
| 3 | Pages có **conversions** (GA/CRM) | Map thủ công |
| 4 | Còn lại (status 200, indexable) | Auto-match theo method dưới; sample review |
| — | Zero-value (zero-CTR nhiều tháng) | 410 / noindex — KHÔNG map |

## Method theo scale

| Scale | Method | Ghi chú |
|---|---|---|
| **< 500 URLs** | Manual map trên sheet | Nhanh hơn setup tool; dùng template cột dưới |
| **500 – 10k URLs** | Screaming Frog **Near Duplicates** ở list mode | Config: disable "Only Check Indexable Pages", refine Content Area; upload URL cũ + mới cùng lúc → chạy Crawl Analysis → export "Bulk Export > Content > Near Duplicates" → match theo similarity (SF migration tutorial) |
| **> 10k URLs** | Screaming Frog **vector embeddings** (semantic similarity) | Có filter rules theo URL pattern — vd chỉ match staging URLs với live pages (SF tutorial: how-to-use-vector-embeddings-for-redirect-mapping) |

🔴 **Mọi auto-match (Near Duplicates lẫn embeddings) phải human-review toàn bộ Tier 1-2** (traffic + backlinks) trước khi deploy. Tier 4 review theo sample.

## QA redirect map trước launch

Chạy toàn bộ map qua SF list mode ("Always Follow Redirects") trên staging/rule preview:

- [ ] **No chain** — flatten về 1 hop (chain mất PageRank + crawl budget; Googlebot follow tối đa 10 hops, Google khuyến nghị ≤3 hops — Google Search Central redirects doc: developers.google.com/search/docs/crawling-indexing/301-redirects; chuẩn nội bộ = 1 hop).
- [ ] **No loop.**
- [ ] **Target trả 200** — không redirect vào 404/410/301 tiếp.
- [ ] **Target indexable** — không noindex, không robots block, canonical self-referencing.
- [ ] **No homepage-dump** — grep map: số dòng có target = homepage phải giải trình được từng dòng.
- [ ] Mọi URL cũ có backlink đều có mặt trong map (đối chiếu Ahrefs export).

## Template sheet

| Cột | Nội dung |
|---|---|
| `old_url` | URL cũ (từ crawl Internal tab + GSC + GA + sitemap — gồm cả orphans) |
| `traffic` | Clicks/sessions 3-12 tháng (nguồn + ngày snapshot) |
| `backlinks` | Referring domains / backlinks count (Ahrefs, ngày snapshot) |
| `new_url` | URL đích trên site mới |
| `match_confidence` | manual / near-dup % / embedding score |
| `reviewed` | yes/no — 🔴 Tier 1-2 phải yes 100% trước launch |
| `status_code` | 301 / 410 (quyết định per-page) |

Naming file: `<project>_Redirect-Map_v1.xlsx` — tăng version khi map đổi sau QA.
