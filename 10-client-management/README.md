# 10 — Client Management (WS Client mgmt)

1. **Mục đích**: Giữ nhịp quan hệ client — kick-off, meeting định kỳ và vòng điều chỉnh theo review Manager/Director.
2. **Công đoạn phụ trách**: #12 (kick-off), #31 (review → điều chỉnh).
3. **Deliverable chuẩn**: kick-off doc, meeting note — naming `<CLIENT>_<slug>_v<N>.md` (vd `<CLIENT>_meeting-note-20260717_v1.md`).
4. **Template**: `_TEMPLATES/kick-off.md` · `_TEMPLATES/meeting-note.md`.
5. **Checklist QC**: DoD trong `_TEMPLATES/kick-off.md` (WS này không có checklist riêng trong `02-raw/knowledge/`).
6. **Skill gọi**: `skills/gtv-client-report/` (⚠ claude-only, chỉ chạy trong Claude Code).
7. **Done-criteria**: Kick-off done (chốt Tier 2 checklist được bật — ghi vào Ghi chú dòng #12 `index.md`); mọi meeting note có action items + owner + deadline.

Ghi chú:

- Append `log.md` op `meeting` sau mỗi buổi; decision quan trọng ghi rõ trong note, không để trôi trong chat.
- Feedback client nêu trong meeting → tách entry vào `12-feedback-lessons/feedback-log.md`, không để nằm im trong note.
