---
name: programmatic-seo-builder
description: "Thiết kế và kiểm soát programmatic SEO: gate có nên làm, template E-A-V, tỷ lệ unique, internal link, schema, guardrail rủi ro AI-era, pilot rồi scale theo batch. Dùng khi: 'làm programmatic [dạng trang]', 'template content hàng loạt', 'trang theo tỉnh/thành có nên tự sinh'."
metadata:
  version: "1.2"
---

# Programmatic SEO Builder

Vận hành loại content **template/programmatic** — dòng 7 ma trận content type × timeline (`sop/09-timeline/10-thang-thuc-day.md`): nhóm trang cùng pattern sản xuất hàng loạt từ 1 template + data (trang địa điểm, danh mục, so sánh/giá…). **TÙY DỰ ÁN, không có timeline cố định** — chỉ triển khai khi plan + research thị trường & phân loại page type cho thấy phù hợp.

🔴 Behavior Gate cứng của cả skill: **template CHƯA được Content Leader duyệt = KHÔNG nhân bản số lượng lớn.** Skill này tồn tại để programmatic không biến thành [[Index Pollution]].

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Chọn cụm topic / vị trí cụm programmatic trong map | `topical-map-creation` | Skill này nhận cụm đã nằm trong map; không tự quyết cụm nào đáng cover |
| Viết nội dung thật cho các block của template | `semantic-content-writing` | Skill này chỉ SPEC block (E-A-V nào, data nào, độ dài) — không viết văn |
| Layout PLP / visual template, buy-box, entity card | `visual-semantic-seo` | Skill này spec cấu trúc thông tin per block; thiết kế visual là việc của skill kia |
| Schema/JSON-LD chi tiết per page type | `schema-markup-generator` | Skill này chỉ chỉ định LOẠI schema per page type; viết markup là việc của skill kia |
| Index monitoring / audit index bloat toàn site | `technical-seo-audit` | Skill này theo dõi index rate của RIÊNG batch programmatic sau publish; audit site-level route đi |
| Mapping keyword cam kết → URL | `keyword-topic-url-mapping` | Programmatic thường nằm NGOÀI bộ cam kết; nếu trùng URL cam kết → đối chiếu bảng mapping trước |

## Input

**Required:**
- `$CLIENT` — client/instance SEO Production.
- `$PATTERN` — pattern trang đề xuất (vd "dịch vụ X tại [quận]", "[sản phẩm] giá bao nhiêu", "[category] tốt nhất").
- `$DATA_SOURCE` — nguồn data sinh unique value per page: CSV / API / DB nội bộ / thu thập tay — kèm mô tả field.

**Optional:**
- `$SCALE` — số page dự kiến.
- `$SITE_AUTHORITY` — site mới hay đã có authority (ảnh hưởng khuyến nghị batch size + tolerance).
- Topical map của instance (xác nhận cụm programmatic đã có chỗ trong map).

**Data ladder (khai báo DATA TIER trong output):**

| Tier | Nguồn | Ghi chú |
|---|---|---|
| Tier 1 | Ahrefs MCP `keywords-explorer-matching-terms` (verify demand lặp pattern) + GSC qua `mcp-gsc` (index rate sau publish) | Báo số call, chờ xác nhận |
| Tier 2 | DataForSEO Labs (pattern volume) + GSC export user cấp | |
| Tier 3 | User paste danh sách biến thể pattern + volume tay; index check bằng `site:` operator mẫu | Luôn chạy được; report ghi rõ giới hạn |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Claude | Chấm gate G1–G3, non-commodity test, spec template, viết block risk disclosure | dùng |
| Code | Đếm field có giá trị của từng biến thể trong `$DATA_SOURCE` khi data là CSV | dùng: phép đếm min-data phải tất định |
| Jev | Chấm non-commodity cho từng page pilot | không dùng: chưa có rubric hiệu chuẩn. Claude đọc mẫu pilot |
| EmbeddingGemma 2 | Đo độ giống giữa các page pilot | không dùng: chưa có ngưỡng near-duplicate đã hiệu chuẩn cho trang template |
| GLM Flash | Trích câu | không dùng: skill không trích câu hàng loạt |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'gsc?,dataforseo?,ahrefs?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0b — Đọc references + xác nhận scope

1. Đọc `sop/09-timeline/10-thang-thuc-day.md` (dòng 7 ma trận content type) + topical map instance (cụm liên quan) + `sop/01-topical-map.md` (chuẩn Core/Outer).
2. Xác nhận `$PATTERN`, `$DATA_SOURCE` (xem được sample data chưa?), `$SCALE`, DATA TIER.
3. Nếu chưa có plan + research thị trường & phân loại page type cho nhóm trang này → DỪNG, nói rõ: theo quy trình, programmatic chỉ triển khai khi 2 điều kiện đó cho thấy phù hợp — đề xuất chạy `topical-map-creation`/`competitor-seo-gap-analysis` trước.

### Bước 1 — Gate "có nên làm programmatic không"

Chấm 3 tiêu chí, mỗi tiêu chí PASS/FAIL kèm evidence:

| # | Tiêu chí | Cách kiểm | PASS khi |
|---|---|---|---|
| G1 | **Search demand lặp pattern** | Sinh 20-30 biến thể pattern → check volume (Tier 1/2) hoặc SERP thực tế | Đa số biến thể có demand thật (volume >0 hoặc SERP có đối thủ rank riêng per biến thể); đối thủ đang phục vụ pattern bằng page riêng |
| G2 | **Data source đủ unique value per page** | Soi sample `$DATA_SOURCE`: đếm field khác biệt per biến thể | Mỗi page nhận được bộ data riêng đủ trả lời intent của biến thể đó — không chỉ swap tên vào cùng một bài |
| G3 | **Số lượng đáng làm template** | So `$SCALE` với chi phí làm template + pilot | `$SCALE` đủ lớn để template rẻ hơn viết tay (heuristic: hàng chục page trở lên; dưới ~15-20 page → viết tay thường rẻ hơn) |

**Bất kỳ tiêu chí nào FAIL → route content thường** (pipeline `seo-content-pipeline` / `semantic-content-writing`) và ghi rõ lý do. Không "cố cho qua gate" — programmatic fail gate chính là nguồn thin content.

**G2 kèm Non-commodity test (v1.1 — 08/2026, Google chính chủ):** ngoài đếm field, chạy test của Google AI optimization guide — nếu page sinh ra từ template "could easily be produced by a generative AI model" (tự tạo được bằng cách summarize SERP + chạy qua LLM) = **commodity → G2 FAIL** dù data field có vẻ đủ. Chuẩn 3 traits Unique/Specific/Authentic (slide Danny Sullivan SCL Toronto 04/2026 — "Authentic" = first-hand knowledge or **experience**): mỗi page programmatic phải mang data/attribute unique thật (proprietary data, đo đạc riêng, inventory thật) — không scale template rỗng. Wiki: [[Non-Commodity Content]].

**G1 chấm bằng QDP Gate (v1.1 — 07/2026):** per biến thể pattern, chạy rubric 4 tiêu chí `skills/keyword-topic-url-mapping/references/qdp-gate.md` (canonical) — biến thể/tổ hợp fail gate KHÔNG sinh trang, hạ thành section/component trên trang cấp trên (evidence scale: Doktorsitesi 4M trang không index → xóa = +600K clicks; Ucuzabilet route "NYC to Erzurum" ~50 search/năm; yacht [model]+[city]+[district] → prune = +248% clicks — `wiki/cases/local-seo-sel-cases-2026.md`). Đặc biệt: tổ hợp [service]+[location] cấp district/phường hầu hết fail similarity WEIGHTED (term location quá nhẹ).

### Bước 2 — Thiết kế template

Spec per page type (output = TEMPLATE SPEC, không phải content):

1. **Block E-A-V bắt buộc per page** — theo [[E-A-V Framework]]: mỗi block khai báo Entity (biến thể pattern) + Attributes bắt buộc + Value lấy từ field nào của `$DATA_SOURCE`. Block thiếu data = block không render (không để trống, không lorem).
2. **Tỷ lệ unique tối thiểu**: đề xuất **≥30-40% nội dung unique data/page** (phần còn lại là khung [[Boilerplate Content]] dùng chung) — dưới ngưỡng này các page trở thành near-duplicate.
3. **Internal link pattern**: mỗi page programmatic link lên hub/category của cụm + link ngang sang biến thể liên quan (cùng quận lân cận, cùng price range…) + hub link về [[Core Section]] — signal flow theo chuẩn topical map, tránh đảo trang mồ côi.
4. **Schema per page type**: chỉ định loại (LocalBusiness/Service cho trang địa điểm, Product/Offer cho trang giá, ItemList cho danh mục…) → chi tiết markup route `schema-markup-generator`.
5. Heading skeleton + vị trí block theo intent của pattern; layout visual route `visual-semantic-seo`.

### Bước 3 — Thin-content & index-bloat prevention

| Cơ chế | Quy tắc |
|---|---|
| **Min-data threshold** | Định ngưỡng field bắt buộc per page (vd ≥N field có giá trị + block E-A-V chính đầy đủ). Page dưới ngưỡng → **noindex hoặc không sinh** — mặc định KHÔNG SINH (không đưa page rỗng vào hệ) |
| **Sitemap segmentation** | Sitemap riêng per batch programmatic (tách khỏi sitemap chính) → đọc được index rate per batch trong GSC |
| **Canonical cho biến thể** | Biến thể không đủ khác biệt (filter/sort/param, biến thể gần trùng data) → canonical về biến thể chính, không sinh URL riêng |
| **Giám sát index rate sau publish** | GSC per sitemap batch: theo dõi indexed/submitted. Index rate thấp kéo dài hoặc giảm dần theo batch → DỪNG scale, xử lý trước khi sinh tiếp ([[Index Pollution]] + [[Cost of Retrieval]] — index bloat làm đắt cả site) |

### Bước 3b — Guardrail rủi ro AI-era (v1.1 — 08/2026)

Lớp risk bắt buộc khi propose programmatic ở scale. Mọi số dưới đây: **refresh theo lint quý** (stats AI = moving target).

1. **Risk disclosure bắt buộc trong mọi proposal/spec scale lớn** — cohort data: **220+ domains** dùng AI content scaling tools (lấy từ customer-stories pages công khai của 12+ platforms; data Ahrefs đối chiếu Sistrix, snapshot 05/2026) → **54% mất ≥30% / 39% mất ≥50% / 22% mất ≥75% peak organic traffic**. Label: **observational/correlational** — tác giả tự disclaim không phải causation (Lily Ray Substack 13/05/2026 — [[sources/ai-content-risks-cohort-lily-ray]]). Correlational nhưng đủ để client phải nghe risk TRƯỚC khi duyệt scale — không trình scale plan thiếu block này.
2. **Pattern "Mount AI"** (cùng nguồn): page growth nhanh 6-12 tháng → traffic peak → rơi thẳng trong năm kế, thường xuống DƯỚI baseline cũ; recovery 6-12 tháng+ và cần core update kế tiếp re-evaluate. Set expectation này trong proposal — spike đầu không phải bằng chứng template an toàn.
3. **Footprint tự kiểm trước launch** (cùng nguồn — sites decline dùng ≥3-4 template trong list): ☐ self-serving listicles (tự xếp mình #1) · ☐ scaled comparison/alternative pages · ☐ FAQ farm 1-question-per-URL · ☐ programmatic glossaries/location pages · ☐ fake-refresh dates. Template dính ≥2 mục → DỪNG, review lại với Content Leader trước khi pilot; các tactic này CÓ work ngắn hạn — vấn đề là khi scale, footprint dễ detect ("packaging is new, but the pattern is not" — tactics HCU/March-2024 repackaged).
4. **Engine counter-adjust** — template listicle/comparison scale để câu AI citation là tactic đang bị trừng phạt: ChatGPT 5.6 (08/2026) cắt citation share listicle **−50,5%** / comparison **−32,1%** (Peec data — ⚠ secondhand qua X post Lily Ray, chưa publish methodology; [[sources/chatgpt-page-type-citation-shift-peec]]). Không bán programmatic listicle/comparison như GEO lever; chi tiết backfire: [[Best List Page]] section Backfire risk + [[GEO]] section Backfire & content quality.

### Bước 4 — Pilot → duyệt → scale (quy trình cứng)

1. **Pilot 10-20 pages** từ template — chọn biến thể data đầy đủ nhất + vài case biên (data mỏng gần ngưỡng).
2. **Đo pilot**: index rate (GSC), initial ranking/impressions các biến thể, spot-check chất lượng render.
3. **Trình Content Leader duyệt template** — deliverable trạng thái **CHỜ DUYỆT: Content Leader** kèm data pilot. Theo quy trình: template phải được Content Leader duyệt TRƯỚC khi nhân bản số lượng lớn.
4. **Scale theo batch** sau duyệt — mỗi batch kèm sitemap riêng + checkpoint index rate trước khi sinh batch kế; template sửa đổi đáng kể sau duyệt → re-approve.

### Bước 5 — Render deliverable & lưu

- Render theo skeleton Output → lưu `05-content-plan/` của instance, naming `{{CLIENT}}_programmatic-spec_<pattern-slug>_v{{N}}.md`.

### Tự phản biện trước khi trình

Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Gate G1–G3 có evidence cho từng tiêu chí. Biến thể fail QDP gate được hạ thành section hoặc component, không sinh trang. Nguồn: ca Doktorsitesi 4M trang không index, xoá đi thì +600K clicks (`wiki/cases/local-seo-sel-cases-2026.md`).
- [ ] G2 có verdict non-commodity và ghi rõ data unique của mỗi page. Nguồn: Google AI optimization guide, test "could easily be produced by a generative AI model".
- [ ] Spec scale có mục 3b: cohort risk gắn nhãn correlational và footprint checklist 5 mục. Nguồn: cohort 220+ domain mất traffic sau khi scale AI content (Lily Ray 05/2026).
- [ ] Spec có min-data threshold, sitemap riêng cho từng batch và nhịp kiểm index rate. Nguồn: [[Index Pollution]], index bloat làm đắt crawl của cả site.
- [ ] Deliverable ghi trạng thái CHỜ DUYỆT Content Leader, và scale plan đứng sau mốc duyệt. Nguồn: `sop/09-timeline/10-thang-thuc-day.md` dòng 7 (bổ sung 05/07/2026).
- [ ] Pattern listicle hoặc comparison có expected return đã chiết khấu. Nguồn: ChatGPT 5.6 cắt citation listicle −50,5% và comparison −32,1% (Peec 08/2026, secondhand).

## Output

```markdown
# <CLIENT> — Programmatic SEO Spec: <pattern>
> Ngày lập: YYYY-MM-DD · DATA TIER: <1/2/3 — nguồn + ngày> · Scale dự kiến: <N> pages
> Trạng thái template: **CHỜ DUYỆT — Content Leader** (chưa duyệt = không nhân bản)

## 1. Gate decision
| Gate | Kết quả | Evidence |
|---|---|---|
| G1 Search demand lặp pattern | PASS/FAIL | |
| G2 Data source unique value | PASS/FAIL | |
| G3 Số lượng đáng làm template | PASS/FAIL | |
→ Verdict: <PROGRAMMATIC | ROUTE CONTENT THƯỜNG (lý do)>

## 2. Template spec
- Page type + intent pattern · Vị trí trong topical map (cụm, Core/Outer)
| Block | E-A-V (Entity · Attributes · Value ← field data) | Bắt buộc? | Unique/Boilerplate |
|---|---|---|---|
- Tỷ lệ unique mục tiêu: ≥30-40%/page · Schema: <loại per page type → schema-markup-generator>
- Internal link pattern: <hub ↔ page ↔ ngang hàng ↔ Core>

## 3. Thin-content & index-bloat controls
- Min-data threshold: <định nghĩa field bắt buộc> · Dưới ngưỡng → <không sinh | noindex>
- Sitemap: <tên sitemap per batch> · Canonical rules biến thể: <quy tắc>
- Index monitoring: <GSC property + nhịp check>

## 3b. Risk disclosure AI-era (bắt buộc khi scale)
- Cohort risk (label correlational, Lily Ray 05/2026, refresh lint quý): 220+ domains AI-scaling → 54%/39%/22% mất ≥30/50/75% peak traffic
- Footprint checklist (5 mục): <PASS/FAIL per mục — dính ≥2 → dừng review>
- Non-commodity test (G2): <verdict + data unique per page là gì>
- Engine note: listicle/comparison citation ChatGPT 5.6 −50,5%/−32,1% (Peec secondhand) — nếu pattern thuộc nhóm này, ghi rõ expected return đã chiết khấu

## 4. Pilot plan
- 10-20 pages: <danh sách biến thể pilot, gồm case biên> · Chỉ số đo: index rate, impressions, initial ranking · Mốc đánh giá: <ngày>

## 5. Scale plan (chỉ chạy SAU duyệt)
- Batch size + thứ tự · Checkpoint index rate giữa các batch · Điều kiện dừng
```

## Behavior Gates

**#1 Think Before** — Chưa thấy sample `$DATA_SOURCE` thật → không spec template. Chưa có plan + research page type → dừng ở Bước 0b. Trước khi gọi MCP: báo số call, chờ xác nhận.

**#2 Evidence** — Gate G1-G3 chấm bằng evidence (volume/SERP/sample data), không chấm bằng cảm giác. Index rate chỉ báo cáo từ data thật (GSC/`site:` mẫu), khai báo DATA TIER; không hard-fail thiếu MCP — Tier 3 luôn chạy được.

**#3 Surgical** — Spec template + control, không viết content, không thiết kế visual, không viết JSON-LD, không audit site — route theo bảng phân vai.

**#4 Gate cứng — Content Leader** — Template **CHƯA DUYỆT = KHÔNG nhân bản số lượng lớn**, không ngoại lệ. Mọi deliverable ghi rõ trạng thái CHỜ DUYỆT cho tới khi user xác nhận Content Leader đã duyệt; scale plan luôn nằm sau mốc duyệt trong mọi bản trình bày.

## Anti-patterns

- ❌ Skip gate rồi thiết kế template vì "pattern trông ngon" — fail gate = route content thường.
- ❌ Nhân bản số lượng lớn khi template chưa có duyệt Content Leader (kể cả "chỉ thêm 50 trang nữa").
- ❌ Sinh page cho biến thể thiếu data ("để trống phần này, bổ sung sau") — dưới min-data threshold là không sinh.
- ❌ Swap mỗi tên địa danh/sản phẩm vào cùng một bài — không đạt unique ≥30-40% = near-duplicate hàng loạt.
- ❌ Đổ toàn bộ page programmatic vào sitemap chính — mất khả năng đọc index rate per batch.
- ❌ Scale toàn bộ một phát sau pilot thay vì theo batch có checkpoint index rate.
- ❌ Coi programmatic là mặc định của mọi dự án / gắn vào timeline cố định — dòng 7 là TÙY DỰ ÁN.
- ❌ Sinh URL riêng cho biến thể filter/sort/param thay vì canonical về biến thể chính.
- ❌ Bỏ qua index rate giảm dần theo batch và tiếp tục sinh — dấu hiệu sớm của [[Index Pollution]].
- ❌ Đặt cụm programmatic ngoài topical map, không internal link về hub/Core — đảo trang mồ côi không chuyển signal.
- ❌ Trình proposal/scale plan programmatic mà KHÔNG kèm block risk disclosure cohort (Bước 3b) — client phải nghe risk trước khi duyệt.
- ❌ Scale template listicle/comparison/FAQ-farm/glossary/location trùng footprint bị flag — kể cả khi pilot đang lên ("Mount AI": spike rồi rơi sau update).
- ❌ Fake-refresh date trên page programmatic để giả freshness — nằm trong footprint bị flag + Google xử như LLM manipulation/spam (04-05/2026).

## References & wiki

**Nguồn quy trình:**
- `sop/09-timeline/10-thang-thuc-day.md` — dòng 7 ma trận content type: template/programmatic TÙY DỰ ÁN, điều kiện triển khai + Content Leader duyệt template (bổ sung 05/07/2026).
- `sop/01-topical-map.md` — chuẩn Core/Outer, internal link signal flow to Core.

**Wiki Semantic SEO (lớp WHY):** [[E-A-V Framework]] · [[Index Pollution]] · [[Cost of Retrieval]] · [[Boilerplate Content]] · [[Page Types]] · [[Core Section]] · [[Outer Section]] · [[Quality Thresholds]] · [[Semantic Content Network]] · [[Initial Ranking]] · [[Non-Commodity Content]] (G2 test) · [[GEO]] (section Backfire & content quality) · [[Best List Page]] (section Backfire risk) · [[sources/ai-content-risks-cohort-lily-ray]] · [[sources/chatgpt-page-type-citation-shift-peec]]

**Skill anh em:** `topical-map-creation` (chọn cụm) · `semantic-content-writing` (nội dung block) · `visual-semantic-seo` (layout PLP/template) · `schema-markup-generator` (markup) · `technical-seo-audit` (index site-level) · `keyword-topic-url-mapping` (đối chiếu URL cam kết)

## Changelog

- **2026-10-27 v1.2** — hợp nhất bản root 27/10/2026: lấy về Bước 3b guardrail AI-era, G2 non-commodity test, mục 3b của output, 3 anti-pattern và 5 wikilink nguồn. Thêm khối chuẩn của skill: Phân việc model, Tự phản biện 6 mục, đổi "## Workflow" thành "## Quy trình", Bước 0 trùng tên thành Bước 0b. Rút description dưới 280 ký tự. Sửa đường dẫn SOP thành `sop/09-timeline/` cho khớp repo.
- **2026-08-22 v1.1** — (Lead duyệt 22/08, nền Batch 39 wiki) thêm lớp guardrail rủi ro AI-era: Bước 3b (risk disclosure cohort 220+ domains 54/39/22% — label correlational Lily Ray 05/2026; pattern "Mount AI"; footprint checklist 5 mục tự kiểm trước launch; engine counter-adjust ChatGPT 5.6 cắt listicle −50,5%/comparison −32,1% — Peec secondhand); Non-commodity test vào G2 (3 traits Unique/Specific/Authentic + test "could easily be produced by a generative AI model" — Google chính chủ); output skeleton thêm mục 3b; +3 anti-patterns (thiếu risk disclosure, footprint flag, fake-refresh date); mọi số AI refresh theo lint quý.
- **2026-07-19 v1.0** — tạo mới: operationalize dòng 7 ma trận content type sop/09 — gate G1-G3 (demand pattern / unique data / scale đáng làm), template spec E-A-V + unique ≥30-40% + internal link + schema per page type, chống thin/index-bloat (min-data, sitemap segmentation, canonical, GSC index rate), quy trình pilot 10-20 → Content Leader duyệt → scale theo batch (gate cứng).
