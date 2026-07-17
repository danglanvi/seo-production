---
template: gate-offpage-decision
ws: 07-offpage
cong_doan: 25
gate: "◇ Gate Offpage — đẩy mạnh link? (T6, khung 10 tháng)"
skill: backlink-plan (input từ backlink-research)
naming: "{{CLIENT}}_gate-offpage-decision_v{{N}}.md"
version: v1
---

# {{CLIENT}} — Gate Offpage Decision (công đoạn 25 · T6)

> Nguyên tắc gate: 80-90% dự án top KHÔNG cần chiến dịch backlink. Site không lên top → 90-99% do content/cấu trúc/UX. Verdict phải đứng trên evidence — không phán chay.

## 0. Điều kiện tiên quyết (FAIL 1 dòng → HALT: verdict "KHÔNG ĐẨY — fix nền trước" + list việc route WS 06)

| # | Điều kiện | PASS/FAIL | Evidence |
|---|---|---|---|
| 1 | Content URL SEO đã publish đủ + onpage PASS tier cam kết (#15, #23) | | |
| 2 | Cấu trúc site + internal link 2 chiều quanh target đã chuẩn (#18) | | |
| 3 | Audit T6 (#24) không còn lỗi nền blocking | | |

## 1. Evidence (điền đủ TRƯỚC khi ghi verdict)

| Nguồn | Data | Kết luận rút ra |
|---|---|---|
| Research §1 — profile mình vs đối thủ (RD, DR, tuổi profile) | | |
| Research §2 — velocity đối thủ (RD mới/tháng, trung bình top 5) | | |
| Research §4 — anchor consensus top 5-10 SERP | | |
| Research §5 — money-page link-gap test | | |
| Keyword kẹt trang 2 (pos 4-20, volume ≥100) | | |

## 2. Verdict

| Trường | Giá trị |
|---|---|
| Verdict | KHÔNG ĐẨY / ĐẨY GIỚI HẠN / ĐẨY MẠNH |
| Lý do (cite dòng evidence mục 1) | |
| Người lập / người duyệt | {{SEO_LEAD}} / SEO Director |
| Ngày quyết | {{YYYY-MM-DD}} |

Luật verdict:
1. Không có link gap rõ + keyword không kẹt trang 2 → KHÔNG ĐẨY; quay lại content/onpage.
2. Đối thủ có 0 quality link vào money page → KHÔNG bắn thẳng money page; route supporting content.
3. Link gap = N RD → tính climb cost; gap quá đắt → đổi target/cluster, ghi lý do.
4. Verdict ĐẨY phải điền đủ mục 3-6; verdict KHÔNG ĐẨY → dừng tại đây, vẫn ghi index + log.

## 3. Target — chọn trang lăng kính

| URL | Vai trò (home/supporting/category/money) | Lý do chọn | Keyword pos 4-20 | Internal link 2 chiều? | Quota link |
|---|---|---|---|---|---|

Luật chọn: tầng thấp trong cấu trúc, intent cụ thể, cạnh tranh thấp, internal link dày 2 chiều (lên cha + xuống con) → tán xạ kéo cả cluster. Chưa có internal 2 chiều → fix internal trước khi bắn. Site mới chưa đủ authority nền → homepage trước với pillow anchor (brand/naked/generic).

## 4. Anchor — mô hình 3 giai đoạn (trần Exact ≤8-10% MỌI giai đoạn)

1. Giai đoạn trust hiện tại: {{1|2|3}} — căn cứ research §1; nghi ngờ giữa 2 giai đoạn → chọn giai đoạn thấp hơn.
2. Khung tổng AN TOÀN/TỪ KHÓA: GĐ1 ~70/30 · GĐ2 40-50/50-60 · GĐ3 35-45/55-65; phần từ khóa tăng bằng Partial/LSI/Brand+KW, KHÔNG bằng Exact.
3. SERP consensus tinh chỉnh trong khung ("mimic the winners"); Authority-Aggression: nguồn <DR40 chỉ brand/generic/naked, exact chỉ ở DR60-85+ editorial đúng theme.
4. Phân bổ chi tiết 8 loại per target → điền ở backlink-campaign, theo `skills/backlink-plan/references/anchor-ratio-framework.md`.

## 5. Velocity

1. Nhịp đối thủ: {{N}} RD/tháng (research §2); nhịp đề xuất: {{N}} (site mới = ½ nhịp đối thủ).
2. Trình tự trong tháng: free/foundational trước → paid sau.
3. Kỳ vọng kết quả 1-6 tháng — ghi rõ vào plan để quản trị kỳ vọng client.

## 6. Budget

| Phương án | Số link/tháng | Đơn giá tham chiếu | Tổng/tháng | Ghi chú |
|---|---|---|---|---|
| Tối thiểu khả thi | | | | |
| Khuyến nghị | | | | |

Triết lý: phân bổ theo chất lượng, không theo số lượng ("1 link 1 triệu đúng chuẩn > gói 5-6 triệu").

## Ghi vào hệ thống

1. index.md dòng #25: Ghi chú `gate: <verdict>` + link file này; log.md op `gate`.
2. Verdict ĐẨY → tạo `{{CLIENT}}_backlink-campaign_v1.md` từ `_TEMPLATES/backlink-campaign.md`.

## Done-criteria

- [ ] Mục 0 chấm PASS/FAIL từng dòng, có evidence — không chấm gộp.
- [ ] Mục 1 đủ 5 dòng evidence có data thật (cite research file), không ô trống.
- [ ] Verdict có lý do cite evidence + người duyệt SEO Director.
- [ ] Verdict ĐẨY: mục 3-6 điền đủ; mọi target qua link-gap test; exact ≤8-10%.
- [ ] index #25 ghi `gate: <verdict>` + log op `gate`.
