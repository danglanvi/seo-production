---
template: feedback-entry
ws: 12-feedback-lessons
dich: 12-feedback-lessons/feedback-log.md
merge: union (append-only — không sửa block cũ)
version: v1
---

# Format entry feedback — append vào `feedback-log.md`

> Đây là template BLOCK, không phải file rời: mỗi feedback = 1 block append vào cuối `12-feedback-lessons/feedback-log.md`. File này merge=union (`.gitattributes`) — sửa block cũ sẽ nhân đôi dòng khi merge.

## Format block (chép nguyên, điền giá trị)

```markdown
### FB-{{YYYY-MM-DD}}-{{alias}}-{{nn}} | {{client | internal | QC}} | {{workstream — vd 06-onpage-internal-link}}
- Nội dung: {{feedback nguyên bản — ai nói, về deliverable/công đoạn nào, trích lời nếu là client}}
- Đề xuất: {{sửa gì, ở đâu — 1-2 câu; chưa nghĩ ra thì ghi "chưa có"}}
- Scope: {{project | system | company}}
- Trạng thái distill: pending
```

## Luật ghi

1. **ID duy nhất** `FB-YYYY-MM-DD-<alias>-<nn>`: alias = người ghi (vd `trang`), `nn` = số thứ tự 2 chữ số của alias trong ngày (`01`, `02`...). Không tái dùng ID.
2. **Nguồn** chỉ 3 giá trị: `client` (khách phản hồi) · `internal` (Lead/team góp ý) · `QC` (item ID fail ≥2 lần QC — Claude tự đề xuất, chờ duyệt).
3. **Append-only**: block mới luôn vào cuối file. Không sửa, không xóa, không sắp xếp lại block cũ.
4. **Scope** mặc định `project`; nâng `system` (lỗi do template/checklist/skill của master) hoặc `company` (bài học vượt hệ SEO Production) do Lead quyết khi distill.
5. **Trạng thái distill** — CHỈ Lead đổi dòng này: `pending` → `distilled → [lessons/lessons-ws<XX>.md]` hoặc `rejected — <lý do 1 câu>`.
6. Ghi ngay khi có feedback — không chờ "đủ hay". Pattern lặp ≥2 lần → đề xuất promote lesson (vòng 1, §9 CLAUDE.md).
7. Mỗi lần append → `log.md` op `feedback`.

## Ví dụ

```markdown
### FB-2026-07-17-trang-01 | client | 09-reporting
- Nội dung: Khách báo bảng KPI dùng tên "PV job+tool" thay vì tên nguyên văn PL01, phải giải thích lại qua email.
- Đề xuất: Thêm bước đối chiếu SOW MAPPING trước khi gửi báo cáo.
- Scope: project
- Trạng thái distill: pending
```

## Done-criteria

- [ ] Block đủ 4 dòng meta (ID + nguồn + workstream / Nội dung / Đề xuất / Scope / Trạng thái distill = `pending`).
- [ ] ID đúng format, không trùng với block đã có (grep trước khi ghi).
- [ ] Append vào cuối `feedback-log.md`, không đụng block cũ.
- [ ] `log.md` có entry op `feedback` cùng ngày.
