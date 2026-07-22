---
type: sop
tier: 3
phase: audit-diagnosis
last_updated: 2026-07-19
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/4. SEO Audit/Review khi rớt và google update/2. Checklist kiểm tra.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/4. SEO Audit/SEO Factors Checklist Audit - 12.2.xlsx
items_count: "6 triage + 96 items / 10 nhánh = 102"
tags: [sop, tier-3, ranking-drop, google-update, runbook, seo-audit, diagnosis]
---

# Tier 3 — Ranking Drop Runbook (Rớt hạng / Google Update)

> **Khi dùng:** Keyword/URL/site rớt hạng hoặc mất traffic, hoặc nghi trùng Google update. Team **tự chạy runbook này trước khi escalate** — escalate không kèm output form (cuối file) = trả về.
> **Cấu trúc:** Bước 0 Triage 15 phút (TR-01→06, chạy 100%) → routing → 10 nhánh phân ngành (chỉ chạy nhánh được route) → Output form kết luận.
> **Nguồn:** Xương sống từ "2. Checklist kiểm tra.xlsx" (10 sheet phân ngành, legacy ~2020) + đối chiếu "SEO Factors Checklist Audit - 12.2.xlsx" (81 factors). Đã modernize 2026 — xem cột **Nguồn**: `L` = legacy giữ nguyên, `L*` = legacy đã modernize, `M` = mới thêm 2026.

**Nguyên tắc:** KHÔNG đổ lỗi nội tại (content/technical/backlink) trước khi loại trừ 3 nguyên nhân ngoại lai: (1) rớt ảo do data, (2) Google update, (3) SERP layout đổi (AI Overview chiếm click ≠ rớt ranking). Đó là lý do TR-02/03/04 đứng đầu runbook.

---

## Bước 0 — Triage nhanh (15 phút, chạy đủ 6 bước, theo thứ tự)

### TR-01 — Xác nhận rớt THẬT: data GSC vs rank tracker `M`

- Đối chiếu rank tracker vs GSC (Performance → query/page, so sánh 28 ngày vs 28 ngày trước). Tracker rớt nhưng GSC position ổn định → nghi rớt ảo: tracker đổi location/device, SERP cá nhân hóa, hoặc lỗi tool.
- Check cả 3 chỉ số GSC: **position / impressions / clicks** — pattern khác nhau chỉ nguyên nhân khác nhau (legacy 81 factors đã có 3 items "CTR/Impression/Traffic bị rớt đột ngột" nhưng tách rời; nay gộp thành 1 phép đọc):
  - Position giữ + clicks rớt → nghi SERP feature/AIO (→ TR-04).
  - Impressions rớt mạnh + position giữ → nghi mất index/coverage (→ nhánh RD-T).
  - Cả 3 cùng rớt → rớt ranking thật (→ TR-02).
- Loại trừ seasonal: so sánh YoY cùng kỳ nếu ngành có mùa vụ.

### TR-02 — Trùng Google update timeline không? `M`

**Check TRƯỚC khi đổ lỗi nội tại.** Đối chiếu ngày bắt đầu rớt với Google Search Status Dashboard (update công bố) + các nguồn theo dõi volatility. Nếu trùng update (±3 ngày):

- Update **chưa roll out xong → KHÔNG kết luận, KHÔNG sửa lớn** — chỉ ghi nhận và theo dõi tới khi Google confirm hoàn tất.
- Roll out xong → phân loại update (core / spam / helpful-content-signal / product review) để chọn nhánh: core → RD-C + RD-P; spam/link → RD-B; ranh giới mờ thì chạy RD-C trước.
- Đánh giá tương quan thị trường: đối thủ cùng rớt hay chỉ mình rớt? Cả thị trường xáo trộn = update tái phân phối; chỉ mình rớt = nội tại (legacy file "4. Đánh giá tổng quan thị trường khi có update").

### TR-03 — Phạm vi rớt: site-wide / cụm topic / 1 URL `M`

- **Site-wide** (đa cụm cùng rớt) → ưu tiên RD-T (technical), RD-E (entity/trust), RD-B (offpage), RD-S (cấu trúc). Nghi manual action → GSC Manual Actions + Security Issues check ngay (legacy factor "GSC bị tác vụ thủ công").
- **1 cụm topic** → RD-P (topic bổ trợ), RD-C (content cụm), RD-I (internal link cụm), RD-F (phân bổ lực).
- **1 URL / 1 nhóm keyword** → RD-C + RD-O (onpage) + cannibalization check.
- Xuất danh sách URL/keyword bị ảnh hưởng kèm mức rớt (top cũ → top mới) làm input cho các nhánh.

### TR-04 — AI Overview / SERP feature layer: mất CLICK ≠ mất RANKING `M`

**Bước phân biệt bắt buộc, đặt sớm** — bài mất traffic vì AIO chiếm SERP là chẩn đoán hoàn toàn khác rớt hạng:

- Search (ẩn danh, đúng location) 5-10 query đại diện: SERP có AIO mới xuất hiện không? AIO có cite mình không? Feature mới nào chiếm above-the-fold (AIO, Shopping pack, video, forum/UGC block như Reddit)?
- Signature của "AIO ăn click": position GSC ổn định + impressions ổn định/tăng + **CTR & clicks rớt**.
- Nếu đúng signature → đây là bài toán **GEO/CTR, không phải bài toán ranking** → route sang skill `geo-content-optimization` (audit AX1-AX5, counter-positioning) + kết luận trong output form là "AIO displacement", KHÔNG chạy 10 nhánh nội tại cho các URL này.
- SERP feature khác đổi (video pack mới, local pack mới) → note vào RD-C item intent/SERP elements.

### TR-05 — Thay đổi gần đây trên site (change log) `L*`

Legacy sheet 0.Technical mở đầu bằng "Thay đổi code" — tổng quát hóa: liệt kê MỌI thay đổi 2-4 tuần trước ngày rớt: deploy code, đổi theme/plugin, migration/đổi URL, sửa content hàng loạt, đổi internal link/menu, chiến dịch backlink mới, đổi robots.txt/sitemap. Không nhớ phiên bản cũ → dùng Wayback Machine (giữ nguyên từ legacy). Thay đổi trùng thời điểm rớt = giả thuyết ưu tiên số 1.

### TR-06 — Chốt routing + độ sâu

Điền bảng routing (dưới), chọn nhánh chạy. Rule độ sâu: rớt nhẹ (top 3→8) chạy 2-3 nhánh nghi nhất; rớt nặng (ra khỏi top 20) hoặc site-wide → chạy tối thiểu 5 nhánh trước khi kết luận.

### Bảng routing

| Tín hiệu từ triage | Nhánh ưu tiên |
|---|---|
| Trùng deploy/đổi code (TR-05) | RD-T → RD-S |
| Site-wide, không trùng update | RD-T → RD-E → RD-B |
| Trùng core update, roll out xong | RD-C → RD-P → RD-U |
| Trùng spam/link update | RD-B → RD-E |
| 1 cụm topic rớt | RD-P → RD-C → RD-I → RD-F |
| 1 URL rớt / keyword nhảy URL | RD-C → RD-O (+ cannibalization RD-C-08) |
| Impressions rớt mạnh (mất index) | RD-T (index/coverage trước) |
| CTR rớt, position giữ, không AIO | RD-O (title/meta/favicon) + RD-C |
| AIO signature (TR-04) | → `geo-content-optimization`, dừng runbook cho URL đó |

---

## RD-T — Technical (12 items)

**Chạy khi:** trùng deploy/đổi code; site-wide drop; impressions rớt mạnh; GSC coverage bất thường.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-T01 | Thay đổi code & audit lại toàn site | Crawl full (Screaming Frog) sau mỗi lần đổi code, diff với crawl cũ; không có bản cũ → Wayback Machine | L |
| RD-T02 | Crawlability + logfile | Response codes, trang chặn nhầm robots.txt/noindex; logfile: Googlebot còn crawl các URL rớt không, tần suất đổi thế nào | L |
| RD-T03 | Index/Coverage GSC | Page indexing report: lượng Excluded tăng đột biến, duplicate w/o canonical, alternate w/ canonical, "Crawled - not indexed" tăng; URL rớt còn indexed không (URL Inspection) | L |
| RD-T04 | **GSC Crawl Stats** | Settings → Crawl Stats: total crawl requests rớt đột ngột, avg response time tăng, host status lỗi (robots fetch fail, DNS, server 5xx) — crawl sụt trước ranking sụt vài tuần | M |
| RD-T05 | **Core Web Vitals** | GSC CWV report + PageSpeed Insights (field data): LCP ≤2.5s / INP ≤200ms / CLS ≤0.1; nhóm URL rớt có rơi vào "Poor" sau đổi giao diện không. (Thay bộ Lighthouse-lab-metrics legacy: First interactive, TTFB, render-blocking — vẫn dùng làm chẩn đoán lab, nhưng chỉ số quyết định là field CWV) | M |
| RD-T06 | Mobile parity | Mobile-first index: bản mobile đủ content/structured data/internal link như desktop không; UX mobile lỗi. (Legacy "code mobile vs desktop" giữ; tool Mobile Friendly Test đã khai tử 2023 → dùng Chrome DevTools + crawl mobile UA) | L* |
| RD-T07 | Rendering JS | Content chính render client-side không index được; URL Inspection → Live Test → rendered HTML + page resources load đủ; content sau tab/interaction | L |
| RD-T08 | Redirect & response codes | Chuỗi 301 mới xuất hiện, redirect không cần thiết, top pages dính 404 (ưu tiên khôi phục, 301 là phương án hai), lỗi 5xx tần suất | L |
| RD-T09 | Canonical & tham số | Canonical bị đổi/tự trỏ sai sau deploy, tracking query strings trong link nội bộ tạo duplicate | L |
| RD-T10 | Sitemap & robots.txt | Sitemap còn đúng URL sống không, broken links trong XML sitemap, robots.txt bị đổi khi deploy | L |
| RD-T11 | Breadcrumbs + schema | Breadcrumb hiển thị đúng cấu trúc, schema breadcrumb khớp hiển thị, Google nhận diện đúng; schema chính còn valid sau deploy (Rich Results Test) | L |
| RD-T12 | HTTPS & bảo mật | Mixed content sau deploy, cert hết hạn, site bị hack/mã độc (GSC Security Issues) — hacked content là nguyên nhân rớt site-wide kinh điển | L |

> **Bỏ khỏi checklist (ghi chú lịch sử):** rel=next/prev pagination (2 items legacy — Google xác nhận không dùng từ 2019; pagination giờ chỉ cần crawlable links + canonical đúng). AMP (2 items legacy — không còn là yêu cầu Top Stories từ 2021, dự án mới không triển khai AMP; site cũ còn AMP chỉ check lỗi hiển thị). Bing Webmaster Tools hạ xuống optional.

---

## RD-C — Content (12 items)

**Chạy khi:** trùng core/helpful update; 1 URL hoặc 1 cụm rớt; CTR thấp bất thường; nghi cannibalization.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-C01 | Intent vs SERP hiện tại | Search lại query (ẩn danh): intent SERP có ĐỔI không (mùa vụ, event, Google đổi theo user data — legacy đã note "changed intent"); content type/format mình còn khớp đa số top 10 không → đối chiếu O1 (3Cs, Dominant/Fractured/Hybrid) | L |
| RD-C02 | Chất lượng vs top hiện tại | Bài mình vs 3 bài đang top: coverage, depth, evidence, information gain — đối thủ mới vượt lên hay mình đứng yên? (6 tiêu chí O16) | L |
| RD-C03 | Cannibalization | Dấu hiệu legacy giữ nguyên: keyword lên 2 URL cùng lúc; keyword lên SAI URL; URL lởn vởn top 7-20 không vào sâu. Fix: gộp/redirect/phân hóa intent + đối chiếu keyword-URL mapping | L |
| RD-C04 | Thin/duplicate content trên cụm | Bài mỏng, mô tả sản phẩm copy nguồn khác, tag pages tạo thin content hàng loạt, comment spam | L |
| RD-C05 | Semantic quality theo chuẩn hiện hành | Bài rớt có đạt chuẩn wiki hiện tại không: L0 answer-first, EAV density, heading hierarchy — audit nhanh bằng `semantic-content-audit` thay cho cảm quan "giọng điệu - lời văn" của legacy. (TF-IDF legacy: ghi chú lịch sử, không còn dùng làm thước đo — thay bằng entity/attribute coverage) | L* |
| RD-C06 | Crucial data (facts) lỗi thời | Số liệu/năm/giá trong bài đã cũ so với top 10; bài "Update 2024" giữa 2026 | L |
| RD-C07 | CTR keywords trọng điểm | GSC: CTR thấp hơn nhiều mức trung bình theo position; chỉ ưu tiên check khi rớt từ top 1-5 (rule legacy giữ) — title/meta nhạt, mất rich result, hoặc favicon/brand kém nổi bật | L |
| RD-C08 | SERP elements coi thiếu gì | Google có (video, image pack, PAA, FS) mà mình không có → bổ sung format tương ứng; FAQ rich result đã chấm dứt 05/2026 — FAQ content giữ trên trang nhưng không kỳ vọng rich result | L* |
| RD-C09 | Hình ảnh & video vs đối thủ | Nguyên tắc legacy giữ nguyên: đối thủ có ảnh unique/chất lượng/cụ thể → mình phải ngang hoặc hơn; video tương tự | L |
| RD-C10 | Drip feed / tần suất publish | Nhịp đăng có gãy không (legacy: đều đặn 3-5 tháng mới thấy kết quả; dồn cục rồi ngưng = tín hiệu xấu); cụm rớt có bị bỏ đói content mới 6+ tháng | L |
| RD-C11 | **Content decay vs update** | Phân biệt: rớt do decay từ từ (nhiều tháng, xu hướng mượt → route sang skill `content-refresh`) vs rớt gãy khúc do update/sự kiện (runbook này xử lý) | M |
| RD-C12 | **AI-generated quality risk** | Cụm rớt có phải batch content AI chưa qua QC 3-Level không (tick tracking sheet); pattern scaled content abuse: hàng loạt bài na ná, không first-hand experience, publish cùng đợt | M |

---

## RD-E — Entity & Brand (10 items)

**Chạy khi:** site-wide drop không rõ technical; trùng update nhắm trust/authority; site mới chưa qua T6; brand yếu so đối thủ.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-E01 | Entity onsite đồng nhất | Trang giới thiệu/liên hệ/chính sách đầy đủ; NAP đồng nhất onsite-offsite | L |
| RD-E02 | Schema entity tổng thể | Organization, LocalBusiness, WebSite, AboutPage + khai báo thành tố (header/footer/nav) còn valid, @id graph nhất quán — đối chiếu skill `schema-markup-generator` | L |
| RD-E03 | Author entity | Bài YMYL/cụm rớt có author thật, bio, trang author, schema Person; author có dấu chân chuyên môn ngoài site không | L |
| RD-E04 | Brand search volume | Traffic brand search còn giữ mức nền không (legacy: tối thiểu 50-60 search/tháng tùy thị trường); brand search rớt cùng lúc = vấn đề brand, không phải SEO thuần | L |
| RD-E05 | Google Business Profile | GBP (tên mới của GMB) còn active/không bị suspend; branded + direct search trong insight giữ ~20% | L* |
| RD-E06 | Knowledge Graph / entity recognition | Brand có KG panel chưa, đã claim chưa; Google nhận diện đúng entity brand không | L |
| RD-E07 | Index các property entity | Social profiles, Google stack còn indexed không — link entity không index = không tính | L |
| RD-E08 | H1/logo trang chủ | Trang chủ H1 = logo, alt = brand name; trang khác logo không mang H1 (rule legacy giữ) | L |
| RD-E09 | PR & mentions nền | Gói PR entity/anchor thương hiệu còn chạy đúng nhịp không; mentions mới có xuất hiện đều không | L |
| RD-E10 | **E-E-A-T surface signals** | Cụm YMYL rớt sau core update: trích dẫn nguồn, credential tác giả, first-hand experience, trang editorial policy — đối chiếu `google-content-standard` (khung E-E-A-T thay thế các item IFTTT/social-stack legacy vốn đã hạ độ ưu tiên: syndication auto footprint 2026 rủi ro hơn lợi ích, chỉ giữ khi có kiểm soát chất lượng) | M |

---

## RD-O — Onpage (10 items)

**Chạy khi:** 1 URL/nhóm keyword rớt; sau đợt tối ưu onpage hàng loạt; CTR rớt không do AIO.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-O01 | Title & meta description | Bị đổi gần đây? Google có rewrite title trên SERP không; meta còn khớp intent | L |
| RD-O02 | URL & lịch sử đổi URL | URL đổi mà thiếu 301, hoặc redirect nhưng mất tín hiệu | L |
| RD-O03 | H1 + heading structure | 1 H1/page, hierarchy H2-H6 đúng sau đổi theme (theme mới hay phá heading bằng CSS class) | L |
| RD-O04 | Semantic HTML | List ra đúng `<ol>/<ul>`, đoạn văn ra `<p>`, bảng ra `<table>` — legacy đã nhắc "Semantic HTML giúp Google hiểu rõ hơn", nay càng nặng ký vì chunk retrieval cho AI — đối chiếu `semantic-html-optimization` | L |
| RD-O05 | Keyword ở vị trí quan trọng | Title/H1/đoạn đầu/URL còn giữ keyword sau khi content bị sửa; keyword avoidance (dùng synonym tránh hẳn keyword chính) | L |
| RD-O06 | Answer-first cho câu hỏi | Câu hỏi được giải đáp ngay đầu section (legacy: tốt cho UX + Featured Snippet; 2026: thêm giá trị AIO citation) | L |
| RD-O07 | Schema bài viết | Article/Product/Review schema còn valid; rich result bị mất trên SERP so trước (đối chiếu GSC Enhancements) | L |
| RD-O08 | Hình ảnh: alt, caption, filename | Alt semantic còn nguyên sau migration/đổi CDN; ảnh bị đổi URL mất index ảnh | L |
| RD-O09 | External links | Link out tới nguồn uy tín còn sống; link out tới trang spam/hết hạn domain (bị redirect sang casino…) | L |
| RD-O10 | Internal links từ bài rớt | Outbound internal links trong bài còn đúng, không trỏ 404/redirect sau tái cấu trúc | L |

> **Bỏ:** AMP onpage (lịch sử — xem note RD-T). Keyword density hạ xuống ghi chú lịch sử — đo bằng EAV/semantic coverage (RD-C05) thay vì %.

---

## RD-P — Topic bổ trợ & Topical Coverage (8 items)

**Chạy khi:** cả cụm topic rớt; keyword chính không vào sâu dù URL tốt; trùng core update.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-P01 | Đủ bài bổ trợ trong cluster | Legacy rule giữ: tối thiểu 5 bài, thường 6-10 bài/cluster; cluster rớt có đủ không | L |
| RD-P02 | Ba tầng ngang-trên-dưới | Bài ngang cấp, bài cha (trên), bài con (dưới) đủ và publish hết chưa | L |
| RD-P03 | Coverage vs top 5 | Top 1-5 cover chủ đề gì mà cluster mình thiếu (legacy: "top 1 viết chủ đề A mình phải có") — chạy `competitor-consensus-content` để ra MANDATORY list | L* |
| RD-P04 | Search journey / funnel | Cluster có đủ bài theo giai đoạn journey không hay chỉ toàn bài commercial | L |
| RD-P05 | Chất lượng bài bổ trợ | Bài bổ trợ publish cho đủ số nhưng kém chất lượng → kéo cả cụm (helpful content signal site-wide) | L |
| RD-P06 | Topic bổ trợ còn thiếu | Re-run keyword/query research: topic bổ trợ quan trọng mới xuất hiện chưa cover | L |
| RD-P07 | **Topical map alignment** | Đối chiếu topical map hiện hành: cluster rớt là core hay outer, có bài lạc theme chính website làm loãng (relevance to central entity) | M |
| RD-P08 | **Query fan-out cho AI-era** | Cụm rớt trong SERP có AIO: các sub-query fan-out đã có bài/section trả lời riêng chưa (nhịp T7-T8 của timeline 10 tháng) | M |

---

## RD-U — UX & UI (10 items)

**Chạy khi:** rớt sau redesign/đổi theme; trùng core update (page experience); engagement metrics xấu đi.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-U01 | So sánh giao diện với thị trường | Site mình vs top 5: bố cục, format bài, mức đầu tư visual — thị trường redesign mà mình đứng yên? | L |
| RD-U02 | Above-the-fold & vị trí content | Content chính bị đẩy xuống bởi banner/ads/pop-up mới thêm? Intrusive interstitial mobile | L |
| RD-U03 | Thứ tự & format nội dung | Thứ tự thông tin (trái→phải, trên→dưới) còn khớp ưu tiên user; số lượng chữ vs chuẩn thị trường | L |
| RD-U04 | Tính năng hoạt động | Filter, calculator, form, on-site search… còn chạy không sau deploy (legacy: "tính năng có hoạt động không") | L |
| RD-U05 | Navigation & breadcrumb UX | Menu đổi làm mất đường vào cụm rớt; breadcrumb hiển thị đúng | L |
| RD-U06 | Ecommerce templates | PDP/PLP/checkout đối chiếu chuẩn (legacy dẫn Baymard — vẫn là benchmark tốt); biến thể sản phẩm, giá, review hiển thị đủ | L |
| RD-U07 | Đồng nhất mobile vs desktop | Giao diện + tính năng 2 bản không lệch nhau nghiêm trọng | L |
| RD-U08 | Review/UGC hiển thị | Review khách còn hiển thị + crawlable (legacy 81 factors: UGC phải rendered trước load xong) | L |
| RD-U09 | **Behavioral signals** | GA4: engagement rate, time on page của nhóm URL rớt xấu đi từ bao giờ — trước hay sau khi rớt ranking (trước = nguyên nhân, sau = hệ quả) | M |
| RD-U10 | **Visual semantic layout** | Centerpiece rõ ràng, block chunking, entity card — đối chiếu skill `visual-semantic-seo` (lớp mới thay cảm quan "wireframe tính năng" legacy) | M |

---

## RD-I — Internal Links (10 items)

**Chạy khi:** rớt sau tái cấu trúc menu/silo; cụm rớt có link profile nội bộ mỏng; crawl depth tăng.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-I01 | Internal link tới URL rớt | Đếm inbound internal links của URL rớt trước/sau (crawl diff); mất link từ menu/footer/bài lớn? | L |
| RD-I02 | Benchmark đối thủ | Ahrefs internal backlinks của URL đối thủ đang top: họ link từ topic nào mà mình thiếu (top 3 đều link từ bài X → mình cũng cần) | L |
| RD-I03 | Anchor text nội bộ | Đa dạng đúng tỷ lệ (exact/partial/semantic); anchor trùng exact hàng loạt gây cannibalization tín hiệu | L |
| RD-I04 | Vị trí đặt link | Link trong body bài > sidebar/footer; link trong H2/H3 context tốt (rule legacy giữ) | L |
| RD-I05 | Topic cluster linking | Cụm rớt: bài con ↔ bài cha ↔ ngang hàng đủ vòng chưa, orphan page trong cụm | L |
| RD-I06 | Crawl depth | URL quan trọng depth ≤3 (legacy: từ 4 trở đi khó crawl, >5 không chấp nhận trừ site >10k page); tái cấu trúc có đẩy URL rớt xuống sâu không | L |
| RD-I07 | Link score / internal PageRank | Screaming Frog link score: URL trọng điểm bị "gián đoạn" điểm sau đổi menu — thêm internal links hoặc cân nhắc vị trí navigation | L |
| RD-I08 | Lãng phí PageRank ở footer | Footer link hàng loạt trang không giá trị SEO (chính sách, pháp lý…) → gom mini-hub (giải pháp legacy giữ nguyên) | L |
| RD-I09 | Trust & traffic flow | Phân bổ trust đồng đều tới page cần tập trung; luồng link từ bài traffic cao về money page còn nguyên | L |
| RD-I10 | **Semantic relevance của link** | Link giữa 2 trang có contextual bridge thật không hay chỉ nhồi module "bài liên quan" — đối chiếu skill `internal-linking` (6 rules + flow to Core); TIPR legacy (PageRank×CheiRank×logfile×backlink) giữ làm kỹ thuật nâng cao cuối dự án | L* |

---

## RD-B — Offpage / Backlink (10 items)

**Chạy khi:** trùng spam/link update; số backlink biến động đột ngột; nghi negative SEO; site-wide drop đã loại trừ technical.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-B01 | Biến động backlink đột ngột | Ahrefs: referring domains tăng/giảm gãy khúc quanh ngày rớt; tăng đột ngột = nghi negative SEO (legacy giữ) | L |
| RD-B02 | Negative SEO / spam links | Backlink profile bị bắn hàng loạt link kém chất lượng → disavow (hiếm nhưng khi bị thì rõ) | L |
| RD-B03 | Mất backlink quan trọng | Lost links report: link từ trang mạnh trỏ URL rớt bị gỡ/đổi thành nofollow/trang nguồn chết | L |
| RD-B04 | Anchor text profile | Tỷ lệ exact match anchor quá cao (dấu chân thao túng); đối chiếu `references/anchor-ratio-framework.md` của skill backlink-plan | L* |
| RD-B05 | Chất lượng & theme của nguồn link | DR, traffic thật của trang nguồn, cùng theme không (keywords trong URL-Title-H1 của nguồn — rule legacy); diversify theme | L |
| RD-B06 | Footprint | Pattern lộ liễu: cùng IP/hosting, cùng template, cùng nhịp đặt link (checklist footprint GTV legacy) | L |
| RD-B07 | Link từ trang 404 / broken backlinks | Backlink trỏ về URL đã chết → khôi phục URL (ưu tiên 1) hoặc 301 (ưu tiên 2) | L |
| RD-B08 | Cân bằng ngoại lực | Phân bổ referring domains giữa các cụm có lệch nghiêm trọng không (cụm rớt đói link so cụm khác) | L |
| RD-B09 | Entity của backlink nguồn | Site vệ tinh/PBN còn được validate entity không (trang giới thiệu, GBP, schema) — site nguồn chết entity thì link mất giá | L |
| RD-B10 | **Link velocity vs đối thủ** | Nhịp link mình vs top 5 trong 6 tháng: đối thủ tăng tốc mà mình dừng → relative loss; chạy `backlink-research` cho data | M |

> **Ghi chú lịch sử:** Trust Flow / Citation Flow (Majestic) legacy — không còn là thước đo vận hành chính; giữ khái niệm "trust của nguồn" nhưng đo bằng DR + organic traffic thật của trang nguồn.

---

## RD-S — Cấu trúc Website (8 items)

**Chạy khi:** rớt sau migration/tái cấu trúc URL/menu; site-wide drop; cụm mới thêm phá theme.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-S01 | Visualize cấu trúc hiện tại | Crawl visualization: cấu trúc thực tế còn khớp thiết kế silo/topic cluster không, cụm nào bị "đứt" khỏi khối chính | L |
| RD-S02 | Thay đổi cấu trúc gần đây | Đổi URL pattern, gộp/tách category, đổi menu — có migration checklist đầy đủ không (redirect mapping) → nếu là sự kiện migration, chạy skill `site-migration-checklist` | L* |
| RD-S03 | Đồng nhất silo theo entity | Cụm cluster tối ưu đồng nhất từ tổng theme xuống từng silo: internal link + anchor, onpage, navigation | L |
| RD-S04 | Breadcrumb phản ánh đúng cấu trúc | 3 lớp legacy: hiển thị đúng — schema khớp — Google nhận diện đúng | L |
| RD-S05 | Navigation & giới hạn link | Nav dùng anchor rõ ràng theo entity, số link trên nav không phình to sau redesign | L |
| RD-S06 | Phân phối tín hiệu theo cấu trúc | Internal PageRank flow, crawl budget, sitemap priority, click depth phân bổ đúng trọng tâm SEO | L |
| RD-S07 | Cấu trúc thư mục ảnh | Image file structure mô phỏng silo (legacy — vẫn hợp lệ cho image ranking + semantic) | L |
| RD-S08 | Centralized vs Decentralized | Cấu trúc tập trung lực về core section hay dàn trải; cụm rớt thuộc khối nào trong thiết kế | L |

---

## RD-F — Phân bổ & Cân bằng lực (6 items)

**Chạy khi:** cuối chuỗi chẩn đoán — các nhánh khác không ra nguyên nhân rõ; hoặc cụm này lên thì cụm kia xuống (trade-off nội bộ). Legacy note giữ nguyên: đây là khâu nâng cao, thị trường cạnh tranh mới cần đào sâu.

| ID | Item | Check | Nguồn |
|---|---|---|---|
| RD-F01 | Cân bằng nội lực | Link score phân bổ theo: click depth, mức tập trung SEO, popularity (volume 6000 vs 300 phải khác điểm) — cụm rớt có bị rút lực cho cụm khác không | L |
| RD-F02 | Cân bằng ngoại lực | Referring domains/UR phân bổ giữa các cụm theo cùng logic; URL rớt đói cả nội lẫn ngoại lực | L |
| RD-F03 | Money page vs supporting | Lực dồn thẳng money page trong khi thị trường cho thấy supporting-content-first hiệu quả hơn (nguyên tắc backlink-plan) | L* |
| RD-F04 | Trade-off sau thay đổi | Sau đợt thêm link/content mới: cụm được thêm lên, cụm bị rút xuống — map lại dòng lực trước/sau | M |
| RD-F05 | Popularity re-check | Volume/demand các keyword đã đổi (trend giảm) → "rớt traffic" thực ra là demand giảm, không phải rớt lực | M |
| RD-F06 | Crawl budget allocation | Site lớn: Googlebot đang tiêu crawl budget vào khu vực rác (faceted, param) thay vì cụm quan trọng (logfile + Crawl Stats) | L |

---

## Output Form — Kết luận chẩn đoán (bắt buộc trước khi escalate)

Điền sau khi chạy xong các nhánh được route. **Không có form này = chưa chạy runbook.**

```
## Ranking Drop Diagnosis — [dự án] — [ngày]

### 1. Triage summary
- Rớt thật/ảo: … (TR-01, evidence GSC vs tracker)
- Phạm vi: site-wide / cụm […] / URL […]  (TR-03)
- Google update: có/không — update nào, ngày, roll out xong chưa (TR-02)
- AIO/SERP feature: có/không — URL nào là AIO displacement (route GEO riêng) (TR-04)
- Thay đổi trên site trùng thời điểm: … (TR-05)
- Nhánh đã chạy: RD-… / Items fail: RD-…

### 2. Giả thuyết nguyên nhân (xếp theo likelihood)
| # | Giả thuyết | Likelihood | Evidence (item IDs + data) | Next action | Owner | Deadline |
|---|---|---|---|---|---|---|
| 1 | … | Cao | RD-T04: crawl requests -60% từ 12/7… | … | … | … |
| 2 | … | Vừa | … | … | … | … |
| 3 | … | Thấp | … | … | … | … |

### 3. Escalation
- [ ] Không cần escalate — team tự xử lý theo next actions
- [ ] SEO Manager — khi: nguyên nhân xác định nhưng cần resource/quyết định ngoài thẩm quyền Lead
- [ ] SEO Director — khi: nghi core update ảnh hưởng chiến lược / cần đổi mục tiêu KPI / rủi ro hợp đồng
- [ ] Coder/Dev — khi: fail items RD-T (kèm danh sách item + evidence)
- [ ] Content Lead — khi: fail items RD-C/RD-P quy mô lớn (kèm danh sách bài)
- [ ] Account — khi: cần khách hành động (access, duyệt, gỡ thay đổi khách tự làm)

### 4. Theo dõi
- Chỉ số theo dõi: … (position/impressions/clicks nhóm URL)
- Điểm review lại: sau … ngày / sau khi update roll out xong
- Log vào 12-feedback-lessons nếu có bài học quy trình
```

**Quy tắc likelihood:** giả thuyết chỉ được xếp "Cao" khi có ≥2 evidence độc lập (vd: trùng thời điểm + item fail cụ thể). Không bao giờ ship kết luận chỉ dựa trên "trùng Google update" mà không có đối chiếu thị trường (TR-02).

**Kết nối:** nguyên nhân xác nhận là decay → `content-refresh` · AIO displacement → `geo-content-optimization` · migration → `site-migration-checklist` · technical sâu → `technical-seo-audit` · kết quả tháng đưa vào [[monthly-project-review]] MR-05.

---

## Đối chiếu coverage với nguồn legacy

| Nguồn | Lấy vào runbook | Bỏ / hạ cấp |
|---|---|---|
| "2. Checklist kiểm tra.xlsx" — 10 sheets (0.Technical → 9. Phân bổ lực) | Xương sống 10 nhánh RD-T/C/E/O/P/U/I/B/S/F; các rule định lượng giữ nguyên (cluster 6-10 bài, crawl depth ≤3-5, brand search 50-60, footer mini-hub, TIPR) | AMP (2 items), IFTTT/syndication auto (hạ cấp — footprint risk), TF-IDF (ghi chú lịch sử), Trust/Citation Flow (đổi thước đo) |
| "SEO Factors Checklist Audit - 12.2.xlsx" — 81 factors | Gộp vào các nhánh: coverage/excluded, canonical, rendering (client/dynamic/hybrid), out-of-stock & discontinued (RD-U06), UGC crawlable, favicon→CTR, mini-hub footer, tags thin content, negative SEO | rel=next/prev pagination (Google bỏ 2019), Mobile Friendly Test (tool khai tử 2023), AMP, Lighthouse lab metrics làm thước quyết định (→ field CWV) |
| Lớp mới 2026 (không có trong legacy) | TR-01→06 triage (đặc biệt TR-02 update timeline + TR-04 AIO/GEO), RD-T04 Crawl Stats, RD-T05 CWV/INP, RD-C11 decay-vs-update, RD-C12 AI content risk, RD-E10 E-E-A-T, RD-P07/08 topical map + query fan-out, RD-U09/10 behavioral + visual semantic, RD-B10 velocity, RD-F04/05 trade-off + demand shift | — |
