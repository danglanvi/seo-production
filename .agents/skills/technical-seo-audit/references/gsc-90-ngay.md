# Nhánh GSC 90 ngày qua API

Đọc file này khi property GSC đã share cho tài khoản Google đang login `gws` trên máy (kiểm bằng `tools/gsc/gsc.sh sites`). Quy trình đã chạy thật trên một site agency ngày 17/10/2026. Lệnh Jev và EmbeddingGemma: `tools/ai-assist/README.md`.

## 1. Kéo dữ liệu

| Dữ liệu | Lệnh | Ghi chú |
|---|---|---|
| Property truy cập được | `tools/gsc/gsc.sh sites` | Không thấy property thì dừng nhánh này, ghi ⬜ THIẾU DATA |
| Số theo cửa sổ | `gsc.sh query <property> <days> <dimensions>` | 28 ngày, 28 ngày trước, 28 ngày cùng kỳ năm trước, 90 ngày, 90 ngày cùng kỳ |
| Chuỗi tháng và tuần | `query` với dimension `date`, gom ở local | Đánh dấu mốc cập nhật của Google lên chuỗi tuần |
| Query × trang, thiết bị, quốc gia | `query` với `query,page`, `device`, `country` | Query ẩn danh không có trong bảng query |
| Sitemap đã submit | `gsc.sh sitemaps <property>` | |
| Trạng thái index từng URL | `gsc.sh coverage <property> <file-urls.txt> <out>` | Quota 2.000 URL/ngày/property. Chạy URL trong sitemap + URL có traffic |
| robots.txt, sitemap thật | `curl` | Lưu bản chụp có ngày |

Bảng kéo về phải làm sạch trước khi đếm:

- API Search Analytics trả tối đa 25.000 dòng mỗi lần kéo. Bảng query × trang đúng 25.000 dòng là bảng bị cắt. Kéo lại theo từng trang (filter `page`) hoặc chia cửa sổ ngày, và ghi giới hạn này trong báo cáo.
- GSC theo trang ghi thêm dòng jump link (URL có mảnh `#`, ví dụ `#ftoc-heading-3` của mục lục) với lượt hiển thị gần bằng URL gốc. Bỏ các dòng này trước khi cộng theo trang hoặc theo truy vấn: `python3 skills/technical-seo-audit/scripts/gsc_clean.py --in <bảng>.tsv --out <bảng>_clean.tsv`. Script in số dòng jump link và cờ `capped`.
- Site mẫu 18/10/2026: 6.702/25.000 dòng là jump link. Một truy vấn có 3.923 lượt hiển thị trên URL gốc thành 18.877 khi cộng cả jump link. Lần chạy đầu thổi số của 2 trang tiền.
- Vị trí của truy vấn lấy theo URL Google chọn, không trung bình qua mọi URL.

API không đọc được: Page indexing tổng, Crawl Stats, báo cáo Core Web Vitals, AI Overview, **Manual actions**, **Security issues**. Nhờ người có quyền GSC kiểm tay trên giao diện. Khi traffic giảm trùng đợt spam update, kiểm Manual actions và Security issues trước mọi phân tích khác.

## 2. Luật đọc số

- So bằng clicks. Impressions và vị trí trung bình trước khoảng 10–14/09/2025 có phần ảo do công cụ quét SERP dùng `num=100`. Mốc này là tin ngành, Google không công bố. Ghi rõ caveat này khi so cùng kỳ.
- Tìm query bất thường: impressions rất lớn, gần như toàn bộ trên desktop, CTR khoảng 0,02%. Trừ query đó khỏi tổng impressions trước khi kết luận (site mẫu: một query 708.061 impressions trong 90 ngày).
- Ghi tỷ lệ clicks thuộc query ẩn danh. Mọi bảng theo query chỉ phủ phần còn lại.
- Đặt chuỗi tuần cạnh lịch cập nhật trên Google Search Status Dashboard. Ghi "trùng thời điểm", không ghi "do" khi chưa có bằng chứng khác.
- Vị trí trung bình "tốt lên" khi query thứ hạng thấp mất impressions. Không dùng vị trí trung bình toàn site làm bằng chứng tăng hạng.

## 3. Phân rã nguyên nhân giảm

Phạm vi: query có tên, theo thiết bị, cửa sổ hiện tại so với cùng kỳ, đã bỏ query bất thường.

| Kiểu mất click | Cách tính |
|---|---|
| Mất hiển thị | Query còn ở kỳ trước, kỳ này 0 impressions |
| Tụt vị trí | Vị trí xấu đi, CTR theo vị trí giảm |
| CTR giảm ở cùng vị trí | Ước lượng phần AI Overview từ chênh CTR. Ghi "ước lượng" |
| URL gỡ hoặc 301 | URL kỳ trước nay trả 3xx, 4xx hoặc nháp |

Ghi phần trăm mức giảm mà phép phân rã phủ được. Phần còn lại thuộc query ẩn danh.

## 4. Phân tích một đợt tụt

1. Mẫu: URL có từ 100 impressions và vị trí ≤20 trong 14 ngày trước đợt.
2. So vị trí với 14 ngày sau đợt. Đếm URL tụt từ 10 bậc, trung vị thay đổi vị trí, clicks trước và sau.
3. Gán nhóm chủ đề bằng Jev `gsc-topical-fit` ở chế độ chữ (từ 0,5; dưới ngưỡng Claude đọc). Input mỗi trang chỉ có url, title, H1, đoạn mở. Không gửi top query. Nhóm mẫu: bài cốt lõi, bài lân cận, bài lạc chủ đề, trang dịch vụ, trang công ty.
4. Kiểm giả thuyết bằng số nhóm. Site mẫu, đợt tụt cuối 09/2026: bài cốt lõi tụt 60/101, trang dịch vụ 1/13. Kết luận của đợt đó: gỡ bài lạc chủ đề không phải việc chính.

## 5. Cơ hội

| Cơ hội | Cách tìm | Model |
|---|---|---|
| Query thương mại rơi vào bài thông tin | Cặp query–trang vị trí ≤15, trang là bài | Không gửi Jev, vì input là query GSC. Trang nào khớp query hơn: `skills/retrieval-lab` chế độ `route` (Gemma local). Ý định thương mại của query: Claude đọc danh sách đã lọc |
| Ăn thịt từ khoá | Ứng viên: EmbeddingGemma cosine từ 0,905, hoặc cặp có từ 3 query chung (`gsc_pairs.py overlap`). Query chung, lượt hiển thị chung, trang thắng: code local | Jev `gsc-cannibal-pair` chế độ chữ (từ 0,7; Claude đọc mọi nhãn trùng ý định và mọi cặp dưới cổng) |
| Cụm query chia cho nhiều URL | Gom query theo cụm, đếm URL nhận impressions | Không cần model |
| CTR thấp | Vị trí ≤10, CTR thấp hơn trung vị cùng vị trí | Không cần model |
| Bài suy giảm | Clicks giảm liên tục qua nhiều tháng | Không cần model |

- Cosine EmbeddingGemma chỉ chọn ứng viên, không kết luận. Trang cùng template (tuyển dụng, chuyên mục) có cosine 0,97+ dù không cạnh tranh.
- Cặp ngôn ngữ (VI ↔ EN) không phải ăn thịt từ khoá.

### Dữ liệu GSC chỉ xử lý local

Jev chỉ nhận chữ công khai của trang. Query, clicks, impressions, vị trí chỉ đi vào code và Gemma chạy trên máy.

```bash
# So query của cặp trang (file ra có query: giữ local)
python3 skills/technical-seo-audit/scripts/gsc_pairs.py overlap --gsc <W>/gsc_page_query_clean.tsv --site <tên miền> \
  [--pairs <W>/pairs.tsv] --out <W>/cannibal_overlap.tsv
# Input Jev chế độ chữ: url, title, H1, đoạn mở; shared_queries rỗng
python3 skills/technical-seo-audit/scripts/gsc_pairs.py jev-in --pages <W>/pages.jsonl --pairs <W>/pairs.tsv \
  --site <tên miền> --out <W>/cannibal_jev_in.jsonl
# Chặn trước mỗi lượt Jev, kể cả input gsc-topical-fit
python3 skills/technical-seo-audit/scripts/gsc_pairs.py check --in <W>/cannibal_jev_in.jsonl
```

- `pages.jsonl`: một dòng mỗi trang `{url, title, h1, opening}`, lấy từ HTML công khai.
- Kiểm lại trên gold gán tay 17/10 (site mẫu, rubric giữ nguyên chữ, chỉ bỏ query):

  | Rubric | Mẫu | Có query GSC | Chế độ chữ |
  |---|---|---|---|
  | `gsc-cannibal-pair` 2026-10-17.2 | 47 cặp | 45/47; từ 0,7: 20/20, phủ 43% | 45/47; từ 0,7: 28/28, phủ 60% |
  | `gsc-topical-fit` 2026-10-17.1 | 45 trang | 45/45; từ 0,5: 40/40, phủ 89% | 45/45; từ 0,5: 42/42, phủ 93% |

- Chế độ chữ gán `duplicate_intent` ít hơn: 3/7 cặp gold trùng ý định so với 4/7. Bốn cặp sót đều dưới cổng 0,7, nên Claude vẫn đọc.
- Cặp chỉ có trong văn bản (không có query chung) vẫn đi qua Jev chế độ chữ. 21/47 cặp gold không có query chung trong bảng 25.000 dòng kéo ngày 18/10.
- Chi phí mẫu: 0,077 USD cho 2.097 lượt Jev, gồm hiệu chuẩn.

## 6. Đầu ra

- Chèn vào báo cáo technical audit: mục "Số liệu GSC" (bảng cửa sổ, chuỗi tuần có mốc cập nhật, phân rã nguyên nhân, đợt tụt theo nhóm).
- Top việc ưu tiên có cột "Chỉ báo theo dõi" (ví dụ "1 URL/query trong GSC sau 4–8 tuần").
- Evidence: `gsc_tong-quan_cua-so.tsv`, `gsc_theo-thang.tsv`, `gsc_theo-tuan.tsv`, `gsc_url_hieu-suat.tsv`, `gsc_url-inspection_<n>.tsv`, `nguyen-nhan-giam_phan-ra.tsv`, `intent-match_query-trang.tsv`, `cannibal_cap-trang.tsv`, `jev/` (rubric, nhãn tay, `nguong-hieu-chuan.md`).
- Mục giới hạn dữ liệu: phần trăm query ẩn danh, ngày cuối của dữ liệu GSC, phần API không đọc được, giả thuyết chưa xác minh.
- Sửa title, meta, link sau audit: ghi qua skill `wp-content-review-apply`.
