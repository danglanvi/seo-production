---
type: sop
status: stable
checklist_type: event # chạy khi có sự cố, không chạy định kỳ
event: website khách bị hack / nhiễm mã độc
last_updated: 2026-07-19
items_count: 35
source_raw:
  - "raw/_ingested/Quy trình SEO PSP - All In One/Checklist xử lý mã độc website - GTV SEO.xlsx" # sheets: Quy trình / Mẫu - Audit Crawl / Thúc đẩy CRAWL / Tài liệu đọc thêm (2024)
  - "raw/_ingested/Quy trình SEO PSP - All In One/Quy trình, checklist & hướng dẫn XỬ LÝ MÃ ĐỘC và khôi phục SEO Ranking.docx" # đọc được full text (206 đoạn + 1 bảng)
related:
  - "[[Index Pollution]]"
  - "[[Status Codes]]"
  - "[[Robots.txt]]"
  - "[[Cost of Retrieval]]"
  - "[[Source Context]]"
  - "[[Historical Data]]"
next_checklist: "checklist-khoi-phuc-seo-ranking.md"
tags: [sop, event-checklist, malware, hacked-site, security, crawl, index]
---

# Event Checklist — Xử lý mã độc website (MD-01 → MD-35)

> **Khi dùng:** Website khách bị hack / nhiễm mã độc / bị inject URL spam. Đây là **event checklist** — kích hoạt khi có sự cố, không phải checklist định kỳ.
> **Cấu trúc:** 4 phase — P1 Phát hiện & cô lập → P2 Làm sạch → P3 Xử lý hậu quả SEO → P4 Phòng ngừa. Làm **theo thứ tự phase**; trong phase có thể song song.
> **Nối tiếp:** Sau khi P1–P3 xong (site sạch, index rác đã xử lý) → chuyển sang `checklist-khoi-phuc-seo-ranking.md` để phục hồi crawl/index/ranking.
>
> **Nguyên tắc xuyên suốt (từ file gốc 2024, vẫn đúng):** *"Khi dính mã độc BẮT BUỘC phải lấy được logfile và follow liên tục crawl/index."* URL spam index hàng loạt sẽ làm **lệch theme website** — Google hiểu chủ đề site thành chủ đề khác ([[Index Pollution]] + tổn thương [[Source Context]]) → xóa index rác càng sớm càng tốt.
> **Deadline:** ưu tiên xử lý dứt điểm trong **tối đa 14 ngày** kể từ khi phát hiện. Càng sớm, [[Historical Data]] càng ít tổn thương.

**Ký hiệu cột Nguồn:** `XLSX-QT` = xlsx sheet "Quy trình" · `XLSX-CRAWL` = xlsx sheet "Thúc đẩy CRAWL" · `XLSX-AUDIT` = xlsx sheet "Mẫu - Audit Crawl" · `DOCX §…` = docx theo mục · `GTV 2026` = bổ sung mới (bản 2024 thiếu).

---

## 0. Phân vai & Escalation (đọc trước khi làm)

| Vai | Chịu trách nhiệm | Không làm |
|---|---|---|
| **Coder khách / Dev** | Toàn bộ thao tác server-side: scan source, clean code, đổi DB prefix, vá lỗ hổng, đổi credentials hosting/DB/FTP, chặn IP, chuyển hosting | Quyết định SEO (de-index, robots, disavow) |
| **GTV (SEO)** | Audit SEO: logfile, site: search, GSC, sitemap/robots, de-index URL rác, disavow, submit security review, follow crawl/index | Tự sửa source/DB của khách (chỉ **đề xuất** để dev thực hiện — vd MD-17 chặn IP) |
| **Account** | Thông báo khách trong **24h đầu**, lấy quyền truy cập (hosting, source, GSC owner), quản trị kỳ vọng & timeline, điều phối coder khách ↔ GTV | Cam kết thời gian phục hồi ranking khi chưa có đánh giá từ SEO Lead |

**Escalation:** không lấy được logfile/quyền truy cập sau 48h → Account escalate với khách. Xử lý kéo dài > 14 ngày hoặc mã độc tái nhiễm sau clean → SEO Lead báo Director. *(Nguồn: DOCX §II-4 "ưu tiên xử lý dứt điểm tối đa 14 ngày" + GTV 2026 phần phân vai.)*

---

## P1 — Phát hiện & Cô lập

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| MD-01 | **Nhận diện triệu chứng** | Check đủ 5 nhóm dấu hiệu: (1) GSC **Security Issues** có cảnh báo; (2) SERP hiển thị lạ — title/description tiếng Nhật/Trung, keyword casino/nike/thuốc; (3) **Cloaked content** — bot thấy khác user; (4) Redirect lạ khi vào từ Google; (5) **Spike URL index rác** (GSC Pages tăng bất thường). Ghi nhận triệu chứng nào có → định hướng loại mã độc. | GTV | GTV 2026 (bản 2024 thiếu bước nhận diện tổng; triệu chứng rải rác ở XLSX-QT C12, C15) |
| MD-02 | **Xác nhận + đo quy mô index rác** | `site:domain` và `site:domain + keyword spam` (shop, men, woman, nike, casino…) → URL rác là dạng gì, **số lượng bao nhiêu**. Đối chiếu GSC Pages (mục Indexed + Not indexed). Chụp screenshot làm evidence + baseline đo tiến độ. | GTV | XLSX-QT C12-C13 · DOCX §II-1.9 |
| MD-03 | **Kiểm tra cloaking** | (1) GSC URL Inspection > View crawled page → data Google thu thập có đúng source không; (2) Screaming Frog > Configuration > User-agent → đổi sang Googlebot desktop/smartphone, Bingbot, Yahoo-slurp → nếu bot thấy URL spam mà user không thấy = đang cloaking, code chưa sạch. | GTV | XLSX-QT D30 · DOCX §II-3.2 B2 |
| MD-04 | **Backup forensic bản nhiễm** | Trước khi đụng vào bất cứ gì: snapshot source + DB **nguyên trạng bản đang nhiễm** (để dev truy vết vector + đối chiếu file modified). Backup này tách riêng, KHÔNG dùng để restore. | Coder | GTV 2026 (bản 2024 chỉ có backup sạch sau clean — XLSX-QT C20) |
| MD-05 | **Cân nhắc maintenance mode 503** | Nếu mã độc gây hại trực tiếp cho user (redirect độc, phishing, drive-by download) → bật maintenance mode trả **503** (không 404/410 toàn site) trong lúc clean. 503 báo Google "tạm thời" — không mất index. Không kéo dài quá vài ngày. Nếu mã độc chỉ inject URL rác, site vẫn dùng được → không cần. | Coder + GTV | GTV 2026 · [[Status Codes]] |
| MD-06 | **Lấy logfile + follow liên tục** | BẮT BUỘC lấy được logfile (Screaming Frog Log File Analyser hoặc tương đương). Theo dõi: URL mã độc được crawl, IP truy cập, tần suất, bot nào, referral, directory, và URL 200 quan trọng (trang chủ, URL SEO, sitemap con, robots.txt) còn được crawl không. Duy trì follow suốt quá trình xử lý. | GTV (data từ Coder) | XLSX-QT A2, C14 · DOCX §II-1.10 |
| MD-07 | **Thông báo khách qua Account** | Trong 24h: Account báo khách hiện trạng + phạm vi ảnh hưởng, xin quyền truy cập cần thiết (hosting, source, DB, GSC owner), chốt phân vai coder khách vs GTV theo bảng mục 0, và set kỳ vọng: xử lý sạch trước — phục hồi ranking là giai đoạn sau. | Account | GTV 2026 |
| MD-08 | **Chụp baseline ranking & traffic** | Export ranking hiện tại (rank tracker) + GSC Performance + GA4 làm mốc. Lưu ý từ file gốc: lúc bị mã độc có thể **chưa ảnh hưởng ngay** — khi thấy rớt thì thường đã bị bắn mã độc trước đó → lấy thêm data 30 ngày trước sự cố làm baseline "trước khi nhiễm". Baseline này dùng cho checklist khôi phục (KP-16). | GTV | XLSX-QT C15 · DOCX §II-1.11 |
| MD-09 | **Audit quyền truy cập GSC/GA** | Check GSC Settings > Users and permissions: có owner/user lạ được add không (hacker thường tự add owner để theo dõi + submit sitemap rác). Gỡ user lạ, verify lại danh sách với khách. | GTV + Account | XLSX-QT C11 · DOCX §II-1.8 |

---

## P2 — Làm sạch (Coder khách chủ trì, GTV verify)

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| MD-10 | **Scan + xác định vector tấn công** | Scan bằng security plugin (Wordfence, iThemes Security/Solid Security bản pro, hoặc server-side scanner) + check thủ công **file modified gần nhất** trong source. Kết luận vector: plugin/theme lỗ hổng, credentials bị lộ, hosting lây chéo, hay core outdated. | Coder | DOCX §I-1, §I-2 · XLSX-QT C16 |
| MD-11 | **Audit plugin/theme nghi ngờ** | Note các plugin đáng ngờ — đặc biệt plugin trả phí nhưng share miễn phí (nulled) rất dễ bị cài sẵn mã độc → dev kiểm tra và gỡ. Update WordPress core + theme + toàn bộ plugin lên bản mới nhất (bản cũ nhiều lỗ hổng). | Coder (GTV note danh sách) | XLSX-QT C6, C8, D6, D8 · DOCX §II-1.4, §II-1.6 |
| MD-12 | **Kiểm tra hosting & lây chéo** | Hosting kém có thể là nguồn (DDoS, spyware); 1 site nhiễm trên shared hosting có thể lây các site cùng host. Check các website cùng hosting; nếu host không đảm bảo → chuyển hosting mới / dựng bản tạm cho user truy cập trong lúc xử lý bản chính. Khuyến nghị 1 website / 1 hosting, hoặc có cách ly giữa các site. | Coder + Account (quyết định với khách) | XLSX-QT C9, D9 · DOCX §II-1.7 |
| MD-13 | **Clean source + backup sạch** | Xử lý clean về source gốc; quét lại toàn bộ xác nhận **không còn đoạn mã độc nào** → lưu backup source sạch (tách khỏi backup forensic MD-04). | Coder | DOCX §I-3 · XLSX-QT C20, D20 |
| MD-14 | **Đổi TOÀN BỘ credentials** | Sau clean (không phải trước — đổi trước clean thì backdoor vẫn lấy lại được): pass + email admin CMS của **toàn bộ user admin**, pass DB, hosting panel, FTP/SSH, API keys. WordPress: đổi thêm salts/security keys trong wp-config để invalidate mọi session cũ. | Coder | DOCX §I-5 (base) + GTV 2026 (mở rộng DB/FTP/salts — bản cũ chỉ đổi user admin) |
| MD-15 | **Đổi DB prefix + URL login** | Đổi table prefix DB (wp_ → prefix riêng, kèm update các meta_key/option_name tương ứng — quy trình chi tiết trong DOCX §I-4) + đổi đường dẫn đăng nhập khỏi mặc định /wp-admin/. | Coder | DOCX §I-4, §I-6 |
| MD-16 | **Truy quét backdoor còn sót** | Check: (1) user admin lạ trong CMS + trong DB; (2) cron jobs / scheduled tasks lạ (server cron + wp-cron); (3) file thực thi lạ trong uploads/, wp-content/, file .php giả dạng ảnh; (4) file .htaccess bị sửa; (5) bài viết tiếng nước ngoài phát sinh trong CMS. Sạch = không còn mục nào. | Coder (GTV check CMS content) | GTV 2026 (bản 2024 thiếu — chỉ có ý "phát sinh bài viết tiếng nước ngoài" ở XLSX-QT C17) |
| MD-17 | **Chặn IP bẩn** | Từ audit logfile (MD-06): chặn các IP truy cập nhiều URL bẩn. **Lưu ý quan trọng:** loại trừ IP Googlebot đã verified — đối chiếu `developers.google.com/static/search/apis/ipranges/googlebot.json` + `gstatic.com/ipranges/goog.json`. Case Deco-crystal: IP công cộng crawl cả URL độc lẫn URL 200 → không chặn được, phải chấp nhận bỏ qua item này. SEOer đề xuất list → dev chặn. | GTV đề xuất → Coder | XLSX-QT C23, D23 · DOCX §I-7, §II-2.6 + MỞ RỘNG case Deco |
| MD-18 | **Check external link out** | Screaming Frog (+ Ahrefs/Semrush) quét outlink: site có đang link out tới website dính độc/nghi ngờ không (mã độc thường inject link out). Gỡ toàn bộ link bị inject. | GTV | XLSX-QT C7, D7 · DOCX §II-1.5 |
| MD-19 | **Theo dõi 3–4 ngày xác nhận sạch + nhận định loại mã độc** | Sau clean, theo dõi 3–4 ngày: không phát sinh file lạ / URL rác mới / IP bất thường mới (đối chiếu logfile). Đồng thời chốt **nhận định loại mã độc** để chọn phương án chặn ở P3: dạng tiền tố chữ/số (case bacsikhai) · dạng parameter · dạng bài viết tiếng nước ngoài trong CMS · dạng từ ngẫu nhiên không pattern (case Deco-crystal — không block pattern được). | Coder + GTV | DOCX §I-8 · XLSX-QT C17 + MỞ RỘNG |

---

## P3 — Xử lý hậu quả SEO (GTV chủ trì)

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| MD-20 | **Lập list URL rác đầy đủ** | Gom từ 4 nguồn: (1) `site:domain` + `site:domain + keyword spam`; (2) GSC Pages (indexed + phát hiện mới); (3) GSC Links > Internal links (URL rác thường lọt vào đây); (4) logfile (URL rác đang được bot crawl). Output: 1 sheet theo dõi (mẫu: sheet "Mẫu - Audit Crawl" trong xlsx — audit theo status 2xx/3xx/4xx/5xx + URL bẩn + IP lạ). | GTV | XLSX-QT C21 · XLSX-AUDIT · DOCX §II-2.4 |
| MD-21 | **URL rác trả 410 (hoặc 404) + noindex** | URL rác phải trả **410 Gone** (ưu tiên — Google drop nhanh hơn) hoặc 404. ⚠️ **Modernize:** bản 2024 hướng dẫn "chuyển toàn bộ link độc 302 qua trang 404 - Noindex Follow" — KHÔNG dùng redirect 302 nữa: 302 giữ URL rác trong index lâu hơn và tốn crawl budget ([[Cost of Retrieval]]). Trả thẳng status code tại chính URL rác. Trang nào buộc phải giữ 200 → meta noindex. | Coder (GTV chỉ định list) | XLSX-QT C19 (legacy, đã thay) · [[Status Codes]] — 404/410 semantics |
| MD-22 | **De-index nhanh bằng GSC Removals** | GSC > Removals > New request: xóa tạm URL/prefix rác đã index (ưu tiên nhóm đang rank keyword spam). ⚠️ **Modernize:** thay thao tác "dùng Extension/UI Vision xóa hàng loạt" của bản 2024. Removals chỉ ẩn ~6 tháng — phải đi kèm 410/noindex (MD-21) mới mất hẳn. Thứ tự ưu tiên xóa: URL đang index (site:) trước → URL từ GSC internal link + phát hiện mới sau. | GTV | XLSX-QT D21 (OP1 legacy, đã thay) · DOCX §II-2.4 |
| MD-23 | **Sitemap tạm cho URL rác** | Tạo sitemap tạm (đặt tên riêng, vd malware-cleanup.xml) chứa list URL rác → submit GSC để Google re-crawl nhanh và **thấy 410** → drop index nhanh hơn. Gỡ sitemap tạm sau khi index rác về ~0. | GTV | XLSX-QT D21 (OP2 — giữ nguyên, vẫn đúng kỹ thuật) |
| MD-24 | **Kiểm tra sitemap.xml & robots.txt có bị sửa** | (1) Sitemap: xuất toàn bộ URL trong sitemap, so với list URL 200 chuẩn (Lead dự án nên có list dự phòng từ trước); check status code từng URL — có 2xx "lạ", 3xx, 4xx lọt vào không; (2) robots.txt: có bị hacker sửa (chặn trang thật / allow directory rác) không. Sitemap chính chỉ chứa URL 200 canonical thật. | GTV | XLSX-QT C4 · DOCX §II-1.2 + GTV 2026 (robots tamper check — bản cũ thiếu) |
| MD-25 | **Robots.txt block pattern URL rác — đúng thời điểm** | CHỈ block sau khi **tỉ lệ index rác đã giảm** — block sớm thì Google không crawl lại được để thấy 410 → URL kẹt trong index. Cách làm khi mã độc có pattern (tiền tố số, parameter): Disallow pattern; nếu chặn diện rộng `Disallow: /*` phải allow ngược các folder cần thiết, **nhớ allow robots.txt + sitemap**. Test lệnh bằng robots.txt Tester/report trong GSC trước khi up. Mã độc dạng từ ngẫu nhiên (Deco-crystal) → không block pattern được, dựa vào 410 + Removals. | GTV đề xuất → Coder up | XLSX-QT C25, D25 · DOCX §II-2.8 + MỞ RỘNG · [[Robots.txt]] |
| MD-26 | **Submit Security Review trong GSC** | Nếu GSC Security Issues có flag (hacked content / deceptive site / malware) hoặc SERP hiện "This site may be hacked": sau khi sạch (P2 xong + MD-21 xong) → GSC Security Issues > **Request Review**, mô tả rõ đã làm gì. Review pass thì cảnh báo trên SERP mới gỡ. ĐẠT = status "No issues detected". | GTV | GTV 2026 — bản 2024 thiếu hoàn toàn bước này |
| MD-27 | **Audit + disavow backlink bẩn** | Site bị mã độc thường **bị bắn kèm backlink bẩn** trỏ về URL rác → audit backlink giai đoạn này (Ahrefs/GSC Links), lọc và disavow domain rác. Chỉ disavow nhóm rõ ràng thuộc đợt tấn công — không disavow tràn lan. | GTV | XLSX-QT C24, D24 · DOCX §II-2.7 |
| MD-28 | **Xử lý trên SERP khác (Bing…)** | Từ logfile check bot nào ngoài Google đã crawl URL rác (Bingbot…) → xử lý tương ứng bên đó: Bing Webmaster Tools submit lại sitemap + dùng công cụ chặn/xóa URL của SERP đó. | GTV | XLSX-QT C26, D26 · DOCX §II-2.9 |
| MD-29 | **Follow tiến độ + handoff sang checklist khôi phục** | Follow theo 3 kênh của bản gốc cho tới khi ổn định: (1) GSC Pages — index rác giảm, không phát sinh mới; (2) site: — trang chủ + URL 200 index lại chưa (chưa → submit lại tới khi index); URL parameter bẩn còn index → tiếp tục xóa; (3) Logfile — event URL rác giảm, không IP mới. Khi đạt: mã độc sạch (MD-19) + index rác giảm rõ + URL 200 chính đã index lại → **chuyển sang `checklist-khoi-phuc-seo-ranking.md` (KP-01)**. | GTV | XLSX-QT C28-C32 · DOCX §II-3 |

---

## P4 — Phòng ngừa (sau sự cố / áp cho mọi dự án mới)

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| MD-30 | **Hardening đăng nhập & phân quyền** | Đổi link đăng nhập CMS khỏi /wp-admin/ mặc định; xóa file editor trong admin (Appearance/Plugin editor); permission chỉ-xem cho user không cần sửa code; khóa/chặn cài plugin tự do; bật **2FA cho toàn bộ admin**. | Coder | DOCX §III + GTV 2026 (2FA — bản cũ thiếu) |
| MD-31 | **Chính sách tài khoản** | Tài khoản admin đúng thông tin thật, password mạnh, đổi pass định kỳ; mỗi người 1 tài khoản riêng (không share chung 1 admin) để truy vết được. | Coder + Account (phổ biến cho khách) | DOCX §III + GTV 2026 (tách account — bản cũ thiếu) |
| MD-32 | **Cập nhật & vá định kỳ** | WordPress core + theme + plugin luôn bản mới nhất; bật auto-update cho plugin ổn định; gỡ plugin/theme không dùng (deactivate chưa đủ — phải xóa). | Coder | DOCX §III · XLSX-QT D6, D8 |
| MD-33 | **Backup + lớp bảo vệ thường trực** | Backup định kỳ tự động (giữ ≥2 bản, có bản offsite); security plugin (Wordfence/Solid Security) chạy thường trực; cân nhắc WAF/CDN (Cloudflare) chặn tầng trước server. | Coder | DOCX §III (backup) + GTV 2026 (WAF — bản cũ thiếu) |
| MD-34 | **Monitoring phát hiện sớm** | Thiết lập theo dõi định kỳ (đưa vào nhịp audit tháng của dự án): GSC Security Issues + email alert GSC; `site:domain` quick-check; GSC Pages đếm indexed bất thường; scan file integrity định kỳ từ security plugin. Phát hiện sớm = xử lý trong window 14 ngày, [[Historical Data]] ít tổn thương. | GTV | GTV 2026 — bản cũ thiếu monitoring chủ động |
| MD-35 | **Kiểm tra mã độc trước khi nhận dự án** | "Phòng bệnh hơn chữa bệnh": trước khi nhận dự án SEO mới → chạy nhanh MD-01/MD-02/MD-03 (triệu chứng + site: + cloaking check) như một bước due-diligence. Phát hiện di chứng mã độc cũ → báo Account đưa vào scope/điều khoản trước khi cam kết KPI. | GTV + Account | DOCX §II-4 ("nên kiểm tra mã độc định kỳ và trước khi nhận dự án") |

---

## Tài liệu đọc thêm (giữ từ xlsx sheet "Tài liệu đọc thêm")

- Anicca — *WordPress Site Hacked: Fake Spam URLs Indexed – RESOLVED*: `anicca.co.uk/blog/wordpress-site-hacked-fake-spam-urls-resolved/`
- Case study VN: khắc phục website bị hack index tiếng Nhật/Trung — `dotrungquan.info`, `brandsvietnam.com/congdong/topic/21129`, `kienthuc24.net`
- Phân loại malware website: `vuihocweb.com/bao-mat-website/cac-loai-malware-website-bi-nhiem-ma-doc`
- Nội bộ (link Google Docs trong xlsx): tổng hợp nghiên cứu mã độc (chị Trang) + file quy trình gốc.

## Nguồn & ghi chú provenance

- **Nguồn chính:** `Checklist xử lý mã độc website - GTV SEO.xlsx` (2024) — đọc đủ 4 sheets. Sheet "Mẫu - Audit Crawl 2110-111" là case thật Deco-crystal (7.674 URL bẩn, audit theo status code) → dùng làm mẫu sheet theo dõi ở MD-20.
- **Nguồn phụ:** docx `Quy trình, checklist & hướng dẫn XỬ LÝ MÃ ĐỘC và khôi phục SEO Ranking.docx` (10/2024) — **đọc được full text**; phần II của docx trùng ~90% sheet Quy trình xlsx (bản diễn giải chi tiết hơn); phần I (ESS xử lý source) và phần III (phòng ngừa) chỉ có trong docx. Ảnh minh họa trong docx (screenshot phpMyAdmin đổi DB prefix) không extract — không ảnh hưởng nội dung checklist.
- **Modernize 2026:** MD-21 (bỏ 302→404, thay bằng 410 tại chỗ), MD-22 (bỏ UI Vision, thay GSC Removals). **Thêm mới** so với bản 2024: MD-01, MD-04, MD-05, MD-07, MD-16, MD-26, MD-34 + 2FA/WAF/tách-account trong P4.
- **SOP liên quan:** `tier-3-technical-advance.md` mục 2 (Crawl & Index Health — dùng chung cách đọc GSC Crawl Stats khi follow MD-29), mục 8-9 (chuẩn Sitemap/Robots.txt khi verify MD-24/MD-25).
