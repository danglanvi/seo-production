---
name: wp-dang-bai
description: "Đăng hoặc cập nhật bài lên WordPress gtvseo.com, theaigrowth.io qua REST bằng app password: file HTML format tài liệu pages.dev giữ nguyên giao diện (bảng, tab, quiz, checklist, SVG, video), tự tải ảnh lên Media, điền Rank Math, chuyên mục, tác giả team. Dùng khi đẩy bài viết từ Claude Code lên website."
metadata:
  version: "1.1"
---

# wp-dang-bai — đăng bài lên WordPress qua API

Script `scripts/wp_publish.py` (Python stdlib) đưa một file HTML lên WordPress. Site cần có mu-plugin `doc-kit` (thư mục `wp/`); gtvseo.com và theaigrowth.io đã cài ngày 27/10/2026.

## Khi nào dùng

- Đăng bài mới hoặc cập nhật bài đã đăng trên gtvseo.com (`--site gtv`) hoặc theaigrowth.io (`--site tag`).
- Bài viết theo format bài blog của site tài liệu GTV (`_format/mau-blog/`), hoặc HTML thường.
- Không dùng khi: sửa title, meta, link hàng loạt trên bài cũ (dùng `wp-content-review-apply`); sửa trang dịch vụ, trang chủ (page); site khác 2 site trên.

## Cài đặt một lần cho mỗi người

1. Xin admin (Vincent) một app password của tài khoản `api-team` trên site cần đăng. Mỗi người một app password, tên `<Tên> - <máy>`.
   - Admin tạo trong wp-admin: Users → API Team → Application Passwords. Hoặc agent có SSH chạy `wp user application-password create api-team "<Tên> - <máy>" --porcelain`.
2. Ghi vào file `.env` ở thư mục gốc repo (đã nằm trong `.gitignore`). Không dán key vào chat, file khác hay commit:

```
WP_GTV_URL=https://gtvseo.com
WP_GTV_USER=api-team
WP_GTV_APP_PASSWORD=<chuỗi app password>
WP_TAG_URL=https://theaigrowth.io
WP_TAG_USER=api-team
WP_TAG_APP_PASSWORD=<chuỗi app password>
```

3. Kiểm: `python3 skills/wp-dang-bai/scripts/wp_publish.py doctor --site gtv`. Kết quả đúng có 2 dòng `OK … role team_writer` và `doc-kit trên site: có`.

Người có tài khoản riêng (SEO Leader, Người đăng bài) tạo app password trong hồ sơ của chính mình và đặt `WP_*_USER` là tên đăng nhập đó. Bài của SEO Leader và Người đăng bài đều đứng tên tài khoản team.

## Quy trình

1. Bài phải xong các bước của repo trước khi đăng: humanize, kiểm entity GTV ≠ TAG, chữ ký thương hiệu, nguồn số liệu.
2. Chạy thử, không gửi gì lên site:
   `python3 skills/wp-dang-bai/scripts/wp_publish.py push <bai.html> --site gtv --dry-run`
   Kiểm tiêu đề, slug, số ảnh. Nếu slug tự sinh quá dài, thêm `--slug`.
3. Đăng:
   `python3 skills/wp-dang-bai/scripts/wp_publish.py push <bai.html> --site gtv --status publish --category <slug chuyên mục> --seo-title "…" --seo-desc "…" --keyword "…" --featured <ảnh đại diện>`
   - `--status draft` (mặc định) để xem trước rồi mới đăng.
   - `--featured first` lấy ảnh đầu bài làm ảnh đại diện. Ảnh đại diện chuẩn: skill `featured-image-seo` (GTV), `tag-anh-dai-dien` (TAG).
   - `--tags` chỉ gán thẻ đã có trên site; thẻ mới nhờ SEO Leader tạo.
4. Sửa bài: sửa file HTML rồi chạy lại đúng lệnh `push`. Script đọc ID bài trong `<bai.html>.wp.json` nên cập nhật bài cũ, không tạo bài mới. Ảnh đã tải không tải lại. Commit file `.wp.json` cùng bài.
5. Mở link script in ra, kiểm trên desktop và mobile: tab bấm được, bảng không tràn ngang, ảnh hiện.
6. Bỏ bài đã đăng từ một file vào thùng rác: `python3 skills/wp-dang-bai/scripts/wp_publish.py trash <bai.html> --site gtv`.

Thử lần đầu: đăng `examples/bai-thu.html` ở dạng nháp, xem trước, rồi chạy `trash`. Hướng dẫn từng bước: https://gtv-dao-tao.pages.dev/production/content/dang-bai-wordpress/

Script tự làm:
- Lấy tiêu đề từ `<h1>`, mô tả SEO từ `<meta name="description">` nếu không truyền `--seo-desc`.
- Chỉ lấy thân `<main>`; bỏ thanh trên, chân trang, khối tiêu đề, mọi `<script>`.
- CSS riêng của bài (thẻ `<style>` trong `<head>`, trừ blog.css chung) gắn tiền tố `.doc-kit` rồi lưu vào meta `_doc_kit_css`.
- Ảnh base64 và file cục bộ (ảnh, video) tải lên Media, đổi link, điền alt từ thẻ `<img>`.
- Dừng nếu bài có câu cam kết hoàn tiền. Cảnh báo nếu bài GTV nhắc brand TAG hoặc ngược lại.
- Tác giả hiển thị tự là "GTV SEO Team" hoặc "The AI Growth Team" (mu-plugin team-accounts). Không truyền tác giả.

## Giới hạn

- `<script>` riêng của bài không lên site (ví dụ khối tự chấm rubric của bài content-effort). Tài khoản `api-team` không có quyền chèn JS. Khối tương tác chung (`.btabs`, `.bquiz`, `.bchk`, `.bcmd`, `.tabs`, `.cmd`, `[data-quiz]`, `.calc`, `.shot`, `.chk`) chạy bằng `doc-kit.js`.
- `.calc` chỉ tính công thức gồm tên thanh trượt, số, `+ - * / ( )` và `round()`.
- Font theo theme (GTV: Inter + Montserrat; TAG: Be Vietnam Pro). Màu nhấn giữ theo format blog.
- Không tạo page, không sửa bài đứng tên người khác (role Người đăng bài).

## Cập nhật bộ giao diện trên site (admin)

1. Sửa `_format/blog.css` hoặc `wp/doc-kit/doc-kit.js`.
2. `python3 scripts/build_kit.py <đường dẫn blog.css>` sinh lại `wp/doc-kit/doc-kit.css`.
3. Chép `wp/doc-kit.php` vào `wp-content/mu-plugins/` và thư mục `wp/doc-kit/` vào `wp-content/doc-kit/` của site, staging trước. Web không đọc được `mu-plugins/`, nên asset nằm ở `wp-content/doc-kit/`.
4. Handle CSS, JS mang tiền tố `tg-tool-`: theme theaigrowth chỉ giữ asset của theme và handle `tg-tool-*`.

## Gate

- [ ] `doctor` trả OK và `doc-kit trên site: có`.
- [ ] `--dry-run` đúng tiêu đề, slug, số ảnh.
- [ ] Script không in cảnh báo "WordPress lọc bớt thẻ".
- [ ] Đã mở bài trên mobile và desktop.

## Bản tốt nhất phải có

- [ ] Bài đăng đúng site của brand, không trộn social proof GTV và TAG.
- [ ] Không có key trong file commit, chat hay log.
- [ ] Đăng lại cùng file thì cập nhật bài cũ (có `.wp.json`), không sinh bài trùng.

## Changelog

- v1.1 (2026-10-27): lệnh `trash`, bài mẫu `examples/bai-thu.html`, link hướng dẫn trên site tài liệu.
- v1.0 (2026-10-27): tạo mới. Thử trên staging GTV và TAG bằng bài content-effort (desktop 1366 px, mobile 390 px: không tràn ngang, 0 lỗi JS, 0 ảnh hỏng), và trên production bằng bản nháp (tác giả team, giữ svg, button, input, bỏ script).
