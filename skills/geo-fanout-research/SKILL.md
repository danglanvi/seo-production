---
name: geo-fanout-research
description: "Tách prompt AI search thành subquery theo 8 lens, gom ≤4 cluster, đo mức phủ từng subquery theo section bằng EmbeddingGemma và map cluster về page/heading. Dùng khi research fan-out GEO trước outline hoặc tìm gap cluster của một topic."
metadata:
  version: "1.1.1"
---

# GEO Fan-out Research — sinh sub-query, gom cluster, map về page

Trả lời câu hỏi: **"Khi user hỏi AI câu Q, máy tách Q thành những cụm câu hỏi con nào, và site mình có passage trả lời từng cụm chưa?"** Đơn vị làm việc là **cluster**, không phải từng sub-query — vì ~90% fan-out gom được vào **≤4 cluster** và chỉ ~27% sub-query lặp lại giữa các lần chạy (Batch 40 wiki, 08/2026). Số sub-query tuyệt đối (8-12, 7,61…) đổi theo phiên bản model → **không in ra deliverable**.

**Vị trí trong quy trình:** công đoạn **28** (T7 research fan-out → T8 triển khai, `lop-geo-v2.md` §G3) · Phase 1 research trước outline (`seo-research` Bước 7 → skill này → `semantic-outline-methodology` Step 2 "Cluster fan-out → heading") · `topical-map-creation` Step 10b · input Bước 3 của `geo-content-optimization`. Đóng lỗ "công đoạn 28 không có skill thực thi" (review 29/08/2026).

## Phân vai

| Việc | Skill |
|---|---|
| Sinh fan-out, gom cluster, chấm ổn định, map cluster → page/heading, gap + AIO seed | **geo-fanout-research (skill này)** |
| Audit + rewrite chunk 1 trang theo cluster map | → `geo-content-optimization` (Bước 3 nhận cluster map từ đây) |
| Outline/AM mới theo cluster (mỗi cluster ≥1 heading) | → `semantic-outline-methodology` v2.1 |
| Gom keyword thành topic/URL theo SERP overlap (Google ranking) | → `serp-clustering` / `keyword-topic-url-mapping` — khác bản chất: skill này gom **câu hỏi con của AI**, không gom keyword theo SERP |
| Chọn prompt set tracking, đo citation share | → `geo-tracking-prompt-selection` |
| Quyết định page/heading/sentence cho gap | → rubric QDP `keyword-topic-url-mapping/references/qdp-gate.md` (skill này chỉ đề xuất mức, không quyết) |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| EmbeddingGemma 2 | Cos từng subquery với từng section của trang mình và trang trong top 10 | dùng: `mean_best` xếp trang được AI trích trên trang không được trích trong cùng top 10, AUC 0,674 dev và 0,683 holdout (30 prompt, 18/10/2026). Cos prompt gốc chỉ đạt 0,636 và 0,561. Không có ngưỡng phủ tuyệt đối. Ngoài top 10 thì ngược chiều (`references/muc-phu-gemma.md`) |
| Code (`fanout_cover.py`) | Tính cos, gộp theo trang, xuất bảng gap | dùng: phép tính phải tất định |
| Jev | Chấm subquery đã được phủ hay chưa | không dùng: chưa có rubric hiệu chuẩn. Verdict phủ cần đọc section |
| GLM Flash | Trích câu từ câu trả lời AI | không dùng: Claude tách ý của câu trả lời. Trích hàng loạt thuộc skill `geo-answer-lab` |
| Claude | Viết subquery theo lens, gom cluster, đọc section cos thấp, ra verdict COVERED / GAP | dùng |

## Input

**Required:**
- `$QUERIES` — 1-10 representative query (1 topic). Nhiều hơn → chia đợt.
- `$MARKET` — VN / US / khác + ngôn ngữ.

**Optional:**
- `$PAGES` — URL/outline hiện có của site cho topic (để map cluster → page/heading). Không có → chỉ xuất cluster map + đề xuất page.
- `$AI_ANSWERS` — câu trả lời AI hiện tại (AI Mode / ChatGPT / AIO) do user paste, kèm engine + ngày + model version.
- `$SERP_DATA` — PAA, related searches, AIO text (từ `seo-research` primer S5/S3, screenshot, DataForSEO).
- `$ENGINE` — ưu tiên Google AI (AI Mode/AIO) hay ChatGPT; mặc định cả hai (2 kênh bắt buộc, `geo-tracking-prompt-selection` v1.3).

**Path detection (evidence):**
1. **Path A — tool:** Firecrawl/Tavily search cho `$QUERIES` → PAA + related + AIO text; AI-search access (nếu cấu hình) → câu trả lời AI Mode/ChatGPT. Báo số call trước khi gọi.
2. **Path B — user paste:** AI answer + PAA screenshot. Đủ cho mọi bước.
3. **Path C — mô phỏng LLM thuần:** không có evidence ngoài → cluster map gắn nhãn **`simulated`**, chỉ dùng để tìm gap sơ bộ, không dùng làm số báo cáo.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,gemma?,firecrawl?,tavily?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `gemma`: bỏ Bước 4a. Claude đọc từng section và ghi "chưa đo Gemma".

### Bước 0b — Gate + scope
- Topic đã có page rank page-one cho ≥1 query chưa? Chưa → vẫn chạy được (research phục vụ outline), nhưng ghi rõ "chưa có vé dự thi — output cho Phase 2, không cho audit" (gate G-T1).
- Chốt `$QUERIES` (≤10) + `$ENGINE`; ghi **ngày + model version** cho mọi evidence (fan-out là moving target — ChatGPT đổi format search 3 lần từ 06/2026; trường `search_queries` biến mất 16-20/08/2026 → tool đọc trường đó trả rỗng).

### Bước 1 — Seed fan-out theo 8 lens
Với mỗi query sinh sub-query theo 8 lens ([references/fanout-lenses.md](references/fanout-lenses.md)): **định nghĩa/là gì · cách làm/quy trình · so sánh/thay thế · chi phí/giá · đối tượng/phù hợp ai · rủi ro/nhược điểm/sai lầm · bằng chứng/đánh giá/uy tín · địa phương/thời điểm/điều kiện**. Mỗi lens 1-3 sub-query bằng ngôn ngữ user (VN/EN theo `$MARKET`). Đây là **seed**, chưa phải evidence.

### Bước 2 — Evidence thật (Path A/B)
- **PAA + related searches** (Google): thêm câu hỏi thật, đánh dấu `observed`.
- **AI answer hiện tại**: tách câu trả lời thành các đoạn/ý → mỗi đoạn suy ngược ra câu hỏi con nó đang trả lời (AI Mode/AIO trả lời theo cấu trúc fan-out) → đánh dấu `observed-answer`; ghi nguồn được cite per đoạn.
- Lặp **≥3 lần chạy** (khác phiên/ngày/wording) nếu có Path A; đánh dấu sub-query xuất hiện ≥2/3 lần = **stable**, 1/3 = **volatile**.
- Không có Path A/B → Path C, nhãn `simulated`, bỏ qua chấm ổn định.

### Bước 3 — Gom cluster ≤4
- Gom sub-query theo **facet của intent** (không theo từ khoá): thường rơi vào 3-4 cluster như *hiểu (định nghĩa+cơ chế)* · *chọn/so sánh (tiêu chí, thay thế, giá)* · *làm (quy trình, điều kiện, sai lầm)* · *tin (bằng chứng, uy tín, rủi ro)*. >4 cluster → gộp lại theo câu hỏi user thực sự muốn trả lời; cluster chỉ có sub-query `volatile` → hạ thành "quan sát thêm".
- Mỗi cluster ghi: tên cluster · câu hỏi đại diện · sub-query thuộc (stable/volatile/seed) · engine nào tách ra · nguồn AI đang cite cho cluster (nếu có answer).
- **Cluster ngoài Central Search Intent của topic** (vd hỏi "SEO là gì" mà fan-out ra "học SEO ở đâu") → ghi riêng mục "cluster lân cận" — ứng viên page khác, không nhồi.

### Bước 4 — Map cluster → page / heading / passage (khi có `$PAGES`)
| Cluster | Page phụ trách | Heading khớp | Passage tự đứng? | Cos Gemma (trang mình / tốt nhất pool) | Verdict |
|---|---|---|---|---|---|
| … | URL hoặc "chưa có" | H2/H3 + mức khớp (khớp/gần/lệch) | ✅/❌ (câu đầu = answer, không hồi chỉ) | từ Bước 4a, hoặc "chưa đo" | COVERED / GAP-HEADING / GAP-PAGE |

- GAP-HEADING: page đúng nhưng thiếu heading → đề xuất heading (K2Q) + Subordinate Text.
- GAP-PAGE: không page nào → đề xuất mức theo QDP (page / heading / sentence — rubric `qdp-gate.md`; skill chỉ đề xuất).
- Title/meta/slug của page phụ trách có chứa từ vựng cluster không (AX7 — cổng lọc title+meta+URL)?

### Bước 4a — Đo mức phủ từng subquery theo section (Gemma)
Đọc `references/muc-phu-gemma.md`. Đặt `S` = `skills/geo-fanout-research/scripts/fanout_cover.py`.

1. Dựng store gồm trang mình và top 10 SERP của từng prompt bằng skill `site-vector-index`.
2. Ghi `<W>/subq.jsonl` với các trường `id`, `query_id`, `lens`, `text`. Ghi `<W>/pools.jsonl` với `id` là prompt, `text`, `candidates` là URL trang mình và top 10.
3. Chạy `~/.venvs/embeddinggemma/bin/python -B -I $S cover --store <store> --subq <W>/subq.jsonl --pools <W>/pools.jsonl --out <W>/cover.jsonl --detail <W>/detail.jsonl`.
4. So `mean_best` của trang mình với trang khác trong cùng pool. Nếu trang mình đứng dưới trang được AI trích, xếp prompt đó lên đầu danh sách gap.
5. Chạy `python3 -B -I $S gaps --detail <W>/detail.jsonl --query-id <prompt> --url <URL trang mình> --out <W>/gaps_<prompt>.md`.
6. Đọc ngưỡng phủ (rubric `geo-fanout-coverage`) theo thứ tự: registry của site (`00-client-context/model-calibration.json`) → `tools/ai-assist/calibration-defaults.json`. Nếu chưa có ngưỡng, không truyền `--cover-at`.
7. Đọc section thắng của subquery cos thấp nhất trước. Claude ra verdict COVERED hoặc GAP cho từng subquery, rồi gộp lên cluster ở bảng Bước 4.

### Bước 5 — AIO counter-positioning seed (khi có `$AI_ANSWERS`)
Facts AI đang nêu + nguồn được cite → facts **bỏ sót** mà nguồn đáng tin có → danh sách "fact cần cover + nguồn + năm" (GE-27) + format AI ưa (định nghĩa đầu, list có cấu trúc, bảng) → chuyển cho outline/AM hoặc `geo-content-optimization` Bước 4.

### Bước 6 — Output + bàn giao
File: `<project>_Fanout-Cluster-Map_<topic>_v1.md` → tài liệu nội bộ «<project>» (ngoài repo, hỏi Lead/Vincent) (hoặc `05-content-plan/` trong SEO Production; `03-research/` trong Content Production).

```markdown
# Fan-out Cluster Map — <topic>
> Queries: <q1; q2…> · Market: <VN/US> · Engine: <AI Mode/AIO/ChatGPT> · Evidence: <Path A/B/C — simulated?> · Ngày + model version: <…> · Số lần chạy: <n>

## 1. Cluster map (≤4/query)
| Cluster | Câu hỏi đại diện | Sub-query (stable ● / volatile ○ / seed ◌) | Engine | Nguồn AI đang cite |
## 2. Cluster lân cận (ngoài CSI — ứng viên page khác)
## 3. Coverage map (nếu có $PAGES) — bảng Bước 4 + verdict
## 4. Gap + đề xuất: GAP-HEADING (heading + Subordinate Text) · GAP-PAGE (mức QDP đề xuất) · AX7 title/meta
## 5. AIO counter-positioning seed (facts bỏ sót + nguồn + năm; format AI ưa)
## 6. Bàn giao: → semantic-outline-methodology (cluster → heading) / geo-content-optimization Bước 3 / topical-map-creation 10b
## Nguồn số liệu + hạn dùng
```

Template đầy đủ + cách chấm ổn định: [references/cluster-map-template.md](references/cluster-map-template.md).

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Verdict COVERED hoặc GAP của từng subquery do Claude đọc section, không do một ngưỡng cos. Nguồn lỗi: hiệu chuẩn 19/10/2026, cặp subquery × trang không có ngưỡng nhận nào đạt precision 0,95 so với trích dẫn AI thật.
- [ ] Mức phủ chỉ so trong cùng top 10 của một prompt. Nguồn lỗi: pilot 10/2026, AUC trên mọi URL được trích ngược chiều (0,35 với prompt gốc, 0,40 với fan-out).
- [ ] Gap có cột so với trang được trích cùng prompt, kèm cos của từng bên. Nguồn lỗi: pilot 19/10/2026, trang của site mình có cos prompt gốc cao nhất top 10 nhưng không được trích; fan-out cho thấy trang đó thua trang được trích ở 3/6 subquery.
- [ ] Subquery viết trước khi xem trang nào được trích, và ghi ngày, engine, model version của mọi evidence. Nguồn lỗi: trường `search_queries` của ChatGPT biến mất 16–20/08/2026, tool đọc trường đó trả rỗng.
- [ ] Tài liệu khách không có số fan-out tuyệt đối hay số cos trần. Số Gemma đi kèm câu "chỉ số mô phỏng, trọng số thật của Google chưa công bố". Nguồn lỗi: register GEO 08/2026 chặn số 8–12 và 7,61 vì số đổi theo version model.

## Behavior Gates

1. **Think Before** — chốt `$QUERIES`, `$MARKET`, engine, path evidence trước khi sinh; MCP → báo số call, chờ xác nhận. Query dạng transactional/shopping ngắn → nói rõ AIO trigger thấp (Shopping 3,2%), ROI thấp.
2. **Evidence** — mọi cluster ghi nhãn `observed` / `observed-answer` / `seed` / `simulated`; mọi số có nguồn + tháng; **không in số fan-out tuyệt đối** (8-12, 7,61, "28 sub-queries") — blacklist register `wiki/syntheses/geo-evidence-register-2026-08`; date-stamp model version.
3. **Surgical** — output là cluster map + gap + seed; không viết bài, không sửa outline, không rewrite chunk (trỏ đúng skill).
4. **Goal-driven** — mục tiêu = mỗi cluster thuộc CSI có ≥1 passage tự đứng trong network (coverage ở cấp network, focus ở cấp page — Indig 815k pairs); không phải "cover mọi sub-query trong 1 bài".

## Anti-patterns

- ❌ Đuổi từng sub-query (chỉ ~27% lặp lại) → làm theo cluster.
- ❌ Nhồi mọi cluster vào 1 page "cho đủ coverage" → 26-50% subtopic thắng 100%; cluster ngoài CSI → page khác.
- ❌ Dùng cluster map `simulated` làm số báo cáo khách.
- ❌ Gom theo từ khoá/SERP overlap (việc `serp-clustering`) thay vì theo facet câu hỏi.
- ❌ Coi PAA = fan-out (PAA là evidence bổ sung, không phải cơ chế AI Mode).
- ❌ Hứa "cover cluster X sẽ được cite" — probabilistic; cam kết aggregate SoV theo topic.

## References & wiki

- [references/fanout-lenses.md](references/fanout-lenses.md) — 8 lens + template VN/EN + ví dụ 2 topic (informational · commercial).
- [references/cluster-map-template.md](references/cluster-map-template.md) — template output, quy tắc gom cluster, chấm ổn định, verdict coverage.
- [references/muc-phu-gemma.md](references/muc-phu-gemma.md) — đo mức phủ subquery theo section bằng Gemma, số hiệu chuẩn 19/10/2026, giới hạn.
- Wiki: [[Query Fan-Out]] · [[AI Mode]] · [[AI Overviews]] · [[ChatGPT Pipeline]] · [[Core Source]] · [[QDP-QDH-QDS]] · [[sources/chatgpt-fanout-28k-nectiv-2026]] · [[sources/how-ai-engines-choose-sources-surfer]] · [[syntheses/geo-evidence-register-2026-08]].
- SOP: `sop/09-timeline/lop-geo-v2.md` §G3 (T7 research fan-out) · `sop/06-self-checklist/tier-1-geo.md` GE-17 · `sop/08-onpage-checklist.md` AX7.

## Changelog

- **v1.1.1 (2026-10-19):** đổi tên mục "## Workflow" thành "## Quy trình" để lệnh kiểm cấu trúc thấy Bước 0 đúng chỗ.
- **v1.1 (2026-10-19):** Bước 0 kiểm tool. Bước 4a đo mức phủ từng subquery theo section bằng EmbeddingGemma (`scripts/fanout_cover.py`, `references/muc-phu-gemma.md`): `mean_best` có tín hiệu trong top 10 (AUC 0,674 dev, 0,683 holdout), không có ngưỡng phủ tuyệt đối nên Claude ra verdict. Thêm phân việc model, tự phản biện, test offline `tests/test_fanout_cover.py`.
- **v1.0 (2026-08-29):** khởi tạo (Vincent chốt Q5 29/08 — skill riêng, `seo-research` gọi). 6 bước: gate → seed 8 lens → evidence PAA/related/AI answer (≥3 lần chạy, stable/volatile) → gom cluster ≤4 → map page/heading/passage (COVERED / GAP-HEADING / GAP-PAGE + AX7) → AIO counter-positioning seed → bàn giao. Nguồn: Batch 40 wiki (cluster ≤4 / 27% ổn định), Indig 815k pairs, Nectiv 28k fan-out, McSweeney pipeline (≈), FINDINGS 22/08/2026 §2.2.
