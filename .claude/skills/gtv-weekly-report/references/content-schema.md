# content-schema.md — Schema `content.yaml` cho `scripts/build_deck.py` (nạp ở Pha 3 RENDER)

> Từ W12, deck tuần được RÁP TỰ ĐỘNG: AI chỉ viết **nhận xét/action** trong 1 file `content.yaml` nhỏ,
> `build_deck.py` ráp toàn bộ HTML (bảng số từ data-ref, class pos/neg/mut, brandbar, page-no, data-meta).
> Exemplar đầy đủ 28 slide: `PROJECTS/careerviet/09-reporting/weekly/2026-W11/content-w11.yaml`.

## Lệnh build

```bash
python3 skills/gtv-weekly-report/scripts/build_deck.py \
  --content 09-reporting/weekly/<YYYY>-W<NN>/content-w<nn>.yaml \
  --skeleton 09-reporting/weekly-template/deck-skeleton.html \
  --datadir  02-raw/seo-data/weekly/<YYYY>-W<NN> \
  --out      09-reporting/weekly/<YYYY>-W<NN>/<CLIENT>_bao-cao-tuan-W<NN>_v1.html
```

- Logo: skeleton nhúng 1 lần qua `var LOGOS = {client, gtv}` (deck nhẹ ~200KB thay vì ~2.6MB).
  Nếu skeleton còn placeholder `{{LOGO_*_B64}}`, script tự lấy PNG trong `assets/` cạnh skeleton
  (`logo-client.png` / `logo-careerviet.png` / `logo-gtv.png`) hoặc nhận `--logo-client/--logo-gtv`.
- Script exit non-zero khi FAIL: thiếu `data_meta` ở slide data, data-ref không resolve được,
  còn `{{`, số section ≠ số slide.

## Khung file

```yaml
meta:
  client: CareerViet          # alt text logo client
  title: "GTV x CareerViet — SEO Report Weekly — Tuần 12 (…) v1"
  edit_key: crv-w12-v1        # key localStorage riêng từng deck (luật edit-mode)
  week_label: W12             # dòng hl trong bảng run-rate
slides:
  - type: cover
    ...
```

## Field chung cho slide nội dung

| Field | Bắt buộc | Ghi chú |
|---|---|---|
| `type` | ✔ | xem bảng type dưới |
| `crumb` | nên có | breadcrumb «Organic PV › Job Listing › 1.2 Ngành nghề» (luật #2) |
| `pill` | nên có | chữ trong pill gradient |
| `idx` + `sub` | tùy | `idx: "1.1"` render `<span class="idx">` trước `sub` |
| `data_meta` | **BẮT BUỘC** với mọi slide data | nguồn + kỳ dữ liệu đúng header bảng nguồn (luật bảng #4). Thiếu → build FAIL |
| `content_style` | tùy | style thô cho `.content` (vd `gap:8px;justify-content:flex-start;padding-top:0;`) |

Slide KHÔNG cần `data_meta`: `cover, agenda, qna, thanks, support, manual`.

## Mini-markup trong text (bullets, action, note, sub)

| Viết | Render |
|---|---|
| `**đậm**` | `<b>` |
| `{pos}+9,003{/pos}` | `<span class="up">` (xanh) |
| `{neg}−54,000{/neg}` | `<span class="down">` (đỏ) |
| `{flat}0{/flat}` | `<span class="flat">` (xám) |
| `{i}…{/i}` hoặc `<i>…</i>` | in nghiêng — HTML thô được pass-through |

## Các type slide

### `cover` / `agenda` / `qna` / `thanks` — static
```yaml
- type: cover
  title: GTV x CAREERVIET
  outline: SEO Report (Weekly)
  week_line: "Tuần 12 · 16/07 – 22/07/2026"
  domain: https://careerviet.vn/
- type: agenda
  items: [1. OVERVIEW KPI, 2. WEEKLY & MONTHLY RUN RATE, "3. SOW: STATUS UPDATE", 4. ACTION ITEMS / NEXT WEEK PLAN]
- type: qna        # big/title có default
- type: thanks     # word/foot có default
```

### `runrate` — thẻ rr-cards + bảng run-rate từ digest
```yaml
- type: runrate
  data: digest:runrate_tuan     # default — summary → 2 thẻ, weeks → bảng
  month_label: T7               # chữ tháng trong nhãn thẻ
  weeks_limit: 8                # optional, mặc định 8 dòng cuối có số thực tế
  bullets: [ ... ]              # optional
```
Dòng tuần = `meta.week_label` tự có class `hl` + in đậm 3 ô. %HT/run-rate ≥100% → `pos`, <100% → `neg`.

### `table_side` — bảng trái + NHẬN XÉT phải
```yaml
- type: table_side
  table: {class, style, wrap_style, headers, col_kinds, rows}   # bảng literal (xem «Bảng literal»)
  # HOẶC data: apply_groups  (+ kpi_rows: [...], name_map: {...}, total_label: ...)
  left_note: "..."              # optional — box .action nhỏ dưới bảng (vd slide Apply intent)
  right:
    title: NHẬN XÉT
    ul_style: "font-size:24px;"
    bullets: [ ... ]
    action: {label, items}      # optional — action box TRONG cột phải
  action: {label, items}        # optional — action box full-width dưới cùng
```

### `table_full` — bảng full-width + scope-note vàng + bullets/split dưới bảng
```yaml
- type: table_full
  scope_note: "⚠ …"             # optional, kèm scope_note_style
  table: { ... }                # literal
  below:                        # optional
    split: {left: {title, title_style, ul_style, bullets}, right: {...}}
    # hoặc bullets: [...] + ul_style
  action: {label, items}        # optional
```

### `nhanxet_2col` / `diagnose` — slide chữ 2 cột (hoặc 1 cột)
```yaml
- type: nhanxet_2col            # diagnose là alias (dùng cho slide chẩn đoán)
  single: true                  # optional — 1 cột full-width (vd 2.1 nhận xét)
  left:  {title: CHIỀU GIẢM, ul_style: "font-size:25px;line-height:1.55;", bullets: [...]}
  right: {title: CHIỀU TĂNG, ul_style: "...;margin-top:52px;", bullets: [...]}
  action: {label: "Việc cần làm:", items: [...]}
```
Bullet có thể là dict `{text, style}` (vd `style: "margin-top:18px;"` giãn ý thứ 2).

### `movers` — bảng top URL từ movers_pv_*.json
```yaml
- type: movers
  data: movers:jl:losers:1-10   # xem «Data-ref»
  columns: jl                   # preset jl: URL·Intent·PV·ΔPV·%·Clicks·ΔClicks·Pos·ΔPos*
                                # preset blog: slug·chủ đề·PV·ΔPV·%·Pos
  scope_note: "⚠ Một số URL thiếu dữ liệu GSC…"
  url_marks: {"/viec-lam/sale-online-k-vi.html": " ↩︎"}   # đánh dấu URL nghi swap
  pattern: {label: "Đọc pattern:", intro: "...", items: ["(1) …", "(2) …"]}
  action:  {label: "Việc cần làm:", items: ["…— **Người làm: X.**"]}
  # HOẶC split: {left: {bullets}, right: {bullets}}  — thay cho pattern/action (vd 3.1b)
```
Ô thiếu GSC (clicks/pos vắng hoặc pos=0) hiển thị «—». ΔClicks/ΔPos script tự tính
(ΔPos = pos_prev − pos, dương = lên hạng theo quy ước sheet). Pattern + action luôn nằm
chung 1 box, mỗi ý 1 `<li>` (luật #13); action không có ①②③ sẵn thì script tự đánh.

### `blog_groups` — bảng 10 cột từ blog_groups.json
```yaml
- type: blog_groups
  include:                      # "seo_flag|group" — thứ tự = thứ tự dòng; grand_total LUÔN tự thêm
    - "non-SEO|Lifestyle: STT / Quotes / Caption"
    - "SEO|Lương / Thuế / BHXH"
  total_label: "Grand Total (Blog) — trong đó SEO: …"
  bullets: [ ... ]              # + bullets_style
  action: { ... }               # optional
```

### `sow` — chips đếm + bảng task
```yaml
- type: sow
  sub: "Tuần 3/7 (20/07 – 26/07) — đủ N task theo sheet"
  rows:                         # literal (tên task đã làm sạch cho client-facing)
    - {task: "…", status: Done}          # Done / Đang làm / Trễ hạn / Tạm ngưng / "" (→ «—»)
  # HOẶC data: "digest:sow:Tuần 2/7 - ( 13/7 - 19/7 )"  (tên task NGUYÊN VĂN sheet — thường xấu, ưu tiên rows)
  # chips tự đếm từ status; muốn ghi đè: chips: [{n, cls: done|doing|notyet|late|paused, label}]
```

### `next_week` — khung dashed (hoặc bảng nếu có rows như sow)
```yaml
- type: next_week
  text: "Sheet chưa có section «Tuần N» — team điền trước họp…"
  # hoặc rows: [...] như sow
```

### `support` — bảng SCOPE/Description điền tay trong họp
```yaml
- type: support
  rows: [Technical, Technical Advance, UX/UI, Phối hợp triển khai Content, Số lượng Job detail]
  note: "Điền trực tiếp trong buổi họp — …"
```

### `manual` — escape hatch (hạn chế dùng)
```yaml
- type: manual
  html: |
    <section class="slide"> … markup thô đúng CSS deck … </section>
```
Dùng khi builder chưa cover loại slide → sau đó ghi feedback nâng builder.

## Bảng literal (`table:` trong table_side / table_full)

```yaml
table:
  class: data compact           # data | data compact | data compact dense
  style: "font-size:17px;"      # optional
  wrap_style: "padding:6px 10px;"
  headers: ["Nhóm", "Số URL", "PV tuần này", "PV tuần trước", "Δ PV", "%"]
  col_kinds: [name, ctr, num, num, delta, delta]
  rows:
    - ["Job Listing", "Có", "537,447", "528,444", "+9,003", "+1.70%"]        # list trần
    - {class: kpi-row, cells: [...]}                                          # dòng cụm KPI
    - {class: total,   cells: [...]}                                          # dòng tổng
    - {divider: "▲ CÁC KHU VỰC TĂNG…", class: divider}                        # dòng chia TĂNG/GIẢM
```

- `col_kinds`: `name` (trái, đậm) · `ctr` (giữa) · `num` (phải) · `delta` (tự class theo dấu:
  dương `pos`, âm `neg`, 0/rỗng `mut`).
- Ghi đè class 1 ô: hậu tố `|cls` — vd `"-0.1|mut"` (biến động nhỏ muốn để xám thay vì đỏ).
- Giá trị NGUYÊN VĂN từ nguồn — không tự làm tròn, không bịa số.

## Data-ref syntax (resolve từ `--datadir`)

| Ref | Nguồn | Trả về |
|---|---|---|
| `digest:runrate_tuan` | digest.json `sections.runrate_tuan` | summary + weeks cho type runrate |
| `digest:<section>` | digest.json section bất kỳ | raw (chỉ dùng cho renderer hỗ trợ) |
| `digest:sow:<week key>` | digest sow_status.weeks | rows cho type sow (tên task nguyên văn) |
| `movers:jl:losers:1-10` | movers_pv_jl.json | 10 dòng giảm đầu (1-based, inclusive) |
| `movers:blog:gainers:*` | movers_pv_blog.json | toàn bộ chiều tăng |
| `apply_groups` | apply_groups.json | groups + grand_total cho table_side |
| `blog_groups` | blog_groups.json | dùng qua type blog_groups + `include` |

## Luật cứng

1. **Số từ data-ref**, không nhét số bịa. Bảng chỉ dùng `rows:` literal khi digest không có
   section máy-đọc-được (bảng 1.1/1.2/1.3, JD, Apply intent…) — khi đó chép NGUYÊN VĂN từ digest/sheet.
2. `data_meta` bắt buộc mọi slide data — build FAIL nếu thiếu.
3. `action.items` là LIST — mỗi ý 1 dòng, script tự bọc ①②③ nếu chưa có (luật #13).
4. Nhận xét theo luật slide-map #3/#7/#8 (3 tăng/3 giảm, ngôn ngữ senior-SEO, đủ 2 chiều).
5. Slide chữ dài → tách slide (luật #6/#14), đừng nén font dưới ~21px.
6. Đổi tuần → đổi `meta.edit_key` để không đè bản sửa localStorage của deck cũ.

## Checklist AI mỗi tuần (6 bước)

1. **FETCH**: `fetch_weekly_data.py` → weekdir; chạy thêm `pv_movers.py` (jl + blog),
   `apply_groups.py`, `blog_groups.py` trên weekdir (Pha 1 SKILL.md).
2. **ANALYZE**: đọc digest + insights cũ → viết `analysis/<YYYY>-W<NN>-insights.md` (Pha 2).
3. **VIẾT content.yaml**: copy `content-w<nn-1>.yaml` tuần trước làm khung, cập nhật data-ref slice,
   bảng literal mới, và CHỈ viết lại nhận xét/action theo insights. KHÔNG viết HTML.
4. **BUILD**: chạy build_deck.py (lệnh trên) — sửa yaml đến khi `BUILD OK` + validate PASS.
5. **EXPORT PDF**: `bash <workspace>/skills/frontend-slides/scripts/export-pdf.sh <deck.html> <deck.pdf>`
   (2 đường dẫn TUYỆT ĐỐI).
6. **SOI PNG spot-check**: `swift scripts/pdf2png.swift <pdf> <outdir> 1.0` → Read tối thiểu các trang
   bảng dày + trang chữ dài: không chữ đè `.data-meta`, số khớp digest (spot-check 5 số), đủ N slide.
