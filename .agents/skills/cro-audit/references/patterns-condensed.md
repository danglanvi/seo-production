# Pattern rút gọn — soi gì, theo thứ tự nào, mức nặng mặc định

Mục đích: bước 3 của cro-audit, bản standalone cho repo. Bản đầy đủ (lỗi hay gặp web VN, spec sửa mẫu, nguồn) ở wiki Inbound Marketing `concepts/cro/patterns/`. Chỉ nạp mục đã chọn ở bước 0. Mức nặng: P0 chặn hành động/mất dữ liệu/không đo · P1 cản/thiếu thông tin quyết định/nhập lại · P2 rõ hơn, nhanh hơn, tin hơn. R = phạm vi (R3 site-wide/template · R2 landing ưu tiên · R1 một trang). Bằng chứng cần: TH = tái hiện; S = số có mẫu số; R = recording; VOC.

## §1. Gọi · Zalo · Messenger (cơ chế)

Outcome: lead đạt chuẩn từ nhật ký gọi/Zalo OA/Sheet; click là micro.

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Nút gọi mở dialer đúng số theo task thực (chuẩn: `<a href="tel:…">`) | Bấm không mở dialer/không gọi được (P0); JS mở được nhưng không đo được (P1 đo); cùng số nhiều định dạng (P2) | P0/P1 R3 theo task | TH iOS+Android |
| 2 | Desktop bấm `tel:` có đường thay thế | Không phản hồi, không số hiển thị/QR Zalo | P1 R3 | TH desktop |
| 3 | Zalo: `zalo.me/<sđt>` · `oa.zalo.me/<oa>` · plugin không `<a>` | Link số cá nhân nghỉ việc; OA chưa xác thực; plugin không đi tiếp | P0/P1 R3 | TH + DOM |
| 4 | Messenger `m.me`/plugin FB | Bắt đăng nhập mất ngữ cảnh; plugin không tải | P1 R3 | TH mobile ẩn danh |
| 5 | Cụm nút nổi mobile | 4–6 icon che CTA/nút gửi form/cuối trang | P1 R3 | Ảnh 360/390 |
| 6 | CTA gọi/Zalo cạnh giá, proof, FAQ | Chỉ header/footer | P2 R2 | Heatmap |
| 7 | Giờ làm việc, auto-reply ngoài giờ | Không có; hotline số bàn tối không bắt máy | P1 R3 | Gọi/nhắn thử |
| 8 | Đo: GTM Just Links `tel:`/`zalo`; không tạo event trong GA4 UI; không bắn 2 lần | Không đo / đo trùng | P0/P1 | Preview+DebugView |
| 9 | Đối soát: Sheet lead có kênh/nguồn/kết quả | Không ai ghi | P1 R3 | Sheet tuần gần |
| 10 | Số nhất quán header/footer/schema/GBP | 3 số khác nhau | P1 R3 | So 4 nguồn |

## §2. Form lead (cơ chế)

Outcome: `generate_lead` sau backend 200 → lead đạt chuẩn ở CRM/Sheet.

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Gửi thử đúng/sai trên 3 môi trường | Lỗi im lặng, spinner, captcha chặn mobile, gửi trùng | P0 R3 | TH |
| 2 | Lead tới đích ≤10 phút (email/CRM/Sheet/Zalo báo) | Spam, webhook chết, nằm trong DB không ai xem | P0 R3 | Gửi thử |
| 3 | Success state: xác nhận + ai/kênh/bao lâu + đo được | "Cảm ơn" trần; alert JS không URL/tín hiệu | P1 R3 / P0 đo | TH + DebugView |
| 4 | Label hiện cố định, liên kết `for/id`; placeholder chỉ bổ sung | Placeholder thay label | P1 R3 | Ảnh + DOM |
| 5 | Validation: lỗi inline, cách sửa, giữ dữ liệu, không báo khi vừa focus | Lỗi chung chung; mất dữ liệu (P0) | P1 R3 | Nhập sai |
| 6 | Mobile: `type=tel/email`, font ≥16px, autofill đúng | Bàn phím chữ cho SĐT; zoom khi focus | P1 R3 | TH mobile |
| 7 | Field inventory: chỉ hỏi thứ cần cho liên hệ đầu; field qualify có lý do | Email bắt buộc với khách chỉ dùng Zalo; MST ở form đầu | P1 R2 | Bảng field + lý do |
| 8 | Một cột mobile, nhóm logic, tab order | Nhiều cột | P2 R3 | Ảnh |
| 9 | Copy nút theo outcome; không nút Reset | "Gửi"/"Submit" | P2 R3 | Ảnh |
| 10 | Form/nút dẫn form có ở trang dịch vụ; Zalo/gọi cạnh form | Chỉ ở trang Liên hệ | P1 R2 | Click map |
| 11 | Không PII trong GA4; consent nêu mục đích | SĐT trong parameter | P0 | Payload |

## §3. Báo giá theo yêu cầu (cơ chế)

Outcome: báo giá đã gửi → phản hồi → chốt (Sheet báo giá).

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Form + upload file lớn (8–20MB) gửi được, tới đích | Upload lỗi im lặng | P0 R3 | TH file thật |
| 2 | Giá tham khảo: "giá từ", bảng bậc số lượng, ví dụ đơn có giá | "Liên hệ" mọi nơi; bảng giá là ảnh | P1 R2 | So 3 đối thủ |
| 3 | Field quyết định giá (loại, số lượng, quy cách, deadline) là select/số; MST/ngân sách hỏi sau | Field giá là text tự do; hỏi MST đầu | P1 R3 | Bảng field |
| 4 | Upload: định dạng/kích thước rõ; chọn được từ Zalo/Drive mobile; đường "gửi file sau" | Không nêu; chặn ảnh | P1 R3 | TH mobile |
| 5 | SLA phản hồi ghi và thật | Không có / không đúng | P1 R3 | Gửi thử + đo |
| 6 | Calculator (nếu có) ra số gần báo giá thật, không bắt SĐT trước khi hiện | Lệch xa; bắt SĐT | P1 R2 | 3 kịch bản |
| 7 | Proof khớp: số lượng, thời gian, vật liệu | Ảnh stock | P2 R2 | Kiểm với client |
| 8 | Đường phụ Zalo/gọi/email doanh nghiệp | Không có | P1 R2 | Ảnh |
| 9 | Sau gửi: mã yêu cầu, bước tiếp, xác nhận đã nhận file | Không | P1 R3 | Gửi thử |
| 10 | Giá là HTML (AI/Google đọc được) | Ảnh/PDF | P2 R2 | HTML |

## §4. Giỏ hàng → checkout (cơ chế)

Outcome: `purchase` từ dataLayer sau backend tạo đơn (COD = đơn tạo) → đơn hợp lệ.

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Đặt thử end-to-end mobile: COD, QR, ví/cổng, thẻ | Cổng quay về trắng/404; đơn tạo 2 lần; huỷ vẫn "thành công" | P0 R3 | TH từng phương thức |
| 2 | `purchase` 1 lần, đúng chỗ, khớp backend | Bắn ở click; không bắn sau redirect; bắn lại khi reload | P0 R3 | DebugView + đối chiếu 7 ngày |
| 3 | Địa chỉ VN: tỉnh/quận/phường hiện hành, không mã bưu điện, ghi chú shipper | Danh mục cũ; bắt ZIP | P1 R3 (chọn không được → P0) | 3 địa chỉ thật |
| 4 | Phí ship + tổng tiền thấy sớm, không đổi bất ngờ | Chỉ ở bước cuối | P1 R3 | Ảnh từng bước |
| 5 | Guest checkout dễ thấy; tài khoản mời sau đơn | Ép đăng ký | P1 R3 | First-click/R |
| 6 | Field: SĐT là định danh, email tuỳ chọn, họ tên 1 ô, không MST cho khách lẻ | Ngược lại | P1 R3 | Field inventory |
| 7 | Lỗi coupon/thanh toán giữ giỏ và dữ liệu | Xoá form/giỏ | P0 R3 | Nhập sai |
| 8 | Ô coupon không nổi bật hơn nút đặt; áp mã có phản hồi | Ngược lại | P2 R3 | R |
| 9 | Giỏ: sửa số lượng cập nhật tổng; xoá có undo; mini-cart không che | Ngược lại | P1 R3 | TH |
| 10 | Chính sách đổi trả/kiểm hàng + hỗ trợ gần nút trả tiền | Không | P2 R3 | Ảnh |
| 11 | Sau đặt: xác nhận Zalo/SMS/email, tra đơn | Không | P1 R3 | Đặt thử |
| 12 | INP ≤200ms, CLS ≤0,1 ở checkout (field p75) | Script chat/ads làm chậm form | P1 R3 | Field data |

## §5. Apply → ATS (cơ chế)

Outcome: `application_complete` từ backend/ATS → hồ sơ đạt chuẩn (HR). Đơn vị candidate–job.

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Nộp thử mobile với CV PDF + ảnh; OTP | Upload lỗi; mất form khi chuyển app; OTP không tới | P0 R3 | TH có id |
| 2 | Hồ sơ tới ATS/HR ≤10 phút | Kẹt DB web; email spam | P0 R3 | Nộp thử |
| 3 | Biết nộp tại đâu (onsite/offsite); quay về không mất job | Rời site không báo | P1 R3 | R + TH |
| 4 | Tài khoản: không ép trước khi xem form; đăng ký xong giữ job | Ngược lại (mất ngữ cảnh → P0) | P1 R3 | TH |
| 5 | Field: không hỏi lại thứ đã có; screening ngắn sau CV; không text tự do vô hạn | Ngược lại | P1 R3 | Field + HR |
| 6 | Lưu nháp; ứng tuyển nhanh bằng hồ sơ đã lưu | Thoát mất hết | P1 R3 | TH |
| 7 | Sau nộp: mã hồ sơ, đã tới NTD, nơi xem trạng thái | "Cảm ơn" trần | P1 R3 | Nộp thử |
| 8 | Offsite: truyền job_id/source; callback hoặc file đối soát; không có → chỉ báo click-out | Gọi click là hồ sơ | P1 R3 đo | Hỏi HR/ATS |
| 9 | `directApply` đúng thực tế; tin hết hạn không nhận, `validThrough` đúng | Ngược lại | P1 R3 | Schema vs hành trình |
| 10 | CV/SĐT không vào analytics/recording; file CV không public | Ngược lại | P0 | Payload + URL |

## §6. Organic landing (loại trang)

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Màn hình đầu khớp top query GSC; hero ≤40% viewport mobile | H1 nói chuyện khác; hero che hết | P1 R2 | GSC × ảnh 390 |
| 2 | CTA theo lớp intent cụm; blog có cầu nối sang thương mại (CR-18) | Blog "Mua ngay" trên đầu; không cầu nối | P1 R2 | Bảng cụm × CTA |
| 3 | Thứ bậc CTA: 1 chính + phụ; giữ navigation | 3 nút cùng cỡ; xoá nav | P1 R2 | Ảnh + click map |
| 4 | Đường tới chuyển đổi ≤3 click hoặc có lý do (CR-16); không dead-end (CR-17) | >3 không lý do; dead-end | P1 R2 | Vẽ path |
| 5 | Trust gần điểm do dự, có nguồn, có phép | Cuối trang; logo không phép | P2 R2 | Ảnh |
| 6 | Không popup/cookie/chat che CTA khi vào từ Google | Popup ngay lập tức | P1 R3 | TH ẩn danh |
| 7 | LCP ≤2,5s · INP ≤200ms · CLS ≤0,1 (field p75, nhóm landing ưu tiên) | Vượt | P1 R2 | CrUX/GA4 |
| 8 | Breadcrumb / biết đang ở đâu | Không | P2 R3 | Ảnh |
| **AI** | Khách từ AI engine: trang tìm kiếm nội bộ dùng được (heading, filter, CTA — tách khỏi index policy); trang được AI trích có khối xác nhận **thông tin thật do client duyệt** ở màn hình đầu (AI sai → làm rõ, không sửa theo AI), CTA theo lớp intent | Trang search trống; thông tin thật ở giữa trang; giá cũ | P1 R2/R3 chỉ khi có AI traffic thật | GA4 landing kênh AI + câu AI trích |

## §7. Trang dịch vụ (loại trang)

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Cơ chế hoạt động (§1–§3 mục 1–3): task gọi/gửi/nhắn hoàn tất được | Task thất bại (thiếu `tel:` chỉ là dấu hiệu, kiểm JS có mở dialer không) | P0 R3 khi task thất bại | TH |
| 2 | Đúng việc, cho ai, khu vực ở màn hình đầu | H1 chung; không phạm vi | P1 R2 | Ảnh |
| 3 | Gồm/không gồm, quy trình có thời gian | Chỉ lợi ích | P1 R2 | So câu sale |
| 4 | Giá hoặc cách tính, bảng HTML | Không gì về giá; ảnh | P1 R2 | So 3 đối thủ |
| 5 | Proof khớp, có nguồn, có consent | Logo không phép; số không kiểm được (giả → P0) | P2 R2 | Kiểm với client |
| 6 | CTA theo mức sẵn sàng: gọi / để lại thông tin / xem giá, case | Một loại CTA lặp 6 lần | P1 R2 | Click map |
| 7 | CTA sau khối giá và sau proof | Chỉ hero + cuối | P2 R2 | Scroll map |
| 8 | FAQ mua hàng (giá, thời gian, bảo hành, thanh toán) | FAQ toàn SEO | P2 R2 | So câu sale |
| 9 | Giờ làm việc, SLA phản hồi thật | Không / không thật | P1 R3 | Hỏi + gọi thử |
| 10 | Local: NAP khớp GBP, bản đồ, chỉ đường | Lệch | P1 R3 | So GBP |
| 11 | Trang con khác trang cha đủ để chọn | Lặp 80% | P2 R2 | Đọc 3 trang |

## §8. PLP · filter · search (loại trang)

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Filter áp được, giữ state khi Back, đóng được trên mobile | Mất state; kẹt | P1 R3 (không áp → P0) | TH mobile |
| 2 | Bộ filter theo danh mục: 4–7 thuộc tính quyết định, tên khách hiểu | Chung cho mọi danh mục; thiếu thuộc tính chính | P1 R2 | Task test + câu sale |
| 3 | Count, chip đang áp, "bỏ tất cả", giá trị 0 kết quả bị mờ | Thiếu | P1 R3 | Ảnh |
| 4 | Zero-results có gợi ý (nới filter, danh mục gần, Zalo) | Trống | P1 R3 | 5 truy vấn |
| 5 | Search hiểu không dấu, đồng nghĩa/miền, SKU, model+dung lượng | Không | P1 R3 | 20 truy vấn từ log |
| 6 | Ô search thấy được mobile; autocomplete ưu tiên còn hàng | Ẩn sau icon; gợi ý hết hàng | P2 R3 | Thử |
| 7 | Trang kết quả search nội bộ dùng được như landing (AI traffic) | Trống/không CTA (index policy là kiểm tra khác, route technical) | P1 R3 nếu có AI traffic thật | GA4 kênh AI |
| 8 | Product card: giá, variant, tồn, ảnh cùng tỷ lệ | "Liên hệ" thay giá ở phần lớn sản phẩm (đếm tại client) | P1 R3 | Ảnh |
| 9 | Sort mặc định hợp lý; hết hàng không đứng đầu | Ngược lại | P2 R2 | Dữ liệu bán |
| 10 | Pagination/tải thêm giữ vị trí khi Back, crawl được | JS không URL | P1 R3 | TH + technical |
| 11 | Đoạn SEO không đẩy grid xuống 2 màn hình mobile | Ngược lại | P1 R2 | Ảnh 390 |
| 12 | Facet index policy | Index mọi tổ hợp / noindex facet có nhu cầu | Route technical | Crawl + GSC |

## §9. PDP (loại trang)

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Thêm vào giỏ với mọi tổ hợp variant; thiếu variant báo inline | Không thể thêm bằng cách nào (P0); không báo nhưng chọn xong vẫn mua được (P1); hết hàng vẫn thêm; "Mua ngay" mất variant | P0/P1 R3 theo task | TH mobile |
| 2 | Variant: swatch có trạng thái còn/hết, ảnh đổi theo màu, bảng size | Dropdown mù | P1 R3 | Ảnh + TH |
| 3 | Giá đang áp dụng rõ; phí ship ước tính; VAT/lắp đặt không phát sinh ở checkout | Mơ hồ | P1 R3 | So checkout |
| 4 | Tồn kho + ước ngày nhận theo tỉnh; đúng thực tế | "Còn hàng" rồi hết (P0) | P1 R3 | Đặt thử |
| 5 | Gallery zoom, tỷ lệ đồng nhất, ảnh bối cảnh/kích thước thật | Ngược lại | P2 R3 | Ảnh |
| 6 | Thông số quyết định là bảng HTML ngay dưới buy box; so sánh model gần | Spec là ảnh; mô tả SEO 1.500 chữ trên spec | P1 R2 | Câu sale/Zalo |
| 7 | Review/spec/Q&A mobile không subpage mất vị trí; accordion mở mục quan trọng | Subpage Back mất chỗ | P1 R3 | R + TH |
| 8 | Buy box sticky mobile không che nội dung | Trôi mất / che | P1 R3 | Ảnh cuộn |
| 9 | Review thật có ngày/ảnh; Q&A được trả lời | Giả (P0 pháp lý) | P2 R3 | Nguồn với client |
| 10 | Zalo/gọi tư vấn cạnh buy box cho hàng cần tư vấn | Không | P1 R2 | Ảnh |
| 11 | Chính sách đổi trả/bảo hành/kiểm hàng ở PDP | Không | P2 R3 | Ảnh |
| 12 | Product schema/offer/availability; giá HTML | Không; ảnh | P2 R3 (route schema) | HTML |
| 13 | LCP ảnh gallery ưu tiên; không CLS khi load giá/variant | Ngược lại | P1 R3 | Field p75 |

## §10. Tìm việc · job detail · nhà tuyển dụng (loại trang)

| # | Kiểm | Lỗi | Mức | BC |
|---|---|---|---|---|
| 1 | Search: tên nghề địa phương, không dấu, viết tắt; địa điểm tới quận/KCN | "ke toan"/"sale" không map; chỉ tỉnh | P1 R3 | 30 truy vấn |
| 2 | Filter: lương, kinh nghiệm, hình thức, ca; giữ state | Thiếu; mất | P1 R3 | Task test |
| 3 | Job card: lương, địa điểm cụ thể, ngày đăng/hạn, logo | "Thoả thuận" 80% | P1 R3 | Đếm tỷ lệ |
| 4 | Job detail 6 thông tin ở màn hình đầu (vị trí, công ty, địa điểm/hình thức, lương, yêu cầu chính, hạn) | 300 chữ giới thiệu trước; lương cuối | P1 R3 | Ảnh 390 |
| 5 | CTA ứng tuyển sticky mobile, nói nộp ở đâu; "Lưu" là phụ | Không sticky; cùng cỡ | P1 R3 | Ảnh cuộn |
| 6 | Tin hết hạn: không nhận, ghi ngày, gợi ý việc tương tự, `validThrough` | Vẫn nhận | P1 R3 | Danh sách quá hạn |
| 7 | Việc tương tự cùng nghề/địa điểm | Ngẫu nhiên | P2 R3 | Ảnh |
| 8 | Trang công ty có quy mô/ngành; cơ chế báo cáo tin lừa | Trống (lừa đảo → P0) | P1 R3 | 20 tin ngẫu nhiên |
| 9 | JobPosting: `baseSalary` khi có lương, `directApply` đúng | Sai | Route schema | Rich Results |
| E1–E5 | Nhà tuyển dụng: đăng ký không hỏi MST/giấy phép trước khi thấy gói; đăng tin có mẫu theo nghề + lưu nháp + xem trước; bảng gói so sánh được; dashboard hồ sơ/lượt xem; thanh toán online kích hoạt ngay | Ngược lại | P1 R3/R2 | TH + hỏi client |

Phía nhà tuyển dụng và toàn bộ "tình huống cần kiểm trên web VN" trong wiki là giả thuyết chưa xác nhận tại client (không có log quan sát có mẫu); không dùng làm E2/E3; dùng bằng chứng client thay cho benchmark.
