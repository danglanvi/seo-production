---
client: "{{CLIENT}}"
cong_doan: 12
ws: 10-client-management
ngay: "{{YYYY-MM-DD}}"
hinh_thuc: "{{online | offline — địa điểm}}"
tham_du_gtv: "{{SEO Lead, Account, ...}}"
tham_du_khach: "{{tên + chức danh}}"
pic: "{{ACCOUNT}}"
status: draft
version: v1
---

# {{CLIENT}} — Kick-off dự án SEO

> Naming: `{{CLIENT}}_kick-off_v{{N}}.md` → `10-client-management/`. Trước buổi: đọc `00-client-context/` + `kpi-commitments.md` + OKRs đã duyệt (#8).
> Kick-off nội bộ chạy TRƯỚC kick-off khách: chốt Tier 2 checklist nào được bật → ghi vào cột Ghi chú dòng #12 `index.md`.

## 1. Agenda

| # | Nội dung | Phút | Người dẫn |
|---|---|---|---|
| 1 | Giới thiệu team 2 bên + vai trò | {{...}} | {{Account}} |
| 2 | Mục tiêu dự án + KPI cam kết (đọc từ kpi-commitments) | {{...}} | {{SEO Lead}} |
| 3 | Timeline {{8/10/12}} tháng + 5 pha + mốc cứng | {{...}} | {{SEO Lead}} |
| 4 | RACI + việc cần khách làm + SLA phản hồi | {{...}} | {{Account}} |
| 5 | Kênh liên lạc + nhịp báo cáo + Q&A | {{...}} | {{Account}} |

## 2. RACI GTV ↔ client

| Hạng mục | GTV | Khách | Ghi chú |
|---|---|---|---|
| Chiến lược + thực thi SEO | R/A | C/I | {{...}} |
| Duyệt content / xuất bản CMS | {{R \| C}} | {{A \| R}} | {{theo mô hình thực thi/advisory}} |
| Technical fix trên website | C (khuyến nghị) | R (dev khách) | {{hoặc GTV nếu HĐ bao}} |
| Cấp quyền truy cập (GA4, GSC, CMS, hosting) | I | R | deadline: {{dd/mm}} |
| Nghiệm thu + thanh toán | I | R/A | theo HĐ |

## 3. Cam kết 2 bên

| Bên | Cam kết | Mốc/SLA |
|---|---|---|
| GTV | KPI theo HĐ + báo cáo tháng đúng hạn + escalate sớm khi có risk | {{...}} |
| GTV | Deliverable qua QC nội bộ trước khi gửi | xuyên suốt |
| Khách | Phản hồi duyệt trong {{04/07 — theo HĐ}} ngày làm việc; quá hạn = auto-accept nếu HĐ quy định | {{...}} |
| Khách | Cấp đủ quyền truy cập + đầu mối quyết định duy nhất | {{dd/mm}} |
| Khách | Không tự triển khai SEO/backlink ngoài kế hoạch chung | xuyên suốt |

## 4. Tier 2 checklist được bật (chốt tại kick-off nội bộ)

| Tier 2 item | Bật? | Lý do |
|---|---|---|
| {{tên item trong sop/06-self-checklist/tier-2-project-specific.md}} | {{☐/☑}} | {{...}} |

## 5. Kênh liên lạc & nhịp

| Kênh/nhịp | Giá trị |
|---|---|
| Kênh chính | {{group Zalo/Slack/email}} |
| Đầu mối GTV / khách | {{ACCOUNT}} / {{tên}} |
| Báo cáo tháng | ngày {{dd}} hằng tháng, qua {{email}} |
| Meeting định kỳ | {{tần suất + khung giờ}} |

## 6. Next steps sau kick-off

| # | Việc | Owner | Deadline |
|---|---|---|---|

## Done-criteria

- [ ] Kick-off diễn ra, meeting note lưu theo `_TEMPLATES/meeting-note.md` với action items + owner + deadline.
- [ ] RACI + SLA phản hồi được khách xác nhận (email/biên bản).
- [ ] Tier 2 đã chốt và ghi vào cột Ghi chú dòng #12 `index.md`.
- [ ] Quyền truy cập có deadline + owner phía khách.
- [ ] Update `index.md` #12 + append `log.md` op `meeting`.
