---
type: sop
tier: 1
phase: visual-semantic
last_updated: 2026-07-19
source_file: sop/07-visual-semantic.md
items_count: 18
related:
  - "[[Visual Semantics]]"
  - "[[Centerpiece Annotation]]"
  - "[[Visual Semantic Weight]]"
  - "[[Blur Test]]"
  - "[[Website Functions]]"
tags: [sop, tier-1, visual-semantic, layout, self-checklist]
---

# Tier 1 — Self-Checklist: Visual Semantic (VS-01…VS-18)

> **Khi dùng:** Người làm layout (SEO lead / content / designer) tự check **từng page hoặc template** TRƯỚC KHI trình duyệt — sau khi có block map / mockup / build, trước khi đưa sang review.
> **Số items:** 18 — operationalize PROCESS 8 bước của `sop/07-visual-semantic.md` (B0-B8) thành tick-items. Checklist KHÔNG thay SOP: item nào fail → mở đúng B-step tương ứng trong sop/07 để fix.
> **Scoring:** Self Score /18 → Self %. Review 3 tầng như các checklist Tier 1 khác (Self 100% → SEO EX verify → Lead random 25-30%).
> **Phạm vi:** per-page / per-template. Audit layout TỔNG THỂ site, thiết kế trang mới từ đầu (Design-in full process), hoặc cần block map + benchmark SERP → route skill `visual-semantic-seo` + sop/07 (2 chế độ Design-in / Audit-fix).
> **Ranh giới:** UX thao tác (tap target, filter, form) → `tier-1-ux-ui.md` · conversion elements → `tier-1-cro-conversion.md` · deliverable cấu trúc + wireframe trước khi gửi khách → `gate-structure-wireframe.md`.

## Điều kiện vào (B0 — Input Gate)

Chưa có Outline AM + page type + Central Search Intent của trang → **không chạy checklist này** (sop/07 B0: "Không có Outline AM → không vào process").

## 🔴 P0 Gate — 5 items PHẢI pass (fail 1 = trả về, không trình duyệt)

| Gate | Item | Điều kiện |
|---|---|---|
| G1 | VS-03 | Centerpiece above-the-fold trả lời đúng intent chính |
| G2 | VS-05 | Visual hierarchy khớp heading hierarchy (LAMPRET) |
| G3 | VS-06 | DOM order = visual order |
| G4 | VS-14 | Critical info không giấu trong tab/accordion |
| G5 | VS-15 | Clutter không cắt main content flow |

---

## Phần A — Centerpiece & Above-the-fold (sop/07 B2)

| ID | Item | Tiêu chí ĐẠT | Wiki ref | B-step |
|---|---|---|---|---|
| VS-01 | **Page Function Statement** | Trang có function được chốt rõ (informational / commercial / transactional / mixed) + Centerpiece spec 1 câu "trang này phải deliver X đầu tiên". Mixed intent → liệt kê đủ CẢ 2 bộ elements above-fold (vd giá + công dụng, CTA + thông số) | [[Page Types]] · [[Central Search Intent]] | B2 |
| VS-02 | **Centerpiece dial đúng vertical** | Đoạn sau H1 theo đúng dial A4: commercial hub = definition ≤120 từ answer-first · transactional spoke = answer-first + giá bằng text (được >120) · YMYL/service = mini-article (definition → authority → hard stats → benefits enumeration). KHÔNG áp cứng "≤120 từ" cho mọi loại trang | [[Centerpiece Annotation]] | B2 (A4) |
| VS-03 | 🔴 **Above-the-fold trả lời intent chính** | Viewport 1 (desktop + mobile) chứa: H1 + L0/offer + trust element + form/CTA theo function statement. Ads/supplementary KHÔNG chiếm viewport 1. User đọc màn hình đầu là biết trang này trả lời query gì | [[Centerpiece Annotation]] · [[Visual Semantic Weight]] | B2 + B6 |
| VS-04 | **Extraction hygiene ~400 ký tự đầu** | View-source: ~400 ký tự đầu sau H1 là MỘT flow liền mạch trong DOM — share buttons / newsletter / related-inject đặt ngoài `<article>` hoặc sau đoạn mở, không chen giữa | [[Centerpiece Annotation]] (Extraction Hygiene) | B2 + B8 |

## Phần B — Hierarchy & Block Chunking (sop/07 B4 + B6)

| ID | Item | Tiêu chí ĐẠT | Wiki ref | B-step |
|---|---|---|---|---|
| VS-05 | 🔴 **Visual hierarchy khớp heading hierarchy** | Font-size giảm dần theo cấp heading (H1 36px+ lớn nhất, above-fold), H2 > H3; bold/italic/underline dùng semantic — không trang trí; heading nhìn to/đậm hơn = cấp cao hơn thật trong DOM | [[Visual Semantics]] · [[LAMPRET]] · [[Contextual Hierarchy]] | B6 |
| VS-06 | 🔴 **DOM order = visual order** | Thứ tự đọc trong DOM = thứ tự nhìn trên màn hình (WCAG C27) — không CSS reorder (flex `order`, absolute positioning) làm lệch reading order; semantic HTML thật (`<main>/<article>/<section>/<aside>`, `ul/ol/table` — không div-soup) | [[Semantic HTML]] | B6 |
| VS-07 | **Block chunking — mỗi block 1 ý** | Mỗi subtopic = 1 block visual riêng (heading + spacing tách rõ, ≥48px desktop / 24px mobile); không wall-of-text nhiều ý dính 1 khối. Mỗi key block đủ 5 slots: heading semantic + L0 answer 40-75 từ + body + visual + functional element (≥4/5) | [[Visual Semantics]] · [[Main Content]] | B4 |
| VS-08 | **Entity card skeleton** | Nhóm entity lặp (sản phẩm / dịch vụ / triệu chứng / địa bàn…) dùng CÙNG skeleton attribute cố định, instantiate ≥3 lần ("page as database render"); data-heavy → bảng `Attribute | Value` | [[Visual Semantics]] · [[E-A-V Framework]] | B4 (A3) |
| VS-09 | **Zone weight + không block mồ côi** | Mọi block bám macro context của trang (Pillar 3 — không block mồ côi); zone weight gán đúng: Centerpiece 100% / Supporting 60-80% / Supplementary 40% / Boilerplate 5-10%; sidebar/supplementary không nổi bật hơn main content; trang list >50-100 items → Tiered Prominence 3 tầng | [[Visual Semantic Weight]] · [[Tiered Visual Prominence]] | B4 |

## Phần C — Trust & Conversion placement (sop/07 A5 + B4)

| ID | Item | Tiêu chí ĐẠT | Wiki ref | B-step |
|---|---|---|---|---|
| VS-10 | **Trust elements đúng vị trí** | Trust xếp theo tầng, đúng chỗ: ≥1 trust element above-fold (badge/review/con số); press logos = dải mỏng giữa trang (không dồn dưới hero); review/testimonial gắn cạnh block liên quan — không rải ngẫu nhiên | [[Website Functions]] · skill `visual-semantic-seo` (Trust Stacking Hierarchy) | B4 |
| VS-11 | **Conversion layer interleave** | CTA/widget là LỚP riêng rải theo pattern vertical (YMYL/service: CTA-as-heading + tel: sau mỗi entity card · e-com/self-serve: widget/form nhúng trong card + above-fold) — KHÔNG dồn 1 CTA cuối trang. Mọi function trang claim đều THẬT (misleading functionality = spam policy) | [[Website Functions]] | B4 (A5) |

## Phần D — Image-level Semantics (sop/07 B5)

| ID | Item | Tiêu chí ĐẠT | Wiki ref | B-step |
|---|---|---|---|---|
| VS-12 | **Ảnh đúng entity, cạnh text, OCR-readable** | Mỗi key block ≥1 visual đặt CẠNH text liên quan (không gom cuối bài); ảnh độc bản CHỨA đúng entity (máy classify từ pixels — stock generic sai chủ đề = topical noise); chữ trong ảnh legible cho OCR + số liệu chính lặp lại trong figcaption/body text | [[Images]] · [[Visual Semantics]] | B5 |
| VS-13 | **Alt chain + dimensions** | Chain đủ: Image URL ≤3 từ → Alt = verbalized expansion; featured image alt = short H1, đặt cạnh H1, ảnh key persistent (không random rotate); mọi `<img>` có width/height (CLS); `ImageObject` + `primaryImageOfPage` cho featured image | [[Images]] · [[Semantic Annotation]] | B5 + B7 |

## Phần E — Structure hygiene & Clutter (sop/07 B4 + B6 + B7)

| ID | Item | Tiêu chí ĐẠT | Wiki ref | B-step |
|---|---|---|---|---|
| VS-14 | 🔴 **FAQ/tab không giấu critical info** | Critical info (giá / spec / answer chunk / L0) visible mặc định, in-flow — không nằm sau click trong tab/accordion (content ẩn mặc định không thể là Centerpiece); phần supplementary được phép collapse. Heading decorative ("FAQ", "Resources") không mang macro context — macro context thật đặt ở H2 semantic | [[Centerpiece Annotation]] · [[Semantic HTML]] (Tabs vs Accordion) | B4 + B6 |
| VS-15 | 🔴 **Clutter check** | Đếm popup / interstitial / auto-play / sticky ads / widget nhiễu: không element nào CẮT ngang main content flow hoặc che centerpiece (leak `clutterScore` — stored quality signal, không chỉ UX); quảng cáo/CTA phụ không chen giữa đoạn mở | [[Visual Semantics]] · [[Google Content Warehouse Leak]] | B7 |
| VS-16 | **Templated sections có unique value** | Section templated (block lặp cross-page, card instantiate) phải đổi TOÀN BỘ value theo entity context của trang — không copy nguyên block từ trang sibling; tự hỏi "đối thủ copy được trang này trong 1 buổi không?" — Có → thêm unique data / custom visuals (`contentEffort`) | [[Visual Semantics]] · [[Information Gain Score]] | B4 + B8 |
| VS-17 | **Mobile giữ cùng above-fold identity** | Mobile render giữ cùng bộ elements above-fold như desktop (H1 + L0 + trust + CTA) — không hạ cấp identity; sticky/bottom bar mobile không che centerpiece | [[Centerpiece Annotation]] | B6 |

## Phần F — Self-validation (sop/07 B8)

| ID | Item | Tiêu chí ĐẠT | Wiki ref | B-step |
|---|---|---|---|---|
| VS-18 | **Blur Test + chunk test tự chấm** | (1) Screenshot 1440px + mobile, blur 50%: còn nhận ra topic + function của trang; (2) tách 1-2 H2 section đọc riêng: block tự đứng vững, trả lời trọn 1 ý — pass cả 2 mới tick | [[Blur Test]] · [[Query Fan-Out]] | B8 |

---

## Quy trình tick

1. Làm xong layout/mockup/build cho page hoặc template → mở checklist, tick VS-01→VS-18.
2. Item fail → mở đúng **B-step** ghi ở cột cuối trong `sop/07-visual-semantic.md`, fix theo SOP rồi tick lại.
3. 5 items 🔴 P0 fail bất kỳ → KHÔNG trình duyệt, quay lại fix trước.
4. Ghi Self % + Self Note (item chưa tick + lý do + plan fix) → submit review.
5. Cần audit sâu (benchmark SERP, block map lại từ đầu, đo goldmine/title factors) → escalate skill `visual-semantic-seo` chế độ Audit-fix.
