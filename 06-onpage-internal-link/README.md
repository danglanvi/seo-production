# 06 — Onpage & Internal Link (WS Onpage & IL)

1. **Mục đích**: Thực thi onpage theo batch, internal link semantic trên URL đã có content — VÀ khâu đăng/sửa bài trên WordPress (publish thuộc bạn SEO, không thuộc team content).
2. **Công đoạn phụ trách**: #7 (phần execute — plan ở WS 03), #18, #23 + phần PUBLISH của #15/16/19 (bài nhận từ fork content qua Google Sheet đăng bài).
3. **Deliverable chuẩn**: onpage batch report, IL plan — naming `<CLIENT>_<slug>_v<N>.md` (vd `<CLIENT>_onpage-batch-t3_v1.md`); bài đăng WP tracked trong Google Sheet đăng bài (schema 11 cột của kit).
4. **Template**: `_TEMPLATES/onpage-batch.md` · `_TEMPLATES/internal-link-plan.md`. Entity (#13) chuyển sang **WS `14-entity/`** từ v2026.09.3 — trạm này chỉ thực thi schema/onpage từng URL theo spec của entity plan. Bài từ fork nhận qua `05-content-plan/content-tracking/delivered/` (content_sync.py) hoặc Google Sheet đăng bài.
5. **Checklist QC**: `02-raw/knowledge/sop/08-onpage-checklist.md` (P0 → /23 → /31 → /39) + `02-raw/knowledge/sop/03-internal-linking.md` + `02-raw/knowledge/sop/11-publish-wp.md` (khi đăng/sửa bài WP).
6. **Skill gọi**: `skills/seo-onpage/` · `skills/internal-linking/` · `skills/schema-markup-generator/` · `skills/image-seo-optimize/`. Đăng/sửa WP: `wp-publish-workflow-kit` (repo riêng — CLAUDE.md root §11). Cheat-sheet: `02-raw/knowledge/cheat-sheets/ws06-onpage-il.md`.
7. **Done-criteria**: Batch onpage PASS /23 (tier bật theo kick-off, ghi tại dòng #12 `index.md`); IL plan thực thi xong, orphan = 0; bài đăng WP có verify kép (WP readback + Sheet readback).

Ghi chú:

- Luật scoring sop/08: P0 là gate chặn — xử lý P0 trước, sửa nền trước khi chấm tiếp các nhóm sau.
- Dây chuyền chuẩn: content publish → +10-15 ngày onpage → +15-30 ngày internal link (cuốn chiếu theo chuỗi, không chờ gộp cuối kỳ).
- Mốc cứng: onpage URL SEO xong T4.
