# Hạng mục "Duyệt web bằng tác nhân" (Agentic Browsing) và accessibility trên PSI

Đọc file này khi PSI báo hạng mục "Duyệt web bằng tác nhân" dưới mức tối đa, hoặc khi người duyệt muốn tối đa cả 5 hạng mục. Nguồn: source Lighthouse 13.5.0 (`core/config/default-config.js`, `core/audits/agentic/`, `report/renderer/report-utils.js`) và lượt làm thật trên site mẫu 2 ngày 18/10/2026.

## 1. Cách tính điểm

- Hạng mục hiện dạng phân số `đạt/tổng`. Audit `notApplicable` không tính vào tổng. Audit `informative` cũng không tính.
- Audit có điểm từ 0,9 là đạt. Audit chuyển từ `notApplicable` sang có điểm mà trượt thì tổng tăng 1, phân số tụt.
- `psi_run.py` mặc định chỉ đo performance. Quét đủ 5 hạng mục: `--categories performance,accessibility,best-practices,seo,agentic-browsing`.

| Audit | Khi nào tính | Điều kiện đạt | Ghi chú |
|---|---|---|---|
| `agent-accessibility-tree` | Luôn tính | Không vi phạm 33 rule axe về tên và ARIA (`link-name`, `button-name`, `label`, `aria-*`…) | Bảng chi tiết chỉ hiện phần tử đầu tiên của mỗi rule. Xem audit `link-name` của hạng mục Accessibility để thấy đủ |
| `cumulative-layout-shift` | Luôn tính | CLS lab ≤ 0,1 | Dùng chung với hạng mục Performance |
| `llms-txt` | `/llms.txt` của origin trả mã < 400 | Có dòng bắt đầu bằng `# `, có ít nhất một link `[chữ](url)`, dài từ 50 ký tự | Lighthouse chờ 2 s. Quá giờ, lỗi mạng hoặc 5xx thì tính là trượt. 404 thì không tính |
| `ard-schema` | Có `/.well-known/ai-catalog.json` trả 200, hoặc có tín hiệu `Agentmap:` trong robots.txt, `<link rel="ai-catalog">` | JSON theo schema ARD (`specVersion: "1.0"`, `entries`) | Spec ARD còn là bản đề xuất và đã đổi tên file. Chỉ làm khi site có agent skill hoặc MCP thật để khai |
| `webmcp-*` (3 audit) | Chrome hỗ trợ WebMCP | Mọi `<form>` có `toolname`, `tooldescription` | Chrome của PSI chưa hỗ trợ (10/2026), nên 3 audit luôn `notApplicable` |

## 2. Việc đã làm ở site mẫu 2 (1/2 lên 3/3 ở 11/11 template)

1. Nút liên hệ nổi chỉ có icon: chữ chú thích có `visibility:hidden`, nên không tính là tên link. Thêm `aria-label` cho từng link (Gọi, Messenger, Zalo). Một lỗi này làm cả 11 template trượt `agent-accessibility-tree` và `link-name`.
2. `/llms.txt` trả trang 404 của WordPress (67 KB, không cache). Lighthouse coi là không có file ở 9 template, nhưng quá 2 s ở 2 template nên tính trượt. Đặt file tĩnh ở web root:
   - Nội dung lấy từ title và meta description đang chạy của trang chính. Không viết claim mới.
   - Cấu trúc theo llmstxt.org: H1 tên site, blockquote tóm tắt, các mục `##` gồm danh sách `- [tên](url): ghi chú`, mục `## Optional` cuối.
   - Kiểm mọi link trong file trả 200.
3. OpenLiteSpeed trả file `.txt` là `text/plain` không có charset. Lighthouse vẫn chấm đạt, nhưng client như Python `requests` đọc tiếng Việt thành ký tự lỗi. Thêm context riêng trong vhost của site, không sửa `mime.properties` chung của server:

   ```
   context /llms.txt {
     location                $DOC_ROOT/llms.txt
     allowBrowse             1
     addDefaultCharset       on
     defaultCharsetCustomized utf-8
     extraHeaders            <<<END_extraHeaders
   Header set X-Content-Type-Options nosniff
   Header set Strict-Transport-Security "max-age=31536000"
     END_extraHeaders
   }
   ```

   Context mới không kế thừa header của `context /`: chép header bảo mật sang. Staging có Basic Auth: chép cả `realm`, `required` sang context mới, nếu không file lộ ra ngoài. Sửa xong chạy `lswsctrl restart`.
4. Không thêm `ai-catalog.json` rỗng. Phân số 3/3 đã tối đa. Catalog rỗng chỉ để lấy điểm và có thể thành trượt khi Lighthouse cập nhật bộ kiểm ARD.

## 3. Accessibility 100

- Màu chữ phụ trên nền sáng thường thiếu tương phản 4.5:1. Tính màu thay bằng công thức WCAG, giữ cùng tông. Site mẫu 2: `#7B8499` thành `#636B7E` (3,5 lên 5,0 trên `#F6F7FC`), đỏ đồng hồ `#D9381E` thành `#C2301A` (4,26 lên 5,18 trên `#FFF3EF`).
- CSS sinh từ nguồn dùng chung: vá ở bước build (hàm riêng trong converter), không sửa nguồn.
- Trang có `content-visibility:auto` (`checklist-theo-lop.md` lớp 5): axe không vẽ được section chưa hiện, nên:
  - Báo nhầm: chữ trắng trên section nền tối bị đọc với nền sáng của trang (tương phản 1,06).
  - Bỏ sót lỗi thật trong section chưa vẽ. Site mẫu 2: bản bật thấy 27 lỗi, bản tắt thấy 34.
  - Cách kiểm: A/B trên PSI bằng 2 bản HTML tĩnh, một bản thêm class tắt `content-visibility` vào `<html>`. Sửa mọi lỗi thật của bản tắt. Section nền tối hay bị báo nhầm thì cho luôn vẽ (`content-visibility:visible`).
- Meta description trống ở trang chuyên mục: Rank Math lấy mô tả chuyên mục. Theme có câu mô tả dự phòng in ra trang thì ghi đúng câu đó vào mô tả chuyên mục, để giao diện không đổi.
