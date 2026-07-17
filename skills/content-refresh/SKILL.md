---
name: content-refresh
description: "Phát hiện và xếp hạng content decay sau publish từ data hiệu suất theo cửa sổ thời gian (28 ngày detect, 90 ngày + YoY validate), tách seasonal vs decay thật, bắt cannibalization, phân loại nguyên nhân và sinh UPDATE BRIEF — DECAY-DETECTION front-end của vòng đời content, output là input cho 10-update-pipeline. Use when: (1) 'kiểm tra content decay [site]', 'bài nào đang rớt traffic', 'rà bài cần refresh [site/cluster]'; (2) 'traffic bài [URL] giảm, có cần update không'; (3) audit quý content sau publish. Data ưu tiên Ahrefs MCP (gsc-*, site-explorer-*-history), fallback GSC export CSV, đường lùi cuối là URL + triệu chứng. KHÔNG dùng cho: thực thi sửa bài (→ Content Production/10-update-pipeline + content-update-orchestrator), audit chất lượng nội dung (→ semantic-content-audit), authority gap/backlink (→ backlink-plan)."
metadata:
  version: "1.0"
---

# Content Refresh — Decay Detection & Update Brief

Front-end DECAY-DETECTION cho vòng đời content sau publish: đọc data hiệu suất theo cửa sổ thời gian → chạy gate chain loại nhiễu (min-data, self-inflicted, seasonal, SERP feature, cannibalization) → xếp hạng bài decay thật theo giá trị cứu được → sinh **UPDATE BRIEF**.

**Upstream:** data hiệu suất (Ahrefs MCP / GSC export CSV / triệu chứng do user mô tả).
**Downstream:** `Content Production/10-update-pipeline` + `content-update-orchestrator` — brief của skill này feed thẳng section "Update reason" của template `_TEMPLATES/update.md`. Skill này **KHÔNG** lặp lại logic sửa bài của pipeline.

## Bảng phân vai

| Việc | Skill |
|---|---|
| Detect decay, gate chain, xếp hạng, sinh UPDATE BRIEF | **content-refresh (skill này)** |
| Thực thi sửa bài: diff SERP top 5, section plan, surgical rewrite, re-verify, re-humanize | `Content Production/10-update-pipeline` + `content-update-orchestrator` |
| Audit chất lượng nội dung (rules, semantic, cấu trúc) | `semantic-content-audit` (+ `sop/05-audit-checklist.md` cho cadence pre-publish) |
| Diff nội dung vs competitor hiện tại | `competitor-seo-gap-analysis` (pipeline nạp ở bước diff) — skill này chỉ flag "competitor vượt" ở mức tín hiệu |
| Authority gap (KD cao, thiếu backlink) | `backlink-research` + `backlink-plan` — skill này chỉ gắn route flag AUTHORITY-GAP |
| Wiki health check | `seo-lint` — đừng nhầm "decay" wiki với decay content client |
| Viết lại từ đầu topic đã mất intent | `seo-article` / `seo-content-pipeline` — skill này chỉ gắn route flag REWRITE |

## Input

**Required:**
- `$SITE` — domain hoặc URL set cần rà soát.
- `$DATA_PATH` — A / B / C (tự detect theo ladder dưới nếu user không chỉ định).

**Optional:**
- `$SCOPE` — cluster / folder / danh sách URL cụ thể (mặc định: toàn site).
- `$WINDOW` — mặc định 28 ngày detect + 90 ngày YoY validate (T1/T2 trong [references/decay-signals.md](references/decay-signals.md)).
- `$BRAND` — GTV / TAG / client — quyết định folder pipeline nhận brief (theo TASK ROUTING của workspace).
- `$AI_DATA` — GSC Search Generative AI report / Ahrefs Brand Radar nếu có → thêm lớp report AI visibility riêng.

**Path detection (ladder — luôn có đường lùi không cần MCP):**

- **Path A (ưu tiên) — Ahrefs MCP:** `gsc-pages`, `gsc-page-history`, `gsc-keyword-history`, `gsc-positions-history`, `gsc-performance-history` (clicks/impressions/CTR/position theo thời gian). Khi không có GSC access trong Ahrefs: `site-explorer-pages-history`, `site-explorer-keywords-history`, `site-explorer-top-pages` (filter Declining). `serp-overview` cho intent-shift check, `keywords-explorer-overview` cho KD.
- **Path B — GSC export CSV:** user export Performance 2 lần so sánh (28 ngày vs 28 ngày liền trước; 90 ngày vs cùng kỳ năm ngoái) hoặc export có date dimension. ⚠️ GSC Performance giữ tối đa ~16 tháng data (con số cần verify tại Google Search Console docs) → YoY validate ở Path B chỉ khả thi trong biên đó.
- **Path C — URL + triệu chứng (đường lùi cuối):** user paste danh sách URL + mô tả triệu chứng. Skill chạy chế độ heuristic: classify nguyên nhân + liệt kê chính xác data cần lấy thêm; **KHÔNG chấm priority score bằng số** ở path này.

## Workflow

### Bước 0 — Scope gate & xác nhận (bắt buộc)

1. Xác nhận `$SITE`, `$SCOPE`, `$DATA_PATH`, `$BRAND` (entity GTV/TAG/client — không mix).
2. Hỏi 3 câu gate trước khi đụng data:
   - **Tuổi data:** site có ≥13 tháng data không? Nếu không → không chạy được seasonal gate YoY, mọi kết luận phải ghi rõ *"chưa loại trừ được seasonality"*.
   - **Self-inflicted check:** có đợt sửa bài / migration / đổi template nào trong ~8 tuần gần đây không? (Traffic giảm ngay sau một lần sửa = self-inflicted → RESTORE, không refresh.)
   - **Business relevance:** cluster/topic nào đang là ưu tiên kinh doanh? (input cho trục relevance của priority score T11).
3. 🔴 Path A: báo số MCP call dự kiến (screening site-level ~3-5 call; mỗi candidate thêm ~2-3 call cho history + KD) — **chờ user xác nhận rồi mới gọi**.
4. 🔴 Nhắc trước 1 lần **6-month lag rule (Koray):** ranking hôm nay phản ánh Historical Data từ ít nhất 6 tháng trước (≥6 tháng); effect của update thấy sớm nhất 7-30 ngày, đầy đủ sau 6+ tháng — set expectation ngay từ đầu.

### Bước 1 — Thu data theo path

- Path A: kéo series clicks/impressions/CTR/position cho `$SCOPE` theo 2 cửa sổ (28d vs prev 28d; 90d vs YoY). Tool + params cụ thể cho từng tín hiệu: xem bảng T1-T14 trong [references/decay-signals.md](references/decay-signals.md).
- Path B: đọc CSV user cung cấp; kiểm tra đủ 2 phép so sánh chưa, thiếu thì yêu cầu export bổ sung (nói rõ filter cần chọn trong GSC).
- Path C: thu triệu chứng theo checklist câu hỏi trong references (cột "Path C" của bảng tín hiệu).

### Bước 2 — Screening rộng (lọc candidate)

Ngưỡng screening T5: clicks giảm **20-40% qua 8-12 tuần**, hoặc flag quý **>20% YoY** (Ahrefs). Path A recipe gốc (Ahrefs blog): Top Pages filter **Declining** + cửa sổ 12 tháng + **KD < 40**.

⚠️ Mọi ngưỡng trong skill là **đề xuất thực nghiệm có nguồn** (không phải chuẩn Google công bố) — hiệu chỉnh theo baseline dự án sau 2-3 chu kỳ audit. Ngưỡng gốc đến từ site tiếng Anh, chưa có số hiệu chỉnh cho SERP VN.

### Bước 3 — Gate chain (thứ tự cố định, không đảo)

Mỗi candidate phải đi qua đủ 5 gate theo đúng thứ tự trước khi được gọi là "decay thật":

```
min-data (T9) → self-inflicted → seasonal YoY (T7) → SERP feature (T6) → cannibalization (T8) → decay confirm (T3/T4)
```

- 🔴 **Min-data (T9):** KHÔNG kết luận decay từ biến động <4-6 tuần (guardrail + 6-month lag rule); query <100 impressions/28 ngày không đủ tín hiệu position.
- **Self-inflicted:** giảm ngay sau một lần sửa → route RESTORE.
- 🔴 **Seasonal (T7) bắt buộc trước khi rank:** YoY delta ≈ 0 → seasonal, loại khỏi queue. Chỉ được bỏ qua khi site <13 tháng tuổi — và phải ghi chú rõ.
- **SERP feature (T6):** CTR giảm ≥25% nhưng position đổi <0,5 (hoặc impressions flat + CTR giảm) → "SERP feature loss" (AIO/snippet xuất hiện), KHÔNG phải lỗi content, không tạo UPDATE BRIEF.
- **Cannibalization (T8):** ≥2 URL cùng query nhận impressions + position flip-flop qua các tuần → route CONSOLIDATE (1 đề xuất cho cả cặp). Benign nếu 2 URL phục vụ intent khác nhau.
- **Decay confirm (T3/T4):** clicks giảm ≥30% vs baseline 28 ngày kéo dài 2 tuần liên tiếp, HOẶC average position tụt ≥2 trên queries ≥100 impressions/28 ngày.

Decision tree đầy đủ: [references/decay-signals.md](references/decay-signals.md), mục 2.

### Bước 4 — Phân loại nguyên nhân + DEPTH đề xuất

7 loại: stale facts / SERP intent shift / competitor vượt / thiếu entity-attribute mới / cannibalization / self-inflicted / SERP feature loss — bảng tín hiệu chẩn đoán + DEPTH ở [references/decay-signals.md](references/decay-signals.md), mục 3. DEPTH gợi ý cho pipeline: stale facts = **light**; competitor / entity gap = **medium**; intent shift = **heavy** (thường cần re-outline, không phải refresh nhẹ). Ghi kèm confidence (cao/vừa/thấp) cho mỗi phân loại.

### Bước 5 — Priority score + Route flag

- **T11 (convention GTV, không phải industry standard):** `Priority = Recovery potential (peak clicks − current clicks, hoặc traffic value) × Ease (KD thấp, structure sound, còn backlinks) × Business relevance`.
- **T10 — Ease filter:** KD < 40 = "cứu được bằng content"; KD cao hơn → vấn đề authority, gắn flag AUTHORITY-GAP route sang `backlink-plan`, ❌ không hứa cứu bằng refresh.
- **Route flag** (theo decision framework Ahrefs): `UPDATE` / `CONSOLIDATE` / `REDIRECT` / `PRUNE` / `RESTORE` / `REWRITE` / `AUTHORITY-GAP` — **chỉ UPDATE mới đổ vào 10-update-pipeline.**
- 🔴 **Protect Historical Data:** chỉ bài qua gate T3/T4/T5 mới vào queue. Bài đang perform không kéo vào — chỉ đưa vào annual review (review 1 lần/năm cho bài quan trọng bất kể metrics, theo Ahrefs).

### Bước 6 — Sinh UPDATE BRIEF + report tổng

1. Present danh sách candidate + route flag → **chờ user duyệt** (execution rule workspace).
2. Mỗi candidate flag UPDATE → 1 brief theo [references/update-brief-template.md](references/update-brief-template.md). Các flag khác (CONSOLIDATE/RESTORE/AUTHORITY-GAP…) chỉ ghi nhận trong report tổng kèm đề xuất route.
3. Skill **dừng tại đây** — không diff SERP chi tiết, không section plan (đó là bước 1-2 của 10-update-pipeline).

## Output

**Report tổng** — skeleton:

```markdown
# Content Refresh Report — <site> — <YYYY-MM-DD>

## Scope & data
- Data path: A/B/C | Cửa sổ: 28d (<dd/mm–dd/mm>) vs prev 28d; 90d vs YoY (<năm>)
- Nguồn data + ngày lấy: <Ahrefs MCP / GSC export ngày X / triệu chứng user>
- Gate bỏ qua (nếu có): <vd: seasonal YoY — site <13 tháng, chưa loại trừ seasonality>

## Decay ranking (đã qua đủ gate chain)
| # | URL | Peak → Current clicks | Δ 28d | Δ YoY | Δ Position | Nguyên nhân (confidence) | DEPTH | Priority | Route |
|---|-----|----------------------|-------|-------|-----------|--------------------------|-------|----------|-------|

## Loại khỏi queue
| URL | Gate chặn | Ghi chú / route thay thế |
|-----|-----------|--------------------------|

## Cannibalization pairs
| Query | URL A ↔ URL B | Pattern quan sát | Đề xuất CONSOLIDATE (URL giữ + 301) |
|-------|---------------|------------------|--------------------------------------|

## AI visibility (chỉ khi có $AI_DATA — lớp riêng, đo aggregate)
- <AI Share of Voice / impressions AI report — KHÔNG đo prompt đơn lẻ>

## Re-measurement plan
- 7-30 ngày: GSC impressions cho target queries (theo SOP GTV)
- 90 ngày: validate clicks/position
- 6 tháng: full Historical Data effect (Koray 6-month lag)

## ⚠️ Disclaimer
- Ngưỡng T1-T14 là đề xuất thực nghiệm có nguồn — hiệu chỉnh theo baseline dự án sau 2-3 chu kỳ audit.
- Ranking hôm nay phản ánh HD từ ít nhất 6 tháng trước (≥6 tháng); không kết luận decay từ biến động <4-6 tuần.
```

**UPDATE BRIEF** — mỗi URL flag UPDATE 1 file, skeleton đầy đủ ở [references/update-brief-template.md](references/update-brief-template.md).

**Đặt tên file:**
- Report: `<site>_Content-Refresh-Report_v1.md` → `Deliverables/<project>/` (tăng `_v2`, `_v3`… nếu trùng).
- Brief: `<slug>__brief_v1.md` → folder `10-update-pipeline/<cluster>/` của brand tương ứng (`Content Production - GTV/` hoặc `Content Production - TAG/`), khớp convention output pipeline `<slug>__vN.md`.

## Behavior Gates

- **#1 Think Before** — đây là task NGHĨ (phân tích) → Opus + Thinking. Thiếu input quyết định output (tuổi site, lần sửa gần nhất, entity brand, business priority) → hỏi qua `cơ chế hỏi người dùng có cấu trúc của runtime`, không lấp bằng assumption. Phép thử: "nếu assumption này sai, ranking priority có hỏng không?"
- **#2 Evidence** — mọi con số trong report/brief truy được về nguồn + ngày lấy data (tool + date range, hoặc file CSV + ngày export). Mọi ngưỡng cite theo mã T1-T14 kèm nguồn gốc (Ahrefs / User Growth / GTV convention). Số không có citation → không đưa vào output.
- **#3 Surgical** — dừng ở UPDATE BRIEF. Không diff SERP chi tiết, không viết section plan, không sửa bài, không đề xuất đổi URL (anti-pattern của pipeline). Phát hiện việc ngoài scope (vd wiki cần update) → note 1 câu, làm xong task trước.
- **#4 Goal-driven** — mục tiêu là recovery traffic có giá trị business, không phải "update cho có Update Score". Update phải substantive (Update Amount > 0); protect HD của bài đang khỏe; ưu tiên theo T11 chứ không theo "bài nào lâu chưa sửa".

## Anti-patterns

- ❌ Kết luận decay từ biến động <4-6 tuần hoặc query <100 impressions/28 ngày (vi phạm T9 + 6-month lag).
- ❌ **Date-spoofing**: đổi ngày publish/modified mà không đổi content — không qualify là substantive update và bị coi là manipulation (Google so old vs new content để detect substantive change — [[Update Score]] fake-freshness; [[GEO]] — Yeşilyurt: date-spoofing = manipulation, không dùng cho client).
- ❌ Kéo bài đang perform vào update queue "cho chắc" — phá Historical Data positive đang tích lũy.
- ❌ Sinh 2 UPDATE BRIEF cho 2 URL đang cannibalize nhau — cặp đó là 1 đề xuất CONSOLIDATE/301.
- ❌ Bỏ qua seasonal gate YoY khi site đủ 13 tháng data.
- ❌ Bỏ qua self-inflicted check — refresh một bài vừa bị sửa hỏng thay vì restore bản trước.
- ❌ Làm thay pipeline: diff SERP top 5, section-level plan, rewrite — đó là bước 1-2 của 10-update-pipeline.
- ❌ Hứa cứu bằng content khi KD cao — đó là authority gap, route `backlink-plan`.
- ❌ Relaunch/redirect với hy vọng "reset historical data" — bad HD không reset được, chỉ overwrite bằng signal positive mạnh hơn.
- ❌ Đo AI visibility theo prompt đơn lẻ — AIO đổi bề mặt mỗi ~2,15 ngày; chỉ đo aggregate (AI Share of Voice), và report tách lớp riêng khỏi decay Google (2 chiều độc lập).

## References & wiki

- [references/decay-signals.md](references/decay-signals.md) — bảng tín hiệu T1-T14 (ngưỡng + cách đo Path A/B/C + nguồn), decision tree gate chain, bảng nguyên nhân → tín hiệu → DEPTH.
- [references/update-brief-template.md](references/update-brief-template.md) — skeleton UPDATE BRIEF khớp input 10-update-pipeline (`_TEMPLATES/update.md`).
- Wiki nền: [[Historical Data]] (6-month lag, engagement polarity, protect HD) · [[Update Score]] (Update Frequency × Update Amount, fake freshness) · [[Traffic Box]] (BCAU re-evaluation, static source) · [[Click Satisfaction]] (CTR/engagement là input decay hợp lệ) · [[GEO]] (URL freshness score, 76,4% top cited update trong 30 ngày, đo AI visibility aggregate).
- SOP liên quan: `sop/05-audit-checklist.md` (post-publish tracking 7-30 ngày, monthly audit cadence).
- Pipeline downstream: `Content Production/10-update-pipeline/README.md` + `CLAUDE.md` (trigger table, `$DEPTH`, template update.md).

## Changelog

- **v1.0 (2026-07-07):** khởi tạo — tổng hợp từ wiki Koray/GTV (Historical Data, Update Score, Traffic Box, Click Satisfaction, GEO) + web research (Ahrefs content-decay, User Growth academy, Animalz ×2, SEO Sherpa cannibalization); ngưỡng T1-T14 đánh dấu đề xuất thực nghiệm; boundary khóa với 10-update-pipeline / semantic-content-audit / backlink-plan.
