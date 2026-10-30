# Site không có staging: theme xem trước trên production

Đọc khi site không có staging, hoặc staging không có LiteSpeed nên không kiểm được CSS và JS gộp. Nhánh này thay Bước 1–3 của `SKILL.md`. Bước 4–6 giữ nguyên ý: gộp 3 phía, backup, rollback, quét lộ.

Nguồn: site bán lẻ mẫu (WooCommerce, theme riêng, shared hosting LiteSpeed, không có staging), 29–30/10/2026. Một lô 40 file theme chạy trên theme xem trước 16/16 URL đạt, rồi deploy lên theme sống. Mobile trung bình 16 URL tăng từ 56,4 lên 90,4.

## 1. Cách hoạt động

- Chép theme sống thành `<theme>-v<N>` cạnh theme sống, rồi đưa lô sửa vào bản chép.
- Mu-plugin tạm (mẫu `templates/theme-preview.php.tpl`) đổi theme sang bản chép khi request có `?thp=<mã>` hoặc cookie `thp` đúng mã. Không có mã thì mu-plugin không làm gì.
- Trang xem trước vẫn qua bộ tối ưu của LiteSpeed (CSS, JS gộp) nhưng không vào cache trang. Khách thường vẫn nhận theme sống từ cache.

## 2. Dựng

1. Lấy khoá mu-plugin của site. Ghi file phối hợp nếu có phiên khác chạy trên site.
2. So sha256 của từng file trong lô với bản sống. File sống lệch bản gốc của lô thì gộp 3 phía (bản gốc → sống → lô) trên máy bằng git trước khi chép.
3. Chép theme: `cp -a <theme> <theme>-v<N>` để giữ mtime. Xoá `error_log` trong bản chép. `diff -rq` chỉ được lệch `error_log`.
4. Đưa file lô vào bản chép bằng `rsync --files-from` từ nhánh git của lô. Không chép file SCSS. Kiểm sha256 trên server khớp từng file.
5. Theme có biên dịch SCSS (WP-SCSS): `touch` file CSS của lô để CSS mới hơn mọi SCSS. Nếu không, plugin biên dịch lại và đè CSS của lô.
6. `php -l` từng file PHP trên PHP của server.
7. Giữ nguyên dòng `Version` trong `style.css`. Theme có hook purge khi đổi version sẽ Purge All. Nguồn lỗi: site bán lẻ mẫu 29/10/2026, hàm purge sau deploy theme đọc version.
8. Sinh mu-plugin trên máy:

   ```bash
   python3 -I skills/wp-staging-deploy/scripts/theme_preview_fill.py --base <theme> --preview <theme>-v<N> \
     --code-file <thư mục đợt>/.thp-code --out <thư mục đợt>/theme-preview.php
   ```

   Script ghi mã 32 ký tự vào file 0600 và không in mã. Thêm `.thp-code` vào `.gitignore` của đợt.
9. Chép `theme-preview.php` vào `mu-plugins/`, `php -l` trên server, ghi sha256.
10. Tắt UCSS, CCSS của QUIC.cloud nếu đang bật. Bật thì URL có mã bị gửi ra dịch vụ ngoài.

## 3. Kiểm

- Gắn `?thp=<mã>` vào mọi URL có cache trang. LiteSpeed trả bản cache trước khi PHP chạy, nên cookie chỉ có tác dụng ở trang không cache và ở ajax (giỏ, checkout, `?wc-ajax=`, admin-ajax, REST).
- Xem bằng phiên khách. Site bật "chỉ tối ưu cho khách" (`optm-guest_only=1`) thì admin nhận HTML chưa gộp. Không xem bằng Customizer: Customizer làm mất `theme_mods`.
- Kiểm có mã, mọi URL của bộ đo: mã 200, HTML dùng đường dẫn theme `-v<N>`, CSS gộp chứa rule mới, 2 lượt liền đều không cache.
- Kiểm không mã, cùng bộ URL: cache hit như trước, 0 chuỗi `-v<N>` trong HTML, 0 header `Set-Cookie: thp`.
- Chạy bộ kiểm không cần PSI của lô (`wp-pagespeed`, `luot-lon.md` mục 5) trên URL có mã. Đo PSI nếu cần (`psi_ab.py` hoặc URL có mã), vì trang xem trước đã qua tối ưu thật.
- Lưu HTML để làm bằng chứng thì thay mã bằng `<THP>` trước khi ghi file.

## 4. Deploy và dọn

1. Deploy lô lên theme sống theo tầng (`wp-pagespeed`, `luot-lon.md` mục 6). File sống đổi sau lúc dựng thì gộp 3 phía, không chép đè.
2. Purge theo URL, lô tối đa 12 path, làm nóng (mục "Đổi phần dùng chung toàn site" của `SKILL.md`).
3. Dọn ngay sau deploy:
   - Đổi `mu-plugins/theme-preview.php` sang `.off`.
   - Chuyển `themes/<theme>-v<N>` vào quarantine ngoài docroot. Theo luật backup: kéo bản sao về máy trước.
   - Xoá file mã `.thp-code` trên máy.

## 5. Bẫy đã gặp

| Bản mu-plugin | Cách chặn cache | Kết quả | Bài học |
|---|---|---|---|
| 1.0 | `DONOTCACHEPAGE` ở `init` | Không cache, nhưng LiteSpeed bỏ tối ưu. HTML lớn hơn 50%, 33 thẻ `<link>` CSS lẻ | Trang không cacheable thì không đo được trang thật |
| 1.1 | `litespeed_control_set_nocache` ở `litespeed_buffer_finalize` 9999 | Có tối ưu, nhưng trang vào cache 14 ngày | LiteSpeed gửi header cache ở `shutdown` 0, trước bước tối ưu |
| 1.2 | Thêm `set_nocache_hard` | Vẫn cache ở 2 URL đầu | Opcache (`revalidate_freq=2`) còn giữ bản cũ của mu-plugin |
| 1.3 (mẫu) | Giữ cờ cacheable, ghi đè header `no-cache` ở `shutdown` 0 (đăng ký sau LiteSpeed) và ở finalize 9999. Ajax, `wc-ajax`, REST đặt no-cache ngay | Có tối ưu, không cache | Dùng bản này |

- Đổi mã sau mỗi lần sửa mu-plugin. Bản cache của mã cũ hết hạn tự nhiên. Không purge URL thật để xoá chúng.
- LiteSpeed sinh thêm file gộp trong `wp-content/litespeed/` cho bản xem trước (site mẫu: 75 file CSS). Cache trang thật không đổi.
- Thư mục theme `-v<N>` truy cập công khai qua URL tĩnh. Không đặt secret, file `.env` hay bản dump trong đó.
- Ảnh có đường dẫn tuyệt đối tới thư mục theme có thể trả 404 trên bản xem trước (site mẫu: 2 logo cổng thanh toán ở checkout). Lỗi này không xảy ra sau deploy vào theme sống. Ghi vào báo cáo kiểm, không tính là lỗi của lô.
