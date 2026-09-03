---
type: sop
status: stub
last_updated: 2026-04-20
related:
  - "[[Content Brief]]"
  - "[[Koray's Framework]]"
  - "[[Representative Queries]]"
  - "[[Heading Vectors]]"
---

> Bản đóng gói cho SEO Production — sync từ `SEO wiki nội bộ «Semantic» (ngoài repo) SEO A - Z/sop/02-content-brief.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# SOP 02 — Viết Content Brief theo Koray Framework

> Quy trình sinh brief cho 1 bài. Dùng cùng với `/seo-brief`.

## Mục tiêu
Brief đủ chi tiết để writer (dù không phải SEO specialist) cũng viết ra bài match Central Search Intent và cover Query Network.

## Pre-conditions
- Đã có [[Topical Map]] cho cluster chứa bài này.
- Đã lock target query + Representative Question.

## Brief Structure (mặc định)

<!--
TODO USER CONTRIBUTION:
Phần này là "xương sống" của brief GTV team dùng hàng ngày. Tôi đã đưa cấu trúc
mặc định Koray-style trong skills/seo-brief/SKILL.md (11 sections).

CÂU HỎI CẦN BẠN CHỐT (5-10 dòng):
1. GTV team hiện đang yêu cầu writer phải fill những fields nào bắt buộc?
2. Có format xuất ra đặc biệt không (Google Doc template, Notion DB, Sheet)?
3. Có checklist QA riêng cho editor trước khi assign cho writer không?

Trả lời ngắn, tôi sẽ merge vào đây thành "GTV brief spec" để mọi session sau đều
follow đúng standard của team bạn.
-->

### Default sections (sẽ refine theo input của bạn)
Xem cấu trúc 11 section trong skill `seo-brief` (thuộc wiki Semantic SEO / fork Content Production — KHÔNG đóng gói trong SEO Production; tương đương gần nhất trong repo này: `skills/topical-map-creation` bước Content Brief + `_TEMPLATES/content-plan-matrix.md`):
1. Central Search Intent
2. Macro Context
3. Micro Context
4. Representative Question (H1)
5. Supporting Questions (H2s)
6. Heading Vectors (table)
7. Entity Coverage (EAV)
8. Internal Linking Plan
9. Responsiveness Requirements
10. Avoidance List
11. Success Criteria

## Process

1. Chạy `/seo-brief <query>` để lấy draft.
2. Editor review theo checklist (xem [[sop/05-audit-checklist]]).
3. Ship cho writer kèm link tới [[Koray's Framework]] và các entity pages được reference.

## Definition of Done
- 100% section fill.
- Representative Question ≠ Supporting Questions.
- Không field `TBD`.
