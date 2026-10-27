# Rà tài khoản Cloudflare, CDN và xử lý secret bị lộ

Đọc ở nhánh C (Bước 1). Nguồn: sự cố trên tài khoản Cloudflare của site agency mẫu, phát hiện 26/10/2026. Kẻ tấn công dùng token API để gắn Worker độc lên 9 zone từ 07/2026. Worker trả trang CAPTCHA giả kiểu ClickFix cho khách trình duyệt, trả trang thật cho Googlebot và curl. Apex của 8 zone để DNS only nên Worker gần như không chạy với khách thật.

Trong file này, Lead là người duyệt. Người dùng là người có quyền đăng nhập tài khoản CDN. Hai vai có thể là một người.

## 1. Ranh giới

- Agent chỉ đọc cấu hình, audit log, mã Worker, rồi lập danh sách việc cần bấm.
- Người dùng tự bấm mọi việc xoá và đổi bảo mật:
  - Xoá Worker, route, token.
  - Roll Global API Key.
  - Đổi mật khẩu.
  - Bật 2FA.
  - Gỡ thành viên.
- Có hai lý do:
  - Lý do 1: các việc này khó đảo ngược.
  - Lý do 2: bộ lọc an toàn của Claude Code chặn thao tác xoá và đổi bảo mật trong tài khoản, qua API lẫn giao diện (site agency mẫu 26/10/2026).
- Trang đang hiện token hay key: agent chỉ bấm nút Copy. Không đọc text trang, không chụp màn hình trang đó.

## 2. Đọc gì

Đọc bằng token có quyền đọc, hoặc bằng API của dashboard trong phiên Chrome người dùng đã đăng nhập. Ghi mỗi mục vào `evidence-<đợt>/cdn-account.md`, che IP và giá trị secret.

| Mục | Đọc | Dấu hiệu lạ |
|---|---|---|
| Worker | Tên, ngày tạo, ngày sửa, sha256 mã, domain mã gọi tới | Tên ngẫu nhiên dạng `tu-tu-xxxx`; mã gọi domain lạ; mã có chữ Adspect, "Verify you are human" |
| Route Worker | Route của mọi zone | Route `<apex>/*` không ai nhớ đã tạo |
| Token API | Tên, quyền, ngày tạo, lần dùng cuối | Tên "(auto) <ngày>" hay "auto-<số>"; quyền ghi Workers, Zone, DNS; dùng gần đây mà không ai nhận |
| Thành viên | Email, vai trò, 2FA | Tài khoản đối tác cũ; Super Administrator chưa bật 2FA |
| Audit log | Thao tác, nguồn (API hay giao diện), IP, giờ | Thao tác Worker và route từ IP nước ngoài, qua API |
| SSL theo host | Chế độ SSL, TLS tối thiểu, Configuration Rule | Flexible; TLS 1.0 |
| Tài nguyên khác | Pages, R2, Access, webhook, chuyển tiếp email, DNSSEC | Tài nguyên không ai nhận; CNAME trỏ dịch vụ đã bỏ (có thể bị chiếm) |

## 3. Kiểm từ ngoài

- Gọi trang qua edge hai lần. Lần 1: gửi UA của Chrome, không gửi header Accept. Lần 2: gửi UA của Googlebot.
- So nội dung hai lần gọi. Trang giả chỉ hiện cho UA trình duyệt.
- Kiểm Google Safe Browsing cho các domain.
- Ghi apex nào bật proxy. Worker chỉ chạy trên tên đang proxy. Không bật proxy khi Worker độc còn. Khách trình duyệt có thể nhận trang giả.

## 4. Danh sách người dùng bấm

Viết theo mức ưu tiên, mỗi dòng có link trang dashboard và tên đúng của mục cần xoá:

1. Ngay:
   - Xoá token lạ.
   - Roll Global API Key.
   - Xoá Worker độc (route tự mất).
   - Đổi mật khẩu tài khoản Cloudflare.
   - Đổi mật khẩu hộp thư nhận link đặt lại mật khẩu.
2. Sau đó: bật 2FA cho thành viên còn thiếu, gỡ thành viên không còn làm việc, xoá token cũ không dùng.
3. Cấu hình: SSL Full (strict), TLS tối thiểu 1.2 trước khi bật proxy.

Trước khi đề xuất, liệt kê nơi dùng mọi key và token. Roll Global API Key và xoá token có thể làm hỏng plugin hay script đang dùng key cũ. Site agency mẫu: người dùng xoá cùng lúc 2 token của plugin trên 2 site khách, nên phải tạo token mới.

Sau khi người dùng bấm: đọc lại route, Worker, token và chạy lại phép kiểm mục 3.

## 5. Secret bị lộ vào transcript, chat hay file

Ca thật 10/2026:

- Key CDN dán vào chat.
- Một lane in DeploymentKey của CDN.
- Một lane in mật khẩu Redis 2 lần.
- Một agent đọc trang dashboard đang hiện token.

1. Dừng việc đang làm. Không in lại giá trị.
2. Báo Lead ngay trong chat: tên secret (không ghi giá trị), nơi lộ (phiên, file, kênh chat), giờ.
3. Đề xuất đổi. Lead quyết đổi hay giữ. Giữ thì ghi rủi ro và người quyết vào báo cáo.
4. Người dùng đổi trên trang nhà cung cấp. Agent chỉ bấm nút Copy nếu được nhờ.
5. Agent ghi giá trị mới vào `.agent-secrets/.env` bằng code đọc clipboard hoặc stdin, không in. Kiểm bằng một lệnh chỉ đọc, ví dụ lệnh liệt kê quyền của token.
6. Rà nơi dùng giá trị cũ: cron, plugin, script, cấu hình server. Cập nhật từng nơi, kiểm từng nơi.
7. File có giá trị cũ: thay giá trị bằng `***`. File đã đồng bộ ra ngoài máy (Git, Drive): báo Lead để quyết cách xử lý bản đã đồng bộ.
8. Ghi vào báo cáo: tên secret, giờ lộ, giờ đổi, nơi đã cập nhật. Không ghi giá trị.

Để phòng trước: khi lane đọc cấu hình hoặc response API, pipe output qua `skills/web-lane-orchestration/scripts/che_secret.py --ip` (chỉ khi workspace có skill đó). Redis dùng biến `REDISCLI_AUTH`, không truyền `-a`.
