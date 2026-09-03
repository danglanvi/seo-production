---
client: "{{CLIENT}}"
cong_doan: "{{5 | 20 | 25 | 27}}"
ws: 03-audits
folder: 03-audits/offsite/
pic: "{{SEO Lead Project}}"
status: draft
version: v1
---

# {{CLIENT}} — Offsite / backlink audit — {{KY}}

> Audit lẻ hạng mục Backlink (mục 2.4 của `audit-toan-dien.md`) — trước gate Offpage #25 hoặc khi nghi ngờ link xấu. Naming `{{CLIENT}}_audit-offsite-{{ky}}_v{{N}}.md` → `03-audits/offsite/`. Checklist: `sop/10-offpage-process.md` + `tier-1-offpage-backlink.md`. Skill: `backlink-research`, `textlink-analyzer`, `backlink-plan`.

## 1. Data

| Nguồn + ngày | Ghi chú |
|---|---|
| Ahrefs Site Explorer (referring domains, anchors, new/lost 90d) — {{dd/mm}} | credit hạn chế: lấy overview + top 200 RD, không kéo full |
| GSC Links | |
| Đối thủ so sánh (2–3) | {{domain}} |

## 2. Finding

| Nhóm | Finding | Mức độ | Evidence |
|---|---|---|---|
| Profile: DR/RD, tốc độ tăng, tỷ lệ dofollow, phân bố theo trang đích | {{...}} | | |
| Anchor: brand / naked / exact-match — tỷ lệ, rủi ro over-optimized | | | |
| Toxic / spam / PBN / link mua lộ liễu | | | |
| Gap vs đối thủ (RD họ có mình chưa có, theo loại: PR, directory, guest, editorial) | | | |
| Brand mention chưa link · link mất 90 ngày | | | |

## 3. Verdict cho gate Offpage (#25)

{{90% dự án KHÔNG cần đẩy link — nền content/technical còn FAIL CRITICAL → không mở chiến dịch}}. Đề xuất: {{không đẩy / nền + phantom guest post / đẩy mạnh + textlink PR}} — lý do.

## 4. Action

| # | Action (disavow · thu hồi · xây theo loại) | Phạm vi | Owner | Deadline | Status |
|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} | todo |

## Done-criteria

- [ ] Có số profile + anchor + gap với ngày export.
- [ ] Verdict gate ghi rõ + link vào dòng #25 `index.md` (`gate: <verdict>`).
- [ ] Action có owner/deadline; log.md update.
