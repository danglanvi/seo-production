---
name: technical-seo-audit
description: "Audit technical SEO tầng SITE theo bộ audit nội bộ GTV/TAG (crawl, PageSpeed, DataForSEO): index, crawl, redirect, CWV, crawl budget. Use when: 'audit technical [domain]', 'kiểm tra technical SEO [site]', 'site không được index / crawl chậm', 'check Core Web Vitals'."
metadata:
  version: "1.10"
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
| Tối ưu PageSpeed theo template, sửa trên server | `wp-pagespeed` (site WordPress có quyền server) | Skill này chấm CWV khu vực 5 và flag nguyên nhân; đo A/B, sửa theo lớp, rollback thuộc skill kia |
| Mã độc, IOC, hardening (khu vực 2.2 Security) | `wp-security-hardening` | Skill này flag dấu hiệu (GSC Security issues, cloaking, file lộ); ứng cứu và siết bảo mật thuộc skill kia |
| Ghi sửa title, meta, H1, slug, link lên site | `wp-content-review-apply` | Skill này lập fix list; ghi lên site phải qua trang duyệt của skill kia |
| CDN để giảm average response time Googlebot (GSC Crawl Stats) và TTFB khách ở xa origin | `cdn-speed-setup` | Skill này chấm 1.4 và ghi vị trí origin; chọn, dựng, kiểm CDN thuộc skill kia |

## Chọn skill theo triệu chứng

Bắt đầu từ triệu chứng đo được, không từ tên skill. Đo theo cột 2, rồi mở skill ở cột 3. Nếu cột 3 ghi "A, rồi B", làm A trước, B sau. Nếu cột 3 ghi điều kiện, chọn một skill theo điều kiện. Nguồn: đợt tốc độ và crawl site agency mẫu 26–27/10/2026. Lý do thêm mục này: nhân sự mới không biết bắt đầu từ skill nào.

| Triệu chứng | Đo bằng | Mở skill | Ghi chú |
|---|---|---|---|
| Average response time trong GSC Crawl Stats cao | CSV Crawl Stats; TTFB đo ngay trên server | TTFB đo trên server từ 200 ms: `wp-pagespeed` (lớp cache, PHP, MySQL). Dưới 200 ms: `cdn-speed-setup` | Ngưỡng TTFB đầy đủ ở mục Bảng ngưỡng. Origin ở VN hoặc châu Á: Googlebot đi từ Mỹ, mỗi lượt request đi và về khoảng 200 ms |
| Tỉ lệ HTML trong lượt Googlebot thấp, Googlebot tải nhiều CSS, JS | Log server bằng `kpi_html.py`; Crawl Stats theo loại file | `seo-logfile-analysis`, rồi `wp-ucss` khi file CSS gộp đổi tên liên tục | Site dưới khoảng 10.000 trang: crawl budget không phải ưu tiên, nhưng tỉ lệ thấp vẫn là dấu hiệu lãng phí |
| LCP, CLS hoặc INP kém | PSI trung vị 3 lượt theo template; CrUX | `wp-pagespeed` | Đo URL đại diện mỗi template, không quét toàn site |
| PSI báo unused CSS hoặc render-blocking với file CSS gộp lớn | PSI; kích thước file `litespeed/css/<md5>.css` | `wp-ucss` | Chỉ site bật CSS combine của LiteSpeed |
| Khách ở xa origin tải chậm | TTFB theo vùng | `cdn-speed-setup` | Việc bật proxy CDN cho tên miền chính cần người duyệt |
| Googlebot gặp nhiều 404, 5xx; bot lạ ăn tài nguyên | Log server | `seo-logfile-analysis`; chặn bot xấu: `wp-security-hardening` | Không chặn Googlebot, Bingbot, AhrefsBot, bot AI |
| Trang không vào index, noindex nhầm, canonical sai | GSC Page indexing; `index_probe.py` | Skill này, khu vực 2 và 3 | Đo bằng URL không tham số, không qua redirect |
| Spam, mã độc, cloaking, file lạ trên server | GSC Security issues; quét file | `wp-security-hardening` | |
| Lỗi giao diện sau khi sửa: tràn ngang, chữ dính, nút hỏng | Chụp và đo DOM | `web-qa-gate` | Chạy sau mọi lượt sửa CSS hoặc template |
| Cần thử thay đổi trên staging trước production | Không cần đo | `wp-staging-deploy` | |
| Có từ 3 việc đã duyệt trên một site sống, mỗi việc dùng một tài nguyên riêng (file, cấu hình, post) | Không cần đo | `web-lane-orchestration` | Chỉ chạy workflow khi người duyệt yêu cầu rõ |

## Input

**Required:**
- `$TARGET` — domain hoặc URL root cần audit (vd `https://example.vn`).

**Optional:**
- `$SITE_TYPE` — ecom / blog / news / SaaS / local. Ảnh hưởng ngưỡng file-type ratio, index bloat tolerance (Open Question tier-3 SOP — chưa có ngưỡng chốt theo site type, phải hỏi thay vì giả định).
- `$SCOPE` — mặc định full 7 khu vực; hoặc user chọn khu vực (vd chỉ "CWV + redirect").
- `$GSC_DATA` — export/screenshot GSC **Page indexing report** + **Crawl Stats** do user cung cấp.
- `$LOG_FILE` — server log hoặc export Screaming Frog Log File Analyser.
- `$CLIENT` — tên client/project để đặt tên file output.
- `$SITEMAP_MODE` — `validate` (default) | `generate` — generate: sinh XML sitemap chuẩn từ crawl (Bước 4c), chỉ khả dụng Path A/B.

**Path detection** (chi tiết ở [references/data-paths.md](references/data-paths.md)): project Ahrefs/Semrush có sẵn → Path A cho nhanh; cần crawl tươi/sâu toàn site → Path B; không có gì → Path C.

| Path | Điều kiện | Data |
|---|---|---|
| **Path A** | $TARGET có project sẵn trong Ahrefs Site Audit (hoặc Semrush — Path A-alt) + chạy được `tools/seo-audit-tool` | Ahrefs `site-audit-*` MCP (site-level) + seo-audit-tool `--deep` (CWV qua PageSpeed API, URL đại diện) — nhanh, không tốn crawl mới |
| **Path B (engine crawl chính)** | Máy có Screaming Frog + license active (SF 24.3 headless, chạy thật 18/10/2026) | Claude TỰ chạy SF `--headless` full-crawl (🔴 tốc độ mặc định 2 threads / 2–3 URL/s — shared hosting hay chặn crawler nhanh) → parse CSV. **B-file (ưu tiên khi có):** user đã crawl GUI → `--load-crawl` file + export, không đụng server. B-manual: user paste export |
| **Path C (đường lùi cuối)** | Chỉ có URL, không tool | Checklist manual: `curl -I`, /robots.txt, /sitemap.xml, view-source vs rendered DOM (hoặc Firecrawl MCP), PageSpeed Insights công khai, `site:` operator |

⚠️ Path C luôn chạy được — skill không bao giờ chết vì thiếu MCP, nhưng report phải ghi rõ độ phủ thấp hơn.

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | `schema-visible`: khối FAQ, Q&A, review mà luật chưa chốt có hiện trên trang không. 2 rubric GSC ở chế độ chữ: `gsc-topical-fit`, `gsc-cannibal-pair` | Dùng, đọc qua cổng registry. Jev chỉ nhận chữ công khai của trang (url, title, H1, đoạn mở). Không gửi query, clicks, impressions: chạy `scripts/gsc_pairs.py check` trước mỗi lượt Jev. Không dùng `gsc-intent-match` vì input của rubric này là query GSC. Không dùng cho HowTo (sai 3/3 ở holdout) và cho rating, giá, video (Jev kém so số) |
| EmbeddingGemma 2 | Chọn cặp bài ứng viên ăn thịt từ khoá ở nhánh GSC (cosine từ 0,905). Query nào nên vào trang nào: `skills/retrieval-lab` chế độ `route`, chạy local | Dùng, chỉ chọn ứng viên. Query GSC chỉ đi vào Gemma local và code (`gsc_pairs.py overlap`). Không dùng cho schema: so khớp nguyên văn và Jev đủ, cosine không tách được "trả lời khác ý" với "cùng chủ đề" |
| GLM Flash | Trích câu nguyên văn | Không dùng. Skill không có việc trích câu |
| Claude | Đọc khối dưới cổng, đọc trang dựng bằng JS, quyết định index chuyên mục và phân trang từ số đo `index_probe.py`, chọn priority, viết fix list và falsifiability | Dùng. Không giao Jev quyết định index: quyết định dựa vào số đo (robots, canonical, link chỉ có ở trang 2), không cần chấm chữ |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,curl,screaming-frog?,gsc?,jev?,gemma?,ssh?,wp-cli?,pagespeed-api?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0b — Scope gate & xác nhận

1. Xác nhận entity (client GTV nào / TAG / site nội bộ) — không mix.
2. Xác nhận `$TARGET`, `$SITE_TYPE`, `$SCOPE`. Thiếu `$SITE_TYPE` → hỏi (ảnh hưởng cách đọc file-type ratio và bloat tolerance).
3. 🔴 **Crawl budget gate**: site < ~10.000 trang unique → tuyên bố ngay "crawl budget không phải ưu tiên" (Google: crawl budget chỉ đáng lo với site ≥ ~10k–1M+ trang hoặc update rất thường xuyên — developers.google.com/crawling/docs/crawl-budget). Tập trung index hygiene thay vì khuyến nghị crawl budget nặng.
4. Nếu Path A: **báo số call dự kiến** (~3–6 Ahrefs MCP call: `site-audit-projects` ×1, `site-audit-issues` ×1, `site-audit-page-explorer` ×1–3 + 1 lần chạy seo-audit-tool trên 3–5 URL đại diện) → **chờ user xác nhận** rồi mới gọi.
5. Nếu Path B: **báo scope crawl** — 🔴 mặc định FULL site, KHÔNG giới hạn URL trừ khi user yêu cầu (quyết định Vincent 07/2026); kèm tốc độ crawl + ước tính thời gian + note server load → **chờ user xác nhận** rồi mới chạy. Site lớn → đề xuất database storage mode + chạy qua đêm theo 2 nhịp (data-paths.md).
6. Hỏi user có GSC access không (hoặc đã nối GSC vào SF — Path B kéo được URL Inspection data ngay trong crawl). Kiểm API trước bằng `tools/gsc/gsc.sh sites`: property đã share cho tài khoản Google đang login `gws` trên máy → chạy nhánh GSC 90 ngày ([references/gsc-90-ngay.md](references/gsc-90-ngay.md)). Không có → khu vực Index Coverage sẽ đánh dấu ⬜ THIẾU DATA kèm hướng dẫn lấy report (không bịa — xem Gate #2).
7. Khi audit chạm item 4.13/1.17: hỏi **chiến lược AI crawler** của client (muốn AI citation → mở bot; muốn opt-out training → chặn là chủ đích) — không giả định.

### Bước 1 — Nạp khung ground truth

1. Đọc [references/audit-checklist-by-area.md](references/audit-checklist-by-area.md) — khung xương 7(+1) khu vực đã convert từ template nội bộ, mỗi item có tiêu chí ĐẠT + nguồn + priority.
2. Khu vực Speed/HTML/CWV: canonical = `sop/06-self-checklist/tier-3-technical-advance.md` (bản operational của sheet "2. Checklist technical advance", đã fix FID→INP, Server Push→preload) — cross-ref, KHÔNG viết lại.
3. 🔴 **Template drift**: item lỗi thời trong template (rel=next/prev, AMP, FID, mobile-friendly test tool, PageSpeed >80, trang ≤35KB, load >20s, GTMetrix <1,7s) → xử lý là "legacy — thay bằng X", KHÔNG lặp lại như tiêu chuẩn. Xem bảng ngưỡng bên dưới.

### Bước 2 — Thu data theo Path

- **Path A**: gọi MCP + chạy tool theo [references/data-paths.md](references/data-paths.md). 🔴 WRAP: check deterministic (meta lengths, heading tree, canonical, schema presence, links) đã nằm trong seo-audit-tool Layer 1; CWV lấy từ `--deep` (PageSpeed API); trang JS-heavy → thêm `--render` (Playwright). Skill chỉ **diễn giải output + xếp priority**, không tự chấm lại.
- **Path B**: chạy SF CLI headless theo data-paths.md (SF 24.3, lệnh chạy thật 18/10 có `--bulk-export` inlinks 3xx/4xx cho Bước 3c) — chạy nền + bọc `caffeinate -i` (chống máy sleep); trong lúc crawl làm các khu vực không cần crawl (curl, robots, sitemap, PSI, log). Crawl xong → 🔴 **completeness check** (đếm Status 0/Connection Timeout — cao thì mọi số đếm ghi caveat "cận dưới") → parse CSV bằng script (DuckDB/awk), phân loại vào khu vực. Link Score trống khi chạy headless: tính PageRank nội bộ bằng `scripts/pagerank.py` (data-paths.md mục Bẫy khi chạy headless). B-file: user có crawl sẵn → `--load-crawl` + export (không đụng server). B-manual: đưa user danh sách export (cột per khu vực trong data-paths.md) → nhận CSV/paste.
- **Path C**: chạy checklist manual per URL mẫu; ghi rõ giới hạn coverage trong report.
- **Nhánh GSC 90 ngày** (chạy kèm mọi Path khi có quyền API): kéo cửa sổ, chuỗi tuần, query × trang, URL Inspection; chạy `scripts/gsc_clean.py` trước khi đếm (bỏ dòng jump link `#ftoc-…`, cờ bảng bị cắt ở 25.000 dòng); đọc theo luật `num=100` và query bất thường; phân rã nguyên nhân giảm; so query của cặp trang bằng `scripts/gsc_pairs.py overlap` (local); Jev `gsc-topical-fit`, `gsc-cannibal-pair` ở chế độ chữ theo [references/gsc-90-ngay.md](references/gsc-90-ngay.md). Dữ liệu GSC chỉ xử lý local: chạy `gsc_pairs.py check` trên file input trước khi gọi Jev. Manual actions và Security issues: nhờ user kiểm tay trên GSC.
- Mọi data point ghi kèm **nguồn + ngày lấy** (vd "Ahrefs Site Audit crawl 2026-07-05", "GSC screenshot user cung cấp 2026-07-07").
- 🔴 **URL sạch khi kiểm robots và canonical.** Không gắn query (`?nc=`, `?utm_*`) để né cache: theme và plugin SEO hay trả noindex cho URL có query. Cần bản chưa cache thì đổi header hoặc User-Agent. Tham số trong `cache-exc_qs` chỉ dùng đo tốc độ, không dùng đo robots. URL có query chỉ dùng để xác nhận noindex. Sau khi purge cache, kiểm 5 biến thể của URL sạch bằng `skills/wp-pagespeed/scripts/cache_variants.py`.

### Bước 3 — Audit theo 7(+1) khu vực

Chạy checklist từng khu vực theo references/audit-checklist-by-area.md:

1. **Crawl & Log File** — 404/soft-404, 5xx/503, orphan URL, wasted budget, spam bots, AI crawler hits (GEO baseline), 3 checkpoint GSC Crawl Stats. Origin ở VN hoặc châu Á: Googlebot crawl chủ yếu từ Mỹ, mỗi vòng đi về khoảng 200 ms. Origin nhanh vẫn khó đạt average response time dưới 250 ms. Ghi vị trí origin, chuyển `cdn-speed-setup` khi chỉ số trên ngưỡng tối thiểu.
2. **Index Coverage** — GSC Page indexing taxonomy hiện hành, Index Pollution/Bloat playbook.
3. **Redirect & Canonical** — chain ≥2 hops, 302→301, 9 biến thể homepage, self-canonical, parameter URLs.
4. **Sitemap & Robots.txt** — 100% URL 200, ≤50.000 URL / ≤50MB, robots không thay noindex, không chặn CSS/JS, AI bot access chủ đích theo **bot-purpose matrix** (search/training/user-triggered — xem checklist 1.17): OAI-SearchBot·GPTBot·ChatGPT-User / Claude-SearchBot·ClaudeBot·Claude-User / PerplexityBot·Perplexity-User / Google-Extended (control token).
5. **Core Web Vitals & Site Speed** — LCP/INP/CLS 75th percentile, DOM, fonts, caching (canonical: tier-3 SOP mục 3–5).
6. **JS Rendering** — 3-phase Crawl→Render→Index, `<a href>`, SPA soft-404, raw vs rendered delta (đa số AI crawler được quan sát fetch raw HTML, không render JS như Googlebot — `observational`, vendor docs không cam kết; delta lớn = rủi ro vô hình với AI engines), SSR.
7. **HTTPS & Mobile** — http/https = 2 entity riêng, 12 items HTTPS, mobile parity.
8. *(chỉ khi site đa ngôn ngữ)* **International/hreflang** — tier-3 SOP mục 10 + 4 nguyên tắc [[syntheses/Multilingual SEO]]; nuance [[Hreflang PageRank Sharing]]: thiếu hreflang có thể là chủ đích khi alternates chưa đủ chất lượng — hỏi trước khi flag ❌.

Site WordPress dùng Rank Math, audit chạm index chuyên mục, thẻ hoặc phân trang (khu vực 2, 3, 4): đọc [references/index-chuyen-muc-rank-math.md](references/index-chuyen-muc-rank-math.md). Đo bằng `scripts/index_probe.py`: lệnh `probe` cho robots, canonical, `<loc>`; lệnh `paged` so trang 1 với trang 2.

Mỗi item chấm **checklist-status** (trung thành mô hình template — KHÔNG bịa thang điểm số):

| Status | Nghĩa |
|---|---|
| ✅ ĐẠT | Thỏa tiêu chí ĐẠT, có evidence |
| ⚠️ CẦN XEM | Gần ngưỡng / evidence chưa đủ kết luận |
| ❌ FAIL | Vi phạm tiêu chí, có evidence |
| ⬜ THIẾU DATA | Không có data (vd không có GSC) — ghi cách lấy |

### Bước 3c — Nguồn của link hỏng

Với mỗi đích 3xx, 4xx trong crawl, tìm nơi chứa link để sửa tận gốc. Đọc [references/nguon-link-va-schema.md](references/nguon-link-va-schema.md) §1.

1. Đếm và tách lớp: `python3 skills/technical-seo-audit/scripts/link_sources.py summarize --inlinks <3xx inlinks> --inlinks <4xx inlinks> --site <domain> --out-dir <W>/links`.
2. Nếu có hồ sơ server, chạy `scripts/find_sources.php` bằng WP-CLI với chuỗi trong `patterns.txt`, rồi `link_sources.py sources`. Không có hồ sơ server thì ghi "chưa tìm nguồn trong DB" và dừng nhánh này.
3. Tìm chuỗi còn thiếu trong file theme, mu-plugin bằng `rg` trên server (chỉ đọc).
4. Ghi cột "Nguồn" vào fix list: ID bài, template Elementor, menu item, trường ACF, usermeta hoặc file theme.

### Bước 3d — Schema khớp nội dung hiển thị

Kiểm khối schema cần nội dung hiển thị: FAQPage, QAPage, HowTo, Review, AggregateRating, Offer, VideoObject. Đọc [references/nguon-link-va-schema.md](references/nguon-link-va-schema.md) §2.

1. Trích và kiểm tất định: `schema_visible.py extract`.
2. Gửi khối FAQ, Q&A, review chưa chốt cho Jev: `schema_visible.py prepare` rồi `tools/ai-assist/jev.py --task skills/technical-seo-audit/tasks/schema-visible.json`.
3. Ghép qua cổng: `schema_visible.py decide --fail-gate <cổng registry>`. Registry chưa có cổng thì bỏ `--fail-gate`: Claude đọc mọi khối chưa chốt.
4. Đưa khối FAIL vào khu vực Semantic Markup của báo cáo và route sửa markup sang `schema-markup-generator`.

### Bước 4 — Xếp priority fix

Xếp mọi ❌/⚠️ theo impact (tinh thần case "in ấn catalog" docx §3.0 — một dòng robots.txt giam cả bộ từ khóa ngoài top 100, gỡ ra → top 8 trong 3 ngày):

| Priority | Loại lỗi | Ví dụ |
|---|---|---|
| **P0 — chặn index** | robots chặn nhầm, noindex nhầm, canonical sai, 5xx, sitemap toàn URL lỗi | "Indexed, though blocked by robots.txt" ≠ 0 |
| **P1 — lãng phí crawl / bloat** | redirect chains, soft 404, index pollution, orphan, parameter URLs index | 404 vĩnh viễn chưa chuyển 410 |
| **P2 — CWV & speed** | LCP/INP/CLS poor, TTFB >800ms, DOM >1.500 nodes | INP >500ms mobile |
| **P3 — tối ưu nhỏ** | Brotli, preload, font, ảnh >100KB, minify | HTML chưa minify |

Mỗi fix ghi: lỗi → evidence (URL/số liệu + nguồn) → hành động cụ thể → người làm (dev/SEO/content) → **Falsifiability**: "làm sao biết nếu khuyến nghị này sai?" + leading indicator theo dõi sau fix (metric + nguồn + khung thời gian — vd 301 prefix cũ → GSC Crawl Stats 404 theo prefix giảm ≥80% trong 4 tuần; không giảm = chẩn đoán sai nguồn 404, xét lại).

Fix có 301 hoặc 410: chọn đích theo `skills/content-inventory-audit/references/bo-bai.md` và rubric Jev `redirect-pick` (`tools/ai-assist/tasks/redirect-pick.json`). Skill này không chép quy trình chọn đích. Skill này kiểm phần kỹ thuật của đích: trả 200, index, canonical tự trỏ, không chuỗi redirect. Sau khi ghi, lần lại chuỗi redirect của cả `/page/N/` thuộc chuyên mục cũ.

### Bước 4b — Whole-site Health Score (0-100)

Điểm tổng hợp cuối audit — để **so sánh giữa các kỳ audit (T1 → T4 → T7)** và nói chuyện với khách. KHÔNG thay checklist-status per item, KHÔNG thay thứ tự fix list.

**Data-tier gate (điều kiện tính):** chỉ tính khi Path A hoặc Path B với crawl đã qua completeness check (Bước 2). Path C hoặc crawl thiếu → KHÔNG tính score, ghi "Health Score: không tính — coverage thấp". Khu vực có >50% items ⬜ THIẾU DATA → loại khỏi score + redistribute trọng số theo tỷ lệ, ghi rõ trong report.

**Công thức:**
- Điểm khu vực = (✅ + 0,5×⚠️) / (✅ + ⚠️ + ❌) × 100 — item ⬜ loại khỏi mẫu số.
- Health Score = Σ (trọng số × điểm khu vực) / 100.

**Trọng số baseline GTV** (ghi chú bắt buộc: *baseline GTV, điều chỉnh theo dự án* — report ghi rõ bộ trọng số đã dùng):

| Khu vực | Trọng số |
|---|---|
| Index Coverage | 25 |
| Crawl & Log File | 15 |
| Redirect & Canonical | 15 |
| CWV & Site Speed | 15 |
| Sitemap & Robots.txt | 10 |
| JS Rendering | 10 |
| HTTPS & Mobile | 10 |
| International/hreflang | 0 — site đa ngôn ngữ: hreflang = 10, giảm Index Coverage 25→20 và Crawl 15→10 |

**Luật hiển thị:** còn ❌ P0 chưa fix → score luôn đi kèm cờ, vd `72/100 (⚠️ 2 lỗi P0)` — không để con số cao che P0. So sánh giữa kỳ chỉ hợp lệ khi cùng Path + cùng bộ trọng số + coverage tương đương; đổi 1 trong 3 → ghi "không so sánh trực tiếp với kỳ trước".

### Bước 4c — Sitemap GENERATE (`$SITEMAP_MODE=generate`)

Khu vực 4 mặc định chỉ VALIDATE. Khi user yêu cầu generate → sinh XML sitemap chuẩn từ danh sách URL đã crawl (bắt buộc Path A/B + qua completeness check — crawl thiếu = sitemap thiếu URL; KHÔNG generate từ Path C):

1. **Lọc URL đủ chuẩn** (tiêu chí = chính checklist 4.1–4.3): chỉ giữ URL HTML 200, indexable, self-canonical. LOẠI: noindex · redirect (3xx) · non-canonical · 4xx/5xx · blocked-by-robots · trang noindex-chủ-đích (thank-you, cart, search nội bộ — 3.8).
2. **Segment theo loại page** khi site lớn (> ~5.000 URL hoặc cấu trúc rõ): sitemap index + file con product/category/blog/static — đồng thời phục vụ trace tỷ lệ index per khu vực (4.5, 2.10). Giới hạn per file: ≤50.000 URL / ≤50MB (Bảng ngưỡng).
3. **Bảng diff "crawled-vs-sitemap"** (bắt buộc kèm output): (a) URL indexable trong crawl nhưng THIẾU trong sitemap hiện tại; (b) URL trong sitemap hiện tại nhưng FAIL chuẩn (non-200/noindex/non-canonical/redirect) — mỗi dòng kèm lý do loại.
4. **Deliverable:** file `sitemap*.xml` + bảng diff → giao dev/CMS review rồi mới upload + submit GSC (4.7) theo [references/gsc-ghi.md](references/gsc-ghi.md); người duyệt duyệt từng lần nộp. Skill KHÔNG tự đẩy file lên server. `<lastmod>` chỉ ghi khi có ngày thật (CMS/crawl) — không bịa; bỏ `changefreq`/`priority` (Google ignore).

### Bước 5 — Render report & trả file

- Render theo skeleton ở mục Output.
- Đặt tên: `<client>_Technical-SEO-Audit_v1.md` → tài liệu nội bộ «<project>» (ngoài repo, hỏi Lead/Vincent) (tăng `_v2` nếu trùng). Audit nội bộ GTV/TAG → hỏi user nơi trả nếu chưa rõ.
- Kết report: đề xuất re-audit sau khi fix P0/P1 (validate qua GSC + re-crawl).

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Số đếm từ crawl có completeness check (Status 0, timeout) và đã tách nút chia sẻ, widget chat khỏi redirect nội bộ. Nguồn lỗi: crawl 10/07/2026 bị shared hosting chặn ở 29%; site mẫu 18/10, 756/4.544 inlink tới redirect là Zalo và Messenger.
- [ ] Robots và canonical kết luận từ URL sạch. Phân trang đề xuất index có số link chỉ ở trang 2 từ `index_probe.py paged`. Nguồn lỗi: site agency mẫu 18/10, đề xuất v1 báo 35 trang noindex, thực tế 35/35 index, vì URL đo gắn `?nc=`; lượt so trang 17/10 ra md5 rỗng `d41d8cd9` vì bộ trích hỏng.
- [ ] Mỗi link hỏng trong fix list có cột nguồn (bài, Elementor, menu, ACF, usermeta, file theme), tìm cả bản `\/` của Elementor. Nguồn lỗi: site mẫu 18/10, chuỗi thường không thấy `_elementor_data`, link tác giả nằm ở usermeta.
- [ ] Số GSC đã bỏ dòng `#ftoc-…` và đã kiểm cờ 25.000 dòng. Nguồn lỗi: site mẫu 18/10, 6.702/25.000 dòng là jump link, lượt hiển thị một truy vấn bị thổi gấp 4,8 lần.
- [ ] Schema đã đối chiếu với nội dung hiển thị: FAQ, review, video, giá. Nguồn lỗi: site mẫu 19/10 khai VideoObject nhưng trang không nhúng video.
- [ ] Input Jev ở nhánh GSC chỉ có chữ công khai của trang, đã qua `gsc_pairs.py check`. Nguồn lỗi: v1.7 gửi `shared_queries` và `top_queries` lấy từ GSC cho Jev.
- [ ] Đề xuất gộp hoặc 301 từ nhánh GSC đã kiểm SERP. Nguồn lỗi: audit GSC 17/10 đề xuất gộp 5 cặp, 3 cặp có SERP trùng 0–1/10.
- [ ] Mỗi fix có điều kiện sai và chỉ báo theo dõi; fix ghi lên site đi qua `wp-content-review-apply`. Nguồn lỗi: v1.4, khuyến nghị "tối ưu thêm" không kiểm được.

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
- **Health Score: nn/100** (trọng số: baseline GTV / custom — kèm cờ `⚠️ n lỗi P0` nếu còn; hoặc "không tính — coverage thấp" khi không đủ data tier — Bước 4b) · kỳ trước: nn/100 (nếu so sánh hợp lệ)
- Top 3 việc phải làm ngay (P0)

## 2. Bảng tổng hợp theo khu vực
| Khu vực | ✅ | ⚠️ | ❌ | ⬜ | Điểm khu vực | Lỗi nặng nhất |
|---|---|---|---|---|---|---|
| Crawl & Log File | | | | | | |
| Index Coverage | | | | | | |
| Redirect & Canonical | | | | | | |
| Sitemap & Robots.txt | | | | | | |
| CWV & Site Speed | | | | | | |
| JS Rendering | | | | | | |
| HTTPS & Mobile | | | | | | |
| International/hreflang *(nếu áp dụng)* | | | | | | |

## 3. Chi tiết theo khu vực
### 3.x <Tên khu vực>
| Check | Status | Evidence (URL/số liệu + nguồn + ngày) | Tiêu chí ĐẠT (nguồn ngưỡng) |
|---|---|---|---|
**Nhận định:** <2-4 câu diễn giải WHY — link concept wiki nếu liên quan>

## 4. Fix list ưu tiên
| # | Priority | Lỗi | Evidence | Hành động | Người làm | Falsifiability — sai thì thấy gì? + leading indicator |
|---|---|---|---|---|---|---|

## 5. Data còn thiếu
- <item ⬜ + hướng dẫn user lấy: GSC Page indexing export, Crawl Stats screenshot, server log…>

## 6. Nguồn & phạm vi
- Tool/data đã dùng + ngày · Khu vực loại khỏi scope (backlink, content quality, schema authoring — route skill anh em)

## 7. Sitemap đề xuất *(chỉ khi $SITEMAP_MODE=generate)*
- Đường dẫn file `sitemap*.xml` đã sinh + cấu trúc segment · Bảng diff crawled-vs-sitemap (thiếu / fail chuẩn + lý do) · Note: dev review trước khi upload + submit GSC
```

## Behavior Gates

**#1 Think Before** — Trước khi audit: entity nào? site type nào? crawl budget gate qua chưa? GSC có không? Path nào? chiến lược AI crawler? Thiếu thông tin quyết định output → hỏi, không giả định. Trước khi gọi MCP: báo số call, chờ xác nhận. Trước khi chạy SF crawl: báo scope (full mặc định) + thời lượng ước tính, chờ xác nhận — crawl chạm server thật của khách.

**#2 Evidence** — 🔴 Mọi con số trong report truy được về nguồn + ngày. Ngưỡng chỉ lấy từ Bảng ngưỡng whitelist. 🔴 **KHÔNG bịa trạng thái GSC**: chỉ báo cáo index coverage khi có data thật (user paste export/screenshot hoặc Ahrefs); không có → ⬜ THIẾU DATA + hướng dẫn lấy. Dùng đúng taxonomy **Page indexing report hiện hành** (Indexed / Not indexed + các lý do Not indexed theo danh sách hiện hành tại support.google.com/webmasters/answer/7440203 — đối chiếu doc Google khi chấm, danh sách có thể thay đổi), KHÔNG dùng tên trạng thái report cũ Valid/Warning/Error/Excluded.

**#3 Surgical** — Chỉ audit technical site-level. Không chấm content quality, không viết JSON-LD, không audit backlink, không sửa HTML semantic — flag + route theo bảng phân vai. Không tái mô tả check deterministic mà seo-audit-tool Layer 1 đã làm.

**#4 Goal-driven** — Deliverable = **fix list ưu tiên theo impact** (P0 chặn index > P1 crawl waste > P2 CWV > P3 tối ưu nhỏ), không phải bản liệt kê lỗi dàn trải. Mỗi finding trả lời "fix cái này thì site được gì" — nối về [[Cost of Retrieval]] (CoR là denominator của Topical Authority).

**#5 Falsifiable** — Mỗi khuyến nghị trong fix list phải trả lời "**làm sao biết nếu khuyến nghị này sai?**" + 1 leading indicator đo được sau fix (metric + nguồn + khung thời gian, vd "GSC Crawl Stats: 404 theo prefix `/product/` giảm ≥80% trong 4 tuần"). Không viết được điều kiện-sai → khuyến nghị chưa đủ chín, hạ thành giả thuyết cần thêm data, không vào fix list. Bộ leading indicators = khung đo cho re-audit (Bước 5) và Health Score kỳ sau (Bước 4b).

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
  - Ngoại lệ (18/10/2026): `/llms.txt` tĩnh đặt để đạt audit `llms-txt` của hạng mục "Duyệt web bằng tác nhân" trên PSI (skill `wp-pagespeed`). Không chấm file này là audit item SEO hay GEO.
- ❌ Bán CWV như ranking lever chính — Google coi là tie-breaker (wiki [[Core Web Vitals]] Open Question, chưa có evidence độc lập); frame lợi ích theo [[Cost of Retrieval]].
- ❌ Flag "thiếu hreflang" thành lỗi mặc định khi alternates chưa đủ chất lượng — hreflang share signal 2 chiều, delay có thể là chủ đích ([[Hreflang PageRank Sharing]]).
- ❌ Kết luận số đếm (orphan, ảnh, duplicate) từ crawl không hoàn chỉnh mà không ghi caveat — check Status 0/Timeout % trước, số từ crawl thiếu là "cận dưới".
- ❌ Báo động số redirect gộp cả external share links (Zalo/X/FB intent) — lọc external trước khi đếm redirect nội bộ.
- ❌ Dùng TTFB lab (Lighthouse) đơn lẻ làm nguồn — lab thường thấp ảo; nguồn chuẩn = GSC avg response time + curl ×3–5.
- ❌ So sánh Health Score giữa 2 kỳ khác Path/coverage/trọng số — score chỉ so sánh được khi cùng điều kiện tính; báo score khi chưa qua data-tier gate.
- ❌ Generate sitemap từ crawl chưa qua completeness check hoặc từ Path C — sitemap thiếu URL tệ hơn không generate; tự upload sitemap lên server thay vì giao dev review.
- ❌ Khuyến nghị không falsifiable ("cải thiện chất lượng", "tối ưu thêm") — không có leading indicator đo được thì không vào fix list.
- ❌ Cộng số GSC theo trang khi còn dòng jump link `#…`; tin bảng query × trang đúng 25.000 dòng là đủ.
- ❌ Tìm nguồn link chỉ trong `post_content`, bỏ `_elementor_data` (dấu `\/`), menu, ACF, usermeta và file theme.
- ❌ Tin nhãn Jev `schema-visible` dưới cổng, hoặc gửi Jev khối HowTo, rating, giá.
- ❌ Gửi query, clicks, impressions của GSC cho Jev (`shared_queries`, `top_queries`, `gsc-intent-match`) → Jev chỉ nhận chữ trang; so query bằng code hoặc Gemma local.
- ❌ Kết luận robots hoặc canonical từ URL có query (`?nc=`, `?utm_*`) → đo URL sạch, né cache bằng header hoặc User-Agent.
- ❌ Cho index trang phân trang khi chưa so danh sách trang 2 với trang 1, hoặc đo robots trên staging đang ép noindex toàn site.
- ❌ Đọc thư mục cấu hình `~/.ScreamingFrogSEOSpider/` → lộ token connector; kiểm licence bằng hash.
- ❌ Báo hạng PageRank từ lượt tính tạm hoặc không ghi bộ lọc nút → tính bằng `pagerank.py`, ghi số nút.

## References & wiki

**References trong skill:**
- [references/audit-checklist-by-area.md](references/audit-checklist-by-area.md) — checklist chi tiết 7(+1) khu vực: check · cách kiểm · tiêu chí ĐẠT · nguồn · priority.
- [references/data-paths.md](references/data-paths.md) — map Path A (Ahrefs site-audit MCP + seo-audit-tool) / Path B (cột Screaming Frog) / Path C (manual chỉ-có-URL). Path B có mục bẫy khi chạy headless và PageRank tự tính.
- [references/gsc-90-ngay.md](references/gsc-90-ngay.md) — nhánh GSC qua API: lệnh `tools/gsc/gsc.sh`, luật đọc số, bẫy jump link và 25.000 dòng, phân rã nguyên nhân giảm, đợt tụt theo nhóm, cơ hội, 2 rubric Jev chế độ chữ, so query local bằng `gsc_pairs.py` (`tools/ai-assist/`).
- [references/nguon-link-va-schema.md](references/nguon-link-va-schema.md) — Bước 3c tìm nguồn link hỏng (SF inlinks, `find_sources.php`, `rg` theme) và Bước 3d schema khớp nội dung hiển thị (luật + Jev `schema-visible`, cổng, bẫy bộ trích).
- [references/index-chuyen-muc-rank-math.md](references/index-chuyen-muc-rank-math.md) — Rank Math: option robots và sitemap của chuyên mục, hàm theme tự noindex, bảng quyết định chuyên mục, thẻ, phân trang, đo bằng `index_probe.py`, thử staging bằng mu-plugin tạm, ghi production, chẩn đoán schema Rank Math tắt.
- [references/gsc-ghi.md](references/gsc-ghi.md) — nộp sitemap qua API (quyền Full user, PUT trả 204, kiểm `lastSubmitted`), việc API không làm được, bẫy đọc.
- `scripts/` — `schema_visible.py`, `link_sources.py`, `find_sources.php`, `gsc_clean.py`, `gsc_pairs.py`, `index_probe.py`, `pagerank.py`, `robots-public-test.php` (mu-plugin tạm cho staging); test offline `tests/test_scripts.py`. `tasks/schema-visible.json` — rubric Jev.

**Ground truth nội bộ:**
- [[sources/seo-audit-template-toan-dien-2025-gtv]] — source page của template 22 sheet (file gốc: `raw/_ingested/SEO Audit Template (audit toàn diện) - Update 3.2025.xlsx`).
- [[sources/giai-thich-seo-audit-toan-dien-tag]] — source page của docx giải thích 19 sections (file gốc: `raw/_ingested/Giải thích các phần trong SEO Audit Toàn diện - The AI Growth.docx`).
- `sop/06-self-checklist/tier-3-technical-advance.md` — canonical cho khu vực Speed/HTML/CWV (bản operational của sheet 2).
- `tools/seo-audit-tool/README.md` — spec CLI 3 lớp.

**Wiki Semantic SEO (lớp WHY):** [[Cost of Retrieval]] · [[Index Pollution]] · [[Status Codes]] · [[Robots.txt]] · [[Faceted Navigation]] · [[Index Partition]] · [[Meta Tags]] · [[Ranking Signal Consolidation]] · [[GEO]] · [[Core Web Vitals]] · [[Font File Optimization]] · [[Hreflang PageRank Sharing]] · [[HTML Normalization]] · [[syntheses/Multilingual SEO]]

**Google docs hiện hành:** web.dev/articles/vitals · support.google.com/webmasters/answer/7440203 · developers.google.com/crawling/docs/crawl-budget · developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics · developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

## Changelog

- **v1.10 (2026-10-27):** mục mới "Chọn skill theo triệu chứng": 11 triệu chứng → cách đo → skill bắt đầu (đề xuất T2 của đợt rà phiên tốc độ và crawl 26–27/10, người duyệt chốt 27/10). `evals/cases.yaml` 4 ca định tuyến.
- **v1.9.1 (2026-10-26):** bảng Phân vai thêm `cdn-speed-setup`; khu vực 1 ghi giới hạn RTT của origin ở VN hoặc châu Á với Googlebot ở Mỹ (đợt CDN site VN 26/10/2026).
- **v1.9 (2026-10-25, tech-1):** reference `index-chuyen-muc-rank-math.md` (option Rank Math, hàm theme tự noindex, bảng quyết định chuyên mục và phân trang, thử staging, schema tắt) và `gsc-ghi.md` (nộp sitemap bằng service account); script `index_probe.py`, `pagerank.py`, mu-plugin tạm `robots-public-test.php`, 11 test mới; luật URL sạch khi kiểm robots; bẫy SF headless trong `data-paths.md`; checklist 3.6 thêm ngoại lệ phân trang giả; chọn đích 301/410 trỏ sang `content-inventory-audit`.
- **v1.8.2 (2026-10-19):** rút description còn 267 ký tự. Thay tên khách thật ở changelog v1.2, `references/data-paths.md` và `references/audit-checklist-by-area.md` bằng "site khách shared hosting" để master trung lập.
- **v1.8.1 (2026-10-19):** mục 3.7 checklist trỏ tới `internal-linking` `link-js.md` §7 (dạng mã link của filter, sắp xếp, phân trang).
- **v1.8.0 (2026-10-19):** Bước 0 kiểm tool; SF 24.3 headless; Bước 3c nguồn link hỏng (`link_sources.py`, `find_sources.php` có bản `\/` và usermeta); Bước 3d schema khớp nội dung hiển thị (rubric Jev `schema-visible` hiệu chuẩn gold mù 140 khối); `gsc_clean.py` bỏ dòng `#ftoc` và cờ 25.000 dòng; phân việc model; tự phản biện; test offline; nhánh GSC: Jev chỉ nhận chữ trang (`gsc-cannibal-pair`, `gsc-topical-fit` chế độ chữ, kiểm lại trên gold 17/10), so query bằng `gsc_pairs.py` hoặc `retrieval-lab route`, bỏ `gsc-intent-match`.
- **v1.7.1 (2026-10-18):** ghi ngoại lệ `/llms.txt` cho audit `llms-txt` của PSI (hạng mục "Duyệt web bằng tác nhân"): được đặt, không tính là đòn bẩy GEO.
- **v1.7 (2026-10-17):** thêm nhánh GSC 90 ngày qua API (`references/gsc-90-ngay.md`, `tools/gsc/gsc.sh`) từ một audit thật 17/10: cửa sổ + chuỗi tuần có mốc cập nhật Google, luật `num=100` và query bất thường, phân rã nguyên nhân giảm, đợt tụt theo nhóm chủ đề, 3 rubric Jev gsc-* có ngưỡng (`tools/ai-assist/`); Bước 0 kiểm `gsc.sh sites` trước khi hỏi export. Sửa title, meta, link sau audit: `wp-content-review-apply`.
- **v1.6 (2026-08-29, Vincent duyệt 29/08 — FINDINGS 22/08 §6-H):** item **4.13 AI bot access** và **1.17 AI crawler hits** nâng lên **P0 khi GEO Readiness verdict = Chuẩn hoá hoặc HĐ có KPI GEO** (= gate G-T1 GE-02 của `tier-1-geo.md` v2.0.2; search + user-triggered bot bị chặn → dừng lớp GEO trước khi audit chunk), giữ P1/P2 cho dự án SEO thường; thêm evidence first-party +111% pageview kênh AI Assistant sau khi mở bot (n=1, nhãn D, ẩn danh); trỏ bot-purpose matrix canonical `lop-geo-v2.md` §G1; bảng route "AX1-AX5" → AX1-AX7 + ghi rõ 4.13/1.17 là pre-flight input cho `geo-content-optimization` Bước 0.
- **v1.5 (2026-08-21):** thêm item 1.18 Markdown for Agents (Cloudflare) — ADVANCED/opt-in P3, measure-first (Vincent duyệt 21/08: "bỏ vào checklist cũng được, tuy nhiên cần đo lường độ hiệu quả kỹ hơn"): curl check content negotiation + đếm markdown-requests trong log làm baseline, 2 gate (Content-Signal policy review + fail-silent limits), KHÔNG bán như GEO lever. Nguồn: Batch 39 wiki (Cloudflare official + Suganthan 44-day n=1).

- **v1.4 (2026-07-19):** INTEGRATE từ gap-audit claude-seo (repo 11.7k★, đã phân loại INTEGRATE): (1) **Whole-site Health Score 0-100** (Bước 4b) — điểm khu vực (✅+0,5×⚠️)/(✅+⚠️+❌) × trọng số baseline GTV (điều chỉnh theo dự án), data-tier gate (chỉ Path A/B + completeness check, khu vực >50% ⬜ loại + redistribute), cờ P0 đi kèm score, luật so sánh giữa kỳ T1→T4→T7; (2) **Sitemap GENERATE mode** (`$SITEMAP_MODE=generate`, Bước 4c) — lọc URL theo chuẩn 4.1–4.3 (loại noindex/redirect/non-canonical/4xx-5xx), segment product/category/blog khi site lớn, bảng diff crawled-vs-sitemap bắt buộc, không tự upload; (3) **Falsifiability field** per finding — gate #5 + cột mới trong fix list + leading indicator sau fix. Output skeleton: thêm Health Score (mục 1), cột Điểm khu vực (mục 2), cột Falsifiability (mục 4), mục 7 sitemap. Metadata version đồng bộ lại theo changelog (drift 1.2/1.3 cũ).
- **v1.3 (2026-07-13, P0 remediation LINT-2026-005):** (1) bỏ blanket claim "AI crawler không render JS" → re-label `observational` (vendor docs không cam kết) ở khu vực 6 + item 6.5; (2) thêm **bot-purpose matrix** search/training/user-triggered (OAI-SearchBot·GPTBot·ChatGPT-User / Claude-SearchBot·ClaudeBot·Claude-User / PerplexityBot·Perplexity-User / Google-Extended) theo crawler docs chính chủ; (3) fix 1.17: Google-Extended không có UA riêng trong log (chỉ là robots token, chặn không ảnh hưởng Google Search) + training-bot hits không phải AI-visibility KPI.
- **v1.2 (2026-07-10):** đúc kết từ lần chạy thật đầu tiên (site khách shared hosting, 10/07/2026): (1) Path B tốc độ mặc định 2 threads/2–3 URL/s + dấu hiệu server chặn giữa crawl + completeness check bắt buộc (Status 0/Timeout → caveat "cận dưới"); (2) Path **B-file** `--load-crawl` (user crawl GUI, Claude load + export không đụng server — bộ export names verified v23.3); (3) checklist mới: chữ ký PHP session giết cache ở 5.9 (PHPSESSID + Expires 1981 + no-store; nghi phạm YITH/Woo plugins), 404-pattern-theo-prefix = đổi URL structure không 301 ở 1.1, pagination canonical về trang 1 ở 3.6, đọc By Googlebot type + JS/CSS `?ver=` ở 1.6; (4) GSC Crawl Stats qua Google Sheets + gws (strip dòng keyring trước parse) + các phép phân tích chuẩn; (5) PSI có key trong `.agent-secrets/.env`, nuance site-không-CrUX chấm bằng lab ghi rõ nguồn; (6) `tools/gsc/gsc.sh` = Path A+ (pending OAuth consent); (7) anti-patterns mới: số đếm từ crawl thiếu, redirect gộp share links, TTFB lab đơn lẻ.
- **v1.1 (2026-07-10):** (1) lớp AI-crawler readiness: check 4.13 robots per-bot + 1.17 log AI hits + ngưỡng TTFB AI gate + note 6.5 "AI không render JS" + anti-patterns llms.txt / CWV tie-breaker; (2) khu vực 8 nạp WHY: [[Hreflang PageRank Sharing]] (gate nuance — delay hreflang chủ đích hợp lệ) + 4 nguyên tắc [[syntheses/Multilingual SEO]] (item 8.5); (3) Path B nâng thành SF CLI headless tự động (v23.3 verified trên máy, 🔴 full-crawl mặc định — không giới hạn URL, quyết định Vincent 07/2026), B-manual thành fallback; (4) Semrush Site Audit MCP = Path A-alt; (5) Fonts 5.8 theo heuristic "4 câu bắt 80%" [[Font File Optimization]]; (6) cite [[Core Web Vitals]] + [[HTML Normalization]] (cross-flag Website Functions); (7) ghi chú Playwright optional (cài 1 lần) + fallback Firecrawl MCP cho rendered DOM.
- **v1.0 (2026-07-07):** khởi tạo — khung xương từ template audit nội bộ 3.2025 (xlsx 22 sheet) + docx giải thích The AI Growth; cross-ref tier-3-technical-advance SOP làm canonical speed/CWV; lớp WHY từ wiki Koray (CoR, Index Pollution, Status Codes, Ranking Signal Consolidation); cập nhật chuẩn hiện hành từ Google docs (CWV/INP 03-2024, GSC Page indexing taxonomy, sitemap 50MB, redirect ≤10 hops, crawl budget gate ~10k trang, JS rendering 3-phase).
