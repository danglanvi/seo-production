# Cheat-sheet WS05 — Content Plan (05-content-plan)

> Bản 1 trang, chưng cất từ `../sop/01-topical-map.md` (DoD 14 mục) + `../sop/02-content-brief.md` + `../sop/09-timeline/10-thang-thuc-day.md` (ma trận content type × timeline) ngày 2026-07-17.
> QC chính thức PHẢI chấm theo checklist đầy đủ trong `../sop/` — cheat-sheet chỉ để nạp nhanh trước khi làm.

## 1. Mục tiêu WS

Từ keyword cam kết → topic → Topical Map + SCN → plan traffic FULL ≥ cam kết +20% → ma trận content theo đúng cửa sổ thời gian. WS này giữ **plan + tracking + QC kết quả** — phần VIẾT BÀI chạy ở fork `Content Production - <client>/`.

Công đoạn phụ trách: **4, 9, 10, 15, 16, 17, 19**.

## 2. Input / Output

| Input | Output |
|---|---|
| Keyword cam kết (`00-client-context/kpi-commitments.md`) + 9 câu discovery client | Topical Map processed (Title + H1 + URL + Meta + Image URL + Alt per page) + SCN, theo `_TEMPLATES/topical-map.md` |
| Access GSC/Ahrefs (≥1 nguồn) + gap analysis từ WS03 công đoạn 2 | Plan traffic FULL theo `_TEMPLATES/traffic-plan.md` + ma trận content theo `_TEMPLATES/content-plan-matrix.md` |
| Competitor topical coverage + momentum benchmark | Publication calendar + Content Brief top 20 pages + link chéo fork Content Production |

## 3. Checklist rút gọn (10 dòng)

| # | Check |
|---|---|
| 1 | 2-3 Buyer Persona + Source Context + Central Entity (Wikipedia-verified) + Central Search Intent — locked |
| 2 | Core Section (main attribute + ≥3 derived) + Outer Section (minor attributes, internal link về Core) |
| 3 | Deep research đủ artifact: Ontology + Lexical Semantics table + Query Network patterns; ≥500 raw queries → filter RPP → ≥50 final topics đã SERP-cluster |
| 4 | V-D-M matrix (Vastness-Depth-Momentum) — Momentum mandatory |
| 5 | Processed TM đủ Title + URL + Meta + Image URL + Alt per page; ONE Macro Context per page |
| 6 | ≥3 Quality Nodes + ≥2 Trending Nodes; Core ↔ Outer link map — signals flow về Core |
| 7 | Publication calendar patternless 5-phase + competitor momentum benchmark; GEO Gate #1/#2/#3 pass cho Quality Nodes |
| 8 | Content Brief top 20 pages: đủ 11 section, 100% fill, không field TBD, Representative Question ≠ Supporting Questions, L0 mandatory + E-A-V |
| 9 | Ma trận 7 content-type đúng cửa sổ: Entity (cuối T1→15ng T3) · URL SEO (T2→hết T3) · Marketing & Strategy (T3→hết T5; 65% + toàn bộ bài traffic quan trọng trong T3-T4) · Offsite (T4→T5, phantom keywords) · non-URL SEO (T4→hết T7) · News/Information Gain (T6→T9) · Template/Programmatic (tùy dự án, template phải được Content Leader duyệt) |
| 10 | Plan traffic FULL (T3 → giữa T4) ≥ cam kết +20% — thiếu thì bổ sung topic, không hạ mục tiêu |

## 4. Ngưỡng pass

- Topical Map chốt = **DoD 14 mục trong `../sop/01-topical-map.md` tick 100%** — đây là checklist chốt, không thay bằng 10 dòng trên.
- Plan traffic tổng dự phóng **≥ cam kết +20%**; ma trận content đủ % theo mốc tháng (gói 8/12 tháng retiming theo bảng biến thể trong `../sop/09-timeline/10-thang-thuc-day.md`).
- Luật thời gian bất biến khi xếp lịch: content cần **~100 ngày mature** → phải làm trước 2-3 tháng so với thời điểm cần kết quả; dây chuyền **content → +10-15 ngày onpage → +15-30 ngày internal link semantic**.
- Brief PASS khi 100% section fill, không TBD — writer không phải SEO specialist vẫn viết đúng Central Search Intent.

## 5. Skill gọi + luật nạp

| Skill | Khi nào |
|---|---|
| `topical-map-creation` | Công đoạn 4, 9, 10, 15 — sinh + chốt Topical Map, SCN |
| `competitor-seo-gap-analysis` | Công đoạn 9, 17 — coverage đối thủ, benchmark momentum, cơ hội topic |

Luật nạp 80/20: `references/` của skill nạp TỪNG file theo pointer khi step cần; không nạp examples/evals; checklist chỉ nạp đúng 3 file: `../sop/01-topical-map.md` + `../sop/02-content-brief.md` + `../sop/09-timeline/10-thang-thuc-day.md` (QC bài viết dùng tier-1 bên fork Content Production) — không quét cả `knowledge/`.

## 6. 5 lỗi thường gặp

1. Keyword clustering ≠ Topical Map — gom keyword theo volume mà bỏ Source Context và contextual boundaries.
2. Filter topic chỉ theo volume, bỏ RPP (Relevance × Prominence × Popularity) → map đầy topic không phục vụ Central Search Intent.
3. Nhiều Macro Context trên 1 page; Core thiếu độ sâu; thiếu Quality/Trending Nodes.
4. Publish theo pattern cố định, bỏ Momentum và competitor momentum benchmark — không đạt Topical Authority.
5. Xếp lịch content sát deadline KPI, quên ~100 ngày mature + dây chuyền onpage/internal link → kết quả đến sau khi hết hợp đồng.
