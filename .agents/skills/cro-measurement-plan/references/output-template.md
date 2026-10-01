# Template output — measurement plan và tracking QA

Mục đích: khung `<CLIENT>_measurement-plan_v<N>.md` (phần A–G) và `<CLIENT>_tracking-qa_v<N>.md`. Trong SEO Production, frontmatter theo chuẩn `_TEMPLATES/` của repo; ngoài repo dùng frontmatter dưới.

## Measurement plan

```md
---
client: "<CLIENT>"
cong_doan: 34
ws: 13-cro
pic: "<SEO Lead Project · CRO>"
duyet: "<SEO Leader>"
status: draft | plan-handed-over | qa-passed
version: v1
---

# <CLIENT> — Kế hoạch đo chuyển đổi

> Naming `<CLIENT>_measurement-plan_v<N>.md` → `13-cro/`. Item CR-06/CR-07 (gate G1). Skill `cro-measurement-plan`. Nếu ≤5 event, nhúng vào §1 conversion-path.

## A. Outcome & mẫu số
| Cơ chế | Outcome (client chốt ngày …) | Micro | Guardrail | Metric: tử số / mẫu số / đơn vị / population / dedup | Cửa sổ |
|---|---|---|---|---|---|

Gọi/chat không join được với user web → ghi hai số riêng (click; lead đối soát), không công bố CVR user.

## B. Event contract
| Event | Trigger | Nguồn xác nhận | Tham số | Chống trùng | Consent | Owner |
|---|---|---|---|---|---|---|

## C. Spec GTM (bàn giao dev/khách)
Inventory DOM → trigger/tag/biến → dataLayer push → quy trình kiểm (theo references/gtm-spec.md). Trạng thái từng dòng: chờ dev / đã làm / đã kiểm.

## D. Kênh AI Assistant
Cấu hình custom channel group (rule, thứ tự), 4 điểm mù, câu hỏi nguồn biết ở form/sale. Bỏ phần này nếu client không có GEO và <30 session AI/tháng — ghi lý do.

## E. Đối soát
Nguồn outcome · cột Sheet lead tối thiểu · cửa sổ · ngưỡng lệch (lý do) · lịch đối soát (tuần/tháng) · ai làm.

## F. Ca QA
Bảng Q1–Q20 rút theo cơ chế của site; cột Kết quả = plan cho tới khi chạy; ca không thuộc cơ chế ghi N/A + lý do. Gate G1 PASS = mọi ca P0 của cơ chế primary PASS (reconciliation-qa §3).

## E2. Quota tham số
| Parameter | Scope | Cần đăng ký custom dimension? | Quota còn lại (event 50 / user 25 / item 10, Standard) |
|---|---|---|---|

## G. Trạng thái & owner
| Việc | Owner | Deadline | Trạng thái |
|---|---|---|---|
| Dev gắn GTM theo §C | | ≤ T3 | |
| GTV kiểm Preview/DebugView | | | |
| Sheet lead / CRM cột nguồn | | | |
| Custom channel group AI | | | |
| Đối soát kỳ đầu | | +7/+14 ngày | |

Chưa xác minh: <liệt kê>.
```

## Tracking QA

```md
---
client: "<CLIENT>"
cong_doan: 34
ws: 13-cro
status: qa-run
version: v1
---

# <CLIENT> — Kết quả QA tracking <ngày>

Môi trường: iOS <ver> Safari · Android <ver> Chrome · macOS Chrome <ver>. Người chạy: <tên>. Container version: <n>.

| # | Ca | Thiết bị | Kết quả | Bằng chứng (screenshot DebugView, che PII) | Ghi chú |
|---|---|---|---|---|---|

## Đối soát 7 ngày đầu
| Kênh | GA4 | Nguồn outcome | Lệch | Nguyên nhân | Hành động |
|---|---|---|---|---|---|

## Kết luận gate G1
PASS / FAIL — điều kiện: mọi ca P0 **thuộc cơ chế primary của site** PASS (Q4, Q4b, Q5, Q6, Q7, Q19, Q20 luôn; Q10–Q12 khi ecommerce; Q13/Q14 khi job; Q1/Q3 khi gọi/Zalo là primary); ca khác ghi N/A + lý do; lệch đối soát có nguyên nhân hoặc ghi "chưa xác định" (không là điều kiện PASS). FAIL → danh sách sửa + ngày kiểm lại.
```
