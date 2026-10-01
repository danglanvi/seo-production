# Triển khai và đọc số — sửa lỗi, rollout có theo dõi, A/B khi đủ điều kiện

Mục đích: bước 5 của cro-audit (#36). Nguồn: wiki `concepts/cro/experimentation` (Kohavi, Stanford, Microsoft SRM, Google website testing), tóm tắt cho skill chạy standalone.

## §1. Ba đường, chọn theo bằng chứng

| Điều kiện | Đường | Kết luận được phép | Ghi trong report |
|---|---|---|---|
| Lỗi tái hiện được (E3): form không gửi, `tel:` sai, checkout lỗi | **Sửa lỗi + QA + rollout** | "Lỗi đã khắc phục ngày …"; tác động kinh doanh đo riêng | Khối 2: việc đã sửa + số trước/sau nhãn quan sát |
| Giả thuyết UX có E≥2, chưa đủ mẫu A/B hoặc client không có tool | **Rollout có theo dõi** | "Sau thay đổi, metric X từ a → b (cùng mẫu số, cùng cửa sổ); yếu tố khác đã đổi: …" | Nhãn "quan sát trước/sau", không "uplift", không "nhờ GTV" |
| Tracking PASS, feasibility đạt, có tool + dev, client đồng ý | **A/B** | Ước lượng tác động trong population/cửa sổ của test | Counts, rates, effect + khoảng bất định, guardrail, SRM |

Mặc định là hai đường đầu. A/B là ngoại lệ có điều kiện.

## §2. Feasibility A/B — tính trước, không hứa "14 ngày"

Cần: baseline p0 (tỷ lệ hiện tại trên population đủ điều kiện), hiệu ứng nhỏ nhất đáng phát hiện (MDE, ví dụ +20% tương đối), alpha 0,05 hai phía, power 0,8, số người đủ điều kiện/ngày tham gia test.

Xấp xỉ mẫu mỗi nhóm: n ≈ [z(0,975)·√(2·p̄(1−p̄)) + z(0,8)·√(p0(1−p0) + p1(1−p1))]² / (p1−p0)², với p̄ = (p0+p1)/2, z(0,975)=1,96, z(0,8)=0,84.

Ví dụ minh hoạ (không phải dữ liệu client): p0 = 2%, p1 = 2,4% → ≈21.100/nhóm, ≈42.200 tổng. Với 300 người đủ điều kiện/ngày → ≈141 ngày chưa kể chờ outcome. Kết luận thực hành: site SME thường không A/B được thay đổi nhỏ; chỉ test khi hiệu ứng kỳ vọng lớn (lỗi rõ, thay đổi flow) hoặc traffic lớn. Ghi phép tính vào heatmap-review §4 trước khi đề xuất test.

Không áp công thức này cho revenue heavy-tail, dữ liệu cluster, hay engine sequential của tool (theo luật của engine).

## §3. Test contract tối thiểu (khi đi đường A/B)

- Câu hỏi + cơ chế kỳ vọng; population/unit (user; giữ variant khi quay lại; cross-device ghi rủi ro).
- Control/treatment mô tả đủ để tái dựng; **một giả thuyết = một treatment** (có thể gồm nhiều thay đổi, khi đó kết luận cho cả gói — không tách từng thay đổi).
- Primary duy nhất chốt trước; secondary chẩn đoán; guardrail + mức tổn hại chấp nhận.
- Thiết kế: baseline, MDE, alpha, power, mẫu, allocation, ngày bắt đầu/kết thúc dự kiến, chu kỳ tuần trọn.
- QA trước launch: exposure log, tracking cả 2 bản, SEO (không cloaking; canonical; redirect 302 tạm; dọn biến thể sau test), accessibility, performance, kill switch, rollback.
- Đọc kết quả: kiểm **SRM** (tỷ lệ phân bổ thực vs kỳ vọng; lệch → điều tra assignment/bot/pipeline trước khi đọc lift); fixed-horizon không dừng sớm vì p vừa nhỏ; không đổi primary; segment sau test là exploratory; "không có ý nghĩa thống kê" ≠ "bằng nhau"; báo counts + rates + effect tuyệt đối/tương đối + khoảng bất định + guardrail.

## §4. Rollout có theo dõi — làm cho đúng

1. Annotation GA4 ngày deploy; ghi mọi thay đổi cùng lúc (giá, khuyến mãi, ads, mùa vụ, content mới).
2. Cùng mẫu số, cùng cửa sổ (≥4 tuần trọn trước và sau; outcome chậm dùng cohort).
3. So theo phân đoạn đã định trước (thiết bị, kênh); không chọn tuần đẹp.
4. Rollback nếu xuất hiện lỗi P0 mới hoặc primary giảm rõ sau 2 tuần và không giải thích được.
5. Viết: "quan sát", "cùng kỳ", "yếu tố khác đã đổi"; không "tăng X% nhờ CTA mới".

## §5. Deadline ≠ cửa sổ đọc số

- Deadline triển khai brief: 14–30 ngày (SOP hiện hành) — là mốc dev làm xong.
- Cửa sổ đọc số: ≥4 tuần trọn sau deploy; lead → đạt chuẩn +7 ngày; đơn COD → hợp lệ +14 ngày; apply → HR theo SLA.
- Report tháng có thể ghi "đã sửa, đang theo dõi, đọc số kỳ sau" — không ép kết luận trong 14 ngày.

## §6. Log trong `heatmap-review` §4

Cột "Biến duy nhất" hiểu là "giả thuyết/treatment"; thêm cột "đường (sửa lỗi / rollout / A/B)", "feasibility (mẫu cần · ngày ước tính)", "SRM PASS/FAIL" khi A/B. Test không có winner nhưng dữ liệu tốt vẫn là kết quả: không triển khai thay đổi kém.
