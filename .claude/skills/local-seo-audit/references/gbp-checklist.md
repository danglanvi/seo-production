# GBP Optimization Checklist — chi tiết per mục

> Dùng bởi `local-seo-audit` Bước 1. Mỗi item: cách kiểm theo DATA TIER + tiêu chí ĐẠT. Chain: chạy per chi nhánh, thêm cột consistency cross-branch.
> Ký hiệu tier: [T1] DataForSEO Business Data API · [T2] quyền quản trị GBP (Insights/dashboard) · [T3] xem public trên Maps ẩn danh.

## 1. Categories

| Item | Cách kiểm | Tiêu chí ĐẠT |
|---|---|---|
| Primary category | [T1/T3] xem listing; [T3] công cụ xem category ẩn: xem source Maps hoặc so hiển thị | = dịch vụ chính tạo doanh thu, cụ thể nhất có thể ("Phòng khám nha khoa" không phải "Phòng khám") |
| Secondary categories | [T2] dashboard; [T3] suy từ dịch vụ hiển thị | Phủ các dòng dịch vụ phụ có thật; không nhồi category không làm |
| So với đối thủ | Lấy category 3-5 đối thủ top map pack (từ `map-pack-intelligence` hoặc xem tay) | Primary category mình xuất hiện trong nhóm thắng; lệch hẳn → ⚠️ CẦN XEM (có thể là lý do không vào pack) |

⚠️ Đổi primary category là thay đổi mạnh — luôn kèm Falsifiability + cửa sổ theo dõi 2-4 tuần + điều kiện revert.

## 2. Attributes

- [T2] Rà hết attribute list theo category (thanh toán, chỗ đậu xe, accessibility, đặt chỗ, phù hợp trẻ em…). [T3] chỉ thấy attribute đang hiển thị → mục chưa khai ghi ⬜.
- ĐẠT: mọi attribute áp dụng đều khai; KHÔNG khai attribute sai thực tế (❌ trust risk, khách đến thất vọng → review xấu).

## 3. Mô tả (Business description)

- ≤750 ký tự; 250 ký tự đầu chứa: [[Central Entity]] (tên đúng biển hiệu) + dịch vụ chính + khu vực phục vụ.
- Không nhồi keyword, không ALL CAPS, không URL, không thông tin khuyến mãi (dùng Posts).
- Chain: mô tả per chi nhánh nêu điểm riêng chi nhánh, không copy nguyên chuỗi.

## 4. Photos

| Check | Tiêu chí ĐẠT |
|---|---|
| Số lượng | ≥ mức đối thủ map pack (đếm tay [T3] hoặc [T1]); nghèo hơn hẳn = ⚠️ |
| Geo-context | Có ảnh mặt tiền nhận diện được vị trí (biển hiệu + bối cảnh phố), ảnh không gian trong thật |
| Chất lượng | Không stock photo, không watermark bên thứ ba, đủ sáng; logo + cover đúng brand hiện hành |
| Tươi mới | Có ảnh trong 6 tháng gần nhất (khách + owner upload) |
| Chain | Ảnh đúng chi nhánh — ảnh chi nhánh A gắn listing B = ❌ |

## 5. GBP Posts cadence

- [T2] xem lịch sử post; [T3] xem tab Updates public.
- ĐẠT: nhịp đều (baseline hàng tuần — điều chỉnh theo ngành, đây là baseline vận hành GTV chưa phải ngưỡng chốt từ nghiên cứu); loại post khớp mùa vụ (offer dịp lễ, update dịch vụ mới); post gần nhất ≤30 ngày.
- Đứt nhịp >90 ngày = ⚠️ (listing trông "chết" với người xem — frame lợi ích theo conversion, KHÔNG claim post là ranking factor).

## 6. Q&A seeding

- [T3] xem tab Hỏi & Đáp: câu hỏi phổ biến (giá, giờ, đặt lịch, chỗ đậu xe) đã được owner seed + tự trả lời chưa.
- Câu hỏi của khách chưa ai trả lời / người lạ trả lời sai = ❌ (owner mất quyền narrative).
- Nội dung seed = câu hỏi khách hỏi thật (lấy từ sales/CSKH), trả lời ngắn + trỏ về trang liên quan.

## 7. Products / Services section

- Khai đủ dịch vụ chính với mô tả riêng; giá công khai được thì để giá (tăng qualify click).
- Tên service = ngôn ngữ khách tìm, không tên nội bộ.
- Chain: services đúng những gì chi nhánh đó có.

## 8. Booking / action links

- Link đặt lịch/đặt bàn/menu/chat hoạt động (click thử), không 404, không về trang chủ chung khi có landing chi nhánh.
- UTM cho link từ GBP để đo (route setup đo lường → `gtv-client-report` layer).

## Cross-branch consistency (chỉ chain)

| Check | Tiêu chí |
|---|---|
| Naming convention | "Brand - Chi nhánh Quận X" nhất quán mọi listing; đúng biển hiệu thật |
| Ownership | Mọi listing trong cùng 1 tài khoản/Location Group quản trị |
| Category set | Primary giống nhau trừ khi chi nhánh khác model kinh doanh |
| Website link | Mỗi listing → đúng location page của nó, không cùng về homepage |
| Giờ mở cửa | Đúng per chi nhánh, cập nhật giờ lễ |
