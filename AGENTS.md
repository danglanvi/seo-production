# SEO Production — agent entry

## BOOTSTRAP — máy chưa cài xong thì làm việc này TRƯỚC

Người dùng vừa clone repo, hỏi "cần cài gì để chạy được", hoặc gặp lỗi thiếu thư viện / thiếu
credential Google / 403 khi đọc sheet → **dừng việc đang làm, đọc `_SETUP/SETUP-MAY.md` và làm theo**.

- Chẩn đoán bằng `python3 _SETUP/setup_doctor.py --json` — không đoán máy thiếu gì.
- Sửa từ tầng thấp lên: A nền → B thư viện → C chìa khóa → D quyền Drive.
- Credential là service account **của riêng từng người**; repo không giữ credential của ai. Không tạo
  hộ người dùng, không nhận file key qua chat.

Chỉ bắt đầu việc nội dung khi doctor trả `ok: true`.

---

Repo tự chứa cho hệ SEO delivery của GTV. Chạy được ở hai chế độ:
- Trong workspace GTV của Vincent: áp toàn bộ `AGENTS.md` ở các thư mục ancestor trước, rồi file này. Master nằm ngay dưới root; instance `PROJECTS/<client-slug>/` nằm sâu hơn một cấp.
- Bản clone standalone của team: file này + `CLAUDE.md` cùng thư mục là luật đầy đủ — KHÔNG tham chiếu ra ngoài repo.

Trước mọi task trong scope này, đọc toàn bộ `CLAUDE.md` cùng thư mục (luật pipeline + 36 công đoạn),
`AGENT.md` (persona giao tiếp), và `SYNC.md` khi task đụng git/đồng bộ.

- Skill canonical của repo: `skills/`; runtime mirror `.claude/skills/` (Claude) + `.agents/skills/` (Codex/Antigravity) — mirror committed sẵn, KHÔNG sửa trực tiếp. Sửa skill = sửa trong `skills/` rồi đồng bộ mirror: bản standalone chạy `bash _SETUP/sync-skills.sh` (đóng gói sẵn trong repo; bản cũ `tools/sync-skills.sh` vẫn dùng được); trong workspace Vincent dùng `tools/sync-agent-skills.rb` ở root workspace như cũ.
- Tên tool cũ (AskUserQuestion/WebFetch/MCP cụ thể) = capability tương đương của runtime hiện tại; thiếu thì dùng fallback trong skill và ghi rõ giới hạn dữ liệu.
- `gtv-client-report` và `gtv-weekly-report` chỉ có ở Claude Code (không nằm trong `.agents/skills/`). Codex/Antigravity chỉ làm draft thủ công theo template + luật trạm `09-reporting`, ghi rõ giới hạn và không gửi thẳng cho khách.

## Kho tri thức khách + đồng bộ với repo content (mọi runtime, thêm 01/10/2026)

- Fact của khách (sản phẩm, thông số, chứng nhận, dự án) có bản gốc ở Kho tri thức của repo content. Repo này chỉ đọc snapshot: `python3 tools/project_sync.py pull` → `00-client-context/kb-snapshot/<ngày>/` (+ trạng thái bài, bài đã humanize). Output ra ngoài (schema, offsite, sửa GEO) chỉ dùng claim `approved` + `public_ok`.
- Repo content kéo ngược hồ sơ khách, KPI, topical map, entity của repo này. Mỗi loại dữ liệu chỉ sửa ở repo chủ. Luật: `_REFERENCE/project-sync.md`.
