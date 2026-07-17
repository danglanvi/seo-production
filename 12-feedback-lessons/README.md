# 12 — Feedback & Lessons (WS Feedback — self-improving 3 vòng)

1. **Mục đích**: Biến mọi feedback thành lesson được vá về đúng vòng — dự án, master hoặc company wiki.
2. **Công đoạn phụ trách**: xuyên suốt (không gắn số công đoạn).
3. **Deliverable chuẩn**: entry trong `feedback-log.md` · `lessons/lessons-ws<XX>.md` · `retro/retro-pha-<n>.md`.
4. **Template**: `_TEMPLATES/feedback-entry.md` · `_TEMPLATES/lessons-workstream.md` · `_TEMPLATES/retro-pha.md`.
5. **Checklist QC**: format feedback-entry (đủ trường ID, nguồn, workstream, scope, trạng thái distill mới nhận entry).
6. **Skill gọi**: —.
7. **Done-criteria**: Lesson được vá về đúng vòng, ghi rõ "đã vá ở đâu" trong file lesson.

## Cơ chế 3 vòng

| Vòng | Phạm vi | Trigger | Hành động |
|---|---|---|---|
| 1 — Dự án | instance này | mọi feedback (client / Lead / QC-fail-lặp) | append `feedback-log.md`; pattern lặp ≥2 lần → đề xuất promote `lessons/lessons-ws<XX>.md`; cuối mỗi pha → `retro/retro-pha-<n>.md` |
| 2 — Hệ thống | master SEO Production | lesson `scope: system` | đề xuất vá master (templates / knowledge / cheat-sheet / skill) — cần Vincent/Lead duyệt; ghi `MIGRATION.md` master + log op `refactor` |
| 3 — Company | GTV Ops wiki | lesson `scope: company` | đề xuất ingest vào GTV Ops wiki (chỉ khi chạy trong workspace Vincent) |

Luật:

1. Mọi promote chỉ ĐỀ XUẤT 1 câu, chờ duyệt — không tự vá.
2. Pre-work protocol: đọc `lessons/lessons-ws<XX>.md` (nếu tồn tại) trước mọi Work/QC của WS tương ứng.
3. Mỗi entry/lesson/retro mới → append `log.md` op `feedback` / `lesson` / `retro`.
