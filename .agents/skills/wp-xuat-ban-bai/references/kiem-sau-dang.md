# Kiểm sau khi đăng

## 1. Bản nháp (ngay sau `wp_publish.py push --status draft`)

Kiểm qua REST bằng app password của người đăng. Chạy từ root repo để script tìm được `.env`:

```bash
python3 - <<'EOF'
import sys
sys.path.insert(0, "skills/wp-dang-bai/scripts")
import wp_publish as w
wp = w.WP("<mã site>", {"url": "<url site>"})
c, j = wp.req("GET", "/wp/v2/posts/<ID bài>?context=edit")
print(j["status"], j["slug"], j["categories"], j["featured_media"], j.get("doc_seo"))
EOF
```

- `slug` đúng `url_slug` của bài.
- `doc_seo` có `title`, `description`, `focus_keyword`.
- `categories` đúng chuyên mục đã chọn, `featured_media` khác 0.
- Ảnh đại diện có alt: `GET /wp/v2/media/<ID>?context=edit`, trường `alt_text`.

Người duyệt mở link xem trước (`?p=<ID>&preview=true`) khi đã đăng nhập. `kiem_render.mjs` không mở được bản nháp vì bản nháp cần cookie đăng nhập. Bản render trước khi đăng (Bước 6) thay cho bước này.

## 2. Bài đã đăng

```bash
node skills/wp-xuat-ban-bai/scripts/kiem_render.mjs --url <URL bài> --profile <profile> --out <thư mục bài>/render-live
```

- Script báo LOI khi thiếu doc-kit (CSS, JS hoặc class `.doc-kit`), tràn ngang, ảnh hỏng, khối bấm không chạy.
- Mở `desktop.png` và `mobile.png`.
- Xem nguồn trang: một thẻ `<title>`, một `meta description`, `canonical` trỏ về chính URL, schema Article của plugin SEO.

## 3. Sau 1–3 ngày

- Kiểm URL trong Google Search Console (URL Inspection). Nếu chưa lập chỉ mục, bấm yêu cầu lập chỉ mục bằng tay. API không có lệnh này cho bài blog.
- Thêm link từ 2–3 bài cũ cùng cụm về bài mới. Ghi các bài đó vào `link-cho.md` của bài cũ hoặc vào kế hoạch internal link.
- Xử lý `link-cho.md` của các bài khác đang chờ bài này.
- Đo PageSpeed bằng `wp-pagespeed` khi bài thuộc nhóm keyword ưu tiên, hoặc khi bài có loại khối mới (video, công cụ tính lớn). Bài thường dùng kết quả đo của template bài viết.
