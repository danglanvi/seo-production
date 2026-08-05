---
name: gtv-weekly-report
description: "Báo cáo tuần SEO client-facing dạng slide (AI-driven, config per client): kéo data từ các workbook Google Sheets client-agreed bằng script batchGet (80/20 — không nạp data lớn vào context), lọc top page bị ảnh hưởng, viết NHẬN XÉT + action theo rubric, phân tích PATTERN từ insights tích lũy các tuần trước, dựng deck HTML 1920×1080 tự chứa theo template chuẩn frontend-slides (kèm bản PowerPoint gốc khi client cần tự sửa, và link mở thẳng tab nguồn trên mỗi slide). Chạy được cả ba nhịp: TUẦN ~11 slide · THÁNG ~26 slide · QUÝ ~45-50 slide (deck kép tháng + tổng kết quý, kèm chấm điểm OKRs). Use when: (1) 'làm báo cáo tuần [client]', 'weekly report W[n]', 'chạy báo cáo tuần CareerViet'; (2) 'làm báo cáo tháng/quý [client]', 'tổng kết quý [n] dự án'; (3) cron thứ Năm chạy bản DRAFT tuần vừa khép; (4) 'phân tích tuần này có pattern gì' trên data weekly đã fetch. KHÔNG dùng cho: báo cáo NGHIỆM THU tuyên bố % đạt KPI cam kết (→ gtv-client-report trên kpi-commitments.md đã stable — skill này render số theo sheet vận hành, không phán đạt/không đạt), sync brief nội bộ Account↔Lead (→ acc-weekly-sync), điều tra nguyên nhân SEO sâu khi số bất thường (→ skill seo-*; skill này chỉ nhận xét + đề xuất hướng). 🔒 GTV-only, cần config 09-reporting/report-config.yaml trong instance."
---

# gtv-weekly-report — Báo cáo tuần SEO client-facing (slide)

Báo cáo TUẦN = **báo cáo vận hành**: render số từ workbook Google Sheets **client-agreed** (nguồn ghi rõ trên từng slide). Nó KHÔNG phải báo cáo nghiệm thu — không tuyên "đạt/không đạt KPI cam kết"; việc đó thuộc `gtv-client-report` (tháng/quý) trên `00-client-context/kpi-commitments.md` đã `stable`.

## Ba format deck — TUẦN · THÁNG · QUÝ

| | TUẦN — weekly catchup | THÁNG — deep dive | QUÝ — deck kép |
|---|---|---|---|
| Mục đích | Họp catchup ~15 phút theo agenda client | Review sâu khi khép tháng + đối chiếu OKRs quý | Tổng kết kỳ + nền để chốt OKRs kỳ kế |
| Độ dài | **~11 slide LEAN** (run-rate/KPI → what works → what fails+solution → task done → task next → blockers aging → new initiatives from GTV) | **~26 slide** (slide-map: movers, intent, ngành, blog groups, apply…) + lớp tháng: MoM, tiến độ OKRs quý, run-rate lũy kế, pattern 4 tuần | **~45–50 slide** — 8 section, mỗi section chạy lớp THÁNG rồi lớp QUÝ so cùng kỳ, + phụ lục (đối chiếu nguồn, những gì đã sửa, **nguồn dữ liệu + link**) |
| Nhịp build | Hằng tuần — pipeline FETCH/ANALYZE giữ nguyên 100%, chỉ content.yaml là bản lean | Ngày 2–4 tháng kế, khi data tháng khép | Ngày 2–5 tháng kế của tháng khép quý |

Map slide + luật từng format: `references/weekly-catchup-format.md` (TUẦN + THÁNG) · `references/period-report-format.md` (THÁNG + QUÝ — luật hai lớp, forensics, nền so sánh, quy công). Nạp ở Pha 0 để chọn format và Pha 3 để render.

**Quý dự án ≠ quý dương lịch** — tính theo tháng dự án (CareerViet: T1 = 05/2026 → Quý 1 khép 31/07/2026). Ghi rõ dải ngày trên cover + mọi `data_meta`.

**Rule carry-over (Vincent 23/07/2026):** task chưa done ở timeline OKRs/sheet tuần TỰ ĐỘNG chuyển sang plan tuần kế với status «Chuyển tiếp», trừ khi Vincent điều chỉnh/feedback. Slide «Task to do next week»: carry-over trước, task mới (action insights + mốc OKR) sau, mỗi task kèm PIC in đậm — trình Vincent chốt cả danh sách, không hỏi từng dòng.

## Dependency check (chạy trước, báo rõ nếu thiếu)

| Cần | Kiểm tra | Thiếu thì |
|---|---|---|
| Config instance | `09-reporting/report-config.yaml` tồn tại | DỪNG — copy schema từ `references/report-config-schema.md`, hỏi ID workbook |
| Service account | file `credentials` trong config tồn tại + được share các workbook | DỪNG — báo Vincent share workbook cho service account |
| Python google libs | `python3 -c "import yaml, googleapiclient"` | Fallback: đọc tab pivot qua MCP google-sheets (chấp nhận nhiều call, tránh tab URL-level) |
| Playwright (export PDF + chụp Looker) | `npx playwright --version` | Deck HTML vẫn giao được; PDF đánh dấu "chưa export" |
| Swift/PDFKit (capture sheet) | `which swift` | Bỏ bậc capture-sheet, dùng bậc khác của thang capture |

## Workflow 5 pha

### Pha 0 — RESOLVE
1. Đọc config + nội quy trạm `09-reporting/CLAUDE.md` (mục Chế độ TUẦN) + `00-client-context/kpi-commitments.md` (chỉ để biết ranh giới cam kết — KHÔNG render bảng nghiệm thu).
2. Chọn nhịp:
   - **TUẦN** — tuần báo cáo N = tuần vừa **KHÉP** theo `week_anchor` (mặc định của script). Muốn tuần khác: `--week N`.
   - **THÁNG / QUÝ** — kỳ phải có trong khối `periods:` của config (`--period 2026-07` / `2026-Q1`). Nạp thêm `references/period-report-format.md`. Kỳ quý = **deck kép** tháng + quý; kiểm lại dải ngày quý dự án trước khi viết chữ.
3. Kỳ THÁNG/QUÝ chạy theo `09-reporting/RUNBOOK-bao-cao-ky.md` (câu lệnh tuần tự) — checklist data phía team ở `09-reporting/PERIOD-DATA-CHECKLIST.md`.

### Pha 1 — FETCH (script, không đốt context)
```bash
# nhịp TUẦN
python3 skills/gtv-weekly-report/scripts/fetch_weekly_data.py \
  --config 09-reporting/report-config.yaml [--week N] [--report-id <id>]

# nhịp THÁNG / QUÝ (khối periods: trong config)
python3 skills/gtv-weekly-report/scripts/fetch_period_data.py \
  --config 09-reporting/report-config.yaml --period 2026-07
```
Bảng đầy đủ 15 script (fetch · analyze · kiểm · render), input/output từng cái: `references/scripts-map.md`.
- 1 `values.batchGet`/workbook (quota Sheets 60 reads/phút — KHÔNG gọi lẻ từng range qua MCP).
- Output: `02-raw/seo-data/weekly/<YYYY>-W<NN>/` (CSV thô + `digest.json` + `digest.md`).
- Workbook "Report Tuần {N}" tự tìm qua Drive search; không thấy → hỏi URL rồi chạy lại với `--report-id` (tìm được ID mới → append vào `known_ids` trong config).
- Re-fetch CÙNG tuần ghi đè folder tuần đó = bản kéo mới nhất (digest có `generated_at`); cần giữ bản cũ → rename folder trước khi chạy lại. Đây là ngoại lệ vận hành duy nhất của 02-raw, chỉ áp cho `seo-data/weekly/`.
- **Top page movers theo CHUẨN TEAM (ΔPV — không phải clicks):** với từng entry trong `config.pv_movers`, chạy:
  `python3 scripts/pv_movers.py --config … --workbook <wb> --tab "<tab>" --min-dpv <n> --out <weekdir>/movers_pv_<key>.json --save-csv <weekdir>/csv/…`
  (resolve tab theo TÊN — gid trong URL người gửi có thể trỏ tab khác). Đây là nguồn DUY NHẤT cho slide top pages; GSC clicks chỉ là cột phụ. Script tự tách losers (ΔPV<0) / gainers (ΔPV>0) — không bao giờ trộn dấu.
- **Apply theo Page Group (slide Apply Overview):** nếu config có `apply_groups`, chạy:
  `python3 scripts/apply_groups.py --config … --workbook <wb> --tab "<tab>" --out <weekdir>/apply_groups.json --save-csv <weekdir>/csv/…`
  Range trong config chỉ lấy ~80 dòng đầu tab pivot nên cộng nhóm sẽ THIẾU — script tải NGUYÊN tab rồi aggregate local; đối chiếu Grand Total với pivot Intent trên sheet trước khi render.
- **Nhóm chủ đề Blog (slide 3. Blog):** chạy `python3 scripts/blog_groups.py` trên weekdir (offline — đọc CSV pivot «Đánh giá Blog» + `data_phan_tich__blog_urllevel.csv` đã fetch) → `<weekdir>/blog_groups.json` (Clicks nguyên văn pivot, Pos dẫn xuất trọng số Imp — luật #15). Đây là input bắt buộc cho slide `blog_groups` của builder.
- Log op `ingest` (data mới vào 02-raw).

### Pha 2b — ANALYZE kỳ THÁNG/QUÝ (thêm, không thay Pha 2)

```bash
python3 .../period_analyze.py --config … --period 2026-07 --source jl --save-csv   # mover + rollup + độ phủ
python3 .../url_yoy_forensics.py --config … --period 2026-Q1 --source jl    # nhóm giảm sâu (kỳ quý)
python3 .../okrs_score.py --config … --period 2026-Q1 --md <đường dẫn>             # chấm OKRs kỳ khép
```

**BA CỔNG KIỂM chạy TRƯỚC khi viết chữ** — không có ngoại lệ:
`bang1_parser.py` (tự tính lại Δ/% từ 2 cột gốc, đối chiếu ô công thức sheet) · `reconcile_totals.py` (các nguồn cùng nói về tổng kỳ lệch nhau bao nhiêu, vì sao) · validator trong `build_deck.py` (tự chạy ở Pha 3).

Luật riêng khi viết nhận xét kỳ: hai lớp (tháng + quý) · forensics cho nhóm giảm sâu · **đối chiếu định nghĩa event giữa hai năm trước mọi số YoY** · chỉ quy công cho hạng mục đã thực sự live. Chi tiết `references/period-report-format.md` §3.

### Pha 2 — ANALYZE (Claude — chỉ đọc digest + insights cũ)
1. Đọc `digest.json` (KHÔNG đọc CSV trừ khi cần soi 1 bảng cụ thể; TUYỆT ĐỐI không đọc tab URL-level qua MCP).
2. Đọc 4-8 file `09-reporting/analysis/*-insights.md` gần nhất (nếu có) → lớp PATTERN.
3. Viết `09-reporting/analysis/<YYYY>-W<NN>-insights.md` theo `references/analysis-rubric.md`:
   - Nhận xét per section (run-rate, per nhóm trang, apply, SOW) — mỗi nhận xét có SỐ + so sánh + nguyên nhân khả dĩ + action đề xuất (owner).
   - Top pages affected: từ `top_movers_*` trong digest — chỉ top page (đã lọc `min_clicks`).
   - PATTERN: giảm ≥2 tuần liên tiếp → flag; imp tăng CTR không tăng → cơ hội title/meta; position 6-10 imp cao → push target; đối chiếu Prior Year (cột trong run-rate) để tách seasonal vs decay.
4. Số bất thường (lệch >20% không giải thích được) → ghi `CANNOT-VERIFY / cần điều tra` + đề xuất skill điều tra (content-refresh, technical-seo-audit…) — KHÔNG bịa nguyên nhân.

### Pha 3 — RENDER (từ W12: BUILDER tự động — không viết HTML tay)
1. **Viết `content.yaml`** theo `references/content-schema.md` — AI chỉ viết nhận xét/action + khai báo data-ref; số liệu do builder đổ từ weekdir. Copy `content-w<nn-1>.yaml` tuần trước làm khung (exemplar chuẩn: `weekly/2026-W11/content-w11.yaml`). Nội dung nhận xét vẫn tuân toàn bộ luật trình bày trong `references/slide-map.md` (#3, #7, #8, #13…).
2. **Build deck**:
   `python3 skills/gtv-weekly-report/scripts/build_deck.py --content <content.yaml> --skeleton 09-reporting/weekly-template/deck-skeleton.html --datadir <weekdir> --out 09-reporting/weekly/<YYYY>-W<NN>/<CLIENT>_bao-cao-tuan-W<NN>_v1.html`
   Builder tự: ráp slide theo type, class `pos`/`neg`/`mut`, `kpi-row`/`total`/`hl`, breadcrumb + pill + brandbar (logo nhúng 1 lần — deck ~200KB), page-no n/N, validate (đủ slide, không còn `{{`, data-meta đủ) — FAIL thì exit non-zero, sửa yaml rồi build lại.
   CHỈ sửa HTML tay khi builder chưa cover loại slide → dùng `type: manual` + ghi feedback để nâng builder (không sửa trực tiếp file build ra).
2a. **Skin chuẩn = frontend-slides (bản v5 W11 — Vincent chốt 23/07)**: `deck-skeleton.html` mang skin này (Bricolage Grotesque/IBM Plex Mono/Fraunces, cover gradient #0693E3→#9900EF). Bản giao diện cũ giữ ở `deck-skeleton-classic.html` — chỉ dùng khi được yêu cầu.
2b. **Edit-mode**: skeleton đã có INLINE EDIT + DECK CHROME (ES5) — builder thay `EDIT_KEY` bằng `meta.edit_key` trong yaml; mỗi deck tuần đặt key riêng (vd `crv-w12-v1`) để không đè bản sửa của nhau.
2c. **Link nguồn trên slide (từ 04/08/2026):** khai `source_links:` trong `report-config.yaml` → chạy `build_source_links.py` → dùng token `[[key]]` / `[[key|nhãn]]` trong `data_meta` và ô bảng → truyền `--sources 09-reporting/data-sources.yaml` cho builder. Build FAIL nếu còn token không tra được. Deck kỳ THÁNG/QUÝ **bắt buộc có slide phụ lục «Nguồn dữ liệu»** (bảng workbook × tab-link × slide + khối nguồn chưa có link).
2d. **Bản PowerPoint** (chỉ khi client cần tự sửa): `build_pptx.py --content <yaml> --out <pptx> --base . --sources 09-reporting/data-sources.yaml` — text box/bảng/chart/hyperlink đều là đối tượng PowerPoint thật. Không thay cho bản HTML: HTML vẫn là bản giao chính thức.
3. Phần cần HÌNH thay vì bảng — **thang capture** (dừng ở bậc đầu tiên chạy được):
   a. **Looker Studio** (nếu config có `looker.url` — link-view): `npx playwright screenshot --viewport-size=1920,1080 --wait-for-timeout=20000 "<url>" <out.png>` (per-page: dán URL `/page/<id>` nếu có). Widget không render (ô mờ) → bậc dưới.
   b. **Sheet range literal**: `python3 scripts/capture_sheet_range.py --config … --workbook <key> --tab "<tab>" --range A1:N30 --out <png>`.
   c. GA4/GSC MCP render bảng/chart từ data (chỉ khi config có property/site).
   d. `.manual-slot` — đánh dấu chỗ Vincent/team dán tay.
   Mọi ảnh lưu `02-raw/screenshots/tools/YYYYMMDD_<slug>_w<nn>.png` + log op `capture` (protocol §8 root).
4. **Nhúng ảnh base64** vào deck (logo từ `weekly-template/assets/` + capture từ `02-raw/screenshots/`): deck phải là 1 file TỰ CHỨA — export server chỉ serve thư mục chứa deck nên relative path `../../` sẽ đứt; ảnh GỐC vẫn sống ở `02-raw/screenshots/` (protocol §8), deck chỉ nhúng bản render.
5. **KHÔNG export PDF** — bản final là file HTML tự chứa (luật HTML-only, Vincent siết 23/07/2026 — áp cả report định kỳ). PDF chỉ khi Vincent yêu cầu rõ trong phiên; khi đó dùng bản `scripts/export-pdf.sh` đóng gói sẵn trong skill với **cả 2 đường dẫn TUYỆT ĐỐI** (script `cd` vào temp dir, path tương đối sẽ lạc).

### Pha 4 — CHECK + FILE-BACK (bắt buộc trước khi báo xong)
1. Vòng tự kiểm trạm Reporter + Chế độ TUẦN (`09-reporting/CLAUDE.md`).
2. **Spot-check 5 số** ngẫu nhiên trên deck ↔ digest ↔ (1 call MCP đọc đúng ô nguồn nếu nghi ngờ). Lệch = DỪNG, sửa trước khi giao.
3. Update `index.md` bảng D (dòng deck + insights) + append `log.md` op `report` (kèm `capture`/`ingest` đã ghi ở pha trước).
4. Chế độ DRAFT (cron): dừng ở file + báo Vincent review — KHÔNG gửi đi đâu.

## Ranh giới & luật

- **Chỉ đọc** các workbook trong config. Không sửa bất kỳ ô nào trên Google Sheets (read-only).
- Slide OKRs / plan tháng: render bảng từ sheet nếu tab có data; Vincent chỉnh tay sau — deck để nguyên chỗ trống có đánh dấu, không bịa.
- 3rd-party (Ahrefs…) = minh họa xu hướng, ghi rõ nguồn — không phải số nghiệm thu.
- Số HĐ 🔒 không xuất hiện trong deck (deck là client-facing nhưng run-rate/KPI theo sheet vận hành là được phép — client cùng vận hành sheet đó).
- Runtime: cần Claude Code + máy có credentials (Lead/Vincent). Codex/Antigravity: chạy được pha FETCH/RENDER nếu có python+node, nhưng skill phân loại claude-only theo manifest — chạy ngoài Claude Code thì làm DRAFT tay theo template, ghi rõ.

## References (nạp đúng file khi cần — §10 root)

- `references/report-config-schema.md` — schema config + cách setup client mới.
- `references/slide-map.md` — LUẬT nội dung slide (thứ tự, luật trình bày, luật bảng) — nạp ở Pha 3 khi viết content.yaml.
- `references/content-schema.md` — schema `content.yaml` + data-ref syntax + checklist 6 bước mỗi tuần (nạp ở Pha 3).
- `references/analysis-rubric.md` — chuẩn NHẬN XÉT + lớp PATTERN (nạp ở Pha 2).
- `references/period-report-format.md` — khung 8 section + 4 luật riêng của deck kỳ THÁNG/QUÝ + back-port khi client sửa thẳng HTML (nạp ở Pha 0 và Pha 3 của nhịp kỳ).
- `references/scripts-map.md` — 15 script: dùng cái nào lúc nào, input/output, thứ tự chạy một kỳ (nạp khi chọn script hoặc bàn giao người mới).

## File vận hành trong instance (không thuộc skill, nhưng phải biết)

| File | Dùng khi |
|---|---|
| `09-reporting/RUNBOOK-bao-cao-ky.md` | Chạy lại báo cáo tháng/quý từ đầu — câu lệnh tuần tự + QA + file-back |
| `09-reporting/PERIOD-DATA-CHECKLIST.md` | Nhắc team chuẩn bị data kỳ (song sinh với `WEEKLY-DATA-CHECKLIST.md`) |
| `09-reporting/data-sources.yaml` | Registry link nguồn — **sinh tự động**, sửa ở `source_links:` trong config rồi chạy lại script |
