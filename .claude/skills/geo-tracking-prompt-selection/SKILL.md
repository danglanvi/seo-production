---
name: geo-tracking-prompt-selection
description: "GEO (Generative Engine Optimization) prompt selection and tracking framework for optimizing brand visibility on AI search engines — ChatGPT + Google AI (AI Overviews / AI Mode / Gemini) bắt buộc, Perplexity / Copilot / Claude bổ sung."
compatibility: "Gói skill kèm references. Router geo-audit cần bundle 5 skill mảng; chế độ audit nhận evidence dán/export hoặc công cụ đọc phù hợp."
metadata:
  version: "1.6.1"
---

# GEO Tracking & Prompt Selection Skill

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

Framework for selecting and organizing prompts to track brand visibility on AI search engines.


**Trước khi chấm GEO:** nếu chưa nạp hợp đồng v1.1 trong phiên, đọc `references/audit-contract.md` (bản đóng gói): UNKNOWN khác N/A, điểm nhị phân + độ phủ, gate theo URL/engine và bàn giao finding. Quy tắc v1.1 này áp cho các bảng audit GEO bên dưới; changelog chỉ là lịch sử.

## Ưu tiên kênh (Lead chốt 29/08/2026)

| Kênh | Vai trò trong prompt set + KPI | Lý do (nguồn + nhãn) |
|---|---|---|
| **ChatGPT** | **Bắt buộc** | ~75-80% AI referral tới website và thị phần chatbot (Similarweb 06/2025 B · SE Ranking 2026 B · StatCounter live A); CR referral cao nhất trong các AI (Seer 15,9% — B, directional) |
| **Google AI** = AI Overviews + AI Mode + Gemini app | **Bắt buộc** (đo **tách 3 bề mặt**, vì AIO ≠ AI Mode chỉ 13,7% trùng citation) | AIO 2 tỷ user (Pichai, A) · AI Mode 100M sau 2 tháng · Gemini app **1 tỷ MAU 08/2026** (Google official, A) · VN: gemini.google.com #9 top website 07/2026 (Similarweb A) |
| Perplexity · Copilot · Claude | **Bổ sung** — có thì đo, không có không sao | Copilot → Bing; Perplexity chia hạ tầng retrieval; tổng cộng phần nhỏ (kinh nghiệm vận hành GTV, nhãn F — chưa có nghiên cứu độc lập) |

Hệ quả vận hành: (1) KPI Brand Mention đọc là **"có mặt trên CẢ ChatGPT lẫn Google AI"** — thay ngưỡng "≥2/4 tool bất kỳ" (GE-36 `tier-1-geo.md` từ v2.0.1, `gtv-client-report` từ v1.3); (2) prompt set chạy tối thiểu trên ChatGPT + AI Mode + Gemini, AIO check theo keyword; (3) DIY sheet cột engine xếp theo thứ tự ưu tiên này. Xem lại mỗi quý — thị phần là moving target.

## Quick Decision: Website Type

First, determine website type to choose the right approach:

| Question | Service/Agency | E-commerce |
|----------|---------------|------------|
| Number of products/services | 1-10 | 50+ |
| User searches by | Brand name | Product name |
| Decision cycle | Long (weeks) | Short (<1 week) |
| **Approach** | Funnel-based (28-40 prompts) | Matrix-based (80-100 prompts) |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| ChatGPT, Perplexity Sonar, Gemini qua OpenRouter | Đối tượng đo: trả lời bộ prompt có web search | Dùng ở bước đo. Đây là engine được đo, không phải model phụ |
| Code tất định (regex, `geo_kpi.py`) | Brand được nhắc, domain được trích, SoV, so lần đo bằng bootstrap, tách số Ahrefs | Dùng. Đếm là việc của code |
| Jev | Vai trò brand trong câu trả lời, loại bằng chứng, phản đối | Không dùng trong skill này. Skill `geo-answer-lab` làm việc này với rubric `ai-answer-brand` đã hiệu chuẩn |
| EmbeddingGemma 2 | Gom prompt gần trùng khi lập bộ prompt | Không dùng. Bộ prompt 28–40 câu do người đọc hết được, và chưa có gold để đặt ngưỡng trùng |
| GLM Flash | Trích câu nguyên văn | Không dùng. Trích câu phản đối thuộc `geo-answer-lab` |
| Claude | Chọn prompt, đọc `compare.md`, đọc câu trả lời gốc của prompt đổi mạnh, viết nhận định | Dùng |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,openrouter?,ahrefs?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0b — Readiness, scope và baseline

Khi router gọi hoặc mở baseline mới: đọc `references/readiness-baseline.md` trước các nhánh dưới; chấm GE-04 từ evidence dự án, chốt scope/prompt set, thu baseline GE-03 và kiểm GE-05. Chưa có dữ liệu thì trả UNKNOWN hoặc xác nhận chưa đo; vẫn thu evidence nền, không mắc vòng lặp “cần baseline để tạo baseline”. Đơn vị phân phối: skill này + references; nguồn wiki chỉ để bảo trì.

### For Service/Agency Websites
1. Identify 1-3 core services
2. List 5-7 competitors
3. Apply funnel allocation: TOFU 15% → MOFU 35% → BOFU 50%
4. Use templates from [prompt-templates.md](references/prompt-templates.md)
5. Set KPIs per [kpis-metrics.md](references/kpis-metrics.md)

### For E-commerce Websites
1. Identify top revenue categories (allocate prompts by revenue %)
2. List 5-7 competitors
3. Build 3-layer matrix: Category × Intent × Price Segment
4. See detailed matrix in [ecommerce-matrix.md](references/ecommerce-matrix.md)
5. Add seasonal prompts (Tết, Black Friday, Product launches)

### Đo mốc và đo lại (ngày 14, 30, 60)

Đọc `references/do-va-do-lai.md` trước khi đo. Tóm tắt:

1. Thu câu trả lời bằng `skills/geo-answer-lab/scripts/collect.py`, mỗi prompt × engine ≥ 3 lượt. Đặt `--budget` theo số lượt: mặc định 5 USD không đủ cho bộ 30 prompt.
2. Chạy lớp regex bằng `skills/geo-answer-lab/scripts/prepare.py`.
3. Tính KPI: `python3 -I skills/geo-tracking-prompt-selection/scripts/geo_kpi.py kpi …` → `kpi/kpi.json`, `kpi/by_prompt.tsv`.
4. Đo lại ở ngày 14, 30, 60 sau ngày ghi đợt sửa lên site. So bằng `geo_kpi.py compare --change-date <ngày ghi>`.
5. Chỉ kết luận tăng hoặc giảm khi ngày 14 và ngày 30 cùng chiều và nằm ngoài nhiễu. Nếu model đổi, không đọc chênh là tác dụng của việc sửa.

Bẫy engine (đo thật 18/10/2026):

- Perplexity Sonar không nhận plugin web `native`. `collect.py` gọi Sonar ở chế độ `builtin`.
- Gemini trả link `vertexaisearch.cloud.google.com/grounding-api-redirect/…`. Domain nằm ở `title`, nên chỉ đếm được domain, không đếm được URL.
- AI Overview và AI Mode không có API. Ghi UNKNOWN hoặc chụp tay 10 prompt BOFU ở cùng ngày đo.

### Số trích dẫn AI từ Ahrefs (theo quý, bổ sung cho bộ prompt)

Ahrefs đếm citation theo kho prompt của Ahrefs, không theo bộ prompt của dự án. Số này cho biết xu hướng và vị trí so với đối thủ. Số này không thay lệnh `kpi`.

1. Gọi `site-explorer-ai-responses-count` cho domain chính và 4–5 đối thủ: `mode` subdomains, `select` gồm `all_platforms`, `google_ai_overviews_keywords` và từng nền tảng. Mỗi lượt tốn khoảng 105 unit.
2. Lấy thêm 1 mốc cũ của domain chính bằng tham số `date` (ví dụ 3 tháng trước).
3. Ghi kết quả vào `snapshots.json`, rồi chạy `geo_kpi.py ahrefs --snapshots snapshots.json --own <domain> --out ahrefs.md`.
4. Báo trích dẫn từ prompt bằng cột "Từ prompt". KPI AIO theo từ khoá trong hợp đồng đọc cột "AIO theo từ khoá". Không báo `all_platforms`: số này cộng cả hai loại.

Bẫy (đo site agency mẫu 19/10/2026):

- `all_platforms` của site agency mẫu là 645, nhưng 522 lượt là AIO theo từ khoá. Citation từ prompt chỉ có 123.
- Hai chỉ số đi ngược chiều: từ 07/2026 đến 10/2026, citation từ prompt tăng 57 → 123, AIO theo từ khoá giảm 717 → 522. Báo `all_platforms` sẽ ra "giảm".
- Gemini từ 0 lên 11 trong cùng kỳ. Có thể Ahrefs mới mở rộng kho prompt. Chỉ kết luận khi đối thủ được đo cùng 2 mốc.
- Mention (tên brand trong câu trả lời) cần addon Brand Radar. Nếu tài khoản Ahrefs chưa có addon này, `brand-radar-*` trả lỗi "Missing addon". Tài khoản GTV chưa có addon này (19/10/2026). Mention lấy từ lệnh `kpi`.

## Funnel Allocation (Service/Agency)

| Stage | % | Prompts | Focus |
|-------|---|---------|-------|
| **BOFU** | 50% | 15-20 | Comparison, Pricing, Reviews |
| **MOFU** | 35% | 10-15 | Features, Use cases, Top lists |
| **TOFU** | 15% | 3-5 | Educational, Awareness |

## BOFU Prompt Types (Highest Priority)

### 1. Comparison Prompts
```
🇻🇳: "[Brand] vs [Competitor]", "Công ty [X] nào tốt nhất tại [Location]"
🇺🇸: "[Brand] vs [Competitor]", "Best [X] company in [Location]"
```

### 2. Pricing Prompts
```
🇻🇳: "Giá [sản phẩm]", "Chi phí [dịch vụ]", "Báo giá [X]"
🇺🇸: "[Product] pricing", "[Service] cost", "How much does [X] cost"
```

### 3. Trust/Review Prompts
```
🇻🇳: "Đánh giá [Brand]", "[Brand] có uy tín không", "[Brand] lừa đảo hay uy tín"
🇺🇸: "[Brand] reviews", "Is [Brand] legit", "Should I trust [Brand]"
```

## Prompt Formula

```
[Product/Brand] + [Intent Action] + [Modifier]

Examples:
🇻🇳: [iPhone 16 Pro Max] + [mua ở đâu] + [giá tốt nhất TPHCM]
🇺🇸: [iPhone 16 Pro Max] + [where to buy] + [best price HCMC]
```

## KPIs to Commit

| KPI | Description | Target |
|-----|-------------|--------|
| Brand Mention | Times brand appears in AI responses — đếm **trên ChatGPT VÀ Google AI** (kênh bắt buộc) | >60% BOFU prompts, cả 2 kênh |
| AI Citations | Citation từ prompt theo Ahrefs `site-explorer-ai-responses-count`, tách khỏi AIO theo từ khoá (`geo_kpi.py ahrefs`), so cùng tập đối thủ. Cited rate từ lệnh `kpi`. GSC Generative AI (Beta) | Increasing trend (directional) |
| Share of Voice | % mention vs competitors, theo topic, tách engine | >30% SOV |
| Information Accuracy | AI describes brand correctly | >90% accurate |
| **AI CVR vs Organic CVR** (mới 08/2026) | Tỷ lệ chuyển đổi kênh GA4 "AI Assistant" so với Organic Search — setup trong [kpis-metrics.md](references/kpis-metrics.md) § GA4 | Báo cáo directional, không nghiệm thu; benchmark tham chiếu ~10× (GTV first-party, n=1) · 23× (Ahrefs 06/2025) · 15,9% vs 1,76% (Seer) |

## Measurement Reliability Rules (added 08/2026 — all numbers are snapshots, refresh theo lint quý)

### 1. Date-stamp every measurement (MANDATORY)

- ChatGPT's search-tool format changed **3 times since 06/2026**; the `search_queries` payload field disappeared **16-20/08/2026** (wire capture Suganthan, n=8 questions/1 account — observation single-researcher).
- Any tool measuring fan-out via that field (FanoutFox, AirOps-style studies) returns **empty/wrong results** on new conversations until patched. New format: pipe syntax `fast|query|freshness_window|domain` inside `web.run` tool-call messages.
- **Numbers measured before vs after 08/2026 are NOT directly comparable.** Every tracked number must carry: measurement date + tool + format era. Never trend across a format break.

### 2. Citation data reliability caveats

- **Bot noise + lag**: a page 404'd AND deindexed (Google + Bing) still received daily citations for **~8 weeks** (@top5seo 07/2026 — single experiment n=1, author's own label "half-baked"; methodological warning, not a quantitative claim). Treat citation counts as **directional and lagging** — never real-time human visibility.
- **Convergence problem**: asking an LLM "does tactic X work?" is NOT measurement — the model returns the running average of internet discourse and flips verdict when discourse flips, even if reality didn't change (cats.txt falsification experiment, Williams-Cook 08/2026).
- **4 fake proofs checklist** — reject these as GEO "evidence" (all 4 happen to literally any text file on the open web): (1) AI bots crawled it, (2) Google indexed it, (3) facts repeated back via RAG, (4) an LLM verbally endorses the tactic.

### 3. Widget answers rời citation game

ChatGPT `genui_run` widget verticals — stocks, sports schedules, map pins — render OpenAI-hosted interfaces with **no citations to win** (same wire capture, n=8, 08/2026). Exclude these query classes from citation opportunity counts when sizing a prompt list.

### 4. New measurement tools (details in [kpis-metrics.md](references/kpis-metrics.md))

- **Microsoft Clarity AI Citations** — branded vs non-branded **grounding queries** + Share of Authority by query type (official feature, 03/08/2026). Caveats: branded-classification methodology unpublished (alias/abbreviation handling unknown); coverage leans Bing/Copilot ecosystem — verify before committing to clients.
- **GSC → LLM classify workflow** (Glenn Gabe/GSQi, 08/2026) for surfacing AI Mode queries: Search Analytics API bulk export → LLM classifies AI Mode candidates. Needed because GSC's 2 reports can't be joined (performance report has clicks but no surface breakout; Generative AI report has surface but no clicks) — and GSC query data is itself polluted by the tracking industry's own bots.

## References

- **Prompt Templates**: See [prompt-templates.md](references/prompt-templates.md) for complete bilingual templates by industry
- **E-commerce Matrix**: See [ecommerce-matrix.md](references/ecommerce-matrix.md) for Category × Intent × Segment framework
- **KPIs & Metrics**: See [kpis-metrics.md](references/kpis-metrics.md) for detailed tracking setup
- **Checklist**: See [checklist.md](references/checklist.md) for BD consultation checklist
- **Đo mốc và đo lại**: [do-va-do-lai.md](references/do-va-do-lai.md): lệnh chạy, bẫy từng engine, lịch ngày 14, 30, 60, cách đọc `compare.md`
- **Script**: `scripts/geo_kpi.py` (`kpi`, `compare`, `ahrefs`). Test: `python3 -B -m unittest discover -s skills/geo-tracking-prompt-selection/tests`
- **Skill mảng khác của lớp GEO** (12/09/2026): `geo-technical-audit` (gate G-T1, G1) · `entity-seo-plan` mục Lăng kính GEO (G2) · `geo-content-optimization` (G3) · `geo-offsite-audit` (G4) · `geo-audit` (router gộp scorecard 4 bộ; skill này cấp verdict GE-04 + baseline + Bộ ĐO)

## Red Flags to Avoid

❌ Generic prompts ("What is SEO?") - No conversion value
❌ Too many prompts (>100 service, >150 e-commerce)
❌ Only tracking mention count without context
❌ Not updating prompts for new products/competitors
❌ Promising specific rankings - GEO is not deterministic like SEO

## Best Practices

✅ Focus 50% on BOFU - Highest conversion
✅ Track context type, not just mention count
✅ Monthly iteration — đề xuất prompt mới trong cohort riêng, giữ cohort cũ để so sánh; không thay prompt chỉ vì brand đang thua
✅ Include competitors for benchmarking
✅ Add seasonal prompts for e-commerce
✅ Bilingual prompts for VN + US markets
✅ Date-stamp every measurement; label citation numbers as directional (see Measurement Reliability Rules)

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Bộ prompt có ID, funnel, cờ branded và URL đích, chốt chữ trước khi đo. Nguồn lỗi: lần đo lại chỉ so được prompt giữ nguyên chữ và ID.
- [ ] Mỗi prompt × engine có ≥ 3 lượt, mỗi dòng ghi ngày và `model_served`. Nguồn lỗi: thử A/A site agency mẫu 18/10, 2 lượt cùng ngày lệch tới 11 điểm % ở Gemini.
- [ ] Tỷ lệ nhắc brand chỉ tính trên prompt không mang tên brand. SoV ghi rõ tập brand cố định. Nguồn lỗi: 3 prompt mang tên brand của site agency mẫu kéo tỷ lệ lên nếu tính chung.
- [ ] Domain Gemini lấy từ `title` của link vertexaisearch. Báo cáo không liệt kê URL Gemini trích. Nguồn lỗi: pilot 18/10, 245 link của Gemini đều là link chuyển hướng.
- [ ] Lần đo lại so bằng `compare` (bootstrap ghép cặp), không so số thô. Lịch đo lại tính từ ngày ghi đợt sửa: ngày 14, 30, 60. Không mở đợt sửa mới trên cùng nhóm trang trước ngày 60. Nguồn lỗi: thử A/A 18/10, dùng chênh giữa các lượt làm nhiễu báo sai "tăng/giảm" ở 6/9 ô.
- [ ] AI Overview và AI Mode ghi UNKNOWN hoặc có ảnh chụp tay cùng ngày. Không suy từ số API.
- [ ] Kế hoạch đo ghi chi phí và `--budget` đủ. Nguồn lỗi: mặc định 5 USD của `collect.py` thấp hơn 6,6 USD của bộ 30 prompt × 3 engine × 3 lượt.
- [ ] KPI citation từ Ahrefs dùng cột "Từ prompt", không dùng `all_platforms`. Nguồn lỗi: site agency mẫu 19/10, `all_platforms` giảm 774 → 645 trong khi citation từ prompt tăng 57 → 123.

## Changelog

- v1.6.1 (2026-10-27): bản root thành bản gốc, bản SEO Production sinh bằng `tools/port-dieu-phoi.py`. Lấy từ bản SEO Production: GE-36 ghi "từ v2.0.1" (bản đóng gói ở repo là v2.0.2), câu addon Brand Radar dạng điều kiện. Gộp mục lịch đo lại vào mục `compare` để checklist Tự phản biện còn 8 mục (lệnh kiểm cấu trúc cần 5–8).
- v1.6 (2026-10-19): port cùng nội dung với bản SEO Production 1.6: mục "Số trích dẫn AI từ Ahrefs", lệnh `geo_kpi.py ahrefs`, dòng KPI AI Citations bỏ Brand Radar (tài khoản chưa có addon), Bước 0 thêm `ahrefs?`, 1 mục Tự phản biện. Số liệu: site agency mẫu và 4 đối thủ ngày 19/10/2026.
- v1.5 (2026-10-19): port cùng nội dung với bản SEO Production 1.5: Bước 0 kiểm tool (readiness đổi thành Bước 0b), bảng Phân việc model, bước "Đo mốc và đo lại (ngày 14, 30, 60)" với `scripts/geo_kpi.py` (`kpi`, `compare` bằng bootstrap theo prompt ghép cặp) và `references/do-va-do-lai.md` (bẫy Sonar và Gemini, lịch đo, thử A/A trên mốc site agency mẫu 18/10), mục Tự phản biện. Bản root gọi `collect.py`, `prepare.py` ở `skills/geo-answer-lab/scripts/`. Giữ khác biệt sẵn có của bản root: `audit-contract.md`, `readiness-baseline.md`, evals, `CHANGELOG.md`.
- v1.4 (2026-09-12): đưa readiness/baseline thành workflow executable, schema evidence và cohort so sánh rõ.

Lịch sử đầy đủ: `CHANGELOG.md` (chỉ đọc khi bảo trì).
