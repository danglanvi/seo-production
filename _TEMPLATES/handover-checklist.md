---
client: "{{CLIENT}}"
cong_doan: 33
ws: 11-handover-maintenance
so_hd: "{{số HĐ}}"
ngay_ban_giao: "{{YYYY-MM-DD}}"
pic: "{{ACCOUNT}} + {{SEO_LEAD}}"
nguoi_nhan_khach: "{{tên + chức danh}}"
status: draft
version: v1
---

# {{CLIENT}} — Checklist bàn giao & chuyển giao Duy trì

> Naming: `{{CLIENT}}_handover-checklist_v{{N}}.md` → `11-handover-maintenance/`. Checklist QC: `02-raw/knowledge/sop/09-timeline/khung-duy-tri.md`. Chạy tháng cuối thúc đẩy → tháng 1 duy trì; kết quả bàn giao dẫn vào BBNT thanh lý mục 3.4 (`_TEMPLATES/account/`).

## 1. Tài sản bàn giao

| # | Hạng mục | Chi tiết | ☐ | Link/nơi lưu |
|---|---|---|---|---|
| 1 | Admin CMS / domain / hosting | Đổi TOÀN BỘ quyền admin về khách; GTV rút về quyền cần thiết theo phạm vi tái ký | ☐ | {{...}} |
| 2 | Tool đã mua | Danh sách tool + license + thời hạn + tài khoản | ☐ | {{...}} |
| 3 | Danh sách backlink đã triển khai | Full list URL + anchor + ngày + trạng thái | ☐ | {{...}} |
| 4 | File content + topical map | Kho bài + topical map + content plan matrix | ☐ | {{...}} |
| 5 | GEO prompt set + baseline AI visibility | Từ báo cáo kép T10 (`08-geo-ai-visibility/` + `09-reporting/`) | ☐ | {{...}} |
| 6 | Danh sách Quality Nodes | Top 20% pages theo traffic/revenue/strategic/hub | ☐ | {{...}} |
| 7 | Hướng dẫn vận hành | Tài liệu vận hành + quyền truy cập GA4/GSC | ☐ | {{...}} |

## 2. Baseline chuyển giao

| Chỉ số | Giá trị tại bàn giao | Nguồn đo | Ngày tracking |
|---|---|---|---|
| Traffic / Ranking / Chuyển đổi | {{...}} | {{GA4 / SpySERP — theo HĐ}} | {{dd/mm/yyyy}} |

## 3. Khung duy trì — 2 track chạy song song

| Track | Bản chất | Phạm vi |
|---|---|---|
| **Dòng A — Duy trì KPI cũ** (luôn có) | 10 việc theo thứ tự ưu tiên trong `khung-duy-tri.md` mục 5, phân bổ 6 tháng đầu; nguyên tắc dứt điểm 60-70% trong khung | {{...}} |
| **Dòng B — Thúc đẩy KPI mới** (nếu tái ký A+B) | Bộ từ khóa mới / traffic cao hơn = dự án thúc đẩy MỚI, chạy lại 33 công đoạn với bước mở màn audit kế thừa (kế thừa · điều chỉnh · tạo mới); thường gói 6-8 tháng | {{...}} |

Luật nguồn lực: dòng B KHÔNG rút người khỏi nhịp tối thiểu dòng A (momentum content + technical + GSC follow) — mất momentum là mất cái đang giữ.

## 4. Lịch duy trì quý (chốt với khách)

| Nhịp | Trọng tâm | PIC |
|---|---|---|
| Weekly | CWV, crawl budget, content momentum, trending scan | {{...}} |
| Monthly | Full report, content audit review, quality nodes, technical fixes | {{...}} |
| Quarterly | Deep technical audit, link ROI, competitor momentum, đo AI visibility | {{...}} |
| Sau mỗi Core Update | Audit so thị trường → điều chỉnh topical map | {{...}} |

## 5. Điều kiện tái ký

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | Phạm vi: chỉ dòng A hay A + B? | {{A \| A+B}} |
| 2 | KPI mới thuộc dạng nào: top cao hơn / traffic hơn / bộ từ khóa mới (kèm thành tựu thúc đẩy làm mốc) | {{...}} |
| 3 | Vai trò PM + ước workload 1-3 tháng (cộng thêm nếu có dòng B) | {{...}} |
| 4 | Timeline dòng B hoạch định lại từ đầu (6-8 tháng, mở rộng chủ đề lớn thì dài hơn) | {{...}} |

**Trigger tái ký (không đợi đến handover):** HĐ còn **≤2 tháng** → SEO Lead gửi input "tiềm năng giai đoạn tiếp" (mục 5 renewal brief) cho Account; Account chạy `acc-renewal-brief` (Account Production) và bàn giao BD mở deal type renewal. Kết quả vs cam kết trong brief phải **khớp tuyệt đối** báo cáo đã gửi khách — không đo mới. Hai tín hiệu tái ký tốt nhất: sau BBNT đợt có kết quả đẹp nhất (không phải khi HĐ sắp hết) · khách hỏi về AI/GEO, thị trường mới, "traffic có mà không ra đơn" (→ CRO).

**Bàn giao PIC nội bộ (khi đổi SEO Lead giữa dự án — ghi ở đây, không có template riêng):** Lead cũ để lại 5 thứ: (1) trạng thái bảng B + việc đang `blocked` và vì sao; (2) 3 quyết định gate gần nhất + lý do; (3) hạng mục khách đang giữ + số ngày; (4) `12-feedback-lessons/feedback-log.md` entry chưa distill; (5) người liên hệ thật phía khách (ai quyết, ai chỉ chuyển tin). Lead mới xác nhận đọc xong → append `log.md` op `handover` (nguồn: internal).

## 5b. Thu feedback khách (bắt buộc trước ký nhận)

Gửi 2 câu qua email/Zalo sau buổi bàn giao (mẫu `email-khao-sat-hai-long` bên Account Production): điểm 0-10 "anh/chị có giới thiệu GTV cho người khác không" + "điều gì hài lòng nhất / muốn GTV làm khác". Ghi điểm + ngày đo vào bảng dưới; điểm ≤6 → mở entry `12-feedback-lessons/feedback-log.md` (nguồn: client) trong 3 ngày.

| Điểm (0-10) | Ngày đo | Ý hài lòng nhất | Ý muốn khác | Entry feedback-log |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{FB-... hoặc —}} |

## 6. Ký nhận

| Bên | Người ký | Ngày | Chữ ký |
|---|---|---|---|
| GTV | {{...}} | {{...}} | |
| Khách | {{...}} | {{...}} | |

## Done-criteria

- [ ] Mọi ô ☐ mục 1 → ☑ hoặc `n/a` kèm lý do; hạng mục ☑ có link mở được bằng quyền của khách.
- [ ] Baseline chuyển giao đo xong, đúng nguồn đo HĐ, có ngày tracking.
- [ ] Danh mục bàn giao dẫn vào BBNT thanh lý mục 3.4; bảo hành {{90%}}/{{30}} ngày ghi đúng điều khoản.
- [ ] Lịch duy trì quý + điều kiện tái ký chốt với khách bằng văn bản/email.
- [ ] Checklist ký nhận 2 bên; update `index.md` #33 (QC PASS trước khi done) + append `log.md` op `handover`.
