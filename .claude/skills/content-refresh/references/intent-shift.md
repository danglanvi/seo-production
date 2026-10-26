# Đo intent dịch chuyển bằng EmbeddingGemma 2

Mục đích: cách chạy `scripts/intent_shift.py`, cách đọc `drift` và giới hạn đã đo. Bước 4a của skill nạp file này. Gốc đường dẫn là root repo.

## 1. Phép đo

- Mỗi kết quả SERP thành văn bản "title | snippet" (tối đa 300 ký tự). Trang mình thành "title | meta". Cả hai encode bằng prompt `Document`.
- Tâm là trung bình vector của top N kết quả (mặc định N = 3), chuẩn hoá lại. `--exclude-own` bỏ kết quả cùng domain với trang mình trước khi lấy top N.
- `spread` là cos trung bình của từng kết quả top N với tâm. Số này cho biết top N thống nhất intent tới đâu.
- `drift` = `spread` − cos(trang mình, tâm). `drift` lớn nghĩa là trang mình đứng xa intent mà top N đang thống nhất.
- So `drift`, không so cos thô: truy vấn có SERP phân tán thì cos thô thấp dù trang mình không lệch.

## 2. Kết quả hiệu chuẩn 19/10/2026

Dữ liệu: 1 site dịch vụ SEO tiếng Việt, 25 truy vấn, SERP Firecrawl top 10 Việt Nam ngày 18/10/2026, vị trí GSC 90 ngày của URL có lượt hiển thị lớn nhất cho đúng truy vấn.

| Phép đo | Spearman với vị trí GSC | Đọc |
|---|---|---|
| `drift`, top 3, bỏ trang mình | 0,545 [0,156; 0,796] | có tín hiệu: drift lớn đi cùng vị trí kém |
| `drift`, khử log lượt hiển thị | 0,533 [0,163; 0,810] | tín hiệu không đến từ quy mô truy vấn |
| −cos thô với tâm | 0,429 [−0,047; 0,723] | chưa chứng minh |

- Kết quả thật về quyết định: trong 15–19/10 chỉ 1 trang được quyết viết lại vì SERP đổi nghĩa (truy vấn định nghĩa phổ thông, trang mình viết theo nghĩa SEO). Trang đó đứng hạng 8/25 theo `drift`. Một nhãn dương không đủ để chọn ngưỡng REWRITE.
- 4/7 truy vấn có `drift` cao nhất là truy vấn dịch vụ mà Google đang chọn trang khác loại (trang bảng giá, trang địa phương, trang định nghĩa). Đây là lỗi định tuyến URL, không phải intent dịch chuyển theo thời gian.
- Top 10 sau khi bỏ trang mình chỉ đủ 10 kết quả ở 3/25 truy vấn. Vì vậy skill dùng top 3.

Kết luận: dùng `drift` để xếp thứ tự truy vấn cần Claude đọc SERP. Chưa có ngưỡng REWRITE. Ghi verdict "chưa hiệu chuẩn, Claude đọc top 3".

## 3. Đo theo thời gian

Một ảnh SERP chỉ cho biết trang mình lệch SERP hiện tại. Muốn nói intent đã dịch chuyển, lưu SERP có ngày ở mỗi lần audit. So `drift` của cùng truy vấn và cùng trang qua 2 ngày SERP. `drift` tăng rõ trong khi trang không đổi nội dung là bằng chứng dịch chuyển.

## 4. Giới hạn

- Hiệu chuẩn trên 1 site, 1 ngành, tiếng Việt, 25 truy vấn. Site khác: chạy lại bằng skill `model-calibration` (chế độ `proxy`, outcome vị trí GSC) trước khi dùng số.
- Số GSC chỉ xử lý local. Không gửi số GSC cho Jev hay API ngoài.
- Khi có ≥ 10 quyết định REWRITE và ≥ 10 quyết định refresh có ghi lý do, hiệu chuẩn ngưỡng bằng `calibrate.py cosine --grid` trên `drift`.
