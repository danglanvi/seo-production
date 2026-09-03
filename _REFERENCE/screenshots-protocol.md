# Screenshots protocol

> Tách từ `CLAUDE.md` (§8) ngày 2026-09-02 (v2026.09.2) để file luật gọn — nội dung giữ nguyên văn. Router trỏ tới file này khi task cần.

## §8. Screenshots

1. Mọi ảnh chụp (SERP, AI Overview, GSC, site mình, đối thủ, tool) lưu **NGAY** vào `02-raw/screenshots/` đúng sub-folder (`own-site/` · `competitors/` · `serp-ai/` · `tools/`) — không để ảnh chỉ trong chat hoặc temp.
2. Naming: `YYYYMMDD_<subject-slug>_<viewport|scope>.png` — vd `20260717_q-iphone-15-cu_aio.png`, `20260717_gsc-performance-28d.png`.
3. Mỗi đợt chụp → 1 entry log op `capture`, ghi "Dùng cho: <deliverable path hoặc công đoạn #n>".
4. Deliverable nhúng ảnh bằng relative path `![](../02-raw/screenshots/…)` — không copy ảnh vào WS folder.
5. Ảnh immutable — không sửa/đè ảnh cũ; chụp lại = file mới ngày mới. Protocol đầy đủ 6 điều: `02-raw/screenshots/README.md`.

---
