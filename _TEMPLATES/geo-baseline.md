---
template: geo-baseline
ws: 08-geo-ai-visibility
cong_doan: 14 (GEO baseline + Technical, T1→T3)
skill: geo-tracking-prompt-selection
lich_do: baseline T1 · giữa kỳ T6 (#24) · báo cáo T10 (#32)
naming: "{{CLIENT}}_geo-baseline_v{{N}}.md"
version: v1
---

# {{CLIENT}} — GEO Baseline (công đoạn 14)

## 0. Phân loại website → quy mô prompt set

| Trường | Giá trị |
|---|---|
| Loại site | Service/Agency (funnel-based, 28-40 prompts) / E-commerce (matrix-based, 80-100 prompts) |
| Dịch vụ/ngành hàng lõi (service: 1-3; e-commerce: theo % doanh thu) | |
| Đối thủ benchmark (5-7 brand) | |
| Thị trường / ngôn ngữ prompt | VN / US / song ngữ |
| Engine theo dõi | ChatGPT · Perplexity · Gemini · Claude · Google AIO |

## 1. Prompt set theo funnel

Phân bổ chuẩn (service): BOFU 50% (15-20) → MOFU 35% (10-15) → TOFU 15% (3-5). E-commerce: ma trận Category × Intent × Price Segment + prompt seasonal (Tết, sale lớn, product launch).

| ID | Funnel | Loại (comparison/pricing/trust/feature/educational) | Prompt VN | Prompt EN (nếu có) |
|---|---|---|---|---|
| B-01 | BOFU | comparison | | |
| M-01 | MOFU | feature | | |
| T-01 | TOFU | educational | | |

Công thức prompt: `[Product/Brand] + [Intent Action] + [Modifier]`.

Luật chọn prompt:
1. BOFU ưu tiên nhất: comparison ("[Brand] vs [đối thủ]"), pricing ("giá/báo giá [X]"), trust ("[Brand] có uy tín không").
2. Cấm prompt generic không có conversion value ("SEO là gì").
3. Không vượt trần: >100 (service) / >150 (e-commerce).
4. Mỗi prompt phải track được context type, không chỉ đếm mention.

## 2. Baseline đo T1 (chạy toàn bộ prompt set, ghi từng engine)

| Chỉ số | ChatGPT | Perplexity | Gemini | Claude | AIO | Tổng |
|---|---|---|---|---|---|---|
| Mention rate BOFU (%) | | | | | | |
| Mention rate MOFU (%) | | | | | | |
| Mention rate TOFU (%) | | | | | | |
| Citation count (page nào được cite) | | | | | | |

## 3. Citation share — brand vs đối thủ

`SOV = mention brand / tổng mention (brand + đối thủ) × 100` — tính trên cùng prompt set.

| Brand | Mention | SOV (%) | Vị trí trung bình trong list | Context chính (recommendation/comparison/information/negative) |
|---|---|---|---|---|
| {{CLIENT}} | | | | |
| Đối thủ 1 | | | | |

## 4. KPI GEO cam kết

| KPI | Baseline T1 | Target | Tần suất đo |
|---|---|---|---|
| Brand Mention | | >60% BOFU · >40% MOFU · >20% TOFU | tháng |
| AI Citations | | trend tăng | tháng |
| Share of Voice | | >30% SOV | tháng |
| Information Accuracy | | >90% mô tả đúng | tháng |

Luật KPI: GEO không deterministic như SEO — KHÔNG hứa vị trí cụ thể; cam kết theo mention rate/SOV/trend.

## 5. Lịch đo T1/T6/T10

| Mốc | Việc | Output |
|---|---|---|
| T1 (baseline) | Chốt prompt set + chạy đo lần đầu, điền mục 2-3 | File này v1 + checkbox bảng C index |
| T6 (giữa kỳ, cùng #24) | Chạy lại full set; so baseline; thay prompt underperform; cập nhật SOV | `{{CLIENT}}_geo-do-giua-ky_v1.md` + evidence vào FS/AIO đợt 2 (#28) |
| T10 (báo cáo) | Đo cuối kỳ; tổng hợp trend vào báo cáo kép (#32) | Section GEO trong báo cáo T10 |

## 6. Luật vận hành

1. Iteration hàng tháng: prompt 0% mention 2 kỳ liên tiếp → thay, ghi log.
2. Prompt set đổi ≥30% → đo lại baseline mới, không so chéo set cũ-mới.
3. Alert: mention rate rớt >20% tuần / xuất hiện mention negative / thông tin sai nghiêm trọng → báo SEO Lead ngay.
4. Kết quả đo lưu kèm screenshot vào `02-raw/screenshots/serp-ai/` (naming chuẩn, log op `capture`); prompt set là tài sản bàn giao — đưa vào handover-checklist (#33).

## Done-criteria

- [ ] Mục 0-1 đủ: loại site, đối thủ 5-7, prompt set đúng phân bổ funnel, không prompt generic.
- [ ] Baseline mục 2-3 có số thật từng engine + screenshot trong `02-raw/screenshots/serp-ai/`.
- [ ] KPI mục 4 điền baseline + target, không cam kết vị trí cụ thể.
- [ ] Lịch đo T1/T6/T10 khớp bảng C index; index #14 + log cập nhật (op `work`).
