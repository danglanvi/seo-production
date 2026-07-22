---
type: sop
tier: monthly-review
phase: project-management
last_updated: 2026-07-19
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/5. Review project /Guideline Review dự án PSP _ Update Th2.2024 - GTV SEO.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/1. Kick off - hoạch định & quản lý dự án/Hoạch định KPI & OKRs Template mẫu cho dự án.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/1. Kick off - hoạch định & quản lý dự án/Kick off dự án/2. file mẫu kick off - review & hoạch định KPI và OKRs.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/1. Đào tạo Quản lý/Mẫu template report tuần - PSP Department - GTV SEO.xlsx
  - sop/09-project-timeline/10-thang-thuc-day.md
items_count: 21 (+5 quarterly)
tags: [sop, self-checklist, monthly-review, project-management, kpi, okrs, quality-gate]
---

# Self-Checklist: Monthly Project Review (SEO Lead)

> **Khi dùng:** SEO Lead Project tự check TRƯỚC khi trình review tháng lên Manager/Director.
> **Gate:** Chưa pass đủ **P0 (7 items)** → **KHÔNG trình review**. Buổi review với data thiếu = lãng phí slot của Manager/Director và mất 1 chu kỳ điều chỉnh.
> **Số items:** 21 (MR-01 → MR-21) = 6 KPI & Sức khỏe + 4 OKRs & Tiến độ + 5 Mốc cứng & Rủi ro + 4 Chất lượng & Bài học + 2 Chuẩn bị trình bày. Tháng cuối quý (T3/T6/T9) thêm 5 items MRQ.
> **Scoring:** Self Score /21 → Self %. Benchmark ≥90% mới đạt chuẩn trình review.

## Map item → nguồn

| ID | Label | Nguồn |
|---|---|---|
| MR-01 | KPI Top vs lộ trình cam kết | Guideline Review Th2.2024 — sheet "2.1 Câu hỏi - Review" mục 2 KPI · template Geyser audit KPI (cột Hiện tại / Thiếu / Thực tế) |
| MR-02 | KPI Traffic vs cam kết | Kick off file mẫu — công đoạn 1.3 (KPI Traffic, note Ahrefs) · Guideline Review sheet 1 mục 2.0 |
| MR-03 | KPI nội bộ +20% | Hoạch định KPI & OKRs Template — sheet KPI, lưu ý 7 |
| MR-04 | Phễu ranking kế cận (top 11-20) | Guideline Review — sheet "1. Checklist review dự án" mục 2.0 |
| MR-05 | Xu hướng traffic + audit giai đoạn giảm | Guideline Review sheet 1 mục 2.0 + sheet 2.1 mục 13 Data Analysis |
| MR-06 | Đối chiếu 2 nguồn data | Guideline Review sheet 1 (Biểu đồ GSC/GA/Spyserp) · Review tuần 14 (SERPRobot vs GA) |
| MR-07 | OKRs quý — % tiến độ per KR | Hoạch định KPI & OKRs Template — sheet OKRs, lưu ý 7 |
| MR-08 | Tiến độ công đoạn vs timeline 10 tháng | Guideline Review sheet 1 mục 1.0 (>80% task) · [[sop/09-project-timeline/10-thang-thuc-day]] |
| MR-09 | Nhân sự content pipeline | Guideline Review sheet 2.1 mục 10 Nhân sự |
| MR-10 | Zero việc ngoài hệ thống | File kick off — sheet "Review tiến độ" mục 1.2 (không file nằm ngoài wework) |
| MR-11 | Mốc cứng tháng tới | [[sop/09-project-timeline/10-thang-thuc-day]] — mốc cứng per tháng + "Rủi ro nếu trễ" |
| MR-12 | Red flags quét đủ 5 | Quy trình 10 tháng + tài liệu training Account mục 06 (red flags) |
| MR-13 | Việc kẹt phía khách + số ngày | Guideline Review sheet 2.1 mục 12 Phối hợp với KH |
| MR-14 | Khó khăn — Gốc rễ — Giải pháp | File kick off — sheet "Review tiến độ" mục 3-4 · Mẫu report tuần PSP (block KHÓ KHĂN - GIẢI PHÁP) |
| MR-15 | Plan thúc đẩy có logic + backup | Guideline Review sheet 2.1 mục 3-5 (plan thúc đẩy traffic/top) |
| MR-16 | Quality sampling content/onpage | README 06-self-checklist (3-Level Review) · Guideline Review sheet 2.1 mục 8 ("chọn ra một bài để review chi tiết") |
| MR-17 | Trạng thái audit content tổng thể | Guideline Review sheet 1 mục 1.0 + sheet 2.1 mục 8 Content |
| MR-18 | Log bài học tháng | SEO Production instance — `12-feedback-lessons/` |
| MR-19 | Đề xuất cần Manager/Director quyết | Guideline Review — sheet "2. Flow & Mindset" (ấn định ngày, nhiều phương án) |
| MR-20 | Gửi tài liệu trước 36h | File kick off — sheet "Review tuần" (Gửi trước 36h trước buổi họp) |
| MR-21 | Format trình bày chuẩn | Guideline Review — Flow & Mindset ("nắm thực tế công việc show ra hơn là nghe trình bày") |

---

## P0 Gate — 7 items bắt buộc trước khi trình

**MR-01 · MR-02 · MR-07 · MR-11 · MR-12 · MR-13 · MR-19**

Logic chọn: đây là 7 items mà nếu thiếu, Manager/Director **không thể ra quyết định** trong buổi review — số KPI (01, 02), tiến độ mục tiêu (07), rủi ro sắp tới (11, 12), điểm kẹt ngoài kiểm soát team (13), và danh sách quyết định cần cấp trên chốt (19). 14 items còn lại thiếu thì buổi review kém chất lượng; 7 items này thiếu thì buổi review **vô nghĩa**.

---

## Nhóm A — KPI & Sức khỏe dự án

### MR-01 — KPI Top tháng vs lộ trình cam kết (có số + % lệch)

Trình bày theo format 3 cột của template Geyser audit KPI: **Mục tiêu — Hiện tại — Thiếu** cho từng tầng top (Top 3/5/10/15/30 tùy hợp đồng), từng bộ keyword cam kết riêng nếu hợp đồng có nhiều bộ.

- Số tuyệt đối (bao nhiêu keyword) + % lệch so với lộ trình tháng này.
- Bộ key tương ứng bao nhiêu URL; % KPI thiếu tương ứng khoảng bao nhiêu keyword, bao nhiêu URL (câu hỏi chuẩn của sheet 2.1 mục 2).
- Nếu hợp đồng nhiều bộ keyword cam kết khác nhau → mỗi bộ 1 bảng riêng (lưu ý 4, file Hoạch định KPI).

✅ "Top 10 blog: mục tiêu 186/372 KW, hiện tại 143, thiếu 43 (-23%), tương ứng ~12 URL."
❌ "Top 10 đang thiếu một chút, team đang đẩy."

### MR-02 — KPI Traffic tháng vs cam kết (đúng nguồn đo cam kết)

- Số traffic hiện tại vs mục tiêu tháng + % lệch.
- Đo bằng **đúng nguồn ghi trong hợp đồng**: GA (users organic search) mặc định; nếu hợp đồng cam kết bằng Ahrefs thì báo bằng Ahrefs (note chuẩn file kick off, công đoạn 1.3).
- Nếu ngành có tính mùa vụ → so thêm YoY, không chỉ MoM.

### MR-03 — Đối chiếu KPI nội bộ (cao hơn cam kết ~20%)

KPI nội bộ lập cao hơn KPI khách hàng ~20%/tháng (lưu ý 7, file Hoạch định KPI) để làm buffer. Check:

- Đang đạt so với KPI nội bộ hay chỉ đạt so với KPI khách?
- Lệch KPI nội bộ nhưng vẫn đạt KPI khách = **early warning**, phải nêu trong review chứ không giấu.

### MR-04 — Phễu ranking kế cận đủ nuôi KPI 2 tháng tới

Rule chuẩn Guideline Review mục 2.0: **top 11-20 cộng dồn với top 10 phải ≥ KPI top của 2 tháng sau đó**. Nếu phễu không đủ → KPI 2 tháng tới sẽ vỡ dù tháng này đạt. Trình rõ: số keyword đang nằm 11-20, thuộc topic nào, plan đẩy nhóm nào.

### MR-05 — Xu hướng traffic ổn định + giai đoạn giảm đã có nguyên nhân

- Biểu đồ GSC + GA 3-6 tháng: xu hướng đi lên/ổn định/đi xuống.
- **Mọi giai đoạn giảm trên biểu đồ phải có nguyên nhân đã audit** (câu hỏi mục 13 Data Analysis: "giai đoạn giảm team đã audit và tìm ra nguyên nhân?"). Nếu rớt chưa rõ nguyên nhân → chạy [[tier-3-ranking-drop-runbook]] TRƯỚC buổi review, mang kết quả triage vào.

### MR-06 — Hai nguồn data khớp nhau

Số tracker (SERPRobot/Spyserp/rank tracker) vs GSC phải nhất quán; traffic GA vs GSC clicks cùng xu hướng. Chênh lệch bất thường (tracker nói đạt, GSC nói giảm) phải được giải thích trước — Manager phát hiện chênh trong buổi review = mất uy tín toàn bộ số liệu.

---

## Nhóm B — OKRs & Tiến độ công việc

### MR-07 — OKRs quý: % tiến độ điền đủ per KR

Rule chuẩn sheet OKRs (lưu ý 7): "Hằng tháng hãy tự review dự án và tổng kết tình trạng ở mục Tiến độ OKRs theo tháng — bao gồm tiến độ (điền %) và tình trạng cụ thể (comment)."

- Mỗi KR có: % hoàn thành + comment tình trạng (không chỉ Done/Not done).
- KR nào chậm → nêu lý do + ảnh hưởng lên Objective.
- OKRs bao gồm cả Content lẫn SEO (lưu ý 6 — lập chung với team Content, review cũng report chung).

### MR-08 — Tiến độ công đoạn vs timeline 10 tháng

- Đối chiếu tháng dự án hiện tại (T1-T10) với [[sop/09-project-timeline/10-thang-thuc-day]]: công đoạn nào đúng hạn / trễ / trễ >1 tuần.
- Chuẩn đạt legacy: **>80% task hoàn thành, task trọng yếu trong tháng phải xong 100%** (Guideline Review sheet 1 mục 1.0).
- Công đoạn trễ >1 tuần: nêu kèm nguyên văn "Rủi ro nếu trễ" từ Bảng B instance SEO Production.

### MR-09 — Nhân sự content pipeline đủ lực cho tháng tới

Bộ câu hỏi chuẩn sheet 2.1 mục 10: số bài cần viết tháng tới là bao nhiêu — đang có bao nhiêu writer/editor — mỗi tuần 1 writer nhận bao nhiêu bài — lượng đó đủ chưa, dự trù rủi ro gì (writer nghỉ, dự án khác giành lực)? Thiếu → đề xuất trong MR-19.

### MR-10 — Zero việc nằm ngoài hệ thống tracking

Mọi task, file, plan phải nằm trong hệ thống quản lý dự án (legacy: wework; hiện tại: instance SEO Production + tracking sheets). Rule gốc sheet Review tiến độ: "không được file nào nằm ngoài wework để đảm bảo thông tin dự án được lưu vết." Review chỉ trình từ hệ thống — không trình từ file cá nhân.

---

## Nhóm C — Mốc cứng & Rủi ro

### MR-11 — Mốc cứng tháng tới: ai giữ, trễ mất gì

Liệt kê mốc cứng của tháng tới theo timeline 10 tháng (vd T3: Content Entity xong ≤15 ngày đầu, Content URL SEO xong hết T3, xử lý audit content xong; T4: onpage URL SEO chốt; T6: Content Strategy chốt + gate offpage...). Mỗi mốc ghi 3 cột:

1. Mốc gì + deadline cụ thể.
2. **Ai giữ** (team mình / khách / coder / bên thứ ba).
3. **Trễ thì mất gì** — nguyên văn "Rủi ro nếu trễ" (ngôn ngữ nói được với khách).

### MR-12 — Red flags: quét đủ 5 cờ, cờ nào đỏ phải khai

Quét đủ — kể cả khi kết quả là "không có":

| # | Red flag | Ngưỡng |
|---|---|---|
| 1 | Traffic sau T6 | < 70% lộ trình cam kết |
| 2 | SLA duyệt content phía khách | quá hạn ≥ 2 lần |
| 3 | Hạng mục kẹt ở coder/dev | > 2 tuần |
| 4 | Thay đổi phạm vi (scope change) | bất kỳ — khách thêm/đổi bộ keyword, đổi site, đổi cấu trúc ngoài hợp đồng |
| 5 | Khách hỏi/gợi ý mua traffic users | bất kỳ — hạng mục rủi ro cao, chỉ SEO Director duyệt (timeline T8-T9 ⚠) |

Cờ đỏ → bắt buộc xuất hiện trong MR-19 (đề xuất cần cấp trên quyết), không được để Manager tự phát hiện.

### MR-13 — Việc kẹt phía khách: liệt kê + số ngày

Format chuẩn: hạng mục — ngày gửi yêu cầu — **số ngày khách đang giữ** — ảnh hưởng dây chuyền (vd: khách chưa gửi ảnh 12 ngày → 50 bài chưa chèn ảnh → onpage trễ theo) — action đốc thúc đã làm + đề xuất escalate qua Account nếu cần. (Câu hỏi gốc sheet 2.1 mục 12: "Task nào cần KH support? Timeline có trì trệ không? Có phương án hạn chế chưa?")

### MR-14 — Khó khăn — Gốc rễ — Giải pháp (đủ 3 tầng)

Mỗi khó khăn lớn trình theo đúng 3 tầng của sheet Review tiến độ:

- **Khó khăn**: cụ thể Who-What-Where-When, phân biệt vấn đề lớn vs nhỏ.
- **Gốc rễ**: là một *nguyên nhân*, không phải một hành động; hỏi "tại sao" liên tục để đào xuống.
- **Giải pháp**: nhiều phương án nếu được, ấn định ngày trước rồi tìm phương án khớp timeline (mindset Guideline Review).

### MR-15 — Plan thúc đẩy tháng tới có logic chọn + backup

Bộ câu hỏi chuẩn sheet 2.1 mục 4-5: đẩy topic gì — action cụ thể — logic/tiêu chí chọn URL — **backup plan nếu triển khai xong vẫn chưa đạt**. Phương án hợp lý tham chiếu legacy: chọn URL trong top <15 cùng topic; ưu tiên bài top 6-10 (thêm traffic ngay) và 11-20 (đẩy vào top 10); tối ưu Featured Snippet. Plan không có backup = chưa đạt.

---

## Nhóm D — Chất lượng & Bài học

### MR-16 — Quality sampling: bài random tháng qua đã qua 3-Level Review

- Chọn random 2-3 bài content/onpage publish trong tháng → confirm đã đi đủ 3-Level Review (Self-check 100% → SEO EX Verify → Lead random 25-30%) trên Tracking Sheet.
- Mang theo 1 bài để review chi tiết nếu Manager yêu cầu (thao tác chuẩn sheet 2.1 mục 8: "Chọn ra một bài để review chi tiết").
- Gap (Self − Lead) tháng này có writer nào ≥3 flag → nêu (dính KPI rule 50%).

### MR-17 — Trạng thái audit content tổng thể

Website còn bài thin content / kém chất lượng không? Đã xử lý audit content tổng thể chưa (mốc chuẩn: xong hết T3, dự án lớn 85% hết T4)? Content giữ lại đã có action gì? Tổng URL toàn site bao nhiêu, còn bao nhiêu bài sắp triển khai? (Sheet 2.1 mục 8.)

### MR-18 — Bài học & feedback tháng đã log `12-feedback-lessons`

Mỗi tháng tối thiểu ghi nhận: feedback từ khách/Account, bài học vận hành (điều gì làm lại sẽ làm khác), pattern lỗi lặp lại — log vào `12-feedback-lessons/` của instance SEO Production trước buổi review. Review mà không có bài học = tháng đó không học được gì (mặc định là sai).

### MR-19 — Đề xuất điều chỉnh cần Manager/Director quyết

Danh sách quyết định cần cấp trên chốt, mỗi mục kèm **phương án đề xuất + trade-off** (không đem vấn đề trống lên chờ cấp trên nghĩ hộ). Ví dụ loại quyết định: điều chỉnh mục tiêu/KPI nội bộ, retiming công đoạn, thêm ngân sách (content/backlink/coder), thêm nhân sự, thay đổi phạm vi với khách, kích hoạt hạng mục rủi ro cao (traffic users — chỉ Director). Cờ đỏ từ MR-12 bắt buộc có mặt ở đây.

---

## Nhóm E — Chuẩn bị trình bày

### MR-20 — Gửi tài liệu review trước 36h

Rule chuẩn legacy (sheet Review tuần): tài liệu gửi trước **36h** trước buổi họp để Manager/Director đọc trước — buổi review dùng để thảo luận quyết định, không dùng để đọc số liệu lần đầu.

### MR-21 — Trình từ data thực tế, đúng format hiện trạng → khoảng cách → gốc rễ → plan

- Mọi claim có link data/file hệ thống đính kèm — "phải nắm thực tế công việc show ra hơn là nghe các bạn trình bày không" (Flow & Mindset).
- Thứ tự trình: hiện trạng KPI → khoảng cách → khó khăn & gốc rễ → plan + đề xuất (khớp flow sheet Review tiến độ mục 1→4).

---

## Phần mở rộng QUÝ (tháng cuối quý: T3 / T6 / T9)

Tháng review trùng cuối quý → thêm 5 items MRQ. Nhịp chuẩn timeline 10 tháng: OKRs lập T1 → quý 2 tại T3 → quý 3 tại T6 → review T9.

### MRQ-01 — Chấm điểm OKRs quý vừa kết thúc

Từng KR: % đạt cuối cùng + lý do miss (nếu <100%) + bài học rút cho quý sau. Không chấm gộp cả Objective khi KR bên trong lệch nhau.

### MRQ-02 — OKRs quý mới lập đúng chuẩn

Theo 6 lưu ý chuẩn file Hoạch định KPI & OKRs: ≤5 Objective (thường ~3/quý) · mỗi Objective ≤5 KR (nhiều hơn → nén lại, link triển khai để riêng) · OKRs ≠ plan task (góc nhìn tổng quan, không liệt kê task vụn) · khớp timeline 10 tháng · lập chung với team Content · KR đo lường được theo S.M.A.R.T.

### MRQ-03 — Cross-review chéo

Dự án được review chéo bởi Lead dự án khác hoặc Manager theo bộ 13 hạng mục câu hỏi Guideline Review sheet 2.1 (Tổng quan → KPI → Plan → Topical Map → Cấu trúc → Content → Backlink → Nhân sự → Workload → Phối hợp KH → Data Analysis). Người review giữ mindset chuẩn: **đặt câu hỏi cho đến khi team tự nhìn ra vấn đề, không đưa đáp án trước**.

### MRQ-04 — Audit định kỳ quý đã chạy + kết quả vào review

Theo nhịp timeline: T4 audit định kỳ (đo hiệu quả + xử lý) · T7 logfile + full audit toàn diện · T10 tổng kết. Quý nào tới nhịp audit → kết quả audit phải nằm trong tài liệu review quý.

### MRQ-05 — Đo AI visibility / GEO theo nhịp quý

Baseline T1 → đo giữa kỳ T6 → báo cáo kép T10 (SEO + GEO). Check: citation share các query tracking, bài mất traffic vì AIO (đối chiếu [[tier-3-ranking-drop-runbook]] bước triage TR-04).

---

## 3-Level Review áp dụng

| Level | Ai | Scope | Mục đích |
|---|---|---|---|
| ① **Self-Check** | SEO Lead Project | 100% tháng — tick toàn bộ MR-01→21 (+MRQ nếu cuối quý) trước khi trình | Gate trình review; tự accountability về data |
| ② **Manager Verify** | SEO Manager | 100% buổi review — verify nhanh 7 items P0 + chất vấn theo bộ câu hỏi 13 hạng mục | Đúng vai người hỏi: "đặt câu hỏi đến khi team tự nhìn ra" |
| ③ **Director Review** | SEO Director | **Random 25-30%** dự án/tháng — re-score độc lập checklist này, so Self vs Director | Catch drift; Gap ≥3 items/quý → cờ đỏ năng lực Lead, đưa vào đánh giá KPI quản lý |

Cơ chế game-theoretic giữ nguyên như content checklist: Lead không biết tháng nào dự án mình bị Director deep-dive → incentive tick trung thực (Mixed Strategy NE).

## Tracking columns đề xuất (Sheet "Tracking Monthly Review")

Theo convention [[tracking-schema]]:

| Nhóm | Cột | Field |
|---|---|---|
| Thông tin | A-G | STT · Dự án · Tháng dự án (T1-T10) · SEO Lead PIC · Ngày review · Link tài liệu review · Trạng thái (Trình được / Trả về) |
| Self-Check | H-AB | MR-01 → MR-21 (tick 1/0) |
| Quarterly | AC-AG | MRQ-01 → MRQ-05 (chỉ điền tháng cuối quý; để trống nếu không áp dụng — không tính denominator, theo Skip Rules của tracking-schema) |
| Score | AH-AJ | Self Score (/21 hoặc /26) · Self % · Self Note |
| Manager Verify | AK-AM | Manager PIC · P0-Pass? (Y/N — N = không trình) · Manager Note |
| Director Review | AN-AS | Director PIC · Review Date · Director Score · Gap (Self−Director) · Flag Items · Director Note |
| Red flags | AT | Red flags active (liệt kê # từ MR-12, để trống nếu sạch) |

---

## Ghi chú nguồn & modernization

- Khung câu hỏi review, phễu 11-20, rule >80% task, mindset review: giữ nguyên từ **Guideline Review dự án PSP Th2.2024** (giá trị nhất trong bộ legacy — vẫn đúng nguyên vẹn 2026).
- KPI nội bộ +20%, format Mục tiêu/Hiện tại/Thiếu, chuẩn OKRs ≤5×≤5: từ bộ file **Hoạch định KPI & OKRs** + **file mẫu kick off** (2020) — format giữ, tool đổi (Spyserp/SERPRobot → rank tracker hiện hành; wework → instance SEO Production).
- Red flags 5 cờ, mốc cứng "Rủi ro nếu trễ", nhịp OKRs quý T1/T3/T6/T9, GEO quarterly: từ **quy trình 10 tháng bản 2026** — lớp mới không có trong legacy.
- Block "Khó khăn - Giải pháp" + nhịp report: từ **Mẫu template report tuần PSP** — review tháng đứng trên nền report tuần, không thay thế.
