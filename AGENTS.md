# SEO Production — agent entry

Repo tự chứa cho hệ SEO delivery của GTV. Chạy được ở hai chế độ:
- Trong workspace GTV của Vincent: áp toàn bộ `AGENTS.md` ở các thư mục ancestor trước, rồi file này. Master nằm ngay dưới root; instance `PROJECTS/<client-slug>/` nằm sâu hơn một cấp.
- Bản clone standalone của team: file này + `CLAUDE.md` cùng thư mục là luật đầy đủ — KHÔNG tham chiếu ra ngoài repo.

Trước mọi task trong scope này, đọc toàn bộ `CLAUDE.md` cùng thư mục (luật pipeline + 33 công đoạn),
`AGENT.md` (persona giao tiếp), và `SYNC.md` khi task đụng git/đồng bộ.

- Skill canonical của repo: `skills/`; runtime mirror `.claude/skills/` (Claude) + `.agents/skills/` (Codex/Antigravity) — mirror committed sẵn, KHÔNG sửa trực tiếp. Sửa skill = sửa trong `skills/` rồi đồng bộ mirror: bản standalone chạy `bash tools/sync-skills.sh` (đóng gói sẵn trong repo); trong workspace Vincent dùng `tools/sync-agent-skills.rb` ở root workspace như cũ.
- Tên tool cũ (AskUserQuestion/WebFetch/MCP cụ thể) = capability tương đương của runtime hiện tại; thiếu thì dùng fallback trong skill và ghi rõ giới hạn dữ liệu.
- `gtv-client-report` và `gtv-weekly-report` chỉ có ở Claude Code (không nằm trong `.agents/skills/`). Codex/Antigravity chỉ làm draft thủ công theo template + luật trạm `09-reporting`, ghi rõ giới hạn và không gửi thẳng cho khách.
