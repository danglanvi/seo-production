# Sửa theo lô lớn rồi mới đo PSI

Đọc ở Bước 3 và Bước 4. Từ v1.19, đây là cách sửa mặc định. A/B PSI riêng chỉ còn dùng cho 4 trường hợp ở mục 1. File này là nguồn duy nhất của luật sửa theo lô. SKILL.md chỉ trỏ tới đây.

Nguồn: site bán lẻ mẫu (WooCommerce, theme riêng do agency web dựng, shared hosting LiteSpeed), 29–30/10/2026. Bằng chứng nằm trong instance của site, thư mục `03-audits/technical/toi-uu-pagespeed/`.

- Ban ngày 29/10: sửa bằng mu-plugin và option, không sửa theme, A/B PSI từng việc. Mobile trung bình 16 URL tăng từ 56,4 lên 57,2. Người duyệt chấm "không cải thiện" lúc 21:21.
- Đêm 29→30/10: sửa ở theme theo template, deploy một lô, đo PSI một lần. Mobile tăng từ 56,4 lên 90,4. Desktop tăng từ 87,5 lên 98,1. LCP mobile giảm từ 13,2 s còn 2,2 s. Có 8/16 URL mobile từ 90 điểm (báo cáo v3 của đợt, `do-sau/bang-truoc-sau-3010.md`).
- Lời người duyệt:
  - 29/10 22:31: "chỉnh một lượt lớn, big upgrade hết đi rồi sau đó mới đo lại".
  - 30/10 09:02: "Xử lý hàng loạt xong rồi hãy đo lường PSI lại để xử tiếp. Đừng có A/B test từng cái."
  - 30/10 13:07: "fix một bulk rồi mới chạy PSI test lại, hạn chế cái nào cũng a/b testing".

## 1. Khi nào dùng

- Dùng mặc định cho mọi đợt sửa có từ 2 việc trở lên.
- Bắt buộc khi mobile trung vị dưới 75, hoặc cách mục tiêu từ 15 điểm. Ở mức này, việc nhỏ không đổi được điểm. Phải cắt byte trước LCP ở cấp theme (mục 3).
- Chỉ dùng A/B PSI riêng (`do-dac.md` mục 3) trong 4 trường hợp:
  1. Việc đổi giao diện người dùng thấy, ví dụ header, PDP, font hiển thị khác. A/B để trình ảnh và số cho người duyệt.
  2. Tham số phải chọn theo số đo, ví dụ số giây hoãn GTM.
  3. Thay đổi khó trả lại nhanh, ví dụ cách nạp tracking hoặc config server cấp site.
  4. Lô đo xấu hơn lô trước và cần tìm việc gây tụt (mục 7).

## 2. Sửa theo template, không theo URL mẫu

- URL trong ảnh PSI chỉ là minh hoạ của template. Sửa ở nguồn để mọi trang cùng template nhận bản sửa, theo thứ tự:
  1. Phần dùng chung: header, footer, enqueue, icon, font, tracking.
  2. Từng template: trang chủ, danh mục, sản phẩm, bài, trang tĩnh.
  3. Ảnh toàn site: định dạng, đúng cỡ, srcset.
- Nguồn: người duyệt 29/10/2026 21:45, "chỉnh toàn bộ cho các nội dung/code/files trong từng file template đó để các pages khác cũng tối ưu theo".
- Xin quyền sửa theme hoặc child theme ngay trong plan đầu. Lô chỉ có mu-plugin và option không chạm được font, icon hay thư viện JS mà theme nạp sẵn. Lỗi đã gặp: ban ngày 29/10, nhóm việc ghi "Agent không ghi file theme". Người duyệt mở quyền lúc 21:21, sau một ngày không có kết quả.

## 3. Chọn việc theo byte trước LCP

- Điểm lab mobile chủ yếu theo tổng byte tải trước LCP: HTML, CSS chặn hiển thị, font, ảnh LCP. Đợt mẫu ước lượng khoảng 5 ms mỗi KB. Ban ngày 29/10, A/B từng việc nhỏ không đổi được điểm, vì tổng byte trước LCP vẫn còn khoảng 1 MB.
- Đo byte theo loại trước lô bằng `psi_table.py --detail` hoặc Chrome mô phỏng. Xếp việc theo số KB cắt được.
- Lô đầu của site mẫu (byte mobile, trung vị 16 URL):

| Việc | Trước → sau |
|---|---|
| Font: tự host bộ chữ Việt, bỏ Google Fonts, làm theo cách của web agency mẫu (lớp 4) | 1.180 → 58 KB |
| Font Awesome Pro → SVG inline, chỉ cho icon đang dùng. Bỏ 4 file font hơn 1 MB, nên hết vướng giấy phép bản Pro | gộp trong dòng font |
| Bỏ thư viện slider Slick, thay bằng script gallery riêng | JS ngoài tag Google của cả lô: 142 → 115 KB |
| CSS chặn: CSS gọn theo template (skill `wp-ucss`) | 124 → 45 KB |
| Ảnh: WebP cạnh ảnh gốc (16.000 file), ảnh LCP `eager` + `fetchpriority=high`, ảnh ẩn trong menu không nhận cờ | 215 → 124 KB |
| Hoãn GTM có trần 2 s (lớp 7) | JS Google tag ra khỏi đường tải đầu |
| **Tổng byte trước LCP** (Chrome mô phỏng, 32 lượt) | **975–1.642 → 106–216 KB** |

- UI gọn cho màn đầu cũng thuộc lô: header mobile chỉ còn icon tìm kiếm (gõ vẫn xổ gợi ý), menu desktop gọn hơn, PDP mobile hiện chữ sớm. Việc này đổi giao diện, nên phải dựng mockup và trình ảnh trước/sau. Chỉ áp khi người duyệt chọn. Nguồn: người duyệt 30/10/2026 09:02 và trang quyết lúc 12:26.

## 4. Dựng lô

1. Chép theme về máy, quản lý bằng git. Nhánh gốc là bản sống chụp lại. Mỗi nhóm việc một nhánh, rồi gộp vào nhánh lô. Ghi sha256 từng file sống lúc chụp vào một bảng TSV.
2. Mỗi mu-plugin mới có công tắc tắt bằng đuôi `.off` và có test offline.
3. Xem trước trên server. Site có staging thì dùng staging. Host không có staging thì dùng theme bản sao và mu-plugin xem trước bằng mã (skill `wp-staging-deploy`, `references/khong-co-staging.md`). Xem bằng phiên khách để thấy HTML mà LiteSpeed đã tối ưu.
4. Không dựng bản HTML tĩnh để A/B cả lô khi lô đổi file CSS/JS gộp, thuộc tính ảnh tính theo attachment, hoặc asset nạp theo điều kiện template. Ghép tay dễ sai hơn thứ cần kiểm.

## 5. Kiểm lô không cần PSI

Chạy bộ kiểm trên bản xem trước. Sau deploy, chạy lại trên site sống. Bộ kiểm đạt thì mới đo PSI.

| Bộ kiểm | Nội dung | Đạt khi |
|---|---|---|
| K-HTML | Bộ URL đại diện × 2 thiết bị: mã 200, cache hit ở lượt 2, 0 request tới font hay thư viện đã bỏ, mỗi trang đúng 1 ảnh `fetchpriority=high` và ảnh đó là ảnh LCP, CSS gọn đúng file trong map, loader tag có mặt, byte trước LCP | 0 lỗi chặn |
| K-CHUC | Chức năng mua hàng: gallery, menu, tìm nhanh, giỏ, so sánh, bộ lọc, form (không gửi), checkout tới bước chọn cổng thanh toán (không đặt đơn) | Khớp bản sống trước lô, 0 lỗi console |
| K-TRACK | Mỗi lượt tải có 1 `page_view` GA4 và 1 `page_view` Ads, đủ sự kiện ecommerce, không hoãn tag ở giỏ và checkout | Đủ, 0 hit lọt ra mạng thật |
| K-HINH | Icon có nét. Ảnh chụp so với bản trước lô: chiều cao trang bằng nhau, lệch điểm ảnh sau làm mờ σ = 1 px dưới 0,1% | 0 khối người dùng thấy khác |

- Chặn tracking khi kiểm phải chặn cả `www.google.com/g/collect` và `www.google.com/rmkt/collect`. Trả 204 cục bộ, không abort. Khi bị abort, gtag gửi lại hit sang hai địa chỉ này. Lỗi đã gặp 30/10/2026 05:49–05:59: khoảng 48 `page_view` GA4 và 26 hit remarketing tới Google thật. Phải ghi annotation GA4 cho khung giờ đó.
- Giỏ thử: thêm 1 món rồi xoá. Không đặt đơn, không chạm cổng thanh toán.

## 6. Deploy theo tầng, đo một lần

1. Thứ tự đã chạy:
   1. Theme: backup tgz kèm sha256. So sha256 file sống với bảng lúc chụp. File lệch thì gộp 3 phía.
   2. Ảnh: canary 2 URL, rồi toàn bộ.
   3. CSS gọn.
   4. Purge theo URL toàn site, rồi làm nóng 4 biến thể.
   5. Chạy K-HTML, K-CHUC, K-TRACK, K-HINH trên site sống.
2. Ghi rollback riêng cho từng tầng trước khi chạy. Ghi CHECKPOINT gồm giờ, sha256 và cách gỡ.
3. Đo PSI một lần cho bộ URL đại diện: 3 lượt × 2 thiết bị, ban ngày, sau khi kiểm cache hit. So với mốc trước lô trong cùng khung giờ, đọc `benchmarkIndex`.
4. Lô sau chạy theo cùng vòng. Không đo PSI giữa hai lô.

## 7. Khi lô đo xấu hơn hoặc không đổi

- Đọc `benchmarkIndex` và `parseHTML` của lượt tụt trước khi kết luận (`do-dac.md` mục 2).
- Nếu hiện tượng chỉ PSI thấy và máy local không tái hiện, gỡ cùng lúc mọi nguyên nhân ứng viên trong lô kế, rồi đo một lần. Ca đã gặp 30/10/2026: mốc vẽ đầu 2,33 s ở 16 template chỉ có trên máy PSI. Lighthouse và trace local không tái hiện.
- Nếu lô vẫn xấu hơn, chia lô làm đôi và A/B hai nửa theo `do-dac.md` mục 3. Lặp tới khi tìm ra việc gây tụt. Không A/B từng việc từ đầu.

## 8. Bẫy của lô lớn

- Không đổi `Version` trong `style.css` của theme. Lý do: LiteSpeed purge toàn site.
- Thẻ `<style>` mới trong `<head>` phải có `data-no-optimize="1"`. Lý do: `css_comb_ext_inl=1` gộp thẻ đó vào file gộp, đổi md5 và làm map CSS gọn trượt.
- Đổi thẻ HTML không đổi md5 file gộp. Path trong map CSS gọn vẫn dùng file gọn cũ, có thể thiếu rule cho DOM mới. Chạy lại job tái tạo của `wp-ucss` cho các path đổi DOM.
- LiteSpeed đổi URL sang `.webp` trong `<img>` và `imagesrcset`, nhưng không đổi `href` của preload. Preload không có srcset thì gọi `\LiteSpeed\Media::cls()->replace_webp()`. Lỗi đã gặp: trang chủ tải ảnh LCP 2 lần (`.png` 34,7 KB và `.webp` 21,8 KB).
- Ảnh ẩn trong mega menu dùng chung attachment với banner danh mục có thể lấy mất cờ `fetchpriority`. Loại class ảnh menu khỏi bộ chọn ảnh LCP (xem thêm `plugin-chong-cheo.md` mục 4).
- Plugin có thể phát lại `DOMContentLoaded` sau ajax. Listener mới phải dùng `{once:true}`. Nếu không, sự kiện tracking bị đẩy 2 lần.
- Shared hosting: loadavg là tải của cả máy dùng chung. Đo nền trong ngày trước khi đặt ngưỡng dừng purge và làm nóng. Site mẫu: nền 20–23 trên máy 96 nhân, dừng từ 25. Purge theo URL, mỗi lô tối đa 12 path.
