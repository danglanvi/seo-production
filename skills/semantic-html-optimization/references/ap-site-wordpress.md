# Áp semantic HTML trên site WordPress đang chạy

Quy trình rút từ đợt sửa thật trên site agency mẫu ngày 27/10/2026: audit 95 URL, 17 file theme, 436 op heading giả trên 109 bài, verify lệch 0, 0 lỗi 5xx, Jev 0,037 USD. Cần quyền server (SSH + WP-CLI) và hồ sơ `00-client-context/wp-server.md`. Ghi nội dung đi qua `wp-content-review-apply`, ghi theme đi qua `wp-staging-deploy`.

## 1. Audit theo mẫu template

1. Chọn URL đại diện mỗi template (trang chủ, dịch vụ, bài, chuyên mục, case, trang tĩnh). Site đã có bộ URL của job CSS gọn hay PageSpeed thì dùng lại. Không audit toàn site.
2. Chạy `python3 -I skills/semantic-html-optimization/scripts/semantic_audit.py --base https://<domain> chon.tsv <thư mục html> audit_truoc.csv`. Chỉ đọc, 1 request/giây.
3. Tìm gốc trong template, không sửa từng trang. Grep tạo danh sách ứng viên, không tự coi `<b>`, `<i>` có chữ hoặc card không bọc `<article>` là lỗi. Đọc ngữ cảnh và `html-aria-runtime.md`; dùng validator cho lỗi cú pháp, AX/keyboard cho tương tác. Ngày hiển thị có thể dùng `<time datetime>` khi có nguồn ngày đúng.
4. Lập bảng: lỗi, số trang, file gốc, cách sửa, ảnh hưởng giao diện. Đưa câu cần quyết lên trang duyệt (skill `decision-page` hoặc trang duyệt của `wp-content-review-apply`). Câu đã gặp: heading giả đổi thành heading thật hay giữ, bài có thêm `<time>` không, case có thêm ngày không, footer giữ chữ đậm hay đổi heading.

## 2. Sửa ở theme

| Lỗi | Cách sửa đã chạy |
|---|---|
| Trang không có `<main>` | Bọc vùng nội dung bằng `<main id="primary">` trong template |
| Bài thiếu `<aside>`, `<time>` | Sidebar bọc `<aside>`. Ngày đăng `<time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>">` |
| Card có nội dung tự đứng độc lập | Có thể bọc `<article>`; không áp cho mọi card chỉ có link/ảnh |
| Nhảy cấp H1 → H3 ở trang chuyên mục | Nhãn mục là `h2`. Chuyên mục thiếu tiêu đề giới thiệu thì thêm `h2.screen-reader-text` |
| Nhấn chữ trong template | Chọn `<strong>`, `<em>`, `<b>`, `<i>` theo nghĩa; CSS cho trang trí. Không đổi hàng loạt, giữ icon và tên accessible |

Bẫy khi sửa theme:

- Thêm `<main>` làm khớp rule `main .container` có sẵn trong mu-plugin, nội dung lệch 4–6 px. Vá bằng rule `html main .container` trong template đó, không sửa file của lane khác.
- Đổi `p` thành `h2` làm rule của builder thắng, ví dụ `.elementor-kit-6 h2{font-weight:700}` đổi chữ đậm 800 thành 700. Dùng shim `html body h2.<class>[class]` để thắng mà không dùng `!important`. Đọc rule thắng bằng CDP `CSS.getMatchedStylesForNode` (skill `wp-ui-fix`, `match.mjs`).
- Thẻ heading có `margin-bottom` mặc định của trình duyệt: đặt lại margin cho class cũ.
- Chuỗi `datetime=\"…\"` lọt từ bản diff vào HTML: grep `\"` ngoài khối PHP trước khi đóng gói.
- Đo trước và sau ở 1366 px và 390 px: ảnh lệch, hình học DOM theo class và id, chiều cao trang, lỗi JS, slider. Mục tiêu 0 phần tử lệch quá 1 px.

## 3. Heading giả trong nội dung bài

1. Quét sau `wpautop`, không quét chuỗi thô: `OUT=<file.jsonl> IDS=<id,...> wp eval-file skills/semantic-html-optimization/scripts/scan_heading_gia.php`. Script đánh dấu vị trí thô của từng thẻ `strong`/`b`, nên mỗi ứng viên map ngược về `post_content`. Lỗi đã gặp: lần quét thô bỏ sót 142 đoạn ở 48 bài vì dòng chữ đậm đứng ngay sau `</ul>` hoặc `[/caption]`.
2. Bỏ đoạn nằm trong `td`, `th`, `li`, `blockquote`, `figcaption`, `a`. Chữ lặp ở từ 10 bài trở lên là phần layout: hỏi người duyệt riêng.
3. Jev task `semantic-role` (`tools/ai-assist/tasks/semantic-role.json`) phân loại. Gán nhãn tay 20 mẫu trước khi xem điểm Jev (skill `model-calibration`). Lần đầu Jev khớp 18/20. Ngưỡng đã dùng: từ 0,7 nhận heading, 0,3–0,69 Claude đọc, dưới 0,3 giữ.
4. Luật giữ chữ đậm: câu dẫn có dấu hai chấm không đánh số, "Ví dụ N:", nhãn của danh sách, trang điều khoản và hợp đồng. Luật đổi heading: tiêu đề khối, "Tài liệu tham khảo", tên công cụ, mục đánh số ("Bước 1", "Cách 2"), câu hỏi FAQ.
5. Cấp heading bằng cấp heading thật đứng trước trong bài cộng 1, tối đa h4. Chuỗi "Bước 1…n" cùng cấp. Kiểm số lần nhảy cấp trước và sau: không bài nào xấu đi.
6. Dựng `ops.json` cho `wp-content-review-apply` (`apply.php`, op `text`): `old` là đúng chuỗi thô `<strong>X</strong>` khớp 1 lần, `new` là `<hN>X</hN>`. Bài không qua `wpautop` (HTML không có `<p>`) thì bỏ khỏi lô.
7. Chạy thử trên production với `FAIL_ON_SKIP=1`, áp 3 bài mẫu trên staging, chụp trước và sau cho người duyệt xem, rồi ghi theo lô. Mục lục tự động của bài sẽ thêm heading mới: cho người duyệt xem ở ảnh mẫu.

## 4. Sau khi ghi

- Đi hết tầng cache theo `wp-content-review-apply` Bước 6 mục 1: purge theo URL, purge CDN, kiểm giờ lưu ở edge.
- Đổi thẻ là đổi DOM. Site có CSS gọn theo path (`wp-ucss`) thì regen map cho đúng các path đã đổi, vì CSS gọn có thể thiếu rule cho thẻ mới (`main`, `article`, `aside`, `time`). Lane khác giữ khoá CSS gọn thì ghi danh sách path vào file phối hợp.
- Đo lại bằng `semantic_audit.py` ra `audit_sau.csv`, so với `audit_truoc.csv`. Đếm 5xx từ giờ bắt đầu ghi bằng `seo-logfile-analysis/scripts/log_health.py`.

## 5. Phối hợp khi phiên khác cùng sửa site

- Đọc khoá staging và khoá CSS gọn trước khi ghi production. Ghi production sau khi lane giữ khoá báo xong.
- Cổng đọc file phối hợp phải khớp dòng có cấu trúc, ví dụ `CHO-PHEP <lane> <giờ>`. Không mở cổng theo từ khoá. Lỗi đã gặp 27/10/2026: một dòng ghi chú chứa cả mã phiên lẫn chữ "cho phép" làm cổng của script mở nhầm.
- Chuỗi lệnh chạy nền dùng đường dẫn tuyệt đối cho mọi file danh sách path.
