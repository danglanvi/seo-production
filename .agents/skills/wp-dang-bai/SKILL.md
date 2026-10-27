---
name: wp-dang-bai
description: "Đăng hoặc cập nhật bài lên WordPress qua REST bằng app password: file HTML format blog doc-kit giữ giao diện (bảng, tab, quiz, checklist, SVG, video), tự tải ảnh lên Media, điền SEO title, meta, keyword, chuyên mục, ảnh đại diện. Dùng khi đẩy bài từ repo lên site có web-profile."
metadata:
  version: "1.2.1"
---

# wp-dang-bai — đăng bài lên WordPress qua API

Script `scripts/wp_publish.py` (Python stdlib) đưa một file HTML lên WordPress. Site cần có mu-plugin `doc-kit` (thư mục `wp/`). Mỗi site có một mã ngắn (`--site`) và một file `web-profile.json` (schema: `wp-xuat-ban-bai/references/web-profile.md`).

Quy trình xuất bản đầy đủ (media, khối bấm, kiểm render, ảnh đại diện) nằm ở skill `wp-xuat-ban-bai`. Skill này chỉ là bước đẩy bài lên site.

## Khi nào dùng

- Đăng bài mới hoặc cập nhật bài đã đăng trên site có profile và có doc-kit.
- Bài viết theo format bài blog doc-kit (`wp-xuat-ban-bai/scripts/md_to_html.py` sinh ra), hoặc HTML thường.
- Không dùng khi: sửa title, meta, link hàng loạt trên bài cũ (dùng `wp-content-review-apply`); sửa trang dịch vụ, trang chủ (page).

## Cài đặt một lần cho mỗi người

1. Xin admin của site một app password của tài khoản đăng bài chung. Mỗi người một app password, tên `<Tên> - <máy>`.
   - Admin tạo trong wp-admin: Users → tài khoản đăng bài → Application Passwords. Hoặc agent có SSH chạy `wp user application-password create <user> "<Tên> - <máy>" --porcelain`.
2. Ghi vào file `.env` ở thư mục gốc repo (đã nằm trong `.gitignore`). `<MÃ>` là mã site viết hoa. Không dán key vào chat, file khác hay commit:

```
WP_<MÃ>_URL=https://<domain>
WP_<MÃ>_USER=<tên đăng nhập>
WP_<MÃ>_APP_PASSWORD=<chuỗi app password>
```

3. Kiểm: `python3 skills/wp-dang-bai/scripts/wp_publish.py doctor --site <mã site>`. Kết quả đúng có 2 dòng `OK … role <vai trò>` và `doc-kit trên site: có`.

Người có tài khoản riêng (SEO Leader, Người đăng bài) tạo app password trong hồ sơ của chính mình và đặt `WP_<MÃ>_USER` là tên đăng nhập đó. Tác giả hiển thị do mu-plugin team-accounts của site gán.

## Profile của site

Script tìm `web-profile.json` trong `00-context/` hoặc `00-client-context/`, từ thư mục hiện tại đi lên. Chạy ngoài repo thì thêm `--profile <file>`.

- `url` của profile dùng khi `.env` không có `WP_<MÃ>_URL`.
- `brand_khac` là regex brand không được nhắc. Script cảnh báo khi bài nhắc brand đó.
- Không thấy profile thì script vẫn đăng, in ghi chú và bỏ kiểm brand.

## Quy trình

1. Bài phải xong các bước của repo trước khi đăng: humanize, kiểm entity, chữ ký thương hiệu, nguồn số liệu. Bài theo `wp-xuat-ban-bai` thì `kiem_bai.py` và `kiem_render.mjs` phải đạt.
2. Chạy thử, không gửi gì lên site:
   `python3 skills/wp-dang-bai/scripts/wp_publish.py push <bai.html> --site <mã site> --dry-run`
   Kiểm tiêu đề, slug, SEO title, keyword, số ảnh.
3. Đăng:
   `python3 skills/wp-dang-bai/scripts/wp_publish.py push <bai.html> --site <mã site> --status draft --category <slug chuyên mục> --featured <ảnh đại diện> --featured-alt "…"`
   - `--status draft` (mặc định) để xem trước rồi mới đăng. Đăng thật: `--status publish` sau khi người duyệt xem bản nháp.
   - Slug lấy từ `<meta name="slug">`, SEO title từ `<title>` (khi khác H1), keyword từ `<meta name="keyword">`. Cờ `--slug`, `--seo-title`, `--keyword` thắng thẻ meta. Không có thẻ và không có cờ thì slug sinh từ tiêu đề.
   - `--featured first` lấy ảnh đầu bài làm ảnh đại diện. Ảnh đại diện chuẩn: engine trong `anh_dai_dien.engine` của profile.
   - `--tags` chỉ gán thẻ đã có trên site; thẻ mới nhờ SEO Leader tạo.
4. Sửa bài: sửa file HTML rồi chạy lại đúng lệnh `push`. Script đọc ID bài trong `<bai.html>.wp.json` nên cập nhật bài cũ, không tạo bài mới. Ảnh đã tải không tải lại. Commit file `.wp.json` cùng bài.
5. Mở link script in ra, kiểm trên desktop và mobile: tab bấm được, bảng không tràn ngang, ảnh hiện. Kiểm trường SEO qua REST theo `wp-xuat-ban-bai/references/kiem-sau-dang.md`.
6. Bỏ bài đã đăng từ một file vào thùng rác: `python3 skills/wp-dang-bai/scripts/wp_publish.py trash <bai.html> --site <mã site>`.

Thử lần đầu: đăng `examples/bai-thu.html` ở dạng nháp, xem trước, rồi chạy `trash`.

Script tự làm:
- Lấy tiêu đề từ `<h1>`, mô tả SEO từ `<meta name="description">` nếu không truyền `--seo-desc`.
- Chỉ lấy thân `<main>`; bỏ thanh trên, chân trang, khối tiêu đề, mọi `<script>`.
- CSS riêng của bài (thẻ `<style>` trong `<head>`, trừ blog.css chung) gắn tiền tố `.doc-kit` rồi lưu vào meta `_doc_kit_css`.
- Ảnh base64 và file cục bộ (ảnh, video) tải lên Media, đổi link, điền alt từ thẻ `<img>`. Ảnh đại diện lấy alt từ `--featured-alt`, không có thì lấy tiêu đề.
- Dừng nếu bài có câu cam kết hoàn tiền. Cảnh báo nếu bài nhắc brand trong `brand_khac`.

## Giới hạn

- `<script>` riêng của bài không lên site. Tài khoản đăng bài không có quyền chèn JS. Khối tương tác chung (`.btabs`, `.bquiz`, `.bchk`, `.bcmd`, `.tabs`, `.cmd`, `[data-quiz]`, `.calc`, `.shot`, `.chk`) chạy bằng `doc-kit.js`. Markup: `wp-xuat-ban-bai/references/khoi-doc-kit.md`.
- `.calc` chỉ tính công thức gồm tên thanh trượt, số, `+ - * / ( )` và `round()`.
- Font theo theme. Màu nhấn giữ theo format blog.
- Không tạo page, không sửa bài đứng tên người khác (role Người đăng bài).

## Cập nhật bộ giao diện trên site (admin)

1. Sửa `_format/blog.css` hoặc `wp/doc-kit/doc-kit.js`.
2. `python3 scripts/build_kit.py <đường dẫn blog.css>` sinh lại `wp/doc-kit/doc-kit.css`.
3. Chép `wp/doc-kit.php` vào `wp-content/mu-plugins/` và thư mục `wp/doc-kit/` vào `wp-content/doc-kit/` của site, staging trước. Web không đọc được `mu-plugins/`, nên asset nằm ở `wp-content/doc-kit/`.
4. Handle CSS, JS mang tiền tố `tg-tool-`. Ví dụ site mẫu TAG: theme chỉ giữ asset của theme và handle `tg-tool-*`.

## Gate

- [ ] `doctor` trả OK và `doc-kit trên site: có`.
- [ ] `--dry-run` đúng tiêu đề, slug, SEO title, số ảnh.
- [ ] Script không in cảnh báo "WordPress lọc bớt thẻ".
- [ ] Đã mở bài trên mobile và desktop.

## Bản tốt nhất phải có

- [ ] Bài đăng đúng site của brand, không trộn social proof giữa các brand.
- [ ] Không có key trong file commit, chat hay log.
- [ ] Đăng lại cùng file thì cập nhật bài cũ (có `.wp.json`), không sinh bài trùng.
- [ ] Bản nháp có slug, SEO title, meta, keyword, chuyên mục, ảnh đại diện có alt.
- [ ] Bài publish mở được ở URL chuẩn (script in "URL trả 200").

## Changelog

- v1.2.1 (2026-10-27): publish xong tự mở URL bài, không trả 200 thì thoát 1; ảnh đại diện trùng slug của bài được đổi tên `<slug>-anh-dai-dien`. Lý do: bài content-effort publish trên site mẫu GTV trả 404 vì plugin permalink chưa ghi URI và ảnh mang cùng slug.
- v1.2 (2026-10-27): `--site` nhận mọi mã site; đọc `web-profile.json` (url, `brand_khac`) thay cho hằng số cứng; `--profile`, `--featured-alt`; slug, SEO title, keyword lấy từ thẻ meta của file khi không truyền cờ. Lý do: pilot content-effort 27/10, lần đẩy đầu slug tự sinh dài 70 ký tự và SEO title trống.
- v1.1 (2026-10-27): lệnh `trash`, bài mẫu `examples/bai-thu.html`, link hướng dẫn trên site tài liệu.
- v1.0 (2026-10-27): tạo mới. Thử trên staging hai site mẫu bằng bài content-effort (desktop 1366 px, mobile 390 px: không tràn ngang, 0 lỗi JS, 0 ảnh hỏng), và trên production bằng bản nháp (tác giả team, giữ svg, button, input, bỏ script).
