---
name: semantic-content-network
description: "Lập plan mạng nội dung (SCN) cả site: kiến trúc root–seed–node, click depth, PageRank nội bộ, trang thiếu theo QDP, gộp chỉ sau kiểm SERP 6/10, 1 URL mỗi template QP, mốc GEO, thẻ before/after duyệt theo lô. Dùng khi dựng lại kiến trúc nội dung hoặc internal link toàn site."
metadata:
  version: "1.0.1"
---

# semantic-content-network — plan mạng nội dung đủ 6 việc, có số và thẻ duyệt

Plan mạng nội dung không dừng ở việc nối link giữa các trang đang có. Plan phải tìm trang còn thiếu, kiểm SERP trước khi gộp, nối bằng chứng riêng vào trang tiền, đo mốc GEO trước khi sửa, gom thẻ thành lô và chọn 1 URL cho mỗi template truy vấn. Skill này điều phối các skill chuyên sâu và giữ phần tính toán tất định trong `scn.py`.

Gốc đường dẫn là root repo. Script: `skills/semantic-content-network/scripts/scn.py`, chỉ cần Python chuẩn. Cấu trúc file plan, luật thẻ và lô: `references/plan-va-the.md`.

## Khi nào dùng

- Dựng hoặc làm lại kiến trúc nội dung của site: root, seed, node, Core, Outer, hub.
- Lập plan internal link toàn site kèm trang mới, trang gộp và lịch đo.
- Chuẩn bị đợt sửa lớn nhiều trang cần người duyệt theo lô.
- Không dùng cho một trang lẻ. Dùng `ngram-semantic-gap` hoặc `seo-onpage`.
- Không dùng để dựng topical map cho site mới chưa có trang. Dùng `topical-map-creation`.
- Không dùng khi chỉ cần link plan cho trang có sẵn. Dùng `internal-linking`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Crawl Screaming Frog: `internal_all.csv`, `all_inlinks.csv` | SF headless (`technical-seo-audit`) | crawl trước |
| Store vector của site (`rows.jsonl` có dòng `anchor`) | `site-vector-index` | dựng store; thiếu thì `graph` dùng luật vị trí Content của SF |
| GSC query × page 90 ngày | `tools/gsc/gsc.sh` | dừng phần QP và trang thiếu; báo người vận hành |
| SERP top 10 của truy vấn cần kiểm | Firecrawl, DataForSEO hoặc Ahrefs (phần Ahrefs làm cuối) | không quyết gộp, không mở trang |
| Danh sách trang tiền, cây chuyên mục, topical map | `00-client-context/`, `04-structure-ux-cro/` | hỏi |
| Trang case study | sitemap của site | ghi "chưa có bằng chứng riêng" |
| Bộ prompt GEO | `geo-tracking-prompt-selection` | chọn prompt trước khi đo |
| Trang duyệt và bản sao lưu review | `wp-content-review-apply` | dựng trang duyệt trước khi trình thẻ |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code (`scn.py`) | Depth, PageRank nội bộ, độ trùng SERP, template QP từ GSC, trạng thái thẻ, chặn sửa chữ đã duyệt, dựng lô | dùng: lượt thử 19/10 tái tạo file 18/10 (mục "Đọc số cho đúng") |
| EmbeddingGemma 2 | Gom cụm chủ đề, định tuyến query → URL, ứng viên trùng ý định, anchor | dùng qua `topical-focus`, `retrieval-lab route`, `link-relevance`. Không tự viết code embedding |
| Jev | Nhãn cặp trùng ý định (`gsc-cannibal-pair`), vị trí link (`link-placement`), mục đích link CTA (`link-purpose`), effort trang | dùng qua rubric đã có registry, đọc qua cổng. `gsc-cannibal-pair` chỉ dùng chế độ chữ: để `shared_queries` rỗng, không gửi query GSC. Nhãn Jev chỉ đề cử cặp gộp, SERP quyết |
| Jev rubric `scn-role` (gán vai root/seed/node) | — | không dùng: bản 18/10 chỉ có 35 nhãn gold, gán cùng lúc với nhãn Jev, chưa có registry. Claude đọc ca chưa chắc. Muốn dùng thì hiệu chuẩn bằng `model-calibration` |
| GLM Flash | Trích câu | không dùng: không có việc trích câu |
| Claude | Foundation, luật gán vai, chấm QDP, quyết gộp, viết thẻ, gom lô, tự phản biện | dùng |

Dữ liệu GSC chỉ xử lý local bằng code hoặc Gemma. Không gửi GSC vào Jev.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,gsc,gemma,screaming-frog?,jev?,firecrawl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Đặt `<W>` = `04-structure-ux-cro/<CLIENT>_scn_<YYYY-MM-DD>/`. Đặt `S` = `skills/semantic-content-network/scripts/scn.py`.

1. Viết Foundation: Source Context, Central Entity, Central Search Intent. Root là trang chủ. Chia trang thành Core Section và Outer Section. Đặt mã cho trang tiền (M1, M2…) trong `<W>/money.tsv` (cột `url`, `ma`).
2. Đo đồ thị link:
   `python3 $S graph --sf <export SF> --money <W>/money.tsv --ctx-rows <store>/rows.jsonl --out <W>/graph`
   - `depth_all` tính theo mọi link follow và phải khớp cột Crawl Depth của SF (`sf_depth_khop`).
   - `depth_ngu_canh` chỉ tính link trong main content. Link header, footer, menu và khối lặp không tính.
   - Mục tiêu: trang tiền depth 1 bằng link ngữ cảnh. Seed Core ≤ 2. Seed Outer ≤ 3. Ít nhất 95% node ≤ 3.
   - Mô phỏng đề xuất bằng `--add add.tsv` (`source`, `target`) trước khi đưa vào thẻ.
3. Gán vai SCN cho từng URL: Root, Seed, Node, Core hoặc Outer, seed cha, hub. Gán bằng luật trước (loại trang, chuyên mục chính, bảng trang cố định). Dùng cụm của `topical-focus` cho trang chưa có luật. Claude đọc mọi ca chưa chắc. Ghi cột `nguon_nhan` (rule, claude).
4. Audit theo khối, mỗi khối dùng skill chuyên sâu:
   - Cụm lặp và boilerplate toàn site: `ngram-semantic-gap` cấp site.
   - Trang tiền: `ngram-semantic-gap` cấp trang, `seo-onpage`, `content-quality-lab` (chặn claim).
   - Link ngữ cảnh: `internal-linking` (luật vị trí link: SC trước), `link-relevance` (anchor).
   - Chất lượng bài: `content-quality-lab` (effort), `content-inventory-audit` (bài trùng, bài bỏ).
5. Tìm trang còn thiếu theo QDP. Lấy nhu cầu từ GSC và Autocomplete. Lấy ý định từ độ trùng SERP:
   `python3 $S serp-overlap --serp <serp.tsv hoặc thư mục JSON> --pairs <W>/pairs_new.tsv --out <W>/serp_new`
   - Cặp keyword mới ↔ trang có sẵn: từ 4/10 URL chung thì xếp keyword vào cụm của trang có sẵn. Cột `verdict` của `serp-overlap` dùng ngưỡng gộp 6/10, nên đọc cột `chung` ở bước này.
   - Chấm 4 tiêu chí QDP theo `skills/keyword-topic-url-mapping/references/qdp-gate.md`.
   - Đạt từ 3/4: mở trang. Đạt 2/4: thành heading trên trang có sẵn. Đạt 1/4 trở xuống: không mở.
6. Kiểm SERP trước khi gộp. Lấy cặp ứng viên từ `retrieval-lab route` (share < 0,6), Jev `gsc-cannibal-pair` và cosine:
   `python3 $S serp-overlap --serp <serp> --pairs <W>/pairs_merge.tsv --out <W>/serp_merge`
   - Từ 6/10 URL chung: được xét gộp. 4–5/10: vùng xám, giữ cả hai và xem lại ở ngày 60. Dưới 4/10: giữ tách.
   - Không gộp trang đang giữ Top 5 cho truy vấn của riêng nó. Không gộp trang bằng chứng.
   - Nhãn Jev hay cosine cao không đủ để gộp.
7. Nối bằng chứng riêng vào trang tiền. Đếm link từ trang case tới từng trang tiền trong `<W>/graph/pages.tsv`. Ghi năm của số liệu case. Chọn case khớp gói giá, địa phương hoặc ngành của trang tiền.
8. Đo mốc GEO trước khi sửa. Chọn prompt bằng `geo-tracking-prompt-selection`. Đo bằng `geo-answer-lab` (`collect.py` → `prepare.py` → `report.py`). Ghi ngày, model engine, chi phí. Ghi AI Overview và AI Mode là UNKNOWN khi chưa đo được.
9. Chẩn đoán Query Processing. Viết `<W>/templates.tsv` (`id`, `template`, `target`, `regex` theo cú pháp RE2 để dán vào GSC), rồi chạy:
   `python3 $S qp --gsc <gsc_query_page_90d.json> --templates <W>/templates.tsv --out <W>/qp`
   - Mỗi template chỉ có 1 URL đích. Nếu URL Google chọn đã ở Top 10, giữ URL đó.
   - Cờ `tách URL` và `lật URL` cần quyết định trong plan. Cờ `chưa chọn URL đích` cần Vincent hoặc khách chọn.
   - Không rút cụm khỏi trang đang giữ Top 5 trước ngày đo. Đo lại ở ngày 14, 30, 60 bằng `baseline.tsv`.
   - Dự án có SpySERP thì dùng `query-processing-diagnosis` thay lệnh này.
10. Viết thẻ before/after theo hợp đồng dữ liệu của `wp-content-review-apply`. Trước khi nạp thẻ:
    - `python3 $S status --reviews <bản sao review> --cards <file thẻ...> --out <W>/status.json`
    - `python3 $S guard --reviews <bản sao review> --cards <file thẻ mới> --out <W>/guard.json`. Mọi dòng `sua_chu_da_duyet` phải có lý do. Thẻ đã duyệt không sửa tại chỗ: tạo id mới.
11. Gom thẻ cùng luật thành lô: viết `<W>/lots.json`, rồi chạy `python3 $S batch --lots <W>/lots.json --cards <file thẻ...> --status <W>/status.json --out <W>/batch`. Luật lô ở `references/plan-va-the.md` mục 3.
12. Viết plan theo `references/plan-va-the.md` mục 1. Tự phản biện theo mục dưới, rồi kiểm Gate.
13. Sau khi người duyệt bấm duyệt, chuyển thẻ sang `wp-content-review-apply`. Skill này không ghi lên site.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Bảng trang còn thiếu: mỗi ứng viên có nhu cầu (GSC, Autocomplete), độ trùng SERP và điểm QDP trên 4. Nguồn lỗi: plan SCN bản 1 ngày 18/10 để /dich-vu-geo/ sang "giai đoạn sau" và không chấm QDP.
- [ ] Bảng gộp trang: mỗi cặp có số URL chung trên 10 và verdict theo ngưỡng 6/10. Không cặp nào gộp chỉ vì nhãn Jev hay cosine. Nguồn lỗi: kiểm SERP 18/10 bác 3/5 cặp gộp của audit GSC 17/10.
- [ ] Bằng chứng riêng (case study) có việc nối vào từng trang tiền, kèm năm của số liệu. Nguồn lỗi: bản 1 chỉ chẩn đoán case tách khỏi mạng và dời việc sang giai đoạn sau.
- [ ] Mốc GEO đo trước khi sửa: tỷ lệ nhắc tên, trích dẫn, share of voice theo engine, ngày đo và lịch đo lại. Nguồn lỗi: bảng chỉ số của bản 1 không có GEO.
- [ ] Thẻ cùng luật gom thành lô, mỗi lô có luật chung. Thẻ title, H1, đoạn mở, FAQ, giá trên trang tiền duyệt riêng. Nguồn lỗi: bản 1 đưa 207 thẻ duyệt từng thẻ.
- [ ] Query Processing: truy vấn trang tiền gom thành template, mỗi template có 1 URL đích, cờ tách hoặc lật URL và lịch đo ngày 14, 30, 60. Nguồn lỗi: bản 2 chưa áp Query Processing; khi áp, QP lật 2 đề xuất gộp và 1 title.

## Đọc số cho đúng

Lượt thử trên site mẫu ngành agency SEO (dữ liệu 15–19/10/2026, chạy lại 19/10):

| Kiểm | Kết quả |
|---|---|
| Độ trùng SERP 26 + 22 truy vấn | 2 file overlap khớp từng byte; 12 cặp gộp và trang mới cho cùng verdict với plan |
| 15 template QP từ GSC 25.000 dòng | `baseline.tsv` khớp từng byte; 15/15 template rơi đúng nhóm "ổn" hoặc "cần xử lý" như nhận định của plan |
| PageRank nội bộ 357 trang | 357/357 giá trị khớp; 54 dòng đổi thứ tự trong nhóm PR bằng nhau |
| Trạng thái 207 thẻ lúc 15:30 | 206/207 khớp; 1 thẻ sau đó đã ghi lên site nên bản sao lưu chỉ còn trạng thái mới |
| 7 lô duyệt | 7/7 danh sách khớp; 147 thẻ chờ = 68 trong lô + 79 thẻ riêng |
| Chặn sửa chữ đã duyệt (bài tiền) | 703 review, 15 chỗ trùng, 0 chỗ sửa, khớp bản cũ |
| Mốc GEO qua `geo-answer-lab` | 12/12 số (nhắc tên, BOFU, trích dẫn, SoV × 3 engine) khớp |

- SF xếp cả khối template vào vị trí Content. Dùng anchor của `site-vector-index` cho link ngữ cảnh: lượt thử khớp số trang link ngữ cảnh của 6/7 trang tiền trong ±1.
- 4/10 URL chung là ngưỡng xếp keyword vào cùng cụm khi lập plan (`serp-clustering`, bước 5). 6/10 là điều kiện gộp 2 URL đang có (bước 6). Lý do: cùng một keyword kéo lại SERP trong ngày chỉ chung 5–10/10 URL với chính nó, nên 4–5/10 nằm trong biên dao động.
- Số đo GEO qua API khác câu trả lời trong app. Chỉ dùng để so xu hướng giữa các lần đo.

## Output

- `04-structure-ux-cro/<CLIENT>_scn-plan_v<N>.md`: plan theo `references/plan-va-the.md` mục 1.
- `<W>/`: `graph/`, `serp_new/`, `serp_merge/`, `qp/`, `status.json`, `guard.json`, `batch/`, `money.tsv`, `templates.tsv`, `lots.json`.
- File thẻ cho trang duyệt của `wp-content-review-apply`.

## Gate

- [ ] `sf_depth_khop` bằng số trang, nghĩa là đồ thị đọc đúng export SF.
- [ ] Mọi cặp gộp có verdict SERP. Không có cặp gộp dưới 6/10.
- [ ] Mốc GEO đo xong trước khi ghi đợt 1 lên site.
- [ ] `guard.json` không còn dòng sửa chữ đã duyệt mà chưa có lý do.
- [ ] Mỗi lô có từ 2 thẻ, cùng một luật, không chứa thẻ title, H1 hay meta.
- [ ] Bảng tự phản biện 6 mục có bằng chứng trỏ được.
- [ ] Không gửi GSC vào Jev. Báo cáo khách ghi "chỉ số mô phỏng, trọng số thật của Google chưa công bố" cạnh số mô phỏng.

## Anti-patterns

- Plan chỉ sửa link, anchor, menu trên trang có sẵn → chạy đủ 6 việc của checklist.
- Gộp vì Jev gán "trùng ý định" 0,97 → kiểm SERP; cặp 4/10 giữ cả hai.
- Sửa chữ của thẻ đã duyệt rồi nạp lại cùng id → trang duyệt hiện value cũ; tạo id mới và báo người duyệt.
- Đo depth chỉ theo mọi link → header và footer che việc trang tiền thiếu link ngữ cảnh.
- Đo GEO sau khi đã ghi đợt 1 → mất mốc so sánh.

## Changelog

- v1.0.1 (2026-10-19): ghi rõ vai trò 2 ngưỡng SERP: 4/10 xếp keyword vào cùng cụm khi lập plan, 6/10 là điều kiện gộp 2 URL đang có. Bước 5 đọc cột `chung`, vì `verdict` của `scn.py` theo ngưỡng gộp.
- v1.0 (2026-10-19): tạo mới. Gom quy trình SCN A1–A5, bản 2–4 (thẻ v2, v3, v4), script s01–s10, `pagerank.py`, `serp_v2.py`, `qp_serp.py`, `qp_gsc_templates.py`, `qp_baseline.py`, `check_approved.py`, `build_v2_cards.py` của workstream site mẫu 15–19/10 thành `scn.py` 6 lệnh. Luật SCN đủ 6 việc thành checklist tự phản biện. Test offline `tests/test_scn.py`.
