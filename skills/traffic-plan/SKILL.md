---
name: traffic-plan
description: "Lập plan traffic cho dự án SEO GTV theo quy trình 10 tháng (sop/09) — FORECAST layer, 2 mode: Outer-first (T2, công đoạn 9) research Outer Section trước để tạo Historical Data sớm; FULL (T3 → giữa T4, công đoạn 17) plan toàn bộ với forecast tổng ≥ cam kết hợp đồng +20%, model min."
metadata:
  version: "1.1"
---

# Traffic Plan

Lập **plan traffic dự phóng** cho dự án SEO GTV — công đoạn (9) T2 và (17) T3 → giữa T4 của quy trình 10 tháng (`sop/09-project-timeline/10-thang-thuc-day.md`). Skill này KHÔNG chọn topic, KHÔNG vẽ map — nó nhận topic/URL đã có (từ `topical-map-creation` + `keyword-topic-url-mapping`) và trả lời một câu hỏi duy nhất: **kế hoạch này có đủ trả cam kết hợp đồng +20% không, và traffic về theo tháng nào.**

🔴 Nguyên tắc trung tâm: forecast phải **trễ pha theo maturity curve** — content cần ~100 ngày mature, tháng đạt ≠ tháng publish. Plan nào cộng traffic ngay tháng publish là plan sai.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Chọn topic, xây Topical Map / SCN đầy đủ toàn site | `topical-map-creation` | Skill này chỉ NHẬN topic list làm input; khi gap check fail → đề xuất danh sách topic bổ sung rồi ROUTE về topical-map-creation, không tự vẽ map |
| Gom bộ keyword cam kết thành topic → URL SEO | `keyword-topic-url-mapping` | Bảng keyword ↔ topic ↔ URL là INPUT của skill này, không phải output |
| Lập OKRs & KPI quý | `okrs-gtv-tag-framework` | Skill này chỉ cấp số forecast làm căn cứ; không viết Objective/KR |
| Báo cáo traffic thực tế cho client | `gtv-client-report` | Plan = dự phóng trước; report = kết quả sau. Không trộn |
| Phát hiện content decay sau publish | `content-refresh` | Skill này dừng ở forecast; theo dõi hậu publish là việc khác |
| Research 1 bài / 1 SERP cụ thể | `seo-research` | Skill này làm ở tầng danh mục topic, không drill từng bài |

## Input

**Required:**
- `$CLIENT` — tên client/instance SEO Production.
- `$MODE` — `outer-first` (T2) hoặc `full` (T3 → giữa T4). Không rõ → hỏi, vì gate duyệt và phạm vi khác nhau.
- Bảng topic ↔ URL: từ `keyword-topic-url-mapping` output hoặc topical map đã chốt (`05-content-plan/` của instance).
- KPI cam kết hợp đồng: `00-client-context/kpi-commitments.md` của instance, hoặc user cung cấp (số traffic/tháng + tháng đạt).

**Optional:**
- `$BASELINE` — traffic hiện tại (GSC/GA4/Ahrefs).
- `$CTR_CURVE` — bảng CTR riêng của site (ưu tiên `gsc-ctr-by-position` khi có GSC nối Ahrefs); không có → dùng bảng default bên dưới.
- `$TIMELINE` — biến thể hợp đồng 8/10/12 tháng (mặc định 10; mốc dịch theo bảng biến thể sop/09).

**Data ladder (khai báo DATA TIER trong output):**

| Tier | Nguồn | Ghi chú |
|---|---|---|
| Tier 1 | Ahrefs MCP — `keywords-explorer-overview` / `keywords-explorer-matching-terms` (volume, KD), `gsc-ctr-by-position` (CTR thật của site) | Báo số call dự kiến, chờ user xác nhận trước khi gọi |
| Tier 2 | DataForSEO Labs (search volume, keyword difficulty) | Khi Ahrefs MCP không có / hết quota |
| Tier 3 | CSV export / user paste tay volume | Luôn chạy được — skill không bao giờ chết vì thiếu MCP; report ghi rõ nguồn + ngày data |

## Workflow

### Bước 0 — Đọc references + xác nhận scope

1. Đọc `SEO Production/_TEMPLATES/traffic-plan.md` (template output, công đoạn 17) + `sop/09-project-timeline/10-thang-thuc-day.md` (ma trận content type × timeline).
2. Xác nhận `$MODE`, `$CLIENT`, timeline hợp đồng, KPI cam kết (số + tháng đạt). Thiếu KPI cam kết → DỪNG, hỏi — không có cam kết thì không có chuẩn để check +20%.
3. Chốt DATA TIER khả dụng; Tier 1 → báo số call MCP dự kiến, chờ xác nhận.

### Bước 1 — Mode Outer-first (T2, công đoạn 9) — bỏ qua nếu $MODE = full

Mục tiêu: **initial traffic sớm để tạo [[Historical Data]]** — research [[Outer Section]] TRƯỚC, triển khai từ cuối T3/T4.

1. Từ Outer Section của topical map, lọc topic dễ lấy traffic nhanh — ưu tiên [[Phantom Keywords]] (volume cao + KD thấp), verify bằng `allintitle:`:

| `allintitle:` kết quả | Đánh giá |
|---|---|
| < 500 | Ngưỡng khuyên dùng cho site mới |
| < 1.000 | Rất tốt |
| < 5.000 | Chấp nhận được |
| ≥ 5.000 | Không tính là Phantom — cạnh tranh title trực diện |

2. Chấm mỗi topic: volume, KD, allintitle, competition thực tế trên SERP → chọn nhóm topic initial.
3. Forecast initial traffic theo model Bước 2 (chỉ phạm vi nhóm topic đã chọn) → plan này là tiền đề cho Mode FULL ở T3.

### Bước 2 — Forecast model (minh bạch, per URL/topic)

```
Traffic dự phóng (URL, tháng M) = Volume × CTR(position kỳ vọng) × Hệ số maturity(tuổi content tại tháng M)
```

**Bảng CTR curve default** (giả định điều chỉnh được — ưu tiên thay bằng `gsc-ctr-by-position` của chính site khi có; dùng bảng nào phải ghi nguồn vào output):

| Position | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| CTR default | 28% | 15% | 10% | 7% | 5% | 4% | 3% | 2,5% | 2% | 1,8% |

**Hệ số maturity theo tuổi content** (content cần ~100 ngày mature — trình bày trong output là GIẢ ĐỊNH điều chỉnh được theo niche/authority site):

| Tuổi content | Hệ số |
|---|---|
| 0–30 ngày | ~10–20% |
| 30–60 ngày | ~30–50% |
| 60–100 ngày | ~60–85% |
| > 100 ngày | 100% |

Quy tắc bắt buộc:
- Position kỳ vọng phải có căn cứ (KD, benchmark đối thủ, authority site) — KHÔNG mặc định Top 3.
- Tuổi content tính từ tháng publish theo ma trận content type sop/09 (Content URL SEO: T2 → hết T3; Content Marketing & Strategy: 65% trong T3-T4, chốt ≤15 ngày đầu T6) + dây chuyền onpage (+10-15 ngày) và internal link (+15-30 ngày).
- Cộng dồn traffic dự phóng theo tháng T1→T10 → vẽ đường plan so với đường cam kết.

### Bước 2b — AI deflection + AI referral (bổ sung 29/08/2026 — kỷ nguyên AI search)

Model Bước 2 giả định CTR SERP cổ điển. Từ 2025-2026 hai thứ đã đổi và phải nằm **tường minh** trong plan (không cộng ngầm, không bỏ qua):

1. **AI deflection — hạ CTR khi SERP có AI Overview.** Với mỗi keyword, gắn cờ `AIO?` (từ research primer S5 / `seo-research` Bước 7 / SERP screenshot / DataForSEO `ai_overview` item). Keyword có AIO → nhân CTR(position) với **hệ số deflection mặc định 0,5** (dải evidence: CTR #1 giảm −34,5% 04/2025 → **−58%** 12/2025, Ahrefs 300k keywords, B; zero-click Google US 68% 2026, SparkToro, B) — ghi là **giả định điều chỉnh được**, hạ xuống 0,4 cho query informational/dạng câu hỏi (AIO trigger 57,9%), giữ 1,0 cho transactional/shopping (AIO trigger 3,2%). Có `gsc-ctr-by-position` của chính site → dùng CTR thực thay hệ số.
2. **AI referral — dòng riêng, KHÔNG tính vào cam kết.** Dự phóng sessions từ kênh GA4 "AI Assistant" (chatgpt.com · gemini · perplexity · copilot · claude) = **0,3-1% tổng organic** (share AI traffic trung bình 0,32% 2026, SE Ranking, B; site đã mở AI bot + content GEO chuẩn có thể cao hơn — first-party GTV n=1: +111%/tháng sau khi mở bot). Giá trị nằm ở **conversion, không ở volume**: CR kênh AI ≈10× organic (GTV n=1, D) · 23× (Ahrefs, F) · 15,9% vs 1,76% (Seer, B) → trình bày bằng **key events dự phóng**, nhãn directional, tách khỏi đường cam kết (attribution gãy — không nghiệm thu bằng số này).
3. **Điều kiện để dòng AI referral có nghĩa:** gate G-T1 pass (index + page-one + bot search/user-triggered mở) và G-BÀI áp cho bài mới — nếu dự án chưa mở bot thì dòng này = 0 và ghi "chưa đủ điều kiện" thay vì ước lượng.

Output: cột `AIO?` + `CTR sau deflection` trong bảng dự phóng; dòng "AI referral dự phóng (directional, không cam kết)" trong bảng cộng dồn; mục 6 ghi hệ số deflection + share AI đã dùng kèm nguồn + tháng.

### Bước 3 — Gap check (chỉ Mode FULL)

1. Tổng traffic dự phóng tại tháng cam kết so với **cam kết +20%**: đạt ≥120% cam kết → PASS.
2. FAIL → **không hạ mục tiêu, không thổi phồng position kỳ vọng**. Tự đề xuất danh sách topic bổ sung (ưu tiên: Outer còn trống trên map, Phantom Keywords chưa dùng, topic đối thủ có traffic mà map thiếu) → route sang `topical-map-creation` để bổ sung map → lặp lại Bước 2.
3. Lập topic backup (điều kiện kích hoạt: [[Initial Ranking]] không như kỳ vọng, gate T4-T6) đủ bù 10-20% tổng dự phóng.

### Bước 4 — Điền template & lưu

1. Điền `SEO Production/_TEMPLATES/traffic-plan.md` đầy đủ 5 mục + Done-criteria.
2. Lưu vào `05-content-plan/` của instance client, naming `{{CLIENT}}_traffic-plan_v{{N}}.md`.
3. Mode FULL → frontmatter/status ghi **CHỜ DUYỆT: SEO Director** (công đoạn 17 duyệt bởi SEO Director). Mode Outer-first → CHỜ DUYỆT: SEO Lead Project.

## Output

```markdown
# <CLIENT> — Traffic Plan (<Mode Outer-first T2 | Mode FULL T3→giữa T4>)
> Ngày lập: YYYY-MM-DD · DATA TIER: <1/2/3 — nguồn + ngày data> · Timeline HĐ: <8/10/12 tháng>
> Trạng thái: **CHỜ DUYỆT — <SEO Director | SEO Lead Project>**

## 1. Cam kết & mục tiêu
| KPI cam kết | Mục tiêu plan (+20%) | Baseline | CTR curve dùng (nguồn) | Maturity model |
|---|---|---|---|---|

## 2. Bảng dự phóng
| # | Topic | URL | Core/Outer | Volume | KD | allintitle (nếu Phantom) | Position kỳ vọng (căn cứ) | AIO? (hệ số deflection) | Traffic dự phóng | Tháng publish | Tháng đạt |
|---|---|---|---|---|---|---|---|---|---|---|---|

## 3. Cộng dồn theo tháng vs đường cam kết
| Tháng | T1 | T2 | ... | T10 |
|---|---|---|---|---|
| Plan cộng dồn (organic, đã trừ AI deflection) | | | | |
| Đường cam kết | | | | |
| AI referral dự phóng — sessions · key events (directional, KHÔNG tính cam kết) | | | | |

## 4. Gap check
- Tổng dự phóng tại tháng cam kết: <N> = <X>% cam kết → <PASS ≥120% | FAIL>
- Nếu FAIL: danh sách topic bổ sung đề xuất → route `topical-map-creation`

## 5. Topic backup
| # | Topic | Volume | Traffic dự phóng | Điều kiện kích hoạt |
|---|---|---|---|---|

## 6. Giả định & giới hạn data
- <mọi giả định: CTR, maturity, position — kèm nguồn; data thiếu gì>
- AI deflection: hệ số <0,5 / 0,4 / 1,0 theo loại query> — nguồn Ahrefs 12/2025 (−58% CTR #1 khi có AIO) + SparkToro 2026 (zero-click 68%); keyword gắn cờ AIO từ <primer S5 / SERP screenshot / DataForSEO>
- AI referral: share <0,3-1%> organic (SE Ranking 2026) · CR ≈<10×> organic (directional) · điều kiện G-T1 <pass/fail>
```

## Behavior Gates

**#1 Think Before** — Xác nhận mode, KPI cam kết, timeline hợp đồng, DATA TIER trước khi tính. Thiếu KPI cam kết → dừng hỏi. Trước khi gọi MCP: báo số call, chờ xác nhận.

**#2 Evidence** — Mọi con số volume/KD/CTR truy được về nguồn + ngày. CTR curve và hệ số maturity luôn label "giả định điều chỉnh được" kèm nguồn. Output khai báo DATA TIER. Không hard-fail khi thiếu MCP — Tier 3 (paste tay) luôn chạy được, ghi rõ giới hạn.

**#3 Surgical** — Chỉ forecast. Không chọn topic mới (route topical-map-creation), không viết brief, không lập OKRs. Gap fail → đề xuất danh sách + route, không tự ý mở rộng map.

**#4 Goal-driven** — Deliverable = bảng dự phóng trả lời được "tháng nào đạt bao nhiêu, có đủ cam kết +20% không". Mode FULL chưa có chữ ký SEO Director thì mọi bản đều ghi **CHỜ DUYỆT** — plan chưa duyệt không phải plan.

## Anti-patterns

- ❌ Cộng traffic dự phóng ngay tháng publish — bỏ qua ~100 ngày maturity.
- ❌ Mặc định position kỳ vọng Top 3 cho mọi URL để plan "đủ số".
- ❌ Hạ mục tiêu xuống dưới cam kết +20% khi gap check fail thay vì bổ sung topic.
- ❌ Tự vẽ thêm topic/map khi gap fail — việc của `topical-map-creation`.
- ❌ Dùng CTR curve default mà không ghi là giả định / không thử `gsc-ctr-by-position` khi site có GSC.
- ❌ Tính Phantom Keyword không verify `allintitle:` (hoặc dùng ngưỡng ngoài bảng <500/<1.000/<5.000).
- ❌ Mode Outer-first mà plan cả Core Section cạnh tranh cao — sai mục tiêu Historical Data sớm.
- ❌ Bỏ qua dây chuyền content → onpage (+10-15 ngày) → internal link (+15-30 ngày) khi tính tháng đạt.
- ❌ Trình plan FULL như bản chốt khi chưa có duyệt SEO Director.

## References & wiki

**Nguồn quy trình:**
- `sop/09-project-timeline/10-thang-thuc-day.md` — công đoạn (9) T2 + (17) T3→giữa T4, ma trận content type, maturity ~100 ngày, biến thể 8/12 tháng.
- `SEO Production/_TEMPLATES/traffic-plan.md` — template output chuẩn.
- `SEO Production/00-client-context/kpi-commitments.md` (per instance) — nguồn KPI cam kết.

**Wiki Semantic SEO (lớp WHY):** [[Historical Data]] · [[Phantom Keywords]] · [[Outer Section]] · [[Core Section]] · [[Topical Map]] · [[Topical Authority]] · [[URL SEO]] · [[Initial Ranking]] · [[Vastness-Depth-Momentum]]

**Skill anh em:** `keyword-topic-url-mapping` (input mapping) · `topical-map-creation` (route khi gap) · `okrs-gtv-tag-framework` · `gtv-client-report` · `content-refresh`

## Changelog

- **2026-08-29 v1.1** — Bước 2b **AI deflection + AI referral** (Vincent duyệt 29/08, FINDINGS 22/08 §1): keyword có AIO → CTR × hệ số deflection mặc định 0,5 (0,4 informational/câu hỏi · 1,0 transactional; evidence Ahrefs −34,5%→−58% CTR #1, SparkToro zero-click 68% — giả định điều chỉnh được, ưu tiên `gsc-ctr-by-position` thực); dòng **AI referral** tách riêng (share 0,3-1%, CR ≈10×/23×/15,9% vs 1,76% — directional, không cam kết, điều kiện G-T1 pass); output thêm cột `AIO?`, dòng AI referral, mục 6 ghi hệ số + nguồn.
- **2026-07-19 v1.0** — tạo mới: 2 mode Outer-first/FULL theo công đoạn (9)+(17) sop/09, forecast model volume × CTR × maturity, gap check cam kết +20% + route topical-map-creation, data ladder Ahrefs MCP → DataForSEO → paste tay, gate duyệt SEO Director.
