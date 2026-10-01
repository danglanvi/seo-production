# Readiness router — chọn mức làm việc, cơ chế và pattern

Mục đích: bước 0 của cro-audit. Trả lời 3 câu trước khi audit: GTV được kết luận tới mức nào, khách chuyển đổi bằng gì, soi những trang nào. Kết quả ghi ở đầu `conversion-path`.

## §1. Hai mức làm việc

| Mức | Điều kiện | GTV bàn giao được | Không được |
|---|---|---|---|
| **A. Research + sửa lỗi + rollout có theo dõi** (mặc định) | Có hoặc đang gắn tracking; có quyền brief cho dev khách | Blocker P0, evidence-backlog, feature brief, measurement plan, số quan sát trước/sau có nhãn, report 3 khối | Công bố "uplift %", "CR tăng nhờ GTV" như nhân quả |
| **B. A/B** (ngoại lệ) | Tracking đã PASS QA; eligible volume đủ theo feasibility (`experiment-lite.md` §2); có tool test và dev; client đồng ý chạy song song 2 bản | Test contract, QA, phân tích theo plan, quyết định ship/reject/inconclusive | Peeking, đổi primary sau test, kết luận từ p>0,05 là "bằng nhau" |

Mức B không phải mục tiêu; đa số client SME của GTV ở mức A suốt hợp đồng. Chỉ chuyển sang B khi feasibility ra số ngày hợp lý (thường <60 ngày) và client thấy giá trị.

## §2. Câu hỏi qualification (hỏi Account/khách ở kickoff #34)

1. Khách chuyển đổi bằng gì trên website: gọi / Zalo / Messenger / form / báo giá / giỏ hàng / apply? Cái nào chính?
2. Outcome thật ghi ở đâu (Sheet sale, CRM, backend đơn, ATS)? Ai ghi? GTV được xem mức nào (số tổng / đã che)?
3. Ai sửa website: dev nội bộ, agency web, freelancer? Thời gian phản hồi thường bao lâu?
4. Có GA4/GTM chưa? Ai có quyền? Có Clarity/Hotjar không, gắn được không?
5. Có traffic từ AI engine không (GEO trong hợp đồng)?
6. Có chính sách nào chặn thay đổi (brand guideline, nền tảng SaaS không sửa được checkout, quy định ngành)?

Câu 3 quyết định giá trị thực của CRO add-on: brief không ai làm = không có giá trị tái ký. **Không đặt KPI "tỷ lệ brief được triển khai"** (bỏ 13/09/2026 — tỷ lệ thưởng việc dễ và che P0 tồn). Theo dõi bằng ba luật: (a) trạng thái brief tách ba mốc **đã brief → dev đã deploy → GTV QA PASS**, chỉ mốc cuối vào "việc đã sửa"; (b) **P0 tồn luôn hiện đầu report** với tuổi lỗi, owner, blocker, ngày follow-up — không đóng khi chỉ gửi brief, không hạ P vì khách chưa sửa; (c) P0 kẹt bên khách → được làm P1/P2 độc lập nhưng không tuyên bố phễu đã khắc phục. Dev phản hồi chậm → ghi SLA vào §5 và bảng ranh giới §4, không biến thành chỉ số.

## §3. Chọn cơ chế và loại trang

| Mô hình client | Cơ chế chính | Loại trang soi | Pattern trong `patterns-condensed.md` |
|---|---|---|---|
| Dịch vụ local (thu mua, sửa chữa, phòng khám, sân thể thao, spa) | Gọi/Zalo | organic-landing, service-page | §1, §6, §7 |
| Dịch vụ B2B, agency, tư vấn, đào tạo doanh nghiệp | Form lead (+ gọi/Zalo phụ) | organic-landing, service-page | §2, §6, §7 (+§1) |
| In ấn, gia công, sản xuất theo yêu cầu, vận chuyển | Báo giá | service-page, pdp (nếu có catalog) | §3, §7, §9 |
| Ecommerce | Giỏ hàng/checkout | plp-filter-search, pdp | §4, §8, §9 |
| Job site / career site | Apply/ATS | job-search-detail | §5, §10 |
| Khoá học, sự kiện | Form đăng ký + thanh toán | organic-landing | §2, §4, §6 |
| Có traffic AI engine | (không đổi cơ chế) | + trang tìm kiếm nội bộ, trang được AI trích | §6 mục AI, §8 #7 |

Site nhiều mô hình (ecommerce + tư vấn Zalo): chọn tối đa 2 cơ chế, ghi cơ chế phụ.

## §4. Ranh giới trách nhiệm ghi vào conversion-path

- GTV: phát hiện, bằng chứng, brief, measurement plan, QA sau khi dev làm, đọc số đúng nhãn.
- Khách/dev: triển khai, quyền GTM/GA4, dữ liệu outcome, duyệt nội dung/giá/cam kết.
- Không thuộc CRO add-on: viết lại positioning, thiết kế lại toàn site, vận hành sale/CSKH, chạy ads.
- Phí, cam kết, KPI hợp đồng: ngoài skill này (BD/Account).

## §4b. Bảng chuyển việc — ca rơi giữa WS13 và skill khác

| Việc gặp trong audit | Ai sở hữu | WS13 làm gì |
|---|---|---|
| Đổi CTA/form/trust/tính năng **trong** block đã lock | WS13 (`cro-audit`) | Brief + QA |
| Đổi block map, H1/heading, URL, internal link cấu trúc | WS04 (`visual-semantic-seo`) | Ghi finding + "route trạm 04", không brief thay đổi |
| CWV field data, script nặng, crawl/index, redirect, canonical | Technical (`technical-seo-audit`, `seo-onpage`) | Ghi outcome/guardrail bị ảnh hưởng; không tự chấm PASS/FAIL CWV từ Lighthouse; thiếu field data → "chưa có số", không FAIL |
| Vừa layout vừa conversion (ví dụ grid PLP bị đẩy xuống) | WS04 quyết layout; WS13 cung cấp bằng chứng conversion | Finding E≥2 + đề xuất, WS04 duyệt |
| Chưa có structure lock nhưng có blocker P0 (form không gửi) | WS13 | Báo và brief sửa lỗi ngay; ghi "chưa có structure lock" cho phần tối ưu |
| Copy/thông điệp/claim/proof | Copywriting (`concepts/copywriting/*`) | Ghi task, vị trí, states, event; copy do copywriting/khách duyệt |
| Chỉ đổi màu/brand | Design/dev | Không mở dự án CRO; theo dõi click nếu client muốn |

## §5. Đầu ra của bước 0 (ghi ở đầu conversion-path)

```
Readiness: A (research + sửa + rollout) | B (A/B) — lý do
Cơ chế: <chính> (+ <phụ>)
Loại trang soi: <2–4>
Outcome: <định nghĩa + nguồn ghi> — trạng thái tracking: chưa có / đang gắn / PASS QA <ngày>
Dev/owner sửa web: <ai, SLA>
Giới hạn: <chính sách/nền tảng>
```
