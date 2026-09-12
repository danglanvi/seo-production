---
name: acc-kickoff-setup
description: "Mốc cứng T1 của Account cho dự án SEO GTV: phân tích hợp đồng đã ký (KPI cam kết, scope, SLA duyệt content, điều khoản đặc biệt) để điền 00-client-context/ của instance SEO Production + sinh checklist lấy từ khách 4 nhóm. Use when: 'kick-off [client]', 'setup context từ hợp đồng [client]', 'checklist cần khách cung cấp'."
metadata:
  version: "1.0"
---

# Account Kick-off & Setup (T1)

Mốc cứng T1 của Account trong dự án SEO 8/10/12 tháng: **phân tích hợp đồng → lấy đủ access & thông tin từ khách trong 2 tuần đầu → kick-off (Account chủ trì) → chốt SLA duyệt + đầu mối duyệt phía khách**. Checklist nghiệp vụ từ training Account 10 tháng đã chưng cất trong Bước 1–5 bên dưới. Tên training là nguồn lịch sử, không yêu cầu kho ngoài repo. Nguồn số của từng client vẫn là hợp đồng/phụ lục đã ký.

🔒 **Tài liệu nội bộ GTV** — output của skill này KHÔNG gửi khách nguyên bản. Riêng bảng checklist lấy từ khách được thiết kế để gửi được, nhưng bản gửi đi phải qua Account biên tập (bỏ ghi chú nội bộ, thêm xưng hô/ngữ cảnh client).

## Phân vai (không lấn sân)

| Việc | Skill/quy trình phụ trách | Ranh giới cụ thể |
|---|---|---|
| Proposal, pitch, cam kết KPI TRƯỚC khi ký | `gtv-proposal` · `gtv-pitch-review` | Skill này chỉ chạy SAU khi hợp đồng đã ký |
| Dựng instance SEO Production (duplicate master, retiming gói, advisory, fork content, bookkeeping) | `SEO Production/SETUP.md` — protocol "setup client" 9 bước | Skill này là **lớp Account**; khi chưa có instance chỉ chuẩn bị hồ sơ cục bộ, chưa hoàn tất setup vận hành |
| OKRs năm/quý của dự án (công đoạn #8) | `okrs-gtv-tag-framework` | Skill này chỉ trích KPI cam kết từ hợp đồng, không viết OKRs |
| Kick-off nội bộ chốt Tier 2 checklist | Lead + team (SETUP bước 6) | Skill này chỉ verify việc đó đã xong trước kick-off khách |
| Sync tuần sau T1, theo dõi mốc cứng T2-T10 | `acc-weekly-sync` | Skill này kết thúc khi "kick-off xong" đạt definition-of-done |
| Báo cáo tháng/quý/nghiệm thu cho khách | `gtv-client-report` | — |

## Input

**Required:**
- Tên/slug client và bộ nguồn đã ký do người dùng cung cấp. Không cần `$INSTANCE` để chuẩn bị hồ sơ cục bộ; muốn cập nhật instance thì instance phải được xác định và qua setup.
- Hợp đồng đã ký + Phụ lục + Tài liệu kỹ thuật (trong `02-raw/contracts-proposals/` của instance, hoặc user đưa file/paste).

**Optional:**
- `$INSTANCE` — root instance SEO người dùng chỉ định hoặc path đã xác nhận trong task/hồ sơ; không tự dò các repo lân cận.
- `$OUTPUT_DIR` — folder chuẩn bị cục bộ; mặc định folder đích trong instance đã chọn, mặc định `10-client-management/kickoff-prep/`; đang ở SEO master thì hỏi instance/folder làm việc của client, không tạo hồ sơ client trong master. Chốt bằng ngữ cảnh đã rõ, chỉ hỏi phần thiếu.
- `$CLIENT_TYPE` — SME / tập đoàn. Tập đoàn → mọi deadline hẹn khách phải trừ hao thời gian duyệt nội bộ của họ.
- `$LOCAL` — dự án local hay không (quyết định item Google Business Profile trong checklist Access).
- Ngày kick-off dự kiến + danh sách tham dự 2 bên.

## Workflow

### Bước 0 — Scope gate

1. Xác định client và chế độ: có `$INSTANCE` → kiểm đã qua SETUP (bảng A `index.md` hết placeholder); thiếu/chưa setup → chỉ chuẩn bị hồ sơ tại `$OUTPUT_DIR`, ghi “CHUẨN BỊ — CHƯA ĐỒNG BỘ INSTANCE”, không sửa registry/context của instance. Hoàn tất setup thực tế vẫn cần Lead chạy protocol tại instance trước kick-off khách.
2. Hỏi `$CLIENT_TYPE` và `$LOCAL` nếu chưa rõ — hai biến này đổi nội dung checklist và cách hẹn deadline.
3. Xác nhận kick-off **nội bộ** (Lead + team chốt Tier 2 checklist — SETUP bước 6) đã chạy hoặc đã lên lịch TRƯỚC buổi kick-off khách. Chưa có → flag vào output, không tự bỏ qua.

### Bước 1 — Phân tích hợp đồng

Đọc toàn bộ hợp đồng + Phụ lục + Tài liệu kỹ thuật. Trích theo 4 nhóm — mỗi giá trị kèm vị trí nguồn (Điều/Phụ lục/trang):

1. **KPI cam kết** — traffic (Organic Session/tháng hoặc tổng kỳ), ranking (bộ từ khóa TOP x%, duy trì vs thúc đẩy), KPI GEO/AI nếu có, thời hạn + mốc tính từng KPI, công cụ đo đã chốt (SpySERP/GA4/Ahrefs…), trọng số.
2. **Scope** — số bài content, nhóm sản phẩm/dịch vụ trong phạm vi, thị trường/ngôn ngữ, mô hình thực thi/advisory, gói timeline 8/10/12 tháng.
3. **SLA & quy trình** — SLA duyệt content phía khách (chuẩn GTV: **3-5 ngày làm việc / lô bài** — hợp đồng ghi khác thì lấy theo hợp đồng và note lệch chuẩn), điều khoản auto-accept nếu có, nhịp báo cáo.
4. **Điều khoản đặc biệt** — độc quyền ngành, song ngữ, ngoại tệ, gia hạn cuối kỳ, điều kiện nghiệm thu/bảo hành, phạt/thưởng.

Chế độ instance: mọi đường dẫn sau tính từ `$INSTANCE`, ghi theo template đã có. Chế độ chuẩn bị: dùng skeleton Output bên dưới để ghi bản trích hợp đồng/KPI tại `$OUTPUT_DIR`, có cột nguồn; không yêu cầu template ngoài repo và không ghi đè bản context chính thức. Nếu template cần thiết thiếu khi cập nhật instance thì báo Lead hoàn tất SETUP trước.

Ghi trong instance đã setup:
- `00-client-context/hop-dong-cam-ket.md` — theo `_TEMPLATES/hop-dong-cam-ket.md` (luật điền mục 0: không suy diễn số liệu, `n/a` thay vì bỏ trống, ghi rõ VAT).
- `00-client-context/kpi-commitments.md` — bảng KPI vận hành.
- Đồng bộ bảng A `index.md` (dòng Hợp đồng, KPI cam kết, Mô hình).

### Bước 2 — Sinh checklist lấy từ khách (4 nhóm)

Sinh bảng checklist gửi khách theo **đúng 4 nhóm + đúng items** đã đóng gói ngay bên dưới (nguồn lịch sử: training mục 05) — không thêm bớt item cốt lõi, chỉ tùy biến theo `$LOCAL` và điều khoản hợp đồng:

- **Access:** Google Search Console + Google Analytics 4 · CMS admin (WordPress/khác) · Hosting/server hoặc đầu mối coder có quyền · Google Business Profile (nếu dự án local).
- **Thông tin doanh nghiệp:** Tài liệu sản phẩm/dịch vụ + bảng giá (nếu công khai) · USP, điểm khác biệt so đối thủ, POPs, Benefits · Brand guideline (nếu có) + quy định pháp lý ngành · Danh sách chi nhánh/đại lý/NAP (cho content entity).
- **Con người:** **1 đầu mối duyệt content — có quyền quyết định, không duyệt qua nhiều tầng** · Coder/dev phụ trách website + cam kết thời gian xử lý · Marketing lead (phối hợp brand search, social, kênh khác).
- **Quy trình làm việc:** SLA duyệt content 3-5 ngày làm việc / lô bài · Lịch báo cáo tháng + kênh liên lạc chính thức · Quy trình thay đổi phạm vi (mọi thay đổi qua Account → SEO Lead Project đánh giá).

Format bảng: mỗi item 1 dòng với cột **Trạng thái** (☐ chờ / ✅ đã nhận / ⚠️ vướng) + **Ngày nhận** + **Đầu mối phía khách** + **Deadline (Fixline → Deadline)**. Deadline tổng: đủ 4 nhóm trong **2 tuần đầu T1** (access thiếu → audit + tracking chuyển đổi trễ; tracking bắt buộc xong ≤ T3).

### Bước 3 — Agenda kick-off + form meeting note

1. Soạn agenda theo `_TEMPLATES/kick-off.md` trong instance đã setup; chế độ chuẩn bị dùng mục 3 của skeleton Output (công đoạn #12, Account chủ trì): giới thiệu team + vai trò → mục tiêu + KPI cam kết (đọc từ kpi-commitments) → timeline gói + 5 pha + mốc cứng → RACI + việc cần khách làm + SLA phản hồi → kênh liên lạc + nhịp báo cáo + Q&A.
2. Nhắc thứ tự bắt buộc: **kick-off nội bộ (Tier 2) chạy TRƯỚC kick-off khách**; chế độ instance ghi kết quả Tier 2 vào dòng #12 `index.md`; chế độ chuẩn bị ghi trạng thái còn chờ trong hồ sơ, không cập nhật #12.
3. Chuẩn bị form meeting note theo `_TEMPLATES/meeting-note.md` trong instance; chế độ chuẩn bị dùng bảng Ngày họp · Người dự · Quyết định · Action · Owner · Deadline · Nguồn xác nhận trong mục 4 của Output — ghi trong 24h sau buổi, mọi action item có đúng 1 owner + deadline, decision chạm KPI/scope/timeline/budget phải có xác nhận email.

### Bước 4 — Định deadline theo 2 mốc Fixline → Deadline

Mọi deadline hẹn khách dùng 2 mốc: **Fixline** (mốc nhắc/chốt nội bộ) → **Deadline** (mốc thật). `$CLIENT_TYPE` = tập đoàn → cộng thêm buffer duyệt nội bộ phía khách vào giữa 2 mốc. Điền cột deadline vào bảng checklist Bước 2 + Next steps của agenda.

### Bước 5 — Definition of done + bookkeeping

"Kick-off xong" khi và chỉ khi:
1. ☐ Đủ **4 nhóm checklist** (Access · Thông tin DN · Con người · Quy trình) — không nhóm nào còn item cốt lõi ☐ chờ.
2. ☐ **Đầu mối duyệt phía khách xác nhận** vai trò (email/biên bản) — 1 người, có quyền quyết.
3. ☐ **SLA duyệt content chốt bằng văn bản** (email xác nhận hoặc meeting note khách confirm).

Chưa đủ các điều kiện trên → trạng thái là "kick-off ĐANG MỞ", liệt kê items còn thiếu + owner + deadline. Chỉ khi instance đã setup và đủ các điều kiện trên mới update `index.md` dòng #12, append `log.md` op `meeting`, bàn giao cho `acc-weekly-sync`. Chế độ chuẩn bị chỉ hoàn tất bộ file chuẩn bị, chưa đóng mốc kick-off.

## Output

Trả file `<client>_acc-kickoff-setup_v<N>.md` (tăng version) vào `$INSTANCE/10-client-management/` khi instance đã setup, hoặc `$OUTPUT_DIR` ở chế độ chuẩn bị. Trả link file, nguồn và trạng thái. Chế độ chuẩn bị không đánh dấu #12 đã xong hay bàn giao nhịp vận hành; log tại repo sở hữu folder đích theo loại việc thực tế. Skeleton:

```markdown
# <CLIENT> — Account Kick-off & Setup (T1)
> Ngày: YYYY-MM-DD · Instance: <path> · Gói: <8/10/12> tháng · Loại khách: <SME/tập đoàn> · 🔒 Nội bộ GTV — bản gửi khách phải qua Account biên tập

## 1. Tóm tắt hợp đồng cho Account (trích từ hop-dong-cam-ket.md)
| Nhóm | Nội dung | Nguồn (Điều/PL) |
|---|---|---|
| KPI cam kết | <traffic / ranking / GEO + thời hạn + công cụ đo> | |
| Scope | <số bài · nhóm SP · thị trường · mô hình> | |
| SLA duyệt content | <3-5 ngày làm việc/lô — hoặc theo HĐ> | |
| Điều khoản đặc biệt | <độc quyền/song ngữ/auto-accept/bảo hành…> | |

## 2. Checklist lấy từ khách (gửi được sau khi Account biên tập)
### Access / Thông tin doanh nghiệp / Con người / Quy trình làm việc
| # | Hạng mục | Đầu mối phía khách | Fixline | Deadline | Trạng thái | Ngày nhận |
|---|---|---|---|---|---|---|

## 3. Agenda kick-off (Account chủ trì)
| # | Nội dung | Phút | Người dẫn |
|---|---|---|---|
- Pre-check: ☐ kick-off nội bộ Tier 2 đã chạy · ☐ ghi chú dòng #12 index.md

## 4. Form meeting note
| Ngày họp | Người dự | Quyết định | Action | Owner | Deadline | Nguồn xác nhận |
|---|---|---|---|---|---|---|

## 5. Definition of done — kick-off xong?
- [ ] Đủ 4 nhóm checklist  ·  [ ] Đầu mối duyệt xác nhận  ·  [ ] SLA chốt bằng văn bản
→ Trạng thái: <XONG | ĐANG MỞ — items thiếu + owner + deadline>

## 6. Bookkeeping
- index.md #12: <updated?> · log.md op meeting: <appended?> · Bàn giao → acc-weekly-sync từ tuần <N>
```

## Behavior Gates

**#1 Think Before** — Trước khi viết: đã xác định chế độ chuẩn bị hay cập nhật instance, folder đích và trạng thái setup chưa? Hợp đồng đủ bộ (HĐ + Phụ lục + Tài liệu kỹ thuật) chưa? Khách SME hay tập đoàn? Dự án local không? Thiếu → hỏi, không giả định.

**#2 Evidence** — Mọi số KPI/scope/SLA trích từ hợp đồng phải kèm vị trí nguồn (Điều/Phụ lục). Hợp đồng không có → `n/a`, không suy diễn. Số lệch chuẩn GTV (vd SLA khác 3-5 ngày) → ghi rõ "theo HĐ, lệch chuẩn".

**#3 Trung thành tài liệu training** — Checklist 4 nhóm lấy ĐÚNG items mục 05; không sáng tác nhóm mới, không bỏ item "1 đầu mối duyệt có quyền quyết".

**#4 Nội bộ trước, khách sau** — Kick-off nội bộ (Tier 2) luôn trước kick-off khách. Output là tài liệu nội bộ; bản gửi khách qua Account biên tập.

**#5 Deadline 2 mốc** — Mọi deadline hẹn khách đều Fixline → Deadline; tập đoàn cộng buffer duyệt nội bộ.

## Anti-patterns

- ❌ Coi bộ hồ sơ chuẩn bị là instance đã setup hoặc tự dựng instance thay SETUP.md.
- ❌ Tuyên bố "kick-off xong" khi mới họp xong buổi kick-off — DoD là đủ 4 nhóm checklist + đầu mối duyệt xác nhận + SLA văn bản.
- ❌ Chấp nhận "team khách cùng duyệt" — phải đúng 1 đầu mối có quyền quyết, không duyệt qua nhiều tầng.
- ❌ Gửi khách nguyên bản output nội bộ (kèm ghi chú rủi ro, ngôn ngữ vận hành GTV).
- ❌ Tự viết OKRs dự án hoặc tự retiming 33 công đoạn — route đúng skill/protocol.
- ❌ Hẹn khách 1 mốc deadline duy nhất, hoặc quên trừ hao duyệt nội bộ với khách tập đoàn.
- ❌ Điền số KPI/giá trị hợp đồng ước lượng "cho đủ bảng" — không có nguồn = `n/a`.
- ❌ Copy giá trị hợp đồng thật vào deliverable hướng ra ngoài (luật 🔒 của hop-dong-cam-ket.md).

## References & wiki

- Checklist và skeleton cần để chuẩn bị đã có trong skill này; training «quy trình SEO 10 tháng Account» là nguồn lịch sử.
- `SEO Production/SETUP.md` — protocol setup client 9 bước (upstream của skill này).
- `SEO Production/index.md` — bảng B: dòng #1 (ký HĐ + OKRs), #12 (kick-off — PIC Account).
- `SEO Production/_TEMPLATES/hop-dong-cam-ket.md` · `_TEMPLATES/kick-off.md` · `_TEMPLATES/meeting-note.md` — template điền trực tiếp.
- Skill anh em: `acc-weekly-sync` (nhịp tuần sau T1) · `gtv-client-report` (báo cáo tháng/quý) · `gtv-proposal` (trước ký) · `okrs-gtv-tag-framework` (OKRs).

## Changelog

- 2026-09-12: path instance do user xác định; hồ sơ chuẩn bị có folder/output rõ, giữ trạng thái mở và gate setup/kick-off.

- **v1.0 (2026-07-19):** tạo mới — chưng cất từ tài liệu training Account 10 tháng (mục 01-05) + SEO Production master (SETUP 9 bước, template kick-off/meeting-note/hop-dong-cam-ket).
