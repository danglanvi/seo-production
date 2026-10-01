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

> Naming `{{CLIENT}}_heatmap-review-{{ky}}_v{{N}}.md` → `13-cro/`. Tool: {{Microsoft Clarity / Hotjar}}, gắn ngày {{dd/mm}}, đọc sau ≥2 tuần. Heatmap = *ở đâu*, recording = *chuỗi hành vi*; *vì sao* cần tái hiện hoặc VOC. Bằng chứng: E3 = 1 lỗi tái hiện được hoặc số có mẫu số (đủ); E2 = ≥3 recording cùng hiện tượng hoặc ≥100 session; ít hơn ghi "mẫu chưa đủ" (E1, cần kiểm). Không suy tỷ lệ từ vài recording. Screenshot lưu `02-raw/screenshots/own-site/heatmap/`.

## 1. Phạm vi

| Landing (ưu tiên CR-08) | Sessions kỳ | CR% | Recording đã xem | Heatmap (click/scroll/move) |
|---|---|---|---|---|
| {{URL}} | {{n}} | {{x%}} | {{n}} | {{✅}} |

## 2. Phát hiện

| # | Trang | Quan sát (số + ảnh) | Recording minh chứng (id/ngày) | Giả thuyết | Item CR/UX |
|---|---|---|---|---|---|
| 1 | {{URL}} | {{"chỉ 28% scroll tới CTA; rage click ở bộ lọc mobile"}} | {{...}} | {{CTA quá thấp / bộ lọc không phản hồi}} | {{CR-10 / UX-xx}} |

## 3. Action

| # | Finding ID | Action | Trang | Đường (sửa lỗi / rollout có theo dõi / A/B) | Owner | Deadline triển khai | QA ngay sau deploy | Đọc số (≥4 tuần, "quan sát") |
|---|---|---|---|---|---|---|---|---|
| 1 | {{F-xx}} | {{...}} | {{...}} | {{...}} | {{Dev khách / CRO}} | {{14–30 ngày}} | {{ngày, PASS/FAIL}} | {{metric tử/mẫu + cửa sổ}} |

## 4. Log triển khai — sửa lỗi / rollout có theo dõi / A/B (#36)

| Việc | Đường (sửa lỗi · rollout · A/B) | Giả thuyết / treatment (gói thay đổi) | Trang | Feasibility (baseline · MDE · mẫu cần · ngày ước tính) — chỉ A/B | Deploy / bắt đầu → kết thúc | SRM (A/B) | Kết quả (counts · rates · effect · bất định · guardrail) | Quyết định |
|---|---|---|---|---|---|---|---|---|
| {{...}} | {{rollout}} | {{...}} | {{...}} | {{— / 2% → 2,4% · 21.100/nhóm · 141 ngày}} | {{dd/mm}} | {{PASS/—}} | {{"quan sát: 1,8% → 2,3%, cùng mẫu số, 4 tuần; tháng 8 thêm 2 bài top 3"}} | {{giữ / rollback / inconclusive}} |

Điểm rơi funnel lớn nhất (CR-19): {{bước · % drop · mẫu số}} → việc kế tiếp: {{...}}. Rollout không phải A/B → ghi "quan sát trước/sau", không "uplift". Test không có winner nhưng dữ liệu tốt vẫn là kết quả.

## Done-criteria

- [ ] Mỗi phát hiện có ảnh + recording/số có mẫu số + nhãn P/R/E + item checklist; không suy tỷ lệ từ vài recording.
- [ ] Action có cách đo và mốc đọc lại (≥4 tuần trọn); A/B chỉ khi feasibility có số, một giả thuyết = một treatment, đủ mẫu + SRM PASS mới kết luận.
- [ ] index.md #35/#36 + log.md update; QC PASS.
