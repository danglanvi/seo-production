---
client: "{{CLIENT}}"
cong_doan: 17
ws: 05-content-plan
pic: "{{PIC}}"
status: draft
version: v1
---

# {{CLIENT}} — Plan traffic FULL (T3 → giữa T4)

> Input bắt buộc: topical-map.md đã chốt + gap-analysis.md + `00-client-context/kpi-commitments.md`.
> Cheat-sheet: `02-raw/knowledge/cheat-sheets/ws05-content-plan.md`. Naming: `{{CLIENT}}_traffic-plan_v{{N}}.md`.

## 1. Cam kết & mục tiêu

| Trường | Giá trị |
|---|---|
| KPI traffic cam kết (HĐ) | {{N}}/tháng tại {{Tx}} |
| Mục tiêu plan = cam kết +20% | {{N × 1,2}} |
| Baseline hiện tại | {{N}}/tháng ({{thang}}) |
| Giả định CTR theo position | {{bảng CTR dùng — ghi nguồn}} |

## 2. Bảng dự phóng topic → URL → volume → traffic

Luật dự phóng:

1. Traffic dự phóng = volume × CTR theo position kỳ vọng × hệ số trưởng thành.
2. Content cần ~100 ngày trưởng thành — tháng đạt ≠ tháng publish.
3. Position kỳ vọng phải có căn cứ (độ khó, benchmark đối thủ), không đặt Top 3 mặc định.

| # | Topic | URL | Section (Core/Outer) | Volume | Position kỳ vọng | Traffic dự phóng/tháng | Tháng publish | Tháng đạt |
|---|---|---|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

## 3. Tổng kiểm

| Chỉ số | Giá trị |
|---|---|
| Tổng traffic dự phóng tại {{Tx}} | {{N}} |
| Tỷ lệ vs KPI cam kết | {{%}} — FAIL nếu <120% |
| Phân bố Core vs Outer | {{% / %}} |
| Số URL trong plan | {{N}} |

Tổng dự phóng < cam kết +20% → quay lại topical map bổ sung topic. Không hạ mục tiêu, không thổi phồng position kỳ vọng.

## 4. Topic backup

Kích hoạt khi initial ranking không như kỳ vọng (gate #22, T4-T6).

| # | Topic backup | Volume | Traffic dự phóng | Điều kiện kích hoạt |
|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} |

## 5. Ràng buộc timeline

1. Content URL SEO xong hết T3; Core Section 50-60% → 100% theo mốc index.md.
2. Dây chuyền trưởng thành: content publish → +10-15 ngày onpage → +15-30 ngày internal link.
3. Content non-URL SEO chạy T4 → hết T7 — không dồn traffic dự phóng vào T8-T9.
4. Ma trận số bài × % mốc chi tiết → content-plan-matrix.md; file này chỉ giữ dự phóng traffic.

## Done-criteria

- [ ] Mỗi dòng đủ topic / URL / volume / position kỳ vọng / traffic dự phóng / tháng publish / tháng đạt.
- [ ] Tổng dự phóng ≥ KPI cam kết +20%, ghi rõ tỷ lệ %.
- [ ] Position kỳ vọng có căn cứ benchmark, không mặc định Top 3.
- [ ] Topic backup có volume + điều kiện kích hoạt, đủ bù {{10-20}}% tổng dự phóng.
- [ ] Tháng đạt tôn trọng ~100 ngày trưởng thành + dây chuyền onpage/internal link.
- [ ] SEO Lead Project duyệt; index.md + log.md đã update.
