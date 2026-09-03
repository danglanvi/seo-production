---
name: entity-seo-plan
description: "Lập và chấm Entity plan (công đoạn #13, gate G-ENT): Brand Info Pack, Entity Home, bộ trang entity, Person, NAP, schema @id graph, offsite consistency, verify recognition. Use when: 'làm công đoạn 13', 'entity plan <client>', 'audit entity', 'gate G-ENT', 'brand có được Google/AI nhận diện chưa'."
---

# Entity SEO Plan — biến website thành Entity Home được Google + AI engine nhận diện

Deliverable: `14-entity/<CLIENT>_entity-plan_v<N>.md` theo `_TEMPLATES/entity-plan.md`. Checklist chấm: `02-raw/knowledge/sop/06-self-checklist/tier-1-entity.md` (EN-01…EN-16, P0 6 item) + `sop/04-entity-optimization.md` + `checklist-entity-onsite-web.md`. Gate **G-ENT** ghi `gate: <verdict>` vào dòng #13 `index.md` + log op `gate`; G-ENT pass mới mở #21 (GEO G3).

## Nguyên tắc (không thương lượng)

- Entity là **điều kiện vào shortlist** của cả Google lẫn AI engine: `site:domain` phải trả lời được câu thương mại bằng text chính chủ. "Official" trong fan-out là triệu chứng đã ở shortlist, không phải nguyên nhân — không nhồi chữ "official".
- **Một nguồn sự thật** (Brand Info Pack EN-01): tên pháp lý/thương hiệu/viết tắt, NAP 1 format, founder, ngành, định danh ngoài (MST, Wikidata, MXH), câu định nghĩa E-A-V 1 dòng. Mọi kênh copy từ đây; lệch = lỗi P0.
- Organization schema đầy đủ **chỉ ở Entity Home**, trang khác reference `@id`. Person schema cho founder/author có sameAs. Không @id loop, không 301 spam (EN-13/14 gated — cần approval bằng văn bản).
- Onsite trước, offsite sau: gate cuối T1 (EN-01, 02, 05, 06) phải pass mới sang social/directory/Google Stack.

## Quy trình 5 bước

| Bước | Làm gì | Bằng chứng |
|---|---|---|
| 1. Audit hiện trạng | Knowledge Panel có/không · `site:` + brand query · schema hiện có (Rich Results Test) · NAP rải rác ở đâu (footer, liên hệ, GBP, social, directory) · Wikidata/Wikipedia · AI engine hỏi "X là gì" có cite domain không | bảng EN-01…16 trạng thái ĐẠT/KHÔNG + screenshot `02-raw/screenshots/own-site/` |
| 2. Brand Info Pack | Điền mục 1 template với khách xác nhận (ĐKKD, brand guideline) | file pack ký nhận trong `00-client-context/` hoặc mục 1 template |
| 3. Onsite plan | Entity Home (home + giới thiệu) · bộ trang entity theo mô hình DN (about, đội ngũ, tuyển dụng, chính sách, liên hệ, đại lý…) · Person page · NAP đồng bộ · schema Organization/Person/@id graph → giao Coder/Content Leader với deadline | mục 2–4 template + bài entity viết ở fork Content Production (content-type Entity, cửa sổ cuối T1 → ≤15 ngày T3) |
| 4. Offsite plan | Social profiles đồng bộ bio/NAP · Google Stack · directory/citation VN · GBP (local) · syndication không IFTTT/Zapier | mục 5 template, mỗi kênh 1 dòng: URL · trạng thái · ngày |
| 5. Verify + tracking | EN-15: brand SERP, Knowledge Panel, AI answer cite, Ahrefs brand mention; EN-16 file quản lý bàn giao | mục 6 template + verdict G-ENT |

Skill liên quan: `schema-markup-generator` (bước 3), `geo-tracking-prompt-selection` (bước 5 — prompt hỏi AI về brand), `internal-linking` (link bộ trang entity về Entity Home). Wiki nền (máy master): Entity Identity Management · Entity Home · E-A-V · Brand Entitization Playbook — instance không có wiki thì dựa hoàn toàn vào `sop/04` + tier-1-entity.

## Output chuẩn

Mỗi finding/action: **phạm vi · hiện trạng · việc · owner · deadline · item EN-xx**. Không viết "tối ưu entity" chung chung. Kết bằng: verdict G-ENT đề xuất (PASS / FAIL + item fail) + 3 việc P0 tuần này.
