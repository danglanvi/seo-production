---
name: geo-answer-lab
description: "Thu câu trả lời AI (ChatGPT, Gemini, Perplexity) cho bộ prompt GEO, đo brand được nhắc, được gợi ý, vị trí, bằng chứng và phản đối bằng regex + Jev + GLM Flash, và kiểm mô tả entity lệch giữa các nguồn. Dùng cho mốc GEO, báo cáo AI visibility và tìm việc sửa trang."
metadata:
  version: "1.1.1"
---

# geo-answer-lab — đọc câu trả lời AI như người mua đọc

Đếm mention chỉ cho biết brand có mặt. Người mua đọc thêm 3 thứ: AI có gợi ý brand không, AI dựa vào bằng chứng gì, và AI bảo họ phải kiểm gì trước khi ký. Skill này đo cả 3 thứ, theo 5 lớp: code tất định → Jev → GLM Flash trích câu → Claude đọc phần dưới cổng → người vận hành quyết việc sửa.

Gốc đường dẫn là root repo. Script ở `skills/geo-answer-lab/scripts/`, rubric ở `skills/geo-answer-lab/tasks/`, Jev và GLM ở `tools/ai-assist/`. Ở workspace gốc chứa repo này, Jev và GLM nằm ở `SEO Production/tools/ai-assist/`.

## Khi nào dùng

- Mốc GEO đầu dự án (#21), giữa kỳ, cuối kỳ (bảng C `index.md`).
- Báo cáo AI visibility cho khách, hoặc so brand với đối thủ trên AI.
- Tìm việc sửa trang: câu AI nghi ngờ, câu hỏi AI bảo người mua phải hỏi.
- Chọn prompt thì dùng `geo-tracking-prompt-selection` trước. Skill này nhận bộ prompt đã chốt.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| `prompts.tsv` (id, funnel, branded, topic, prompt) | `geo-tracking-prompt-selection` | dừng, chọn prompt trước |
| `brands.json`: brand chính, domain, đối thủ, regex chữ thường, alias | `00-client-context/`, danh sách đối thủ | hỏi người vận hành |
| `OPENROUTER_API_KEY`, `OPENROUTER_JEV_API_KEY` | `.agent-secrets/.env` | dừng |
| Cổng confidence của rubric | registry `00-client-context/model-calibration.json` | dùng defaults, ghi "bản nháp"; hiệu chuẩn ở bước 5 |
| Nhất quán mô tả entity: `sources.tsv` (url, kind), `canon.txt`, `facts.json` | danh sách nguồn ngoài, mô tả chính thức người vận hành duyệt, bảng fact của skill `site-fact-consistency` | thiếu `canon.txt` hoặc `facts.json` thì dừng phần này, hỏi người vận hành |

## Phân việc model

| Lớp | Việc trong skill | Quyết định |
|---|---|---|
| Code | Regex mention, vị trí nhắc, citation, gom đoạn mô tả brand, tìm số và năm, so số với `facts.json`, tìm cụm cấm | Dùng. Mọi phép so số là luật tất định |
| Jev | `ai-answer-brand` (role, proof, objection); `entity-desc` (mô tả lệch định vị); `company-fact-claim` (số thuộc brand hay người sáng lập, loại số) | Dùng. Jev chỉ nhận chữ công khai |
| GLM Flash | Trích nguyên văn câu phản đối | Dùng, cho cặp có `objection` p > 0,3 |
| EmbeddingGemma | Cosine đoạn mô tả với `canon.txt`, xếp nguồn | Dùng để xếp nguồn. Không dùng để bắt mô tả lệch: pilot site mẫu, AUC 0,36 (đoạn lệch vẫn nói về SEO nên cosine cao) |
| Claude | Đọc mục "review", câu phản đối, đoạn "mô tả cần đọc"; gom việc sửa | Dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,openrouter,jev,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. Thu câu trả lời: `python3 -I scripts/collect.py --prompts prompts.tsv --out <W>/raw.jsonl --runs 3`. Mỗi lượt khoảng 0,01–0,03 USD. Chạy lại lệnh thì script bỏ qua lượt đã có.
2. Lớp tất định: `python3 -I scripts/prepare.py --raw <W>/raw.jsonl --prompts prompts.tsv --brands brands.json --out-dir <W>`.
   - Script ra `det.jsonl` với regex mention, vị trí nhắc và cờ brand có trong câu hỏi.
   - Script ra `citations.jsonl`. Link vertexaisearch của Gemini lấy domain từ title.
   - Script ra `jev_in.jsonl` chỉ gồm cặp regex thấy brand. Pilot 19/10 đo regex khớp Jev ở 1.080/1.080 cặp, nên Jev không chấm cặp vắng mặt.
3. Jev gán nhãn: `python3 -I tools/ai-assist/jev.py --task skills/geo-answer-lab/tasks/ai-answer-brand.json --in <W>/jev_in.jsonl --out <W>/jev_out.jsonl --budget 0.2`. Rubric có 3 câu hỏi:
   - `role`: recommended, subject, source_only, mentioned_other.
   - `proof`: third_party, named_results, self_description, none.
   - `objection`: yes/no.
   Vị trí trong danh sách đã có từ code, nên Jev không chấm top_pick.
4. GLM trích câu phản đối cho cặp có `objection` p > 0,3:
   - Chọn cặp: `python3 -I scripts/prepare.py --raw <W>/raw.jsonl --prompts prompts.tsv --brands brands.json --out-dir <W> --jev-out <W>/jev_out.jsonl`.
   - Trích: `python3 -I tools/ai-assist/glm.py --task skills/geo-answer-lab/tasks/ai-answer-objection-extract.json --in <W>/glm_in.jsonl --out <W>/glm_out.jsonl`. Script bỏ mọi câu không có nguyên văn trong câu trả lời.
5. Site mới, ngành mới hoặc rubric đổi version: gán gold 40–50 cặp có mặt trước khi xem nhãn Jev, lấy đều 3 engine và cả prompt mang tên brand. Chạy skill `model-calibration` chế độ `jev` cho từng câu hỏi, rồi ghi registry của site.
6. Báo cáo: `python3 -I scripts/report.py --dir <W> --brands brands.json --registry 00-client-context/model-calibration.json --site <domain>`. Script ra `report.json` và `report.md` theo brand × engine. Nhãn dưới cổng ghi "review".
7. Claude đọc mục "review" và toàn bộ câu phản đối của brand chính. Gom câu phản đối thành việc sửa trang:
   - proof_doubt → bằng chứng bên thứ ba. Nghi ngờ vì brand tự xếp hạng hoặc tự công bố bằng chứng không phải lỗi lớn. Không đề xuất gỡ bài. Đề xuất đợt offsite consensus bằng `geo-offsite-audit`, và rà bài top list của site theo GE-26: khách quan, có EEAT.
   - scope_question → bảng phạm vi trên trang dịch vụ.
   - price_question → fact giá thống nhất.
   - Câu sai sự thật → skill `site-fact-consistency`.

## Nhất quán mô tả entity

Phần này tìm nơi mô tả brand khác mô tả chính thức, rồi chuyển việc sửa về đúng nguồn. AI thường lặp lại mô tả cũ từ top list, directory và chính trang giới thiệu của brand. `<E>` = `<W>/entity/`.

1. Soạn `<E>/canon.txt`: 2–4 câu nói brand là gì và các dịch vụ chính. Lấy từ trang chủ và trang dịch vụ hiện hành. Người vận hành duyệt file này.
2. Gom đoạn mô tả: `python3 -I skills/geo-answer-lab/scripts/entity_desc.py collect --sources sources.tsv --brands brands.json --raw <W>/raw.jsonl --paste-dir <E>/paste --save-dir <E>/html --out <E>/passages.jsonl`
   - Script chỉ GET trang công khai. Với trang cần đăng nhập (LinkedIn, Google Business Profile), dán chữ vào `<E>/paste/<kind>__<tên>.txt`. Dòng đầu file là URL.
   - Script lấy meta description, JSON-LD, mục dưới heading có tên brand và khối có nhắc brand. Script bỏ nav, footer, form.
   - Nếu một nguồn trả 0 đoạn hoặc báo lỗi, đọc `<E>/sources_log.jsonl`.
3. Chuẩn bị input Jev: `entity_desc.py prepare --passages <E>/passages.jsonl --brands brands.json --canon <E>/canon.txt --out-dir <E>`.
4. Chạy Jev cho 2 rubric:
   - `python3 -I tools/ai-assist/jev.py --task skills/geo-answer-lab/tasks/entity-desc.json --in <E>/services_in.jsonl --out <E>/services_out.jsonl --budget 0.3`
   - `python3 -I tools/ai-assist/jev.py --task skills/geo-answer-lab/tasks/company-fact-claim.json --in <E>/claims_in.jsonl --out <E>/claims_out.jsonl --budget 0.15`
   - Pilot site mẫu: 472 đoạn và 89 số tốn 0,024 USD.
5. Gemma (tuỳ chọn): `<venv>/bin/python -I skills/geo-answer-lab/scripts/entity_desc.py embed --passages <E>/passages.jsonl --canon <E>/canon.txt --out <E>/cos.jsonl`. Nếu máy không có Gemma, bỏ bước này. Report vẫn chạy, chỉ thiếu cột cosine.
6. Nếu site mới, ngành mới hoặc rubric đổi version, hiệu chuẩn `entity-desc` trước khi tin cổng:
   - Gán gold mù trước lượt Jev đầu: `entity_desc.py gold-sheet --passages <E>/passages.jsonl --n 60 --seed 19 --out <E>/calibration/sheet_dev.jsonl`.
   - Lấy holdout bằng `--skip` các id đã gán, seed khác, và `--enrich '<regex nhãn định vị cũ>'` để có đủ đoạn lệch.
   - Ghi sha256 và giờ gán vào `<E>/calibration/gold_log.md` trước khi chạy Jev.
   - Chạy `model-calibration` chế độ `jev` (`--question services --positive different`). Chạy thêm chế độ `cosine` trên P(different) để lấy `reject_below`.
7. Báo cáo: `entity_desc.py report --passages <E>/passages.jsonl --facts facts.json --dir <E> --registry 00-client-context/model-calibration.json --site <domain> --entity <chủ thể công ty trong facts.json> [--founder <chủ thể người sáng lập>]`. Script ra `issues.tsv`, `summary.json`, `entity_report.md`.
   - Code so số với `facts.json` và gắn các loại lỗi: lệch năm, lệch hoặc cũ, nói quá, cách viết cấm (cụm `banned` trong `facts.json`).
   - Cổng `entity-desc`: nếu P(different) dưới `reject_below` và Jev không chọn different, script bỏ qua đoạn đó. Script chỉ ghi "mô tả dịch vụ lệch" khi registry có `threshold` tự chốt. Nếu chưa có entry, Claude đọc mọi đoạn có mô tả.
   - Số có Jev dưới cổng ghi "số cần đọc".
8. Claude đọc "mô tả cần đọc" theo thứ tự P(lệch) giảm dần, rồi đọc "số cần đọc". Gom việc sửa:
   - Lỗi trên site của brand: skill `site-fact-consistency` sửa theo `facts.json`. Sửa trang của brand trước, vì AI trích trang này.
   - Lỗi ở nguồn ngoài (báo, directory, top list, hồ sơ): ghi vào danh sách xin sửa của `geo-offsite-audit`.
   - Lỗi trong câu trả lời AI: tìm trang AI trích trong `citations.jsonl` theo id câu trả lời, rồi sửa trang đó.
   - Nếu trang của brand ghi định vị khác `canon.txt`, người vận hành quyết sửa trang hay sửa `canon.txt`. Claude không tự chọn.

Hiệu chuẩn trên pilot site mẫu 19/10/2026 (rubric `entity-desc` 2026-10-19.2):

- Bản .1 bắt 1/5 đoạn lệch của dev. Câu "nêu ít dịch vụ hơn vẫn khớp" kéo đoạn có cả SEO lẫn nhãn định vị cũ về consistent. Bản .2 sửa câu này.
- Bản .2 trên 100 gold đã xem: đoạn lệch có P(different) từ 0,84, đoạn không lệch tối đa 0,76. Ngưỡng lọc chọn là 0,8.
- Holdout2 mù 40 đoạn: luật "Jev chọn different hoặc P ≥ 0,8" bắt 5/5 đoạn lệch và bỏ qua 33 đoạn, không sót đoạn lệch nào. Riêng điều kiện P ≥ 0,8 bắt 4/5.
- Precision trên holdout2 là 5/7, nên skill chưa tự chốt "mô tả dịch vụ lệch". Claude đọc 48/472 đoạn thay cho 318 đoạn có mô tả.
- `company-fact-claim` dùng cổng 17/10 (subject 0,5, metric 0,83), hiệu chuẩn trên trang của site. Pilot ra 23 số lệch, và Claude đọc thấy 23/23 số nói về brand. Cổng này chưa hiệu chuẩn riêng cho top list và câu trả lời AI.

## Đọc số cho đúng

- Tỷ lệ chỉ tính prompt không nêu tên brand đó. Prompt mang tên brand đo bằng proof và objection, không đo bằng "được gợi ý".
- So engine với chính nó qua các mốc. Không so tỷ lệ phản đối giữa engine: ChatGPT gieo câu hỏi thẩm định cho mọi agency (pilot site mẫu: 68–80% cho cả 3 brand), Gemini gần như không.
- `answers_citing_own_domain` đếm câu trả lời có trích domain của brand chính, kể cả trích để cảnh báo.

## Output

- `<W>` = `08-geo-ai-visibility/<CLIENT>_geo-answer_<YYYY-MM-DD>/`: `raw.jsonl`, `det.jsonl`, `citations.jsonl`, `jev_out.jsonl`, `glm_out.jsonl`, `report.json`, `report.md`.
- Gold và kết quả hiệu chuẩn: `<W>/calibration/`. Entry registry ở `00-client-context/model-calibration.json`.
- Báo cáo khách lấy bảng và danh sách việc sửa từ `report.md`. Kèm câu: "số liệu là ảnh chụp ngày <ngày>, câu trả lời AI đổi theo lần chạy".
- Nhất quán mô tả entity: `<W>/entity/` gồm `canon.txt`, `passages.jsonl`, `sources_log.jsonl`, `services_out.jsonl`, `claims_out.jsonl`, `cos.jsonl`, `issues.tsv`, `summary.json`, `entity_report.md`. Gold ở `<W>/entity/calibration/`.

## Gate

- [ ] Mỗi engine × prompt có ≥ 3 lần chạy và ghi ngày, model.
- [ ] Cổng confidence lấy từ registry của site, hoặc báo cáo ghi rõ "bản nháp, cổng defaults".
- [ ] Jev chỉ nhận nội dung công khai: câu hỏi, câu trả lời AI, tên brand. Không gửi GSC, hợp đồng, email.
- [ ] Mọi câu phản đối trong báo cáo có nguyên văn trong `raw.jsonl` và có id câu trả lời.
- [ ] Không biến câu AI nói về cam kết, hoàn phí, bảo hành thành claim trên trang. Câu đó là việc cần người vận hành kiểm.
- [ ] Nhất quán mô tả entity: `canon.txt` có người vận hành duyệt. Cổng `entity-desc` lấy từ registry, hoặc Claude đọc mọi đoạn có mô tả.
- [ ] Mỗi lỗi mô tả hay số trong báo cáo có URL hoặc id câu trả lời, kèm đoạn nguyên văn.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Tỷ lệ "được gợi ý" chỉ tính prompt không nêu tên brand. Nguồn lỗi: prompt mang tên brand luôn nhắc brand, nên làm tỷ lệ tăng giả.
- [ ] Không so tỷ lệ phản đối giữa engine. Nguồn lỗi: pilot site mẫu, ChatGPT gieo câu hỏi thẩm định cho 68–80% agency, Gemini gần như không.
- [ ] `sources.tsv` có trang chủ, trang giới thiệu và bản tiếng Anh của brand. Nguồn lỗi: pilot 19/10, AI lặp nhãn định vị cũ có trong meta description trang giới thiệu tiếng Anh của brand.
- [ ] `canon.txt` khớp các dịch vụ trang chủ đang bán. Nguồn lỗi: pilot 19/10, trang chủ liệt kê thêm dịch vụ ngoài `canon.txt`, nên Jev gắn "lệch" cho chính trang chủ.
- [ ] Claude đã đọc từng đoạn "mô tả cần đọc" và ghi kết luận. Nguồn lỗi: precision của Jev là 5/7 trên holdout2.
- [ ] Không kết luận mô tả lệch từ cosine Gemma. Nguồn lỗi: pilot 19/10, AUC 0,36, đoạn lệch có cosine cao hơn đoạn khớp.
- [ ] Lỗi trong câu trả lời AI có kèm trang mà AI trích. Nguồn lỗi: báo cáo cũ chỉ nêu câu AI sai, không nêu trang gốc cần sửa.
- [ ] Số cũ ở top list ghi là "cũ", kèm ngày đăng nếu có. Nguồn lỗi: pilot 19/10, "7 năm", "400 dự án" là số đúng tại ngày đăng bài.

## Anti-patterns

- Đề xuất gỡ bài top list vì AI nghi ngờ brand tự xếp hạng → giữ bài, viết khách quan + EEAT, tăng consensus bên ngoài (luật GE-26, chốt 19/10/2026).
- Gọi Jev cho mọi cặp brand × câu trả lời → regex lọc vắng mặt trước.
- Dùng sentiment 5 lớp → pilot đo đúng 64% trên 50 mẫu; rubric v3 thay bằng objection yes/no.
- Hỏi Jev top_pick hay shortlisted → vị trí lấy từ `mention_order`.
- Đưa câu GLM trích vào báo cáo mà không đọc → GLM bắt dư ở dải xám: pilot recall 15/15, precision 15/22.
- Bỏ qua đoạn mô tả theo nhãn `choice` của `entity-desc` → dùng cổng `reject_below` trên P(different), cộng nhãn different.
- Bắt mô tả lệch bằng cosine Gemma → đoạn lệch vẫn nói về SEO, nên cosine cao (AUC 0,36).
- Xin nguồn ngoài sửa trước khi sửa trang của brand → AI và top list chép mô tả từ trang của brand.

## Changelog

- v1.1.1 (2026-10-19): rút description còn 265 ký tự.
- v1.1 (2026-10-19): thêm phần Nhất quán mô tả entity: `scripts/entity_desc.py` (collect, prepare, gold-sheet, embed, report), rubric `tasks/entity-desc.json` bản 2026-10-19.2, chép `tasks/company-fact-claim.json` để skill tự chứa. Hiệu chuẩn gold mù 140 đoạn (dev 60, holdout 40, holdout2 40). Report đọc `facts.json` theo schema của `site-fact-consistency`. Thêm Bước 0 kiểm tool, bảng Phân việc model, Tự phản biện. Test offline `tests/test_entity_desc.py`.

- v1.0 (2026-10-19): tạo mới từ pilot site mẫu 18–19/10: 270 câu trả lời × 4 brand. Rubric v3 qua 3 vòng gold 50 mẫu: role 96%, proof 94%, objection 96% ở cổng 0,7.
