---
type: sop
status: draft
last_updated: 2026-10-02
sources:
  - raw/_ingested/gtv-training-backlink-that-truyen-v6.md
related:
  - "[[Link Building]]"
  - "[[TrustRank]]"
  - "[[PageRank]]"
  - "[[Reasonable Surfer]]"
  - "[[Authority Stacking]]"
  - "[[Tiered Link Building]]"
  - "[[Phantom Keywords]]"
  - "[[Traffic Users]]"
  - "[[Internal Linking Rules and Strategy]]"
tags: [semantic-seo, sop, offpage, backlink, stacking, gtv, risk-controlled]
---

# SOP 12 — Mô hình backlink stack (Model Layer)

> **Vị trí trong hệ thống:** SOP này thuộc quy trình backlink của GTV, đứng cạnh [SOP 10](10-offpage-process.md). SOP 10 quy định trình tự, handoff, người làm, người duyệt và method catalog. SOP 12 quy định cách chấm nguồn link (T.T.T), thư viện mô hình stack, bộ luật thiết kế, chuẩn tài sản, cách đo và điểm dừng.
>
> **Nguồn:** tài liệu training nội bộ "Bí thuật backlink thất truyền" (Vincent Do, 27/09/2026, bản 6). Các mục ghi nhãn bằng chứng B, C, D theo §11.
>
> **Chưa gắn vào quy trình 10 tháng.** [sop/09](09-project-timeline/10-thang-thuc-day.md) chưa có mốc cho mô hình stack. Vincent cập nhật sau. Cho tới lúc đó, mô hình stack chỉ chạy khi có phương án được duyệt theo §1.
>
> **Phạm vi bản này:** bản đóng gói cho đội SEO. Bảng năm dạng textlink báo, cách tìm nguồn trust cao qua Ahrefs, sáu mô hình mở rộng và danh sách vendor do SEO Lead và SEO Director giữ. Bước thao tác chi tiết không ghi trong SOP: SEO Lead hướng dẫn khi phương án được duyệt.

---

## 0. Nguyên tắc nền

1. **Backlink là gia tốc, không phải điều kiện bắt buộc.** Quy trình chuẩn của GTV vẫn đưa dự án lên top khi không dùng các mô hình trong SOP này. Gate "90% site chưa cần đẩy backlink" ở SOP 10 §1 vẫn đứng trước.
2. **Hỏi hai câu trước khi nghĩ tới mô hình:** quy trình chuẩn đã chạy đủ chưa, và dự án có thật sự cần gia tốc không.
3. **Gia tốc có kiểm soát:** đúng nguyên lý, đúng người duyệt, có điểm dừng ghi trước.
4. **Website có trust sẵn lên nhanh hơn với cùng quy trình (D).** Năm 2026 Google siết website mới và content AI làm hàng loạt. Website mới thiếu trust là trường hợp mô hình stack có ích nhất.
5. **Backlink chỉ phát huy khi content đứng được.** Content AI phải có information gain đưa vào prompt từ bước outline, AM và bước viết nháp, rồi người có chuyên môn duyệt và biên tập.

---

## 1. Quy trình duyệt

| Nhóm | Gồm | Duyệt |
|---|---|---|
| ✅ White hat | Semantic content, vibe-code tool, minisite, blog có UX/UI trên website của mình; traffic thật vào tài sản (§7.4) | Làm theo quy trình bình thường |
| ⚠ Grey hat và black hat | Mọi mô hình backlink trong §3, PBN, link tự động số lượng lớn, T3, textlink trang chủ, chuyên mục, sitewide của báo, mô hình báo có buffer, traffic user, social signal | **SEO Lead xem trước, SEO Director chốt.** Director duyệt mọi phương án, kể cả mô hình nhỏ |

Cách gửi:

1. Người làm điền worksheet (§9.1) và tự chấm rubric (§9.2), gửi SEO Lead (Line Manager).
2. SEO Lead soát kỹ thuật, chuyển SEO Director.
3. SEO Director chốt và feedback phương án cho dự án.
4. Khi phương án được duyệt, SEO Lead hướng dẫn bước thao tác chi tiết.

Không tự làm cho dự án khi chưa có trao đổi kỹ thuật. Tool white hat chỉ cần duyệt khi bắn tầng link vào nó.

---

## 2. Khung T.T.T: chấm một nguồn link

Hai cơ chế quyết định giá trị một backlink: [[PageRank]] đo link juice chảy qua link, [[TrustRank]] đo khoảng cách từ seed site tới trang. Khung T.T.T gom lại thành ba chữ:

- **Theme:** trang chứa link đúng chủ đề với trang đích.
- **Traffic:** trang nguồn có người dùng thật.
- **Trust:** gồm hai phần, sức mạnh (PageRank, link juice) và TrustRank (khoảng cách tới seed).

**Thang điểm 2026 (Vincent chốt 02/10/2026, nhãn D):** Theme 35 điểm, Traffic 35 điểm, Trust 30 điểm, tổng 100. Theme và Traffic nặng ngang nhau; Trust thấp hơn một bậc vì dễ bị đẩy bằng link. Chấm mỗi nguồn trên thang này và ghi điểm từng chữ vào worksheet. Bản training 27/09/2026 ghi "Traffic đứng đầu, Theme và Trust ngang nhau", tài liệu 2025 ghi "Theme > Trust > Traffic"; cả hai là bản cũ.

Bảng chấm nhanh trước khi đặt link hoặc dựng tài sản:

| Chữ | Câu hỏi | Cách kiểm nhanh |
|---|---|---|
| Theme | Title, URL và đoạn chữ quanh link có từ khoá của trang đích không? Chuyên mục và website cùng ngành chỉ là điểm cộng | Đọc tiêu đề, URL và vài câu quanh link. Bài PR trên báo tổng hợp vẫn đúng Theme nếu đủ ba chỗ |
| Traffic | Trang nguồn có người dùng thật vào không? Topic của nó có người tìm và có click không? | Xem traffic ước tính và keyword của đúng trang đó trên Ahrefs |
| Trust (sức mạnh) | Trang mạnh cỡ nào, có bao nhiêu link ra? | Đếm link ra trên trang, xem backlink trỏ vào trang; DR, Citation Flow để lọc thô |
| Trust (TrustRank) | Trang cách seed mấy bước? Có được báo lớn, Wikipedia, trang .gov trỏ tới không? | Xem referring domain chất lượng của trang và domain nguồn; Trust Flow của Majestic để đọc nhanh |

DR, DA, Trust Flow, Citation Flow là số của công cụ, không phải số của Google. Dùng để lọc thô; quyết định dựa trên ba chữ T.

**Danh sách seed của ngách (làm trước khi dựng tài sản):**

1. Tìm 20 trang cận seed: `site:gov.vn [chủ đề]`, "hiệp hội [ngành]", "[hãng] đại lý uỷ quyền", chuyên mục đúng chủ đề trên báo lớn.
2. Kiểm website dự án đã được nhắc tên hoặc có link ở từng trang chưa.
3. Đánh dấu 5 trang có thể có mặt trong 3 tháng tới (trang đại lý uỷ quyền, bài báo chuyên mục, danh sách hội viên).
4. Đưa 5 trang đó vào bản thiết kế mô hình làm đường ngắn nhất tới website.

Google không công bố danh sách seed. Wikipedia, báo lớn và trang .gov thuộc nhóm trust rank cao nhất, có thể coi phần nào như seed. Nhóm cận seed của từng ngách là cách GTV suy ra.

---

## 3. Thư viện mô hình

| Mô hình | Cấu trúc | Tăng phần nào | Hợp khi | Tier |
|---|---|---|---|---|
| **DAS** (Domain Authority Stacking) | Nhóm tài sản trên nền tảng trust cao liên kết với nhau, cùng trỏ về website | TrustRank | Website mới, thiếu trust chứ không thiếu nội dung | ⚠ |
| **TAS** (Traffic Authority Stacking) | DAS, thêm traffic thật cho từng tài sản và tầng T2 bắn vào tài sản | TrustRank và PageRank | Cần cả trust lẫn sức mạnh | ⚠ |
| **08 method** | Vòng các subdomain trên cùng một tên miền gốc; nút giữa chỉ một link về website | PageRank, dồn về một URL | Một keyword, category hay sản phẩm cần đẩy | ⚠ |
| **Mô hình báo có buffer** | Bài trung gian trên báo nhận link rủi ro, trỏ sang bài khác cùng báo bằng internal link, bài thứ hai trỏ về website | PageRank từ nguồn gần seed | Cần juice lớn mà vẫn cách ly rủi ro | ⚠ |
| **Link wheel giữa các domain rời** | Các domain nối thành vòng khép kín | | Không dùng | ⛔ |

Chọn mô hình theo dự án:

- **Mô hình 1 (kiểu TAS, trỏ nhiều URL):** thiên về TrustRank, an toàn hơn, hợp website mới.
- **Mô hình 2 (vòng 08 method, trỏ một URL):** thiên về PageRank.
- Làm mô hình 1 trước, có kết quả rồi mới sang mô hình 2.
- Dự án không đủ thời gian còn lại thì không bắt đầu (mốc thời gian ở §7.1).

Lưu ý theo mô hình:

- **Nền tảng đổi theo thời điểm.** Nền nào đang được đánh giá tốt thì xem tăng trưởng trên Ahrefs. SEO Lead giữ bảng nền tảng dựng được; tìm được nền mới thì báo về đó. Không dùng lại nền đã bị hạ giá.
- **Không dùng 08 method khi:** nền gắn nofollow cho link ra hoặc không index trang của tài khoản mới; không đủ nội dung thật cho các node; website quá mới, chưa có entity và link nền; ngách YMYL (y tế, tài chính, pháp lý).
- **Link wheel** giữa các domain rời là mô hình thao túng link; cấu trúc vòng là dấu hiệu nhận diện. Nguyên lý vòng chỉ dùng ở dạng internal link (pillar–cluster) trong cùng một website.
- **Quan điểm GTV về cơ chế (Google không công bố):** patent đo khoảng cách tới seed ở cấp trang, nhưng tài sản dựng trên nền trust cao vẫn thừa hưởng một phần trust của nền đó. Link giữa các subdomain cùng một nền có thể được Google coi là link trên cùng một hosting và xử lý khác với backlink giữa các domain rời. Kiểm bằng số đo ở §7.

---

## 4. Tầng link và luật tầng đẩy

- **T1:** tài sản hoặc link trỏ thẳng về website cần SEO.
- **T2:** link bắn vào T1.
- **T3:** link bắn vào T2.

Luật:

1. **Link càng rẻ và ồ ạt càng nằm sâu.** Link tự động số lượng lớn mặc định ở T3, chỉ chạm tầng đệm, không chạm website.
2. **Website chỉ nhận link từ T1 là tài sản thật.** Tài sản T1 vừa là trang đệm vừa lọc juice từ tầng đẩy.
3. **PBN có hai trường hợp.** PBN GTV tự dựng bài bản (nền sạch, content thật, có traffic, vận hành như website riêng) được trỏ thẳng website như T1. PBN order ngoài luôn đặt từ T2 trở xuống.
4. **Textlink báo mặc định là link T2**, trỏ vào tài sản T1 đúng chủ đề. Trỏ thẳng website khi chỗ đặt link khớp source context của trang đích và, với link ở trang chủ, chuyên mục, sitewide, website đã có nền tảng. Bảng điều kiện theo từng dạng do SEO Lead giữ.
5. **Parasite không trỏ thẳng website.** Vòng đời ngắn, chỉ đứng làm cầu đẩy vào tài sản T1 bền.
6. **Đợt T2 chỉ mở khi tầng ngay trên đã index.**
7. **Trên website khách không đặt link rủi ro.** Với tool trên minisite: trang chủ nhận link an toàn trước, link rủi ro vào cụm bài cluster rồi internal link về trang tool.

"Website có nền tảng" gồm: entity tốt (social, Google stack, citation, trang giới thiệu và tác giả rõ ràng); referring domain từ nhiều loại nguồn, không thua xa đối thủ cùng tầng trang; DR/DA tăng đều và có traffic organic. Mốc theo ngành do SEO Lead chốt.

Chính sách Google cần biết (B): link trả phí không gắn `rel="sponsored"` hoặc `nofollow` và link rải ở footer, template của nhiều site thuộc nhóm link spam; chính sách site reputation abuse (19/11/2024) áp cho nội dung bên thứ ba đăng trên một host để mượn tín hiệu xếp hạng. Textlink dofollow chỉ nên là phần nhỏ của profile. Link sitewide lặp trên nhiều trang không cộng tuyến tính: leak 2024 cho thấy mỗi cặp domain và chữ neo chỉ giữ 200 anchor (C); sitewide mạnh là nhờ nằm trên nhiều trang được crawl dày và gần seed.

---

## 5. Bộ luật thiết kế mô hình

### 5.1 Năm luật gốc (GTV dùng từ 2018, nhãn D)

1. Một tài sản link ra tối đa **3 link**.
2. Tối đa **2 link về website** từ một tài sản.
3. Hai tài sản đã nối với nhau thì mỗi cái chỉ còn **1 link về website**.
4. URL quan trọng nhất nhận nhiều link nhất; các URL còn lại nhận ít hơn.
5. Mỗi tài sản khác nhau một chút về nội dung và cách đặt link, như các website độc lập.

Cách đếm để cả đội đếm giống nhau:

- **Link ra** của một tài sản là link sang một mắt xích khác trong mô hình hoặc sang website. Internal link giữa các bài trong cùng một tài sản không tính. Riêng trang đặt link đi thì cả trang không quá 3 link ra ngoài, kể cả link trích nguồn và link nofollow.
- **Bước nhảy** tính theo đường dài nhất đi xuôi chiều juice, từ mắt xích xa nhất (kể cả T2, T3) tới URL cần SEO. Internal link trên website cũng là một bước. Link chạy vòng trong cùng một vòng 08 method không cộng.

### 5.2 Mười nguyên lý bổ sung 2026

Chỗ nào hai nhóm cùng nói về một con số thì theo luật gốc.

| # | Nguyên lý | Kiểm nhanh |
|---|---|---|
| 1 | Đường dài nhất không quá 5 bước nhảy (D) | Tìm đường dài nhất trên sơ đồ, tính cả T2, T3. Muốn mở rộng thì thêm tài sản song song trong cùng tầng, không nối dài chuỗi |
| 2 | Nền DR cao đổ về tài sản thấp hơn, không trỏ ngược | Trong lớp tài sản tự dựng, nền cao đặt ở xa, càng gần website càng là tài sản nhỏ hơn |
| 3 | Đường juice chính là link dofollow, cùng chủ đề (B: nofollow là gợi ý từ 10/09/2019) | Mở mã nguồn trang thật để kiểm rel của từng link. Mỗi mắt xích có một đoạn nội dung nối chủ đề về trang cần SEO |
| 4 | Mọi tài sản tự dựng có traffic thật | Ghi nguồn traffic cho từng mắt xích trong worksheet |
| 5 | Mỗi tài sản dựng như một website thật | Có cụm bài theo một chủ đề, tool tính đúng, giao diện như website thương hiệu. Sơ đồ không có node rỗng |
| 6 | Tài sản được index rồi mới bơm tầng dưới | Ghi trạng thái index và ngày kiểm cho từng tài sản |
| 7 | Có ít nhất một mắt xích là bài báo có sẵn | Sơ đồ có ít nhất một bài báo đúng chủ đề, đã index, có đường tới website |
| 8 | Vòng link nằm trên cùng một tên miền gốc | Khoanh mọi vòng khép kín. Vòng nào đi qua hơn một tên miền gốc thì cắt một cạnh |
| 9 | Đa dạng nền tảng và chủ sở hữu (B: patent tính theo seed gần thứ k) | Mỗi lớp tài sản có ít nhất hai chủ nền tảng khác nhau |
| 10 | Nhịp link theo nhịp tự nhiên của ngành (B: patent US7346839) | Theo §10; lệch nhịp thì dừng đợt và báo SEO Lead |

### 5.3 Sáu bước vẽ một mô hình

1. Chọn URL đích: URL cần SEO, keyword mục tiêu, vị trí hiện tại, các trang supporting dẫn về nó.
2. Chọn mô hình gốc theo §3.
3. Xếp tài sản theo DR gốc: nền cao ở tầng xa, tài sản nhỏ hơn ở giữa, hub và bài báo có sẵn ở gần website.
4. Nối link theo một chiều từ xa về gần; ghi số link ra và số link về website vào từng ô. T2 chỉ trỏ vào tài sản, T3 chỉ trỏ vào T2.
5. Đếm đường dài nhất. Vượt 5 bước thì bỏ một tầng hoặc chuyển tài sản sang cột gần hơn.
6. Gắn traffic và điểm dừng cho từng mắt xích, điền worksheet (§9.1), tự chấm rubric (§9.2), gửi duyệt (§1).

---

## 6. Chuẩn tài sản 2026

Chuẩn 2018 (bài chính khoảng 1.200 chữ, bài support khoảng 500 chữ) không còn đủ. Bài khoảng 500 chữ không còn gây ấn tượng với Google và không thể hiện human effort, vì AI tạo dạng bài này quá dễ. Tài sản stack phải làm như một website thật: content có human effort, có UX/UI, có traffic. Làm 10–20 bài chất lượng cho một tài sản thì nó bền hơn và nhận link tầng đẩy tốt hơn (D).

### 6.1 Checklist MS-01 → MS-14

Tài sản chưa đạt đủ 14 dòng thì chưa gắn vào stack và chưa bơm tầng đẩy. Áp cho minisite, tool và web 2.0 làm như website thật.

| ID | Tiêu chí | Đạt khi |
|---|---|---|
| MS-01 | Có 10–20 bài theo một phantom topic | Mỗi bài có outline, trả lời một câu hỏi hẹp, không trùng thuộc tính với bài khác |
| MS-02 | Có bài đi link và ít nhất 4 bài support trỏ về nó | Bài đi link có câu trả lời thẳng, số liệu có nguồn, link đặt dưới heading nối chủ đề |
| MS-03 | Không có đoạn chép từ trang cần SEO | Tài sản nói góc khác và dẫn về trang cần SEO |
| MS-04 | Tool tính đúng và chạy thật | Đã thử ít nhất 10 bộ đầu vào, đối chiếu tính tay; không có nút hay chức năng giả |
| MS-05 | Tool ở vùng hiển thị đầu tiên của hub | H1 là truy vấn chính, phần giải thích công thức nằm ngay dưới tool |
| MS-06 | Thứ bậc thị giác rõ | Một điểm nhấn chính, CTA chính và phụ, khối trust đặt cạnh CTA |
| MS-07 | Thẻ cùng loại dùng chung một khung, lặp ít nhất 3 lần | Dữ liệu nhiều thì có bảng thuộc tính và giá trị |
| MS-08 | Dùng tốt trên điện thoại | Tool bấm được bằng ngón tay, chữ không tràn, không popup che nội dung |
| MS-09 | Cả tài sản tối đa 3 link out, 1–2 URL về website | Link về website nằm trong thân bài, trong đoạn 100–200 chữ đúng chủ đề |
| MS-10 | Internal link theo cụm | Hub trỏ tới mọi bài, bài support trỏ về bài đi link, không có trang mồ côi |
| MS-11 | Bản production không noindex, có sitemap và canonical | Đã kiểm header; robots.txt không chặn |
| MS-12 | Schema và metadata nằm trong HTML ban đầu | WebApplication cho tool, Article cho bài, Organization hoặc Person cho người biên soạn |
| MS-13 | HTML nhẹ và đúng cấu trúc | Mỗi trang dưới 2 MB, ảnh có width và height, thẻ main, article, section đặt đúng chỗ |
| MS-14 | Có nguồn traffic đầu tiên | Bài được chia sẻ ở cộng đồng đúng chủ đề hoặc chạy ads ngân sách nhỏ; sự kiện dùng tool đã được đo |

Chính sách liên quan (B): Google nhắm tới việc tạo nhiều trang chủ yếu để thao túng xếp hạng mà không thêm giá trị (scaled content abuse) và tool giả, nút giả (misleading functionality). Vài trăm trang biến thể chỉ đổi một chữ trong tiêu đề nằm ở phía vi phạm.

### 6.2 Tool và minisite

- Trước khi viết bài, hỏi "topic này làm thành tool được không". Tool là tài sản T1 có traffic thật và tự nó là tài sản kinh doanh dài hạn.
- **Chọn topic có click, không chỉ có volume.** Keyword thông tin thuần thường bị AI Overview trả lời trên SERP.
- **Chấm cầu nối ngữ cảnh 1–3 trước khi nhìn volume:** 3 khi tài sản và trang cần SEO dùng chung một mẫu truy vấn; 2 khi cùng lĩnh vực nhưng khác mẫu; 1 khi xa nhau. Cụm volume cao mà điểm 1 thì để sau. Mỗi trang cần SEO nên nhận link từ ít nhất ba tài sản khác góc.
- Đối thủ đã có tool trên website của họ và đang top thì đó là khoảng trống on-site phải lấp trước.
- **Hosting:** dùng hosting miễn phí trước; traffic cao thì chuyển sang trả phí hoặc hosting chung của công ty.
- **Domain:** làm backlink thì mua domain riêng hoặc dùng subdomain của một web 2.0. Không dùng subdomain của khách. Tool white hat thì dựng thẳng trên website của mình.
- Đưa keyword liên quan vào subdomain hoặc URL của tài sản: cách này có tác dụng tăng Theme (GTV xác nhận từ thực tế). Không nhồi từ khoá: leak 2024 có mức hạ điểm cho exact match domain (C).

---

## 7. Đo và lịch kiểm

### 7.1 Mốc thời gian (D)

Bắn link thẳng thấy tín hiệu sau khoảng 1 tháng; đi qua T2 khoảng 1,5 tháng; mô hình stack cần 1,5–2 tháng mới thấy hiệu quả và khoảng 3 tháng đạt tối đa. Đây là mốc kinh nghiệm, không phải cam kết. Dự án có mùa vụ hoặc deadline đếm ngược từ mốc cuối tháng 3 để biết phải bắt đầu khi nào.

### 7.2 Đo theo ba tầng

Đọc số từ tầng 1 lên. Tầng 1 chưa đạt thì chưa kết luận gì ở tầng 3.

| Tầng | Chỉ số | Công cụ | Tần suất |
|---|---|---|---|
| 1 · Tài sản index, crawl | Tỷ lệ URL tài sản đã index, link còn sống, lần crawl gần nhất, trang chứa link T2 đã index chưa | Search Console cho tài sản xác minh được; truy vấn `site:`; Ahrefs hoặc Semrush | Ngày 7, ngày 30, sau đó hằng tháng |
| 2 · Tài sản lên hạng phantom, có traffic | Vị trí phantom keyword của bài đặt link và hub; impression, click của tài sản; lượt dùng tool | Rank tracker; property Search Console riêng cho từng tài sản; event GA4 cho tool | Hằng tuần |
| 3 · Trang cần SEO nhúc nhích | Vị trí keyword mục tiêu; impression của URL; referring domain mới đã loại link spam; phân bổ anchor | Rank tracker, Search Console, Ahrefs | Hằng tuần; chốt ở tuần 8 và cuối tháng 3 |

Một link chỉ tính là "đã có" khi đủ bốn điều kiện: còn sống, đã index, anchor đúng kế hoạch, ngữ cảnh quanh link còn nguyên (khớp SOP 10 §5).

### 7.3 Bốn mốc kiểm

Ngày 0 là ngày tài sản đầu tiên được đăng. Ghi sẵn bốn ngày kiểm vào lịch dự án ngay khi mô hình được duyệt.

| Mốc | Kiểm gì | Quyết định |
|---|---|---|
| Ngày 7 | Link đã live chưa, tài sản đã gửi index chưa, Google đã crawl lần đầu chưa | Chưa được crawl thì thúc bằng internal link từ trang mạnh, chia sẻ thật và sitemap |
| Ngày 30 | Tỷ lệ index của đợt; phantom keyword của tài sản đã có impression chưa | Dưới 80% thì thúc vòng 2; sau hai vòng vẫn dưới 80% thì đổi nguồn. Tài sản đã index thì mới mở đợt T2 |
| Tuần 8 | Bài đặt link, hub đã vào top 30 phantom chưa; tài sản có traffic chưa; trang cần SEO có impression tăng hoặc vị trí nhích chưa | Lần đánh giá đầu tiên. Đạt thì giữ nhịp; tài sản chưa vào top 30 thì sửa tài sản trước khi bơm thêm |
| Cuối tháng 3 | Vị trí keyword mục tiêu so với lúc bắt đầu; tầng 1 và tầng 2 còn đạt không | Giữ, sửa hay dừng. Trang cần SEO không đổi hạng thì dừng bơm, audit lại content và onpage, rồi xem lại mô hình theo §5 |

Ngưỡng 80% index, top 30 phantom và 4 tuần chưa index là mốc kinh nghiệm GTV (D), không phải ngưỡng Google công bố. Trước tuần 8, trang cần SEO chưa đổi hạng là bình thường.

### 7.4 Traffic thật vào tài sản (✅ white hat)

1. Chọn topic có người tìm và có click.
2. Tool có người dùng lặp lại; đo lượt dùng bằng event GA4.
3. Internal link từ bài đang có traffic về bài đặt link trong cùng tài sản.
4. Chia sẻ thật khi đăng và khi cập nhật trên các kênh đang hoạt động của dự án (fanpage, newsletter, nhóm cộng đồng).

Giả lập click, traffic bot, thuê người bấm theo kịch bản và mua social signal không thuộc phần này. Đó là nhóm traffic user và social signal: theo SOP 10 §4 và checklist `tier-1-traffic-users.md`, SEO Director duyệt bằng văn bản.

---

## 8. Kill switch

Kill switch là điều kiện dừng ghi sẵn trước khi chạy. Tầng dưới chưa đạt thì không bơm thêm link vào tầng trên, dù trang cần SEO đang đứng yên.

| Tín hiệu | Hành động | Hướng |
|---|---|---|
| Tài sản chưa index sau 4 tuần, đã thúc hai vòng | Dừng đặt link vào tài sản đó; sửa nội dung hoặc chuyển sang nền khác | Dừng; tháo nếu sửa không được |
| Nền tảng thêm noindex, nofollow hoặc đổi điều khoản | Ngừng dựng thêm trên nền đó; chuyển bản HTML đã sao lưu sang nền khác | Tháo |
| Đợt T2 index dưới 80% sau hai vòng thúc | Đổi nguồn; không lấy thêm từ nguồn cũ | Dừng nguồn đó |
| Tuần 8, bài đặt link chưa vào top 30 phantom | Không bơm thêm T2; sửa tài sản về nội dung, tool và traffic | Dừng bơm, giữ tài sản |
| Tuần 8, tầng 1 và tầng 2 đạt nhưng trang cần SEO chưa đổi hạng | Bình thường ở mốc này; giữ nhịp và đo tiếp tới cuối tháng 3 | Giữ |
| Cuối tháng 3, trang cần SEO không đổi hạng | Dừng bơm, không lấy thêm link; audit content và onpage; xem lại mô hình theo §5 | Dừng |
| Số link mới lệch hẳn nhịp của ngành và đối thủ, hoặc một cụm anchor dồn vào vài ngày | Dừng đợt đang chạy và báo SEO Lead; đợt sau do người duyệt chốt | Dừng |
| Search Console có thông báo tác vụ thủ công | Dừng mọi đợt, báo SEO Director, xử lý theo §10.3 | Dừng |

Để tháo được, ngay từ đầu giữ ba thứ ngoài nền tảng: mã nguồn HTML trong một repo riêng, bản xuất nội dung của mọi bài, danh sách URL cùng link out của từng tài sản.

---

## 9. Worksheet và rubric

### 9.1 Worksheet stack

Một mô hình chỉ được gửi duyệt khi mọi ô đã điền, kể cả cột điều kiện dừng.

| Mục | Điền |
|---|---|
| Trang cần SEO · keyword mục tiêu · vị trí hiện tại | |
| Mô hình gốc (§3) hoặc tự vẽ theo §5.3 | |
| Ngày bắt đầu · mốc tuần 8 · mốc cuối tháng 3 | |
| Đường dài nhất (số bước nhảy) · số link ra lớn nhất · số link về website lớn nhất | |
| Người duyệt: SEO Lead xem trước · SEO Director chốt · ngày chốt | |

Bảng từng mắt xích:

| Mắt xích (tên · nền tảng · DR gốc) | Phantom | Link ra (số link và đích) | Bước | Index (trạng thái · ngày kiểm) | Traffic (lượt/tuần · nguồn) | T2 | Dừng khi |
|---|---|---|---|---|---|---|---|
| Ví dụ: Hub · Cloudflare Pages · DR gốc 93 | tính lượng cà phê xay theo số cốc | 1 link → URL cần SEO | 1 | Đã index · ngày 9 | 120 lượt/tuần, tìm kiếm và chia sẻ | Không | Chưa vào top 30 phantom ở tuần 8 |

### 9.2 Rubric 10 tiêu chí

Người làm tự chấm trước khi gửi; SEO Lead dùng để soát nhanh. Trượt một trong ba tiêu chí dòng juice thì sửa sơ đồ trước khi chấm tiếp.

| # | Nhóm | Tiêu chí | Đạt khi |
|---|---|---|---|
| 1 | Dòng juice | Link ra và link về website | Mỗi tài sản tối đa 3 link ra và 2 link về website; hai tài sản đã nối thì mỗi cái chỉ 1 link về |
| 2 | Dòng juice | Không quá 5 bước nhảy | Đường dài nhất, tính cả T2 và T3, tới URL cần SEO không quá 5 bước |
| 3 | Dòng juice | DR cao đổ về DR thấp | Trong lớp tài sản không có link nào từ nền DR gốc thấp trỏ lên nền cao hơn |
| 4 | Chất lượng mắt xích | T.T.T đã chấm | Mọi nguồn trỏ thẳng website đã chấm theo bảng §2 trên thang 100 (Theme 35, Traffic 35, Trust 30); nguồn thiếu chữ nào thì ghi cách bù hoặc đặt xuống T2 |
| 5 | Chất lượng mắt xích | Dofollow và cùng chủ đề | Đã kiểm rel trên trang thật; mọi mắt xích có đoạn nội dung nối chủ đề về trang cần SEO |
| 6 | Chất lượng mắt xích | Mọi tài sản tự dựng có traffic | Worksheet ghi nguồn traffic cho từng mắt xích |
| 7 | Chất lượng mắt xích | Có mắt xích báo | Ít nhất một bài báo có sẵn, đúng chủ đề, đã index |
| 8 | An toàn và đo | Nhịp và anchor tự nhiên | Không có đợt dồn link, không dồn một cụm anchor vào vài ngày; loại anchor cho từng nguồn do người duyệt chốt |
| 9 | An toàn và đo | Có log đo | Bảng đo ba tầng với ngày kiểm 7, 30, tuần 8 và cuối tháng 3; ghi cả những lần số không đạt |
| 10 | An toàn và đo | Có điểm dừng | Kill switch ghi trước cho từng tài sản và từng đợt T2 |

Bốn nguyên lý không có dòng riêng trong rubric (dựng như website thật, index trước khi bơm, vòng trên cùng tên miền gốc, đa dạng nền tảng) vẫn phải đạt trước khi gửi duyệt. Anchor theo canonical framework ở SOP 10 §1.4.

---

## 10. Đa dạng, velocity và khi stack bị vô hiệu

### 10.1 Đa dạng

- Link nền (profile, citation, web 2.0 có hoạt động thật) có mặt trước link mạnh.
- Dofollow đi cùng nofollow.
- Tài sản nằm trên nền của nhiều công ty khác nhau.
- Profile của website trải về trang chủ, trang supporting và trang tiền. Mô hình dồn juice về một URL vẫn nằm trong một profile có link về nhiều trang khác.
- Căn cứ: patent US7783639 mô tả link từ các trang nguồn có liên hệ với nhau (đồ thị link, cùng hostname, cùng dải IP) có thể chỉ được tính theo giá trị lớn nhất thay vì cộng dồn (B), nên mười tài sản giống hệt nhau có thể chỉ được tính như một.

### 10.2 Velocity

Không có con số velocity an toàn cố định cho mọi website. GTV giữ nhịp bằng ba nguyên lý:

1. **Tăng đều theo nhịp tự nhiên của ngành.** Link mới đến đều qua các tuần, nhiều loại link cùng lúc, không bung một đợt rồi dừng hẳn. Website mới đi chậm hơn website đã có nền.
2. **Theo dõi đối thủ.** Nhịp referring domain mới hằng tháng của đối thủ top đầu là thước đo; mỗi tháng so nhịp của dự án với nhịp này (khớp SOP 10 §1.5).
3. **Lệch thì dừng.** Nhịp vượt hẳn nhịp ngành, hoặc một cụm anchor dồn vào vài ngày, thì dừng đợt đang chạy và báo SEO Lead.

### 10.3 Dấu hiệu stack bị vô hiệu

Từ 2016 Google chủ yếu vô hiệu hoá link xấu thay vì phạt, nên stack bị vô hiệu thường không kèm thông báo. Rủi ro hay gặp nhất là tiền và công bỏ vào không ra juice. Dấu hiệu:

- Tài sản rớt khỏi index, hoặc chưa index sau 4 tuần dù đã thúc hai vòng.
- Phantom keyword của nhiều tài sản cùng rớt khỏi top 30 trong thời gian ngắn.
- Link đã index từ 80% mỗi đợt trở lên mà URL cần SEO không đổi hạng ở tuần 8 và tới cuối tháng 3 vẫn đứng yên.
- Impression của trang cần SEO tăng vọt vài ngày rồi rơi đột ngột.
- Search Console có thông báo tác vụ thủ công. Đây là dấu hiệu duy nhất về link mà Google báo trực tiếp.

Thứ tự xử lý:

1. Dừng mọi đợt T2, T3 vào nhánh có vấn đề và báo SEO Lead.
2. Kiểm lại sơ đồ theo §5.
3. Sửa tài sản: thêm bài, sửa tool, gỡ node rỗng.
4. Đổi nền khi nền thêm noindex, nofollow hoặc đang bị lạm dụng nặng.
5. Xét disavow sau cùng.

**Disavow:** chỉ xét khi website có tác vụ thủ công về link, hoặc đã có một mạng link lớn trỏ vào website và mạng đó có khả năng dẫn tới tác vụ thủ công (khớp tài liệu Google, B). SEO Lead chuẩn bị danh sách link và lý do; SEO Director quyết.

---

## 11. Nhãn bằng chứng và điểm chưa kiểm chứng

| Nhãn | Nghĩa |
|---|---|
| B | Tài liệu công khai của Google hoặc bằng sáng chế |
| C | Số của bên thứ ba, công cụ ước tính, số người đăng tự công bố |
| D | Mốc kinh nghiệm GTV, chưa có phương pháp đo công bố. Coi là tín hiệu tự kiểm, không phải luật |

Các điểm dưới đây Google không công bố. Vincent đã chốt cách ghi ngày 02/10/2026; dùng như quy tắc thực hành của GTV và kiểm bằng số đo dự án:

- Quy tắc 5 bước nhảy và 3 link ra: quy tắc của GTV.
- Thang điểm T.T.T: Theme 35, Traffic 35, Trust 30.
- Tài sản trên nền trust cao thừa hưởng một phần trust của nền; patent đo khoảng cách ở cấp trang.
- Link giữa các subdomain cùng một nền có thể là link trên cùng một hosting; Google xử lý khác backlink giữa các domain rời.
- Keyword trong subdomain và URL có tác dụng tăng Theme.
- Wikipedia, báo lớn, trang .gov thuộc nhóm trust rank cao nhất, có thể coi phần nào như seed.
- Bài khoảng 500 chữ không còn thể hiện human effort.
- Ngưỡng 80% index, top 30 phantom, 4 tuần chưa index: mốc kinh nghiệm GTV.

Một điểm đã có nguồn: site làm programmatic SEO mất niềm tin của Google thì việc khắc phục "tốn thời gian và công sức đáng kể" (John Mueller, Google, phát biểu trên Bluesky tháng 09/2026; theo techwyse.com ngày 09/09/2026 và relevantaudience.com).

Bản đối chiếu đầy đủ 44 claim nằm ở wiki Google Leak Decoded (`fact-check-training-backlink-v6`), tra trên máy master.

---

## Changelog

- **2026-10-02 v1.1** — Vincent chốt cách ghi các điểm Google không công bố: thang điểm T.T.T là Theme 35, Traffic 35, Trust 30 (§2, rubric #4); tài sản thừa hưởng một phần trust của nền và link giữa subdomain cùng nền được xử lý khác backlink giữa domain rời (§3); Wikipedia, báo lớn, .gov thuộc nhóm trust rank cao nhất (§2); keyword trong subdomain và URL có tác dụng (§6.2); bài 500 chữ không còn thể hiện human effort (§6); giới hạn 200 anchor cho sitewide (§4); nguồn John Mueller về programmatic SEO (§11).
- **2026-10-02 v1.0** — tạo từ tài liệu training "Bí thuật backlink thất truyền" bản 6 (Vincent duyệt ingest 02/10/2026). Phạm vi bằng bản đội SEO: không gồm bảng năm dạng textlink báo, cách tìm nguồn trust cao qua Ahrefs, sáu mô hình mở rộng, danh sách vendor. Chưa gắn vào quy trình 10 tháng (sop/09).
