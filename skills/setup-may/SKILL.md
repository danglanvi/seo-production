---
name: setup-may
description: "Cài đặt máy để chạy repo GTV này: kiểm tra và cài phần mềm thiếu (Python, thư viện, Node, Playwright, uv), hướng dẫn tự tạo Google service account, gắn credential, in danh sách Drive cần xin quyền. Use when vừa clone repo, hỏi 'cần cài gì để chạy', hoặc gặp lỗi thiếu thư viện/credential/403."
---

# Cài đặt máy cho repo này

Đọc `_SETUP/SETUP-MAY.md` và làm theo từ đầu đến cuối. File đó là runbook đầy đủ; skill này chỉ là
cửa vào.

Ba luật không được bỏ:

1. **Chẩn đoán trước, sửa sau.** `python3 _SETUP/setup_doctor.py --json` là nguồn sự thật duy nhất
   về việc máy thiếu gì. Không đoán, không cài mò.
2. **Sửa từ tầng thấp lên**: A nền → B thư viện → C chìa khóa → D quyền Drive.
3. **Không tự tạo credential hộ người dùng và không nhận file key qua chat.** Chìa khóa là bí mật
   của họ; AI chỉ hướng dẫn và gắn file họ đã tự tải về.

Báo xong khi và chỉ khi `setup_doctor.py` trả `ok: true` và `setup_credential.py check` trả `ĐẠT`.
Chưa đạt thì nói rõ đang kẹt tầng nào và chờ ai làm gì.
