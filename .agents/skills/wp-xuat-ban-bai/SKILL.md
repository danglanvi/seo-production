---
name: wp-xuat-ban-bai
description: "Xuất bản bài blog đã humanize lên WordPress: Markdown thành HTML doc-kit, media trong bài, ảnh đại diện, khối bấm thử, kiểm luật site và link nội bộ, render thử trên theme thật, đăng nháp, kiểm sau đăng. Dùng khi đưa bài mới lên site có web-profile."
metadata:
  version: "1.0.1"
---

# wp-xuat-ban-bai — xuất bản bài blog lên WordPress

Skill này nối các trạm từ bài humanize tới bài đã đăng. Mỗi site có một file `web-profile.json` giữ luật riêng: link ngoài, chữ ký, màu, font, khung nội dung của theme, engine ảnh đại diện. Script đọc profile, nên skill dùng chung cho mọi site.

Gốc đường dẫn là root repo. Script ở `skills/wp-xuat-ban-bai/scripts/`:

| File | Việc |
|---|---|
| `md_to_html.py` | Markdown humanize thành HTML theo format blog doc-kit: H1, đoạn mở, khối `.prose` và `.wide`, số chú thích nguồn, khung chờ media |
| `kiem_bai.py` | Kiểm luật trước khi đăng: H1, chuỗi giữ chỗ, script, cam kết hoàn tiền, brand khác, link ngoài, chữ ký, alt, cấu trúc khối bấm. `--online` kiểm link nội bộ trả 4xx, 3xx |
| `kiem_render.mjs` | Ghép thân bài vào bài mẫu của theme thật, đo ở 1366 px và 390 px: tràn ngang, ảnh hỏng, lỗi JS của doc-kit, khối bấm chạy được, chữ sơ đồ trên điện thoại. `--url` kiểm bài đã đăng |
| `_cdp.mjs` | Hàm Chrome headless dùng chung (mở tab, chặn analytics, chụp, gom lỗi JS) |

Mẫu profile: `web-profile/_mau.json`. Test, chạy từ `skills/wp-xuat-ban-bai/`: `python3 -B tests/test_xuat_ban.py`.

## Khi nào dùng

- Bài blog mới đã qua Humanize, cần lên site WordPress có mu-plugin doc-kit.
- Bài cũ cần đăng lại với media, khối bấm hoặc format mới.
- Không dùng để sửa title, meta, link hàng loạt trên bài cũ. Dùng `wp-content-review-apply`.
- Không dùng cho trang dịch vụ, trang chủ, landing. Các trang đó đi theo `wp-theme-build` hoặc `wp-ui-fix`.

## Phân vai với skill khác

| Trạm | Skill | Ra gì |
|---|---|---|
| Viết, humanize | `seo-article`, `humanizer` (repo content) | Bài `.md` có frontmatter `meta_title`, `meta_description`, `url_slug`, `primary_keyword`, bảng `## Image placeholders` |
| Media trong bài | `anh-trong-bai` | `media_plan.json`, sơ đồ SVG, ảnh chụp, ảnh AI, khối tương tác đã chèn vào HTML |
| Ảnh đại diện | engine trong `anh_dai_dien.engine` của profile | WebP 16:9 kèm 4:3 và 1:1, alt |
| Link nội bộ | `internal-linking` (repo SEO) hoặc bảng "Internal links used" của bài | Link đúng ngữ cảnh, đích trả 200 |
| Title, meta | `seo-onpage` (`serp_pixel.py` khi repo có) | Title và meta không bị cắt |
| Đẩy lên site | `wp-dang-bai` | Bài nháp hoặc bài đăng, `<bai>.html.wp.json` |
| Sau đăng | `web-qa-gate`, `wp-pagespeed` | Kiểm giao diện, tốc độ theo template |

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Bài humanize `.md`, hoặc HTML format blog | repo content (`08-humanized/`) hoặc người vận hành | dừng |
| `web-profile.json` của site | `00-context/` (repo content) hoặc `00-client-context/` (repo SEO). Schema: `references/web-profile.md` | dựng từ `web-profile/_mau.json`, hỏi các trường luật |
| Media brief của bài | `07-media-brief/` (repo content) | `anh-trong-bai` lập plan từ bảng placeholder |
| App password của người đăng | `.env` theo `wp-dang-bai` | dừng ở bước đăng |
| Danh sách chuyên mục của site | `curl -s "<url>/wp-json/wp/v2/categories?per_page=100&_fields=slug,name,count"` | hỏi SEO Leader |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Script | Chuyển định dạng, kiểm luật đếm được, kiểm link sống, render trên theme thật, đo tràn và chữ nhỏ | Dùng. Script là cổng chặn |
| Jev `category-pick` | Chọn chuyên mục chính khi site có trên 15 chuyên mục | Repo SEO có `tools/ai-assist/`. Claude đọc lại khi xác suất dưới 0,7 |
| Jev `link-placement` | Chấm vị trí link nội bộ (zone, fit, need) khi bài có từ 5 link | Theo ngưỡng của `internal-linking` Bước 4b |
| Jev `seo-text-qa` | Soát chính tả, thiếu chữ ở title, meta, caption | Dùng khi đăng từ 5 bài một đợt. Bài lẻ thì Claude đọc |
| Jev `ui-visual` | Soát `desktop.png`, `mobile.png` của `kiem_render.mjs`: chữ bị cắt, khối che, đè nhau | Claude xem ảnh khi nhãn khác "không" |
| EmbeddingGemma 2 | Tìm bài đích cho link nội bộ khi site có chỉ mục `site-vector-index` | Chỉ là danh sách ứng viên. Claude chọn |
| Claude | Chọn khối bấm cho từng H2, viết spec media, đọc mục bị cờ, chọn chuyên mục, quyết định đăng nháp | Dùng |

Repo content không có `tools/ai-assist/`. Ở đó Claude làm phần của Jev và EmbeddingGemma.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,pillow,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu repo không có `tools/capabilities.py` (repo content), kiểm tay: `python3 --version` (từ 3.9), `node --version` (từ 22), `python3 -c "import PIL"`, và Chrome có trong `/Applications/Google Chrome.app` hoặc biến `CHROME`. Thiếu Chrome thì bỏ Bước 6 và báo người duyệt kiểm tay trên 2 cỡ màn hình.

1. Đọc profile. In `luat_rieng` ra và đọc hết trước khi sửa bài. Nếu profile thiếu `render.bai_mau` hoặc `chu_ky`, hỏi người vận hành.
2. Chuyển bài sang HTML:

   ```bash
   python3 skills/wp-xuat-ban-bai/scripts/md_to_html.py <bai.md> --profile <profile> --out <thư mục bài>
   ```

   - Script lấy thân bài, bỏ phần báo cáo của Humanize (Change log, Image placeholders, Internal links used).
   - Link ra ngoài thành số chú thích `[n]` khi `link_ngoai` là `chu-thich`. Mục Nguồn tham khảo ghi URL dạng chữ.
   - Mỗi dòng `[IMG-NN]` thành khung chờ media.
3. Dựng media trong bài theo skill `anh-trong-bai`. Kết thúc bước này khi `media_plan.py kiem --html` không còn lỗi.
4. Thêm khối bấm thử theo `references/khoi-doc-kit.md`.
   - Mỗi H2 có một hình, bảng hoặc khối bấm. Ngoại lệ: FAQ, Nguồn tham khảo.
   - Bài có ít nhất một khối bấm: tab, quiz, checklist hoặc công cụ tính.
   - Không viết `<script>` trong bài. WordPress bỏ thẻ này. Công cụ tính dùng `.calc`.
5. Rà link nội bộ và chữ ký theo `references/luat-bai-web.md`.
   - Link tới bài chưa đăng: bỏ thẻ `<a>`, giữ chữ, ghi dòng vào `link-cho.md` cạnh bài (anchor, URL dự kiến, câu chứa link).
   - Đo title và meta bằng `serp_pixel.py` của `seo-onpage` khi repo có script này.
6. Kiểm trước khi đăng:

   ```bash
   python3 skills/wp-xuat-ban-bai/scripts/kiem_bai.py <bai.html> --profile <profile> --online
   node skills/wp-xuat-ban-bai/scripts/kiem_render.mjs <bai.html> --profile <profile> --out <thư mục bài>/render-1
   ```

   - `kiem_bai.py` thoát 1 thì sửa mọi dòng `LOI`. Đọc từng `CANH_BAO` và ghi lý do giữ.
   - `kiem_render.mjs` thoát 1 thì sửa rồi chạy lại vào thư mục `render-2`. Lỗi JS của plugin khác trên site chỉ là `canh_bao_js`.
   - Mở `desktop.png` và `mobile.png` để xem bằng mắt.
7. Dựng ảnh đại diện theo `anh-trong-bai/references/anh-dai-dien.md`.
8. Đăng nháp bằng `wp-dang-bai`:

   ```bash
   python3 skills/wp-dang-bai/scripts/wp_publish.py push <bai.html> --site <mã site> --profile <profile> --status draft \
     --category <slug chuyên mục> --featured <ảnh đại diện.webp> --featured-alt "<alt>"
   ```

   - Script lấy slug, SEO title, keyword từ thẻ meta do Bước 2 sinh. Cờ dòng lệnh thắng thẻ meta.
   - Kiểm kết quả qua REST: slug, `doc_seo`, chuyên mục, ảnh đại diện, alt (`references/kiem-sau-dang.md` mục 1).
   - Khi publish, script mở URL bài. URL trả 404 thì xử lý theo `references/kiem-sau-dang.md` mục 2.
9. Gửi link xem trước cho người duyệt. Chỉ đăng thật khi người duyệt đồng ý: chạy lại lệnh Bước 8 với `--status publish`.
10. Kiểm sau đăng theo `references/kiem-sau-dang.md`: `kiem_render.mjs --url`, link nội bộ, Rank Math, chỉ mục.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] `kiem_bai.py --online` thoát 0. Nguồn lỗi: pilot 27/10, bài còn `[LINK-CHỜ]` và một link nội bộ trả 404 vì bài đích chưa đăng.
- [ ] `kiem_render.mjs` đạt ở 1366 px và 390 px trên theme thật, và đã xem 2 ảnh chụp. Nguồn lỗi: pilot 27/10, plugin mục lục của theme ném lỗi JS sau khi ghép thân bài; script tách lỗi doc-kit khỏi lỗi plugin khác.
- [ ] Mỗi H2 có hình, bảng hoặc khối bấm; bài có ít nhất một khối bấm chạy được khi không có `<script>`. Nguồn lỗi: 27/10, khối tự chấm của bài pilot viết bằng script riêng không lên được site.
- [ ] Link ngoài theo `link_ngoai` của profile, mục Nguồn tham khảo đủ URL. Nguồn: luật site mẫu 20/10, không hyperlink ra ngoài.
- [ ] Slug, SEO title, meta, keyword, chuyên mục, alt ảnh đại diện có trên bản nháp, kiểm qua REST. Nguồn lỗi: pilot 27/10, lần đẩy đầu slug tự sinh dài 70 ký tự và SEO title trống.
- [ ] Không có câu cam kết hoàn tiền, không nhắc brand bên kia, chữ ký thương hiệu đúng 1 lần. Nguồn: luật workspace về cam kết và luật tách brand, `kiem_bai.py` chặn cả hai.
- [ ] Bài chỉ lên `publish` sau khi người duyệt xem bản nháp. Nguồn: pilot 27/10, bản nháp đầu thiếu slug và SEO title, chỉ thấy khi kiểm qua REST.

## Output

- `<slug>.html` đã chèn media, `render-N/` (render.json, desktop.png, mobile.png), `link-cho.md` nếu có.
- Bản nháp hoặc bài đăng trên site, `<slug>.html.wp.json` (ID bài, ID media).
- Báo cáo ngắn cho người duyệt: link xem trước, số lỗi và cảnh báo còn giữ kèm lý do, việc chờ (link chờ, ảnh chờ).

## Gate

- Không đăng khi `kiem_bai.py` hoặc `kiem_render.mjs` còn lỗi.
- Không đăng `publish` khi chưa có người duyệt bản nháp.
- Không sửa bài đứng tên người khác, không tạo chuyên mục hay thẻ mới.
- Không đưa key, app password vào bài, log hay file commit.

## Anti-patterns

- Dán HTML có `<script>` riêng rồi tin bài sẽ chạy như bản local.
- Để link tới bài chưa đăng. Link đó trả 404 khi bài lên.
- Coi lỗi JS của plugin khác là lỗi của bài, hoặc bỏ qua lỗi JS của doc-kit.
- Chỉ xem bài ở desktop. Sơ đồ và bảng hay vỡ ở 390 px.
- Đổi màu, font của bài khác theme. Màu và font lấy từ profile.

## Changelog

- v1.0.1 (2026-10-27): `kiem_render.mjs --url` nhận doc-kit theo rule CSS và khối bấm chạy được (plugin cache gộp file). `kiem-sau-dang.md` thêm cách xử lý URL 404 sau publish do plugin permalink và ảnh trùng slug. Lý do: publish bài pilot trên site mẫu GTV.
- v1.0 (2026-10-27): tạo mới. Pilot bài content-effort trên site mẫu GTV: `md_to_html.py` ra 7 khung media, `kiem_bai.py` bắt link chờ và link 404, `kiem_render.mjs` đạt ở 1366 px và 390 px, đăng nháp có slug, SEO title, chuyên mục, ảnh đại diện.
