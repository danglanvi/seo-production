# Chuẩn tên gọi SOW & KPI — Rules report đồng nhất từ PSP → Account → Khách hàng

> **Vấn đề giải quyết:** báo cáo tháng/quý, BBNT và dashboard phải khớp **nguyên văn** Scope of Work + KPI cam kết trong hợp đồng; team SEO (PSP) report cho Account phải dùng đúng cùng một bộ tên — không mỗi người một kiểu gọi, đến kỳ nghiệm thu Account phải "dịch" lại.
> **Phiên bản:** v1 — 07/2026. Fact-check dựa trên: HĐ CareerViet (PL01/PL02/Tài liệu đính kèm 1), HĐ Minh Tuấn Mobile 2026, BBNT PVI đợt 3, BBNT Sơn Báu, BBNT thanh lý Surface.

---

## 1. Nguyên tắc gốc — "Contract Vocabulary"

**Tên hạng mục trong mọi artifact = chép NGUYÊN VĂN từ Phụ lục hợp đồng (PL01 / Bảng khối lượng công việc).**

Chuỗi khớp tên bắt buộc:

```
PL01 hợp đồng ──► SOW MAPPING (lập 1 lần khi ký HĐ)
                        │
     ┌──────────────────┼──────────────────────┐
     ▼                  ▼                      ▼
PSP report tháng   Email báo cáo khách    Dashboard/Looker
(sheet PSP REPORT)  + BBNT + hóa đơn      (tên tile/bảng)
```

- **SOW MAPPING** (sheet mới trong file `GTV_Quan-ly-du-an_Template_v1.xlsx`) là **từ điển duy nhất** của dự án: Account lập trong tuần đầu sau ký, PSP và mọi report chỉ được dùng tên trong cột "Tên nguyên văn theo HĐ".
- Tên nội bộ/tên tool (vd "Apply Thanks", "traffic user", "cloudstack") **cấm xuất hiện** trong deliverable gửi khách — nếu cần chú thích kỹ thuật thì để trong ngoặc sau tên hợp đồng.
- Mỗi chỉ số phải kèm **nguồn đo + cách đo đúng Tài liệu kỹ thuật của HĐ** (GA4 filter nào, SpySERP check ở google.com hay google.com.vn, Ahrefs chỉ số nào). Sai nguồn đo = số không có giá trị nghiệm thu.

**Phép thử trước khi gửi bất kỳ report nào:** đặt bảng KPI của report cạnh bảng PL01 — nếu có dòng không tìm thấy tên tương ứng nguyên văn trong PL01, dòng đó sai chuẩn.

---

## 2. Kết quả fact-check bộ template & dashboard (07/2026)

| # | Kiểm tra | Kết quả | Hành động |
|---|---|---|---|
| 1 | Cấu trúc bảng KPI 6 cột (Loại KPI · Hạng mục · Cam kết · Kết quả · Tỷ lệ thực tế · Tỷ lệ để nghiệm thu) so với BBNT thực tế PVI/Sơn Báu/Surface | ✅ Khớp | Giữ — đây là format chuẩn xuyên suốt |
| 2 | Ngưỡng nghiệm thu 75% bình quân, **cap 100%/hạng mục, không bù chéo** (MTM K4.2; CRV PL01 5.2) | ✅ Đã có trong email/BBNT/dashboard/xlsx | Giữ |
| 3 | Hồ sơ thanh toán 4 giấy tờ + thời hạn 10/15/5 ngày LV là biến theo HĐ | ✅ Đúng | Giữ |
| 4 | **CRV — scope Pageview:** HĐ ghi "Organic Pageview cụm **Việc làm + Tool**"; dashboard Looker đang hiển thị "Việc làm + Tool **+ 332 URL Blog CV/Lương**" | ⚠️ Lệch scope so nguyên văn HĐ | Vincent xác nhận: nếu 332 Blog đã được thống nhất bằng phụ lục/email thì **ghi căn cứ ngay trên dashboard & báo cáo** ("theo Phụ lục …/email ngày …"); nếu chưa có văn bản → rủi ro khi đối chiếu GA4 lúc nghiệm thu, cần chốt lại với khách bằng email |
| 5 | **CRV — tên chỉ số chuyển đổi:** Looker đặt "Apply Thanks view"; HĐ gọi "**Số lượt sự kiện ứng tuyển thành công**" (đo bằng pageview URL chứa `applythanks`, bộ lọc source/medium theo Tài liệu đính kèm 1) | ⚠️ Tên tool ≠ tên HĐ | Mọi report/BBNT dùng tên HĐ, chú thích kỹ thuật trong ngoặc. Dashboard demo đã dùng đúng; **Looker hiện tại nên đổi title** |
| 6 | **SpySERP market:** PVI/Sơn Báu check google.com**.vn**; MTM check google.com (thị trường VN). Email mẫu cũ ghi cứng "google.com.vn" | ⚠️ Đã sửa | Template v1 chuyển thành biến `[google.com / google.com.vn — theo HĐ]` |
| 7 | **MTM — quy tắc TOP lồng nhau** (TOP 5 ⊂ TOP 10, 1 từ khóa đếm ở cả 2 mức, nghiệm thu độc lập từng mức) | ⚠️ Chưa ghi trong report ranking | Đã thêm vào rules mục 4 — PSP phải đếm theo quy tắc này, ghi chú dưới bảng ranking |
| 8 | PVI — đơn vị "Organic Session (chỉ số tải về GA4)" | ✅ Dashboard demo ghi đúng | Giữ |
| 9 | SLA xác nhận 04 vs 07 ngày (đã phát hiện đợt trước) | ✅ Đã chuẩn hóa thành biến | Rà email các dự án đang chạy |
| 10 | KPI CRV có **trọng số** (Pageview 60% · Ứng tuyển 40%) | ⚠️ Bảng KPI chưa có cột trọng số cho HĐ dạng này | Đã bổ sung cột "Trọng số" trong SOW MAPPING; công thức Kết quả KPI kỳ = bình quân **có trọng số** khi HĐ quy định |

---

## 3. SOW MAPPING — mẫu bảng (lập 1 lần/hợp đồng)

| STT | Tên NGUYÊN VĂN theo HĐ (PL01) | Loại | Nguồn đo | Cách đo (dẫn điều khoản) | Đơn vị | Cam kết | Trọng số | Tên nội bộ (CẤM dùng trong deliverable) |
|---|---|---|---|---|---|---|---|---|
| 1 | Organic Pageview cụm Việc làm + Tool | KPI cam kết | GA4 | TL đính kèm 1 — filter hostname careerviet.vn, Organic Search, phân loại nhóm trang | Pageview | +85.007.480 (12 tháng) | 60% | "PV job+tool" |
| 2 | Số lượt sự kiện ứng tuyển thành công | KPI cam kết | GA4 | Pageview URL chứa `applythanks`, source/medium regex theo TL đính kèm 1 | Lượt | +1.105.738 | 40% | "Apply Thanks" |
| 3 | Audit & Edit nội dung Core section | Công việc SOW | Sheet worklog | Đếm số bài hoàn thành có link bằng chứng | Bài | theo Bảng khối lượng | — | "audit content" |
| … | *(chép tiếp từng dòng PL01)* | | | | | | | |

Ví dụ PVI: "Bộ từ khóa Brand — TOP 3/5 (SpySERP, google.com.vn)", "Organic Session (chỉ số tải về GA4)". Ví dụ MTM: "Bộ từ khóa cam kết 1.377 từ khóa — TOP 5/TOP 10 (SpySERP, google.com, quy tắc tập lồng nhau)", "Organic Cate & Product Pageview thuộc thương hiệu Apple (GA4)", "Citation AIO (Ahrefs)".

---

## 4. Rules — PSP report hằng tháng cho Account

**Deadline & nơi nộp:** ngày **28–29 hằng tháng** (nhịp 2 đợt thì thêm ngày 13–14), điền trực tiếp vào sheet **PSP REPORT** của file quản lý dự án (không gửi file rời, không nhắn số qua chat).

**5 rules cứng:**

1. **Đúng tên:** cột "Hạng mục" chỉ được chọn từ dropdown SOW MAPPING — không gõ tay tên mới. Việc phát sinh ngoài SOW → ghi ở khu "Ngoài SOW" riêng, không trộn vào bảng nghiệm thu.
2. **Đúng nguồn đo:** số KPI lấy đúng nguồn + filter trong SOW MAPPING (GA4 view nào, SpySERP market nào, ngày tracking nào). Ghi rõ **kỳ dữ liệu từ ngày–đến ngày** và **ngày tracking** cho ranking. TOP đếm theo quy tắc HĐ (vd MTM: TOP 5 ⊂ TOP 10 — 1 từ khóa đạt TOP 5 được đếm ở cả 2 mức).
3. **Đúng trạng thái:** chỉ 3 giá trị cho công việc — Hoàn thành / Đang triển khai / Chưa bắt đầu (+lý do nếu trễ). "Hoàn thành" bắt buộc có **link bằng chứng** mở được bằng quyền của khách.
4. **Đúng phân loại public:** đánh dấu Public/Nội bộ từng dòng — task nội bộ (cloudstack, GSA, traffic user…) không bao giờ để Public.
5. **Đúng hạn + tự chấm:** PSP tự điền "% hoàn thành để nghiệm thu" (cap 100%) trước; Account chỉ **đối chiếu**, không tự tính lại từ đầu. Trễ deadline nộp report = escalate SEO Lead ngay hôm sau.

**Checklist PSP trước khi bàn giao số cho Account (in trong sheet PSP REPORT):**
- [ ] Mọi dòng dùng tên từ dropdown SOW MAPPING
- [ ] Kỳ dữ liệu + ngày tracking ghi rõ
- [ ] Số khớp nguồn đo của HĐ (không lấy tool khác "cho nhanh")
- [ ] Dòng Hoàn thành có link bằng chứng
- [ ] Public/Nội bộ đã đánh dấu đủ
- [ ] Vấn đề tồn đọng + việc cần khách làm đã ghi (nếu có)

**Account nhận report làm gì (30 phút, ngày 29–30):** đối chiếu bảng PSP vs PL01 (đủ dòng SOW chưa?) → soát cap 100%/không bù chéo/trọng số → copy dòng Public sang email báo cáo khách → số lệch với dashboard >2% thì dừng lại truy nguồn trước khi gửi.

---

## 5. Báo cáo QUÝ (khác gì báo cáo tháng)

Theo nhịp SOP (T3 · T6 · T9): báo cáo quý = báo cáo tháng cuối quý **+ 3 khối bổ sung**, cũng phải theo tên SOW:

1. **Lũy kế quý vs timeline PL01** — bảng runrate 3 tháng (KPI kế hoạch/thực tế/% lũy kế) đúng tên từng hạng mục.
2. **OKRs quý sau** — mục tiêu viết theo hạng mục SOW (không viết mục tiêu bằng tên nội bộ).
3. **Kết quả audit định kỳ + action** — audit Q2 (T4), FULL audit (T7): action chia "GTV làm / Khách làm" kèm deadline.

Riêng **T6**: báo cáo quý 2 = tài liệu buổi review giữa kỳ trực tiếp với khách (kết quả T1–T6 + kế hoạch T7–T10 + budget offpage nếu gate mở).

---

## 6. Các file đã điều chỉnh theo chuẩn này (07/2026)

- `GTV_Quan-ly-du-an_Template_v1.xlsx` — **thêm sheet "1B. SOW MAPPING"** (từ điển hợp đồng) + **sheet "7. PSP REPORT"** (form PSP nộp hằng tháng, dropdown ăn theo SOW MAPPING) + cột "Hạng mục SOW" trong sheet CONG VIEC.
- `account-report_Email-Templates_v1.md` — thêm rule tên nguyên văn PL01; bỏ ghi cứng google.com.vn.
- `account-report_BBNT-Templates_v1.md` — checklist thêm mục khớp tên SOW MAPPING.
- `account-report_Dashboard-Demo_v1.html` — chip KPI CRV đổi theo tên hợp đồng ("Ứng tuyển thành công").
- Việc còn lại phía Vincent/team: đổi title "Apply Thanks view" trên Looker CRV + xác nhận căn cứ scope "332 URL Blog" (mục 2, dòng 4–5).
