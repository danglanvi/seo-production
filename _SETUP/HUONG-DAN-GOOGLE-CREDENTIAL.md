# Kết nối Google cho máy của bạn

> Dành cho người dùng đọc. Làm một lần, dùng được cho mọi repo GTV trên máy này.
>
> - **Phần 1 — đăng nhập `gws`: bắt buộc**, khoảng 10 phút.
> - **Phần 2 — robot (service account): chỉ khi** `setup_doctor.py` báo dòng `robot (service account)` THIẾU.

## Phần 1 — Đăng nhập gws bằng email công ty

`gws` (Google Workspace CLI) cho script trong repo đọc và ghi Sheet, Doc, Drive dưới tên của bạn.
File Google của công ty đã share cho cả domain, nên bạn không phải xin quyền từng file.

### 1. Cài gws

Claude cài giúp bằng lệnh `npm install -g @googleworkspace/cli`. Máy cần có Node trước (tầng A).

### 2. Tạo project và bật API

Vào https://console.cloud.google.com bằng **email công ty**. Bấm ô chọn project → **New Project** →
đặt tên (ví dụ `gtv-hieu`) → **Create**, rồi chọn project đó. Menu trái → **APIs & Services** →
**Library**, bật lần lượt **Google Drive API**, **Google Sheets API**, **Google Docs API**.

Đã tạo project ở phần 2 trước đây thì dùng lại project đó, chỉ bật thêm API còn thiếu.

### 3. Tạo màn hình đồng ý

**APIs & Services** → **OAuth consent screen**. Chọn **Internal** (chỉ người trong công ty dùng
được), điền tên app (ví dụ `gws`) và email của bạn → **Save**.

### 4. Tạo OAuth client

**APIs & Services** → **Credentials** → **Create credentials** → **OAuth client ID** → loại
**Desktop app** → **Create** → **Download JSON**.

Báo Claude *"tôi tải file client rồi"*. Claude chép file vào `~/.config/gws/client_secret.json`.
File này coi như mật khẩu: không gửi qua chat, email, Drive, không để trong repo.

### 5. Đăng nhập

Claude chạy `gws auth login -s drive,sheets,docs`. Trình duyệt mở ra: chọn **email công ty**, bấm
**Allow**. Xong, Claude chạy lại `python3 _SETUP/setup_doctor.py` để kiểm.

Máy có sẵn `gcloud` thì bước 2–4 làm nhanh bằng `gws auth setup --login`.

Đổi máy: làm lại bước 4–5 trên máy mới. Nghỉ việc: chạy `gws auth logout` và báo Lead.

## Phần 2 — Robot (service account), khi repo cần

Làm khoảng 10 phút. Chỉ làm khi doctor báo repo có script cần robot.

### Hiểu trước khi làm: robot và chìa khóa

Các script trong repo không đăng nhập bằng tài khoản Google của bạn. Chúng đăng nhập bằng một
**tài khoản robot** (Google gọi là *service account*) — một tài khoản không có mật khẩu, không đăng
nhập bằng trình duyệt được, chỉ dùng cho máy móc.

Hai thứ khác nhau, đừng nhầm:

| | Là gì | Bí mật không |
|---|---|---|
| **Địa chỉ robot** `abc@duan.iam.gserviceaccount.com` | Địa chỉ của robot. Dùng để **share** file Google cho nó, y hệt share cho một người | **Không.** Cứ gửi thoải mái cho người cần share file |
| **File chìa khóa** `.json` | Bằng chứng máy này đúng là robot đó | **Có.** Coi như mật khẩu. Không gửi email, không bỏ lên Drive, không commit |

**Mỗi người một robot riêng.** Bạn tạo robot của bạn, đồng nghiệp tạo robot của họ. Không chuyền file
chìa khóa cho nhau — người nghỉ việc thì chỉ cần xóa robot của người đó, không ảnh hưởng ai.

### 6 bước tạo

#### 1. Tạo project trên Google Cloud

Vào https://console.cloud.google.com bằng **email công ty**. Ở thanh trên cùng, bấm ô chọn project →
**New Project** → đặt tên (ví dụ `gtv-hieu`) → **Create**. Đợi vài giây, rồi chọn project vừa tạo.

Lần đầu vào Google Cloud có thể phải đồng ý điều khoản. Không cần nhập thẻ — những API dùng ở đây
đều miễn phí trong hạn mức thường ngày.

#### 2. Bật hai API

Menu trái → **APIs & Services** → **Library**. Tìm và bật lần lượt:

- **Google Sheets API** → bấm **Enable**
- **Google Drive API** → bấm **Enable**

Thiếu bước này thì mọi thứ sau vẫn tạo được nhưng chạy sẽ báo lỗi `API has not been used`.

#### 3. Tạo robot

Menu trái → **IAM & Admin** → **Service Accounts** → **Create service account**.

- *Service account name*: đặt gì cũng được, ví dụ `claude-sheets`
- Bấm **Create and continue** → phần cấp role **bỏ trống, bấm Continue** → **Done**

Không cần cấp role nào ở đây. Quyền của robot đến từ việc người ta share file Google cho nó, không
đến từ role trong Cloud.

#### 4. Lấy chìa khóa

Trong danh sách Service Accounts, bấm vào robot vừa tạo → tab **KEYS** → **Add key** →
**Create new key** → chọn **JSON** → **Create**.

Trình duyệt tải về một file `.json` (thường vào `Downloads`). **Đây là chìa khóa.**

#### 5. Gắn vào repo

Quay lại Claude Code, nói: *"tôi tải file key về rồi"* — hoặc chạy thẳng:

```bash
python3 _SETUP/setup_credential.py register ~/Downloads/<tên-file>.json
```

Script chép chìa khóa vào chỗ an toàn ngoài repo, khóa quyền đọc chỉ cho tài khoản máy của bạn, và
ghi cấu hình cho cả Claude Code lẫn terminal. Xong, xóa file trong `Downloads` đi.

#### 6. Xin quyền trên các file Google

Script in ra địa chỉ robot của bạn và danh sách file/folder cần share. Gửi cho Lead hoặc người sở
hữu file, xin quyền **Editor**.

Bạn không tự cấp quyền cho robot của mình được — quyền do người sở hữu file cấp, giống hệt share
file cho một đồng nghiệp mới.

Chi tiết cách share và vì sao phải Editor: `_SETUP/CHIA-QUYEN-DRIVE.md`.

### Giữ chìa khóa cho an toàn

- Một máy một chìa khóa. Đổi máy → tạo key mới ở bước 4, không chép file cũ sang.
- Không bao giờ để file `.json` bên trong thư mục repo.
- Lỡ gửi chìa khóa cho ai, hoặc lỡ commit lên GitHub: vào **KEYS** xóa key đó ngay rồi tạo key mới.
  Xóa key cũ không ảnh hưởng file đã share — địa chỉ robot không đổi.
- Nghỉ việc / bàn giao máy: báo Lead xóa robot của bạn trong Google Cloud.
