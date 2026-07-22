# Checklist data hằng tuần — Báo cáo tuần AI ({{CLIENT_NAME}})

> Người làm: SEO Lead / Executive phụ trách data. Deadline: **thứ Tư trước 17:00** (cron AI chạy thứ Năm 08:03 ra bản DRAFT).
> Nguyên tắc: AI đọc data bằng script theo TÊN TAB + HEADER cột. Giữ đúng format bên dưới thì AI chạy 1 phát ăn ngay (~20% token so với làm tay); đổi tên tab/header mà không báo = deck sai hoặc phải chạy lại.

## 1. Việc phải làm mỗi tuần (tick ✅ trước 17:00 thứ Tư)

| ☐ | Việc | Vì sao |
|---|---|---|
| ☐ | Tạo workbook **«Report Tuần {N}»** (đúng format tên, N = tuần dự án) và **share Viewer** cho `{{SERVICE_ACCOUNT_EMAIL}}` | Script tự tìm workbook theo tên qua Drive search |
| ☐ | Refresh **CẢ HAI cột kỳ** (tuần này + tuần trước) ở mọi bảng trong tab «Đánh giá Joblisting» (Intent / ngành nghề / khu vực) | Đã dính thực tế: bảng ngành & khu vực còn giữ kỳ cũ 25/06–01/07 → Δ so lệch 1 kỳ, deck phải flag |
| ☐ | Tab **Data_Blog**: URL chuẩn hóa **chữ thường toàn bộ** | Đã dính thực tế: URL trùng hoa/thường bị đếm thành 2 dòng |
| ☐ | Website có **redirect / đổi URL** trong tuần → ghi cặp URL cũ→mới vào tab ghi chú (hoặc báo Account) | AI đang phải "nghi URL swap" (ví dụ W11 CareerViet) mà không có nguồn xác nhận |
| ☐ | Sheet «[Mới] Report tuần» (workbook Kế hoạch tổng): section **Tuần hiện hành đủ task + status**, và **đã tạo section tuần KẾ TIẾP** (dù mới có task khung) | Slide SOW + Next week plan đọc thẳng từ đây; thiếu section = slide trống |
| ☐ | Tab **«1. VIỆC CẦN PHỐI HỢP»** (workbook 5. Báo Cáo Kết Quả): thêm mục mới cần {{CLIENT_SHORT}} hỗ trợ (nếu có) | Đổ vào slide «Cần {{CLIENT_SHORT}} hỗ trợ»; không có mục mới thì thôi |
| ☐ | Dữ liệu cần dạng HÌNH (SpySERP ranking distribution…): xuất được **bảng số dạng ô** thì dán thành tab/bảng | AI không đọc được ảnh dán trong sheet — chỉ có ảnh thì slide đó để khung điền tay |

## 2. Luật format KHÔNG được phá (script phụ thuộc)

1. **Không đổi TÊN TAB**: «1. Overview Data WoW» · «2. PV Job Listing data» · «Đánh giá Joblisting» · «Đánh giá NTD» · «Đánh giá Blog» · «Data_Blog» · «Data Apply thanks» · «Run-rate tuần» · «[Mới] Report tuần» · «1. VIỆC CẦN PHỐI HỢP». Buộc phải đổi → báo trước để sửa `report-config.yaml`.
2. **Không đổi HEADER cột** các tab URL-level: script dò cột theo chữ «PV 7 ngày…», «Clicks 7 ngày…», «Imp…», «Pos…», «Đường dẫn/URL», «Intent», «Nhóm ngành/chủ đề», «Khu vực/Location», «SEO / non». Thêm cột mới cứ thêm về BÊN PHẢI.
3. **Không chèn dòng ghi chú / merge cell vào giữa vùng bảng** pivot — ghi chú để trên đầu tab hoặc tab riêng.
4. Bảng pivot giữ **Grand Total** ở đáy (script nhận diện tổng theo dòng này).
5. Số giữ format hiện tại (dấu phẩy nghìn, ▲▼ ok) — script đọc nguyên văn.

## 3. AI tự lo (team KHÔNG cần làm)

- Kéo data 4 workbook (1 API call/workbook), lọc top movers theo ΔPV chuẩn team, gộp Apply theo Page Group, tính Pos dẫn xuất cho nhóm Blog, viết nhận xét/action theo rubric, dựng deck (render bằng script từ file nội dung YAML), export PDF, tự soi từng trang chống lỗi trình bày.
- Cron thứ Năm 08:03 ra bản **DRAFT** để Vincent/Lead review — AI không tự gửi đi đâu.

## 4. Khi nào phải báo AI chạy lại

- Sửa số liệu trên sheet SAU 08:03 thứ Năm → nhắn «chạy lại báo cáo tuần N» (script re-fetch ghi đè folder tuần đó).
- Muốn tuần khác: «làm báo cáo tuần N».
