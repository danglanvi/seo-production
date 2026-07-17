---
name: gtv-client-report
description: "Sinh báo cáo client GTV theo mẫu Account chuẩn — layer REPORTING: chỉ render kết quả trên KPI đã cam kết trong hợp đồng/workbook, 3 chế độ THÁNG, QUÝ (OKRs review theo sheet OKRs workbook), THÁNG CUỐI/NGHIỆM THU (họp nghiệm thu + auto-accept 7 ngày + bảo hành 30 ngày). Use when: (1) 'viết báo cáo tháng cho [client]', 'làm report KPI tháng thứ [n]'; (2) 'báo cáo quý / review OKRs quý [n] cho [client]'; (3) 'báo cáo nghiệm thu / báo cáo tháng cuối [client]'. Data ladder: Ahrefs MCP → SpySERP+GA4 → điền tay. Output kép: markdown draft email + .docx theo MẪU. 🔒 GTV-only, chạy trong Claude Code workspace, không đóng gói claude.ai. KHÔNG dùng cho: lập proposal/cam kết KPI mới (→ gtv-proposal), hoạch định OKRs mới (→ okrs-gtv-tag-framework), phân tích SEO sâu nguyên nhân tụt hạng (→ skill seo-*)."
metadata:
  version: "1.1"
---

# GTV Client Report

Sinh báo cáo gửi khách hàng GTV (email + .docx) đúng MẪU BÁO CÁO của phòng Account: bảng KPI 7 cột, bảng tiến độ, dữ liệu CRO, điều khoản nghiệm thu nguyên văn. Skill này đứng **hạ nguồn** của `gtv-proposal` (KPI đã cam kết là input, không phải output) và **thượng nguồn** của việc gửi mail/nghiệm thu của Account.

🔒 **GTV-only, workspace-only**: skill đọc wiki `GTV Ops/` và có thể chạm dữ liệu client thật — chỉ chạy trong Claude Code workspace, KHÔNG đóng gói lên claude.ai. Không mix entity TAG dưới mọi hình thức.

## Phân vai (tránh lấn sân)

| Việc | Skill |
|---|---|
| Render báo cáo tháng/quý/nghiệm thu từ KPI đã cam kết | **gtv-client-report** (skill này) |
| Lập proposal, thiết kế/đàm phán cam kết KPI mới | `gtv-proposal` |
| Hoạch định OKRs quý mới | `okrs-gtv-tag-framework` — chế độ QUÝ ở đây chỉ REVIEW OKRs đã có |
| Phân tích SEO sâu (nguyên nhân tụt hạng, audit, research) | các skill `seo-*` — report chỉ nêu sự kiện + action ở mục "vấn đề phát sinh" |
| Review deck/pitch có cam kết KPI | `gtv-pitch-review` |
| Render file .docx | skill `docx` (document-skills) — skill này gọi docx để xuất file, không tự viết engine |
| Điều khoản hợp đồng, tính hoàn trả, gia hạn | `contract-playbook` (wiki, 🔒 confidential — không phải skill; chỉ trích điều khoản nghiệm thu công khai) |

## Input

**Required:**
- `$CLIENT` — tên dự án/khách hàng GTV (phải là client GTV, không phải học viên TAG).
- `$MODE` — `thang` | `quy` | `nghiem-thu` (tháng cuối).
- `$PERIOD` — tháng thứ mấy của hợp đồng (hoặc quý mấy), kèm khoảng ngày đo (vd: 01/06–30/06).
- `$KPI_SOURCE` — nguồn KPI cam kết: workbook `1. BÁO CÁO KẾT QUẢ.xlsx` của dự án (sheet KPI/OKRs) hoặc trang client trong `GTV Ops/wiki/entities/clients/`.

**Optional:**
- `$RANK_EXPORT` — file/paste export SpySERP (bộ keyword cam kết + vị trí + ngày tracking).
- `$TRAFFIC_EXPORT` — file/paste export GA4 (Sessions hoặc Product Pageview, kênh Organic, theo khoảng ngày).
- `$CRO_DATA` — Time on site, Bounce Rate, chuyển đổi CTA (Call/Mess/Hotline/Form) — chỉ số trực tiếp lấy từ trao đổi với khách.
- `$PROGRESS` — danh sách công việc tháng (tên, thời hạn, trạng thái, kết quả).
- `$REPORT_FOLDER_URL` — link folder `[Tên Dự Án] - SEO Reports` để điền cột "Link báo cáo".

**Path detection (data ladder — chi tiết ở [references/data-paths.md](references/data-paths.md)):**
- **Path A (ưu tiên khi có MCP): Ahrefs MCP** — rank-tracker/gsc-*/site-explorer/brand-radar + render charts. ⚠️ Chỉ dùng cho **chart minh họa trend + GEO/AIO citation** (Ahrefs là công cụ đo Citation AI Overview theo Điều 1 HĐ — nguồn: [[contract-playbook]]). KHÔNG dùng làm số nghiệm thu thứ hạng/traffic.
- **Path B: export paste** — nguồn chuẩn hợp đồng: **thứ hạng = SpySERP (Google.com.vn, khu vực Việt Nam)**, **traffic = GA4**. Đây là số được điền vào bảng KPI nghiệm thu.
- **Path C (đường lùi cuối — luôn chạy được không cần MCP): account điền tay** — render skeleton đầy đủ với placeholder `[CẦN SỐ LIỆU: …]` từng ô.

## Workflow

### Bước 0 — Scope gate & confirm (🔴 bắt buộc, chờ xác nhận rồi mới chạy)
- [ ] Xác nhận `$CLIENT` là **client GTV** (đối chiếu `GTV Ops/wiki/entities/clients/` nếu nghi ngờ). Nghi ngờ mix TAG → dừng, hỏi.
- [ ] Xác nhận `$MODE` + `$PERIOD` + khoảng ngày đo. Mode `nghiem-thu` → hỏi thêm giờ/ngày đề xuất họp nghiệm thu + số HĐ.
- [ ] Hỏi **đơn vị Organic Traffic theo HĐ client này** (Sessions / Product Pageview / Organic Traffic — các nguồn mẫu không thống nhất, KHÔNG tự chọn mặc định).
- [ ] Detect data path A/B/C theo input có sẵn. Nếu Path A: **báo số MCP call dự kiến** (thường 3-6 call: rank-tracker-overview, gsc-performance-history, brand-radar nếu có GEO KPI, + render) và **chờ xác nhận** trước khi gọi.
- [ ] Show plan (mode, sections sẽ render, data path, nơi trả file) → chờ duyệt (EXECUTION RULE).

### Bước 1 — Đọc KPI cam kết
- Đọc `$KPI_SOURCE`: sheet KPI (grid theo tháng) + sheet OKRs (nếu mode `quy`) của workbook, hoặc trang client wiki.
- Map từng hạng mục cam kết vào **menu KPI chuẩn** (TOP theo bộ thúc đẩy/duy trì, Organic Traffic, GEO: Citation AIO / Brand Mention LLMs / Information Accuracy) — bảng map ở [references/kpi-table-formats.md](references/kpi-table-formats.md), nguồn menu: [[kpi-commitment-template]].
- Hạng mục HĐ không cam kết tháng này → ghi "Chưa cam kết", **loại khỏi mẫu số** khi tính KẾT QUẢ KPI.

### Bước 2 — Thu số liệu theo data path
- Path B (số nghiệm thu): đếm % keyword đạt TOP3/5/10 từ export SpySERP theo **nguyên tắc TOP lồng nhau TOP3 ⊂ TOP5 ⊂ TOP10** ([[contract-playbook]] Điều 2); tổng traffic GA4 theo đúng khoảng ngày. Ghi lại **ngày tracking / khoảng ngày** cho từng con số.
- Path A (minh họa + GEO): gọi tool theo map ở [references/data-paths.md](references/data-paths.md); tool có `render_with` metadata → 🔴 BẮT BUỘC gọi render tool tương ứng.
- Thiếu số nào → placeholder `[CẦN SỐ LIỆU: <mô tả + nguồn cần lấy>]`. 🔴 **Tuyệt đối không bịa số.**

### Bước 3 — Dựng bảng KPI 7 cột
Header cố định: `LOẠI KPI | HẠNG MỤC | CAM KẾT | KẾT QUẢ | TỶ LỆ HOÀN THÀNH THỰC TẾ | TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU | Link báo cáo`. Quy tắc render (chi tiết + ví dụ đã điền ở [references/kpi-table-formats.md](references/kpi-table-formats.md)):
- Nhóm hàng theo LOẠI KPI: ORGANIC TRAFFIC → TOP (mỗi bộ 1 hàng) → NGUYÊN LIỆU DỰ ÁN/CÔNG VIỆC → GEO (nếu HĐ có).
- Cột HẠNG MỤC ghi rõ **nguồn + khoảng ngày đo** (vd "Tổng Sessions tải về từ GA4, từ ngày 01/06 đến ngày 30/06").
- `TỶ LỆ HOÀN THÀNH THỰC TẾ` = KẾT QUẢ / CAM KẾT — tính từ số thô rồi mới làm tròn % (docx mẫu hiển thị 194% cho hàng 78%/40% do làm tròn từ số keyword thô — xem references/kpi-table-formats.md mục 2; công thức chưa văn bản hóa — nêu để account xác nhận lần đầu dùng).
- 🔴 `TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU` **cap 100%** — thực tế 195% vẫn ghi 100%, không ngoại lệ.
- 🔴 Hàng chốt `KẾT QUẢ KPI` = **trung bình cộng các hạng mục CÓ cam kết trong tháng** (nguồn: workbook sheet BÁO CÁO KPI). "Chưa cam kết" ≠ 0% — loại khỏi mẫu số.
- Câu chốt: "Như vậy, GTV SEO đã hoàn thành …% KPI theo cam kết tháng thứ … của hợp đồng SEO."

### Bước 4 — Render các section còn lại theo chế độ
- **`thang`**: bảng TIẾN ĐỘ (`STT | Tên công việc | Thời hạn | Trạng thái | Kết quả công việc`; trạng thái chuẩn: Đã làm / Đang làm / Cần xử lý) → dữ liệu CRO (gián tiếp + trực tiếp, kèm ghi chú đính PDF từ GA) → vấn đề phát sinh (3 ý bắt buộc: điều chỉnh web / thay đổi từ KH / khâu content) → kế hoạch tháng sau → 2 câu Lưu ý cố định (SpySERP Google.com.vn; khách check thứ hạng trong 2-3 ngày) → **điều khoản nghiệm thu THÁNG nguyên văn** (4 ngày xác nhận / 7 ngày làm việc tạm dừng / cộng dồn tối đa 14 ngày / >15 ngày điều chỉnh KPI).
- **`quy`**: render đủ 5 section theo mẫu v1.1 (references mục 6): OKRs review (+% hoàn thành, tổng quý) → diễn biến thứ hạng 3 tháng + Δ quý trước → KPI lũy kế 3 tháng + trung bình → GEO/AI visibility quý (nếu HĐ có) → vấn đề & trọng tâm quý tới. ⚠️ Chỉ cập nhật Status/% của OKRs đã hoạch định — KHÔNG lập OKRs mới. Không kèm điều khoản nghiệm thu 4/7 ngày (nghiệm thu theo đợt/tháng). Cuối report luôn kèm dòng "Format báo cáo quý v1.1 — góp ý sau lần dùng đầu".
- **`nghiem-thu`**: như `thang` nhưng: câu chốt tham chiếu số HĐ + lời cảm ơn; KHÔNG có "kế hoạch tháng tiếp theo"; thay bằng **đề xuất họp nghiệm thu** (giờ/ngày cụ thể); điều khoản: khách phản hồi trong 4 ngày → chuyển giai đoạn **Bảo hành kết quả 30 ngày**; sau **7 ngày làm việc** không phản hồi → báo cáo **mặc nhiên được chấp thuận** → thủ tục thanh lý HĐ.
- 🔴 Đoạn điều khoản nghiệm thu là ngôn ngữ pháp lý đã chuẩn hóa — **render nguyên văn theo skeleton trong references, không paraphrase.**

### Bước 5 — Xuất output kép
1. **Markdown draft email** — đúng skeleton, tiêu đề `[GTV SEO] – BÁO CÁO TIẾN ĐỘ VÀ KPI DỰ ÁN (<Tên dự án>) THÁNG THỨ <n>`, account dán thẳng vào Gmail.
2. **File .docx theo MẪU** — gọi skill `docx` render từ markdown, giữ đúng cấu trúc bảng (hàng chốt KẾT QUẢ KPI merge ô như mẫu gốc).
Ghi cả 2 file về `Deliverables/<project-GTV>/` (TASK ROUTING), tên `<client>_Report_v1.md` / `.docx` (tăng `_v2`, `_v3` nếu trùng).

### Bước 6 — Delivery checklist
- [ ] Đúng entity GTV, không lẫn case/số liệu TAG.
- [ ] Mọi con số có nguồn + ngày đo; ô thiếu để `[CẦN SỐ LIỆU]`, không bịa.
- [ ] Cột nghiệm thu không ô nào >100%; "Chưa cam kết" loại khỏi trung bình.
- [ ] Điều khoản nghiệm thu nguyên văn, đúng biến thể chế độ.
- [ ] Tiếng Việt có dấu đầy đủ; thuật ngữ SEO giữ tiếng Anh.
- [ ] File đặt đúng `Deliverables/<project-GTV>/`, không sửa gì trong `GTV Ops/wiki/account/`.

## Output

Skeleton đầy đủ 3 chế độ ở [references/kpi-table-formats.md](references/kpi-table-formats.md). Khung rút gọn chế độ THÁNG:

```markdown
# [GTV SEO] – BÁO CÁO TIẾN ĐỘ VÀ KPI DỰ ÁN (<Tên dự án>) THÁNG THỨ <n>

Kính gửi:
- Anh/chị <tên người nhận>
- Công ty <tên đầy đủ>

GTV SEO kính gửi đến anh/chị báo cáo tiến độ và KPI đạt được của dự án SEO tháng <n>, cụ thể như sau:

## 1. KẾT QUẢ KPI ĐẠT ĐƯỢC
| LOẠI KPI | HẠNG MỤC | CAM KẾT | KẾT QUẢ | TỶ LỆ HOÀN THÀNH THỰC TẾ | TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU | Link báo cáo |
|---|---|---|---|---|---|---|
| ORGANIC TRAFFIC | Tổng <đơn vị theo HĐ> tải về từ GA4, từ ngày <dd/mm> đến ngày <dd/mm> | … | … | …% | ≤100% | <link> |
| TOP | Bộ <i> — TOP <03/05/10> (SpySERP, ngày tracking <dd/mm>) | …% | …% | …% | ≤100% | <link> |
| NGUYÊN LIỆU DỰ ÁN | <hạng mục công việc> | … | … | …% | ≤100% | <link> |
| **KẾT QUẢ KPI** | | | | | **…%** | |

Như vậy, GTV SEO đã hoàn thành …% KPI theo cam kết tháng thứ <n> của hợp đồng SEO.

*Lưu ý: Báo cáo thứ hạng từ khoá được lấy từ SpySERP - check ở Google.com.vn, khu vực Việt Nam. Anh/chị vui lòng kiểm tra thứ hạng trong 2-3 ngày kể từ ngày nhận báo cáo.*

## 2. BÁO CÁO TIẾN ĐỘ DỰ ÁN THÁNG
| STT | Tên công việc | Thời hạn | Trạng thái | Kết quả công việc |
|---|---|---|---|---|

## 3. Các dữ liệu báo cáo khác (CRO)
## 4. Vấn đề phát sinh / tồn đọng
## 5. KẾ HOẠCH THÁNG TIẾP THEO

<Điều khoản nghiệm thu — NGUYÊN VĂN theo references/kpi-table-formats.md>
```

**Naming:** `Deliverables/<project-GTV>/<client>_Report_v1.md` + `<client>_Report_v1.docx`.

## Behavior Gates

1. **🧠 Think Before** — Trước khi render: mode nào? Entity chắc chắn GTV? Đơn vị traffic theo HĐ client này là gì? KPI nào có cam kết tháng này? Assumption sai làm hỏng bảng nghiệm thu → hỏi trước, không đoán.
2. **🔴 Evidence** — Mọi con số trong bảng KPI truy được về **nguồn + ngày/khoảng ngày đo** (SpySERP ngày tracking nào, GA4 từ ngày–đến ngày, Ahrefs/SemRush cho GEO). Không nguồn → `[CẦN SỐ LIỆU]`, không điền. Số nghiệm thu chỉ lấy từ nguồn chuẩn hợp đồng (SpySERP/GA4/Ahrefs-AIO theo Điều 1).
3. **✂️ Surgical** — Read-only với template gốc trong `GTV Ops/wiki/account/`; không sửa workbook dự án; chỉ tạo file output mới trong `Deliverables/<project-GTV>/`. Phát hiện wiki client cần update → note 1 câu, không tự sửa.
4. **🎯 Goal-driven** — Mục tiêu report: khách đủ evidence để reply "Đồng ý nghiệm thu kết quả KPI theo báo cáo" trong 4 ngày. Mọi hàng KPI phải có link báo cáo trỏ đúng folder `[Tên Dự Án] - SEO Reports` (khách quyền Comment).

## Anti-patterns

- ❌ Bịa số hoặc ước lượng số liệu KPI — thiếu thì để `[CẦN SỐ LIỆU]`.
- ❌ Paraphrase / "viết lại cho mượt" đoạn điều khoản nghiệm thu 4 ngày / 7 ngày.
- ❌ Ghi >100% ở cột TỶ LỆ HOÀN THÀNH ĐỂ NGHIỆM THU.
- ❌ Tính "Chưa cam kết" = 0% rồi kéo tụt trung bình KẾT QUẢ KPI.
- ❌ Dùng Ahrefs rank-tracker làm số nghiệm thu thứ hạng (nguồn chuẩn là SpySERP) hoặc Ahrefs traffic thay GA4. Hai nguồn lệch nhau → SpySERP/GA4 thắng, Ahrefs chỉ minh họa trend.
- ❌ Nhúng rate card, % tỷ trọng KPI → tiền, công thức hoàn trả, giá trị HĐ thật từ [[contract-playbook]] vào report/skill (confidential) — chỉ giữ điều khoản nghiệm thu vốn công khai với khách.
- ❌ Đưa cơ chế gate giải ngân theo đợt vào email khách (không có trong mẫu chuẩn) — chi tiết cách tính xem [[contract-playbook]] (🔒), chỉ dùng khi account cần giải thích trực tiếp.
- ❌ Lập OKRs mới trong mode `quy` (→ `okrs-gtv-tag-framework`) hoặc chèn phân tích SEO sâu (→ skill `seo-*`).
- ❌ Mix client GTV với học viên/case TAG; tiếng Việt không dấu trong output.
- ❌ Dùng tên khách + số HĐ thật làm ví dụ few-shot — phải ẩn danh hóa.

## References & wiki

- [references/kpi-table-formats.md](references/kpi-table-formats.md) — skeleton đầy đủ 3 chế độ, menu KPI chuẩn, điều khoản nghiệm thu nguyên văn, ví dụ đã điền (ẩn danh).
- [references/data-paths.md](references/data-paths.md) — map Ahrefs MCP tools từng ô bảng KPI, cách đọc export SpySERP/GA4, skeleton Path C, cấu trúc folder báo cáo khách.
- Nguồn nền (read-only, KHÔNG sửa; tên file/folder giữ nguyên văn filesystem, kể cả space thừa): `GTV Ops/wiki/account/3. MẪU BÁO CÁO CÔNG VIỆC HÀNG THÁNG.docx` · `GTV Ops/wiki/account/3.1 MẪU BÁO CÁO KPI DỰ ÁN - THÁNG CUỐI - NGHIỆM THU .docx` · `GTV Ops/wiki/account/(T11-2024) MẪU BÁO CÁO DỰ  ÁN/1. BÁO CÁO KẾT QUẢ.xlsx` · `GTV Ops/wiki/account/(T11-2024) MẪU BÁO CÁO DỰ  ÁN/GUIDELINE THIẾT LẬP FILE BÁO CÁO KHÁCH HÀNG.docx`.
- Wiki: [[kpi-commitment-template]] — menu KPI chuẩn (TOP theo bộ, Organic Traffic, GEO); [[contract-playbook]] — nguồn đo Điều 1 (SpySERP/Ahrefs/GA4), TOP lồng nhau, cách tính gate giải ngân theo đợt, bảo hành ≥90%/30 ngày (🔒 phần giá/hoàn trả confidential); [[tracking-schema]] — chỉ dùng làm evidence QA content nội bộ, KHÔNG đưa vào email khách.

## Changelog

- **v1.1 (2026-07-07):** chốt mẫu chế độ QUÝ (5 section: OKRs review + % hoàn thành, thứ hạng 3 tháng + Δ, KPI lũy kế, GEO quý, trọng tâm) và quy ước hàng GEO đủ 5 hàng khớp menu KPI (kèm cách gộp chỉ tiêu ngưỡng ≥2/4 vào trung bình) — do Claude tự đề xuất theo ủy quyền Vincent, chưa qua account dùng thật; hiệu chỉnh sau báo cáo thật đầu tiên.
- **v1.0 (2026-07-07):** khởi tạo — nền từ 2 docx mẫu báo cáo tháng/tháng cuối của Account, workbook `1. BÁO CÁO KẾT QUẢ.xlsx` (9 sheet), GUIDELINE thiết lập folder báo cáo, [[kpi-commitment-template]] và điều khoản nghiệm thu công khai trong [[contract-playbook]]. Chế độ QUÝ và hàng GEO chưa có mẫu canonical — chờ mẫu thật để tinh chỉnh v1.1.
