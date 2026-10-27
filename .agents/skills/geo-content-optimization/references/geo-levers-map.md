# GEO Levers Map — 5 Core Levers ↔ AX1-AX6 ↔ hành động của skill

Reference cho Bước 0, 3, 4, 5 của `geo-content-optimization`. Nguồn khung: `GEO.md` (5 Core Levers) + `sop/08-onpage-checklist.md` (AX Extension AX1-AX7, map AX↔GE: AX1→GE-19 · AX2→GE-16 · AX3→GE-27 · AX4→GE-07 · AX5→GE-25 · AX6→GE-23 · AX7→GE-17 heading/title/meta ↔ cluster — bổ sung 29/08/2026).

## 1. Bảng map 3 chiều

| Lever (GEO.md) | AX (sop/08) | Hành động trong skill này | Ngoài scope → trỏ đi |
|---|---|---|---|
| **Structured Answers** | AX1 (chunk self-containment) + AX2 (front-load) + **AX6 (passage verifiability)** | Workflow Bước 1-2-5: tách chunk theo H2/H3, rubric 5 tiêu chí (chuẩn chunk GTV 4 tầng, không cap số từ section), front-load check, rewrite đủ intent, L0 40-75 từ và khối ý <~200 từ; 100-170 chỉ là tham khảo, gộp claim quan trọng về 1 câu quotable trong passage rank được | HTML/DOM → `semantic-html-optimization` |
| **Semantic Coverage** | **AX7** (heading/title/meta ↔ cluster) + AX3 (counter-positioning) | Workflow Bước 3-4: fan-out gom **cluster ≤4** (không đuổi từng query), heading↔cluster alignment + title/meta/slug chứa từ vựng cluster, consensus-gap vs AI answer hiện tại, KDD tactics (Quotation > Statistics > Cite Sources đứng riêng) | Consensus đa competitor → `competitor-consensus-content`; outline mới → `semantic-outline-methodology`; cluster map đầy đủ cho cả topic (công đoạn 28, Phase 1 research) → skill `geo-fanout-research` v1.0 |
| **Topical Authority** | (nền — ngoài scope page-level) | Note 1 dòng trong report nếu page mồ côi topic; điều kiện nền indexed + rank ở Bước 0 | Topical map → `/seo-topical-map` |
| **Entity Recognition** | (nền) | Note — không phải việc của skill này | Entity/schema/brand → pipeline semantic + `product-annotation` |
| **Authority Signals** | (nền) | Note — nhắc "DR does not matter much" ở page-level, đừng đổ lỗi thiếu link khi chunk kém | → `backlink-research` + `backlink-plan` |

**AX4 (canonical/index hygiene) + AX5 (Blur Test):** skill chỉ chấm pass/fail nhanh trong report mục "Ngoài scope — trỏ đi": AX4 fail → `/seo-onpage` (evidence [[Index Partition]]); AX5 fail → `sop/07-visual-semantic.md` B7 / `image-seo-optimize` / `visual-semantic-seo`. Không mở rộng.

## 2. AIO trigger table (rút gọn) — chọn page/query đáng audit ở Bước 0

Nguồn: [[AI Overviews]] (146M SERPs). Baseline AIO: 20,5% queries.

| Đặc điểm query | Xác suất AIO | Ưu tiên audit |
|---|---|---|
| Informational | 99,9% AIO keywords là informational | 🔴 cao nhất |
| Dạng câu hỏi | 57,9% (vs non-question 15,5%) | cao |
| Query dài 7+ từ | 46,4% | cao |
| Classifier: reason | 59,8% | cao |
| Classifier: bool | 57,4% | cao |
| Classifier: definition | 47,3% | trung bình-cao |
| Transactional / navigational ngắn | thấp | ⚠ ROI GEO thấp — nói rõ với user trước khi audit |

Ghi chú citation ↔ rank decoupling (lý do vẫn audit dù đã rank): AIO cite top-10 organic giảm ~76% (07/2025) → ~38% (01/2026); 36,7% cited URLs ngoài top-100 — do Query Fan-Out: trang được cite là trang thắng ở SUB-queries ([[Query Fan-Out]], GEO.md).

**Dải ưu tiên theo rank hiện tại (bổ sung 29/08/2026):**

| Rank của $TARGET cho sub-query/cluster | Verdict Bước 0 | Việc nên làm |
|---|---|---|
| Page-one (1-10) có evidence | Đạt phần ưu tiên rank của GE-01 [GTV]; chưa suy G-T1 PASS | Chạy Bước 1-6 theo scope; G-T1 cần thêm index/access/baseline |
| Rank 11-50 hoặc >50 đã xác minh | Chưa đạt ưu tiên top 10 [GTV], không suy mọi engine không thể cite | Ưu tiên nền SEO và heading/intent theo finding. Vẫn audit chẩn đoán; không mặc định ROI rewrite thấp chỉ từ dải rank. |
| Chưa index đã xác minh trên Google | Lỗi index trong scope Google; không suy mọi engine | Sửa nền index; vẫn kiểm nội dung và ghi giới hạn; rollout phụ thuộc chờ gate. |
| Chưa đo rank/index hoặc chỉ có GSC average position | UNKNOWN ở phần chưa xác minh; average position không phải retrieval rank của AI | Xin evidence đúng URL/query/market; tiếp tục phần audit có dữ liệu, không xin chấp nhận caveat để được chẩn đoán. |

Các ước tính reverse engineering về số URL được ChatGPT lọc không phải tiêu chí gate hay bằng chứng ROI. Áp trạng thái và scope theo `audit-contract.md`.

## 3. Per-engine emphasis khi counter-positioning (Bước 4)

Nguồn: `sop/08` (Suski 50M AIO). Dùng làm EMPHASIS nhẹ khi $ENGINE chỉ định — không optimize cứng.

| Engine | Nhấn mạnh | Ghi chú |
|---|---|---|
| ChatGPT | Early Query Confirmation + Intent Alignment + Section Connectivity | EEAT weight thấp; gatekeep Title/Snippet/URL trước khi đọc page; ref_type: search 88,46% / news 12,01% / reddit 1,93% / youtube 0,51% / academia 0,40% |
| AI Mode | General→Specific + Early Query Answer + Section Connectivity | Passage-level retrieval, fan-out gom ≤4 cluster (số tuyệt đối đổi theo model — không neo); top cited Wikipedia-heavy |
| AIO | Rộng đều các tín hiệu | Top cited: YouTube #1 + Reddit ~21%; volatility ~2,15 ngày nhưng semantic stability 0,95 |
| Perplexity | Rộng đều | Reddit 46,5% top cited |

🔴 Pattern cited-source per engine KHÔNG ổn định: chỉ 2,37% URLs được cả 3 engine cùng cite, 91% single-engine; AIO ≠ AI Mode (86% semantic similarity nhưng 13,7% citation overlap) → optimize + track 2 kênh riêng, không nhại style nguồn ưa thích của 1 engine (vd viết Reddit-style vì Perplexity — Reddit Paradox: retrieve ồ ạt 16M points nhưng ChatGPT cite 1,93%).

⚠ Open Question: AIO merge vào AI Mode 05/2026 — sau merge AIO còn là surface đo riêng không? Theo dõi qua lint quý; hiện tại vẫn báo cáo 2 kênh riêng.

## 4. Bảng "cái gì KHÔNG phải lever" (chốt, kèm evidence)

| Không phải lever | Evidence | Skill phản hồi khi client hỏi |
|---|---|---|
| 🔴 llms.txt | Google không dùng (Mueller: như keywords meta tag); audit log 2025: GPTBot/ClaudeBot/PerplexityBot không request llms.txt; falsification cats.txt 08/2026: 4 "proofs" (crawled/indexed/RAG-repeated/LLM-endorsed) đều fake — xảy ra với mọi text file | "Điều khiển AI crawler là robots.txt. llms.txt không nằm trong deliverable." (GEO.md đã chốt) |
| 🟡 Markdown for Agents (Cloudflare) — KHÁC llms.txt, nhưng chưa phải lever | CÓ demand thật (1.421 req/44 ngày, n=1) nhưng từ coding agents + RAG pipelines, KHÔNG phải search crawlers (GPTBot/ClaudeBot/PerplexityBot chưa request); chưa có data markdown → citation lift | "Advanced hygiene cost 0, bật được — nhưng đo trước khi claim: baseline markdown-request trong log + review quý. ⚠️ Bật = tự gắn Content-Signal ai-train=yes — review policy client trước. Chi tiết: technical-seo-audit item 1.18." |
| 🔴 Schema (cho citation) | Causal test Ahrefs 1.885 pages: AI Mode +2,4%, ChatGPT +2,2% ≈ 0 | "Schema đáng làm cho rich results / entity / second-impression rendering — việc khác, không tính điểm GEO." (GEO.md Open Questions — RESOLVED 2026-07-02) |
| Content volume | Correlation ~0,194 | Số bài ≠ citation; focus per page thắng |
| Độ dài bài / "ultimate guide" | 26-50% subtopics thắng 100% (chỉ +4,6pp vs 0%); mixed performers 17% = ultimate guides — dài nhất, DA cao nhất, kém ổn định nhất; snippet length ↔ quality r=0,05; page length ↔ representativeness r=-0,07 (Dejan 2026)¹ | Đề xuất TÁCH page; "best answer to one question" |
| Bold/format số lượng | Không có evidence citation | Không đưa vào rewrite checklist |
| DR page-level | "DR does not matter much" ([[Core Source]]); GEO paper KDD 2024 Table 2: trang là **nguồn yếu** trong câu trả lời hưởng lợi nhiều nhất từ tactic (Cite Sources Rank-5 +115,1% đi kèm Rank-1 −30,3% — không tách vế đầu ra dùng riêng) | Không viện cớ DR thấp; chunk quality + rank sub-query quyết định |
| Date-spoofing | Google 04-05/2026: LLM manipulation xử như spam | Freshness = update nội dung thật theo chu kỳ ≤30 ngày (76,4% top cited) |

¹ ⚠ Lệch biến đo với wiki: [[Audition Chunk]] hiện gán r=0.05 cho "độ dài bài ↔ citation" — theo bài gốc Dejan, r=0,05 là snippet length ↔ quality, còn page length ↔ representativeness là r=-0,07. Reconcile ở `/seo-lint` quý.

## 5. Nhắc nguồn + ngày (Evidence gate)

Citation stats = moving target. Bảng nguồn chính để report cite đúng:

| Cụm số | Nguồn | Ngày |
|---|---|---|
| 58%/14% retrieval rank; 41%/30% heading cosine; 26-50% coverage; 500-2.000 từ + 7-20 subheadings (quan sát trên tập mẫu — **không phải spec GTV**, độ dài theo node type + benchmark, Lead 29/08) | Indig × AirOps (qua [[sources/shorter-focused-content-wins-chatgpt-indig]]) — **B** | 04/2026 |
| 0,656 title-fanout; 89,78%/81,11% slug; ~50% retrieved→cited; ref_type 5 kênh | Ahrefs (qua [[sources/why-chatgpt-cites-one-page-over-another-ahrefs]]) — **B** | 04/2026 |
| 76,4% update 30 ngày; **~38% AIO cite top-10** (metric: tỷ lệ citation đến từ top-10 organic); llms.txt/schema verdicts | GEO.md / Ahrefs 01/2026 — **B** | cập nhật 07/2026 |
| **38% AIO citations từ 100 từ đầu trang** (metric KHÁC dòng trên; 2025: 20%) — song song 44,2% first-30% (Indig 02/2026, ChatGPT) | Surfer (qua [[sources/ai-citations-first-100-words-surfer]]) — **C** COI | 06/2026 |
| **KDD 2024 tactics**: Quotation Addition top; "+41% và +28%" theo 2 metric proxy (GPT-3.5-turbo + Perplexity 2023-24); Cite Sources Rank-5 +115,1% / Rank-1 −30,3%; keyword stuffing 17,8 < baseline 19,5 | Aggarwal et al. arXiv 2311.09735, đọc primary ([[sources/geo-paper-kdd-2024]]) — **A** thứ tự / **C** độ lớn (C-SEO Bench tranh cãi) | KDD 08/2024 |
| **+17,3% citation chỉ bằng tái cấu trúc, không đổi chữ** (6 engine) | Yu et al. arXiv 2603.29979 — đọc qua Surfer, **C→B**, cần đọc primary | 03/2026 |
| **~90% fan-out gom vào ≤4 cluster; ~27% sub-query ổn định giữa các lần chạy**; +161% cite khi rank nhiều sub-query | Batch 40 wiki (Google AI Mode) — **A** cơ chế / Surfer — **C** (+161%) | 08/2026 |
| AIO trigger %; 2,15 ngày; 0,95 stability; 13,7% overlap | [[AI Overviews]] | 2025-2026 |
| Snippet phẳng rank 1→10; 6,5 snippets/query; representativeness đo bằng model tiếng Anh (mốc của nghiên cứu không dùng làm ngưỡng Gemma); 200-300 từ | Dejan | 2026 (chưa ingest wiki) |
| 128 tokens; 2s timeout; 80/20 intent/topic; 300 từ window; lọc title+meta+URL ~40-50 URL → fetch 10-20 | McSweeney ([[ChatGPT Pipeline]]) | đơn nguồn — label "reverse-engineered estimate" (≈) |

**Lớp phát hành:** cột nhãn A/B/C/D theo [[syntheses/geo-evidence-register-2026-08]]. Report nội bộ dùng đủ; tài liệu public / gửi khách chỉ in **whitelist** của register (58%/14% · 38%+44,2% · 26-50% · schema ≈ 0 · llms.txt không dùng · 2,15 ngày…), **không in** 8-12 / 7,61 / +115% / "+40%" / cosine 0,90 / 375 từ / 128 token / 2s / Gecko-Jetstream. Refresh theo `/seo-lint` quý (hạn 31/10/2026).
