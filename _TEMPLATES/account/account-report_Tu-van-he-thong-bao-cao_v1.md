# Tư vấn hệ thống báo cáo khách hàng — Team Account GTV SEO

> **Phạm vi:** review bộ template hiện tại, phương án dashboard (Looker vs HTML), kiến trúc dữ liệu & cách nhập liệu, phân tách nội bộ vs client.
> **Nguồn đọc:** `GTV Ops/wiki/account/` (bộ mẫu T11-2024 + quy trình phối hợp SA–PSP), hợp đồng CareerViet/PVI/MTM, dashboard Looker CRV (ảnh chụp 05/07/2026).
> **Phiên bản:** v1 — 07/2026. Đi kèm 4 file: Email-Templates, BBNT-Templates, Quy-trinh-nghiem-thu (HTML), Dashboard-Demo (HTML).

---

## 1. TL;DR — khuyến nghị

**Chạy mô hình HYBRID 2 lớp, thống nhất "một nguồn số liệu duy nhất":**

1. **Lớp real-time (dashboard online):** HTML dashboard kết nối GA4 + GSC API (tự động) và Google Sheets API (dữ liệu thủ công: ranking SpySERP, KPI cam kết, kế hoạch công việc). Looker CRV hiện tại giữ chạy song song đến khi HTML ổn định — không cắt ngay thứ khách đang ưng.
2. **Lớp pháp lý (định kỳ):** email báo cáo + BBNT + hồ sơ 4 giấy tờ — **snapshot số liệu chốt tại ngày báo cáo**, không phụ thuộc dashboard (dashboard là "cửa sổ xem", chứng từ mới là căn cứ nghiệm thu). Số trong email/BBNT phải chép từ đúng nguồn dashboard đọc, để 2 lớp không bao giờ lệch nhau.

Lý do chiến lược: dashboard đẹp tạo trải nghiệm và niềm tin hằng ngày, nhưng thứ bảo vệ GTV khi đối chiếu — và thứ giải phóng tiền — là bộ chứng từ đúng trình tự. Hai lớp phục vụ 2 việc khác nhau, đừng bắt một công cụ làm cả hai.

---

## 2. Review bộ template hiện tại (T11-2024)

### 2.1. Những gì đang tốt — giữ nguyên khung

| Hạng mục | Đánh giá |
|---|---|
| Tách 5 file theo mục đích (Kết quả / CRO / Technical / Content & Onpage / Entity & Offsite) | ✅ Đúng hướng — giải quyết đúng cái đau "1 file quá nhiều sheet, khách rối". Giữ. |
| Bảng KPI "Cam kết – Kết quả – Tỷ lệ thực tế – Tỷ lệ để nghiệm thu" | ✅ Là xương sống pháp lý, khớp BBNT. Giữ nguyên cấu trúc ở mọi nơi (email, BBNT, dashboard). |
| Quy trình SA–PSP với timeline ngày 28-29-30 + nhịp 2 đợt/tháng | ✅ Rõ vai, rõ ngày. Giữ; đã nhúng vào lưu đồ nghiệm thu (bước B1–B2). |
| File `0. Thông tin dự án` (share tài khoản, author, entity, social có sẵn) | ✅ Kick-off checklist tốt — khớp mục 05 của SOP Account 10 tháng. |

### 2.2. Vấn đề cần sửa

1. **Lệch pháp lý 04 vs 07 ngày** (email cũ ghi cứng 04 ngày, hợp đồng 07 ngày làm việc) → đã chuẩn hóa thành biến `[X ngày]` trong Email-Templates v1. **Việc cần làm: rà lại các email đang gửi ở dự án chạy.**
2. **Số liệu nhập tay nhiều lần** — cùng 1 con số KPI được gõ lại ở: sheet Báo cáo kết quả → email → BBNT → Looker. Mỗi lần gõ lại là một cơ hội sai. → Kiến trúc mục 4: nhập 1 lần ở nguồn, mọi nơi khác đọc/chép từ nguồn đó.
3. **Sheet "Looker- dữ liệu (Hide)" lẫn trong file khách** — dữ liệu trung gian nên tách hẳn ra file nội bộ (mục 5), tránh khách sửa nhầm làm gãy dashboard.
4. **Thiếu mục "Việc cần khách làm" chuẩn hóa** trong email tháng — nguyên nhân số 1 gây trễ dây chuyền (theo SOP 10 tháng: duyệt chậm cấu trúc → trễ cả quý). Đã thêm thành mục cố định trong Template 1.
5. **CRO phần khách cung cấp (lead, doanh thu) hay bị thiếu** → đưa thành dòng nhắc định kỳ T8–T9 (chuẩn bị dữ liệu chuyển đổi cho báo cáo cuối) — đã có trong SOP Account, cần Account bám.
6. **Bảng công việc trong BBNT dài & lẫn task nội bộ** — nguyên tắc đã có từ T11-2024 (không public cloudstack, GSA…) nhưng chưa thành checklist. Đã đưa vào checklist pháp lý của BBNT-Templates.

### 2.3. Điểm học từ Looker CRV (dự án lớn) → chuẩn hóa xuống dự án thường

Dashboard CRV có 4 pattern rất tốt nên thành chuẩn mọi dự án, ở quy mô nhỏ hơn:
- **Executive KPI trên cùng**: cam kết HĐ – thực tế – % run rate – MoM – YoY. Khách C-level chỉ cần nhìn hàng này.
- **Run-rate kép**: KPI run-rate (lũy kế thực tế/kế hoạch) đặt cạnh Time run-rate (% thời gian trôi qua) — trả lời ngay câu "đang nhanh hay chậm so với tiến độ".
- **Bảng RUNRATE 12 tháng** kế hoạch vs thực tế — chính là bảng timeline PL01 của hợp đồng sống trên dashboard; nghiệm thu chỉ việc đọc ra.
- **CR theo nhóm trang** — nối SEO với giá trị kinh doanh (đúng tinh thần mục "Các dữ liệu báo cáo khác" trong email mẫu).

Một số lỗi Looker đang gặp mà HTML demo đã xử lý: nhãn số in trên **mọi** điểm line chart gây đè chữ (→ chỉ nhãn điểm cuối + tooltip khi rê chuột); ô "Invalid dimension"/trống trắng khi filter lỗi; `null` hiển thị thô trong bảng taxonomy (→ để "—" hoặc ẩn); tile trắng khi chưa có dữ liệu (→ ghi rõ "chưa tới kỳ").

---

## 3. Looker Studio vs HTML report — trade-off

| Tiêu chí | Looker Studio | HTML + API |
|---|---|---|
| Thẩm mỹ & brand | Giới hạn (grid Looker, component có sẵn) | ★ Toàn quyền — đúng brand GTV, đẹp như sản phẩm |
| Real-time GA4/GSC | ★ Connector có sẵn, 0 công build | Phải build lớp lấy dữ liệu (một lần, dùng mọi dự án) |
| Dữ liệu thủ công (ranking…) | Qua Google Sheet connector | Qua Sheets API — tương đương |
| Công build ban đầu | Thấp (kéo thả) | Trung bình — nhưng build 1 template, nhân bản mọi dự án chỉ là đổi config |
| Maintain khi GA4 đổi schema | Google lo | GTV lo (điểm trừ chính) |
| Trải nghiệm khách | Chậm, hay "invalid dimension", mobile kém | ★ Nhanh, mobile tốt, tooltip/tab mượt |
| Quyền truy cập | Google account của khách | Link riêng + mật khẩu/token — kiểm soát tốt hơn |
| Khớp format nghiệm thu | Phải tự dựng lại bảng | ★ Bảng KPI/Runrate dựng đúng format BBNT |
| Chi phí vận hành | 0đ | ~0–vài trăm k/tháng (hosting free tier đủ dùng) |

**Khuyến nghị:** đúng như bạn định — **hybrid, thử HTML trước ở 1 dự án**. HTML thắng ở 3 điểm quyết định với tiêu chuẩn của bạn (chuyên nghiệp, khách dễ theo dõi, khớp nghiệm thu); cái giá là lớp data pipeline phải build một lần cho tử tế. Looker vẫn là phương án đúng cho dự án nhỏ/ngắn hạn không đáng công setup.

---

## 4. Kiến trúc dữ liệu & cách nhập liệu (phương án triển khai)

### 4.1. Sơ đồ

```
 NGUỒN TỰ ĐỘNG                       NGUỒN THỦ CÔNG (nhập 1 lần)
 ┌─────────────┐  ┌─────────────┐    ┌──────────────────────────────┐
 │  GA4 API    │  │  GSC API    │    │ Google Sheet «File theo dõi» │
 │ pageview,   │  │ clicks,     │    │ · KPI cam kết theo tháng(PL01)│
 │ sự kiện,    │  │ impressions,│    │ · Ranking SpySERP (SA dán)   │
 │ session     │  │ queries     │    │ · Kế hoạch & báo cáo công việc│
 └──────┬──────┘  └──────┬──────┘    └──────────────┬───────────────┘
        └────────────────┴──────────────────────────┘
                         ▼
        Apps Script (chạy hằng đêm, mỗi dự án 1 config)
        → xuất JSON theo schema thống nhất (= schema trong Dashboard-Demo)
                         ▼
        ┌────────────────────────────────────────┐
        │ HTML Dashboard (1 template dùng chung)  │ ← khách xem link riêng
        │ report.gtvseo.com/<client>?key=...      │
        └────────────────────────────────────────┘
                         ▼ (cuối kỳ)
        Số liệu chốt kỳ → Email báo cáo → BBNT → Hóa đơn
```

### 4.2. Cách nhập dữ liệu — ai làm gì

| Dữ liệu | Ai nhập | Vào đâu | Tần suất |
|---|---|---|---|
| KPI cam kết + timeline PL01 | Account (1 lần khi ký HĐ) | Sheet «File theo dõi» tab `kpi_target` | 1 lần/HĐ (sửa khi có phụ lục) |
| Traffic/Pageview/Sự kiện | — tự động | GA4 API | Hằng đêm |
| Click/Impression/Query | — tự động | GSC API | Hằng đêm |
| Ranking bộ từ khóa | SA (xuất SpySERP → dán) | Sheet tab `ranking`, mỗi kỳ 1 cột kèm ngày tracking | 2 lần/tháng (nhịp 15 & 30) |
| Kế hoạch & trạng thái công việc | PSP nhập, SA soát | Sheet tab `worklog` | Hằng tuần |
| Lead/doanh thu (nếu có) | Khách cung cấp, Account nhập | Sheet tab `conversion_client` | Hằng tháng |

Nguyên tắc: **sheet là nơi duy nhất con người gõ số**; dashboard, email, BBNT đều đọc từ đó ra. Ranking không có API chính thức từ SpySERP bản GTV dùng → chấp nhận bán thủ công qua sheet (đúng ý bạn).

### 4.3. Kỹ thuật (để team build ước lượng)

- **Auth GA4/GSC:** 1 service account GTV, khách grant quyền Viewer property GA4 + GSC (đã nằm sẵn trong checklist share tài khoản của file `0. Thông tin dự án`).
- **Scheduler:** Google Apps Script (miễn phí, nằm luôn trong hệ Google của GTV) đủ cho nhu cầu 1 lần/đêm; nếu sau này cần intraday thì chuyển Cloud Run.
- **Xuất JSON:** Apps Script Web App endpoint (`?client=crv&key=<token>`) hoặc ghi file JSON vào hosting tĩnh. Schema = đúng object `DATA` trong `account-report_Dashboard-Demo_v1.html` — demo hôm nay chính là contract cho pipeline, cắm dữ liệu thật vào là chạy.
- **Hosting:** 1 site tĩnh (Cloudflare Pages/Netlify — free tier) + mỗi khách 1 đường dẫn & token riêng. KHÔNG đưa dữ liệu khách này vào bundle của khách khác.
- **Bảo mật:** token trong link + noindex; dữ liệu nhạy cảm (doanh thu khách) chỉ hiển thị khi khách bật. Không nhúng API key trong HTML — mọi call API nằm ở lớp Apps Script.
- **Fallback pháp lý:** nút "Xuất PDF kỳ này" (print stylesheet) → chính là file đính kèm email báo cáo, số khớp 100% dashboard.

### 4.4. Ước lượng công

| Việc | Công |
|---|---|
| Chuẩn hóa Sheet «File theo dõi» template | 0,5 ngày |
| Apps Script GA4+GSC+Sheet → JSON | 2–3 ngày |
| Hoàn thiện HTML template từ demo (print CSS, token, config đa dự án) | 2–3 ngày |
| Pilot 1 dự án (đề xuất: CareerViet, chạy song song Looker 1 tháng) | 1 tháng theo dõi |

---

## 5. Tách nội bộ vs client (chuẩn hóa)

| Tài liệu | Nội bộ | Client | Ghi chú |
|---|---|---|---|
| Email báo cáo, BBNT, ĐNTT, hóa đơn | ✔ lưu | ✔ nhận | Lớp pháp lý — cả 2 bên giữ |
| HTML dashboard | ✔ | ✔ (link riêng) | Chỉ số đã thống nhất công khai |
| Sheet «File theo dõi» | ✔ | ✘ | Nguồn nhập liệu — khách không sửa |
| 5 file báo cáo hạng mục (Kết quả/CRO/Technical/Content/Entity) | ✔ | ✔ quyền Comment | Giữ nguyên tắc T11-2024: chỉ sheet public, không cloudstack/GSA/task nội bộ |
| Kế hoạch nội bộ (PSP worklog đầy đủ) | ✔ | ✘ | SA copy phần công bố sang Báo cáo công việc |
| Lưu đồ quy trình nghiệm thu, SOP, template review này | ✔ | ✘ | Training nội bộ |

---

## 6. Lộ trình đề xuất

1. **Tuần 1:** duyệt bộ template v1 (email + BBNT) → áp cho kỳ báo cáo gần nhất; rà lỗi 04/07 ngày ở các dự án đang chạy.
2. **Tuần 2–3:** build pipeline Apps Script + hoàn thiện HTML template từ demo; chuẩn hóa Sheet «File theo dõi» cho CRV.
3. **Tháng tiếp theo:** pilot CRV chạy song song Looker; lấy feedback khách; chốt go/no-go nhân bản sang PVI, MTM và dự án mới.
4. **Sau pilot:** file-back quy trình chốt vào `GTV Ops/wiki/account/` (wiki hóa), đóng gói thành SOP onboarding Account.

## Câu hỏi mở (cần Vincent chốt dần)

- Domain report: dùng subdomain `report.gtvseo.com` hay domain riêng trung tính?
- Ahrefs API (đã có MCP) có đưa vào dashboard không — đề xuất: chỉ cho dự án có KPI liên quan (Ref.Domain, Citation AIO như MTM), tránh nhiễu.
- Dashboard có tab "Công việc & kế hoạch" đọc từ worklog không, hay giữ công việc trong email/sheet như hiện tại?
