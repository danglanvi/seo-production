# Đếm đúng trước khi dọn

## Parser và đơn vị

- `scan_html.py`, `footprint_count.py` dùng Node + Acorn để đọc JavaScript. Cài một lần: `npm install --prefix ~/.cache/wp-code-footprint acorn@8.19.0` (Windows: cùng lệnh, thư mục `%USERPROFILE%\.cache\wp-code-footprint`). Script tìm theo thứ tự `ACORN_PATH`, thư mục cache này, rồi `acorn` của Node. Script không tự tải package. JSON kết quả ghi phiên bản parser. Đã kiểm với Acorn 8.19.0; kiểm fixture sau khi đổi version.
- JSON-LD, importmap và speculationrules là dữ liệu, không đưa vào parser JS. Script có `src`/`data-src` là external. Byte inline dữ liệu được ghi riêng, không tính vào JS thực thi.
- Regex literal, URL, chuỗi và phần chữ của template literal không phải comment. Comment trong `${...}` vẫn là comment. Không dùng regex xoá chuỗi để chứng minh code sạch.
- Byte là UTF-8; ký tự và KiB ghi đúng tên. `important_raw_html` của bộ đếm là số chuỗi trong toàn HTML, có thể gồm JS/chuỗi CSS; không gọi đó là số khai báo CSS `!important`.
- `scan_complete=false`, lỗi parse, thiếu Acorn/Node, tập HTML rỗng hoặc tập trước/sau khác nhau: trả mã 2, giữ dữ liệu một phần, không PASS. Số comment 0 chỉ có nghĩa khi quét hoàn tất.
- Khử trùng script bằng hash nội dung + loại script; ID và độ dài bằng nhau không chứng minh code giống nhau.

## Phân loại có ngữ cảnh

- Comment nội bộ, prompt, lời duyệt và marker dàn trang không phục vụ output là ứng viên dọn. Tên class có chữ “AI”, HTML Gutenberg, conditional comments, license và directive của công cụ không tự động là rác.
- Jev chỉ gắn cờ. Đọc lại đoạn nguồn và chức năng trước khi sửa. Điểm tương đồng embedding chỉ chọn cặp để so hook, dependency, phạm vi URL và đường rollback; không chứng minh hai plugin thay thế được nhau.
- Tách nội dung công khai đang hoạt động, bản nháp/revision lịch sử, cache sinh ra và backup. Không xoá lịch sử/backup chỉ vì một marker xuất hiện ở đó.
- “Không còn code dùng” cần cả đường gọi, biến thể, trạng thái tương tác và rollback; tìm không thấy bằng grep chưa đủ.
- Đếm heading gồm chữ trong thẻ con. `<aside>` trong `<article>` hoặc `<nav>` trong `<aside>` có thể đúng; không gắn lỗi chỉ từ quan hệ lồng.
- Cổng tối thiểu: `scan_complete=1`, `comment_quytrinh=0`, `htmlcomment_quytrinh=0`; đọc tay license/directive và cờ ngoài regex. Báo coverage cụ thể thay vì “database sạch 100%”.

## Kiểm sau sửa

Đọc `wp-staging-deploy/references/bang-chung-sau-ghi.md`. Additional CSS có mặt trong file gộp **không đủ** để kết luận sửa comment làm đổi hash: phải chạy đúng minifier và so 4 biến thể. Nếu byte đầu ra giống nhau, không tái tạo map/purge toàn site chỉ vì byte nguồn giảm.

Test offline: `tests/test_footprint.py`, `tests/test_parser_regressions.py`. Chạy lại trên bộ HTML đã lưu để chứng minh không mất coverage khi thay parser; không gửi DB riêng tư cho model phụ.
