---
client: "{{CLIENT}}"
cong_doan: "{{5 | 13 | 24 | 27}}"
ws: 03-audits
folder: 03-audits/entity/
pic: "{{SEO Lead Project}}"
status: draft
version: v1
---

# {{CLIENT}} — Entity audit — {{KY}}

> Audit lẻ hạng mục Entity (mục 2.3 của `audit-toan-dien.md`) — hiện trạng trước khi lập `entity-plan.md` (#13) hoặc kiểm giữa kỳ (#24/#27). Naming `{{CLIENT}}_audit-entity-{{ky}}_v{{N}}.md` → `03-audits/entity/`. Checklist: `sop/06-self-checklist/tier-1-entity.md` (EN-01…16) + `sop/04-entity-optimization.md`. Skill: `entity-seo-plan`, `schema-markup-generator`, `geo-tracking-prompt-selection`.

## 1. Nhận diện hiện tại

| Kiểm | Kết quả | Evidence (screenshot `02-raw/screenshots/`) |
|---|---|---|
| Knowledge Panel brand | {{có/không · nội dung}} | |
| `site:domain` + query thương mại chính | {{trả lời được bằng text chính chủ?}} | |
| Brand query SERP: profile nào xuất hiện (social, directory, Wikipedia/Wikidata) | | |
| AI engine (ChatGPT/Gemini/AIO) hỏi "{{brand}} là gì / có uy tín không" | {{cite domain? nói đúng?}} | |
| Ahrefs brand mention / referring domains có anchor brand | | |

## 2. Chấm EN-01…16

| Item | Trạng thái | Finding | Mức độ |
|---|---|---|---|
| EN-01 Brand Info Pack | {{ĐẠT/KHÔNG}} | {{NAP bao nhiêu biến thể}} | |
| EN-02 Entity Home | | | |
| EN-03 Bộ trang entity | | | |
| EN-04 Person/Author | | | |
| EN-05 NAP consistency | | | |
| EN-06 Schema Organization/Person/@id | | {{Rich Results Test}} | |
| EN-07…EN-12 Offsite + syndication | | | |
| EN-15 Verify recognition | | | |

## 3. Action

| # | Action | Phạm vi | Owner | Deadline | Item EN | Status |
|---|---|---|---|---|---|---|
| 1 | {{...}} | {{onsite/offsite}} | {{...}} | {{...}} | {{EN-xx}} | todo |

## Done-criteria

- [ ] Mục 1 đủ 5 kiểm có evidence; mục 2 đủ 16 item.
- [ ] Action P0 (EN-01/02/05/06) có deadline ≤ cuối T1 (dự án mới) hoặc ≤ 30 ngày (giữa kỳ).
- [ ] Kết quả nạp vào `entity-plan.md`; index.md + log.md update.
