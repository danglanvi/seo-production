# Audit Entity theo GEO — chế độ độc lập GE-11…15

Mục đích: chấm nguồn sự thật thương hiệu, không cần template SEO Production. Nguồn: master tier-1-geo.md v2.0.3; patch review 12/09/2026. Đọc audit-contract.md cùng thư mục để chấm trạng thái, scope và gate.

## Input và cách lấy

Brand/domain, engine mục tiêu, danh sách trang và câu hỏi thương mại user giao; mẫu gợi ý 5–10 câu từ sales/CSKH, không tự bịa thông tin brand. Nhận bảng sự thật đã được chủ brand xác nhận (tên, NAP, mô tả, năm thành lập, phạm vi phục vụ) hoặc ghi UNKNOWN phần chưa có chuẩn đối chiếu. Dữ liệu lấy từ web có ngày, hoặc user dán/export; không cần truy cập tài liệu riêng ngoài scope.

## Tiêu chí và evidence

| GE | ĐẠT khi | Evidence / thiếu thì |
|---|---|---|
| GE-11 | Mỗi câu thương mại trong scope có trang chính chủ trả lời bằng text đọc được. Câu hỏi giá: có thông tin giá/điều kiện báo giá giúp trả lời câu hỏi; một nút liên hệ đơn thuần không phải câu trả lời. Không bắt công bố giá nhạy cảm hoặc tự tạo dải giá | Câu hỏi → URL → đoạn trả lời → ngày/cách lấy. site: là cách tìm, không thấy kết quả thì kiểm trực tiếp sitemap/trang; chỉ kết luận thiếu sau kiểm phù hợp, không coi site: là toàn bộ index |
| GE-12 | Có và cập nhật các trang about, giá, FAQ, docs/hướng dẫn, chính sách phù hợp loại doanh nghiệp; docs vẫn hữu ích dù không rank | URL + nội dung + ngày. Nếu có AI answer: lưu prompt/engine/ngày/URL bị bịa, kiểm 404 và đích đúng; không tự tạo redirect |
| GE-13 | Thông tin cốt lõi khớp bảng sự thật đã xác nhận trên những kênh áp dụng | Website/GBP/social/danh bạ/review → thuộc tính → giá trị → lệch gì. Không có GBP do không đủ điều kiện local thì kênh đó N/A, không làm toàn item FAIL |
| GE-14 | Entity Home rõ; Organization/Person phù hợp; sameAs là hồ sơ chính chủ; @id nối đúng entity giữa các trang | JSON-LD + URL profile/Entity Home. Validate cú pháp và graph; Rich Results Test chỉ kiểm tính năng Google hỗ trợ, không thay kiểm toàn bộ schema. Không hứa schema tăng citation |
| GE-15 | Bài trọng điểm có tác giả thật, nguồn xác nhận chuyên môn và kinh nghiệm nằm trong nội dung khi phù hợp; không chỉ box bio | URL bài + URL author + đoạn kinh nghiệm có nguồn; không bịa trải nghiệm/số để đạt. Thiếu toàn văn hoặc xác nhận tác giả → UNKNOWN |

Không áp quota mới về số trang tác giả hay lượng trải nghiệm. Khi nguồn/intent cần ngoại lệ, nêu rõ phạm vi thay vì tự tick. Crawl/index/AI đọc lại đúng chỉ chứng minh hiện trạng tương ứng, không chứng minh một tactic có hiệu quả nhân quả.

## Output

Repo Production: `14-entity/<CLIENT>_geo-entity-audit_vN.md`; standalone: `outputs/<brand>_geo-entity-audit_vN.md` hoặc thư mục user giao. Mỗi dòng: GE · scope · status · evidence có ngày · việc sửa/lấy data · owner · acceptance_check. Kết: G-ENT [GEO] = GE-11 theo PASS/FAIL/UNKNOWN; điểm/độ phủ 5 item; không ghi vào gate EN khi chạy riêng. GE-11 chưa PASS vẫn có thể spot-check bài, chưa mở đợt tối ưu hàng loạt phụ thuộc gate.
