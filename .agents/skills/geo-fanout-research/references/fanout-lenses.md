# 8 lens sinh fan-out — template VN/EN + ví dụ

> Reference cho Bước 1 của `geo-fanout-research`. Lens = góc mà AI Mode/ChatGPT thường tách một câu hỏi thành câu hỏi con (quan sát từ cấu trúc câu trả lời AI Mode/AIO 2025-2026 + phân loại Nectiv 28k fan-out 08/2026). Seed từ lens **chưa phải evidence** — phải đối chiếu PAA/related/AI answer ở Bước 2.

## Bảng lens

| # | Lens | Câu hỏi con điển hình (VN) | (EN) | Cluster hay rơi vào |
|---|---|---|---|---|
| 1 | **Định nghĩa / cơ chế** | "[X] là gì", "[X] hoạt động thế nào", "[X] khác [Y] chỗ nào" | what is [X], how does [X] work | *Hiểu* |
| 2 | **Cách làm / quy trình** | "cách [làm X]", "các bước [X]", "[X] cần chuẩn bị gì" | how to [X], steps to [X] | *Làm* |
| 3 | **So sánh / thay thế** | "[X] hay [Y] tốt hơn", "thay [X] bằng gì", "[X] vs [Y]" | [X] vs [Y], alternatives to [X] | *Chọn* |
| 4 | **Chi phí / giá / thời gian** | "[X] giá bao nhiêu", "chi phí [X] 2026", "[X] mất bao lâu" | how much does [X] cost, [X] pricing | *Chọn* |
| 5 | **Đối tượng / phù hợp ai** | "[X] phù hợp với ai", "[X] cho [doanh nghiệp nhỏ/người mới]", "khi nào nên [X]" | is [X] right for [audience], when to [X] | *Chọn / Hiểu* |
| 6 | **Rủi ro / nhược điểm / sai lầm** | "[X] có tác dụng phụ/rủi ro gì", "sai lầm khi [X]", "[X] có đáng không" | risks of [X], common mistakes, is [X] worth it | *Tin* |
| 7 | **Bằng chứng / đánh giá / uy tín** | "[X] có hiệu quả không", "đánh giá [X]", "[Brand] có uy tín không", "nghiên cứu về [X]" | does [X] work, [X] reviews, is [Brand] legit | *Tin* |
| 8 | **Địa phương / thời điểm / điều kiện** | "[X] tại [TP.HCM]", "[X] 2026", "[X] cho [ngành/luật VN]" | [X] in [city], [X] 2026, [X] for [regulation] | *Làm / Chọn* |

**Quy tắc sinh:** 1-3 sub-query/lens; giữ ngôn ngữ user (không jargon); với query **branded** (tên brand/sản phẩm) lens 7 + 4 + 5 nặng nhất (AI verify tại entity home — `site:` 64% fan-out); với query **transactional** lens 3 + 4 + 8 nặng nhất; với **informational** lens 1 + 2 + 6.

## Ví dụ 1 — informational: "AI Overview ảnh hưởng SEO thế nào" (VN)

| Lens | Sub-query seed |
|---|---|
| 1 | AI Overview là gì · AI Overview lấy nguồn từ đâu |
| 2 | cách tối ưu bài để được AI Overview trích dẫn |
| 3 | AI Overview vs AI Mode khác gì · AI Overview vs featured snippet |
| 4 | tối ưu cho AI Overview tốn bao nhiêu / mất bao lâu |
| 5 | ngành nào bị AI Overview ảnh hưởng nhiều |
| 6 | AI Overview làm giảm click bao nhiêu · rủi ro zero-click |
| 7 | nghiên cứu về CTR khi có AI Overview · có đáng đầu tư GEO không |
| 8 | AI Overview ở Việt Nam đã có chưa (2026) |

Gom cluster (≤4): **Hiểu** (1, 3) · **Tác động** (6, 7 — CTR, zero-click, ngành) · **Làm** (2, 4) · **Bối cảnh VN** (5, 8). Cluster "Bối cảnh VN" thường ngoài CSI của bài "ảnh hưởng thế nào" → ứng viên page riêng.

## Ví dụ 2 — commercial: "dịch vụ SEO cho doanh nghiệp nhỏ" (VN)

| Lens | Sub-query seed |
|---|---|
| 1 | dịch vụ SEO gồm những gì · SEO tổng thể vs SEO từ khóa |
| 2 | quy trình làm SEO của agency · doanh nghiệp cần chuẩn bị gì |
| 3 | thuê agency hay tự làm / freelancer · so sánh gói SEO |
| 4 | giá dịch vụ SEO 2026 · chi phí SEO theo tháng cho SME |
| 5 | SME ngành nào nên làm SEO · khi nào chưa nên làm SEO |
| 6 | rủi ro khi thuê SEO giá rẻ · dấu hiệu agency lừa đảo |
| 7 | agency SEO nào uy tín · case study SEO SME · cam kết KPI thế nào |
| 8 | dịch vụ SEO tại TP.HCM / Hà Nội |

Gom cluster: **Hiểu gói** (1, 2) · **Chọn & giá** (3, 4, 8) · **Tin** (6, 7) · **Phù hợp** (5). Với brand: cluster **Tin** cần owned truth pages trả lời được (pricing, case study, cam kết) — gate G-ENT.

## Ghi chú evidence

- PAA/related của Google là **evidence bổ sung** cho lens, không phải cơ chế fan-out của AI Mode; AI answer hiện tại (paste) là evidence mạnh nhất vì phản ánh cấu trúc câu hỏi con máy đang dùng.
- ChatGPT: trường `search_queries` biến mất 16-20/08/2026 — tool đọc trường đó trả rỗng; đọc fan-out từ cấu trúc câu trả lời + citation, date-stamp model version.
- Không in số fan-out tuyệt đối; chỉ ghi số cluster + tỷ lệ stable.
