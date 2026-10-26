# FCP mobile dồn một mốc và LiteSpeed Guest Mode

Đọc file này khi FCP observed của PSI mobile dồn quanh một mốc ở nhiều template, và site bật LiteSpeed Guest Mode. Kiểm cả bẫy script nạp font ở `checklist-theo-lop.md` lớp 4, vì bẫy đó cho cùng dấu hiệu.

## Dấu hiệu

- FCP observed mobile dừng quanh một mốc ở nhiều lượt và nhiều template. Site agency mẫu 19/10/2026: 2.342–2.460 ms ở trang chủ và trang dịch vụ.
- Trong `network-requests`, file CSS gộp tải xong sớm (0,4–0,7 s), nhưng khung hình đầu vẽ muộn.
- Trang không có critical CSS. File CSS gộp lớn chặn hiển thị trong `<head>` (site agency mẫu: khoảng 1,4 MB).
- Desktop không bị, vì CPU không bị giới hạn.

## Chẩn đoán

1. Ghi trace Chrome ở chế độ mô phỏng mobile (CPU x4, 4G chậm). Bật category `viz`, `cc` và `devtools.timeline` qua CDP `Tracing.start`.
2. Đếm event `ThrottleUndrawnFrames` và số lần Chrome từ chối `BeginFrame`. Đo khoảng `requestAnimationFrame` ngừng chạy.
3. Kết luận cổng FCP khi Chrome hoãn commit khung đầu tới lúc parse xong CSS. Site agency mẫu: `ThrottleUndrawnFrames` 402–2.304 ms, 98 lần từ chối `BeginFrame`, rAF ngừng 1.405–2.406 ms.

Những thứ đã thử và không chữa được cổng này:

- Bật critical CSS hoặc nạp CSS gộp bằng `media="print"`. Hai cách này chuyển cổng sang TBT: parse 1,4 MB CSS sau FCP thành long task, TBT lab 1,8–2,6 s.
- Gỡ video ẩn. Video ẩn có `preload="metadata"` vẫn tải nhiều phản hồi 206 lớn, nhưng gỡ video không đổi điểm. Đặt `preload="none"` để bớt byte, không coi đó là bản sửa FCP.

## Phương án đã chạy (cần duyệt riêng)

- Filter `litespeed_buffer_after` trong mu-plugin hiệu năng của site. Chỉ áp cho UA mobile, chỉ ở template đã chọn, chỉ khi trang chưa có critical CSS.
- Filter chuyển thẻ CSS gộp và các `<style>` sau nó xuống ngay sau `<body>`. Sau khối đó, filter thêm một `<script> </script>` rỗng để parser chờ CSS, nên khách không thấy nội dung chưa có CSS.
- Giữ nguyên trang ở các ca sau:
  - Sau thẻ CSS đầu tiên có script thường (bản HTML ngoài Guest Mode).
  - Regex trả NULL hoặc lỗi.
  - `<head>` có `<noscript` hoặc `<!--`.
- Bỏ qua chữ `<style` nằm trong nội dung `<script>` (ví dụ JSON-LD).

Đánh đổi phải trình chủ site: khi mở trang từ trang khác trên Chrome, khách mới thấy màn trắng từ lúc commit tới khi CSS về. Lab đo 2,1–2,4 s ở CPU x4 và 4G chậm.

Kiểm trước khi giữ:

1. So bố cục 390 px trước và sau bằng `shot.mjs`. Chặn `guest.vary.php` như PSI.
2. Đo PSI 3 lượt cho mọi template đã áp. Rút template nào có CLS tăng. Site agency mẫu 20/10: một trong 3 trang có CLS 0 → 0,035 nên đã rút khỏi danh sách.
3. Ghi lệnh rollback về `v0` trước khi ghi production.

Staging thường không bật Guest Mode, nên không đo được cổng này trên staging. A/B trên production bằng bản HTML tĩnh (`do-dac.md` mục 3).

## Loại trừ JS của Guest Mode

- Guest Mode dùng danh sách loại trừ JS riêng: option `optm-gm_js_exc` (filter `litespeed_optm_gm_js_exc`).
- Danh sách Delay JS thường (`optm-js_defer_exc`) không áp cho Guest Mode. Script nằm sai danh sách vẫn bị trễ ở lượt xem đầu, kể cả loader GTM hoãn.
- Kiểm cấu hình đã xuất (chỉ đọc):

  ```bash
  for k in guest optm-js_defer optm-js_defer_exc optm-gm_js_exc; do printf '%s\t' "$k"; <lệnh wp> option get "litespeed.conf.$k" --format=json; done > <ev>/ls-conf.tsv
  python3 -I "$WPS/scripts/ls_exclusions_check.py" --conf <ev>/ls-conf.tsv --script gtm-delay-loader
  ```

- Dòng cuối `LS_EXCL ok` là đạt. `LS_EXCL fail` kèm tên script còn thiếu ở danh sách đang có hiệu lực.
