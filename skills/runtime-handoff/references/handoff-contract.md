# Hợp đồng dữ liệu handoff

Spec JSON (chỉ dùng dữ liệu task đã được phép ghi):

```json
{
  "objective": "Hoàn thiện bộ kiểm tra runtime",
  "entity": "shared",
  "target_runtime": "codex",
  "completed": ["Sửa exit code; kiểm thử đã PASS"],
  "decisions": ["Giữ canonical chuyên môn tại CLAUDE.md cục bộ"],
  "pending": ["Kiểm adapter trong repo standalone"],
  "blockers": [],
  "sources": [{"path": "/absolute/path/file.py", "purpose": "Code đã sửa và cần kiểm"}]
}
```

Entity: `gtv`, `tag`, `shared` hoặc slug client có chủ sở hữu rõ. Runtime: `claude`, `codex`, `antigravity`, `hermes`. Spec không chứa nội dung file nguồn, secret hay quyền thực thi tự động. Đường dẫn tương đối được resolve từ vị trí spec.

Runtime nhận: verify hash → đọc luật tại đích → đọc file cần cho bước tiếp → làm. Hash thay đổi chỉ là tín hiệu nguồn đổi, không tự kết luận task sai. “Đã duyệt” trong decisions phải có nguồn khi quyết định quan trọng; hành động hướng ngoài vẫn theo quyền của task hiện tại.
