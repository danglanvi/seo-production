# web-profile.json — luật xuất bản của một site

Mỗi site có một file. Repo content đặt ở `00-context/web-profile.json`. Repo SEO đặt ở `00-client-context/web-profile.json`. File có thể là một object hoặc một mảng object khi repo đăng lên nhiều site. Mẫu trống: `web-profile/_mau.json`.

Script dùng file này: `md_to_html.py`, `kiem_bai.py`, `kiem_render.mjs`, `wp_publish.py` (của `wp-dang-bai`), và các script của `anh-trong-bai`. `wp_publish.py` tìm file từ thư mục hiện tại đi lên. Nếu chạy ngoài repo, truyền `--profile`.

## Trường

| Trường | Bắt buộc | Nghĩa | Script dùng |
|---|---|---|---|
| `site` | có | Mã ngắn chữ thường, trùng tiền tố key trong `.env` (`WP_<MÃ>_URL`) | `wp_publish.py` |
| `url` | có | Gốc site, không có `/` cuối | mọi script |
| `brand` | có | Tên brand ghi vào metadata ảnh | `anh_chu_thich.py` |
| `byline` | không | Tên tác giả hiển thị. mu-plugin team-accounts tự gán | ghi chú cho người đăng |
| `brand_khac` | không | Regex tên brand không được nhắc trên site này | `kiem_bai.py` (LOI), `wp_publish.py` (cảnh báo) |
| `link_ngoai` | có | `chu-thich`: link ra ngoài thành số chú thích, không hyperlink. `giu`: giữ link, thêm `rel="noopener"` | `md_to_html.py`, `kiem_bai.py` |
| `tieu_de_nguon` | không | Tiêu đề mục nguồn cuối bài. Mặc định "Nguồn tham khảo" | `md_to_html.py` |
| `chu_ky` | có | Mảng 2 dòng chữ ký thương hiệu. Rỗng thì `kiem_bai.py` cảnh báo | `md_to_html.py`, `kiem_bai.py` |
| `nhan_dich_vu` | không | Nhãn bắt buộc khi link về trang dịch vụ | người viết, Jev `link-placement` |
| `chuyen_muc.ghi_chu` | không | Luật chọn chuyên mục | người đăng |
| `luat_rieng` | có | Mảng câu luật riêng của site, có ngày chốt | `kiem_bai.py` in ra cuối báo cáo |
| `render.bai_mau` | có | URL một bài đã đăng dùng template bài viết chuẩn của theme | `kiem_render.mjs` |
| `render.khung_noi_dung` | có | Selector vùng nội dung của bài trên theme (`.entry-content`, `.tg-prose`…) | `kiem_render.mjs` |
| `media.mau` | có | Bảng màu sơ đồ: `chinh`, `phu`, `grad1`, `grad2`, `chu`, `chu_phu`, `vien`, `nen`, `nen_nhat`, `canh_bao` | `svg_dung.py`, `anh_chu_thich.py` |
| `media.font` | có | Chuỗi font-family của sơ đồ, theo font của theme | `svg_dung.py` |
| `media.font_css` | không | URL CSS font cho Chrome khi đo sơ đồ. Mặc định Google Fonts Inter + Be Vietnam Pro | `svg_kiem.mjs` |
| `media.logo` | có khi có ảnh AI | Đường dẫn logo PNG nền trong, tính từ thư mục chứa profile | `anh_chu_thich.py` |
| `media.rong_anh` | không | Bề rộng ảnh trong bài. Mặc định 1200 | `anh_chu_thich.py` |
| `media.kb_do_hoa`, `media.kb_anh_chup` | không | Trần dung lượng (KB) cho đồ hoạ và ảnh chụp. Mặc định 80 và 140 | `media_plan.py`, `anh_chu_thich.py` |
| `anh_dai_dien.engine` | có | Skill dựng ảnh đại diện của site | `anh-trong-bai/references/anh-dai-dien.md` |
| `anh_dai_dien.brand` | không | Tham số `--brand` của engine | engine |

## Cách dựng profile cho site mới

1. Chép `web-profile/_mau.json` vào thư mục context của repo.
2. Lấy màu và font từ CSS thật của theme, không lấy từ brand guideline khi màu guideline không đủ tương phản cho chữ trắng. Ghi lý do vào `media.mau_ghi_chu`.
3. Chọn `render.bai_mau` là một bài dài, có bảng, đã đăng trên template bài viết chuẩn. Mở DevTools để lấy selector vùng nội dung.
4. Hỏi người duyệt các trường luật: `link_ngoai`, `chu_ky`, `nhan_dich_vu`, `luat_rieng`. Không tự đặt chữ ký hay câu hứa của brand.
5. Chạy `kiem_render.mjs` với một bài đã đăng (`--url`) để xác nhận selector và doc-kit đúng.
