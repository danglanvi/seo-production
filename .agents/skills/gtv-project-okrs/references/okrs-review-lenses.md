# Rà OKRs nháp — 6 lăng kính + cách ra quyết định điều chỉnh

> Nạp ở B2–B4 của skill. Đây là **cách nghĩ**, không phải checklist tick cho có. Chuẩn tick là 22 mục KO trong `02-raw/knowledge/sop/06-self-checklist/checklist-kpi-okrs-planning.md`.
>
> Rút từ đợt rà OKRs Quý 2 CareerViet (04/08/2026): 5 Objective / 20 KR trên sheet → 15 quyết định điều chỉnh (5 sửa · 5 chỉnh · 5 thêm) → bản 24 KR.

---

## Lăng kính 1 — Baseline có còn đúng không?

Baseline viết lúc lập nháp, tới lúc chốt đã cũ. Soi từng KR: **con số ở cột Baseline có phải sự thật của hôm nay?**

Dấu hiệu baseline chết:
- Ghi «chưa triển khai» trong khi thực tế đã làm được một phần (CareerViet: O4 ghi «chưa triển khai», thực tế 3/26 hạng mục đã live — và đợt đã live cho kết quả đo được).
- Ghi một con số mà không ghi **đo bằng gì** — sang kỳ sau không ai tái lập được.
- Hai bộ số ngược nhau trong cùng một dòng (mô tả nói A, cột Note nói B).

→ Quyết định loại **sửa**. Sửa baseline thường kéo theo phải sửa target, vì target cũ tính trên nền sai.

## Lăng kính 2 — Thước đo có đo đúng thứ KR nói không?

KR nói «tăng X» nhưng chấm bằng chỉ số Y không phản ánh X. Ba dạng hay gặp:

| Dạng | Ví dụ | Xử |
|---|---|---|
| Đo bằng chỉ số nhóm này đang yếu vì lý do khác | Cụm trang công ty đo bằng apply, trong khi nhóm này mạnh ở pageview | Đổi thước đo, ghi lý do |
| Trung bình quý che biến động tháng | CR «≥1,45% trung bình quý» — T8 phải vượt nền +27%, T10 chỉ +7,8%; trung bình che mất việc T8 là tháng khó nhất | Tách target theo tháng |
| So sai mốc | So CR với tháng trước thay vì **nền cùng kỳ năm ngoái** → nhịp mùa vụ bị đọc thành suy thoái | Chốt mốc so, ghi cả dải nền |

→ Quyết định loại **chỉnh**.

## Lăng kính 3 — Có KR nào đang bị chặn bởi thứ chưa ai làm không?

Nếu KR A không chấm được cho tới khi B xong, mà B không phải KR của ai, thì A là target trên giấy.

Cách xử: **tách B thành một KR riêng, đánh dấu «KR CHẶN»**, ghi rõ nó chặn cái gì và hạn chót. KR chặn thường là việc hạ tầng nhàm chán (chuẩn hoá định nghĩa chỉ số, dựng tracking, xác nhận luồng dữ liệu) nên hay bị bỏ quên — chính vì bị bỏ quên nên nó mới chặn.

CareerViet: hai định nghĩa CR song song (1,459% trên sheet vs 1,342% trong báo cáo) → mọi target CR đều vô nghĩa cho tới khi chốt một định nghĩa → KR chặn hạn 15/08.

→ Quyết định loại **thêm**.

## Lăng kính 4 — Phần nào KHÔNG lấy lại được?

Đây là lăng kính người ta hay né vì nói ra thì khó nhìn. Nhưng gộp phần không lấy lại được vào target khôi phục là tự đặt bẫy: cuối quý không đạt, và không ai phân biệt được «làm dở» với «đặt mục tiêu bất khả thi».

Cách xử: phân rã mức mất theo nhóm, chỉ rõ **nhóm nào khôi phục được bằng việc mình làm** và **nhóm nào mất do yếu tố ngoài** (cầu tìm kiếm biến mất, thay đổi địa giới hành chính, thuật toán). Target chỉ đặt trên phần khôi phục được; phần còn lại ghi thẳng **«không cam kết»** kèm số.

CareerViet: −196.184 click ở 27 trang danh mục lõi = khôi phục được (đặt target 52,7% → ≥65%); −581.160 click ở tập truy vấn CTR cao 2025 = không cam kết.

## Lăng kính 5 — Nghiệm thu bằng tài liệu hay bằng website?

KR kiểu «bàn giao audit», «gửi template», «đề xuất phương án» đều **đạt 100% mà website không đổi một dòng**. Đây là bài học đắt nhất của Q1 CareerViet: audit 30 phát hiện bàn giao 12/06, tới 04/08 mới 3/26 hạng mục live.

Cách xử:
1. Phát biểu Objective bằng **thay đổi đã live và đã kiểm chứng**, không bằng tài liệu bàn giao.
2. Thêm KR **kiểm chứng sau release**: hạng mục Dev báo xong phải được verify bằng crawl + Search Console trong ≤7 ngày rồi mới tick Done. (Q1 đã có hạng mục báo «Done» nhưng URL vẫn trả HTTP 200.)
3. Việc phụ thuộc phía client → **backup plan có ngưỡng kích hoạt bằng ngày**, không phải «sẽ theo dõi sát».

## Lăng kính 6 — Trần KR và thứ tự ưu tiên

Chuẩn trạm là 3–4 O × 3–4 KR; dự án chạy trần khác thì ghi nhận chỗ lệch. Vượt trần thì **gộp**, không cắt.

**Luật gộp — chỉ gộp khi cả ba đều đúng:**

1. Cùng **dây chuyền thực thi** (đầu ra của việc này là đầu vào của việc kia).
2. Cùng **PIC**.
3. Cùng **cách nghiệm thu** (một câu là chấm được cả hai).

Ví dụ đúng: «Go-live UI-UX 2 page lõi» + «Duyệt wireframe Home + Hub» → một KR «Go-live trải nghiệm 4 trang lõi» (cùng chuỗi wireframe → product chốt → Dev release, cùng PIC, cùng nghiệm thu «đã live + có báo cáo CR before/after»).

Ví dụ SAI: gộp «viết content» với «đi backlink» chỉ vì cùng nhắm một nhóm từ khoá — khác PIC, khác nghiệm thu, gộp xong không ai chịu trách nhiệm phần nào.

**Chuyển Objective** cũng là một cách giải trần: KR nằm nhầm Objective sẽ luôn bị chấm bằng thước đo của Objective đó. Chuyển sang O đúng vừa giải phóng chỗ vừa sửa được thước đo.

---

## Sản phẩm của bước rà: danh sách quyết định

Không nộp bản OKRs mới trước. Nộp **danh sách quyết định đánh số**, mỗi quyết định:

```
Đ<n> · [sửa|chỉnh|thêm] · <O/KR nào>
  Hiện tại : <nguyên văn nháp>
  Vấn đề   : <sai ở đâu — kèm số/nguồn>
  Đề xuất  : <đổi thành gì>
  Hệ quả   : <ai phải làm gì thêm / ảnh hưởng KR nào>
```

Người duyệt cần thấy **vì sao đổi**, không phải chỉ **đổi thành gì**. Danh sách được duyệt rồi mới dựng bản mới — và giữ lại file danh sách làm hồ sơ lý do (CareerViet: `CAREERVIET_okrs-q2-de-xuat-dieu-chinh_v1.html`).

## Bản HTML để review — 5 mức màu

Bản `.md` là canonical, nhưng người duyệt đọc bản `.html`. Yêu cầu:

| Mức | Màu | Nghĩa |
|---|---|---|
| giữ | không tô | Giữ nguyên so với bản trước |
| **sửa** | đỏ nhạt | Số/baseline cũ không còn đúng |
| **chỉnh** | vàng nhạt | Đổi cách đo / target / gộp KR |
| **thêm** | xanh nhạt | KR mới |
| **đôn lịch** | xanh dương nhạt | Chỉ đổi deadline (dùng khi vòng sau chỉ chạm timeline) |

Cộng thêm: `<mark>` tô sáng **đúng phần chữ đã đổi** trong dòng · pill nhãn loại thay đổi cạnh tiêu đề KR · deadline cũ gạch ngang cạnh deadline mới · **một khối callout đầu trang liệt kê đổi gì ở bản này**, và một callout ghi **trạng thái chưa hoàn tất** (chưa fact-check sheet / chưa self-check / chưa duyệt).

Bảng phải **mirror đúng cột của sheet team** (Objectives · Key Results · PIC · Deadline · Note · Baseline) — người duyệt đang quen sheet, đổi bố cục là bắt họ học lại.

## Ba lỗi đã mắc, đừng lặp

1. **Đề xuất dựa trên bản `.md` trong instance thay vì sheet team đang chạy.** Bản trong instance cũ hơn: target Tool đã hạ 120K → 50–60K trên sheet mà file cũ vẫn cảnh báo 120K. **Luôn kéo sheet trước.**
2. **Sửa số trong im lặng.** Đổi nền so sánh, đổi định nghĩa chỉ số → phải ghi «trước / sau / vì sao» ở chỗ người duyệt nhìn thấy.
3. **Đặt số khi chưa có forecast.** Chưa có forecast thì ghi «chốt số sau khi có forecast — hạn <ngày>». Đặt số đẹp rồi sửa sau làm hỏng cả kỳ chấm điểm.
