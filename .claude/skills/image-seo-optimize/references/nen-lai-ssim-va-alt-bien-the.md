# Nén lại ảnh đã đăng bằng SSIM và kiểm alt ở mọi biến thể

Đọc file này khi `$APPLY=apply` nén ảnh đã có trên site, hoặc khi sửa alt của ảnh nằm trên trang đang chạy. Nguồn: hai lượt trên một site WordPress agency mẫu, 27/10/2026 (nén 35 banner case study; sửa ảnh hero và alt của 3 trang dịch vụ). Cả hai lượt có người kiểm độc lập, md5 file khớp ở origin và CDN, 5xx bằng 0.

Script nằm ở `scripts/`. Cần Pillow và numpy. `webp_recompress.py` cần thêm `cwebp`. Test: `python3 -B scripts/tests/test_image_tools.py`.

## 1. Ngưỡng SSIM theo loại ảnh

| Loại ảnh | `--kind` | Ngưỡng SSIM luma | Ví dụ |
|---|---|---|---|
| Có chữ hoặc logo | `chu` | 0,98 | banner chứa tên khách, ảnh chụp màn hình |
| Ảnh chụp thật | `that` | 0,97 | ảnh nội thất, sản phẩm, người |

- Cách đo: trung bình 3 kênh RGB, cửa sổ đều 7x7. Đổi cách đo thì đo lại ngưỡng.
- So bản mới với file đang phục vụ, không so với nguồn gốc. Mục tiêu là bản mới không khác bản khách đang thấy.
- Chọn `chu` khi không chắc. Ảnh có chữ vỡ trước ảnh thật.
- Kiểm bằng mắt vài cặp ở 100% trước khi áp lô. Lượt 27/10 kiểm 4 cặp (banner có chữ và logo), không thấy khác biệt.

## 2. Nén lại một lô ảnh WebP

```bash
python3 scripts/webp_recompress.py --src <goc.jpg|png> --ref <dang-phuc-vu.webp> --kind chu|that --out <moi.webp> [--target-kb 30]
```

- Vòng lặp: `cwebp -m 6 -pass 10` từ nguồn gốc, q giảm từ 80 theo bước 2. Dừng khi file nhỏ hơn `--target-kb` hoặc SSIM dưới ngưỡng.
- Chỉ ghi khi bản mới nhỏ hơn file đang phục vụ ít nhất 8%. Dưới 8% thì giữ: đổi file mà lợi ít làm tốn purge CDN.
- Chưa có file WebP (đang phục vụ JPG): bản WebP mới cũng phải nhỏ hơn JPG ít nhất 8% và đạt SSIM. Ca thật: 4 ảnh chỉ nhỏ hơn 5%, không tạo.
- Giữ nguyên kích thước pixel, tên file, URL, chủ sở hữu file và quyền. Không đụng JPG, PNG gốc: `og:image` và trình duyệt không có WebP dùng chúng.
- Ca thật: 32/35 banner, 1.514 KB còn 1.205 KB (-20,4%). 3 banner giữ nguyên vì đã nhỏ.
- Backup file cũ và lệnh trả lại phải có trước khi ghi. Sau khi ghi, so md5 ở origin và ở CDN, rồi purge đúng URL ảnh đã đổi.

### Kỳ vọng đúng về PSI

- Byte giảm thật. Ca thật: banner chính của một trang case giảm 8,6 KB (41,9 xuống 33,1 KB).
- Điểm PSI và LCP đổi trong nhiễu của PSI. Ba lượt trung vị của một trang cho LCP lệch 1.265 ms vì một lượt trùng giá trị cache cũ, không do nén ảnh.
- Báo lợi ích là byte và băng thông. Không hứa điểm.
- Mục "Cải thiện việc phân phối hình ảnh" của PSI đặt mục tiêu theo công thức đo được: số điểm ảnh hiển thị chia 6 là số byte mục tiêu, và PSI báo phần file vượt mục tiêu. Hai điểm đo khớp công thức: ảnh 446x417 có mục tiêu 30.997 B, file 45.900 B báo 14,6 KiB, file 35.324 B báo 4,2 KiB. Đây là công thức rút ra bằng đo trên 40 ảnh, không phải tài liệu chính thức. Dùng để chọn `--target-kb`, rồi chạy PSI để xác nhận.
- Không tạo bản 2x từ nguồn nhỏ hơn. Nguồn rộng 642 px thì không tạo bản 892w: đó là phóng to. Máy DPR 2 dùng bản 642w. Cách đo cỡ hiển thị và viết `srcset`, `sizes` nằm ở `wp-pagespeed` `references/checklist-theo-lop.md` lớp 3.

## 3. Ảnh có kênh alpha

- Đo SSIM trên nền thật của trang, không dùng nền đen hoặc trắng. Cùng một cặp ảnh hero: 0,9737 trên nền xanh-tím thật, 0,9616 trên nền đen hoặc trắng. Cổng 0,97 cho kết quả khác nhau theo nền.
- Truyền nền bằng `ssim_luma.py --bg '#RRGGBB'`. Không có `--bg` thì script từ chối ảnh có alpha (thoát 2).
- Truyền thêm `--bg` nền đen và trắng để biết mức xấu nhất. Cổng đạt chỉ dùng nền đầu tiên.
- Kênh alpha thường chiếm phần lớn byte của WebP có viền tóc hoặc nền mờ. Hạ `alpha_q` của cwebp xuống dưới 75 gây quầng sáng quanh chủ thể và vân ở vùng mờ. Cách đã dùng: làm tròn alpha về bội số của 8, lưu alpha không mất dữ liệu, tăng q màu lên 82. Kết quả: 45.900 B còn 35.324 B.
- Xem cặp ảnh ở 2x để tìm vân. Ca thật có vân rất nhẹ ở 2x và không thấy ở cỡ thật. Ghi lệnh trả lại vào báo cáo.

## 4. Alt phải đúng ở mọi biến thể HTML

Alt của một ảnh có thể đến từ hai nguồn:

| Nguồn | Khi nào in ra |
|---|---|
| Alt của attachment | Ảnh nhúng bằng trường ảnh hoặc `wp_get_attachment_image` |
| Chuỗi cứng trong template | Nhánh mobile khi trường ảnh mobile để trống, hoặc thẻ `<img>` viết thẳng |

Quy trình:

1. Tìm mọi nơi sinh thẻ `<img>` của ảnh: `grep` tên file và tên trường ảnh trong theme. Ghi bảng "trang, thẻ desktop, thẻ mobile, nguồn alt, attachment".
2. Tìm mọi attachment trỏ cùng file. Ca thật: 4 attachment cho 2 file, md5 trùng. Sửa alt ở mọi attachment mà trang đang dùng. Attachment trùng không trang nào tham chiếu: báo trong báo cáo, không sửa.
3. Sửa chuỗi cứng trong template theo luật deploy của `wp-staging-deploy`.
4. Kiểm HTML thật ở ba biến thể, sau khi purge cache trang:

   ```bash
   python3 scripts/alt_variants.py --url <URL1> --url <URL2> --match <tên-file-ảnh> --alt "<alt đúng>" --old-alt "<alt cũ>"
   ```

   Đạt khi mọi biến thể in alt đúng từng ký tự và HTML không còn alt cũ ở chỗ nào, kể cả JSON-LD. Ca thật: 9/9 (3 trang x 3 biến thể).
5. Biến thể Googlebot chỉ là chuỗi UA, không phải IP Google. Ghi lượt kiểm vào báo cáo để người phụ trách log crawl lọc theo IP đã xác minh, không lọc theo UA.
6. Kiểm robots meta và canonical không đổi. Sửa alt không được chạm hai thẻ này.

Alt người duyệt đưa nguyên văn mà có lỗi chính tả rõ: sửa lỗi, rồi báo lại trong tin trả lời. Ca thật: "Developement" thành "Development" (27/10/2026, báo trong cùng tin).

Trang tiếng Anh chưa dùng ảnh thì chưa có alt tiếng Anh. Đề xuất alt khi trang đó dùng ảnh, không tự thêm.
