---
client: "{{CLIENT}}"
cong_doan: "{{35 | 36}}"
ws: 13-cro
ky: "{{đợt 1 T4-T6 | đợt 2 T7-T9}}"
pic: "{{CRO}}"
duyet: "{{SEO Lead Project (#35) · SEO Director (#36)}}"
status: draft
version: v1
---

# {{CLIENT}} — Heatmap & recording review — {{kỳ}}

> Naming `{{CLIENT}}_heatmap-review-{{ky}}_v{{N}}.md` → `13-cro/`. Tool: {{Microsoft Clarity / Hotjar}}, gắn ngày {{dd/mm}}, đọc sau ≥2 tuần. Heatmap = *ở đâu*, recording = *vì sao* — kết luận phải có ≥3 recording hoặc ≥100 session; ít hơn ghi "mẫu chưa đủ". Screenshot lưu `02-raw/screenshots/own-site/heatmap/`.

## 1. Phạm vi

| Landing (ưu tiên CR-08) | Sessions kỳ | CR% | Recording đã xem | Heatmap (click/scroll/move) |
|---|---|---|---|---|
| {{URL}} | {{n}} | {{x%}} | {{n}} | {{✅}} |

## 2. Phát hiện

| # | Trang | Quan sát (số + ảnh) | Recording minh chứng (id/ngày) | Giả thuyết | Item CR/UX |
|---|---|---|---|---|---|
| 1 | {{URL}} | {{"chỉ 28% scroll tới CTA; rage click ở bộ lọc mobile"}} | {{...}} | {{CTA quá thấp / bộ lọc không phản hồi}} | {{CR-10 / UX-xx}} |

## 3. Action

| # | Action | Trang | Loại (sửa ngay / A/B) | Owner | Deadline | Đo sau 14–30 ngày |
|---|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{Coder/CRO}} | {{...}} | {{metric + ngưỡng}} |

## 4. A/B log (#36)

| Test | Giả thuyết | Biến duy nhất | Trang | Mẫu cần | Bắt đầu → kết thúc | Kết quả | Quyết định |
|---|---|---|---|---|---|---|---|
| {{...}} | {{...}} | {{CTA màu / headline / form length}} | {{...}} | {{n session}} | {{...}} | {{...}} | {{giữ B / giữ A}} |

Điểm rơi funnel lớn nhất (CR-19): {{bước · % drop}} → test kế tiếp: {{...}}.

## Done-criteria

- [ ] Mỗi phát hiện có ảnh + recording + item checklist.
- [ ] Action có cách đo và mốc đọc lại; A/B 1 biến/lần, đủ mẫu mới kết luận.
- [ ] index.md #35/#36 + log.md update; QC PASS.
