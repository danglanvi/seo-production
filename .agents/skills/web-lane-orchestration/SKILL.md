---
name: web-lane-orchestration
description: "Dựng và chạy workflow nhiều lane sửa website đang chạy (WordPress, Shopify, Next.js): chia lane theo tài nguyên, khoá, cổng staging, kiểm độc lập, một vòng sửa, theo dõi và cứu lane treo. Dùng khi Lead yêu cầu rõ chạy workflow hoặc sub-agent cho nhiều việc trên site sống."
metadata:
  version: "1.2.1"
---

# web-lane-orchestration — nhiều lane sửa site sống trong một workflow

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

Skill này biến danh sách việc đã duyệt thành script Workflow nhỏ. Mỗi lane làm một nhóm việc trên tài nguyên riêng, theo một BRIEF tối đa 3 KB. Một agent kiểm độc lập từng lane, rồi lane có lỗi production được đúng một vòng sửa. Nguồn v1.0: 7 script workflow chạy thật trên site agency mẫu ngày 22–24/10/2026 và mục "Bẫy đã gặp" của `Deliverables/GTV-Brand/GTV-Website/HANDOFF.md`. Nguồn v1.1: đợt rà transcript 16–24/10 (`Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-lane-orchestration_bo-sung_v1.md`, 13 mục Lead duyệt).

Skill chỉ chạy khi Lead yêu cầu rõ workflow hoặc sub-agent cho task hiện tại (luật `_REFERENCE/luat-duyet-dieu-phoi.md` mục "SUB-AGENT — CHỈ KHI LEAD YÊU CẦU RÕ"). Nếu không có yêu cầu đó, làm tuần tự trong phiên và vẫn áp `references/luat-lane.md`.

## Khi nào dùng

- Từ 3 việc đã duyệt trở lên trên một site sống, các việc đụng tài nguyên khác nhau, và Lead bảo chạy workflow.
- Audit chỉ đọc nhiều mảng rồi gom thành một plan có phản biện (mẫu C).
- Workflow đang chạy bị treo và cần dựng lại phần còn lại.
- Không dùng khi: chỉ có một việc (dùng thẳng skill chuyên môn), việc chưa được duyệt, hoặc chỉ ghi chữ qua trang duyệt (dùng `wp-content-review-apply`).

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Danh sách việc đã duyệt, kèm lời duyệt nguyên văn có giờ hoặc file quyết định | Tin của Lead, file quyết định, HANDOFF của workstream | Hỏi. Lane không có nguồn duyệt thì không ghi |
| Thư mục workstream có `HANDOFF.md` mục "Bẫy đã gặp" | Workstream | Tạo HANDOFF theo luật `_REFERENCE/luat-duyet-dieu-phoi.md` trước khi dựng |
| Quyền vào site: SSH alias, CLI hoặc token trong `.agent-secrets/` | Lead, runbook của site | Dừng và báo |
| Nền tảng: WordPress, Shopify, Next.js | Site | Hỏi |
| Giờ chạy: ban ngày hay ban đêm | Lead | Mặc định ban ngày. Ban đêm hoặc khi Lead vắng nhiều giờ: đọc `references/chay-dem.md`, chạy từ phiên mới |
| Model từng lane | `references/chon-model.md` | Theo bảng trong file đó |

## Phân việc model

Bảng vai → model ở `references/chon-model.md`, luật gốc ở `_REFERENCE/luat-duyet-dieu-phoi.md`.

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Claude Sonnet | Lane chỉ đọc, lane áp thẻ và sửa có checklist, agent kiểm lane thường | Dùng, effort xhigh |
| Claude Opus | Lane hạ tầng, theme, template, mu-plugin, config sống, viết chữ mới; agent kiểm lane `core` và kiểm cuối đợt; plan mẫu C | Dùng, effort high |
| Jev | QA ảnh và chữ trong lane (`ui-visual`, `chu-dinh`), phân loại user-agent lạ số lượng lớn, cổng tất định trước agent kiểm | Dùng trong task của lane, có ngân sách USD. Claude đọc lại mọi mục Jev gắn cờ |
| EmbeddingGemma 2 | Chọn bài liên quan, đo độ giống của chữ mới trong lane | Dùng trong task của lane khi việc cần. Ghi ở dòng "Model phụ" của BRIEF |
| GLM Flash | Trích câu nguyên văn | Không dùng: skill không có việc trích câu |
| Script (không model) | Lint script, đếm slot, dò treo, đọc kết quả, sổ token | `tools/wf-status.py`, `scripts/wf_watchdog.py` |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,ssh?,curl,jev?,gemma?,playwright?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. **Chia lane theo tài nguyên.** Lập bảng tài nguyên → lane chủ: file theme, CSS, cấu hình server, từng post hay trang, GTM, lệnh restart. Mỗi tài nguyên có đúng một lane chủ. Ghi loại tài nguyên theo `references/luat-lane.md` §4 để chọn chạy song song hay tuần tự.
2. **Vẽ đồ thị phụ thuộc, rồi chọn mẫu** trong `references/mau-workflow.js`. Chỉ nối hai lane khi có phụ thuộc thật: cùng URL, post, file, hoặc lane sau cần dữ liệu lane trước.

   | Mẫu | Khi nào | Ví dụ thật |
   |---|---|---|
   | A. Đồ thị | Các chuỗi lane độc lập chạy trong `pool(CHAINS, SLOTS)`, lane trong chuỗi nối bằng `await` | Bản 7: 9 lane ban ngày (trước trần 6 agent; nay tách 3–4 workflow) |
   | B. Chuỗi có cổng | Mốc → việc không restart → staging → production → phần đuôi | Đợt 1 tối ưu VPS |
   | C. Audit chỉ đọc | Nhiều lane đọc → một agent gom plan → một agent phản biện → sửa plan | Audit host không nâng VPS |
   | D. Nhiều lô | Nhiều lô cùng tài nguyên: ghi tuần tự, kiểm lô N song song với ghi lô N+1 | Lô chữ Đợt 1, 20/10 |

   Có hai trần. Mỗi workflow tối đa 6 agent, tính cả agent kiểm và sửa, chạy khoảng 90 phút. Số agent chạy cùng lúc trong phiên không vượt `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (repo này đặt 2 trong `.claude/settings.json`). Trần này tính theo từng phiên, agent của phiên khác không tính chung. Khi Lead nói "tối đa N agent", hiểu là trần chạy cùng lúc, không phải trần mỗi workflow. Việc nhiều hơn thì tách thành nhiều workflow theo đồ thị. Không để lane chờ khoá của lane cùng workflow. Lane cần chờ thì trả `held`. Lane hết `budget_min` thì dừng sớm và trả `partial` (early stop). Script không đo được giờ, nên tổng `budget_min` trên chuỗi dài nhất, cộng lượt kiểm, giữ trong 90 phút.
3. **Viết `plan.json` và BRIEF từng lane.** Định dạng `plan.json` ghi ở đầu `scripts/make_brief.py`. Chạy `python3 skills/web-lane-orchestration/scripts/make_brief.py --plan <plan.json> --lane <key> --decisions <file quyết định>` cho từng lane. Script dừng khi lane ghi không có nguồn duyệt, thiếu dòng Model phụ, hoặc BRIEF quá 3 KB.
4. **Viết khối `COMMON`**: bối cảnh, khối NGUỒN PHÊ DUYỆT, dòng trỏ BRIEF và CHECKPOINT, rồi khối luật `references/luat-lane.md` §1, mục nền tảng §3 và bảng sở hữu.
5. **Viết từng lane**: `key`, `model`, `effort`, `folder`, `task`, `accept`, `readOnly`, `core`, `budget_min`. Task đánh số, ghi lệnh hoặc giá trị cụ thể và file nguồn. `accept` ghi cổng tất định (verify.py, sweep, Jev) và tiêu chí đo được. Kết quả lane trước truyền bằng đường dẫn `ket-qua.json`, không nhúng JSON vào prompt.
6. **Ước chi phí**: khoảng 240.000 token cho mỗi agent (8 lượt chạy 22–24/10: 88 agent, 21 triệu token, dải 190.000–346.000 mỗi agent). Lane ghi tốn 2 agent khi đạt ngay và 4 agent khi có lỗi production. Lane chỉ đọc tốn 2 agent.
7. **Lint**: chạy `python3 tools/wf-status.py lint-script <script.js> --args <args.json> --base <thư mục workstream>`. Sửa hết ERROR. Đếm agent đang chạy bằng `python3 tools/wf-status.py slots <thư mục session> --cap <CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS>`. Đặt `SLOTS` không quá cap trừ số đang chạy.
8. **Tự phản biện** theo mục dưới, rồi trình Lead: bảng lane (việc, tài nguyên, model, giờ), đồ thị, mẫu, điểm dừng, số agent, chi phí ước tính. Chỉ chạy khi Lead duyệt.
9. **Chạy**: lưu script, chép một bản vào thư mục đợt (`workflow-<tên>.js`), chạy với `args: { base, now }`. Chạy `date` để lấy `now`. Ghi `<đợt>/OWNER.md` và các dòng `Lane:` theo `references/theo-doi-va-cuu.md` §0. Không launch workflow ghi ngay sau một tin hỏi Lead gửi giữa lượt: trả lời tin đó trước, chờ duyệt rồi mới chạy. Khi Lead vắng quá 10 phút, áp khối "Phiên chính và lịch khi Lead vắng" ở `references/luat-lane.md`.
10. **Theo dõi**: ngay sau khi launch, chạy `scripts/wf_watchdog.py` bằng Bash `run_in_background` theo `references/theo-doi-va-cuu.md` §1. Không dùng Monitor, không tự poll.
11. **Đổi phạm vi và cứu treo**: đổi phạm vi lane đang chạy bằng `<lane>/inbox.md`, không SendMessage vào agent đang chạy. Watchdog báo `TREO` hoặc `IM`: làm theo `references/theo-doi-va-cuu.md` §2–§3.
12. **Đóng đợt** theo `references/theo-doi-va-cuu.md` §4: bảng kết quả, sửa `loi_bao_cao` bằng Edit, `mark_applied`, khoá, lịch, chi phí thật, HANDOFF.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Bảng sở hữu tài nguyên nằm trong `COMMON`, mỗi tài nguyên một lane chủ. Lane ghi chữ đọc lại giá trị live ngay trước khi ghi và dừng ô khi chữ cũ đã đổi. Nguồn lỗi: 23/10 ba workflow cùng ghi site agency mẫu; thẻ cũ v2-qp-titles suýt ghi đè chữ thẻ m24 duyệt sau.
- [ ] Đồ thị phụ thuộc: chuỗi độc lập chạy trong `pool`, mỗi workflow tối đa 6 agent và khoảng 90 phút, tổng agent cùng lúc không vượt cap của máy, lane cần chờ trả `held` thay vì ngủ chờ. Nguồn lỗi: 18/87 workflow bị kill, mất 2.528 phút và 26,8 triệu token; chuỗi UI 7 lane nối tiếp chờ 175 phút (16–24/10); đêm 26–27/10 hai workflow 8 và 7 agent vì hiểu "tối đa 8 agent" là trần mỗi workflow.
- [ ] Mỗi lane có BRIEF tối đa 3 KB với NGUỒN PHÊ DUYỆT nguyên văn kèm giờ. Kết quả lane trước truyền bằng `ket-qua.json`. Nguồn lỗi: agent khởi đầu khoảng 67k token, 75 agent đọc HANDOFF; prompt kiểm 22,7 nghìn ký tự vì nhúng JSON; 19/10 10 agent trả `not_applied`, tốn 1,09 triệu token vì thiếu nguồn duyệt.
- [ ] Model theo `references/chon-model.md`: lane chỉ đọc và cơ học chạy Sonnet xhigh, agent kiểm chạy Sonnet xhigh trừ lane `core`, Opus chạy high (Lead chốt 27/10/2026). Nguồn lỗi: đợt rà 16–24/10, 99,7% lượt chạy Opus; 96/96 agent của t-106e đặt xhigh.
- [ ] Kiểm: cổng tất định chạy trước, schema tách `loi_production` và `loi_bao_cao`, chỉ `loi_production` mở vòng sửa, lane chỉ đọc có `readOnly: true`. Nguồn lỗi: t-106e có 47 lượt kiểm dùng 1.180 phút; 5 lượt chỉ có lỗi báo cáo kéo theo khoảng 188 agent-phút sửa và kiểm lại; lane mốc B-0 ngày 24/10 tốn 4 agent.
- [ ] `accept` ghi backup theo phiên bản và thử lệnh trả lại ở chế độ DRY; lệnh đo 5xx dùng `log_health.py`. Nguồn lỗi: lane ảnh LCP 24/10, lệnh trả lại cài lại bản v1; 4 lane đếm sai 5xx ngày 23–24/10 vì gán cứng `$9`/`$10`.
- [ ] Không có lệnh chờ không trần: không Monitor, không vòng `until`/`while … sleep`, và watchdog chạy nền ngay sau launch. Nguồn lỗi: 20–21/10 agent chờ 2 lệnh Monitor có `$(wc -l …)` 155 và 321 phút; lane font 24/10 treo ở Monitor có `$(grep -c …)`, phát hiện sau 50 phút.
- [ ] Script qua `wf-status.py lint-script` không còn ERROR. Plan ghi số agent và token ước tính. Không gọi ArtifactData, Artifact publish, Monitor hay Workflow đầu ngày khi Lead vắng quá 10 phút. Nguồn lỗi: hơn 7 giờ dừng vì hạn mức, script khởi 12 agent sau khi chạm hạn mức; phiên chính treo 607 phút ngày 21/10 vì hộp duyệt.

## Output

- Script workflow: bản phiên lưu tự động, bản sao ở `<workstream>/<đợt>/workflow-<tên>.js`, kèm `plan.json` và `args.json`.
- Mỗi lane một thư mục: `BRIEF.md`, `inbox.md`, `CHECKPOINT.md`, `ket-qua.json`, `bao-cao.md` (kết luận trước, bảng số trước/sau), `rollback.md` (mỗi thay đổi một lệnh trả lại), `backup/`, `mark_applied.json`, `work/`, `shots/` khi có ảnh. Agent kiểm ghi `kiem-doc-lap.md` (mục "Lượt 1", "Lượt 2").
- `<đợt>/OWNER.md` (phiên chủ, run, lane) và `<đợt>/watchdog.log`.
- Báo cáo đợt: bảng lane → trạng thái, kết quả kiểm, file kết quả, việc chờ Lead, chi phí thật từ `wf-status.py tokens`.
- `HANDOFF.md` của workstream: đoạn Trạng thái sửa đè, dưới 60 dòng.

## Gate trước khi trả

- [ ] Lead đã yêu cầu rõ workflow và đã duyệt plan (lane, model, giờ).
- [ ] Script qua `wf-status.py lint-script`, không còn ERROR.
- [ ] Mỗi lane ghi production có lượt kiểm cuối không còn `loi_production`. Lane không đạt có lý do và lệnh trả lại trong báo cáo đợt.
- [ ] Mục `loi_bao_cao` đã sửa hoặc ghi vào báo cáo đợt.
- [ ] Không có 5xx mới. Robots và canonical bản Googlebot smartphone không đổi ở URL bị chạm.
- [ ] Mọi khoá lane đã thành `.lock.done-HHMM` hoặc `.lock.stopped-HHMM`. `staging.lockdir` và `_server-maint.lockdir` đã nhả.
- [ ] `mark_applied` đã ghi batch khi Lead có mặt, hoặc nằm trong `~/.cm/ma/cho-sang-<ngày>/`.
- [ ] Watchdog đã thoát. Lịch tự kiểm đã huỷ, hoặc HANDOFF ghi lịch còn treo kèm giờ. Dòng `Lane:` của đợt đã xoá khỏi HANDOFF.
- [ ] Không file nào chứa host staging, mật khẩu, slug đăng nhập hay key.

## Anti-patterns

- Resume workflow đã chết. Dựng workflow mới chỉ gồm lane còn lại.
- SendMessage vào agent đang chạy trong workflow. Mỗi tin sinh một bản chạy trùng.
- Nhúng `JSON.stringify` kết quả lane vào prompt. Truyền đường dẫn `ket-qua.json`.
- Agent kiểm tin báo cáo của lane. Agent kiểm phải tự đo lại.
- Hai workflow cùng lúc ghi một tài nguyên.
- Lane gọi Workflow, Agent, Monitor hoặc tạo agent cháu.
- Purge toàn site, hoặc restart dịch vụ ngoài mốc plan và khoá `_server-maint`.
- Gộp 5 nhóm việc không liên quan vào một lane. Agent dễ bỏ sót, và agent kiểm khó chấm.
- Workflow hơn 6 agent trong một script. Tách theo đồ thị.

## Changelog

- v1.2.1 (2026-10-27): effort theo model, Lead chốt 27/10: Opus high, Sonnet và Haiku xhigh, mỗi dòng dùng bản mới nhất. Sửa bảng phân việc model, `references/chon-model.md`, `references/mau-workflow.js`.
- v1.2 (2026-10-27): rút từ chương trình đêm 26–27/10 site agency mẫu (24 workflow, 102 agent). Reference mới `chay-dem.md`: chạy từ phiên mới (Lead chốt 27/10), mẫu TIEN-DO, prompt lịch có khung yên lặng, hai trần agent, hết hạn mức giữa đêm, đóng buổi sáng. Bước 2 ghi rõ hai trần. `scripts/che_secret.py` che mật khẩu, key, IP trong output cấu hình và API (một lane in mật khẩu Redis 2 lần), test 9 ca; `luat-lane.md` §1 thêm luật dùng bộ lọc và `REDISCLI_AUTH`. `theo-doi-va-cuu.md` §0 thêm phối hợp phiên song song (khoá `cdn-no-restart`, `lsof` cho khoá flock, file trả lời giữa phiên); §1 watchdog chạy bằng `run_in_background`, không `&`. Eval thêm 3 ca.
- v1.1.4 (2026-10-26): `references/luat-lane.md` §1 thêm 3 luật và một dòng từ đợt CDN site agency mẫu 26/10/2026 (`Deliverables/GTV-Brand/GTV-Website/perf-20261020/crawl-speed-2610/cdn-cf/`): lọc response API nhà cung cấp (một lane in DeploymentKey của Bunny lúc 20:41, đã đổi key); tài nguyên do phiên khác giữ thì không sửa, không restart; quota Globalping 250 probe/giờ/IP dùng chung (10 vòng mẫu DNS tốn 240 probe, lượt đo sau trả file rỗng); lane readOnly vẫn có rollback.md.
- v1.1.3 (2026-10-26): `references/luat-lane.md` thêm 2 luật từ HANDOFF site agency mẫu mục "Bẫy đã gặp" (bản 26/10). §1: không chạy URL Inspection live test hay Rich Results Test hàng loạt, tối đa 1 đợt mỗi tuần; đợt 20/10 tạo 832 lượt Google (`Deliverables/GTV-Brand/GTV-Website/perf-20261020/crawl-speed-2610/plan.md` CS-01). §3.1: site có Basic Auth đọc mật khẩu từ `.agent-secrets/`, WP-Cron qua HTTP nhận 401 (bản tiếng Anh của site agency mẫu từ 24/10).
- v1.1.2 (2026-10-25): chủ run và lane khi nhiều phiên cùng chạy (`OWNER.md`, dòng `Lane:`, dò run sống; coord-5, ops2-5). Trạng thái HANDOFF ghi bằng `handoff.py stamp`. Kiểm độc lập ghi dòng "Kết luận: đạt/không đạt" cho `mark_batch.py`. `mark_applied.json` theo dạng của `wp-content-review-apply` 1.6. Trỏ tới `apply.php` + `so_duyet.py check`, `apply_server_block.sh` của `wp-security-hardening` 1.7, `jev.py --preflight-only`, mẫu dòng Model phụ.
- v1.1.1 (2026-10-25): sửa chẩn đoán lane font 24/10 (Monitor bật hộp duyệt quyền, không phải vòng until; hs-1 mục 4). Ghi hook `artifact_away_guard.py`. Trỏ tới công cụ PSI của `wp-pagespeed` 1.12, helper staging của `wp-staging-deploy` 1.1, skill `decision-page` cho mục `for_lead`, và `tools/shell-traps-macos.md`.
- v1.1 (2026-10-24): thêm 13 mục từ đợt rà 16–24/10, Lead duyệt.
  - Theo dõi: cấm Monitor. Cổng "Lead vắng 10 phút" áp cho phiên chính, lịch và agent. `scripts/wf_watchdog.py` thay lịch LLM 30 phút.
  - Công cụ: `tools/wf-status.py` (lint-script, tokens, result, slots, stale). `scripts/make_brief.py` sinh BRIEF 3 KB. Kết quả truyền bằng `ket-qua.json`.
  - Mẫu script: `goi()` có cờ dừng, `pool`, trần 6 agent và 90 phút, `budget_min`, `held`, mẫu D.
  - Luật: khoá `_server-maint`, khoá giữ tối đa 45 phút, `inbox.md` thay SendMessage, khối NGUỒN PHÊ DUYỆT, 8 bẫy shell.
  - Kiểm: schema tách `loi_production` và `loi_bao_cao`. Model theo `references/chon-model.md`.
  - Kiểm thử: 23 ca `wf-status.py`, 17 ca hai script của skill. Một agent Sonnet kiểm độc lập bản vá; 2 lỗi chặn đã sửa (mẫu D không chặn lô N+2, watchdog báo XONG giả cho run cũ). Chưa có lượt chạy thật bằng v1.1.
  - Lệch có chủ đích so với đặc tả: prompt lane giữ khối luật chung (khoảng 6 KB) cùng dòng trỏ BRIEF, không chỉ một dòng, để luật cứng luôn nằm trong prompt.
- v1.0 (2026-10-24): tạo mới từ 7 script workflow phiên f00d80af (22–24/10) và HANDOFF site agency mẫu mục Bẫy. Kiểm cấu trúc: `mau-workflow.js` tái dựng được cả 3 mẫu của 7 script. Chưa có lượt chạy thật bằng skill. Nhánh Shopify và Next.js chưa chạy thật.
