---
name: wp-host-optimize
description: "Tối ưu VPS chạy nhiều site WordPress (panel, OpenLiteSpeed, MySQL, Redis) mà không nâng gói: đo tải PHP theo nhóm actor, chặn trước PHP, WP-Cron hệ thống, trần PHP, MySQL, ổ đĩa, OS hết hạn. Dùng khi server chậm, thiếu RAM, OOM, ổ đầy, hoặc trước khi đề xuất nâng VPS."
metadata:
  version: "1.1.0"
---

# wp-host-optimize — tối ưu VPS WordPress không nâng gói

Quy trình đã chạy thật trên VPS site agency mẫu 23–27/10/2026: 4 vCPU, 3,9 GB RAM, aaPanel, OpenLiteSpeed, MySQL 5.7, Redis, 6 vhost. Sau Đợt 1, request PHP bên ngoài của site chính giảm 45% và PHP-giây giảm 54% (đo 48 giờ). TTFB request đầu sau khoảng nhàn giảm từ 2.466 ms còn 735 ms. Số 7 ngày: chờ đo 04/11/2026. Stack khác (Apache, Nginx, PHP-FPM) dùng cùng quy trình đo và chia đợt, đổi lệnh theo stack.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-host-optimize/scripts/`. Hồ sơ server nằm ở `00-client-context/wp-server.md`.

## Khi nào dùng

- Server chậm, TTFB trượt cache cao, pool PHP đầy, có OOM, swap cao, ổ trên 80%.
- Trước khi đề xuất nâng VPS hay đổi gói. Kết luận "cần nâng" phải có số đo theo mục 2.
- OS hoặc MySQL sắp hết hạn hỗ trợ.
- Không dùng khi: tối ưu PageSpeed theo template (`wp-pagespeed`), dựng CDN (`cdn-speed-setup`), ứng cứu xâm nhập hoặc tài khoản (`wp-security-hardening`), phân tích crawl SEO (`seo-logfile-analysis`).

## Luật

- Không chặn bot tìm kiếm và bot AI. Mọi khối chặn, nhóm robots và giới hạn tốc độ phải để Googlebot, Bingbot, AhrefsBot và mọi bot AI qua. Kiểm 7 ngày sau: request 200 của bot thật theo dải IP công bố không giảm.
- Không nâng trần PHP khi đỉnh do IP quét gây ra. Chặn nguồn trước PHP.
- Mỗi việc có lệnh trả lại một dòng. Sửa file cấu hình theo khối có dòng `BEGIN`/`END`, không chép đè cả file.
- Đọc giá trị live của mọi khoá trước khi plan đổi khoá đó.
- Chỉ đọc trường cấu hình cần thiết bằng whitelist trong code; không in cả `wp-config.php`, `.env`, token hay salt. `WP_CACHE_KEY_SALT` là namespace cache, không đồng nhất với các authentication salt; xử lý đúng loại giá trị nếu có sự cố, không tự xoay toàn bộ secret.
- Truy vấn DB có danh sách bảng/trường và giới hạn lô/thời gian. Không quét toàn DB bằng regex nặng rồi coi output thiếu là sạch; không huỷ query của tác vụ khác. Backup ngoài webroot, bản local có quyền hạn chế; không đưa dump vào deliverable chia sẻ.
- Khi ghi DB/cache hoặc báo health, đọc `wp-staging-deploy/references/bang-chung-sau-ghi.md`. Kiểm nguồn mới qua WordPress/object cache/HTML; số 0 lỗi cần log đọc được và giờ đầu/cuối cụ thể.
- Việc cấp server không có staging thay thế. Thay bằng backup, DRY, cổng và rollback đã thử (`wp-security-hardening` mục Luật).
- Restart OLS ảnh hưởng mọi vhost và nạp mọi cấu hình đang chờ. Kiểm theo `references/danh-muc-viec.md` mục 8 trước mỗi lần restart.
- Không đề xuất tăng phí tháng. OS hết hạn và thiếu tài nguyên đi đường ở `references/os-het-han.md`.
- Site khách cùng server: Lead báo khách trước. Mỗi site một ngày.

## Input

- Quyền SSH root và hồ sơ `wp-server.md`: panel, web server, vhost, đường dẫn log, trần PHP mỗi pool, lịch backup.
- IP văn phòng và IP khác của agent, để tách tải nội bộ.
- Khoá lane của các phiên đang sửa site, ví dụ `~/.cm/locks/`.
- Quyết định của Lead theo mục "Cần Lead quyết" của plan.

## Output

Thư mục `<thư mục web của dự án>/toi-uu-host-<ngày>/`:

- `moc.md`: số đo mốc và lệnh đo.
- `plan.md`: kết luận có cần nâng không, bảng mục tiêu đo được, bảng việc theo đợt (lệnh, lợi ích, rủi ro, đo trước và sau, trả lại, duyệt), việc không làm, câu cần Lead quyết.
- `phan-bien.md` và mục "Đã sửa theo phản biện" trong plan.
- Mỗi đợt: `bao-cao.md`, `rollback.md`, log chạy. Đo 48 giờ và 7 ngày ở `do-sau/`.

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code | `php_tai.sh`, `tong_hop_php_tai.py`, `rtreport_*`, lệnh `/proc`, `free`, `df`, SQL | Dùng. Mọi số liệu lấy từ lệnh |
| Jev | Phân loại mục đích của UA mới trước khi thêm vào R6 hay robots | Dùng khi có UA lạ. Phép kiểm còn lại là số đo, mã HTTP, header, dải IP công bố: có đáp án tất định |
| EmbeddingGemma 2 | – | Không dùng. Skill không có việc so nghĩa |
| Claude | Chẩn đoán, viết plan, phản biện, chạy lệnh sau khi duyệt, đọc số đo | Dùng |

## Quy trình

### Bước 0 — kiểm tool

Chạy "python3 tools/capabilities.py check --need 'python3,ssh'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Kiểm thêm trên server: `ssh <host> 'command -v gawk'`. Thiếu `gawk` thì `php_tai.sh` không chạy được.

### Bước 1 — đo mốc, chỉ đọc

Đọc `references/do-moc.md`. Đo ít nhất 24 giờ ngày thường, sau thay đổi gần nhất. Mở bộ lấy mẫu `.rtreport` trước, để có số hàng chờ pool.

### Bước 2 — chẩn đoán

| Dấu hiệu | Kết luận ở site mẫu |
|---|---|
| Load dưới số vCPU, pool đầy theo từng đợt ngắn | Không thiếu CPU. Đỉnh do IP quét hoặc do lane |
| Một IP chiếm phần lớn phút chạm trần | Chặn trước PHP. Nâng trần thì IP đó vẫn lấp đầy |
| mysqld RSS gấp 3 lần buffer pool | Cấu hình MySQL lãng phí: biến động, `performance_schema`, arena malloc |
| Tổng trần PHP × RAM mỗi tiến trình vượt RAM | Hạ trần pool ít dùng và pool site khách |
| Request đầu sau khoảng nhàn chậm gấp 2–3 lần miss thường | Tiến trình PHP bị dừng khi nhàn: `LSAPI_PGRP_MAX_IDLE` |
| SQL chiếm phần nhỏ của TTFB miss | Thêm RAM không giảm TTFB. Đo plugin trên staging |

### Bước 3 — viết plan theo đợt

Chọn việc từ `references/danh-muc-viec.md`. Chia đợt theo mục 1 của file đó. Trong mỗi đợt, xếp việc theo lợi ích trên rủi ro. Ghi lợi ích là trần trên khi chưa trừ phần trùng với khối đã chạy. Ghi việc cần đo thêm và việc không làm, kèm lý do.

### Bước 4 — phản biện

Giao một agent khác hoặc một lượt riêng phản biện plan trước khi trình, nếu Lead cho dùng agent phụ. Nếu không, tự chấm theo checklist dưới. Phản biện plan site mẫu 23/10/2026 tìm 23 điểm, gồm lệnh apt sai, số lợi ích phóng đại và nguyên nhân OOM ghi sai.

### Bước 5 — áp theo đợt

- Lấy khoá server trước khi ghi. Không ghi khi lane khác đang đo hay đang giữ khoá staging.
- Việc cấp site: staging trước, rồi production.
- Đợt đêm chạy bằng script có cổng, DRY và tự trả lại (`references/danh-muc-viec.md` mục 9).
- Sau mỗi việc: mọi site 200, 0 5xx mới (`seo-logfile-analysis/scripts/log_health.py`), 0 PHP fatal mới, `oom_kill` không tăng.
- Kiểm wp-admin bằng phiên đăng nhập tạm của WP-CLI: ghi token vào `WP_Session_Tokens` của user kiểm, hạn 10 phút, kiểm trang admin, rồi xoá token. File tạm đặt ở thư mục user web đọc được. Không nhờ Lead đăng nhập. Lỗi đã gặp 27/10/2026: file tạm trong thư mục `mktemp` của root làm lệnh lỗi 3 lần và để lại token mồ côi.
- Ghi giờ áp, trước và sau tức thời, lệnh trả lại vào `bao-cao.md` của đợt.

### Bước 6 — đo sau

Đo 48 giờ và 7 ngày theo `references/do-moc.md` mục 4. So với mục tiêu và ngưỡng xét lại của plan. Chạm ngưỡng thì xét đổi máy cùng giá.

### Tự phản biện trước khi trình

Chấm plan theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ.

Bản tốt nhất phải có:
- [ ] Mốc đo sau thay đổi gần nhất, và lợi ích ghi trần trên khi chưa trừ phần trùng. Nguồn lỗi: plan site mẫu 23/10/2026 tính lợi ích trên 48 giờ phần lớn trước một khối chặn đã chạy, phản biện ghi "số phóng đại".
- [ ] Nguyên nhân OOM đọc từ kernel log và log pool theo giờ, không suy từ số đếm. Nguồn lỗi: plan bản 1 ngày 23/10/2026 ghi sai nguyên nhân OOM 20/10 và xếp việc hạ trần site khách xuống đợt cuối.
- [ ] Việc chặn hay giới hạn tốc độ có phép tách bot thật theo dải IP công bố, IP văn phòng và callback thanh toán trước khi áp. Nguồn lỗi: bản 1 của việc `dynReqPerSec` có thể chặn Bingbot và fetcher AI, 23/10/2026.
- [ ] Mọi khoá sắp đổi đã đọc giá trị live. Nguồn lỗi: 24/10/2026 việc tắt Live Traffic của Wordfence không có tác dụng, vì khoá đã bằng 0 từ trước.
- [ ] Lệnh OS: mô phỏng trước, `dist-upgrade` trong một `systemd-run`, hold gói từ repo ngoài, backup ngoài máy. Nguồn lỗi: phản biện 23/10/2026 mục 2.1, lệnh apt bản 1 chỉ chạy `update` trong `systemd-run` và giữ lại kernel ESM.
- [ ] Bộ đo chạy nền có nối lại, và số dùng trong báo cáo đã qua kiểm độ phủ. Nguồn lỗi: đo 48 giờ ngày 26/10/2026 không có số hàng chờ pool, vì bộ lấy mẫu chết từ 24/10 13:45.
- [ ] Nhóm nội bộ có IP văn phòng và mọi IP của agent. Nguồn lỗi: 27/10/2026 lượt đo của lane bị tính là IP quét, chiếm 92% PHP-giây bên ngoài.
- [ ] Mỗi lần restart OLS có bước kiểm cấu hình đang chờ của lane khác. Nguồn lỗi: chuẩn bị Đợt 2a ngày 26/10/2026, restart sẽ nạp thay đổi keep-alive và QUIC của lane khác.

## Gate

- [ ] Có `moc.md` với lệnh đo và cửa sổ.
- [ ] Plan có kết luận cần nâng hay không, kèm số đo.
- [ ] Mỗi việc có lệnh trả lại, phép đo trước và sau, cấp duyệt.
- [ ] Không việc nào chặn bot tìm kiếm hay bot AI.
- [ ] Đợt đã áp có `bao-cao.md`, `rollback.md`, 0 5xx mới, `oom_kill` không tăng.
- [ ] Báo lợi ích từ số 48 giờ và 7 ngày, không từ số tức thời.
- [ ] Đã chấm theo "Bản tốt nhất phải có"; mục bỏ có lý do.

## Anti-patterns

- Đề xuất nâng VPS từ cảm giác "server chậm" hay từ một ảnh chụp `top`.
- So tổng request trước và sau mà không tách nhóm actor. Cuối tuần ít người dùng, máy quét không theo tuần.
- Purge toàn site sau khi đổi option cache.
- Chép đè `.htaccess` hay vhost bằng bản backup trong khi lane khác đã sửa file đó.
- Dùng `autoremove` khi gỡ kernel cũ.

## Changelog

- v1.1.0 (2026-11-05): đọc cấu hình theo whitelist, phân biệt cache salt/auth salt, truy vấn DB có giới hạn và backup riêng tư; bổ sung postcondition cache và bằng chứng health thay vì tin mã thoát.
- v1.0.1 (2026-10-27): thêm từ file gom bài học của phiên tốc độ: sandbox A/B và PCRE2 khi nâng OLS, nhả khoá sau cache hit, purge CLI chưa đủ làm bằng chứng, redirect plugin sang rule tĩnh, mu-plugin bớt việc PHP, kiểm wp-admin bằng phiên tạm.
- v1.0 (2026-10-27): tạo từ đợt tối ưu VPS site agency mẫu 23–27/10/2026 (plan, phản biện 23 điểm, Đợt 1, Đợt 2a, đo 48 giờ, 5 lane máy chủ ngày 27/10). Script `php_tai.sh`, `tong_hop_php_tai.py`, `rtreport_mau.sh`, `rtreport_phan_tich.py`, test 6 ca. Chạy thật `php_tai.sh` trên server mẫu 27/10/2026: phát hiện thiếu IP agent trong nhóm nội bộ, script tự thêm IP phiên SSH. Chưa có: số 7 ngày (04/11), kết quả gắn Ubuntu Pro (đêm 29→30/10), kết quả `dynReqPerSec`.
