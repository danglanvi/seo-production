---
type: sop
status: stable
checklist_type: event # chạy sau sự cố xác định, không chạy định kỳ
event: khôi phục SEO ranking sau sự cố (hack đã sạch / penalty đã gỡ / mất index diện rộng)
last_updated: 2026-07-19
items_count: 24
source_raw:
  - "raw/_ingested/Quy trình SEO PSP - All In One/Quy trình, checklist & hướng dẫn XỬ LÝ MÃ ĐỘC và khôi phục SEO Ranking.docx" # §II-4 "Thúc đẩy lại ranking" — đọc được full text
  - "raw/_ingested/Quy trình SEO PSP - All In One/Checklist xử lý mã độc website - GTV SEO.xlsx" # sheet "Thúc đẩy CRAWL" + sheet "Quy trình" mục Follow
related:
  - "[[Historical Data]]"
  - "[[Initial Ranking]]"
  - "[[Re-Ranking]]"
  - "[[Quality Thresholds]]"
  - "[[Index Pollution]]"
  - "[[Internal Linking Rules and Strategy]]"
  - "[[Topical Authority]]"
  - "[[URL SEO]]"
prev_checklist: "checklist-xu-ly-ma-doc.md"
tags: [sop, event-checklist, recovery, ranking, re-crawl, index, historical-data]
---

# Event Checklist — Khôi phục SEO Ranking sau sự cố (KP-01 → KP-24)

> **Khi dùng:** SAU khi sự cố đã được xử lý xong về mặt kỹ thuật — hack đã sạch (checklist-xu-ly-ma-doc P1–P3 hoàn tất), penalty/manual action đã gỡ, hoặc mất index diện rộng đã tìm ra và fix nguyên nhân. Checklist này phục hồi lại crawl → index → ranking.
>
> **⚠️ RANH GIỚI với `tier-3-ranking-drop-runbook`:**
> - **Ranking-drop runbook** = công cụ **chẩn đoán** khi ranking rớt mà **chưa biết nguyên nhân** (rớt thường: algo update, đối thủ, decay…). Chạy runbook trước để xác định nguyên nhân.
> - **Checklist này (KP)** = quy trình **phục hồi** khi nguyên nhân **đã xác định và đã xử lý xong** (hack/penalty/mất index). Không dùng file này để chẩn đoán.
> - Nếu đang ở giữa: rớt ranking + nghi mã độc chưa xác nhận → runbook chẩn đoán trước; xác nhận mã độc → `checklist-xu-ly-ma-doc.md` → rồi mới quay lại đây.
>
> **Logic phục hồi (thứ tự bắt buộc):** Xác nhận sạch (gate) → thúc đẩy re-crawl → khôi phục index → khôi phục ranking → theo dõi 30-60-90 ngày. Không skip gate — thúc đẩy crawl khi site chưa sạch = mời Google index lại rác nhanh hơn.
> **Nền tảng kỳ vọng:** [[Historical Data]] của site đã tổn thương trong sự cố; [[Re-Ranking]] cần thời gian tích lũy lại tín hiệu — phục hồi là quá trình theo tuần/tháng, không phải theo ngày. File gốc 2024 đã ghi thẳng: *"khả năng mất trust rank lẫn việc khôi phục lại thứ hạng như ban đầu có thể khó xảy ra"* — quản trị kỳ vọng khách ngay từ đầu (KP-20).

**Ký hiệu cột Nguồn:** `DOCX §…` = docx mục II-4 (Thúc đẩy lại ranking) & II-3 (Follow) · `XLSX-CRAWL` = xlsx sheet "Thúc đẩy CRAWL" · `XLSX-QT` = xlsx sheet "Quy trình" · `GTV 2026` = bổ sung mới.

---

## Phase A — GATE: Xác nhận sạch (đủ 5/5 mới đi tiếp)

> Cả 5 items dưới phải ĐẠT trước khi làm Phase B. Thiếu bất kỳ item nào → quay lại `checklist-xu-ly-ma-doc.md`, KHÔNG thúc đẩy crawl/index.

| ID | Hạng mục | Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| KP-01 | **Rescan source sạch** | Security scan chạy lại toàn bộ: 0 phát hiện; coder xác nhận đã vá vector gốc (plugin/credentials/hosting); qua tối thiểu 3–4 ngày theo dõi không phát sinh file/URL rác mới (= MD-19 pass). | Coder xác nhận, GTV verify | DOCX §I-8 |
| KP-02 | **GSC Security Issues cleared** | GSC Security Issues = "No issues detected". Nếu từng bị flag → Request Review (MD-26) đã được **approve**, cảnh báo SERP đã gỡ. Với case penalty: Manual Actions = "No issues detected". | GTV | GTV 2026 (bản 2024 thiếu) |
| KP-03 | **Google thấy đúng source — hết cloaking** | GSC URL Inspection > View crawled page: data Google thu thập khớp source thật trên 3–5 URL đại diện (home, URL SEO, blog). Screaming Frog đổi user-agent Googlebot/Bingbot: không còn thấy URL spam. | GTV | XLSX-QT D30 · DOCX §II-3.2 B2 |
| KP-04 | **Logfile ổn định** | Event crawl URL rác giảm về ~0; không IP bất thường mới; bot chủ yếu quay lại crawl URL 200 chất lượng (home, URL SEO, sitemap, robots.txt). | GTV | XLSX-QT C31-C32 · DOCX §II-3.3 |
| KP-05 | **Index rác không phát sinh lại** | `site:domain` + `site:domain + keyword spam` và GSC Pages: số index rác giảm liên tục, **không phát sinh mới trong ≥7 ngày liên tiếp**. (Index rác cũ có thể chưa về 0 — chấp nhận, miễn là trend giảm và không mọc mới.) | GTV | XLSX-QT C29, D29 · DOCX §II-3.1-3.2 · [[Index Pollution]] |

---

## Phase B — Thúc đẩy Re-crawl

> Nguồn chính: xlsx sheet **"Thúc đẩy CRAWL"** (6 tactics) — giữ nguyên logic, modernize công cụ. Mục tiêu: kéo bot quay lại crawl dày hơn để thấy site đã sạch → cập nhật lại đánh giá. Theo dõi hiệu quả bằng GSC Crawl Stats (cách đọc: `tier-3-technical-advance.md` mục 0 — không lặp lại ở đây).

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| KP-06 | **Submit lại toàn bộ sitemap** | Re-submit sitemap index + toàn bộ sitemap con trong GSC (và Bing WMT nếu sự cố lan sang SERP khác — MD-28). Verify sitemap chỉ chứa URL 200 canonical (đã clean ở MD-24). Theo dõi "Last read" + số discovered URLs trong GSC Sitemaps. | GTV | XLSX-QT D26 · chuẩn sitemap: tier-3 mục 8 |
| KP-07 | **Indexing API — nếu áp dụng được** | Bản 2024 ghi "Cài API cho site". ⚠️ **Modernize:** Google Indexing API chỉ **chính thức hỗ trợ JobPosting/BroadcastEvent** — site thường dùng ngoài scope là gray-hat, hiệu quả không bảo đảm và có rủi ro. Nếu site đúng vertical → dùng; site thường → ưu tiên KP-06 + KP-09 + Bing IndexNow (chính thống, Bing/Yandex). | GTV | XLSX-CRAWL B1 (legacy, đã gắn caveat) + GTV 2026 (IndexNow) |
| KP-08 | **Google News (nếu đủ điều kiện)** | Set up Google News / Publisher Center và kết nối từ bài blog ngược lại Google News — chỉ áp dụng site có content dạng news đủ điều kiện. Site dịch vụ/ecom thường không đủ → skip, không cố. | GTV | XLSX-CRAWL B2 |
| KP-09 | **Hubpage + internal link từ trang crawl thường xuyên** | (1) Tạo/refresh Hubpage tổng hợp URL bài viết/dịch vụ; (2) chèn link URL ít crawl + URL Hubpage vào các vị trí bot ghé dày: trang chủ, footer, bài TF/traffic cao, GMB post, social post. Đây là tactic kéo crawl mạnh nhất trong bộ 2024 — internal link là đường dẫn crawl chính ([[Internal Linking Rules and Strategy]]). | GTV | XLSX-CRAWL B4, B6 |
| KP-10 | **Refresh tín hiệu fresh cho URL ít crawl** | Điều chỉnh Description + đoạn sapo 100 chữ đầu cho list URL ít được crawl (tín hiệu content fresh → mời bot quay lại). Title/H1: cân nhắc kỹ — chỉnh có thể ảnh hưởng thứ hạng đang có, chỉ đụng khi thật cần. | GTV | XLSX-CRAWL B3 |
| KP-11 | **Schema hỗ trợ re-crawl** | Với URL ưu tiên: cập nhật trường `dateModified`; chèn link Hubpage trong citation ở bài TF cao; rút gọn schema theo chuẩn hiện hành (schema phình to tốn [[Cost of Retrieval]]). | GTV | XLSX-CRAWL B5 |
| KP-12 | **Phát tán URL kéo bot ngoài site** | Đẩy URL ít crawl + Hubpage ra kênh ngoài: social post, GMB/Google Business post, web 2.0, các trang có bot ghé dày. Mục tiêu là discovery path, không phải backlink số lượng. | GTV | XLSX-CRAWL B6 |

---

## Phase C — Khôi phục Index

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| KP-13 | **Ưu tiên URL SEO cam kết trước** | Lập list ưu tiên request indexing (URL Inspection > Request indexing) theo thứ tự: (1) trang chủ; (2) **URL SEO cam kết KPI** ([[URL SEO]]); (3) URL từng có organic traffic cao; (4) category/hub; (5) còn lại theo sitemap. Submit lại "cho tới khi index" (nguyên tắc bản gốc). | GTV | XLSX-QT D29 · DOCX §II-4 B1.2 + GTV 2026 (thứ tự ưu tiên theo URL SEO cam kết) |
| KP-14 | **Theo dõi coverage hồi phục** | GSC Pages theo tuần: (1) indexed count của URL thật hồi dần về mức trước sự cố; (2) index rác tiếp tục giảm về ~0; (3) lý do "Not indexed" của URL thật (Crawled-not-indexed / Discovered-not-crawled) không tăng. Ghi số liệu vào sheet theo dõi (cùng sheet MD-20). | GTV | XLSX-QT C28-C29 · DOCX §II-3.1 |
| KP-15 | **Re-index tín hiệu offpage** | Re-index toàn bộ sitemap lẫn các tài sản offpage cũ: backlink, social stack, google stack — để Google crawl lại và **lấy lại tín hiệu trust sẵn có** cho site (tài sản đã build trước sự cố là lợi thế phục hồi, không phải build mới). | GTV | DOCX §II-4 B1.4 |

---

## Phase D — Khôi phục Ranking

| ID | Hạng mục | Cách làm / Tiêu chí ĐẠT | Vai | Nguồn |
|---|---|---|---|---|
| KP-16 | **Baseline + phân loại URL ảnh hưởng** | Lấy baseline ranking/traffic **trước sự cố** (đã chụp ở MD-08; nếu thiếu → GSC Performance compare 28 ngày trước sự cố vs hiện tại + rank tracker history). Liệt kê URL: rớt traffic / rớt top / đang tự hồi. URL đang dần khôi phục → chỉ phân loại & follow, **không đụng vào**; URL kẹt → vào KP-17. | GTV | DOCX §II-4 B1.2-3 |
| KP-17 | **Audit lại URL target bị kẹt** | Với URL kẹt ranking, kiểm 4 mục của bản gốc: (1) onpage & content so với thị trường (SERP hiện tại — có thể đối thủ đã vượt trong lúc mình xử lý sự cố); (2) onpage & content so với checklist GTV (P-series / SCA); (3) internal link Theme–Trust về URL đó; (4) các bài topic cluster liên quan còn đủ và còn index không. | GTV | DOCX §II-4 B3 |
| KP-18 | **Tối ưu thí điểm 1 cụm → follow 14 ngày → scale** | Chọn **1 cụm URL cụ thể** (không làm cả site cùng lúc): tối ưu chuẩn lại + update sapo/200 chữ đầu tạo tín hiệu fresh → request index → follow 14 ngày. Kỳ vọng đúng bản gốc: **7–10 ngày đầu đôi khi thấy rớt thêm** — bình thường ([[Re-Ranking]] cần chu kỳ đánh giá lại); sau 14 ngày có tín hiệu tăng = tốt → lên kế hoạch scale cụm còn lại. Không tăng = giữ nguyên cụm đó, thử biến số khác, không tối ưu đè liên tục. | GTV | DOCX §II-4 B4 (mục 2-4) |
| KP-19 | **Tăng trust bổ sung — chỉ khi cần + có phê duyệt** | Điều kiện kích hoạt (nguyên tắc bản gốc): xử lý sự cố kéo dài **>15 ngày** VÀ sau xử lý **~5 ngày** không thấy phục hồi đáng kể. Menu bản 2024 theo thứ tự ưu tiên: cloud stack & google stack → social stack (50–100 link) → backlink forum → backlink PR → backlink PBN → traffic user. Đích: home, category, blog pillar/hub, URL SEO, URL traffic. ⚠️ **Guardrail 2026:** PBN + traffic user = tactic rủi ro với site vừa mất trust — bắt buộc SEO Lead trình **Director phê duyệt** trước khi chạy; ưu tiên nửa đầu menu (stack/social/PR) + gate "cần-link-không" của skill `backlink-plan`. | GTV + Director approve | DOCX §II-4 B2 (legacy menu, đã gắn guardrail) |
| KP-20 | **Quản trị kỳ vọng khách qua Account** | Account chuyển thông điệp cho khách ngay đầu Phase D: (1) [[Historical Data]] bị tổn thương — Google cần thời gian tích lũy lại tín hiệu, phục hồi tính theo **tuần/tháng**; (2) timeline kỳ vọng thực tế: index hồi trước (2–6 tuần), ranking hồi sau (6–12 tuần tùy mức độ + độ cạnh tranh); (3) không cam kết hồi 100% vị trí cũ — file gốc 2024 đã ghi rõ khả năng này; (4) báo cáo theo mốc 30-60-90 (Phase E), không báo theo ngày. Escalate khách ép cam kết → SEO Lead + Director. | Account (nội dung từ GTV) | DOCX §II-4 (đoạn mở đầu) + GTV 2026 (timeline + cơ chế báo cáo) |

---

## Phase E — Theo dõi 30-60-90 ngày & tiêu chí đóng

> Mốc tính từ ngày pass GATE (Phase A). Mỗi mốc: GTV cập nhật sheet theo dõi + Account gửi khách 1 báo cáo ngắn.

| ID | Hạng mục | Tiêu chí ĐẠT tại mốc | Vai | Nguồn |
|---|---|---|---|---|
| KP-21 | **Mốc 30 ngày** | (1) Index rác = 0 hoặc còn không đáng kể và trend về 0; (2) coverage URL thật ≥ **80–90% baseline**; (3) GSC Crawl Stats bình thường trở lại (response 200+304 chiếm chủ đạo, HTML là tỷ trọng chính — chuẩn tier-3 mục 2); (4) cụm thí điểm KP-18 có tín hiệu tăng. Lệch → soi lại Phase B/C trước khi đổ lỗi cho ranking. | GTV | GTV 2026 (khung mốc) trên nền follow XLSX-QT C28-C32 |
| KP-22 | **Mốc 60 ngày** | (1) Ranking URL SEO cam kết hồi ≥ **70–80% baseline** (số keyword top 10 so với trước sự cố); (2) organic traffic hồi ≥ 70% baseline; (3) không còn URL rác mới trong GSC suốt 60 ngày. Đạt → scale tối ưu toàn bộ list KP-16. | GTV | GTV 2026 |
| KP-23 | **Mốc 90 ngày — tiêu chí "đã phục hồi" / "cần review Director"** | **ĐÃ PHỤC HỒI** (đóng event, về nhịp vận hành thường): index sạch + ranking/traffic ≥ **90% baseline** HOẶC < 90% nhưng trend tăng đều 4 tuần liên tiếp. **CẦN REVIEW DIRECTOR**: < 70% baseline và plateau ≥ 3 tuần dù đã chạy đủ KP-17/18 (+KP-19 nếu được duyệt) → Director quyết: đổi chiến lược (content/[[Topical Authority]] rebuild), đàm phán lại KPI với khách, hoặc chấp nhận rebuild dài hạn. Đã áp dụng đủ các bước mà chưa tự tin/chưa tăng trưởng → luật gốc 2024: **liên hệ Line Manager để được hỗ trợ** — không tự xoay một mình. | GTV + Director | GTV 2026 (ngưỡng) + DOCX §II-4 B4.5 (escalate Line Manager) |
| KP-24 | **Post-mortem & đóng hồ sơ** | Ghi vào log dự án: nguyên nhân gốc, timeline xử lý (ngày phát hiện → sạch → pass gate → các mốc phục hồi), % phục hồi cuối, tactic nào hiệu quả/không, bài học. Verify P4 phòng ngừa (MD-30 → MD-35) đã triển khai đủ — sự cố lặp lại vì bỏ P4 là lỗi quy trình, không phải rủi ro. | GTV + Account | GTV 2026 |

---

## Nguồn & ghi chú provenance

- **Nguồn chính:** docx `Quy trình, checklist & hướng dẫn XỬ LÝ MÃ ĐỘC và khôi phục SEO Ranking.docx` (10/2024) — **đọc được full text** (206 đoạn + bảng Thúc đẩy CRAWL); phần §II-4 "Thúc đẩy lại ranking & lưu ý" (4 bước + điều kiện kích hoạt + escalate Line Manager) là xương sống Phase C/D. Lưu ý nhỏ: trong docx, danh sách "Bước 4: Tối ưu lại các URL Target" bắt đầu từ mục 2 (mục 1 nhiều khả năng mất trong định dạng numbered-list của file gốc) — nội dung không thiếu ý chính.
- **Nguồn phụ:** xlsx `Checklist xử lý mã độc website - GTV SEO.xlsx` — sheet **"Thúc đẩy CRAWL"** (6 tactics → KP-06…KP-12) + sheet "Quy trình" mục Follow (C28-C32 → KP-04/05/14).
- **Modernize 2026:** KP-07 (caveat Indexing API + thêm IndexNow), KP-19 (guardrail Director approve cho PBN/traffic user). **Thêm mới** so với bản 2024: KP-02 (security review cleared), KP-13 (thứ tự ưu tiên theo URL SEO cam kết), KP-20 (timeline + thông điệp Account), toàn bộ Phase E khung 30-60-90 + tiêu chí đóng (KP-21…KP-24) — bản 2024 dừng ở "follow 14 ngày", chưa có tiêu chí "đã phục hồi".
- **SOP liên quan:** `checklist-xu-ly-ma-doc.md` (bắt buộc chạy trước) · `tier-3-technical-advance.md` mục 0 + 2 (cách đọc GSC Crawl Stats — dùng ở KP-21, không duplicate ngưỡng tại đây) · `tier-3-ranking-drop-runbook` (chẩn đoán rớt thường — xem ranh giới đầu file) · skill `backlink-plan` (gate cần-link-không cho KP-19) · skill `content-refresh` (nếu sau 90 ngày phát hiện decay không liên quan sự cố).
