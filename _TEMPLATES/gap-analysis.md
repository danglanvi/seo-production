---
client: "{{CLIENT}}"
cong_doan: 2
ws: 03-audits
pic: "{{PIC}}"
status: draft
version: v1
---

# {{CLIENT}} — Gap Analysis đối thủ theo page type

> Skill: `skills/competitor-seo-gap-analysis`. Naming: `{{CLIENT}}_gap-analysis_v{{N}}.md`.
> Data: export Ahrefs/GSC ngày {{NGAY_EXPORT}} — lưu `02-raw/seo-data/`.

## 1. Scope & đối thủ

| Trường | Giá trị |
|---|---|
| Domain client | {{DOMAIN}} |
| Loại website | {{Job site \| E-commerce \| Service \| Informational}} |
| Đối thủ phân tích | {{DT1}}, {{DT2}}, {{DT3}} |
| Benchmark leader | {{DOMAIN_LEADER}} |

## 2. Traffic distribution theo page type

Phân loại URL theo pattern trước khi tính. Efficiency = traffic ÷ số URL cùng page type.

| Page type | {{CLIENT}} % | {{DT1}} % | {{DT2}} % | Benchmark chuẩn | Gap |
|---|---|---|---|---|---|
| Category (PLP) | {{...}} | {{...}} | {{...}} | 40-60% | {{...}} |
| Product/Detail | {{...}} | {{...}} | {{...}} | 5-20% | {{...}} |
| Blog | {{...}} | {{...}} | {{...}} | 15-30% | {{...}} |
| Tools | {{...}} | {{...}} | {{...}} | 5-15% | {{...}} |
| Homepage | {{...}} | {{...}} | {{...}} | 10-25% | {{...}} |

| Efficiency (traffic/URL) | {{CLIENT}} | {{DT1}} | {{DT2}} | Target |
|---|---|---|---|---|
| Category | {{...}} | {{...}} | {{...}} | 50-150 |
| Product/Detail | {{...}} | {{...}} | {{...}} | 5-20 |
| Blog | {{...}} | {{...}} | {{...}} | 100-500 |

## 3. Gap theo layer

### 3.1 Category — loại gap: MISSING / UNDERPERFORMING / STRUCTURAL / DEPTH

| Gap | Loại | Đối thủ có gì | {{CLIENT}} thiếu gì | Ưu tiên |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

### 3.2 Product/Detail — loại gap: SCALE / SCHEMA / QUALITY / LINKING

| Gap | Loại | Đối thủ có gì | {{CLIENT}} thiếu gì | Ưu tiên |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

### 3.3 Blog — loại gap: RELEVANCE / COVERAGE / QUALITY / AUTHORITY / FRESHNESS

| Gap | Loại | Đối thủ có gì | {{CLIENT}} thiếu gì | Ưu tiên |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

## 4. Chấm ưu tiên gap

1. Gap % = (target − current) ÷ target × 100.
2. Ngưỡng: >80% CRITICAL · >50% HIGH · >30% MEDIUM · còn lại LOW.
3. Gap Priority Score = Relevance (1-3) × Prominence (1-3) × Potential (1-3).

| # | Gap | Gap % | R×P×P | Priority | Effort | Timeline |
|---|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} | {{Low/Med/High}} | {{...}} |

## 5. Kết luận cơ hội

| Nhóm | Hành động | Traffic tiềm năng ước tính |
|---|---|---|
| Quick win (1-4 tuần) | {{...}} | {{...}} |
| Medium (1-3 tháng) | {{...}} | {{...}} |
| Long (3-6 tháng) | {{...}} | {{...}} |

Output feed tiếp: topical-map.md (topic coverage) + traffic-plan.md (dự phóng).

## Done-criteria

- [ ] URL client + đối thủ đã phân loại đủ page type, ghi rõ ngày export data.
- [ ] Bảng distribution + efficiency đủ client + ≥2 đối thủ + benchmark.
- [ ] Mỗi layer Category/Product/Blog có bảng gap riêng, gap gắn đúng loại.
- [ ] 100% gap có priority score + effort + timeline.
- [ ] Kết luận có ước tính traffic + ghi rõ feed sang topical map / traffic plan.
