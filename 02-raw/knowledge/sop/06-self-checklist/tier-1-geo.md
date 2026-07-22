---
type: sop
tier: 1
phase: geo-ai-visibility
last_updated: 2026-07-19
source_file: "sop/08-onpage-checklist.md (AX1-AX5) + skills/geo-content-optimization + skills/geo-tracking-prompt-selection + GEO.md (5 Core Levers)"
items_count: 13
related:
  - "[[GEO]]"
  - "[[Audition Chunk]]"
  - "[[Core Source]]"
  - "[[Query Fan-Out]]"
  - "[[AI Overviews]]"
  - "[[Subordinate Text Match]]"
  - "[[Structured Data]]"
tags: [sop, tier-1, geo, ai-visibility, ai-overviews, self-checklist]
---

# Tier 1 — Self-Checklist: GEO / AI-Visibility (GE-01…GE-13)

> **Khi dùng:** Lớp GEO chạy song song quy trình T1-T10 — người làm content + SEO tự check theo 4 trụ: TECHNICAL (T1-T3) · CONTENT (mỗi bài publish/refresh) · OFFSITE (T4-T7) · ĐO LƯỜNG (T1 → T6 → T10).
> **Số items:** 13. **Scoring:** Self Score /13 → Self %.
> **Nguyên tắc REUSE:** checklist này KHÔNG chế khái niệm mới — item content map thẳng về **AX1-AX5** (`sop/08-onpage-checklist.md`, canonical) và **5 Core Levers** (GEO.md, operationalize bởi skill `geo-content-optimization`). AX chấm riêng, không tính vào /39 của P-series.

## 🔴 P0 Gate — 5 items PHẢI pass

| Gate | Item | Điều kiện |
|---|---|---|
| G1 | GE-02 | Page indexed + có rank (page-one cho ≥1 sub-query) — chưa rank thì GEO chưa có "vé dự thi", quay về pipeline SEO thường |
| G2 | GE-03 | Chunk self-contained (AX1) |
| G3 | GE-04 | Front-load answer (AX2) |
| G4 | GE-05 | Heading-query alignment (AX3) |
| G5 | GE-11 | Prompt set baseline chốt tại T1 — không có baseline thì T6/T10 không có gì để so |

## 🔴 GUARDRAIL bắt buộc (ghi nhớ khi nói chuyện với khách — GE-13)

1. **llms.txt ≠ citation lever.** Google không dùng (Mueller so với keywords meta tag); log 2025: GPTBot/ClaudeBot/PerplexityBot không request file này. Điều khiển AI crawler = `robots.txt`. KHÔNG đưa llms.txt vào deliverable.
2. **Schema ≠ AI-citation lever.** Causal test (DiD) Ahrefs 1.885 pages: thêm schema KHÔNG tăng AI citation (AI Mode +2,4%, ChatGPT +2,2% ≈ 0). Schema vẫn đáng làm cho rich results/entity — việc khác, không cam kết citation.
3. **Không cam kết deterministic** ("làm xong sẽ được cite") — AI output probabilistic, AIO đổi ~2,15 ngày; chỉ cam kết ở mức aggregate SoV + Core Source.

---

## Trụ 1 — TECHNICAL (T1-T3)

> Pointer sang `tier-3-technical-advance.md` — KHÔNG duplicate ngưỡng ở đây.

| ID | Item | Tiêu chí ĐẠT | Reuse |
|---|---|---|---|
| GE-01 | **Speed / TTFB nền** | Mục speed của `tier-3-technical-advance.md` pass (response time <200ms tốt, <350ms tối thiểu). Note GEO: TTFB target <700ms, hard timeout 2s của ChatGPT fetcher = "reverse-engineered estimate", note-only | tier-3-technical §0, §2.1 |
| GE-02 | 🔴 **Indexed + rank + hygiene (AX4)** | Page indexed, canonical tự trỏ, không noindex ngoài ý muốn, featured image indexed; có page-one presence cho ≥1 sub-query (retrieval rank = predictor mạnh nhất: position 0 = 58% citation vs position 10 = 14%) | AX4 + gate Bước 0 `geo-content-optimization` |

## Trụ 2 — CONTENT (mỗi bài publish / refresh)

| ID | Item | Tiêu chí ĐẠT | Reuse |
|---|---|---|---|
| GE-03 | 🔴 **Chunk self-contained (AX1)** | Mỗi H2 section ≤~375 từ, cắt rời vẫn đủ Entity + context + claim; câu trả lời trực tiếp 40-50 từ ngay sau heading (câu 1 = answer, Subordinate Text Match); không đại từ hồi chỉ ("điều này", "như đã nói ở trên") | AX1 · Lever Structured Answers |
| GE-04 | 🔴 **Front-load answer (AX2)** | First 100-150 từ = answer-first, không storytelling intro (trừ narrative niches — SERP-intent-conditional); best content trong 30% đầu trang; keyword chính 100 chữ đầu VÀ cuối (P16) | AX2 · P16 |
| GE-05 | 🔴 **Heading-query alignment (AX3)** | Heading match trực tiếp sub-query người dùng hỏi AI (fan-out 8-12 sub-queries); K2Q khi query dạng question; page 500-2.000 từ, 7-20 subheadings; KHÔNG phình thành ultimate guide — cover quá rộng → TÁCH page | AX3 · O7/P7 · Lever Semantic Coverage |
| GE-06 | **General Summary + Key-Facts table** | Intro theo Extractive + Abstractive (đúng Concordance với thứ tự H2); có Key-Facts table cho bài informational chính | W1/P10 · skill `general-summary-introduction` |
| GE-07 | **Citation & evidence (KDD tactics)** | Cite nguồn SAU claim, statistics cụ thể, expert quotation — 3 tactics top của GEO paper KDD 2024 (visibility tới ~40%); mỗi con số truy được nguồn + ngày | W3/P17 · Bước 4 `geo-content-optimization` |
| GE-08 | **AX5 Blur Test + freshness** | Screenshot blur 50% vẫn nhận ra topic + function (AX5 — fail → `sop/07` B7); bài trọng điểm có chu kỳ update NỘI DUNG thật ≤30 ngày (76,4% top cited pages) — 🔴 KHÔNG date-spoofing | AX5 · Bước 5 `geo-content-optimization` |

## Trụ 3 — OFFSITE (T4-T7)

| ID | Item | Tiêu chí ĐẠT | Reuse |
|---|---|---|---|
| GE-09 | **Backlink consensus** | Đợt link T4-T7 có ưu tiên nguồn mà AI engines hay cite trong ngách (xác định qua anchor/source consensus khi research); nhớ "DR does not matter much" ở page-level — không viện DR thay cho chunk quality | skill `backlink-research` → `backlink-plan` |
| GE-10 | **Brand entity nhất quán** | Tên brand, mô tả dịch vụ, thông tin cốt lõi nhất quán trên các nguồn AI hay cite (site chính, profile, review platforms, Wikipedia-type nếu có); brand mention đi kèm đúng ngữ cảnh dịch vụ | Lever Entity Recognition + Authority Signals |

## Trụ 4 — ĐO LƯỜNG (T1 → T6 → T10)

> Route toàn bộ sang skill `geo-tracking-prompt-selection` — checklist chỉ xác nhận ĐÃ LÀM.

| ID | Item | Tiêu chí ĐẠT | Reuse |
|---|---|---|---|
| GE-11 | 🔴 **Prompt set baseline T1** | Chốt prompt set ngay T1: service/agency = funnel-based 28-40 prompts (BOFU 50% / MOFU 35% / TOFU 15%); e-commerce = matrix 80-100 prompts; chạy baseline citation/mention lần đầu | skill `geo-tracking-prompt-selection` |
| GE-12 | **Re-measure T6 → T10** | Đo lại cùng prompt set tại T6 và T10; báo cáo aggregate (AI Share of Voice theo TOPIC, không theo từng query — semantic stability 0,95 dù bề mặt đổi ~2,15 ngày); track AIO và AI Mode 2 kênh riêng (chỉ 13,7% citation overlap) | skill `geo-tracking-prompt-selection` |
| GE-13 | 🔴 **Guardrail communication** | Mọi deliverable/proposal/report GEO tuân thủ 3 guardrail đầu file: không llms.txt, không bán schema như citation lever, không hứa deterministic | GEO.md (chốt) |

---

## Wiki / skill cross-refs

- AX1-AX5 canonical → `sop/08-onpage-checklist.md` mục AX · per-engine emphasis (ChatGPT/AI Mode/AIO/Perplexity) cũng ở đó
- Audit + rewrite chunk bài cụ thể → skill `geo-content-optimization` (retrievability scorecard, fan-out simulation, counter-positioning)
- Đo lường citation share → skill `geo-tracking-prompt-selection`
- Khái niệm nền → [[GEO]], [[Audition Chunk]], [[Core Source]], [[Query Fan-Out]], [[AI Overviews]], [[Retrieval-Augmented Generation]]
