---
name: retrieval-lab
description: "Mô phỏng truy xuất dense trên site vector index (EmbeddingGemma 2 local): xếp passage theo query, định tuyến query → URL so với URL Google đang chọn trong GSC, và kiểm proxy với trích dẫn AI thật. Dùng khi chẩn đoán cannibalization, chọn trang đích, hoặc sửa passage cho GEO."
metadata:
  version: "1.0"
---

# retrieval-lab — đo trang nào thắng ở bước truy xuất

Hệ truy xuất dense (RankEmbed của Google, retriever của ChatGPT và Perplexity) chấm query với từng passage, không chấm cả trang. Skill này tái tạo bước đó bằng EmbeddingGemma 2 trên index của skill `site-vector-index`. Kết quả là giả thuyết để sửa trang. Kết quả chưa phải trọng số thật của Google.

Gốc đường dẫn là root repo. Script: `skills/retrieval-lab/scripts/retrieval.py`, chạy bằng venv embedding với `-I`. Script đọc store qua `skills/site-vector-index/scripts/svi.py`.

## Khi nào dùng

- Hai URL cùng nhận impression cho một query, cần biết trang nào khớp nội dung hơn.
- Chọn trang đích cho cụm query mới trước khi viết.
- Sửa passage cho GEO: đoạn nào của site gần nhất với prompt, đoạn của đối thủ được AI trích gần hơn bao nhiêu.
- Không dùng để dự đoán thứ hạng. Thứ hạng còn phụ thuộc liên kết, hành vi người dùng và độ tin cậy của site.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Store của site, đối thủ hoặc SERP | skill `site-vector-index` | dựng store trước |
| Query | GSC (query × page, ≥ 90 ngày), prompt GEO, fan-out | hỏi người vận hành |
| URL Google đang chọn (chế độ route) | GSC: trang có impression lớn nhất của query | chỉ chạy chế độ rank |
| Nhãn thật (chế độ validate) | URL được AI trích dẫn (skill `geo-answer-lab`), URL top 10 không được trích | chưa kiểm được thì ghi "chưa chứng minh" |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,numpy,gemma,gsc?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

1. Gộp query theo NFC + casefold, giữ dấu và ký tự "&". Bỏ query dưới 20 impression trong kỳ.
2. **Định tuyến:** `retrieval.py route --store <store> --in queries.jsonl --out routing.jsonl --level page`. Mỗi dòng query mang `chosen`, `impr`, `pos`, `share`.
   - `agree_top1` sai và `share` < 0,6: Google đang chia query cho nhiều URL. Đây là ứng viên cannibalization. Đọc `gemma_top3` và nội dung 2 trang trước khi đề xuất gộp hay chỉnh.
   - `agree_top1` sai và `share` ≥ 0,6: Google ổn định chọn URL khác URL khớp nội dung nhất. Kiểm liên kết nội bộ và anchor trước khi sửa chữ.
3. **Xếp passage:** `retrieval.py rank --store <store> --in queries.jsonl --out ranks.jsonl --level passage` (có `candidates` thì chỉ xếp trong tập đó). Mỗi URL có cosine passage tốt nhất, hạng và khoảng cách tới URL đầu.
4. **Kiểm proxy** trước khi đưa số vào báo cáo khách: `retrieval.py validate --ranks ranks.jsonl --out report.json`. Script tính AUC từng query (URL nhãn dương với URL nhãn âm) và bootstrap CI 95%. Proxy chỉ có tín hiệu khi CI nằm trên 0,5. Ghi kết quả vào registry bằng skill `model-calibration`.
5. Claude đọc passage thắng (`best_item`) của các ca lệch. Sau đó đề xuất sửa heading, câu mở đoạn hoặc anchor. Không đề xuất theo cosine khi chưa đọc đoạn.

## Output

- `03-audits/content/<CLIENT>_retrieval_<YYYY-MM-DD>/`: `queries.jsonl`, `routing.jsonl`, `ranks.jsonl`, `report.json`, và một file `.md` gồm ca lệch, đoạn thắng, đề xuất sửa.
- Ngưỡng và verdict proxy: registry `00-client-context/model-calibration.json`.

## Gate

- [ ] Query dùng prompt `SearchQuery`, tài liệu dùng `Document`. Store và query cùng model.
- [ ] Số liệu đưa cho khách có verdict proxy "có tín hiệu" và câu ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
- [ ] Mọi đề xuất gộp, đổi hướng hay xoá trang đi qua người vận hành duyệt, rồi qua `wp-content-review-apply` nếu dự án có quyền WP-CLI. Skill này không tự sửa site.
- [ ] Số GSC chỉ xử lý local. Không gửi số GSC cho Jev hay API ngoài.

## Anti-patterns

- Kết luận cannibalization chỉ vì 2 URL có cosine gần nhau → kiểm `share` trong GSC trước.
- So cosine giữa 2 site có độ dài trang rất khác → so ở level passage, không so level page.
- Dùng một ngưỡng cosine cho mọi site → hiệu chuẩn lại theo site và theo cặp prompt.

## Changelog

- v1.0 (2026-10-19): tạo mới. Test offline `tests/test_retrieval.py`.
