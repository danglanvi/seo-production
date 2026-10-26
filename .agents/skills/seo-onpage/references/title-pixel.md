# Đo title và meta description theo pixel (P2, P3)

File này ghi cách đo, nguồn số đo và giới hạn của `scripts/serp_pixel.py`. Gốc đường dẫn là root repo. Nạp file này ở Bước 2 khi chấm P2 và P3.

## 1. Lệnh

| Việc | Lệnh |
|---|---|
| Đo một title và meta | `python3 skills/seo-onpage/scripts/serp_pixel.py measure --title "<title>" --desc "<meta>" --out <W>/pixel.tsv` |
| Đo nhiều trang | `python3 skills/seo-onpage/scripts/serp_pixel.py measure --in <W>/pages.tsv --out <W>/pixel.tsv` (cột `url`, `title`, `description`) |
| Hiệu chuẩn lại ngưỡng từ SERP đã lưu | `python3 skills/seo-onpage/scripts/serp_pixel.py calibrate --serp <thư mục JSON Firecrawl search> --full <full.tsv> --out <W>/pixel_calibrate.json` |

- Output TSV có cột: `url`, `field`, `chars`, `px`, `limit_px`, `verdict` (`vừa` hoặc `bị cắt`), `hien_thi` (phần chữ còn hiện, cắt theo từ, thêm " ..."), `do_bang`, `nguon_nguong`.
- `do_bang` = `font`: script đo bằng Pillow và file Arial. `do_bang` = `table`: máy thiếu Pillow hoặc thiếu Arial, script đo bằng bảng `scripts/arial_widths.json`. Hai cách lệch nhau dưới 1,5 px trên title thật.
- Đặt biến `SERP_FONT` khi file Arial nằm ở chỗ khác.

## 2. Nguồn số đo

| Trường | Font và cỡ chữ | Ngưỡng | Nguồn |
|---|---|---|---|
| Title | Arial 20 px | 688 px | Đo trên SERP lưu ngày 18/10/2026 (mục 3) |
| Meta description | Arial 14 px | 920 px | Ước lượng phổ biến của các công cụ xem trước SERP. Chưa kiểm chứng trên dữ liệu (mục 4) |

- Google không công bố font, cỡ chữ hay ngưỡng cắt. Ngưỡng là đơn vị quy đổi theo Arial, không phải bề rộng cột kết quả thật.
- Mốc 580–600 px của nhiều công cụ chặt hơn số đo. Trong dữ liệu 18/10, 143/256 title hiện đủ rộng trên 580 px.
- Profile tên `desktop` vì dùng cỡ chữ desktop. Dữ liệu SERP không ghi viewport.

## 3. Kiểm chứng ngưỡng title

Dữ liệu: 284 kết quả Firecrawl search ngày 18/10/2026 của 40 truy vấn tiếng Việt, ngành dịch vụ SEO. Title hiển thị kết thúc bằng "..." là title Google đã cắt.

| Mục | Kết quả |
|---|---|
| Title Google hiện đủ | 256 |
| Title bị cắt | 28. Có title đầy đủ (GET trang, phần đầu khớp phần hiện): 17. Trang chặn, Facebook, title đã đổi: 11 |
| Tách dev và holdout | Theo hash MD5 của URL, trước khi đo |
| Ngưỡng học trên dev | 688 px. Dev 133/133 đúng |
| Holdout | 138/140 đúng (98,6%) |
| 11 title bị cắt không có bản đầy đủ | 11/11 có phần hiện ≤ 688 px |
| So với đếm ký tự | Ngưỡng 75 ký tự, holdout 137/140 |

Hai ca lệch, giữ làm ca test:

- Title 681,5 px bị cắt: "Dịch vụ GEO website là gì? Tại sao SEO lại là nền tảng của GEO phát triển?".
- Title 688,2 px hiện đủ: "GEO là gì? 9 kỹ thuật tối ưu GEO giúp tăng hiển thị trên AI [2026] - " cộng tên thương hiệu 7 ký tự của site mẫu.

Cách đọc: title dưới khoảng 680 px gần như chắc hiện đủ. Title từ 680 tới 700 px nằm ở vùng biên. Title trên 700 px bị cắt.

## 4. Giới hạn

- Meta description chưa kiểm chứng. Snippet trong SERP 18/10 gồm ngày, điểm sao, sitelink, và Google thường tự viết snippet. Snippet bị cắt rộng 912–1.632 px nên không học được ngưỡng.
- Chưa có số đo cho mobile. Khi có SERP mobile đã lưu, chạy `calibrate --size <cỡ chữ>` trên dữ liệu đó rồi thêm profile.
- Google có thể viết lại title. Ngưỡng chỉ nói title có bị cắt hay không, không nói Google giữ title đó.
- Đây là chỉ số mô phỏng. Báo cáo khách ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
