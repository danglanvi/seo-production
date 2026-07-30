# QDP Gate — rubric "Query Deserves a Page" (CANONICAL)

> File canonical cho toàn hệ skill (tiền lệ `anchor-ratio-framework.md`). Consumers: `keyword-topic-url-mapping` (chủ nhà — quyết 1 topic = 1 URL), `topical-map-creation` (Step 10c), `programmatic-seo-builder` (gate chống mở triệu trang), `visual-semantic-seo` (Bước 1), `content-refresh` (quyết merge/prune khi decay). Wiki: `[[QDP-QDH-QDS]]`, `[[sources/local-seo-topical-authority-sel-koray]]`.
> Nguồn: Koray — SOP QDP/QDH/QDS + bài SEL 22/07/2026 (public). QDH/QDS = complementary concept từ Germans Frolovs. QDP inspired by QDF (Amit Singhal).

## Câu hỏi gate

Search engine hỏi: *"Should we create an index for this query?"* → SEO hỏi: *"Should we create a page for this query?"* — "Whenever Google creates an index, we create a page for indexing. Parse sai → dilute ranking signals → micro-cannibalization."

## 4 tiêu chí query — chấm ✓/✗ từng biến thể/cluster

| # | Tiêu chí | Cách chấm (GTV operational) |
|---|---|---|
| 1 | **High search demand** | Volume tool (DataForSEO/Ahrefs/GSC impressions) — "high" là TƯƠNG ĐỐI theo market; VN dùng thêm allintitle (Phantom Keywords) khi volume tool = 0. Zero-demand thật → không page (trừ Phantom Keyword có evidence nhu cầu) |
| 2 | **Different entities** | Query chứa entity KHÁC BIỆT so với cluster đang có? "Glock 18" vs "Glock 18X" = khác entity → ✓; "Glock 19/20/21" = biến thể số hiệu nhẹ → ✗ |
| 3 | **Low similarity — WEIGHTED** | KHÔNG phải string similarity. Similarity theo TRỌNG SỐ term (entity importance + demand — paper Bendersky/Najork: "Nike" nặng hơn "running shoes"). Term nặng nhất xuất hiện ở mọi biến thể → similarity CAO dù chữ khác ("1911" case, "direct flights to Istanbul"). Proxy đo được: **SERP overlap** từ `serp-clustering` (≥ ngưỡng chain-merge = high similarity = ✗) |
| 4 | **Recognizable pattern (query template)** | Biến thể thuộc query template có cấu trúc lặp ("[city] [service] lawyer", "Can X cause Y?")? Lưu ý: tiêu chí này GẦN NHƯ LUÔN pass với entity có attribute queries (price/review/problems/repair) — đừng để nó một mình quyết |

**Verdict: ≥3/4 ✓ → QDP (page riêng).** Không đạt → xuống thang:

| Mức | Điều kiện | Hành động |
|---|---|---|
| **QDP — Page** | ≥3/4 | Node riêng trong topical map: URL + title + brief riêng. 1 topic = 1 URL chính (chống cannibalization) |
| **QDH — Heading** | Contextual domain thật nhưng thiếu demand/pattern riêng | H2/H3 trong page cha, giữ query template phrasing + L0 answer → "thăng cấp" thành page được khi demand tăng |
| **QDS — Sentence** | Attribute phụ, không đứng độc lập | 1 câu trong section liên quan |
| **Component** *(mở rộng 2026)* | Query dạng dữ liệu/hành động lặp | **Table / list / form / calculator / converter / filter** — 1 component trả lời cả family ("when does X pollen fly" × 12 tháng = 1 matrix, không phải 12 đoạn) |

## Tiêu chí phía DOCUMENT CLUSTER (đường phụ)

Google cũng construct index mới từ nature của document cluster: (1) **index size** đủ lớn, (2) **vocabulary uniformity** — cluster PR cao + nhiều URL phải share vocabulary, lệch quá thì documents bị phân phối sang index khác, (3) **PageRank** của ranking documents. → SEO: giữ vocabulary uniform trong 1 cluster (cùng term nặng, cùng template) để cluster giữ index riêng.

## Reminders khi áp dụng

- **Term nặng nhất = subject của triples + heading vocabulary** của trang được mở — nếu chấm sai term nặng, cả map lệch.
- **Local**: mọi "[service] + [location]" qua gate — evidence: Melbourne merge 19 trang → +232 queries; Doktorsitesi xóa → +600K clicks; yacht +248% ([[cases/local-seo-sel-cases-2026]]).
- **Programmatic**: gate chạy TRƯỚC khi sinh template × dimension — không sinh trang cho tổ hợp không có query deserve index ("NYC to Erzurum": ~50 search/năm, route không tồn tại).
- **Re-run định kỳ**: QDS hôm nay có thể thành QDP khi demand xuất hiện (trending/seasonal).
- Trang fail gate ĐÃ LỠ MỞ → merge về trang pass gate + redirect; nội dung giữ dạng QDH/QDS/component trên trang đích (playbook `[[Index Pollution]]`).
