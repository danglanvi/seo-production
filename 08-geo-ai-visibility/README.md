# 08 — GEO · AI Visibility (WS GEO)

1. **Mục đích**: Đo và tăng khả năng brand được AI engines trích dẫn (AI Overviews, AI Mode, ChatGPT, Perplexity).
2. **Công đoạn phụ trách** (lớp GEO v2 — 6 điểm chạm, `02-raw/knowledge/sop/09-timeline/lop-geo-v2.md`): #14 (G0+G1, gate G-T1) · #13 (G2 entity, gate G-ENT — phối hợp WS14 Entity) · #21 (G3 đợt 1 + G4) · #24 (G5 giữa kỳ) · #27 (G1 verify) · #28 (G3 đợt 2 + fan-out) · #32/#33 (G5 báo cáo + handover).
3. **Deliverable chuẩn**: GEO baseline, report đợt G3 — naming `<CLIENT>_geo-baseline_v<N>.md` · `<CLIENT>_geo-dot-<1|2>_v<N>.md` · `<CLIENT>_Fanout-Cluster-Map_<topic>_v<N>.md`.
4. **Template**: `_TEMPLATES/geo-baseline.md` (#14). Đợt G3 và cluster map chưa có template riêng — dùng khung output của skill tương ứng, giữ naming trên.
5. **Checklist QC**: AX1-AX7 trong `02-raw/knowledge/sop/08-onpage-checklist.md` (chấm riêng, không gộp điểm /23) + DoD trong `_TEMPLATES/geo-baseline.md`.
6. **Skill gọi**: `skills/geo-tracking-prompt-selection/` (#14, #24, #32) · `skills/geo-fanout-research/` (#28 và #10 — trước outline) · `skills/geo-content-optimization/` (#21, #28). Cheat-sheet: `02-raw/knowledge/cheat-sheets/ws08-geo.md`.
7. **Done-criteria**: Baseline đo được (prompt set theo funnel + citation share brand vs đối thủ); mỗi đợt FS/AIO có danh sách query + kết quả cite.

Ghi chú:

- Lịch đo cố định: T1 baseline / T6 giữa kỳ / T10 báo cáo — tick bảng C `index.md`.
- Evidence AI answer (screenshot) lưu `02-raw/screenshots/serp-ai/` theo protocol, deliverable nhúng bằng relative path.
