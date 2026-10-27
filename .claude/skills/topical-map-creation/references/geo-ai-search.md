# GEO và AI search cho topical map

Chuyển từ SKILL.md ngày 27/10/2026 để SKILL.md dưới 500 dòng. Nội dung giữ nguyên.


### 7 Stages of ChatGPT Search Pipeline

| Stage | Description | Topical Map Optimization |
|-------|-------------|--------------------------|
| 1. Sonic Classifier | Decides if web search needed | N/A |
| 2. Thinky Query | Creates Simple + Semantic queries | N/A |
| 3. Gate #1 | Title + Meta Description filter | ONE clear Macro Context per page |
| 4. Gate #2 | 2-second hard timeout | Optimize Core Section speed, TTFB <2s |
| 5. Gate #3 | Chunk + Cosine Similarity scoring | Comprehensive coverage, L0 Answer-First |
| 6. Deep Reading | Top chunks read deeply | Quality content structure |
| 7. Final Generation | GPT synthesis with citations | Clear, citable statements |

**Key Insight**: Topical Map directly supports Gates #1, #3 through clear structure and comprehensive topical coverage.

### AI Mode / AI Overviews layer (v2.0 — bổ sung cho ChatGPT pipeline ở trên)

- Cả AIO lẫn AI Mode dùng **query fan-out** (Google docs xác nhận) — xem Step 10b; retrieval ở passage level → brief phải spec chunk tự đứng (L0 answer-first per heading — 40-75 từ là chuẩn nội bộ GTV, khớp skill visual-semantic-seo; wiki L0 gốc ~40 từ).
- **KPI shift**: CTR #1 giảm 58% khi có AIO (Ahrefs 2026); "Great Decoupling" — impressions tăng, clicks giảm. Track **LLM citations + AI share of voice + Topic Share** song song clicks. Koray: "historical data will shift… to being validated through LLM-based citations."
- **GEO brief rules** (Princeton GEO, +30-40% visibility — label directional): mọi brief phải có named-source citations + quotations + statistics; keyword stuffing vô dụng.
- **Micro-semantics pass (Algorithmic Authorship + Relevance Configuration)**: word order/phrasing khớp tokenization ("bird sounds" vs "sound of bird") — spec trong brief cho writer.
- **Map refresh định kỳ** ("semantic distance maintenance" — Koray 2025): map decay nếu không update theo entity expansions; re-audit theo quý cùng lint.
- **Small-index asymmetry**: local topical maps + EMD — consensus rẻ hơn trong index nhỏ.
