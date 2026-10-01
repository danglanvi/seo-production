# Đồng bộ dự án giữa repo SEO và repo Content của cùng một khách

> Thêm 01/10/2026 (Vincent duyệt). Team SEO và team Content làm ở hai repo riêng (`seo-<khách>`, `content-production-<khách>` trên GitHub org GTV-SEO-Agency) nhưng dùng chung **một nguồn sự thật cho mỗi loại dữ liệu**: dữ liệu nào thì chỉ sửa ở repo chủ của nó, repo kia kéo bản chỉ đọc qua GitHub. Bản giống hệt nằm ở repo content (`_REFERENCE/project-sync.md`).

## 1. Ai giữ dữ liệu nào

| Dữ liệu | Repo chủ (sửa ở đây) | Bên kia nhận (chỉ đọc) |
|---|---|---|
| Kho tri thức khách `00-context/kb/` (sổ fact, catalog, thuật ngữ, câu hỏi mở) | Content | SEO: `00-client-context/kb-snapshot/<ngày>/` |
| Trạng thái bài, bài đã humanize | Content | SEO: `05-content-plan/content-tracking/` (`content-status.md`, `delivered/`) |
| Hồ sơ khách, Marketing Foundation, KPI cam kết | SEO (`00-client-context/`) | Content: `00-context/seo-snapshot/<ngày>/00-client-context/` |
| OKRs, cấu trúc URL, topical map / content plan / brief, internal link plan, GEO (prompt, baseline), entity (Brand Info Pack, entity plan), audit content | SEO | Content: `00-context/seo-snapshot/<ngày>/…` |
| Hợp đồng, giá (`hop-dong-cam-ket.md`) | SEO | Không chia sẻ |

## 2. Lệnh

| Ở repo | Lệnh | Kết quả |
|---|---|---|
| Content | `python3 contracts/scripts/project_sync.py pull` | Kéo repo SEO về `.peer/seo/` → chép danh sách chia sẻ vào `00-context/seo-snapshot/<YYYY-MM-DD>/` + `_source.md` (repo, commit) |
| SEO | `python3 tools/project_sync.py pull` | Kéo repo content về `.peer/content/` → `content-status.md` + `delivered/` + `kb-snapshot/<YYYY-MM-DD>/` (kèm `_source.md`) |

- Cấu hình: file `project-sync.yaml` ở root repo, chép từ `_TEMPLATES/project-sync.yaml` và điền `seo_repo`, `content_repo`, `branch`. Dùng chung một nội dung cho cả hai repo.
- `--repo <URL|thư mục>` để chỉ định repo khác cấu hình (thư mục local cũng được).
- Mỗi ngày một snapshot, không ghi đè; bản cũ giữ lại để truy vết. `.peer/` là bản clone tạm, không commit.
- Mỗi thành viên cần quyền đọc repo bên kia trên GitHub org.

## 3. Nhịp làm việc

1. Đầu phiên, hoặc trước công đoạn cần dữ liệu bên kia: chạy `pull`.
2. Làm việc trên dữ liệu của repo mình. Dữ liệu của bên kia chỉ đọc trong snapshot mới nhất.
3. Thấy dữ liệu bên kia sai hoặc thiếu: báo team chủ sửa ở repo chủ. Không sửa snapshot, không chép đè vào file của mình.
4. Cuối phiên: commit + push repo của mình để bên kia kéo được bản mới.

## 4. Repo content dùng snapshot SEO thế nào

- Topical map, content plan, brief: bản trong snapshot SEO mới nhất là nguồn chủ. `01-topical-plan/` của fork là bản làm việc của team content; lệch thì theo snapshot và báo team SEO.
- Entity (Brand Info Pack): tên pháp lý, NAP, câu định nghĩa thương hiệu lấy từ snapshot `14-entity/`, không tự viết lại.
- KPI cam kết và Marketing Foundation (persona, thuật ngữ, yêu cầu evidence) đọc ở snapshot `00-client-context/`.
