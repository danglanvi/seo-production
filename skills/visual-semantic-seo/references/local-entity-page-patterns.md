# Local Entity Page Patterns (v3.7)

> Pattern cho store/office location page, specialist person page, city/service local landing. Nguồn: Koray SEL 22/07/2026 (Oscar Wylee, allergist/pollen, Doktorsitesi, Pricelisto, CBD) + 4 wireframe mẫu (`raw/assets/local-seo-sel-2026/page-layout-semantic-5/6/7.webp` + `image-321`). Wiki: `[[Local SEO]]`, `[[cases/local-seo-sel-cases-2026]]`, `[[Surround Sound]]`.

## Nguyên tắc gốc

1. **Trang local tồn tại được phải pass QDP** — không mở trang cho mọi city/district/service; fail gate → thành section/component trên hub. Root của cụm local thường là trang "**[term] near me**", city hierarchy nằm dưới nó.
2. **"Helpful means functional"** — trang local thiếu function thật (book/route/compare/calculate) khó rank hậu HCU; function giả = misleading functionality (spam policy). Chưa có function → imitate có kiểm soát (form "book an appointment" gửi enquiry thật) trong khi build CMS.
3. **NAP + hours = GBP field parity từng ký tự** — trang web đóng vai 3rd-party consensus source cho chính entity của mình; Name/Address/Phone/Opening hours khớp verbatim với Google Business Profile để parser align với knowledge panel (hỗ trợ "open now" queries).
4. **Anti-doorway localization** — sibling store pages chung template phải khác nhau bằng region-bound attributes THẬT (CBD location, Medicare bulk billing, landmark, đội ngũ) — không đổi mỗi city name.

## Store / Office Location Page — 9 components

| # | Component | Chi tiết | Cơ chế |
|---|---|---|---|
| 1 | **Site-wide transaction entry** | Phone + booking CTA trong global nav — mọi trang cách core conversion 1 click | Conversion path ngắn |
| 2 | **Near-me hub breadcrumb** | `{Brand} / [Service] Near Me / [Store name]` — hub node ĐẶT TÊN theo near-me query class; mọi store page thừa kế context | Query class capture ở hub level |
| 3 | **H1 = entity fusion** | Service + place trong 1 entity: "Optometrist Canberra Centre" (retailer) hoặc brand + city: "Arvada {Brand}" (franchise — brand carry service ngầm) | 1 heading phủ cả doctor-name lẫn service+city queries |
| 4 | **Landmark grounding** | Địa chỉ + "Opposite {Anchor Store}" (spatial reference tương đối tới entity đã biết) + map pin GIỮA các landmark entities (không pin trơ trọi) | Đặt store vào city entity network |
| 5 | **NAP + hours block** | GBP field parity; disclaimer "hours exclude public holidays" = accuracy hedge trung thực | Consensus + click satisfaction |
| 6 | **Explicit GBP reconciliation** | Link đích danh "Visit our {Store} Google Business page for directions, reviews, updates" | Same-entity signal mạnh nhất brand tự control |
| 7 | **2-3 conversion modes** | Route (offline/directions) + Call + Book (online); mode 3 tùy chọn: **"Leave a Review!"** = review acquisition loop — không phải conversion mà là máy nuôi review signals | Đóng cả 2 nhánh intent local |
| 8 | **Imported review consensus** | Google reviews render TRONG trang (named reviewer + rating + recency) — 3rd-party consensus trong 1st-party document | Trust + UGC freshness |
| 9 | **Localized content block** | H2 "Find an [Occupation] in [City] With {Brand}" + region-bound attributes (anti-doorway) | Unique main content per store |

**GBP-attached map iframe:** mỗi GBP embed vào ĐÚNG trang khớp nó; GBP quan trọng nhất embed homepage (Oscar Wylee).

## Specialist / Person Entity Page — thêm trên nền store page

- **Person entity header**: {Doctor Name} + specialty binding 2 profession entities ("Otolaryngology (ENT), Allergology") — phủ cả doctor-name queries lẫn "[specialist] + [city]".
- **Breadcrumb sibling switcher**: segment city là DROPDOWN — breadcrumb expose topical map path xuống VÀ ngang (sibling cities) từ mọi practice page.
- **Progressive phone reveal** ("Show phone number") = engagement event log per lead.
- **Entity reconciliation links**: website + email trỏ domain riêng của practice — same-entity signals cross nguồn độc lập.
- **Opening hours = structured attribute set** mirror GBP 1-to-1.
- **Verbalization checklist** (Koray, case allergist): working hours · biography · background · address · expertise · valid insurances · reviews · Q&A — mỗi thứ là text thật trên trang, không chỉ trong widget.

## City / Seasonal Attribute Page (pollen-calendar pattern)

- **Geo utility bar** localize TRƯỚC khi content render ("Current pollen forecast for {City}") + specialist CTA — locality + transaction khai báo ở pixel row đầu.
- **H1 = temporal promise** ("Pollen calendar: discover when which pollen is in the air") — trang rank cho tổ hợp (entity con × tháng).
- **Symptom hook 2nd person** ("Is your nose itchy right now?") khớp symptom-based queries + prevalence stat.
- **Centerpiece = component dữ liệu**: calendar/matrix EAV — (pollen type, flies in, month) triples, intensity = attribute value; 1 component trả lời hàng trăm "when does X fly" queries không cần 1 đoạn văn per tổ hợp.
- **Sub-entity filters** (checkbox hazel/birch/grasses) — engagement data = relevance data.
- **Informational-to-transactional bridge**: CTA specialist đặt GIỮA hook và tool — convert trước payload informational; trang calendar link trang "find an allergist in [city]" (transactional child node).
- **Topical entry grid** cuối trang link quality nodes; EMA anchors cho subdistricts kèm context.

## Menu / Price Listing Page (Pricelisto pattern)

H1 = Brand + temporal + regional ("{Brand} Menu with Prices 2026 (United States)") · verification strip first-party ("prices confirmed at {store address}, updated {date}") · statistical summary trả superlative queries (most expensive / cheapest / average — extraction-ready 1 câu) · sub-menu taxonomy tabs theo QDP · item cards = cross-platform price triples (DoorDash/UberEats/GrubHub — information gain menu chính chủ không publish) · scale proof ("12,827 locations") · ingredient entity expansion → nutrition contexts.

## Store-Entity Skeleton — phần CHUNG vs phần theo business model

Từ diff matrix optometrist (appointment retailer) vs CBD franchise (`image-321`):

- **Skeleton chung (A=B)**: near-me hub · entity-fusing H1 · NAP + hours GBP parity · spatial grounding.
- **Khác theo business model (A≠B, không phải taste)**: hub depth (flat 1 cấp vs geo hierarchy 3 cấp theo store count) · H1 naming (service+place vs brand+city) · spatial proof (map landmark vs storefront photo + computed distance) · conversion modes (booking+review loop vs directions+shop online).
- **Chỉ 1 bên có (A!/B!)**: review module (retailer — cần acquisition loop) vs commerce fusion + franchise referral link graph (franchise).

→ Khi design store page mới: bắt đầu từ skeleton chung, chọn nhánh theo business model — KHÔNG copy nguyên trang mẫu khác model.

## Counter-signals (tránh)

- Trang [service]+[district] mở hàng loạt không qua QDP (case Melbourne 19 trang, Doktorsitesi 4M, "NYC to Erzurum").
- Store page rỗng khi tắt JS (CBD case: duplicate + canonicalize sai) — main content phải trong initial HTML.
- Hours/NAP lệch GBP; hours không hedge ngày lễ (stale hours phá click satisfaction).
- Doorway: sibling pages chỉ khác city name.
- Function giả (nút book không book) — spam policy + US12536233B1 trigger.
- Parameter filter URLs indexable ("?loc=…") — chuẩn: `#value` hoặc đổi content không đổi URL.
