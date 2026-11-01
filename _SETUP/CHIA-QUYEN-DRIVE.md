# Chia quyền Drive cho robot

> Ai cũng đọc được: người mới cần biết xin gì, Lead cần biết cấp gì.
>
> Chỉ áp cho repo dùng robot. Đi bằng `gws` (bắt buộc mọi repo) thì file share cho domain công ty là đủ.

## Nguyên tắc

**Mặc định xin Editor. Viewer chỉ khi luật của repo nói rõ là chỉ-đọc.**

Vì sao Editor là mặc định: robot làm việc qua hai đường, và một trong hai đường có ghi.

| Đường | Ghi hay đọc | Quyền tối thiểu |
|---|---|---|
| Script Python trong repo (`fetch_*`, `ingest-drive-links`, `capture_*`…) | **Chỉ đọc** — mọi script hiện tại dùng scope `.readonly` | Viewer đủ |
| MCP `google-sheets` (AI thao tác sheet trực tiếp trong phiên) | **Ghi** — tạo tab, cập nhật ô, dựng bảng | Bắt buộc Editor |

Cấp Viewer thì phần đọc chạy êm, đến lúc AI cần ghi mới lỗi `403 insufficientPermissions` — lỗi rơi
vào giữa chừng công việc, sau khi đã tốn thời gian, và thông báo lỗi không nói rõ là do quyền. Xin
Editor ngay từ đầu tránh được cả lớp sự cố đó mà không mất gì thêm.

**Ngoại lệ cố ý — giữ Viewer:** workbook mà luật của repo quy định *người gõ, hệ chỉ đọc*. Ví dụ
sheet «Theo dõi dự án» của skill `acc-review-du-an` (Account Production `CLAUDE.md` §9). Ở đó Viewer
là đúng và phải giữ nguyên; ghi lý do vào registry để lần sau không ai "sửa nhầm" thành Editor.

## Share folder, đừng share từng file

Share **folder cha** một lần thì mọi file bên trong có quyền luôn — kể cả file tạo mới sau này.
Share từng file thì tuần nào có workbook mới lại phải xin quyền lại, và sẽ có tuần quên.

Thứ tự ưu tiên khi cấp quyền:

1. Folder dự án của client → Editor. Xong.
2. Chỉ share riêng file nào nằm ngoài các folder đó.

`setup_credential.py share` liệt kê folder trước, file lẻ sau, đúng theo thứ tự này.

## Cách share (người sở hữu file làm)

1. Mở folder hoặc file trên Google Drive.
2. Bấm **Share**.
3. Dán **địa chỉ robot** của người xin — dạng `abc@duan.iam.gserviceaccount.com`.
4. Đổi quyền từ *Viewer* sang **Editor**.
5. **Bỏ tick "Notify people"** — robot không có hộp thư, gửi thông báo sẽ báo lỗi.
6. **Send** / **Share**.

Google có thể cảnh báo địa chỉ này không phải tài khoản Google thường. Bình thường, cứ tiếp tục.

## Người mới cần làm gì

Bạn **không tự cấp quyền cho robot của mình được**. Quyền do người sở hữu file cấp.

Chạy `python3 _SETUP/setup_credential.py share` — script in sẵn địa chỉ robot, danh sách cần share
và một đoạn tin nhắn để copy gửi Lead. Share xong chạy lại lệnh đó để xác nhận.

## Đọc trạng thái

| Script báo | Nghĩa là | Làm gì |
|---|---|---|
| `✅ Editor` | Đủ quyền cho cả script lẫn MCP | Không phải làm gì |
| `⚠️ chỉ Viewer` | Script đọc được; AI ghi qua MCP sẽ lỗi | Xin nâng lên Editor — trừ khi đây là file cố ý Viewer |
| `❌ chưa share` | Robot chưa thấy file | Xin share |
| `— không kiểm được` | Thiếu thư viện Google hoặc mạng lỗi | Chạy `setup_doctor.py --fix` rồi thử lại |

Đã share rồi vẫn `❌`: gần như luôn là share nhầm robot của người khác. Đối chiếu địa chỉ robot bằng
`python3 _SETUP/setup_credential.py detect`.

## Ranh giới dữ liệu

- Chỉ share file thuộc phạm vi công việc của người đó. Robot kế thừa đúng những gì được share — không
  hơn, không kém.
- Không share sheet chứa mật khẩu, tài khoản đăng nhập của khách cho bất kỳ robot nào. Sheet nào lỡ
  có tab như vậy thì tách tab đó ra file riêng trước khi share.
- Người nghỉ việc: xóa robot của họ khỏi danh sách share, và Lead xóa service account trong Google
  Cloud. Không cần đụng tới robot của người khác.
