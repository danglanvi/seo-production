# Format deck kỳ THÁNG / QUÝ — spec đầy đủ

> Chốt sau bản chạy thật T7 + Quý 1 CareerViet (04/08/2026). Nạp file này ở **Pha 0** (chọn format) và **Pha 3** (viết content.yaml) khi làm báo cáo kỳ THÁNG hoặc QUÝ. Format TUẦN ở `weekly-catchup-format.md` — không trộn hai file.
>
> Ba format, một pipeline: TUẦN ~11 slide · THÁNG ~26 slide · **QUÝ ~45–50 slide** (tháng cuối quý = deck kép «tháng N + tổng kết quý»). Pha FETCH/ANALYZE dùng chung; chỉ `content.yaml` khác.

---

## 1. Deck kỳ QUÝ = deck kép

Tháng cuối quý KHÔNG làm 2 deck. Làm **một deck hai lớp**: mọi section chạy lớp THÁNG trước (diễn biến trong tháng, so tháng liền trước) rồi lớp QUÝ (so cùng kỳ năm ngoái, đúc kết cả quý). Lý do: client ngồi họp một lần; hai lớp cạnh nhau mới thấy «tháng tốt nhưng quý vẫn âm so cùng kỳ» — đây chính là kết luận có giá trị nhất của kỳ Q1 CareerViet.

**Quý dự án ≠ quý dương lịch.** Quý tính theo tháng dự án (CareerViet: T1 = 05/2026 → Quý 1 khép 31/07/2026). Ghi rõ dải ngày ở slide cover + `data_meta` mọi slide kỳ quý, nếu không người đọc mặc định hiểu là Q1 dương lịch.

## 2. Khung 8 section + phụ lục (bản chạy thật: 49 slide)

| § | Section | Slide | Nội dung bắt buộc |
|---|---|---|---|
| — | Cover + Agenda | 1–2 | Agenda = đúng 8 mục dưới đây, chữ của client |
| **1** | Overview run-rate | 1.1–1.7 | 1.1 bảng tổng 3 chỉ số × các tháng (kế hoạch·thực tế·%HT·MoM·cùng kỳ) · 1.2 tháng · 1.3 quý · 1.4–1.5 chart thực tế vs kế hoạch + CR · 1.6 so cùng kỳ năm ngoái · 1.7 đúc kết |
| **2** | Pageview theo nhóm trang | 2.1–2.10 | Lớp tháng (2.1–2.3) → lớp quý so cùng kỳ (2.4–2.5) → **forensics nhóm giảm sâu** (2.6–2.8) → nhóm tăng (2.9) → đúc kết ghép hai lớp (2.10) |
| **3** | Applythanks theo nhóm trang | 3.1–3.5 | Cùng cấu trúc §2 + slide riêng cho chỉ số ưu tiên kỳ sau |
| **4** | SOV từ khoá | 4.1–4.4 | 4.1 giải thích cách tính TRƯỚC khi trình số · chart theo tháng · bảng snapshot kỳ |
| **5** | Góc nhìn bên thứ ba (traffic) | 5.1–5.2 | Toàn site → theo nhóm trang |
| **6** | Review tactic đã làm | 6.1–6.7 | 6.1 sổ impact (việc → số đã đổi) · 6.2–6.6 bằng chứng ảnh · 6.7 hạng mục audit chờ phía client |
| **7** | OKRs | 7.1–7.3 | Chấm điểm kỳ vừa khép · danh sách carry-over · OKRs kỳ kế |
| **8** | Plan kỳ kế | 8.1–8.2 | Bảng việc GTV (`sow`) · hạng mục chờ quyết định kèm **số ngày chờ** (`support`) |
| — | Q&A | 43 | `qna` |
| **A** | Phụ lục | A.0–A.4 | A.0 dẫn nhập · A.1 chi tiết ngành/chủ đề · A.2 đối chiếu nguồn đo · A.3 những gì đã sửa trong kỳ · **A.4 nguồn dữ liệu + link** |
| — | Thanks | 49 | `thanks` |

Đây là khung, không phải khuôn cứng: section nào kỳ này không có chuyện để kể thì bỏ, đừng độn slide. Nhưng **§1, §7, §8 và A.4 là bắt buộc** — không có chúng thì deck không phải báo cáo kỳ.

## 3. Bốn luật riêng của deck kỳ

### 3.1 Luật hai lớp — mỗi section phải trả lời cả hai câu

«Tháng này so tháng trước thế nào?» và «Cả kỳ so cùng kỳ năm ngoái thế nào?». Chỉ trả lời một câu là báo cáo thiên lệch: tháng tốt che quý xấu (hoặc ngược lại). Slide đúc kết cuối mỗi section phải **ghép hai lớp** trong cùng một câu.

### 3.2 Luật forensics — nhóm giảm sâu phải phân rã tới nguyên nhân

Nhóm trang giảm > ~20% so cùng kỳ thì KHÔNG được dừng ở «giảm x%». Phải có tối thiểu:

1. Phân rã mức mất theo **nhóm URL / loại truy vấn** (slide bảng), không phải nói chung chung.
2. **Chữ ký chẩn đoán**: impressions và vị trí trung bình đi hướng nào so với clicks — tách «mất hạng» khỏi «mất cầu tìm kiếm» khỏi «mất hiển thị».
3. Danh sách **giả thuyết đã loại trừ** (viết ra), để người đọc biết kết luận không phải đoán.
4. Phần nào **khôi phục được** vs phần nào **không cam kết lấy lại** — nói thẳng, đừng hứa cả cụm.

Script hỗ trợ: `url_yoy_forensics.py`.

### 3.3 Luật nền so sánh — đổi nền thì phải khai

So cùng kỳ là chỗ dễ sai nhất và sai thì sai to. Trước khi render bất kỳ số YoY nào:

- **Đối chiếu định nghĩa event/metric giữa hai năm.** Kỳ Q1 CareerViet: 2025 đo bằng `ApplyThanks_Pmax`, 2026 đổi tên thành `Applythanks` — so cùng tên biến là so hai sự kiện khác nhau, ra −58,4% thay vì −10,95% thật.
- **Kiểm dòng «cùng kỳ» trên sheet có căn đúng tháng không.** Dòng YoY của sheet Run-rate từng lệch tháng (T5/26 ↔ T1/25).
- Nền thay đổi so với bản báo cáo trước → **slide phụ lục A.3 ghi trước/sau + lý do**. Không im lặng sửa số.
- Nền còn hai phạm vi đo chưa chốt → ghi cả hai + hạn chốt, KHÔNG chọn bừa số đẹp hơn.

### 3.4 Luật quy công — chỉ quy cho việc đã thực sự triển khai

Slide §6 là sổ impact, không phải bảng thành tích. Việc GTV đã bàn giao nhưng phía client **chưa triển khai** thì ghi rõ trạng thái chờ ở §6.7 và không được quy kết quả về nó. Kỳ Q1 CareerViet: audit bàn giao 30 hạng mục, chỉ 3/26 hạng mục điều chỉnh đã live — mọi kết quả crawl/AI bot quy về **đúng đợt robots.txt**, không quy cho filter/sitemap/schema.

## 4. Slide A.4 «Nguồn dữ liệu» — bắt buộc từ 04/08/2026

Deck kỳ đi tới cấp quản lý phía client; họ cần mở lại được số. Slide cuối phụ lục là bảng **workbook × tab (link) × slide dùng**, cộng một khối riêng liệt kê **nguồn chưa có link mở trực tiếp** và lý do. Link trỏ tới `#gid=` của tab, không phải trang chủ workbook.

Cách dựng: khai `source_links:` trong `report-config.yaml` → chạy `build_source_links.py` → dùng token `[[key]]` trong `data_meta` và trong ô bảng. Chi tiết: `report-config-schema.md` + `content-schema.md`.

Không bịa link. Nguồn không mở được (GA4/GSC chưa được cấp quyền, file rời chưa share) thì liệt kê ở khối «chưa có link» — đó cũng là đòn bẩy để client cấp quyền.

## 5. Ba cổng kiểm bắt buộc trước khi giao deck kỳ

| Cổng | Chạy bằng | Fail thì |
|---|---|---|
| **Đối chiếu tổng** — mọi nguồn URL-level cộng lại phải khớp BẢNG 1, ghi độ phủ % lên slide | `reconcile_totals.py` | Không render slide đó, hoặc render kèm chip scope ghi rõ độ phủ |
| **Kiểm công thức BẢNG 1** — tự tính lại Δ và % từ hai cột giá trị gốc rồi so với ô công thức trên sheet | `bang1_parser.py` | DỪNG, truy nguồn; ô sheet sai thì báo team sửa sheet, deck ghi số đúng + note ở A.3 |
| **Chống tràn slide** — đo `scrollHeight` từng slide vs 1080 | Playwright (xem RUNBOOK) | Rút nội dung slide, không thu nhỏ chữ dưới ngưỡng đọc được |

Cộng thêm gate tự động trong `build_deck.py` (build FAIL, không cảnh báo suông): còn `{{`, còn `{"t":`, còn `**` chưa render, còn `[[` chưa resolve, thiếu `data_meta` ở slide data.

## 6. Nhịp làm — deck kỳ mất khoảng 2 buổi, không phải 2 giờ

| Bước | Việc | Đừng làm |
|---|---|---|
| 1 | Kéo data kỳ + snapshot vào `02-raw/seo-data/<monthly\|quarterly>/<kỳ>/` | Đọc tab URL-level qua MCP — dùng CSV export |
| 2 | Chạy 3 cổng kiểm §5 TRƯỚC khi viết một chữ nào | Viết nhận xét rồi mới phát hiện nền sai |
| 3 | Viết `analysis/<kỳ>-insights.md` — nguồn của mọi nhận xét trên deck | Viết nhận xét thẳng vào content.yaml |
| 4 | Viết `content.yaml` (copy kỳ trước làm khung) | Sửa HTML tay |
| 5 | Build HTML → QA overflow → spot-check số | Giao deck chưa qua QA overflow |
| 6 | Build PPTX nếu client cần bản sửa được | Xuất PDF (luật HTML-only) |
| 7 | File-back: index bảng D + log op `report` + insights | Để tri thức chỉ nằm trong chat |

## 7. Khi client sửa thẳng trên file HTML

Chuyện thường: bản giao là HTML, client/Vincent sửa chữ trực tiếp trong đó. Khi ấy **YAML không còn là nguồn** — lần build kế tiếp sẽ xoá sạch phần sửa.

Luật xử lý (áp dụng 04/08/2026): **back-port trước, build sau.**

1. Diff bản HTML đã sửa với bản build gần nhất (bỏ base64 ảnh) → danh sách hunk.
2. Đổi từng hunk HTML về mini-markup (`<b>`→`**`, `<span class="up">`→`{pos}`, `<a href>`→`[nhãn](url)`) rồi áp vào YAML, tăng version YAML.
3. Build lại → **diff bản mới với bản client sửa: phải bằng 0** ở phần chữ. Khác chỗ nào là back-port sót chỗ đó.
4. Từ đó mới thêm nội dung mới lên bản YAML đã đồng bộ.

Bỏ qua bước này = mất chỉnh sửa của client, hoặc tệ hơn: giao lại bản cũ mà tưởng là bản mới.
