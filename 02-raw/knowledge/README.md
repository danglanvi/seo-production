# Knowledge pack — checklist & SOP đóng gói theo dự án

Bản đóng gói READ-ONLY từ kho `SEO Knowledge/Semantic SEO A - Z/sop/`. Nguồn gốc + ngày sync từng file: xem `_MANIFEST.md`. Path dưới đây tính từ `02-raw/knowledge/`.

## 1. Ma trận WS ↔ checklist

| WS | Folder | Checklist trong knowledge pack | Ghi chú |
|---|---|---|---|
| Context | 00-client-context | — (DoD nằm trong template) | |
| Strategy | 01-strategy-okrs | — (DoD template okrs) | |
| Audit | 03-audits | sop/05-audit-checklist.md · sop/06-self-checklist/tier-3-audit-configuration.md · sop/06-self-checklist/tier-3-technical-advance.md | |
| Structure | 04-structure-ux-cro | sop/07-visual-semantic.md (Bước 0-8 — viết tắt B0-B8 — + RACI) | Bản chưng cất — deep theory ở kho gốc |
| Content plan | 05-content-plan | sop/01-topical-map.md (DoD 15) · sop/02-content-brief.md · sop/06-self-checklist/tier-1-outline-am.md · sop/06-self-checklist/tier-1-content-writing.md (QC bài) | Bài viết chạy ở fork `Content Production - <client>/` |
| Onpage & IL | 06-onpage-internal-link | sop/08-onpage-checklist.md (P0 → /23 → /31 → /39) · sop/03-internal-linking.md · sop/04-entity-optimization.md | |
| Offpage | 07-offpage | — (DoD gate-offpage-decision + backlink-campaign trong `_TEMPLATES/`) | |
| GEO | 08-geo-ai-visibility | AX1-AX5 trong sop/08-onpage-checklist.md · DoD geo-baseline (`_TEMPLATES/`) | |
| Reporting | 09-reporting | — (DoD bao-cao-thang + `_TEMPLATES/account/`) | |
| Client mgmt | 10-client-management | — (DoD kick-off template) | |
| Handover | 11-handover-maintenance | sop/09-timeline/khung-duy-tri.md · handover-checklist (`_TEMPLATES/`) | |
| Feedback | 12-feedback-lessons | — (format feedback-entry `_TEMPLATES/`) | |

Xuyên suốt:

| Phạm vi | File |
|---|---|
| Mọi thao tác QC | sop/06-self-checklist/README.md (3-Level Review) · tracking-schema.md |
| QC Tier 2 | sop/06-self-checklist/tier-2-project-specific.md — chỉ item được bật tại kick-off (#12) |
| Timeline dự án | sop/09-timeline/10-thang-thuc-day.md (khung 10 tháng + biến thể 8/12) · sop/09-timeline/README.md |
| Nạp nhanh khi Work | cheat-sheets/ws<XX>-*.md (6 file, WS03→WS08 — 1 trang per WS) |

## 2. Quy ước wikilink đứt

1. Wikilink `[[...]]` trong pack là link đứt CÓ CHỦ ĐÍCH — trỏ về wiki Semantic SEO (436 file, không đóng gói theo dự án).
2. Không tạo file mới để "vá" wikilink. Không xóa hoặc sửa wikilink.
3. Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.
4. Wikilink là tín hiệu có tầng lý thuyết sâu hơn; checklist trong pack đủ để vận hành.

## 3. Luật re-sync

1. knowledge/ READ-ONLY trong instance: không sửa, không thêm, không xóa.
2. Vá nội dung: vá ở kho gốc `SEO Knowledge/Semantic SEO A - Z/sop/` → sync vào master `SEO Production/` → instance nhận qua MIGRATION (xem `MIGRATION.md` root).
3. File copy nguyên giữ tên gốc → re-sync bằng diff: strip banner rồi diff với kho gốc.
4. Mỗi lần re-sync: cập nhật ngày trong banner từng file + cột Ngày sync trong `_MANIFEST.md` + log op refactor.

## 4. Luật nạp

1. Nạp ĐÚNG file theo ma trận mục 1 (khớp ma trận M trong CLAUDE.md). KHÔNG quét cả knowledge/.
2. QC chấm tier nào → nạp đúng file tier đó, không nạp cả 3 tier cùng lúc.
3. Tier 2 chỉ nạp item đã bật tại kick-off (Ghi chú dòng #12 index).
4. Checklist đầy đủ chỉ nạp khi Work công đoạn có checklist hoặc khi QC; Work thường ngày dùng cheat-sheet.
