# 14 — Entity (WS Entity)

1. **Mục đích**: Làm website thành **Entity Home** được Google và AI engine nhận diện đúng — brand info một nguồn sự thật, bộ trang entity, schema @id graph, NAP đồng bộ onsite–offsite, verify recognition. Tách khỏi WS 06 (onpage/IL là tối ưu trên URL đã có content; entity là lớp danh tính của cả thương hiệu, chạy cuối T1 → T3 và duy trì).
2. **Công đoạn phụ trách**: **#13** (Entity onsite/offsite + Content Entity, GEO G2 source-of-truth, **gate G-ENT** — mốc cứng ≤15 ngày đầu T3). Phối hợp: WS 08 GEO (G2/G3), WS 03 (audit entity), WS 05 + fork Content Production (bài entity).
3. **Deliverable chuẩn**: `<CLIENT>_entity-plan_v<N>.md` (bắt buộc) · `<CLIENT>_entity-profiles_v<N>.md` (bảng quản lý NAP + profile offsite, EN-16 — tuỳ dự án).
4. **Template**: `_TEMPLATES/entity-plan.md`. Audit hiện trạng trước khi lập plan: `_TEMPLATES/audit-entity.md` → lưu `03-audits/entity/`.
5. **Checklist QC**: `02-raw/knowledge/sop/06-self-checklist/tier-1-entity.md` (EN-01…EN-16, P0 6 item — gate cuối T1: EN-01/02/05/06; gate cuối T3: EN-13/14 nếu chạy tactic gated + EN-15) + `sop/04-entity-optimization.md` + `checklist-entity-onsite-web.md` + `tier-1-social-google-stack.md` (phần offsite).
6. **Skill gọi**: `skills/entity-seo-plan/` (xương sống) · `skills/schema-markup-generator/` (EN-06) · `skills/geo-tracking-prompt-selection/` (EN-15 — kiểm AI có cite brand không). Cheat-sheet: `02-raw/knowledge/cheat-sheets/ws06-onpage-il.md` phần entity.
7. **Done-criteria**: Brand Info Pack khách xác nhận; Entity Home + bộ trang entity live; NAP một format duy nhất trên mọi kênh; schema Organization/Person validate pass; offsite đồng bộ; **gate G-ENT có verdict** ghi vào dòng #13 `index.md` + log op `gate`.

Ghi chú:

- **Gate G-ENT (GE-11) chặn #21**: `site:domain` phải trả lời được 5–10 câu thương mại cơ bản bằng text chính chủ; chưa pass thì KHÔNG mở đợt GEO G3. Mốc cứng §6.2.
- **Bài entity viết ở fork** `Content Production - <client>/` (content-type Entity, cửa sổ cuối T1 → ≤15 ngày T3). WS này giữ plan + trạng thái từng trang + link, không viết prose.
- **Phân vai với WS 06**: schema/onpage của từng URL thường do trạm 06 thực thi theo spec của entity plan; đổi lại, quyết định "entity nào, trang nào là source-of-truth, NAP viết thế nào" là của trạm này. Xung đột → entity plan thắng ở tầng danh tính, P-series thắng ở tầng tối ưu URL.
- Không lưu mật khẩu tài khoản social/directory trong repo — chỉ ghi URL profile + trạng thái + người giữ.
