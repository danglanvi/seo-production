# Setup kit — bản canonical

Bộ cài đặt dùng chung cho các repo production của GTV. **Sửa ở đây, không sửa mirror.**

```
wiki nội bộ «setup-kit» (ngoài repo, hỏi Lead/Vincent)            ← canonical (thư mục này)
        ↓  python3 tools/sync-setup-kit.py
<repo>/_SETUP/                ← mirror trong 6 repo, sinh tự động, có MANIFEST.json
<repo>/.claude/skills/setup-may/   ← skill, sinh cùng lúc từ skill/setup-may/
```

## Nội dung

| File | Ai đọc | Vai trò |
|---|---|---|
| `SETUP-MAY.md` | AI | Runbook 6 bước — AI đọc rồi làm, không đưa cho người dùng |
| `HUONG-DAN-GOOGLE-CREDENTIAL.md` | Người dùng | Phần 1: đăng nhập `gws` (bắt buộc). Phần 2: tạo service account riêng (repo dùng robot) |
| `CHIA-QUYEN-DRIVE.md` | Người dùng + Lead | Share gì, quyền gì, vì sao Editor chứ không Viewer |
| `setup_doctor.py` | AI chạy | Khám máy 4 tầng: nền (có `gws`) · thư viện · đăng nhập (gws bắt buộc, robot khi repo cần) · quyền robot |
| `setup_credential.py` | AI chạy | `detect` / `register` / `share` / `check` |
| `sync-skills.sh` | Người vận hành | Dựng lại mirror skill trong clone standalone (không có `tools/` của workspace) |
| `skill/setup-may/SKILL.md` | Claude Code | Cửa vào bằng ngôn ngữ tự nhiên |

## Mô hình credential

**`gws` là bắt buộc ở mọi repo** (Vincent chốt 01/11/2026). Mỗi người tạo OAuth client riêng, đăng
nhập `gws` bằng email công ty. File Google của công ty share cho cả domain, nên không phải xin quyền
từng file. Doctor kiểm `gws` đã đăng nhập đúng domain và đủ quyền drive, sheets, docs.

**Robot chỉ cho repo có script cần nó** (doctor suy từ `requirements.txt` có thư viện google, hoặc
bản mẫu MCP khai service account). Mỗi người một service account riêng. Repo không chứa robot của ai. Người dùng tự tạo trong
Google Cloud của mình, `register` gắn vào repo, rồi xin Lead share file Drive cho địa chỉ robot đó
với quyền **Editor**.

Ba chỗ `register` ghi — tất cả đều gitignore:

| Chỗ | Cho ai dùng |
|---|---|
| `~/.config/gcp/<project>-<robot>.json` | Chìa khóa thật, `chmod 600`, nằm NGOÀI repo |
| `config/local.yaml` | Script chạy tay từ Terminal |
| `.claude/settings.local.json` (`env`) | Mọi lệnh chạy trong Claude Code — nhờ vậy script cũ đọc `GOOGLE_APPLICATION_CREDENTIALS` chạy được mà không phải sửa dòng nào |

## Kit tự thích ứng theo repo

Không có file profile riêng cho từng repo. Doctor tự đọc `requirements.txt` để biết cần thư viện gì,
tự tìm registry (`tools/review-sheets.yaml`, `tools/drive-links.yaml`, `report-config.yaml`) để biết
cần quyền trên ID nào. Repo không có registry → tầng D tự bỏ qua.

Hệ quả: thêm repo mới vào `TARGETS` của `tools/sync-setup-kit.py` là đủ, không phải sửa kit.

## Sửa kit

```bash
python3 tools/sync-setup-kit.py --check     # so canonical ↔ 6 mirror
python3 tools/sync-setup-kit.py --dry-run   # xem sẽ ghi gì
python3 tools/sync-setup-kit.py             # sync + tự kiểm lại
```

Mirror bị sửa tay sẽ bị đè. Thấy sai thì vá canonical rồi sync.
