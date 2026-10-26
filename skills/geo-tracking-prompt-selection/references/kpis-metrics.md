# GEO KPIs & Metrics Tracking

## Core KPIs to Commit

| KPI | Description | Target | Tracking Frequency |
|-----|-------------|--------|-------------------|
| **Brand Mention** | Times brand appears in AI responses — **ChatGPT + Google AI (AI Mode/Gemini/AIO) là kênh bắt buộc**, Perplexity/Copilot/Claude bổ sung (29/08/2026) | >60% BOFU prompts trên cả 2 kênh bắt buộc | Weekly-2 weeks nội bộ (polling ≥3 lần/prompt — GE-33) |
| **AI Citations** | Citation từ prompt theo Ahrefs `site-explorer-ai-responses-count` (lệnh `geo_kpi.py ahrefs`, không dùng `all_platforms`) · GSC Generative AI (Beta) impressions | Increasing trend (directional) | Weekly |
| **Share of Voice** | % mention vs competitors — theo topic, tách engine | >30% SOV | Monthly |
| **Information Accuracy** | AI describes brand correctly | >90% accurate | Monthly |
| **AI Referral + AI CVR vs Organic CVR** | Sessions + conversion rate kênh GA4 "AI Assistant" so với Organic Search (mục § GA4 bên dưới) | Directional — không nghiệm thu | Monthly |

## Detailed Metrics

### 1. Brand Mention Metrics

**What to track:**
- Mention count per prompt
- Mention count trend over time
- Mention by AI platform — thứ tự ưu tiên: **ChatGPT · Google AI Mode · Gemini app · AI Overviews** (bắt buộc) → Perplexity · Copilot · Claude (bổ sung). Đo Google AI **tách 3 bề mặt** (AIO ≠ AI Mode: 13,7% trùng citation)

**How to measure:**
```
Mention Rate = (Prompts with brand mention / Total prompts) × 100

Target by funnel:
- BOFU: >60%
- MOFU: >40%
- TOFU: >20%
```

### 2. AI Citations

**What to track:**
- Number of AI citations in Semrush/Ahrefs
- Citation sources (which pages get cited)
- Citation growth rate

**How to measure:**
- Semrush: Position Tracking → AI Overviews
- Ahrefs: Site Explorer → AI Citations (if available)
- Manual: Run prompts, note source citations

**⚠️ Reliability caveats (added 08/2026 — refresh theo lint quý):**
- Citation counts are **directional and lagging**, not real-time human visibility: a 404'd + deindexed page still received daily citations for ~8 weeks (@top5seo 07/2026, n=1, author-labeled "half-baked" — methodological warning only). Suspect any standalone "citations up/steady" chart.
- **Date-stamp every number**: ChatGPT search format changed 3x since 06/2026; `search_queries` field gone 16-20/08/2026 → fan-out numbers pre/post 08/2026 are not comparable, and tools reading that field return empty/wrong until patched for the pipe format (`fast|query|freshness_window|domain`).
- Asking an LLM whether a tactic works is **not** measurement (convergence problem — cats.txt, Williams-Cook 08/2026). Reject the 4 fake proofs as evidence: crawled / indexed / RAG-repeated / LLM-endorsed.
- `genui_run` widget queries (stocks, sports, maps) have no citations to win — exclude from citation opportunity counts.

### 3. Share of Voice (SOV)

**What to track:**
- Brand mentions vs competitor mentions
- SOV by category/topic
- SOV trend over time

**How to measure:**
```
SOV = (Brand mentions / Total mentions including competitors) × 100

Example:
- Your brand: 15 mentions
- Competitor A: 12 mentions
- Competitor B: 8 mentions
- Competitor C: 5 mentions
- Total: 40 mentions
- Your SOV: 15/40 = 37.5%
```

### 4. Information Accuracy

**What to track:**
- Correct product/service descriptions
- Correct pricing (for e-commerce)
- Correct contact/location info
- Absence of negative misinformation

**How to measure:**
```
Accuracy Rate = (Accurate responses / Total responses with brand info) × 100

Check for:
✓ Product names correct
✓ Service descriptions accurate
✓ Pricing current (±5%)
✓ No false claims
✓ No competitor confusion
```

## Secondary Metrics

### Context Type Distribution

Track HOW brand is mentioned:

| Context Type | Description | Value |
|--------------|-------------|-------|
| **Recommendation** | AI recommends brand | High |
| **Comparison** | Brand in comparison list | Medium |
| **Information** | Neutral mention | Low |
| **Negative** | Critical mention | Alert |

**Target distribution:**
- Recommendation: >50%
- Comparison: 30-40%
- Information: <20%
- Negative: <5%

### Position in Response

When brand appears in lists:

| Position | Impact |
|----------|--------|
| #1-3 | High visibility |
| #4-7 | Medium visibility |
| #8+ | Low visibility |

**Target:** Top 3 position in >60% of list responses

### Competitor Tracking

Track same metrics for 5-7 competitors:
- Mention frequency
- Position
- Context type
- Accuracy

**Benchmark:** Your brand should outperform average competitor metrics

## Tracking Schedule

### Daily
- [ ] Run top 20 BOFU prompts
- [ ] Log mention counts
- [ ] Note any alerts (negative mentions, inaccuracies)

### Weekly
- [ ] Run full prompt list (all categories)
- [ ] Update mention rate trends
- [ ] Check competitor changes
- [ ] Identify content → citation wins

### Monthly
- [ ] Calculate Share of Voice
- [ ] Audit information accuracy
- [ ] Review context type distribution
- [ ] Generate monthly report
- [ ] Update/replace underperforming prompts

## Tools for Tracking

### Recommended Platforms

| Tool | Use Case | Key Features |
|------|----------|--------------|
| **Promptmonitor** | Comprehensive GEO | 250+ prompts, multi-model, competitor benchmarking |
| **SE Ranking** | AI visibility | Multi-platform, sentiment analysis |
| **AIClicks.io** | Cross-platform | Brand vs competitor, source identification |
| **Semrush** | AI citations | Position tracking with AI Overviews |
| **Microsoft Clarity AI Citations** | Grounding-query visibility (free) | Branded vs non-branded grounding queries + Share of Authority by query type (official feature 03/08/2026). Caveats: branded-classification methodology unpublished; coverage leans Bing/Copilot ecosystem — verify before client commitments |
| **Ahrefs — AI responses + Brand Radar** (GTV có MCP) | Citation + mention count per engine (AIO / ChatGPT / AI Mode / Gemini / Perplexity / Copilot) | `site-explorer-ai-responses-count` (số AI responses cite site — nguồn đo AIO hợp lệ theo HĐ GTV), nhóm `brand-radar-*` (mentions overview/history, cited pages, SoV; cần addon Brand Radar, kiểm 19/10/2026 tài khoản chưa có). `all_platforms` cộng cả AIO theo từ khoá SERP (`google_ai_overviews_keywords`), nên KPI lấy tổng các nền tảng chạy prompt. ⚠ Tách **cited** (hiện link) vs **found** (retrieve không link) — 2 metric riêng; mọi số kèm ngày query + nhãn directional. Map tool → ô báo cáo: `gtv-client-report/references/data-paths.md` §1 |
| **GSC → Performance → Generative AI features (Beta)** | Impressions/clicks từ AIO + AI Mode (official, free) | Bề mặt có nhưng không join được với query/click của performance report; số nhiễm bot của các tool tracking → dùng như trend directional, kèm workflow GSQi bên dưới |
| **GA4 — channel group "AI Assistant"** | Traffic + conversion thực từ AI (official, free) | Setup ở mục § GA4 bên dưới — đây là **nguồn đối chiếu bắt buộc** trước khi tuyên bố thắng GEO (GE-35) |

### GA4 — channel "AI Assistant" setup + AI CVR vs Organic CVR (mới 29/08/2026)

**Vì sao:** citation/mention là số **lagging + nhiễm bot**; referral thật + chuyển đổi thật trong GA4 là bằng chứng duy nhất khách tin. Case first-party GTV (08/2026, enterprise VN, ẩn danh, n=1, nhãn D): mở robots cho AI bot → pageview kênh AI Assistant 84.764 → 179.177 (+111%/tháng), CR từ AI ≈10× organic.

**Cách setup (Admin → Data display → Channel groups → tạo custom group hoặc thêm channel vào bản copy của Default):**

| Channel | Điều kiện (Session source matches regex) | Ghi chú |
|---|---|---|
| **AI Assistant** | `chatgpt\.com\|chat\.openai\.com\|gemini\.google\.com\|bard\.google\.com\|perplexity\.ai\|copilot\.microsoft\.com\|bing\.com/chat\|claude\.ai\|you\.com\|meta\.ai\|grok\.com\|x\.ai` | Đặt **trên** Referral trong thứ tự ưu tiên channel; thêm domain khi thấy referrer mới trong báo cáo Traffic acquisition |
| AI Assistant — Google AI Mode | không tách được bằng referrer (AI Mode/AIO click về dạng `google` organic) | Dùng GSC Generative AI (Beta) làm proxy impressions; không cộng vào channel AI Assistant |

**Đọc số (Reports → Acquisition → Traffic acquisition, dimension = Session channel group):** Sessions · Engaged sessions · Key events · **Session key event rate** → so sánh hàng "AI Assistant" với "Organic Search" cùng kỳ. Xuất 2 số: `AI CVR / Organic CVR` (bội số) + AI sessions share (%). Kỳ so sánh ≥28 ngày; mẫu <100 session/tháng → chỉ ghi "chưa đủ mẫu".

**Benchmark tham chiếu (đặt kỳ vọng, KHÔNG cam kết — mẫu người khác):** Ahrefs tự đo 23× (0,5% traffic → 12,1% signups, 06/2025, F) · Seer Interactive: ChatGPT 15,9% · Perplexity 10,5% · Claude 5% · Gemini 3% vs Google organic 1,76% (B) · Semrush: LLM visitor 4,4× (C) · GTV first-party ≈10× (D). AI visitor ở lại lâu hơn (Claude 18,6' · ChatGPT 9,7' vs Google 4,3' — SE Ranking 2026, B). Số AI referral tổng chỉ ~0,3% traffic (SE Ranking) → giá trị nằm ở CR, không ở volume.

**Luật report:** hàng "Conversion từ AI Assistant" là mục chuẩn trong báo cáo tháng (`gtv-client-report` v1.3), nhãn directional, không phải KPI nghiệm thu; attribution gãy (user discover ở ChatGPT, quay lại qua Google/direct) → đọc cùng branded search trend.

### GSC workflow: surfacing AI Mode queries (GSQi, 08/2026)

GSC's 2 reports cannot be joined: performance report has clicks but no AIO/AI Mode surface breakout; Generative AI report has surface but no clicks. Workaround (Glenn Gabe/GSQi, practitioner ops guide — fragile to GSC changes, refresh theo lint quý):

1. Bulk export query + page via **Search Analytics API** (beats the 1,000-row UI limit).
2. Feed the spreadsheet to an LLM to classify **AI Mode candidates** (signals: ultra-short follow-ups "yes/tell me more", context-less danglers, long conversational prompts) + reasoning + cited URL.
3. Treat results as candidates, not ground truth — Google doesn't label surface.

⚠️ GSC query data is itself polluted by **automated queries from AI-visibility tracking companies** — your own GSC AI impressions include the tracking industry's bots.

### DIY Tracking (Google Sheets)

**Tab 1: Prompt List**
| Prompt ID | Category | Intent | Prompt VN | Prompt EN |

**Tab 2: Tracking (weekly-2 weeks, ≥3 lần chạy/prompt/engine — ghi tỷ lệ)**
| Date | Prompt ID | ChatGPT (bắt buộc) | Google AI Mode (bắt buộc) | Gemini app (bắt buộc) | AIO (theo keyword) | Perplexity | Copilot | Claude | Model version / format era | Notes |

**Tab 3: Monthly Summary**
| Month | Mention Rate | SOV | Accuracy | Top Performer | Underperformer |

## Reporting Template

### Monthly GEO Report Structure

```
1. Executive Summary
   - Overall mention rate: X%
   - SOV: X% (vs X% last month)
   - Key wins this month

2. Metrics Dashboard
   - Brand Mention: X% (target: 60%)
   - AI Citations: X (trend: ↑/↓)
   - Share of Voice: X%
   - Accuracy: X%

3. By Funnel Stage
   - BOFU: X% mention rate
   - MOFU: X% mention rate
   - TOFU: X% mention rate

4. Competitor Analysis
   - Brand vs Competitor A: X% vs Y%
   - Brand vs Competitor B: X% vs Y%

5. Top Performing Prompts
   - Prompt 1: X% mention rate
   - Prompt 2: X% mention rate

6. Underperforming Prompts (to replace)
   - Prompt X: 0% mention rate
   - Prompt Y: 10% mention rate

7. Recommendations
   - Content optimization needed for [topic]
   - New prompts to add: [list]
   - Prompts to retire: [list]

8. Next Month Focus
   - Priority actions
   - Seasonal considerations
```

## Alert Thresholds

Set up alerts for:

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Mention rate drop | >20% decrease week-over-week | Investigate immediately |
| Negative mention | Any negative context | Review and address |
| Inaccurate info | Critical misinformation | Urgent content update |
| Competitor surge | Competitor SOV >50% | Competitive analysis |
| New competitor | New brand appearing frequently | Add to tracking |
