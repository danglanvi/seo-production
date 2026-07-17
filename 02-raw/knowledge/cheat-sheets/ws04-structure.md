# Cheat-sheet WS04 — Structure / UX / CRO (04-structure-ux-cro)

Ký hiệu B0-B8 trong file này = «Bước 0»→«Bước 8» của `../sop/07-visual-semantic.md`.

> Bản 1 trang, chưng cất từ `../sop/07-visual-semantic.md` (Phần B process 8 bước + Phần C RACI) ngày 2026-07-17.
> QC chính thức PHẢI chấm theo checklist đầy đủ trong `../sop/07-visual-semantic.md` — cheat-sheet chỉ để nạp nhanh trước khi làm.

## 1. Mục tiêu WS

Chốt cấu trúc site + wireframe UX/UI + HTML template semantic cho từng page type — layout phải "phát" đúng page function. Mốc cứng: **xong ≤15 ngày đầu T2**.

Công đoạn phụ trách: **11**. Hai chế độ: **Design-in** (trang mới — chạy đủ B0-B8) và **Audit-fix** (trang có sẵn — vào thẳng B8, quay lại bước fail).

## 2. Input / Output

| Input | Output |
|---|---|
| Topical Map + Outline AM (BẮT BUỘC — thiếu thì không vào process) | Block map + wireframe per page type theo `_TEMPLATES/structure-brief.md` |
| Entity + attribute pair, page type, funnel position, persona, Central Search Intent | Entity card skeleton + component library note |
| Kết quả QDP-QDH-QDS của node + SERP benchmark data | HTML template semantic được SEO Leader/SEO Manager duyệt |

## 3. Checklist rút gọn (10 dòng)

| # | Check |
|---|---|
| 1 | B0 Input Gate: có Outline AM + entity/attribute + page type + Central Search Intent — thiếu → dừng |
| 2 | B1 Query Augmentation: liệt kê biến thể augmented → map page type/layout/function → quyết prune/merge |
| 3 | B2 Function & Centerpiece: Page Function Statement + Centerpiece spec 1 câu + danh sách above-fold elements + định nghĩa ~400 ký tự đầu sau H1 |
| 4 | B3 SERP & Attribute Benchmark: chụp above-fold top 5-10 → đọc ngược SERP features ra attribute ưu tiên → chốt category thắng + design archetype |
| 5 | B4 Block Architecture: mỗi attribute = 1 section riêng; card skeleton instantiate ≥3 lần; mỗi block đủ 5 slots (heading semantic + L0 40-75 từ + body + visual + functional element); conversion layer spec vị trí từng CTA/widget |
| 6 | B5 Visual Asset Layer: mỗi key block ≥1 visual độc bản đặt cạnh text; chain Title → URL → Description → Image URL ≤3 từ → Alt = verbalized expansion |
| 7 | B6 Design Implementation: typography giảm dần theo cấp heading (H1 36px+ above-fold); DOM order = visual order; semantic HTML thật; không giấu critical info trong tabs/accordion |
| 8 | B7 Technical Verification: HTML <2MB · ảnh có width/height (CLS) · metadata trong initial HTML · TTFB <2s · clutter check · JSON-LD đúng page type (không dùng FAQPage/HowTo làm rich-result lever) |
| 9 | B8 Validation Loop: extraction test 400 ký tự · Blur Test · effort/replicability review · chunk extraction test per H2 · SERP/AI-surface check · function test |
| 10 | RACI đúng vai + deliverable duyệt đúng mốc ≤15 ngày đầu T2 |

## 4. Ngưỡng pass

- Mỗi bước B0-B8 phải có Output đúng spec trong `../sop/07-visual-semantic.md` — không nhảy bước.
- **B7 là hard gate**: mọi ô checkbox phải pass trước khi build được duyệt.
- B8 fail bước nào → quay lại đúng bước đó (Audit-fix mode), không patch tại chỗ.
- RACI (Phần C, rút gọn): B0-B3 + B8 — SEO lead R/A · B4 — SEO lead + Content cùng R · B5 — Content + Designer R · B6 — Designer/Dev R · B7 — Dev R, SEO A.

## 5. Skill gọi + luật nạp

| Skill | Khi nào |
|---|---|
| `visual-semantic-seo` | Toàn bộ B0-B8 — skill này lái output thiết kế (block map, mockup, wireframe) |
| `semantic-html-optimization` | B6-B7 — HTML template, heading hierarchy, main/article/section, extraction hygiene |

Luật nạp 80/20: `references/` của skill nạp TỪNG file theo pointer khi bước cần (vd bảng Website Functions chỉ nạp ở B6); không nạp examples/evals; checklist chỉ nạp `../sop/07-visual-semantic.md` — không quét cả `knowledge/`.

## 6. 5 lỗi thường gặp

1. Vào process khi chưa có Outline AM — vi phạm B0, mọi bước sau đều xây trên cát.
2. Nghĩ "viết section" thay vì "thiết kế skeleton, đổ data" — block thiếu bộ sub-attribute cố định, không instantiate lại được.
3. Dồn 1 CTA cuối trang thay vì conversion layer interleave vào từng entity card/block.
4. Heading decorative ("FAQ", "Resources") không mang macro context; giấu critical info trong tabs/accordion.
5. Gom hết ảnh xuống cuối bài hoặc dùng ảnh stock không chứa đúng entity; CSS reorder làm DOM order lệch visual order.
