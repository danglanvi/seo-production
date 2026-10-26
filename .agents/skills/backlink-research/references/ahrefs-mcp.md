# Path B: Ahrefs MCP cho backlink-research (kiểm 19/10/2026)

Bảng này ghi công cụ Ahrefs MCP cho từng bước, trường cần chọn và số unit đã đo. Gọi `doc` của connector trước khi dùng công cụ lần đầu.

## Bước → công cụ

| Bước | Công cụ | Tham số chính | Unit đo được |
|---|---|---|---|
| Chọn đối thủ | `site-explorer-organic-competitors` | `country=vn`, `order_by=keywords_common:desc`, select `competitor_domain,keywords_common,traffic,domain_rating` | 15/dòng |
| 1 Profile | `batch-analysis` | select `url,domain_rating,refdomains,backlinks,org_traffic,org_keywords`, tối đa 100 target một lần | 19/target |
| 2 Velocity | `site-explorer-refdomains-history` | `history_grouping=monthly`, 13 tháng | 6/dòng |
| 3 Link gap | `site-explorer-referring-domains` | `history=live`, `order_by=domain_rating:desc`, select `domain,domain_rating,is_spam,traffic_domain,positions_source_domain,dofollow_links,links_to_target,first_seen,dofollow_linked_domains` | 18/dòng; chỉ `domain,domain_rating` 2/dòng |
| 4 Anchor | `site-explorer-anchors` | `history=live`, `order_by=refdomains:desc`, select `anchor,refdomains,links_to_target,dofollow_links` | 8/dòng |
| 6 Linkable assets | `site-explorer-pages-by-backlinks` | select `url_to,title_target,refdomains_target,dofollow_to_target`, loại trang chủ bằng `where url_to neq` | 8/dòng |
| Kiểm unit | `subscription-info-limits-and-usage` | — | miễn phí |

Một lượt research cho 1 site và 4 đối thủ tốn khoảng 8.000 unit.

## Bẫy đã gặp

- Connector trả tối đa 250 dòng mỗi lần, không có offset. Để lấy đủ RD của mình trong dải DR của đối thủ, chia theo dải `domain_rating` (ví dụ `gte 48`, rồi `gte 45` và `lt 48`).
- Gap chỉ đúng trong dải DR đã lấy. Ghi dải DR vào Caveats.
- `output: csv` trả lỗi máy chủ. Dùng JSON.
- Kết quả lớn tự lưu ra file `[{type, text}]`. `bl_research.py` đọc thẳng file đó. Kết quả nhỏ hiện trong chat: chép vào file `{"target", "refdomains"|"anchors"}` trước khi chạy script.
- `traffic_domain` và `refdomains` của từng dòng tốn thêm unit. Chỉ chọn khi bước cần.
- `refdomains-history` là số ròng, gồm RD spam. Không dùng làm nhịp chuẩn khi hồ sơ nhiễm spam.
- Thứ tự `pages-by-backlinks` theo RD bị một mạng spam lớn thổi lên: nhiều trang cùng có 1.000–2.000 RD. Lọc trước khi kết luận tài sản hút link.
- Site nhỏ (ví dụ theaigrowth.io, 3 từ khoá) không có organic competitor có nghĩa. Xin người vận hành danh sách đối thủ.
