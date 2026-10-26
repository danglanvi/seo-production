# Định tuyến query → URL (pha E2)

File này ghi cách đọc kết quả `retrieval-lab route` cho bộ keyword cam kết. Gốc đường dẫn là root repo. Nạp ở pha E2 của `query-processing-diagnosis` và Bước 2b của `keyword-topic-url-mapping`.

## 1. Đầu vào

- GSC query × page 90 ngày: export vào `02-raw/seo-data/keywords/`. File chỉ xử lý local.
- Store của site: skill `site-vector-index`, prompt `Document`, cùng model với query.
- `--candidates`: danh sách URL cùng ngôn ngữ với query. Thiếu danh sách này thì trang `/en/` có thể thắng query tiếng Việt.
- URL Google chọn:
  - Có `hang.tsv` của `qp_ranks.py`: truyền `--chosen-col url`. URL lấy từ SpySERP, khớp số hạng trên deck.
  - Không có: `gsc_route.py prep` lấy trang có nhiều hiển thị nhất trong GSC.

## 2. Đọc verdict

| Verdict trong `tom-tat.tsv` | Nghĩa | Việc tiếp |
|---|---|---|
| `khớp` | Trang Google chọn cũng là trang gần query nhất | Không đổi URL. Tìm trạm hỏng ở chỗ khác |
| `Google chia query` | Gemma chọn khác, `share` < 0,6 | Ứng viên cannibalization. Đọc 2 trang, xem GSC theo ngày trước khi đề xuất gộp hay chỉnh |
| `Google chọn URL khác` | Gemma chọn khác, `share` ≥ 0,6 | Google ổn định chọn URL khác URL khớp nội dung nhất. Kiểm link nội bộ và anchor trước khi sửa chữ |
| `Gemma chọn URL khác, chưa có share GSC` | URL lấy từ SpySERP, GSC không có query | Đọc 2 trang. Ghi "cần GSC" |
| `chưa có dữ liệu GSC` | Không có URL Google chọn | `gemma_top` là trang nên đọc đầu tiên khi gán URL |
| `URL Google chọn không có trong store` | Store thiếu trang, hoặc trang khác ngôn ngữ | Dựng lại store hoặc kiểm `--candidates` |

- Cổng `share` 0,6 lấy từ skill `retrieval-lab`. Không đặt ngưỡng cosine mới ở đây.
- Mọi verdict khác `khớp` là giả thuyết. Deck ghi chữ đỏ, kèm tên 2 trang đã đọc.

## 3. Số đo trên site mẫu (19/10/2026)

Site mẫu ngành dịch vụ SEO, GSC 90 ngày, store 343 trang, 333 trang tiếng Việt làm candidates.

| Tập query | Top-1 trùng Google | Top-3 |
|---|---|---|
| 4.718 query ≥ 20 hiển thị, mọi chủ đề | 75,5% | 89,0% |
| 781 query thuộc 11 template của trang tiền | 29,3% | 51,6% |

- Template địa phương và template dịch vụ con khớp cao: 92,3% và 87,9% hiển thị có Gemma top-1 trùng URL Google chọn.
- Template tiền chính khớp thấp: "dịch vụ seo" 2,5% hiển thị, "công ty seo" 33%. Google dồn query về trang dịch vụ chính, còn Gemma chọn bài viết chứa cùng cụm từ.
- Cách đọc: query tiền đặt URL theo Google và theo kế hoạch. Định tuyến Gemma chỉ chỉ ra trang nào đang cạnh tranh nội dung với trang tiền.
- Đây là chỉ số mô phỏng. Báo cáo khách ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
