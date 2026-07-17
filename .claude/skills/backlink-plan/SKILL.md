---
name: backlink-plan
description: "Lập kế hoạch backlink toàn diện — DECISION layer của bộ skill backlink. Use when: (1) 'lập plan backlink cho [domain/client]', 'backlink recommend', 'nên đi link vào đâu', 'chọn target URL + anchor text'; (2) đã có research data (từ skill backlink-research hoặc data user cấp) cần chuyển thành kế hoạch: gate có-cần-link-không, target URLs, anchor plan per target, method mix, velocity, budget; (3) cần file plan spreadsheet format vận hành GTV. Nguyên tắc: gate 90%-site-không-cần-backlink → money-page link-gap test → supporting-content-first + lăng kính internal link → anchor SERP-consensus (GTV prior làm fallback, references/anchor-ratio-framework.md) → velocity theo nhịp đối thủ. KHÔNG dùng cho: thu thập data (→ backlink-research), thực thi lọc URL textlink PR (→ textlink-analyzer)."
metadata:
  version: "1.1"
---

# Backlink Plan — Decision Layer

Chuyển research data thành **kế hoạch backlink hành động được**: gate → target → anchor → method → velocity → budget → tracking. Nền: process Vincent 2021 ([[sources/backlink-a-z-video-vincent-2021]]) + consensus ngành 2026 ([[sources/research-2026-07-backlink-methods]]).

## Bộ 3 skill backlink

DATA `backlink-research` → **DECISION ✅ skill này** → EXECUTION `textlink-analyzer` (format textlink PR) / outreach team (guest post, digital PR, niche edit).

## Input

**Required:**
- `$RESEARCH` — research file từ `backlink-research` (hoặc data tương đương user cấp: profile/gap/anchors/velocity). Thiếu → chạy `backlink-research` trước, không plan chay.
- `$SITE_CONTEXT` — cấu trúc site + internal link map (cây phân tầng) + trạng thái content ("content/structure đã chuẩn chưa?")

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
4. **Ưu tiên theo cơ hội**: trang có keyword đang rank **vị trí 4-20, volume ≥100** = quick win.
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
- **Aggressive (chỉ khi Vincent duyệt rõ):** flag rủi ro từng hạng mục — KHÔNG mặc định đề xuất PBN/parasite (GTV không làm cho khách).
- **Entity/foundational** (social, profile, citations) → tách sang Entity campaign, KHÔNG trộn (quyết định GTV 2021).

### Bước 4 — Velocity & timeline
- Nhịp chuẩn = **RD/tháng trung bình của đối thủ** (research §2); site mới → bắt đầu ½ nhịp đó (Floate).
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
Kèm **CSV/sheet** mỗi dòng 1 link dự kiến: `Domain/nguồn | Dạng (free/guest/niche-edit/PR) | Giá | Target URL | Anchor type | Anchor (3 phần) | Tháng | Trạng thái` — đúng format file plan Vincent dùng (video 2021 + sheet Rạng Đông).

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
- Đề xuất PBN/parasite mặc định cho client GTV.
- Plan không có điều kiện dừng — link mãi cho keyword không nhúc nhích thay vì quay lại sửa content.

## References & wiki

- [references/anchor-ratio-framework.md](references/anchor-ratio-framework.md) — **canonical anchor framework** (GTV prior + SERP-consensus workflow + Authority-Aggression; textlink-analyzer trỏ về đây)
- Wiki: [[Link Building]] · [[TrustRank]] · [[Internal Linking Rules and Strategy]] (lăng kính/tán xạ) · [[sources/backlink-a-z-video-vincent-2021]] · [[sources/research-2026-07-backlink-methods]]
