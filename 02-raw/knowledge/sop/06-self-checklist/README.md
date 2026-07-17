---
type: sop
phase: content-creation
last_updated: 2026-04-20
source_file: raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx
tier_system: [tier-1, tier-2, tier-3]
related_wiki:
  - "[[Article Methodology]]"
  - "[[Content Brief]]"
  - "[[Main Content]]"
  - "[[Supplementary Content]]"
  - "[[Contextual Layers]]"
  - "[[Representative Question]]"
  - "[[E-A-V Framework]]"
tags: [sop, self-checklist, outline, content-writing, quality-gate]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/README.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# Semantic Content Self-Checklist v2 (16.4.2026)

> Self-audit checklist cho nhân sự (Writer / SEO EX / Lead) kiểm tra **Outline & AM** và **Content Writing** trước khi onpage. Nguồn gốc: Vincent's internal SOP — `raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx`.

---

## 1. Triết lý: 3-Tier System

| Tier | Scope | Khi nào dùng | Số items |
|---|---|---|---|
| **Tier 1 — Foundation** | Universal, áp dụng mọi bài | Mặc định cho MỌI bài viết | OL+AM: 19 (P0 + O1-O18) · Writing: 21 (W1-W21) |
| **Tier 2 — Project Specific** | Bật khi PM/Lead quyết định tại Kickoff | YMYL, Review, E-commerce, Multi-market, có SCN consistency yêu cầu | OL+AM: 8 · Writing: 7 |
| **Tier 3 — Advanced / Audit & Configuration** | Senior + dự án cạnh tranh cao, hoặc khi content audit / content configuration | Full Semantic Audit (66pt), Information Gain Scoring, Google Helpful Content audit | OL+AM: 3 · Writing: 5 |

**Nguyên tắc:**
- Tier 1 = **luôn tick**. Không optional.
- Tier 2 = PM bật tại Kickoff. Cột được thêm vào Tracking Sheet chỉ khi dự án có yêu cầu.
- Tier 3 = mode audit / configuration — áp dụng khi rework content cũ, audit competitive content, hoặc build content configuration cho niche cạnh tranh cao.

---

## 2. Cơ chế 3-Level Review (Game Theory: Mixed Strategy NE)

| Level | Ai | Scope | Mục đích |
|---|---|---|---|
| ① **Self-Check** | Writer | 100% bài — tick toàn bộ items Tier 1 (+ Tier 2 nếu enable) | Self accountability |
| ② **SEO EX Verify** | SEO Executive (khác Writer càng tốt) | 100% bài — quick verify 5 items kỹ thuật + confirm V-Pass | Rubber-stamp nếu cùng người (80%) — **chỉ có value khi khác người** (20%) |
| ③ **Lead Review** | Lead / Senior | **Random 25–30%** — full re-score, so sánh Self vs Lead | Catch drift, KPI flag (Gap ≥ 3 items/tháng → KPI 50%) |

**Cơ chế game-theoretic:** Writer không biết bài nào sẽ bị Lead review → incentive tick trung thực. Mixed Strategy Nash Equilibrium.

**Công thức Score:**
- Self Score (Outline): SUM tick O1–O18 + P0 → /19. Self % = Score/19.
- Self Score (Writing): SUM tick W1–W21 + Depth + Tone → /23. Self % = Score/23.
- Gap = Self Score − Lead Score (nếu dương lớn = cờ đỏ).

---

## 3. File Structure

| File | Dùng khi |
|---|---|
| `tier-1-outline-am.md` | Pre-writing — Writer self-check sau khi làm xong Outline & AM |
| `tier-1-content-writing.md` | Post-writing — Writer self-check trước khi submit |
| `tier-2-project-specific.md` | Kickoff — PM/Lead quyết định bật items nào cho dự án |
| `tier-3-audit-configuration.md` | Senior audit / Content Configuration cho niche cạnh tranh cao |
| `tracking-schema.md` | Column map cho Tracking Sheet (để setup sheet mới hoặc hiểu sheet cũ) |

---

## 4. Content Quality Gate (P0) — 9 items 🔄 PHẢI pass trước Onpage

P0 là gate giữa Content và Onpage. Nhân sự onpage CHỈ confirm P0 = pass → tick 1 lần, KHÔNG tick lại từng 🔄 item.

- 🔄O (Outline overlap): P2 Search Intent Verify (= O1), P7 Heading Hierarchy (= O3/O4/O5)
- 🔄W (Writing overlap): P10 Intro/General Summary (= W1), P15 L0 Answer-First (= W2), P17 Citation (= W3), P18 Paragraph Structure (= W12), P24 Conclusion & CTA, P27 FAQ Structure, P32 Follow Outline & AM (= W18)
- P9 EAV Density giữ lại ở Onpage CL (verify trên CMS) — không thuộc P0.

---

## 5. Quy trình Self-Check (Writer)

1. **Sau Outline & AM** → mở `tier-1-outline-am.md`, tick từng item O1-O18 + P0 trên Tracking Sheet 4.
2. **Sau Writing** → mở `tier-1-content-writing.md`, tick từng item W1-W21 trên Tracking Sheet 5.
3. Nếu dự án có **Tier 2 enable** → mở file tương ứng, tick thêm items được bật.
4. Note rõ **Self %** và **Self Note** (lý do chưa tick item nào, plan fix).
5. Submit → SEO EX Verify → (random) Lead Review.

---

## 6. Wiki Cross-References (concepts liên quan)

Khi đọc item mà không hiểu thuật ngữ → tra wiki tương ứng:

- **Search Intent, SERP** → [[Central Search Intent]], [[Understanding SERP]]
- **Contextual Vector / Hierarchy / Flow / Structure** → folder `wiki/concepts/core/context/`
- **Representative Question, PQ, K2Q** → folder `wiki/concepts/core/query/`
- **EAV, Attributes, RPP Scoring** → [[E-A-V Framework]], [[Attribute Taxonomies]]
- **Main / Supplement / Article Methodology** → folder `wiki/concepts/core/content-structure/`
- **Topical Authority, SCN, Topical Map** → folder `wiki/concepts/frameworks/`
- **Anti-AI (Nuke Words, Burstiness, Modality)** → (stubs — xem section Anti-AI trong writing)
- **General Summary (Extractive/Abstractive)** → [[Initial Contact Section]], [[sources/general-summary-training-gtv]]

---

## 7. Nguồn gốc & Change History

Source: `raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx` (Vincent Do, CEO GTV SEO Agency). Change log chi tiết trong sheet **'Claude Log'** — 7 turns từ 2026-03-16 đến 2026-03-20 ghi lại các lần điều chỉnh schema.

Key refactor moments:
- Turn 2 (2026-03-17): Align Tracking headers với Description sheets (100%).
- Turn 5 (2026-03-20): Chia vùng header Tracking Content Writing thành nhóm (Semantic 9 / Anti-AI 6 / QA 4 / Depth 1 / Tone 1).
- Turn 6 (2026-03-20): Xây cơ chế 3-level SCORE & REVIEW (14 cột). Nhúng Game Theory Mixed Strategy NE.
- Turn 7 (2026-03-20): Thêm 22 notes hover cho nhân sự trong vùng Score & Review.
