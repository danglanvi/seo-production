---
type: sop
tier: 1
phase: gbp-local
last_updated: 2026-07-19
source_file: "skills/local-seo-audit/references/gbp-checklist.md (canonical) + raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình triển khai GMB Post - GMB Post Silo.xlsx (legacy 2021)"
items_count: 15
related:
  - "[[Central Entity]]"
  - "[[E-A-V Framework]]"
tags: [sop, tier-1, gbp, local-seo, gmb, self-checklist]
---

# Tier 1 — Self-Checklist: Google Business Profile / Local (GB-01…GB-15)

> **Khi dùng:** CHỈ cho dự án local (quy trình ghi rõ: "GMB chỉ dùng khi dự án local"). Đây là **self-check của người vận hành, nhịp hằng tháng** — audit đầy đủ (data tier T1/T2/T3, map pack, competitor) → route skill `local-seo-audit`.
> **Số items:** 15 (Setup GB-01→08 · Vận hành GB-09→15). **Scoring:** Self Score /15 → Self %.
> **Nguyên tắc REUSE:** phần Setup là tick-list RÚT GỌN — tiêu chí chi tiết + cách kiểm theo data tier nằm ở `skills/local-seo-audit/references/gbp-checklist.md` (canonical, pointer per nhóm, KHÔNG copy toàn văn). Multi-location → thêm `references/location-page-checklist.md`.

## 🔴 P0 Gate — 5 items PHẢI pass

| Gate | Item | Điều kiện |
|---|---|---|
| G1 | GB-01 | Primary category = dịch vụ chính tạo doanh thu, cụ thể nhất có thể |
| G2 | GB-06 | Booking/action links hoạt động (không 404, không về homepage chung) |
| G3 | GB-07 | NAP khớp từng ký tự với website |
| G4 | GB-09 | Post cadence sống: post gần nhất ≤30 ngày |
| G5 | GB-10 | Review response SLA đạt trong tháng |

---

## Phần 1 — Setup / Foundation (tick-list rút gọn — chi tiết ở gbp-checklist.md)

| ID | Item | Tick khi | Pointer |
|---|---|---|---|
| GB-01 | 🔴 **Categories** | Primary = dịch vụ chính tạo doanh thu, cụ thể nhất ("Phòng khám nha khoa" không phải "Phòng khám"); secondary phủ dòng dịch vụ CÓ THẬT, không nhồi. ⚠️ Đổi primary = thay đổi mạnh → kèm điều kiện revert + theo dõi 2-4 tuần | gbp-checklist §1 |
| GB-02 | **Attributes** | Mọi attribute áp dụng đều khai; KHÔNG khai attribute sai thực tế (trust risk → review xấu) | gbp-checklist §2 |
| GB-03 | **Business description** | ≤750 ký tự; 250 ký tự đầu = [[Central Entity]] (tên đúng biển hiệu) + dịch vụ chính + khu vực; không keyword stuffing / CAPS / URL / khuyến mãi | gbp-checklist §3 |
| GB-04 | **Photos nền** | ≥ mức đối thủ map pack; có ảnh mặt tiền geo-context; không stock/watermark; logo + cover đúng brand hiện hành | gbp-checklist §4 |
| GB-05 | **Products / Services** | Khai đủ dịch vụ chính, mô tả riêng, giá nếu công khai được; tên = ngôn ngữ khách tìm | gbp-checklist §7 |
| GB-06 | 🔴 **Booking / action links** | Link đặt lịch/menu/chat click thử OK; UTM gắn để đo (route đo lường → `gtv-client-report`) | gbp-checklist §8 |
| GB-07 | 🔴 **NAP khớp từng ký tự với website** | Name + Address + Phone trên GBP = trên website (và location page nếu multi-location) chính xác đến từng ký tự | location-page-checklist §B |
| GB-08 | **Chain consistency** *(chỉ khi chuỗi)* | Naming convention, ownership 1 tài khoản, category set, website link per chi nhánh, giờ per chi nhánh — nhất quán cross-branch. Không phải chain → để trống (không tính denominator) | gbp-checklist §Cross-branch |

## Phần 2 — VẬN HÀNH theo nhịp (self-check hằng tháng)

| ID | Item | Tiêu chí ĐẠT | Ghi chú |
|---|---|---|---|
| GB-09 | 🔴 **Post cadence** | Nhịp đều, baseline hàng tuần (baseline vận hành GTV — chưa phải ngưỡng nghiên cứu); post gần nhất ≤30 ngày; loại post khớp mùa vụ. Đứt >90 ngày = cờ đỏ "listing chết". Frame lợi ích theo CONVERSION với khách — KHÔNG claim post là ranking factor | gbp-checklist §5 |
| GB-10 | 🔴 **Review response SLA** | 100% review mới được trả lời ≤72h; review tiêu cực ≤24h; giọng trả lời đúng brand, không template y hệt nhau; xin review đều từ khách thật (không mua review) | SLA vận hành |
| GB-11 | **Q&A seeding** | Câu hỏi khách hỏi thật (lấy từ sales/CSKH: giá, giờ, đặt lịch, đậu xe) được owner seed + tự trả lời; KHÔNG để câu hỏi của khách chưa ai trả lời hoặc người lạ trả lời sai (mất quyền narrative) | gbp-checklist §6 |
| GB-12 | **Photo mới hằng tháng** | Mỗi tháng có ảnh thật mới upload (đảm bảo luôn có ảnh ≤6 tháng); chain: ảnh đúng chi nhánh — ảnh chi nhánh A gắn listing B = ❌ | gbp-checklist §4 (Tươi mới) |
| GB-13 | **Info drift check** | Giờ mở cửa đúng (kể cả giờ lễ/Tết sắp tới), phone/địa chỉ/link không lệch so với tháng trước; thay đổi doanh nghiệp thật → cập nhật GBP + website CÙNG LÚC (giữ GB-07) | — |
| GB-14 | **GBP Post content chuẩn** *(chắt lọc legacy)* | Post đúng loại mục (update/sự kiện/ưu đãi/sản phẩm); nội dung ~300 từ hoặc viết mới cho post (tốt hơn copy nguyên bài); tận dụng nút CTA (đặt lịch/gọi/tìm hiểu thêm) link về đúng URL cần đẩy; log link post + ngày + loại vào file quản lý | Legacy sheet "GMB Post - Cơ bản" — GIỮ phần content + log |
| GB-15 | ⚠️ **Gate risk — KHÔNG chạy tactic silo/spam** | KHÔNG triển khai "GMB Post Silo" kiểu legacy (mô phỏng internal link giữa các post, chèn 2-3 link tier-1 mỗi post, hashtag #keyword hàng loạt) — đây là tactic link-scheme era 2021, rủi ro suspend listing, không có evidence hiện hành. Post chỉ chứa link phục vụ NGƯỜI XEM (1 link về trang liên quan là đủ). Tick item này = xác nhận trong tháng KHÔNG dùng tactic trên | Legacy sheet "GMB Post Silo" — LOẠI, giữ làm cảnh báo |

---

## Legacy reconciliation — `Quy trình triển khai GMB Post - GMB Post Silo.xlsx` (2021)

| Legacy | Xử lý |
|---|---|
| Sheet "Tối ưu GMB" (audit info/photo/product per listing) | Đã cover tốt hơn bởi `gbp-checklist.md` (GB-01→08) — không mang nguyên bảng case SanF.vn sang |
| Sheet "GMB Post - Cơ bản" (quy trình đăng post 5 bước + file quản lý) | CHẮT LỌC → GB-14 (content chuẩn + log); bỏ yêu cầu hashtag #KeywordSEO (stuffing signal) |
| Sheet "GMB Post Silo" (internal link giữa post, link tier-1, dofollow farm) | ⚠️ LOẠI — gắn gate risk GB-15. Không đưa vào deliverable khách |

## Cross-refs

- Audit local đầy đủ (data tier, map pack, competitor category) → skill `local-seo-audit` (+ `map-pack-intelligence`)
- Location page multi-location / SAB / hybrid → `skills/local-seo-audit/references/location-page-checklist.md`
- LocalBusiness schema per chi nhánh → skill `schema-markup-generator` (⚠️ schema ≠ AI-citation lever — xem guardrail `tier-1-geo.md`)
- Đo lường UTM/report → skill `gtv-client-report`
