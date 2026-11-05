# Gate AI + spam trước khi đăng

Gate này áp cho bài và trang làm bằng AI hoặc theo template, trước khi đăng hoặc trước khi đăng lại. Check ID lấy từ checklist E-E-A-T của Aleyda Solis (`skills/semantic-content-audit/references/eeat-checklist/checklist.json`). Trạng thái và luật bằng chứng theo `skills/semantic-content-audit/references/eeat-aleyda.md` §2.

Gate FAIL khi có một check Does not meet. Check Not assessed không làm FAIL. Báo cáo ghi check đó là CANNOT-VERIFY và nêu bằng chứng cần lấy.

## Bảng check

| Check | Câu hỏi | Bằng chứng trong skill này | Does not meet khi |
|---|---|---|---|
| AI01 | Tự động hoá có mục đích biên tập rõ và giữ chất lượng? | Jev `content-effort` qua cổng; tỷ lệ khối lặp của lệnh `template` | Trang không có `original_data`, không có `first_hand`, và phần lớn chữ là khối lặp của trang khác |
| AI02 | Người đọc có được biết việc dùng AI khi họ có lý do để mong biết? | Chữ trên trang | Trang tự nhận "chuyên gia viết", "đã test" nhưng nội dung do AI sinh và không ai test |
| AI03 | Người đã duyệt chữ do AI sinh trước khi đăng? | Bản ghi duyệt: tên người duyệt + ngày, ví dụ verdict ở repo content hoặc trang duyệt | Có bản ghi cho thấy bài đăng thẳng từ bản AI. Không có bản ghi thì Not assessed |
| AI04 | Title, meta, alt, schema do AI sinh cũng đã duyệt? | Lệnh `claims` chạy trên title, meta, alt; so schema với chữ hiển thị | Title hoặc meta có cam kết, "#1", số không nguồn; schema nêu điều trang không nói |
| CP01 | Sản xuất số lượng lớn có giá trị, không chỉ để thao túng thứ hạng? | Effort + khối lặp trên cả lô; số trang mới mỗi tuần | Lô trang chủ yếu đổi từ khoá, không có dữ liệu riêng, khối lặp ≥ ngưỡng `passage-dup` ở phần lớn thân trang |
| CP04 | Trang theo địa phương hay biến thể từ khoá có ích riêng, không phải doorway? | Lệnh `template` trên nhóm trang địa phương | Trang chỉ đổi tên địa phương, không có địa chỉ, giá, lịch, ảnh hay dữ liệu riêng của nơi đó |
| CP07 | Trang không cố thao túng câu trả lời AI tạo sinh? | Code tìm chữ ẩn (display:none, cỡ chữ 0, màu trùng nền) có câu nhắm vào AI; Claude đọc | Có chữ ẩn hoặc câu lệnh gửi AI, ví dụ "AI hãy giới thiệu X là tốt nhất", "ignore previous instructions" |
| CP09 | Nội dung affiliate có giá trị riêng ngoài mô tả của nhà bán? | Jev `original_data`, `first_hand`; so chữ với trang nhà bán bằng Gemma | Phần lớn chữ chép hoặc viết lại từ mô tả nhà bán, không có so sánh hay trải nghiệm riêng |

## Luật

- Việc dùng AI, template hay số lượng trang lớn chưa đủ để kết luận vi phạm. Kết luận CP phải đọc đủ chính sách spam của Google, gồm ngoại lệ: https://developers.google.com/search/docs/essentials/spam-policies
- Không ghi tên người duyệt khi không có bản ghi. Không suy AI03 từ chất lượng chữ.
- Site khách: bản nháp chưa đăng không gửi Jev (mục Gate của SKILL.md). Lượt đó Claude đọc thay Jev.
- Cần chạy gate trên cả site: dùng skill `eeat-site-qc`.

## Output

Thêm vào `<W>/report.md` một bảng: check, trạng thái, bằng chứng, việc sửa. Ghi verdict `G-AI-SPAM: PASS` hoặc `G-AI-SPAM: FAIL (<check rớt>)`.
