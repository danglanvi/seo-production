# Checklist data hằng tuần — Báo cáo tuần AI ({{CLIENT_NAME}})

> Người làm: SEO Lead / Executive phụ trách data. Deadline: **thứ Tư trước 17:00** (cron AI chạy thứ Năm 08:03 ra bản DRAFT).
> Nguyên tắc: AI đọc data bằng script theo TÊN TAB + HEADER cột. Giữ đúng format bên dưới thì AI chạy 1 phát ăn ngay (~20% token so với làm tay); đổi tên tab/header mà không báo = deck sai hoặc phải chạy lại.

## 0. Quy định folder & tên file trên Drive (agency nhiều dự án — robot tìm file theo 2 điều kiện này)

1. **Mỗi client 1 folder Drive cố định** cho báo cáo tuần, vd `{{CLIENT_NAME}} — SEO Weekly Report/`. Share folder này **1 LẦN** (quyền Viewer) cho email robot `{{SERVICE_ACCOUNT_EMAIL}}` → mọi workbook tạo TRONG folder tự kế thừa quyền, **không phải share từng file mỗi tuần nữa**.
2. Lấy **ID folder** (đoạn ký tự sau `folders/` trên URL folder) đưa cho AI kèm câu «cập nhật drive_folder_id» — AI ghi vào `report-config.yaml → report_tuan.drive_folder_id`. Từ đó robot CHỈ tìm trong folder này, không dính nhầm workbook trùng tên của dự án khác.
3. **Tên workbook tuần đúng cú pháp `name_pattern`** trong config (mặc định `Report Tuần {N}`, N = số tuần dự án) — không thêm tiền tố/hậu tố. Sai tên hoặc để ngoài folder → robot báo «không thấy» và deck ra bản SLIM.
4. **Các workbook cố định** (Kế hoạch tổng · Báo Cáo Kết Quả · Data phân tích) **GIỮ NGUYÊN URL** — chỉ cập nhật số bên trong, không tạo bản sao mới, không đổi tên.

## 1. Việc phải làm mỗi tuần (tick ✅ trước 17:00 thứ Tư)

| ☐ | Việc | Vì sao |
|---|---|---|
| ☐ | Tạo workbook **«Report Tuần {N}»** TRONG folder client (quy định mục 0) — đúng cú pháp tên. File tạo ngoài folder thì phải share Viewer thủ công cho `{{SERVICE_ACCOUNT_EMAIL}}` | Script tự tìm workbook theo tên trong đúng folder qua Drive search |
| ☐ | Refresh **CẢ HAI cột kỳ** (tuần này + tuần trước) ở mọi bảng trong tab «Đánh giá Joblisting» (Intent / ngành nghề / khu vực) | Đã dính thực tế: bảng ngành & khu vực còn giữ kỳ cũ 25/06–01/07 → Δ so lệch 1 kỳ, deck phải flag |
| ☐ | Tab **Data_Blog**: URL chuẩn hóa **chữ thường toàn bộ** | Đã dính thực tế: URL trùng hoa/thường bị đếm thành 2 dòng |
| ☐ | Website có **redirect / đổi URL** trong tuần → ghi cặp URL cũ→mới vào tab ghi chú (hoặc báo Account) | AI đang phải "nghi URL swap" (ví dụ W11 CareerViet) mà không có nguồn xác nhận |
| ☐ | Sheet «[Mới] Report tuần» (workbook Kế hoạch tổng): section **Tuần hiện hành đủ task + status**, và **đã tạo section tuần KẾ TIẾP** (dù mới có task khung) | Slide SOW + Next week plan đọc thẳng từ đây; thiếu section = slide trống |
| ☐ | Tab **«1. VIỆC CẦN PHỐI HỢP»** (workbook 5. Báo Cáo Kết Quả): thêm mục mới cần {{CLIENT_SHORT}} hỗ trợ (nếu có) | Đổ vào slide «Cần {{CLIENT_SHORT}} hỗ trợ»; không có mục mới thì thôi |
| ☐ | Dữ liệu cần dạng HÌNH — tool đòi đăng nhập (SpySERP…, robot không tự vào được): ưu tiên xuất **bảng số dạng ô** dán thành tab; chỉ có ảnh thì lưu PNG vào `02-raw/screenshots/manual/` tên `YYYYMMDD_<tool>_w{N}.png` (chắc ăn nhất) hoặc dán vào workbook «Report Tuần {N}» | Ảnh file AI nhúng thẳng vào slide; ảnh dán trong sheet có thể bị cắt khi robot chụp |
| — | **Looker Studio: KHÔNG tải ảnh tay** — giữ link ở chế độ «bất kỳ ai có đường liên kết – Viewer», AI tự vào chụp qua trình duyệt ẩn (link trong `report-config.yaml → looker.url`) | Robot chụp bản mới nhất mỗi lần chạy; share riêng cho email robot KHÔNG thay được chế độ link vì robot không đăng nhập giao diện web như người |

## 2. Luật format KHÔNG được phá (script phụ thuộc)

1. **Không đổi TÊN TAB**: «1. Overview Data WoW» · «2. PV Job Listing data» · «Đánh giá Joblisting» · «Đánh giá NTD» · «Đánh giá Blog» · «Data_Blog» · «Data Apply thanks» · «Run-rate tuần» · «[Mới] Report tuần» · «1. VIỆC CẦN PHỐI HỢP». Buộc phải đổi → báo trước để sửa `report-config.yaml`.
2. **Không đổi HEADER cột** các tab URL-level: script dò cột theo chữ «PV 7 ngày…», «Clicks 7 ngày…», «Imp…», «Pos…», «Đường dẫn/URL», «Intent», «Nhóm ngành/chủ đề», «Khu vực/Location», «SEO / non». Thêm cột mới cứ thêm về BÊN PHẢI.
3. **Không chèn dòng ghi chú / merge cell vào giữa vùng bảng** pivot — ghi chú để trên đầu tab hoặc tab riêng.
4. Bảng pivot giữ **Grand Total** ở đáy (script nhận diện tổng theo dòng này).
5. Số giữ format hiện tại (dấu phẩy nghìn, ▲▼ ok) — script đọc nguyên văn.

## 3. AI tự lo (team KHÔNG cần làm)

- Kéo data 4 workbook (1 API call/workbook), lọc top movers theo ΔPV chuẩn team, gộp Apply theo Page Group, tính Pos dẫn xuất cho nhóm Blog, viết nhận xét/action theo rubric, dựng deck HTML (render bằng script từ file nội dung YAML), tự chụp từng slide soi lỗi trình bày (output CHỈ HTML — không xuất PDF, luật 23/07/2026).
- Cron thứ Năm 08:03 ra bản **DRAFT** để Vincent/Lead review — AI không tự gửi đi đâu.

## 4. Khi nào phải báo AI chạy lại

- Sửa số liệu trên sheet SAU 08:03 thứ Năm → nhắn «chạy lại báo cáo tuần N» (script re-fetch ghi đè folder tuần đó).
- Muốn tuần khác: «làm báo cáo tuần N».

## 5. KÍCH HOẠT HỆ — làm MỘT LẦN trước tuần báo cáo đầu tiên

> Instance mới chưa có workbook thì hệ chưa chạy được. Bảng này là việc setup 1 lần; xong thì xóa banner "chưa kích hoạt" ở đầu file.

| ☐ | Việc | Ai | Ghi kết quả vào |
|---|---|---|---|
| ☐ | Thiết kế + duyệt format tab/cột workbook với team data (họp 30') — viết ra `09-reporting/<CLIENT>_workbook-schema_v1.md`, chốt thì khóa tên tab | SEO Lead + team data | File schema, `status: stable` |
| ☐ | Dựng bộ workbook cố định của dự án (kế hoạch tổng · báo cáo kết quả · data phân tích) theo schema | Team data | Dán ID vào `spreadsheets.*.id` trong `report-config.yaml` |
| ☐ | Tạo folder Drive cố định cho báo cáo tuần + share Viewer 1 lần cho service account | SEO Lead | `report_tuan.drive_folder_id` |
| ☐ | Dựng template «Report Tuần {N}» tuần đầu đủ tab → chốt tên tab nguyên văn | Team data | Sửa `report_tuan.ranges` khớp nguyên văn |
| ☐ | Điền tên tab URL-level vào `pv_movers` | SEO Lead | `report-config.yaml` |
| ☐ | Xin khách cấp quyền **GA4 + GSC** (Viewer) cho service account | Account | `ga4_property_id` + `gsc_site` |
| ☐ | Chốt **scope KPI** (danh sách URL/pattern thuộc KPI cam kết) với khách — mốc setup baseline | SEO Lead + khách | Tab scope trong workbook + `page_groups` |
| ☐ | Verify: `fetch_weekly_data.py --dry-run` → fetch thật 1 tuần có ground truth → so số tay → `build_source_links.py --check` → sinh `data-sources.yaml` | AI + SEO Lead | `RUNBOOK-bao-cao-ky.md` §0 |
| ☐ | Báo AI ghi `log.md` op `setup` «kích hoạt hệ báo cáo tuần» | SEO Lead | `log.md` |
