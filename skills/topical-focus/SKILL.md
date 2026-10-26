---
name: topical-focus
description: "Đo độ tập trung chủ đề của site bằng EmbeddingGemma local, gán bài dự kiến vào cụm trước khi viết và tìm khoảng trống chủ đề so với đối thủ từ sitemap công khai. Dùng khi rà topical map, sàng lọc kế hoạch content, chọn trang cho content-refresh hoặc chuẩn bị pitch BD."
metadata:
  version: "1.1.1"
---

# topical-focus — site đang nói về chủ đề gì, và bài mới rơi vào đâu

Tài liệu rò rỉ của Google có các thuộc tính `siteFocusScore`, `siteRadius` và `siteEmbedding`. Công thức thật chưa công bố. Skill này mô phỏng ý tưởng đó bằng vector cấp trang. Skill tính tâm site, khoảng cách từng trang tới tâm, các cụm chủ đề và trang lệch tâm. Skill cũng gán bài dự kiến vào cụm trước khi viết.

Gốc đường dẫn là root repo. Script: `skills/topical-focus/scripts/topical.py`. Script đọc store của `site-vector-index` và chạy bằng venv embedding (numpy, scikit-learn). Lệnh `plan`, `selftest` và `gap` cần thêm sentence-transformers. `scripts/competitor_titles.py` (Python stdlib) lấy title và H1 của trang đối thủ từ sitemap công khai.

## Khi nào dùng

- Rà topical map hoặc cơ cấu chủ đề của site: cụm nào chiếm bao nhiêu trang, cụm nào xa tâm.
- Sàng lọc kế hoạch content: bài dự kiến rơi vào cụm nào, gần trang có sẵn nào.
- Chọn trang lệch tâm để `content-refresh` xét CONSOLIDATE hoặc PRUNE.
- So mốc quý trên cùng site, cùng scope.
- Tìm khoảng trống chủ đề so với đối thủ: chủ đề đối thủ có trang mà site chưa có. Dùng cho kế hoạch content và cho pitch BD.
- Không dùng để dự báo traffic hay thứ hạng. Pilot không chứng minh được khoảng cách tới tâm dự báo hiển thị khi đã khử độ dài bài (mục "Đọc số cho đúng").

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Store có vector cấp `page`, prompt `Document` | `site-vector-index` (`svi.py build --levels page,passage`) | dựng store trước |
| `pages.jsonl` (lang, robots, canonical, H2) | `extract.py` của `site-vector-index` | chạy không có scope; `selftest` không chạy được |
| Hiển thị GSC theo **chiều page**, 90 ngày | `tools/gsc/gsc.sh query <property> 90 page` → jsonl `{"url", "impressions", "clicks"}` | báo cáo không có cột hiển thị, không kiểm proxy |
| URL trang lõi (trang chủ, trang dịch vụ) | `00-client-context/` | bỏ `--core` |
| Regex trang bằng chứng (case study, tác giả, giới thiệu) | cấu trúc URL của site | hỏi người vận hành |
| Sitemap công khai của 2–3 đối thủ (chỉ việc khoảng trống) | Ahrefs organic competitors, SERP của query chính, hoặc người vận hành | hỏi người vận hành |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| EmbeddingGemma 2 (local) | Vector trang, tâm site, cụm; title + H1 của site và đối thủ cho việc khoảng trống | Dùng. Prompt `Document`, 768 chiều (bảng "Năng lực model đã xét") |
| Code tất định | Scope trang, chọn số cụm, gom trang khoảng trống, ngưỡng theo registry | Dùng |
| Jev | Đặt tên cụm, lọc cụm khoảng trống ngoài định vị | Không dùng. Đặt tên là viết, Claude làm. Lọc theo định vị cần biết chiến lược của brand |
| GLM Flash | Trích câu | Không dùng. Skill không có việc trích câu |
| Claude | Đặt tên cụm, đọc trang lệch tâm, đọc cụm khoảng trống và mục `review`, quyết bài nên viết | Dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,gemma,curl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. Dựng bản đồ:
   `<venv>/bin/python -I skills/topical-focus/scripts/topical.py map --store <store> --pages pages.jsonl --lang vi --exclude '/en/' --core core.txt --metrics gsc_page.jsonl --proof '/case-study/|/tac-gia/' --out <W>`
   - Scope chỉ giữ trang ≥ 300 chữ, đúng ngôn ngữ, không noindex, có canonical trỏ về chính trang đó.
   - Script tự chọn số cụm bằng silhouette, từ 3 tới 12. Mỗi cụm phải có ít nhất max(5, 2% số trang).
   - Trang lệch tâm là trang nằm dưới phân vị 10 của cosine tới tâm (`--outlier-pct`). Ngưỡng theo hạng, vì cosine không so được giữa các site.
2. Claude đọc `near_titles` trong `clusters.json` và đặt tên từng cụm vào `names.json`, ví dụ `{"0": "Website, WordPress"}`. Chạy lại bước 1 với `--names names.json`. KMeans cố định `random_state`, nên cùng store và cùng scope cho cùng số cụm.
3. Tự hiệu chuẩn cổng gán cụm: `topical.py selftest --map <W> --pages pages.jsonl`. Script lấy tiêu đề + H2 của trang có sẵn làm bài dự kiến, rồi ghi cổng `margin` vào `<W>/plan_gate.json`.
4. Sàng lọc kế hoạch: `topical.py plan --map <W> --in plan.jsonl --out <W>/plan_out.jsonl`. Dòng input có dạng `{"id", "title", "outline": [H2...]}`.
   - Bài có `review: true` (margin dưới cổng) thì Claude đọc và tự gán cụm.
   - `nearest_pages` chỉ là gợi ý trùng chủ đề. Kiểm cannibalization bằng `retrieval-lab route`.
   - Bài rơi vào cụm xa tâm: người vận hành quyết có mở rộng nhánh đó không.
5. Kiểm proxy trên site trước khi đưa số vào báo cáo khách. Chạy `model-calibration` chế độ proxy trên `<W>/proxy_rows.jsonl`:
   - `--metric cos_site --outcome log_impr` (gộp mọi trang).
   - Thêm `--control log_words` để khử độ dài bài.
   - Thêm `--group cluster` để kiểm trong từng cụm.
   Ghi cả 3 entry vào `00-client-context/model-calibration.json` (rubric `topical-focus`).
6. Claude đọc `report.md`:
   - Trang nội dung lệch tâm, ít hiển thị: chuyển sang `content-refresh`.
   - Trang nội dung lệch tâm, nhiều hiển thị: giữ trang và ghi vào kế hoạch.
   - Cụm xa tâm: đối chiếu topical map (`topical-map-creation`) và định vị của brand.
   - Trang bằng chứng lệch tâm: không xét bỏ, vì trang này phục vụ EEAT và consensus (luật GE-26).

### Khoảng trống chủ đề với đối thủ

1. Lấy title và H1 của đối thủ, mỗi đối thủ một lệnh. Chỉ GET trang công khai:
   `python3 -I skills/topical-focus/scripts/competitor_titles.py --sitemap https://<đối thủ>/sitemap_index.xml --site <đối thủ> --include '(post|page|blog)-sitemap' --max 600 --out <W>/gap/titles_<đối thủ>.jsonl`
   - `--include` chọn sitemap con. Bỏ taxonomy, tag, tuyển dụng. Mở `sitemap_index.xml` để xem tên sitemap con trước khi chạy.
   - Sitemap lớn hơn `--max` thì script lấy mẫu có seed. Báo cáo ghi số URL đã lấy trên tổng số URL.
   - Nếu site trả 429 hoặc 503, script nghỉ rồi thử lại. Nếu vẫn lỗi, chạy lại cùng lệnh với `--workers 1`.
2. Trang của site: `pages.jsonl` của `extract.py` (đã có title, H1, lang, robots).
3. Site mới, ngành mới, hoặc registry chưa có ngưỡng `topical-gap`: hiệu chuẩn trước.
   - Chạy `topical.py gold-sheet --site-pages <pages.jsonl> --competitor <titles_*.jsonl> --n 60 --out <W>/gap/calibration/sheet_dev.jsonl`. Mỗi dòng có 8 trang của site gần nhất theo trùng chữ, không có cosine.
   - Gán `covered` 0/1 trước khi xem cosine. 1 = site đã có trang cùng thực thể và cùng ý định. Ghi sha256 và giờ vào `gold_log.md`.
   - Chạy `gap` không có ngưỡng, rồi chạy skill `model-calibration` chế độ `cosine` (nhãn `covered`) để lấy ngưỡng `reject_below`.
   - Gán holdout mới bằng `gold-sheet --skip <id dev> --seed <khác>` trước khi kiểm ngưỡng. Ghi registry `00-client-context/model-calibration.json` (rubric `topical-gap`).
4. Chạy: `<venv>/bin/python -I skills/topical-focus/scripts/topical.py gap --site-pages <pages.jsonl> --competitor <W>/gap/titles_a.jsonl --competitor <W>/gap/titles_b.jsonl --gap <ngưỡng> --out <W>/gap`
   - Cosine dưới `--gap`: script gắn nhãn khoảng trống. Nhãn này là ứng viên Claude đọc, không phải kết luận: ngưỡng 0,86 đúng 94% (gộp dev và holdout), dưới cổng 95%. Còn lại ghi `review`. Chỉ đặt `--cover` khi registry có ngưỡng "đã có" đạt cổng.
   - Script bỏ đoạn đuôi brand lặp ở title, bỏ năm và tháng, rồi embed "title + H1".
   - Script gom trang khoảng trống thành cụm (`--group-cos` 0,83). Cụm nhiều đối thủ xếp trước. Cụm trang thương hiệu, case study của đối thủ xếp cuối.
5. Claude đọc `gap_report.md`:
   - Bỏ cụm ngoài định vị hoặc ngoài mảng kinh doanh: tin tuyển dụng, mẹo app, sự kiện, chủ đề của entity khác.
   - Đọc mục `review` của trang dịch vụ và trang địa phương. Title của các trang này giống nhau theo template, nên cosine cao dù site chưa có trang đó (mục "Đọc số cho đúng").
   - Bài đề xuất từ cụm: gán vào bản đồ bằng `plan`, kiểm SERP trước khi viết. Pitch BD chỉ nêu cụm Claude đã đọc, kèm ngày lấy sitemap.

## Đọc số cho đúng

Pilot site mẫu ngành agency SEO (19/10/2026, 308 trang tiếng Việt, GSC 90 ngày chiều page):

| Kiểm | Kết quả |
|---|---|
| `cos_site` → log hiển thị, gộp mọi trang | rho 0,22 [0,10; 0,33] — có tín hiệu |
| Như trên, khử log số chữ | rho 0,11 [−0,01; 0,21] — chưa chứng minh |
| Trong từng cụm (5 cụm) | rho 0,09 [−0,11; 0,34] — chưa chứng minh |
| `cos_core` (gần trang dịch vụ) → hiển thị | rho −0,29 [−0,41; −0,18] — ngược chiều |
| Gán cụm từ tiêu đề + H2 | khớp 93,1%; margin ≥ 0,005 khớp 96,8% (phủ 92%) |

- Tín hiệu gộp phần lớn đến từ độ dài bài: trang dài gần tâm hơn (rho 0,38) và có nhiều hiển thị hơn.
- Cụm xa tâm nhất (Facebook) có trung vị hiển thị cao nhất. Cụm xa tâm không có nghĩa là trang kém.
- `cos_core` đo độ gần trang dịch vụ. Trang thông tin rộng kéo hiển thị nên chỉ số này ngược chiều với hiển thị. Không dùng `cos_core` làm proxy traffic.
- Dùng GSC chiều page. Bản query × page thiếu query ẩn danh (pilot: thiếu 17% hiển thị) và làm rho khử độ dài lên 0,15 sai lệch.
- Báo cáo khách chỉ dùng cơ cấu cụm, danh sách trang lệch tâm và kết quả gán bài. Kèm câu: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".

Khoảng trống với đối thủ, pilot site mẫu 19/10/2026: 333 trang của site, 1.127 trang của 2 đối thủ (đối thủ A 600/600 URL sitemap, đối thủ B mẫu 600/2.007). Gold gán mù 110 trang.

| Kiểm | Kết quả |
|---|---|
| AUC của cosine tới trang gần nhất, prompt `Document` | dev 0,896; holdout 0,905 |
| Cosine < 0,86 là khoảng trống (ngưỡng chọn trên dev) | dev 39/41; holdout 28/30; gộp 67/71 (94%), phủ 65% |
| Ngưỡng "đã có" | chưa đạt cổng: 1 trang chưa có đạt cosine 0,922. Không tự gắn "đã có" |

- Cosine của title ngắn dồn trong dải 0,80–0,95. Chỉ so trên cùng site, cùng prompt.
- Trang dịch vụ và trang địa phương có title theo template ("Dịch vụ SEO <thành phố>"). Pilot: "Dịch vụ SEO Đà Nẵng" có cosine 0,890 tới trang công ty SEO, và "Dịch vụ GEO" có cosine 0,921 tới trang dịch vụ SEO Hà Nội. Cả 2 trang đều là khoảng trống thật, nhưng nằm ở mục `review`.
- Một trang đối thủ không có trang tương ứng chưa chứng minh chủ đề đó có traffic. Kiểm volume và SERP trước khi đề xuất.

## Năng lực model đã xét

Số đo: rho giữa `cos_site` và log hiển thị (GSC chiều page), 308 trang, CI bootstrap 1.000 lần.

| Năng lực | Việc | Quyết định |
|---|---|---|
| EmbeddingGemma prompt `Document`, 768 chiều | vector trang, tâm, cụm | dùng: rho 0,23 [0,10; 0,33], cao nhất trong 4 prompt |
| Prompt `Classification` | như trên | bỏ: rho 0,15; khử độ dài còn 0,03 |
| Prompt `Clustering`, `SentenceSimilarity` | như trên | bỏ: rho 0,00 và −0,02, CI chứa 0 |
| MRL 256, 128 chiều | tâm, cụm | bỏ cho đo tập trung: rho 0,17 và 0,20, thấp hơn 768. 128 chiều chỉ dùng lọc thô trong `svi.py query` |
| Trung bình passage, trung bình section | vector trang | bỏ: rho 0,04–0,06 ở bản đo đầu |
| Ảnh, video của Gemma | — | không áp: skill đo chữ; ảnh ở `visual-serp-lab` |
| Jev | đặt tên cụm, gán bài | không dùng: đặt tên là viết, Claude làm. Gán bài bằng cosine đã đạt 96,8% trên cổng |
| Gemma, title + H1, cho khoảng trống | trang đối thủ có trang tương ứng trên site không | dùng prompt `Document`: AUC dev 0,896, holdout 0,905. `SentenceSimilarity` dev 0,839, holdout 0,914; `Clustering` 0,783 và 0,836. Chọn theo dev |
| Gemma, toàn văn trang đối thủ | như trên | không áp: phải tải và tách toàn văn hàng nghìn trang. Title + H1 đã đạt AUC 0,9 |

## Output

- `<W>` = `03-audits/content/<CLIENT>_topical-focus_<YYYY-MM-DD>/`: `pages.jsonl`, `clusters.json`, `summary.json`, `centroids.npz`, `proxy_rows.jsonl`, `report.md`, `plan_gate.json`, `names.json`.
- Khoảng trống: `<W>/gap/`: `titles_<đối thủ>.jsonl`, `gap_pages.jsonl`, `gap_groups.json`, `gap_report.md`, `calibration/` (gold, `gold_log.md`, kết quả `calibrate.py`).
- Kết quả gán bài: `<W>/plan_out.jsonl`, đính vào kế hoạch ở `05-content-plan/`.
- Entry proxy trong `00-client-context/model-calibration.json`.

## Gate

- [ ] Store dùng prompt `Document`, cùng model với lần đo trước. Mốc so sánh dùng cùng scope và cùng số chiều.
- [ ] Mọi cụm có tên do Claude đặt từ tiêu đề thật trước khi gửi báo cáo.
- [ ] Hiển thị lấy từ GSC chiều page, có ghi khoảng ngày.
- [ ] Không có trang bằng chứng nào trong danh sách đề xuất gộp hay bỏ.
- [ ] Báo cáo khách không nêu khoảng cách tới tâm như yếu tố xếp hạng, trừ khi registry của site ghi "dùng được" ở entry đã khử độ dài.
- [ ] Khoảng trống: ngưỡng lấy từ registry, có gold mù dev và holdout. Báo cáo ghi ngày lấy sitemap và số URL đã lấy trên tổng số.
- [ ] Khoảng trống: không gửi cụm trang thương hiệu, case study của đối thủ như chủ đề nên viết.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Mỗi cụm có tên Claude đặt từ tiêu đề thật. Nguồn lỗi: KMeans chỉ trả số cụm, tên tự sinh không đọc được.
- [ ] Trang lệch tâm tách trang nội dung và trang bằng chứng. Nguồn lỗi: pilot site mẫu, case study nằm trong nhóm xa tâm nhất.
- [ ] Không kết luận traffic từ khoảng cách tới tâm. Nguồn lỗi: pilot, rho khử độ dài 0,11, CI chứa 0.
- [ ] Danh sách khoảng trống đã bỏ cụm ngoài định vị (mẹo app, tuyển dụng, tin của đối thủ). Nguồn lỗi: pilot 19/10, 41/426 cụm là trang thương hiệu, case study của đối thủ.
- [ ] Trang dịch vụ và trang địa phương trong mục `review` đã được đọc. Nguồn lỗi: pilot 19/10, "Dịch vụ GEO" và "Dịch vụ SEO Đà Nẵng" là khoảng trống thật nhưng có cosine 0,92 và 0,89.
- [ ] Bài đề xuất từ khoảng trống có kiểm SERP và volume. Nguồn lỗi: trang đối thủ có không chứng minh chủ đề có traffic.
- [ ] Phần pitch BD ghi rõ entity và không dùng tên khách của đối thủ làm social proof.

## Anti-patterns

- Kết luận "lệch tâm nên bỏ trang" → script chỉ chọn ứng viên. `content-refresh` và người vận hành quyết, theo hiển thị, click và vai trò trang.
- So focus giữa 2 site, hoặc giữa 2 model → cosine chỉ so được trên cùng site, cùng model, cùng scope.
- Dùng tiêu đề bài dự kiến để chấm focus → pilot đo outline chỉ tương quan 0,6 với vector bài thật. Chỉ dùng outline để gán cụm.
- Lấy số cụm theo cảm giác → dùng silhouette có sàn kích thước cụm, rồi Claude đặt tên.

## Changelog

- v1.1.1 (2026-10-19): ghi rõ nhãn khoảng trống dưới 0,86 là ứng viên Claude đọc (94%, dưới cổng 95%), không phải kết luận. Rút description còn 268 ký tự. Không đổi ngưỡng.
- v1.1 (2026-10-19): thêm việc khoảng trống chủ đề với đối thủ: `scripts/competitor_titles.py` (title + H1 từ sitemap công khai), lệnh `gold-sheet` và `gap` trong `topical.py`, hiệu chuẩn gold mù 110 trang (prompt `Document`, ngưỡng khoảng trống 0,86). Thêm Bước 0 kiểm tool, bảng Phân việc model, Tự phản biện. Test offline `tests/test_gap.py`, `tests/test_competitor_titles.py`.
- v1.0 (2026-10-19): tạo mới từ pilot site mẫu: 4 prompt × 3 mức MRL, kiểm proxy với GSC chiều page, `selftest` cho cổng gán bài. Test offline `tests/test_topical.py`.
