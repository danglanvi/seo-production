---
name: geo-fanout-research
description: "Research query fan-out cho AI search (Google AI Mode / AI Overviews / ChatGPT) rồi gom thành cluster ≤4 per query — DATA layer cho GEO: sinh sub-query theo 8 lens + evidence PAA/related/AIO, chấm ổn định qua ≥3 lần chạy, map cluster → page/heading/passage hiện có, xuất cluster ma."
metadata:
  version: "1.0"
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

## Workflow

### Bước 0 — Gate + scope
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
| Cluster | Page phụ trách | Heading khớp | Passage tự đứng? | Verdict |
|---|---|---|---|---|
| … | URL hoặc "chưa có" | H2/H3 + mức khớp (khớp/gần/lệch) | ✅/❌ (câu đầu = answer, không hồi chỉ) | COVERED / GAP-HEADING / GAP-PAGE |

- GAP-HEADING: page đúng nhưng thiếu heading → đề xuất heading (K2Q) + Subordinate Text.
- GAP-PAGE: không page nào → đề xuất mức theo QDP (page / heading / sentence — rubric `qdp-gate.md`; skill chỉ đề xuất).
- Title/meta/slug của page phụ trách có chứa từ vựng cluster không (AX7 — cổng lọc title+meta+URL)?

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
- Wiki: [[Query Fan-Out]] · [[AI Mode]] · [[AI Overviews]] · [[ChatGPT Pipeline]] · [[Core Source]] · [[QDP-QDH-QDS]] · [[sources/chatgpt-fanout-28k-nectiv-2026]] · [[sources/how-ai-engines-choose-sources-surfer]] · [[syntheses/geo-evidence-register-2026-08]].
- SOP: `sop/09-timeline/lop-geo-v2.md` §G3 (T7 research fan-out) · `sop/06-self-checklist/tier-1-geo.md` GE-17 · `sop/08-onpage-checklist.md` AX7.

## Changelog

- **v1.0 (2026-08-29):** khởi tạo (Vincent chốt Q5 29/08 — skill riêng, `seo-research` gọi). 6 bước: gate → seed 8 lens → evidence PAA/related/AI answer (≥3 lần chạy, stable/volatile) → gom cluster ≤4 → map page/heading/passage (COVERED / GAP-HEADING / GAP-PAGE + AX7) → AIO counter-positioning seed → bàn giao. Nguồn: Batch 40 wiki (cluster ≤4 / 27% ổn định), Indig 815k pairs, Nectiv 28k fan-out, McSweeney pipeline (≈), FINDINGS 22/08/2026 §2.2.
