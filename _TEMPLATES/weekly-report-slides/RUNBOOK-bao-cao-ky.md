# RUNBOOK — chạy báo cáo kỳ THÁNG / QUÝ từ đầu tới cuối

> 📋 **Template client-neutral** — copy vào `09-reporting/RUNBOOK-bao-cao-ky.md` của instance rồi thay `<client-slug>` / `<CLIENT>` / kỳ ví dụ theo dự án. Hệ chỉ chạy được sau khi hoàn tất `WEEKLY-DATA-CHECKLIST.md` §5 (dựng workbook + điền ID vào `report-config.yaml`).
>
> Dành cho người vận hành (SEO Lead / Executive phụ trách data) chạy lại toàn bộ quy trình mà không cần đọc lịch sử chat. Câu lệnh chép nguyên văn, chạy từ **thư mục gốc instance** (`PROJECTS/<client-slug>/`).
>
> Luật vận hành ở `CLAUDE.md` root + `09-reporting/CLAUDE.md`. Spec nội dung deck ở `skills/gtv-weekly-report/references/period-report-format.md`. Bảng script ở `references/scripts-map.md`. Format workbook: file schema của instance (vd `<CLIENT>_workbook-schema_v1.md`). File này chỉ trả lời: **gõ gì, theo thứ tự nào, kiểm gì trước khi giao.**

---

## 0. Trước khi bắt đầu — 4 thứ phải có

| Cần | Kiểm bằng | Thiếu thì |
|---|---|---|
| Python + thư viện | `python3 -c "import yaml, googleapiclient, pptx, PIL"` | `pip3 install pyyaml google-api-python-client google-auth python-pptx pillow` |
| Credentials service account | `ls ~/.config/gcp/<key-cua-ban>.json` | Chạy `python3 _SETUP/setup_credential.py detect` |
| Workbook kỳ đã share cho service account | `python3 skills/gtv-weekly-report/scripts/build_source_links.py --config 09-reporting/report-config.yaml --out /dev/null --check` | Share Viewer cho `<robot-cua-ban>@<project>.iam.gserviceaccount.com` |
| Playwright (QA chống tràn) | `npx playwright --version` | `npm i playwright && npx playwright install chromium` |

Kỳ mới (vd `2026-08`, `2026-Q1`) phải được **khai trong khối `periods:`** của `report-config.yaml` trước — khai cột tường minh, không autodetect (lý do ghi ngay trong file config). Quý dự án tính theo T1 của hợp đồng, KHÔNG theo quý dương lịch — tra bảng A `index.md`.

---

## 1. Kéo số

```bash
python3 skills/gtv-weekly-report/scripts/fetch_period_data.py \
    --config 09-reporting/report-config.yaml --period 2026-08
```

Ra `02-raw/seo-data/monthly/2026-08/` (kỳ quý → `quarterly/2026-Q1/`): CSV thô + `digest.json` + `digest.md`.
Chạy lại cùng kỳ = ghi đè folder kỳ đó. Cần giữ bản cũ → đổi tên folder trước.

## 2. Phân tích URL-level

```bash
# mỗi nguồn khai trong periods.<kỳ>.sources — category · pdp · blog
python3 skills/gtv-weekly-report/scripts/period_analyze.py \
    --config 09-reporting/report-config.yaml --period 2026-08 --source pdp --save-csv
```

Ra `analysis_<source>.json` trong folder kỳ: top mover + rollup theo dimension + **độ phủ % so BẢNG 1**. Độ phủ là số phải in lên slide (chip scope) — mẫu con không được nói như toàn bộ.

Kỳ QUÝ, nhóm nào giảm sâu thì chạy thêm forensics (bắt URL đổi slug / biến mất / sụt sâu — hữu ích nhất cho site thương mại điện tử vòng đời sản phẩm ngắn; cơ chế generic theo `--source`, chạy được cho mọi nhóm trang):

```bash
python3 skills/gtv-weekly-report/scripts/url_yoy_forensics.py \
    --config 09-reporting/report-config.yaml --period 2026-Q1 --source pdp \
    --min-prev 1000 --drop-pct 50 --csv 02-raw/seo-data/quarterly/2026-Q1/forensics_pdp.csv
```

## 3. BA CỔNG KIỂM — chạy TRƯỚC khi viết chữ

```bash
python3 skills/gtv-weekly-report/scripts/bang1_parser.py \
    --config 09-reporting/report-config.yaml --period 2026-08
python3 skills/gtv-weekly-report/scripts/reconcile_totals.py \
    --config 09-reporting/report-config.yaml --period 2026-08
```

- `bang1_parser` báo ô công thức sai trên sheet → **báo team sửa sheet**, deck ghi số đúng và note lại ở slide phụ lục «đã sửa gì trong kỳ này».
- `reconcile_totals` báo các nguồn lệch bao nhiêu và vì sao → con số này đi thẳng vào slide phụ lục đối chiếu nguồn.
- Cổng thứ ba (validator của `build_deck.py`) chạy tự động ở bước 6.

Kỳ khép quý, chấm OKRs:

```bash
python3 skills/gtv-weekly-report/scripts/okrs_score.py \
    --config 09-reporting/report-config.yaml --period 2026-Q1 \
    --md 09-reporting/<CLIENT>_okrs-q1-cham-diem_<YYYY-MM-DD>.md
```

## 4. Viết insights (bước của người/AI, không phải script)

`09-reporting/analysis/<kỳ>-insights.md` theo `references/analysis-rubric.md`. Mỗi nhận xét: **số → so sánh → nguyên nhân khả dĩ → action + owner**. Dự án ADVISORY: action luôn ghi rõ owner GTV (cố vấn) hay in-house khách (thực thi). Đây là nguồn của mọi câu chữ trên deck — không viết nhận xét thẳng vào `content.yaml`.

## 5. Registry link nguồn (khi `source_links:` đổi)

```bash
python3 skills/gtv-weekly-report/scripts/build_source_links.py \
    --config 09-reporting/report-config.yaml --out 09-reporting/data-sources.yaml
```

In ra danh sách nguồn **chưa có link** — đây là danh sách đi hỏi client/team, và cũng là nội dung khối cuối slide phụ lục nguồn.

## 6. Dựng deck

```bash
python3 skills/gtv-weekly-report/scripts/build_deck.py \
    --content 09-reporting/quarterly/2026-Q1/content-t<n>-quy<N>-v1.yaml \
    --skeleton 09-reporting/weekly-template/deck-skeleton.html \
    --datadir  02-raw/seo-data/quarterly/2026-Q1 \
    --sources  09-reporting/data-sources.yaml \
    --out      09-reporting/quarterly/2026-Q1/<CLIENT>_bao-cao-T<n>-Quy<N>_v1.html
```

Build FAIL (exit≠0) khi còn `{{`, còn `{"t":`, còn `**` chưa render, còn `[[` chưa resolve, thiếu `data_meta`, số slide lệch YAML. **Sửa YAML rồi build lại — không sửa HTML tay.**

## 7. QA chống tràn (bắt buộc, mọi slide)

```bash
mkdir -p /tmp/deckqa && cd /tmp/deckqa && npm i playwright >/dev/null 2>&1
cat > overflow.js <<'JS'
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + process.argv[2]);
  await p.waitForTimeout(2500);
  const r = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('section.slide').forEach((s, i) => {
      const prev = s.style.display; s.style.display = 'block';
      if (s.scrollHeight > 1080 || s.scrollWidth > 1920)
        out.push({ n: i + 1, h: s.scrollHeight, w: s.scrollWidth });
      s.style.display = prev;
    });
    return { total: document.querySelectorAll('section.slide').length, over: out };
  });
  console.log(JSON.stringify(r, null, 1));
  await b.close();
})();
JS
node overflow.js "<đường dẫn TUYỆT ĐỐI tới deck.html>"
```

`over: []` mới được giao. Tràn thì **rút nội dung slide**, không thu nhỏ chữ xuống dưới ngưỡng đọc được ở máy chiếu.

## 8. Bản PowerPoint (chỉ khi client cần tự sửa)

```bash
python3 skills/gtv-weekly-report/scripts/build_pptx.py \
    --content 09-reporting/quarterly/2026-Q1/content-t<n>-quy<N>-v1.yaml \
    --out     09-reporting/quarterly/2026-Q1/<CLIENT>_bao-cao-T<n>-Quy<N>_v1.pptx \
    --base . --sources 09-reporting/data-sources.yaml
```

Mọi thứ trên slide là đối tượng PowerPoint thật (text box · bảng · chart native · hyperlink) nên sửa được. **KHÔNG export PDF** — luật HTML-only, PDF chỉ khi Vincent yêu cầu rõ trong phiên.

## 9. Spot-check số (không bỏ được)

Chọn ngẫu nhiên **5 con số** trên deck → mở đúng tab nguồn bằng link ở slide phụ lục nguồn → so nguyên văn. Lệch một số = dừng, truy nguồn, sửa rồi mới giao.

## 10. File-back (chưa làm là chưa xong)

| Việc | Ở đâu |
|---|---|
| Dòng deliverable mới (deck · yaml · pptx · insights) | `index.md` bảng D |
| Trạng thái công đoạn liên quan | `index.md` bảng B |
| Timeline | `log.md` — op `report` (kèm `ingest` nếu có snapshot data mới) |
| Insights kỳ | `09-reporting/analysis/<kỳ>-insights.md` |
| Đổi infra (script/skeleton/schema) | `MIGRATION.md` + `log.md` op `refactor` |

---

## 11. Client sửa thẳng trên file HTML → back-port trước, đừng build đè

1. Diff bản client sửa với bản build gần nhất (bỏ base64 ảnh) → danh sách hunk.
2. Đổi từng hunk về mini-markup rồi áp vào YAML, tăng version YAML.
3. Build lại → **diff với bản client sửa phải bằng 0** ở phần chữ.
4. Xong bước 3 mới thêm nội dung mới.

Bỏ bước này = mất chỉnh sửa của client. Chi tiết: `skills/gtv-weekly-report/references/period-report-format.md` §7.

## 12. Sự cố hay gặp

| Hiện tượng | Nguyên nhân thật | Xử |
|---|---|---|
| `tab «X» không tồn tại` | Tên tab có **space thừa ở cuối** hoặc dấu chấm cuối | Chép nguyên văn tên tab từ sheet vào config (script tự thử bản `.strip()`) |
| Danh sách tăng/giảm **ngược hoàn toàn** | Tab kỳ quý để cột năm trước TRƯỚC cột năm nay | Khai `cur_col`/`prev_col` tường minh trong `periods:` — không autodetect |
| Bảng có ô hiện `{"t":…}` | Cell dict viết dạng chuỗi mà renderer chưa parse | Đã có gate build FAIL; nếu tái diễn thì báo — đừng sửa HTML tay |
| Deck nặng bất thường | Ảnh gốc quá lớn nhúng base64 | Giảm kích thước ảnh nguồn trước khi nhúng |
| Số YoY lệch khó hiểu | Định nghĩa event/metric đổi giữa hai năm, hoặc dòng «cùng kỳ» trên sheet lệch tháng | Xem luật nền so sánh: `period-report-format.md` §3.3 |
| PDP "rớt traffic" hàng loạt | URL đổi slug / hết hàng / 404 — không phải rớt hạng | Đối chiếu tab `Ghi chú URL` + cột Trạng thái URL; chạy forensics bước 2 |
