---
name: geo-content-optimization
description: "Audit + rewrite content ĐÃ publish để được AI engines trích dẫn (AI Overviews, AI Mode, ChatGPT, Perplexity) — operationalize AX1-AX5 của sop/08 và 5 Core Levers của GEO.md thành workflow retrievability: chunk audit self-containment, front-load check, heading-query alignment, AIO counter-positioning, retrievability scoring + rewrite đề xuất per chunk. Use when: (1) 'audit GEO cho [URL]', 'tối ưu bài [X] cho AI Overviews', 'vì sao bài [Y] không được ChatGPT cite'; (2) 'rewrite chunk theo GEO cho bài [Z]'; (3) bài đã indexed + rank nhưng chưa được AI cite. Chạy được không cần MCP (user paste content + AI answer là đường lùi); AI-search access chỉ cần cho counter-positioning. KHÔNG dùng cho: chọn prompt tracking / đo citation share (→ geo-tracking-prompt-selection), HTML structure (→ semantic-html-optimization), viết bài mới (→ semantic-content-writing)."
metadata:
  version: "1.0"
---

# GEO Content Optimization — Audit & Rewrite cho AI Citation

Tối ưu content ĐÃ có để thắng ở bước retrieval + chunk selection của AI search (RAG là khung nền chung: query → rewrite/expand → retrieval → chunk selection → generation + citation). Skill này là lớp OPTIMIZE page-level: nhận bài đã indexed + rank, trả về audit + rewrite đề xuất per chunk.

**Upstream:** bài đến từ `semantic-content-writing` / pipeline Content Production, đã publish + indexed. **Downstream:** bàn giao danh sách page đã optimize + target queries + ngày optimize cho `geo-tracking-prompt-selection` đo citation share.

## Phân vai (không lấn sân)

| Việc | Skill |
|---|---|
| Audit + rewrite chunk cho bài ĐÃ có, retrievability scoring | **geo-content-optimization (skill này)** |
| Chọn prompt tracking, funnel TOFU/MOFU/BOFU, matrix e-commerce, KPI/citation share, đo lường sau optimize | → `geo-tracking-prompt-selection` |
| HTML structure (`<article>`, semantic tags, heading hierarchy DOM) | → `semantic-html-optimization` (skill này chỉ FLAG "chunk dính nav/junk", không sửa HTML) |
| Viết bài mới từ đầu | → `semantic-content-writing` / `-ca` |
| Outline mới | → `semantic-outline-methodology` |
| Onpage tổng thể P-series (/23, /39) | → `/seo-onpage` (skill này = operationalize riêng AX Extension, chấm riêng, KHÔNG tính vào /39) |
| Consensus analysis đa competitor cho topic | → `competitor-consensus-content` (AX3 ở đây chỉ so với AI answer hiện tại) |
| Backlink / authority signals | → `backlink-research` + `backlink-plan` |
| Ảnh / visual semantic (AX5 chỉ pass/fail rồi trỏ đi) | → `image-seo-optimize`, `visual-semantic-seo` |

## Input

**Required:**
- `$TARGET` — URL bài đã publish HOẶC content paste trực tiếp (markdown/text đầy đủ heading).
- `$QUERIES` — 1-5 target queries chính mà bài muốn được AI cite.

**Optional:**
- `$AI_ANSWERS` — AI answer hiện tại cho $QUERIES (per engine), dùng cho Bước 4.
- `$ENGINE` — engine ưu tiên (AIO / AI Mode / ChatGPT / Perplexity). Mặc định: audit chung, note per-engine emphasis.
- `$RANK_STATUS` — vị trí organic hiện tại của $TARGET cho $QUERIES.

**Path detection (data ngoài):**

1. **Content của $TARGET:**
   - Path A (ưu tiên): fetch URL bằng web fetch hoặc Firecrawl → markdown.
   - Path B: user paste toàn văn (giữ nguyên heading structure).
2. **$RANK_STATUS (gate Bước 0):**
   - Path A: Ahrefs MCP (`site-explorer-organic-keywords` / `serp-overview`) — báo số call trước khi gọi.
   - Path B: user export GSC / Ahrefs.
   - Path C: user tự xác nhận "bài đã page-one cho query X" — chấp nhận, ghi chú "rank status: user-confirmed".
3. **$AI_ANSWERS (Bước 4 — tầng ⚙ governance):**
   - Path A: AI-search access nếu có cấu hình.
   - Path B: user tự hỏi ChatGPT/Google rồi paste answer + ngày hỏi.
   - Path C: không có answer → BỎ QUA Bước 4, ghi rõ trong report "counter-positioning: skipped — chưa có AI answer hiện tại", các bước khác vẫn chạy đủ.

## Workflow

### Bước 0 — Gate điều kiện nền + scope confirm

🔴 **Điều kiện nền:** page phải indexed + rank được (tối thiểu page-one của MỘT sub-query nào đó). Retrieval rank là predictor mạnh nhất — position 0 trong retrieval set = 58% citation vs position 10 = 14% (Indig 04/2026); "Classic SEO enables AI rankings". Page chưa rank → ROI thấp — mặc định trả về pipeline SEO thường (`/seo-onpage`, topical map); chỉ audit tiếp khi user chấp nhận caveat. Ngoại lệ đã biết (decoupling do fan-out long-tail + freshness): 28,3% cited pages có 0 organic keywords (GEO.md); 36,7% cited URLs ngoài top-100 ([[AI Overviews]]) — exception, không phải kế hoạch mặc định.

⚠ Ngưỡng "đủ điều kiện dự thi" là page-one presence, KHÔNG cần #1: chất lượng snippet phẳng từ rank 1→10 (drop ~2%, Dejan 2026) — page-one = pooled source list.

Checklist trước khi chạy:
- [ ] $TARGET indexed + rank status xác nhận (Path A/B/C).
- [ ] $QUERIES chốt (1-5). Query dạng nào? Ưu tiên effort theo AIO trigger model: Informational/question/7+ từ = xác suất AIO cao nhất (bảng rút gọn trong [references/geo-levers-map.md](references/geo-levers-map.md)).
- [ ] Nếu gọi MCP: báo số call dự kiến (thường 1-3 call Ahrefs), **chờ user xác nhận**.
- [ ] $AI_ANSWERS có chưa? Không có → hỏi user muốn paste hay skip Bước 4.

### Bước 1 — Chunk audit: self-containment (AX1)

Tách bài thành chunk theo H2/H3 (heading = extraction boundary tự nhiên — Dejan khuyến nghị nguyên văn). Chấm từng chunk theo rubric trong [references/chunk-audit-method.md](references/chunk-audit-method.md):

- **Kích thước:** mỗi H2 section ≤~375 TỪ (sop/08 AX1; ≈500 tokens). ⚠ SOP canonical ghi "từ", không phải tokens — muốn đổi đơn vị phải Vincent duyệt.
- **Tự đứng:** chunk cắt rời khỏi bài vẫn đủ Entity + context + claim để trả lời trọn 1 sub-query (AI Mode retrieve ở passage-level, fan-out ~8-12 sub-queries — mỗi sub-query cần 1 passage tự đứng).
- **Không đại từ hồi chỉ:** "điều này", "như đã nói ở trên" → chunk mất context khi bị cắt.
- **Câu 1 sau heading = câu trả lời heading** (Subordinate Text Match — 5 anti-patterns + bảng heading-type → L0 pattern trong reference).

Output bước này: bảng chunk × điểm self-containment × verdict (PASS / REWRITE / TÁCH PAGE).

### Bước 2 — Front-load check (AX2)

- **First 100-150 từ main content = audition chunk target:** answer-first, không filler — đây là chunk cosine cao nhất đại diện toàn page trước cửa Deep Reading; nếu là nav/junk/vòng vo → page bị loại dù thân bài hay ([[Audition Chunk]]).
- Manual proxy khi không có embedding: đếm overlap key terms của Semantic Query trong 100-150 từ đầu — **≥5/10 pass, <3/10 rewrite** ([[Audition Chunk]] In Practice — Manual audit).
- **Best content trong 30% đầu trang:** 44,2% AI citations đến từ first-30% (Indig 02/2026; patent US9940367B1).
- Keyword chính xuất hiện trong 100 chữ đầu VÀ 100 chữ cuối (sop/08 P16).
- ✅ "Kill the storytelling intros" (Indig 02/2026, theo sop/08 AX2) — ⚠ trừ narrative niches (travel/lifestyle): đây là Open Question, không áp máy móc 100%.

### Bước 3 — Heading-query alignment (AX3 — phần alignment)

1. **Fan-out simulation:** sinh 8-12 sub-queries cho mỗi $QUERY theo lens (định nghĩa / so sánh / how-to / chi phí / đối tượng...). Default 8-12 theo Google AI Mode; số của ChatGPT mâu thuẫn giữa nguồn (~2 đến 4-20) — ghi caveat, không cam kết.
2. **Cosine heading ↔ query:** ≥0,90 = excellent (41% citation) / 0,80-0,90 = pass / <0,50 = fail (30% citation) — dùng DẢI, không 1 cutoff (threshold pass/fail chính xác chưa tồn tại). Không có embedding tool → manual proxy trong reference. ⚠ Embedding benchmarks đều đo tiếng Anh (bge-base-en-v1.5, embeddinggemma) — threshold cho tiếng Việt chưa validated, label "estimate" khi áp cho content Việt.
3. **Title ↔ fan-out queries:** benchmark cited 0,656 — match sub-questions NỘI BỘ của AI quan trọng hơn match query gốc. ChatGPT gatekeep trên Title + Snippet + URL trước khi mở page (~50% retrieved URLs mới được cite).
4. **URL slug natural-language:** citation 89,78% vs 81,11% khi không có. Slug đổi được không? (cân nhắc redirect cost — chỉ đề xuất khi page mới/traffic thấp).
5. **Page spec check:** 500-2.000 từ + 7-20 subheadings, heading match trực tiếp query (Indig).

🔴 **Không đẩy về ultimate guide:** page cover 26-50% subtopics THẮNG page cover 100% (100% chỉ +4,6pp vs 0%). Nếu bài cover quá rộng / heading dàn trải → đề xuất TÁCH page, không đề xuất bổ sung sections "cho đủ coverage". Coverage ở cấp network, focus ở cấp page — "build the page that is the best answer to one question".

### Bước 4 — AIO counter-positioning (AX3 — phần consensus-gap)

Cần $AI_ANSWERS (Path A/B/C ở Input). Có answer thì:

1. **Extract facts** trong AI answer hiện tại → danh sách facts + nguồn được cite.
2. **Fact coverage check:** bài mình cover được bao nhiêu facts đó? Mục tiêu = Core Source: Fact Coverage Ratio phân biệt mạnh nhất — 0,42 (core) vs 0,34 (non-core) vs 0,23 (uncited); "DR does not matter much".
3. **Consensus-gap:** góc/thuộc tính nào AI answer hiện tại THIẾU mà nguồn đáng tin có? → bổ sung để vừa cover consensus vừa vượt (lý do AI cite thêm mình).
4. **GEO paper tactics (KDD 2024)** khi rewrite: Cite Sources + Quotation Addition + Statistics Addition = top-3 (visibility tới ~40%); site rank thấp hưởng lợi nhiều nhất (+115%). Keyword stuffing vô dụng/âm.
5. **Per-engine emphasis** nếu $ENGINE chỉ định (bảng trong [references/geo-levers-map.md](references/geo-levers-map.md)): ChatGPT → Early Query Confirmation + Intent Alignment + Section Connectivity; AI Mode → General→Specific + Early Query Answer + Section Connectivity; AIO/Perplexity → rộng đều. ⚠ Per-engine cited-source patterns KHÔNG ổn định (chỉ 2,37% URLs được cả 3 engine cite, 91% single-engine) — emphasis nhẹ, không optimize cứng theo 1 engine.

### Bước 5 — Retrievability scoring + rewrite đề xuất

1. **Scorecard tổng per page** (chi tiết + trọng số trong [references/chunk-audit-method.md](references/chunk-audit-method.md)) — weighted theo thứ tự sức mạnh predictor: rank status → heading-query match → chunk quality (self-containment + front-load) → freshness → KDD tactics.
2. **Rewrite đề xuất per chunk** — CHỈ chunk verdict REWRITE/TÁCH, giữ nguyên chunk PASS (surgical). Mỗi rewrite: passage trả lời sweet spot 100-170 từ (AIO cited passages phổ biến 134-167 từ; 62% trong dải 100-300 từ), khối coherent 200-300 từ khi cần dài hơn; câu 1 = answer; đúng pattern L0 theo heading-type.
3. **Freshness lever:** 76,4% top cited pages update trong 30 ngày (GEO.md, giữ đúng số) + cơ chế `URL_freshness_score` (Yeşilyurt) → đề xuất chu kỳ update thật. 🔴 KHÔNG date-spoofing — fake refresh date = LLM manipulation, Google 04-05/2026 xử như spam.
4. **AX4 (canonical/index hygiene) + AX5 (Blur Test):** chấm pass/fail nhanh; AX4 fail → `/seo-onpage` (evidence [[Index Partition]]); AX5 fail → `sop/07-visual-semantic.md` B7 / `image-seo-optimize`. Không mở rộng ở đây.
5. **TTFB note-only:** target <700ms, ideal <200ms, hard timeout 2s (Gate #2 ChatGPT Pipeline — đơn nguồn, label "reverse-engineered estimate"). Ghi vào report mục Notes, KHÔNG thuộc scope sửa của skill này.

### Bước 6 — Bàn giao đo lường

Đóng gói cho `geo-tracking-prompt-selection`:
- Danh sách page đã optimize + target queries + ngày optimize + engine ưu tiên.
- Baseline: AI answer hiện tại (nếu có ở Bước 4) + rank status.
- Nhắc nguyên tắc đo: AIO bề mặt đổi mỗi ~2,15 ngày nhưng semantic stability 0,95 — thắng TOPIC chứ không thắng query, đo aggregate AI Share of Voice; AIO ≠ AI Mode (chỉ 13,7% citation overlap) → track 2 kênh riêng.

## Output

File: `<project>_GEO-Audit_v1.md` (tăng `_v2`, `_v3` nếu trùng) — trả về `Deliverables/<project>/` theo TASK ROUTING.

```markdown
# GEO Audit — <page title>
> URL: <url> | Ngày audit: <YYYY-MM-DD> | Target queries: <q1; q2...>
> Rank status: <page-one cho query X — nguồn: Ahrefs/GSC/user-confirmed> | Engine ưu tiên: <AIO/AI Mode/ChatGPT/Perplexity/chung>

## 1. Retrievability Scorecard
| Trục | Trọng số | Điểm | Ghi chú |
|---|---|---|---|
| Rank status (gate) | — | PASS/FAIL | <nguồn + ngày> |
| Heading↔query alignment | 30% | x/10 | best cosine <n> / proxy <n>/10 terms |
| Chunk quality (AX1+AX2) | 30% | x/10 | <n>/<m> chunks PASS |
| Freshness | 20% | x/10 | last update <ngày> |
| Tactics KDD (stats/quotes/cites) | 20% | x/10 | |
| **Tổng** | | **x/10** | |

## 2. Chunk Audit (AX1 + AX2)
| # | Heading | Số từ | Self-contain | Câu 1 = answer | Verdict |
|---|---|---|---|---|---|
| 1 | <H2...> | 320 | ✅ | ❌ hedge-words | REWRITE |

### Front-load
- First 100-150 từ: <PASS/REWRITE> — overlap <n>/10 key terms
- 30% đầu trang: <nhận xét> | P16 đầu-cuối: <✅/❌>

## 3. Alignment (AX3)
- Fan-out sub-queries (8-12): <danh sách>
- Heading↔query: <bảng heading → best sub-query → cosine/proxy → dải>
- Title: <hiện tại> → <đề xuất — so với mean cited 0,656 (tham chiếu, không phải cutoff)> | Slug: <natural-language ✅/❌ + khuyến nghị>

## 4. Counter-positioning (nếu có AI answer)
- AI answer ngày <d>, engine <e>: facts = <list>
- Fact coverage của bài: <n>/<m> | Gap bổ sung: <list>
- Tactics thêm: <statistics / expert quote / cite nguồn — cụ thể>

## 5. Rewrite đề xuất per chunk
### Chunk <n> — <heading>
- Vấn đề: <anti-pattern nào>
- Rewrite (100-170 từ, câu 1 = answer): <đoạn đề xuất>

## 6. Ngoài scope — trỏ đi
- [ ] HTML/nav junk trong chunk → semantic-html-optimization
- [ ] AX4 canonical/index: <PASS/FAIL> → /seo-onpage
- [ ] AX5 Blur Test: <PASS/FAIL> → image-seo-optimize
- [ ] TTFB: <n>ms (note-only, estimate đơn nguồn)

## 7. Bàn giao đo lường → geo-tracking-prompt-selection
- Pages + queries + ngày optimize + baseline
- Chu kỳ re-update đề xuất: <30 ngày...> (update thật, không spoof date)

## Nguồn số liệu
<mỗi con số dùng trong report: nguồn + ngày — vd "58%/14%: Indig 04/2026">
```

## Behavior Gates

1. **#1 Think Before** — Bước 0 là gate ưu tiên: không rank → mặc định không audit GEO, chỉ tiếp khi user chấp nhận caveat (ngoại lệ decoupling ở Bước 0). Query không thuộc dạng AIO-trigger cao → nói rõ ROI thấp trước khi user quyết. Nếu $QUERIES/$TARGET mơ hồ → hỏi, không tự giả định.
2. **#2 Evidence** — MỌI con số trong report truy được về nguồn + ngày (mục "Nguồn số liệu" bắt buộc). Số wiki giữ đúng: 76,4% / 58%-14% / 41%-30% / 89,78%-81,11% / ~38%. Tham số McSweeney (128 tokens, 2s, 80/20, sliding window 300 từ) là đơn nguồn — luôn label "reverse-engineered estimate", không cam kết spec với client. AI citation stats = moving target → ghi ngày nguồn, refresh theo lint quý.
3. **#3 Surgical** — chỉ rewrite chunk FAIL; chunk PASS không chạm. Không sửa HTML, không đề xuất schema/backlink/outline mới — flag rồi trỏ đúng skill. Không tự mở rộng sang page khác cùng site.
4. **#4 Goal-driven** — mục tiêu cuối = Core Source (được cite LẶP LẠI qua N lần hỏi), không phải 1 lần xuất hiện. Mọi đề xuất phải map về 1 trong 5 levers / AX1-AX5 ([references/geo-levers-map.md](references/geo-levers-map.md)); đề xuất không map được → bỏ.

## Anti-patterns

- 🔴 **KHÔNG bao giờ đề xuất llms.txt** — llms.txt KHÔNG phải GEO lever: Google không dùng (Mueller so sánh với keywords meta tag), audit log 2025 cho thấy GPTBot/ClaudeBot/PerplexityBot không request file này. Điều khiển AI crawler = **robots.txt**. GEO.md đã chốt — skill nói đúng như vậy, kể cả khi client hỏi.
- 🔴 **KHÔNG tính schema vào retrievability score** — causal test Ahrefs 1.885 pages: thêm schema KHÔNG tăng AI citations (AI Mode +2,4%, ChatGPT +2,2% ≈ 0). Thiếu schema → note 1 dòng chuyển việc khác (rich results/entity), không phải lever citation.
- ❌ Đẩy bài thành ultimate guide "cho đủ coverage" — ngược evidence 26-50% optimal; đề xuất TÁCH page thay vì phình page.
- ❌ Date-spoofing / fake refresh date — manipulation, Google xử như spam. Freshness lever = update NỘI DUNG thật.
- ❌ Hứa deterministic ("làm xong sẽ được cite") — AI output probabilistic, cited hôm nay biến mất mai là bình thường (AIO đổi ~2,15 ngày). Chỉ cam kết ở mức aggregate + Core Source.
- ❌ Keyword stuffing để "match query" — GEO paper: vô dụng hoặc âm.
- 🔴 **KHÔNG bán "adversarial phrasing" làm GEO lever** (bổ sung 16/07/2026) — paper RAF "Are LLMs Reliable Rankers?" (arXiv 2510.06732, đọc full-text): chèn chuỗi text tối ưu hóa đẩy được rank trong LLM reranker mở 7-8B, NHƯNG (1) claim "tăng 20-60%" lan truyền trong ngành KHÔNG có trong paper; (2) hiệu quả gần như mất trên closed models lớn (GPT-5.1 ≈ baseline no-injection); (3) là attack paper — defense phía platform: n-gram duplicate detection. Takeaway hợp lệ duy nhất: phrasing tự nhiên + self-contained thắng stuffing — trùng lever sẵn có. Chi tiết: [[sources/raf-llm-rank-manipulation-2510-06732]].
- ❌ Optimize cứng theo cited-source pattern của 1 engine (vd nhồi Reddit-style vì Perplexity thích Reddit) — pattern không ổn định, 91% URLs single-engine.
- ❌ Cắt storytelling intro máy móc cho narrative niches — gates là SERP-intent-conditional.
- ❌ Sửa HTML/DOM, viết bài mới, chọn prompt tracking — việc của skill khác (xem bảng phân vai).

## References & wiki

- [references/chunk-audit-method.md](references/chunk-audit-method.md) — cách tách chunk, bảng chunk size đa hệ, rubric self-containment, Subordinate Text Match patterns, manual cosine proxy, scorecard.
- [references/geo-levers-map.md](references/geo-levers-map.md) — map 5 Core Levers ↔ AX1-AX5 ↔ hành động; per-engine emphasis; AIO trigger table; bảng "KHÔNG phải lever".
- SOP: `sop/08-onpage-checklist.md` (AX1-AX5 canonical + P16), `sop/07-visual-semantic.md` (Blur Test B7 — AX5).
- Wiki: [[Retrieval-Augmented Generation]], [[ChatGPT Pipeline]], [[Audition Chunk]], [[AI Mode]], [[Query Fan-Out]], [[AI Overviews]], [[Core Source]], [[Subordinate Text Match]], [[GEO]], [[sources/shorter-focused-content-wins-chatgpt-indig]], [[sources/why-chatgpt-cites-one-page-over-another-ahrefs]].
- Web (mới hơn wiki, ứng viên ingest): Dejan "In AI SEO #10 is the new #1" (https://dejan.ai/blog/in-ai-seo-10-is-the-new-1/); iPullRank "A Refutation of Misinformation about Chunking" (https://ipullrank.com/misinformation-about-chunking) — backing lý luận khi client phản biện "Google bảo cứ viết tự nhiên".

## Changelog

- **v1.0.1 (2026-07-16):** thêm anti-pattern 🔴 adversarial phrasing (RAF paper full-text — 20-60% không có thật, GPT-5.1 miễn nhiễm, dual-use caution); nguồn [[sources/raf-llm-rank-manipulation-2510-06732]] (Batch 32).
- **v1.0 (2026-07-07):** khởi tạo — operationalize AX1-AX5 (sop/08) + 5 Core Levers (GEO.md) thành workflow audit + rewrite 6 bước; nguồn nền: wiki AI-systems pages (ChatGPT Pipeline, Audition Chunk, AI Mode, Query Fan-Out, AI Overviews, Core Source, RAG) + Ahrefs/Indig 04/2026 + GEO paper KDD 2024 + web refresh Dejan/iPullRank 2026.
