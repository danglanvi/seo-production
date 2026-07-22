---
type: sop
tier: gate
phase: structure-wireframe
last_updated: 2026-07-19
source_file:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/6. Cấu Trúc website/Checklist triển khai cấu trúc website.xlsx
items_count: 12
tags: [sop, gate, structure, wireframe, pre-handoff, self-checklist]
---

# Gate — Cấu trúc website & Wireframe (pre-handoff cho khách duyệt)

> **Khi dùng:** NGAY TRƯỚC khi gửi khách duyệt bộ cấu trúc + wireframe. **Mốc cứng: 15 ngày đầu T2** — trễ mốc này là dây chuyền trễ cả quý (coder, content, onpage đều chờ cấu trúc).
> **Số items:** 12 (GS-01…GS-12). **P0: TẤT CẢ — gate 100%**, fail 1 item = chưa gửi khách.
> **Phân vai:** gate này chỉ check **ĐỦ + ĐÚNG DELIVERABLE**. Chất lượng layout/semantic đã được cover bởi skill `visual-semantic-seo` (thiết kế) + `semantic-html-optimization` (HTML template) trong lúc làm — không chấm lại ở đây.
> **Nguồn:** modernize từ `Checklist triển khai cấu trúc website.xlsx` (2020) + mốc T2 của quy trình SEO Production.

## Map item → wiki concept

| ID | Label | Wiki ref |
|---|---|---|
| GS-01 | URL structure khớp Topical Map | [[Topical Map]] + [[Semantic Content Network]] |
| GS-02 | Click depth ≤3 tới URL SEO | [[Internal Linking Rules and Strategy]] |
| GS-03 | URL convention + không duplicate danh mục | [[Topical Map]] |
| GS-04 | Keyword→URL mapping đúng intent + loại trang | [[Central Search Intent]] + [[Page Types]] |
| GS-05 | Wireframe đủ template chính | [[Page Types]] |
| GS-06 | Semantic HTML template cho coder | [[Page Types]] |
| GS-07 | Internal link zones đánh dấu | [[Internal Linking Rules and Strategy]] |
| GS-08 | Menu / filter / sidebar spec | [[Topical Map]] |
| GS-09 | CRO site-wide elements | [[Entity Home]] (NAP footer) |
| GS-10 | Chức năng đặc trưng thị trường | [[Source Context]] |
| GS-11 | File bàn giao đúng format + naming | — (luật deliverable client-facing) |
| GS-12 | Fixline → Deadline khách | — (mốc T2) |

---

### GS-01 — Cấu trúc URL tầng đúng Topical Map
**Nguồn legacy:** GIỮ+NÂNG — "Phân loại tầng của từng keywords theo modifier" + "Phân silo vật lý" (2020). Nâng: chuẩn đối chiếu nay là Topical Map đã duyệt, không chỉ logic đối thủ.
Mỗi node trong Topical Map (core/outer section) có URL tương ứng đúng tầng (danh mục / sub-danh mục / page dịch vụ / blog); không node quan trọng nào bị bỏ sót, không URL nào lơ lửng ngoài map. Silo vật lý/phẳng đã chốt nhất quán với map.
✅ Bảng đối chiếu node ↔ URL đính kèm deliverable. ❌ URL tự phát sinh không truy được về node nào.

### GS-02 — Click depth ≤3 tới mọi URL SEO
**Nguồn legacy:** MỚI (chuẩn hiện hành, legacy 2020 chưa có).
Từ trang chủ, mọi URL SEO target đến được trong ≤3 click qua navigation/danh mục/internal link zones (không tính pagination). URL money/pillar ưu tiên ≤2.
✅ Trace thử 5 URL sâu nhất trên sơ đồ cấu trúc. ❌ Sản phẩm nằm ở tầng 5 chỉ tới được qua filter.

### GS-03 — URL convention + không duplicate/trùng nghĩa danh mục
**Nguồn legacy:** GIỮ — "Check duplicate, trùng nghĩa" + "Lên cấu trúc url | chọn cấu trúc phẳng hay silo url" (2020).
Slug chuẩn (không dấu, ngắn, chứa keyword chính, không stopword thừa); quy tắc slug nhất quán toàn site; không 2 danh mục trùng nghĩa cạnh tranh nhau (cannibalization ngay từ cấu trúc).
✅ Bảng URL final không có cặp trùng intent. ❌ Vừa `/san-nhua-gia-go/` vừa `/san-nhua-van-go/` làm 2 danh mục.

### GS-04 — Keyword→URL mapping đúng intent + đúng loại trang
**Nguồn legacy:** GIỮ — "Tìm phiên bản keywords cao volume nhất" + "Xét khả năng đưa keywords vào cấu trúc: intent của keyword là danh mục hay blog, sản phẩm" (2020).
Mỗi URL trong cấu trúc gắn keyword chính (phiên bản volume cao nhất) + intent đã verify SERP: keyword ra danh mục thì làm danh mục, ra blog thì về blog — không ép keyword informational vào category page.
✅ File mapping keyword/volume/intent/loại trang per URL. ❌ Danh mục dựng cho keyword mà SERP toàn bài blog.

### GS-05 — Wireframe đủ bộ template chính
**Nguồn legacy:** GIỮ — "Lên wireframe: đầy đủ cho trang chủ, top level navigation, cate, subcate, page dịch vụ, trang blog, trang sản phẩm; đảm bảo user flow, đầy đủ element" (2020).
Tối thiểu: home / category (PLP) / product (PDP) hoặc page dịch vụ theo model / blog listing + blog detail. Model có subcategory hoặc template đặc thù trong scope → thêm wireframe tương ứng. Mỗi template phủ đủ element đã liệt kê (GS-10).
✅ Đếm đủ template theo scope hợp đồng. ❌ Gửi khách khi thiếu wireframe PDP "làm sau".

### GS-06 — Semantic HTML template cho coder có trong bộ bàn giao
**Nguồn legacy:** MỚI (deliverable 2026; legacy chỉ có wireframe).
Bộ bàn giao chứa HTML template/spec semantic cho coder per loại trang (heading hierarchy, `<main>/<article>/<section>`, thứ tự DOM = thứ tự visual) do luồng `visual-semantic-seo` + `semantic-html-optimization` sản xuất. **Gate chỉ check ĐỦ file + ĐÚNG phiên bản mới nhất** — không review lại chất lượng ở đây.
✅ Mỗi wireframe chính có file HTML/spec đi kèm, version khớp. ❌ Bàn giao wireframe hình ảnh không kèm spec cho coder.

### GS-07 — Internal link zones đã đánh dấu trên wireframe
**Nguồn legacy:** MỚI (chuẩn hiện hành, kế thừa tinh thần "user flow" 2020).
Trên từng wireframe đánh dấu rõ các zone internal link: menu/mega-menu, breadcrumb, sidebar/danh mục con, block link contextual (bài liên quan, sản phẩm liên quan, link cluster→pillar), footer links. Coder nhìn wireframe biết zone nào là link động/tĩnh.
✅ Mọi template có annotation zone link + hướng flow về Core section. ❌ Wireframe chỉ có layout hình, không chỉ ra link đặt đâu.

### GS-08 — Cấu trúc menu / filter / sidebar / sorter spec
**Nguồn legacy:** GIỮ — "Lên cấu trúc filter, sidebar, sorter" + "Cấu trúc menu: bố cục menu, tầng nào show trên menu" (2020).
Spec rõ: menu chính show những tầng nào (top level + tầng 2 nào đáng show), mega-menu hay dropdown; PLP có filter/sorter gì, filter nào tạo URL index được vs filter nào noindex/canonical (quyết định này phải ghi rõ để coder không tự quyết).
✅ Sơ đồ menu + bảng filter (param, index/noindex). ❌ Coder tự quyết filter URL → sinh hàng nghìn URL rác sau launch.

### GS-09 — CRO site-wide elements có mặt
**Nguồn legacy:** GIỮ+NÂNG — "Liệt kê các element, component cần thiết" (2020), cụ thể hóa thành bộ CRO site-wide.
Header (logo, hotline/CTA), footer (NAP nhất quán với Entity — khớp EN-05, link chính sách, social), CTA chính per template (nút mua/form báo giá/đăng ký đúng vị trí above-the-fold khi phù hợp), form liên hệ/lead có mặt trên wireframe các trang cần chuyển đổi.
✅ Check 4 nhóm header/footer/CTA/form trên từng template. ❌ Page dịch vụ không có bất kỳ CTA/form nào trên wireframe.

### GS-10 — Chức năng đặc trưng thị trường đã liệt kê & xuất hiện
**Nguồn legacy:** GIỮ — "Liệt kê các chức năng đặc trưng trong thị trường" + "Chọn website tham khảo" (2020).
Từ benchmark đối thủ/website tham khảo: các function đặc thù ngành (tính giá/quote tool, đặt lịch, so sánh sản phẩm, tra cứu bảo hành, live chat…) được liệt kê thành danh sách, và cái nào trong scope thì xuất hiện trên wireframe tương ứng; ngoài scope → ghi rõ "phase sau" để khách không hiểu nhầm.
✅ Danh sách function + trạng thái (in-wireframe / phase sau). ❌ Đối thủ nào cũng có tool tính giá mà bộ gửi khách không nhắc gì.

### GS-11 — File bàn giao đúng format + naming
**Nguồn legacy:** MỚI (luật deliverable client-facing GTV).
Bộ deliverable theo chuẩn gửi khách: đúng format đã thống nhất (sheet cấu trúc + wireframe), naming file nhất quán có version + ngày; wireframe đủ 2 bản theo luật deliverable; không nêu tên nguồn benchmark trong file gửi khách; viết tắt khai báo lần đầu; có mục khác biệt hóa ✚; tất cả nằm chung folder Drive dự án đúng cây thư mục.
✅ Checklist format pass, link Drive final sạch (không file draft lẫn). ❌ Gửi khách file "wireframe-final-final-v3(1)" kèm tên đối thủ benchmark bên trong.

### GS-12 — Fixline → Deadline khách đã ghi
**Nguồn legacy:** MỚI (mốc cứng T2 của quy trình SEO Production).
Email/tin nhắn gửi khách ghi rõ deadline duyệt (Fixline → Deadline), nêu hệ quả dây chuyền nếu duyệt trễ (coder + content chờ cấu trúc); deadline đồng bộ vào tracking dự án để Account nhắc theo nhịp `acc-weekly-sync` (hạng mục "KHÁCH đang giữ").
✅ Deadline nằm trong văn bản gửi khách + trong tracking. ❌ Gửi bộ file "anh chị xem giúp em" không hẹn ngày → fail gate.
