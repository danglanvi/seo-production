> Bản đóng gói cho SEO Production — sync từ `SEO wiki nội bộ «Semantic» (ngoài repo) SEO A - Z/sop/07-visual-semantic.md` ngày 2026-07-17.
> Bản chưng cất — đã lược evidence/theory; bản đầy đủ ở kho gốc.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# SOP 07 — Visual Semantic SEO: Process 8 bước (v3.6, 2026-07-16)

> **Đối tượng:** SEO lead, content writer, designer, dev trong pipeline GTV.
> **Vị trí trong pipeline:** chạy giữa [[Layer 2 Outline AM]] và [[Layer 4 Onpage]], theo trình tự: *topical map → document architecture → mockup blocks → Figma*.
> **2 chế độ:** **Design-in** (trang mới — chạy đủ Bước 0-8) và **Audit-fix** (trang có sẵn — vào thẳng Bước 8, quay lại bước fail).

---

## PHẦN B — PROCESS 8 BƯỚC

### Bước 0 — Input Gate *(điều kiện vào)*

Nhận từ [[Topical Map]] + [[Layer 2 Outline AM]]:
- Entity + attribute pair, page type ([[Page Types]] 6 loại), funnel position, persona, Central Search Intent.
- Kết quả [[QDP-QDH-QDS]] của node (page này "deserve" những heading nào).
- **Không có Outline AM → không vào process.**

### Bước 1 — Query Augmentation Classification *(SEO lead)*

1. Liệt kê biến thể **augmented** của query gốc: experience / local / price / instructional / so sánh… (soi PAA + `search_model_queries` ChatGPT DevTools khi có).
2. Map mỗi biến thể → **page type + layout + function** (experience→forum, local→directory, price→hybrid, instructional→guide — bảng trong [[Query-SERP Mapping]]).
3. Quyết **prune/merge**: biến thể không cần page riêng → prune; page quá giống → merge (CoR ↓, PageRank cô đặc).

**Output:** bảng variation → page type/layout/function + quyết định prune/merge.

### Bước 2 — Page Function & Centerpiece Definition *(SEO lead)*

1. Chốt page function: informational / commercial / transactional / **mixed** — layout phải "phát" đúng function.
2. Viết **Centerpiece spec 1 câu**: "Trang này phải deliver X đầu tiên."
3. Mixed intent → liệt kê CẢ 2 bộ elements bắt buộc above-fold (giá + công dụng; CTA + thông số; form + definition).
4. Chốt format + độ dài đoạn centerpiece (sau H1) theo vertical/page type — chuẩn chi tiết: hỏi SEO Lead hoặc tra kho gốc.
5. Định nghĩa **~400 ký tự đầu sau H1** sẽ nói gì — flow liền mạch, không share/inject chen giữa.

**Output:** Page Function Statement + Centerpiece spec + danh sách above-fold elements.

### Bước 3 — SERP & Attribute Benchmark *(SEO lead)*

1. Chụp above-fold top 5-10 SERP của target query (đúng geo/device).
2. Ghi: block nào xuất hiện, thứ tự, elements commercial/trust, functions, format thắng — format trang phải khớp category đang thắng.
3. **Đọc NGƯỢC SERP features → attribute được ưu tiên** cho entity type (Location→map, số đo→chart, năm→timeline, bộ sưu tập→gallery; "best" = soft property cần khối review/so sánh).
4. Xác định **category thắng SERP** (listicle/PLP/video) — trang phải build đúng category đó.
5. Xác định **design archetype của vertical** → match trước, differentiate sau.

**Output:** bảng benchmark + archetype notes (1 trang).

### Bước 4 — Block Architecture: Entity Card Skeletons *(SEO lead + content)*

1. Liệt kê attributes của entity (E-A-V từ outline) → **mỗi attribute = 1 HTML section riêng** có label + retrieval purpose ("hotel-card pattern").
2. Thiết kế **card skeleton** cho mỗi nhóm entity lặp (sản phẩm, dịch vụ, triệu chứng, địa bàn…): bộ sub-attribute cố định, instantiate ≥3 lần.
3. Mỗi block đủ 5 slots: **heading semantic + L0 answer 40-75 từ + body + visual + functional element**.
4. Gán zone weight ([[Visual Semantic Weight]] — % là heuristic biên tập GTV, không phải số đo Google): Centerpiece 100% / Supporting 60-80% / Supplementary 40% / Boilerplate 5-10%; RQ làm border marker.
5. **Conversion layer**: interleave CTA/widget theo từng block/card — KHÔNG dồn 1 CTA cuối trang; spec vị trí từng CTA/widget ngay trong block map.
6. Data-heavy topics → bảng `Attribute | Value` (artifact E-A-V thuần nhất).
7. Trang list >50-100 items → [[Tiered Visual Prominence]] 3 tầng.
8. Heading decorative ("FAQ", "Resources") không mang macro context — macro context thật nằm ở H2 semantic. (Lưu ý: có site dùng tab-label H3 rỗng — trade-off widget; GTV giữ rule sạch.)

**Output:** **Block map** (mockup text-level — chính là "mockup phase") + component library note (block nào share cross-page).

### Bước 5 — Visual Asset Layer *(content + designer)*

1. Mỗi key block ≥1 visual đặt **cạnh text liên quan** (Google official) — không gom cuối bài.
2. Ảnh: **độc bản** (effort + Information Gain), chứa đúng entity (máy classify từ pixels), chữ trong ảnh OCR-legible + số liệu lặp lại trong figcaption/text.
3. Chain: Title → URL → Description → **Image URL ≤3 từ** → Alt = verbalized expansion; featured image alt = short H1, đặt cạnh H1; ảnh key persistent (không random).
4. Schema: `ImageObject` + `primaryImageOfPage`; **video companion** cho core topics (transcript + chapters + `VideoObject`) — YouTube = 18% AIO citations.

**Output:** Visual asset spec per block (kèm alt text + filename).

### Bước 6 — Design Implementation: mockup → Figma → build *(designer/dev)*

1. Typography hierarchy: font-size giảm dần theo cấp heading, H1 36px+ above-fold, bold/italic semantic.
2. **DOM order = visual order** (WCAG C27) — cấm CSS reorder làm lệch reading order.
3. Above-fold identity: H1 + L0/offer + trust + form/CTA (theo Bước 2); ads/supplementary xuống dưới.
4. Semantic HTML thật: `<main>/<article>/<section>/<aside>`, `ul/ol/table` — không div-soup.
5. Không giấu critical info trong tabs/accordion (safe default cho AI extraction); mobile giữ cùng above-fold identity.
6. Functions theo intent (bảng Website Functions trong skill `visual-semantic-seo`).

**Output:** Figma/build khớp block map (diff check).

### Bước 7 — Technical Verification *(dev + SEO)*

- [ ] **HTML < 2MB** (hard gate 12/2025) — DOM không phình catalog-as-heading.
- [ ] CLS: mọi ảnh/embed có width/height đặt trước (WRS không fetch ảnh khi có dimensions).
- [ ] Metadata (title/canonical/schema) trong initial HTML, nhất quán pre/post-render; JS tách bundle stable/changing.
- [ ] TTFB < 2s ([[GEO]] Gate #2); page weight hợp lý (cost of retrieval).
- [ ] Clutter check: đếm popup/interstitial/auto-play/widget nhiễu — nhiễu là quality signal xấu, không chỉ UX.
- [ ] Featured image indexed (check `src:` operator).
- [ ] JSON-LD đúng page type (YMYL: entity graph đầy đủ — LegalService/Service, OfferCatalog, Geo; e-com: Product/Offer/AggregateRating — Product snippet required = name + 1 trong review/rating/offers). ⚠️ KHÔNG dùng FAQPage/HowTo như rich-result lever: HowTo retire 09/2023, FAQ rich result chấm dứt 07/05/2026 (FAQ content hiển thị trên trang vẫn giá trị — đó là content, không phải schema).
- [ ] Mobile render = desktop identity.

### Bước 8 — Validation Loop *(SEO — lặp theo quý hoặc sau redesign)*

1. **Extraction test** — view-source: ~400 ký tự đầu sau H1 liền mạch, không từ "contextless" chen giữa.
2. **[[Blur Test]]** — screenshot 1440px + mobile, blur 50%: còn nhận ra topic + function không?
3. **Effort/replicability review** — đối thủ copy được trang trong 1 buổi không? Có → thêm unique data/custom visuals.
4. **Chunk extraction test** — tách từng H2 section cho LLM đọc riêng: có tự đứng vững + trả lời trọn 1 fan-out variant không?
5. **SERP/AI-surface check** — Google có viết lại title không? Snippet đúng ý? GSC image data; AIO/AI Mode citation tracking.
6. **Function test** — mọi function trang claim đều thật (misleading functionality = spam policy).
7. Fail bước nào → quay lại bước đó (Audit-fix mode).

---

## PHẦN C — RACI

| Bước | SEO lead | Content | Designer | Dev |
|---|---|---|---|---|
| 0 Input Gate | **R/A** | C | — | — |
| 1 Query Augmentation Classification | **R/A** | C | — | — |
| 2 Function & Centerpiece | **R/A** | C | — | — |
| 3 SERP & Attribute Benchmark | **R** | C | C | — |
| 4 Block Architecture | **R/A** | **R** | C | — |
| 5 Visual Assets | C | **R** | **R** | — |
| 6 Design/Build | C | — | **R** | **R** |
| 7 Technical Verify | **A** | — | — | **R** |
| 8 Validation Loop | **R/A** | C | C | C |

## PHẦN D — Trade-offs phải quyết định theo dự án (không có đáp án chuẩn)

1. **Above-fold density vs UX minimalism**: nhồi info + commercial cùng viewport (mixed intent) vs CRO orthodoxy = 1 message 1 CTA. → A/B khi có traffic; default GTV: density cao cho mixed-intent money page, theo CRO cho single-intent LP.
2. **Tabs/accordion**: gọn mobile nhưng rủi ro AI extraction. Default: critical info không giấu; supplementary được phép.
3. **On-page layout vs SERP-surface**: cả hai đều cần — đừng dồn 100% resource một phía.
