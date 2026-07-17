# Log — SEO Production

Timeline append-only của dự án. Mỗi thao tác = 1 entry, thêm vào CUỐI file, không sửa entry cũ.

## Format entry

```
## [YYYY-MM-DD] <op> | <short title> — @<alias>
- <what happened>
- Files touched: <paths>
- Công đoạn: #<n> (nếu có) · WS: <XX>
```

Luật ghi:

1. Mỗi entry bắt buộc có `op` đúng vocabulary bên dưới + alias người/agent thực hiện.
2. `Files touched` liệt kê path tương đối từ root instance; nhiều file thì liệt kê hết hoặc ghi theo folder.
3. `Công đoạn / WS` bỏ qua bằng `—` khi thao tác không gắn công đoạn cụ thể (vd `lint`, `bookkeep`).
4. Parse nhanh 10 op gần nhất: `grep "^## \[" log.md | tail -10`.

## Vocabulary op

| op | Khi dùng |
|---|---|
| `setup` | Setup instance client theo SETUP.md (duplicate master, fill context, retiming) |
| `ingest` | Đưa file mới vào `02-raw/` + phân loại + cập nhật index bảng D |
| `capture` | Chụp/lưu screenshot vào `02-raw/screenshots/` — 1 entry/đợt, kèm "Dùng cho:" |
| `work` | Làm 1 công đoạn / 1 deliverable trong WS folder |
| `qc` | Chấm QC deliverable theo checklist → report `03-audits/qc/` + verdict vào index |
| `feedback` | Ghi feedback client/Lead/QC-fail-lặp vào `12-feedback-lessons/feedback-log.md` |
| `lesson` | Promote pattern lặp ≥2 lần thành `lessons-ws<XX>.md` |
| `retro` | Retro cuối pha → `12-feedback-lessons/retro/retro-pha-<n>.md` |
| `gate` | Chốt 1 trong 4 nút decision ◇ (#6, #22, #25, #30) — ghi verdict + link deliverable |
| `report` | Báo cáo client (tháng / quý / nghiệm thu) |
| `meeting` | Meeting note (kick-off, review, họp client) — action items + owner |
| `handover` | Bàn giao / chuyển giao duy trì (công đoạn #33) |
| `lint` | Rà index vs thực tế folder — chạy hàng tháng |
| `bookkeep` | Cập nhật sổ sách (index, registry, link chéo) không thuộc op khác |
| `refactor` | Thay đổi infra (template/knowledge/skill) — bắt buộc ghi kèm MIGRATION.md |
| `archive` | Chuyển file vào `99-archive/` |
| `bootstrap` | Khởi tạo master / instance lần đầu |

---

## [2026-07-17] bootstrap | Khởi tạo master SEO Production v2026.07 — @vincent

- Dựng master SEO Production theo Blueprint A đã duyệt 17/07/2026: cây folder 00→12 + 99-archive, file hệ thống (CLAUDE.md, AGENT.md, AGENTS.md, README.md, SETUP.md, MIGRATION.md, SYNC.md), index.md prefill 33 công đoạn + dòng optional Traffic users, knowledge pack `02-raw/knowledge/`, `_TEMPLATES/` và 20 skill.
- Files touched: toàn bộ cây `SEO Production/`
- Công đoạn: — · WS: —
