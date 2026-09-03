# Cheat-sheet WS08 — GEO & AI Visibility

> Chưng cất từ `skills/geo-content-optimization/SKILL.md` v1.2 + `skills/geo-tracking-prompt-selection/SKILL.md` v1.3 — sync 2026-08-29 (bản trước 2026-07-17 còn AX1-AX5 / 8-12 sub-queries / 375 từ — đã hết hạn). Canonical: **AX1-AX7** trong `02-raw/knowledge/sop/08-onpage-checklist.md` (chấm riêng, không tính vào /39) · **GE-01…GE-37** trong `02-raw/knowledge/sop/06-self-checklist/tier-1-geo.md` v2.0.2 · quy trình 6 điểm chạm `02-raw/knowledge/sop/09-timeline/lop-geo-v2.md`.

## 1. Mục tiêu WS

Brand được AI engines (ChatGPT + Google AI = AI Overviews / AI Mode / Gemini — 2 chiến trường bắt buộc; Perplexity/Copilot bổ sung) trích dẫn lặp lại → thành Core Source; đo được citation share vs đối thủ theo **topic** với prompt set cố định; đối chiếu bằng **referral + conversion thật** trong GA4.

- Công đoạn phụ trách (lớp GEO v2): **#14** G0+G1 (gate G-T1) · **#13** G2 entity/source-of-truth (gate G-ENT, phối hợp WS06) · **#21** G3 đợt 1 + G4 consensus · **#24** G5 giữa kỳ · **#27** G1 verify crawler · **#28** G3 đợt 2 + research fan-out theo cluster · **#32/#33** G5 báo cáo kép + handover.

## 2. Input / Output

| Input | Output |
|---|---|
| Bài đã indexed + rank (từ WS05/WS06) + 1-5 target queries/bài; robots.txt/CDN rule của domain | GEO Readiness verdict + baseline + prompt set → `_TEMPLATES/geo-baseline.md` v2, lưu `08-geo-ai-visibility/` |
| AI answer hiện tại cho queries (paste được, không cần MCP) | GEO audit (Bộ BÀI /12) + rewrite đề xuất per chunk (per bài) |
| Danh sách competitor (5-7) + core services / top categories | Bàn giao đo lường: pages + queries + ngày optimize + baseline + register số liệu có hạn dùng |

## 3. Khung 2 lớp

- **Optimize (geo-content-optimization v1.2):** AX1-AX7 per page — thắng ở bước retrieval + chunk selection + passage verifiability. Chạy ở G3, SAU gate G-ENT.
- **Measure (geo-tracking-prompt-selection v1.3):** Readiness scorecard → prompt set theo funnel → KPI citation share theo topic, tách engine — đo aggregate, ≥3 lần chạy/prompt, date-stamp model version.
- **5 Core Levers** (thứ tự sức mạnh predictor): rank status (gate) → heading↔cluster alignment → chunk quality (AX1+AX2+AX6) → freshness → KDD tactics (quote nguồn > số liệu > cite nguồn đứng riêng).

## 4. Checklist rút gọn (12 dòng)

1. **Gate G-T1:** page indexed + rank page-one cho ≥1 sub-query; **AI crawler search/user-triggered không bị chặn** (robots/CDN); có baseline. Fail → dừng lớp GEO, quay về `/seo-onpage` / topical map.
2. **Gate G-ENT (≤T3):** `site:domain` trả lời được 5-10 câu thương mại cơ bản (giá / tính năng / so sánh / chính sách) bằng text trên site chính chủ — chưa xong thì chưa mở đợt FS/AIO.
3. **AX1 chunk tự đứng:** không cap số từ section; 1 heading = 1 facet; không đại từ hồi chỉ xuyên section; khối ý <~200 từ; heading tổ tiên có nghĩa; mỗi câu tự đứng S-V-O.
4. **AX2 front-load:** 100-150 từ đầu = answer (overlap ≥5/10 key terms pass, <3/10 rewrite); không storytelling intro; keyword 100 chữ đầu VÀ cuối (P16); bài informational chính có Key-Facts table.
5. **AX3 alignment:** fan-out gom **cluster ≤4** (không đuổi từng query); mỗi cluster ≥1 heading + 1 passage tự đứng; title/meta/slug chứa từ vựng cluster (cổng lọc title+meta+URL của ChatGPT).
6. **AX3 counter-positioning:** extract facts trong AI answer hiện tại → fact coverage của bài → bổ sung gap; thêm quote nguồn + số liệu + cite nguồn (KDD 2024 primary — không hứa %).
7. **AX4 hygiene:** canonical tự trỏ, đã index, không noindex ngoài ý muốn, featured image indexed.
8. **AX5 Blur Test:** screenshot blur 50% vẫn nhận ra topic + function của trang.
9. **AX6 passage verifiability:** 3-6 claim quan trọng, mỗi claim = 1 câu S-V-O có số + nguồn + ngày, nằm dưới đúng heading của cluster (linkify 2 pha — document nuôi summary ≠ document được cite).
10. **Scope page:** không dải số từ / số heading cố định — độ dài theo loại node (pillar/quality node dài hơn leaf), benchmark đối thủ, intent, vị trí topical map, query target; bài gánh ≥2 câu hỏi chính → TÁCH page (26-50% subtopic thắng 100%) — không phình ultimate guide. Freshness = update nội dung thật (~30 ngày commercial); content năm cũ không chết — không re-stamp năm.
11. **Prompt set:** Service/Agency = funnel 28-40 prompts (BOFU 50% · MOFU 35% · TOFU 15%); E-commerce = matrix Category × Intent × Segment 80-100 + seasonal. Chạy trên **ChatGPT + AI Mode + Gemini** (bắt buộc), AIO theo keyword; Perplexity/Copilot bonus; Information Accuracy + branded-prompt defense bắt buộc.
12. **Đo T1/T6/T10 + weekly nội bộ:** aggregate SoV theo topic, tách engine (AIO ≠ AI Mode 13,7% trùng); **GA4 channel "AI Assistant"** (sessions + conversion, AI CVR vs Organic) + GSC Generative AI (Beta) + Ahrefs AI responses/Brand Radar (found vs cited) — đối chiếu referral thật trước khi claim win; mọi số dán nhãn directional + ngày + model version.

## 5. Ngưỡng pass

| Hạng mục | Ngưỡng |
|---|---|
| Readiness + Baseline (#14) | Verdict Tối thiểu/Chuẩn hoá ghi proposal; prompt set chốt; citation share brand vs đối thủ đo được theo topic; gate G-T1 PASS |
| Đợt FS/AIO (#21, #28) | Bộ BÀI /12 chấm per page (Sheet "GEO Checklist GE v2"); chunk REWRITE có bản rewrite 100-170 từ, câu 1 = answer; AX6 n/m claim PASS |
| KPI tracking | Brand mention >60% BOFU prompts **trên cả ChatGPT lẫn Google AI** · SOV >30% · information accuracy >90% · AI citations trend tăng (directional) |
| Đối chiếu thật | GA4 AI Assistant sessions + key events cùng kỳ; <100 session → "chưa đủ mẫu" |
| Retrievability scorecard | Chấm per page theo 5 levers; chỉ rewrite chunk FAIL, chunk PASS không chạm; restructure trước, thêm chữ sau |

## 6. Skill gọi + luật nạp

| Skill | Khi nào nạp |
|---|---|
| `skills/geo-tracking-prompt-selection/` v1.3 | Readiness, prompt set, KPI, GA4 AI Assistant setup, đo citation share (#14, #24, #32) |
| `skills/geo-content-optimization/` v1.2 | Audit + rewrite chunk bài đã publish (#21, #28) — sau gate G-ENT |

Luật nạp: references/ nạp từng file theo bước (`chunk-audit-method.md` khi chấm chunk/AX6; `geo-levers-map.md` khi map lever + dải amber rank 11-50; `kpis-metrics.md` § GA4 khi setup đo; `prompt-templates.md` / `ecommerce-matrix.md` khi build prompt set). HTML structure → `semantic-html-optimization`; viết bài mới → fork Content Production (gate G-BÀI đã nằm trong pipeline). Research fan-out cho cả topic (#28) → skill `geo-fanout-research` (đang xây, Đợt 4) — tạm thời làm thủ công theo Bước 3 của geo-content-optimization.

## 7. 7 lỗi thường gặp

1. Đề xuất llms.txt làm GEO lever — AI crawlers không request file này; điều khiển crawler = robots.txt.
2. Tính schema vào retrievability score — causal test: schema KHÔNG tăng AI citation (≈0%).
3. Đẩy bài thành ultimate guide "cho đủ coverage" — ngược evidence; tách page thay vì phình page.
4. Date-spoofing / fake refresh date — Google xử như spam; freshness phải là update nội dung thật.
5. Hứa deterministic với client ("làm xong sẽ được cite") hoặc track prompt generic không có conversion value — chỉ cam kết mức aggregate + Core Source.
6. Audit chunk khi bot AI còn bị chặn, hoặc đuổi từng fan-out query thay vì cluster.
7. In số blacklist ra deliverable khách (8-12 sub-queries, 7,61, +115%, "+40%", cosine 0,90, 375 từ, 128 token, 2s, "Gecko Score/Jetstream") — chỉ whitelist của register `wiki/syntheses/geo-evidence-register-2026-08`.
