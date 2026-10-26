# Ghi lên Google Search Console

Đọc file này khi cần nộp lại sitemap lên GSC (sau Bước 4c, hoặc sau khi đổi index chuyên mục), hoặc khi cần biết việc nào API không làm được. Nộp sitemap là thay đổi hướng ra ngoài: Lead hoặc Vincent duyệt từng lần. Gốc đường dẫn là root repo.

## 1. Quyền và property

- `tools/gsc/gsc.sh` dùng token của `gws` với scope `webmasters.readonly`. Lệnh ghi bằng token này trả 403.
- Nộp sitemap cần tài khoản có quyền Full user (`siteFullUser`) hoặc Owner trên property. Dùng service account của người vận hành (tầng C của `_SETUP/SETUP-MAY.md`, file key nằm ngoài repo). Chủ property thêm email service account làm Full user trên GSC.
- Kiểm quyền trước khi ghi: gọi `GET https://www.googleapis.com/webmasters/v3/sites` bằng service account, đọc `permissionLevel` của property.
- Dùng đúng dạng property đã share. Property `sc-domain:` trả 403 khi tài khoản chỉ có property URL-prefix. Ghi dạng property của từng site vào hồ sơ site (`00-client-context/`), không ghi vào skill.

## 2. Nộp sitemap

1. Lấy access token của service account với scope `https://www.googleapis.com/auth/webmasters`.
2. Gọi `PUT https://www.googleapis.com/webmasters/v3/sites/{property}/sitemaps/{feedpath}`. Mã hoá URL cả `property` và `feedpath`. Thành công trả 204, không có thân.
3. Kiểm bằng `GET .../sitemaps/{feedpath}`: `lastSubmitted` phải là mốc vừa nộp. Đọc thêm `isPending`.
4. Ghi mã HTTP và `lastSubmitted` vào HANDOFF của workstream. Không ghi token.

Ví dụ (site agency mẫu, 18/10/2026): service account có `siteFullUser`. Nộp lại `sitemap_index.xml` và `category-sitemap.xml`, cả hai trả 204.

`gsc.sh` chưa có lệnh `submit-sitemap`. Khi lệnh này có, dùng lệnh đó thay cho bước 1–3.

## 3. Việc API không làm được

- Request indexing: URL Inspection API chỉ đọc. Indexing API của Google chỉ nhận trang JobPosting và BroadcastEvent. Làm trên giao diện GSC bằng Chrome đã đăng nhập, sau khi người duyệt đồng ý.
- Manual actions và Security issues: nhờ người có quyền kiểm tay trên GSC (Bước 2 của SKILL.md).

## 4. Bẫy khi đọc

- `gsc.sh coverage` gọi URL Inspection tuần tự, khoảng 2 lượt mỗi giây. Lô lớn: chạy nền và giữ trong quota 2.000 URL mỗi ngày mỗi property.
- stdout của `gws` có dòng "Using keyring backend" trước JSON. Cắt từ ký tự `{` đầu tiên trước khi parse.
