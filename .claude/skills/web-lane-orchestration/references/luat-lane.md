# Luật lane dùng chung

Mục đích: khối luật cứng để chép vào hằng `COMMON` của script workflow. Đọc ở bước 4 của skill. §1 áp cho mọi nền tảng. §3 chọn đúng một mục nền tảng. Nguồn: 7 script phiên f00d80af (22–24/10/2026), `Deliverables/GTV-Brand/GTV-Website/HANDOFF.md` mục "Bẫy đã gặp", và đợt rà transcript 16–24/10 (`Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-lane-orchestration_bo-sung_v1.md`).

## 1. Khối chung

Chép nguyên văn khối dưới vào `COMMON`, sau khối NGUỒN PHÊ DUYỆT và dòng trỏ BRIEF. Thay phần trong `<…>`.

```text
Luật cứng:
- Không in host staging, mật khẩu, key, token, slug đăng nhập ra chat hay file. Lọc output bằng sed. Tên thư mục chứa host staging thì thay bằng STG.
- Response của API nhà cung cấp (CDN, DNS, hosting) có thể chứa key: lọc trước khi in hoặc lưu. Chỉ in trường cần dùng, che IP. Nếu lỡ in key, báo trong bao-cao.md để phiên chính xin đổi key.
- Lệnh đọc file cấu hình server (redis.conf, wp-config.php, .env, vhost) hoặc response API: pipe output qua python3 -I skills/web-lane-orchestration/scripts/che_secret.py --ip. Không cat cả file cấu hình: grep đúng dòng cần.
- Redis: đặt mật khẩu bằng biến REDISCLI_AUTH đọc trên server, ví dụ ssh <alias> 'REDISCLI_AUTH=$(awk "/^requirepass/{print \$2}" /etc/redis/redis.conf) redis-cli INFO keyspace'. Không dùng redis-cli -a.
- Mỗi thay đổi: backup (đường dẫn + md5) → đo trước → đổi → đo sau → ghi 1 lệnh trả lại vào rollback.md. Backup theo phiên bản (backup/v1/, backup/v2/…). Sau vòng sửa, thử lại lệnh trả lại ở chế độ DRY.
- Sửa đúng dòng cần sửa. Không chép đè cả file config, vì lane khác có thể đã sửa file đó trong tuần.
- Quarantine thay vì xoá.
- Chỉ ghi tài nguyên lane mình sở hữu (bảng dưới). Cần sửa tài nguyên của lane khác thì ghi vào bao-cao.md, không tự sửa.
  <bảng tài nguyên → lane chủ>
- Ghi chữ hay giá trị: đọc giá trị live ngay trước khi ghi, kiểm chữ cũ còn khớp (DRY), chỉ thay đúng chuỗi đó. Nếu chữ cũ không còn khớp, dừng ô đó và ghi lý do.
- Khoá lane: chạy mkdir -p ~/.cm/locks một lần, rồi tạo ~/.cm/locks/<tên lane>.lock lúc bắt đầu, ghi giờ từ lệnh date. Đổi tên thành .lock.done-HHMM khi xong, .lock.stopped-HHMM khi dừng giữa chừng. Không đụng khoá do phiên chính giữ.
- Khoá tài nguyên dùng chung (staging, URL): "mkdir ~/.cm/locks/<tên>.lockdir" thành công mới dùng, ghi tên lane và giờ vào file owner. Giữ tối đa 45 phút rồi nhả. Nếu khoá bị giữ, kiểm lại một lần sau tối đa 10 phút. Vẫn bị giữ thì làm việc khác; hết việc thì trả status held, held_until "<tên khoá> nhả".
- Restart dịch vụ (web server, PHP, Redis, MySQL) và vá OS: chỉ lane chủ, chỉ ở mốc plan cho phép, chỉ khi "mkdir ~/.cm/locks/_server-maint.lockdir" thành công. Khi khoá này bị giữ, lane khác không đo hiệu năng và không restart.
- Tài nguyên do phiên khác giữ (BRIEF ghi tên phiên và tài nguyên): lane không sửa và không restart tài nguyên đó. Ghi việc cần làm và lệnh vào bao-cao.md để phiên chính phối hợp.
- Đo từ nhiều vùng bằng Globalping: quota 250 probe mỗi giờ cho mỗi IP, tính theo từng probe, dùng chung cho mọi lane và phiên trên máy. Đọc https://api.globalping.io/v1/limits trước khi đo. Thiếu quota thì ghi giờ mở lại, không chạy đo dở.
- Mọi lệnh chờ tối đa 10 phút. Không dùng vòng until/while … sleep để chờ. Kiểm log một lần mỗi lệnh.
- Không dùng Monitor, Workflow, Agent, SendMessage, Artifact, ArtifactData. Id đã áp ghi vào mark_applied.json.
- Nếu thư mục lane có inbox.md, đọc file đó ở mỗi mốc CHECKPOINT. Phiên chính đổi phạm vi lane bằng file này.
- Một agent làm một vòng việc. Sau khoảng 150 lượt tool, khi ngữ cảnh vượt khoảng 250k token, hoặc khi hết budget_min: ghi CHECKPOINT.md và trả status partial.
- Tool Chrome chỉ gọi sau khi list_connected_browsers trả về trình duyệt.
- Ghi kết quả theo schema vào ket-qua.json và trả lại đúng kết quả đó trong tin cuối. Kết quả lane khác đọc từ ket-qua.json của lane đó.
- Chạy date trước khi ghi giờ vào file.
- Điều kiện dừng: 5xx mới ở site bị chạm, lỗi fatal mới, noindex/robots/canonical đổi, đăng nhập admin hỏng, <ngưỡng tải của host>. Gặp một điều kiện thì trả lại bước vừa làm, ghi lý do, dừng phần còn lại của lane.
- Không chặn Googlebot, Bingbot, AhrefsBot, Applebot, DuckDuckBot, Cốc Cốc và mọi bot AI (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User, PerplexityBot…).
- Không đổi GTM live, Pixel, Hotjar, Cloudflare live, HSTS, trừ khi task của lane giao rõ việc đó.
- Không chạy URL Inspection live test hay Rich Results Test hàng loạt. Kiểm schema offline trước. Tối đa 1 đợt mỗi tuần, chỉ cho URL vừa đổi schema, và chỉ khi task của lane giao rõ. Mỗi lượt test là một request Googlebot vào site.
- Chữ mới qua skill humanizer nếu runtime có skill đó; không có thì rà theo `skills/semantic-content-audit/references/ai-detection-checklist.md`. Không viết "cam kết KPI", "cam kết thứ hạng" hay câu hoàn tiền.
- QA ảnh và chữ hàng loạt: Jev theo tools/ai-assist/README.md, rubric theo bảng hiệu chuẩn trong tools/ai-assist/README.md, ngân sách ghi trong BRIEF. Trước lượt Jev đầu tiên của lane, chạy jev.py với --preflight-only. Claude đọc lại mọi mục Jev gắn cờ.
- Thư mục lane chứa: BRIEF.md, inbox.md, CHECKPOINT.md (cập nhật ở mỗi mốc), ket-qua.json, bao-cao.md (tiếng Việt có dấu, kết luận trước, bảng số trước/sau), rollback.md, backup/, mark_applied.json (dạng [{"id", "status": "applied", "note"}], [] nếu không có), work/ (log, pid), shots/ khi có ảnh. Lane readOnly vẫn tạo rollback.md với một dòng "Lane chỉ đọc, không có thay đổi".
```

### Bẫy shell

`scripts/make_brief.py` chép khối dưới vào `BRIEF.md` của lane. Lane không có BRIEF thì chép khối này vào `COMMON`. Bản đầy đủ cho người đọc: `tools/shell-traps-macos.md`. Khi sửa một bẫy, sửa cả hai nơi. Nguồn: đợt rà 16–24/10, lỗi zsh "no matches found" 90 lần ở 39 agent, `timeout` không có trên macOS 11 lần, `sleep` mở đầu lệnh bị chặn 24 lần, 12 lệnh `rm -rf` bị từ chối.

```text
1. Quote glob: grep --include='*.php', rg -g '*.css'. Glob không quote làm zsh báo "no matches found".
2. macOS không có timeout/gtimeout: dùng perl -e 'alarm 60; exec @ARGV' <lệnh>.
3. Không mở đầu lệnh bằng sleep. Cần chờ thì chạy nền, rồi kiểm một lần ở lượt sau.
4. Không rm -rf: mv vào _cu/ hoặc tạo thư mục mới có hậu tố giờ.
5. Đặt dấu phân cách trong nháy: echo '====='.
6. Script cần PIL: không chạy python3 -I, dùng ~/.venvs/embeddinggemma/bin/python.
7. Không pkill -f theo tên chung: chỉ kill PID ghi trong work/*.pid.
8. Mẫu regex có {0,N} lớn: dùng Python re, không dùng ugrep.
Lệnh dự kiến quá 2 phút: nohup <lệnh> >work/x.log 2>&1 </dev/null & echo $! >work/x.pid. Kiểm log bằng lệnh ngắn bọc perl alarm.
```

### Phiên chính và lịch khi Lead vắng

Khối này không chép vào `COMMON`. Phiên chính, lịch CronCreate và agent cùng áp. Nguồn: phiên chính treo 607 phút ngày 21/10 và 321 phút hai lần ngày 20/10 vì chờ hộp duyệt quyền.

- Nếu Lead không nhắn trong 10 phút gần nhất, không gọi tool có thể bật hộp duyệt quyền: ArtifactData (cả get, query, list lẫn ghi), Artifact publish, Monitor, lần launch Workflow đầu tiên trong ngày.
- Ghi việc cần các tool đó vào `~/.cm/ma/cho-sang-<ngày>/`. Sáng hôm sau, khi Lead đã nhắn, làm một batch.
- Không dùng Monitor để chờ tiến trình. Chạy lệnh chờ bằng Bash `run_in_background`; harness báo phiên chính khi lệnh thoát. Lệnh nền khác: `nohup` như khối Bẫy shell, rồi kiểm bằng lệnh ngắn bọc `perl -e 'alarm 60; exec @ARGV'`.
- Từ 25/10, hook `tools/hooks/artifact_away_guard.py` (chỉ có ở workspace của master) (khai trong `.claude/settings.json` root) chặn ArtifactData và Artifact publish khi Lead không nhắn 10 phút, áp cả sub-agent. Monitor và lần launch Workflow đầu ngày chưa có hook, vẫn theo luật này.

## 2. Đo sức khoẻ site trong lane

- Đếm 5xx bằng `skills/seo-logfile-analysis/scripts/log_health.py`. Script đọc mã trạng thái bằng regex, nên log có hay không có trường đầu đều đọc đúng. Nếu không đọc được dòng nào, script trả mã 2. Khi đó lane không được ghi "0 lỗi".
- Nếu phải dùng awk, tách theo dấu `"` rồi đọc trường thứ 3. Không gán cứng `$9` hay `$10`: log site agency mẫu đặt mã ở `$10`, log en và staging đặt mã ở `$9`.
- Dòng lỗi không có giờ, ví dụ "max children" trong `stderr.log` của OpenLiteSpeed: so tổng số dòng trước và sau thay đổi.
- Robots và canonical: so bản Googlebot smartphone của URL bị chạm với bản lưu trước thay đổi.

## 3. Nền tảng

### 3.1 WordPress

Đã chạy thật trên site agency mẫu (OpenLiteSpeed, LiteSpeed Cache, Redis object cache) ngày 22–24/10/2026.

```text
- Thứ tự ghi: backup → staging (theme, CSS, plugin, mu-plugin, template) → DRY → production → purge theo URL → làm nóng → verify cả bản cache lẫn ?nc=<số> → kiểm robots và canonical bản Googlebot smartphone.
- Staging là bản clone cũ: chạy script đồng bộ staging của site trước khi ghi staging.
- Site có Basic Auth (staging, bản ngôn ngữ chưa công khai): đọc user:pass từ file quyền 600 trong .agent-secrets/ mà BRIEF chỉ định. Không in mật khẩu, không ghi vào thư mục lane. WP-Cron gọi qua HTTP nhận 401: chạy WP-Cron bằng cron hệ thống.
- Giới hạn tải production: tối đa 2 request đồng thời và 1 request/giây khi quét hoặc làm nóng. Tối đa 2 WP-CLI cùng lúc (flock /tmp/wpcli-slot-1.lock hoặc /tmp/wpcli-slot-2.lock), thêm -d memory_limit=512M. Không chạy backup, crawl, đồng bộ staging cùng lúc. Không quét LIKE trên postmeta production.
- WP-CLI chạy bằng user web, không chạy bằng root.
- Purge theo URL, tối đa 12 path mỗi lệnh. Không purge toàn site. Không xoá CSS Elementor toàn site.
- LiteSpeed Cache: ghi option bằng SQL + wp_cache_delete, không dùng wp litespeed-option set.
- Sau SQL thô: xoá khoá object cache liên quan (không FLUSHALL), rồi purge URL.
- PSI chỉ đo URL sạch hoặc ?nc=, không dùng utm_*. Lấy trung vị 3 lượt. Chênh A/B dưới 10 điểm hoặc nằm trong IQR của 3 lượt thì ghi "không đổi". A/B dùng HTML tĩnh, không dùng công tắc tham số trong mu-plugin production.
- Restart web server: chỉ graceful, theo luật khoá _server-maint ở khối chung. Chạy date trước. Sau restart: kiểm 5xx, trang chủ và URL chính trả 200, cache hit sau làm nóng.
```

Skill chuyên môn cho task của lane: `wp-content-review-apply` (chữ), `wp-pagespeed` (tốc độ), `wp-staging-deploy` (gói nhiều file), `wp-security-hardening`, `web-qa-gate`.

Task lane trỏ tới công cụ có sẵn, không tự viết script chạy nền và không chép script vào thư mục lane:

- Đo PSI: `wp-pagespeed` 1.12. Chạy `psi_run.py --detach`, đọc `PSI_STATE.txt` sau thời gian ước tính, dùng `perf_probe.mjs --done` khi cần. Mỗi site tối đa 2 request PSI đồng thời. Kết luận A/B bằng `psi_decide.py`.
- Ghi chữ lên trang: `wp-content-review-apply` 1.6. Dựng `ops.json`, chạy `so_duyet.py check` trước khi ghi, ghi bằng engine `apply.php`. Không viết `apply*.php` riêng cho lane.
- Chặn ở `.htaccess` hoặc vhost: `scripts/apply_server_block.sh` của `wp-security-hardening` 1.7. Diễn tập trước, rồi chạy `--apply`. Script tự backup, ghi md5 và sinh `rollback.sh`.
- Gọi staging: helper của `wp-staging-deploy` 1.1. Mở tunnel bằng `stg_tunnel.sh up --lane <key> --port <cổng riêng của lane>`, đọc trang bằng `stg_get.sh`. Chạy `stg_leak_check.sh` trên thư mục lane trước khi báo xong.

### 3.2 Shopify

Chưa chạy thật. Trước lượt đầu, đọc tài liệu chính thức của Shopify CLI và Admin API, ghi URL và ngày đọc vào `bao-cao.md`.

| Khái niệm lane | Cách làm trên Shopify |
|---|---|
| Staging | Theme chưa publish: `shopify theme push --unpublished` từ bản pull của theme live. Xem bằng link preview |
| Backup | `shopify theme pull --theme <id>` vào `backup/` trước khi ghi. Nội dung (product, page, metafield) đọc qua Admin API và lưu JSON |
| Production | Theme: `shopify theme publish --theme <id>` sau khi bản preview đạt. Nội dung: ghi qua Admin API |
| Purge | CDN của Shopify tự làm mới sau khi ghi. Verify bằng URL sạch thêm tham số phá cache |
| Giới hạn tải | Đọc giới hạn trong phản hồi Admin API: header `X-Shopify-Shop-Api-Call-Limit` (REST) hoặc `extensions.cost.throttleStatus` (GraphQL). Giữ mức dùng dưới 50% |
| Khoá | Mỗi theme id có một lane chủ. Khoá `~/.cm/locks/` như §1 |
| Trả lại | Publish lại theme cũ (giữ nguyên, không xoá). Nội dung: ghi lại từ JSON backup |
| Không có | SSH, log server, restart. Bỏ các mục sức khoẻ server. Theo dõi bằng mã trạng thái và robots/canonical |

### 3.3 Next.js

Chưa chạy thật. Trước lượt đầu, đọc tài liệu chính thức của host (ví dụ Vercel) và của Next.js về revalidate, ghi URL và ngày đọc vào `bao-cao.md`.

| Khái niệm lane | Cách làm với Next.js |
|---|---|
| Staging | Preview deployment của nhánh riêng cho từng lane |
| Backup | Commit và nhánh git. Nội dung ở CMS headless: export qua API vào `backup/` |
| Production | Merge vào nhánh production theo thứ tự lane, hoặc promote deployment đã kiểm |
| Purge | `revalidatePath`/`revalidateTag` hoặc endpoint revalidate theo yêu cầu. CDN purge theo URL |
| Khoá | Mỗi lane một nhánh. Lane không push thẳng nhánh production. Merge nối tiếp |
| Trả lại | Promote deployment trước, hoặc revert commit rồi deploy lại |
| Sức khoẻ | Log runtime của host, mã trạng thái, robots/canonical |

## 4. Bảng sở hữu tài nguyên

Ví dụ từ bản 7 site agency mẫu ngày 23/10 (9 lane song song):

| Tài nguyên | Lane chủ |
|---|---|
| CSS Customizer (post 83220), CSS bố cục | l7-giao-dien |
| Code favicon trong header theme, Site Icon, `/favicon.ico` | l7-favicon |
| post_content và ACF của trang dịch vụ M1, M4, M5, trang chủ | l7-noi-dung |
| `.htaccess`, cấu hình vhost, lệnh restart web server | l7-ha-tang |
| mu-plugin phân trang, mu-plugin purge khi đăng bài, template lưu trữ | l7-seo-ky-thuat |
| Trang tĩnh khoá học, GTM | l7-gtm |
| Thẻ duyệt mới (chỉ file local) | l7-the |

Lane chỉ ghi file local cũng ghi vào bảng, để agent kiểm biết lane đó không được chạm site.

Lane ghi vào bảng loại tài nguyên để chọn cách chạy: lô chỉ đọc, ghi file riêng, hoặc chỉ ghi DB trên tập URL rời nhau chạy song song, tối đa 2 luồng. Lô chạm theme, CSS, Elementor, mu-plugin chạy tuần tự. Việc chỉ đo (PSI, A/B) tách khỏi chuỗi ghi.
