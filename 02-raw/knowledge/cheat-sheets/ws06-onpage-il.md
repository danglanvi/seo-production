# Cheat-sheet WS06 — Onpage & Internal Link

> Chưng cất từ `02-raw/knowledge/sop/08-onpage-checklist.md` (Tier 1 P0-P23) + `sop/03-internal-linking.md` + `sop/04-entity-optimization.md` — sync 2026-07-17. Cheat-sheet chỉ để định hướng nhanh; khi Work/QC phải mở checklist đầy đủ.

## 1. Mục tiêu WS

Mọi URL publish đạt chuẩn onpage Tier 1 (/23), internal link chạy theo cluster (orphan = 0), site được recognize là Entity Home cho Central Entity.

- Công đoạn phụ trách: **#7** (execute action audit content) · **#13** (Entity onsite/offsite) · **#18** (Internal link semantic) · **#23** (Điều chỉnh content & onpage).

## 2. Input / Output

| Input | Output |
|---|---|
| URL batch + content đã V-Pass (từ fork Content Production) | Onpage batch report → `_TEMPLATES/onpage-batch.md`, lưu `06-onpage-internal-link/` |
| Topical map + SCN (`05-content-plan/`) | IL plan → `_TEMPLATES/internal-link-plan.md` |
| Cấu trúc site + wireframe (`04-structure-ux-cro/`) | Entity checklist (onsite/offsite) + schema đã triển khai |

## 3. Checklist rút gọn (10 dòng — ID đầy đủ trong sop/08, sop/03, sop/04)

1. **P0 Gate:** content chưa V-Pass → KHÔNG onpage, trả về Content. Không có ngoại lệ.
2. **Meta (P1-P5):** URL 3-5 từ đúng folder topical map · Title 50-60 ký tự, keyword 3 từ đầu, KHÁC H1+URL · Meta 150-160 ký tự có CTA · CTR hook Title ↔ detail Meta · H1 cùng predicate với Title, 1 H1 duy nhất.
3. **Heading (P6-P7):** H2 attribute chính, không nhồi keyword / H3 variations + entity MỚI / H4 entity cụ thể; entity đứng đầu heading; câu đầu sau heading khớp format heading.
4. **Body (P8-P16):** Topical Coverage đủ attribute/entity MANDATORY của top 10 (yếu tố mạnh nhất) · mỗi paragraph ≥1 E-A-V · macro terms xuyên suốt, micro terms theo section · bold câu trả lời, không quota · Central Entity + keyword chính trong 100 chữ đầu.
5. **Link (P17-P18):** Contextual Bridge Main→Supplement, vị trí theo link-placement (Main chỉ MC1–MC5), dạng mã theo link-js, không quota số link, anchor = seed query của trang đích · trích nguồn bằng tên trong câu, không quota link ngoài, KHÔNG link đối thủ.
6. **Ảnh (P19-P20):** filename tả nội dung ảnh, gạch ngang không dấu · alt tả đúng ảnh + context, không nhồi keyword · Caption ≠ Alt · `.webp` <150KB, lazy, W/H explicit.
7. **Technical (P21-P23):** Semantic HTML5 (`<main>`, `<article>`, heading hierarchy sạch) · CTA/form/filter hoạt động + Mobile UX · chạy Prompt Tối Ưu Onpage 2 bước (extract → audit đủ attribute MANDATORY).
8. **IL khi publish:** bài link TỚI pillar (≥1) + sibling cùng cluster khi có ngữ cảnh chung (không quota); pillar update link NGƯỢC lại; cross-cluster CHỈ qua Contextual Bridge; anchor descriptive theo intent trang đích, không keyword-stuff.
9. **IL audit tháng:** orphan pages = 0 · pillar >50 inbound cùng cluster → tách sub-pillar · cross-cluster không qua bridge → fix hoặc tạo bridge.
10. **Entity (sop/04):** schema đúng type cho Central Entity + sameAs Wikipedia/Wikidata/social · Entity Home page có URL canonical · Author bio Person schema · NAP nhất quán · mỗi attribute E-A-V có long-form definitive answer, không conflicting statement giữa các page.

## 4. Ngưỡng pass

| Tình huống | Ngưỡng |
|---|---|
| Publish trang mới | Chạy đủ Tier 1 → chấm /23; Tier 2 (+8 → /31) theo quyết định kick-off; Tier 3 (+8 → /39) cho Quality Node/cạnh tranh cao |
| Audit trang cũ | Chạy Tier 1 → 3, DỪNG ở tier có ≥3 item FAIL — sửa nền trước, tối ưu sau |
| AX Extension (GEO) | Chấm riêng, KHÔNG tính vào /39 → xem `cheat-sheets/ws08-geo.md` |
| Internal link | Orphan = 0; mỗi bài đủ pillar + sibling links |
| Review | 3 tầng: Self 100% → verify → Lead random 25-30% (gap dương lớn = cờ đỏ) |

## 5. Skill gọi + luật nạp

| Skill | Khi nào nạp |
|---|---|
| `skills/seo-onpage/` | Mặc định cho mọi batch onpage (chấm P-series) |
| `skills/internal-linking/` | Khi lập/audit IL plan (#18) |
| `skills/schema-markup-generator/` | Chỉ khi gắn schema cho URL theo spec entity plan (`14-entity/`, #13) — schema ≠ lever AI citation |
| `skills/image-seo-optimize/` | Chỉ khi batch có ảnh cần tối ưu bulk |

Luật nạp 80/20: nạp đúng file checklist theo ma trận M, không quét cả `knowledge/`; references/ của skill nạp từng file theo pointer khi step cần.

## 6. 5 lỗi thường gặp

1. Onpage khi content chưa qua P0 gate — tốn công tối ưu bài sẽ bị viết lại.
2. Bold nhiều thay vì bold đúng chỗ (số lượng bold ≈ 0 tín hiệu; bold câu trả lời + 2-3 variations là đủ).
3. Anchor internal link keyword-stuff thay vì contextual — anchor phải khớp intent trang đích.
4. Cross-cluster link thẳng không qua Contextual Bridge — phá boundary của cluster.
5. QC chấm gộp cả nhóm thay vì từng item ID có evidence; hoặc tự hạ ngưỡng để cho qua — cấm theo CLAUDE.md §1.
