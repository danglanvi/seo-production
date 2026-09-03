---
template: onpage-batch
ws: 06-onpage-internal-link
cong_doan: "{{7 | 13 | 23}}"
checklist: 02-raw/knowledge/sop/08-onpage-checklist.md
batch: "{{BATCH_ID}}"
tier: "{{1 | 2 | 3}}"
client: "{{CLIENT}}"
status: draft
date: "{{YYYY-MM-DD}}"
---

# Onpage Batch {{BATCH_ID}} — {{CLIENT}}

> Checklist gốc: `02-raw/knowledge/sop/08-onpage-checklist.md` (P0 gate + Tier 1 /23 + Tier 2 /31 + Tier 3 /39 + AX1-AX7).
> Khi instantiate: lưu thành `06-onpage-internal-link/{{CLIENT}}_onpage-batch-<n>_v1.md`.

## 1. Thông tin batch

| Trường | Giá trị |
|---|---|
| Nhóm content | {{URL SEO | Entity | Strategy | non-URL SEO | Khác}} |
| Số URL trong batch | {{N}} |
| Tier áp dụng | Tier 1 /23 mặc định · Tier 2 /31 nếu bật tại kick-off (xem Ghi chú dòng #12 index) · Tier 3 /39 cho Quality Node/Root-Seed/cạnh tranh cao |
| Deadline batch | {{NGAY}} (content xong + 10-15 ngày theo dây chuyền) |
| PIC / Duyệt | {{SEO_EX}} / SEO Lead Project |

## 2. Luật chấm

1. **P0 — Content Quality Gate**: content chưa V-Pass thì KHÔNG onpage — trả về Content, không chấm tiếp.
2. Publish trang mới: chạy đủ Tier 1 (P1-P23, /23). Tier 2/3 cộng thêm theo cột Tier.
3. Audit trang cũ: chạy Tier 1 → 3, dừng ở tier có ≥3 item FAIL. **Sửa nền trước, tối ưu sau.**
4. AX1-AX7 (AI-search) KHÔNG tính vào /39 — chấm riêng cho trang cần GEO/AI Overview (mục 5).
5. Review 3 tầng: Self 100% → SEO EX verify → Lead random 25-30% (gap dương lớn = cờ đỏ).
6. Không tự hạ ngưỡng để cho qua; item không verify được ghi CANNOT-VERIFY, không tính pass.

## 3. Bảng batch — score per URL

Cột Item FAIL ghi ID theo P-series (vd `P2, P8, P17`); Re-score sau khi fix.

| # | URL | Loại content | P0 | Score /23 | Item FAIL | Ngày fix | Re-score | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | {{URL_1}} | {{LOAI}} | ☐ | {{x}}/23 | {{IDS}} | {{NGAY}} | {{x}}/23 | ☐ |
| 2 | {{URL_2}} | {{LOAI}} | ☐ | {{x}}/23 | {{IDS}} | {{NGAY}} | {{x}}/23 | ☐ |
| 3 | {{URL_3}} | {{LOAI}} | ☐ | {{x}}/23 | {{IDS}} | {{NGAY}} | {{x}}/23 | ☐ |

Tier 2/3 (nếu bật): thêm cột Score /31 hoặc /39 ngay sau Score /23 — cùng luật.

## 4. Item FAIL lặp trong batch

Item ID fail ≥2 lần → đề xuất entry `12-feedback-lessons/feedback-log.md` (nguồn: QC).

| Item ID | Số URL fail | Nguyên nhân | Hành động | Owner |
|---|---|---|---|---|
| {{ID}} | {{N}} | {{NGUYEN_NHAN}} | {{HANH_DONG}} | {{OWNER}} |

## 5. AX Extension (chỉ trang cần GEO — chấm riêng)

| URL | AX1 chunk | AX2 front-load | AX3 AIO counter | AX4 canonical/index | AX5 Blur Test | Ghi chú |
|---|---|---|---|---|---|---|
| {{URL}} | ☐ | ☐ | ☐ | ☐ | ☐ | {{GHI_CHU}} |

## 6. Dây chuyền content → onpage → internal link

| Nhóm content | Content xong | Onpage deadline (+10-15 ngày) | IL deadline (+15-30 ngày) |
|---|---|---|---|
| {{NHOM}} | {{NGAY}} | {{NGAY}} | {{NGAY}} → ghi vào `{{CLIENT}}_internal-link-plan` |

Mốc cứng gói 10 tháng: onpage URL SEO XONG hết T4; onpage content strategy chốt ≤15 ngày đầu T7.

## 7. Done-criteria

- [ ] 100% URL trong batch qua P0 gate trước khi chấm.
- [ ] 100% URL đạt ngưỡng tier cam kết; URL chưa đạt có Item FAIL + ngày fix + re-score.
- [ ] Item FAIL lặp ≥2 lần đã có entry đề xuất vào feedback-log.
- [ ] Dây chuyền IL đã lên lịch khớp internal-link-plan.
- [ ] Cập nhật index.md (cột QC + status) + log.md op `work`/`qc`.
