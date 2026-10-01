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

## 0. Readiness · cơ chế · pattern (bước 0 skill `cro-audit`)

Readiness: {{A research + sửa + rollout | B A/B — lý do}} · Cơ chế: {{chính (+ phụ)}} · Loại trang soi: {{2–4}} · Outcome: {{định nghĩa + nguồn ghi}} — tracking: {{chưa có / đang gắn / PASS QA ngày}} · Dev/owner sửa web: {{ai, SLA}} · Giới hạn: {{…}}.

## 1. Điểm chuyển đổi & tracking (gate G1 — xong ≤ T3)

> ≤5 event → điền rút gọn A–G tại đây (outcome/mẫu số · event contract · spec GTM · kênh AI nếu có · đối soát · ca QA · owner). Nhiều hơn hoặc có ecommerce/ATS/CRM → tách `<CLIENT>_measurement-plan_v<N>.md` + `tracking-qa` (skill `cro-measurement-plan`). Tên event theo contract mới; site đã có tên legacy (`form_submit`, `zalo`, `messenger`) thì ghi mapping + ngày chuyển, không tạo event trùng chỉ để đạt CR-06.

| Điểm chuyển đổi | Cơ chế | GA4 event (contract) | Điều kiện bắn (nghiệp vụ, không phải click/HTTP 200) | Nguồn xác nhận outcome | QA (ngày, PASS/FAIL/N/A) | Owner |
|---|---|---|---|---|---|---|
| {{Form tư vấn}} | form | `generate_lead` (`form_id`, `lead_type`) | {{callback plugin / success:true}} | {{Sheet lead / CRM}} | {{plan}} | {{Dev khách}} |
| {{Gọi}} | gọi | `click_to_call` (`position`) | click `tel:` (đo click, không xác nhận cuộc gọi) | {{nhật ký gọi}} | | |
| {{Zalo / Messenger}} | chat | `click_zalo` / `click_messenger` | click hostname `zalo.me` / `m.me` | {{Zalo OA / inbox}} | | |
| {{Giỏ hàng / mua}} (ecommerce) | giỏ hàng | `add_to_cart` / `purchase` (`transaction_id`) | dataLayer sau backend tạo đơn | {{backend đơn}} | | |
| {{Ứng tuyển}} (job) | apply | `apply_start` / `application_complete` | ATS trả `application_id` | {{ATS}} | | |

Metric: {{tử số / mẫu số / đơn vị / population / cửa sổ}}. Heatmap/recording tool: {{Clarity / Hotjar — đã gắn trên: …}}.

## 2. Path theo cụm intent (≤3 click là diagnostic — vượt phải khai lý do; không dead-end)

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

- [ ] Mọi điểm chuyển đổi có event theo contract + trạng thái QA (plan / PASS / FAIL / N/A) — G1 pending thì phần research/blocker/brief vẫn hoàn tất, không giả PASS.
- [ ] Mỗi cụm intent có 1 outcome ưu tiên với thứ bậc CTA, không dead-end; path >3 click có lý do ghi rõ.
- [ ] Blocker P0 site-wide (nếu có) đã ghi ở §3 với nhãn P/R/E, bất kể ranking.
- [ ] Spec site-wide đo được, không đụng cấu trúc đã lock (#11).
- [ ] index.md dòng #34 + log.md update; QC PASS.
