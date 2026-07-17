---
template: backlink-campaign
ws: 07-offpage
cong_doan: 20 (nền + guest post phantom T4-T5) · 26 (đẩy mạnh + textlink PR T6-T7)
skill: backlink-plan · thực thi textlink PR → textlink-analyzer
input_bat_buoc: research file (backlink-research) · gate-offpage-decision (bắt buộc với #26)
naming: "{{CLIENT}}_backlink-campaign_v{{N}}.md"
version: v1
---

# {{CLIENT}} — Backlink Campaign · Đợt: {{NEN_T4_T5 | DAY_MANH_T6_T7}}

## 0. Phạm vi & căn cứ

| Trường | Giá trị |
|---|---|
| Công đoạn / tháng chạy | #{{20|26}} / T{{...}} |
| Gate verdict (link file gate-offpage-decision, bắt buộc với #26) | |
| Research file | |
| Risk level | conservative (default GTV) / moderate / aggressive (chỉ khi Vincent duyệt rõ) |
| Budget duyệt | {{VND}}/tháng |

## 1. Targets

| URL | Vai trò (home/supporting/category/money) | Lý do (cite research §) | Keyword pos 4-20 | Quota link | Climb cost (nếu money page) |
|---|---|---|---|---|---|

Luật: money page fail link-gap test → route supporting content. Target chưa có internal link 2 chiều → chưa bắn.

## 2. Anchor plan per target

Theo `skills/backlink-plan/references/anchor-ratio-framework.md` — 4 lớp đúng thứ tự: giai đoạn trust → SERP consensus → GTV prior per page type → Authority-Aggression.

| Target URL | Brand thuần | Partial | Naked/URL | Brand+KW | Exact (≤8-10%) | Generic | Semantic | Title | Tổng |
|---|---|---|---|---|---|---|---|---|---|

Luật anchor:
1. Anchor map 20-30 variations/target, rotate — không lặp anchor non-brand trong cùng tháng.
2. Format 3 phần "Mô tả trước + Từ khóa + Mô tả sau"; co-occurrence quanh anchor bắt buộc; keyword exact/partial phải tồn tại trong content trang đích; lowercase cho non-brand.
3. Nguồn <DR40 chỉ nhận brand/generic/naked; exact chỉ đặt ở DR60-85+ editorial đúng theme.

## 3. Method mix

| Method | Số link/tháng | Target nhóm | Ghi chú |
|---|---|---|---|
| Guest post blog đúng theme | | | |
| Textlink PR (→ textlink-analyzer, kèm quota + ratio per target) | | | |
| Linkable asset / data study | | | |
| Reclaim / unlinked mention | | | |
| Niche edit / digital PR (chỉ moderate+) | | | |

Luật: Entity/foundational (social, profile, citations) tách sang Entity campaign — KHÔNG trộn vào đây. KHÔNG đề xuất PBN/parasite mặc định cho client GTV.

## 4. Lịch tháng — velocity theo nhịp đối thủ

| Tháng | Free/foundational | Paid | Tổng RD mới | Nhịp đối thủ (research §2) | Milestone review |
|---|---|---|---|---|---|

Luật: nhịp chuẩn = RD/tháng trung bình đối thủ; site mới bắt đầu ½ nhịp. Trong tháng: free trước → paid sau. Không vượt nhịp đối thủ nhiều lần.

## 5. Budget

| Method | Đơn giá | Số lượng | Thành tiền/tháng | Tổng đợt |
|---|---|---|---|---|

## 6. Tracking & review

| Mốc đo | Chỉ số | Cadence | Điều kiện dừng/đổi hướng |
|---|---|---|---|
| Ranking | keyword pos 4-20 → top | tháng | link {{N}} tháng mà keyword không nhúc nhích → dừng, quay lại soi content |
| RD growth | RD mình vs nhịp đối thủ | tháng | |
| Anchor profile | % 8 loại vs khung giai đoạn | quý | exact vượt trần → dilute bằng pillow wave brand/generic/naked |

## 7. Risk log

1. Exact cap ≤8-10% — trần cứng mọi giai đoạn; ratio = internal benchmark chống footprint, không phải safe harbor với Google.
2. Footprint: không lặp 1 anchor y hệt quá ~10 lần/đợt/domain.
3. Velocity cap: giữ trong nhịp mục 4 — không "bung" link; disavow chỉ khi negative impact rõ, không disavow phòng ngừa.

## Sheet vận hành (mỗi dòng 1 link dự kiến)

`Domain/nguồn | Dạng (free/guest/niche-edit/PR) | Giá | Target URL | Anchor type | Anchor (3 phần) | Tháng | Trạng thái`

## Done-criteria

- [ ] Mục 0 đủ: gate verdict (với #26) + research file + risk level + budget duyệt.
- [ ] Quota mục 1 khớp tổng mục 3 và mục 4; mọi money page qua link-gap test.
- [ ] Anchor % per target trong khung giai đoạn, exact ≤8-10%.
- [ ] Có sheet vận hành đủ cột; handoff textlink PR ghi rõ quota + ratio.
- [ ] Có điều kiện dừng/đổi hướng ở mục 6; index + log cập nhật (op `work`).
