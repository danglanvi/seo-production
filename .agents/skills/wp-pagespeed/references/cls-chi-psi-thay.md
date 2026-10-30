# CLS chỉ PSI thấy: dựng lại môi trường PSI trước khi sửa

Đọc file này khi PSI báo CLS từ 0,1 (hoặc CLS lệch giữa các lượt), mà `perf_probe.mjs` và `cls_trace.mjs` trên máy không tái hiện. Script nằm ở `$WPS/scripts/`.

Lỗi đã gặp ở site agency mẫu 19/10/2026, trang blog: truy CLS gần 2 giờ, nhiều lượt lab trên máy không tái hiện. Bản sửa bằng cách bổ sung critical CSS lên production dù A/B lab không khác (0,009 cả hai bản). PSI sau đó vẫn báo CLS 0,334.

## Thứ tự bắt buộc

Làm đúng thứ tự. Không bỏ bước 1–2 để sửa thẳng.

1. Đọc field trước. Mở `loadingExperience` (URL) và `originLoadingExperience` (origin) trong JSON PSI. Nếu CLS p75 của field dưới 0,1, áp luật ở SKILL.md Bước 3 mục 0.
2. Đổ dữ liệu CLS của PSI cho 2–3 lượt, gồm một lượt CLS cao và một lượt CLS thấp:

   ```bash
   python3 -I "$WPS/scripts/psi_cls_dump.py" <ev>/psi-base/<tên>_mobile_run1.json --out <ev>/cls-<tên>-r1
   ```

   - Script in `benchmarkIndex`, CLS lab, CLS field, rồi từng dịch chuyển: selector, điểm, `boundingRect`, nguyên nhân PSI gán.
   - Script ghi `final-screenshot.png`, từng khung filmstrip và `filmstrip-all.png`. Xem ảnh bằng công cụ đọc ảnh.
   - So khung trước và sau dịch chuyển. Xác định phần tử dịch và thứ gây dịch: font, ảnh, khối JS chèn, class đổi trạng thái.
   - Tính ngược khoảng dịch trước khi đoán nguyên nhân. Điểm một lần dịch xấp xỉ bằng tỉ lệ vùng ảnh hưởng nhân tỉ lệ khoảng dịch. Lấy `boundingRect` cuối và chiều cao viewport (mobile 823 px), giải ra khoảng dịch. So số đó với chiều cao các phần tử lân cận.
     - Site agency mẫu 28/10: khối chữ hero có top 508 px và điểm 0,323. Khoảng dịch tính ra khoảng 330 px, gần bằng chiều cao ảnh banner phía trên (khoảng 324 px).
   - So filmstrip với một lượt CLS 0 của cùng trang trước khi kết luận do font. Site agency mẫu 28/10: frame 750 ms có FOUT ở cả lượt CLS 0,323 lẫn lượt CLS 0 của ngày trước, nên font không phải nguyên nhân.
3. Dựng lại môi trường PSI trên máy bằng Lighthouse local:

   ```bash
   node "$WPS/scripts/lh_local.mjs" --url <URL> --dev mobile --runs 3 --block-vary --expect '<chuỗi trong title>' --out <ev>/lh-<tên>
   python3 -I "$WPS/scripts/psi_cls_dump.py" <ev>/lh-<tên>/lh_mobile_run1.json --out <ev>/lh-<tên>/r1
   ```

   - `--block-vary` chặn `guest.vary.php`. LiteSpeed Guest Mode reload trang một lần cho trình duyệt thường. PSI không reload, nên lab không chặn sẽ đo một trang khác PSI.
   - Máy PSI chậm hơn máy trên bàn. Thêm `--delay 200` hoặc `--obs-cpu 1.5` khi lab chưa ra cùng phần tử.
   - Script dùng module Lighthouse trong cache npx. Thiếu module thì script thoát mã 3. Đặt `--lh-modules` hoặc biến `LH_MODULES`.
4. Chỉ viết bản sửa khi lab tái hiện được cùng phần tử dịch với cùng cỡ CLS. Thử bản sửa trong lab trước: chèn CSS qua CDP `Fetch` (`checklist-theo-lop.md` lớp 6), hoặc A/B bằng bản HTML tĩnh (`do-dac.md` mục 3).
5. Đo bản sửa trên PSI bằng `psi_ab.py`, quyết định bằng `psi_decide.py`. Ngưỡng CLS mặc định 0,02.

## Luật

- Lab chưa tái hiện được nguyên nhân thì chưa deploy bản sửa CLS. Ghi giả thuyết và bằng chứng còn thiếu vào báo cáo.
- Bản sửa CLS cấp site (font, CSS dùng chung, critical CSS) phải thử trên ít nhất 7 bài khác bố cục trước khi giữ. Một bài đạt chưa đủ, vì chữ đổi dòng tuỳ độ dài từng đoạn.
- Nguyên nhân "Phông chữ web" của PSI chỉ là phỏng đoán theo thời điểm font tải (`do-dac.md` mục 2). Kiểm bằng ảnh filmstrip và `boundingRect`.
- CLS dưới 0,1 do chữ đổi dòng khi font thật thay font dự phòng: ghi là giới hạn đã đo (`checklist-theo-lop.md` lớp 4).

## `size-adjust` có bậc theo pixel

Chrome trên Linux của PSI làm tròn bề rộng ký tự theo pixel. Hệ quả:

- Số `size-adjust` tính bằng fontTools (`fallback_faces.py`) lệch 1–3% so với số tối ưu trên PSI. Site agency mẫu 22/10 đo được độ lệch này ở 2 họ font (Be Vietnam Pro, Roboto).
- Nhiều giá trị gần nhau cho cùng một kết quả. Site agency mẫu 22/10, một bài blog desktop: `size-adjust` 103%, 104% và 105,07% đều để đoạn thứ 4 có 3 dòng khi chữ hiện bằng font dự phòng. Chỉ 100–102% làm đoạn này hết lệch, nhưng cùng giá trị đó làm mobile lệch thêm nhiều đoạn (4–10 đoạn thành 32–54 đoạn).
- Một số `size-adjust` cho mọi bề rộng màn hình có thể không đủ. Site agency mẫu 22/10: tiêu đề hero mobile 34 px đổi từ 3 sang 4 dòng khi font về. Tách hai bộ số bằng `@media (min-width:768px)`.
- Không có face dự phòng nào khớp cả Mac lẫn máy PSI. Tên `local('Arial')` khớp ở cả hai hệ (máy PSI dùng Liberation Sans), nên không khai được face riêng cho máy PSI. Chỉnh theo máy PSI thì Windows, Mac, iOS xuống dòng khác khi font về.
  - Site agency mẫu 27/10/2026, đo trên máy PSI: web font thường hẹp hơn face dự phòng 4,1%, web font đậm rộng hơn 5,6%.
  - Hiệu chỉnh trên Chrome Mac (đo khối chữ mẫu trong `main` bằng font thật, đổi face sang Arial qua CSSOM, quét `size-adjust`) cho cửa sổ đạt rất hẹp. Ví dụ ở site mẫu: Inter thường đạt ở 104,75–105,0%. Đây là số của một cặp font trên một site, không dùng làm luật.
  - Bản hiệu chỉnh Mac đạt 57/57 khối cùng số dòng trên Mac. A/B PSI production 8 lượt mỗi nhánh vẫn cho CLS trang chủ 0 → 0,285 và bài pillar 0 → 0,118 khi nạp font sau FCP.
- Vì vậy mọi thay đổi font (cách nạp, preload, face dự phòng, `size-adjust`) phải A/B trên PSI production bằng bản HTML tĩnh trước khi giữ. Lab Chrome Mac và `lh_local.mjs` không thấy CLS do làm tròn bề rộng chữ của Linux.

Cách hiệu chuẩn:

1. Dựng biến thể bản HTML tĩnh, mỗi biến thể một giá trị `size-adjust` (ví dụ 100%, 102%, 104%, 106%).
2. A/B trên PSI bằng `psi_ab.py` cho cả mobile và desktop.
3. So chiều cao từng khối chữ giữa trạng thái chỉ có face dự phòng và trạng thái font web đã về. Chặn file font trong `lh_local.mjs --block '*.woff2'` để chụp trạng thái chỉ có face dự phòng.
4. Chọn giá trị làm số khối lệch thấp nhất ở cả hai thiết bị. Không chọn theo một trang.

Field đã đạt mà lab còn lệch dưới 0,1 thì đề xuất giữ nguyên. Đổi `size-adjust` có thể làm lab tốt hơn nhưng field xấu đi.
