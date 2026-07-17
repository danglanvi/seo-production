---
client: "{{CLIENT}}"
cong_doan: "{{5 | 24 | 27 | 29}}"
ws: 03-audits
pic: "{{PIC}}"
status: draft
version: v1
---

# {{CLIENT}} — SEO Audit toàn diện — {{KY_AUDIT}}

> Checklist QC: `02-raw/knowledge/sop/05-audit-checklist.md` + `02-raw/knowledge/sop/06-self-checklist/tier-3-audit-configuration.md` + `tier-3-technical-advance.md`.
> Naming: `{{CLIENT}}_audit-toan-dien_v{{N}}.md`. Kết quả QC → `03-audits/qc/`.

## 1. Scope

| Trường | Giá trị |
|---|---|
| Domain | {{DOMAIN}} |
| Kỳ audit | {{T1 toàn diện \| T3-T4 định kỳ \| T6-T7 logfile + full \| T9-T10 tổng kết}} |
| Data nguồn | {{GSC / Ahrefs / crawl / logfile — ghi ngày export từng nguồn}} |
| Số URL crawl | {{N}} |
| Baseline so sánh | {{link audit kỳ trước hoặc n/a}} — evidence ảnh lưu `02-raw/screenshots/` |

## 2. Sáu hạng mục audit

Luật chấm: mỗi finding có mức độ CRITICAL / HIGH / MEDIUM / LOW + evidence (URL, số liệu, screenshot). Hạng mục sạch ghi PASS, không để trống.

### 2.1 Toppage

| Finding | URL / nhóm URL | Mức độ | Evidence |
|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} |

### 2.2 Cấu trúc site & internal link

| Finding | URL / nhóm URL | Mức độ | Evidence |
|---|---|---|---|
| {{orphan / depth / flow về Core...}} | {{...}} | {{...}} | {{...}} |

### 2.3 Entity

| Finding | Phạm vi | Mức độ | Evidence |
|---|---|---|---|
| {{entity home / schema / consistency onsite-offsite...}} | {{...}} | {{...}} | {{...}} |

### 2.4 Backlink

| Finding | Phạm vi | Mức độ | Evidence |
|---|---|---|---|
| {{profile / anchor / toxic / gap vs đối thủ...}} | {{...}} | {{...}} | {{...}} |

### 2.5 Technical

| Finding | URL / nhóm URL | Mức độ | Evidence |
|---|---|---|---|
| {{crawl / index / 4xx-5xx / CWV / redirect-canonical / sitemap-robots...}} | {{...}} | {{...}} | {{...}} |

### 2.6 Content

| Finding | URL / nhóm URL | Mức độ | Evidence |
|---|---|---|---|
| {{intent mismatch / cannibalization / thin / decay / duplicate...}} | {{...}} | {{...}} | {{...}} |

## 3. Phân loại action — full URL

Mọi finding quy về action có URL/scope cụ thể. Cấm action chung chung kiểu "tối ưu content".

| # | Action | URL / scope | Hạng mục | Mức độ | Owner | Deadline | Status |
|---|---|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | todo |

## 4. Thứ tự ưu tiên — sửa nền trước

1. Technical chặn crawl/index sửa TRƯỚC mọi tối ưu khác.
2. Cấu trúc site + internal link sửa trước onpage từng URL.
3. Content quality sửa trước khi đẩy backlink.
4. Nền còn FAIL mức CRITICAL → không mở chiến dịch offpage.

## 5. Post-audit tracking

Track sau fix: GSC impressions target query 7-30 ngày · không cannibalize page cũ (check SERP) · orphan = 0 sau 30 ngày (log crawler).

## Done-criteria

- [ ] Đủ 6 hạng mục, mỗi hạng mục có finding + evidence hoặc PASS.
- [ ] 100% action có full URL/scope + owner + deadline.
- [ ] Action xếp đúng thứ tự sửa-nền-trước (mục 4).
- [ ] Verdict tổng + top 3 việc phải sửa trình SEO Lead Project.
- [ ] QC PASS theo ma trận M; index.md + log.md đã update.
