# Chọn loại media cho từng khung

## Loại và trường trong media_plan.json

| `loai` | Dùng khi | Trường cần thêm | Script |
|---|---|---|---|
| `so-do` | Quan hệ, quy trình, quyết định, so sánh, mốc thời gian, số liệu có nguồn | `so_do` (spec ở `so-do-spec.md`) → script ghi `svg`, `svg_m` | `svg_dung.py`, `svg_kiem.mjs` |
| `anh-chup` | Bài trích chữ của một trang nguồn: tài liệu Google, tài liệu API, kết quả công cụ | `src` (WebP đã xử lý) | `chup_trang.mjs`, `anh_chu_thich.py` |
| `anh-that` | Người, nơi, sự kiện, sản phẩm thật của brand | `src`, quyền dùng | `anh_chu_thich.py --nguon anh-that` |
| `anh-ai` | Minh hoạ khái niệm không có ảnh thật, không có chữ, không có người | `prompt` (file JSON), `src` sau khi tạo | `anh-ai.md`, `anh_chu_thich.py --nguon ai` |
| `tuong-tac` | Người đọc tự chấm, tự tính, tự kiểm | `html`, `css`, `caption_duoi` (tuỳ chọn) | `wp-xuat-ban-bai/references/khoi-doc-kit.md` |
| `video` | Video sở hữu giải thích đúng H2 | `youtube` (id) hoặc `src` MP4 + `poster` | `chen_media.py` (facade) |

Mọi mục có `id`, `vi_tri`, `alt`, `caption`, `ten_file` (chữ thường không dấu, nối bằng gạch ngang), `trang_thai`.

## Chọn theo nội dung của H2

| H2 nói về | Loại nên dùng |
|---|---|
| Định nghĩa trích từ tài liệu chính thức | `anh-chup` đoạn định nghĩa, tô câu chính |
| Nhiều khái niệm dễ lẫn | `so-do` kiểu `khoi` có quan hệ |
| Quy trình có thứ tự | `so-do` kiểu `luong`; 6 bước trở lên dùng `mot_hang` hoặc `nhom` |
| Một câu hỏi rẽ hai hướng | `so-do` kiểu `quyet-dinh` |
| So sánh 2–3 phương án | bảng `.tbl` trước; `so-do` kiểu `so-sanh` khi mỗi cột ngắn |
| Số liệu từ nghiên cứu | `so-do` kiểu `cot`, có `nguon` |
| Diễn biến theo thời gian | `so-do` kiểu `moc` |
| Cách làm có thể tự chấm | `tuong-tac` dùng `.calc` hoặc `.bchk` |

Khung trong bảng placeholder ghi "diagram" nhưng nội dung là định nghĩa trích nguyên văn: đổi sang `anh-chup`. Bằng chứng gốc thuyết phục hơn hình vẽ lại.

## Ảnh chụp trang nguồn

- Chụp ở `--rong 640`, thu về 1200 px. Chữ trong ảnh còn khoảng 13 px trên điện thoại.
- `--chua` là một đoạn chữ có thật trong khối cần chụp. Script tìm khối nhỏ nhất chứa đoạn đó.
- `--to` là câu cần tô vàng. Script so theo từ, bỏ qua xuống dòng trong mã nguồn.
- `--khoi p|section|table|li` chọn thẻ của khối. `--them N` lấy thêm N khối liền sau.
- `--an "<selector>"` ẩn banner, thanh dính. Script tự ẩn header cố định và hộp cookie.
- Trang song ngữ: chụp 2 bản rồi ghép dọc bằng `anh_chu_thich.py` (bản gốc trên, bản dịch dưới). Caption nói bản nào ở trên.
- Caption ghi tên trang và ngày chụp. Script in ngày chụp trong dòng JSON cuối.
- Ca thật 27/10/2026: trang tài liệu Google tự chuyển sang bản dịch (thêm `?hl=en`), và giấu đoạn cần chụp trong khối thu gọn. Script mở khối thu gọn và so chữ theo NFC.

## Trạng thái

| `trang_thai` | Nghĩa |
|---|---|
| `can-dung` | Chưa dựng |
| `xong` | Có file, đã xem, đã kiểm |
| `ready_to_generate` | Ảnh AI đã có prompt, chưa có công cụ tạo ảnh |
| `needs_capture` | Cần người có quyền chụp (trang sau đăng nhập) |
| `needs_source` | Chưa có ảnh thật hoặc chưa có quyền dùng |
