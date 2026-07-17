---
name: semantic-content-audit
description: "Audit and optimize existing content for semantic SEO compliance. Use when: (1) Reviewing content against the 60 Semantic Writing Rules, (2) Checking E-E-A-T compliance with emphasis on first-hand experience, (3) Auditing content structure and hierarchy, (4) Verifying Contextual Layers implementation, (5) Checking Introduction General Summary quality, (6) Auditing measurement precision and citation patterns, (7) Verifying internal link placement, (8) Identifying content gaps and improvements, (9) Checking consistency across Semantic Content Network, (10) Auditing review content against Google guidelines, (11) Detecting AI-writing patterns — 'bài này có AI không', 'check AI content', Humanness verdict with evidence (Phase 5, routes fixes to humanizer skill)."
metadata:
  version: "2.0"
---

# Semantic Content Audit

Audit existing content against semantic SEO standards, the 60 Semantic Writing Rules, E-E-A-T requirements, Google Helpful Content guidelines, **and AI-writing pattern detection (Phase 5 — Humanness)**.

## 5-Phase Audit Process

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
- Apply the 60 Semantic Writing Rules (full list: skill `semantic-content-writing` → `references/45-semantic-writing-rules.md` — tên file lịch sử, chứa đủ 60 rules; bảng 16 điểm dưới là subset chấm được standalone)
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

## Scoring System (66 Points Total + Humanness verdict riêng)

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
| L0 answer-first | 2 | Every H2 starts with direct answer |
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

**CRITICAL**: Always read `references/extended-eeat-audit.md` when auditing reviews, YMYL content, or any content requiring E-E-A-T compliance. Run Phase 5 whenever the user asks "bài này có AI không" / "check AI content" — or by default on any full audit of drafted content.

## Changelog

- **v2.0 (2026-07-04):** thêm **Phase 5 — AI-Pattern Detection (Humanness)** theo yêu cầu Vincent: tích hợp taxonomy humanizer v3.1 thành `references/ai-detection-checklist.md` (DETECT-only, 4 nhóm + ngưỡng đếm, verdict LOW/MEDIUM/HIGH + evidence, chấm riêng không phá thang 66đ; fix → route `humanizer`). Cập nhật label "45-point" → 60 Semantic Writing Rules (đúng hiện trạng file rules).
- v1.x: 4-phase audit + 66-point scoring.
