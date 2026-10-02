---
type: sop
tier: 1
phase: offpage-backlink
last_updated: 2026-10-02
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/Checklist triển khai Bosting Linkjuice.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/6. Tiêu chuẩn Triển khai backlinks.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/4. Research & đánh giá backlinks.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/10. Quy Trinh Offpage SEO/3. Link building offpage GTV.xlsx
canonical_frameworks:
  - skills/backlink-plan/references/anchor-ratio-framework.md
items_count: 21
tags: [sop, tier-1, offpage, backlink, textlink, self-checklist, quality-gate]
---

# Tier 1 — Self-Checklist: Offpage & Backlink (per batch)

> **Khi dùng:** Người chạy offpage tự check **MỖI BATCH link** trước khi triển khai và sau khi triển khai xong batch.
> **Phạm vi công đoạn:** 20 — Offpage nền (T4-T5) · 25 — Gate Offpage (T6) · 26 — Đẩy mạnh backlink (T6-T8) · Textlink PR (T7-T8) · Master list bàn giao (T10).
> **Số items:** 21 (OF-01 – OF-21) = 4 Pre-batch gate + 5 Chất lượng nguồn + 5 Content offpage + 3 Textlink PR + 4 Post-batch verify.
> **P0 gate (7 items):** OF-01 · OF-02 · OF-03 · OF-04 · OF-08 · OF-13 · OF-20 — fail bất kỳ item P0 nào → **KHÔNG bắn batch** (hoặc không đóng batch với OF-20).
> **Scoring:** Self Score /21 → Self %. Cơ chế 3-level review (Self → Lead spot-check ngẫu nhiên) giống hệ Content — xem `README.md` mục 2.

**Nguyên tắc số 1 (kế thừa Gate Offpage):** 80-90% dự án top KHÔNG cần chiến dịch backlink. Checklist này chỉ chạy SAU KHI Gate Offpage đã verdict "cần link". Anchor ratio duy nhất được phép dùng là bản canonical `skills/backlink-plan/references/anchor-ratio-framework.md` — **không chế số mới, không dùng lại bảng % trong file legacy** (bảng legacy giữ làm lịch sử đối chiếu).

## Map item → skill / wiki ref

| ID | Label | Ref |
|---|---|---|
| OF-01 | Gate Offpage + link-gap test | skill `backlink-plan` B0-B1 · [[Link Building]] |
| OF-02 | Target URL lăng kính supporting-first | skill `backlink-plan` B1 · [[Internal Linking Rules and Strategy]] |
| OF-03 | Anchor plan đúng canonical framework | `anchor-ratio-framework.md` (4 lớp) |
| OF-04 | Velocity theo nhịp đối thủ | skill `backlink-plan` B4 |
| OF-05 | Tiêu chí site đặt link (T.T.T bản 2026: Theme 35 · Traffic 35 · Trust 30) | [[Source Authority]] · `sop/12-backlink-stack-models.md` §2 |
| OF-06 | Footprint check nguồn | [[TrustRank]] |
| OF-07 | Authority-Aggression per nguồn | `anchor-ratio-framework.md` Nguyên tắc 3 |
| OF-08 | Legacy tactic + mô hình stack ⚠ Lead xem trước, Director chốt | `sop/12-backlink-stack-models.md` |
| OF-09 | Đa dạng nền tảng + dofollow/nofollow + cap domain | — |
| OF-10 | Phantom Keywords cho bài offpage | [[Query Network]] |
| OF-11 | Bài unique — không spin | — |
| OF-12 | Entity brand nhất quán | [[Entity Home]] |
| OF-13 | 1 link money + anchor đúng plan | `anchor-ratio-framework.md` |
| OF-14 | Co-occurrence + contextual link + onpage bài offpage | `anchor-ratio-framework.md` Nguyên tắc 4b |
| OF-15 | Textlink PR: lọc URL slug-only | skill `textlink-analyzer` |
| OF-16 | Textlink PR: tỷ lệ anchor an toàn per đợt | `anchor-ratio-framework.md` |
| OF-17 | Textlink PR: tracking file theo đợt | skill `textlink-analyzer` B6 |
| OF-18 | Link live + index sau X ngày | — |
| OF-19 | Anchor thực tế vs plan | — |
| OF-20 | Master list backlink cập nhật | bàn giao T10 |
| OF-21 | Review kết quả + điều kiện dừng | skill `backlink-plan` B6 |

---

## NHÓM 1 — PRE-BATCH GATE (trước khi bắn batch)

### OF-01 — Gate Offpage / link-gap test đã pass 🔴 P0

**Nhóm:** Pre-batch gate

**Tóm tắt:** Batch này chỉ tồn tại khi Gate Offpage (công đoạn 25, T6) hoặc quyết định offpage nền (công đoạn 20, T4-T5) đã verdict "cần link" qua skill `backlink-plan` Bước 0: content + structure đã chuẩn, có dấu hiệu cần link (link gap rõ / keyword kẹt trang 2 / mất cân đối RD). Money page phải qua **link-gap test**: đối thủ có 0 quality link vào money page → không link thẳng money page.

**Mô tả đầy đủ:**
1. Có file plan từ `backlink-plan` (hoặc gate-offpage-decision) ghi verdict + lý do đi link → batch phải trỏ về plan đó.
2. Batch nằm trong quota + timeline của plan — không bắn ngoài plan.
3. Nếu content/structure chưa chuẩn → HALT, trả về onpage/content. "Đi link cho site content chưa chuẩn = đốt tiền" — lỗi số 1.

**Ví dụ Đạt / Không Đạt:**
✅ Batch 15 link tháng T6 nằm trong plan đã duyệt, verdict gate ghi "cluster X kẹt pos 8-15, gap 12 RD vs đối thủ".
❌ "Tiện có nguồn rẻ nên bắn thêm 30 link" — không có gate, không thuộc plan nào.

**Nguồn:** `backlink-plan` SKILL.md B0 · Legacy: `3. Link building offpage GTV.xlsx` sheet "1. Tổng Quan quy trình" B2 (phân tích RD đối thủ trước khi định số lượng).

---

### OF-02 — Target URL theo mô hình lăng kính supporting-first 🔴 P0

**Nhóm:** Pre-batch gate

**Tóm tắt:** URL nhận link trong batch chọn theo mô hình lăng kính: ưu tiên trang tầng thấp, intent cụ thể, cạnh tranh thấp, **internal link dày 2 chiều** (lên cha + xuống con) để sức mạnh tán xạ kéo cả cluster. Money page chỉ nhận link trực tiếp khi link-gap test cho phép. Site mới chưa đủ trust → homepage trước với pillow anchor.

**Mô tả đầy đủ:**
1. Đối chiếu bảng target trong plan: URL | vai trò (home/supporting/category/money) | lý do | quota.
2. Check internal link 2 chiều của trang đích TRƯỚC khi bắn — chưa có → yêu cầu fix internal trước (handoff, không tự sửa).
3. Ưu tiên URL có keyword đang rank **vị trí 4-20, volume ≥100** (quick win) và URL/topic chứa nhiều keyword chưa rank.
4. Cân bằng mật độ backlink theo cấu trúc site — tầng càng thấp volume càng lớn thì phân bổ RD tương xứng, không dồn hết vào 1 URL.

**Ví dụ Đạt / Không Đạt:**
✅ Batch trỏ vào bài supporting "cách chọn X" (pos 9, volume 320, internal 2 chiều về category) — kéo cả cluster.
❌ Bắn 100% batch thẳng money page trong khi top 3 đối thủ có 0 RD vào money page tương ứng.

**Nguồn:** `backlink-plan` B1 (lăng kính, Vincent) · Legacy: `3. Link building offpage GTV.xlsx` B1 ("URL có khả năng link tới nhiều URL SEO khác — tính cộng hưởng/tán xạ ánh sáng"; "cân bằng mật độ backlink theo cấu trúc") · `6. Tiêu chuẩn Triển khai backlinks.xlsx` (nguyên tắc "Topic cluster & sự phối hợp của link juice", "Cân bằng mật độ backlink theo cấu trúc site").

---

### OF-03 — Anchor plan đúng canonical framework (Exact ≤8-10%, 3 giai đoạn) 🔴 P0

**Nhóm:** Pre-batch gate

**Tóm tắt:** Anchor của batch phải nằm trong anchor plan lập theo `skills/backlink-plan/references/anchor-ratio-framework.md` — áp **4 lớp đúng thứ tự**: (1) giai đoạn trust của site → chốt tổng AN TOÀN vs TỪ KHÓA (GĐ1 ~70/30 · GĐ2 40-50/50-60 · GĐ3 35-45/55-65); (2) SERP consensus tinh chỉnh; (3) GTV prior per page type; (4) Authority-Aggression. **Trần cứng Exact ≤8% homepage / ≤10% category-money — MỌI giai đoạn.**

**Mô tả đầy đủ:**
1. Xác định giai đoạn trust từ research data — nghi ngờ giữa 2 giai đoạn → chọn giai đoạn thấp hơn.
2. Batch có anchor map 20-30 variations per target, rotate; không lặp anchor non-brand trong cùng tháng.
3. Cộng dồn anchor batch này với các batch trước trong tháng → tổng % vẫn trong ngưỡng.
4. ⚠ KHÔNG dùng bảng % trong file legacy (Boosting Linkjuice: exact 12-15%; bảng 2019/2022 trong Link building offpage GTV) làm chuẩn — các bảng đó đã bị canonical framework thay thế. Có xung đột → framework thắng.

**Ví dụ Đạt / Không Đạt:**
✅ Site GĐ1 (RD thấp, DR mới): batch 20 link = 14 brand/naked/generic + 6 partial/brand+KW, exact = 0.
❌ Site mới nhưng batch dùng 15% exact "theo file PBN cũ" — vượt trần + sai giai đoạn.

**Nguồn:** `anchor-ratio-framework.md` (canonical duy nhất) · Legacy đối chiếu (KHÔNG dùng làm chuẩn): `Checklist triển khai Bosting Linkjuice.xlsx` sheets "plan PBN", "anchor text & plan" · `3. Link building offpage GTV.xlsx` sheet "2. Phân bổ tỉ lệ anchor text".

---

### OF-04 — Velocity theo nhịp đối thủ, tăng dần đều 🔴 P0

**Nhóm:** Pre-batch gate

**Tóm tắt:** Số link của batch nằm trong nhịp tháng của plan: chuẩn = RD/tháng trung bình của đối thủ; site mới bắt đầu ½ nhịp. Tiến độ **tăng dần đều** — không đột biến, không "bung 5.000 link 1 ngày". Trong tháng: free/foundational trước → paid sau.

**Mô tả đầy đủ:**
1. Check batch size vs quota tháng trong plan; batch textlink lớn phải rải theo tuần.
2. GTV triển khai onsite kỹ → tổng RD thường chỉ cần **50-75% RD đối thủ** — không chạy đua số lượng.
3. Kết thúc plan chính vẫn giữ nhịp link nhỏ (không dừng đột ngột — tránh footprint "dồn rồi tắt").
4. Mỗi backlink trỏ trực tiếp money site từ cùng hệ thống nguồn phải cách nhau tối thiểu 2 ngày (rule legacy PBN — giữ như nguyên tắc giãn nhịp chung).

**Ví dụ Đạt / Không Đạt:**
✅ Đối thủ trung bình 25 RD/tháng → site mới đi 12-13 RD/tháng, chia 3-4 batch/tuần.
❌ Dồn 80 link trong tuần cuối tháng để "đủ KPI".

**Nguồn:** `backlink-plan` B4 · Legacy: `6. Tiêu chuẩn Triển khai backlinks.xlsx` ("Tiến độ tăng dần đều") · `3. Link building offpage GTV.xlsx` B2 (ước tính 50-75% RD đối thủ), B8 (tăng dần, chia nhỏ sau plan) · `Checklist triển khai Bosting Linkjuice.xlsx` sheet "plan PBN" (giãn cách 2 ngày).

---

## NHÓM 2 — CHẤT LƯỢNG NGUỒN LINK

### OF-05 — Tiêu chí site đặt link: Theme → Traffic → Trust

**Nhóm:** Chất lượng nguồn

**Tóm tắt:** Mỗi domain/URL trong batch được đánh giá theo thứ tự **Theme (liên quan ngành) → Traffic (thật) → Trust**, hiện đại hóa từ tiêu chuẩn 2020/2025: (1) Theme: keyword ở domain/URL/title, có ranking topic liên quan; (2) Traffic thật: page traffic >100 (bài có sẵn) hoặc site traffic >1.000 (guest post) trên Ahrefs — tùy thị trường; (3) Trust: DR >30 tham chiếu, backlink profile tự nhiên; (4) site được index bình thường, không bị penalty; (5) outbound profile sạch: domain không bán link tràn lan, external link ít, link out cùng theme.

**Cập nhật 02/10/2026 (khung T.T.T bản 2026, `sop/12` §2):** thang điểm là **Theme 35, Traffic 35, Trust 30** trên tổng 100 (Vincent chốt 02/10/2026, kinh nghiệm GTV). Theme xét ở cấp trang: Title, URL và đoạn chữ quanh link có từ khoá của trang đích; website cùng ngành là điểm cộng. Trust tách hai phần: sức mạnh (DR, UR, số link ra) và TrustRank (trang có được nguồn cận seed trỏ tới không). Câu "Theme là ưu tiên quan trọng nhất" ở phần mô tả bên dưới là bản 2025, giữ làm lịch sử. Kiểm thêm chính trang đặt link: đã index chưa, chuyên mục còn cập nhật không, có link nào trỏ vào không.

**Mô tả đầy đủ:**
Phân loại ưu tiên theo hệ 2025 (`4. Research & đánh giá backlinks.xlsx`):
- **Loại 1:** Theme + Trust + Traffic, đặt trên bài đã có traffic (>100 page traffic), keyword ở domain/URL/title → tốt nhất cho tier 1.
- **Loại 2:** Guest post trên site theme liên quan, traffic site >1.000, DR >30, ít external link.
- **Loại 3:** chỉ Trust + Traffic nhưng viết được bài liên quan (tự tạo theme trong title/URL).
- Domain ít traffic/trust thấp nhưng **theme cao** → vẫn dùng được để đa dạng (forum, web 2.0 liên quan).
- Note nghiệm thu: bài chưa top nhưng Google đã nhận diện đúng chủ đề (rank 11-30) → nguồn vẫn tốt. **Theme là ưu tiên quan trọng nhất.**

**Ví dụ Đạt / Không Đạt:**
✅ Blog ngành điện DR 35, organic 4.200/tháng, bài "đèn LED nhà xưởng" rank 14 → guest post loại 2.
❌ Site DR 60 nhưng bán link mọi ngành, external link dày đặc casino + thẩm mỹ viện → loại.

**Nguồn:** `4. Research & đánh giá backlinks.xlsx` sheets "2. Yếu tố đánh giá backlink", "3. Chọn lựa domain - URL, page" · `Checklist triển khai Bosting Linkjuice.xlsx` sheet "guest post" (organic traffic ≥3.000, RD >50, tuổi >5 tháng — ngưỡng gốc 2019, dùng bản 2025 làm chuẩn chính, ngưỡng cụ thể chốt theo thị trường trong plan).

---

### OF-06 — Footprint check nguồn link

**Nhóm:** Chất lượng nguồn

**Tóm tắt:** Trước khi đặt link trên nguồn thuộc hệ thống (PBN, site vệ tinh, mạng site của nhà cung cấp): check footprint — Whois trùng, IP trùng lớp C, nameserver trùng, chung tài khoản GA/GTM/GSC, source code giống nhau. Backlink bị footprint → xuống loại 4-6: chỉ đi tier 2/3 hoặc đổi cách đi (schema/iframe/mention), không tier 1 trực tiếp.

**Mô tả đầy đủ:**
1. Check tối thiểu: IP (lớp C trở đi không trùng) · DNS/nameserver · Whois · source code/theme.
2. Nguồn footprint nhưng theme/traffic/trust cao → vẫn có thể về tier 1 bằng cách đi khác (schema, iframe, mention) — quyết định ghi vào plan, không tự quyết trong batch.
3. Không dùng Chrome/Gmail đăng nhập khi thao tác trên hệ thống site — hành vi để lại footprint.

**Ví dụ Đạt / Không Đạt:**
✅ 10 nguồn batch: check IP class C + nameserver, loại 2 nguồn cùng dải IP + cùng theme WP.
❌ Nhận list 20 site từ nhà cung cấp và bắn thẳng không check — 15 site chung GA account.

**Nguồn:** `4. Research & đánh giá backlinks.xlsx` sheets "0. Tiêu chuẩn setup PBN" (whois/IP/nameserver/tài khoản Google), "3. Chọn lựa domain" (loại 4-6 = footprint → tier 2-3 / schema / iframe / mention) · `3. Link building offpage GTV.xlsx` B5 (kiểm tra footprint IP/DNS/source code).

---

### OF-07 — Authority-Aggression: anchor nào đặt ở nguồn nào

**Nhóm:** Chất lượng nguồn

**Tóm tắt:** Phân bổ anchor theo sức nguồn, không rải đều: nguồn <DR40 / nguồn yếu / bài không chủ đích → CHỈ branded · generic · naked. DR40-60 đúng theme → + partial, brand+KW, title. Exact CHỈ đặt ở nguồn DR60-85+ editorial đúng theme, title + URL bài nguồn có keyword.

**Mô tả đầy đủ:**
1. Map từng link trong batch: nguồn → loại anchor được phép.
2. Rule legacy tương đương (Vincent 2021 + Boosting Linkjuice): title bài nguồn liên quan chính xác keyword → anchor KHÔNG chứa keyword; bài thuộc lĩnh vực rộng hơn → anchor chứa keyword. Logic này đã được canonical framework chuẩn hóa thành Authority-Aggression — dùng bản framework.
3. Forum/social/web 2.0 (nguồn yếu mặc định) → chỉ brand/URL/generic (khớp legacy "anchor text brands/Url/chung").

**Ví dụ Đạt / Không Đạt:**
✅ Batch: 2 exact duy nhất nằm trên 2 bài editorial DR 65+ đúng theme; forum toàn brand/naked.
❌ Exact "dịch vụ seo" đặt trên forum DR 18.

**Nguồn:** `anchor-ratio-framework.md` Nguyên tắc 3 · Legacy: `Checklist triển khai Bosting Linkjuice.xlsx` sheet "đi link PBN" mục 1.3 (anchor theo lĩnh vực bài viết) · sheets "Forum cho moneysite", "forum cho web2.0,báo,social" (anchor brand/URL/chung cho forum).

---

### OF-08 — Legacy tactics và mô hình stack (PBN / Web 2.0 / RSS / Forum spin / backlink 3rd party / DAS, TAS, 08 method, báo có buffer) ⚠ risk-controlled — Lead xem trước, Director chốt 🔴 P0

**Nhóm:** Chất lượng nguồn

**Tóm tắt:** Các chiến thuật legacy trong bộ Boosting Linkjuice — PBN/PBN mininet/The 08 Method/10-minutes Tier 2, Web 2.0 articles brand, RSS Feedburner, Forum spin content, backlink 3rd party (mua Konker...) — **GIỮ trong kho chiến thuật nhưng KHÔNG phải mặc định**. Batch chứa bất kỳ hạng mục nào trong nhóm này → phải có **SEO Lead xem trước và SEO Director chốt bằng văn bản** (risk level = aggressive trong plan). Nhóm này không phải hạng mục mặc định; PBN, parasite và mô hình stack làm được cho khách khi đã có duyệt (Vincent xác nhận 02/10/2026). Từ 02/10/2026 luật này áp cho cả mô hình stack ở `sop/12` (DAS, TAS, 08 method, báo có buffer) và textlink báo ở trang chủ, chuyên mục, sitewide.

**Mô tả đầy đủ:**
1. Nhận diện hạng mục legacy trong batch: PBN các dạng, Web 2.0 copy bài, RSS/hub site, forum bài spin, link mua 3rd party (chỉ từng cho phép ở T2/T3).
2. Có → check plan: `$RISK_LEVEL = aggressive` + chữ ký duyệt của SEO Director (sau khi SEO Lead đã xem)? Không có → bỏ hạng mục đó ra khỏi batch.
3. Được duyệt → áp nguyên các guardrail legacy đi kèm: PBN (authority link out ≥ số link về money site, outlink cùng Topical Trust Flow, bài ≥400 chữ, ≤3 link out, giãn 2 ngày, 3-6 link/domain); Forum (DA>10/DR>15, index >5.000 bài, ≥50% forum đúng chủ đề, ≤15 backlink/forum); Web 2.0 (DA>80, 50/50 do-no); 3rd party (không bao giờ trỏ thẳng money site — chỉ T2/T3).
4. Ghi riêng các link nhóm này trong master list với tag `risk-controlled` — để disavow được khi cần.
5. Batch thuộc một mô hình stack → kèm worksheet và rubric 10 tiêu chí đã chấm (`sop/12` §9), tài sản đạt MS-01→14 (`sop/12` §6), kill switch ghi trước (`sop/12` §8). Luật tầng: link rẻ, số lượng lớn không chạm website; PBN GTV tự dựng bài bản được trỏ thẳng website như T1, PBN order ngoài từ T2 trở xuống; đợt T2 chỉ mở khi tầng ngay trên đã index.

**Ví dụ Đạt / Không Đạt:**
✅ Dự án nội bộ, Vincent duyệt aggressive: batch PBN 5 link theo đúng guardrail, tag riêng trong master list.
❌ Client GTV, batch lẫn 10 link web 2.0 spin "cho đa dạng" — không ai duyệt.

**Nguồn:** Training "Bí thuật backlink thất truyền" 27/09/2026 (người duyệt, luật PBN, mô hình stack — cập nhật 02/10/2026) · Chỉ đạo Vincent 07/2026 (không xóa tactic cũ — gắn gate) · `backlink-plan` v1.2 B3 (aggressive: SEO Lead xem trước, SEO Director chốt; PBN/parasite làm được cho khách khi đã duyệt) · Legacy: `Checklist triển khai Bosting Linkjuice.xlsx` sheets "plan PBN", "đi link PBN", "the 08 method", "10 minutes Tier 2", "web 2.0 articles brands", "RSS feedburner", "forum 2.0", "backlinks 3rd party".

---

### OF-09 — Đa dạng nền tảng + dofollow/nofollow + cap per domain

**Nhóm:** Chất lượng nguồn

**Tóm tắt:** Batch (cộng dồn tháng) phải đa dạng: nền tảng (guest post, báo, forum, social, blog cá nhân...), gốc domain unique, tỷ lệ dofollow/nofollow tự nhiên (nofollow vẫn cần — kích hoạt sự tự nhiên của profile), đích đến đa dạng. Không dồn >30-35% tổng link 1 đợt vào 1 domain; số link tối đa trên 1 domain theo plan (legacy PBN: 3-6 link/domain).

**Mô tả đầy đủ:**
1. Đếm phân bố batch theo: nền tảng / domain gốc / do-no / URL đích.
2. Anchor Google chỉ tính dofollow — nhưng profile 100% dofollow là footprint; social/forum là nguồn nofollow tự nhiên nhất.
3. Domain đã dùng nhiều batch trước → giảm ưu tiên (unique domain trong backlink).

**Ví dụ Đạt / Không Đạt:**
✅ Batch 20 link: 8 domain mới, 3 nền tảng, 15 do / 5 no, không domain nào >6 link tổng.
❌ 18/20 link cùng 1 báo, 100% dofollow.

**Nguồn:** `6. Tiêu chuẩn Triển khai backlinks.xlsx` ("unique domain trong backlink", "Số lượng backlink có thể triển khai trên một domain") · `4. Research & đánh giá backlinks.xlsx` sheet "2. Yếu tố đánh giá" mục 4 (đa dạng nền tảng/domain/anchor/đích đến) · `3. Link building offpage GTV.xlsx` B3 (lưu ý dofollow/nofollow) · `textlink-analyzer` ($CAP_PER_DOMAIN 30-35%).

---

## NHÓM 3 — CONTENT OFFPAGE (bài guest post / PR / bài đăng nguồn)

### OF-10 — Bài offpage target Phantom Keywords (allintitle <1.000 / <5.000)

**Nhóm:** Content offpage

**Tóm tắt:** Mỗi bài guest post/PR chọn topic theo **Phantom Keywords** — keyword ngách có search demand nhưng cạnh tranh title gần bằng 0: check `allintitle:"keyword"` — **<1.000 kết quả (chuẩn) / <5.000 (nới cho ngách rộng)**; ưu tiên volume 10-500, KD thấp. Bài offpage tự rank → backlink nằm trên bài CÓ traffic thật, giá trị gấp nhiều lần bài chết.

**Mô tả đầy đủ:**
1. Research phantom keywords cho cluster đang đẩy (Ahrefs volume 10-500, KD <2 tham chiếu; check allintitle từng key).
2. Topic bài offpage phải support anchor + trang đích (cùng cluster ngữ nghĩa) — anchor đặt trong bài phải "có lý" với topic.
3. Topic có thể trùng giữa các bài, content phải khác.
4. Bài PR/guest post nếu >2 bài/project → đăng lần lượt để internal link bài 1 → bài 2 → bài 3.

**Ví dụ Đạt / Không Đạt:**
✅ Bài PR "máy làm đá viên cho quán trà sữa nhỏ" — allintitle 340 kết quả, volume 90 → bài tự lên top, link về category máy làm đá.
❌ Bài PR target "máy làm đá" (allintitle 45.000) — bài không bao giờ rank, link nằm trên trang 0 traffic.

**Nguồn:** Yêu cầu Vincent (ngưỡng allintitle <1.000/<5.000) · Legacy: `Checklist triển khai Bosting Linkjuice.xlsx` sheet "guest post" ("Sử dụng bài viết phantom keywords"), sheet "10 minutes Tier 2" (ưu tiên đích có phantom keywords) · `3. Link building offpage GTV.xlsx` B7 ("Research phantom keywords và chọn cluster content") · Traffic User pptx slide "Ví dụ demo key techrum" (key 10-500, KD <2).

---

### OF-11 — Bài unique, không spin

**Nhóm:** Content offpage

**Tóm tắt:** Content offpage tier 1 (guest post, PR, bài PBN được duyệt) phải **unique 100% — không spin, không copy**. Kỹ thuật spin trong file legacy (forum spin từ 3 bài, web 2.0 copy y chang) chỉ tồn tại trong nhóm OF-08 risk-controlled; mặc định 2026 mọi bài đặt link là bài viết thật, đọc được, có giá trị độc lập.

**Mô tả đầy đủ:**
1. Bài ≥ độ dài tối thiểu theo kênh (tham chiếu legacy: ≥400 chữ PBN, ≥500 forum — bài guest post/PR thực tế nên 800+).
2. Check unique (Copyscape/tương đương hoặc so trực tiếp với bài gốc money site) — không dán lại bài money site.
3. Bài AI-gen phải qua chuẩn humanize + fact-check như content chính (route skill `humanizer` nếu cần).

**Ví dụ Đạt / Không Đạt:**
✅ Guest post 900 chữ viết riêng cho blog nguồn, dẫn số liệu riêng, không trùng bài nào trên money site.
❌ Lấy bài money site spin 30% từ đồng nghĩa rồi đăng 10 forum.

**Nguồn:** `Checklist triển khai Bosting Linkjuice.xlsx` sheet "đi link PBN" mục 7 ("Unquie, tối thiểu 400 chữ") — modernize: spin từng cho phép ở forum/web2.0 nay chuyển vào OF-08 gate.

---

### OF-12 — Entity brand nhất quán

**Nhóm:** Content offpage

**Tóm tắt:** Thông tin brand trong bài offpage phải nhất quán tuyệt đối với Entity Home: tên brand (đúng 1 cách viết chuẩn + biến thể đã khai báo), NAP (tên-địa chỉ-số điện thoại), mô tả dịch vụ, tên author. Bài offpage là citation — mỗi lần nhắc brand là 1 lần củng cố (hoặc phá) entity.

**Mô tả đầy đủ:**
1. Check tên brand trong bài + anchor brand khớp bộ biến thể chuẩn (vd "GTV SEO" / "gtvseo.com" — không tự chế "GTV Agency Seo").
2. Mention brand không link (entity mention) cũng tính — viết đúng chuẩn.
3. Bài PR có box giới thiệu doanh nghiệp → NAP khớp GMB/Entity Home.
4. Không trộn chiến dịch Entity (social stack, profile, citations) vào batch backlink — Entity là campaign riêng.

**Ví dụ Đạt / Không Đạt:**
✅ 5 bài PR cùng dùng đúng boilerplate brand 2 câu + NAP chuẩn.
❌ Mỗi báo viết tên công ty một kiểu, 2 bài sai số điện thoại.

**Nguồn:** `6. Tiêu chuẩn Triển khai backlinks.xlsx` ("Link mention (entity)") · `4. Research & đánh giá backlinks.xlsx` mục 5 Entity · `backlink-plan` B3 (Entity tách campaign riêng — quyết định GTV 2021) · wiki [[Entity Home]].

---

### OF-13 — 1 link money + anchor đúng plan; link phụ tự nhiên 🔴 P0

**Nhóm:** Content offpage

**Tóm tắt:** Mỗi bài offpage: **đúng 1 link về trang đích money/target** với anchor lấy từ anchor plan của batch (OF-03). Link phụ (nếu có) phải tự nhiên: link out tới nguồn uy tín cùng theme, hoặc về bài blog/social của brand — anchor brand/URL/generic, KHÔNG thêm anchor keyword thứ 2 về cùng domain.

**Mô tả đầy đủ:**
1. 1 bài = 1 anchor money duy nhất; các anchor trong batch không trùng nhau (rule "các anchor text phải khác nhau").
2. Link out uy tín ≥ số link về money site trong bài (nguyên tắc authority link legacy — giữ cho bài guest/PR: tối thiểu 1-2 link out nguồn uy tín cùng chủ đề).
3. Các link cách xa nhau trong bài (~200 chữ/link), link money nằm trong đoạn văn có ngữ cảnh (không ở author box trơ trọi, không sidebar — trừ chiến dịch textlink có plan riêng).
4. Keyword anchor exact/partial phải tồn tại trong content trang đích.

**Ví dụ Đạt / Không Đạt:**
✅ Bài 900 chữ: 1 anchor partial về category + 1 link out báo ngành + 1 link về bài blog brand (anchor title).
❌ 1 bài nhét 3 anchor keyword về 3 URL money cùng domain.

**Nguồn:** `Checklist triển khai Bosting Linkjuice.xlsx` sheet "đi link PBN" mục 3 (authority link ≥ link money, khoảng cách link, anchor khác nhau), mục 6 (mỗi 200 chữ/backlink) · `anchor-ratio-framework.md` Nguyên tắc 4 (keyword tồn tại trong trang đích).

---

### OF-14 — Co-occurrence + contextual link + onpage bài offpage

**Nhóm:** Content offpage

**Tóm tắt:** Anchor phải nằm trong ngữ cảnh: đoạn văn chứa anchor (± câu lân cận) chứa keyword mục tiêu/liên quan — "sự liên quan của bài với anchor càng cao, backlink càng mạnh". Anchor 3 phần `Mô tả trước + Từ khóa + Mô tả sau`; anchor generic không bao giờ đứng trơ. Bài offpage tối ưu onpage như bài SEO thường: title/URL chứa keyword lĩnh vực (không exact-dup), heading, ảnh có alt, schema nếu gắn được.

**Mô tả đầy đủ:**
1. Contextual link: backlink bao quanh bởi text (trên-dưới-trái-phải), nằm trong đoạn 100-200 chữ đúng chủ đề trang đích.
2. Co-occurrence: khi anchor KHÔNG phải keyword (brand/generic/naked) → chữ trước/sau anchor phải là keyword SEO — đây là cách nguồn yếu vẫn truyền relevance.
3. Title bài nguồn: chứa keyword lĩnh vực, keyword ở đầu, KHÔNG để chính xác 100% keyword cần SEO; URL dùng biến thể đồng nghĩa, ≤70 ký tự.
4. Ảnh trong bài đặt tên file + alt; hỏi gắn schema Article cho bài nếu báo cho phép.

**Ví dụ Đạt / Không Đạt:**
✅ "…các dòng *đèn led panel* tiết kiệm điện như [đèn led panel Rạng Đông] đang được ưa chuộng tại nhà xưởng…" — keyword vây quanh anchor.
❌ "Xem thêm: [tại đây]" cuối bài, đoạn xung quanh nói chuyện khác.

**Nguồn:** `Checklist triển khai Bosting Linkjuice.xlsx` sheet "Chiến thuật sử dụng anchor text" (Contextual links + Co-occurrence), sheet "đi link PBN" mục 5 (title/URL/onpage) · `anchor-ratio-framework.md` Nguyên tắc 4b · `3. Link building offpage GTV.xlsx` B7.3 (onpage + schema bài offpage).

---

## NHÓM 4 — TEXTLINK PR (T7-T8)

### OF-15 — URL báo lọc slug-only (route textlink-analyzer)

**Nhóm:** Textlink PR

**Tóm tắt:** Chiến dịch textlink PR số lớn: danh sách URL bài báo đặt link phải qua skill `textlink-analyzer` — lọc **slug-only bằng script** (không crawl, không lọc tay): term-set 3 tầng (A trang đích / B topic / C ngành) + negative terms, có dạng không dấu; mỗi URL giữ `matched_terms` làm evidence; cộng điểm URL có backlink trỏ tới nếu có data.

**Mô tả đầy đủ:**
1. Batch textlink → phải có output CSV từ textlink-analyzer: `url | domain | tier | score | matched_terms`.
2. Phân bổ đúng tier: A → trang đích money/category tương ứng; B → category tầng 1; C → homepage/brand.
3. Vincent/Lead spot-check mẫu URL bằng matched_terms trước khi gửi báo.
4. Negative terms (chinh-tri, tai-nan, phap-luat…) đã loại — brand safety.

**Ví dụ Đạt / Không Đạt:**
✅ Export 40.000 URL 5 báo → script lọc còn 1.800 URL tier A-C kèm evidence, phân bổ theo quota.
❌ Gửi báo "chọn giúp URL liên quan" hoặc lọc tay 500 URL đầu danh sách.

**Nguồn:** skill `textlink-analyzer` B1-B4 (quy trình gốc chiến dịch Rạng Đông Mall/Elmall).

---

### OF-16 — Textlink PR: tỷ lệ anchor an toàn per đợt

**Nhóm:** Textlink PR

**Tóm tắt:** Anchor plan textlink theo đúng canonical framework (OF-03 áp cho cả textlink): bảng phân bổ per trang đích trong ngưỡng (Exact ≤8% homepage / ≤10% category), format 3 phần, không lặp 1 anchor y hệt quá ~10 lần/đợt/domain báo, tổng % lệch target >2% → flag và cân lại trước khi gửi.

**Mô tả đầy đủ:**
1. Bảng plan đủ cột vận hành: `Mô tả trước | Từ khóa | Mô tả sau | URL đích | Dofollow | Số link | Volume | Anchor Type | URL đi link`.
2. Site giai đoạn đầu → co nhóm từ khóa về ~30%, Exact ≈ 0-3% (Lớp 1 framework thắng bảng mặc định).
3. Velocity textlink rải theo tuần — không bung cả đợt 1 ngày.

**Ví dụ Đạt / Không Đạt:**
✅ Đợt 1.200 link: exact 6,8% homepage-mix, mỗi anchor non-brand ≤10 lần/domain, rải 5 tuần.
❌ 1 anchor exact lặp 60 lần trên cùng 1 báo trong 3 ngày.

**Nguồn:** `textlink-analyzer` B5-B6 + `anchor-ratio-framework.md` (bản canonical thắng khi xung đột).

---

### OF-17 — Textlink PR: tracking file cập nhật theo đợt

**Nhóm:** Textlink PR

**Tóm tắt:** Mỗi đợt textlink có sheet tracking riêng cập nhật NGAY khi báo đặt xong: URL bài báo, anchor, trang đích, ngày đặt, dofollow, trạng thái live/index. Giữ danh sách domain đầy đủ — điều kiện để disavow được khi cần (risk mitigation bắt buộc của chiến dịch textlink).

**Mô tả đầy đủ:**
1. Sheet theo format vận hành GTV (cột như OF-16).
2. Đối chiếu số link báo báo cáo vs số link verify được — lệch → yêu cầu báo bổ sung.
3. Link die/gỡ trong đợt → ghi trạng thái, cộng vào quota đòi bù.

**Ví dụ Đạt / Không Đạt:**
✅ Sheet đợt 2 cập nhật 100% trạng thái trong 48h sau khi báo confirm.
❌ "Báo bảo đặt xong rồi" — không có file đối chiếu.

**Nguồn:** `textlink-analyzer` Risk note (track theo đợt, giữ danh sách domain để disavow) · `Checklist triển khai Bosting Linkjuice.xlsx` sheet "đi link PBN" mục 8 (lưu link vào file dự án).

---

## NHÓM 5 — POST-BATCH VERIFY

### OF-18 — Link live + index sau X ngày

**Nhóm:** Post-batch verify

**Tóm tắt:** Sau khi bắn batch: verify 100% link **live** (đúng anchor, đúng URL đích, đúng dofollow như plan) trong 3-7 ngày; verify **index** sau 7-14 ngày (mặc định X=14, chốt theo plan). Link chưa index → đưa vào công cụ/quy trình index; link die → đòi bù nhà cung cấp.

**Mô tả đầy đủ:**
1. Check live: tồn tại, không bị sửa anchor, không bị gắn thêm nofollow/sponsored ngoài thỏa thuận, không redirect.
2. Check index: `site:url` hoặc tool; toàn bộ link batch thống kê và đẩy index (quy trình legacy: "thống kê lại và bỏ vô công cụ index hàng loạt").
3. Tỷ lệ index thấp bất thường của 1 nguồn (<50% sau 14 ngày) → hạ điểm nguồn cho batch sau.

**Ví dụ Đạt / Không Đạt:**
✅ Batch 20 link: ngày 5 verify 20/20 live; ngày 14: 17/20 indexed, 3 link đẩy index lại.
❌ Không verify — 1 tháng sau phát hiện 6 link bị gỡ, 4 link bị đổi thành nofollow.

**Nguồn:** `Checklist triển khai Bosting Linkjuice.xlsx` (mục "Index backlinks" lặp lại ở mọi sheet chiến thuật) · `3. Link building offpage GTV.xlsx` B10 (Index backlink sau triển khai hoặc song song) · `3. Link building offpage GTV.xlsx` B5 (thương lượng đặt link 3-6 tháng — cơ sở đòi bù).

---

### OF-19 — Anchor thực tế vs plan

**Nhóm:** Post-batch verify

**Tóm tắt:** Sau verify live: đối chiếu bảng anchor THỰC TẾ của batch (+ cộng dồn tháng) vs anchor plan. Lệch >2% ở bất kỳ anchor type nào, hoặc exact vượt trần → flag; batch sau phải bù bằng pillow wave (branded/generic/naked), không disavow trừ khi negative rõ.

**Mô tả đầy đủ:**
1. Đếm anchor thực tế từ tracking sheet (không tin plan — báo/CTV hay tự đổi anchor).
2. So với consensus SERP định kỳ: mình lệch xa top 3-5 (vd top 3 ~3% exact, mình 12%) = red flag.
3. Ghi kết quả đối chiếu vào batch log để Lead review.

**Ví dụ Đạt / Không Đạt:**
✅ Plan exact 7% — thực tế 8,5% do báo đổi 2 anchor → batch sau bù 5 link brand/naked.
❌ Không đối chiếu, 3 tháng sau audit thấy exact 14%.

**Nguồn:** `anchor-ratio-framework.md` Nguyên tắc 5 (chẩn đoán & sửa, pillow wave) · `Checklist triển khai Bosting Linkjuice.xlsx` sheet "anchor text & plan" mục 2.0 (kiểm tra mật độ anchor hiện tại + kiểm tra anchor đã đi trong file dự án).

---

### OF-20 — Master list backlink cập nhật (bàn giao T10) 🔴 P0

**Nhóm:** Post-batch verify

**Tóm tắt:** Mọi link của batch (kể cả free/forum/social) vào **master list backlink** của dự án ngay khi verify xong: `Domain/nguồn | Dạng | Giá | Target URL | Anchor type | Anchor 3 phần | Tháng | Trạng thái (+ tag risk-controlled nếu OF-08)`. Master list là tài sản bàn giao T10 — thiếu = batch chưa đóng.

**Mô tả đầy đủ:**
1. Format khớp CSV plan của `backlink-plan` B6 — 1 dòng 1 link.
2. Link risk-controlled (OF-08) và textlink (OF-17) tag riêng — phục vụ disavow chọn lọc sau này.
3. Cuối tháng: đối chiếu master list vs quota plan — báo Lead số thực đi / kế hoạch.

**Ví dụ Đạt / Không Đạt:**
✅ Master list realtime, cuối T8 đối chiếu: 96/100 link plan, 4 link dời T9 có ghi chú.
❌ Mỗi CTV giữ file riêng, đến T10 gom không đủ, khách hỏi không trả lời được link nằm đâu.

**Nguồn:** `backlink-plan` B6 (format CSV vận hành — file plan Vincent video 2021 + sheet Rạng Đông) · `Checklist triển khai Bosting Linkjuice.xlsx` sheet "đi link PBN" mục 8.

---

### OF-21 — Review kết quả batch + điều kiện dừng/đổi hướng

**Nhóm:** Post-batch verify

**Tóm tắt:** Mỗi mốc review tháng: đo keyword target (kỳ vọng pos 4-20 → top), RD growth vs đối thủ. Keyword không nhúc nhích sau 2-3 tháng link đúng plan → KHÔNG link thêm — quay lại nghi vấn content/structure (điều kiện dừng trong plan). Kỳ vọng hiệu quả backlink 1-6 tháng — ghi rõ để quản trị kỳ vọng.

**Mô tả đầy đủ:**
1. Batch log link với ranking snapshot tại thời điểm bắn → so tại mốc review.
2. Trigger dừng/đổi hướng lấy từ plan section 6 (Tracking & review) — không tự chế.
3. Kết quả + bài học filed về `12-feedback-lessons` của SEO Production instance (nguồn nào ngon/rác, anchor nào hiệu quả).

**Ví dụ Đạt / Không Đạt:**
✅ Sau 2 tháng cluster A pos 8→4; cluster B đứng im → dừng link cluster B, mở audit content.
❌ Keyword đứng im 4 tháng vẫn tăng gấp đôi ngân sách link.

**Nguồn:** `backlink-plan` B6 mục 6 + Anti-pattern "plan không có điều kiện dừng" · `6. Tiêu chuẩn Triển khai backlinks.xlsx` ("Thời gian hiệu quả của backlink").

---

## Ghi chú nguồn legacy

| File legacy | Trạng thái đọc | Dùng cho |
|---|---|---|
| `Checklist triển khai Bosting Linkjuice.xlsx` (16 sheets, ~2017-2019) | ✅ Đọc đầy đủ | OF-02/03/04/07/08/10/11/13/14/17/18/19 — tactic PBN/forum/web2.0/RSS đưa vào OF-08 gate; contextual/co-occurrence + guardrail giữ nguyên giá trị |
| `6. Tiêu chuẩn Triển khai backlinks.xlsx` (2020) | ⚠ Đọc một phần — sheet chỉ còn TÊN 28 nguyên tắc (T-T-T, cân bằng mật độ, tiến độ tăng dần, unique domain, first link count, link echo, mention, schema, iframe…), cột "Cụ thể tiêu chuẩn" phần lớn trống | OF-02/04/09/12/21 — dùng tên nguyên tắc; chi tiết lấy từ file 2025 + framework hiện hành |
| `4. Research & đánh giá backlinks.xlsx` (2025) | ✅ Đọc đầy đủ | OF-05/06/12 — hệ đánh giá Theme-Trust-Traffic + phân loại 1-6 + footprint |
| `3. Link building offpage GTV.xlsx` (2025) | ✅ Đọc đầy đủ | OF-01/02/03/04/09/10/14/18 — quy trình B1-B10; bảng anchor 2019/2022 KHÔNG dùng làm chuẩn (canonical framework thay thế) |
