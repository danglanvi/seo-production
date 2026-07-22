---
type: sop
status: draft
last_updated: 2026-07-19
sources:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/2. Quy trình lập kế hoạch Link building - chưa có.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/3. Link building offpage GTV.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/3. Link building offpage GTV - bản đào tạo.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/4. Research & đánh giá backlinks.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/6. Tiêu chuẩn Triển khai backlinks.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/Checklist triển khai Bosting Linkjuice.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/Hướng dẫn Syndication.docx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/11. Các phương pháp index link/Index Blog comment.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/11. Các phương pháp index link/Index link - Entity Mastermind.docx
related:
  - "[[Link Building]]"
  - "[[TrustRank]]"
  - "[[Phantom Keywords]]"
  - "[[Consensus]]"
  - "[[Topical Authority]]"
  - "[[Internal Linking Rules and Strategy]]"
  - "[[Entity Home]]"
  - "[[Historical Data]]"
tags: [semantic-seo, sop, offpage, backlink, gtv]
---

# SOP 10 — Quy Trình Offpage SEO (Process Layer)

> **Vị trí trong hệ thống:** Đây là tầng PROCESS — nối 3 skill backlink hiện hành (`backlink-research` → `backlink-plan` → `textlink-analyzer`) với timeline dự án 10 tháng ([sop/09-project-timeline/10-thang-thuc-day.md](09-project-timeline/10-thang-thuc-day.md)) và checklist QC per-batch ([sop/06-self-checklist/tier-1-offpage-backlink.md](06-self-checklist/tier-1-offpage-backlink.md)). SOP này KHÔNG lặp lại nội dung skill/checklist — nó định nghĩa **trình tự, handoff, ai làm / ai duyệt, và điều kiện dùng từng method**.
>
> **Nguồn gốc:** hợp nhất quy trình offpage legacy GTV 2017-2025 (folder `raw/.../10. Quy Trinh Offpage SEO/` + `11. Các phương pháp index link/`) với hệ skill backlink 3 layer (07/2026). Mỗi mục ghi rõ *[Legacy giữ]* vs *[Nâng cấp 2026]*.

---

## 1. Nguyên tắc nền (đọc trước khi làm bất cứ gì)

1. **Gate số 1 — 90% site chưa cần đẩy backlink.** Site không lên top → 90-99% do content / cấu trúc / UX, không phải thiếu link. Content + structure chưa chuẩn → **HALT**, fix trước (route `seo-onpage` / SOM / SCW). Chỉ proceed khi có dấu hiệu rõ: mất cân đối content-vs-RD, link gap trong research data, keyword kẹt trang 2. *(Lưu đồ B + `backlink-plan` Bước 0 — [Nâng cấp 2026: legacy không có gate này, mặc định cứ dự án là đi link].)*
2. **Money-page link-gap test trước khi bắn link thẳng.** Đối thủ top 5 có **0 quality links vào money page tương ứng** → KHÔNG link thẳng money page → route qua supporting content. Gap = N quality RDs → đó là climb cost, cân economics trước khi cam kết. *(`backlink-research` §5 — [Nâng cấp 2026].)*
3. **Supporting-content-first + trang "lăng kính".** Chọn trang tầng thấp trong cấu trúc, intent cụ thể, cạnh tranh thấp, internal link dày 2 chiều (lên cha + xuống con) → sức mạnh tán xạ kéo cả cluster. Không có internal link 2 chiều → fix internal trước khi bắn ([[Internal Linking Rules and Strategy]]). *(Legacy giữ: đây chính là "phương án Tán xạ ánh sáng — Hubpage" + "Topic cluster & phối hợp link juice" trong quy trình 2022; 2026 chỉ đặt tên lại và đưa thành bước bắt buộc.)*
4. **Anchor theo canonical framework — KHÔNG chế số mới.** Mọi tỷ lệ anchor lấy từ [`skills/backlink-plan/references/anchor-ratio-framework.md`](../../../skills/backlink-plan/references/anchor-ratio-framework.md) (4 lớp: giai đoạn trust 3 giai đoạn → SERP consensus → GTV prior per page type → Authority-Aggression; **Exact ≤8-10% trần cứng mọi giai đoạn**). Bảng ratio 2019/2022 trong file legacy chỉ còn giá trị lịch sử — đã được reconcile vào framework canonical. *(Legacy giữ nguyên lý "an toàn trước, từ khóa sau" + rule "nguồn yếu chỉ nhận brand/naked/generic"; nâng cấp: 1 bản canonical duy nhất thay vì 3 bảng lệch nhau.)*
5. **Velocity theo nhịp đối thủ — "Hiệu ứng Cừu Đen".** Đừng lạc loài so với đối thủ: nhịp chuẩn = RD/tháng trung bình đối thủ (`backlink-research` §2); site mới bắt đầu ½ nhịp. Tiến độ tăng dần đều, không bung rồi dừng đột ngột — sau khi kết thúc plan chính vẫn duy trì link nền nhỏ giọt. *(Legacy giữ: Cừu Đen + "tiến độ tăng dần đều" + "chia nhỏ backlink sau plan" là luật GTV từ 2019; 2026 chỉ chuẩn hóa cách đo nhịp bằng data.)*
6. **Theme > Trust > Traffic khi đánh giá nguồn.** Thứ tự đánh giá backlink legacy 2025 giữ nguyên: Theme (keyword ở Domain > URL > Title > onpage > ranking topic liên quan) → Trust (seedsite, TF, sự tự nhiên, DR, UR) → Traffic (từ keyword liên quan, CTR) → Đa dạng (nền tảng, gốc domain, anchor, đích đến). 1 link đúng theme DR50 > 100 link directory rác ([[TrustRank]], [[Consensus]]). *(Legacy giữ nguyên — trùng khớp với rule "Theme > User signal > Trust" của skill 2026.)*
7. **Entity campaign tách riêng.** Social profile / Google Stack / citations thuộc chiến dịch Entity ([[Entity Home]], sop/04) — không đếm vào quota backlink, không tính vào velocity so với đối thủ. Nhưng chúng là **điều kiện đi trước**: URL SEO chủ chốt phải có social + stack nền trước khi nhận link trả phí. *(Legacy giữ: "triển khai social và google stack trước khi đi link"; quyết định tách Entity/Backlink là GTV 2021.)*
8. **Offpage phục vụ Topical Authority, không thay thế nó.** Link chỉ khuếch đại [[Topical Authority]] + [[Historical Data]] đã có từ content — không cứu được site coverage kém. Content offpage (guest post, site vệ tinh) target [[Phantom Keywords]] để tự nó rank và mang trust thật.

---

## 2. Pipeline 3 layer — DATA → DECISION → EXECUTION

Xương sống vận hành là bộ 3 skill; SOP này quy định handoff và vai trò:

| Layer | Skill / công cụ | Output | Ai làm | Ai duyệt |
|---|---|---|---|---|
| **DATA** | `backlink-research` (DataForSEO ưu tiên → Ahrefs → CSV) | Research file 6 section: profile mình vs đối thủ, velocity 12 tháng, link gap, anchor consensus, money-page link-gap test, linkable assets | SEO Executive / SEO Lead Project | SEO Lead Project |
| **DECISION** | `backlink-plan` (+ Gate Offpage T6 — Lưu đồ B) | Plan 8 section + CSV per-link: gate verdict, targets, anchor plan, method mix, lịch tháng, budget, tracking, risk log | SEO Lead Project | SEO Leader / **SEO Director** (bắt buộc khi risk moderate/aggressive hoặc budget vượt hợp đồng) |
| **EXECUTION** | `textlink-analyzer` (textlink PR) · outreach team (guest post, digital PR, niche edit) · nhà cung cấp đã vet | Link live + sheet vận hành cập nhật trạng thái | SEO Executive / Content (bài offpage) | SEO Lead Project per batch |

**Luật handoff (bắt buộc, không skip):**

1. **Không plan chay:** `backlink-plan` chỉ chạy khi có research file (hoặc data tương đương user cấp). Không có → quay lại DATA.
2. **Không execute ngoài plan:** mọi link đặt ra phải trace được về 1 dòng trong CSV plan (Domain/nguồn | Dạng | Giá | Target URL | Anchor type | Anchor 3 phần | Tháng | Trạng thái). Link phát sinh ngoài plan → thêm dòng + SEO Lead Project duyệt trước.
3. **Budget & khách:** Account trình budget offpage cho khách tại Gate T6 (mục 3) — dựa trên plan section 5; Account KHÔNG tự điều chỉnh method mix/velocity (việc của SEO Lead Project).
4. **Nhịp review:** research refresh mỗi quý hoặc khi SERP biến động; plan review milestone hàng tháng (điều kiện dừng/đổi hướng ghi sẵn trong plan section 6).
5. **Content offpage** (bài guest post / bài cho site vệ tinh) đi qua pipeline content bình thường (Phase 3 draft + skill SCW), target [[Phantom Keywords]], onpage như bài SEO thật — Content làm, SEO Lead Project duyệt.

*[Legacy giữ: cấu trúc B1→B10 của quy trình 2022 (chọn URL target → đếm RD đối thủ → anchor → research domain → chọn nguồn → hoạch định plan → content nâng cao → timeline → triển khai → index) chính là tiền thân của pipeline này — B1-B5 nay là DATA, B6-B8 là DECISION, B9-B10 là EXECUTION + mục 5. Nâng cấp 2026: tách vai trò cứng 3 layer, thêm gate, mọi số liệu chạy bằng API thay vì đếm tay Ahrefs Top Pages.]*

---

## 3. Timeline chuẩn 10 tháng (khớp sop/09)

```
T1-T3       T4-T5              T6                T6-T8            T7-T8         T10
Entity nền  Backlink NỀN       GATE OFFPAGE      ĐẨY MẠNH         Textlink PR   Bàn giao
(sop/04)    + phantom content  (Lưu đồ B)        (đỉnh T6-T7)                    master list
            └────────── GEO backlink consensus chạy chung T4-T7 ──────────┘
```

| Giai đoạn | Việc | Ghi chú vận hành |
|---|---|---|
| **T1-T3** | Entity campaign (social, stack, citations) — sop/04, KHÔNG thuộc quota backlink | Điều kiện nền để T4+ nhận link an toàn |
| **T4-T5** | **Backlink nền + phantom guest post**: link nền an toàn (brand/naked/generic) vào homepage + URL trọng điểm; Content Offsite SEO target [[Phantom Keywords]] (`allintitle:` <1.000 rất tốt / <5.000 chấp nhận) đăng guest post / site vệ tinh. `backlink-research` chạy full trong cửa sổ này để có data cho Gate T6 | PIC: SEO + Content · Duyệt: SEO Lead Project |
| **T4-T7** | **GEO backlink consensus** chạy chung chiến dịch offsite: chọn nguồn xuất hiện trong citation set của AI engines ([[Consensus]]) — cùng 1 chiến dịch, thêm 1 lăng kính chọn nguồn | Không tách budget riêng |
| **T6** | **GATE OFFPAGE (Lưu đồ B)**: verdict cần-đẩy-hay-không → target lăng kính supporting-first → anchor theo mô hình 3 giai đoạn (Exact ≤8-10%) → velocity theo đối thủ → **budget trình khách (Account)** | `backlink-research` → `backlink-plan`; Duyệt: SEO Leader/Director |
| **T6-T8** | **Đẩy mạnh** theo plan, **đỉnh T6-T7**; trong tháng: free/foundational trước → paid sau; hoàn tất T8 | Kỳ vọng kết quả 1-6 tháng — ghi vào plan để quản trị kỳ vọng khách |
| **T7-T8** | **Textlink báo PR**: lọc URL slug-only + anchor plan → route `textlink-analyzer`; chốt T8 | Risk-managed — xem mục 4 |
| **T9** | Không mở batch mới; duy trì link nền nhỏ giọt (tránh dừng đột ngột — luật "tiến độ tăng dần đều") + xử lý link chết/rớt index | |
| **T10** | Nghiệm thu: master list backlink (mục 6) + refdomains/DR trend + tỷ lệ index vào báo cáo bàn giao | |

**Biến thể 8 / 12 tháng** (theo bảng sop/09): 8 tháng — nền+phantom T3-T4, đẩy mạnh T5-T7 (đỉnh T5-T6), textlink T6-T7 · 12 tháng — nền+phantom T4-T6, đẩy mạnh T7-T9 (đỉnh T7-T8), textlink T9-T10. Nguyên tắc bất biến: gate luôn đứng trước đẩy mạnh; không nén giai đoạn nền.

*[Legacy giữ: tư duy "hoạch định số lượng theo timeline, tăng dần rồi hạ dần, dự án gấp dồn link mạnh lên đầu, site trust cao chịu được dồn link" (B8, 2022) + khung phân bổ % theo tháng của checklist Boosting Linkjuice. Nâng cấp 2026: neo cứng vào timeline 10 tháng rev 2, thêm Gate T6 và lớp GEO consensus.]*

---

## 4. Method catalog — tier kiểm soát

> Chỉ đạo Vincent: **GIỮ tactic legacy, gắn tier kiểm soát thay vì xóa.** 3 tier: ✅ mặc định (mọi dự án client) · ⚠ risk-controlled (chỉ khi SEO Lead/Director duyệt rõ, có điều kiện dùng) · ⛔ deprecated (không dùng nữa, ghi lý do). Chi phí tương đối: $ thấp · $$ vừa · $$$ cao.

### ✅ Tier mặc định (conservative — chuẩn client GTV)

| Method | Mục đích | Chi phí | Rủi ro | Điều kiện dùng |
|---|---|---|---|---|
| **Guest post / Digital PR chính thống** | Link editorial đúng theme, mang trust thật + citation cho GEO | $$-$$$ | Thấp (nguồn vet kỹ) | Nguồn đạt chuẩn legacy 2025: liên quan chủ đề, organic traffic ≥3.000, RD >50, tuổi >5 tháng, ít external link; bài target [[Phantom Keywords]], onpage đầy đủ; nếu ≥2 bài/nguồn → internal link bài 1 → bài 2 cuốn chiếu |
| **Đặt link trên bài đã có traffic (niche edit)** | Nhận trust + traffic sẵn có của bài top | $$ | Thấp-vừa | Ưu tiên loại 1 legacy: Theme ở Domain/URL/Title, page traffic >100 (Ahrefs, tùy thị trường); anchor theo Authority-Aggression (exact chỉ ở nguồn mạnh đúng theme) |
| **Social entity / stack support** | Nền anchor an toàn (brand/naked/generic) + kích hoạt entity trước khi link trả phí vào | $ | Rất thấp | Chạy TRƯỚC mọi đợt link trả phí vào URL trọng điểm (luật legacy "social + google stack trước khi đi link"); thuộc Entity campaign, không đếm quota backlink |
| **Linkable asset / data study + reclaim mention** | Earned link compliant, bền nhất | $$ (công content) | Rất thấp | Khi research §6 cho thấy content type hút link trong niche; unlinked mention của brand → xin gắn link |
| **Textlink báo PR** (route `textlink-analyzer`) | Phủ số lượng lớn anchor an toàn qua hệ báo | $$ | Vừa (paid placement — risk-managed) | Chỉ trong cửa sổ T7-T8, sau khi nền đã vững; lọc URL slug-only, exact ≤ trần, rải velocity theo tuần, giữ danh sách domain để disavow được khi cần |

### ⚠ Tier risk-controlled — SEO Lead/Director duyệt từng chiến dịch

Nguyên tắc chung của tier này (kế thừa phân loại backlink 6 loại legacy): đây là các backlink **dính footprint** (loại 4-6 legacy) — chấp nhận khi (a) khách đã hiểu + đồng ý risk level moderate/aggressive trong plan, (b) keyword kẹt mà economics của link sạch quá đắt, (c) không phải site YMYL/brand lớn nhạy cảm rủi ro. GTV **không mặc định đề xuất** cho client.

| Method | Mục đích | Chi phí | Rủi ro | Điều kiện dùng (khi nào chấp nhận) |
|---|---|---|---|---|
| **Web 2.0 / articles brand** | Đa dạng profile, đẩy anchor an toàn, tier 2 cho asset | $ | Vừa (footprint pattern) | Chỉ nền tảng DA cao còn sống (Medium, LinkedIn, Tumblr, WordPress.com); syndication content thật của brand, KHÔNG spin; anchor brand/URL/generic only |
| **PBN / PBN mininet / "08 method" (subdomain mininet)** | Kiểm soát hoàn toàn anchor + link juice cho keyword kẹt | $$$ (nuôi hệ thống) | **Cao** (manual action, mất cả hệ thống) | Chỉ risk aggressive + Director duyệt; tuân thủ trọn bộ tiêu chuẩn setup PBN legacy (whois/IP lớp C/DNS không trùng, không chung account Google, authority outlink ≥ link về moneysite, bài ≥400 chữ, link cách nhau ≥2 ngày, 3-6 link/domain); không bao giờ chạy trên site khách không thể tách rời |
| **Forum seeding / blog comment (link + index)** | Đa dạng + social signal + thúc index tier 1 | $ | Vừa (spam pattern lộ) | Forum thật còn hoạt động, ≥50% đúng chủ đề, DR >15, tỷ lệ index >80%; anchor brand/URL/generic only, ≤15 link/forum; bài liên quan thật, không spin hàng loạt |
| **Redirect / schema / iframe / mention link** | Tận dụng nguồn mạnh nhưng dính footprint (loại 4-5 legacy) mà không đặt link trực tiếp | $$ | Vừa-cao (dễ bị neutralize, giá trị không bền) | Chỉ khi nguồn theme rất cao không lấy được link thường; từng case SEO Lead duyệt; không dùng làm trụ chính của plan |
| **Backlink 3rd party marketplace (konker-style gigs)** | Đẩy tier 2/3 cho asset offpage | $ | Cao (chất lượng không kiểm soát) | CHỈ tier 2-3 (không bao giờ trỏ moneysite — luật legacy giữ nguyên); nhà cung cấp đã test; ngân sách nhỏ thí điểm trước |
| **Tiered boosting (10-minutes tier 2, link wheel, syndication tier 2)** | Bơm sức mạnh cho web 2.0 / bài báo / stack đang giữ phantom ranking | $-$$ | Vừa | Chỉ boost asset offpage (không trực tiếp moneysite); asset phải đang có phantom keyword rank 5-30 đáng đẩy |

### ⛔ Deprecated — không dùng, giữ làm tư liệu

| Method | Lý do khai tử |
|---|---|
| **RSS / Feedburner hub** | Hệ sinh thái chết — Feedburner ngừng phát triển, footprint lộ, giá trị index ≈ 0 |
| **Spin content hàng loạt (forum/web 2.0 spin ≥3 bài trộn)** | SpamBrain/scaled-content-abuse 2024+ nhận diện thẳng; chất lượng âm cho brand |
| **AMP như đòn bẩy index** | AMP đã bị Google bỏ ưu đãi; các bước cài AMP trong tài liệu index legacy không còn tác dụng |
| **Fetch as Google / công cụ index đời cũ (Ghostindexer, Lar index, gói fiverr blog-comment-index)** | Tool/endpoint chết hoặc đổi; thay bằng mục 5 |

*[Legacy giữ: toàn bộ danh mục tactic 16 sheets Boosting Linkjuice + phân loại 6 loại backlink + tiêu chuẩn từng kênh (forum DA/DR/tỷ lệ index, web 2.0 DA>80, guest post traffic ≥3.000...) — chuyển thành điều kiện dùng per method. Nâng cấp 2026: gắn tier + người duyệt + tách compliant (earned/PR) vs risk-managed (paid/tiered) theo guardrail chính sách trong anchor framework.]*

---

## 5. Index & verify

**Nguyên lý giữ lại từ legacy (folder 11 + Syndication):** link không index = link không tồn tại. 3 cơ chế thúc index còn giá trị:

1. **Internal link từ trang mạnh (hubpage crawl):** với danh sách link offsite cần index (social, web 2.0, bài báo) — dẫn crawl qua trang/tập hợp có sức mạnh sẵn để Google cào chuỗi ("cào 1 thằng sẽ cào luôn những thằng còn lại" — nguyên lý stack). Với URL trên site mình: internal link từ trang authority cao + đảm bảo nằm trong sitemap.
2. **Social signal / syndication:** share bài gốc + asset offpage lên hệ social của brand (Zapier/tay — nguyên lý Syndication giữ, tool tự chọn theo thời điểm); mỗi bản sao trích nguồn về bài gốc.
3. **Sitemap + ping chủ động:** URL của mình → GSC URL Inspection / sitemap resubmit (thay thế "Fetch as Google" đã chết); URL ngoài site → không kiểm soát được trực tiếp, dùng cơ chế 1-2.

**Phân loại trước khi index (giữ từ Index link - Entity Mastermind):** chỉ thúc index link có giá trị — bài viết/trang danh mục/service page + asset offpage chất lượng. KHÔNG index: thin content, trang trùng lặp, link spam, trang bẩn.

**Tiêu chí link "TÍNH" (đủ 4 mới đếm vào quota):**
1. **Live** — HTTP 200, link còn trên trang, đúng vị trí trong content (không bị đẩy xuống footer/hidden).
2. **Indexed** — URL nguồn có trong index Google (`site:` check hoặc index checker).
3. **Anchor đúng plan** — đúng anchor 3 phần + anchor type như dòng CSV; đúng dofollow/nofollow đã mua.
4. **Context còn nguyên** — đoạn co-occurrence quanh anchor không bị sửa mất.

**Nhịp check:** sau đặt 7 ngày (live + submit index) → 30 ngày (indexed? chưa → thúc index đợt 2, vẫn không → đòi nhà cung cấp thay thế) → hàng tháng đến hết dự án (link rớt/bị sửa → xử lý trong tháng). Mục tiêu tỷ lệ index ≥80% mỗi batch (ngưỡng kế thừa chuẩn legacy); batch <80% sau 2 vòng thúc → đánh giá lại nguồn.

*[Legacy giữ: nguyên lý hubpage/stack/social signal + chuẩn ">80% index". Nâng cấp 2026: bỏ tool chết (mục 4 deprecated), thêm định nghĩa link "tính" 4 tiêu chí + nhịp check gắn vào sheet vận hành.]*

---

## 6. Quality control

- **Per-batch:** mọi đợt link trước khi nghiệm thu chạy checklist [sop/06-self-checklist/tier-1-offpage-backlink.md](06-self-checklist/tier-1-offpage-backlink.md) *(checklist đang được build — reference theo tên file; SOP này không lặp nội dung)*. SEO Executive tự check → SEO Lead Project duyệt batch.
- **Master list backlink (bàn giao T10):** 1 sheet duy nhất suốt dự án, mỗi dòng 1 link theo format plan CSV (Domain/nguồn | Dạng | Giá | Target URL | Anchor type | Anchor 3 phần | Tháng | Trạng thái) + 3 cột verify (Live | Indexed | Lần check cuối). Đây vừa là công cụ vận hành vừa là tài sản bàn giao: khách/đội duy trì cần nó để giám sát link rớt và để disavow được khi cần.
- **Kỷ luật plan-trace:** link không trace được về plan = không nghiệm thu, không thanh toán.
- **Review theo quý:** anchor profile thực tế vs framework (lệch >2% có chủ đích phải có ghi chú; exact vượt trần → dilute bằng pillow wave brand/generic/naked, không disavow trừ khi negative impact rõ).

*[Legacy giữ: thói quen "lưu trữ link vào file dự án" + template plan sheet (Bamboo Airway, Tin Học Anh Phát...). Nâng cấp 2026: chuẩn hóa 1 master list + gắn checklist per-batch riêng.]*

---

## 7. Đo lường & báo cáo

**Spam-discount rule (convention GTV — áp trước mọi đánh giá):** trước khi đọc bất kỳ chỉ số profile nào, loại bỏ (discount) anchor rác + spam refdomains khỏi dataset — cả của mình lẫn đối thủ — theo tiêu chí `backlink-research/references/spam-filter-criteria.md` (REJECT cần ≥2 tín hiệu máy; nghi ngờ → REVIEW giữ + đánh dấu; không dùng chữ "toxic"). Số chưa discount không được đưa vào báo cáo.

| Chỉ số | Cách đo | Nhịp | Ngưỡng hành động |
|---|---|---|---|
| **Refdomains trend (đã discount)** | RD mới/mất per tháng vs nhịp đối thủ (research §2) | Tháng | Lệch nhịp đối thủ quá xa 2 chiều → điều chỉnh velocity (Cừu Đen) |
| **DR/authority trend** | DR + phân bố DR của RD mới | Tháng | DR nguồn mới tụt liên tục → xem lại nhà cung cấp |
| **Ranking money page & keyword pos 4-20** | Rank tracker per target URL trong plan | Tuần/tháng | 2-3 tháng link đủ quota mà keyword không nhúc nhích → DỪNG link, quay lại audit content (điều kiện dừng trong plan) |
| **Tỷ lệ index** | Live + Indexed từ master list | Batch + tháng | <80%/batch sau 2 vòng thúc → đổi nguồn |
| **Anchor distribution thực tế** | Đếm từ master list + `anchors/live` | Quý | Vượt trần exact / lệch consensus → pillow wave |
| **GEO citation (T4-T7)** | Nguồn đã link có xuất hiện trong AI citation set không | Quý | Đo qua `geo-tracking-prompt-selection`, vào báo cáo kép T10 |

**Báo cáo:** tháng — SEO Lead Project tổng hợp vào báo cáo dự án (Account nhận phần ngôn ngữ khách qua `gtv-client-report`); T10 — chương offpage trong báo cáo nghiệm thu: master list + RD/DR trend + tỷ lệ index + đóng góp ranking money pages.

*[Legacy giữ: tư duy đếm RD (không đếm backlink thô Ahrefs) + đo 3 tầng domain/topic/URL. Nâng cấp 2026: spam-discount rule bắt buộc, điều kiện dừng chính thức, lớp đo GEO.]*

---

## Changelog

- **2026-07-19 v1.0** — hợp nhất legacy 2020-2025 + hệ skill backlink 3 layer. Nguồn legacy đọc đủ: Checklist Boosting Linkjuice (16 sheets), Tiêu chuẩn Triển khai backlinks (2020), Link building GTV (2022 + bản đào tạo), Research & đánh giá backlinks (2025), Quy trình lập kế hoạch Link building, Hướng dẫn Syndication, folder 11 (Index Blog comment + Index link Entity Mastermind). Quyết định chính: gate 90%-chưa-cần đứng đầu quy trình; anchor trỏ canonical framework duy nhất; tactic legacy giữ nguyên nhưng gắn tier ✅/⚠/⛔ + người duyệt; index workflow bỏ tool chết giữ nguyên lý; spam-discount rule thành bước bắt buộc của đo lường.
