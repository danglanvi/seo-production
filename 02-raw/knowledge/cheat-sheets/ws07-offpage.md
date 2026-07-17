# Cheat-sheet WS07 — Offpage (Backlink)

> Chưng cất từ `skills/backlink-plan/SKILL.md` + `skills/backlink-plan/references/anchor-ratio-framework.md` — sync 2026-07-17. Ratio trong file = internal benchmark giám sát footprint, KHÔNG phải safe harbor với Google.

## 1. Mục tiêu WS

Chỉ đi link khi có evidence cần link; khi đi thì đúng target, đúng anchor, đúng velocity, đúng budget — có điều kiện dừng.

- Công đoạn phụ trách: **#20** (Backlink nền + guest post, T4-T5) · **#25◇** (Gate Offpage — Lưu đồ B, T6) · **#26** (Backlink đẩy mạnh + textlink PR, đỉnh T6-T7).

## 2. Input / Output

| Input | Output |
|---|---|
| Research data từ `backlink-research` (profile/gap/anchors/velocity) — thiếu thì KHÔNG plan chay | Gate verdict → `_TEMPLATES/gate-offpage-decision.md`, lưu `07-offpage/` |
| Cấu trúc site + internal link map + trạng thái content | Backlink campaign plan + CSV per-link → `_TEMPLATES/backlink-campaign.md` |
| Money pages mong muốn (nếu có) + budget + risk level | Handoff: textlink PR → `textlink-analyzer`; outreach → team |

## 3. Lưu đồ B — Gate Offpage (#25◇)

```
B0. Content + structure chuẩn chưa?  ─KHÔNG→  HALT: fix content/structure trước
 │ CÓ + evidence cần link (gap RD rõ / keyword kẹt trang 2)
 ▼
B1. Money-page link-gap test → chọn target (lăng kính / supporting content)
 ▼
B2. Anchor plan 4 lớp — 3 giai đoạn trust, Exact ≤8-10% trần cứng
 ▼
B3. Velocity theo nhịp đối thủ → B4. Budget theo chất lượng → B5. Tracking + điều kiện dừng
```

Verdict ghi vào index: `gate: <ĐẨY LINK | KHÔNG ĐẨY — lý do>` + link file quyết định.

## 4. Checklist rút gọn (10 dòng)

1. **Gate B0:** 80-90% dự án top KHÔNG cần chiến dịch backlink; site không lên top → 90-99% do content/cấu trúc/UX. Chưa chuẩn → HALT, route về seo-onpage/structure.
2. Proceed chỉ khi có dấu hiệu: link gap rõ trong research · keyword kẹt trang 2 · mất cân đối content/RD — ghi lý do vào verdict.
3. **Link-gap test:** đối thủ có 0 quality link vào money page → KHÔNG bắn thẳng money page → route supporting content; gap = N RDs → tính climb cost, quá đắt thì đổi target.
4. **Target lăng kính:** trang tầng thấp, intent cụ thể, cạnh tranh thấp, internal link dày 2 chiều (lên cha + xuống con). Chưa có IL 2 chiều → fix internal trước khi bắn.
5. Ưu tiên quick win: trang có keyword rank vị trí 4-20, volume ≥100. Site mới: homepage + pillow anchors (brand/naked/generic) trước, gate lại sau 5-10 bài content.
6. **Anchor 4 lớp đúng thứ tự:** (1) giai đoạn trust → (2) SERP consensus "mimic the winners" → (3) GTV prior 8 loại → (4) Authority-Aggression theo sức nguồn.
7. **3 giai đoạn trust** (AN TOÀN / TỪ KHÓA): GĐ1 ~70/30 · GĐ2 40-50/50-60 · GĐ3 35-45/55-65. **Exact ≤8-10% trần cứng MỌI giai đoạn** — tăng phần từ khóa bằng Partial/LSI/Brand+KW, không bằng Exact. Nghi ngờ → chọn giai đoạn thấp hơn.
8. **Footprint:** nguồn <DR40 chỉ nhận branded/generic/naked; exact CHỈ ở DR60-85+ editorial đúng theme · anchor map 20-30 variations/target · không lặp anchor non-brand trong tháng · anchor 3 phần + co-occurrence keyword quanh anchor (bắt buộc).
9. **Velocity:** nhịp chuẩn = RD/tháng trung bình của đối thủ; site mới bắt đầu ½ nhịp; trong tháng: free/foundational trước → paid sau; kỳ vọng kết quả 1-6 tháng — ghi vào plan.
10. **Method mix:** conservative mặc định (guest post đúng theme + textlink PR + linkable asset + reclaim); Entity campaign (social/profile/citation) TÁCH RIÊNG; plan phải có điều kiện dừng/đổi hướng.

## 5. Ngưỡng pass

- Gate verdict có evidence cite research §; không phán chay.
- Plan đủ 8 section + CSV per-link; quota khớp tổng; anchor % nằm trong khung giai đoạn; Exact không vượt trần.
- Campaign chạy đúng velocity/anchor plan; tracking cadence tháng (ranking pos 4-20 → top; RD growth vs đối thủ).

## 6. Skill gọi + luật nạp

| Skill | Vai trò |
|---|---|
| `skills/backlink-research/` | DATA — chạy TRƯỚC, không plan khi thiếu research |
| `skills/backlink-plan/` | DECISION — gate → target → anchor → velocity → budget |
| `skills/textlink-analyzer/` | EXECUTION — lọc URL báo PR, nhận quota + ratio per target |

Luật nạp: `references/anchor-ratio-framework.md` chỉ nạp khi lập anchor plan (Bước 2); không quét cả references/.

## 7. 5 lỗi thường gặp

1. Đi link khi content/structure chưa chuẩn (bỏ qua Gate B0) — lỗi #1, đốt tiền.
2. Bắn thẳng money page khi đối thủ không có link vào đó — fail link-gap test.
3. Exact vượt trần 8-10% hoặc lặp anchor non-brand trong cùng tháng — footprint.
4. Velocity bung vượt nhịp đối thủ nhiều lần; hoặc trộn Entity campaign vào backlink plan.
5. Plan không có điều kiện dừng — link mãi cho keyword không nhúc nhích thay vì quay lại sửa content.
