---
master_version: v2026.07.1
---

# MIGRATION — Cập nhật instance lên version master mới

> **Dành cho:** SEO Lead Project của instance dự án (`PROJECTS/<client-slug>/` hoặc repo `seo-<client>`). Team Executive/Account KHÔNG chạy migration — chỉ cần `git pull` sau khi Lead xong.
>
> **`master_version` ở frontmatter** = version master mà bản này đang chạy. Master tag bằng git (`v2026.07`…); migration xong Claude cập nhật frontmatter này trong instance.
>
> **File này đồng thời là changelog infra của master** — mọi thay đổi infra ghi vào mục "Có gì mới" (rule cứng ở mục 5). Team tra 1 chỗ là thấy khác biệt giữa các version.
>
> Đọc kèm: [`SYNC.md`](./SYNC.md) mục 6 (nhận update từ master) · [`SETUP.md`](./SETUP.md) (setup client mới — không phải migration).

---

## 1. Có gì mới

### v2026.07.2 (2026-07-22) — Chế độ TUẦN: skill `gtv-weekly-report` + template slide tuần

> **Bổ sung 22/07 tối (round 3 Vincent):** slide-map luật #7-11 (ngôn ngữ senior-SEO không mật mã · mọi mục có TĂNG+GIẢM · top pages 20/chiều đủ Clicks/Pos WoW · blog 3 bài tiêu biểu/nhóm · deck editable); template `weekly-report-slides` nhúng khối INLINE EDIT (bấm E, localStorage, guard nav — đổi `EDIT_KEY` per deck) + ô Description bảng điền-tay 92px; `pv_movers.py` trả thêm cột intent/ngành/chủ đề/location; SKILL.md bước 2b.
>
> **Bổ sung 22/07 khuya (round 4 + 4b Vincent):** slide-map luật #12-15 — template có sẵn khối **DECK CHROME** (rail thumbnail «☰ Slides»/phím T + «▶ Present» fullscreen + deep-link `#n` hashchange; nút tự ẩn khi không rê chuột nên không dính PDF export; test Playwright PASS trên Chromium + WebKit) · action «Việc cần làm» phải xuống dòng từng ý dạng ul (cấm paragraph liền) · khối chữ cuối slide cấm chạm `.data-meta` (3 slide điển hình 1.1 Intent / 2.1 Apply / 2.2 Apply mặc định tách cặp bảng—nhận xét, soi PNG từng trang trước khi giao) · bảng nhóm Blog đủ Clicks + Pos (Pos dẫn xuất trọng số Imp từ CSV URL-level). Template: hàng SCOPE bảng «Cần client hỗ trợ» căn giữa dọc.

- **Skill `gtv-weekly-report`** (claude-only, KHÔNG vào `.agents/skills`): báo cáo tuần client-facing dạng slide, config-driven per client (`09-reporting/report-config.yaml` trong instance). Workflow 5 pha: RESOLVE tuần → FETCH bằng `scripts/fetch_weekly_data.py` (service account + `values.batchGet`, 1 call/workbook, output CSV + `digest.json` vào `02-raw/seo-data/weekly/` — LLM không nạp data lớn) → ANALYZE theo `references/analysis-rubric.md` (nhận xét 4 phần + lớp PATTERN so 4-8 tuần, file-back `09-reporting/analysis/`) → RENDER deck 1920×1080 theo `references/slide-map.md` → CHECK (spot-check 5 số + log). Kèm thang capture: Looker (Playwright) → sheet range (`scripts/capture_sheet_range.py` + `pdf2png.swift`) → GA4/GSC render → manual-slot.
- **`_TEMPLATES/weekly-report-slides/`** — skeleton deck client-neutral (12 loại slide exemplar, design system GTV, viewport-base frontend-slides, CSS completeness đã audit) + README. Instance customize tại `09-reporting/weekly-template/` (logo client).
- **`09-reporting/CLAUDE.md`** — thêm mục "Chế độ TUẦN (vận hành)": nguồn số = workbook client-agreed; deck tuần không render verdict nghiệm thu; ngoại lệ có chủ đích của Vòng tự kiểm bước 1 (chỉ áp cho tuần); tự kiểm bổ sung. Cập nhật luật nạp + Giới hạn runtime.
- Manifest workspace: đăng ký `gtv-weekly-report` (source = `SEO Production/skills/`, class claude-only) + thêm vào `shared_exclude`.
- GHI ĐÈ khi migration: 2 file trạm 09 + `_TEMPLATES/weekly-report-slides/` + `skills/gtv-weekly-report/` + mirror `.claude/skills/gtv-weekly-report/`. GIỮ: `09-reporting/report-config.yaml`, `weekly-template/`, `weekly/`, `analysis/`, `samples/` (dữ liệu instance).

### v2026.07.1 (2026-07-22) — Nội quy trạm + Quản đốc + Lớp mẫu (mindset 4 trụ cột Agentic SEO)

- **12 cặp `CLAUDE.md` + `AGENTS.md` nội quy trạm** (00, 01, 03→12): persona per trạm, bảng ĐƯỢC/KHÔNG ĐƯỢC, **vòng tự kiểm** (tự chấm theo checklist → sửa tới khi đạt → mới submit QC), luật nạp 80/20 riêng trạm. Trạm không lặp luật root — vênh thì root thắng. `02-raw/` + `99-archive/` giữ README-only.
- **`ORCHESTRATOR.md`** (quản đốc: lệnh cấp mục tiêu → vòng điều phối 6 bước → bảng chốt giám đốc → fan-out ≤4 — "Sub-agent là nhân viên. Orchestrator là quản đốc. Bạn là giám đốc.") + **`COMMANDS.md`** (bảng lệnh chuẩn per trạm).
- **`_TEMPLATES/examples/`** — lớp mẫu đạt chuẩn (trụ cột 4): 5 mẫu deliverable hư cấu "Công ty Ví Dụ / vidu.vn" (qc-report, audit-findings, gate-offpage KHÔNG-đẩy, báo cáo tháng có báo đỏ, meeting-note) + README luật nạp cùng-loại + quy trình promote mẫu thật.
- Root cập nhật: CLAUDE.md §3 thêm bước 0b đọc nội quy trạm + câu vòng tự kiểm, §4.4 đọc CLAUDE.md trạm, folder map thêm ORCHESTRATOR/COMMANDS; MIGRATION bảng 2.A thêm 2 file quản đốc + cặp nội quy per trạm; SYNC read-only 9 file root + cặp trạm; README bảng Đọc tiếp; thống nhất ID feedback `FB-<YYYY-MM-DD>-<alias>-<nn>`.

### v2026.07.1 (2026-07-22) — Nhận đợt mở rộng từ workspace (phiên song song 19-20/07)

- Kho gốc `06-self-checklist` mở rộng 8 → 30 file: bộ checklist theo lĩnh vực (tier-1-entity/geo/offpage-backlink/structure-website/ux-ui/cro-conversion/visual-semantic/gbp-local/social-google-stack/traffic-users), checklist sự kiện (khôi phục ranking, mã độc, pháp lý content, intake thẩm định), `checklist-kpi-okrs-planning` (KO-01→22), `monthly-project-review` (MR-01→21), gate-structure-wireframe, runbook tier-3 — knowledge pack đã nhận đủ kèm banner.
- ⚠ `tier-1-outline-am.md` trong pack bị đè bằng BẢN FULL 649 dòng (kèm evidence/theory — vượt ranh giới chưng cất đã chốt). CHỜ VINCENT QUYẾT: chưng cất lại hay chấp nhận bản full. Instance tạm GIỮ bản chưng cất cũ.
- Skills: +11 skill mới (acc-kickoff-setup, acc-weekly-sync, hreflang-planner, keyword-topic-url-mapping, local-seo-audit, map-pack-intelligence, programmatic-seo-builder, seo-drift-tracker, seo-logfile-analysis, serp-clustering, traffic-plan) + 4 skill cập nhật (technical-seo-audit, competitor-seo-gap-analysis, image-seo-optimize, topical-map-creation). Mirror .claude/.agents đã rebuild qua sync script.

### v2026.07 (vá 2026-07-18) — 17 fix từ đợt verification chéo

- DoD topical map chuẩn **15 mục** (trước ghi 14) — đồng bộ CLAUDE.md ma trận M, `index.md`, knowledge pack, cheat-sheet ws05, README WS05 và template topical-map (tách item Document Design Template / Content Briefs cho khớp sop/01).
- Chuẩn hóa `SYNC.md`: prompt migration mục 6 trỏ về bảng 2.A (GHI ĐÈ) / 2.B (GIỮ) của MIGRATION.md thay vì hard-code; danh sách read-only mục 3 đồng bộ đủ bảng 2.A; nhịp hằng ngày đổi thứ tự **commit TRƯỚC pull**; bootstrap `init -b main`; escape `\|` bảng ba file dùng chung.
- File thứ 4 `00-client-context/hop-dong-cam-ket.md` khai báo chính thức: SETUP bước 3 tạo + verify tồn tại, done-criteria ma trận M dòng Context, README WS00, pointer trong `kpi-commitments.md`.
- Ký hiệu **B0-B8** khai báo tường minh = «Bước 0»→«Bước 8» của `sop/07-visual-semantic.md` (CLAUDE.md, knowledge README, `_MANIFEST.md`, README WS04, cheat-sheet ws04); cheat-sheets ghi rõ 6 file WS03→WS08 + điều kiện ở pre-work §3.
- Dọn khác: quick-start README lên 5 lệnh (thêm `ingest`), banner 3 file .html lưu đồ không đóng gói (`sop/09-timeline/README.md`), `_MANIFEST.md` bỏ vế "Đang chưng cất bởi agent riêng", ngoại lệ trivial read-only ở CLAUDE.md §0, bảng 2.B ghi rõ trừ README `12-feedback-lessons/`, ghi chú standalone bước 7 trong SETUP.md.

### v2026.07 — khởi tạo master

Bản đầu tiên của hệ SEO Production. Không có instance cũ để migrate — entry này là mốc gốc.

- Timeline **33 công đoạn** (4 decision gate ◇) × **12 workstream**, tracking bằng `index.md` (bảng A/B/C/D).
- **4 thao tác vận hành:** Ingest · Work · QC · Feedback (`CLAUDE.md` §2) + pre-work protocol + ma trận M.
- **Knowledge pack** `02-raw/knowledge/`: 12 file copy nguyên + 5 file chưng cất từ SOP Semantic SEO + 6 cheat-sheet per workstream + `_MANIFEST.md`.
- **QC gate:** công đoạn có checklist không được set `done` khi chưa QC PASS; report theo `_TEMPLATES/qc-report.md` vào `03-audits/qc/`.
- **_TEMPLATES/** 21 file + `account/` (8 file mẫu báo cáo Account).
- **20 skill** trong `skills/` + mirror `.claude/skills/` và `.agents/skills/` (`gtv-client-report` chỉ Claude Code).
- **Git polyrepo:** master template repo + repo per client, main-only + phân vùng PIC + `merge=union` cho `log.md`/`feedback-log.md` (`SYNC.md`).
- **Self-improving 3 vòng:** feedback-log → lessons → vá master/wiki (`CLAUDE.md` §9).

*(Version sau append lên TRÊN entry này: `### v<tag> — <tên đợt>` + bullet thay đổi + file/nhóm bị ảnh hưởng.)*

---

## 2. Nguyên tắc vàng

> **GHI ĐÈ infra mới · GIỮ data dự án.**
> Infra = phần client-neutral (luật, template, skill, knowledge pack). Data dự án = context client + deliverable + registry + feedback — công sức của team, không được mất.

### A. GHI ĐÈ (copy từ master mới, đè lên instance)

| Nhóm | File / folder |
|---|---|
| Root luật | `CLAUDE.md` · `AGENT.md` · `AGENTS.md` · `README.md` · `SETUP.md` · `MIGRATION.md` · `SYNC.md` · `ORCHESTRATOR.md` · `COMMANDS.md` |
| Git config | `.gitignore` · `.gitattributes` |
| Templates | `_TEMPLATES/` toàn bộ (kể cả `account/`) |
| Skills | `skills/` + mirror `.claude/skills/` + `.agents/skills/` |
| Knowledge pack | `02-raw/knowledge/` toàn bộ |
| Screenshots infra | `02-raw/screenshots/README.md` (CHỈ README — ảnh là data) |
| WS infra | `README.md` + **`CLAUDE.md` + `AGENTS.md` (nội quy trạm)** của MỌI workstream folder (`00-client-context/` → `12-feedback-lessons/`) + `03-audits/qc/README.md` |
| Config | `config/` (`mcp.json.example`) |

### B. GIỮ (KHÔNG đụng — data + công sức của dự án)

| Nhóm | File / folder |
|---|---|
| Client context | `00-client-context/` toàn bộ (trừ `README.md` — thuộc nhóm A) |
| Registry | `index.md` · `log.md` |
| Raw client | `02-raw/contracts-proposals/` · `seo-data/` · `logfiles/` · `client-docs/` · `screenshots/` (mọi thứ NGOÀI `README.md`) |
| **Deliverable** | mọi file trong `01-strategy-okrs/` → `11-handover-maintenance/` (trừ `README.md` từng folder) |
| Feedback & lessons | `12-feedback-lessons/` toàn bộ (`feedback-log.md` · `lessons/` · `retro/`) — trừ `README.md` (thuộc nhóm A) |
| Archive | `99-archive/` |

> ⚠ **Điểm khéo:** workstream folder chứa CẢ `README.md` (infra) LẪN deliverable (data). Chỉ đè `README.md`, giữ nguyên deliverable. Vì vậy KHÔNG `cp -R` cả workstream folder — dùng cách Claude-assisted ở mục 3.

---

## 3. Mô hình 2 bước (Claude-assisted — chỉ SEO Lead)

Mô hình: **master là bản tham chiếu chuẩn** → lấy master version mới về trước → để Claude port khác biệt sang instance, theo đúng 2 bảng mục 2.

### Bước 1 — Lấy master version mới

- Máy Vincent: `SEO Production/` chính là master — pull mới nhất, xác nhận tag.
- Máy Lead: clone nông về folder tạm (lệnh đầy đủ ở `SYNC.md` mục 6):

```bash
git clone --depth 1 <master-repo> /tmp/seo-master-new
```

> Vì sao đè master an toàn 100%: master **client-neutral by design** — không chứa deliverable, không chứa client data. Khác hẳn instance, nơi chứa công sức cần giữ.

### Bước 2 — Port sang repo dự án

1. **Backup** instance (git đã là backup; muốn chắc thì zip 1 bản).
2. Mở AI runtime tại repo dự án → dán prompt migration dưới đây.
3. Claude diff master ↔ instance → báo danh sách file ghi đè → Lead **duyệt** → Claude ghi → commit → push. Team chỉ cần `git pull`.

### Prompt migration mẫu (Lead dán nguyên văn, thay 2 chỗ `<...>`)

```text
Tôi vừa lấy master SEO Production version <tag> về <path-master-mới>.
Đọc MIGRATION.md của bản master mới, so sánh với instance này và port
khác biệt infra: GHI ĐÈ đúng nhóm ở bảng 2.A, GIỮ NGUYÊN data dự án ở
bảng 2.B — đặc biệt workstream folder chỉ đè README.md, không đụng
deliverable. Báo diff (danh sách file ghi đè + file giữ nguyên) cho tôi
duyệt TRƯỚC khi ghi. Sau khi ghi: cập nhật frontmatter master_version
của MIGRATION.md instance thành <tag>, append log.md op=refactor, rồi
commit "migration: master <tag>" và push.
```

---

## 4. Sau migration — kiểm tra

- [ ] Frontmatter `master_version` của `MIGRATION.md` instance = tag mới.
- [ ] Deliverable trong `01-strategy-okrs/` → `11-handover-maintenance/` **còn nguyên** (spot-check vài file).
- [ ] `00-client-context/` + `index.md` + `log.md` + `12-feedback-lessons/` **còn nguyên**.
- [ ] `log.md` có entry op=`refactor` cho đợt migration.
- [ ] `git log` có commit `migration: master <tag>`; team pull không conflict.
- [ ] Mục "Có gì mới" của version mới: file/nhóm nào bị ảnh hưởng → mở kiểm tra đúng bản mới.

---

## 5. Rule cứng — changelog infra

**Mọi thay đổi infra ở master PHẢI ghi 2 nơi, cùng lúc với thay đổi:**

1. **`MIGRATION.md` (file này)** — append mục "Có gì mới" theo version + cập nhật bảng GHI ĐÈ/GIỮ nếu có file mới hoặc file đổi vai trò.
2. **`log.md`** — entry op = `refactor` / `setup` / `bookkeep`, ghi rõ file touched.

**"Thay đổi infra" gồm:** file client-neutral — luật root (`CLAUDE.md` · `AGENT.md` · `AGENTS.md` · `SETUP.md` · `SYNC.md` · `README.md`) · `_TEMPLATES/` · `skills/` + mirrors · `02-raw/knowledge/` · README workstream · `config/` · cấu trúc folder.

**KHÔNG tính:** data dự án (`00-client-context/`, deliverable, `index.md`, `log.md`, feedback/lessons) — thuộc từng instance, không vào MIGRATION.

**Nhịp tích lũy:** Lead distill lessons TUẦN → Vincent gộp lesson `scope: system` về master THÁNG → master tag version + broadcast MIGRATION theo QUÝ hoặc theo batch đủ lớn.
