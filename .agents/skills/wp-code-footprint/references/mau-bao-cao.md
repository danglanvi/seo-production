# Mẫu báo cáo audit footprint và prompt cho reviewer ngoài

## 1. Khung báo cáo `<site>_footprint-audit_v1.md`

1. **Kết luận** (5–6 câu): lỗi người duyệt thấy có thật không, trên bao nhiêu trang; nguyên nhân gốc; code thừa lớn hơn phần comment; semantic HTML đúng/thừa/sai; DB có sạch không; phương án mấy bước, bước 0 mất bao lâu.
2. **Vì sao xảy ra**: cơ chế sinh lỗi (luật lane, cách agent ghi chú, cờ tắt minify, cổng kiểm thiếu mục, luật cấm chạm template).
3. **Số liệu tổng**: bảng chỉ số → giá trị → nguồn (file quét, agent, Jev).
4. **Phát hiện theo mức** Cao/Trung/Thấp: mã, phát hiện, bằng chứng file:dòng, ảnh hưởng, cách sửa.
5. **Semantic HTML5**: đúng (giữ) / thừa (không hại SEO, hại bảo trì) / sai (mức thấp) / ảnh hưởng thật. Nói thẳng: công cụ tìm kiếm không xếp hạng theo số section hay landmark.
6. **Jev và EmbeddingGemma đã làm gì**: bảng việc → model → input → kết quả → ngưỡng; chi phí.
7. **Phương án**: bảng bước → việc → ngày công → rủi ro → kết quả; luật mới đề xuất.
8. **Chờ người duyệt quyết**: danh sách đánh số.
9. **Giới hạn của audit**: biến thể cache, scanner đếm thừa, chưa đo coverage, chưa xác minh.
10. **Tệp bằng chứng**.

## 2. Khung handoff sau khi dọn `<site>_footprint-fix_handoff_v1.md`

1. Kết luận: làm gì, kết quả số, lỗi production.
2. Bảng trước → sau trên cùng bộ URL và cùng biến thể cache (`compare.py`), kèm Jev trước/sau.
3. Mỗi lane: file đổi, cách chứng minh chỉ comment đổi, backup và lệnh rollback, kiểm sau áp.
4. Việc chưa làm và lý do (kèm mức rủi ro).
5. Chỗ audit sai mà lane phát hiện (ví dụ file bị gọi chết nhưng vẫn in).
6. Cách reviewer tự kiểm: URL, lệnh grep/curl, con số mong đợi.
7. Prompt cho reviewer ngoài (mục 3).

## 3. Prompt cho reviewer ngoài (ChatGPT hoặc người)

```text
Bạn là reviewer độc lập cấp senior về WordPress, front-end performance, semantic HTML5, WCAG và technical SEO. Bạn không viết code. Việc của bạn là phản biện một bản audit và một đợt dọn do AI làm trên website <site>.

Bối cảnh: <stack>; trong <khoảng ngày> nhiều phiên AI đã sửa site; người vận hành thấy comment nội bộ lọt ra view-source, ví dụ: <2–3 trích dẫn>. Đính kèm: <audit>, <handoff trước/sau>, <báo cáo agent>.

Việc:
1. Kiểm chứng độc lập trên site sống: mở view-source ≥ 5 URL <danh sách>, tự đếm khối script/style inline và byte, comment tiếng Việt trong code, !important, section không heading, landmark. So với bảng của audit và của handoff. Ghi chỗ lệch. Lưu ý site trả 2 biến thể cache theo header Accept image/webp; nói rõ bạn xem bản nào.
2. Phản biện từng phát hiện (mã C/T/L): đúng / đúng một phần / sai / không kiểm được, lý do 1–2 câu. Soi riêng: ảnh hưởng SEO của section/landmark; HTML nặng cho bot có ảnh hưởng CWV không; trade-off khi chuyển CSS inline ra file; rủi ro của link giả span role=link; skip link và tabindex=-1 trên main; MutationObserver toàn body.
3. Tìm thứ audit bỏ sót trên 5 URL: footprint khác, lỗi HTML validator, lỗi axe, schema, link hỏng, tài nguyên tải trùng.
4. Phản biện đợt dọn: thay đổi nào có thể đổi hành vi dù lane nói "chỉ comment đổi"; việc gộp mu-plugin có rủi ro thứ tự hook không; purge và làm nóng đã đủ chưa; rollback có chạy được không.
5. Phản biện phương án còn lại và luật mới. Độ tin cậy của Jev/Gemma trong audit này.

Định dạng: tiếng Việt có dấu, câu ngắn. Phần 1 bảng số liệu có cột "lệch so với audit". Phần 2 bảng mã → phán quyết → lý do. Phần 3 danh sách có URL + bằng chứng + mức. Phần 4–5 prose ngắn. Cuối cùng: 5 việc bạn làm đầu tiên nếu là dev của site, xếp theo lợi ích trên rủi ro. Không kiểm được thì ghi "không kiểm được" và lý do. Không đoán số.
```
