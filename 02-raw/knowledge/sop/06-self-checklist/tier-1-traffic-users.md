---
type: sop
tier: 1
phase: traffic-users
last_updated: 2026-07-19
source_files:
  - raw/_ingested/Quy trình SEO PSP - All In One/Kiến Thức triển khai Traffic User.pptx
items_count: 16
risk_class: high
approval_required: SEO Director
tags: [sop, tier-1, traffic-users, ctr, self-checklist, quality-gate, high-risk]
---

# Tier 1 — Self-Checklist: Traffic Users (T8 → hết T9)

> **Khi dùng:** Người vận hành traffic users tự check TRƯỚC khi bật chiến dịch, HẰNG TUẦN trong lúc chạy, và khi kết thúc.
> **Phạm vi:** Hạng mục triển khai traffic users theo lộ trình dự án — T8 đến hết T9. Traffic users là mắt xích CUỐI của lộ trình đẩy top key: `CONTENT → MẬT ĐỘ KEY → INTERNAL LINK → BACKLINK → USER/CTR` — chỉ chạy khi 4 mắt xích trước đã chuẩn.
> **Số items:** 16 (TU-01 – TU-16) = 5 Gate tiền triển khai + 5 Thiết lập + 4 Giám sát + 2 Kết thúc.
> **🔴 RỦI RO CAO:** Đây là hạng mục thao túng hành vi tìm kiếm — vi phạm Google spam policies nếu bị nhận diện. **CHỈ triển khai khi SEO Director duyệt bằng văn bản.** Gate tiền triển khai (TU-01 → TU-05) = **P0, phải pass 100%** trước khi bật bất kỳ user nào. Fail 1 item gate → KHÔNG chạy, không có ngoại lệ.
> **Scoring:** Self Score /16. Lead/Director review 100% (KHÔNG random như checklist content — hạng mục này review toàn bộ).

## Map item → ref

| ID | Label | Ref |
|---|---|---|
| TU-01 | Văn bản duyệt SEO Director | — |
| TU-02 | Phân biệt với Content Traffic | Content Production / Historical Data |
| TU-03 | Không mô tả "chuẩn trắng" với khách | acc red-flags (khách hỏi traffic users) |
| TU-04 | Stop-loss định nghĩa trước | — |
| TU-05 | Nguồn user đã thẩm định (chống user fake) | pptx slide Traffic1s |
| TU-06 | Query chỉ định khớp bộ từ khóa mục tiêu | pptx "Cách chạy key Suggest / key N/A" |
| TU-07 | Nền tảng 4 mắt xích trước đã chuẩn | pptx "Lộ trình đẩy top key" |
| TU-08 | Ramp-up dần không đột biến | pptx (10/day → 15/day sau ngày 11) |
| TU-09 | Phân bổ thiết bị / địa lý (VN) | Open Questions |
| TU-10 | CTR mục tiêu trong ngưỡng tự nhiên | pptx "Tính CTR để đẩy user" + Open Questions |
| TU-11 | Đo lường tách biệt (annotation) | tracking dự án |
| TU-12 | Theo dõi ranking + GSC anomaly | GSC / rank tracker |
| TU-13 | Checkpoint 10 ngày + chuyển chế độ key | pptx "Đẩy User" |
| TU-14 | Lịch review với Director | — |
| TU-15 | Tắt dần không cliff | — |
| TU-16 | Ghi nhận kết quả + bài học | 12-feedback-lessons |

---

## NHÓM 1 — GATE TIỀN TRIỂN KHAI 🔴 P0 (pass 100% trước khi bật)

### TU-01 — Văn bản duyệt của SEO Director có TRƯỚC khi chạy 🔴 P0

**Nhóm:** Gate

**Tóm tắt:** Có văn bản duyệt (email/doc có tên, ngày, phạm vi) của SEO Director cho ĐÚNG dự án này, ĐÚNG bộ keyword này, ĐÚNG khoảng thời gian này. Duyệt miệng, duyệt qua chat không truy vết được, hoặc "dự án trước được duyệt rồi" → không tính.

**Mô tả đầy đủ:**
1. Văn bản ghi tối thiểu: dự án, bộ keyword/URL target, ngân sách, thời gian chạy (trong T8-T9), nguồn user, stop-loss (TU-04).
2. Thay đổi phạm vi giữa chừng (thêm keyword, tăng volume vượt plan) → phải duyệt lại.
3. Link văn bản duyệt lưu vào tracking dự án — Account và Lead cùng thấy.

**Ví dụ Đạt / Không Đạt:**
✅ Doc "Traffic users [client X] T8-T9" có scope + chữ ký Director ngày 05/T8, link trong tracking.
❌ "Anh D. gật đầu trong meeting tuần trước" — không có văn bản.

**Nguồn:** Quy trình GTV — hạng mục rủi ro cao chỉ chạy khi SEO Director duyệt (chỉ đạo vận hành; pptx không đề cập approval — bổ sung theo quy trình hiện hành).

---

### TU-02 — Phân biệt rõ với Content Traffic 🔴 P0

**Nhóm:** Gate

**Tóm tắt:** KHÔNG nhầm lẫn 2 hạng mục: (1) **Content Traffic** = bài viết target keyword ngách/phantom kéo traffic TỰ NHIÊN → thuộc Content Production, đổ vào Historical Data — hạng mục trắng, không cần gate này; (2) **Traffic Users** = user/CTR được điều phối vào keyword chỉ định — hạng mục rủi ro cao, checklist này. Kế hoạch, tracking, ngân sách của 2 hạng mục tách riêng hoàn toàn.

**Mô tả đầy đủ:**
1. Rà kế hoạch T8-T9: mọi dòng "traffic" phải gắn nhãn rõ thuộc hạng mục nào.
2. Bài content traffic (phantom keywords, site tài liệu/download hướng dẫn trong pptx phần "tips kéo user" FREE) nếu làm trên site khách → đi theo pipeline content thường, KHÔNG đi theo checklist này.
3. Không dùng ngân sách/kênh của hạng mục này để "bơm" cho bài content traffic và ngược lại — số liệu lẫn nhau sẽ phá đo lường (TU-11).

**Ví dụ Đạt / Không Đạt:**
✅ Sheet kế hoạch T8: tab "Content Traffic (Historical Data)" 12 bài phantom + tab riêng "Traffic Users (Director-approved)" 8 keyword.
❌ Gộp chung 1 tab "kéo traffic", không phân biệt bài viết với user điều phối.

**Nguồn:** pptx "Tóm lại về chạy user" (mục 1 FREE — key phantom + forum = đường content/tự nhiên, tách khỏi user trả phí) · quy trình Content Production 10-update/Historical Data.

---

### TU-03 — KHÔNG mô tả với khách là "chuẩn trắng" — Account đã được brief 🔴 P0

**Nhóm:** Gate

**Tóm tắt:** Mọi giao tiếp với khách về hạng mục này (nếu có) phải trung thực về bản chất và rủi ro — **cấm mô tả là "kỹ thuật chuẩn trắng/white-hat"**. Account phụ trách dự án đã được brief: nói gì được, nói gì không, và red-flag "khách hỏi traffic users" xử lý thế nào (escalate về SEO Lead/Director, không tự trả lời).

**Mô tả đầy đủ:**
1. Check Account của dự án đã nhận brief (có ghi nhận — message/doc) trước ngày bật.
2. Report gửi khách: số liệu hạng mục này không được trình bày như organic growth thuần (liên quan TU-11 — đo tách).
3. Khách chủ động yêu cầu triển khai → yêu cầu đó cũng phải qua gate TU-01, và văn bản trao đổi lưu lại.

**Ví dụ Đạt / Không Đạt:**
✅ Account trả lời khách: "Hạng mục này thuộc nhóm kỹ thuật có rủi ro, bên em chỉ chạy khi anh/chị xác nhận đồng ý phạm vi + rủi ro" — sau đó escalate.
❌ Slide gửi khách ghi "dịch vụ tăng CTR an toàn tuyệt đối, chuẩn trắng theo Google".

**Nguồn:** Quy trình Account GTV (red-flags mục 06 — "hỏi traffic users") · chỉ đạo Vincent cho checklist này.

---

### TU-04 — Điều kiện dừng (stop-loss) định nghĩa TRƯỚC 🔴 P0

**Nhóm:** Gate

**Tóm tắt:** Trước khi bật phải có bảng stop-loss viết sẵn trong văn bản duyệt: trigger nào → DỪNG NGAY (không đợi review tuần). Tối thiểu 4 trigger: (1) ranking keyword target GIẢM ≥N vị trí so với baseline; (2) GSC anomaly/manual action/thông báo bất thường; (3) nguồn user phát hiện fake/bẩn (TU-05 fail giữa chừng); (4) khách/Director rút duyệt. Dừng = ngừng mua user mới + kích hoạt quy trình tắt dần TU-15.

**Mô tả đầy đủ:**
1. Baseline ranking + GSC (impressions/CTR/position per keyword) chụp TRƯỚC ngày bật — không có baseline thì không đo được trigger.
2. Ngưỡng N (vị trí giảm), % CTR bất thường, và người có quyền ra lệnh dừng ghi rõ tên.
3. Stop-loss nằm trong văn bản duyệt TU-01 — Director ký là ký cả stop-loss.

**Ví dụ Đạt / Không Đạt:**
✅ "Keyword nào giảm ≥5 vị trí giữ 7 ngày, hoặc GSC có manual action → dừng ngay, quyền lệnh: [Lead], báo Director trong 24h."
❌ "Chạy rồi thấy sao tính tiếp."

**Nguồn:** Khung quản trị rủi ro GTV (pptx không có stop-loss — bổ sung bắt buộc theo chỉ đạo; xem Open Questions).

---

### TU-05 — Nguồn user đã thẩm định — chống user FAKE 🔴 P0

**Nhóm:** Gate

**Tóm tắt:** Trước khi chọn nguồn user (thuê ngoài hoặc tự xây): tìm hiểu **user bên đó đến từ đâu, cách họ tạo user là gì**. Cảnh báo gốc từ tài liệu: "hiện nay khá nhiều user FAKE — có thể ban đầu user xịn nhưng sau họ làm lợi nhuận nên pha user fake". Tự xây hệ thống → control được chất lượng; thuê ngoài → rủi ro fake rất cao, phải verify trước và định kỳ.

**Mô tả đầy đủ:**
1. Nguồn thuê ngoài: yêu cầu giải trình cơ chế (vd mô hình site trung gian đổi mã — user thật làm nhiệm vụ search keyword rồi click, kéo từ social: tham chiếu case Traffic1s — Twitter ~67% / Facebook ~19% / YouTube ~14%); check chéo web nguồn trên Ahrefs.
2. So sánh phương án theo chi phí/user: FREE (tự làm key phantom + forum — tốn thời gian, quy ra phí) vs trả phí (tự chạy ads/tiktok/seo site trung gian) vs mua ngoài — quyết định theo ngân sách, ghi vào văn bản duyệt.
3. Tiêu chí nghi fake để loại: user không có hành vi thật (bounce 100%, time-on-site 0, không cuộn), device/IP pattern lặp, giờ truy cập dồn cục.
4. Nguồn phát hiện pha fake giữa chiến dịch → trigger stop-loss (TU-04).

**Ví dụ Đạt / Không Đạt:**
✅ Test nguồn 7 ngày với 1 keyword phụ + đo GA4 behavior trước khi ký tháng.
❌ Mua gói "10.000 traffic giá rẻ" không rõ nguồn, không test.

**Nguồn:** pptx slides "Ví dụ demo Traffic1s.com" (lời khuyên tìm hiểu nguồn user, cảnh báo user FAKE) + "Tóm lại về chạy user" (tự xây control chất lượng; thuê ngoài rủi ro fake cao; so sánh chi phí/user theo ngân sách).

---

## NHÓM 2 — THIẾT LẬP

### TU-06 — Query chỉ định khớp bộ từ khóa mục tiêu + đúng chế độ chạy

**Nhóm:** Thiết lập

**Tóm tắt:** Bộ query giao cho nguồn user phải khớp 1-1 với bộ keyword mục tiêu đã duyệt, và chọn đúng 1 trong 3 chế độ theo tài liệu gốc: (1) **Key cần SEO** — keyword đã có ranking cần đẩy top; (2) **Key Suggest** — kéo suggest: query = key cần SEO + key brand (vd "dịch vụ backlink seo thành công"); (3) **Key N/A** — cho key brand chưa được nhận diện hoặc Google nhận nhầm key.

**Mô tả đầy đủ:**
1. Mỗi keyword trong campaign ghi rõ chế độ + URL đích cần user click (user phải click ĐÚNG site mình trong SERP).
2. Key Suggest: bản chất là tạo lượt quan tâm tìm kiếm — trung bình cần >10 lượt tìm/ngày trong 1 tháng để suggest xuất hiện; CHỈ đúng khi ngách chưa ai làm suggest — ngách có 10-30 bên cùng làm → phải tính toán lại volume (không dùng con số mặc định).
3. Key N/A: trước khi chạy phải tối ưu bài (mật độ key ~2%, internal link ưu tiên từ khóa cần SEO, link out chủ đề liên quan) — user không cứu được bài chưa tối ưu.
4. Query ngoài danh sách duyệt → không giao cho nguồn (scope creep = chạy lại TU-01).

**Ví dụ Đạt / Không Đạt:**
✅ Sheet campaign: 8 key cần SEO (pos 6-15) + 2 key suggest ("[dịch vụ X] + [brand]") — mỗi dòng có chế độ, URL đích, volume/ngày.
❌ Giao nguồn "chạy các từ liên quan dịch vụ X" — không danh sách, không chế độ.

**Nguồn:** pptx slides "Cách chạy User", "Cách chạy key Suggest" (định nghĩa key suggest, >10 search/day, điều kiện ngách), "Cách chạy key N/A" (mật độ 2%, internal, link out) · case demo "Dịch vụ backlink Seothanhcong" (4 bên làm suggest, <10 người → chạy đều là lên; trên 10-30 bên → tính lại).

---

### TU-07 — Nền tảng 4 mắt xích trước đã chuẩn (user là mắt xích CUỐI)

**Nhóm:** Thiết lập

**Tóm tắt:** Theo lộ trình đẩy top key của tài liệu gốc: `CONTENT → MẬT ĐỘ KEY → INTERNAL LINK → BACKLINK → USER/CTR`. Trước khi bật user cho 1 keyword: content đã chỉnh theo phân tích đối thủ (mật độ key, internal link, external link), và **backlink đang đi ĐỀU — chia theo tuần** trong suốt thời gian đẩy user. User bơm vào trang chưa tối ưu = đốt tiền + tăng risk mà không có kết quả.

**Mô tả đầy đủ:**
1. Per keyword: check bài đã qua audit onpage (mật độ ~2% tham chiếu, internal link ưu tiên keyword cần SEO, link out chủ đề liên quan).
2. Phân tích đối thủ top: mật độ key, internal/external link, backlink (GP bao nhiêu, báo bao nhiêu, tỷ lệ do/no) → điều chỉnh trước.
3. Backlink kết hợp: trong quá trình đẩy user, backlink phải đẩy dần đều theo bảng đi link chi tiết; đối thủ không đi link mà vẫn top → dựa KD Ahrefs định lượng (tham chiếu gốc: KD <15 → ~5 bài guest post, mảng ngoài YMYL).
4. Key suggest: kết hợp internal link key suggest + đi link anchor text đặt key suggest; tốt nữa thì ~50 link social profile.

**Ví dụ Đạt / Không Đạt:**
✅ Keyword pos 7: bài đã re-optimize tuần trước, 4 link/tuần đang chạy đều → bật user.
❌ Bật user cho bài chưa có internal link, backlink = 0, "để user kéo lên".

**Nguồn:** pptx slides "Lộ trình đẩy top key" (5 mắt xích; "link đi đều - chia theo từng tuần") + "Cách chạy User" (phân tích đối thủ, KD<15 → 5 GP) + "Cách chạy key Suggest" (kết hợp internal + anchor + 50 social profile).

---

### TU-08 — Ramp-up dần, không đột biến

**Nhóm:** Thiết lập

**Tóm tắt:** Volume user tăng DẦN theo bậc thang, không bật max ngay ngày 1. Nhịp tham chiếu từ tài liệu gốc (cho key suggest/key N/A, keyword ngách VN): **10 ngày đầu ~10 user/ngày → từ ngày 11 tăng dần lên ~15 user/ngày**; key nhẹ có thể thấy kết quả sau ~5 ngày. Keyword volume lớn hơn → scale theo tỷ lệ CTR tự nhiên (TU-10), vẫn giữ nguyên tắc bậc thang + ổn định từng bậc.

**Mô tả đầy đủ:**
1. Kế hoạch ramp viết trước theo tuần: volume/ngày per keyword, ngày đổi bậc.
2. Không đổi bậc khi chưa đủ thời gian quan sát (tham chiếu: 10 ngày/bậc đầu).
3. Chạy ĐỀU quan trọng hơn chạy nhiều — case gốc: "chạy đều 10 user/day, ngày thứ 6 đã lên" ở ngách ít cạnh tranh.
4. Volume/ngày cho keyword volume cao: chưa có chuẩn nội bộ → đề xuất trong văn bản duyệt, Director chốt (xem Open Questions).

**Ví dụ Đạt / Không Đạt:**
✅ Key suggest ngách: ngày 1-10 = 10 user/ngày đều đặn; ngày 11+ = 15 user/ngày; log volume mỗi ngày.
❌ Ngày 1 bơm 200 user, ngày 3 nghỉ, ngày 5 bơm 300 — răng cưa đột biến.

**Nguồn:** pptx slides "Cách chạy key Suggest" + "Cách chạy key N/A" (10 user/day 10 ngày đầu, sau ngày 11 lên 15 user/day; key nhẹ 5 ngày) · case "Seothanhcong" (chạy đều 10/day, ngày 6 lên suggest).

---

### TU-09 — Phân bổ thiết bị / địa lý hợp lý (VN)

**Nhóm:** Thiết lập

**Tóm tắt:** Profile user phải giống người dùng thật của thị trường VN: mix thiết bị (mobile chiếm đa số theo ngành), địa lý phân bổ theo vùng khách hàng thật (không 100% từ 1 tỉnh/1 dải IP), trình duyệt/OS đa dạng, giờ truy cập theo nhịp ngày thật (không dồn 2h sáng). Đối chiếu với phân bố thật trong GA4/GSC của site trước khi chốt.

**Mô tả đầy đủ:**
1. Lấy phân bố thật (GA4: devices, cities; GSC: device) làm chuẩn — profile user mua vào không được lệch quá xa phân bố organic hiện có.
2. Keyword local → địa lý phải khớp khu vực (key "X quận 1" mà user toàn Hà Nội = footprint).
3. Yêu cầu nguồn user cung cấp báo cáo phân bố device/geo per đợt — nguồn không cung cấp được → điểm trừ thẩm định TU-05.
4. ⚠ pptx gốc KHÔNG có thông số phân bổ chuẩn — mục này là khung dựng theo nguyên tắc chống footprint; ngưỡng cụ thể chờ Vincent bổ khuyết (Open Questions).

**Ví dụ Đạt / Không Đạt:**
✅ Site organic 72% mobile, top 3 tỉnh HCM/HN/ĐN → yêu cầu nguồn ~70% mobile, geo trải theo tỷ lệ đó.
❌ 100% desktop Chrome cùng resolution, toàn IP 1 nhà mạng, truy cập 0h-4h.

**Nguồn:** Khung dựng từ nguyên tắc footprint (pptx không có thông số — ghi rõ gap) · GA4/GSC làm baseline đối chiếu.

---

### TU-10 — CTR mục tiêu trong ngưỡng tự nhiên của position

**Nhóm:** Thiết lập

**Tóm tắt:** Nguyên tắc gốc: **"Tính CTR để đẩy User"** — volume user tính NGƯỢC từ CTR tự nhiên của vị trí hiện tại, không bơm số tuyệt đối tùy hứng. CTR tổng (organic + user bơm) của keyword không được vượt xa ngưỡng CTR tự nhiên của position kế tiếp mà mình nhắm tới; vượt ngưỡng = footprint rõ nhất của hạng mục này.

**Mô tả đầy đủ:**
1. Per keyword: lấy impressions + CTR hiện tại từ GSC, tra CTR benchmark theo position (dùng data `gsc-ctr-by-position` của chính site làm chuẩn tốt nhất) → tính volume user/ngày sao cho CTR sau bơm ≈ CTR tự nhiên của position mục tiêu (nhích dần, không nhảy vọt).
2. Dùng file tính user (tài liệu gốc có "File tính user demo" — Google Sheet; xin link từ Director nếu chưa có bản dự án).
3. Impressions thấp (<50/ngày) → dừng lại cân nhắc: bơm user vào keyword impressions thấp làm CTR nhảy phi lý rất nhanh.
4. Ngưỡng CTR chuẩn nội bộ per position chưa chốt → Open Questions; tạm dùng CTR curve thực tế của site + không vượt CTR của position cao hơn 2 bậc.

**Ví dụ Đạt / Không Đạt:**
✅ Key pos 8, 400 impressions/ngày, CTR 1,2%; mục tiêu pos 5 (CTR site-curve ~4%) → ramp tới ~11-12 click/ngày, tăng bậc thang.
❌ Key pos 15, 30 impressions/ngày — bơm 50 click/ngày → CTR 160%+ phi thực tế.

**Nguồn:** pptx slide "Cách chạy User" ("Tính CTR để đẩy User"; "File tính user demo" — Google Sheet link trong slide) + "Lộ trình đẩy top key" ("Kết hợp tính CTR để đẩy user"). Ngưỡng cụ thể: gap — xem Open Questions.

---

## NHÓM 3 — GIÁM SÁT

### TU-11 — Đo lường tách biệt: annotation trong tracking

**Nhóm:** Giám sát

**Tóm tắt:** Ngày bật / đổi bậc volume / tạm dừng / tắt đều được **annotate** trong hệ tracking dự án (GA4 annotation, sheet tracking ranking, log dự án) — để mọi biến động ranking/traffic đọc được là "có user bơm từ ngày X, volume Y". Số liệu hạng mục này tách khỏi báo cáo organic thuần cho khách.

**Mô tả đầy đủ:**
1. Log tối thiểu per ngày: keyword, volume user giao, nguồn, chế độ (cần SEO/suggest/N/A).
2. Report nội bộ tách 2 lớp: organic thuần vs tổng (có user) — Account chỉ dùng lớp phù hợp với brief TU-03.
3. Kết thúc chiến dịch phải trả lời được: keyword nào lên nhờ nền (content/link), keyword nào chỉ giữ nhờ user (insight cho TU-16).

**Ví dụ Đạt / Không Đạt:**
✅ Sheet tracking có cột "TU volume/day" per keyword + annotation "08/T8: bật TU 8 keys @10/day".
❌ Ranking tăng nhưng không ai nhớ user bật ngày nào, volume bao nhiêu.

**Nguồn:** Khung đo lường GTV (pptx không đề cập — bổ sung bắt buộc cho hạng mục rủi ro cao).

---

### TU-12 — Theo dõi biến động ranking + GSC anomaly

**Nhóm:** Giám sát

**Tóm tắt:** Trong suốt thời gian chạy: theo dõi ranking keyword target (tối thiểu 2 lần/tuần) + GSC (impressions/CTR/position daily; tab Manual actions + Security issues hằng tuần). Bất kỳ dấu hiệu nào khớp trigger stop-loss TU-04 → dừng ngay theo quy trình, không đợi lịch review.

**Mô tả đầy đủ:**
1. Dashboard/sheet theo dõi: ranking + GSC metrics per keyword, đánh dấu ngày đổi bậc volume để đối chiếu nhân quả.
2. Anomaly cần bắt: CTR tăng nhưng position giảm (dấu hiệu Google discount/phạt hành vi), impressions tụt bất thường, keyword biến mất khỏi top 100.
3. Keyword lên bền qua checkpoint → cân nhắc GIẢM user sớm (mục tiêu là organic giữ vị trí, không phải user nuôi vị trí mãi).

**Ví dụ Đạt / Không Đạt:**
✅ Log thứ 2 & thứ 5 hằng tuần; ngày 18 phát hiện key A CTR tăng mà position tụt 3 → tạm dừng key A, báo Lead cùng ngày.
❌ Chạy 6 tuần chưa mở GSC lần nào.

**Nguồn:** Khung giám sát GTV + trigger từ TU-04 (pptx không có quy trình giám sát — bổ sung).

---

### TU-13 — Checkpoint 10 ngày + chuyển chế độ key đúng luật

**Nhóm:** Giám sát

**Tóm tắt:** Theo nhịp tài liệu gốc: **mốc 10 ngày** là checkpoint bắt buộc per keyword. Key N/A: sau 10 ngày check key đã vào top 100 chưa. Key suggest: check suggest đã xuất hiện chưa. Luật chuyển chế độ: key (suggest) đã vào **trang 1-2 → NGỪNG chạy key suggest, chuyển sang chạy key cần SEO** và quay lại quy trình từ đầu (gate + thiết lập cho chế độ mới).

**Mô tả đầy đủ:**
1. Lịch checkpoint per keyword đặt sẵn từ ngày bật (D+10, sau đó mỗi 7-10 ngày).
2. Kết quả checkpoint ghi vào tracking: đạt mốc → theo plan (tăng bậc/giữ); không đạt → chẩn đoán lại nền tảng TU-07 (content/link) thay vì chỉ tăng volume user.
3. Không đạt sau 2 checkpoint liên tiếp → đưa lên review Director (TU-14): tiếp tục / đổi chế độ / dừng key đó.

**Ví dụ Đạt / Không Đạt:**
✅ D+10: key N/A vào top 100 → giữ nhịp, tăng 15/day theo plan; key suggest đã hiện → chuyển chế độ key cần SEO, cập nhật văn bản phạm vi.
❌ Suggest đã hiện trang 1 từ tuần 2 nhưng vẫn đốt ngân sách chạy suggest thêm 1 tháng.

**Nguồn:** pptx slides "Cách chạy key N/A" (10 ngày check top 100; vào trang 1-2 → chuyển chế độ, "quay lại từ đầu, xem slide Cách chạy User") + "Cách chạy key Suggest" (nhịp 10 ngày/bậc).

---

### TU-14 — Lịch review với Director

**Nhóm:** Giám sát

**Tóm tắt:** Review định kỳ với SEO Director trong suốt thời gian chạy — tối thiểu 2 tuần/lần (khuyến nghị tuần/lần trong tháng đầu): số liệu TU-11/TU-12, checkpoint TU-13, chi phí vs ngân sách duyệt, đề xuất tiếp tục/điều chỉnh/dừng. Không có review đúng lịch = văn bản duyệt hết hiệu lực cho kỳ kế tiếp.

**Mô tả đầy đủ:**
1. Lịch review ghi ngay trong văn bản duyệt TU-01.
2. Mỗi review có note quyết định (tiếp tục/điều chỉnh gì) — append vào log dự án.
3. Hết T9 = hết cửa sổ triển khai theo lộ trình → muốn kéo dài phải có văn bản duyệt MỚI, không auto-extend.

**Ví dụ Đạt / Không Đạt:**
✅ Review 2 tuần/lần có note; cuối T9 chốt "đạt mục tiêu 6/8 key, tắt dần theo TU-15".
❌ Chạy qua T10 theo quán tính vì "chưa ai bảo dừng".

**Nguồn:** Khung quản trị hạng mục rủi ro cao GTV (bổ sung — pptx không có).

---

## NHÓM 4 — KẾT THÚC

### TU-15 — Tắt dần, không cliff

**Nhóm:** Kết thúc

**Tóm tắt:** Kết thúc (đạt mục tiêu, hết cửa sổ T9, hoặc stop-loss): volume user giảm BẬC THANG ngược (mirror giai đoạn ramp-up) — không tắt cụt từ max về 0 trong 1 ngày. CTR rơi thẳng đứng sau một thời gian cao bất thường = footprint kết thúc chiến dịch, và ranking dễ rơi theo "cliff".

**Mô tả đầy đủ:**
1. Kế hoạch tắt viết trước khi bật (nằm trong văn bản duyệt): vd giảm ~30-50% volume mỗi 5-7 ngày cho tới 0.
2. Trường hợp stop-loss khẩn (manual action) → được phép tắt ngay — an toàn pháp lý/penalty ưu tiên hơn smoothness; ghi rõ lý do.
3. Trong giai đoạn tắt dần: nền tảng organic (content/internal/backlink đều) phải tiếp tục — để organic gánh vị trí thay user.
4. Annotation ngày bắt đầu tắt + ngày về 0 (TU-11).

**Ví dụ Đạt / Không Đạt:**
✅ Đạt mục tiêu ngày 20/T9: 15/day → 10 (5 ngày) → 5 (5 ngày) → 0; ranking giữ nhờ nền link vẫn chạy.
❌ Hết ngân sách → tắt 100% qua đêm, tuần sau key rơi 6 bậc.

**Nguồn:** Nguyên tắc đối xứng với ramp-up (pptx chỉ có chiều tăng — chiều giảm là khung bổ sung theo cùng logic "đều đặn, không đột biến").

---

### TU-16 — Ghi nhận kết quả + bài học vào 12-feedback-lessons

**Nhóm:** Kết thúc

**Tóm tắt:** Đóng chiến dịch = có báo cáo kết thúc file về `12-feedback-lessons` của SEO Production instance: kết quả per keyword (before/after position, CTR, thời gian đạt), nguồn user dùng + đánh giá chất lượng (fake %?), chi phí/user thực tế, trigger nào suýt/đã kích hoạt, và bài học (chế độ nào hiệu quả, volume nào tối ưu, ngách nào không nên chạy).

**Mô tả đầy đủ:**
1. Báo cáo kết thúc nộp trong 7 ngày sau khi volume về 0; Director sign-off đóng hạng mục.
2. Đánh giá nguồn user vào danh sách nguồn (dùng lại/blacklist) — tài sản cho dự án sau.
3. Bài học có giá trị hệ thống (vd ngưỡng CTR thực nghiệm theo position) → đề xuất cập nhật ngược vào checklist này + Open Questions bên dưới.

**Ví dụ Đạt / Không Đạt:**
✅ Report: 6/8 key đạt top 5; nguồn A sạch, nguồn B nghi pha fake tuần 4 (đã cắt); chi phí 1.850đ/user; bài học ghi vào 12-feedback-lessons.
❌ Chiến dịch kết thúc không dấu vết — dự án sau lặp lại đúng các lỗi cũ.

**Nguồn:** Quy trình feedback-lessons SEO Production · pptx "Tóm lại về chạy user" (tư duy tính chi phí/user để so sánh phương án — input cho bài học).

---

## Thông số baseline GTV — đề xuất 19/07/2026 (Director chốt per dự án)

> Nguồn gốc pptx (22 slides, đọc bằng vision) cho nhịp ramp 10→15 user/day, 3 chế độ key, nguyên tắc "Tính CTR để đẩy User" và cảnh báo user fake — nhưng thiếu 5 thông số vận hành. Bộ số dưới đây là **baseline đề xuất** (Vincent duyệt 07/2026 cơ chế "đề xuất thử"); mọi dự án vẫn phải ghi số cụ thể vào văn bản duyệt TU-01, Director chốt cuối.

**1. Nguồn tool/nhà cung cấp** — pptx chỉ có ví dụ mô hình Traffic1s.com (site trung gian đổi mã, user từ Twitter/FB/YT) + "File tính user demo" (Google Sheet). Danh sách nguồn thẩm định 2026: xem mục **Phụ lục A — Nguồn user** cuối file (research 07/2026); mọi nguồn trước khi dùng vẫn phải qua thẩm định TU-05 + test nhỏ 5-7 ngày.

**2. Volume ramp cho keyword volume lớn** (volume ≥5.000/tháng hoặc impressions ≥500/ngày):
- Bậc thang: 15 → 25 → 40 user/day, mỗi bậc giữ 7-10 ngày, mỗi lần tăng ≤ +50% bậc trước.
- Trần cứng: min(**50 user/day/query**, **5% impressions hiện tại/ngày**). SERP có Shopping/AIO chiếm mạnh → hạ trần còn 3% impressions.
- Key ngách/suggest/N/A giữ nguyên nhịp gốc pptx 10→15/day.

**3. CTR benchmark theo position** (baseline VN non-brand — CHỈ dùng khi site chưa đủ data; ưu tiên tuyệt đối `gsc-ctr-by-position` của chính site):

| Position | CTR tự nhiên | Position | CTR tự nhiên |
|---|---|---|---|
| 1 | 25–32% | 6 | 3–4,5% |
| 2 | 13–18% | 7 | 2,5–4% |
| 3 | 8–12% | 8 | 2–3,5% |
| 4 | 6–8% | 9–10 | 1,5–3% |
| 5 | 4–6% | 11–20 | 0,5–1,5% |

Luật áp: CTR tổng sau bơm ≤ **trần của position MỤC TIÊU** (mục tiêu cách hiện tại ≤2 bậc) và ≤ **1,5× CTR site-curve** của position đó. Nhích bậc thang, không nhảy vọt (khớp TU-10).

**4. Stop-loss số hóa** (điền vào TU-04) — dừng NGAY khi chạm 1 trong 4:
- (a) Keyword target **rớt ≥3 bậc giữ ≥5 ngày liên tiếp** kể từ khi bật;
- (b) CTR tổng **vượt trần position 3 ngày liên tiếp** dù đã giảm volume;
- (c) Impressions **giảm ≥30%** so trung bình 7 ngày trước bật (loại trừ trùng Google update/seasonal — check TR-02 runbook);
- (d) **Manual action / Security issue** xuất hiện → dừng TOÀN BỘ + escalate Director trong 24h.
- Điều kiện thoát: sau **30 ngày** không cải thiện ≥2 bậc → tắt dần theo TU-15, không gia hạn tự động.

**5. Phân bổ thiết bị/địa lý chuẩn VN** (điền vào TU-09):
- Device: **mobile 65-75% / desktop 25-35%**, điều chỉnh theo GA4 của site ±10 điểm.
- Geo: **≥5 tỉnh**, trọng số theo phân bố khách thật (tham chiếu: HCM 30-40% / HN 20-30% / còn lại trải); key local → **≥70% user đúng tỉnh/khu vực**.
- Giờ truy cập 7h-23h theo nhịp ngày tự nhiên, khung đêm ≤10%; IP dân cư/di động VN — cấm datacenter/VPN.

---

## Phụ lục A — Nguồn user (research 07/2026, verify live)

**Trạng thái Traffic1s (mô hình gốc trong pptx):** vendor VN thật (thành lập 2016, Long Biên HN) nhưng **hạ tầng chính đã chết 07/2026** (traffic1s.com lỗi SSL 525, .org 404) — không dùng được nếu không liên hệ trực tiếp thẩm định lại từ đầu. "Traffica" không verify được — loại.

**Shortlist test nhỏ (theo TU-05, chưa phải danh sách duyệt):**

| Vendor | Mô hình | Giá | Ghi chú thẩm định |
|---|---|---|---|
| **TrafficSEO.net** (VN) — ưu tiên #1 | User thật download-only, cam kết không "nhiệm vụ", 1 click/user/ngày, dashboard log | 1.100-1.540đ/user | Minh bạch nhất; đang full slot phải đặt trước; ⚠ gắn mã vào site khách — Director cân nhắc footprint |
| **SEOTOP** seotop.vn (VN) — backup | User download (~100 site vệ tinh), có tool tính user/ngày ~10-15% volume | 1.500-1.800đ/user | ⚠ mã đếm ngược pass hiển thị trên site = footprint crawl được — chất vấn kỹ trước khi dùng |
| **SerpClix** (Intl) — chỉ dự án EN/quốc tế | Crowdsource người thật 400k+ clicker, IP residential | ~$0,37-0,64/click (~10× VN) | Trial 7 ngày free đáng benchmark; pool VN mỏng — key tiếng Việt phải test trước |

**Loại thẳng:** SearchSEO (bot emulator qua residential proxy — đúng loại "user FAKE" pptx cảnh báo) · faceseo.vn (500k/năm — giá phi lý = bot) · TrafficUserViet (kém minh bạch, chỉ xét nếu 2 vendor đầu fail).

**8 câu hỏi thẩm định vendor (chạy cùng TU-05):** (1) nguồn user: download/nhiệm vụ/tool? (2) tỷ lệ trùng IP + số click/user/ngày? (3) IP residential hay datacenter — xem sample log; (4) dwell time do đâu mà có? (5) có gắn mã lên site không — Googlebot render mã đó thế nào? (6) cap ngày/giờ + ramp tùy chỉnh được không? (7) dashboard log timestamp + keyword + position đối chiếu GSC được không? (8) taper khi key lên top được không?

**Test protocol trước khi scale:** 1 URL không phải money page × 10 user/ngày × 10 ngày → đối chiếu 3 nguồn (dashboard vendor / GA4 / GSC trễ ~2 ngày) → check ASN từng IP (dính datacenter = dừng ngay) → check phân bố tỉnh/thiết bị/giờ truy cập tự nhiên.

**Cảnh báo bổ sung 2026 (giữ nguyên khi trình Director):** spam update 06/2026 mở rộng sang thao túng AI search; **tuyệt đối không dùng cho local/GBP** (cộng đồng báo penalty nặng ở map pack); hiệu ứng mang tính duy trì — ngừng bơm là tụt (thí nghiệm Fishkin); mô hình download VN "thật người, giả intent" — hành vi sau click là vector Google đo ngày càng tốt.
