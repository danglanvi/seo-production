---
name: seo-drift-tracker
description: "Chụp và so 9 thành phần SEO của từng URL sau deploy (title, meta, canonical, robots, H1, hreflang, schema, status, link nội bộ); Jev phân loại diff chữ đáng kể hay vô hại. Dùng khi chụp baseline SEO, so sánh sau deploy, hỏi element đổi từ bao giờ."
metadata:
  version: "1.1.1"
---

# SEO Drift Tracker

"Git cho SEO" — theo dõi **regression element-level** giữa 2 thời điểm trên bộ URL SEO cam kết. Không đánh giá element tốt hay xấu (việc của seo-onpage); chỉ trả lời một câu: **"so với baseline đã chốt, cái gì ĐỔI?"** — vì thay đổi không chủ đích sau deploy là lỗi phát hiện càng muộn càng đắt ([[Historical Data]]: signal xấu ghi đè cần thời gian gỡ).

**Vị trí trong quy trình:** baseline bắt buộc ngay sau khi chốt onpage **T4**; compare sau MỖI đợt coder khách sửa web (T2 cấu trúc, T4 audit Q2, T7 full audit) + hằng tháng giai đoạn duy trì. **Downstream:** bảng diff giao Account/dev truy vết; fix cụ thể route theo phân vai.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Performance decay — traffic/rank rớt theo thời gian | `content-refresh` | Skill này so ELEMENT, không so traffic; drift CRITICAL có thể là *nguyên nhân* → khi tìm ra element đổi, gợi ý content-refresh check hệ quả traffic |
| Sự kiện migration (đổi domain/URL/CMS có kế hoạch) | `site-migration-checklist` | Migration = thay đổi CHỦ ĐÍCH có checklist riêng; skill này bắt thay đổi KHÔNG chủ đích giữa 2 nhịp thường. Trước migration → chụp baseline bằng skill này làm input benchmark |
| Chấm chất lượng element (title dài/ngắn, H1 đúng intent…) | `seo-onpage` (OP1-OP55) | Skill này báo "title đổi từ A → B", KHÔNG chấm A hay B tốt hơn |
| Audit technical site tổng | `technical-seo-audit` | Status 200→4xx/5xx hàng loạt trong compare → escalate technical-seo-audit, không tự mở rộng |
| Sinh/sửa schema markup | `schema-markup-generator` | Skill này chỉ so *danh sách schema types hiện diện* (@type), không validate/viết JSON-LD |

## Input

**Required:**
- `$MODE` — `baseline` / `compare` / `history`.
- `$URL_LIST` — bộ URL theo dõi. Ưu tiên **bộ URL SEO cam kết** (workbook client) + homepage + template đại diện mỗi page type (1 category, 1 product, 1 bài). File `.txt`/`.csv` hoặc user paste. `compare`/`history` không cần nếu đã có trong baseline store.

**Optional:**
- `$CLIENT` — tên client → xác định store path trong SEO Production instance.
- `$LABEL` — nhãn snapshot (vd `post-T4-onpage`, `pre-deploy-2026-07`, `monthly-07`).
- `$BASELINE_ID` — compare với snapshot cụ thể (default: baseline mới nhất có label `baseline`).

**Elements chụp per URL (cố định — thêm/bớt phải ghi vào Changelog):**

| # | Element | Cách lấy |
|---|---|---|
| 1 | HTTP status (+ final URL sau redirect) | `curl -sI` / requests |
| 2 | `<title>` | raw HTML |
| 3 | meta description | raw HTML |
| 4 | canonical (`<link rel=canonical>` href) | raw HTML |
| 5 | meta robots (+ X-Robots-Tag header) | raw HTML + header |
| 6 | H1 (text, đếm số lượng) | raw HTML |
| 7 | hreflang set (cặp lang→href, sorted) | raw HTML |
| 8 | schema types hiện diện (danh sách @type trong JSON-LD, sorted unique) | raw HTML |
| 9 | số internal links out (link `<a href>` cùng host trong HTML) | raw HTML, đếm |

⚠️ Chụp từ **raw HTML** (curl/requests, UA thường) — nhất quán mọi snapshot. Site JS-heavy render lệch raw → ghi chú 1 lần trong store metadata; đổi phương pháp fetch giữa chừng = phá tính so sánh được.

**Storage ladder (khai báo TIER trong report):**

| Tier | Điều kiện | Store |
|---|---|---|
| **A — SQLite** | Chạy được Python | `scripts/drift_tracker.py` (viết 1 lần vào skill folder, tái dùng) → `05-tracking/drift/<client>.sqlite`: bảng `snapshots(id, ts, label)` + `elements(snapshot_id, url, element, value)` — history đầy đủ, diff bằng SQL |
| **B — CSV** | Không SQLite nhưng có shell | Mỗi snapshot 1 file `05-tracking/drift/<client>/<ts>_<label>.csv` (url, element, value) — diff bằng script so 2 file; history = so nhiều file |
| **C — Markdown** | Không chạy được script | Bảng markdown baseline trong repo client (`05-tracking/drift/<client>-baseline.md`), URL × 9 elements; compare = fetch tay từng URL + so mắt với bảng — chỉ khả thi ≤ ~20 URL, ghi rõ giới hạn |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code | Chuẩn hoá chữ (NFC, khoảng trắng, hoa thường, dấu câu, dấu phân cách số), bắt số đổi và rỗng ↔ có chữ, xếp severity | dùng. Hiệu chuẩn 19/10: 51/118 diff do code chốt, kiểm tay đúng 51/51 |
| Jev | Rubric `diff-impact` 2026-10-19.1, câu `significant`: diff chữ của title, meta, H1, khối chữ đổi nghĩa hay không | dùng cho nhãn "đáng kể": p ≥ 0,65 đúng 46/47 (phủ 70% ca gửi Jev). Không tin nhãn "vô hại" của Jev: p ≤ 0,3 chỉ đúng 7/8, nên ca đó Claude đọc |
| EmbeddingGemma 2 | Cosine chữ cũ ↔ chữ mới | không dùng: `content-quality-lab` đo AUC 0,74 với mất fact, không đủ để quyết; title và meta quá ngắn |
| GLM Flash | Trích câu | không dùng: diff đã là cặp câu ngắn |
| Claude | Gán gold, đọc ca "Claude đọc", điền cột Chủ đích? cùng Account | dùng |

Jev chỉ nhận chữ công khai của trang (URL, element, chữ cũ, chữ mới). Nhãn Jev nói mức đổi nghĩa, không nói chủ đích.

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,curl?,jev?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0b — Đọc references + xác định tier & scope

1. Xác định `$CLIENT` → store path trong SEO Production instance (`05-tracking/drift/`; instance không có folder → tạo). Kiểm tra store đã tồn tại chưa: `compare`/`history` mà CHƯA có baseline → dừng, báo user chạy `baseline` trước — không có gì để so, không bịa baseline.
2. Xác định storage tier (A/B/C) theo môi trường. Đọc bảng severity dưới trước khi diff.
3. `baseline`: xác nhận `$URL_LIST` = bộ URL cam kết + đại diện template. >200 URL → báo thời gian fetch ước tính + đề xuất rate limit (1-2 req/s — bài học shared hosting VN chặn crawler nhanh, technical-seo-audit v1.2) → **chờ user xác nhận** rồi mới fetch.
4. Snapshot nào cũng gắn `$LABEL` + timestamp — snapshot không nhãn sau 3 tháng không ai hiểu chụp lúc nào, vì sao.

### Bước 1 — Fetch & snapshot

1. Fetch từng URL trong `$URL_LIST` (rate limit lịch sự), extract 9 elements theo bảng Input.
2. Fetch lỗi (timeout, 5xx thoáng qua) → retry 1 lần; vẫn lỗi → ghi element = `FETCH_ERROR`, KHÔNG ghi giá trị rỗng (rỗng sẽ diff giả thành "element bị xóa" ở lần compare).
3. Ghi vào store theo tier + in tóm tắt: n URL chụp OK / n lỗi / label / snapshot id.

### Bước 2 — Compare (chỉ `$MODE = compare`)

1. Chụp snapshot hiện tại (Bước 1) → diff với `$BASELINE_ID` per (url, element).
2. Phân loại mỗi thay đổi theo **bảng severity**:

| Severity | Element đổi | Vì sao |
|---|---|---|
| 🔴 **CRITICAL** | canonical đổi/mất · meta robots thêm noindex/nofollow · HTTP status đổi (200→3xx/4xx/5xx) | Đụng thẳng index/signal — canonical sai trỏ signal đi chỗ khác ([[Ranking Signal Consolidation]]); noindex lọt production = trang rời index |
| 🟠 **HIGH** | title đổi · H1 đổi (text hoặc số lượng) · hreflang set đổi/mất · schema type mất | Đụng relevance signal chính ([[Meta Tags]]) + hreflang mất phá return tags cả cụm ngôn ngữ ([[Hreflang PageRank Sharing]]) |
| 🟡 **MEDIUM** | meta description đổi · schema type thêm mới · internal links out lệch >20% | Ảnh hưởng CTR/hiểu trang nhưng không chặn index |
| ⚪ **INFO** | internal links out lệch ≤20% · URL mới thêm vào list | Ghi nhận, thường không cần action |

3. 🔴 **Không suy diễn chủ đích**: skill không biết thay đổi là cố ý hay tai nạn — bảng diff luôn có cột "Chủ đích? (Account xác nhận với khách)". Thay đổi cố ý được xác nhận → user quyết định **promote thành baseline mới** (chạy lại `baseline` với label mới), không sửa tay baseline cũ.
4. FETCH_ERROR ở 1 trong 2 phía → hàng riêng "không so được", không tính là thay đổi.
5. Phân loại mức đổi nghĩa của diff chữ (title, meta description, H1):
   - Lấy diff: tier A chạy `python3 -B skills/seo-drift-tracker/scripts/diff_classify.py from-drift --json <compare.json> --out <W>/diffs.jsonl` trên output `--json compare`. Tier B chạy lệnh `diffs --old <A.jsonl> --new <B.jsonl>` trên 2 snapshot `{url, title, meta, h1}`.
   - Chạy `prepare --diffs <W>/diffs.jsonl --out-dir <W>`. Code chốt ca rõ; phần còn lại vào `<W>/jev_in.jsonl`.
   - Chạy `python3 -B -I tools/ai-assist/jev.py --task skills/seo-drift-tracker/tasks/diff-impact.json --in <W>/jev_in.jsonl --out <W>/jev_out.jsonl --budget 0.05`. 67 diff tốn 0,0016 USD.
   - Chạy `report --diffs <W>/diffs.jsonl --jev-out <W>/jev_out.jsonl --registry 00-client-context/model-calibration.json --site <domain> --out-dir <W>`.
   - Site mới hoặc rubric đổi version: gán gold mù ≥ 40 diff trước lượt Jev đầu, rồi hiệu chuẩn bằng skill `model-calibration`: `calibrate.py jev --question significant --positive yes`. Chưa có ngưỡng thì Claude đọc mọi ca Jev.
   - Ghi nhãn vào cột "Mức đổi nghĩa" của bảng diff. Nhãn không đổi severity và không thay cột Chủ đích?.

### Bước 3 — History (chỉ `$MODE = history`)

Liệt kê chuỗi giá trị của 1 URL (hoặc 1 element across URLs) qua các snapshot: ts, label, giá trị — trả lời "canonical trang X đổi từ bao giờ, giữa 2 deploy nào". Tier C: giới hạn = so các file baseline markdown đã lưu.

### Bước 4 — Report

- `baseline`: xác nhận store + n URL + label; nhắc nhịp compare kế tiếp (sau deploy gần nhất / đầu tháng sau).
- `compare`: render skeleton Output → `03-audits/<client>_Drift-Report_<YYYY-MM-DD>.md`. Mỗi finding CRITICAL/HIGH kèm **Falsifiability** (xem Gates).
- Có ≥1 CRITICAL → mở đầu report bằng khối cảnh báo + khuyến nghị báo dev trong ngày (cửa sổ sửa trước khi Googlebot re-crawl + ghi đè signal là hữu hạn).

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Hai snapshot dùng cùng cách trích: H1 cùng dạng (chuỗi hoặc danh sách), cùng phương pháp fetch. Nguồn lỗi: 19/10 so snapshot 17/10 (H1 dạng danh sách) với store 19/10 (H1 dạng chuỗi) ra 327 diff H1 giả.
- [ ] Diff chỉ khác NBSP, khoảng trắng hay hoa thường nằm ở nhóm "vô hại", không nằm trong bảng HIGH. Nguồn lỗi: 19/10 title một case study và meta một bài blog chỉ khác NBSP.
- [ ] Nhãn "vô hại" chỉ do code chốt; ca Jev dưới ngưỡng đã có kết luận của Claude. Nguồn lỗi: hiệu chuẩn 19/10, Jev cho p 0,29 với "Dẫn đầu → Tiên phong", một lần đổi claim.
- [ ] Đổi tên entity được ghi "đáng kể" dù tên cũ còn trong ngoặc. Nguồn lỗi: "Google Data Studio → Looker Studio (Google Data Studio)" và "Google My Business → Google Business Profile", Jev p 0,31–0,50.
- [ ] Mỗi diff "đáng kể" có cột Chủ đích? và không bị gọi là regression trước khi Account xác nhận. Nguồn lỗi: các vòng sửa 15–19/10 có 96 diff "đáng kể", phần lớn là sửa chủ đích (bỏ "hàng đầu", thêm GEO).
- [ ] Diff đọc trên chữ hiển thị của trang, không đọc biến template trong DB. Nguồn lỗi: 19/10 diff `%title% %sep% %sitename%` của một trang chuyên mục.

## Output

```markdown
# Drift Report — <client/domain>
> Baseline: <label, ts> → Current: <ts> · DATA TIER: <A/B/C> · URLs: <n> so sánh / <m> FETCH_ERROR
> Deploy event liên quan (user khai): <mô tả hoặc "không rõ">

## 1. Verdict
- 🔴 CRITICAL: <n> · 🟠 HIGH: <n> · 🟡 MEDIUM: <n> · ⚪ INFO: <n>
- <1-2 câu: có cần báo dev ngay không>

## 2. Thay đổi CRITICAL
| URL | Element | Baseline | Hiện tại | Mức đổi nghĩa (code/Jev/Claude) | Chủ đích? | Action | Falsifiability + leading indicator |

## 3. Thay đổi HIGH / 4. MEDIUM (+ INFO gộp cuối)
| URL | Element | Baseline | Hiện tại | Mức đổi nghĩa (code/Jev/Claude) | Chủ đích? | Action |

## 5. Không so được
| URL | Lý do (FETCH_ERROR phía nào) |

## 6. Next
- Xác nhận chủ đích với khách → promote baseline mới nếu cố ý
- Nhịp compare kế tiếp: <ngày/sự kiện>
```

## Behavior Gates

**#1 Data tier declare** — Report ghi rõ tier storage (A/B/C) + phương pháp fetch (raw HTML) + n URL lỗi. Tier C ghi giới hạn coverage.

**#2 No hard-fail** — Không Python → CSV; không script → bảng markdown baseline. Skill luôn chạy được; chỉ thu hẹp năng lực history.

**#3 Baseline là sự thật bất biến** — Không sửa tay baseline cũ, không "tiện thể" cập nhật giá trị. Thay đổi cố ý → promote snapshot mới có label. Compare không có baseline → dừng + yêu cầu chạy baseline, không bịa.

**#4 Diff, không phán xét** — Skill báo THAY ĐỔI, không chấm chất lượng (→ seo-onpage) và không kết luận chủ đích — cột "Chủ đích?" luôn để Account/khách xác nhận.

**#5 Falsifiability** — Finding CRITICAL/HIGH kèm: "làm sao biết nếu cảnh báo này sai?" (vd canonical đổi có thể là consolidation chủ đích hợp lệ — nếu khách xác nhận có kế hoạch gộp trang thì đây không phải regression) + leading indicator (GSC URL Inspection / impressions URL đó 2-4 tuần sau).

## Anti-patterns

- ❌ So sánh 2 snapshot fetch bằng 2 phương pháp khác nhau (raw vs rendered, UA khác) — diff giả hàng loạt.
- ❌ Ghi giá trị rỗng cho URL fetch lỗi — lần sau diff thành "element bị xóa".
- ❌ Tự ý sửa baseline cho "khớp hiện tại" — mất toàn bộ giá trị truy vết.
- ❌ Kết luận "coder làm hỏng" khi chưa có cột Chủ đích? xác nhận — thay đổi có thể là task SEO chính mình yêu cầu.
- ❌ Mở rộng sang chấm chất lượng element hoặc audit technical tổng khi thấy lỗi — route theo phân vai.
- ❌ Dùng skill này đo traffic drop — element drift là NGUYÊN NHÂN khả dĩ, traffic là việc của content-refresh.
- ❌ Snapshot không label/timestamp, hoặc chỉ chụp URL "có vấn đề" — mất tính đại diện template.
- ❌ Fetch >200 URL không rate limit / không báo trước — server khách thật, shared hosting VN dễ chặn.

## References & wiki

**References nội bộ (cross-ref):**
- `skills/technical-seo-audit/SKILL.md` — bảng ngưỡng whitelist (không lặp lại; drift không cần ngưỡng chất lượng, chỉ cần severity).
- `skills/site-migration-checklist/SKILL.md` — Bước 1 PRE benchmark: baseline drift = input cho migration benchmark.
- `sop/06-self-checklist/tier-3-technical-advance.md` — mục 2.4-2.5 (index health) để hiểu hệ quả của noindex/canonical drift.

**Wiki Semantic SEO (lớp WHY):** [[Ranking Signal Consolidation]] · [[Historical Data]] · [[Meta Tags]] · [[Status Codes]] · [[Hreflang PageRank Sharing]] · [[Index Pollution]]

## Changelog

- **v1.1.1 (2026-10-19):** Bước 0 đổi `python3?` thành `python3`, vì script bắt buộc python3.
- **v1.1 (2026-10-19):** thêm `scripts/diff_classify.py` và rubric Jev `tasks/diff-impact.json` 2026-10-19.1 phân loại diff chữ đáng kể hay vô hại; hiệu chuẩn 67 diff thật 15–19/10 (ngưỡng p ≥ 0,65, đúng 46/47). Thêm Bước 0, phân việc model, tự phản biện, cột Mức đổi nghĩa. Test `tests/test_diff_classify.py`.
- **v1.0 (2026-07-19):** tạo mới — 9 elements cố định per URL, 3 mode baseline/compare/history, severity CRITICAL (canonical/robots/status) → HIGH (title/H1/hreflang/schema mất) → MEDIUM (meta desc); storage ladder SQLite → CSV → markdown; nhịp T2/T4/T7 + hằng tháng duy trì.
