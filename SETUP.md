# SETUP — SEO Production Master

> **Mục đích:** Hướng dẫn tạo instance dự án cho 1 client mới từ master template này.
>
> **Đối tượng đọc:** Vincent / SEO Lead Project — người khởi tạo dự án. Team Executive/Account chỉ cần clone repo dự án đã setup xong (xem `SYNC.md` mục 1).
>
> **Folder này là gì?** Master template **client-neutral** — không chứa data của bất kỳ client nào. Mọi infra (36 công đoạn, 13 workstream, knowledge pack, QC gate, 37 skill) đã sẵn sàng. Việc của bạn: duplicate → drop hợp đồng → trigger Claude setup.
>
> Đọc kèm: [`CLAUDE.md`](./CLAUDE.md) (luật vận hành) · [`SYNC.md`](./SYNC.md) (git + đồng bộ team) · [`MIGRATION.md`](./MIGRATION.md) (update instance cũ lên version master mới).

---

## 0. Trước khi bắt đầu

### Hai chế độ chạy

| Chế độ | Ai dùng | Khác biệt khi setup |
|---|---|---|
| **Máy master của Vincent** | Vincent, SEO Lead trên máy master | Bước 3 đọc được client meta từ tài liệu nội bộ «clients» (ngoài repo, hỏi Lead/Vincent); bước 7-8 chạy đủ |
| **Standalone** (clone repo dự án của team) | Executive, Account, Lead làm remote | Không có tài liệu nội bộ «GTV Ops» (ngoài repo) — bước 3 Claude hỏi thông tin thay vì tự đọc; bước 8 bỏ phần bookkeeping GTV Ops |

Standalone: bước 7 (fork Content Production) do Vincent/Lead thực hiện trên máy master rồi cấp repo content cho team; instance chỉ giữ link fork trong `05-content-plan/README.md`.

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

1. Đọc toàn bộ raw vừa drop + tài liệu nội bộ «<slug>» (ngoài repo, hỏi Lead/Vincent) (nếu trong workspace; standalone → hỏi thông tin còn thiếu).
2. Fill 3 file skeleton trong `00-client-context/`: `client-profile.md` · `marketing-foundation.md` · `kpi-commitments.md`.
3. Tạo `00-client-context/hop-dong-cam-ket.md` từ `_TEMPLATES/hop-dong-cam-ket.md` — trích trường cam kết, công thức đo KPI, mốc nghiệm thu từ hợp đồng.
4. Điền bảng A (Thông tin dự án) trong `index.md` — hết `{{PLACEHOLDER}}`.
5. Dự án có quyền vào hosting hoặc đọc GSC, GA4 bằng tài khoản Google khác: làm theo `_REFERENCE/nhan-khach-server.md` (secret riêng, khoá SSH, bảng quyền, tài khoản `gws`), rồi điền `00-client-context/wp-server.md` từ `_TEMPLATES/wp-server.md`.

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
- **Đồng bộ nguồn sự thật (01/10/2026):** chép `_TEMPLATES/project-sync.yaml` ra root của **cả** repo này và repo content, điền `seo_repo` + `content_repo` giống nhau, commit + push cả hai. Từ đó mỗi team chạy `pull` ở repo mình để có dữ liệu của team kia (`_REFERENCE/project-sync.md`). Khách B2B kỹ thuật / nhiều SKU: nhắc team content dựng Kho tri thức khách (`00-context/kb/`) ngay sau kick-off.

### Bước 8 — Bookkeeping

Chỉ khi chạy trong workspace Vincent:

- Client page tài liệu nội bộ «<slug>» (ngoài repo, hỏi Lead/Vincent) thêm link sang instance.
- Log op `setup` cả 2 nơi: `log.md` của instance + log GTV Ops.

Standalone: chỉ log `log.md` instance.

### Bước 9 — Verify

Chạy checklist mục 2. Fail bất kỳ check nào → báo Claude "verify setup status" để diagnose + fix.

### 1.1 Biến thể: website nội bộ của GTV hoặc TAG (thêm 03/10/2026)

Dùng khi dự án là website của chính công ty (gtvseo.com, theaigrowth.io): không có hợp đồng, không có khách. Chín bước giữ nguyên, khác ở các điểm sau:

- **Bước 2:** không có hợp đồng. Tài liệu brand, định vị, sản phẩm/khoá học → `02-raw/client-docs/`.
- **Bước 3:** bảng A ghi `Hợp đồng` = "Dự án nội bộ, không có hợp đồng"; dòng `Entity` ghi entity sở hữu website (GTV SEO Agency hoặc The AI Growth); `hop-dong-cam-ket.md` ghi "không áp dụng"; `kpi-commitments.md` lấy mục tiêu từ OKR công ty, chưa đặt thì ghi "chưa đặt", không tự đặt số.
- **Bảng B:** giữ đủ 36 dòng. Phần hợp đồng ở #1, BBNT ở #32, ký nhận bàn giao ở #33 ghi "không áp dụng" trong Ghi chú; #12 là kick-off nội bộ (vẫn chốt Tier 2 tại đây); #30 so với mục tiêu OKR thay cho KPI cam kết. Báo cáo gửi SEO Lead/CEO thay cho khách (bảng C).
- **Instance TAG:** deliverable mang nhãn The AI Growth, dùng offer, khoá học, học viên của TAG; không đưa client, case, social proof của GTV vào (`CLAUDE.md` §1). Repo content nối với là fork content cùng brand.
- **Bước 8:** không có client page; chỉ log `log.md` instance.

---

## 2. Verify sau setup

```bash
# 1. Client placeholder phải = 0 hit (Claude đã fill hết)
grep -rn "{{" 00-client-context/ index.md
# Expected: KHÔNG có output

# 2. Log có entry op=setup
grep "setup" log.md
# Expected: ≥1 entry "## [YYYY-MM-DD] setup | ..."

# 3. File thứ 4 đã được tạo ở bước 3 (bản chưng cất HĐ đầy đủ)
ls 00-client-context/hop-dong-cam-ket.md
# Expected: file tồn tại
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

Bộ lệnh vận hành — xem bảng quick-start `README.md` (chi tiết `CLAUDE.md`):

```
"làm công đoạn <n>"
"QC <path> theo công đoạn <n>"
"feedback: <nội dung>"
"ingest <file> vào 02-raw"
```

Team clone repo dự án + nhịp git hằng ngày: `SYNC.md` mục 1-2.

---

**Master version:** xem frontmatter `MIGRATION.md` + git tag.
