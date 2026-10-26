# Tiêu chí hạng mục 1–12 của web-qa-gate

File này ghi cách script chấm từng hạng mục, cách đọc kết quả và bẫy đã gặp. Đọc file ở Bước 3, khi đọc `report.md`. Hạng mục 13 (tương tác), 14 (bố cục, landmark) và 15 (Open Graph) nằm ở `hang-muc-13-15.md`.

## Trạng thái

| Trạng thái | Nghĩa |
|---|---|
| PASS | Hạng mục đã chạy và không có lỗi. |
| FAIL | Có ít nhất một lỗi chặn. Sửa rồi chạy lại. |
| WARN | Có mục cần người xem, hoặc phép đo lỗi. Đọc từng dòng trước khi báo xong. |
| SKIP | Hạng mục không chạy vì thiếu input. Report ghi lý do. |

Kết luận chung: có FAIL thì `FAIL`. Không có FAIL mà có WARN thì `REVIEW`. Còn lại là `PASS`. SKIP không chặn kết luận, nhưng report liệt kê mọi hạng mục bị bỏ qua.

Model không tự đánh FAIL. Jev chỉ tạo dòng WARN để Claude xem ảnh.

## 1. Tràn ngang

- Script đo ở mọi bề rộng trong `widths`. Mặc định là 360, 768 và 1366 px.
- Bề rộng dưới 800 px dùng UA điện thoại, cảm ứng và tỉ lệ điểm ảnh gần 2. Script không bật cờ `mobile` của CDP (xem bẫy đầu tiên).
- Mỗi bề rộng là một lần tải trang mới, với UA Chrome thường.
- FAIL khi bề rộng tài liệu lớn hơn bề rộng đặt. Report ghi số px tràn và tối đa 4 phần tử thủ phạm (selector, mép phải).
- Phần tử nằm trong khối có `overflow-x: hidden|clip|auto|scroll` không tính là thủ phạm.
- Cờ `--cache` của `run` chọn bản đo:
  - `cached`: URL sạch. Script tải 2 lần khi lần đầu chưa hit cache.
  - `nc`: thêm `?nc=<chuỗi ngẫu nhiên>` để bỏ cache.
  - `both`: đo cả hai bản. Report ghi riêng dòng "Tràn chỉ ở bản cached" và "Tràn chỉ ở bản nc".
  - Không có cờ: script tải đúng URL đã cho, và report nhắc thêm `--cache both`.
- Mỗi dòng đo ghi header cache (`x-litespeed-cache`, `x-cache`, `cf-cache-status`). Axe, focus và ảnh chụp chỉ chạy ở bản đo đầu.

Bẫy:

- Không bật cờ `mobile` của CDP (`isMobile` của puppeteer) khi đo tràn. Cờ này nới `innerWidth` theo phần tràn: đặt 390 px thì JS đọc 421 px lúc load, đặt 768 px thì `innerWidth` thành 778 px. Hai hậu quả:
  - Phép so `scrollWidth` với `innerWidth` luôn ra 0. Site agency mẫu 20/10: một lane đo bằng `isMobile` (`innerWidth` thành 481) và báo "không tràn ở 390 px". Kiểm độc lập đo lại ở viewport thật và thấy tràn 90 px.
  - JS đọc `innerWidth` (slider, menu) dựng theo sai mốc, nên báo thủ phạm giả hoặc bỏ sót thủ phạm thật.
- Script so với bề rộng đặt (`vw`). Bản `ux_probe.mjs` cũ ghi `W = innerWidth` nên che lỗi 768 px. Đọc lại file cũ bằng `check overflow <file> --widths <danh sách đã đo>`.
- Script tự viết phải đặt UA Chrome thường. UA mặc định của Chrome headless chứa `HeadlessChrome`, và slick không khởi tạo với UA này, nên mũi tên slider biến mất khỏi phép đo. Site agency mẫu 21/10: UA mặc định báo 0 trang tràn, UA Chrome thường thấy 11/48 trang tràn 15–16 px do `button.slick-next`.
- Tải lại trang ở từng bề rộng. Slider dựng mũi tên theo cỡ lúc tải: một trang tải ở 1000 px rồi đổi lên 1100 px đo 0, tải thẳng ở 1100 px đo 16 px.
- Không chặn ảnh để quét nhanh khi kết luận. `figure` có `width` cố định đổi cỡ khi thiếu ảnh và tạo tràn giả. Đo lại mọi URL bị gắn cờ ở chế độ tải đầy đủ.
- Bộ bề rộng thưa bỏ sót lỗi giữa hai mốc. Site agency mẫu 20/10: 11 cỡ từ 390 đến 1366 px báo 0, trang vẫn tràn 40 px ở 800 px và 10 px ở 900 px. Nếu lần ghi chạm CSS có media query, thêm các mốc quanh breakpoint của theme vào `widths` (ví dụ 769, 800, 900, 1024, 1100).
- Phần tử ẩn bằng `visibility:hidden` (ví dụ tooltip `::after`) vẫn tính vào vùng cuộn. Report không liệt kê nó là thủ phạm, nhưng bề rộng tài liệu vẫn tăng. Ẩn bằng `display:none`.
- Không đặt bề rộng dưới 500 px bằng cờ `--window-size`. Chrome headless ép tối thiểu 500 px. Script dùng `Emulation.setDeviceMetricsOverride`.
- Trang hoãn JS tới lần chạm đầu (LiteSpeed, delay JS) đổi bố cục sau lần chạm. Script giả một lần rê chuột và một phím Shift trước khi đo.
- Không kết luận chỉ từ bản bỏ cache. Plugin cache gộp và tối ưu CSS, nên bản có cache có thể tràn mà bản bỏ cache không tràn. Site agency mẫu 20/10: trang tràn ở 1099–1100 px chỉ trên bản có cache, lượt quét bằng query bỏ cache không thấy. Lần ghi kèm purge, làm nóng hoặc đổi CSS: chạy `--cache both`.

## 2. Axe

- Script chạy axe-core ở bề rộng nhỏ nhất và lớn nhất. Bộ tag: WCAG 2.0/2.1/2.2 A, AA và best-practice.
- FAIL khi có luật mức `critical` hoặc `serious`. Luật mức thấp hơn là WARN.
- Đổi mức chặn bằng `axe.fail_impacts`. Bỏ một luật bằng `axe.ignore` và ghi lý do vào report.
- Thiếu file axe-core thì hạng mục SKIP. Tải một lần: `curl -o ~/.cache/web-qa-gate/axe.min.js https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js` (tạo thư mục trước).

Bẫy:

- Tên link, alt và nhãn phải có trong HTML server. JS hoãn tới lần chạm đầu không giúp crawler và trình đọc màn hình ở lần tải đầu.
- Kết quả `incomplete` của axe (ví dụ tương phản trên nền gradient) không vào report. Kiểm tay các khối đó.

## 3. Focus bàn phím

- Script bấm Tab thật qua CDP, tối đa 80 lần (`focus.max`), ở bề rộng nhỏ nhất và lớn nhất.
- Script ghi style của phần tử lúc có focus. Khi Tab sang phần tử kế, script đọc lại style đó lúc không có focus. Style gồm outline, box-shadow, màu và độ dày viền, nền, màu chữ, gạch chân.
- FAIL khi style không đổi giữa 2 lần đọc. Dữ liệu cũ của `focus.mjs` không có số so: FAIL khi không có `outline` hay `box-shadow`.
- FAIL khi phần tử ẩn vẫn nhận focus, ví dụ slide `aria-hidden` của carousel.
- WARN khi phần tử đầu tiên nhận focus không phải skip link.
- Phần tử ngoài màn hình lúc đo chỉ vào ghi chú. Trang cuộn mượt làm số này tăng. Script tắt cuộn mượt trước khi bấm Tab.
- Script không đo tương phản của chỉ báo focus. Chỉ báo phải đạt 3:1 với nền, nhất là trên footer tối.

Bẫy: style focus thường có transition 0,15 s. Script đọc sau 120 ms, lúc giá trị đã khác giá trị gốc, nên vẫn thấy thay đổi. Trang có transition dài hơn 1 s cần xem ảnh.

## 4. Form

Mặc định script chỉ kiểm cấu trúc và không gửi form.

- HTML server: mỗi form không phải ô tìm kiếm được đọc `action`, `method`, trường nhập, trường ẩn.
  - FAIL khi form không có trường nhập.
  - WARN khi form không có trường email hay điện thoại.
  - WARN khi không thấy honeypot, captcha (reCAPTCHA, Turnstile, hCaptcha) hay token chống spam do JS thêm. Script lấy token từ trường ẩn có trong DOM mà không có trong HTML server, ví dụ `wpforms[token]`.
  - WARN khi form có `method="get"`, có `action` và có trường liên hệ. Form không có method lẫn action thường do JS gửi, nên không tính.
  - Trường `nonce`, `token`, `csrf` được ghi vào report.json để tham khảo. Thiếu nonce không phải lỗi, vì nhiều plugin form gửi qua AJAX.
- DOM ở từng bề rộng: FAIL khi trang khai báo `"form": true` mà form không hiện hoặc không có trường nhìn thấy. FAIL cả khi form hiện ở một bề rộng mà mất ở bề rộng khác.
- Gửi thật: đọc `references/form-gui-that.md`.

Bẫy: form có thể khởi tạo ở desktop mà không khởi tạo ở bề rộng 768 px trở xuống. Lượt kiểm chỉ ở desktop bỏ sót lỗi này.

### Đường đi của lead (kiểm tay)

Script không kiểm phần sau khi form gửi đi, nên report của hạng mục Form luôn có dòng nhắc. Kiểm checklist này khi lần ghi chạm form, plugin form, plugin SMTP, plugin ghi Sheet hoặc template của trang có form. Kiểm thêm một lần ở cổng trước production.

Mọi bước chỉ đọc. Lấy dữ liệu server theo hồ sơ `00-client-context/wp-server.md`. Không SSH khi không có hồ sơ. Che mật khẩu, API key và token khi đọc option. Không in các giá trị đó ra chat hay file.

| Chặng | Kiểm gì | Lỗi chặn |
|---|---|---|
| 1. Form | Liệt kê mọi form (Contact Form 7, WPForms, form của theme) kèm người nhận, người gửi, tiêu đề mail. Contact Form 7 lưu cấu hình mail trong post meta `_mail` của post type `wpcf7_contact_form`. | Người nhận là `{admin_email}`, `[_site_admin_email]` hoặc hộp thư không ai đọc |
| 2. Mail | Đọc option của plugin SMTP đã che secret. Nếu nhà gửi mail có trang sự kiện, đọc bounce và danh sách chặn (suppression). | Địa chỉ nhận bị bounce hoặc bị chặn; SMTP báo lỗi |
| 3. Sheet | Đọc hook mà plugin ghi Sheet dùng. | Plugin chỉ ghi Sheet sau khi mail gửi thành công, nên mail hỏng kéo theo mất Sheet |
| 4. CMS | Kiểm lead có bản lưu trong CMS độc lập với mail (bảng entry của plugin form, plugin lưu tin nhắn, post type lead). | Không có bản lưu, nên mail hỏng là mất lead vĩnh viễn |
| 5. Hộp thư thật | Gửi một lượt thử theo `references/form-gui-that.md` và tìm token. | Không thấy mail sau thời gian người vận hành hẹn |

Đối chiếu số:

1. Đếm số request POST tới endpoint form trong access log, theo ngày (đường log ghi trong hồ sơ server).
2. Nhờ người vận hành đếm số thư nhận cùng ngày, kể cả thư mục spam và thùng rác. Skill không tự đọc hộp thư.
3. Nếu số thư ít hơn số POST hợp lệ, ghi FAIL cho chặng Mail và tìm mốc hỏng.

Khi một chặng hỏng:

- Tìm mốc bắt đầu hỏng. So option SMTP và `active_plugins` giữa các bản backup DB theo ngày. Đọc log gửi mail của plugin nếu có.
- Báo sự cố ghi đủ 4 ý: tên site, chặng hỏng, mốc bắt đầu, số lead có thể đã mất.
- Không sửa trong lượt kiểm. Sửa là việc ghi, cần duyệt theo skill của việc ghi.

Lỗi đã gặp (đợt 17/10/2026, 2 site mẫu):

- Một site mất mail và Sheet khoảng 4 tháng. Lead không khôi phục được.
- Site còn lại có 48/49 form gửi về một hộp thư không ai đọc. Địa chỉ nhận chính bị bounce từ nhiều tháng trước.
- Câu báo "form đang mất lead" không ghi tên site, nên người đọc hiểu nhầm site khác bị hỏng.

## 5. Tracking

- Script chặn request tới GTM, GA, Google Ads, DoubleClick, Meta Pixel, Clarity, Hotjar, TikTok và Apps Script ngay từ đầu phiên. Cách chặn tương đương `route.abort()` của Playwright.
- Thêm host tracking riêng (ví dụ server-side GTM) vào `tracking.block_extra`.
- FAIL khi một request tracking lọt qua chặn và nhận phản hồi.
- FAIL khi HTML thiếu thẻ khai báo trong `tracking.expect`. Mỗi mục là chuỗi con, hoặc regex có tiền tố `re:`.
- Chưa khai báo `tracking.expect` thì script chỉ kiểm phần chặn. Report liệt kê mã thẻ thấy trong HTML (GTM, GA4, UA, Ads, Pixel, Clarity).

Bẫy: cuộn trang hay rê chuột làm GTM hoãn chạy. Lượt chụp không chặn tracking trên production thành hit thật trong analytics.

## 6. Plugin staging = production

- Script so 2 file `wp plugin list` theo tên, trạng thái, version. File nhận dạng JSON, CSV, TSV hoặc bảng.
- Script bỏ dòng `Notice:`, `Warning:`, `Success:` của WP-CLI ở đầu output.
- FAIL khi có plugin chỉ có ở một bên, khác trạng thái hay khác version.
- Plugin khác có chủ ý (ví dụ mu-plugin chặn mail của staging) thì ghi vào `plugins.ignore`.
- Thiếu một trong 2 file thì hạng mục SKIP.

Bẫy: staging tắt plugin cache, bảo mật hay SMTP của production. Lỗi do plugin đó chỉ hiện trên production.

## 7. Mã HTTP

- Mọi URL trong `urls` phải trả 200 ở bước đầu. URL trả 301 nghĩa là danh sách QA chứa URL cũ.
- Mục `http` kiểm mã của đường dẫn đặc biệt: trang đăng nhập, `xmlrpc.php`, file cấu hình, trang 404 hay 410.
- `http` nhận list JSON, hoặc tên file text với dòng `mã đường-dẫn [location]` như `httpcheck.sh`.
- Mã `000` nghĩa là không kết nối được: tunnel rớt, DNS hay timeout. Mở lại tunnel rồi chạy lại.

## 8. Redirect

- Mỗi mục `redirects` có `from`, `to` và `code` (mặc định 301).
- Script đi theo tối đa 6 bước. FAIL khi mã bước đầu sai, đích cuối khác `to`, hoặc đích không trả 200.
- WARN khi chuỗi có hơn 1 bước.

## 9. Canonical

- Chỉ kiểm trang trả 200.
- Trang `noindex` (meta robots hoặc header `X-Robots-Tag`) được phép thiếu canonical. Rank Math bỏ canonical khi staging đặt `blog_public=0`.
- FAIL khi trang index được mà thiếu canonical, có nhiều thẻ canonical, canonical trỏ host khác `canonical_host`, hoặc canonical không tự trỏ.
- Trang có canonical chủ ý trỏ URL khác: khai báo `"canonical": "<đường dẫn>"` trong mục URL.
- WARN khi canonical là đường dẫn tương đối.
- Hạng mục này đọc một bản cache: HTML do curl lấy với UA desktop và `Accept: */*`. Plugin cache tách bản theo thiết bị và theo `image/webp` trong `Accept`, nên bản Googlebot và bản điện thoại có thể khác. Sau đợt PSI, purge hoặc làm nóng, chạy `skills/wp-pagespeed/scripts/cache_variants.py` cho URL vừa ghi. Script kiểm robots và canonical ở 5 biến thể.
- Chỉ kiểm canonical trên URL sạch. Nhiều theme và plugin SEO trả `noindex` và bỏ canonical cho URL có query.

## 10. Schema

- Script đọc mọi khối `application/ld+json`, kể cả `@graph` và node lồng nhau.
- FAIL khi một khối không parse được, khi thiếu loại khai báo trong `schema` của mục URL, hoặc khi node Person hay Organization không có `name`.
- WARN khi trang không có JSON-LD, khi tên là `admin` hay `administrator`, hoặc khi `@id` mang host khác `canonical_host`.
- ImageObject (ví dụ ảnh gravatar) không tính khi so host.

Bẫy:

- Trang tạo bằng WP-CLI không có `post_author` thì schema có Person `@id=/author/` mà không có tên.
- Node schema gộp trên staging có thể mang domain production.
- Script không thay Rich Results Test. Chạy công cụ đó cho template mới.

## 11. Jev ui-visual

- `ui_visual.tiles` mặc định là `"all"`: script chụp đủ ceil(cao trang / cao màn) màn cho mỗi URL và bề rộng, tối đa `tiles_max` (mặc định 12). Thiếu màn so với số cần là FAIL. Chạm trần `tiles_max` là WARN. Site đặt số màn cố định thì thiếu màn chỉ là WARN.
- Ẩn nút nổi khi chụp: khai `ui_visual.hide_selectors` (danh sách selector) hoặc `ui_visual.hide_fixed: true`. Cờ `hide_fixed` ẩn phần tử `position: fixed` nằm dưới mép trên 100 px, nên header dính vẫn hiện. Script hiện lại các phần tử này sau khi chụp.
- Mỗi URL × bề rộng có trần giờ `--page-timeout` (mặc định 120000 ms). Hết giờ thì script ghi `err` vào dòng đó, mở lại Chrome và đo tiếp.
- Script dọn Chrome mồ côi của lượt cũ khi bắt đầu. Dọn tay: `node skills/web-qa-gate/scripts/chrome_cleanup.mjs` (chỉ liệt kê), rồi thêm `--apply`. Script chỉ đụng profile có tiến trình chủ đã chết.
- Trước khi gửi Jev, `pad_image` thu ảnh về tối đa 1.568 px mỗi cạnh và 0,8 MP, rồi đệm nền trắng cho cạnh dưới 320 px và cho ảnh dẹt (cao dưới 0,3 lần rộng). Jev trả `http_400` với ảnh cạnh dưới khoảng 280 px, ảnh trên khoảng 1 MP và ảnh dẹt (đo 23/10/2026). Script tự viết gửi ảnh cho Jev phải theo cùng giới hạn.
- Rubric: `tools/ai-assist/tasks/ui-visual.json`. Jev trả 6 câu có/không, 1 hộp lỗi và 2 điểm.
- Script đọc ngưỡng theo thứ tự: registry của site (`00-client-context/model-calibration.json`), rồi `tools/ai-assist/calibration-defaults.json`. Entry phải khớp rubric, version và site.
- Câu chưa có ngưỡng dùng ngưỡng tạm 0,7. Report ghi "chưa hiệu chuẩn, chỉ báo cho người đọc".
- Mọi dòng Jev là WARN. Claude xem ảnh của mọi dòng rồi mới kết luận.
- Ghi vào `ui_visual.site_note` một câu tiếng Anh tả thiết kế và các phần tử cố định có chủ ý (header dính, nút liên hệ nổi, thanh dưới đáy).

Bẫy:

- `fixed_covers` hỏi theo nghĩa đen. Ảnh chụp giữa trang thường có header dính hay thanh đáy che một dòng chữ. Claude chỉ coi là lỗi khi phần bị che không lộ ra khi cuộn. Ví dụ: nút nổi che chữ ở chân trang, thanh đáy che nút gửi của form.
- Ẩn nút nổi bằng `hide_selectors` hoặc `hide_fixed`, không chỉ mô tả trong `site_note`. Lượt chụp 18/10 trên site mẫu: Jev gắn cờ `fixed_covers` nhầm 453/742 ảnh vì 3 nút nổi. Thêm mô tả vào `site_note` không giảm cờ (54 trước, 54 sau).
- Không dùng `pkill` để dừng Chrome của lượt treo. Lệnh này giết cả Chrome của lượt khác đang chạy. Lượt 18/10: 27 Chrome headless chạy, 9 tiến trình mồ côi sau `pkill`, và script chụp treo 27 phút làm lỡ mốc trước deploy. Dùng `chrome_cleanup.mjs`.
- `cut_off` của Jev không thấy phần tử bị cắt trong hộp của nó, ví dụ ô chọn ngôn ngữ trên header. Phép đo tràn ngang cũng không bắt lỗi này, vì hộp cha có `overflow: hidden`. Xem header ở mọi bề rộng.
- `media_problem` của Jev không thấy ảnh bị thiếu khi chỗ trống không có khung, ví dụ ảnh tác giả cạnh tên.
- Không dùng điểm `polish` để loại.
- Rubric hỏi chung "có lỗi không" gắn cờ gần mọi ảnh. Mỗi câu hỏi một loại lỗi.
- Chi phí khoảng 0,0002 USD mỗi ảnh. Lượt 72 ảnh tốn 0,015 USD.

## 12. Chữ dễ đọc (kiểm tay, script chưa chấm)

Kiểm khi lần ghi thêm hoặc sửa chữ trên trang, hoặc sửa CSS chữ. Đo bằng DOM ở 6 bề rộng 360, 390, 440, 768, 1024, 1366 px, trên bản bỏ cache (`?nc=`). Rê chuột một lần trước khi đo: LiteSpeed hoãn JS tới lần tương tác đầu, nên slider và form chưa dựng.

| Lỗi | Cách đo | Ngưỡng |
|---|---|---|
| Dòng chữ dính | Chữ thường hoặc số liền ngay chữ hoa tiếng Việt, không có khoảng trắng (ví dụ "30/11/2016Chịu"); `<br>` thiếu giữa hai câu | 0 |
| Line-height đoạn thân | `line-height` / `font-size` của khối văn bản không phải tiêu đề | ≥ 1,5; mục tiêu 1,6 |
| Đoạn dài căn giữa | Đoạn trên 3 dòng có `text-align: center` ở mobile | 0, trừ thẻ có icon và tiêu đề cùng căn giữa |
| Khoảng cách đoạn | Margin giữa hai `<p>` liền nhau | ≥ 0,6em |
| Tiêu đề sát thân | Khoảng cách từ tiêu đề tới đoạn đầu | ≥ 12 px |
| Dòng quá dài | Số ký tự mỗi dòng ở desktop | ≤ 80 |
| Tràn sau khi thêm chữ | Mục 1, chạy lại sau khi thêm copy | 0 |

Bẫy:

- Thêm chữ vào khối có `aspect-ratio` cộng `min-height` của theme làm khung rộng hơn cột và tràn ngang. Đặt `min-height: 0` khi dùng `aspect-ratio`.
- Nhãn, câu hỏi FAQ, tên và chức danh khách không phải đoạn thân. Không tính vào lỗi line-height.
- Không tự rút chữ đã duyệt để vừa khung. Ghi đề xuất bản ngắn cho người duyệt.
- Site agency mẫu 23/10, 7 trang × 6 bề rộng: line-height dưới 1,6 giảm từ 1.122 xuống 339 ô, đoạn trên 3 dòng căn giữa trên mobile giảm từ 367 xuống 14, lỗi footer dính chữ giảm từ 41 xuống 0. Phần còn lại là nhãn và tiêu đề.
