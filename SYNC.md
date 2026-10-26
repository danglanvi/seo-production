# SYNC.md — Luật đồng bộ git cho SEO Production

File này dành cho MỌI thành viên làm việc trong repo dự án `seo-<client>`, kể cả người chưa từng dùng git. Đọc hết một lần khi onboard. Khi gặp sự cố, mở đúng mục theo mục lục.

Hai cách thao tác đều hợp lệ ngang nhau — chọn 1 và dùng nhất quán:

| Việc | Terminal (gõ lệnh) | GitHub Desktop (bấm nút) |
|---|---|---|
| Lấy bản mới nhất về máy | `git pull` | `Fetch origin` → `Pull origin` |
| Gom mọi thay đổi vừa làm | `git add -A` | Tự động — tab `Changes` đã liệt kê sẵn |
| Chốt một phiên bản kèm mô tả | `git commit -m "..."` | Điền message ô dưới trái → `Commit to main` |
| Đẩy phiên bản lên server | `git push` | `Push origin` |

Mô hình nhánh: **main-only**. Team không tạo branch, không tạo PR. Chỉ SEO Lead được tạo nhánh khi thí nghiệm lớn.

---

## 1. Cài đặt lần đầu

1. Cài công cụ — chọn 1 trong 2:
   - **GitHub Desktop** (desktop.github.com): khuyến nghị cho người mới, mọi thao tác trong file này đều bấm nút được.
   - **git terminal** (git-scm.com): cho người quen dòng lệnh.
2. Nhận email invite vào repo `seo-<client>` từ Lead → bấm **Accept invitation**. Chưa accept thì chưa clone được.
3. Clone repo dự án về máy — team CHỈ clone repo dự án, KHÔNG clone master:

   ```bash
   git clone git@github.com:<org>/seo-<client>.git ~/seo-<client>
   ```

   Lệnh này tải toàn bộ repo về folder `~/seo-<client>` trên máy bạn. GitHub Desktop: `File → Clone Repository → URL` rồi dán địa chỉ repo.
4. Config chuẩn — chạy 3 lệnh sau đúng 1 lần, bên trong folder repo vừa clone:

   ```bash
   git config user.name "Ten Cua Ban"
   git config user.email "ban@gtvseo.com"
   git config pull.rebase false
   ```

   - Lệnh 1 và 2 gắn tên + email vào mỗi commit để ai cũng biết dòng nào của ai.
   - Lệnh 3 buộc git trộn thay đổi kiểu merge (an toàn với luật union ở mục 3) thay vì rebase.
   - GitHub Desktop: tên + email đặt ở `Preferences → Git`; riêng lệnh 3 chạy 1 lần qua `Repository → Open in Terminal`.
5. Mở folder repo bằng Claude Code / Codex / Antigravity và chạy thử 1 skill bất kỳ. Agent đọc được `CLAUDE.md` + trả lời đúng luật nghĩa là setup xong.

---

## 2. Nhịp hằng ngày (Executive + Account)

1. **Bắt đầu ca**: chạy `git pull`. Lệnh này kéo mọi thay đổi đồng nghiệp đã push về máy bạn, để bạn luôn làm trên bản mới nhất.
2. **Kết thúc mỗi khối việc** (không đợi cuối ngày):

   ```bash
   git add -A && git commit -m "<client>: <workstream> — <việc>" && git pull && git push
   ```

   Chuỗi này làm 4 bước liền: gom thay đổi của bạn → chốt phiên bản kèm mô tả (commit TRƯỚC để thay đổi của bạn được an toàn) → kéo bản mới nhất về trộn → đẩy lên server. GitHub Desktop: điền message → `Commit to main` → `Fetch origin` / `Pull origin` → `Push origin`.
3. Commit message theo đúng format `<client>: <workstream> — <việc>`, ví dụ: `acme: onpage — audit entity trang danh mục`.
4. **Luật vàng: không để việc qua đêm chưa push.** Chưa xong cũng push — bản dở trên server tốt hơn bản đẹp kẹt trong máy hỏng.

---

## 3. Khu vực ghi của bạn

1. **1 file — 1 PIC.** Mỗi file deliverable có đúng 1 PIC, ghi ở cột PIC trong `index.md`. Chỉ PIC được ghi file đó. Người khác góp ý qua `12-feedback-lessons/feedback-log.md`, không sửa thẳng.
2. **File cấu trúc/luật là read-only với team** — chỉ Lead đụng, và chỉ qua MIGRATION (mục 6). Danh sách khớp bảng 2.A của `MIGRATION.md`:
   - 9 file root: `CLAUDE.md`, `AGENT.md`, `AGENTS.md`, `README.md`, `SETUP.md`, `MIGRATION.md`, `SYNC.md`, `ORCHESTRATOR.md`, `COMMANDS.md`
   - `.gitignore` · `.gitattributes`
   - `_TEMPLATES/`, `skills/`, `.claude/skills/`, `.agents/skills/`, `02-raw/knowledge/`, `config/`
   - `README.md` + `CLAUDE.md` + `AGENTS.md` (nội quy trạm) của mọi WS folder (`00-client-context/` → `12-feedback-lessons/`)
3. **Ba file dùng chung** — mỗi file một luật riêng:

   | File | Cơ chế | Luật ghi |
   |---|---|---|
   | `log.md` | merge=union (git giữ cả hai phía, không nổ conflict) | Append-only: chỉ thêm entry mới dạng `## [YYYY-MM-DD] <op> \| <title> — @<alias>`. CẤM sửa entry cũ — union sẽ nhân đôi dòng bị sửa. |
   | `12-feedback-lessons/feedback-log.md` | merge=union | Mỗi feedback 1 block: `### FB-YYYY-MM-DD-<alias>-<nn> \| <nguồn: client/internal/QC> \| <workstream>` + `- Nội dung:` + `- Đề xuất:` + `- Trạng thái distill: pending`. Chỉ Lead được đổi dòng Trạng thái distill. |
   | `index.md` | KHÔNG union — conflict xử theo mục 4 | Mỗi công đoạn 1 dòng, chỉ PIC sửa dòng của mình. Luôn `git pull` NGAY TRƯỚC khi sửa. Cấu trúc bảng chỉ Lead đổi, vào thời điểm Lead đã báo team push hết. |

---

## 4. Khi push bị từ chối / conflict

1. **Push bị từ chối (rejected)**: nghĩa là server có commit mới hơn máy bạn. Chạy `git pull` để kéo về rồi `git push` lại — 90% trường hợp xong ở đây. GitHub Desktop tự báo "newer commits on remote": bấm `Pull` rồi `Push`.
2. **Pull xong màn hình báo CONFLICT**: đừng sửa tay, đừng đoán. Mở AI (Claude Code / Codex / Antigravity) ngay tại folder repo và dán nguyên văn prompt sau:

   ```text
   Repo này đang có merge conflict. Đọc SYNC.md mục 4 và .gitattributes. Resolve theo luật: file append-only (log.md, feedback-log.md) giữ CẢ HAI phía, sắp theo ngày; index.md resolve từng dòng — mỗi dòng công đoạn lấy phiên bản của người là PIC dòng đó (cột PIC); file deliverable lấy phiên bản của PIC. Liệt kê từng file + cách resolve cho tôi duyệt TRƯỚC khi ghi, rồi commit message 'merge: resolve conflict <files>' và push.
   ```

3. AI liệt kê phương án → bạn duyệt → AI commit + push. Nếu AI báo trường hợp nằm ngoài luật trên, dừng lại hỏi Lead.

> ### ⛔ KHUNG ĐỎ — CẤM TUYỆT ĐỐI
>
> 1. **CẤM `git push --force`** (và mọi biến thể `--force-with-lease`) — xóa sạch công sức người khác trên server, không cứu được.
> 2. **CẤM `git reset --hard` khi chưa hỏi Lead** — vứt bỏ thay đổi chưa commit trên máy bạn, không undo được.
> 3. **CẤM xóa clone rồi tải zip về đè lại** — mất toàn bộ lịch sử git, repo của bạn thành file chết không đồng bộ được nữa.
>
> Bí quá thì dừng, chụp màn hình, nhắn Lead. Mọi sự cố git đều cứu được — trừ 3 hành động trên.

---

## 5. Quy trình SEO Lead (canonical + merge)

Hằng ngày: Lead theo nhịp mục 2 như mọi người. Hằng tuần thêm nghi thức 4 bước:

1. **Tổng hợp tuần**: `git pull`, rồi đọc `git log --since="1 week ago" --oneline` (danh sách commit tuần qua) và `git diff @{1.week.ago} --stat` (file nào đổi, đổi bao nhiêu) — hoặc nhờ AI tổng hợp theo workstream, đối chiếu với `index.md`.
2. **Distill feedback**: đọc `feedback-log.md`, chuyển block đáng giữ thành lesson trong `12-feedback-lessons/lessons/` — mỗi lesson 1 file, frontmatter `scope: project|system|company`, `status: new`, `credit: @alias` — rồi đổi dòng Trạng thái distill của block.
3. **Sửa cấu trúc index.md nếu cần** — đây là thời điểm DUY NHẤT trong tuần được đổi cấu trúc bảng, sau khi đã báo team push hết.
4. **Chốt**: commit + push; đạt mốc dự án thì `git tag milestone-<n>` — lệnh này đóng dấu phiên bản tại mốc để sau này quay lại xem đúng trạng thái repo lúc đó.

Prompt in sẵn — Lead mở AI tại repo và dán nguyên văn:

```text
Làm nghi thức tuần cho repo này theo SYNC.md mục 5:
1) Chạy `git pull`, rồi `git log --since="1 week ago" --oneline` và `git diff @{1.week.ago} --stat`; tổng hợp thay đổi tuần qua theo workstream, đối chiếu index.md và chỉ ra lệch (file đã đổi nhưng index chưa cập nhật, người ghi ngoài vùng PIC).
2) Đọc 12-feedback-lessons/feedback-log.md, liệt kê mọi block còn "Trạng thái distill: pending"; với từng block đề xuất lesson: 1 file trong 12-feedback-lessons/lessons/, frontmatter scope: project|system|company, status: new, credit: @alias của người ghi feedback.
3) Trình toàn bộ danh sách cho tôi duyệt TRƯỚC khi ghi file; sau khi duyệt mới tạo lesson và đổi "Trạng thái distill" của block tương ứng.
4) Nếu tôi yêu cầu sửa cấu trúc index.md thì làm ở bước này — thời điểm duy nhất trong tuần.
5) Kết thúc: commit 'chore: nghi thức tuần YYYY-MM-DD' và push; nếu tôi xác nhận đạt mốc thì tạo git tag milestone-<n>.
```

---

## 6. Nhận update từ master (MIGRATION — chỉ Lead)

Master đổi (luật, template, skill mới) → repo dự án KHÔNG tự nhận. Lead chạy MIGRATION, team chỉ cần pull.

1. Clone master bản mới về folder tạm:

   ```bash
   git clone --depth 1 git@github.com:<org>/seo-production-master.git /tmp/seo-master-new
   ```

   `--depth 1` nghĩa là chỉ tải bản mới nhất, không tải lịch sử — nhanh và đủ dùng cho migration.
2. Mở AI tại repo DỰ ÁN (không phải folder tạm), dán nguyên văn prompt:

   ```text
   Master mới ở /tmp/seo-master-new, tag <tag, ví dụ v2026.07>. Đọc `MIGRATION.md` của bản master mới, thực hiện đúng bảng 2.A (GHI ĐÈ) và 2.B (GIỮ) của nó. Báo diff cho tôi duyệt TRƯỚC khi ghi. Sau khi ghi: cập nhật `master_version` trong MIGRATION.md của repo này, commit 'migration: master <tag>' và push.
   ```

3. Duyệt diff → AI commit + push. Báo team chạy `git pull` để nhận bản mới.

---

## 7. Đường tri thức về master + wiki

Việc của Vincent — team chỉ cần biết luồng này tồn tại. Tri thức chảy 3 vòng:

| Vòng | Nhịp | Việc |
|---|---|---|
| Repo dự án | Tuần | Lead distill feedback-log → `lessons/` (mục 5) |
| Master | Tháng | Vincent pull các repo dự án, gộp lesson `scope: system|company` về master + wiki |
| Broadcast | Quý / theo batch | Master tag phiên bản mới → Lead các dự án chạy MIGRATION (mục 6) |

Người ghi feedback/lesson giữ nguyên credit `@alias` khi lesson được gộp lên master/wiki.

---

## 8. Bảng giới hạn theo runtime

| Hạng mục | Claude Code | Codex | Antigravity | Ghi chú |
|---|---|---|---|---|
| Skill delivery (`skills/`, 42 skill) | ✅ | ✅ | ✅ | Skill tool-dependent cần dependency bên dưới; thiếu thì chạy fallback + ghi rõ giới hạn dữ liệu |
| `gtv-client-report` | ✅ CHỈ Claude Code | ❌ | ❌ | Không nằm trong `.agents/skills/`. Task báo cáo client BẮT BUỘC chạy Claude Code (thường là Lead) |
| `wp-content-review-apply` | ✅ CHỈ Claude Code | ❌ | ❌ | Trang duyệt Duyệt/E là artifact claude.ai có database. Không nằm trong `.agents/skills/` |
| MCP (ahrefs, firecrawl, ga4, gsc, google-sheets...) | Theo cấu hình máy | Theo cấu hình máy | Theo cấu hình máy | `.mcp.json` KHÔNG commit — ai có API key tự tạo từ `config/mcp.json.example` |
| Slash command | Quét `.claude/skills/` khi mở đúng folder repo | Gọi skill theo `.agents/skills/` bằng ngôn ngữ tự nhiên | Gọi skill theo `.agents/skills/` bằng ngôn ngữ tự nhiên | Codex/Antigravity không có slash command — mô tả việc là đủ |

Dependency của nhóm skill tool-dependent: node/pagespeed, dataforseo, image-read, python, firecrawl/web, ahrefs, ai-search; nhóm `wp-*` thêm SSH + WP-CLI vào server của site, Chrome, key Jev (`OPENROUTER_JEV_API_KEY`) và venv EmbeddingGemma (`tools/ai-assist/README.md`). Máy thiếu dependency nào thì skill tương ứng tự hạ cấp sang fallback và PHẢI ghi rõ giới hạn dữ liệu trong output.

---

## 9. Tạo repo & remote (Vincent/Lead)

Chỉ Vincent hoặc Lead làm mục này. Lệnh copy-paste:

```bash
# Master (1 lần, tại workspace root):
git -C "SEO Production" init -b main && git -C "SEO Production" add -A && git -C "SEO Production" commit -m "bootstrap: master v2026.07" && git -C "SEO Production" tag v2026.07
# Khi có GitHub org: tạo repo private seo-production-master (bật Template repository) rồi:
git -C "SEO Production" remote add origin git@github.com:<org>/seo-production-master.git && git -C "SEO Production" push -u origin main --tags
# Repo dự án mới: GitHub "Use this template" → seo-<client> → clone vào PROJECTS/<client>/
```

Giải thích từng dòng:

1. Dòng 1 biến folder `SEO Production/` thành repo git, chốt commit đầu tiên và đóng dấu tag `v2026.07` làm phiên bản master.
2. Dòng 2 nối repo local với repo private `seo-production-master` trên GitHub rồi đẩy toàn bộ nội dung + tag lên — nhớ bật **Template repository** trong Settings của repo GitHub trước.
3. Dòng 3 là luồng tạo dự án mới: trên GitHub bấm **Use this template** → đặt tên `seo-<client>` (private) → Vincent clone vào `PROJECTS/<client>/` → setup dữ liệu client → push → team clone.

Sau khi tạo repo, đặt branch protection cho `main` (GitHub → Settings → Branches → Add rule):

1. Bật **Block force pushes** — chặn tuyệt đối lệnh cấm số 1 ở mục 4.
2. Bật **Block deletions** — không ai xóa được nhánh main.
3. KHÔNG bật Require pull request — mô hình main-only không dùng PR.

Ghi chú: org GitHub dùng placeholder `<org>` (dự kiến `github.com/gtvseo/` — Vincent chốt tên org sau). Master versioning bằng git tag (`v2026.07`, `v2026.10`...); mỗi repo dự án ghi `master_version` đang dùng trong frontmatter `MIGRATION.md`.
