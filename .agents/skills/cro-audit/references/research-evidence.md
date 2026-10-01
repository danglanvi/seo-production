# Research và bằng chứng — thu thập, gắn nhãn, viết finding

Mục đích: bước 2 của cro-audit. Nguồn: wiki Inbound Marketing `concepts/cro/foundations` (ResearchXL, phân loại bằng chứng), `patterns/scorecard`; tóm tắt để skill chạy standalone.

## §1. Năm nguồn research và câu hỏi của từng nguồn

| Nguồn | Câu hỏi | Bằng chứng đầu ra | Ghi chú |
|---|---|---|---|
| Technical | Hành động có hoàn tất trên iOS Safari, Android Chrome, desktop không? | Ca tái hiện: bước, thiết bị, kết quả, ảnh | Làm đầu tiên; ra blocker P0 nhanh nhất |
| Analytics | Mất người ở đâu, nhóm nào? | Funnel có mẫu số, cửa sổ, phân đoạn (thiết bị, kênh, mới/quay lại, loại trang) | Chỉ tin khi tracking đã QA; chưa QA → ghi "số chưa tin cậy" |
| Heuristic theo pattern | Trang có đủ thông tin/điều khiển cho task không? | Danh sách nghi ngờ gắn nhãn E1 | Không tự thành finding; cần một nguồn khác xác nhận |
| Recording / heatmap | Người dùng gặp gì trên đường thao tác? | Recording ID, trang/version, hiện tượng, event/error đi kèm | Heatmap = *ở đâu*; recording = *chuỗi hành vi*; cả hai không nói *vì sao* |
| VOC | Khách hỏi gì, do dự gì? | Câu hỏi lặp từ sale/Zalo/support, lý do lost, review | Rẻ nhất với SME; hỏi sale 30 phút thường ra 3–5 giả thuyết mạnh |

Usability test nhỏ (3–5 người đúng tệp làm task) dùng khi cần xác nhận giả thuyết mà không có traffic; ghi là nghiên cứu, không phải số đại diện.

## §2. Nhãn bằng chứng và cách nâng nhãn

| Nhãn | Đủ để | Nâng lên bằng |
|---|---|---|
| E3 — lỗi tái hiện được / số có mẫu số | Xác nhận hiện tượng hoặc tỷ lệ mô tả; brief, report. **Không** tự xác nhận nguyên nhân hay tác động của sửa đổi — uplift chỉ qua test contract | — |
| E2 — ≥3 recording cùng hiện tượng / ≥100 session heatmap trên trang / VOC lặp ≥3 nguồn độc lập | Giả thuyết mạnh, brief sửa, report ghi "quan sát" | Tái hiện lỗi; funnel có mẫu số |
| E1 — heuristic, pattern ngoài | Backlog "cần kiểm" | Recording, VOC, tái hiện |

Không nâng E1 lên E2 bằng cách mô tả kỹ hơn. Rage click / dead click là tín hiệu điều tra: xác nhận bằng tái hiện (phần tử không phản hồi?) hoặc VOC.

## §3. Đọc recording/heatmap cho đúng

- Phân đoạn trước khi xem: loại trang, thiết bị, kênh vào, mới/quay lại. Xem cả phiên thành công lẫn thất bại; không chỉ phiên tool đánh dấu.
- Ghi sampling: số phiên đủ điều kiện, số đã xem, cửa sổ, những gì mất do consent/tracking.
- Ngưỡng ≥3 recording / ≥100 session là mức vận hành, không cho phép suy tỷ lệ phổ biến. "3/3 recording mobile gặp lỗi X, đã tái hiện" là E3; "3 recording cho thấy đa số khách bỏ vì form" là sai.
- Screenshot heatmap/recording che mọi dữ liệu cá nhân; lưu theo protocol screenshot của repo.
- Không dùng người dùng giả lập bằng AI thay nghiên cứu với khách thật.

## §4. Format finding (bắt buộc, dùng cho evidence-backlog và heatmap-review)

```
ID · Trang/template · Cơ chế
Quan sát: <số + mẫu số + cửa sổ + nguồn | hoặc bước tái hiện + thiết bị>
Nhãn: P_ (dự kiến) R_ E_ · trạng thái bằng chứng: đã xác nhận / cần xác minh
       (P0 chặn / P1 cản / P2 cải thiện · R3 site-wide / R2 landing ưu tiên / R1 một trang)
Cách diễn giải khác: <ít nhất 1>
Giả thuyết: <vì sao mất outcome>
Action: <component, thay đổi, trạng thái>
Metric theo dõi: <event/outcome, cửa sổ ≥4 tuần, "quan sát">
Item SOP: CR-xx / UX-xx · Pattern: <§>
Owner · deadline triển khai · trạng thái (đề xuất / khách duyệt / đã sửa / chờ khách)
```

## §5. Xếp ưu tiên

1. Thứ tự tường minh: **P0 → P1 → P2; cùng P: R3 → R2 → R1; cùng R: E3 → E2**; hoà hoàn toàn → effort thấp trước (copy/CSS < component < flow/backend). P0 báo bất kể ranking.
2. Mức nặng dự kiến và bằng chứng độc lập: **nghi P0 mới E1 → giữ P0, trạng thái "cần xác minh"**, việc tái hiện được ưu tiên trước mọi P1 đã chắc; không hạ xuống P2 cho tiện xếp.
3. E1 ở backlog "cần kiểm" với cách kiểm và người kiểm; không vào report.
3b. Kiểm sort bằng 6 finding giả lập gồm P1 effort cao và P2 effort thấp: P1 vẫn đứng trước.
4. Không quy đổi thành điểm số × uplift dự đoán. Không xếp theo "drop-off lớn nhất" đơn thuần: bước qualification cố ý loại người không phù hợp.

## §6. Không nhập thành "best practice"

Median CR của Unbounce, % thiếu sót Baymard, "native apply 4×", "form ≤4 field", "≤3 click", "1 CTA" — là gợi ý để đặt câu hỏi, không phải chuẩn pass/fail. Số của client thay cho benchmark ngoài. Không lấy word count/reading grade tiếng Anh làm quota tiếng Việt.
