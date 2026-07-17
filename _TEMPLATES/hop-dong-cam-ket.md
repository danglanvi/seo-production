---
client: "{{CLIENT}}"
domain: "{{DOMAIN}}"
so_hop_dong: "{{SO_HD}}"
ngay_ky: "{{YYYY-MM-DD}}"
mo_hinh: "{{thực thi | advisory}}"
goi_timeline: "{{8|10|12}} tháng"
nguon: "02-raw/contracts-proposals/{{file-hd-goc}}"
status: draft
version: v1
last_updated: "{{YYYY-MM-DD}}"
---

# {{CLIENT}} — Hợp đồng cam kết (bản chưng cất)

> Output của thao tác **Ingest** khi hợp đồng vào `02-raw/contracts-proposals/`. Đích: `00-client-context/hop-dong-cam-ket.md`.
> File này là **schema vận hành**, KHÔNG thay thế hợp đồng pháp lý. Mọi tranh chấp/nghi vấn → tra hợp đồng gốc + Phụ lục.
> 🔒 Khi đã điền, file chứa giá trị hợp đồng thật — chỉ dùng trong instance, không copy vào deliverable hướng ra ngoài.

## 0. Luật điền

1. Nguồn duy nhất = hợp đồng gốc + Phụ lục + Tài liệu kỹ thuật trong `02-raw/contracts-proposals/`. Không suy diễn số liệu.
2. Chưng cất CƠ CHẾ + THAM SỐ, kèm vị trí nguồn (Điều/Phụ lục) để truy vết. Không chép nguyên văn điều khoản pháp lý.
3. Trường hợp đồng không có → ghi `n/a`. Không để trống, không để `{{...}}` sót lại.
4. Mọi giá trị tiền ghi rõ đã/chưa VAT.
5. Hợp đồng sửa đổi bằng phụ lục mới → update file này + ghi mục 8 + tăng version + log op `ingest`.
6. Điền xong → đồng bộ 2 nơi: bảng A `index.md` (dòng Hợp đồng, KPI cam kết, Mô hình) + `00-client-context/kpi-commitments.md`.

## 1. Thông tin hợp đồng

| Trường | Giá trị | Nguồn |
|---|---|---|
| Bên A (client) | {{PHAP_NHAN_CLIENT}} | {{Điều/trang}} |
| Website cam kết | {{DOMAIN}} | {{...}} |
| Số HĐ / Ngày ký | {{SO_HD}} / {{NGAY_KY}} | {{...}} |
| Ngày bắt đầu triển khai | {{ngày nhận khoản thanh toán đầu tiên \| ngày email xác nhận}} — mọi timeline/KPI tính từ mốc này | {{...}} |
| Thời hạn | {{N}} tháng + gia hạn cuối kỳ {{60}} ngày KPI + {{30}} ngày hồ sơ | {{...}} |
| Mô hình | {{thực thi \| advisory}} (biến thể khác: platform/global → ghi rõ) | {{...}} |
| Giá trị hạng mục công việc | {{X}} VNĐ (chưa VAT) | {{...}} |
| Giá trị gói KPI cam kết | {{Y}} VNĐ (chưa VAT) | {{...}} |
| VAT ({{8}}%) | {{Z}} VNĐ | {{...}} |
| Tổng giá trị | {{TONG}} VNĐ (đã VAT) | {{...}} |
| Số đợt thanh toán | {{N_DOT}} đợt ({{chia đều theo tháng \| theo mốc}}) | {{...}} |
| Công cụ đo đã chốt | {{vd: SpySERP = thứ hạng · GA4 = Organic Session · Ahrefs = Citation AIO}} | {{Điều Định nghĩa}} |
| Thứ tự ưu tiên tài liệu | {{HĐ chính > Phụ lục > Tài liệu kỹ thuật}} | {{...}} |
| Điều khoản đặc thù khác | {{độc quyền ngành: có/không · song ngữ: có/không · ngoại tệ: có/không}} | {{...}} |

## 2. Bảng KPI cam kết

| # | KPI | Loại | Mức cam kết | Công thức đo | Nguồn data / công cụ | Trọng số | Giá trị quy đổi (chưa VAT) | Mốc tính |
|---|---|---|---|---|---|---|---|---|
| 1 | {{TOP 3 bộ từ khóa duy trì}} | duy trì | {{x% / y từ trên tổng Z từ}} | {{% từ khóa đạt TOP theo bộ Phụ lục}} | {{SpySERP}} | {{...}}% | {{...}} | {{từ T{{n}}}} |
| 2 | {{TOP 3/5/10 bộ từ khóa thúc đẩy}} | thúc đẩy | {{x% / y từ trên tổng Z từ}} | {{% từ khóa đạt TOP tại thời điểm nghiệm thu}} | {{SpySERP}} | {{...}}% | {{...}} | {{T{{n}}}} |
| 3 | {{Organic Session / Organic Traffic}} | {{duy trì \| thúc đẩy}} | {{n session/tháng \| tổng kỳ}} | {{session kênh Organic theo định nghĩa HĐ}} | {{GA4}} | {{...}}% | {{...}} | {{từ T{{n}}}} |
| 4 | {{KPI business-outcome — vd pageview cụm URL, lượt chuyển đổi/ứng tuyển}} | thúc đẩy | {{tổng N trong kỳ}} | {{chép NGUYÊN định nghĩa metric: báo cáo + filter + nguồn/phương tiện + phạm vi URL}} | {{GA4 + báo cáo cụ thể}} | {{...}}% | {{...}} | {{...}} |
| 5 | {{Citation AI Overview}} | GEO | {{N từ khóa được cite}} | {{số keyword website xuất hiện trong AIO}} | {{Ahrefs \| SemRush + check thủ công}} | {{...}}% | {{...}} | {{...}} |
| 6 | {{Brand Mention LLM}} | GEO | {{xuất hiện ≥{{2}}/{{4}} công cụ AI}} | {{bộ prompt tracking đã thống nhất, check ẩn danh}} | {{ChatGPT/Gemini/Perplexity/AI Mode}} | {{...}}% | {{...}} | {{...}} |
| — | **Tổng** | | | | | **100%** | {{= giá trị gói KPI}} | |

Luật đọc bảng:

1. Tổng trọng số bắt buộc = 100%. Lệch → tra lại Phụ lục, không tự cân.
2. TOP lồng nhau (nếu HĐ áp dụng): TOP 3 ⊂ TOP 5 ⊂ TOP 10 — 1 từ khóa được ghi nhận đồng thời nhiều mức, không tính trùng giá trị nghiệm thu.
3. TOP chỉ tính liên kết tự nhiên — không tính ảnh/video/Maps/Ads/AI Overview (theo Điều Định nghĩa, nếu HĐ chốt vậy).
4. KPI business-outcome: KHÔNG tóm tắt định nghĩa metric — chép đủ nguồn/filter/phạm vi URL vào cột Công thức đo. Sai định nghĩa = sai số nghiệm thu.
5. KPI GEO trọng số 0% (chỉ cam kết thiện chí, không gánh tiền) vẫn phải có dòng riêng + ghi `0%`.
6. KPI thiếu công thức đo hoặc nguồn data → hỏi Account/SEO Lead, không tự bịa.

### 2.1 Định nghĩa đo lường per KPI

| KPI | Công cụ | Đường lấy số (báo cáo/filter) | Chu kỳ chốt số |
|---|---|---|---|
| {{KPI #1}} | {{...}} | {{vd: mục báo cáo + filter + bước thao tác theo Tài liệu kỹ thuật}} | {{tháng \| đợt \| cuối kỳ}} |
| {{KPI #4}} | {{...}} | {{...}} | {{...}} |

## 3. Điều khoản thanh toán theo KPI

| Đợt | Số tiền (đã VAT) | Điều kiện giải ngân | Hạn thanh toán |
|---|---|---|---|
| 1 | {{...}} | {{sau ký HĐ — vai trò tạm ứng/khởi động, triển khai tính từ khi nhận khoản này}} | {{trong {{5\|15}} ngày làm việc}} |
| 2..{{n-1}} | {{...}} | {{sau nghiệm thu tháng/đợt tương ứng đạt ngưỡng mục 3.1}} | {{trong {{N}} ngày làm việc từ khi nhận hồ sơ}} |
| {{n}} (cuối) | {{...}} | {{sau BBNT cuối + thanh lý; quyết toán theo trọng số KPI}} | {{trong {{N}} ngày làm việc}} |

### 3.1 Cơ chế nghiệm thu — thanh toán (schema)

1. **Nghiệm thu 2 lớp**: (a) theo đợt = bình quân cộng tỷ lệ hoàn thành các hạng mục ≥ {{75}}% để giải ngân — mỗi hạng mục tối đa 100%, cấm bù chéo; (b) quyết toán cuối = theo % trọng số từng KPI → chênh lệch bù/hoàn trong {{N}} ngày.
2. **Gia hạn bậc thang khi miss**: chưa đạt ngưỡng đợt → +{{30}} ngày → +{{30}} ngày; cuối kỳ → +{{60 ngày KPI + 30 ngày hồ sơ \| 2 tháng}}; Google core update → +{{1-2}} tháng. Hết gia hạn vẫn thiếu → sang luật hoàn trả (3).
3. **Hoàn trả**: hạng mục công việc = số đầu việc chưa làm × đơn giá (bảng mục 4). KPI = {{theo bậc TOP: đạt TOP3 hoàn 0% · TOP4-5 hoàn {{20}}% · TOP6-10 hoàn {{30}}% · ngoài TOP10 hoàn 100% | theo % tỷ lệ chưa đạt}}. KPI duy trì: giá trị phân bổ đều theo tháng, đối chiếu timeline từng tháng.
4. **Sàn KPI** (nếu HĐ có): KPI đạt dưới {{50}}% {{hoặc tăng trưởng < 0%}} → client không thanh toán phí gói KPI. Ghi rõ ngưỡng + phạm vi áp dụng.
5. **Công thức khi kéo dài thời gian**: mức đạt trung bình = (tổng đạt toàn kỳ thực tế ÷ số tháng thực tế) × số tháng cam kết.
6. **Chậm thanh toán**: lãi {{8}}%/năm ({{2 chiều — áp cho cả hoàn trả chậm}}); quá {{15}} ngày sau gia hạn → GTV được tạm ngưng dịch vụ, thời gian tạm ngưng không tính vào tiến độ.
7. **Review định kỳ giữa kỳ** (nếu HĐ có): mốc {{6}} tháng; KPI lũy kế < {{60}}% → GTV nộp phương án khắc phục trong {{5}} ngày; phương án không đủ cơ sở → client được đơn phương chấm dứt, thanh toán theo khối lượng thực tế.

## 4. Phạm vi công việc / loại trừ

### 4.1 Hạng mục công việc (căn cứ nghiệm thu đầu việc + đơn giá hoàn trả)

| Hạng mục | Đơn vị | Số lượng | Đơn giá | Thành tiền | Ghi chú |
|---|---|---|---|---|---|
| {{vd: Phân tích thị trường + chiến lược}} | {{gói}} | {{...}} | {{...}} | {{...}} | {{...}} |
| {{vd: OKRs theo quý}} | {{gói}} | {{...}} | {{...}} | {{...}} | {{...}} |
| {{vd: Audit toàn diện / định kỳ}} | {{gói}} | {{...}} | {{...}} | {{...}} | {{...}} |
| {{vd: Content chỉnh sửa / viết mới}} | {{bài}} | {{...}} | {{...}} | {{...}} | {{...}} |
| {{vd: Onpage URL}} | {{URL}} | {{...}} | {{...}} | {{...}} | {{...}} |
| {{vd: Backlink/Contextual link}} | {{link}} | {{...}} | {{...}} | {{...}} | {{ràng buộc chất lượng → mục 7}} |

### 4.2 Loại trừ + điều kiện phối hợp

| # | Nội dung | Tham số |
|---|---|---|
| 1 | Việc ngoài phạm vi Phụ lục → báo giá riêng bằng văn bản, không ảnh hưởng nghiệm thu kỳ | {{...}} |
| 2 | Technical fix trên website thuộc {{client \| GTV}}; client sửa theo danh mục audit trong SLA {{15}} ngày; trễ → cộng dồn tiến độ | {{Điều/khoản}} |
| 3 | Giới hạn vòng sửa deliverable: {{2}} lần/hạng mục; vượt → tính phí phát sinh | {{...}} |
| 4 | Client cấp quyền {{GA4, GSC, CMS, ...}} cho {{email admin GTV}} — chậm cấp → cộng dồn tiến độ | {{...}} |
| 5 | Bên thứ ba SEO cùng website (nếu HĐ cho phép): client thông báo trong {{7}} ngày + scope không overlap + không can thiệp hạng mục GTV phụ trách | {{...}} |

## 5. Mốc nghiệm thu + cơ chế BBNT

| Mốc | Thời điểm | Nội dung nghiệm thu | Hồ sơ |
|---|---|---|---|
| Tháng/đợt | {{cuối mỗi tháng \| theo đợt}} | Bình quân cộng hạng mục theo timeline Phụ lục ≥ {{75}}% | Báo cáo tiến độ & KPI + đề nghị thanh toán |
| Giữa kỳ (nếu có) | {{T6}} | Review KPI lũy kế vs {{60}}% | Báo cáo review |
| Cuối kỳ | {{T{{N}} + gia hạn}} | Quyết toán toàn bộ KPI theo trọng số | Báo cáo tổng + BBNT + thanh lý |

Cơ chế BBNT:

1. Client phản hồi hồ sơ nghiệm thu trong {{7}} ngày làm việc. Quá hạn không phản hồi, hoặc tiếp tục sử dụng sản phẩm → mặc nhiên chấp thuận nghiệm thu.
2. Từ chối nghiệm thu phải bằng văn bản/email, nêu đủ 4 nội dung: hạng mục chưa đạt · căn cứ đánh giá · dữ liệu đối chiếu · yêu cầu sửa cụ thể. Thiếu → không tính là từ chối hợp lệ.
3. BBNT qua email có giá trị pháp lý ngang văn bản (nếu HĐ chốt vậy — ghi rõ: {{có/không}}).
4. Client chậm phản hồi → GTV được tạm dừng, số ngày chậm cộng dồn vào tiến độ.
5. Nghiệm thu TOP trùng lễ/Tết → chốt số sau kỳ nghỉ {{2}} ngày (nếu HĐ có).
6. **Bảo hành**: duy trì ≥ {{90}}% kết quả nghiệm thu trong {{30}} ngày sau BBNT (dự trù {{10}}% rủi ro Google update).
7. Tháng cuối chạy chế độ NGHIỆM THU của template `bao-cao-thang.md` (họp nghiệm thu + auto-accept + bảo hành).

## 6. Advisory vs thực thi — ai làm gì

Điền cột đúng mô hình; mô hình advisory phải map sang cột Thực thi của bảng B `index.md` (SETUP bước 5).

| Hạng mục | Thực thi (GTV làm) | Advisory (phân vai) |
|---|---|---|
| Chiến lược, kế hoạch, OKRs | GTV | GTV |
| Audit + phương án điều chỉnh | GTV | GTV |
| Content (brief → viết → đăng) | GTV | {{GTV brief + QC · client viết/đăng}} |
| Onpage + internal link | GTV | {{client thực thi theo chỉ đạo GTV}} |
| Backlink | GTV | {{GTV plan · client đặt link}} |
| Technical fix | {{client dev \| GTV}} | client dev |
| Đào tạo + chuyển giao quy trình | n/a | GTV ({{phạm vi: Semantic SEO, Onpage, Content, Entity, Technical...}}) |
| Giám sát + meeting định kỳ | GTV nội bộ | GTV → team in-house, nhịp {{...}} |

Luật riêng mô hình advisory (schema — chỉ áp khi `mo_hinh: advisory`):

1. Bản chất = quản lý + cố vấn chuyên môn; quan hệ dịch vụ độc lập, KHÔNG phải quan hệ lao động. Client toàn quyền tuyển/quản/trả lương nhân sự mình.
2. KPI = mục tiêu chung 2 bên. Phân định: GTV chịu chất lượng chiến lược/kế hoạch/cảnh báo; client chịu chất lượng + tiến độ thực thi.
3. Miss KPI phân loại nguyên nhân theo hồ sơ 2 phía (hồ sơ cố vấn GTV vs hồ sơ thực thi client): (a) do thực thi client → client chịu, GTV re-plan KPI; (b) do cố vấn GTV → xử theo luật hoàn trả Phụ lục; (c) khách quan/bất khả kháng → điều chỉnh KPI theo thỏa thuận.
4. Client không thực thi đúng/đủ theo cố vấn dù GTV đã cảnh báo → mặc nhiên nhóm (a), trừ khi client chứng minh ngược bằng tài liệu.
5. GTV được đánh giá năng lực nhân sự client + đề xuất thay thế; client không xử lý trong {{N}} ngày → trách nhiệm KPI thuộc client.
6. SLA phản hồi của GTV: {{24 giờ \| 4 giờ}} làm việc.

## 7. Rủi ro & điều khoản bảo vệ 2 bên (schema)

| # | Nhóm điều khoản | Cơ chế trong HĐ | Tham số | Nguồn |
|---|---|---|---|---|
| 1 | Miss KPI / chậm tiến độ | KHÔNG cấu thành vi phạm nghiêm trọng, không là căn cứ hủy HĐ — xử bằng gia hạn + hoàn trả (mục 3) | {{có/không}} | {{Điều}} |
| 2 | Vi phạm nghiêm trọng (định nghĩa hẹp) | Bên A: chậm thanh toán > {{15}} ngày sau gia hạn · SHTT · bảo mật-liêm chính. Bên B: SHTT · bảo mật-liêm chính. Kèm thời hạn khắc phục {{14}} ngày trước khi được chấm dứt | {{...}} | {{...}} |
| 3 | Đơn phương chấm dứt sai căn cứ | Bồi thường = giá trị {{1 tháng triển khai}} (tổng chưa VAT ÷ số tháng) + thanh toán phần đã làm | {{...}} | {{...}} |
| 4 | Trần bồi thường | Tổng trách nhiệm GTV ≤ {{tổng giá trị HĐ chưa VAT}} | {{...}} | {{...}} |
| 5 | Bất khả kháng | Gồm {{Google/AI update toàn ngành: có/không}}; thông báo trong {{N}} ngày; kéo dài > {{N}} tháng → được chấm dứt | {{...}} | {{...}} |
| 6 | Client / bên thứ ba tự sửa web | GTV miễn trừ KPI trong thời gian ảnh hưởng; quy trình: thông báo + evidence trong {{5}} ngày → họp trong {{7}} ngày → biên bản điều chỉnh KPI; thời gian ảnh hưởng không tính tiến độ | {{...}} | {{...}} |
| 7 | Client chậm phối hợp / chậm cấp quyền | Cộng dồn tiến độ + GTV được tạm ngưng sau cảnh báo {{14}} ngày | {{...}} | {{...}} |
| 8 | SHTT | Tài nguyên client thuộc client; phương pháp/kỹ thuật/dữ liệu SEO của GTV thuộc GTV — client không dùng ngoài HĐ | {{...}} | {{...}} |
| 9 | Bảo mật + liêm chính | Đối xứng 2 chiều; GTV được nêu tên dự án cho mục đích quảng bá: {{có/không}} | {{...}} | {{...}} |
| 10 | Chất lượng backlink | PBN ≤ {{35}}% tổng link; bảo trì link ≥ {{6}} tháng | {{...}} | {{...}} |
| 11 | Chấm dứt giữa chừng | Thanh toán/hoàn trả theo phần đã thực hiện (đơn giá công việc + % KPI tại thời điểm chấm dứt); chốt số KPI sau {{30}} ngày từ thông báo | {{...}} | {{...}} |
| 12 | Ngoại tệ (chỉ HĐ global) | Đồng tiền niêm yết + tỷ giá quy đổi + phí chuyển quốc tế + thuế nhà thầu | {{n/a nếu HĐ nội địa}} | {{...}} |

Luật: gặp điều khoản nằm ngoài 12 nhóm trên → thêm dòng mới + báo SEO Lead trong report ingest. Không bỏ sót điều khoản có hệ quả tiền/tiến độ.

## 8. Lịch sử phụ lục / sửa đổi

| Phụ lục | Ngày ký | Thay đổi chính | File nguồn |
|---|---|---|---|
| {{PL số}} | {{YYYY-MM-DD}} | {{đổi KPI/giá/timeline gì}} | `02-raw/contracts-proposals/{{file}}` |

## 9. Done-criteria

- [ ] `grep -n "{{" file` = 0 hit; trường không có trong HĐ đã ghi `n/a`.
- [ ] Tổng trọng số KPI = 100%; mỗi KPI có đủ công thức đo + nguồn data + mốc tính.
- [ ] Tổng các đợt mục 3 = tổng giá trị HĐ (đã VAT); giá trị công việc + gói KPI + VAT khớp mục 1.
- [ ] KPI business-outcome (nếu có) chép đủ định nghĩa metric: nguồn/filter/phạm vi URL.
- [ ] Mô hình khớp 3 nơi: frontmatter `mo_hinh` + bảng mục 6 + cột Thực thi bảng B `index.md`.
- [ ] Mỗi dòng mục 7 có cột Nguồn (Điều/Phụ lục) — không có dòng nào chép nguyên văn điều khoản.
- [ ] Đã đồng bộ bảng A `index.md` + `00-client-context/kpi-commitments.md`.
- [ ] Log có entry op `ingest` (Files touched gồm file này + file HĐ gốc trong bảng D).
