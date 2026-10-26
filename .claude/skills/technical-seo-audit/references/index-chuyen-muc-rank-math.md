# Index chuyên mục và phân trang trên site WordPress dùng Rank Math

Đọc file này ở Bước 3 (khu vực 2, 3, 4) khi site dùng Rank Math và audit cần quyết định index chuyên mục, thẻ hoặc trang phân trang. Gốc đường dẫn là root repo. Script: `skills/technical-seo-audit/scripts/`. Lệnh trên server chỉ đọc. Ghi option hoặc sửa theme lên production đi qua trang duyệt của `wp-content-review-apply` và quy trình staging của `wp-staging-deploy` (`skills/`). Hồ sơ server: `00-client-context/wp-server.md`.

Ví dụ trong file lấy từ site agency mẫu, ngày 17–18/10/2026, Rank Math 1.0.280.

## 1. Căn cứ

- Không chặn chuyên mục, thẻ hay trang lưu trữ một cách máy móc. Đánh giá giá trị index của từng loại trang. Nguồn: docx giải thích audit toàn diện §1.9 (wiki [[sources/giai-thich-seo-audit-toan-dien-tag]]).
- Dọn index theo giá trị (traffic, nội dung riêng), không theo loại trang. Nguồn: wiki [[Index Pollution]].
- Google tự gom các trang phân trang vào một cụm. Trang phân trang thật không cần canonical về trang 1. Nguồn: Google Leak Decoded, yếu tố F03.2. Checklist 3.6 dùng cùng luật.

## 2. Đọc trạng thái (chỉ đọc)

Chạy WP-CLI trên server theo `00-client-context/wp-server.md`:

```bash
wp option get rank-math-options-titles --format=json   # tax_category_robots, tax_category_custom_robots, noindex_empty_taxonomies, tax_post_tag_robots
wp option get rank-math-options-sitemap --format=json  # tax_category_sitemap, exclude_terms
wp option get rank_math_modules --format=json          # có "rich-snippet" thì module Schema đang bật
wp option get show_on_front; wp option get page_for_posts
wp post meta get <ID trang blog> rank_math_robots
wp term meta list <term_id> --keys=rank_math_robots    # noindex đặt tay cho từng term
wp post-type list --fields=name,has_archive --format=json
```

Tìm hàm theme và mu-plugin tự gắn noindex:

```bash
rg -n "rank_math/frontend/robots|wp_robots|is_paged\(|noindex" wp-content/themes/<theme> wp-content/mu-plugins
```

Ví dụ (site agency mẫu): hàm theme `custom_rank_math_paged_noindex` gắn noindex cho mọi trang `is_paged()` và cho URL có `/?`. Rank Math cũng đặt `tax_category_robots` = noindex. Kết quả: chuyên mục và trang 2 đều noindex, dù trang 2 có bài khác trang 1. Bản sửa bỏ nhánh `is_paged()` và giữ nhánh URL có query.

## 3. Bảng quyết định

| Loại URL | Mặc định đề xuất | Khi nào đổi |
|---|---|---|
| Chuyên mục có bài và có mô tả riêng | index, có trong sitemap chuyên mục | noindex khi chuyên mục chỉ lặp chuyên mục khác hoặc không có giá trị riêng |
| Chuyên mục rỗng | noindex (`noindex_empty_taxonomies` = on) | Không đổi |
| Thẻ (tag) | Giữ cấu hình hiện tại | Đánh giá theo giá trị như chuyên mục. Thẻ mỏng giữ noindex |
| Phân trang thật (trang 2 có bài khác trang 1) | index, canonical tự trỏ | Không đổi |
| Phân trang giả (trang 2 lặp danh sách trang 1) | canonical về trang 1 | Sửa template cho phân trang thật, rồi cho index |
| URL có tham số (`?s=`, `?orderby=`, filter) | noindex | Filter có nhu cầu tìm kiếm: checklist 3.7 |
| Chuyên mục trùng URL với trang lưu trữ của custom post type | Bỏ khỏi sitemap chuyên mục bằng `exclude_terms` | Sitemap của post type đã có URL này |
| Term đã đặt noindex tay | Giữ | Hỏi người duyệt trước khi đổi |

Ví dụ (site agency mẫu): 14 chuyên mục vào sitemap. 3 chuyên mục trùng URL với trang lưu trữ custom post type bị bỏ khỏi sitemap chuyên mục. Trang `/blog/` index, canonical giữ về `/blog/`, vì `/blog/page/2/` lặp đúng danh sách trang 1.

## 4. Đo

1. Lập `urls.tsv`: mỗi dòng "url<TAB>kỳ vọng". Kỳ vọng là `index`, `noindex`, `loc>=N` hoặc `loc=N`.

   ```text
   https://<domain>/<chuyen-muc>/	index
   https://<domain>/<chuyen-muc>/page/2/	index
   https://<domain>/?s=seo	noindex
   https://<domain>/category-sitemap.xml	loc>=10
   ```

2. Chạy probe. Script không theo redirect, nghỉ 1 giây giữa 2 request, exit 1 khi có dòng lệch:

   ```bash
   python3 skills/technical-seo-audit/scripts/index_probe.py probe --urls urls.tsv --out kq.tsv
   ```

3. Trước khi cho index phân trang, so trang 1 với trang 2:

   ```bash
   python3 skills/technical-seo-audit/scripts/index_probe.py paged https://<domain>/<chuyen-muc>/ https://<domain>/<chuyen-muc>/page/2/
   ```

   - Script bỏ link phân trang (`/page/N/`, `?paged=`) và link có trên cả hai trang (menu, footer).
   - `only_p2` từ 1 trở lên: phân trang thật. Ví dụ (site agency mẫu): `/seo/` p1=50, p2=53, only_p2=13.
   - `only_p2` = 0: phân trang giả.
   - Exit 1 khi một trang không trích được link nào. Không kết luận: bộ trích hỏng. Lượt đo 17/10 ra md5 `d41d8cd9` (chuỗi rỗng) cho danh sách bài.

4. Kết luận index chỉ từ URL sạch. URL có query chỉ dùng để xác nhận noindex. Sau mỗi lần purge cache, kiểm 5 biến thể cache của URL sạch bằng `skills/wp-pagespeed/scripts/cache_variants.py`.

## 5. Thử trên staging

Staging ép noindex toàn site. `zz-staging-safety.php` của `wp-staging-deploy` trả `blog_public` = 0 và gửi `X-Robots-Tag: noindex`. Đo robots trên staging lúc này chỉ thấy noindex.

1. Ghi đổi cấu hình lên staging theo `wp-staging-deploy`.
2. Chép `scripts/robots-public-test.php` vào `wp-content/mu-plugins/` của staging. File chỉ chạy khi `WP_ENVIRONMENT_TYPE` = `staging`.
3. Purge cache staging.
4. Lấy HTML từng URL bằng `stg_get.sh --out <file> <đường dẫn>` của `wp-staging-deploy`.
5. Đọc meta robots và canonical bằng `index_probe.py probe --html <đường dẫn> <file>`. Header `X-Robots-Tag` của staging không vào kết quả.
6. Gỡ `robots-public-test.php` ngay sau lượt đo. Đo lại một URL: meta robots phải về noindex.
7. Ghi giờ gắn và giờ gỡ vào HANDOFF của workstream.

## 6. Ghi lên production

1. Chạy thử script ghi option trước (DRY). Script in giá trị trước và sau của `tax_category_robots`, `tax_category_sitemap`, `exclude_terms` và robots trang blog. So với kết quả staging.
2. Backup option. Ghi sau khi người duyệt bấm Duyệt trên trang duyệt của `wp-content-review-apply`.
3. Sửa hàm theme (ví dụ bỏ nhánh `is_paged()`) trên staging trước, rồi đưa lên theo `wp-staging-deploy`.
4. Sau khi ghi: xoá cache sitemap của Rank Math (`\RankMath\Sitemap\Cache::invalidate_storage()`), purge cache trang.
5. Chạy lại `index_probe.py probe` và `cache_variants.py` trên URL sạch. Đếm `<loc>` của sitemap chuyên mục.
6. Nộp lại sitemap lên GSC theo `references/gsc-ghi.md`. Người duyệt duyệt từng lần.

## 7. Schema Rank Math không xuất JSON-LD

Khi đa số trang không có JSON-LD, tìm nguyên nhân theo thứ tự. Ví dụ (site agency mẫu, 17/10): 357/379 trang không có JSON-LD.

1. Module `rich-snippet` trong `rank_math_modules`. Không có thì module Schema đang tắt.
2. Hàm schema riêng của theme hoặc mu-plugin: `rg -n "application/ld\+json|rank_math/json_ld" wp-content/themes/<theme> wp-content/mu-plugins`. Hàm riêng có thể xuất dữ liệu cũ (địa chỉ, số điện thoại) hoặc trùng với Rank Math.
3. Template Theme Builder của Elementor Pro có điều kiện `include/general`: so JSON-LD của trang dùng template đó với trang không dùng.

Bật lại module hoặc sửa hàm theme trên staging trước. Viết hoặc sửa markup: route sang `schema-markup-generator`.
