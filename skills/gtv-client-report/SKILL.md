---
name: gtv-client-report
description: "Sinh báo cáo client GTV theo mẫu Account chuẩn — layer REPORTING: chỉ render kết quả. Use when: (1) 'viết báo cáo tháng cho [client]', 'làm report KPI tháng thứ [n]'; (2) 'báo cáo quý / review OKRs quý [n] cho [client]'; (3) 'báo cáo nghiệm thu / báo cáo tháng cuối [client]'."
metadata:
  version: "1.4.2"
---

# GTV Client Report

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

Sinh báo cáo gửi khách hàng GTV (email + .docx) đúng MẪU BÁO CÁO của phòng Account: bảng KPI 7 cột, bảng tiến độ, dữ liệu CRO, điều khoản nghiệm thu nguyên văn. Skill này đứng **hạ nguồn** của `gtv-proposal` (KPI đã cam kết là input, không phải output) và **thượng nguồn** của việc gửi mail/nghiệm thu của Account.

🔒 **GTV-only, workspace-only**: skill đọc mẫu báo cáo account (ngoài repo, hỏi Lead) và có thể chạm dữ liệu client thật — chỉ chạy trong Claude Code workspace, KHÔNG đóng gói lên claude.ai. Không mix entity TAG dưới mọi hình thức.

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
- `$KPI_SOURCE` — nguồn KPI cam kết: workbook `1. BÁO CÁO KẾT QUẢ.xlsx` của dự án (sheet KPI/OKRs) hoặc trang client trong `00-client-context/` của instance.

**Optional:**
- `$RANK_EXPORT` — file/paste export SpySERP (bộ keyword cam kết + vị trí + ngày tracking).
- `$TRAFFIC_EXPORT` — file/paste export GA4 (Sessions hoặc Product Pageview, kênh Organic, theo khoảng ngày).
- `$CRO_DATA` — v1.4: 4 khối từ WS 13 (`13-cro/` của instance): 3a chuyển đổi kỳ này (micro GA4 đã QA + outcome đối soát, đúng nhãn), 3b phát hiện (evidence-backlog E≥2), 3c việc đã sửa + số quan sát trước/sau, 3d chờ phía khách. Không còn Time on site / Bounce. Tracking chưa PASS → câu chờ dev, không kết luận.
- `$PROGRESS` — danh sách công việc tháng (tên, thời hạn, trạng thái, kết quả).
- `$REPORT_FOLDER_URL` — link folder `[Tên Dự Án] - SEO Reports` để điền cột "Link báo cáo".

**Path detection (data ladder — chi tiết ở [references/data-paths.md](references/data-paths.md)):**
- **Path A (ưu tiên khi có MCP): Ahrefs MCP** — rank-tracker/gsc-*/site-explorer/brand-radar + render charts. ⚠️ Chỉ dùng cho **chart minh họa trend + GEO/AIO citation** (Ahrefs là công cụ đo Citation AI Overview theo Điều 1 HĐ — nguồn: [[contract-playbook]]). KHÔNG dùng làm số nghiệm thu thứ hạng/traffic.
- **Path B: export paste** — nguồn chuẩn hợp đồng: **thứ hạng = SpySERP (Google.com.vn, khu vực Việt Nam)**, **traffic = GA4**. Đây là số được điền vào bảng KPI nghiệm thu.
- **Path C (đường lùi cuối — luôn chạy được không cần MCP): account điền tay** — render skeleton đầy đủ với placeholder `[CẦN SỐ LIỆU: …]` từng ô.

## Workflow

### Bước 0 — Scope gate & confirm (🔴 bắt buộc, chờ xác nhận rồi mới chạy)
- [ ] Xác nhận `$CLIENT` là **client GTV** (đối chiếu `00-client-context/` của instance nếu nghi ngờ). Nghi ngờ mix TAG → dừng, hỏi.
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
- **`thang`**: bảng TIẾN ĐỘ (`STT | Tên công việc | Thời hạn | Trạng thái | Kết quả công việc`; trạng thái chuẩn: Đã làm / Đang làm / Cần xử lý) → dữ liệu CRO (4 khối 3a–3d theo `kpi-table-formats.md` mục 3, ảnh che PII) → vấn đề phát sinh (3 ý bắt buộc: điều chỉnh web / thay đổi từ KH / khâu content) → kế hoạch tháng sau → 2 câu Lưu ý cố định (SpySERP Google.com.vn; khách check thứ hạng trong 2-3 ngày) → **điều khoản nghiệm thu THÁNG nguyên văn** (4 ngày xác nhận / 7 ngày làm việc tạm dừng / cộng dồn tối đa 14 ngày / >15 ngày điều chỉnh KPI).
- **`quy`**: render đủ 5 section theo mẫu v1.1 (references mục 6): OKRs review (+% hoàn thành, tổng quý) → diễn biến thứ hạng 3 tháng + Δ quý trước → KPI lũy kế 3 tháng + trung bình → GEO/AI visibility quý (nếu HĐ có) → vấn đề & trọng tâm quý tới. ⚠️ Chỉ cập nhật Status/% của OKRs đã hoạch định — KHÔNG lập OKRs mới. Không kèm điều khoản nghiệm thu 4/7 ngày (nghiệm thu theo đợt/tháng). Cuối report luôn kèm dòng "Format báo cáo quý v1.1 — góp ý sau lần dùng đầu".
- **`nghiem-thu`**: như `thang` nhưng: câu chốt tham chiếu số HĐ + lời cảm ơn; KHÔNG có "kế hoạch tháng tiếp theo"; thay bằng **đề xuất họp nghiệm thu** (giờ/ngày cụ thể); điều khoản: khách phản hồi trong 4 ngày → chuyển giai đoạn **Bảo hành kết quả 30 ngày**; sau **7 ngày làm việc** không phản hồi → báo cáo **mặc nhiên được chấp thuận** → thủ tục thanh lý HĐ.
- 🔴 Đoạn điều khoản nghiệm thu là ngôn ngữ pháp lý đã chuẩn hóa — **render nguyên văn theo skeleton trong references, không paraphrase.**

### Bước 5 — Xuất output kép
1. **Markdown draft email** — đúng skeleton, tiêu đề `[GTV SEO] – BÁO CÁO TIẾN ĐỘ VÀ KPI DỰ ÁN (<Tên dự án>) THÁNG THỨ <n>`, account dán thẳng vào Gmail.
2. **File .docx theo MẪU** — gọi skill `docx` render từ markdown, giữ đúng cấu trúc bảng (hàng chốt KẾT QUẢ KPI merge ô như mẫu gốc).
Ghi cả 2 file về `09-reporting/` của instance (theo `_REFERENCE/folder-map.md`), tên `<client>_Report_v1.md` / `.docx` (tăng `_v2`, `_v3` nếu trùng).

### Bước 6 — Delivery checklist
- [ ] Đúng entity GTV, không lẫn case/số liệu TAG.
- [ ] Mọi con số có nguồn + ngày đo; ô thiếu để `[CẦN SỐ LIỆU]`, không bịa.
- [ ] Cột nghiệm thu không ô nào >100%; "Chưa cam kết" loại khỏi trung bình.
- [ ] Điều khoản nghiệm thu nguyên văn, đúng biến thể chế độ.
- [ ] Tiếng Việt có dấu đầy đủ; thuật ngữ SEO giữ tiếng Anh.
- [ ] File đặt đúng `09-reporting/` của instance, không sửa gì trong thư mục mẫu báo cáo account (ngoài repo, hỏi Lead).

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

**Naming:** `09-reporting/<client>_Report_v1.md` + `<client>_Report_v1.docx`.

## Luật GEO/AI metrics trong report (v1.2 — mọi số là snapshot 08/2026, refresh theo lint quý)

Áp cho hàng GEO của bảng KPI + section GEO quý. Nguồn: wiki [[AI Visibility Measurement]] Batch 39.

1. **Citation/impression AI luôn label DIRECTIONAL.** Mọi số citation/impression (Ahrefs AIO, brand-radar, GSC Generative AI) render kèm nhãn "(directional)"; **đối chiếu server logs (referral thực) trước khi claim win** trong email khách. Nghi ngờ mọi chart "citations tăng/giữ vững" đứng một mình: citation counts nhiễm bot prompt-tracking + là lagging indicator — page 404 + deindexed vẫn nhận daily citations ~8 tuần (@top5seo 07/2026, experiment n=1, tác giả tự label "half-baked" — cảnh báo phương pháp luận, không phải hằng số).
2. **Tách 2 metric: found (retrieval presence) vs cited.** Được retrieve ≠ được cite, và tỷ lệ do ENGINE quyết chứ không phải page: Perplexity để 76% present-pages ở dạng uncited vs ChatGPT cite 61% (experiment Ahrefs 4 tháng 02-06/2026, n=2 brand cùng công ty, COI vendor — directional). Brand Radar phân biệt được cited/found → hàng GEO tách "retrieval presence" khỏi "citation", không gộp thành 1 số.
3. **Evidence-bar khi khách/vendor mang claim GEO.** 4 fake proofs KHÔNG phải evidence (cả 4 xảy ra với mọi text file trên open web — falsification cats.txt, Williams-Cook 08/2026): (a) được AI bot crawl, (b) được Google index, (c) fact được RAG lặp lại, (d) LLM xác nhận tactic work ("LLM tự xác nhận" = convergence problem — model chỉ trả về trung bình discourse, không phải measurement). Script phản hồi lịch sự cho Account: *"Cảm ơn anh/chị đã chia sẻ tài liệu. Bốn dấu hiệu này (được crawl, được index, thông tin được AI nhắc lại, AI xác nhận) xảy ra với mọi nội dung công khai trên web nên chưa đủ làm bằng chứng hiệu quả. GTV đề xuất đối chiếu bằng số referral thực từ server logs/GA4 trước khi kết luận và đưa vào kế hoạch."*
4. **Đặt kỳ vọng cam kết GEO.** Citation slot là tạm thời: page được cite chỉ ~1/3 số ngày eligible, ~25% cite đúng 1 lần rồi biến mất (Ahrefs 4 tháng, n=2, vendor); cited sources drift 56-74%/tuần (SISTRIX 82.619 prompts/17 tuần). → Cam kết **topic-level Share of Voice**, KHÔNG cam kết "xuất hiện cho prompt X". AI traffic KHÔNG phải primary KPI — attribution gãy (user discover trong ChatGPT, quay lại qua Google/direct).
5. **Kênh bắt buộc + conversion (v1.3, Lead chốt 29/08/2026).** Brand Mention LLM ĐẠT khi có mention trên **cả ChatGPT lẫn Google AI (AI Mode/Gemini)** — thay ngưỡng "≥2/4 tool"; Perplexity/Copilot/Claude là bonus. Report tháng có **hàng "Conversion từ AI Assistant"** (GA4 channel group "AI Assistant": key events · CVR · bội số vs Organic) — **directional, không nghiệm thu, không vào trung bình KPI**; là số đối chiếu bắt buộc trước khi email khách nói "GEO đang thắng". Benchmark đặt kỳ vọng: ≈10× (GTV n=1) · 23× (Ahrefs) · 15,9% vs 1,76% (Seer) — nhãn directional, mẫu người khác. Case public: luật ẩn danh ở `references/kpi-table-formats.md` § "Dùng số GEO cho case study công khai".

## Behavior Gates

1. **🧠 Think Before** — Trước khi render: mode nào? Entity chắc chắn GTV? Đơn vị traffic theo HĐ client này là gì? KPI nào có cam kết tháng này? Assumption sai làm hỏng bảng nghiệm thu → hỏi trước, không đoán.
2. **🔴 Evidence** — Mọi con số trong bảng KPI truy được về **nguồn + ngày/khoảng ngày đo** (SpySERP ngày tracking nào, GA4 từ ngày–đến ngày, Ahrefs/SemRush cho GEO). Không nguồn → `[CẦN SỐ LIỆU]`, không điền. Số nghiệm thu chỉ lấy từ nguồn chuẩn hợp đồng (SpySERP/GA4/Ahrefs-AIO theo Điều 1).
3. **✂️ Surgical** — Read-only với template gốc trong thư mục mẫu báo cáo account (ngoài repo, hỏi Lead); không sửa workbook dự án; chỉ tạo file output mới trong `09-reporting/` của instance. Phát hiện wiki client cần update → note 1 câu, không tự sửa.
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
- ❌ Render số citation/impression AI không kèm nhãn directional, hoặc claim win GEO chỉ từ chart citations mà chưa đối chiếu referral thực (server logs/GA4).
- ❌ Cam kết "xuất hiện cho prompt X" hoặc dùng AI traffic làm primary KPI trong report (→ luật GEO/AI metrics mục 4).

## References & wiki

- [references/kpi-table-formats.md](references/kpi-table-formats.md) — skeleton đầy đủ 3 chế độ, menu KPI chuẩn, điều khoản nghiệm thu nguyên văn, ví dụ đã điền (ẩn danh).
- [references/data-paths.md](references/data-paths.md) — map Ahrefs MCP tools từng ô bảng KPI, cách đọc export SpySERP/GA4, skeleton Path C, cấu trúc folder báo cáo khách.
- Nguồn nền (read-only, KHÔNG sửa; tên file/folder giữ nguyên văn filesystem, kể cả space thừa): `<mẫu account, ngoài repo>/3. MẪU BÁO CÁO CÔNG VIỆC HÀNG THÁNG.docx` · `<mẫu account, ngoài repo>/3.1 MẪU BÁO CÁO KPI DỰ ÁN - THÁNG CUỐI - NGHIỆM THU .docx` · `<mẫu account, ngoài repo>/(T11-2024) MẪU BÁO CÁO DỰ  ÁN/1. BÁO CÁO KẾT QUẢ.xlsx` · `<mẫu account, ngoài repo>/(T11-2024) MẪU BÁO CÁO DỰ  ÁN/GUIDELINE THIẾT LẬP FILE BÁO CÁO KHÁCH HÀNG.docx`.
- Wiki: [[kpi-commitment-template]] — menu KPI chuẩn (TOP theo bộ, Organic Traffic, GEO); [[contract-playbook]] — nguồn đo Điều 1 (SpySERP/Ahrefs/GA4), TOP lồng nhau, cách tính gate giải ngân theo đợt, bảo hành ≥90%/30 ngày (🔒 phần giá/hoàn trả confidential); [[tracking-schema]] — chỉ dùng làm evidence QA content nội bộ, KHÔNG đưa vào email khách.

## Changelog

- **v1.4.2 (2026-10-27):** bản root thành bản gốc, bản SEO Production sinh bằng `tools/port-dieu-phoi.py`. Lấy từ bản SEO Production: `references/kpi-table-formats.md` mục 3b ghi đường dẫn `13-cro/<CLIENT>_evidence-backlog`.
- **v1.4.1 (2026-10-19, Lead duyệt 19/10):** `references/data-paths.md` dòng GEO AI responses: KPI AIO theo từ khoá đọc `google_ai_overviews_keywords`, không báo `all_platforms` (cộng cả AIO theo từ khoá lẫn trích dẫn từ prompt). Đồng bộ `geo-tracking-prompt-selection` 1.6.
- **v1.4 (2026-09-13):** §3 CRO đổi từ Time on site / Bounce / CTA click thành 4 khối 3a–3d (chuyển đổi đúng nhãn · phát hiện E≥2 · đã sửa + số quan sát · chờ khách) nhận từ WS 13 (`cro-audit` v2 `report-hook.md`, `cro-measurement-plan`). Đồng bộ fork SEO Production `kpi-table-formats.md` mục 3 (MIGRATION v2026.09.4). Nền: plan CRO add-on Lead duyệt 12/09.
- **v1.3 (2026-08-29, Lead duyệt 29/08):** luật GEO #5 — kênh bắt buộc ChatGPT + Google AI (thay ≥2/4; HĐ cũ giữ chữ HĐ tới gia hạn), hàng **Conversion từ AI Assistant** (GA4 channel group, directional, không nghiệm thu) trong menu KPI + skeleton tháng + quý, luật ẩn danh case study công khai (ngành chung / jobsite không nói ngành / tỷ lệ thay tuyệt đối / consent). `references/data-paths.md` §2c + `kpi-table-formats.md` mục 3/4/quý cập nhật; quy ước gộp trung bình v1.3 (ĐẠT 100% · 1/2 kênh 50% · 0 kênh 0%). Đồng bộ GE-36 `tier-1-geo.md` v2.0.1 + `geo-tracking-prompt-selection` v1.3.
- **v1.2 (2026-08-22):** thêm section "Luật GEO/AI metrics trong report" — 4 luật: label DIRECTIONAL + đối chiếu server logs trước khi claim win (bot noise + lag, n=1 @top5seo); tách found vs cited (Perplexity 76% uncited vs ChatGPT 61%, Ahrefs 4 tháng, COI vendor); evidence-bar 4 fake proofs + script phản hồi cho Account (cats.txt, Williams-Cook); kỳ vọng cam kết topic-level SoV (~1/3 ngày eligible, 25% one-shot, drift 56-74%/tuần), AI traffic không phải primary KPI. Thêm 2 anti-patterns + note cited/found ở data-paths.md §2c. (Lead duyệt 22/08, nền Batch 39.)
- **v1.1 (2026-07-07):** chốt mẫu chế độ QUÝ (5 section: OKRs review + % hoàn thành, thứ hạng 3 tháng + Δ, KPI lũy kế, GEO quý, trọng tâm) và quy ước hàng GEO đủ 5 hàng khớp menu KPI (kèm cách gộp chỉ tiêu ngưỡng ≥2/4 vào trung bình) — do Claude tự đề xuất theo ủy quyền Lead, chưa qua account dùng thật; hiệu chỉnh sau báo cáo thật đầu tiên.
- **v1.0 (2026-07-07):** khởi tạo — nền từ 2 docx mẫu báo cáo tháng/tháng cuối của Account, workbook `1. BÁO CÁO KẾT QUẢ.xlsx` (9 sheet), GUIDELINE thiết lập folder báo cáo, [[kpi-commitment-template]] và điều khoản nghiệm thu công khai trong [[contract-playbook]]. Chế độ QUÝ và hàng GEO chưa có mẫu canonical — chờ mẫu thật để tinh chỉnh v1.1.
