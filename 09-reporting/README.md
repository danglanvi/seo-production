# 09 — Reporting (WS Reporting)

1. **Mục đích**: Render kết quả trên KPI đã cam kết — báo cáo tháng/quý/nghiệm thu và case study cuối dự án.
2. **Công đoạn phụ trách**: #30◇ (Đạt KPI cam kết?), #32 (báo cáo kép + case study, T10).
3. **Deliverable chuẩn**: báo cáo tháng/quý, BBNT, case study — naming `<CLIENT>_<slug>_v<N>.<ext>` (vd `<CLIENT>_bao-cao-t03_v1.docx`).
4. **Template**: `_TEMPLATES/bao-cao-thang.md` + bộ `_TEMPLATES/account/` (email, BBNT, quy trình nghiệm thu, SOW-KPI naming).
5. **Checklist QC**: DoD trong `_TEMPLATES/bao-cao-thang.md` + chuẩn bộ `_TEMPLATES/account/` (WS này không có checklist riêng trong `02-raw/knowledge/`).
6. **Skill gọi**: `skills/gtv-client-report/` (⚠ claude-only, chỉ chạy trong Claude Code) · `skills/expert-case-study/`.
7. **Done-criteria**: Báo cáo gửi đúng hạn hằng tháng; tháng cuối: báo cáo kép + BBNT (auto-accept 7 ngày, bảo hành 30 ngày).

Ghi chú:

- Chỉ báo cáo trên KPI trong `00-client-context/kpi-commitments.md` — không tự thêm metric ngoài cam kết.
- Gate #30: verdict ghi `gate: <verdict>` vào `index.md`, log op `gate`; không đạt → về #31 (WS 10) điều chỉnh.
