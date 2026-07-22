---
type: sop
tier: gate
phase: legal-compliance
last_updated: 2026-07-19
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/Checklist giúp website bạn _tránh_ bị pháp luật phạt - The AI Growth.docx
related_wiki:
  - "[[sources/gtv-security-legal-legacy]]"
skills_routed:
  - humanizer
  - semantic-content-writing
items_count: 16 (P0 gate: 7)
tags: [sop, self-checklist, phap-ly, legal, content, website, vietnam, quality-gate]
---

# Self-Checklist: Pháp lý Content & Website (thị trường Việt Nam)

> **Khi dùng:** (1) **T1 audit** — rà toàn site khách mới ngay sau kick-off (đặc biệt ecommerce/YMYL); (2) **per batch content** — Writer/SEO EX tự check trước khi publish bài có claim chất lượng, bài ngành có điều kiện; (3) **khi Luật thay đổi** — re-run toàn site (mốc gần nhất: Luật Quảng cáo 2025 + Luật Bảo vệ Dữ liệu Cá nhân cùng hiệu lực 01/01/2026).
> **Gate:** Fail bất kỳ item **P0 (7 items)** → KHÔNG publish content / KHÔNG nghiệm thu website với khách cho đến khi xử lý xong.
> **Số items:** 16 (PL-01 → PL-16) = 5 Từ ngữ & claim + 4 Thông tin bắt buộc + 2 Dữ liệu cá nhân + 2 Bản quyền & điều khoản + 2 Hàng hóa + 1 Vận hành.
> **Scoring:** Self Score /16 → Self %. Cơ chế 3-Level Review theo README (Self 100% → SEO EX Verify → Lead random 25-30%).
> **⚠ Disclaimer bắt buộc đọc:** Nguồn gốc là tài liệu research nội bộ TAG/GTV (update 11/2025), **không phải tư vấn của luật sư**. Phạm vi: pháp luật Việt Nam. Mức phạt trích theo bản 11/2025 — fact-check trước khi trích cho khách; ngành rủi ro cao (dược, tài chính) phải escalate luật sư của khách (PL-16).

## Ranh giới với checklist khác

- Từ ngữ khẳng định cao chạm cả **nuke-list** của skill `humanizer` và Language Discipline của `semantic-content-writing` — nhưng ở đây là **luật, không phải style**: vi phạm = phạt tiền, không phải trừ điểm chất lượng.
- Trang chính sách bắt buộc (PL-09) overlap bộ trang entity EN-03 của `tier-1-entity.md` — EN-03 nhìn từ góc trust/entity, PL-09 nhìn từ góc nghĩa vụ pháp lý. Tick riêng từng bên.
- Thẩm định ngành/pháp lý TRƯỚC khi nhận dự án → [[sop/06-self-checklist/checklist-project-intake-tham-dinh]] (PI-02). Checklist này chạy SAU khi đã nhận.

---

## Nhóm 1 — Từ ngữ & claim quảng cáo

### PL-01 🔴 P0 — Không dùng từ ngữ khẳng định tuyệt đối khi không có chứng minh hợp lệ
Theo Luật Quảng cáo 2012 (sửa đổi 2025): CẤM "chất lượng nhất", "tốt nhất", "số một/số 1", "duy nhất", "hàng đầu" và mọi từ nghĩa tương tự — TRỪ KHI có tài liệu chứng minh hợp lệ: kết quả khảo sát thị trường bởi tổ chức khảo sát hoạt động hợp pháp, hoặc chứng chỉ/văn bằng từ cuộc thi/triển lãm cấp khu vực hoặc quốc gia. Tài liệu chứng minh chỉ có hiệu lực **1 năm** kể từ ngày phát hành — quá hạn = claim trở lại thành vi phạm.
- ✅ Grep toàn bộ content (title, meta, H1, body, alt, schema) theo danh sách từ cấm; mỗi claim tuyệt đối còn giữ đều có file chứng minh + ngày hết hạn ghi trong tracking.
- ❌ "Dịch vụ SEO tốt nhất Việt Nam" trên trang chủ, không kèm khảo sát nào → fail, gỡ trước khi làm gì khác.
- Mức phạt legacy 11/2025: 60-80 triệu đồng (dự thảo tăng 80-100 triệu).
- Nguồn: docx pháp lý mục 1 + Action summary 11/2025 — **GIỮ**.

### PL-02 — Claim chất lượng viết theo phương án an toàn
Khi muốn nói sản phẩm/dịch vụ tốt, dùng thang an toàn của tài liệu legacy (mục 6):
| Cách viết | Điều kiện | An toàn? |
|---|---|---|
| "Chất lượng nhất / tốt nhất" | Cần tài liệu chứng minh hợp lệ (PL-01) | ❌ Rủi ro cao |
| "Chất lượng cao / tốt" (không so sánh tuyệt đối) | Đúng thực tế, chứng minh được bằng đánh giá khách hàng, hình ảnh thực | ✅ |
| "Được [tổ chức X] công nhận" | Có chứng chỉ/giấy chứng nhận từ đúng tổ chức đó | ✅ |
| Liệt kê tính năng cụ thể | Chính xác, khớp sản phẩm thực | ✅ |
| Hiển thị đánh giá khách hàng | Chỉ dùng đánh giá thực, đã xác minh — không fake review | ✅ |
- Nguồn: docx pháp lý mục 6 (bảng lựa chọn an toàn) — **GIỮ**. Đây cũng là hướng rewrite mặc định khi PL-01 bắt được vi phạm.

### PL-03 🔴 P0 — Không có nội dung quảng cáo bị cấm
Rà 6 dạng bị cấm (mục 4 legacy): (1) thông tin sai sự thật về chất lượng/nguồn gốc sản phẩm; (2) so sánh trực tiếp với sản phẩm đối thủ (trừ khi có tài liệu chứng minh hợp pháp); (3) khẳng định không bằng chứng; (4) hình ảnh gây nhầm lẫn hoặc dùng logo/thương hiệu đối thủ; (5) quảng cáo sản phẩm thuộc nhóm phải có chứng chỉ mà không có; (6) gây nhầm lẫn về khả năng kinh doanh (vd claim chứng chỉ quốc tế không có thật).
- ❌ Bảng "So sánh [brand khách] vs [đối thủ]" nêu đích danh + chê đối thủ, không tài liệu chứng minh → fail. (Lưu ý: consensus/comparison content vẫn làm được — so sánh THUỘC TÍNH chung chung của loại sản phẩm, không đích danh chê đối thủ.)
- Mức phạt legacy: 60-80 triệu trở lên tùy tính chất.
- Nguồn: docx pháp lý mục 4 — **GIỮ**.

### PL-04 🔴 P0 — Disclaimer & điều kiện quảng cáo bắt buộc theo ngành (YMYL)
Ngành có điều kiện phải có disclaimer/thủ tục riêng, thiếu = vi phạm trực tiếp:
- **TPCN / thực phẩm bảo vệ sức khỏe:** bắt buộc khuyến cáo "Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh" hiển thị rõ; sản phẩm phải có công bố chất lượng (khớp PL-14); không mô tả công dụng như thuốc chữa bệnh.
- **Dược:** nội dung quảng cáo thuốc phải được cơ quan y tế xác nhận trước khi đăng; thuốc kê đơn KHÔNG được quảng cáo tới công chúng — content chỉ được ở mức thông tin tra cứu, không kêu gọi mua.
- **Tài chính / đầu tư:** nêu rõ giấy phép hoạt động; có cảnh báo rủi ro; không cam kết/hứa hẹn lợi nhuận chắc chắn.
- **Y tế / khám chữa bệnh:** không claim "chữa khỏi", "cam kết khỏi bệnh"; khuyến nghị tham khảo ý kiến bác sĩ.
- ✅ Mỗi dự án YMYL có danh sách disclaimer bắt buộc của ngành trong `foundation-content-nganh.md` của dự án; template bài viết chèn sẵn.
- Nguồn: **MỚI** — suy ra từ docx mục 4/8 (sản phẩm cần chứng chỉ) + kiến thức ngành YMUL của wiki; docx legacy chưa liệt kê disclaimer per ngành → đây là phần bổ sung, cần fact-check theo PL-16.

### PL-05 — Nhận diện quảng cáo & trách nhiệm liên đới (Luật Quảng cáo 2025)
Từ 01/01/2026: quảng cáo trực tuyến phải có **dấu hiệu nhận diện rõ ràng**, không được che giấu mục đích thương mại (bài PR/advertorial/affiliate phải label); KOL/influencer phải xác minh độ tin cậy nhà quảng cáo, kiểm tra tài liệu chứng minh và **chịu trách nhiệm liên đới** nếu quảng cáo sai sự thật; nền tảng phải gỡ quảng cáo vi phạm trong 24h khi cơ quan nhà nước yêu cầu. Mức phạt tối đa mới: 100 triệu (cá nhân) / 200 triệu (tổ chức).
- ✅ Bài PR/textlink/booking KOL trong plan offpage có label quảng cáo theo chuẩn kênh đăng; brief gửi KOL kèm tài liệu chứng minh claim.
- Áp dụng chéo: chiến dịch của skill `textlink-analyzer` / `backlink-plan` khi dùng báo PR.
- Nguồn: docx pháp lý mục 5 — **GIỮ**.

---

## Nhóm 2 — Thông tin doanh nghiệp & thủ tục bắt buộc trên website

### PL-06 🔴 P0 — Thông tin chủ sở hữu website công bố đầy đủ
Theo Nghị định 52/2013/NĐ-CP, website bán hàng phải công bố (thường ở footer + trang liên hệ/giới thiệu): tên thương nhân/tổ chức/cá nhân; **địa chỉ chi tiết** (số nhà, đường, phường/xã — không chỉ tên tỉnh); số điện thoại; email liên hệ; số đăng ký kinh doanh hoặc mã số thuế; giấy phép/chứng chỉ nếu là ngành kinh doanh có điều kiện.
- ✅ Đối chiếu đúng Brand Info Pack (EN-01 của `tier-1-entity.md`) — thông tin pháp lý và thông tin entity phải là MỘT bộ số liệu.
- ❌ Footer chỉ ghi "Công ty ABC — TP.HCM" → fail.
- Mức phạt legacy: 1-10 triệu tùy mức độ (thiếu/không đầy đủ).
- Nguồn: docx pháp lý mục 2A + Action summary — **GIỮ**.

### PL-07 🔴 P0 — Thông báo website với Bộ Công Thương (online.gov.vn)
Bắt buộc khi website có chức năng đặt hàng trực tuyến (giỏ hàng, thanh toán online…) hoặc thương mại điện tử là hoạt động chính. Thông báo miễn phí tại www.online.gov.vn, cần mã số thuế, thực hiện **trước khi bắt đầu bán hàng**; sau khi duyệt gắn logo đã thông báo BCT ở footer.
- ❌ Site ecommerce chạy 2 năm chưa thông báo → fail; đưa vào action list T1 gửi khách ngay (việc của khách, GTV không tự làm thay nhưng phải phát hiện và nhắc).
- Mức phạt legacy: 10-20 triệu (cá nhân) / 20-40 triệu (doanh nghiệp) + có thể đình chỉ hoạt động 6-12 tháng.
- Nguồn: docx pháp lý mục 3 — **GIỮ**.

### PL-08 — Thông tin hàng hóa/dịch vụ đầy đủ và khớp thực tế
Trang sản phẩm/dịch vụ phải có: tên, số lượng, chủng loại; **giá bán rõ ràng bao gồm tất cả chi phí**; phương thức + thời hạn giao hàng; điều kiện bảo hành/đổi trả. Thông tin phải **khớp với nhãn hàng hóa** — content SEO "viết cho hay" mà lệch thông số nhãn = rủi ro sai sự thật (PL-03).
- Nguồn: docx pháp lý mục 2B — **GIỮ**.

### PL-09 — Bộ trang chính sách bắt buộc
Ecommerce: đủ 5 trang — hướng dẫn mua hàng, chính sách giao hàng, hình thức thanh toán, chính sách bảo hành/đổi trả, chính sách bảo mật thông tin. Website dịch vụ: tối thiểu trang bảo vệ thông tin (chính sách thu thập thông tin). Các trang này đồng thời là bộ trang trust của EN-03 (`tier-1-entity.md`) — build một lần phục vụ cả hai mục đích.
- ✅ Trang tồn tại, index được, nội dung thật (không copy template lệch với vận hành thực của khách), link từ footer.
- Nguồn: docx pháp lý mục 2C + Action summary 11/2025 — **GIỮ**.

---

## Nhóm 3 — Dữ liệu cá nhân

### PL-10 🔴 P0 — Chính sách bảo vệ dữ liệu cá nhân + consent trước khi thu thập
Khung hiện hành: Nghị định 13/2023/NĐ-CP (PDPD) và **Luật Bảo vệ Dữ liệu Cá nhân** (thông qua 25/06/2025, hiệu lực 01/01/2026). Website thu thập data (form lead, đăng ký, checkout, tracking) phải: có chính sách bảo vệ thông tin cá nhân đúng quy định; **hiển thị công khai ở vị trí dễ thấy**; có cơ chế để khách hàng **đồng ý rõ ràng TRƯỚC khi thu thập** (checkbox consent tại form, không pre-tick).
- ❌ Form "Nhận tư vấn miễn phí" lấy tên + SĐT, không link chính sách, không consent → fail. Đây là pattern phổ biến nhất trên landing SEO/CRO — check mọi form khi làm `tier-1-cro-conversion.md`.
- Nguồn: docx pháp lý mục 7 — **GIỮ**; đối chiếu thêm NĐ 13/2023 (docx không nêu số nghị định — bổ sung từ kiến thức wiki, fact-check theo PL-16).

### PL-11 — Quyền chủ thể dữ liệu & giới hạn sử dụng
Có cơ chế: kiểm tra/cập nhật/điều chỉnh/hủy thông tin cá nhân khi khách yêu cầu; kênh tiếp nhận khiếu nại về vi phạm thông tin cá nhân; đảm bảo an toàn dữ liệu. KHÔNG chia sẻ dữ liệu cho bên thứ ba khi chưa được phép; KHÔNG dùng data để gửi quảng cáo (email/SMS/remarketing list) khi chưa được đồng ý.
- Áp dụng chéo: chiến dịch email của skill `email-marketing-automation` trên list khách VN phải qua item này.
- Nguồn: docx pháp lý mục 7 — **GIỮ**.

---

## Nhóm 4 — Bản quyền & điều khoản sử dụng

### PL-12 — Bản quyền ảnh & nội dung
Hàng hóa/nội dung vi phạm quyền sở hữu trí tuệ (bản quyền, nhãn hiệu) là nhóm vi phạm được legacy xếp cùng hàng cấm (mục 8). Áp cho content SEO: (1) KHÔNG lấy ảnh từ Google Images/website khác khi không rõ license — dùng ảnh tự chụp/tự thiết kế, ảnh khách cung cấp, hoặc stock có license lưu hồ sơ; (2) trích dẫn số liệu/đoạn văn phải dẫn nguồn; (3) KHÔNG copy content đối thủ (vừa rủi ro SHTT vừa chết duplicate); (4) ảnh có mặt người (nhân viên, khách hàng, testimonial) phải có sự đồng ý sử dụng hình ảnh.
- ✅ Mỗi bài publish có nguồn ảnh ghi trong tracking content; logo/nhãn hiệu bên thứ ba chỉ xuất hiện đúng ngữ cảnh được phép.
- Nguồn: docx pháp lý mục 8 (SHTT) — **GIỮ + MỞ RỘNG** sang tác nghiệp content (phần mở rộng là chuẩn nội bộ GTV, không phải trích luật).

### PL-13 — Điều khoản sử dụng (Terms of Use)
Website có tài khoản người dùng, UGC (comment/review), công cụ online, hoặc chương trình khuyến mãi nên có trang Điều khoản sử dụng: phạm vi dịch vụ, trách nhiệm người dùng, quyền gỡ nội dung vi phạm, giới hạn trách nhiệm, luật áp dụng. Site YMYL bổ sung disclaimer nội dung chỉ mang tính tham khảo (khớp PL-04).
- Nguồn: **MỚI** — chuẩn nội bộ bổ sung từ kiến thức wiki (legacy không có mục riêng); mức "nên có", không gate.

---

## Nhóm 5 — Hàng hóa & ngành hàng

### PL-14 🔴 P0 — Không bán/giới thiệu hàng cấm, hàng giới hạn thiếu chứng chỉ
Website và social của khách không được bán/giới thiệu: hàng giả, hàng nhái, hàng lậu/nhập lậu; hàng vi phạm SHTT; **thuốc chữa bệnh, mỹ phẩm không có chứng chỉ**; **TPCN không có công bố chất lượng**; hàng bị cấm (thuốc lá không đúng chứng chỉ, rượu tại địa phương cấm…). Với agency: phát hiện ở T1 → báo khách gỡ; khách không gỡ → đây là red-flag hợp đồng (xem PI checklist RF-02).
- ✅ Rà toàn bộ danh mục sản phẩm được đưa vào topical map/content plan; sản phẩm nhóm điều kiện có số công bố/chứng chỉ đính kèm brief.
- Nguồn: docx pháp lý mục 8 + Action summary — **GIỮ**.

### PL-15 — Nguồn gốc hàng hóa công bố rõ
Với hàng hóa vật lý, công bố: nước sản xuất, nhà sản xuất, nhà nhập khẩu (nếu hàng nhập). Content sản phẩm không được mập mờ nguồn gốc ("hàng chuẩn Âu" không chứng từ).
- Nguồn: docx pháp lý mục 8 (hàng không rõ nguồn gốc) — **GIỮ**.

---

## Nhóm 6 — Vận hành gate

### PL-16 — Fact-check, escalation & re-run định kỳ
(1) Tài liệu nguồn tự khai KHÔNG phải tư vấn luật sư — mọi con số phạt/điều luật khi đưa vào deliverable gửi khách phải fact-check theo văn bản pháp luật hiện hành tại thời điểm gửi; (2) dự án ngành rủi ro cao (dược, tài chính, y tế) → khuyến nghị khách xác nhận với luật sư, GTV không tự kết luận pháp lý; (3) đặt lịch re-run checklist khi có luật mới hiệu lực (mốc đang treo: cả Luật Quảng cáo 2025 và Luật BVDLCN hiệu lực 01/01/2026 — đã qua, verify khách đã tuân thủ bản mới); (4) kết quả rà ghi vào log dự án, action item pháp lý tách mục riêng trong report gửi khách.
- Nguồn: docx pháp lý phần Lưu ý đầu file — **GIỮ** (nâng từ disclaimer thành quy trình vận hành).

---

## P0 Gate — 7 items chặn publish/nghiệm thu

| ID | Tóm tắt | Vì sao chặn |
|---|---|---|
| PL-01 | Không từ ngữ khẳng định tuyệt đối thiếu chứng minh | Phạt 60-100 triệu, lỗi phổ biến nhất |
| PL-03 | Không nội dung quảng cáo bị cấm | Phạt 60-80 triệu+, gồm so sánh đối thủ |
| PL-04 | Disclaimer bắt buộc theo ngành YMYL | Thiếu = vi phạm trực tiếp, rủi ro cao nhất ở TPCN/dược |
| PL-06 | Thông tin chủ sở hữu đầy đủ | Nghĩa vụ NĐ 52/2013, sửa rẻ — không có lý do fail |
| PL-07 | Thông báo Bộ Công Thương | Phạt tới 40 triệu + đình chỉ 6-12 tháng |
| PL-10 | Chính sách DLCN + consent | Luật mới hiệu lực 01/01/2026, mọi form lead đều chạm |
| PL-14 | Không hàng cấm/thiếu chứng chỉ | Rủi ro nặng nhất (có thể hình sự), ảnh hưởng cả agency |

## Quy trình dùng nhanh

1. **T1:** chạy full 16 items trên site khách → action list pháp lý (việc của khách vs việc của GTV) đưa vào báo cáo audit T1.
2. **Per batch content:** Writer tick PL-01, PL-02, PL-03, PL-04, PL-12 trước khi submit; SEO EX verify lại trong vòng review.
3. **Chiến dịch PR/KOL:** thêm PL-05 vào brief.
4. **Có luật mới / khách đổi ngành hàng:** re-run toàn bộ (PL-16).
