---
master_version: v2026.10.2
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

### v2026.10.2 (2026-10-02) — Knowledge pack: SOP 12 mô hình backlink stack + SOP 10 v1.2

Vincent duyệt 02/10. Nguồn: tài liệu training nội bộ "Bí thuật backlink thất truyền" bản 6, đã ingest vào kho gốc wiki Semantic SEO.

- **Knowledge pack, file mới:** `02-raw/knowledge/sop/12-backlink-stack-models.md` (v1.0). Nội dung ở mức bản đội SEO: quy trình duyệt, khung T.T.T, thư viện mô hình (DAS, TAS, 08 method, báo có buffer), luật tầng T1/T2/T3, bộ luật thiết kế, chuẩn tài sản MS-01→14, đo ba tầng với bốn mốc kiểm, kill switch, worksheet, rubric 10 tiêu chí. Không gồm bảng năm dạng textlink báo, cách tìm nguồn trust cao, sáu mô hình mở rộng, danh sách vendor (SEO Lead và SEO Director giữ).
- **Knowledge pack, re-sync:** `sop/10-offpage-process.md` (v1.2: §1.6 khung T.T.T bản 2026; §4 người duyệt tier ⚠ là SEO Lead xem trước, SEO Director chốt mọi phương án; textlink báo ở trang chủ, chuyên mục, sitewide sang tier ⚠; luật PBN hai trường hợp; link wheel giữa các domain rời vào tier ⛔) và `sop/06-self-checklist/tier-1-offpage-backlink.md` (OF-05, OF-08; số item và P0 không đổi).
- **Skill:** `backlink-plan` 1.2. Mức Aggressive (PBN, parasite, mô hình stack, textlink báo ở trang chủ/chuyên mục/sitewide) do SEO Lead xem trước, SEO Director chốt; làm được cho khách khi phương án đã duyệt; có luật tầng đi kèm. Bỏ câu "GTV không làm cho khách".
- **Chưa đổi:** ma trận nạp (`02-raw/knowledge/README.md` mục 1, `_REFERENCE/runtime-workstream-matrix.md`, `CLAUDE.md` §5.2), khung công đoạn, `index.md`. SOP 12 chưa có mốc trong quy trình 10 tháng; Vincent cập nhật sau. Cho tới lúc đó, mô hình stack chỉ chạy khi có phương án được SEO Director chốt.
- **Port sang instance:** GHI ĐÈ 3 file knowledge pack trên, `02-raw/knowledge/_MANIFEST.md`, `skills/backlink-plan` và mirror. Batch đang chạy có hạng mục thuộc OF-08: bổ sung chữ ký SEO Director nếu trước đó chỉ có SEO Lead duyệt.

### v2026.10.1 (2026-10-01) — Đọc Kho tri thức khách (KB) từ fork content

Vincent duyệt 01/10. Fork content giữ bản gốc fact của khách ở `00-context/kb/` (sổ fact + catalog sản phẩm/biến thể); instance SEO chỉ đọc snapshot.

- **Tool:** `tools/content_sync.py --pull-kb` chép bundle `kb/` của fork vào `00-client-context/kb-snapshot/<YYYY-MM-DD>/` (mỗi ngày một bản, không ghi đè, không ghi gì vào fork).
- **Luật trạm (1–2 dòng mỗi trạm):** root `CLAUDE.md` §11 (điểm chạm KB) · `00-client-context` (tài liệu kỹ thuật chuyển về fork; #3 tra FD-11/14/15/22 trong snapshot) · `05-content-plan` (node topical map ghi trang KB + cột gap) · `14-entity` luật 8 (Brand Info Pack giữ danh tính/NAP, KB giữ fact sản phẩm; `@id` là IRI trên domain khách) · `06-onpage-internal-link` (link theo quan hệ KB, bảng thông số + schema Product từ catalog, giá/tồn kho từ hệ thống bán hàng) · `07-offpage` + `08-geo-ai-visibility` (output ra ngoài chỉ dùng claim `approved` + `public_ok`; GEO đối chiếu câu trả lời AI với KB).
- **Đồng bộ qua GitHub (nguồn sự thật chung giữa team SEO và team content):** `tools/project_sync.py pull` kéo repo content cùng khách (theo `project-sync.yaml` ở root) về `.peer/content/` rồi chạy `content_sync.py` (trạng thái bài + bài đã humanize + KB snapshot kèm `_source.md`). Repo content có lệnh đối xứng kéo hồ sơ khách, KPI, OKRs, cấu trúc URL, topical map/plan, internal link plan, GEO, entity (không bao giờ kéo `hop-dong-*`). Bảng "ai giữ dữ liệu nào": `_REFERENCE/project-sync.md` (mới). Mẫu cấu hình `_TEMPLATES/project-sync.yaml` (mới). `SETUP.md` bước 7, `COMMANDS.md`, `AGENTS.md`, `.gitignore` (`.peer/`) cập nhật. Thử thật với GitHub 01/10: kéo `content-production-minh-tuan-mobile` (5 bài, 1 bài delivered).
- **Port sang instance:** GHI ĐÈ `tools/content_sync.py`, `tools/project_sync.py` (mới), `_REFERENCE/project-sync.md`, `_TEMPLATES/project-sync.yaml`, 7 file `CLAUDE.md` trên, `SETUP.md`, `COMMANDS.md`; PATCH TAY `AGENTS.md` (mục mới cuối file) và `.gitignore` (thêm `.peer/`). Sau đó chép `project-sync.yaml` ra root instance, điền 2 repo, commit + push. Không đổi knowledge pack.

### v2026.09.5 (2026-09-28) — Quy định về tăng CTR theo leak Google + fact-fix dẫn patent

Vincent duyệt 28/09. Căn cứ: wiki `Knowledge/Google Leak Decoded` (toàn văn patent và mô tả gốc của leak).

- **Knowledge pack:** re-sync `02-raw/knowledge/sop/10-offpage-process.md` (v1.1: §4 thêm mục "Tín hiệu người dùng (click)") và `02-raw/knowledge/sop/06-self-checklist/tier-1-traffic-users.md` (thêm Phụ lục B). Dòng Traffic users giữ nguyên ở tier ⚠, chỉ chạy khi SEO Director duyệt bằng văn bản. Click bot, trình giả lập, proxy, gói click không rõ nguồn bị cấm trong mọi dự án khách. Số item TU-01 → TU-16 không đổi.
- **Skill:** `seo-onpage` 1.4.1 và `visual-semantic-seo` 3.0.1 bỏ dẫn US10565267B1, US8868565B1, US20150234930A1 làm căn cứ cho website function (chi tiết ở `log.md` ngày 28/09).
- **Port sang instance:** GHI ĐÈ 2 file knowledge pack trên, `02-raw/knowledge/_MANIFEST.md`, `skills/seo-onpage`, `skills/visual-semantic-seo` và mirror. Không có file mới, không đổi cấu trúc folder. Chiến dịch Traffic users đang chạy ở instance: bổ sung 3 rủi ro của Phụ lục B vào văn bản duyệt TU-01.

### v2026.09.4 (2026-09-13) — WS 13 CRO v2: đo trước, pattern có mức nặng, brief dev làm được, rollout có theo dõi

Vincent chốt 12/09: CRO là phần tăng giá trị hợp đồng SEO để tái ký (không phải dịch vụ riêng); mặc định "research + sửa lỗi + rollout có theo dõi", A/B là ngoại lệ; pattern theo cơ chế chuyển đổi (gọi/Zalo · form · báo giá · giỏ hàng · apply) thay vì theo ngành. Nguồn phương pháp: wiki `Knowledge/Inbound Marketing/` (44 + 13 nguồn, review Fable 5.1 12–13/09).

- **Skill `cro-audit` v2.0:** router readiness (A research+fix+rollout | B A/B) × cơ chế × loại trang; scorecard P0/P1/P2 × R × E; blocker P0 site-wide tách khỏi CR-08; ≤3 click thành diagnostic; deadline triển khai ≠ cửa sổ đọc số; 6 references (`readiness-router`, `research-evidence`, `patterns-condensed` 10 pattern, `feature-brief` 10 mục, `experiment-lite` feasibility + SRM, `report-hook` 3 khối) + `evals/cases.yaml` 10 ca.
- **Skill MỚI `cro-measurement-plan`:** outcome + mẫu số, event contract theo cơ chế (GA4 recommended + custom gọi/Zalo/apply), spec GTM cho dev khách, kênh AI Assistant (custom channel group đặt trên Referral, 4 điểm mù), đối soát CRM/Sheet, 20 ca QA; 4 references + evals.
- **`13-cro/CLAUDE.md`:** luật cứng 1–7 viết lại (G1 cho phép research/blocker/brief; blocker P0 bất kể rank; scorecard; ≤3 click diagnostic; deadline ≠ cửa sổ; spec 10 mục); bảng I/O thêm measurement-plan, tracking-qa, evidence-backlog; không đặt KPI nội bộ theo tỷ lệ brief được triển khai (bỏ 13/09) — theo dõi bằng ba mốc trạng thái brief + P0 còn mở.
- **Checklist:** `tier-1-cro-conversion.md` — G1, CR-08, CR-14 (+INP/CLS p75), CR-15 (rollout có theo dõi; 1 giả thuyết = 1 treatment; feasibility), CR-16 (diagnostic). `tier-1-ux-ui.md` — UX-18 (label ≠ placeholder, focus not obscured, 24px AA / 44px nội bộ).
- **Template:** MỚI `measurement-plan.md`, `tracking-qa.md`, `evidence-backlog.md`; SỬA `ux-feature-brief.md` (§2 metric theo dõi thay "CR +x%", §3 spec 10 mục, §4 cửa sổ ≥4 tuần + trạng thái brief), `heatmap-recording-review.md` (§4 log sửa lỗi/rollout/A/B + feasibility + SRM). `_TEMPLATES/README.md` 32 → 35.
- **Root:** `CLAUDE.md` §6.2 dòng tracking; `index.md` bảng C hàng CRO; `README.md` 35 template / 38 skill. Report tháng: skill `gtv-client-report` §3 CRO đổi thành 3 khối (phát hiện · đã sửa + số quan sát · chờ khách) — vá ở root và fork repo này.
- **Patch cùng ngày (review Astra 13/09, 11 finding):** `cro-audit` v2.1 + `cro-measurement-plan` v1.1 — "thành công" = kết quả nghiệp vụ (không HTTP 200), listener WPForms bằng jQuery, metric tử/mẫu/đơn vị tường minh, regex kênh AI full match + allowlist có neo, quota GA4, dedup không dựa localStorage, QA có N/A + gate theo cơ chế primary, scorecard thứ tự tường minh + severity tách evidence + P0 tồn hiện đầu report, bảng chuyển việc WS13/WS04/technical/copywriting, "lỗi web VN" → giả thuyết cần kiểm. SOP: ma trận `_REFERENCE/runtime-workstream-matrix.md` hàng CRO; `13-cro/README.md`; `conversion-path.md` (§0 readiness, §1 contract mới + mapping legacy, ≤3 click diagnostic, DoD); `heatmap-recording-review.md` (E3/E2, §3 đường + QA ngay sau deploy); `ux-feature-brief.md` (nguồn vấn đề E3/E2, QA ngay sau deploy); `tracking-qa.md` + `measurement-plan.md` (N/A, gate theo cơ chế, quota, metric); CR-06 (contract + mapping legacy), CR-19 (pending khi G1 chưa pass/offsite); `04-structure-ux-cro/CLAUDE.md` (WS04 kiểm thiết kế, WS13 giữ tracking/live QA); `CLAUDE.md` §4 đếm 35 template/38 skill; report §3 (root + fork). Review: `Knowledge/Inbound Marketing/wiki/syntheses/gtv-cro-build-review-astra-2026-09-13_v1.md`.
- **Port sang instance:** GHI ĐÈ nhóm A (`13-cro/CLAUDE.md` + `README.md`, 2 checklist, `_TEMPLATES/` 6 file CRO, `_REFERENCE/runtime-workstream-matrix.md`, `skills/cro-audit`, `skills/cro-measurement-plan` + mirror, `skills/gtv-client-report/references/kpi-table-formats.md`, `04-structure-ux-cro/CLAUDE.md`, `CLAUDE.md`, `README.md`, `MIGRATION.md`); `index.md` instance: sửa tay hàng CRO bảng C (không ghi đè vì có status thật). Deliverable `13-cro/` đã có giữ nguyên; conversion-path cũ thêm §0 readiness ở đầu khi chạm lại. Port sau pilot và duyệt.

### v2026.09.3 (2026-09-03) — Keyword research · WS 14 Entity · Đấu nối content · Audit lẻ · WS 13 CRO (#34–36)

Vincent chốt 03/09: 5 khoảng trống theo `quy-trinh-seo-10-thang` — keyword research chưa có chỗ lưu phương pháp + data, entity có gate mà không có folder/skill, content không đấu nối được với fork, audit lẻ phải chạy full, CRO lẫn trong cấu trúc.

- **13 → 14 workstream · khung 33 → 36 công đoạn:** thêm **#34** CRO conversion path + tracking (T2→T3, gate G1 CR-06/07 ≤T3 — mốc cứng mới §6.2), **#35** UX/UI feature brief + heatmap đợt 1 (T4→T6), **#36** tối ưu landing + A/B (T7→T9). `index.md` bảng B + bảng C (nhịp CRO, content tracking); `_REFERENCE/khung-33-cong-doan.md` (giữ tên file, nội dung 36); README sơ đồ pha.
- **WS MỚI `13-cro/`** (README · CLAUDE.md persona *CRO Analyst* · AGENTS.md) + 3 template `conversion-path.md` / `ux-feature-brief.md` / `heatmap-recording-review.md` + **skill mới `cro-audit`**. Checklist dùng lại `tier-1-cro-conversion.md` (CR-01…19) + `tier-1-ux-ui.md`. Trạm 04 chỉ còn cấu trúc lock #11 (ma trận M hàng Structure bỏ tier-1-cro phần A → sang WS 13).
- **Keyword research:** `05-content-plan/keyword-research/` (README) + `_TEMPLATES/keyword-research.md` (M1–M9, cluster, quyết định) + cheat-sheet MỚI `02-raw/knowledge/cheat-sheets/keyword-research-methods.md` (chưng cất wiki: SERP overlap, GSC mining, phantom gate, KD là tool-metric, intent bằng SERP) + `02-raw/seo-data/keywords/` (export immutable). Ma trận M thêm hàng *Keyword research*.
- **Entity thành workstream riêng (Vincent chốt 03/09):** WS MỚI **`14-entity/`** (README · CLAUDE.md persona *Entity Manager* · AGENTS.md) — #13 chuyển WS `06` → `14`; **skill mới `entity-seo-plan`** (lập + chấm EN-01…16) + `_TEMPLATES/audit-entity.md` → `03-audits/entity/`; `entity-plan.md` đổi `ws: 14-entity`. WS 06 bỏ #13 khỏi công đoạn phụ trách + bỏ checklist entity (chỉ còn thực thi schema/onpage từng URL theo spec entity plan); WS 08 GEO ghi "phối hợp WS14". Ma trận M: hàng *Entity* mới, hàng *Onpage & IL* rút gọn.
- **Đấu nối content ↔ fork:** `05-content-plan/content-tracking/` (README · `delivered/`) + `tools/content_sync.py` (stdlib): đọc `index.md` + `log.md` fork → `content-status.md` (đếm 9 status, bài kẹt ≥14 ngày, bài humanized sẵn cho WS06) + `--pull-delivered` copy bản humanized về. Ma trận M thêm hàng *Content tracking*.
- **Audit lẻ:** `03-audits/{technical,content,entity,offsite,full}/` (README mỗi folder) + 4 template `audit-technical.md` / `audit-content.md` / `audit-entity.md` / `audit-offsite.md`; `audit-toan-dien.md` giữ cho bản gộp (#5/#27) trong `full/`.
- `CLAUDE.md`: §4 folder map, §5.1 (36), §5.2 (+4 hàng, hàng Audit ghi template lẻ), §6.2 (+ mốc tracking ≤T3). `README.md`: 36 công đoạn, 14 WS, 32 template, 37 skill. `_REFERENCE/folder-map.md`.
- **Port sang instance:** GHI ĐÈ nhóm A (root luật, `_REFERENCE/`, `_TEMPLATES/`, `02-raw/knowledge/`, `skills/` + mirror, README/CLAUDE/AGENTS trạm, `tools/`); **THÊM** folder mới (`13-cro/`, `14-entity/`, `03-audits/*/`, `05-content-plan/keyword-research/`, `content-tracking/`, `02-raw/seo-data/keywords/`); instance đã nhận bản sáng 03/09 có `06-onpage-internal-link/entity/` rỗng → script tự xoá (chỉ khi trong đó không có file nào ngoài README) — không đụng deliverable; `index.md` instance: **append 3 dòng #34–36 + 2 dòng bảng C** (không ghi đè vì có status thật), đổi tiêu đề bảng B. Script `tools/migrate_v2026_09_3.py` ở master làm việc này (idempotent). File audit/keyword research cũ đang nằm rải trong instance: Lead dời tay vào folder mới, log op `move`.

### v2026.09.2 (2026-09-02) — Trạm-first: router §0.5, ORCHESTRATOR thành tùy chọn nâng cao, sub-agent chỉ khi opt-in, tách `_REFERENCE/`, standalone

- **`CLAUDE.md` (463 → 347 dòng):** thêm **§0.5 Router** — bảng lệnh → thao tác (Ingest/Work/QC/Feedback/tra cứu/protocol/điều phối nâng cao) → trạm → "Nạp đúng thứ tự". Luật mới: làm **trong phiên, từng trạm một**; nhiều item cùng trạm (onpage 10 bài, audit 5 URL, QC 3 deliverable) = lặp tuần tự cùng context, báo từng item; **0 sub-agent mặc định**. Pre-work §3 + ma trận M §5.2 + mốc cứng §6.2 + QC §7 giữ nguyên nội dung (không rút gọn input chất lượng). §11 viết lại thành "Standalone": repo không tham chiếu folder nào ngoài nó; 2 điểm chạm duy nhất là repo content của team và kit `wp-publish-workflow-kit` (repo public). §13 thêm anti-pattern "bung sub-agent/orchestrator cho việc 1 trạm".
- **`_REFERENCE/` MỚI (5 file, nguyên văn từ CLAUDE.md cũ):** `folder-map.md` (§4), `khung-33-cong-doan.md` (§5.1), `qc-report-format.md` (§7.3), `screenshots-protocol.md` (§8), `self-improving.md` (§9). Nạp khi router trỏ tới.
- **`ORCHESTRATOR.md`:** header → "tùy chọn nâng cao — chỉ đọc khi gọi rõ chạy trọn/nối tiếp/song song/quản đốc"; mặc định quản đốc tự đóng vai nhân viên từng trạm trong cùng phiên; sub-agent (kể cả `ws08-geo`) chỉ khi opt-in "song song"/"fan-out", trần theo `.claude/settings.json` (2 đồng thời, độ sâu 1); §4 fan-out + §5.1 Pre-work đổi câu chữ tương ứng.
- **`.claude/agents/ws08-geo.md`:** description "CHỈ gọi khi opt-in fan-out hoặc gọi rõ tên"; thêm `tools` (không có Agent → không đẻ sub-agent lồng). **`.claude/settings.json` MỚI:** effort high + trần sub-agent.
- **`COMMANDS.md`:** tách `làm công đoạn <n>` (trạm-first) và `chạy trọn công đoạn <n>` (điều phối nâng cao). `README.md`: mô tả ORCHESTRATOR là tùy chọn. `AGENT.md`: mục 0 bản nhúng v2026-09-02 (miễn trừ luật ngắn gọn cho deliverable/báo cáo khách/hợp đồng, luật mật độ chữ, sub-agent).
- **Port sang instance:** GHI ĐÈ nhóm A bảng mục 2 (kể cả `_REFERENCE/`, `.claude/agents/`, `.claude/settings.json`); GIỮ nhóm B. Instance chưa nhận v2026.09.1 thì nhận luôn cả 2 đợt trong một lần đè.

### v2026.09.1 (2026-09-02) — Vá chuỗi GEO v2 đứt gãy + đăng ký gate vào lớp điều phối + lớp business còn thiếu

- **Knowledge pack:** đóng gói `02-raw/knowledge/sop/09-timeline/lop-geo-v2.md` (guideline 6 điểm chạm — trước đây 6 file trỏ path không tồn tại `sop/09-project-timeline/`); re-sync mục AX của `sop/08-onpage-checklist.md` lên **AX1-AX7** (AX6 passage verifiability, AX7 heading/title/meta ↔ fan-out, chuẩn chunk 29/08 bỏ cap 375 từ) — mọi chỗ ghi AX1-AX5/AX1-AX6 đã thống nhất AX1-AX7; version `tier-1-geo.md` thống nhất 2.0.2. `_MANIFEST.md` 18 hàng.
- **`index.md`:** dòng #13/#14/#21/#28 mang nhãn G0-G5 + gate G-ENT/G-T1 (khớp ma trận M §5.2); luật đọc bảng 3 nói cách ghi gate GEO; bảng C thêm nhịp **Báo cáo khách** (tháng/quý/nghiệm thu) + **Content refresh** (T6/T9).
- **`ORCHESTRATOR.md` §3:** thêm hàng 4 gate GEO (G-T1 · G-ENT · G-BÀI · G-KH) vào bảng chốt giám đốc; §7 báo đỏ soạn theo `_TEMPLATES/escalation-note.md` (MỚI).
- **`CLAUDE.md`:** §5.2 hàng Strategy thêm `gtv-project-okrs`; hàng Content plan thêm `geo-fanout-research` ở #10 (fan-out trước khi chốt map, không đợi #28); hàng Reporting thêm `gtv-weekly-report` + `report-config.example.yaml`; §6.2 thêm mốc cứng **G-ENT ≤15 ngày đầu T3**; số skill 35.
- **Template MỚI (21 → 24):** `entity-plan.md` (#13 — deliverable gate G-ENT, trước đây gate có checklist mà không có mẫu) · `escalation-note.md` · `report-config.example.yaml` (instance mới trước đây không có file khởi tạo báo cáo tuần/OKRs quý).
- **Template sửa:** `kick-off.md` thêm mục **3b Kỳ vọng & giới hạn** (7 điều nói với khách buổi đầu — 100 ngày, 90% không cần link, GEO directional, SLA, sửa web, cách đo, kỳ vọng mềm ngoài HĐ) + DoD; `handover-checklist.md` mục 5 thêm **trigger tái ký ≤2 tháng → acc-renewal-brief**, khối **bàn giao PIC nội bộ**, mục **5b thu feedback khách 2 câu**; `content-plan-matrix.md` thêm **mục 2b information gain + fan-out coverage per cụm** + DoD.
- **README trạm 03/08/09/06/11:** đồng bộ danh sách skill/công đoạn/template với ma trận M.
- **Link chết ra ngoài repo:** `sop/02-content-brief.md`, `common-ai-errors.md`, `weekly-report-slides/README.md`, `.claude/agents/ws08-geo.md` — ghi rõ skill/wiki thuộc fork Content Production hoặc wiki, không đóng gói ở đây (luật standalone §11).
- **Instance nhận:** nhóm A GHI ĐÈ (root luật + knowledge pack + `_TEMPLATES/` + README trạm); `index.md` instance đang chạy: sửa tay 4 dòng #13/#14/#21/#28 + 2 dòng bảng C (không ghi đè vì có status thật).
- Ghi chú: `12-feedback-lessons/lessons/` ở master vẫn 0 lesson sau 14 tháng — đề xuất 1 buổi distill hồi tố từ `log.md` (feedback CareerViet 22-23/07, review chéo Codex 30/07) — chưa làm trong đợt này.

### v2026.08.3 (2026-08-29) — Tích hợp wp-publish-workflow-kit + policy `<strong>` + SOP 11 đăng bài WP

- **Phân vai chốt (Vincent):** khâu đăng/sửa bài WordPress thuộc **WS06 (bạn SEO)** — team content dừng ở Google Doc (fork Content Production giữ nguyên Phase 7 gdoc). Executor: kit `wp-publish-workflow-kit` (repo GitHub riêng của team, KHÔNG vendor vào master — xem §11 CLAUDE.md).
- **Policy `<strong>`:** mọi bold trong content = thẻ `<strong>`, `<b>` = 0. Vá P14 trong `02-raw/knowledge/sop/08-onpage-checklist.md` + `skills/seo-onpage/references/p-series-checklist.md`. Khi đăng WP: KHÔNG chạy bước strong-to-b của kit.
- **SOP MỚI** `02-raw/knowledge/sop/11-publish-wp.md`: 2 flow input (bài từ content qua Google Doc + link trong Google Sheet đăng bài 11 cột / SEO kiêm content đăng thẳng), gate pre-publish (P0 content + pháp lý, meta P1-P5, strong policy, ảnh P19-P20 + tier, IL SOP 03, block đặc biệt), verify kép WP+Sheet, bảng giới hạn kit + cách bù. Đăng ký ở `_MANIFEST.md` + `knowledge/README.md`.
- CLAUDE.md root: §5.2 hàng WS06 · §5.4 · §11 (+ interface kit). Trạm 06: README + CLAUDE.md.
- File chỉ ở master (không cần port sang instance đang chạy): `06-onpage-internal-link/WP-PUBLISH-KIT_upgrade-spec_v1.md` (spec nâng cấp gửi team kit).
- Instance nhận qua nhóm A GHI ĐÈ như thường lệ (root luật + knowledge pack + skills + WS infra). Instance muốn đăng WP: clone kit theo docs của kit + tạo Google Sheet đăng bài từ template kit.
- **Cùng đợt (28/08 — setup máy standalone):** `_SETUP/` MỚI (SETUP-MAY.md · setup_doctor.py · setup_credential.py · HUONG-DAN-GOOGLE-CREDENTIAL.md · CHIA-QUYEN-DRIVE.md · sync-skills.sh) + mục BOOTSTRAP đầu `CLAUDE.md` + `requirements.txt` + skill `setup-may` + helper `_cred.py` cho script sheet (credential per-user qua `config/local.yaml`, đã gitignore) + đổi tên công đoạn GEO theo G0-G5 trong §5.1/§5.2. Nhóm A GHI ĐÈ thêm `_SETUP/` + `requirements.txt`.

### v2026.08.2 (2026-08-15) — Nguyên tắc giao tiếp nền nhúng vào AGENT.md (mục 0)

- `AGENT.md` thêm mục **0. Nguyên tắc giao tiếp nền (bản nhúng root — v2026-08-15)**: chat ngắn gọn kết luận trước · deliverable không thừa hưởng luật ngắn gọn (completeness > brevity) · cấu trúc template/QC là sàn · độ dài file/code tối thiểu đủ dùng · trình khung trước khi dựng deliverable lớn · báo rõ phần chưa xác minh. Bản nhúng để repo standalone có đủ luật cấp workspace.
- Instance nhận bản này: chỉ GHI ĐÈ `AGENT.md` (1 file — không phải full migration, KHÔNG đổi `master_version` frontmatter), không đụng client data. 2 instance trong workspace (careerviet, minh-tuan-mobile) đã được áp thẳng cùng ngày.

### v2026.08.1 (2026-08-05) — Hệ báo cáo KỲ (tháng/quý) + OKRs quý lên master

Nguồn: hạ tầng chín ở instance CareerViet (07-08/2026), chạy thật qua báo cáo tuần W11-W13 + kỳ T7/Quý 1, rồi port sang instance Minh Tuấn Mobile (e-commerce) để kiểm tính client-neutral. Nay promote về master.

- **`skills/gtv-weekly-report/` 14 → 24 file.** Thêm 8 script: `fetch_period_data.py` (kéo số kỳ tháng/quý) · `period_analyze.py` (URL-level + độ phủ so BẢNG 1) · `bang1_parser.py` + `reconcile_totals.py` (2 trong 3 cổng kiểm số trước khi viết chữ) · `okrs_score.py` (chấm điểm OKRs khép quý) · `url_yoy_forensics.py` (truy nguyên URL sụt sâu so cùng kỳ — 4 nhóm A/B/C/D) · `build_pptx.py` (YAML → PowerPoint native: text box/bảng/chart/hyperlink thật) · `build_source_links.py` (registry link nguồn, resolve `gid` qua API, build FAIL nếu còn token `[[key]]` chưa resolve). Thêm 2 references: `period-report-format.md` (spec deck kỳ 8 section + 4 luật + 3 cổng) · `scripts-map.md` (bảng 15 script). `SKILL.md` + `build_deck.py` + `export-pdf.sh` lên bản mới.
- **`skills/gtv-project-okrs/` (MỚI, 3 file).** Giải bài "OKRs sống ở hai nơi" (Google Sheet team vs bản `.md` canonical trong instance): quy trình 5 bước, `references/okrs-review-lenses.md` (6 lăng kính review + luật merge KR + format HTML 5 màu), `scripts/okrs_sheet_diff.py` (chỉ ĐỌC sheet, không bao giờ ghi ngược). Master: 32 → **33 skill**.
- **Neutral hóa khi promote:** `joblisting_yoy_forensics.py` → **`url_yoy_forensics.py`** (cơ chế vốn generic theo `--source`, tên cũ mang tính lịch sử job site — đã cập nhật cross-ref ở SKILL.md, scripts-map, period-report-format); `okrs_score.py` lấy tên client từ `client_name` trong config thay vì hard-code; `build_pptx.py` header bảng blocker → "Người quyết (khách)"; `okrs_sheet_diff.py` bỏ default `--range-key`/`--workbook` (chuyển **required** — tab OKRs đổi giữa các kỳ và giữa client, bắt khai tường minh).
- **`_TEMPLATES/weekly-report-slides/` nhận 2 file mới + 1 bổ sung:** `PERIOD-DATA-CHECKLIST.md` (data team phải chuẩn bị cho kỳ tháng/quý — song sinh với checklist tuần) · `RUNBOOK-bao-cao-ky.md` (12 mục: 4 thứ phải có → kéo số → phân tích → 3 cổng kiểm → insights → registry nguồn → dựng deck → QA chống tràn → PowerPoint → spot-check → file-back → back-port khi client sửa tay → sự cố hay gặp) · `WEEKLY-DATA-CHECKLIST.md` thêm **§5 «Kích hoạt hệ»** (bảng 9 việc setup 1 lần cho instance mới: dựng workbook → dán ID → folder Drive → quyền GA4/GSC → chốt scope KPI → verify dry-run).
- **`_TEMPLATES/BAN-GIAO-TEAM.md` (MỚI, template cấp root).** Trước đây chỉ tồn tại dưới dạng file riêng của gói CareerViet; nay là template client-neutral: chuẩn bị máy, phân biệt email robot vs file chìa khóa, bảng ai-làm-gì (SEO Lead / Executive data / Account / Content), câu lệnh 3 nhịp báo cáo, luật sửa deck. `_TEMPLATES/README.md` cập nhật index.
- **Bảng GHI ĐÈ (mục 2.A) thêm nhóm `tools/`** — `sync-skills.sh` là infra, instance nhận qua migration.

**Instance nhận bản này cần biết:** `report-config.yaml` của instance phải khai khối `periods:` (cột `cur_col`/`prev_col` **tường minh**, không autodetect) trước khi chạy báo cáo kỳ đầu tiên; chưa có workbook thì làm `WEEKLY-DATA-CHECKLIST.md` §5 trước. Instance đang chạy script cũ tên `joblisting_yoy_forensics.py` → đổi lệnh sang `url_yoy_forensics.py` (CareerViet chưa nhận bản này, còn tên cũ cho tới lần migration kế).

### v2026.07.6 (2026-07-30) — Gói bàn giao team: tooling standalone + deck hướng dẫn + doc fixes

- **`tools/sync-skills.sh` (MỚI)**: đồng bộ `skills/` → 2 mirror bằng bash thuần cho bản STANDALONE (rsync + parity check; tự loại 2 skill claude-only khỏi `.agents/`). Luật ghi vào `AGENTS.md`: standalone chạy script này; trong workspace Vincent vẫn dùng `tools/sync-agent-skills.rb` root.
- **`GTV_SEO-Production_huong-dan-cai-dat_v1.html` (MỚI, root)**: deck 18 slide hướng dẫn cài đặt & sử dụng cho team — 2 track Claude Code/GPT Codex, MCP, chìa khóa robot, ngày đầu tiên, luật lõi, skill 3 tầng, SETUP 9 bước, vận hành báo cáo tuần/tháng CareerViet, 3 điều cấm. Copy kèm trong mọi gói phân phối.
- **`README.md`**: sửa drift "20 skill" → 32; thêm mục «Ngày đầu tiên» trỏ deck hướng dẫn. **`_TEMPLATES/README.md` (MỚI)**: index 21 template + 3 subfolder. **`.gitignore`**: thêm pattern file nặng (`*.zip`, `*.mp4`, PDF hợp đồng/samples).
- Kênh phân phối chốt (Vincent 30/07): **zip → Google Drive** (git local giữ trong gói, remote để trống — GitHub tính sau).
- **Vòng review chéo GPT Codex (30/07, findings M4-01→M4-04 — verdict CẦN-SỬA, đã vá cùng ngày)**: deck hướng dẫn ghi rõ path checklist tuần THEO GÓI (CareerViet `09-reporting/WEEKLY-DATA-CHECKLIST.md` · master `_TEMPLATES/weekly-report-slides/`) + ghi rõ `BAN-GIAO-TEAM.md` là file trong gói CareerViet; `_TEMPLATES/weekly-report-slides/WEEKLY-DATA-CHECKLIST.md` mục «AI tự lo» bỏ «export PDF» → «tự chụp từng slide soi lỗi» (luật HTML-only 23/07). Findings gốc: `Deliverables/GTV-SEO-Production-handoff/review-codex-2026-07-30.md` (workspace Vincent).


### v2026.07.5 (2026-07-27) — metadata `visual-semantic-seo` hợp lệ đa runtime

- `skills/visual-semantic-seo/SKILL.md`: sửa frontmatter YAML, rút description còn 829 ký tự và cô đọng bảng định tuyến reference; nội dung phương pháp, checklist E1–E12 và changelog không đổi.
- File chính còn 483 dòng, đạt gate dưới 500 dòng; root sync dựng lại mirror cho Claude Code và `.agents/skills` dùng chung bởi Codex/Antigravity.
- Instance đang hoạt động nhận đúng bản metadata này; không đụng client data, deliverable, registry hoặc checklist dự án.

### v2026.07.4 (2026-07-24) — tương thích cây PROJECTS với Codex/Antigravity

- **`AGENTS.md`**: bỏ giả định root workspace luôn nằm ở `../AGENTS.md`; runtime phải áp chuỗi `AGENTS.md` của ancestor. Cách này dùng được cho cả master `SEO Production/`, instance `PROJECTS/<client>/` và repo standalone.
- Khai báo đúng cả hai skill reporting chỉ có ở Claude Code: `gtv-client-report` và `gtv-weekly-report`. Codex/Antigravity chỉ làm draft thủ công theo template + luật trạm `09-reporting`, không giả lập skill và không gửi thẳng cho khách.
- Workspace root thêm lớp định tuyến `PROJECTS/AGENTS.md` + adapter `PROJECTS/CLAUDE.md`; đăng ký hai instance đang hoạt động (`careerviet`, `minh-tuan-mobile`) vào root skill manifest để sync/lint kiểm tra mirror riêng.
- Không thay đổi client data, deliverable, index hoặc cấu trúc workstream của instance.

### v2026.07.3 (2026-07-23) — gtv-weekly-report: 2 format TUẦN/THÁNG + rule carry-over + HTML-only

- **`skills/gtv-weekly-report/SKILL.md`**: thêm mục «Hai format deck — TUẦN vs THÁNG» (tuần = LEAN ~11 slide theo agenda catchup client: run-rate/KPI → what works → what fails+solution → task done → task next → blockers aging → new initiatives from GTV; tháng = đầy đủ ~26 slide + lớp MoM/OKRs quý/pattern 4 tuần, build khi khép tháng). Pha 3 bước 5 đổi: **KHÔNG export PDF** — HTML tự chứa là bản final, PDF chỉ khi Vincent yêu cầu rõ.
- **`skills/gtv-weekly-report/references/weekly-catchup-format.md` (MỚI)**: map 11 slide format tuần ↔ type builder ↔ nguồn data, lớp tháng cho format 26 slide, và **RULE CARRY-OVER** (Vincent 23/07/2026): task chưa done ở timeline OKRs/sheet tuần tự động chuyển plan tuần kế status «Chuyển tiếp» trừ khi Vincent điều chỉnh — build slide Task next week theo rule, kèm PIC in đậm, trình chốt cả danh sách không hỏi từng dòng.
- **`09-reporting/CLAUDE.md`** (Chế độ TUẦN): output CHỈ HTML; ghi 2 format + rule carry-over, trỏ về reference mới.
- **`scripts/build_deck.py`**: render `sow`/`next_week` hỗ trợ **bảng công việc 5 cột** (Hạng mục rowspan | Task cụ thể | PIC | Deadline | Tiến độ) khi rows có `hangmuc/pic/deadline`; fallback 2 cột giữ nguyên cho deck cũ. Spec trong `references/weekly-catchup-format.md`.
- Bối cảnh: client CareerViet yêu cầu weekly catchup meeting agenda 5 mục (23/07); bản deep 26 slide chuyển thành nhịp tháng. Áp cho mọi client dùng skill này.


### v2026.07.2 (2026-07-22) — Chế độ TUẦN: skill `gtv-weekly-report` + template slide tuần

> **Bổ sung 22/07 tối (round 3 Vincent):** slide-map luật #7-11 (ngôn ngữ senior-SEO không mật mã · mọi mục có TĂNG+GIẢM · top pages 20/chiều đủ Clicks/Pos WoW · blog 3 bài tiêu biểu/nhóm · deck editable); template `weekly-report-slides` nhúng khối INLINE EDIT (bấm E, localStorage, guard nav — đổi `EDIT_KEY` per deck) + ô Description bảng điền-tay 92px; `pv_movers.py` trả thêm cột intent/ngành/chủ đề/location; SKILL.md bước 2b.
>
> **Bổ sung 22/07 khuya (round 4 + 4b Vincent):** slide-map luật #12-15 — template có sẵn khối **DECK CHROME** (rail thumbnail «☰ Slides»/phím T + «▶ Present» fullscreen + deep-link `#n` hashchange; nút tự ẩn khi không rê chuột nên không dính PDF export; test Playwright PASS trên Chromium + WebKit) · action «Việc cần làm» phải xuống dòng từng ý dạng ul (cấm paragraph liền) · khối chữ cuối slide cấm chạm `.data-meta` (3 slide điển hình 1.1 Intent / 2.1 Apply / 2.2 Apply mặc định tách cặp bảng—nhận xét, soi PNG từng trang trước khi giao) · bảng nhóm Blog đủ Clicks + Pos (Pos dẫn xuất trọng số Imp từ CSV URL-level). Template: hàng SCOPE bảng «Cần client hỗ trợ» căn giữa dọc.
>
> **Bổ sung 23/07 (industrialize 80/20):** `scripts/build_deck.py` — dựng TOÀN BỘ deck từ `content.yaml` (schema: `references/content-schema.md`; 15 type slide, data-ref đổ số thẳng từ digest/movers/blog_groups/apply_groups, validate tự động; deck nhẹ ~220KB nhờ logo nhúng 1 lần) + `scripts/blog_groups.py` (Clicks pivot + Pos dẫn xuất trọng số Imp, offline 0 API) + `_TEMPLATES/weekly-report-slides/deck-skeleton.html` + `WEEKLY-DATA-CHECKLIST.md` (requirement data team chuẩn bị mỗi thứ Tư). SKILL.md Pha 3 đổi chuẩn: viết content.yaml → build_deck → export → soi PNG; viết HTML tay chỉ còn qua `type: manual`. Nghiệm thu: tái dựng W11 28 slide từ YAML — so PNG với bản tay: tương đương.

> **Bổ sung 23/07 (quy định Drive agency nhiều client):** `fetch_weekly_data.py` hỗ trợ `report_tuan.drive_folder_id` — Drive search khoanh trong folder client (share folder 1 lần cho service account → file mới tự kế thừa quyền, hết share từng tuần) + cảnh báo khi nhiều file trùng tên; schema config + `WEEKLY-DATA-CHECKLIST.md` thêm mục 0 «Quy định folder & tên file trên Drive» (1 folder/client · tên đúng `name_pattern` · workbook cố định giữ nguyên URL) + phân nhánh nguồn hình: tool đòi login (SpySERP) = team lưu PNG `02-raw/screenshots/manual/`, Looker = giữ link unlisted robot tự chụp.

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
- **35 skill** trong `skills/` + mirror `.claude/skills/` và `.agents/skills/` (`gtv-client-report` chỉ Claude Code).
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
| Tooling | `tools/` (`sync-skills.sh` — dựng lại mirror skill khi chạy standalone) |

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
