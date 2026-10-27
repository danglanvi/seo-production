# Data Paths — Ahrefs MCP map + SpySERP/GA4 export + Path C

> Data ladder cho gtv-client-report. 🔴 Nguyên tắc bất di bất dịch (Điều 1 Định nghĩa HĐ — contract-playbook): **thứ hạng nghiệm thu = SpySERP** (qua Google Search API, check Google.com.vn khu vực Việt Nam) · **traffic nghiệm thu = GA4** (Organic Session) · **Citation AI Overview = Ahrefs**. Hai nguồn lệch nhau → SpySERP/GA4 là số nghiệm thu, Ahrefs chỉ minh họa trend.

## 1. Path A — Ahrefs MCP (chart minh họa + GEO/AIO)

⚠️ **Cảnh báo phạm vi:** Ahrefs KHÔNG phải nguồn chuẩn hợp đồng cho thứ hạng (SpySERP) và traffic (GA4). Path A chỉ dùng cho: (a) chart minh họa trend đính kèm báo cáo, (b) GEO/AIO citation — hạng mục duy nhất Ahrefs là công cụ đo chính thức theo Điều 1 HĐ. Trước khi gọi: báo số call dự kiến + chờ xác nhận (Bước 0 SKILL.md). Gọi `doc` trước khi dùng tool lần đầu.

**Map ô bảng KPI → tool:**

| Ô cần điền / minh họa | Tool Ahrefs MCP | Ghi chú |
|---|---|---|
| Tìm project + bộ keyword đã setup | `management-projects`, `management-project-keywords` | chạy trước để lấy project id/scope |
| Thứ hạng bộ keyword (trend minh họa) | `rank-tracker-overview` | ❌ không dùng làm số nghiệm thu TOP |
| So sánh đối thủ (phụ lục nếu account cần) | `rank-tracker-competitors-overview` | optional |
| Traffic/keyword trend (minh họa) | `gsc-performance-history`, `gsc-keywords`, `gsc-positions-history` | GSC data — vẫn không thay GA4 |
| Organic keywords / metrics history (minh họa) | `site-explorer-organic-keywords`, `site-explorer-metrics-history` | |
| GEO — số lượng AI responses trích dẫn site | `site-explorer-ai-responses-count`: KPI AIO theo từ khoá đọc `google_ai_overviews_keywords`; trích dẫn từ prompt cộng các nền tảng chatgpt, google_ai_overviews, google_ai_mode, gemini, perplexity, copilot. Không báo `all_platforms` (cộng cả hai loại, kiểm site agency mẫu 19/10/2026: 645 = 522 + 123) | ✅ nguồn đo AIO hợp lệ theo Điều 1; đối chiếu định nghĩa KPI trong HĐ trước khi chọn trường |
| GEO — brand mentions/citations trong AI | nhóm `brand-radar-*` (`brand-radar-mentions-overview`, `brand-radar-mentions-history`, `brand-radar-cited-pages`, `brand-radar-ai-responses`) | evidence cho hàng GEO; kèm ngày query |
| Chart time series | `render-time-series-chart` | 🔴 tool trả về `render_with` metadata → BẮT BUỘC gọi render tool, không tự tóm tắt raw data |
| Bảng data | `render-data-table` | như trên |
| Scorecard KPI | `render-scorecard` | như trên |

**Provenance:** mỗi số/chart lấy từ Ahrefs phải ghi caption `Nguồn: Ahrefs <tool>, query ngày <dd/mm/yyyy>` — minh họa cũng phải truy được nguồn (Behavior Gate #2).

## 2. Path B — Export paste (nguồn chuẩn hợp đồng)

### 2a. SpySERP export → % đạt TOP theo bộ

Khớp layout sheet đích `BÁO CÁO THỨ HẠNG (TOP)` của workbook: `STT | Keywords | URL | Đầu dự án | Tháng thứ 1…12` + hàng **Ngày tracking** (vd 30/06, 30/07) + summary TOP 3 / TOP 5 / TOP 10.

Quy trình đọc:
1. Xác nhận export đúng cấu hình: **Google.com.vn, khu vực Việt Nam**, đúng bộ keyword cam kết (đối chiếu số keyword với sheet — vd "BỘ 81 KEYWORD CAM KẾT").
2. Ghi **ngày tracking** — bắt buộc xuất hiện trong cột HẠNG MỤC hoặc GHI CHÚ của bảng KPI.
3. Đếm keyword theo ngưỡng, áp **TOP lồng nhau**: vị trí ≤3 đếm vào cả TOP3, TOP5, TOP10; vị trí 4-5 đếm vào TOP5, TOP10; vị trí 6-10 đếm vào TOP10. Chỉ tính **liên kết tự nhiên** (không ảnh/video/Maps/Ads/AI Overview).
4. % đạt = số keyword đạt ngưỡng ÷ tổng keyword trong bộ. So với % cam kết → cột THỰC TẾ = %đạt ÷ %cam kết; cột NGHIỆM THU = min(THỰC TẾ, 100%).
5. Khuyến nghị khách check lại trong 2-3 ngày kể từ ngày nhận báo cáo (câu Lưu ý cố định).

⚠️ Chưa có file export SpySERP mẫu trong wiki — lần đầu chạy với client mới, xin 1 file CSV thật để đối chiếu cột trước khi parse hàng loạt.

### 2b. GA4 export → Organic Traffic

Khớp layout sheet đích `BÁO CÁO TRAFFIC`: block theo tháng, cột `Ngày | Organic Traffic` + hàng `TỔNG ORGANIC TRAFFIC THÁNG`.

Quy trình đọc:
1. Hỏi/xác nhận **đơn vị theo HĐ client**: Sessions (kpi-commitment-template) / Product Pageview (docx mẫu) / Organic Traffic (workbook) — 🔴 không tự chọn.
2. Lọc đúng kênh **Organic** + đúng khoảng ngày (từ ngày 01 đến ngày cuối tháng — ghi nguyên văn vào cột HẠNG MỤC: "tải về từ GA, từ ngày … đến ngày …").
3. Tổng theo khoảng ngày = KẾT QUẢ. CRO trực tiếp (lead, doanh thu) KHÔNG lấy từ GA export — trao đổi với khách lấy số liệu thực tế (GUIDELINE docx).
4. Đính kèm file PDF tải về từ GA cho section CRO.

### 2c. GEO evidence (khi HĐ có GEO KPI)

- Citation AIO: export SemRush (filter SERP Feature > Google AI Overview) hoặc Ahrefs `site-explorer-ai-responses-count` + fact-check thủ công.
- Brand Mention LLM: chạy bộ prompt Query Fan-out trên các công cụ, chế độ ẩn danh, screenshot từng công cụ + ngày check + model version. **Ngưỡng ĐẠT (v1.3, Lead chốt 29/08/2026): có mention trên CẢ ChatGPT lẫn Google AI (AI Mode hoặc Gemini)** — 2 kênh bắt buộc; Perplexity/Copilot/Claude là bonus, ghi thêm nếu có. HĐ ký trước 29/08/2026 còn ghi "≥2/4" → giữ đúng chữ HĐ cho tới khi gia hạn, nhưng report vẫn hiện tách 2 kênh bắt buộc.
- **Conversion từ AI Assistant (v1.3):** GA4 → Reports → Acquisition → Traffic acquisition, dimension Session channel group, hàng **"AI Assistant"** (custom channel group regex `chatgpt\.com|gemini\.google\.com|perplexity\.ai|copilot\.microsoft\.com|claude\.ai…` — setup theo `geo-tracking-prompt-selection/references/kpis-metrics.md` § GA4) → lấy Sessions · Key events · Session key event rate; so với hàng Organic Search cùng kỳ → bội số `AI CVR / Organic CVR`. Kỳ ≥28 ngày; <100 session → ghi "chưa đủ mẫu".
- Information Accuracy: bảng chấm % đúng/sai thông tin brand trên cùng 4 công cụ.
- ⚠️ (v1.2) Brand Radar phân biệt **cited** (hiện link nguồn) vs **found** (được retrieve nhưng không hiện link) — export cả hai, report tách 2 metric, không gộp; mọi số citation/impression AI kèm nhãn "(directional)" + ghi ngày query. Chi tiết + kỳ vọng cam kết: SKILL.md mục "Luật GEO/AI metrics trong report".

## 3. Path C — Account điền tay (đường lùi cuối, không cần MCP/export)

Render skeleton đầy đủ theo [kpi-table-formats.md](kpi-table-formats.md) với placeholder từng ô:

```
[CẦN SỐ LIỆU: <mô tả số cần lấy> — nguồn: <SpySERP ngày …/GA4 từ …–…/trao đổi khách> — PIC: <account>]
```

Quy tắc: cấu trúc bảng + điều khoản nghiệm thu render sẵn 100%; account chỉ điền số. Không được để model "ước lượng tạm" thay placeholder.

## 4. Map folder báo cáo khách (điền cột "Link báo cáo")

Theo `GUIDELINE THIẾT LẬP FILE BÁO CÁO KHÁCH HÀNG.docx`:

- Tên folder chuẩn: **`[Tên Dự Án] - SEO Reports`** — share cho khách quyền **Comment** (không Edit); giải thích cấu trúc trong lần gửi đầu.
- 5 mục con đánh số:

| # | Folder | Workbook chính | Ô bảng KPI trỏ về |
|---|---|---|---|
| 1 | Báo cáo kết quả | `1. BÁO CÁO KẾT QUẢ.xlsx` (9 sheet: THÔNG TIN DỰ ÁN · KPI · OKRs · BÁO CÁO THỨ HẠNG (TOP) · BÁO CÁO TRAFFIC · BÁO CÁO CÔNG VIỆC · BÁO CÁO KPI · Looker- chi tiết từ khoá · Looker- thứ hạng) | hàng TOP, hàng chốt KPI, mode QUÝ |
| 2 | Báo cáo chuyển đổi (CRO) | `2. BÁO CÁO CHUYỂN ĐỔI (CRO).xlsx` (Time on Site & Bounce Rate · Product Page view · Tracking lead · Phương án CRO) | hàng ORGANIC TRAFFIC/Page View, section CRO |
| 3 | Technical & UX-UI | `3. TECHNICAL.xlsx` | hàng công việc technical |
| 4 | Content & Onpage | `4. CONTENT & ONPAGE.xlsx` | hàng Audit/Triển khai Content, Onpage URLs |
| 5 | Entity & Offsite | `5. ENTITY & OFFSITE.xlsx` | hàng Backlink/Entity |

Ghi chú vận hành liên quan (từ workbook sheet THÔNG TIN DỰ ÁN): khách điền thông tin đầu dự án trong **3 ngày đầu**; hạng mục phối hợp 2 team theo dõi hàng ngày — dùng khi viết mục "vấn đề phát sinh".
