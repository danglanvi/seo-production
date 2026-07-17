---
template: structure-brief
ws: 04-structure-ux-cro
cong_doan: 11
checklist: 02-raw/knowledge/sop/07-visual-semantic.md
client: "{{CLIENT}}"
page_type: "{{PAGE_TYPE}}"
mode: "{{DESIGN-IN | AUDIT-FIX}}"
status: draft
date: "{{YYYY-MM-DD}}"
---

# Structure Brief — {{CLIENT}} / {{PAGE_TYPE}}

> Checklist gốc: `02-raw/knowledge/sop/07-visual-semantic.md` (Phần B, process B0→B8).
> Mode Design-in = trang mới, chạy đủ B0→B8. Mode Audit-fix = trang có sẵn, vào thẳng B8, quay lại bước FAIL.
> Khi instantiate: lưu thành `04-structure-ux-cro/{{CLIENT}}_structure-brief-<page-slug>_v1.md`.

## 1. Thông tin chung

| Trường | Giá trị |
|---|---|
| Page type | {{PAGE_TYPE}} (1 trong 6 loại theo topical map) |
| URL / nhóm URL | {{URL}} |
| Entity + attribute chính | {{ENTITY}} / {{ATTRIBUTE}} |
| Central Search Intent | {{CSI}} |
| Funnel position / persona | {{FUNNEL}} / {{PERSONA}} |
| Mốc cứng | Structure lock ≤15 ngày đầu T2 — deadline: {{NGAY_DEADLINE}} |

## 2. Output B0→B8

Luật: mỗi bước phải có output ghi link vào cột Kết quả. Không có Outline AM → không vào process (B0 chặn).

| Bước | Output bắt buộc | Kết quả / link | Status |
|---|---|---|---|
| B0 Input Gate | Entity + attribute, page type, funnel, persona, CSI, kết quả QDP-QDH-QDS từ Outline AM | {{LINK}} | ☐ |
| B1 Query Augmentation | Bảng variation → page type/layout/function + quyết định prune/merge | {{LINK}} | ☐ |
| B2 Function & Centerpiece | Page Function Statement + Centerpiece spec 1 câu + danh sách above-fold elements + định nghĩa ~400 ký tự đầu sau H1 | {{LINK}} | ☐ |
| B3 SERP & Attribute Benchmark | Bảng benchmark top 5-10 (đúng geo/device) + category thắng SERP + design archetype — 1 trang | {{LINK}} | ☐ |
| B4 Block Architecture | Block map (mockup text-level) + entity card skeleton + conversion layer + component library note | {{LINK}} | ☐ |
| B5 Visual Asset Layer | Visual asset spec per block (kèm alt text + filename) | {{LINK}} | ☐ |
| B6 Design Implementation | Figma/build khớp block map (diff check) | {{LINK}} | ☐ |
| B7 Technical Verification | Pass: HTML <2MB · ảnh có width/height (CLS) · metadata trong initial HTML · TTFB <2s · clutter check · JSON-LD đúng page type · mobile = desktop identity | {{LINK}} | ☐ |
| B8 Validation Loop | Extraction test ~400 ký tự đầu + Blur Test + effort/replicability review + chunk extraction test + SERP/AI-surface check + function test | {{LINK}} | ☐ |

## 3. Entity card skeleton

Luật: mỗi attribute = 1 HTML section riêng có label; card skeleton instantiate ≥3 lần; mỗi block đủ 5 slots (heading semantic + L0 answer 40-75 từ + body + visual + functional element); data-heavy → bảng `Attribute | Value`.

| Card | Sub-attribute cố định | Số lần instantiate | CTA/widget trong card |
|---|---|---|---|
| {{CARD_1}} | {{SUB_ATTRIBUTES}} | {{N}} | {{CTA}} |
| {{CARD_2}} | {{SUB_ATTRIBUTES}} | {{N}} | {{CTA}} |

Zone weight (heuristic biên tập GTV): Centerpiece 100% / Supporting 60-80% / Supplementary 40% / Boilerplate 5-10%.

## 4. RACI

| Bước | SEO lead | Content | Designer | Dev |
|---|---|---|---|---|
| B0 Input Gate | R/A | C | — | — |
| B1 Query Augmentation | R/A | C | — | — |
| B2 Function & Centerpiece | R/A | C | — | — |
| B3 SERP & Attribute Benchmark | R | C | C | — |
| B4 Block Architecture | R/A | R | C | — |
| B5 Visual Assets | C | R | R | — |
| B6 Design/Build | C | — | R | R |
| B7 Technical Verify | A | — | — | R |
| B8 Validation Loop | R/A | C | C | C |

## 5. Done-criteria

- [ ] Đủ 9 output B0→B8 có link kết quả (Design-in) hoặc bước FAIL đã fix + re-test B8 (Audit-fix).
- [ ] Block map + wireframe được SEO Leader duyệt; HTML template semantic đã gửi Coder.
- [ ] B7 pass toàn bộ; B8 không còn bước FAIL.
- [ ] Structure lock ≤15 ngày đầu T2 — nếu trễ, ghi lý do vào index.md cột Ghi chú.
- [ ] Cập nhật index.md (công đoạn 11) + log.md op `work`.
