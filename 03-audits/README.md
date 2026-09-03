# 03 — Audits (WS Audit)

1. **Mục đích**: Chẩn đoán toàn trạng site theo chu kỳ quý và gác decision gate để mọi action dựa trên evidence.
2. **Công đoạn phụ trách**: #2, #5, #6◇, #7 (phần plan — execute ở WS 06), #22◇, #24, #27, #29.
3. **Deliverable chuẩn**: audit report, gap analysis — naming `<CLIENT>_<slug>_v<N>.md`. Nơi lưu: `full/` (toàn diện 6 hạng mục #5/#27, vd `<CLIENT>_audit-toan-dien-q1_v1.md`) · `technical/` · `content/` · `entity/` · `offsite/` (audit lẻ giữa kỳ, sau deploy, rớt hạng — không phải chạy full).
4. **Template**: `_TEMPLATES/audit-toan-dien.md` (full) · `audit-technical.md` · `audit-content.md` · `audit-entity.md` · `audit-offsite.md` · `_TEMPLATES/gap-analysis.md`.
5. **Checklist QC**: `02-raw/knowledge/sop/05-audit-checklist.md` + `02-raw/knowledge/sop/06-self-checklist/tier-3-audit-configuration.md` + `02-raw/knowledge/sop/06-self-checklist/tier-3-technical-advance.md`.
6. **Skill gọi**: `skills/semantic-content-audit/` · `skills/technical-seo-audit/` · `skills/competitor-seo-gap-analysis/` · `skills/content-refresh/` (#24, #29 — update brief bàn giao sang fork Content Production) · `skills/seo-logfile-analysis/` (#27) · `skills/seo-drift-tracker/` (QA sau deploy) · `skills/hreflang-planner/` (đa thị trường) · `skills/local-seo-audit/` + `skills/map-pack-intelligence/` (dự án local). Cheat-sheet: `02-raw/knowledge/cheat-sheets/ws03-audit.md`.
7. **Done-criteria**: Audit report + phân loại action full URL + owner/deadline cho từng action.

Ghi chú:

- Gate ◇ (#6, #22): verdict ghi `gate: <verdict>` vào cột Ghi chú `index.md` + link deliverable, append `log.md` op `gate`.
- `qc/` là kho QC report của MỌI workstream — xem `qc/README.md`.
- Nguyên tắc ưu tiên action: sửa nền (technical, cấu trúc) trước, tối ưu ngọn sau.
