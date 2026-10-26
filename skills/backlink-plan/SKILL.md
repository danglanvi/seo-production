---
name: backlink-plan
description: "Lập kế hoạch backlink toàn diện — DECISION layer của bộ skill backlink. Use when: (1) 'lập plan backlink cho [domain/client]', 'backlink recommend', 'nên đi link vào đâu', 'chọn target URL + anchor text'."
metadata:
  version: "1.3.1"
---

# Backlink Plan — Decision Layer

Chuyển research data thành **kế hoạch backlink hành động được**: gate → target → anchor → method → velocity → budget → tracking. Nền: process Vincent 2021 ([[sources/backlink-a-z-video-vincent-2021]]) + consensus ngành 2026 ([[sources/research-2026-07-backlink-methods]]).

## Bộ 3 skill backlink

DATA `backlink-research` → **DECISION ✅ skill này** → EXECUTION `textlink-analyzer` (format textlink PR) / outreach team (guest post, digital PR, niche edit).

> **📌 Backlog (24/07/2026, Vincent duyệt): module "External Topical Map"** — lớp off-page KHÁC link thường: bài trên site bên thứ ba (ưu tiên locale news) target query template pass QDP, pass tín hiệu quality/click/historical qua NavBoost + build claims/co-occurrences consensus cho GBP + AI answers (bảng attribute/predicate/contextual-phrase/measurement-unit; Gibberish guard). CHƯA build — chờ Koray ra bài anchor text patent US10210256B2. Nền lý thuyết: `wiki/concepts/frameworks/Surround Sound.md` mục External Topical Map + `wiki/sources/local-seo-topical-authority-sel-koray.md` L378-553.

## Input

**Required:**
- `$RESEARCH` — research file từ `backlink-research` (hoặc data tương đương user cấp: profile/gap/anchors/velocity). Thiếu → chạy `backlink-research` trước, không plan chay.
- `$SITE_CONTEXT` — cấu trúc site + internal link map (cây phân tầng) + trạng thái content ("content/structure đã chuẩn chưa?")

**Công cụ:** `scripts/plan_tools.py` (thư viện chuẩn) có 3 lệnh: `velocity`, `quickwins`, `check`. Test: `tests/test_plan_tools.py`. Dữ liệu Ahrefs lấy qua connector theo `backlink-research/references/ahrefs-mcp.md`.

**Optional:** `$MONEY_PAGES` (URLs SEO mong muốn — không có thì skill tự đề xuất "URLs tốt để target" từ data) · `$BUDGET` (VND/tháng) · `$RATIO` (override anchor prior) · `$TIMELINE` · `$RISK_LEVEL` (conservative default / moderate / aggressive — quyết định method mix)

## Workflow 7 bước

### Bước 0 — GATE: có cần backlink không? (quyết định số 1)
Theo Vincent: 80-90% dự án top KHÔNG cần chiến dịch backlink; site không lên top → 90-99% do content/cấu trúc/UX.
- Content + structure chưa chuẩn → **HALT**: "Chưa đi link — fix content/structure trước" + list việc (route seo-onpage / SOM / SCW).
- Đã chuẩn + có dấu hiệu cần (mất cân đối content/RD; link gap rõ trong research; keyword kẹt trang 2) → proceed, ghi rõ lý do.

### Bước 1 — Target URL selection (WHERE)
Từ `$SITE_CONTEXT` + research:
1. **Money-page link-gap test** (đã có ở research §5): đối thủ **0 quality links vào money page** → KHÔNG link thẳng money page → route **supporting content**; gap = N RDs → climb cost, cân economics (gap quá đắt → đổi target/cluster).
2. **Chọn trang "lăng kính"** (Vincent): tầng thấp trong cấu trúc, intent cụ thể, cạnh tranh thấp, internal link dày 2 chiều (lên cha + xuống con) → sức mạnh tán xạ kéo cả cluster. Không có internal link 2 chiều → yêu cầu fix internal trước khi bắn.
3. **Site mới** (chưa đủ authority nền): homepage trước với pillow anchors (brand/naked/generic), gate sau 5-10 bài content.
4. **Ưu tiên theo cơ hội**: trang có keyword đang rank **vị trí 4-20, volume ≥100** = quick win. Ahrefs `site-explorer-organic-keywords` (where `best_position` 4–20, `volume` ≥ 100) → `plan_tools.py quickwins --file <json> --out <W>/quickwins.md`. Kiểm mã HTTP và canonical của mọi URL trước khi chọn: Ahrefs còn giữ URL đã 410 hoặc 301. Lệnh loại khỏi bảng các URL có chữ hoa trong path hoặc `%20`: thường là breadcrumb danh mục Ahrefs ghi thành URL.
Output: bảng target — URL | vai trò (home/supporting/category/money) | lý do chọn | keyword pos 4-20 | quota link.

### Bước 2 — Anchor plan per target
Theo [references/anchor-ratio-framework.md](references/anchor-ratio-framework.md) (canonical) — áp 4 lớp ĐÚNG THỨ TỰ:
1. **Lớp 1 — Giai đoạn trust của site** (mô hình 3 giai đoạn Vincent): xác định từ research §1 → chốt tổng AN TOÀN vs TỪ KHÓA (GĐ1: ~70/30 · GĐ2: 40-50/50-60 · GĐ3: 35-45/55-65). Nghi ngờ → chọn giai đoạn thấp hơn.
2. **Lớp 2 — SERP consensus** (research §4): "Mimic the winners" — tinh chỉnh trong khung giai đoạn.
3. **Lớp 3 — GTV prior per page type** (bảng reference) phân bổ chi tiết 8 loại; Exact ≤8-10% trần cứng MỌI giai đoạn.
4. **Lớp 4 — Authority-Aggression**: nguồn <DR40 chỉ nhận branded/generic/naked; exact chỉ ở nguồn mạnh đúng theme (≡ rule Vincent 2021). Anchor map 20-30 variations/target, không lặp non-brand trong tháng; format 3 phần + co-occurrence quanh anchor (bắt buộc).

### Bước 3 — Method mix
Chọn theo mục tiêu + `$RISK_LEVEL` + budget (evidence 2026: digital PR #1; niche edit > guest post mới; taxonomy đầy đủ ở [[Link Building]]):
- **Conservative (default, client GTV):** guest post blog cá nhân đúng theme + textlink PR (→ `textlink-analyzer`) + linkable asset/data study + reclaim/unlinked mention.
- **Moderate:** + niche edit trên aged pages + digital PR local.
- **Aggressive (SEO Lead xem trước, SEO Director chốt):** PBN, parasite, mô hình stack (DAS, TAS, 08 method, báo có buffer), textlink báo ở trang chủ/chuyên mục/sitewide. **Làm được cho khách** khi phương án đã duyệt (Vincent chốt 02/10/2026); không tự đưa vào plan khi `$RISK_LEVEL` chưa là aggressive. Flag rủi ro từng hạng mục và đặt đúng tầng: PBN GTV tự dựng bài bản (content thật, có traffic) trỏ thẳng money page như T1; PBN order ngoài luôn từ T2 trở xuống; parasite trỏ vào tài sản T1, không trỏ thẳng money page; link rẻ số lượng lớn chỉ chạm tầng đệm. Mỗi hạng mục ghi điều kiện dừng và tag `risk-controlled` trong CSV. Luật thiết kế, chuẩn tài sản, đo ba tầng: SOP 12 `12-backlink-stack-models.md` (wiki Semantic SEO `sop/`; repo Production `02-raw/knowledge/sop/`).
- **Entity/foundational** (social, profile, citations) → tách sang Entity campaign, KHÔNG trộn (quyết định GTV 2021).

### Bước 4 — Velocity & timeline
- Nhịp chuẩn = **RD mới không spam còn sống/tháng của đối thủ, lấy trung vị** (research §2); site mới → bắt đầu ½ nhịp đó (Floate).
- Lấy số: Ahrefs `site-explorer-referring-domains` (`is_spam` false, `traffic_domain` > 0, `first_seen` 12 tháng, `history=all_time`) → `plan_tools.py velocity --file <rdnew_*.json>... --mine <domain> --since <YYYY-MM> --until <YYYY-MM> [--new-site]`. Không dùng `refdomains-history` (số ròng, gồm spam) và không dùng trung bình (tháng bùng kéo lệch).
- Đơn vị vận hành = **tháng**; trình tự trong tháng: free/foundational trước → paid sau (Vincent); kỳ vọng kết quả 1-6 tháng — ghi rõ vào plan để quản trị kỳ vọng client.

### Bước 5 — Budget
- Đơn giá tham chiếu: VN guest post (case GTV 2021: 600k-3,5tr — cập nhật giá hiện tại khi chạy); quốc tế 2026: $300+/link phổ biến, $500+ = 47% thị trường.
- Triết lý Vincent: "1 link 1 triệu đúng chuẩn > gói 5-6 triệu" — phân bổ theo chất lượng, không theo số lượng; tổng theo `$BUDGET`, thiếu thì đề xuất 2 phương án (tối thiểu khả thi / khuyến nghị).

### Bước 6 — Output: File plan (format vận hành GTV)

```markdown
# Backlink Plan — [client/domain] · [timeline] · risk: [level]
## 0. Gate verdict + lý do đi link
## 1. Targets: URL | vai trò | lý do | quota | climb cost (nếu money page)
## 2. Anchor plan per target: bảng phân bổ 8 loại + anchor map mẫu (theo consensus/prior + Authority-Aggression)
## 3. Method mix + phân bổ số link per method per tháng
## 4. Lịch tháng: velocity + trình tự (free → paid) + milestone review
## 5. Budget: per method + per target + tổng
## 6. Tracking & review: mốc đo (ranking pos 4-20 → top; RD growth vs đối thủ), cadence tháng; điều kiện dừng/đổi hướng
## 7. Risk log: exact cap, footprint rules, velocity cap, disavow policy (chỉ khi negative rõ)
## Handoff: textlink PR → skill textlink-analyzer (kèm quota + ratio per target); outreach → team
```
Kèm **CSV/sheet** mỗi dòng 1 link dự kiến: `Domain/nguồn | Dạng (free/guest/niche-edit/PR) | Giá | Target URL | Anchor type | Anchor (3 phần) | Tháng | Trạng thái` — đúng format file plan Vincent dùng (video 2021 + sheet Rạng Đông). Thêm cột `DR` khi đã biết nguồn.

Chạy `plan_tools.py check --csv <plan.csv> --stage <1|2|3> --out <W>/anchor-check.md` trước khi trình. Lệnh kiểm khung giai đoạn, trần exact, anchor non-brand lặp trong tháng và luật DR nguồn. Có FAIL thì sửa CSV.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:

- [ ] Gate cite money-page link-gap test của research §5. Nguồn lỗi: research gtvseo.com 19/10/2026 chưa có §5, gate không đủ evidence.
- [ ] Nhịp lấy từ RD mới không spam còn sống, trung vị. Nguồn lỗi: `refdomains-history` của gtvseo.com +133 RD/tháng gồm spam; seovip.vn có khoảng 250 RD mới trong 3 ngày 10/2025.
- [ ] Mọi target URL trả 200 và tự canonical. Nguồn lỗi: 8 URL Ahrefs ghi đang rank của gtvseo.com trả 410 hoặc 301 (19/10/2026).
- [ ] `plan_tools.py check` không FAIL. Exact ≤ 8–10% ở cả plan và từng target. Nguồn: `references/anchor-ratio-framework.md`.
- [ ] Nguồn dưới DR40 chỉ nhận brand, generic, naked. Nguồn: luật Vincent 2021 và Floate 2026.
- [ ] Mỗi dòng budget có đơn giá × số lượng × nguồn giá. Nguồn: nội quy trạm 07-offpage.
- [ ] Có điều kiện dừng hoặc đổi hướng. Nguồn: anti-pattern "link mãi cho keyword không nhúc nhích".

## Phân việc model

| Năng lực | Việc | Quyết định |
|---|---|---|
| Code (`plan_tools.py`) | nhịp, quick win, kiểm anchor theo khung | dùng |
| Claude | gate, chọn target sau khi đọc trang, anchor 3 phần, co-occurrence, budget | dùng |
| EmbeddingGemma | từ khoá exact/partial có trong trang đích (luật 4 của framework) | chưa: cần store của site; dùng `site-vector-index` khi plan có trên 30 dòng |
| Jev | độ tự nhiên của anchor 3 phần | chưa: chưa có rubric và gold |
| GLM Flash | — | không cần |

## Behavior Gates

- **#1 Think Before:** báo verdict Gate B0 + khung plan trước khi viết chi tiết; `$MONEY_PAGES` thiếu → đề xuất targets, chờ Vincent chốt.
- **#2 Evidence:** mọi quyết định cite research data (§ nào) hoặc nguyên tắc wiki — không phán chay.
- **#3 Surgical:** plan ≠ thực thi — không outreach, không đặt link, không sửa site; đề xuất fix internal link chỉ ghi handoff.
- **#4 Goal-driven:** đủ 8 section + CSV; quota khớp tổng; anchor % trong ngưỡng framework.

## Anti-patterns

- Plan không có Gate B0 (đi link cho site content chưa chuẩn = đốt tiền — lỗi #1 Vincent chỉ ra).
- Bắn thẳng money page khi đối thủ không có link vào đó (fail link-gap test).
- Anchor ratio cứng bỏ qua SERP consensus; exact vượt trần; lặp anchor trong tháng.
- Trộn Entity campaign vào backlink plan.
- Velocity vượt nhịp đối thủ nhiều lần ("bung 5.000 link 1 ngày").
- Đưa PBN/parasite/mô hình stack vào plan khi `$RISK_LEVEL` chưa là aggressive hoặc chưa có SEO Lead xem và SEO Director chốt.
- PBN order ngoài, parasite hoặc link rẻ số lượng lớn trỏ thẳng money page.
- Plan không có điều kiện dừng — link mãi cho keyword không nhúc nhích thay vì quay lại sửa content.
- Lấy nhịp từ RD ròng hoặc trung bình tháng khi đối thủ có tháng bùng spam.

## References & wiki

- [references/anchor-ratio-framework.md](references/anchor-ratio-framework.md) — **canonical anchor framework** (GTV prior + SERP-consensus workflow + Authority-Aggression; textlink-analyzer trỏ về đây)
- Wiki: [[Link Building]] · [[TrustRank]] · [[Internal Linking Rules and Strategy]] (lăng kính/tán xạ) · [[sources/backlink-a-z-video-vincent-2021]] · [[sources/research-2026-07-backlink-methods]]

## Changelog

- v1.3.1 (2026-10-19): `quickwins` loại URL lạ (chữ hoa trong path, `%20`) khỏi bảng target, liệt kê riêng. Nguồn: phiên Logfile đối chiếu log gtvseo.com, các URL /SEO/... là breadcrumb.
- v1.3.0 (2026-10-19): `scripts/plan_tools.py` (velocity, quickwins, check) và test offline; nhịp chuẩn đổi sang trung vị RD mới không spam còn sống; tự phản biện; phân việc model. Lượt thử dữ liệu gtvseo.com và 4 agency.
