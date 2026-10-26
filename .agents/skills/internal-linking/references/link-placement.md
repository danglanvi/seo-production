# Vị trí link: đúng ngữ cảnh, ưu tiên supplementary content, bám topical map

Vincent chốt 18/10/2026, sau audit 161 link mới hoặc đổi trên một site WordPress thật. Áp cho link plan mới, thẻ before/after có link và audit link đã đặt. Thuật ngữ: MC = Main Content, SC = Supplementary Content.

## 1. Nguyên tắc

1. Đặt link ở đúng ngữ cảnh. Đoạn chứa link phải nói về chủ đề chính của trang đích. Anchor phải gọi đúng chủ đề đó.
2. Ưu tiên SC. SC gồm 2 mục H2 cuối, FAQ, kết luận, mục giới thiệu công ty hoặc dịch vụ, khối đọc thêm cuối bài, khối cuối trang chuyên mục.
3. Chỉ đặt link ở MC khi link thuộc một trong 5 trường hợp ở mục 2.
4. Bám topical map. Quan hệ giữa trang nguồn và trang đích quyết định vùng đặt link (mục 3).
5. Một trang có tối đa 1 link tới một đích. Link thứ hai tới cùng đích, kể cả link mảnh `#...`, phải có lý do riêng ghi trong plan.
6. Mỗi mục H2 thuộc MC nhận tối đa 1 link mới.
7. Không đặt link ở mở bài, trước câu trả lời chính.
8. Nếu link sai nằm ở MC, bỏ link. Không đổi đích sang trang dịch vụ để giữ link.
9. Nếu không có đoạn SC đạt ngưỡng ở mục 5, giữ liên kết bằng chữ (Link-less Connection) hoặc bỏ link.

## 2. Năm trường hợp được đặt link ở MC

| Mã | Trường hợp | Ví dụ |
|---|---|---|
| MC1 | Node → seed của chính nó (cluster page → pillar) | Trang dịch vụ SEO Hà Nội → trang dịch vụ SEO tổng thể |
| MC2 | Mục tóm tắt chính chủ đề của trang đích: seed → node của nó, hoặc H3 tóm tắt một chủ đề đã có trang riêng | Mục "GEO hoạt động như thế nào" → bài "AI Overview trích dẫn nguồn nào" |
| MC3 | Thuật ngữ mà đoạn dùng nhưng không tự giải thích | "dùng công cụ Kiểm tra URL trong Google Search Console" |
| MC4 | Bước tiếp theo mà đoạn yêu cầu người đọc làm | Mục giá → trang bảng giá. Câu mời liên hệ → trang liên hệ |
| MC5 | Phân biệt nghĩa khi một cụm từ có hai nghĩa | "AI SEO" theo nghĩa tối ưu cho câu trả lời AI → bài GEO |

Bài thông tin chỉ link tới trang thương mại (dịch vụ, báo giá, liên hệ) ở MC theo MC4. Câu chứa link phải là câu mời thật của đoạn. Nếu câu quảng cáo nằm giữa mục hướng dẫn, xoá câu đó. Không đổi nhãn để giữ câu.

Link MC4 hợp ngữ cảnh giữ link thật (D1), hoặc D2 khi form nằm trên cùng trang. Chỉ link giữ lại để tăng chuyển đổi ở vị trí ngữ cảnh không cần link, hoặc nút tới trang noindex, dùng link JS D3 ([link-js.md](link-js.md) §2).

## 3. Quan hệ trên topical map và vùng đặt link

Topical map có 3 tầng: Root (trang chủ) → Seed (pillar của từng cụm) → Node (bài trong cụm). Mô hình topic cluster dùng cùng trục: pillar = seed, cluster page = node. Trang chuyên mục là trang điều hướng của cụm.

| Quan hệ nguồn → đích | Vùng mặc định |
|---|---|
| `len_seed`: node → seed của nó | MC được (MC1). Đặt sau câu trả lời |
| `xuong_node`: seed → node của nó | MC trong mục tóm tắt node đó (MC2). Ngoài mục đó: SC |
| `cung_cum`: 2 node cùng seed | SC. MC chỉ khi thuộc MC3 |
| `khac_cum`: 2 trang khác cụm | SC |
| `outer_ve_core`: bài Outer → trang Core | SC: FAQ, kết luận, mục giới thiệu công ty |
| `core_core`: trang Core ↔ trang Core | SC, hoặc mục giá theo MC4 |
| Trang chưa có trong map | Claude đọc từng ca. Mặc định SC |

Trang chuyên mục: đoạn dưới mô tả chỉ link xuống seed của chuyên mục. Đặt link khác cụm và link dịch vụ ở khối cuối trang, sau danh sách bài.

## 4. Cách xác định MC và SC của một trang

1. Dùng luật tất định trước. H2 có tên FAQ, câu hỏi thường gặp, kết luận, lời kết, tổng kết, giới thiệu công ty, dịch vụ của công ty thuộc SC. Mở bài trước H2 đầu thuộc MC.
2. Đọc title. Mục trả lời đúng lời hứa của title thuộc MC.
3. Mục đứng sau phần trả lời chính và nói chủ đề liên quan thuộc SC, trừ khi title hứa mục đó. Ví dụ: đo lường, xu hướng, tự làm hay thuê ngoài, lỗi thường gặp.
4. Trang dịch vụ: mục giới thiệu dịch vụ, phạm vi việc, phương pháp, giá thuộc MC. Mục lý do chọn, case study, cảm nhận khách, FAQ, liên hệ thuộc SC.
5. Nếu một mục trộn nhiều loại nội dung, xếp theo đoạn chứa link và ghi chú trong plan. Ví dụ: mục văn phòng địa phương có đoạn liên hệ và đoạn quy trình.

## 5. Kiểm hàng loạt bằng Jev

Chạy bước này khi plan hoặc đợt thẻ duyệt có từ 20 link. Nếu ít hơn 20 link, Claude đọc từng link theo mục 1–4.

1. Kiểm kê link: nguồn, đích, anchor, đoạn chứa link, H2 và H3 của đoạn, quan hệ trên map. Với thẻ hoặc bản nháp, `the_link.py check` đếm luật 5, luật 6 và cảnh báo luật 7 ([scripts.md](scripts.md) §1).
2. Chạy rubric `link-placement` (`tools/ai-assist/tasks/link-placement.json`) qua `tools/ai-assist/jev.py`. Rubric có 3 câu: `zone` (MC hay SC), `fit` (đúng ngữ cảnh), `need` (người đọc cần link ở chỗ đó không).
3. Đọc kết quả theo ngưỡng:
   - `zone` từ 0,7: nhận nhãn. Dưới 0,7: Claude xếp mục theo mục 4.
   - `fit` = `natural_bridge` từ 0,85: nhận. Dưới 0,7, hoặc nhãn khác: Claude đọc đoạn. Nếu link ở MC có `fit` dưới 0,7, bỏ link hoặc chuyển xuống SC.
   - `need` chỉ là tín hiệu phụ. Không bỏ link chỉ vì `need` = `optional`.
4. Với link cần chuyển, chạy rubric `link-bridge` trên các đoạn SC của trang nguồn. Đoạn đạt `natural_bridge` từ 0,85 mới vào danh sách Claude chọn. Lọc đoạn và xuất input Jev bằng `bridge_candidates.py build --sc-only`, ghép điểm bằng `merge`. Chuyển link trong thẻ bằng `the_link.py to-sc` ([scripts.md](scripts.md) §1, §3).
5. Cho câu mới hoặc câu sửa chữ qua humanizer và kiểm chính tả trước khi giao.

Hiệu chuẩn 18/10/2026 trên 115 link có vị trí của một site WordPress thật: `zone` từ 0,7 khớp nhãn Claude 80/82, tổng 94/101. Jev hay xếp mục đo lường, mục tự làm hay thuê ngoài vào MC. Jev cũng chấm theo đoạn hơn là theo mục. Với site mới, gán tay 20–50 link trước khi dùng ngưỡng.

## 6. Cột bắt buộc trong link plan

- `Vùng`: MC hoặc SC. Link ở MC ghi thêm mã MC1–MC5.
- `Quan hệ map`: một giá trị ở bảng mục 3.
- `Dạng mã`: D1–D6 theo [link-js.md](link-js.md) §2.
