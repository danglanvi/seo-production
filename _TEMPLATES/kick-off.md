---
client: "{{CLIENT}}"
cong_doan: 12
ws: 10-client-management
ngay: "{{YYYY-MM-DD}}"
hinh_thuc: "{{online | offline — địa điểm}}"
tham_du_gtv: "{{SEO Lead, Account, ...}}"
tham_du_khach: "{{tên + chức danh}}"
pic: "{{ACCOUNT}}"
status: draft
version: v1
---

# {{CLIENT}} — Kick-off dự án SEO

> Naming: `{{CLIENT}}_kick-off_v{{N}}.md` → `10-client-management/`. Trước buổi: đọc `00-client-context/` + `kpi-commitments.md` + OKRs đã duyệt (#8).
> Kick-off nội bộ chạy TRƯỚC kick-off khách: chốt Tier 2 checklist nào được bật → ghi vào cột Ghi chú dòng #12 `index.md`.

## 1. Agenda

| # | Nội dung | Phút | Người dẫn |
|---|---|---|---|
| 1 | Giới thiệu team 2 bên + vai trò | {{...}} | {{Account}} |
| 2 | Mục tiêu dự án + KPI cam kết (đọc từ kpi-commitments) | {{...}} | {{SEO Lead}} |
| 3 | Timeline {{8/10/12}} tháng + 5 pha + mốc cứng | {{...}} | {{SEO Lead}} |
| 4 | RACI + việc cần khách làm + SLA phản hồi | {{...}} | {{Account}} |
| 5 | Kênh liên lạc + nhịp báo cáo + Q&A | {{...}} | {{Account}} |

## 2. RACI GTV ↔ client

| Hạng mục | GTV | Khách | Ghi chú |
|---|---|---|---|
| Chiến lược + thực thi SEO | R/A | C/I | {{...}} |
| Duyệt content / xuất bản CMS | {{R \| C}} | {{A \| R}} | {{theo mô hình thực thi/advisory}} |
| Technical fix trên website | C (khuyến nghị) | R (dev khách) | {{hoặc GTV nếu HĐ bao}} |
| Cấp quyền truy cập (GA4, GSC, CMS, hosting) | I | R | deadline: {{dd/mm}} |
| Nghiệm thu + thanh toán | I | R/A | theo HĐ |

## 3. Cam kết 2 bên

| Bên | Cam kết | Mốc/SLA |
|---|---|---|
| GTV | KPI theo HĐ + báo cáo tháng đúng hạn + escalate sớm khi có risk | {{...}} |
| GTV | Deliverable qua QC nội bộ trước khi gửi | xuyên suốt |
| Khách | Phản hồi duyệt trong {{04/07 — theo HĐ}} ngày làm việc; quá hạn = auto-accept nếu HĐ quy định | {{...}} |
| Khách | Cấp đủ quyền truy cập + đầu mối quyết định duy nhất | {{dd/mm}} |
| Khách | Không tự triển khai SEO/backlink ngoài kế hoạch chung | xuyên suốt |

## 3b. Kỳ vọng & giới hạn — nói rõ với khách ngay buổi đầu

> Mục đích: đặt kỳ vọng một lần, có văn bản, để tháng 3-4 không phải giải thích lại. Account đọc nguyên văn, ghi vào meeting note, gửi lại email xác nhận. Mọi dòng dưới đây là luật vận hành đã có trong hệ (CLAUDE.md §6.2, `tier-1-geo.md` GE-05, content-plan-matrix §1) — không phải cam kết mới.

| Chủ đề | Điều GTV nói với khách | Nguồn luật |
|---|---|---|
| Thời gian có kết quả | Content cần **~100 ngày** để mature; số liệu 2-3 tháng đầu là **leading indicator** (coverage, index, entity), traffic/lead là lagging — báo cáo tháng sẽ tách 2 nhóm này | content-plan-matrix §1 · KO-06 |
| Backlink | **90% dự án không cần đẩy mạnh link** — gate #25 (T6) chỉ mở khi có evidence; khách không tự mua link ngoài kế hoạch | CLAUDE.md §6.2 |
| GEO / AI search | Không hứa "được AI cite theo prompt X"; số AI là **directional**, kèm nguồn + tháng + model version; không bán llms.txt hay schema như "đòn bẩy citation" | GE-05 · GE-35 |
| Việc phía khách quyết tốc độ | SLA duyệt {{04/07}} ngày làm việc; hạng mục khách giữ (access, deploy, duyệt) quá hạn sẽ được ghi rõ trong báo cáo tháng kèm "rủi ro nếu trễ" | §3 bảng cam kết · ORCHESTRATOR §7 |
| Thay đổi website | Khách sửa cấu trúc/website/nội dung ngoài kế hoạch → báo GTV trước; đây là nguyên nhân rớt hạng phổ biến nhất sau T4 | red-flag Account §6 |
| Cách đo | Số liệu đối chiếu trên **công cụ ghi trong HĐ**; khách đo tay lệch → đồng kiểm, ghi dung sai ±% | Account CLAUDE §10 |
| Kỳ vọng mềm ngoài HĐ | {{liệt kê điều khách "mong" nhưng HĐ không có — vd thiết kế web, dataset, thị trường phụ}} → chốt bằng văn bản: làm/không làm/tính phí | handoff BD mục 4 |

- [ ] Khách xác nhận bảng này qua email/biên bản trước khi kết thúc T1.

## 4. Tier 2 checklist được bật (chốt tại kick-off nội bộ)

| Tier 2 item | Bật? | Lý do |
|---|---|---|
| {{tên item trong sop/06-self-checklist/tier-2-project-specific.md}} | {{☐/☑}} | {{...}} |

## 5. Kênh liên lạc & nhịp

| Kênh/nhịp | Giá trị |
|---|---|
| Kênh chính | {{group Zalo/Slack/email}} |
| Đầu mối GTV / khách | {{ACCOUNT}} / {{tên}} |
| Báo cáo tháng | ngày {{dd}} hằng tháng, qua {{email}} |
| Meeting định kỳ | {{tần suất + khung giờ}} |

## 6. Next steps sau kick-off

| # | Việc | Owner | Deadline |
|---|---|---|---|

## Done-criteria

- [ ] Kick-off diễn ra, meeting note lưu theo `_TEMPLATES/meeting-note.md` với action items + owner + deadline.
- [ ] RACI + SLA phản hồi được khách xác nhận (email/biên bản).
- [ ] Bảng "Kỳ vọng & giới hạn" (3b) đã nói với khách và có xác nhận văn bản; kỳ vọng mềm ngoài HĐ đã chốt làm/không làm.
- [ ] Tier 2 đã chốt và ghi vào cột Ghi chú dòng #12 `index.md`.
- [ ] Quyền truy cập có deadline + owner phía khách.
- [ ] Update `index.md` #12 + append `log.md` op `meeting`.
