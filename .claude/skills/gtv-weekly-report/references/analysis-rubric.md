# analysis-rubric.md — chuẩn NHẬN XÉT + lớp PATTERN (nạp ở Pha 2 ANALYZE)

Output pha 2: `09-reporting/analysis/<YYYY>-W<NN>-insights.md`. File này vừa là nguồn NHẬN XÉT cho deck, vừa là **bộ nhớ tích lũy** cho phân tích pattern các tuần sau — viết đủ để tuần sau đọc lại hiểu ngay.

## Format file insights

```markdown
---
week: <N>
range: "<dd/mm–dd/mm/yyyy>"
digest: ../../02-raw/seo-data/weekly/<YYYY>-W<NN>/digest.json
summary:            # KHỐI MÁY-ĐỌC — tuần sau load 4-8 file chỉ cần đọc frontmatter
  pv_week: <int>
  pv_pct_ht: "<%HT>"
  runrate_lk: "<%>"
  apply_week: <int>
  apply_pct_ht: "<%>"
  groups:           # Δ% per nhóm trang chính
    job_listing: "+1.7%"
    job_detail: "-7.78%"
    blog_kpi: "-19.71%"
  movers_down: ["<url>: -284", ...]   # top 3-5
  movers_up: ["<url>: +97", ...]
  flags: ["<pattern/red-flag tuần này>"]
---
# W<N> — Insights
## 1. Run-rate & KPI vận hành
## 2. Per nhóm trang (nhận xét + action)
## 3. Top pages bị ảnh hưởng
## 4. PATTERN (đối chiếu 4-8 tuần)
## 5. Cơ hội & đề xuất tuần tới
## 6. SOW & phối hợp
```

## Chuẩn MỘT nhận xét (bắt buộc đủ 4 phần — cấm nhận xét suông)

`[SỐ + so sánh] → [nguyên nhân khả dĩ, đánh dấu độ chắc] → [ý nghĩa với KPI] → [action + owner đề xuất]`

- ✅ "Job Detail **-54.000 PV (-7,78% WoW)**, giảm tập trung nhóm Bán hàng/Kế toán/Hành chính; Imp -8.6k và CTR -0,56 điểm trong khi Position gần như đứng yên → khả năng **demand giảm theo mùa** (Prior Year cùng kỳ cũng chững) hơn là mất hạng [độ chắc: trung bình — cần xem thêm 1 tuần]. Cụm KPI phụ thuộc 53% vào Job Detail → run-rate tháng 7 đang 54% vs time 50%, chưa nguy hiểm. **Action:** theo dõi thêm W12; nếu giảm tuần thứ 3 liên tiếp → chạy content-refresh cụm ngành giảm sâu nhất (owner: SEO Lead)."
- ❌ "Traffic giảm nhẹ, cần theo dõi thêm." (không số, không nguyên nhân, không action)

Luật evidence (thừa hưởng trạm Reporter):
- Số lấy từ digest, giữ nguyên định dạng nguồn. Không truy được nguồn → không viết.
- Nguyên nhân chỉ ở mức **khả dĩ + độ chắc** (thấp/trung bình/cao). Muốn kết luận chắc → đề xuất skill điều tra (`content-refresh`, `technical-seo-audit`, `seo-drift-tracker` nếu nghi coder deploy), KHÔNG tự phán.
- Báo đỏ trung thực: %HT <100%, mục trễ SOW phải hiện đúng màu + lý do; không làm mềm.

## Lớp PATTERN (mục 4) — quy tắc so tuần

Load frontmatter `summary` của 4-8 insights gần nhất rồi kiểm tuần tự:

| Pattern | Điều kiện | Kết luận/Action |
|---|---|---|
| Decay thật | Nhóm/URL giảm ≥2 tuần liên tiếp VÀ Prior Year cùng kỳ không giảm tương ứng | Flag 🔴 + đề xuất điều tra (refresh/technical) |
| Seasonal | Giảm nhưng Prior Year cùng kỳ (cột trong run-rate) cũng giảm nhịp tương tự | Ghi nhận, không action lớn; nói rõ với client |
| Cơ hội CTR | Imp tăng ≥10% nhưng CTR đi ngang/giảm | Đề xuất title/meta batch cho nhóm đó |
| Push target | Position 6-10 + Imp cao (từ movers có pos) | Đề xuất onpage/internal link đẩy top 5 |
| Cannibalization nghi vấn | URL A giảm đúng nhịp URL B cùng cụm tăng | Đề xuất serp-clustering verify |
| Momentum | Nhóm tăng ≥2 tuần liên tiếp | Đề xuất nhân rộng pattern (content/IL tương tự) |
| Run-rate lệch time | Run-rate LK tháng < time run-rate quá 10 điểm | Cảnh báo sớm nguy cơ hụt KPI tháng — nêu ở đầu insights |

Mỗi pattern bắn ra ≤1 dòng trong `summary.flags` để tuần sau đọc rẻ.

## Kỷ luật 80/20

- Chỉ phân tích trên digest + insights cũ. KHÔNG mở CSV trừ khi cần soi đúng 1 bảng; KHÔNG bao giờ đọc tab URL-level (28k dòng) vào context.
- Top pages = đúng danh sách `top_movers_*` (đã lọc `min_clicks`) — không đi tìm thêm URL ngoài danh sách trong tuần thường; muốn sâu hơn là việc của skill điều tra.
