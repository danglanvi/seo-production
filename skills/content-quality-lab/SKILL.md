---
name: content-quality-lab
description: "Đo dấu hiệu effort bằng Jev, tìm khối chữ lặp bằng EmbeddingGemma, chặn claim rủi ro (cam kết, hoàn tiền, tự xếp hạng, số không nguồn, số lệch fact) và kiểm an toàn khi viết lại. Dùng khi rà trang trước refresh hoặc GEO, soát template, copy hay bản viết lại trước khi đăng."
metadata:
  version: "1.3.0"
---

# content-quality-lab — trang có gì mà trang khác không chép được

Tài liệu rò rỉ của Google có `contentEffort`, `OriginalContentScore` và `siteAutopilotScore`. Công thức thật chưa công bố. Skill này đo 2 thứ đã kiểm được trên dữ liệu thật, và chặn claim rủi ro:

1. Dấu hiệu effort trong chữ của trang, đo bằng rubric Jev `content-effort`. Pilot đo nhãn `original_data` dự báo trang được AI trích trong cùng pool tìm kiếm với AUC 0,73.
2. Khối chữ lặp giữa các trang cùng site, đo bằng cosine passage của EmbeddingGemma. Lệnh này chỉ mô tả, chưa phải proxy traffic.
3. Claim rủi ro trong từng câu (lệnh `claims`): cam kết hoàn tiền, bảo đảm KPI hay thứ hạng, "#1", "hàng đầu", "tốt nhất", số liệu không nguồn, số lệch bảng fact của công ty. Lệnh này thực thi luật "không tự đưa cam kết hoàn tiền hay bảo đảm" của chủ site.
4. An toàn khi viết lại (lệnh `rewrite`): so từng đoạn cũ với đoạn viết lại. Code bắt số mất, tên mất, cam kết mới, cách viết cấm mới. Jev rubric `rewrite-keep` bắt fact bị bỏ hay bị đổi. EmbeddingGemma so query GSC đang mang click với passage của trang cũ và trang mới, trên máy.

Gốc đường dẫn là root repo. Script: `skills/content-quality-lab/scripts/quality.py`. Rubric: `skills/content-quality-lab/tasks/` (`content-effort.json`, `claim-guard.json`, `fact-match.json`, `rewrite-keep.json`). Jev ở `tools/ai-assist/jev.py`, EmbeddingGemma ở `tools/ai-assist/emb.py`; ở workspace gốc, 2 script này nằm ở `SEO Production/tools/ai-assist/`.

## Khi nào dùng

- Chọn trang cho `content-refresh`: trang thiếu số đo từ dự án thật trong khi trang được AI trích có.
- Chuẩn bị GEO cho một nhóm truy vấn: so trang mình với trang được trích trong cùng pool.
- Soát template: trang địa phương gần trùng nhau, lời chứng thực lặp, khối mẫu nằm sai mục.
- Soát claim trên trang đã đăng hoặc copy nháp trước khi đăng: cam kết, tự xếp hạng, số không nguồn, số lệch bảng fact.
- Soát bản viết lại trước khi đăng, nhất là trang có click: fact cũ còn đủ, không thêm cam kết, query đang mang click còn passage trả lời.
- Bài hoặc trang làm bằng AI hay theo template sắp đăng: chạy gate AI + spam (`references/gate-ai-spam.md`).
- Không dùng để chấm văn hay. Jev chỉ đọc dấu hiệu trong chữ. Lệnh `claims` chỉ so số với bảng fact đã chốt; lan truyền một fact vừa đổi thì dùng `site-fact-consistency`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| `rows.jsonl` cấp section và `pages.jsonl` | `extract.py` của `site-vector-index` | chạy extract trước |
| Pool truy vấn có nhãn được trích (chế độ so sánh) | `geo-answer-lab` (citations) + top 10 tìm kiếm, hoặc query của `retrieval-lab` | chỉ chạy báo cáo nhãn, không so sánh |
| Store passage (lệnh template) | `site-vector-index` | dựng store trước |
| `facts.json` và bí danh entity (lệnh claims) | `site-fact-consistency` sinh từ bảng fact đã chốt | chạy claims không có lớp fact, báo cáo ghi "chưa so bảng fact" |
| `OPENROUTER_JEV_API_KEY` | `.agent-secrets/.env` | dừng nhánh effort; nhánh claims chỉ chạy regex và cụm cấm |
| Cổng confidence, ngưỡng trùng, sàn fact | registry `00-client-context/model-calibration.json` | dùng defaults và ghi "bản nháp"; ngưỡng trùng không có defaults |
| `pairs.jsonl` {id, url, old, new} (lệnh rewrite) | trang duyệt nội dung, ops áp lên site, hoặc bản nháp người viết. Bản nháp chỉ gửi Jev khi site là site của chính đơn vị vận hành (`--own-site`) | dừng nhánh rewrite |
| Chữ trang hiện tại `{url, text}` và GSC page × query (lệnh rewrite, kiểm query) | crawl hoặc `extract.py`; `tools/gsc/gsc.sh query <property> 90 page,query` | bỏ kiểm query, báo cáo ghi "chưa chạy" |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | `content-effort`: dữ liệu gốc, trải nghiệm tự làm, nguồn có tên. `claim-guard`: bảo đảm ngầm, tự xếp hạng, số không nguồn, chủ thể câu. `fact-match`: chọn fact cùng chỉ số với câu. `rewrite-keep`: bản viết lại bỏ hay đổi fact, thêm fact hay lời hứa | dùng, đọc qua cổng của registry. Jev chỉ nhận chữ trang, không nhận query GSC. Bản nháp chưa đăng chỉ gửi Jev khi có `--own-site` |
| EmbeddingGemma 2 | Khối chữ lặp (cosine passage). Lấy 5 fact ứng viên cho câu có số (SentenceSimilarity cả 2 phía). Query GSC (SearchQuery) ↔ passage trang cũ và mới (Document); đoạn cũ ↔ đoạn mới (SentenceSimilarity) | dùng; prompt FactChecking đã thử, tách kém hơn. Cosine cũ ↔ mới chỉ mô tả |
| GLM Flash | Trích câu dẫn chứng | không dùng: lệnh claims đã làm việc ở cấp câu, Claude đọc trang review trực tiếp |
| Code | Regex cam kết, so số với fact, cụm cấm của bảng fact, lệch entity, thứ tự đề xuất. Lệnh rewrite: số mất, số mới chưa có cách viết trong bảng fact, tên mất, cam kết hay xếp hạng mới, cách viết cấm mới, passage khớp nhất của query bị sửa | dùng |
| Claude | Gán gold, hiệu chuẩn, đọc mọi dòng "người đọc" và trang review, quyết sửa | dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,numpy?,gemma?,jev?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. Chuẩn bị input Jev: `python3 -I skills/content-quality-lab/scripts/quality.py prepare --rows rows.jsonl --pages pages.jsonl --urls urls.txt --out <W>/jev_in.jsonl`. Script cắt mỗi trang ở 12.000 ký tự, vì Jev nhận tối đa khoảng 8K token.
2. Chạy Jev: `python3 -I tools/ai-assist/jev.py --task skills/content-quality-lab/tasks/content-effort.json --in <W>/jev_in.jsonl --out <W>/jev_out.jsonl --budget 0.1`. Mỗi trang tốn khoảng 0,00016 USD.
3. Site mới hoặc rubric đổi version: hiệu chuẩn bằng skill `model-calibration`.
   - Gán gold ≥ 40 trang trước khi xem nhãn Jev. Lấy mẫu theo dải p_yes, cộng một holdout ngẫu nhiên.
   - Chạy `calibrate.py jev` cho `original_data` và `first_hand`, rồi ghi registry.
   - Có pool: chạy `quality.py validate`, rồi `calibrate.py auc --metric original_data --label cited --group pool`.
4. Báo cáo: `quality.py report --jev-out <W>/jev_out.jsonl --registry 00-client-context/model-calibration.json --site <domain> --pools pools.jsonl --own-domain <domain> --out-dir <W>`.
5. Soát template: `<venv>/bin/python -I skills/content-quality-lab/scripts/quality.py template --store <store> --registry ... --site <domain> --urls urls.txt --out-dir <W>/template`. Site mới cần hiệu chuẩn ngưỡng `passage-dup` trước: gán 40+ cặp passage, rồi chạy `calibrate.py cosine --rubric passage-dup`.
6. Chặn claim: đọc `references/claims.md`, rồi chạy chuỗi lệnh ở mục 3 của file đó.
   - Lượt đầu không cần model: regex lớp 1 và cụm cấm của bảng fact.
   - Ghép Jev `claim-guard`, rồi Gemma, rồi Jev `fact-match`. Chạy lại `claims` sau mỗi bước.
   - Site mới: hiệu chuẩn `claim-guard`, sàn `fact-check` và `fact-match` bằng `model-calibration` trước khi ghép model. Gold câu gán mù trước lượt model đầu.
7. Claude đọc trang "review", các cặp trùng ở dải xám, các cặp trùng chứa lời chứng thực hay số liệu, và mọi dòng "người đọc" của `claims.tsv`. Claude gom kết quả thành việc:
   - Trang thiếu số đo trong khi trang được trích có → `expert-case-study` lấy số từ dự án thật, rồi `content-refresh`.
   - Lời chứng thực hay số liệu lặp nhưng lệch người nói hoặc lệch số → `site-fact-consistency`.
   - Trang địa phương gần trùng → thêm nội dung riêng của địa phương, hoặc gộp trang.
   - Câu cam kết, hoàn phí, bảo hành → danh sách cho chủ site quyết, kèm nguồn đối chiếu. Không viết câu cam kết mới.
   - Câu "sửa theo fact" → giá trị chuẩn của bảng fact; câu "xoá" → bỏ cụm so sánh nhất hoặc dẫn nguồn bên thứ ba.
8. Kiểm an toàn khi viết lại, trước khi đăng bản mới. Bản mới là chữ nháp chưa đăng, nên luật dữ liệu ở mục Gate quyết có gửi Jev hay không:
   - Lượt không model: `python3 -I skills/content-quality-lab/scripts/quality.py rewrite --pairs pairs.jsonl --facts facts.json --entity "ACM=Acme SEO|ACM" --out-dir <W>/rewrite`. Thêm `--own-site` khi site là site của chính đơn vị vận hành. Có cờ: lệnh ra `rw_jev_in.jsonl`, chỉ gồm chữ trang cũ, chữ trang mới và URL.
   - Site khách (không có `--own-site`): `rw_jev_in.jsonl` rỗng và lệnh dừng khi ghép `--jev-out`. Lệnh chỉ chạy code, cụm cấm và Gemma trên máy. Claude đọc mọi cặp, và báo cáo ghi rõ "không gửi Jev". Bỏ bước Jev bên dưới.
   - Jev (chỉ site của chính đơn vị vận hành): `python3 -I tools/ai-assist/jev.py --task skills/content-quality-lab/tasks/rewrite-keep.json --in <W>/rewrite/rw_jev_in.jsonl --out <W>/rewrite/rw_jev_out.jsonl --budget 0.1`. 90 cặp tốn 0,003 USD.
   - Lượt đủ: `<venv>/bin/python -I skills/content-quality-lab/scripts/quality.py rewrite --pairs pairs.jsonl --own-site --facts facts.json --entity ... --jev-out <W>/rewrite/rw_jev_out.jsonl --registry 00-client-context/model-calibration.json --site <domain> --embed --pages pages.jsonl --gsc page_query.tsv --out-dir <W>/rewrite`. Site khách: bỏ `--own-site` và `--jev-out`.
   - Dữ liệu GSC chỉ đi vào Gemma chạy trên máy. Không đưa query GSC vào `pairs.jsonl` hay input Jev.
   - Site mới hoặc rubric đổi version: gán gold mù cho `facts` và `added` trước lượt Jev đầu, rồi chạy `calibrate.py cosine` trên P(dropped) + P(changed) để lấy `reject_below`, và `calibrate.py jev --question added --positive yes`.
   - Claude đọc mọi cặp "chặn" và "cần đọc", rồi mọi query "query cần đọc". Cặp "chặn" không đăng. Số mới chạy thêm lệnh `claims` trên bản mới.
9. Gate AI + spam (bài làm bằng AI hoặc theo template, trước khi đăng): đọc `references/gate-ai-spam.md`. Chấm 8 check AI01–04, CP01, CP04, CP07, CP09 bằng kết quả bước 2, 5, 6 và bản ghi duyệt. Ghi verdict G-AI-SPAM vào `<W>/report.md`.

## Đọc số cho đúng

Pilot 19/10/2026: 167 trang công khai trong 30 pool truy vấn GEO ngành agency SEO, 27 pool có cả trang được trích và không được trích.

| Dấu hiệu | AUC được trích | Khử độ dài bài |
|---|---|---|
| Jev `original_data` | 0,73 [0,65; 0,81] | 0,71 [0,62; 0,79] |
| Jev `first_hand` | 0,71 [0,63; 0,79] | 0,70 [0,61; 0,77] |
| Jev `effort` (score) | 0,66 [0,58; 0,75] | 0,63 [0,55; 0,71] |
| Jev `named_sources` | 0,62 [0,55; 0,69] | 0,60 [0,51; 0,69] |
| Độ dài bài | 0,64 | — |
| Cosine passage với truy vấn | 0,60 | — |
| Độ mới passage so với pool (information gain bằng embedding) | 0,52–0,55, CI chứa 0,5 | — |

- Độ đúng nhãn trên 104 trang gold: `original_data` 91%, đạt 95,5% ở cổng 0,75 (phủ 85%). `first_hand` 87%, đạt 98% ở cổng 0,85 (phủ 59%).
- Jev dao động giữa các lượt chạy. Cùng một câu hỏi, 2 lượt cho độ đúng 75% và 81% trên cùng holdout. Luôn đọc theo cổng, không đọc nhãn thô.
- Định nghĩa gold:
  - `original_data` = yes khi trang có số đo từ dự án, phép thử hoặc khảo sát của chính bên đăng. Số đếm quy mô ("550+ dự án"), bảng giá, khoảng cam kết, số trích của bên khác và kết quả gán cho công ty khác đều là no.
  - `first_hand` = yes khi tác giả hoặc công ty kể việc tự làm và điều đã xảy ra. Mô tả quy trình dịch vụ ở thì tương lai, ý kiến về đơn vị khác và lời chứng thực của khách đều là no.
- Trong pool BOFU ("công ty SEO nào uy tín"), trang được trích chủ yếu là listicle, ít dữ liệu gốc. So trang của mình với chính pool đó, không so với một chuẩn chung.
- Khối chữ lặp: ngưỡng 0,96 đạt precision 100% trên 64 cặp gold. Trên toàn site, tỷ lệ lặp tương quan với hiển thị. Phần này do case study vừa lặp khối mẫu vừa không có hiển thị. Trên trang nội dung, rho là −0,03. Không báo tỷ lệ lặp như yếu tố xếp hạng.
- Claims: cổng và độ đúng từng câu hỏi ở `references/claims.md` mục 5. Cổng `self_superlative`, `unsourced_stat` và cổng chọn fact của `fact-match` đang là bản nháp.
- Rewrite, pilot site mẫu 19/10/2026: 90 cặp chữ của 4 vòng viết lại trang tiền, gold mù dev 50 và holdout 40.
  - Jev `facts`: Claude đọc khi Jev chọn dropped/changed hoặc P(dropped) + P(changed) ≥ 0,72 (ngưỡng chọn trên dev). Holdout: bắt 9/9 cặp mất hay đổi fact, bỏ qua 19 cặp không sót. Precision chỉ 9/21: Jev hay coi việc bỏ "hàng đầu Việt Nam" là mất fact, nên không tự chốt.
  - Jev `added`: p_yes ≤ 0,15 là no (18/18 trên 2 tập). p_yes ≥ 0,85 là yes nhưng holdout chỉ đúng 14/17, nên cặp yes vẫn Claude đọc, trừ khi câu mới chứa đúng cách viết của bảng fact.
  - Cả lượt: Claude đọc 55/90 cặp; 18/19 cặp mất hay đổi fact nằm trong số đó. Cặp sót là câu trích dẫn của người khác bị sửa chữ (P 0,53).
  - Cosine cũ ↔ mới thấp hơn ở cặp mất fact (AUC 0,74), nhưng skill chỉ dùng số này để mô tả.
  - Kiểm query: 150 query mang click ở 12 trang. Không lượt viết lại nào làm cosine của query giảm. Thử xoá passage khớp nhất của từng query: 150/150 query giảm, trung vị chỉ −0,014, vì trang có passage khác gần như cùng nghĩa. Vì vậy luật là "passage khớp nhất bị sửa và cosine giảm" thì Claude đọc; ngưỡng `rewrite-query-drop` chưa có gold dương thật.

## Năng lực model đã xét

| Năng lực | Việc | Quyết định |
|---|---|---|
| Jev `noul` | original_data, first_hand, named_sources | dùng 2 câu đầu có cổng; named_sources chưa có gold |
| Jev `noul` | guarantee, self_superlative, unsourced_stat (claims) | dùng có cổng; regex đơn lẻ báo sai 19/21 câu so sánh nhất |
| Jev `score` 4 mức | effort tổng | dùng làm tham khảo (AUC 0,66), chưa có gold dạng số |
| Jev `choice` | chủ thể câu (`subject`), fact cùng chỉ số (`fact-match`) | dùng có cổng; dấu hiệu effort là có hoặc không nên không cần choice |
| Jev ảnh | ảnh chụp màn hình case study | để `visual-serp-lab`: dữ liệu gốc thường nằm trong ảnh biểu đồ |
| EmbeddingGemma `Document`, cosine passage–passage | khối chữ lặp | dùng, ngưỡng 0,96 |
| EmbeddingGemma `SentenceSimilarity` câu–fact | lấy fact ứng viên cho câu có số | dùng, sàn 0,82; `FactChecking` và `SearchQuery` tách kém hơn trên 58 câu gold |
| EmbeddingGemma độ mới so với pool | information gain | bỏ: AUC 0,52–0,55 sau khi loại trang cùng domain |
| EmbeddingGemma độ phủ ý chung của pool | consensus coverage | bỏ: AUC 0,49–0,54 |
| Jev `choice` + `noul` | bản viết lại bỏ, đổi hay thêm fact (`rewrite-keep`) | dùng làm cổng lọc: bắt đủ cặp mất fact trên holdout, precision thấp |
| EmbeddingGemma `SearchQuery` ↔ `Document` | query GSC mang click còn passage trả lời sau khi viết lại | dùng, chạy local; chưa có ngưỡng giảm, dùng luật passage khớp nhất bị sửa |
| EmbeddingGemma `SentenceSimilarity` cũ ↔ mới | mức đổi chữ | chỉ mô tả: AUC 0,74 với mất fact, không đủ để quyết |
| GLM Flash trích câu | dẫn chứng cho nhãn | chưa dùng; Claude đọc trang review trực tiếp |

## Output

- `<W>` = `03-audits/content/<CLIENT>_content-quality_<YYYY-MM-DD>/`: `jev_in.jsonl`, `jev_out.jsonl`, `pages.jsonl`, `report.md`, `auc_rows.jsonl`, `template/`.
- `<W>/rewrite/`: `rewrite.tsv` (cột `decision, url, id, why, p_loss, drift, old, new`), `rewrite.jsonl`, `queries.tsv`, `queries.jsonl`, `report.md`, `rw_jev_in.jsonl`, `rw_jev_out.jsonl`.
- `<W>/claims/`: `claims.tsv` (cột `cau, url, so_trang, lop, nhan, p, fact, de_xuat, ghi_chu`), `claims.jsonl`, `report.md`, cùng input và output model (`jev_in/out`, `fact_q`, `fact_d`, `fact_nn`, `fact_jev_in/out`).
- Gold và kết quả hiệu chuẩn: `<W>/calibration/`. Entry registry ở `00-client-context/model-calibration.json`.

## Trước khi trình

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:

1. Bảng fact là bản mới nhất từ wiki, và cụm cấm có quy tắc theo thời gian đã nằm trong `banned`. Lỗi đã gặp: bảng fact 19/10 thiếu "10+ năm", nên 6 câu P0 về số năm ra "giữ".
2. Mọi dòng "người đọc" đã có kết luận của Claude, câu lặp nhiều trang được đọc một lần. Lỗi đã gặp: dòng dưới cổng vẫn chứa câu cam kết thật (dev 4/27).
3. Câu cam kết, hoàn phí, bảo hành chỉ ghi điểm lệch và nguồn đối chiếu. Lỗi đã gặp: 3 phiên bản câu hoàn phí trên cùng site, không bản nào khớp hợp đồng mẫu.
4. Câu nêu thương hiệu khác với fact gần nhất không bị "sửa theo fact". Lỗi đã gặp: số học viên của công ty thứ hai bị so với fact của công ty chính.
5. Câu phủ định, lời khuyên chung, thương hiệu khách và số có nguồn không nằm trong danh sách xoá. Lỗi đã gặp: audit đếm thô cụm cấm, tính cả "Số 128" trong địa chỉ và "đặt lợi ích khách hàng lên hàng đầu".
6. Cổng đọc từ registry của site; cổng "bản nháp" được ghi trong báo cáo. Lỗi đã gặp: cổng dev của `self_superlative` và `unsourced_stat` trượt holdout mới.
7. Câu số liệu công ty ra "giữ" đã được soát lại theo bảng fact. Lỗi đã gặp: "80 Chuyên gia SEO" không có fact nhân sự trong 5 ứng viên của Gemma.
8. Bản viết lại đã qua lệnh `rewrite`: mọi cặp "chặn", "cần đọc" và mọi "query cần đọc" có kết luận của Claude. Lỗi đã gặp: 4 vòng viết lại trang tiền đổi 18 fact (số năm, giá, số nhân viên, câu trích dẫn của chuyên gia). QA chữ chỉ chấm chữ mới, nên không ai đối chiếu fact cũ với fact mới.

## Gate

- [ ] Jev chỉ nhận chữ công khai của trang web, hoặc bản nháp chưa đăng của site của chính đơn vị vận hành (`claims --text` và `rewrite` có `--own-site`). Không gửi GSC, hợp đồng, email.
- [ ] Bản nháp chưa đăng của site khách không gửi Jev: chạy `claims --text` và `rewrite` không có `--own-site`. Lượt đó chỉ dùng regex, cụm cấm và Gemma trên máy. Claude đọc mọi câu và mọi cặp chạm dấu hiệu.
- [ ] Cổng lấy từ registry của site, hoặc báo cáo ghi rõ "bản nháp, cổng defaults".
- [ ] Mọi trang "review", mọi cặp trùng chứa lời chứng thực hay số liệu, và mọi dòng "người đọc" đã có Claude đọc.
- [ ] Báo cáo khách ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
- [ ] Không đề xuất bịa số liệu hay case. Thiếu số đo thì xin số từ dự án thật qua `expert-case-study`.
- [ ] Không viết câu cam kết hoàn tiền, bảo đảm KPI hay thứ hạng mới. Chủ site quyết câu cam kết.
- [ ] Lệnh rewrite: query GSC chỉ xử lý trên máy. `rw_jev_in.jsonl` chỉ có chữ trang và URL, và rỗng khi không có `--own-site`.
- [ ] Gate AI + spam: mỗi check có trạng thái và bằng chứng; không ghi Does not meet chỉ vì trang dùng AI, template hay số lượng lớn; AI03 không có bản ghi duyệt thì ghi CANNOT-VERIFY.

## Anti-patterns

- Dùng nhãn Jev thô không qua cổng → độ đúng dao động giữa các lượt.
- Viết thêm điều kiện vào câu hỏi Jev để sửa ca lệch → v3 dài hơn làm `original_data` tụt từ 93% xuống 83% trên 104 mẫu. Sửa câu hỏi thì đo lại trên holdout mới.
- Đo information gain bằng độ khác embedding → pilot không có tín hiệu với trích dẫn AI.
- Xoá khối chữ lặp hàng loạt → CTA, form và bảng giá lặp là bình thường. Chỉ sửa khối nằm sai mục hoặc lệch thông tin.
- Đếm thô cụm cấm rồi đề xuất xoá → phần lớn "tốt nhất", "hàng đầu" là lời khuyên hoặc nói về bên khác. Dùng nhãn `self_superlative` và `subject` qua cổng.
- Bỏ qua dòng "Jev dưới cổng" vì danh sách dài → câu dưới cổng chứa 10–20% câu cam kết thật. Gom câu lặp rồi đọc hết.
- Sửa số của thương hiệu B theo fact của thương hiệu A → khai đủ `--entity` cho mọi thương hiệu có fact riêng.
- Coi bản viết lại là an toàn vì cosine cũ ↔ mới cao → cặp mất fact vẫn có cosine 0,85–0,97.
- Coi số mới là đúng vì số đó có trong bảng fact → pilot: năm "2022" khớp fact về khoá học, nhưng câu mới dùng năm đó cho một dịch vụ khác. Lệnh rewrite chỉ nhận số khi câu chứa đúng cách viết canon hoặc allowed.
- Gửi query GSC cho Jev để hỏi bản mới còn trả lời query không → dùng Gemma chạy trên máy.

## Changelog

- v1.3.0 (2026-11-02): bước 9 gate AI + spam (AI01–04, CP01, CP04, CP07, CP09 của checklist Aleyda Solis), `references/gate-ai-spam.md`. Gate dùng tín hiệu sẵn có của skill, chưa thêm rubric Jev; rubric cấp site nằm ở `eeat-site-qc`.
- v1.2.3 (2026-10-19): cờ `--own-site` cho `rewrite` và `claims --text`. Bản nháp chưa đăng của site của chính đơn vị vận hành được gửi Jev. Bản nháp site khách không gửi Jev: input Jev rỗng, ghép `--jev-out` thì dừng, Claude đọc, chỉ chạy regex, cụm cấm và Gemma trên máy.
- v1.2.2 (2026-10-19): rút description còn 273 ký tự.
- v1.2.1 (2026-10-19): `claims --text` (chữ nháp chưa công khai) không gửi Jev: `jev_in.jsonl` và `fact_jev_in.jsonl` rỗng, ghép `--jev-out` thì dừng, câu chạm dấu hiệu chuyển Claude đọc. Cụm cấm của bảng fact dùng `strict_rx`: cụm sau dấu gạch nối không tính.
- v1.2 (2026-10-19): thêm lệnh `rewrite` (kiểm an toàn khi viết lại) và rubric `tasks/rewrite-keep.json` 2026-10-19.1. Hiệu chuẩn gold mù 90 cặp chữ (dev 50, holdout 40) của 4 vòng viết lại trang tiền site mẫu; thử độ nhạy kiểm query bằng cách xoá passage khớp nhất. Test offline `tests/test_rewrite.py`. Bước 0 đặt danh sách id trong nháy đơn.

- v1.1 (2026-10-19): thêm lệnh `claims` (regex lớp 1, Jev `claim-guard` 2026-10-19.2, cụm cấm của bảng fact, Gemma + Jev `fact-match` 2026-10-19.2), `references/claims.md`, `tests/test_claims.py`. Hiệu chuẩn trên site mẫu: gold dev 167 câu, holdout 60 câu, holdout h4 60 câu claim và 50 câu fact; gold fact 58 câu × 20 fact. Câu chạm regex lớp 1 luôn gửi Jev. Regex "số 1", "#1", "top 1" nhận dấu chấm cuối câu. `--pages` chỉ lấy trang có trong rows. Thêm Bước 0, phân việc model, tự phản biện.
- v1.0 (2026-10-19): tạo mới từ pilot site mẫu: rubric `content-effort` 2026-10-19.4 qua 4 vòng (v3 bỏ), gold 104 trang, 64 cặp passage gold. Chế độ `auc` mới ở `model-calibration`. Test offline `tests/test_quality.py`.
