# Nguồn link hỏng và schema khớp nội dung hiển thị

Đọc file này ở Bước 3c và Bước 3d của SKILL.md. Gốc đường dẫn là root repo. Script: `skills/technical-seo-audit/scripts/`. Mọi lệnh chỉ đọc. Ghi sửa lên site đi qua skill `wp-content-review-apply`.

## 1. Nguồn của link hỏng hoặc link qua redirect

Mục tiêu: với mỗi URL đích lỗi (3xx, 4xx), biết link nằm ở đâu để sửa tận gốc: bài, template Elementor, menu, footer, trường ACF, hồ sơ tác giả hay file theme.

### 1.1 Đếm từ crawl Screaming Frog

1. Xuất bulk export khi crawl: `--bulk-export "Response Codes:Internal & External:Client Error (4xx) Inlinks,Response Codes:Internal & External:Redirection (3xx) Inlinks"`.
2. Chạy:

```bash
python3 skills/technical-seo-audit/scripts/link_sources.py summarize \
  --inlinks "<crawl>/redirection_(3xx)_inlinks.csv" --inlinks "<crawl>/client_error_(4xx)_inlinks.csv" \
  --site <tên miền> --out-dir <W>/links
```

3. Đọc `summary.json` và `targets.tsv`. Script tách 3 lớp:
   - Nội bộ: sửa link về URL đích cuối.
   - Link ngoài: kiểm đích cuối bằng `curl -sIL` trước khi đổi.
   - Nút chia sẻ, widget chat (Zalo, Messenger, intent của X/Facebook): báo riêng, không gộp vào số redirect nội bộ.
4. Cột `positions` gợi ý nơi chứa: Header, Footer, Navigation thường là menu hoặc template; Content thường là bài, Elementor hoặc trường ACF.

Site mẫu 18/10: 4.544 inlink tới redirect. Sau khi tách: nội bộ 1.815, link khoá học sang domain khác 1.084, chia sẻ/widget 756.

### 1.2 Tìm trong DB WordPress

Cần hồ sơ server ở `00-client-context/wp-server.md` (SSH + WP-CLI). Không có thì dừng nhánh này, ghi "chưa tìm nguồn trong DB".

1. Lấy chuỗi tìm ở `<W>/links/patterns.txt`. Link nội bộ giữ dấu `/` hai đầu (`/seo/seo-offpage/`). Chuỗi không có dấu `/` hai đầu sẽ khớp cả tên file ảnh: site mẫu, "silo-la-gi" khớp "cau-truc-silo-la-gi.png".
2. Chép `scripts/find_sources.php` lên thư mục tạm của server, rồi chạy:

```bash
PAT='/seo/seo-offpage/|online.gov.vn/Home/WebDetails/73931' wp eval-file /tmp/find_sources.php > <W>/links/sources.json
```

3. Đọc kết quả:

```bash
python3 skills/technical-seo-audit/scripts/link_sources.py sources --json <W>/links/sources.json --out <W>/links/sources_live.tsv
```

Script bỏ dòng cảnh báo PHP lẫn ở đầu output, bỏ revision, autosave, bản nháp, option sao lưu. Script gắn nhãn: Elementor template, `_elementor_data`, menu, postmeta (ACF), termmeta, usermeta, JSON-LD.

Bẫy đã gặp (site mẫu 18/10):

- `_elementor_data` lưu JSON với dấu `/` dạng `\/`. Tìm bằng chuỗi thường không thấy. `find_sources.php` tự thêm bản `\/` cho chuỗi có `/`.
- Sửa `_elementor_data` xong phải xoá `_elementor_element_cache` và sinh lại CSS của đúng tài liệu đó. Cache không phải nguồn để sửa.
- Link trong hồ sơ tác giả (usermeta, ví dụ link mạng xã hội) không nằm trong bài. Bản đầu của script không tìm usermeta nên báo "không thấy".
- Chuỗi trong `header_schema` hoặc trường schema là JSON-LD, không phải thẻ `<a>`. Crawl không đếm các dòng này.
- WP-CLI in cảnh báo PHP của plugin vào stdout. Không parse JSON thẳng từ output thô.

### 1.3 Tìm trong file theme và mu-plugin

Chuỗi không thấy trong DB thường nằm trong file PHP của theme (header, footer, template trang) hoặc file tĩnh. Chạy trên server, chỉ đọc:

```bash
rg -n --fixed-strings '<chuỗi>' <web root>/wp-content/themes <web root>/wp-content/mu-plugins
```

Site mẫu 18/10: link footer tới trang đăng ký Bộ Công Thương nằm ở `footer.php` và 6 footer Elementor; link khoá học nằm ở 3 menu item và 3 bài.

## 2. Schema khớp nội dung hiển thị

Google yêu cầu nội dung khai trong structured data phải hiện trên trang. Kiểm này bắt: FAQ schema mà trang không có FAQ, câu trả lời trong schema khác trang, VideoObject khi trang không nhúng video, review chỉ có trong JSON-LD, giá trong Offer không hiện.

### 2.1 Chạy

```bash
# Trích khối schema cần nội dung hiển thị, kiểm tất định
python3 skills/technical-seo-audit/scripts/schema_visible.py extract --urls <W>/urls.txt --save-dir <W>/html --out <W>/schema/blocks.jsonl
# Khối chữ chưa chốt (FAQ, Q&A, review): gửi Jev
python3 skills/technical-seo-audit/scripts/schema_visible.py prepare --blocks <W>/schema/blocks.jsonl --out <W>/schema/jev_in.jsonl
python3 -I tools/ai-assist/jev.py --task skills/technical-seo-audit/tasks/schema-visible.json \
  --in <W>/schema/jev_in.jsonl --out <W>/schema/jev_out.jsonl --budget 0.05
# Ghép kết quả qua cổng của registry
python3 skills/technical-seo-audit/scripts/schema_visible.py decide --blocks <W>/schema/blocks.jsonl \
  --jev <W>/schema/jev_out.jsonl --fail-gate <cổng> --out <W>/schema/report.tsv
```

`--urls` chỉ GET trang công khai. Đã có HTML lưu thì dùng `--html-dir` (file `.html` kèm file `.url` cùng tên).

### 2.2 Luồng quyết định

| Khối | Cách chốt | Kết quả |
|---|---|---|
| Mọi câu hỏi, câu trả lời, bước, review khớp nguyên văn | Luật | ĐẠT |
| Không câu hỏi nào hiện, hoặc câu hỏi hiện mà câu trả lời không khớp | Luật | FAIL |
| Schema khai mục rỗng | Luật | FAIL |
| FAQ, Q&A, review còn lại | Jev `schema-visible`: p(partial) + p(none) từ cổng | FAIL |
| Dưới cổng, và mọi khối HowTo chưa chốt | Claude đọc trang | CẦN XEM |
| Rating, giá, video | Luật (số, mã video). Không gửi Jev vì Jev kém so số | ĐẠT / FAIL |

- AggregateRating gắn vào Organization hoặc LocalBusiness: ghi chú "Google bỏ qua review tự đánh giá". Không tính là FAIL hiển thị.
- Giá đọc được dạng "15 triệu", "1,5tr", "999k", "3.000.000đ".
- Chữ trong accordion vẫn tính là hiện. HTML lưu không render JS: trang dựng FAQ bằng JS cần kiểm thêm bằng trình duyệt trước khi kết luận FAIL.

### 2.3 Hiệu chuẩn

- Rubric `schema-visible` 2026-10-19.1, câu hỏi `shown`. Cổng FAIL = p(partial) + p(none). Đọc cổng theo thứ tự: `00-client-context/model-calibration.json` → `tools/ai-assist/calibration-defaults.json` → chưa có thì Claude đọc mọi khối chưa chốt.
- Số đo gốc 19/10 (140 khối của 44 site công khai, gold gán mù trước Jev):
  - Luật ĐẠT 59/59 đúng, luật FAIL 23/23 đúng.
  - Cổng FAIL 0,7 chọn trên dev và holdout, kiểm trên holdout h3 chưa xem: 5/5. Tổng 29/29 mẫu qua cổng đúng, cận dưới Wilson 0,883.
  - Jev chốt thêm 14/58 khối chưa chốt. 44 khối còn lại Claude đọc.
  - Cổng ĐẠT p(all) ≥ 0,55 cho FAQ: 9/9 đúng nhưng mẫu dưới 10. Chưa dùng.
  - HowTo: Jev gắn "all" sai 3/3 ca ở holdout. Không dùng Jev cho HowTo.
- Site khách mới: gán 40 khối gold trước khi tin cổng (skill `model-calibration`).

## 3. Bẫy của bộ trích HTML

- Plugin lazyload lồng `<noscript>` không đóng. Bộ trích bản đầu bỏ chữ trong `<noscript>` nên mất chữ cả trang và báo FAIL sai. Bản hiện tại không bỏ `<noscript>`.
- Yoast tách câu hỏi FAQ thành node riêng trong `@graph`, `mainEntity` chỉ chứa `{"@id": ...}`. Script giải tham chiếu `@id`.
- Plugin lưu schema mất dấu `\`: chuỗi `u003cstrongu003e` thay cho `<strong>`. Script bỏ chuỗi này khi so.
- Câu hỏi nằm chung khối dài với câu trả lời (không có thẻ heading) làm luật tất định bỏ sót. Khối này rơi vào nhóm chưa chốt và đi qua Jev hoặc Claude.
