# SEO Production — agent entry

Repo tự chứa cho hệ SEO delivery của GTV. Chạy được ở hai chế độ:
- Trong workspace GTV của Vincent (tồn tại `../AGENTS.md`): áp luật root đó trước, rồi file này.
- Bản clone standalone của team: file này + `CLAUDE.md` cùng thư mục là luật đầy đủ — KHÔNG tham chiếu ra ngoài repo.

Trước mọi task trong scope này, đọc toàn bộ `CLAUDE.md` cùng thư mục (luật pipeline + 33 công đoạn),
`AGENT.md` (persona giao tiếp), và `SYNC.md` khi task đụng git/đồng bộ.

- Skill canonical của repo: `skills/`; runtime mirror `.claude/skills/` (Claude) + `.agents/skills/` (Codex/Antigravity) — mirror committed sẵn, KHÔNG sửa trực tiếp, không tự sinh lại.
- Tên tool cũ (AskUserQuestion/WebFetch/MCP cụ thể) = capability tương đương của runtime hiện tại; thiếu thì dùng fallback trong skill và ghi rõ giới hạn dữ liệu.
- `gtv-client-report` chỉ có ở Claude Code (không nằm trong `.agents/skills/`) — Codex/Antigravity không nhận task reporting client.
