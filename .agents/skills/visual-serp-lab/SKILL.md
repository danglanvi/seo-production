---
name: visual-serp-lab
description: "Đo ảnh trong bài (alt có tả đúng ảnh, ảnh có khớp mục chứa nó) và màn đầu của trang so với trang được AI trích cùng pool, bằng code + EmbeddingGemma ảnh + Jev ảnh có hiệu chuẩn. Dùng khi audit ảnh, alt hàng loạt hoặc so màn đầu với trang được trích."
metadata:
  version: "1.0"
---

# visual-serp-lab — ảnh trong bài và màn đầu của trang

Skill này đo hai việc bằng model có hiệu chuẩn theo site:

1. Ảnh trong main content: alt có tả đúng ảnh không, và ảnh có khớp mục chứa nó không.
2. Màn đầu desktop của trang: trang có những đặc điểm gì, so với trang được AI trích trong cùng pool truy vấn.

Skill `visual-semantic-seo` thiết kế và audit layout theo framework. Skill này cấp số đo hàng loạt cho việc đó. Skill này không thay framework.

Gốc đường dẫn là root repo. Script: `skills/visual-serp-lab/scripts/visual.py`. Rubric Jev: `skills/visual-serp-lab/tasks/image-fit.json` và `first-screen.json`. Jev ở `tools/ai-assist/jev.py`; ở workspace gốc, Jev nằm ở `SEO Production/tools/ai-assist/`.

## Khi nào dùng

- Audit ảnh và alt của một site: tìm alt thiếu, alt dạng tên file, một alt cho nhiều ảnh khác nhau, alt không tả ảnh.
- Tìm ảnh không khớp mục chứa nó, ví dụ ảnh stock trang trí trong mục hướng dẫn.
- So màn đầu của trang mình với trang được AI Overview hoặc ChatGPT trích cùng truy vấn.
- Không dùng để thiết kế wireframe hay chọn component. Việc đó thuộc `visual-semantic-seo`.
- Không dùng để viết alt mới. Claude viết alt sau khi xem ảnh; Jev và GLM không viết nội dung.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| HTML của các trang (`<store>/html`) | `site-vector-index` (`extract.py`) | dựng trước |
| `pools.jsonl` (id, text, urls có label được trích) | `content-quality-lab`, từ citations của `geo-answer-lab` + top 10 | bỏ nhánh layout |
| `OPENROUTER_JEV_API_KEY` | `.agent-secrets/.env` | chỉ chạy phần code + Gemma; mọi ảnh ghi "chưa đo" |
| Venv EmbeddingGemma 2 | `~/.venvs/embeddinggemma` | bỏ điểm gộp alt-score; alt chỉ có cờ của code |
| Google Chrome | `/Applications/Google Chrome.app` | bỏ lệnh `shoot` |
| Cổng `alt-score`, `image-fit`, `first-screen` | registry `00-client-context/model-calibration.json` | dùng defaults nếu có và ghi "bản nháp"; thiếu cổng thì lệnh dừng |

Các lệnh `images`, `fetch`, `jev-in`, `pairs`, `media`, `layout`, `shoot` chạy bằng `python3 -E` (cần beautifulsoup4 và Pillow). Lệnh `embed` chạy bằng `<venv>/bin/python -I`.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,bs4,pillow,numpy,gemma,jev,chrome?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Nhánh media

1. Lấy ảnh: `python3 -E skills/visual-serp-lab/scripts/visual.py images --html-dir <store>/html --out <W>/images.jsonl`.
   - Code gắn cờ `missing_alt`, `fileish_alt`, `alt_reused`. Code bỏ ảnh trong header, ảnh SVG, data URI và ảnh rộng dưới 80 px.
   - Lệnh ghi thêm `<W>/sections.jsonl`, chứa chữ của từng mục.
2. Tải mẫu: `visual.py fetch --images <W>/images.jsonl --cache <store>/img --out <W>/sample.jsonl`. Mặc định lấy 2 ảnh có alt mỗi trang. Thêm `--all` để tải mọi ảnh.
3. Embed: `<venv>/bin/python -I skills/visual-serp-lab/scripts/visual.py embed --sample <W>/sample.jsonl --sections <W>/sections.jsonl --out <W>/media.jsonl`. Lệnh dừng khi một đường dẫn ảnh không tồn tại.
4. Chạy Jev: `visual.py jev-in --media <W>/media.jsonl --out <W>/jev_media_in.jsonl`, rồi `python3 -I tools/ai-assist/jev.py --task skills/visual-serp-lab/tasks/image-fit.json --in <W>/jev_media_in.jsonl --out <W>/jev_media_out.jsonl --budget 0.3`. 576 ảnh tốn khoảng 0,04 USD.
5. Quyết định: `visual.py media --images <W>/images.jsonl --media <W>/media.jsonl --jev-out <W>/jev_media_out.jsonl --registry 00-client-context/model-calibration.json --site <domain> --out-dir <W>`.

### Nhánh layout

1. Chụp màn đầu: `visual.py shoot --urls <W>/urls.txt --out-dir <shots>`. `urls.txt` gồm mọi URL trong `pools.jsonl`.
2. Chạy Jev: `visual.py jev-in --shots <shots>/shots.jsonl --pools pools.jsonl --out <W>/jev_layout_in.jsonl`, rồi `jev.py --task skills/visual-serp-lab/tasks/first-screen.json --in <W>/jev_layout_in.jsonl --out <W>/jev_layout_out.jsonl --budget 0.5`. Mỗi cặp pool × URL tốn khoảng 0,00017 USD.
3. Báo cáo: `visual.py layout --jev-out <W>/jev_layout_out.jsonl --pools pools.jsonl --registry 00-client-context/model-calibration.json --site <domain> --own-domain <domain> --out-dir <W>`.
4. Kiểm tín hiệu của từng đặc điểm: `calibrate.py auc --data <W>/auc_rows.jsonl --metric <đặc điểm> --label cited --group pool`. Đặc điểm có CI chứa 0,5 không vào báo cáo khách.

### Hiệu chuẩn (site mới hoặc rubric đổi version)

Dùng skill `model-calibration`. Claude gán gold bằng mắt trước khi xem điểm model.

- Media: gán ≥ 60 ảnh gồm dev lấy theo dải `alt_cos` và holdout ngẫu nhiên. Gán `alt_matches` và `fits_section` theo định nghĩa ở mục dưới.
  - `calibrate.py jev --question fits_section --positive yes` và `--question alt_matches --positive no`.
  - `visual.py pairs --media <W>/media.jsonl --jev-out <W>/jev_media_out.jsonl --gold gold_alt.jsonl --out <W>/calibration/alt_score_pairs.jsonl`, rồi `calibrate.py cosine --pairs ... --grid=0.8:2.8:0.02 --rubric alt-score --version <version image-fit>+w2 --write`.
- Layout: gán ≥ 40 cặp ngẫu nhiên. Đặc điểm có dưới 10 ca dương thì gán thêm mọi ca Jev chấm có, cộng một mẫu ca chấm không. Ở vòng thêm, Claude gán đủ 8 câu mà không xem điểm. Chạy `calibrate.py jev --question <câu> --positive yes` cho từng câu.

Claude đọc báo cáo, xem ảnh của mọi dòng trước khi đề xuất:

- Alt thiếu hoặc dạng tên file: đề xuất alt mới sau khi xem ảnh, qua `wp-content-review-apply`.
- Alt lệch ảnh: xem ảnh rồi viết alt tả đúng nội dung. Không nhồi từ khóa.
- Một alt cho nhiều ảnh (ví dụ logo khách hàng cùng alt "img"): sửa ở template hoặc khối dùng chung một lần.
- Ảnh có thể không khớp mục: xem ảnh và mục. Nếu ảnh là stock trang trí trong mục hướng dẫn, đề xuất ảnh chụp màn hình hoặc sơ đồ thật. Bỏ qua ảnh thẻ bài viết trên trang chuyên mục và trang tác giả.
- Màn đầu: so trang mình với trang được trích trong cùng pool, chỉ với đặc điểm đã có AUC chứng minh.

## Định nghĩa gold

Ảnh:

- `alt_matches` yes khi người không thấy ảnh đọc alt là biết ảnh có gì. Alt chỉ lặp từ khóa, lặp tiêu đề trang, hoặc nêu thứ ảnh không có thì là no.
- `fits_section` yes khi ảnh cho thấy thứ thuộc chủ đề của mục: ảnh chụp màn hình, biểu đồ, sơ đồ, ví dụ, ảnh của chính thứ mục giải thích. Ảnh stock chung, ảnh trang trí, ảnh chủ đề khác là no. Ảnh trên trang chuyên mục: bỏ câu này.

Màn đầu (desktop 1366 × 900, trước khi cuộn):

- `answer_visible` yes khi có đoạn hoặc danh sách trả lời thẳng truy vấn. Trả lời đúng một vế của truy vấn hai vế cũng tính. Tiêu đề có con số mà không có đoạn trả lời là no. Ca không chắc thì để trống, không ép nhãn.
- `price`: giá của dịch vụ hay sản phẩm trang nói tới, kể cả giá trong tiêu đề. Giá trong quảng cáo không tính.
- `form`: ô nhập tên, điện thoại hoặc email. Ô tìm kiếm và nút mở form không tính.
- `trust`: bằng chứng từ bên thứ ba như sao đánh giá, số đánh giá, testimonial, logo báo chí, chứng nhận, giải thưởng. Số công ty tự nêu, lượt xem, lượt thích không tính.
- `byline`: tên tác giả, hoặc ngày đăng hay ngày cập nhật, kể cả nhãn "Cập nhật 01/2026".
- `media`: video, ảnh thu nhỏ của video, biểu đồ, infographic, sơ đồ, ảnh chụp dữ liệu, báo cáo hay phần mềm. Banner, ảnh đại diện mang tiêu đề, ảnh stock, chân dung, minh họa giao diện giả lập và bảng HTML không tính.
- `toc`: danh sách các mục của trang hiện trên màn. Nút mục lục đang thu gọn là no.
- `covered`: popup, hộp xin quyền thông báo, banner cookie, cửa sổ chat hay quảng cáo đè lên trang. Nút liên hệ nổi ở mép và thanh cố định ở đầu hay cuối màn không tính.
- Trang trả 403 hoặc màn trắng: gán no cho mọi câu và ghi chú. Khi so sánh, loại trang đó ra hoặc chụp lại.

## Đọc số cho đúng

Pilot trên site mẫu ngành agency SEO (19/10/2026).

Media: 5.602 ảnh trong main content của 337 trang, tải mẫu 576 ảnh. Gold gồm 80 ảnh gán mù: dev 60 lấy theo dải `alt_cos`, holdout 20 ngẫu nhiên.

| Kiểm | Kết quả |
|---|---|
| Cos ảnh–alt của Gemma → alt tả đúng ảnh | AUC 0,85 |
| Jev `alt_matches` | AUC 0,92 |
| Điểm gộp p + 2 × cos, loại khi dưới 1,64 | gắn cờ 44/80, đúng 42 (95%); bắt 42/46 alt xấu (91%) |
| Jev `fits_section`, ngưỡng 0,7 | precision 98,3%, phủ 79% |
| Code "alt dạng tên file" | đúng 20/20 |
| Cos ảnh–mục của Gemma: mục của ảnh so với mục khác cùng trang | AUC 0,61, không dùng làm cổng |

Layout: 228 cặp pool × URL của 30 truy vấn, 159 ảnh màn đầu. Gold gồm 85 cặp: 45 ngẫu nhiên và 40 phân tầng theo điểm Jev.

| Kiểm | Kết quả |
|---|---|
| Jev 7 câu trừ `media`, qua cổng của từng câu | đúng 95–100%, phủ 94–100% |
| `media` ở cổng 0,85 | đúng 97%, phủ 48% |
| `media` nếu lấy thẳng p ≥ 0,5 | đúng 10/28: Jev gọi banner là infographic |
| `answer_visible` → được trích, AUC trong pool | 0,644 [0,574; 0,719], 27 pool |
| 7 đặc điểm còn lại và `centerpiece_top` | CI chứa 0,5: chưa chứng minh |

- Gold media lấy mẫu theo dải cos, nên có nhiều alt xấu hơn thực tế. Gold layout vòng 2 lấy theo điểm Jev. Hai mẫu này đo độ đúng của model, không đo tỷ lệ của site hay của SERP.
- Cos ảnh–chữ dồn trong dải hẹp và khác thang cos chữ–chữ. Mỗi site cần ngưỡng riêng.
- Có 2/159 trang trả 403 cho Chrome headless. Những trang này cho màn trắng.
- Đặc điểm đi cùng trang được trích không chứng minh rằng đặc điểm đó làm trang được trích.

## Năng lực model đã xét

| Năng lực | Việc | Quyết định |
|---|---|---|
| Code | alt thiếu, alt dạng tên file, alt dùng lại, bỏ ảnh header, SVG, data URI; đệm ảnh nhỏ cho Jev | dùng |
| EmbeddingGemma ảnh (không prompt) + alt (`SearchQuery`) | alt tả đúng ảnh | dùng trong điểm gộp alt-score; chọn không prompt sau khi so với prompt `Document` trên mẫu |
| EmbeddingGemma ảnh + mục (`Document`) | ảnh khớp mục | bỏ làm cổng: AUC 0,61. Giữ `sec_cos`, `sec_margin` để tham khảo |
| Jev ảnh `alt_matches` | alt tả đúng ảnh | dùng trong điểm gộp; một mình cổng 0,85 chỉ phủ 42% |
| Jev ảnh `fits_section` | ảnh khớp mục | dùng, ngưỡng theo site |
| Jev ảnh màn đầu, 8 câu noul | đặc điểm màn đầu | dùng qua cổng của từng câu |
| Jev box `centerpiece`, `primary_cta` | vị trí khối chính và nút chính | chỉ mô tả: chưa có gold box, AUC `centerpiece_top` 0,52 |
| Gemma ảnh màn đầu + truy vấn | màn đầu trả lời truy vấn | chưa thử: `answer_visible` của Jev đã có tín hiệu; để v1.1 |
| Màn đầu mobile | đặc điểm màn đầu mobile | chưa làm: Chrome ép tối thiểu 500 px, cần iframe wrapper và gold riêng |
| Video | nội dung video | bỏ: video trên site mẫu là YouTube embed, Jev 1.14 nhận ảnh; ảnh thu nhỏ đi theo nhánh ảnh |
| GLM Flash | — | không cần: skill không trích câu |

## Output

- `<W>` = `03-audits/content/<CLIENT>_visual-serp-lab_<YYYY-MM-DD>/`.
  - Media: `images.jsonl`, `sections.jsonl`, `sample.jsonl`, `media.jsonl`, `jev_media_in.jsonl`, `jev_media_out.jsonl`, `media_decisions.jsonl`, `media_report.md`.
  - Layout: `urls.txt`, `jev_layout_in.jsonl`, `jev_layout_out.jsonl`, `auc_rows.jsonl`, `layout_report.md`.
- Cache ảnh và ảnh màn đầu là input của model: `03-audits/_vector-index/<domain>/img/` và `03-audits/_vector-index/serp/first-screen/<YYYY-MM-DD>/`. Thư mục này nằm trong `.gitignore`. Ảnh dùng làm bằng chứng trong deliverable thì chép sang `02-raw/screenshots/` theo `_REFERENCE/screenshots-protocol.md`.
- Gold và kết quả hiệu chuẩn: `<W>/calibration/`. Entry registry: `image-fit`, `alt-score`, `first-screen`, `first-screen-cited`.

## Gate

- [ ] Jev chỉ nhận ảnh và ảnh chụp của trang công khai. Không chụp trang cần đăng nhập. Không gửi ảnh nội bộ của khách.
- [ ] Cổng lấy từ registry của site, hoặc báo cáo ghi rõ "bản nháp, cổng defaults".
- [ ] Báo cáo khách chỉ nêu đặc điểm màn đầu có AUC trong pool với CI trên 0,5.
- [ ] Claude đã xem ảnh của mọi dòng được đề xuất sửa. Alt mới do Claude viết.
- [ ] Báo cáo khách ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".

## Anti-patterns

- Chạy `embed` với đường dẫn ảnh tương đối từ thư mục khác. Model sẽ encode chuỗi đường dẫn như chữ, và cos sụt khỏi thang của ảnh. Ở pilot, lỗi này làm cos lệch tới 0,32 và gắn cờ 286 ảnh thay vì 150. Bản 1.0 dừng khi thiếu file.
- Dùng cổng ảnh–alt của site khác. Thang cos ảnh–chữ khác nhau theo site.
- Đếm `media` bằng nhãn thô p ≥ 0,5. Ở mức đó, 18/28 ca Jev chấm có không phải media, phần lớn là banner.
- Kết luận "trang được trích vì có mục lục hay byline". AUC trong pool chưa chứng minh điều đó.
- Sửa alt bằng cách thêm từ khóa. Rubric coi alt chỉ lặp từ khóa là alt không tả ảnh.
- Sửa từng ảnh trong khối dùng chung (logo khách hàng, ảnh tác giả). Sửa một lần ở template.

## Changelog

- v1.0 (2026-10-19): tạo mới từ pilot site mẫu: 5.602 ảnh, gold 80 ảnh; 228 màn đầu của 30 truy vấn, gold 85 cặp. Rubric `image-fit` và `first-screen` 2026-10-19.1. Lệnh `embed` dừng khi thiếu file ảnh. Test offline `tests/test_visual.py`.
