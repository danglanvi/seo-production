# Cheat-sheet WS03 — Audit (03-audits)

> Bản 1 trang, chưng cất từ `../sop/05-audit-checklist.md` + `../sop/06-self-checklist/tier-3-audit-configuration.md` ngày 2026-07-17.
> QC chính thức PHẢI chấm theo checklist đầy đủ trong `../sop/` — cheat-sheet chỉ để nạp nhanh trước khi làm.

## 1. Mục tiêu WS

Phát hiện, phân loại và ưu tiên vấn đề SEO toàn site + content theo chu kỳ. Output cuối luôn là danh sách action gắn URL cụ thể, có owner + deadline — không phải báo cáo mô tả.

Công đoạn phụ trách: **2, 5, 6◇, 7 (plan), 22◇, 24, 27, 29** (◇ = decision gate, verdict ghi vào index).

## 2. Input / Output

| Input | Output |
|---|---|
| Access GSC/GA4/Ahrefs + crawl data (+ logfile ở công đoạn 27) | Audit report trong `03-audits/` theo `_TEMPLATES/audit-toan-dien.md` (công đoạn 2: `gap-analysis.md`) |
| Bảng keyword cam kết (`00-client-context/kpi-commitments.md`) | Phân loại action FULL URL + owner + deadline |
| Audit report kỳ trước (nếu có) + feedback-log WS03 | Verdict gate ◇ #6/#22 ghi vào index + QC report nếu chấm bài |

## 3. Checklist rút gọn (10 dòng)

| # | Check |
|---|---|
| 1 | Scope đủ 6 hạng mục: toppage · cấu trúc · entity · backlink · technical · content |
| 2 | Cadence đúng: weekly writer self-audit 1 bài · bi-weekly Lead pre-publish · monthly senior 3-5 bài top traffic · quarterly full retro |
| 3 | Pre-publish flow: self-check → editor review format GTV → REWORK = fix 3 priority items rồi re-audit → PASS mới ship |
| 4 | Post-publish: GSC impressions của Representative Question tăng trong 7-30 ngày |
| 5 | Không cannibalization: check SERP target query — không 2 URL nội bộ cùng cạnh tranh 1 query |
| 6 | Internal link được crawl (check log crawler); orphan sau 30 ngày = red flag |
| 7 | T3-O1/O2: chấm Information Gain vs đối thủ + vị trí bài trên Topical Map (Root/Seed/Node, upstream/downstream) |
| 8 | T3-W2 People-first: Who-How-Why transparent + ≥1 unique insight/data point mà top 10 SERP chưa có |
| 9 | T3-W3 Full Semantic Audit 66 điểm cho pillar/revenue-critical page: target ≥50/66 |
| 10 | T3-W5 Cross-SCN gate (SCN mature): L0 của Root + Seeds đọc liền thành super summary mạch lạc, không mâu thuẫn |

## 4. Ngưỡng pass

- Report PASS khi: đủ 6 hạng mục + mọi action gắn URL/owner/deadline + red flag có phân loại nguyên nhân.
- Bài flagship: **≥50/66** theo T3-W3. Verdict REWORK → fix priority 3 items → re-audit, chưa PASS chưa ship.
- Tier 3 chỉ bật khi: senior · audit mode · niche cạnh tranh cao — không áp cho bài mới thông thường.
- Item FAIL ≥2 lần qua các kỳ QC → đề xuất entry `12-feedback-lessons/feedback-log.md`.

## 5. Skill gọi + luật nạp

| Skill | Khi nào |
|---|---|
| `semantic-content-audit` | Audit content/bài, T3-W2/W3, công đoạn 5, 7, 24, 29 |
| `technical-seo-audit` | Audit technical tầng site, công đoạn 5, 27 |
| `competitor-seo-gap-analysis` | Công đoạn 2 — gap theo page type |
| `content-refresh` | Decay detection từ T6 trở đi (công đoạn 24, 29) |
| `query-processing-diagnosis` | Bộ keyword cam kết đã có hạng: gate 22, công đoạn 24, 29, hoặc keyword cam kết đứng hạng/rơi. Ra JSON + deck + hồ sơ ở `ranking/` |

Luật nạp 80/20: chỉ nạp skill đúng loại audit đang làm; `references/` nạp TỪNG file theo pointer trong SKILL.md; checklist chỉ nạp đúng file: `../sop/05-audit-checklist.md` + `../sop/06-self-checklist/tier-3-audit-configuration.md` + `../sop/06-self-checklist/tier-3-technical-advance.md` — không quét cả `knowledge/`.

## 6. 5 lỗi thường gặp

1. Chấm gộp cả nhóm item, không trích evidence (quote/số liệu/cell) cho từng item.
2. Action chung chung không gắn URL + owner + deadline → không thực thi được.
3. Traffic tăng nhưng impression target query flat mà không flag intent mismatch (lỗi disambiguation).
4. Đề xuất tactic trước khi sửa nền — technical/nền tảng phải sửa trước (dễ, hiệu quả nhanh).
5. Bật Tier 3 cho bài mới thông thường, hoặc ngược lại: audit page flagship mà bỏ thang 66 điểm.
