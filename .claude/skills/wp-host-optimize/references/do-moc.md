# Đo mốc và đo sau

Mọi lệnh ở file này chỉ đọc. Chạy với `nice -n 19` khi lệnh quét log. Cách đo rút từ đợt tối ưu VPS site agency mẫu 23–27/10/2026 (aaPanel, OpenLiteSpeed 1.8–1.9, MySQL 5.7, Redis 7, 6 vhost trên 4 vCPU và 3,9 GB RAM).

## 1. Chuẩn bị

- Ghi vào `00-client-context/wp-server.md`: alias SSH, panel, đường dẫn log, tên vhost, trần PHP mỗi pool, IP văn phòng, IP khác của agent.
- Kiểm `logFormat` của vhost chính có `%D` và cột trạng thái cache, theo mẫu ở đầu `scripts/php_tai.sh`. Nếu thiếu, đề xuất thêm 2 cột ở cuối, giữ nguyên các cột cũ. Việc này đổi config sống: Lead duyệt. Thiếu 2 cột thì số PHP là trần trên và không có PHP-giây.
- Ghi giờ các khối chặn hay thay đổi đã chạy gần đây. Mốc phải đo sau thay đổi cuối cùng. Lỗi đã gặp 23/10/2026: lợi ích của khối `.htaccess` mới tính trên 48 giờ phần lớn trước một khối chặn đã chạy lúc 13:46, nên số giảm bị phóng đại.

## 2. Bộ đo

| Câu hỏi | Lệnh | Đọc thế nào |
|---|---|---|
| Ai tiêu PHP | `ssh <host> "WSTART='…' VHS='…' NOIBO='…' bash -s" < scripts/php_tai.sh > php_tai.txt`, rồi `python3 -I scripts/tong_hop_php_tai.py php_tai.txt --tran <trần pool>` | Bảng actor × endpoint, PHP/ngày, PHP-giây/ngày, phút chạm trần, IP và path tốn nhất |
| Pool có xếp hàng không | `nohup bash scripts/rtreport_mau.sh --ssh 'ssh <host>' --out rtreport.log &`, rồi `python3 -I scripts/rtreport_phan_tich.py rtreport.log` | Giây có `WAITQUE_DEPTH > 0` theo pool. `BLOCKED_IP` phải rỗng với IP bot thật và IP văn phòng |
| CPU | `uptime`, `vmstat 5 12` | Load 1 phút dưới số vCPU, `wa` thấp: CPU không nghẽn |
| RAM | `free -m`; `grep -E 'VmRSS|VmSwap' /proc/$(pgrep -x mysqld)/status`; `grep oom_kill /proc/vmstat` | RAM khả dụng giờ thấp điểm, mysqld RSS + swap, số lần OOM |
| Nguyên nhân OOM | `journalctl -k | grep -i -A20 'invoked oom-killer'` | Đọc danh sách tiến trình lúc OOM. Không suy nguyên nhân từ số đếm |
| Pool đầy theo log | `grep -c 'max children' /usr/local/lsws/logs/stderr.log` | Chỉ số phụ. Dòng này không có giờ, và OLS xếp hàng ở `maxConns` mà không ghi log |
| PHP khởi động nguội | Trong access log, lấy request miss 200 đứng sau một khoảng từ 60 giây không có request PHP nào. So `%D` của nhóm này với miss thường | Request đầu sau khoảng nhàn chậm hơn nhiều so với miss thường (site mẫu: 2.466 ms so với 930 ms): xem `LSAPI_PGRP_MAX_IDLE` |
| TTFB trượt cache | `curl -o /dev/null -s -w '%{time_starttransfer}'` với tham số phá cache, tối đa 5 URL × 5 lượt | Mỗi lượt phá cache có thể sinh file CSS gộp mới. Không đo nhiều hơn |
| Ổ đĩa | `df -h /`; `du -xh --max-depth=2 / 2>/dev/null | sort -h | tail -30` | Log chưa nén, CSS gộp, backup cũ, kernel cũ |
| MySQL | `SHOW GLOBAL STATUS` (`Created_tmp_disk_tables`, `Key_reads`, `Innodb_buffer_pool_reads`), digest của `performance_schema` nếu bật | Tỉ lệ bảng tạm trên đĩa, hit buffer pool |

Gán actor:

- `php_tai.sh` tự tính IP của server và IP của phiên SSH đang chạy là nội bộ. Truyền thêm IP văn phòng và IP thứ hai của agent qua `NOIBO`. Lỗi đã gặp 27/10/2026: thiếu IP của máy agent, lượt đo của lane bị tính là IP quét và chiếm 92% PHP-giây bên ngoài.
- "IP quét" là IP có ít nhất 20 lượt 404 chiếm từ 50% request động, hoặc ít nhất 2 lượt gọi đường dẫn khai thác. Bot thật (Googlebot, Bingbot, bot AI) không bao giờ vào nhóm này.
- UA Googlebot từ IP ngoài dải Google công bố là phép thử của người hoặc bot giả. Lỗi đã gặp 26/10/2026: 350 PHP/ngày nhóm "Google, Bing" đến từ một IP Việt Nam.

## 3. Bộ lấy mẫu chạy nền

- Bộ lấy mẫu tự nối lại khi phiên SSH rớt. Trước khi dùng số, chạy `rtreport_phan_tich.py` và đọc độ phủ, các khoảng mất mẫu và cảnh báo mẫu cuối cũ.
- Reboot server xoá `/tmp`. Sau reboot, kiểm OLS đã tạo lại `.rtreport`.

## 4. So trước và sau

- So theo nhóm actor, không so tổng. Máy quét và bot không theo ngày trong tuần. Người dùng thì theo.
- Quy về /ngày theo độ dài cửa sổ. Ghi rõ cửa sổ trước và sau, kể cả khi hai cửa sổ khác ngày trong tuần.
- Tách chỉ số của site đang tối ưu (request PHP, PHP-giây, hàng chờ, TTFB) khỏi chỉ số toàn server (RAM, swap, `oom_kill`, mysqld). Đợt sau chạm site khác làm lẫn chỉ số toàn server.
- Lịch đo: ngay sau áp (tức thời), 48 giờ, 7 ngày. Số tức thời không phải lợi ích. Báo lợi ích từ số 48 giờ và 7 ngày.
- Kết quả site mẫu: sau Đợt 1, request PHP bên ngoài 5.525 → 3.012/ngày (−45%), PHP-giây 5.983 → 2.754/ngày (−54%), TTFB request đầu sau khoảng nhàn 2.466 → 735 ms. mysqld, swap và ổ chưa đạt sau 48 giờ, chờ đợt config. Số 7 ngày: chờ đo 04/11/2026.

## 5. Ngưỡng xét lại

Đặt ngưỡng trong plan trước khi áp. Site mẫu dùng: trong 7 ngày, RAM khả dụng thấp nhất dưới 800 MB, hoặc swap trên 1 GB, hoặc `oom_kill` tăng, hoặc pool site chính xếp hàng tổng trên 3 phút mỗi ngày. Khi chạm ngưỡng, xét đổi máy cùng giá (`references/os-het-han.md` mục 3). Không đề xuất tăng phí tháng.
