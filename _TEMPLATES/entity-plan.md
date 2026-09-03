---
client: "{{CLIENT}}"
cong_doan: 13
ws: 14-entity
phoi_hop: 08-geo-ai-visibility · 06-onpage-internal-link (thực thi schema/onpage)
pic: "{{SEO Lead Project}}"
thuc_thi: "{{Content Leader (bài entity) · SEO (schema, NAP, profile) · Coder (nếu cần)}}"
gate: "G-ENT (GE-11) — hạn ≤15 ngày đầu T3"
status: draft
version: v1
---

# {{CLIENT}} — Entity plan (G2 Source-of-truth & Entity)

> Naming: `{{CLIENT}}_entity-plan_v{{N}}.md` → `14-entity/`. Checklist chấm: `02-raw/knowledge/sop/06-self-checklist/tier-1-entity.md` (EN-01…EN-16, P0 6 item) + `sop/04-entity-optimization.md` + `checklist-entity-onsite-web.md`. Guideline vị trí trong dự án: `sop/09-timeline/lop-geo-v2.md` §G2. Gate G-ENT ghi `gate: <verdict>` vào dòng #13 `index.md` + log op `gate`.
> Nguyên tắc: entity là **điều kiện vào shortlist** của cả Google lẫn AI engine — `site:domain` phải trả lời được câu thương mại bằng text chính chủ; "official"/"site:" trong fan-out là triệu chứng đã ở shortlist, không phải nguyên nhân. Không nhồi chữ "official".

## 1. Brand Info Pack (EN-01) — nguồn sự thật duy nhất

| Trường | Giá trị chính chủ | Nguồn xác nhận (khách) | Đã đồng bộ ở |
|---|---|---|---|
| Tên pháp lý / tên thương hiệu / viết tắt | {{...}} | {{ĐKKD / brand guideline}} | {{web, GBP, social, directory}} |
| NAP (địa chỉ, SĐT, email) — 1 format duy nhất | {{...}} | | |
| Founder / người đại diện (Person entity) | {{...}} | | |
| Ngành, sản phẩm/dịch vụ lõi, thị trường | {{...}} | | |
| Định danh ngoài: MST, Wikidata/Wikipedia (nếu có), MXH chính | {{...}} | | |
| Câu định nghĩa 1 dòng (E-A-V) dùng chung mọi kênh | "{{Brand}} là {{loại thực thể}} cung cấp {{giá trị}} cho {{ai}} tại {{đâu}}." | | |

## 2. Entity Home & bộ trang entity (EN-02, EN-03, EN-04)

| Trang | URL | Nội dung phải có | Status |
|---|---|---|---|
| Trang chủ (entity home) | {{/}} | định nghĩa 1 dòng + NAP + sameAs + dịch vụ lõi | {{todo/done}} |
| Giới thiệu | {{/gioi-thieu}} | lịch sử, năng lực, con người, bằng chứng (số/giải/chứng nhận có nguồn) | |
| Author / Founder (Person) | {{/tac-gia/...}} | credential thật, kinh nghiệm first-hand, link social | |
| Trang theo mô hình DN (chi nhánh, đối tác, chính sách, giá) | {{...}} | trả lời câu thương mại bằng text (không PDF, không JS-only) | |

## 3. Schema & @id graph (EN-06)

| Type | Trang | @id | sameAs | Verify (Rich Results / validator) |
|---|---|---|---|---|
| Organization | / | {{#organization}} | {{MXH, Wikidata, directory}} | {{☐}} |
| Person (founder/author) | {{...}} | | | |
| LocalBusiness (nếu local) | {{...}} | | | |

## 4. Off-site (EN-05, EN-07…EN-09, EN-10 nếu local)

| Kênh | Tài khoản | NAP khớp? | Mô tả dùng câu định nghĩa 1 dòng? | Link về entity home | Owner | Hạn |
|---|---|---|---|---|---|---|
| Google Business Profile | | | | | | |
| Facebook / LinkedIn / YouTube | | | | | | |
| Directory / citation VN ({{danh sách}}) | | | | | | |
| Google Stack brand | | | | | | |

## 5. Test G-ENT — `site:domain` answerability (GE-11)

Chạy 5-10 câu khách hay hỏi (giá, tính năng, so sánh, chính sách, ở đâu, ai đứng sau). Pass = có trang chính chủ trả lời **bằng text** trong kết quả `site:`.

| # | Câu hỏi thương mại | `site:{{domain}}` trả lời được? | URL trả lời | Việc phải làm nếu ❌ |
|---|---|---|---|---|
| 1 | {{giá dịch vụ X}} | {{✅/❌}} | | |
| 2 | {{so sánh gói}} | | | |
| … | | | | |

**Verdict G-ENT:** {{PASS / FAIL — lý do}} · ngày {{...}} · người chốt {{SEO Lead Project}}

## 6. Tracking & bàn giao (EN-15, EN-16)

- Verify entity recognition: {{Knowledge Panel / brand SERP / AI hỏi "{{Brand}} là gì" — kết quả + ngày}}
- File quản lý profile/citation bàn giao khách: {{link}} (mục 1 handover-checklist).

## Done-criteria

- [ ] EN-01, 02, 05, 06 (P0-T1) pass cuối T1; EN-07…09 pass cuối T3.
- [ ] Bảng 5 có ≥5 câu, verdict ghi vào dòng #13 `index.md` + log op `gate`.
- [ ] Không có claim/số/giải thưởng nào trong trang entity thiếu nguồn.
- [ ] Đợt GEO #21 chỉ mở sau khi verdict = PASS.
