# Truy nguồn CSS và sửa có scope

Mục đích: tìm đúng rule đang thắng và mọi bản sao của nó, rồi viết bản sửa không làm hỏng phần khác. Đọc ở Bước 2 và Bước 3 của `SKILL.md`. Gốc đường dẫn là root repo. `$UIF` là `skills/wp-ui-fix/scripts`.

## 1. Bảy nguồn CSS của một site WordPress

`css_sources.sh` quét đủ 7 nguồn dưới. Bảng ghi chỗ sửa đúng cho từng nguồn.

| # | Nguồn | Ví dụ đường dẫn | Sửa ở đâu |
|---|---|---|---|
| 1 | Theme | `wp-content/themes/<theme>/style.css`, `*.scss`, CSS in trong `*.php` | Sửa file theme bằng `theme_patch.py`, hoặc đè bằng mu-plugin có scope |
| 2 | Critical CSS theo template | file tên có `ccss` hoặc `critical`, `litespeed/ccss/` | Sửa mọi bản theo template. Đổi nguồn thì dựng lại critical CSS bằng `skills/wp-pagespeed/scripts/ccss_gen.mjs` |
| 3 | Customizer `custom_css` | bảng `wp_posts`, `post_type=custom_css` | Xuất ra file, sửa, ghi lại bằng WP-CLI sau khi backup. Hoặc chuyển rule sang mu-plugin rồi gỡ khỏi Customizer |
| 4 | mu-plugins | `wp-content/mu-plugins/*.php` | Sửa đúng file của việc đó, không gộp việc khác vào |
| 5 | Elementor | `uploads/elementor/css/post-*.css`, kit | Sửa trong Elementor hoặc kit. Sau khi sửa dữ liệu Elementor, chạy `regen_elementor_css.php` của `wp-staging-deploy` |
| 6 | Plugin | `wp-content/plugins/<plugin>/**/*.css`, CSS do plugin sinh (ví dụ `style_*.css` của Max Mega Menu) | Không sửa file plugin. Đổi trong cài đặt plugin, hoặc đè bằng mu-plugin có scope |
| 7 | File gộp của cache | `litespeed/css/`, `litespeed/ucss/`, `wp-content/cache/` | Không sửa. Sửa bản nguồn ở nguồn 1–6, rồi purge theo URL |

Bẫy Max Mega Menu (nguồn 6): CSS của mega menu có thể nằm trong widget, không nằm trong theme. Nếu `css_sources.sh` không thấy rule ở nguồn 1–5, tìm trong nội dung widget `widget_text` (HTML tuỳ biến của ô menu, có `<style>` hoặc `style=""`). Xuất widget từ DB bằng WP-CLI chỉ đọc (`wp option get widget_text --format=json`), rồi tìm selector trong đó. Sửa bằng cách đổi widget qua dữ liệu đã backup, hoặc đè bằng mu-plugin có scope. Không sửa file `style_*.css` của plugin.

Nguồn 3 nằm trong DB. Truyền `--custom-css-file` hoặc `--wp-cmd`, nếu không script ghi "chưa kiểm" cho nguồn này. Ca thật: lỗi nút slider trang chủ site mẫu gtvseo có gốc ở Customizer CSS (post `custom_css` từ 14/04/2026). Lane chạy 268 phút (22/10/2026).

Lệnh mẫu, chạy trên bản copy local của web root:

```bash
bash "$UIF/css_sources.sh" --wp <web root local> --custom-css-file <lane>/custom_css.txt --tsv '.feat-img' 'height:350px' > <lane>/css_sources.tsv
```

Chạy thẳng trên server qua SSH. Lấy lệnh WP-CLI và user chạy từ `00-client-context/wp-server.md`:

```bash
ssh <alias> "bash -s -- --wp <web root> --wp-cmd '<lệnh wp-cli theo wp-server.md>' --tsv '.feat-img'" < "$UIF/css_sources.sh" > <lane>/css_sources.tsv
```

Nếu lệnh chạm staging, pipe cả stdout và stderr qua `stg_mask` theo `wp-staging-deploy` Bước 2.

### Luật sửa mọi bản sao

1. Ghi mọi file khớp ở nguồn 1–6 vào bảng nguồn (mục 3).
2. Mỗi dòng có cách sửa, hoặc lý do giữ.
3. Sau khi sửa, chạy lại `css_sources.sh` với giá trị cũ. Nguồn 1–6 phải trả 0 khớp (mã thoát 1), trừ dòng đã ghi lý do giữ.
4. Nguồn 7 tự hết sau khi purge. Kiểm lại trên bản có cache bằng `match.mjs`.

Ca thật: lần sửa khung ảnh ngày 19/10/2026 trên site mẫu gtvseo bỏ sót `height:350px` ở 5 file critical CSS. Ngày 20/10 phải làm lại một lane (56 phút).

## 2. Đọc kết quả `match.mjs`

```bash
node "$UIF/match.mjs" https://example.vn/dich-vu/ '.accordion-body p' --widths 390,1366 --props font-size,line-height --out <lane>/match_acc.json
```

| Trường | Ý nghĩa |
|---|---|
| `thắng` | Selector, specificity `(a,b,c)`, `!important`, inline, `@media`, file và dòng của rule đang áp |
| `bản sao bị đè` | Mọi khai báo cùng thuộc tính bị thua, kèm lý do thua |
| `muốn đè` | Điều kiện để một rule mới thắng, ví dụ "specificity > (0,4,1)" |
| `lưu ý` | Rule nằm ở file gộp cache, critical CSS hoặc CSS Elementor sinh: phải tìm bản nguồn |

- Đo đủ bề rộng: 390, 1366 và các mốc `@media` của theme mà output in ra.
- Thẻ hay nút vừa đổi: chạy thêm `--state hover`, `--state focus`, `--state visited`. Ca thật: sau khi đổi thẻ, `:visited` cộng `:hover` ra chữ trắng trên nền trắng (site mẫu gtvseo, 18/10/2026 17:33).
- Rule nằm trong `@layer` có tên: output ghi "thứ tự giữa các layer chưa được kiểm". Kiểm tay thứ tự khai báo layer.

Bẫy chụp mega menu: panel của Max Mega Menu không mở bằng hover trong Chrome headless. Chụp bằng click vào mục menu, rồi chụp lúc mở. Dùng `interact_probe.mjs` của `web-qa-gate`. Không kết luận "panel không hiện" từ ảnh chụp bằng hover.

## 3. Bảng nguồn

Ghi file `<lane>/nguon-css.md` trước khi viết rule mới:

| Nguồn | File:dòng | Selector | Giá trị hiện tại | Cách sửa | Bản sao còn lại |
|---|---|---|---|---|---|
| 2 critical | `.../ccss-home.css:1` | `.feat-img` | `height:350px` | `theme_patch.py` mục `feat-img-h` | 0 sau khi sửa |

## 4. Luật scope

1. Đặt tiền tố scope cho mọi rule: body class của template (`body.single-post`, `body.page-id-<id>`) hoặc id, class của section.
2. Không viết rule toàn cục trên `h1`–`h6`, `p`, `nav`, `button`, `a`, `li`. `theme_patch.py` chặn rule có selector không chứa class, id hoặc thuộc tính, kể cả trong `@media`. Ca thật: review đối kháng 18/10/2026 bỏ 3 rule gây hồi quy (H1 toàn cục, flex menu, 13 px diện rộng).
3. Loại icon khỏi selector đổi font: thêm `:not(i):not([class*="fa-"]):not([class*="icon"]):not(svg)`. `theme_patch.py` cảnh báo khi rule font chạm icon.
4. Loại component đặc biệt khai trong `00-client-context/ui-rules.md`. Dùng `:not(:where(.comp-a, .comp-b) *)`. `:where()` có specificity 0, nên rule giữ nguyên độ ưu tiên với phần còn lại của trang. Ví dụ site mẫu gtvseo (21/10/2026): `:not(:where(.gtv-tool,.gtv-sp,.gtv-fc) *)`.
5. Nếu gộp nhiều selector trong `:is()` ở vế phải của rule trên trang nặng, đo A/B PSI trước khi giữ. Ca thật: site mẫu gtvseo 21/10/2026, bản gộp `:is()` làm PSI mobile tụt 4–11 điểm. Bản viết từng selector riêng không tụt. Nguyên nhân chưa đo bằng trace.
6. Khi đổi `div onclick` sang `a` hoặc `button`: reset style nút của kit builder (màu nút kit Elementor), rồi chạy hạng mục "Tương tác và trạng thái" của `web-qa-gate`.

## 5. Mỗi việc một mu-plugin

- Đặt tên file theo việc, có tiền tố của site: `<tiền tố>-<việc>.php`. Ví dụ site mẫu gtvseo: `gtv-thang-chu-template.php`.
- Hàm PHP có tiền tố riêng của đợt. Kiểm trùng tên hàm bằng `wp eval` theo `wp-staging-deploy` Bước 3.
- In CSS trong `<style id="<việc>" data-no-optimize="1">`. Id riêng giúp kiểm khối có mặt ở bản có cache và bản bỏ cache.
- Ghi marker version trong CSS, ví dụ `/* v4 */`. Kiểm marker sau khi purge.
- Trả về: chuyển file vào quarantine, không xoá.

```bash
python3 "$UIF/theme_patch.py" quarantine <web root> wp-content/mu-plugins/<việc>.php --to <lane>/quarantine            # chạy thử
python3 "$UIF/theme_patch.py" quarantine <web root> wp-content/mu-plugins/<việc>.php --to <lane>/quarantine --apply
python3 "$UIF/theme_patch.py" unquarantine <web root> --from <lane>/quarantine --apply                                   # trả lại
```

`MANIFEST.tsv` trong thư mục quarantine ghi giờ, đường dẫn, sha256, cỡ file.

## 6. Sửa theme bằng `theme_patch.py`

Spec là danh sách mục `{id, file, old, new, count, regex?, css?, allow_global?}`. Ví dụ:

```json
[{"id": "feat-img-h", "file": "wp-content/themes/<theme>/assets/ccss-home.css", "old": ".feat-img{height:350px}", "new": "body.home .feat-img{aspect-ratio:16/9}", "count": 1}]
```

Trình tự:

1. Chép file cần sửa về bản copy local. Không sửa thẳng trên production.
2. Chạy thử: `python3 "$UIF/theme_patch.py" apply <bản copy> <lane>/spec.json --backup <lane>/backup`. Lệnh in JSON, không ghi gì.
3. Ghi: thêm `--apply`. Script backup bản gốc đầu tiên, lint (`php -l` hoặc ngoặc CSS), tự trả bản gốc khi lint hỏng.
4. Chạy lại lệnh ở bước 3. Mọi mục phải ra `already`. Nếu không, spec chưa idempotent.
5. Deploy lên staging, rồi production, theo `wp-staging-deploy`.
6. Trước khi đè production, chạy bước 2 trên bản copy mới lấy từ production. Số khớp phải bằng số khớp trên staging. Nếu lệch, dừng: file production đã khác bản đã thử.
7. Trả về: `python3 "$UIF/theme_patch.py" restore <bản copy> --backup <lane>/backup --apply`, rồi deploy lại.

Mã thoát 1 khi có mục lệch, rule toàn cục hoặc lint hỏng. File có mục lệch không bị ghi. Thiếu php thì script không ghi file `.php`: đặt `--php` hoặc `PHP_BIN` theo `wp-server.md`.

## 7. Thử CSS trước khi deploy

- Rule mới thắng chưa: `node "$UIF/match.mjs" <url> <selector> --props <thuộc tính> --css <lane>/thu.css`. Mã thoát 3 nghĩa là CSS thử thua ở ít nhất một thuộc tính. Tăng specificity theo dòng "muốn đè", chạy lại tới khi mã thoát 0. Ca thật: CSS form thua specificity, lane đẩy staging 3 lượt (site mẫu gtvseo, 18/10/2026 21:00).
- Ảnh khi chưa deploy: `node "$UIF/shot_el.mjs" ... --css <lane>/thu.css --label thu`.
- Đo CLS của CSS mới: chèn CSS qua CDP `Fetch` theo `skills/wp-pagespeed/references/checklist-theo-lop.md` lớp 6. `--css` của hai script trên chèn sau khi tải trang, nên không dùng để đo CLS.
- Vòng sửa chỉ chạy trên trang lỗi. Lượt cuối chạy đủ mọi trang của template.
