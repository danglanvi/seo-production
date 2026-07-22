---
type: sop
tier: planning
phase: project-management
last_updated: 2026-07-19
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/1. Kick off - hoạch định & quản lý dự án/Hoạch định KPI & OKRs Template mẫu cho dự án.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/1. Kick off - hoạch định & quản lý dự án/Quy trình KPI - OKRs Project - Update 09_2020.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/1. Kick off - hoạch định & quản lý dự án/Kick off dự án/2. file mẫu kick off - review & hoạch định KPI và OKRs.xlsx
  - sop/09-project-timeline/10-thang-thuc-day.md
skills_routed:
  - okrs-gtv-tag-framework
  - traffic-plan
items_count: 22 (P0 gate: 5)
tags: [sop, self-checklist, kpi, okrs, planning, kickoff, quality-gate]
---

# Self-Checklist: Hoạch định KPI & OKRs (SEO Lead)

> **Khi dùng:** SEO Lead Project tự check khi **LẬP** KPI & OKRs — đầu dự án (T1, công đoạn 1 + 8 của quy trình 10 tháng) và đầu mỗi quý (OKRs quý T3 / T6 / review T9).
> **Gate:** Chưa pass đủ **P0 (5 items)** → KHÔNG trình duyệt SEO Director, KHÔNG kick-off với khách.
> **Số items:** 22 (KO-01 → KO-22) = 4 Input + 5 KPI + 5 OKRs + 4 Sai lầm phổ biến + 4 Gate duyệt.
> **Scoring:** Self Score /22 → Self %.

## Ranh giới với `monthly-project-review.md`

| | Checklist này (PLANNING) | [[sop/06-self-checklist/monthly-project-review]] (REVIEW) |
|---|---|---|
| **Khi nào** | Đầu dự án (T1) + đầu quý (T3/T6/T9) | Hằng tháng, trước khi trình Manager/Director |
| **Câu hỏi** | KPI/OKRs được **lập đúng** chưa? | KPI/OKRs đang **đạt** không? |
| **Output** | Bộ KPI + OKRs ở trạng thái CHỜ DUYỆT | Report review tháng + điều chỉnh |

Framework OKRs (định nghĩa O/KR, SMART, cascade, scoring 0.0-1.0, 4 pillars, common mistakes) là **canonical ở skill `okrs-gtv-tag-framework`** — checklist này KHÔNG chép lại framework, chỉ gate việc áp dụng nó cho dự án SEO. Plan traffic chi tiết là **canonical ở skill `traffic-plan`** — T1 không làm việc đó (xem KO-14).

---

## Nhóm 1 — Input đủ trước khi lập

### KO-01 🔴 P0 — KPI cam kết hợp đồng đã trích xuất đầy đủ
Toàn bộ chỉ tiêu ràng buộc trong hợp đồng (bộ keyword cam kết + mốc top theo tháng, traffic cam kết + nguồn đo GA hay Ahrefs, PR/backlink nếu có) đã được trích ra file chuẩn — trong SEO Production instance là `00-client-context/kpi-commitments.md`. Không lập KPI từ trí nhớ hoặc từ bản proposal chưa ký.
- ✅ Có bảng KPI cam kết theo tháng, ghi rõ nguồn đo ("nếu cam kết traffic bằng Ahrefs thì báo cáo bằng Ahrefs" — file kick off mẫu, công đoạn 1.3-1.4).
- ❌ Chỉ có con số tổng "17.000 traffic" mà không rõ tháng nào, đo bằng gì.
- Nguồn: file kick off mẫu — sheet "Kick off dự án" mục 1 (Mô tả dự án: ngân sách, mục tiêu top, traffic, yêu cầu khác) — **GIỮ**.

### KO-02 — Baseline hiện trạng đã đo
Trước khi đặt mục tiêu phải có số nền: ranking hiện tại của bộ keyword cam kết (top 3/5/10/30/100), organic traffic hiện tại, tình trạng index/technical nổi cộm. Template Geyser có riêng khối "HIỆN TẠI" đặt cạnh "KPI TRONG HỢP ĐỒNG" — không có baseline thì không audit được thiếu/đủ về sau.
- ✅ Bảng baseline cùng cấu trúc hàng-cột với bảng KPI cam kết để đối chiếu 1-1.
- Nguồn: Hoạch định KPI & OKRs Template — sheet "3. mẫu template Geyser" khối HIỆN TẠI + sheet "3.1 Geyser audit KPI" (cột Hiện tại / Thiếu / Thực tế) — **GIỮ**. Principle "Ignoring baseline" trong `okrs-gtv-tag-framework` (Common Mistakes 7).

### KO-03 — Phân tích hợp đồng & thẩm định dự án đã pass
Công đoạn "Lấy thông tin và phân tích hợp đồng" (công đoạn 1, T1 ngày 1-7) đã xong: đọc kỹ lưu ý từ Account/trưởng phòng, yêu cầu đặc biệt của khách (topic ưu tiên, penalty GMB, website mới/redirect…) đã ghi nhận — vì các yêu cầu này đổi thẳng cấu trúc KPI (vd: web bị phạt → timeline dài hơn, xem sheet Checklist 12/10/8/6 tháng).
- Nguồn: Quy trình KPI-OKRs 09/2020 — sheet "Overview Process" dòng 1 + sheet "Checklist" (khung 6/8/10/12 tháng theo loại cam kết) — **SỬA**: cập nhật theo timeline 10 tháng rev 2 ở [[sop/09-project-timeline/10-thang-thuc-day]]; phân tích hợp đồng phía Account route skill `acc-kickoff-setup`.

### KO-04 — Nguồn lực & ban dự án xác nhận
RACI đã chốt: ai làm SEO, ai làm Content, ai review (accountable), ai cần inform; ngân sách content/kỹ thuật đã tách. KPI đặt cho đội hình chưa tồn tại = KPI ảo.
- Nguồn: file kick off mẫu — mục 1.5 "Ban tổ chức dự án theo RACI" + ngân sách mục 1.1 — **GIỮ**.

---

## Nhóm 2 — Lập KPI dự án

### KO-05 🔴 P0 — KPI ràng buộc hợp đồng vs KPI vận hành nội bộ tách rõ
Hai bảng riêng, không trộn: (a) KPI cam kết khách hàng — copy đúng timeline hợp đồng để đối chiếu; (b) KPI nội bộ — lập để đảm bảo milestones, thông thường **cao hơn KPI khách ~20% mỗi tháng**. Trường hợp hợp đồng có nhiều bộ keyword cam kết khác nhau → lập file KPI nội bộ tương ứng cho từng bộ (như dự án Geyser: Brand / NaNo / Blog tách riêng).
- ✅ 2 bảng cùng format; KPI nội bộ ≥ KPI khách +20%; mỗi bộ keyword cam kết có ladder riêng.
- Nguồn: Hoạch định KPI & OKRs Template — sheet KPI, lưu ý 1, 2, 4, 7 — **GIỮ** (đây là luật gốc rõ nhất của file legacy).

### KO-06 — KPI theo pha: không cam kết kết quả cuối ở T1-T3
Đường KPI phải tôn trọng vật lý của SEO: content cần **~100 ngày mature** → T1-T2 gần như 0% kết quả, kết quả thật dồn về nửa sau. Mẫu 10 tháng legacy: traffic 0% / 0% / 5% / 10% / 20% / 35% / 55% / 65% / 80% / 100%. KPI tuyến tính đều từ T1 = sai và tự đặt bẫy cho review tháng.
- ✅ Curve ramp chậm 3 tháng đầu, dốc từ T4-T5; khớp ma trận content type × timeline.
- Nguồn: Quy trình KPI-OKRs 09/2020 — sheet "Timeline Project" (mẫu 8/10/12 tháng) — **GIỮ**, đối chiếu [[sop/09-project-timeline/10-thang-thuc-day]] (content mature ~100 ngày).

### KO-07 — Ladder top có bậc đệm hợp lệ
Quy tắc legacy: khi hoạch định top 5 hay top 3, mốc top 10 phải **đi trước và cao hơn 5-10%** so với mốc top 5 của tháng sau (tương tự top 3 sau top 5). Kèm bậc trung gian top 100 → 30 → 20 → 10 → 5 → 3 để thấy phễu di chuyển.
- ✅ Ví dụ chuẩn legacy: T4 top 10 = 10% → T5 mới cam kết top 5 ở mức 5%; top 3 để qua T6.
- Nguồn: Quy trình KPI-OKRs 09/2020 — sheet "Timeline Project" note lặp 3 lần ở cả 3 mẫu — **GIỮ**.

### KO-08 — Leading vs lagging indicators tách rõ
Ngoài KPI kết quả (top, traffic — lagging), bảng KPI nội bộ phải có chỉ số dẫn dắt (leading) theo dõi được sớm: tiến độ content xuất bản theo cửa sổ (keywords research/outline → content → onpage → backlink theo % từng tháng như mẫu Timeline Project), index coverage, keywords top 30-100 (phễu kế cận). Tư duy GTV 2026: "process drives results" — kết quả là lagging indicator của hệ thống.
- Nguồn: Quy trình KPI-OKRs 09/2020 — sheet "Timeline Project" (4 dòng công việc % theo tháng) — **SỬA**: gọi tên tường minh leading/lagging (legacy có data nhưng chưa có khái niệm); align GTV Philosophy trong `okrs-gtv-tag-framework`.

### KO-09 — Chỉ số theo dõi ngoài phạm vi KPI đã ghi chú
Organic traffic ngành (không thuộc KPI nhưng cần theo dõi vì ảnh hưởng ranking một số ngành), seasonal của ngành, và các chỉ số khách quan tâm nhưng không cam kết — ghi vào mục "theo dõi", KHÔNG đưa vào bảng cam kết.
- Nguồn: Hoạch định KPI & OKRs Template — sheet KPI, lưu ý 6 (Organic Traffic Ngành) — **GIỮ**.

---

## Nhóm 3 — Lập OKRs

### KO-10 🔴 P0 — Đúng format framework — route `okrs-gtv-tag-framework`
OKRs viết theo skill `okrs-gtv-tag-framework` (canonical): công thức Objective, KR SMART, scoring 0.0-1.0, 4 pillars SEO project (Technical / Content / Onpage / Offsite), cấu trúc 3 tầng O → KR → Tasks. Checklist này không định nghĩa lại — chỉ xác nhận đã chạy skill và output khớp.
- ✅ Đã trả lời đủ 8 Quick Validation Questions của skill trước khi trình.
- Nguồn: **MỚI** (route skill; legacy chưa có framework thống nhất — 2 template insieutoc/Ifree mỗi cái một format).

### KO-11 — O truyền cảm hứng, KR đo được
Mỗi Objective là đích chiến lược quý trả lời "muốn đạt gì" (qualitative, có thời hạn); mỗi KR có **con số + deadline + người đảm nhận**. KR dạng outcome ưu tiên hơn output; ngoại lệ GTV: KR được phép là task cụ thể nếu đóng góp trực tiếp vào O và verify được done/not-done (đúng tinh thần template Ifree: "Hoàn thành 100% Audit Edit entity onsite + offsite, deadline 20/5, PIC Phong + Trang").
- ❌ KR kiểu "Cải thiện content" — không số, không deadline, không PIC.
- Nguồn: template "4.1 Mẫu OKR - Ifree" (được legacy đánh giá "chuẩn nhất") — **GIỮ**, đối chiếu Outcome vs Output trong `okrs-gtv-tag-framework`.

### KO-12 — KR không phải task list; OKRs ≠ plan triển khai
Luật legacy ghi thẳng: "OKRs sinh ra để có góc nhìn tổng quan — điều gì cần đạt qua những hạng mục chính nào. **Khác với plan triển khai** là liệt kê task tương ứng." Task chi tiết nằm ở cột "Công việc chi tiết"/Wework, không nằm ở cấp KR. Nếu 1 O có hơn 5 KR → gom ý, nén lại.
- ✅ Mỗi O ≤ 5 KR; đọc riêng cột KR vẫn hiểu được quý này dự án cần đạt gì.
- Nguồn: Hoạch định KPI & OKRs Template — sheet OKRs, lưu ý 1 + 2 — **GIỮ**.

### KO-13 — Số lượng & phạm vi: ~3 Objective/quý, lập chung SEO + Content, khớp timeline
Mỗi quý dự án thường 3 Objective chính, không quá 5. OKRs cover cả content lẫn SEO — team SEO chịu trách nhiệm chính nhưng **lập chung với team content**. OKRs phải khớp timeline công đoạn của quy trình 10 tháng (không đặt KR offpage rầm rộ ở quý 1 khi timeline để offpage ở P4). Nếu công ty đang chạy OKRs công ty/phòng ban và dự án cần align → ghi "Link OKRs: O_ KR_" theo luật cascade của skill.
- Nguồn: Hoạch định KPI & OKRs Template — sheet OKRs, lưu ý 3, 4, 5, 6 — **GIỮ**; cascade là **MỚI** từ `okrs-gtv-tag-framework` (áp dụng nếu có).

### KO-14 🔴 P0 — CẤM cam kết/hoạch định traffic chi tiết ở T1 khi chưa có plan traffic
Quy trình 10 tháng rev 2 ghi rõ ở công đoạn Chiến lược + OKRs & KPI (T1): "**T1 KHÔNG research traffic ≥ cam kết nữa**". Plan traffic chi tiết thuộc: (a) công đoạn Research content Outer Section — T2 (initial traffic, historical data sớm); (b) công đoạn **Plan content traffic FULL — T3 → giữa T4**, chuẩn đạt **≥ cam kết traffic +20%**, duyệt bởi SEO Director. Ở T1, KPI traffic chỉ copy đúng cam kết hợp đồng theo curve (KO-06) — mọi hoạch định topic-level để đạt traffic → route skill `traffic-plan`.
- ❌ T1 đã hứa với khách phân bổ traffic per topic/URL trong khi topical map còn là demo.
- Nguồn: **MỚI** (rev 2 05/07/2026) — [[sop/09-project-timeline/10-thang-thuc-day]] T1 + T2 + T3; **SỬA** so với legacy (Overview Process 2020 dồn hết vào "công đoạn 6 ngày 8-14").

---

## Nhóm 4 — Sai lầm phổ biến (chắt lọc từ file legacy)

### KO-15 — Không có backup plan cho thứ tự topic
Chiến lược T1 phải có "thứ tự triển khai topic + **backup**" — topic chính không ăn thì đánh topic nào thay. Bài học Geyser: nhiều bộ cam kết chạy song song, bộ Blog hụt sâu (-101.8 keyword top 5 tại mốc audit) trong khi bộ Brand gần đạt — không có backup/tái phân bổ thì cả dự án chết theo bộ yếu nhất.
- ✅ Mỗi nhóm KPI có phương án B ghi sẵn (bộ keyword thay thế, topic bổ sung, đòn bẩy kéo lại).
- Nguồn: sheet "3.1 Geyser audit KPI" (khoảng cách Kế hoạch vs Hiện tại) + [[sop/09-project-timeline/10-thang-thuc-day]] T1 ("Thứ tự triển khai topic + backup") — **GIỮ + SỬA** (legacy chỉ audit hậu quả, checklist đưa backup thành điều kiện lúc lập).

### KO-16 — OKR viết thành danh sách việc không có đích
Anti-pattern thấy ngay trong template insieutoc legacy: "Mục tiêu: Nâng cấp giao diện", "Mục tiêu: Tăng trust cho URL" — thực chất là nhóm task, không phải Objective; đích ranking bị nhét vào ô ghi chú. Test: đọc O mà không đọc KR — có biết quý này dự án PHẢI ĐẠT gì không? Không → viết lại theo KO-10/KO-12.
- Nguồn: sheet "4. Mẫu template OKR - insieutoc" — **SỬA** (giữ làm ví dụ phản diện; format chuẩn theo Ifree + skill).

### KO-17 — KR không có số / không có baseline so sánh
Mọi KR phải trả lời được "từ bao nhiêu → lên bao nhiêu, trước ngày nào". "Hoàn thành review GMB và tối ưu (nếu có)" — chữ "(nếu có)" làm KR không thể chấm điểm. KR số lượng content phải kèm mẫu số (45/55 bài) như cách legacy track "done 80% (45/55)".
- Nguồn: file kick off mẫu — sheet "KPI & OKRs Qúy 1" (cột Tình trạng có % và phân số) — **GIỮ**; đối chiếu Common Mistakes 2, 7 trong `okrs-gtv-tag-framework`.

### KO-18 — Cơ chế tracking tiến độ OKRs theo tháng được set up ngay lúc lập
Luật legacy: "Hằng tháng tự review dự án và tổng kết ở mục Tiến độ OKRs theo tháng — điền % + comment tình trạng." Lúc lập OKRs phải dựng sẵn cột tiến độ tháng 1/2/3 — không có chỗ ghi thì sẽ không ghi. Việc CHẤM tiến độ hằng tháng thuộc [[sop/06-self-checklist/monthly-project-review]] (MR-07), không thuộc checklist này.
- Nguồn: Hoạch định KPI & OKRs Template — sheet OKRs, lưu ý 7 + cột "Tiến độ OKRs theo tháng" — **GIỮ**.

---

## Nhóm 5 — Gate duyệt

### KO-19 🔴 P0 — SEO Director duyệt chiến lược + OKRs/KPI dự án
Công đoạn 8 của quy trình 10 tháng: Chiến lược + OKRs & KPI do SEO + Content lập, người duyệt là **SEO Director** (không phải SEO Lead tự duyệt). OKRs quý T3/T6 và review T9 cũng duyệt bởi SEO Director. Chưa có chữ ký duyệt → bộ KPI/OKRs chưa có hiệu lực với khách lẫn nội bộ.
- Nguồn: **SỬA** — [[sop/09-project-timeline/10-thang-thuc-day]] T1/T3/T6/T9 cột Duyệt (legacy 2020 chỉ ghi "SEO & Content", chưa có tầng duyệt Director).

### KO-20 — Trạng thái CHỜ DUYỆT ghi tường minh
Bộ KPI + OKRs trình đi phải đóng dấu trạng thái: `CHỜ DUYỆT — [ngày trình] — [người duyệt: SEO Director]`. Sau duyệt mới chuyển `ĐÃ DUYỆT` và mới được dùng trong kick-off với khách / nhập Wework. Tránh tình trạng legacy: file lập xong dùng luôn, không ai biết bản nào là bản chốt.
- Nguồn: **MỚI** (chuẩn hóa từ execution rule "show plan → approve → execute" của wiki; legacy có bước "Thống nhất trên wework sau buổi họp" — file kick off mục 9 — nhưng thiếu trạng thái).

### KO-21 — Lịch OKRs quý + review T6 đã đặt trên calendar
Ngay khi OKRs T1 được duyệt, đặt luôn 4 mốc: **lập OKRs quý 2 tại T3, quý 3 tại T6, review OKRs tại T9**, và **review nền tảng T6 bắt buộc với Manager/Director** (chất lượng T1-T6). Legacy 2020 để "ngày 88-100" cuối quý mới lo lập OKRs quý sau → thường trễ; đặt lịch từ đầu là cách duy nhất giữ nhịp.
- Nguồn: Quy trình KPI-OKRs 09/2020 — Overview Process dòng 25/42 (Lên OKRs quý sau, ngày 88-100) — **SỬA** theo nhịp [[sop/09-project-timeline/10-thang-thuc-day]] (OKRs: lập T1 → T3 → T6 → review T9; Review T6 với Manager/Director).

### KO-22 — Meeting thống nhất + điều chỉnh OKRs sau audit T1 đã lên lịch
Sau khi audit tổng thể + audit content T1 có data, phải có meeting thống nhất thứ tự ưu tiên và **điều chỉnh OKRs nếu có** (legacy: công đoạn 10, ngày 25-30, SEO - Content - trưởng phòng). OKRs lập ngày 8-14 dựa trên phân tích sơ bộ — data audit về sau được phép sửa OKRs, nhưng phải sửa qua meeting + duyệt lại, không sửa ngầm.
- Nguồn: Quy trình KPI-OKRs 09/2020 — Overview Process dòng 11 (công đoạn 10) — **GIỮ**.

---

## P0 Gate — 5 items chặn trình duyệt

| ID | Tóm tắt | Vì sao chặn |
|---|---|---|
| KO-01 | KPI cam kết hợp đồng đã trích đúng | Lập KPI sai nguồn = sai cả dây chuyền review 10 tháng |
| KO-05 | Tách KPI hợp đồng vs nội bộ (+20%) | Trộn 2 bảng = mất khả năng đối chiếu và mất buffer |
| KO-10 | Đúng format `okrs-gtv-tag-framework` | Sai format = không chấm điểm được, không cascade được |
| KO-14 | Không cam kết traffic chi tiết ở T1 | Vi phạm quy trình rev 2; hứa khi chưa có plan = rủi ro hợp đồng |
| KO-19 | SEO Director duyệt | Chưa duyệt = chưa có hiệu lực |

## Quy trình dùng nhanh

1. Xong công đoạn phân tích hợp đồng + phân tích thị trường T1 → chạy Nhóm 1.
2. Lập KPI (Nhóm 2) → lập OKRs qua skill `okrs-gtv-tag-framework` (Nhóm 3) → tự soi Nhóm 4.
3. Đóng trạng thái CHỜ DUYỆT → trình SEO Director (Nhóm 5) → duyệt xong mới kick-off khách.
4. Đầu quý T3/T6/T9: chạy lại checklist này cho OKRs quý mới (Nhóm 1 rút gọn: baseline = data review tháng gần nhất).
