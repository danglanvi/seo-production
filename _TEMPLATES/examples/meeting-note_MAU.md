> ⚠️ MẪU MINH HỌA — client hư cấu "Công ty Ví Dụ / vidu.vn", số liệu giả định để agent noi theo CẤU TRÚC + ĐỘ SÂU + GIỌNG.
> Không copy số vào deliverable thật. Mẫu thật của dự án tích lũy trong instance qua vòng feedback → lesson → promote.

---
client: "Công ty Ví Dụ"
loai: định kỳ tháng (review báo cáo T5)
ngay: 2026-08-05
tham_du: Bình (Account — GTV), An (SEO Lead Project — GTV) / chị Hoa (TP Marketing), anh Tú (dev) — Công ty Ví Dụ
nguoi_ghi: "@binh"
cong_doan: 30 (nhịp báo cáo tháng)
ws: 10-client-management
version: v1
---

# Công ty Ví Dụ — Meeting note 2026-08-05 — Review báo cáo T5 + đề xuất mở rộng cụm chủ đề

> Naming thật khi dùng: `VIDU_meeting-note-20260805_v1.md` → `10-client-management/`. Ghi trong vòng 24h sau họp, gửi tóm tắt cho người tham dự xác nhận.

## 1. Tóm tắt

Khách đồng ý với báo cáo T5 (KPI kỳ 90%; traffic đạt 80% kèm phương án bù) và sẽ xác nhận qua email. Khách đề xuất mở rộng sang cụm "máy lọc nước công nghiệp" — hai bên thống nhất đây là thay đổi scope: GTV đánh giá impact trước, không cam kết trong họp. Chốt bổ sung người duyệt nội dung dự phòng để giữ SLA 5 ngày làm việc.

## 2. Decisions

| # | Quyết định | Căn cứ | Người chốt |
|---|---|---|---|
| D1 | Khách xác nhận báo cáo T5 qua email trước 12/08 | Đã đối chiếu trực tiếp bảng KPI + nguồn đo trong họp | chị Hoa — phía khách |
| D2 | Cụm "máy lọc nước công nghiệp" đi theo đường thay đổi scope: GTV đánh giá volume/effort trước; nếu triển khai sẽ lập phụ lục hợp đồng — KHÔNG cam kết miệng | Nằm ngoài danh mục 100 từ khóa cam kết tại PL01 | An (GTV) + chị Hoa (khách) |
| D3 | Giữ SLA duyệt nội dung 5 ngày làm việc; khách cử 1 người duyệt dự phòng khi chị Hoa vắng | Lô 3 vừa trễ 8 ngày, ảnh hưởng dây chuyền #19 | chị Hoa — phía khách |

D2 chạm scope/KPI → bắt buộc có xác nhận email của khách trước khi triển khai bất kỳ việc gì — không dừng ở lời nói trong họp.

## 3. Action items

| # | Việc | Owner | Deadline | Status |
|---|---|---|---|---|
| A1 | Gửi email tóm tắt họp + báo cáo T5 xin xác nhận | Bình | 06/08 | ☐ |
| A2 | Đánh giá cụm "công nghiệp": volume, số bài ước tính, effort, đề xuất làm/không | An | 12/08 | ☐ |
| A3 | Deploy bản vá dữ liệu có cấu trúc lên production theo tài liệu 28/07 | anh Tú | 15/08 | ☐ |
| A4 | Gửi lô nội dung 4 kèm hướng dẫn SLA cho người duyệt dự phòng | Chi | 08/08 | ☐ |
| A5 | Đặt lịch họp trình kết quả kiểm tra giữa kỳ + verdict phương án backlink giai đoạn 2 | Bình | 25/08 | ☐ |

## 4. Follow-up từ meeting trước (05/07)

| Action cũ | Status | Ghi chú |
|---|---|---|
| A2 (05/07) — cấp quyền GSC cho GTV | done | Nhận quyền 08/07 |
| A4 (05/07) — duyệt lô nội dung 3 | trễ | Duyệt xong 30/07, trễ 8 ngày so với SLA → sinh D3 hôm nay |

## 5. Link liên quan

- `09-reporting/VIDU_bao-cao-thang-T5_v1.md` — báo cáo được review trong họp.
- Feedback phát sinh: khách muốn bảng KPI có thêm cột "so với tháng trước" → đã tách thành entry `FB-2026-08-05-binh-01` trong `12-feedback-lessons/feedback-log.md`.

## Done-criteria (đối chiếu DoD template)

- [x] Mọi action item đúng 1 owner có tên + deadline — không dòng nào ghi "team/cả hai bên".
- [x] Decision chạm scope (D2) có căn cứ + kế hoạch xác nhận email.
- [x] Follow-up meeting trước đối chiếu đủ — không action nào rơi tự do.
- [x] Feedback trong họp đã tách thành entry feedback-log.
- [x] Append `log.md` op `meeting`; update `index.md` (không chạm gate nào trong buổi này).
