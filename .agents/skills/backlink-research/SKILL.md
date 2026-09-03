---
name: backlink-research
description: "Backlink research toàn diện — DATA layer của bộ skill backlink (research → plan → thực thi). Use when: (1) 'research backlink [domain/keyword]', 'phân tích backlink đối thủ', 'link gap analysis', 'backlink audit', 'đối thủ lấy link ở đâu'."
metadata:
  version: "2.1"
---

# Backlink Research — Data Layer

Thu thập + phân tích **toàn bộ data nền** cho quyết định backlink: profile mình vs đối thủ, link gap, anchor consensus, velocity, linkable assets, money-page link-gap test. **Chỉ data + observation — KHÔNG ra quyết định plan** (việc của `backlink-plan`).

## Bộ 3 skill backlink (phân vai cứng)

| Layer | Skill | Việc |
|---|---|---|
| **DATA** | ✅ skill này | Research: profile, gap, anchors, velocity, assets |
| **DECISION** | `backlink-plan` | Gate cần-link-không, target URLs, anchor plan, method mix, velocity, budget |
| **EXECUTION** | `textlink-analyzer` | Lọc URL báo + sheet vận hành cho format textlink PR |

## Input

**Required:**
- `$TARGET` — domain/URL của mình (hoặc client GTV)
- `$COMPETITORS` — 3-5 đối thủ (thiếu → đề xuất từ `competitors/live` hoặc SERP, chờ confirm)

**Optional:** `$MARKET` (default vn) · `$MONEY_PAGES` (list URL SEO mong muốn — bật Bước 5 link-gap test) · `$KEYWORDS` (cho anchor consensus SERP) · `$SOURCE_CONTEXT` (đánh relevance)

**Path detection (thứ tự ưu tiên Vincent chốt 07/2026):**
```
Path A — DataForSEO Backlinks API (PRIORITY — user cấp key/data hoặc chạy qua API)
  → references/dataforseo-backlinks-api.md: endpoint map + fields + cost notes
Path B — Ahrefs (MCP hoặc export UI)
Path C — CSV export bất kỳ (user paste/gửi file)
```
Cost-aware mọi path: báo số call dự kiến trước; bulk endpoints (`bulk_ranks`, `bulk_spam_score`, `bulk_referring_domains`) cho danh sách lớn thay vì gọi lẻ.

## Workflow 7 bước

### Bước 0 — Scope & confirm
Báo: target, competitor set, path, money pages có/không, số call dự kiến, output location. Chờ confirm.

### Bước 1 — Profile overview (mình + từng đối thủ)
`summary/live` per domain: rank, backlinks, **referring_domains** (+main domains, IPs, subnets — đa dạng thật hay farm), **backlinks_spam_score**, broken, **referring_links_attributes** (dofollow/nofollow/sponsored/ugc ratio), links_types, TLDs, countries. Bảng so sánh 1 nhìn ra vị thế.

### Bước 2 — Velocity
`timeseries_summary/live` + `timeseries_new_lost_summary/live` 12 tháng: RD mới/mất per tháng per domain → **nhịp RD/tháng của đối thủ** = input chuẩn velocity cho plan (nguyên tắc Floate 2016→2026: match nhịp đối thủ, không bung).

### Bước 3 — Link gap
`domain_intersection/live` (mình + competitors): domain trỏ **≥2 đối thủ nhưng KHÔNG trỏ mình** = gap chính. Per gap domain: rank, spam score (`bulk_spam_score` — **prior yếu, không phải verdict**), loại site (news/blog/directory/tool — đoán từ domain + spot-check), link tới đối thủ nào/trang nào/anchor gì. Screening theo [references/spam-filter-criteria.md](references/spam-filter-criteria.md): verdict `KEEP / REVIEW / REJECT` — REJECT cần **≥2 tín hiệu máy đồng thời** (M1-M6), nghi ngờ → REVIEW (giữ + đánh dấu); relevance theo `$SOURCE_CONTEXT` **trước** DR (Theme > Trust — [[Link Building]]).

### Bước 4 — Anchor consensus (nền cho plan)
`anchors/live` cho: mình + top đối thủ (+ nếu có `$KEYWORDS`: top 5-10 URL đang rank). Phân loại 8 nhóm (exact/partial/brand/brand+KW/naked/generic/synonym/title) → bảng **consensus per SERP**: "top 5 đang ở X% brand / Y% exact". Đây là input quyết định của anchor plan (SERP-consensus-first — Floate 2026: "Mimic the winners"); flag lệch của mình vs consensus.

### Bước 5 — Money-page link-gap test (nếu có $MONEY_PAGES)
Per money page dự kiến: export backlink của **money page tương ứng ở top 5 đối thủ** (`backlinks/live` mode URL / `page_intersection/live`) → đếm **unique quality RDs** (lọc theo [references/spam-filter-criteria.md](references/spam-filter-criteria.md) — chỉ trừ REJECT; REVIEW vẫn đếm kèm dấu *) → delta vs trang mình = **climb cost**. Ghi observation: "đối thủ 0 quality links vào money page" (→ plan sẽ route supporting content) hoặc "gap = N RDs DR30+" — KHÔNG tự kết luận build hay không (việc của plan).

### Bước 6 — Linkable assets & nguồn của đối thủ
`domain_pages_summary/live` per competitor: top trang hút link → content type nào hút link trong niche (data study/tool/guide/infographic) + pattern nguồn (báo/blog lặp lại ở nhiều đối thủ = ứng viên outreach).

### Bước 7 — Research file (output chuẩn)

```markdown
# Backlink Research — [target] vs [competitors] · [date] · Path A/B/C
## 1. Profile overview [bảng: rank/RD/spam/dofollow%/velocity]
## 2. Velocity: nhịp RD/tháng từng đối thủ (12 tháng) + trung bình
## 3. Link gap: top N domain (≥2 competitors, chưa trỏ mình) — relevance-first, kèm spam score
## 4. Anchor consensus: bảng 8 nhóm per SERP/domain + lệch của mình
## 5. Money-page link-gap test (nếu chạy): per URL — quality RDs đối thủ vs mình = climb cost
## 6. Linkable assets: content type hút link + nguồn lặp lại
## Caveats: ngày pull, path, tiêu chí bỏ qua, độ tin
```
**Location:** client GTV → `PROJECTS/<client>/backlink-research/`; standalone → trả trong chat. File này = input bắt buộc của `backlink-plan`.

## Behavior Gates

- **#1 Think Before:** confirm scope + cost trước khi gọi API.
- **#2 Evidence:** mọi số truy nguyên được (endpoint nào, ngày nào); anchor % kèm bảng đếm.
- **#3 Surgical:** research = observation, KHÔNG ra quyết định (target nào, anchor gì, build bao nhiêu — của `backlink-plan`); KHÔNG đề xuất mua link/PBN/disavow.
- **#4 Goal-driven:** đủ 6 section + caveats.

## Anti-patterns

- **Loại domain CHỈ vì tool flag spam/toxic score** — score là prior yếu (DataForSEO = 18 tín hiệu thuần technical, không đo traffic/relevance; Mueller: "toxic links là metric tool bịa"); REJECT cần ≥2 tín hiệu M1-M6 + mọi ca lưng chừng → REVIEW. Không dùng chữ "toxic" trong report.
- Đếm backlink thô không lọc spam/relevance — 1 link relevant DR50 > 100 directory rác.
- Chọn gap theo DR thô bỏ qua Theme (vi phạm Theme > User signal > Trust).
- Kết luận "nên build X links vào Y" trong research file (lấn sân DECISION layer).
- Bỏ Bước 2 velocity — plan không có nhịp chuẩn sẽ bung link sai tốc độ.
- Pull từng domain lẻ khi có bulk endpoint (đốt cost).
- Quên `referring_links_attributes` — thiếu dofollow/sponsored ratio là thiếu nửa bức tranh.

## References & wiki

- [references/dataforseo-backlinks-api.md](references/dataforseo-backlinks-api.md) — endpoint map verified 07/2026 + fields + cost notes
- [references/spam-filter-criteria.md](references/spam-filter-criteria.md) — tiêu chí GIỮ/LOẠI link: Tầng 1 máy (≥2 tín hiệu M1-M6) + Tầng 2 người/LLM (relevance-first) + disavow policy
- Wiki: [[Link Building]] (nguyên tắc hợp nhất Vincent 2021 + Floate 2026) · [[TrustRank]] (proxy trust ≠ DR) · [[sources/backlink-a-z-video-vincent-2021]] · [[sources/research-2026-07-backlink-methods]] · [[sources/research-2026-07-spam-link-criteria]]

## Changelog

- **v2.1 (2026-07-04):** thêm `references/spam-filter-criteria.md` (research 07/2026: Mueller/SpamBrain neutralize, DataForSEO 18 signals thuần technical, Semrush false positives, Floate Link Vetting, Ahrefs no-score-by-design) — screening Bước 3/5 chuyển sang verdict KEEP/REVIEW/REJECT, spam score hạ xuống prior yếu; anti-pattern mới "loại chỉ vì tool flag".
- **v2.0 (2026-07-04):** rename từ `competitor-backlink-analysis` v1.0 + mở rộng thành DATA layer đầy đủ: DataForSEO Path A ưu tiên (endpoint reference mới), thêm Bước 2 Velocity + Bước 4 Anchor consensus (SERP-first) + Bước 5 Money-page link-gap test (Floate 09/2025); siết phân vai 3 layer (bỏ "opportunity shortlist" — chuyển sang backlink-plan). Nền: video process Vincent 2021 + research Floate/industry 07/2026.
- v1.0 (2026-07-04): bản đầu tên `competitor-backlink-analysis` (Ahrefs-first, 6 bước, shortlist Authority×Relevance×Attainability).
