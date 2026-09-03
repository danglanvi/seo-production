# SOP 08 — Onpage SEO Checklist (Cơ bản → Nâng cao)

> Bản đóng gói cho SEO Production — sync từ `SEO wiki nội bộ «Semantic» (ngoài repo) SEO A - Z/sop/08-onpage-checklist.md` ngày 2026-07-17 (vá P14 strong-policy 2026-08-29).
> Bản chưng cất — đã lược evidence/theory; bản đầy đủ ở kho gốc.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

> **Canonical operational = P-series** (P0-P23 + T2-P1..8 + T3-P1..8, scoring /23 → /31 → /39). Đây là bản team chấm điểm trên Tracking sheet; spec đầy đủ ở kho gốc (`Checklist_Onpage_Semantic_SEO - Final.xlsx` v5.3). AX Extension (AI-Search/GEO) chấm riêng. Skill chạy: `seo-onpage`.

## Cách dùng & scoring

1. **P0 — Content Quality Gate (điều kiện tiên quyết):** content chưa V-Pass (9 items chất lượng) thì **KHÔNG onpage** — trả về Content. SEO EX review → scan nhanh gate; chưa pass → gửi lại.
2. **Publish trang mới:** chạy đủ **Tier 1 (P1-P23, chấm /23)**. Tier 2 bật theo loại dự án tại Kickoff (+8 → /31). Tier 3 cho Quality Node / Root-Seed / cạnh tranh cao (+8 → /39).
3. **AX Extension (AI-search):** áp cho trang cần tối ưu GEO/AI Overview — không tính vào /39, chấm riêng.
4. **Audit trang cũ:** chạy Tier 1 → 3, dừng ở tier có ≥3 item FAIL để sửa nền trước. **Sửa nền trước, tối ưu sau.**
5. **Review 3 tầng:** Self 100% → SEO EX verify → Lead random 25-30% (gap dương lớn = cờ đỏ).

---

## TIER 1 — P0–P23 (chấm /23)

**P0 — Content Quality Gate** (điều kiện tiên quyết, không tính điểm)

### A. Chuẩn bị & Meta (P1-P5)

| ID | Check |
|---|---|
| P1 | URL 3-5 từ, gạch ngang, keyword volume cao nhất, không dấu/ID, đúng folder topical map |
| P2 | Title 50-60 ký tự, **Main Predicate** khớp query cluster, keyword chính 3 từ đầu, KHÁC H1+URL |
| P3 | Meta 150-160 ký tự, 1-2 keyword tự nhiên, CTA rõ, ~70% bộ keyword |
| P4 | **CTR: Title hook (tính từ mạnh/số/năm) → Meta detail (CTA/value), không lặp ý; cross-check top 5-10** |
| P5 | H1 Macro Context, **cùng predicate với Title**, Salient Entity, 60-70 ký tự, 1 H1 duy nhất |

### B. Heading & Contextual Vector (P6-P7)

| ID | Check |
|---|---|
| P6 | H2 keyword chính / H3 semantic variations + entity chuyên sâu MỚI / H4 entity cụ thể; mỗi sub-heading ≥1 entity mới; variations dời xuống H3/H4, H1 giữ exact/sạch |
| P7 | Entity đầu heading, K2Q khi query question, Subordinate Match câu đầu khớp format heading |

### C. Semantic Keywords & Content Body (P8-P16)

| ID | Check |
|---|---|
| P8 | Topical Coverage: audit top 10 → cover ≥70% facts/entities/LSI (NeuronWriter/prompt). **Yếu tố onpage hiệu quả nhất** |
| P9 | EAV Density: VERIFY + BỔ SUNG EAV trên CMS thực tế (khác P0); mỗi paragraph ≥1 E-A-V |
| P10 | **Distribution Semantics: Macro Terms xuyên suốt / Micro Terms theo section; mỗi H2 bộ semantic riêng** |
| P11 | **Word Relationships 5 loại: Synonyms (≥3-4) / Hypernym-Hyponym / Meronym-Holonym / Antonym / Co-hyponym** |
| P12 | Co-occurrence (E+A cùng câu) + Proximity + **Anchor Segments** + Context Qualifiers |
| P13 | **N-gram phrase-level: unique per section; macro n-gram ≠ micro n-gram** |
| P14 | Bold câu trả lời + 2-3 keyword variations — bold = thẻ `<strong>`, KHÔNG dùng `<b>` (policy 2026-08-29); KHÔNG bold thuật ngữ, `<em>` từ ngoại, ~5-8 bold/1800 chữ; bold đúng chỗ, không bold nhiều |
| P15 | Featured Snippet: density ≥ top-0, format khớp, ~40 từ/320 ký tự, bold answer L0 |
| P16 | Keyword chính **100 chữ đầu VÀ 100 chữ cuối**; đoạn 2 synonyms; ≥1 H2 keyword |

### D. Link & Bridge (P17-P18)

| ID | Check |
|---|---|
| P17 | Contextual Bridge (How/RQ) Main→Supplement; justify ≥1-3 lần trước link; anchor khớp Title đích; ít link Main; 5-10 internal link/bài |
| P18 | **External Link: .edu/.gov/Wikipedia/peer-reviewed, 2-4/bài, new tab, nofollow affiliate, KHÔNG link đối thủ; Blockquote chuẩn** |

### E. Hình ảnh (P19-P20)

| ID | Check |
|---|---|
| P19 | Feature ảnh keyword volume cao, ảnh sau keyword phụ, gạch ngang viết thường không dấu |
| P20 | Alt 8-15 từ + keyword + context; Caption ≠ Alt; `.webp`, <150KB, max 1200px, `lazy`, W/H explicit |

### F. Technical & Experience (P21-P23)

| ID | Check |
|---|---|
| P21 | Clean Code & Semantic HTML5 (`<main>` weight 100%, `<article>` AI-cite, heading hierarchy sạch) |
| P22 | Function Web (CTA/form/filter hoạt động — function hỏng = tín hiệu âm) + Mobile UX + Creative Function |
| P23 | **Chạy Prompt Tối Ưu Onpage 2 bước: Step 1 extract (macro/micro/entities/LSI/n-gram/facts) → Step 2 audit (coverage ≥70%? variations? n-gram unique?)** |

---

## TIER 2 — Project-specific (T2-P1..8, +8 → /31) · bật tại Kickoff

| ID | Check |
|---|---|
| T2-P1 | YMYL Title & Meta: qualifier, không overclaim |
| T2-P2 | Visual Semantic Structure: Centerpiece ≥60%, H1 36px+ |
| T2-P3 | Dual Measurement |
| T2-P4 | E-commerce Format |
| T2-P5 | Original Media E-E-A-T |
| T2-P6 | SCN Consistency |
| T2-P7 | *(label cắt trong xlsx — chờ Vincent xác nhận)* |
| T2-P8 | *(label cắt trong xlsx — chờ Vincent xác nhận)* |

## TIER 3 — Advanced / Quality Node (T3-P1..8, +8 → /39)

| ID | Check |
|---|---|
| T3-P1 | Information Gain & UX: ≥110% facts vs top 1, original data, calculator |
| T3-P2 | Schema: basic + advanced (sameAs/mainEntityOfPage). Guardrail: schema KHÔNG tăng AI citation — giá trị ở rendering/entity |
| T3-P3 | Core Web Vitals: LCP <2.5s / INP <200ms / CLS <0.1 |
| T3-P4 | People-first/Helpful Content assessment: 66 điểm Who-How-Why → skill `semantic-content-audit` |
| T3-P5 | N-gram Advanced: unique per section, density ≥ top 1, front-load, AI Search |
| T3-P6 | UX & UI: visual hierarchy, Flesch 6-8, heatmap |
| T3-P7 | **Proper Word Sequence & Phrase Order**: Rule 11+23, NLP parse trái→phải, front-load — 5 tầng |
| T3-P8 | *(label cắt trong xlsx — chờ Vincent xác nhận)* |

---

## AX — AI-Search & GEO Extension

> Không tính vào /39. Chấm riêng cho trang cần tối ưu AI Overview / ChatGPT / Perplexity.
> **Canonical checklist GEO:** `sop/06-self-checklist/tier-1-geo.md` v2.0.2 (GE-01…GE-37) — AX1-AX7 là lớp per-page của nó, map: AX1→GE-19 · AX2→GE-16 · AX3→GE-27 · AX4→GE-07 · AX5→GE-25 · AX6→GE-23 · AX7→GE-17. Quy trình 6 điểm chạm: `sop/09-timeline/lop-geo-v2.md`. (Re-sync từ wiki 2026-09-02 — bản trước 07/2026 chỉ có AX1-AX5 và cap 375 từ, đã hết hạn.)

| ID | Check |
|---|---|
| AX1 | **Chunk self-containment** — mỗi H2 section tự đứng như answer hoàn chỉnh (đủ entity + context + claim khi cắt rời; không hồi chỉ xuyên section). **Chuẩn chunk GTV 29/08/2026: không cap số từ section** — 1 heading = 1 facet · câu đầu sau heading 40-75 từ · khối ý <~200 từ · mỗi câu tự đứng; heading hierarchy mạch lạc và mang nghĩa (heading tổ tiên đi kèm chunk như metadata — heading rỗng nghĩa "Tổng quan"/"Kết luận" làm mất lợi thế này) |
| AX2 | **Front-load value** — best content trong 30% đầu trang; không bury the lede; bỏ storytelling intro |
| AX3 | **AIO counter-positioning** — so content vs AI Overview hiện tại: claim AIO miss → cover sâu; format AIO prefer (definition đầu, structured list, E-A-V) → align |
| AX4 | **Canonical & index hygiene** — canonical tự trỏ, không noindex ngoài ý muốn, đã index, featured image indexed (`src:`) |
| AX5 | **Blur Test** — screenshot blur 50% vẫn nhận ra topic + function của trang |
| AX6 | **Passage verifiability** — mỗi claim quan trọng nằm trong passage vừa **rank được** vừa **khớp câu phát biểu** ở mức passage. Citation AIO/AI Mode chạy 2 pha: AI sinh summary từ tài liệu được chọn rồi mới verify từng đoạn bằng khoảng cách embedding trước khi gắn link → **document nuôi summary ≠ document được cite**. Check: passage trả lời 1 sub-query có tự đứng không (đi cùng AX1) + dùng đúng vocabulary của câu trả lời kỳ vọng (patent Google verified 21/08/2026) |
| AX7 | **Heading / title / meta ↔ cluster fan-out** — fan-out của query gom **≤4 cluster** (~90%, chỉ ~27% sub-query ổn định giữa các lần chạy — số tuyệt đối không neo); mỗi cluster thuộc Central Search Intent của bài có ≥1 heading khớp câu hỏi con (K2Q khi query dạng câu hỏi; heading khớp sát cite 41% vs lệch 30%); **title + meta + slug chứa từ vựng cluster** — AI engine lọc ứng viên theo title+meta+URL trước khi fetch; cluster ngoài CSI → page khác (QDP), không nhồi. Cluster map: skill `geo-fanout-research` hoặc mô phỏng nhanh 8 lens. Chấm: 3 mức khớp/gần/lệch per cluster + ✅/❌ title/meta |

**Per-engine emphasis** (tinh chỉnh AX3 theo engine mục tiêu):

| Engine | Ưu tiên |
|---|---|
| ChatGPT | Early Query Confirmation + Intent Alignment + Section Connectivity (E-E-A-T/Author trọng số thấp) |
| AI Mode | General→Specific + Early Query Answer + Section Connectivity |
| AI Overview + Perplexity | Rộng đều mọi chiều |

Mục tiêu cuối: trở thành **Core Source** — nguồn được AI cite lặp lại. Điều kiện nền: trang đã indexed + rank tốt.
