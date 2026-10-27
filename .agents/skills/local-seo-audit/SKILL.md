---
name: local-seo-audit
description: "Audit local SEO tầng WEBSITE-SIGNALS + GBP-CONTENT cho khách local VN (nửa website của cặp skill local; nửa kia: map-pack-intelligence): business type, GBP checklist, NAP onsite, location pages đa chi nhánh, citations, review. Use when: 'audit local SEO [khách]', 'tối ưu GBP', 'location page cho chuỗi'."
metadata:
  version: "1.0.1"
---

# Local SEO Audit — website signals + GBP content theo business type

Audit **nửa WEBSITE-SIGNALS** của local SEO: những gì client kiểm soát trực tiếp — GBP listing content, NAP onsite, location pages, citations, review operations. Nửa còn lại (đo lường ngoài platform: geo-grid ranking, Share of Local Voice, competitor radius) thuộc `map-pack-intelligence` — hai skill là một cặp: skill này tạo **action list**, skill kia đo **kết quả theo tọa độ**.

Ngữ cảnh VN: Google Business Profile + Google Maps là kênh local chính; directory VN (Foody, ngành dọc y tế/F&B) là lớp phụ; mô hình đa chi nhánh rất phổ biến (chuỗi phòng khám, showroom, nhà hàng) → checklist location pages là mục nặng ký, không phải phụ lục.

Lớp WHY: GBP listing = một [[Entity Home]] cấp local cho [[Central Entity]]; NAP consistency = entity reconciliation tín hiệu ([[Knowledge Graph]] gộp signal khi Name/Address/Phone nhất quán cross-source, tinh thần [[Consensus]]); mỗi chi nhánh = 1 entity con với [[E-A-V Framework]] riêng (địa chỉ, giờ, đội ngũ, dịch vụ).

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Geo-grid rank tracking, SoLV, competitor radius, cross-platform NAP matrix (Google/Apple/Bing) | `map-pack-intelligence` | Skill này audit CÁI CLIENT LÀM (listing + website); nửa kia đo CÁI GOOGLE TRẢ (vị trí per điểm lưới). Review: skill này audit *vận hành* (velocity mình, phản hồi, keyword) — so sánh nhịp review vs 3-5 đối thủ map pack thuộc nửa kia |
| Viết/sửa JSON-LD LocalBusiness, @id graph, sameAs | `schema-markup-generator` | Skill này chỉ *flag* schema thiếu/lệch NAP + route sang, không viết markup |
| Entity strategy tổng (Entity Home, Wikipedia/Wikidata, Knowledge Panel) | `sop/04-entity-optimization.md` + [[Brand Entitization Playbook]] | Skill này chỉ lo lớp LOCAL của entity (GBP + NAP), không dẫn toàn bộ entitization |
| Crawl/index/redirect/CWV site-level | `technical-seo-audit` | Location page không index được → flag + route, không tự audit technical |
| Citations như LINK layer (authority của nguồn citation) | `backlink-research` | Skill này chỉ check *NAP consistency + duplicate* trên citations, không đánh giá link value |
| Content chất lượng trang chi nhánh (semantic, E-A-V trong body) | `seo-onpage` / `semantic-content-audit` | Skill này check location page có *đủ yếu tố unique* hay không (checklist structural), không chấm chất lượng viết |

## Input

**Required:**
- `$BUSINESS` — tên business + domain (nếu có website).

**Optional:**
- `$GBP_URL` — link Google Maps listing (hoặc tên tìm được trên Maps).
- `$BRANCHES` — danh sách chi nhánh (tên + địa chỉ + SĐT); bắt buộc hỏi nếu là chain.
- `$GBP_DATA` — export GBP Insights / screenshot dashboard (photos, posts, Q&A, reviews) do khách cung cấp.
- `$COMPETITORS` — 3-5 đối thủ map pack (nếu chưa có → lấy từ output `map-pack-intelligence` hoặc user search tay).
- `$NICHE` — ngành dọc (quyết định directory VN nào đáng check: Foody cho F&B, BookingCare cho phòng khám…).

**Data ladder (khai báo TIER ngay đầu report):**

| Tier | Điều kiện | Data |
|---|---|---|
| **Tier 1** | DataForSEO Business Data API khả dụng | Listing data + reviews + photos count máy đọc được, cross-check nhiều listing 1 lần |
| **Tier 2** | Khách có quyền quản trị GBP | Export GBP Insights + screenshot dashboard (posts, Q&A, review inbox, attributes) — phần insights KHÔNG xem được từ ngoài |
| **Tier 3 (đường lùi cuối)** | Chỉ có tên business + website | Xem GBP public trên Maps ẩn danh + crawl website + search directory tay. Luôn chạy được; report ghi rõ mục nào thiếu data quản trị |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'curl,firecrawl?,dataforseo?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0 — Đọc references + phân loại business type (gate cứng, chờ xác nhận)

1. Đọc [references/gbp-checklist.md](references/gbp-checklist.md) + [references/location-page-checklist.md](references/location-page-checklist.md).
2. Xác định **DATA TIER** theo bảng trên + entity nào (client GTV nào — không mix).
3. Phân loại **business type** — quyết định checklist nào chạy:

| Type | Đặc điểm | Checklist khác biệt |
|---|---|---|
| **Brick-and-mortar** | 1 địa điểm khách đến (nhà hàng, showroom đơn) | Full GBP + NAP + review; KHÔNG cần location pages |
| **Service-area business (SAB)** | Đến nhà khách (sửa chữa, vận chuyển) — GBP ẩn địa chỉ | Service-area settings đúng vùng; KHÔNG ép hiện địa chỉ; trang service-area thay location page |
| **Hybrid** | Có cửa hàng + phục vụ tận nơi | Cả hai lớp trên; địa chỉ hiện + service area khai đúng |
| **Multi-location chain** | Chuỗi phòng khám/showroom/nhà hàng | Mỗi chi nhánh 1 GBP + 1 location page; thêm lớp consistency cross-branch + store locator |

4. Chain → bắt buộc có `$BRANCHES` đầy đủ trước khi chạy; thiếu → hỏi, không đoán số chi nhánh.
5. Báo scope + số call/tool dự kiến (nếu Tier 1 dùng API) → chờ user xác nhận.

### Bước 1 — GBP optimization checklist (per listing)

Chạy [references/gbp-checklist.md](references/gbp-checklist.md), tóm khung:

1. **Categories** — primary category = dịch vụ chính doanh thu (không phải category rộng nhất); secondary categories phủ dịch vụ phụ; đối chiếu category đối thủ top map pack (data từ `map-pack-intelligence` nếu có).
2. **Attributes** — điền hết attributes áp dụng (thanh toán, tiện ích, accessibility); attribute sai thực tế = flag ❌ (trust risk).
3. **Mô tả** — có [[Central Entity]] + dịch vụ chính + khu vực; không nhồi keyword.
4. **Photos** — số lượng (so đối thủ), chất lượng, **geo-context** (ảnh mặt tiền nhận diện được vị trí, ảnh trong không gian thật, không stock); logo + cover đúng brand.
5. **GBP posts cadence** — tần suất đăng (baseline: có nhịp đều còn sống, vd hàng tuần), loại post (offer/update/event) khớp mùa vụ ngành.
6. **Q&A seeding** — câu hỏi phổ biến đã được owner seed + trả lời chưa; Q&A trôi nổi không ai trả lời = flag.
7. **Products/Services section** — khai đủ dịch vụ với mô tả + giá (nếu công khai được).
8. **Booking/action link** — link đặt lịch/đặt bàn/chat hoạt động, về đúng landing chi nhánh (chain: không đổ hết về homepage).

### Bước 2 — NAP consistency onsite

1. Lấy NAP chuẩn = **đúng như trên GBP** (single source of truth, thống nhất với khách nếu GBP đang sai).
2. Check 4 vị trí: **LocalBusiness schema** (chỉ flag đúng/thiếu/lệch — generate/sửa → route `schema-markup-generator`), **footer**, **contact page**, **trang chi nhánh**.
3. Tiêu chí: Name/Address/Phone khớp GBP **từng ký tự** — "Số 12" vs "12", "P.508" vs "Phòng 508", "+84" vs "0" đều tính là lệch (entity reconciliation bằng string matching + signal aggregation, đừng bắt Google đoán).
4. SĐT: 1 số chính per chi nhánh, nhất quán; tracking number → flag rủi ro NAP mismatch, cần quyết định của khách.

### Bước 3 — Location pages (chỉ multi-location / hybrid nhiều điểm)

Chạy [references/location-page-checklist.md](references/location-page-checklist.md), tóm khung — mỗi chi nhánh 1 trang UNIQUE:

- URL riêng ổn định (`/chi-nhanh/quan-1/`), không tab JS chung 1 URL.
- **Chống duplicate template mỏng** — trang chỉ khác mỗi địa chỉ = thin duplicate; bắt buộc yếu tố riêng: đội ngũ/bác sĩ/quản lý chi nhánh, dịch vụ riêng có tại chi nhánh, review chi nhánh đó (không trộn review toàn chuỗi), ảnh thật chi nhánh, chỉ đường/landmark địa phương ([[E-A-V Framework]]: mỗi chi nhánh có bộ attribute-value riêng).
- Embed map đúng tọa độ + NAP + giờ mở cửa (khớp GBP, kể cả giờ lễ).
- Internal link: trang chủ/footer/store locator → mọi location page; location page → dịch vụ liên quan. Trang mồ côi = ❌.
- Index check: location page có index không → nếu vấn đề technical, route `technical-seo-audit`.

### Bước 4 — Citations health

1. Lớp citation VN theo thứ tự trọng số: **Google Maps → Facebook page → directory ngành dọc theo `$NICHE`** (Foody/F&B, BookingCare/y tế…) → directory tổng hợp. Không đu bám danh sách citation US (Yelp, YellowPages) — ghi rõ không áp dụng.
2. Check NAP trên từng citation vs NAP chuẩn — bảng consistency.
3. **Duplicate listing detection** — search Maps theo tên + SĐT + địa chỉ gần đúng; listing trùng/cũ (địa chỉ cũ chưa đóng, tên cũ) = ❌ P0 vì chẻ review + signal.
4. Cross-platform matrix đầy đủ (Google/Apple/Bing/Facebook) → thuộc `map-pack-intelligence`; skill này chỉ lo layer VN chính + duplicate.

### Bước 5 — Review signals (vận hành phía mình)

1. **Velocity** — nhịp review mới/tháng (3-6 tháng gần nhất); đứt nhịp dài = flag quy trình xin review chết.
2. **Rating trung bình vs đối thủ** — so 3-5 đối thủ map pack (số lấy từ Maps public hoặc `map-pack-intelligence`).
3. **Tỷ lệ phản hồi** — % review được owner trả lời, đặc biệt review xấu; template trả lời copy-paste y hệt = flag.
4. **Keyword trong review** — review có nhắc tên dịch vụ/khu vực tự nhiên không (không seed giả — mua/fake review = cấm tuyệt đối, vi phạm policy + rủi ro suspension).

### Bước 6 — Render report + action list

Theo skeleton Output; mỗi finding ❌/⚠️ bắt buộc kèm **Falsifiability**. Kết report: đề xuất chạy `map-pack-intelligence` lấy SoLV baseline trước khi fix (đo được before/after).

## Output

File: `<client>_Local-SEO-Audit_v1.md` trong thư mục công đoạn theo ma trận M (`_REFERENCE/runtime-workstream-matrix.md` §5.2). Ngoài repo dự án: thư mục output của workstream. Tăng `_v2` nếu trùng.

```markdown
# Local SEO Audit — <business>
> Ngày: YYYY-MM-DD · Business type: <B&M / SAB / hybrid / chain (n chi nhánh)> · DATA TIER: <1/2/3 + nguồn> · Niche: <niche>

## 1. Executive Summary
- Tình trạng 3-5 câu · số finding theo priority P0/P1/P2
- Top 3 việc làm ngay

## 2. Bảng tổng hợp
| Khu vực | ✅ | ⚠️ | ❌ | ⬜ | Lỗi nặng nhất |
|---|---|---|---|---|---|
| GBP listing (per chi nhánh nếu chain) | | | | | |
| NAP onsite | | | | | |
| Location pages *(chain/hybrid)* | | | | | |
| Citations | | | | | |
| Review signals | | | | | |

## 3. Chi tiết theo khu vực
### 3.x <Khu vực>
| Check | Status | Evidence (nguồn + ngày) | Tiêu chí ĐẠT |
|---|---|---|---|
**Nhận định:** <WHY — link wiki concept nếu liên quan>

## 4. Action list ưu tiên
| # | Priority | Finding | Hành động | Người làm | **Falsifiability** (biết sai nếu…? + leading indicator) |
|---|---|---|---|---|---|

## 5. Data còn thiếu
- <mục ⬜ + hướng dẫn khách lấy: GBP Insights export, screenshot Q&A/posts, danh sách chi nhánh…>

## 6. Route sang skill anh em
- <schema cần viết → schema-markup-generator · đo SoLV baseline → map-pack-intelligence · …>
```

## Behavior Gates

**#1 Think Before** — Bước 0 là gate cứng: chưa chốt business type + DATA TIER + danh sách chi nhánh (nếu chain) thì chưa audit — checklist sai type = report sai (vd bắt SAB hiện địa chỉ). Trước khi gọi API/tool: báo số call, chờ xác nhận.

**#2 Data Tier & Evidence** — Report khai báo DATA TIER ngay đầu. Không hard-fail khi thiếu MCP/API: Tier 3 luôn chạy được (Maps public + crawl website); mục cần quyền quản trị (Insights, Q&A inbox) → ⬜ THIẾU DATA + hướng dẫn khách export/screenshot, **không bịa số** (số photo views, search queries, direction requests chỉ có trong GBP Insights — không suy diễn từ ngoài). Mọi con số kèm nguồn + ngày.

**#3 Falsifiability** — Mỗi finding ❌/⚠️ kèm trường Falsifiability: "làm sao biết nếu khuyến nghị này sai?" + leading indicator kiểm chứng được (vd "đổi primary category → nếu đúng, GBP Insights search views tăng trong 2-4 tuần + SoLV grid không giảm; nếu 4 tuần giảm cả hai → revert"). Khuyến nghị không nêu được cách kiểm chứng → hạ xuống đề xuất thử nghiệm, không đưa vào P0/P1.

**#4 Surgical** — Chỉ audit website signals + GBP content. Không viết JSON-LD, không đo geo-grid, không audit technical site-level, không đánh giá link value của citation — flag + route theo bảng phân vai.

## Anti-patterns

- ❌ Chạy chung 1 checklist cho mọi business type — SAB bị bắt hiện địa chỉ, chain bị audit như single location.
- ❌ Bịa số GBP Insights (search views, direction requests) khi chỉ xem được listing public.
- ❌ Coi NAP "gần khớp" là đạt — "+84 28" vs "028", "Đường" vs "Đ." đều là lệch, liệt kê từng ký tự khác biệt.
- ❌ Khuyến nghị location pages hàng loạt từ 1 template chỉ thay địa chỉ — chính là thin duplicate mà audit phải bắt.
- ❌ Áp danh sách citation US (Yelp, YellowPages, BBB) cho khách VN.
- ❌ Đề xuất seed/mua review hoặc nhét keyword vào review — vi phạm policy, rủi ro suspension.
- ❌ Nhồi city/keyword vào GBP business name khác tên biển hiệu thật — vi phạm guidelines, rủi ro suspension.
- ❌ Tự viết/sửa LocalBusiness schema thay vì route `schema-markup-generator`.
- ❌ Hứa "lên top 3 map pack" như deliverable — đo lường là việc của SoLV baseline (`map-pack-intelligence`), audit chỉ cam kết fix signal.
- ❌ Finding không có Falsifiability vẫn xếp P0/P1.

## References & wiki

**References trong skill:**
- [references/gbp-checklist.md](references/gbp-checklist.md) — checklist GBP chi tiết per mục (categories → booking link), tiêu chí ĐẠT + cách kiểm per DATA TIER.
- [references/location-page-checklist.md](references/location-page-checklist.md) — checklist location page + store locator + phân nhánh theo business type.

**SOP nội bộ:**
- `sop/04-entity-optimization.md` — NAP consistency + Entity Home + Knowledge Panel timeline (lớp entity tổng mà local là một phần).
- `sop/09-project-timeline/` — quy trình 10 tháng: "GMB Post / Simulation — chỉ dùng khi dự án local / có GMB" (điểm chạm kích hoạt skill này).

**Wiki Semantic SEO (lớp WHY):** [[Entity Home]] · [[Central Entity]] · [[Knowledge Graph]] · [[E-A-V Framework]] · [[Consensus]] · [[Brand Entitization Playbook]] · [[User Intent]] (Local là 1 trong 7 intent types)

**Skill anh em:** `map-pack-intelligence` (nửa platform-data) · `schema-markup-generator` · `technical-seo-audit` · `backlink-research` · `seo-onpage`

## Changelog

- **v1.0.1 (2026-10-27):** dòng Output trỏ thư mục công đoạn thay cho tài liệu ngoài repo; gộp bản root vào bản này (27/10/2026).
- **v1.0 (2026-07-19):** tạo mới — nửa WEBSITE-SIGNALS của cặp skill local; khung business type 4 loại, GBP checklist 8 mục, NAP từng-ký-tự, location pages chống thin duplicate, citations lớp VN, review operations; Falsifiability bắt buộc per finding; ranh giới với map-pack-intelligence / schema-markup-generator / sop-04.
