# Mode core update: tụt hoặc tăng quanh một đợt core update của Google

Dùng mode này khi traffic hoặc hiển thị của site đổi mạnh trong khoảng một đợt core update. Mode decay thường không dùng được ở đây: decay là sụt dần theo từng bài, còn core update đổi đánh giá trên nhiều trang cùng lúc.

Nguồn: Google, "Core updates and your website", https://developers.google.com/search/docs/appearance/core-updates (cập nhật 31/12/2025). Quy trình phỏng theo `references/core-update.md` của skill eeat-helpfulness-assessment (Aleyda Solis, bản 1.2.1, 29/10/2026). Đọc lại trang Google trước mỗi lần audit thật.

## Google nói gì (diễn giải, không trích nguyên văn)

- Phần lớn site không cần làm gì. Core update rộng và không nhắm vào site cụ thể.
- Xác nhận ngày bắt đầu và kết thúc trên Google Search Status Dashboard. Chờ ít nhất 1 tuần đủ sau khi update xong. So tuần đó với tuần trước khi update bắt đầu trong Search Console. Tách Web, Image, Video, News.
- Tụt nhẹ (ví dụ vị trí 2 xuống 4) không cần đổi lớn. Tụt mạnh (ví dụ 4 xuống 29) cần rà toàn site: nội dung có hữu ích, đáng tin, viết cho người đọc không. Nên nhờ người ngoài, không liên quan, đánh giá.
- Không sửa vội. Cải thiện, viết lại hoặc sắp lại nội dung. Xoá là lựa chọn cuối cho nội dung không cải thiện được.
- Một số thay đổi thấy sau vài ngày. Hệ thống cần nhiều tháng để ghi nhận cải thiện. Có thể phải chờ đợt core update sau. Không bảo đảm phục hồi.

## Quy trình

1. **Xác định thay đổi.**
   - Lấy GSC page × query (click, hiển thị, vị trí) cho 2 cửa sổ: tuần trước update, tuần đủ sau khi update xong.
   - Loại nguyên nhân khác trong cùng giai đoạn: lỗi tracking, migration, mùa vụ, SERP feature mới, AI Overviews và AI Mode, manual action, spam update.
   - Không có GSC export thì xin export và ghi "chẩn đoán tạm".
2. **Chia nhóm.** Gom trang theo template, cụm chủ đề, loại nội dung, tác giả hoặc chuyên mục. Tìm nhóm mất nhiều nhất. Đổi vị trí nhỏ không đủ để kết luận lỗi chất lượng.
3. **Chọn mẫu thắng và thua.**
   - 5–10 trang mất nhiều nhất.
   - 3–5 trang cùng loại giữ hoặc tăng, ưu tiên cùng site và cùng query.
   - 2–3 trang ngoài đang vượt trang thua ở query chính.
4. **Chấm từng trang mẫu** bằng checklist Aleyda: preset `core` + `core_update` + preset theo loại trang (`skills/semantic-content-audit/references/eeat-aleyda.md`). Chấm check Site và Workflow một lần. Cả site: chạy `eeat-site-qc` với preset `core_update`.
5. **Tìm mẫu hình, không tìm lỗi đơn lẻ.**
   - So tần suất và mức nặng của phát hiện có bằng chứng giữa nhóm thua và nhóm thắng.
   - Ghi phản ví dụ: trang thắng cũng có lỗi đó.
   - Lỗi nặng về độ đúng, an toàn, niềm tin thì sửa cả trên trang thắng.
   - Khác biệt chỉ là giả thuyết, không chứng minh update gây ra thay đổi.
6. **Báo cáo.** Thêm mục "Phân tích thay đổi" trước danh sách phát hiện chính, gồm:
   - cửa sổ đã so;
   - nhóm mất nhiều nhất;
   - mẫu hình tìm thấy;
   - nguyên nhân khác đã loại hoặc chưa loại.

   Ghi rõ: mẫu hình là tương quan, chưa phải nguyên nhân đã chứng minh.

## Đề xuất

- Ưu tiên cải thiện cả site về độ hữu ích, nội dung riêng, bằng chứng tự làm, độ đúng và niềm tin, hơn là chỉnh từng trang.
- Không đề xuất: xoá hàng loạt, đổi ngày cho đẹp, thêm bio tác giả khi không có chuyên môn thật, viết thêm chữ cho đủ số từ.
- Đặt kỳ vọng: đo theo tháng; theo dõi tỷ lệ hoàn thành việc và chuyển đổi, không chỉ thứ hạng.
