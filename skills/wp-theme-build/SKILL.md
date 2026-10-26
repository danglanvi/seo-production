---
name: wp-theme-build
description: "Chuyển HTML hoặc bản thiết kế thành theme WordPress classic tự code: khung code chung, template khoá học, mẫu blog (TOC, tác giả, trích nguồn, chỗ nhúng công cụ), form lead. Kiểm giống hệt: ảnh lệch ≤3% cả trang và ≤1% màn đầu, chữ và mã HTTP khớp 100%."
metadata:
  version: "1.1"
---

# wp-theme-build — dựng theme WordPress native và kiểm giống hệt

Skill này dựng trang WordPress thật từ HTML tĩnh, landing hay bản thiết kế. Nội dung sửa được trong CMS. Theme không phụ thuộc page builder hay plugin trả phí. Skill đo bản dựng lại có giống hệt bản gốc không trước khi đổi giao diện production.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-theme-build/scripts/`:

- `parity.py`: so ảnh, mã HTTP và chữ. Script cần Pillow.
- `contrast.py`: đo tương phản bảng token màu và báo màu ngoài guideline. Script chỉ dùng thư viện chuẩn của Python.
- `measure_ref.mjs`: đo trang tham chiếu và so font. Script cần Node 22 và Chrome. Script dùng `skills/web-qa-gate/scripts/_cdp.mjs`, nên skill `web-qa-gate` phải nằm cạnh.

Test: `tests/test_parity.py`, `tests/test_contrast.py`, `tests/test_measure_ref.py`.

Skill gom từ một theme tự code và mu-plugin core của site nội bộ, dựng 16–18/10/2026.

## Khi nào dùng

- Chuyển landing HTML tĩnh hoặc trang Ladipage thành trang WordPress sửa được trong CMS.
- Thay theme dựa trên page builder hoặc theme trả phí bằng theme tự code.
- Thêm template mới: trang khoá học, trang khối, mẫu blog, form lead.
- Không dùng để gỡ một plugin trả phí lẻ. Dùng `wp-paid-plugin-exit`.
- Không dùng để sửa chữ, meta hay link trong bài. Dùng `wp-content-review-apply`.
- Không dùng để đo tốc độ. Dùng `wp-pagespeed`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Bản gốc: HTML, landing hoặc site đang chạy | thư mục dự án hoặc URL | dừng |
| Quyền server, staging | `00-client-context/wp-server.md`, skill `wp-staging-deploy` | dựng staging trước |
| Danh sách URL cần giữ mã HTTP | sitemap + URL mẫu + biến thể có tham số | dựng danh sách trước khi code |
| Brand guideline: màu, font, logo | file của khách trong `02-raw/client-docs/` | hỏi. Không tự chọn màu |
| 1–2 trang tham chiếu cho trang thiết kế mới (mẫu blog, trang khối) | người duyệt | hỏi trước khi vẽ mockup |
| Người nhận lead, nơi lưu lead | người vận hành | hỏi trước khi dựng form |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code (`parity.py`) | % điểm ảnh lệch cả trang và màn đầu, so mã HTTP, so chữ hiển thị | dùng: lượt thử 19/10 tái tạo bảng lệch ảnh 17/10 (chênh tối đa 1,25 điểm %, kết luận giống 18/18) và danh sách lệch mã HTTP (8/8 dòng) |
| Code (`contrast.py`) | tỉ lệ tương phản WCAG từng dòng bảng token, màu brand ngoài guideline | dùng: lượt thử 25/10 trên 24 cặp màu của site TAG ngày 17/10 khớp script cũ của site 24/24 (chênh ≤0,01). `--brand` bắt màu chàm `#2F3E9E` mà phép đo tương phản cho qua (9,11:1) |
| Code (`measure_ref.mjs`) | cột chữ, font, line-height, mục lục, phần tử dính trên trang tham chiếu | dùng: test offline trên trang mẫu đạt 4/4, gồm trang chặn `scrollTo`. Chưa chạy trên trang thật |
| Jev `ui-visual` | gắn nhãn lỗi giao diện trên ảnh chụp | qua `web-qa-gate`. Jev chỉ xếp ảnh cho Claude đọc, không quyết định. Không dùng Jev đo tương phản: ở site TAG 17/10, `empty_control` gắn cờ 5 ảnh và không ảnh nào có lỗi màu thật |
| Claude | viết code theme, đọc ảnh lệch, quyết định lệch nào chấp nhận | dùng |
| EmbeddingGemma | không dùng | so chữ dùng so khớp chính xác, không dùng độ giống |

## Khung theme

### Kiến trúc

- Theme classic độc lập, không có theme cha. Mọi hàm và selector có một tiền tố riêng của site.
- `functions.php` chỉ khai hằng số và nạp `inc/`. Mỗi file trong `inc/` giữ một việc: `setup`, `settings`, `template-tags`, `walker`, `content`, `blocks`, `post-meta`, `gtm`.
- Trang Cài đặt riêng của theme giữ hotline, email, địa chỉ, nút CTA, danh sách khoá học. Không hard-code thông tin liên hệ.
- `theme.json` khai bảng màu, font, cỡ chữ, độ rộng nội dung cho trình soạn thảo.
- Một mu-plugin core giữ phần không thuộc giao diện: routing, 301, form, mail, schema, bảo mật. Phần này chạy được với mọi theme, nên đổi theme không làm mất 301 hay form.
- Theme không nạp jQuery, Font Awesome hay CSS và JS của plugin ở trang không cần. Trang có form mới nạp asset của form.
- Font tự host, chỉ subset `vietnamese` và `latin`, có font dự phòng chỉnh cỡ để giảm CLS.
- Màu trong CSS lấy từ bảng token màu đã đo (Bước 1b). Không thêm màu ngoài bảng.

### Một nguồn code và file sinh

- Mỗi file dùng chung có một nguồn. Theme cũ và theme mới cùng chạy trong lúc kiểm giống hệt và 7 ngày rollback. Trong thời gian đó, sinh token màu, CSS trang chủ và CSS trang khối từ một nguồn bằng script, rồi ghi vào cả 2 theme.
- Không sửa tay từng bản chép. Sau mỗi lần build, so sha256 các bản chép với nhau. Nếu có bản lệch, build lại từ nguồn.
- Ghi dòng đầu của mỗi file sinh: "Sinh bởi <script> từ <nguồn>. Không sửa tay."
- README của theme có bảng: file sinh, nguồn, lệnh build.
- Sửa ở nguồn rồi build lại. Lần build sau sẽ ghi đè mọi sửa tay trong file sinh.
- Ca thật (site TAG, 17/10/2026): script build sinh lại `home.css` của 2 theme từ bản nguồn. Khối `:root` và `pages.css` có 2 bản chép, mỗi theme một bản. Đợt đổi màu tốn khoảng 12 phút để port thay đổi sang 2 theme.

### Template khoá học (landing)

- Mỗi landing là một trang WordPress dùng template riêng. Nội dung là HTML dựng sẵn trong `post_content`.
- Meta của trang khai CSS, JS, font, schema riêng của landing đó.
- Sinh nội dung bằng script build. Không sửa landing trong wp-admin.
- Không đặt thư mục tĩnh cùng đường dẫn với trang WordPress. Thư mục tĩnh che trang WordPress.

### Mẫu blog

- Sapo 2–3 câu dưới H1. Ảnh đại diện hiện sau sapo và byline, không chèn trong nội dung.
- Mục lục lấy từ H2, gọn, mở và đóng được trên điện thoại.
- Byline có tác giả thật, chức danh, ngày cập nhật. Trang tác giả có schema Person.
- Hộp trích nguồn: nút chép trích dẫn bài theo định dạng có tên bài, tác giả, URL, ngày.
- H2 theo quy ước đổi giao diện: "Câu hỏi thường gặp" thành FAQ mở và đóng được, "Nguồn" thành danh sách nguồn, "Kết luận" thành khung tóm tắt.
- Khối nội dung bằng shortcode: biểu đồ, lời chứng thực, con số có nguồn, checklist, tab, khối CTA.
- Chỗ nhúng công cụ: shortcode `[<tiền tố>_tool slug=""]`. Theme chỉ nạp `tool.css` và `tool.js` ở bài có shortcode đó. Cách viết công cụ: skill `blog-interactive-tools`.
- Cột chữ, font, cỡ chữ và line-height theo số đo trang tham chiếu đã duyệt (Bước 1b).
- Trên điện thoại, một nút nhìn thấy được mở mục lục.
- Trên điện thoại, CTA dính ở đáy màn hình. CTA không che chữ và không che nút mở mục lục.

### Form lead

- Dùng form miễn phí (Contact Form 7) hoặc form tự code trong mu-plugin core.
- Gửi mail tới người nhận đã duyệt. Tiêu đề mail có tên site, tên form, tên và số điện thoại người gửi.
- Lưu lead vào CMS (menu Lead riêng). Đồng bộ Google Sheet nếu người vận hành yêu cầu.
- Chống spam: trường ẩn do JS điền (thiếu trường thì đánh dấu spam), giới hạn tần suất, không dùng captcha làm chậm trang.
- Mặc định form có tối đa 2 trường bắt buộc và 1 trường tuỳ chọn. Thêm trường khi khách yêu cầu.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,pillow,node,ssh,wp-cli,chrome'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu thiếu `pillow`, phần so ảnh không chạy. Nếu thiếu `ssh` hoặc `wp-cli`, chỉ dựng code và không deploy. Nếu thiếu `node` hoặc `chrome`, bỏ phần đo trang tham chiếu và ghi giới hạn.

### Bước 1 — kiểm kê bản gốc

1. Lập danh sách URL: sitemap, URL mẫu mỗi template, URL có tham số, URL cũ đã 301.
2. Chụp mốc mã HTTP của bản gốc: một dòng `<path>\t<mã> <đích redirect>` cho mỗi URL.
3. Chụp ảnh bản gốc ở 2 bề rộng (1440 và 390), tên `<trang>-<a>-<viewport>.png`.
4. Trích chữ hiển thị mỗi trang mẫu vào `<trang>.txt`.
5. Liệt kê shortcode, meta, option mà bản gốc dùng. Theme mới phải giữ hợp đồng dữ liệu này.

### Bước 1b — đo trang tham chiếu và lập bảng màu trước mockup

Làm bước này khi dựng trang thiết kế mới hoặc đổi màu, font. Nếu chỉ port giữ nguyên giao diện, bỏ qua bước này. Lưu file đo vào thư mục evidence của đợt.

1. Đo 1–2 trang tham chiếu mà người duyệt nêu:
   ```bash
   node skills/wp-theme-build/scripts/measure_ref.mjs measure <url tham chiếu> --widths 1440,390 --out <evidence>/ref-<tên>.json
   ```
   Ghi số đo vào brief mockup: cột chữ, font, cỡ chữ, line-height, markup mục lục, nút mở mục lục, phần tử dính trên điện thoại. Script cuộn bằng wheel, vì trang dùng thư viện cuộn mượt có thể bỏ qua `scrollTo`.
2. Kiểm font có subset tiếng Việt. Loại font mà script báo `THIẾU vietnamese`:
   ```bash
   node skills/wp-theme-build/scripts/measure_ref.mjs vi-subset "<Font A>,<Font B>"
   ```
3. So tối đa 6 bộ font trên cùng một đoạn văn, theo số đo tham chiếu. Gửi ảnh cho người duyệt chọn:
   ```bash
   node skills/wp-theme-build/scripts/measure_ref.mjs fonts --ref <evidence>/ref-<tên>.json --fonts "<A>,<B>,<C>" --out <evidence>/so-font.html --shot <evidence>/so-font.png
   ```
   Nếu người duyệt cần xem font trên trang thật, thêm công tắc `?font=<slug>` vào mu-plugin staging và lưu lựa chọn vào cookie. Gỡ thanh chọn font trước khi đổi giao diện.
4. Đọc brand guideline. Lập bảng token màu theo `references/bang-mau-token.md`.
5. Đo bảng màu. Sửa bảng tới khi script báo 0 dòng cần sửa:
   ```bash
   python3 -B skills/wp-theme-build/scripts/contrast.py check <bang-mau.md> --brand <file guideline>
   python3 -B skills/wp-theme-build/scripts/contrast.py check <bang-mau.md> --brand <file guideline> --write
   ```
   Chạy lệnh thứ hai khi người duyệt đồng ý bảng. Lệnh này ghi cột Tương phản vào bảng. Đo nhanh một cặp: `contrast.py pair <chữ> <nền> --size text|large|ui`.
6. Vẽ mockup theo số đo và bảng màu đã duyệt.

### Bước 2 — dựng code trên staging

1. Dựng theme theo mục "Khung theme".
2. Giữ một nguồn cho file dùng chung và file sinh, theo mục "Một nguồn code và file sinh".
3. Deploy lên staging bằng `wp-staging-deploy`.
4. Xem theme mới bằng công tắc cookie trong mu-plugin staging. Theme active trong DB không đổi.

### Bước 3 — kiểm giống hệt

```bash
python3 -B skills/wp-theme-build/scripts/parity.py shots --dir <ảnh> --a <bản gốc> --b <bản mới> --fold d1440=900,m390=844
python3 -B skills/wp-theme-build/scripts/parity.py status --a truoc.tsv --b sau.tsv
python3 -B skills/wp-theme-build/scripts/parity.py text --a <chữ bản gốc> --b <chữ bản mới>
```

- Ảnh đạt khi 2 ảnh cao bằng nhau, cả trang lệch ≤3%, màn đầu lệch ≤1%. `--tol 32` bỏ qua lệch màu khử răng cưa.
- Mã HTTP và chữ phải khớp 100%. Mỗi dòng lệch phải nằm trong danh sách "thay đổi đã biết" kèm lý do.
- Trang cố ý thiết kế lại (404, tìm kiếm) không cần giống hệt. Ghi vào danh sách thay đổi đã biết.

### Bước 4 — QA và đổi giao diện

1. Chạy `web-qa-gate` trên staging.
2. Rà 4 bẫy trước khi đổi giao diện (gặp ở site TAG, 17/10/2026):
   - Staging thiếu plugin của production, ví dụ cache, tường lửa, SMTP. Liệt kê plugin lệch giữa 2 nơi. Ghi phần chưa kiểm được trên staging vào checklist đổi giao diện.
   - Theme mới bỏ CSS và JS của plugin. Quét `post_content` tìm shortcode và thẻ `<style>` dán tay. Shortcode không còn plugin xử lý sẽ hiện thô. CSS dán trong nội dung áp lên cả trang.
   - Template có thể đọc markup trong nội dung, ví dụ header lấy mục lục từ một khối có `id` riêng. Ghi hợp đồng markup này trong README. Nếu đổi markup, kiểm lại hàm đọc.
   - Trình duyệt giữ ảnh và font tới 1 năm khi URL không có version. Khi đổi ảnh hoặc font, đổi tên file.
3. Viết checklist đổi giao diện: backup, chép theme và mu-plugin core, đổi theme, chuyển menu, tắt plugin cũ, purge, kiểm.
4. Đổi giao diện production khi người duyệt đồng ý. Làm vào giờ ít truy cập.
5. Sau khi đổi: chạy lại `parity.py status`, kiểm canonical, gửi 1 lead thử, kiểm GTM, chạy `web-qa-gate`.
6. Giữ theme cũ và plugin cũ ở trạng thái tắt 7 ngày để rollback.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] Mọi thông tin liên hệ và CTA sửa được trong trang Cài đặt. Nguồn lỗi: rà cutover site TAG 17/10/2026, hotline và giờ làm việc ghi cứng trong HTML trang khối và trong file JS.
- [ ] Routing, 301, form, mail nằm trong mu-plugin core, không nằm trong theme. Nguồn lỗi: plan theme site TAG 17/10/2026, routing đặt trong theme thì rollback làm hỏng 230 lượt 301 và URL khoá học.
- [ ] Không còn page builder hay plugin trả phí trong đường hiển thị. Nguồn lỗi: theme cũ site TAG phụ thuộc page builder, plugin permalink trả phí và plugin field trả phí, 17/10/2026.
- [ ] `parity.py` chạy đủ 3 lệnh. Mọi dòng lệch có trong danh sách thay đổi đã biết. Nguồn lỗi: site TAG 17/10/2026, so 324 URL giữa 2 theme thấy 8 URL đổi mã HTTP.
- [ ] Form gửi mail, lưu CMS và chống spam đã thử trên staging. Nguồn lỗi: site TAG 17/10/2026, form production mất lead từ 16/10, vì plugin chỉ ghi Sheet khi mail gửi được. Lead phải lưu vào CMS cả khi mail lỗi.
- [ ] Có checklist đổi giao diện và cách rollback. Nguồn lỗi: site TAG 17/10/2026, 13 trang khoá học trả 404 khoảng 3,5 phút khi chuyển, rollback ngay theo script.
- [ ] Bảng token màu có gốc guideline. `contrast.py check --brand` báo 0 dòng cần sửa. Mọi ngoại lệ có lý do và người duyệt. Nguồn lỗi: site TAG 17/10/2026, màu chàm `#2F3E9E` ngoài guideline lên staging, người duyệt phát hiện bằng mắt; vòng sửa màu tốn 1 agent 21 phút.
- [ ] Mockup và mẫu blog theo số đo trang tham chiếu: cột chữ, font, mục lục gọn, nút mở mục lục trên điện thoại. Nguồn lỗi: site TAG 17/10/2026, mockup đầu vẽ khi chưa đo trang tham chiếu, người duyệt chưa ưng và thiếu nút mở mục lục; chờ 38 phút, dựng lại khoảng 50 phút.

## Output

- Code theme và mu-plugin core trong thư mục dự án, kèm README mô tả file và cách sửa trong CMS.
- Bảng `parity.py` của 3 lệnh, lưu trong thư mục evidence của đợt.
- Danh sách thay đổi đã biết.
- Checklist đổi giao diện.
- Khi có Bước 1b: bảng token màu có cột Tương phản do `contrast.py --write` ghi, file `ref-<tên>.json`, ảnh so font.

## Gate

- Không đổi giao diện production khi chưa có người duyệt.
- Không đổi giao diện khi `parity.py status` còn dòng lệch ngoài danh sách thay đổi đã biết.
- Không đổi mã GTM hay thêm tag tracking khi chưa được duyệt.
- Không xoá theme cũ hay plugin cũ trong 7 ngày đầu.
- Không đẩy CSS màu lên staging khi `contrast.py check` còn dòng cần sửa.

## Anti-patterns

- Dán HTML tĩnh vào trang WordPress rồi bỏ chỗ sửa trong CMS.
- Đặt routing và form trong theme. Đổi theme sẽ làm mất 301 và form.
- Sửa nội dung landing trong wp-admin khi landing được sinh bằng script.
- Kiểm "giống" bằng mắt mà không có bảng số.
- Tự chọn màu ngoài bảng token, hoặc chỉ đo tương phản mà không đối chiếu guideline.
- Sửa tay file sinh, hoặc sửa từng bản chép của một file dùng chung ở 2 theme.
- Vẽ mockup trang mới trước khi đo trang tham chiếu.

## Changelog

- v1.1 (2026-10-25): ui-4 — Bước 1b đo trang tham chiếu (`measure_ref.mjs`) và bảng token màu (`contrast.py` nhận chữ gradient, `references/bang-mau-token.md`), mục một nguồn code và file sinh, 4 bẫy trước khi đổi giao diện, checklist có nguồn lỗi; ca thật 24 cặp màu site TAG 17/10 khớp 24/24.
- v1.0 (2026-10-19): bản đầu, gom từ theme tự code và mu-plugin core của site nội bộ (16–18/10). Script `parity.py` so ảnh, mã HTTP và chữ. Lượt thử trên ảnh và file trạng thái 17/10: bảng lệch ảnh chênh tối đa 1,25 điểm %, kết luận giống 18/18; lệch mã HTTP trùng 8/8 dòng.
