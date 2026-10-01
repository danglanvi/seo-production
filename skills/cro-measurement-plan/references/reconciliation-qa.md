# Đối soát outcome và ca QA

Mục đích: phần E và F của measurement plan. Số GA4 chỉ có giá trị khi đối chiếu được với nơi outcome thật được ghi. QA chưa chạy = "plan"; chạy rồi = ngày, người, môi trường, kết quả từng ca. v1.1 (13/09/2026, sau review Astra F04/F05): ca không thuộc cơ chế của site ghi **N/A + lý do**; gate PASS theo cơ chế primary; ngưỡng lệch là đề xuất chờ kiểm, không phải điều kiện PASS.

## §1. Nguồn đối soát theo cơ chế

| Cơ chế | GA4 (micro) | Nguồn outcome | Khớp bằng | Nguyên nhân lệch thường gặp |
|---|---|---|---|---|
| Gọi | `click_to_call` | Nhật ký cuộc gọi điện thoại/tổng đài; Sheet lead do sale ghi | Cửa sổ ngày + giờ; không có id chung → **hai số riêng**, không tính CVR user | Bấm không gọi; gọi từ số thấy trên GBP; sale không ghi |
| Zalo/Messenger | `click_zalo`, `click_messenger` | Hộp thư Zalo OA / inbox fanpage; Sheet lead | Ngày + giờ; OA có thống kê người theo dõi mới | Bấm mở app rồi không nhắn; nhắn từ tìm kiếm Zalo trực tiếp |
| Form | `generate_lead` | Email nhận form; CRM; Sheet lead | `form_id` + timestamp; CRM có `lead_id` | Form gửi lỗi vẫn bắn (sai spec); spam; consent/ad-block chặn GA4 |
| Báo giá | `generate_lead` (`lead_type=quote`) | Sheet báo giá | Mã yêu cầu | Khách gửi file qua Zalo không qua form |
| Đơn hàng | `purchase` | Backend đơn (WooCommerce/Haravan/Sapo/KiotViet) | `transaction_id` | Consent/ad-block; cổng thanh toán quay về không nạp GTM; đơn tạo tay bởi sale; COD bom |
| Apply | `application_complete` | ATS / DB ứng tuyển | `application_id` (giữ ở backend) | Offsite không callback; nộp qua email/Zalo theo JD |

## §2. Cửa sổ, ngưỡng, cột tối thiểu

- **Cửa sổ:** so cùng khoảng ngày, timezone Asia/Ho_Chi_Minh; outcome chậm (lead → đạt chuẩn, đơn → hợp lệ) dùng cohort theo ngày phát sinh, đọc sau ≥7 ngày (lead) / ≥14 ngày (đơn COD) / theo SLA HR (apply).
- **Ngưỡng lệch:** là quyết định của dự án, ghi lý do, và **không phải điều kiện PASS gate G1** (G1 PASS theo ca QA §3). Gợi ý để bàn với client, chờ kiểm bằng baseline thật: GA4 thấp hơn backend là hướng lệch thường gặp khi có consent/ad-block (mức tuỳ site, không có dải chung); GA4 **cao hơn** backend là dấu hiệu sai spec (bắn ở click, bắn trùng). Không viết "chính xác 95%". "Không thấy banner" không đủ để loại consent khỏi nguyên nhân — ghi cấu hình consent thật (không có / basic / advanced).
- **Sheet lead tối thiểu** (khi client không có CRM): `thời điểm` · `kênh` (gọi/Zalo/Messenger/form/báo giá) · `nguồn` (web/ads/giới thiệu/khác — sale hỏi khách) · `trang` (nếu form có) · `nhu cầu` · `kết quả` (đạt chuẩn / không / chưa liên lạc được) · `ngày phản hồi đầu` · `chốt` (có/không/đang). GTV chỉ nhận bản đếm hoặc bản đã che.
- **Bảng đối soát mẫu:**

| Kỳ | Kênh | GA4 micro | Outcome nguồn | Lệch | Nguyên nhân đã xác định | Hành động |
|---|---|---|---|---|---|---|
| 01–31/… | Zalo | 412 click | 96 đoạn chat có nhu cầu | — (khác đơn vị, không join được) | Ghi tỷ lệ 23% làm baseline nội bộ, không gọi là CVR user | Theo dõi theo tháng |
| 01–31/… | Form | 58 `generate_lead` | 61 email nhận | −5% | 3 form gửi khi GA4 bị chặn (ad-block, đã kiểm) | Chấp nhận |
| 01–31/… | Đơn | 240 `purchase` | 205 đơn backend | +17% | Reload trang cảm ơn bắn lại | Sửa chống trùng, kiểm lại |

## §3. Ca QA

Chạy trên iOS Safari, Android Chrome, desktop Chrome; ghi thiết bị/phiên bản. Kết quả: **PASS / FAIL / plan / N/A (+ lý do)**. Ca không thuộc cơ chế của site (site chỉ gọi/Zalo không có checkout, apply) ghi N/A; **gate G1 PASS = mọi ca đánh dấu P0 thuộc cơ chế primary của site PASS** và không còn ca P0 ở trạng thái plan.

| # | Ca | Thao tác | Kỳ vọng | P0? |
|---|---|---|---|---|
| Q1 | Gọi | Bấm nút gọi header, hero, sticky, footer | Mỗi lần 1 `click_to_call` với `position` đúng; mobile mở dialer đúng số | P0 khi gọi là cơ chế primary |
| Q2 | Gọi desktop | Bấm trên desktop | Có event dù OS không mở app; không lỗi JS; có số/QR/Zalo thay thế | — |
| Q3 | Zalo | Bấm từng dạng nút (link, OA, plugin) | 1 `click_zalo`/click; mở đúng OA/số; `zalo_target` đúng | P0 khi Zalo là primary |
| Q4 | Form thành công | Điền đúng, gửi | 1 `generate_lead`; success state; lead tới đích trong 10 phút | P0 |
| Q4b | HTTP 200 + nghiệp vụ thất bại | Gửi ca backend trả `success:false` / `action_required` (giả lập trên test) | **Không** `generate_lead`; thông báo đúng | P0 |
| Q5 | Form lỗi validation | Thiếu SĐT, gửi | `form_error` (nếu có), **không** `generate_lead`; dữ liệu giữ nguyên | P0 |
| Q6 | Double click | Bấm gửi 2 lần nhanh | 1 lead ở đích, 1 event (idempotency backend và analytics kiểm riêng) | P0 |
| Q7 | Reload success | Reload trang/khối cảm ơn | Không bắn lại | P0 |
| Q7b | Nhiều tab / storage không khả dụng / tag bị chặn | Mở 2 tab; tắt storage; bật ad-block | Không đếm trùng; không mất lead backend; ghi mức lệch GA4 | — |
| Q8 | Form iframe | Gửi form nhúng | Có event qua callback/redirect, hoặc ghi "không đo được" | — |
| Q9 | Add to cart | Thêm với/không variant | `add_to_cart` đủ `items`; thiếu variant → lỗi inline, không event | N/A nếu không ecommerce |
| Q10 | Checkout COD | Đặt COD | `purchase` 1 lần, `payment_type=cod`, `transaction_id` = mã đơn backend | P0 (ecommerce) |
| Q11 | Cổng thanh toán | Thành công; huỷ giữa chừng; Back từ cổng | Thành công: 1 `purchase` ở trang quay về; huỷ/Back: không `purchase`, giỏ còn | P0 (ecommerce) |
| Q12 | Đơn trùng | Reload order-received, mở lại link | Không event mới | P0 (ecommerce) |
| Q13 | Apply onsite | Nộp CV PDF từ mobile | `application_submit` rồi `application_complete`; ATS nhận | P0 (job onsite) |
| Q14 | Apply offsite | Bấm ứng tuyển rời site | `apply_start` với `apply_type=offsite`, `job_id`; không `application_complete` | P0 (job offsite) |
| Q15 | Consent | Theo cấu hình thật: không consent mode / basic / advanced; từ chối rồi thao tác | Hành vi đúng cấu hình (basic: không tag; advanced: ping không cookie); ghi để giải thích lệch | — |
| Q16 | Cross-domain/SPA | Chuyển trang không reload; subdomain checkout | Session không đứt; event vẫn có tham số | — |
| Q17 | Bot/nội bộ | IP văn phòng, GTM Preview | Đã loại khỏi property (internal traffic filter) | — |
| Q18 | Kênh AI | Mở link từ ChatGPT (web) tới site; kiểm 1 source thật với regex (positive/negative) | Session vào kênh AI Assistant/AI Traffic; regex không bắt nhầm | — |
| Q19 | PII | Xem payload mọi event | Không SĐT/email/tên/nội dung field/CV/ID cardinality cao | P0 |
| Q20 | Key events + quota | GA4 Admin → Key events, Custom definitions | Đúng danh sách plan; counting method đã chốt; bảng quota dimension đã điền | P0 |

## §4. Ngôn ngữ trong report

- "Click Zalo" không phải "lead Zalo"; "đơn tạo" không phải "doanh thu" khi có COD; "hồ sơ hoàn tất" chỉ khi ATS xác nhận. Gọi/chat không join được với user → hai số riêng, ghi giới hạn attribution.
- Số kênh AI: "directional; phần AI referral nhận diện được, có điểm mù attribution", không nghiệm thu; không cộng vào tổng conversion lần nữa.
- Khi QA chưa chạy: "Kế hoạch đo đã bàn giao, chờ dev triển khai; số kỳ này chưa dùng để kết luận."
- Khi lệch chưa giải thích được: ghi "chưa xác định nguyên nhân", không làm tròn cho khớp.
