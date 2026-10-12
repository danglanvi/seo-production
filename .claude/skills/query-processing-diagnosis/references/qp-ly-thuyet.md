# Query Processing: phần lý thuyết dùng khi chẩn đoán

> Nạp theo pha: mục 2 ở pha C, mục 5 ở pha D, mục 3–8 ở pha F. Chưng cất ngày 12/10/2026 từ deck training Query Processing của GTV, wiki Semantic SEO (trang query journey, Query Template, Canonical Query, Query Augmentation, K2Q) và đợt chẩn đoán 10 dự án (10/2026, đã kiểm chéo). Bản clone không có wiki: file này đủ để làm. Muốn đào sâu thì hỏi SEO Lead hoặc Vincent.

## 1. Ý chính

- Hợp đồng đếm từng keyword, nhưng Google không xử lý từng keyword riêng lẻ. Patent US8645407B2 (Haahr, Baker) mô tả việc gom các query gần nghĩa thành cụm và lấy **tâm cụm** làm gợi ý tìm kiếm. GTV dùng tâm cụm làm **query đại diện** của cả họ keyword.
- **Giả thuyết của GTV** (chưa có nguồn Google xác nhận): Google xếp hạng cả cụm theo một URL chính. Dữ liệu đợt 10/2026 khớp giả thuyết này (một URL giữ phần lớn keyword của một họ), nhưng đó là quan sát, không phải cơ chế đã công bố.
- Hệ quả nếu giả thuyết đúng: đẩy đúng một trang cho một query đại diện có thể kéo nhiều keyword cam kết lên cùng lúc. Một lỗi ở một trạm cũng có thể làm rơi cả họ keyword.
- Vì vậy skill gom bộ keyword cam kết thành **query template**, đọc hạng theo họ, rồi tìm trạm đang hỏng của từng họ.

**Mức bằng chứng.** Tên trạm và patent là tài liệu công khai của Google. Patent mô tả cái Google *có thể* làm, không xác nhận Google đang dùng. Câu nói một cơ chế đang tác động lên dự án là **giả thuyết**. Trên deck, câu đó viết "Giả thuyết: …" và renderer tô đỏ.

## 2. Query template và biến thể

- **Query template** là họ keyword cùng cấu trúc, chỉ khác một ô biến. Ví dụ: "đèn học [hãng]", "đèn mây [size]", "việc làm [tỉnh]".
- **Biến thể** là một cách điền vào ô biến. Ví dụ: "10 inch" là một biến thể của "đèn mây [size]".
- Theo Koray, khi site thắng vài biến thể, Google thử site cho cả họ ("lan trust"). Google chưa công bố cơ chế này. Deck chỉ dùng nó để minh hoạ, không dùng làm bằng chứng.
- Trạng thái của một template trên slide:

| Trạng thái | Điều kiện | Việc thường làm |
|---|---|---|
| `ok` Đã mở | Có keyword Top 3 | Phủ các biến thể còn lại trên cùng URL |
| `up` Đang lan | Số keyword Top 10 tăng rõ trong 4 tuần | Giữ trang, chỉ chỉnh nhỏ |
| `mid` Kẹt | Có keyword trong Top 50 nhưng chưa vào Top 10 | Dò trạm hỏng ở slide Pipeline |
| `no` Chưa có hạng | Phần lớn keyword ngoài độ sâu đo | Thường là lỗi Retrieve hoặc site chưa có trang đúng loại |

## 3. Tám trạm xử lý query (B1–B8)

| Trạm | Google làm gì | Cụm hỏng ở đây khi | Đòn bẩy SEO | Nguồn |
|---|---|---|---|---|
| B1 Tokenize | Tách query thành token | — | Không có đòn bẩy. Deck không có cột B1 | — |
| B2 Segment | Cắt query thành mảnh có nghĩa theo log tìm kiếm | Title, heading không dùng đúng mảnh người dùng gõ: thiếu tên sản phẩm, chen chữ vào giữa, viết không dấu | Đặt đúng mảnh vào title, H1, heading | US9690847B2 |
| B3 Augment | Giữ mảnh chính, thay mảnh phụ bằng biến thể gần nghĩa để mở rộng query | Trang chỉ phủ vài biến thể của template | Phủ biến thể anh em trên cùng URL: bảng, H3, card. Anchor nhất quán | US8577913B1; anchor: US9916366B1 |
| B4 Canonical | Gom cách gõ thành cụm, lấy tâm cụm làm query đại diện. Chọn một URL cho cụm là giả thuyết của GTV | Một họ query chia cho nhiều URL. Google chọn URL khác URL site muốn. URL lật qua lại giữa các lần đo | Chốt một URL, một anchor cho mỗi query đại diện | US8645407B2 |
| B5 Context | Gắn ngữ cảnh địa điểm, thời gian, người dùng | Query địa phương mà trang thiếu tín hiệu địa điểm | Tín hiệu địa điểm có thật (địa chỉ, khu vực phục vụ) | US10146829B2 |
| B6 Câu hỏi (K2Q) | Đổi keyword thành câu hỏi ngầm | Heading không phải câu người dùng hỏi, hoặc câu trả lời nằm xa heading | Heading dạng câu hỏi cho query thông tin, giá, so sánh | US9898554B2 |
| B7 Retrieve | Lấy trang vào danh sách ứng viên, lọc dần trước khi chấm hạng | Trang noindex, canonical sai, trang chờ Cloudflare, chưa crawl lại, chưa go-live, quá giống trang khác: keyword không có hạng dù trang tồn tại | Sửa kỹ thuật. **Làm trước mọi việc nội dung** | US8407239B2 (lọc ứng viên qua nhiều tầng) |
| B8 Passage | Chọn đoạn trả lời dựa trên heading và đoạn ngay dưới heading | Đoạn trả lời dài, lan man hoặc nằm cuối bài | Đoạn trả lời tự đủ nghĩa, đặt ngay dưới heading | US9959315B1 |

**Đọc ma trận cụm × trạm.** Mỗi cụm có tối đa 2 trạm chính và 1 trạm phụ. Cùng là "chưa lên Top", nhưng cách sửa khác nhau:
- Lỗi Retrieve thì sửa kỹ thuật.
- Lỗi Canonical thì chọn lại URL.
- Chỉ lỗi Augment hoặc Passage mới cần thêm nội dung.

## 4. Canonical: một query đại diện, một URL

- Lấy URL Google đang trả cho từng keyword từ công cụ đo hạng. Không lấy URL site "muốn" rank.
- Giữ URL Google đang chọn nếu URL đó đã vào Top 10. Chỉ gom hai URL khi có bằng chứng hai URL tranh nhau: lật URL giữa các lần đo, hoặc hai URL cùng đứng 11–30.
- Hai URL phục vụ hai nhóm người dùng khác nhau thì không ép gộp.
- Quy trình khi Google lật URL:
  1. Ghi hai URL và ngày lật.
  2. Kiểm canonical, internal link và anchor trỏ về mỗi URL.
  3. Chọn URL đại diện theo loại trang của SERP (mục 5).
  4. Dồn anchor và link ngữ cảnh về URL đó. Trang kia chuyển sang vai phụ, hoặc 301 nếu trùng intent.
  5. Chờ 14 ngày rồi đọc median.

## 5. SERP: loại trang quyết định URL nào được đẩy

- Đọc SERP của 3 query đại diện thuộc 3 intent khác nhau. Ghi loại trang của từng kết quả: danh mục, sản phẩm, bài list, bài hướng dẫn, trang chủ, local, video, AI Overview, diễn đàn.
- Kết luận theo dạng: "Top 10 gần như toàn trang danh mục → đẩy category, không đẩy PDP".
- Kiểm SERP overlap trước khi gộp hay tách URL. So top 10 của hai keyword:
  - Trùng từ 6/10 trở lên: một query group, một URL phục vụ cả hai (ngưỡng của wiki Query Semantics và deck training).
  - Trùng 4–5/10: vùng xám. Xem thêm loại trang và intent của SERP trước khi gộp. SOP gộp keyword của GTV năm 2020 dùng mốc 4/10, nay chỉ dùng để đánh dấu cặp cần xem.
  - Dưới 4/10: tách URL.

## 6. Augmentation map, cặp "X và Y", K2Q

- **Augmentation map:** trên trang đang rank, mỗi khối (H1 và gallery, bảng, H3, card, đoạn trả lời) nhắm một nhóm keyword cam kết. Bảng map ghi khối → keyword → hạng hiện tại. Sắp lại khối có sẵn trước khi thêm khối mới.
- **Query "X và Y" / "X hay Y" / "X vs Y":** hai entity anh em. Trang cần đặt hai entity song song (bảng so sánh, hai cột). Không nêu tên đối thủ theo hướng chê.
- **K2Q và passage:** chỉ dùng cho keyword dạng câu hỏi, giá, so sánh. Không dùng heading câu hỏi cho query thương mại thuần. Passage là điều kiện cần, chưa đủ.

## 7. Bảy pattern dùng lại được

| Trạm | Pattern | Khi nào dùng | Lưu ý |
|---|---|---|---|
| B4 | Chốt một URL cho mỗi canonical query | Hai hoặc ba URL cùng nhận một họ query | Giữ URL Google đang chọn nếu đã Top 10 |
| B3 | Phủ biến thể template trên trang đã thắng một biến thể | Trang Top 3–5 cho một biến thể, biến thể anh em đứng 6–20 | Đọc trang live trước. Sắp khối có sẵn trước |
| B2 · B7 | Đưa đúng segment vào title, H1, heading | Title, H1 thiếu mảnh người dùng gõ | Giả thuyết: pilot có nhóm đối chứng trước khi áp cả template |
| B6 · B8 | K2Q và đoạn trả lời ngay dưới heading | Keyword câu hỏi, giá, so sánh ở hạng 4–10 | Không áp cho query thương mại thuần |
| B5 | Context địa điểm | Biến thể địa danh của cùng query | Kiểm SERP overlap trước khi gom. Chỉ ghi dịch vụ có thật |
| B3 | Một anchor trỏ một URL | Anchor lặp sitewide trỏ nhiều URL | Anchor thành synthetic query chỉ khi lặp trên rất nhiều trang (patent ví dụ khoảng 500 trang). Link lẻ chủ yếu giúp PageRank và discovery |
| B7 | Sửa điều kiện retrieve trước mọi topic | Trang có trên site mà keyword không có hạng | Một lỗi retrieve có thể gỡ nhiều keyword cùng lúc |

## 8. Ngoài chữ: internal link, hình ảnh, chức năng, schema

Mỗi việc gắn một nhãn tác động. Không hứa hạng cho việc chỉ là UX.

| Nhãn | Nghĩa | Ví dụ |
|---|---|---|
| Ranking | Ảnh hưởng hạng qua relevance hoặc link | Link ngữ cảnh từ trang mạnh về URL đại diện; anchor đúng mảnh query |
| Kỹ thuật | Giúp Google đọc đúng trang | Sửa JSON-LD hỏng; breadcrumb đúng tên; gỡ noindex trang phân trang |
| Shopping | Điều kiện cho kết quả sản phẩm | Product/ProductGroup có variant, giá, tình trạng hàng |
| UX | Giúp người mua, không đẩy hạng trực tiếp | Slideshow, bộ lọc, FAQ hiển thị |

Câu team hay hỏi, trả lời bằng dữ liệu của dự án:
- Size và biến thể tối ưu ở PDP hay category? Chọn theo loại trang của SERP và URL Google đang trả.
- Có cần giảm click depth, link sitewide hay đổi cấu trúc không? Chỉ khi trang đích nhận ít link nội bộ và nằm sâu hơn 3 click. Link sitewide không phải đòn bẩy hạng mặc định.
- URL đại diện lật thì sửa thế nào? Theo quy trình ở mục 4.
