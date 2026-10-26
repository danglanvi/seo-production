---
type: sop
tier: 1
phase: geo-ai-visibility
version: "2.0.2"
last_updated: 2026-08-29
data_version: "v2026.08 — số liệu tính đến 23/08/2026 (Batch 40); refresh_due 2026-10"
source_file: "sop/08-onpage-checklist.md (AX1-AX7) + skills/geo-content-optimization + skills/geo-tracking-prompt-selection + GEO.md (5 Core Levers) + wiki AI-systems cluster (Batch 39-40)"
items_count: 37
related:
  - "[[GEO]]"
  - "[[AI Visibility Measurement]]"
  - "[[Audition Chunk]]"
  - "[[Query Fan-Out]]"
  - "[[Core Source]]"
  - "[[AI Overviews]]"
  - "[[AI Mode]]"
  - "[[ChatGPT Pipeline]]"
  - "[[Entity Home]]"
  - "[[Non-Commodity Content]]"
  - "[[Subordinate Text Match]]"
  - "[[Structured Data]]"
  - "[[Vertex AI Search]]"
tags: [sop, tier-1, geo, ai-visibility, ai-overviews, self-checklist, master]
---

> Bản đóng gói cho SEO Production — sync NGUYÊN BẢN từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/tier-1-geo.md` v2.0.1 ngày 2026-08-29 (bản trước là v1.0/13 items, 2026-07-17 — đã hết hạn). Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án); HTML tick + Google Sheet derive từ master ở kho gốc.

# Tier 1 — Self-Checklist: GEO / AI-Visibility (GE-01…GE-37) — v2.0

> **Khi dùng:** Lớp GEO chạy song song quy trình 10 tháng (`sop/09-project-timeline/`) theo **6 điểm chạm** = 6 trụ dưới đây. Không có "dự án GEO riêng" — cùng một semantic content phục vụ cả ranking Google lẫn AI citation.
> **Số items:** 37, chia **4 nhịp chấm riêng** (xem Scoring) — KHÔNG chấm chung /37 vì các trụ có nhịp khác nhau.
> **Nguyên tắc REUSE:** không chế khái niệm mới — item map thẳng về **AX1-AX7** (`sop/08-onpage-checklist.md` + `skills/seo-onpage/references/p-series-checklist.md`, canonical) và **5 Core Levers** ([[GEO]]). AX chấm riêng, không tính vào /39 của P-series.
> **Ranh giới:** ngưỡng technical → `tier-3-technical-advance.md` · layout/visual → `tier-1-visual-semantic.md` · entity onsite chi tiết → `checklist-entity-onsite-web.md` · offpage vận hành → `tier-1-offpage-backlink.md`. Checklist này chỉ giữ **lăng kính GEO** của các mục đó.
> **⚠ Hạn số liệu:** mọi con số ở đây gắn nhãn nguồn + tháng trong [[syntheses/geo-evidence-register-2026-08]]. Refresh theo lint quý (hạn 10/2026). Số fan-out/citation là **moving target** — luôn date-stamp + ghi model version khi đưa vào deliverable khách.

---

## 📄 Master file — luật phân lớp

File này là **nguồn sự thật duy nhất** cho cả 3 lớp phát hành. Cột **Lớp** trong mỗi bảng quy định item xuất hiện ở đâu:

| Tag | Xuất hiện ở | Đối tượng |
|---|---|---|
| `L1` | Quà sự kiện (public) + L2 + L3 | Khách dự sự kiện GTV — WHAT + what NOT |
| `L2` | Học viên TAG + L3 | Học viên khoá AI & Automation SEO & GEO — HOW tự làm, tự chấm |
| `L3` | Chỉ nội bộ GTV | Team GTV — HOW ở quy mô, có QC + cam kết |

Bản dưới lớp được **derive bằng filter**, không viết tay lại. Luật derive đầy đủ: `sop/09-timeline/lop-geo-v2.md`.

**Cột Ev (evidence tier):** **A** = official documentation / causal test · **B** = multi-source correlational hoặc ≥2 phương pháp độc lập hội tụ · **C** = vendor COI / single-source / n nhỏ · **D** = GTV practice / internal benchmark.

---

## 🎯 Top-10 theo impact (thứ tự làm khi nguồn lực có hạn)

| # | Việc | Trụ | Ev | Công |
|---|---|---|---|---|
| 1 | Trang phải index + rank page-one ≥1 sub-query — chưa rank thì chưa có "vé dự thi" | A · GE-01 | A/B | Cao |
| 2 | AI crawler vào được (robots/CDN/firewall) — quyết định chủ đích, không để mặc định | A · GE-02 | A | Thấp |
| 3 | Baseline prompt set T1 — không có baseline thì không chứng minh được gì về sau | A · GE-03 | D | Vừa |
| 4 | `site:domain` trả lời được: pricing/features/specs canonical nằm trên site chính chủ | C · GE-11 | B | Vừa |
| 5 | 100 từ đầu = câu trả lời (không storytelling intro) | D · GE-16 | B | Thấp |
| 6 | Heading = câu hỏi thật của user; map theo **cluster**, không đuổi từng fan-out | D · GE-17 | B | Vừa |
| 7 | Câu đầu sau heading = câu trả lời (Subordinate Text) | D · GE-18 | B | Thấp |
| 8 | Mỗi H2 cắt rời vẫn tự đứng (chunk self-contained) + heading hierarchy mạch lạc | D · GE-19 | A/B | Vừa |
| 9 | Fact kiểm chứng được + cite nguồn sau claim + số liệu + quote | D · GE-21 | B | Vừa |
| 10 | Nội dung chỉ mình có (non-commodity / information gain) | D · GE-22 | A | Cao |

> **Không nằm trong top-10 vì evidence không ủng hộ:** schema, llms.txt, số lượng bài, DR/backlink page-level. Xem Phụ lục NOT-a-lever.

---

## 🔴 P0 Gate — 10 items, chia 3 gate theo mốc

Checklist này phủ 4 nhịp khác nhau nên P0 chia theo **mốc**, không gộp một bảng.

| Gate | Mốc | Items | Điều kiện |
|---|---|---|---|
| **G-T1** Mở dự án | T1 (công đoạn 14) | GE-01 · GE-02 · GE-03 | Chưa rank → GEO chưa có vé dự thi, quay về pipeline SEO thường · bot bị chặn → mọi việc sau vô nghĩa · không baseline → T6/T10 không có gì để so |
| **G-ENT** Nền entity | ≤ T3 (công đoạn 13) | GE-11 | `site:domain` không trả lời được câu hỏi thương mại cơ bản → fan-out `site:` quét về tay không |
| **G-BÀI** Mỗi bài publish/refresh | T2 → T9 | GE-16 · GE-17 · GE-18 · GE-19 | 4 item kiến trúc passage — fail bất kỳ = trả về content, không tick |
| **G-KH** Giao tiếp khách | mọi deliverable | GE-05 · GE-35 | Guardrail + evidence bar — fail = không gửi |

---

## 🔴 GUARDRAIL bắt buộc (nói với khách — GE-05 · GE-35)

1. **llms.txt ≠ citation lever.** Google không dùng (Mueller: như keywords meta tag); audit log 2025: GPTBot/ClaudeBot/PerplexityBot **không request** file này; Ahrefs 100.000 domains: không có lợi thế citation đo được. Điều khiển AI crawler = `robots.txt`. **KHÔNG đưa llms.txt vào deliverable.**
2. **Schema ≠ AI-citation lever.** Causal test DiD Ahrefs 1.885 pages: thêm schema KHÔNG tăng AI citation (AI Mode +2,4% · ChatGPT +2,2% ≈ 0). Schema vẫn đáng làm cho rich results / entity / rendering — **việc khác**, không cam kết citation.
3. **Không cam kết deterministic.** AI output probabilistic; AIO đổi bề mặt ~2,15 ngày (45,5% citation mới mỗi lần regenerate) nhưng semantic stability 0,95 → chỉ cam kết **aggregate SoV theo topic** + mục tiêu [[Core Source]], không cam kết "prompt X sẽ ra brand".
4. **Không cite tên bịa.** "Gecko Score" và "Jetstream" **không tồn tại** trong tài liệu Google (tên thật: `semantic_similarity_score`, `relevance_score`). "500-token chunk" là default cấu hình của [[Vertex AI Search]] — sản phẩm cloud khách tự chỉnh — **không phải yêu cầu của Google Search** (Google nói ngược lại: *"no requirement to break your content into tiny pieces"*). Xem [[sources/vertex-ai-search-discovery-engine-metehan]].
5. **Không nhồi từ khoá "official".** `site:`/`official` trong fan-out là **triệu chứng brand ĐÃ nằm trong shortlist**, không phải nguyên nhân vào được shortlist (`author_recommendation_unsupported`, xem GE-11).

---

## Trụ A — GATE & READINESS (T1 · công đoạn 14 · PIC: SEO Lead Project)

> Nhịp: **1 lần đầu dự án**, review lại mỗi quý. Scoring: **/5**.

| ID | Item | Tiêu chí ĐẠT | Ev | Lớp | Route |
|---|---|---|---|---|---|
| GE-01 | 🔴 **Retrieval eligibility** | Trang mục tiêu **đã index** + có **page-one presence cho ≥1 sub-query**. Retrieval rank là predictor mạnh nhất: position 0 = **58%** citation vs position 10 = **14%** (Ahrefs/Indig 04/2026). Ngoại lệ đã biết (28,3% trang được cite có 0 organic keyword) là ngoại lệ — không dùng làm cớ bỏ qua nền SEO | B | L1 | `geo-content-optimization` Bước 0 · AX4 |
| GE-02 | 🔴 **AI crawler access — quyết định chủ đích** | Kiểm robots.txt + firewall + CDN theo **bot-purpose matrix**: search/discovery (OAI-SearchBot · Claude-SearchBot · PerplexityBot · Googlebot) · training (GPTBot · ClaudeBot · Google-Extended) · user-triggered (ChatGPT-User · Claude-User · Perplexity-User). Muốn được cite → mở nhóm search + user-triggered. Chặn training là lựa chọn riêng, **không ảnh hưởng Google Search**. 🔴 Hit của training bot **KHÔNG phải KPI AI-visibility** | A | L1 | `technical-seo-audit` 1.17 |
| GE-03 | 🔴 **Prompt set baseline T1** | Chốt prompt set ngay T1 và chạy baseline: service/agency = funnel 28-40 prompts (BOFU 50% / MOFU 35% / TOFU 15%); e-commerce = matrix 80-100. Ghi cả **Information Accuracy** (AI nói về brand có đúng không) + **branded-prompt defense**. Baseline phải date-stamp engine + model version | D | L2 | skill `geo-tracking-prompt-selection` |
| GE-04 | 🟠 **GEO Readiness scorecard** | Chấm mức đầu tư GEO theo dữ liệu, không theo cảm tính: AIO trigger share của vertical (Informational 99,9% AIO keywords · Medical 44,1% · **Shopping chỉ 3,2%** · Navigational 0,9%) + competitor AI citation set + hiện trạng rank. Verdict: **Tối thiểu** (baseline + bot access + content rules — không phát sinh chi phí vì trùng semantic content) hoặc **Chuẩn hoá** (đủ 6 điểm chạm) | B | L2 | [[AI Overviews]] · `geo-tracking-prompt-selection` |
| GE-05 | 🔴 **Guardrail communication tại kickoff** | 5 guardrail đầu file được nói rõ trong kickoff + ghi vào proposal/SOW. Không bán llms.txt, không bán schema như citation lever, không hứa deterministic, không cite tên bịa, không nhồi "official" | A | L1 | [[GEO]] · `gtv-client-report` v1.2 🔒 |

## Trụ B — RETRIEVAL HYGIENE (T1→T3, verify T7 · công đoạn 14 + 27 · PIC: SEO + Coder)

> Nhịp: **hoàn thiện trong 3 tháng đầu**, verify lại ở logfile T7. Scoring: gộp chung Bộ T1 (xem Scoring).

| ID | Item | Tiêu chí ĐẠT | Ev | Lớp | Route |
|---|---|---|---|---|---|
| GE-06 | 🟠 **Speed / TTFB nền** | Mục speed của `tier-3-technical-advance.md` pass (response time <200ms tốt · <350ms tối thiểu — ngưỡng GTV). Ghi chú GEO: TTFB target <700ms và "hard timeout 2s của ChatGPT fetcher" = **reverse-engineered estimate đơn nguồn**, note-only, KHÔNG dùng làm cam kết | C/D | L2 | `tier-3-technical-advance` §0, §2.1 |
| GE-07 | 🟠 **Index & canonical hygiene (AX4)** | Canonical tự trỏ · không noindex ngoài ý muốn · đã index · featured image indexed. Đây là điều kiện vào retrieval pool | D | L2 | AX4 · `/seo-onpage` |
| GE-08 | 🟠 **Trang đọc được bằng máy** | HTML ≤ **2MB** · DOM order = visual order · nội dung quan trọng **in-flow** (không nằm sau click trong tab/accordion, không JS-only) · extraction hygiene: ~400 ký tự đầu sau H1 là một flow liền mạch, share button/newsletter không chen giữa | B | L1 | `semantic-html-optimization` · `tier-1-visual-semantic` VS-04/VS-06/VS-14 |
| GE-09 | 🟡 **Markdown for Agents — ADVANCED, opt-in** | Chỉ bật khi đo trước: `curl -H "Accept: text/markdown"` + baseline markdown-requests trong log. ⚠ Bật = tự gắn `Content-Signal: ai-train=yes` → client đang chặn training phải duyệt trước. **Chưa có data markdown → citation** — là hygiene rẻ, **không phải lever**, không đưa vào cam kết | C | L3 | `technical-seo-audit` 1.18 |
| GE-10 | 🟡 **Logfile T7 — verify access, không phải KPI** | Logfile quý 3 tách hit theo mục đích bot (search / training / user-triggered). Dùng để **xác nhận GE-02 còn đúng**, không dùng làm chỉ số visibility báo cáo khách | A | L3 | `seo-logfile-analysis` · công đoạn 27 |

## Trụ C — SOURCE OF TRUTH & ENTITY (cuối T1→T3 · công đoạn 13 · PIC: Content + SEO)

> Nhịp: **1 lần dựng nền**, review mỗi quý. 🔺 Nâng hạng 08/2026: fan-out đã dịch từ *keyword discovery* sang **verification tại entity home** — 3 phương pháp độc lập hội tụ.

| ID | Item | Tiêu chí ĐẠT | Ev | Lớp | Route |
|---|---|---|---|---|---|
| GE-11 | 🔴 **`site:domain` answerability test** | Tự chạy `site:yourdomain.com [câu hỏi thương mại]` cho 5-10 câu khách hay hỏi (giá, tính năng, so sánh, chính sách, ở đâu): phải có trang trả lời được **bằng text trên site chính chủ** — không giấu trong PDF, không render JS-only, không chỉ nằm trên sàn/đại lý. Evidence: `site:` xuất hiện trong **64% fan-out queries** của ChatGPT (Nectiv 13/08/2026, n≈4K, đo qua API), domain slot điền từ memory (wire capture), citation share `site:`/`official`/`pricing` đang tăng (Peec) — **3 phương pháp độc lập cùng hướng** | B | L1 | [[Entity Home]] · [[Query Fan-Out]] |
| GE-12 | 🟠 **Owned truth pages đầy đủ** | Có và cập nhật: about · pricing · FAQ · docs/hướng dẫn · chính sách. Trang docs **có giá trị GEO kể cả khi không bao giờ rank** (vai trò: nguồn để AI mô tả đúng brand). Kèm **hallucinated-URL check**: URL AI bịa ra = ứng viên tạo trang / redirect | C | L2 | [[GEO]] §4 Pillars |
| GE-13 | 🟠 **Brand E-A-V nhất quán đa kênh** | Tên brand · mô tả dịch vụ · thông tin cốt lõi (NAP, năm thành lập, phạm vi phục vụ) **giống nhau** trên site chính, GBP, LinkedIn, Facebook, directory ngành, review platform. Lệch thông tin = AI trả lời sai về brand (đo bằng Information Accuracy ở GE-03) | D | L1 | `tier-1-entity` · `tier-1-social-google-stack` |
| GE-14 | 🟡 **Entity Home + schema entity** | Organization/Person + `sameAs` trỏ đủ profile chính; @id graph nối Entity Home. ⚠ Làm vì **entity understanding + rich result**, KHÔNG vì citation (guardrail 2) | A | L2 | `schema-markup-generator` §0 |
| GE-15 | 🟡 **Named author + experience-in-content** | Bài trọng điểm có tác giả thật, và **kinh nghiệm nằm TRONG nội dung** ("khi chúng tôi test trên 40 site khách…") — không phải box bio. Rubric AI Mode: Experience Signals **17,4%** vs Author Credibility 8,5% (Surfer, ⚠ COI vendor, correlational) | C | L2 | [[Authorship]] · `semantic-content-writing` |

## Trụ D — PASSAGE ARCHITECTURE (mỗi bài publish/refresh · công đoạn 15-21-23-28-29 · PIC: Content + SEO)

> Nhịp: **mỗi bài**, design-in từ Outline/AM chứ không vá sau. Scoring: **/12**.
> Ngưỡng chunk: dùng bảng canonical **"3 con số chunk"** tại [[Audition Chunk]] — không neo con số ở đây.

| ID | Item | Tiêu chí ĐẠT | Ev | Lớp | Route |
|---|---|---|---|---|---|
| GE-16 | 🔴 **Mở đầu trang = câu trả lời (AX2)** | 100-150 từ đầu của main content trả lời thẳng câu hỏi chính; không storytelling intro (ngoại lệ narrative niche — SERP-intent-conditional). Intro theo Extractive + Abstractive, đúng Concordance với thứ tự H2; bài informational chính có **Key-Facts table**. Evidence: **38%** citation AIO trích từ 100 từ đầu — tăng từ 20% một năm trước (Surfer 06/2026); **44,2%** từ 30% đầu trang (Indig 02/2026) | B | L1 | AX2 · P16 · `general-summary-introduction` |
| GE-17 | 🔴 **Heading = câu hỏi thật + scope 1 trang 1 câu hỏi (AX7)** | Heading khớp trực tiếp câu hỏi con user hỏi AI (K2Q khi query dạng câu hỏi). Map fan-out theo **cluster** — ~90% fan-out gom được vào ≤4 cluster và chỉ ~27% consistent giữa các lần chạy → **không đuổi từng query**. **Không dải số từ / số heading cố định** — độ dài theo loại node (quality node/pillar dài hơn leaf), benchmark đối thủ, intent, vị trí topical map, bộ query target (Vincent 29/08/2026); trang gánh ≥2 câu hỏi chính → **TÁCH page** theo QDP (26-50% subtopic thắng 100%) | B | L1 | AX7 (title/meta/heading ↔ cluster) · O7/P7 · [[QDP-QDH-QDS]] · `geo-fanout-research` |
| GE-18 | 🔴 **Câu đầu sau heading = câu trả lời (Subordinate Text)** | 4 pattern theo loại heading: định nghĩa → "X là…" · how-to → "Để X, làm N bước…" · so sánh → verdict trước · yes/no → trả lời ngay rồi mới điều kiện. Câu trả lời trực tiếp 40-50 từ | B | L1 | [[Subordinate Text Match]] · W1 |
| GE-19 | 🔴 **Chunk tự đứng + heading hierarchy mạch lạc (AX1)** | Mỗi H2 cắt rời vẫn đủ Entity + context + claim; không đại từ hồi chỉ ("điều này", "như đã nói ở trên"); passage 100-170 từ cho ý chính. Heading hierarchy phải mạch lạc và mang nghĩa — cơ chế `includeAncestorHeadings` của [[Vertex AI Search]] cho thấy **heading tổ tiên đi kèm chunk như metadata**, chunk giữa bài vẫn "biết" mình thuộc mục nào. Heading rỗng nghĩa ("Tổng quan", "Kết luận") làm mất lợi thế này | A/B | L1 | AX1 · [[Audition Chunk]] |
| GE-20 | 🟠 **Mật độ E-A-V** | ≥3 EAV/100 từ ở L0; câu chứa số phải là **câu hoàn chỉnh quotable** (S-V-O) — "không phải con số được cite, mà là câu bao quanh nó". ⚠ Có trần: mật độ fact cao quá ngưỡng thì signal-to-noise giảm — cover đủ rồi dừng | C | L2 | [[E-A-V Framework]] · `semantic-content-writing` v2.1 |
| GE-21 | 🟠 **Quote + số liệu + cite nguồn sau claim** | 3 tactic peer-reviewed mạnh nhất (KDD 2024, đọc primary): **quote nguồn liên quan** (mạnh nhất) · **số liệu định lượng** · **trích nguồn sau claim** (yếu khi đứng một mình, mạnh nhất khi kết hợp). Chọn theo domain: bài factual → cite nguồn · opinion/pháp lý → số liệu · kể chuyện/lịch sử → quote. Mỗi con số truy được **nguồn + ngày**. Ngược lại: **nhồi từ khoá còn tệ hơn không làm gì**; giọng văn "authoritative" không cải thiện đáng kể. ⚠ Đòn bẩy lớn nhất khi trang đang là **nguồn yếu** trong câu trả lời; trang đã thống trị câu trả lời thì đầu tư chỗ khác | A | L1 | W3/P17 · [[sources/geo-paper-kdd-2024]] |
| GE-22 | 🟠 **Non-commodity / Information Gain** | Bài phải trả lời được: *"cái gì ở đây chỉ có thể đến từ chúng tôi?"* — dữ liệu gốc, test thật, case thật, ảnh/biểu đồ tự làm. Test ngược: nếu tóm tắt top SERP rồi chạy qua AI là ra được bài này → **commodity, làm lại**. Google chính chủ: *"unique, non-commodity content"* (Sullivan 04/2026: unique · specific · authentic) | A | L1 | [[Non-Commodity Content]] · [[Information Gain Score]] |
| GE-23 | 🟡 **Passage verifiability (AX6)** | Mỗi claim quan trọng nằm trong passage vừa **rank được** vừa **khớp câu phát biểu** ở mức passage. Cơ chế linkify 2 pha (patent US11769017B1 + US20240289407A1): AI sinh summary từ SRD rồi mới verify từng đoạn bằng khoảng cách embedding trước khi gắn link → **document nuôi summary ≠ document được cite** | A | L2 | AX6 · [[AI Mode]] |
| GE-24 | 🟠 **Freshness thật** | Trang commercial/pricing/so sánh có chu kỳ cập nhật **nội dung thật** ~30 ngày (freshness window per-query-type). 🔴 KHÔNG date-spoofing, KHÔNG chỉ đổi năm trên title. Lưu ý mới 08/2026: **content năm cũ không chết** — ChatGPT search song song "2026" và "2025" trong cùng chain (multi-year search, kỹ thuật Gemini có trước); unigram year đã rớt khỏi top-5 | B | L1 | `content-refresh` v1.1 T15 · [[Freshness]] |
| GE-25 | 🟠 **Visual semantic tự soi + Blur Test (AX5)** | 5 điểm: (1) centerpiece above-the-fold trả đúng intent · (2) visual hierarchy khớp heading hierarchy · (3) DOM order = visual order · (4) info quan trọng không giấu trong tab/accordion · (5) không popup/ads cắt ngang main content. Chốt bằng Blur Test: screenshot blur 50% vẫn nhận ra topic + function | D | L1 | AX5 · `sop/07` B7 · `tier-1-visual-semantic` |
| GE-26 | 🟠 **Page-type fit + backfire guard** | Chọn page type theo engine mục tiêu và **date-stamp** (mix citation theo page type đổi theo phiên bản engine). Guardrail listicle: không tự xếp mình #1 khi không có phương pháp chấm công khai · công bố CoI · không scale hàng loạt · `ItemList` schema, **cấm AggregateRating** trên listicle tự làm. ⚠ Cite ≠ recommend: bài liệt kê đối thủ có thể được cite mà vẫn recommend đối thủ · **AI nghi ngờ vì brand tự xếp hạng hoặc tự công bố bằng chứng** (Vincent chốt 19/10/2026): không coi là lỗi lớn, không gỡ bài. Giải nghi ngờ bằng offsite consensus (GE-28…32: mention, review, listicle bên thứ ba). Bài top list trên site mình viết khách quan, có EEAT: tiêu chí chấm công khai, tác giả có chuyên môn thật, nguồn dẫn, nêu điểm mạnh thật của đối thủ, công bố CoI | C | L2 | [[Best List Page]] · [[Page Types]] |
| GE-27 | 🟡 **AIO counter-positioning** | So content hiện tại với AI answer đang hiển thị: claim AIO bỏ sót → cover sâu; format AIO ưa (definition đầu, danh sách có cấu trúc, E-A-V) → align. Mục tiêu cuối là thành [[Core Source]] (được cite lặp lại), không phải 1 lần | C | L2 | AX3 · `geo-content-optimization` Bước 4 |

## Trụ E — OFF-SITE CONSENSUS & MENTIONS (T4→T7 + duy trì · công đoạn 20 + 26 · PIC: SEO + Content)

> Nhịp: **mỗi đợt offsite**. Scoring: **/5**. Nguyên tắc nền: **mention ≠ link** — off-page link authority tương quan ≈ 0 với AI citation, nhưng **brand mention** là nhóm tương quan mạnh nhất.

| ID | Item | Tiêu chí ĐẠT | Ev | Lớp | Route |
|---|---|---|---|---|---|
| GE-28 | 🟠 **Backlink consensus lens** | Đợt link T4-T7 ưu tiên nguồn mà AI engines hay cite trong ngách (xác định khi research). Không viện DR thay cho chất lượng chunk — "DR does not matter much" ở page-level | B | L2 | `backlink-research` → `backlink-plan` |
| GE-29 | 🟠 **Third-party mentions có chủ đích** | Kênh theo thứ tự tương quan (Ahrefs 75k brands 12/2025, ⚠ correlation): **YouTube mentions ~0,737** · branded web mentions 0,66-0,71 · branded anchors 0,51-0,63. Ưu tiên: 1 video YouTube đúng chủ đề + bài trên blog/báo ngành đang rank + review platform. Brand xuất hiện **cạnh đối thủ, đúng ngữ cảnh dịch vụ** | B | L1 | [[Surround Sound]] · `pr-semantic-content` |
| GE-30 | 🟡 **Surround Sound nodes nằm trong topical map** | Node off-site cho core entity được **lên kế hoạch trong topical map**, không phải PR rời. Phân bổ theo funnel: educational cho giai đoạn chưa nhận thức vấn đề → social proof (listicle/review/forum) cho giai đoạn quyết định | C | L2 | `topical-map-creation` v2.1 §14b |
| GE-31 | 🟡 **UGC/forum VN — giả thuyết, phải test** | Reddit seeding có evidence ở thị trường Anh ngữ nhưng **ROI đảo chiều theo engine + thời điểm** (Reddit #1 trên Gemini app 29,2% · #2 AIO 18,5% · ChatGPT sập <1% từ 08/2026). Ở VN, tương đương Voz/Tinhte/nhóm Facebook = **giả thuyết chưa có data** → chạy như thí nghiệm có đo, không bán như tactic đã chứng minh | C | L3 | [[Reddit Seeding]] |
| GE-32 | 🟡 **Best-of bên thứ ba** | Pitch để có mặt ở **1/3 đầu** các listicle bên thứ ba đang được cite trong ngách; giữ thông tin cập nhật (danh sách cũ feed AI thông tin sai về chính mình) | C | L2 | [[Best List Page]] |

## Trụ F — MEASUREMENT & REPORTING (T1 → weekly nội bộ → T6 → T10 → quý · công đoạn 24 + 32 + 33 · PIC: SEO Lead Project)

> Nhịp: **chạy suốt dự án**. Scoring: **/5**.

| ID | Item | Tiêu chí ĐẠT | Ev | Lớp | Route |
|---|---|---|---|---|---|
| GE-33 | 🔴 **Polling standard** | Mỗi prompt chạy **≥3 lần** (chuẩn nội bộ 5 lần/prompt/engine) rồi báo tỷ lệ, không báo 1 lần chạy. Lý do: variance nội bộ 1 model 10-34%; sau 3 lần chỉ ~2,2% citation còn nguyên. Nhịp nội bộ **hàng tuần-2 tuần** (AI Mode đổi 56% nguồn/tuần, ChatGPT 74%), báo cáo khách theo mốc. Mọi lần đo **date-stamp engine + model version** | B | L2 | `geo-tracking-prompt-selection` v1.1 |
| GE-34 | 🟠 **Per-engine + topic-level SoV** | Báo cáo **theo topic**, không theo từng prompt. Tách kênh: AIO ≠ AI Mode (86% tương đồng nội dung nhưng chỉ 13,7% trùng citation) ≠ Gemini app ≠ ChatGPT — chỉ 2,37% URL được cả 3 engine cùng cite, 91% single-engine. Cảnh báo nếu Concentration >70% ở một engine | B | L2 | [[AI Visibility Measurement]] |
| GE-35 | 🔴 **Evidence bar + version discipline** | (1) **4 dấu hiệu KHÔNG phải bằng chứng**: được crawl · được index · AI nhắc lại nội dung của bạn · AI nói tactic đó hiệu quả — cả 4 xảy ra với **mọi file text trên web mở** (thí nghiệm cats.txt). (2) **Luật truy-về-primary**: mọi "leak"/nghiên cứu trước khi vào pitch/deck phải truy về nguồn gốc — case "LEAKED Google" 01/2026 là bản viral đã **cắt disclaimer** của tác giả gốc. (3) Metric AI luôn dán nhãn **directional**, đối chiếu referral thật (GA4/server log) trước khi tuyên bố thắng. (4) Mọi số có nguồn + tháng; register refresh theo lint quý | A | L1 | [[syntheses/geo-evidence-register-2026-08]] · `gtv-client-report` v1.2 🔒 |
| GE-36 | 🟠 **KPI GEO cam kết được** 🔒 | Deal có ≥1 KPI GEO đo được: keyword xuất hiện trong AI Overview · brand mention trong AI Overview cho query Commercial Investigation · **Brand Mention in LLM: ChatGPT + Google AI (AI Mode/Gemini) BẮT BUỘC cả hai** (Vincent chốt 29/08/2026 — thay ngưỡng "≥2/4 tool" cũ; Perplexity/Copilot/Claude là bonus, chạy ẩn danh). Lý do: 2 chiến trường phủ ~85-95% việc (ChatGPT 75-80% AI referral/thị phần chatbot — Similarweb/StatCounter; Gemini app 1B MAU 08/2026 + AIO 2B — Google official). Kèm **AI CVR vs Organic CVR** (GA4 channel "AI Assistant") là KPI directional, không phải KPI nghiệm thu. Không cam kết per-prompt | D | L3 | `GTV Ops/wiki/offers/kpi-commitment-template.md` §D 🔒 · `gtv-client-report` v1.3 |
| GE-37 | 🟠 **T6 giữa kỳ · T10 báo cáo kép · handover** | Đo lại **cùng prompt set** ở T6 và T10; báo cáo kép = KPI ranking/traffic + AI visibility so baseline T1. Bàn giao duy trì: prompt set + baseline + register số liệu + lịch đo quý | D | L3 | công đoạn 24/32/33 · `khung-duy-tri.md` |

---

## Phụ lục — Bảng NOT-a-lever (nói được với khách)

| Không phải lever | Vì sao | Nói gì thay thế |
|---|---|---|
| 🔴 **llms.txt** | Không AI system nào dùng (Mueller, nguyên văn); bot không request; Ahrefs 100k domains không thấy lợi thế | "Điều khiển AI crawler là robots.txt" → GE-02 |
| 🔴 **Schema để được cite** | Causal DiD 1.885 trang: hiệu ứng ≈ 0 | "Schema cho rich result + entity" → GE-14 |
| **Đẻ thêm thật nhiều bài** | Số trang ↔ AI mention tương quan ~0,19 | "1 trang trả lời trọn 1 câu hỏi" → GE-17 |
| **DR / backlink page-level** | Off-page authority tương quan ≈ 0 với citation; "DR does not matter much" | "Mention thay vì link" → GE-29 |
| **Ultimate guide dài** | Trang cover 26-50% subtopic thắng trang cover 100% | "Tách trang" → GE-17 |
| **Đổi ngày đăng cho mới** | Google xử như spam; freshness thật mới tính | "Cập nhật nội dung thật" → GE-24 |
| **Tự xếp mình #1 trong listicle** | Cite ≠ recommend; cohort 220+ site scale AI content: 54% mất ≥30% traffic | "Listicle có guardrail" → GE-26 |
| **Gỡ bài top list vì AI nghi ngờ brand tự xếp hạng** | Nghi ngờ đến từ thiếu consensus bên ngoài, không đến từ việc có bài (Vincent chốt 19/10/2026) | Giữ bài, viết khách quan + EEAT; tăng offsite consensus → GE-26, GE-28…32 |
| **Nhồi chữ "official" vào trang** | `site:`/`official` là triệu chứng đã ở trong shortlist, không phải nguyên nhân; unigram đổi gần hết sau 1 phiên bản model | "Làm entity home trả lời được" → GE-11 |
| **Chèn câu tối ưu cho LLM reranker** | Paper RAF: hiệu quả gần như mất trên model lớn; là attack paper, dual-use | "Viết tự nhiên, rõ ràng" → GE-18 |
| **Chạy theo từng fan-out keyword** | Chỉ ~27% fan-out lặp lại giữa các lần chạy | "Cover cluster" → GE-17 |
| **Markdown for Agents để được cite** | Chưa có data markdown → citation; crawler search chưa request | "Hygiene rẻ, đo trước" → GE-09 |
| **"Gecko Score" / "Jetstream"** | Không tồn tại trong tài liệu Google | Nói `semantic_similarity_score` / `relevance_score` → guardrail 4 |

---

## Mapping v1 (GE-01…13) → v2 (GE-01…37)

| v1 | v2 | Ghi chú |
|---|---|---|
| GE-01 Speed/TTFB | **GE-06** | giữ nguyên nội dung + nhãn estimate |
| GE-02 Indexed + rank + hygiene | **GE-01** (rank) + **GE-07** (hygiene) | tách: eligibility là gate, hygiene là vệ sinh |
| GE-03 Chunk self-contained | **GE-19** | + cơ chế ancestor headings |
| GE-04 Front-load | **GE-16** | + General Summary/Key-Facts gộp vào |
| GE-05 Heading-query alignment | **GE-17** | bỏ "8-12 sub-queries" trần → map theo cluster |
| GE-06 General Summary + Key-Facts | gộp vào **GE-16** | |
| GE-07 Citation & evidence KDD | **GE-21** | |
| GE-08 Blur Test + freshness | **GE-25** (visual) + **GE-24** (freshness) | tách 2 việc khác nhau |
| GE-09 Backlink consensus | **GE-28** | |
| GE-10 Brand entity nhất quán | **GE-13** | + tách GE-11/12/14/15 |
| GE-11 Prompt set baseline | **GE-03** | + Information Accuracy |
| GE-12 Re-measure T6→T10 | **GE-33** (polling) + **GE-34** (per-engine) + **GE-37** (mốc) | tách 3 |
| GE-13 Guardrail communication | **GE-05** (kickoff) + **GE-35** (evidence bar) | tách 2 |
| — | **mới:** GE-02, GE-04, GE-08, GE-09, GE-10, GE-11, GE-12, GE-14, GE-15, GE-18, GE-20, GE-22, GE-23, GE-26, GE-27, GE-29, GE-30, GE-31, GE-32, GE-36 | |

⚠ Nơi còn tham chiếu ID cũ, sửa khi chạy Bước 3-4: `sop/06/README.md` §3b · `SEO Production/CLAUDE.md` Ma trận M · `tier-1-gbp-local.md` L71 · `monthly-project-review.md` MRQ-05.

---

## Scoring — 4 bộ theo nhịp

| Bộ | Items | Điểm | Khi chấm | Ai chấm |
|---|---|---|---|---|
| **Bộ NỀN** (trụ A+B+C) | GE-01…GE-15 | **/15** | T1 → chốt cuối T3; review lại mỗi quý | SEO Lead Project |
| **Bộ BÀI** (trụ D) | GE-16…GE-27 | **/12** | Mỗi bài publish/refresh | Content self-check → SEO EX |
| **Bộ OFFSITE** (trụ E) | GE-28…GE-32 | **/5** | Mỗi đợt offsite T4-T7 + duy trì | SEO |
| **Bộ ĐO** (trụ F) | GE-33…GE-37 | **/5** | T1 · T6 · T10 · quý duy trì | SEO Lead Project |

**Skip Rules** (theo `tracking-schema.md`): item không áp dụng cho dự án (vd GE-31 khi không làm forum, GE-09 khi client chặn AI training, GE-36 khi deal không có KPI GEO) → **để trống, không tick 0**, không tính vào mẫu số. Verdict GE-04 = *Tối thiểu* → GE-09, GE-27, GE-30, GE-31, GE-32 để trống hợp lệ.

**Review 3 tầng** như các checklist Tier 1 khác: Self 100% → SEO EX verify → Lead random 25-30%. Gap ≥3 item/tháng = cờ đỏ.

## Bản render & tracking

| Dạng | Ở đâu | Ghi chú |
|---|---|---|
| **Markdown (file này)** | `sop/06-self-checklist/tier-1-geo.md` | **Nguồn sự thật.** Sửa ở đây, không sửa nơi khác |
| **HTML nội bộ** | `sop/06-self-checklist/tier-1-geo.html` | Tick được, 4 thanh tiến độ theo bộ, trạng thái gate tự cập nhật. **Sinh tự động:** `python3 build-tier-1-geo-html.py` |
| **Google Sheet** | "GEO Checklist GE v2 — Tracking (GTV SEO)" · folder Drive **GTV SEO — GEO Checklist 2026** | 3 tab: lưới chấm · từ điển 37 items · hướng dẫn+guardrail. **Sinh tự động:** `build-geo-sheet-payload.py` → `push-geo-sheet.py --reuse` |

> Cả 3 dạng derive từ file markdown này. **Master đổi → chạy lại 2 script**, đừng vá tay từng bản (đó chính là cách 3 lớp bắt đầu lệch nhau).

## Tracking columns đề xuất (cho Google Sheet)

| Nhóm | Cột | Field |
|---|---|---|
| Thông tin | A-F | STT · Dự án · Tháng dự án (T1-T10) · Bộ đang chấm (NỀN/BÀI/OFFSITE/ĐO) · URL hoặc đợt · PIC |
| Nền | G-U | GE-01 → GE-15 (tick 1/0/trống) |
| Bài | V-AG | GE-16 → GE-27 |
| Offsite | AH-AL | GE-28 → GE-32 |
| Đo | AM-AQ | GE-33 → GE-37 |
| Gate | AR-AU | G-T1 · G-ENT · G-BÀI · G-KH (Y/N) |
| Score | AV-AX | Self Score (/15, /12, /5, /5 theo bộ — denominator động theo cột D) · Self % (mẫu số = COUNTA, ô trống không tính) · Self Note |
| Review | AY-BB | EX V-Pass · Lead Score · Gap (trống khi chưa có Lead Score) · Flag Items |

---

## Quy trình tick

1. **T1 mở dự án** → chấm Bộ NỀN. G-T1 fail (GE-01/02/03) → dừng lớp GEO, báo Lead: làm nền SEO trước.
2. **Cuối T1→T3** → chốt Bộ NỀN, G-ENT (GE-11) phải pass trước khi tính là "nền GEO xong".
3. **Mỗi bài** → Content tự chấm Bộ BÀI trước khi submit. 4 item G-BÀI fail bất kỳ = trả về, không đưa sang onpage.
4. **Mỗi đợt offsite** → chấm Bộ OFFSITE cùng lúc với `tier-1-offpage-backlink.md`.
5. **T1 / T6 / T10 + quý** → chấm Bộ ĐO. Mọi deliverable gửi khách qua G-KH (GE-05 + GE-35) trước khi gửi.
6. Item fail → mở **Route** ở cột cuối, fix theo skill/SOP rồi tick lại. Cần audit sâu 1 trang → escalate skill `geo-content-optimization` (6 bước + Retrievability Scorecard).
7. Ghi Self % + Self Note (item chưa tick + lý do + plan fix) → submit review.

---

## Wiki / skill cross-refs

- **AX1-AX7 canonical** → `sop/08-onpage-checklist.md` §AX + `skills/seo-onpage/references/p-series-checklist.md` (AX6 mới 08/2026, patent verified 21/08).
- **Ngưỡng chunk canonical** → [[Audition Chunk]] §"3 con số chunk" (128 ChatGPT · 800 OpenAI file_search · 500 Vertex · 200 words Chrome). **Không neo số ở checklist này.**
- **Số liệu + nhãn evidence** → [[syntheses/geo-evidence-register-2026-08]] (whitelist/blacklist số được in theo lớp).
- **Audit + rewrite 1 trang** → skill `geo-content-optimization` · **đo citation share** → skill `geo-tracking-prompt-selection`.
- **Khái niệm nền** → [[GEO]] · [[AI Visibility Measurement]] · [[Query Fan-Out]] · [[Audition Chunk]] · [[Core Source]] · [[Entity Home]] · [[Non-Commodity Content]] · [[Vertex AI Search]] · [[Retrieval-Augmented Generation]].
- **Quy trình 6 điểm chạm + luật derive 3 lớp** → `sop/09-timeline/lop-geo-v2.md`.

## Changelog

- **v2.0.2 (2026-08-29)** — GE-17: gỡ "Trang 500-2.000 từ / 7-20 subheading" (feedback Vincent cùng ngày: con số chỉ thường đúng cho cluster content/query dài; độ dài theo **loại node** — quality node/pillar dài hơn leaf — + đối thủ + intent + vị trí topical map + query target). GE-17 chỉ kiểm scope 1 trang 1 câu hỏi chính. Đồng bộ: `tier-1-outline-am` / `tier-1-content-writing` § G-BÀI, `02-content-brief`, skill SOM 2.1.1 · SCA 2.1.1 · GCO 1.2.1, Content Production + SEO Production/PROJECTS pack, Sheet ô F31. Chạy lại build HTML + payload.
- **v2.0.1 (2026-08-29)** — GE-36: ngưỡng Brand Mention in LLM "≥2/4 tool" → **ChatGPT + Google AI bắt buộc cả hai** (Vincent chốt 29/08; Perplexity/Copilot/Claude bonus) + KPI directional AI CVR vs Organic CVR (GA4 channel "AI Assistant"). Gate G-BÀI đã nối vào `tier-1-content-writing.md` § "G-BÀI" + `tier-1-outline-am.md` § "G-BÀI design-in" + pipeline Content Production (`G-BAI-01`). Chuẩn chunk GTV 4 tầng (không cap số từ section · L0 40-75 từ · khối ý <~200 từ · câu tự đứng) thống nhất ở `semantic-content-writing` 2.2 / `general-summary-introduction` 2.3 / `semantic-outline-methodology` 2.0.3 / `geo-content-optimization` 1.2. Chạy lại `build-tier-1-geo-html.py` + `build-geo-sheet-payload.py` sau khi sửa.
- **v2.0 (2026-08-23)** — 13 → 37 items, 4 trụ → **6 trụ = 6 điểm chạm** quy trình. Mới: trụ Source-of-truth & Entity (nâng hạng theo evidence `site:` 64%), scoring 4 bộ theo nhịp, Top-10 impact, tag phân lớp L1/L2/L3, cột evidence tier, bảng NOT-a-lever, mapping v1→v2, tracking columns, Quy trình tick. Gỡ: "8-12 sub-queries" trần (hết hạn theo Batch 40). Thêm guardrail 4 (tên bịa Gecko/Jetstream, 500-token) + 5 (nhồi "official"). AX5 → AX6.
- **v1.0 (2026-07-19)** — 13 items, 4 trụ, P0 5 items, 3 guardrail. Nguồn: AX1-AX5 + 5 Core Levers.
