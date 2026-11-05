# Chia lane dọn footprint — 4 lane, mỗi lane một tập file

Mục đích: dọn trong một đêm với 4 agent song song mà không đè nhau. Nguồn: site agency mẫu 05/11/2026 (70 mu-plugin, 194 file theme AI đã chạm; 4 lane xong trong 15 phút, 0 lỗi production).

## Bảng lane

| Lane | Model | Sở hữu | Việc | Kiểm riêng |
|---|---|---|---|---|
| `cmt-out` | Opus high | Các mu-plugin và file JS/CSS có comment lọt ra HTML (danh sách từ audit mục "nguồn comment lọt") | Xoá comment trong chuỗi echo, heredoc, file bị nhúng nguyên văn; bỏ regex "xoá comment lúc chạy"; bỏ khối chết đã xác minh trên HTML sống; docblock ≤ 3 dòng | `footprint_count.py` trên 6 trang: comment VI trong khối của lane = 0; số khối script không đổi; JS parse được (acorn) |
| `docblock-dead` | Sonnet high | Mọi mu-plugin còn lại (trừ 2 lane kia) + thư mục dữ liệu chết | Docblock ≤ 3 dòng; bỏ từ quy trình trong comment PHP; quarantine file và thư mục chết | So token 100%; `php -l`; 4 trang 200; khối inline của lane giữ nguyên byte |
| `theme-fix` | Sonnet high | Toàn bộ theme trừ file JS của `cmt-out` | Lỗi HTML mức thấp (id trùng, thẻ đóng sai, `<main id>`, 404.php thiếu main, script chết), khối `if (false)`, file v1 song song → quarantine, comment theme có dấu vết quy trình | Diff sau khi bóc comment chỉ gồm việc đã nêu; 6 trang 200/404 đúng; `<main id="primary"` tĩnh |
| `merge-php` | Opus high | 16 mu-plugin PHP thuần → 3 file: `<prefix>-security`, `<prefix>-cache-purge`, `<prefix>-seo` | Gộp giữ nguyên token, thứ tự khối = thứ tự nạp cũ; liệt kê hook cùng tên với file ngoài tập gộp; MOVES 16 file | Mốc trước/sau: mã HTTP 9 URL (phân trang, trailing slash, search, 404), header CSP, meta generator, icon, robots/canonical bản cache, trang đăng nhập, danh sách role |

## Luật chia

- Mỗi file có đúng một lane chủ. Liệt kê tập file của `cmt-out` và `merge-php` trước, phần còn lại thuộc `docblock-dead`. Theme thuộc `theme-fix`, trừ file JS mà `cmt-out` phải sửa.
- Lane `merge-php` không nhận file có `ob_start`, `litespeed_buffer_*`, in CSS/JS: các file đó chờ bước gộp perf (bước 5 của phương án, rủi ro cao hơn).
- Không đưa vào đêm dọn: chuyển CSS/JS inline ra file (cần A/B PSI), bỏ link giả `span role="link"` (quyết định SEO), bỏ jQuery CDN trong template (10+ template), bỏ nhúng CSS cho bot. Ghi vào "chờ người duyệt".
- Việc lane phát hiện ngoài BRIEF (ví dụ comment sót ở file lane khác) → phiên chính vá bằng một lượt `orch` riêng sau khi mọi lane xong, EXPECT lấy md5 hiện tại trên server.

## Phiên chính sau khi lane xong

1. Vá chỗ sót (lượt `orch`).
2. Purge toàn danh sách path theo lô ≤ 12, 1 request bỏ cache sau mỗi lô, nghỉ 2 giây. Làm nóng `guest-d,guest-m`. Purge CDN theo cùng danh sách.
3. Tải lại cùng bộ URL, `compare.py`, Jev `code-comment-leak` trên HTML sau và mu-plugin sau. `health.sh` 0/0. Robots và canonical bản cache không đổi ở ≥ 12 path.
   Cột `css_bytes` hay `inline_style` tăng sau purge: so id khối style trước/sau (`scan_html.json` → `style_sizes`). Khối mới có id của plugin cache (ví dụ `litespeed-ccss`) là tính năng đang chờ của plugin (comment `CCSS in queue` ở bản trước) lộ ra khi purge, không phải do lane. Ghi vào handoff mục "ngoài phạm vi" kèm md5 khớp file CCSS trên server, không quy cho đợt và không tự tắt cấu hình. Khối CCSS làm plugin chuyển CSS sang tải không chặn (`rel="preload" as="style"`): đo PSI mobile 3 lượt trang đó và đọc `layout-shifts`. Site mẫu 05/11/2026: trang chủ 97 → 83, CLS 0,28 ở ảnh hero mobile; trang chưa có CCSS giữ 95.
4. Handoff cho reviewer ngoài: trước/sau theo số, file đổi, rollback, việc chưa làm, cách tự kiểm.

## Số tham chiếu từ site mẫu (05/11/2026)

| Chỉ số | Trước | Sau |
|---|---|---|
| mu-plugin | 70 | 57 |
| Comment quy trình lọt HTML (6 trang mẫu) | 3–6 mỗi trang | 0 |
| Comment VI trong code của 6 trang | 19–41 | 0–3 (còn comment dev gốc) |
| Comment có dấu vết quy trình trong mu-plugin | 82 (regex) / 93 (Jev) | 0 |
| File theme đổi | — | 57 (56 chỉ comment + 6 sửa HTML) |
| Lỗi production | — | 0 5xx, 0 fatal |
