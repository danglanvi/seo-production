# Khối bấm thử doc-kit

Bài trên WordPress không chạy `<script>` riêng. Tài khoản đăng bài không có quyền chèn JS. mu-plugin doc-kit nạp `doc-kit.css` và `doc-kit.js` cho bài có meta `_doc_kit`, và chỉ chạy trong `.doc-kit`. Các khối dưới đây chạy bằng `doc-kit.js`. Bản gốc của JS: `skills/wp-dang-bai/wp/doc-kit/doc-kit.js`.

## Chọn khối theo nội dung của H2

| Nội dung của H2 | Khối | Lý do |
|---|---|---|
| Quy trình nhiều bước, mỗi bước có chi tiết | `.btabs` | Người đọc xem từng bước, trang không dài ra |
| Khái niệm dễ hiểu sai, cần kiểm hiểu | `.bquiz` | Người đọc tự kiểm, có giải thích |
| Việc cần làm, danh sách kiểm | `.bchk` | Đánh dấu được, trang nhớ trạng thái |
| Lệnh, prompt, đoạn mã để chép | `.bcmd` hoặc `.cmd` | Nút Chép |
| Tự chấm, tính nhanh theo vài biến | `.calc` | Thanh trượt và công thức an toàn |
| So sánh nhiều phương án theo tiêu chí | bảng `.tbl` | Đọc ngang được, không cần bấm |
| Ảnh giao diện cần chỉ từng vùng | `.shot` | Ghim số trên ảnh, rê chuột sáng mục |
| Ảnh chụp nhiều chữ, cần xem cỡ lớn | `figure.zoom` | Bấm ảnh để phóng, bấm lại hoặc Esc để đóng |
| Template, bảng tính, tài liệu người đọc cần mở | `.tpl` + nút `data-embed` | Nút mở link thật, khung xem trước nạp khi bấm |
| Quy trình nhiều bước khó hình dung bằng chữ | `figure.vid` > `video` | Video 40–60 giây có lời và phụ đề, đặt đầu mục |

Mỗi bài có ít nhất một khối bấm. Không thêm khối chỉ để có khối: khối phải giúp người đọc làm hoặc kiểm điều H2 nói.

## Markup

Khối rộng thêm class `wide`. Chữ thường của bài nằm trong `<div class="prose">`.

Tab:

```html
<div class="btabs wide">
<div class="btab-bar"><button type="button">Bước 1</button><button type="button">Bước 2</button></div>
<div class="btab-pane"><h4>Tên bước 1</h4><p>…</p></div>
<div class="btab-pane"><h4>Tên bước 2</h4><p>…</p></div>
</div>
```

Số nút bằng số pane. `kiem_bai.py` báo LOI khi lệch.

Quiz:

```html
<div class="bquiz wide">
<div class="qz"><p>Câu hỏi?</p><div class="opts"><button type="button" data-ok>Đáp án đúng</button><button type="button">Đáp án sai</button></div><p class="fb" hidden><span class="res"></span>Giải thích vì sao.</p></div>
</div>
```

Mỗi `.qz` có đúng một nút `data-ok`. Giải thích trong `.fb` nói lý do, không chỉ nhắc lại đáp án.

Checklist:

```html
<div class="bchk wide" data-key="<khoá ngắn, duy nhất trong bài>"><div class="grp">
<label><input type="checkbox"><span>Việc 1</span></label>
<label><input type="checkbox"><span>Việc 2</span></label>
</div><div class="bchk-foot"><span class="bchk-n"></span><button type="button" class="bchk-reset">Làm lại</button></div></div>
```

Thiếu `data-key` thì trang không nhớ ô đã đánh dấu.

Lệnh để chép: `<div class="bcmd"><code>lệnh</code><button type="button">Chép</button></div>`. Khối `.cmd` tự thêm nút Chép.

Công cụ tính:

```html
<div class="calc wide">
<label><span>Biến 1</span><input type="range" min="0" max="2" step="1" value="0" data-i="a"></label>
<label><span>Biến 2</span><input type="range" min="0" max="2" step="1" value="0" data-i="b"></label>
<p>Tổng: <b data-f="a+b" data-u="/4">0</b></p>
</div>
```

- Công thức `data-f` chỉ gồm tên trong `data-i`, số, `+ - * / ( )` và `round()`. Công thức khác không chạy. `kiem_bai.py` báo LOI.
- `doc-kit.css` chưa có style cho `.calc`. Viết CSS riêng trong `<style>` ở `<head>` của bài. `wp_publish.py` gắn tiền tố `.doc-kit` rồi lưu vào meta `_doc_kit_css`.
- Ghi rõ trên khối: đây là khung tự kiểm của brand hay số của nguồn nào. Không đặt ngưỡng đạt khi chưa có dữ liệu hiệu chỉnh.

Phóng ảnh:

```html
<figure class="wide zoom"><img src="…" alt="…" width="1200" height="760"><ol class="sn"><li>Giải thích ghim 1</li></ol><figcaption>Nguồn, ngày chụp. Bấm vào ảnh để xem cỡ lớn.</figcaption></figure>
```

Khung template, xem trước khi bấm:

```html
<div class="tpl wide"><h3>Tên template</h3><p>Dùng để làm gì.</p>
<p><a href="https://docs.google.com/spreadsheets/d/<id>/copy">Tạo bản sao</a> · <a href="https://docs.google.com/spreadsheets/d/<id>/edit">Mở template</a></p>
<button type="button" data-embed="tpl-1" data-src="https://docs.google.com/spreadsheets/d/<id>/preview" data-title="Tên template">Xem ngay trong bài</button>
<div id="tpl-1" hidden data-h="520"><p>Khung trống hoặc báo cần quyền: đăng nhập tài khoản được share, hoặc bấm "Mở template".</p></div></div>
```

- `data-src` chỉ nhận link https của Google Docs, Sheets, Drive, Looker Studio. Link khác không nạp. `kiem_bai.py` báo LOI.
- Link tạo bản sao và mở template là thẻ `<a>` thật trong HTML, để crawler và người không bật JS vẫn mở được.
- CSS của `.tpl` viết trong `<style>` ở `<head>` của bài, như `.calc`.

Video:

```html
<figure class="wide vid"><video controls preload="metadata" playsinline poster="<ảnh poster>.jpg" src="<video>.mp4" width="1280" height="720"></video><figcaption>Xem nhanh trong N giây. Video có phụ đề; bật tiếng để nghe giọng đọc.</figcaption></figure>
```

Video do repo video dựng (brief từ `media-brief` hoặc `semantic-media`). Nén bản web bằng H.264 CRF 22, `+faststart`.

## Kiểm

- `kiem_bai.py` kiểm cấu trúc: quiz có `data-ok`, checklist có `data-key`, tab đủ pane, công thức an toàn.
- `kiem_bai.py` kiểm thêm: nút `data-embed` có phần tử đích và link nằm trong danh sách cho phép.
- `kiem_render.mjs` bấm thử trên theme thật: đổi tab, chọn đáp án quiz, đánh dấu checklist, kéo thanh trượt `.calc`, phóng ảnh `figure.zoom`, mở khung `data-embed`.
- Ca thật 27/10/2026: khối tự chấm của bài pilot viết bằng `<script>` riêng không chạy trên site. Viết lại bằng `.calc` thì chạy ở cả 2 cỡ màn hình.
