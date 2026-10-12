# Bẫy đã gặp

> Nạp phần Dữ liệu hạng ở pha A, phần Trang thật ở pha E, phần Diễn giải và Deck khi viết ở pha F. Rút từ đợt chẩn đoán 10 dự án GTV, 10/2026. Mỗi bẫy kèm cách tránh.

## Dữ liệu hạng

| Bẫy | Cách tránh |
|---|---|
| Từ khoảng 25/09/2026, nhiều project SpySERP chỉ quét 50 hạng. "Ngoài top 100" thực ra là "ngoài top 50" | Đọc độ sâu từ lệnh `runs`, ghi `measure.depth`. So sánh hai mốc khác độ sâu thì chỉ so trong phạm vi 50 |
| Lần chạy thiếu dữ liệu (ví dụ các đợt 25–27/09 và 03–05/10/2026) làm số tụt giả | Lọc bằng `qp_ranks.py runs`. Đọc median 3 lần chạy hợp lệ, không đọc một ngày |
| Số của một ngày có thể là đỉnh hoặc đáy (một dự án có 68/290 keyword nhảy giữa Top 20 và "không thấy") | Báo cả median và số ngày; ghi dao động vào flags |
| Engine team đo lệch hợp đồng: G1 (desktop) thay vì mobile; vị trí hẹp hơn hợp đồng (một thành phố thay vì cả nước) | Kiểm `engine_config` trong output so với hợp đồng. Ghi lệch, không tự đổi engine báo cáo |
| SpySERP có thể đếm sitelink trong AI Overview thành một hạng organic, trong khi hợp đồng chỉ tính link organic | Keyword có hạng 1–3 bất thường thì mở SERP thật kiểm. Ghi vào flags |
| Bộ keyword và số dòng lệch: sheet KPI ghi 381, bộ hợp đồng 390; hai danh sách 80 keyword khác nhau; mẫu số của một bộ không rõ | Dùng `--keywords` với bộ trong hợp đồng; báo `not_in_export` |
| Volume lệch nhiều lần giữa SpySERP, sheet và Ahrefs (một keyword: 2.400 / 60.500 / 39.000; keyword khác: Ahrefs 2.200, sheet 210) | Không dùng volume để ước traffic hay xếp ưu tiên topic. Volume trên deck lấy từ cột Volume của SpySERP trong `hang.json`; dùng nguồn khác thì ghi nguồn. SpySERP ghi 0 khi chưa lấy volume |
| Export tự động theo lịch của SpySERP hay lọc theo view: project nhiều domain hiện như một domain, hoặc bị phân trang | Export tay bản đủ domain, đủ trang. Kiểm số keyword trong output bằng số trong project |
| SpySERP chia lần chạy theo trang (dòng meta "Schedules Page 1"): một file chỉ có khoảng 10 lần chạy gần nhất. Không có lần chạy quanh mốc 4 tuần trước thì số "ago" về 0 và mọi template thành "Đang lan" giả (đã gặp: 10/16 template, "Top 10: 0 → 21") | `runs` in khoảng ngày và cảnh báo dưới 35 ngày; `table` dừng mã 2. Export thêm trang lịch hoặc khoảng ngày đủ, truyền mọi file vào cùng lệnh; không được thì `--no-compare` |
| Phiên SpySERP hết hạn khi cần export gấp | Lấy tab hạng trong sheet của Lead (dán từ SpySERP), tải thành CSV. Script đọc được dấu phẩy. Ghi nguồn "sheet của Lead, ngày …" |
| Project một domain: lần chạy mới có ít keyword có hạng có thể là SpySERP thiếu dữ liệu, cũng có thể là site rơi thật | Script không tự quyết. `table` dừng mã 3; Lead kiểm trên SpySERP rồi chọn `--keep-recent` hoặc `--drop` |
| Hạng một ngày dao động mạnh với keyword đứng sát Top 10 (một keyword: riêng một ngày #8, median 3 lần #30) | Chip và chữ trên deck dùng median. Verify cảnh báo khi số chỉ khớp một lần chạy |
| SERP lấy qua Firecrawl cho query địa phương lẫn video, tin tức, và không đặt được vị trí đo (ví dụ TP.HCM) | Ghi giới hạn vào `serp.cards[].meta`. Query địa phương quan trọng thì xin Lead chụp SERP đúng vị trí |

## Trang thật

| Bẫy | Cách tránh |
|---|---|
| Cloudflare trả trang chờ "One moment, please…" cho category, kể cả với UA Googlebot | Kiểm title trong output `site_check.py`; thử thêm `curl -A Googlebot`. Đây là lỗi Retrieve P0 |
| Site trả gzip kể cả khi không xin, HTML tải về đọc không được | `site_check.py` đã dùng `curl --compressed` |
| JSON-LD hỏng vì xuống dòng thô trong description, hoặc `@type` viết thường: Google bỏ cả khối | Đọc dòng "JSON-LD … lỗi" trong output; kiểm bằng Rich Results Test |
| Trang phân trang đặt noindex làm sản phẩm trang 2 trở đi mất đường link | Đọc robots của URL `?page=2` |
| Site chưa go-live hoặc vẫn là WordPress mặc định ("Hello world!") | Đặt `measure.has_rank: false`, dùng khối `retrieve` cho lỗi go-live. Không viết topic nội dung khi trang chưa tồn tại |
| Bản thiết kế định thêm khối mà trang live đã có sẵn | Đọc trang live trước khi đề xuất khối mới. Sắp lại khối có sẵn trước |
| Nhiều trang dùng đúng một khung H2 (footprint template) | Không đề xuất nhân khung H2. Ghi footprint vào chẩn đoán B7 |

## Diễn giải

| Bẫy | Cách tránh |
|---|---|
| Hiểu sai US9916366B1: coi mọi link ngữ cảnh là synthetic query | Anchor thành synthetic query chỉ khi lặp trên rất nhiều trang (patent ví dụ khoảng 500 trang). Link lẻ chủ yếu giúp PageRank và discovery |
| Trình bày cơ chế patent như sự thật đang tác động | Viết "Giả thuyết: …". Patent cho biết Google có thể làm gì, không xác nhận Google đang làm |
| Gom biến thể địa danh theo từ điển (hcm, tphcm, tp hcm, hồ chí minh) | Kiểm SERP overlap trước khi gom; geo-synonym phụ thuộc query log |
| Hứa hạng cho slideshow, FAQPage, link sitewide | Gắn nhãn UX hoặc Kỹ thuật, không gắn Ranking |
| Đưa dịch vụ khách không có vào trang để phủ query (ví dụ mail-in) | Chỉ ghi dịch vụ có thật; rủi ro luật bảo vệ người tiêu dùng |
| Trang vừa sửa đã đọc hạng sau vài ngày | Chờ 14 ngày, đọc median. Giữ nhật ký thay đổi theo URL |

## Deck

| Bẫy | Cách tránh |
|---|---|
| Audit chỉ đo phần tràn khỏi khung, không bắt chữ chồng nhau | Chụp slide bảng dài (kế hoạch, ưu tiên) và xem bằng mắt |
| Nhãn domain dài hơn 26 ký tự làm vỡ thẻ SERP | Rút gọn domain; `check` chặn khi vượt |
| Glossary bọc lần xuất hiện đầu của mã topic (T5…). Khi "T5" còn là kỳ đo, tooltip trỏ nhầm topic | Viết ngày cụ thể ("kỳ đo 17–19/10") thay cho mã kỳ |
| Regex trong `gloss` chạy bằng JS với cờ `u`: ký tự escape như `\-` làm hỏng regex | Viết thuật ngữ thường; renderer tự escape |
| Sửa HTML đã dựng: lần dựng sau ghi đè | Sửa JSON rồi dựng lại |
