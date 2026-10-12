# _TEMPLATES/ — Kho template deliverable (client-neutral)

Mỗi deliverable của 13 workstream có template chuẩn ở đây. Naming khi dùng: `<CLIENT>_<slug>_v<N>.<ext>` — clone template về đúng WS folder rồi điền, KHÔNG sửa template gốc (muốn nâng cấp template → vá ở master qua MIGRATION).

## Template cấp 1 (37 file)

| Nhóm | Template |
|---|---|
| Chiến lược & kế hoạch | `okrs.md` · `keyword-research.md` (#4, v2026.09.3) · `topical-map.md` · `traffic-plan.md` · `content-plan-matrix.md` (có mục 2b information gain + fan-out) · `structure-brief.md` |
| Audit & QC | `audit-toan-dien.md` (full 6 hạng mục) · `audit-technical.md` · `audit-content.md` · `audit-entity.md` · `audit-offsite.md` (lẻ, v2026.09.3) · `gap-analysis.md` · `qc-report.md` · `qp-intake.md` (phiếu đầu vào Lead điền trước khi gọi chẩn đoán QP) · `qp-chan-doan.md` (hồ sơ chẩn đoán Query Processing, đi kèm JSON + deck của skill `query-processing-diagnosis`, v2026.10.5) |
| Onpage · Entity · Offpage | `onpage-batch.md` · `entity-plan.md` (#13, gate G-ENT — WS 14) · `internal-link-plan.md` · `backlink-campaign.md` · `gate-offpage-decision.md` · `textlink` (xem skill) |
| GEO | `geo-baseline.md` |
| CRO (WS 13, v2026.09.3 → v2026.09.4) | `conversion-path.md` (#34) · `measurement-plan.md` + `tracking-qa.md` (#34, gate G1 — skill `cro-measurement-plan`) · `evidence-backlog.md` (#34/#35, khi >5 finding) · `ux-feature-brief.md` (#35, spec 10 mục component) · `heatmap-recording-review.md` (#35/#36, log sửa lỗi / rollout / A/B) |
| Reporting | `bao-cao-thang.md` · `report-config.example.yaml` (copy → `09-reporting/report-config.yaml`) |
| Client & vận hành | `kick-off.md` (có 3b Kỳ vọng & giới hạn) · `meeting-note.md` · `escalation-note.md` · `hop-dong-cam-ket.md` · `handover-checklist.md` (có trigger tái ký + bàn giao PIC + feedback khách) |
| Self-improving | `feedback-entry.md` · `lessons-workstream.md` · `retro-pha.md` |

## Subfolder

| Folder | Nội dung |
|---|---|
| `account/` | Bộ mẫu Account: BBNT, email templates, SOW-KPI naming standard, tư vấn hệ thống báo cáo, dashboard demo, 2 file Excel quản lý dự án/danh mục — đọc `account/README.md` |
| `examples/` | 5 bản điền MẪU (audit findings, báo cáo tháng, gate offpage, meeting note, QC report) — để xem "điền đúng trông thế nào", không dùng làm template |
| `weekly-report-slides/` | Skeleton deck báo cáo tuần (skin v5 + deck chrome) + bộ vận hành hệ báo cáo: `WEEKLY-DATA-CHECKLIST.md` (nhịp tuần, §5 = kích hoạt hệ 1 lần) · `PERIOD-DATA-CHECKLIST.md` (nhịp tháng/quý) · `RUNBOOK-bao-cao-ky.md` (câu lệnh tuần tự kéo số → 3 cổng kiểm → dựng deck → QA) — dùng bởi skill `gtv-weekly-report` |

## Template cấp ROOT (copy ra gốc instance, không vào WS folder)

| Template | Dùng khi |
|---|---|
| `BAN-GIAO-TEAM.md` | Bàn giao instance cho team: chuẩn bị máy, chìa khóa robot, câu lệnh chạy báo cáo tuần/tháng/quý, bảng ai-làm-gì. Copy ra root instance rồi thay `{{CLIENT}}` |

Luật nạp 80/20: chỉ mở đúng template cần cho deliverable đang làm (CLAUDE.md §10).
