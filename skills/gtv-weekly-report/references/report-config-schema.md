# report-config.yaml — schema (per client, đặt tại `09-reporting/report-config.yaml`)

Mẫu sống đầy đủ: instance CareerViet. Mọi field bắt buộc trừ khi ghi (optional).

```yaml
client: <slug>                 # trùng slug instance
client_name: <Tên hiển thị>
domain: <domain client>

credentials: ~/.config/gcp/<service-account>.json   # env GOOGLE_APPLICATION_CREDENTIALS ghi đè

week_anchor: "YYYY-MM-DD"      # NGÀY ĐẦU của W1 (đúng thứ trong tuần mà chu kỳ dùng)
project_start: "YYYY-MM-DD"
project_end: "YYYY-MM-DD"
gsc_lag_days: 2                # cửa sổ GSC lệch bao nhiêu ngày so với GA4

ga4_property_id: ""            # (optional) bật module GA4-direct khi có quyền
gsc_site: ""                   # (optional) bật module GSC-direct khi có quyền

looker:                        # (optional) dashboard link-view để CHỤP
  url: "https://datastudio.google.com/reporting/<id>"
  pages: [<tên page — tài liệu tham chiếu cho người>]

spreadsheets:                  # workbook CỐ ĐỊNH (id không đổi theo tuần)
  <workbook_key>:
    id: "<spreadsheetId>"
    ranges:
      <range_key>: "'<Tên tab>'!A1:N70"
  # range_key có ý nghĩa với fetch script:
  #   runrate_tuan      → parse summary KPI + dòng W(N-5)..W(N+1)
  #   report_tuan_tasks → đếm Status + gom dòng trễ (slide SOW)
  #   còn lại           → lưu nguyên bảng nhỏ vào digest (cắt 40-45 dòng đầu)

report_tuan:                   # workbook thay đổi THEO TUẦN
  name_pattern: "Report Tuần {week}"   # tên để Drive search
  known_ids: {"11": "<id>"}            # cache id đã biết (append dần)
  ranges:
    overview_wow: "'<tab bảng 1>'!A1:N45"   # → parse bang1_overview_wow
    gsc_jlp: "'<tab GSC>'!A1:K260"          # gsc_* → tính top movers theo ΔClicks
    gsc_blog: "'<tab GSC blog>'!A1:K160"

top_movers:
  min_clicks: 30               # "top page" = max(clicks 2 kỳ) ≥ ngưỡng — đúng yêu cầu 80/20
  top_n: 10

kpi_targets:                   # mục tiêu NĂM theo sheet vận hành client-agreed
  pageview_year: <int>
  apply_year: <int>

page_groups:                   # nhóm trang + cờ thuộc cụm KPI (render kpi-row trong deck)
  - {name: "<nhóm>", kpi: true|false}

output:
  weekly_dir: "09-reporting/weekly"
  analysis_dir: "09-reporting/analysis"
  deck_name: "<CLIENT>_bao-cao-tuan-W{week}_v{ver}"
  template: "09-reporting/weekly-template/deck-template.html"
```

## Setup client mới (1 lần)

1. Copy `_TEMPLATES/weekly-report-slides/` → `09-reporting/weekly-template/`; thay `assets/logo-client.png` + `logo-gtv.png`; điền tên client/đối thủ trong exemplar.
2. Tạo `report-config.yaml` theo schema; lấy spreadsheetId từ URL các workbook team đang vận hành.
3. Share các workbook (kể cả workbook "Report Tuần" mỗi tuần) cho service account — email trong file credentials.
4. Chạy `fetch_weekly_data.py --dry-run` xem tuần resolve đúng chưa → chạy thật 1 tuần cũ có ground truth để đối chiếu.
5. Ghi log op `setup`.

## Lưu ý quota & bảo mật

- Sheets API: 60 read/phút/user — fetch script luôn batchGet (1 call/workbook). KHÔNG gọi lẻ range qua MCP khi số range >3.
- Config chứa ID workbook nội bộ dự án — sống trong instance (repo private per client), không copy sang master.
- Master chỉ giữ SCHEMA này (client-neutral).
