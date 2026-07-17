# Screenshots — kho ảnh chụp màn hình của dự án

Kho ảnh IMMUTABLE phục vụ audit, benchmark, review cấu trúc và theo dõi SERP/AI. Mọi ảnh chụp trong quá trình làm dự án đều lưu tại đây — không rải trong các folder workstream.

## Cấu trúc

| Folder | Chứa gì | Ví dụ |
|---|---|---|
| `own-site/<page-slug>/` | Ảnh site của client, gom theo page | `own-site/iphone-plp/` |
| `competitors/<domain-slug>/` | Ảnh site đối thủ, gom theo domain | `competitors/cellphones-com-vn/` |
| `serp-ai/` | SERP, AI Overview, câu trả lời ChatGPT/Perplexity/Gemini | ảnh AIO cho query mục tiêu |
| `tools/` | Dashboard GSC, GA4, Ahrefs, SpySERP... | ảnh GSC performance 28 ngày |

## Quy ước đặt tên

`YYYYMMDD_<subject-slug>_<viewport|scope>.png`

- `20260717_iphone-plp_desktop-full.png` — full-page desktop (hậu tố `-full`)
- `20260717_iphone-plp_mobile-buybox.png` — crop 1 block (hậu tố `-<block>`)
- `20260717_q-iphone-15-cu_aio.png` — ảnh SERP/AI theo query (slug query, prefix `q-`)
- `20260717_gsc-performance-28d.png` — dashboard tool
- Ảnh do khách gửi: thêm hậu tố `_client`.

## Protocol 6 điều

1. **AI chụp qua browser capability** (Firecrawl screenshot / browser tool của runtime): sau khi chụp phải **tải ảnh về và lưu NGAY** vào đúng sub-folder với tên chuẩn — không để ảnh chỉ tồn tại trong chat hoặc thư mục tạm.
2. **Ghi log mỗi đợt chụp**: append `log.md` op `capture` — 1 entry/đợt, liệt kê danh sách file + dòng `Dùng cho: <deliverable path hoặc công đoạn #n>`. Đây là sợi liên kết screenshot ↔ deliverable; tra ngược bằng grep log.
3. **Deliverable nhúng ảnh bằng relative path** (vd `![](../02-raw/screenshots/own-site/iphone-plp/20260717_iphone-plp_desktop-full.png)`) — không copy ảnh vào folder workstream. Ngoại lệ duy nhất: artifact build tự chứa (kiểu `build/img/`) giữ ảnh riêng của nó.
4. **Ảnh người chụp tay** (khách gửi, chụp màn hình họp) cũng lưu vào đây theo cùng naming.
5. **Immutable**: không sửa/đè ảnh cũ. Chụp lại = file mới với prefix ngày mới — so sánh before/after dựa vào prefix ngày.
6. **Ảnh >5MB không commit git** — nén JPG/giảm width trước khi lưu; file quá nặng đưa Drive và dán link vào deliverable (xem SYNC.md).
