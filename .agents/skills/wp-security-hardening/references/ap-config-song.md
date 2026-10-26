# Áp cấu hình sống: cấp site, cấp server, script áp khối

Đọc file này ở Bước 4 trước khi sửa `.htaccess`, vhost hoặc cấu hình server. Nguồn: ít nhất 7 lần áp khối bằng tay trên 2 site WordPress (OpenLiteSpeed, aaPanel) 17–18/10/2026. Một lần áp làm 13 trang trả 404 trong khoảng 3,5 phút (17/10).

## 1. Cấp site hay cấp server

Ghi cấp của từng việc vào plan. Không hứa "staging trước" cho việc cấp server.

| Cấp | Ví dụ | Đường lên production |
|---|---|---|
| Site, có staging | Theme, mu-plugin, `.htaccess` riêng của site | Staging trước, rồi `wp-staging-deploy` |
| Server, không có staging | Vhost production, `php.ini` của bản PHP dùng chung, `my.cnf`, `sshd`, firewall, handler PHP mặc định | Backup có md5, diễn tập, probe, rollback sẵn |
| Ứng cứu khẩn (nhánh A) | Rule chặn file độc đang bị gọi | Sửa thẳng production sau khi backup |

- Việc cấp server ảnh hưởng mọi site trên máy. Kiểm các site khác sau khi áp.
- Restart web server chỉ trong giờ thấp điểm hoặc khi người duyệt cho phép trong đợt đó.

## 2. Áp khối `.htaccess` hoặc vhost bằng script

Dùng `skills/wp-security-hardening/scripts/apply_server_block.sh` cho mọi khối `.htaccess` và vhost. Script làm các việc sau:

1. Kiểm công cụ trên server và quyền ghi file đích.
2. Bọc khối bằng `# BEGIN <nhãn> (<ngày>)` và `# END <nhãn>`. Chạy lại cùng nhãn: nội dung giống thì không làm gì, nội dung khác thì thay đúng khối đó.
3. Backup file đích trên server (`/root/backup-<nhãn>-<giờ>/`) và về máy (`~/Backups/<alias>/<ngày>/<nhãn>-pre/`), so md5, giữ owner và mode.
4. Chụp mã HTTP các path hồi quy trước và sau khi áp.
5. Sinh `rollback.sh` cạnh bản backup ở máy.
6. Tự rollback khi mã HTTP đổi hoặc site trả 5xx.

Mặc định script chỉ diễn tập. Thêm `--apply` để ghi thật.

`my.cnf` và `sshd` làm tay theo `references/checklist-hardening.md` mục 6. Mỗi lần sửa hai file này khác nhau. Sửa sai `sshd` có thể khoá luôn đường vào server.

### Chuẩn bị

1. Viết khối vào file trong thư mục evidence, ví dụ `<ev>/block-sec-r1.txt`.
2. Chép các dòng probe liên quan từ `scripts/exposure_default.txt` vào `<ev>/probes.txt`. Probe là path khối này cố ý đổi mã, ví dụ `403 /wp-content/uploads/test-wps-nonexistent.php`.
3. Ghi path hồi quy vào `<ev>/paths.txt`: `/`, 1 bài, 1 ảnh trong `uploads`, `/wp-admin/admin-ajax.php`, `/wp-login.php`. Không đưa path mà khối cố ý đổi mã vào file này.
4. Nếu site là staging có Basic Auth, nạp `STAGING_AUTH` từ file secret của đợt vào môi trường. Không gõ giá trị vào lệnh.

### Lệnh mẫu

Chạy từ root repo. Ví dụ dưới là site giả `example.vn` trên OpenLiteSpeed.

```bash
S=skills/wp-security-hardening/scripts
# Diễn tập: đọc server, in diff, chụp mã HTTP, không ghi gì
bash "$S/apply_server_block.sh" --alias site-vps --target htaccess \
  --remote-file /www/wwwroot/example.vn/.htaccess --block <ev>/block-sec-r1.txt \
  --mark sec-r1 --site-url https://example.vn --probes <ev>/probes.txt --paths <ev>/paths.txt
# Ghi thật, restart OpenLiteSpeed (giờ thấp điểm)
bash "$S/apply_server_block.sh" ... --restart 1 --apply
```

- Khối phải nằm sau một dòng có sẵn: thêm `--after '<biểu thức ERE>'`. Không có dòng khớp thì script không chèn. Đọc diff ở lượt diễn tập trước khi thêm `--apply`.
- Nginx: `--restart 1 --restart-cmd 'nginx -t && systemctl reload nginx'`.
- Apache với `.htaccess`: không cần restart.
- `--check-cmd 'cmd {FILE}'` chạy lệnh kiểm cú pháp trên file mới. Lệnh lỗi thì script không ghi.

### Đọc mã thoát

| Mã | Nghĩa | Việc làm |
|---|---|---|
| 0 | Xong hoặc khối đã có | Ghi đường dẫn `rollback.sh` vào HANDOFF |
| 2 | Sai tham số | Sửa lệnh |
| 3 | Thiếu công cụ hoặc không ghi được file đích | Đọc dòng "thiếu:", báo người vận hành |
| 4 | Backup lệch md5 | Dừng. Server chưa bị sửa |
| 5 | Hồi quy, đã rollback | Đọc bảng path trước và sau, sửa khối, chạy lại diễn tập |
| 6 | Khối đã ghi nhưng probe không đạt | OpenLiteSpeed chưa restart thì chạy lại với `--restart 1`. Nếu vẫn không đạt, chạy `rollback.sh` |
| 7 | Ghi file lỗi hoặc lệnh kiểm cú pháp báo lỗi | Đọc dòng LỖI. Nếu dòng đó yêu cầu chạy `rollback.sh`, chạy ngay. Các trường hợp khác: file gốc chưa bị thay |
| 8 | Rollback không khôi phục được | Dừng mọi việc. Khôi phục tay từ bản backup ở máy, báo người duyệt |

Sau mã 0: chạy `sitecheck.sh` cho mốc đó và kiểm các site khác trên cùng server vẫn trả 200.

## 3. HSTS tăng dần

Đặt HSTS ở `extraHeaders` của vhost theo `references/checklist-hardening.md` mục 1. HSTS cần người duyệt. Tăng `max-age` theo từng nấc. Mỗi nấc giữ ít nhất bằng thời gian của nấc đó trước khi lên nấc sau:

| Nấc | `max-age` | Kiểm trước khi lên nấc sau |
|---|---|---|
| 1 | `300` (5 phút) | `curl -sI` trên HTML, file tĩnh, 301, 403 có header. Mọi trang chạy HTTPS |
| 2 | `604800` (1 tuần) | Không có báo lỗi chứng chỉ, không có trang HTTP lẫn |
| 3 | `2592000` (1 tháng) | Như nấc 2 |
| 4 | `31536000` (1 năm) | Giữ lâu dài |

- Thêm `includeSubDomains` chỉ khi mọi subdomain có HTTPS, gồm staging và mail.
- Rollback ở nấc 1: bỏ header, hoặc đặt `max-age=0`. Trình duyệt đã nhận header giữ HSTS đến khi hết `max-age`, nên nấc thấp giúp rollback nhanh.
- Sau khi aaPanel ghi lại vhost (đổi PHP, đổi SSL), kiểm lại header.
