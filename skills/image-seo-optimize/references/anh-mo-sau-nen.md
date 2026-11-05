# Ảnh mờ sau đợt tối ưu: chẩn đoán và sửa

Đọc file này khi người duyệt báo ảnh trên site bị mờ, vỡ hoặc nhoè sau đợt nén hay tối ưu PageSpeed. Nguồn: một site WordPress agency mẫu, 05/11/2026. Đợt sửa thay 36 file ảnh trên 3 trang chính, đo 331 vị trí ảnh trước và sau, có kiểm độc lập bằng ảnh chụp DPR thật.

## 1. Ba nguyên nhân thường gặp

| Nguyên nhân | Dấu hiệu | Cách đo |
|---|---|---|
| Ảnh gốc bị ghi đè khi nén | File gốc có `mtime` mới hơn các cỡ con. PNG ở mode `P` (256 màu). JPG nhỏ hơn nhiều so với bản backup | So `ls -la --time-style=full-iso` của file gốc và cỡ con; mở bằng Pillow xem `mode` |
| Nén chồng | File `.webp` sinh từ JPG/PNG đã nén, hoặc ảnh LCP riêng sinh từ bản đã hỏng | SSIM của file đang phục vụ so với bản gốc trước tối ưu (backup), không so với file đang phục vụ |
| Thiếu pixel cho màn hình nét | Pixel thật nhỏ hơn cỡ hiển thị × DPR. iPhone DPR 3, MacBook DPR 2 | Đo trong Chrome ở DPR thật, xem mục 2 |

- Ca thật: đợt nén cũ ép PNG ảnh đội ngũ ở hero mobile từ 482 KB truecolor về 147 KB mode `P`. Bản WebP và ảnh LCP mobile 570 px sinh từ bản đã ép. Trên iPhone, ảnh 358 px CSS cần khoảng 1.074 px.
- Một mu-plugin đặt `sizes="(max-width: 768px) 1px"` để điện thoại luôn tải bản 570 px. Cách này làm mọi điện thoại mất bản lớn. Xem `wp-pagespeed` lớp 3.

## 2. Đo pixel đúng

- `img.naturalWidth` của ảnh có `srcset` dạng `w` là cỡ đã chia density, không phải pixel thật. Ca thật: file 1536 px báo `naturalWidth` 390. Lấy pixel thật bằng `new Image()` với `img.currentSrc`, rồi đọc `naturalWidth` của ảnh mới.
- Ảnh nền CSS: lấy URL từ `getComputedStyle(el).backgroundImage`. Tính theo `background-size` (`cover` lấy tỉ lệ lớn hơn).
- Chỉ số "đủ nét" = pixel thật ÷ (cỡ CSS × DPR). Dưới 0,7 ở ảnh lớn trên màn đầu thì nhìn thấy mờ.
- Chụp ảnh trước/sau bằng Chrome thật ở DPR 3 (390 px) và DPR 2 (1440 px). Chặn host tracking khi chụp.

## 3. Sửa

1. Tìm bản gốc trước tối ưu: thư mục backup của đợt nén, `_quarantine`, bản trong uploads có tên gốc. Chạy `scripts/tim_anh_goc.py --dich <ảnh mờ> --ung-vien <thư mục ứng viên>`.
   - `ti_le` ≥ 1,3: có nguồn lớn hơn đáng dùng.
   - `xoay` ≈ 0 và `doi_xung` ≈ 0: ảnh đích là bản thu thẳng của ứng viên. Thu nhỏ trực tiếp từ ứng viên.
   - Ảnh thiết kế có lớp màu, bo góc, mờ dần: dựng lại bằng `scripts/dung_lai_anh.py --nho <ảnh đang phục vụ> --nguon <ảnh gốc lớn> --out <mới.png> --diff-png <diff.png>`.
2. Mã hoá WebP từ bản gốc: `cwebp -m 6 -q 85 -sharp_yuv`. Ảnh có alpha thêm `-alpha_q 100 -exact`.
   - Ca thật: q80, q85 và q92 nhìn như nhau ở cỡ iPhone; q96 nặng gấp đôi q85. Đợt đầu chọn ngưỡng SSIM 0,993 nên lên q96, tổng byte gấp 2,2 lần; hạ về q85 còn +13%.
   - Ảnh không bị nén chồng: chỉ nén lại khi SSIM so với gốc tăng ít nhất 0,005.
3. Giữ URL nếu CSS cố định cỡ hiển thị (`object-fit`, `background-size: cover`, width/height trong CSS). Đổi URL kéo theo sửa HTML, CSS và map CSS gọn.
4. Không ghi đè file gốc trong `uploads/` bằng bản nén. Khôi phục bản gốc nếu đợt trước đã ghi đè.
5. Backup theo phiên bản, kiểm SHA trước khi ghi, ghi nguyên tử (`install` ra file tạm rồi `mv`), giữ owner web server.
6. Purge CDN đúng URL ảnh, gồm cả URL `.jpg`/`.png` gốc khi `.htaccess` trả WebP theo `Accept`.

## 4. Kiểm sau sửa

- Đo lại cỡ hiển thị mọi ảnh ở 2 thiết bị: số ảnh đổi cỡ phải bằng 0.
- HTTP origin trả đúng byte mới (so SHA). CDN trả bản mới.
- Xem bằng mắt ảnh dựng lại ở 100%, nhất là vùng mờ dần sang trắng. Ca hỏng: banner desktop dựng lại có lớp mờ trắng sau đầu người, bản gốc không có. Chỉ số sai khác màu không bắt được ca này (p99 8,9, thấp hơn ảnh tốt 10,8). Đã bỏ bản dựng, chỉ khôi phục bản gốc.
- Ghi byte tăng của ảnh LCP. Đo PSI mobile sau đợt sửa.

## 5. Jev

- Rubric `anh-net` (bộ `ai-assist`): câu `blurry`, `compression`, điểm `sharpness`.
- Hiệu chuẩn 7 ảnh đã biết nhãn: Jev xếp đúng chiều nhưng hai nhóm chồng nhau (ảnh hỏng 0,66, ảnh nét 0,67). Câu `compression` gắn cờ 113/123 ảnh.
- Chỉ dùng Jev so trước/sau trên cùng một ảnh. Ca thật: 3 hero mobile giảm `blurry` 0,15–0,20. Không dùng làm cổng tuyệt đối.
- EmbeddingGemma không đo độ nét điểm ảnh. Không dùng cho việc này.
