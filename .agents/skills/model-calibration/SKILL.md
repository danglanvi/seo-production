---
name: model-calibration
description: "Hiệu chuẩn ngưỡng nhãn Jev, cosine EmbeddingGemma và chuỗi nhiều bước trên gold gán mù, kiểm proxy với kết quả thật (GSC, AI trích dẫn), rồi ghi registry theo site. Dùng trước khi tin một ngưỡng ở site, ngành, version rubric hoặc model mới."
metadata:
  version: "1.4"
---

# model-calibration — ngưỡng có bằng chứng, proxy có kiểm chứng

Jev trả xác suất, EmbeddingGemma trả cosine. Cả hai chưa có ngưỡng dùng chung, vì ngưỡng đổi theo site, ngành, tiếng Việt, version rubric và cặp prompt. Skill này biến mẫu gán tay thành ngưỡng ghi trong registry. Skill cũng chặn mọi chỉ số proxy chưa tương quan với kết quả thật khỏi báo cáo khách. Ngưỡng chỉ thành cổng khi ngưỡng giữ được trên holdout mù.

Gốc đường dẫn là root repo. Script: `skills/model-calibration/scripts/calibrate.py`, chạy bằng Python có numpy. Reference: `references/phieu-gold-va-holdout.md` (phiếu gold, holdout, entry draft).

## Khi nào dùng

- Lần đầu chạy một rubric Jev hoặc một ngưỡng cosine trên site hay ngành mới.
- Jev ra bản mới, rubric đổi version, hoặc đổi cặp prompt embedding.
- Trước khi đưa một chỉ số mô phỏng vào báo cáo khách, ví dụ điểm tập trung chủ đề, điểm truy xuất passage hay information gain.
- Trước khi báo một chuỗi nhiều bước (Jev lọc rồi GLM trích) là đã lọc xong.
- Không dùng khi việc đã có luật tất định (regex, mã HTTP, checksum).

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Output model | `jev.py` (`tools/ai-assist/`) hoặc `svi.py` | chạy model trên mẫu trước |
| Gold gán tay | Phiếu `gold-sheet`, người hoặc Claude gán mù. Tối thiểu 40 mẫu, có cả dương lẫn âm | dựng phiếu rồi gán; không lấy nhãn của chính model làm gold |
| Holdout (để entry thành cổng) | Phiếu thứ hai, ≥ 40 mẫu mới, gán mù | entry ghi `draft`, threshold null; skill đọc dùng defaults hoặc Claude đọc |
| Đầu ra từng bước (chế độ pipeline) | jsonl `{id, <bước>: true\|false}` dựng từ đầu ra Jev, GLM | dựng file trước; không lấy độ đúng của Jev làm recall của chuỗi |
| Kết quả thật (chế độ proxy) | GSC (vị trí, click), câu trả lời AI có trích dẫn, Ahrefs | dừng; chưa kiểm được thì ghi "chưa chứng minh" |
| Site, ngành, version rubric, model | rubric `tasks/*.json`, `00-client-context/` | hỏi |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | Ra nhãn và confidence cần hiệu chuẩn (`tools/ai-assist/jev.py`) | Là đối tượng đo. Không dùng Jev gán gold hay xử ca lệch, vì gold lấy từ model làm ngưỡng tự khớp với chính model. |
| EmbeddingGemma 2 | Ra cosine cần hiệu chuẩn | Là đối tượng đo. Không dùng để gán gold, cùng lý do. |
| GLM Flash | Bước trích trong chuỗi `pipeline` | Là đối tượng đo khi chuỗi có bước GLM. Không dùng để gán gold. |
| Claude | Gán gold mù khi người không gán, đọc ca lệch và vùng xám, chọn chế độ, viết verdict | Dùng. |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,numpy,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

1. Dựng phiếu gold mù bằng `gold-sheet`. Lệnh lấy đều các dải confidence và cộng ca khó đã biết. Phiếu không in nhãn model. Đầu ra Jev cần `--content` để phiếu có nội dung. Chạy thử trước, rồi thêm `--out` và `--write`. Đọc `references/phieu-gold-va-holdout.md` §1–2.
   `python3 -E skills/model-calibration/scripts/calibrate.py gold-sheet --pred <W>/jev_out.jsonl --question <câu hỏi> --content <W>/jev_in.jsonl --n 60 --hard <W>/calibration/hard_ids.txt --out <W>/calibration/<rubric>_phieu-gold.txt --write`
2. Gán gold trên phiếu trước khi xem nhãn model. Ca mơ hồ để trống. Ghép bằng `calibrate.py gold-merge --todo <phiếu> --gold <W>/calibration/gold.jsonl --write`. File `gold.jsonl` có dạng `{"id", "label"}`.
   - Dựng holdout bằng phiếu thứ hai có `--exclude-gold <W>/calibration/gold.jsonl`, rồi ghép vào `holdout.jsonl`. Đọc reference §3–4.
3. Chạy chế độ hợp với việc. Lệnh `jev`, `cosine`, `pipeline` thêm `--holdout <W>/calibration/holdout.jsonl`:
   - **Nhãn Jev:** `calibrate.py jev --pred out.jsonl --gold gold.jsonl --question <tên> --positive <nhãn>`. Script ra độ đúng theo dải confidence. Script chọn ngưỡng thấp nhất có precision ≥ 0,95 (đặt bằng `--target`) và cận dưới Wilson ≥ target − 0,1.
   - **Câu hỏi nhiều lớp:** lớp ít mẫu thường không đạt Wilson. Khi đó dùng `conf_gate` trong kết quả: nhãn có confidence từ cổng trở lên đúng ≥ target, dưới cổng Claude đọc. Câu hỏi yes/no (`noul`) tính confidence là max(p, 1 − p).
   - **Cosine:** `calibrate.py cosine --pairs pairs.jsonl`. Dòng có dạng `{"id", "cos", "label"}`. Script ra ngưỡng nhận, ngưỡng loại và vùng xám để Claude đọc. Điểm ngoài dải 0,50–0,995 (margin, điểm gộp) thì thêm `--grid LO:HI:STEP`, ví dụ `--grid=0.0:1.4:0.02`.
   - **Cosine với gold từ phiếu:** thêm `--gold gold.jsonl`. Script lấy nhãn `1`, `0` từ gold và lấy cos từ `--pairs`. Cặp không có gold bị bỏ.
   - **Chuỗi nhiều bước:** `calibrate.py pipeline --pred rows.jsonl --gold gold.jsonl --positive <nhãn> --stages jev,glm [--min-recall 0.8]`. Dòng có dạng `{"id", "jev": true|false, "glm": true|false}`.
     - Mục được bắt khi mọi bước đều giữ. Bước vắng tính là không giữ. Mục gold vắng trong `rows.jsonl` tính là sót và được đếm ở `absent_in_pred`.
     - Gold cần ≥ 20 mẫu và ≥ 5 mẫu mỗi lớp.
     - Script ra bảng 2×2, recall và precision kèm cận dưới Wilson, `missed_by_stage` (bước làm mất mục), `stage_recall` và `report_line`.
     - Nếu recall dưới `--min-recall`, verdict bắt đầu bằng "recall thấp". Không giao kết quả như đã lọc xong.
   - **Proxy:** `calibrate.py proxy --data rows.jsonl --metric <proxy> --outcome <kết quả> --group <nhóm>`. Script tính Spearman theo nhóm (ví dụ theo query) với bootstrap 1.000 lần. Proxy chỉ "dùng được" khi CI 95% nằm trên 0.
   - **Proxy có biến nhiễu:** thêm `--control <trường>`, ví dụ log số chữ. Script tính Spearman riêng phần sau khi khử hạng của biến đó. Proxy embedding cấp trang luôn chạy thêm bản khử độ dài: pilot `topical-focus` có rho 0,22 khi gộp, khử độ dài còn 0,11 và CI chứa 0.
4. Đọc tay các ca lệch. Nếu model đúng mà gold sai, sửa gold bằng `gold-merge --overwrite --reason "<lý do>"`. Không sửa gold cho khớp model.
5. Ghi registry bằng `--write --registry <file> --rubric --version --model --site --industry --lang --evidence <đường dẫn>`. Entry cùng rubric, version, model, site, câu hỏi, nhãn dương, metric, outcome, group và control thì thay entry cũ.
   - Trạng thái: entry `jev`, `cosine`, `pipeline` chỉ ghi `ready` khi `--holdout` đạt. Thiếu holdout hoặc holdout không đạt thì entry ghi `draft`, threshold null. Giá trị đề xuất nằm ở `draft_values`. Entry `proxy`, `auc` ghi `ready`. Reference §5.
   - Instance khách: `00-client-context/model-calibration.json`.
   - Ngưỡng dùng chung: `tools/ai-assist/calibration-defaults.json`. Ngưỡng ở đây chỉ là điểm khởi đầu, chưa thay được hiệu chuẩn theo site.
6. Skill khác đọc ngưỡng theo thứ tự: entry `ready` trong registry của site → defaults → chưa có thì Claude đọc mọi mục. Entry `draft` không phải cổng. Skill đọc bỏ qua entry này, báo cáo ghi "bản nháp".
7. Báo cáo chuỗi nhiều bước chép nguyên `report_line`, để độ sót đứng cạnh độ đúng. Không chỉ báo độ đúng của bước Jev.
8. Tự phản biện theo mục dưới, rồi kiểm theo Gate và trả.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Gold và holdout được gán mù trên phiếu `gold-sheet`, trước khi xem nhãn model. Nguồn lỗi: rubric `scn-role` bản 18/10 có 35 nhãn gold gán cùng lúc với nhãn Jev.
- [ ] Phiếu lấy đều các dải confidence cộng ca khó. Gold có ≥ 40 mẫu, mỗi lớp ≥ 5. Nguồn lỗi: agent tự viết script tạm dựng phiếu 4 lần, đợt rà skill 16–24/10.
- [ ] Entry `jev`, `cosine`, `pipeline` chỉ `ready` khi holdout mới đạt. Entry còn lại là `draft`, threshold null. Nguồn lỗi: 19/10, cổng không YMYL được chọn trên chính 53 trang gold, không có holdout.
- [ ] Báo cáo chuỗi nhiều bước chép `report_line`: recall, số mục sót, precision. Nguồn lỗi: 19/10, chuỗi Jev → GLM bắt 15/22 mục có thật (recall 0,68), tin cuối chỉ báo Jev đúng.
- [ ] Proxy cấp trang có bản `--group` và bản `--control` độ dài. Nguồn lỗi: pilot `topical-focus` 10/2026, rho 0,22 khi gộp, khử độ dài còn 0,11, CI chứa 0.
- [ ] Ngưỡng ghi kèm version rubric, model, site và evidence. Nguồn lỗi: rubric `link-placement` cũ, defaults che lỗi thiếu hiệu chuẩn, 10/2026.

## Output

- `<workstream>/evidence/calibration/<rubric>_<ngày>.json`: bảng ngưỡng, độ đúng theo dải, verdict. Ghi bằng `--out`.
- `<workstream>/evidence/calibration/`: phiếu `<rubric>_phieu-gold.txt` (thêm `.html` khi gán ảnh), `gold.jsonl`, `holdout.jsonl`.
- Chuỗi nhiều bước: `<rubric>_pipeline_<ngày>.json` có bảng 2×2 và `report_line`.
- Một entry trong registry của site, kèm trạng thái `ready` hoặc `draft`.

## Gate

- [ ] Gold có ≥ 40 mẫu, đủ cả 2 lớp, gán trước khi xem nhãn model.
- [ ] Phiếu gold dựng bằng `gold-sheet`, không lộ nhãn hay confidence của model.
- [ ] Entry `jev`, `cosine`, `pipeline` ghi `ready` chỉ khi holdout ≥ 40 mẫu mới đạt. Không dùng entry `draft` làm cổng.
- [ ] Báo cáo chuỗi nhiều bước có `report_line`: recall và số mục sót đứng cạnh precision.
- [ ] Ngưỡng ghi kèm version rubric, model, site, ngành và đường dẫn evidence.
- [ ] Proxy đưa vào báo cáo khách có verdict "dùng được" và câu ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
- [ ] Dữ liệu khách gửi Jev chỉ là nội dung công khai trên web. Số GSC, hợp đồng, email chỉ xử lý bằng code hoặc EmbeddingGemma local.

## Anti-patterns

- Lấy ngưỡng của site mẫu dùng cho khách ngành khác → hiệu chuẩn lại trên 40 mẫu của khách.
- Tin `confidence` cao là đúng → bảng theo dải confidence trả lời câu này.
- Chọn ngưỡng trên 10 mẫu → Wilson cận dưới chặn.
- Proxy tương quan trên toàn bộ dòng nhưng không tương quan trong từng nhóm query → dùng `--group`.
- Proxy chỉ tương quan qua độ dài bài → dùng `--control`.
- Lấy outcome GSC từ bản query × page → bản này thiếu query ẩn danh. Dùng chiều page cho outcome cấp trang.
- Báo độ đúng của Jev cho cả chuỗi Jev → GLM → chạy `pipeline` và chép `report_line`.
- Chọn ngưỡng và kiểm ngưỡng trên cùng gold → thêm `--holdout` mẫu mới. Thiếu holdout thì entry là `draft`.
- Viết script tạm để dựng phiếu hay ghép gold → dùng `gold-sheet` và `gold-merge`.
- Dựng phiếu từ đầu ra Jev mà thiếu `--content` → phiếu chỉ có id. Thêm `--content jev_in.jsonl`.

## Changelog

- v1.4 (2026-10-25): cal-1: lệnh `gold-sheet` (kèm `--content`), `gold-merge`, `pipeline`, `cosine --gold`; cổng holdout, entry thiếu holdout ghi `draft`, threshold null. Thêm Phân việc model, Tự phản biện, `references/phieu-gold-va-holdout.md`, test `tests/test_gold_pipeline.py`.
- v1.3 (2026-10-19): `cosine --grid LO:HI:STEP` cho điểm ngoài dải cosine, dùng cho điểm gộp `anchor-score` của `link-relevance`.
- v1.2 (2026-10-19): thêm `--control` cho proxy (Spearman riêng phần). Khoá registry thêm control.
- v1.1 (2026-10-19): thêm `conf_gate` cho câu hỏi nhiều lớp (pilot: proof 0,5, objection 0,7). Khoá registry thêm nhãn dương, metric, outcome, group. `show` in metric và rho.
- v1.0 (2026-10-19): tạo mới. Chuyển 14 ngưỡng của `tools/ai-assist/README.md` §5 vào registry. Test offline `tests/test_calibrate.py`.
