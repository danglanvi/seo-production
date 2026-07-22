# slide-map.md — map slide ↔ nguồn digest ↔ exemplar template (nạp ở Pha 3 RENDER)

Cấu trúc deck chuẩn (theo format weekly report GTV — mẫu gốc: deck CareerViet W11, 23 slide). Số slide co giãn theo section thực có data tuần đó; thứ tự GIỮ NGUYÊN. Exemplar = slide mẫu trong `deck-template.html` (12 loại).

| Thứ tự | Slide | Exemplar | Nguồn data (digest.json `sections.*`) | Ghi chú render |
|---|---|---|---|---|
| 1 | Cover | cover | meta (week, range_display) | Điền `{{WEEK_NO}}`, `{{WEEK_RANGE}}` |
| 2 | Agenda | agenda | — | 4 mục cố định |
| 3 | Overview KPI — run-rate tuần | runrate | `runrate_tuan.summary` (2 card) + `runrate_tuan.weeks` (bảng, dòng W hiện tại class `hl`) | Run-rate <100% dùng `rr-pct-bad`; nguồn + kỳ ở `.data-meta` |
| 4 | BẢNG 1 — PV per nhóm trang WoW | bảng WoW 2 cột | `bang1_overview_wow.rows` | Nhóm thuộc cụm KPI → `kpi-row` (tra `page_groups` config); dòng tổng → `total`; NHẬN XÉT phải: cụm KPI trước, toàn site sau |
| 5 | Joblisting theo Intent | bảng full-width | `joblisting_intent_apply` (Apply per intent) + bảng intent PV nếu team có trong workbook tuần | Nếu tuần này digest không có bảng intent-PV → bỏ slide, KHÔNG bịa |
| 6 | Joblisting theo ngành nghề | bảng full-width | `apply_nganh` / bảng ngành PV | như trên |
| 7 | Joblisting theo khu vực | bảng full-width | `apply_khuvuc` / bảng khu vực PV | như trên |
| 8 | Ranking distribution (SpySERP/RankTracker) | capture | ảnh — thang capture (Looker/sheet) | Không có → `.manual-slot` |
| 9 | Job Detail theo nhóm ngành | bảng full-width | `jobdetail_nhom_nganh` | top tăng/giảm bôi bằng `pos`/`neg` |
| 10 | Blog SEO/non-SEO | bảng full-width | `danh_gia_blog` | gộp theo SEO/non-SEO như tab |
| 11 | Homepage | capture hoặc bảng | Looker page / GA4-direct (nếu có quyền) / số từ bang1 | ít data → gộp vào slide 4 note |
| 12 | Top pages bị ảnh hưởng (JLP) | top movers | `top_movers_gsc_jlp` (gainers/losers) | Đây là slide "top page affected" Vincent yêu cầu — luôn có |
| 13 | Top pages Blog | top movers | `top_movers_gsc_blog` | có data mới render |
| 14 | Applythanks per page group + intent/khu vực/ngành | bảng WoW 2 cột (+full-width nếu cần 2 slide) | `apply_thanks_pivot` + `joblisting_intent_apply` + `apply_khuvuc` + `apply_nganh` | NHẬN XÉT: apply cụm cam kết trước |
| 15 | SOW status update | SOW | `sow_status.counts` (chips — lọc key rác không phải status) + `.late` (bảng) | Label plan tháng lấy từ tab; chips: Done/Đang làm/Chưa bắt đầu/Tạm ngưng/Trễ hạn |
| 16 | Next week plan | SOW (bảng) | `sow_status.late` + task tuần kế từ CSV `report_tuan_tasks` (đọc lát nhỏ khi cần) | Vincent chỉnh tay sau — đổ khung + việc P0/P1 |
| 17 | Hạng mục cần client hỗ trợ | support | `viec_phoi_hop` (đề xuất sẵn các mục đang chờ client) | để trống phần Description cho buổi họp |
| 18-21 | 3rd Party View — Tổng site / Job Listing / Blog / Recruiter | 3rd party | tab 3rd-party trong workbook (nếu team duy trì) HOẶC Ahrefs MCP `site-explorer-metrics-history` 4 domain | SVG polyline: scale tuyến tính, x chia đều; ghi rõ nguồn minh họa |
| 22 | Q&A | qna | — | |
| 23 | Thank You | thanks | — | |

## Luật render bảng

1. Mỗi giá trị lấy NGUYÊN VĂN từ digest (đã là FORMATTED_VALUE của sheet — giữ dấu phẩy nghìn, %). Không tự làm tròn lại.
2. Δ dương → `pos`, âm → `neg`, 0/rỗng → `mut`. %/số giữ đúng dấu như nguồn.
3. Bảng dài hơn slide → cắt theo TOP |Δ| + dòng tổng, ghi chú "top N theo biến động — bảng đủ trong file data" + link.
4. Mọi slide data có `.data-meta` (nguồn + kỳ) — thiếu là FAIL vòng tự kiểm.
5. Placeholder `{{...}}` không được sót lại trong deck final — grep trước khi export.
