---
name: seo-onpage
description: "Onpage SEO audit & optimization theo checklist P-series chính chủ GTV (bundled đầy đủ trong references/p-series-checklist.md — standalone, chạy được cả trên claude.ai): P0 Quality Gate + P1-P23 Tier 1 (/23) + T2/T3 (/31 → /39) + AX AI-Search Extension. Use when: (1) 'audit onpage [URL/trang]', 'check onpage', 'tối ưu onpage', 'chấm điểm onpage'; (2) 'pre-publish check' — verify content + meta trước khi lên CMS; (3) 'checklist onpage cho [page type]'; (4) user hỏi về title/meta/CTR/heading/distribution/word relationships/n-gram/internal+external link/schema/alt/Featured Snippet/word sequence/AI Overview cho 1 trang. KHÔNG dùng cho: audit content quality 66pt toàn diện (→ semantic-content-audit); outline mới (→ semantic-outline-methodology); viết bài (→ semantic-content-writing)."
metadata:
  version: "1.2"
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

Skill này CHẤM + CHỈ ĐIỂM (verdict per item + fix hint) — fix sâu route theo bảng.

## Input

**Required (1 trong 3):** `$URL` (Firecrawl scrape markdown+html) · `$HTML`/`$CONTENT` (paste, pre-publish) · `$DRAFT_PATH` (pipeline).

**Optional:** `$TARGET_KEYWORD` + `$INTENT` (thiếu → suy từ H1/title, flag inferred) · `$TIER` (`1` | `1+2` default | `all` | `+AX`) · `$PAGE_TYPE` (informational/commercial/YMYL/e-commerce → bật T2 item tương ứng) · `$SERP_SCREENSHOT` (cho P15 FS + AX3 AIO) · `$AUTHORITY_URLS` (top 1 + authority để so P8 topical coverage + T3-P1 info gain).

## Workflow

### Bước 0 — P0 Content Quality Gate (chặn)
Confirm content đã V-Pass (9 items chất lượng). Khác SEO EX review → scan nhanh. **Chưa pass → HALT, trả về Content**, không onpage.

### Bước 1 — Scope & thu thập
Xác định mode (Audit URL live / Pre-publish). Đọc **[references/p-series-checklist.md](references/p-series-checklist.md)** — load đúng tier theo `$TIER`. Thu thập: title/meta/`<head>`, heading tree, internal + external links + anchors, ảnh + alt, JSON-LD, `<main>/<article>` structure. Mode Audit + `$AUTHORITY_URLS` → pull top 1 để so P8/T3-P1.

### Bước 2 — Chấm Tier 1 (P1-P23)
Chấm ✅/⚠️/❌ + evidence cụ thể (quote đúng title/slug/heading/anchor lỗi). Nhóm:
- **A Meta (P1-P5):** URL, Title (predicate!), Meta, **CTR (Title hook→Meta detail)**, H1 (cùng predicate Title).
- **B Heading (P6-P7):** variations H2/H3/H4 + entity mới, K2Q, Subordinate Match.
- **C Semantic body (P8-P16):** topical coverage ≥70%, EAV density, **Distribution macro/micro**, **Word Relationships 5 loại**, **Co-occurrence + anchor segments**, **N-gram unique/section**, Bold answer, FS, **keyword 100 đầu + 100 cuối**.
- **D Link (P17-P18):** internal bridge/justify, **External link .edu/.gov 2-4/bài + không link đối thủ**.
- **E Image (P19-P20):** filename, alt+caption+tech.
- **F Technical (P21-P23):** semantic HTML5, function/mobile, **chạy Prompt onpage** (xem Bước 4).

### Bước 3 — Tier 2/3 (nếu $TIER ≥ 1+2 / all)
T2 bật theo `$PAGE_TYPE`. T3 cho Quality Node: Info Gain (≥110% facts vs top 1), Schema advanced, CWV, HCU (→ route `semantic-content-audit`), N-gram advanced, UX, **Word Sequence (T3-P7)**.

### Bước 3b — AX AI-Search (nếu $TIER có +AX)
AX1 chunk self-containment · AX2 front-load (30% đầu) · AX3 AIO counter-positioning · AX4 canonical/index · AX5 Blur Test (cần render → không có thì mark "cần visual review").

### Bước 4 — Prompt Tối Ưu Onpage (P23, tùy chọn nhưng khuyến khích)
Chạy 2 bước AI thay "cảm tính":
1. **Extract:** từ content → liệt kê Macro terms, Micro terms/section, Named + Technical entities, LSI, keyword variations, n-grams, facts.
2. **Audit:** topical coverage ≥70% vs top 10? Variations đủ mỗi paragraph? N-gram unique/section? → bổ sung thiếu, loại tràn, ghi note tracking.

### Bước 5 — Report & route

```markdown
# Onpage Audit — [URL/title]
**Mode:** Audit | Pre-publish · **Page type:** … · **Keyword:** …
**Score:** Tier 1 x/23 · Tier 2 y/8 · Tier 3 z/8 · AX: n/5
## P0 Gate: PASS / FAIL (fail → dừng, trả Content)
## Verdict: PASS / PASS-với-fix / FAIL
  (❌ P1/P2/P5/P8/P9 = fail nền → ưu tiên; ❌ P0 = không onpage)
## ❌ Fail (fix trước) — Pxx [tên] · evidence · fix hint · route
## ⚠️ Warning
## ✅ Pass đáng giữ (2-3 điểm mạnh)
## Fix plan ưu tiên (theo impact + tier)
```

Nguyên tắc: **sửa nền trước tối ưu sau** — còn ❌ Tier 1 thì chưa đụng T2/T3/AX.

## Behavior Gates

- **#1 Think Before:** báo scope (mode, tier, page type, artifact có/thiếu) trước khi chấm.
- **#2 Evidence:** mỗi ❌/⚠️ kèm quote/số đếm cụ thể — không phán chung chung.
- **#3 Surgical:** KHÔNG tự sửa trang — output là report + fix plan. Fix theo route.
- **#4 Goal-driven:** mọi item chấm xong nằm trong report; bỏ qua ghi N/A + lý do.

## Anti-patterns

- Chấm T2/T3/AX khi Tier 1 còn ❌ (sai thứ tự impact).
- Bỏ P0 gate → onpage content chưa đạt chất lượng.
- **Quên External Link (P18)** — dễ sót vì bản cũ chỉ lo internal.
- Bold keyword thay vì bold ANSWER (P14/P15).
- Đề xuất schema để "tăng AI citation" — evidence: schema ✗ citation, ✓ rendering/entity ([[Structured Data]], T3-P2).
- Chấm Distribution/N-gram bằng mắt thay vì chạy Prompt P23.
- Tự sửa trang trong lúc audit (vi phạm #3).

## Reference

- **Bundled (đọc khi chạy):** [references/p-series-checklist.md](references/p-series-checklist.md) — full spec P0 → Tier 1/2/3 + AX, kèm data notes Suski 1M SERPs.
- **Nguồn gốc & sync (chỉ để đối chiếu, không bắt buộc khi chạy):** xlsx v5.3 của Vincent (thắng khi xung đột) · wiki `sop/08-onpage-checklist.md` + [[sources/onpage-checklist-final-gtv]] · cross-ref [[Layer 4 Onpage]], [[Distribution Semantics]], [[Featured Snippet]].
- AX evidence: [[sources/research-2026-07-general-summary-summarization]] · [[sources/suski-onpage-llm-signals-cmseo2025]] (per-engine + Core Source).

## Changelog

- **v1.2 (2026-07-04):** STANDALONE — bundle full P-series spec vào `references/p-series-checklist.md` (trước đó bắt đọc `sop/08` ngoài skill folder → gãy trên claude.ai/CP folders); thêm data notes từ Suski 1M SERPs (P6/P8/P9-P10/P14/T3-P2) + per-engine emphasis & Core Source vào AX3. Sync ra root + 4 CP folders (trước chỉ có ở wiki).
- v1.1 (2026-07-04): P-series runner theo xlsx v5.3, P0 gate, Prompt P23, AX extension.
- v1.0 (2026-07-04): bản đầu theo OP-series (retired).
