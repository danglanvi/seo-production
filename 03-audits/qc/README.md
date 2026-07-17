# qc/ — QC report của mọi workstream

- Naming: `QC-<##>-<slug>-<YYYYMMDD>.md` — `<##>` = số công đoạn 2 chữ số (vd `QC-05-audit-content-20260717.md`).
- Template bắt buộc: `_TEMPLATES/qc-report.md` (frontmatter score/verdict + bảng item-evidence + việc phải sửa).
- Chấm TỪNG item ID với evidence trích từ deliverable; item không verify được = CANNOT-VERIFY, không tính pass.
- Verdict: PASS | FAIL | CONDITIONAL-PASS (fail ≤2 item không-blocking, có deadline sửa — Lead quyết).
- Sau mỗi QC: update cột QC + status trong `index.md` (FAIL → giữ `qc`, không lên `done`) + append `log.md` op `qc`.
- Item ID fail ≥2 lần QC → đề xuất entry `12-feedback-lessons/feedback-log.md` (nguồn: QC).
