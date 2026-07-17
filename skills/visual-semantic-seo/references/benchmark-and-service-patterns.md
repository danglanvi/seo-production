# Benchmark and service application patterns

## VN E-commerce Visual Patterns (NEW v3.1 — benchmark CellphoneS + TGDĐ, 07/2026)

10 pattern verified từ 2 SERP leader VN (CellphoneS = chuẩn cao nhất, TGDĐ = á quân) qua crawl heading + screenshot full-page desktop & mobile + audit thực tế MTM. Evidence: `wiki/syntheses/vn-ecommerce-visual-patterns-cps-tgdd-2026.md`.

| # | Pattern | Rule |
|---|---|---|
| 1 | **Personalized carousel placement** | "Sản phẩm đã xem" đặt ĐẦU PLP, CHỈ render khi có data (TGDĐ). Không xếp chồng 2 carousel cá nhân hoá; wishlist về trang tài khoản. |
| 2 | **Flash-sale placement** | PLP: dải section riêng có countdown ngay DƯỚI filter, 1 hàng cuộn ngang, không đè filter/grid. Homepage: khối tab-theo-ngày + countdown + progress suất thật ("Còn 15/15 suất"). Countdown luôn từ CMS — ngày ảo = trust-breaker. |
| 3 | **Mobile spec-elevation (PDP)** | Mobile-first: Thông số + FAQ đặt NGAY SAU gallery, TRƯỚC khối giá/variant; sticky bottom buy-bar (giá + trả góp + CTA) lo chuyển đổi (CPS mobile). Desktop giữ buy-box cột phải. |
| 4 | **Condition-as-attribute (hàng cũ)** | Tình trạng máy (Cũ đẹp/Trầy xước/Xước cấn/Đã kích hoạt) = entity attribute hạng nhất: filter facet ở PLP + trong TÊN card ("… - Cũ Đẹp") + variant PDP có giá riêng + `Product.itemCondition` schema. Giá cũ hiện % rẻ hơn máy mới (CPS: 38-59%). |
| 5 | **Category FAQ vs PDP UGC-Q&A** | UGC hỏi-đáp CHỈ ở PDP (gắn SP cụ thể, admin SLA trả lời). Category chỉ giữ FAQ biên tập cấp danh mục (FAQ **content** — FAQPage schema không còn rich result từ 07/05/2026, không phải lever; 2026-07-13) — tránh block UGC rỗng lặp mọi trang. |
| 6 | **Entity > Commercial attribute weighting trên card** | Card PLP 7-8 lớp; thứ tự visual: Giá (to nhất) → entity attrs (variant/màu/spec chips) → 1 dòng promo → social proof. Khối promo không được to hơn giá; logo thanh toán/trust seller không lặp per card (clutterScore). |
| 7 | **Spec grouping 7 nhóm (PDP)** | Bảng thông số gom 7 block chunk: Màn hình / Camera / Hiệu năng / Pin & Sạc / Kết nối / Thiết kế & Chất liệu / Tiện ích (TGDĐ) — mỗi nhóm tự đứng, trích xuất được. |
| 8 | **Trade-in service page** | H1 → definition-first (blockquote) → cam kết bullet → QUY TRÌNH bằng HTML ordered list (không chỉ trong ảnh banner) → H3 per loại máy/brand → spoke URLs (`/thu-cu/iphone`…) → FAQ đặc thù dịch vụ → công cụ định giá online = core function (function validation). |
| 9 | **Homepage section heading = entity name** | H2 section = tên danh mục thật ("Điện thoại", "Laptop", "Hàng cũ" — CPS); adjective marketing ("Laptop chất lượng", "PC đỉnh cao") ra khỏi heading, xuống sub-line (goldmineHeadingFactor). |
| 10 | **Facet definition tooltip** | Chip nhu cầu (chơi game / pin trâu / chụp ảnh) kèm tooltip định nghĩa spec tối thiểu ("RAM 12GB + 120Hz + pin 5000mAh + chip từ A19 Pro…" — TGDĐ): absolute facts cho taxonomy, gắn nhãn SP nhất quán. |

**Homepage theo Source Context:** thứ tự section homepage phải phản ánh thứ tự ưu tiên entity của site (vd Apple Authorized Reseller: iPhone → MacBook → iPad → Watch → phụ kiện Apple → dịch vụ thu cũ/hàng cũ → brand khác → danh mục phụ hạ thành tile strip). Homepage dàn hàng ngang mọi danh mục = Source Context pha loãng.

---

## Koray Live-Site Patterns (NEW v3.2 — sutliffstout.com · morethanpanel.com · oscarwylee.com.au, 07/2026)

11 pattern verified trên 3 site case-study của Koray (legal service YMYL · SMM panel transactional · eyewear e-commerce AU) qua mobile screenshot full-page + heading/markup crawl + **ranking data Ahrefs 07/2026**. Evidence: `wiki/syntheses/koray-live-site-patterns-2026.md`.

Ranking evidence: sutliffstout.com homepage top 5-8 cụm "houston car accident attorney" (CPC ~$60, org value ~$160K/tháng) · oscarwylee `/glasses.html` **#1 "glasses" 23K vol AU**, `/mens-glasses` #1-2 cả cụm · morethanpanel 99K traffic/tháng nhưng 97% từ 1 trang `/free-instagram-views`.

| # | Pattern | Rule |
|---|---|---|
| 1 | **Review-proof TRÊN H1** | Money page đặt rating badge (điểm + số review + avatar/logo Google) ngay TRÊN H1 (SS: 4.9★/551 · MTP: 4.8/5) — trust signal vào viewport trước cả entity claim. |
| 2 | **Definition-first dưới H1** | Đoạn đầu tiên = câu trả lời định nghĩa tuyệt đối cho query H1 (không lead marketing), truncate "read-more"; MTP nhắc cả đối thủ (Buzzoid, Twicsy) trong định nghĩa — information gain + độ trung lập. |
| 3 | **Question-form heading network** | H2→H5 literal dạng câu hỏi; cây heading = representative question → supporting questions (Query Network render thẳng thành outline). |
| 4 | **Micro-template attribute lặp per entity** | Mỗi entity con trong list nhận đúng 1 bộ heading con cố định (mỗi injury: H4 Common Symptoms / Settlement Value Factors / Required Documentation + H5 Claim Impact / Defense Strategy / Legal Considerations) — máy trích xuất được, người so sánh được. |
| 5 | **E-A-V thành chip + con số tuyệt đối** | Attribute hiển thị thành badge (MODERATE · SOFT TISSUE) + khoảng giá trị số in đậm to ($10K–$100K mild / $250K–$1M+ chronic; giá $0.50–$500K) — numeric range = quality node, không giấu trong text. |
| 6 | **Variant enumeration có heading riêng** | Biến thể theo attribute (số lượng 10→1M followers; chất liệu Titanium/Acetate/TR90 đánh số 1-7; Global/Country-Targeted/Drip-Feed) — mỗi variant 1 H3 + mini-definition + chip/nút riêng. |
| 7 | **Core function nhúng ngay money page** | Calculator giá (MTP), lead form + case-type quick picker (SS), booking CTA persistent trong sticky header (OW "Book an Eye Test") — function validation ngay trên trang rank. |
| 8 | **Template re-instantiation across spokes** | Cùng 1 template heading + layout, chỉ thay central entity noun (followers↔likes · car-accident↔rideshare · glasses↔mens-glasses) — context sharpening bằng danh từ trung tâm, cấu trúc giữ nguyên để so sánh cross-page nhất quán. |
| 9 | **Entity consolidation qua redirect** | `/houston-uber-accident-lawyer/` → 301 `/houston-rideshare-attorney/` — gộp Uber/Lyft về 1 concept "Rideshare" rộng hơn, 1 entity 1 page, tránh cannibalization. |
| 10 | **Freebie spoke magnet** | Bản FREE của dịch vụ trả phí làm spoke riêng (`/free-instagram-views` gánh 96.7K/99K traffic domain, bắt cả competitor-brand queries) — magnet đầu funnel dẫn về money page. |
| 11 | **PLP mobile: accordion hoá content network** | OW mobile: grid 15/212 + load-more, card tối giản (ảnh → tên riêng → giá → bundle badge "2 from $199" → swatch); SEO text dưới grid thu thành accordion câu hỏi + jump chips (Characteristics & Suitability / Styling & FAQ) — giữ đủ content, không đè commerce. |

**⚠️ Counter-signals (liều lượng, đừng copy mù):** SS homepage 340 headings, MTP `/pricing` 4.355 H5 (cả catalog render thành heading) — heading bloat/clutterScore thật; 2 money page MTP (`/buy-instagram-followers`, `/buy-instagram-likes`) hiện gần như mất ranking, `/pricing` bị chủ động `noindex`; heading có typo programmatic ("usersfind") = dấu hiệu scaled content. Pattern đúng ở CẤU TRÚC — mật độ phải theo clutterScore của skill này.

---

## Marketplace PDP Patterns (NEW v3.3 — benchmark Amazon B0CZ3S7S3P, 07/2026)

9 pattern verified từ 1 listing chuẩn UGC do Vincent chỉ định (Dgroositon rattan plug-in pendant — 4.5★/165, Amazon's Choice, "50+ bought in past month") qua Playwright capture desktop 1440px (15 slice) + mobile 390px (17 slice) + DOM facts extract, 10/07/2026. Evidence + 10 ảnh chú giải: `Deliverables/IndochinaLight/indochinalight_PDP-Review_v2.html` mục 8. Phạm vi: pattern **thương mại/UGC cho PDP** — bổ sung cho khung PDP zone-weight của skill này và VN pattern #3.

| # | Pattern | Rule |
|---|---|---|
| 1 | **Isolated buy-box card** | Mọi decision element gom trong 1 card viền riêng, đúng thứ tự: giá → phí ship minh bạch → **delivery date cụ thể theo NGÀY** ("Get it by Monday, July 20") → stock status có màu → CTA chính/phụ 2 màu phân cấp → trust ledger 4 dòng (Ships from / Sold by / Returns / Payment). Delivery promise theo ngày là microcopy chuyển đổi mạnh nhất — trả lời "bao giờ tới?" ngay tại điểm mua. |
| 2 | **Variant card self-priced** | Mỗi option mang giá + compare-at + tồn kho riêng ("Only 14 left in stock") ngay trên card chọn — không pill trần bắt khách bấm dò. Scarcity per-variant (số thật) đáng tin; urgency generic ("26+ views") là anti-pattern. |
| 3 | **E-A-V mini table in-fold** | Bảng attribute 5-6 dòng (Brand/Color/Material/Style/Form) đứng TRƯỚC About bullets ngay trong fold — "page as database render" tại centerpiece. Mobile: "Top highlights" 6 dòng visible mặc định, spec dài vào accordion in-DOM — attribute quyết định không bao giờ nằm trong accordion (2 trục v3.2.2). |
| 4 | **Identity-first mobile order** | Mobile xếp title + rating + badge + social proof TRƯỚC gallery — quyết định "đọc tiếp hay không" xong trong viewport 1; ATC/Buy-Now full-width nằm trong ~viewport 2. Đảo với desktop (gallery trái, info giữa, buy-box phải). |
| 5 | **Sticky in-page nav** | Segmented jump-link (Top · Details · Explore · Reviews) sticky trên cả 2 thiết bị — trang 13.000px nhưng mọi zone cách 1 tap (Cost of Retrieval thấp trong 1 URL). Bản brand-store: hàng anchor chips `#id` dưới buy box (Specs · Size Guide · Care · FAQ · Reviews), thuần anchor, KHÔNG fetch-on-click. |
| 6 | **About-bullets 【benefit-label】** | 5 bullet, mỗi bullet mở bằng nhãn 【benefit】 + 1 chủ đề trọn vẹn (material → install → application → cord → dimension), đứng trước mọi carousel — scan 10 giây nắm đủ ý. |
| 7 | **Room-tabs use-case block** | 1 khối ảnh × N tab theo phòng (Kitchen Island · Dinner Room · Porch · Reading Room · Bedroom) — PQ "hợp phòng nào?" trả lời bằng visual; content các tab nằm sẵn trong DOM. Với PDP có RQ "Who is this for?": khối này chính là thân của RQ. |
| 8 | **UGC-as-attribute-layer** | "Customers say" (đoạn consensus AI từ review, GIỮ cả ý chê — "size receives mixed feedback") + aspect chips kèm tần suất (Appearance 27 · Quality 20 · Space-friendly 12 · Cord length 6…) = bảng E-A-V thứ hai do khách viết; mỗi chip = 1 PQ được đám đông trả lời + là filter reviews. Consensus + histogram luôn server-rendered (chỉ review text chi tiết gate sau sign-in). Ít review → viết consensus thủ công TRUNG THỰC từ review thật, đếm chips bằng số thật — không bịa. |
| 9 | **Social-proof recency tĩnh** | "50+ bought in past month" = 1 dòng text im dưới title — không popup, không countdown; chỉ dùng khi số kiểm chứng được (đây là bản đúng của sales-pop). |

**⚠️ Counter-signals (marketplace ≠ brand store — KHÔNG copy):** title 193 ký tự nhồi 8 cụm keyword (luật search nội sàn; brand store giữ H1/title entity sạch — goldmine hygiene) · **13 thẻ H1, 29 H2 phẳng, 0 JSON-LD, div-soup** (Amazon có domain power + data feed riêng với Google; site thường phải thắng bằng Product schema đầy đủ (GTV 4-field benchmark — Google required chỉ là name + 1 trong review/rating/offers) + heading sạch) · attribute rác trong bảng spec ("Connectivity Protocol: Ethernet", "Control Method: Touch" trên đèn dây kéo — seller điền bừa; attribute SAI tệ hơn attribute THIẾU, Pegasus) · 6+ sponsored carousel chen giữa content (clutterScore marketplace chịu được vì khách đến để so hàng; brand store vỡ conversion layer) · gate review text sau sign-in (chỉ hợp lý khi UGC là moat khổng lồ cần chống scrape — shop ít review phải server-render toàn bộ).

---

## Service Page Application Playbook (NEW v3.4 — dịch benchmark thương mại sang trang dịch vụ, 07/2026)

Đúc từ 3 bộ benchmark đã verify của skill này sang **service page**: (a) case GTV **Minh Tuấn Mobile** — trang dịch vụ Thu Cũ + đối chiếu CPS/TGDĐ + báo cáo Koray Benchmark #5 (evidence: `Deliverables/MTM-iPhone-PLP-Review/` — file `MTM_Home_DienThoai_ThuCu_Feedback_v1.html`, `MTM_Koray_Benchmark_v1.html`); (b) **Koray live-sites** (module v3.2 — sutliffstout chính là service page YMYL rank top 5 cụm CPC ~$60); (c) **Amazon PDP** (module v3.3). Nguyên tắc dịch: **dịch vụ = sản phẩm vô hình** — mọi pattern thương mại đều có bản service nếu thay product attribute bằng service attribute (deliverable · SLA · timeline · người thực hiện · phạm vi · kết quả đo được). Đi cùng wiki [[Service Landing Page]] (1-2 RQ + 20-30 PQ, 3 layers Problem Awareness → Service Details → Decision) và references: `service-page-visual-template.md` · `trust-stacking-hierarchy.md` · `multi-tier-pricing-pattern.md` · `real-time-function-validators.md`.

### Bảng dịch pattern → service page

| # | Pattern gốc (nguồn) | Bản service page |
|---|---|---|
| S1 | Isolated buy-box + delivery date (AMZ #1) | **Quote-box cô lập**: gói/giá from → **response-time promise** ("Nhận báo giá trong 24h" / "Audit mẫu trong 48h" = delivery date của dịch vụ) → slot/lead-time thật → CTA chính (Đặt lịch/Nhận báo giá) + phụ (Gọi/Chat) → trust ledger 4 dòng (đơn vị thực hiện / cam kết-hoàn tiền / thanh toán / bảo hành công việc). |
| S2 | Variant self-priced (AMZ #2) + Multi-Tier Pricing | Gói per-tier mang **giá + phạm vi + capacity thật** ngay trên card ("Nhận thêm 2 dự án tháng này") — scarcity của service là capacity/lịch thật, không countdown ảo. Best Offer badge theo `multi-tier-pricing-pattern.md`. |
| S3 | E-A-V mini table in-fold (AMZ #3) | **Bảng "thông số dịch vụ"** trong fold: thời lượng · deliverables · SLA · người thực hiện · hình thức (online/onsite) · phạm vi — thay cho adjective ("chuyên nghiệp, tận tâm"). Service cũng có spec. |
| S4 | Review-proof trên H1 (Koray K1 / Trust L1) | Giữ nguyên cho service: rating + số review + logo nền tảng (Google Reviews) trên/sát H1 — SS 4.9★/551 là mẫu chuẩn. |
| S5 | Definition-first (K2 + CPS thu-cũ) | H2 "Dịch vụ X là gì?" định nghĩa tuyệt đối trong `<blockquote>` ngay sau hero — kể cả trên money page; nhắc competitor/phương án thay thế trong định nghĩa = information gain + trung lập (MTP nhắc Buzzoid/Twicsy). |
| S6 | Quy trình = markup thật (case MTM Thu Cũ) | H2 Quy trình dùng `<ol>` HTML 4-6 bước — **KHÔNG chỉ nằm trong ảnh banner** (OCR đọc được nhưng không thay được markup); mỗi bước 1 hành động + 1 dòng thời gian. |
| S7 | Micro-template per entity (K4) | Mỗi dịch vụ con / ngành phục vụ nhận đúng 1 bộ heading con cố định lặp ≥3 lần: *Phù hợp với ai / Deliverables / Timeline / Giá from / Kết quả đo được* — patterned data cho máy, so sánh được cho người. |
| S8 | E-A-V chip + con số tuyệt đối (K5) | Kết quả dịch vụ render thành **numeric range in đậm** ("+200-300% traffic / 6 tháng", "$10K–$100K settlement") + badge mức độ — không giấu số trong văn xuôi; mỗi số phải có case thật đứng sau. |
| S9 | Variant enumeration heading riêng (K6) | Biến thể dịch vụ (theo quy mô / ngành / hình thức) = mỗi biến thể 1 H3 + mini-definition + anchor — không chỉ là option trong form (MTP: 10→1M followers mỗi mức 1 chip + định nghĩa). |
| S10 | Core function nhúng (K7 + MTM wireframe F5) | **Công cụ sống ngay money page**: calculator báo giá / định giá / estimator — flow ≤5 bước, **kết quả tạm tính hiện sớm** (từ bước 2-3, trước khi hỏi SĐT); mobile mở bottom-sheet từng bước. Form thu lead KHÔNG phải function — calculator mới là "trang làm được việc" (contentEffort). |
| S11 | Freebie spoke magnet (K10) | Bản FREE của dịch vụ đứng thành spoke riêng (audit mẫu miễn phí · tool kiểm tra · mẫu template) → funnel về money page — /free-instagram-views gánh 96.7K/99K traffic domain là bằng chứng trần. |
| S12 | Room-tabs use-case (AMZ #7 + K3) | **Tabs theo tình huống/ngành khách hàng** ("Cho e-commerce · Cho SaaS · Cho local business") — PQ "dịch vụ này hợp ai?" trả bằng visual, đồng thời là thân RQ. Trục câu hỏi lấy **attribute của USER** (OW: tông da/dáng mặt/màu mắt), không chỉ attribute dịch vụ. |
| S13 | UGC-as-attribute-layer (AMZ #8 + Trust L3-L5) | Testimonial nén thành **aspect chips kèm tần suất** ("Đúng hạn (12) · Chất lượng report (8) · Hỗ trợ (6)") + đoạn "Khách nói gì" tổng hợp trung thực; video testimonial có **tên thật + role** (SS: H3 per reviewer). Bản mạnh nhất của UGC service = case study có số (schema **Article** — type CaseStudy không tồn tại). |
| S14 | Social-proof recency tĩnh (AMZ #9 / Trust L6) | "N dự án hoàn thành quý này / đang chạy" — 1 dòng text hoặc stats bar, số thật kiểm chứng được, không popup. |

### Khung 14 block service page (hợp nhất 3 nguồn — thay khung 5 block cũ khi cần bản đầy đủ)

```
 1. HERO: rating badge sát H1 (S4/L1) → H1 tên dịch vụ → subtitle → CTA chính+phụ   [Centerpiece 100%]
 2. Definition-first "X là gì?" blockquote 40-75 từ (S5)                             [100%]
 3. QUOTE-BOX cô lập: giá from · response-time promise · slot thật · trust ledger (S1) [100%]
 4. Bảng thông số dịch vụ E-A-V (S3)                                                 [80%]
 5. Trust strip: badge chứng nhận + logo báo chí/khách hàng (L2 — kéo từ đáy lên)     [strip 5-10%]
 6. Benefits → Services: mỗi service con = <article> + micro-template (S7)           [Centerpiece 100%]
 7. Use-case tabs theo ngành/tình huống — RQ "hợp ai?" (S12)                          [Supporting 80%]
 8. Quy trình <ol> 4-6 bước thật (S6)                                                [60-80%]
 9. CÔNG CỤ SỐNG: calculator/estimator, tạm tính hiện sớm (S10)                       [100% function]
10. Case studies: numeric range đậm + schema Article (S8)                             [60-80%]
11. Pricing tiers + capacity thật (S2)                                               [60-80%]
12. Testimonials: aspect chips + video tên/role (S13/L3-5)                            [60%]
13. FAQ đặc thù dịch vụ 8-12 PQ + final CTA                                          [40% + conversion]
14. Team profiles (L7) pre-footer                                                    [40%]
```
Mobile: anchor chips (Quy trình · Bảng giá · Case study · FAQ · Reviews) dưới quote-box + sticky CTA trên header (OW "Book an Eye Test") — thay cho sticky buy-bar của PDP.

**⚠️ Counter-signals cho service page:** heading adjective ("Dịch vụ chuyên nghiệp/tận tâm/đỉnh cao") — heading = entity/câu hỏi, adjective xuống body (bài học MTM homepage, goldmineHeadingFactor) · quy trình/cam kết chỉ nằm trong ảnh banner (mất markup — case MTM Thu Cũ) · numeric claim không có case thật đứng sau (Pegasus; YMYL service càng nặng) · form-only không có công cụ sống (form ≠ function validation) · heading bloat programmatic (MTP 4.355 H5 → money pages decay + noindex) · trust signals rải ngẫu nhiên không compound — phải đúng vị trí 7 layer (`trust-stacking-hierarchy.md`).

---
