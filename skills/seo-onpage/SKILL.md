---
name: seo-onpage
description: "Audit và tối ưu onpage một trang theo checklist P-series GTV (P0 gate, Tier 1–3, AX AI-Search), đo title và meta theo pixel, lấy cụm thiếu từ ngram-semantic-gap. Dùng khi audit onpage [URL], tối ưu onpage, kiểm title hoặc meta bị cắt, pre-publish CMS."
metadata:
  version: "1.8"
---

# SEO Onpage — Audit & Optimization

Chạy **checklist onpage chính chủ GTV** (P-series). **Full spec bundled tại [references/p-series-checklist.md](references/p-series-checklist.md)** — skill tự chứa, chạy được ở mọi môi trường (claude.ai, Content Production, agent khác) không cần file ngoài. Gốc: xlsx v5.3 của Vincent; bản wiki cho người đọc: `sop/08-onpage-checklist.md` + [[sources/onpage-checklist-final-gtv]] (sync 2 chiều, xung đột → xlsx thắng). Skill = runner + scoring; mỗi finding cite `Pxx / T2-Px / T3-Px / AXx`.

**Scoring:** Tier 1 **/23** (P1-P23) → +Tier 2 **/31** → +Tier 3 **/39**. AX (AI-Search) chấm riêng. P0 Content Quality Gate = điều kiện tiên quyết (fail → không onpage).

## Phân vai với skill khác

| Việc | Skill |
|---|---|
| Audit/chấm điểm onpage 1 trang | ✅ Skill này |
| Pre-publish check trên CMS | ✅ Skill này |
| Content quality 66pt (verdict, HCU) | `semantic-content-audit` (= T3-P4) |
| Viết lại intro | `general-summary-introduction` |
| Sửa HTML semantic | `semantic-html-optimization` (= P21) |
| Layout/visual re-design | `visual-semantic-seo` + `sop/07` (= T2-P2) |
| Research SERP/keyword | `seo-research` |
| Ghi fix đã duyệt (title, meta, H1, slug, đoạn văn) lên WordPress có quyền server | `wp-content-review-apply` (qua trang duyệt Duyệt/E); chỉ có REST thì `wp-publish-workflow-kit` |

Skill này CHẤM + CHỈ ĐIỂM (verdict per item + fix hint) — fix sâu route theo bảng.

## Input

**Required (1 trong 3):** `$URL` (Firecrawl scrape markdown+html) · `$HTML`/`$CONTENT` (paste, pre-publish) · `$DRAFT_PATH` (pipeline).

**Optional:** `$TARGET_KEYWORD` + `$INTENT` (thiếu → suy từ H1/title, flag inferred) · `$TIER` (`1` | `1+2` default | `all` | `+AX`) · `$PAGE_TYPE` (informational/commercial/YMYL/e-commerce → bật T2 item tương ứng) · `$SERP_SCREENSHOT` (cho P15 FS + AX3 AIO) · `$AUTHORITY_URLS` (top 1 + authority để so P8 topical coverage + T3-P1 info gain).

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code (`serp_pixel.py`, `ngram.py`) | Đo title và meta theo pixel. Đếm cụm thiếu, cụm GSC, đo bản sửa | dùng: việc đo phải tất định. Ngưỡng title 688 px đúng 138/140 title holdout (`references/title-pixel.md`) |
| EmbeddingGemma 2 | So section trang biến thể với trang gốc | dùng qua `ngram-semantic-gap` lệnh `sections`, chỉ khi trang dùng chung template |
| Jev | Chấm từng item P-series | không dùng: chưa có rubric hiệu chuẩn cho P-series. Claude chấm có trích dẫn. Không gửi query GSC vào Jev |
| GLM Flash | Trích câu | không dùng: skill trích quote bằng cách đọc trang |
| Claude | Chấm P0–P23, T2, T3, AX, đọc bảng số đo, viết fix plan | dùng |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,pillow?,firecrawl?,bs4?,gemma?,gsc?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `pillow`: `serp_pixel.py` tự đo bằng bảng `scripts/arial_widths.json`.
- Thiếu `bs4`, `gemma` hoặc `gsc`: bỏ phần tương ứng của `ngram-semantic-gap` và ghi giới hạn vào report.

### Bước 0b — P0 Content Quality Gate (chặn)
Confirm content đã V-Pass (9 items chất lượng). Khác SEO EX review → scan nhanh. **Chưa pass → HALT, trả về Content**, không onpage.

### Bước 1 — Scope & thu thập
Xác định mode (Audit URL live / Pre-publish). Đọc **[references/p-series-checklist.md](references/p-series-checklist.md)** — load đúng tier theo `$TIER`. Thu thập: title/meta/`<head>`, heading tree, internal + external links + anchors, ảnh + alt, JSON-LD, `<main>/<article>` structure. Mode Audit + `$AUTHORITY_URLS` → pull top 1 để so P8/T3-P1.

### Bước 2 — Chấm Tier 1 (P1-P23)
Chấm ✅/⚠️/❌ + evidence cụ thể (quote đúng title/slug/heading/anchor lỗi). Nhóm:
- **A Meta (P1-P5):** URL, Title (predicate!), Meta, **CTR (Title hook→Meta detail)**, H1 (cùng predicate Title).
  - P2, P3: đo pixel bằng `python3 skills/seo-onpage/scripts/serp_pixel.py measure --title "<title>" --desc "<meta>" --out <W>/pixel.tsv`. Title trên 688 px ghi ⚠️ "bị cắt" kèm cột `hien_thi`. Meta dùng mốc ước lượng 920 px. Nguồn số đo và giới hạn: `references/title-pixel.md`.
  - Title hoặc meta đề xuất cũng đo bằng lệnh này trước khi đưa vào fix plan.
- **B Heading (P6-P7):** variations H2/H3/H4 + entity mới, K2Q, Subordinate Match.
- **C Semantic body (P8-P16):** topical coverage theo attribute consensus, EAV density, **Distribution macro/micro**, **Word Relationships 5 loại**, **Co-occurrence + anchor segments**, **N-gram unique/section**, Bold answer, FS, **Central Entity + keyword trong 100 chữ đầu**.
  - P10, P12, P13 và cụm query GSC: chạy skill `ngram-semantic-gap` (lệnh `page` cho cụm thiếu và cụm riêng so với top SERP, lệnh `gsc` cho cụm query có hiển thị). Không đếm N-gram bằng mắt và không chép logic đếm vào skill này.
- **D Link (P17-P18):** internal bridge/justify, **trích nguồn bằng tên trong câu, không quota link ngoài, không link đối thủ**.
- **E Image (P19-P20):** filename, alt+caption+tech.
- **F Technical (P21-P23):** semantic HTML5, function/mobile, **chạy Prompt onpage** (xem Bước 4).

### Bước 3 — Tier 2/3 (nếu $TIER ≥ 1+2 / all)
T2 bật theo `$PAGE_TYPE`. T3 cho Quality Node: Info Gain (attribute mới so với top 3), Schema advanced, CWV, HCU (→ route `semantic-content-audit`), N-gram advanced, UX, **Word Sequence (T3-P7)**.

### Bước 3b — AX AI-Search (nếu $TIER có +AX)
AX1 chunk self-containment (chuẩn chunk GTV 4 tầng, không cap số từ; heading tổ tiên có nghĩa) · AX2 front-load (30% đầu) · AX3 AIO counter-positioning · AX4 canonical/index · AX5 Blur Test (cần render → không có thì mark "cần visual review") · AX6 passage-level citation match (linkify 2 pha — patent US11769017B1 + US20240289407A1, verified 21/08/2026: document nuôi summary ≠ document được cite; passage phải vừa rank tốt vừa self-contained + đúng vocabulary câu trả lời kỳ vọng) · **AX7 heading/title/meta ↔ cluster fan-out** (bổ sung 29/08/2026: mỗi cluster ≤4 của query có ≥1 heading khớp câu hỏi con — heading khớp sát → 41% cite vs 30% lệch, Indig × AirOps 04/2026 B; title + meta + slug chứa từ vựng cluster vì AI engine lọc ứng viên theo title+meta+URL trước khi fetch, ≈; cluster map lấy từ `geo-fanout-research` hoặc mô phỏng nhanh 8 lens). Map GE: AX1→GE-19 · AX2→GE-16 · AX3→GE-27 · AX4→GE-07 · AX5→GE-25 · AX6→GE-23 · AX7→GE-17.

### Bước 4 — Prompt Tối Ưu Onpage (P23, tùy chọn nhưng khuyến khích)
Chạy 2 bước AI thay "cảm tính":
1. **Extract:** từ content → liệt kê Macro terms, Micro terms/section, Named + Technical entities, attribute, keyword variations, facts. Lấy n-gram từ output `ngram-semantic-gap` ở Bước 2.
2. **Audit:** đủ attribute MANDATORY của consensus top 10? Variations đủ mỗi paragraph? N-gram unique/section? → bổ sung thiếu, loại tràn, ghi note tracking.
3. **Đo bản sửa chữ thân** bằng `ngram-semantic-gap` lệnh `measure` trước khi đưa vào fix plan: `stuffing` rỗng, mỗi cụm trong `unique_lost` có lý do, `gsc_impr_covered_after` không thấp hơn `before`.

### Bước 5 — Report & route

```markdown
# Onpage Audit — [URL/title]
**Mode:** Audit | Pre-publish · **Page type:** … · **Keyword:** …
**Score:** Tier 1 x/23 · Tier 2 y/8 · Tier 3 z/8 · AX: n/7
## P0 Gate: PASS / FAIL (fail → dừng, trả Content)
## Verdict: PASS / PASS-với-fix / FAIL
  (❌ P1/P2/P5/P8/P9 = fail nền → ưu tiên; ❌ P0 = không onpage)
## ❌ Fail (fix trước) — Pxx [tên] · evidence · fix hint · route
## ⚠️ Warning
## ✅ Pass đáng giữ (2-3 điểm mạnh)
## Fix plan ưu tiên (theo impact + tier)
```

Nguyên tắc: **sửa nền trước tối ưu sau** — còn ❌ Tier 1 thì chưa đụng T2/T3/AX.

### Bước 5b — Region Completeness Summary (quy tắc "không bỏ sót yếu tố")

Lead duyệt bước này ngày 30/08/2026. Nguồn: quy tắc "không bỏ sót yếu tố" của Kyle Roof ([references/kyle-roof-philosophy.md](references/kyle-roof-philosophy.md)).

1. Sau khi chấm xong, đếm item ✅/⚠️/❌ theo từng nhóm vùng: A Meta, B Heading, C Semantic body, D Link, E Image, F Technical.
2. Thêm 1 khối vào report theo mẫu dưới.
3. Ưu tiên fix vùng có nhiều ❌/⚠️ nhất trước khi tối ưu sâu một vùng.

```
## Region completeness (quy tắc không bỏ sót — Kyle Roof)
A Meta 4/5 ✅ · B Heading 2/2 ✅ · C Semantic 6/9 (⚠ thiếu: P10 n-gram, P12 co-occurrence)
D Link 1/2 (❌ P18 trích nguồn) · E Image 2/2 ✅ · F Technical 3/3 ✅
→ Vùng trống cần lấp trước: D (trích nguồn), C (n-gram)
```

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Title và meta hiện tại và đề xuất có số px từ `serp_pixel.py`, kèm phần hiển thị khi bị cắt. Nguồn lỗi: SERP 18/10/2026, 28/284 title bị cắt; mốc 580 px của công cụ cũ chỉ là ước lượng.
- [ ] Mỗi cụm đề xuất thêm có hiển thị GSC hoặc df đối thủ từ `ngram-semantic-gap`. Nguồn lỗi: audit trang dịch vụ 18/10, cụm "dịch vụ seo website" có ở 6/7 đối thủ và 3.648 hiển thị nhưng thẻ sửa chỉ đưa cụm vào title và H1 phương án B.
- [ ] Bản sửa chữ thân có kết quả `measure`: `stuffing` rỗng, cụm mất có lý do. Nguồn lỗi: các vòng viết lại trang tiền r9–r13 (10/2026) không đo bản mới.
- [ ] Title và meta đề xuất không có "#1", "hàng đầu", cam kết KPI hay "không TOP không tính phí". Nguồn lỗi: SERP 18/10, title và snippet đối thủ dùng "uy tín #1" và "Cam kết KPI, không TOP không tính phí"; luật root CAM KẾT VÀ BẢO ĐẢM cấm các câu này.
- [ ] Không chấm theo quota đếm số (số link, mật độ keyword, số bold). Nguồn lỗi: v1.4.3 ngày 19/10/2026, Vincent bỏ các chuẩn đếm số không theo Semantic SEO.
- [ ] Query GSC chỉ xử lý local bằng code. Không gửi vào Jev hay API ngoài. Nguồn lỗi: `jev.py` thêm chặn `must_be_empty` ngày 19/10/2026 vì rubric suýt nhận query GSC.

## Behavior Gates

- **#1 Think Before:** báo scope (mode, tier, page type, artifact có/thiếu) trước khi chấm.
- **#2 Evidence:** mỗi ❌/⚠️ kèm quote/số đếm cụ thể — không phán chung chung.
- **#3 Surgical:** KHÔNG tự sửa trang — output là report + fix plan. Fix theo route.
- **#4 Goal-driven:** mọi item chấm xong nằm trong report; bỏ qua ghi N/A + lý do.

## Anti-patterns

- Chấm T2/T3/AX khi Tier 1 còn ❌ (sai thứ tự impact).
- Bỏ P0 gate → onpage content chưa đạt chất lượng.
- **Quên trích nguồn (P18)** — claim có số liệu mà câu không nêu tên nguồn. Không sửa bằng cách thêm link ngoài cho đủ số.
- Bold keyword thay vì bold ANSWER (P14/P15).
- Đề xuất schema để "tăng AI citation" — evidence: schema ✗ citation, ✓ rendering/entity ([[Structured Data]], T3-P2).
- Chấm Distribution/N-gram bằng mắt thay vì chạy Prompt P23.
- Tự sửa trang trong lúc audit (vi phạm #3).

## Reference

- **Bundled (đọc khi chạy):** [references/p-series-checklist.md](references/p-series-checklist.md) — full spec P0 → Tier 1/2/3 + AX, kèm data notes Suski 1M SERPs.
- **Đo pixel (Bước 2, P2/P3):** [references/title-pixel.md](references/title-pixel.md) — lệnh, nguồn số đo, kiểm chứng ngưỡng title. Test offline: `python3 skills/seo-onpage/tests/test_serp_pixel.py`.
- **Nền tư duy (nạp 1 lần đầu phiên):** [references/kyle-roof-philosophy.md](references/kyle-roof-philosophy.md) — Kyle Roof, patent US10540263B1, single-variable testing. File giải thích vì sao checklist có dạng này và là nguồn của Bước 5b.
- **Nguồn gốc & sync (chỉ để đối chiếu, không bắt buộc khi chạy):** xlsx v5.3 của Vincent (thắng khi xung đột) · wiki `sop/08-onpage-checklist.md` + [[sources/onpage-checklist-final-gtv]] · cross-ref [[Layer 4 Onpage]], [[Distribution Semantics]], [[Featured Snippet]].
- AX evidence: [[sources/research-2026-07-general-summary-summarization]] · [[sources/suski-onpage-llm-signals-cmseo2025]] (per-engine + Core Source) · [[AI Mode]] §Linkify/SRD Verification (AX6 — patent 2 pha, verified 21/08/2026).

## Changelog

- **v1.8 (2026-10-27):** hợp nhất bản root 27/10/2026: thêm Bước 5b Region Completeness Summary, `references/kyle-roof-philosophy.md`, câu P1 về URL ngắn và virtual silo trong `references/p-series-checklist.md` (các mục này thuộc bản root v1.5, Lead duyệt 30/08/2026). Ví dụ vùng D của Bước 5b đổi "external link" thành "trích nguồn" cho khớp P18 của v1.4.3. Bản root ghi số v1.6 và v1.7 cho 2 mục v1.4.3 và v1.5.0 dưới đây. Bản này nhảy lên v1.8 để vượt cả 2 dãy số.
- **v1.5.0 (2026-10-19):** Bước 0 kiểm tool. Thêm `scripts/serp_pixel.py` đo title và meta theo pixel (ngưỡng title 688 px Arial 20, holdout 138/140 trên SERP 18/10) và `references/title-pixel.md`. P10, P12, P13 và Prompt P23 trỏ sang `ngram-semantic-gap` (`page`, `gsc`, `measure`). Thêm phân việc model và tự phản biện.

- **v1.4.3 (2026-10-19):** Vincent yêu cầu bỏ chuẩn đếm số không theo Semantic SEO. P18 bỏ quota 2–4 link .edu/.gov; bài nêu tên nguồn trong câu (`internal-linking` link-js D6). P17 bỏ quota 5-10 link mỗi bài và luật anchor khớp Title đích. P16 bỏ keyword ở 100 chữ cuối và trong H2. P3, P8 bỏ ngưỡng ~70%; P8 chấm theo attribute MANDATORY của consensus. P6 bỏ luật H2 chứa keyword chính. P14 bỏ quota bold. P19 đặt tên file theo nội dung ảnh. P20 bỏ ngưỡng 8-15 từ của alt. T3-P1 bỏ ngưỡng 110%, T3-P5 bỏ density, T3-P6 chỉ dùng Flesch cho tiếng Anh. Bỏ nhãn LSI.
- **v1.4.2 (2026-10-17):** bảng phân vai thêm bước ghi fix lên WordPress qua `wp-content-review-apply`.
- **v1.4 (2026-08-29, Vincent duyệt 29/08 — Đợt 3, FINDINGS 22/08 §6-A1/E):** thêm **AX7 heading/title/meta ↔ cluster fan-out** (AX chấm /7; tách khỏi AX3 vốn gánh cả alignment lẫn counter-positioning; map AX7→GE-17, AX3→GE-27); **AX1** bỏ ngưỡng "≤~375 từ" → chuẩn chunk GTV 4 tầng + heading tổ tiên có nghĩa (`includeAncestorHeadings`); **P2/P3** thêm lens GEO: title/meta chứa từ vựng cluster + meta nêu câu trả lời chính (cổng lọc title+meta+URL của AI engine, ≈). `sop/08` v2.1 đồng bộ + `tier-1-geo.md` GE-17 route AX7. Sync p-series ra mọi bản (CP ×5, SEO Production, PROJECTS ×2, wiki).
- **v1.3 (2026-08-22, Vincent duyệt 22/08, nền Batch 39):** thêm **AX6 Passage-level citation match** vào AX Extension (AX chấm /6) — từ cơ chế linkify 2 pha (patent verified 21/08/2026: US11769017B1 + US11886828B1 → AIO · US20240289407A1 → AI Mode, chung spec): Pha 1 summary generate grounded trên SRDs; Pha 2 mỗi portion verify bằng embedding distance với candidate document (có thể từ search MỚI trên chính portion) → chỉ linkify khi đủ gần. Hệ quả: document nuôi summary ≠ document được cite — passage phải vừa rank tốt vừa match statement ở passage-level (self-contained, đúng vocabulary câu trả lời kỳ vọng). Sửa CHỈ bản root skills/seo-onpage/ — các bản sync (CP folders, SEO Production, PROJECTS, runtime mirrors) cập nhật sau theo pipeline sync.
- **v1.2 (2026-07-04):** STANDALONE — bundle full P-series spec vào `references/p-series-checklist.md` (trước đó bắt đọc `sop/08` ngoài skill folder → gãy trên claude.ai/CP folders); thêm data notes từ Suski 1M SERPs (P6/P8/P9-P10/P14/T3-P2) + per-engine emphasis & Core Source vào AX3. Sync ra root + 4 CP folders (trước chỉ có ở wiki).
- v1.1 (2026-07-04): P-series runner theo xlsx v5.3, P0 gate, Prompt P23, AX extension.
- v1.0 (2026-07-04): bản đầu theo OP-series (retired).
