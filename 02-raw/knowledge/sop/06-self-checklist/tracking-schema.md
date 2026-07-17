---
type: sop
phase: tracking-schema
last_updated: 2026-04-20
source_file: raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx
tags: [sop, tracking-schema, scoring, game-theory]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/tracking-schema.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# Tracking Sheet Schema — Column Map

> Reference để setup/hiểu Google Sheet "Tracking Outline & AM" và "Tracking Content Writing". Nếu cần recreate sheet mới, dùng schema này.

---

## Sheet 4 — Tracking Outline & AM (cột A-AS)

### Nhóm 1: THÔNG TIN BÀI VIẾT (A-M)
| Cột | Field |
|---|---|
| A | STT |
| B | Keywords |
| C | Main Entity/Topic |
| D | Volume |
| E | Link Outline & AM |
| F | Deadline dự kiến |
| G | Ngày hoàn thành |
| H | Loại bài |
| I | Dạng bài (Audit/viết mới) |
| J | Content Type |
| K | PIC |
| L | Action |
| M | Trạng thái |

### Nhóm 2: OUTLINE (N-W) — Tick 1=Đạt, 0=Chưa đạt
| Cột | Item | Label |
|---|---|---|
| N | O1 | Search Intent |
| O | O2 | Flow Main Content |
| P | O3 | Flow Open-Close |
| Q | O4 | Contextual Vector |
| R | O5 | Contextual Hierarchy |
| S | O6a | Authority + Source Ctx |
| T | O6b | Attribute Filtration |
| U | O7 | K2Q |
| V | O8 | Coverage & Allocation |
| W | O9 | Representative Question |

### Nhóm 3: ARTICLE METHODOLOGY (X-AD)
| Cột | Item | Label |
|---|---|---|
| X | O10 | Contextual Flow |
| Y | O11 | Contextual Structure |
| Z | O12 | Layers & PQ Depth |
| AA | O13 | Media & Format Justify |
| AB | O14 | EAV Granularity |
| AC | O15 | Contextual Phrase / N-gram |
| AD | O16 | Information Gain |

### Nhóm 4: SUPPLEMENT (AE-AF)
| Cột | Item | Label |
|---|---|---|
| AE | O17 | Bridge to Supplement |
| AF | O18 | Supplement Quality |

### Nhóm 5: SCORE & REVIEW (AF-AS) — 3-level system

#### ① Self-Check (Writer) — AF-AH
| Cột | Field | Formula |
|---|---|---|
| AF | Self Score (/19) | `=SUM(N{r}:AF{r})` (toàn bộ ticks Tier 1 + Tier 2 slot) |
| AG | Self % | `=AF{r}/19` |
| AH | Self Note | Writer note lý do chưa tick / plan fix |

#### ② SEO EX Verify — AI-AL
| Cột | Field | Notes |
|---|---|---|
| AI | SEO EX PIC | Ai verify |
| AJ | Verify Date | |
| AK | V-Pass? | Y/N — gate cho P0 |
| AL | SEO EX Note | |

#### ③ Lead Review (Random 25-30%) — AM-AS
| Cột | Field | Notes |
|---|---|---|
| AM | Lead PIC (Role) | |
| AN | Review Date | |
| AO | Lead Score (/17) | Lead re-score độc lập |
| AP | Lead % | `=AO{r}/17` |
| AQ | Gap (Self−Lead) | `=AF{r}-AO{r}` — Gap dương lớn = cờ đỏ |
| AR | Flag Items | Items Lead fail mà Self pass |
| AS | Lead Note | |

**KPI rule:** Flag ≥3 items sai/tháng → Writer KPI = 50%.

---

## Sheet 5 — Tracking Content Writing (cột A-AU)

### Nhóm 1: THÔNG TIN (A-K)
| Cột | Field |
|---|---|
| A | STT |
| B | Keywords |
| C | Main Entity/Topic |
| D | Volume |
| E | Loại bài |
| F | Link Docs bài viết |
| G | Link outline & AM |
| H | Word Count |
| I | Writer PIC |
| J | Ngày submit |
| K | Trạng thái |

### Nhóm 2: SEMANTIC WRITING (L-T) — 9 items W1-W9

### Nhóm 3: ANTI-AI & HUMAN WRITING (U-Z) — 6 items W10-W15

### Nhóm 4: QUALITY ASSURANCE (AA-AD) — 4 items W16-W19

### Nhóm 5: DEPTH (AE) — W20 Parent Heading = General Summary

### Nhóm 6: TONE (AF) — W21 Tone & Brand Voice

### Nhóm 7: TIER 2 SLOT (AG-AH)

### Nhóm 8: SCORE & REVIEW (AI-AU) — 3-level system
Giống sheet 4, denominator = /23.

---

## Scoring Rules (Game Theory Mechanism)

### Mixed Strategy Nash Equilibrium logic
- Writer KHÔNG biết bài nào sẽ bị Lead review (random 25-30%).
- Incentive: tick trung thực — vì Gap dương lớn = cờ đỏ = KPI penalty.
- SEO EX Verify (tier 2) = mandatory gate (100% bài), nhưng 80% value là rubber stamp nếu cùng người. Value thật đến từ khi Writer ≠ SEO EX.

### Score hierarchy
```
Self Score → SEO EX V-Pass → (Random) Lead Score
    ↓              ↓                    ↓
 /19 or /23     Y/N gate         Compared vs Self
                                       ↓
                                 Gap & Flag Items
                                       ↓
                                  KPI impact
```

### Notes trong ô (Google Sheet hover)
- **Cột AF/Self Score**: "Tổng tick 1 trên toàn item Tier 1. Cảnh báo tick ảo: nếu Self = 19 mà Lead thấy fail → flag nghiêm trọng."
- **Cột AG/Self %**: "Score / denominator. Benchmark: ≥ 90% cho publication-ready."
- **Cột AK/V-Pass?**: "Quick verify 5 items kỹ thuật trước đăng. Y = pass, N = trả về writer."
- **Cột AQ/Gap**: "Self − Lead. Dương lớn (≥3) = cờ đỏ — writer có xu hướng tick ảo."
- **Cột AR/Flag Items**: "Các item Lead fail mà Self pass. ≥3 flag/tháng → KPI 50%."

---

## Skip Rules

- Item Tier 2 KHÔNG bật cho project → để trống (không tick 0, không tick 1). Không tính vào denominator.
- Item Tier 3 = audit-mode only → không nằm trong Self Score /19 hoặc /23 thông thường.
