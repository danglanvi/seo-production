# _TEMPLATES/ — Kho template deliverable (client-neutral)

Mỗi deliverable của 12 workstream có template chuẩn ở đây. Naming khi dùng: `<CLIENT>_<slug>_v<N>.<ext>` — clone template về đúng WS folder rồi điền, KHÔNG sửa template gốc (muốn nâng cấp template → vá ở master qua MIGRATION).

## Template cấp 1 (21 file)

| Nhóm | Template |
|---|---|
| Chiến lược & kế hoạch | `okrs.md` · `topical-map.md` · `traffic-plan.md` · `content-plan-matrix.md` · `structure-brief.md` |
| Audit & QC | `audit-toan-dien.md` · `gap-analysis.md` · `qc-report.md` |
| Offpage | `backlink-campaign.md` · `gate-offpage-decision.md` · `internal-link-plan.md` · `textlink` (xem skill) |
| GEO | `geo-baseline.md` |
| Client & vận hành | `kick-off.md` · `meeting-note.md` · `bao-cao-thang.md` · `hop-dong-cam-ket.md` · `handover-checklist.md` |
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
