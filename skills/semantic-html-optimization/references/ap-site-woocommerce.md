# Áp semantic HTML trên site WooCommerce có theme riêng

Đọc sau `ap-site-wordpress.md`, khi site bán hàng bằng WooCommerce hoặc theme do agency web dựng riêng.

Nguồn: site bán lẻ mẫu (WooCommerce, theme riêng, shared hosting LiteSpeed), 29–30/10/2026. Đợt này áp 94 việc qua 8 lane. Số thông báo html-validate trên toàn site giảm từ 13.761 xuống 5.912. Lane nào cũng có 0 lỗi PHP Fatal mới, 0 mã 5xx, và giữ nguyên robots, canonical của bản Googlebot smartphone. Bằng chứng nằm trong instance của site, thư mục `03-audits/technical/trien-khai-2910/semantic-ap-*/bao-cao.md`.

## 1. Phạm vi audit

- Audit đủ mọi template trước khi sửa: trang chủ, shop, danh mục, danh mục thương hiệu, PDP, bài, chuyên mục blog, tác giả, tìm kiếm, 404, giỏ, thanh toán, so sánh, liên hệ, trang chính sách. Người duyệt nhắc 29/10/2026 23:00 vì lượt đầu sót PDP, bài và chuyên mục blog.
- Phần nội dung trong template cũng cần thẻ riêng: mô tả danh mục, mô tả PDP, khối FAQ của danh mục và PDP. Người duyệt nhắc 29/10/2026 23:20.
- Giỏ và thanh toán chỉ hiện đủ khi giỏ có hàng. Đo với 1 món trong giỏ, rồi xoá món đó sau mỗi lượt đo.

## 2. Số đo

| Công cụ | Lệnh | Dùng để |
|---|---|---|
| html-validate | `bash scripts/html_validate.sh <thư mục html> <out.jsonl>` | Đếm thông báo theo rule, so trước và sau. Script ghi JSON ra file tạm vì Node cắt stdout khi đi qua pipe |
| `deep_audit.py` | `python3 -B scripts/deep_audit.py <thư mục html> <urls.tsv> <out.csv> <chi_tiet.jsonl>` | Đếm landmark, nhảy cấp, section không heading, form không nhãn, nút không tên, ngày không có `time`, bảng không `th`, breadcrumb, id trùng. File HTML đặt tên `<nhom>_d.html` |
| Đo bố cục | Chrome 1366 px và 500 px, toạ độ từng khối và chiều cao trang | Đạt khi 0 khối lệch quá 2 px. Khối đổi có chủ ý thì ghi lý do |

- Chạy `deep_audit.py` bằng `-B`, không dùng `-I`. bs4 nằm ở user site-packages nên `-I` làm script lỗi. HTML tải về chỉ đi vào script qua tham số.
- Tăng số thông báo của rule `prefer-native-element` sau khi thêm `role=list` cho lưới không phải lỗi mới. Rule này chỉ gợi ý dùng `ul`/`li` gốc.

## 3. Mẫu sửa đã chạy

| Khối | Cách sửa |
|---|---|
| Vùng nội dung WooCommerce | Thêm `woocommerce/global/wrapper-start.php` và `wrapper-end.php` của theme để bọc `<main>` |
| PDP | Bọc gallery, tóm tắt, mô tả, thông số, đánh giá, hỏi đáp bằng `article`. H1 nằm trong article. Khối Mô tả, Đánh giá, Hỏi đáp dùng `section aria-labelledby` trỏ H2 có id. Khối Thông số giữ `div` để tránh section lồng |
| Sản phẩm liên quan | Dùng `aside aria-labelledby`, đặt ngoài article của PDP |
| Khối trang trí không heading (quà tặng, cam kết, thanh toán, khuyến mãi) | Đổi `section` thành `div`, giữ class |
| Bảng thông số | Có `tbody`. `table` có `aria-labelledby` trỏ heading của khối |
| Giá | Giá gốc là `del`. Thêm chữ ẩn "Giá gốc: " và "Giá bán: " |
| Lưới sản phẩm | Thêm `role=list` và `role=listitem` khi CSS đã khoá lưới là `div` |
| Bảng so sánh | Thêm caption ẩn. Ô tên sản phẩm là `td`, ô tên nhóm là `th scope="colgroup"`, ô thông số có `scope` |
| Nút tăng giảm số lượng | Đổi `span` thành `button type="button"`, có `aria-label` tiếng Việt |
| Thanh toán | Phương thức thanh toán là `fieldset` có `legend` ẩn. Không chạm cổng thanh toán |
| Giỏ | Danh sách món là `ul > li` |
| Nhãn ARIA | Đổi nhãn tiếng Anh của theme sang tiếng Việt: Mở menu, Tìm kiếm, Menu chính, Xem giỏ hàng, Tài khoản của tôi |
| Phân trang | Chữ ẩn "Trang " trước số, nút trước và sau có chữ ẩn "Trang trước", "Trang sau" |
| Chip danh mục con | Dùng `nav aria-label` ("Danh mục sản phẩm", "<tên> theo thương hiệu") |
| Thẻ bài trong lưới blog | Đổi `div` thành `article` ở mọi template part của thẻ |
| Phần mở đầu của trang lưu trữ, tác giả, tìm kiếm | Bọc H1 và mô tả bằng `header` |
| Mô tả danh mục | `section aria-labelledby` trỏ H2 đầu của mô tả. Không có H2 thì dùng `aria-label`. Nút "Xem thêm" có `aria-controls` và `aria-expanded` |
| Bảng trong mô tả danh mục | Gán `scope` cho `th` bằng filter `term_description`, không sửa từng danh mục |
| Trang 404 | Menu gợi ý dùng `nav aria-label` |
| Ngăn kéo menu mobile | Panel đổi `section` thành `div`. Nút đóng đổi `a href="#"` thành `button` |
| Menu chính | Menu con mở được bằng bàn phím |
| Ngày cập nhật | Dòng "Cập nhật" dùng `time datetime`, lấy giá trị từ trường "Ngày cập nhật nội dung". Không lấy ngày sửa của bài, vì sửa link hay schema cũng đổi ngày đó |
| Ảnh thẻ sản phẩm | Alt bằng tên sản phẩm |
| Hộp tác giả | Hàng mạng xã hội bọc `address`. Không thêm `rel="author"` khi tên lấy từ option, vì link có thể sai trang tác giả |
| Đánh giá và hỏi đáp của plugin | Bọc markup ở file của theme. Microdata hỏi đáp sai thì sửa trong plugin, có backup và ghi chú áp lại khi plugin cập nhật |

## 4. Bẫy đã gặp

- WooCommerce lưu đường dẫn template trong object cache. File wrapper mới chỉ có hiệu lực sau khi xoá đúng khoá `template-globalwrapper-startphp-*` và `template-globalwrapper-endphp-*`. Lệnh rollback cũng phải xoá hai khoá này.
- `address` không được chứa heading. Ca đã gặp: khối liên hệ có 4 H2. Cách đúng là bọc riêng từng dòng địa chỉ, hotline, email.
- CSS gộp có rule `section:not(:first-child){padding-top:2rem}`. Đổi `div` thành `section` làm mỗi khối lệch 32 px.
- Style inline `line-height:inherit` đè line-height của class. Chỉ bù đúng thuộc tính lệch, đo A/B trên cùng trang.
- `button` mới không có CSS bù sẽ đổi màu chữ, nền, viền và mất icon. Mô phỏng trong trình duyệt trước khi áp.
- CSS bù đặt trong mu-plugin, trong thẻ `<style data-no-optimize="1">`. Không sửa file CSS của theme, vì CSS gọn theo path khoá theo md5 file CSS gộp.
- `wpautop` in `\r\n` giữa `<iframe>` và `</iframe>` thành `<br />`. Bỏ ký tự xuống dòng trong `post_content`, giữ nguyên `post_modified`.
- Chữ trong option và tên người dùng có thể lưu dạng Unicode tổ hợp. Chuẩn hoá NFC rồi so độ dài byte trước và sau.
- Thử form thật (đánh giá, hỏi đáp): đặt mu-plugin tạm chặn email có chuỗi kiểm thử. Gửi, duyệt, kiểm hiển thị, xoá bằng WP-CLI, rồi chuyển mu-plugin tạm vào quarantine. Ca đã gặp: 3 email bị chặn, 0 email gửi đi.
- Đo giỏ và thanh toán theo đúng thứ tự cũ. Mở thanh toán ngay sau khi thêm giỏ làm thông báo WooCommerce (63 px) hiện sai trang và báo lệch giả.
- Khi phiên tốc độ có CSS gọn theo path, gửi danh sách path đổi DOM cho phiên đó chạy lại bước kiểm sau giao (`wp-ucss`).
- Purge theo URL, lô tối đa 12 path. Dừng khi tải server vượt ngưỡng của site (`wp-pagespeed`, `luot-lon.md` mục 8).

## 5. Việc giao cho team

- Mô tả PDP (site mẫu có 242 PDP) và heading giả trong bài: dựng ops, làm 2 mẫu trước, rồi đi qua trang duyệt của `wp-content-review-apply`.
- Alt ảnh chính PDP: team Content viết, Agent ghi theo `image-seo-optimize`.
- Team Content điền trường "Ngày cập nhật nội dung" khi sửa nội dung thật. Khi sửa link, schema hay ảnh thì không điền.

## 6. Báo cáo cho người duyệt

- Mỗi việc có ảnh vị trí trên giao diện và code trước/sau. Người duyệt hỏi 29/10/2026 22:07 vì chưa hình dung được chỗ chèn thẻ.
- Thuật ngữ như "form không nhãn", "skip link", "heading chứa khối" phải có ảnh hoặc ví dụ đi kèm.
- Câu cần quyết dựng bằng skill `decision-page`, mỗi thẻ có minh hoạ và đề xuất.
