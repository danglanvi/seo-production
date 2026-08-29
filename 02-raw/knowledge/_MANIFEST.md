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
| 17 | 08-onpage-checklist.md | Chưng cất — giữ nguyên P0-P23 (/23) + T2-P1..8 (/31) + T3-P1..8 (/39) + AX1-AX5 (chấm riêng) + luật scoring + luật "sửa nền trước"; lược evidence inline, cột cross-ref wikilink, bảng reconciliation OP1-OP55 | sop/08-onpage-checklist.md | WS06 Onpage & IL — #7, 13, 18, 23 · WS08 GEO (AX1-AX5) — #14, 21, 28 | 2026-08-29 (vá P14 strong-policy) |
| 18 | 11-publish-wp.md | Copy nguyên — SOP đăng bài WordPress (2 flow input, gate pre-publish, kit wp-publish-workflow-kit, giới hạn kit) | sop/11-publish-wp.md | WS06 Onpage & IL — khâu publish #7, 13, 15, 16, 19, 23 | 2026-08-29 |

## Bổ sung 19.7.2026 — Hệ checklist v3 (24 hàng, đều Copy nguyên)

Hàng #6 (README.md) đã RE-SYNC 2026-07-19 (bản v3.1 — registry toàn hệ + 2 checklist treo #6 Batch 36). Các file mới:

| # | File nguồn (06-self-checklist/ trừ khi ghi khác) | Đích | Dùng cho WS / công đoạn | Ngày sync |
|---|---|---|---|---|
| 18 | foundation-content-nganh.md | sop/06-self-checklist/ | WS00+WS05 — #3 (dựng checklist ngành, nguồn bật Tier 2) | 2026-07-19 |
| 19 | checklist-kpi-okrs-planning.md | sop/06-self-checklist/ | WS01 — #1, 8 (lập KPI/OKRs, P0 5) | 2026-07-19 |
| 20 | monthly-project-review.md | sop/06-self-checklist/ | WS10 — Lead tự check trước review tháng (P0 7) + quý T3/T6/T9 | 2026-07-19 |
| 21 | gate-structure-wireframe.md | sop/06-self-checklist/ | WS04 — #11 gate trước gửi khách (P0 100%) | 2026-07-19 |
| 22 | tier-1-structure-website.md | sop/06-self-checklist/ | WS04 — #11 full check thiết kế | 2026-07-19 |
| 23 | tier-1-visual-semantic.md | sop/06-self-checklist/ | WS04 — layout per page (operationalize sop/07 B0-B8) | 2026-07-19 |
| 24 | tier-1-ux-ui.md | sop/06-self-checklist/ | WS04 — wireframe T2 + CRO landing T8-T10 | 2026-07-19 |
| 25 | tier-1-cro-conversion.md | sop/06-self-checklist/ | WS04 — site-wide T2-T3 · landing T8-T10 · conversion path | 2026-07-19 |
| 26 | tier-1-entity.md | sop/06-self-checklist/ | WS06 — #13 gate cuối T1 & T3 (⚠ tactic gated) | 2026-07-19 |
| 27 | checklist-entity-onsite-web.md | sop/06-self-checklist/ | WS06 — #13 deep-dive onsite per trang | 2026-07-19 |
| 28 | tier-1-social-google-stack.md | sop/06-self-checklist/ | WS06 — entity offsite: social + Google Stack | 2026-07-19 |
| 29 | tier-1-offpage-backlink.md | sop/06-self-checklist/ | WS07 — #20, 25◇, 26 per batch (P0 7) | 2026-07-19 |
| 30 | tier-1-traffic-users.md | sop/06-self-checklist/ | WS07 — T8-T9 ⚠ Director duyệt (kèm baseline thông số 19.7) | 2026-07-19 |
| 31 | tier-1-geo.md | sop/06-self-checklist/ | WS08 — #14, 21, 28 (guardrail llms.txt/schema ≠ lever) | 2026-07-19 |
| 32 | tier-1-gbp-local.md | sop/06-self-checklist/ | WS03/WS08 — dự án local, vận hành GBP hằng tháng | 2026-07-19 |
| 33 | quality-content-ai.md | sop/06-self-checklist/ | WS05 — vận hành content AI 6 phase (pointer về tier-1) | 2026-07-19 |
| 34 | common-ai-errors.md | sop/06-self-checklist/ | WS05 — error catalog 28 lỗi QC/edit bài AI | 2026-07-19 |
| 35 | tier-3-ranking-drop-runbook.md | sop/06-self-checklist/ | WS03 — sự kiện rớt hạng/Google update (triage + 10 nhánh) | 2026-07-19 |
| 36 | checklist-xu-ly-ma-doc.md | sop/06-self-checklist/ | WS03 — sự kiện hack/mã độc (4 phase, 35 items) | 2026-07-19 |
| 37 | checklist-khoi-phuc-seo-ranking.md | sop/06-self-checklist/ | WS03 — phục hồi SAU sự cố (gate sạch 5/5) | 2026-07-19 |
| 38 | 10-offpage-process.md (sop/ gốc) | sop/10-offpage-process.md | WS07 — SOP offpage toàn diện (3 layer + method catalog 3 tier) | 2026-07-19 |
| 39 | checklist-phap-ly-content-website.md | sop/06-self-checklist/ | WS03 Audit T1 + WS05 per batch content — pháp lý content/website VN (PL-01→16, P0 7) | 2026-07-19 |
| 40 | checklist-project-intake-tham-dinh.md | sop/06-self-checklist/ | Tiền dự án (trước SETUP instance) — go/no-go thẩm định, Director duyệt (PI-01→14 + 6 red-flags, P0 6) | 2026-07-19 |

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
