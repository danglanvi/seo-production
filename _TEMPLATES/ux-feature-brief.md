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
| Vấn đề người dùng (từ recording ≥3 hoặc heatmap ≥100 session) | {{...}} |

## 2. Tính năng / thành phần đề xuất

| # | Tính năng | Vị trí (block trong structure brief) | Vì sao (dữ liệu + item CR/UX) | Kỳ vọng đo được | Ưu tiên |
|---|---|---|---|---|---|
| 1 | {{bảng so sánh gói / calculator / bộ lọc / trust block / form 3 field}} | {{block #}} | {{"42% rời ở block giá — CR-09/CR-11"}} | {{CR +x% / drop-off −y%}} | P1 |

## 3. Spec cho Coder (đo được)

| Thành phần | DOM order / semantic tag | Kích thước (desktop/mobile) | Nội dung tối thiểu | Event tracking | Ảnh (w×h, alt) |
|---|---|---|---|---|---|
| {{...}} | {{section > h2 > …}} | {{...}} | {{...}} | {{event name}} | {{...}} |

Không thay heading hierarchy / URL / internal link đã duyệt. Ảnh có kích thước đặt trước (chống CLS).

## 4. Đo sau triển khai

Ngày deploy: {{...}} · đọc lại sau 14 và 30 ngày: {{metric}} · nếu không đạt → rollback hay A/B (#36).

## Done-criteria

- [ ] Mỗi tính năng có lý do dữ liệu + item checklist; không có mục "cho đẹp".
- [ ] Spec Coder không còn chỗ phải đoán.
- [ ] Đã duyệt bởi SEO Lead Project; index.md #35 + log.md update.
