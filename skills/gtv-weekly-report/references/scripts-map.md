# Bản đồ script — dùng cái nào, lúc nào

> Nạp file này khi cần chọn script (Pha 1 FETCH, Pha 2 ANALYZE, Pha 3 RENDER) hoặc khi bàn giao cho người mới. 15 script, chia 4 nhóm. Mọi script đều chạy được độc lập với `-h`.
>
> Nguyên tắc chung: **script chạm data lớn, LLM chỉ đọc digest.** Tab URL-level hàng chục nghìn dòng luôn tải bằng CSV export (1 request, không tốn quota `values` API) rồi lọc local — không bao giờ nạp vào context.

---

## 1. FETCH — kéo số về máy

| Script | Kỳ | Vào | Ra |
|---|---|---|---|
| `fetch_weekly_data.py` | TUẦN | `report-config.yaml` (+ `--week N`, `--report-id`) | `02-raw/seo-data/weekly/<YYYY>-W<NN>/` — CSV thô + `digest.json` + `digest.md` |
| `fetch_period_data.py` | THÁNG · QUÝ | khối `periods:` trong config (+ `--period 2026-07`) | `02-raw/seo-data/<monthly\|quarterly>/<kỳ>/` — cùng cấu trúc |
| `capture_sheet_range.py` | mọi kỳ | `--workbook <key> --tab "<tên>" --range A1:N30` | PNG chụp literal vùng sheet (bậc 2 thang capture) |

1 lần `values.batchGet` cho MỖI workbook (quota Sheets 60 reads/phút). Tab không tồn tại → script bỏ range đó, không chết cả lần fetch.

## 2. ANALYZE — biến số thô thành thứ đọc được

| Script | Kỳ | Việc |
|---|---|---|
| `pv_movers.py` | TUẦN | Top page tăng/giảm theo **ΔPV** (chuẩn team; clicks chỉ là cột phụ). Tự tách losers/gainers, không trộn dấu |
| `period_analyze.py` | THÁNG · QUÝ | Top mover + rollup theo dimension (intent/ngành/khu vực) + **độ phủ so BẢNG 1**, gộp trong 1 lần tải tab (tab kỳ tới ~100K dòng) |
| `apply_groups.py` | mọi kỳ | Gộp Applythanks theo Page Group — tải NGUYÊN tab rồi cộng local (range trong config chỉ lấy ~80 dòng đầu, cộng nhóm sẽ thiếu) |
| `blog_groups.py` | TUẦN | Nhóm chủ đề Blog: Clicks nguyên văn pivot, Pos **dẫn xuất** trung bình trọng số theo Impressions. Chạy offline, 0 API call |
| `url_yoy_forensics.py` | QUÝ | Truy nguyên URL từng có PV lớn kỳ trước nhưng sụt sâu kỳ này — phân rã theo nhóm URL, tách «mất hạng» khỏi «mất cầu» khỏi «mất hiển thị» |
| `okrs_score.py` | QUÝ | Chấm điểm KR + Objective thang 0,0–1,0 · sinh danh sách carry-over · soi chất lượng bản nháp OKRs kỳ kế |

## 3. KIỂM — ba cổng bắt buộc của deck kỳ

| Script | Kiểm gì | Fail thì |
|---|---|---|
| `bang1_parser.py` | Tự tính lại Δ và % từ hai cột giá trị gốc của BẢNG 1 rồi đối chiếu ô công thức trên sheet | DỪNG, truy nguồn. Ô sheet sai → báo team sửa sheet, deck ghi số đúng + note ở slide phụ lục «đã sửa gì» |
| `reconcile_totals.py` | Các nguồn cùng nói về «tổng PV/Apply của kỳ» lệch nhau bao nhiêu và vì sao (BẢNG 1 vs Run-rate vs URL-level) | Ghi độ phủ % lên slide dưới dạng chip scope; độ phủ thấp → không kết luận trên mẫu con |
| `build_deck.py` (validator) | Còn `{{` · còn `{"t":` · còn `**` chưa render · còn `[[` chưa resolve · thiếu `data_meta` · số slide lệch yaml | Build FAIL (exit≠0). Không có chế độ cảnh báo suông |

## 4. RENDER — dựng bản giao

| Script | Ra gì | Ghi chú |
|---|---|---|
| `build_source_links.py` | `09-reporting/data-sources.yaml` — registry key → link `#gid=` của tab | Chạy TRƯỚC build khi `source_links:` trong config có thay đổi. `--check` chỉ đối chiếu |
| `build_deck.py` | Deck HTML tự chứa 1920×1080 | Bản giao chính thức. **KHÔNG export PDF** trừ khi được yêu cầu rõ |
| `build_pptx.py` | PowerPoint gốc (text box · bảng · chart native — sửa được) | Chỉ khi client cần bản tự sửa. Ảnh nhúng thật, chart là chart PowerPoint |
| `export-pdf.sh` | PDF | Chỉ chạy khi Vincent yêu cầu rõ trong phiên |
| `pdf2png.swift` | PNG từ PDF | Phụ trợ cho `capture_sheet_range.py` (không cần poppler) |

## 5. Thứ tự chạy một kỳ THÁNG/QUÝ

```bash
# 1 · kéo số
python3 skills/gtv-weekly-report/scripts/fetch_period_data.py \
    --config 09-reporting/report-config.yaml --period 2026-07

# 2 · phân tích URL-level (mỗi nguồn khai trong periods.<kỳ>.sources)
python3 skills/gtv-weekly-report/scripts/period_analyze.py \
    --config 09-reporting/report-config.yaml --period 2026-07 --source jl

# 3 · BA CỔNG KIỂM — chạy trước khi viết chữ
python3 skills/gtv-weekly-report/scripts/bang1_parser.py    --config … --period 2026-07
python3 skills/gtv-weekly-report/scripts/reconcile_totals.py --config … --period 2026-07

# 4 · registry link nguồn (khi source_links: đổi)
python3 skills/gtv-weekly-report/scripts/build_source_links.py \
    --config 09-reporting/report-config.yaml --out 09-reporting/data-sources.yaml

# 5 · dựng deck
python3 skills/gtv-weekly-report/scripts/build_deck.py \
    --content <content.yaml> --skeleton 09-reporting/weekly-template/deck-skeleton.html \
    --datadir 02-raw/seo-data/quarterly/<kỳ> --sources 09-reporting/data-sources.yaml \
    --out <deck.html>

# 6 · bản PowerPoint (chỉ khi client cần sửa)
python3 skills/gtv-weekly-report/scripts/build_pptx.py \
    --content <content.yaml> --out <deck.pptx> --base . \
    --sources 09-reporting/data-sources.yaml
```

Bản đầy đủ kèm QA overflow và checklist file-back: `09-reporting/RUNBOOK-bao-cao-ky.md`.

## 6. Script chưa có — biết để không đi tìm

| Thiếu | Hiện làm sao | Khi nào nên viết |
|---|---|---|
| Fetch GA4/GSC trực tiếp | Đọc qua file trung gian + ảnh chụp; `ga4_property_id`/`gsc_site` trong config còn trống | Ngay khi client cấp quyền cho service account |
| QA overflow đóng gói | Script Playwright viết tay mỗi lần (mẫu trong RUNBOOK) | Khi chạy kỳ thứ 3 — lúc đó đã đủ chắc về khuôn |
| Diff/back-port HTML → YAML | Làm bằng script tạm mỗi lần client sửa thẳng HTML | Nếu chuyện này lặp ≥3 kỳ |
