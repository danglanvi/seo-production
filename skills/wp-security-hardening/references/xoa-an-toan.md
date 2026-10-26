# Xoá an toàn: site phụ, DB, user MySQL, user hệ thống, dịch vụ

Đọc file này trước mọi thao tác xoá trên server. Xoá luôn cần người duyệt từng lần. Đây là checklist, không có script, vì mỗi lần xoá khác nhau. Nguồn: đợt xoá 3 site phụ ngày 16/10/2026. Sau đợt đó, ảnh trang giới thiệu của site chính hỏng vì theme lấy ảnh dự phòng từ một site phụ đã xoá. Một kết luận "DB thừa" sai suýt làm xoá DB đang dùng.

Bẫy riêng của panel (`DeleteSite`, `files.DeleteDir`, `userdel`, `RemoveIPC`) ở `references/checklist-hardening.md` mục 7.

## 1. Trước khi hỏi duyệt (chỉ đọc)

- Liệt kê site, domain từ cấu hình panel và vhost. Đo `du -sh` từng thư mục.
- Với từng domain: `dig A` và `dig NS`, mã HTTP bằng `curl`, ngày cuối có request trong access log.
- Grep tên site trong hồ sơ khách `00-client-context/`.
- Grep domain của site phụ trong theme, postmeta, options của mọi site còn giữ. Có kết quả thì sửa các chỗ đó trước khi xoá.
- Map `DB_NAME` và `DB_USER` với `wp-config.php` của mọi vhost, gồm staging. Chỉ gọi DB hoặc user MySQL là "thừa" khi không vhost nào dùng.
- Home của user hệ thống có thể chứa token, ví dụ token OAuth. Liệt kê file trong home, báo chủ token để thu hồi.

Lập bảng chờ duyệt. Mỗi dòng gồm: mục, bằng chứng không còn dùng, dung lượng, lệnh làm, lệnh rollback. Người duyệt chọn từng dòng.

## 2. Bốn điều kiện trước mỗi lệnh DROP DATABASE

1. Tên DB không có trong `wp-config.php`, `.env`, crontab, vhost và cấu hình panel của mọi site.
2. Số bảng và `UPDATE_TIME` lớn nhất trong `information_schema.TABLES` không đổi từ lúc dump.
3. `SHOW PROCESSLIST` không có kết nối tới DB đó.
4. Bản dump đã qua `scripts/verify_backup.sh` và có `SHA256SUMS`.

Thiếu một điều kiện thì không DROP. Ghi lý do vào bảng chờ duyệt.

## 3. Backup trước khi xoá

- DB của khách: giữ 2 bản dump ở 2 nơi khác nhau, ví dụ thư mục backup trên server và máy làm việc. Nạp thử một bản vào DB tạm, đếm bảng, rồi xoá DB tạm.
- File site: tar vào quarantine theo `references/ung-cuu-su-co.md` mục 6. Không xoá thư mục site khi chưa có bản tar đã kiểm.
- Home của user hệ thống: nén vào quarantine trước `userdel`.
- Dịch vụ: tắt và disable trước, giữ gói cài đặt.

## 4. Lệnh rollback

- Ghi lệnh rollback cạnh mỗi lệnh xoá: nạp lại dump, tạo lại user MySQL, giải nén tar, bật lại dịch vụ.
- Lệnh rollback không chứa mật khẩu. Ghi tên khoá trong `.agent-secrets/`, ví dụ `DB_PASS_<site>`, và truyền giá trị qua stdin.

## 5. Sau khi xoá

- Mọi site còn giữ trả 200. Grep HTML các trang chính, không còn URL trỏ tới domain đã xoá.
- Ghi dung lượng đĩa trước và sau, danh sách đã xoá và nơi giữ backup vào HANDOFF của đợt.
