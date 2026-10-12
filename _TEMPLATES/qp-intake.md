---
type: qp-intake
client: {{CLIENT}}
date: {{YYYY-MM-DD}}
nguoi_dien: {{Lead}}
---

# {{CLIENT}} — Phiếu đầu vào chẩn đoán Query Processing

> Lead điền phiếu này **trước khi** gọi lệnh `chẩn đoán QP {{CLIENT}}`. Lưu ở `03-audits/ranking/_work/{{CLIENT}}_qp-chan-doan_v{{N}}/intake.md`. Ô nào chưa biết thì ghi "chưa có". Đừng xoá ô. Agent đọc phiếu này đầu tiên. Phiếu đủ thì agent chỉ dừng hỏi một lần (xác nhận Pre-work).

## A. Bắt buộc (thiếu thì agent dừng)

| # | Thông tin | Điền |
|---|---|---|
| A1 | Tên khách, domain chính | {{Acme Shop · acme.vn}} |
| A2 | Lead phụ trách, người làm dev và content (tên thật, dùng cho cột "Ai làm") | {{Lead: … · Dev: … · Content: …}} |
| A3 | Bộ keyword cam kết: file có cột keyword (sheet KPI tải CSV, hoặc file trong `00-client-context/`), tên cột keyword, và nhóm cần chẩn đoán nếu bộ có nhiều nhóm | {{02-raw/client-docs/kpi-2026.csv · cột "Từ khóa" · cột "Nhóm" = "Thúc đẩy"}} |
| A4 | Engine đo theo hợp đồng: thiết bị, vị trí, ngôn ngữ, Google nào | {{Google Mobile · Hà Nội · tiếng Việt · google.com}} |
| A5 | File export SpySERP (CSV) đã lưu trong `02-raw/seo-data/keywords/`. Nhiều trang lịch thì liệt kê đủ các file; cộng lại phải ≥35 ngày | {{2026-10-09_spyserp_bo-thuc-day.csv · …_p2.csv (35 ngày, 08/09–12/10)}} |
| A6 | Project SpySERP: tên, có theo dõi domain đối thủ không (bản nhiều domain) | {{"Acme - TĐ", có 12 domain đối thủ}} |
| A7 | Kỳ đo nghiệm thu tới (ngày) | {{04/11/2026}} |
| A8 | Ngày bắt đầu kế hoạch 2 tuần | {{13/10/2026}} |

## B. Nên có (thiếu thì agent vẫn chạy, ghi "cần kiểm tay" và tô đỏ)

| # | Thông tin | Điền |
|---|---|---|
| B1 | Chỉ tiêu ở kỳ đo tới (Top 3/5/10), chỉ dùng trong khối nội bộ | {{12/31/117}} |
| B2 | 5–10 URL chính: trang chủ, category, landing đang nhận keyword cam kết | {{https://acme.vn/ · https://acme.vn/den-hoc/ · …}} |
| B3 | Nhật ký thay đổi 30 ngày gần nhất: URL nào vừa sửa, ngày sửa, sửa gì | {{/den-hoc/ — 04/10 — thêm bảng size}} |
| B4 | GSC: có quyền không; nếu có, export Performance theo page × query 3 tháng vào `02-raw/seo-data/keywords/` | {{có · 2026-10-09_gsc-3m_page-query.csv}} |
| B5 | Nguồn đọc SERP agent được dùng: Ahrefs, Firecrawl, hay Lead tự chụp 3 SERP | {{Firecrawl, quốc gia VN}} |
| B6 | Ràng buộc triển khai: dev bận, đang làm lại giao diện, chưa go-live, không được sửa trang nào | {{giao diện mới go-live 20/10, không sửa template trước ngày đó}} |
| B7 | Bộ keyword có nhiều nhóm với trọng số nghiệm thu khác nhau không (vd. Duy trì, Thúc đẩy) | {{có: 1 kw Thúc đẩy Top 10 ≈ 2 kw Duy trì Top 3}} |
| B8 | Lần chẩn đoán trước (nếu có): file JSON hoặc deck | {{03-audits/ranking/acme_qp-chan-doan_v1.json}} |
| B9 | URL target theo kế hoạch: file hai cột keyword và URL (topical map, content plan, sheet URL) | {{05-content-plan/url-target.csv}} |
| B10 | Volume muốn dùng trên deck: cột Volume của SpySERP (mặc định) hay nguồn khác (ghi nguồn và ngày) | {{SpySERP}} |

## C. Câu lệnh gọi agent

```
chẩn đoán QP {{CLIENT}} theo phiếu 03-audits/ranking/_work/{{CLIENT}}_qp-chan-doan_v{{N}}/intake.md
```
