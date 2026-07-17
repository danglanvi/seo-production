---
client: "{{CLIENT}}"
loai: "{{kick-off | định kỳ tháng | review quý | nghiệm thu | ad-hoc | nội bộ}}"
ngay: "{{YYYY-MM-DD}}"
tham_du: "{{tên — bên GTV / bên khách}}"
nguoi_ghi: "{{@alias}}"
cong_doan: "{{#n nếu gắn công đoạn cụ thể, vd 12 hoặc 31}}"
ws: 10-client-management
version: v1
---

# {{CLIENT}} — Meeting note {{YYYY-MM-DD}} — {{chủ đề 1 dòng}}

> Naming: `{{CLIENT}}_meeting-note-{{YYYYMMDD}}_v{{N}}.md` → `10-client-management/`. Ghi trong vòng 24h sau meeting, gửi tóm tắt cho người tham dự xác nhận.

## 1. Tóm tắt (3-5 dòng)

{{Bối cảnh + kết quả chính của buổi. Không chép lại diễn biến — chỉ điều thay đổi sau meeting.}}

## 2. Decisions

| # | Quyết định | Căn cứ | Người chốt |
|---|---|---|---|
| D1 | {{...}} | {{...}} | {{tên — phía nào}} |

Luật: quyết định ảnh hưởng KPI, scope, timeline hoặc budget → phải có xác nhận email của khách, không dừng ở lời nói. Quyết định chạm gate ◇ → ghi `gate: <verdict>` vào `index.md` + log op `gate`.

## 3. Action items

| # | Việc | Owner | Deadline | Status |
|---|---|---|---|---|
| A1 | {{...}} | {{tên — 1 người, không ghi "team"}} | {{dd/mm}} | ☐ |

## 4. Follow-up từ meeting trước

| Action cũ | Status | Ghi chú |
|---|---|---|
| {{A-n meeting {{dd/mm}}}} | {{done \| trễ \| hủy}} | {{...}} |

## 5. Link liên quan

- Deliverable nhắc trong meeting: {{path trong WS folder}}
- Feedback phát sinh → tạo entry theo `_TEMPLATES/feedback-entry.md` vào `12-feedback-lessons/feedback-log.md`.

## Done-criteria

- [ ] Mọi action item có đúng 1 owner + deadline; không có dòng owner "team/cả hai bên".
- [ ] Decision ảnh hưởng scope/KPI có căn cứ + kế hoạch xác nhận email.
- [ ] Follow-up meeting trước đã đối chiếu — không action nào rơi tự do.
- [ ] Feedback trong meeting đã tách thành entry feedback-log (nếu có).
- [ ] Append `log.md` op `meeting`; update `index.md` nếu chạm công đoạn/gate.
