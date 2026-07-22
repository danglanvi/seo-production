# Location Page Checklist — multi-location / hybrid

> Dùng bởi `local-seo-audit` Bước 3. Mỗi chi nhánh 1 trang; mục tiêu: từng trang đứng được như 1 entity con riêng ([[E-A-V Framework]] per chi nhánh), không phải template đổi mỗi địa chỉ.

## A. Cấu trúc URL & index

| Check | Tiêu chí ĐẠT |
|---|---|
| URL riêng ổn định | `/chi-nhanh/<khu-vuc>/` hoặc `/dia-diem/<ten>/`; mỗi chi nhánh 1 URL — không tab JS/accordion chung 1 URL |
| Index status | Trang index được (check `site:` hoặc GSC nếu có); vấn đề crawl/canonical → route `technical-seo-audit` |
| Store locator | Có trang danh sách chi nhánh, link tới mọi location page |

## B. Yếu tố bắt buộc per trang

| # | Yếu tố | Ghi chú |
|---|---|---|
| 1 | NAP khớp GBP từng ký tự | Đối chiếu Bước 2 của SKILL |
| 2 | Embed map đúng tọa độ | Pin đúng địa điểm, không pin trụ sở chung |
| 3 | Giờ mở cửa | Khớp GBP, kể cả giờ lễ/Tết |
| 4 | LocalBusiness schema per chi nhánh | Chỉ flag đúng/thiếu — generate → `schema-markup-generator` (mỗi chi nhánh 1 node `@id` riêng) |
| 5 | CTA chi nhánh | Gọi/đặt lịch/chỉ đường về đúng chi nhánh |

## C. Yếu tố UNIQUE (chống thin duplicate) — cần ≥3/6

| # | Yếu tố | Vì sao |
|---|---|---|
| 1 | Đội ngũ riêng (bác sĩ/quản lý/kỹ thuật viên chi nhánh) | Attribute-value không copy được giữa các trang |
| 2 | Dịch vụ riêng có tại chi nhánh (kèm giá nếu công khai) | Chain hiếm khi đồng nhất 100% dịch vụ |
| 3 | Review đúng chi nhánh đó | Không trộn review toàn chuỗi; nguồn: GBP chi nhánh |
| 4 | Ảnh thật chi nhánh | Mặt tiền + không gian, không tái sử dụng ảnh chi nhánh khác |
| 5 | Chỉ đường + landmark địa phương | "Đối diện chợ X, cạnh trường Y" — nội dung không tự sinh hàng loạt được |
| 6 | FAQ/nội dung theo khu vực | Câu hỏi thật của khách khu vực đó (giữ xe, tuyến đường, giờ đông) |

< 3/6 yếu tố unique = ⚠️ thin-duplicate risk; chỉ khác địa chỉ = ❌.

## D. Internal linking

- Trang chủ + footer → store locator → mọi location page (không trang mồ côi).
- Location page → trang dịch vụ liên quan; trang dịch vụ → location page khu vực (2 chiều).
- Chain lớn (>10 chi nhánh): footer chỉ link locator + chi nhánh chính, tránh footer 50 link; chi tiết flow → skill `internal-linking`.

## E. Phân nhánh theo business type

| Type | Điều chỉnh |
|---|---|
| **SAB** | KHÔNG tạo "location page" cho địa chỉ ẩn; thay bằng **service-area pages** theo vùng phục vụ — nội dung phải chứng minh phục vụ thật ở vùng đó (case, review khách vùng đó), không mass-generate trang "dịch vụ X tại quận Y" rỗng (doorway page = vi phạm) |
| **Hybrid** | Location page cho điểm bán + khai service area trong GBP; không tạo trang vùng nếu không có evidence phục vụ |
| **Chain** | Full checklist A-D per chi nhánh + cross-branch consistency (gbp-checklist.md) |
