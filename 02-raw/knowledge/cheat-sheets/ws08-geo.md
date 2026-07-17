# Cheat-sheet WS08 — GEO & AI Visibility

> Chưng cất từ `skills/geo-content-optimization/SKILL.md` + `skills/geo-tracking-prompt-selection/SKILL.md` — sync 2026-07-17. AX1-AX5 canonical nằm trong `02-raw/knowledge/sop/08-onpage-checklist.md` (chấm riêng, không tính vào /39).

## 1. Mục tiêu WS

Brand được AI engines (AI Overviews, AI Mode, ChatGPT, Perplexity) trích dẫn lặp lại → thành Core Source; đo được citation share vs đối thủ theo prompt set cố định.

- Công đoạn phụ trách: **#14** (GEO baseline + Technical, T1→T3) · **#21** (FS & AIO đợt 1 + consensus) · **#28** (FS & AIO đợt 2 + research fan-out).

## 2. Input / Output

| Input | Output |
|---|---|
| Bài đã indexed + rank (từ WS05/WS06) + 1-5 target queries/bài | GEO baseline + prompt set → `_TEMPLATES/geo-baseline.md`, lưu `08-geo-ai-visibility/` |
| AI answer hiện tại cho queries (paste được, không cần MCP) | GEO audit + rewrite đề xuất per chunk (per bài) |
| Danh sách competitor (5-7) + core services / top categories | Bàn giao đo lường: pages + queries + ngày optimize + baseline |

## 3. Khung 2 lớp

- **Optimize (geo-content-optimization):** AX1-AX5 per page — thắng ở bước retrieval + chunk selection.
- **Measure (geo-tracking-prompt-selection):** prompt set theo funnel + KPI citation share — đo aggregate, không đo 1 query.
- **5 Core Levers** (thứ tự sức mạnh predictor): rank status (gate) → heading↔query alignment → chunk quality (AX1+AX2) → freshness → KDD tactics (statistics + quotes + cite sources).

## 4. Checklist rút gọn (10 dòng)

1. **Gate nền:** page phải indexed + rank page-one cho ít nhất 1 sub-query. Chưa rank → quay về pipeline SEO thường (`/seo-onpage`), GEO sau — "Classic SEO enables AI rankings".
2. **AX1 chunk self-containment:** mỗi H2 section ≤~375 từ, cắt rời vẫn đủ entity + context + claim; không đại từ hồi chỉ ("như đã nói ở trên"); câu 1 sau heading = câu trả lời heading.
3. **AX2 front-load:** first 100-150 từ answer-first (overlap ≥5/10 key terms = pass, <3/10 = rewrite); best content trong 30% đầu trang; keyword trong 100 chữ đầu VÀ cuối (P16).
4. **AX3 alignment:** fan-out 8-12 sub-queries per query; heading match trực tiếp sub-query; Title match sub-questions nội bộ của AI; URL slug natural-language.
5. **AX3 counter-positioning:** extract facts trong AI answer hiện tại → chấm fact coverage của bài → bổ sung gap; thêm statistics + expert quote + cite nguồn (KDD top-3 tactics).
6. **AX4 hygiene:** canonical tự trỏ, đã index, không noindex ngoài ý muốn, featured image indexed.
7. **AX5 Blur Test:** screenshot blur 50% vẫn nhận ra topic + function của trang.
8. **Page spec:** 500-2.000 từ, 7-20 subheadings; bài cover quá rộng → TÁCH page (cover 26-50% subtopics THẮNG 100%) — không phình ultimate guide.
9. **Prompt set:** Service/Agency = funnel 28-40 prompts (BOFU 50% · MOFU 35% · TOFU 15%; ưu tiên comparison/pricing/review); E-commerce = matrix Category × Intent × Segment 80-100 prompts + seasonal. Luôn kèm 5-7 competitor để benchmark.
10. **Nhịp đo T1/T6/T10:** baseline T1 → đo giữa kỳ T6 (cùng audit #24) → báo cáo T10. Đo aggregate AI Share of Voice (AIO bề mặt đổi ~2,15 ngày — thắng TOPIC, không thắng query); track AIO và AI Mode thành 2 kênh riêng; freshness = update nội dung THẬT theo chu kỳ ~30 ngày.

## 5. Ngưỡng pass

| Hạng mục | Ngưỡng |
|---|---|
| Baseline (#14) | Prompt set chốt + citation share brand vs đối thủ đo được per prompt |
| Đợt FS/AIO (#21, #28) | Có danh sách query + kết quả cite per query; chunk REWRITE có bản rewrite 100-170 từ, câu 1 = answer |
| KPI tracking | Brand mention >60% BOFU prompts · SOV >30% · information accuracy >90% · AI citations trend tăng |
| Retrievability scorecard | Chấm per page theo 5 levers; chỉ rewrite chunk FAIL, chunk PASS không chạm |

## 6. Skill gọi + luật nạp

| Skill | Khi nào nạp |
|---|---|
| `skills/geo-content-optimization/` | Audit + rewrite chunk bài đã publish (#21, #28) |
| `skills/geo-tracking-prompt-selection/` | Chọn prompt set, KPI, đo citation share (#14, #24, #32) |

Luật nạp: references/ nạp từng file theo bước (`chunk-audit-method.md` khi chấm chunk; `geo-levers-map.md` khi map lever; `prompt-templates.md` / `ecommerce-matrix.md` khi build prompt set). HTML structure → `semantic-html-optimization`; viết bài mới → fork Content Production.

## 7. 5 lỗi thường gặp

1. Đề xuất llms.txt làm GEO lever — AI crawlers không request file này; điều khiển crawler = robots.txt.
2. Tính schema vào retrievability score — causal test: schema KHÔNG tăng AI citation (≈0%).
3. Đẩy bài thành ultimate guide "cho đủ coverage" — ngược evidence; tách page thay vì phình page.
4. Date-spoofing / fake refresh date — Google xử như spam; freshness phải là update nội dung thật.
5. Hứa deterministic với client ("làm xong sẽ được cite") hoặc track prompt generic không có conversion value — chỉ cam kết mức aggregate + Core Source.
