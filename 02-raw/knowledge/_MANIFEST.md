# _MANIFEST — Nguồn gốc knowledge pack

Kho gốc: `SEO Knowledge/Semantic SEO A - Z/sop/`. Cột File nguồn tính từ folder này. Cột Đích tính từ `02-raw/knowledge/`.

Luật:

1. File trong knowledge/ là bản đóng gói READ-ONLY. Không sửa trong instance.
2. Vá nội dung → vá ở kho gốc, sync lại vào master, instance nhận qua MIGRATION. Chi tiết: `README.md` mục 3.
3. Mỗi lần re-sync: cập nhật ngày trong banner từng file + cột Ngày sync bảng dưới.

## Bảng nguồn (17 hàng)

| # | File nguồn | Hành động | Đích | Dùng cho WS / công đoạn | Ngày sync |
|---|---|---|---|---|---|
| 1 | 01-topical-map.md | Copy nguyên | sop/01-topical-map.md | WS05 Content plan — #4, 9, 10 (DoD 15 mục chốt topical map) | 2026-07-17 |
| 2 | 02-content-brief.md | Copy nguyên | sop/02-content-brief.md | WS05 Content plan — #15, 16, 17, 19 | 2026-07-17 |
| 3 | 03-internal-linking.md | Copy nguyên | sop/03-internal-linking.md | WS06 Onpage & IL — #18 | 2026-07-17 |
| 4 | 04-entity-optimization.md | Copy nguyên | sop/04-entity-optimization.md | WS06 Onpage & IL — #13 | 2026-07-17 |
| 5 | 05-audit-checklist.md | Copy nguyên | sop/05-audit-checklist.md | WS03 Audit — #2, 5, 6◇, 7(plan), 22◇, 24, 27, 29 | 2026-07-17 |
| 6 | 06-self-checklist/README.md | Copy nguyên | sop/06-self-checklist/README.md | Thao tác QC mọi WS — 3-Level Review (Self 100% → Verify → Lead random 25-30%) | 2026-07-17 |
| 7 | 06-self-checklist/tracking-schema.md | Copy nguyên | sop/06-self-checklist/tracking-schema.md | Thao tác QC — schema tracking điểm | 2026-07-17 |
| 8 | 06-self-checklist/tier-2-project-specific.md | Copy nguyên | sop/06-self-checklist/tier-2-project-specific.md | Thao tác QC Tier 2 — chỉ item được bật tại kick-off (#12) | 2026-07-17 |
| 9 | 06-self-checklist/tier-3-audit-configuration.md | Copy nguyên | sop/06-self-checklist/tier-3-audit-configuration.md | WS03 Audit — #5, 24, 27, 29 | 2026-07-17 |
| 10 | 09-project-timeline/10-thang-thuc-day.md | Copy nguyên | sop/09-timeline/10-thang-thuc-day.md | Timeline toàn dự án — SETUP bước 4 (retiming gói 8/10/12 tháng), bảng B index | 2026-07-17 |
| 11 | 09-project-timeline/khung-duy-tri.md | Copy nguyên | sop/09-timeline/khung-duy-tri.md | WS11 Handover — #33 | 2026-07-17 |
| 12 | 09-project-timeline/README.md | Copy nguyên | sop/09-timeline/README.md | Tổng quan quy trình 10 tháng + pointer lưu đồ | 2026-07-17 |
| 13 | 06-self-checklist/tier-1-outline-am.md | Chưng cất — giữ O1-O18 + P0 (ID + mô tả check + ngưỡng pass); lược evidence/rationale/ví dụ dài (~50% dung lượng) | sop/06-self-checklist/tier-1-outline-am.md | WS05 — QC outline/AM (bài viết chạy ở fork Content Production) | 2026-07-17 |
| 14 | 06-self-checklist/tier-1-content-writing.md | Chưng cất — giữ W1-W21 + Depth/Tone /23; lược evidence/ví dụ dài | sop/06-self-checklist/tier-1-content-writing.md | WS05 — QC bài viết | 2026-07-17 |
| 15 | 06-self-checklist/tier-3-technical-advance.md | Chưng cất — bỏ cột Data/Evidence, giữ item + ngưỡng | sop/06-self-checklist/tier-3-technical-advance.md | WS03 Audit — #27, 29 | 2026-07-17 |
| 16 | 07-visual-semantic.md | Chưng cất — giữ Phần B (process Bước 0-8 — viết tắt B0-B8 — + Output + checkbox), Phần C (RACI), Phần D (trade-offs); LOẠI HOÀN TOÀN Phần A (deep theory bảo mật: patents, leak factors, 4 Pillars, centerpiece dial) | sop/07-visual-semantic.md | WS04 Structure — #11 | 2026-07-17 |
| 17 | 08-onpage-checklist.md | Chưng cất — giữ nguyên P0-P23 (/23) + T2-P1..8 (/31) + T3-P1..8 (/39) + AX1-AX5 (chấm riêng) + luật scoring + luật "sửa nền trước"; lược evidence inline, cột cross-ref wikilink, bảng reconciliation OP1-OP55 | sop/08-onpage-checklist.md | WS06 Onpage & IL — #7, 13, 18, 23 · WS08 GEO (AX1-AX5) — #14, 21, 28 | 2026-07-17 |

## Nhóm KHÔNG copy

| Nguồn | Lý do |
|---|---|
| wiki/ (436 file) | Tri thức lý thuyết sâu của wiki Semantic SEO — không đóng gói theo dự án; tra kho gốc trên máy master |
| 07-visual-semantic-slides.html | Slide trình chiếu — không phải checklist vận hành |
| 07-visual-semantic-deep-dive.html | Deep theory bảo mật (patents/leak) — chỉ ở kho gốc |
| 06-self-checklist/tier-3-technical-advance.html | Bản HTML trùng nội dung file .md cùng tên |
| GTV-Benchmark-Quoc-Te_International-Live-Sites_v1.html | Benchmark tham khảo — không phải checklist vận hành |
| 09-project-timeline/*.html (3 file lưu đồ) | Visualization — xem trên máy master |
| CLAUDE.md · AGENTS.md · index.md · log.md của kho | Infra riêng của wiki Semantic SEO — không thuộc knowledge pack |
