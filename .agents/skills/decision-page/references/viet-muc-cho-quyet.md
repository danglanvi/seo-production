# Viết thẻ chờ quyết bằng tiếng thường

Mục đích: viết thẻ mà Lead hiểu ngay lần đọc đầu và chọn được trong 30 giây. Đọc file này ở bước viết `cau-hoi.json`. Trường JSON nằm ở `references/schema-cau-hoi.md`.

Nguồn lỗi: ngày 19/10/2026 lúc 19:53, Lead trả lời trang chờ quyết web site agency mẫu: "các phần còn lại tôi không hiểu ý bạn lắm". Hai mục bị hỏi lại là "Rule chặn PHP trên .htaccess live" và "4 template Elementor còn...". Hai mục đó thiếu bối cảnh, thiếu hậu quả và dùng tên nội bộ.

## 1. Bốn ý của mỗi thẻ hỏi

Mỗi thẻ `question` có đủ 4 ý. Script từ chối thẻ thiếu ý 1, 2 hoặc 3.

| Ý | Trường | Câu hỏi mà ý đó trả lời |
|---|---|---|
| 1. Bối cảnh | `context[]` | Chuyện gì đang xảy ra, ở đâu, bao nhiêu? |
| 2. Nếu bỏ qua | `risk_if_skipped` | Nếu anh không quyết thì sao? |
| 3. Chạm site sống | `touches_live` | Việc này có sửa site, server hoặc config đang chạy không? |
| 4. Hậu quả từng phương án | `options[].consequence` | Chọn phương án này thì điều gì đổi, đảo ngược được không? |

Đặt đúng 1 phương án đề xuất. Viết phương án đề xuất trước.

## 2. Luật viết tiếng thường

1. Gọi tên việc bằng tác dụng, không bằng mã. Mã nội bộ như `M16`, `scn-a1`, `lane-d`, `r7s` chỉ đặt trong ngoặc sau tên thường.
2. Giải nghĩa thuật ngữ kỹ thuật một lần, ở câu bối cảnh đầu. Giải nghĩa bằng việc mà thứ đó làm.
3. Dùng số cụ thể: số trang, số phút, số đồng, số lỗi. Không dùng "nhiều", "đáng kể".
4. Viết một quyết định cho một câu hỏi. Câu hỏi có dạng chọn một, không hỏi mở.
5. Viết `label` của phương án thành hành động: "Áp rule, giữ bản sao 7 ngày." Không viết "Phương án A".
6. Viết `short` ngắn, 2 đến 5 từ. `short` đứng trong câu trả lời, ví dụ `Rule chặn PHP: Áp rule`.
7. Không đưa chi tiết bảo mật lên trang: host staging, slug đăng nhập, IP, mật khẩu. Viết "trang đăng nhập" hoặc "máy chủ staging".

## 3. Minh hoạ cho mỗi thẻ hỏi

Lead chọn nhanh khi thấy việc trên trang thật. Nguồn: 29/10/2026 22:07, Lead hỏi lại vì chưa hình dung được chỗ chèn thẻ HTML; 30/10/2026 12:10, "ghi cụ thể, minh hoạ và cho đề xuất của bạn cho tôi dễ hình dung".

| Loại việc | Minh hoạ | Cách làm |
|---|---|---|
| Đổi giao diện | Ảnh trước và sau ở khổ điện thoại và máy tính | Áp code thật lên trang sống trong Chrome headless (không ghi lên site), chụp cùng vùng. Ghi trong `context` rằng ảnh dựng bằng code chưa đưa lên site |
| Sửa HTML, schema, thẻ ẩn | Ảnh vị trí có khung đỏ quanh khối + khối `code` trước và sau | Chụp trang có viền quanh phần tử, rồi trích đoạn HTML thật đã rút gọn |
| Đổi cấu hình server, plugin, GTM | Khối `code` trước và sau, hoặc bảng giá trị cũ và mới | Trích dòng config thật, che mọi secret, IP, host |
| Đổi theo số đo | Bảng hoặc `bars` có số trước và sau | Số lấy từ file dữ liệu bằng code |

- Đặt ảnh trước và sau thành hai mục liền nhau, `caption` ghi ảnh nào là trước.
- Khối `code` chỉ giữ 3–10 dòng quanh chỗ đổi. Bỏ phần không đổi bằng `…`.
- Dòng `why` nói vì sao chọn đề xuất bằng số hoặc hệ quả, ví dụ "Gỡ lại trong 1 phút, khách không thấy đổi gì".
- Ca tốt: trang tốc độ bản 3 của site bán lẻ mẫu 30/10/2026 12:04. Mỗi thẻ có ảnh dựng bằng code thật áp lên trang sống và số vị trí px đo bằng Chrome.

## 4. Ví dụ trước và sau (site site agency mẫu, mục ngày 19/10/2026)

Ví dụ này chỉ minh hoạ cách viết. Rule trong ví dụ đã áp ngày 19/10/2026. Không lấy ví dụ làm trạng thái hiện tại của site.

Bản cũ chỉ có tên mục và hai nút, dạng như sau:

> **Rule chặn PHP trên .htaccess live.** Áp rule? [Có] [Không]

Bản viết lại:

```json
{"id": "l1", "label": "L1", "title": "Chặn chạy file PHP trong 3 thư mục hệ thống",
 "context": [
   "Ba thư mục hệ thống của site agency mẫu còn chạy được file PHP.",
   "Kẻ tấn công thường đặt mã độc vào thư mục kiểu này rồi gọi file từ trình duyệt.",
   "Rule mới nằm trong `.htaccess`, file cấu hình máy chủ web của site."],
 "risk_if_skipped": "Ba thư mục đó vẫn chạy được mã độc nếu có người đặt file vào.",
 "touches_live": true,
 "blocks": [{"type": "code", "title": "Khối thêm vào .htaccess của 3 thư mục",
   "after": "<FilesMatch \"\\.php$\">\n  Require all denied\n</FilesMatch>"}],
 "questions": [{"text": "Áp rule chặn PHP cho 3 thư mục?", "short": "Rule chặn PHP",
   "why": "Trang không đổi gì với khách, gỡ rule trong 1 phút bằng bản sao.",
   "options": [
     {"label": "Áp rule, giữ bản sao file cũ 7 ngày.", "value": "Áp rule", "recommended": true,
      "consequence": "Trang vẫn chạy bình thường. Gỡ rule trong 1 phút bằng bản sao."},
     {"label": "Chưa áp.", "value": "Chưa áp",
      "consequence": "Không đổi gì. Rủi ro mã độc giữ nguyên."}]}]}
```

Thẻ này có `touches_live: true`, nên trang hiện nhãn "Phải chọn". Câu trống ở thẻ này nghĩa là chưa làm.

## 5. Thẻ không hỏi

- Thẻ `done`: liệt kê việc agent đã tự quyết theo đề xuất. Mỗi dòng ghi việc, nơi ghi và cách đảo ngược. Lead đọc thẻ này để biết việc nhỏ đã xử lý thế nào.
- Thẻ `info`: số liệu chung, ví dụ khối `stats` hoặc `bars`. Đặt trước các thẻ hỏi khi số liệu giúp Lead quyết.
- Bật ô ghi chú cho thẻ `info` hoặc `done` bằng `"note": true` khi Lead cần sửa một dòng trong thẻ.

## 6. Tự kiểm một thẻ

Đọc thẻ và trả lời 5 câu. Một câu "không" thì sửa thẻ.

- Người không đọc chat trước đó có hiểu việc này không?
- Thẻ có số cụ thể không?
- Thẻ có minh hoạ và câu `why` không?
- Mỗi phương án có hậu quả không?
- Lead đã quyết câu này ở bản cũ hoặc trong file quyết định chưa? Nếu rồi, bỏ thẻ.
- Việc này có qua cổng "vấn đề lớn" của workstream không? Nếu không, agent tự quyết và ghi vào thẻ `done`.
