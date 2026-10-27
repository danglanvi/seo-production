---
name: wp-security-hardening
description: "Ứng cứu sự cố và hardening site WordPress khi có quyền vào server (SSH + WP-CLI): backup, tìm IOC, cách ly, đổi credentials, siết server và site, kiểm, báo cáo việc chờ duyệt. Dùng khi site bị xâm nhập, có mã độc, cần rà bảo mật định kỳ hoặc vá OS, PHP."
metadata:
  version: "1.8"
---

# wp-security-hardening — ứng cứu và siết bảo mật WordPress

Quy trình đã chạy thật trên 2 site WordPress (VPS Ubuntu, aaPanel, OpenLiteSpeed) ngày 16–17/10/2026: webshell của site khác cùng server, cửa sau dev để lại trong theme, 472 khối script tiêm vào bài, webshell trong thư mục plugin, 19 plugin cũ. Stack khác (Apache, Nginx, cPanel) dùng cùng quy trình, đổi lệnh theo bảng ở `references/checklist-hardening.md`.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-security-hardening/scripts/`. Bộ model nằm ở `tools/ai-assist/`.

## Khi nào dùng

- Site có dấu hiệu bị xâm nhập: link lạ, script lạ, admin lạ, GSC báo Security issues, host báo mã độc.
- Rà bảo mật định kỳ, hoặc trước khi đổi theme, đổi server.
- Vá OS hoặc PHP sau advisory, áp khối `.htaccess` hoặc vhost, xoá site phụ, DB, user trên server.
- Không dùng khi: chỉ tối ưu tốc độ (`wp-pagespeed`), chỉ sửa nội dung (`wp-content-review-apply`), không có quyền vào server (chỉ chạy được `exposure_check.sh` từ ngoài, ghi giới hạn).

## Luật cho mọi đợt

- Backup trước mỗi thay đổi. Quarantine thay vì xoá.
- Không in mật khẩu, key, slug đăng nhập ẩn ra chat, báo cáo hay file ngoài `.agent-secrets/`.
- Reboot, restart dịch vụ chỉ trong giờ thấp điểm hoặc khi người duyệt cho phép trong đợt đó.
- Xong từng mục thì cập nhật `HANDOFF.md` của đợt.
- Agent không gõ mật khẩu wp-admin, panel hay hosting. Việc cần trang quản trị: người vận hành đăng nhập trên Chrome, agent dùng tab đó.
- Đổi tracking, xoá site, đổi DNS, SSL, firewall, đóng cổng đang dùng: người duyệt (SEO Lead Project hoặc chủ site) duyệt từng lần.
- Site khác trên cùng server: chỉ liệt kê và kiểm khi ảnh hưởng site đang làm. Báo chủ site đó, không tự sửa.

## Đọc trước

- `00-client-context/wp-server.md`: cách vào server, web root, lệnh WP-CLI, stack, bẫy riêng của site. Chưa có thì tạo từ `_TEMPLATES/wp-server.md` cùng người vận hành.
- `references/ung-cuu-su-co.md`: tìm IOC, sàng file bằng model, cách ly, dấu bám trụ. Đọc ở nhánh A.
- `references/checklist-hardening.md`: checklist theo lớp, lệnh kiểm, rollback. Đọc ở Bước 4.
- `references/ap-config-song.md`: cấp site hay cấp server, script áp khối, HSTS tăng dần. Đọc trước khi sửa `.htaccess`, vhost.
- `references/va-os-php.md`: vá OS, vá PHP theo advisory. Đọc khi vá.
- `references/xoa-an-toan.md`: checklist trước mọi thao tác xoá trên server.
- `references/ra-tai-khoan-cdn.md`: rà tài khoản Cloudflare, CDN; quy trình khi secret bị lộ. Đọc ở nhánh C.
- `tools/ai-assist/README.md` trước khi gọi Jev hoặc EmbeddingGemma.

## Input

| Bắt buộc | Ví dụ | Thiếu thì |
|---|---|---|
| Domain và SSH alias | `example.vn`, `site-vps` | Hỏi. Không tự dò credential. |
| Phạm vi đã duyệt | "Dọn mã độc + hardening, được reboot" | Chỉ chạy phần chỉ đọc, lập danh sách chờ duyệt. |
| Site khác trên cùng server | 5 site trên một VPS | Liệt kê từ cấu hình web server. |
| Thư mục evidence | `03-audits/technical/security-<YYYY-MM>/evidence-<đợt>/` | Dùng mặc định này. |

## Phân việc model

| Phần | Việc | Quyết định |
|---|---|---|
| Code | `exposure_check.sh`, `persistence.sh`, `scan_files.py`, `apply_server_block.sh`, `preflight_remote.sh`, `verify_backup.sh`, `sitecheck.sh` | Dùng. Mọi phép kiểm có mã thoát chạy bằng script |
| Jev | Task `malware-triage` xếp file nghi độc sau lớp checksum và scanner | Dùng. Ngưỡng và cách gọi theo `references/ung-cuu-su-co.md` mục 2. Nhãn `benign` không thay việc Claude đọc file có dấu hiệu |
| EmbeddingGemma 2 | So excerpt file với bộ mẫu webshell đã cách ly, cosine từ 0,90 thì chuyển Claude đọc | Dùng khi có bộ mẫu dương. Thiếu bộ mẫu thì bỏ |
| GLM Flash | Trích câu | Không dùng. Skill không có việc trích câu tự do |
| Claude | Đọc file gắn cờ, kết luận IOC, lập plan và danh sách chờ duyệt, viết báo cáo | Dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,ssh,wp-cli,curl,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Kiểm thêm dependency riêng và backup. Lệnh dưới chạy từ root repo, `S=skills/wp-security-hardening/scripts`.

1. Kiểm một lần: `ssh -o BatchMode=yes <alias> 'echo ok'`, WP-CLI chạy được theo lệnh trong `wp-server.md`, `curl`, `python3`. Key Jev và venv EmbeddingGemma theo `tools/ai-assist/README.md`. Thiếu model thì Claude đọc thay và ghi giới hạn.
2. Preflight server: `ssh <alias> 'bash -s -- --path /root --need-db' < "$S/preflight_remote.sh"`. Nếu `RESULT=fail`, dừng và báo dòng "không". Dùng `COMPRESS` (zstd hoặc gzip) và `PULL` (rsync hoặc tar qua SSH) cho các lệnh sau.
3. Dump DB: `mysqldump --single-transaction --quick --no-tablespaces --routines --triggers --events --hex-blob <db>`, truyền qua SSH về máy vận hành rồi nén. User WordPress thường không có quyền PROCESS, nên luôn thêm `--no-tablespaces`.
4. Dump một phần (`--where`, vài bảng trước một lần sửa nhỏ): thêm `--no-create-info --replace`. Dump có `DROP TABLE` khi nạp lại sẽ xoá cả bảng.
5. Tar mã nguồn site qua SSH.
6. Kiểm bằng `bash "$S/verify_backup.sh" --min-tables <số bảng trên server> --min-entries <số file trên server> --write-sums <dump> <tar>`. Dump một phần dùng `--partial`. Script bắt file 0 byte, dump thiếu "Dump completed", tar thiếu entry, rồi ghi `SHA256SUMS`. Mã thoát khác 0 thì dump lại, không làm tiếp.
7. Lưu ngoài repo: `~/Backups/<host>/<YYYY-MM-DD>/<đợt>-pre/`. Không commit backup. Mỗi thay đổi lớn có thư mục backup riêng.

## Bước 1 — chọn nhánh

- **Nhánh A, ứng cứu sự cố:** có IOC hoặc nghi xâm nhập. Làm Bước 2 → 6.
- **Nhánh B, rà soát định kỳ:** chưa thấy IOC. Bỏ Bước 3. Làm Bước 2, 4, 5, 6.
- **Nhánh C, tài khoản Cloudflare hoặc CDN, secret bị lộ:** trang lạ chỉ hiện qua edge (CAPTCHA giả, redirect lạ), rà tài khoản CDN định kỳ, hoặc secret lọt vào transcript, chat, file. Làm theo `references/ra-tai-khoan-cdn.md`, rồi Bước 6. Agent chỉ đọc và lập danh sách. Người dùng tự bấm xoá và đổi bảo mật.

## Bước 2 — thu thập, chỉ đọc

1. Kiểm từ ngoài: `scripts/exposure_check.sh https://<domain>`. Script không in Location, nên không lộ slug đăng nhập. Staging có Basic Auth: đặt `EXPOSURE_CURL_CONFIG=<file cấu hình curl>`. Hai dòng `{RAND}` gọi URL ngẫu nhiên và chỉ nhận 404. FAIL ở hai dòng này nghĩa là site trả soft-404 hoặc theme đổi mã (200, 301 về trang chủ, 410). Ghi vào bảng phát hiện và chuyển cho `technical-seo-audit`.
2. Kiểm dấu bám trụ server: `ssh <alias> "bash -s" < scripts/persistence.sh > <ev>/persistence.txt`. Script chạy bằng root, cần Ubuntu hoặc Debian.
3. Sàng file theo `references/ung-cuu-su-co.md` mục 2: checksum → `scan_files.py` → EmbeddingGemma → Jev `malware-triage` → Claude đọc.
4. Quét DB theo mục 3 của cùng file: script tiêm trong bài, option lạ, admin lạ, app password, cron.
5. Kiểm lớp đăng nhập: panel hosting (cổng, 2FA, API, log đăng nhập), admin WordPress (2FA, tên dễ đoán, slug tác giả), slug đăng nhập ẩn, FTP. Audit tài khoản theo checklist cuối `references/ung-cuu-su-co.md` mục 1.
6. Lập bảng phát hiện 3 mức Cao, Trung bình, Thấp. Mỗi dòng có bằng chứng, cách sửa, nơi sửa.

## Bước 3 — cách ly (nhánh A)

1. File độc: chuyển ra thư mục quarantine ngoài web root (`/root/<site>-offweb-<ngày>/`, chmod 600), giữ cấu trúc thư mục, ghi hash.
2. Mã tiêm trong DB: lưu các khối gốc ra JSONL nén, rồi gỡ bằng `$wpdb`, không tạo revision, không đổi `post_modified`.
3. File lộ (backup, zip, `wp-config.php.bak`): chuyển vào quarantine, thêm rule chặn theo checklist.
4. Kiểm lại: URL cũ của file trả 403, 404 hoặc 410. Purge cache.
5. Bản backup "sau dọn" có thể còn IOC bị sót. Ghi rõ trong HANDOFF bản nào sạch.

## Bước 4 — đổi credentials và hardening

1. Credentials (nhánh A, hoặc khi lộ): ghi giá trị mới vào `.agent-secrets/<host>_<site>_credentials_<ngày>.env` (chmod 600) trước. Chỉ gửi lên server qua stdin. Đổi salt, huỷ session admin. Kiểm từng giá trị sau khi áp.
2. Hardening theo `references/checklist-hardening.md`, từng lớp: web server, `wp-config`, WordPress (mẫu `templates/mu-plugin-security.php`), plugin, đăng nhập, server. Ghi cấp của từng việc theo `references/ap-config-song.md` mục 1. File theme và mu-plugin đi qua staging và `wp-staging-deploy` trước khi lên production. Việc cấp server không có staging: thay bằng backup, diễn tập, probe, rollback. Ứng cứu khẩn (nhánh A) được sửa thẳng production sau khi backup.
3. Khối `.htaccess` và vhost: áp bằng `scripts/apply_server_block.sh`, diễn tập trước, rồi `--apply`. Lệnh mẫu và cách đọc mã thoát ở `references/ap-config-song.md` mục 2. Ghi đường dẫn `rollback.sh` vào HANDOFF.
4. Vá OS, vá PHP: theo `references/va-os-php.md`. Xoá site phụ, DB, user, dịch vụ: theo `references/xoa-an-toan.md`, người duyệt từng lần.
5. Sau mỗi mốc: `scripts/sitecheck.sh https://<domain> <mốc> <paths.txt>`. Mốc nào có lỗi thì rollback mốc đó trước khi làm tiếp.
6. Việc nằm ngoài phạm vi đã duyệt: ghi vào danh sách chờ duyệt, kèm lệnh làm và rollback.
7. Site có CDN (skill `cdn-speed-setup`):
   - Khai IP trạm CDN là tin cậy ở web server. Nếu không khai, Wordfence, giới hạn tần suất và log chỉ thấy IP trạm CDN.
   - Khai đúng từng IP lấy từ log origin sau khi đổi DNS. Không gộp thành /24: máy khác trong cùng dải sẽ giả được IP khách.
   - OpenLiteSpeed: `useIpInProxyHeader 2`, mỗi IP dạng `a.b.c.dT`. OLS 1.8.1 không nhận `/32T`. Việc này cần restart OLS theo luật restart ở trên.
   - Wordfence: khi web server đã đặt `REMOTE_ADDR` đúng, để Wordfence đọc `REMOTE_ADDR`. Lệnh `wfConfig::set` qua `wp eval-file` không lưu được (site VN, 26/10/2026).
   - Chặn `xmlrpc.php` và `wp-login.php` ở edge CDN. Ghi vào HANDOFF: admin ở nước ngoài cần VPN về VN để đăng nhập.
   - Apex DNS-only không có WAF và bot rule của Cloudflare. Ghi rõ trong báo cáo.

## Bước 5 — kiểm

- Chạy lại `exposure_check.sh` và `persistence.sh`, so với Bước 2.
- Kiểm cloaking: cùng URL với UA Chrome, Googlebot, mobile kèm referer Google phải trả cùng mã, cùng title, cùng tập host.
- Kiểm PHP trong `uploads`, `languages`, `upgrade`: gọi `.php`, `.PHP` và biến thể path-info `.php/a`, mong 403. Mã 404 hoặc 410 nghĩa là rule chưa có. Nếu tạo file thử, chuyển file vào quarantine sau khi kiểm.
- Kiểm cổng từ ngoài bằng `nc -z`. Kiểm các site khác trên cùng server vẫn trả 200.
- Site có CDN: request qua CDN phải ghi IP khách thật vào `REMOTE_ADDR` và log. Header `X-Forwarded-For` giả gửi thẳng tới origin phải bị bỏ qua.
- Chụp template chính trước và sau bằng `skills/wp-pagespeed/scripts/shot.mjs` và `shot_cmp.py`.

## Bước 6 — báo cáo

- File `<CLIENT>_bao-cao-su-co-bao-mat_v<N>.md` (nhánh A) hoặc `<CLIENT>_bao-mat-ra-soat_v<N>.md` (nhánh B) trong `03-audits/technical/security-<YYYY-MM>/`.
- Cấu trúc: tóm tắt, IOC và timeline, đã gỡ, thay đổi cấu hình, credentials đã đổi (chỉ tên key, không giá trị), bằng chứng kiểm, rủi ro còn lại, việc chờ duyệt (mỗi việc có lệnh và rollback), chi phí Jev.
- Không kết luận "sạch tuyệt đối" khi chưa rõ đường vào hoặc còn plugin không có checksum.
- Trước khi báo xong, quét lộ secret trong thư mục evidence và báo cáo: `bash skills/wp-staging-deploy/scripts/stg_leak_check.sh <thư mục> --env-file <file secret của đợt>`. Thêm `--no-host` nếu đợt không chạm staging. Mã thoát 1: che hoặc bỏ chuỗi lộ khỏi file rồi chạy lại. Bước tuỳ chọn khi chạy trong workspace gốc có `tools/leak_scan.sh`: `bash tools/leak_scan.sh <thư mục>` ở root workspace.
- Cập nhật `HANDOFF.md` của đợt, bảng D `index.md`, append `log.md`.

### Tự phản biện trước khi trình
Chấm plan, danh sách chờ duyệt và báo cáo theo checklist dưới. Lập bảng 4 cột: mục, đạt chưa (Đạt, Một phần, Chưa, Bỏ), bằng chứng, việc sửa. Sửa mọi mục Chưa và Một phần trước khi trình. Mục bỏ ghi lý do. Nếu có output của agent khác cho cùng đợt, so từng mục và lấy phần tốt hơn.

Bản tốt nhất phải có:
- [ ] Mọi số liệu (số gói, số file, số bảng) lấy từ lệnh vừa chạy, có lệnh đi kèm. Nguồn lỗi: một lượt vá OS 10/2026 đếm bằng danh sách apt cũ ra 75 gói, thực tế 281.
- [ ] Tài khoản, DB hoặc user chỉ gọi là "thừa" hay "lạ" sau khi map với `wp-config.php` mọi vhost và đối chiếu nhật ký phiên agent. Nguồn lỗi: 10/2026 một kết luận "DB thừa" sai suýt làm xoá DB đang dùng; 22/10/2026 lượt SSH của agent qua VPN trông như IP lạ.
- [ ] Mỗi việc ghi cấp site hay cấp server; việc cấp server có backup, diễn tập, probe và rollback thay cho "staging trước". Nguồn lỗi: đợt rà skill 24/10/2026 (đề xuất sec-1), plan hứa "staging trước" cho việc cấp server.
- [ ] Config sống chỉ đổi trong danh sách đã duyệt; việc phát sinh vào danh sách chờ duyệt kèm lệnh và rollback. Nguồn lỗi: 22/10/2026 agent tự đổi handler PHP mặc định và tắt php-fpm ngoài 4 đề xuất đã duyệt.
- [ ] Mọi backup qua `verify_backup.sh` đạt trước thay đổi đầu tiên. Nguồn lỗi: 16/10/2026 dump ra file 0 byte vì server không có `zstd`; 18/10/2026 `backup_pull.sh` báo xong dù server không có `rsync`.
- [ ] Mỗi khối `.htaccess`, vhost có probe hồi quy và `rollback.sh` trước khi báo xong. Nguồn lỗi: 17/10/2026 một khối áp tay làm 13 trang trả 404 khoảng 3,5 phút.
- [ ] Probe chặn chỉ nhận mã chặn (403); URL ngẫu nhiên chỉ nhận 404. Nguồn lỗi: 19/10/2026 theme trả 410 cho path lạ nên probe cũ báo đạt dù chưa có rule.
- [ ] Bản vá không có mã CVE trong changelog ghi "chưa xác minh trực tiếp", kèm phép thử và phương án chuyển. Nguồn lỗi: vá PHP 22/10/2026, 2 site còn chạy bản dựng lại chưa xác minh nên thêm 1 vòng chờ quyết.

## Gate

- [ ] Có backup đã qua `verify_backup.sh` (có `SHA256SUMS`) trước thay đổi đầu tiên.
- [ ] Không xoá file nào. File độc nằm trong quarantine có hash.
- [ ] Không có mật khẩu, key, slug đăng nhập trong chat, báo cáo hay log ngoài `.agent-secrets/`.
- [ ] Mỗi mốc thay đổi có `sitecheck` đạt và lệnh rollback. Khối `.htaccess`, vhost có `rollback.sh` do `apply_server_block.sh` sinh.
- [ ] `exposure_check.sh` và `persistence.sh` chạy cả trước và sau.
- [ ] Việc ngoài phạm vi nằm trong danh sách chờ duyệt, không tự làm.
- [ ] Quét lộ secret trong thư mục evidence và báo cáo trả mã 0.
- [ ] Đã chấm theo "Bản tốt nhất phải có"; mục bỏ có lý do.

## Anti-patterns

- Tin nhãn `benign` của Jev để bỏ qua file có dấu hiệu. Claude phải đọc file.
- Restore từ backup "sau dọn" mà không quét lại.
- Thêm `Header set` vào `.htaccess` trên OpenLiteSpeed. OLS bỏ qua lệnh này, header phải đặt ở vhost.
- Xoá site phụ trước khi grep domain của nó trong theme, postmeta, options của site chính.
- Kéo backup rồi báo xong mà không kiểm file. File 0 byte và lỗi `rsync: command not found` từng qua im lặng.
- Hứa "staging trước" cho việc cấp server như vhost production, `php.ini` dùng chung, `my.cnf`. Server không có staging cho các file này.
- Chạy WP-CLI bằng root. WordPress có thể chọn FTP và lỗi fatal. Chạy bằng user của web server.
- Đếm 5xx bằng awk gán cứng một cột cho mọi log trên server. Ngày 23–24/10/2026, 4 lane trên một site OLS báo "0 5xx" ở site phụ vì log của site đó đặt mã ở cột khác. Dùng `log_health.py` (`references/ung-cuu-su-co.md` mục 1).

## Changelog

- v1.8 (2026-10-27): nhánh C và `references/ra-tai-khoan-cdn.md`: rà Worker, route, token, thành viên, 2FA, audit log, SSL theo host; kiểm từ ngoài bằng UA trình duyệt và UA Googlebot; ranh giới agent đọc, người dùng bấm; 8 bước khi secret bị lộ. Nguồn: sự cố Worker độc trên tài khoản Cloudflare của site agency mẫu (phát hiện 26/10/2026, người dùng xoá 14:1x, agent kiểm lại sạch) và 4 lần lộ secret tháng 10/2026. Eval thêm 2 ca. Chưa có script đọc tài khoản: token hiện có trả 403 ở Workers Routes.
- v1.7.2 (2026-10-26): Bước 4 mục 7 và Bước 5 thêm phần site có CDN: khai IP trạm CDN tin cậy (đúng từng IP, OLS dạng `IPT`), Wordfence đọc `REMOTE_ADDR`, chặn đăng nhập ở edge, kiểm XFF giả. Nguồn: đợt CDN site VN 26/10/2026 (`cdn-speed-setup` v1.0).
- v1.7.1 (2026-10-26): `backup_pull.sh` kéo bằng `rsync -rlt` thay `-a` rồi `chmod -R u+rwX,go-rwx` thư mục đích. Lần kéo đầu từ site khoá học mẫu lỗi `fstatat: Permission denied` vì thư mục trên server mang mode 600 và `-a` chép mode đó về máy. openrsync của macOS không có `--chmod`.
- v1.7 (2026-10-25): sec-1, sec-4, sec-6, sec-7, sec-8, sec-9, sec-10. `references/checklist-hardening.md` mục 1 trỏ dòng Status hygiene trong Bảng ngưỡng của `seo-logfile-analysis` cho luật 410 và 404. Script `apply_server_block.sh` (backup md5, diễn tập, mã HTTP trước và sau, `rollback.sh`), `preflight_remote.sh`, `verify_backup.sh`; sửa `backup_pull.sh`, `site-backup.sh`, `backup-cnf.php`; probe URL ngẫu nhiên phải 404. Reference mới `ap-config-song.md`, `va-os-php.md`, `xoa-an-toan.md`. Bước 0 thêm preflight, `--no-tablespaces`, dump một phần `--no-create-info --replace`. Thêm Phân việc model, Tự phản biện, quét lộ secret ở Bước 6. Test offline `scripts/tests/test_sec_scripts.py`. Nguồn: `Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-skill-review_bao-cao_v1.md`.
- v1.6 (2026-10-24): `ung-cuu-su-co.md` mục 1: log OLS xoay vòng `.gz`, cột mã trạng thái khác nhau giữa các log trên cùng server, dòng "max children" không có giờ, PHP warning ở `lsws/logs/error.log`. Anti-patterns: awk cột cứng, đếm bằng `seo-logfile-analysis/scripts/log_health.py`. Nguồn: `Deliverables/GTV-Brand/GTV-Website/perf-20261020/toi-uu-khong-nang-vps-2310/dot1-2410/d1a/kiem-doc-lap.md`, HANDOFF gtvseo.com mục Bẫy.
- v1.5 (2026-10-19): chặn PHP trong `languages` và `upgrade` ngoài `uploads`, kèm biến thể path-info. Probe trong `exposure_default.txt` chỉ nhận 403: trước đây nhận cả 404, 410 nên site có theme trả 410 cho path lạ vẫn qua kiểm dù chưa có rule (đo 19/10 trên một site nội bộ). Ghi production đi qua `wp-staging-deploy`.
- v1.4 (2026-10-18): bẫy mục 7: `context` mới của vhost OpenLiteSpeed không kế thừa `extraHeaders` và Basic Auth của staging (gặp khi thêm charset cho `/llms.txt` trên site thứ hai, đã chép lại header, realm và kiểm `curl -sI` cả 2 bản).

- v1.3 (2026-10-18): checklist mục 4 thêm quy trình tắt plugin hết chức năng sau khi đổi theme (đã làm thật với plugin chấm sao trên site thứ hai: 200, không còn dấu plugin, không fatal) và luật cách ly theme, plugin không dùng. Mẫu mới `templates/backup-tu-dong/cai-lich-pull-mac.command` (lịch launchd, thoát `&` trong plist, `plutil -lint`). Bẫy: plist cần `&amp;`, `date -j` chỉ có trên macOS.
- v1.2 (2026-10-18): thêm từ đợt siết server site thứ hai sau cutover. Checklist: chặn web `mu-plugins/`, HSTS ở vhost, dòng backup tự động; bẫy `bind-address` của aaPanel, tắt pure-ftpd init.d, `tar` mã 1 với `pipefail`, phần việc panel để chủ site làm. Mẫu mới `templates/backup-tu-dong/` (site-backup.sh, backup-cnf.php, backup.cron, backup_pull.sh), đã chạy thật: DB 4,5 MB đủ 146 bảng, file 1,4 GB, kéo về máy 1,5 phút.
- v1.1 (2026-10-17): chuyển bản gốc vào SEO Production, viết lại cho mọi site WordPress có quyền server. Thêm `templates/mu-plugin-security.php`, hồ sơ server `00-client-context/wp-server.md`, phần sàng file bằng model (trước nằm ở skill riêng), bảng lệnh theo stack.
- v1.0 (2026-10-17): tạo mới từ 2 đợt ứng cứu 16–17/10. Chạy thử `exposure_check.sh` trên 2 site: bắt được `/wp-activate.php` 302 lộ slug đăng nhập ở cả 2.
