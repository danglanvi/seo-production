# Log — SEO Production

Timeline append-only của dự án. Mỗi thao tác = 1 entry, thêm vào CUỐI file, không sửa entry cũ.

## Format entry

```
## [YYYY-MM-DD] <op> | <short title> — @<alias>
- <what happened>
- Files touched: <paths>
- Công đoạn: #<n> (nếu có) · WS: <XX>
```

Luật ghi:

1. Mỗi entry bắt buộc có `op` đúng vocabulary bên dưới + alias người/agent thực hiện.
2. `Files touched` liệt kê path tương đối từ root instance; nhiều file thì liệt kê hết hoặc ghi theo folder.
3. `Công đoạn / WS` bỏ qua bằng `—` khi thao tác không gắn công đoạn cụ thể (vd `lint`, `bookkeep`).
4. Parse nhanh 10 op gần nhất: `grep "^## \[" log.md | tail -10`.

## Vocabulary op

| op | Khi dùng |
|---|---|
| `setup` | Setup instance client theo SETUP.md (duplicate master, fill context, retiming) |
| `ingest` | Đưa file mới vào `02-raw/` + phân loại + cập nhật index bảng D |
| `capture` | Chụp/lưu screenshot vào `02-raw/screenshots/` — 1 entry/đợt, kèm "Dùng cho:" |
| `work` | Làm 1 công đoạn / 1 deliverable trong WS folder |
| `qc` | Chấm QC deliverable theo checklist → report `03-audits/qc/` + verdict vào index |
| `feedback` | Ghi feedback client/Lead/QC-fail-lặp vào `12-feedback-lessons/feedback-log.md` |
| `lesson` | Promote pattern lặp ≥2 lần thành `lessons-ws<XX>.md` |
| `retro` | Retro cuối pha → `12-feedback-lessons/retro/retro-pha-<n>.md` |
| `gate` | Chốt 1 trong 4 nút decision ◇ (#6, #22, #25, #30) — ghi verdict + link deliverable |
| `report` | Báo cáo client (tháng / quý / nghiệm thu) |
| `meeting` | Meeting note (kick-off, review, họp client) — action items + owner |
| `handover` | Bàn giao / chuyển giao duy trì (công đoạn #33) |
| `lint` | Rà index vs thực tế folder — chạy hàng tháng |
| `bookkeep` | Cập nhật sổ sách (index, registry, link chéo) không thuộc op khác |
| `refactor` | Thay đổi infra (template/knowledge/skill) — bắt buộc ghi kèm MIGRATION.md |
| `archive` | Chuyển file vào `99-archive/` |
| `bootstrap` | Khởi tạo master / instance lần đầu |

---

## [2026-07-17] bootstrap | Khởi tạo master SEO Production v2026.07 — @vincent

- Dựng master SEO Production theo Blueprint A đã duyệt 17/07/2026: cây folder 00→12 + 99-archive, file hệ thống (CLAUDE.md, AGENT.md, AGENTS.md, README.md, SETUP.md, MIGRATION.md, SYNC.md), index.md prefill 33 công đoạn + dòng optional Traffic users, knowledge pack `02-raw/knowledge/`, `_TEMPLATES/` và 20 skill.
- Files touched: toàn bộ cây `SEO Production/`
- Công đoạn: — · WS: —

## [2026-07-18] refactor | Vá 17 finding verification — @claude

- Nhóm consistency: DoD topical map 14 → **15 mục** (đồng bộ 8 file, tách item gộp trong template topical-map); ký hiệu B0-B8 khai báo tường minh = «Bước 0»→«Bước 8» sop/07; cheat-sheets ghi rõ 6 file WS03→WS08 + điều kiện pre-work §3; banner sop/09-timeline ghi 3 file .html lưu đồ không đóng gói; `_MANIFEST.md` bỏ vế "Đang chưng cất bởi agent riêng" (hàng #13-17).
- Nhóm hop-dong-cam-ket.md (file thứ 4 của 00-client-context, phương án b): khai báo ở README WS00, done-criteria ma trận M, pointer kpi-commitments, verify SETUP mục 2.
- Nhóm SYNC/MIGRATION: prompt migration trỏ bảng 2.A/2.B thay vì hard-code; danh sách read-only mục 3 đồng bộ đủ bảng 2.A; commit TRƯỚC pull ở nhịp hằng ngày; `init -b main`; escape `\|` bảng ba file dùng chung; bảng 2.B ghi rõ trừ README `12-feedback-lessons/`; path `knowledge/` trần → `02-raw/knowledge/`.
- Nhóm quick-start & rule: README lên 5 lệnh (thêm `ingest`, sửa mô tả `setup client`); SETUP mục 4 trỏ bảng quick-start README; ghi chú standalone bước 7; CLAUDE.md §0 ngoại lệ trivial read-only theo AGENT.md §4.
- Files touched: CLAUDE.md, README.md, SETUP.md, SYNC.md, MIGRATION.md, index.md, log.md, 00-client-context/README.md, 00-client-context/kpi-commitments.md, 04-structure-ux-cro/README.md, 05-content-plan/README.md, _TEMPLATES/topical-map.md, 02-raw/knowledge/README.md, 02-raw/knowledge/_MANIFEST.md, 02-raw/knowledge/cheat-sheets/ws04-structure.md, 02-raw/knowledge/cheat-sheets/ws05-content-plan.md, 02-raw/knowledge/sop/09-timeline/README.md
- Công đoạn: — · WS: —

## [2026-07-19] bookkeep | Thêm 10 skill mới đợt 07/2026 — @claude

- Thêm 10 skill vào `skills/` (đồng bộ twin từ root `skills/`, đã đăng ký manifest + chạy sync): **Wave 1 gap quy trình** — seo-logfile-analysis (công đoạn 27, advertools+GoAccess, verify Googlebot reverse-DNS), traffic-plan (công đoạn 9+17, mode Outer-first/FULL +20%, CHỜ DUYỆT Director), keyword-topic-url-mapping (công đoạn 4, SERP-overlap clustering), acc-kickoff-setup (phân tích HĐ + checklist 4 nhóm T1), acc-weekly-sync (sync brief 5 phần + 5 red-flags); **net-new từ gap-audit claude-seo** — seo-drift-tracker (snapshot/diff element sau deploy), hreflang-planner (audit/generate, case vn→vi), programmatic-seo-builder (gate G1-G3, Content Leader duyệt template), local-seo-audit + map-pack-intelligence (cặp local: website-signals + geo-grid SoLV).
- Ma trận M (§5.2) cập nhật 4 hàng: Context (+acc-kickoff-setup), Audit (+4 skill), Content plan (+3 skill), Client mgmt (+2 skill acc).
- Nguồn quyết định: đề xuất skills 07/2026 + phân loại DROP/INTEGRATE/CREATE-NEW từ claude-seo (11.7k★) + so sánh DataForSEO vs SerpApi. Grounding: sop/01, sop/04, sop/06-self-checklist/tier-3, sop/09-timeline (bản Account), wiki concepts (wikilinks đã verify tồn tại).
- Files touched: skills/ (10 folder mới), CLAUDE.md §5.2, log.md
- Công đoạn: — · WS: —

## [2026-07-19] bookkeep | Skill wave 2 + hệ checklist QC v3 — @claude

- Skill mới: serp-clustering (DATA layer clustering, tách theo quyết định Vincent). Nâng cấp INTEGRATE từ gap-audit claude-seo: technical-seo-audit v1.4 (Health Score 0-100 + sitemap GENERATE + falsifiability field), image-seo-optimize v1.1 (performance layer), seo-research v1.2 (SXO page-type-mismatch), seo-brief v1.1 (word-budget + MANDATORY/RECOMMENDED/DIFFERENTIATOR), competitor-seo-gap-analysis v1.1 (marketplace intel VN), keyword-topic-url-mapping v1.1 + topical-map-creation v2.1 (route serp-clustering). Manifest + sync + twin đã chạy (68 .claude / 31 SEO Production).
- Hệ checklist QC v3: 20 checklist mới trong wiki sop/06-self-checklist (registry trong README v3) + sop/10-offpage-process.md. Ma trận M §5.2 cập nhật cột Skill chính + Checklist QC cho 8 hàng WS.
- ⚠ Việc treo: knowledge pack 02-raw/knowledge/ của master CHƯA đóng gói các checklist mới (cần MIGRATION pass + _MANIFEST update trước khi setup client mới dùng được offline).
- Files touched: skills/ (7 folder), CLAUDE.md §5.2, log.md
- Công đoạn: — · WS: —

## [2026-07-22] refactor | v2026.07.1 — Nội quy 12 trạm + ORCHESTRATOR + COMMANDS + lớp mẫu examples — @claude
- 12 cặp CLAUDE.md+AGENTS.md per trạm (persona + vòng tự kiểm + nạp 80/20); ORCHESTRATOR.md (quản đốc) + COMMANDS.md (bảng lệnh); _TEMPLATES/examples/ 6 file mẫu hư cấu vidu.vn.
- Root: pre-work §3 bước 0b + §4.4 đọc nội quy trạm; MIGRATION/SYNC/README đồng bộ; thống nhất ID FB-<YYYY-MM-DD>.
- Files touched: 26 file trạm + 2 quản đốc + 6 examples + 6 file root.

## [2026-07-22] bookkeep | Nhận đợt mở rộng workspace 19-20/07 (phiên song song) — @claude
- Knowledge pack 06-self-checklist 8→30 file (bộ checklist lĩnh vực + sự kiện, KO/MR series); +11 skill mới, 4 skill cập nhật, mirror rebuild.
- ⚠ tier-1-outline-am.md bị đè bản FULL — chờ Vincent quyết chưng cất lại hay giữ; instance tạm giữ bản chưng cất.
- Files touched: 02-raw/knowledge/ + skills/ + .claude/skills/ + .agents/skills/

## [2026-07-22] refactor | v2026.07.2 — Chế độ TUẦN: skill gtv-weekly-report + template slide tuần — @claude
- Skill `gtv-weekly-report` (claude-only): fetch batchGet → digest → analyze theo rubric (pattern 4-8 tuần) → render deck 1920×1080 → check. Scripts: fetch_weekly_data.py · capture_sheet_range.py · pdf2png.swift.
- `_TEMPLATES/weekly-report-slides/` (12 exemplar client-neutral) + patch `09-reporting/CLAUDE.md` (mục Chế độ TUẦN + luật nạp + giới hạn runtime).
- Manifest: đăng ký skill + shared_exclude; sync 32 skill (2 claude-only không vào .agents); lint PASS.
- File PDF mẫu tuần W11 CareerViet (197MB) Vincent drop vào 09-reporting master → move về instance careerviet/09-reporting/samples/ (master client-neutral).
- Files touched: skills/gtv-weekly-report/**, _TEMPLATES/weekly-report-slides/**, 09-reporting/CLAUDE.md, MIGRATION.md, .claude/skills/gtv-weekly-report/**
- Công đoạn: — · WS: 09

## [2026-07-22] refactor | Vá skill gtv-weekly-report theo feedback SEO Lead CareerViet (scope system) — @claude
- slide-map.md: luồng phân tích chuẩn JL→Job Detail→Blog→Homepage, JL break 4 slide (Intent/ngành/khu vực/top pages), BẢNG 1 render đủ mọi dòng (+Blog còn lại dẫn xuất), SOW = "Plan Tuần" đủ task, không slide dashboard trùng Overview KPI; JL = Job Listing.
- analysis-rubric.md: nhận xét 4 lớp (số → phân rã driver → chẩn đoán theo ma trận tín hiệu PV/Clicks/Imp/CTR/Pos + độ chắc → action); khung Apply "vì sao tăng/giảm" nối PV/clicks landing per nhóm.
- fetch_weekly_data.py: parse tasklist theo tuần kế hoạch (marker "Tuần X/..."), digest sow_status.weeks; xử lý overview_wow_alt + plan_tuan_* + danh_gia_*.
- Nguồn: FB-2026-07-22-tranphong-01/02 (instance careerviet). Mirror sync + lint PASS.
- Files touched: skills/gtv-weekly-report/**, .claude/skills/gtv-weekly-report/**
- Công đoạn: — · WS: 09

## [2026-07-22] refactor | Round 2 feedback SEO Lead → pv_movers.py + 5 luật trình bày deck — @claude
- Script mới `scripts/pv_movers.py`: tải tab URL-level về CSV qua export URL (1 request, không tốn quota values) → lọc top page theo ΔPV (chuẩn team, clicks chỉ là cột phụ); resolve tab theo TÊN.
- slide-map: scope-note bảng top-page, cấm phân tích số tổng bảng scope 58K, Δ Pos bắt buộc 1.2/1.3, movers từ pv_movers, Blog chẩn đoán riêng + action nối content strategy SOW, slide Apply OVERVIEW theo page group trước Intent, 5 luật trình bày (đánh số slide, breadcrumb, 3 tăng/3 giảm + chẩn đoán mỗi chiều, chẩn đoán per nhóm BẢNG 1, action cụ thể).
- rubric: pattern "URL swap/redirect" + "Scope vênh". Template (+instance): CSS .crumb/.page-no/.scope-note.
- Files touched: skills/gtv-weekly-report/**, _TEMPLATES/weekly-report-slides/deck-template.html, .claude/skills/gtv-weekly-report/**
- Công đoạn: — · WS: 09

## [2026-07-22] refactor | Round 3 (Vincent): luật trình bày #7-11 + INLINE EDIT template + pv_movers dims — @claude
- Nguồn: FB-2026-07-22-vincent-01 (instance careerviet). slide-map +5 luật; template weekly-report-slides nhúng edit-mode (E/localStorage/guard nav) + Description 92px; pv_movers.py thêm cột phân loại; SKILL.md bước 2b (EDIT_KEY riêng per deck, ES5 Safari-safe).
- Mirror: 2 instance + root đã sync; lint PASS.
- Files touched: skills/gtv-weekly-report/**, _TEMPLATES/weekly-report-slides/deck-template.html, MIGRATION.md
- Công đoạn: — · WS: 09

## [2026-07-22] refactor | Round 4 + 4b Vincent → vá canonical gtv-weekly-report + template — @claude
- slide-map luật #12-15 (DECK CHROME có sẵn · action xuống dòng dạng ul · cấm chạm .data-meta + 3 slide mặc định tách cặp · bảng Blog đủ Clicks/Pos dẫn xuất); template weekly-report-slides: SCOPE căn giữa dọc + khối DECK CHROME (rail thumbnail/T · ▶ Present · #hash + hashchange · tự ẩn khi không rê chuột — không dính PDF export; ES5, test Playwright PASS Chromium + WebKit). MIGRATION.md addendum "Bổ sung 22/07 khuya". Mirror .claude/skills + 2 instance đã đồng bộ.
- Files touched: skills/gtv-weekly-report/references/slide-map.md · _TEMPLATES/weekly-report-slides/deck-template.html · MIGRATION.md · mirror .claude/skills/

## [2026-07-23] refactor | gtv-weekly-report v2: render bằng build_deck.py + content.yaml (80/20) — @claude
- Thêm scripts/build_deck.py + scripts/blog_groups.py + references/content-schema.md + _TEMPLATES/weekly-report-slides/deck-skeleton.html + WEEKLY-DATA-CHECKLIST.md (neutral); SKILL.md Pha 1 + Pha 3 viết lại; slide-map ghi chú «từ W12 render bằng builder». Nghiệm thu trên instance CareerViet: tái dựng W11 từ YAML tương đương bản tay.
- Files touched: skills/gtv-weekly-report/* · _TEMPLATES/weekly-report-slides/* · MIGRATION.md

## [2026-07-23] refactor | Skin chuẩn deck tuần = frontend-slides (v5) — @claude
- _TEMPLATES/weekly-report-slides/deck-skeleton.html đổi sang skin v5; bản cũ = deck-skeleton-classic.html; SKILL.md 2a + content-schema.md cập nhật. Nghiệm thu trên CareerViet W11 (v7 build 28/28, WebKit smoke PASS).
- Files touched: _TEMPLATES/weekly-report-slides/deck-skeleton*.html · skills/gtv-weekly-report/SKILL.md + references/content-schema.md · mirror

## [2026-07-23] refactor | gtv-weekly-report: đóng gói export-pdf.sh vào skill (standalone-ready) — @claude
- scripts/export-pdf.sh (copy từ frontend-slides) + SKILL.md sửa ghi chú standalone: instance clone chạy được export không cần workspace. Sync đủ mirror.
- Files touched: skills/gtv-weekly-report/scripts/export-pdf.sh · SKILL.md · mirror

## [2026-07-23] refactor | gtv-weekly-report: drive_folder_id + quy định Drive cho agency nhiều client — @claude
- fetch_weekly_data.py: Drive search khoanh theo report_tuan.drive_folder_id (share folder 1 lần → file kế thừa quyền) + warning khi trùng tên nhiều file; report-config-schema.md ghi field mới; _TEMPLATES WEEKLY-DATA-CHECKLIST.md thêm mục 0 quy định folder/tên file + phân nhánh SpySERP (ảnh manual) vs Looker (link unlisted). Sync đủ 6 mirror.
- Files touched: skills/gtv-weekly-report/scripts/fetch_weekly_data.py · references/report-config-schema.md · _TEMPLATES/weekly-report-slides/WEEKLY-DATA-CHECKLIST.md · MIGRATION.md · mirror

## [2026-07-23] refactor | gtv-weekly-report v2026.07.3 — 2 format TUẦN/THÁNG + rule carry-over + HTML-only — @claude
- SKILL.md: mục «Hai format deck» (tuần LEAN ~11 slide theo agenda catchup client / tháng ~26 slide + lớp MoM-OKRs-pattern); Pha 3: KHÔNG export PDF (HTML-only, PDF chỉ khi Vincent yêu cầu rõ).
- references/weekly-catchup-format.md (MỚI): map slide 2 format + RULE CARRY-OVER (task chưa done tự chuyển tuần kế «Chuyển tiếp», Vincent chốt 23/07).
- 09-reporting/CLAUDE.md (Chế độ TUẦN): cập nhật output HTML-only + 2 format + carry-over.
- Đồng bộ mirror .claude/skills/ (master + instance CareerViet). Chi tiết: MIGRATION.md v2026.07.3. Chưa commit git — chờ Vincent gọi.
- Files touched: skills/gtv-weekly-report/{SKILL.md, references/weekly-catchup-format.md}, 09-reporting/CLAUDE.md, MIGRATION.md, mirrors

## [2026-07-23] refactor | build_deck.py — bảng công việc 5 cột (Hạng mục/Task/PIC/Deadline/Tiến độ) — @claude
- render sow/next_week nhận rows {hangmuc, task, pic, deadline, status} → bảng 5 cột, Hạng mục gộp rowspan; fallback 2 cột cho deck cũ. Spec bổ sung vào references/weekly-catchup-format.md; đồng bộ đủ mirror master + CareerViet + MTM. MIGRATION v2026.07.3 đã cập nhật.
- Files touched: skills/gtv-weekly-report/{scripts/build_deck.py, references/weekly-catchup-format.md}, MIGRATION.md, mirrors

## [2026-07-24] refactor | Tương thích cây PROJECTS với Codex/Antigravity — @codex
- AGENTS root repo dùng cơ chế ancestor thay cho đường dẫn `../AGENTS.md` cố định; ghi đúng hai skill reporting chỉ có ở Claude Code. Workspace thêm routing PROJECTS và đưa hai instance đang hoạt động vào root sync/lint.
- Files touched: AGENTS.md · MIGRATION.md · ../PROJECTS/{AGENTS.md,CLAUDE.md} · ../skills/manifest.yaml · ../tools/{sync-agent-skills.rb,lint-agent-setup.rb}
- Công đoạn: — · WS: —

## [2026-07-27] refactor | visual-semantic-seo đạt chuẩn metadata đa runtime — @codex
- Sửa YAML frontmatter, description 829 ký tự và cô đọng reference routing; SKILL.md còn 483 dòng. Mirror Claude/Codex/Antigravity được dựng lại từ source.
- Files touched: skills/visual-semantic-seo/SKILL.md · MIGRATION.md · .claude/skills/visual-semantic-seo/ · .agents/skills/visual-semantic-seo/
- Công đoạn: — · WS: 04

## [2026-07-30] refactor | v2026.07.6 — gói bàn giao team (tooling standalone + deck hướng dẫn + doc fixes) — @claude
- tools/sync-skills.sh (bash, standalone sync mirror + parity check) + luật vào AGENTS.md; README sửa 20→32 skill + mục «Ngày đầu tiên»; _TEMPLATES/README.md mới; .gitignore thêm pattern file nặng; deck GTV_SEO-Production_huong-dan-cai-dat_v1.html (18 slide, QA PNG 18/18) đặt ở root.
- Chuẩn bị đóng zip phân phối qua Google Drive (quyết định Vincent 30/07). Chi tiết: MIGRATION.md v2026.07.6.
- Files touched: tools/, AGENTS.md, README.md, _TEMPLATES/README.md, .gitignore, GTV_SEO-Production_huong-dan-cai-dat_v1.html, MIGRATION.md

## [2026-07-30] bookkeep | Deck hướng dẫn ghi rõ 3 runtime + RECAP-HANDOFF cho review chéo — @claude
- Deck cài đặt: cover + slide 7 ghi đủ Claude Code / GPT Codex / Antigravity (trước chỉ ghi Codex). RECAP-HANDOFF-2026-07-30.md đặt tại Deliverables/GTV-SEO-Production-handoff/ — đề bài 7 mục cho Codex/Antigravity review chéo gói bàn giao.
- Files touched: GTV_SEO-Production_huong-dan-cai-dat_v1.html, log.md

## [2026-07-30] refactor | Vá findings review chéo Codex (M4-01, M4-02) + checklist template HTML-only — @claude
- Review chéo GPT Codex (đề bài mục 4 RECAP-HANDOFF) trả 4 findings CẦN-SỬA; 2 thuộc master: deck hướng dẫn trỏ path checklist tuần chỉ đúng cho gói CareerViet (master phải trỏ _TEMPLATES/weekly-report-slides/) + câu «Đọc BAN-GIAO-TEAM.md» chưa ghi rõ là file của gói CareerViet. Đã vá cả 2 trong deck (rebuild 18 slide, QA PNG slide 3 + 16 sạch).
- _TEMPLATES/weekly-report-slides/WEEKLY-DATA-CHECKLIST.md mục «AI tự lo»: bỏ «export PDF» → «tự chụp từng slide soi lỗi trình bày» (khớp luật HTML-only 23/07).
- Files touched: GTV_SEO-Production_huong-dan-cai-dat_v1.html, _TEMPLATES/weekly-report-slides/WEEKLY-DATA-CHECKLIST.md, MIGRATION.md, log.md

## [2026-08-05] refactor | v2026.08.1 — promote hệ báo cáo KỲ (tháng/quý) + OKRs quý lên master — @claude
- `skills/gtv-weekly-report/` 14 → 24 file: +8 script kỳ (fetch_period_data · period_analyze · bang1_parser · reconcile_totals · okrs_score · url_yoy_forensics · build_pptx · build_source_links) + 2 references (period-report-format · scripts-map) + SKILL.md/build_deck.py/export-pdf.sh bản mới. Nguồn: instance CareerViet (chạy thật W11-W13 + kỳ T7/Quý 1), đã kiểm tính client-neutral qua instance Minh Tuấn Mobile (e-commerce).
- `skills/gtv-project-okrs/` MỚI (3 file) — đối chiếu OKRs sheet team vs bản .md canonical, 6 lăng kính review, script chỉ đọc sheet. Master 32 → 33 skill.
- Neutral hóa khi promote: rename `joblisting_yoy_forensics.py` → `url_yoy_forensics.py` (+ cross-ref SKILL.md/scripts-map/period-report-format/docstring); `okrs_score.py` lấy tên client từ config; `build_pptx.py` header "Người quyết (khách)"; `okrs_sheet_diff.py` bỏ default CRV-shaped → `--range-key`/`--workbook` required.
- `_TEMPLATES/weekly-report-slides/`: +PERIOD-DATA-CHECKLIST.md, +RUNBOOK-bao-cao-ky.md, WEEKLY-DATA-CHECKLIST.md thêm §5 «Kích hoạt hệ» (9 việc setup 1 lần). `_TEMPLATES/BAN-GIAO-TEAM.md` MỚI (template cấp root, client-neutral). `_TEMPLATES/README.md` cập nhật index.
- MIGRATION.md: mục v2026.08.1 + bảng 2.A thêm nhóm `tools/`.
- Files touched: skills/gtv-weekly-report/** (24), skills/gtv-project-okrs/** (3), _TEMPLATES/{BAN-GIAO-TEAM.md,README.md,weekly-report-slides/{PERIOD-DATA-CHECKLIST.md,RUNBOOK-bao-cao-ky.md,WEEKLY-DATA-CHECKLIST.md}}, MIGRATION.md, log.md, .claude/skills/** + .agents/skills/** (regen)

## [2026-08-15] refactor | v2026.08.2 — Nguyên tắc giao tiếp nền nhúng vào AGENT.md (mục 0) — @claude
- AGENT.md thêm mục 0 bản nhúng luật giao tiếp + chất lượng cấp workspace (chat ngắn gọn / deliverable completeness > brevity) để repo standalone tự chứa.
- Áp thẳng cùng file cho 2 instance careerviet + minh-tuan-mobile (1 file, không đổi master_version).
- Files touched: AGENT.md, MIGRATION.md, log.md

## [2026-08-29] refactor | v2026.08.3 — tích hợp wp-publish-workflow-kit + policy `<strong>` + SOP 11 đăng bài WP — @claude
- Phân tích repo team `github.com/LongDZ1204/wp-publish-workflow-kit` (66 file) + đối chiếu wiki Semantic SEO A-Z. Quyết định Vincent: content team dừng ở Google Doc; khâu đăng/sửa WordPress thuộc WS06 (bạn SEO); policy bold = `<strong>`, `<b>` = 0; kit giữ repo riêng, không vendor.
- Policy `<strong>`: vá P14 ở kho gốc wiki + pack `02-raw/knowledge/sop/08-onpage-checklist.md` + `skills/seo-onpage/references/p-series-checklist.md`; mục Policy GTV mới trong wiki [[Semantic Emphasis]]. Khi đăng WP: KHÔNG chạy bước strong-to-b của kit.
- SOP MỚI `02-raw/knowledge/sop/11-publish-wp.md` (sync từ kho gốc, copy nguyên): 2 flow input (Google Doc link trong Sheet đăng bài 11 cột / SEO kiêm content đăng thẳng), gate pre-publish, verify kép WP+Sheet, giới hạn kit + cách bù. Đăng ký: `_MANIFEST.md` hàng 18 + `knowledge/README.md` ma trận WS06.
- CLAUDE.md root: §5.2 hàng WS06 (+ kit + sop/11 + done-criteria verify kép) · §5.4 (chốt khâu đăng web thuộc WS06) · §11 (+ interface kit, dùng được standalone). Trạm 06: README + CLAUDE.md (persona publish, ĐƯỢC/KHÔNG ĐƯỢC, luật nạp).
- Upgrade spec gửi team kit (4 nhóm A-D: policy strong + slugify tiếng Việt · enforce width/height + lazy + tier ảnh + ngưỡng meta · approval hash AUDIT + so modified + backup immutable + env guard + drop-block cảnh báo · hooks tích hợp internal-linking/image-seo-optimize): `06-onpage-internal-link/WP-PUBLISH-KIT_upgrade-spec_v1.md`.
- Mirror skills đồng bộ bằng `tools/sync-skills.sh` (34/34, parity 0 lệch).
- Files touched: CLAUDE.md, 02-raw/knowledge/{sop/08-onpage-checklist.md,sop/11-publish-wp.md,_MANIFEST.md,README.md}, 06-onpage-internal-link/{README.md,CLAUDE.md,WP-PUBLISH-KIT_upgrade-spec_v1.md}, skills/seo-onpage/references/p-series-checklist.md (+2 mirror), MIGRATION.md, log.md · kho gốc wiki: Semantic Emphasis.md, sop/08, sop/11 (mới), index.md, log.md
- Công đoạn: — (infra master) · WS: 06

## [2026-08-29] setup | Gom đợt setup máy standalone 28/08 lên master + push GitHub — @claude
- Commit phần dang dở từ 28/08: `_SETUP/` (doctor + credential per-user + hướng dẫn Drive), BOOTSTRAP trong CLAUDE.md, `requirements.txt`, skill `setup-may`, `_cred.py` cho script sheet, GEO G0-G5 trong §5.1/§5.2, mirror skills. Soát secret: không có key trong tree; `config/local.yaml` đã gitignore.
- Push `origin/main` → github.com/GTV-SEO-Agency/seo-production (v2026.08.3).
- Files touched: MIGRATION.md, log.md + toàn bộ file đợt 28/08

## [2026-09-02] refactor | v2026.09.1 — vá chuỗi GEO v2 (lop-geo-v2 đóng gói, AX1-AX7), gate GEO vào ORCHESTRATOR/index, 3 template mới (entity-plan, escalation-note, report-config.example), lớp business kick-off/handover — @claude
- Nguồn: audit tổng thể workspace 02/09 (Vincent yêu cầu chủ động improve SEO/BD/Account Production theo wiki Business + Semantic SEO).
- Pages touched: CLAUDE.md §5.2/§6.2 · ORCHESTRATOR.md §3/§7 · index.md (#13/14/21/28, luật 3, bảng C) · MIGRATION.md · README 03/06/08/09/11 · 09-reporting/CLAUDE.md · _TEMPLATES/{kick-off, handover-checklist, content-plan-matrix, README} · 02-raw/knowledge/{_MANIFEST, sop/08, sop/09-timeline/lop-geo-v2 (MỚI), sop/02, common-ai-errors} · path lop-geo-v2 trong skills + 2 mirror + .claude/agents.
- Chi tiết: MIGRATION.md mục v2026.09.1. Chưa làm: distill lesson hồi tố (0 lesson ở 12-feedback-lessons).

## [2026-09-02] refactor | v2026.09.2 — trạm-first: router §0.5, ORCHESTRATOR tùy chọn, sub-agent opt-in, `_REFERENCE/`, standalone — @claude
- CLAUDE.md 463 → 347 dòng (router §0.5, §11 standalone, §13 anti-pattern mới); 5 file `_REFERENCE/`; ORCHESTRATOR header/§4/§5.1; ws08-geo description + tools; `.claude/settings.json`; COMMANDS.md tách làm/chạy trọn; README mô tả ORCHESTRATOR; AGENT.md bản nhúng v2026-09-02. Ma trận M, Pre-work, mốc cứng, QC không đổi nội dung.
- Files touched: CLAUDE.md, _REFERENCE/*.md (5), ORCHESTRATOR.md, .claude/agents/ws08-geo.md, .claude/settings.json, COMMANDS.md, README.md, AGENT.md, MIGRATION.md
- Công đoạn: — · WS: root

## [2026-09-02] refactor | Standalone sweep (v2026.09.2 bổ sung) — @claude
- 40 file infra (12 nội quy trạm 0X/CLAUDE.md, skills, cheat-sheet, SETUP.md, CLAUDE.md) — đường dẫn tới wiki/kho nội bộ ngoài repo đổi thành mô tả «tài liệu nội bộ … (ngoài repo, hỏi Lead/Vincent)»; SETUP.md bảng chế độ: "Máy master của Vincent". Đã đè sang 2 instance PROJECTS (careerviet, minh-tuan-mobile) trong đợt migration cùng ngày.
- Files touched: 0X-*/CLAUDE.md, skills/*/SKILL.md, 02-raw/knowledge/cheat-sheets/*.md, SETUP.md, CLAUDE.md
- Công đoạn: — · WS: root

## [2026-09-05] refactor | Runtime adapter và nguồn luật
- Sửa entry đúng scope; adapter trỏ luật cục bộ. SEO/CareerViet/Minh Tuan Mobile dời nguyên văn mục tra cứu sang _REFERENCE/runtime-*.md; giữ gate và đường dẫn tính từ root.
- Files touched: AGENTS.md, AGENT.md khi có sửa, CLAUDE.md khi có tách, .agents/rules/runtime-entry.md, _REFERENCE/runtime-*.md.

## [2026-09-05] refactor | Persona sinh từ nguồn và runtime quickstart
- AGENT.md có block/hash sinh từ root, giữ nguyên phần cục bộ. README.md có bảng bắt đầu theo runtime. Content thêm proof contract cho claim-verifier; Account thêm snapshot contract cho report, không đổi nguồn nghiệm thu.
- Files touched: AGENT.md, README.md; skills/claim-verifier hoặc skills/gtv-client-report khi có.

## [2026-09-12] refactor | Standalone skill dependencies — Vincent duyệt

- Backlink output trong instance; sửa pointer informational-analysis; kickoff phân biệt chuẩn bị/setup. Audit có đủ bộ 60 rules; schema report trỏ sample giả lập nội repo, giữ runtime Claude-only của report.
- Source trong skills/; mirror sinh từ canonical đúng repo. Kiểm dependency/retention/mirror và fixture builder; Content chạy contracts, tests và lessons lint. Ca live model chưa chạy.
- Files touched: `skills/acc-kickoff-setup/SKILL.md`, `skills/acc-kickoff-setup/evals/cases.yaml`, `skills/backlink-research/SKILL.md`, `skills/backlink-research/evals/cases.yaml`, `skills/competitor-seo-gap-analysis/SKILL.md`, `skills/gtv-weekly-report/references/content-sample.yaml`, `skills/gtv-weekly-report/references/content-schema.md`, `skills/semantic-content-audit/SKILL.md`, `skills/semantic-content-audit/evals/cases.yaml`, `skills/semantic-content-audit/references/45-semantic-writing-rules.md`; các runtime mirror được phép, `MIGRATION.md`, `log.md`.

## [2026-09-28] skill-update | Fact-fix dẫn patent cho website function (seo-onpage 1.4.1, visual-semantic-seo 3.0.1) — Vincent duyệt

- seo-onpage P22: bỏ "broken function = negative signal — patent US10565267B1, interaction weight cao"; giữ yêu cầu CTA/form/filter hoạt động như tiêu chuẩn UX và chuyển đổi. US10565267B1 là patent xếp hạng bài đăng mạng xã hội.
- visual-semantic-seo: 2 reference bỏ dẫn US10565267B1, US8868565B1, US20150234930A1 làm căn cứ website function; bảng 1x/5x/10x thành mức ưu tiên kiểm nội bộ; SKILL.md bỏ dẫn US7716225B1 cho "broken function".
- Nguồn đối chiếu: `Knowledge/Google Leak Decoded` (toàn văn patent). Mirror `.claude/skills/`, `.agents/skills/` chỉ đồng bộ 2 skill này (repo đang có thay đổi chưa commit ở mirror khác).
- Còn lại: xlsx `Deliverables/Admin/Checklist_Onpage_Semantic_SEO - v5.4.xlsx` ô D33 vẫn ghi claim cũ; skill ghi xlsx là bản gốc khi lệch, chờ Vincent sửa.
- Files touched: `skills/seo-onpage/SKILL.md`, `skills/seo-onpage/references/p-series-checklist.md`, `skills/visual-semantic-seo/SKILL.md`, `skills/visual-semantic-seo/CHANGELOG.md`, `skills/visual-semantic-seo/references/website-function-seo.md`, `skills/visual-semantic-seo/references/ecommerce-website-functions.md` (+ mirror)

## [2026-09-28] refactor | Knowledge pack: quy định về tăng CTR theo leak Google (V61) — Vincent duyệt — @claude

- Re-sync từ kho gốc: `sop/10-offpage-process.md` (v1.1, §4 thêm mục "Tín hiệu người dùng (click)") và `sop/06-self-checklist/tier-1-traffic-users.md` (thêm Phụ lục B: 5 hình thức không dùng, 3 lý do theo leak, câu trả lời mẫu cho Account).
- Dòng Traffic users ⚠ giữ nguyên trong khung công đoạn và `index.md`: vẫn optional, chỉ chuyển `todo` khi SEO Director duyệt bằng văn bản. Click bot, trình giả lập, proxy, gói click không rõ nguồn bị cấm trong mọi dự án khách.
- `MIGRATION.md` thêm mục v2026.09.5 (gộp cả fact-fix 2 skill cùng ngày); `_MANIFEST.md` cập nhật ngày sync hàng 30 và 38. Chưa commit, chưa tag git. Instance (`PROJECTS/`) chưa nhận bản vá.
- Files touched: `02-raw/knowledge/sop/10-offpage-process.md`, `02-raw/knowledge/sop/06-self-checklist/tier-1-traffic-users.md`, `02-raw/knowledge/_MANIFEST.md`, `MIGRATION.md`
- Công đoạn: dòng Traffic users (T8 → T9) · WS: 07


## [2026-10-01] work | v2026.10.1 — đọc Kho tri thức khách (KB) từ fork content — @claude
- Vincent duyệt kế hoạch KB 01/10 (bản gốc KB ở fork Content `00-context/kb/`, SEO lấy snapshot). `tools/content_sync.py` thêm `--pull-kb` → `00-client-context/kb-snapshot/<ngày>/` (thử trên instance + fork giả trong scratchpad: snapshot đúng, checksum fork không đổi, lần 2 từ chối ghi đè).
- Luật trạm thêm 1–2 dòng: root `CLAUDE.md` §11, `00-client-context`, `05-content-plan`, `14-entity` (luật 8), `06-onpage-internal-link`, `07-offpage`, `08-geo-ai-visibility`. `MIGRATION.md` mục v2026.10.1. Chưa commit, chưa tag, chưa migrate instance.
- Files touched: `tools/content_sync.py`, `CLAUDE.md`, `00-client-context/CLAUDE.md`, `05-content-plan/CLAUDE.md`, `14-entity/CLAUDE.md`, `06-onpage-internal-link/CLAUDE.md`, `07-offpage/CLAUDE.md`, `08-geo-ai-visibility/CLAUDE.md`, `MIGRATION.md`

## [2026-10-01] work | đồng bộ nguồn sự thật với repo content qua GitHub (bổ sung v2026.10.1) — @claude
- Vincent chốt 01/10: giữ 2 repo mỗi khách, kéo chéo qua GitHub, mỗi loại dữ liệu một repo chủ. Mới: `tools/project_sync.py`, `_REFERENCE/project-sync.md`, `_TEMPLATES/project-sync.yaml`. Sửa: `CLAUDE.md` §11, `SETUP.md` bước 7, `COMMANDS.md`, `AGENTS.md` (mục mới cho mọi runtime), `.gitignore` (`.peer/`), `MIGRATION.md`.
- Kiểm: chạy thật với `GTV-SEO-Agency/content-production-minh-tuan-mobile` trong scratchpad (content-status 5 bài, delivered 1 bài; KB bỏ qua vì repo content chưa có KB), lần 2 cùng ngày từ chối ghi đè snapshot. Chưa commit, chưa migrate instance.
- Files touched: `tools/project_sync.py`, `_REFERENCE/project-sync.md`, `_TEMPLATES/project-sync.yaml`, `CLAUDE.md`, `SETUP.md`, `COMMANDS.md`, `AGENTS.md`, `.gitignore`, `MIGRATION.md`

## [2026-10-02] refactor | Knowledge pack: SOP 12 mô hình backlink stack + SOP 10 v1.2 — Vincent duyệt — @claude

- Re-sync từ kho gốc: `sop/10-offpage-process.md` (v1.2), `sop/06-self-checklist/tier-1-offpage-backlink.md` (OF-05, OF-08). File mới: `sop/12-backlink-stack-models.md` (v1.0, mức bản đội SEO).
- Nguồn: training nội bộ "Bí thuật backlink thất truyền" bản 6. Người duyệt mọi phương án grey hat và black hat: SEO Lead xem trước, SEO Director chốt.
- Chưa nối SOP 12 vào ma trận nạp, khung công đoạn và `index.md`; chờ Vincent cập nhật quy trình 10 tháng. Skill `backlink-plan` chưa sửa.
- `MIGRATION.md` thêm mục v2026.10.2; `_MANIFEST.md` cập nhật hàng 29, 38, thêm hàng 41. Chưa commit, chưa tag git. Instance (`PROJECTS/`) chưa nhận bản vá.
- Files touched: `02-raw/knowledge/sop/10-offpage-process.md`, `02-raw/knowledge/sop/12-backlink-stack-models.md`, `02-raw/knowledge/sop/06-self-checklist/tier-1-offpage-backlink.md`, `02-raw/knowledge/_MANIFEST.md`, `MIGRATION.md`
- Công đoạn: 20, 25◇, 26 · WS: 07

## [2026-10-02] skill-update | backlink-plan 1.2: PBN, parasite làm được cho khách khi được duyệt — Vincent duyệt — @claude

- `skills/backlink-plan/SKILL.md` 1.1 → 1.2 theo canonical root: mức Aggressive do SEO Lead xem trước, SEO Director chốt; luật tầng cho PBN, parasite, link rẻ số lượng lớn; bỏ câu "GTV không làm cho khách". Chép tay 3 nơi (skills, .claude/skills, .agents/skills), không chạy sync toàn bộ.
- Checklist `tier-1-offpage-backlink.md` re-sync lần 2 trong ngày (OF-08 khớp câu chữ skill). `MIGRATION.md` mục v2026.10.2 bổ sung dòng Skill.
- Files touched: `skills/backlink-plan/SKILL.md` (+ 2 mirror), `02-raw/knowledge/sop/06-self-checklist/tier-1-offpage-backlink.md`, `MIGRATION.md`
- Công đoạn: 25◇, 26 · WS: 07

## [2026-10-02] refactor | Knowledge pack: thang điểm T.T.T 35/35/30 + SOP 12 v1.1 — Vincent duyệt — @claude

- Re-sync lần 3 trong ngày: `sop/12-backlink-stack-models.md` (v1.1), `sop/10-offpage-process.md` (§1.6), `sop/06-self-checklist/tier-1-offpage-backlink.md` (OF-05).
- Nội dung: thang điểm chấm nguồn link là Theme 35, Traffic 35, Trust 30 trên tổng 100; chốt cách ghi các điểm Google không công bố (thừa hưởng trust của nền tảng, link giữa subdomain cùng nền, seed nhóm trust rank cao nhất, keyword trong subdomain và URL, giới hạn 200 anchor của sitewide).
- Thuộc mục v2026.10.2 của `MIGRATION.md`, không tăng version. Chưa commit; instance chưa nhận.
- Files touched: 3 file knowledge pack trên
- Công đoạn: 20, 25◇, 26 · WS: 07


## [2026-10-02] refactor | v2026.10.3 — Onpage: MX nâng cấp định dạng (chấm riêng) + batch report dạng bảng nhiệt HTML — Vincent duyệt — @claude

- Vì sao: sop/08 chỉ xét ảnh ở P19–P20 và nhắc calculator ở T3-P1; không có mục nào xét sơ đồ, bảng, video, khối tương tác cho trang đã có. Batch report 20 URL × 23 item khó đọc ở dạng bảng chữ.
- Mới: mục "Nâng cấp định dạng (MX)" trong `06-onpage-internal-link/CLAUDE.md` (MX1–MX6, chấm riêng, không tính /23 · /31 · /39, không phải gate); mục 7 của `_TEMPLATES/onpage-batch.md`; `tools/onpage_report_html.py`.
- Sửa theo: `06-onpage-internal-link/README.md`, `COMMANDS.md`, `_REFERENCE/runtime-workstream-matrix.md`, `.gitignore` (`*.view.html`), `MIGRATION.md` (v2026.10.3, bảng GHI ĐÈ hàng Tooling).
- Không đổi knowledge pack (`02-raw/knowledge/` giữ nguyên).
- Files touched: như trên
- Công đoạn: 7(execute), 18, 23 · WS: 06

## [2026-10-03] refactor | v2026.10.4 — Instance website nội bộ (GTV, TAG): dòng Entity + biến thể setup — Vincent duyệt — @claude

- Vì sao: Vincent mở instance cho website gtvseo.com và theaigrowth.io; luật entity cũ cấm nhãn TAG trong mọi instance, và bản thay đổi chỉ ở instance sẽ bị migration ghi đè.
- Mới: dòng `Entity` ở bảng A `index.md`; `SETUP.md` mục 1.1; ngoại lệ entity ở `CLAUDE.md` §1 và hàng cấm số 4 của `10-client-management/CLAUDE.md`.
- Gắn tag `v2026.10.3` cho commit 5d303a9 (master thiếu tag từ v2026.08.1).
- Files touched: CLAUDE.md, 10-client-management/CLAUDE.md, index.md, SETUP.md, MIGRATION.md, log.md
- Công đoạn: — · WS: —

## [2026-10-12] refactor | v2026.10.5 — Skill query-processing-diagnosis (chẩn đoán QP bộ keyword cam kết) — Vincent duyệt — @claude

- Vì sao: đóng gói quy trình đợt chẩn đoán 10 dự án GTV (10/2026) để team chạy lại ở gate #22, audit #24, #29 mà không phụ thuộc workspace GTV, và bàn giao kết quả cho team content.
- Mới: `skills/query-processing-diagnosis` v1.2 (SKILL.md quy trình chuẩn 8 pha có ngân sách tool call, 5 reference, 7 script + assets, fixture `examples/`, `evals/` 10 ca hành vi + 54 test offline), `03-audits/ranking/README.md` (hướng dẫn Lead), `_TEMPLATES/qp-intake.md`, `_TEMPLATES/qp-chan-doan.md`.
- Tối ưu so với đợt 10/2026 (11–32 script riêng mỗi dự án, hàng trăm tool call): `qp_ranks.py` (bo, runs, table, terms), `qp_scaffold.py` điền sẵn số, `qp_build.py` verify số trên deck với bảng hạng, quét chữ dễ lộ điều khoản trên bản web, sinh file bàn giao content và bảng con số → nguồn.
- Sửa theo review nội bộ 12/10: mốc so sánh rỗng không còn tạo "Đang lan" giả (table dừng mã 2, có `--no-compare`); project một domain có lần chạy mới nghi thiếu thì dừng hỏi Lead (mã 3); đọc CSV dấu phẩy, gộp nhiều trang export, đọc cột Volume, `--targets` đếm keyword lệch URL kế hoạch; pha A đọc AGENT.md, nội quy trạm, cheat-sheet; nội quy trạm `03-audits/CLAUDE.md` thêm chẩn đoán QP; bỏ dữ liệu khách khỏi skill (ca eval ẩn danh, demo của deck training trong `assets/base.js`).
- Kiểm: 54 test offline PASS; chạy lại export thật của hai dự án (nhiều domain và một domain) ra đúng số đã đối chiếu tay; `qp_render.py check` OK cả 11 JSON đợt 10/2026; audit 0 slide tràn.
- Files touched: skills/query-processing-diagnosis/, 03-audits/ranking/README.md, 03-audits/README.md, 03-audits/CLAUDE.md, _TEMPLATES/qp-intake.md, _TEMPLATES/qp-chan-doan.md, _TEMPLATES/README.md, CLAUDE.md, README.md, COMMANDS.md, MIGRATION.md, _REFERENCE/runtime-workstream-matrix.md, _REFERENCE/folder-map.md, _REFERENCE/project-sync.md, 02-raw/knowledge/cheat-sheets/ws03-audit.md, log.md
- Công đoạn: 22, 24, 29 · WS: 03

## [2026-10-13] refactor | v2026.10.6 — Gate QA link trước khi đăng (SOP 10 v1.3) + textlink-analyzer v1.1.0 — Vincent duyệt — @claude

- Vì sao: Vincent duyệt 13/10/2026 sau đợt ingest Clippings 10/2026 (wiki Semantic SEO, nguồn Dejan Petrovic 2026): link đặt sai chỗ người đọc cần dễ bị đoán là link mua và có thể bị Google bỏ qua không báo.
- SOP 10 v1.3: §2 luật handoff 6, gate 6 bước cho link đặt trong thân bài. Bản canonical ở `Knowledge/Semantic SEO A - Z/sop/10-offpage-process.md`, chép nguyên sang master.
- `skills/textlink-analyzer` v1.1.0: Bước 5b chấm gate, 2 cột mới trong bảng plan; mirror sinh lại bằng `tools/sync-agent-skills.rb` ở root workspace; lint drift runtime 0.
- Files touched: 02-raw/knowledge/sop/10-offpage-process.md, skills/textlink-analyzer/SKILL.md, .claude/skills/textlink-analyzer/, .agents/skills/textlink-analyzer/, MIGRATION.md, log.md
- Công đoạn: offpage · WS: 07

## [2026-10-17] refactor | v2026.10.7 — Bộ skill WordPress có quyền server + nhánh GSC API — Vincent duyệt — @claude

- Vì sao: Vincent duyệt 17/10/2026: đưa quy trình tốc độ, bảo mật, ghi nội dung qua trang duyệt đã chạy thật trên 2 site WordPress vào master, viết chung cho mọi dự án có quyền vào server; thông tin riêng của site nằm trong `00-client-context/wp-server.md` của instance.
- Skill mới `wp-pagespeed`, `wp-security-hardening`, `wp-content-review-apply` (claude-only); sửa `technical-seo-audit` v1.7, `seo-onpage` v1.4.2, `internal-linking` v1.1.1. Bản gốc của 3 skill mới chuyển vào repo này; workspace Vincent đọc qua `source` trong manifest.
- Tool mới `tools/ai-assist/`, `tools/gsc/gsc.sh`; template mới `_TEMPLATES/wp-server.md`.
- Files touched: skills/wp-pagespeed/, skills/wp-security-hardening/, skills/wp-content-review-apply/, skills/technical-seo-audit/, skills/seo-onpage/SKILL.md, skills/internal-linking/SKILL.md, .claude/skills/, .agents/skills/, tools/ai-assist/, tools/gsc/, tools/sync-skills.sh, _TEMPLATES/wp-server.md, _TEMPLATES/README.md, CLAUDE.md, README.md, COMMANDS.md, SYNC.md, _REFERENCE/runtime-workstream-matrix.md, _REFERENCE/folder-map.md, 03-audits/technical/README.md, MIGRATION.md, log.md
- Công đoạn: 5, 7, 18, 23, 24, 27 · WS: 03, 06

## [2026-10-18] refactor | v2026.10.8 — Bài học nghiệm thu tốc độ và đổi theme site WordPress thứ hai — Vincent duyệt — @claude

- Vì sao: Vincent duyệt 18/10/2026 ("tự quyết và tự nâng cấp"): đưa bài học từ đợt đổi theme, đưa trang tĩnh vào WordPress, đổi tên ảnh, nghiệm thu PSI vào master, viết client-neutral.
- `wp-pagespeed` v1.2 (lớp 4 font, lớp 7 tracking, A/B trên PSI, 3 script mới đã chạy thử trên production site mẫu); `image-seo-optimize` v1.2 (Mode D, script cách ly đã chạy thử cách ly và trả lại trên server); `site-migration-checklist` v1.1; `schema-markup-generator` v1.0.2. Mirror sinh lại bằng `tools/sync-agent-skills.rb` ở root workspace.
- Files touched: skills/wp-pagespeed/, skills/image-seo-optimize/, skills/site-migration-checklist/, skills/schema-markup-generator/, .claude/skills/, .agents/skills/, MIGRATION.md, log.md
- Công đoạn: 5, 7, 18, 23, 24 · WS: 03, 06

## [2026-10-18] refactor | v2026.10.9 — Vị trí internal link: đúng ngữ cảnh, ưu tiên supplementary content, bám topical map — Vincent yêu cầu — @claude

- Vì sao: Vincent yêu cầu 18/10/2026: link chỉ đặt ở đúng ngữ cảnh, ưu tiên supplementary content, main content chỉ khi thật sự cần, bám topical map và topic cluster; bổ sung vào skill internal link và luật trạm, dò bằng Jev.
- `internal-linking` v1.2 (`references/link-placement.md`, Bước 4b, 2 cột mới trong link plan); rubric Jev `link-placement` (hiệu chuẩn 115 link: `zone` từ 0,7 khớp 80/82); luật trạm 06. Mirror sinh lại bằng `tools/sync-agent-skills.rb` ở root workspace.
- Files touched: skills/internal-linking/, .claude/skills/internal-linking/, .agents/skills/internal-linking/, tools/ai-assist/tasks/link-placement.json, tools/ai-assist/README.md, 06-onpage-internal-link/CLAUDE.md, MIGRATION.md, log.md
- Công đoạn: 18 · WS: 06

## [2026-10-18] refactor | v2026.10.10 — wp-pagespeed v1.3, wp-security-hardening v1.2 — Vincent duyệt "làm full", cho tự nâng cấp skill — @claude

- Bài học đợt tốc độ thứ hai và siết server của một site WordPress sau khi đổi theme: font dự phòng trên máy đo PSI và Android, unicode-range, content-visibility, srcset ảnh màn hình đầu, forced reflow; chặn mu-plugins, HSTS, bind MariaDB, backup tự động xoay vòng không xoá file.
- Files touched: skills/wp-pagespeed/, skills/wp-security-hardening/ (thêm templates/backup-tu-dong/), .claude/skills/, .agents/skills/, MIGRATION.md, log.md

## [2026-10-18] refactor | v2026.10.11 — wp-pagespeed v1.4, wp-security-hardening v1.3, site-migration-checklist v1.2 — Vincent yêu cầu cập nhật skill từ phiên — @claude

- Bài học lượt nghiệm thu đợt 2 của một site WordPress sau khi đổi theme: lượt PSI chậm dồn vào một URL phải đo lại, mốc so cùng buổi; tắt plugin chấm sao hết chức năng (backup `active_plugins`, grep dấu plugin, error log); cách ly theme cũ sau khi ổn định; công cụ chép file theme lẻ và lịch launchd kéo backup.
- Files touched: skills/wp-pagespeed/ (thêm scripts/deploy_theme_files.sh), skills/wp-security-hardening/ (thêm templates/backup-tu-dong/cai-lich-pull-mac.command), skills/site-migration-checklist/, .claude/skills/, .agents/skills/, MIGRATION.md, log.md

## [2026-10-18] refactor | v2026.10.12 — wp-pagespeed v1.5: hoãn GTM có hẹn giờ, hạng mục Agentic Browsing — Vincent yêu cầu tối đa TBT và Agentic — @claude

- A/B 48 lượt PSI: hoãn GTM 2 s vẫn bị tính TBT, 4 s cho TBT = 0 ở 12/12 lượt; mốc chọn theo observedTraceEnd − observedLoad + biên. Hạng mục Agentic: aria-label nút icon, llms.txt tĩnh có charset, axe với content-visibility.
- Files touched: skills/wp-pagespeed/ (thêm references/agentic-browsing.md, psi_run.py --categories), .claude/skills/, .agents/skills/, MIGRATION.md, log.md

## [2026-10-18] refactor | v2026.10.13 — wp-pagespeed v1.6, wp-security-hardening v1.4, geo-content-optimization v1.3.1, technical-seo-audit v1.7.1, cro-measurement-plan v1.2 — Vincent: trang khoá học và blog chưa tối ưu xong, cho tự cập nhật skill — @claude

- Bài học đợt đo đủ trang con của một site WordPress: CLS 0,92 do JS defer đổi bố cục sau lần vẽ đầu (sửa bằng trạng thái trong <head>, đo từng nhánh dữ liệu), stack font thiếu face dự phòng (Mac 0,03, PSI 0,28), bản 720w cho hero, logo dải chạy ngang, sizes ảnh thân bài, ảnh đại diện PNG sang WebP giữ OG, forced reflow bằng ResizeObserver, TBT trang chuyển đổi đến từ tracking. Ngoại lệ /llms.txt cho audit PSI. Kiểm GTM bị hoãn trong kế hoạch đo.
- Files touched: skills/wp-pagespeed/ (thêm scripts/cls_trace.mjs, scripts/featured_webp.sh), skills/wp-security-hardening/, skills/geo-content-optimization/, skills/technical-seo-audit/, skills/cro-measurement-plan/, .claude/skills/, .agents/skills/, MIGRATION.md, log.md

## [2026-10-18] refactor | v2026.10.14 — wp-pagespeed v1.7, site-migration-checklist v1.3 — kết quả A/B font trên PSI, plugin còn bật sau đổi theme — @claude
- wp-pagespeed: psi_ab.py gộp spec; do-dac.md và checklist lớp 4 ghi kết quả A/B font.
- site-migration-checklist: so plugin staging với production, kiểm plugin front-end bằng DOM, quét `<style>` và ảnh hotlink trong nội dung cũ.
- Files touched: skills/wp-pagespeed/{SKILL.md,scripts/psi_ab.py,references/do-dac.md,references/checklist-theo-lop.md}, skills/site-migration-checklist/{SKILL.md,references/wp-tu-quan.md}, MIGRATION.md

## [2026-10-19] refactor | v2026.10.15 — wp-pagespeed v1.8 — CLS do critical CSS thiếu font và mục lục chờ JS — @claude
- wp-pagespeed: lớp 5 thêm bẫy LiteSpeed gom `<style>` có `@font-face` vào file async và luật dựng lại critical CSS sau khi đổi font; lớp 6 thêm mục lục Fixed TOC chờ JS và cách thử CSS bằng CDP `Fetch`.
- Files touched: skills/wp-pagespeed/{SKILL.md,references/checklist-theo-lop.md}, MIGRATION.md

## [2026-10-19] refactor | v2026.10.16 — lớp model cho SEO: 4 skill mới + glm.py — @claude
- Skill mới: site-vector-index, model-calibration, geo-answer-lab, retrieval-lab (v1.0, mỗi skill có test offline).
- Tool mới: tools/ai-assist/glm.py. calibration-defaults.json thêm cổng ai-answer-brand v3. .gitignore thêm 03-audits/_vector-index/.
- Files touched: skills/{site-vector-index,model-calibration,geo-answer-lab,retrieval-lab}/, tools/ai-assist/{glm.py,calibration-defaults.json}, .gitignore, .claude/skills/, .agents/skills/, MIGRATION.md, CLAUDE.md, README.md, log.md

## [2026-10-19] refactor | knowledge pack tier-1-geo GE-26 — AI nghi ngờ vì brand tự xếp hạng — @claude
- Vincent chốt 19/10: không gỡ bài top list; viết khách quan + EEAT; giải nghi ngờ bằng offsite consensus GE-28…32. Vá theo kho gốc v2.0.4, chỉ dòng GE-26 và 1 dòng anti-pattern.
- Files touched: 02-raw/knowledge/sop/06-self-checklist/tier-1-geo.md, 02-raw/knowledge/_MANIFEST.md, MIGRATION.md, log.md

## [2026-10-19] refactor | v2026.10.17 — topical-focus, content-quality-lab, model-calibration v1.2 — @claude
- Skill mới: topical-focus (map, selftest, plan), content-quality-lab (prepare, validate, report, template), mỗi skill có test offline.
- model-calibration v1.2: proxy --control, chế độ auc, lưới cosine 0,01. calibration-defaults.json thêm cổng content-effort.
- Files touched: skills/{topical-focus,content-quality-lab,model-calibration}/, tools/ai-assist/calibration-defaults.json, .claude/skills/, .agents/skills/, MIGRATION.md, CLAUDE.md, README.md, log.md

## [2026-10-19] refactor | v2026.10.18 — link-relevance, model-calibration v1.3 — @claude
- Skill mới: link-relevance (prepare, sample, validate, decide), rubric Jev anchor-target 2026-10-19.1, test offline.
- model-calibration v1.3: cosine --grid cho điểm ngoài dải cosine. calibration-defaults.json thêm cổng anchor-score 0,52.
- Files touched: skills/{link-relevance,model-calibration}/, tools/ai-assist/calibration-defaults.json, .claude/skills/, .agents/skills/, MIGRATION.md, CLAUDE.md, README.md, log.md

## [2026-10-19] refactor | v2026.10.19 — visual-serp-lab — @claude
- Skill mới: visual-serp-lab (images, fetch, embed, jev-in, pairs, media, shoot, layout), rubric Jev image-fit và first-screen 2026-10-19.1, test offline.
- Lệnh embed dừng khi thiếu file ảnh: SentenceTransformer encode chuỗi đường dẫn như chữ khi file không tồn tại.
- calibration-defaults.json thêm cổng first-screen (8 câu) và image-fit fits_section. Không thêm default alt-score.
- Files touched: skills/visual-serp-lab/, tools/ai-assist/calibration-defaults.json, .claude/skills/, .agents/skills/, MIGRATION.md, CLAUDE.md, README.md, log.md

## [2026-10-19] refactor | v2026.10.20 — Dạng mã của link: link thật hay link JS — Vincent chốt — @claude
- `internal-linking` v1.3 (`references/link-js.md` mã D1–D6, Bước 4c, cột `Dạng mã`, 3 anti-pattern); luật trạm 06. Mirror sinh lại bằng `tools/sync-agent-skills.rb` ở root workspace.
- Files touched: skills/internal-linking/, .claude/skills/internal-linking/, .agents/skills/internal-linking/, 06-onpage-internal-link/CLAUDE.md, MIGRATION.md, log.md
- Công đoạn: 18 · WS: 06

## [2026-10-19] refactor | v2026.10.21 — Bỏ chuẩn đếm số không theo Semantic SEO — Vincent yêu cầu — @claude
- Checklist onpage P3, P6, P8, P14, P16–P20, T3-P1/P5/P6 bỏ quota keyword, link, bold, alt và ngưỡng %; internal link bỏ quota 2-5 sibling và 5-10 link mỗi bài; Tier 1 bỏ quota câu hỏi tu từ; nhãn "LSI" đổi thành "đồng nghĩa/biến thể".
- Skill: seo-onpage 1.4.3, internal-linking 1.3.1, geo-content-optimization 1.3.3, visual-semantic-seo 3.7.1, image-seo-optimize 1.2.1, backlink-plan 1.2.1, textlink-analyzer 1.1.1. Mirror sinh lại bằng `tools/sync-agent-skills.rb`.
- Files touched: 02-raw/knowledge/sop/03, 06-self-checklist/tier-1 + tier-2, 08, 11; 02-raw/knowledge/cheat-sheets/ws06, ws07; 06-onpage-internal-link/CLAUDE.md; _TEMPLATES/internal-link-plan.md, gate-offpage-decision.md; 7 skill trên + .claude/skills/, .agents/skills/; MIGRATION.md; log.md
- Công đoạn: 18, 19, 25 · WS: 06, 07

## [2026-10-19] refactor | v2026.10.22 — web-qa-gate, content-quality-lab v1.1, tools/capabilities — @claude
- Skill mới: web-qa-gate (cổng kiểm 11 hạng mục sau mỗi lần ghi lên site WordPress; Jev ui-visual hiệu chuẩn lượt đầu 72 ảnh, chưa câu nào đạt ngưỡng).
- content-quality-lab v1.1: lệnh claims (cam kết, tự xếp hạng, số không nguồn, số lệch bảng fact); hiệu chuẩn dev 167, holdout 60, h4 60 câu claim + 50 câu fact.
- Tool mới: tools/capabilities.md, capabilities.py, tests/test_capabilities.py (Bước 0 kiểm tool). CLAUDE.md §0 thêm tự chấm plan.
- Files touched: skills/{web-qa-gate,content-quality-lab}/, tools/{capabilities.md,capabilities.py,tests/test_capabilities.py}, tools/ai-assist/calibration-defaults.json, .claude/skills/, .agents/skills/, MIGRATION.md, CLAUDE.md, README.md, log.md

## [2026-10-19] refactor | v2026.10.23 — ngram, SCN, kiểm kê bài, technical, GEO đo lại, topical gap, entity, viết lại an toàn — @claude
- Skill mới: ngram-semantic-gap 1.0, semantic-content-network 1.0, content-inventory-audit 1.0 (54 skill).
- Skill sửa: technical-seo-audit 1.8.1, geo-tracking-prompt-selection 1.5, topical-focus 1.1, geo-answer-lab 1.1, content-quality-lab 1.2.1, web-qa-gate (Bước 0).
- Tool: jev.py chặn trường `must_be_empty`; gsc-cannibal-pair khai `shared_queries`; calibration-defaults +6 entry.
- Đánh lại số entry 19/10 "web-qa-gate, content-quality-lab v1.1" từ v2026.10.20 thành v2026.10.22, vì phiên khác đã dùng v2026.10.20 và v2026.10.21.
- Files touched: skills/{9 skill trên}/, tools/ai-assist/{jev.py,README.md,calibration-defaults.json,tasks/gsc-cannibal-pair.json}, MIGRATION.md, README.md, CLAUDE.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.24 — seo-onpage pixel, serp-clustering Gemma, định tuyến query → URL — @claude
- seo-onpage 1.5.0 (serp_pixel.py, mốc 688 px), serp-clustering 1.1 (lọc trước cosine < 0,90), keyword-topic-url-mapping 1.3, query-processing-diagnosis 1.3 (gsc_route.py).
- Tool: capabilities.md (pillow, gemma, numpy), calibration-defaults +1 entry serp-clustering-prefilter.
- Files touched: skills/{seo-onpage,serp-clustering,keyword-topic-url-mapping,query-processing-diagnosis}/, tools/capabilities.md, tools/ai-assist/calibration-defaults.json, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.25 — geo-fanout-research, geo-content-optimization, content-refresh — @claude
- geo-fanout-research 1.1 (fanout_cover.py), geo-content-optimization 1.4.0 (bỏ ngưỡng 0,80/0,90), content-refresh 1.1 (intent_shift.py). Bản root geo-variant-simulation 1.1 dùng margin 0,015.
- Tool: capabilities.md (gemma, numpy, ahrefs), calibration-defaults +2 entry.
- Files touched: skills/{geo-fanout-research,geo-content-optimization,content-refresh}/, tools/capabilities.md, tools/ai-assist/calibration-defaults.json, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.26 — semantic-content-audit, seo-drift-tracker, seo-logfile-analysis, hreflang-planner — @claude
- semantic-content-audit 2.3 (Jev writing-rules chỉ lọc), seo-drift-tracker 1.1 (Jev diff-impact từ 0,65), seo-logfile-analysis 1.1 (log theo cụm, chưa có log thật), hreflang-planner 1.1 (sec_cov < 0,82). Bản root eeat-proof 1.2 (Jev ymyl).
- Tool: capabilities.md (jev, numpy, gemma, bs4).
- Files touched: skills/{semantic-content-audit,seo-drift-tracker,seo-logfile-analysis,hreflang-planner}/, tools/capabilities.md, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.27 — sửa sau kiểm đợt 2, quyết định Vincent, parser log OLS — @claude
- content-quality-lab 1.2.3 (--own-site), serp-clustering 1.1.1, keyword-topic-url-mapping 1.3.1, semantic-content-network 1.0.1, query-processing-diagnosis 1.3.1 (vai trò 4/10 và 6/10, Gemma trang tiền chỉ là danh sách đọc).
- geo-answer-lab 1.1.1, topical-focus 1.1.1, technical-seo-audit 1.8.2, hreflang-planner 1.1.1, geo-fanout-research 1.1.1, geo-content-optimization 1.4.1, seo-drift-tracker 1.1.1, seo-logfile-analysis 1.1.1 (parser OpenLiteSpeed, 6 bot mới).
- Files touched: skills/{content-quality-lab,serp-clustering,keyword-topic-url-mapping,semantic-content-network,query-processing-diagnosis,geo-answer-lab,topical-focus,technical-seo-audit,hreflang-planner,geo-fanout-research,geo-content-optimization,seo-drift-tracker,seo-logfile-analysis}/, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.28 — 5 skill WordPress và media mới, 4 skill sửa — @claude
- Mới: wp-staging-deploy 1.0, wp-theme-build 1.0, wp-paid-plugin-exit 1.0, semantic-media 1.0, blog-interactive-tools 1.0. Lượt thử chỉ đọc hoặc dry, bằng chứng ngoài repo.
- Sửa: wp-security-hardening 1.5 (PHP trong languages, upgrade, path-info; probe chỉ 403), wp-content-review-apply 1.3 (sửa trực tiếp nút E), image-seo-optimize 1.2.2, wp-pagespeed 1.9.1.
- Tool: capabilities.md thêm ffmpeg và tên skill. README, CLAUDE.md §4: 59 skill.
- Files touched: skills/{wp-staging-deploy,wp-theme-build,wp-paid-plugin-exit,semantic-media,blog-interactive-tools,wp-security-hardening,wp-content-review-apply,image-seo-optimize,wp-pagespeed}/, tools/capabilities.md, README.md, CLAUDE.md, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.29 — Bước 0 kiểm tool cho 21 skill, chuẩn câu Bước 0 cho 5 skill — @claude
- Bước 0 theo câu mẫu của skill-creator; lệnh kiểm cấu trúc đạt 103/103 khối trong workspace.
- media_match.py không sinh __pycache__ trong site-vector-index nữa.
- Pilot chỉ đọc trên instance careerviet (route Gemma 76/88 top 1, title vượt 688 px 31/92). Không ghi vào instance; bằng chứng ngoài repo.
- Files touched: 26 thư mục skills/ (liệt kê trong MIGRATION v2026.10.29), MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-19] refactor | v2026.10.30 — Nối dữ liệu Ahrefs cho bộ backlink và đo trích dẫn AI — @claude
- link-relevance 1.1 (verdict M1–M3), backlink-research 2.2, backlink-plan 1.3.0, textlink-analyzer 1.2.0, geo-tracking-prompt-selection 1.6: thêm script đọc kết quả Ahrefs + test offline.
- Lượt thử trên dữ liệu Ahrefs thật của site mẫu và 4 đối thủ; bằng chứng ngoài repo.
- Files touched: skills/{link-relevance,backlink-research,backlink-plan,textlink-analyzer,geo-tracking-prompt-selection}/, tools/capabilities.md, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-21] refactor | v2026.10.31 — Bài học đo tràn, biến thể cache và object cache — @claude
- web-qa-gate 1.1 (đo tràn không bật cờ mobile, 6 bẫy), wp-pagespeed 1.10 (cache_variants.py, psi_run chặn utm_*, shot.mjs không bật cờ mobile, lớp 1 và lớp 4), wp-content-review-apply 1.4 (apply.php xoá object cache trước purge, CSS Elementor theo tài liệu).
- Rút từ đợt site agency mẫu 20–21/10; test offline 13/13, fixture local, server giả, 2 URL production chỉ đọc. Bằng chứng ngoài repo.
- Files touched: skills/{web-qa-gate,wp-pagespeed,wp-content-review-apply}/, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-24] refactor | v2026.10.32 — Model mặc định là Opus mới nhất, bài học đợt nhiều lane 23–24/10 — @claude
- `.claude/settings.json` thêm `"model": "opus"` (Vincent chốt 24/10). wp-pagespeed 1.11, wp-paid-plugin-exit 1.1, web-qa-gate 1.2, wp-security-hardening 1.6, wp-content-review-apply 1.5, seo-logfile-analysis 1.2, hreflang-planner 1.2.
- Kiểm: test offline web-qa-gate 13/13, log_health.py 3/3. Bằng chứng ngoài repo.
- Files touched: .claude/settings.json, skills/{wp-pagespeed,wp-paid-plugin-exit,web-qa-gate,wp-security-hardening,wp-content-review-apply,seo-logfile-analysis,hreflang-planner}/, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-25] refactor | v2026.10.33 — Đợt dựng skill sau rà soát web 16–24/10 — @claude
- Skill mới wp-ui-fix 1.0. Nâng cấp wp-pagespeed 1.12, wp-staging-deploy 1.1, wp-content-review-apply 1.6, web-qa-gate 1.3, wp-security-hardening 1.7, semantic-media 1.1, content-inventory-audit 1.2 (26/10: chỉ 301 về bài cùng chủ đề), internal-linking 1.4, seo-logfile-analysis 1.3, technical-seo-audit 1.9, wp-theme-build 1.1, model-calibration 1.4, wp-paid-plugin-exit 1.2. `tools/ai-assist` thêm cờ jev.py và 8 rubric.
- Kiểm: test offline 14 skill đạt, kiểm cấu trúc và client-neutral đạt. Bằng chứng ngoài repo.
- Files touched: skills/{wp-ui-fix,wp-pagespeed,wp-staging-deploy,wp-content-review-apply,web-qa-gate,wp-security-hardening,semantic-media,content-inventory-audit,internal-linking,seo-logfile-analysis,technical-seo-audit,wp-theme-build,model-calibration,wp-paid-plugin-exit}/, tools/ai-assist/, tools/capabilities.md, .gitignore, CLAUDE.md, README.md, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-26] refactor | v2026.10.34 — backup_pull.sh không chép mode thư mục của server — @claude
- wp-security-hardening 1.7.1: `rsync -rlt` + `chmod` thư mục đích. Kéo thật 2,7 GB đạt.
- Files touched: skills/wp-security-hardening/, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-27] refactor | v2026.10.36 — Nâng 7 skill tốc độ, crawl, bảo mật; thêm 4 skill điều phối, wf-status, sổ lượt gọi Jev — @claude
- Nâng wp-ucss 1.1.0, wp-pagespeed 1.14, seo-logfile-analysis 1.4, cdn-speed-setup 1.2, wp-security-hardening 1.8, web-qa-gate 1.3.1, technical-seo-audit 1.10. Thêm 4 skill điều phối bản sinh từ master (web-lane-orchestration 1.2, decision-page 1.0.1, workstream-master-plan 1.0.1, runtime-handoff 1.3.1), không sửa tay.
- Thêm `tools/wf-status.py`, `tools/shell-traps-macos.md`, `tools/ai-assist/jev_ledger.py`, `_REFERENCE/luat-duyet-dieu-phoi.md`. `jev.py` ghi sổ lượt gọi và có cờ `--label`. `ORCHESTRATOR.md` thêm mục 4.1 trỏ tới 4 skill điều phối. `master_version` đổi thành v2026.10.36.
- Files touched: skills/{wp-ucss,wp-pagespeed,seo-logfile-analysis,cdn-speed-setup,wp-security-hardening,web-qa-gate,technical-seo-audit,web-lane-orchestration,decision-page,workstream-master-plan,runtime-handoff}/, tools/wf-status.py, tools/tests/test_wf_status.py, tools/shell-traps-macos.md, tools/ai-assist/jev.py, tools/ai-assist/jev_ledger.py, _REFERENCE/luat-duyet-dieu-phoi.md, ORCHESTRATOR.md, MIGRATION.md, log.md, .claude/skills/, .agents/skills/

## [2026-10-27] refactor | v2026.10.37 — Gộp skill hai bản: repo này là bản gốc của 29 skill, 4 skill sinh từ master — @claude
- 19 skill gộp giữ nguyên, 10 skill hợp nhất nội dung của master, 4 skill GEO và báo cáo sinh bằng công cụ port của master. Chi tiết: MIGRATION.md v2026.10.37.
- Files touched: skills/<29 skill>/, skills/<4 skill sinh>/, .claude/skills/, .agents/skills/, MIGRATION.md

## [2026-10-27] refactor | v2026.10.38 — Skill wp-dang-bai đăng bài lên gtvseo.com, theaigrowth.io qua REST — @claude
- Script wp_publish.py (doctor, push, media, trash), mu-plugin doc-kit, bài mẫu. Đã thử staging và production 2 site.
- Files touched: skills/wp-dang-bai/, .claude/skills/wp-dang-bai/, .agents/skills/wp-dang-bai/, CLAUDE.md §11, MIGRATION.md

## [2026-10-27] refactor | v2026.10.39 — Skill wp-xuat-ban-bai, anh-trong-bai; wp-dang-bai 1.2 đọc web-profile — @claude
- wp-xuat-ban-bai 1.0: md_to_html.py, kiem_bai.py, kiem_render.mjs, 4 reference, mẫu web-profile, test offline. anh-trong-bai 1.0: media_plan.py, svg_dung.py (7 kiểu), svg_kiem.mjs, chup_trang.mjs, anh_chu_thich.py, chen_media.py, 4 reference, test offline. wp-dang-bai 1.2: profile, --featured-alt, slug và SEO title từ thẻ meta.
- Pilot bài content-effort: đăng nháp trên site mẫu GTV, 7 khung media, render đạt 1366 px và 390 px.
- Files touched: skills/{wp-xuat-ban-bai,anh-trong-bai,wp-dang-bai}/, .claude/skills/, .agents/skills/, CLAUDE.md §11, MIGRATION.md, log.md

## [2026-10-27] refactor | v2026.10.40 — Kiểm URL sau publish (wp-dang-bai 1.2.1, wp-xuat-ban-bai 1.0.1) — @claude
- Publish bài pilot content-effort: URL 404 do plugin permalink chưa ghi URI và ảnh trùng slug. Đã sửa trên site, vá script và reference.
- Files touched: skills/wp-dang-bai/, skills/wp-xuat-ban-bai/, .claude/skills/, .agents/skills/, MIGRATION.md, log.md

## [2026-10-27] refactor | v2026.10.41 — Eval 3 skill xuất bản; router đăng web — @claude
- evals/cases.yaml cho wp-xuat-ban-bai (9 ca), anh-trong-bai (7), wp-dang-bai (5); wp-dang-bai thêm mục xoá media WPML. Router §0.5 và trạm WS06 trỏ tới wp-xuat-ban-bai khi site có web-profile.
- Files touched: skills/{wp-xuat-ban-bai,anh-trong-bai,wp-dang-bai}/, .claude/skills/, .agents/skills/, CLAUDE.md, 06-onpage-internal-link/{CLAUDE.md,README.md}, MIGRATION.md, log.md
