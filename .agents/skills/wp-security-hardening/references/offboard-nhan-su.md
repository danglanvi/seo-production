# Thu hồi quyền khi nhân sự nghỉ (nhánh D)

Nguồn: rà tài khoản Cloudflare của site agency mẫu ngày 26/10/2026. Hai email nhân sự đã nghỉ vẫn là Super Administrator ở 2 tài khoản Cloudflare giữ zone site chính, chưa bật 2FA. Một email đã bị xoá khỏi Google Workspace từ trước.

Ranh giới: agent đọc, lập danh sách, viết hướng dẫn và kiểm lại sau khi người dùng làm. Người dùng tự bấm xoá thành viên, đổi mật khẩu, bật 2FA, xoá token. Agent không gõ mật khẩu thay người dùng.

## 1. Thứ tự

1. Đặt chuyển tiếp email trước. Link đặt lại mật khẩu của các hệ thống gửi về hộp thư của nhân sự cũ.
2. Không Suspend user Google Workspace khi còn cần nhận mail. User bị Suspend không nhận mail, nên chuyển tiếp cũng dừng.
3. User Workspace đã bị xoá: thêm email đó làm alias của tài khoản quản trị, để nhận cảnh báo bảo mật và mail đặt lại mật khẩu.
4. Rà từng hệ thống ở mục 2. Xoá user Google không xoá login ở hệ thống có đăng nhập riêng (Cloudflare, Bunny, panel hosting). Login đó vẫn đăng nhập được bằng mật khẩu cũ, và mọi API token của nó vẫn chạy.
5. Với login còn giữ: đổi mật khẩu, bật 2FA, đổi API key toàn cục, lưu recovery code vào vault.
6. Mời tài khoản quản trị hiện hành làm Super Administrator ở mọi tài khoản CDN, rồi bật 2FA cho chính tài khoản đó. Lỗi đã gặp: tài khoản quản trị là Super admin ở cả 2 tài khoản Cloudflare mà chưa bật 2FA.
7. Kiểm lại trên dashboard sau khi người dùng làm: danh sách thành viên, trạng thái 2FA, danh sách token. Ghi kết quả vào báo cáo và HANDOFF.

## 2. Hệ thống cần rà

| Hệ thống | Kiểm gì |
|---|---|
| Google Workspace | Role admin, chuyển tiếp mail, alias của user đã xoá |
| Cloudflare | Thành viên mọi account, 2FA, User API Token của từng login, Global API key, Worker và route lạ (`references/ra-tai-khoan-cdn.md`) |
| CDN khác (Bunny…) | Thành viên, API key, cài đặt pull zone đổi gần đây |
| Panel hosting (aaPanel, cPanel), portal nhà cung cấp VPS | Tài khoản, 2FA, API, log đăng nhập |
| WordPress | Admin, app password, user có email của người nghỉ. Bài đứng tên người nghỉ giữ nguyên, chỉ khoá đăng nhập |
| GSC, GA4, GTM | User và quyền trên property, container |
| GitHub | Thành viên org, collaborator của repo, deploy key, token |
| `.agent-secrets/` | Key do người nghỉ tạo hoặc giữ: đổi và cập nhật file |

## 3. Quyết định của Lead

- Giữ login cũ (đã đổi mật khẩu, bật 2FA) hay gỡ khỏi tài khoản. Giữ thì cần recovery code trong vault và alias email còn nhận mail.
- Token, tài khoản thuộc site khách trên cùng tài khoản CDN: hỏi trước khi xoá. Token có lần dùng cuối lâu ngày vẫn có thể là của khách.
