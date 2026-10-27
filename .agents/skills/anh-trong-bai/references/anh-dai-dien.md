# Ảnh đại diện của bài

Ảnh đại diện (featured image) hiện ở lưới blog, kết quả Discover và ảnh chia sẻ. Mỗi site dùng một engine, khai trong `anh_dai_dien.engine` của profile. Repo nào đăng bài phải có engine đó trong `skills/`.

## Luật chung

- Chữ trên ảnh là H1 rút gọn, không phải câu mới. Chữ trái, hình phải.
- Hình tả thực thể chính của bài.
- Ảnh WebP 16:9 (1200×675). Engine có tỉ lệ 4:3 và 1:1 thì xuất kèm cho Discover và mạng xã hội.
- Alt là headline cộng sub của ảnh. Tên file tối đa 3 từ không dấu, chứa keyword chính.
- Dùng `~` giữa hai từ không được tách dòng (engine `featured-image-seo`).
- Ảnh đại diện không lặp ảnh trong thân bài.

## Engine `featured-image-seo`

Ví dụ site mẫu GTV, `anh_dai_dien.brand` là `gtv`. Một bài là một spec trong `specs.json`:

```json
[{"id": 1, "h1": "<H1 đầy đủ>", "title": "*<cụm nhấn>* là gì?", "sub": "<sub ngắn, dùng ~ để giữ cụm>",
  "alt": "<headline + sub>", "file_name": "<keyword>.webp", "style": "ui-annotated", "variant": "pipeline",
  "kind": "flat", "win": [610, 96, 680, 640], "tw": 500, "th": 520, "fit": "92,60", "nguon": "code"}]
```

```bash
/usr/bin/python3 skills/featured-image-seo/scripts/dung_anh.py <thư mục bài>/anh-dai-dien/specs.json --brand <brand> --ratios 4:3,1:1
python3 skills/featured-image-seo/scripts/kiem_ocr.py <thư mục bài>/anh-dai-dien/specs.json --brand <brand>
```

- `title` dùng `*…*` để tô gradient cụm nhấn.
- Chọn `style` và `variant` theo `skills/featured-image-seo/references/template-va-thuong-hieu.md`. `ui-annotated` cần `win`, `tw`, `th`.
- `kiem_ocr.py` đọc lại chữ trên ảnh bằng Vision của macOS. Script báo `chu_thap` khi dòng chữ thấp hơn `--min-h` (mặc định 25, tương ứng chữ cỡ 30 px). Chữ thiếu hoặc tách dòng sai thì sửa spec.
- Repo có Jev thì chạy thêm `kiem_jev.py` theo `skills/featured-image-seo/references/kiem-jev.md`.
- Output: `out/<id>.webp`, `out/<id>-43.webp`, `out/<id>-11.webp`. Đổi tên `out/<id>.webp` thành `file_name` trước khi đăng.

## Engine `tag-anh-dai-dien`

Ví dụ site mẫu TAG. Một bài là một spec trong `specs.json` theo `skills/tag-anh-dai-dien/references/format.md`: `id`, `slug`, `cat`, `hl`, `sub`, `alt`, `panel` và trường riêng của panel.

```bash
python3 skills/tag-anh-dai-dien/scripts/anh_dai_dien.py <thư mục bài>/anh-dai-dien/specs.json --sheet
```

- Output: `out/<slug>.webp` (1200×675, dưới 45 KB) và `out/<slug>-og.jpg` (ảnh chia sẻ).
- Script in `ok <cỡ chữ>` khi chữ vừa khung. `TRAN` thì rút chữ trong spec.
- Bài mới không cần `dat_anh.sh`. Ảnh lên site qua `wp_publish.py --featured`.

## Đưa lên site

```bash
python3 skills/wp-dang-bai/scripts/wp_publish.py push <bai.html> --site <mã site> --featured <ảnh.webp> --featured-alt "<alt>"
```

`wp_publish.py` tải ảnh lên Media, gắn alt và đặt làm ảnh đại diện. Đăng lại cùng file thì không tải ảnh lần hai.

## Ca thật

- Pilot 27/10/2026: sub "nỗ lực trong nội dung" bị tách giữa "nỗ" và "lực". Viết `nỗ~lực` và `nội~dung` thì OCR đọc đúng, chữ nhỏ nhất 33 px.
