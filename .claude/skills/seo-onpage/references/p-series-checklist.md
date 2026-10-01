# P-Series Onpage Checklist — Full Spec (bundled, standalone)

> **Bản tự chứa cho skill `seo-onpage`** — đủ để chạy audit ở BẤT KỲ môi trường nào (Claude Code, claude.ai .skill, Content Production folders, agent khác) mà không cần file ngoài skill folder.
>
> **Nguồn gốc & đồng bộ:** distill từ checklist chính chủ GTV `Checklist_Onpage_Semantic_SEO - Final.xlsx` v5.3 (03/2026). Trong wiki Knowledge, bản dành cho người đọc + cross-ref sống ở `sop/08-onpage-checklist.md` và source page `wiki/sources/onpage-checklist-final-gtv.md` — **khi 1 trong 2 bên đổi, phải sync bên kia** (rule ghi ở cả 2 file). Xung đột → xlsx của Vincent thắng.
>
> Data notes 2026-07: từ study Suski 1M SERPs + 50M AIO (wiki: `sources/suski-onpage-llm-signals-cmseo2025`).

## Scoring

- **Tier 1 = P1-P23, chấm /23** — mọi trang publish mới. **P0 = gate, không tính điểm.**
- **Tier 2 = T2-P1..8, +8 → /31** — bật theo loại dự án tại Kickoff (YMYL, e-commerce, SCN, UX…).
- **Tier 3 = T3-P1..8, +8 → /39** — Quality Node / Root-Seed / cạnh tranh cao / senior.
- **AX Extension (AX1-AX7)** — AI-search/GEO, chấm RIÊNG không tính vào /39 (AX7 heading/title/meta ↔ cluster fan-out, bổ sung 29/08/2026).
- Audit trang cũ: chạy Tier 1→3, dừng ở tier có ≥3 item FAIL — **sửa nền trước, tối ưu sau**.
- Review 3 tầng: Self 100% → SEO EX verify → Lead random 25-30% (gap dương lớn = cờ đỏ).

## P0 — Content Quality Gate (điều kiện tiên quyết)

Content phải **V-Pass 9 hạng mục chất lượng content** (self-checklist writing tier-1) TRƯỚC khi onpage. Trong skill: scan nhanh (không phải SEO EX review đầy đủ) — đủ section theo outline, L0 answer-first mỗi H2, E-A-V có thật, không placeholder/lorem, không mâu thuẫn nội bộ, không dilute paragraph, nguồn cite chuẩn, ngôn ngữ đúng brief, media đúng brief. **Chưa pass → HALT, trả về Content** — onpage cho content hỏng = đốt công.

## TIER 1 — P1-P23 (/23)

### A. Chuẩn bị & Meta (P1-P5)

- **P1 URL Structure** — 3-5 từ, gạch ngang, keyword volume cao nhất/đại diện cluster, không dấu tiếng Việt/không ID số, nằm đúng folder theo topical map.
- **P2 Title Tag** — 50-60 ký tự; chứa **Main Predicate** khớp query cluster; keyword chính trong 3 từ đầu; Title KHÁC H1 và KHÁC URL (không copy nhau); Title + H1 **cùng predicate**. *Lens GEO (→ AX7):* title chứa từ vựng của ≥1 cluster fan-out — AI engine lọc ứng viên theo **title + meta + URL** trước khi mở trang (≈ ước tính đơn nguồn, McSweeney 12/2025; benchmark cited title↔fan-out 0,656 Ahrefs 04/2026).
- **P3 Meta Description** — 150-160 ký tự, 1-2 keyword tự nhiên, CTA rõ, ~70% bộ keyword tối ưu xuất hiện trong meta. *Lens GEO (→ AX7):* meta nêu **câu trả lời/facet chính bằng từ vựng cluster**, không chỉ CTA — cùng cổng lọc title+meta+URL.
- **P4 CTR Optimization** — Title dùng hook (tính từ mạnh/số/năm/cảm xúc); Meta mang CTA + value prop; **Title hook → Meta detail, không lặp ý nhau**; cross-check với top 5-10 SERP hiện tại.
- **P5 H1 Optimization** — H1 set Macro Context; **cùng predicate với Title**; chứa Salient Entity; 60-70 ký tự; duy nhất 1 H1; mọi H2 ở trong cùng predicate frame của H1.

### B. Heading & Contextual Vector (P6-P7)

- **P6 Keyword & Variations In Headings** — H2 = keyword chính/attribute chính; H3 = semantic variations + entity chuyên sâu MỚI; H4 = entity cụ thể nhất; mỗi sub-heading thêm ≥1 entity mới. *Data 2022-2024: variations dời xuống H3/H4 — H1 giữ exact/sạch.*
- **P7 Word Order, K2Q & Subordinate** — entity đứng đầu heading; heading dạng question theo K2Q (Definitional/Grouping/Comparative/Boolean) khi query là question; **Subordinate Text Match**: câu đầu dưới heading khớp format heading (What→definition, How→step/method, số→số).

### C. Semantic Keywords & Content Body (P8-P16)

- **P8 Topical Coverage, Entities & LSI** — audit top 10 SERP → bài cover **≥70% facts/entities/LSI** của tập top; đủ Named Entities + Technical Entities. **Yếu tố onpage hiệu quả nhất** *(data: ρ≈0,28 #1 toàn study; top 10 coverage 0,74 vs bottom 0,50)*.
- **P9 EAV Density & Semantic Writing (onpage)** — VERIFY + BỔ SUNG E-A-V trên CMS thực tế (P0 chỉ confirm bản draft); mỗi paragraph ≥1 E-A-V; đúng semantic writing rules. *Chấm bằng ĐẾM TUYỆT ĐỐI câu E-A-V/variations — không dùng % density (density ρ≈0).*
- **P10 Distribution Semantics & KW Variations** — **Macro Terms xuyên suốt toàn bài / Micro Terms CHỈ trong section của nó**; mỗi H2 có bộ semantic riêng. *(Variations in body/paragraphs là content-factor mạnh nhất nhóm — ρ≈0,03; density bét bảng ≈0.)*
- **P11 Word Relationships** — đủ 5 loại: Synonyms (≥3-4, rải xuyên suốt) / Hypernym-Hyponym / Meronym-Holonym / Antonym / Co-hyponym → signal hiểu sâu chủ đề.
- **P12 Word Co-occurrence & Proximity** — Entity + Attribute trong CÙNG câu; modifier đứng ngay trước noun; **Anchor Segments** (lặp key term từ câu trước sang câu sau); Context Qualifiers khi cần điều kiện.
- **P13 N-gram Optimization** — phrase-level (khác P10 word-level); n-gram **unique per section**; macro n-gram (toàn bài) ≠ micro n-gram (per section).
- **P14 Bold Keywords & Variations** — bold CÂU TRẢ LỜI/insight + 2-3 keyword variations quan trọng; KHÔNG bold thuật ngữ đơn thuần; `<em>` cho từ ngoại; ~5-8 bold/1800 ký tự. *Data: keywords-in-bold có tín hiệu, SỐ LƯỢNG bold ≈0 — bold đúng chỗ, không bold nhiều.*
- **P15 Featured Snippet Optimization** — xem FS hiện tại của SERP (dạng, word count); information density ≥ trang đang giữ position-0; format khớp (paragraph/list/table); answer ~40 từ/320 ký tự; bold answer trong L0.
- **P16 Keyword Positions** — keyword chính trong **100 chữ đầu VÀ 100 chữ cuối**; đoạn 2 dùng synonyms (không lặp exact); ≥1 H2 chứa keyword; không nhồi.

### D. Link & Bridge (P17-P18)

- **P17 Contextual Bridge & Internal Link** — bridge heading (How/RQ) chuyển Main→Supplementary; **justify trước khi link** (nhắc/giải thích chủ đề đích ≥1-3 lần trước khi đặt link); anchor khớp Title trang đích; ít link trong Main, nhiều trong Supplementary; 5-10 internal links/bài; có annotation text quanh link.
- **P18 External Link & Blockquote** — 2-4 external links/bài tới .edu/.gov/Wikipedia/peer-reviewed; mở tab mới; `rel="nofollow"` cho affiliate/nguồn không chắc; **KHÔNG external link cho đối thủ**; blockquote đúng chuẩn khi trích.

### E. Hình ảnh (P19-P20)

- **P19 Image File Naming** — ảnh feature đặt tên theo keyword volume cao nhất; các ảnh sau theo keyword phụ/semantic; chữ thường, gạch ngang, không dấu.
- **P20 Alt, Caption & Image Tech** — Alt 8-15 từ = Entity + Attribute + Action + context (không generic, không nhồi); Caption ≠ Alt (thông tin bổ sung); `.webp` ưu tiên, <150KB, max 1200px, `loading="lazy"` dưới fold, width/height explicit (chống CLS).

### F. Technical & Experience (P21-P23)

- **P21 Clean Code & Semantic HTML** — `<main>` duy nhất (weight 100%), `<article>` self-contained (block AI cite), `<section>` đúng, heading hierarchy sạch không nhảy cấp.
- **P22 Function Web, Mobile UX & Creative Function** — mọi CTA/form/filter/calculator HOẠT ĐỘNG (tiêu chuẩn UX và chuyển đổi: chức năng hỏng làm mất chuyển đổi. Không dẫn patent cho ý này: US10565267B1 từng được dẫn là "broken function = negative signal", nhưng patent này xếp hạng bài đăng mạng xã hội theo tốc độ tương tác, không nói về chức năng trang hay hệ số tương tác; fact-fix 28/09/2026 theo wiki Google Leak Decoded); mobile chuẩn; function sáng tạo thỏa intent SERP.
- **P23 Chạy Prompt Tối Ưu Onpage (2 bước)** — Step 1 EXTRACT từ content: Macro terms, Micro terms/section, Named + Technical entities, LSI, keyword variations, n-grams, facts. Step 2 AUDIT: coverage ≥70% vs top 10? variations đủ mỗi paragraph? n-gram unique/section? → bổ sung thiếu, loại tràn, ghi note tracking.

## TIER 2 — Project-specific (T2-P1..8, bật tại Kickoff)

- **T2-P1 YMYL Title & Meta** — qualifier thận trọng, không overclaim, author schema.
- **T2-P2 Visual Semantic Structure** — Centerpiece content ≥60% above-fold, H1 36px+ *(⚠️ citation US8949242B1 trong xlsx là misattribution — patent thật về change detection; nguyên tắc Centerpiece vẫn đúng theo Martin Splitt 2021)*.
- **T2-P3 Dual Measurement** — 2 đơn vị đo cho số liệu (metric + imperial / VND + USD) khi audience cần.
- **T2-P4 E-commerce Format** — Carousel/Table/Filter/Price/Product schema đúng loại trang.
- **T2-P5 Original Media E-E-A-T** — ảnh/video tự chụp, không stock cho review/YMYL.
- **T2-P6 SCN Consistency** — entity naming/keyword/CTA đồng bộ toàn Semantic Content Network.
- **T2-P7 / T2-P8** — label bị cắt trong xlsx, chờ Vincent xác nhận (tạm N/A, ghi chú khi chấm).

## TIER 3 — Advanced / Quality Node (T3-P1..8)

- **T3-P1 Information Gain & UX** — ≥110% facts density vs top 1; original data/tool/calculator.
- **T3-P2 Schema** — basic (plugin) + advanced (sameAs/mainEntityOfPage/additionalType). *Kỳ vọng đúng: schema ✗ ranking correlation (ρ≈0,03) ✗ AI-citation lever (causal test) — ✓ rendering/rich result/entity recognition. Không bán schema như GEO magic.*
- **T3-P3 Core Web Vitals** — LCP <2,5s · INP <200ms · CLS <0,1.
- **T3-P4 People-first/Helpful Content assessment** (tên cũ "Google HCU Audit" — đổi 2026-07-13: helpful content classifier đã tích hợp core systems 03/2024) — 66 điểm Who-How-Why → route skill `semantic-content-audit`.
- **T3-P5 N-gram Advanced** — unique per section, density ≥ top 1, front-load, phục vụ AI Search.
- **T3-P6 UX & UI** — visual hierarchy, readability Flesch grade 6-8, heatmap nếu có.
- **T3-P7 Proper Word Sequence & Phrase Order** — NLP parse trái→phải; front-load; 5 tầng: Heading↔câu đầu / front-load per section / word order per sentence / modifier trước noun / phrase order theo importance.
- **T3-P8** — label bị cắt trong xlsx, chờ xác nhận (tạm N/A).

## AX — AI-Search & GEO Extension (chấm riêng)

- **AX1 Chunk self-containment** — mỗi H2 section tự đứng như answer hoàn chỉnh (đủ entity + context + claim khi cắt rời; không đại từ hồi chỉ xuyên section). **Chuẩn chunk GTV 29/08/2026 — không cap số từ section:** 1 heading = 1 facet · câu đầu sau heading 40-75 từ · mỗi khối ý <~200 từ (observational, Chrome) · mỗi câu tự đứng S-V-O. **Heading tổ tiên có nghĩa** — máy gắn H1/H2 cha vào chunk như metadata (`includeAncestorHeadings`, Google Cloud docs); heading rỗng nghĩa ("Tổng quan", "Kết luận") làm mất lợi thế. Con số chunk theo token (128/800/500) là 3 hệ khác nhau, không dùng làm ngưỡng ([[Audition Chunk]] §"3 con số chunk").
- **AX2 Front-load value** — best content trong 30% đầu trang (44,2% AI citations từ first-30%); không bury the lede; kill storytelling intro.
- **AX3 AIO counter-positioning** — so content vs AI Overview hiện tại: claim AIO miss → cover sâu; format AIO prefer (definition đầu, structured list, E-A-V) → align. **Tinh chỉnh theo engine mục tiêu**: ChatGPT ưu tiên Early Query Confirmation + Intent Alignment + Section Connectivity · AI Mode: General→Specific + Early Query Answer · AIO/Perplexity: rộng đều. Mục tiêu: thành **Core Source** (nguồn được cite lặp lại; Fact Coverage Ratio là biến quyết định; "DR does not matter much").
- **AX4 Canonical & index hygiene** — canonical tự trỏ, không noindex ngoài ý muốn, ĐÃ INDEX (điều kiện vào retrieval pool), featured image indexed.
- **AX5 Blur Test** — screenshot blur 50% vẫn nhận ra topic + function của trang.
- **AX6 Passage-level citation match — linkify 2 pha (bổ sung 08/2026, patent verified 21/08/2026)** — Citation của AIO/AI Mode chạy 2 pha theo patent Google (US11769017B1 + continuation US11886828B1 "Generative summaries for search results" → AIO; US20240289407A1 "Search with stateful chat" → AI Mode; họ độc lập nhưng chung spec linkify/verification): **Pha 1** LLM generate summary GROUNDED trên content các Search Result Documents (SRDs) được chọn; **Pha 2** mỗi portion của summary được verify bằng embedding distance với candidate document — candidate có thể đến từ một search MỚI chạy trên chính portion đó — chỉ linkify (cite) khi distance đủ gần threshold. Hệ quả: **document nuôi summary ≠ document được cite** — bài của bạn có thể nuôi summary nhưng link về bài khác vừa rank tốt vừa gần statement hơn trong embedding space. Check: mỗi passage trả lời trực tiếp 1 sub-query có TỰ ĐỨNG được không (self-contained — đi cùng AX1) + dùng đúng vocabulary của câu trả lời kỳ vọng (match statement ở passage-level, không chỉ rank tốt)?
- **AX7 Heading / title / meta ↔ cluster fan-out (bổ sung 29/08/2026)** — fan-out của query gom **≤4 cluster** (~90%; chỉ ~27% sub-query ổn định giữa các lần chạy — số tuyệt đối không neo); mỗi cluster thuộc Central Search Intent của bài có ≥1 heading khớp câu hỏi con (K2Q khi query dạng câu hỏi) — heading khớp sát → 41% cite vs 30% lệch (Indig × AirOps 04/2026, 815k cặp, B); **title + meta + slug chứa từ vựng cluster** — AI engine lọc ứng viên theo title+meta+URL trước khi fetch (≈ McSweeney 12/2025; benchmark title↔fan-out 0,656, slug natural-language 89,78% vs 81,11% — Ahrefs 04/2026); cluster ngoài CSI → page khác (QDP), không nhồi. Cluster map: skill `geo-fanout-research` hoặc mô phỏng nhanh 8 lens. Map GE-17. Chấm: 3 mức khớp/gần/lệch per cluster + ✅/❌ title/meta.
