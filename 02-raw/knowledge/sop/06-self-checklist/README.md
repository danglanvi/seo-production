---
type: sop
phase: full-delivery
last_updated: 2026-07-19
source_file: raw/_ingested/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx
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

# GTV Self-Checklist System v3.1 (19.7.2026)

> Hệ self-audit checklist cho nhân sự (Writer / SEO EX / Account / Lead) — khởi nguồn từ bộ **Outline & AM + Content Writing** (v2, 16.4.2026), **mở rộng 19.7.2026 phủ toàn dây chuyền 33 công đoạn**: entity, offpage, CRO, GEO, GBP, cấu trúc, visual, UX, review tháng, runbook sự cố. Nguyên tắc chung không đổi: mỗi checklist có item ID + P0 gate + 3-Level Review — người làm tự lặp đến khi qua gate, **Lead không bao giờ là người review đầu tiên**.

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

## 3. File Structure — Registry toàn hệ (v3, 19.7.2026)

### 3a. Content (bộ gốc v2)

| File | Dùng khi |
|---|---|
| `tier-1-outline-am.md` | Pre-writing — Writer self-check sau khi làm xong Outline & AM |
| `tier-1-content-writing.md` | Post-writing — Writer self-check trước khi submit |
| `tier-2-project-specific.md` | Kickoff — PM/Lead quyết định bật items nào cho dự án |
| `tier-3-audit-configuration.md` | Senior audit / Content Configuration cho niche cạnh tranh cao |
| `tracking-schema.md` | Column map cho Tracking Sheet |

### 3b. Per công đoạn (mở rộng 07/2026 — nhịp per batch/mốc)

| File | Công đoạn · nhịp | P0 |
|---|---|---|
| `foundation-content-nganh.md` | (3) T1 — dựng checklist content ngành per dự án, nguồn bật Tier 2 | 5 |
| `gate-structure-wireframe.md` | (11) — gate TRƯỚC khi gửi khách duyệt cấu trúc, 15 ngày đầu T2 | 100% |
| `tier-1-structure-website.md` | (11) — full check khi THIẾT KẾ cấu trúc (chạy trước gate) | 6 |
| `tier-1-visual-semantic.md` | Layout per page/template — operationalize sop/07 B0-B8 | 5 |
| `tier-1-ux-ui.md` | Duyệt wireframe T2 + CRO landing T8-T10 | 5 |
| `tier-1-entity.md` | (13) — gate cuối T1 & cuối T3 (⚠ tactic rủi ro gắn gate Lead/Director) | 6 |
| `checklist-entity-onsite-web.md` | (13) — deep-dive triển khai entity ONSITE per trang | 7 |
| `tier-1-social-google-stack.md` | Entity offsite — social profiles + Google Stack | 5 |
| `tier-1-offpage-backlink.md` | (20)(25)(26) — per batch link + content offpage + textlink PR | 7 |
| `tier-1-traffic-users.md` | T8-T9 — ⚠ risk cao, CHỈ khi SEO Director duyệt (gate 100% phần P0) | 5 |
| `tier-1-cro-conversion.md` | Site-wide T2-T3 · per landing T8-T10 · conversion path | 3 |
| `tier-1-geo.md` | Lớp GEO T1-T10 (reuse AX1-AX7, guardrail llms.txt/schema ≠ lever) | 5 |
| `tier-1-gbp-local.md` | Dự án local — vận hành GBP hằng tháng | 5 |
| `quality-content-ai.md` | Vận hành content AI 6 phase (pointer về tier-1, không duplicate) | 5 |
| `common-ai-errors.md` | Error catalog 28 lỗi khi QC/edit bài AI | — |

### 3c. Review & Planning (nhịp tháng/quý + tiền dự án)

| File | Nhịp |
|---|---|
| `checklist-project-intake-tham-dinh.md` | Thẩm định TRƯỚC khi nhận dự án — go/no-go gate, Director duyệt (P0: 6 + 6 red-flags từ chối) |
| `checklist-kpi-okrs-planning.md` | LẬP KPI/OKRs — T1 + đầu quý T3/T6/T9 (P0: 5) |
| `monthly-project-review.md` | SEO Lead tự check TRƯỚC khi trình review tháng lên Manager/Director (P0: 7) + phần quý |
| `checklist-phap-ly-content-website.md` | Pháp lý content & website VN — T1 audit + per batch content + khi luật đổi (P0: 7) |

### 3d. Runbook sự kiện

| File | Trigger |
|---|---|
| `tier-3-ranking-drop-runbook.md` | Rớt hạng / Google update — triage 15 phút + 10 nhánh phân ngành (102 items) |
| `checklist-xu-ly-ma-doc.md` | Website bị hack/mã độc — 4 phase (35 items) |
| `checklist-khoi-phuc-seo-ranking.md` | Phục hồi SAU sự cố đã xác định — gate sạch 5/5 rồi mới chạy (24 items) |
| `tier-3-technical-advance.md` | Technical audit chuyên sâu (bộ gốc) |

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

Source: `raw/_ingested/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx` (Vincent Do, CEO GTV SEO Agency). Change log chi tiết trong sheet **'Claude Log'** — 7 turns từ 2026-03-16 đến 2026-03-20 ghi lại các lần điều chỉnh schema.

Key refactor moments:
- Turn 2 (2026-03-17): Align Tracking headers với Description sheets (100%).
- Turn 5 (2026-03-20): Chia vùng header Tracking Content Writing thành nhóm (Semantic 9 / Anti-AI 6 / QA 4 / Depth 1 / Tone 1).
- Turn 6 (2026-03-20): Xây cơ chế 3-level SCORE & REVIEW (14 cột). Nhúng Game Theory Mixed Strategy NE.
- Turn 7 (2026-03-20): Thêm 22 notes hover cho nhân sự trong vùng Score & Review.
- v3.1 (2026-07-19): Thêm 2 checklist treo #6 Batch 36 — `checklist-phap-ly-content-website.md` (PL-01→16, từ docx pháp lý TAG 11/2025) + `checklist-project-intake-tham-dinh.md` (PI-01→14 + red-flags, modernize Thẩm định dự án 10 bước PSP).
