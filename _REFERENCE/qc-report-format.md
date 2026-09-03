# QC report — format output

> Tách từ `CLAUDE.md` (§7.3) ngày 2026-09-02 (v2026.09.2) để file luật gọn — nội dung giữ nguyên văn. Router trỏ tới file này khi task cần.

### 7.3 Output

Path: `03-audits/qc/QC-<##côngđoạn>-<slug>-<YYYYMMDD>.md` — theo `_TEMPLATES/qc-report.md`:

```markdown
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
## Kết quả theo item
| ID | Check (rút gọn) | Kết quả | Evidence | Ghi chú |

## Việc phải sửa (item FAIL, sắp theo impact)
| ID | Sửa gì | Owner | Deadline |

## Verdict & điều kiện
```
