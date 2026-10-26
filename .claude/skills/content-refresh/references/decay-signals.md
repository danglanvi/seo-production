# Decay Signals — ngưỡng, cách đo, decision tree

Reference cho skill `content-refresh`. Mọi ngưỡng là **đề xuất thực nghiệm có nguồn** — không phải chuẩn Google công bố. Hiệu chỉnh theo baseline dự án sau 2-3 chu kỳ audit; toàn bộ số gốc đến từ site tiếng Anh, chưa có hiệu chỉnh SERP VN.

## TOC

1. [Bảng tín hiệu T1-T14](#1-bảng-tín-hiệu-t1-t14)
2. [Decision tree — gate chain](#2-decision-tree--gate-chain)
3. [Bảng nguyên nhân → tín hiệu → DEPTH](#3-bảng-nguyên-nhân--tín-hiệu--depth)
4. [Ghi chú Path A — Ahrefs MCP tool map](#4-ghi-chú-path-a--ahrefs-mcp-tool-map)
5. [Ghi chú hiệu chỉnh & open questions](#5-ghi-chú-hiệu-chỉnh--open-questions)

---

## 1. Bảng tín hiệu T1-T14

| # | Signal | Ngưỡng đề xuất | Path A — Ahrefs MCP | Path B — GSC CSV | Path C — câu hỏi triệu chứng | Nguồn ngưỡng |
|---|--------|----------------|----------------------|-------------------|------------------------------|--------------|
| T1 | Cửa sổ detect | 28 ngày vs 28 ngày liền trước | `gsc-page-history` / `gsc-performance-history`, date range 56 ngày, tách 2 cửa sổ | GSC Performance → Date → "Compare last 28 days to previous period", export | "Traffic bắt đầu giảm từ khoảng nào?" | usergrowth.io/academy/content-decay/ |
| T2 | Cửa sổ validate | 90 ngày vs cùng kỳ năm ngoái (YoY) | `gsc-performance-history` 15 tháng (trong biên retention); không GSC access → `site-explorer-pages-history` 24 tháng | 2 export: 90 ngày năm nay + cùng kỳ năm ngoái. ⚠️ GSC giữ ~16 tháng (cần verify docs) | "Cùng kỳ năm ngoái bài này có giảm tương tự không?" | usergrowth.io + ahrefs.com/blog/content-decay/ (3 tháng vs cùng kỳ năm trước) |
| T3 | Decay confirm — clicks | Giảm ≥30% vs baseline 28 ngày, kéo dài **2 tuần liên tiếp** | `gsc-page-history` granularity tuần | Cột Clicks group theo tuần, so baseline 28d | "Mức giảm khoảng bao nhiêu %, kéo dài mấy tuần?" | usergrowth.io |
| T4 | Decay confirm — position | Average position tụt ≥2 trên queries có **≥100 impressions/28 ngày** | `gsc-keyword-history` + `gsc-positions-history` cho top queries của URL | Query-level export, cột Position + Impressions | "Từ khóa chính rớt từ hạng mấy xuống hạng mấy?" | usergrowth.io |
| T5 | Screening rộng | Giảm 20-40% clicks qua 8-12 tuần; flag quý >20% YoY | `site-explorer-top-pages` filter **Declining** + 12 tháng, kết hợp KD<40 (recipe gốc Ahrefs) | So sánh clicks theo quý YoY, flag >20% | "Liệt kê các bài cảm thấy 'đuối dần' trong 2-3 tháng" | usergrowth.io (20-40%/8-12 tuần); ahrefs.com (20% YoY/quý) |
| T6 | KHÔNG phải decay — SERP feature loss | CTR giảm ≥25% nhưng position đổi <0,5; hoặc impressions flat + CTR giảm | `gsc-performance-history` (series CTR + position) + `serp-overview` xem AIO/featured snippet mới | Cột CTR + Position cùng kỳ: CTR rơi, position đứng yên | "SERP của query đó có AI Overview / snippet mới xuất hiện không?" | usergrowth.io + ahrefs.com |
| T7 | Seasonal gate | YoY delta ≈ 0 (cùng kỳ năm ngoái cũng giảm tương đương) → seasonal, không phải decay. Seasonality mạnh → bắt buộc so YoY thay window liền kề | Như T2 | Như T2 | "Ngành có mùa vụ không? Năm ngoái tháng này thế nào?" | usergrowth.io + animalz.co/blog/organic-traffic-decline |
| T8 | Cannibalization | 1 query có ≥2 URLs cùng nhận impressions + position flip-flop qua các tuần (nếu cần số: ≥3 lần swap/8 tuần — **GTV convention**, chưa có nguồn cứng). Benign nếu 2 URL khác intent | `gsc-keywords` filter query → xem pages; `gsc-positions-history` từng URL trên cùng query | GSC Performance → filter Query → tab Pages: nhiều page cùng có impressions; theo dõi position theo tuần | "Có 2 bài cùng nhắm 1 chủ đề/từ khóa không? Thứ hạng có kiểu thay nhau lên xuống?" | seosherpa.com/keyword-cannibalization/ |
| T9 | Min-data gate | KHÔNG kết luận decay từ biến động <4-6 tuần; query <100 impressions/28d không đủ tín hiệu position | Kiểm tra độ dài series trước khi phân tích | Kiểm tra date range export | "Data theo dõi được bao lâu rồi?" | Historical Data.md (6-month lag Koray) + usergrowth.io |
| T10 | Ease filter | KD < 40 = cứu được bằng content; KD cao hơn → authority gap, route `backlink-plan` | `keywords-explorer-overview` cho main query | User cung cấp KD (Ahrefs/tool khác) hoặc bỏ qua kèm ghi chú | Bỏ qua, ghi chú "chưa lọc KD" | ahrefs.com/blog/content-decay/ |
| T11 | Priority score | `Priority = Recovery potential (peak clicks − current clicks, hoặc traffic value) × Ease (KD thấp, structure sound, còn backlinks) × Business relevance` | Peak từ history series; backlinks từ `site-explorer-backlinks-stats` | Peak từ export dài nhất có được | KHÔNG chấm bằng số ở Path C — chỉ xếp hạng định tính | Tổng hợp ahrefs.com (3 trục: business relevance, historical traffic peak, KD) — **công thức là convention đề xuất của skill, không phải industry standard** |
| T12 | Stale-fact trigger | Data/facts trong bài >12 tháng | Đọc content bài (ngày số liệu, năm trong text) | Như Path A | "Bài cập nhật số liệu lần cuối khi nào?" | Content Production/10-update-pipeline/CLAUDE.md (trigger table sẵn có) |
| T13 | Re-measure sau update | Sớm nhất 7-30 ngày (GSC impressions); validate 90 ngày; full HD effect 6 tháng | `gsc-page-history` sau ngày re-publish | Export sau mốc 30/90 ngày | Hẹn lịch check thủ công | sop/05-audit-checklist.md + usergrowth.io + Historical Data.md |
| T14 | AI freshness benchmark | Top cited pages: 76,4% update trong 30 ngày; AI-cited fresher hơn organic SERP 25,7%; median cited age 500 ngày | `brand-radar-*` / `site-explorer-ai-responses-count` (nếu có); GSC AI report chỉ có impressions | GSC Search Generative AI report export | "Bài có xuất hiện trong ChatGPT/AIO khi hỏi topic này không?" (aggregate, không prompt đơn lẻ) | 76,4% + median 500 ngày: GEO.md; 25,7%: ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/ (study 17M citations, riêng — không phải bài content-decay) |

**Cách đọc impressions + CTR cùng nhau (Ahrefs methodology):**
- Cả impressions + CTR cùng giảm → decay cổ điển.
- Impressions giảm + CTR tăng → mất position nhưng user còn engage → **recoverable, ưu tiên cao**.
- Impressions flat + CTR giảm → SERP feature problem (T6), **KHÔNG phải decay**.

---

## 2. Decision tree — gate chain

Thứ tự gate **cố định**, mỗi candidate đi từ trên xuống, dừng ở gate đầu tiên chặn:

```
Candidate (qua screening T5)
│
├─ Gate 0 — MIN-DATA (T9)
│    Data <4-6 tuần? Queries <100 imp/28d?
│    → CÓ: DỪNG — "chưa đủ data", hẹn re-check, KHÔNG kết luận decay
│
├─ Gate 1 — SELF-INFLICTED
│    Có content change / migration trong ~8 tuần TRƯỚC khi giảm?
│    Traffic giảm NGAY SAU một lần sửa?
│    → CÓ: route RESTORE (khôi phục bản trước) — không refresh
│    (ahrefs.com — Content Changes pattern)
│
├─ Gate 2 — SEASONAL (T7) 🔴 bắt buộc trước khi rank
│    YoY delta ≈ 0 (năm ngoái cùng kỳ cũng giảm tương đương)?
│    → CÓ: SEASONAL — ghi nhận, loại khỏi queue
│    Site <13 tháng → skip gate nhưng ghi rõ "chưa loại trừ seasonality"
│
├─ Gate 3 — SERP FEATURE (T6)
│    CTR giảm ≥25% & position đổi <0,5? Impressions flat + CTR giảm?
│    → CÓ: SERP-FEATURE-LOSS — ghi nhận, KHÔNG tạo UPDATE BRIEF
│    (AIO/snippet chiếm click — không phải lỗi content)
│
├─ Gate 4 — CANNIBALIZATION (T8)
│    ≥2 URL swap position trên cùng query?
│    → CÓ + cùng intent: route CONSOLIDATE (1 đề xuất cho cả cặp, absorb + 301 vào URL mạnh hơn)
│    → CÓ + khác intent: benign — quay lại chain với từng URL riêng
│
└─ Gate 5 — DECAY CONFIRM (T3/T4)
     Clicks −≥30% vs baseline 28d, 2 tuần liên tiếp?
     HOẶC position tụt ≥2 trên queries ≥100 imp/28d?
     → CÓ: DECAY THẬT → phân loại nguyên nhân (mục 3) → UPDATE BRIEF
     → KHÔNG: theo dõi tiếp (watchlist), chưa vào queue
```

Cũng cần nhớ: tách "tracking errors" (Animalz — 5 loại decline: decay / SERP shifts / cannibalization / seasonality / tracking errors) — nếu số liệu bất thường kiểu rơi thẳng đứng về 0, kiểm tra tag/GA/GSC property trước khi chạy chain.

---

## 3. Bảng nguyên nhân → tín hiệu → DEPTH

Chỉ áp cho candidate đã qua Gate 5 (decay thật), trừ 3 dòng cuối là output của gate chain:

| Nguyên nhân | Tín hiệu chẩn đoán | DEPTH gợi ý cho pipeline | Nguồn |
|---|---|---|---|
| **Stale facts** | Traffic giảm dần KHÔNG có content change trước đó + bài >12 tháng không sửa (T12) | **light** | ahrefs.com (Content Changes pattern) + pipeline trigger table |
| **Competitor vượt** | Position trượt từ từ, content mình không đổi, impressions giảm theo position. Nguyên nhân phổ biến nhất và khó nhận ra nhất (displacement diễn ra từ từ). Xác nhận bằng diff vs SERP top 5 — bước 1 của pipeline, skill này chỉ flag | **medium** | ahrefs.com ("most common cause") |
| **Thiếu entity-attribute mới** | Impressions tăng cho query mới liên quan nhưng page không rank cho chúng; gap topical coverage | **medium** | Nội suy từ Koray framework (Topical Coverage) — **GTV convention** |
| **SERP intent shift** | SERP similarity thấp, nhiều Lost/New rankings trong SERP overview; format thống trị đổi (guide → forum/UGC) | **heavy** (thường cần re-outline, không phải refresh nhẹ) | ahrefs.com |
| **Cannibalization** | T8 — gate 4 | — (route CONSOLIDATE, KHÔNG vào update pipeline như refresh thường) | ahrefs.com decision framework + seosherpa.com |
| **Self-inflicted** | Giảm ngay sau 1 lần sửa — gate 1 | — (route RESTORE) | ahrefs.com (Content Changes) |
| **SERP feature loss** | T6 — gate 3 | — (ghi nhận, không UPDATE BRIEF) | ahrefs.com + usergrowth.io |

**Route flags đầy đủ** (decision framework Ahrefs): keyword còn relevant + content outdated → **UPDATE**; 2 pages cùng keyword → **CONSOLIDATE** (absorb + 301 vào page mạnh hơn); keyword hết fit strategy + có backlinks → **REDIRECT**; low-value + ít traffic + ít backlinks → **PRUNE**; tối ưu sai từ đầu + topic còn cạnh tranh → **REWRITE**; KD cao (T10) → **AUTHORITY-GAP**; self-inflicted → **RESTORE**.

---

## 4. Ghi chú Path A — Ahrefs MCP tool map

| Việc | Tool | Ghi chú params |
|---|---|---|
| Danh sách pages + metrics GSC | `gsc-pages` | Filter theo `$SCOPE`; sort theo clicks giảm dần |
| Series clicks/imp/CTR/position 1 URL | `gsc-page-history` | Date range 56 ngày (T1) hoặc 15 tháng (T2) |
| Series site-level | `gsc-performance-history` | Dùng cho baseline site (loại trừ site-wide drop vs page-level decay) |
| Query của URL + history | `gsc-keyword-history`, `gsc-positions-history` | Chỉ queries ≥100 imp/28d (T4/T9) |
| Fallback không có GSC access | `site-explorer-pages-history`, `site-explorer-keywords-history`, `site-explorer-top-pages` (filter Declining) | Ahrefs estimate — độ nhạy thấp hơn GSC, ghi rõ trong report |
| Intent-shift check | `serp-overview` | So Lost/New + format thống trị; KHÔNG diff nội dung chi tiết (việc của pipeline) |
| KD cho ease filter | `keywords-explorer-overview` | T10: KD<40 |
| Backlinks cho ease | `site-explorer-backlinks-stats` | Thành phần Ease trong T11 |
| AI visibility (lớp riêng) | `brand-radar-*`, `site-explorer-ai-responses-count` | Aggregate only; report tách riêng |

🔴 Trước khi gọi: báo tổng số call dự kiến ở Bước 0b và chờ user xác nhận. Gọi `doc` cho tool lần đầu dùng.

---

## 5. Ghi chú hiệu chỉnh & open questions

- **Baseline VN:** toàn bộ ngưỡng đến từ site tiếng Anh — thu thập số hiệu chỉnh sau 2-3 quý chạy trên project GTV thật.
- **GSC 16-month retention:** cần verify chính thức tại Google Search Console docs trước khi dựa cứng vào YoY ở Path B.
- **Ngưỡng swap cannibalization bằng số** (≥3 lần/8 tuần): GTV convention — SEO Sherpa chỉ mô tả pattern định tính.
- **Traffic value trong T11:** clicks thô hay clicks × CPC-equivalent (Ahrefs traffic value)? — chờ Vincent chốt convention.
- **Update Score decay curve** (update cũ có mất effect theo thời gian?): Open Question sẵn trong [[Update Score]] — ảnh hưởng tần suất refresh tối ưu.
- **Ngưỡng engagement polarity** (CTR<1% position 1-10, bounce>80%): proposed của Vincent trong [[Historical Data]], chưa validate.
