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
| 5 | 1.1 JL theo Intent | bảng full-width | `danh_gia_joblisting` (bảng "1. Pageview theo Intent") | Đủ cột PV/Clicks/Imp/CTR/**Δ Pos** WoW + Grand Total. **CẤM phân tích "số tổng" của bảng này như xu hướng JL** (bảng chỉ tính trên ~58K URL top PV≥5/tuần trong ~100K URL export — sẽ vênh với JL WoW ở BẢNG 1). Bắt buộc dòng scope-note trên slide: "Bảng tính trên N URL JL thuộc top page (PV≥5/tuần) — chỉ coi cơ cấu nhóm, không so với tổng slide trước" |
| 6 | 1.2 JL theo ngành nghề | bảng full-width | `danh_gia_joblisting` (bảng "2. Pageview theo ngành nghề") | **Bắt buộc cột Δ Pos.** ⚠ Kiểm tra header kỳ dữ liệu — cột "tuần trước" giữ kỳ cũ → ghi đúng kỳ vào `.data-meta` + flag, KHÔNG im lặng |
| 7 | 1.3 JL theo khu vực | bảng full-width | `danh_gia_joblisting` (bảng "3. Pageview theo khu vực") | **Bắt buộc cột Δ Pos.** Top 10-12 khu vực theo PV + ghi chú như slide 6 |
| 8 | 1.4 Top pages JL bị ảnh hưởng | top movers | **`movers_pv_jl.json` (scripts/pv_movers.py — lọc theo ΔPV ≥ ngưỡng config, CHUẨN TEAM)** | Nằm TRONG cụm JL. KHÔNG lọc theo GSC clicks (đã bị SEO Lead đánh "dữ liệu AI lọc sai" 22/07) — clicks/pos chỉ là cột phụ nếu có. Bắt cặp URL-swap: URL rớt ~100% + URL cùng chủ đề tăng đột biến → nghi redirect/đổi URL, hỏi team |
| 9 | 2. Job Detail theo nhóm ngành | bảng full-width | `danh_gia_jobdetail` (khối Δ PV + ngành ưu tiên) hoặc `jobdetail_nhom_nganh` (workbook Data phân tích) | |
| 10 | 3. Blog (SEO / non-SEO) | bảng full-width | `danh_gia_blog_tab` hoặc `danh_gia_blog` + **`movers_pv_blog.json`** | Tách rõ subtotal SEO vs non-SEO. **Blog phải có CHẨN ĐOÁN RIÊNG** (không mượn chẩn đoán JL): drill movers PV Blog + ma trận tín hiệu; action nối với content strategy blog hàng tuần/tháng đang chạy trong SOW (nếu có task tương ứng — nêu đích danh) |
| 11 | 4. Homepage + NTD (ngoài cam kết) | bảng WoW 2 cột | dòng Homepage/NTD trong bang1 + `danh_gia_ntd` | Homepage PV lớn nhưng SEO không tác động — vẫn đưa vào theo lệ các tuần (feedback 22/07); ghi rõ "ngoài cam kết" |
| 12 | **Apply OVERVIEW theo page group** | bảng WoW 2 cột | **`apply_groups.json` (scripts/apply_groups.py — tải FULL tab «Data Apply thanks» rồi gộp theo Page Group)** | **ĐỨNG TRƯỚC slide Apply theo Intent** (feedback 22/07). KHÔNG cộng nhóm từ section `apply_thanks_pivot` trong digest — range config chỉ lấy ~80 dòng đầu nên thiếu (đã dính: 3,895 vs GT thật 12,417). Đối chiếu Grand Total với pivot Intent trên sheet |
| 13+ | Apply (Applythanks) theo Intent / khu vực / ngành | bảng WoW 2 cột (+full-width khi cần) | `danh_gia_apply` + `joblisting_intent_apply` + `apply_khuvuc` + `apply_nganh` | NHẬN XÉT bắt buộc trả lời "VÌ SAO tăng/giảm" per nhóm biến động lớn (rubric mục Apply) — nối với PV/clicks landing nhóm đó |
| 13 | SOW: **Plan Tuần** | SOW | `plan_tuan_truoc` (template mới) hoặc `sow_status.weeks[<tuần hiện hành>]` | Tiêu đề "SOW: Plan Tuần — <marker tuần>" (KHÔNG ghi Plan tháng); bảng show **ĐỦ task của tuần** kèm status, không chỉ dòng trễ; chips đếm theo tuần đó |
| 14 | Next week plan | SOW (bảng) | `plan_tuan_ke` hoặc `sow_status.weeks[<tuần kế>]` | Đủ task tuần kế; chưa có data → khung + đánh dấu Vincent/Lead điền |
| 15 | Hạng mục cần client hỗ trợ | support | `viec_phoi_hop` | Trống Description — điền trong họp |
| 16-19 | 3rd Party View monthly (tùy tuần có data) | 3rd party | tab 3rd-party khi xác định được / Ahrefs MCP (minh họa) | |
| 20 | Q&A | qna | — | |
| 21 | Thank You | thanks | — | |

## Luật trình bày deck (feedback 22/07 round 2)

1. **Đánh số slide**: mọi slide có `<div class="page-no">n/N</div>` (góc phải dưới).
2. **Breadcrumb**: slide nội dung có `<div class="crumb">Organic PV › Job Listing › 1.2 Ngành nghề</div>` ngay trên pill — người xem luôn biết đang ở nhánh nào.
3. **Nhận xét bảng nhóm — format chuẩn "3 tăng / 3 giảm"**: liệt kê top 3 nhóm tăng mạnh + top 3 nhóm giảm mạnh THEO THỨ TỰ, rồi **chẩn đoán chung cho CHIỀU TĂNG và CHIỀU GIẢM** (không chỉ chẩn đoán 1 nhóm lớn nhất); không cần đối chiếu % tổng của bảng scope top-page.
4. **Chẩn đoán per nhóm giảm ở BẢNG 1**: mỗi nhóm trang giảm (JD, Blog, NTD…) có 1 dòng chẩn đoán riêng theo ma trận — không mượn chẩn đoán của nhóm khác.
5. **Action phải cụ thể**: {làm gì × trên nhóm/URL nào × nối task SOW đang chạy (đích danh) × owner}. Cấm action mơ hồ kiểu "cơ hội title/meta" không kèm danh sách nhóm/URL.
6. **Text nhiều → TÁCH SLIDE, không nén font** (feedback Vincent 22/07): slide có bảng lớn + nhận xét/chẩn đoán dài thì tách thành 2 slide — slide bảng (+ 1-2 bullet tóm tắt, trỏ "chẩn đoán ở slide kế tiếp") và slide "Chẩn đoán & Action" chữ cỡ chuẩn. Đã áp cho BẢNG 1 (4→4+5), 1.2 ngành (7→7+8), Blog (12→12+13) ở deck W11 v3. Chữ không được nhỏ hơn ~21px; chữ tràn/đè `.data-meta` = FAIL tự kiểm — soi bằng render thử vài trang PDF ra PNG trước khi giao.
7. **Ngôn ngữ senior-SEO, không mật mã** (feedback Vincent 22/07 round 3): mọi NHẬN XÉT/CHẨN ĐOÁN/ACTION viết câu hoàn chỉnh, đọc phát hiểu ngay. CẤM ký hiệu nén kiểu "Imp↑ CTR↓", "-1.36đ", "check SERP + drift", "URL swap" trần trụi — ký hiệu/khái niệm nào dùng lần đầu phải nói bằng lời ("được Google hiển thị nhiều hơn nhưng tỷ lệ click giảm 1,36 điểm %"; "nhiều khả năng website đã redirect/đổi URL — traffic không mất mà chuyển nhà"). Action đủ 4 vế: **làm gì — trên nhóm/URL nào — vì sao — ai làm**. Độ chắc viết "(độ chắc: khá/trung bình/thấp)".
8. **Mọi mục phân tích có CẢ TĂNG lẫn GIẢM** (feedback Vincent 22/07 round 3): tăng để thấy kết quả + cơ hội khai thác tiếp, giảm để xử lý. Chiều nào rỗng thật thì ghi rõ ("Không có nhóm nào tăng kỳ này — giảm diện rộng 14/14 nhóm"), không im lặng bỏ chiều.
9. **Top pages = TOP 20 mỗi chiều** (thay vì 8), bảng đủ cột `PV · Δ PV · % · Clicks · Δ Clicks · Pos · Δ Pos` (Clicks/Pos 2 kỳ — pv_movers.py đã trả sẵn) + cột Intent/nhóm khi có. Nhiều URL → tách 2-3 slide thoải mái (slide nhiều hơn là chấp nhận được, chi tiết + action rõ quan trọng hơn ngắn).
10. **Blog chẩn đoán: 3 bài tiêu biểu mỗi nhóm chủ đề** (thay vì 1), lấy từ movers_pv_blog.json; cần thì tách 2 slide.
11. **Deck phải EDIT được tại chỗ**: bấm phím E bật/tắt chế độ sửa (contenteditable + lưu localStorage, key riêng theo deck) — port từ khối editor trong template `weekly-report-slides`. Bảng điền-tay (vd «Cần client hỗ trợ») cột Description rộng ≥65%, mỗi hàng cao ≥90px để gõ nhiều dòng.

## Luật render bảng

1. Mỗi giá trị lấy NGUYÊN VĂN từ digest (FORMATTED_VALUE của sheet). Không tự làm tròn lại.
2. Δ dương → `pos`, âm → `neg`, 0/rỗng → `mut`. Nhóm thuộc cụm KPI → `kpi-row`; dòng tổng → `total`.
3. Bảng dài hơn slide → cắt theo TOP |Δ| + dòng tổng + ghi "top N theo biến động — bảng đủ trong file data". NGOẠI LỆ: BẢNG 1 (slide 4) và bảng task Plan Tuần (slide 13) phải ĐỦ dòng.
4. Mọi slide data có `.data-meta` (nguồn + kỳ dữ liệu ĐÚNG theo header bảng nguồn) — thiếu là FAIL tự kiểm.
5. Ảnh (nếu dùng thang capture) nhúng base64; ảnh gốc ở `02-raw/screenshots/`.
6. `grep '{{'` deck final = 0.
