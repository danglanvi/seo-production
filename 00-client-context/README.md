# 00 — Client Context (WS Context)

1. **Mục đích**: Nguồn sự thật duy nhất về client — mọi Work/QC chạm KPI hoặc context phải đọc folder này trước.
2. **Công đoạn phụ trách**: #1 (Ký hợp đồng · OKRs năm & quý), #3 (Marketing Foundation).
3. **Deliverable chuẩn**: 3 file cố định `client-profile.md` · `marketing-foundation.md` · `kpi-commitments.md` + `hop-dong-cam-ket.md` (tạo lúc SETUP bước 3 từ `_TEMPLATES/hop-dong-cam-ket.md` — bản chưng cất HĐ đầy đủ) — cập nhật tại chỗ, không version theo naming WS.
4. **Template**: skeleton có sẵn trong folder; trích hợp đồng theo schema `_TEMPLATES/hop-dong-cam-ket.md`.
5. **Checklist QC**: DoD ghi cuối mỗi skeleton (WS này không có checklist riêng trong `02-raw/knowledge/`).
6. **Skill gọi**: — (fill bằng protocol "setup client <tên>" trong `SETUP.md`).
7. **Done-criteria**: 3 file `status: stable`, sạch placeholder; HĐ đã trích vào `kpi-commitments.md`.

Luật:

- Master chỉ giữ skeleton placeholder — KHÔNG hard-code dữ liệu client thật vào master.
- Instance: fill khi setup; mỗi lần sửa phải append `log.md` (op `ingest` hoặc `bookkeep`).
- Nguồn gốc (HĐ, proposal, tài liệu khách) nằm ở `02-raw/contracts-proposals/` + `02-raw/client-docs/`; folder này chỉ giữ bản chưng cất.
- Verify sau setup: `grep -rn "{{" 00-client-context/` phải = 0 hit (SETUP bước 9).
