---
client: "{{CLIENT}}"
pha: "{{1 Khởi động T1 | 2 Nền tảng & lõi T1-T3 | 3 Mở rộng T3-T6 | 4 Thúc đẩy T6-T9 | 5 Về đích T10}}"
khoang_thoi_gian: "{{T{{x}}–T{{y}} — {{mm/yyyy}}–{{mm/yyyy}}}}"
ngay_retro: "{{YYYY-MM-DD}}"
tham_du: "{{SEO Lead, Executive, Account...}}"
nguoi_ghi: "{{@alias}}"
ws: 12-feedback-lessons
version: v1
---

# {{CLIENT}} — Retro pha {{n}}: {{tên pha}}

> Naming: `12-feedback-lessons/retro/retro-pha-{{n}}.md`. Chạy CUỐI mỗi pha, trước khi mở pha sau. Input: `index.md` (bảng B các dòng thuộc pha), OKRs quý tương ứng, `feedback-log.md` trong kỳ, QC report của pha.

## 1. Kết quả vs OKRs pha

| OKR/KPI | Mục tiêu | Thực tế | % | Nhận định 1 câu |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

Tình trạng công đoạn thuộc pha (chép từ bảng B, chỉ dòng của pha):

| # | Công đoạn | Status | QC | Ghi chú |
|---|---|---|---|---|
| {{n}} | {{...}} | {{done \| done* \| qc \| blocked \| trượt sang pha sau}} | {{...}} | {{gate: verdict nếu là ◇}} |

## 2. What worked — giữ lại

1. {{Việc/cách làm hiệu quả + evidence (số liệu, QC score, phản hồi khách). Không khen chung chung.}}

## 3. What failed — nguyên nhân gốc

| Vấn đề | Nguyên nhân gốc (không dừng ở triệu chứng) | FB/QC liên quan |
|---|---|---|
| {{...}} | {{...}} | {{FB-... / QC-...}} |

## 4. Lesson promote

| Nguồn (FB/QC) | Lesson đề xuất | Scope | File đích |
|---|---|---|---|
| {{FB-...}} | {{1 câu}} | {{project \| system \| company}} | `lessons/lessons-ws{{XX}}.md` |

Luật: chỉ promote pattern lặp ≥2 lần hoặc lỗi impact cao; mỗi promote = đề xuất 1 câu, chờ Lead duyệt; lesson ghi theo `_TEMPLATES/lessons-workstream.md`.

## 5. Điều chỉnh pha sau

| Điều chỉnh | Lý do | Ai duyệt | Phản ánh vào đâu |
|---|---|---|---|
| {{đổi ưu tiên/nguồn lực/timeline/checklist}} | {{...}} | {{Lead \| SEO Director}} | {{index.md dòng #n / OKRs quý sau / kế hoạch WS}} |

## Done-criteria

- [ ] Bảng kết quả vs OKRs đủ mọi KR của pha, số khớp nguồn đo.
- [ ] Mọi dòng What failed có nguyên nhân gốc + link FB/QC — không có dòng mồ côi evidence.
- [ ] Lesson promote đã tạo entry/file tương ứng hoặc ghi rõ "chờ duyệt".
- [ ] Điều chỉnh pha sau đã phản ánh vào `index.md`/OKRs — không nằm lại trong retro.
- [ ] Append `log.md` op `retro`.
