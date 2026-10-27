---
master_version: v2026.10.39
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

### v2026.10.39 (2026-10-27) — Skill mới `wp-xuat-ban-bai` và `anh-trong-bai`; `wp-dang-bai` 1.2 đọc web-profile

- **Vì sao:** đăng bài lên website cần nhiều hơn một lệnh đẩy: media trong bài, ảnh đại diện, khối bấm thử, link nội bộ sống, kiểm giao diện trên theme thật. Luật của từng site (link ngoài, chữ ký, màu, font) trước đây nằm rải trong chat và memory.
- **Thêm:** `skills/wp-xuat-ban-bai/` (Markdown humanize → HTML doc-kit, `kiem_bai.py` kiểm luật trước khi đăng, `kiem_render.mjs` render trên theme thật ở 1366 px và 390 px, mẫu `web-profile/_mau.json`). `skills/anh-trong-bai/` (media plan từ khung `[IMG-NN]`, sơ đồ SVG 7 kiểu có bản điện thoại, chụp trang nguồn có tô câu, ảnh AI có watermark, chèn media).
- **Sửa:** `wp-dang-bai` 1.2: `--site` nhận mọi mã site, đọc `web-profile.json` thay cho hằng số cứng, thêm `--profile`, `--featured-alt`; lấy slug, SEO title, keyword từ thẻ meta của file.
- **Pilot:** bài content-effort đăng nháp trên site mẫu GTV ngày 27/10, đủ 7 khung media, render đạt 2 cỡ màn hình.
- **Port sang instance:**
  1. GHI ĐÈ `skills/wp-dang-bai/`. Thêm `skills/wp-xuat-ban-bai/` và `skills/anh-trong-bai/`.
  2. Instance có đăng bài lên WordPress: chép `skills/wp-xuat-ban-bai/web-profile/_mau.json` thành `00-client-context/web-profile.json`, điền theo `skills/wp-xuat-ban-bai/references/web-profile.md`. Thêm skill ảnh đại diện mà profile khai ở `anh_dai_dien.engine`.
  3. Instance không đăng bài: chỉ làm bước 1.
  4. Cập nhật frontmatter `master_version` thành `v2026.10.39`.

### v2026.10.38 (2026-10-27) — Skill mới `wp-dang-bai`: đăng bài lên gtvseo.com, theaigrowth.io qua REST

- **Vì sao:** Vincent giao team đăng bài từ Claude Code lên 2 website công ty, giữ giao diện của bài blog tài liệu nội bộ (pages.dev).
- **Thêm:** `skills/wp-dang-bai/` (script Python stdlib `wp_publish.py`: doctor, push, media, trash; mu-plugin `doc-kit` cho site; bài mẫu `examples/bai-thu.html`). Bản sao cùng nội dung ở repo Content Production - GTV và - TAG.
- **Cài cho từng người:** thêm `WP_GTV_URL`, `WP_GTV_USER`, `WP_GTV_APP_PASSWORD` (và `WP_TAG_*` nếu đăng TAG) vào `.env` ở gốc repo. App password do SEO Lead hoặc Vincent cấp, mỗi người một chuỗi. Hướng dẫn: https://gtv-dao-tao.pages.dev/production/content/dang-bai-wordpress/
- **Instance:** không cần migration; `git pull` là có skill. Skill chỉ dùng cho 2 site công ty, không dùng cho site khách.

### v2026.10.37 (2026-10-27) — Repo này là bản gốc duy nhất của 29 skill; 4 skill GEO và báo cáo sinh từ master

- **Vì sao:** 37 skill có 2 bản gốc (master và repo này) và lệch nhau, nên mỗi lần nâng cấp chỉ vào một bản. Người duyệt chốt 27/10: gộp 29 skill về repo này, 4 skill sinh từ master bằng công cụ, master thêm lint chặn skill hai bản.
- **Gộp, giữ nguyên chức năng (19 skill):** backlink-plan, cro-audit, cro-measurement-plan, expert-case-study, okrs-gtv-tag-framework, semantic-html-optimization, site-migration-checklist, textlink-analyzer, traffic-plan, hreflang-planner, competitor-seo-gap-analysis, backlink-research, serp-clustering, image-seo-optimize, semantic-content-audit, seo-logfile-analysis. Riêng `local-seo-audit` 1.0.1, `map-pack-intelligence` 1.0.1, `schema-markup-generator` 1.0.3: dòng Output trỏ thư mục công đoạn theo ma trận M.
- **Hợp nhất nội dung của master (10 skill):**
  - `technical-seo-audit` 1.10.1: giữ 3 hàng định tuyến của repo này.
  - `seo-onpage` 1.8: Bước 5b Region Completeness, `references/kyle-roof-philosophy.md`, câu URL ngắn ở P1.
  - `internal-linking` 1.4.1: rubric Jev `link-purpose`, `link-external`, `evals/cases.yaml`.
  - `keyword-topic-url-mapping` 1.3.2: verdict QDP 01/08/2026 trong `qdp-gate.md`.
  - `visual-semantic-seo` 3.8.0: Phân việc model, Tự phản biện 7 mục; bỏ hệ số 3x/5x/10x và dẫn US7716225B1 cho chức năng trang (fact-fix); bảng patent chuyển sang `references/related-patents.md`.
  - `content-refresh` 1.3: tín hiệu T15 (AI-cited + stale), T14b.
  - `seo-drift-tracker` 1.3.0: `scripts/drift_tracker.py`, test, `references/cli.md`.
  - `programmatic-seo-builder` 1.2: Bước 3b guardrail AI-era, G2 non-commodity test, Phân việc model, Tự phản biện.
  - `topical-map-creation` 2.3: Phân việc model, Bước 0, Tự phản biện; mục GEO chuyển sang `references/geo-ai-search.md`.
  - `geo-fanout-research` 1.2: khối chấm nhanh QDP.
- **Sinh từ master bằng công cụ (4 skill, không sửa tay ở repo này):** `entity-seo-plan` 1.2.1, `geo-content-optimization` 1.5.1, `geo-tracking-prompt-selection` 1.6.1, `gtv-client-report` 1.4.2. Muốn sửa thì đề xuất sửa bản master theo `_REFERENCE/self-improving.md`.
- **Port sang instance:** GHI ĐÈ các thư mục skill trên trong `skills/`. Không có bước nào chạm site hay dữ liệu dự án. Cập nhật frontmatter `master_version` thành `v2026.10.37`.

### v2026.10.36 (2026-10-27) — Nâng 7 skill tốc độ, crawl và bảo mật; thêm 4 skill điều phối, công cụ theo dõi workflow, sổ lượt gọi Jev

- **Vì sao:** đợt chạy đêm 26–27/10 trên site agency mẫu (CDN chia vùng, CSS gọn theo trang, 24 workflow) cho bài học về tốc độ, crawl, bảo mật tài khoản CDN và cách điều phối nhiều lane. Người duyệt chốt 27/10. Số version dưới đây lấy từ dòng `version:` và mục Changelog đầu của từng `SKILL.md`.
- **wp-ucss 1.1.0:** `map_diff.py` thay đoạn heredoc trong `regen.sh` (cổng `MAX_LOST`, file `purge_paths.txt`). `qa_sau_giao.py` kiểm sau giao theo path × biến thể, link đã đổi, robots và canonical so baseline. Mẫu `site.json` thêm `swap_attr`. Eval 7 ca.
- **wp-pagespeed 1.14:** `fcp-guest-mode.md` thêm mục khách mới bị tải lại trang (rewrite `guest.vary.php`, mẫu `templates/guest-tap.php`). `checklist-theo-lop.md` thêm bảng "Đã A/B và không áp". Bước 3 thêm mục 11–12.
- **seo-logfile-analysis 1.4:** `scripts/kpi_html.py` tính KPI tỉ lệ HTML trong lượt Googlebot web. Mẫu số bỏ file hạ tầng. Có `--trust-xff` cho log sau CDN và cảnh báo khi mẫu số dưới 30. Bước 3 Tier C thêm cách đọc CSV Crawl Stats.
- **cdn-speed-setup 1.2:** `warm.py` gửi HTML với `Accept` có `image/webp` (cờ `--accept`), đúng với `origin-sau-cdn.md` §2. Thêm mục "Quyền hành động trên Cloudflare" và cách làm nóng đúng trạm bot dùng bằng ECS.
- **wp-security-hardening 1.8:** nhánh C và `references/ra-tai-khoan-cdn.md` rà Worker, route, token, thành viên, 2FA, audit log, SSL. Kiểm từ ngoài bằng UA trình duyệt và UA Googlebot. Có 8 bước khi secret bị lộ. Chưa có script đọc tài khoản.
- **web-qa-gate 1.3.1:** `_cdp.mjs` thêm `dnsRules()`: host tracking bị chặn thêm ở tầng DNS. Beacon gửi lúc đóng tab không đi qua `Network.setBlockedURLs`, nên Chrome headless trước đây làm lọt sự kiện thử vào GA4 của site sống. Test `tests/test_dns_block.py` chạy Chrome thật.
- **technical-seo-audit 1.10:** mục "Chọn skill theo triệu chứng": 11 triệu chứng, cách đo, skill bắt đầu. `evals/cases.yaml` thêm 4 ca định tuyến.
- **Bốn skill điều phối mới, bản sinh từ master:** `web-lane-orchestration` 1.2 (workflow nhiều lane trên site sống, chạy đêm từ phiên mới), `decision-page` 1.0.1 (trang HTML chờ Lead quyết, trả lời thành danh sách việc), `workstream-master-plan` 1.0.1 (sổ yêu cầu và master plan của workstream dài), `runtime-handoff` 1.3.1 (HANDOFF, bàn giao phiên, đổi runtime). Đầu mỗi `SKILL.md` có dòng ghi đây là bản sinh. Không sửa tay. Muốn đổi, đề xuất một câu theo `_REFERENCE/self-improving.md` vòng 2.
- **Tài liệu mới `_REFERENCE/luat-duyet-dieu-phoi.md`:** luật duyệt (quyền hành động, việc cần duyệt từng lần), luật sub-agent (chỉ khi Lead yêu cầu rõ, trần 2 agent cùng lúc trong mỗi phiên theo `.claude/settings.json` của repo, 6 agent mỗi workflow; effort theo model: Opus high, Sonnet và Haiku xhigh, mỗi dòng dùng bản mới nhất), luật HANDOFF (5 mục, dưới 60 dòng), luật đặt tên, mục "Khi Lead vắng". Bốn skill điều phối trỏ về file này. Khi file này vênh `CLAUDE.md`, `CLAUDE.md` thắng. `ORCHESTRATOR.md` thêm mục 4.1 trỏ tới 4 skill.
- **Tool mới:** `tools/wf-status.py` (lệnh `lint-script`, `tokens`, `result`, `slots`, `stale`; Python stdlib) và `tools/tests/test_wf_status.py`. `tools/shell-traps-macos.md` ghi các lệnh shell hay hỏng trên Mac và 2 dòng `~/.zshenv`. `tools/leak_scan.sh` dò secret trong file trước khi giao (skill `runtime-handoff` gọi).
- **tools/ai-assist:** `jev.py` ghi mỗi lượt có gọi API vào sổ `~/.cache/ai-assist/jev-ledger.jsonl` (đổi đường dẫn bằng `JEV_LEDGER`), thêm cờ `--label`. `jev_ledger.py` (mới) tổng hợp số lượt, lỗi và chi phí theo ngày và theo task: `python3 tools/ai-assist/jev_ledger.py [--since YYYY-MM-DD] [--label <chuỗi>]`. Sổ nằm ngoài repo, không commit.
- **Port sang instance:** THÊM 4 thư mục skill điều phối, `_REFERENCE/luat-duyet-dieu-phoi.md`, `tools/wf-status.py`, `tools/tests/test_wf_status.py`, `tools/shell-traps-macos.md`, `tools/leak_scan.sh`, `tools/ai-assist/jev_ledger.py`. GHI ĐÈ 7 thư mục skill còn lại, `tools/ai-assist/jev.py`, `ORCHESTRATOR.md` và mirror. Bước instance cần làm:
  1. Instance đã chạy job tái tạo `wp-ucss`: chép `map_diff.py`, `qa_sau_giao.py`, `regen.sh` mới vào thư mục làm việc của đợt, rồi chạy `regen.sh` một lần ở chế độ thử.
  2. Instance dùng CDN: làm nóng lại bằng `warm.py` mới để HTML có `Accept` WebP.
  3. Instance có `guest.vary` trong mu-plugin: đọc `fcp-guest-mode.md` mục khách mới bị tải lại trang. Mu-plugin trên server là config sống, xin Lead duyệt riêng trước khi đổi.
  4. Script `web-qa-gate` chạy trên site có GA4: dùng `_cdp.mjs` mới để chặn beacon ở tầng DNS.
  5. Mỗi máy của Lead: thêm 2 dòng vào `~/.zshenv` theo `tools/shell-traps-macos.md`. Syncthing không đồng bộ dotfile.
  6. Instance chưa có `HANDOFF.md` cho workstream nhiều phiên: tạo theo `_REFERENCE/luat-duyet-dieu-phoi.md` mục HANDOFF. Không cần làm gì với sổ Jev, `jev.py` tự tạo file khi chạy lượt đầu.
  7. Cập nhật frontmatter `master_version` của `MIGRATION.md` trong instance thành `v2026.10.36`.

### v2026.10.35 (2026-10-27) — CSS gọn theo trang (wp-ucss), bài học speed và crawl của một site OLS + LiteSpeed Cache

- **Vì sao:** site WordPress mẫu (OLS 1.8.1 + LiteSpeed Cache 7.9.1, CDN Bunny chia vùng) có file CSS gộp 0,96–1,48 MB chặn render. Đợt 26–27/10 tự dựng CSS gọn theo trang thay cho UCSS trả phí: PSI mobile trung vị 7 template 94 → 98, trang chủ LCP 2,9 → 2,3 s, FCP 2,0 → 1,4 s.
- **Skill mới `wp-ucss` 1.0.0:** chọn URL đại diện (`chon_url.py`), quét 4 biến thể `m`, `d`, `p`, `q`, sinh bằng engine Chrome, kiểm computed style A/B/A2 có lượt xác nhận, map theo (md5 file gộp, path), mu-plugin đổi `href`, deploy DRY rồi thật, purge 12 path mỗi lệnh, làm nóng, purge và làm nóng Bunny bằng bản WebP (`bunny_purge.py --warm`), job tái tạo launchd (`regen.sh`), kiểm khoảng hở critical CSS (`ccss_gap.mjs`). Rubric Jev `tools/ai-assist/tasks/ucss-diff.json` (chưa hiệu chuẩn, chỉ xếp thứ tự).
- **wp-pagespeed 1.13:** Bước 1 chọn URL bằng `chon_url.py`; Bước 3 thêm CSS gọn, 404 dò quét trả trước PHP (`references/ttfb-cache-trang.md` §4b), CDN không tách HTML theo Accept; checklist lớp 1 và lớp 5 thêm bẫy `-V` của `guest.vary`, Googlebot dùng bản `Accept: */*`, TBT tăng khi critical CSS kèm file gộp lớn, `.screen-reader-text` gây CLS.
- **Kiểm:** `wp-ucss/scripts/tests/run.sh` đạt mọi phần (cần css-tree 3.x; thư mục module khác đặt `UCSS_NODE_MODULES`). `skill_struct_check.py --moi` đạt. Chạy thật trên site mẫu: 66 path, 128 cặp bản `*/*` lệch 0.
- **wp-pagespeed 1.13.1:** `psi_run.py` cách lượt cùng URL + thiết bị `--min-gap` 60 giây và đo lại lượt trùng `fetchTime` (PSI trả kết quả đã lưu khi gọi lại quá sớm; 27/10 một lane báo "3 lượt" nhưng chỉ có 1). 162 ca test đạt.
- **wp-ucss 1.0.1:** `gen.mjs` lấy URL file gộp gốc trong `onerror` ở trang đã đổi sang CSS gọn. Bản 1.0.0 ghi hash null nên job tái tạo sinh lại các cặp đó mỗi lượt.
- **wp-pagespeed 1.13.2:** Bước 3 mục 8 thêm luật so md5 file gộp ở cả 4 biến thể `m`, `d`, `p`, `q` khi site đã có CSS gọn.
- **wp-ucss 1.0.2:** `verify.mjs` dùng chung hàm `combinedHref()` với `gen.mjs`; bản cũ bỏ qua mọi cặp đã đổi link và làm map mới mất path. `regen.sh` thêm cổng `MAX_LOST` (mặc định 3 path). Instance đã chạy job tái tạo: thay `gen.mjs`, `verify.mjs`, `lib-ucss.mjs`, `regen.sh` trong thư mục làm việc của đợt.
- **Port sang instance:** GHI ĐÈ `skills/wp-ucss` (mới), `skills/wp-pagespeed`, `tools/ai-assist/tasks/ucss-diff.json` và mirror. Instance dùng CDN Bunny điền `cdn_host`, `cdn_warm_ecs` trong `site.json` của đợt.

### v2026.10.34 (2026-10-26) — Kéo backup về máy không chép mode thư mục của server

- **Vì sao:** lần cài lịch kéo backup đầu tiên cho site khoá học mẫu (26/10) lỗi `fstatat: Permission denied`. Thư mục backup trên server mang mode 600 (root vẫn đọc được), và `rsync -a` chép mode đó về máy.
- **wp-security-hardening 1.7.1:** `templates/backup-tu-dong/backup_pull.sh` kéo bằng `rsync -rlt`, rồi `chmod -R u+rwX,go-rwx` thư mục đích. openrsync của macOS không có `--chmod`. Checklist mục 7 thêm bẫy này.
- **Kiểm:** kéo thật 2,7 GB từ server mẫu: 9 bản DB và 2 bản file, `verify_backup.sh` đạt. `test_sec_scripts.py` đạt.
- **Port sang instance:** GHI ĐÈ `skills/wp-security-hardening` và mirror. Máy đã cài lịch kéo bằng bản cũ: nếu thư mục đích báo lỗi quyền, chạy `chmod -R u+rwX` trên thư mục đó rồi chạy lại `backup_pull.sh` một lần.

### v2026.10.33 (2026-10-25, bổ sung 26/10) — Đợt dựng skill sau rà soát web 16–24/10

- **Vì sao:** rà 9 ngày làm web trên site agency mẫu và site khoá học mẫu (16–24/10) ra 26 đơn vị dựng mới hoặc nâng cấp skill. Người duyệt chốt 24/10. Bản này gồm 14 skill của repo, bản sao công cụ Jev, bảng kiểm tool và `.gitignore`.
- **Skill mới wp-ui-fix 1.0:** sửa lỗi giao diện site WordPress đang chạy. Truy nguồn CSS bằng `match.mjs --css` và `css_sources.sh`. Sửa theme có backup bằng `theme_patch.py`. Đo thang chữ bằng `type_probe.mjs` và `type_check.py`. Chụp phần tử và so trước, sau bằng `shot_el.mjs` và `so_sanh.py`. Có 3 reference và 47 test offline. Instance có thể tạo `00-client-context/ui-rules.md`. Thiếu file này thì skill dùng thang mặc định.
- **wp-pagespeed 1.12:** biến `WPS` cho đường dẫn script, Bước 0b đọc lộ trình site, parity staging bằng `diff -rq`, `BASELINE.md`. Script mới: `psi_decide.py`, `psi_cls_dump.py`, `lh_local.mjs`, `lam_nong.sh`, `ls_exclusions_check.py`, `psi_con_tru.py`, `fallback_faces.py`, `fa_subset/`, `img_variants.py`, `img_display_width.mjs`, `img_width_report.py`. `psi_run.py` chạy `--jobs 2`, có `--detach`, từ chối chạy tiền cảnh quá 8 phút. `psi_ab.py` tự gắn noindex, khoá ngưỡng, có `--split-bench` và `--apply`.
- **wp-staging-deploy 1.1:** `stg_env.sh`, `stg_tunnel.sh`, `stg_get.sh` (che chuỗi host, tunnel tự nối lại, giữ mã thoát của `SSH`). Bước 6 quét lộ bằng `stg_leak_check.sh`. Bước 3 kiểm trùng tên hàm. Thêm bẫy URL tuyệt đối và opcache.
- **wp-content-review-apply 1.6:** `apply.php` thêm op `text`, `fix`, `el_rm`, `el_restore`, field `usermeta` và `option`, `FAIL_ON_SKIP`. Script mới: `locate.php`, `doi_chieu.py`, `so_duyet.py`, `the_qa.py`, `check_cards.py`, `kiem_trang_duyet.mjs`, `mark_batch.py`, `seed_batches.py` và bộ dọn HTML hàng loạt. Luật "duyệt tới đâu áp tới đó" ở Bước 4. Trường có khối `qa`, chữ ngắn chạy humanizer chế độ lô. Reference mới `thao-tac-ghi.md`, `don-html-hang-loat.md`.
- **web-qa-gate 1.3:** hạng mục 13 tương tác (`interact_probe.mjs`: menu bấm thật, slider chạm thật), 14 bố cục và landmark (`landmarks.mjs`), 15 OG. Cờ mới `--cache both`, `--tabs`, `--resume`, `--sample`, `--plan`, `--page-timeout`. Thêm `chrome_cleanup.mjs`, checklist form gửi thật, chế độ cổng trước production, audit đầu workstream và kiểm độc lập.
- **wp-security-hardening 1.7:** `apply_server_block.sh` (backup md5, diễn tập, mã HTTP trước và sau, `rollback.sh`), `preflight_remote.sh`, `verify_backup.sh`. Sửa `backup_pull.sh`, `site-backup.sh`, `backup-cnf.php`: từ chối dump rỗng, dùng gzip khi thiếu zstd. Probe URL ngẫu nhiên phải trả 404. Reference mới `ap-config-song.md`, `va-os-php.md`, `xoa-an-toan.md`.
- **semantic-media 1.1:** sửa `minFont` null ở `diagram_render.mjs` (thêm `diagram_checks.mjs`). `diagram_body_check.py` so chữ sơ đồ với thân bài. Luật 8 kiểm người nói của video lời chứng thực. Luật 9 và `check --used` chặn ảnh trùng giữa các trang.
- **content-inventory-audit 1.2:** nhánh B đổi cây chuyên mục (`build_tax_plan.py`, `taxonomy_rollout.php`, `export_tax_redirects.php`, `references/cay-chuyen-muc.md`). Nhánh C vòng đời URL (`pick_target.py`, `wayback_cdx.py`, `chain_check.py`, `bo-bai.md` mục 4). 410 chỉ cho danh sách bỏ đã duyệt. Dump phải gồm mọi `post_type` và mọi `post_status`. Bản 1.2 (người duyệt chốt 26/10): chỉ 301 về bài cùng chủ đề, không có bài phù hợp thì 410. `pick_target.py` báo `loi` khi đích là chuyên mục, thẻ hoặc archive, vì 301 về trang chuyên mục bị Google coi là soft 404.
- **internal-linking 1.4:** 4 script stdlib có test offline: `the_link.py`, `link_code_audit.py`, `bridge_candidates.py`, `anchor_gsc.py`. Thêm `references/scripts.md` và Bước 4d.
- **seo-logfile-analysis 1.3:** `verify_googlebot.py` lọc dải IP trước rDNS, bỏ đuôi `googleusercontent.com`, mã thoát 0–3. `log_checks.py` kiểm uploads, redirect, 404 và 410 theo nhóm. Reference mới `aapanel-ols.md`.
- **technical-seo-audit 1.9:** reference `index-chuyen-muc-rank-math.md` và `gsc-ghi.md`. Script `index_probe.py`, `pagerank.py`, mu-plugin tạm `robots-public-test.php`. Checklist 3.6 thêm ngoại lệ phân trang giả.
- **wp-theme-build 1.1:** Bước 1b đo trang tham chiếu bằng `measure_ref.mjs`. `contrast.py` nhận chữ gradient. Reference mới `bang-mau-token.md`.
- **model-calibration 1.4:** lệnh `gold-sheet`, `gold-merge`, `pipeline`, `cosine --gold`. Cổng holdout: entry thiếu holdout ghi `status: draft` và `threshold: null`. Reference mới `phieu-gold-va-holdout.md`.
- **wp-paid-plugin-exit 1.2:** ACF → SCF bước 3 thêm bẫy SCF lọc `<script>` trong `the_field()`. Mu-plugin `allow_unsafe_html`. Số thẻ `<script>` và mã GTM giữa lượt ACF và lượt SCF phải trùng ở mọi URL.
- **tools/ai-assist:** `jev.py` thêm `--dry-run`, `--preflight-only`, `--no-preflight`, `--max-consecutive-errors`, `--min-image-side`, mã thoát 2 (input hỏng) và 3 (dừng sớm). Script tự đệm ảnh có cạnh ngắn dưới 320 px và chặn ảnh thiếu trước khi gọi API. `tasks/` chép thêm 8 rubric client-neutral, từ 17 lên 25 file. README thêm bảng cờ, bảng mã thoát và dòng `ui-type-align`.
- **tools/capabilities.md:** thêm `fonttools`, `lighthouse` và cột skill cho `wp-ui-fix`.
- **.gitignore:** chặn `02-raw/logfiles/*` vì log server chứa IP. Giữ `02-raw/logfiles/README.md`.
- **Sync mirror:** `tools/sync-agent-skills.rb` của workspace không chép `__pycache__`, `.pytest_cache`, `.pyc` vào mirror. Script standalone `tools/sync-skills.sh` của repo chưa đổi.
- **Kiểm:** test offline đạt ở cả 14 skill. Ví dụ: wp-ui-fix 47, internal-linking 36, wp-staging-deploy 36, technical-seo-audit 31, web-qa-gate 13, `jev.py` 56. Kiểm cấu trúc và client-neutral của `skill-creator` đạt cả 14 skill. Bằng chứng ngoài repo.
- **Port sang instance:** THÊM `skills/wp-ui-fix`. GHI ĐÈ 13 thư mục skill còn lại và mirror. Instance có rule 301 về chuyên mục: chạy `chain_check.py --terms` để liệt kê, rồi đổi đích sang bài cùng chủ đề hoặc 410 qua trang duyệt. GHI ĐÈ `tools/ai-assist/jev.py` và README. Chép rubric mới vào `tools/ai-assist/tasks/` bằng `cp -n`, để giữ rubric instance đã chỉnh. Script backup đã cài trên server và lịch kéo backup trên máy Lead vẫn là bản cũ. Cập nhật theo `wp-security-hardening` `references/ap-config-song.md`, có diễn tập, và xin duyệt riêng vì đây là config sống.

### v2026.10.32 (2026-10-24) — Model mặc định là Opus mới nhất, bài học đợt nhiều lane 23–24/10

- **Vì sao:** Vincent chốt 24/10: repo dùng Opus mới nhất, không ghim ID phiên bản. Đợt sửa nhiều lane trên site agency mẫu 23–24/10 gặp lỗi thật ở PageSpeed, ACF→SCF, ảnh gửi Jev, log OLS và ghi nội dung.
- **`.claude/settings.json`:** thêm `"model": "opus"`. Alias `opus` luôn trỏ tới bản Opus mới nhất. Effort giữ `high`.
- **wp-pagespeed 1.11:** backup theo version v0/v1, rollback về v0, cách ly file mới. Không bật A/B bằng tham số trong mu-plugin production. Tách lượt PSI theo `benchmarkIndex`. `checklist-theo-lop.md`: ảnh hero desktop trùng, preload Montserrat.
- **wp-paid-plugin-exit 1.1:** ACF→SCF bước 5–7: render-diff ≥350 URL có chuẩn hoá honeypot WPForms, md5 `get_fields()`, đếm admin, reset `acf_version` khi rollback, theo dõi ≥20 phút.
- **web-qa-gate 1.2:** `pad_image` thu ảnh về ≤0,8 MP và ≤1.568 px mỗi cạnh, đệm lên 320 px và tỉ lệ cao/rộng 0,3. Jev trả http_400 ngoài giới hạn này. `hang-muc.md` thêm §12 chữ dễ đọc.
- **wp-security-hardening 1.6:** `ung-cuu-su-co.md` §1: log web `.gz`, `log_health.py`, cột trạng thái khác nhau giữa các vhost OLS, log lỗi OLS.
- **wp-content-review-apply 1.5:** kiểm điều kiện ngày trong nguồn duyệt. Thẻ mới thay thẻ cũ thì rebase. Đánh `appliedAt` chỉ sau khi kiểm live.
- **seo-logfile-analysis 1.2:** script `log_health.py` đếm 4xx/5xx theo khung giờ, nhận cột từ dòng mẫu. **hreflang-planner 1.2:** mục 3d nút chuyển ngôn ngữ, không tự chuyển hướng theo IP hay Accept-Language.
- **Kiểm:** test offline `web-qa-gate` 13/13, `log_health.py` 3/3. `log_health.py` chạy trên 249.105 dòng log thật, khớp số đếm bằng awk. Bằng chứng ngoài repo.
- **Port sang instance:** GHI ĐÈ `.claude/settings.json` và 7 thư mục skill trên cùng mirror. Instance đã đổi `effortLevel` thì giữ giá trị của instance.

### v2026.10.31 (2026-10-21) — Bài học đo tràn, biến thể cache và object cache

- **Vì sao:** đợt tối ưu site agency mẫu 20–21/10 gặp lỗi thật. Phép đo tràn bỏ sót lỗi do `isMobile` và UA `HeadlessChrome`. Lượt PSI bằng `?utm_source=` ghi bản `noindex` vào cache URL sạch của trang chủ. Lệnh ghi Elementor xoá CSS toàn site.
- **web-qa-gate 1.1:** `browser_probe.mjs` không bật cờ `mobile` của CDP. `references/hang-muc.md` mục 1 thêm 6 bẫy đo tràn. Mục 9: canonical chỉ đọc một bản cache, kiểm 5 biến thể bằng `cache_variants.py`.
- **wp-pagespeed 1.10:** script mới `scripts/cache_variants.py` (robots, canonical, nhãn cache ở 5 biến thể của URL sạch). `psi_run.py` từ chối URL có `utm_*`, `fbclid`, `gclid`, `_ga`. `shot.mjs` không bật cờ `mobile` và ghi `vw`; `shot_cmp.py` so `scrollWidth` với `vw`. `checklist-theo-lop.md` lớp 1: biến thể cache, làm nóng, object cache, lsphp, RAM. Lớp 4: kết quả `font-display: optional`.
- **wp-content-review-apply 1.4:** `apply.php` xoá object cache trước khi purge trang, và sinh lại CSS Elementor của từng tài liệu thay cho `files_manager->clear_cache()`. Bước 6 thêm `cache_variants.py`. `references/ghi-an-toan.md` thêm luật SQL thô khi bật object cache, CRLF, staging clone cũ, nhiều phiên cùng ghi, rollback so md5.
- **Kiểm:** test offline `web-qa-gate` 13/13 đạt. Fixture local cho `browser_probe.mjs` và `shot.mjs`: bản cũ bỏ sót hoặc báo sai, bản mới đúng. `cache_variants.py` chạy trên server giả và 2 URL production chỉ đọc. `php -l apply.php` sạch.
- **Port sang instance:** GHI ĐÈ 3 thư mục skill trên và mirror. Baseline `shot.mjs` cũ của instance chụp lại bằng bản mới trước khi so.

### v2026.10.30 (2026-10-19) — Nối dữ liệu Ahrefs cho bộ backlink và đo trích dẫn AI

- **Vì sao:** các skill backlink và GEO ghi "dùng Ahrefs" nhưng không có lệnh đọc kết quả connector. Lượt thử trên site mẫu tìm ra nhịp link, verdict spam và KPI citation tính sai.
- **link-relevance 1.1:** nhánh backlink chấm T.T.T từ dữ liệu Ahrefs. Verdict KEEP, REVIEW, REJECT theo tín hiệu máy M1–M3. REJECT cần ít nhất 2 tín hiệu. Script `scripts/backlinks.py`, test `tests/test_backlinks.py`. Ngưỡng Theme đọc từ registry entry `backlink-theme` (`lo`, `hi`, `pass`).
- **backlink-research 2.2:** `scripts/bl_research.py` có 3 lệnh: `gap`, `anchors`, `velocity`. Thêm `references/ahrefs-mcp.md` (tool theo bước, unit, bẫy trần 250 dòng).
- **backlink-plan 1.3.1:** `scripts/plan_tools.py` có 3 lệnh: `velocity` (trung vị RD mới không spam còn sống, không dùng `refdomains-history`), `quickwins`, `check` (kiểm anchor plan, exit 1 khi FAIL). `quickwins` loại URL có chữ hoa trong path hoặc `%20` (breadcrumb Ahrefs ghi thành URL) khỏi bảng target.
- **textlink-analyzer 1.2.0:** `scripts/textlink.py` có 3 lệnh: `filter`, `enrich`, `allocate`. Tên đối thủ vào `neg`. Script cảnh báo term ngắn dễ trùng nghĩa sau khi bỏ dấu.
- **geo-tracking-prompt-selection 1.6:** lệnh `geo_kpi.py ahrefs` tách citation từ prompt khỏi AI Overviews theo từ khoá. KPI AI Citations không dùng `all_platforms`. Brand Radar cần addon riêng.
- **tools/capabilities.md:** fallback của `ahrefs` ghi rõ cách dùng connector của runtime.
- **gtv-client-report 1.1.1:** `references/data-paths.md` ghi trường Ahrefs cho KPI AIO theo từ khoá (`google_ai_overviews_keywords`), không dùng `all_platforms`.
- **Kiểm:** test offline của 5 skill đạt. Lượt thử chạy trên dữ liệu Ahrefs thật của site mẫu và 4 đối thủ.
- **Port sang instance:** GHI ĐÈ 6 thư mục skill trên, mirror và `tools/capabilities.md`. Instance muốn dùng ngưỡng Theme riêng thì hiệu chuẩn rồi thêm entry `backlink-theme` vào `00-client-context/model-calibration.json`. Không có entry thì script dùng ngưỡng mặc định.

### v2026.10.29 (2026-10-19) — Bước 0 kiểm tool cho 21 skill, chuẩn câu Bước 0

- **Vì sao:** việc chung 3 của chương trình lớp model yêu cầu mọi skill audit và build có "Bước 0 — kiểm tool". Lệnh kiểm cấu trúc của `skill-creator` đòi dòng ngay sau heading là câu mẫu chạy `tools/capabilities.py check --need`. 5 skill mới của v2026.10.28 viết lệnh trong code block nên trượt kiểm.
- **Thêm Bước 0 (21 skill):** wp-pagespeed, visual-serp-lab, link-relevance, site-vector-index, retrieval-lab, model-calibration, local-seo-audit, map-pack-intelligence, cro-audit, competitor-seo-gap-analysis, site-migration-checklist, visual-semantic-seo, semantic-html-optimization, entity-seo-plan, schema-markup-generator, programmatic-seo-builder, internal-linking, gtv-weekly-report, wp-security-hardening, wp-content-review-apply, image-seo-optimize. Skill có danh sách bước ngay sau heading nhận thêm heading "### Các bước". Skill không có heading quy trình nhận "## Quy trình" ngay trước phần các bước. `image-seo-optimize` đổi heading "Workflow 6 bước" thành "Quy trình 6 bước".
- **Đổi Bước 0 sang câu mẫu (5 skill):** wp-staging-deploy, wp-theme-build, wp-paid-plugin-exit, semantic-media, blog-interactive-tools.
- **Sửa script:** `semantic-media/scripts/media_match.py` tắt ghi bytecode trước khi import `svi.py`, để không sinh `__pycache__` trong `site-vector-index`.
- **Kiểm:** 103 khối Bước 0 trong workspace đạt lệnh kiểm cấu trúc. Mọi danh sách `--need` chạy được, không có id lạ.
- **Port sang instance:** GHI ĐÈ 26 thư mục skill trên và mirror. Không đổi script khác, không đổi template.

### v2026.10.28 (2026-10-19) — 5 skill WordPress và media mới, nâng cấp bảo mật, sửa trực tiếp, ảnh

- **Vì sao:** việc staging, deploy, dựng theme, bỏ plugin trả phí, media theo mục và công cụ trong bài đã chạy thật trên 2 site nội bộ 16–19/10 nhưng nằm rải trong thư mục dự án. Probe PHP trong `uploads` nhận cả 410 nên bỏ sót site thiếu rule.
- **Skill mới:**
  - `wp-staging-deploy` v1.0: làm mới staging, tunnel, gộp 3 phía có backup và lệnh rollback (`merge3.py`), regen CSS Elementor từng tài liệu, purge theo URL. Lượt thử dry trên server thật: plan trùng script cũ 15/15 file.
  - `wp-theme-build` v1.0: khung theme classic tự code, template khoá học, mẫu blog, form lead; `parity.py` kiểm ảnh (cả trang ≤3%, màn đầu ≤1%), mã HTTP và chữ.
  - `wp-paid-plugin-exit` v1.0: Elementor Pro sang widget free, ACF Pro sang SCF, Permalink Manager sang `permalink-uris.php` (xuất bản đồ bằng `pm_export.php`, xử lý tiền tố WPML). Converter chạy lại khớp 18/18 lượt đổi cũ.
  - `semantic-media` v1.0: `media_match.py` (EmbeddingGemma xếp video cho slot, kiểm luật plan), `diagram_render.mjs` (render và kiểm chữ sơ đồ), `watermark.py`, mẫu YouTube facade + VideoObject. Tái tạo top 8 cũ 83/83.
  - `blog-interactive-tools` v1.0: chèn shortcode trước heading neo với điều kiện MD5, rollback, mẫu 8 công cụ JS thuần. Phát lại khớp 8/8 vị trí.
- **Skill sửa:**
  - `wp-security-hardening` v1.5: chặn PHP trong `languages`, `upgrade` và biến thể path-info. Probe chỉ nhận 403.
  - `wp-content-review-apply` v1.3: chế độ sửa trực tiếp (`sua_truc_tiep.py`, nút E trên bản HTML của trang, xuất `edits` chuẩn NFC, `k#n` cho chữ lặp); bẫy mạng nội dung.
  - `image-seo-optimize` v1.2.2: phân vai trỏ sang `semantic-media`, `visual-serp-lab`. `wp-pagespeed` v1.9.1: trỏ sang `wp-staging-deploy`.
- **Tool:** `tools/capabilities.md` thêm dòng `ffmpeg` và thêm skill vào dòng `ssh`, `wp-cli`, `node`, `chrome`, `axe`, `pillow`, `gemma`, `gsc`.
- **Port sang instance:** THÊM 5 thư mục skill mới, GHI ĐÈ 4 thư mục skill sửa, `tools/capabilities.md` và mirror. Instance có site WordPress: kiểm lại probe bảo mật bằng `exposure_check.sh`.

### v2026.10.27 (2026-10-19) — Sửa sau kiểm độc lập đợt 2, áp quyết định Vincent, parser log OpenLiteSpeed

- **Vì sao:** kiểm độc lập đợt 2 tìm ra description quá 280 ký tự, cổng chưa có holdout, Bước 0 sai chỗ và tên khách trong master. Vincent chốt thêm luật gửi bản nháp cho Jev, vai trò 2 ngưỡng SERP và cách dùng định tuyến Gemma. Log thật của OpenLiteSpeed không parse được.
- **Quyết định Vincent (19/10):**
  - `content-quality-lab` v1.2.3: cờ `--own-site` cho `rewrite` và `claims --text`. Bản nháp chưa đăng của site chính đơn vị vận hành được gửi Jev. Bản nháp site khách không gửi Jev.
  - `serp-clustering` v1.1.1, `keyword-topic-url-mapping` v1.3.1, `semantic-content-network` v1.0.1: 4/10 URL chung để xếp keyword vào cụm khi lập plan, 6/10 để gộp 2 URL đang có.
  - `keyword-topic-url-mapping` v1.3.1, `query-processing-diagnosis` v1.3.1: định tuyến Gemma trên trang tiền chỉ là danh sách cần đọc (top-1 trùng URL Google 29,3%).
- **Sửa theo kiểm độc lập:**
  - `geo-answer-lab` v1.1.1, `topical-focus` v1.1.1, `technical-seo-audit` v1.8.2: description còn dưới 280 ký tự. `topical-focus` ghi rõ nhãn khoảng trống dưới 0,86 là ứng viên Claude đọc. `technical-seo-audit` bỏ tên khách thật khỏi master.
  - `hreflang-planner` v1.1.1: ngưỡng `sec_cov` < 0,82 về nháp, report không tự loại cặp.
  - `geo-fanout-research` v1.1.1, `geo-content-optimization` v1.4.1, `seo-drift-tracker` v1.1.1: Bước 0 nằm đúng mục "Quy trình", `python3` bắt buộc.
  - `seo-logfile-analysis` v1.1.1: `log_clusters.py` đọc log OpenLiteSpeed (dòng bọc nháy đơn, trường proxy trước IP). Thêm 6 bot: GoogleOther, Applebot, Meta, Bytespider, Amazonbot, CCBot. Log gtvseo.com 06–19/10 parse 48.803/48.803 dòng.
- **Port sang instance:** GHI ĐÈ các thư mục skill trên và mirror. Không đổi registry hay calibration-defaults.

### v2026.10.26 (2026-10-19) — Jev chấm luật viết theo đoạn, phân loại diff, cặp hreflang, logfile theo cụm chủ đề

- **Vì sao:** audit luật viết, phân loại diff sau deploy và kiểm cặp VI–EN vẫn do Claude đọc toàn bộ. Logfile chưa được đối chiếu với cụm chủ đề của site.
- **Skill sửa:**
  - `semantic-content-audit` v2.3: rubric Jev `writing-rules` chấm 4 luật theo đoạn (answer_first, fluff, vague_quantity, plural_no_example). AUC 0,83–0,90 nhưng không câu nào đạt cổng tự chốt 0,95: Jev chỉ xếp đoạn cho Claude đọc. Information gain dùng dấu hiệu effort của `content-quality-lab`, không dùng embedding.
  - `seo-drift-tracker` v1.1: code chốt diff tất định; Jev rubric `diff-impact` xếp "đáng kể" từ p 0,65 (46/47 đúng). Nhãn "vô hại" của Jev không dùng.
  - `seo-logfile-analysis` v1.1: gom URL bot đã crawl theo cụm của `topical-focus`, so với cụm lõi. Logfile chỉ xử lý trên máy, không gửi Jev. Chưa thử trên logfile thật.
  - `hreflang-planner` v1.1: EmbeddingGemma đo độ phủ section của cặp VI–EN. Cặp có `sec_cov` dưới 0,82 là không tương đương (28/29 đúng). Không có ngưỡng nhận: Claude đọc phần còn lại.
- **Tool:** `tools/capabilities.md` thêm skill vào dòng `jev`, `numpy`, `gemma`, `bs4`.
- **Port sang instance:** GHI ĐÈ 4 thư mục skill trên, `tools/capabilities.md` và mirror. Registry của instance hiệu chuẩn theo skill `model-calibration`.

### v2026.10.25 (2026-10-19) — Đo phủ subquery theo section, bỏ ngưỡng 0,80/0,90, phát hiện intent dịch chuyển

- **Vì sao:** ngưỡng 0,80/0,90 lấy từ bge/AirOps không phân biệt được trang được AI trích (39,6% so với nền 34,2% trên dữ liệu site mẫu). Chấm biến thể và mức phủ subquery vẫn do Claude tự chấm.
- **Skill sửa:**
  - `geo-fanout-research` v1.1: `scripts/fanout_cover.py` chấm từng subquery với từng section bằng EmbeddingGemma. So tương đối trong cùng top 10: AUC dev 0,674, holdout 0,683. Không có ngưỡng "đã phủ" tuyệt đối: Claude ra verdict.
  - `geo-content-optimization` v1.4.0: bỏ ngưỡng 0,80/0,90, đọc ngưỡng từ registry. Chưa có ngưỡng thì ghi "chưa hiệu chuẩn, Claude đọc".
  - `content-refresh` v1.1: `scripts/intent_shift.py` đo độ lệch của trang so với tâm top 3 SERP. Độ lệch tương quan với vị trí GSC (Spearman 0,545, n = 25). Chưa có ngưỡng REWRITE: Claude đọc top 3 SERP.
- **Tool:** `tools/capabilities.md` thêm skill vào dòng `gemma`, `numpy`, `ahrefs`. `tools/ai-assist/calibration-defaults.json` thêm `geo-fanout-coverage` và `geo-variant-margin`.
- **Port sang instance:** GHI ĐÈ 3 thư mục skill trên, `tools/capabilities.md`, `tools/ai-assist/calibration-defaults.json` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.24 (2026-10-19) — Title theo pixel, gom keyword trước bằng Gemma, định tuyến query → URL

- **Vì sao:** công cụ cũ báo title bị cắt ở 580 px, quá chặt so với SERP thật. Gom cụm kéo SERP cho mọi cặp keyword. Định tuyến query → URL làm tay.
- **Skill sửa:**
  - `seo-onpage` v1.5.0: `scripts/serp_pixel.py` đo title và meta theo pixel (Arial 20 px, thiếu Pillow thì dùng bảng `arial_widths.json`). Mốc cắt title đo trên SERP đã lưu là 688 px, đúng 138/140 holdout. Phần cụm thiếu và cụm GSC trỏ sang `ngram-semantic-gap`.
  - `serp-clustering` v1.1: EmbeddingGemma gom trước. Cặp có cosine dưới 0,90 là chắc khác cụm, không kéo SERP (holdout 0/186 sai). Không có ngưỡng chắc cùng cụm: gộp vẫn do SERP quyết.
  - `keyword-topic-url-mapping` v1.3 và `query-processing-diagnosis` v1.3: định tuyến query → URL qua `retrieval-lab route`; `query-processing-diagnosis` có `scripts/gsc_route.py`, query GSC chỉ xử lý trên máy.
- **Tool:** `tools/capabilities.md` thêm skill vào dòng `pillow`, `gemma`, `numpy`. `tools/ai-assist/calibration-defaults.json` thêm entry `serp-clustering-prefilter`.
- **Port sang instance:** GHI ĐÈ 4 thư mục skill trên, `tools/capabilities.md`, `tools/ai-assist/calibration-defaults.json` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.23 (2026-10-19) — N-gram, mạng nội dung, kiểm kê bài, khoảng trống chủ đề, viết lại an toàn

- **Vì sao:** workstream site mẫu 15–19/10 có nhiều script rời cho N-gram, mạng nội dung (SCN) và dọn danh mục. Query GSC từng được gửi cho Jev, trái luật "Jev chỉ nhận nội dung công khai".
- **Skill mới:**
  - `ngram-semantic-gap` v1.0: `ngram.py` 7 lệnh. Cấp site và cấp GSC đếm cụm 1–3 tiếng, cấp trang 2–4 tiếng (Vincent chốt 19/10).
  - `semantic-content-network` v1.0: `scn.py` 6 lệnh, checklist SCN đủ 6 việc, gộp chỉ sau kiểm SERP.
  - `content-inventory-audit` v1.0: `inventory.py` 5 lệnh và 2 script WP-CLI. Jev `category-pick` từ 0,9 tự ghi, 0,6–0,9 Claude đọc, dưới 0,6 người quyết. Luật bỏ bài: nháp + 410/301.
- **Skill sửa:**
  - `technical-seo-audit` v1.8.1: Bước 0; nguồn link hỏng (`link_sources.py`, `find_sources.php`); schema khớp nội dung hiển thị (`schema_visible.py`, rubric `schema-visible`); nhánh GSC chỉ gửi Jev chữ trang, không gửi query.
  - `geo-tracking-prompt-selection` v1.5: đo mốc và đo lại ngày 14, 30, 60 (`geo_kpi.py`).
  - `topical-focus` v1.1: khoảng trống chủ đề so với đối thủ (`competitor_titles.py`, `topical.py gap`), cosine EmbeddingGemma.
  - `geo-answer-lab` v1.1: nhất quán mô tả entity (`entity_desc.py`, rubric `entity-desc`).
  - `content-quality-lab` v1.2.1: lệnh `rewrite` (rubric `rewrite-keep`); `claims --text` không gửi Jev chữ nháp.
  - `web-qa-gate` v1.0: Bước 0 đặt danh sách id trong nháy đơn.
- **Tool:**
  - `tools/ai-assist/jev.py` dừng khi trường khai trong `must_be_empty` của rubric có dữ liệu. `tasks/gsc-cannibal-pair.json` khai `shared_queries`.
  - `tools/ai-assist/README.md`: `gsc-intent-match` không dùng với dữ liệu GSC.
  - `calibration-defaults.json` thêm 6 entry: `schema-visible`, `gsc-cannibal-pair` chế độ chữ, `topical-gap`, `entity-desc`, `rewrite-keep` ×2.
- **Port sang instance:** GHI ĐÈ 9 thư mục skill trên, `tools/ai-assist/{jev.py,README.md,calibration-defaults.json,tasks/gsc-cannibal-pair.json}`, `README.md`, `CLAUDE.md` và mirror. Registry `00-client-context/model-calibration.json` của instance giữ nguyên; instance mới hiệu chuẩn theo skill `model-calibration`.

### v2026.10.22 (2026-10-19) — Cổng kiểm sau khi ghi lên site, chặn claim, kiểm tool ở Bước 0

- **Vì sao:** đợt 15–18/10 trên site mẫu gặp lỗi tràn ngang bị che, form không khởi tạo ở 768 px, GTM gửi hit thật lúc chụp, staging thiếu plugin của production. Audit 17/10 thấy 3 phiên bản câu hoàn phí và nhiều số lệch bảng fact. Agent hay chạy việc khi máy thiếu tool.
- **Skill mới:** `web-qa-gate` v1.0: `qa_gate.py run` kiểm 11 hạng mục (tràn ngang 3 bề rộng, axe, focus, form, tracking, plugin, HTTP, redirect, canonical, schema, Jev `ui-visual`), ra `report.json` + `report.md`. Chặn GA/GTM/Meta khi QA. Form mặc định chỉ kiểm cấu trúc; gửi thật cần `--submit-live` + `WEB_QA_SUBMIT_LIVE`, production cần duyệt từng lượt. Jev `ui-visual` chưa có câu đạt ngưỡng: Claude xem ảnh.
- **Skill sửa:** `content-quality-lab` v1.1: lệnh `quality.py claims` 3 lớp (regex; Jev `claim-guard` 2026-10-19.2; bảng fact: cụm cấm + EmbeddingGemma + Jev `fact-match` 2026-10-19.2). Cần `facts.json` của chủ site và cổng trong registry.
- **Tool mới:** `tools/capabilities.md` (bảng 29 tool: id, lệnh kiểm, cách cài, fallback, skill dùng), `tools/capabilities.py` (`check --need 'a,b?'`, `list`, `key`, `gws-auth`; không in giá trị key), `tools/tests/test_capabilities.py`. Skill audit và build gọi lệnh này ở "Bước 0 — kiểm tool". Đặt danh sách id trong nháy đơn, vì zsh coi "?" là ký tự glob.
- **Luật:** `CLAUDE.md` §0 thêm bước tự chấm plan theo checklist "Bản tốt nhất phải có" của skill trạm; §4 ghi `capabilities.py`.
- **Tool:** `tools/ai-assist/calibration-defaults.json` thêm 6 cổng nháp `claim-guard` và `fact-match`.
- **Port sang instance:** GHI ĐÈ 2 skill trên, `tools/capabilities.*`, `tools/tests/test_capabilities.py`, `tools/ai-assist/calibration-defaults.json`, `CLAUDE.md` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.21 (2026-10-19) — Bỏ chuẩn đếm số không theo Semantic SEO

- **Vì sao:** Vincent yêu cầu rà mọi chuẩn trong skill và checklist ngày 19/10/2026. Các quota dưới đây không có nguồn Koray hay Google, hoặc đếm keyword thay cho attribute và ngữ cảnh. Checklist giờ chấm theo attribute, Central Entity và ngữ cảnh của đoạn.
- **Checklist onpage** (`02-raw/knowledge/sop/08-onpage-checklist.md`, cheat-sheet `ws06-onpage-il.md`, skill `seo-onpage` v1.4.3 + `references/p-series-checklist.md`):
  - P18 bỏ quota 2–4 link .edu/.gov. Bài nêu tên nguồn trong câu chứa claim (`internal-linking` link-js D6). Link ngoài chỉ đặt khi người đọc phải mở trang đó, dạng D5.
  - P17 bỏ quota 5-10 link mỗi bài và luật anchor khớp Title đích. Anchor là seed query hoặc biến thể của trang đích.
  - P16 bỏ keyword ở 100 chữ cuối và trong H2. P6 bỏ luật H2 chứa keyword chính.
  - P3, P8 bỏ ngưỡng ~70%. P8 chấm theo attribute MANDATORY của consensus top 10.
  - P14 bỏ quota bold. P19 đặt tên file theo nội dung ảnh. P20 bỏ ngưỡng 8-15 từ của alt.
  - T3-P1 bỏ ngưỡng 110% facts. T3-P5 bỏ density. T3-P6 chỉ dùng Flesch cho tiếng Anh.
- **Internal link** (`sop/03-internal-linking.md`, `sop/11-publish-wp.md`, `06-onpage-internal-link/CLAUDE.md`, `_TEMPLATES/internal-link-plan.md`, skill `internal-linking` v1.3.1): bỏ quota 2-5 link tới sibling và 5-10 link mỗi bài. Bài link tới sibling khi đoạn có ngữ cảnh chung.
- **Tier 1, Tier 2** (`sop/06-self-checklist/`): bỏ quota 1-2 câu hỏi tu từ mỗi section. Link plan của content team bỏ luật anchor khớp title và "Main tối đa 0-2 link", thay bằng `link-placement` (Main chỉ MC1–MC5).
- **Skill khác:** `geo-content-optimization` v1.3.3 bỏ keyword ở 100 chữ cuối. `visual-semantic-seo` v3.7.1 ghi rõ goldmine factor chấm title candidate, bỏ quota nhắc brand 5-7 lần, bỏ Flesch ≥60 cho tiếng Việt, bỏ số từ cố định theo funnel, xoá ví dụ số liệu GTV không có nguồn. `image-seo-optimize` v1.2.1 bỏ ngưỡng 8-15 từ của alt. `backlink-plan` v1.2.1, `textlink-analyzer` v1.1.1, `ws07-offpage.md`, `_TEMPLATES/gate-offpage-decision.md` đổi nhãn "LSI" thành "đồng nghĩa/biến thể".
- **Dạng mã của CTA (Vincent chốt chiều 19/10):** `internal-linking` v1.3.2. Ngữ cảnh quyết định dạng mã. CTA hợp ngữ cảnh giữ link thật (D1). Link JS (D3) chỉ cho link giữ lại để tăng chuyển đổi ở vị trí ngữ cảnh không cần link, hoặc nút tới trang noindex. Sửa `link-js.md` §2 (3 bước chọn), `link-placement.md` dòng MC4, `06-onpage-internal-link/CLAUDE.md` dòng dạng mã.
- **Filter trang danh mục ecommerce (Vincent chốt chiều 19/10):** `internal-linking` v1.3.3 thêm `link-js.md` §7 theo phân tích faceted navigation của Koray. Filter có demand làm trang đích, link thật. Filter không demand và sắp xếp dùng checkbox hoặc button, không sinh URL mà Google thấy. Link sản phẩm, phân trang, breadcrumb giữ link thật. `technical-seo-audit` v1.8.1: mục 3.7 checklist trỏ tới §7. Instance ecommerce (minh-tuan-mobile) áp khi chạy link plan hoặc audit trang danh mục.
- **Chưa đổi, chờ Vincent quyết:** trần ~12 fact mỗi trang của `semantic-content-writing` (Vincent duyệt 22/08), "≥3 EAV/100 từ", luật burstiness 3 loại câu mỗi đoạn, P5 H1 60-70 ký tự, P11 "synonyms ≥3-4", T2-P2 "60% above fold". `06-onpage-internal-link/WP-PUBLISH-KIT_upgrade-spec_v1.md` B4 còn ghi "Validate alt 8-15 từ" (mức warning).
- **Port sang instance:** GHI ĐÈ `02-raw/knowledge/sop/` (03, 06, 08, 11), `02-raw/knowledge/cheat-sheets/` (ws06, ws07), `06-onpage-internal-link/CLAUDE.md`, `_TEMPLATES/internal-link-plan.md`, `_TEMPLATES/gate-offpage-decision.md`, 7 skill trên và mirror. QC report cũ giữ nguyên. QC mới chấm theo checklist mới. Không đổi `index.md`, deliverable.

### v2026.10.20 (2026-10-19) — Dạng mã của link: link thật hay link JS

- **Vì sao:** Vincent chốt 19/10/2026 cách code link theo 2 site của Koray (morethanpanel.com, sutliffstout.com, kiểm mã nguồn 9 trang). Link chủ đề và link tới trang cần xếp hạng giữ `<a href>`. Nút chuyển đổi tới trang không cần xếp hạng, link phụ lặp ở header/footer và link ngoài làm bằng chứng dùng link JS (onclick). Trích nguồn trong thân bài nêu tên nguồn bằng chữ, không đặt link.
- **Skill sửa:** `internal-linking` v1.3: thêm `references/link-js.md` (mã D1–D6, 9 luật bắt buộc gồm giữ đường crawl, không dùng dạng lai, bàn phím, đo lường, staging), Bước 4c, cột `Dạng mã` trong link plan (`references/link-plan-template.md`), 3 anti-pattern. `link-placement.md` và `anchor-rules.md` thêm dòng trỏ luật mới.
- **Luật trạm:** `06-onpage-internal-link/CLAUDE.md` thêm 1 dòng ĐƯỢC/KHÔNG ĐƯỢC và cột `Dạng mã` ở Vòng tự kiểm bước 4.
- **Chưa đổi:** P18 của `seo-onpage` (2–4 link ngoài mỗi bài) vênh với D6, chờ Vincent chốt. Repo chưa có rubric Jev `link-purpose`, `link-external`: Claude gắn mục đích theo `link-js.md` §2.
- **Port sang instance:** GHI ĐÈ `skills/internal-linking` và mirror (`.claude/skills/`, `.agents/skills/`), `06-onpage-internal-link/CLAUDE.md`. Link plan đang làm dở: thêm cột `Dạng mã` cho dòng chưa đặt link. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.19 (2026-10-19) — Ảnh trong bài và màn đầu của trang

- **Vì sao:** Đợt C của lớp model. Pilot trên site mẫu đo ảnh và màn đầu bằng Jev ảnh và EmbeddingGemma ảnh, có gold gán mù:
  - Ảnh: điểm gộp p `alt_matches` + 2 × cos ảnh–alt gắn cờ alt không tả ảnh, đúng 42/44 ca trên gold 80 ảnh. Jev `fits_section` ở ngưỡng 0,7 đạt precision 98,3%.
  - Màn đầu: Jev đúng 95–100% trên gold 85 cặp cho 7 đặc điểm. Riêng `answer_visible` dự báo trang được AI trích trong cùng pool (AUC 0,644). 7 đặc điểm còn lại chưa có tín hiệu.
- **Skill mới:** `visual-serp-lab` v1.0: `visual.py images`, `fetch`, `embed`, `jev-in`, `pairs`, `media` (cổng `alt-score`, `image-fit`), `shoot`, `layout` (rubric `first-screen`). Rubric Jev `image-fit` và `first-screen` 2026-10-19.1.
- **Tool:** `tools/ai-assist/calibration-defaults.json` thêm cổng `first-screen` (8 câu) và `image-fit` `fits_section`. Không có default cho `alt-score`: thang cos ảnh–chữ khác theo site.
- **Port sang instance:** GHI ĐÈ skill trên, `tools/ai-assist/calibration-defaults.json` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.18 (2026-10-19) — Độ khớp anchor và trang đích

- **Vì sao:** Đợt C của lớp model. Pilot trên 3.123 link nội bộ của site mẫu kiểm độ khớp anchor với 2 nguồn:
  - Định tuyến GSC: margin Gemma của "anchor: đoạn" dự báo link trỏ đúng URL Google chọn cho query bằng anchor, AUC trong cụm 0,91.
  - Gold 130 link gán mù: điểm gộp Jev + Gemma đạt AUC 0,95 trên holdout mới. Rubric cũ `link-placement` chỉ đạt 0,82 cho việc này.
- **Skill mới:** `link-relevance` v1.0: `links.py prepare` (code gắn cờ đích lỗi, trang chuyên mục, anchor trùng query GSC, một anchor nhiều đích; margin Gemma), `sample` (phiếu gold mù), `validate`, `decide` (cổng `anchor-score`). Rubric Jev `anchor-target` 2026-10-19.1.
- **Skill sửa:** `model-calibration` v1.3: `cosine --grid LO:HI:STEP` cho điểm ngoài dải 0,50–0,995.
- **Tool:** `tools/ai-assist/calibration-defaults.json` thêm cổng `anchor-score` 0,52.
- **Port sang instance:** GHI ĐÈ 2 skill trên, `tools/ai-assist/calibration-defaults.json` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.17 (2026-10-19) — Độ tập trung chủ đề, dấu hiệu effort của trang, khối chữ lặp

- **Vì sao:** Đợt C của lớp model. Pilot trên site mẫu kiểm từng chỉ số với kết quả thật trước khi đưa vào skill.
  - Dấu hiệu "số đo từ dự án thật" do Jev gán dự báo trang được AI trích trong cùng pool tìm kiếm: AUC 0,73.
  - Khoảng cách tới tâm site không dự báo hiển thị khi đã khử độ dài bài, nên `topical-focus` chỉ dùng để đọc cơ cấu chủ đề và gán bài vào cụm.
  - Information gain đo bằng embedding không có tín hiệu, nên đã bỏ.
- **Skill mới (2):**
  - `topical-focus` v1.0: `topical.py map` (tâm site, bán kính, cụm KMeans có sàn kích thước, trang lệch tâm, trang bằng chứng tách riêng), `selftest` (cổng gán cụm từ tiêu đề + H2), `plan` (gán bài dự kiến vào cụm).
  - `content-quality-lab` v1.0: `quality.py prepare`, `validate`, `report` (rubric Jev `content-effort` 2026-10-19.4, so trang mình với trang được trích cùng pool), `template` (passage gần trùng giữa các trang, ngưỡng `passage-dup`).
- **Skill sửa:** `model-calibration` v1.2: `proxy --control` (Spearman riêng phần), chế độ `auc` (AUC trong từng nhóm, ghi registry), lưới ngưỡng cosine 0,01.
- **Tool:** `tools/ai-assist/calibration-defaults.json` thêm cổng `content-effort` (original_data 0,75 · first_hand 0,85).
- **Port sang instance:** GHI ĐÈ 3 skill trên, `tools/ai-assist/calibration-defaults.json` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.16 (2026-10-19) — Lớp model cho SEO: index vector, hiệu chuẩn, câu trả lời AI, truy xuất

- **Vì sao:** Các workstream trước tự embed và tự đặt ngưỡng ở từng việc. Ngưỡng không có bằng chứng theo site, và chỉ số mô phỏng chưa được kiểm với kết quả thật. Pilot trên site mẫu (19/10): Jev chấm câu trả lời AI đạt 94–96% ở cổng confidence; định tuyến query → URL bằng embedding trùng URL Google chọn 75,6%, baseline từ khoá 49,9%.
- **Skill mới (4):**
  - `site-vector-index` v1.1: `extract.py` tách page, section, passage, anchor; `svi.py` dựng index, query, centroid, cặp gần trùng, so 2 store.
  - `model-calibration` v1.1: `calibrate.py` hiệu chuẩn nhãn Jev (ngưỡng theo lớp, cổng confidence), ngưỡng cosine, kiểm proxy bằng Spearman theo nhóm + bootstrap. Registry theo site ở `00-client-context/model-calibration.json`.
  - `geo-answer-lab` v1.0: thu câu trả lời AI, regex + vị trí bằng code, rubric Jev `ai-answer-brand` v3, GLM trích câu phản đối, báo cáo brand × engine.
  - `retrieval-lab` v1.0: `retrieval.py` xếp passage theo query, định tuyến query → URL so với GSC, kiểm proxy bằng AUC.
- **Tool mới:** `tools/ai-assist/glm.py` (GLM Flash chỉ trích câu nguyên văn). `tools/ai-assist/calibration-defaults.json` thêm cổng ai-answer-brand v3.
- **Infra:** `.gitignore` thêm `03-audits/_vector-index/`.
- **Knowledge pack:** `sop/06-self-checklist/tier-1-geo.md` GE-26 thêm cách xử lý khi AI nghi ngờ vì brand tự xếp hạng: giữ bài top list, viết khách quan + EEAT, giải nghi ngờ bằng offsite consensus (GE-28…32). Thêm 1 dòng anti-pattern. Port: GHI ĐÈ file này.
- **Port sang instance:** GHI ĐÈ 4 skill, `tools/ai-assist/`, `.gitignore` và mirror. Instance tạo `00-client-context/model-calibration.json` khi hiệu chuẩn lần đầu. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.15 (2026-10-19) — CLS do critical CSS thiếu font và mục lục chờ JS

- **Vì sao:** Sau đợt đổi font và tắt plugin dựng trang trên site mẫu, CLS desktop bài viết lên 0,53. Ba nguyên nhân: critical CSS dựng trước khi đổi font, LiteSpeed gom `<style>` chứa `@font-face` vào file tải async, mục lục Fixed TOC chờ JS mới vào luồng trang.
- **Skill sửa:** `wp-pagespeed` v1.8: `checklist-theo-lop.md` lớp 5 thêm 2 bẫy critical CSS; lớp 6 thêm mục lục Fixed TOC và cách thử CSS sửa CLS bằng CDP `Fetch`.
- **Port sang instance:** GHI ĐÈ `skills/wp-pagespeed` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.14 (2026-10-18) — Kết quả A/B font trên PSI, plugin còn bật sau khi đổi theme

- **Vì sao:** Đợt tối đa điểm tiếp theo trên cùng site: A/B trên PSI cho thấy các cách chỉnh font không giảm CLS mà còn đổi lấy LCP. Sau cutover, một plugin mục lục còn bật chèn danh sách thô vào mọi bài; staging tắt plugin này nên không lộ.
- **Skill sửa:**
  - `wp-pagespeed` v1.7: `psi_ab.py build` gộp trang của nhiều spec. `do-dac.md` đọc CLS từ JSON khi A/B, kiểm tính năng máy PSI bằng `console.error`. Lớp 4 ghi kết quả A/B font (tên `local()` bold khớp, chia face theo độ đậm, preload, `font-display: optional`).
  - `site-migration-checklist` v1.3: so plugin đang bật giữa staging và production; kiểm plugin front-end bằng DOM; quét `<style>`, `<script>`, ảnh hotlink trong nội dung cũ.
- **Port sang instance:** GHI ĐÈ 2 skill trên và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.13 (2026-10-18) — CLS do JS đổi bố cục, font dự phòng trên PSI, ảnh blog, công cụ đo CLS

- **Vì sao:** Vincent nhận xét 18/10/2026: 3 trang khoá học và trang blog chưa tối ưu xong. Đo đủ trang con tìm ra CLS 0,92 ở trang thanh toán, ảnh PNG 944 KB ở một bài. Bài học đã chạy thật trên production một site WordPress.
- **Skill sửa:**
  - `wp-pagespeed` v1.6: Bước 1 đo mọi trang con của template. Bước 3 kiểm CLS mà PSI gán cho font. Lớp 3 bản 720w cho hero, logo, `sizes` ảnh thân bài, ảnh đại diện WebP giữ OG. Lớp 4 stack font thiếu face dự phòng. Lớp 6 trạng thái trang trong `<head>`, forced reflow bằng `ResizeObserver`. Lớp 7 TBT trang chuyển đổi. Script mới `cls_trace.mjs`, `featured_webp.sh`; tài liệu cho `psi_ab.py`, `gtm_delay_check.mjs`, `templates/gtm-delay-loader.php`.
  - `wp-security-hardening` v1.4: bẫy `context` mới của vhost OpenLiteSpeed không kế thừa header bảo mật và Basic Auth.
  - `geo-content-optimization` v1.3.1, `technical-seo-audit` v1.7.1: ngoại lệ `/llms.txt` cho audit của PSI, không tính là đòn bẩy GEO.
  - `cro-measurement-plan` v1.2: kiểm GTM bị hoãn, trigger click tự động bỏ lỡ cú click đầu.
- **Port sang instance:** GHI ĐÈ 5 skill trên và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.12 (2026-10-18) — Hoãn GTM có hẹn giờ, hạng mục "Duyệt web bằng tác nhân"

- **Vì sao:** Vincent yêu cầu 18/10/2026 tối đa TBT và hạng mục "Duyệt web bằng tác nhân" của PSI, duyệt hoãn GTM ("2s hoặc khi có thao tác, hoặc bạn thấy cái nào ổn"). Bài học đã chạy thật trên production một site WordPress.
- **Skill sửa:** `wp-pagespeed` v1.5:
  - `references/checklist-theo-lop.md` lớp 7: hoãn 2 s không có tác dụng, cách chọn mốc theo lúc Lighthouse dừng ghi trace, nạp ngay cho URL quảng cáo và trang chuyển đổi, bẫy `cdp.mjs` tự cuộn. Lớp 5: bẫy axe với `content-visibility`.
  - File mới `references/agentic-browsing.md`.
  - `scripts/psi_run.py` thêm `--categories`.
- **Port sang instance:** GHI ĐÈ `skills/wp-pagespeed` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.11 (2026-10-18) — Nghiệm thu đợt 2: đo lại lượt chậm, tắt plugin thừa, 2 công cụ mới

- **Vì sao:** Vincent yêu cầu 18/10/2026: tắt plugin chấm sao còn sót sau khi đổi theme, và cập nhật skill từ việc đã làm trong phiên.
- **Skill sửa:**
  - `wp-pagespeed` v1.4: `references/do-dac.md` thêm luật đo lại khi một URL có từ 2/3 lượt chậm, so trước và sau trong cùng buổi, mỗi cột báo cáo một công cụ, grep key trong evidence. Script mới `scripts/deploy_theme_files.sh` (chép file theme lẻ có backup, lint PHP, owner, purge). `references/tool-call-thua.md` thêm 2 dòng.
  - `wp-security-hardening` v1.3: `references/checklist-hardening.md` mục 4 thêm quy trình tắt plugin hết chức năng và luật cách ly theme, plugin không dùng; mục 7 thêm bẫy plist `&amp;`, `date -j`. Mẫu mới `templates/backup-tu-dong/cai-lich-pull-mac.command`.
  - `site-migration-checklist` v1.2: `references/wp-tu-quan.md` thêm kiểm plugin front-end sau khi đổi theme, mục 5 mới "Sau khi ổn định" (cách ly theme cũ). Mục "Bẫy đã gặp" thành mục 6.
- **Port sang instance:** GHI ĐÈ `skills/wp-pagespeed`, `skills/wp-security-hardening`, `skills/site-migration-checklist` và mirror. Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.10 (2026-10-18) — Tốc độ đợt 2 và siết server của site WordPress thứ hai

- **Vì sao:** Vincent duyệt "làm full" đợt tốc độ theme và bảo mật server ngày 18/10/2026, và cho tự nâng cấp skill từ bài học trong phiên. Bài học đã chạy thật trên production.
- **Skill sửa:**
  - `wp-pagespeed` v1.3 (`references/checklist-theo-lop.md`): cache trình duyệt 1 năm và luật đổi tên ảnh; bản 640w cho ảnh màn hình đầu và bẫy lightbox đọc `currentSrc`; `local()` nào khớp trên máy đo PSI, họ dự phòng Roboto cho Android, CLS do chữ đổi dòng; thứ tự `unicode-range` vi sau latin-ext; `content-visibility` cho trang dài và cách tắt khi nhảy `#mục`; forced reflow của thanh tiến độ cuộn.
  - `wp-security-hardening` v1.2: checklist chặn web `mu-plugins/`, HSTS ở vhost, backup tự động; bẫy `bind-address` của aaPanel, tắt pure-ftpd init.d, `tar` mã 1 với `pipefail`, phần việc panel để chủ site làm. Mẫu mới `templates/backup-tu-dong/`.
- **Port sang instance:** GHI ĐÈ `skills/wp-pagespeed`, `skills/wp-security-hardening` và mirror (`.claude/skills/`, `.agents/skills/`). Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.9 (2026-10-18) — Vị trí internal link: đúng ngữ cảnh, ưu tiên supplementary content, bám topical map

- **Vì sao:** Vincent yêu cầu 18/10/2026: internal link và contextual bridge chỉ đặt ở đúng ngữ cảnh, ưu tiên supplementary content, chỉ đặt ở main content khi thật sự cần, bám topical map (root → seed → node) và mô hình topic cluster; bổ sung vào skill và luật trạm, dò bằng Jev. Luật rút từ audit 161 link trên một site WordPress thật.
- **Skill sửa:** `internal-linking` v1.2: thêm `references/link-placement.md` (5 trường hợp được đặt link ở main content MC1–MC5, bảng quan hệ topical map → vùng, cách xác định main và supplementary content, kiểm hàng loạt bằng Jev), Bước 4b, 2 cột `Vùng` và `Quan hệ map` trong link plan (`references/link-plan-template.md`).
- **Tool:** rubric mới `tools/ai-assist/tasks/link-placement.json` (3 câu `zone`, `fit`, `need`); `tools/ai-assist/README.md` §4 thêm dòng ngưỡng.
- **Luật trạm:** `06-onpage-internal-link/CLAUDE.md` thêm 1 dòng ĐƯỢC/KHÔNG ĐƯỢC và mục kiểm vị trí ở Vòng tự kiểm bước 4.
- **Port sang instance:** GHI ĐÈ `skills/internal-linking` và mirror (`.claude/skills/`, `.agents/skills/`), `tools/ai-assist/README.md`, `06-onpage-internal-link/CLAUDE.md`; THÊM `tools/ai-assist/tasks/link-placement.json`. Link plan đang làm dở: thêm 2 cột mới cho dòng chưa đặt link. Không đổi `index.md`, deliverable.

### v2026.10.8 (2026-10-18) — Bài học đợt nghiệm thu tốc độ và đổi theme site WordPress thứ hai: font, tracking, đổi tên ảnh, đưa trang tĩnh vào WordPress

- **Vì sao:** Vincent duyệt 18/10/2026: đưa bài học đã chạy thật khi đổi theme một site WordPress (cutover, đưa 13 trang landing tĩnh vào WordPress, đổi tên 271 ảnh, nghiệm thu PSI) vào master, viết chung cho mọi dự án.
- **Skill sửa:**
  - `wp-pagespeed` v1.2: lớp 4 bỏ luật preload font, thêm bẫy `document.fonts.load()` trong `<head>` (PSI chờ ~2,35 s mới vẽ), bẫy font dự phòng `local('Arial')` trên PSI, quy trình tự host Google Fonts; lớp 7 thêm bảng đánh đổi khi hoãn GTM; `references/do-dac.md` mục 3 A/B trên PSI, cách đọc LCP mô phỏng có GTM, lượt chậm ngẫu nhiên; `references/tool-call-thua.md` thêm 7 dòng. Script mới `gfonts_selfhost.py`, `font_same.mjs`, `gtm_inventory.py`.
  - `image-seo-optimize` v1.2: Mode D đổi tên ảnh đã đăng (`references/doi-ten-anh-da-dang.md`, `templates/mu-plugin-301-anh.php`, `scripts/anh_cach_ly.sh`); luật tên riêng viết đủ.
  - `site-migration-checklist` v1.1: `references/wp-tu-quan.md` (đưa trang tĩnh vào WordPress giữ URL, switch có rollback tự động, bẫy OpenLiteSpeed giữ `.htaccess`, kiểm giờ đầu).
  - `schema-markup-generator` v1.0.2: `references/rank-math-wp.md` (filter `rank_math/json_ld`, node Article, Person mồ côi, `primaryImageOfPage`, ảnh OG theo ID).
- **Repo content đi kèm:** Content Production bản vá 18/10/2026 sửa luật tên file ở skill `media-brief` cho khớp `image-seo-optimize`.
- **Port sang instance:** GHI ĐÈ `skills/wp-pagespeed`, `skills/image-seo-optimize`, `skills/site-migration-checklist`, `skills/schema-markup-generator` và mirror (`.claude/skills/`, `.agents/skills/`). Không đổi `index.md`, deliverable, template, SOP.

### v2026.10.7 (2026-10-17) — Bộ skill WordPress có quyền server: tốc độ, bảo mật, ghi nội dung qua trang duyệt + nhánh GSC API

Vincent duyệt 17/10: đóng gói quy trình đã chạy thật trên 2 site WordPress (16–17/10/2026) thành skill dùng cho mọi dự án có quyền SSH + WP-CLI vào server của site. Skill viết chung, không gắn site cụ thể; thông tin riêng của từng site nằm trong hồ sơ server của instance.

- **Skill mới:**
  - `wp-pagespeed` v1.1: PSI trung vị 3 lượt, mô phỏng Chrome cho staging có Basic Auth, chẩn đoán và sửa theo 7 lớp có A/B, ảnh chụp so chức năng, rollback. 12 script (`psi_run.py`, `psi_table.py`, `perf_probe.mjs`, `probe_table.py`, `shot.mjs`, `shot_cmp.py`, `fontmap.mjs`, `ccss_gen.mjs`, `webp_gen.py`, `htaccess_webp.py`, `templates.php`, `_chrome.mjs`) + mẫu mu-plugin ưu tiên ảnh LCP.
  - `wp-security-hardening` v1.1: ứng cứu sự cố (IOC, sàng file checksum → scanner → EmbeddingGemma → Jev → Claude đọc, cách ly không xoá, gỡ mã tiêm không tạo revision) và rà định kỳ. Script `exposure_check.sh`, `persistence.sh`, `sitecheck.sh`; mẫu `mu-plugin-security.php`; checklist theo lớp có bảng lệnh cho OpenLiteSpeed, Apache, Nginx.
  - `wp-content-review-apply` v1.1 (CHỈ Claude Code): trang duyệt Duyệt/E (artifact có database, mẫu `templates/trang-duyet.html`) → `plan.py` → `apply.php` chạy thử rồi ghi bằng WP-CLI → `verify.py`. Chặn đổi slug khi site không có bảng redirect Rank Math; purge theo plugin cache đang có.
- **Skill sửa:** `technical-seo-audit` v1.7 (nhánh GSC 90 ngày qua API, `references/gsc-90-ngay.md`; bảng phân vai trỏ sang 3 skill mới); `seo-onpage` v1.4.2 và `internal-linking` v1.1.1 (bước ghi lên site qua `wp-content-review-apply`).
- **Tool mới:** `tools/ai-assist/` (`jev.py`, `emb.py`, `scan_files.py`, 10 rubric trong `tasks/`, README có bảng ngưỡng đã hiệu chuẩn) và `tools/gsc/gsc.sh` (GSC API qua OAuth của `gws`). Key Jev đặt ở `.agent-secrets/.env` của repo (đã gitignore). Thiếu key hoặc venv EmbeddingGemma thì skill để Claude đọc thay và ghi giới hạn.
- **Template mới:** `_TEMPLATES/wp-server.md` (hồ sơ máy chủ WordPress → `00-client-context/wp-server.md`), tổng 38 template. Hồ sơ chỉ ghi tên biến secret, không ghi giá trị.
- **Sửa theo:** `CLAUDE.md` §4 (số template, skill, tool) và §11 (dự án có quyền server dùng `wp-content-review-apply` thay kit publish), `README.md`, `COMMANDS.md` (lệnh `pagespeed <site>`, `rà bảo mật <site>`, `ghi lên site <đợt>`), `SYNC.md` §8, `tools/sync-skills.sh` (thêm skill claude-only), `_REFERENCE/runtime-workstream-matrix.md` (hàng Audit, Onpage & IL), `_REFERENCE/folder-map.md`, `03-audits/technical/README.md`, `_TEMPLATES/README.md`, `00-client-context/CLAUDE.md` (thêm `wp-server.md` vào Output của trạm).
- **Port sang instance:** GHI ĐÈ `skills/technical-seo-audit`, `skills/seo-onpage`, `skills/internal-linking` và mirror; THÊM `skills/wp-pagespeed`, `skills/wp-security-hardening`, `skills/wp-content-review-apply` và mirror (`wp-content-review-apply` không vào `.agents/skills/`), `tools/ai-assist/`, `tools/gsc/`, `_TEMPLATES/wp-server.md`; GHI ĐÈ các file sửa theo ở trên (`CLAUDE.md` có phần riêng của instance thì chỉ thêm đúng các dòng mới). Instance có quyền server: tạo `00-client-context/wp-server.md` cùng người vận hành. Không đổi `index.md`, deliverable.

### v2026.10.6 (2026-10-13) — Offpage: gate QA link trước khi đăng (SOP 10 v1.3) + textlink-analyzer v1.1.0

Vincent duyệt 13/10: đưa gate kiểm vị trí đặt link của Dejan Petrovic (2026) vào quy trình offpage, sau đợt ingest Clippings 10/2026 của wiki Semantic SEO.

- **SOP 10 v1.3** (`02-raw/knowledge/sop/10-offpage-process.md`): §2 thêm luật handoff 6 "Gate QA link trước khi đăng" cho guest post, niche edit, textlink báo đặt trong thân bài. 6 bước: vị trí ở đỉnh link desire, có link khác ra nguồn thật, đúng 1 trong 10 mục đích, trang đích mạnh nhất, anchor khớp cách host viết, phép thử mù. Người viết hoặc SEO Executive chấm, SEO Lead Project duyệt batch; chưa đạt 6/6 thì sửa bài trước khi gửi nhà cung cấp. Link sidebar, footer, trang chủ giữ tier cũ và ghi rủi ro vào risk log. Không đổi tier, timeline, đo lường.
- **Skill `textlink-analyzer` v1.1.0:** thêm Bước 5b chấm gate QA; bảng plan thêm cột `Vị trí đặt` và `Gate QA`; link sidebar ghi `n/a (sidebar)` và đưa rủi ro vào Caveats.
- **Port sang instance:** GHI ĐÈ `02-raw/knowledge/sop/10-offpage-process.md`, `skills/textlink-analyzer/` và mirror (`.claude/skills/`, `.agents/skills/`). Không đổi `index.md`, deliverable, template.

### v2026.10.5 (2026-10-12) — Skill chẩn đoán Query Processing cho bộ keyword cam kết

Vincent duyệt 12/10: đóng gói quy trình của đợt chẩn đoán 10 dự án (10/2026) thành skill dùng lại cho gate #22, audit #24, #29, và bàn giao kết quả cho team content.

- **Skill mới:** `skills/query-processing-diagnosis` v1.2. Đọc hạng SpySERP (CSV export dấu `;` hoặc `,`, một hay nhiều file, hoặc JSON chuẩn hoá) bằng median các lần chạy hợp lệ, gom query template, URL Google chọn, SERP, trang thật, ma trận 8 trạm, topic ưu tiên, kế hoạch 2 tuần. Đầu ra: JSON + deck HTML + hồ sơ + file bàn giao content `<CLIENT>_qp-handoff-content_v<N>.md`. Quy trình chuẩn 8 pha, một điểm dừng hỏi Lead, ngân sách 25–35 tool call mỗi dự án. Thiếu mốc so sánh 4 tuần thì dừng (không còn trạng thái "Đang lan" giả); project một domain có lần chạy mới nghi thiếu thì hỏi Lead. Script đóng gói trong skill: `qp_ranks.py` (bo, runs, table, terms), `qp_scaffold.py` (JSON nháp có sẵn mọi số), `qp_build.py` (check + verify số với bảng hạng + dựng + quét bản web + bàn giao content + audit trong một lệnh), `qp_render.py`, `site_check.py`, `audit.py` + `cdp.mjs` (audit cần Node ≥22 và Chrome, tuỳ chọn). Checklist QC QP-01…QP-18 (P0 8) nằm trong skill.
- **Folder mới:** `03-audits/ranking/` (README + nơi lưu chẩn đoán). **Template mới:** `_TEMPLATES/qp-intake.md` (phiếu đầu vào Lead điền trước khi gọi agent) và `_TEMPLATES/qp-chan-doan.md` (hồ sơ), tổng 37 template. `03-audits/ranking/README.md` là hướng dẫn cho Lead: chuẩn bị máy, export SpySERP, điền phiếu, câu lệnh, nhận gì, sau khi nhận.
- **Sửa theo:** `CLAUDE.md` §4 (folder map, số template và skill), `README.md`, `COMMANDS.md` (lệnh `chẩn đoán QP <client>`), `_REFERENCE/runtime-workstream-matrix.md` (hàng Audit và Keyword research), `_REFERENCE/folder-map.md`, `_REFERENCE/project-sync.md` (chẩn đoán QP trong danh sách dữ liệu chia sẻ; giữ giống bản ở repo content), `03-audits/README.md`, `03-audits/CLAUDE.md` (Input/Output, vòng tự kiểm mục 5, luật nạp skill), `_TEMPLATES/README.md`, cheat-sheet `02-raw/knowledge/cheat-sheets/ws03-audit.md`.
- **Repo content đi kèm:** Content Production bản vá 12/10/2026 kéo `03-audits/ranking/*.md` qua `project_sync.py` và dùng file bàn giao ở research, outline, update (`_REFERENCE/query-processing.md` của repo content). Instance SEO cần commit và push file bàn giao để repo content kéo được.
- **Port sang instance:** GHI ĐÈ `skills/query-processing-diagnosis` và mirror, `_TEMPLATES/`, `_REFERENCE/project-sync.md`, các file sửa theo ở trên (`03-audits/CLAUDE.md` có phần riêng của instance thì chỉ thêm đúng các dòng mới); THÊM `03-audits/ranking/README.md`. Không đổi `index.md`, không đổi deliverable. Instance đã có chẩn đoán QP làm tay (ví dụ đợt 10/2026 lưu ở workspace GTV): giữ nguyên, lần chẩn đoán sau dùng skill.

### v2026.10.4 (2026-10-03) — Instance website nội bộ (GTV, TAG): dòng Entity + biến thể setup

Vincent duyệt 03/10: mở 2 instance cho website gtvseo.com và theaigrowth.io.

- **Luật entity:** `CLAUDE.md` §1 thêm ngoại lệ duy nhất cho instance website TAG; `10-client-management/CLAUDE.md` hàng cấm số 4 đổi thành "nhãn theo dòng `Entity`".
- **Template:** `index.md` bảng A thêm dòng `Entity` (mặc định GTV SEO Agency).
- **Setup:** `SETUP.md` mục 1.1 (biến thể website nội bộ: không hợp đồng, KPI từ OKR công ty, ghi chú #1/#12/#30/#32/#33).
- **Port sang instance:** GHI ĐÈ `CLAUDE.md`, `10-client-management/CLAUDE.md`, `SETUP.md`. Instance client cũ không cần thêm dòng `Entity` (thiếu dòng = GTV SEO Agency). Không đổi knowledge pack, skill, tool.

### v2026.10.3 (2026-10-02) — Onpage: MX nâng cấp định dạng (chấm riêng) + batch report dạng bảng nhiệt HTML

Vincent duyệt 02/10. Đi cùng bản vá Content Production 02/10 (đợt 2): fork content có luật chọn định dạng media và brief video, khối tương tác; trạm 06 là nơi đề xuất nâng cấp cho trang đã có.

- **Trạm 06, mục mới "Nâng cấp định dạng (MX)":** 6 item MX1–MX6 (sơ đồ quy trình, bảng so sánh, biểu đồ số liệu, screenshot/video thao tác, video + transcript + VideoObject, khối tương tác có bảng tĩnh dự phòng). Chấm riêng, điểm `MX x/y`, không cộng vào /23 · /31 · /39, không phải gate, không chặn `done`. SEO chỉ tự làm phần trình bày lại nội dung đã có; cần claim, số liệu, lời đọc mới thì chuyển fork content; khối tương tác đi qua trạm 13 CRO (`ux-feature-brief.md`).
- **Template:** `_TEMPLATES/onpage-batch.md` thêm luật chấm số 7 và mục 7 (bảng MX).
- **Tool mới:** `tools/onpage_report_html.py` đọc batch report `.md`, dựng `<report>.view.html`: bảng nhiệt URL × item (sắp xếp theo điểm, lọc theo item FAIL), item rớt nhiều nhất, bảng MX, bảng AX. Chỉ dùng thư viện chuẩn. `.gitignore` thêm `*.view.html`.
- **Sửa theo:** `06-onpage-internal-link/CLAUDE.md` (hàng ĐƯỢC/KHÔNG ĐƯỢC, vòng tự kiểm bước 7, mục MX), `06-onpage-internal-link/README.md`, `COMMANDS.md` (2 lệnh), `_REFERENCE/runtime-workstream-matrix.md` (ô checklist hàng Onpage & IL).
- **Chưa đổi:** knowledge pack. `sop/08-onpage-checklist.md` giữ nguyên P-series và AX; MX ở trạng thái thử nghiệm, đủ dữ liệu batch thì Vincent quyết việc đưa vào sop/08 ở kho gốc.
- **Port sang instance:** GHI ĐÈ `06-onpage-internal-link/CLAUDE.md`, `06-onpage-internal-link/README.md`, `_TEMPLATES/onpage-batch.md`, `tools/onpage_report_html.py` (mới), `COMMANDS.md`, `_REFERENCE/runtime-workstream-matrix.md`, `.gitignore`. Batch report đang chạy: thêm mục 7 khi chấm MX, không cần sửa các mục đã có.

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
| WS infra | `README.md` + **`CLAUDE.md` + `AGENTS.md` (nội quy trạm)** của MỌI workstream folder (`00-client-context/` → `12-feedback-lessons/`) + `03-audits/qc/README.md` + `03-audits/ranking/README.md` |
| Config | `config/` (`mcp.json.example`) |
| Tooling | `tools/` (`sync-skills.sh` — dựng lại mirror skill khi chạy standalone · `content_sync.py` · `project_sync.py` · `onpage_report_html.py`) |

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
