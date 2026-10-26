# SEO Production — Hệ vận hành dự án SEO client (GTV)

> 🔧 **Máy mới clone repo?** Mở repo bằng Claude Code rồi nói *"cài đặt giúp tôi repo này"* — hoặc đọc [`_SETUP/SETUP-MAY.md`](_SETUP/SETUP-MAY.md). Cần Python 3, Node và một Google service account **của riêng bạn** ([`_SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md`](_SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md)).

Master template cho một dự án SEO delivery trọn gói: 36 công đoạn (33 gốc + 3 CRO), 14 workstream, 5 pha, QC theo checklist, self-improving qua feedback → lessons. Folder này là **master client-neutral** — mỗi client nhân bản thành instance tại `PROJECTS/<client-slug>/` (hoặc team clone repo `seo-<client>` riêng). Không điền dữ liệu client vào master.

## Sơ đồ 5 pha (gói chuẩn 10 tháng)

```
┌─ Pha 1 · Khởi động (T1) ─────────── #1-3, 5, 8, 12 — ký HĐ + OKRs, phân tích, foundation,
│                                       audit toàn diện, chiến lược, kick-off
├─ Pha 2 · Nền tảng & lõi (T1-T3) ─── #4, 6◇, 7, 9-11, 13-16 — topical map + SCN, cấu trúc site,
│                                       entity, GEO baseline, content URL SEO + Core Section
├─ Pha 3 · Mở rộng (T3-T6) ────────── #17-24 — plan traffic FULL, internal link, content non-URL,
│                                       backlink nền, GEO đợt 1, gate initial ranking 22◇, audit T6
├─ Pha 4 · Thúc đẩy (T6-T9) ───────── #25◇-29 (+ Traffic users ⚠ optional) — Gate Offpage,
│                                       backlink đẩy mạnh + textlink PR, logfile + FULL audit, GEO đợt 2
└─ Pha 5 · Về đích (T10) ──────────── #30◇-33 — gate KPI cam kết, review điều chỉnh,
                                        báo cáo kép + case study, bàn giao Duy trì
   WS 13 · CRO (song song) ─────────── #34 conversion path + tracking (T2-T3) · #35 UX/UI brief + heatmap (T4-T6)
                                        · #36 tối ưu landing + A/B (T7-T9)
   WS 14 · Entity ──────────────────── #13 entity onsite/offsite, gate G-ENT (cuối T1 → ≤15 ngày đầu T3)
```

- ◇ = decision gate (#6, 22, 25, 30). Kết quả gate ghi vào cột Ghi chú của `index.md`.
- Biến thể 8/12 tháng: bảng retiming trong `02-raw/knowledge/sop/09-timeline/10-thang-thuc-day.md`.
- Toàn bộ 36 công đoạn theo dõi tại bảng B của `index.md`; mọi thao tác append `log.md`.

## 14 workstream

| WS | Folder | Việc chính |
|---|---|---|
| Context | `00-client-context/` | Hồ sơ client, marketing foundation, KPI cam kết trích từ hợp đồng |
| Strategy | `01-strategy-okrs/` | Chiến lược dự án + OKRs quý, backup plan, SEO Director duyệt |
| Audit | `03-audits/` | Audit toàn diện (`full/`) + lẻ (`technical/ content/ entity/ offsite/`), gap analysis, logfile, kho QC report (`qc/`) |
| Structure | `04-structure-ux-cro/` | Cấu trúc site + wireframe UX/UI semantic, lock ≤15 ngày đầu T2 (CRO tách sang WS 13) |
| Content plan | `05-content-plan/` | Keyword research (`keyword-research/`), topical map + SCN, plan traffic, ma trận content, đấu nối fork (`content-tracking/` + `tools/content_sync.py`) |
| Onpage & IL | `06-onpage-internal-link/` | Batch onpage /23, internal link semantic, orphan = 0, đăng/sửa bài WordPress |
| Offpage | `07-offpage/` | Backlink nền → Gate Offpage → đẩy mạnh + textlink PR, anchor plan + velocity |
| GEO | `08-geo-ai-visibility/` | Baseline AI visibility, FS & AIO 2 đợt, llm.txt, citation share |
| Reporting | `09-reporting/` | Báo cáo tháng/quý/nghiệm thu, báo cáo kép + case study T10 |
| Client mgmt | `10-client-management/` | Kick-off, meeting note, action items, điều chỉnh theo review |
| Handover | `11-handover-maintenance/` | Checklist bàn giao ký nhận, khung duy trì quý |
| Feedback | `12-feedback-lessons/` | Feedback log → lessons → retro pha; self-improving 3 vòng |
| CRO | `13-cro/` | Conversion path theo cụm intent + tracking ≤T3, UX/UI feature brief, heatmap-recording → A/B (#34–36, skill `cro-audit`) |
| Entity | `14-entity/` | Brand Info Pack, Entity Home, bộ trang entity, schema @id, NAP onsite–offsite, gate G-ENT (#13, skill `entity-seo-plan`) |

Chi tiết công đoạn ↔ WS ↔ checklist ↔ skill: ma trận M trong `CLAUDE.md`. README từng WS folder ghi deliverable chuẩn + done-criteria.

## Quick start — 5 lệnh

| Lệnh | Việc AI làm |
|---|---|
| `setup client <tên>` | Điền context + bảng A index + retiming gói 8/10/12 tháng — chạy SAU khi đã duplicate master và drop raw bằng tay (SETUP.md bước 1-2; protocol đủ 9 bước) |
| `làm công đoạn <n>` | Pre-work protocol → làm deliverable theo template + cheat-sheet WS → update index + log |
| `QC <path> theo công đoạn <n>` | Chấm từng item theo checklist ma trận M, evidence cụ thể → QC report vào `03-audits/qc/` + verdict PASS/FAIL vào index |
| `feedback: <nội dung>` | Ghi entry vào `12-feedback-lessons/feedback-log.md`; pattern lặp ≥2 lần → đề xuất promote lesson |
| `ingest <file> vào 02-raw` | Phân loại raw + chưng cất context (CLAUDE.md §2) |

Luật cứng: công đoạn có checklist không được set done khi chưa QC PASS. `02-raw/` immutable — chỉ thêm, không sửa/xóa. `02-raw/knowledge/` chỉ vá ở master, instance nhận qua MIGRATION.

## Cấu trúc folder (tóm tắt)

```
SEO Production/
├── CLAUDE.md · AGENT.md · AGENTS.md · README.md · SETUP.md · MIGRATION.md · SYNC.md
├── index.md (registry 36 công đoạn) · log.md (timeline append-only) · config/ · tools/content_sync.py
├── 00-client-context/            ← context client ({{VAR}} ở master, điền lúc setup)
├── 01-strategy-okrs/ … 11-handover-maintenance/ · 13-cro/ · 14-entity/   ← 13 WS folder (+ 00, 12) mỗi folder có README riêng
├── 02-raw/                       ← IMMUTABLE: contracts, seo-data, logfiles, client-docs,
│   ├── knowledge/                   knowledge pack (sop/ + cheat-sheets/ + _MANIFEST.md)
│   └── screenshots/                 own-site/ · competitors/ · serp-ai/ · tools/
├── 12-feedback-lessons/          ← feedback-log.md + lessons/ + retro/
├── 99-archive/ · _TEMPLATES/ (38 template + account/ + examples/ + weekly-report-slides/)
├── skills/ (60 skill delivery — canonical) · .claude/skills/ (mirror Claude) · .agents/skills/ (mirror Codex)
└── tools/sync-skills.sh              ← đồng bộ skills/ → 2 mirror khi chạy standalone
```

## Ngày đầu tiên (team mới nhận folder)

1. Mở deck **`GTV_SEO-Production_huong-dan-cai-dat_v1.html`** (root folder này) — hướng dẫn cài đặt Claude Code / Codex, MCP, chìa khóa robot và cách dùng từng bước.
2. Mở Claude Code (hoặc Codex) tại folder → nói: *«đọc CLAUDE.md và README.md rồi tóm tắt cho tôi»*.
3. Thử 2 lệnh đầu trong `COMMANDS.md`. Xong — bạn đã vận hành được hệ.

## Đọc tiếp

| File | Nội dung |
|---|---|
| `CLAUDE.md` | Luật vận hành đầy đủ: 4 thao tác, pre-work protocol, ma trận M, QC spec, self-improving |
| `AGENT.md` | Persona giao tiếp: Tiếng Việt thuần, cách present plan + QC findings |
| `AGENTS.md` | Entry point cho mọi agent runtime (Claude Code / Codex / Antigravity) |
| `ORCHESTRATOR.md` | Tùy chọn nâng cao — quản đốc khi gọi rõ "chạy trọn công đoạn <n>"/"nối tiếp"/"song song"; việc thường ngày đi theo router `CLAUDE.md` §0.5 (trạm-first) |
| `COMMANDS.md` | Bảng lệnh chuẩn per trạm cho team |
| `SETUP.md` | Protocol "setup client <tên>" 9 bước |
| `SYNC.md` | Git đồng bộ team: nhịp pull/push, phân vùng PIC, xử lý conflict, MIGRATION cho Lead |
| `MIGRATION.md` | Update master → instance: bảng GHI ĐÈ / GIỮ, master_version |

## Bắt đầu theo runtime — 05/09/2026

Mở **chính repo này** làm workspace; luật chuyên môn giữ ở `CLAUDE.md`, persona ở `AGENT.md`.

| Runtime | Đường nạp luật và skill | Ca thử read-only |
|---|---|---|
| Claude Code | CLAUDE.md → AGENT.md → luật trạm; .claude/skills từ skills/ | “Đọc luật, cho biết trạm và gate của việc tôi định làm; chưa sửa file.” |
| Codex | AGENTS.md yêu cầu đọc CLAUDE.md + AGENT.md; .agents/skills | Cùng ca thử; đối chiếu đúng entity và nơi trả output trong luật. |
| Antigravity | Global bootstrap + .agents/rules trỏ AGENTS/CLAUDE/AGENT; .agents/skills | Kiểm rule trong Customizations; chọn Always On nếu chưa bật, rồi chạy ca thử trên. |
| Hermes | Chỉ profile được cấp cho vai trò này; terminal.cwd/workdir của job phải nạp AGENTS.md của profile | Hỏi nguồn được đọc, nơi được ghi và điểm cần người duyệt; không cấp cả repo cho bot team chỉ để thử. |

Kiểm môi trường: `python3 _SETUP/setup_doctor.py --json`

Skill `private`/`claude-only` giữ giới hạn trong manifest; có mirror không đồng nghĩa có quyền dữ liệu. Bản standalone không cần toàn bộ workspace của Vincent: thiếu nguồn ngoài repo thì dùng fallback của skill hoặc báo phần thiếu. Chỉ sync canonical của repo; giữ fork có chủ đích. Có quyền read-only không tự có quyền gửi/publish.
