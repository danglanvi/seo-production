# Sổ quyết định và sổ lệnh của workstream

Mục đích: giữ lời Lead nguyên văn và lệnh đã chạy được qua compact và qua phiên mới. Đọc file này khi tạo `decisions.md` hoặc `_tools/RECIPES.md` cho một workstream.

Nguồn lỗi: 40 lần mất ngữ cảnh sau compact (134 phút) và 12 lần đọc lại ngữ cảnh (74 phút) trên 10 phiên, 17–20/10/2026. Agent hỏi lại điều đã chốt 8 lần trong 17–19/10/2026. Đề xuất hs-6, báo cáo `Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-skill-review_bao-cao_v1.md` mục 4.

## 1. Vị trí

- Đặt cả hai file trong thư mục workstream, cạnh `HANDOFF.md`: `<workstream>/decisions.md` và `<workstream>/_tools/RECIPES.md`.
- Không đóng gói nội dung hai file vào skill. Nội dung là fact riêng của từng site.
- Trong HANDOFF, chỉ trỏ tới hai file. Không chép nội dung vào HANDOFF.
- Lệnh `handoff.py prompt` tự thêm đường dẫn hai file vào prompt khi file có mặt cạnh HANDOFF.
- Nếu repo dùng chung với team, chỉ ghi nội dung team được đọc. Luật gốc: `_REFERENCE/luat-duyet-dieu-phoi.md` mục HANDOFF THEO WORKSTREAM.

## 2. decisions.md: lời Lead nguyên văn

1. Ghi ngay khi nhận lời chốt của Lead, trước khi làm việc kế.
2. Mỗi mục có 4 phần: giờ `dd/mm/yyyy HH:MM`, thẻ hoặc chủ đề, câu nguyên văn trong ngoặc kép, nguồn.
3. Lấy giờ của tin bằng `transcript_recall.py user <id> --last 3`. Script in `dd/mm HH:MM`, nên thêm năm khi chép. Không gõ giờ theo trí nhớ.
4. Không tóm tắt câu của Lead. Nếu cần diễn giải, thêm dòng riêng bắt đầu bằng "Hiểu là:".
5. Nếu Lead đổi ý, thêm mục mới có chữ "thay mục <giờ cũ>". Không xoá mục cũ.
6. Không ghi secret, nội dung journal, số nhạy cảm ngoài scope.

Mẫu:

```md
## [site: site-mau] 20/10/2026 20:45 · <thẻ hoặc chủ đề>
"<câu nguyên văn của Lead>"
Nguồn: chat phiên <8 ký tự đầu của id phiên>.
Hiểu là: <một câu, chỉ khi câu gốc cần diễn giải>.
```

Ghi chú "đã duyệt" trong `decisions.md` chỉ là lịch sử. Ghi chú này không cấp quyền gửi hay publish mới.

## 3. _tools/RECIPES.md: sổ công thức lệnh

1. Ghi ngay sau lần đầu một lệnh có ích chạy thành công.
2. Mỗi lệnh có 3 dòng: khi nào dùng, lệnh nguyên văn, bẫy.
3. Không ghi secret, host staging, slug đăng nhập, IP hay mật khẩu vào lệnh. Dùng biến môi trường hoặc tên script để đọc giá trị lúc chạy.
4. Trước khi báo xong, chạy `bash tools/leak_scan.sh <thư mục workstream>`. Mã 1 nghĩa là file có lộ: sửa rồi chạy lại.
5. Nếu lệnh đổi, sửa đè 3 dòng tại chỗ và ghi bẫy mới.

Workstream web nên có công thức cho các việc sau:

- gọi trang staging và chụp staging;
- deploy lên staging;
- nạp thẻ lên trang duyệt, kèm schema của một thẻ mẫu;
- purge Cloudflare (ghi tên script, không ghi token);
- đăng nhập `gws`;
- pipeline Jev: dump dữ liệu, embedding, gọi Jev, kiểm kết quả.

Mẫu:

```md
## [site: site-mau] Chụp trang staging
- Khi nào: kiểm giao diện trên staging trước khi báo xong.
- Lệnh: `bash <script chụp của workstream> /duong-dan-trang/`
- Bẫy: <lỗi đã gặp và cách tránh>.
```

## 4. Sau compact

1. Trả lời bằng tiếng Việt có dấu.
2. Đọc `HANDOFF.md`, rồi `decisions.md`, rồi `_tools/RECIPES.md`.
3. Nếu cần lời Lead hoặc lệnh đã chạy trước compact, dùng `transcript_recall.py`. Không grep hay đọc thẳng file transcript `.jsonl`, vì file có thể nặng hơn 20 MB.
4. Nếu tìm thấy lời chốt chưa có trong `decisions.md`, ghi bổ sung theo mục 2.
