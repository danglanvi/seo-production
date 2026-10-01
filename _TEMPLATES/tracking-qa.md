---
client: "{{CLIENT}}"
cong_doan: 34
ws: 13-cro
pic: "{{CRO · Dev}}"
duyet: "{{SEO Lead Project}}"
status: qa-run
version: v1
---

# {{CLIENT}} — Kết quả QA tracking {{dd/mm/yyyy}}

> Naming `{{CLIENT}}_tracking-qa_v{{N}}.md` → `13-cro/`. Kết luận gate G1 (CR-06/07). Skill `cro-measurement-plan` → `references/reconciliation-qa.md`. Screenshot DebugView che PII, lưu `02-raw/screenshots/own-site/tracking/`.

Môi trường: iOS {{ver}} Safari · Android {{ver}} Chrome · macOS Chrome {{ver}}. Người chạy: {{tên}}. GTM container version: {{n}}. Measurement plan: v{{N}}.

## 1. Ca QA

| # | Ca | Thiết bị | Kết quả (PASS / FAIL / N/A + lý do) | Bằng chứng | Ghi chú |
|---|---|---|---|---|---|
| Q1 | Gọi 4–5 vị trí (event đo click; QA mở dialer riêng) | | | | |
| Q4b | HTTP 200 nhưng nghiệp vụ thất bại → không `generate_lead` | | | | |
| Q3 | Zalo (từng dạng nút) | | | | |
| Q4 | Form thành công → lead tới đích ≤10 phút | | | | |
| Q5 | Form lỗi → không `generate_lead`, giữ dữ liệu | | | | |
| Q6 | Double click → 1 lead, 1 event | | | | |
| Q7 | Reload success → không bắn lại | | | | |
| Q10 | Đơn COD → `purchase` 1 lần, khớp mã đơn | | | | |
| Q11 | Cổng thanh toán: thành công / huỷ / Back | | | | |
| Q13–Q14 | Apply onsite / offsite | | | | |
| Q18 | Kênh AI Assistant | | | | |
| Q19 | Payload không PII | | | | |
| Q20 | Key events đúng danh sách + counting method | | | | |

## 2. Đối soát 7 ngày đầu

| Kênh | GA4 | Nguồn outcome | Lệch | Nguyên nhân | Hành động |
|---|---|---|---|---|---|

## 3. Kết luận gate G1

**PASS / FAIL** — điều kiện: mọi ca P0 **thuộc cơ chế primary của site** PASS (luôn: Q4, Q4b HTTP 200 + nghiệp vụ thất bại, Q5, Q6, Q7, Q19, Q20; ecommerce: Q10–Q12; job: Q13/Q14; gọi/Zalo là primary: Q1/Q3); ca không thuộc cơ chế ghi **N/A + lý do**; lệch đối soát có nguyên nhân hoặc ghi "chưa xác định" (không là điều kiện PASS). FAIL → danh sách sửa + ngày kiểm lại: {{…}}

## Done-criteria

- [ ] Mỗi ca có thiết bị, kết quả, bằng chứng.
- [ ] Lệch chưa giải thích được ghi "chưa xác định", không làm tròn.
