---
template: geo-baseline
ws: 08-geo-ai-visibility
cong_doan: 14 (GEO G0 Readiness & Baseline + G1 Retrieval hygiene, T1→T3)
skill: geo-tracking-prompt-selection
lich_do: baseline T1 · giữa kỳ T6 (#24) · báo cáo T10 (#32) · quý (duy trì)
checklist: sop/06-self-checklist/tier-1-geo.md v2.0 (GE-01…GE-37)
guideline: sop/09-project-timeline/lop-geo-v2.md (6 điểm chạm)
naming: "{{CLIENT}}_geo-baseline_v{{N}}.md"
version: v2
---

# {{CLIENT}} — GEO Baseline (công đoạn 14 · điểm chạm G0 + G1)

## 0a. 🔴 Gate G-T1 — chạy TRƯỚC khi làm gì khác

Fail bất kỳ dòng nào = **dừng lớp GEO**, báo SEO Lead, ghi lý do vào proposal. Không "làm tạm cho có".

| # | Điều kiện | Cách kiểm | Đạt? |
|---|---|---|---|
| GE-01 | Trang mục tiêu **đã index** + có **page-one presence cho ≥1 sub-query** | GSC + kiểm tay | ☐ |
| GE-02 | **AI crawler vào được** — robots.txt + firewall + CDN không chặn nhóm search & user-triggered | mục 0c | ☐ |
| GE-03 | **Có baseline** — prompt set chốt và chạy xong trong T1 | mục 1-2 | ☐ |

> Chưa rank thì chưa có vé dự thi: retrieval rank là predictor mạnh nhất của citation (position 0 = 58% vs position 10 = 14% — Ahrefs/Indig 04/2026). Site chưa có nền SEO mà chạy GEO là bán sai thứ.

## 0b. GEO Readiness scorecard → verdict

| Đầu vào | Giá trị | Ghi chú |
|---|---|---|
| Vertical + AIO trigger share | | Informational 99,9% · Medical 44,1% · **Shopping 3,2%** · Navigational 0,9% |
| Hiện trạng rank trang mục tiêu | | bao nhiêu % đã page-one |
| Competitor AI citation set | | đối thủ nào đang được cite, ở engine nào |
| YMYL? | | ảnh hưởng ngưỡng E-E-A-T |

**Verdict:** ☐ **Tối thiểu** (G0 baseline + G1 bot access/hygiene + G3 content rules — *không phát sinh chi phí vì trùng semantic content*) ☐ **Chuẩn hoá** (đủ 6 điểm chạm)

Verdict phải **ghi vào proposal/SOW** và nói với khách tại kick-off. Verdict *Tối thiểu* → GE-09, GE-27, GE-30, GE-31, GE-32 để trống hợp lệ khi chấm.

## 0c. G1 — Quyết định AI crawler access (bot-purpose matrix)

Ghi **quyết định chủ đích** của khách, không để mặc định. Chặn training **không ảnh hưởng Google Search**.

| Nhóm | Bot | Khuyến nghị | Khách chốt |
|---|---|---|---|
| Search / discovery | OAI-SearchBot · Claude-SearchBot · PerplexityBot · Googlebot | **Mở** — muốn được cite thì bắt buộc | ☐ mở ☐ chặn |
| User-triggered | ChatGPT-User · Claude-User · Perplexity-User | **Mở** — user đang chủ động hỏi về brand | ☐ mở ☐ chặn |
| Training | GPTBot · ClaudeBot · Google-Extended | Quyết định của khách | ☐ mở ☐ chặn |

Kiểm cả 3 tầng: `robots.txt` · firewall/WAF · CDN rule. 🔴 **Hit của bot KHÔNG phải KPI AI-visibility** — logfile T7 (#27) chỉ để xác nhận access còn đúng.

## 0d. G2 — `site:domain` answerability test (gate G-ENT, chốt ≤T3)

Chạy `site:{{DOMAIN}} [câu hỏi]` cho 5-10 câu khách hay hỏi. Mỗi câu phải có trang trả lời được **bằng text trên site chính chủ** — không giấu trong PDF, không render JS-only, không chỉ nằm trên sàn/đại lý.

| # | Câu hỏi thương mại | URL trả lời | Đạt? | Việc cần làm |
|---|---|---|---|---|
| 1 | (giá / báo giá) | | ☐ | |
| 2 | (tính năng / thông số) | | ☐ | |
| 3 | (so sánh với đối thủ) | | ☐ | |
| 4 | (chính sách bảo hành/đổi trả) | | ☐ | |
| 5 | (ở đâu / chi nhánh) | | ☐ | |

> Vì sao quan trọng: `site:` xuất hiện trong **64% fan-out queries** của ChatGPT (Nectiv 13/08/2026, n≈4K, đo qua API) — engine đã dịch từ *keyword discovery* sang **verification tại entity home**. Entity home không trả lời được thì fan-out quét về tay không.
> ⛔ **Không** nhồi chữ "official" vào trang — đó là triệu chứng đã ở trong shortlist, không phải nguyên nhân vào được shortlist.

## 0. Phân loại website → quy mô prompt set

| Trường | Giá trị |
|---|---|
| Loại site | Service/Agency (funnel-based, 28-40 prompts) / E-commerce (matrix-based, 80-100 prompts) |
| Dịch vụ/ngành hàng lõi (service: 1-3; e-commerce: theo % doanh thu) | |
| Đối thủ benchmark (5-7 brand) | |
| Thị trường / ngôn ngữ prompt | VN / US / song ngữ |
| Engine theo dõi | ChatGPT · Perplexity · Gemini · Claude · Google AIO |

## 1. Prompt set theo funnel

Phân bổ chuẩn (service): BOFU 50% (15-20) → MOFU 35% (10-15) → TOFU 15% (3-5). E-commerce: ma trận Category × Intent × Price Segment + prompt seasonal (Tết, sale lớn, product launch).

| ID | Funnel | Loại (comparison/pricing/trust/feature/educational) | Prompt VN | Prompt EN (nếu có) |
|---|---|---|---|---|
| B-01 | BOFU | comparison | | |
| M-01 | MOFU | feature | | |
| T-01 | TOFU | educational | | |

Công thức prompt: `[Product/Brand] + [Intent Action] + [Modifier]`.

Luật chọn prompt:
1. BOFU ưu tiên nhất: comparison ("[Brand] vs [đối thủ]"), pricing ("giá/báo giá [X]"), trust ("[Brand] có uy tín không").
2. Cấm prompt generic không có conversion value ("SEO là gì").
3. Không vượt trần: >100 (service) / >150 (e-commerce).
4. Mỗi prompt phải track được context type, không chỉ đếm mention.

## 2. Baseline đo T1 (chạy toàn bộ prompt set, ghi từng engine)

| Chỉ số | ChatGPT | Perplexity | Gemini | Claude | AIO | Tổng |
|---|---|---|---|---|---|---|
| Mention rate BOFU (%) | | | | | | |
| Mention rate MOFU (%) | | | | | | |
| Mention rate TOFU (%) | | | | | | |
| Citation count (page nào được cite) | | | | | | |

## 3. Citation share — brand vs đối thủ

`SOV = mention brand / tổng mention (brand + đối thủ) × 100` — tính trên cùng prompt set.

| Brand | Mention | SOV (%) | Vị trí trung bình trong list | Context chính (recommendation/comparison/information/negative) |
|---|---|---|---|---|
| {{CLIENT}} | | | | |
| Đối thủ 1 | | | | |

## 4. KPI GEO cam kết

| KPI | Baseline T1 | Target | Tần suất đo |
|---|---|---|---|
| Brand Mention | | >60% BOFU · >40% MOFU · >20% TOFU | tháng |
| AI Citations | | trend tăng | tháng |
| Share of Voice | | >30% SOV | tháng |
| Information Accuracy | | >90% mô tả đúng | tháng |

Luật KPI: GEO không deterministic như SEO — KHÔNG hứa vị trí cụ thể, KHÔNG cam kết per-prompt; cam kết theo **mention rate / SOV theo topic / trend**. Chuẩn polling: mỗi prompt chạy **≥3 lần** (chuẩn GTV 5 lần/prompt/engine) rồi báo tỷ lệ — variance nội bộ 1 model là 10-34%, một lần chạy không phải dữ liệu. Mọi lần đo **date-stamp engine + model version**.

**Information Accuracy** là KPI dễ thắng nhất và hay bị bỏ quên: AI đang mô tả sai gì về brand (giá cũ, dịch vụ không còn, nhầm với đối thủ) → sửa được bằng G2 entity home, thấy kết quả nhanh hơn mọi lever khác.

## 5. Lịch đo T1/T6/T10

| Mốc | Việc | Output |
|---|---|---|
| T1 (baseline) | Chốt prompt set + chạy đo lần đầu, điền mục 2-3 | File này v1 + checkbox bảng C index |
| T6 (giữa kỳ, cùng #24) | Chạy lại full set; so baseline; thay prompt underperform; cập nhật SOV | `{{CLIENT}}_geo-do-giua-ky_v1.md` + evidence vào FS/AIO đợt 2 (#28) |
| T10 (báo cáo) | Đo cuối kỳ; tổng hợp trend vào báo cáo kép (#32) | Section GEO trong báo cáo T10 |

## 6. Luật vận hành

1. Iteration hàng tháng: prompt 0% mention 2 kỳ liên tiếp → thay, ghi log.
2. Prompt set đổi ≥30% → đo lại baseline mới, không so chéo set cũ-mới.
3. Alert: mention rate rớt >20% tuần / xuất hiện mention negative / thông tin sai nghiêm trọng → báo SEO Lead ngay.
4. Kết quả đo lưu kèm screenshot vào `02-raw/screenshots/serp-ai/` (naming chuẩn, log op `capture`); prompt set là tài sản bàn giao — đưa vào handover-checklist (#33).

## Done-criteria

- [ ] **Gate G-T1 (0a) có verdict** — fail = dừng lớp GEO, đã báo Lead + ghi lý do vào proposal.
- [ ] **Readiness verdict (0b)** Tối thiểu/Chuẩn hoá đã ghi vào proposal/SOW và nói tại kick-off.
- [ ] **Bot access (0c)** là quyết định chủ đích của khách, kiểm đủ 3 tầng robots/firewall/CDN.
- [ ] **`site:` test (0d)** chạy đủ 5-10 câu; câu nào fail có việc cần làm + owner (gate G-ENT chốt ≤T3).
- [ ] 5 guardrail đã nói tại kick-off (llms.txt ≠ lever · schema ≠ citation lever · không deterministic · không cite tên bịa · không nhồi "official").
- [ ] Mục 0-1 đủ: loại site, đối thủ 5-7, prompt set đúng phân bổ funnel, không prompt generic.
- [ ] Baseline mục 2-3 có số thật từng engine + screenshot trong `02-raw/screenshots/serp-ai/`.
- [ ] KPI mục 4 điền baseline + target, không cam kết vị trí cụ thể.
- [ ] Lịch đo T1/T6/T10 khớp bảng C index; index #14 + log cập nhật (op `work`).
