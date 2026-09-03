---
name: seo-logfile-analysis
description: "Phân tích server log file để thấy Googlebot (và AI crawler) THỰC TẾ crawl gì — crawl budget theo section, status codes bot gặp, đối chiếu 3 nguồn sitemap ↔ cấu trúc ↔ log, crawl waste, tần suất crawl URL quan trọng vs URL rác — phục vụ công đoạn (27) T7 của quy trình SEO 10 tháng."
metadata:
  version: "1.0"
---

# SEO Logfile Analysis

Deep-dive **log file server** — nguồn dữ liệu duy nhất cho thấy search engine bot *thực tế* làm gì trên site (GSC Crawl Stats chỉ là sample tổng hợp). Trả lời 3 câu hỏi: Googlebot crawl GÌ, gặp GÌ (status codes), và có đang LÃNG PHÍ budget vào URL rác thay vì URL SEO cam kết không — tất cả quy về [[Cost of Retrieval]].

**Vị trí trong quy trình:** công đoạn **(27) T7** của quy trình SEO 10 tháng (logfile + FULL audit, chạy cùng `technical-seo-audit`) + nhịp audit duy trì hằng tuần giai đoạn maintain. **Upstream:** file log trong `02-raw/logfiles/` của SEO Production instance (hoặc user cung cấp). **Downstream:** report vào `03-audits/` + action list "technical sửa trước" giao dev; các fix ngoài scope route theo bảng phân vai.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Audit technical site tổng (7 khu vực: index, redirect, sitemap, CWV, JS, HTTPS) | `technical-seo-audit` | Skill này = deep-dive khu vực 1 (Crawl & Log File) với log đầy đủ; T7 chạy CẢ HAI — logfile cấp evidence crawl-side cho technical audit |
| Orphan page → link plan sửa | `internal-linking` | Skill này chỉ *phát hiện* "URL Googlebot crawl nhưng không trong sitemap/cấu trúc" — không lập link plan |
| Bài rớt traffic / decay | `content-refresh` | Tần suất crawl giảm trên 1 URL chỉ là *tín hiệu phụ* — kết luận decay cần data hiệu suất |
| Sự kiện migration (crawl pattern quanh launch) | `site-migration-checklist` | Skill này audit nhịp thường; log quanh migration event → skill migration dùng làm evidence |
| Chiến lược AI crawler (mở/chặn bot) | `technical-seo-audit` (item 1.17, 4.13) | Skill này chỉ *đếm + báo cáo* AI bot hits trong log, không quyết định allow/block |

## Input

**Required:**
- `$LOG_SOURCE` — đường dẫn file log: mặc định tìm trong `02-raw/logfiles/` của SEO Production instance của client; hoặc user cung cấp trực tiếp (`.log`, `.gz`, export CDN/hosting).
- `$TARGET` — domain của log (để đối chiếu sitemap + cấu trúc).

**Optional:**
- `$LOG_FORMAT` — `combined` (default, Apache/Nginx access phổ biến) / `common` / `nginx_error` / `apache_error` / custom regex (user cung cấp mẫu 2-3 dòng log → build regex). advertools hỗ trợ tất cả các format này qua `log_format=`.
- `$SITEMAP_URL` — sitemap index để đối chiếu 3 nguồn (không có → fetch `/sitemap.xml` + đọc robots.txt).
- `$COMMITTED_URLS` — bộ URL SEO cam kết (từ workbook/hợp đồng) — ưu tiên số 1 cho phân tích tần suất crawl.
- `$PERIOD` — khoảng ngày phân tích (default: toàn bộ log; audit tuần → 7 ngày gần nhất).
- `$CLIENT` — tên client để đặt tên file output + tìm đúng SEO Production instance.

**Data ladder (khai báo TIER trong report — Gate #1):**

| Tier | Điều kiện | Data & giới hạn |
|---|---|---|
| **A — Full** | Có log đầy đủ + Python với `advertools` | `advertools.logs_to_df()` → parquet + errors file → phân tích đầy đủ 6 khối (Bước 3) + GoAccess dashboard HTML |
| **B — Dashboard-only** | Có log nhưng không chạy được Python/advertools | GoAccess (`brew install goaccess`) → dashboard HTML: hits, status, URL top — KHÔNG có verify reverse-DNS + đối chiếu sitemap chi tiết → các khối đó chấm ⬜ THIẾU DATA |
| **C — Proxy** | Không có log | GSC Crawl Stats làm proxy (3 checkpoint theo `sop/06-self-checklist/tier-3-technical-advance.md` mục 0 + 2). 🔴 Ghi rõ trong report: Crawl Stats là *sample toàn site theo loại request, không per-URL* — không kết luận được crawl frequency per URL, không verify được fake bot |

⚠️ Tier C luôn chạy được — skill không bao giờ chết vì thiếu log, nhưng report phải ghi rõ mọi giới hạn của proxy.

## Workflow

### Bước 0 — Đọc references + xác định data tier

1. Đọc `sop/06-self-checklist/tier-3-technical-advance.md` mục 0 (cách đọc GSC Crawl Stats) + mục 2 (3 checkpoint) — canonical cho ngưỡng crawl health; và `skills/technical-seo-audit/references/audit-checklist-by-area.md` khu vực 1 — tránh chấm lại item technical-seo-audit đã cover.
2. Xác định `$LOG_SOURCE`: `ls 02-raw/logfiles/` trong SEO Production instance của `$CLIENT`. Không có file → hỏi user; user không có log → tuyên bố Tier C ngay, không giả vờ có log.
3. Nhận diện `$LOG_FORMAT`: đọc 5 dòng đầu log — combined có `"referer" "user-agent"` cuối dòng, common không có. Không khớp format chuẩn → xin user 2-3 dòng mẫu, build custom regex, test parse trước khi chạy full.
4. Xác định `$PERIOD` + hỏi `$COMMITTED_URLS` nếu chưa có (workbook client) — thiếu thì phân tích tần suất chỉ theo section, ghi chú thiếu.
5. Báo user: tier + số dòng log ước tính + việc sẽ chạy → **chờ xác nhận** rồi mới parse (log file lớn có thể tốn thời gian đáng kể).

### Bước 1 — Parse log (Tier A) / dựng dashboard (Tier B)

**Tier A** — advertools (pip install advertools nếu chưa có):

```python
import advertools as adv
adv.logs_to_df(log_file="02-raw/logfiles/access.log",
               output_file="scratch/logs.parquet",
               errors_file="scratch/log_errors.txt",
               log_format="combined")  # hoặc common / nginx_error / apache_error / regex
```

- Đọc parquet bằng pandas/DuckDB — KHÔNG đọc thô từng dòng log.
- 🔴 Check `log_errors.txt`: % dòng parse fail cao (>5%) → format sai hoặc log lẫn nhiều nguồn → sửa format trước khi kết luận. Số liệu từ parse thiếu = "cận dưới".

**Tier B** — GoAccess dashboard (cũng chạy Ở CẢ Tier A để có HTML gửi khách/Account):

```bash
goaccess access.log --log-format=COMBINED -o 03-audits/<client>-goaccess-<date>.html
# .gz: zcat access.log.gz | goaccess --log-format=COMBINED -o report.html -
```

### Bước 2 — 🔴 Verify Googlebot THẬT (reverse-DNS)

UA-match KHÔNG đủ — fake Googlebot (scraper giả UA) phổ biến ở hosting VN. Bắt buộc trước mọi phân tích:

1. Lọc record có UA chứa `Googlebot` → lấy danh sách IP unique.
2. Reverse DNS từng IP (sample ≥20 IP hoặc toàn bộ nếu ít): `host <IP>` → hostname phải kết thúc `.googlebot.com` hoặc `.google.com` → forward-confirm: `host <hostname>` trả về đúng IP đó.
3. Đường nhanh thay thế: đối chiếu IP với dải chính chủ `https://www.gstatic.com/ipranges/goog.json` + `developers.google.com/static/search/apis/ipranges/googlebot.json` (script python so CIDR).
4. Output: % hits Googlebot là THẬT. Fake % đáng kể → tách riêng, báo trong report (fake bot ăn tài nguyên server = vấn đề riêng cho dev), và **mọi phân tích từ Bước 3 chỉ chạy trên verified hits**.
5. Bot khác cùng nguyên tắc: Bingbot (`.search.msn.com`), AI crawler (GPTBot/ClaudeBot/PerplexityBot — đối chiếu published IP ranges; phân loại theo bot-purpose matrix của technical-seo-audit 1.17, chỉ đếm + báo).

### Bước 3 — Phân tích chuẩn (6 khối, Tier A)

1. **Crawl budget theo section/URL type** — group hits Googlebot theo directory cấp 1-2 (`/blog/`, `/product/`, `/category/`…) + file type (HTML vs ảnh vs JS/CSS). Đối chiếu: section nào quan trọng cho SEO nhưng nhận ít hits? JS/CSS mang `?ver=` chiếm nhiều = cache tắt (bài học Crawl Stats, technical-seo-audit v1.2).
2. **Status codes Googlebot gặp** — phân bố 200/304/3xx/4xx/5xx trên verified hits. Ngưỡng theo bảng dưới. Liệt kê: 3xx chains (URL bị crawl lặp qua nhiều hop), top 404 (pattern theo prefix = đổi URL structure không 301), mọi 5xx/503.
3. **Đối chiếu 3 nguồn: sitemap ↔ cấu trúc ↔ log** — fetch sitemap URLs, so tập hợp với URL Googlebot đã crawl trong `$PERIOD` → 2 bảng deliverable: **"URL trong sitemap nhưng Googlebot chưa ghé"** (thiếu internal link? bị chặn? sitemap rác?) và **"URL Googlebot crawl nhưng không trong sitemap/cấu trúc"** (orphan, parameter, URL cũ chưa chết — cross-flag `internal-linking` / [[Index Pollution]]).
4. **Crawl waste** — hits vào parameter URLs (`?`, session ID, UTM), faceted/filter URLs ([[Faceted Navigation]]), redirect chains, URL đã 404 vĩnh viễn mà bot vẫn quay lại (→ đề xuất 410, [[Status Codes]]). Tính % waste trên tổng verified hits.
5. **Tần suất crawl: URL SEO quan trọng vs URL rác** — crawl hits/ngày cho từng URL trong `$COMMITTED_URLS` (ngưỡng <1,5 lần/ngày = review) so với các URL waste được crawl nhiều nhất. Đây là bảng "đắt" nhất cho Account nói chuyện với khách.
6. **Response time & bytes theo URL/section** (nếu log có trường `time`/`bytes`) — URL chậm >3s bị crawl nhiều = CoR cao; đối chiếu GSC Average response time.

**Tier C** thay bằng: 3 checkpoint GSC Crawl Stats (avg response time / by response / by file type) + By purpose + By Googlebot type theo tier-3 SOP mục 0 — chấm được khối 1, 2 ở mức toàn site; khối 3-6 chấm ⬜ THIẾU DATA kèm hướng dẫn xin log từ hosting/CDN.

### Bước 4 — Findings + action list

Mỗi finding: evidence (số + URL mẫu + khoảng ngày log) → hành động → người làm (dev/SEO) → **Falsifiability**: "làm sao biết nếu khuyến nghị này sai?" + leading indicator (vd fix redirect chain → leading indicator: hits 3xx trong log tuần sau giảm; nếu 3xx giảm mà hits 200 vào URL đích KHÔNG tăng trong 2-4 tuần → khuyến nghị chưa trúng, xét lại).

### Bước 5 — Render report & trả file

- Report markdown → `03-audits/<client>_Logfile-Analysis_<YYYY-MM-DD>.md` (SEO Production instance) + GoAccess HTML cùng folder, link từ report.
- Audit tuần: report ngắn dạng delta so tuần trước (chỉ khối 2 + 5 + thay đổi bất thường).

## Bảng ngưỡng (whitelist — nguồn bắt buộc)

🔴 Con số KHÔNG có trong bảng → không phát biểu như chuẩn trong report.

| Ngưỡng | Giá trị | Nguồn |
|---|---|---|
| URL quan trọng ít crawl | <1,5 lần/ngày → review | xlsx sheet3 dòng 10 (template audit nội bộ, qua technical-seo-audit) |
| URL crawl chậm | Average Response Time >3s → review | xlsx sheet3 dòng 13 |
| Log 404 hits | mục tiêu <50/tháng | wiki [[Status Codes]] (baseline case Koray >25.000) |
| By response (GSC/log) | 200+304 ≥ ~95%; 4xx <1%; 5xx ~0% — 🔴 304 cao là TỐT, không phải lỗi | tier-3-technical-advance.md mục 2.2 |
| GSC Avg response time | <200ms tốt / <350ms tối thiểu / >500ms cờ đỏ | tier-3-technical-advance.md mục 0 + 2.1 |
| Crawl budget gate | site < ~10k trang unique → crawl budget không phải ưu tiên, frame findings theo index hygiene | developers.google.com/crawling/docs/crawl-budget |
| Status hygiene | 404 vĩnh viễn → 410; 302 tạm → 301 nếu permanent | wiki [[Status Codes]] |
| Googlebot verify | reverse-DNS về `.googlebot.com`/`.google.com` + forward-confirm; hoặc IP trong googlebot.json | developers.google.com/search/docs/crawling-indexing/verifying-googlebot |

## Output

```markdown
# Logfile Analysis — <domain>
> Kỳ log: <from → to> · DATA TIER: <A/B/C — nguồn + giới hạn> · Parse errors: <n%> · Googlebot verified: <n%> thật / <n%> fake

## 1. Executive Summary
- 3-5 câu: budget đang đổ vào đâu, waste %, lỗi nặng nhất bot gặp

## 2. Crawl budget theo section
| Section | Hits | % | HTML/asset | Nhận định |

## 3. Status codes Googlebot gặp
| Status | Hits | % | Top URL mẫu | Action |

## 4. Đối chiếu sitemap ↔ crawl ↔ log
### 4a. URL trong sitemap nhưng Googlebot chưa ghé (<n>)
### 4b. URL Googlebot crawl nhưng không trong sitemap/cấu trúc (<n>)

## 5. Crawl waste (<n>% tổng hits)
| Loại waste | Hits | URL mẫu | Fix |

## 6. Tần suất crawl: URL cam kết vs URL rác
| URL | Hits/ngày | Ngưỡng | Status |

## 7. Action list — technical sửa trước
| # | Priority | Việc | Evidence | Người làm | Falsifiability + leading indicator |

## 8. Đính kèm & data thiếu
- GoAccess dashboard: <file.html> · Item ⬜ + cách lấy data
```

## Behavior Gates

**#1 Data tier declare** — Report LUÔN mở đầu bằng DATA TIER (A/B/C) + nguồn + giới hạn. Tier C không được trình bày như phân tích log thật.

**#2 No hard-fail** — Thiếu advertools → Tier B; thiếu log → Tier C (GSC Crawl Stats proxy). Không bao giờ dừng vì thiếu tool; ghi giới hạn thay vì chết.

**#3 Verify trước, phân tích sau** — 🔴 Không có kết luận nào về "Googlebot" khi chưa qua Bước 2. UA-match đơn thuần chỉ được gọi là "self-reported bot hits".

**#4 Falsifiability** — Mỗi finding trong action list kèm trường Falsifiability: điều kiện nào chứng minh khuyến nghị sai + leading indicator đo trong log/GSC kỳ sau.

**#5 Evidence** — Mọi con số truy được về: file log + khoảng ngày + bộ lọc. Ngưỡng chỉ lấy từ bảng whitelist. Parse errors % và fake-bot % luôn khai báo.

## Anti-patterns

- ❌ Kết luận "Googlebot crawl X" từ UA-match chưa reverse-DNS — fake Googlebot phổ biến ở hosting VN.
- ❌ Coi 304 cao là lỗi — 304 = tiết kiệm crawl budget, dấu hiệu tốt (tier-3 mục 2.2).
- ❌ Khuyến nghị crawl budget nặng cho site < ~10k trang — frame theo index hygiene thay vì budget.
- ❌ Đọc thô log/parquet từng dòng thay vì script (pandas/DuckDB/awk).
- ❌ Phát biểu số đếm từ log parse lỗi >5% hoặc log thiếu ngày như số cuối — luôn ghi "cận dưới".
- ❌ Dùng GSC Crawl Stats (Tier C) để kết luận crawl frequency per URL — Crawl Stats là sample toàn site.
- ❌ Tự lập link plan cho orphan phát hiện được — cross-flag `internal-linking`.
- ❌ Quyết định allow/block AI crawler từ log — chỉ đếm + báo; chiến lược thuộc technical-seo-audit Bước 0.
- ❌ Đè lên khu vực 2-7 của technical-seo-audit (index coverage, CWV, HTTPS…) — skill này chỉ crawl-side.

## References & wiki

**References nội bộ (cross-ref, không copy):**
- `sop/06-self-checklist/tier-3-technical-advance.md` — mục 0 (đọc Crawl Stats), 2 (3 checkpoint), 6.6 (logfile dashboard) — canonical ngưỡng crawl health.
- `skills/technical-seo-audit/references/audit-checklist-by-area.md` — khu vực 1 (Crawl & Log File) — ranh giới item.
- `skills/technical-seo-audit/references/data-paths.md` — đường lấy GSC Crawl Stats qua Google Sheets + gws.

**Wiki Semantic SEO (lớp WHY):** [[Cost of Retrieval]] · [[Index Pollution]] · [[Status Codes]] · [[Robots.txt]] · [[Faceted Navigation]] · [[GEO]]

**Docs & tools:** developers.google.com/search/docs/crawling-indexing/verifying-googlebot · developers.google.com/crawling/docs/crawl-budget · advertools.readthedocs.io (`logs_to_df`) · goaccess.io (`brew install goaccess`)

## Changelog

- **v1.0 (2026-07-19):** tạo mới — phục vụ công đoạn (27) T7 quy trình 10 tháng + audit duy trì hằng tuần; data ladder advertools → GoAccess → GSC Crawl Stats proxy; reverse-DNS verify bắt buộc; 6 khối phân tích chuẩn; ngưỡng kế thừa whitelist technical-seo-audit + tier-3 SOP.
