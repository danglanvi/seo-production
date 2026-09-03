# weekly-report-slides/ — template deck báo cáo tuần (client-facing)

Skeleton HTML cho deck báo cáo tuần theo skill `gtv-weekly-report` — chuẩn `frontend-slides` (stage cố định 1920×1080, export PDF bằng Playwright). Master giữ bản **client-neutral** (`{{PLACEHOLDER}}`); instance customize tại `09-reporting/weekly-template/` (logo client + tên đối thủ + agenda).

## Cách dùng (trong instance)

1. Lần đầu setup client: copy folder này → `09-reporting/weekly-template/`, thay logo (`assets/logo-client.png`, `assets/logo-gtv.png`), điền tên client/đối thủ cố định.
2. Mỗi tuần: skill `gtv-weekly-report` CLONE `deck-template.html` → `09-reporting/weekly/<YYYY>-W<NN>/<CLIENT>_bao-cao-tuan-W<NN>_v1.html`, điền data từ `digest.json` theo `skills/gtv-weekly-report/references/slide-map.md`.
3. Giao khách bản **HTML** (mở trực tiếp bằng trình duyệt, luật HTML-only của hệ báo cáo). Chỉ export PDF khi khách yêu cầu rõ: dùng `python3 skills/gtv-weekly-report/scripts/qa_deck.py --pdf` nếu có, hoặc Playwright/Chrome headless theo `RUNBOOK-bao-cao-ky.md` — skill `frontend-slides` KHÔNG đóng gói trong SEO Production.

## Loại slide có sẵn trong skeleton (12 exemplar)

| # | Loại | Dùng cho |
|---|---|---|
| 1 | cover | Trang bìa gradient GTV |
| 2 | agenda | 4 mục chuẩn |
| 3 | runrate | Overview KPI — card run-rate năm/tháng + bảng tuần (highlight tuần hiện tại) |
| 4 | bảng WoW 2 cột | BẢNG 1 per nhóm trang + NHẬN XÉT phải |
| 5 | bảng full-width | Intent / ngành / khu vực + NHẬN XÉT dưới |
| 6 | top movers | 2 bảng URL tăng/giảm do AI lọc từ GSC + action |
| 7 | capture | Ảnh Looker/sheet/tool từ `02-raw/screenshots/` + NHẬN XÉT (không có ảnh → `.manual-slot`) |
| 8 | SOW status | Chips đếm status + bảng việc trễ |
| 9 | cần client hỗ trợ | Bảng SCOPE/Description (điền trong họp) |
| 10 | 3rd party | Bảng đối thủ + line chart SVG tự vẽ (không lib ngoài) |
| 11 | Q&A | — |
| 12 | thank you | — |

## Luật cứng

- **CSS completeness**: mọi class dùng trong markup phải có rule trong `<style>` (House Rules frontend-slides). Skeleton này đã audit đủ — thêm class mới thì thêm CSS ngay.
- **Số phải trace được** về `digest.json` của tuần (`02-raw/seo-data/weekly/`). Ô Δ dùng class `pos`/`neg`/`mut`.
- Mỗi slide data có dòng `.data-meta` ghi **nguồn + kỳ dữ liệu** (luật trạm Reporter).
- Ảnh nhúng bằng relative path về `02-raw/screenshots/` — không copy ảnh vào folder deck.
- 3rd-party data chỉ **minh họa xu hướng** — không phải số nghiệm thu (ranh giới `gtv-client-report` Path A).
- Deck KHÔNG render verdict "đạt KPI nghiệm thu" — đó là việc của báo cáo tháng/quý (`gtv-client-report` + `kpi-commitments.md`).
