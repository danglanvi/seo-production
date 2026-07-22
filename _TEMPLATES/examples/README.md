> ⚠️ MẪU MINH HỌA — client hư cấu "Công ty Ví Dụ / vidu.vn", số liệu giả định để agent noi theo CẤU TRÚC + ĐỘ SÂU + GIỌNG.
> Không copy số vào deliverable thật. Mẫu thật của dự án tích lũy trong instance qua vòng feedback → lesson → promote.

# Lớp MẪU ĐẠT CHUẨN — `_TEMPLATES/examples/`

## 1. Lớp này để làm gì

Trụ cột 4 của mindset Agentic SEO: **"Agent chỉ tốt bằng bối cảnh và mẫu bạn đưa."**

- Template khung trong `_TEMPLATES/` trả lời câu hỏi *điền ô nào*. Lớp mẫu này trả lời *điền sâu đến đâu, evidence cụ thể cỡ nào, giọng ra sao* — thứ mà khung trống không dạy được.
- Chuẩn ở đây là chuẩn TỐI THIỂU về độ sâu: deliverable thật nông hơn mẫu cùng loại → coi như chưa đạt, tự sửa trong vòng tự kiểm của trạm trước khi submit QC (§3 CLAUDE.md).
- Mẫu KHÔNG thay checklist: QC vẫn chấm theo checklist của ma trận M (§5 CLAUDE.md). Mẫu vênh template khung/checklist (do lệch nhịp migration) → khung + checklist thắng.

## 2. Luật nạp (80/20)

1. **Chỉ nạp mẫu CÙNG LOẠI deliverable đang làm** — làm QC report thì nạp `qc-report_MAU.md`, KHÔNG nạp 4 mẫu còn lại. Không bao giờ quét cả folder này.
2. Thứ tự nạp khi Work: template khung → mẫu cùng loại → checklist (nếu công đoạn có). Mẫu đọc để CALIBRATE độ sâu và giọng, không đọc để chép.
3. Cấm copy câu chữ, tên, link, số liệu từ mẫu vào deliverable thật — mọi số trong mẫu là hư cấu tròn trịa có chủ đích (100 keyword, 20.000 sessions, DR 20...) để ai copy nhầm cũng nhận ra ngay.
4. Trong mẫu, banner ⚠ đứng TRƯỚC frontmatter (luật an toàn riêng của lớp mẫu). Deliverable thật: frontmatter đứng đầu file và KHÔNG có banner.
5. Luật này bổ sung §10 CLAUDE.md: `examples/` trong folder SKILL vẫn tuyệt đối không nạp lúc production; folder này là lớp mẫu DELIVERABLE, nạp theo luật riêng tại đây.

## 3. Bảng mẫu ↔ trạm ↔ template khung

| Mẫu | Trạm (WS) | Template khung | Nạp khi |
|---|---|---|---|
| `qc-report_MAU.md` | 03-audits/qc — dùng cho MỌI trạm khi QC | `_TEMPLATES/qc-report.md` | Mọi prompt `QC <path> theo công đoạn <n>` |
| `audit-findings_MAU.md` | 03-audits | `_TEMPLATES/audit-toan-dien.md` (trích đoạn findings + action) | Work #2, #5, #24, #27, #29 |
| `gate-offpage-decision_MAU.md` | 07-offpage | `_TEMPLATES/gate-offpage-decision.md` | Work gate #25◇ (T6) |
| `bao-cao-thang_MAU.md` | 09-reporting | `_TEMPLATES/bao-cao-thang.md` (chế độ THÁNG) | Work báo cáo tháng (nhịp #30) |
| `meeting-note_MAU.md` | 10-client-management | `_TEMPLATES/meeting-note.md` | Ghi note họp khách/nội bộ (#12, #31, định kỳ) |

Loại deliverable chưa có mẫu (topical map, onpage batch, OKRs...) → làm theo template khung + checklist; khi instance sinh được bản đạt chuẩn thì promote theo mục 5.

## 4. Bộ dữ liệu hư cấu dùng chung (đọc 30 giây để hiểu cả 5 mẫu)

Cả 5 mẫu là MỘT dự án xuyên suốt — để agent thấy dữ liệu chảy giữa các trạm: audit T1 tìm ra lỗi nền → báo cáo T5 giải trình hậu quả của lỗi đã dọn → gate T6 chỉ mở xét khi nền đã sạch.

| Trường | Giá trị hư cấu |
|---|---|
| Client / domain | Công ty TNHH Ví Dụ — vidu.vn (phân phối máy lọc nước) |
| Gói | 10 tháng, T1 = 03/2026 (T2 = 04, T5 = 07, T6 = 08/2026) |
| KPI cam kết (PL01 hư cấu) | Danh mục 100 từ khóa; 50 từ đạt TOP 10 ở T10 (lũy kế T5: 30) · organic traffic 40.000 sessions/tháng ở T10 (lũy kế T5: 20.000) |
| Nhân sự | GTV: An (SEO Lead Project) · Bình (Account) · Chi (Content Leader). Khách: chị Hoa (TP Marketing) · anh Tú (dev) |

## 5. Promote mẫu thật từ instance (vòng nâng cấp lớp mẫu — §9 CLAUDE.md vòng 2)

1. **Phát hiện**: deliverable thật được khách/Lead đánh giá tốt hoặc QC điểm cao → append entry vào `12-feedback-lessons/feedback-log.md` như mọi feedback khác.
2. **Distill**: pattern lặp ≥2 lần hoặc Lead chỉ định → lesson `scope: system`, đề xuất đúng 1 câu: "dùng `<path deliverable>` làm mẫu chuẩn loại `<Y>` thay mẫu hư cấu ở master".
3. **Duyệt**: Lead/Vincent duyệt — Claude không tự thay mẫu.
4. **Neutral hóa BẮT BUỘC trước khi về master**: thay tên client + domain → "Công ty Ví Dụ / vidu.vn"; làm tròn mọi số về số minh họa; xóa tên người thật (thay bằng bộ tên mục 4), link thật, số hợp đồng; giữ nguyên cấu trúc + độ sâu + giọng; gắn banner ⚠ 2 dòng lên đầu file.
5. **Thay mẫu ở MASTER**: ghi đè file trong `_TEMPLATES/examples/` (hoặc tăng version nếu giữ song song), ghi `MIGRATION.md` + log op `refactor`; instance nhận qua migration — KHÔNG sửa mẫu trong instance tại chỗ.

Luật an toàn tuyệt đối: mẫu còn dính bất kỳ dữ liệu client thật nào (tên, số, link, người, số hợp đồng) thì KHÔNG được nằm trong folder này — master sẽ đi tới mọi client tương lai.

## 6. Done-criteria khi thêm/thay một mẫu

- [ ] Banner ⚠ đủ 2 dòng ở đầu file; grep tên/số/link client thật = 0 kết quả.
- [ ] Có dòng tương ứng trong bảng mục 3 (mẫu ↔ trạm ↔ template khung ↔ nạp khi).
- [ ] Dài 60-120 dòng — đủ sâu để noi theo, không lan man.
- [ ] Cấu trúc khớp template khung hiện hành; giọng khớp trạm (QC sắc lạnh, account chuyên nghiệp, note họp gọn).
- [ ] Đã ghi `MIGRATION.md` + log op `refactor` ở master.
