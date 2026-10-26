# Lọc trước bằng EmbeddingGemma, SERP quyết cặp giáp ranh

File này ghi cách chạy `scripts/cluster.py`, ngưỡng đã hiệu chuẩn và giới hạn. Gốc đường dẫn là root repo. Nạp file này ở Bước 1b.

## 1. Lệnh

Đặt `S` = `skills/serp-clustering/scripts/cluster.py`. Đặt `PY` = `~/.venvs/embeddinggemma/bin/python`.

| Việc | Lệnh |
|---|---|
| Cosine mọi cặp keyword | `$PY -I $S cos --keywords <W>/keywords.txt --prompt SentenceSimilarity --out <W>/cos.jsonl` |
| Phân loại cặp | `python3 $S triage --cos <W>/cos.jsonl --diff-below 0.90 --out <W>/triage` |
| Đếm overlap SERP | `python3 $S overlap --serp <TSV seed,pos,url hoặc thư mục JSON Firecrawl>... --out <W>/serp` |
| Đo lại trên dữ liệu đã có SERP | `python3 $S evaluate --triage <W>/triage/triage.jsonl --serp-pairs <W>/serp/serp_pairs.jsonl --out <W>/triage/report.json` |
| Dòng cho hiệu chuẩn | `python3 $S labels --cos <W>/cos.jsonl --serp-pairs <W>/serp/serp_pairs.jsonl --pos-min 2 --out <W>/rows_ge2.jsonl` |

- `triage` ra `need_serp.txt`: chỉ keyword trong file này cần kéo SERP. Keyword còn lại là cụm đơn, verdict "TÁCH (Gemma)".
- `triage` không có `--same-from` khi chưa có ngưỡng "chắc cùng cụm" đã hiệu chuẩn. Gemma không ra verdict GỘP.

## 2. Ngưỡng và nguồn

Ngưỡng đọc theo thứ tự: registry của site (`00-client-context/model-calibration.json`) → `tools/ai-assist/calibration-defaults.json` → bảng dưới.

| Ngưỡng | Giá trị | Nguồn |
|---|---|---|
| Chắc khác cụm | cos < 0,90 (prompt `SentenceSimilarity`) | Hiệu chuẩn 19/10/2026 trên dev, nhãn overlap ≥ 2/10, NPV mục tiêu 0,99 |
| Chắc cùng cụm | không có | Trên dev, cặp âm cao nhất 0,9694 và chỉ 6 cặp overlap ≥ 6/10. Không ngưỡng nào đạt precision 0,95 |

Dữ liệu hiệu chuẩn: SERP Firecrawl ngày 18/10/2026, 46 keyword ngành dịch vụ SEO tiếng Việt, 1.035 cặp. Tách dev và holdout theo keyword (23 + 23, seed 20261019) trước khi đo cosine.

| Prompt (chọn trên dev) | AUC dev, nhãn overlap ≥ 2 |
|---|---|
| SentenceSimilarity | 0,879 |
| SearchQuery | 0,836 |
| Clustering | 0,832 |

| Đo với cos < 0,90 | Dev (253 cặp, 23 keyword) | Holdout (253 cặp, 23 keyword) |
|---|---|---|
| Cặp quyết không cần SERP | 134 | 186 |
| Lượt kéo SERP (1 lượt mỗi keyword) | 22/23, tiết kiệm 1 | 18/23, tiết kiệm 5 |
| Cặp sai: Gemma tách nhưng SERP ≥ 4/10 | 1 | 0 |
| Cặp sai: Gemma tách nhưng SERP ≥ 2/10 | 1 | 0 |

Cặp sai trên dev: "báo giá seo website" và "bảng giá dịch vụ seo tổng thể", cos 0,8961, SERP 7/10. Query giá dùng từ khác nhau ("báo giá", "bảng giá") có cosine thấp hơn mức SERP gộp.

## 3. Giới hạn

- Ngưỡng 0,90 hiệu chuẩn trên một ngành và 46 keyword. Site hoặc ngành mới: dùng 0,90 làm điểm khởi đầu, rồi hiệu chuẩn lại bằng skill `model-calibration` khi đã có SERP của ít nhất 40 cặp, gồm cả cặp overlap ≥ 2.
- Bộ keyword cùng ngách tiết kiệm ít lượt kéo SERP, vì gần như keyword nào cũng có ít nhất một cặp từ 0,90. Trên holdout, 5 keyword không cần kéo SERP đều là query định nghĩa ("... là gì").
- SERP cũng dao động. Ngày 18/10, 11 keyword kéo lại trong ngày (14 lần) có overlap với chính nó 5–10/10 ("seo agency" 5/10). Overlap 4–5/10 nằm trong biên dao động này.
- Cosine là chỉ số mô phỏng. Báo cáo khách ghi: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
