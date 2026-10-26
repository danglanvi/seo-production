# Nhánh TTFB và cache phía trang

Đọc file này khi CrUX TTFB p75 trên 0,8 s, hoặc khi lượt đầu của khách thật thường miss cache. Nhánh này chỉ đọc: mọi bước đo không đổi option, plugin hay file trên site. Sửa thì theo `checklist-theo-lop.md` lớp 1 và cần duyệt.

Site agency mẫu 21/10/2026 làm nhánh này trong khoảng 6 giờ. Thứ tự dưới đây làm trong khoảng 60 phút.

## 1. Kiểm nguồn field

- Gọi CrUX History API một lần trước. Nếu API trả 403, dùng `loadingExperience` và `originLoadingExperience` trong JSON PSI, rồi ghi giới hạn vào báo cáo.
- CrUX cập nhật theo cửa sổ 28 ngày. Không dùng CrUX để nghiệm thu thay đổi vừa làm.

## 2. Tỉ lệ hit theo thiết bị

1. Lấy 40 URL nhiều khách nhất từ GSC hoặc GA4. Ghi mỗi dòng một path vào `top40.txt`.
2. Chạy `lam_nong.sh` một lượt. Lượt này vừa đo trạng thái cache hiện tại, vừa làm nóng:

   ```bash
   bash "$WPS/scripts/lam_nong.sh" --host https://example.com -f <ev>/top40.txt -o <ev>/hit-truoc.tsv
   ```

3. Đọc dòng tóm tắt của từng bản cache: `đã hit sẵn <n> (<x>%)`. Bản `guest-m` (khách mới, mobile) thấp hơn hẳn `guest-d` nghĩa là làm nóng thiếu bản mobile.
4. Site agency mẫu 21/10: lượt đầu bản mobile hit 5%, bản desktop 95%. Sau khi làm nóng đủ 4 bản và Accept WebP: lượt đầu mobile vào cache ở 39/40 URL.

`lam_nong.sh` chỉ gửi GET, chạy 1 luồng, nghỉ ít nhất 0,5 s giữa các lượt và thử lại lượt lỗi một lần sau 60 s. Mã thoát 2 nghĩa là còn lượt lỗi. Chạy `-n` trước để xem kế hoạch.

## 3. Thời gian dựng trang khi miss

- Đo TTFB của URL có tham số nằm trong `cache-exc_qs` (không vào cache), 5 lượt mỗi URL. Đọc option trước, không thêm tham số mới.
- So với TTFB miss của một site đối chứng cùng server. Site agency mẫu: 0,8–1,3 s khi miss.

## 4. Phần nào làm chậm khi dựng trang

Đo trong tiến trình WP-CLI riêng. Không tắt plugin trên site để đo.

- Plugin: đo thời gian nạp WordPress với và không với `--skip-plugins=<danh sách>`, 5 lần xen kẽ mỗi bên, so trung vị. Lệnh chỉ đổi tiến trình CLI.

  ```bash
  cd /tmp && for i in 1 2 3 4 5; do /usr/bin/time -p <lệnh wp> --path=<root> eval '1;' 2>&1 | grep real; /usr/bin/time -p <lệnh wp> --path=<root> --skip-plugins=<a,b> eval '1;' 2>&1 | grep real; done
  ```

  Site agency mẫu: bỏ một plugin sao lưu bớt 45 ms. Bỏ nhóm plugin cộng sửa plugin đa ngôn ngữ bớt 91 ms.
- Truy vấn SQL: bật `SAVEQUERIES` chỉ trong tiến trình CLI riêng, bằng file nạp qua `--require` định nghĩa hằng. Không sửa `wp-config.php` trên production. Gom `$wpdb->queries` theo hàm gọi. Site agency mẫu: theme chạy 150–428 câu, 51–191 ms mỗi trang.
- Chạy mỗi lúc một tiến trình WP-CLI nặng. VPS ít RAM có thể bị kernel OOM giết tiến trình (`checklist-theo-lop.md` lớp 1).

## 5. Ngoài phạm vi skill này

- Cấu hình OPcache, log OOM của kernel, cron làm nóng định kỳ trên VPS là việc cấp server. Ghi số đo và đề xuất vào báo cáo, giao người quản trị server.
- Danh sách tham số bỏ khỏi khoá cache (`cache-drop_qs`) của từng site ghi ở `00-client-context/wp-server.md`.

## 6. Ghi vào báo cáo

| Mục | Ghi |
|---|---|
| Field | TTFB p75 URL và origin, nguồn (CrUX API hay PSI), ngày |
| Hit lượt đầu | Tỉ lệ từng bản cache, trước và sau làm nóng |
| Miss | TTFB miss trung vị, site đối chứng |
| Plugin, SQL | Mức chênh trung vị, số lần đo |
| Đề xuất | Việc, tác động ước tính, rủi ro, rollback, người duyệt |
