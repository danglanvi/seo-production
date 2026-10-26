---
name: content-inventory-audit
description: "Kiểm kê mọi bài của site: chất lượng (Jev), lỗi thời, bài trùng (Gemma + SERP), danh mục chính qua cổng tin cậy, đề xuất giữ, làm mới, gộp, 301, 410. Đổi cây chuyên mục an toàn, chọn đích 301 hoặc 410 cho URL chết. Dùng khi dọn blog, rà danh mục hoặc xử lý URL 404."
metadata:
  version: "1.2"
---

# content-inventory-audit — kiểm kê bài, cây chuyên mục và vòng đời URL

Skill này rà mọi bài viết của site. Skill gán danh mục chính qua cổng tin cậy, tìm thông tin lỗi thời, tìm bài trùng và đề xuất số phận từng bài. Skill cũng đổi cây chuyên mục qua DRY và chọn đích 301 hoặc 410 cho URL chết. Phần tất định nằm trong script. Chấm chất lượng bài dùng `content-quality-lab`. Tìm cặp trùng dùng `site-vector-index`. Kiểm SERP dùng `semantic-content-network`.

Gốc đường dẫn là root repo. Script nằm ở `skills/content-inventory-audit/scripts/`, chỉ cần Python chuẩn và WP-CLI trên server:

- Kiểm kê: `inventory.py`, `export_posts.php`, `apply_cats.php`. Rubric Jev: `tasks/category-pick.json`.
- Cây chuyên mục: `build_tax_plan.py`, `taxonomy_rollout.php`.
- Vòng đời URL: `pick_target.py`, `wayback_cdx.py`, `chain_check.py`.
- Xuất dữ liệu chỉ đọc: `export_urls.php`, `export_tax_redirects.php`.

Reference: luật bỏ bài, cột bảng kiểm kê và quy trình chọn đích 301 hoặc 410 ở `references/bo-bai.md`. Đổi cây chuyên mục ở `references/cay-chuyen-muc.md`. Danh sách công cụ đã ngừng hoặc đổi tên ở `references/loi-thoi.tsv`.

## Khi nào dùng

- Dọn blog: tìm bài trùng, bài lỗi thời, bài chỉ có kiến thức chung, bài của kênh đã ngừng.
- Rà danh mục chính của mọi bài, thêm hoặc gỡ chuyên mục sai.
- Chuẩn bị danh sách bài cần làm mới cho đợt content.
- Người duyệt chê gốc cây chuyên mục, hoặc sắp gán danh mục chính hàng loạt: chạy nhánh B.
- URL 404 cần chọn đích 301 hoặc 410, trang ngừng bán, đổi slug hàng loạt: chạy nhánh C. `technical-seo-audit` chuyển việc này sang đây.
- Không dùng cho một trang lẻ. Dùng `seo-onpage` hoặc `ngram-semantic-gap`.
- Không dùng để dựng lại kiến trúc nội dung và link. Dùng `semantic-content-network`.
- Không dùng để chấm effort một nhóm trang nhỏ. Dùng `content-quality-lab`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| `posts.json`: bài, chuyên mục, danh mục chính, mô tả, H2 | `scripts/export_posts.php` qua SSH + WP-CLI (hồ sơ `00-client-context/wp-server.md`) | không có quyền server: dùng REST API, không đọc được danh mục chính. Chỉ làm phần gán chuyên mục và báo người vận hành |
| `scope.tsv`: phạm vi từng chuyên mục (`slug`, `pham_vi`) | Claude viết từ mô tả chuyên mục, người duyệt xác nhận | hỏi |
| `rows.jsonl`, `pages.jsonl` và store vector của site | `site-vector-index` (`extract.py`, `build --keep-text`) | dựng store trước |
| GSC query × page 90 ngày | `tools/gsc/gsc.sh` | dừng bước đề xuất bỏ bài; vẫn làm danh mục và quét lỗi thời |
| SERP top 10 của cặp trùng | Firecrawl hoặc DataForSEO | không đề xuất gộp |
| Danh sách trang tiền và trang bằng chứng | `00-client-context/` | hỏi |
| Registry ngưỡng | `00-client-context/model-calibration.json`, rồi `tools/ai-assist/calibration-defaults.json` | dùng 0,9/0,6 và hiệu chuẩn trước khi ghi lô lớn |
| Nhánh B, C: `urls.json`, `cats.json`, `rules.json`, `uris.json`, `terms.json`, `cpt.json` | `export_urls.php`, `export_tax_redirects.php` qua SSH + WP-CLI | dừng nhánh B và C. Giao plan cho dev, ghi giới hạn vào báo cáo |
| Nhánh B: `spec.json` (cây mới), `map.tsv` (danh mục chính mới) | Claude viết, người duyệt chốt cây | hỏi |
| Nhánh C: `urls.tsv` (URL chết, click, danh sách bỏ đã duyệt) | GSC, crawl, log, backlink; người duyệt chốt danh sách bỏ | hỏi |
| Nhánh C: bản lưu Wayback | `wayback_cdx.py` | báo cáo ghi "chưa tra Wayback". Mọi dòng `410_de_xuat` chuyển sang người duyệt |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code (`inventory.py`) | Input Jev, cổng danh mục chính, quét năm cũ và tên công cụ đã ngừng, ghép cặp trùng với GSC, luật đề xuất | dùng: lượt thử 19/10 tái tạo file 17–18/10 (mục "Đọc số cho đúng") |
| Code (`build_tax_plan.py`, `pick_target.py`, `chain_check.py`, `wayback_cdx.py`) | Chẩn đoán cây, dựng plan, tra DB → slug cũ → Wayback, kiểm chuỗi và đích redirect | dùng: tất định. `tests/test_url_lifecycle.py` tái tạo ca hỏng thật 17–18/10 |
| Jev `redirect-pick` | Chọn đích 301 khi nhiều URL cần đích (nhánh C) | dùng qua ngưỡng ở `tools/ai-assist/README.md` §4. Chạy lại `pick_target.py --strict` để kiểm đích Jev chọn |
| Jev `category-pick` 2026-10-18.1 | Danh mục chính | dùng qua cổng registry. Rubric viết cho blog agency SEO tiếng Việt. Site ngành khác: sửa câu đầu và 2 câu cuối của `instructions`, tăng version, hiệu chuẩn mù |
| Jev `content-effort` | Effort, dữ liệu gốc (information gain), trải nghiệm tự làm (E-E-A-T), nguồn có tên | dùng qua `content-quality-lab`, đọc qua cổng registry |
| Jev `claim-guard` | Câu bảo đảm, tự xếp hạng, số không nguồn | dùng qua `content-quality-lab` cho bài giữ hoặc làm mới |
| Jev `gsc-cannibal-pair` | Nhãn cặp trùng ý định | chỉ dùng chế độ chữ: để `shared_queries` rỗng. Không gửi query GSC. Nhãn chỉ đề cử cặp, SERP quyết |
| EmbeddingGemma 2 | Ứng viên cặp trùng; 5 ứng viên đích 301 (nhánh C) | cặp trùng: dùng qua `site-vector-index pairs --level page` trên store `--prompt Clustering`. Chưa có ngưỡng cosine hiệu chuẩn cho cặp trang: lấy cặp cao nhất, Claude và SERP quyết. Đích 301: `tools/ai-assist/emb.py nn --k 5`, không lấy top-1 làm đích (top-1 đúng 4/11 URL, 17/10) |
| GLM Flash | Trích câu | không dùng. Không dùng nhãn hành động của GLM: GLM gắn "refresh" cho 82% trang |
| Rubric `content-quality` của `site_quality_llm.py` | — | không chuyển vào skill: script gọi model ngoài danh sách được duyệt. `content-effort` thay thế |
| Claude | Scope chuyên mục, quyết dải dưới ngưỡng tự ghi, đọc hit lỗi thời, chọn bài giữ, loại bài, đích 301, đọc trục chia của cây, đọc bản lưu Wayback, tự phản biện | dùng. Trục chia của cây không giao Jev: chưa có rubric, mỗi site chỉ một cây |

Dữ liệu GSC chỉ xử lý local bằng code hoặc Gemma. Không gửi GSC vào Jev.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,jev,gsc,gemma?,ssh?,wp-cli?,firecrawl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nhánh B và C dùng danh sách `'python3,ssh,wp-cli,gsc?,jev?,gemma?'`.

| Yêu cầu | Nhánh | Đọc |
|---|---|---|
| Kiểm kê bài, gán danh mục chính, bài trùng, lỗi thời, bỏ bài | A (bước 1–12) | `references/bo-bai.md` mục 1–3 tại bước cần |
| Đổi cây chuyên mục: chê gốc cây, thêm, gộp, đổi cha hoặc slug chuyên mục | B | `references/cay-chuyen-muc.md` |
| Chọn đích 301 hoặc 410 cho URL chết, trang ngừng bán, đóng tạm, redirect hàng loạt | C | `references/bo-bai.md` mục 4 |

### Nhánh A — kiểm kê bài

Đặt `<W>` = `03-audits/content/<CLIENT>_inventory_<YYYY-MM-DD>/`. Đặt `S` = `skills/content-inventory-audit/scripts/inventory.py`.

1. Xuất bài: `wp eval-file skills/content-inventory-audit/scripts/export_posts.php > <W>/posts.json` (chỉ đọc).
   - Nếu người duyệt chê gốc cây chuyên mục, hoặc sắp gán danh mục chính hàng loạt, chạy `diagnose` của nhánh B trước bước 2.
   - Nếu `permalink_structure` chứa `%category%`, đổi danh mục chính sẽ đổi URL. Dừng và hỏi người duyệt.
   - Nếu `pm_settings.auto_update_uris` bật, Permalink Manager có thể đổi URI. Dừng và hỏi người duyệt.
   - Đọc nơi theme hiển thị chuyên mục: breadcrumb, nhãn trên thẻ bài, schema. Theme có thể không đọc danh mục chính.
2. Viết `<W>/scope.tsv`: mỗi chuyên mục một dòng phạm vi. Chuyên mục không có dòng thì Jev không chọn được.
   `python3 $S jev-in --posts <W>/posts.json --scope <W>/scope.tsv --site <domain> --out <W>/jev_in.jsonl`
   `python3 -I tools/ai-assist/jev.py --task skills/content-inventory-audit/tasks/category-pick.json --in <W>/jev_in.jsonl --out <W>/jev_out.jsonl --budget 0.05`
3. Nếu site hoặc version rubric chưa có registry, hiệu chuẩn bằng `model-calibration`:
   - Gán gold ≥ 40 bài trước khi xem nhãn Jev (`{"id", "label": slug đúng}`). Ghi sha256 và giờ vào `calibration/gold_log.md`.
   - Chạy `calibrate.py jev --question primary --positive <slug bất kỳ>` và đọc `conf_gate` làm ngưỡng tự ghi. Ghi registry với `--rubric category-pick`.
   - Nếu sửa rubric sau khi xem dev, gán holdout mới.
4. Chạy cổng: `python3 $S category --posts <W>/posts.json --jev-out <W>/jev_out.jsonl --registry 00-client-context/model-calibration.json --registry tools/ai-assist/calibration-defaults.json --site <domain> --industry <ngành> --out <W>/category`
   - Entry của site thắng entry `*`. Entry `*` chỉ khớp khi cùng ngành, vì rubric viết theo ngành.
   - Từ ngưỡng tự ghi: tự ghi. Bài đang có danh mục chính hẹp, còn gắn và khác Jev thì Claude đọc.
   - Từ `reject_below` tới dưới ngưỡng tự ghi: Claude đọc tiêu đề + H2 và xác nhận.
   - Từ 0,6 tới dưới `reject_below`: Claude chọn thay Jev.
   - Dưới 0,6: người duyệt quyết.
5. Claude ghi quyết định vào `<W>/quyet.tsv` (`id`, `quyet` = `giu`, `chon` hoặc `theo_jev`, `chuyen_muc`, `go`, `ly_do`).
   - Giữ danh mục chính hiện có khi danh mục đó hẹp, còn gắn và khớp chủ đề chính.
   - Gỡ chuyên mục chỉ khi chủ đề bài nằm ngoài hẳn phạm vi chuyên mục.
   - Bài dưới 0,6 lên trang duyệt. Id người duyệt chốt ghi vào `<W>/da_duyet.txt`.
   - Chạy lại bước 4 với `--claude <W>/quyet.tsv --approved <W>/da_duyet.txt`. File ghi là `<W>/category/apply.json`.
6. Quét lỗi thời: `python3 $S scan --pages <store>/pages.jsonl --rows <store>/rows.jsonl --out <W>/scan`
   - `--year-max` mặc định là năm trước năm nay. Thêm tên công cụ mới ngừng vào `references/loi-thoi.tsv`, kèm ngày theo thông báo chính thức.
   - Claude đọc mọi dòng của `scan_hits.tsv`. Bài nhắc tên cũ trong ngữ cảnh lịch sử không tính là lỗi thời.
7. Chấm effort theo bước 1–4 của `content-quality-lab`. Ghi `effort` = `yes` hoặc `no` theo cổng registry. Bài ở vùng chưa chắc để trống.
8. Tìm cặp trùng:
   - `<venv>/bin/python -I skills/site-vector-index/scripts/svi.py pairs --store <store Clustering> --level page --min 0.9 --cross-url --out <W>/pairs.jsonl`
   - `python3 $S dup --pairs <W>/pairs.jsonl --gsc <gsc_query_page_90d.tsv> --min 0.95 --out <W>/dup`. Hạ `--min` khi số cặp quá ít.
   - Bỏ cặp là bản dịch của nhau. Chọn query đại diện khác nếu `dup` chọn query điều hướng.
   - `python3 skills/semantic-content-network/scripts/scn.py serp-overlap --serp <serp> --pairs <W>/dup/serp_pairs.tsv --out <W>/serp`
   - Từ 6/10 URL chung: được xét gộp. 4–5/10: giữ cả hai, đo lại ở ngày 60. Dưới 4/10: giữ tách.
9. Ghép `<W>/inventory.tsv` theo `references/bo-bai.md` mục 1, rồi chạy `python3 $S decide --inv <W>/inventory.tsv --out <W>/decide`.
10. Claude đọc `proposals.tsv`: chọn đích 301 còn thiếu theo `references/bo-bai.md` mục 4, kiểm loại bài, ghi lý do. Mọi đề xuất bỏ bài lên trang duyệt của `wp-content-review-apply`.
11. Viết báo cáo, tự phản biện theo mục dưới, rồi kiểm Gate.
12. Sau khi người duyệt chốt:
    - Danh mục: `FIX=<W>/category/apply.json DRY=1 wp eval-file skills/content-inventory-audit/scripts/apply_cats.php`. Backup quan hệ chuyên mục và meta danh mục chính, rồi chạy `DRY=0`. Site dùng Yoast thêm `META=_yoast_wpseo_primary_category`.
    - Bỏ bài: làm theo `references/bo-bai.md` mục 3 bằng `wp-content-review-apply`.
    - Làm mới: chuyển danh sách sang plan content và `seo-onpage`.

### Nhánh B — đổi cây chuyên mục

Đặt `<T>` = `03-audits/content/<CLIENT>_taxonomy_<YYYY-MM-DD>/`. Lệnh đầy đủ ở `references/cay-chuyen-muc.md`.

1. Xuất dữ liệu chỉ đọc theo §2: `urls.json`, `cats.json`, `rules.json`, `uris.json`, `cpt.json`, `terms.json`, GSC 180 ngày.
2. Chẩn đoán: `python3 skills/content-inventory-audit/scripts/build_tax_plan.py diagnose --cats <T>/cats.json --posts <T>/urls.json --cpt-archives <T>/cpt.json --gsc <T>/gsc_page_180d.json --rules <T>/rules.json --out <T>/diagnose.json`
3. Nếu `ket_luan` = `cay_sai`, trình cây mới trước. Gán bài chỉ sau khi người duyệt chốt cây.
4. Viết `spec.json` và `map.tsv` theo §4. Dựng `plan.json` và kiểm redirect của plan theo §5.
5. Ghi theo §6: staging `DRY=1` → `DRY=0` → kiểm, rồi production `DRY=1` → backup → `DRY=0`. Kiểm sau ghi theo §7.

### Nhánh C — chọn đích 301 hoặc 410 cho URL chết

Đặt `<U>` theo `references/bo-bai.md` mục 4.2.

1. Xuất `urls.json`, `terms.json`, `rules.json`, `uris.json` như nhánh B bước 1. Viết `urls.tsv`.
2. Chạy `pick_target.py`, `wayback_cdx.py`, rồi `pick_target.py --wayback` theo mục 4.3.
3. Xử lý từng mã theo mục 4.4. 410 chỉ cho URL có `bo` = 1. Trang ngừng bán theo mục 4.5.
4. Kiểm trước khi ghi theo mục 4.6: `pick_target.py --strict` và `chain_check.py` thoát 0.
5. Ghi qua `wp-content-review-apply`, rồi kiểm theo mục 4.7.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Nhánh B chấm thêm checklist ở `references/cay-chuyen-muc.md` §8. Nhánh C chấm thêm checklist ở `references/bo-bai.md` mục 4.8.

Bản tốt nhất phải có:
- [ ] Mọi đổi danh mục chính đi qua cổng. Bài đang có danh mục chính hẹp, còn gắn và khác Jev không tự ghi dù Jev từ 0,9. Nguồn lỗi: lượt 17/10 có 4/57 bài Jev từ 0,9 bị người duyệt giữ danh mục cũ. Cả 4 bài đều có danh mục chính hẹp đúng chủ đề.
- [ ] Bài dưới 0,6 có quyết định của người duyệt, không theo Jev. Nguồn lỗi: ở dải dưới 0,6, Jev chỉ khớp quyết định cuối ở 5/30 bài.
- [ ] Báo cáo ghi URL trước và sau khi đổi danh mục, và nơi theme hiển thị chuyên mục. Nguồn lỗi: site mẫu in cố định một nhãn chuyên mục cho mọi thẻ bài, và breadcrumb lấy chuyên mục theo thứ tự chữ cái.
- [ ] Mọi cặp gộp có số URL chung trên 10. Không gộp chỉ vì cosine hay nhãn Jev. Nguồn lỗi: 5 cặp gộp của audit GSC 17/10 đều có cosine từ 0,957; SERP 18/10 cho 4 cặp tách và 1 cặp vùng xám.
- [ ] Mỗi bài gắn cờ lỗi thời có câu sai cụ thể do Claude đọc xác nhận. Nguồn lỗi: quét tên cũ khớp 44 lượt trên 39 trang, Claude đọc ngữ cảnh và chỉ còn 12 trang nói sai.
- [ ] Đề xuất làm mới dựa trên nhãn đã hiệu chuẩn (`content-effort`) và hit đã đọc, không dựa trên nhãn hành động của LLM. Nguồn lỗi: GLM gắn "refresh" cho 82% trang của site mẫu.
- [ ] Mỗi bài bỏ có đủ 4 việc: về nháp, rule 410 hoặc 301, sửa link nội bộ, sửa rule cũ trỏ vào bài. Nguồn lỗi: site mẫu thứ hai còn rule cũ trỏ vào bài đã bỏ, và một cặp 301 cứng trong mu-plugin làm bài giữ lại mất khỏi sitemap.
- [ ] Mọi rule 301, 302, 410 định ghi qua `chain_check.py` không còn phát hiện mức `loi`. URL chết đã tra DB, slug cũ và Wayback trước khi đề xuất 410. Nguồn lỗi: site agency mẫu (gtvseo) 17/10/2026, rule 301 cũ dẫn qua rule trung gian tới trang nháp; site khoá học mẫu (theaigrowth) 17/10/2026, 301 trỏ URI cũ của Permalink Manager.

## Đọc số cho đúng

Lượt thử trên site mẫu ngành agency SEO (dữ liệu 17–18/10/2026, chạy lại 19/10) và trên site mẫu thứ hai có kênh newsletter đã ngừng (18/10):

| Kiểm | Kết quả |
|---|---|
| Input Jev 186 bài | 186/186 dòng khớp; khác duy nhất ở 21 tiêu đề, vì skill giải mã HTML entity |
| Quyết định danh mục 131 bài | `decisions.tsv` khớp sau khi giải mã entity ở tiêu đề; `apply.json` khớp từng byte với file đã ghi: 106 bài đổi danh mục chính, 24 bài thêm chuyên mục, 5 bài gỡ |
| Jev khớp quyết định cuối theo dải | ≥0,90: 53/57 · 0,75–0,89: 21/27 · 0,60–0,74: 9/17 · <0,60: 5/30 |
| Cổng mới với registry site mẫu | tự ghi 48 bài, 48/48 khớp quyết định cuối; Claude đọc 36; Claude chọn 17; người duyệt 30 |
| Quét lỗi thời 329 trang (blocks) | `scan_hits.tsv` khớp từng byte: 44 lượt trên 39 trang; cột năm khớp 329/329 |
| Quét lỗi thời từ `rows.jsonl` 343 trang | 36 trang có hit, 35 trùng bản blocks. 4 trang chỉ có ở bản blocks đều không có thẻ sửa |
| Cặp trùng | 5/5 cặp của audit GSC nằm trong top 71 cặp store Clustering (cosine từ 0,957). `dup` chọn 5/10 query trùng chữ với bản kiểm SERP 18/10. 5 query còn lại là biến thể gần, ví dụ "seo từ khóa" thay cho "từ khóa seo" |
| Luật bỏ bài, 230 bài newsletter | 230/230 mã 410 hoặc 301 khớp; 82/82 đích 301 khớp. Nhãn bài trong file là nhãn sau khi Claude đọc lại |

- Store `--prompt SentenceSimilarity` cho cosine trang quá cao: 21.756 cặp từ 0,8. Store `Clustering` tách tốt hơn: 171 cặp từ 0,95.
- Ngưỡng 6/10 dùng cho quyết định gộp trang. `serp-clustering` dùng 4/10 để gom keyword. Hai việc khác nhau.
- Cổng 0,6 của skill là sàn chung. Registry của site có thể đặt `reject_below` cao hơn, ví dụ 0,75.
- `khop_jev_theo_dai` trong `summary.json` so Jev với quyết định cuối. Số này chỉ có nghĩa sau khi có `quyet.tsv`.
- Nhánh B và C chưa chạy trên site thật bằng bản script này. Test offline tái tạo các ca hỏng 17–18/10. `taxonomy_rollout.php` mới chạy đường DRY trên stub: chạy `DRY=1` trên staging trước lần ghi đầu.

## Output

- `03-audits/content/<CLIENT>_content-inventory_v<N>.md`: kết luận, bảng danh mục theo cổng, bảng lỗi thời, cặp trùng và verdict SERP, đề xuất từng bài, tự phản biện.
- `<W>/`: `posts.json`, `scope.tsv`, `jev_in.jsonl`, `jev_out.jsonl`, `category/`, `quyet.tsv`, `scan/`, `dup/`, `serp/`, `inventory.tsv`, `decide/`.
- Nhánh B: `03-audits/content/<CLIENT>_taxonomy_v<N>.md` (5 dấu hiệu, cây cũ và cây mới, URL trước và sau, redirect, log DRY). Thư mục `<T>/`: file xuất, `diagnose.json`, `spec.json`, `map.tsv`, `texts.json`, `plan.json`, log rollout.
- Nhánh C: bảng `ra.tsv` có lý do từng dòng, `moi.json`, `findings.tsv` trong `<U>/`. Chạy trong kiểm kê thì gộp vào báo cáo kiểm kê.
- Skill không ghi lên site. Ghi chỉ sau khi người duyệt chốt, theo bước 12 của nhánh A, §6 của nhánh B hoặc mục 4.7 của nhánh C.

## Gate

- [ ] URL bài không đổi khi đổi danh mục chính, hoặc người duyệt đã chốt redirect.
- [ ] Ngưỡng cổng lấy từ registry đúng site và version, hoặc báo cáo ghi rõ "chưa hiệu chuẩn".
- [ ] Không bài nào dưới 0,6 vào `apply.json` khi chưa có id trong `da_duyet.txt`.
- [ ] Mọi cặp gộp có verdict SERP từ 6/10.
- [ ] Không trang tiền hay trang bằng chứng nào trong danh sách bỏ.
- [ ] Mọi đề xuất 410, 301, gộp có trạng thái "chờ người duyệt".
- [ ] Bảng tự phản biện 8 mục có bằng chứng trỏ được. Nhánh B và C có thêm checklist của nhánh.
- [ ] Không gửi GSC vào Jev.
- [ ] Nhánh B: cây sai theo `diagnose` có cây mới đã duyệt trước khi gán bài. Log `DRY=1` có `errors` rỗng trước mỗi lần `DRY=0`.
- [ ] Nhánh C: không URL nào thành 410 khi chưa có `bo` = 1. Không dòng `khoi_phuc`, `doc_wayback` hay `hoi` nào thành rule khi chưa có quyết định.
- [ ] `chain_check.py` thoát 0 trước và sau khi ghi redirect.

## Anti-patterns

- Ghi mọi nhãn Jev từ 0,9 → bài đang có danh mục hẹp đúng chủ đề bị đổi sai.
- Gộp vì cosine 0,98 → kiểm SERP; cặp 2/10 giữ tách.
- Xoá bài hoặc trả 404 → về nháp, rồi 410 hoặc 301.
- 301 bài bỏ về trang chủ hoặc trang chuyên mục → 301 về bài cùng chủ đề, không có bài phù hợp thì 410.
- Để rule 301 cũ trỏ vào bài vừa trả 410 → đổi rule cũ thành 410 hoặc sang bài giữ lại.
- Gắn "lỗi thời" cho mọi bài nhắc Universal Analytics → đọc ngữ cảnh trước.
- Sửa danh mục từng bài khi gốc cây sai → chạy `diagnose`, chốt cây, rồi mới gán bài.
- Đổi slug chuyên mục mà không đặt URI Permalink Manager → 301 trỏ URI cũ. Đặt `uri` cho mọi chuyên mục trong plan.
- 301 URL chết ngay → tra DB và slug cũ trước. Bài còn ở nháp thì hỏi khôi phục.
- Coi attachment trùng slug là bằng chứng bài còn → attachment không là đích và không là bằng chứng.
- Trả 410 cho mọi URL không tồn tại → 410 chỉ cho danh sách bỏ đã duyệt, URL khác giữ 404.

## Changelog

- v1.2 (2026-10-26): người duyệt chốt chỉ 301 về bài cùng chủ đề, không có bài phù hợp thì 410. Bỏ đích chuyên mục khỏi `bo-bai.md` (luật 6, mục 3, mục 4.1, checklist 4.8). `pick_target.py` báo `loi` khi đích là chuyên mục, thẻ hoặc archive; `chain_check.py` và `inventory.py` đổi thông báo theo luật mới. Nguồn: 301 về trang chuyên mục bị Google coi là soft 404 (19/10/2026).
- v1.1 (2026-10-25): nd-5 và tech-1 (phần chọn đích 301 hoặc 410). `bo-bai.md` mục 4.1 thêm câu "410 chỉ cho URL trong danh sách bỏ" kèm dòng Status hygiene của `seo-logfile-analysis` 1.3, và luật dump mọi post_type, post_status (chạy `export_urls.php` không kèm `--skip-plugins`, vì trường `path` cần plugin). Thêm nhánh B đổi cây chuyên mục (`build_tax_plan.py`, `taxonomy_rollout.php`, `references/cay-chuyen-muc.md`) và nhánh C vòng đời URL (`pick_target.py`, `wayback_cdx.py`, `chain_check.py`, `bo-bai.md` mục 4). Thêm `export_tax_redirects.php`. 410 chỉ cho danh sách bỏ đã duyệt.
- v1.0 (2026-10-19): tạo mới. Gom audit danh mục 17–18/10 (`build_jev_in.py`, `decide.py`, `export_posts_cats.php`, `apply_cats.php`), quét tất định của A5 (`a5_scan.py`) và luật bỏ bài ngày 18/10 thành `inventory.py` 5 lệnh và 2 script WP-CLI. Rubric `category-pick` 2026-10-18.1 giữ nguyên. Thêm cổng theo registry và luật "bài có danh mục hẹp thì Claude đọc". Không chuyển `site_quality_llm.py`. Test offline `tests/test_inventory.py`. Vincent chốt 19/10/2026: giữ ngoại lệ danh mục hẹp ở cổng 0,9; ngưỡng dưới 2 tầng (0,6–0,75 Claude chọn, dưới 0,6 người quyết).
