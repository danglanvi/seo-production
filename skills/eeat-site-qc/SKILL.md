---
name: eeat-site-qc
description: "QC E-E-A-T, helpfulness và page experience cho cả site theo checklist 83 check của Aleyda Solis: code chấm check tất định, Jev và EmbeddingGemma gắn cờ, Claude chốt mọi lỗi. Dùng khi audit chất lượng nội dung toàn site, sau core update hoặc trước đợt refresh."
metadata:
  version: "1.0.1"
---

# eeat-site-qc — checklist E-E-A-T cho mọi trang của site

Skill này chạy checklist "Google's Content Quality, E-E-A-T, Helpfulness & Page Experience" của Aleyda Solis trên toàn bộ URL của một site. Máy chỉ đề xuất trạng thái. Claude chốt mọi Does not meet và Partly meets, rồi đọc một mẫu ngẫu nhiên trong các Meets.

Phương pháp chấm (5 trạng thái, 4 scope, luật bằng chứng, ưu tiên gap) nằm ở `skills/semantic-content-audit/references/eeat-aleyda.md`. Đọc file đó trước lần chạy đầu. Gốc đường dẫn là root repo. Script: `skills/eeat-site-qc/scripts/site_qc.py`. Rubric Jev: `skills/eeat-site-qc/tasks/`. Định tuyến 83 check: `skills/eeat-site-qc/references/routing.json`.

## Khi nào dùng

- Audit chất lượng nội dung toàn site: đầu dự án, audit định kỳ, trước đợt refresh lớn.
- Site tụt sau core update: chạy với preset `core_update`, rồi phân tích theo `content-refresh` mode core update.
- Rà một nhóm trang theo template: trang địa phương, trang sản phẩm, trang review.
- Không dùng cho một URL lẻ: dùng `semantic-content-audit` Phase 4. Không dùng để viết lại bài.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Domain và danh sách URL công khai | sitemap hoặc crawl | hỏi phạm vi |
| Store crawl: `rows.jsonl`, `pages.jsonl`, `html/` | `site-vector-index` bước extract, dưới 7 ngày | chạy extract trước |
| `robots.txt` của site | `curl -s https://<domain>/robots.txt -o <W>/robots.txt` | SP01 ghi Not assessed |
| Ngôn ngữ đích, preset theo loại site | người vận hành | mặc định `vi`, preset `core` |
| Registry ngưỡng | `00-client-context/model-calibration.json` | cổng lấy từ defaults; báo cáo ghi "bản nháp" |
| Output `content-quality-lab` (effort, template, claims) và `topical-focus` | 2 skill đó | check tương ứng ghi "chưa chạy lane" |
| Bằng chứng ngoài trang: CrUX, bản ghi duyệt, uy tín | chủ site, `wp-pagespeed`, `geo-offsite-audit` | Not assessed, ghi vào `bang-chung-can-lay.md` |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code | SP01–03, PE04, PS08, CQ07, MT01, TA01–02, TA10, CP06, CP07, CP10, AI04 | dùng: kết quả tất định; Meets và N/A tự chốt, lỗi vẫn để Claude đọc |
| Jev | 4 rubric: `eeat-page-core` (loại trang, YMYL, PS01, PS03, PS04, CQ03, CQ09), `eeat-review` (RC, TA08, TA11, CP09), `eeat-ai-spam` (CP01, CP02, CP04, CQ06, CQ10), `eeat-ymyl-flag` (TA04, TA06, TA09, TA13). Dùng lại `content-effort` cho CQ01, CQ10, TA08 | dùng, đọc qua cổng của registry. Chưa có cổng thì mọi nhãn vào danh sách Claude đọc. Chỉ gửi chữ công khai của trang đang sống |
| EmbeddingGemma 2 | Khối chữ lặp (`content-quality-lab template`) cho CP01, CP04, AI01; độ lệch chủ đề (`topical-focus`) cho PS02, PS09 | dùng; mốc dup_share 0,2 và 0,5 là mốc nháp tới khi hiệu chuẩn |
| GLM Flash | Trích câu dẫn chứng | không dùng: Claude đọc trang trong danh sách trực tiếp |
| Claude | 20 check cần đọc (CQ04, CQ05, CQ11, TA07, TA12, RC05, RC07–11, SP04–07…), chốt mọi lỗi, đọc mẫu, gán gold, viết báo cáo | dùng |

20 check còn lại cần bằng chứng ngoài chữ trang (CWV field, quy trình, uy tín, Merchant Center). Máy không chấm các check này.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,bs4,jev,gemma?,numpy?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `gemma`: bỏ bước 5b và 5c. CP01, CP04, PS02, PS09 chỉ dùng Jev hoặc ghi "chưa chạy lane".

Đặt `<W>` = `03-audits/content/<CLIENT>_eeat-qc_<YYYY-MM-DD>/`, `<S>` = store crawl của site.

1. **Chốt phạm vi.** Domain, số URL, ngôn ngữ, preset (`core` + `review`, `ymyl`, `ecommerce`, `programmatic`, `ai_assisted`, `ai_search`, `core_update` theo site). Tải `robots.txt` vào `<W>`.
2. **Crawl.** Chạy extract của `site-vector-index` nếu store cũ hơn 7 ngày. Kiểm `pages.jsonl.failed.json`: URL lỗi ghi Not assessed, không ghi Does not meet.
3. **Code:** `python3 -E skills/eeat-site-qc/scripts/site_qc.py code --pages <S>/pages.jsonl --html-dir <S>/html --robots <W>/robots.txt --lang vi --out <W>/code.jsonl`.
4. **Jev.** Mỗi rubric chạy `--dry-run` trước, rồi lượt thật:
   - `site_qc.py prepare --rows <S>/rows.jsonl --pages <S>/pages.jsonl --rubric eeat-page-core --out <W>/jev/core_in.jsonl`
   - `python3 -I tools/ai-assist/jev.py --task skills/eeat-site-qc/tasks/eeat-page-core.json --in <W>/jev/core_in.jsonl --out <W>/jev/core_out.jsonl --budget 0.2 --label eeat-qc`
   - Lặp lại cho `eeat-ai-spam` (mọi trang), `eeat-review` và `eeat-ymyl-flag` (thêm `--core <W>/jev/core_out.jsonl` ở bước prepare: script chỉ lấy trang review hoặc YMYL).
   - Mỗi trang tốn khoảng 0,0002 USD mỗi rubric. Xem tổng bằng `python3 tools/ai-assist/jev_ledger.py --label eeat-qc`.
5. **Lane dùng lại:**
   - a. `content-quality-lab` bước 1–2 (rubric `content-effort`) và bước 4 (report) → `<W>/effort/pages.jsonl`.
   - b. `content-quality-lab` bước 5 (`template`) → `<W>/template/pages.jsonl`.
   - c. `topical-focus` lệnh `map` → `<W>/topical/pages.jsonl`.
   - d. Tuỳ chọn: `content-quality-lab` bước 6 (`claims`) → `<W>/claims/claims.jsonl`.
6. **Gộp:** `site_qc.py report --pages <S>/pages.jsonl --code <W>/code.jsonl --jev <W>/jev/core_out.jsonl,<W>/jev/spam_out.jsonl,<W>/jev/review_out.jsonl,<W>/jev/ymyl_out.jsonl --effort <W>/effort/pages.jsonl --dup <W>/template/pages.jsonl --topical <W>/topical/pages.jsonl --presets core,<preset> --registry 00-client-context/model-calibration.json --site <domain> --out-dir <W>`.
7. **Claude đọc `doc-lai.tsv`.** Mở từng trang, ghi cột `ket_luan_claude` theo dạng `<trạng thái> | <bằng chứng>`. Thứ tự: Does not meet, Partly meets, Not assessed, rồi mẫu Meets.
   - Đọc check Template và Site một lần, rồi áp cho các trang cùng template.
   - Dòng "Claude đọc mẫu": đọc 1–2 trang mỗi template. Trang còn lại giữ Not assessed.
   - Chạy `site_qc.py merge --status <W>/trang-thai.csv --read <W>/doc-lai.tsv --out <W>/trang-thai-chot.csv`.
8. **Bằng chứng ngoài trang.** Gửi `bang-chung-can-lay.md` cho chủ site. Có bằng chứng thì cập nhật dòng đó trong `trang-thai-chot.csv`.
9. **Báo cáo** `<W>/<CLIENT>_eeat-qc_v1.md`:
   - câu phạm vi ở đầu (đánh giá chuyên môn, không phải điểm Google);
   - phát hiện chính theo template, mỗi gap có check ID, URL và scope, phát hiện, hậu quả cho người đọc, bằng chứng, thay đổi, người làm, effort, completion test;
   - danh sách Not assessed và bằng chứng cần lấy;
   - dòng ghi nguồn Aleyda ở cuối (có sẵn trong `report.md`).
10. **Hiệu chuẩn** (lần đầu mỗi version rubric, hoặc site khách mới): dùng skill `model-calibration`.
    - Gán gold mù ≥ 40 trang mỗi câu hỏi trước khi xem nhãn Jev. Lấy mẫu theo dải p_yes, cộng holdout ngẫu nhiên.
    - Chạy `calibrate.py jev --pred <out> --gold <gold> --question <q> --positive yes`, rồi ghi registry của site.
    - Site khách mới mà chỉ có cổng defaults: gán gold 20 trang, so với cổng defaults trước khi tin cổng đó. Lệch thì hiệu chuẩn đủ 40.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình người duyệt.

Bản tốt nhất phải có:
- [ ] Mọi Does not meet và Partly meets trong báo cáo có kết luận của Claude kèm bằng chứng, không lấy nhãn Jev làm verdict. Nguồn lỗi: `content-quality-lab` 19/10/2026, cùng câu hỏi Jev cho độ đúng 75% và 81% ở 2 lượt trên cùng holdout.
- [ ] Not assessed tách khỏi Does not meet; URL tải lỗi và check thiếu bằng chứng không bị tính là lỗi. Nguồn lỗi: thang E-E-A-T cũ của `semantic-content-audit` cho 0 điểm khi thiếu bằng chứng (rà 02/11/2026).
- [ ] Báo cáo ghi cổng nào lấy từ registry của site, cổng nào lấy từ defaults. Nguồn lỗi: cổng dev của `self_superlative` và `unsourced_stat` trượt holdout mới (`content-quality-lab` 19/10/2026).
- [ ] Check Template và Site được chấm một lần và nêu số trang áp dụng, không nhân lỗi theo số URL. Nguồn lỗi: checklist Aleyda tách 4 scope; một URL không đại diện cho cả template.
- [ ] Không kết luận spam chỉ vì trang dùng AI, template hay số lượng lớn; kết luận CP đã đọc chính sách spam của Google. Nguồn lỗi: `content-quality-lab`, đếm thô cụm cấm rồi đề xuất xoá cả câu khuyên chung và câu nói về bên khác.
- [ ] Jev chỉ nhận chữ công khai của trang đang sống; không gửi query GSC, bản nháp site khách, hợp đồng. Nguồn lỗi: luật dữ liệu `content-quality-lab` v1.2.3 (19/10/2026).
- [ ] Mỗi gap có completion test kiểm được. Nguồn lỗi: checklist Aleyda yêu cầu audit sau mới đổi trạng thái; đánh dấu việc xong chưa đủ.

## Output

- `<W>/code.jsonl`, `<W>/jev/*_in.jsonl`, `<W>/jev/*_out.jsonl`.
- `<W>/trang-thai.csv`: cột `target, template, scope, check_id, status, route, source, p, evidence`. `target` = URL, `__site__` hoặc `*` (theo template).
- `<W>/doc-lai.tsv`: dòng cần Claude đọc, thêm cột `ket_luan_claude`.
- `<W>/trang-thai-chot.csv`: sau bước merge.
- `<W>/bang-chung-can-lay.md`, `<W>/report.md` (bản máy), `<W>/<CLIENT>_eeat-qc_v1.md` (báo cáo chốt).
- Gold và kết quả hiệu chuẩn: `<W>/calibration/`. Entry registry ở `00-client-context/model-calibration.json`.

## Gate

- [ ] `doc-lai.tsv` không còn dòng Does not meet hoặc Partly meets thiếu `ket_luan_claude`.
- [ ] Mỗi dòng Meets, Does not meet, Not applicable trong `trang-thai-chot.csv` có evidence.
- [ ] Báo cáo có câu phạm vi ở đầu và dòng ghi nguồn Aleyda ở cuối. Báo cáo không có điểm E-E-A-T tổng hay % đạt.
- [ ] Số lượt và chi phí Jev lấy từ `jev_ledger.py`, không cộng tay.
- [ ] YMYL có lỗi: đề xuất người có chuyên môn duyệt. Không chẩn đoán y tế, không kết luận pháp lý.
- [ ] Không đề xuất bịa chuyên môn, đổi ngày cho đẹp, viết thêm chữ cho đủ số từ, xoá bài hàng loạt.

## Anti-patterns

- Dùng nhãn Jev chưa hiệu chuẩn làm trạng thái cuối → mọi nhãn chưa có cổng đi vào `doc-lai.tsv`.
- Gộp nhiều lỗi vào một câu hỏi Jev → mỗi câu hỏi hỏi một điều. `ui-visual` v1 hỏi chung "có lỗi không" thì gắn cờ 81% ảnh (17/10/2026).
- Coi trang không có byline là lỗi ở mọi loại trang → trang dịch vụ, sản phẩm chỉ cần tổ chức chịu trách nhiệm rõ; script chỉ đổi sang Does not meet ở trang bài, review, tin.
- Coi trang lệch chủ đề (outlier của Gemma) là lỗi → outlier chỉ là cờ đọc; trang giới thiệu, liên hệ thường lệch tâm.
- Chấm CWV bằng điểm PageSpeed lab → PE01–PE03 chỉ dùng field p75; không có field data thì Not assessed.

## Changelog

- v1.0.1 (2026-11-02): sửa 6 luật code sau lượt chạy đầu trên site mẫu 332 trang (CP07 chỉ bắt câu lệnh gửi AI, không bắt tab ẩn nhắc tên AI; CQ07 và MT01 bỏ qua chữ giải thích biến template; PS08 đo trên title, H2, đoạn đầu; TA02 nhận link nội bộ trong khối tác giả; dòng Not assessed của code chỉ lấy 2 trang mẫu mỗi template). Báo nhầm ở CP07, CQ07, MT01: 7 → 0; TA02 Partly 308 → 50. Test 7/7.
- v1.0.0 (2026-11-02): tạo mới. `site_qc.py` (code, prepare, report, merge), 4 rubric Jev 2026-11-02.1 chưa hiệu chuẩn, `references/routing.json` (43/83 check có tín hiệu máy), test offline `tests/test_site_qc.py`.
