# Thao tác ghi của apply.php

Mục đích: dạng thao tác (op) mà `scripts/apply.php` nhận, cách tìm chữ cũ và cách đọc log. Đọc ở Bước 5 khi dựng `ops.json` tay hoặc khi `plan.py` không phủ được thao tác. Gốc đường dẫn là root repo.

Mọi lô ghi dùng chung một engine. Không viết `apply*.php` riêng cho từng lô. Lý do: thư mục workstream của một site agency có 133 bản `apply*.php` chép tay ngày 24/10, và mỗi bản lặp lại lỗi NBSP, NFC, khoá rác.

## 1. Biến môi trường

| Biến | Bắt buộc | Nghĩa |
|---|---|---|
| `PLAN` | Có | Đường dẫn tuyệt đối tới `{"ops": [...]}` |
| `DRY` | Không | Thiếu biến thì chạy thử. Chỉ `DRY=0` mới ghi |
| `OUT` | Nên có | File log JSON. Script không ghi đè file có sẵn |
| `SRC` | Khi có `src_key` | File JSON chứa widget gốc cho `el_restore` |
| `PURGE` | Không | `PURGE=0`: không purge toàn site, người chạy purge theo URL |
| `FAIL_ON_SKIP` | Không | `1`: thoát mã 2 khi còn dòng `skip`. Dùng cho lượt chạy không người trực |

Mã thoát: 0 xong, 1 lỗi đầu vào (thiếu `PLAN`, JSON sai, `OUT` đã có), 2 còn `skip` khi bật `FAIL_ON_SKIP`.

Đặt các biến này sau `sudo -u www`, không đặt trước. Lý do và lệnh mẫu: `references/ghi-an-toan.md` mục 2.

## 2. Dạng op

Mỗi op có `item` (id thẻ) và `post` (ID bài, trừ op option và usermeta).

| `target` | Trường thêm | Việc làm |
|---|---|---|
| `meta:<key>`, `post_title`, `post_name`, `acf:<field>`, `elementor:<widget>:<đường.dẫn>` | `before`, `value` | Dạng cũ do `plan.py` sinh. So giá trị hiện tại với `before`, ghi `value` |
| `content` | `md5_before`, `value` | Ghi cả `post_content` khi md5 khớp |
| `redirect` | `src`, `to`, `code` | Thêm redirect Rank Math. Op `post_name` do `plan.py` sinh mang sẵn khối `redirect` cùng dạng |
| `text` | `field`, `old`, `new`, `ctx_trai?`, `ctx_phai?`, `nth?`, `multi?`, `count?` | Thay một câu trong một trường |
| `fix` | `field`, `old`, `new` | Sửa đích danh cả trường. `old: null` nghĩa là khoá chưa có |
| `el_rm` | `id`, `widget_type?` | Gỡ một phần tử Elementor theo id |
| `el_restore` | `id`, `parent`, `index?`, `widget` hoặc `src_key` | Chèn lại phần tử vào container `parent` tại vị trí `index` |

`field` của `text` và `fix` nhận một trong các dạng:

- `post_content`, `post_title`, `post_excerpt`;
- `meta:<key>`;
- `elementor:<widget>:<đường.dẫn>`, ví dụ `elementor:b435907:editor`;
- `usermeta:<uid>:<key>`;
- `option:<tên>` hoặc `option:<tên>:<đường.dẫn>` cho option dạng mảng.

Ví dụ (site mẫu `example.vn`):

```json
{"ops": [
  {"item": "scn-a1-12", "post": 101633, "target": "text", "field": "post_content",
   "old": "dịch vụ SEO", "new": "dịch vụ SEO & GEO", "ctx_trai": "Bảng giá", "nth": 1},
  {"item": "fx-07", "post": 2210, "target": "fix", "field": "elementor:a67e445:list.0.list_title",
   "old": "Bước 1", "new": "Bước 1: kiểm kỹ thuật"},
  {"item": "rm-hero", "post": 2210, "target": "el_rm", "id": "3f9c2d1", "widget_type": "image"}
]}
```

## 3. Luật khớp của `text`

1. Script chuẩn hoá cả chữ DB lẫn `old`: NFC, NBSP thành dấu cách, gộp khoảng trắng. Chữ DB có `\r\n` vẫn khớp.
2. `old` phải khớp đúng 1 vị trí. Khớp nhiều vị trí thì thêm `ctx_trai`, `ctx_phai` hoặc `nth` (đếm từ 1).
3. Muốn thay mọi vị trí: đặt `multi: true` và `count` bằng số vị trí mong đợi. Số khác thì skip.
4. Op đã áp rồi (chữ `new` đã nằm đúng chỗ) báo "đã đúng", không áp lần hai. Chạy lại cả plan an toàn.
5. Nhiều op cùng một trường chạy nối tiếp trên cùng bộ đệm, rồi ghi một lần ở cuối.

## 4. Đường dẫn Elementor và option

- Đường dẫn phải có đủ khoá cha. Thiếu một khoá thì skip với lý do "không thấy đường dẫn". Script không tạo khoá rác, không đánh dấu tài liệu là đã đổi.
- `el_rm` chỉ gỡ khi id xuất hiện đúng 1 lần. Có `widget_type` thì loại phần tử phải khớp.
- `el_restore` lấy widget gốc từ `widget` hoặc từ `SRC[src_key].widget`. Id của widget phải bằng `id` của op. Phần tử đã có trên trang thì báo "đã đúng".

## 5. Tìm nơi lưu chữ cũ trước khi dựng op

Chạy `scripts/locate.php` (chỉ đọc) để biết chữ nằm ở `post_content`, `post_title`, meta, `_elementor_data` hay option:

```bash
NEEDLES=/tmp/<phiên>/needles.json OUT=/tmp/<phiên>/locate.json SKIP_META=1 <lệnh wp> --path=<root> eval-file /tmp/<phiên>/locate.php
```

- `needles.json`: `[{"id": "<id thẻ>", "needle": "<chữ cũ>"}]`.
- Script đếm lại bằng regex đúng chữ, vì `LIKE` của MySQL không phân biệt dấu. Hit có `count` 0 bị bỏ.
- Trên production luôn đặt `SKIP_META=1`. Quét postmeta bằng `LIKE` rất nặng trên DB lớn. Cần quét meta thì chạy trên staging.
- Lấy `old` từ kết quả này hoặc từ JSON đọc thẳng DB, không lấy từ file thẻ (mục 4 của `ghi-an-toan.md`).

## 6. Đọc log

Log trong `OUT` có:

- `before`: giá trị trước khi ghi, theo loại trường. Dùng để rollback từng trường.
- `md5_after`: md5 của giá trị vừa ghi. Dùng để kiểm trước khi rollback (`ghi-an-toan.md` mục 5).
- `ok`: op đã ghi hoặc "đã đúng". `skip`: op bị bỏ kèm lý do. `notes`, `redirect_ids`.

Mỗi dòng `skip` của lượt chạy thử phải có lý do đã hiểu trước khi chạy `DRY=0`.

## 7. Chặn op ghi đè giá trị đã duyệt

Trước khi chạy `ops.json` tự dựng, so với sổ giá trị đã duyệt:

```bash
python3 -I skills/wp-content-review-apply/scripts/so_duyet.py check --so so-duyet.json --plan ops.json --out so-kiem.json
```

Mã 1 nghĩa là có op ghi đè giá trị đã duyệt mới hơn của thẻ khác, hoặc op không qua trang duyệt. Bỏ các op đó khỏi lượt ghi và báo người duyệt. Op `text` không so được với sổ, nên tra reviews theo post trước khi ghi (SKILL.md Bước 5).
