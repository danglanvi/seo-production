# SEO drift CLI — baseline, compare, history

Script đi kèm: `scripts/drift_tracker.py`, Python 3.9+ standard library; không cần pip/API key.
Chạy từ repo dự án, thay `<skill-dir>` bằng đường dẫn skill đang được nạp. Store ở dự án, không đặt dữ liệu client trong skill/master.

```bash
python3 <skill-dir>/scripts/drift_tracker.py --db 05-tracking/drift/client.sqlite baseline --urls urls.txt --label post-onpage
python3 <skill-dir>/scripts/drift_tracker.py --db 05-tracking/drift/client.sqlite compare --label after-deploy
python3 <skill-dir>/scripts/drift_tracker.py --db 05-tracking/drift/client.sqlite history --url https://example.com/article --element canonical
```

- `urls.txt`: một HTTP(S) URL mỗi dòng, bỏ dòng trống/comment `#`; hoặc CSV UTF-8 có cột `url`. Loại fragment/trùng URL, không nhận URL chứa credential.
- `compare` mặc định dùng URL của baseline mới nhất; `--baseline-id N` chọn snapshot cụ thể. `--urls` thay danh sách khi cần, URL thêm/bỏ chỉ là INFO.
- Mỗi lần baseline/compare tạo snapshot mới có timestamp và label. Compare không thay baseline. Thay đổi có chủ đích chỉ trở thành baseline sau quyết định của người dùng và một lệnh baseline mới.
- Mặc định nghỉ 1 giây giữa URL; `--interval` tối thiểu 0.5 giây. Trên 200 URL phải trình phạm vi/rate limit rồi dùng `--allow-large` sau khi được duyệt.
- `--timeout` mặc định 15 giây/request; lỗi mạng hoặc HTTP 5xx retry đúng một lần. Giới hạn response 5 MiB.
- `--json` đặt trước subcommand để xuất JSON cho bot. Mặc định stdout là Markdown; chỉ lưu report vào đường dẫn dự án đã chọn. Không tự gửi thông báo, tạo cron hay sửa website.

## Giá trị và giới hạn

Chụp đúng 9 nhóm trong skill: HTTP/final URL/redirect chain, title, description, canonical, robots (meta + X-Robots-Tag), H1, hreflang, schema types, số internal links. Nội dung lấy từ raw HTML; không chạy JavaScript.

Title/description/canonical là danh sách để giữ trường hợp HTML có nhiều thẻ; H1 có cả text và count. Hreflang/schema types được sắp xếp, tránh diff do thứ tự. Relative URL dùng final URL và `<base href>` nếu có. Internal links đếm thẻ `<a>` cùng hostname, không suy thành số URL duy nhất.

Timeout/lỗi mạng → `FETCH_ERROR`, không so bất kỳ element nào, không biến thành giá trị rỗng. HTTP 4xx/5xx có response thì giữ status để báo thay đổi HTTP; bỏ so phần HTML của trang lỗi. JSON-LD hỏng → schema_types không so được, không báo giả mất schema. Header robots thay đổi được ghi nhận; thêm noindex/nofollow (kể cả `none`) là CRITICAL.

Metadata phương pháp fetch/User-Agent đi cùng snapshot. Script từ chối compare khi phương pháp khác; nếu thay extractor phải tăng revision phương pháp. SQLite giữ lịch sử append-only qua CLI; không sửa trực tiếp database cũ.

## Exit code

| Code | Nghĩa |
|---|---|
| 0 | Lệnh hoàn thành, không có CRITICAL/HIGH; vẫn đọc MEDIUM/INFO nếu có |
| 1 | Có CRITICAL/HIGH cần Account/khách xác nhận chủ đích |
| 2 | Input/store lỗi hoặc có phần không so được; đọc JSON/Markdown, không suy là website không có drift |

Nếu vừa có CRITICAL vừa có phần không so được, exit 2; findings CRITICAL vẫn có trong report. Snapshot thành công chỉ chứng minh các element quan sát được, không chứng minh chất lượng SEO.

Kiểm thử bằng server cục bộ:

```bash
python3 -B -m unittest discover -s <skill-dir>/tests -p 'test_*.py'
```
