# Cheat-sheet — Phương pháp keyword research (công đoạn #4 · refresh #24/#29)

> Chưng cất 2026-09-03 từ wiki Semantic SEO (máy master): `sources/gtv-keyword-research-methods-2020.md` (22 method PSP), `keyword-difficulty-koray.md`, `keyword-search-volume-koray.md`, `phantom-keyword-gtv.md`, `us9916366-query-augmentation.md`, `scn-query-document-templates-koray.md`, `lexical-query-semantics-differences-koray.md` + `sop/01-topical-map.md`. Instance không có wiki: file này là đủ để làm; sâu hơn hỏi SEO Lead/Vincent.

## 1. Luật chọn (Vincent chốt 19/07/2026)

- **SERP là trọng tài**: tool grouping (Parent Topic, KD, volume) chỉ là gợi ý. Hai keyword cùng topic khi **~4/10 kết quả top 10 trùng** (title/domain/URL) trên tab ẩn danh → gộp 1 bài; không trùng → tách. Mỗi lần đối chiếu mở tab ẩn danh mới. (= skill `serp-clustering`.)
- **KD là tool-metric, không phải gate.** Ngưỡng KD ≤2 / 0–5 là heuristic 2020 cho site mới. Gate hiện hành = **Phantom keyword**: `allintitle:"keyword"` <1.000 tốt · <5.000 chấp nhận · <500 cho site mới/yếu.
- **Volume tool ở VN không tin cậy tuyệt đối** — dùng để xếp ưu tiên tương đối; chốt bằng GSC (nếu có lịch sử) + SERP thực (bao nhiêu kết quả, có ads/shopping/PAA không).
- **Intent đọc từ SERP thật**, không đoán từ mặt chữ: page type top 10 (cate/product/blog/tool/video) = page type mình phải làm. Mapping stage: Consider/Customer → product/category/service; Discover/Awareness → blog.
- **Topic bổ trợ đẩy topic chính**: muốn rank keyword chuyển đổi phải phủ cụm bổ trợ xung quanh (Core ↔ Outer trong topical map). Chọn topic bổ trợ theo Central Entity + attribute coverage (E-A-V) + query network, không chỉ theo volume.
- **Query augmentation** (patent US9916366): Google mở rộng query bằng đồng nghĩa/ngữ cảnh → viết cho *nhóm query* của một page, không nhồi từng biến thể; GSC là nơi thấy nhóm query thật.

## 2. Chín phương pháp (M1–M9) — dùng khi nào

| # | Phương pháp | Khi nào | Output tối thiểu | Tool |
|---|---|---|---|---|
| M1 | Mở rộng từ seed: phrase match / having same terms / Google Suggest / PAA / related searches | Dự án mới, ít data | ≥500 raw query → lọc RPP (relevance · profit · phantom) | Ahrefs KE, Google ẩn danh, Firecrawl search |
| M2 | Organic keywords + Top pages đối thủ → pivot theo URL | Luôn — URL đối thủ = proxy topic; traffic ước tính ×30–50% | bảng URL · topic · kw · traffic | Ahrefs Site Explorer (credit hạn chế → top 200) |
| M3 | Content gap ≥3 đối thủ | Sau M2 để tìm topic mình chưa cover | danh sách kw/topic thiếu | Ahrefs Content Gap |
| M4 | **GSC query mining**: page ≥2 tháng, query có impression, vị trí ngoài top 10, chưa có trong bài | Site đã có lịch sử; refresh #24/#29 | bảng page · query · impr · pos → chèn/viết mới | GSC 16 tháng (`gsc.sh` / MCP) |
| M5 | **SERP overlap clustering** | Bắt buộc trước khi chốt cluster | cluster đã kiểm SERP | `serp-clustering` |
| M6 | Internal link + `site:domain` đối thủ top 1–3 | Hiểu cụm bổ trợ của người đang rank | sơ đồ cụm đối thủ | Google, crawl nhẹ |
| M7 | Entity/attribute từ Wikipedia + NLP salience | Topic có entity rõ; E-A-V coverage | danh sách entity/attribute cần phủ | Google NL API / `seo-research` |
| M8 | Phantom keyword gate | Chọn kw P1 cho site mới/yếu; offsite guest post (#20) | allintitle từng kw P1 | Google `allintitle:` |
| M9 | Intent bằng SERP thật + page type | Mọi cluster trước khi giao page type | intent + page type + SERP feature | Google ẩn danh |

Dự án mới tối thiểu: M1 → M2 → M5 → M9 → M8. Dự án có lịch sử: M4 → M2/M3 → M5 → M9.

## 3. Thứ tự ưu tiên triển khai

1. Keyword cam kết hợp đồng (gộp theo M5) → 2. cluster nhiều kw cam kết + chuyển đổi + phantom đạt → 3. tầng keyword dài/cụ thể (dễ rank, chuyển đổi cao dù volume thấp) → 4. đánh giá đối thủ thực tế top 5–10 (DR/RD + chất lượng content), không chỉ KD → 5. traffic topic (M2/M3) cho plan traffic FULL (#17, ≥ cam kết +20%).

## 4. Lưu trữ (bắt buộc)

- Kết luận: `05-content-plan/keyword-research/<CLIENT>_keyword-research-<phạm-vi>_v<N>.md` (template `keyword-research.md`).
- Data gốc: `02-raw/seo-data/keywords/<YYYY-MM-DD>_<nguồn>_<mô-tả>.csv` — immutable; đợt mới thêm file mới, không sửa file cũ. Ghi ngày export vì volume/SERP đổi theo tháng.
- Đầu ra nạp vào #4 (`keyword-topic-url-mapping`) rồi #10 (topical map DoD 15 mục).
