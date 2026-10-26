# Gửi form thật và kiểm hộp mail

Lệnh này tạo lead thật trong CMS hay CRM và gửi mail tới hộp thư thật. Đọc hết file này trước khi chạy.

## Quyền chạy

| Môi trường | Điều kiện |
|---|---|
| Staging | Chạy được khi staging gửi mail tới hộp thư thử của người vận hành, không gửi tới khách. |
| Production | Người có quyền duyệt (với dự án của GTV: Vincent) duyệt rõ cho từng lượt. Ghi tên người duyệt và giờ duyệt vào `--approved`. |

- Không chạy khi chưa biết mail sẽ tới hộp thư nào.
- Không dùng tên, số điện thoại hay email của người thật làm dữ liệu thử.
- Một phê duyệt chỉ áp cho một lượt gửi. Lượt sau cần duyệt mới.

## Chuẩn bị

1. Hỏi người vận hành cách kiểm hộp mail: hộp thư nào, ai mở, tìm theo chữ gì. Skill không tự đọc hộp thư.
2. Tạo file dữ liệu, ví dụ `form_live_data.json`. Khoá là `name` của trường trong form. Chuỗi `{token}` được thay bằng mã của lượt gửi:

   ```json
   {"your-name": "QA web-qa-gate {token}", "your-email": "qa+{token}@<hộp thư thử>", "your-message": "Lượt kiểm form tự động {token}. Bỏ qua lead này."}
   ```

3. Thêm mục `form_live` vào config: `page` (tên trong `urls`), `data` (file trên), `form` (selector nếu trang có nhiều form), `success` (selector hay chữ của thông báo gửi thành công).

## Chạy

```bash
export WEB_QA_SUBMIT_LIVE=<host đúng của trang, ví dụ stg.example.vn>
python3 -E skills/web-qa-gate/scripts/qa_gate.py run --config <qa.json> --out <thư mục> --submit-live [--approved "<người duyệt, ngày giờ>"]
```

- Script từ chối khi thiếu cờ `--submit-live`, khi `WEB_QA_SUBMIT_LIVE` khác host của trang, hoặc khi môi trường không phải staging mà thiếu `--approved`.
- `form_submit.mjs` kiểm lại cờ và biến môi trường lần nữa.
- Lượt gửi chặn GA, GTM và Pixel để lead thử không thành chuyển đổi trong báo cáo. Endpoint của form không bị chặn.
- Kết quả nằm ở `raw/form_live.json`: token, trường thiếu, thông báo thành công có hiện không, mã HTTP của các request POST.

## Kiểm hộp mail

1. Tìm token trong hộp mail theo cách người vận hành đã cấp.
2. Ghi kết quả vào report:

   ```bash
   python3 -E skills/web-qa-gate/scripts/qa_gate.py report --config <qa.json> --out <thư mục> --mail-ok <token>
   python3 -E skills/web-qa-gate/scripts/qa_gate.py report --config <qa.json> --out <thư mục> --mail-missing <token>
   ```

3. Báo người vận hành xoá lead thử trong CMS, CRM hoặc Google Sheet nếu quy trình của site yêu cầu.

Trạng thái hạng mục Form sau lượt gửi:

| Tình huống | Trạng thái |
|---|---|
| Không thấy thông báo thành công, hoặc không có POST trả 2xx/3xx | FAIL |
| Gửi được, chưa kiểm hộp mail | WARN, kèm token |
| Hộp mail có mail chứa token | PASS |
| Hộp mail không có mail sau thời gian người vận hành hẹn | FAIL |
