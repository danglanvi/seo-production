# Readiness và baseline GEO — đầu vào/đầu ra cho router

Mục đích: chấm GE-03/04/05 và cấp dữ liệu GE-33…35. Nguồn: master tier-1-geo.md v2.0.3 + guideline G0/G5; quy ước đo GTV, không phải công thức dự báo ROI. Trạng thái theo audit-contract.md cùng thư mục.

## 1. Readiness GE-04

Nhận domain/brand, thị trường/ngôn ngữ, ngành, mục tiêu kinh doanh, URL/câu hỏi mục tiêu, đối thủ và khả năng cung cấp nguồn tin đáng tin (đặc biệt YMYL). Không yêu cầu giá/doanh thu để chấm readiness.

Lập bảng: tín hiệu · quan sát · nguồn/ngày · giới hạn · hệ quả. Kiểm mẫu query lõi (gợi ý 10, ghi nguyên danh sách): bề mặt AIO có/không, citation/mention của đối thủ trên engine mục tiêu, index/access/rank của URL, nguồn lực sản xuất evidence/đo. Không lấy tỷ lệ AIO toàn ngành thay mẫu của dự án.

- Chuẩn hoá (đề xuất): có cơ hội quan sát liên quan mục tiêu thương mại (đối thủ được trích/nhắc hoặc AI trả lời sai về brand), đủ scope và nguồn lực triển khai/đo cả các mảng; ghi lý do từ evidence.
- Tối thiểu (đề xuất): cơ hội quan sát thấp/chưa ưu tiên hoặc chưa đủ nguồn lực; duy trì nền và baseline. Chưa có data không được suy ngành không cần GEO; verdict tạm/UNKNOWN, nêu dữ liệu để xét lại.
- Không dùng điểm trọng số/ngưỡng AIO tự đặt. Nếu tín hiệu trái nhau, nêu trade-off và mức đề xuất, xác nhận scope với người phụ trách; không tự tạo cam kết chi phí/hiệu quả.

GE-04 PASS khi có verdict có lý do + scope + ngày; verdict chưa chốt → UNKNOWN. Applicability GE-28/29 theo từng đợt/scope, không tự bỏ toàn OFFSITE vì mức Tối thiểu.

## 2. GE-03 baseline

Dùng prompt-templates.md (dịch vụ, khung 28–40 câu) hoặc ecommerce-matrix.md (80–100 câu); là chuẩn vận hành GTV, scope nhỏ được ghi là pilot thay vì baseline đầy đủ. Chốt prompt nguyên văn, ID, topic, intent, branded/non-branded và URL liên quan trước khi đo. Thu tối thiểu ChatGPT + Google AI Mode + Gemini; AIO theo query khi khả dụng, giữ từng bề mặt riêng. Mỗi prompt/engine lặp ≥3 lần (chuẩn nội bộ 5), ghi response_id, câu trả lời gốc/nguồn cited, ngày, model nếu biết, môi trường API/UI/ngôn ngữ/thị trường. Thiếu khả năng truy cập thì nhận export/paste; không tự giả lập câu trả lời từ search thường.

Schema dòng dữ liệu: `prompt_id · prompt_text · topic · intent · branded · engine/surface · model_if_known · date · run_id · response_id · raw_answer_or_file · found_urls · cited_urls · brand_mentioned · recommended · competitors · context · information_accuracy`.

Mỗi response đếm brand/domain tối đa một lần cho tỷ lệ hiện diện; nhiều link cùng domain không tạo nhiều lượt hiện diện. Tách found, citation, mention, recommendation. Lưu định nghĩa SoV (brand appearances / tổng appearances của tập brand cố định, có thể nhiều brand/response), không trộn với mention rate (response có brand / tổng response hợp lệ). Không có response → tỷ lệ N/A, không 0%. Tỷ lệ lặp là mô tả mẫu, không tự tuyên bố ý nghĩa thống kê.

GE-03 PASS khi prompt set và dữ liệu đủ scope/lần chạy có bằng chứng, thông tin accuracy được đối chiếu với brand facts; xác nhận chưa đo → FAIL; chưa đưa file/không biết → UNKNOWN. Không lấy lời khẳng định có baseline thay toàn bộ evidence để gate PASS. Khi đo muộn, tạo baseline phiên bản mới; không gọi là dữ liệu T1 hồi phục.

## 3. GE-05 và bàn giao

GE-05: kế hoạch ghi 5 giới hạn: không bán llms.txt như lever; schema cho entity/rich result không bảo đảm citation; không cam kết từng prompt; không dùng tên tín hiệu chưa xác minh; không nhồi official. Lưu đoạn/file chứng minh; không cần tự soạn hay gửi SOW để audit đạt.

Output: mức + lý do + ngày + bảng applicability; prompt set; raw responses/baseline; bảng GE-03/04/05 trạng thái/evidence; data thiếu; lịch đo đề xuất. Repo Production: `08-geo-ai-visibility/<CLIENT>_geo-baseline_vN.md`; standalone: `outputs/` hoặc nơi user giao. Không tự tạo automation. Bàn giao GE-33/34/35 bằng bảng nguồn có thể kiểm, G-T1 do router kết hợp GE-01/02.

Đối chiếu hiệu quả kinh doanh với GA4 hoặc server log khi có; GSC Generative AI nếu report khả dụng. Không có referral do zero-click không phủ nhận visibility; cũng không đủ chứng minh doanh thu. So sánh trước/sau theo hợp đồng audit, không đổi prompt tháng này rồi so raw total với tháng trước.
