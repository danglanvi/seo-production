# GEO Levers Map — 5 Core Levers ↔ AX1-AX5 ↔ hành động của skill

Reference cho Bước 0, 3, 4 của `geo-content-optimization`. Nguồn khung: `GEO.md` (5 Core Levers) + `sop/08-onpage-checklist.md` (AX Extension).

## 1. Bảng map 3 chiều

| Lever (GEO.md) | AX (sop/08) | Hành động trong skill này | Ngoài scope → trỏ đi |
|---|---|---|---|
| **Structured Answers** | AX1 (chunk self-containment) + AX2 (front-load) | Workflow Bước 1-2: tách chunk theo H2/H3, rubric 4 tiêu chí, front-load check, rewrite per chunk 100-170 từ | HTML/DOM → `semantic-html-optimization` |
| **Semantic Coverage** | AX3 (+ fan-out simulation) | Workflow Bước 3-4: fan-out 8-12 sub-queries, heading↔query alignment, consensus-gap vs AI answer hiện tại, KDD tactics | Consensus đa competitor → `competitor-consensus-content`; outline mới → `semantic-outline-methodology` |
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

## 3. Per-engine emphasis khi counter-positioning (Bước 4)

Nguồn: `sop/08` (Suski 50M AIO). Dùng làm EMPHASIS nhẹ khi $ENGINE chỉ định — không optimize cứng.

| Engine | Nhấn mạnh | Ghi chú |
|---|---|---|
| ChatGPT | Early Query Confirmation + Intent Alignment + Section Connectivity | EEAT weight thấp; gatekeep Title/Snippet/URL trước khi đọc page; ref_type: search 88,46% / news 12,01% / reddit 1,93% / youtube 0,51% / academia 0,40% |
| AI Mode | General→Specific + Early Query Answer + Section Connectivity | Passage-level retrieval, fan-out 8-12; top cited Wikipedia-heavy |
| AIO | Rộng đều các tín hiệu | Top cited: YouTube #1 + Reddit ~21%; volatility ~2,15 ngày nhưng semantic stability 0,95 |
| Perplexity | Rộng đều | Reddit 46,5% top cited |

🔴 Pattern cited-source per engine KHÔNG ổn định: chỉ 2,37% URLs được cả 3 engine cùng cite, 91% single-engine; AIO ≠ AI Mode (86% semantic similarity nhưng 13,7% citation overlap) → optimize + track 2 kênh riêng, không nhại style nguồn ưa thích của 1 engine (vd viết Reddit-style vì Perplexity — Reddit Paradox: retrieve ồ ạt 16M points nhưng ChatGPT cite 1,93%).

⚠ Open Question: AIO merge vào AI Mode 05/2026 — sau merge AIO còn là surface đo riêng không? Theo dõi qua lint quý; hiện tại vẫn báo cáo 2 kênh riêng.

## 4. Bảng "cái gì KHÔNG phải lever" (chốt, kèm evidence)

| Không phải lever | Evidence | Skill phản hồi khi client hỏi |
|---|---|---|
| 🔴 llms.txt | Google không dùng (Mueller: như keywords meta tag); audit log 2025: GPTBot/ClaudeBot/PerplexityBot không request llms.txt | "Điều khiển AI crawler là robots.txt. llms.txt không nằm trong deliverable." (GEO.md đã chốt) |
| 🔴 Schema (cho citation) | Causal test Ahrefs 1.885 pages: AI Mode +2,4%, ChatGPT +2,2% ≈ 0 | "Schema đáng làm cho rich results / entity / second-impression rendering — việc khác, không tính điểm GEO." (GEO.md Open Questions — RESOLVED 2026-07-02) |
| Content volume | Correlation ~0,194 | Số bài ≠ citation; focus per page thắng |
| Độ dài bài / "ultimate guide" | 26-50% subtopics thắng 100% (chỉ +4,6pp vs 0%); mixed performers 17% = ultimate guides — dài nhất, DA cao nhất, kém ổn định nhất; snippet length ↔ quality r=0,05; page length ↔ representativeness r=-0,07 (Dejan 2026)¹ | Đề xuất TÁCH page; "best answer to one question" |
| Bold/format số lượng | Không có evidence citation | Không đưa vào rewrite checklist |
| DR page-level | "DR does not matter much" ([[Core Source]]); GEO paper: site rank thấp hưởng lợi +115% | Không viện cớ DR thấp; chunk quality + rank sub-query quyết định |
| Date-spoofing | Google 04-05/2026: LLM manipulation xử như spam | Freshness = update nội dung thật theo chu kỳ ≤30 ngày (76,4% top cited) |

¹ ⚠ Lệch biến đo với wiki: [[Audition Chunk]] hiện gán r=0.05 cho "độ dài bài ↔ citation" — theo bài gốc Dejan, r=0,05 là snippet length ↔ quality, còn page length ↔ representativeness là r=-0,07. Reconcile ở `/seo-lint` quý.

## 5. Nhắc nguồn + ngày (Evidence gate)

Citation stats = moving target. Bảng nguồn chính để report cite đúng:

| Cụm số | Nguồn | Ngày |
|---|---|---|
| 58%/14% retrieval rank; 41%/30% heading cosine; 26-50% coverage; 500-2.000 từ + 7-20 subheadings | Indig (qua [[sources/shorter-focused-content-wins-chatgpt-indig]]) | 04/2026 |
| 0,656 title-fanout; 89,78%/81,11% slug; ~50% retrieved→cited; ref_type 5 kênh | Ahrefs (qua [[sources/why-chatgpt-cites-one-page-over-another-ahrefs]]) | 04/2026 |
| 76,4% update 30 ngày; ~38% cite top-10; llms.txt/schema verdicts; KDD tactics ~40%/+115% | GEO.md | cập nhật 07/2026 |
| AIO trigger %; 2,15 ngày; 0,95 stability; 13,7% overlap | [[AI Overviews]] | 2025-2026 |
| Snippet phẳng rank 1→10; 6,5 snippets/query; representativeness 0,92/<0,80; 200-300 từ | Dejan | 2026 (chưa ingest wiki) |
| 128 tokens; 2s timeout; 80/20 intent/topic; 300 từ window | McSweeney ([[ChatGPT Pipeline]]) | đơn nguồn — label "reverse-engineered estimate" |

Web refresh 07/2026 không tìm thấy nghiên cứu mâu thuẫn số wiki; refresh tiếp theo qua `/seo-lint` quý.
