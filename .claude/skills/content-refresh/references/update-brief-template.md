# Update Brief Template — input cho 10-update-pipeline

Reference cho skill `content-refresh`. Mỗi URL có route flag **UPDATE** sinh đúng 1 brief theo skeleton dưới. Brief này là **input** cho `Content Production/10-update-pipeline`: section "Update reason (kèm bằng chứng)" của brief map 1:1 vào section cùng tên trong template `_TEMPLATES/update.md` của pipeline; các section còn lại của pipeline (Section-level diff, Updated content, Re-publish checklist) do pipeline tự làm — brief KHÔNG viết trước.

**Ranh giới cứng:**
- ✅ Brief chứa: bằng chứng decay, phân loại nguyên nhân + DEPTH, priority score, queries/entities cần chú ý, route flag, re-measurement plan.
- ❌ Brief KHÔNG chứa: diff SERP top 5 chi tiết, section-level plan, content viết sẵn, đề xuất đổi URL.

**Đặt tên & vị trí:** `<slug>__brief_v1.md` → `Content Production - <brand>/10-update-pipeline/<cluster>/` (tăng `_v2`… nếu trùng).

---

## Skeleton

```markdown
# UPDATE BRIEF — <slug>

## Header
- **URL:** <https://…>
- **Slug / Cluster:** <slug> / <cluster>
- **Ngày detect:** <YYYY-MM-DD>
- **Data path:** A (Ahrefs MCP) / B (GSC export <ngày export>) / C (heuristic — triệu chứng)
- **Route flag:** UPDATE  ← chỉ flag UPDATE mới có brief; flag khác ghi trong report tổng
- **DEPTH đề xuất:** light / medium / heavy  ← quyết định skill mà pipeline nạp
- **$REASON đề xuất cho pipeline:** <fact-stale | serp-shift | quarterly-refresh>  ← map vào field `update_trigger` của `_TEMPLATES/update.md` (bảng map cố định ở Hướng dẫn điền nhanh — pre-flight gate của content-update-orchestrator HALT nếu thiếu)

## Update reason (bằng chứng — map 1:1 vào section "Update reason" của _TEMPLATES/update.md)
### Bảng số
| Metric | 28d hiện tại | 28d liền trước | Δ 28d | 90d hiện tại | 90d YoY | Δ YoY |
|--------|--------------|-----------------|-------|--------------|---------|-------|
| Clicks |              |                 |       |              |         |       |
| Impressions |         |                 |       |              |         |       |
| CTR    |              |                 |       |              |         |       |
| Avg position |        |                 |       |              |         |       |

- **Nguồn data + date range:** <tool/file + dd/mm–dd/mm>
- **Gate chain đã qua:** min-data ✅ · self-inflicted ✅ (lần sửa gần nhất: <ngày>) · seasonal YoY ✅ (delta YoY: <x%>) · SERP feature ✅ · cannibalization ✅
- **Queries bị mất / tụt hạng:** (query | position cũ → mới | impressions/28d)
- **Mô tả đồ thị bằng chữ:** <vd: "clicks đi ngang 9 tháng ở ~450/28d, trượt dần từ tháng 3, hiện ~210/28d; position query chính 3,2 → 6,8">

## Cause classification
- **Nguyên nhân chính:** stale facts / SERP intent shift / competitor vượt / thiếu entity-attribute mới (1 trong 4 — 3 loại còn lại đã bị gate chain route đi trước khi tới brief)
- **Confidence:** cao / vừa / thấp
- **Tín hiệu dẫn tới kết luận:** <bullet, cite T-code từ decay-signals.md>
- **Nguyên nhân phụ (nếu có):** <…>

## Priority score (T11 — convention GTV)
- Recovery potential: <peak clicks − current clicks, hoặc traffic value> = <số>
- Ease: KD = <số> (<40 ✅) · structure sound: có/không · backlinks còn: <số RD>
- Business relevance: cao/vừa/thấp (theo input Bước 0)
- **Priority = <kết quả> → hạng <n>/<tổng candidates>**
- (Path C: bỏ section này, thay bằng xếp hạng định tính + danh sách data cần lấy)

## Queries / entities cần chú ý (input cho bước Diff analysis của pipeline — KHÔNG phải section plan)
- Queries đang mất: <…>
- Queries mới liên quan mà page chưa rank: <…>
- Entities/attributes nghi thiếu: <…>
- SERP note thô: <vd: "AIO xuất hiện cho query chính từ ~tháng 5; top 5 có 2 URL mới dạng tool page"> — pipeline sẽ diff chi tiết

## Re-measurement plan
- **7-30 ngày sau re-publish:** GSC impressions cho target queries (SOP GTV — sop/05-audit-checklist.md); check không cannibalize page cũ
- **90 ngày:** validate clicks + position vs baseline trước update
- **6 tháng:** full Historical Data effect (Koray 6-month lag — không kết luận fail sớm hơn mốc này)
- ⚠️ Red flag theo dõi: traffic tăng nhưng impressions target query flat → intent mismatch

## Disclaimer
- Ngưỡng dùng trong brief là đề xuất thực nghiệm có nguồn (T-codes trong references/decay-signals.md) — hiệu chỉnh theo baseline dự án.
- 🔴 Update phải substantive (Update Amount > 0) — cấm chỉ đổi ngày/title/meta (date-spoofing: không qualify là substantive update, bị coi là manipulation — [[Update Score]] / [[GEO]]).
```

---

## Hướng dẫn điền nhanh

| Section | Nguồn dữ liệu | Lưu ý |
|---|---|---|
| Header — DEPTH | Bảng nguyên nhân → DEPTH (decay-signals.md mục 3) | stale = light; competitor/entity = medium; intent shift = heavy |
| Header — $REASON | Bảng map cố định dưới đây | Bắt buộc — thiếu thì pre-flight gate của content-update-orchestrator HALT |
| Update reason | Series từ Bước 1-3 của skill | Mọi số kèm date range + nguồn; không có số không citation |
| Cause classification | Bước 4 | Nếu confidence thấp → ghi rõ data nào sẽ nâng confidence |
| Priority score | Bước 5 | Path C không chấm số |
| Queries/entities | gsc-keyword-history / query export | Dừng ở mức "cần chú ý" — không viết outline |
| Re-measurement | T13 | Luôn đủ 3 mốc 7-30d / 90d / 6 tháng |

**Bảng map cố định: nguyên nhân (Cause classification) → $REASON (`update_trigger` enum của `_TEMPLATES/update.md`):**

| Nguyên nhân chính | $REASON |
|---|---|
| Stale facts | `fact-stale` |
| SERP intent shift | `serp-shift` |
| Competitor vượt | `serp-shift` |
| Thiếu entity-attribute mới | `serp-shift` hoặc `quarterly-refresh` (chọn theo tín hiệu trội: gap do SERP đổi → serp-shift; gap phát hiện qua audit định kỳ → quarterly-refresh) |

Ghi chú: 2 giá trị enum còn lại (`google-update`, `link-broken`) không do skill này sinh — pipeline tự set khi trigger đến từ nguồn khác.
