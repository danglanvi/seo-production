# Chọn phương án CDN: cây quyết định, bảng giá, số đo thật

Nạp ở bước 2 của SKILL.md. Số đo lấy từ một site VN (WordPress, OpenLiteSpeed, VPS ở VN, DNS Cloudflare gói Free), 26/10/2026. Giá đọc ngày 26/10/2026; đọc lại trang giá trước khi trình.

## 1. Cây quyết định

1. Khách chính ở đâu?
   - Ngoài VN, hoặc toàn cầu → **nhánh A**: proxy Cloudflare toàn site (`nhanh-a-cloudflare-proxy.md`). Dừng ở đây.
   - Chủ yếu VN hoặc châu Á → câu 2.
2. Origin ở đâu?
   - Ngoài châu Á (Mỹ, châu Âu) → nhánh A vẫn được. Khách VN đi trạm Singapore hoặc Hồng Kông vẫn gần hơn origin. Đo trước khi chốt.
   - Ở VN → **nhánh B**: chia vùng. Khách châu Á đi thẳng origin, Googlebot và khách vùng khác đi CDN (`nhanh-b-chia-vung.md`).
3. Ngân sách và mức chịu rủi ro của nhánh B → chọn một dòng ở bảng §2.

Lý do không bật proxy Cloudflare toàn site cho site VN: trạm Cloudflare trả lời khách VN tuỳ đường định tuyến của nhà mạng. Đo 26/10/2026:
- Bật thử: TTFB khách VN từ 13–22 ms lên 220–1.590 ms (trạm Marseille, Hồng Kông).
- Mac FPT qua edge: HIT 150–1.047 ms ở trạm SIN, CDG, MRS.
- Đi thẳng VPS: 14–19 ms.

Gói trả phí (Pro, Business) không cam kết đưa khách VN vào trạm Hà Nội hay TP.HCM. Regional Tiered Cache và chọn trạm theo data center chỉ có ở Enterprise.

## 2. Phương án nhánh B

| Mã | Cách làm | Khách VN | Googlebot Mỹ | Bảo mật | Giá/tháng | Rủi ro |
|---|---|---|---|---|---|---|
| O2 | Cloudflare Load Balancing chế độ DNS-only, geo steering theo quốc gia → pool origin cho VN, pool edge Cloudflare cho vùng khác | Đi thẳng origin (LB xét IP resolver hoặc ECS) | Edge Cloudflare: lượt đầu khi trạm Mỹ trượt, tầng trên trúng 290,5 ms (đo, trượt ngưỡng 260) | Cloudflare cho đường ngoài VN | LB Basic 5 USD + Traffic Steering 10 USD = 15 USD | Cache Cloudflare trạm Mỹ trượt nhiều. Cần thêm Argo (từ 5 USD + theo GB) |
| O4 | LB Cloudflare geo steering như O2, nhưng pool ngoài VN là Bunny | Đi thẳng origin | Bunny, Origin Shield ở Mỹ: lượt đầu 67,5 ms, lặp 20,5 ms (đo, n = 24) | Cloudflare DNS + Bunny cho đường ngoài VN | khoảng 16 USD | Chắc chắn nhất cho khách VN. Thêm nhà cung cấp |
| O7 | Apex CNAME sang pull zone Bunny, mọi khách qua Bunny | **Chậm hơn** 91–233 ms: Cloudflare tra địa chỉ thay khách từ HKG/SIN, Bunny trả trạm HK1/SG1 (đo) | Như O4 | Bunny | khoảng 1 USD | Không đạt khách VN |
| O7b | Apex CNAME tới tên trên Bunny DNS có script chia vùng; DNS vẫn ở Cloudflare | Đi thẳng origin ở 95–100% lượt hỏi DNS (mục §3) | Như O4 | Cloudflare DNS + Bunny cho đường ngoài châu Á | khoảng 1–3 USD | Đôi khi đưa khách VN sang Bunny Mỹ; Bunny DNS thành điểm hỏng đơn lẻ cho cả khách VN |
| O8 | Chuyển DNS sang Bunny DNS, bản ghi chia vùng | Đi thẳng origin | Như O4 | Mất proxy Cloudflare cho các tên phụ | khoảng 1 USD | Rời Cloudflare |

Mặc định trình:
- Nếu Lead chấp nhận 15 USD/tháng: O4.
- Nếu Lead muốn rẻ: O7b, kèm mẫu đo khách VN và giám sát (§3).
- Người duyệt site VN ngày 26/10/2026 chọn O7b vì 15 USD/tháng "cao".

## 3. Giới hạn của O7b (đo 26/10/2026)

- Cloudflare làm phẳng CNAME ở apex mà không gửi ECS. Script Bunny chỉ thấy máy Cloudflare đi hỏi, không thấy khách.
- Bản script chỉ xét quốc gia: 4/120 lượt hỏi từ VN nhận Bunny (3,3%), dù trạm Cloudflare trả lời luôn ở Singapore.
- Sau khi thêm điều kiện mã trạm Bunny DNS nhận câu hỏi (`serverZone`) ở châu Á:
  - NS Cloudflare: 50/50 lượt nhận origin.
  - 1.1.1.1: 50/50 lượt nhận origin.
  - DNS nhà mạng: 50/50 lượt nhận origin.
  - 8.8.8.8: 5/50 lượt nhận Bunny.
- Khi khách VN nhận Bunny, TTFB 600–700 ms thay vì 14–49 ms.
- Load Balancing (O2, O4) xét IP resolver hoặc ECS của khách, nên tránh được lỗi này. Đây là phần khách trả thêm 15 USD.

## 4. Nhà CDN thêm hay thay

Ghi rõ trong bảng trình duyệt:
- **Thêm:** DNS, SSL, tên phụ, email vẫn ở nhà cũ. Nhà mới chỉ phục vụ đường tốc độ.
- **Thay:** chuyển DNS hoặc proxy toàn bộ.

Người duyệt muốn bảo mật và setup chung ở Cloudflare, nhà khác chỉ lo tốc độ.

Nhắc rõ: apex DNS-only (nhánh B) không có WAF và bot rule của Cloudflare. Trước khi đổi cũng vậy, nhưng người duyệt dễ hiểu nhầm là Cloudflare đang bảo vệ apex.
