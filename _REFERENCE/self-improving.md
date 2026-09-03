# Self-improving — 3 vòng feedback

> Tách từ `CLAUDE.md` (§9) ngày 2026-09-02 (v2026.09.2) để file luật gọn — nội dung giữ nguyên văn. Router trỏ tới file này khi task cần.

## §9. Self-improving — 3 vòng

Hệ thống tự tốt lên qua 3 vòng feedback. Mọi promote: **đề xuất 1 câu, chờ duyệt** — Claude không tự vá.

| Vòng | Phạm vi | Cơ chế | Ai duyệt |
|---|---|---|---|
| **1 — Dự án** | Instance đang chạy | Mọi feedback (client / Lead / QC) → append `12-feedback-lessons/feedback-log.md`. Pattern lặp **≥2 lần** → đề xuất promote thành `lessons/lessons-ws<XX>.md`. Cuối mỗi pha → `retro/retro-pha-<n>.md` | Lead |
| **2 — Hệ thống** | Master `SEO Production/` | Lesson có `scope: system` → đề xuất vá master (`_TEMPLATES/`, `02-raw/knowledge/`, cheat-sheet, skill) → ghi `MIGRATION.md` master + log op `refactor`. Instance nhận bản vá qua migration | Vincent / Lead |
| **3 — Company** | GTV Ops wiki | Lesson có `scope: company` (bài học vượt khỏi hệ SEO Production) → đề xuất ingest vào GTV Ops wiki — chỉ khi chạy trong workspace Vincent (§11) | Vincent |

Luật kèm:

1. Lesson phải ghi theo format `_TEMPLATES/lessons-workstream.md`: bối cảnh → sai → đúng → rule mới → đã vá ở đâu.
2. Feedback chưa distill vẫn có giá trị — append feedback-log trước, promote sau. Không chờ "đủ hay" mới ghi.
3. Pre-work protocol (§3 bước 2) bảo đảm lesson được ĐỌC lại — vòng lặp chỉ khép khi lesson cũ chặn được lỗi mới.

---
