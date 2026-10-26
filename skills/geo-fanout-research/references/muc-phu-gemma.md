# Đo mức phủ subquery theo section bằng EmbeddingGemma 2

Mục đích: cách chạy `scripts/fanout_cover.py`, cách đọc số và giới hạn đã đo. Bước 4 của skill nạp file này. Gốc đường dẫn là root repo.

## 1. Phép đo

- Mỗi subquery được encode với prompt `SearchQuery`. Passage của trang được encode với prompt `Document` trong store của skill `site-vector-index`.
- `best_cos` của một subquery trên một trang là cos cao nhất trên mọi passage của trang. Section thắng là section chứa passage đó.
- `mean_best` của một trang là trung bình `best_cos` qua mọi subquery của prompt.
- `share_ge_<t>` là tỉ lệ subquery có `best_cos` ≥ t. Cột này chỉ dùng khi registry có ngưỡng phủ đã hiệu chuẩn.

## 2. Kết quả hiệu chuẩn 19/10/2026

Dữ liệu: 30 prompt GEO ngành dịch vụ SEO, 178 subquery Claude viết theo 8 lens trước khi xem nhãn, 270 câu trả lời AI ngày 18/10/2026 (ChatGPT, Perplexity, Gemini). Nhãn dương là URL được AI trích cho đúng prompt. Tách dev/holdout theo prompt, 15/15, seed 20261019.

| Phép đo | Dev | Holdout | Đọc |
|---|---|---|---|
| `mean_best`, trong top 10 của prompt (AUC) | 0,674 [0,521; 0,807] | 0,683 [0,606; 0,746] | có tín hiệu ở cả 2 nửa |
| Cos prompt gốc, trong top 10 (AUC) | 0,636 [0,499; 0,748] | 0,561 [0,473; 0,653] | yếu hơn fan-out |
| `mean_best`, khử log số passage (Spearman) | 0,202 [−0,066; 0,453] | 0,199 [0,015; 0,387] | tín hiệu yếu, chỉ đạt ở holdout |
| `share_ge_0,825` (ngưỡng tốt nhất ở dev, AUC) | 0,652 | 0,603 | không hơn `mean_best` |
| Cặp subquery × trang (`calibrate.py cosine`) | không có ngưỡng nhận; ngưỡng loại 0,71 phủ 26/699 cặp | không có ngưỡng nhận; 0,72 phủ 28/739 cặp | không dùng làm verdict |
| `mean_best`, mọi URL được trích so với top 10 (AUC) | 0,364 | — | ngược chiều, như prompt gốc (0,351) |

Kết luận:

- Dùng `mean_best` để so trang mình với trang khác trong cùng top 10 của một prompt.
- Không dùng một ngưỡng cos để nói subquery đã được phủ. Claude đọc section thắng rồi ra verdict COVERED hay GAP.
- Trang được trích ngoài top 10 đến từ truy vấn mà subquery theo lens chưa bắt được. Không dùng phép đo này cho trang ngoài top 10.

## 3. Ví dụ đọc bảng gaps

Prompt "Làm sao đo hiệu quả GEO cho website doanh nghiệp?" (18/10/2026). Trang A của site mình có cos prompt gốc cao nhất top 10 nhưng không được trích. Bảng gaps cho thấy trang A thua trang được trích ở 3/6 subquery:

| Subquery | Trang A | Trang được trích |
|---|---|---|
| Cách theo dõi thương hiệu xuất hiện trên ChatGPT | 0,7212 | 0,7914 |
| Share of voice trong AI search là gì | 0,7402 | 0,7647 |
| Công cụ đo AI visibility | 0,7960 | 0,8239 |

Claude đọc section thắng của trang A cho 3 subquery đó. Nếu section chỉ nhắc ý mà không trả lời, verdict là GAP-HEADING và đề xuất heading mới.

## 4. Giới hạn

- Hiệu chuẩn trên 1 ngành, 1 thị trường, tiếng Việt. Site hoặc ngành mới: hiệu chuẩn lại bằng skill `model-calibration` khi có câu trả lời AI thật.
- Subquery do Claude viết theo lens. Subquery thật của engine không công khai.
- Câu ghi bắt buộc khi đưa số này cho khách: "chỉ số mô phỏng, trọng số thật của Google chưa công bố".
