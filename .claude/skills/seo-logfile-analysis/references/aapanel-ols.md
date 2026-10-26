# Log trên aaPanel + OpenLiteSpeed

Mục đích: tìm đúng file log, đọc đúng định dạng và kéo log về máy an toàn khi site chạy aaPanel với OpenLiteSpeed (OLS). Nạp ở Bước 0b khi log còn nằm trên server.

Nguồn: file cấu hình vhost và log thật của gtvseo.com (site nội bộ GTV), 10/2026. Số có nhãn site là số của site đó, không phải chuẩn.

## 1. Đường file

| File | Đường dẫn | Dùng cho |
|---|---|---|
| Access log của vhost | `/www/wwwlogs/<vhost>_ols.access_log` | Bước 1–3, kỳ hôm nay |
| Access log đã xoay vòng | `/www/wwwlogs/<vhost>_ols.access_log.<YYYY_MM_DD>[.NN].gz` | Kỳ nhiều ngày |
| Error log của vhost | `/www/wwwlogs/<vhost>_ols.error_log` | Lỗi rewrite, lỗi truy cập |
| Error log của server | `/usr/local/lsws/logs/error.log` | PHP warning |
| stderr của server | `/usr/local/lsws/logs/stderr.log` | "max children", dòng không có giờ |
| Cấu hình vhost | `/www/server/panel/vhost/openlitespeed/detail/<vhost>.conf` | Khối `accesslog`: `logFormat`, `rollingSize`, `keepDays` |

- `<vhost>` thường là tên miền chính. Một server có thể chạy nhiều vhost: bản tiếng Anh, staging, site khác. Mỗi vhost có file log riêng và có thể có `logFormat` riêng.
- Đọc khối `accesslog` trong file cấu hình vhost để biết định dạng. Chỉ đọc. Sửa file này là sửa cấu hình sống (§4).
- Xác định kỳ log thật bằng tên file cũ nhất. Không tin số `keepDays`. Ví dụ gtvseo.com 19/10/2026: server chỉ còn log từ 06/10, tức 13 ngày.
- Hồ sơ server của dự án nằm ở `00-client-context/wp-server.md` của instance. Không ghi host, IP hay slug đăng nhập vào report.

## 2. Kéo log về máy

Log chứa IP người dùng. Giữ log trên máy. Không đưa log vào report, Jev hay dịch vụ ngoài.

1. Liệt kê file trên server. Ghi danh sách ra file:

   ```bash
   ssh -o BatchMode=yes -o LogLevel=ERROR <alias> 'cd /www/wwwlogs && ls <vhost>_ols.access_log.2*' > "<W>/list.txt"
   ```

2. Đọc danh sách từng dòng. Bỏ dòng không khớp tên file. Tải từng file:

   ```bash
   while IFS= read -r f; do
     case "$f" in <vhost>_ols.access_log.2*) ;; *) continue ;; esac
     case "$f" in
       *.gz) ssh <alias> "cat /www/wwwlogs/$f" > "<DEST>/$f" ;;
       *)    ssh <alias> "cat /www/wwwlogs/$f" | gzip -6 > "<DEST>/$f.gz" ;;
     esac
   done < "<W>/list.txt"
   ```

3. Nếu kỳ cần cả hôm nay, tải thêm file đang ghi `<vhost>_ols.access_log`.
4. Lưu `<DEST>` ngoài thư mục đồng bộ. Nếu `<DEST>` nằm trong repo có git, thêm đường dẫn vào `.gitignore` trước khi chép.
5. Nếu server giữ log ngắn hơn kỳ cần phân tích, kéo log định kỳ. Cách đặt job thuộc luật workstream của dự án.

Bẫy: không đưa output SSH thẳng vào vòng lặp có glob. Cảnh báo của SSH có thể bị bung thành tên file trên máy. Ghi danh sách ra file, đọc từng dòng và lọc tên như bước 1–2.

## 3. Định dạng dòng

`logFormat` của gtvseo.com sau ngày 21/10/2026:

```text
'%{X-Forwarded-For}i %h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i" %D "%{X-LiteSpeed-Cache}o"'
```

- OLS ghi cả dấu nháy đơn của `logFormat` vào log. Mỗi dòng bắt đầu và kết thúc bằng `'`.
- Trường đầu là `X-Forwarded-For`. Trường này là `-` khi request không qua proxy. IP client `%h` nằm ở trường thứ hai.
- Vhost khác trên cùng server có thể dùng định dạng combined, không có trường đầu. Khi đó mã trạng thái nằm ở `$9`, không ở `$10`. Các script của skill dò cả hai dạng. Không đếm bằng awk gán cứng cột.
- `%D` là thời gian phản hồi, đơn vị micro giây. Log không có `%D` thì khối 6 chỉ có dung lượng.
- `%{X-LiteSpeed-Cache}o` là trạng thái cache của trang (hit hoặc miss).
- Log không ghi scheme và host. Hit vào `http://` và `www.` gộp với bản chuẩn. Khi chỉ có log, ghi redirect vào `/` từ hai nguồn này là CANNOT-VERIFY.
- Nếu site chạy sau CDN hoặc proxy, kiểm `%h` là IP client hay IP của proxy. Nếu `%h` là IP proxy, mọi IP Googlebot sẽ ra `fake`. Dừng và hỏi cấu hình trước khi xác minh bot.

## 4. Đề xuất sửa cấu hình log và uploads

Hai việc dưới sửa cấu hình sống và cần restart OLS. Skill chỉ đề xuất trong action list. Người có quyền duyệt từng lần. Dev thử trên staging trước, có backup và rollback.

1. Thêm `%D` vào cuối `logFormat` để đo khối 6.
2. Trả 404 tĩnh cho file thiếu trong `/wp-content/uploads/`. OLS chỉ đọc rewrite trong `.htaccess`. Đặt rule trước khối WordPress:

   ```apache
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteRule ^wp-content/uploads/ - [L]
   ```

   Request dừng ở rule này, không vào `index.php`, nên server trả trang 404 mặc định.

Kiểm sau khi sửa:

- Gọi 1 file không tồn tại trong uploads. Response phải dưới 2 KB và mã là 404.
- Chạy `log_checks.py uploads` trên log sau mốc sửa. Trung vị byte của file thiếu phải dưới `--max-bytes`.
- Chạy `log_health.py` trên log mới. Script phải đọc được dòng sau khi `logFormat` đổi.

Ví dụ gtvseo.com 21/10/2026: sau rule trên và graceful restart, file thiếu trong uploads trả 404 tĩnh 1.249 byte trong 16 ms. Trước đó response là 132 KB trong 1,1 giây.
