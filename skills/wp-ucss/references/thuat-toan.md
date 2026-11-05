# Thuật toán sinh, safelist và kiểm của wp-ucss

Đọc file này ở Bước 3–5 của SKILL.md, hoặc khi sửa `model.mjs`, `gen.mjs`, `build.mjs`, `verify.mjs`. Nguồn: đọc mã 11 repo mã nguồn mở về cắt CSS (PurgeCSS, minimalcss, uncss, dropcss, Jetpack Boost critical CSS gen, Beasties, critical, Debloat, LiteSpeed Cache 7.9.1, BackstopJS, Playwright, reg-suit), ngày 26/10/2026, rồi chạy thật trên một site WordPress (OpenLiteSpeed + LiteSpeed Cache, 66 path × 4 biến thể) ngày 26–27/10/2026.

Không chép mã GPL (Jetpack Boost, Debloat, LiteSpeed) vào script hay mu-plugin. Chỉ lấy ý.

## 1. Nguyên tắc

1. Khớp selector bằng engine của Chrome (`querySelector`). Không dùng token, cheerio, jsdom hay engine tự viết.
2. Chuẩn hoá selector bằng parser, chỉ nới tập khớp. Selector lỗi thì giữ rule (fail open).
3. Gom URL theo md5 của file CSS gộp. Tên file gộp của LiteSpeed đã là md5 nội dung. Cộng dồn selector đã khớp qua mọi URL, mọi biến thể và mọi trạng thái giao diện của nhóm đó.
4. Lọc tại chỗ: xoá node khỏi cây gốc, giữ thứ tự và văn bản gốc, không minify lại, không đánh giá điều kiện at-rule.
5. Giữ hết `@font-face`, `@keyframes` và custom property ở bản đầu.
6. Kiểm bằng computed style và hộp phần tử. Ngưỡng lệch là 0 phần tử.
7. Mu-plugin chỉ đổi `href` khi map có đúng cặp (md5 file gộp, path đã kiểm). File gộp đổi md5 (sửa theme, plugin) thì trang tự dùng file gốc tới lần tái tạo sau.

## 2. Bộ sinh (`gen.mjs`, `model.mjs`, `build.mjs`)

- Parse mỗi file gộp một lần bằng PostCSS. Trước khi parse, `fixCss` sửa 2 lỗi đã gặp:
  - Khoảng trắng U+00A0 nằm giữa khai báo. Chrome coi U+00A0 là một phần của tên, nên khai báo đó vô hiệu. PostCSS coi là khoảng trắng và giữ khai báo, nên bản gọn khác bản gốc. `fixCss` đổi khoảng trắng thường cạnh U+00A0 thành U+00A0 để PostCSS cũng bỏ.
  - Dấu `}` thừa ở cấp ngoài cùng. Chrome bỏ qua dấu đó và vô hiệu rule kế tiếp. PostCSS báo `CssSyntaxError: Unexpected }`. `strayBrace` thay dấu thừa bằng ký tự làm rule kế tiếp vô hiệu như Chrome. Đã kiểm bằng CSSOM của Chrome.
- Nếu parse vẫn lỗi, không xuất bản gọn cho md5 đó.
- Truyền cả mảng selector vào một lần `page.evaluate`. Mỗi lần chụp chỉ thử selector chưa khớp.
- Chuẩn hoá selector bằng danh sách trắng pseudo cấu trúc (mục 4). Khớp 2 đường: selector đã chuẩn hoá và selector gốc. Một đường khớp là giữ.
- Phần tử có trong DOM ở bất kỳ trạng thái nào là "được dùng", kể cả `display:none`.
- Trạng thái chụp (`runStates` trong `lib-ucss.mjs`): tải xong; sau khi kích JS hoãn (chuột, chạm, phím); cuộn hết trang; lên đầu; menu mobile mở và menu con, hoặc hover 8 mục menu desktop; accordion, tab, `details`; nút next của slider; focus và blur ô form. Cuối cùng dựng lại nội dung `<noscript>` thành phần tử thật rồi thử lần nữa.
- Selector có token xuất hiện trong JS của trang (chuỗi trong file JS và script inline) được nới: thử lại với class đó coi như có mặt. Token kết thúc bằng `-` hoặc `_` là tiền tố.
- Giữ cả rule khi một selector trong danh sách khớp. Bản đầu không cắt selector chết khỏi danh sách.
- Đệ quy vào mọi at-rule có khối. Dọn khối rỗng từ trong ra ngoài, chỉ với `@media`, `@supports`, `@container`. Giữ `@layer` rỗng, `@import`, `@charset`, `@property`, `@page`. Bỏ qua rule bên trong `@keyframes`.
- `build.mjs` chạy hai lần phải cho cùng byte. Không ghi thời gian vào file gọn.
- Dấu hiệu bình thường của build (site mẫu 27/10): mỗi file gộp giữ 1.099–3.360 trên 6.901–9.885 rule; 959 KB → 259 KB raw, 110 KB → 26 KB brotli; 29/29 `@font-face`, 17–31/31 `@keyframes` giữ nguyên.

## 3. Safelist (`templates/safelist.example.json`)

- Mỗi mục có `p` (mẫu), `reason` (bắt buộc), `src` (nguồn). Chuỗi dạng `/.../` là regex.
- Khoá: `keep_selector`, `keep_class`, `exclude_selector`, `keyframes`, `font_families`, `files.<md5>` (chỉ áp cho một file gộp).
- Luôn giữ `*`, `:root`, `html`, `body`, `::before`, `::after` đứng riêng.
- Lớp WordPress, Elementor, Max Mega Menu, slick, lazyload LiteSpeed, WPForms: có sẵn trong file mẫu. Chỉ thêm mẫu của plugin khi tiền tố có trong ít nhất một file gộp.
- Đánh giá mọi mẫu, không dừng ở mẫu khớp đầu tiên.
- Không dán nguyên danh sách WordPress của PurgeCSS. Đo byte khi bật và tắt từng họ regex rộng (`^is-`, `^has-`).

## 4. Pseudo bỏ trước khi khớp

Dùng danh sách trắng: pseudo nằm ngoài nhóm "Giữ" thì bỏ.

- Giữ để Chrome đánh giá: `:root :empty :first-child :last-child :only-child :nth-child() :nth-last-child() :nth-of-type() :nth-last-of-type() :first-of-type :last-of-type :only-of-type :not() :is() :where() :has()`.
- Bỏ: mọi pseudo trạng thái (`:hover :focus :focus-visible :checked :disabled :placeholder-shown :valid :open :autofill`…) và mọi pseudo-element (`::*`, `:before`, `:after`, `:first-line`, `:first-letter`).
- Quy tắc:
  1. Pseudo trạng thái nằm trong `:not()`, `:is()`, `:where()`, `:has()`: bỏ cả cụm hàm. `a:not(:hover)` thành `a`.
  2. Không cắt bên trong cụm hàm chỉ chứa class hoặc pseudo cấu trúc.
  3. Selector rỗng sau khi bỏ thì dùng `*`.
  4. So tên pseudo theo token của parser, không phân biệt hoa thường.
- Selector có pseudo mà Chrome không đọc được (`CSS.supports('selector(…)')` trả false): ghi vào `model/<md5>.invalid.json`. Chrome bỏ rule đó trong bản gốc, nên bản gọn cũng bỏ.

## 5. Bộ kiểm (`verify.mjs`)

- Mỗi trạng thái chụp 3 lần trong cùng trang: A (CSS gốc), B (CSS gọn), A2 (CSS gốc lại). Đổi bằng `sheet.disabled`, không tải lại trang.
- Chỉ tính lệch khi A = A2 và B ≠ A. Cách này loại nhiễu do slider, animation, timer.
- Phần tử có class hoặc style đổi giữa A và A2 (JS đang chạy) ghi `unstable`, không tính lệch.
- Đóng băng animation bằng `document.getAnimations()`: hữu hạn thì `finish()`, vô hạn thì `cancel()`. Không chèn `animation:none`.
- Chờ `document.fonts.ready` sau khi đổi sheet. So cả danh sách font đã nạp: font có ở A và A2 mà mất ở B là lỗi `lostFonts`.
- So `document.scrollHeight` riêng (`hDiff`).
- Lượt xác nhận: nếu lượt 1 có lệch, chạy lượt 2 trên trang mới. Chỉ giữ khoá lệch (`phần tử|pseudo|thuộc tính`) có ở cả hai lượt, đánh dấu `transient` cho phần còn lại. Nguồn: site mẫu 26/10, 3 lệch giả của lượt 1 (margin `auto` của flex item đọc ra `0px` ở một lượt; số đếm của khối thống kê đang chạy).
- Lệch còn lại: chụp ảnh vùng phần tử ở A và B (`shots/<tên>_<i>_a.png`, `_b.png`), rồi đọc bằng mắt hoặc Jev (mục 6).
- Debug một phần tử: `dbg_el.mjs` in quy tắc khớp của phần tử ở bản gốc và bản gọn (CDP `CSS.getMatchedStylesForNode`).
- Không thêm class vào DOM khi đo. Dùng thứ tự phần tử.
- Mỗi cặp (path, biến thể) một file `verify/<v>_<slug>.json`. Số file phải bằng số cặp đã sinh.
- Giới hạn: `verify.mjs` khởi tạo JS của trang dưới CSS gộp rồi mới đổi sheet. Lỗi xảy ra khi JS đo phần tử lúc khởi tạo không hiện ra ở bước so.
- `verify_init.mjs` phủ giới hạn này. Script tải HTML một lần, nạp trang hai lượt bằng đúng HTML đó: lượt đầu trả CSS gộp, lượt sau trả CSS gọn (qua request interception, không ghi server). Mỗi lượt có chuột, Shift, chạm (mobile), cuộn hết trang. Script so chiều cao trang và chiều cao từng widget trong `init_widgets`. Lệch quá `INIT_TOL` px (mặc định 2) là LỆCH.
- Site agency mẫu 27/10/2026: 17/95 path trong map có carousel (Owl, slick, Swiper, Elementor). Chạy `verify_init.mjs` cho mọi path có widget, không chỉ path đang nghi.

### Dữ liệu và ngẫu nhiên trong bộ kiểm

- Đọc log request bị chặn trước khi nhận kết quả. Carousel lấy dữ liệu bằng GET JSON phải có dữ liệu trong cả hai nhánh. Cho phép đúng asset công khai hoặc dùng cùng snapshot; không mở mọi request.
- Khai báo selector widget thật trong `init_widgets`. Kiểm số item lớn hơn 0 khi trang phải có item. Hai mảng widget rỗng bằng nhau không chứng minh carousel đạt.
- Nếu A/A (CSS gốc so với chính nó) cũng lệch, truy nguyên yếu tố không cố định trước. Không nới `INIT_TOL` để bỏ qua.
- Nếu code dùng `Math.random()` đổi vị trí field, có thể cố định cùng PRNG seed trước khi khởi tạo hai nhánh thử. Giữ thay đổi trong fixture, ghi cách làm và kiểm thứ tự field; không sửa sản phẩm.
- Ca thực tế 05/11/2026: bộ kiểm chặn JSON danh sách logo; WPForms chọn ngẫu nhiên vị trí honeypot làm chiều cao form lệch 18 px cả A/A. Bằng chứng này giải thích lỗi bộ thử, chưa thay thế lượt A/B đạt với dữ liệu và điều kiện đã cố định.

## 6. Jev cho lệch còn lại

- `jev_ucss.py prep <outDir>` so pixel 2 ảnh, ghép ảnh cạnh nhau có vạch phân cách, ghi `items.jsonl`. `read` đọc `visible_change.p_yes` và `change_kind`.
- Rubric `ucss-diff` chưa hiệu chuẩn. Chỉ dùng để xếp thứ tự cho người đọc, không dùng làm cổng. Trước khi dùng làm cổng: lập gold gán mù từ một lượt negative test (bỏ cố ý một rule rồi chạy verify), rồi hiệu chuẩn bằng skill `model-calibration`.
- Chạy `jev_ucss.py` bằng `python3` không có `-I`, vì script cần Pillow cài ở site-packages của người dùng.

## 7. Bẫy đã gặp

1. File gộp có U+00A0 hoặc `}` thừa: bản gọn khác bản gốc, hoặc build dừng (mục 2). Test: `scripts/tests/test_model.mjs`.
2. Đo một lượt: 3/132 cặp báo lệch giả. Lượt xác nhận loại cả 3.
3. Bản gọn dựng cho bản WebP không áp cho bản `Accept: */*` (bản Googlebot) khi bản này dùng file gộp khác. CDN không tách HTML theo Accept có thể đưa bản không có CSS gọn cho mọi khách (`giao-cdn-tai-tao.md` §3).
4. Pseudo cấu trúc đổi kết quả khi JS chèn phần tử (slider nhân bản slide). Cộng dồn trạng thái và đường khớp thứ hai giảm rủi ro.
5. Job tái tạo chỉ sinh lại khi md5 file gộp đổi. Sửa nội dung bài (class mới) hoặc đổi thẻ HTML (theme hay mu-plugin đổi `div` thành `section`, `b` thành `strong`) không đổi md5, nên job không chạy lại.
   - Selector theo thẻ mới (`section.x`) bắt đầu khớp ở CSS gộp nhưng có thể thiếu ở CSS gọn. Site agency mẫu 27/10/2026: sau khi đổi container sang `section`, file gọn của 9 path thiếu 17–27 selector có `section`, `header` hoặc `figure`.
   - Sau mỗi đợt đổi DOM: quét selector chứa thẻ mới trong file gộp, đối chiếu file gọn, rồi chạy `FORCE=1 DRY=1 regen.sh` và đọc kết quả kiểm. Site mẫu: lượt `FORCE=1` DRY kiểm 388/388 cặp đạt sau khi safelist giữ thẻ `strong`, `em`, `main`, `article`, `aside`, `time`.
6. Purge CSS/JS của LiteSpeed xoá cả `wp-content/litespeed/css/` và đổi `?ver=`. Đọc file gộp ngay khi thấy md5 mới. Không dùng `?ver=` làm khoá.
7. Job đăng nhập hoặc mang cookie nhận file gộp khác trang khách. Job đi đường khách: không đăng nhập, xoá cookie giữa các URL.
8. `document.fonts.ready` resolve cả khi bản gọn mất `@font-face`. So danh sách font, không chỉ chờ.
9. Chrome coverage có lỗi. Không dùng coverage làm nguồn xoá rule.
10. CSS nesting và `@scope`: không repo nào xử lý tốt. Build in số `nestRules`, `scope` cho mỗi file gộp. Có `@scope` thì kiểm tay trước khi giao.
11. Class do JS thêm rồi gỡ trong vài mili giây không có trong DOM ở trạng thái nào mà `gen.mjs` chụp. Owl Carousel thêm `owl-loading`, kiểm phần tử có hiển thị, rồi đổi sang `owl-loaded`. CSS gọn thiếu `.owl-carousel.owl-loading` thì carousel còn `display:none` lúc đo, Owl bỏ bước tính bề rộng và item xếp lưới. Giữ bằng `keep_class` trong safelist (mẫu có sẵn). Site agency mẫu 27/10/2026: 8/72 file gọn thiếu rule, carousel cao 1.400–2.703 px thay vì 350–503 px. Sau khi sửa: 16/16 cặp `verify_init.mjs` khớp, 8/8 trang trên production trùng bản gộp.
12. Một nhóm bài có thể tách thành nhiều md5 file gộp vì thẻ `<style>` có điều kiện. Ví dụ: shortcode in vài rule trong `<style>` chỉ khi bài có bài liên quan, nên bài không có bài liên quan nhận md5 khác. md5 lẻ đó không có trong map và không có khoá `all`, nên bài tải file gộp. Cách tìm: đếm bài theo md5 trong inventory, so file gộp của md5 lẻ với md5 chính (site agency mẫu 27/10/2026: khác đúng 4 rule). Cách phủ: thêm một bài của md5 lẻ vào `chon.tsv` (site mẫu: kiểm 8/8 cặp đạt), hoặc dựng holdout riêng cho md5 đó (§8).
13. Inventory đọc bản cache đang có. Path vừa thêm vào bộ chọn có thể còn HTML dựng trước lần đổi CSS gộp gần nhất, nên map khoá theo md5 cũ. Purge của lượt giao làm trang dựng lại với md5 mới, map không khớp, trang dùng file gộp. Purge và làm nóng path mới trước khi chạy inventory. Site agency mẫu 27/10/2026: 11/12 URL vẫn tải file gộp sau lượt giao đầu.
14. Bài có iframe YouTube `src` trực tiếp (không `loading=lazy`): CSS gọn làm parser tới iframe sớm hơn, script YouTube chen trước FCP. Site agency mẫu 27/10/2026: một bài điểm mobile 93 → 56, FCP 2,13 → 6,62 s ở 3/3 lượt PSI. Mu-plugin mẫu bỏ qua nhánh `all` cho bài có iframe như vậy; bài đó giữ file gộp. Lazy iframe rồi đưa bài vào nhóm: chưa thử.

## 8. Khoá `all`: phủ cả nhóm bài theo md5 file gộp

- Bài viết cùng template thường dùng chung một md5 file gộp. Khoá `all` cho phép mọi bài viết dùng file gọn của md5 đó mà không cần path trong map.
- Mu-plugin (`templates/ucss-swap.php`) chỉ áp `all` cho trang `is_singular()`, không phải page, không phải attachment, không có iframe YouTube tải ngay. Map không có `all` thì mu-plugin chạy như cũ.
- `make_map.py` chỉ ghi `all` cho md5 H khi đủ 4 điều kiện:
  1. Mọi path đã chọn của H đạt kiểm.
  2. Thư mục holdout (`HOLDOUT`, mặc định `<outDir>-ho`) có ít nhất `HOLDOUT_MIN` bài (mặc định 10), mọi lượt đạt kiểm.
  3. Bài holdout nằm ngoài tập dựng.
  4. `reduced/<H>.css` của holdout trùng từng byte với file gọn của tập dựng.
- Dựng holdout:
  1. Chọn bài theo loại khối (mục lục, bảng, video, iframe, code, cột, trích dẫn, mỗi loại bài tuỳ chỉnh), thêm `?nc=<số mới>` để có bản dựng mới với md5 hiện hành.
  2. Chạy `gen.mjs` cho holdout vào `<outDir>-ho`. Chép `<outDir>/reduced/<H>.css` vào `<outDir>-ho/reduced/`.
  3. Chạy `verify.mjs` cho holdout. Chạy lại `make_map.py`.
- Regen giữ `all` khi md5 và file gọn không đổi. File gọn đổi thì `make_map.py` bỏ `all`, `map_diff.py` in CẢNH BÁO; chạy lại holdout cho file mới.
- Site agency mẫu 27/10/2026: holdout 12 bài × 4 biến thể = 48/48 cặp lệch 0. Sau khi giao: 30 bài mẫu × 5 biến thể tải CSS gọn, 230/231 bài nhóm tải CSS gọn khi cache đã dựng lại, 5xx 0 trên 15.066 request.

## 9. Đã thử, không mở rộng

- Nhúng CSS gọn vào HTML cho bản Googlebot (Accept không có WebP). Cơ chế: danh sách path và file cờ bật; CDN không tách HTML theo Accept nên phải làm nóng bằng header Googlebot.
- Kết quả site agency mẫu 27/10/2026 (10 path): HTML bản Googlebot tăng trung bình 52 KB gzip (+74%). Log origin 05:30–09:41: Googlebot tải 402 HTML nhưng chỉ 3 file CSS, vì Google giữ CSS trong bộ nhớ đệm. PSI gửi Accept có WebP nên luôn nhận bản link, không đo được lợi ích bằng PSI.
- Trước khi bật cho site khác: đọc log Googlebot, đếm lượt tải CSS so với lượt tải HTML. Lượt tải CSS ít thì không bật.
