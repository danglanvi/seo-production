# slide-map.md — map slide ↔ nguồn digest ↔ exemplar template (nạp ở Pha 3 RENDER)

> **LUỒNG PHÂN TÍCH CHUẨN (feedback SEO Lead 22/07/2026 — không tự đảo thứ tự):**
> Overview KPI → **1. PV Joblisting (JL)** → **2. PV Job Detail** → **3. PV Blog (SEO/non-SEO)** → **4. PV Homepage (+ Nhà tuyển dụng, ngoài cam kết)** → **Apply** → SOW Plan Tuần → Next week → Cần client hỗ trợ → Q&A.
> Trong đó cụm JL bắt buộc break 4 slide nhỏ: **1.1 theo Intent → 1.2 theo ngành nghề → 1.3 theo khu vực → 1.4 top pages JL**.
> Viết tắt: **JL = Job Listing** · JD = Job Detail · NTD = Nhà tuyển dụng.

| Thứ tự | Slide | Exemplar | Nguồn data (digest `sections.*`) | Ghi chú render |
|---|---|---|---|---|
| 1 | Cover | cover | meta | |
| 2 | Agenda | agenda | — | 4 mục cố định |
| 3 | Overview KPI — run-rate tuần | runrate | `runrate_tuan.summary` + `.weeks` (dòng tuần hiện tại class `hl`) | KHÔNG thêm slide dashboard/Looker lặp thông tin này — 2 slide trùng 1 nội dung là lỗi (feedback 22/07) |
| 4 | 1. KPI Organic PV per nhóm trang (BẢNG 1) | bảng WoW 2 cột | `bang1_overview_wow.rows` | **RENDER ĐỦ MỌI DÒNG** của tab: khối TOÀN SITE (JL, JD, Blog toàn bộ, NTD, Tool, Homepage, tổng) + khối CAM KẾT SEO (JL, JD, Blog CV/Lương, Tool, tổng). Nếu tab không có dòng "Blog còn lại (non-SEO)" → TỰ DẪN XUẤT = Blog toàn bộ − Blog CV/Lương, đánh dấu (dẫn xuất). Thiếu dòng nhóm nào so với tab = FAIL tự kiểm |
| 5 | 1.1 JL theo Intent | bảng full-width | `danh_gia_joblisting` (bảng "1. Pageview theo Intent") | Đủ cột PV/Clicks/Imp/CTR/Pos WoW + Grand Total |
| 6 | 1.2 JL theo ngành nghề | bảng full-width | `danh_gia_joblisting` (bảng "2. Pageview theo ngành nghề") | ⚠ Kiểm tra header kỳ dữ liệu của bảng — nếu cột "tuần trước" giữ kỳ cũ (team chưa refresh) → ghi đúng kỳ theo header vào `.data-meta` + flag trong insights, KHÔNG im lặng |
| 7 | 1.3 JL theo khu vực | bảng full-width | `danh_gia_joblisting` (bảng "3. Pageview theo khu vực") | Top 10-12 khu vực theo PV + ghi chú như slide 6 |
| 8 | 1.4 Top pages JL bị ảnh hưởng | top movers | `top_movers_gsc_jlp` | Nằm TRONG cụm JL (không tách ra sau) — feedback 22/07 |
| 9 | 2. Job Detail theo nhóm ngành | bảng full-width | `danh_gia_jobdetail` (khối Δ PV + ngành ưu tiên) hoặc `jobdetail_nhom_nganh` (workbook Data phân tích) | |
| 10 | 3. Blog (SEO / non-SEO) | bảng full-width | `danh_gia_blog_tab` hoặc `danh_gia_blog` | Tách rõ subtotal SEO vs non-SEO |
| 11 | 4. Homepage + NTD (ngoài cam kết) | bảng WoW 2 cột | dòng Homepage/NTD trong bang1 + `danh_gia_ntd` | Homepage PV lớn nhưng SEO không tác động — vẫn đưa vào theo lệ các tuần (feedback 22/07); ghi rõ "ngoài cam kết" |
| 12+ | Apply (Applythanks) theo Intent / khu vực / ngành | bảng WoW 2 cột (+full-width khi cần) | `danh_gia_apply` + `joblisting_intent_apply` + `apply_khuvuc` + `apply_nganh` + `apply_thanks_pivot` | NHẬN XÉT bắt buộc trả lời "VÌ SAO tăng/giảm" per nhóm biến động lớn (rubric mục Apply) — nối với PV/clicks landing nhóm đó |
| 13 | SOW: **Plan Tuần** | SOW | `plan_tuan_truoc` (template mới) hoặc `sow_status.weeks[<tuần hiện hành>]` | Tiêu đề "SOW: Plan Tuần — <marker tuần>" (KHÔNG ghi Plan tháng); bảng show **ĐỦ task của tuần** kèm status, không chỉ dòng trễ; chips đếm theo tuần đó |
| 14 | Next week plan | SOW (bảng) | `plan_tuan_ke` hoặc `sow_status.weeks[<tuần kế>]` | Đủ task tuần kế; chưa có data → khung + đánh dấu Vincent/Lead điền |
| 15 | Hạng mục cần client hỗ trợ | support | `viec_phoi_hop` | Trống Description — điền trong họp |
| 16-19 | 3rd Party View monthly (tùy tuần có data) | 3rd party | tab 3rd-party khi xác định được / Ahrefs MCP (minh họa) | |
| 20 | Q&A | qna | — | |
| 21 | Thank You | thanks | — | |

## Luật render bảng

1. Mỗi giá trị lấy NGUYÊN VĂN từ digest (FORMATTED_VALUE của sheet). Không tự làm tròn lại.
2. Δ dương → `pos`, âm → `neg`, 0/rỗng → `mut`. Nhóm thuộc cụm KPI → `kpi-row`; dòng tổng → `total`.
3. Bảng dài hơn slide → cắt theo TOP |Δ| + dòng tổng + ghi "top N theo biến động — bảng đủ trong file data". NGOẠI LỆ: BẢNG 1 (slide 4) và bảng task Plan Tuần (slide 13) phải ĐỦ dòng.
4. Mọi slide data có `.data-meta` (nguồn + kỳ dữ liệu ĐÚNG theo header bảng nguồn) — thiếu là FAIL tự kiểm.
5. Ảnh (nếu dùng thang capture) nhúng base64; ảnh gốc ở `02-raw/screenshots/`.
6. `grep '{{'` deck final = 0.
