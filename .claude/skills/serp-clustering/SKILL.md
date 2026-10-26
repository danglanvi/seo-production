---
name: serp-clustering
description: "Gom keyword thành cụm bằng SERP overlap top 10, lọc trước bằng EmbeddingGemma để chỉ kéo SERP cho cặp giáp ranh, ra bảng cụm có evidence cho skill quyết định URL. Dùng khi gom cụm keyword [bộ X], hỏi keyword này chung URL không, clustering cho topical map."
metadata:
  version: "1.1.1"
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
- `$OVERLAP_THRESHOLD` — ngưỡng xếp keyword vào cùng cụm khi lập plan, mặc định **≥4/10**. Ngưỡng này không dùng để gộp 2 URL đang có: gộp URL cần ≥6/10. Điều chỉnh được (niche SERP đồng nhất cao → nâng 5-6; consumer topical-map-creation Step 10 truyền thống dùng 3): mọi điều chỉnh **khai báo trong output**.
- `$VOLUME_GATE` — mức volume mà cụm chứa keyword ≥ mức này bắt buộc có evidence Tier ≤3 (mặc định: top 20% volume của bộ, hoặc user chốt số tuyệt đối).

**Data ladder (khai báo DATA TIER + % keyword verified trong output):**

| Tier | Nguồn | Ghi chú |
|---|---|---|
| Tier 1 | Ahrefs MCP `serp-overview` per keyword (top-10 organic URLs) | Ưu tiên. 🔴 Chi phí: **số call = số keyword** — báo trước, chờ xác nhận |
| Tier 2 | DataForSEO SERP API | Khi Ahrefs không khả dụng; cùng logic cost per keyword |
| Tier 3 | Search tay mẫu đại diện | Chọn n keyword volume lớn nhất + cụm nghi ngờ (borderline/chain-merge) → search thủ công, ghi top-10 vào bảng; phần còn lại rơi xuống Tier 4 |
| Tier 4 | Semantic/intent grouping thủ công | Fallback cuối — cluster bằng phân tích intent + lexical, **mọi cụm label `⚠️ chưa verify SERP`**; đề xuất verify lại khi có data |

🔴 **Cost gate:** danh sách >200 keyword → cảnh báo trước khi chạy Tier 1-2 (200+ call), đề xuất phương án lai: Tier 1-2 cho top volume + Tier 3 mẫu đại diện + Tier 4 phần đuôi.

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| EmbeddingGemma 2 | Cosine giữa keyword để tách trước cặp chắc khác cụm | dùng: cos < 0,90 (`SentenceSimilarity`) đúng 186/186 cặp holdout, tiết kiệm 5/23 lượt kéo SERP (`references/gemma-truoc.md`). Không ra verdict GỘP: không có ngưỡng "chắc cùng cụm" đạt precision 0,95 |
| Code (`cluster.py`) | Đếm overlap SERP, phân loại cặp, đo lại | dùng: việc đếm phải tất định |
| Jev | Chấm intent của cặp BORDERLINE | không dùng: cặp BORDERLINE cần mắt người nhìn 2 SERP thật (Behavior Gate #2). Chưa có rubric hiệu chuẩn |
| GLM Flash | Trích câu | không dùng: skill không trích câu |
| Claude | Review tay cặp BORDERLINE và chain-merge, đặt tên cụm, viết ghi chú bàn giao | dùng |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,gemma?,dataforseo?,ahrefs?,firecrawl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `gemma`: bỏ Bước 1b, kéo SERP cho mọi keyword.

### Bước 0b — Scope & cost gate

1. Xác nhận bộ keyword (nguồn, số lượng, có volume không) + `$LOCATION`/`$LANGUAGE` + ngưỡng.
2. Chốt DATA TIER khả dụng; Tier 1-2 → báo số call, chờ user xác nhận; >200 keyword → đề xuất phương án lai (cost gate ở trên). Khi chạy Bước 1b, số call = số keyword trong `need_serp.txt`.
3. Hỏi mục đích consumer (mapping / topical map / cannibalization / research) — không đổi method, chỉ để ghi chú bàn giao đúng skill.

### Bước 1 — Chuẩn hóa bộ keyword

1. Dedupe, gom biến thể chính tả/dấu hiển nhiên (chỉ biến thể chắc chắn cùng query — nghi ngờ thì để SERP quyết).
2. Gắn volume per keyword nếu có (thiếu → ghi trống, ảnh hưởng cách đặt tên cụm và `$VOLUME_GATE`).

### Bước 1b — Lọc trước bằng EmbeddingGemma

Đọc `references/gemma-truoc.md`. Đặt `S` = `skills/serp-clustering/scripts/cluster.py`.

1. Ghi bộ keyword đã chuẩn hoá vào `<W>/keywords.txt`, mỗi dòng một keyword.
2. Chạy `~/.venvs/embeddinggemma/bin/python -I $S cos --keywords <W>/keywords.txt --prompt SentenceSimilarity --out <W>/cos.jsonl`.
3. Đọc ngưỡng "chắc khác cụm" theo thứ tự: registry của site → `tools/ai-assist/calibration-defaults.json` → 0,90 trong reference.
4. Chạy `python3 $S triage --cos <W>/cos.jsonl --diff-below <ngưỡng> --out <W>/triage`.
5. Kéo SERP ở Bước 2 chỉ cho keyword trong `<W>/triage/need_serp.txt`. Keyword còn lại là cụm đơn, verdict "TÁCH (Gemma)".
6. Không truyền `--same-from` khi site chưa có ngưỡng "chắc cùng cụm" đã hiệu chuẩn. Mọi verdict GỘP phải có overlap SERP thật.

### Bước 2 — Lấy SERP top-10 per keyword

1. Theo tier đã chốt: per keyword lấy **top-10 organic URLs** (bỏ ads, bỏ SERP features không phải organic link). Đã chạy Bước 1b thì chỉ lấy cho keyword trong `need_serp.txt`.
2. Ghi **ngày chụp SERP** per batch — kết quả clustering có tuổi thọ (xem Behavior Gates #3).
3. Keyword không lấy được SERP (tier fail cục bộ) → đánh dấu, xử lý ở Tier thấp hơn.

### Bước 3 — Ma trận overlap & phân cụm theo ngưỡng

1. Per cặp keyword: đếm số URL trùng giữa 2 bộ top-10 (normalize URL: bỏ trailing slash, utm, http/https — cùng canonical = trùng). Đếm bằng `python3 $S overlap --serp <file SERP>... --out <W>/serp`; script giữ nguồn đầu khi một keyword có nhiều lần kéo SERP và ghi `conflicts.json`.
2. Áp ngưỡng:
   - **≥ `$OVERLAP_THRESHOLD` (mặc định 4/10) URL chung → cùng cụm** (verdict GỘP — 1 URL phục vụ cả cụm).
   - **2-3/10 → BORDERLINE** — không tự verdict: bắt buộc review tay (nhìn 2 SERP thật: page type đang rank, intent signals), ghi lý do gộp/tách vào output.
   - **≤1/10 → TÁCH** (verdict TÁCH — URL riêng).
   - Vai trò 2 ngưỡng: 4/10 URL chung là ngưỡng xếp keyword vào cùng cụm khi lập plan. 6/10 là điều kiện gộp 2 URL đang có. Lý do: cùng một keyword kéo lại SERP trong ngày chỉ chung 5–10/10 URL với chính nó, nên 4–5/10 nằm trong biên dao động của SERP.
3. Keyword không match cụm nào → cụm đơn (singleton).

### Bước 4 — Transitive merge có kiểm soát + đặt tên cụm

1. Merge bắc cầu: A~B và B~C → xét gộp A,B,C. 🔴 Nhưng kiểm tra **cặp xa nhất**: nếu A≁C (overlap dưới ngưỡng) → **flag `chain-merge`, KHÔNG auto gộp** — trình cả 2 phương án (gộp 3 / tách A | B,C hoặc A,B | C) cho review tay.
2. Đặt tên cụm = **keyword volume cao nhất** trong cụm (fallback khi không có volume: keyword ngắn nhất).
3. Ghi overlap evidence per cụm: **min-max số URL chung** giữa các cặp trong cụm (vd "4-7/10").

### Bước 5 — Render output & bàn giao

1. Render bảng theo skeleton Output, kèm header khai báo: DATA TIER, % keyword verified SERP, ngưỡng, location/language, ngày chụp SERP.
2. Bàn giao đúng consumer: chạy trong pipeline client → lưu cạnh deliverable của consumer skill (vd `05-content-plan/` của instance); standalone → trả trong chat.
3. Nhắc rõ: bảng này CHƯA phải quyết định URL/page type — bước kế tiếp thuộc consumer skill.
4. Tự phản biện theo mục dưới, rồi kiểm Behavior Gates.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Mọi verdict GỘP có số overlap SERP thật. Không có verdict GỘP từ cosine. Nguồn lỗi: hiệu chuẩn 19/10/2026, không ngưỡng cosine nào đạt precision 0,95 cho overlap ≥ 6/10; audit GSC 17/10 đề xuất gộp 5 cặp trang, SERP 18/10 cho 4 cặp tách.
- [ ] Gộp 2 URL đang có chỉ khi SERP ≥ 6/10, ghi số overlap cho từng cặp. Verdict GỘP ở 4/10 chỉ xếp keyword vào cùng cụm khi lập plan. Nguồn lỗi: plan mạng nội dung bản 1 ngày 18/10/2026 chỉ kiểm SERP 1 cặp trước khi gộp.
- [ ] Cặp query giá dùng từ khác nhau ("báo giá", "bảng giá", "chi phí") được kéo SERP, không bị Gemma tách. Nguồn lỗi: dev 19/10, "báo giá seo website" và "bảng giá dịch vụ seo tổng thể" có cos 0,8961 nhưng SERP 7/10.
- [ ] Header ghi ngưỡng Gemma, prompt, nguồn ngưỡng (registry, defaults hay reference) và số keyword không cần kéo SERP. Nguồn lỗi: trial `content-inventory-audit` 19/10, prompt `SentenceSimilarity` cho 21.756 cặp trang từ 0,8, nên ngưỡng không dùng chéo prompt hay cấp được.
- [ ] Mỗi cụm ghi ngày chụp SERP. Keyword kéo lại trong ngày có SERP khác thì ghi nguồn được giữ. Nguồn lỗi: 18/10/2026, 11 keyword kéo lại trong ngày có overlap với chính nó 5–10/10.

## Output

```markdown
# SERP Clustering — <bộ keyword / client> · YYYY-MM-DD
> DATA TIER: <1/2/3/4 — nguồn> · Verified SERP: <n/N keyword = %> · Ngày chụp SERP: <date>
> Location/Language: <VN/vi> · Overlap threshold: <4/10 mặc định | điều chỉnh + lý do>
> Lọc Gemma: <cos < ngưỡng, prompt, nguồn ngưỡng | không chạy + lý do> · Keyword không cần kéo SERP: <n/N>
> Consumer dự kiến: <keyword-topic-url-mapping / topical-map-creation / content-refresh / seo-research>

## 1. Bảng cụm
| # | Cụm (keyword đại diện) | Members (kw · vol) | Volume tổng | Overlap evidence (min-max URL chung) | Verdict | Tier |
|---|---|---|---|---|---|---|
| 1 | | | | vd 4-7/10 | GỘP / TÁCH / TÁCH (Gemma) / BORDERLINE-reviewed(lý do) | 1-4 |

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
- ❌ Chạy 500 call MCP không báo trước — cost gate ở Bước 0b là bắt buộc.
- ❌ Trộn SERP khác location/language trong cùng ma trận (kw chụp SERP VN so với kw chụp SERP US).
- ❌ Tái sử dụng bảng cụm >90 ngày cho quyết định mới mà không re-verify cụm quan trọng.
- ❌ Đếm overlap không normalize URL (http vs https, trailing slash, utm) — đếm hụt overlap thật.
- ❌ Gộp cụm vì cosine cao → cosine chỉ được tách cặp chắc khác cụm; GỘP cần SERP.
- ❌ Dùng ngưỡng 0,90 cho site hay ngành mới như số đã chứng minh → ghi là điểm khởi đầu, hiệu chuẩn lại khi có SERP.

## References & wiki

**Skill consumer (DECISION/EXECUTION layer):** `keyword-topic-url-mapping` (công đoạn 4 T1 — consumer chính) · `topical-map-creation` (Step 10 grouping) · `content-refresh` (cannibalization) · `seo-research` (research 1 bài)

**Pattern lớp:** bộ backlink `backlink-research` (DATA) → `backlink-plan` (DECISION) — serp-clustering giữ đúng vai DATA trong bộ keyword/topical.

**Wiki Semantic SEO (lớp WHY):** [[Central Search Intent]] · [[User Intent]] · [[Mixed Intent]] · [[Query Network]] · [[Canonical Query]] · [[syntheses/Lexical-vs-Intent Rule]]

**Nguồn quy trình:** `sop/09-project-timeline/10-thang-thuc-day.md` (công đoạn 4 T1 — nơi method này phục vụ đầu tiên) · `sop/01-topical-map.md` (Central Search Intent).

## Changelog

- **2026-10-19 v1.1.1** — ghi rõ vai trò 2 ngưỡng SERP: 4/10 xếp keyword vào cùng cụm khi lập plan, 6/10 là điều kiện gộp 2 URL đang có (SERP kéo lại trong ngày chỉ chung 5–10/10 với chính nó). Code `cluster.py` đã dùng đúng 2 ngưỡng.
- **2026-10-19 v1.1** — Bước 0 kiểm tool. Thêm Bước 1b lọc trước bằng EmbeddingGemma (`scripts/cluster.py`, `references/gemma-truoc.md`): cos < 0,90 là chắc khác cụm, SERP chỉ quyết cặp giáp ranh. Holdout 18/10: 0 cặp sai, tiết kiệm 5/23 lượt kéo SERP. Không có ngưỡng chắc cùng cụm. Thêm phân việc model, tự phản biện, test offline `tests/test_cluster.py`.

- **2026-07-19 v1.0** — tạo mới, tách từ `keyword-topic-url-mapping` theo quyết định Vincent: SERP-overlap clustering thành DATA/METHOD layer dùng chung (4 consumer: keyword-topic-url-mapping, topical-map-creation, content-refresh, seo-research); ngưỡng ≥4/10 gộp · 2-3/10 borderline review tay · ≤1/10 tách; chain-merge có kiểm soát; data ladder 4 tier (Ahrefs serp-overview → DataForSEO → search tay mẫu → semantic fallback ⚠️); gate SERP 90 ngày + cost gate >200 keyword.
