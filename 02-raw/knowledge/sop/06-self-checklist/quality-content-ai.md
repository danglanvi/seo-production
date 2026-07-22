---
type: sop
phase: ai-content-workflow
last_updated: 2026-07-19
source_file: raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/AI Content checklist Topical Authority/3. Checklist đảm bảo chất lượng nội dung Content AI - Quality Content AI SEO Checklist.xlsx (Sheet 1)
supporting_sources:
  - raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/AI Content checklist Topical Authority/1. Tài liệu training, giải thích workflow tạo dựng Content AI chất lượng_.docx
  - raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/AI Content checklist Topical Authority/2. Content Quality AI Workflow - Topical Authority - Update 4.9.2025.docx
  - raw/_ingested/Quy trình SEO PSP - All In One/AI Agents/Tài liệu Project Knowledge - Topical authority - Audit content/Optimized Semantic SEO Content Checklist.docx
items_count: 28
related_wiki:
  - "[[Information Density]]"
  - "[[Cost of Retrieval]]"
  - "[[Information Gain Score]]"
  - "[[Website Functions]]"
  - "[[Nuke Words]]"
  - "[[Audition Chunk]]"
tags: [sop, self-checklist, ai-content, quality-gate, workflow]
---

# Quality Content AI — Self-Checklist theo 6 Phase Workflow

> **Ai dùng / khi nào:** Người vận hành content AI (Writer/SEO EX chạy pipeline AI) tự check theo từng phase của workflow Content AI, từ research đến monitoring.
> **Quan hệ với tier-1:** Checklist này KHÔNG thay thế `tier-1-outline-am.md` (O1-O18) và `tier-1-content-writing.md` (W1-W21). Item nào tier-1 đã cover → chỉ có 1 dòng pointer `→ O-xx / W-xx`, tick ở tracking sheet tier-1. File này giữ những items **đặc thù AI-workflow** mà tier-1 không có.
> **Nguồn gốc:** Sheet 1 của xlsx "Quality Content AI SEO Checklist" (6 phase, 18 hạng mục) — nâng cấp theo wiki + skill routing 07/2026. Delta chi tiết ở cuối file.

---

## P0 Gate — 5 điều kiện KHÔNG publish nếu fail

| # | Điều kiện | Item |
|---|---|---|
| 1 | Tier-1 Content Quality Gate (V-Pass + 9 items 🔄) đã pass | → P0 trong `tier-1-outline-am.md` |
| 2 | Hallucination check xong — mọi claim/số liệu/citation từ AI đã verify nguồn thật | QA-10 |
| 3 | Nuke Words Tier 1 = 0 sau scan cuối | QA-11 (→ W10) |
| 4 | Humanize pass đã chạy (Humanness Score ≥ 70 hoặc user duyệt exception) | QA-14 |
| 5 | Nếu bài có interactive function: mọi function hoạt động đúng trên mobile + desktop | QA-20 |

---

## Phase 1 — Nền tảng nghiên cứu (Research Foundation)

**WHY (wiki):** Coverage bắt đầu từ [[Query Network]] chứ không từ 1 keyword; nội dung chỉ đáng tồn tại khi có [[Information Gain Score]] so với SERP hiện tại. Intent sai từ đầu → mọi phase sau vô nghĩa ([[Central Search Intent]]).

| ID | Item | Check cụ thể | Route / Pointer |
|---|---|---|---|
| QA-01 | Search Intent + SERP analysis | *Đã cover đầy đủ (taxonomy 9 intent canonical từ 19/07/2026 — xem [[User Intent]]; 7 classical = lớp tương thích — 3Cs, Dominant/Fractured/Hybrid, SERP features)* | → **O1** |
| QA-02 | Query export + Attribute Filtration (RPP) | *Đã cover (export Ahrefs top 1 + authority + đối thủ, lọc RPP)* | → **O6b** |
| QA-03 | Three-grams & action predicates | Lập bản đồ biến thể keyword (số ít/số nhiều, long-tail); liệt kê action predicates (mua, so sánh, kiểm tra, đánh giá); check độ phủ cụm 3 từ chưa có trong outline | Bổ sung vào bước research của O6b; kết quả đổ vào AM mục Phrase |
| QA-04 | AI-surface opportunity | Xác định query nào có [[AI Overviews]] / AI Mode; đánh dấu section cần pass [[Audition Chunk]] (~128 tokens đầu tự đứng được); ghi vào AM Lưu ý | Skill `geo-content-optimization` (audit sau publish) |
| QA-05 | Unique Data Collection | Có ≥1 nguồn dữ liệu độc quyền (khảo sát, case nội bộ, thử nghiệm, data ngành) đã verify chéo; ghi rõ information gap trên SERP mà data này lấp | [[Unique Information Score]] + [[Information Gain Score]]; feed vào O16 |
| QA-06 | Function mapping theo intent | Với mỗi intent chính/phụ: user cần CHỨC NĂNG gì (calculator, filter, form, so sánh)? Map user journey → điểm chuyển đổi. Trang chỉ-text cho query cần function = thua từ thiết kế | [[Website Functions]]; thực thi ở Phase 4 |

---

## Phase 2 — Kiểm soát AI Generation (AI Generation Control)

**WHY (wiki):** Detection 2026 hoạt động ở mức ngữ nghĩa và diệt theo cụm ([[sources/synthetic-slop-detection-lora-paper]] — Google S-CTS, Generation Clusters). Kiểm soát tại NGUỒN (prompt + verify) rẻ hơn nhiều so với sửa ở editing. [[Nuke Words]] + [[Burstiness]] là lớp bề mặt; information gain thật mới là lớp bền.

| ID | Item | Check cụ thể | Route / Pointer |
|---|---|---|---|
| QA-07 | Prompt 3 lớp | Prompt có đủ 3 lớp Facts / Experience / Perspectives; unique data (QA-05) được đưa VÀO prompt chứ không để AI tự bịa; chỉ định modality + format output per section theo AM | Khung 3 lớp: docx training Phần 2 |
| QA-08 | Prompt hygiene | Prompt có anti-pattern instructions (cấm nuke words, cấm mở "Trong thời đại...", yêu cầu đa dạng từ vựng); KHÔNG paste PII/secret client vào model; prompt lấy từ library có version, không viết tay mỗi lần | Nuke list: skill `humanizer` references |
| QA-09 | Model output verification | Đọc 100% output (không skim); đối chiếu từng heading với Outline + AM ngay khi nhận output (đừng đợi đến final check W18); flag section AI tự thêm/bỏ/lệch format | Final gate → **W18** |
| QA-10 | Hallucination check 🔴 P0 | MỌI claim, số liệu, tên nghiên cứu, citation do AI sinh → trace về nguồn thật. Không tìm được nguồn → xóa hoặc thay bằng số có nguồn. KHÔNG giữ "số đẹp" không nguồn (tiền lệ LINT-2026-002) | Pipeline: skill `claim-verifier` (Phase 4); citation format → **W3** |
| QA-11 | AI Pattern Detection scan 🔴 P0 | Scan output thô: nuke words, cấu trúc câu dễ đoán, vocabulary valley (từ lặp đơn điệu), tone bất nhất. Lập danh sách vị trí cần sửa TRƯỚC khi vào Phase 3 | Pattern catalog: skill `humanizer`; tick chính thức → **W10, W13** |
| QA-12 | Output variation có ý nghĩa | Section quan trọng (centerpiece, L0 các heading HIGH): sinh 2-3 biến thể (đa model nếu được), chọn/mix bản tốt nhất. ⚠️ Variation phải ở cấp THÔNG TIN + GÓC NHÌN — đổi từ đồng nghĩa/xáo câu không thoát semantic detection | [[sources/synthetic-slop-detection-lora-paper]] |

---

## Phase 3 — Tối ưu hóa bởi con người (Human Optimization)

**WHY (wiki):** [[Algorithmic Authorship]] — giá trị người thêm vào phải là thứ AI không tái tạo được: trải nghiệm thật, quan sát ngoài specs, [[Collocation]] tự nhiên của người trong ngành. Sửa bề mặt mà không thêm gì = vẫn nằm trong Generation Cluster.

| ID | Item | Check cụ thể | Route / Pointer |
|---|---|---|---|
| QA-13 | Anti-AI editing pass | *Đã cover: nuke filter, câu đầy đủ, sentence connection, burstiness, personality* | → **W10, W11, W12, W13, W14** |
| QA-14 | Humanize pass chuẩn pipeline 🔴 P0 | Chạy skill `humanizer` (governance: ưu tiên Antigravity/Codex; trong Claude → Sonnet, thinking tắt). Pipeline mode = surgical (pre-edit report → duyệt → sửa, không tự thêm ý). Chạy đủ 2-prompt final audit + chấm Humanness Score, ngưỡng ≥ 70 | Skill `humanizer` v3.1 |
| QA-15 | Experience integration | *Đã cover: 8 patterns first-hand experience; YMYL/service ≥2.000 từ cần ≥3 instances patterns (6)(7)(8)* | → **W15** |
| QA-16 | Multi-perspective + Safe Answers | Bài có góc nhìn người dùng + chuyên gia + ý kiến trái chiều (khi topic có tranh luận); topic nhạy cảm/YMYL dùng safe answer — trả lời trực tiếp nhưng thận trọng, kèm nguồn, không tuyệt đối hóa claim đang tranh cãi | [[Truth Ranges]]; intro safe answer → **W1** |

---

## Phase 4 — Kiến trúc tương tác (Interactive Architecture)

**WHY (wiki):** [[Website Functions]] — function site được thuật toán "khoan dung" hơn pure-content site khi dùng AI; function hữu ích là lớp bảo vệ + lý do user chọn trang mình thay vì AI answer. [[Centerpiece Annotation]] + [[Semantic HTML]] là nền cho cả 3 hệ ranking (document / passage / generated passage).

| ID | Item | Check cụ thể | Route / Pointer |
|---|---|---|---|
| QA-17 | Function integration đúng intent | Interactive element khớp function map QA-06 (calculator, bảng so sánh có filter, quiz, form); progressive disclosure cho nội dung dài; conversion path tự nhiên, không chặn main content | Skill `visual-semantic-seo` + `sop/07-visual-semantic`; media per heading → **O13, W8** |
| QA-18 | Semantic HTML + Centerpiece | Semantic HTML5 đúng tag; main content flow liền mạch — share button/inject không cắt đoạn mở; DOM order = visual order; HTML ≤ 2MB | Skill `semantic-html-optimization`; [[Semantic HTML]], [[Centerpiece Annotation]], [[Cost of Retrieval]] |
| QA-19 | Schema markup | JSON-LD đúng page type, @id graph nối Entity Home + Author. 🔴 Guardrail: schema ≠ lever AI-citation ([[sources/schema-ai-citations-did-ahrefs]]) — làm đúng chuẩn, không kỳ vọng ăn citation nhờ schema | Skill `schema-markup-generator` |
| QA-20 | Interactive element quality 🔴 P0 | Mọi function hoạt động đúng; mobile responsive; không kéo tụt tốc độ tải; đạt accessibility cơ bản (WCAG). Function lỗi tệ hơn không có function | Test đa thiết bị trước publish |

---

## Phase 5 — Kiến trúc nội dung (Content Architecture)

**WHY (wiki):** [[Contextual Structure]] + [[Contextual Flow]] quyết định Google đọc bài như MỘT context khép kín hay tập đoạn rời. Ba lớp Facts/Experience/Perspectives là khung Koray cho coverage toàn diện mà không pha loãng ([[Contextual Coverage]]).

| ID | Item | Check cụ thể | Route / Pointer |
|---|---|---|---|
| QA-21 | Three-layer structure | Bài đủ 3 lớp: Facts (có cấu trúc, dẫn nguồn) / Experience (chân thực, kể chuyện) / Perspectives (cân bằng, đa chiều); mỗi lớp đúng văn phong của lớp đó; chuyển lớp mượt, không gãy context | Khung: docx training Phần 2; văn phong per lớp → **W9** |
| QA-22 | Content flow + CTA | *Flow giữa heading/section đã cover.* Riêng CTA: đặt tại điểm ngắt tự nhiên (cuối section lớn, sau proof), không aggressive trong Main Content | → **O10, W12**; Conclusion & CTA = P24 trong P0 tier-1 |
| QA-23 | Comprehensive coverage | *Đã cover: allocation depth, information gain, K2Q/PQ, FAQ theo PAA* | → **O7, O8, O12, O16**; FAQ = P27 trong P0 tier-1 |
| QA-24 | AM v2.0 compliance (khi AI sinh outline/AM) | AM đúng block 6 mục (Format / Subordinate Text / Ý chính / Media / Phrase / Lưu ý); Ý chính = flow đánh số chỉ dẫn writer — KHÔNG planner language, KHÔNG content viết sẵn; render paragraph + list, KHÔNG markdown table; word ladder (H3 ~120-150, H2 ~200, YMYL +20-30%) | Skill `semantic-outline-methodology`; lỗi thường gặp → `common-ai-errors.md` AE-22, AE-23 |

---

## Phase 6 — Hiệu suất kỹ thuật (Technical Performance)

**WHY (wiki):** [[Cost of Retrieval]] — Google ưu tiên nguồn rẻ để crawl/hiểu/serve; [[Core Web Vitals]] và HTML sạch giảm chi phí đó. Monitoring khép vòng: content AI không có vòng đo = không biết bị decay hay bị cluster-suppress.

| ID | Item | Check cụ thể | Route / Pointer |
|---|---|---|---|
| QA-25 | Page performance | Tải < 3s; CWV pass (LCP/INP/CLS); ảnh WebP + lazy load; JS/CSS tối giản | Skill `technical-seo-audit`; [[Core Web Vitals]] |
| QA-26 | Onpage SEO cơ bản | *Title, meta, heading hierarchy, URL — đã có checklist riêng, không lặp ở đây* | → `sop/08-onpage-checklist.md` (OP1-OP55) / skill `seo-onpage` |
| QA-27 | Internal linking | Link nội bộ chiến lược từ/đến bài; anchor phản ánh title trang đích; bài mới không orphan; flow về Core section | Skill `internal-linking`; [[Internal Linking Rules and Strategy]] |
| QA-28 | Monitoring setup | GA4 + GSC tracking hoạt động; conversion goal cho function (QA-17); định metric thành công per bài; đưa bài vào vòng decay-watch (cửa sổ 28 ngày) | Skill `content-refresh` |

---

## Delta vs bản xlsx (2026-01)

**Thêm (chưa có trong xlsx):**
- **Item ID (QA-01…QA-28) + P0 gate 5 điều kiện** — xlsx gốc là bảng mô tả, không có ID, không có gate cứng trước publish.
- **QA-10 Hallucination check + QA-09 Model output verification** — xlsx kiểm soát văn phong AI nhưng KHÔNG có bước verify sự thật của output AI; đây là gap lớn nhất, giờ là P0, route `claim-verifier`.
- **QA-04 AI-surface opportunity** nâng từ 1 dòng "tiềm năng AI Overview" thành check Audition Chunk + route `geo-content-optimization`.
- **QA-24 AM v2.0 compliance** — xlsx ra đời trước convention AM v2.0 (block 6 mục, không planner language, không table render).
- **Routing sang skill hiện hành** (`humanizer`, `claim-verifier`, `semantic-html-optimization`, `schema-markup-generator`, `visual-semantic-seo`, `technical-seo-audit`, `internal-linking`, `content-refresh`, `geo-content-optimization`) + wikilink WHY per phase — biến checklist tĩnh thành checklist có đường thực thi.
- **Guardrail schema ≠ AI-citation lever** (QA-19) theo DiD Ahrefs — xlsx chỉ ghi "thêm schema markup".

**Gộp (tránh duplicate với tier-1):**
- 18 hạng mục xlsx → 8 items thành pointer: Search Intent Mapping → O1; Query Architecture (phần export/RPP) → O6b; Anti-AI Editing → W10-W14; Experience Integration → W15; Content Flow → O10/W12; Comprehensive Coverage → O7/O8/O12/O16; Onpage Technical → sop/08; media → O13/W8. Lý do: tier-1 là source-of-truth tick chính thức, file này chỉ giữ phần AI-workflow không trùng.

**Sửa/loại (vì sao):**
- Loại "**Thêm vào những điểm không nhất quán một cách tự nhiên**" (Anti-AI Editing gốc) — hướng dẫn này lỗi thời và nguy hiểm sau S-CTS 06/2026: hack bề mặt không thoát semantic detection, còn làm giảm chất lượng thật. Thay bằng QA-12 (variation cấp thông tin) + QA-14 (humanize surgical) + QA-15 (experience thật).
- "Tạo 3-5 biến thể mỗi phần, trộn phần tốt nhất" hạ xuống "2-3 biến thể cho section quan trọng" + cảnh báo semantic clustering — nguyên bản khuyến khích volume variation dễ tự tạo Generation Cluster nội bộ.
- Monitoring nâng từ "cài GA4/dashboard" thành khép vòng với decay-detection (`content-refresh`, cửa sổ 28 ngày).
