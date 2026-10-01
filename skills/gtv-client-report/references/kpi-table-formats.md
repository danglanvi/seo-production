# KPI Table Formats — Skeleton 3 chế độ báo cáo

> Nguồn nền (tên file/folder giữ nguyên văn filesystem, kể cả space thừa): tài liệu nội bộ «3. MẪU BÁO CÁO CÔNG VIỆC HÀNG THÁNG» (ngoài repo, hỏi Lead/Vincent), tài liệu nội bộ «3.1 MẪU BÁO CÁO KPI DỰ ÁN - THÁNG CUỐI - NGHIỆM THU » (ngoài repo, hỏi Lead/Vincent), workbook tài liệu nội bộ «1. BÁO CÁO KẾT QUẢ» (ngoài repo, hỏi Lead/Vincent), tài liệu nội bộ «kpi-commitment-template» (ngoài repo, hỏi Lead/Vincent), tài liệu nội bộ «contract-playbook» (ngoài repo, hỏi Lead/Vincent). Template gốc read-only — file này chỉ trích cấu trúc + điều khoản công khai với khách.

## TOC

1. [Khối mở đầu chung](#1-khối-mở-đầu-chung)
2. [Bảng KPI 7 cột — quy tắc render](#2-bảng-kpi-7-cột--quy-tắc-render)
3. [Menu KPI chuẩn (map từ kpi-commitment-template)](#3-menu-kpi-chuẩn)
4. [Chế độ THÁNG — skeleton đầy đủ](#4-chế-độ-tháng--skeleton-đầy-đủ)
5. [Chế độ THÁNG CUỐI / NGHIỆM THU — skeleton](#5-chế-độ-tháng-cuối--nghiệm-thu--skeleton)
6. [Chế độ QUÝ — skeleton OKRs review](#6-chế-độ-quý--skeleton-okrs-review)
7. [Ví dụ đã điền (ẩn danh hóa)](#7-ví-dụ-đã-điền-ẩn-danh-hóa)
8. [Render hàng GEO (chưa có mẫu chính thức)](#8-render-hàng-geo)

---

## 1. Khối mở đầu chung

**Tiêu đề mail (nguyên văn format):**

```
[GTV SEO] – BÁO CÁO TIẾN ĐỘ VÀ KPI DỰ ÁN (<Tên dự án>) THÁNG THỨ <n>
```

**Khối Kính gửi + câu dẫn:**

```
Kính gửi:
- Anh/chị <tên người nhận>
- Công ty <tên đầy đủ công ty khách hàng>

GTV SEO kính gửi đến anh/chị báo cáo tiến độ và KPI đạt được của dự án SEO
tháng <n>, cụ thể như sau:
```

## 2. Bảng KPI 7 cột — quy tắc render

**Header cố định (không đổi tên cột, không thêm bớt):**

```
LOẠI KPI | HẠNG MỤC | CAM KẾT | KẾT QUẢ | TỶ LỆ HOÀN THÀNH THỰC TẾ | TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU | Link báo cáo
```

(Workbook sheet BÁO CÁO KPI có thêm cột `GHI CHÚ` — bản email dùng 7 cột; bản .docx/sheet nội bộ được phép thêm GHI CHÚ.)

**Quy tắc nhóm hàng theo LOẠI KPI** (merge ô LOẠI KPI khi nhóm có nhiều hàng):

| Thứ tự | LOẠI KPI | Hàng bên trong |
|---|---|---|
| 1 | ORGANIC TRAFFIC | 1 hàng/chỉ số traffic cam kết (đơn vị theo HĐ: Sessions / Product Pageview / Organic Traffic) |
| 2 | TOP | mỗi bộ keyword 1 hàng (Bộ 1, Bộ 2… — bộ thúc đẩy và bộ duy trì tách hàng riêng) |
| 3 | NGUYÊN LIỆU DỰ ÁN *(docx)* / CÔNG VIỆC *(workbook)* | 1 hàng/hạng mục đầu việc (Audit Content, Triển khai Content, Onpage URLs, Backlink…) |
| 4 | GEO *(nếu HĐ có)* | xem mục 8 |
| cuối | **KẾT QUẢ KPI** | hàng chốt: chỉ 2 ô có nội dung (nhãn + %), các ô còn lại merge/trống như mẫu gốc — lưu ý khi render .docx |

**Quy tắc điền từng cột:**

- **HẠNG MỤC** — 🔴 ghi rõ nguồn + khoảng ngày đo. Mẫu chuẩn:
  - Traffic: `Tổng <đơn vị> tải về từ GA, từ ngày <dd/mm> đến ngày <dd/mm>`
  - TOP: `Bộ <i> — TOP <03|05|10>` (kèm ngày tracking SpySERP trong ngoặc hoặc GHI CHÚ)
- **CAM KẾT / KẾT QUẢ** — TOP dùng % số keyword trong bộ đạt ngưỡng (vd cam kết 40% → kết quả 78%); traffic/công việc dùng số tuyệt đối.
- **TỶ LỆ HOÀN THÀNH THỰC TẾ** = KẾT QUẢ ÷ CAM KẾT (mẫu: 10.614/5.433 ≈ 195%). ⚠️ Docx mẫu hiển thị 194% cho hàng 78%/40% dù 78/40 = 195% — chênh do docx làm tròn từ số keyword thô; khi render, tính từ số thô (số keyword đạt ÷ tổng số keyword trong bộ) rồi mới làm tròn %, KHÔNG tính lại từ % đã làm tròn. Công thức suy từ hàng mẫu, chưa văn bản hóa — xác nhận với account lần đầu áp dụng.
- **TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU** — 🔴 cap 100%. Thực tế 195% vẫn ghi 100%.
- **Hạng mục chưa cam kết** — ghi `Chưa cam kết` ở CAM KẾT, 🔴 KHÔNG tính 0%, loại khỏi mẫu số hàng chốt.
- **Hàng chốt KẾT QUẢ KPI** = trung bình cộng cột "TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU" của **các hạng mục có cam kết trong tháng** (nguyên văn workbook: "Tính trung bình các hạng mục có cam kết trong tháng").
- **Link báo cáo** — trỏ đúng file trong folder `[Tên Dự Án] - SEO Reports` (xem data-paths.md mục 4): Page View → `2. Báo cáo chuyển đổi (CRO)`, TOP → `1. Báo cáo kết quả` (sheet BÁO CÁO THỨ HẠNG), Content Audit → `4. Content & Onpage`…
- **TOP lồng nhau** — TOP3 ⊂ TOP5 ⊂ TOP10: keyword đạt TOP3 đồng thời tính đạt TOP5 và TOP10 (contract-playbook Điều 2). "Top từ khóa" chỉ tính **liên kết tự nhiên** — không tính ảnh/video/Maps/Ads/AI Overview.

**Câu chốt sau bảng:**

```
Như vậy, GTV SEO đã hoàn thành <x>% KPI theo cam kết tháng thứ <n> của hợp đồng SEO.
```

**2 câu Lưu ý cố định (giữ nguyên văn ý, đặt ngay sau câu chốt):**

```
Lưu ý:
- Báo cáo thứ hạng từ khoá được lấy từ SpySERP - check ở Google.com.vn, khu vực Việt Nam.
- Anh/chị vui lòng kiểm tra thứ hạng từ khóa trong vòng 2-3 ngày kể từ ngày nhận được báo cáo.
```

## 3. Menu KPI chuẩn

Map từ `kpi-commitment-template.md` — chọn hàng đúng theo HĐ từng client, không render hạng mục HĐ không có:

| Nhóm | Hạng mục | Đơn vị | Công cụ đo (chuẩn HĐ) |
|---|---|---|---|
| TOP TỪ KHOÁ | Core Section — thúc đẩy TOP03/05/10 | % và số key | SpySERP (Google.com.vn, VN) |
| TOP TỪ KHOÁ | Bộ duy trì — duy trì TOP03/05/10 | % và số key | SpySERP |
| TOP TỪ KHOÁ | Bộ GEO — keywords hiển thị trong AIO | số key | SemRush/Ahrefs |
| ORGANIC TRAFFIC | Duy trì / Thúc đẩy | Sessions (biến thể HĐ: Product Pageview) | GA4 |
| TRAFFIC TỪ GEO | Tổng Traffic từ AI Search Engine | Sessions | GA4 (Referral + traffic chứng minh từ ChatGPT, Google AI Mode, Perplexity, Copilot) |
| GEO | Website trong AI Overview | số keyword | SemRush filter SERP Feature > Google AI Overview + fact-check thủ công |
| GEO | Brand mention trong AIO Commercial Investigation | Mentions | check ẩn danh |
| GEO | Brand Mention trong LLM | ≥2/4 công cụ = tối ưu | bộ prompt Query Fan-out trên ChatGPT/Gemini/Perplexity/Google AI Mode |
| GEO | Information Accuracy About Brand | % | cùng 4 công cụ |
| CÔNG VIỆC | Audit Content / Triển khai Content / Onpage URLs / Backlink… | số đầu việc | Google Sheets tiến độ |

⚠️ Bộ 4 công cụ LLM ở trên lấy theo dòng "bộ Prompt Tracking" trong `kpi-commitment-template.md` (Google AI Mode/Gemini/Perplexity/ChatGPT); wiki còn 1 dòng định nghĩa khác nhắc **Claude** thay vì Google AI Mode — nguồn tự mâu thuẫn, đề xuất lint wiki thống nhất. HĐ từng client quyết định bộ công cụ cuối cùng.

⚠️ HĐ tách 2 nhóm nghiệm thu: **Hạng mục công việc** (theo số đầu việc — nhóm NGUYÊN LIỆU DỰ ÁN/CÔNG VIỆC) vs **Cam kết KPI** (TOP/ORGANIC TRAFFIC/GEO) — giữ đúng 2 nhóm này trong bảng.

## 4. Chế độ THÁNG — skeleton đầy đủ

```markdown
# [GTV SEO] – BÁO CÁO TIẾN ĐỘ VÀ KPI DỰ ÁN (<Tên dự án>) THÁNG THỨ <n>

Kính gửi:
- Anh/chị <tên người nhận>
- Công ty <tên đầy đủ>

GTV SEO kính gửi đến anh/chị báo cáo tiến độ và KPI đạt được của dự án SEO tháng <n>, cụ thể như sau:

## 1. KẾT QUẢ KPI ĐẠT ĐƯỢC

| LOẠI KPI | HẠNG MỤC | CAM KẾT | KẾT QUẢ | TỶ LỆ HOÀN THÀNH THỰC TẾ | TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU | Link báo cáo |
|---|---|---|---|---|---|---|
| ORGANIC TRAFFIC | Tổng <đơn vị theo HĐ> tải về từ GA, từ ngày <dd/mm> đến ngày <dd/mm> | <số> | <số> | <x>% | <≤100>% | <link Page View> |
| TOP | Bộ 1 — TOP <03> (SpySERP, tracking ngày <dd/mm>) | <x>% | <y>% | <y/x>% | <≤100>% | <link TOP> |
| TOP | Bộ 2 — TOP <05> (SpySERP, tracking ngày <dd/mm>) | <x>% | <y>% | <y/x>% | <≤100>% | <link TOP> |
| NGUYÊN LIỆU DỰ ÁN | <hạng mục, vd Audit Content sẵn có> | <số> | <số> | <x>% | <≤100>% | <link> |
| NGUYÊN LIỆU DỰ ÁN | <hạng mục chưa cam kết, vd Backlink> | Chưa cam kết | — | — | — | — |
| **KẾT QUẢ KPI** | | | | | **<x>%** | |

Như vậy, GTV SEO đã hoàn thành <x>% KPI theo cam kết tháng thứ <n> của hợp đồng SEO.

Lưu ý:
- Báo cáo thứ hạng từ khoá được lấy từ SpySERP - check ở Google.com.vn, khu vực Việt Nam.
- Anh/chị vui lòng kiểm tra thứ hạng từ khóa trong vòng 2-3 ngày kể từ ngày nhận được báo cáo.

## 2. BÁO CÁO TIẾN ĐỘ DỰ ÁN THÁNG

| STT | Tên công việc | Thời hạn | Trạng thái | Kết quả công việc |
|---|---|---|---|---|
| 1 | <tên công việc> | <dd/mm> | <Đã làm / Đang làm / Cần xử lý> | <kết quả + link> |

## 3. Các dữ liệu báo cáo khác (CRO) — v2026.09.4: 3 khối từ WS 13 (skill `cro-audit` → `references/report-hook.md`)

**3a. Chuyển đổi kỳ này** (đúng nhãn: "click" ≠ "lead"; "đơn tạo" ≠ "doanh thu" khi có COD; hàng AI Assistant directional, không nghiệm thu)

| Kênh | Micro (GA4, đã QA) | Outcome đối soát (nguồn, độ trễ) | Kỳ trước |
|---|---|---|---|
| Gọi / Zalo / Messenger | click_to_call <…> · click_zalo <…> | Lead đạt chuẩn từ Sheet sale: <…> | <…> |
| Form / báo giá | generate_lead <…> | Lead đạt chuẩn / báo giá đã gửi: <…> | <…> |
| Đơn hàng | user có ≥1 purchase / user vào PDP+giỏ (đơn tạo) | Đơn hợp lệ sau 14 ngày: <…> | <…> |
| Apply / ATS (khi cơ chế job) | application_complete / apply_start (candidate–job) | Hồ sơ đạt chuẩn từ HR: <…> | <…> |
| Từ AI Assistant | session <…> · CVR một outcome đã chốt, cùng population với Organic | (directional — phần AI referral nhận diện được, có điểm mù; là phân đoạn, **không cộng vào tổng**) | <…> |

Metric ghi dạng tử số/mẫu số/đơn vị; gọi/chat không join được với user → hai số riêng. Tracking chưa PASS QA → ghi: "Kế hoạch đo đã bàn giao ngày <…>, chờ dev triển khai; số kỳ này chưa dùng để kết luận." Không thay bằng Time on site / Bounce.

**3b. Phát hiện kỳ này** (từ `13-cro/<CLIENT>_evidence-backlog`, chỉ E≥2, **finding mới trong kỳ**, tối đa 5 dòng, P0 trước, ảnh che PII, nối bằng finding ID)

| ID | Trang/template | Phát hiện | Mức | Đề xuất | Trạng thái |
|---|---|---|---|---|---|
| F-xx | <…> | <quan sát + bằng chứng> | P0/P1 | <component> | Đã brief <dd/mm> / khách duyệt / dev đã deploy / GTV QA PASS / chờ khách |

**3c. Việc đã sửa và số quan sát** (chỉ mốc **GTV QA PASS**; cùng mẫu số, cùng độ dài cửa sổ ≥4 tuần; nhãn "quan sát trước/sau"; nêu yếu tố khác đã đổi — không "uplift", không "tăng X% nhờ GTV"; chưa đủ cửa sổ ghi "đang theo dõi tới <ngày>")

| ID | Việc | Ngày QA PASS | Metric (tử/mẫu) | Trước (cửa sổ) | Sau (cửa sổ) | Ghi chú |
|---|---|---|---|---|---|---|

**3d. Chờ phía khách** (**mọi P0 còn mở** kèm tuổi lỗi + brief chưa triển khai — bằng chứng GTV đã làm phần mình; không gộp với 3b)

| ID | Brief | Ngày gửi | Tuổi lỗi (ngày) | Mức | Ảnh hưởng nếu chưa làm | Cần gì từ khách |
|---|---|---|---|---|---|---|

Không có phát hiện mới → vẫn ghi "không phát hiện mới; đang theo dõi <…> tới <ngày>". Đính kèm: ảnh DebugView/heatmap đã che PII (không đính PDF GA trần).

## 4. Vấn đề phát sinh / tồn đọng

1. Tiến độ điều chỉnh website: <hạng mục chậm — do bên nào — ảnh hưởng KPI ra sao — action phối hợp>.
2. Thay đổi từ phía khách hàng ảnh hưởng KPI: <mô tả — action 2 bên>.
3. Khâu content: <hạng mục chậm/delay duyệt — action tiếp theo>.

## 5. KẾ HOẠCH THÁNG TIẾP THEO

- File Báo cáo công việc tháng: <link>
- Folder báo cáo: <link folder [Tên Dự Án] - SEO Reports>
- Kính đề nghị anh/chị xem Plan tháng <n+1> và phản hồi để 2 bên thống nhất triển khai.

---

**ĐIỀU KHOẢN NGHIỆM THU (🔴 nguyên văn docx `3. MẪU BÁO CÁO CÔNG VIỆC HÀNG THÁNG.docx`, không paraphrase — quy đổi: Bên A = khách hàng, Bên B = GTV; chỉ thay placeholder `<n>`):**

Trên đây là một số thông tin về Tiến độ công việc và kết quả KPI của dự án SEO
tháng <n> do GTV thực hiện. Trong trường hợp anh/chị đồng ý với kết quả ở mục
1 & 2 ở trên, vui lòng phản hồi email xác nhận "Đồng ý nghiệm thu kết quả KPI
theo báo cáo", trong vòng 04 ngày kể từ ngày nhận được báo cáo này để GTV hoàn
thành các giấy tờ nghiệm thu liên quan và các hạng mục triển khai cho tháng/đợt
tiếp theo.

Nếu sau 07 (bảy) ngày làm việc kể từ ngày Bên B gửi báo cáo kết quả KPI, Bên A
vẫn chưa có phản hồi chính thức qua email để thống nhất nghiệm thu, Bên B sẽ tạm
dừng triển khai các hạng mục công việc tiếp theo của dự án.

Việc tạm dừng này sẽ kéo dài cho đến khi hai bên đạt được sự đồng thuận về kết
quả KPI qua email và hoàn tất các thủ tục nghiệm thu liên quan.

Thời gian tạm ngưng sẽ được cộng dồn vào mốc thời gian báo cáo hàng tháng của
dự án, nhưng không vượt quá 14 ngày.

Trong trường hợp việc tạm ngưng do chưa thống nhất được kết quả nghiệm thu KPI
kéo dài trên 15 ngày, Bên B sẽ thông báo cho Bên A về những điều chỉnh có thể
xảy ra đối với KPI tổng cam kết, ngân sách triển khai phát sinh (nếu có) của dự
án do các yếu tố nhu cầu thị trường hoặc thay đổi thuật toán của Google trong
thời gian tạm ngưng.

Trân trọng cảm ơn!
<Tên Account> — GTV SEO
```

## 5. Chế độ THÁNG CUỐI / NGHIỆM THU — skeleton

Cấu trúc = chế độ THÁNG (giữ nguyên section 1-4 + Lưu ý), khác các điểm sau:

```markdown
<!-- Câu chốt thay bằng: -->
Như vậy, ở tháng cuối của dự án, GTV SEO đã hoàn thành <x>% KPI theo cam kết tại
Hợp đồng SEO số <số HĐ>. GTV SEO chân thành cảm ơn anh/chị và Quý công ty đã tin
tưởng đồng hành cùng GTV trong suốt thời gian triển khai dự án.

<!-- KHÔNG có section "KẾ HOẠCH THÁNG TIẾP THEO". Thay bằng: -->

## 5. ĐỀ XUẤT HỌP NGHIỆM THU

GTV đề xuất 2 Bên có 1 buổi họp trao đổi về KPI nghiệm thu của tổng Hợp đồng này
vào <giờ>, ngày <dd>, tháng <mm>, năm <yyyy>.

---

**ĐIỀU KHOẢN NGHIỆM THU THÁNG CUỐI (🔴 nguyên văn docx `3.1 MẪU BÁO CÁO KPI DỰ ÁN - THÁNG CUỐI - NGHIỆM THU .docx`, không paraphrase — chỉ thay placeholder `<số HĐ>`):**

Trong trường hợp Anh Chị đồng ý với kết quả trên, vui lòng phản hồi email xác
nhận "Đồng ý nghiệm thu kết quả KPI theo báo cáo", trong vòng 04 ngày kể từ
ngày nhận được báo cáo này để GTV hoàn thành các thủ tục nghiệm thu và thanh
toán còn lại (nếu có). Sau đó GTV chuyển dự án qua giai đoạn Bảo hành kết quả
trong 30 ngày tiếp theo.

Sau 07 (bảy) ngày làm việc, nếu bên GTV không nhận được phản hồi, báo cáo nghiệm
thu sẽ được xem là đã được chấp thuận. Phía GTV sẽ tiến hành các thủ tục thanh
lý hợp đồng được quy định trong Hợp đồng số <số HĐ>.

Trân trọng cảm ơn!
```

Ghi chú cho account (không đưa vào email): giai đoạn Bảo hành = duy trì kết quả **≥90% trong 30 ngày** (dự trù 10% rủi ro Google update — contract-playbook). Cách tính gate giải ngân theo đợt → xem [[contract-playbook]] (🔒) — chỉ dùng khi account cần giải thích trực tiếp cách tính nghiệm thu, KHÔNG chèn vào email mẫu.

## 6. Chế độ QUÝ — skeleton OKRs review (v1.1 — mẫu chính thức tự đề xuất)

📌 **Trạng thái format:** v1.1 do Claude tự thiết kế 07/2026 theo ủy quyền Vincent (sheet OKRs workbook chỉ có header, chưa từng có mẫu email thật). Đây là format CHÍNH THỨC để render — cuối report luôn kèm 1 dòng: *"Format báo cáo quý v1.1 — anh/chị account góp ý sau lần dùng đầu để hiệu chỉnh."* 🔴 Chỉ REVIEW OKRs đã hoạch định (cập nhật Status + nhận xét) — lập OKRs quý mới là việc của `okrs-gtv-tag-framework`. Báo cáo quý mang tính tổng kết-định hướng, KHÔNG kèm điều khoản nghiệm thu 4/7 ngày (nghiệm thu chạy theo đợt/tháng).

```markdown
# [GTV SEO] – BÁO CÁO QUÝ <I/II/III/IV> DỰ ÁN (<Tên dự án>) – REVIEW OKRs & KPI

Kính gửi: <như khối mở đầu chung>

GTV SEO kính gửi anh/chị báo cáo tổng kết quý <n> của dự án SEO, gồm review OKRs đã hoạch định, diễn biến thứ hạng, KPI lũy kế và trọng tâm quý tới:

## 1. REVIEW OKRs QUÝ <n> (theo sheet OKRs — HOẠCH ĐỊNH OKR HÀNG QUÝ)

| MỤC TIÊU | HẠNG MỤC (Key Result) | Bắt đầu | Kết thúc | PIC | Status | % hoàn thành | Nhận xét |
|---|---|---|---|---|---|---|---|
| <objective đã hoạch định> | <key result> | <dd/mm> | <dd/mm> | <PIC> | <Đã làm / Đang làm / Cần xử lý> | <n>% | <đạt/lệch — evidence + ngày đo> |
| **TỔNG OKRs QUÝ** | | | | | | **<trung bình %>** | |

## 2. DIỄN BIẾN THỨ HẠNG THEO QUÝ (SpySERP, Google.com.vn, khu vực Việt Nam)

| Tháng | TOP 3 | TOP 5 | TOP 10 | Ngày tracking |
|---|---|---|---|---|
| Tháng <n> | <số key> | <số key> | <số key> | <dd/mm> |
| Tháng <n+1> | … | … | … | … |
| Tháng <n+2> | … | … | … | … |
| **Δ so cuối quý trước** | <+/− key> | <+/− key> | <+/− key> | |

## 3. KPI LŨY KẾ 3 THÁNG TRONG QUÝ

| Tháng | KẾT QUẢ KPI tháng (từ báo cáo đã nghiệm thu) | Ghi chú |
|---|---|---|
| Tháng <n> | <x>% | <đã nghiệm thu ngày dd/mm> |
| Tháng <n+1> | <y>% | … |
| Tháng <n+2> | <z>% | … |
| **Trung bình quý** | **<tb>%** | |

## 4. GEO / AI VISIBILITY QUÝ *(chỉ khi HĐ có GEO KPI)*

| Chỉ số | Đầu quý | Cuối quý | Δ | Nguồn + ngày đo |
|---|---|---|---|---|
| Keywords hiển thị trong AI Overview | … | … | … | SemRush/Ahrefs + fact-check, <dd/mm> |
| Brand Mention LLMs (số công cụ /4) | <k>/4 | <k>/4 | … | Query Fan-out check ẩn danh, <dd/mm> |
| Traffic từ GEO (Sessions) | … | … | … | GA4, <dd/mm–dd/mm> |

(Đo aggregate theo quý — không kết luận từ 1 lần check đơn lẻ; AIO đổi bề mặt ~2 ngày/lần.)

## 5. VẤN ĐỀ TỒN ĐỌNG & TRỌNG TÂM QUÝ TỚI
- Vấn đề: <sự kiện + phía chịu trách nhiệm + action>
- Trọng tâm quý tới: <theo OKRs đã hoạch định cho quý sau — KHÔNG lập OKRs mới ở đây; nếu cần hoạch định lại → buổi làm việc OKRs riêng>

*Format báo cáo quý v1.1 — anh/chị account góp ý sau lần dùng đầu để hiệu chỉnh.*
```

## 7. Ví dụ đã điền (ẩn danh hóa)

Ẩn danh từ mẫu thật trong docx 3.1 (tên khách + số HĐ thật đã thay bằng placeholder — 🔴 không dùng tên thật trong skill/report mẫu):

> Như vậy, ở tháng cuối của dự án, GTV SEO đã hoàn thành 100% KPI theo cam kết tại Hợp đồng SEO số **[SỐ HĐ]/GTV/SEO - [MM/YYYY]** với Công ty **[TÊN KHÁCH HÀNG]**.
>
> GTV đề xuất 2 Bên có 1 buổi họp trao đổi về KPI nghiệm thu của tổng Hợp đồng này vào **[15h00], ngày [29], tháng [04], năm [2025]**.

Hàng KPI mẫu (từ docx 3., số giữ nguyên làm few-shot cách điền):

| LOẠI KPI | HẠNG MỤC | CAM KẾT | KẾT QUẢ | THỰC TẾ | NGHIỆM THU | Link |
|---|---|---|---|---|---|---|
| ORGANIC TRAFFIC | Tổng Product Pageview tải về từ GA, từ ngày 01/07 đến ngày 30/07 | 5,433 | 10,614 | 195% | 100% | Page View |
| TOP | Bộ 1 — TOP 03 | 40% | 78% | 194% | 100% | TOP |
| TOP | Bộ 2 — TOP 05 | 56% | 94% | 168% | 100% | TOP |
| NGUYÊN LIỆU DỰ ÁN | Audit Content sẵn có | 5 | 5 | 100% | 100% | Content Audit |
| **KẾT QUẢ KPI** | | | | | **100%** | |

## 8. Render hàng GEO (v1.1 — quy ước chính thức tự đề xuất)

📌 **Trạng thái format:** template gốc (T11-2024) tiền-GEO, không có hàng mẫu. Quy ước dưới đây là v1.1 do Claude tự thiết kế 07/2026 theo ủy quyền Vincent — dùng làm chuẩn render; đối chiếu với báo cáo thật đầu tiên có GEO KPI rồi hiệu chỉnh file này (ghi vào Changelog skill).

Đủ 5 hàng khớp menu KPI chuẩn (mục 3) — chỉ render hàng nào HĐ có cam kết, đủ 7 cột như bảng tháng:

| LOẠI KPI | HẠNG MỤC (mẫu) | CAM KẾT | KẾT QUẢ | TỶ LỆ THỰC TẾ | NGHIỆM THU (cap 100%) | Link báo cáo (evidence) |
|---|---|---|---|---|---|---|
| GEO | Keywords hiển thị trong AI Overview (SemRush filter SERP Feature > Google AI Overview + fact-check thủ công, ngày <dd/mm>) | <số key> | <số key> | <n>% | ≤100% | export SemRush/Ahrefs + screenshot |
| GEO | Brand mention trong AI Overview — nhóm keyword Commercial Investigation (check ẩn danh, ngày <dd/mm>) | <số mentions> | <số mentions> | <n>% | ≤100% | screenshot check ẩn danh |
| GEO | Brand Mention trong LLM — bộ prompt Query Fan-out, 4 công cụ ChatGPT/Gemini/Perplexity/Google AI Mode (check ngày <dd/mm>) | ≥2/4 công cụ | <k>/4 công cụ | — | ĐẠT khi ≥2/4 | screenshot từng công cụ |
| GEO | Information Accuracy About Brand (4 công cụ trên, ngày <dd/mm>) | <x>% | <y>% | <n>% | ≤100% | bảng chấm accuracy + screenshot |
| TRAFFIC TỪ GEO | Tổng Sessions từ AI Search (GA4: Referral + traffic chứng minh từ ChatGPT/Google AI Mode/Perplexity/Copilot, từ <dd/mm> đến <dd/mm>) | <sessions> | <sessions> | <n>% | ≤100% | GA4 export |

Quy tắc: cột nghiệm thu cap 100%; hàng Brand Mention LLM là chỉ tiêu ngưỡng (ĐẠT/CHƯA ĐẠT theo ≥2/4) — không tính %, khi gộp vào trung bình KẾT QUẢ KPI thì ĐẠT = 100%, CHƯA ĐẠT = (k/2)×100% (quy ước v1.1, nêu rõ với account lần đầu dùng); mọi evidence GEO kèm ngày check + screenshot ẩn danh (không đăng nhập account cá nhân); bộ 4 công cụ cuối cùng theo HĐ từng client (xem ⚠️ mục 3).
