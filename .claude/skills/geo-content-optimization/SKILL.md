---
name: geo-content-optimization
description: "Audit và đề xuất rewrite bài đã có theo GEO: chấm Bộ BÀI GE-16…27, cấu trúc đoạn, heading, nguồn và nội dung riêng. Dùng khi audit GEO một URL, spot-check nội dung hoặc tối ưu bài để AI dễ đọc và trích."
compatibility: "Gói skill kèm references. Router geo-audit cần bundle 5 skill mảng; chế độ audit nhận evidence dán/export hoặc công cụ đọc phù hợp."
metadata:
  version: "1.5.1"
---

# GEO Content Optimization — Audit & Rewrite cho AI Citation

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

Tối ưu content ĐÃ có để thắng ở bước retrieval + chunk selection của AI search (RAG là khung nền chung: query → rewrite/expand → retrieval → chunk selection → generation + citation). Skill này là lớp OPTIMIZE page-level: nhận bài đã publish; triển khai hàng loạt cần gate nền đạt, chẩn đoán vẫn nhận bài chưa đủ bằng chứng index/rank và ghi UNKNOWN theo phạm vi; trả về audit + rewrite đề xuất per chunk.

**Upstream:** bài đến từ `semantic-content-writing` / pipeline Content Production, đã publish + indexed. **Downstream:** bàn giao danh sách page đã optimize + target queries + ngày optimize cho `geo-tracking-prompt-selection` đo citation share.

**Vị trí trong quy trình:** điểm chạm **G3 Passage architecture** của `sop/09-timeline/lop-geo-v2.md` — chạy SAU khi gate **G-ENT [GEO]** pass khi triển khai hàng loạt; spot-check chẩn đoán vẫn chạy và ghi gate chưa đạt; skill này = lớp audit + rewrite 1 trang, chấm **Bộ BÀI /12 (GE-16…GE-27)** của `sop/06-self-checklist/tier-1-geo.md`. **2 chế độ:** *spot-check* (tick /12, không rewrite — mục dưới) · *full* (Workflow 6 bước + rewrite). Bộ NỀN (GE-01…15) không chấm lại ở đây.


**Trước khi chấm GEO:** nếu chưa nạp hợp đồng v1.1 trong phiên, đọc `references/audit-contract.md` (bản đóng gói): UNKNOWN khác N/A, điểm nhị phân + độ phủ, gate theo URL/engine và bàn giao finding. Quy tắc v1.1 này áp cho các bảng audit GEO bên dưới; changelog chỉ là lịch sử.

## Phân vai (không lấn sân)

| Việc | Skill |
|---|---|
| Audit + rewrite chunk cho bài ĐÃ có, retrievability scoring | **geo-content-optimization (skill này)** |
| Audit chất lượng semantic tổng thể (66 điểm + Humanness) + **gate G-BÀI 4 item** (GE-16…19) | → `semantic-content-audit`; hai skill chia sẻ 4 check (câu 1 = answer, L0, heading hierarchy, citation sau claim). SCA = verdict chất lượng + gate; skill này = Bộ BÀI /12 (spot-check) và "vì sao không được cite" + rewrite (full) |
| Chọn prompt tracking, funnel TOFU/MOFU/BOFU, matrix e-commerce, KPI/citation share, đo lường sau optimize | → `geo-tracking-prompt-selection` |
| HTML structure (`<article>`, semantic tags, heading hierarchy DOM) | → `semantic-html-optimization` (skill này chỉ FLAG "chunk dính nav/junk", không sửa HTML) |
| Viết bài mới từ đầu | → `semantic-content-writing` / `-ca` |
| Outline mới | → `semantic-outline-methodology` |
| Onpage tổng thể P-series (/23, /39) | → `/seo-onpage` (skill này = operationalize riêng AX Extension, chấm riêng, KHÔNG tính vào /39) |
| Consensus analysis đa competitor cho topic | → `competitor-consensus-content` (AX3 ở đây chỉ so với AI answer hiện tại) |
| Backlink / authority signals | → `backlink-research` + `backlink-plan` |
| Ảnh / visual semantic (AX5 chỉ pass/fail rồi trỏ đi) | → `image-seo-optimize`, `visual-semantic-seo` |
| Gate G-T1 + Bộ NỀN kỹ thuật (bot 3 tầng, index, trang đọc được bằng máy) · Bộ OFFSITE · scorecard 6 điểm chạm | → `geo-technical-audit` · `geo-offsite-audit` · `geo-audit` (router gọi skill này ở chế độ spot-check) |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| EmbeddingGemma 2 | Cos heading và section ↔ subquery; so trang mình với trang trong cùng top 10 | dùng qua skill `geo-fanout-research` Bước 4a: `mean_best` trong top 10 có AUC 0,674 dev, 0,683 holdout (19/10/2026). Không có ngưỡng phủ tuyệt đối, nên Claude ra verdict |
| Jev | Chấm chunk tự đứng, câu trả lời ở màn đầu | không dùng trong skill này: rubric chunk tự đứng chưa hiệu chuẩn. Màn đầu chấm bằng Jev ở skill `visual-serp-lab` |
| GLM Flash | Trích facts từ câu trả lời AI ở Bước 4 | không dùng: Claude trích facts của vài câu trả lời. Trích hàng loạt thuộc skill `geo-answer-lab` |
| Claude | Chunk audit, đọc section cos thấp, counter-positioning, viết rewrite | dùng |

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
2. **$RANK_STATUS (gate Bước 0b):**
   - Path A: Ahrefs MCP (`site-explorer-organic-keywords` / `serp-overview`) — báo số call trước khi gọi.
   - Path B: user export GSC / Ahrefs.
   - Path C: user tự xác nhận "bài đã page-one cho query X" — chấp nhận, ghi chú "rank status: user-confirmed".
3. **$AI_ANSWERS (Bước 4 — tầng ⚙ governance):**
   - Path A: AI-search access nếu có cấu hình.
   - Path B: user tự hỏi ChatGPT/Google rồi paste answer + ngày hỏi.
   - Path C: không có answer → BỎ QUA Bước 4, ghi rõ trong report "counter-positioning: skipped — chưa có AI answer hiện tại", các bước đủ evidence vẫn chạy; GE-27 UNKNOWN nếu thuộc scope, không tự N/A chỉ vì thiếu AI answer.

## Chế độ spot-check — Bộ BÀI /12 (tick-only, v1.3)

Dùng khi chỉ cần biết bài **đứng ở đâu** trên 12 item passage architecture (audit định kỳ, bài trọng điểm, sau khi `semantic-content-audit` báo gate G-BÀI) — không scorecard, không rewrite. Dùng bảng GE-16…27 tự chứa dưới đây (derive master v2.0.3 + chuẩn content đã chốt 29/08/2026); wiki/SOP chỉ để bảo trì. Đọc hợp đồng audit: UNKNOWN giữ trong mẫu số áp dụng, báo độ phủ; 4 item đầu = G-BÀI.

| GE | Check nhanh (PASS/PARTIAL/FAIL/UNKNOWN/N/A) | Gate |
|---|---|---|
| GE-16 | 100-150 từ đầu main content = câu trả lời thẳng, không storytelling intro (ngoại lệ narrative niche); bài informational chính có Key-Facts table | G-BÀI |
| GE-17 | Heading = câu hỏi thật của user; bài gánh đúng 1 câu hỏi chính (≥2 → đề xuất tách page); cluster fan-out có heading cover; không chấm độ dài/số heading theo dải cố định (độ dài theo loại node + benchmark đối thủ) | G-BÀI |
| GE-18 | Câu đầu sau MỌI heading = câu trả lời đúng pattern (định nghĩa/how-to/so sánh/yes-no), 40-75 từ theo chuẩn GTV, đủ E-A-V; giữ điều kiện/độ bất định cần thiết để câu đúng | G-BÀI |
| GE-19 | Mỗi H2 cắt rời vẫn đủ Entity + context + claim; không "như đã nói ở trên" xuyên section; khối ý <~200 từ; heading tổ tiên có nghĩa | G-BÀI |
| GE-20 | ≥3 EAV/100 từ ở L0; số nằm trong câu S-V-O quotable; có trần — cover đủ rồi dừng | — |
| GE-21 | Quote nguồn liên quan · số liệu · cite sau claim; mỗi số truy được nguồn + năm | — |
| GE-22 | Non-commodity: có thứ chỉ site này có (data gốc, test thật, case, ảnh tự làm); test ngược "tóm tắt top SERP qua AI ra được bài này?" | — |
| GE-23 | Claim quan trọng nằm dưới heading khớp cluster, phát biểu bằng 1 câu quotable (passage verifiability) | — |
| GE-24 | Freshness thật theo cửa sổ vertical (commercial ~30 ngày); không date-spoofing; không re-stamp năm hàng loạt | — |
| GE-25 | Blur Test 50% vẫn nhận ra topic + function; info quyết định không giấu trong tab/accordion | — |
| GE-26 | Page-type fit + guardrail listicle (không tự xếp #1 không phương pháp, không AggregateRating tự làm · AI nghi ngờ vì brand tự xếp hạng: không gỡ bài; viết top list khách quan + EEAT, giải bằng offsite consensus GE-28…32 (Lead chốt 19/10/2026)) | — |
| GE-27 | So với AI answer hiện tại (user paste): facts AIO bỏ sót đã cover? format AIO ưa đã align? | — |

Output: **G-BÀI: PASS/FAIL/UNKNOWN theo URL** + Bộ BÀI P/A đã xác minh, K/A độ phủ, U UNKNOWN, N N/A + việc sửa/lấy data. Nhận toàn văn để chấm nội dung; thiếu nguồn dẫn/ảnh render/lịch sử sửa/AI answer thì item liên quan UNKNOWN. Chỉ ghi Sheet nếu có quyền; bảng markdown đủ để bàn giao. Rewrite ở chế độ full khi được giao, giữ finding_id và recheck evidence.

## Quy trình — chế độ full (6 bước)

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,gemma?,firecrawl?,ahrefs?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `gemma`: Bước 3 mục 2 dùng manual proxy trong reference và ghi "chưa đo Gemma".

### Bước 0b — Gate điều kiện nền (G-T1) + pre-flight AI crawler + scope confirm

**Điều kiện nền:** nhận G-T1 theo URL/engine từ audit kỹ thuật + baseline. Top 10 truy vấn con liên quan là tiêu chí ưu tiên GTV, không phải điều kiện citation do hãng công bố. G-T1 FAIL/UNKNOWN → chưa xác nhận hoàn tất hoặc triển khai hàng loạt phụ thuộc gate; vẫn spot-check từ dữ liệu user giao. Không tự chấm lại GE-01/02/03 nếu output còn phù hợp.

Chuẩn rank dùng để ưu tiên nguồn lực, không suy page-one Google bằng pooled source list của mọi engine.

Checklist trước khi chạy:
- [ ] Ghi index/rank status của $TARGET và nguồn/ngày (UNKNOWN nếu thiếu); không suy từ lời xác nhận ra dữ liệu GSC.
- [ ] **Pre-flight access:** đọc output kỹ thuật theo engine/URL hoặc ghi UNKNOWN. Nếu search access của engine mục tiêu bị chặn, ưu tiên sửa access; không suy tất cả engine bị chặn. GPTBot/ClaudeBot là training; Google-Extended kiểm soát training và grounding Gemini Apps/Vertex AI, không ảnh hưởng Google Search. Evidence và nguồn chính chủ ở `references/audit-contract.md`; không tự thay robots trong audit content.
- [ ] $QUERIES chốt (1-5). Query dạng nào? Ưu tiên effort theo AIO trigger model: Informational/question/7+ từ = xác suất AIO cao nhất (bảng rút gọn trong [references/geo-levers-map.md](references/geo-levers-map.md)).
- [ ] Nếu gọi MCP: báo số call dự kiến (thường 1-3 call Ahrefs), **chờ user xác nhận**.
- [ ] $AI_ANSWERS có chưa? Không có → hỏi user muốn paste hay skip Bước 4.

### Bước 1 — Chunk audit: self-containment (AX1 → GE-19)

Tách bài thành chunk theo H2/H3 (heading = extraction boundary tự nhiên — Dejan khuyến nghị nguyên văn). Chấm từng chunk theo rubric trong [references/chunk-audit-method.md](references/chunk-audit-method.md):

- **Chuẩn chunk GTV:** KHÔNG cap số từ cho H2 section. 4 tầng: (1) **1 heading = 1 facet** — section trả lời trọn 1 sub-question và tự đứng; (2) **L0 = đoạn trả lời 40-75 từ, có thể nhiều câu; câu đầu sau heading trả lời thẳng** (GE-18); (3) **mỗi khối ý <~200 từ** — con số vận hành duy nhất, nhãn `observational` (Chrome DocumentChunker cap 200 words/passage — Dejan 2025); section dài hơn 1 khối ý → tách H3 hoặc đoạn mới, không "cắt cho ngắn"; (4) **mỗi câu tự đứng S-V-O** đủ E-A-V (53% citation là câu giữa đoạn — Indig 1,2M responses, B). Các con số 128 / 800 / 500 token thuộc 3 hệ khác nhau — chỉ để hiểu cơ chế, xem bảng "3 con số chunk" [[Audition Chunk]], **không dùng làm ngưỡng**.
- **Tự đứng:** chunk cắt rời khỏi bài vẫn đủ Entity + context + claim để trả lời trọn 1 sub-query (AI Mode retrieve ở passage-level — mỗi cluster sub-query cần ≥1 passage tự đứng).
- **Heading tổ tiên có nghĩa:** máy gắn H1/H2 cha vào chunk như metadata (`includeAncestorHeadings`, Google Cloud docs) — chunk giữa bài vẫn "biết" mình thuộc mục nào; heading rỗng nghĩa ("Tổng quan", "Kết luận", "Phần 2") làm mất lợi thế → flag.
- **Không đại từ hồi chỉ:** "điều này", "như đã nói ở trên" → chunk mất context khi bị cắt.
- **Câu 1 sau heading = câu trả lời heading** (Subordinate Text Match — 5 anti-patterns + bảng heading-type → L0 pattern trong reference).

Output bước này: bảng chunk × điểm self-containment × verdict (PASS / REWRITE / TÁCH PAGE).

### Bước 2 — Front-load check (AX2)

- **First 100-150 từ main content = audition chunk target:** answer-first, không filler — đây là chunk cosine cao nhất đại diện toàn page trước cửa Deep Reading; nếu là nav/junk/vòng vo → page bị loại dù thân bài hay ([[Audition Chunk]]).
- Manual proxy khi không có embedding: đếm overlap key terms của Semantic Query trong 100-150 từ đầu — **≥5/10 pass, <3/10 rewrite** ([[Audition Chunk]] In Practice — Manual audit).
- **Best content trong 30% đầu trang:** 44,2% AI citations đến từ first-30% (Indig 02/2026; patent US9940367B1).
- Central Entity + keyword chính xuất hiện trong 100 chữ đầu (sop/08 P16).
- ✅ "Kill the storytelling intros" (Indig 02/2026, theo sop/08 AX2) — ⚠ trừ narrative niches (travel/lifestyle): đây là Open Question, không áp máy móc 100%.

### Bước 3 — Heading-query alignment (AX7 → GE-17; cluster map đầy đủ cho cả topic → skill `geo-fanout-research`)

1. **Fan-out simulation → gom CLUSTER (v1.2 — thay cho "sinh 8-12 sub-queries"):** sinh sub-queries cho mỗi $QUERY theo lens (định nghĩa / so sánh / how-to / chi phí / đối tượng / rủi ro / thay thế…) rồi **gom thành cluster ≤4** — ~90% fan-out gom được vào ≤4 cluster, chỉ ~27% sub-query lặp lại giữa các lần chạy (Batch 40, 08/2026) → **tối ưu theo cluster, không đuổi từng query**. Số fan-out tuyệt đối (8-12, 7,61…) đã hết hạn theo phiên bản model — không in ra deliverable. Mỗi cluster cần ≥1 heading + ≥1 passage tự đứng trong bài; cluster không có heading nào cover → gap. Trang rank cho nhiều sub-query cùng lúc có xác suất cite cao hơn (+161%, Surfer — nhãn C).
2. **Cos heading ↔ cluster (EmbeddingGemma 2):** đo bằng skill `geo-fanout-research` Bước 4a (`fanout_cover.py cover` rồi `gaps`). Đọc ngưỡng phủ (rubric `geo-fanout-coverage`) theo thứ tự: registry của skill `model-calibration`: site trước (`00-client-context/model-calibration.json` của instance), defaults sau (`calibration-defaults.json`). Chưa có ngưỡng hiệu chuẩn: ghi "chưa hiệu chuẩn, Claude đọc", rồi Claude đọc heading và section của subquery cos thấp nhất trước. Hiệu chuẩn 19/10/2026 chưa tìm được ngưỡng phủ tuyệt đối. Phép đo có tín hiệu là so `mean_best` của trang mình với trang khác trong cùng top 10 (AUC 0,674 dev, 0,683 holdout). Mốc cos của nghiên cứu Indig × AirOps đo bằng bge-base-en-v1.5 trên tiếng Anh, không dùng cho Gemma hay content Việt. Không có embedding → manual proxy trong reference. 🔒 Số cos chỉ dùng nội bộ (blacklist register cho tài liệu public/khách).
3. **Title ↔ fan-out queries:** benchmark cited 0,656 — match sub-questions NỘI BỘ của AI quan trọng hơn match query gốc. ChatGPT gatekeep trên Title + Snippet + URL trước khi mở page (~50% retrieved URLs mới được cite).
4. **URL slug natural-language:** citation 89,78% vs 81,11% khi không có. Slug đổi được không? (cân nhắc redirect cost — chỉ đề xuất khi page mới/traffic thấp).
5. **Scope check — không dùng dải số từ / số heading cố định (Lead 29/08/2026):** heading match trực tiếp query; bài gánh đúng **1 câu hỏi chính** (≥2 câu hỏi chính / ≥2 cluster ngoài Central Search Intent → đề xuất tách page QDP). Độ dài + số heading là hệ quả của loại node trong topical map (quality node / pillar dài hơn leaf node), Section Benchmark đối thủ, search intent, vị trí topical map, bộ query target — bài dài vì node type đòi hỏi **không** phải lỗi GEO; "500-2.000 từ / 7-20 subheading" (Indig) chỉ là quan sát trên tập mẫu, không in ra deliverable như spec.

🔴 **Không đẩy về ultimate guide:** page cover 26-50% subtopics THẮNG page cover 100% (100% chỉ +4,6pp vs 0%). Nếu bài cover quá rộng / heading dàn trải → đề xuất TÁCH page, không đề xuất bổ sung sections "cho đủ coverage". Coverage ở cấp network, focus ở cấp page — "build the page that is the best answer to one question".

### Bước 4 — AIO counter-positioning (AX3 — phần consensus-gap)

Cần $AI_ANSWERS (Path A/B/C ở Input). Có answer thì:

1. **Extract facts** trong AI answer hiện tại → danh sách facts + nguồn được cite.
2. **Fact coverage check:** bài mình cover được bao nhiêu facts đó? Mục tiêu = Core Source: Fact Coverage Ratio phân biệt mạnh nhất — 0,42 (core) vs 0,34 (non-core) vs 0,23 (uncited); "DR does not matter much".
3. **Consensus-gap:** góc/thuộc tính nào AI answer hiện tại THIẾU mà nguồn đáng tin có? → bổ sung để vừa cover consensus vừa vượt (lý do AI cite thêm mình).
4. **GEO paper tactics (KDD 2024 — đọc PRIMARY 23/08/2026, [[sources/geo-paper-kdd-2024]])** khi rewrite: top tactic là **Quotation Addition** (quote nguồn liên quan), kế đến **Statistics Addition**; **Cite Sources** đứng một mình yếu hơn (~8% dưới) nhưng mạnh nhất khi kết hợp. Mức tăng verbatim: *"best methods improve upon baseline by 41% and 28%"* theo 2 metric proxy nội bộ (Position-Adjusted Word Count / Subjective Impression), đo trên GPT-3.5-turbo + Perplexity 2023-24 — KHÔNG phải traffic, KHÔNG viết "+40%"/"+115%". Đòn bẩy lớn nhất khi trang đang là **nguồn yếu** trong câu trả lời (Table 2: Cite Sources Rank-5 +115,1% **đi kèm** Rank-1 −30,3%) → trang đã thống trị câu trả lời thì đầu tư chỗ khác. Chọn theo domain (GE-21): factual → cite nguồn · opinion/pháp lý → số liệu · kể chuyện/lịch sử → quote. Keyword stuffing tệ hơn không làm gì (17,8 < baseline 19,5); giọng "authoritative" *no significant improvement*. C-SEO Bench (NeurIPS 2025) tranh cãi độ lớn → nhãn A cho thứ tự tactic, C cho độ lớn.
5. **Per-engine emphasis** nếu $ENGINE chỉ định (bảng trong [references/geo-levers-map.md](references/geo-levers-map.md)): ChatGPT → Early Query Confirmation + Intent Alignment + Section Connectivity; AI Mode → General→Specific + Early Query Answer + Section Connectivity; AIO/Perplexity → rộng đều. ⚠ Per-engine cited-source patterns KHÔNG ổn định (chỉ 2,37% URLs được cả 3 engine cite, 91% single-engine) — emphasis nhẹ, không optimize cứng theo 1 engine.

### Bước 5 — Retrievability scoring + rewrite đề xuất

1. **Bảng chẩn đoán per page** (chi tiết trong [references/chunk-audit-method.md](references/chunk-audit-method.md)): rank theo scope → heading-query match → chunk quality → freshness theo intent → nguồn/quote/số liệu phù hợp. Ghi evidence và action từng trục; không tính tổng /10 từ trọng số chưa hiệu chuẩn. Điểm GEO chính thức chỉ theo Bộ BÀI và audit-contract.
2. **Rewrite đề xuất per chunk** — CHỈ chunk verdict REWRITE/TÁCH, giữ nguyên chunk PASS (surgical). Mỗi rewrite giữ trọn câu trả lời theo intent; L0 40-75 từ có thể gồm nhiều câu, bắt đầu trả lời ngay câu đầu; mỗi khối ý <~200 từ theo quy ước GTV, không cap H2 section. Dải 100-170 từ chỉ là tham khảo quan sát, không ép đạt dải, không chấm fail nếu ngoài dải; không cắt mất điều kiện cần để claim đúng. Mỗi câu quan trọng tự đứng S-V-O. **ROI của tái cấu trúc không đổi chữ:** +17,3% citation trên 6 engine chỉ bằng restructure (Yu et al., arXiv 2603.29979 — đọc qua Surfer, nhãn C→B, cần đọc primary) → verdict REWRITE ưu tiên đảo thứ tự / tách khối / câu đầu trước, thêm chữ sau.
3. **AX6 — Passage verifiability (GE-23, bổ sung v1.2):** với mỗi claim quan trọng mà bài muốn được cite, kiểm: (a) claim nằm trong passage **rank được** cho cluster tương ứng (heading match ở Bước 3); (b) claim được phát biểu bằng **1 câu S-V-O hoàn chỉnh, có số/nguồn/ngày** trong chính passage đó, không rải ở 2-3 đoạn. Cơ chế: linkify 2 pha (patent US11769017B1 + US20240289407A1) — AI sinh summary từ nhiều SRD rồi verify từng đoạn bằng khoảng cách embedding trước khi gắn link → **document nuôi summary ≠ document được cite**; trang có claim đúng nhưng phát biểu rời rạc sẽ nuôi câu trả lời mà không được link. Fail → gộp claim về 1 câu quotable trong passage đúng heading.
4. **Freshness lever (GE-24):** 76,4% top cited pages update trong 30 ngày (GEO.md, giữ đúng số; cửa sổ per-vertical: commercial/pricing ~30 ngày, news ~7 ngày — `content-refresh` T14b) + cơ chế `URL_freshness_score` (Yeşilyurt) → đề xuất chu kỳ update **nội dung** thật. 🔴 KHÔNG date-spoofing — fake refresh date = LLM manipulation, Google 04-05/2026 xử như spam. Nuance 08/2026: **content năm cũ không chết** — ChatGPT search song song "2026" và "2025" trong cùng chain (multi-year search), unigram năm đã rớt khỏi top-5 → không đề xuất re-stamp năm hàng loạt trên title.
5. **AX4 (canonical/index hygiene) + AX5 (Blur Test):** chấm pass/fail nhanh; AX4 fail → `/seo-onpage` (evidence [[Index Partition]]); AX5 fail → `sop/07-visual-semantic.md` B7 / `image-seo-optimize`. Không mở rộng ở đây.
6. **TTFB note-only:** target <700ms, ideal <200ms, hard timeout 2s (Gate #2 ChatGPT Pipeline — đơn nguồn, label "reverse-engineered estimate"; blacklist register cho tài liệu public). Ghi vào report mục Notes, KHÔNG thuộc scope sửa của skill này.

### Bước 6 — Bàn giao đo lường

Đóng gói cho `geo-tracking-prompt-selection`:
- Danh sách page đã optimize + target queries + ngày optimize + engine ưu tiên.
- Baseline: AI answer hiện tại (nếu có ở Bước 4) + rank status.
- Nhắc nguyên tắc đo: AIO bề mặt đổi mỗi ~2,15 ngày nhưng semantic stability 0,95 — thắng TOPIC chứ không thắng query, đo aggregate AI Share of Voice; AIO ≠ AI Mode (chỉ 13,7% citation overlap) → track 2 kênh riêng.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Bảng heading ↔ cluster ghi nguồn ngưỡng, hoặc ghi "chưa hiệu chuẩn, Claude đọc". Không dùng dải cos của nghiên cứu tiếng Anh. Nguồn lỗi: bản trước 19/10/2026 dùng dải lấy từ bge-base-en (AirOps); hiệu chuẩn Gemma 19/10 không tìm được ngưỡng phủ tuyệt đối.
- [ ] Cos của trang chỉ so với trang trong cùng top 10 của query. Nguồn lỗi: pilot 10/2026, AUC ngược chiều (0,35) khi so với URL được trích ngoài top 10.
- [ ] 100–150 từ đầu trả lời thẳng câu hỏi chính. Nguồn lỗi: pilot 19/10/2026, một trang dịch vụ mở bằng câu dẫn, trong khi 2/4 trang được trích cùng truy vấn trả lời ngay (AUC 0,644).
- [ ] Số liệu đề xuất thêm là số đo thật có nguồn; thiếu thì ghi `[chưa có bằng chứng]`. Nguồn lỗi: pilot 10/2026, số đo từ dự án thật là tín hiệu mạnh nhất với trích dẫn AI (AUC 0,73).
- [ ] Bài bị AI nghi ngờ vì tự xếp hạng không bị đề xuất gỡ. Đề xuất top list khách quan có EEAT và offsite consensus GE-28…32. Nguồn lỗi: GE-26, Lead chốt 19/10/2026.
- [ ] Mọi số trong report có nguồn và ngày. Tài liệu khách không có số cos hay số trong blacklist register. Nguồn lỗi: register GEO 08/2026 chặn số cos, "+40%" và "+115%".

## Output

File: `<project>_GEO-Audit_v1.md` (tăng `_v2`, `_v3` nếu trùng) — trả về `08-geo-ai-visibility/` của instance theo `_REFERENCE/folder-map.md`.

```markdown
# GEO Audit — <page title>
> URL: <url> | Ngày audit: <YYYY-MM-DD> | Target queries: <q1; q2...>
> Rank status: <page-one cho query X — nguồn: Ahrefs/GSC/user-confirmed> | Engine ưu tiên: <AIO/AI Mode/ChatGPT/Perplexity/chung>

## 1. Bảng chẩn đoán (không cộng thành điểm GEO)
| Trục | Kết quả / giới hạn | Evidence + ngày | Action |
|---|---|---|---|
| GE-01 ưu tiên GTV; G-T1 từ audit nền | <PASS/FAIL/PARTIAL/UNKNOWN theo scope; không suy toàn gate từ rank> | <URL/query/engine/nguồn> | <sửa nền; vẫn chẩn đoán> |
| Heading↔query alignment | <khớp/chưa khớp/UNKNOWN; proxy chỉ tham khảo> | <heading/query> | <đổi gì, vì sao> |
| Chunk quality (AX1+AX2) | <n>/<m> chunk đã kiểm đạt; <u> chưa kiểm | <chunk IDs> | <giữ/rewrite/tách> |
| Freshness | <còn đúng/cần cập nhật/UNKNOWN theo intent> | <fact kiểm + ngày nguồn> | <cập nhật nội dung thật> |
| Nguồn/quote/số liệu phù hợp | <claim đủ/thiếu bằng chứng/UNKNOWN> | <claim → source> | <bổ sung hoặc bỏ claim> |

## 2. Chunk Audit (AX1 + AX2)
| # | Heading | Số từ | Self-contain | Câu 1 = answer | Verdict |
|---|---|---|---|---|---|
| 1 | <H2...> | <tổng section; từng khối ý> | <đủ/thiếu context> | <trả lời/dẫn nhập; giữ điều kiện đúng> | <theo rubric> |

### Front-load
- First 100-150 từ: <PASS/REWRITE> — overlap <n>/10 key terms
- 30% đầu trang: <nhận xét> | P16 đầu-cuối: <✅/❌>

## 3. Alignment (AX3)
- Fan-out → cluster (≤4): <cluster A: sub-queries…; cluster B…> | cluster chưa có heading cover: <list>
- Heading↔cluster: <bảng heading → cluster → cos Gemma (trang mình / tốt nhất top 10) hoặc proxy → verdict Claude; ghi nguồn ngưỡng hoặc "chưa hiệu chuẩn, Claude đọc">
- Title: <hiện tại> → <đề xuất — so với mean cited 0,656 (tham chiếu, không phải cutoff)> | Slug: <natural-language ✅/❌ + khuyến nghị>
- AX6 passage verifiability: <n>/<m> claim quan trọng nằm đúng passage + quotable → <PASS/FAIL + claim cần gộp>

## 4. Counter-positioning (nếu có AI answer)
- AI answer ngày <d>, engine <e>: facts = <list>
- Fact coverage của bài: <n>/<m> | Gap bổ sung: <list>
- Tactics thêm: <statistics / expert quote / cite nguồn — cụ thể>

## 5. Rewrite đề xuất per chunk
### Chunk <n> — <heading>
- Vấn đề: <anti-pattern nào>
- Rewrite (đủ intent, L0 40-75 từ, khối ý <~200 từ; không cap section): <đoạn đề xuất>

## 6. Ngoài scope — trỏ đi
- [ ] AI crawler access (GE-02): <mở/chặn — bot nào> → technical-seo-audit 4.13
- [ ] HTML/nav junk trong chunk → semantic-html-optimization
- [ ] AX4 canonical/index: <PASS/FAIL> → /seo-onpage
- [ ] AX5 Blur Test: <PASS/FAIL> → image-seo-optimize
- [ ] TTFB: <n>ms (note-only, estimate đơn nguồn)
- [ ] Bộ BÀI GE-16…GE-27: <P>/<A> đạt đã xác minh; độ phủ <K>/<A>; <U> UNKNOWN; <N> N/A có lý do. Chỉ chốt điểm khi U=0; A=0 ghi N/A (xuất Sheet theo audit-contract)

## 7. Bàn giao đo lường → geo-tracking-prompt-selection
- Pages + queries + ngày optimize + baseline
- Chu kỳ re-update đề xuất: <30 ngày...> (update thật, không spoof date)

## Nguồn số liệu
<mỗi con số dùng trong report: nguồn + ngày — vd "58%/14%: Indig 04/2026">
```

## Behavior Gates

1. **#1 Think Before** — Bước 0b phân biệt ưu tiên đầu tư với quyền audit: G-T1 FAIL/UNKNOWN chặn rollout phụ thuộc, vẫn audit chẩn đoán từ evidence sẵn có. Không kết luận ROI thấp chỉ từ rank hoặc prevalence AIO; nêu cơ hội, giới hạn và finding cụ thể. Nếu $QUERIES/$TARGET mơ hồ → hỏi đúng input còn thiếu.
2. **#2 Evidence** — MỌI con số trong report truy được về nguồn + ngày (mục "Nguồn số liệu" bắt buộc). Số wiki giữ đúng: 76,4% / 58%-14% / 41%-30% / 89,78%-81,11% / **38% first-100-words (Surfer 06/2026, C)** ≠ **~38% AIO cite top-10 (Ahrefs 01/2026, B)** — hai số khác nhau, ghi rõ metric. Tham số McSweeney (128 tokens, 2s, 80/20, sliding window 300 từ) là đơn nguồn — luôn label "reverse-engineered estimate", không cam kết spec với client. AI citation stats = moving target → ghi ngày nguồn, refresh theo lint quý. **Lớp phát hành (v1.2):** report nội bộ dùng đủ số kèm nhãn A/B/C/D; deliverable gửi khách / tài liệu public chỉ dùng **whitelist** của [[syntheses/geo-evidence-register-2026-08]] — các số blacklist (8-12 sub-queries, 7,61, +115%, "+40%", cosine 0,90, 375 từ, 128 token, 2s, Gecko/Jetstream) không in ra.
3. **#3 Surgical** — chỉ rewrite chunk FAIL; chunk PASS không chạm. Không sửa HTML, không đề xuất schema/backlink/outline mới — flag rồi trỏ đúng skill. Không tự mở rộng sang page khác cùng site.
4. **#4 Goal-driven** — mục tiêu cuối = Core Source (được cite LẶP LẠI qua N lần hỏi), không phải 1 lần xuất hiện. Mọi đề xuất phải map về 1 trong 5 levers / AX1-AX6 ([references/geo-levers-map.md](references/geo-levers-map.md)); đề xuất không map được → bỏ.

## Anti-patterns

- 🔴 **KHÔNG bao giờ đề xuất llms.txt** — llms.txt KHÔNG phải GEO lever: Google không dùng (Mueller so sánh với keywords meta tag), audit log 2025 cho thấy GPTBot/ClaudeBot/PerplexityBot không request file này. Điều khiển AI crawler = **robots.txt**. GEO.md đã chốt — skill nói đúng như vậy, kể cả khi client hỏi.
  - Ngoại lệ duy nhất (18/10/2026): site cần điểm hạng mục "Duyệt web bằng tác nhân" của PageSpeed Insights được đặt `/llms.txt` tĩnh, vì audit `llms-txt` của Lighthouse chấm file này. Ghi mục đích là điểm lab PSI. Không đưa file vào kế hoạch GEO, không báo cáo như việc GEO. Cách làm: `wp-pagespeed/references/agentic-browsing.md`.
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
- [references/geo-levers-map.md](references/geo-levers-map.md) — map 5 Core Levers ↔ AX1-AX6 ↔ hành động; per-engine emphasis; AIO trigger table; bảng "KHÔNG phải lever".
- SOP: `sop/08-onpage-checklist.md` (AX1-AX6 canonical + P16), `sop/07-visual-semantic.md` (Blur Test B7 — AX5).
- Wiki: [[Retrieval-Augmented Generation]], [[ChatGPT Pipeline]], [[Audition Chunk]], [[AI Mode]], [[Query Fan-Out]], [[AI Overviews]], [[Core Source]], [[Subordinate Text Match]], [[GEO]], [[sources/shorter-focused-content-wins-chatgpt-indig]], [[sources/why-chatgpt-cites-one-page-over-another-ahrefs]].
- Web (mới hơn wiki, ứng viên ingest): Dejan "In AI SEO #10 is the new #1" (https://dejan.ai/blog/in-ai-seo-10-is-the-new-1/); iPullRank "A Refutation of Misinformation about Chunking" (https://ipullrank.com/misinformation-about-chunking) — backing lý luận khi client phản biện "Google bảo cứ viết tự nhiên".

## Changelog

- v1.5.1 (2026-10-19): đổi tên mục "Workflow — chế độ full" thành "Quy trình — chế độ full" để lệnh kiểm cấu trúc thấy Bước 0 đúng chỗ.
- v1.5.0 (2026-10-19): Bước 3 mục 2 bỏ dải cos lấy từ bge/AirOps, đọc ngưỡng phủ từ registry của `model-calibration`; chưa có ngưỡng thì "chưa hiệu chuẩn, Claude đọc". Đo bằng `geo-fanout-research` Bước 4a. Thêm Bước 0 kiểm tool (Gate cũ thành Bước 0b), phân việc model, tự phản biện. Sửa tương ứng `references/chunk-audit-method.md` và `geo-levers-map.md`.
- v1.4.4 (2026-10-19): bỏ luật keyword chính trong 100 chữ cuối (P16 mới): chỉ giữ Central Entity + keyword trong 100 chữ đầu.
- v1.4.3 (2026-10-19): GE-26 thêm cách xử lý khi AI nghi ngờ vì brand tự xếp hạng (Lead chốt): giữ bài, top list khách quan + EEAT, offsite consensus GE-28…32.
- v1.4.2 (2026-10-18): ghi ngoại lệ `/llms.txt` cho audit `llms-txt` của PSI (hạng mục "Duyệt web bằng tác nhân"): được đặt, không tính là đòn bẩy GEO.
- v1.4 (2026-09-12): đồng bộ gate/evidence với router, sửa Google-Extended và giữ spot-check tự chứa.

Lịch sử đầy đủ: `CHANGELOG.md` (chỉ đọc khi bảo trì).
