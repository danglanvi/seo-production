# COMMANDS — Bảng lệnh chuẩn cho team

> **Bảng tra, không phải tài liệu khái niệm.** Lệnh là mẫu câu ngôn ngữ tự nhiên — gõ khác đi vẫn hiểu, miễn đủ tham số; chạy được trên mọi runtime (Claude Code / Codex / Antigravity), riêng nhóm Reporting cần Claude Code.
>
> Đọc sâu hơn: `README.md` (tổng quan) · `CLAUDE.md` (luật vận hành + ma trận M §5) · `ORCHESTRATOR.md` (vòng điều phối, chốt giám đốc, fan-out) · `SETUP.md` (dựng instance) · `SYNC.md` (git).
>
> Mọi lệnh tuân Execution Rule: show plan → chờ duyệt → thực hiện. Công đoạn có checklist: KHÔNG `done` khi QC chưa PASS.

---

## 1. Vận hành chung

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `setup client <tên>` | Protocol 9 bước `SETUP.md`: điền context + bảng A + retiming gói 8/10/12 tháng (chạy SAU khi đã duplicate master + drop raw) | Lead | `setup client acme` |
| `đến lượt gì tiếp?` / `status dự án` | Đọc bảng B + C `index.md` → công đoạn đến lượt, việc `blocked` + lý do, nhịp quý đến kỳ, mốc cứng sắp chạm | Mọi người | `đến lượt gì tiếp?` |
| `làm công đoạn <n>` / `làm <deliverable>` | **Trạm-first** (`CLAUDE.md` §0.5): tra ma trận M → nạp nội quy trạm → làm trong phiên → tự kiểm → QC → update index + log. Nhiều item cùng trạm (onpage 10 bài, audit 5 URL) = lặp tuần tự, báo từng item | PIC công đoạn | `làm công đoạn 5` · `onpage 10 bài trong sheet X` |
| `chạy trọn công đoạn <n>` / `chạy <n>→<m> nối tiếp` | Điều phối nâng cao (`ORCHESTRATOR.md` mục 2): quản đốc tra bảng, xếp việc nhiều công đoạn, chốt giám đốc; sub-agent chỉ khi thêm "song song"/"fan-out" | Lead | `chạy trọn công đoạn 13→14` |
| `ingest <file> vào 02-raw` | Phân loại raw theo signal (`CLAUDE.md` §2.1) + chưng cất context — không sửa raw, op `ingest` | Mọi người | `ingest hop-dong-acme.pdf vào 02-raw` |
| `feedback: <nội dung>` | Append `12-feedback-lessons/feedback-log.md`; pattern lặp ≥2 lần → đề xuất promote lesson (§9) | Mọi người | `feedback: khách muốn mục GEO riêng trong báo cáo` |
| `kéo dữ liệu content` / `project sync` | `python3 tools/project_sync.py pull`: kéo repo content cùng khách từ GitHub → trạng thái bài, bài đã humanize, snapshot Kho tri thức khách (`_REFERENCE/project-sync.md`) | Mọi người, đầu phiên | `kéo dữ liệu content` |

Nội quy chung: root `CLAUDE.md` (4 thao tác §2, pre-work §3) + `AGENT.md`.

## 2. Lệnh theo trạm (map ma trận M — `CLAUDE.md` §5)

### Audit — công đoạn 2, 5, 6◇, 7(plan), 22◇, 24, 27, 29

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `audit toàn diện` | #5 (T1) / #27 (T7, kèm logfile): audit 6 hạng mục theo `sop/05-audit-checklist.md` + tier-3 → phân loại action full URL + owner/deadline | Lead | `audit toàn diện quý 1` |
| `audit định kỳ T<k>` | Audit theo nhịp bảng C: #24 (T6) / #29 (T8-T9 tactic nâng cao); chuẩn bị input cho gate #22 khi tới kỳ | Lead / Executive | `audit định kỳ T6` |

Nội quy trạm: `03-audits/CLAUDE.md` + `03-audits/README.md` + cheat-sheet `02-raw/knowledge/cheat-sheets/ws03-audit.md`.

### Structure — công đoạn 11

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `review cấu trúc <page-type>` | Chấm wireframe + HTML template semantic theo `tier-1-structure-website.md` → `gate-structure-wireframe.md` (P0 100% trước khi gửi khách); mốc cứng lock ≤15 ngày đầu T2 | Lead + CRO + Coder | `review cấu trúc trang dịch vụ` |

Nội quy trạm: `04-structure-ux-cro/CLAUDE.md` + `04-structure-ux-cro/README.md` + cheat-sheet `ws04-structure.md`.

### Content plan — công đoạn 4, 9, 10, 15, 16, 17, 19

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `lập topical map` | #10: topical map + SCN theo `_TEMPLATES/topical-map.md`, DoD 15 mục (`sop/01-topical-map.md`); demo T1 → chốt đầu T2 | Lead / Content Leader | `lập topical map cụm dịch vụ` |
| `plan traffic FULL` | #17: plan ≥ cam kết +20% theo `_TEMPLATES/traffic-plan.md` — chốt là chốt giám đốc (SEO Director duyệt) | Content Leader | `plan traffic FULL cho quý 3` |
| `tracking content tuần` | Nhận bài + QC verdict từ fork `Content Production - <client>/` → cập nhật % mốc #15/#16/#19 bảng B + content-plan-matrix; op `bookkeep`. Không viết bài bên này (§5.4) | Content Leader | `tracking content tuần này` |

Nội quy trạm: `05-content-plan/CLAUDE.md` + `05-content-plan/README.md` + cheat-sheet `ws05-content-plan.md`.

### Onpage & Internal link — công đoạn 7(execute), 13, 18, 23

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `onpage batch <danh sách URL> tier <1\|2\|3>` | Chạy batch theo `sop/08-onpage-checklist.md` (P0 → /23 → /31 → /39) + `_TEMPLATES/onpage-batch.md`; không ghi tier → tra Ghi chú dòng #12 | Executive / Lead | `onpage batch 12 URL danh mục tier 1` |
| `internal link plan cluster <x>` | #18: IL semantic theo `sop/03-internal-linking.md` + `_TEMPLATES/internal-link-plan.md`; done-criteria orphan = 0 | Lead | `internal link plan cluster máy lọc nước` |
| `chấm MX batch <n>` | Nâng cấp định dạng MX1–MX6 (sơ đồ, bảng, biểu đồ, screenshot/video, khối tương tác): chấm riêng, không tính /23 · /31 · /39, ghi mục 7 của batch report kèm việc đề xuất + người làm (`06-onpage-internal-link/CLAUDE.md`) | Executive / Lead | `chấm MX batch 3` |
| `xem batch <file> dạng HTML` | `python3 tools/onpage_report_html.py <batch-report.md>` → bảng nhiệt URL × item, sắp xếp theo điểm, lọc theo item FAIL, kèm bảng MX và AX; file `.md` vẫn là bản gốc | Mọi người | `xem batch ACME_onpage-batch-t3_v1.md dạng HTML` |

Nội quy trạm: `06-onpage-internal-link/CLAUDE.md` + `06-onpage-internal-link/README.md` + cheat-sheet `ws06-onpage-il.md`.

### Offpage — công đoạn 20, 25◇, 26

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `chạy gate offpage` | #25◇: chấm theo Lưu đồ B + DoD `gate-offpage-decision`; verdict chỉ là ĐỀ XUẤT — Lead chốt, ghi `gate: <verdict>` + log op `gate`. Mặc định 90% dự án KHÔNG cần đẩy link | Lead | `chạy gate offpage` |
| `plan backlink` | #20 (nền + guest post phantom) / #26 (đẩy mạnh + textlink PR): research → plan → `_TEMPLATES/backlink-campaign.md`; QC per batch `tier-1-offpage-backlink.md` | Lead | `plan backlink nền T4` |

Nội quy trạm: `07-offpage/CLAUDE.md` + `07-offpage/README.md` + cheat-sheet `ws07-offpage.md`.

### GEO — công đoạn 14, 21, 28

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `geo baseline` | #14: prompt set theo funnel + KPI GEO theo `_TEMPLATES/geo-baseline.md`, DoD geo-baseline; guardrail `tier-1-geo.md` | Lead | `geo baseline` |
| `đo AI visibility kỳ <k>` | Theo bảng C: baseline T1 · giữa kỳ T6 (#24) · báo cáo T10; đợt FS & AIO #21/#28 phải kèm danh sách query + kết quả cite | Lead / Executive | `đo AI visibility kỳ T6` |

Nội quy trạm: `08-geo-ai-visibility/CLAUDE.md` + `08-geo-ai-visibility/README.md` + cheat-sheet `ws08-geo.md`.

### Reporting — công đoạn 30◇, 32 — ⚠ CHỈ Claude Code

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `báo cáo tháng <n>` | Skill `gtv-client-report` + template `bao-cao-thang.md`; trễ mốc cứng phải báo đỏ trong báo cáo (§6.2); op `report` | Account / Lead | `báo cáo tháng 2` |
| `báo cáo quý` | Gộp nhịp quý bảng C: OKRs + audit + AI visibility của kỳ | Account / Lead | `báo cáo quý 2` |
| `báo cáo nghiệm thu` | #30◇/#32: báo cáo kép KPI + AI visibility, BBNT theo `_TEMPLATES/account/`; gửi khách = chốt giám đốc | Account | `báo cáo nghiệm thu đợt 2` |

Nội quy trạm: `09-reporting/CLAUDE.md` + `09-reporting/README.md`. Skill `gtv-client-report` chỉ chạy Claude Code — runtime khác dùng template thủ công + báo rõ giới hạn (ma trận M ghi chú 4, `SYNC.md` mục 8).

### Client management — công đoạn 12, 31

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `chuẩn bị kick-off` | #12: agenda + `_TEMPLATES/kick-off.md` (skill `acc-kickoff-setup`); chốt Tier 2 checklist được bật → ghi vào Ghi chú dòng #12 bảng B | Account | `chuẩn bị kick-off acme` |
| `meeting note <ngày>` | `_TEMPLATES/meeting-note.md`: action items + owner; op `meeting` | Account | `meeting note 2026-07-22` |

Nội quy trạm: `10-client-management/CLAUDE.md` + `10-client-management/README.md`.

### Handover — công đoạn 33

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `chuẩn bị bàn giao` | #33: `_TEMPLATES/handover-checklist.md` theo `khung-duy-tri.md` — checklist ký nhận + lịch duy trì quý; op `handover` | Lead + Account | `chuẩn bị bàn giao` |

Nội quy trạm: `11-handover-maintenance/CLAUDE.md` + `11-handover-maintenance/README.md`.

### Feedback & lessons — xuyên suốt

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `distill lessons tuần` | Nghi thức tuần (`SYNC.md` mục 5): block pending trong feedback-log → lesson theo `_TEMPLATES/lessons-workstream.md` (frontmatter scope) + retro cuối pha; op `lesson`/`retro` | Lead | `distill lessons tuần` |

Nội quy trạm: `12-feedback-lessons/CLAUDE.md` + `12-feedback-lessons/README.md`.

## 3. QC

| Lệnh | Làm gì | Ai dùng | Ví dụ |
|---|---|---|---|
| `QC <path> theo công đoạn <n> [tier 1\|2\|3] [role self\|verify\|lead]` | Prompt chuẩn §7.2: tra ma trận M → chấm TỪNG item theo ID + evidence → report `03-audits/qc/QC-<##>-<slug>-<YYYYMMDD>.md` → verdict vào index. Mặc định: tier tra Ghi chú #12, role `self` | Người làm / người được chỉ định | `QC 07-offpage/acme_backlink-campaign_v1.md theo công đoạn 26 tier 1 role self` |
| `QC random WS <XX>` | Lead chấm xác suất 25-30% deliverable của workstream (role `lead`) — mọi gate ◇ luôn thuộc diện Lead chấm | Lead | `QC random WS 06` |

Nội quy: `CLAUDE.md` §7 — ngưỡng PASS/FAIL lấy của chính checklist; `CONDITIONAL-PASS` và waiver `done*` chỉ Lead quyết.

## 4. Git

Không lặp lệnh git ở đây — theo `SYNC.md`: mục 2 nhịp ngày (pull đầu ca · commit + push cuối MỖI khối việc, message `<client>: <workstream> — <việc>`), mục 4 khi conflict (dán prompt in sẵn, nhớ KHUNG ĐỎ 3 lệnh cấm), mục 5 nghi thức tuần của Lead, mục 6 nhận update master (MIGRATION — chỉ Lead).
