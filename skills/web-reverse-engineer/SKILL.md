---
name: web-reverse-engineer
description: "Soi cách một plugin, theme WordPress, theme hoặc app Shopify, web app làm một tính năng, có bằng chứng file:dòng, rồi lập plan tự dựng lại bằng code riêng. Dùng khi cần hiểu hoặc chép hành vi một tính năng web mà không có tài liệu."
metadata:
  version: "1.0"
---

# web-reverse-engineer — hiểu tính năng web rồi tự dựng lại

Skill này trả lời câu "tính năng X chạy thế nào" bằng bằng chứng: file, dòng code, request mạng. Sau đó skill lập plan dựng lại bằng code riêng trong theme, mu-plugin hoặc section Shopify. Công cụ chính là CLI `rea` (REA, package npm `rea-agents`) cho phần JS và trình duyệt. REA không phân tích PHP và Liquid, nên agent đọc thẳng các file đó.

Gốc đường dẫn là root repo. Script: `skills/web-reverse-engineer/scripts/rea_cdp.sh`.

## Khi nào dùng

- Cần làm tính năng giống plugin, theme hoặc site khác: popup, bộ lọc, calculator, mega menu, form nhiều bước, hiệu ứng scroll.
- Cần thay plugin trả phí bằng code riêng và phải biết plugin đang làm gì. Phần kiểm kê và đổi dữ liệu theo skill `wp-paid-plugin-exit`.
- Cần biết một app Shopify chèn script, request và DOM gì vào storefront.
- Cần so hai version của plugin hoặc bundle JS để biết thay đổi gì.
- Không dùng khi tài liệu chính thức đã trả lời câu hỏi. Đọc tài liệu trước.
- Không dùng để sửa lỗi CSS hoặc giao diện trên site của mình. Dùng `wp-ui-fix`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Tính năng cần soi, mô tả bằng hành vi người dùng thấy | Người giao việc | hỏi, không đoán |
| Nguồn: URL trang có tính năng, hoặc file plugin/theme, hoặc file HAR | Người giao việc, server qua SSH, wordpress.org | hỏi |
| Đích dựng lại: theme, mu-plugin, section Shopify, app riêng | Người giao việc | ghi "chưa chốt" trong plan |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | Phân loại listener, request | Không dùng. Việc chính là đọc code và suy cơ chế. Chưa có rubric hiệu chuẩn. |
| EmbeddingGemma 2 | Tìm hàm giống nhau giữa 2 bundle | Không dùng. REA so version bằng graph có bằng chứng. |
| GLM Flash | Trích câu | Không dùng. Skill không trích văn bản. |
| Claude | Chọn lệnh, đọc code tại dòng có bằng chứng, viết ghi chú và plan | Dùng. |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'node,rea,chrome?,ssh?,wp-cli?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. **Chọn nhánh theo nguồn.** Đọc bảng dưới và chạy nhánh hợp nguồn. Một tính năng có thể cần 2 nhánh, ví dụ plugin WP có cả PHP và JS.

   | Nguồn | Nhánh |
   |---|---|
   | Trang đang chạy (site mình hoặc site khác, trang công khai) | A. Trình duyệt |
   | File plugin hoặc theme WordPress | B. WordPress |
   | Theme hoặc app Shopify | C. Shopify |
   | File HAR, hoặc 2 version cần so | D. Capture và so version |

2. **Nhánh A — trình duyệt.** Lưu mọi kết quả vào thư mục tạm của phiên, không lưu vào repo.
   - Mở Chrome có cổng CDP: `eval "$(skills/web-reverse-engineer/scripts/rea_cdp.sh open <url>)"`. Lệnh này đặt biến `$EP` và `$TID`.
   - Tìm code xử lý tương tác: `rea inspect-web-event-listeners "$EP" "$TID" "<css selector>" --format json`. Kết quả cho file JS và dòng của handler.
   - Chụp trang, script và request: `rea inspect-web-page "$EP" "$TID" --observation-ms 3000 --include-script-sources --include-json-body-shapes --format json > cap.json`.
   - Với bundle lớn hoặc đã minify (React, Vue, webpack): xuất script bằng `rea export-web-scripts cap.json <thư mục chưa có>`. Sau đó chạy `rea analyze-javascript-application <thư mục>/files --format json > js.json`. Thêm `--fetch-source-maps` vào `rea analyze-web-bundle` khi trang công bố source map.
   - Với JS nhỏ của theme WP: đọc thẳng file tại dòng listener trả về. Lệnh `analyze-javascript-application` ra 6,6 MB cho 5 file nhỏ ở lượt thử 28/10/2026.
   - Đóng Chrome: `skills/web-reverse-engineer/scripts/rea_cdp.sh close`.
3. **Nhánh B — WordPress.**
   - Tìm plugin từ đường dẫn asset `/wp-content/plugins/<slug>/` trong `cap.json` hoặc HTML.
   - Lấy file: site có quyền server thì dùng `ssh <alias> wp plugin path <slug>` rồi tải về thư mục tạm. Plugin miễn phí thì tải `https://downloads.wordpress.org/plugin/<slug>.latest-stable.zip`.
   - Đọc PHP bằng grep theo hook: `grep -rnE "add_action|add_filter|add_shortcode|register_rest_route|wp_ajax_|register_post_type|register_block_type|update_option" <thư mục>`.
   - Đọc JS của plugin theo nhánh A, hoặc chạy `rea analyze-javascript-application <thư mục assets>`.
   - Ghi option, bảng DB, CPT và meta key mà plugin tạo. Plan dựng lại cần các dữ liệu này để giữ hoặc chuyển.
4. **Nhánh C — Shopify.**
   - Có quyền staff: kéo theme bằng `shopify theme pull --store <store>` rồi đọc Liquid và JS trực tiếp.
   - Không có quyền: chạy nhánh A trên storefront. Script của theme nằm ở `cdn.shopify.com/.../assets/`. Script của app thường nằm ở `/extensions/` hoặc domain của app. Liquid không xem được từ ngoài, chỉ suy ra từ HTML đã render và id `shopify-section-*`.
5. **Nhánh D — capture và so version.**
   - File HAR: `rea inspect-web-network-capture <file.har> --format json`.
   - Hai version JS: chạy `rea analyze-javascript-application` cho từng bản, rồi `rea compare-application-versions`. Hai version PHP: `diff -ru <cũ> <mới>`.
6. **Đọc kết quả.** Mỗi lệnh `rea` in dòng tiến độ JSONL trước. Lấy dòng cuối: `tail -n1 js.json | python3 -c "import json,sys; ..."`. Không đọc nguyên file kết quả vào context. Dùng `--filter-output <key>` hoặc `--token-limit <n>` khi cần xem nhanh. Không dùng `--detail summary` khi không có `--view`, vì lệnh sẽ báo lỗi.
7. **Viết ghi chú và plan** theo mục Output. Tách 3 mức: quan sát (có file:dòng hoặc evidence_id), suy luận, chưa rõ.
8. Tự phản biện theo mục dưới, rồi tự kiểm theo Gate → trả.

### Luật dùng code của bên khác

- Viết lại bằng code riêng. Chỉ chép đoạn code có licence cho phép, ví dụ GPL hoặc MIT. Giữ header licence và ghi nguồn trong code.
- Không chép CSS, ảnh, font hoặc JS của theme và plugin thương mại có licence riêng, ví dụ ThemeForest bản split licence.
- Không bẻ kiểm tra licence, không dùng bản nulled, không gọi API trả phí bằng key của bên khác.
- Với site của bên khác: chỉ soi trang công khai bằng thao tác người dùng thường. Không đăng nhập tài khoản của họ, không quét hàng loạt, không gửi form thật.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình người duyệt.

Bản tốt nhất phải có:
- [ ] Mỗi kết luận về cơ chế có file:dòng, URL request hoặc evidence_id. Nguồn lỗi: lượt thử trên site WordPress mẫu 28/10/2026, listener trả đúng file JS của theme và dòng 64, còn đọc HTML chỉ đoán được tên file.
- [ ] Phần PHP hoặc Liquid được đọc trực tiếp, không suy từ JS. Nguồn lỗi: REA 6.8.0 không có bộ phân tích PHP, Liquid (README, 28/10/2026).
- [ ] Ghi chú tách quan sát, suy luận, chưa rõ. Nguồn lỗi: REA trả riêng `observations`, `inferences`, `unknowns`. Gộp lại làm mất mức chắc (lượt thử 28/10/2026).
- [ ] Plan dựng lại liệt kê dữ liệu cần giữ: option, meta key, CPT, bảng DB, URL. Nguồn lỗi: thay Permalink Manager phải dựng bản đồ URL riêng (`wp-paid-plugin-exit`, 10/2026).
- [ ] Plan ghi licence của nguồn và phần nào viết lại. Nguồn lỗi: luật tự code thay plugin trả phí không licence, 10/2026.
- [ ] Kết quả `rea` lớn nằm ngoài repo; ghi chú chỉ trích phần cần. Nguồn lỗi: kết quả 6,6 MB cho 5 file JS, 28/10/2026.

## Output

Thư mục đợt do người giao việc chỉ định. Mặc định: `04-structure-ux-cro/reverse/<YYYY-MM-DD>-<tính-năng>/` của instance.

| File | Nội dung |
|---|---|
| `ghi-chu.md` | Mục tiêu · nguồn đã soi (URL, file, version) · bảng hành vi → bằng chứng → mức chắc · phụ thuộc (thư viện, API, licence) · giới hạn |
| `plan-dung-lai.md` | File sẽ tạo hoặc sửa · dữ liệu cần giữ · bước làm trên staging · cách kiểm |

Không đưa file JSON kết quả của `rea` vào thư mục đợt. Trích đoạn cần dùng vào `ghi-chu.md`.

## Gate

- [ ] Câu hỏi "tính năng chạy thế nào" có câu trả lời kèm bằng chứng, hoặc ghi rõ phần chưa rõ.
- [ ] Không có đoạn code chép từ nguồn mà licence không cho phép.
- [ ] Chrome CDP đã đóng.
- [ ] Plan dựng lại đi qua staging theo `wp-staging-deploy` trước khi lên production.

## Anti-patterns

- Chạy `analyze-javascript-application` cho mọi trang → chỉ chạy cho bundle lớn hoặc minify.
- Đăng ký REA làm MCP global → dùng CLI theo skill này. MCP của REA có rất nhiều tool và làm tăng context mỗi phiên.
- Cài Hopper, Ghidra hoặc JADX cho việc web → không cần. Các công cụ đó chỉ dành cho binary và app Android.

## Changelog

- v1.0 (2026-10-28): tạo mới. Thử trên trang chủ site WordPress mẫu: `inspect-web-page`, `inspect-web-event-listeners`, `export-web-scripts`, `analyze-javascript-application`, `analyze-web-bundle` với REA 6.8.0, Node 24.22.1.
