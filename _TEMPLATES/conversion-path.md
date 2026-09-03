---
client: "{{CLIENT}}"
cong_doan: 34
ws: 13-cro
pic: "{{SEO Lead Project · CRO}}"
duyet: "{{SEO Leader}}"
status: draft
version: v1
---

# {{CLIENT}} — Conversion path theo cụm intent

> Naming `{{CLIENT}}_conversion-path_v{{N}}.md` → `13-cro/`. Input: topical map (#10) + structure brief đã lock (#11) + KPI chuyển đổi trong `00-client-context/kpi-commitments.md`. Checklist: `sop/06-self-checklist/tier-1-cro-conversion.md` phần A (CR-01…07) + phần C (CR-16…19). Skill `cro-audit`.

## 1. Điểm chuyển đổi & tracking (gate G1 — xong ≤ T3)

| Điểm chuyển đổi | Kênh | GA4 event | Trang/thành phần bắn | Verify (DebugView ngày) | Owner |
|---|---|---|---|---|---|
| {{Form tư vấn}} | form | `form_submit` | {{thank-you / success state}} | {{dd/mm ✅}} | {{Coder}} |
| {{Gọi}} | tel: | `click_to_call` | header + CTA | | |
| {{Zalo / Messenger}} | widget | `zalo` / `messenger` | | | |
| {{Giỏ hàng / mua}} (e-commerce) | | `add_to_cart` / `purchase` | | | |

Heatmap/recording tool: {{Clarity / Hotjar — đã gắn trên: …}}.

## 2. Path theo cụm intent (≤3 click, không dead-end)

| Cụm intent (topical map) | Landing vào (page type) | Bước giữa | Điểm chuyển đổi | CTA chính (1/trang) | CTA phụ | Internal link thương mại (CR-18) | Số click |
|---|---|---|---|---|---|---|---|
| {{Core thương mại: "dịch vụ X"}} | service page | — | form/gọi | {{...}} | {{...}} | — | 1 |
| {{So sánh / giá}} | bảng giá | service | form | | | | 2 |
| {{Outer blog "cách chọn X"}} | blog | service liên quan | form | {{CTA cuối bài}} | | {{anchor tự nhiên sau đoạn justify}} | 2–3 |
| {{Hỗ trợ / FAQ}} | FAQ | | chat | | | | |

## 3. Site-wide (CR-01…05)

| Item | Quyết định | Spec cho Coder (đo được) |
|---|---|---|
| Header/nav + CTA liên hệ mọi trang, sticky mobile | {{...}} | {{vị trí, kích thước, tel: link}} |
| Footer có mục đích | | |
| Hệ CTA phân cấp (màu/kích thước chính-phụ) | | |
| Form chuẩn (field tối thiểu, success state) | | |
| Chat/widget không che CTA mobile | | |

## 4. Funnel GA4 sẽ dựng (CR-19)

Landing ưu tiên: {{danh sách theo traffic × ranking × ROI (CR-08)}} → funnel: {{landing → bước giữa → conversion}}. Đọc lần đầu: {{cuối P2}}.

## Done-criteria

- [ ] Mọi điểm chuyển đổi có event + verify ngày (G1).
- [ ] Mỗi cụm intent có path ≤3 click, 1 CTA chính, không dead-end.
- [ ] Spec site-wide đo được, không đụng cấu trúc đã lock (#11).
- [ ] index.md dòng #34 + log.md update; QC PASS.
