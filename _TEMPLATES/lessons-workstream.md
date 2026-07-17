---
ws: "{{XX — vd 06-onpage-internal-link}}"
scope: "{{project | system | company}}"
status: "{{new | applied | patched-master | ingested-wiki}}"
credit: "@{{alias người phát hiện — giữ nguyên khi promote lên master/wiki}}"
date: "{{YYYY-MM-DD}}"
source: "{{FB-... / QC-... — ID entry hoặc report sinh ra lesson này}}"
version: v1
---

# Lessons WS {{XX}} — {{tên workstream}}

> Naming: `12-feedback-lessons/lessons/lessons-ws{{XX}}.md` — 1 file/workstream. Lesson thứ hai trở đi của cùng WS: append section `## Lesson <nn>` mới vào file này, cập nhật frontmatter `date` + `status` theo lesson mới nhất; scope frontmatter = scope cao nhất trong file (company > system > project).
> Pre-work protocol (§3 CLAUDE.md) BẮT BUỘC đọc file này trước mọi Work/QC trong WS — lesson là luật đã trả giá, không phải gợi ý.

## Lesson {{nn}} — {{tiêu đề 1 dòng, động từ trước}}

### 1. Bối cảnh

{{3-5 dòng: công đoạn #n, deliverable nào, chuyện gì xảy ra, phát hiện qua kênh nào (client / QC / Lead). Dẫn ID: FB-... hoặc QC-...}}

### 2. Sai → Đúng

| Trước (sai) | Sau (đúng) |
|---|---|
| {{cách làm cũ gây lỗi — cụ thể, trích được}} | {{cách làm thay thế — cụ thể, làm lại được}} |

### 3. Rule mới

1. {{Viết dạng luật thực thi được: điều kiện → hành động → ngưỡng. Không viết cảm nhận.}}
2. {{Rule 2 nếu có — tối đa 3 rule/lesson; nhiều hơn = tách lesson.}}

### 4. Đã vá ở đâu

| Vòng | Nơi vá | File/path | Ngày | Log op |
|---|---|---|---|---|
| 1 — Dự án | {{deliverable/quy trình instance}} | {{path}} | {{dd/mm}} | `lesson` |
| 2 — Master (nếu scope ≥ system) | {{_TEMPLATES/ \| 02-raw/knowledge/ \| cheat-sheet \| skill}} | {{path + MIGRATION.md}} | {{dd/mm}} | `refactor` |
| 3 — Company (nếu scope company) | GTV Ops wiki | {{page}} | {{dd/mm}} | — |

Luật promote: mọi vá vòng 2/3 = đề xuất 1 câu, chờ Vincent/Lead duyệt — Claude không tự vá. Instance không sửa `02-raw/knowledge/` tại chỗ; bản vá về qua MIGRATION.

## Done-criteria

- [ ] Frontmatter đủ ws + scope + status + credit + source; scope đúng định nghĩa (project = dự án này / system = master / company = ngoài hệ).
- [ ] Sai → Đúng cụ thể, người khác đọc là làm lại được — không viết chung chung.
- [ ] Rule mới ≤3, dạng thực thi được (điều kiện → hành động → ngưỡng).
- [ ] Bảng "Đã vá ở đâu" khớp thực tế: vòng nào chưa vá thì để trống + status phản ánh đúng.
- [ ] Entry gốc trong `feedback-log.md` đã đổi Trạng thái distill (Lead) + `log.md` op `lesson`.
