---
client: "{{CLIENT}}"
cong_doan: "{{5 | 24 | 27 | 29}}"
ws: 03-audits
folder: 03-audits/technical/
pic: "{{SEO Lead Project}}"
status: draft
version: v1
---

# {{CLIENT}} — Technical SEO audit — {{KY}}

> Audit lẻ hạng mục Technical (mục 2.5 của `audit-toan-dien.md`) — dùng giữa kỳ, sau deploy, khi rớt hạng bất thường. Naming `{{CLIENT}}_audit-technical-{{ky}}_v{{N}}.md` → `03-audits/technical/`. Checklist: `sop/05-audit-checklist.md` + `sop/06-self-checklist/tier-3-technical-advance.md` + `tier-3-audit-configuration.md`; sự kiện rớt hạng: `tier-3-ranking-drop-runbook.md`. Skill: `technical-seo-audit`, `seo-drift-tracker`, `seo-logfile-analysis` (#27).

## 1. Scope & data

| Trường | Giá trị |
|---|---|
| Trigger | {{định kỳ T3-T4 / sau deploy dd/mm / rớt hạng / logfile T7}} |
| Nguồn + ngày | {{crawl (tool, N URL) · GSC Coverage/CWV · PSI · logfile · Ahrefs Site Audit}} |
| Baseline | {{link audit trước}} |

## 2. Finding theo nhóm

| Nhóm | Finding | URL / nhóm URL | Mức độ | Evidence |
|---|---|---|---|---|
| Crawl & index (robots, sitemap, noindex, canonical, 4xx/5xx, redirect chain) | {{...}} | {{...}} | {{C/H/M/L}} | {{...}} |
| Core Web Vitals (LCP/INP/CLS field + lab) theo template | {{...}} | {{...}} | | |
| Render & semantic HTML (heading, main/article, JS-render, lazy) | {{...}} | {{...}} | | |
| Cấu trúc URL · hreflang · pagination · faceted | {{...}} | {{...}} | | |
| Schema & structured data lỗi | {{...}} | {{...}} | | |
| Logfile (#27): bot hit theo nhóm URL, waste crawl, orphan bot-visited | {{...}} | {{...}} | | |

## 3. Action full URL

| # | Action | URL / scope | Mức độ | Owner (Coder/SEO) | Deadline | Verify sau fix | Status |
|---|---|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{GSC/PSI/crawl lại}} | todo |

## 4. Thứ tự

Chặn crawl/index → CWV landing thương mại → render/semantic → còn lại. Nền FAIL CRITICAL → không mở offpage.

## Done-criteria

- [ ] Mỗi finding có URL + evidence; nhóm sạch ghi PASS.
- [ ] Action có owner + deadline + cách verify; bàn giao Dev qua Sheet/Drive nếu khách tự sửa.
- [ ] Ghi vào `index.md` (dòng công đoạn) + `log.md`; QC PASS theo ma trận M.
