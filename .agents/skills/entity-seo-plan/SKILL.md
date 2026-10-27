---
name: entity-seo-plan
description: "Lập Entity plan trong repo Production hoặc audit nguồn sự thật thương hiệu theo GEO GE-11…15. Tách gate Entity/EN và GEO. Dùng khi: 'công đoạn 13', 'entity plan [client]', 'audit entity', 'gate G-ENT', 'brand được Google/AI nhận diện chưa', kiểm Entity Home hoặc geo-audit gọi."
compatibility: "Gói skill kèm references. Router geo-audit cần bundle 5 skill mảng; chế độ audit nhận evidence dán/export hoặc công cụ đọc phù hợp."
metadata:
  version: "1.2.1"
---

# Entity SEO Plan — biến website thành Entity Home được Google + AI engine nhận diện

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

**Chế độ Entity/EN trong repo Production:** deliverable `14-entity/<CLIENT>_entity-plan_v<N>.md` theo `_TEMPLATES/entity-plan.md`. Checklist chấm: `02-raw/knowledge/sop/06-self-checklist/tier-1-entity.md` (EN-01…EN-16, P0 6 item) + `sop/04-entity-optimization.md` + `checklist-entity-onsite-web.md`. Gate **G-ENT [Entity/EN]** ghi `gate: <verdict>` vào dòng #13 `index.md` + log op `gate`; G-ENT pass mới mở #21 (GEO G3).


**Trước khi chấm GEO:** nếu chưa nạp hợp đồng v1.1 trong phiên, đọc `references/audit-contract.md` (bản đóng gói): UNKNOWN khác N/A, điểm nhị phân + độ phủ, gate theo URL/engine và bàn giao finding. Quy tắc v1.1 này áp cho các bảng audit GEO bên dưới; changelog chỉ là lịch sử.

## Nguyên tắc (không thương lượng)

- Entity là **điều kiện vào shortlist** của cả Google lẫn AI engine: `site:domain` phải trả lời được câu thương mại bằng text chính chủ. "Official" trong fan-out là triệu chứng đã ở shortlist, không phải nguyên nhân — không nhồi chữ "official".
- **Một nguồn sự thật** (Brand Info Pack EN-01): tên pháp lý/thương hiệu/viết tắt, NAP 1 format, founder, ngành, định danh ngoài (MST, Wikidata, MXH), câu định nghĩa E-A-V 1 dòng. Mọi kênh copy từ đây; lệch = lỗi P0.
- Organization schema đầy đủ **chỉ ở Entity Home**, trang khác reference `@id`. Person schema cho founder/author có sameAs. Không @id loop, không 301 spam (EN-13/14 gated — cần approval bằng văn bản).
- Onsite trước, offsite sau: gate cuối T1 (EN-01, 02, 05, 06) phải pass mới sang social/directory/Google Stack.

## Chọn chế độ

- `audit entity GEO` hoặc `geo-audit` gọi: chỉ đọc `references/geo-entity-checklist.md` và hợp đồng audit đóng gói; trả GE-11…15 + G-ENT [GEO]. Không yêu cầu template, wiki hay EN-01…16.
- Lập/chấm Entity/EN toàn bộ: cần repo Production có template và SOP nêu đầu file; thiếu repo thì yêu cầu đúng gói tài liệu, không tự chạy GEO rồi gọi là audit Entity đầy đủ.
- Giao việc sửa: nhận finding đã duyệt → dùng workflow EN/schema/content phù hợp → kiểm lại item, giữ evidence trước/sau.

## Quy trình 5 bước — chỉ chế độ Entity/EN

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'curl,firecrawl?,ahrefs?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

| Bước | Làm gì | Bằng chứng |
|---|---|---|
| 1. Audit hiện trạng | Knowledge Panel có/không · `site:` + brand query · schema hiện có (Rich Results Test) · NAP rải rác ở đâu (footer, liên hệ, GBP, social, directory) · Wikidata/Wikipedia · AI engine hỏi "X là gì" có cite domain không | bảng EN-01…16 trạng thái ĐẠT/KHÔNG + screenshot `02-raw/screenshots/own-site/` |
| 2. Brand Info Pack | Điền mục 1 template với khách xác nhận (ĐKKD, brand guideline) | file pack ký nhận trong `00-client-context/` hoặc mục 1 template |
| 3. Onsite plan | Entity Home (home + giới thiệu) · bộ trang entity theo mô hình DN (about, đội ngũ, tuyển dụng, chính sách, liên hệ, đại lý…) · Person page · NAP đồng bộ · schema Organization/Person/@id graph → giao Coder/Content Leader với deadline | mục 2–4 template + bài entity viết ở fork Content Production (content-type Entity, cửa sổ cuối T1 → ≤15 ngày T3) |
| 4. Offsite plan | Social profiles đồng bộ bio/NAP · Google Stack · directory/citation VN · GBP (local) · syndication không IFTTT/Zapier | mục 5 template, mỗi kênh 1 dòng: URL · trạng thái · ngày |
| 5. Verify + tracking | EN-15: brand SERP, Knowledge Panel, AI answer cite, Ahrefs brand mention; EN-16 file quản lý bàn giao | mục 6 template + verdict G-ENT |

Skill liên quan: `schema-markup-generator` (bước 3), `geo-tracking-prompt-selection` (bước 5 — prompt hỏi AI về brand), `internal-linking` (link bộ trang entity về Entity Home). Wiki nền (máy master): Entity Identity Management · Entity Home · E-A-V · Brand Entitization Playbook — instance không có wiki thì dựa hoàn toàn vào `sop/04` + tier-1-entity.

## Lăng kính GEO — điểm chạm 3, Bộ NỀN phần C (GE-11…15)

Chạy trong bước 1 khi dự án có GEO, hoặc chạy độc lập khi router gọi. Đọc `references/geo-entity-checklist.md`: input, 5 tiêu chí, evidence và output đều có trong gói. G-ENT [GEO] chỉ lấy GE-11; không thay verdict G-ENT [Entity/EN]. Nếu repo yêu cầu cả hai, ghi hai verdict riêng và chỉ đề xuất hoàn tất khi cả hai PASS.

## Output chuẩn

Mỗi finding/action: **phạm vi · hiện trạng · việc · owner · deadline · item EN-xx**. Không viết "tối ưu entity" chung chung. Kết bằng: verdict G-ENT đề xuất (PASS / FAIL + item fail) + 3 việc P0 tuần này. Có lớp GEO → thêm bảng GE-11…15 (mục Lăng kính GEO) để `geo-audit` gộp vào Bộ NỀN.

## Changelog

- v1.2.1 (2026-10-27): bản root thành bản gốc, bản SEO Production sinh bằng `tools/port-dieu-phoi.py`. Lấy từ bản SEO Production: trigger "brand được Google/AI nhận diện chưa" trong description. Chế độ Entity/EN đã có sẵn ở bản root.
- v1.2 (2026-09-12): tách gate GEO/EN, đóng gói chế độ audit GEO độc lập và bàn giao finding.

- v1.1 (2026-09-12): thêm mục "Lăng kính GEO" GE-11…15 (site: test, trang nguồn sự thật, URL máy bịa, nhất quán kênh, tác giả thật) để chấm Bộ NỀN phần C và nối `geo-audit`; không đổi quy trình 5 bước.
