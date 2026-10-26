# Bảng token màu: mẫu và luật điền

Dùng ở Bước 1b của `wp-theme-build`. Bảng nối màu trong brand guideline với token của theme, nơi dùng và tỉ lệ tương phản. Script `scripts/contrast.py` đọc bảng này.

## 1. Cột

| Cột | Điền gì |
|---|---|
| Token brand | Mã màu gốc trong guideline. Màu pha từ guideline: ghi các màu gốc và chữ "(pha)". Màu không có gốc: ghi "-" và ghi lý do ở cột Nơi dùng |
| Token theme | Biến CSS của theme, ví dụ `--x-link` |
| Nơi dùng | Thành phần dùng màu: link, nút, nhãn, nền khối |
| Chữ | Màu chữ. Chữ gradient: ghi mọi điểm dừng |
| Nền | Màu nền thật dưới chữ. Nền gradient: ghi mọi điểm dừng, cách nhau bằng dấu phẩy, dấu cách hoặc "→" |
| Cỡ | `text`: ngưỡng 4.5. `large` (từ 24px, hoặc từ 18,66px đậm): ngưỡng 3.0. `ui` (viền, icon, đồ hoạ): ngưỡng 3.0 |
| Ngoại lệ | Lý do giữ một dòng trượt và người duyệt. Để trống khi dòng đạt |
| Tương phản | Script ghi cột này khi chạy `--write`. Không điền tay |

Script nhận tên cột không dấu, ví dụ "noi dung". Dòng màu chỉ trang trí (không mang chữ): để trống cột Chữ và Nền. Script bỏ qua dòng đó.

## 2. Luật

- Đọc guideline trước khi lập bảng. Không đưa màu ngoài bảng vào CSS.
- Màu có alpha: trộn lên nền thật, rồi ghi mã 6 ký tự. Script báo lỗi khi gặp mã có alpha.
- Đo trên nền thật dưới chữ. Không đo mặc định trên nền trắng. Khối tối, ảnh phủ màu và chip: mỗi nền một dòng.
- Màu sáng như cyan, vàng trên nền sáng thường trượt mức `text`. Chỉ dùng các màu này cho đường kẻ, thanh, hoặc trên nền tối.
- Giữ dòng trượt khi cột Ngoại lệ có lý do và người duyệt đồng ý. Script vẫn in dòng đó, nhưng không trả exit 1.
- Truyền guideline bằng `--brand <file>` hoặc `--brand "#hex,#hex"`. Script báo mọi mã ở cột Token brand không có trong guideline.

## 3. Ví dụ (site TAG, 17/10/2026)

| Token brand | Token theme | Nơi dùng | Chữ | Nền | Cỡ | Ngoại lệ | Tương phản |
|---|---|---|---|---|---|---|---|
| #850DBA #00CCFF (pha) | --tg-pu3 | link, nhãn | #4F46C8 | #FFFFFF | text | | 6.90:1 đạt |
| #850DBA | --tg-gt | chữ gradient H1, H2 | #850DBA #4F46C8 #1D72C9 | #FFFFFF | large | | 4.88:1 đạt |
| #7A7FD1 | --tg-pu | chấm đầu dòng, viền focus | #7A7FD1 | #FFFFFF | ui | | 3.63:1 đạt |
| - | --tg-cta | nút mua (màu CTA giữ theo quyết định của người duyệt) | #FFFFFF | #F0123A → #FF3D1F → #FF7A00 | text | điểm treo cũ, người duyệt giữ màu CTA | 2.61:1 ngoại lệ (điểm treo cũ, người duyệt giữ màu CTA) |
| #2F3E9E | --tg-pu3 (bản 16/10) | link | #2F3E9E | #FFFFFF | text | | 9.11:1 đạt; ngoài guideline: #2F3E9E |

Dòng cuối là lỗi thật. Màu chàm đạt tương phản, nhưng nằm ngoài guideline (tím #850DBA → cyan #00CCFF). Người duyệt chỉ phát hiện bằng mắt sau khi theme đã lên staging. Cờ `--brand` bắt lỗi này trước khi viết CSS.
