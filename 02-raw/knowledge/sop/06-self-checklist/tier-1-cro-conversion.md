---
type: sop
tier: 1
phase: cro-conversion
last_updated: 2026-09-13
source_file: "raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/CONVERSION/Checklist Onsite tối ưu conversion - GTV SEO.xlsx"
changelog: "v2026.09.4 (2026-09-13): G1 cho phép research/blocker/brief sửa lỗi; CR-08 tách blocker P0; CR-14 +INP/CLS p75; CR-15 rollout có theo dõi + 1 giả thuyết/treatment + feasibility; CR-16 thành diagnostic. Nguồn: wiki Inbound Marketing (concepts/cro), Vincent duyệt hướng 12/09."
items_count: 19
related:
  - "[[Website Functions]]"
  - "[[Internal Linking Rules and Strategy]]"
  - "[[Centerpiece Annotation]]"
tags: [sop, tier-1, cro, conversion, tracking, self-checklist]
---

# Tier 1 — Self-Checklist: CRO / Conversion (CR-01…CR-19)

> **Khi dùng:** 3 thời điểm trong quy trình dự án — **Phần A** chạy chung đợt cấu trúc + UX/UI (T2-T3), **Phần B** chạy trên landing thương mại đã có traffic + ranking (T8-T10), **Phần C** chạy liên tục từ cuối P2 khi đã có tracking data.
> **Số items:** 19 (A: CR-01→07 · B: CR-08→15 · C: CR-16→19)
> **Scoring:** Self Score /19 → Self %. Review 3 tầng như các checklist Tier 1 khác (Self 100% → SEO EX verify → Lead random 25-30%).
> **Nguồn chính:** `Checklist Onsite tối ưu conversion - GTV SEO.xlsx` (2025 — sheets "Checklist Onsite" + "Dạng tracking"). Cột **Legacy** ghi rõ item nào GIỮ / SỬA / MỚI so với bản gốc.

## 🔴 P0 Gate — 3 điều kiện PHẢI pass

| Gate | Item | Điều kiện |
|---|---|---|
| G1 | CR-06 + CR-07 | **Tracking chuyển đổi gắn xong + verify ≤ T3** — mốc bắt buộc của quy trình. Chưa có tracking = mọi tối ưu sau đó không đo được → KHÔNG công bố CR/uplift, KHÔNG A/B (Phần B mục đo số, Phần C). Vẫn làm research, báo blocker P0 và brief sửa lỗi (v2026.09.4). |
| G2 | CR-10 | Mỗi landing thương mại có **1 CTA chính duy nhất**, nổi bật nhất trang. |
| G3 | CR-19 | **Funnel đo được** — xác định được điểm drop-off lớn nhất từ tracking data. |

---

## Phần A — Site-wide (T2-T3, làm chung đợt cấu trúc + UX/UI)

Nguyên tắc: từng element site-wide phải trả lời được "element này phục vụ chuyển đổi gì?" — không có câu trả lời → bỏ hoặc hạ cấp.

| ID | Item | Tiêu chí ĐẠT | Legacy |
|---|---|---|---|
| CR-01 | **Header / Navigation** | Nav bar chọn lọc thông tin (không nhồi mọi menu); CTA liên hệ (click-to-call / Zalo) hiển thị trong header trên MỌI trang; header sticky hoặc CTA luôn trong tầm với mobile | GIỮ (2.0-2.3) |
| CR-02 | **Footer có mục đích** | Footer chứa: liên hệ + link trang thương mại chính + trust info (chính sách, cam kết). Footer không phải bãi rác link | MỚI |
| CR-03 | **Hệ CTA phân cấp** | Bộ nút site-wide (gọi, Zalo, Messenger, form) có phân cấp chính-phụ rõ: nút chính màu nổi nhất (màu nóng/tương phản), to nhất, ở trên; nút phụ không cạnh tranh thị giác | SỬA (6.2, 6.3 — nâng từ per-page lên design system site-wide) |
| CR-04 | **Form chuẩn hệ thống** | Form dùng chung 1 chuẩn: field tối thiểu, label rõ, có trạng thái thành công riêng (thank-you page / success state) để bắn event đo được | MỚI |
| CR-05 | **Chat / widget hoạt động** | Live chat / Zalo widget hoạt động thật (test gửi thử), KHÔNG che CTA chính trên mobile | GIỮ (14) |
| CR-06 | 🔴 **Measurement plan + tracking gắn xong ≤ T3** | Event theo contract của skill `cro-measurement-plan` (v2026.09.4): dịch vụ = `generate_lead` (sau kết quả nghiệp vụ, không phải click/HTTP 200) + `click_to_call` + `click_zalo` + `click_messenger`; ecommerce thêm `add_to_cart` + `purchase` (`transaction_id`, dataLayer sau backend); job thêm `apply_start` + `application_complete`. Site đã có tên legacy (`form_submit`, `zalo`, `messenger` — sheet "Dạng tracking") → ghi **mapping cũ→mới + ngày chuyển**, không tạo event trùng để đạt item này. Mốc bắt buộc: plan bàn giao trước hết T3 | SỬA (v2026.09.4: contract mới + mapping legacy) |
| CR-07 | 🔴 **Sự kiện verify đo được** | Test bắn event thật (submit form thử, click call, mở chat) → thấy trong GA4 DebugView/Realtime. Heatmap tool (nếu trong scope) đã gắn | GIỮ (note G3 legacy: "GA4 sự kiện + bản đồ nhiệt") |

## Phần B — Per landing page (T8-T10)

Chỉ chạy trên **landing thương mại đã có traffic + ranking** — không tối ưu trang chưa ai vào.

| ID | Item | Tiêu chí ĐẠT | Legacy |
|---|---|---|---|
| CR-08 | **Chọn trang theo ROI** | Danh sách landing ưu tiên = giao của (traffic cao × ranking tốt × ngách ROI cao nhất của khách). Có danh sách được duyệt trước khi **tối ưu** (P1/P2). **Blocker P0 site-wide** (form không gửi, nút gọi không `tel:`, checkout lỗi, `purchase` không bắn) báo và sửa bất kể ranking — nằm ngoài CR-08 (v2026.09.4) | GIỮ + SỬA (tách blocker P0) |
| CR-09 | **Above-fold value proposition** | Không cần scroll vẫn thấy: bán gì + 3 điểm vượt trội (USP dạng icon/bullet, không chỉ thông số kỹ thuật) + CTA chính | SỬA (5 Buy Box + 8 USP — gộp thành 1 tiêu chí above-fold) |
| CR-10 | 🔴 **CTA chính duy nhất + vị trí** | 1 CTA chính/trang, khớp hành vi tệp khách (Zalo/gọi/form/mua); xuất hiện above-fold + lặp lại sau mỗi section dài; CTA phụ tồn tại nhưng không tranh vai chính | GIỮ (6.1, 6.4) |
| CR-11 | **Trust elements** | Có ≥2 trong: review khách thật (sao + số lượt), case/công trình thực tế, chứng nhận/đánh giá từ trang uy tín, cam kết ngành hàng cụ thể (không cam kết chung chung) | GIỮ + GỘP (3, 9, 10) |
| CR-12 | **Form độ dài hợp lý** | Số field = tối thiểu đủ để sales xử lý (thường 3-4); mobile dùng đúng input type (`tel`, `email`); không bắt tạo tài khoản để liên hệ | MỚI (legacy không có) |
| CR-13 | **FAQ mua hàng + gợi ý liên quan** | FAQ giải đáp trở ngại mua thật (giá, bảo hành, giao hàng); sản phẩm/dịch vụ liên quan được CHỌN LỌC theo hành vi khách, không auto-random. Pop-up exit-intent = optional test, chỉ trên trang trọng điểm | GIỮ (11, 12, 13) |
| CR-14 | **Tốc độ + mobile** | Field data p75 trên landing thương mại: LCP ≤ 2.5s, **INP ≤ 200ms, CLS ≤ 0.1** (không chỉ Lighthouse một lần); script chat/heatmap/A/B tool không làm INP form vượt ngưỡng; CTA bấm được bằng ngón cái (≥44px chuẩn nội bộ); click-to-call hoạt động thật trên mobile (`tel:` link) | GIỮ + SỬA (15 + mobile; v2026.09.4 thêm INP/CLS p75) |
| CR-15 | **Triển khai có theo dõi / A/B khi đủ mẫu** | Mặc định: sửa lỗi + rollout có theo dõi (annotation ngày deploy, cùng mẫu số, cửa sổ ≥4 tuần trọn, ghi "quan sát trước/sau"). A/B chỉ khi tracking PASS + feasibility có số (baseline, MDE, mẫu cần, ngày ước tính — `cro-audit/references/experiment-lite.md`); **một giả thuyết = một treatment** (gói thay đổi kết luận cho cả gói); primary chốt trước, kiểm SRM, không dừng sớm; input ưu tiên lấy từ CR-19. Không "test 14 ngày đủ" | SỬA (v2026.09.4: thay "1 biến số" + thêm rollout có theo dõi; note G4 legacy → test nội bộ) |

## Phần C — Conversion path (liên tục từ cuối P2)

| ID | Item | Tiêu chí ĐẠT | Legacy |
|---|---|---|---|
| CR-16 | **Đường đi ≤ 3 bước (diagnostic)** | Từ organic landing → conversion point (form/gọi/giỏ hàng) ≤ 3 click là mặc định để soi; mỗi bước có CTA chỉ đường rõ. Vượt 3 click **không tự động là lỗi**: chấm theo task success / dead-end / nhập lại; giữ bước có ích (bảng giá, so sánh) phải khai lý do (v2026.09.4) | MỚI → SỬA (diagnostic, không phải chuẩn cứng — NN/g 3-click rule) |
| CR-17 | **Không dead-end** | MỌI page có next action: blog → sản phẩm liên quan/slider; thank-you → bước tiếp theo; 404 → điều hướng về trang giá trị | GIỮ (mục BLOG legacy: "chèn giới thiệu sản phẩm liên quan / slider") + MỞ RỘNG |
| CR-18 | **Internal link blog → thương mại đúng ngữ cảnh** | Bài blog cùng cụm chủ đề link về trang thương mại với anchor tự nhiên, đặt SAU khi đã justify trong nội dung (không nhét đầu bài). Lập link plan → route skill `internal-linking` | MỚI (route skill) |
| CR-19 | 🔴 **Đo funnel drop-off** | Từ cuối P2: dựng funnel GA4 (landing → bước giữa → conversion) cho nhóm landing ưu tiên, cùng mẫu số/population; xác định điểm rơi lớn nhất (không tự coi là lỗi nếu là bước qualification) → feed vào CR-15. **Khi G1 chưa PASS hoặc offsite không có callback (apply/ATS):** ghi "G3 pending — đo tới <event cuối đo được>", không giả PASS; research/brief phần được phép vẫn hoàn tất | MỚI → SỬA (v2026.09.4: trạng thái pending) |

---

## Legacy reconciliation — items xlsx KHÔNG mang sang

- **Mục 1.0 "Chọn giao diện phù hợp mặt hàng"** — quyết định design-time, không phải self-check lặp lại → thuộc đợt UX/UI T2-T3, không thành item.
- **Mục 4.1-4.4 (Carousel, hình ảnh, video, thị giác nâng cao)** — thuộc visual semantic, đã cover ở `sop/07` + skill `visual-semantic-seo` / `image-seo-optimize`; tránh duplicate.
- **Mục 7.1-7.4 (nội dung mô tả sản phẩm)** — thuộc pipeline content (tier-1-content-writing + skill `semantic-content-writing`).
- **CATEGORY PAGE items (1.0-11.0)** — phần lớn là onpage/visual (Title/H1, bộ lọc, box sản phẩm) → `sop/08` P-series + `visual-semantic-seo` (PLP pattern); yếu tố conversion của category (CTA "xem chi tiết", sao + số lượt) đã hấp thụ vào CR-03/CR-11 ở cấp hệ thống.

## Wiki / skill cross-refs

- CTA, form, function hoạt động → [[Website Functions]] (broken function = negative signal, sop/08 P22)
- Internal link plan → [[Internal Linking Rules and Strategy]] + skill `internal-linking`
- Above-fold / visual hierarchy → [[Centerpiece Annotation]] + `sop/07-visual-semantic.md`
- Đo lường / báo cáo khách → skill `gtv-client-report`
