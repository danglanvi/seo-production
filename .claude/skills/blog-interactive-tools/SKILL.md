---
name: blog-interactive-tools
description: "Nhúng công cụ tương tác vào thân bài blog (xem trước SERP, gom từ khoá, checklist, máy tính chỉ số), viết bằng JS thuần. Server in sẵn khung và chữ cho crawler, chỉ nạp ở bài có công cụ, chèn bằng điều kiện MD5, có rollback, đo axe và CLS."
metadata:
  version: "1.1"
---

# blog-interactive-tools — công cụ tương tác trong bài blog

Công cụ trong bài giúp người đọc làm được việc mà bài hướng dẫn: đo độ dài title, gom từ khoá, tính chỉ số quảng cáo. Mỗi công cụ lấy ngưỡng và công thức từ chính bài chứa nó. Công cụ không làm chậm trang và không gây CLS.

Gốc đường dẫn là root repo. File ở `skills/blog-interactive-tools/`:

| File | Việc |
|---|---|
| `scripts/insert_shortcode.php` | Chèn shortcode trước heading neo. `DRY=1` mặc định. UPDATE có điều kiện MD5 nội dung cũ. `SRC` phát lại trên bản backup |
| `scripts/rollback_shortcode.php` | Trả bài về bản trước. Bài đã bị người khác sửa thì chỉ gỡ đúng đoạn shortcode |
| `assets/tools-library.php` | Mẫu mu-plugin có 8 công cụ: `serp`, `kw-group`, `seo-checklist`, `swot`, `fb-cover`, `faq-schema`, `fb-ads`, `alt-text` |
| `tests/replay_insert.php` | Chạy `insert_shortcode.php` ngoài WordPress trên file nội dung, để kiểm vị trí chèn |

## Công cụ hay khối bài

Skill này dựng **công cụ**: code tính toán riêng của bài, chạy bằng mu-plugin và shortcode. Phần lớn nhu cầu tương tác trong bài không cần công cụ riêng. Chọn theo bảng:

| Người đọc cần | Dùng | Nơi có markup |
|---|---|---|
| Xem từng bước, tự kiểm hiểu, đánh dấu việc, chép lệnh | khối doc-kit `.btabs`, `.bquiz`, `.bchk`, `.bcmd` | `skills/wp-xuat-ban-bai/references/khoi-doc-kit.md` |
| Tự chấm theo vài thanh trượt | `.calc` | như trên |
| Xem ảnh chụp cỡ lớn, mở template hoặc bảng tính ngay trong bài | `figure.zoom`, `.tpl` + `data-embed` | như trên |
| Xem quy trình khó hình dung bằng chữ | `figure.vid` có lời và phụ đề, brief từ `semantic-media` | như trên |
| Nhập dữ liệu của mình và nhận kết quả theo công thức của bài (đo title, gom từ khoá, tính chỉ số) | công cụ của skill này | `assets/tools-library.php` |

Cả 2 loại theo cùng luật: server in sẵn chữ, nhãn, link thật và kết quả mẫu; JS chỉ thêm tương tác. Khối doc-kit chạy trên site đã cài mu-plugin doc-kit (`wp-dang-bai`). Màu khối lấy từ biến CSS của site khách, không mang màu GTV sang.

## Khi nào dùng

- Bài hướng dẫn có quy tắc đo được (độ dài, ngưỡng, công thức) và có traffic.
- Muốn tăng thời gian tương tác và lý do quay lại bài, không thêm chữ.
- Không dùng cho trang dịch vụ hay landing bán hàng. Công cụ ở đó làm loãng CTA.
- Không dùng để viết lại nội dung bài. Dùng `wp-content-review-apply`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Danh sách bài và clicks 90 ngày | GSC (`tools/gsc/gsc.sh`) | chọn theo topical map, ghi chưa có số |
| Ngưỡng và công thức trong bài | đọc bài | không làm công cụ cho bài đó |
| Heading neo (cuối mục liên quan) | đọc bài | hỏi |
| Quyền server, staging | `00-client-context/wp-server.md`, `wp-staging-deploy` | chỉ dựng code |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code | chèn shortcode, rollback, QA bằng Chrome, axe, đo CLS | dùng: lượt thử 19/10 phát lại chèn 8 bài, khớp 8/8 vị trí với lần chạy production |
| Claude | chọn bài, đọc ngưỡng trong bài, viết công cụ, viết câu dẫn trong khung công cụ | dùng. Câu dẫn chạy qua bước humanize của dự án |
| Jev, EmbeddingGemma | không dùng | công cụ là code tất định, không cần chấm |

## Luật thiết kế công cụ

1. Server in sẵn khung HTML đầy đủ: nhãn, ô nhập có giá trị mẫu, vùng kết quả cao cố định. JS chỉ đổi chữ bên trong khung, nên khung không đổi chiều cao (CLS 0).
2. Crawler đọc được câu dẫn, nhãn và kết quả mẫu mà không cần JS.
3. JS thuần, không thư viện, không gọi mạng. File người dùng chọn chỉ mở bằng `URL.createObjectURL`. HTML dán vào đọc bằng `DOMParser`, không tải ảnh.
4. CSS in ở `<head>`, JS ở cuối trang, chỉ ở bài có shortcode. Gắn `data-no-optimize="1"` (và `data-no-defer` cho script) để LiteSpeed không gộp hay hoãn.
5. Mỗi công cụ dưới 10 KB chưa nén, không tính phần dùng chung.
6. Ngưỡng là số của chính bài. Số ước lượng (ví dụ pixel cắt title) ghi rõ là ước lượng.
7. Mỗi bài tối đa một công cụ, đặt cuối mục liên quan, trước heading neo. Không thêm đoạn văn mới vào bài.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'ssh,wp-cli,node,chrome,axe,gsc?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu thiếu `ssh` hoặc `wp-cli`, chỉ dựng công cụ và chạy thử bằng file HTML local.

### Bước 1 — chọn bài và công cụ

1. Lọc bài hướng dẫn có quy tắc đo được, xếp theo clicks 90 ngày.
2. Mỗi bài ghi: tên công cụ, heading neo, ngưỡng và công thức trích từ bài.
3. Ghi `plan.json`: `{"<post_id>": ["<tên công cụ>", "<đầu chữ heading neo>"]}`.

### Bước 2 — dựng và kiểm trên staging

1. Viết công cụ theo luật thiết kế, dựa trên mẫu `assets/tools-library.php`.
2. Deploy mu-plugin lên staging bằng `wp-staging-deploy`.
3. Chèn shortcode trên staging:

   ```bash
   sudo -u www HOME=/tmp/wpcli-home PLAN=plan.json SC=<tiền tố>_tool DRY=1 <php> /usr/local/bin/wp --path=<staging> eval-file insert_shortcode.php
   ```

   Đọc trường `ctx` của từng bài. Mỗi bài phải có đúng 1 heading neo. Chạy lại với `DRY=0 BK=<thư mục>`.
4. Kiểm từng công cụ: điền input thử, so kết quả với công thức của bài, axe 0 lỗi trong khung, chiều cao khung trước và sau khi nhập không đổi, không lỗi console.

### Bước 3 — production

1. Trình bảng công cụ, bài, ngưỡng và ảnh chụp cho người duyệt.
2. Khi được duyệt: deploy mu-plugin, chèn shortcode với `DRY=0 BK=<thư mục>`, purge theo URL.
3. Kiểm lại trên production: HTTP 200, có khung, không còn shortcode thô, CLS mobile 3 lượt trước và sau, axe.
4. Ghi lệnh rollback vào báo cáo.

### Rollback

1. Chạy `rollback_shortcode.php` với `DRY=1`, rồi `DRY=0`, cùng `BK` của lần chèn.
2. Sau đó mới chuyển mu-plugin ra khỏi `mu-plugins/`. Gỡ mu-plugin trước thì trang in nguyên chuỗi shortcode.
3. Purge các URL đã chèn.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] Ngưỡng và công thức của công cụ trùng số trong bài.
- [ ] Khung in từ server, chiều cao không đổi khi JS chạy.
- [ ] Không gọi mạng, không thư viện, mỗi công cụ dưới 10 KB.
- [ ] `insert_shortcode.php` chạy `DRY=1` và mỗi bài có đúng 1 heading neo.
- [ ] axe 0 lỗi và CLS không đổi trên staging.
- [ ] Có thư mục backup và lệnh rollback.

## Output

- mu-plugin công cụ, `plan.json`, log chèn (`before.json`, `after.json`).
- Bảng kiểm từng công cụ: kết quả với input thử, axe, CLS, ảnh desktop và mobile.
- Danh sách mâu thuẫn số liệu phát hiện trong bài, gửi người phụ trách nội dung.

## Gate

- Không chèn lên production khi chưa có người duyệt.
- Không ghi đè bài mà người khác vừa sửa. Câu UPDATE có điều kiện MD5 đã chặn việc này.
- Không thêm tracking sự kiện cho công cụ khi chưa được duyệt.

## Anti-patterns

- Dựng khung bằng JS sau khi tải trang. Crawler không thấy gì và trang bị CLS.
- Nhúng iframe công cụ từ site khác.
- Đặt nhiều công cụ trong một bài.
- Ngưỡng của công cụ lệch với số trong bài.

## Changelog

- v1.1 (2026-10-31): mục "Công cụ hay khối bài": chọn giữa công cụ riêng và khối doc-kit (tab, quiz, checklist, nút Chép, `.calc`, phóng ảnh, khung xem trước, video). Phóng ảnh và khung xem trước thêm vào `doc-kit.js` (`wp-dang-bai` 1.2.4), chạy thử trên bài tài liệu nội bộ về chuẩn outline 31/10.
- v1.0 (2026-10-19): bản đầu, gom từ 8 công cụ chạy trên production của một site nội bộ (19/10) và cách nạp công cụ theo bài của theme site còn lại. Lượt thử: `insert_shortcode.php` phát lại trên nội dung trước khi chèn cho đúng vị trí và kiểu bài 8/8.
