---
client: "{{CLIENT}}"
cong_doan: "{{5 | 7 | 23 | 24 | 29}}"
ws: 03-audits
folder: 03-audits/content/
pic: "{{SEO Lead Project · Content Leader}}"
status: draft
version: v1
---

# {{CLIENT}} — Content audit — {{KY}}

> Audit lẻ hạng mục Content (mục 2.6 + 2.1 toppage của `audit-toan-dien.md`). Naming `{{CLIENT}}_audit-content-{{ky}}_v{{N}}.md` → `03-audits/content/`. Skill: `semantic-content-audit`, `content-refresh` (#24/#29 — brief bàn giao fork Content Production), `competitor-seo-gap-analysis`. Checklist: `sop/05-audit-checklist.md` + tier-1 outline/writing (chấm bài).

## 1. Scope & data

| Trường | Giá trị |
|---|---|
| Phạm vi URL | {{toàn site / cụm X / N URL top page}} |
| Nguồn + ngày | {{GSC 16 tháng (query·page) · crawl nội dung · SpySERP/hub ranking · GA4}} |
| Baseline | {{audit trước}} |

## 2. Finding

| Nhóm | Finding | URL / nhóm | Mức độ | Evidence |
|---|---|---|---|---|
| Toppage: URL mang traffic/ranking chính, đang giữ hay rớt | {{...}} | {{...}} | | {{GSC clicks 28d vs 28d}} |
| Intent mismatch (SERP thật vs page type) | | | | |
| Cannibalization (2+ URL cùng query) | | | | |
| Thin / duplicate / outdated (decay >20% impressions) | | | | |
| Thiếu coverage: cluster trong topical map chưa có bài · attribute E-A-V thiếu | | | | |
| Chất lượng theo tier-1-content-writing (W-series) trên mẫu N bài | | | | |

## 3. Action

| # | Action (refresh / gộp / tách / viết mới / noindex / redirect) | URL / scope | Mức độ | Owner | Deadline | Đích | Status |
|---|---|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{Content Leader / SEO}} | {{...}} | {{fork Content Production slug hoặc WS06}} | todo |

Bài viết mới/refresh → brief sang fork `Content Production - <client>/` (content-type + cửa sổ theo bảng 7 loại của trạm 05); tracking ở `05-content-plan/content-tracking/`.

## Done-criteria

- [ ] Toppage có bảng giữ/rớt với số GSC; cannibalization liệt kê cặp URL + query.
- [ ] Mỗi action có đích rõ (fork/WS06) + owner + deadline.
- [ ] index.md + log.md update; QC PASS.
