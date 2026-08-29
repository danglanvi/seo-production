# BÀN GIAO TEAM — Vận hành dự án SEO {{CLIENT}} bằng AI

> 📋 **Template client-neutral.** Copy ra ROOT của instance thành `BAN-GIAO-TEAM.md`, thay `{{CLIENT}}` / `{{DOMAIN}}` / `{{MO_HINH}}` và xóa các mục không áp dụng. File này là thứ team đọc ĐẦU TIÊN khi nhận folder.
>
> Hệ báo cáo chưa kích hoạt (instance mới) → giữ banner cảnh báo bên dưới cho tới khi làm xong `09-reporting/WEEKLY-DATA-CHECKLIST.md` §5.

> ⚠ **Hệ báo cáo tuần/tháng/quý đã cài nhưng CHƯA KÍCH HOẠT** — workbook data chưa dựng. Việc đầu tiên của SEO Lead: chạy mục **§5 «Kích hoạt hệ»** trong `09-reporting/WEEKLY-DATA-CHECKLIST.md`. Xong mục đó thì mọi câu lệnh ở mục 3/3b chạy được ngay.
>
> Cài đặt từ đầu (Claude Code / Codex / Antigravity / MCP / chìa khóa): deck **`GTV_SEO-Production_huong-dan-cai-dat_v1.html`** ở root folder.

## 1. Folder này là gì

Toàn bộ hệ vận hành dự án SEO {{CLIENT}}: luật (`CLAUDE.md`), SOP cho AI (`skills/`), script kéo số + ráp slide, registry 33 công đoạn (`index.md`), timeline (`log.md`), deliverable theo workstream (00→12). **Copy nguyên folder về máy là đủ file** — chỉ thiếu 1 thứ duy nhất: file chìa khóa robot (mục 2).

**Mô hình dự án: {{MO_HINH — THỰC THI | ADVISORY}}.** Với ADVISORY: GTV quản lý/chỉ đạo/đào tạo/review/QC, khách tự thực thi in-house; cột «Thực thi» trong `index.md` bảng B ghi rõ việc nào của ai, và deck tuần có slide **tiến độ adoption khuyến nghị** (GTV recommend → khách đã làm/chưa làm).

## 1b. Ai làm gì trong folder này

| Vai trò | Việc chính | Chỗ làm việc |
|---|---|---|
| **SEO Lead Project** | Điều phối theo `index.md` bảng B (quản đốc: `ORCHESTRATOR.md`) · duyệt plan AI · QC random 25-30% (`03-audits/qc/`) · chốt kích hoạt hệ báo cáo | Toàn instance |
| **SEO Executive (data)** | Nhịp tuần: chuẩn bị data trước **17:00 thứ Tư** theo `09-reporting/WEEKLY-DATA-CHECKLIST.md` · nhịp kỳ theo `PERIOD-DATA-CHECKLIST.md` | `09-reporting/` + workbook Drive |
| **Account** | Sync tuần với Lead (skill `acc-weekly-sync`) · gửi báo cáo · nhắc hạng mục khách đang giữ · nghiệm thu (`gtv-client-report`) | `10-client-management/` + `09-reporting/` |
| **Content Leader / Executive** | Plan + brief + QC bài ở `05-content-plan/` (KHÔNG viết bài ở đây — bài viết chạy ở fork `Content Production - {{CLIENT}}/`) | `05-content-plan/` + fork content |

Lệnh chuẩn per trạm: `COMMANDS.md`. Luật từng trạm: `CLAUDE.md` trong mỗi folder 00→12.

## 2. Chuẩn bị máy (làm 1 lần)

**Cách nhanh nhất:** mở folder này bằng Claude Code rồi nói *"cài đặt giúp tôi repo này"*. AI đọc
`_SETUP/SETUP-MAY.md` và dẫn bạn đi hết, kể cả phần tạo chìa khóa Google.

Muốn tự làm tay thì đây là 4 thứ cần:

| # | Cần | Cách có |
|---|---|---|
| 1 | Mac + **Claude Code** | Cài từ https://claude.com/claude-code — đăng nhập tài khoản được cấp |
| 2 | **Python 3** + thư viện | `python3 -m pip install -r requirements.txt` |
| 3 | **Node + Playwright** (tự soi lỗi slide) | `npx playwright install chromium` (lần đầu tự tải) |
| 4 | **Chìa khóa robot của riêng bạn** | `_SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md` → xong chạy `python3 _SETUP/setup_credential.py register <file>.json` |

Khám lại bất cứ lúc nào: `python3 _SETUP/setup_doctor.py` — nó chỉ đúng chỗ còn thiếu và lệnh sửa.

**Email robot ≠ file chìa khóa:**
- **Email robot** = «địa chỉ» của robot. Dùng để SHARE sheet/folder. Không phải bí mật.
- **File chìa khóa** `.json` = chứng minh máy này đúng là robot đó. File bí mật: KHÔNG gửi email,
  KHÔNG bỏ vào Drive share chung, KHÔNG commit vào folder. Mỗi máy giữ 1 bản ở `~/.config/gcp/`.
- **Mỗi người một robot riêng.** Bạn tự tạo trong Google Cloud của mình, rồi xin Lead share các file
  Drive cho địa chỉ robot đó (`python3 _SETUP/setup_credential.py share` in sẵn danh sách + đoạn tin
  nhắn để copy). Nghỉ việc thì xóa đúng robot của mình, không ảnh hưởng ai.
- Quyền share: xin **Editor** làm mặc định — `_SETUP/CHIA-QUYEN-DRIVE.md` giải thích vì sao và nêu
  các ngoại lệ cố ý để Viewer.
- Playwright KHÔNG có sẵn trong Claude Code — chưa cài thì AI vẫn dựng được deck HTML nhưng không tự
  soi lỗi từng slide được.

**Dùng GPT Codex / Antigravity (tùy chọn):** mở folder này trong Codex hoặc Antigravity thì `AGENTS.md` tự dẫn toàn bộ luật — làm được phân tích, audit, plan, QC. **Giới hạn:** không chạy được báo cáo tuần/tháng (2 skill `gtv-weekly-report`, `gtv-client-report` chỉ có trên Claude Code); chỉ làm draft thủ công theo template và ghi rõ giới hạn, không gửi khách.

## 3. Chạy báo cáo tuần — 1 câu lệnh (sau khi kích hoạt hệ)

Mở Terminal → `cd` vào folder này → gõ `claude` → gõ prompt:

- `làm báo cáo tuần {{CLIENT}}` — chạy tuần vừa khép (Thứ Năm→Thứ Tư)
- `làm báo cáo tuần 12` — chạy tuần cụ thể
- `chạy lại báo cáo tuần 12` — data về trễ, chạy đè bản cũ
- `phân tích tuần này có pattern gì` — chỉ phân tích, không dựng deck

AI tự làm 5 bước: kéo số → phân tích → viết nhận xét → ráp deck → tự soi lỗi từng slide. Ra bản **DRAFT** để Lead duyệt — AI không tự gửi khách. Muốn tự động: nói AI «đặt cron thứ Năm 08:00 chạy báo cáo tuần {{CLIENT}} bản draft».

**Khung deck tuần ~11 slide** theo agenda catchup của khách; nhóm trang trên deck bám `page_groups` của dự án (job site: Job Listing/Job Detail · e-commerce: Category/PDP…). Task chưa done tự chuyển tiếp sang plan tuần kế (rule carry-over) — team chỉ cần giữ status trong sheet đúng. **Output CHỈ là file HTML** — không xuất PDF (luật 23/07/2026).

## 3b. Chạy báo cáo THÁNG / QUÝ và làm OKRs quý

Cùng bộ máy, khác nhịp và độ dài: **TUẦN ~11 slide · THÁNG ~26 slide · QUÝ ~45–50 slide** (tháng khép quý làm **deck kép**: lớp tháng + lớp tổng kết quý). Quý dự án tính theo T1 hợp đồng, KHÔNG theo quý dương lịch — tra bảng A `index.md`.

- `làm báo cáo tháng {{CLIENT}}` — sau khi data tháng khép (ngày 2–4 tháng kế)
- `làm báo cáo quý <N> dự án {{CLIENT}}` — tháng khép quý, cần thêm ~1 ngày cho lớp so cùng kỳ
- `đối chiếu OKRs quý với sheet của team` — sau khi team chỉnh sheet OKRs (skill `gtv-project-okrs`)
- `lên OKRs quý <N> cho {{CLIENT}}` — dựa trên kết quả quý vừa khép

**Chạy tay từng bước:** `09-reporting/RUNBOOK-bao-cao-ky.md`. **Data team phải chuẩn bị:** `09-reporting/PERIOD-DATA-CHECKLIST.md`. Ba thứ hay quên nhất: (1) BẢNG 1 phải giữ **cả hai cột giá trị gốc**, không chỉ Δ và %; (2) tab URL-level **giữ nguyên thứ tự cột** giữa các kỳ — đổi mà không báo thì danh sách tăng/giảm đảo ngược hoàn toàn; (3) chỉ số so cùng kỳ phải **đối chiếu định nghĩa event/metric giữa hai năm**.

**Link nguồn trên slide:** mỗi slide data có dòng nguồn ở đáy, bấm được — mở thẳng đúng tab đã dựng nên con số đó. Có workbook/file mới → **báo để khai vào `source_links:`**, nếu không nó nằm ở khối «chưa có link».

**Bản PowerPoint:** nói «xuất deck sang PowerPoint» → file `.pptx` mà text/bảng/biểu đồ/hyperlink đều là đối tượng thật. Bản **HTML vẫn là bản chuẩn** để trình chiếu và gửi khách.

**⚠ Sửa deck rồi thì báo:** ai sửa chữ trực tiếp trên file `.html` đã giao thì **nói với AI trước khi build lại** — AI back-port phần sửa về file nguồn rồi mới dựng bản mới. Không nói thì lần build kế tiếp xoá sạch phần sửa.

## 4. Data phải chuẩn bị TRƯỚC 17:00 THỨ TƯ (người: SEO Executive)

**Tất cả là Google Sheets ONLINE share cho robot — không ai tải file về folder.** Chi tiết + luật format: `09-reporting/WEEKLY-DATA-CHECKLIST.md`. Tóm tắt: tạo workbook «Report Tuần N» đúng cú pháp tên trong folder Drive cố định · refresh **cả 2 cột kỳ** mọi tab Đánh giá · cập nhật run-rate + section tuần/tuần kế · KHÔNG đổi tên tab / header cột / chèn ghi chú vào giữa bảng.

Quên bước nào → AI vẫn chạy nhưng ra bản SLIM + slide liệt kê đúng phần thiếu.

## 5. Deck dùng thế nào (file .html)

- **Phím E**: bật/tắt sửa chữ trực tiếp — bấm E lần nữa là lưu (trên máy mình).
- **Phím T / nút ☰ Slides**: khung thumbnail bên trái — click nhảy slide.
- **▶ Present**: chiếu toàn màn hình. Gửi khách: gửi thẳng file `.html` (tự chứa, mở bằng mọi trình duyệt).

## 6. Khi có góp ý / lỗi

Ghi vào `12-feedback-lessons/feedback-log.md` hoặc nói thẳng với AI («slide X sai chỗ Y») — hệ tự vá luật để tuần sau không lặp lại. Sổ cái công việc: `index.md` + `log.md`.
