# Folder Map + luật cứng folder

> Tách từ `CLAUDE.md` (§4) ngày 2026-09-02 (v2026.09.2) để file luật gọn — nội dung giữ nguyên văn. Router trỏ tới file này khi task cần.

## §4. Folder Map

```
SEO Production/                      (instance: PROJECTS/<client-slug>/)
├── CLAUDE.md · AGENT.md · AGENTS.md · README.md · SETUP.md · MIGRATION.md · SYNC.md
├── ORCHESTRATOR.md (quản đốc điều phối theo index) · COMMANDS.md (bảng lệnh chuẩn per trạm)
├── index.md                  ← registry: bảng A dự án + B 33 công đoạn + C nhịp quý + D deliverable
├── log.md                    ← timeline append-only
├── config/                   ← mcp.json.example (MCP cần cho dự án)
│
├── 00-client-context/        ← client-profile + marketing-foundation + kpi-commitments ({{VAR}} ở master)
├── 01-strategy-okrs/         ← WS Strategy
│
├── 02-raw/                   ← IMMUTABLE — nguồn gốc, AI không sửa
│   ├── contracts-proposals/  ← hợp đồng, proposal, phụ lục
│   ├── seo-data/             ← export tool, SERP scrape, crawl data · keywords/ = export keyword research (immutable)
│   ├── logfiles/             ← server logfile cho công đoạn #27
│   ├── client-docs/          ← tài liệu khách gửi
│   ├── knowledge/            ← SOP + checklist + cheat-sheets (READ-ONLY, vá ở master qua MIGRATION)
│   └── screenshots/          ← own-site/ · competitors/ · serp-ai/ · tools/ (§8)
│
├── 03-audits/                ← WS Audit · qc/ = kho QC report toàn dự án · full/ toàn diện · technical/ content/ entity/ offsite/ audit lẻ · ranking/ chẩn đoán bộ keyword cam kết
├── 04-structure-ux-cro/      ← WS Structure (cấu trúc lock #11 — CRO chuyển sang 13-cro/)
├── 05-content-plan/          ← WS Content plan (plan + tracking — KHÔNG chứa bài viết) · keyword-research/ · content-tracking/ (đấu nối fork, tools/content_sync.py)
├── 06-onpage-internal-link/  ← WS Onpage & IL
├── 07-offpage/               ← WS Offpage
├── 08-geo-ai-visibility/     ← WS GEO
├── 09-reporting/             ← WS Reporting
├── 10-client-management/     ← WS Client mgmt
├── 11-handover-maintenance/  ← WS Handover
├── 12-feedback-lessons/      ← feedback-log.md + lessons/ + retro/
├── 13-cro/                   ← WS CRO (#34–36): conversion path · ux-feature-brief · heatmap-recording-review
├── 14-entity/                ← WS Entity (#13, gate G-ENT): entity-plan · entity-profiles
│
├── 99-archive/               ← bản cũ khi thay đổi cấu trúc lớn
├── _TEMPLATES/               ← 32 template deliverable + account/ (mẫu báo cáo Account)
├── tools/                    ← content_sync.py (đấu nối fork content) · sync-skills.sh · ai-assist/ (Jev + EmbeddingGemma) · gsc/gsc.sh (GSC API)
└── skills/                   ← 37 skill SEO đóng gói theo dự án
```

Luật cứng folder:

1. `02-raw/` chỉ **ADD** — không sửa, không xóa, không đổi tên file đã có. Muốn phiên bản mới → thêm file mới.
2. `02-raw/knowledge/` **read-only trong instance** — phát hiện checklist sai/thiếu → đề xuất vá ở MASTER (vòng 2, §9), instance nhận bản vá qua `MIGRATION.md`. Không bao giờ sửa tại chỗ.
3. WS folder (01-11) chứa CẢ `README.md` (infra — bị đè khi migration) LẪN deliverable (của dự án — giữ nguyên). Không trộn vai trò: README không chứa dữ liệu client, deliverable không chứa luật.
4. Trước khi Work trong một WS folder, đọc **nội quy trạm** `CLAUDE.md` của folder đó (persona, được/không được, vòng tự kiểm) + `README.md` (công đoạn phụ trách, deliverable chuẩn, done-criteria). Folder không có CLAUDE.md (`02-raw/`, `99-archive/`) → chỉ README.

---
