---
name: wp-paid-plugin-exit
description: "Thay plugin và theme trả phí không có licence bằng bản free hoặc code tự viết: Elementor Pro sang widget free, ACF Pro sang SCF, Permalink Manager Pro sang bản đồ URL khoảng 80 dòng, Flatsome sang theme riêng. Kiểm kê trước, giữ bản tắt 7 ngày để rollback."
metadata:
  version: "1.3"
---

# wp-paid-plugin-exit — bỏ plugin trả phí không licence

Plugin hoặc theme trả phí không có licence thì không nhận bản vá bảo mật. Skill này kiểm kê phần site đang dùng của plugin đó, thay bằng bản free hoặc code tự viết, kiểm trên staging, rồi tắt plugin trên production. Skill giữ plugin ở trạng thái tắt 7 ngày để rollback.

Gốc đường dẫn là root repo. Script ở `skills/wp-paid-plugin-exit/scripts/`:

| Script | Việc |
|---|---|
| `el_inventory.php` | Kiểm kê Elementor Pro: widget Pro, Custom CSS, sticky, motion, link popup, điều kiện Theme Builder. Chỉ đọc |
| `el_free_convert.php` | Đổi widget Pro sang widget free (image, shortcode, html). `DRY=1` mặc định. Lưu bản gốc trước khi ghi |
| `acf_inventory.php` | Kiểm kê ACF Pro: nhóm trường, loại trường Pro, trang Options, block. Chỉ đọc |
| `pm_export.php` | Xuất bản đồ URL của Permalink Manager và so với link plugin đang in. Chỉ đọc |
| `permalink-uris.php` | mu-plugin thay Permalink Manager: đọc `permalink-uris.json`, phân giải request, in link, 301 URL gốc |

Mẫu mu-plugin cho Elementor free: `assets/elementor-free-compat.php`. Mẫu này giữ header và footer Theme Builder, shortcode `[elementor-template]`, ô Custom CSS, và shortcode thay widget Pro.

Test: `tests/test_permalink_uris.php` (chạy `php tests/test_permalink_uris.php`).

## Khi nào dùng

- Site có plugin hoặc theme trả phí đã hết licence hoặc dùng bản không rõ nguồn.
- Rà bảo mật báo plugin trả phí không cập nhật được.
- Chuẩn bị đổi theme và cần gỡ phụ thuộc page builder Pro.
- Không dùng để dựng theme mới từ đầu. Dùng `wp-theme-build`.
- Không dùng khi plugin trả phí còn licence và còn cập nhật. Giữ plugin đó.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Danh sách plugin và theme đang bật, version | `wp plugin list`, `wp theme list` qua SSH | dừng |
| Staging khớp production | skill `wp-staging-deploy` | làm mới staging trước |
| Danh sách trang public cần giữ giao diện | sitemap + kết quả kiểm kê | lập danh sách trước |
| Người duyệt tắt plugin trên production | người vận hành | không tắt trên production |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code (5 script) | kiểm kê, đổi widget, xuất bản đồ URL, phân giải URL | dùng: lượt thử 19/10 tái tạo đúng 18 lượt đổi widget ngày 18/10 và khớp 185/185 URL của Permalink Manager |
| Claude | đọc kiểm kê, chọn cách thay từng phần, viết CSS cho widget mới, đọc ảnh so trước và sau | dùng |
| Jev `ui-visual` | gắn nhãn lỗi giao diện sau khi tắt plugin | qua `web-qa-gate`, chỉ xếp ảnh cho Claude đọc |
| EmbeddingGemma | không dùng | không có việc đo độ giống |

## Cách thay từng plugin

### Elementor Pro → Elementor free

1. Chạy `el_inventory.php`. Ghi các phần Pro mà tài liệu publish đang dùng.
2. Thay phần Pro bằng code trong theme hoặc mu-plugin (mẫu `assets/elementor-free-compat.php`):
   - Header và footer Theme Builder: in mẫu đang gắn điều kiện toàn site, hoặc viết lại bằng PHP trong theme.
   - `[elementor-template id]`: đăng ký lại bằng `get_builder_content_for_display` của bản free.
   - Ô Custom CSS cấp widget và trang: thêm lại ô ở tab Nâng cao, in CSS giống Pro.
   - Popup: dựng `<dialog>` trong theme, đổi link của nút sang `#<id>`.
   - Widget posts, nav-menu, progress-tracker: shortcode của theme. Carousel testimonial, media, slides: HTML + CSS scroll-snap.
3. Chạy `el_free_convert.php` với `IDS=<danh sách>` và `PREFIX=<tiền tố theme>` ở `DRY=1`. Đọc log rồi chạy `DRY=0 BK=<thư mục>`.
4. Code thay thế chỉ chạy khi Pro tắt. Bật lại Pro là quay về trạng thái cũ.
5. So trước và sau bằng render-diff như mục ACF → SCF bước 5: 2 lượt chụp khi Pro còn bật, 1 lượt sau khi tắt, đủ URL sitemap. Header, footer, popup và widget thay thế phải ra cùng chữ, link và ảnh.

### ACF Pro → Secure Custom Fields (SCF)

1. Chạy `acf_inventory.php`. Ghi loại trường Pro (repeater, flexible content, gallery, clone), trang Options và block ACF.
2. Cài SCF từ WordPress.org trên staging. SCF đọc cùng nhóm trường và cùng dữ liệu trong `postmeta` và `options`.
3. Tắt ACF Pro, bật SCF. Kiểm từng nhóm trường trong wp-admin và kiểm trang có dữ liệu của nhóm đó.
   - Bẫy: SCF lọc HTML trong `the_field()` và `the_sub_field()`. Mã GTM, `<script>`, `<noscript>` in từ trường (thường ở trang Options) mất thẻ, và mã JS hiện thành chữ. Ví dụ site mẫu 23/10: 87/102 URL hỏng, GTM không chạy.
   - Sửa: thêm mu-plugin 1 dòng `add_filter( 'acf/the_field/allow_unsafe_html', '__return_true' );`. Chỉ dùng khi chỉ admin sửa được các trường đó. ACF Pro 6.0.5 không có bộ lọc này, nên file không đổi gì trước khi chuyển. Không gỡ file khi SCF còn bật.
   - Kiểm: so HTML staging lượt ACF với lượt SCF, đếm riêng số thẻ `<script>` và mã GTM mỗi URL. Mọi URL phải trùng (site mẫu: 102/102) trước khi lên production.
4. Nếu site chỉ cần đọc vài meta, đăng ký meta bằng `register_post_meta` trong mu-plugin và bỏ hẳn ACF.
5. Trên production, so 3 lớp trước và sau khi chuyển. Lượt chạy thật ngày 24/10/2026 trên site agency mẫu dùng đúng 3 lớp này:
   - **Render-diff**: chụp HTML bỏ cache của mọi URL trong sitemap, từ 350 URL trở lên: `scripts/render_snap.py --base https://<domain> --sitemap > urls.txt`, rồi `render_snap.py --base https://<domain> urls.txt <thư mục>` cho mỗi lượt. Script bỏ cache bằng cookie `_lscache_vary` ngẫu nhiên. Không dùng `?nc=` trên site có CSS gọn theo URL, vì tham số query sinh file CSS mới. So bằng `scripts/render_diff.py <trước1,trước2> <sau> --host <domain>`: mã thoát 1 khi có URL khác thật hoặc khác mã HTTP. Chụp 2 lượt trước để thấy phần đổi ngẫu nhiên, 1 lượt sau. Giữ giới hạn tải của host (site mẫu: 1 request/giây, 2 luồng, khoảng 6 phút cho 352 URL). Chuẩn hoá trước khi so: bỏ container honeypot của WPForms (nhãn 3 chữ ngẫu nhiên, container có `position:absolute`). Nếu không bỏ, 11/352 URL báo khác dù không có gì đổi. Các ô form khác vẫn so.
   - **Dữ liệu**: md5 kết quả `get_fields()` của từng đối tượng (post, term, options) trước và sau: `OUT=<file> wp eval-file scripts/acf_fields_sig.php`. Site mẫu: 376 đối tượng, lệch 0.
   - **Admin**: mở các màn có repeater, gallery, trang Options. Đếm số trường, hàng repeater, ảnh gallery và ô. Không bấm lưu.
6. SCF ghi `acf_version` mới (site mẫu: 6.0.5 → 6.9.6), có thể ngay khi màn admin mở. ACF Pro bản cũ không chạy upgrade khi số trong DB cao hơn. Vì vậy lệnh rollback phải đưa `acf_version` về số cũ trước khi bật lại ACF Pro.
7. Theo dõi ít nhất 20 phút sau khi chuyển: 5xx, fatal, warning mới, "max children", URL đang `hit` vẫn `hit`. Không purge toàn site. Chỉ purge theo URL các trang mẫu rồi làm nóng.

### Permalink Manager Pro → bản đồ URL

1. Khi plugin còn bật, chạy `pm_export.php`. Kết quả phải có `mismatch` rỗng và `dupes` rỗng.
2. Ghi khoá `map` vào `wp-content/mu-plugins/permalink-uris.json`. Chép `permalink-uris.php` vào `mu-plugins/`.
3. Tắt Permalink Manager trên staging. mu-plugin chỉ chạy khi plugin tắt.
4. Kiểm mã HTTP mọi URL trong bản đồ và URL gốc của WordPress bằng `parity.py status` của `wp-theme-build`. URL trong bản đồ trả 200. URL gốc trả 301 về URI trong bản đồ.
5. Site dùng WPML dạng thư mục: `pm_export.php` thêm tiền tố ngôn ngữ vào URI. mu-plugin in link bằng option `home` thô để WPML không thêm tiền tố lần nữa.

### Flatsome và theme trả phí khác → theme riêng

Dùng `wp-theme-build`. Shortcode UX Builder còn trong nội dung cần một lớp tương thích trong mu-plugin core: in markup thay thế và xoá thẻ còn sót.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'ssh,wp-cli,python3'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu thiếu `ssh` hoặc `wp-cli`, dừng skill. Script kiểm kê cần chạy trên server.

### Bước 1 — kiểm kê

1. Chạy script kiểm kê của plugin cần bỏ trên production. Script chỉ đọc.
2. Lập bảng: phần của plugin, nơi dùng, hậu quả nếu tắt mà không thay.
3. Tách trang private, nháp, template không gắn trang ra khỏi đợt. Ghi lý do.

### Bước 2 — thay trên staging

1. Làm mới staging bằng `wp-staging-deploy`.
2. Chụp ảnh "trước" và danh sách mã HTTP trên staging.
3. Thay từng phần theo mục "Cách thay từng plugin".
4. Tắt plugin trên staging. Sinh lại CSS Elementor từng tài liệu. Purge.
5. Chụp ảnh "sau". Chạy `parity.py` của `wp-theme-build` và `web-qa-gate`.

### Bước 3 — áp production

1. Trình bảng so trước và sau cho người duyệt.
2. Khi người duyệt đồng ý: backup theme, mu-plugin, bảng `options` và `postmeta`.
3. Deploy code bằng `wp-staging-deploy`, chạy script đổi dữ liệu, tắt plugin, sinh lại CSS, purge.
4. Chạy `web-qa-gate` trên production.

### Bước 4 — 7 ngày sau

1. Giữ plugin ở trạng thái tắt 7 ngày. Theo dõi log 404, log PHP và form.
2. Sau 7 ngày, hỏi người duyệt trước khi gỡ hẳn plugin. Chuyển thư mục plugin vào quarantine, không xoá.

Rollback: bật lại plugin, rồi trả theme và 2 bảng từ backup. Dữ liệu của plugin vẫn nằm trong DB.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] Bảng kiểm kê ghi mọi phần của plugin mà trang publish đang dùng.
- [ ] Code thay thế chỉ chạy khi plugin tắt.
- [ ] Script đổi dữ liệu đã chạy `DRY=1` và có thư mục backup trước khi ghi.
- [ ] `pm_export.php` báo 0 lệch, 0 trùng trước khi tắt Permalink Manager.
- [ ] Ảnh, chữ và mã HTTP trước và sau đã so bằng `parity.py`.
- [ ] Có cách rollback và mốc 7 ngày.
- [ ] ACF → SCF: render-diff đủ sitemap có chuẩn hoá honeypot, số thẻ `<script>` và mã GTM trùng lượt ACF, md5 `get_fields()` theo đối tượng, đếm ô trong admin, và rollback đưa `acf_version` về số cũ. Nguồn lỗi: staging 23/10 thiếu mu-plugin làm 87/102 URL mất GTM; lượt production 24/10, báo cáo ghi sai `acf_version` vẫn là 6.0.5 trong khi DB đã là 6.9.6.

## Output

- Bảng kiểm kê (JSON + bảng tóm tắt).
- Log của script đổi dữ liệu và thư mục backup.
- Bảng so trước và sau, report `web-qa-gate`.

## Gate

- Không tắt plugin trên production khi chưa có người duyệt.
- Không ghi dữ liệu khi chưa chạy `DRY=1` và chưa có backup.
- Không gỡ hẳn plugin trước 7 ngày và khi chưa hỏi người duyệt.
- Không cài plugin trả phí khác để thay. Ưu tiên bản free trên WordPress.org hoặc code tự viết.

## Anti-patterns

- Tắt plugin Pro rồi mới kiểm trang nào hỏng.
- Xoá dữ liệu của plugin cũ trong DB khi đổi sang bản free.
- In link bằng `home_url()` trên site WPML. Link sẽ lặp tiền tố ngôn ngữ.

## Changelog

- v1.3 (2026-10-27): đóng gói render-diff thành script dùng cho mọi lượt gỡ plugin: `render_snap.py` (lấy URL từ sitemap, chụp HTML bỏ cache bằng cookie), `render_diff.py` (chuẩn hoá nonce, giờ, honeypot WPForms; tách khác thật khỏi nhiễu giữa 2 lượt trước), `acf_fields_sig.php` (md5 `get_fields()`), test 4 ca. Mục Elementor Pro thêm bước so bằng render-diff. Chạy thật 27/10/2026 trên site agency mẫu: 5 URL, 3 lượt đều `miss`, 0 khác thật.
- v1.2 (2026-10-25): sec-12. ACF → SCF bước 3 thêm bẫy SCF lọc `<script>` trong `the_field()`, mu-plugin `allow_unsafe_html`, phép đếm `<script>` và GTM. Nguồn: render-diff staging gtvseo.com 23/10 (thiếu mu-plugin 87/102 URL lệch, có mu-plugin 0).
- v1.1 (2026-10-24): mục ACF → SCF thêm bước 5–7 từ lượt production đã chạy thật trên gtvseo.com 24/10 08:13: render-diff 352 URL có chuẩn hoá honeypot WPForms (lệch 0), md5 `get_fields()` 376 đối tượng (lệch 0), đếm ô admin, `acf_version` đổi sau khi mở admin, theo dõi 20 phút. Thêm 1 mục tự phản biện. Nguồn: `Deliverables/GTV-Brand/GTV-Website/security-2026-10/acf-scf-2310/prod/bao-cao.md`, `kiem-doc-lap.md`.
- v1.0 (2026-10-19): bản đầu. Gom script bỏ Elementor Pro (18/10) và bản thay Permalink Manager của 2 site nội bộ. Thêm `acf_inventory.php`, `pm_export.php` (xử lý tiền tố WPML), `permalink-uris.php`. Lượt thử 19/10, chỉ đọc: converter chạy lại trên bản backup 18/10 cho đúng 18 lượt đổi và cùng md5 nguồn; `pm_export.php` khớp 185/185 URL đang chạy.
