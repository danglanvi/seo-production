---
type: sop
tier: 1
phase: structure-website
last_updated: 2026-07-19
source_file: "raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/6. Cấu Trúc website/Checklist triển khai cấu trúc website.xlsx"
items_count: 19
related:
  - "[[Topical Map]]"
  - "[[Core Section]]"
  - "[[Outer Section]]"
  - "[[URL SEO]]"
  - "[[Internal Linking Rules and Strategy]]"
  - "[[Faceted Navigation]]"
  - "[[Entity Home]]"
tags: [sop, tier-1, structure, website-architecture, self-checklist]
---

# Tier 1 — Self-Checklist: Cấu trúc Website (ST-01…ST-19)

> **Khi dùng:** Công đoạn cấu trúc website (T1 → 15 ngày đầu T2) — người THIẾT KẾ cấu trúc (SEO lead / kỹ thuật SEO) tự check khi làm, TRƯỚC khi đóng gói deliverable.
> **Phân biệt với `gate-structure-wireframe.md`:** gate = check **ĐỦ** deliverable trước khi gửi khách (1 trang, 10-15 items) · checklist này = check **ĐÚNG** khi thiết kế (full, 19 items). Chạy checklist này xong mới chạy gate.
> **Số items:** 19. **Scoring:** Self Score /19 → Self %. Review 3 tầng như các checklist Tier 1 khác.
> **Nguồn:** `Checklist triển khai cấu trúc website.xlsx` (2020) + `Tối ưu Ecommerce.xlsx` (2023) — modernize theo wiki (topical map, faceted, pagination chuẩn hiện hành). Cột **Nguồn** ghi legacy / wiki / mới. ⚠️ Legacy 2023 có claim outdated về pagination (canonical về trang 1 + disallow robots) — ST-11 là chuẩn ĐÃ SỬA.
> **Ranh giới:** wireframe/element từng trang → `tier-1-ux-ui.md` · layout semantic per page → `tier-1-visual-semantic.md` · link plan chi tiết khi vận hành → skill `internal-linking`.

## 🔴 P0 Gate — 6 items PHẢI pass

| Gate | Item | Điều kiện |
|---|---|---|
| G1 | ST-01 | Cấu trúc sinh từ topical map — Core/Outer rõ, mỗi nhóm keyword cam kết có URL |
| G2 | ST-04 | 1 intent = 1 URL — không node trùng nghĩa/cannibalization |
| G3 | ST-07 | URL sạch: không parameter rác index, canonical hóa 1 phiên bản |
| G4 | ST-08 | Click depth ≤3 tới mọi URL SEO |
| G5 | ST-11 | Pagination theo chuẩn hiện hành (không canonical về trang 1, không chặn robots) |
| G6 | ST-12 | Faceted navigation có chiến lược index rõ từng loại facet |

---

## Phần A — Kiến trúc tầng khớp Topical Map

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| ST-01 | 🔴 **Cấu trúc sinh từ topical map** | Cây cấu trúc đi ra từ [[Topical Map]] đã duyệt: [[Core Section]] (nhóm gần money/service) vs [[Outer Section]] (hinterland informational) phân vùng rõ; MỌI nhóm keyword cam kết (cả core lẫn outer) có URL tương ứng — [[URL SEO]] là đơn vị cam kết; không section nào "mồ côi" ngoài map | Wiki (modernize bước "liệt kê top navigation + item bằng Ahrefs/đối thủ" 2020 R5-R6) |
| ST-02 | **Đúng loại trang theo intent** | Từng keyword/node xét intent SERP để chốt loại trang: danh mục vs blog vs sản phẩm vs page dịch vụ — không tạo danh mục cho keyword intent bài viết và ngược lại; keyword SEO chung được thì không tách URL riêng | Legacy (2020 R4, R9: "intent của keyword đó có đúng là danh mục không hay blog, sp") |
| ST-03 | **Phân tầng theo modifier + silo/cluster logic** | Keyword phân tầng theo modifier (2020 R10); nhóm trang cùng chủ đề tổ chức thành silo vật lý / cluster có logic (dựa đối thủ + logic + định hướng — 2020 R11); cluster khớp [[Semantic Content Network]] đã thiết kế, benchmark thị trường mạnh nhất (ưu tiên ngoài nước nếu ngành cho phép — Ecom 1.0) | Legacy + wiki |
| ST-04 | 🔴 **1 intent = 1 URL** | Check duplicate/trùng nghĩa giữa mọi node (2020 R7): 2 node cùng intent → gộp; chọn phiên bản keyword volume cao nhất làm đại diện node (2020 R8); không 2 URL cạnh tranh cùng 1 query network | Legacy (2020 R7-R8) + wiki [[Query Network]] |

## Phần B — URL Conventions

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| ST-05 | **URL ngắn, sạch, đúng convention** | URL: ngắn gọn thể hiện nội dung trang (Ecom 3.0), không dấu tiếng Việt, lowercase toàn bộ, hyphen phân tách (không underscore/space), không từ thừa (stop words rác) | Legacy (Ecom 3.0) + MỚI (chuẩn hóa lowercase/không dấu) + wiki [[URL Slugs]] |
| ST-06 | **Chọn phẳng vs phân tầng CÓ LÝ DO** | Quyết định cấu trúc URL phẳng hay silo-URL được ghi lý do (2020 R12): phẳng khi keyword trang con (dài) lẫn danh mục cha (ngắn) khó SEO ngang nhau (Ecom 3.0); top-navigation thường phẳng, từ category cụ thể trở xuống mới phân tầng; không quá nhiều tầng URL (≤3 segment sau domain là default) | Legacy (2020 R12 + Ecom 3.0) |
| ST-07 | 🔴 **Không parameter rác + canonical hóa 1 phiên bản** | URL index không chứa parameter rác (session, sort, tracking); chuẩn hóa 1 phiên bản duy nhất: https, www/non-www thống nhất, trailing slash thống nhất, các biến thể 301 hoặc canonical về bản chính | MỚI (2020/2023 chưa có mục này) |

## Phần C — Click Depth & Internal Link Zones

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| ST-08 | 🔴 **Click depth ≤3** | Từ trang chủ tới MỌI URL SEO ≤3 click qua link crawlable; URL SEO quan trọng nhất (core/money) ≤2; verify bằng crawl tool trên cây cấu trúc đã lên, không ước lượng | MỚI + wiki [[Cost of Retrieval]] |
| ST-09 | **Internal link zones thiết kế sẵn** | 5 zone link được thiết kế NGAY trong cấu trúc (không đợi vận hành): nav (URL SEO chính) · footer (thương mại + chính sách) · contextual in-content (giữa các node theo [[Contextual Bridge]]) · related/sibling (sub-cate, cùng cấp, blog bổ trợ) · breadcrumb; mỗi zone ghi rõ loại trang nào link đi đâu — chi tiết rule theo [[Internal Linking Rules and Strategy]] | Wiki + legacy (UXUI xlsx: link sub-cate/cùng cấp/blog bổ trợ đã là zone design) |
| ST-10 | **First link count + anchor plan cấu trúc** | Với mỗi URL đích, link ĐẦU TIÊN xuất hiện trong DOM mang anchor đúng chủ đích (nguyên tắc First Link Count — Ecom 1.0); anchor điều hướng trong nav/breadcrumb dùng tên node nhất quán, không mỗi nơi 1 kiểu | Legacy (Ecom 1.0: "lưu ý nguyên tắc First Link Count & Anchor text") |

## Phần D — Pagination & Faceted Navigation

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| ST-11 | 🔴 **Pagination chuẩn hiện hành** | Trang phân trang: **self-canonical từng trang** (KHÔNG canonical về trang 1), KHÔNG disallow trong robots.txt, page links `<a href>` crawlable; rel=next/prev không còn là tín hiệu — bỏ dựa vào nó. ⚠️ Đây là mục SỬA legacy: Ecom 2023 ghi "pagination phải có canonical và disallow ở robots.txt" — outdated, làm theo sẽ chặn crawl sản phẩm | MỚI (sửa legacy Ecom 2.0) |
| ST-12 | 🔴 **Faceted navigation có chiến lược index** | Mỗi loại facet có quyết định rõ ghi thành bảng: facet CÓ search demand + intent riêng → mở thành facet landing/sub-cate index được (có URL tĩnh, content); facet chỉ là chức năng lọc → noindex hoặc chặn param, không nhận internal link ưu tiên; tránh bùng nổ tổ hợp facet index ([[Index Pollution]]) | Wiki [[Faceted Navigation]] + legacy (Ecom 5.0: demand thấp → để ở bộ lọc) |

## Phần E — Breadcrumb, Schema & Trang bắt buộc

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| ST-13 | **Breadcrumb + schema khớp cấu trúc** | Breadcrumb ở TỪNG tầng website (Ecom 3.0), đường dẫn khớp cây cấu trúc đã chốt (không khớp = cấu trúc chưa chốt xong); markup BreadcrumbList (JSON-LD chi tiết → skill `schema-markup-generator`) | Legacy (Ecom 3.0) + MỚI (schema) |
| ST-14 | **Trang bắt buộc có mặt trong cấu trúc** | Cây cấu trúc có đủ trang entity requirements: Giới thiệu, Liên hệ, Chính sách (bảo mật + đổi trả/vận chuyển nếu bán hàng), Đại lý/Showroom/Khu vực phục vụ nếu có hiện diện địa lý; các trang này nằm trong footer nav — thiếu = trừ trust cả site | MỚI + wiki [[Entity Home]] |
| ST-15 | **Entity Home được chỉ định** | 1 URL được chốt làm [[Entity Home]] của brand (thường trang Giới thiệu hoặc trang chủ): NAP nhất quán, schema Organization trỏ sameAs đủ profile; mọi trang khác nói về brand → link về Entity Home | Wiki (mới so với legacy 2020/2023) |

## Phần F — E-commerce riêng (nguồn chính: Tối ưu Ecommerce 2023)

> Site không phải e-com: bỏ Phần F, mẫu số Self Score còn /15.

| ID | Item | Tiêu chí ĐẠT | Nguồn |
|---|---|---|---|
| ST-16 | **Category tree theo demand** | Mỗi danh mục/sub trong tree có demand thật (volume + intent danh mục); phân tầng khớp cách thị trường trong/ngoài nước làm (ưu tiên benchmark ngoài nước — Ecom 1.0); danh mục không có demand riêng → xóa khỏi tree | Legacy (Ecom 1.0, 5.0) |
| ST-17 | **Sub-category vs filter decision** | Từng sub-cate ứng viên xét: search demand đủ + user chủ động search → sub-cate riêng (tối ưu như category — Ecom 5.0); chỉ là tính năng lọc khi đã vào page → để ở filter; sub-cate giữ tính nhất quán với category chính | Legacy (Ecom 5.0) |
| ST-18 | **Variant handling** | Chốt chiến lược biến thể ngay từ cấu trúc: variant có demand search riêng (màu/size/model được search) → URL riêng index; variant chỉ là lựa chọn mua → gộp trong 1 PDP (selector đổi giá/ảnh), không đẻ URL trùng nội dung | MỚI (legacy chưa cover) |
| ST-19 | **Out-of-stock policy** | Quy tắc xử hết hàng ghi thành policy trước khi vận hành: hết TẠM → giữ 200 + thông báo + gợi ý SP thay thế (không xóa URL đang rank); ngừng VĨNH VIỄN → 301 về SP/danh mục thay thế gần nhất, không có nơi thay thế → 410; không để trang chết trắng | MỚI (legacy chưa cover) |

---

## Quy trình tick

1. Thiết kế cấu trúc theo trình tự legacy 2020 vẫn đúng: chọn website tham khảo → liệt kê node (Ahrefs + đối thủ) → phân tầng → URL → link zones. Vừa làm vừa tick ST-01→ST-19.
2. 6 items 🔴 P0 fail bất kỳ → chưa đóng gói deliverable.
3. Checklist này pass → chạy `gate-structure-wireframe.md` (check đủ bộ deliverable) → mới gửi khách.
4. Ghi Self % + Self Note; cấu trúc đổi giữa chừng dự án (thêm section, đổi silo) → tick lại Phần A-D cho phần thay đổi.
