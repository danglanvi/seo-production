# DataForSEO Backlinks API — Endpoint Map (verified docs.dataforseo.com 07/2026)

> Path A ưu tiên của `backlink-research`. Base: `https://api.dataforseo.com/v3/backlinks/…` — chỉ **Live method** (POST, kết quả tức thời). Limit: 2.000 calls/phút, 30 concurrent. Sandbox free để test. Filter/sort không tính thêm phí. Verify lại docs khi API đổi version.

## Endpoint map theo bước workflow

| Bước skill | Endpoint | Mục đích |
|---|---|---|
| B1 Profile | `/v3/backlinks/summary/live` | Toàn cảnh profile 1 target (domain/subdomain/page) |
| B1 (lịch sử) | `/v3/backlinks/history/live` | Performance link theo thời gian |
| B2 Velocity | `/v3/backlinks/timeseries_summary/live` | Backlink data giữa 2 mốc ngày |
| B2 Velocity | `/v3/backlinks/timeseries_new_lost_summary/live` | RD/link mới & mất theo tháng |
| B3 Link gap | `/v3/backlinks/domain_intersection/live` | Domain trỏ vào ≥2 targets chỉ định (Link Intersect) |
| B3 screening | `/v3/backlinks/bulk_spam_score/live` · `bulk_ranks` · `bulk_referring_domains` · `bulk_backlinks` | Metrics bulk (tới 1.000 targets/call) — LUÔN dùng cho list lớn |
| B3 (chi tiết) | `/v3/backlinks/backlinks/live` | Từng backlink của 1 target |
| B3 (footprint) | `/v3/backlinks/referring_networks/live` | IPs/subnets gửi link (phát hiện farm) |
| B4 Anchors | `/v3/backlinks/anchors/live` | Anchor texts + stats — lõi anchor consensus |
| B5 Page gap | `/v3/backlinks/page_intersection/live` | Referring pages trỏ vào các URL chỉ định |
| B5 RD đếm | `/v3/backlinks/referring_domains/live` | Data per referring domain — đếm unique quality RDs |
| B6 Assets | `/v3/backlinks/domain_pages_summary/live` | Metrics backlink per page của domain — trang hút link |
| B6 (thô) | `/v3/backlinks/domain_pages/live` | Pages nhiều/ít backlink nhất |
| Đối thủ | `/v3/backlinks/competitors/live` | Sites chia sẻ backlink profile với target |
| Meta | `/v3/backlinks/index` | Kích thước index hiện tại |

## Request keys quan trọng

`target` (bắt buộc — domain/subdomain/URL) · `include_subdomains` · `include_indirect_links` · `exclude_internal_backlinks` (bật để số sạch) · `backlinks_status_type`: `live` (mặc định nên dùng) / `all` / `lost` · `backlinks_filters` (vd `["dofollow","=",true]`) · `rank_scale` (`one_thousand` để so DR-like).

## Response fields dùng nhiều (summary/live)

- **`rank`** — thang authority DataForSEO (không phải DR Ahrefs — đừng trộn 2 thang trong 1 bảng).
- **`backlinks`**, **`referring_domains`**, `referring_main_domains`, `referring_pages`.
- **`backlinks_spam_score`** — screening prospect.
- `referring_ips`, `referring_subnets` — đa dạng hạ tầng (farm detection).
- **`referring_links_attributes`** — nofollow/sponsored/ugc → tính dofollow ratio.
- `referring_links_types` (anchor/image/redirect/canonical) · `referring_links_platform_types` (blogs/cms/news...) · `referring_links_tlds` · `referring_links_countries`.
- `broken_backlinks`, `broken_pages` — cơ hội reclaim.

## Cost notes

- Ưu tiên **bulk endpoints** cho mọi danh sách >10 targets (1 call thay N call).
- `limit` + `filters` chặt ngay trong request (đừng pull 10.000 rows rồi lọc local).
- Báo user số call + estimate trước khi chạy (Gate #1).
- Ahrefs fallback (Path B): mapping tương đương — summary→`site-explorer-backlinks-stats`, anchors→`site-explorer-anchors`, intersection→Link Intersect UI/export, domain_pages_summary→`site-explorer-pages-by-backlinks`, timeseries→`site-explorer-refdomains-history`.
