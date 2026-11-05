# PHP được gọi trực tiếp từ web

Dùng khi log báo hàm WordPress chưa định nghĩa trong file chỉ dành cho include. Đây không tự chứng minh malware hoặc bot.

1. Ghép access log và error log theo domain, timestamp, path và status. Đọc log xoay vòng khi cần; không xuất IP/UA thô vào báo cáo.
2. Xác minh file còn cần: plugin active, require/include, endpoint gọi trực tiếp và multisite. Plugin tắt vẫn có thể được gọi qua web.
3. Ưu tiên rule chính thức hẹp, rồi mở rộng theo bằng chứng site. `wp-admin/includes/` không phải endpoint công khai. Trong `wp-includes/`, giữ TinyMCE PHP và nhu cầu multisite thực tế. Không chặn toàn bộ PHP plugin: ví dụ LiteSpeed cần `guest.vary.php`.
4. Kiểm regex có path-info, chữ hoa và các đường hợp lệ. Fixture Apache không thay kiểm OLS hoặc Nginx.
5. Backup, staging theo stack thật, diễn tập, duyệt restart nếu cần. Sau nạp, kiểm origin và edge: file bị chặn phải 403; editor/admin, Ajax, REST, CSS/JS và plugin endpoint giữ chức năng. Không gửi form thật để kiểm.
6. File plugin thừa đã xác minh: backup hash/owner/mode, quarantine ngoài webroot, kiểm URL cũ không truy cập được. Kiểm lại active status ngay trước di chuyển. Không xoá.

[WordPress hardening](https://developer.wordpress.org/advanced-administration/security/hardening/) có mẫu chặn include và lưu ý multisite. Mẫu rộng hơn phải có allowlist theo site; không chép nguyên rule của site mẫu cho mọi instance.

Kết luận chỉ trong phạm vi đã kiểm. GET trực tiếp gây Fatal không đủ xác định danh tính bot; 0 tham chiếu một hằng trong PHP hiện tại không bảo đảm mọi hệ thống đều không dùng.
