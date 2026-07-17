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

## [2026-07-18] refactor | Vá 17 finding verification — @claude

- Nhóm consistency: DoD topical map 14 → **15 mục** (đồng bộ 8 file, tách item gộp trong template topical-map); ký hiệu B0-B8 khai báo tường minh = «Bước 0»→«Bước 8» sop/07; cheat-sheets ghi rõ 6 file WS03→WS08 + điều kiện pre-work §3; banner sop/09-timeline ghi 3 file .html lưu đồ không đóng gói; `_MANIFEST.md` bỏ vế "Đang chưng cất bởi agent riêng" (hàng #13-17).
- Nhóm hop-dong-cam-ket.md (file thứ 4 của 00-client-context, phương án b): khai báo ở README WS00, done-criteria ma trận M, pointer kpi-commitments, verify SETUP mục 2.
- Nhóm SYNC/MIGRATION: prompt migration trỏ bảng 2.A/2.B thay vì hard-code; danh sách read-only mục 3 đồng bộ đủ bảng 2.A; commit TRƯỚC pull ở nhịp hằng ngày; `init -b main`; escape `\|` bảng ba file dùng chung; bảng 2.B ghi rõ trừ README `12-feedback-lessons/`; path `knowledge/` trần → `02-raw/knowledge/`.
- Nhóm quick-start & rule: README lên 5 lệnh (thêm `ingest`, sửa mô tả `setup client`); SETUP mục 4 trỏ bảng quick-start README; ghi chú standalone bước 7; CLAUDE.md §0 ngoại lệ trivial read-only theo AGENT.md §4.
- Files touched: CLAUDE.md, README.md, SETUP.md, SYNC.md, MIGRATION.md, index.md, log.md, 00-client-context/README.md, 00-client-context/kpi-commitments.md, 04-structure-ux-cro/README.md, 05-content-plan/README.md, _TEMPLATES/topical-map.md, 02-raw/knowledge/README.md, 02-raw/knowledge/_MANIFEST.md, 02-raw/knowledge/cheat-sheets/ws04-structure.md, 02-raw/knowledge/cheat-sheets/ws05-content-plan.md, 02-raw/knowledge/sop/09-timeline/README.md
- Công đoạn: — · WS: —
