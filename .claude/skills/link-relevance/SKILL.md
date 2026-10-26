---
name: link-relevance
description: "Kiểm anchor và đoạn chứa link có khớp trang đích không. Internal link: code bắt đích lỗi, trang chuyên mục, anchor trùng query GSC mà trỏ khác URL Google chọn; Gemma + Jev chấm độ khớp. Backlink: chấm T.T.T từ dữ liệu Ahrefs, verdict KEEP/REVIEW/REJECT theo tín hiệu máy M1–M3, đích 410. Dùng khi audit internal link, audit backlink hoặc trước khi sửa link hàng loạt."
metadata:
  version: "1.1"
---

# link-relevance — anchor có đưa người đọc tới đúng trang không

Tài liệu rò rỉ của Google có trường ngữ cảnh của anchor và `anchorMismatchDemotion`. Công thức thật chưa công bố. Skill này đo một việc đã kiểm được trên dữ liệu thật: anchor và đoạn chứa link có nêu đúng điều trang đích trả lời không.

Gốc đường dẫn là root repo. Script: `skills/link-relevance/scripts/links.py`. Rubric Jev: `skills/link-relevance/tasks/anchor-target.json`. Jev ở `tools/ai-assist/jev.py`; ở workspace gốc, Jev nằm ở `SEO Production/tools/ai-assist/`.

## Khi nào dùng

- Audit internal link của một site: tìm link trỏ sai trang, trỏ trang chuyên mục, trỏ trang đã redirect hoặc 404.
- Trước khi sửa link hàng loạt bằng `internal-linking` hoặc `wp-content-review-apply`: lấy danh sách link cần sửa có bằng chứng.
- Tìm anchor tranh query với trang khác: anchor trùng query GSC nhưng trỏ khác URL Google đang chọn.
- Không dùng để chọn vị trí đặt link mới (MC hay SC). Việc đó thuộc `internal-linking`, rubric Jev `link-placement`.
- Audit backlink: loại nguồn, T.T.T của từng link, link spam hoặc độc, backlink trỏ trang đã 410 hoặc redirect về trang chủ. Đọc mục "Nhánh backlink".

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| `rows.jsonl` (có level anchor), `pages.jsonl`, store vector | `site-vector-index` (`extract.py`, `svi.py build`) | dựng trước |
| `queries.jsonl` GSC (text, chosen, share, impr) | lệnh `route` của `retrieval-lab` | bỏ phần kiểm định tuyến GSC |
| `OPENROUTER_JEV_API_KEY` | `.agent-secrets/.env` | chỉ chạy phần code + Gemma, mọi link chưa có code xử lý ghi review |
| Cổng `anchor-score` | registry `00-client-context/model-calibration.json` | dùng defaults và ghi "bản nháp" |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,numpy,gemma,jev,gsc?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

1. Chuẩn bị: `<venv>/bin/python -I skills/link-relevance/scripts/links.py prepare --rows rows.jsonl --pages pages.jsonl --store <store> --queries queries.jsonl --brand "<Tên brand>" --out-dir <W>`.
   - Code gắn cờ: `target_missing`, `target_listing`, `listing_named`, `anchor_names_target`, `generic_anchor`, `naked_url`, `empty_anchor`, `lang_mismatch`, `gsc_conflict`, `anchor_multi_target`.
   - Trang chuyên mục tự nhận khi dưới 150 chữ và có ≥ 8 link vùng main. Thêm `--listing REGEX` nếu site có mẫu URL riêng.
2. Chạy Jev: `python3 -I tools/ai-assist/jev.py --task skills/link-relevance/tasks/anchor-target.json --in <W>/jev_in.jsonl --out <W>/jev_out.jsonl --budget 0.2`. Mỗi link tốn khoảng 0,00004 USD. Link đã có code xử lý không vào Jev.
3. Site mới hoặc rubric đổi version: hiệu chuẩn bằng skill `model-calibration`.
   - `links.py sample --links <W>/links.jsonl --out-dir <W>/calibration`. Phiếu `gold_todo.txt` không có điểm model.
   - Claude gán gold ≥ 40 link theo định nghĩa ở mục dưới, trước khi xem điểm. Mở chữ của trang đích khi ca biên.
   - `links.py validate --links ... --gold gold.jsonl --jev-out ... --out-dir <W>/calibration --clusters <topical-focus>/pages.jsonl`.
   - `calibrate.py cosine --pairs <W>/calibration/score_pairs.jsonl --grid=0.0:1.4:0.02 --rubric anchor-score --write ...`.
   - Có GSC: `calibrate.py auc --data <W>/calibration/gsc_rows.jsonl --metric margin --label agree --group group --rubric anchor-gsc-routing --write ...`.
4. Quyết định: `links.py decide --links <W>/links.jsonl --jev-out <W>/jev_out.jsonl --registry 00-client-context/model-calibration.json --site <domain> --out-dir <W>`.
5. Claude đọc mọi link review, bảng trang chuyên mục và bảng anchor trùng query GSC. Claude gom kết quả thành việc:
   - Link trỏ trang chuyên mục hoặc trang sai → sửa đích về trang có cột "Trang gần hơn" sau khi đọc trang đó, qua `internal-linking` rồi `wp-content-review-apply`.
   - Đích lỗi → trỏ thẳng về URL cuối của redirect, hoặc bỏ link.
   - Anchor trùng query nhưng Google chọn trang khác → đọc cả 2 trang. Nếu link đúng còn Google chọn trang khác, chuyển `retrieval-lab` hoặc `query-processing-diagnosis` để xét cannibalization.
   - Khối mẫu lặp trên nhiều trang (ví dụ nút "Xem bảng giá" trỏ trang dịch vụ) → sửa một lần ở template.

## Nhánh backlink (T.T.T)

Thang T.T.T theo SOP `02-raw/knowledge/sop/12-backlink-stack-models.md` §2: Theme 35, Traffic 35, Trust 30. DR, DA, TF, CF chỉ là bộ lọc thô. Script: `skills/link-relevance/scripts/backlinks.py`.

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,numpy,gemma,ahrefs?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

1. Lấy backlink từ Ahrefs `site-explorer-all-backlinks`, `mode=subdomains`, `history=live`, `aggregation=1_per_domain`.
   - Chọn trường: `url_from,url_to,anchor,title,snippet_left,snippet_right,domain_rating_source,url_rating_source,traffic,positions,links_external,tld_class_source,page_type_source,page_category_source,is_spam,is_content,is_dofollow,is_ugc,is_sponsored,is_image,languages,root_name_source,first_seen_link`.
   - Mỗi dòng tốn khoảng 42 unit. Lấy 2 lát: mới nhất theo `first_seen_link`, và `is_spam=false` + `is_content=true` theo `url_rating_source`. Không dùng `output: csv` vì connector trả lỗi.
   - Kết quả lớn tự lưu ra file `[{type,text}]`. Script đọc thẳng file đó.
2. Chuẩn bị: `<venv>/bin/python -I skills/link-relevance/scripts/backlinks.py prepare --ahrefs <file>... --store <store site> --own-domains <domain mình> --registry 00-client-context/model-calibration.json --site <domain> --out-dir <W>`.
   - Code gắn cờ: `spam` (Ahrefs), `zero_organic` (tên miền nguồn không có organic traffic), `obl_farm` (trên 100 link ra), `spam_topic` (danh mục cờ bạc, người lớn, hoặc anchor casino, black hat, PBN), `own_network`, `platform`, `nofollow`, `not_content`, `image`, `target_missing`, `lang_other`, `empty_context`.
   - Verdict theo `skills/backlink-research/references/spam-filter-criteria.md`: M1 = `spam`, M2 = `zero_organic`, M3 = `obl_farm` hoặc `spam_topic`. Từ 2 tín hiệu là REJECT, 1 tín hiệu là REVIEW, không có là KEEP.
   - Theme: EmbeddingGemma đo "title | anchor: đoạn quanh link" (`SearchQuery`) với trang đích (`Document`). Code bỏ URL và tên miền khỏi chữ trước khi đo.
   - Traffic: traffic của chính trang nguồn, trang chỉ có từ khoá được tối đa nửa thang. Trust: UR, số link ra, dofollow, cộng DR hoặc tên miền gov, edu. Chỉ link REJECT có Trust 0.
3. Site mới: gán gold ≥ 40 link bằng `sample` rồi `validate`, như bước 3 của nhánh internal link. Ghi cổng vào registry, rubric `backlink-theme`, trường `lo`, `hi`, `pass`.
4. Báo cáo: `backlinks.py report --links <W>/bl_links.jsonl --out <W>/report.md`.
5. Claude kiểm mã HTTP của mọi đích trong mục "Đích không còn trong store" bằng `curl -s -o /dev/null -w "%{http_code} %{redirect_url}"`.
   - Đích 410 hoặc 302 về trang chủ còn backlink tốt → đề xuất 301 về trang cùng chủ đề. Người duyệt quyết, vì bài đã bỏ có lý do riêng.
   - Đích 301 về trang chuyên mục → xét trang con cùng chủ đề hơn.
6. Claude đọc nhóm REJECT theo tháng `first_seen`. Nếu nhóm này tăng nhanh hoặc chiếm phần lớn link mới, báo người vận hành. Chỉ đề xuất disavow theo disavow policy của file tiêu chí: có manual action, hoặc tụt hạng trùng thời điểm với đợt link lạ.

### Định nghĩa gold backlink

- yes khi title, URL hoặc đoạn quanh link của trang nguồn nói đúng chủ đề của trang đích. Với đích là trang chủ, chủ đề là thương hiệu và dịch vụ chính.
- yes với trang hồ sơ hoặc bài giới thiệu thương hiệu của chính site (Google Sites, Behance, trang tuyển dụng).
- no với danh bạ tên miền, trang "sites like", guestbook, trang cùng ngành mà đoạn quanh link không nói chủ đề đích.

### Đọc số cho đúng (gtvseo.com, 19/10/2026)

| Kiểm | Kết quả |
|---|---|
| Gold gán mù 3 tập: dev 60, holdout 40, holdout mới 31 (bỏ 11 link spam lộ rõ) | 120 link |
| AUC cos Theme, holdout mới | 0,92 (bản giữ URL 0,94, nhưng nhiều link sai qua ngưỡng hơn) |
| Ngưỡng `pass` 0,64 trên 120 link | precision 0,87, recall 0,99 |
| Ngưỡng 0,68 | precision 0,93, recall 0,82 |

- Holdout mới chỉ có 7 ca no, nên AUC dao động mạnh giữa các tập. Đọc precision ở ngưỡng, không đọc riêng AUC.
- Link sai còn qua ngưỡng: trang cùng ngành SEO có đoạn quanh link yếu. Claude đọc các link có cos từ 0,64 đến 0,70 khi cần quyết định.
- Ahrefs `is_spam` bỏ sót link farm và anchor cờ bạc. Trên gtvseo.com, 41 link REJECT theo M2 + M3 không bị Ahrefs gắn spam. Trên theaigrowth.io, 26 trong 33 tên miền không bị gắn spam có anchor cờ bạc và trên 500 link ra.
- Traffic và Trust là thang quy đổi từ số Ahrefs, chưa hiệu chuẩn với thứ hạng thật.

## Định nghĩa gold

- yes khi trang đích có đúng điều anchor nêu. Với anchor chung chung ("xem chi tiết", "tại đây"), đoạn chứa link cho biết điều đó. Điều đó là chủ đề chính của trang, hoặc có mục, mục danh sách hay định nghĩa riêng trên trang.
- no khi đích là trang chuyên mục chỉ liệt kê bài, trừ khi anchor gọi đúng tên chuyên mục.
- no khi đích hẹp hơn điều anchor hứa (anchor hứa 20 công cụ, đích nói một công cụ), hoặc đích nói chủ đề khác có chung từ.
- Ghi lý do vào trường `note` cho mọi ca biên.

## Đọc số cho đúng

Pilot site mẫu ngành agency SEO (19/10/2026): 3.123 link nội bộ vùng main của 308 trang, gold 130 link gán mù (dev 60, holdout 30, holdout mới 40).

| Kiểm | Kết quả |
|---|---|
| Margin Gemma (anchor + đoạn) → link trùng URL Google chọn cho query bằng anchor | AUC trong cụm 0,91 [0,86; 0,97], 379 cặp |
| Margin Gemma trên gold | AUC 0,90 |
| Jev `delivers` trên holdout mới (rubric viết sau dev) | AUC 0,93 |
| Điểm gộp p + 4 × margin trên holdout mới | AUC 0,95 |
| Ngưỡng điểm gộp 0,52 trên 111 link gold không trỏ chuyên mục | precision 95,6%, phủ 82% |
| Code "trang chuyên mục" | đúng 18/18 ca gold |

- Gold lấy mẫu theo dải margin nên có nhiều ca lệch hơn thực tế. Precision và độ phủ đo trên mẫu này, không phải tỷ lệ lệch của site.
- Jev dao động giữa các lượt chạy. Luật Jev ≥ 0,7 và margin ≥ −0,04 chọn ở lượt đầu đạt 77/78 ở lượt Jev thứ hai. Luôn đọc qua cổng.
- Điểm sát ngưỡng thì Claude đọc. Pilot có 35 nút "Xem bảng giá" cùng một template ở điểm 0,50.
- Bảng anchor trùng query GSC mô tả việc anchor tranh query với trang khác. Bảng này không chứng minh link làm mất thứ hạng.

## Năng lực model đã xét

| Năng lực | Việc | Quyết định |
|---|---|---|
| Code | đích lỗi, trang chuyên mục, anchor gọi tên đích, anchor rỗng, URL trần, lệch ngôn ngữ, query GSC, một anchor nhiều đích | dùng: xử lý 874 link không cần model |
| EmbeddingGemma `SearchQuery` cho "anchor: đoạn", `Document` cho trang | margin giữa đích và trang gần nhất còn lại | dùng: AUC gold 0,90; trong cụm GSC 0,91 |
| EmbeddingGemma chỉ anchor | như trên | bỏ: AUC gold 0,81 |
| EmbeddingGemma `Document` cho đoạn (vector anchor trong store) | như trên | bỏ: AUC gold 0,88, thấp hơn `SearchQuery` |
| Jev `link-placement` câu `fit` | độ khớp | bỏ cho việc này: AUC 0,82, gắn `natural_bridge` cho 19/26 ca lệch. Rubric này vẫn dùng cho vùng MC, SC ở `internal-linking` |
| Jev `anchor-target` câu `delivers` (noul) | độ khớp | dùng trong điểm gộp |
| Jev ảnh | link ảnh | chưa: link ảnh dùng alt làm anchor; ảnh thuộc `visual-serp-lab` |
| GLM Flash | — | không cần: skill không trích câu |
| Code trên trường Ahrefs | tín hiệu M1–M3, verdict, loại nguồn, đích mất, Traffic, Trust | dùng: không cần model. Gold: 1/83 link Theme yes bị REJECT (diễn đàn 4.062 link ra) |
| EmbeddingGemma "title \| anchor: đoạn" của trang ngoài, bỏ URL | Theme của backlink | dùng: precision 0,87 ở ngưỡng 0,64 trên 120 gold |
| Jev cho backlink | Theme | chưa: Gemma đủ dùng. Jev chỉ nhận chữ công khai, trang nguồn ngoài đạt điều kiện này nếu sau cần |

## Output

- `<W>` = `06-onpage-internal-link/<CLIENT>_link-relevance_<YYYY-MM-DD>/`: `links.jsonl`, `jev_in.jsonl`, `jev_out.jsonl`, `summary.json`, `decisions.jsonl`, `report.md`.
- Gold và kết quả hiệu chuẩn: `<W>/calibration/`. Entry registry: `anchor-target`, `anchor-score`, `anchor-gsc-routing`, `backlink-theme`.
- Nhánh backlink: `<W>` = `07-offpage/<CLIENT>_backlink-ttt_<YYYY-MM-DD>/`: `bl_links.jsonl`, `summary.json`, `report.md`.

## Gate

- [ ] Jev chỉ nhận chữ công khai của trang web. Không gửi GSC hay dữ liệu nội bộ vào Jev.
- [ ] Cổng `anchor-score` lấy từ registry của site, hoặc báo cáo ghi rõ "bản nháp, cổng defaults".
- [ ] Claude đã đọc mọi link review và mọi dòng của bảng GSC trước khi đề xuất sửa.
- [ ] Đề xuất sửa nêu trang đích mới đã được Claude đọc, không lấy thẳng cột "Trang gần hơn".
- [ ] Báo cáo khách ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".

## Anti-patterns

- Sửa link theo cột "Trang gần hơn" mà không đọc trang → Gemma gợi ý trang gần nghĩa, có khi là trang chuyên mục hay case study.
- Dùng Jev `link-placement` để bắt link lệch → câu `fit` đo độ liên quan chủ đề nên nhận cả link trỏ trang chuyên mục.
- Sửa một link trong khối template → khối lặp ở mọi trang, sửa ở template một lần.
- Coi `gsc_conflict` là link sai → nhiều ca link đúng nhưng Google đang chọn trang khác. Đọc cả 2 trang trước.
- Tin `is_spam` của Ahrefs là đủ → bỏ sót link farm và anchor cờ bạc. Đọc verdict, không đọc riêng `is_spam`.
- Dùng chữ "toxic" trong báo cáo → ghi "REJECT theo M#" để truy được tín hiệu.
- Đo Theme khi chữ còn URL trần → slug của trang đích trong URL đẩy cos lên, dù trang nguồn là danh bạ tên miền.

## Changelog

- v1.0 (2026-10-19): tạo mới từ pilot site mẫu: 3.123 link, gold 130 link (có holdout mới cho rubric `anchor-target` 2026-10-19.1), điểm gộp Jev + Gemma, kiểm định tuyến GSC. Test offline `tests/test_links.py`. Nhánh backlink để v1.1.
- v1.1 (2026-10-19): nhánh backlink T.T.T từ Ahrefs, `scripts/backlinks.py`, test `tests/test_backlinks.py`. Gold 120 link của gtvseo.com qua 3 tập, ngưỡng `pass` 0,64.
