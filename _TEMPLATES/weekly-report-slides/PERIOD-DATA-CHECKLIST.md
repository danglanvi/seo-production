# Checklist data kỳ THÁNG / QUÝ — báo cáo AI ({{CLIENT}})

> Song sinh với `WEEKLY-DATA-CHECKLIST.md` (nhịp tuần). File này áp cho **báo cáo tháng** (ngày 2–4 tháng kế) và **báo cáo quý** (tháng khép quý — deck kép tháng + quý).
> 📋 **Template client-neutral** — copy vào `09-reporting/PERIOD-DATA-CHECKLIST.md` của instance, thay `{{CLIENT}}` + mốc quý + tên nhóm trang theo `page_groups` của dự án.
> Người làm: SEO Lead / Executive phụ trách data phía GTV + đầu mối data phía khách (dự án ADVISORY — data vận hành phần lớn do team in-house khách cập nhật).
> Nguyên tắc như nhịp tuần: AI đọc bằng script theo **TÊN TAB + HEADER cột** (chuẩn: file schema workbook của instance, vd `<CLIENT>_workbook-schema_v1.md`). Giữ đúng format thì chạy một phát ăn ngay; đổi tên mà không báo = deck sai hoặc phải chạy lại.

---

## 0. Deadline

| Kỳ | Data phải xong | AI dựng deck |
|---|---|---|
| THÁNG | hết ngày **2** tháng kế | ngày 2–4 |
| QUÝ (tháng khép quý) | hết ngày **2** tháng kế | ngày 2–5 — deck kép, cần thêm 1 ngày cho lớp so cùng kỳ |

Quý dự án ≠ quý dương lịch — tính theo T1 của hợp đồng (tra bảng A `index.md`). Vd T1 = 06/2026 → Quý 1 khép 31/08/2026.

## 1. Việc phải làm mỗi kỳ

| ☐ | Việc | Vì sao |
|---|---|---|
| ☐ | Tạo workbook kỳ: **«Report Monthly (Tháng MM.YYYY)»** / **«Report Quý N (dd/mm - dd/mm/yyyy)»**, share Viewer cho service account (hoặc tạo trong folder Drive client đã share) | Script kéo theo ID/khối `periods:` khai trong `report-config.yaml` — báo ID mới ngay khi tạo |
| ☐ | **BẢNG 1 «Overview»** đủ hai cột giá trị gốc của cả hai kỳ so sánh (không chỉ cột Δ và %) | Script tự tính lại Δ/% từ hai cột gốc để kiểm ô công thức — thiếu cột gốc thì không kiểm được |
| ☐ | Tab URL-level từng nhóm trang (theo `page_groups` của dự án — vd Category · PDP · Blog với e-commerce; Job Listing · Job Detail · Blog với job site) — **giữ nguyên thứ tự cột giữa các kỳ** | Cột `cur`/`prev` khai tường minh trong config; đổi thứ tự mà không báo → danh sách tăng/giảm **đảo ngược hoàn toàn** (bài học CareerViet Q1) |
| ☐ | Kỳ QUÝ: tab nhóm trang chính so cùng kỳ tách hai năm (`_<năm trước>` / `_<năm nay>`) giữ **cùng cột URL** để join | Không có cột Δ sẵn, phải join theo URL. URL đổi slug giữa hai năm → dùng tab ghi chú URL để map |
| ☐ | **Đối chiếu định nghĩa event/metric giữa hai năm** cho mọi chỉ số YoY (GA4 đổi tên event, đổi cách đếm pageview…) — đổi thì ghi chú ngay trên tab | Bài học CareerViet Q1: 2025 dùng `ApplyThanks_Pmax`, 2026 dùng `Applythanks` — so cùng tên biến ra −58,4% thay vì −10,95% thật |
| ☐ | Dòng «cùng kỳ / YoY» trên sheet Run-rate **căn đúng tháng dương lịch** | CareerViet từng lệch (T5/26 ↔ T1/25) — deck phải căn lại tay và báo đỏ |
| ☐ | Tab **«4.1 REPORT TUẦN»**: đủ các section tuần trong kỳ + plan tháng kế | Nguồn slide việc đã làm + plan kỳ kế |
| ☐ | Sheet **OKRs Quý** kỳ vừa khép: cập nhật status từng KR (Done / Đang làm / Trễ hạn) | Nguồn slide chấm điểm + carry-over. Ô status trống → deck ghi «Chưa cập nhật», không tự đoán |
| ☐ | Sheet **OKRs Quý kế**: bản nháp đủ O/KR + PIC + deadline | Nguồn slide OKRs kỳ kế |
| ☐ | Tab **scope KPI** (danh sách URL/pattern thuộc KPI cam kết): rà lại trong kỳ, thêm dòng mới kèm ngày, không xóa dòng cũ | Số KPI của kỳ đọc theo scope này (`scope_ref`); scope trôi mà không ghi ngày = số kỳ trước không tái lập được |
| ☐ | Sheet **hạng mục technical / action plan**: khách cập nhật cột Status/Dev Confirm mọi hạng mục | Nguồn slide tiến độ technical — quy công chỉ cho hạng mục đã thực sự live |
| ☐ | Ảnh bằng chứng (GSC Crawl Stats · Performance · GA4…) lưu `02-raw/screenshots/tools/` tên `YYYYMMDD_<slug>.png` | Deck nhúng base64; ảnh gốc phải sống ở 02-raw (protocol §8) |
| ☐ | Nguồn mới phát sinh trong kỳ (file rời, workbook mới) → **báo để khai vào `source_links:`** | Slide phụ lục nguồn phải mở được mọi nguồn; nguồn không khai nằm ở khối «chưa có link» |

## 2. Luật format KHÔNG được phá

1. **Không đổi TÊN TAB** giữa các kỳ. Buộc phải đổi → báo trước để sửa `report-config.yaml`. (Tên tab có space thừa/dấu chấm cuối cứ giữ nguyên — script hiểu, miễn khai đúng nguyên văn.)
2. **Không đổi thứ tự / tên HEADER cột** ở tab URL-level. Thêm cột mới thì thêm về **bên phải**.
3. **Không chèn dòng ghi chú / merge cell vào giữa vùng bảng** pivot.
4. Bảng pivot giữ **Grand Total** ở đáy.
5. Không tạo bản sao workbook kỳ cũ dùng cho kỳ mới **rồi giữ nguyên tên tab** — gid đổi, nội dung đổi, nhưng script vẫn trỏ đúng tên: dễ ra số kỳ cũ mà không ai biết. Tạo mới thì báo ID.

## 3. AI tự lo (team KHÔNG cần làm)

- Kéo data kỳ (1 API call/workbook), phân tích URL-level + độ phủ so BẢNG 1, forensics nhóm giảm sâu (URL biến mất/đổi slug/sụt sâu), chấm điểm OKRs, tự kiểm công thức BẢNG 1, đối chiếu tổng giữa các nguồn, viết insights theo rubric, dựng deck HTML + PowerPoint, tự đo chống tràn từng slide, sinh registry link nguồn.
- Output là **HTML** (+ PPTX khi client cần bản sửa được). Không tự export PDF.

## 4. Các hạng mục đang chặn chất lượng — cần xử trước kỳ báo cáo đầu tiên

> Bảng dưới là **khung mẫu** — mỗi instance liệt kê hạng mục đang chặn của chính dự án đó, xóa dòng không áp dụng.

| Hạng mục | Ảnh hưởng nếu tiếp tục thiếu |
|---|---|
| **Bộ workbook báo cáo chưa dựng** (workbook cố định + nhịp Report Tuần) | Chưa chạy được kỳ nào — làm `WEEKLY-DATA-CHECKLIST.md` §5 |
| **Quyền GA4 + Search Console** cho service account | Số pageview/hiệu suất phải đọc qua sheet/ảnh chụp; không đối chiếu được số gốc khi lệch; slide nguồn phải ghi «chưa có link» |
| **Scope KPI chưa chốt với khách** (danh sách URL/pattern thuộc KPI cam kết) | Số KPI render ra không có căn cứ đối chiếu → rủi ro tranh chấp nghiệm thu (xem `../00-client-context/kpi-commitments.md` §2) |
| **Số cam kết trong HĐ chưa thống nhất giữa các phụ lục** (nếu dự án gặp) | `kpi_targets` chưa khai được; Lead phải chốt MỘT con số bằng văn bản (ghi quyết định + ngày vào `kpi-commitments.md`) trước kỳ báo cáo đầu — không để hai giá trị song song trong báo cáo |
