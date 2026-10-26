# Tiêu chí hạng mục 13–15 của web-qa-gate

File này ghi cách script chấm hạng mục 13 (tương tác và trạng thái), 14 (toàn vẹn bố cục) và 15 (Open Graph), cùng bẫy đã gặp. Đọc file ở Bước 1 khi khai khối `interact`, và ở Bước 3 khi đọc `report.md`. Trạng thái PASS, FAIL, WARN, SKIP có nghĩa như `hang-muc.md`.

## Bật hạng mục 13 và 14

- Chép khối `interact` từ `scripts/qa.interact.example.json` vào `qa.json` của site. Không có khối này thì hạng mục 13 và 14 SKIP.
- Selector, màu kit, heading có số và cặp ngôn ngữ là cấu hình của từng site. Bản master không giữ giá trị của site nào. Đặt số riêng của site trong `qa.json` ở thư mục evidence của dự án.
- `run` tự gọi `interact_probe.mjs` (13a–13d, 14a–14d) và `landmarks.mjs` (14e). Hai script ghi `raw/interact.jsonl` và `raw/landmarks.jsonl`.
- Script chỉ bấm nút giao diện: nút mở menu và mũi tên slider. Script không điền form, không bấm link sang trang khác.
- Tracking bị chặn từ đầu phiên. Mỗi bề rộng dùng viewport thật, UA Chrome thường và một lần tải mới, như hạng mục 1.

Chạy riêng một nhóm đo trên job đã dựng (không gọi lại `run`):

```bash
node skills/web-qa-gate/scripts/interact_probe.mjs --job <out>/raw/interact_job.json --out <ev>/i.jsonl --only menu,slider
node skills/web-qa-gate/scripts/landmarks.mjs --url https://stg.example.vn/ --out <ev>/l.jsonl --widths 390,1366
python3 -E skills/web-qa-gate/scripts/qa_gate.py check interact <ev>/i.jsonl --config <ev>/qa.json
python3 -E skills/web-qa-gate/scripts/qa_gate.py check layout <ev>/i.jsonl --landmarks <ev>/l.jsonl
```

## 13. Tương tác và trạng thái

| Mục | Bề rộng mặc định | Cách đo | FAIL | WARN |
|---|---|---|---|---|
| 13a Menu mobile | 390 | Tìm nút theo `menu_toggle.selector`. Không khai thì tìm `button[aria-controls]`, `[aria-expanded]`, `.mega-menu-toggle`, `.menu-toggle`, `.navbar-toggler`, nút burger trong header. Bấm thật. Đếm link nhìn thấy trước và sau. Chụp lúc đóng và lúc mở. | Nút đã khai không hiện. Nút có kích thước mà vạch và chữ trong suốt, rỗng hoặc cùng màu nền. Bấm xong số link nhìn thấy không tăng. | Không thấy nút. Site không có menu mobile thì bỏ qua dòng này. |
| 13b Slider | 360, 390 | Cuộn tới `sliders[].selector`. Gọi `elementFromPoint` ở tâm và 4 mép mũi tên next. Chạm thật. So tập thẻ nhìn thấy trong viewport (thẻ hiện ít nhất 50% bề rộng) trước và sau. | Phần tử khác che mũi tên. Chạm xong tập thẻ nhìn thấy không đổi. | Không thấy slider, mũi tên hoặc thẻ. Khai `next`, `items` khi theme dùng selector khác. |
| 13c Trạng thái | 1366 | Với `changed_selectors`, ép `:hover`, `:focus`, `:active`, `:visited` bằng `CSS.forcePseudoState`. Đọc màu bằng `CSS.getComputedStyleForNode`. | Tương phản chữ và nền dưới 4,5:1 (chữ lớn dưới 3:1, hoặc dưới `min_contrast` đã khai). `:focus` không đổi kiểu hiển thị. | `:hover`, `:active` hoặc `:visited` không đổi kiểu hiển thị. Selector không khớp phần tử nào. |
| 13d Màu nút theo kit | 390, 1366 | So nền của CTA (`kit_button_colors.selectors`) với `colors`, sai số `tolerance`. Đọc nền của phần tử không phải CTA: `button`, `[role=button]`, mũi tên slider, accordion, tab (đổi danh sách bằng `non_cta`). | CTA không dùng màu kit. | Phần tử không phải CTA mang nền màu kit. |

Giới hạn: script chạm bằng Chrome qua `Input.dispatchTouchEvent`, không dùng WebKit. Nếu lỗi chỉ hiện trên Safari iOS, kiểm trên máy thật và ghi giới hạn này vào báo cáo.

Script chưa đo icon font. Nếu icon hiện thành ô vuông hoặc chữ thay icon, chạy `skills/wp-pagespeed/scripts/fontmap.mjs` để xem font Chrome thật sự vẽ cho từng vùng.

Bẫy:

- Không kiểm slider bằng class trạng thái của thư viện (`slick-current`, `swiper-slide-active`). Class có thể đổi trong khi track đứng yên. Site agency mẫu 22/10: vòng kiểm đầu đọc `slick-current` nên báo đạt, nút slide trên mobile vẫn bấm không được. Lỗi này tốn 268 phút và 823k token.
- CSS bổ sung trong Customizer có thể khoá slider bằng `!important` toàn cục trên `transform`. Chỉ phép chạm thật mới thấy lỗi này.
- Ô màu để trống trong cài đặt Max Mega Menu sinh `background-color: ;`, nên nút menu thành trong suốt. Site agency mẫu 18/10: hamburger vô hình trên production và staging nhiều ngày, qua nhiều vòng QA.
- Rule nút của kit Elementor tô mọi `<button>` mới. Site agency mẫu 18/10: màu nút kit hiện ở accordion, ở mũi tên slick trên 3 trang và ở facade video. Mỗi chỗ cần một lượt sửa riêng.
- `getComputedStyle` trong trang luôn trả màu của link chưa thăm, vì luật riêng tư của trình duyệt. Script đọc màu `:visited` qua CDP. Site agency mẫu 18/10: link ở trạng thái visited cộng hover có chữ trắng trên nền trắng.
- Rule đổi font dạng `body :is(h1,h2,h3,h4,h5,h6) *` đè cả font icon trong heading. Site agency mẫu 18/10: icon FAQ mất Font Awesome sau một lần đổi font.

## 14. Toàn vẹn bố cục

| Mục | Bề rộng mặc định | Cách đo | FAIL | WARN |
|---|---|---|---|---|
| 14a Lưới | 390, 1366 | Lấy lưới `grid` hoặc `flex-wrap` có từ 3 con, mỗi con từ 80×80 px, ngoài header, footer, nav. Khai `grids.selectors` để chỉ đo lưới đã chọn. Đếm ô mỗi hàng. | (không có) | Ô trống (không chữ, ảnh, nút, nền ảnh). Hàng giữa thiếu ô. Hàng cuối thiếu ô. |
| 14b Số trong heading | 390, 1366 | Chỉ chạy khi site khai `count_claims` (heading, selector thẻ, regex số). | Số trong heading khác số thẻ nhìn thấy. | Không thấy heading. Heading không có số. |
| 14c CTA trùng link | 390, 1366 | Gom CTA (`cta_selectors` hoặc mặc định `a.elementor-button`, `a.btn`, `a.button`) theo section. | (không có) | Từ 2 CTA trong một section trỏ cùng href. Cùng nhãn thường là bản lặp desktop và mobile. |
| 14d Cặp VI/EN | 1366 | Với `pairs` (đường dẫn VI, đường dẫn EN), so số h1, h2, h3, form, số thẻ trong lưới, số section, nút, ảnh, đoạn. | Một trong hai trang không trả 200. | Lệch h1, h2, h3, form hoặc số thẻ lưới. Lệch section, nút, ảnh, đoạn quá 1 và quá 10%. |
| 14e Landmark | 390, 1366 | `landmarks.mjs` đếm trên DOM đã render: main, banner, contentinfo, nav, h1 trong main, menu chính, skip link. Khai `landmarks.menu_selector` khi menu không nằm ở chỗ quen. | Số `main` khác 1. Số h1 nhìn thấy khác 1. Menu chính (từ 3 link) không nằm trong `nav` hay `role=navigation`. Trang không trả 200. | h1 nằm ngoài main. Thiếu banner hoặc contentinfo, hoặc có nhiều hơn 1. Nhiều vùng nav thiếu tên hoặc trùng tên. Không có skip link. Không tìm thấy menu chính. |

Mức WARN ở 14a, 14c, 14d theo đặc tả đã duyệt 24/10: các phép này dễ báo giả, ví dụ cột đệm rỗng của Elementor hay lưới masonry có ô đầu rộng gấp đôi. Claude xem ảnh của từng dòng WARN rồi kết luận.

Bẫy:

- Đếm landmark trên DOM đã render, không đếm bằng regex trên HTML thô. Plugin menu có thể dựng menu bằng `<div>` trong widget, nên HTML server và DOM có thể khác nhau về `nav`, `main`, `header`. Report ghi "menu nằm trong widget_text" khi gặp dạng này.
- Lưới thiếu ô thường xuất hiện sau khi ghi nội dung (thêm hoặc bớt thẻ). Site agency mẫu 20/10: lượt kiểm độc lập bắt lưới 3+2 có ô trống ở 1366 px, phụ đề ghi "6 giải pháp" khi trang có 5 thẻ, và 2 nút cùng trỏ một trang. Lane đã tự báo đạt trước đó.
- Heading có số là quyết định nội dung của từng site. Chỉ khai `count_claims` cho heading thật sự đếm thẻ bên dưới.

## 15. Open Graph

Script đọc thẻ meta từ HTML server của mọi trang trả 200. Script tải mỗi `og:image` một lần (tối đa 12 MB) để đọc mã HTTP, loại nội dung, cỡ ảnh và dung lượng.

| FAIL | WARN |
|---|---|
| Thiếu `og:image`, hoặc thiếu cả `og:image` lẫn `twitter:image` | Thiếu `og:title`, `og:description`, `og:url`, `og:type` |
| `og:image` là đường dẫn tương đối | `og:image` là WebP hoặc AVIF (JPEG, PNG an toàn nhất) |
| `og:image` là SVG (Facebook và X không hiển thị) | `og:image` trỏ host khác canonical, hoặc dùng http trên trang https |
| Ảnh trả mã khác 200 | Ảnh rộng dưới `og.min_width` (mặc định 1200 px), hoặc tỉ lệ ngoài 1,6–2,0 |
| URL ảnh không trả loại nội dung ảnh | `og:image:width` hoặc `og:image:height` khác cỡ ảnh thật |
| | Ảnh nặng hơn 5 MB. Thiếu `twitter:card`. Thiếu `twitter:image`. `og:url` khác canonical. |

Bẫy:

- Mô tả chia sẻ có thể lấy nhầm chữ nháp trong trang. Site khoá học mẫu 19/10: `og:description` của trang liên hệ là một ghi chú nội bộ. Đọc chữ của `og:title` và `og:description` trên mọi trang mới.
- Khi chạy trong workspace của Vincent: đọc `skills/featured-image-seo/references/og-trang.md` mục 8 cho `og:image`, `og:image:type` (phải là `image/jpeg`) và bước Scrape Again của Facebook (người có tài khoản làm, agent ghi danh sách URL vào HANDOFF). Luật chấm ở bảng trên vẫn là nội dung kiểm cốt lõi và không phụ thuộc file đó.
- Kiểm OG trên production sau deploy. Staging thường chặn bot và có thể trả ảnh qua Basic Auth, nên nền tảng chia sẻ không tải được.
