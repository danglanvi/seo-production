---
name: serp-clustering
description: "Gom nhóm keyword bằng SERP-overlap — DATA/METHOD layer dùng chung của bộ skill keyword/topical: top-10 URL per keyword → ma trận overlap → phân cụm theo ngưỡng → verdict gộp/tách kèm evidence. Use when: 'gom cụm keyword [bộ X]', 'keyword này chung URL không', 'clustering cho topical map'."
metadata:
  version: "1.0"
---

# SERP Clustering — Data/Method Layer

Gom nhóm keyword bằng **SERP-overlap**: nếu 2 keyword trả về phần lớn cùng một bộ URL top-10, Google đang nói "đây là cùng một intent → một URL phục vụ được cả hai". Skill này CHỈ sản xuất **bảng cụm + evidence** — mọi quyết định downstream (URL nào, page type gì, Core hay Outer, gộp bài hay tách bài) thuộc về consumer skills.

🔴 Nguyên tắc lớp: đây là **DATA/METHOD layer** (cùng vai với `backlink-research` trong bộ backlink). Output là input cho DECISION layer — không thay thế nó.

## Phân vai (consumer map — không lấn sân)

| Consumer | Dùng output này để | Ranh giới |
|---|---|---|
| `keyword-topic-url-mapping` | Công đoạn (4) T1 — nhận bảng cụm → quyết định URL SEO / intent I-N-C-T / Core-Outer / page type / % phân bổ | DECISION layer chính thức của bộ keyword cam kết; serp-clustering không đề xuất URL |
| `topical-map-creation` | Bước grouping/cluster queries (Step 10) — verify cụm bằng SERP evidence trước khi chốt node của map/SCN | Map ownership (SCN, QDP/QDH/QDS, Core:Outer ratio) thuộc topical-map-creation |
| `content-refresh` | Cannibalization check — 2 bài đang rớt vì cùng cụm SERP? Re-rank T5: cụm nào Google đã merge SERP | Chẩn đoán decay + UPDATE BRIEF thuộc content-refresh; skill này chỉ trả evidence cụm |
| `seo-research` | Research 1 bài — xác nhận keyword phụ nào chung SERP với target query để gom vào 1 brief | Phân tích content đối thủ / Layer A-B thuộc seo-research |

## Input

**Required:**
- `$KEYWORDS` — danh sách keyword: CSV, paste trực tiếp, hoặc đọc từ `00-client-context/kpi-commitments.md` của instance SEO Production. Kèm volume nếu có (dùng đặt tên cụm + gate evidence).

**Optional:**
- `$LOCATION` / `$LANGUAGE` — mặc định **Vietnam / vi**. Khai báo trong output (SERP khác nhau per market).
- `$OVERLAP_THRESHOLD` — ngưỡng gộp cụm, mặc định **≥4/10**. Điều chỉnh được (niche SERP đồng nhất cao → nâng 5-6; consumer topical-map-creation Step 10 truyền thống dùng 3): mọi điều chỉnh **khai báo trong output**.
- `$VOLUME_GATE` — mức volume mà cụm chứa keyword ≥ mức này bắt buộc có evidence Tier ≤3 (mặc định: top 20% volume của bộ, hoặc user chốt số tuyệt đối).

**Data ladder (khai báo DATA TIER + % keyword verified trong output):**

| Tier | Nguồn | Ghi chú |
|---|---|---|
| Tier 1 | Ahrefs MCP `serp-overview` per keyword (top-10 organic URLs) | Ưu tiên. 🔴 Chi phí: **số call = số keyword** — báo trước, chờ xác nhận |
| Tier 2 | DataForSEO SERP API | Khi Ahrefs không khả dụng; cùng logic cost per keyword |
| Tier 3 | Search tay mẫu đại diện | Chọn n keyword volume lớn nhất + cụm nghi ngờ (borderline/chain-merge) → search thủ công, ghi top-10 vào bảng; phần còn lại rơi xuống Tier 4 |
| Tier 4 | Semantic/intent grouping thủ công | Fallback cuối — cluster bằng phân tích intent + lexical, **mọi cụm label `⚠️ chưa verify SERP`**; đề xuất verify lại khi có data |

🔴 **Cost gate:** danh sách >200 keyword → cảnh báo trước khi chạy Tier 1-2 (200+ call), đề xuất phương án lai: Tier 1-2 cho top volume + Tier 3 mẫu đại diện + Tier 4 phần đuôi.

## Workflow

### Bước 0 — Scope & cost gate

1. Xác nhận bộ keyword (nguồn, số lượng, có volume không) + `$LOCATION`/`$LANGUAGE` + ngưỡng.
2. Chốt DATA TIER khả dụng; Tier 1-2 → báo số call (= số keyword), chờ user xác nhận; >200 keyword → đề xuất phương án lai (cost gate ở trên).
3. Hỏi mục đích consumer (mapping / topical map / cannibalization / research) — không đổi method, chỉ để ghi chú bàn giao đúng skill.

### Bước 1 — Chuẩn hóa bộ keyword

1. Dedupe, gom biến thể chính tả/dấu hiển nhiên (chỉ biến thể chắc chắn cùng query — nghi ngờ thì để SERP quyết).
2. Gắn volume per keyword nếu có (thiếu → ghi trống, ảnh hưởng cách đặt tên cụm và `$VOLUME_GATE`).

### Bước 2 — Lấy SERP top-10 per keyword

1. Theo tier đã chốt: per keyword lấy **top-10 organic URLs** (bỏ ads, bỏ SERP features không phải organic link).
2. Ghi **ngày chụp SERP** per batch — kết quả clustering có tuổi thọ (xem Behavior Gates #3).
3. Keyword không lấy được SERP (tier fail cục bộ) → đánh dấu, xử lý ở Tier thấp hơn.

### Bước 3 — Ma trận overlap & phân cụm theo ngưỡng

1. Per cặp keyword: đếm số URL trùng giữa 2 bộ top-10 (normalize URL: bỏ trailing slash, utm, http/https — cùng canonical = trùng).
2. Áp ngưỡng:
   - **≥ `$OVERLAP_THRESHOLD` (mặc định 4/10) URL chung → cùng cụm** (verdict GỘP — 1 URL phục vụ cả cụm).
   - **2-3/10 → BORDERLINE** — không tự verdict: bắt buộc review tay (nhìn 2 SERP thật: page type đang rank, intent signals), ghi lý do gộp/tách vào output.
   - **≤1/10 → TÁCH** (verdict TÁCH — URL riêng).
3. Keyword không match cụm nào → cụm đơn (singleton).

### Bước 4 — Transitive merge có kiểm soát + đặt tên cụm

1. Merge bắc cầu: A~B và B~C → xét gộp A,B,C. 🔴 Nhưng kiểm tra **cặp xa nhất**: nếu A≁C (overlap dưới ngưỡng) → **flag `chain-merge`, KHÔNG auto gộp** — trình cả 2 phương án (gộp 3 / tách A | B,C hoặc A,B | C) cho review tay.
2. Đặt tên cụm = **keyword volume cao nhất** trong cụm (fallback khi không có volume: keyword ngắn nhất).
3. Ghi overlap evidence per cụm: **min-max số URL chung** giữa các cặp trong cụm (vd "4-7/10").

### Bước 5 — Render output & bàn giao

1. Render bảng theo skeleton Output, kèm header khai báo: DATA TIER, % keyword verified SERP, ngưỡng, location/language, ngày chụp SERP.
2. Bàn giao đúng consumer: chạy trong pipeline client → lưu cạnh deliverable của consumer skill (vd `05-content-plan/` của instance); standalone → trả trong chat.
3. Nhắc rõ: bảng này CHƯA phải quyết định URL/page type — bước kế tiếp thuộc consumer skill.

## Output

```markdown
# SERP Clustering — <bộ keyword / client> · YYYY-MM-DD
> DATA TIER: <1/2/3/4 — nguồn> · Verified SERP: <n/N keyword = %> · Ngày chụp SERP: <date>
> Location/Language: <VN/vi> · Overlap threshold: <4/10 mặc định | điều chỉnh + lý do>
> Consumer dự kiến: <keyword-topic-url-mapping / topical-map-creation / content-refresh / seo-research>

## 1. Bảng cụm
| # | Cụm (keyword đại diện) | Members (kw · vol) | Volume tổng | Overlap evidence (min-max URL chung) | Verdict | Tier |
|---|---|---|---|---|---|---|
| 1 | | | | vd 4-7/10 | GỘP / TÁCH / BORDERLINE-reviewed(lý do) | 1-4 |

## 2. Borderline & chain-merge log
- <cặp/cụm 2-3/10 hoặc flag chain-merge — quan sát SERP thật + lý do gộp/tách sau review tay>

## 3. Keyword chưa verify
- <keyword Tier 4 `⚠️ chưa verify SERP` — đề xuất verify khi có data>

## 4. Ghi chú bàn giao
- Skill này KHÔNG quyết định page type / intent / URL / Core-Outer — việc của consumer skill.
- Re-verify: kết quả quá 90 ngày → chạy lại cụm quan trọng trước khi dùng cho quyết định mới.
```

## Behavior Gates

**#1 Think Before** — Trước khi gọi API: báo số call = số keyword, chờ xác nhận; >200 keyword → bắt buộc trình phương án lai trước. Xác nhận location/language — SERP VN ≠ SERP US.

**#2 Evidence** — 🔴 Không kết luận GỘP/TÁCH cho cụm chứa keyword ≥ `$VOLUME_GATE` khi chưa có evidence Tier ≤3 (Tier 4 chỉ được ra cụm tạm kèm label `⚠️ chưa verify SERP`). Mọi verdict GỘP ghi số overlap thực (vd "6/10"); borderline 2-3/10 **bắt buộc review tay** — không auto verdict theo máy. Output khai báo tier + % keyword verified.

**#3 SERP có tuổi thọ** — SERP biến động theo update: mọi kết quả kèm **ngày chụp**; quá **90 ngày** → cụm quan trọng (volume cao / đang là căn cứ quyết định URL) phải re-verify trước khi tái sử dụng.

**#4 Surgical** — Chỉ cluster + evidence. Không đề xuất URL, không phân loại intent/Core-Outer, không viết brief, không audit content. Consumer hỏi gì ngoài bảng cụm → route đúng skill theo bảng Phân vai.

## Anti-patterns

- ❌ Auto gộp chain-merge (A~B, B~C → gộp luôn A,C) khi cặp xa nhất dưới ngưỡng — phải flag + review tay.
- ❌ Auto verdict cụm borderline 2-3/10 — vùng này máy không đủ, bắt buộc mắt người nhìn 2 SERP.
- ❌ Cluster chỉ bằng lexical similarity (chung chữ) rồi trình như SERP-verified — Tier 4 phải mang label `⚠️ chưa verify SERP` ([[syntheses/Lexical-vs-Intent Rule]]).
- ❌ Quyết định page type / intent / URL trong output — lấn sân DECISION layer (`keyword-topic-url-mapping`).
- ❌ Chạy 500 call MCP không báo trước — cost gate ở Bước 0 là bắt buộc.
- ❌ Trộn SERP khác location/language trong cùng ma trận (kw chụp SERP VN so với kw chụp SERP US).
- ❌ Tái sử dụng bảng cụm >90 ngày cho quyết định mới mà không re-verify cụm quan trọng.
- ❌ Đếm overlap không normalize URL (http vs https, trailing slash, utm) — đếm hụt overlap thật.

## References & wiki

**Skill consumer (DECISION/EXECUTION layer):** `keyword-topic-url-mapping` (công đoạn 4 T1 — consumer chính) · `topical-map-creation` (Step 10 grouping) · `content-refresh` (cannibalization) · `seo-research` (research 1 bài)

**Pattern lớp:** bộ backlink `backlink-research` (DATA) → `backlink-plan` (DECISION) — serp-clustering giữ đúng vai DATA trong bộ keyword/topical.

**Wiki Semantic SEO (lớp WHY):** [[Central Search Intent]] · [[User Intent]] · [[Mixed Intent]] · [[Query Network]] · [[Canonical Query]] · [[syntheses/Lexical-vs-Intent Rule]]

**Nguồn quy trình:** `sop/09-project-timeline/10-thang-thuc-day.md` (công đoạn 4 T1 — nơi method này phục vụ đầu tiên) · `sop/01-topical-map.md` (Central Search Intent).

## Changelog

- **2026-07-19 v1.0** — tạo mới, tách từ `keyword-topic-url-mapping` theo quyết định Vincent: SERP-overlap clustering thành DATA/METHOD layer dùng chung (4 consumer: keyword-topic-url-mapping, topical-map-creation, content-refresh, seo-research); ngưỡng ≥4/10 gộp · 2-3/10 borderline review tay · ≤1/10 tách; chain-merge có kiểm soát; data ladder 4 tier (Ahrefs serp-overview → DataForSEO → search tay mẫu → semantic fallback ⚠️); gate SERP 90 ngày + cost gate >200 keyword.
