---
type: sop
tier: planning
phase: project-intake
last_updated: 2026-07-19
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/2. Thẩm định dự án/Thẩm định dự án.xlsx
  - sop/09-project-timeline/10-thang-thuc-day.md
related_wiki:
  - "[[sources/gtv-tu-van-tham-dinh-vanhoa]]"
skills_routed:
  - gtv-proposal
  - acc-kickoff-setup
  - backlink-research
items_count: 14 (P0 gate: 6) + 6 red-flags
tags: [sop, self-checklist, project-intake, tham-dinh, go-no-go, planning, quality-gate]
---

# Self-Checklist: Project Intake — Thẩm định dự án TRƯỚC khi nhận

> **Khi dùng:** Account + SEO (Lead/Manager) chạy **TRƯỚC khi ký hợp đồng** — ngay khi có lead nghiêm túc, trước khi `gtv-proposal` cam kết bất kỳ con số nào. Modernize từ quy trình thẩm định 10 bước PSP (2020-2022).
> **Vị trí trong chuỗi:** `checklist này (go/no-go)` → ký hợp đồng → `acc-kickoff-setup` (T1) → `checklist-kpi-okrs-planning.md` (KO-01…KO-22). KO-03 giả định checklist này đã pass.
> **Gate:** Fail bất kỳ item **P0 (6 items)** → KHÔNG gửi proposal có cam kết số. Dính bất kỳ **Red-flag** nào không có ngoại lệ thỏa mãn → TỪ CHỐI dự án hoặc đổi cấu trúc deal (không cam kết KPI).
> **Số items:** 14 (PI-01 → PI-14) = 2 Khách & ngành + 5 Thị trường & website + 3 Kỳ vọng & cam kết + 2 Nguồn lực & phối hợp + 2 Gate quyết định. Kèm section Red-flags riêng (RF-01 → RF-06).
> **Scoring:** Self Score /14 → Self %. Review: Account/SEO Lead tự check 100% → Manager verify → **Director duyệt quyết định nhận/từ chối** (PI-14).

---

## Nhóm 1 — Khách hàng & ngành

### PI-01 — Mục tiêu doanh nghiệp của khách rõ ràng
Bước 2 quy trình thẩm định legacy: định hướng kinh doanh, mục tiêu thật đằng sau SEO (lead? doanh thu? brand?), bộ keyword khách muốn, số lượng website/domain khách đang có (nhiều domain cùng ngành = rủi ro cannibalization/PBN tự phát). Khách không nói được mục tiêu kinh doanh → mọi cam kết phía sau đều là đoán.
- ✅ Ghi được 1 đoạn "khách cần SEO để đạt [mục tiêu kinh doanh X] đo bằng [Y]" mà khách xác nhận đúng.
- Nguồn: Thẩm định dự án.xlsx bước 1-2 — **GIỮ**.

### PI-02 🔴 P0 — Thẩm định ngành & pháp lý của khách
Phân loại site (Ecommerce / Dịch vụ / Thông tin / Tin tức / **YMYL** / Portfolio — bước 6 legacy) và rà lớp pháp lý bằng [[sop/06-self-checklist/checklist-phap-ly-content-website]] ở mức intake: ngành có điều kiện (dược, TPCN, tài chính, y tế) → sản phẩm có đủ chứng chỉ/công bố không; ngành có nội dung quảng cáo bị giới hạn → scope content bị bó thế nào; hàng hóa có nhóm cấm/giới hạn không (PL-14). Kết luận ảnh hưởng trực tiếp: nhận hay không (RF-02), bật Tier 2 YMYL, timeline và mức cam kết.
- ✅ Có 3 dòng kết luận: loại site + ràng buộc pháp lý chính + ảnh hưởng lên scope/cam kết.
- ❌ Nhận dự án TPCN rồi T1 mới phát hiện sản phẩm chưa có công bố chất lượng → lỗi thẩm định, không phải lỗi vận hành.
- Nguồn: Thẩm định dự án.xlsx bước 6 — **GIỮ + NÂNG** (legacy chỉ phân loại site, chưa có lớp pháp lý; nâng theo docx pháp lý 11/2025).

---

## Nhóm 2 — Thẩm định thị trường & website

### PI-03 — Bộ keyword cam kết theo form chuẩn
Bộ keyword dự kiến cam kết lập theo form legacy: STT · keyword · volume/tháng · KD · CPC · parent keyword. Đây là input cho PI-08/PI-09 — không có bộ keyword định lượng thì "cam kết top" là cam kết mồm.
- Nguồn: Thẩm định dự án.xlsx bước 4 — **GIỮ**.

### PI-04 — Phân tích 5-10 đối thủ trực tiếp
Theo form legacy có refresh 2026: DR, referring domains, organic keywords, organic traffic, top pages + **nhận xét định tính từng đối thủ**. Refresh: bỏ TF/CF (Majestic — không còn trong stack), thêm 2 cột thời đại mới: topical coverage (đối thủ có Topical Map bài bản không) và AI search visibility (có được AI Overviews/ChatGPT cite không). Data qua skill `backlink-research` + `seo-research`.
- ✅ ≥5 đối thủ trực tiếp cùng ngành-cùng thị trường (không lấy site quốc tế làm chuẩn cho deal VN); mỗi đối thủ có 1-2 câu nhận xét định tính.
- Nguồn: Thẩm định dự án.xlsx bước 5 (sheet Mẫu phân tích đối thủ) — **GIỮ + SỬA** (bỏ TF/CF, thêm tiêu chí semantic/AI — theo Open Questions của source page).

### PI-05 — Đánh giá độ cạnh tranh thị trường
Kết luận độ cạnh tranh (thấp / trung bình / cao; đối thủ lớn hay nhỏ) từ data PI-04, đối chiếu loại site PI-02. Độ cạnh tranh là biến số quyết định tỉ lệ % cam kết ở PI-08 — không được kết luận "làm được" chỉ vì muốn có deal.
- Nguồn: Thẩm định dự án.xlsx bước 6 — **GIỮ**.

### PI-06 🔴 P0 — Lịch sử domain: penalty, PBN cũ, mã độc
Item legacy KHÔNG có tường minh — bổ sung bắt buộc từ bài học vận hành: (1) **Manual action / penalty**: xin quyền GSC xem mục Manual Actions + Security Issues; chưa có access thì check gián tiếp (site: index bất thường, brand SERP sạch không); (2) **Lịch sử backlink bẩn/PBN cũ**: profile backlink qua `backlink-research` — anchor spam, refdomains rác, dấu vết mua link/textlink cũ, redirect từ domain lạ về; (3) **Mã độc/hack cũ**: Security Issues + quét index tìm URL lạ (tiếng Nhật/casino…), lịch sử Wayback Machine; (4) **Lai lịch domain**: tuổi domain, domain từng đổi chủ/đổi ngành, từng là site khác hoàn toàn. Site có tiền sử → timeline phải dài hơn và có phase khắc phục (legacy Checklist 12/10/8/6 tháng đã thừa nhận nguyên tắc này; nay có `checklist-khoi-phuc-seo-ranking.md` làm phase riêng).
- ✅ Báo cáo lịch sử domain 1 trang: 4 mục trên + kết luận "sạch / có tiền sử cần khắc phục / RF-01".
- ❌ Ký cam kết top trên domain đang gánh manual action chưa gỡ → RF-01, không phải chỉnh timeline.
- Nguồn: **MỚI** (legacy bước 7 chỉ xem tuổi domain + thực trạng keyword/traffic) — chuẩn hóa từ kinh nghiệm vận hành + hệ runbook sự cố 07/2026.

### PI-07 — Thực trạng website vs đối thủ
Bước 7 legacy: organic keywords + organic traffic hiện tại của site khách đặt cạnh trung bình đối thủ PI-04; khoảng cách (gap DR, gap content, gap topical coverage) lượng hóa được. Đây là "HIỆN TẠI" mà mọi cam kết phải xuất phát từ đó — cùng logic baseline với KO-02 nhưng ở mức deal.
- Nguồn: Thẩm định dự án.xlsx bước 7 — **GIỮ**.

---

## Nhóm 3 — Kỳ vọng & cam kết khả thi

### PI-08 🔴 P0 — Cam kết SUY RA từ data thẩm định, không đặt trước
Luật gốc của file legacy (bước 8): tỉ lệ % Top 3/5/10 đề xuất dựa trên đánh giá thị trường (PI-05) và thực trạng site (PI-07); % traffic dựa trên bộ keyword cam kết (PI-03) + đối thủ (PI-04). Chiều đúng: **data → cam kết**. Chiều sai: khách muốn số X → đi tìm lý lẽ đỡ số X.
- ✅ Mỗi con số trong proposal trace ngược được về bước thẩm định nào; kịch bản conservative/expected ghi rõ.
- ❌ "Khách chỉ ký nếu cam kết top 3 trong 4 tháng" và mình gật để lấy deal → fail P0 + xem RF-03.
- Nguồn: Thẩm định dự án.xlsx bước 8 — **GIỮ** (logic ngầm quan trọng nhất của file).

### PI-09 🔴 P0 — Test khả thi theo chuẩn "plan traffic ≥ cam kết +20%"
Chuẩn quy trình 10 tháng hiện hành: plan content traffic FULL (T3 → giữa T4) phải đạt **≥ cam kết traffic +20%**, duyệt bởi SEO Director; KPI nội bộ cũng chạy cao hơn KPI khách ~20% (KO-05). Suy ngược về intake: ngay lúc thẩm định phải ước lượng thô — tổng volume khả dụng của topic space × CTR kỳ vọng có tạo nổi đường traffic ≥ cam kết dự kiến +20% trong 10 tháng không. Nếu ước lượng lạc quan nhất vẫn không tới +20% → hạ cam kết hoặc từ chối, KHÔNG để đội vận hành gánh con số không có cửa.
- ✅ Bảng ước lượng thô: topic space chính, volume tổng, giả định CTR/position, đường ramp 10 tháng (0/0/5/10/20/35/55/65/80/100% theo mẫu legacy) so với số cam kết dự kiến.
- Nguồn: **MỚI** — [[sop/09-project-timeline/10-thang-thuc-day]] (chuẩn +20%, Director duyệt) chiếu ngược về intake; legacy bước 8 mới có nguyên tắc, chưa có ngưỡng số.

### PI-10 — Timeline chào khách theo mẫu lộ trình, ramp chậm 3 tháng đầu
Timeline trong proposal theo mẫu legacy (traffic/keyword/content/backlink/ngân sách theo 10 tháng; ưu tiên: Audit + nền tảng → thúc đẩy backlink → tối ưu), tôn trọng vật lý SEO: content mature ~100 ngày → không hứa kết quả T1-T3 (khớp KO-06). Kỳ vọng khách về "tháng đầu có gì" phải được chỉnh ngay từ intake — sau này chỉnh đắt hơn nhiều.
- Nguồn: Thẩm định dự án.xlsx bước 9 (sheet Mẫu Timeline) — **GIỮ**, đối chiếu [[sop/09-project-timeline/10-thang-thuc-day]].

---

## Nhóm 4 — Nguồn lực & văn hóa phối hợp của khách

### PI-11 🔴 P0 — Nguồn lực khách đủ gánh phần việc phía họ
Bước 3 legacy: ngân sách chi trả (đủ cho scope + content + kỹ thuật trong 10 tháng, không phải 3 tháng đầu rồi đứt) + đội ngũ nội bộ: ai viết/duyệt content phía khách, có dev/coder xử lý technical không (chuẩn red-flag vận hành: coder treo việc >2 tuần là cờ đỏ ở `acc-weekly-sync`), design, marketing. SEO agency không thay được nghĩa vụ phía khách — khách không có nguồn lực thì KPI đẹp mấy cũng vỡ.
- ✅ Bảng RACI thô phía khách: content/dev/design/budget — mỗi dòng có người thật, không phải "bên em sẽ thu xếp".
- Nguồn: Thẩm định dự án.xlsx bước 3 — **GIỮ**.

### PI-12 — Văn hóa & quy trình phối hợp
Thẩm định mềm nhưng quyết định trải nghiệm 10 tháng: (1) người quyết định cuối phía khách là AI — một đầu mối hay hội đồng 5 người ý kiến vòng lặp; (2) SLA duyệt content khách chấp nhận được không (vượt SLA 2 lần là red-flag vận hành); (3) khách sẵn sàng cấp access GSC/GA/CMS/hosting không (từ chối cấp access để thẩm định → RF-06); (4) lịch sử làm việc với agency trước — hỏi thẳng đã qua mấy agency, vì sao dừng; (5) kênh liên lạc + nhịp họp thống nhất được không.
- ✅ Ghi nhận 5 điểm trên vào hồ sơ thẩm định; điểm nào đáng ngại → đưa vào điều khoản hợp đồng (SLA, phạt chậm duyệt) thay vì hy vọng.
- Nguồn: **MỚI** — chuẩn hóa từ tài liệu training Account (red-flags mục 06) + văn hóa review PSP; legacy thẩm định chưa có lớp văn hóa.

---

## Nhóm 5 — Gate quyết định

### PI-13 — Review hợp đồng trước khi ký
Bước 10 legacy: rà điều khoản KPI cam kết (đo bằng gì — GA hay Ahrefs, tính tại thời điểm nào), điều khoản phạt/hoàn tiền, scope (bao nhiêu bài, ai viết, technical ai làm), điều kiện phía khách (SLA duyệt, cấp access), điều khoản thoát cho cả 2 bên, và điều khoản tactic (dự án có yêu cầu tactic rủi ro như traffic users → phải có văn bản gate như `tier-1-traffic-users.md` quy định). Hợp đồng ký xong là input cho KO-01 — sai từ hợp đồng thì cả dây chuyền 10 tháng sai theo.
- Nguồn: Thẩm định dự án.xlsx bước 10 — **GIỮ**.

### PI-14 🔴 P0 — Quyết định go/no-go có Director duyệt + lưu hồ sơ
Quyết định nhận/không nhận (hoặc nhận với cấu trúc deal khác: không cam kết KPI, chỉ retainer/consulting) do **Director duyệt** — người thẩm định không tự quyết deal mình sẽ chạy. Hồ sơ thẩm định (PI-01 → PI-13 + kết luận red-flags) lưu lại kể cả khi từ chối — data từ chối là tài sản: lần sau khách quay lại hoặc gặp deal cùng ngành có sẵn baseline.
- ✅ 1 trang quyết định: nhận/từ chối/nhận-có-điều-kiện + chữ ký Director + ngày; nếu nhận-có-điều-kiện thì điều kiện phải nằm trong hợp đồng (PI-13).
- Nguồn: **MỚI** — đồng bộ tầng duyệt Director của hệ hiện hành (KO-19, plan traffic Director duyệt); legacy chưa ghi người duyệt.

---

## Red-flags TỪ CHỐI dự án

> Game-changer của intake: biết **không nhận** deal nào quan trọng hơn biết nhận deal nào. Dính red-flag mà không thỏa ngoại lệ → từ chối hoặc đổi cấu trúc deal (bỏ cam kết KPI). Quyết định cuối cùng: Director (PI-14).

| ID | Red-flag | Vì sao từ chối | Ngoại lệ có điều kiện |
|---|---|---|---|
| RF-01 | Domain đang manual action chưa gỡ / lịch sử PBN-link bẩn dày đặc / mã độc tái đi tái lại | Cam kết KPI trên nền phạt = cầm chắc vỡ; chi phí khắc phục ăn hết timeline | Nhận dạng dự án KHẮC PHỤC riêng (scope = `checklist-xu-ly-ma-doc` + `checklist-khoi-phuc-seo-ranking`), KHÔNG cam kết top/traffic; hoặc SEO trên domain mới |
| RF-02 | Ngành/sản phẩm vi phạm pháp lý: hàng cấm, hàng giả/nhái, TPCN không công bố, thuốc-mỹ phẩm không chứng chỉ, tài chính không phép | Rủi ro pháp lý liên đới cho chính GTV (PL-14, trách nhiệm liên đới Luật QC 2025); không có content hợp pháp nào để viết | Khách hoàn tất chứng chỉ/công bố TRƯỚC khi ký — có bằng chứng, không phải lời hứa |
| RF-03 | Kỳ vọng phi thực tế và KHÔNG chịu điều chỉnh (top 3 keyword đầu ngành trong 3-4 tháng; không chấp nhận ramp 10 tháng; đòi cam kết vượt kết quả test PI-09) | Vi phạm PI-08/PI-09 từ ngày 0; deal chỉ có thể kết thúc bằng tranh chấp | Khách chấp nhận kịch bản data-driven sau khi được educate — xác nhận bằng văn bản trong hợp đồng, không phải gật đầu miệng |
| RF-04 | Không có nguồn lực tối thiểu: budget không đủ 10 tháng, không người duyệt content, không dev, muốn "khoán trắng" cả nghĩa vụ phía khách | Fail PI-11 — KPI phụ thuộc phần việc khách không ai gánh | GTV nhận thêm scope thay khách (content full, technical full) và deal được reprice tương ứng |
| RF-05 | Văn hóa phối hợp độc hại: đã qua ≥3 agency và đổ lỗi toàn bộ cho agency cũ; đòi can thiệp từng bài vô nguyên tắc; tiền sử trả chậm; ép tactic rủi ro (mua link bẩn, traffic users) bất chấp gate | Deal ngốn chi phí quản lý vượt lợi nhuận; ép tactic rủi ro đặt đội ngũ vào thế vi phạm quy trình gate | Có bằng chứng nguyên nhân đứt gãy cũ nằm ở agency trước (data thật); tactic rủi ro chỉ khi khách ký nhận rủi ro theo đúng cơ chế gate hiện hành |
| RF-06 | Không cho access data để thẩm định (GSC/GA/backlink) nhưng vẫn đòi cam kết số | Không data = không thẩm định được PI-06/PI-07 = mọi con số là đoán | Cam kết chỉ đưa SAU khi có access (cấu trúc 2 bước: phí audit/thẩm định trước, proposal cam kết sau) |

---

## P0 Gate — 6 items chặn gửi proposal cam kết

| ID | Tóm tắt | Vì sao chặn |
|---|---|---|
| PI-02 | Ngành & pháp lý khách đã thẩm định | Nhận nhầm ngành rủi ro = rủi ro liên đới cho chính GTV |
| PI-06 | Lịch sử domain sạch hoặc đã định giá khắc phục | Penalty/PBN/mã độc ẩn = quả bom nổ giữa hợp đồng |
| PI-08 | Cam kết suy từ data, không đặt trước | Chiều ngược lại là nguồn gốc mọi deal vỡ |
| PI-09 | Test khả thi +20% pass | Không có cửa +20% = đội vận hành gánh số chết |
| PI-11 | Nguồn lực khách đủ | KPI phụ thuộc phần việc không ai gánh = KPI ảo |
| PI-14 | Director duyệt go/no-go | Người thẩm định không tự quyết deal mình chạy |

## Quy trình dùng nhanh

1. Lead nghiêm túc → Account thu PI-01, PI-02, PI-11, PI-12 (phía khách); SEO chạy PI-03 → PI-07 (data).
2. Chạy PI-08 + PI-09 → dựng kịch bản cam kết + timeline PI-10.
3. Soi bảng Red-flags — dính flag nào ghi rõ + ngoại lệ (nếu có).
4. Trình Director quyết định (PI-14) → go: `gtv-proposal` dùng số đã thẩm định → ký (PI-13) → bàn giao hồ sơ thẩm định cho `acc-kickoff-setup` + `checklist-kpi-okrs-planning.md`.
