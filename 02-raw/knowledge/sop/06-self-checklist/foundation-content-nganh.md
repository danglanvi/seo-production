---
type: sop
phase: marketing-foundation
cong_doan: 3
tier_role: foundation-template
last_updated: 2026-07-19
items_count: 34
source_files:
  - "raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/Content SEO/Checklist các trường hợp Content trao đổi với khách hàng và Action.xlsx"
  - "raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/Content SEO/Checklist lưu ý điểm then chốt cho các lĩnh vực dự án.xlsx"
  - "raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/Content SEO/Checklist riêng cho từng dự án [Lưu hành nội bộ].xlsx"
  - "raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/Content SEO/Checklist đa dạng hóa hình ảnh, video, infographic cho dự án hợp đồng 40tr_tháng.xlsx"
related_wiki:
  - "[[Source Context]]"
  - "[[Brand Identity]]"
  - "[[Buyer Persona]]"
  - "[[Central Search Intent]]"
  - "[[E-A-V Framework]]"
  - "[[VIP Sources]]"
tags: [sop, foundation-checklist, marketing-foundation, content-nganh, client-context, tier-2-source]
---

# Foundation Checklist — Content Ngành (công đoạn #3, Marketing Foundation)

> **Template-checklist nền** để mỗi dự án mới dựng "checklist content ngành" riêng. Gộp + hiện đại hóa 4 checklist legacy (2020-2022) thành 1 bộ 4 module / 34 items (FD-01…FD-34).
> Output của checklist này **đổ vào `00-client-context/marketing-foundation.md`** của SEO Production instance (mục 3 "Checklist content ngành" + mục 4 "Brand guideline content & SEO").

## Định vị trong quy trình

| Thuộc tính | Giá trị |
|---|---|
| Công đoạn | **#3 — Marketing Foundation** (Buyer Persona + Customer Journey + **checklist content ngành** + Brand Guideline content & SEO + Source Context) |
| Thời điểm | **T1** — song song/ngay sau kick-off Account (`acc-kickoff-setup`) |
| PIC | **Content + SEO** (điền + phỏng vấn khách) |
| Duyệt | **SEO Lead + Content Leader** |
| Downstream | Topical map (#10), content plan (WS 05), fork `Content Production - <client>/`, Tracking Sheet content |

**Quan hệ với tier-2 (`tier-2-project-specific.md`):** Foundation checklist này là **NGUỒN dữ kiện để PM/Lead bật tier-2 items** tại kick-off nội bộ. Tier-2 là lớp gần nhất phía trên: câu trả lời ở Module B/C ở đây quyết định cột nào được thêm vào Tracking Sheet (map cụ thể tại FD-25). Foundation trả lời "ngành/khách này CẦN gì" — tier-2 thực thi "mỗi bài phải tick gì".

**Cách dùng:** đây là checklist-để-dựng-checklist. Mỗi item là một việc phải HỎI/CHỐT/GHI khi onboard dự án mới; kết quả ghi thành checklist ngành riêng của dự án, không copy nguyên văn template.

---

## 🔴 P0 Gate — phải xong TRƯỚC khi pipeline content chạy bài đầu tiên

5 items sau chưa xong → chưa được brief bài nào cho Writer:

| Gate | Item | Vì sao chặn |
|---|---|---|
| G1 | FD-04 — Đầu mối trả lời + đầu mối duyệt phía khách | Không có người chốt → mọi câu hỏi ngành treo, bài viết sai không ai chịu |
| G2 | FD-02 — USP · POPs · Benefits · giá · chính sách đã chốt bằng văn bản | Thiếu → Writer tự bịa claim thương mại, rủi ro cao nhất của content agency |
| G3 | FD-10 — YMYL flag + cấm kỵ pháp lý ngành | Viết trước, phát hiện sau = gỡ bài + mất trust với khách |
| G4 | FD-18 — Văn phong + danh xưng per content type | Sai tone từ bài 1 → sửa hàng loạt, khách mất niềm tin sớm nhất ở điểm này |
| G5 | FD-28 — Media mix + nguồn ảnh (thật/stock/generate) đã chốt | Quyết định sau khi viết → bottleneck design, bài chờ ảnh không publish được |

---

## Module A — Trao đổi khách hàng về content (FD-01 → FD-08)

Nguồn: "Checklist các trường hợp Content trao đổi với khách hàng và Action.xlsx" (2021). Legacy là 4 tình huống xử lý sự cố; bản này chuyển thành **các việc phải hỏi/chốt CHỦ ĐỘNG trước khi viết** để tình huống không xảy ra.

### FD-01 — Training sản phẩm/dịch vụ từ khách `[GIỮ — legacy #1]`
Nhờ khách training chi tiết SP/DV trước khi viết bài đầu: cung cấp gì, giá cả, lợi ích, tính năng, USP, sản phẩm best-seller, combo, số lượng SKU, những lưu ý bắt buộc trong bài viết. Ghi thành tài liệu trong `02-raw/` của instance + bảng Source context (mục 5 marketing-foundation.md). Buổi training này lấy luôn input cho [[Source Context]] và Buyer Persona.

### FD-02 — Chốt bằng văn bản: USP · POPs · Benefits · giá · chính sách 🔴 `[SỬA — legacy #1, tách riêng vì là P0]`
Mọi claim thương mại Writer được phép dùng phải nằm trong danh sách khách đã duyệt: USP (điểm khác biệt), POPs (points of parity — điểm ngang bằng thị trường được phép nói), Benefits per persona, bảng giá (kèm link nguồn + ngày hiệu lực), chính sách (bảo hành, đổi trả, vận chuyển, thanh toán). Không có trong danh sách → không viết, hỏi lại. Đây là nguồn cho block điều hướng SP/DV (FD-23).

### FD-03 — Danh sách chủ đề/thông tin NHẠY CẢM phải hỏi trước khi viết `[MỚI — nâng cấp từ tinh thần legacy #1, #3]`
Lập danh sách các trường hợp bắt buộc dừng-và-hỏi khách: claim pháp lý/y khoa, so sánh trực tiếp đối thủ, cam kết hiệu quả ("giảm X% sau Y ngày"), thông tin chưa công bố (giá sắp đổi, SP sắp ra), nội dung nói về đối tác/nhà cung cấp của khách. Mỗi dự án liệt kê cụ thể theo ngành (input từ Module B).

### FD-04 — Đầu mối trả lời + đầu mối duyệt phía khách 🔴 `[MỚI — kế thừa acc-kickoff-setup nhóm Con người]`
Chốt từ kick-off Account: (1) ai TRẢ LỜI câu hỏi chuyên môn ngành, (2) ai DUYỆT outline/bài (có quyền chốt cuối), (3) kênh hỏi-đáp chính thức (group chat/email/sheet comment), (4) format chốt — mọi câu trả lời quan trọng phải được ghi lại thành văn bản trong instance, không nằm trong chat trôi. Lấy trực tiếp từ checklist "Con người + Quy trình làm việc" của `acc-kickoff-setup`, không hỏi khách lần hai.

### FD-05 — SLA review outline/bài + cơ chế quá hạn `[GIỮ — legacy #2]`
Chốt deadline review cụ thể với khách (thường +2-3 ngày thư thả). Quá deadline → team SEO đăng bài để kịp tiến độ, hoàn thiện theo feedback sau hoặc trong nhịp audit content định kỳ. Ghi rõ cơ chế này vào biên bản kick-off để không thành tranh chấp. Đối chiếu SLA duyệt content trong hợp đồng (acc-kickoff-setup đã trích).

### FD-06 — Chuẩn feedback của khách `[GIỮ — legacy #2]`
Trước vòng review đầu, note khéo với khách (Account hỗ trợ): feedback cần rõ ràng, chỉ đúng điểm sai + lý do, không "sai nhưng không nói sai chỗ nào". Feedback mẫu tốt/xấu đưa vào agenda kick-off.

### FD-07 — Nguyên tắc dung hòa: định hướng khách vs Search Intent `[GIỮ — legacy #3]`
Khi định hướng/thông điệp khách mâu thuẫn với intent SERP: (1) giải thích vì sao phải theo intent (Google nhận diện đúng → mới có ranking, có ranking thông điệp mới ai đó đọc); (2) khách vẫn giữ ý → triển khai dung hòa trong outline, đảm bảo **tối thiểu 70-80% thỏa mãn intent người dùng**, phần thông điệp khách lồng vào [[Source Context]]/Supplement. Nguyên tắc này ghi thẳng vào checklist ngành của dự án để Writer không tự xử.

### FD-08 — Cam kết cung cấp của khách: thông tin, hình ảnh, video `[GIỮ — legacy #4]`
Chốt sớm khách cung cấp được gì: (1) thông tin — gửi checklist thông tin cần cho từng loại bài, kèm định nghĩa khái niệm khó để khách trả lời đúng; (2) hình ảnh — hướng dẫn khách chụp đa góc, đủ sáng, có bối cảnh thật (feed vào Module D); (3) video — nếu thị trường cần (FD-32), note kịch bản để khách quay. Ghi rõ mục nào khách KHÔNG cung cấp được → chuyển phương án thay thế ở Module D.

---

## Module B — Điểm then chốt theo lĩnh vực (FD-09 → FD-16)

Nguồn: "Checklist lưu ý điểm then chốt cho các lĩnh vực dự án.xlsx" (2021 + sheet Update T9.2021, ~33 ngành). Legacy là kho tra cứu per-niche; bản này rút thành **khung 8 câu hỏi dựng "lưu ý ngành"** cho bất kỳ dự án mới nào — tra legacy làm ví dụ, không copy nguyên (nhiều lưu ý 2021 đã lỗi thời).

### FD-09 — Xác định profile ngành + dạng dự án `[SỬA — cột "Lĩnh vực/Dạng dự án" legacy]`
Chốt: ngành cụ thể (không dừng ở "Ecommerce" — phải tới mức "thiết bị vệ sinh", "kính áp tròng"), dạng dự án (Ecommerce / Dịch vụ / Hybrid / Publisher), và page types chính sẽ có content (Category, Product, Service, Blog, Landing). Mỗi page type sau này có chuẩn văn phong + độ dài + media riêng (FD-18, FD-28).

### FD-10 — YMYL flag + yêu cầu E-E-A-T tương ứng 🔴 `[SỬA — legacy "Sức khỏe/Luật/Bảo hiểm" → khung hóa]`
Ngành có chạm YMYL không (sức khỏe, tài chính, pháp lý, bảo hiểm, giáo dục-định cư)? Nếu có: (1) văn phong dạng chỉ định-khuyến cáo của người có chuyên môn, không phán tuyệt đối; (2) author entity thật + credentials hiển thị (byline, bio); (3) mọi claim có trích dẫn nguồn; (4) disclaimer chuẩn ngành. Đánh giá theo thang E-E-A-T 0-3 và Who-How-Why của skill `google-content-standard` ngay ở planning. YMYL = YES → bật tier-2 T2-O1 + T2-W1 (FD-25).

### FD-11 — Thuật ngữ ngành: bắt buộc, cấm, song ngữ `[SỬA — legacy scattered → gom thành 1 item]`
Lập 3 danh sách: (1) thuật ngữ bắt buộc dùng đúng (tên kỹ thuật, tên pháp lý, cách gọi chuẩn ngành); (2) từ cấm/từ thay thế (từ ngành kiêng, từ vi phạm quy định quảng cáo); (3) danh sách "thuật ngữ EN thông dụng không cần dịch" — phần còn lại áp quy tắc song ngữ VN (EN) theo tier-2 T2-W7. PM chốt danh sách này tại kick-off.

### FD-12 — Cấm kỵ pháp lý + quy định quảng cáo ngành `[MỚI — legacy chỉ chạm nhẹ ở Cầm đồ/Luật]`
Ngành có luật quảng cáo riêng không (TPCN "không phải là thuốc", tài chính-bảo hiểm, rượu bia, y tế, giáo dục du học)? Liệt kê: câu chữ bắt buộc, claim bị cấm, giấy phép cần dẫn, vùng xám cần hỏi khách (FD-03). Content liên quan pháp luật phải dẫn nguồn văn bản luật + số hiệu (legacy Cầm đồ: anchor về nguồn luật để tăng trust).

### FD-13 — Chuẩn trích nguồn/nghiên cứu của dự án `[SỬA — legacy "có nguồn trích dẫn" → chuẩn hóa theo W3/P17]`
Chốt cho Writer: (1) citation đặt SAU claim, trong ngữ cảnh — không gom hết xuống cuối bài; (2) loại nguồn chấp nhận theo ngành ([[VIP Sources]]: văn bản luật, tạp chí y khoa, số liệu hiệp hội, tài liệu nhà sản xuất) và nguồn KHÔNG chấp nhận (blog đối thủ, nguồn không rõ gốc); (3) YMYL → mức chi tiết trích dẫn cao hơn (tên nghiên cứu, năm, cỡ mẫu); (4) research thị trường (khảo sát, thống kê) → để nguồn tham khảo cuối bài theo format thống nhất.

### FD-14 — Quy tắc con số `[SỬA — gom legacy "fact, thông số, đo lường được" + tier-2 T2-W3]`
Chuẩn viết số cho toàn dự án: (1) số liệu phải đo lường được + có nguồn/năm (giá, thông số, %, thời gian xử lý); (2) dấu thập phân dùng dấu chấm (3.7); (3) dự án international/khoa học → dual measurement "70 lbs (31.75 kg)", đơn vị của target audience đứng trước (bật T2-W3); (4) số thuộc nhóm biến động (giá, lãi suất, quota) → ghi kèm thời điểm + nhịp cập nhật; (5) không làm tròn quá tay làm sai lệch claim (mỗi con số là 1 bộ [[E-A-V Framework]] — Entity-Attribute-Value phải chính xác).

### FD-15 — Fact ngành + độ sâu chuyên môn per page type `[GIỮ — pattern chung mạnh nhất của legacy 33 ngành]`
Pattern legacy lặp ở mọi ngành, vẫn đúng: **content thắng bằng yếu tố fact + văn phong expert, không hoa mỹ**. Chốt per page type: Product/Service cần trường thông tin nào (thông số kỹ thuật, chất liệu, kích thước, bảo hành, quy trình dịch vụ, bảng giá design chuẩn); Blog cần độ sâu nào (định nghĩa, cơ chế, so sánh, evidence). Kiến thức chuyên môn ngành = yếu tố thành công (legacy Ngoại ngữ: "yếu tố thành công nằm ở kiến thức về IELTS") → xác định team lấy chuyên môn từ đâu: khách training (FD-01), tài liệu ngành, chuyên gia review.

### FD-16 — Ví dụ tra cứu từ legacy (4 ngành minh họa khung FD-09→15)
Tra file legacy khi dự án rơi vào ngành đã làm; 4 ví dụ cho thấy khung trên map thế nào:

| Ngành (legacy) | Lưu ý then chốt đã đúc kết (2021, đọc có phê phán) |
|---|---|
| **Luật — thành lập DN** | Thông tin luật chính xác + nguồn trích dẫn rõ; dịch vụ nêu điểm nổi bật riêng + giá + thời gian + quy trình; entity chuyên viên xử lý từng mảng pháp lý; linh hoạt text/bảng/infographic; văn phong ngắn gọn, lập luận chặt |
| **Sức khỏe — TPCN, chăm sóc da (YMYL)** | Viết dạng chỉ định-khuyến cáo của bác sĩ/chuyên viên; E-A-T (nay E-E-A-T); TPCN bắt buộc rõ "không phải là thuốc"; fact + trích dẫn per topic; author thể hiện chuyên gia; pillar-cluster trọn chủ đề |
| **Nội thất — thiết kế thi công (Dịch vụ)** | Hình ảnh là vua: 15-50 hình/bài, đa phòng, đa phong cách, logo + kích thước đồng nhất; từ ngữ miêu tả khớp từng phong cách; dịch vụ ngắn gọn + quy trình + FAQ; bảng giá càng chi tiết càng tốt |
| **Du lịch — tour (Dịch vụ)** | Văn phong bay bổng nhưng phải có yếu tố thực tế; unique từ nội dung trải nghiệm (group FB, travel blogger); sản phẩm tour ngắn gọn + bảng giá; hình theo nội dung, trích nguồn ảnh |

> Lưu ý khi tra legacy: các con số word count (500-800, 1500-3000 chữ), lời khuyên "research hình ở shutterstock/pinterest" và mẹo giao diện 2021 KHÔNG mang sang nguyên trạng — độ dài nay theo word ladder AM v2.0 + SERP thực tế, hình ảnh theo Module D.

---

## Module C — Dựng checklist riêng từng dự án (FD-17 → FD-27)

Nguồn: "Checklist riêng cho từng dự án [Lưu hành nội bộ].xlsx" (2022) — legacy đã là form fill-in-the-blank; bản này giữ các hạng mục còn giá trị, bỏ phần lỗi thời, và bổ sung **quy trình vận hành**: dựng → lưu → bật tier-2 → vá.

### Quy trình dựng (4 bước)

1. **Input:** Module A (những gì đã chốt với khách) + Module B (khung ngành) + brand guideline khách gửi (nếu có) + hợp đồng (điều khoản content, từ `acc-kickoff-setup`).
2. **Output:** checklist ngành per dự án — điền vào mục 3 + 4 của `00-client-context/marketing-foundation.md` (SEO Production instance), theo các hạng mục FD-17→24 dưới đây. Điền xong, sạch placeholder → đổi `status: stable`.
3. **Kick-off nội bộ:** PM/Lead dùng checklist vừa dựng để bật tier-2 items (map FD-25) + phổ biến cho Writer/SEO EX trước bài đầu tiên.
4. **Vá định kỳ:** theo FD-26, FD-27.

### FD-17 — Thông tin chung dự án `[GIỮ — legacy mục 1]`
Website + tên thương hiệu (quy ước viết hoa/tên đầy đủ), phân khúc khách hàng hướng đến, mô hình kinh doanh, sản phẩm/dịch vụ chủ lực, bảng giá (dẫn link). Đồng bộ với Buyer Persona + Customer Journey đã điền ở mục 1-2 marketing-foundation.md — không duplicate, chỉ reference.

### FD-18 — Văn phong per content type + danh xưng 🔴 `[GIỮ — legacy mục 2]`
Định nghĩa văn phong CHUYÊN NGHIỆP-AM HIỂU cụ thể cho từng loại: content dịch vụ / blog / sản phẩm / danh mục (mỗi loại 2-3 câu mô tả + 1 đoạn mẫu đạt chuẩn). Danh xưng: "chúng tôi" hoặc tên thương hiệu; gọi người đọc "bạn/anh chị" tùy ngành; hạn chế lặp danh xưng. Các thực thể bắt buộc nhắc trong bài theo ngành (legacy ví dụ điện máy: thương hiệu, xuất xứ, công suất). Dự án Service/Commercial → bật T2-W4 Brand Voice.

### FD-19 — Meta description & title convention `[SỬA — legacy mục 3, hiện đại hóa]`
Chuẩn meta per dự án: có main point (con số/lợi ích cụ thể) khiến người đọc muốn bấm; tham khảo SERP thực của keyword để khớp kỳ vọng; bỏ từ thừa. Bỏ quy tắc legacy "thêm dấu tick ✓" — chỉ dùng nếu SERP ngành đang cho thấy pattern đó hoạt động; ký tự trang trí không còn là chuẩn mặc định.

### FD-20 — Keyword & element integration `[SỬA — legacy mục 4, lọc qua semantic writing]`
Giữ từ legacy: chèn keyword phải TỰ NHIÊN cho người đọc — được phép chêm từ vào giữa cụm ("ghế xoay văn phòng **với** giá rẻ **tại** TPHCM"); keyword phụ không cần chèn nguyên văn, chỉ cần elements đúng intent, elements và head keyword nằm gần nhau trong đoạn. Hiện đại hóa: keyword chính xuất hiện trong 100 từ đầu theo W1/P10; KHÔNG còn quy tắc "càng về bên trái càng tốt" kiểu 2021 — ưu tiên câu định nghĩa E-A-V chuẩn (Answer-First) hơn vị trí keyword cơ học.

### FD-21 — Số lượng chữ theo content type `[GIỮ — legacy mục 6, đã đúng tinh thần hiện đại]`
Legacy đã viết đúng: "số lượng chữ có thể điều chỉnh, chú trọng viết đủ nội dung". Chốt range tham khảo per content type dựa trên SERP thực tế + word ladder AM v2.0 (H3 ~120-150, H2 ~200, YMYL +20-30%), không dựa con số cứng của ngành từ 2021.

### FD-22 — Dữ liệu fact của dự án `[GIỮ — legacy mục 7]`
Hai nguồn fact được phép: (1) từ thương hiệu/khách cung cấp (số khách đã phục vụ, năm kinh nghiệm, chứng nhận — phải có trong FD-02); (2) từ research thị trường (theo chuẩn trích nguồn FD-13). Ghi rõ fact nào được dùng ở loại bài nào.

### FD-23 — Điều hướng SP/DV: USP · POPs · Benefits · NAP `[GIỮ — legacy mục 8]`
Chuẩn block điều hướng trong bài: (1) điều hướng tự nhiên giữa/cuối bài, không aggressive trong Main Content (khớp nguyên tắc Hybrid Intent O1); (2) danh sách SP/DV chủ lực cần điều hướng về (theo thứ tự ưu tiên); (3) ưu điểm SP/DV được phép nêu = đúng danh sách USP/POPs/Benefits đã chốt FD-02; (4) NAP (Name - Address - Phone, thêm Email/Website) format thống nhất toàn site — bắt buộc cho dự án local; (5) CTA chuẩn per page type + funnel stage (khớp T2-O7).

### FD-24 — Bố cục & trình bày bài `[SỬA — legacy mục 9, bỏ phần lỗi thời]`
Giữ: câu ≤20 từ là chính, đoạn 2-4 câu, bullet cho liệt kê ≥3 items song song, heading in đậm phân cấp rõ, kết thúc câu có dấu chấm. **Bỏ hẳn:** quy định font Times New Roman size 12/heading màu xanh (thời Google Docs 2021 — nay format theo CMS + design system của site). Chuẩn trình bày chi tiết đã nằm ở tier-1 W12/P18; checklist dự án chỉ ghi các NGOẠI LỆ riêng của khách.

### FD-25 — Bật tier-2 items từ foundation `[MỚI]`
Tại kick-off nội bộ, PM/Lead dùng kết quả foundation để bật tier-2, ghi vào Tracking Sheet:

| Kết quả foundation | Tier-2 items bật |
|---|---|
| FD-10 YMYL = YES | T2-O1 (YMYL Evidence in AM) + T2-W1 (YMYL Evidence Depth) |
| FD-09 dạng E-commerce | T2-O4 (Visual Semantic) + T2-O5 (E-com Format) + T2-W3 nếu có thông số |
| FD-18 có brand voice riêng / Service-Commercial | T2-W4 (Brand Voice Specific) |
| FD-14 có dual measurement / international | T2-W3 (Dual Measurement) + T2-O8 (Multi-market) |
| FD-11 có danh sách thuật ngữ song ngữ | T2-W7 (Bilingual Terminology) |
| Dự án >10 bài trong SCN | T2-O6 + T2-W5 (SCN Consistency) |
| Khách yêu cầu content team đặt IL | T2-O3 + T2-W6 (Internal Link) |

(T2-O2, T2-W2 đang BLOCKED theo LINT-2026-001 — không bật cho đến khi nguồn được khôi phục.)

### FD-26 — Nhịp vá checklist khi có feedback khách `[MỚI]`
Checklist ngành là tài liệu sống: (1) feedback khách về content đi qua flow Account (`acc-weekly-sync` bắt trong nhịp tuần; sự cố lớn escalate theo red-flags mục 06 tài liệu training Account); (2) feedback nào lộ ra LỖ HỔNG của checklist ngành (khách sửa cùng 1 kiểu lỗi ≥2 lần) → cập nhật `marketing-foundation.md` ngay trong tuần, không chờ cuối tháng; (3) mỗi lần vá ghi 1 dòng vào `12-feedback-lessons/` của instance (khớp MR-18 monthly-project-review); (4) Writer/SEO EX được thông báo diff mỗi lần checklist đổi.

### FD-27 — Phân tích topic cluster đối thủ tại kick-off `[GIỮ — legacy mục 10.2]`
Khi kick-off, phân tích cả những topic cluster đối thủ đang triển khai để hoạch định chiến lược content (feed vào topical map #10 + `competitor-seo-gap-analysis`). Legacy mục 10.1 (đồng nhất format bài cùng dạng) chuyển thành ghi chú trong FD-18/FD-24.

---

## Module D — Đa dạng hóa hình ảnh / video / infographic (FD-28 → FD-34)

Nguồn: "Checklist đa dạng hóa hình ảnh, video, infographic cho dự án hợp đồng 40tr_tháng.xlsx" (2020). Legacy phân theo Ecommerce vs Service và gate theo giá trị hợp đồng; bản này giữ logic **ưu tiên media theo loại bài**, thay "40tr/tháng" bằng nguyên tắc phân bổ theo scope hợp đồng, và thay "research hình web khác" bằng route generate on-brand.

### FD-28 — Media mix per loại bài 🔴 `[SỬA — legacy "Hình ảnh Chung/URL SEO/Content Strategy"]`
Chốt ma trận đầu tư media theo tier bài viết:

| Loại bài | Chuẩn tối thiểu | Ưu tiên đầu tư |
|---|---|---|
| **Bài thương mại** (Product/Service/Category — URL SEO, keyword cam kết) | 100% ảnh unique (thật hoặc design), đúng thứ tự ưu tiên: Sản phẩm/Dịch vụ → Blog money → Sub-category → Category | Cao nhất — đây là legacy "Hình ảnh URL SEO" |
| **Blog traffic** (Content Strategy) | ≥1 ảnh unique/bài (feature image); ảnh trong bài theo nhu cầu minh họa thật | Trung bình; nâng lên 100% unique với ngành visual-heavy (nội thất, thời trang) |
| **Bài hướng dẫn/quy trình** | Cân nhắc infographic hoặc step-images | Theo intent (FD-31, FD-32) |

Số lượng + chất lượng ảnh benchmark theo đối thủ trực tiếp trên SERP (legacy: hơn đối thủ 2-5 hình — nay hiểu là "không thua về media coverage", không phải đếm cơ học).

### FD-29 — Nguồn ảnh: thật vs stock vs generate `[SỬA — hiện đại hóa toàn bộ]`
Thứ tự ưu tiên: (1) **Ảnh thật từ khách** (FD-08) — bắt buộc cho: sản phẩm thực tế, đội ngũ/chuyên viên đang làm việc (legacy Điện lạnh: kỹ thuật viên đang sửa), dự án đã thi công, evidence E-E-A-T (YMYL/review cần original media — T2-W1); (2) **Generate on-brand** qua skill `brand-image-gen-gtv-tag` — cho illustration, concept, feature image blog; (3) **Stock** — phương án cuối, chỉ khi 2 nguồn trên không khả thi và phải xử lý lại (crop/blend/text overlay), không dùng nguyên ảnh stock phổ biến. Route sản xuất: **media-brief trước khi có ảnh** (brief media nằm trong AM theo O13 + L4 7.5 sop/08) → sản xuất → tối ưu filename/alt/caption bằng skill `image-seo-optimize` (P19-P20). **Bỏ hẳn** lời khuyên legacy "tìm hình unique từ web design/instagram rồi chèn logo" — rủi ro bản quyền, không còn chấp nhận.

### FD-30 — Chuẩn kỹ thuật ảnh của dự án `[GIỮ — legacy "Chuẩn chấp nhận" + legacy mục 5 file 3]`
Ghi thành chuẩn per dự án: ảnh khớp nội dung đoạn + khớp kết quả Google Images của keyword; không vỡ nét; đồng nhất background/blend màu cho ảnh sản phẩm; chèn logo thương hiệu (nhận diện + unique); caption mô tả đúng ảnh theo intent đoạn — không nhồi keyword; kích thước chuẩn theo template site; link Drive ảnh khách cung cấp ghi vào Source context.

### FD-31 — Infographic `[GIỮ — legacy]`
Dùng cho bài hướng dẫn các bước, cách làm, tác dụng, so sánh — cả URL SEO lẫn Content Strategy. Design theo template thống nhất của dự án. Outsource → khống chế đơn giá theo budget dự án (legacy benchmark 2020: <500k/infographic — cập nhật theo rate hiện hành khi dựng checklist).

### FD-32 — Video: khi nào cần `[GIỮ — legacy Video Sản phẩm/Blog]`
Chỉ triển khai khi SERP/intent cho thấy cần (Video Pack, bài how-to, ngành review sản phẩm — khớp O1 SERP Features). Thứ tự nguồn: (1) khách tự quay/edit (FD-08); (2) research video thị trường VN; (3) research video nước ngoài (kèm transcript/phụ đề Việt). Điều kiện bắt buộc: không dính logo/watermark đối thủ, liên quan trực tiếp nội dung. Bài thương mại ngành điện tử/thiết bị → video đánh giá/hướng dẫn sử dụng là chuẩn thị trường.

### FD-33 — Phân bổ media theo scope hợp đồng `[SỬA — legacy gate "40tr/tháng"]`
Legacy gate cứng "hợp đồng ≥40tr/tháng mới chạy full checklist này" chuyển thành nguyên tắc: mức đầu tư media (tỷ lệ ảnh design, số infographic/tháng, có video hay không) chốt ngay khi dựng checklist dự án, căn theo ngân sách + kỳ vọng trong hợp đồng (acc-kickoff-setup đã trích scope). Outsource design → cân nhắc ngân sách giới hạn của dự án mà phân bổ (giữ nguyên note legacy). Ghi quyết định vào marketing-foundation.md để không phát sinh tranh cãi giữa chừng.

### FD-34 — Media evidence cho YMYL/Review `[MỚI — nối Module B với D]`
Dự án YMYL hoặc có bài review: ảnh/video phải là **original evidence** (tác giả tự chụp/quay, thể hiện first-hand experience) — stock/generate không được tính là evidence. Khớp T2-W1 và Who-How-Why (`google-content-standard`). Nếu khách không cung cấp được → ghi rõ limitation trong checklist ngành và hạ kỳ vọng loại bài review tương ứng.

---

## Nguồn gốc & maintenance

- Gộp từ 4 checklist legacy 2020-2022 (frontmatter `source_files`) — đọc đầy đủ 4/4 file ngày 2026-07-19. Tag mỗi item: `[GIỮ]` giữ nguyên tinh thần legacy / `[SỬA]` hiện đại hóa / `[MỚI]` bổ sung theo quy trình 2026.
- File legacy vẫn nằm trong `raw/` làm kho tra cứu per-niche (Module B FD-16) — không sửa file raw.
- Checklist này là template nền; bản điền của từng dự án sống trong `00-client-context/marketing-foundation.md` của instance và được vá theo FD-26.
