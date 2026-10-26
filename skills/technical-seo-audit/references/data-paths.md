# Data Paths — technical-seo-audit

Map 3 đường lấy data cho audit. Chọn theo tình huống: project Ahrefs/Semrush có sẵn → Path A cho nhanh; cần crawl tươi/sâu toàn site → Path B (engine chính); không có gì → Path C. Report luôn ghi rõ path đã dùng + ngày lấy data. Path C luôn là đường lùi cuối — skill chạy được không cần MCP.

## Mục lục

1. [Path A — Ahrefs Site Audit MCP + seo-audit-tool](#path-a--ahrefs-site-audit-mcp--seo-audit-tool)
2. [Path B — Screaming Frog CLI headless (tự động)](#path-b--screaming-frog-cli-headless-tự-động--engine-crawl-chính)
3. [Path C — Manual, chỉ có URL](#path-c--manual-chỉ-có-url)
4. [Data user luôn phải cung cấp (mọi path)](#data-user-luôn-phải-cung-cấp-mọi-path)

---

## Path A — Ahrefs Site Audit MCP + seo-audit-tool

**Điều kiện:** site có project trong Ahrefs Site Audit + workspace chạy được `tools/seo-audit-tool`.

🔴 Trước khi gọi: báo user số call dự kiến (~3–6 MCP call + 1 lần chạy tool), chờ xác nhận (Bước 0 SKILL.md).

### Ahrefs MCP tools

| Tool | Dùng để | Map vào khu vực |
|---|---|---|
| `site-audit-projects` | Liệt kê project, xác nhận $TARGET có project + lấy project ID, ngày crawl gần nhất | Bước 0 |
| `site-audit-issues` | Danh sách issue toàn site theo loại (4xx/5xx, redirect chains, canonical, sitemap, hreflang, noindex conflict…) | Phân loại issue → khu vực 1, 3, 4, 8 |
| `site-audit-page-explorer` | Drill danh sách URL theo filter (vd tất cả URL 302, URL canonical sai, URL trong sitemap non-200) | Evidence per finding — lấy URL mẫu cho fix list |
| `site-audit-page-content` | Xem nội dung crawl của 1 page cụ thể | Verify case lẻ (canonical trong HTML, noindex) |
| `site-explorer-crawled-pages` *(phụ trợ)* | Pages Google/Ahrefs thấy — so với sitemap để tìm orphan/bloat | Khu vực 1.8, 2.5 |
| `site-explorer-pages-by-internal-links` *(phụ trợ)* | URL inlinks = 0 (orphan) hoặc outlinks >100 | Khu vực 1.8; cross-flag internal-linking |

⚠️ Ahrefs `gsc-*` tools (gsc-pages, gsc-keywords…) có trong MCP nhưng **chưa verify có coverage/crawl-stats** — không dùng thay GSC Page indexing/Crawl Stats khi chưa test; 2 report đó vẫn xin từ user.

**Path A-alt (Semrush):** client có project Semrush Site Audit → dùng MCP `Semrush siteaudit_research` thay/bổ sung Ahrefs. Khi 2 nguồn lệch nhau → ghi cả 2 + cross-check bằng SF crawl (Path B) hoặc curl.

### seo-audit-tool (URL-level — WRAP)

```bash
cd "tools/seo-audit-tool"
npm run audit -- <URL> --keyword <kw> --deep [--render] [--json]
```

| Flag | Khi nào | Cho khu vực |
|---|---|---|
| (mặc định, Layer 1) | Luôn — ~30 check deterministic: meta lengths, heading tree, links, ảnh, schema presence, canonical (<10s, 0đ) | Khu vực 3.5 (canonical), cross-flags mục 9 checklist. 🔴 KHÔNG tự chấm lại các check này |
| `--deep` | Luôn cho audit này | **PageSpeed API → CWV (T3-P3)** cho khu vực 5 + DataForSEO SERP. Key: `PAGESPEED_API_KEY` trong `.agent-secrets/.env` (đã cấu hình 10/07/2026, 25k req/ngày — keyless dùng pool chung, hay cạn quota). ⚠️ Site ít traffic không có CrUX field data → chấm bằng **lab, ghi rõ nguồn**; TTFB lab (Lighthouse "root document") thường thấp ảo — nguồn TTFB chuẩn = GSC avg response time + `curl -w time_starttransfer` ×3–5 lần |
| `--render` | Trang JS-heavy (SPA, framework). ⚠️ Cần Playwright — CHƯA cài sẵn, setup 1 lần: `npm i playwright && npx playwright install chromium` (trong tools/seo-audit-tool). Site-level JS delta đã có SF JS-rendering (Path B); không cài gì → fallback Firecrawl MCP (rendered) so `curl` (raw) | Khu vực 6 — so raw HTML vs rendered DOM |
| `--skip-llm` | Audit technical thuần, không cần rubric content | Tiết kiệm — Layer 2 LLM rubric không cần cho skill này |
| `--json` | Luôn — để parse | Mọi khu vực |

**Chọn URL đại diện (3–5 URL):** homepage + 1 category/hub + 1 bài viết + 1 product (nếu ecom) + 1 trang nghi vấn JS-heavy. Tool ở tầng URL — kết luận site-level chỉ khi pattern lặp trên nhiều URL đại diện.

**Giới hạn tool:** Blur Test / Centerpiece cần screenshot = manual — ngoài scope skill này (thuộc onpage/visual).

### Map field JSON → khu vực

| Nhóm field output | Khu vực |
|---|---|
| `canonical`, `meta_robots` | 2, 3 |
| `cwv` / PageSpeed metrics (LCP/INP/CLS, TTFB) | 5; TTFB → 1.16 |
| `schema` presence | Cross-flag → schema-markup-generator |
| `links` (broken, redirect target) | 3.9 |
| `images` (size, alt) | 5.10; cross-flag → image-seo-optimize |
| rendered delta (khi `--render`) | 6.5 |

---

## Path B — Screaming Frog CLI headless (tự động — engine crawl chính)

**Điều kiện:** máy có SF + license active. Bản đã chạy thật: **SF 24.3** trên máy chạy audit (18/10/2026, 2.023 URL trong 3 phút); bản 23.3 chạy từ 07/2026. Binary CLI tại `/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher`. Claude TỰ chạy crawl + parse — user không cần export tay.

**Lệnh đã chạy thật 18/10/2026 (SF 24.3, config mặc định):**

```bash
"$SF" --headless --crawl https://<domain>/ --save-crawl --output-folder <folder> --overwrite \
  --export-tabs "Internal:All,Response Codes:Internal Client Error (4xx),Response Codes:Internal Server Error (5xx),Response Codes:Internal Redirection (3xx),Response Codes:Internal Redirect Chain,Response Codes:External Client Error (4xx),Page Titles:Over X Pixels,Meta Description:Over X Pixels,H1:Missing,Images:Missing Alt Text,Images:Missing Size Attributes,Canonicals:Non-Indexable Canonical,Directives:Noindex,Links:Internal Nofollow Outlinks,Content:Soft 404 Pages,Sitemaps:Orphan URLs,Structured Data:Validation Errors,Validation:Multiple <head> Tags" \
  --bulk-export "Response Codes:Internal & External:Client Error (4xx) Inlinks,Response Codes:Internal & External:Redirection (3xx) Inlinks,Images:Images Missing Alt Text Inlinks"
```

- Tên tab hợp lệ: `"$SF" --help export-tabs`, `--help bulk-export`, `--help save-report`.
- Hai file bulk export inlinks 3xx/4xx là input của Bước 3c (`link_sources.py summarize`).
- Config crawl `.seospiderconfig` là Java serialization: không sửa bằng script. Embeddings, semantic similarity, AI prompt, Store HTML và crawl analysis tự động phải bật trong GUI, `File > Configuration > Save As`, rồi truyền `--config`. Config mặc định chạy headless không có Link Score và Near Duplicates.
- Licence nằm ở `~/.ScreamingFrogSEOSpider/licence.txt`. Không in licence ra log.

### Bẫy khi chạy headless (SF 24.3, 18/10/2026)

- Kiểm bản cài: `/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "/Applications/Screaming Frog SEO Spider.app/Contents/Info.plist"`.
- Kiểm licence: so hash của `licence.txt` với hash của licence người vận hành đưa. Không in key.
- Không đọc, `grep`, `cat` hay `strings` thư mục `~/.ScreamingFrogSEOSpider/` (prefs, config). Thư mục này giữ token API của connector. Lọc `grep -v token` không đủ: ngày 18/10, một lệnh đọc cấu hình SF đã in token Ahrefs ra output.
- Headless không chạy Crawl Analysis, nên Link Score trống. Thêm `Links:All Inlinks` vào `--bulk-export` (tên đã chạy thật trên SF 24.3), rồi tính PageRank nội bộ:

  ```bash
  python3 skills/technical-seo-audit/scripts/pagerank.py --internal <folder>/internal_all.csv \
    --inlinks <folder>/all_inlinks.csv --out <folder>/pagerank_internal.tsv
  ```

  Báo cáo ghi bộ lọc nút (HTML 200 Indexable) và số nút cạnh hạng PageRank. Lấy hạng từ file đã lưu, không từ lượt tính tạm. Ngày 18/10, lượt tính tạm dùng 389 trang HTML, còn file lưu có 357 trang index được.
- macOS không có lệnh `timeout`. Giới hạn thời gian bằng `perl -e 'alarm N; exec @ARGV' <lệnh>`, hoặc chạy nền.

### Setup một lần (3 bước — user làm trong GUI)

1. **License**: Licence > Enter Licence (headless CLI yêu cầu license active).
2. **API Access**: nối Google account (Search Console — crawl kéo được cả URL Inspection data) + PageSpeed key (free, 25k req/ngày). CLI gọi lại bằng `--use-google-search-console "<account>" "<property>"` và `--use-pagespeed`.
3. **Config chuẩn**: bật JS rendering (khu vực 6), structured data validation, database storage mode (site lớn), speed limit lịch sự với server → Config > Save As `gtv-technical-audit.seospiderconfig`.

### Lệnh chuẩn

```bash
SF="/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher"
caffeinate -i "$SF" --crawl https://client.vn --headless \
  --config <path/gtv-technical-audit.seospiderconfig> \
  --output-folder <folder> --timestamped-output --export-format csv --save-crawl \
  --export-tabs "Internal:All,Response Codes:Redirection (3xx),Response Codes:Client Error (4xx),Response Codes:Server Error (5xx),Canonicals:All,Directives:All,Hreflang:All,Page Titles:All,Images:All" \
  --save-report "Crawl Overview,Redirects:All Redirects,Canonicals:Canonical Chains,Orphan Pages"
```

**Vận hành:**
- 🔴 **Mặc định FULL crawl — KHÔNG đặt giới hạn URL** trừ khi user yêu cầu (quyết định Vincent 07/2026). Trước khi chạy: báo scope + tốc độ + ước tính thời gian, chờ xác nhận (Bước 0 SKILL.md — crawl chạm server thật).
- 🔴 **Tốc độ mặc định: 2 threads / 2–3 URL/giây** (đặt trong config profile). Bài học 10/07/2026 (site khách shared hosting): SF default 5 threads chạy 31 URL/s → shared hosting LiteSpeed VN chặn kết nối hàng loạt ở 29% crawl; crawl GUI cùng ngày cũng dính 64% Connection Timeout. Shared hosting VN rate-limit crawler là PHỔ BIẾN — chậm mà xong hơn nhanh mà gãy (~3.400 URL @ 3 URL/s ≈ 20 phút).
- **Dấu hiệu bị server chặn giữa crawl:** log SF flood `ConnectException`/`Connection Timeout` trên mọi worker cùng lúc → queue còn lại chết nhanh → SF exit 0 nhưng output folder RỖNG (kèm Derby "No current connection"). Xử lý: đợi server hồi (vài phút — verify bằng curl), giảm tốc độ, chạy lại.
- 🔴 **Completeness check sau mọi crawl/export** (kể cả crawl user đưa): đếm `Status Code = 0` trong response_codes (SF status: Connection Timeout / Blocked by robots.txt / No Response). Timeout % cao = crawl KHÔNG hoàn chỉnh → mọi kết luận đếm được (orphan, số ảnh, duplicate) phải ghi caveat "**cận dưới**", không phát biểu như số cuối.
- Chạy **nền** (background) + bọc `caffeinate -i` chống máy sleep. Trong lúc crawl: làm các khu vực không cần crawl (curl, robots, sitemap, PSI, log).
- Site lớn → database storage mode, chạy qua đêm theo **2 nhịp**: nhịp 1 = setup + bấm crawl + audit phần không cần crawl; nhịp 2 = parse CSV + report. SF là tiến trình OS độc lập — phiên Claude đóng không ảnh hưởng crawl; CSV nằm trong folder timestamped, phiên sau nhặt lên làm tiếp.
- Tên export trong lệnh chuẩn trên **đã verify chạy thật trên SF v23.3 (10/07/2026)** — sai tên khác SF validate lúc khởi động và báo lỗi ngay, đối chiếu menu Bulk Export/Reports để sửa.
- Parse CSV bằng script (DuckDB/awk/pandas) — không đọc thô từng dòng. ⚠️ Khi đọc `redirects.csv`: **lọc external share links trước khi đếm** (nút share Zalo/X/Facebook tạo hàng trăm redirect external — không phải redirect nội bộ, đừng báo động "422 redirect").
- Crawl sitemap riêng (nhanh): `--crawl-sitemap <sitemap_url>` cho khu vực 4; list mode: `--crawl-list <file>`.

### Path B-file — user tự crawl GUI, Claude load file (verified 10/07/2026)

User crawl bằng GUI (hoặc có file `.seospider`/`.dbseospider` sẵn) → CLI load + export, **KHÔNG đụng server**:

```bash
"$SF" --load-crawl "<path/crawl-file.dbseospider>" --headless \
  --output-folder <folder> --timestamped-output --export-format csv \
  --export-tabs "Internal:All,Response Codes:All,Page Titles:All,Meta Description:All,Canonicals:All,Directives:All,Hreflang:All,Images:All,H1:All" \
  --save-report "Crawl Overview,Redirects:All Redirects,Canonicals:Canonical Chains,Orphan Pages"
```

Nhanh (~1 phút cho site nhỏ), an toàn tuyệt đối với server — ưu tiên đường này khi user đã có crawl. Vẫn chạy completeness check ở trên (crawl GUI cũng có thể thiếu do timeout).

### Map export → khu vực (dùng cho cả CLI tự động lẫn B-manual)

| Khu vực | SF export / filter | Cột lấy |
|---|---|---|
| 1. Crawl | Response Codes → filter 3xx/4xx/5xx | URL, Status Code, Redirect URI (chuỗi Status Code 1→Redirect URI 1→Status Code 2→Redirect URI 2 — format sheet Response) |
| 1. Log File | **SF Log File Analyser**: Num Events · Average Bytes · Average Response Time · View "Not in URL Data" (orphan) | Per URL/directory; ngưỡng: crawl <1,5 lần/ngày (sheet3 dòng 10), response >3s (sheet3 dòng 13) |
| 2. Index | Directives → Noindex; so crawl list vs `site:` vs GSC export | URL, Meta Robots, X-Robots-Tag |
| 3. Redirect & Canonical | Reports > Redirect Chains; Directives > Canonicalised | URL, Chain length, Canonical Link Element, Canonical target status |
| 4. Sitemap | **Mode List** upload sitemap.xml → crawl | Status Code (non-200 in sitemap), Indexability, Canonical |
| 4. Robots | Response Codes → Blocked by Robots.txt | URL bị chặn — đối chiếu chủ đích |
| 5. Speed/Ảnh | Images tab → over 100KB + Missing Alt Text | URL ảnh, Size, Alt (alt → cross-flag image-seo-optimize) |
| 6. JS Rendering | Config: JavaScript rendering mode → so 2 crawl (text-only vs JS) | Word Count delta, link delta |
| 7. Meta (cross-flag) | Page Titles → Missing/Duplicate/Over 65 Characters; Meta Description → Missing/Duplicate; H1/H2 → Missing/Multiple | URL + giá trị (sheet15; docx §9 — evidence cannibalization) |
| Internal link (cross-flag) | Internal tab; Inlinks = 0; Outlinks >100 | URL, Inlinks, Outlinks, Word Count |

### Path B-manual (fallback)

SF nằm trên máy khác / user đã có crawl sẵn → đưa user danh sách export theo bảng trên (ground truth: cột worksheet xlsx sheet 8–22 + docx), nhận CSV/paste rồi phân loại.

⚠️ CSV lớn (chỉ B-manual): yêu cầu user lọc trước theo filter trên thay vì paste toàn bộ crawl. CLI tự động không cần — parse bằng script.

---

## Path C — Manual, chỉ có URL

**Điều kiện:** không có tool nào. Coverage thấp nhất — report phải ghi rõ giới hạn. Chạy trên URL đại diện (như Path A).

### Checklist lệnh

```bash
# Status + redirect chain (đếm hops, xem 301 vs 302)
curl -sIL -o /dev/null -w '%{http_code} %{redirect_url}\n' <URL>
curl -sIL <URL> | grep -iE '^(HTTP|location|cache-control|etag|content-encoding)'

# 9 biến thể homepage (khu vực 3.4) — www/non-www × http/https, /index.html (cả hoa-thường), uppercase host, trailing slash, param
# (đổi index.html theo stack site: index.php, home…)
for u in "http://domain.vn" "http://www.domain.vn" "https://domain.vn" "https://www.domain.vn" \
         "https://domain.vn/index.html" "https://domain.vn/Index.html" "https://DOMAIN.VN" \
         "https://www.domain.vn/" "https://domain.vn/?ref=test"; do
  curl -sI -o /dev/null -w "$u → %{http_code} %{redirect_url}\n" "$u"; done

# Robots + sitemap
curl -s https://domain.vn/robots.txt
curl -s https://domain.vn/sitemap.xml | head -50
```

### Kiểm tay

| Việc | Cách | Khu vực |
|---|---|---|
| View-source vs rendered DOM | Browser: view-source + DevTools Elements; so title/heading/body/canonical. Không có browser/Playwright → Firecrawl MCP `firecrawl_scrape` (rendered) so với `curl` (raw) | 6.4, 6.5 |
| CWV | PageSpeed Insights công khai (pagespeed.web.dev) — field data 75th %ile, tách mobile/desktop | 5 |
| Ước lượng index bloat | `site:domain.vn` (số kết quả chỉ là ước lượng thô) so với quy mô site user khai | 2.5 |
| Soft 404 | Mở URL không tồn tại (`/khong-ton-tai-xyz`) → DevTools Network xem status | 1.2, 6.3 |
| hreflang / viewport / canonical | View-source từng URL đại diện | 7, 8 |
| Cache/index status 1 URL | GSC URL Inspection (cần user có GSC). ⚠️ `cache:` operator trong template = legacy, Google đã ngừng — không dùng | 2 |

---

## Data user luôn phải cung cấp (mọi path)

Không tool nào thay được — thiếu thì item tương ứng chấm ⬜ THIẾU DATA, tuyệt đối không bịa:

| Data | Lấy ở đâu | Cho item |
|---|---|---|
| GSC **Page indexing report** (export hoặc screenshot) | GSC > Indexing > Pages > Export. Path B: nối GSC vào SF một lần → crawl kéo tự động (`--use-google-search-console`, gồm URL Inspection per URL) — giảm phụ thuộc export tay nhưng KHÔNG thay được report tổng Page indexing. **Path A+ (khi OAuth webmasters.readonly đã consent):** `tools/gsc/gsc.sh` — `sites` / `query` (Search Analytics 16 tháng) / `inspect` (index status 1 URL) / `sitemaps` / `coverage <file-urls>` (inspect hàng loạt → CSV, quota 2.000/ngày/property) | Khu vực 2 (taxonomy hiện hành) |
| GSC **Crawl Stats** (3 checkpoint) | GSC > Settings > Crawl stats: Average response time · By response · By file type. **Đường đã test 10/07/2026:** user export từng report ra Google Sheets → đọc bằng `gws sheets spreadsheets values get` (mỗi export 3 tab Chart/Table/Metadata, Table max 1.000 examples; ⚠️ stdout gws có dòng "Using keyring backend" trước JSON — strip trước khi parse). Phân tích chuẩn trên Table: 404 theo extension + folder + tháng-upload (lộ đợt xóa hàng loạt & **URL structure change không 301** — vd `/product/` cũ vs `/products/` mới) · JS/CSS: % mang `?ver=` + unique files vs total requests (lộ cache tắt) · HTML: tần suất crawl per URL + bản `http://` lẫn trong list | 1.4–1.6 |
| GSC Manual Actions / Security | GSC > Security & Manual Actions | 2.1, 2.2 |
| Server log (nếu muốn audit log file đầy đủ) | Hosting/CDN export, hoặc SF Log File Analyser project | 1.7–1.14 |
| File disavow đã submit (nếu có) | GSC Disavow tool | 7.3 |
| **Chiến lược AI crawler** (muốn AI citation? opt-out training?) | Hỏi user 1 câu ở Bước 0 — quyết định cách chấm allow/block per bot | 1.17, 4.13 |
