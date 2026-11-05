# Đọc field và lab đúng phạm vi

Đọc khi đánh giá báo cáo cũ hoặc trước khi kết luận khách thật nhanh/chậm.

1. Mỗi bảng ghi nguồn, URL/origin, mobile/desktop, ngày thu thập, cửa sổ thời gian và số mẫu nếu nguồn cung cấp. `loadingExperience.id` có thể cho biết phạm vi thực tế; không suy URL-level chỉ từ tên trường. Không có số mẫu thì ghi không được cung cấp.
2. CrUX p75 không đại diện mọi người dùng. Ngưỡng tốt: LCP ≤2,5 s, CLS ≤0,1, INP ≤200 ms, đánh giá theo thiết bị. LCP 2,66 s chưa đạt ngưỡng tốt. CrUX là cửa sổ trượt 28 ngày; dữ liệu cũ ảnh hưởng kết quả, nhưng điều đó không chứng minh mọi request hiện tại đã nhanh. [Web Vitals](https://web.dev/articles/vitals), [CrUX API](https://developer.chrome.com/docs/crux/api/).
3. RUM tự thu phải tách thiết bị và template, ngày, số mẫu hợp lệ, cách tính percentile, loại bot/probe và dữ liệu thiếu. Mẫu 88% desktop không dùng để bác bỏ vấn đề mobile. Không có raw/aggregate kiểm được thì gắn “chưa xác minh”, không sao số từ ảnh thành kết luận mới.
   - Kiểm mã collector: CLS có dùng session window, “INP” có chỉ là max Event Timing, và beacon có chỉ bật sau tương tác không. Tách beacon khỏi số người dùng, viewport khỏi thiết bị; ghi `valid_n` từng metric và cách xử lý giá trị 0. UA filter không loại hết lượt test dùng Chrome thường. Log đang xoay vòng: đọc đủ file cho cửa sổ đã ghi, chỉ xuất aggregate không IP/UA/URL riêng tư.
4. Lab CLS cao nhưng field CLS thấp: ghi “đã tái hiện trong điều kiện lab; field của phạm vi này thấp”. Không kết luận “chỉ tồn tại trong lab” hoặc “người dùng thật không chậm”. Khác thiết bị, mạng, cache, thời gian và độ phủ có thể giải thích chênh lệch. [CrUX methodology](https://developer.chrome.com/docs/crux/methodology).
5. Trước/sau lab: đủ lượt độc lập, trung vị + khoảng dao động, `fetchTime`, `benchmarkIndex`, đúng URL và cùng cache/device. Nếu máy PSI khác đáng kể hoặc kết quả mâu thuẫn, dùng đối chứng; không gom các JSON trả cùng phép đo thành nhiều lượt.
6. Giữ một bộ runner tự động và một nơi tổng hợp. Không gọi model đọc từng JSON thô hay đo lại chỉ để xác nhận con số đã đủ. Agent phụ chỉ khi được yêu cầu; có thể giao model rẻ đọc bảng, còn nguyên nhân và quyết định deploy dựa vào bằng chứng kỹ thuật.

## CLS khi CSS async đến muộn

- Xem filmstrip/rect và HTML thực tế để biết CCSS nào đang được dùng. `width`/`height` trên ảnh không bảo đảm ổn định nếu wrapper, display hoặc kích thước theo breakpoint đến muộn.
- Tái hiện cùng phần tử dịch trước khi sửa; lab không throttling có CLS 0 không bác bỏ PSI. Theo `cls-chi-psi-thay.md`.
- So tối đa hai phương án có căn cứ: bổ sung CSS màn đầu còn thiếu, hoặc bỏ async/CCSS trong phạm vi thích hợp. Không mặc định đổi cấu hình toàn site từ một URL.
- Staging tắt LiteSpeed nên không đại diện pipeline CSS production: dùng HTML tĩnh cùng tài nguyên để A/B. Config cấp site phải phủ nhiều template và trạng thái chưa/có CCSS trong hàng đợi; bản vá riêng hero kiểm cả desktop/mobile.
- Giữ lựa chọn hạ tầng ngoài scope (ví dụ HTTP/3). Báo byte nguồn, byte HTML và byte truyền qua mạng riêng.

## Loại script khỏi Delay JS

- Exclude khỏi Delay JS có thể biến script thành tài nguyên chặn hiển thị. Kiểm thẻ HTML sau optimizer, render-blocking audit, FCP/LCP và thứ tự thực thi; số thư viện bằng một chưa đủ.
- Giữ dependency và loại fallback tải trùng trước khi quyết định có cần exclude. Kiểm click đầu, tương tác sau khi chờ lâu, menu, slider và form. Không đổi sang async nếu inline còn phụ thuộc thứ tự.
- Ca thực tế 05/11/2026: thêm exclude jQuery/Slick làm xuất hiện khoảng 41 KB script blocking, trước đó không có. Trang Giới thiệu giảm trung vị 98→94, LCP tăng 375 ms ở lô đo đầu. Máy PSI khác nhau; lượt có benchmark gần nhau cũng chậm hơn nên phải điều tra, không gán hết cho nhiễu. Ước tính tiết kiệm trong audit không phải hiệu quả chắc chắn của patch.
- Có hồi quy mới hoặc sửa thứ tự JS toàn site thì đo lại phạm vi bị ảnh hưởng sau sửa. Giữ riêng JSON của các lô; không dùng số của nguồn cũ làm kết quả cuối.
