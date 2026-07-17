---
name: technical-seo-audit
description: "Audit technical SEO tầng SITE theo bộ audit nội bộ GTV/TAG (template xlsx audit toàn diện 3.2025 + docx giải thích The AI Growth): crawl & log file, index coverage, redirect & canonical, sitemap & robots.txt, Core Web Vitals & site speed, JS rendering, HTTPS & mobile — DIAGNOSTIC layer, wrap tools/seo-audit-tool và Ahrefs Site Audit MCP, output báo cáo checklist-status kèm priority fix. Use when: (1) 'audit technical [domain]', 'kiểm tra technical SEO [site]'; (2) 'site không được index / crawl chậm / redirect loạn / index bloat'; (3) 'check Core Web Vitals / crawl budget cho [domain]'. Data priority: Ahrefs/Semrush site-audit MCP (khi có project sẵn) hoặc Screaming Frog CLI headless tự chạy full-crawl + seo-audit-tool --deep → SF export tay → checklist manual chỉ-có-URL; kèm AI-crawler readiness (robots per-bot, log AI hits, TTFB AI gate). KHÔNG dùng cho: onpage semantic per-page (→ seo-onpage), viết schema/JSON-LD (→ schema-markup-generator), sửa HTML semantic structure (→ semantic-html-optimization), backlink audit (→ backlink-research)."
metadata:
  version: "1.2"
---

# Technical SEO Audit

Audit technical SEO **tầng SITE** — chẩn đoán những gì cản Google crawl, render, index và phục vụ site: crawl diagnostics, index coverage, redirect chains, canonical, robots/sitemap, Core Web Vitals, JS rendering.

🔴 **GROUND TRUTH SỐ 1** = bộ audit nội bộ (template xlsx audit toàn diện 3.2025 — 22 sheet + docx giải thích của The AI Growth — 19 sections; đã ingest vào wiki 07/2026: [[sources/seo-audit-template-toan-dien-2025-gtv]] + [[sources/giai-thich-seo-audit-toan-dien-tag]], file gốc ở `raw/_ingested/`). Khung xương checklist đã được convert vào [references/audit-checklist-by-area.md](references/audit-checklist-by-area.md); wiki + web chỉ bổ sung/cập nhật chỗ template thiếu hoặc lỗi thời.

**Upstream:** `tools/seo-audit-tool` (URL-level, deterministic + CWV), Screaming Frog CLI headless (site-level crawl engine — Path B) và Ahrefs/Semrush Site Audit MCP cấp data — skill này WRAP, không chấm lại. **Downstream:** báo cáo fix list ưu tiên cho dev/SEO team; phần semantic/schema/backlink route sang skill anh em theo bảng dưới.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Onpage semantic (P0-P23, EAV, topical coverage, heading vector) | `/seo-onpage` (sop/08, P-series) | Skill này KHÔNG chấm nội dung; P21 Semantic HTML & T3-P3 CWV chồng lấn → skill này đo *site-level*, seo-onpage đo *page-level content* |
| Schema/JSON-LD (tạo + sửa markup) | `schema-markup-generator` | Skill này chỉ *flag* schema lỗi/thiếu (sheet Semantic Markup), không viết markup |
| Semantic HTML structure (6 Golden Rules, main/article) | `semantic-html-optimization` | Skill này chỉ đo HTML errors / DOM size / minify — không sửa cấu trúc semantic |
| Ảnh: filename/alt/caption/metadata | `image-seo-optimize` | Skill này chỉ flag ảnh >100KB / thiếu alt hàng loạt / thiếu image sitemap |
| Backlinks & disavow (sheet 4, 4.1, 19 của template) | `backlink-research` + `backlink-plan` | LOẠI hẳn khỏi scope skill này dù có trong template |
| Content audit (thin/duplicate/under-optimized — sheet 5, 5.1, 13) | `/seo-onpage` + semantic-content-audit | Skill này chỉ flag *index status* của trang thin (bloat), không đánh giá chất lượng content |
| Keyword cannibalization / Ranking Signal Dilution | `/seo-topical-map` (outline/topical layer) | Skill này chỉ cung cấp evidence (duplicate title, nhiều URL cùng query) |
| Audit bài viết đơn lẻ tự động | `tools/seo-audit-tool` | Skill này ở tầng SITE, wrap tool ở tầng URL |
| Site migration / dịch chuyển domain | `site-migration-checklist` | Skill này chỉ audit hiện trạng HTTPS/redirect, không dẫn migration |

## Input

**Required:**
- `$TARGET` — domain hoặc URL root cần audit (vd `https://example.vn`).

**Optional:**
- `$SITE_TYPE` — ecom / blog / news / SaaS / local. Ảnh hưởng ngưỡng file-type ratio, index bloat tolerance (Open Question tier-3 SOP — chưa có ngưỡng chốt theo site type, phải hỏi thay vì giả định).
- `$SCOPE` — mặc định full 7 khu vực; hoặc user chọn khu vực (vd chỉ "CWV + redirect").
- `$GSC_DATA` — export/screenshot GSC **Page indexing report** + **Crawl Stats** do user cung cấp.
- `$LOG_FILE` — server log hoặc export Screaming Frog Log File Analyser.
- `$CLIENT` — tên client/project để đặt tên file output.

**Path detection** (chi tiết ở [references/data-paths.md](references/data-paths.md)): project Ahrefs/Semrush có sẵn → Path A cho nhanh; cần crawl tươi/sâu toàn site → Path B; không có gì → Path C.

| Path | Điều kiện | Data |
|---|---|---|
| **Path A** | $TARGET có project sẵn trong Ahrefs Site Audit (hoặc Semrush — Path A-alt) + chạy được `tools/seo-audit-tool` | Ahrefs `site-audit-*` MCP (site-level) + seo-audit-tool `--deep` (CWV qua PageSpeed API, URL đại diện) — nhanh, không tốn crawl mới |
| **Path B (engine crawl chính)** | Máy có Screaming Frog + license active (verified v23.3, 07/2026) | Claude TỰ chạy SF `--headless` full-crawl (🔴 tốc độ mặc định 2 threads / 2–3 URL/s — shared hosting hay chặn crawler nhanh) → parse CSV. **B-file (ưu tiên khi có):** user đã crawl GUI → `--load-crawl` file + export, không đụng server. B-manual: user paste export |
| **Path C (đường lùi cuối)** | Chỉ có URL, không tool | Checklist manual: `curl -I`, /robots.txt, /sitemap.xml, view-source vs rendered DOM (hoặc Firecrawl MCP), PageSpeed Insights công khai, `site:` operator |

⚠️ Path C luôn chạy được — skill không bao giờ chết vì thiếu MCP, nhưng report phải ghi rõ độ phủ thấp hơn.

## Workflow

### Bước 0 — Scope gate & xác nhận

1. Xác nhận entity (client GTV nào / TAG / site nội bộ) — không mix.
2. Xác nhận `$TARGET`, `$SITE_TYPE`, `$SCOPE`. Thiếu `$SITE_TYPE` → hỏi (ảnh hưởng cách đọc file-type ratio và bloat tolerance).
3. 🔴 **Crawl budget gate**: site < ~10.000 trang unique → tuyên bố ngay "crawl budget không phải ưu tiên" (Google: crawl budget chỉ đáng lo với site ≥ ~10k–1M+ trang hoặc update rất thường xuyên — developers.google.com/crawling/docs/crawl-budget). Tập trung index hygiene thay vì khuyến nghị crawl budget nặng.
4. Nếu Path A: **báo số call dự kiến** (~3–6 Ahrefs MCP call: `site-audit-projects` ×1, `site-audit-issues` ×1, `site-audit-page-explorer` ×1–3 + 1 lần chạy seo-audit-tool trên 3–5 URL đại diện) → **chờ user xác nhận** rồi mới gọi.
5. Nếu Path B: **báo scope crawl** — 🔴 mặc định FULL site, KHÔNG giới hạn URL trừ khi user yêu cầu (quyết định Vincent 07/2026); kèm tốc độ crawl + ước tính thời gian + note server load → **chờ user xác nhận** rồi mới chạy. Site lớn → đề xuất database storage mode + chạy qua đêm theo 2 nhịp (data-paths.md).
6. Hỏi user có GSC access không (hoặc đã nối GSC vào SF — Path B kéo được URL Inspection data ngay trong crawl). Không có → khu vực Index Coverage sẽ đánh dấu ⬜ THIẾU DATA kèm hướng dẫn lấy report (không bịa — xem Gate #2).
7. Khi audit chạm item 4.13/1.17: hỏi **chiến lược AI crawler** của client (muốn AI citation → mở bot; muốn opt-out training → chặn là chủ đích) — không giả định.

### Bước 1 — Nạp khung ground truth

1. Đọc [references/audit-checklist-by-area.md](references/audit-checklist-by-area.md) — khung xương 7(+1) khu vực đã convert từ template nội bộ, mỗi item có tiêu chí ĐẠT + nguồn + priority.
2. Khu vực Speed/HTML/CWV: canonical = `sop/06-self-checklist/tier-3-technical-advance.md` (bản operational của sheet "2. Checklist technical advance", đã fix FID→INP, Server Push→preload) — cross-ref, KHÔNG viết lại.
3. 🔴 **Template drift**: item lỗi thời trong template (rel=next/prev, AMP, FID, mobile-friendly test tool, PageSpeed >80, trang ≤35KB, load >20s, GTMetrix <1,7s) → xử lý là "legacy — thay bằng X", KHÔNG lặp lại như tiêu chuẩn. Xem bảng ngưỡng bên dưới.

### Bước 2 — Thu data theo Path

- **Path A**: gọi MCP + chạy tool theo [references/data-paths.md](references/data-paths.md). 🔴 WRAP: check deterministic (meta lengths, heading tree, canonical, schema presence, links) đã nằm trong seo-audit-tool Layer 1; CWV lấy từ `--deep` (PageSpeed API); trang JS-heavy → thêm `--render` (Playwright). Skill chỉ **diễn giải output + xếp priority**, không tự chấm lại.
- **Path B**: chạy SF CLI headless theo data-paths.md — chạy nền + bọc `caffeinate -i` (chống máy sleep); trong lúc crawl làm các khu vực không cần crawl (curl, robots, sitemap, PSI, log). Crawl xong → 🔴 **completeness check** (đếm Status 0/Connection Timeout — cao thì mọi số đếm ghi caveat "cận dưới") → parse CSV bằng script (DuckDB/awk), phân loại vào khu vực. B-file: user có crawl sẵn → `--load-crawl` + export (không đụng server). B-manual: đưa user danh sách export (cột per khu vực trong data-paths.md) → nhận CSV/paste.
- **Path C**: chạy checklist manual per URL mẫu; ghi rõ giới hạn coverage trong report.
- Mọi data point ghi kèm **nguồn + ngày lấy** (vd "Ahrefs Site Audit crawl 2026-07-05", "GSC screenshot user cung cấp 2026-07-07").

### Bước 3 — Audit theo 7(+1) khu vực

Chạy checklist từng khu vực theo references/audit-checklist-by-area.md:

1. **Crawl & Log File** — 404/soft-404, 5xx/503, orphan URL, wasted budget, spam bots, AI crawler hits (GEO baseline), 3 checkpoint GSC Crawl Stats.
2. **Index Coverage** — GSC Page indexing taxonomy hiện hành, Index Pollution/Bloat playbook.
3. **Redirect & Canonical** — chain ≥2 hops, 302→301, 9 biến thể homepage, self-canonical, parameter URLs.
4. **Sitemap & Robots.txt** — 100% URL 200, ≤50.000 URL / ≤50MB, robots không thay noindex, không chặn CSS/JS, AI bot access chủ đích theo **bot-purpose matrix** (search/training/user-triggered — xem checklist 1.17): OAI-SearchBot·GPTBot·ChatGPT-User / Claude-SearchBot·ClaudeBot·Claude-User / PerplexityBot·Perplexity-User / Google-Extended (control token).
5. **Core Web Vitals & Site Speed** — LCP/INP/CLS 75th percentile, DOM, fonts, caching (canonical: tier-3 SOP mục 3–5).
6. **JS Rendering** — 3-phase Crawl→Render→Index, `<a href>`, SPA soft-404, raw vs rendered delta (đa số AI crawler được quan sát fetch raw HTML, không render JS như Googlebot — `observational`, vendor docs không cam kết; delta lớn = rủi ro vô hình với AI engines), SSR.
7. **HTTPS & Mobile** — http/https = 2 entity riêng, 12 items HTTPS, mobile parity.
8. *(chỉ khi site đa ngôn ngữ)* **International/hreflang** — tier-3 SOP mục 10 + 4 nguyên tắc [[syntheses/Multilingual SEO]]; nuance [[Hreflang PageRank Sharing]]: thiếu hreflang có thể là chủ đích khi alternates chưa đủ chất lượng — hỏi trước khi flag ❌.

Mỗi item chấm **checklist-status** (trung thành mô hình template — KHÔNG bịa thang điểm số):

| Status | Nghĩa |
|---|---|
| ✅ ĐẠT | Thỏa tiêu chí ĐẠT, có evidence |
| ⚠️ CẦN XEM | Gần ngưỡng / evidence chưa đủ kết luận |
| ❌ FAIL | Vi phạm tiêu chí, có evidence |
| ⬜ THIẾU DATA | Không có data (vd không có GSC) — ghi cách lấy |

### Bước 4 — Xếp priority fix

Xếp mọi ❌/⚠️ theo impact (tinh thần case "in ấn catalog" docx §3.0 — một dòng robots.txt giam cả bộ từ khóa ngoài top 100, gỡ ra → top 8 trong 3 ngày):

| Priority | Loại lỗi | Ví dụ |
|---|---|---|
| **P0 — chặn index** | robots chặn nhầm, noindex nhầm, canonical sai, 5xx, sitemap toàn URL lỗi | "Indexed, though blocked by robots.txt" ≠ 0 |
| **P1 — lãng phí crawl / bloat** | redirect chains, soft 404, index pollution, orphan, parameter URLs index | 404 vĩnh viễn chưa chuyển 410 |
| **P2 — CWV & speed** | LCP/INP/CLS poor, TTFB >800ms, DOM >1.500 nodes | INP >500ms mobile |
| **P3 — tối ưu nhỏ** | Brotli, preload, font, ảnh >100KB, minify | HTML chưa minify |

Mỗi fix ghi: lỗi → evidence (URL/số liệu + nguồn) → hành động cụ thể → người làm (dev/SEO/content).

### Bước 5 — Render report & trả file

- Render theo skeleton ở mục Output.
- Đặt tên: `<client>_Technical-SEO-Audit_v1.md` → `Deliverables/<project>/` (tăng `_v2` nếu trùng). Audit nội bộ GTV/TAG → hỏi user nơi trả nếu chưa rõ.
- Kết report: đề xuất re-audit sau khi fix P0/P1 (validate qua GSC + re-crawl).

## Bảng ngưỡng (whitelist — nguồn bắt buộc)

🔴 Con số KHÔNG có trong bảng này → không được phát biểu như chuẩn trong report.

| Ngưỡng | Giá trị | Nguồn |
|---|---|---|
| LCP / INP / CLS (75th %ile, tách mobile/desktop) | good ≤2,5s / ≤200ms / ≤0,1 · poor >4s / >500ms / >0,25 | https://web.dev/articles/vitals (INP thay FID chính thức 03/2024) |
| Redirect hops Googlebot theo được | ≤10; audit flag chain ≥2 hops, fix về 1 (A→C và B→C) | developers.google.com/crawling/docs/troubleshooting/http-status-codes; docx §17.1.6 |
| Sitemap | ≤50.000 URL / ≤50MB mỗi file; 100% URL 200 + self-canonical + không bị block | developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap; xlsx sheet1 A19-A28; tier-3 SOP mục 8. ⚠️ Template ghi 10MB = số cũ, dùng 50MB |
| GSC Avg response time | <200ms tốt / <350ms tối thiểu / >500ms cờ đỏ | tier-3-technical-advance.md mục 0+2.1 (ngưỡng GTV) |
| GSC By response | 200+304 ≥ ~95%; 4xx <1%; 5xx ~0% (304 cao là TỐT) | tier-3-technical-advance.md mục 2.2 |
| Time-to-index trang mới | 24–48h (authority site) | tier-3 mục 2.4; wiki [[Cost of Retrieval]] (Measurement Proxies) |
| TTFB | <200ms ideal / <800ms min | wiki [[Cost of Retrieval]] |
| DOM size | <1.500 nodes | xlsx sheet2 A30 (Google suggests); tier-3 mục 4.3 |
| HTML size | tham chiếu Koray ~15KB/trang (minified) | xlsx sheet2 A5; tier-3 mục 3.1 |
| Status code hygiene | 404 vĩnh viễn → 410; 302/307 tạm → 301 nếu permanent; bảo trì → 503 (không 500) | wiki [[Status Codes]] (Koray case); docx §1.5 (John Mueller) |
| Log file: URL ít crawl | <1,5 lần/ngày → review ưu tiên | xlsx sheet3 dòng 10 |
| Log file: crawl chậm | Average Response Time >3s → review | xlsx sheet3 dòng 13 |
| Log 404 hits | mục tiêu <50/tháng | wiki [[Status Codes]] (baseline case Koray >25.000) |
| Title/meta | Title >65 ký tự = flag (sheet15); title ~50-60 / meta description ~120-155 ký tự (mobile) | xlsx sheet15; wiki [[Meta Tags]] |
| Ảnh | Template flag >100KB; chuẩn P20 onpage (sop/08) là `.webp` <150KB — reconcile: **>150KB = ❌ FAIL, 100–150KB = ⚠️ CẦN XEM** | xlsx sheet1 A42, sheet12; docx §5.2; sop/08-onpage-checklist.md P20 |
| Crawl budget gate | site < ~10k trang unique → không ưu tiên crawl budget | developers.google.com/crawling/docs/crawl-budget |
| TTFB AI gate (GEO) | <2s hard timeout fetch ChatGPT / target <700ms — label bắt buộc: "reverse-engineered estimate, đơn nguồn" | wiki [[GEO]] (ChatGPT Pipeline Gate #2); thống nhất geo-content-optimization |
| Font files | >5 files = flag; >15 files = TTI impact rõ (HTTPArchive); chuẩn: Woff2 + preload font LCP + font-display | wiki [[Font File Optimization]] |
| ❌ Số legacy KHÔNG dùng | trang ≤35KB, load >20s, GTMetrix <1,7s, PageSpeed >80, FID, AMP, rel=next/prev, mobile-friendly test tool | xlsx sheet1/16 + docx §7 — thay bằng CWV hiện hành (web.dev) + note "legacy" |

## Output

```markdown
# Technical SEO Audit — <domain>
> Ngày audit: YYYY-MM-DD · Data: <Path A/B/C — nguồn + ngày crawl> · Site type: <type> · Scope: <7 khu vực / tùy chọn>

## 1. Executive Summary
- Tình trạng tổng quan (3-5 câu), số lỗi theo priority: P0: n · P1: n · P2: n · P3: n
- Top 3 việc phải làm ngay (P0)

## 2. Bảng tổng hợp theo khu vực
| Khu vực | ✅ | ⚠️ | ❌ | ⬜ | Lỗi nặng nhất |
|---|---|---|---|---|---|
| Crawl & Log File | | | | | |
| Index Coverage | | | | | |
| Redirect & Canonical | | | | | |
| Sitemap & Robots.txt | | | | | |
| CWV & Site Speed | | | | | |
| JS Rendering | | | | | |
| HTTPS & Mobile | | | | | |
| International/hreflang *(nếu áp dụng)* | | | | | |

## 3. Chi tiết theo khu vực
### 3.x <Tên khu vực>
| Check | Status | Evidence (URL/số liệu + nguồn + ngày) | Tiêu chí ĐẠT (nguồn ngưỡng) |
|---|---|---|---|
**Nhận định:** <2-4 câu diễn giải WHY — link concept wiki nếu liên quan>

## 4. Fix list ưu tiên
| # | Priority | Lỗi | Evidence | Hành động | Người làm |
|---|---|---|---|---|---|

## 5. Data còn thiếu
- <item ⬜ + hướng dẫn user lấy: GSC Page indexing export, Crawl Stats screenshot, server log…>

## 6. Nguồn & phạm vi
- Tool/data đã dùng + ngày · Khu vực loại khỏi scope (backlink, content quality, schema authoring — route skill anh em)
```

## Behavior Gates

**#1 Think Before** — Trước khi audit: entity nào? site type nào? crawl budget gate qua chưa? GSC có không? Path nào? chiến lược AI crawler? Thiếu thông tin quyết định output → hỏi, không giả định. Trước khi gọi MCP: báo số call, chờ xác nhận. Trước khi chạy SF crawl: báo scope (full mặc định) + thời lượng ước tính, chờ xác nhận — crawl chạm server thật của khách.

**#2 Evidence** — 🔴 Mọi con số trong report truy được về nguồn + ngày. Ngưỡng chỉ lấy từ Bảng ngưỡng whitelist. 🔴 **KHÔNG bịa trạng thái GSC**: chỉ báo cáo index coverage khi có data thật (user paste export/screenshot hoặc Ahrefs); không có → ⬜ THIẾU DATA + hướng dẫn lấy. Dùng đúng taxonomy **Page indexing report hiện hành** (Indexed / Not indexed + các lý do Not indexed theo danh sách hiện hành tại support.google.com/webmasters/answer/7440203 — đối chiếu doc Google khi chấm, danh sách có thể thay đổi), KHÔNG dùng tên trạng thái report cũ Valid/Warning/Error/Excluded.

**#3 Surgical** — Chỉ audit technical site-level. Không chấm content quality, không viết JSON-LD, không audit backlink, không sửa HTML semantic — flag + route theo bảng phân vai. Không tái mô tả check deterministic mà seo-audit-tool Layer 1 đã làm.

**#4 Goal-driven** — Deliverable = **fix list ưu tiên theo impact** (P0 chặn index > P1 crawl waste > P2 CWV > P3 tối ưu nhỏ), không phải bản liệt kê lỗi dàn trải. Mỗi finding trả lời "fix cái này thì site được gì" — nối về [[Cost of Retrieval]] (CoR là denominator của Topical Authority).

## Anti-patterns

- ❌ Bịa trạng thái GSC / index coverage khi không có data thật.
- ❌ Dùng taxonomy GSC cũ (Valid/Warning/Error/Excluded) — report Index Coverage đã bị thay bằng Page indexing.
- ❌ Lặp lại số legacy của template như chuẩn (≤35KB, >20s, GTMetrix 1,7s, PageSpeed >80, FID, AMP, rel=next/prev, mobile-friendly test).
- ❌ Coi 304 cao hoặc Image-heavy file-type là lỗi mặc định (tier-3 mục 0 — false positive kinh điển; 304 = tiết kiệm budget).
- ❌ Khuyên block duplicate bằng robots.txt khi mục tiêu là consolidation — SE không thấy duplicate để gộp signal; robots.txt = crawl control, noindex = index control (wiki [[Ranking Signal Consolidation]]; docx §3.6).
- ❌ Tự chấm lại các check deterministic seo-audit-tool Layer 1 đã chạy.
- ❌ Bịa thang điểm số — template dùng checklist-status, giữ nguyên mô hình.
- ❌ Khuyến nghị crawl budget nặng cho site < ~10k trang.
- ❌ Đưa ngưỡng theo site type (ecom vs blog) như chuẩn đã chốt — đang là Open Question, phải ghi rõ "chưa có ngưỡng GTV chốt".
- ❌ Audit backlink/content/schema rồi "tiện tay" đề xuất fix — route sang skill anh em.
- ❌ Kiểm tra/đề xuất llms.txt như audit item — không bot nào request nó (Google không dùng; GPTBot/ClaudeBot/PerplexityBot bỏ qua); kiểm soát AI crawler = robots.txt (wiki [[GEO]], thống nhất guardrail geo-content-optimization).
- ❌ Bán CWV như ranking lever chính — Google coi là tie-breaker (wiki [[Core Web Vitals]] Open Question, chưa có evidence độc lập); frame lợi ích theo [[Cost of Retrieval]].
- ❌ Flag "thiếu hreflang" thành lỗi mặc định khi alternates chưa đủ chất lượng — hreflang share signal 2 chiều, delay có thể là chủ đích ([[Hreflang PageRank Sharing]]).
- ❌ Kết luận số đếm (orphan, ảnh, duplicate) từ crawl không hoàn chỉnh mà không ghi caveat — check Status 0/Timeout % trước, số từ crawl thiếu là "cận dưới".
- ❌ Báo động số redirect gộp cả external share links (Zalo/X/FB intent) — lọc external trước khi đếm redirect nội bộ.
- ❌ Dùng TTFB lab (Lighthouse) đơn lẻ làm nguồn — lab thường thấp ảo; nguồn chuẩn = GSC avg response time + curl ×3–5.

## References & wiki

**References trong skill:**
- [references/audit-checklist-by-area.md](references/audit-checklist-by-area.md) — checklist chi tiết 7(+1) khu vực: check · cách kiểm · tiêu chí ĐẠT · nguồn · priority.
- [references/data-paths.md](references/data-paths.md) — map Path A (Ahrefs site-audit MCP + seo-audit-tool) / Path B (cột Screaming Frog) / Path C (manual chỉ-có-URL).

**Ground truth nội bộ:**
- [[sources/seo-audit-template-toan-dien-2025-gtv]] — source page của template 22 sheet (file gốc: `raw/_ingested/SEO Audit Template (audit toàn diện) - Update 3.2025.xlsx`).
- [[sources/giai-thich-seo-audit-toan-dien-tag]] — source page của docx giải thích 19 sections (file gốc: `raw/_ingested/Giải thích các phần trong SEO Audit Toàn diện - The AI Growth.docx`).
- `sop/06-self-checklist/tier-3-technical-advance.md` — canonical cho khu vực Speed/HTML/CWV (bản operational của sheet 2).
- `tools/seo-audit-tool/README.md` — spec CLI 3 lớp.

**Wiki Semantic SEO (lớp WHY):** [[Cost of Retrieval]] · [[Index Pollution]] · [[Status Codes]] · [[Robots.txt]] · [[Faceted Navigation]] · [[Index Partition]] · [[Meta Tags]] · [[Ranking Signal Consolidation]] · [[GEO]] · [[Core Web Vitals]] · [[Font File Optimization]] · [[Hreflang PageRank Sharing]] · [[HTML Normalization]] · [[syntheses/Multilingual SEO]]

**Google docs hiện hành:** web.dev/articles/vitals · support.google.com/webmasters/answer/7440203 · developers.google.com/crawling/docs/crawl-budget · developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics · developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

## Changelog

- **v1.3 (2026-07-13, P0 remediation LINT-2026-005):** (1) bỏ blanket claim "AI crawler không render JS" → re-label `observational` (vendor docs không cam kết) ở khu vực 6 + item 6.5; (2) thêm **bot-purpose matrix** search/training/user-triggered (OAI-SearchBot·GPTBot·ChatGPT-User / Claude-SearchBot·ClaudeBot·Claude-User / PerplexityBot·Perplexity-User / Google-Extended) theo crawler docs chính chủ; (3) fix 1.17: Google-Extended không có UA riêng trong log (chỉ là robots token, chặn không ảnh hưởng Google Search) + training-bot hits không phải AI-visibility KPI.
- **v1.2 (2026-07-10):** đúc kết từ lần chạy thật đầu tiên (chanlongpickleball.com): (1) Path B tốc độ mặc định 2 threads/2–3 URL/s + dấu hiệu server chặn giữa crawl + completeness check bắt buộc (Status 0/Timeout → caveat "cận dưới"); (2) Path **B-file** `--load-crawl` (user crawl GUI, Claude load + export không đụng server — bộ export names verified v23.3); (3) checklist mới: chữ ký PHP session giết cache ở 5.9 (PHPSESSID + Expires 1981 + no-store; nghi phạm YITH/Woo plugins), 404-pattern-theo-prefix = đổi URL structure không 301 ở 1.1, pagination canonical về trang 1 ở 3.6, đọc By Googlebot type + JS/CSS `?ver=` ở 1.6; (4) GSC Crawl Stats qua Google Sheets + gws (strip dòng keyring trước parse) + các phép phân tích chuẩn; (5) PSI có key trong `.agent-secrets/.env`, nuance site-không-CrUX chấm bằng lab ghi rõ nguồn; (6) `tools/gsc/gsc.sh` = Path A+ (pending OAuth consent); (7) anti-patterns mới: số đếm từ crawl thiếu, redirect gộp share links, TTFB lab đơn lẻ.
- **v1.1 (2026-07-10):** (1) lớp AI-crawler readiness: check 4.13 robots per-bot + 1.17 log AI hits + ngưỡng TTFB AI gate + note 6.5 "AI không render JS" + anti-patterns llms.txt / CWV tie-breaker; (2) khu vực 8 nạp WHY: [[Hreflang PageRank Sharing]] (gate nuance — delay hreflang chủ đích hợp lệ) + 4 nguyên tắc [[syntheses/Multilingual SEO]] (item 8.5); (3) Path B nâng thành SF CLI headless tự động (v23.3 verified trên máy, 🔴 full-crawl mặc định — không giới hạn URL, quyết định Vincent 07/2026), B-manual thành fallback; (4) Semrush Site Audit MCP = Path A-alt; (5) Fonts 5.8 theo heuristic "4 câu bắt 80%" [[Font File Optimization]]; (6) cite [[Core Web Vitals]] + [[HTML Normalization]] (cross-flag Website Functions); (7) ghi chú Playwright optional (cài 1 lần) + fallback Firecrawl MCP cho rendered DOM.
- **v1.0 (2026-07-07):** khởi tạo — khung xương từ template audit nội bộ 3.2025 (xlsx 22 sheet) + docx giải thích The AI Growth; cross-ref tier-3-technical-advance SOP làm canonical speed/CWV; lớp WHY từ wiki Koray (CoR, Index Pollution, Status Codes, Ranking Signal Consolidation); cập nhật chuẩn hiện hành từ Google docs (CWV/INP 03-2024, GSC Page indexing taxonomy, sitemap 50MB, redirect ≤10 hops, crawl budget gate ~10k trang, JS rendering 3-phase).
