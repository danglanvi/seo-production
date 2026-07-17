---
client: "{{CLIENT}}"
cong_doan: "{{1 | 8 | 24 | 31}}"
ws: 01-strategy-okrs
pic: "{{PIC}}"
status: draft
version: v1
---

# {{CLIENT}} — OKRs dự án SEO — Quý {{N}} ({{Tx}}-{{Ty}})

> Skill: `skills/okrs-gtv-tag-framework`. Duyệt: SEO Director. Naming: `{{CLIENT}}_okrs-q{{N}}_v{{N}}.md`.
> KPI cam kết đọc từ `00-client-context/kpi-commitments.md` — không chép tay số khác nguồn.

## 1. Ngữ cảnh quý

| Trường | Giá trị |
|---|---|
| Pha dự án | {{Q1 Foundation \| Q2 Growth \| Q3 Optimization \| Q4 Sustainability}} |
| Baseline đầu quý | {{traffic / ranking / DR / index coverage...}} |
| KPI hợp đồng liên quan | {{trích kpi-commitments.md}} |
| OKRs quý trước | {{link + score, hoặc n/a nếu Q1}} |

## 2. O/KR theo quý

Luật lập:

1. 3-4 Objective, mỗi O 3-4 KR. Không vượt.
2. KR đo outcome, không đo output; task chỉ được làm KR khi verifiable done/not-done.
3. Mỗi KR bắt buộc: baseline + con số target + deadline + owner.
4. Phủ đủ 4 trụ khi phù hợp pha: Technical / Content / Onpage / Offsite.

### O1: {{động từ + đạt gì + con số}}

| KR | Baseline | Target | Owner | Deadline | Score |
|---|---|---|---|---|---|
| KR1: {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | — |
| KR2: {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | — |

### O2: {{...}}

| KR | Baseline | Target | Owner | Deadline | Score |
|---|---|---|---|---|---|
| KR1: {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | — |

### O3: {{...}} (thêm O4 nếu cần, tối đa 4)

## 3. KPI cam kết vs stretch

KPI hợp đồng = sàn, phải đạt 100%. Target OKRs đặt cao hơn — score 0.7-0.8 là vùng đạt tốt.

| Chỉ số | KPI cam kết (HĐ) | Target OKRs (stretch) | Ghi chú |
|---|---|---|---|
| {{traffic}} | {{...}} | {{...}} | {{...}} |
| {{ranking / khác}} | {{...}} | {{...}} | {{...}} |

## 4. Backup plan

| Rủi ro | Ngưỡng kích hoạt | Hành động backup | Owner |
|---|---|---|---|
| {{initial ranking không như kỳ vọng...}} | {{...}} | {{...}} | {{...}} |

## 5. Cadence

| Mốc | Việc |
|---|---|
| T1 | Lập OKRs năm + quý 1 (công đoạn 1, 8) |
| T3 | Lập OKRs quý 2 |
| T6 | Lập OKRs quý 3 + audit định kỳ (#24) |
| T9 | Review OKRs, đối chiếu KPI cam kết (gate #30) |

Trong quý: weekly 30 phút check traffic/ranking + task; monthly chấm score đủ mọi KR.

## 6. Chấm điểm cuối quý

Thang: 0.0-0.3 không đạt · 0.4-0.6 đạt một phần · 0.7-0.8 đạt tốt · 0.9-1.0 xuất sắc (nghi target quá thấp). O score = trung bình KR score.

| O | Score | Nhận xét 1 câu |
|---|---|---|
| O1 | {{...}} | {{...}} |

## Done-criteria

- [ ] 3-4 O, mỗi O 3-4 KR; mỗi KR đủ baseline + số + deadline + owner.
- [ ] KR outcome-first; task-KR chỉ khi verifiable done/not-done.
- [ ] Bảng KPI cam kết vs stretch khớp `kpi-commitments.md`.
- [ ] Backup plan có ngưỡng kích hoạt + owner.
- [ ] SEO Director đã duyệt — ghi ngày duyệt + link evidence vào index.md.
