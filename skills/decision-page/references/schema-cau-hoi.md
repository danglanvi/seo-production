# Schema `cau-hoi.json`, file đầu ra và mã thoát

Mục đích: tra trường của `cau-hoi.json` khi viết thẻ, và đọc mã thoát của hai script. Nguồn sự thật là `scripts/gen_decision.py` (hàm `load_spec`). Khi file này lệch với script, script đúng.

## 1. Trường gốc

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `project` | có | Slug `a-z0-9-`. Script đặt tên file theo slug này. Ví dụ `gtv-website`, `web-skill-review`. |
| `title` | có | Tiêu đề H1 của trang. |
| `intro` | không | Một đoạn mở: trang này hỏi gì, bao nhiêu câu. |
| `eyebrow` | không | Dòng nhỏ trên H1. Mặc định là `<project> · bản N`. |
| `key_note` | không | Ô luật ở đầu trang. Mặc định là luật "để trống = theo đề xuất, trừ mục Phải chọn". Đặt `""` để ẩn. |
| `notes` | không | `[{kind, text}]`. `kind` nhận `warn`, `key` hoặc rỗng. |
| `mo_tu_ban_cu` | không | `[{label, href, note}]`. Liệt kê trang cũ còn chờ trả lời. Trang hiện khối "Bản cũ vẫn chờ anh trả lời". |
| `answer_title` | không | Dòng đầu của câu trả lời khi bấm Chép. Mặc định: `Trả lời trang <title> (bản N):`. |
| `page_title` | không | Thẻ `<title>`. Bản artifact cần tên 2 đến 4 từ, ví dụ "Duyệt skill web site-mau". |
| `db` | không | `{collection, doc}`. Mặc định `answers` và `lead`. Chỉ bản artifact dùng. |
| `report_html_file` | không | Đường dẫn tương đối tới mảnh HTML của tab "Báo cáo". Script từ chối file có `<script>`. |
| `report_label` | không | Nhãn nút tab báo cáo. Mặc định "Báo cáo đầy đủ". |
| `cards` | có | Danh sách thẻ, không rỗng. |

Script tự thêm `version` và `built` vào bản sao `.cau-hoi.json` cạnh trang. Không gõ hai trường này tay.

## 2. Trường của thẻ

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | có | Khớp `[a-z0-9][a-z0-9_-]*`, duy nhất. Không dùng id hệ thống: `toc`, `out`, `copy`, `done`, `clear`, `cnt`, `sync`, `view-quyet`, `view-baocao`, `tab-quyet`, `tab-baocao`, `dp-root`. |
| `label` | có | Nhãn ngắn, duy nhất, ví dụ `A1`, `Luật 1`. Nhãn đứng đầu mỗi dòng của câu trả lời. Thiếu thì script lấy `title`. |
| `title` | có | Tiêu đề thẻ, viết bằng tiếng thường. |
| `toc` | không | Chữ ở mục lục. Mặc định là `title`. |
| `kind` | không | `question`, `info` hoặc `done`. Thẻ có `questions` mặc định là `question`. Thẻ không có câu hỏi mặc định là `info`. |
| `context` | có với `question` | Danh sách câu bối cảnh, ít nhất 1 câu có chữ. |
| `risk_if_skipped` | có với `question` | Một câu: nếu Lead bỏ qua thì chuyện gì xảy ra. |
| `touches_live` | có với `question` | `true` hoặc `false`. `true` khi việc chạm site, server hoặc config đang chạy. |
| `blocks` | không | Khối nội dung phụ, xem mục 3. |
| `images` | không | `[{src, caption, alt}]`. Xem mục 4. |
| `questions` | có với `question` | Xem mục 5. Thẻ `info` và `done` không được có câu hỏi. |
| `note` | không | Ô ghi chú. Thẻ `question` mặc định có ô. Thẻ `info` và `done` mặc định không có. `true` để bật, `false` để tắt, `{placeholder}` để đổi chữ gợi ý. |
| `in_toc` | không | `true` để đưa thẻ `info` hoặc `done` lên mục lục. |

Dùng thẻ `done` để liệt kê việc agent đã tự quyết theo đề xuất. Dùng thẻ `info` cho số liệu hoặc bối cảnh chung.

## 3. Khối `blocks`

| `type` | Trường | Hiển thị |
|---|---|---|
| `p` | `text`, `muted` (mặc định `true`) | Đoạn văn. |
| `h3` | `text` | Tiêu đề phụ. |
| `list` | `items[]` | Danh sách chấm. |
| `note` | `text`, `tone` (`warn`, `key` hoặc rỗng) | Ô ghi chú màu. |
| `stats` | `items[{n, label}]` | Hàng số lớn. |
| `table` | `head[]`, `rows[[...]]`, `num_cols[]` | Bảng. Cột có số thứ tự trong `num_cols` căn phải. |
| `bars` | `title`, `max`, `rows[{label, value, tone, display}]`, `caption` | Biểu đồ thanh ngang. `tone` nhận `ok` hoặc `bad`. |

Script từ chối `type` khác danh sách trên.

## 4. Ảnh

- Bản local nhận đường dẫn tương đối so với file JSON. Script kiểm file có tồn tại.
- Bản artifact chỉ nhận URL `https://` hoặc `data:`. Ảnh cục bộ không chạy trên artifact, nên script trả mã 2.
- Đặt ảnh trước và sau thành hai mục liền nhau. Ghi `caption` nói rõ ảnh nào là trước, ảnh nào là sau.

## 5. Câu hỏi và phương án

```json
{"key": "rule", "short": "Rule chặn PHP", "text": "Áp rule chặn PHP cho 3 thư mục?",
 "options": [
   {"label": "Áp rule, giữ bản sao file cũ 7 ngày.", "value": "Áp rule", "recommended": true,
    "consequence": "Ba thư mục ngừng chạy PHP. Gỡ lại trong 1 phút."},
   {"label": "Chưa áp.", "value": "Chưa áp", "consequence": "Ba thư mục vẫn chạy được PHP."}]}
```

Ví dụ minh hoạ theo một mục ngày 19/10/2026 của site site agency mẫu. Bản đầy đủ của thẻ nằm ở `references/viet-muc-cho-quyet.md` mục 3.

- `text` bắt buộc. `short` là tên câu trong câu trả lời. Thiếu `short` thì script lấy `text`.
- `key` bắt buộc khi thẻ có từ 2 câu hỏi. Tên câu trong db là `<id>.<key>`. Thẻ một câu dùng tên `<id>`.
- Mỗi câu có ít nhất 2 phương án và đúng 1 phương án `recommended: true`.
- `label` bắt buộc. `value` mặc định bằng `label`, và phải duy nhất trong câu.
- `destructive: true` đánh dấu việc xoá, gửi ra ngoài, tiền hoặc pháp lý. Trang hiện nhãn "Xoá hoặc ra ngoài".
- `consequence` là một câu hậu quả. Ghi cho mọi phương án.

Luật để trống: câu trống tính là theo đề xuất. Có hai ngoại lệ:

- Thẻ có `touches_live: true`.
- Phương án đề xuất có `destructive: true`.

Hai loại này hiện nhãn "Phải chọn". `parse_answer.py` đưa câu trống loại này vào mục "Chờ chọn rõ", không đưa vào danh sách làm.

## 6. Định dạng chữ

- Mọi trường chữ nhận ba dạng: `` `code` ``, `**đậm**`, `[chữ](https://...)`.
- Script escape mọi HTML thô. Link `javascript:`, `data:` và `vbscript:` chỉ còn chữ.
- Không viết HTML trong JSON. Cần bảng hoặc biểu đồ thì dùng `blocks`.

## 7. File đầu ra

Với `project` = `gtv-website` và số bản 8, script ghi vào `--out`:

| File | Khi nào | Nội dung |
|---|---|---|
| `gtv-website_cho-anh-quyet_v8.html` | bản local | Trang đủ `<html>`, nút "Chép câu trả lời", nút "Xoá lựa chọn", lưu `localStorage`. |
| `gtv-website_cho-anh-quyet_v8_artifact.html` | `--artifact` hoặc `--both` | Mảnh HTML cho Artifact tool: token màu ở `:root`, dark mode, nút "Lưu, tôi trả lời xong", nút Chép dự phòng. |
| `gtv-website_cho-anh-quyet_v8_khoi-phuc.md` | cùng bản artifact | Cách publish lại và nạp lại db khi đổi tài khoản. |
| `gtv-website_cho-anh-quyet_v8.cau-hoi.json` | luôn có | Bản sao spec kèm `version`, `built`. `parse_answer.py --spec` đọc file này. |

- Số bản bằng số lớn nhất của `<project>_cho-anh-quyet_v*.html` trong thư mục cộng 1.
- Script mở file ở chế độ `x`, nên không ghi đè file có sẵn.
- `--version N` ép số bản. Script từ chối khi file của bản đó đã có.

Doc db mà trang ghi có 5 trường: `choices` (tên câu → value), `notes` (id thẻ → chữ), `text` (đúng chữ của nút Chép), `done` (`true` sau khi bấm Lưu), `updated` (ISO).

## 8. Mã thoát

`gen_decision.py`:

| Mã | Nghĩa | Làm gì |
|---|---|---|
| 0 | Đạt | Đi tiếp. |
| 2 | Spec hoặc tham số sai, hoặc file đã tồn tại | Đọc danh sách lỗi, sửa JSON. Không ép `--version` để né. |
| 3 | Chrome test lỗi | Nút Chép, `localStorage` hoặc db làm mất dữ liệu. Không gửi trang. Báo lỗi script. |
| 4 | Trang chứa secret, IP, mật khẩu, lệnh ssh hoặc mẫu cấm riêng | Bỏ chi tiết đó khỏi JSON. Không dùng `--allow-sensitive`. |
| 5 | `open -a` lỗi, hoặc chỉ thấy Chrome headless sau khi mở | Đưa Lead dòng "file URL" mà script đã in. |
| 6 | Máy không có Chrome cho `--chrome-test` | Báo thiếu tool. Không bỏ bước test. |

`parse_answer.py`:

| Mã | Nghĩa | Làm gì |
|---|---|---|
| 0 | Đạt | Làm theo mục "Làm". |
| 2 | File, JSON hoặc spec hỏng | Kiểm `--spec` đúng bản, kiểm file dán đủ dòng. |
| 3 | Có giá trị không khớp phương án, tên câu hoặc tên thẻ lạ, hoặc chữ dán thiếu dòng của một thẻ | Chỉ hỏi Lead các dòng ở mục "Không khớp phương án" và "Cảnh báo". Thẻ thiếu dòng nằm ở "Chờ chọn rõ". |
| 4 | `--require-done` mà doc chưa có `done: true` | Lead chưa bấm Lưu. Hỏi một câu, hoặc chờ. |

Mẫu cấm riêng của một site, ví dụ host staging hoặc slug đăng nhập, đặt trong một file ở `.agent-secrets/`. Không commit file đó. Truyền file bằng `--deny-file`. Mỗi dòng của file là một regex, dòng bắt đầu bằng `#` là chú thích.
