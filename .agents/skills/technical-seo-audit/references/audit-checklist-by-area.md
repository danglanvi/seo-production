# Audit Checklist theo khu vực — technical-seo-audit

Khung xương convert từ **template audit nội bộ** (`raw/guidelines/SEO Audit Template (audit toàn diện) - Update 3.2025.xlsx` — 22 sheet) + **docx giải thích** (`raw/guidelines/Giải thích các phần trong SEO Audit Toàn diện - The AI Growth.docx` — 19 sections), cập nhật chuẩn hiện hành từ Google docs và cross-ref wiki Koray.

Format mỗi item: **Check · Cách kiểm (tool/path) · Tiêu chí ĐẠT · Nguồn · Priority khi fail** (P0 chặn index / P1 crawl waste / P2 CWV / P3 tối ưu nhỏ).

⚠️ Item đánh dấu *(diễn giải)* = phần template "chỉ có trong video" (docx không có logic chẩn đoán đầy đủ) — dựng từ tên item sheet 1 + kiến thức chuẩn, không phải verbatim template.

## Mục lục

1. [Crawl & Log File](#1-crawl--log-file)
2. [Index Coverage](#2-index-coverage)
3. [Redirect & Canonical](#3-redirect--canonical)
4. [Sitemap & Robots.txt](#4-sitemap--robotstxt)
5. [Core Web Vitals & Site Speed](#5-core-web-vitals--site-speed)
6. [JS Rendering](#6-js-rendering)
7. [HTTPS & Mobile](#7-https--mobile)
8. [International / hreflang (optional)](#8-international--hreflang-optional--chỉ-khi-site-đa-ngôn-ngữ)
9. [Cross-area flags (route sang skill anh em)](#9-cross-area-flags-route-sang-skill-anh-em)

---

## 1. Crawl & Log File

Nguồn khung: xlsx sheet1 khối Crawl (13 items) + sheet3 "Log File Audit" (17 bước Screaming Frog Log File Analyser) + docx §1 + tier-3 SOP mục 0+2.

**Gate đầu khu vực:** site < ~10.000 trang unique → crawl budget KHÔNG phải ưu tiên (developers.google.com/crawling/docs/crawl-budget) — chỉ chạy các item hygiene (1.1–1.5), bỏ nhóm budget (1.6–1.9).

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 1.1 | 404 / 410 hygiene | Crawl (Ahrefs issues / SF Response Codes 4xx) + log + **GSC Crawl Stats 404 examples: nhóm theo prefix/folder/tháng** — 404 tụ theo 1 prefix cũ = dấu vân tay **đổi URL structure không 301** (case 10/07: `/product/` cũ vs `/products/` mới, mỗi URL bị crawl lại 10–12 lần); tụ theo tháng uploads = đợt xóa media hàng loạt | Trang xóa vĩnh viễn trả 410 (hoặc 404); trang lỗi có traffic/backlink → 301 về URL liên quan; đổi structure → 301 regex theo prefix; xóa internal link trỏ tới trang lỗi; **xóa khỏi sitemap** | docx §1.0; wiki [[Status Codes]] (Koray: 404→410 >30.000 URL) | P1 |
| 1.2 | Soft 404 | Crawl chéo Screaming Frog vs GSC (trang "not found" nhưng status 200/301/302) | Không có soft 404; trang hết nội dung trả 404/410 thật | docx §1.3; GSC taxonomy "Soft 404" | P1 |
| 1.3 | 5xx & bảo trì | Log + GSC Crawl Stats By response | 5xx ~0%; khi bảo trì trả **503**, không trả 500 | docx §1.5 (John Mueller); tier-3 mục 2.2 | P0 |
| 1.4 | GSC Crawl Stats — Average response time | GSC Settings > Crawl Stats (user cung cấp) | <200ms tốt / <350ms tối thiểu / >500ms cờ đỏ | tier-3 mục 0+2.1 (ngưỡng GTV) | P2 |
| 1.5 | GSC Crawl Stats — By response | GSC Crawl Stats | 200+304 ≥ ~95%; 4xx <1%; 5xx ~0%. ⚠️ 304 cao là TỐT (tiết kiệm budget) — không flag | tier-3 mục 2.2 | P1 |
| 1.6 | GSC Crawl Stats — By file type + By Googlebot type | GSC Crawl Stats | HTML là tỷ trọng "việc thật"; ecom/media chấp nhận Image cao — KHÔNG mặc định là lỗi, đọc theo $SITE_TYPE. ⚠️ JS+CSS cao bất thường (>~30–40%) + 304 thấp = bot tải lại resource mỗi lần → điều tra cache headers + `?ver=` params (case 10/07: 46% JS/CSS, 98% mang ?ver, no-store). Đọc kèm **By Googlebot type**: Page-resource-load + Image lấn át, Smartphone (crawl trang thật) mỏng = crawl inefficiency | tier-3 mục 2.3 | P1 |
| 1.7 | Wasted budget theo directory | Log File Analyser: hits per directory vs giá trị SEO của directory | Bot không dồn hits vào directory không cần index (param, filter, admin) | xlsx sheet3; wiki [[Faceted Navigation]] | P1 |
| 1.8 | Orphan URL | Log File Analyser View "Not in URL Data" (URL có bot hit nhưng không có trong crawl) + Ahrefs pages-by-internal-links = 0 inlink | Không có orphan có giá trị SEO; orphan rác → chặn/gỡ | xlsx sheet3; docx §1 | P1 |
| 1.9 | URL ít được crawl | Log File Analyser: Num Events | URL quan trọng crawl ≥1,5 lần/ngày; dưới ngưỡng → review internal link/sitemap | xlsx sheet3 dòng 10 | P1 |
| 1.10 | Crawl chậm theo log | Log File Analyser: Average Response Time | Không có nhóm URL Average Response Time >3s | xlsx sheet3 dòng 13 | P2 |
| 1.11 | Average Bytes bất thường | Log File Analyser: Average Bytes per URL | Không có URL/directory nặng bất thường kéo băng thông bot | xlsx sheet3 | P3 |
| 1.12 | Spam bots | Log: lọc IP giả Googlebot (verify reverse DNS) | Bot giả bị chặn qua .htaccess/firewall | xlsx sheet3 | P3 |
| 1.13 | Infinitely-expanding URLs | Log + crawl: calendar, filter chồng filter, session param | Không có URL space vô hạn; có → chặn robots.txt | xlsx sheet3; developers.google.com/crawling/docs/crawl-budget | P1 |
| 1.14 | Inconsistent Response | Log: cùng URL trả status khác nhau theo thời gian | Status ổn định; dao động 200↔5xx/302 → điều tra server | xlsx sheet3 | P1 |
| 1.15 | Time-to-index trang mới | Publish → kiểm index (GSC URL Inspection) | 24–48h với authority site; lâu hơn nhiều → cờ CoR cao | tier-3 mục 2.4; wiki [[Cost of Retrieval]] | P1 |
| 1.16 | TTFB | seo-audit-tool `--deep` / PageSpeed / curl timing | <200ms ideal / <800ms min. Lens GEO: <2s = hard timeout fetch ChatGPT, target <700ms (label "reverse-engineered estimate, đơn nguồn") | wiki [[Cost of Retrieval]]; wiki [[GEO]] Gate #2 | P2 |
| 1.17 | AI crawler hits (GEO baseline) | Log: lọc UA theo **bot-purpose matrix** bên dưới (verify IP nếu nghi giả — cross 1.12). ⚠️ Google-Extended KHÔNG có UA riêng trong log (chỉ là robots.txt control token — crawl vẫn bằng UA Google thường; official: developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) | Chấm theo **chiến lược client** (hỏi ở Bước 0): muốn AI visibility → search/user-triggered bots có hits + không bị chặn; muốn opt-out training → 0 hits GPTBot/ClaudeBot là chủ đích, không flag. 🔴 **Training-bot hits (GPTBot/ClaudeBot) KHÔNG phải AI-visibility KPI** — đo visibility bằng search bots (OAI-SearchBot, Claude-SearchBot, PerplexityBot) + user-triggered (ChatGPT-User, Claude-User, Perplexity-User) | wiki [[GEO]]; crawler docs chính chủ OpenAI/Anthropic/Perplexity | P2 (theo chiến lược) |

**Bot-purpose matrix (official crawler docs, 2026-07-13):**

| Provider | Search/discovery | Training | User-triggered |
|---|---|---|---|
| OpenAI | OAI-SearchBot | GPTBot | ChatGPT-User |
| Anthropic | Claude-SearchBot | ClaudeBot | Claude-User |
| Perplexity | PerplexityBot | — (không train từ crawl) | Perplexity-User |
| Google | Googlebot (Search index) | Google-Extended (robots token, không phải crawler riêng; chặn KHÔNG ảnh hưởng Google Search) | tùy agent/product |

Sources: developers.openai.com/api/docs/bots · support.claude.com/en/articles/8896518 · docs.perplexity.ai/docs/resources/perplexity-crawlers · developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers

**WHY (wiki):** crawl budget = băng thông bot phân bổ; hết budget bot sang domain khác → hướng crawler vào content muốn index, loại duplicate (docx §1.0). CoR cao (TTFB >800ms, div soup, JS không SSR fallback) = denominator kéo Topical Authority xuống ([[Cost of Retrieval]]).

---

## 2. Index Coverage

Nguồn khung: sheet1 khối "Google & Entity" (16 items GSC/GA) + sheet3 dòng 7–9 (Index Pollution/Bloat) + wiki [[Index Pollution]] + GSC docs hiện hành.

🔴 **Không bịa trạng thái GSC.** Toàn khu vực này chỉ chấm khi có data thật (GSC export/screenshot user cung cấp, hoặc Ahrefs). Không có → ⬜ THIẾU DATA + hướng dẫn: GSC > Indexing > Pages > Export.

🔴 **Taxonomy hiện hành** (support.google.com/webmasters/answer/7440203) — 2 trạng thái top-level `Indexed` / `Not indexed`; lý do Not indexed thường gặp: Excluded by noindex tag · Crawled – currently not indexed · Discovered – currently not indexed · Soft 404 · Redirect error · Blocked by robots.txt · Duplicate without user-selected canonical · Duplicate, Google chose different canonical than user · Alternate page with proper canonical tag · Not found (404) · Server error (5xx) · Blocked due to unauthorized request (401) · Blocked due to access forbidden (403) · URL blocked due to other 4xx issue · Blocked by page removal tool · Page with redirect. ⚠️ Danh sách không exhaustive — đối chiếu doc Google hiện hành khi chấm. ❌ KHÔNG dùng taxonomy report cũ (Valid/Warning/Error/Excluded).

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 2.1 | Manual action | GSC > Security & Manual Actions (user xác nhận) | Không có manual action | xlsx sheet1 khối Google & Entity | P0 |
| 2.2 | Malware / hacked | sitecheck.sucuri.net (tool template chỉ định) + GSC Security | Sạch | xlsx sheet1 | P0 |
| 2.3 | Not indexed breakdown | GSC Page indexing report | Lý do not-indexed đều giải thích được & chủ đích (noindex chủ động, redirect...); "Crawled/Discovered – currently not indexed" số lượng lớn → điều tra chất lượng + CoR | GSC docs F.1; wiki [[Cost of Retrieval]] | P0–P1 tùy lý do |
| 2.4 | "Blocked by robots.txt" nhưng vẫn indexed | GSC "Indexed, though blocked by robots.txt" | = 0 | wiki [[Robots.txt]] (Koray fix >500 coverage problems) | P0 |
| 2.5 | Index Bloat ước lượng | So `site:domain` vs số URL crawl được vs số URL chủ đích | Chênh lệch nhỏ; index >> crawlable = bloat (param, tag, filter) | xlsx sheet3 dòng 7–9 | P1 |
| 2.6 | Index Pollution | GSC/GA: pages indexed nhưng 0 traffic / 0 CTR / 0 organic keywords nhiều tháng liên tục (Koray verbatim: "haven't produced traffic for months" — không chốt số; ngưỡng operational GTV gợi ý 3–6 tháng, tự đặt, không phải từ wiki) | Không có nhóm lớn; có → playbook: noindex + sửa internal link + canonical đúng | wiki [[Index Pollution]] (Koray case >300 pages removed) | P1 |
| 2.7 | Fix bloat đúng phương pháp | Review kế hoạch fix | Dùng 1 trong 4 methods: 301 rules / 410 / 404 / 301-trước-khi-delete + dọn internal links + validate GSC. ⚠️ Đang rebuild → giữ URL, chỉ đổi content | wiki [[Ranking Signal Consolidation]] | P1 |
| 2.8 | Canonical được Google tôn trọng | GSC "Duplicate, Google chose different canonical" | = 0 hoặc giải thích được. ⚠️ Canonical chỉ là *hint* (2+ năm nay) — không dựa mình canonical để consolidation | wiki [[Index Pollution]]; GSC docs | P1 |
| 2.9 | Noindex side-effect | Trang noindex+dofollow quan trọng | Hiểu rõ: noindex làm giảm crawl rate trên trang đó — không noindex trang hub cần crawl | wiki [[Index Pollution]] | P2 |
| 2.10 | Coverage per khu vực site | Sitemap index theo category → tỷ lệ index per sitemap | Trace được tỷ lệ index từng khu vực; khu vực tỷ lệ thấp → điều tra | docx §2.x; wiki [[Robots.txt]] | P2 |

**Background concept (không thành check item):** [[Index Partition]] — SE chia index thành cluster Triples S-P-O; lý do Topical Authority tăng tốc ranking cho query mới (document đã nằm đúng cluster).

---

## 3. Redirect & Canonical

Nguồn khung: sheet Response (chuỗi Status Code 1→Redirect URI 1→Status Code 2→Redirect URI 2) + sheet Canonicalization (8 items) + docx §14, §17.1.6.

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 3.1 | Redirect chains | SF Reports > Redirect Chains / Ahrefs issues / curl -I -L. ⚠️ **Lọc external share links trước khi đếm** (nút share Zalo/X/FB tạo hàng trăm redirect external trong SF Redirects — không phải redirect nội bộ, tránh báo động giả) | Không chain ≥2 hops; fix A→B→C thành **A→C và B→C**. Googlebot theo tối đa 10 hops — không được lại gần giới hạn | docx §17.1.6; developers.google.com/crawling/docs/troubleshooting/http-status-codes | P1 |
| 3.2 | Redirect loops | Crawl / curl | Không có loop | sheet Response *(diễn giải)* | P0 |
| 3.3 | 302/307 dùng cho permanent | SF Response Codes 3xx | Redirect permanent dùng 301 (= tín hiệu canonical cho target — developers.google.com/search/docs/crawling-indexing/301-redirects). ⚠️ Illyes/Mueller nói 302 không mất PageRank — GTV vẫn khuyến nghị đổi 301; 302 chỉ giữ cho tạm thời thật (hết hàng) | docx §14.1.1, §1.0; wiki [[Status Codes]] (Koray: 302/307→301 >1.500) | P1 |
| 3.4 | 9 biến thể URL homepage | curl từng biến thể: www/non-www × http/https, /index.html, hoa-thường, trailing param | Tất cả 301 về đúng 1 phiên bản canonical; **ưu tiên 301 hơn canonical tag** | docx §14 | P0 |
| 3.5 | Self-referential canonical | seo-audit-tool Layer 1 (wrap) / SF Directives > Canonicalised | Mọi trang indexable có canonical trỏ về chính nó | docx §14; sheet Canonicalization | P1 |
| 3.6 | Canonical trỏ chéo sai | SF: canonical ≠ URL và target không hợp lý (non-200, noindex, redirect). Pattern phổ biến: **pagination canonical về trang 1** (`/page/N/` → trang 1, setting sai của Rank Math/Yoast) — báo Google "trang N là bản sao trang 1", sản phẩm nằm sâu pagination chỉ còn đường sitemap; kéo theo duplicate title hàng loạt. Fix: page/N self-canonical + title đuôi "– Trang N" | Canonical target là trang 200, indexable; pagination self-canonical | sheet Canonicalization *(diễn giải)*; case 10/07/2026 | P0 (P1 với pagination) |
| 3.7 | Parameter URLs (ecommerce) | Crawl filter URL có `?`; so demand | Filter không mong muốn → disallow robots.txt khi quy mô lớn; chỉ để index combination có search demand. Case Annie Cushing: 5,8M trang index → 37k có traffic (0,6%) → 645 tạo doanh thu (0,01%) | docx §14; wiki [[Faceted Navigation]] | P1 |
| 3.8 | Trang conversion/thank-you bị index | site: + crawl | Thank-you, cart, checkout, kết quả search nội bộ: noindex | sheet Canonicalization *(diễn giải)* | P1 |
| 3.9 | Internal link trỏ vào redirect/404 | SF / Ahrefs issues; sheet Internal link + Architecture (broken internal link) | Internal link trỏ thẳng URL 200 cuối cùng | xlsx sheet Internal link, Architecture; docx §17 | P1 |

---

## 4. Sitemap & Robots.txt

Nguồn khung: sheet1 Sitemap (11 items) + Robots.txt (6 items) + sheet Site maps + sheet Robot.txt (worksheet) + docx §2, §3 + tier-3 SOP mục 8 (8 items) & mục 9 (5 items).

### Sitemap

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 4.1 | 100% URL trong sitemap trả 200 | SF Mode List upload sitemap | Không có non-200 ("Bing chỉ chịu 1% dirt" — docx §2); trang lỗi phải gỡ khỏi sitemap | docx §2, §1.0; xlsx sheet Site maps | P1 |
| 4.2 | URL sitemap self-canonical | SF List mode + canonical check | Mọi URL trong sitemap canonical về chính nó | docx §2.x | P1 |
| 4.3 | Không có noindex/robots-blocked trong sitemap | SF List mode + Directives | 0 URL noindex hoặc bị robots chặn nằm trong sitemap | docx §2.x; xlsx sheet Site maps (blocked pages) | P1 |
| 4.4 | Giới hạn kích thước | Đếm URL/dung lượng file | ≤50.000 URL / **≤50MB** (uncompressed) mỗi file; lớn hơn → sitemap index. ⚠️ Template ghi 10MB = số cũ, dùng 50MB | developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap; tier-3 mục 8 | P2 |
| 4.5 | Sitemap index theo category | Xem cấu trúc sitemap_index.xml | Chia theo khu vực content để trace tỷ lệ index per khu vực | docx §2.x; wiki [[Robots.txt]] | P2 |
| 4.6 | Không có PPC/landing tạm trong sitemap | Review URL list | PPC pages, orphaned pages chủ đích không nằm trong sitemap | xlsx sheet Site maps | P2 |
| 4.7 | Sitemap khai báo trong robots.txt + submit GSC | Đọc /robots.txt + GSC Sitemaps | Có dòng `Sitemap:`; GSC đã submit, status Success | docx §3; tier-3 mục 8 | P2 |

### Robots.txt

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 4.8 | Vị trí & tồn tại | curl domain/robots.txt | File ở root, trả 200 | docx §3 | P0 |
| 4.9 | Không chặn nhầm khu vực cần index | Đọc từng Disallow, đối chiếu GSC | Không có Disallow đè lên content SEO. 🔴 Case "in ấn catalog" (docx §3.0): lệnh delay-bot giam từ khóa ngoài top 100, gỡ → top 8 trong 3 ngày | docx §3.0 | P0 |
| 4.10 | Không dùng robots.txt thay noindex | Đối chiếu mục đích từng rule | Trang cần loại khỏi index → noindex (Google có thể vẫn index URL bị chặn nếu có link — Mueller, docx §3.6). Robots.txt = crawl control, noindex = index control. ❌ Không block duplicate bằng robots.txt khi cần consolidation | docx §3.6; wiki [[Ranking Signal Consolidation]] | P0 |
| 4.11 | Không chặn CSS/JS | Đọc rules + GSC URL Inspection render | CSS/JS render được (`Allow: .js`, `Allow: .css` — Gary Illyes) | docx §3.4 | P0 |
| 4.12 | Disallow rác chủ đích | Review rules | Third-party JS không cần + affiliate pages + filter không demand → disallow | wiki [[Robots.txt]]; wiki [[Faceted Navigation]] | P2 |
| 4.13 | AI bot access chủ đích | Đọc robots.txt rules per bot: GPTBot, OAI-SearchBot, Google-Extended, ClaudeBot, PerplexityBot | Allow/Disallow **khớp chiến lược client** (hỏi ở Bước 0, không giả định): muốn AI citation → không chặn OAI-SearchBot/PerplexityBot/ClaudeBot; muốn opt-out training → chặn GPTBot/Google-Extended là chủ đích, không phải lỗi. ❌ llms.txt KHÔNG phải item kiểm tra — không bot nào request (wiki GEO; Mueller so sánh keywords meta tag) | wiki [[GEO]]; guardrail thống nhất `geo-content-optimization` | P1 nếu chặn ngược chiến lược |

---

## 5. Core Web Vitals & Site Speed

🔴 **Canonical cho khu vực này = `sop/06-self-checklist/tier-3-technical-advance.md` mục 3–5** (bản operational của sheet "2. Checklist technical advance", 51 dòng Koray-based case encazip.com, đã fix FID→INP và Server Push→preload). Bảng dưới là tóm tắt để chấm — chi tiết tiêu chí đọc SOP, KHÔNG duy trì 2 bản.

Data: seo-audit-tool `--deep` (PageSpeed API) — WRAP, không chấm lại; Path C → PageSpeed Insights công khai.

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 5.1 | LCP | PageSpeed API (`--deep`), 75th %ile, tách mobile/desktop | good ≤2,5s (poor >4,0s) | https://web.dev/articles/vitals; tier-3 mục 5 | P2 |
| 5.2 | INP | như trên | good ≤200ms (poor >500ms). ⚠️ INP thay FID chính thức 03/2024 — template ghi FID = legacy | web.dev/articles/vitals; tier-3 mục 5 | P2 |
| 5.3 | CLS | như trên | good ≤0,1 (poor >0,25) | web.dev/articles/vitals | P2 |
| 5.4 | HTML size & minify | View-source / seo-audit-tool | Tham chiếu Koray ~15KB/trang minified; HTML normalization, không inline rác | xlsx sheet2 A5; tier-3 mục 3.1 | P3 |
| 5.5 | DOM size | Lighthouse/PageSpeed | <1.500 nodes | xlsx sheet2 A30; tier-3 mục 4.3 | P2 |
| 5.6 | Nén & giao thức | Response headers | Brotli enabled; HTTP/2. ⚠️ HTTP/2 Server Push đã deprecated → dùng preload (tier-3 đã sửa) | xlsx sheet2; tier-3 mục 3–4 | P3 |
| 5.7 | Resource load order | View-source đầu trang | Critical CSS trong 1460 bytes đầu; preload/preconnect cho critical, defer/async cho non-critical; CSS/JS refactor theo template (headfoot.css/homepage.css/subpage.css) + cache theo template | xlsx sheet2; tier-3 mục 3 | P3 |
| 5.8 | Fonts | Devtools/headers — **4 câu bắt 80% vấn đề**: (1) đếm font files + format (TTF/Woff cũ?), (2) đã Woff2 chưa?, (3) có preload font của LCP element/heading không?, (4) `font-display` set chưa? | Woff2 (+variable fonts); ≤5 files (>5 = flag, >15 = TTI impact rõ — HTTPArchive); preload font LCP; xử lý FOUT/FOIT | wiki [[Font File Optimization]]; xlsx sheet2; tier-3 mục 4 | P3 |
| 5.9 | Browser caching | Response headers. 🔴 **Check 30 giây — chữ ký PHP session giết cache**: `curl -sI <homepage>` thấy bộ 3 `PHPSESSID` cookie + `Expires: Thu, 19 Nov 1981` + `Cache-Control: no-store, no-cache, must-revalidate` = một plugin/theme gọi `session_start()` mọi request → PHP tự phát header chống-cache → LiteSpeed/page cache bypass toàn bộ. Nghi phạm WooCommerce thường gặp: YITH Compare/Wishlist, review plugins, theme custom (grep `session_start` trong plugins+theme). Root cause phổ biến của avg response time cao | cache-control/ETag đặt đúng cho static assets; HTML cacheable cho guest; hết chữ ký session → bật page cache (LiteSpeed Cache nếu server LiteSpeed) | xlsx sheet2; tier-3 mục 4; case chanlongpickleball 10/07/2026 (937ms → roadmap <350ms) | P3 (P1 nếu dính chữ ký session) |
| 5.10 | Ảnh (khía cạnh speed) | Crawl Images + PageSpeed | AVIF/định dạng mới, lazy-load bằng Intersection Observer, srcset, ảnh ~600px, IPTC thay EXIF. Ảnh nặng: template flag >100KB, chuẩn P20 onpage (sop/08) là <150KB → **>150KB = ❌ FAIL, 100–150KB = ⚠️ CẦN XEM** (xem Bảng ngưỡng SKILL.md). Filename/alt/caption → route `image-seo-optimize` | xlsx sheet2, sheet1 A42, sheet12; docx §5.2 | P3 |

❌ **Legacy KHÔNG chấm:** trang ≤35KB, load >20s, GTMetrix <1,7s, PageSpeed score >80, FID, AMP (xlsx sheet1/16 + docx §7) — ghi trong report là "legacy — thay bằng CWV hiện hành".

---

## 6. JS Rendering

Nguồn: developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics (updated 03/2026) + wiki [[Cost of Retrieval]]. Data: seo-audit-tool `--render` (Playwright) so raw HTML vs rendered DOM.

Mô hình nền: Google xử lý JS qua 3 phase **Crawling → Rendering → Indexing**; render bằng headless evergreen Chromium, page vào render queue ("vài giây tới lâu hơn").

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 6.1 | Resource JS/CSS không bị robots chặn | robots.txt + GSC URL Inspection | Bị chặn = không render được → content JS invisible | Google JS SEO basics | P0 |
| 6.2 | Link là `<a href>` thật | View rendered DOM | Navigation dùng `<a href>`; fragment `#` không được Googlebot resolve; SPA dùng History API | Google JS SEO basics | P0 |
| 6.3 | SPA soft 404 | Route không tồn tại → xem status | JS redirect về URL trả 404 thật, hoặc inject `noindex` — không trả 200 với trang "không tìm thấy" | Google JS SEO basics | P1 |
| 6.4 | Canonical trong HTML gốc | View-source vs rendered | Canonical đặt trong raw HTML (inject bằng JS được đọc lúc render nhưng không ưu tiên) | Google JS SEO basics | P1 |
| 6.5 | Raw vs rendered delta | seo-audit-tool `--render` (cần Playwright — cài 1 lần) hoặc SF JS-rendering crawl (Path B) hoặc Firecrawl MCP (rendered) so `curl` (raw) | Delta nhỏ — content chính (title, heading, body) có trong raw HTML; delta lớn = CoR cao **và rủi ro vô hình với AI engines** (`observational`: đa số AI crawler được quan sát fetch raw HTML, không render JS như Googlebot; vendor docs OpenAI/Anthropic/Perplexity KHÔNG công bố khả năng render — không trình bày như hard fact phổ quát, năng lực có thể đổi) | wiki [[Cost of Retrieval]] (Measurement Proxies); wiki [[GEO]] | P1 |
| 6.6 | SSR / pre-rendering | Kiến trúc site | Site JS-heavy nên có SSR/pre-render — không phải bot nào cũng chạy JS. ⚠️ Dynamic rendering = workaround, không phải giải pháp lâu dài | Google JS SEO basics; developers.google.com/…/dynamic-rendering | P2 |
| 6.7 | Caching fingerprint | Build config | WRS có thể bỏ qua caching headers → dùng content fingerprinting cho file JS/CSS versioned | Google JS SEO basics | P3 |
| 6.8 | Infinite scroll | UX kiểm tay | Có pagination fallback (`<a href>` trang tiếp) — infinite scroll thuần = high CoR pattern | wiki [[Cost of Retrieval]] | P1 |

---

## 7. HTTPS & Mobile

Nguồn: sheet1 khối "Dịch chuyển HTTPS" (12 items) + Mobile (24 items, đã lọc legacy) + docx §10, §12 + tier-3 SOP mục 7.

### HTTPS

Nguyên tắc nền: **http và https = 2 entity riêng với Google** (docx §12) — mọi cấu hình phải làm lại cho property https.

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 7.1 | Force HTTPS toàn site | curl http:// biến thể | 301 về https; không mixed content | docx §12; tier-3 mục 7 | P0 |
| 7.2 | robots.txt cho https | curl | Property https có robots.txt riêng đúng | docx §12 | P1 |
| 7.3 | Disavow submit lại | GSC (user xác nhận) | File disavow đã submit cho property https (nếu từng có) | docx §12 | P2 |
| 7.4 | Sitemap submit lại + GSC property riêng | GSC | Sitemap https đã submit; property https tồn tại | docx §12 | P1 |
| 7.5 | hreflang update sau HTTPS | Kiểm thẻ hreflang | hreflang trỏ URL https | docx §12 | P2 |
| 7.6 | Chứng chỉ & HSTS + các item còn lại | tier-3 mục 7 (12 items) | Theo checklist SOP — cross-ref, không viết lại | tier-3 mục 7 | P2 |

### Mobile

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 7.7 | Viewport & responsive | View-source + devtools | Có meta viewport; layout responsive | xlsx sheet1 Mobile *(diễn giải)* | P1 |
| 7.8 | Content parity mobile/desktop | So rendered DOM 2 user-agent | Mobile-first indexing: content/structured data/meta trên mobile đủ như desktop | xlsx sheet1 Mobile *(diễn giải)* | P1 |
| 7.9 | CWV mobile riêng | PageSpeed API tách mobile | Chấm CWV theo mobile 75th %ile (mục 5) — mobile thường tệ hơn desktop | web.dev/articles/vitals | P2 |
| 7.10 | Tap targets / font size / interstitials | Lighthouse | Không lỗi usability lớn | xlsx sheet1 Mobile *(diễn giải)* | P3 |

❌ **Legacy KHÔNG chấm:** Mobile-Friendly Test tool (đã ngừng — ghi "legacy, dùng Lighthouse/CWV thay thế", không kèm ngưỡng bịa), AMP.

---

## 8. International / hreflang (optional — chỉ khi site đa ngôn ngữ)

Nguồn: sheet1 International (13 items) + docx §11 (note "skip nếu không đa ngôn ngữ") + tier-3 SOP mục 10 (9 items — canonical, cross-ref không viết lại) + wiki [[Hreflang PageRank Sharing]] + [[syntheses/Multilingual SEO]].

**Gate khu vực (WHY):** hreflang thiếu KHÔNG mặc định là lỗi. [[Hreflang PageRank Sharing]] (Koray, non-official claim): hreflang chia sẻ PageRank + historical data **2 chiều** — alternate kém chất lượng kéo canonical xuống. Delay hreflang chủ đích khi alternates chưa mature là hợp lệ (case Getwordly: gắn sau 60 ngày → +100% traffic các nước khác trong 2,5 ngày). → Hỏi user về độ trưởng thành của alternates trước khi flag ❌.

| # | Check | Cách kiểm | Tiêu chí ĐẠT | Nguồn | Priority fail |
|---|---|---|---|---|---|
| 8.1 | hreflang return tags | Crawl hreflang / Ahrefs issues | Mọi cặp có return tag 2 chiều | tier-3 mục 10 | P1 |
| 8.2 | x-default | Kiểm thẻ | Có x-default cho selector/trang mặc định | tier-3 mục 10 | P2 |
| 8.3 | hreflang khớp canonical + status 200 | Crawl | hreflang trỏ URL 200, self-canonical | tier-3 mục 10 | P1 |
| 8.4 | Các item còn lại | tier-3 mục 10 | Theo 9 items SOP | tier-3 mục 10 | P2 |
| 8.5 | Symmetry & consistency giữa language sections | So sánh các section ngôn ngữ: internal links/anchor, số URL, design/layout/brand, content profile | 4 nguyên tắc: **symmetry** (links/anchors/lượng content) · **consistency** (design/brand identity) · **matching** (content profile, heading-text pairs, URL count) · **prioritization** (canonical version + popular language được ưu tiên) | [[syntheses/Multilingual SEO]] | P2 |

---

## 9. Cross-area flags (route sang skill anh em)

Phát hiện trong lúc audit nhưng KHÔNG fix trong skill này — flag + route:

| Phát hiện | Evidence khu vực | Route |
|---|---|---|
| Schema lỗi/thiếu (sheet Semantic Markup, 3 items) | seo-audit-tool Layer 1 schema presence | → `schema-markup-generator` |
| HTML không semantic (div soup, thiếu main/article) | Khu vực 5 (DOM) + [[Cost of Retrieval]] | → `semantic-html-optimization` |
| Ảnh thiếu filename/alt/caption chuẩn hàng loạt | SF Images Missing Alt; sheet12 | → `image-seo-optimize` |
| Duplicate title/meta/H1/H2 site-wide | SF Page Titles/Meta duplicate; sheet15. Đây là tín hiệu duplicate content + cannibalization (docx §9) | → evidence cho `/seo-topical-map` (Ranking Signal Dilution ≠ Keyword Cannibalization — wiki [[Ranking Signal Consolidation]]) |
| Trang thin/duplicate content (sheet 5, 13) | Chỉ flag index status (bloat) | → `/seo-onpage` + semantic-content-audit |
| Backlink độc / disavow (sheet 4, 19) | NGOÀI SCOPE hoàn toàn | → `backlink-research` + `backlink-plan` |
| Internal link: menu 5×5, trang >100 outlinks (tín hiệu spam, không còn phạt cứng — docx §17.1.3–4), category thiếu IL | Sheet Internal link | → `internal-linking` |
| Page type thiếu functional component khớp source context (calculator page không có calculator thật, consultancy không có form/CTA) | Khu vực 6/HTML — [[HTML Normalization]]: SE đọc input elements làm conversion signal ([[Website Functions]] US20150234930A1) | → `semantic-html-optimization` |
| Content-level GEO: chunk retrievability, answer-first, AX1-AX5, rewrite cho AI citation | Khu vực 1.17/4.13/6.5 chỉ đo tầng site (bot access, log, render) | → `geo-content-optimization` |
