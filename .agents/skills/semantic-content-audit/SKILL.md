---
name: semantic-content-audit
description: "Audit and optimize existing content for semantic SEO compliance. Use when: (1) Reviewing content against the 60 Semantic Writing Rules, (2) Checking E-E-A-T compliance with emphasis on first-hand experience, (3) Auditing content structure and hierarchy."
metadata:
  version: "2.2"
---

# Semantic Content Audit

Audit existing content against semantic SEO standards, the 60 Semantic Writing Rules, E-E-A-T requirements, Google Helpful Content guidelines, **AI-writing pattern detection (Phase 5 — Humanness)** và **gate GEO G-BÀI (Phase 6 — 4 item, chấm riêng)**.

**Phân vai với `geo-content-optimization`:** skill này trả lời "bài có đạt chuẩn semantic/E-E-A-T/human không" + gate G-BÀI 4 item; `geo-content-optimization` chấm Bộ BÀI /12 (mode spot-check) và trả lời "vì sao bài không được AI cite, sửa chunk nào" (mode full). Gate FAIL, cần /12 hoặc rewrite → route sang đó.

## 6-Phase Audit Process

### Phase 1: Structural Audit
- Compare against content brief/outline
- Verify heading hierarchy (H1→H2→H3)
- Check Main/Supplementary proportion (75/25)
- Verify contextual bridge exists
- Check first-last heading connection

### Phase 2: Semantic Audit
- Check macro/micro term distribution
- Verify word proximity (related terms close)
- Audit contextual layers (L0-L6) presence
- Check RQ/PQ implementation
- Verify General Summary in Introduction

### Phase 3: Writing Quality Audit
- Apply the 60 Semantic Writing Rules: đọc `references/45-semantic-writing-rules.md` đã đóng gói trong skill này (tên lịch sử, đủ 60 rules). Bảng 16 điểm dưới là subset để tóm tắt, không thay bộ 60 khi chạy audit đầy đủ. Nếu user chỉ yêu cầu kiểm nhanh subset, ghi rõ phạm vi 16 điểm; không kết luận đã kiểm đủ 60.
- Check answer modality matching
- Verify measurement precision
- Audit citation positioning
- Check 5C's compliance

### Phase 4: E-E-A-T & Helpful Content Audit
- Experience signals present (CRITICAL)
- Expertise demonstrated
- Authority citations
- Trust factors
- Google Helpful Content compliance

### Phase 5: AI-Pattern Detection — Humanness (chấm RIÊNG, không tính vào 66đ)
- Chạy [references/ai-detection-checklist.md](references/ai-detection-checklist.md): quét 4 nhóm (Vocabulary/cliché · Grammar/structure · Statistical/rhythm · Content/experience) với ngưỡng đếm cụ thể.
- Output: **verdict AI-likelihood LOW / MEDIUM / HIGH + điểm N/42 + top offenders** (mã pattern × số lần × quote + vị trí). KHÔNG output "% AI probability" — evidence-based verdict, trung thực hơn mọi detector.
- **DETECT-only**: Phase này không sửa bài. MEDIUM/HIGH → route skill `humanizer` (FIX layer — rewrite, giữ voice, preserve personality markers). Không flag rhetorical question / direct address / contractions là lỗi — đó là dấu hiệu NGƯỜI.
- Lý do chấm riêng (không cộng vào 66đ): giữ backward-compatibility mọi audit cũ, giống AX Extension bên `seo-onpage`.

### Phase 6: Gate GEO G-BÀI — 4 item (chấm RIÊNG, không tính vào 66đ)

Chạy mặc định khi full audit bài đã publish hoặc khi user hỏi "bài này có được AI cite không". Bốn item = gate cứng mỗi bài (fail bất kỳ → G-BÀI FAIL, bài phải sửa trước khi onpage/refresh) — tiêu chí đầy đủ + evidence tại `sop/06-self-checklist/tier-1-content-writing.md` § "G-BÀI" (canonical, không chép lại ở đây).

| GE | Check nhanh (tick ✅/❌) |
|---|---|
| GE-16 | 100-150 từ đầu main content = câu trả lời thẳng, không storytelling intro (ngoại lệ narrative niche); bài informational chính có Key-Facts table |
| GE-17 | Heading = câu hỏi thật của user; bài gánh đúng 1 câu hỏi chính (≥2 → đề xuất tách page); cluster fan-out có heading cover; không chấm độ dài/số heading theo dải cố định |
| GE-18 | Câu đầu sau MỌI heading = câu trả lời đúng pattern (định nghĩa/how-to/so sánh/yes-no), 40-75 từ, đủ E-A-V, không modality |
| GE-19 | Mỗi H2 cắt rời vẫn đủ Entity + context + claim; không "như đã nói ở trên" xuyên section; khối ý <~200 từ; heading tổ tiên có nghĩa |

Output: **G-BÀI: PASS/FAIL (item rớt)**. Bộ BÀI /12 đầy đủ (GE-20…GE-27), scorecard, rewrite per chunk → `geo-content-optimization` (mode spot-check = tick /12; mode full = 6 bước).

## Scoring System (66 Points Total + Humanness verdict riêng + gate G-BÀI riêng)

### Structural Score (12 Points)

| Item | Points | Check |
|------|--------|-------|
| H1 reflects macro context | 2 | H1 matches overall topic |
| Heading hierarchy correct | 2 | H2→H3→H4 logical |
| Main/Supplement ratio ~75/25 | 2 | Not diluted |
| Contextual bridge exists | 2 | Main→Supplement transition |
| First-last connection | 2 | Synonym/antonym relationship |
| No redundant headings | 2 | Each heading adds value |

### Semantic Score (12 Points)

| Item | Points | Check |
|------|--------|-------|
| Macro terms throughout | 2 | Central entity consistent |
| Micro terms contained | 2 | Section-specific terms stay local |
| Word proximity | 2 | Related terms close together |
| L0 answer-first | 2 | Every H2/H3 starts with direct answer (câu đầu sau heading — GE-18; không ép mọi đoạn thân) |
| L1-L3 present | 2 | Concept, mechanism, evidence layers |
| General Summary in intro | 2 | Extractive + Abstractive |

### Writing Quality Score (16 Points)

| Item | Points | Check |
|------|--------|-------|
| Subordinate text match | 2 | First sentence matches heading |
| No delayed answers | 2 | Direct answer first |
| Modality correct | 2 | Present=fact, can/may=research |
| Citations after claims | 2 | Not before |
| Numeric precision | 2 | YMYL has exact figures |
| Dual measurements | 2 | Multiple units where needed |
| Examples after plurals | 2 | Min 3 examples |
| Serial comma correct | 2 | "A, B, và C" format |

### E-E-A-T Score (16 Points)

| Item | Points | Check |
|------|--------|-------|
| **First-hand usage evidence** | 3 | Personal use demonstrated |
| **Original evidence media** | 3 | Photos/videos from actual experience |
| **Specific observations** | 2 | Details beyond specs/official info |
| Technical accuracy | 2 | No factual errors |
| Domain language | 1 | Appropriate terminology |
| Author credentials | 2 | Byline with relevant background |
| Source quality | 1 | Reputable citations |
| No contradictions | 1 | Internal consistency |
| Transparent limitations | 1 | Caveats disclosed |

### Google Helpful Content Score (10 Points)

| Item | Points | Check |
|------|--------|-------|
| Created for audience (not rankings) | 2 | Serves existing audience |
| Reader doesn't need to re-search | 2 | Complete, satisfying |
| Original value added | 2 | Beyond existing content |
| No warning signs present | 2 | See warning signs list |
| Who-How-Why addressed | 2 | Transparent creation |

## Severity Levels

### Critical (Fix Immediately)
- Contradictions within article
- YMYL inaccuracies
- Missing direct answers (L0)
- Missing first-hand experience in reviews/YMYL
- Plagiarized content
- "Best" claims without comparative testing

### High Priority (Fix Soon)
- Missing E-E-A-T signals in YMYL
- Incorrect heading hierarchy
- Opinion language for facts
- Spec recitation without personal observation
- Stock images instead of original evidence
- Missing drawbacks in reviews

### Medium Priority (Improve)
- Missing dual measurements
- Word proximity issues
- Missing L4-L6 layers
- Single affiliate link in reviews

### Low Priority (Enhance)
- Stylistic improvements
- Additional examples
- Better transitions

## Common Issues & Fixes

| # | Issue | Detection | Fix |
|---|-------|-----------|-----|
| 1 | Subordinate text mismatch | First sentence doesn't match heading | Rewrite to directly answer heading |
| 2 | Delayed answer | Answer buried in paragraph | Move answer to first sentence |
| 3 | Citation before claim | "Theo WHO, ..." | "[Claim], theo WHO." |
| 4 | Missing examples | Plural without specifics | Add minimum 3 examples |
| 5 | Wrong modality | "may" for established facts | Use present tense for facts |
| 6 | Missing L0 | Background before answer | Start with direct answer |
| 7 | Macro term inconsistency | Central entity missing in sections | Add entity references |
| 8 | Missing General Summary | No Extractive + Abstractive | Add both to intro |
| 9 | Measurement imprecision | "khoảng 2 lít" | "2.5 lít (85 ounces)" |
| 10 | Internal link in Main | Links before bridge | Move to Supplementary |

---

## Extended Audit Guidelines

For detailed audit criteria, see reference files:

| Topic | Reference File |
|-------|----------------|
| **Extended E-E-A-T Audit** (Experience focus) | [references/extended-eeat-audit.md](references/extended-eeat-audit.md) |
| Google Helpful Content Audit | [references/google-helpful-content-audit.md](references/google-helpful-content-audit.md) |
| Review Content Audit | [references/review-content-audit.md](references/review-content-audit.md) |
| Helpful Content Issues & Fixes | [references/helpful-content-issues.md](references/helpful-content-issues.md) |
| **AI-Pattern Detection (Phase 5 Humanness)** | [references/ai-detection-checklist.md](references/ai-detection-checklist.md) |
| **Gate GEO G-BÀI (Phase 6)** | `sop/06-self-checklist/tier-1-content-writing.md` § G-BÀI (canonical) · Bộ BÀI /12 + rewrite → skill `geo-content-optimization` (spot-check / full) |

**CRITICAL**: Always read `references/extended-eeat-audit.md` when auditing reviews, YMYL content, or any content requiring E-E-A-T compliance. Run Phase 5 whenever the user asks "bài này có AI không" / "check AI content" — or by default on any full audit of drafted content. Run Phase 6 by default on any full audit of **published** content or when the user asks about AI citation.

## Changelog

- 2026-09-12: đóng gói bộ 60 rules canonical cho audit đầy đủ; giữ phân biệt subset 16 điểm và gate nguồn.

- **v2.2 (2026-08-29 — gộp v2.1 → v2.2 cùng ngày, Vincent duyệt):** (1) **Phase 6 = gate GEO G-BÀI 4 item** (GE-16…19; canonical `sop/06-self-checklist/tier-1-content-writing.md` § G-BÀI), chấm riêng không phá 66đ, chạy mặc định với bài đã publish; Bộ BÀI /12, scorecard, rewrite → `geo-content-optimization` 1.3 (mode spot-check / full) — phương án C: core skill giữ hook, lớp GEO ở skill geo-*. (2) Reconcile "L0 answer-first" = câu đầu sau heading (không ép đoạn thân) với `semantic-content-writing` 2.2. (3) GE-17 không chấm độ dài/số heading theo dải cố định (độ dài theo loại node + benchmark đối thủ). (4) Description +(12); phân vai 1 câu với GCO; header 6-Phase. Bản `-ca` 1.3.2-ca giữ module Retrievability 12 việc public. Port CP ×5.
- **v2.0 (2026-07-04):** thêm **Phase 5 — AI-Pattern Detection (Humanness)** theo yêu cầu Vincent: tích hợp taxonomy humanizer v3.1 thành `references/ai-detection-checklist.md` (DETECT-only, 4 nhóm + ngưỡng đếm, verdict LOW/MEDIUM/HIGH + evidence, chấm riêng không phá thang 66đ; fix → route `humanizer`). Cập nhật label "45-point" → 60 Semantic Writing Rules (đúng hiện trạng file rules).
- v1.x: 4-phase audit + 66-point scoring.
