# SETUP — SEO Production Master

> **Mục đích:** Hướng dẫn tạo instance dự án cho 1 client mới từ master template này.
>
> **Đối tượng đọc:** Vincent / SEO Lead Project — người khởi tạo dự án. Team Executive/Account chỉ cần clone repo dự án đã setup xong (xem `SYNC.md` mục 1).
>
> **Folder này là gì?** Master template **client-neutral** — không chứa data của bất kỳ client nào. Mọi infra (33 công đoạn, 12 workstream, knowledge pack, QC gate, 20 skill) đã sẵn sàng. Việc của bạn: duplicate → drop hợp đồng → trigger Claude setup.
>
> Đọc kèm: [`CLAUDE.md`](./CLAUDE.md) (luật vận hành) · [`SYNC.md`](./SYNC.md) (git + đồng bộ team) · [`MIGRATION.md`](./MIGRATION.md) (update instance cũ lên version master mới).

---

## 0. Trước khi bắt đầu

### Hai chế độ chạy

| Chế độ | Ai dùng | Khác biệt khi setup |
|---|---|---|
| **Trong workspace Vincent** (tồn tại `../GTV Ops/`) | Vincent, SEO Lead trên máy master | Bước 3 đọc được client meta từ `GTV Ops/wiki/entities/clients/`; bước 7-8 chạy đủ |
| **Standalone** (clone repo dự án của team) | Executive, Account, Lead làm remote | Không có `GTV Ops/` — bước 3 Claude hỏi thông tin thay vì tự đọc; bước 8 bỏ phần bookkeeping GTV Ops |

### Điều kiện tiên quyết

| Điều kiện | Vì sao | Bắt buộc? |
|---|---|---|
| Master đã có git tag version (`v2026.07`…) | Instance ghi `master_version` vào MIGRATION.md — không có tag thì sau này không biết đang chạy bản nào | **Bắt buộc** |
| Git (CLI hoặc GitHub Desktop) | Tạo repo, clone, push — chi tiết `SYNC.md` | **Bắt buộc** |
| Claude Code / Codex / Antigravity | Chạy skill + 4 thao tác vận hành | **Bắt buộc** (≥1 runtime) |
| MCP Ahrefs / Firecrawl / GA4 / GSC | Data cho audit, research, reporting | Khuyến nghị — mẫu ở `config/mcp.json.example` |

---

## 1. Protocol "setup client <tên>" — 9 bước

Tóm tắt:

| Bước | Việc | Ai làm |
|---|---|---|
| 1 | Duplicate master → `PROJECTS/<client-slug>/` | Vincent / Lead |
| 2 | Drop hợp đồng + tài liệu khách vào `02-raw/` | Vincent / Lead |
| 3 | Trigger `setup client <tên>` — Claude fill context + index | Claude (duyệt: người setup) |
| 4 | Chọn gói 8/10/12 tháng → retiming 33 dòng | Claude (duyệt: Lead) |
| 5 | Advisory → set cột Thực thi per dòng | Claude (duyệt: Lead) |
| 6 | Kick-off nội bộ: chốt Tier 2 checklist | Lead + team |
| 7 | Fork `Content Production - <client>/` nếu dự án có content | Vincent / Lead |
| 8 | Bookkeeping GTV Ops + log 2 nơi | Claude |
| 9 | Verify (mục 2 dưới) | Người setup |

### Bước 1 — Duplicate master → `PROJECTS/<client-slug>/`

Chuẩn (có GitHub org): GitHub **"Use this template"** trên `seo-production-master` → repo private `seo-<client>` → clone vào `PROJECTS/<client-slug>/`. Lịch sử sạch, không leak data client khác. Lệnh copy-paste: `SYNC.md` mục **"Tạo repo & remote"**.

Fallback (chưa có org/remote):

```bash
cp -R "SEO Production" "PROJECTS/<client-slug>"
```

Slug: kebab-case, ví dụ `minh-tuan-mobile`, `careerviet`.

### Bước 2 — Drop raw

- Hợp đồng + proposal → `02-raw/contracts-proposals/`.
- Tài liệu khách cung cấp (brand book, access, brief…) → `02-raw/client-docs/`.
- Không đổi tên file gốc. `02-raw/` là immutable — chỉ ADD.

### Bước 3 — Trigger Claude setup

Mở AI runtime tại folder instance, gõ:

```
setup client <tên>
```

Claude thực hiện (theo Execution Rule — show plan, chờ duyệt, rồi ghi):

1. Đọc toàn bộ raw vừa drop + `GTV Ops/wiki/entities/clients/<slug>.md` (nếu trong workspace; standalone → hỏi thông tin còn thiếu).
2. Fill 3 file skeleton trong `00-client-context/`: `client-profile.md` · `marketing-foundation.md` · `kpi-commitments.md`.
3. Tạo `00-client-context/hop-dong-cam-ket.md` từ `_TEMPLATES/hop-dong-cam-ket.md` — trích trường cam kết, công thức đo KPI, mốc nghiệm thu từ hợp đồng.
4. Điền bảng A (Thông tin dự án) trong `index.md` — hết `{{PLACEHOLDER}}`.

### Bước 4 — Chọn gói timeline 8/10/12 tháng

- Retiming cột **Tháng** của 33 dòng bảng B theo bảng biến thể trong `02-raw/knowledge/sop/09-timeline/10-thang-thuc-day.md`.
- Công đoạn ngoài scope gói → status `n/a` (không xóa dòng).

### Bước 5 — Mô hình Advisory (nếu có)

Dự án cố vấn → set cột **Thực thi** per dòng: `GTV` hoặc `In-house`. Dự án thực thi toàn phần giữ mặc định `GTV`.

### Bước 6 — Kick-off nội bộ

Lead + team chốt **Tier 2 checklist nào được bật** cho dự án này (tier-2-project-specific). Ghi kết quả vào cột Ghi chú dòng #12 của `index.md`.

### Bước 7 — Fork content pipeline (nếu dự án có content)

- Fork `Content Production - <client>/` theo `SETUP.md` bên đó (setup brand riêng).
- Link chéo 2 chiều: ghi path fork vào `05-content-plan/README.md` của instance này.
- Nhắc lại luật: phần VIẾT BÀI (công đoạn 13, 15, 16, 19) chạy ở fork; bên này chỉ giữ plan + tracking + QC kết quả.

### Bước 8 — Bookkeeping

Chỉ khi chạy trong workspace Vincent:

- Client page `GTV Ops/wiki/entities/clients/<slug>.md` thêm link sang instance.
- Log op `setup` cả 2 nơi: `log.md` của instance + log GTV Ops.

Standalone: chỉ log `log.md` instance.

### Bước 9 — Verify

Chạy checklist mục 2. Fail bất kỳ check nào → báo Claude "verify setup status" để diagnose + fix.

---

## 2. Verify sau setup

```bash
# 1. Client placeholder phải = 0 hit (Claude đã fill hết)
grep -rn "{{" 00-client-context/ index.md
# Expected: KHÔNG có output

# 2. Log có entry op=setup
grep "setup" log.md
# Expected: ≥1 entry "## [YYYY-MM-DD] setup | ..."
```

Kiểm tra bằng mắt trong `index.md`:

- [ ] Bảng A: đủ client/domain, hợp đồng, mô hình, gói timeline, KPI, Lead/Account.
- [ ] Bảng B: đủ **33 dòng đánh số + 1 dòng optional "— Traffic users ⚠"** (sau #29).
- [ ] Cột Tháng đã retiming theo gói; dòng ngoài scope đã `n/a`.
- [ ] Dự án advisory: cột Thực thi đã set per dòng.
- [ ] Dòng #12 có ghi chú Tier 2 checklist được bật (sau bước 6).
- [ ] Có content → `05-content-plan/README.md` có link fork Content Production.

---

## 3. Anti-patterns

| Anti-pattern | Vì sao CẤM | Làm đúng |
|---|---|---|
| **Multi-client trong 1 instance** | Leak data giữa client, vỡ luật phân vùng PIC, vỡ luật entity | Mỗi client = 1 instance riêng tại `PROJECTS/<client-slug>/` (1 repo riêng) |
| **Setup khi master chưa tag version** | Instance không ghi được `master_version` → MIGRATION sau này không biết đang chạy bản nào | Tag master trước (`SYNC.md` mục Tạo repo & remote), setup sau |
| Chạy `setup client` ngay trong `SEO Production/` (master) | Master là template client-neutral — dính client data là hỏng mọi instance sau | Duplicate ra `PROJECTS/<client-slug>/` rồi mới setup |
| Copy tay từng folder thay vì duplicate nguyên master | Sót file ẩn (`.gitattributes`, `.gitignore`, mirror skills) → vỡ merge union + slash command | Bước 1: "Use this template" hoặc `cp -R` nguyên folder |
| Sửa `02-raw/knowledge/` trong instance khi thấy checklist chưa hợp | Knowledge pack là read-only trong instance — sửa tại chỗ gây drift với master | Đề xuất vá ở master → nhận lại qua `MIGRATION.md` |

---

## 4. Sau setup — bắt đầu vận hành

Quick start 4 lệnh (chi tiết `README.md` + `CLAUDE.md`):

```
"làm công đoạn <n>"
"QC <path> theo công đoạn <n>"
"feedback: <nội dung>"
"ingest <file> vào 02-raw"
```

Team clone repo dự án + nhịp git hằng ngày: `SYNC.md` mục 1-2.

---

**Master version:** xem frontmatter `MIGRATION.md` + git tag.
