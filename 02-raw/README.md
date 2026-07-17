# 02-raw — Nguồn bất biến (IMMUTABLE)

**Luật IMMUTABLE**: chỉ ADD file mới. Không sửa, không xóa, không đổi tên file đã nằm trong đây. Bản mới = file mới với ngày mới hoặc version mới. Phát hiện sai sót → thêm file đính chính, không đè.

## Bản đồ 6 sub

| Sub | Chứa gì | Ghi chú |
|---|---|---|
| `contracts-proposals/` | HĐ, phụ lục, proposal, báo giá | Input trích vào `00-client-context/kpi-commitments.md` |
| `seo-data/` | Export GSC/GA4/Ahrefs, crawl data, keyword data | Đặt tên `YYYYMMDD_<nguon>_<scope>.<ext>` |
| `logfiles/` | Server logfile cho công đoạn #27 | File nặng không commit git — đưa Drive, dán link |
| `client-docs/` | Tài liệu khách gửi (brand, sản phẩm, phân quyền) | |
| `knowledge/` | Knowledge pack: SOP + cheat-sheets | READ-ONLY trong instance; chỉ vá ở master qua `MIGRATION.md` |
| `screenshots/` | Ảnh own-site / competitors / serp-ai / tools | Protocol riêng: `screenshots/README.md` |

## Luật vận hành

1. File mới vào đây = thao tác Ingest: phân loại đúng sub → cập nhật `00-client-context/` nếu là context → ghi bảng D `index.md` → append `log.md` op `ingest`.
2. `knowledge/` không nhận file dự án — chỉ nhận bản sync từ master (checklist QC nạp đúng file theo ma trận M trong `CLAUDE.md`, không quét cả folder).
3. Deliverable KHÔNG sống ở đây — deliverable về đúng WS folder 01-11.
4. Ảnh/file >5MB: đưa Drive, dán link vào file .md trong đúng sub.
