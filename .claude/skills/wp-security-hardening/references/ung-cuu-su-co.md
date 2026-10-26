# Ứng cứu sự cố: tìm IOC, sàng file, cách ly, dấu bám trụ

Đọc file này ở nhánh A. Các mẫu dưới lấy từ 2 đợt thật 10/2026: cửa sau dev trong theme, webshell của site khác cùng server, script tiêm vào bài, webshell trong thư mục plugin.

## 1. Nguồn bằng chứng

| Nguồn | Lệnh hoặc vị trí | Ghi chú |
|---|---|---|
| Log web | Theo `wp-server.md` (aaPanel + OLS: `/www/wwwlogs/<site>_ols.access_log*`) | Thường chỉ giữ khoảng 10 ngày. Bản xoay vòng có thể là `.gz`: đọc bằng `zgrep`/`zcat`. Đếm mã trạng thái bằng `skills/seo-logfile-analysis/scripts/log_health.py` hoặc tách theo `"` rồi đọc trường 3. Không gán cứng `$9`/`$10`: trên cùng server, log có trường đầu `'-` đặt mã ở `$10`, log không có trường đó đặt mã ở `$9` |
| Log lỗi OLS | `/www/wwwlogs/<site>_ols.error_log`, `/usr/local/lsws/logs/stderr.log`, `/usr/local/lsws/logs/error.log` | PHP warning của site có thể chỉ nằm ở `lsws/logs/error.log`. Dòng "max children" ở `stderr.log` không có giờ: so tổng số dòng trước và sau thay đổi |
| Log panel hosting | aaPanel: bảng `logs` trong DB panel. cPanel: `/usr/local/cpanel/logs/` | Ghi đăng nhập, terminal, restart |
| Đăng nhập server | `last -F`, `journalctl -u ssh` | Syslog giữ khoảng 7 ngày |
| mtime, ctime file | `find <root> -newer <mốc> -printf '%TY-%Tm-%Td %p\n'` | Kẻ tấn công có thể sửa mtime. Đối chiếu ctime |
| Wordfence cũ | Bảng `wp_wfissues`, `wp_wflogins` | Cho biết plugin từng bị báo lỗ hổng |
| Option `recently_edited` | `wp option get recently_edited` | Ghi file đã sửa bằng trình sửa file của WordPress |

Ghi mỗi IOC theo dạng: IOC, nơi thấy, thời điểm, trạng thái. Ghi timeline có bằng chứng cho từng mốc. Không đoán đường vào. Liệt kê các ứng viên và mức chắc chắn.

Trước khi ghi một tài khoản hoặc một thay đổi là IOC:

- [ ] Audit tài khoản đủ 4 lớp và MySQL: user hệ thống cùng `authorized_keys`, panel hosting, admin WordPress cùng application password, user MySQL. Map `DB_USER` với `wp-config.php` của mọi vhost, gồm staging, trước khi gọi một user là lạ hoặc thừa.
- [ ] Đối chiếu thời điểm, IP và key của thay đổi với nhật ký phiên agent và người vận hành (HANDOFF, log lệnh). Agent chạy qua VPN trông như IP lạ: ngày 22/10/2026, một lượt SSH từ IP nước ngoài bằng key của agent là agent, không phải xâm nhập.

## 2. Sàng file bằng luật và model

Mỗi lớp chỉ nhận phần lớp trước chưa chốt. Đặt input và output trong thư mục evidence. `<wp>` là lệnh WP-CLI trong `wp-server.md`.

1. Checksum: `<wp> --path=<root> core verify-checksums --skip-plugins --skip-themes`, rồi `plugin verify-checksums --all` cùng tham số.
2. Quét phần không qua checksum bằng scanner chỉ đọc. Đưa core và plugin đã khớp checksum vào `--skip`:

   ```bash
   ssh <alias> "python3 - <root> --skip wp-admin,wp-includes,<plugin đã khớp>" \
     < tools/ai-assist/scan_files.py > <ev>/scan.jsonl
   ```

3. So excerpt với bộ mẫu webshell bằng EmbeddingGemma. Bộ mẫu dương là file độc đã cách ly ở các đợt trước (giữ trong quarantine, không commit). Thiếu bộ mẫu thì bỏ bước này.

   ```bash
   jq -c 'select(.excerpt | startswith("[config") | not) | {id, text: .excerpt}' scan.jsonl > emb_q.jsonl
   ~/.venvs/embeddinggemma/bin/python -I tools/ai-assist/emb.py nn --query emb_q.jsonl \
     --docs pos_shell.jsonl --k 3 --qprompt SentenceSimilarity --dprompt SentenceSimilarity \
     --max-tokens 512 --out emb_nn.jsonl
   ```

4. Chuyển file có dấu hiệu, vị trí lạ hoặc cosine từ 0,90 sang Jev. Bỏ file cấu hình: Claude đọc trực tiếp trên server.

   ```bash
   jq -c 'select(((.signals|length) > 0 or .odd_location) and (.excerpt | startswith("[config") | not))
     | {id, state: {location, signals, excerpt}}' scan.jsonl > jev_mal_in.jsonl
   python3 -I tools/ai-assist/jev.py --task tools/ai-assist/tasks/malware-triage.json \
     --in jev_mal_in.jsonl --out jev_mal_out.jsonl --budget 0.1
   ```

5. Danh sách Claude đọc gồm:
   - mọi file lệch checksum;
   - mọi file `odd_location` hoặc có `epoch_name`, `req_input_exec`, `file_write_input`, `shell_names`, dù Jev trả nhãn gì;
   - mọi nhãn `malicious`, `suspicious`, `unknown`, mọi dòng `route: review`;
   - mọi file có `exec_request_input` từ 0,5 hoặc cosine từ 0,90.
6. Claude đọc file thật trên server rồi kết luận từng file.

Gửi dữ liệu site khách qua Jev: hỏi người duyệt trước lượt đầu. Một lượt khoảng 500 file tốn khoảng 0,03 USD.

## 3. Quét DB

Chạy bằng một file `wp eval-file`, in JSON, không in nội dung nhạy cảm.

- Bài viết: `post_content` chứa `<script`, `eval(`, `atob(`, `document.write`, domain lạ, `String.fromCharCode`. Tính cả revision.
- Postmeta, options: giá trị chứa `<script`, `base64_decode`, `eval(`, URL ngoài lạ. Lành thường gặp: `theme_mods_*` chứa GTM, Font Awesome.
- `siteurl`, `home` đúng domain.
- User: danh sách administrator, email, ngày tạo. Option ẩn user (ví dụ `wal_hidden_users`).
- Application password: tên, ngày tạo, lần dùng cuối, IP cuối.
- Cron WordPress: hook không có callback là dấu vết plugin đã gỡ, không chạy.
- Attachment: file `.zip`, `.php` tải lên gần thời điểm sự cố, user tải lên.

Gỡ mã tiêm:

1. Lưu khối gốc (ID, trường, đoạn mã) ra JSONL rồi nén, đặt trong thư mục backup quarantine.
2. Gỡ bằng `$wpdb->update`, không gọi `wp_update_post`, để không tạo revision và không đổi `post_modified`.
3. Quét lại: 0 chuỗi nhận diện trong posts, postmeta, options. Purge cache 2 lần (HTML và object cache).

## 4. Dấu bám trụ server

Chạy `scripts/persistence.sh`. Đọc kết quả theo bảng:

| Mục | Bình thường | Cần đọc kỹ |
|---|---|---|
| Unit systemd ngoài package | Dịch vụ của panel, web server | Unit khác, nhất là ExecStart trỏ vào `/tmp`, `/dev/shm` |
| `rc.local`, `ld.so.preload`, profile.d | Không có | Có nội dung |
| SUID/SGID ngoài package | Không có | Có file |
| File chạy trong tmp | Thư mục tạm của web server, WP-CLI | Script `.sh`, `.php`, `.so`, file ẩn |
| Tiến trình user web server | Chỉ PHP và web server | Tiến trình khác |
| Kết nối ra ngoài | Kết nối biết rõ | IP lạ, cổng lạ |
| Crontab | Gia hạn SSL, watchdog DB | Job tải script về |
| `authorized_keys` | Key đã biết | Key lạ |
| File của user web server ngoài web root | Không có | Có file mới |

Script mặc định user web server là `www` và web root `/www/wwwroot/` (aaPanel). Stack khác: truyền `WWW_USER` và `WEBROOT`, ví dụ `ssh <alias> "WWW_USER=www-data WEBROOT=/var/www bash -s" < scripts/persistence.sh`.

## 5. Cửa sau trong theme, plugin

Grep theme và plugin không có checksum:

```bash
grep -rnE "register_rest_route|wp_set_auth_cookie|wp_create_user|set_role\(['\"]administrator|base64_decode|eval\(|assert\(|create_function|\\\$_(POST|GET|REQUEST)\[[^]]+\]\s*\)" <thư mục>
```

- Route REST không kiểm quyền, hàm tạo user hoặc đặt cookie đăng nhập theo tham số là cửa sau, kể cả khi dev viết với ý tốt.
- Script dev có khoá tĩnh trong query string: ghi lại, báo dev, chặn hoặc chuyển vào quarantine theo phạm vi duyệt.
- Plugin premium không licence không có checksum công khai. Chỉ quét pattern được. Ghi giới hạn này vào báo cáo.

## 6. Cách ly

- Thư mục quarantine: `/root/<site>-offweb-<YYYY-MM-DD>/` hoặc `/root/<site>-security-review-<timestamp>/`, chmod 600, ngoài mọi docroot.
- Giữ đường dẫn gốc trong cấu trúc thư mục quarantine. Ghi `SHA256SUMS`.
- File của site khác cùng server: cách ly, báo chủ site hoặc dev, đổi mật khẩu DB nếu webshell chứa credentials.
- Sau cách ly: URL cũ trả 403, 404 hoặc 410. Rule `.htaccess` chặn theo đuôi file trả 403 cả khi file đã chuyển đi.

## 7. Sau sự cố

- Tăng thời gian lưu log web và syslog để lần sau truy được đường vào.
- Đổi mọi mật khẩu từng nằm trong sheet chung hoặc file cấu hình lộ. Không chép file `.env` mới vào sheet.
- Báo dev của các theme có cửa sau rằng code đã gỡ.
- Theo dõi GSC Security issues và Manual actions trong 2 tuần.
