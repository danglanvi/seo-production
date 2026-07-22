---
name: keyword-topic-url-mapping
description: "Gom bộ keyword CAM KẾT hợp đồng thành topic → xác định URL SEO tương ứng — công đoạn (4) T1 của quy trình 10 tháng GTV, MAPPING layer đứng trước topical map và traffic plan. Phương pháp: gọi skill serp-clustering (DATA layer) lấy bảng cụm SERP-overlap → skill này CONSUME bảng cụm rồi quyết định; fallback semantic/intent grouping thủ công theo Central Search Intent khi không chạy được serp-clustering. Từ topic → 1 URL SEO chính (chống cannibalization), phân loại Core/Outer, intent I/N/C/T, page type đề xuất, % keyword + % search volume per topic. Use when: (1) 'nhóm keyword cam kết thành topic cho [client]', 'mapping keyword → URL SEO', 'công đoạn 4 T1'; (2) có bộ từ khóa hợp đồng (kpi-commitments.md hoặc paste) cần chuyển thành cấu trúc topic/URL trước khi làm topical map; (3) cần bảng keyword ↔ topic ↔ URL ↔ intent ↔ Core/Outer ↔ % làm input cho topical-map-creation + traffic-plan. Data priority: Ahrefs MCP (serp-overview) → DataForSEO SERP → grouping thủ công theo intent. KHÔNG dùng cho: xây SCN/topical map đầy đủ toàn site (→ topical-map-creation — skill này CHỈ mapping bộ keyword cam kết), research 1 bài/1 SERP sâu (→ seo-research), forecast traffic (→ traffic-plan)."
metadata:
  version: "1.1"
---

# Keyword → Topic → URL SEO Mapping

Thực thi công đoạn (4) T1 quy trình 10 tháng: **"Nhóm keyword cam kết thành topic → URL SEO tương ứng"** (`sop/09-project-timeline/10-thang-thuc-day.md`, bảng Tháng 1). Input là bộ từ khóa CAM KẾT trong hợp đồng — output là bảng mapping keyword ↔ topic ↔ [[URL SEO]] ↔ intent ↔ Core/Outer ↔ % keyword + % volume, làm nền cho `topical-map-creation` (T1-T2) và `traffic-plan` (T2-T4).

🔴 Phạm vi CHỈ là bộ keyword cam kết (thường vài chục đến vài trăm keyword) — không phải toàn bộ query space của niche. Toàn bộ query space là việc của topical map.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Gom nhóm keyword bằng SERP-overlap (ma trận overlap, ngưỡng, chain-merge, tier data) | `serp-clustering` | DATA layer — skill này CONSUME bảng cụm của serp-clustering rồi ra quyết định URL/intent/Core-Outer; không tự chạy clustering. Fallback thủ công (Tầng 2) chỉ khi serp-clustering không chạy được |
| SCN / topical map đầy đủ toàn site (Source Context, Central Entity, 23 bước) | `topical-map-creation` | Skill này CHỈ mapping bộ keyword cam kết; output là 1 input của topical map, không thay thế map. Topic Outer phát sinh thêm ngoài bộ cam kết → ghi chú gợi ý, không tự mở rộng |
| Research sâu 1 bài / 1 SERP (Layer A/B, consensus) | `seo-research` | Skill này chỉ nhìn SERP ở mức overlap URL để cluster, không phân tích content đối thủ |
| Forecast traffic per topic/URL | `traffic-plan` | Skill này không gắn số traffic dự phóng — chỉ % keyword + % volume phân bổ |
| Audit cannibalization site đang chạy | `technical-seo-audit` + `content-refresh` | Skill này CHỐNG cannibalization từ khâu plan (1 topic = 1 URL chính), không audit hiện trạng |
| Wireframe / cấu trúc website từ URL list | `visual-semantic-seo` + `semantic-html-optimization` | Skill này dừng ở đề xuất page type, không thiết kế trang |

## Input

**Required:**
- `$CLIENT` — tên client/instance SEO Production.
- Bộ keyword cam kết: đọc từ `00-client-context/kpi-commitments.md` của instance, hoặc user paste (keyword + volume nếu có + vị trí hiện tại nếu có).

**Optional:**
- `$SITE` — domain client (để nhận diện URL đã tồn tại có thể nhận topic thay vì tạo URL mới).
- `$SERP_DATA` — export SERP top-10 per keyword (Ahrefs/DataForSEO/user tự chạy).
- `$OVERLAP_THRESHOLD` — ngưỡng cluster, mặc định **≥4/10 URL top-10 chung → cùng topic** (điều chỉnh được: niche SERP đồng nhất cao có thể nâng 5-6; lưu ý `topical-map-creation` Step 10 dùng threshold 3 — khác biệt là chủ đích: bộ cam kết cần cluster chặt hơn để không thiếu URL money).

**Data ladder (v1.1 — Tier 1-2 chạy BÊN TRONG `serp-clustering`, ladder chi tiết + cost gate xem skill đó; khai báo DATA TIER trong output):**

| Tier | Nguồn | Ghi chú |
|---|---|---|
| Tier 1-2 | Skill `serp-clustering` (Ahrefs MCP `serp-overview` → DataForSEO SERP → search tay mẫu đại diện) | Gọi serp-clustering với bộ keyword + `$OVERLAP_THRESHOLD` → nhận bảng cụm kèm overlap evidence + tier data; cost gate (số call = số keyword) do serp-clustering báo |
| Tier 3 | Semantic/intent grouping thủ công theo [[Central Search Intent]] | Fallback khi không chạy được serp-clustering — luôn chạy được: cluster bằng phân tích intent + lexical, ghi rõ "cluster chưa verify bằng SERP" |

## Workflow

### Bước 0 — Đọc references + xác nhận scope

1. Đọc `sop/09-project-timeline/10-thang-thuc-day.md` (công đoạn 4, T1) + `00-client-context/kpi-commitments.md` của instance.
2. Xác nhận: bộ keyword đủ chưa (đúng bản cam kết hợp đồng, không phải wishlist), có volume kèm không, `$SITE` có content sẵn không.
3. Chốt DATA TIER; Tier 1-2 → gọi `serp-clustering` (cost gate + báo số call do skill đó thực hiện).

### Bước 1 — Chuẩn hóa bộ keyword

1. Dedupe, tách biến thể chính tả/dấu, gắn volume (thiếu volume → lấy qua Ahrefs `keywords-explorer-overview` hoặc để trống ghi chú).
2. Gắn nhãn intent sơ bộ per keyword: **I** (Informational) / **N** (Navigational) / **C** (Commercial) / **T** (Transactional) — theo [[User Intent]]; keyword mơ hồ → đánh dấu xử lý ở Bước 2 theo [[Mixed Intent]].

### Bước 2 — Clustering 2 tầng

**Tầng 1 — SERP-overlap clustering qua `serp-clustering` (ưu tiên khi có data):**
1. Gọi skill `serp-clustering` với bộ keyword đã chuẩn hóa (Bước 1), truyền `$OVERLAP_THRESHOLD` nếu khác mặc định → nhận **bảng cụm**: members, volume, overlap evidence (min-max URL chung), verdict GỘP/TÁCH/BORDERLINE, tier data, ngày chụp SERP.
2. Skill này KHÔNG tự chạy ma trận overlap nữa — CONSUME bảng cụm rồi ra quyết định URL / intent / Core-Outer ở Bước 3.
3. Cụm BORDERLINE hoặc flag `chain-merge` từ serp-clustering → quyết định tại đây theo intent + monetization, ghi lý do vào mục 3 của output.

**Tầng 2 — Semantic/intent grouping (fallback khi không chạy được serp-clustering, hoặc bổ trợ cho keyword thiếu SERP data):**
1. Nhóm theo [[Central Search Intent]]: cùng entity + cùng nhu cầu người dùng + cùng loại kết quả kỳ vọng → cùng topic.
2. Keyword khác intent (I vs T) KHÔNG gộp dù chung entity — "mua X" và "X là gì" là 2 topic/URL khác nhau.
3. Cluster từ tầng 2 đánh dấu `⚠️ chưa verify SERP` — đề xuất verify lại khi có data.

### Bước 3 — Topic → URL SEO

Per topic:
1. **1 topic = 1 URL chính** — chống cannibalization từ khâu plan. Keyword phụ trong topic = biến thể/secondary keyword của cùng URL.
2. Phân loại **Core / Outer Section**: topic mang monetization + gần Central Search Intent → [[Core Section]]; topic bổ trợ/informational nuôi [[Historical Data]] → [[Outer Section]] (chuẩn phân loại theo `sop/01-topical-map.md` Bước 5-6).
3. Intent chủ đạo của topic (I/N/C/T) — topic hybrid ghi chú theo [[Mixed Intent]] (default tách, exception khi SERP ≥7/10 hybrid).
4. **Page type đề xuất**: category / product / blog / landing (theo intent + SERP top-10 đang rank page type gì — [[Page Types]]).
5. URL: dùng URL sẵn có của `$SITE` nếu match topic (ghi `EXISTING`), không thì đề xuất slug mới (`NEW`) — Core flat, Outer sâu hơn theo convention topical map.

### Bước 4 — Tính % phân bổ

- **% keyword per topic** = số keyword trong topic / tổng bộ cam kết.
- **% search volume per topic** = tổng volume topic / tổng volume bộ cam kết (chỉ khi có volume; thiếu → ghi N/A).
- Sanity check: topic chiếm >40% volume → flag "topic quá nặng, xem xét tách" ; keyword lẻ loi không cluster được → topic đơn hoặc gán làm secondary cho topic gần nhất (ghi chú lý do).

### Bước 5 — Render output & lưu

1. Render bảng theo skeleton Output.
2. Lưu `05-content-plan/` của instance, naming `{{CLIENT}}_keyword-topic-url-mapping_v{{N}}.md`.
3. Ghi trạng thái **CHỜ DUYỆT: SEO Lead Project** (cột Duyệt công đoạn 4, T1).
4. Nhắc bước kế tiếp: bảng này là input cho `topical-map-creation` (chốt SCN đầu T2) + `traffic-plan`.

## Output

```markdown
# <CLIENT> — Keyword → Topic → URL SEO Mapping (công đoạn 4, T1)
> Ngày lập: YYYY-MM-DD · DATA TIER: <1/2/3 — nguồn SERP + ngày> · Overlap threshold: <4/10>
> Bộ keyword cam kết: <N> keywords · Tổng volume: <N | N/A>
> Trạng thái: **CHỜ DUYỆT — SEO Lead Project**

## 1. Bảng mapping
| # | Topic | URL SEO (EXISTING/NEW) | Core/Outer | Intent | Page type | Keywords trong topic | % keyword | % volume | Verify SERP |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | kw1 (vol) · kw2 (vol)… | | | ✅ / ⚠️ chưa verify |

## 2. Tổng hợp phân bổ
| Chỉ số | Giá trị |
|---|---|
| Số topic | |
| Số URL (EXISTING / NEW) | |
| Tỷ lệ Core : Outer (theo URL) | |
| Topic nặng nhất (% volume) | |

## 3. Keyword chưa xếp được / cần quyết định
- <keyword mơ hồ intent, cluster mâu thuẫn SERP vs semantic — kèm đề xuất>

## 4. Ghi chú cho bước sau
- Input cho: topical-map-creation (chốt SCN đầu T2) · traffic-plan (forecast)
- Gợi ý topic Outer phát sinh ngoài bộ cam kết (nếu thấy): <liệt kê — KHÔNG tự triển khai>
```

## Behavior Gates

**#1 Think Before** — Xác nhận bộ keyword đúng là bản CAM KẾT hợp đồng trước khi cluster. Trước khi gọi MCP: báo số call (= số keyword ở Tier 1), chờ xác nhận; bộ >100 keyword → đề xuất phương án mẫu đại diện.

**#2 Evidence** — Cluster nào từ SERP-overlap ghi số overlap thực (vd "6/10"); cluster nào từ semantic grouping đánh dấu `⚠️ chưa verify SERP`. Output khai báo DATA TIER. Không hard-fail thiếu MCP — Tier 3 luôn chạy được.

**#3 Surgical** — Chỉ mapping bộ cam kết. Không mở rộng sang toàn niche, không viết brief, không forecast traffic, không thiết kế page. Topic phát sinh ngoài bộ cam kết → mục "Gợi ý" rồi dừng.

**#4 Goal-driven** — Deliverable trả lời được: "bộ cam kết cần bao nhiêu URL, URL nào Core URL nào Outer, keyword nào về URL nào, sức nặng volume nằm ở đâu" — mỗi keyword cam kết phải có đúng 1 URL phụ trách, không keyword nào 2 URL (cannibalization) và không keyword nào 0 URL (bỏ sót cam kết).

## Anti-patterns

- ❌ Gộp keyword khác intent (I vs T) vào 1 URL vì chung entity.
- ❌ 1 topic nhiều URL chính — cannibalization từ khâu plan.
- ❌ Cluster chỉ bằng lexical similarity (chung chữ) khi có SERP data — SERP overlap là bằng chứng mạnh hơn ([[syntheses/Lexical-vs-Intent Rule]]).
- ❌ Tự mở rộng sang topic ngoài bộ cam kết rồi trình như một topical map — lấn sân `topical-map-creation`.
- ❌ Bỏ keyword cam kết ra khỏi bảng vì "khó cluster" — mọi keyword cam kết phải có URL phụ trách.
- ❌ Đề xuất URL NEW khi site đã có URL EXISTING match topic — kiểm tra `$SITE` trước.
- ❌ Trình % volume khi một nửa bộ keyword không có volume mà không ghi N/A/caveat.
- ❌ Trình bảng như bản chốt khi chưa có duyệt SEO Lead Project.

## References & wiki

**Nguồn quy trình:**
- `sop/09-project-timeline/10-thang-thuc-day.md` — công đoạn (4) T1: "Nhóm keyword cam kết thành topic → URL SEO tương ứng + % keyword theo topic".
- `sop/01-topical-map.md` — chuẩn Core/Outer Section (Bước 5-6), Central Search Intent (Bước 4).
- `SEO Production/00-client-context/kpi-commitments.md` (per instance) — nguồn bộ keyword cam kết.

**Wiki Semantic SEO (lớp WHY):** [[URL SEO]] · [[Central Search Intent]] · [[User Intent]] · [[Mixed Intent]] · [[Core Section]] · [[Outer Section]] · [[Query Network]] · [[Canonical Query]] · [[Page Types]] · [[syntheses/Lexical-vs-Intent Rule]]

**Skill anh em:** `topical-map-creation` (downstream — SCN đầy đủ) · `traffic-plan` (downstream — forecast) · `seo-research` (research 1 bài) · `competitor-seo-gap-analysis`

## Changelog

- **2026-07-19 v1.1** — tách SERP-overlap clustering ra skill `serp-clustering` (DATA layer), skill này giữ DECISION layer: Bước 2 Tầng 1 = gọi serp-clustering → nhận bảng cụm → quyết định URL/intent/Core-Outer; giữ Tầng 2 fallback thủ công khi không chạy được serp-clustering; thêm dòng Phân vai + cập nhật data ladder.
- **2026-07-19 v1.0** — tạo mới: thực thi công đoạn (4) T1 sop/09; clustering 2 tầng (SERP-overlap ≥4/10 ưu tiên → semantic/intent fallback), 1 topic = 1 URL chính, phân loại Core/Outer + intent I/N/C/T + page type + % keyword/% volume; data ladder Ahrefs serp-overview → DataForSEO → thủ công; gate duyệt SEO Lead Project.
