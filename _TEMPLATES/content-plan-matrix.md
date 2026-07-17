---
template: content-plan-matrix
ws: 05-content-plan
cong_doan: "15, 16, 17, 19"
checklist: 02-raw/knowledge/sop/09-timeline/10-thang-thuc-day.md
client: "{{CLIENT}}"
goi_timeline: "{{8 | 10 | 12}} tháng"
status: draft
date: "{{YYYY-MM-DD}}"
---

# Content Plan Matrix — {{CLIENT}}

> Nguồn khung: `02-raw/knowledge/sop/09-timeline/10-thang-thuc-day.md` (ma trận Content Type × Timeline). Cửa sổ dưới đây theo gói 10 tháng chuẩn — gói 8/12 tháng retiming theo bảng biến thể trong cùng file.
> Bài VIẾT chạy ở fork `Content Production - {{CLIENT}}/` — file này chỉ giữ plan + tracking + QC kết quả.
> Khi instantiate: lưu thành `05-content-plan/{{CLIENT}}_content-plan-matrix_v1.md`.

## 1. Nguyên tắc

1. Content cần ~100 ngày mature → làm trước 2-3 tháng so với thời điểm cần kết quả.
2. Mốc cửa sổ GỒM content + onpage (content thuần = trừ 10-15 ngày).
3. Dây chuyền: content → (+10-15 ngày) onpage → (+15-30 ngày) internal link semantic.
4. Plan traffic FULL (T3 → giữa T4) phải ≥ cam kết +20%; chưa đủ → bổ sung topic.
5. P1 + chuỗi content lõi (Entity, URL SEO, Core) không bao giờ nén, kể cả gói 8 tháng.
6. Template/programmatic chỉ chạy khi research phân loại page type cho thấy phù hợp; template phải được Content Leader duyệt trước khi nhân bản.

## 2. Ma trận 7 content-type × cửa sổ

| # | Loại content | Cửa sổ (10T chuẩn) | Số bài plan | % mốc bắt buộc | PIC | Duyệt |
|---|---|---|---|---|---|---|
| 1 | Content Entity | Cuối T1 → ≤15 ngày đầu T3 | {{N}} | 100% xong ≤15 ngày đầu T3 | Content, SEO | SEO |
| 2 | Content URL SEO | T2 → hết T3 (trễ nhất ≤15 ngày đầu T4) | {{N}} | Core Section 50-60% hết T2 → 100% hết T3 | Content | SEO Lead Project |
| 3 | Content Marketing & Strategy | T3 → hết T5 (trễ nhất ≤15 ngày đầu T6) | {{N}} | 65% + toàn bộ bài traffic quan trọng xong T3-T4 | Content, SEO | SEO |
| 4 | Content Offsite SEO | T4 → T5 | {{N}} | Target Phantom Keywords: `allintitle:` <1.000 rất tốt / <5.000 chấp nhận | SEO, Content | SEO Lead Project |
| 5 | Content non-URL SEO | T4 → hết T7 | {{N}} | Chốt hết T7 | Content | SEO |
| 6 | News / Information Gain | T6 → T9 | {{N}} | Số lượng ít — giữ momentum + unique | Content | SEO |
| 7 | Template / Programmatic | Không cố định — theo research | {{N}} | Template duyệt trước khi nhân bản | Content | Content Leader |

## 3. Tracking % mốc

Cập nhật hàng tháng. Lệch âm → ghi hành động + owner, không để trống.

| Mốc | Deadline | Kế hoạch (bài) | Thực tế | Lệch | Hành động |
|---|---|---|---|---|---|
| Content Entity 100% | ≤15 ngày đầu T3 | {{N}} | | | |
| Core Section 50-60% | Hết T2 | {{N}} | | | |
| Content URL SEO 100% | Hết T3 | {{N}} | | | |
| Plan traffic FULL ≥ cam kết +20% | Giữa T4 | {{TRAFFIC}} | | | |
| Strategy 65% + bài traffic quan trọng | Hết T4 | {{N}} | | | |
| Strategy 100% | ≤15 ngày đầu T6 | {{N}} | | | |
| Content non-URL SEO 100% | Hết T7 | {{N}} | | | |
| News / Information Gain | T6 → T9 | {{N}} | | | |

## 4. Liên thông fork Content Production

| Trường | Giá trị |
|---|---|
| Fork content | `Content Production - {{CLIENT}}/` |
| QC bài viết | Checklist tier-1 outline/writing chạy bên fork |
| Kết quả về | Bảng D deliverable registry trong index.md instance |

## 5. Retiming gói {{8 | 12}} tháng

Chỉ điền khi không phải gói 10 tháng. Nguồn: bảng "Biến thể 8 & 12 tháng" trong `02-raw/knowledge/sop/09-timeline/10-thang-thuc-day.md`.

| Loại content | Cửa sổ sau retiming | Ghi chú |
|---|---|---|
| {{LOAI}} | {{CUA_SO}} | {{GHI_CHU}} |

## 6. Done-criteria

- [ ] Ma trận đủ 7 dòng, mỗi dòng có số bài plan + PIC + người duyệt.
- [ ] Cột cửa sổ đã retiming đúng gói {{8 | 10 | 12}} tháng.
- [ ] Tổng traffic dự phóng ≥ cam kết +20% (khớp `{{CLIENT}}_traffic-plan`).
- [ ] Tracking % mốc cập nhật đến tháng hiện tại, lệch âm có hành động + owner.
- [ ] Link fork Content Production hoạt động; cập nhật index.md + log.md op `work`.
