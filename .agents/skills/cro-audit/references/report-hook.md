# Report hook — đưa CRO vào §3 báo cáo tháng để khách thấy giá trị

Mục đích: bước 6 của cro-audit. CRO là add-on để tái ký: khách phải thấy mỗi tháng GTV phát hiện gì, sửa gì, số ra sao. Mục §3 "Các dữ liệu báo cáo khác (CRO)" của skill `gtv-client-report` v1.4 có **4 khối tổng cộng**: 3a bảng chuyển đổi (từ measurement plan) + **3 khối WS13 cấp thêm** (3b phát hiện · 3c việc đã sửa + số quan sát · 3d chờ phía khách). Nối 3b/3c/3d bằng **finding ID**, không chép lại nội dung. v1.1 (13/09/2026, sau review Astra F02/S01/S03).

## §1. 3a — Chuyển đổi kỳ này (từ measurement plan, đúng nhãn)

| Cơ chế | Micro (GA4 đã QA) | Outcome đối soát (nguồn, độ trễ) | Kỳ trước |
|---|---|---|---|
| Gọi / Zalo / Messenger | click_to_call · click_zalo (đếm) | Lead đạt chuẩn từ Sheet sale (đếm) — hai số riêng, không join | |
| Form / báo giá | user có ≥1 generate_lead / user đủ điều kiện | Lead đạt chuẩn / báo giá đã gửi (cohort +7 ngày) | |
| Đơn hàng | user có ≥1 purchase / user vào PDP+giỏ (đơn tạo) | Đơn hợp lệ sau 14 ngày (backend) | |
| Apply / ATS (khi cơ chế job) | application_complete / apply_start (candidate–job) | Hồ sơ đạt chuẩn từ HR (theo SLA) | |
| Từ AI Assistant | session kênh AI · CVR một outcome đã chốt, cùng population với Organic | (directional — phần nhận diện được, có điểm mù; là phân đoạn của các hàng trên, **không cộng vào tổng**) | |

Metric ghi đúng dạng tử số/mẫu số/đơn vị (event-contracts §1). Tracking chưa PASS → "Kế hoạch đo đã bàn giao ngày …, chờ dev; số kỳ này chưa dùng để kết luận."

## §2. 3b — Phát hiện kỳ này (E≥2, tối đa 5 dòng, P0 trước)

| ID | Trang/template | Phát hiện (ảnh đính kèm, che PII) | Mức | Đề xuất | Trạng thái |
|---|---|---|---|---|---|
| F-07 | Checkout mobile | Cổng VNPay quay về trang trắng trên iOS 17 (tái hiện 3/3) | P0 | Trang quay về đọc trạng thái từ backend | Đã brief 05/09 → chờ dev |

Không đưa E1. Chỉ finding mới trong kỳ; finding cũ còn mở nằm ở 3d.

## §3. 3c — Việc đã sửa và số quan sát (chỉ mốc GTV QA PASS)

| ID | Việc | Ngày QA PASS | Metric (tử/mẫu) | Trước (cửa sổ) | Sau (cửa sổ) | Ghi chú |
|---|---|---|---|---|---|---|
| F-02 | Form tư vấn: label cố định + success state | 12/08 | user có ≥1 generate_lead / user vào trang dịch vụ | 1,8% (15/07–11/08) | 2,3% (13/08–09/09) | Quan sát trước/sau, cùng mẫu số; tháng 8 có thêm 2 bài blog top 3 |

Cùng mẫu số, cùng độ dài cửa sổ, nhãn "quan sát"; cột Ghi chú nêu yếu tố khác đã đổi. Chưa đủ cửa sổ → "đang theo dõi tới <ngày>". Không ghi "tăng 28% nhờ GTV".

## §4. 3d — Chờ phía khách (mọi P0 còn mở + brief chưa triển khai)

| ID | Brief | Ngày gửi | Tuổi lỗi (ngày) | Mức | Ảnh hưởng nếu chưa làm | Cần gì từ khách |
|---|---|---|---|---|---|---|
| F-07 | Sửa trang quay về VNPay | 05/09 | 38 | P0 | Đơn thanh toán online không hoàn tất trên iOS | Dev 4 giờ |
| F-11 | Chuẩn hoá `tel:` + Zalo OA | 20/08 | 24 | P1 | Không đối soát được cuộc gọi từ web | Dev 2 giờ; quyết định dùng OA |

P0 không rời khỏi 3d cho tới khi GTV QA PASS. Khối này là bằng chứng GTV đã làm phần mình và giúp Account nói chuyện tiến độ. Không gộp 3b vào 3d (3b = mới, 3d = tồn đọng cần quyết).

## §5. Câu chữ

- Dùng: "phát hiện", "đã sửa (QA PASS)", "quan sát trước/sau", "chờ phía khách", "cần thêm dữ liệu", "đang theo dõi tới".
- Không dùng: "uplift", "tăng X% nhờ", "best practice", "đảm bảo", số benchmark ngoài làm mục tiêu, "số nhìn thấy là sàn".
- Khi không có gì mới: "không phát hiện mới; đang theo dõi F-xx tới <ngày>" — vẫn có mặt trong report.

## §6. Chuẩn bị trước kỳ

SEO/CRO cung cấp cho Account trước ngày report: bảng 3a đã QA, evidence-backlog có ID và trạng thái, ảnh đã che PII. Account chỉ tổng hợp. "30 phút" chỉ đúng khi dữ liệu đã chuẩn bị; đo thời gian thật ở pilot đầu trước khi hứa.

## §7. Nguồn số

GA4 (event đã QA), Sheet lead/CRM (outcome), backend đơn, ATS; ảnh từ Clarity/Hotjar che PII. Không dùng số từ evidence-backlog E1 hay từ recording lẻ làm tỷ lệ.
