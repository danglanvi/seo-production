# Schema plan.json, lint, mã thoát và cách chuyển instance cũ

Mục đích: tra trường của `plan.json`, luật lint và cách xử lý từng mã thoát. Nạp ở bước 1 khi tạo hoặc mở plan, và khi một lệnh trả mã khác 0. Gốc đường dẫn: thư mục skill `skills/workstream-master-plan/`.

## 1. Khoá gốc

| Khoá | Kiểu | Ai ghi | Ghi chú |
|---|---|---|---|
| `title` | chuỗi | agent qua `init --title` | Ví dụ "Master plan <tên workstream>" |
| `updated` | chuỗi `DD/MM/YYYY HH:MM` | script | Mỗi lần ghi, script đặt lại giờ máy |
| `rules` | list chuỗi | agent | Luật riêng của workstream. Skeleton có sẵn 3 luật chung |
| `phases` | list `{id, name, when, why}` | agent | Mỗi việc phải trỏ một `id` có ở đây |
| `items` | list việc | `add-item`, `set-status` | Xem §2 |
| `done` | list `{when, what, evidence}` | agent | Nhóm việc đã xong trước khi có plan |
| `requests` | list yêu cầu | `add-request` | Xem §4 |

Skeleton trung tính nằm ở `templates/plan.skeleton.json`. Skeleton không chứa dữ liệu của site nào.

## 2. Việc (`items[]`)

| Trường | Bắt buộc | Ai ghi | Ghi chú |
|---|---|---|---|
| `id` | có | script tự cấp theo `--prefix` (mặc định `M`), hoặc `--id` | Chữ, số, `.`, `_`, `-`. Không trùng |
| `phase` | có | `--phase` | Phải có trong `phases` |
| `status` | có | `--status`, `set-status` | Xem §3 |
| `title` | có | `--title` | Một dòng |
| `detail` | không | `--detail`, dùng nhiều lần | List chuỗi. Đặt chi tiết dài ở đây, không đặt ở ask |
| `deps` | không | `--deps "<ID1>,<ID2>"` | Việc phải xong trước. Lint bắt id lạ và vòng |
| `blocks` | không | script | Script tự thêm khi việc khác khai `deps` |
| `source` | có | `--source` | Tin của Lead kèm giờ, hoặc tên tài liệu nguồn |
| `evidence` | có khi `done` | `--evidence` | Đường dẫn file, log hoặc số đo kiểm được |
| `program` | không | `--program` | Tên chương trình để đếm tiến độ riêng |
| `need_checked` | có khi `need` | `--checked` | Nơi đã tra mà chưa thấy Lead duyệt |
| `added`, `status_at` | không | script | Giờ máy, không có tham số nhập tay |

Plan cũ có thể thiếu `program`, `need_checked`, `added`, `status_at`. Lint vẫn đọc được các plan này.

## 3. Trạng thái

| Mã | Nhãn trên trang | Khi nào đặt |
|---|---|---|
| `doing` | Đang làm | Agent đang làm hoặc làm tiếp ở lượt sau |
| `todo` | Chưa làm | Đã vào plan, chưa bắt đầu |
| `need` | Cần Lead quyết | Đã tra thẻ, chat, ủy quyền chung và chưa thấy duyệt. Bắt buộc `--checked` |
| `wait` | Chờ mốc | Chờ ngày hoặc sự kiện ngoài, ví dụ "từ 25/10" |
| `other` | Phiên khác | Phiên hoặc lane khác đang giữ việc |
| `done` | Xong | Bắt buộc `--evidence` |

## 4. Yêu cầu (`requests[]`)

- `date`: script ghi `DD/MM/YYYY HH:MM`. Plan cũ có thể ghi `DD/MM HH:MM`, `20/10 17:0x` hoặc chữ. Build gom mốc không đọc được vào nhóm "Không rõ ngày".
- `ask`: tối đa 200 ký tự. Trích nguyên văn ý chính của tin. Nối nhiều đoạn trích bằng `…`.
- `items`: CHUỖI, ví dụ `"<ID1>, <ID2>"`. Không ghi list. List làm `build.py` lỗi `list.replace`.
- `items` phải nhắc ít nhất một id có trong plan. Ngoại lệ: chuỗi bắt đầu bằng `không có việc`, `xong` hoặc `luật`. Lệnh `--no-items-reason` ghi sẵn dạng `không có việc: <lý do>`.

Viết ask bằng đoạn trích nguyên văn dài từ 15 ký tự. Lý do: `audit_open.py` khớp tin với ask bằng so chuỗi. Ask diễn đạt lại làm tin đó hiện mãi trong danh sách mở.

## 5. Lint

Lỗi (lint mã 1, build từ chối dựng, lệnh ghi từ chối nếu thay đổi tạo lỗi mới):

- Thiếu khoá gốc, sai kiểu, thiếu `title`.
- Phase thiếu trường hoặc trùng id.
- Việc thiếu id, trùng id, thiếu title, phase lạ, status lạ, thiếu `source`.
- Việc `done` thiếu `evidence`.
- `detail`, `deps`, `blocks` không phải list chuỗi. `deps` trỏ id lạ, tự trỏ hoặc tạo vòng.
- Yêu cầu có `items` không phải chuỗi, thiếu ask hoặc date, không trỏ việc nào.
- `done[]` thiếu `when`, `what` hoặc `evidence`.

Cảnh báo (lint mã 0, trừ khi chạy `--strict`):

- Việc `need` chưa có `need_checked`.
- Mốc giờ nằm sau giờ hiện tại hơn 1 phút. Mốc không có năm qua tháng 12 sang tháng 1 vẫn đúng.
- Mốc giờ không đọc được.
- `blocks` trỏ id lạ. Yêu cầu nhắc một id cùng tiền tố mà plan không có.

## 6. Mã thoát

| Script | Mã | Nghĩa | Làm gì |
|---|---|---|---|
| `plan.py` | 0 | Xong | Tiếp bước sau |
| | 1 | Lint còn lỗi | Sửa theo dòng LỖI rồi chạy lại |
| | 2 | Đầu vào sai, hoặc thay đổi tạo lỗi mới | Đọc dòng LỖI, sửa tham số |
| | 3 | Không đọc hoặc ghi được plan.json | Kiểm đường dẫn và JSON |
| | 4 | Phiên khác vừa ghi plan.json | Chạy lại đúng lệnh đó |
| `build.py` | 0 | Xong | Mở HTML |
| | 2 | Lint còn lỗi hoặc `--since` sai dạng | Chạy `plan.py lint`, sửa, build lại |
| | 3 | Không ghi được file | Kiểm thư mục `--out-dir` |
| | 5 | Assert thất bại: bản dựng thiếu việc, thiếu ngày hoặc đếm lệch | Không sửa HTML tay. Báo lỗi script và giữ bản dựng cũ |
| `audit_open.py` | 0 | Không còn tin hoặc thẻ chưa vào sổ | Tiếp bước dựng |
| | 1 | Còn tin hoặc thẻ chưa vào sổ | Quay lại bước nhận yêu cầu |
| | 2 | Đầu vào sai, hoặc `.jsonl` không phải transcript Claude Code | Sửa tham số, hoặc xuất tin ra file text |

## 7. Rà tin bằng `audit_open.py`

- Nguồn `.jsonl`: transcript Claude Code. Script lấy tin Lead gõ, tin gửi giữa lượt (`queued_command`) và tin phiên khác chuyển. Script bỏ tin hệ thống, tin lịch tự chạy và khối `<ide_opened_file>`, `<ide_selection>`.
- Nguồn `.txt` hoặc `.md`: mỗi tin cách nhau dòng `---`. Đầu tin có thể ghi `[DD/MM/YYYY HH:MM]` để `--since` lọc được.
- Một tin coi là đã vào sổ khi một ask nằm trong tin, tin nằm trong ask, một đoạn ask từ 15 ký tự nằm trong tin, hoặc tin chứa từ 60% từ của ask.
- Tin ngắn hơn `--min-chars` (mặc định 12 ký tự) bị bỏ, ví dụ "ok", "duyệt".
- `--cards`: thẻ có status `approved` hoặc `edited` mà chưa áp. `--applied` nhận `mark_applied.json`. Giả định schema thẻ này chưa kiểm trên export thẻ thật.
- Đầu ra che chuỗi giống token, mật khẩu, khoá API và tham số `?sk=` của link chia sẻ.
- Lần chạy đầu trên plan có ask diễn đạt lại sẽ ra nhiều tin mở giả. Nếu phần lớn ask là câu diễn đạt lại, số tin mở có thể vượt nửa tổng số tin. Giới hạn bằng `--since` mốc phiên trước.

## 8. Chuyển instance cũ sang script của skill

Instance cũ là thư mục workstream đã có `plan.json` và `build.py` riêng trước khi có skill. Schema của instance cũ thường tương thích với skill. Dữ liệu cũ hay có hai lỗi mà lint của skill bắt: việc `done` thiếu evidence, và yêu cầu có `items` không trỏ id nào, ví dụ "file này". Khi lint còn lỗi, `build.py` của skill từ chối dựng.

Chỉ chuyển khi workstream đó chạy lại:

1. Chạy `plan.py lint --plan "<thư mục>/plan.json"` và ghi danh sách lỗi.
2. Với mỗi việc `done` thiếu evidence, tìm bằng chứng thật. Nếu tìm thấy, chạy `set-status <ID> done --evidence "<bằng chứng>" --apply`. Nếu không thấy, chạy `set-status <ID> doing --apply` để kiểm lại.
3. Với yêu cầu không trỏ việc, sửa chuỗi `items` bằng Edit. Không có lệnh cho việc này. Không sửa trường giờ bằng Edit.
4. Chạy lại lint tới khi 0 lỗi.
5. Chạy `build.py --slug <project>` ở chế độ dry-run. Bản `--apply` ghi đè file HTML và MD do build cũ dựng, nên kiểm dry-run trước.
6. Giữ `build.py` cũ trong thư mục instance. Không xoá.
