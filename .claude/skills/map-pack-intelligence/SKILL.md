---
name: map-pack-intelligence
description: "Đo map pack theo tọa độ cho khách local VN (nửa platform-data của cặp skill local; nửa kia: local-seo-audit): geo-grid rank tracking 3x3/5x5, Share of Local Voice (SoLV), competitor radius, review velocity, NAP matrix. Use when: 'đo map pack [khách]', 'SoLV baseline', 'rank Google Maps theo khu vực'."
metadata:
  version: "1.0"
---

# Map Pack Intelligence — geo-grid, SoLV, competitor radius

Đo **nửa PLATFORM-DATA** của local SEO: những gì Google Maps trả về theo từng tọa độ — không phải những gì client làm. Skill này trả lời "mình đang đứng đâu, ai đang thắng, ở khu vực nào"; việc fix (GBP content, NAP, location pages) là của `local-seo-audit` — cặp skill chạy vòng lặp: **đo baseline → fix theo audit → đo lại**.

**Vì sao 1 con số ranking không đủ với local:** kết quả map pack thay đổi theo **vị trí người tìm** — cùng query "phòng khám nha khoa", người đứng cách 500m và người đứng cách 3km thấy 2 bộ top 3 khác nhau (proximity là một trong ba trục Google công bố: relevance / distance / prominence). "Rank #2" đo từ 1 điểm là thông tin gần như vô nghĩa; cái cần là **phân bố vị trí trên lưới tọa độ** → SoLV. Lớp WHY: mỗi điểm lưới ≈ một context tìm kiếm khác nhau cho cùng [[User Intent]] local; prominence gắn với [[Central Entity]] được corroborate cross-platform ([[Knowledge Graph]], tinh thần [[Consensus]]).

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| GBP listing content, NAP onsite, location pages, citations VN, review operations phía mình | `local-seo-audit` | Skill này ĐO, không khuyến nghị fix listing — mọi action item output đổ về checklist item của local-seo-audit (vd "SoLV thấp phía Tây + đối thủ X thắng nhờ category Y → local-seo-audit Bước 1.1") |
| Citations như LINK layer (authority nguồn) | `backlink-research` | Skill này chỉ dựng bảng NAP consistency cross-platform, không đánh giá link value |
| JSON-LD / schema | `schema-markup-generator` | Không đụng |
| Đưa SoLV vào báo cáo client định kỳ | `gtv-client-report` | Skill này xuất SoLV + grid dạng data block chuẩn để report layer nhúng, không tự viết báo cáo tháng |
| Organic local ranking (blue links, không phải pack) | `seo-research` / Ahrefs rank tracking | Skill này chỉ đo map pack (local finder/3-pack) |

## Input

**Required:**
- `$BUSINESS` — tên business đúng như GBP + địa chỉ (chain: chi nhánh nào đang đo — mỗi lượt đo 1 chi nhánh).
- `$QUERIES` — 3-7 query local đại diện ("nha khoa quận 3", "phòng khám nha khoa gần đây"…). Chưa có → đề xuất từ dịch vụ chính + confirm.

**Optional:**
- `$GRID` — cỡ lưới + bán kính; không có → đề xuất theo bảng dưới.
- `$COMPETITORS` — đối thủ nghi vấn; không có → lấy từ chính kết quả grid (ai xuất hiện nhiều nhất).
- `$BASELINE_FILE` — file đo kỳ trước (để so before/after).

**Bảng grid đề xuất theo loại hình** (baseline vận hành GTV — chưa phải ngưỡng nghiên cứu chốt, điều chỉnh theo mật độ đô thị):

| Loại hình | Lưới | Bán kính | Lý do |
|---|---|---|---|
| Dịch vụ cự ly gần, mật độ cao (F&B, cafe, nha khoa nội đô) | 5x5 | 2-3 km | Proximity quyết định mạnh, cần độ phân giải cao |
| Showroom / dịch vụ đáng đi xa (ô tô, nội thất, phòng khám chuyên khoa) | 5x5 | 5-10 km | Catchment rộng hơn |
| SAB (đến nhà khách) | 5x5 | theo service area khai trên GBP | Đo đúng vùng phục vụ, không đo quanh địa chỉ ẩn |
| Spot-check nhanh / budget thấp | 3x3 | như trên | 9 điểm đủ thấy pattern thô |

**Data ladder (khai báo TIER ngay đầu output):**

| Tier | Điều kiện | Data |
|---|---|---|
| **Tier 1** | DataForSEO Business Data / SERP API hỗ trợ tọa độ per call | Máy đo full grid × queries; lặp lại được, so kỳ được |
| **Tier 2** | Không API, tự đo tay được | Search ẩn danh theo grid (hướng dẫn chuẩn ở [references/geo-grid-manual.md](references/geo-grid-manual.md): giả lập vị trí qua devtools/UULE, hoặc đi thực địa spot-check 3-5 điểm) + export GBP Insights của khách |
| **Tier 3 (đường lùi cuối)** | Chỉ nhận được screenshot khách gửi | Khách chụp Maps tại các vị trí theo hướng dẫn; grid thưa, ghi rõ giới hạn — vẫn ra được SoLV thô |

## Workflow

### Bước 0 — Đọc references + chốt phép đo (gate cứng, chờ xác nhận)

1. Đọc [references/geo-grid-manual.md](references/geo-grid-manual.md).
2. Xác định **DATA TIER** + business type (lấy từ `local-seo-audit` nếu đã chạy — SAB đo theo service area, không đo quanh địa chỉ).
3. Chốt: `$QUERIES` (3-7), `$GRID` (cỡ + bán kính theo bảng), chi nhánh nào (nếu chain), có baseline cũ không.
4. Báo chi phí: Tier 1 = số call ≈ điểm lưới × queries (5x5 × 5 queries = 125 call) → **chờ user xác nhận** rồi mới chạy. Tier 2 = ước thời gian đo tay (~2-3 phút/điểm/query) → đề xuất thu hẹp queries nếu quá lớn.

### Bước 1 — Đo grid

- Per điểm lưới × per query, ghi: **vị trí của mình trong map pack/local finder** (1-3 = trong pack; 4-20 = ngoài pack; ∅ = không xuất hiện) + **top 3 businesses tại điểm đó**.
- Tier 1: gọi API theo tọa độ. Tier 2: theo protocol trong references — mỗi điểm phải ẩn danh (incognito, không đăng nhập) + đúng tọa độ giả lập. Tier 3: nhận screenshot, đọc + nhập bảng.
- Ghi **ngày giờ đo** — kết quả local dao động theo giờ; các kỳ đo sau cùng khung giờ.

### Bước 2 — Tính SoLV + đọc pattern grid

1. **SoLV per query** = số điểm lưới mình trong top 3 ÷ tổng điểm lưới đo được (%). **SoLV tổng** = trung bình các query (ghi kèm per-query, không chỉ số gộp).
2. Vẽ bảng grid ký hiệu (🟢 top 3 · 🟡 4-10 · 🔴 >10/∅) per query — pattern đọc được ngay: thắng quanh nhà, chết hướng nào, lỗ hổng khu nào.
3. Ghi **bán kính hiệu dụng** ước lượng: khoảng cách xa nhất còn vào top 3 (theo hướng) — đây là số mô tả hiện trạng, không phải hằng số.

### Bước 3 — Competitor radius mapping

1. Từ data Bước 1, đếm tần suất từng đối thủ trong top 3 toàn lưới → 3-5 đối thủ chính + SoLV của họ (so sánh được trực tiếp với mình).
2. Map **vùng thắng của từng đối thủ**: đối thủ A phủ phía Bắc, B phủ toàn lưới (prominence mạnh — thắng cả điểm xa vị trí họ), C chỉ thắng sát địa chỉ (thuần proximity).
3. Đọc nghĩa: đối thủ thắng ở điểm GẦN MÌNH hơn họ → không phải proximity mà là relevance/prominence gap → việc của `local-seo-audit` (category, review, listing). Ghi khoảng cách từ điểm lưới đến địa chỉ mỗi đối thủ khi kết luận.

### Bước 4 — Review velocity comparison

- Mình vs 3-5 đối thủ Bước 3: tổng review, rating, **review mới/tháng trong 3-6 tháng gần nhất** (Tier 1: API; Tier 2/3: đếm tay từ tab review — sample gần nhất, ghi rõ phương pháp đếm).
- Output: bảng + kết luận nhịp ("đối thủ A +12 review/tháng, mình +2 → gap vận hành xin review" → đổ về local-seo-audit Bước 5).

### Bước 5 — Cross-platform NAP matrix

- Bảng đồng nhất trên 4 platform: **Google Maps / Apple Maps / Bing Places / Facebook** — mỗi ô: Name / Address / Phone / trạng thái listing (đã claim? duplicate?).
- Apple Maps + Bing: nhiều business VN chưa từng claim — ⬜ chưa có listing cũng là finding (VN: ưu tiên thấp hơn Google + Facebook, ghi rõ để khách không over-invest).
- Lệch NAP phát hiện được → action đổ về local-seo-audit Bước 2/4 (NAP chuẩn = GBP).

### Bước 6 — Render output + đổ action

- Theo skeleton Output. Mọi action item **trỏ về checklist item cụ thể của `local-seo-audit`** — skill này không tự đề khuyến nghị listing ngoài phạm vi đo.
- Có `$BASELINE_FILE` → thêm cột delta (SoLV kỳ này vs kỳ trước, cùng grid + cùng khung giờ mới so được).
- Đề xuất nhịp đo lại: sau đợt fix 4-6 tuần, hoặc theo chu kỳ báo cáo (`gtv-client-report` nhúng block SoLV).

## Output

File: tài liệu nội bộ «<client>_Map-Pack-SoLV_<YYYY-MM>_v1» (ngoài repo, hỏi Lead/Vincent).

```markdown
# Map Pack Intelligence — <business> (chi nhánh <X>)
> Ngày đo: YYYY-MM-DD HH:mm · DATA TIER: <1/2/3 + phương pháp> · Grid: <5x5, bán kính r km> · Queries: <n>

## 1. SoLV Baseline
| Query | SoLV (top 3) | Điểm 🟢/🟡/🔴 | Ghi chú pattern |
|---|---|---|---|
**SoLV tổng: xx%** · Bán kính hiệu dụng ước lượng: <r km, hướng>

## 2. Bảng grid per query
### "<query>"
🟢🟢🟡🔴🔴
🟢🟢🟢🟡🔴  (mỗi ô kèm chú thích tọa độ trong phụ lục)
...

## 3. Competitor map
| Đối thủ | SoLV | Vùng thắng | Đọc nghĩa (proximity vs prominence) | Khoảng cách địa chỉ |
|---|---|---|---|---|

## 4. Review velocity
| Business | Tổng review | Rating | Review mới/tháng (3-6m) |
|---|---|---|---|

## 5. Cross-platform NAP matrix
| Platform | Name | Address | Phone | Claimed? | Duplicate? |
|---|---|---|---|---|---|

## 6. Action → local-seo-audit
| # | Finding từ data | Đổ về checklist item | Kỳ vọng đo lại (leading indicator) |
|---|---|---|---|

## 7. Phương pháp & giới hạn
- Cách đo, khung giờ, điểm không đo được, caveat tier · Kỳ đo lại đề xuất: <ngày>
```

## Behavior Gates

**#1 Think Before** — Bước 0 là gate cứng: chưa chốt queries + grid + tier + chi nhánh thì chưa đo. Tier 1: báo số call (grid × queries), chờ xác nhận — 125 call không phải nhỏ. Tier 2: báo thời gian đo tay, đề xuất thu hẹp trước khi bắt khách/team đo 175 lượt search.

**#2 Data Tier & Evidence** — Khai báo DATA TIER + phương pháp + ngày giờ đo ngay đầu output. Không hard-fail thiếu MCP/API: Tier 2 (đo tay theo protocol) và Tier 3 (screenshot khách) luôn chạy được — nhưng số từ grid thưa/screenshot ghi rõ "SoLV thô, n điểm". 🔴 KHÔNG bịa ô lưới không đo được — ô thiếu = ⬜, mẫu số SoLV chỉ tính ô có data. Không so SoLV giữa 2 kỳ khác grid/khác khung giờ.

**#3 Measurement honesty** — SoLV là metric mô tả phân bố, không phải lời hứa: không quy đổi "SoLV 60% = X khách". Kết luận nguyên nhân (proximity vs prominence) phải kèm evidence khoảng cách (Bước 3.3); không kết luận "vì thiếu review" khi chưa có bảng Bước 4. Mỗi action ở mục 6 kèm leading indicator đo lại được — đây là nguồn Falsifiability cho các finding bên `local-seo-audit`.

**#4 Surgical** — Chỉ đo + đọc data. Không audit listing, không viết khuyến nghị content GBP, không tự viết báo cáo client — action đổ về `local-seo-audit`, số đổ về `gtv-client-report`.

## Anti-patterns

- ❌ Báo "rank #N trên Maps" như một con số duy nhất — không có grid thì không có ranking local đáng tin.
- ❌ Đo tay khi đang đăng nhập Google / không ẩn danh / không set vị trí — kết quả cá nhân hóa, vứt.
- ❌ Bịa/ngoại suy ô lưới không đo được để bảng đẹp.
- ❌ So sánh SoLV 2 kỳ khác cỡ grid, khác bán kính, khác khung giờ rồi tuyên bố tăng/giảm.
- ❌ Phát biểu ngưỡng grid (5x5/2km…) như chuẩn nghiên cứu — đây là baseline vận hành GTV, ghi rõ.
- ❌ Kết luận "đối thủ thắng vì gần hơn" mà không ghi khoảng cách thật từ điểm lưới tới địa chỉ họ.
- ❌ Quy đổi SoLV ra doanh thu/khách hàng trong deliverable.
- ❌ Lấn sang khuyến nghị sửa listing/website chi tiết — chỉ trỏ về checklist item của local-seo-audit.
- ❌ Bắt khách claim đủ 4 platform như việc ưu tiên cao ở VN — Apple/Bing là hygiene, Google + Facebook mới là mặt trận.
- ❌ Chạy đo cho chain bằng 1 lưới chung cho mọi chi nhánh — mỗi chi nhánh 1 lưới riêng quanh vị trí nó.

## References & wiki

**References trong skill:**
- [references/geo-grid-manual.md](references/geo-grid-manual.md) — protocol đo tay chuẩn: dựng lưới tọa độ, giả lập vị trí (devtools sensor override / UULE), đi thực địa spot-check, template ghi số + hướng dẫn khách tự chụp screenshot (Tier 3).

**SOP nội bộ:**
- `sop/04-entity-optimization.md` — prominence cross-platform là một phần entity corroboration.
- `sop/09-project-timeline/` — điểm chạm "dự án local / có GMB" trong quy trình 10 tháng.

**Wiki Semantic SEO (lớp WHY):** [[User Intent]] (Local intent type) · [[Central Entity]] · [[Knowledge Graph]] · [[Consensus]] · [[Entity Home]] · [[Brand Entitization Playbook]]

**Skill anh em:** `local-seo-audit` (nửa website — nhận action) · `backlink-research` (citations link layer) · `gtv-client-report` (nhúng SoLV vào báo cáo) · `schema-markup-generator`

**Nguồn ngoài:** ba trục local ranking relevance/distance/prominence — support.google.com/business/answer/7091 (doc Google hiện hành, đối chiếu khi cite).

## Changelog

- **v1.0 (2026-07-19):** tạo mới — nửa PLATFORM-DATA của cặp skill local; geo-grid 3x3/5x5 + bảng bán kính theo loại hình, SoLV (% điểm lưới top 3), competitor radius mapping (proximity vs prominence), review velocity comparison, cross-platform NAP matrix; data ladder API → đo tay UULE/thực địa → screenshot; action đổ về local-seo-audit, số đổ về gtv-client-report.
