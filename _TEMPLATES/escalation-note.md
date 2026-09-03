---
client: "{{CLIENT}}"
cong_doan: "{{#n}}"
ws: "{{XX}}"
ngay: "{{YYYY-MM-DD}}"
tin_hieu: "{{blocked >3 ngày | khách giữ hạng mục | lệch số giữa nguồn | SLA quá 2 lần | traffic <70% lộ trình sau T6 | đổi phạm vi}}"
muc: "{{vàng | đỏ}}"
nguoi_bao: "{{alias}}"
bao_cho: "{{SEO Lead Project | SEO Director | Account | Vincent}}"
han_quyet: "{{YYYY-MM-DD}}"
status: open
---

# {{CLIENT}} — Báo đỏ #{{n}} — {{tiêu đề 1 dòng: việc gì đang kẹt}}

> Naming: `{{CLIENT}}_escalation-{{YYYYMMDD}}-{{slug}}.md` → `10-client-management/`. Viết trong 15 phút, không chờ đủ dữ liệu — thiếu thì ghi "chưa rõ". Tin xấu đi trước, kèm phương án; im lặng làm người nhận tự dựng phiên bản tệ hơn. Append `log.md` op `feedback` (nguồn: internal) ngay khi gửi.

## 1. Chuyện gì — 3 dòng

- Việc: {{công đoạn #n / deliverable nào}}
- Kẹt từ: {{ngày}} → đã {{N}} ngày · phụ thuộc: {{khách / dev / data / nội bộ}}
- Evidence: {{link bảng B, email, số liệu — không kể cảm nhận}}

## 2. Nếu không xử lý — nói bằng ngôn ngữ khách

{{1-2 câu Account có thể nói nguyên văn với khách: mốc nào trễ, KPI nào ảnh hưởng, trễ bao lâu. Không thuật ngữ nội bộ.}}

## 3. Phương án đề xuất (chọn 1, người quyết chỉ cần tick)

| # | Phương án | Được | Mất | Ai làm | Xong khi |
|---|---|---|---|---|---|
| A | {{khuyến nghị — ghi rõ "đề xuất"}} | | | | |
| B | {{phương án dự phòng}} | | | | |

## 4. Cần người nhận quyết gì, trước ngày nào

- {{Quyết định 1 — deadline}}
- {{Nếu không quyết → mặc định GTV sẽ làm A vào ngày ...}} (mặc định phải reversible)

## 5. Đóng vòng

| Ngày | Quyết định | Người quyết | Hành động đã làm | Feedback-log |
|---|---|---|---|---|
| | | | | {{FB-... nếu thành lesson}} |

## Done-criteria

- [ ] Mục 2 viết được bằng ngôn ngữ khách (Account đọc là dùng được).
- [ ] Có ≥1 phương án reversible + mặc định nếu không ai quyết.
- [ ] Đã gửi đúng người theo bảng Duyệt bảng B; log op `feedback`.
- [ ] Đóng vòng ghi vào mục 5; tín hiệu lặp lần 2 cùng loại → bắt buộc mở lesson `12-feedback-lessons/` (khủng hoảng lần 2 là lỗi hệ thống).
