# Patent liên quan (verified 2026-07-02)

Chuyển từ SKILL.md ngày 27/10/2026 để SKILL.md dưới 500 dòng. Nội dung giữ nguyên.

| Patent | Focus | Verdict |
|--------|-------|---------|
| **US7421651B2** (từ US20060149775A1, Egnor) | Document segmentation based on visual gaps — segment theo white space khi render | STRONG |
| **US12393768B2** (LAMPRET, granted 08/2025) | Layout-aware multimodal pretraining — font-size/bold/italic/underline per block là model input | STRONG |
| **US9053177B1** (Minkoo Seo) | Sitelinks based on visual location — link chấm theo tọa độ X/Y render | STRONG |
| **US11907337B2** (granted 02/2024) | Multimodal image classifier — đọc ảnh từ pixels, không cần alt | STRONG |
| **WO2018097872A1/EP3529714B1** | Animated snippets — chọn ảnh theo prominence + persistence | STRONG |
| **US7716225B1** (Reasonable Surfer, Dean) | Link value theo prominence + topical cluster match | MODERATE |
| **US8498984B1** (Hwang/Seo, 2013) | Categorization of search results — chấm điểm cấp CATEGORY bằng position-CTR curve (37.3%/12.9%/10.1%…), cap per category → format phải khớp category thắng SERP | STRONG (đọc full-text v3.6) |
| **US9069855B2** (Zunger, granted 2015) | Pseudo-rendering 1 pass → quasi-DOM → **chunk tree**: merge node "gần nhau + tương thích" thành semantically distinct regions; hạ boilerplate | STRONG |
| **US10445328B2** (granted 2019, active) | Search result ranking & presentation: entity type → ranked property schema → presentation technique (map/chart/timeline/gallery); soft properties chấm co-occurrence | STRONG (cho SERP-feature benchmark) |
| **US9916366B1** (Bharat/Shukla, granted 2018) | Query Augmentation: query perform tốt + synthetic queries (anchor text lặp đủ ngưỡng = query gắn thẳng document); long click vs reversion | STRONG (cho Bước 1) |
| **US12536233B1** (granted 01/2026) | AI-generated content page: landing page score vượt ngưỡng (trang kém — vd không có product filter) → chèn AI page | STRONG (cho function argument) |
| US8949242B1 | "Semantic document analysis" — change detection per segment. ⚠️ KHÔNG phải centerpiece patent (từng bị cite sai ở v2.x) | historical note |

**Patent applications — chưa cấp, đọc như DESIGN INTENT, phân loại riêng (quyết định của Lead 07/2026):**
- **WO2020033805A1** (Website representation vector — **CEASED**): site → vector ~100 chiều (text+images+links, KHÔNG có layout input); tier expert/apprentice/layperson per knowledge domain; site mới classify bằng dot-product với composite vector; representation sinh được từ subdomain.
- **US20240289407A1** (Search with stateful chat — **PENDING**): user state đa lượt; LLM sinh synthetic queries; response linkify về source "verify claim" (mục tiêu GEO).

**De-attributed** (v2.x cite sai, không phải patent layout): US10565267B1 (social feed quality), US8868565B1 (click duration calibration), US20150234930A1 (Ads functional extensions). WebFormer = paper **Meta-led** (WWW 2022, 1 đồng tác giả Google — vì thế xuất hiện trên research.google), không phải "Google's Web Page Transformer"; **WebRef ≠ WebFormer** (Webref = hệ entity annotation trong leak). ⚠️ US12393768B2 (LAMPRET) KHÔNG chứa chữ "cards" — "structured information cards" là diễn giải Koray, dùng như design pattern thì được nhưng đừng cite là patent text. Fact-check đầy đủ: `wiki/sources/research-2026-07-sel-visual-semantics-verification.md` (12 verdicts).

---
