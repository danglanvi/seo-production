---
name: setup-may
description: Cài đặt máy để chạy được repo GTV này — kiểm tra và cài phần mềm còn thiếu (Python, thư viện, Node, Playwright, uv), hướng dẫn người dùng tự tạo Google service account riêng, gắn credential vào repo, rồi in danh sách file/folder Drive cần xin quyền Editor. Use when (1) vừa clone hoặc muốn cài repo — "cài đặt repo github này", "mới tải repo về", "máy tôi cần cài gì", "setup máy", "install this repo", "what do I need to install"; (2) script/skill lỗi thiếu môi trường — "thiếu thư viện", "ModuleNotFoundError", "no module named yaml", "pip install gì", "không chạy được script"; (3) lỗi credential hoặc quyền Google — "không thấy credentials", "GOOGLE_APPLICATION_CREDENTIALS", "service account", "chìa khóa robot", "403 khi đọc sheet", "chưa share sheet", "xin quyền Drive", "tạo credential Google"; (4) hỏi về MCP hoặc .mcp.json của repo. KHÔNG dùng cho việc nội dung (báo cáo, audit, content, hợp đồng) — chỉ cho cài đặt và môi trường.
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
