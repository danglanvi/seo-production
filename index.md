# {{CLIENT}} — SEO Production Registry

> Master template — client fields dùng `{{PLACEHOLDER}}`. Setup instance theo `SETUP.md` (9 bước). Cập nhật file này sau MỖI thao tác (luật §6 CLAUDE.md).

## A. Thông tin dự án

| Trường | Giá trị |
|---|---|
| Client / domain | {{CLIENT}} / {{DOMAIN}} |
| Hợp đồng | {{SO_HD}} — ký {{NGAY_KY}} — {{GIA_TRI}} — {{THOI_HAN}} |
| Mô hình | {{THUC_THI \| ADVISORY}} |
| Gói timeline | {{8\|10\|12}} tháng · T1 = {{THANG_DUONG_LICH}} |
| KPI cam kết | {{KPI}} |
| SEO Lead / Account | {{LEAD}} / {{ACCOUNT}} |

## B. Bảng 36 công đoạn (33 gốc + #34–36 CRO từ v2026.09.3)

Luật đọc bảng:

1. Tháng = khung 10 tháng chuẩn. Gói 8/12 tháng → retiming theo `02-raw/knowledge/sop/09-timeline/10-thang-thuc-day.md` (SETUP bước 4).
2. Status flow: `todo → in-progress → qc → done` (+ `blocked`, `n/a`, `done*` = done có waiver).
3. Dòng có ◇ là decision gate (#6, #22, #25, #30). Chốt gate → ghi `gate: <verdict>` vào Ghi chú + link deliverable quyết định + log op `gate`. Gate GEO (G-T1 ở #14, G-ENT ở #13 — `tier-1-geo.md`) ghi cùng cách; G-BÀI/G-KH chấm per deliverable, không ghi ở bảng này.
4. Công đoạn có checklist trong ma trận M (CLAUDE.md §5): KHÔNG set `done` khi QC chưa PASS.
5. Công đoạn #13, #15, #16, #19: phần VIẾT BÀI chạy ở fork `Content Production - <client>/` — bảng này giữ plan/tracking/QC kết quả.

| # | Công đoạn | Tháng | WS | Deliverable | PIC | Thực thi | Duyệt | Status | QC | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Ký hợp đồng · OKRs năm & quý | T1 | 00+01 | | Account, SEO Lead Project | GTV | SEO Director | todo | — | HĐ trích vào `00-client-context/kpi-commitments.md` |
| 2 | Phân tích DN – website – thị trường – đối thủ | T1 | 03 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Gap theo page type + benchmark đầu ngành |
| 3 | Marketing Foundation | T1 | 00 | | Content Leader | GTV | SEO Lead Project | todo | — | Buyer Persona · Customer Journey · checklist content ngành · Brand Guideline · Source Context |
| 4 | Nhóm keyword thành topic → URL SEO | T1 | 05 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Topic → URL SEO + % keyword theo topic |
| 5 | SEO Audit toàn diện + Audit content (quý 1) | T1 | 03 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | 6 hạng mục + phân loại action full URL |
| 6 | ◇ Website cũ — có content? (decision) | T1 | 03 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Gate — ghi `gate: <verdict>` + link deliverable |
| 7 | Xử lý action audit content (xong hết T3) | T2→T3 | 03+06 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Plan ở 03, execute ở 06 · mốc cứng: xong hết T3 |
| 8 | Chiến lược + OKRs/KPI dự án | T1 | 01 | | SEO Lead Project | GTV | SEO Director | todo | — | Thứ tự triển khai topic + backup plan |
| 9 | Research Outer Section trước | T2 | 05 | | Content Leader | GTV | SEO Lead Project | todo | — | Ưu tiên trước để tạo Historical Data sớm |
| 10 | Topical Map + outer ước tính → SCN | T1→T2 | 05 | | SEO Lead Project | GTV | SEO Leader → SEO Director | todo | — | Demo T1 → chốt SCN đầu T2 · DoD 15 mục |
| 11 | Cấu trúc site + wireframe UX/UI | T1→T2 | 04 | | SEO Lead Project, CRO, Coder | GTV | SEO Leader | todo | — | Mốc cứng: lock ≤15 ngày đầu T2 · HTML template semantic · site-wide CRO T2→T3 |
| 12 | Kick-off dự án với khách hàng | T1 | 10 | | Account, SEO Lead Project | GTV | Account | todo | — | Chốt Tier 2 checklist được bật — ghi tại dòng này |
| 13 | Entity onsite/offsite + Content Entity (G2 Source-of-truth, gate G-ENT) | T1→T3 | 14 | | SEO Lead Project | GTV (Content Leader: bài entity · SEO: schema/NAP/offsite) | SEO Lead Project | todo | — | Cuối T1 → ≤15 ngày đầu T3 · plan `14-entity/` theo `_TEMPLATES/entity-plan.md` · viết bài ở fork Content Production · gate G-ENT (GE-11) pass trước khi mở #21 → ghi `gate: <verdict>` |
| 14 | GEO: G0 Readiness & Baseline + G1 Retrieval hygiene (gate G-T1) | T1→T3 | 08 | | SEO Lead Project, Coder | GTV | SEO Lead Project | todo | — | Readiness scorecard Tối thiểu/Chuẩn hoá ghi vào proposal · prompt set funnel + KPI GEO · bot access + speed + TTFP · gate G-T1 (GE-01·02·03) → ghi `gate: <verdict>` |
| 15 | Content URL SEO | T2→T3 | 05 | | Content Leader | GTV | SEO Lead Project | todo | — | Mốc cứng: xong hết T3 (trễ nhất ≤15 ngày đầu T4) · viết bài ở fork |
| 16 | Content Core Section 50-60% → 100% | T2→T3 | 05 | | Content Leader | GTV | SEO Lead Project | todo | — | 50-60% số bài trong T2 → 100% hết T3 |
| 17 | Plan traffic FULL + Content Strategy | T3→T4 | 05 | | Content Leader | GTV | SEO Director | todo | — | Plan ≥ cam kết +20% · Content Strategy chốt ≤15 ngày đầu T6 · 65% + bài traffic quan trọng xong T3-T4 |
| 18 | Internal link semantic | T4→T9 | 06 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Cụm URL SEO: T4 → 15 ngày đầu T5 · còn lại cuốn chiếu T5→T9 · orphan = 0 |
| 19 | Content non-URL SEO | T4→T7 | 05 | | Content Leader | GTV | SEO Lead Project | todo | — | Product details non-SEO + cluster/pillar · viết bài ở fork |
| 20 | Backlink nền + guest post phantom | T4→T5 | 07 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Target Phantom Keywords: `allintitle:` <1.000 tốt / <5.000 chấp nhận |
| 21 | GEO: G3 đợt 1 (audit chunk + rewrite AX1-AX7) + G4 off-site consensus | T4→T5 | 08 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Chỉ mở khi G-ENT pass · mỗi bài qua G-BÀI · consensus off-site T4→T7 · KHÔNG bán llms.txt/schema như lever (guardrail GE-05) |
| 22 | ◇ Initial ranking như kỳ vọng? (decision) | T4→T6 | 03 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Gate — audit initial ranking · ghi `gate: <verdict>` |
| 23 | Điều chỉnh content & onpage | T4→T6 | 06 | | SEO Lead Project, Content Leader | GTV | SEO Lead Project | todo | — | Re-ranking bài out-top 10-30 · chủ đạo T6→T9 theo audit |
| 24 | T6 · Audit định kỳ + OKRs Q3 + đo AI visibility | T6 | 03+01 | | SEO Lead Project | GTV | SEO Director | todo | — | OKRs quý 3 · đo AI visibility giữa kỳ |
| 25 | ◇ Gate Offpage — đẩy mạnh link? (decision) | T6 | 07 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Gate — Lưu đồ B · 90% dự án KHÔNG cần đẩy link · ghi `gate: <verdict>` |
| 26 | Backlink đẩy mạnh + textlink PR | T6→T8 | 07 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Đỉnh T6-T7 · textlink PR T7 → chốt T8 · anchor plan an toàn |
| 27 | Logfile + FULL audit toàn diện | T7 | 03 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Điều chỉnh full theo audit · technical sửa trước |
| 28 | GEO: G3 đợt 2 + research fan-out theo cluster | T7→T9 | 08 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | `geo-fanout-research` T7 (cluster ≤4/query) → triển khai T8 · ưu tiên query có AIO chưa được cite · deliverable `<CLIENT>_geo-dot-2_v<N>.md` |
| 29 | Giữa T8-T9: audit & tactic nâng cao | T8→T9 | 03 | | SEO Lead Project | GTV | SEO Lead Project | todo | — | Internal link trust · click depth · onpage Tier 2-3 (/31→/39) |
| — | Traffic users ⚠ (optional) | T8→T9 | — | | SEO Lead Project | GTV | SEO Director | n/a | — | Rủi ro cao — CHỈ chuyển `todo` khi SEO Director duyệt · phân biệt Content Traffic |
| 30 | ◇ Đạt KPI cam kết? (decision, OKRs T9) | T9 | 09 | | SEO Lead Project | GTV | SEO Director | todo | — | Gate — OKRs review T9 · ghi `gate: <verdict>` |
| 31 | Review Manager/Director → điều chỉnh | T9 | 10 | | SEO Lead Project | GTV | SEO Director | todo | — | Review dự án khó · chốt hướng điều chỉnh về đích |
| 32 | Báo cáo kép + case study | T10 | 09 | | Account | GTV | SEO Director | todo | — | Báo cáo kép KPI + AI visibility · case study (`expert-case-study`) · BBNT |
| 33 | Chuyển giao Duy trì | T10 | 11 | | SEO Lead Project, Account | GTV | SEO Director | todo | — | Theo `khung-duy-tri.md` · checklist bàn giao ký nhận · lịch duy trì quý |
| 34 | CRO: conversion path theo cụm intent + tracking chuyển đổi (gate G1 CR-06/07) | T2→T3 | 13 | | SEO Lead Project, CRO, Coder | GTV | SEO Leader | todo | — | `_TEMPLATES/conversion-path.md` · mốc cứng: tracking verify ≤ hết T3 · path ≤3 click, 1 CTA chính/trang · không đụng cấu trúc đã lock #11 |
| 35 | CRO: UX/UI feature brief per section/cụm intent + heatmap-recording đợt 1 | T4→T6 | 13 | | CRO, Coder | GTV | SEO Lead Project | todo | — | `_TEMPLATES/ux-feature-brief.md` + `heatmap-recording-review.md` · chỉ landing có traffic + ranking (CR-08) · Clarity/Hotjar gắn T4, đọc sau ≥2 tuần |
| 36 | CRO: tối ưu landing thương mại theo recording + A/B (CR-08→15, funnel CR-19) | T7→T9 | 13 | | CRO | GTV | SEO Director | todo | — | `heatmap-recording-review.md` đợt 2 + A/B log · 1 biến/lần, đủ mẫu · điểm rơi funnel → test kế tiếp |

### Format cột QC

| Giá trị | Nghĩa |
|---|---|
| `✅ 21/23 → [QC-05](03-audits/qc/QC-05-<slug>-<date>.md)` | PASS — score + link QC report |
| `❌ → [link]` | FAIL — link QC report, status giữ `qc` |
| `n/a` | Công đoạn không có checklist trong ma trận M |
| `waived (<người>)` | Miễn QC — ghi người chịu trách nhiệm, status thành `done*` |

## C. Nhịp định kỳ quý

| Nhịp | Mốc 1 | Mốc 2 | Mốc 3 | Mốc 4 |
|---|---|---|---|---|
| OKRs | ☐ Lập T1 | ☐ Quý 2 — T3 | ☐ Quý 3 — T6 | ☐ Review T9 |
| SEO Audit | ☐ Toàn diện T1 | ☐ Định kỳ T3-T4 | ☐ Logfile + full T6-T7 | ☐ Tổng kết T9-T10 |
| AI visibility | ☐ Baseline T1 | ☐ Giữa kỳ T6 | ☐ Báo cáo T10 | — |
| Báo cáo khách (WS09) | ☐ Tháng — ngày {{dd}} hằng tháng (theo kick-off) | ☐ Quý — T3 · T6 · T9 | ☐ Nghiệm thu — theo đợt HĐ | ☐ Báo cáo kép + BBNT + case study T10 |
| Content refresh (WS03 #24/#29) | ☐ Rà decay T6 | ☐ Rà decay T9 | — | — |
| CRO (WS13 #34–36) | ☐ Measurement plan + tracking QA ≤T3 · blocker P0 | ☐ Evidence-backlog + brief + heatmap đợt 1 T4-T6 | ☐ Rollout có theo dõi / A/B (nếu đủ mẫu) T7-T9 | — |
| Content tracking (WS05 `content_sync.py`) | ☐ T2 hằng tuần | ☐ Trước review tháng | — | — |

## D. Deliverable registry

| path | WS | công đoạn | ngày | status | QC report |
|---|---|---|---|---|---|
