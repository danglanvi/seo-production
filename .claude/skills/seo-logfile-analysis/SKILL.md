---
name: seo-logfile-analysis
description: "Phân tích server log để thấy Googlebot và AI crawler thật sự crawl gì: crawl budget theo section và theo cụm chủ đề, status code bot gặp, đối chiếu sitemap ↔ cấu trúc ↔ log, crawl waste, tần suất crawl URL quan trọng. Dùng ở công đoạn 27 (T7) hoặc audit crawl định kỳ."
metadata:
  version: "1.3"
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

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code | Parse log, xác minh IP bot (dải IP chính chủ trước, reverse DNS + forward-confirm cho IP ngoài dải), gom URL theo cụm, đếm hit, status, redirect, uploads, waste | dùng. Log chỉ xử lý trên máy |
| EmbeddingGemma 2 | Cụm chủ đề của trang | dùng gián tiếp: map cụm của skill `topical-focus` dựng từ chữ trang công khai. Không embed log: log chỉ có URL, URL ngoài map gom theo thư mục cấp 1 |
| Jev | Phân loại URL hay hành vi bot | không dùng: log chứa IP và hành vi truy cập, không gửi ra ngoài; việc đếm thuộc về code |
| GLM Flash | Trích câu | không dùng: không có việc trích câu |
| Claude | Đọc bảng cụm, so cụm quan trọng, viết finding và falsifiability | dùng |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,curl?,ssh?,gws?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0b — Đọc references + xác định data tier

1. Đọc `sop/06-self-checklist/tier-3-technical-advance.md` mục 0 (cách đọc GSC Crawl Stats) + mục 2 (3 checkpoint) — canonical cho ngưỡng crawl health; và `skills/technical-seo-audit/references/audit-checklist-by-area.md` khu vực 1 — tránh chấm lại item technical-seo-audit đã cover.
2. Xác định `$LOG_SOURCE`: `ls 02-raw/logfiles/` trong SEO Production instance của `$CLIENT`. Không có file → hỏi user; user không có log → tuyên bố Tier C ngay, không giả vờ có log. Log còn trên server aaPanel + OpenLiteSpeed: đọc `references/aapanel-ols.md` §1–2 để tìm file và kéo về máy.
3. Nhận diện `$LOG_FORMAT`: đọc 5 dòng đầu log — combined có `"referer" "user-agent"` cuối dòng, common không có. Không khớp format chuẩn → xin user 2-3 dòng mẫu, build custom regex, test parse trước khi chạy full. Log OpenLiteSpeed có thể bọc dòng trong nháy đơn và thêm trường đầu `'-`; log khác trên cùng server có thể không có trường đó. Vì vậy dò cột từ dòng mẫu của từng file, không gán cứng `$9`/`$10`. Mẫu `logFormat` của OpenLiteSpeed và nghĩa từng trường: `references/aapanel-ols.md` §3.
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

**Đếm nhanh 4xx/5xx theo khung giờ** (theo dõi sau thay đổi hoặc restart, không cần parse đầy đủ): `python3 -B skills/seo-logfile-analysis/scripts/log_health.py --log <file> [--log <file>.gz] --since "YYYY-MM-DD HH:MM:SS"`. Script đọc mã bằng regex, ra bảng theo file và phút có 5xx. Mã thoát 2 khi một file không đọc được dòng nào: không ghi "0 lỗi" cho file đó. Dòng lỗi không có giờ, như "max children" trong `stderr.log` của OpenLiteSpeed: so tổng số dòng trước và sau. PHP warning của OpenLiteSpeed còn nằm ở `/usr/local/lsws/logs/error.log`.

### Bước 2 — 🔴 Verify Googlebot THẬT (dải IP trước, reverse-DNS sau)

UA-match KHÔNG đủ — fake Googlebot (scraper giả UA) phổ biến ở hosting VN. Bắt buộc trước mọi phân tích:

1. Tải file dải IP chính chủ vào `<W>/ranges/`. Script không tự gọi mạng:
   `for f in googlebot special-crawlers user-triggered-fetchers; do curl -fsS -o "<W>/ranges/$f.json" "https://developers.google.com/static/search/apis/ipranges/$f.json"; done`
   Bingbot: `https://www.bing.com/toolbox/bingbot.json`. Không dùng `goog.json` hay `cloud.json`, vì hai file này gồm cả máy thuê Google Cloud.
2. Chạy `python3 -B skills/seo-logfile-analysis/scripts/verify_googlebot.py --log <file> [--log <file>.gz] --ranges <W>/ranges/googlebot.json --ranges <W>/ranges/special-crawlers.json --ranges <W>/ranges/user-triggered-fetchers.json --out-dir <W>/verify --write`.
   - Script so IP với dải trước. Chỉ IP ngoài dải mới qua reverse-DNS + forward-confirm. rDNS chạy song song và ưu tiên IP nhiều hit.
   - Giới hạn rDNS bằng `--max-rdns` (mặc định 500) và `--deadline` (mặc định 120 giây).
   - Không có `--write`, script chỉ chạy thử. `--write` ghi `verified_ips.txt`, `fake_ips.txt`, `unchecked_ips.txt`. Ba file này chứa IP: giữ trên máy, không đưa vào report.
3. Đọc trạng thái của từng IP:

   | Trạng thái | Nghĩa | Xử lý |
   |---|---|---|
   | `range` | IP nằm trong dải chính chủ | Thật |
   | `rdns` | Ngoài dải; rDNS về `.googlebot.com` hoặc `.google.com`, forward-confirm đúng IP | Thật. Nhiều IP nhóm này nghĩa là file dải cũ: tải lại rồi chạy lại |
   | `fake` | Ngoài dải; rDNS sai đuôi hoặc forward lệch. PTR `googleusercontent.com` thuộc nhóm này | Tách riêng, báo dev |
   | `unchecked` | Chưa rDNS (vượt hạn mức, quá giờ, `--no-rdns`) | Không tính là thật |

   Mã thoát: 0 = mọi IP thật · 1 = có IP fake · 2 = lỗi đầu vào (thiếu dải IP, file hỏng, log không có IP bot) · 3 = còn IP `unchecked`. Gặp mã 2 hoặc 3: không ghi "100% thật", ghi số IP chưa kiểm.
4. Output: % IP và % hit Googlebot là THẬT. Fake % đáng kể → tách riêng, báo trong report (fake bot ăn tài nguyên server = vấn đề riêng cho dev). **Mọi phân tích từ Bước 3 chỉ chạy trên `verified_ips.txt`**: truyền file này vào `--verified-ips` của `log_clusters.py` và `log_checks.py`.
5. Bot khác cùng nguyên tắc: Bingbot dùng `--bot bingbot --ranges <W>/ranges/bingbot.json` (đuôi `.search.msn.com`). AI crawler (GPTBot/ClaudeBot/PerplexityBot): đối chiếu dải IP hãng công bố; hãng chưa công bố dải thì ghi "hit tự khai". Phân loại theo bot-purpose matrix của technical-seo-audit 1.17, chỉ đếm + báo.

### Bước 3 — Phân tích chuẩn (7 khối, Tier A)

1. **Crawl budget theo section/URL type** — group hits Googlebot theo directory cấp 1-2 (`/blog/`, `/product/`, `/category/`…) + file type (HTML vs ảnh vs JS/CSS). Đối chiếu: section nào quan trọng cho SEO nhưng nhận ít hits? JS/CSS mang `?ver=` chiếm nhiều = cache tắt (bài học Crawl Stats, technical-seo-audit v1.2).
2. **Status codes Googlebot gặp** — phân bố 200/304/3xx/4xx/5xx trên verified hits. Ngưỡng theo bảng dưới. Liệt kê: 3xx chains (URL bị crawl lặp qua nhiều hop), top 404 (pattern theo prefix = đổi URL structure không 301), mọi 5xx/503.
   - Chạy `python3 -B skills/seo-logfile-analysis/scripts/log_checks.py redirects --log <file> --site https://<domain> --verified-ips <W>/verify/verified_ips.txt [--remove-list bo.txt] [--hub-urls hub.txt] --out-dir <W>/checks`. `bo.txt` là danh sách bỏ đã duyệt, `hub.txt` là URL trang danh mục hoặc hub, mỗi dòng một URL. Script chỉ tính hit HTML của Googlebot đã xác minh và bỏ URL có query. Output không chứa IP.
   - Thêm `--probe` để đo status hiện tại, số bước, đích cuối và status đích. Probe gửi GET tới site thật: chỉ chạy khi được phép, giữ `--workers 4`. Hit của probe là hit công cụ nội bộ, không tính là bot.
   - Xử lý theo nhóm: `chuoi` → rút về 1 bước · `dich_khong_200` → sửa đích, không để 301 dẫn tới trang 410 · `ve_trang_chu`, `tam_thoi` → 301 về trang cùng ý định, hoặc 410 nếu URL có trong danh sách bỏ · `ve_hub` → rà từng URL: có bài thay thế thì 301 thẳng về bài đó · `thieu_gach_cuoi`, `mot_buoc_200` → giữ · `da_doi` → chỉ ghi nhận.
   - 404 và 410: chỉ URL trong danh sách bỏ đã duyệt trả 410 (`content-inventory-audit`, `references/bo-bai.md`). URL gõ sai và link hỏng trả 404. Truyền danh sách bỏ bằng `--remove-list` để script gắn cờ 410 ngoài danh sách. Log có 410 nhiều hơn 404: kiểm URL ngẫu nhiên phải trả 404 bằng `wp-security-hardening` (`scripts/exposure_check.sh`, dòng `{RAND}`). Ví dụ gtvseo.com 06–19/10/2026: theme đổi mọi 404 thành 410, log có 3.387 hit 410 và 10 hit 404.
3. **Đối chiếu 3 nguồn: sitemap ↔ cấu trúc ↔ log** — fetch sitemap URLs, so tập hợp với URL Googlebot đã crawl trong `$PERIOD` → 2 bảng deliverable: **"URL trong sitemap nhưng Googlebot chưa ghé"** (thiếu internal link? bị chặn? sitemap rác?) và **"URL Googlebot crawl nhưng không trong sitemap/cấu trúc"** (orphan, parameter, URL cũ chưa chết — cross-flag `internal-linking` / [[Index Pollution]]).
4. **Crawl waste** — hits vào parameter URLs (`?`, session ID, UTM), faceted/filter URLs ([[Faceted Navigation]]), redirect chains, URL đã 404 vĩnh viễn mà bot vẫn quay lại (→ đề xuất 410 nếu URL vào danh sách bỏ đã duyệt, [[Status Codes]]). Tính % waste trên tổng verified hits.
   - Site WordPress: chạy thêm kiểm uploads trên mọi UA, vì băng thông là của cả server: `python3 -B skills/seo-logfile-analysis/scripts/log_checks.py uploads --log <file> --site https://<domain> [--from <ngày> --to <ngày>]`.
   - Mã thoát 1 nghĩa là trung vị response của file thiếu trên 2.048 byte: WordPress đang dựng cả trang lỗi cho mỗi file thiếu. Đề xuất sửa và cách kiểm sau sửa: `references/aapanel-ols.md` §4.
   - Ghi kết quả ở mục 5b của report. Không cộng số này vào % waste của Googlebot.
5. **Tần suất crawl: URL SEO quan trọng vs URL rác** — crawl hits/ngày cho từng URL trong `$COMMITTED_URLS` (ngưỡng <1,5 lần/ngày = review) so với các URL waste được crawl nhiều nhất. Đây là bảng "đắt" nhất cho Account nói chuyện với khách.
6. **Response time & bytes theo URL/section** (nếu log có trường `time`/`bytes`) — URL chậm >3s bị crawl nhiều = CoR cao; đối chiếu GSC Average response time.
7. **Crawl theo cụm chủ đề** — gom URL bot đã crawl theo cụm của `topical-focus`, so với cụm quan trọng của site.
   - Input: `pages.jsonl` và `clusters.json` của map `topical-focus` (cùng site, dựng gần ngày log), danh sách URL lõi `core.txt`, danh sách IP đã xác minh ở Bước 2.
   - Chạy `python3 -B skills/seo-logfile-analysis/scripts/log_clusters.py --log <file log> --site https://<domain> --map <map>/pages.jsonl --clusters <map>/clusters.json --core core.txt --verified-ips <W>/verify/verified_ips.txt --from <ngày> --to <ngày> --out-dir <W>/clusters`. File `.gz` đọc thẳng; lặp `--log` cho nhiều file.
   - Script bỏ query, file tĩnh, bot khác và IP chưa xác minh. Output không chứa IP.
   - Đọc cột "Hit/trang so với TB": dưới 1 ở cụm quan trọng nghĩa là bot ghé cụm đó ít hơn trung bình của site. So tỷ lệ, không so hit tuyệt đối.
   - URL ngoài map gom theo thư mục cấp 1. Thư mục ngoài map nhận nhiều hit → đối chiếu khối 4 và 5 (orphan, URL cũ, waste).
   - Không có map `topical-focus` thì chạy skill đó trước, hoặc bỏ khối này và ghi ⬜ THIẾU DATA.

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
| Status hygiene | 404 vĩnh viễn của URL trong danh sách bỏ đã duyệt → 410; URL gõ sai, link hỏng → 404; 302 tạm → 301 nếu permanent; không để 301 dẫn tới trang 410 | wiki [[Status Codes]] · `content-inventory-audit` `references/bo-bai.md` · `wp-security-hardening` (URL ngẫu nhiên chỉ nhận 404) |
| Googlebot verify | IP trong googlebot.json, special-crawlers.json, user-triggered-fetchers.json; IP ngoài dải: reverse-DNS về `.googlebot.com`/`.google.com` + forward-confirm | developers.google.com/search/docs/crawling-indexing/verifying-googlebot |
| File upload thiếu | response dưới 2 KB (404 tĩnh, không chạy WordPress). Ngưỡng nội bộ, không phải chuẩn Google | tiêu chí nghiệm thu audit log gtvseo.com 19/10/2026; đo sau sửa 21/10: 1.249 byte, trước sửa 132 KB |

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Report dựa trên file log thật và nêu tỷ lệ dòng parse lỗi; không có log thì ghi Tier C. Nguồn lỗi: 19/10 thư mục `02-raw/logfiles/` của 4 instance đều rỗng; file tên "access-log" duy nhất tìm được là bản tóm tắt 4 dòng.
- [ ] Hit của công cụ audit nội bộ không tính là bot tìm kiếm. Nguồn lỗi: tóm tắt log 06–19/10 của site mẫu ghi phần lớn request là bot hoặc công cụ audit nội bộ (`?shotx=`, UA riêng).
- [ ] Bảng cụm chỉ tính IP đã xác minh, hoặc ghi rõ "hit bot tự khai". Nguồn lỗi: bài học hosting VN ở bản 1.0, Googlebot giả UA phổ biến.
- [ ] Bảng cụm so tỷ lệ hit với tỷ lệ trang, không so hit tuyệt đối. Nguồn lỗi: map 19/10 của site mẫu có cụm SEO chiếm 34% trang và cụm Facebook 8%; so hit tuyệt đối thì cụm nhỏ luôn có vẻ bị bỏ quên.
- [ ] Log và IP không rời máy, không vào Jev hay dịch vụ ngoài. Nguồn lỗi: luật dữ liệu khách của lớp model 10/2026; `jev.py` đã phải chặn trường GSC.
- [ ] Xác minh bot lọc dải IP chính chủ trước rDNS. Report ghi số IP `unchecked`, và không ghi "% thật" khi mã thoát là 2 hoặc 3. Nguồn lỗi: 19/10/2026 log gtvseo.com, rDNS tuần tự 429 IP chạy quá 600 giây; rDNS lệch dải IP ở 8/25 IP.
- [ ] Site WordPress có mục 5b kiểm uploads: hit, byte, % băng thông, trung vị byte. Nguồn lỗi: 19/10/2026 log gtvseo.com, file upload thiếu trả 410 kèm trang lỗi đầy đủ, chiếm 45,2/120,0 GB băng thông trong 13 ngày.
- [ ] Bảng redirect có nhóm và status đích. 410 chỉ có ở URL trong danh sách bỏ. Nguồn lỗi: 19/10/2026 theme gtvseo.com đổi mọi 404 thành 410; 9 URL 302 về trang chủ; 4 redirect có đích không trả 200.

## Output

```markdown
# Logfile Analysis — <domain>
> Kỳ log: <from → to> · DATA TIER: <A/B/C — nguồn + giới hạn> · Parse errors: <n%> · Googlebot verified: <n%> thật / <n%> fake / <n> IP unchecked

## 1. Executive Summary
- 3-5 câu: budget đang đổ vào đâu, waste %, lỗi nặng nhất bot gặp

## 2. Crawl budget theo section
| Section | Hits | % | HTML/asset | Nhận định |

## 3. Status codes Googlebot gặp
| Status | Hits | % | Top URL mẫu | Action |
### 3b. Redirect theo nhóm (<n> URL, <n> hit)
| Nhóm | URL | Hit | Action |
### 3c. 404 và 410
| Status | Hit | URL | Ngoài danh sách bỏ |

## 4. Đối chiếu sitemap ↔ crawl ↔ log
### 4a. URL trong sitemap nhưng Googlebot chưa ghé (<n>)
### 4b. URL Googlebot crawl nhưng không trong sitemap/cấu trúc (<n>)

## 5. Crawl waste (<n>% tổng hits)
| Loại waste | Hits | URL mẫu | Fix |
### 5b. File upload thiếu trả 404/410 (mọi UA)
| Hit | File | Dung lượng | % băng thông | Trung vị byte | Referer ngoài site nhiều nhất |

## 6. Tần suất crawl: URL cam kết vs URL rác
| URL | Hits/ngày | Ngưỡng | Status |

## 6b. Crawl theo cụm chủ đề
| Cụm | Quan trọng | Trang | Trang được crawl | % trang | % hit | Hit/trang so với TB | Nhận định |

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
- ❌ rDNS tuần tự mọi IP khi đã có file dải IP. Ngày 19/10/2026, rDNS 429 IP của log gtvseo.com chạy quá 600 giây. Dùng `verify_googlebot.py`: dải IP trước, rDNS song song cho phần còn lại.
- ❌ Tính PTR `googleusercontent.com` hoặc IP trong `goog.json` là Googlebot. Hai nguồn này gồm máy thuê Google Cloud. Log gtvseo.com 19/10/2026 có 126 IP PTR `googleusercontent.com`, đều giả UA.
- ❌ Coi 304 cao là lỗi — 304 = tiết kiệm crawl budget, dấu hiệu tốt (tier-3 mục 2.2).
- ❌ Khuyến nghị crawl budget nặng cho site < ~10k trang — frame theo index hygiene thay vì budget.
- ❌ Đọc thô log/parquet từng dòng thay vì script (pandas/DuckDB/awk).
- ❌ Đếm mã trạng thái bằng awk gán cứng `$9` hay `$10` cho mọi file log. Ngày 23–24/10/2026, 4 lane trên gtvseo.com đếm sai 5xx vì log en và staging đặt mã ở `$9`. Dùng `log_health.py`, hoặc tách theo `"` rồi đọc trường 3.
- ❌ Phát biểu số đếm từ log parse lỗi >5% hoặc log thiếu ngày như số cuối — luôn ghi "cận dưới".
- ❌ Dùng GSC Crawl Stats (Tier C) để kết luận crawl frequency per URL — Crawl Stats là sample toàn site.
- ❌ Tự lập link plan cho orphan phát hiện được — cross-flag `internal-linking`.
- ❌ Quyết định allow/block AI crawler từ log — chỉ đếm + báo; chiến lược thuộc technical-seo-audit Bước 0.
- ❌ Đè lên khu vực 2-7 của technical-seo-audit (index coverage, CWV, HTTPS…) — skill này chỉ crawl-side.

## References & wiki

**References nội bộ (cross-ref, không copy):**
- `references/aapanel-ols.md` — đường log, `logFormat`, kéo log về máy, đề xuất sửa cấu hình log và uploads trên aaPanel + OpenLiteSpeed. Nạp ở Bước 0b khi log còn trên server.
- Skill `content-inventory-audit`, `references/bo-bai.md` — danh sách bỏ, chọn 410 hay 301. Skill `wp-security-hardening`, `scripts/exposure_check.sh` — URL ngẫu nhiên phải trả 404.
- `sop/06-self-checklist/tier-3-technical-advance.md` — mục 0 (đọc Crawl Stats), 2 (3 checkpoint), 6.6 (logfile dashboard) — canonical ngưỡng crawl health.
- `skills/technical-seo-audit/references/audit-checklist-by-area.md` — khu vực 1 (Crawl & Log File) — ranh giới item.
- `skills/technical-seo-audit/references/data-paths.md` — đường lấy GSC Crawl Stats qua Google Sheets + gws.

**Wiki Semantic SEO (lớp WHY):** [[Cost of Retrieval]] · [[Index Pollution]] · [[Status Codes]] · [[Robots.txt]] · [[Faceted Navigation]] · [[GEO]]

**Docs & tools:** developers.google.com/search/docs/crawling-indexing/verifying-googlebot · developers.google.com/crawling/docs/crawl-budget · advertools.readthedocs.io (`logs_to_df`) · goaccess.io (`brew install goaccess`)

## Changelog

- **v1.3 (2026-10-25):** log-1: `verify_googlebot.py` lọc dải IP trước rDNS (song song, 4 trạng thái, mã thoát 0–3, bỏ đuôi `googleusercontent.com`); `log_checks.py` kiểm uploads và redirect, 404/410 theo nhóm; `references/aapanel-ols.md`. Chạy offline trên 28 file log gtvseo.com 06–19/10: uploads 284.139 hit, 45,1/119,3 GB, khớp báo cáo 19/10.
- **v1.2 (2026-10-24):** thêm `scripts/log_health.py` (4xx/5xx theo khung giờ, mã thoát 2 khi không đọc được dòng nào) và test `tests/test_log_health.py`, có ca awk `$10` đọc nhầm số byte. Chạy thật trên 6 file log gtvseo.com 06–19/10: đọc 249.105/249.139 dòng, số 5xx khớp awk `$10` và awk tách theo `"` (175/175/175). Bước 0b và Anti-patterns: dò cột từ dòng mẫu. Nguồn: `Deliverables/GTV-Brand/GTV-Website/perf-20261020/toi-uu-khong-nang-vps-2310/dot1-2410/d1a/kiem-doc-lap.md`, `b0/kiem-doc-lap.md`.
- **v1.1.1 (2026-10-19):** `log_clusters.py` đọc được log OpenLiteSpeed (dòng bọc nháy đơn, có trường proxy trước IP client). Nhận thêm bot GoogleOther, Applebot, Meta, Bytespider, Amazonbot, CCBot. Chạy thật trên log gtvseo.com 06–19/10: parse 48.803/48.803 dòng. Test `test_ols_line_and_more_bots`.
- **v1.1 (2026-10-19):** thêm khối 7 Crawl theo cụm chủ đề (`scripts/log_clusters.py`, stdlib): gom URL bot đã crawl theo cụm `topical-focus`, so với cụm chứa URL lõi. Thêm Bước 0, phân việc model, tự phản biện, mục 6b. Test fixture `tests/test_log_clusters.py`. Chưa chạy trên log thật.
- **v1.0 (2026-07-19):** tạo mới — phục vụ công đoạn (27) T7 quy trình 10 tháng + audit duy trì hằng tuần; data ladder advertools → GoAccess → GSC Crawl Stats proxy; reverse-DNS verify bắt buộc; 6 khối phân tích chuẩn; ngưỡng kế thừa whitelist technical-seo-audit + tier-3 SOP.
