---
client: "{{CLIENT}}"
cong_doan: 35
ws: 13-cro
section: "{{section | cụm intent}}"
pic: "{{CRO · Coder}}"
duyet: "{{SEO Lead Project}}"
status: draft
version: v1
---

# {{CLIENT}} — UX/UI feature brief — {{section / cụm intent}}

> Naming `{{CLIENT}}_ux-feature-brief-{{section}}_v{{N}}.md` → `13-cro/`. Mỗi section hoặc cụm intent = 1 brief. Đề xuất phải trace về item CR-xx / UX-xx và dữ liệu; không sửa cấu trúc đã lock (#11) — cần đổi cấu trúc thì về trạm 04. Checklist: `tier-1-cro-conversion.md` + `tier-1-ux-ui.md`.

## 1. Bối cảnh

| Trường | Giá trị |
|---|---|
| Section / cụm intent | {{PLP máy giặt / cụm "báo giá" / blog so sánh}} |
| Trang áp dụng (URL) | {{...}} |
| Số liệu hiện tại (ngày) | {{sessions 28d · CR% · scroll depth · rage click · drop-off funnel — nguồn GA4/Clarity}} |
| Vấn đề người dùng (E3: lỗi tái hiện được / số có mẫu số · E2: recording ≥3 / heatmap ≥100 session / VOC lặp ≥3) | {{finding ID + nhãn P/R/E + mô tả}} |

## 2. Tính năng / thành phần đề xuất

| # | Tính năng | Vị trí (block trong structure brief) | Vì sao (finding ID + nhãn P/R/E + pattern § + item CR/UX) | Metric theo dõi (cửa sổ ≥4 tuần, nhãn "quan sát") | Ưu tiên |
|---|---|---|---|---|---|
| 1 | {{bảng so sánh gói / calculator / bộ lọc / trust block / form 3 field}} | {{block #}} | {{"F-03 · P1 R2 E2 · §7 · CR-09/CR-11 — 42% rời ở block giá (funnel 28 ngày, n=1.240)"}} | {{generate_lead / user vào trang, so cùng kỳ}} | P1 |

## 3. Spec cho Coder (đo được — 10 mục component, `cro-audit/references/feature-brief.md`)

| Thành phần | Task người dùng | DOM order / semantic tag + `data-*` | Kích thước, hành vi desktop/mobile | Nội dung (copy client duyệt nếu giá/cam kết/SLA) | Trạng thái (loading/success/error/empty/disabled) | Keyboard · label · focus | Event (không PII) | Acceptance (PASS đo được) | Rollback |
|---|---|---|---|---|---|---|---|---|---|
| {{...}} | {{...}} | {{section > h2 > …}} | {{...}} | {{...}} | {{...}} | {{...}} | {{event name + tham số}} | {{"trên 390px thấy H1 + CTA không cuộn"}} | {{≤1 giờ, điều kiện}} |

Không thay heading hierarchy / URL / internal link đã duyệt (cần đổi → route trạm 04). Ảnh có kích thước đặt trước (chống CLS). Không viết "gọn hơn/đẹp hơn" — phải ra kích thước, vị trí, nội dung, trạng thái.

## 4. Đo sau triển khai

Ngày deploy (annotation GA4): {{...}} · QA chức năng + tracking ngay sau deploy (cùng ngày) · kiểm lại 14 ngày · đọc số sau ≥4 tuần trọn: {{metric, cùng mẫu số, cùng cửa sổ, nhãn "quan sát"; yếu tố khác đã đổi}} · điều kiện rollback: {{lỗi P0 mới / primary giảm rõ sau 2 tuần không giải thích được}} · A/B chỉ khi feasibility có số (#36).

Trạng thái brief: {{đề xuất → khách duyệt (ngày) → đã sửa (ngày) → chờ khách (ngày gửi)}} — đưa vào report tháng khối 3.

## Done-criteria

- [ ] Mỗi tính năng có lý do dữ liệu + item checklist; không có mục "cho đẹp".
- [ ] Spec Coder không còn chỗ phải đoán.
- [ ] Đã duyệt bởi SEO Lead Project; index.md #35 + log.md update.
