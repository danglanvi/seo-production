# Link thật hay link JS: chọn dạng mã theo ngữ cảnh

Vincent chốt 19/10/2026, sau khi agent đọc mã nguồn 2 site của Koray Tuğberk Gübür: morethanpanel.com và sutliffstout.com. Áp cho link plan mới, template header và footer, nút chuyển đổi, và audit link đã đặt. File [link-placement.md](link-placement.md) chọn vị trí link. File này chọn dạng mã của link.

## 1. Hai dạng mã

| Thuật ngữ | Mã mẫu | Google xử lý |
|---|---|---|
| Link thật | `<a href="/dich-vu-seo/">dịch vụ SEO</a>` | Google crawl link, tính anchor và chia PageRank. |
| Link JS | `<button type="button" onclick="location.href='/lien-he/'">Nhận tư vấn</button>` | Google không bảo đảm crawl link. Link không chia PageRank và anchor như link thật. Google vẫn có thể đọc URL trong mã JS. |

Link JS giữ phần tử bấm được cho người đọc. Link JS bớt số link mà Google tính, nên đồ thị link nội bộ dồn vào trang cần xếp hạng.

Link JS không chặn index. Muốn chặn index, dùng `noindex`.

## 2. Bảng chọn dạng mã

Chọn theo 3 bước. Ngữ cảnh quyết định dạng mã, loại phần tử thì không (Vincent chốt chiều 19/10/2026):

1. Hỏi link có cần ở vị trí đó không, theo [link-placement.md](link-placement.md). Main content phục vụ intent của người đọc trước, nên ít link. Nếu ngữ cảnh không cần link, bỏ link. Không giữ link đó dưới dạng link JS.
2. Nếu link hợp ngữ cảnh, giữ link thật (D1), kể cả khi link là CTA. Ví dụ: câu mời liên hệ ở cuối mục giá, nút "Nhận audit" ngay sau mục nói về quy trình dịch vụ, dòng "Liên hệ" trong khối điều hướng "Bạn đang cần thông tin gì?". Một CTA không tự động là link JS.
3. Dùng link JS khi cần giữ một link để tăng chuyển đổi ở vị trí mà ngữ cảnh không cần link: nút ở thanh trên trước nội dung, thanh dính, nút nổi, banner, popup, khối CTA lặp theo template. Link JS cũng dùng cho link phụ lặp ở header và footer (D4), link ngoài làm bằng chứng (D5) và đích noindex (§3 luật 5).

| Mã | Ngữ cảnh | Dạng mã | Mẫu trên site Koray |
|---|---|---|---|
| D1 | Link mang tín hiệu chủ đề, link tới trang cần xếp hạng, hoặc CTA hợp ngữ cảnh: link MC1–MC5, link trong SC của bài, menu tới trang dịch vụ, khu vực, bảng giá, breadcrumb, link tác giả ở byline, case study → dịch vụ đã dùng | Link thật, anchor mô tả đích | Sutliffstout giữ 32 link menu tới trang practice area và trang địa phương. MoreThanPanel giữ link thật cho mega menu dịch vụ. |
| D2 | Nút chuyển đổi (MC4) trên trang có form | `<a href="#id-form">` hoặc `<button>` cuộn tới form | Trang dịch vụ có form tư vấn cuộn tới `#contact`. |
| D3 | Link giữ lại để tăng chuyển đổi ở vị trí ngữ cảnh không cần link (thanh trên, thanh dính, nút nổi, banner, popup, khối CTA lặp theo template), hoặc nút tới trang noindex | `<button type="button" onclick="location.href='…'">` | MoreThanPanel: nút "Start Free Trial" mở /signup bằng onclick. |
| D4 | Link phụ lặp toàn site ở header và footer, tới trang không cần xếp hạng cho truy vấn dịch vụ: giới thiệu, đội ngũ, sứ mệnh, tuyển dụng, chính sách, cộng đồng, hoạt động xã hội, tài nguyên phụ | `<span class="non-indexable-link" role="link" tabindex="0" onclick="…">` hoặc `<button>` | Sutliffstout: 26 link trong menu About và Resources (Our Team, Our Mission, Research, Case Results…) và 13 link footer. |
| D5 | Link ra ngoài làm bằng chứng hoặc kênh của công ty: logo báo chí, điểm Google Maps, nền tảng đánh giá, mạng xã hội, nút "để lại đánh giá" | `<div>` hoặc `<button>` với `onclick="window.open('…', '_blank', 'noopener')"` | MoreThanPanel: 12–14 link ngoài mỗi trang (Google Maps, MSN, G2, Product Hunt). Sutliffstout: 5 link mạng xã hội ở footer là `<p onclick>`. |
| D6 | Trích nguồn trong thân bài: số liệu, nghiên cứu, tài liệu của bên thứ ba | Nêu tên nguồn bằng chữ trong câu, không đặt link | Sutliffstout: bài blog viết "according to the CDC", "Medscape reports", không có link ngoài nào trong thân bài. |

Cách đọc bảng:

- Link tới trang liên hệ: câu mời liên hệ hợp ngữ cảnh (MC4, hoặc cuối bài nói về dịch vụ) giữ link thật. Nút liên hệ lặp ở thanh trên, nút nổi hoặc khối CTA template dùng D3, khi trang liên hệ đã có link thật ở menu. Sutliffstout giữ 39–43 nút `<a href="/contact-us/">` mỗi trang, anchor khác nhau, vì trang liên hệ của họ cần xếp hạng.
- Trang chủ, trang chuyên mục, trang blog tổng là trang điều hướng có giá trị. Giữ D1.
- Link `tel:` và `mailto:` giữ dạng `<a href>`. Các link này không chia PageRank sang trang khác.
- Link tới hồ sơ tác giả hoặc nhân sự ở trang ngoài (LinkedIn) giữ link thật với `rel="noopener noreferrer"`. MoreThanPanel làm theo cách này. Link này nối tác giả với thực thể của họ.
- D6: nếu người đọc phải mở trang ngoài để làm theo một bước (ví dụ công cụ của Google), dùng link JS D5 và ghi lý do trong plan. Ngoài trường hợp này, không đặt link ngoài trong thân bài.
- Mục P18 của skill `seo-onpage` đã theo D6 từ 19/10/2026. Checklist bỏ quota 2–4 link ngoài tới .edu, .gov mỗi bài. Bài viết nêu tên nguồn trong câu chứa claim. Bài chỉ đặt link ngoài khi người đọc phải mở trang đó để làm một bước, và link đó dùng dạng D5.
- Website của khách trong case study: mặc định dùng D5. Nếu hợp đồng hoặc khách yêu cầu link thật, giữ link thật và ghi lý do.
- Filter, sắp xếp và phân trang trên trang danh mục ecommerce: xem mục 7.

## 3. Luật bắt buộc

1. Không đổi link D1 sang link JS. Link chủ đề trong thân bài là tín hiệu mà luật vị trí 18/10 đã chọn. CTA hợp ngữ cảnh cũng là D1.
2. Giữ ít nhất một đường crawl cho trang index. Trước khi đổi link sang D3 hoặc D4, kiểm 2 điều: trang đích còn trong XML sitemap, và trang đích còn ít nhất 1 link thật từ trang mẹ cùng chủ đề. Ví dụ: /gioi-thieu/ giữ link thật tới trang đội ngũ.
3. Không dùng dạng lai. Không viết `<a href="…" onclick="…">`, `<a href="javascript:…">` hoặc `<a>` không có href. Google vẫn đọc href trong dạng lai.
4. Không dùng nofollow thay cho link JS. Nofollow không giữ lại PageRank cho trang khác (Matt Cutts, 2009).
5. Trang đích noindex (ví dụ trang form riêng) nhận link JS. Không trỏ link thật tới trang noindex.
6. Link JS phải dùng được bằng bàn phím. Ưu tiên `<button>`. Khi dùng `<span>`, thêm `role="link"`, `tabindex="0"` và xử lý phím Enter. Link mở tab mới phải có `noopener`.
7. Giữ đo lường. Nếu GTM bắt click bằng trigger "Just Links", đổi sang trigger "All Elements" hoặc gắn sự kiện GA4 vào nút. Kiểm sự kiện trước khi publish template.
8. Sửa template header, footer và khối CTA trên staging trước. Đếm số link thật mỗi trang trước và sau khi sửa bằng `link_code_audit.py compare` ([scripts.md](scripts.md) §2).
9. Không đổi trạng thái index của trang chỉ vì trang đó nhận link JS. Koray để các trang sau link JS ở `index, follow` (/our-team/, /faq/, /signup).

## 4. Thứ tự áp

1. Sửa template lặp toàn site trước: header, footer, khối CTA trong template bài viết và template câu chuyện khách hàng. Một lần sửa áp cho mọi trang.
2. Sửa nút chuyển đổi trỏ tới trang noindex.
3. Sửa nút chuyển đổi chèn ngoài ngữ cảnh trong thân trang tiền.

Không sửa link lẻ trong một bài chỉ để đổi dạng mã. Tác động của một link lẻ rất nhỏ.

## 5. Mức bằng chứng

- Google, tài liệu "Link best practices for Google": Google chỉ bảo đảm crawl link `<a href>`. Dạng onclick "không khuyến nghị, nhưng Google vẫn có thể thử đọc".
- John Mueller (SEJ, 15/07/2026): đổi link thành nút để link khác "thắng" là "overthinking". Ông không kỳ vọng thấy thay đổi.
- Koray, kiểm mã nguồn ngày 19/10/2026 trên 9 trang (trang chủ, trang dịch vụ, blog tổng, 4 bài blog): giấu link phụ, link chuyển đổi tới trang không cần xếp hạng và link ngoài làm bằng chứng. Giữ link thật cho trang tiền, link `tel:` và nút liên hệ của Sutliffstout. Thân bài blog có 12–13 link nội bộ thật và không có link ngoài, trừ LinkedIn tác giả ở MoreThanPanel.
- Hai site khác nhau ở header và footer. MoreThanPanel giữ 35 link nội bộ thật ở footer, gồm Our Story, Career, Privacy Policy. Sutliffstout giấu link phụ ở menu và footer. Luật D4 theo mức của Sutliffstout.
- Kết luận: bảng ở mục 2 là khung thực hành của Koray, không phải luật Google. Lợi ích chính là đồ thị link gọn và anchor sạch. Không hứa tăng thứ hạng trong plan hay báo cáo.

## 6. Kiểm hàng loạt

Phân việc model: Jev gắn mục đích của phần tử bấm được (rubric `link-purpose` cho link nội bộ, `link-external` cho link ngoài). Mã tất định gắn vùng, trạng thái index và loại trang đích. Claude áp bảng mục 2 và đọc lại dòng cần đọc. Không dùng EmbeddingGemma ở bước này, vì quyết định dựa trên vùng, mục đích và loại trang đích, không dựa trên độ giống nghĩa. Repo này chưa có rubric `link-purpose` và `link-external` trong `tools/ai-assist/tasks/`. Nếu thiếu rubric, Claude gắn mục đích từng phần tử theo mục 2 và ghi giới hạn trong output.

1. Kiểm kê mọi phần tử bấm được: vùng (header, mega menu, MC, SC, footer, popup), dạng mã hiện tại, đích, anchor. Gộp template lặp thành 1 dòng. Chạy `link_code_audit.py scan` trên HTML đã lưu, không kiểm kê tay ([scripts.md](scripts.md) §2).
2. Gắn đặc điểm đích bằng mã: index hay noindex, trang tiền hay không (theo topical map), số link thật còn lại tới đích, có trong XML sitemap không. Script gắn index (`--noindex` hoặc meta robots), sitemap (`--sitemap`) và số link thật. Claude gắn trang tiền theo topical map.
3. Link nội bộ trong thân trang trỏ bài blog hoặc chuyên mục nhận D1 tất định. Chạy Jev `link-purpose` cho phần tử trỏ trang tiền, trang liên hệ, trang form, popup và mọi nút. Nhận nhãn từ 0,5, gộp `conversion` với `offer` khi cần. Phần tử header, footer gắn mục đích theo đích.
4. Chạy Jev `link-external` cho link ngoài. Nhãn `citation` nhận D6, `proof` và `social` nhận D5, `author_profile` giữ link thật. Nhãn `tool` và `client_site` cần Claude đọc.
5. Áp 3 bước và bảng mục 2, rồi luật mục 3. Với mỗi nút hoặc CTA, Claude đọc câu và mục chứa nó: hợp ngữ cảnh thì D1 hoặc D2, chèn để tăng chuyển đổi thì D3. Khi nhiều nút, Jev `link-placement` chấm độ hợp ngữ cảnh trước. Claude đọc lại mọi dòng Jev dưới ngưỡng và mọi dòng đổi giữa D1 và D3, D4.
6. Ghi cột `Dạng mã` (D1–D6) vào link plan và thẻ duyệt.

## 7. Trang danh mục ecommerce: filter, sắp xếp, phân trang

Vincent chốt chiều 19/10/2026. Nguồn chính là phân tích faceted navigation của Koray: wiki Semantic SEO `[[Faceted Navigation]]` và `[[sources/ranking-signal-consolidation-koray]]` (JetOctopus, 11/2020). Tài liệu Google bổ sung phần kỹ thuật.

Koray xét filter theo nhu cầu tìm kiếm, không theo vị trí trên trang:

- Filter có lượng tìm thật tạo landing page cho sub-intent của cùng nhóm sản phẩm. Trang này tăng chuyển đổi và authority của web entity trong knowledge domain.
- Filter không kiểm soát sinh hàng triệu URL gần trùng. Phần lớn URL đó xếp hạng cho truy vấn không ai tìm. Web entity phình, crawl cost tăng và PageRank bị chia (PageRank Damping). Koray chặn filter không muốn crawl.
- Case JetOctopus: 40 sản phẩm × 25 filter sinh hơn 3 triệu URL, và traffic giảm 30% trong 3 tuần. Koray đưa cấu trúc về 47 URL (7 danh mục, 40 sản phẩm) và gộp URL thừa bằng 301, 410. Site lấy lại 90% phần mất trong 1 tháng.
- Trong case đó, Koray ghi: URL bị chặn bằng robots.txt vẫn gây dilution, vì máy không gộp được tín hiệu của URL nó không truy cập được. Koray xếp canonical và nofollow vào nhóm gợi ý (hint), không phải lệnh.

Kết luận: filter không có demand không nên sinh URL mà Google thấy. Robots.txt là lớp bảo vệ thêm, không phải cách chính.

| Phần tử | Dạng mã | Điều kiện |
|---|---|---|
| Filter có search demand: thương hiệu trong danh mục, loại sản phẩm, nhu cầu dùng, khoảng giá có người tìm | D1. Làm trang đích riêng: URL sạch, title, H1 và đoạn mở riêng, canonical trỏ về chính nó, có trong XML sitemap. Danh mục mẹ đặt link thật tới trang này. | Kiểm demand bằng GSC, Ahrefs hoặc Google Autocomplete. Kiểm SERP: top 10 có trang danh mục hoặc trang lọc cho truy vấn đó. |
| Filter không có demand: tổ hợp màu × size × giá, chọn nhiều giá trị, còn hàng, số sao | Checkbox hoặc `<button>` trong form. JS cập nhật lưới sản phẩm. Không tạo `<a href>`. | Lưu trạng thái lọc ở fragment `#`. Nếu phải dùng tham số `?`, chặn tham số đó bằng robots.txt. |
| Sắp xếp, số sản phẩm mỗi trang, chế độ lưới hoặc danh sách | `<select>` hoặc `<button>`. Không tạo URL mới. | Nếu đã có tham số, chặn bằng robots.txt. |
| Link sản phẩm trong lưới | D1 | Lưới sản phẩm là main content của trang danh mục. |
| Phân trang | D1: `<a href="?page=2">` | Không để nút "Xem thêm" không có href làm đường duy nhất tới sản phẩm ở trang sau. |
| Breadcrumb, danh mục con | D1 | |

Luật:

1. Không viết filter dạng `onclick="location.href='?mau=do'"`. Google có thể đọc URL trong mã JS (mục 1). Mã JS chỉ cập nhật lưới hoặc fragment.
2. Không chặn bằng robots.txt và đặt `noindex` trên cùng một URL. URL bị chặn thì Google không đọc được `noindex`.
3. Không đưa URL filter không có demand vào XML sitemap, link nội bộ, schema hay hreflang.
4. Trang filter có demand: giữ thứ tự filter cố định, nối tham số bằng `&`. Tổ hợp không có sản phẩm và trang phân trang không tồn tại trả 404 (Google).
5. Site đã có URL filter bị index: gộp theo thứ tự Koray xếp. Thứ tự là 301 kèm sửa link nội bộ và kiểm tra, rồi 301 theo luật đơn giản, rồi 410. Không chặn robots.txt trước khi Google đọc xong mã 301 hoặc 410 của các URL đó.
6. Gắn sự kiện GA4 cho thao tác lọc (mục 3 luật 7).
7. Kiểm bằng log file: tỷ lệ hit của bot vào URL tham số và URL filter (skill `seo-logfile-analysis`, mục crawl waste).

Mức bằng chứng: Google ("Managing crawling of faceted navigation URLs", cập nhật 18/12/2025) khuyên dùng robots.txt hoặc URL fragment khi không cần index URL filter. Google ghi canonical và nofollow "generally less effective in the long term". Google không nói về onclick. Cách làm filter bằng nút là áp dụng mục 2 của file này, không phải luật Google.
