# Query Augmentation Map — template Bước 1 (v3.7)

> Deliverable chuẩn của Bước 1 (Query Augmentation & QDP Gate). Nguồn: Koray SEL 22/07/2026 ("How semantics and topical authority improve local SEO") — bảng rehab Thailand 12 dòng; wiki: `[[Query Augmentation]]`, `[[QDP-QDH-QDS]]`, `[[sources/local-seo-topical-authority-sel-koray]]`.

## Vì sao bảng này tồn tại

"What Google publicly calls **query fan-out** is technically **query augmentation** in its patents" (US9916366B1 — Shukla; hậu duệ: Search with stateful chat / AI Mode). Nếu hiểu cách Google augment một query, ta build được **contextual vector tốt hơn cho trang và tối ưu layout theo đó**. Bảng này là cây cầu: query processing (trái) → visual semantics (phải). Mỗi dòng trả lời: *nhóm augmented queries này được component NÀO trên trang phục vụ, verbalize bằng triples nào, neo entities nào?*

## Quy trình 4 bước

1. **Augment canonical query** — nguồn: PAA, autocomplete, `search_model_queries` (ChatGPT DevTools → Network/XHR → `backend-api/conversation`), AI Mode ("What are the most important attributes for [X] in [Y]?"), query logs GSC. Phân loại biến thể theo trục: transactional / trust-verification / cost / comparison / experience / local-origin / process / attribute-specific.
2. **QDP Gate per biến thể** (rubric: `keyword-topic-url-mapping/references/qdp-gate.md`): ≥3/4 tiêu chí → PAGE riêng (ra khỏi bảng này, vào topical map). Không đạt → ở LẠI trang này dưới dạng heading (QDH), sentence (QDS), hoặc **component** (table/list/form/calculator/converter/filter).
3. **Gán component + triples + entities** cho từng nhóm ở lại — mỗi nhóm 1 dòng. Component phải THẬT (function validation — nút book phải book được).
4. **Phân phối xuống layout**: thứ tự dòng ≈ thứ tự block trên trang (macro context trước, micro contexts sau, closure cuối). Feed thẳng vào Bước 4 Block Architecture / Wireframe Mode BUILD.

## Weighted-term rule (bắt buộc trước khi viết dòng nào)

Query similarity + term weighting KHÔNG phải string matching: BERT weight "Nike" > "running" > "shoes" (paper "End-to-end query term weighting", Bendersky/Najork). Xác định **term nặng nhất** của canonical query → term đó phải là:
- **Subject của các triples** trong bảng (không phải object);
- Vocabulary chính của H1/H2 + annotations;
- Nếu term nặng đổi ("Los Angeles" vs "attorney") → cả topical map + sentence structure đổi theo.

## Template

| Query augmentation (nhóm biến thể) | Visual component (figure #) | Triples (Subject – Predicate – Object) | Named entities |
|---|---|---|---|
| _các query cùng intent, phân tách phẩy_ | _# + tên component trên wireframe_ | _(S, P, O) × 2-3_ | _entities được neo_ |

## Worked example — "rehab thailand" (Koray, 12 components)

| Query augmentation | Visual component | Triples (S-P-O) | Named entities |
|---|---|---|---|
| find a rehab thailand, book rehab thailand | 2 – Hero H1 "Drug and Alcohol Rehab in Thailand" + CTA "Talk to us – free and confidential" | ({Rehab}, is a, Rehab Centre) · ({Rehab}, located in, Thailand) · (User, contacts, {Rehab}) | {Rehab}, Thailand |
| rehab thailand for foreigners, rehab in thailand from uk | 1 – Utility bar regional phone chips (UK US AU HK TH) | ({Rehab}, serves, United Kingdom/US/AU) | UK, US, AU, HK, TH |
| licensed rehab thailand, accredited rehab thailand | 3 – Evidence strips: license + logo pills | ({Rehab}, licensed by, {Health Authority}) · ({Rehab}, certified under, {Accreditation Body}) | {Health Authority}, {Accreditation Body} |
| reviews for rehab thailand, is rehab in thailand safe | 4 – Review carousel + star ratings + Google badge | ({Reviewer}, rates, {Rehab}) · (Review, verified by, Google) | {Rehab}, {Reviewers}, Google |
| rehab chiang mai, rehab resort thailand | 5 – Definitional block + proof line "7000+ recoveries, {Landmark}" | ({Rehab}, is a, Luxury Rehab Centre) · ({Rehab}, located in, {City}) · ({Rehab}, has recovery count, 7000+) | {Rehab}, {City}, {Landmark} |
| best rehab therapist thailand | 6 – Therapist carousel, named practitioner entities | ({Therapist}, works at, {Rehab}) · ({Therapist}, has credential, MSc) | {Rehab}, person entities |
| cocaine/ketamine/alcohol rehab thailand | 7 – Tabbed micro context selector "What We Treat" + definitional snippet mirror child page | ({Rehab}, treats, Ketamine Addiction) · (Tab, links to, /ketamine-addiction-treatment/) | {Rehab}, substance entities |
| rehab thailand cost, how much is rehab in thailand | 8 – Mid-page conversion band + form + "Privacy protected, 24h reply" | (Enquiry, protected by, Privacy Policy) · ({Rehab}, responds within, 24 Hours) | {Rehab} |
| meth rehab / gambling addiction / trauma thailand | 9 – Programme card grid, 8 contextual bridges, anchor = child page H1 | ({Rehab}, offers, {Programme}) · (Card, links to, Child Page) | {Rehab}, condition entities |
| medical detox thailand, aftercare rehab thailand | 10 – Process accordions ĐÚNG THỨ TỰ điều trị: Withdrawal → Residential → Aftercare | (Programme, starts with, Medical Withdrawal) · (Programme, ends with, Aftercare) | {Rehab}, process entities |
| luxury rehab thailand, best rehab thailand | 11 – Vertical tab attribute verbalizer: mỗi tab = 1 attribute + proof panel | ({Rehab}, has care type, Luxury Rehab Care) · ({Rehab}, positioned as, Asia's Rehab Hub) | {Rehab}, Asia |
| how long is rehab in thailand, what to expect | 12 – Tabbed FAQ accordion, câu hỏi khớp PAA, answer mở bằng definitional sentence | ({Programme}, has duration, 4 to 12 Weeks) · (Answer, aligned with, PAA) | {Rehab} |

## Eval khi review bảng

- [ ] Mỗi augmented query của canonical đều có dòng (không nhóm nào mồ côi) — coverage test.
- [ ] Term nặng nhất là subject của ≥80% triples.
- [ ] Component nào claim function (book/call/compare/filter) → function THẬT.
- [ ] Superlative ("best", "luxury") có attribute verbalizer + proof panel — không adjective trần.
- [ ] Thứ tự dòng khớp thứ tự block dự kiến (macro → micro → closure); conversion bands interleave sau mỗi trust escalation.
- [ ] Biến thể pass QDP (≥3/4) KHÔNG nằm trong bảng — nó là page riêng, ở đây chỉ giữ contextual bridge trỏ tới.
