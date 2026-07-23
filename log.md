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
