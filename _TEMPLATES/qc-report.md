---
deliverable: <path>
cong_doan: <n>
ws: <XX>
checklist: 02-raw/knowledge/sop/<file>
tier: <1|2|3>
role: self|verify|lead
scorer: <AI + người duyệt>
score: <x>/<max>
verdict: PASS | FAIL | CONDITIONAL-PASS
date: YYYY-MM-DD
---

# QC report — công đoạn #<n> · <slug deliverable>

> Naming: `03-audits/qc/QC-<##côngđoạn>-<slug>-<YYYYMMDD>.md`. Prompt chuẩn: `QC <deliverable-path> theo công đoạn <n> [tier 1|2|3] [role self|verify|lead]`. Checklist lấy từ ma trận M (§5 CLAUDE.md) — không dùng checklist ngoài ma trận.

## Kết quả theo item

| ID | Check (rút gọn) | Kết quả | Evidence | Ghi chú |
|---|---|---|---|---|
| <P1/O1/W1/AX1...> | <mô tả rút gọn từ checklist> | PASS \| FAIL \| CANNOT-VERIFY | <quote / số liệu / cell trích từ deliverable> | <...> |

Luật chấm:

1. Chấm TỪNG item theo ID — không chấm gộp, không chấm cảm tính.
2. Evidence bắt buộc trích được từ deliverable (quote / số liệu / cell). Không có evidence = không có kết quả.
3. Item không verify được → `CANNOT-VERIFY`, KHÔNG tính pass.
4. Tier 2 chỉ chấm item đã bật lúc kick-off (Ghi chú dòng #12 `index.md`).

## Việc phải sửa (item FAIL, sắp theo impact)

| ID | Sửa gì | Owner | Deadline |
|---|---|---|---|
| <ID> | <hành động cụ thể, làm lại được> | <tên> | <dd/mm> |

## Verdict & điều kiện

- **Verdict:** <PASS | FAIL | CONDITIONAL-PASS> — ngưỡng dùng của CHÍNH checklist đang chấm (vd onpage Tier 1 theo luật scoring /23 trong `sop/08-onpage-checklist.md`). Không tự đặt/nới ngưỡng.
- **CONDITIONAL-PASS** chỉ khi: fail ≤2 item không-blocking + có deadline sửa cụ thể — Lead quyết, Claude chỉ đề xuất.
- **Điều kiện kèm (nếu CONDITIONAL-PASS):** <item + deadline + ai xác nhận đã sửa>.
- **FAIL** → dòng công đoạn giữ status `qc`, không lên `done`. Sửa xong → QC lại → report MỚI (không sửa report này).

## Done-criteria

- [ ] Frontmatter đủ 10 field; score khớp tổng bảng item.
- [ ] 100% item của checklist có mặt trong bảng, mỗi item có kết quả + evidence.
- [ ] Mọi item FAIL có dòng trong bảng "Việc phải sửa" với owner + deadline.
- [ ] `index.md` đã update: cột QC (format `✅ <x>/<max> → [QC-...](path)` / `❌ → [link]`) + status + bảng D.
- [ ] Append `log.md` op `qc`; item fail ≥2 lần QC → đã đề xuất entry feedback-log (nguồn: QC).
