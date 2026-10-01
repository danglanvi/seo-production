---
client: "{{CLIENT}}"
cong_doan: 34
ws: 13-cro
pic: "{{SEO Lead Project · CRO}}"
duyet: "{{SEO Leader}}"
status: draft
version: v1
---

# {{CLIENT}} — Kế hoạch đo chuyển đổi

> Naming `{{CLIENT}}_measurement-plan_v{{N}}.md` → `13-cro/`. Item CR-06/CR-07 (gate G1, ≤ T3). Skill `cro-measurement-plan`. Site chỉ có 1 cơ chế và ≤5 event → nhúng vào §1 của `conversion-path` thay vì tách file. Trạng thái QA chưa chạy ghi **plan**, không ghi PASS.

## A. Outcome & mẫu số

| Cơ chế | Outcome (client chốt ngày …) | Micro-event | Guardrail | Metric: tử số / mẫu số / đơn vị / population / dedup | Cửa sổ |
|---|---|---|---|---|---|
| {{gọi/Zalo · form · báo giá · giỏ hàng · apply}} | {{lead đạt chuẩn / đơn hợp lệ / hồ sơ hoàn tất}} | {{click_to_call, generate_lead, purchase…}} | {{spam, bom COD, trùng…}} | {{user có ≥1 outcome / user đủ điều kiện (cùng population ở tử và mẫu)}} | {{tháng, Asia/Ho_Chi_Minh}} |

Gọi/chat không join được với user web → hai số riêng (click; lead đối soát), không công bố CVR user. Không cộng nhiều key event chia session.

## B. Event contract

| Event | Trigger | Nguồn xác nhận outcome | Tham số (không PII) | Chống trùng | Consent | Owner |
|---|---|---|---|---|---|---|
| {{generate_lead}} | {{dataLayer sau response 200}} | {{CRM / Sheet lead}} | {{form_id, lead_type, page_type}} | {{token form}} | {{banner? tỷ lệ từ chối ước tính}} | {{Dev khách}} |

## C. Spec GTM (bàn giao dev/khách)

Container: {{GTM-…}}. Inventory DOM → trigger/tag/biến → dataLayer push → quy trình kiểm (Preview + DebugView). Trạng thái từng dòng: chờ dev / đã làm / đã kiểm.

| Điểm chuyển đổi | Dạng DOM | Bắt bằng | Ghi chú |
|---|---|---|---|
| {{nút gọi header}} | {{`<a href="tel:…">`}} | {{Just Links `tel:`}} | |

## D. Kênh AI Assistant

{{Custom channel group: rule Source regex OR medium = ai-assistant, đặt trên Referral; 4 điểm mù (ChatGPT paid noreferrer → Direct; app; AI Overviews lẫn Organic; branded search sau AI); thêm "ChatGPT/AI" vào câu "biết từ đâu". Bỏ mục này nếu không có GEO và <30 session AI/tháng — ghi lý do.}}

## E. Đối soát

| Kênh | GA4 micro | Nguồn outcome | Cửa sổ | Ngưỡng lệch (lý do) | Lịch | Ai làm |
|---|---|---|---|---|---|---|

Sheet lead tối thiểu: thời điểm · kênh · nguồn · trang · nhu cầu · kết quả · ngày phản hồi đầu · chốt.

## E2. Quota tham số (parameter → scope → cần đăng ký custom dimension? → quota còn lại)

| Parameter | Scope | Đăng ký? | Quota còn lại (event 50 / user 25 / item 10, Standard) |
|---|---|---|---|

## F. Ca QA (kết quả = plan cho tới khi chạy; ca không thuộc cơ chế ghi N/A + lý do; gate G1 = mọi ca P0 của cơ chế primary PASS)

| # | Ca | Thao tác | Kỳ vọng | Kết quả |
|---|---|---|---|---|
| Q4 | Form thành công | Điền đúng, gửi | 1 `generate_lead`; lead tới đích ≤10 phút | plan |
| Q7 | Reload success | Reload | Không bắn lại | plan |
| Q10–Q12 | Đơn COD / cổng / trùng | Đặt thử | `purchase` 1 lần, khớp backend | plan |
| Q19 | PII | Xem payload | Không SĐT/email/CV | plan |

## G. Trạng thái & owner

| Việc | Owner | Deadline | Trạng thái |
|---|---|---|---|
| Dev gắn GTM theo §C | | ≤ T3 | |
| GTV kiểm Preview/DebugView | | | |
| Sheet lead / CRM cột nguồn | | | |
| Đối soát kỳ đầu | | +7/+14 ngày | |

Chưa xác minh: {{…}}

## Done-criteria

- [ ] Mỗi outcome có nguồn xác nhận ngoài GA4 hoặc ghi "chỉ báo micro".
- [ ] Không click nào đặt tên như outcome; `purchase`/`application_complete` từ dataLayer sau backend, có id chống trùng.
- [ ] Không PII trong tham số; QA chưa chạy ghi plan.
