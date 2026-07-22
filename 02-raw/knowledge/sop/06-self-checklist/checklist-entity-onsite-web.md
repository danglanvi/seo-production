---
type: sop
tier: 1-deep-dive
phase: entity-onsite
parent: sop/06-self-checklist/tier-1-entity.md
last_updated: 2026-07-19
source_file:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình Entity Onsite Web - GTV SEO.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình Entity Onsite Web - The AI Growth - AI & Automation Content.xlsx
items_count: 36
tags: [sop, entity, onsite, checklist, deep-dive, quality-gate]
---

# Deep Checklist — Entity Onsite Web (EO-01…EO-36)

> **Quan hệ với `tier-1-entity.md`:** Tier-1 Entity (EN-01…EN-16) là **self-check nhanh per mốc** (gate cuối T1 / cuối T3). File này là **DEEP-DIVE của riêng phần ONSITE** — checklist triển khai chi tiết **từng trang/từng hạng mục**, dùng khi thực thi công đoạn 13 (nhóm Onsite). Mỗi nhóm ghi rõ "chi tiết hóa EN-xx"; không mâu thuẫn ID/nội dung với tier-1.
> **Ai dùng:** SEO Executive/Technician triển khai + Content Executive viết trang entity. Tick per trang; tổng hợp lên EN-01…EN-06 khi self-check mốc.
> **Nguồn chính:** `Quy trình Entity Onsite Web - GTV SEO.xlsx` (6 sheets — bản đầy đủ hơn; bản TAG variant chỉ có 4 sheets, thiếu "Triển khai IFTTT" + "Tối ưu Schema", nội dung 4 sheets chung giống hệt).
> **Nhãn nguồn per item:** GIỮ (giữ nguyên tinh thần legacy) · SỬA (legacy có nhưng sai/cũ, đã nâng cấp) · MỚI (2023 chưa có — bổ sung theo wiki/sop hiện hành).

## P0 Gate — 7 items PHẢI pass (fail = chưa close Entity Onsite / chưa qua EN-xx tương ứng)

| Item | Tên | Đổ về tier-1 |
|---|---|---|
| EO-01 | Brand Info Pack = single source of truth | EN-01 🔒P0-T1 |
| EO-09 | 1 URL Entity Home được chỉ định + canonical | EN-02 🔒P0-T1 |
| EO-10 | Entity Home đủ E-A-V, không generic | EN-02 🔒P0-T1 |
| EO-15 | Trang liên hệ: NAP crawlable text khớp info pack | EN-05 🔒P0-T1 |
| EO-19 | Đủ bộ trang chính sách theo mô hình DN (ecommerce = bắt buộc) | EN-03 |
| EO-33 | NAP footer sitewide đồng nhất 100% | EN-05 🔒P0-T1 |
| EO-36 | Schema tầng site: CÓ + ĐÚNG LOẠI + @id graph nối đúng, validate pass | EN-06 🔒P0-T1 |

## Map nhóm → tier-1 → wiki

| Nhóm | Items | Chi tiết hóa | Wiki WHY chính |
|---|---|---|---|
| A. Chuẩn bị & tracking | EO-01…04 | EN-01, EN-03, EN-16 | [[Entity Identity Management]], [[Central Entity]] |
| B. Trang chủ | EO-05…08 | EN-02, EN-05, EN-06 | [[Entity Home]], [[Brand Identity]] |
| C. Trang giới thiệu (Entity Home) | EO-09…14 | EN-02 | [[Entity Home]], [[E-A-V Framework]] |
| D. Trang liên hệ | EO-15…18 | EN-03, EN-05 | [[Entity Identity Management]], [[Knowledge-Based Trust]] |
| E. Trang chính sách | EO-19…21 | EN-03 | [[Knowledge-Based Trust]] |
| F. Author / Founder / đội ngũ | EO-22…27 | EN-04, EN-06 | [[Authorship]], [[Algorithmic Authorship]] |
| G. Đại lý / chi nhánh | EO-28…29 | EN-03, EN-05, (EN-10) | [[Entity Home]] (local surface) |
| H. Trust bổ trợ (tuyển dụng, dự án, FAQ) | EO-30…32 | EN-03 | [[Knowledge-Based Trust]], [[Source Context]] |
| I. Footer / sitewide | EO-33…35 | EN-05 | [[Entity Identity Management]] |
| J. Schema tầng site | EO-36 | EN-06 | [[Structured Data]], [[Knowledge Graph]] |

---

## Nhóm A — Chuẩn bị & tracking (chi tiết hóa EN-01, EN-03, EN-16)

### EO-01 — Brand Info Pack = single source of truth 🔒P0

**Nguồn:** GIỮ+GỘP — sheet "Tạo lập các Trang Entity cần th" bước 2.0 (chuẩn bị thông tin DN) + sheet "Tối ưu Schema" bước 1.0 (địa chỉ, SĐT chính, Maps). Legacy note "hạn chế fake" → nay là **bắt buộc thông tin thật**, khách confirm.
**WHY:** [[Entity Identity Management]] — mọi document nói về entity phải thống nhất; một field lệch là một tín hiệu nhiễu cho entity reconciliation trong [[Knowledge Graph]].
**Check (pass/fail):**
- ✅ Tồn tại 1 file Brand Info Pack (theo EN-01) và **mọi trang onsite trong checklist này lấy thông tin TỪ file đó** — không ai gõ tay NAP/bio riêng.
- ✅ Field tối thiểu cho onsite: tên đúng ĐKKD, tên thương hiệu, MST, địa chỉ (1 cách viết duy nhất), phone, email, giờ làm việc, map embed code, logo, bio ngắn/dài, danh sách social profile THẬT.
- ❌ Fail: NAP trên trang liên hệ khác NAP footer, hoặc info pack chưa được khách confirm mà đã đăng.

### EO-02 — Phân loại mô hình DN → chốt danh sách trang áp dụng

**Nguồn:** GIỮ — sheet "Tạo lập các Trang Entity cần th" bước 1.0: phân loại website cá nhân / DN nhỏ / thương hiệu lớn / ecommerce; benchmark đối thủ top cùng mô hình ("phải làm tối thiểu ngang ngửa hoặc hơn đối thủ").
**WHY:** [[Source Context]] — bộ trang entity phải phản ánh đúng mô hình kinh doanh thật; [[Knowledge-Based Trust]] — thị trường nào có trang trust đặc thù của thị trường đó (legacy ví dụ: tour du lịch cần "điều kiện hủy tour", nội thất/dịch vụ SEO cần "dự án đã triển khai").
**Check:**
- ✅ Có ghi nhận: mô hình DN + 2-3 đối thủ top cùng mô hình đã soi + danh sách trang entity áp dụng (từ 14 trang chuẩn ở EO-03, cộng trang đặc thù thị trường); trang không áp dụng ghi N/A + lý do.
- ❌ Fail: dùng nguyên danh sách 14 trang máy móc cho mọi site, không benchmark thị trường.

### EO-03 — Bảng tracking per trang đủ cột vận hành

**Nguồn:** GIỮ — sheet "Entity Onsite Checklist": cấu trúc cột Page / URL hiện tại / URL target / Action / Tham khảo / PIC / Link content / Deadline content / Note / Tiến độ update; 14 trang chuẩn: trang chủ, giới thiệu, founder, author 1-2, liên hệ, CS bảo mật, CS thanh toán, CS bảo hành, CS vận chuyển, CS đổi trả, tuyển dụng, dự án đã thi công, FAQ.
**WHY:** đầu vào trực tiếp cho EN-16 (bàn giao file quản lý) — người mới đọc bảng là chạy tiếp được.
**Check:**
- ✅ Mỗi trang trong danh sách áp dụng (EO-02) có 1 dòng, đủ cột, tiến độ cập nhật đúng thực tế; Action rõ (tạo mới / update / giữ nguyên).
- ❌ Fail: bảng chỉ có tên trang không có URL target/PIC/deadline — không vận hành được.

### EO-04 — Chuẩn kỹ thuật chung mọi trang entity

**Nguồn:** GIỮ+GỘP — bước "Triển khai đăng tải" lặp lại ở cả 3 sheet triển khai: tạo **page không phải post**; onpage cơ bản title/meta/URL/H1→H4 "như 1 URL SEO"; format cân đối chữ-ảnh-video; tối ưu tính năng page theo đối thủ (ngang bằng hoặc hơn).
**WHY:** [[Semantic HTML]] — trang entity vẫn là document Google đọc; heading hierarchy và onpage sạch giúp entity extraction.
**Check (áp cho TỪNG trang trước khi tick các nhóm B-H):**
- ✅ Là page (không nằm trong blog feed/category post); title + meta description + H1 định danh đúng trang; URL ngắn gọn có nghĩa; ảnh có alt mô tả (chèn brand/keyword tự nhiên, không nhồi); layout cân đối, không lỗi hiển thị mobile.
- ❌ Fail: trang chính sách tạo dạng post có ngày đăng + author box lẫn trong blog, hoặc trang không có H1.

---

## Nhóm B — Trang chủ (chi tiết hóa EN-02, EN-05, EN-06)

### EO-05 — Trang chủ định danh entity ngay màn hình đầu

**Nguồn:** MỚI — legacy chỉ liệt kê "Trang chủ" trong bảng tracking, không có tiêu chuẩn nội dung; bổ sung theo [[Entity Home]] (Koray: Zone/Point/Home) + [[Central Entity]].
**WHY:** trang chủ là bề mặt entity được crawl/link nhiều nhất — câu định danh "X là [type] cung cấp [dịch vụ] cho [đối tượng] tại [khu vực]" cho Google câu trả lời absolute-fact đầu tiên về entity ([[E-A-V Framework]]).
**Check:**
- ✅ Trong viewport đầu hoặc section giới thiệu đầu tiên có đoạn text (không phải chỉ trong ảnh/slider) nêu: brand name + entity type + sản phẩm/dịch vụ chính + đối tượng/khu vực phục vụ; khớp bio trong info pack.
- ❌ Fail: trang chủ chỉ có slogan cảm xúc ("Nâng tầm giá trị của bạn") — không câu nào nói công ty là gì, làm gì.

### EO-06 — NAP + định danh pháp lý hiển thị trên trang chủ

**Nguồn:** GIỮ — legacy audit "đồng nhất NAP Social, website, trang entity khác"; cụ thể hóa cho trang chủ (thường qua footer — check chi tiết ở EO-33).
**WHY:** [[Entity Identity Management]] — trang chủ là node được citation/social trỏ về nhiều nhất, NAP tại đây là bản NAP "đại diện" khi Google đối chiếu.
**Check:**
- ✅ Footer/khối liên hệ trang chủ hiển thị đúng tên ĐKKD + địa chỉ + phone + email theo info pack, dạng text crawlable.
- ❌ Fail: NAP chỉ nằm trong ảnh banner, hoặc trang chủ ghi số hotline khác trang liên hệ.

### EO-07 — Trang chủ liên kết tới bộ trang entity

**Nguồn:** MỚI — legacy không có; bổ sung theo nguyên tắc internal link + entity page discoverability.
**WHY:** trang entity không có inbound link từ trang chủ/footer = trust page mồ côi, giảm khả năng được associate với [[Central Entity]]; đồng thời là tín hiệu [[Knowledge-Based Trust]] cho user thật.
**Check:**
- ✅ Từ trang chủ (menu/footer) bấm tới được: giới thiệu, liên hệ, chính sách bảo mật (+ bộ chính sách ecommerce nếu có), tuyển dụng/dự án nếu áp dụng — toàn bộ là link `<a href>` crawlable, không bị noindex/nofollow nội bộ.
- ❌ Fail: trang giới thiệu tồn tại nhưng không link nào trên site trỏ tới (chỉ truy cập bằng URL trực tiếp).

### EO-08 — Schema trang chủ: Organization reference đúng, không nhân bản

**Nguồn:** SỬA — sheet "Tối ưu Schema" (template "Tại đây" đã chết) → thay bằng route skill `schema-markup-generator`; checklist chỉ check CÓ/ĐÚNG LOẠI.
**WHY:** [[Structured Data]] + [[Knowledge Graph]] — Organization đầy đủ chỉ khai báo 1 nơi (Entity Home `{domain}/#organization`), mọi trang khác reference qua `@id` để tránh conflicting claims.
**Check:**
- ✅ Trang chủ có WebSite + Organization **reference** (`@id` trỏ về Entity Home), KHÔNG lặp full Organization thứ hai với dữ liệu khác; sameAs (nếu xuất hiện) chỉ chứa profile thật từ info pack.
- ❌ Fail: trang chủ nhúng 1 bản Organization đầy đủ có địa chỉ khác bản ở trang giới thiệu.

---

## Nhóm C — Trang giới thiệu / About = Entity Home (chi tiết hóa EN-02)

### EO-09 — Chỉ định 1 URL Entity Home + canonical 🔒P0

**Nguồn:** MỚI — khái niệm [[Entity Home]] theo Koray, 2023 chưa có; legacy chỉ có "tối ưu trang giới thiệu".
**WHY:** [[Entity Home]] — Google cần 1 địa chỉ nhất quán để "về nhà" khi reconcile entity; mọi tín hiệu offsite (sameAs, citation, social) sẽ trỏ về URL này.
**Check:**
- ✅ Đã chốt bằng văn bản (trong bảng tracking EO-03): URL nào là Entity Home (mặc định = trang giới thiệu; site nhỏ = trang chủ); URL đó self-canonical, indexable, status 200, không có bản trùng (vd `/gioi-thieu/` và `/about/` cùng sống).
- ❌ Fail: không ai trả lời được "Entity Home của site này là URL nào", hoặc có 2 trang giới thiệu song song.

### EO-10 — Content Entity Home đủ E-A-V, không generic 🔒P0

**Nguồn:** GIỮ+NÂNG — sheet "Tối ưu trang giới thiệu" bước 1.0-2.0: sứ mệnh & tầm nhìn, tổng quan công ty, sản phẩm/dịch vụ chính, ban lãnh đạo & hình ảnh đội ngũ, video công ty (mẫu legacy: gtvseo.com/gioi-thieu, hubspot.com/our-story, hellobacsi.com/about-us). Nâng: từ "đủ mục + dài hơn đối thủ" → **đủ E-A-V theo chuẩn wiki**.
**WHY:** [[E-A-V Framework]] — entity được define bằng attribute-value cụ thể, không bằng tính từ; `sop/04-entity-optimization.md` mục EAV.
**Check (đối chiếu từng block):**
- ✅ Identity: tên đầy đủ + alias/tên viết tắt. ✅ Type: ngành/loại hình. ✅ Key attributes: năm thành lập, quy mô (nhân sự/chi nhánh), sản phẩm/dịch vụ chính, sứ mệnh & tầm nhìn. ✅ Relations: công ty mẹ/con, đối tác, membership. ✅ Authority signals: chứng nhận, giải thưởng, số liệu kết quả, khách hàng/dự án tiêu biểu. Mỗi attribute = câu khẳng định definitive có value cụ thể.
- ✅ Keyword dịch vụ chính chèn tự nhiên (legacy bước 2.0); độ dài ngang hoặc hơn đối thủ nhưng **tiêu chí chính là mật độ facts**, không phải word count.
- ❌ Fail: 3 đoạn "chúng tôi uy tín — tận tâm — chuyên nghiệp" không có con số/danh từ riêng nào; hoặc thông tin bịa để "cho đẹp hồ sơ".

### EO-11 — Ban lãnh đạo & đội ngũ: người thật + link tới trang person

**Nguồn:** GIỮ — block "Ban lãnh đạo & hình ảnh đội ngũ công ty" của sheet giới thiệu; nối với sheet "Tối ưu trang person".
**WHY:** [[Authorship]] — liên kết Organization ↔ Person là cạnh quan trọng trong entity graph; đội ngũ có tên là tín hiệu E-E-A-T.
**Check:**
- ✅ Section đội ngũ nêu tên thật + chức danh + ảnh thật; founder/người đại diện link tới trang person riêng (nhóm F).
- ❌ Fail: ảnh đội ngũ là stock photo, hoặc nêu "đội ngũ chuyên gia 10 năm kinh nghiệm" mà không có một cái tên nào.

### EO-12 — Hình ảnh / video công ty unique

**Nguồn:** GIỮ+SỬA — legacy yêu cầu "hình ảnh chất lượng, unique tương ứng cho từng phần, có video giới thiệu càng tốt". Sửa: legacy còn mở đường fake ảnh — nay **cấm tuyệt đối ảnh fake/stock giả danh công ty**.
**WHY:** ảnh unique verify được là bằng chứng first-hand cho [[Knowledge-Based Trust]]; ảnh stock bị reverse-search ra là tín hiệu ngược.
**Check:**
- ✅ Ảnh văn phòng/đội ngũ/hoạt động là ảnh thật của DN (reverse image search không ra site khác dùng trước); có video giới thiệu = điểm cộng, embed kèm mô tả text.
- ❌ Fail: ảnh "văn phòng" xuất hiện trên 40 website khác.

### EO-13 — Absolute facts: không mâu thuẫn cross-page

**Nguồn:** MỚI — 2023 chưa có; theo Pegasus/REALM principle (`CLAUDE.md` mục 9 + `sop/04` mục Responsiveness).
**WHY:** [[E-A-V Framework]] + [[Entity Identity Management]] — một attribute hai value (năm thành lập 2016 ở About, 2017 ở footer) làm giảm confidence của mọi claim còn lại.
**Check:**
- ✅ Grep/quét các facts lặp lại (năm thành lập, số nhân sự, số khách hàng, địa chỉ, tên pháp lý) trên: Entity Home, trang chủ, footer, trang person, schema — tất cả cùng 1 value; số liệu có mốc thời gian ("hơn 500 dự án tính đến 2026").
- ❌ Fail: bất kỳ cặp trang nào nêu 2 con số khác nhau cho cùng 1 attribute mà không có mốc thời gian giải thích.

### EO-14 — Onpage Entity Home: title/H1 định danh brand

**Nguồn:** GIỮ — bước "Triển khai đăng tải và tối ưu": onpage cơ bản như 1 URL SEO + tối ưu SEO hình ảnh (alt mô tả công ty, chèn keyword nếu tự nhiên — ví dụ legacy: "công ty SEO GTV").
**WHY:** Entity Home cũng cạnh tranh cho brand SERP (EN-15) — title/H1 chuẩn giúp chiếm top 1 brand query + sitelinks.
**Check:**
- ✅ Title dạng "Giới thiệu [Brand] — [định vị ngắn]"; H1 chứa brand name; meta description dùng bio chuẩn info pack; alt ảnh mô tả đúng nội dung + brand.
- ❌ Fail: title mặc định "About — Home", hoặc H1 là "Chào mừng".

---

## Nhóm D — Trang liên hệ (chi tiết hóa EN-03, EN-05)

### EO-15 — NAP đầy đủ dạng text crawlable, khớp info pack 🔒P0

**Nguồn:** GIỮ+NÂNG — legacy: trang liên hệ trong bộ 14 trang, mẫu gtvseo.com/lien-lac; audit NAP. Nâng: nêu rõ yêu cầu **text crawlable** (không chỉ nằm trong ảnh/JS render lỗi).
**WHY:** [[Entity Identity Management]] — trang liên hệ là bản NAP canonical onsite mà mọi citation offsite (EN-09) phải khớp về.
**Check:**
- ✅ Đủ: tên công ty đúng ĐKKD, địa chỉ đúng 1 cách viết chuẩn, phone (click-to-call `tel:`), email domain công ty, giờ làm việc; toàn bộ là HTML text, so khớp 100% với info pack (EO-01).
- ❌ Fail: mẫu lệch legacy từng bắt — web ghi "Số 15 Đông Quan", nơi khác ghi "Lô C4, 15 đường Đông Quan"; hoặc email liên hệ là gmail cá nhân.

### EO-16 — Map embed đúng địa điểm, khớp GBP

**Nguồn:** GIỮ+NÂNG — legacy sheet Schema bước 1.0 yêu cầu chuẩn bị "Maps". Nâng: map embed phải trỏ đúng **GBP listing của chính DN** (consistency với EN-10), không phải pin địa chỉ suông.
**WHY:** map embed từ GBP listing tạo liên kết tường minh website ↔ GBP — hai bề mặt của cùng entity trong [[Knowledge Graph]].
**Check:**
- ✅ Iframe Google Maps nhúng đúng listing GBP (hiện tên DN trên pin, không chỉ tọa độ); địa chỉ pin = địa chỉ text trên trang.
- ❌ Fail: map pin sang tòa nhà khác, hoặc nhúng listing cũ đã đổi địa chỉ. (Site không có địa điểm vật lý → N/A, ghi chú.)

### EO-17 — Form + kênh liên hệ hoạt động thật

**Nguồn:** GIỮ — legacy "tối ưu tính năng của page" + UX/UI; cụ thể hóa cho trang liên hệ.
**WHY:** [[Knowledge-Based Trust]] — trang liên hệ chết (form không gửi được) là trust signal âm cho cả user lẫn quality rater.
**Check:**
- ✅ Test gửi form thật → nhận được (email/CRM); phone bấm gọi được trên mobile; các kênh chat (Zalo/Messenger) nếu gắn thì hoạt động.
- ❌ Fail: form submit ra lỗi 500 hoặc không ai nhận.

### EO-18 — Schema trang liên hệ: ContactPage / LocalBusiness đúng loại

**Nguồn:** SỬA — legacy item "Schema person, local business, contactpage" (template chết) → route `schema-markup-generator`; đây chỉ check CÓ/ĐÚNG LOẠI.
**WHY:** [[Structured Data]] — ContactPage + contactPoint nối về Organization `@id` giúp máy đọc đúng vai trò trang.
**Check:**
- ✅ Có ContactPage (hoặc LocalBusiness nếu local) do skill sinh; NAP trong schema = EO-15; nối `@id` về Entity Home; validate pass (chi tiết graph check ở EO-36).
- ❌ Fail: trang liên hệ mang schema Article, hoặc LocalBusiness khai giờ mở cửa khác giờ ghi trên trang.

---

## Nhóm E — Trang chính sách — YMYL trust (chi tiết hóa EN-03)

### EO-19 — Đủ bộ chính sách theo mô hình DN 🔒P0 (ecommerce = bắt buộc)

**Nguồn:** GIỮ — bộ 5 trang chính sách trong sheet checklist (bảo mật, thanh toán, bảo hành, vận chuyển, đổi trả) + luật phân loại theo mô hình (sheet "Tạo lập..." — "tham khảo các trang ecommerce lớn").
**WHY:** [[Knowledge-Based Trust]] — bộ chính sách là tập absolute facts về cam kết giao dịch của entity; với site ecommerce/YMYL đây là tiêu chí trust tối thiểu.
**Check:**
- ✅ Mọi site: chính sách bảo mật. Ecommerce: + thanh toán, vận chuyển/giao hàng, đổi trả, bảo hành (nếu hàng có bảo hành). Dịch vụ: điều khoản dịch vụ. Thị trường đặc thù: trang theo benchmark EO-02 (vd điều kiện hủy tour).
- ✅ Trang không áp dụng → N/A + lý do trong bảng tracking; KHÔNG tạo trang rỗng cho đủ số.
- ❌ Fail: site bán hàng không có chính sách đổi trả, hoặc trang chính sách là placeholder "đang cập nhật".

### EO-20 — Nội dung chính sách thật, cụ thể theo vận hành DN

**Nguồn:** GIỮ+NÂNG — legacy: "thông tin phải chính xác hạn chế fake", "đối thủ 500 chữ mình tầm 700 chữ". Nâng: bỏ thước đo word count; tiêu chí = điều khoản cụ thể, khớp vận hành thật, không copy nguyên văn đối thủ.
**WHY:** chính sách copy-paste đổi tên brand = duplicate + conflicting claims (số hotline, thời hạn đổi trả của công ty khác) — phá [[Entity Identity Management]].
**Check:**
- ✅ Điều khoản có value cụ thể: số ngày đổi trả, điều kiện, phí, kênh tiếp nhận, SLA xử lý; tên công ty/hotline trong văn bản đúng info pack; khách đã confirm nội dung khớp vận hành thật.
- ❌ Fail: search 1 đoạn chính sách ra hàng chục site khác nguyên văn, hoặc chính sách ghi hotline của... template gốc.

### EO-21 — Chính sách link từ footer sitewide + indexable

**Nguồn:** MỚI — legacy không nêu; bổ sung theo thực hành trust page.
**WHY:** chính sách chỉ có giá trị trust khi tìm thấy được từ mọi trang (user đứng ở PDP phải thấy đường tới đổi trả); đồng thời crawlable để Google associate với entity.
**Check:**
- ✅ Footer sitewide link đủ bộ chính sách; các trang này indexable (không disallow/noindex trừ khi có quyết định riêng ghi chú), status 200.
- ❌ Fail: chính sách chỉ link từ trang thanh toán, hoặc bị noindex "cho sạch index" mà không có quyết định.

---

## Nhóm F — Author / Founder / đội ngũ (chi tiết hóa EN-04, EN-06)

### EO-22 — Founder + mỗi author có URL riêng dạng page

**Nguồn:** GIỮ — sheet checklist (trang founder, author 1, author 2) + sheet "Tối ưu trang person" (mẫu: gtvseo.com/vincent-do, hubspot.com/company/management, vinmec.com danh sách bác sĩ).
**WHY:** [[Authorship]] — author phải là entity có địa chỉ (URL) để Google gom tín hiệu; author box 2 dòng không đủ làm entity home cho Person.
**Check:**
- ✅ Founder/người đại diện + mỗi author đang viết bài có 1 page riêng (`/ten-nguoi/`), sống, indexable; số lượng author theo scope dự án (ghi trong bảng tracking).
- ❌ Fail: byline bài viết là plain text không link, hoặc author page là archive post rỗng tự sinh của CMS.

### EO-23 — Outline person đủ E-A-V nghề nghiệp (bỏ field nhạy cảm)

**Nguồn:** GIỮ+SỬA — legacy outline: tên, tuổi, giới tính, học tập, thành tựu, lĩnh vực chuyên môn, công ty, SĐT/email/địa chỉ sống. **SỬA:** bỏ tuổi/giới tính/địa chỉ sống/SĐT cá nhân (không có giá trị entity, rủi ro privacy); bỏ hoàn toàn hướng dẫn "trường hợp bắt buộc phải fake" — thông tin person **phải thật 100%**.
**WHY:** [[E-A-V Framework]] áp cho Person + [[Algorithmic Authorship]] — điều Google cần là credentials nghề nghiệp verify được, không phải hồ sơ nhân khẩu.
**Check:**
- ✅ Trang person đủ: tên đầy đủ, chức danh/vai trò tại công ty, lĩnh vực chuyên môn, quá trình học tập & chứng chỉ, thành tựu có value (số liệu, giải thưởng, đầu sách/talk), tổ chức trực thuộc; giọng định danh, không tự sự lan man.
- ❌ Fail: bio bịa thành tựu, hoặc chỉ có "chuyên gia nhiều năm kinh nghiệm" không dẫn chứng.

### EO-24 — Ảnh chân dung unique, verify bằng reverse image search

**Nguồn:** GIỮ+SỬA — legacy có quy trình verify ảnh qua Google Image search ("khi search phải ra không có website nào hoặc chỉ website bạn") — GIỮ quy trình verify. **SỬA:** legacy note gợi ý lấy ảnh ít view trên TikTok/Instagram/Pinterest làm profile fake — **CẤM**, chỉ dùng ảnh thật của đúng người.
**WHY:** ảnh person là tín hiệu định danh cross-platform ([[Entity Identity Management]]); ảnh đánh cắp bị reverse-search ra người khác phá toàn bộ trust chain và có rủi ro pháp lý.
**Check:**
- ✅ Reverse image search ảnh chân dung: chỉ ra site mình + các profile chính chủ; cùng 1 ảnh (hoặc bộ ảnh nhất quán) dùng cho social profiles (đồng bộ với EN-07).
- ❌ Fail: ảnh ra kết quả là người khác / kho stock.

### EO-25 — Entity link 2 chiều: byline ↔ trang author ↔ kho bài viết

**Nguồn:** GIỮ — legacy "Tối ưu Entity link": tạo danh mục/bài viết tác giả đã chia sẻ, mẫu gtvseo.com/vincent-do.
**WHY:** [[Authorship]] + [[Algorithmic Authorship]] — vòng khép byline → author page → danh sách bài → bài viết cho phép gom author signals về 1 entity.
**Check:**
- ✅ Byline mọi bài viết link về đúng trang author; trang author có block/danh mục "bài viết của [tên]" link ngược ra bài; author page link từ trang giới thiệu (EO-11).
- ❌ Fail: 2 author trùng tên dùng chung 1 URL, hoặc byline link về trang chủ.

### EO-26 — Person schema + sameAs cá nhân đúng loại

**Nguồn:** SỬA — legacy "tối ưu schema person theo format schema GTV" (format cũ đã bỏ) → route `schema-markup-generator` (Person + ProfilePage, `{author-url}/#person`); đây chỉ check CÓ/ĐÚNG LOẠI.
**WHY:** [[Structured Data]] — Person node có `worksFor` trỏ Organization `@id` + sameAs social cá nhân thật = cạnh Person↔Organization trong graph.
**Check:**
- ✅ Trang person có Person (+ ProfilePage) schema; `worksFor` nối đúng `#organization`; sameAs chỉ profile cá nhân thật; validate pass.
- ❌ Fail: Person schema khai `jobTitle` khác chức danh hiển thị trên trang.

### EO-27 — Site nhiều chuyên gia → trang danh sách đội ngũ

**Nguồn:** GIỮ — note đầu sheet person: site nhiều person/author (giáo dục, y tế…) nên có trang giới thiệu toàn bộ đội ngũ (mẫu legacy: vus.edu.vn teachers, vinmec.com danh sách bác sĩ, hubspot.com/company/management).
**WHY:** trang hub đội ngũ là listing page phân phối internal link + context cho từng Person entity; với thị trường YMYL gần như bắt buộc theo benchmark.
**Check:**
- ✅ Nếu site có ≥3 chuyên gia: tồn tại trang danh sách đội ngũ, mỗi người 1 card (ảnh + tên + chuyên môn) link về page riêng. Site 1-2 person → N/A.
- ❌ Fail: 10 bác sĩ có bio nhưng không có trang tổng, mỗi trang person mồ côi.

---

## Nhóm G — Trang đại lý / chi nhánh (chi tiết hóa EN-03, EN-05; local → EN-10)

### EO-28 — Trang hệ thống đại lý/chi nhánh với NAP per điểm

**Nguồn:** GIỮ — legacy "Tạo lập...": thương hiệu lớn cần "danh sách đại lý", "đăng kí làm đại lý"; chuẩn chấp nhận "trang danh sách đại lý phải có bản đồ và thể hiện vị trí đại lý".
**WHY:** mỗi chi nhánh là 1 sub-entity có NAP riêng; trang hệ thống là nơi khai báo tường minh quan hệ Organization ↔ các địa điểm ([[Entity Identity Management]]).
**Check:**
- ✅ Nếu DN có ≥2 điểm bán/chi nhánh: có trang hệ thống liệt kê từng điểm với tên điểm + địa chỉ + phone + giờ mở cửa (text crawlable) + map; chuỗi lớn → mỗi chi nhánh 1 trang con riêng. Không có chi nhánh → N/A.
- ❌ Fail: trang đại lý chỉ có ảnh chụp danh sách, hoặc số điện thoại các điểm lẫn lộn.

### EO-29 — Consistency chi nhánh ↔ GBP; local sâu → route `local-seo-audit`

**Nguồn:** MỚI — 2023 chưa có yêu cầu khớp GBP per điểm; bổ sung để nhất quán với EN-10.
**WHY:** mỗi điểm có GBP listing riêng — NAP onsite per điểm phải khớp listing tương ứng, nếu không mỗi chi nhánh tự tạo một mâu thuẫn NAP.
**Check:**
- ✅ Đối chiếu từng điểm: NAP onsite = NAP GBP listing của đúng điểm đó; trang chi nhánh link tới listing (hoặc embed map listing). Dự án nặng local → chuyển sang skill `local-seo-audit` chạy checklist GBP đầy đủ, ở đây chỉ tick consistency.
- ❌ Fail: GBP chi nhánh Quận 7 trỏ website về trang chủ trong khi có trang chi nhánh riêng, NAP lệch nhau.

---

## Nhóm H — Trust bổ trợ: tuyển dụng, dự án, FAQ (chi tiết hóa EN-03)

### EO-30 — Trang tuyển dụng với vị trí thật

**Nguồn:** GIỮ — trang "Tuyển dụng" trong bộ 14 trang + "một số vị trí điển hình" (mẫu legacy: gtvseo.com/tuyen-dung-gtvseo).
**WHY:** [[Knowledge-Based Trust]] — công ty thật thì tuyển người thật; trang tuyển dụng đồng thời là nguồn nội dung cho company profile trên job sites (EN-09).
**Check:**
- ✅ Trang tuyển dụng có mô tả môi trường làm việc + các vị trí (đang mở hoặc điển hình, ghi rõ trạng thái); thông tin liên hệ ứng tuyển đúng info pack; nội dung khớp company profile trên TopCV/job sites nếu có.
- ❌ Fail: trang tuyển dụng 404 hoặc tin tuyển từ 3 năm trước không trạng thái.

### EO-31 — Trang dự án đã thi công / portfolio với bằng chứng thật

**Nguồn:** GIỮ — legacy nhấn mạnh: trang "dự án đã triển khai/project portfolio" quan trọng với thị trường dịch vụ/nội thất — "đăng nội dung không cần SEO nhưng phải có ảnh unique thực tế, content unique" — vừa tăng chuyển đổi vừa thiết lập entity.
**WHY:** portfolio = tập evidence first-hand cho authority claims ở Entity Home ([[Knowledge-Based Trust]]); claim "500+ dự án" ở About phải có trang này chống lưng.
**Check:**
- ✅ Ngành dịch vụ/thi công/agency: có trang dự án, mỗi dự án có ảnh thật (không stock), thông tin cụ thể (hạng mục, thời gian, kết quả; tên khách nếu được phép); con số tổng khớp claim ở EO-10. Ngành không áp dụng → N/A.
- ❌ Fail: portfolio dùng ảnh render/stock gắn logo, hoặc case không có thông tin kiểm chứng nào.

### EO-32 — Trang FAQ về brand/dịch vụ, answer-first

**Nguồn:** GIỮ+NÂNG — trang "Câu hỏi thường gặp" trong bộ 14 trang. Nâng: câu trả lời theo chuẩn answer-first 40-60 từ (đồng bộ chuẩn FAQ của hệ checklist content); lưu ý FAQ rich result đã chấm dứt 05/2026 — **không hứa rich result**, giá trị là coverage câu hỏi brand.
**WHY:** [[Source Context]] — FAQ brand cover các query "brand + giá/địa chỉ/có uy tín không" giúp site tự trả lời brand SERP (nối EN-15); từng answer là absolute fact về entity.
**Check:**
- ✅ FAQ gom câu hỏi thật (từ sales/support/PAA brand query); mỗi answer trả lời thẳng trong 1-2 câu đầu, facts khớp info pack + chính sách.
- ❌ Fail: FAQ 5 câu tự bịa dạng "Vì sao chọn chúng tôi?" trả lời quảng cáo, không có câu hỏi thật nào của user.

---

## Nhóm I — Footer / sitewide (chi tiết hóa EN-05)

### EO-33 — NAP footer đồng nhất 100% mọi template 🔒P0

**Nguồn:** GIỮ — audit "đồng nhất NAP Social, website, trang entity khác"; cụ thể hóa cho footer sitewide.
**WHY:** footer xuất hiện trên mọi URL — đây là bản NAP được crawl lặp lại nhiều nhất; footer lệch = mâu thuẫn nhân bản ra toàn site ([[Entity Identity Management]]).
**Check:**
- ✅ Kiểm footer trên đủ các template (trang chủ, page, post, category, landing builder riêng): tên + địa chỉ + phone + email cùng 1 value, cùng 1 cách viết, khớp info pack; đổi NAP → checklist redeploy mọi template.
- ❌ Fail: landing page dựng bằng builder khác còn giữ footer NAP cũ.

### EO-34 — Social icons footer → đúng profile thật trong sameAs set

**Nguồn:** GIỮ+NÂNG — legacy có audit NAP social; nâng: footer social links phải = danh sách sameAs trong schema = danh sách profile thật của info pack (3 nguồn 1 bộ).
**WHY:** liên kết web → social là tín hiệu 2 chiều xác nhận profile chính chủ, cùng bộ với sameAs graph ([[Knowledge Graph]], nối EN-07).
**Check:**
- ✅ Mọi icon social ở footer/header trỏ đúng profile brand đang hoạt động (không 404, không profile bỏ hoang trống); bộ link này khớp sameAs trong Organization schema.
- ❌ Fail: icon YouTube trỏ về kênh chưa tạo, hoặc footer link Facebook cá nhân của nhân viên cũ.

### EO-35 — Định danh pháp lý sitewide (ĐKKD, MST, đăng ký BCT)

**Nguồn:** MỚI — legacy chỉ có NAP; bổ sung theo chuẩn trust ecommerce VN hiện hành.
**WHY:** [[Knowledge-Based Trust]] — số ĐKKD/MST là attribute định danh mạnh nhất (unique, verify được qua cổng quốc gia); với ecommerce VN, logo "Đã thông báo Bộ Công Thương" là chuẩn thị trường.
**Check:**
- ✅ Footer ghi: tên pháp lý đầy đủ + số ĐKKD/MST + nơi cấp; site ecommerce VN đã đăng ký/thông báo Bộ Công Thương → gắn logo link tới hồ sơ trên online.gov.vn. Không thuộc diện → N/A ghi chú.
- ❌ Fail: gắn logo BCT nhưng link chết hoặc chưa đăng ký (đây là fail nặng — fake trust signal).

---

## Nhóm J — Schema tầng site (chi tiết hóa EN-06)

### EO-36 — Schema graph tầng site: CÓ + ĐÚNG LOẠI + @id nối đúng 🔒P0

**Nguồn:** SỬA TOÀN BỘ — sheet "Tối ưu Schema" legacy (template Organization/Author dạng link "Tại đây" đã chết + format schema GTV cũ). Thay bằng: **route skill `schema-markup-generator`** sinh JSON-LD; checklist này KHÔNG viết schema, chỉ verify deliverable đã deploy.
**WHY:** [[Structured Data]] + [[Knowledge Graph]] — schema là kênh khai báo E-A-V machine-readable; giá trị = rich results + entity understanding. ⚠ Guardrail của skill: **schema ≠ AI-citation lever** (DiD Ahrefs) — không hứa với khách schema làm tăng AI citations.
**Check (per page type, tick CÓ/ĐÚNG LOẠI):**
- ✅ Entity Home: Organization ĐẦY ĐỦ duy nhất (`{domain}/#organization`) — NAP = info pack, sameAs = bộ profile thật (EO-34), KHÔNG bịa Wikipedia/Wikidata QID.
- ✅ Trang chủ: WebSite + Organization reference `@id` (EO-08). Trang liên hệ: ContactPage/LocalBusiness (EO-18). Trang person: Person + ProfilePage, `worksFor` → `#organization` (EO-26). Chi nhánh: LocalBusiness per điểm `parentOrganization` → `#organization` (nếu áp dụng).
- ✅ Toàn bộ validate pass (Rich Results Test / Schema validator, không lỗi required field); mọi giá trị trong schema khớp visible content 1:1; không trang nào nhân bản Organization đầy đủ thứ hai.
- ❌ Fail: 2 Organization đầy đủ khác nhau trên site; sameAs chứa profile chưa tạo; schema khai địa chỉ khác trang hiển thị. (Lỗi legacy phổ biến: "khai báo chưa đúng @id" — đây là điểm check chính.)

---

## Bảng map: sheet legacy → nhóm mới

| Sheet legacy (GTV xlsx) | Nội dung chính | → Nhóm mới |
|---|---|---|
| Entity Onsite Checklist | Bảng tracking 14 trang (cột Page/URL/Action/PIC/Deadline/Tiến độ) | Nhóm A (EO-02, EO-03) — cấu trúc bảng giữ nguyên làm file vận hành; 14 trang phân bổ vào nhóm B-H |
| Tạo lập các Trang Entity cần th | Phân loại mô hình DN, benchmark đối thủ, chuẩn bị info, đăng page + onpage + format | Nhóm A (EO-01, EO-02, EO-04) + Nhóm E (EO-19, EO-20) + Nhóm G (EO-28) + Nhóm H (EO-30, EO-31) |
| Tối ưu trang giới thiệu | Sứ mệnh/tầm nhìn/ban lãnh đạo/ảnh video, onpage, format | Nhóm C (EO-10, EO-11, EO-12, EO-14) — nâng cấp thành Entity Home E-A-V (EO-09, EO-13 mới) |
| Tối ưu trang person | Outline person, ảnh unique verify, entity link, schema person | Nhóm F (EO-22…EO-27) |
| Triển khai IFTTT | RSS → IFTTT → social syndication | **KHÔNG thuộc file này** — syndication là hạng mục offsite, đã xử lý ở tier-1-entity **EN-11/EN-12** (giữ tactic, bỏ IFTTT/Zapier làm tool) |
| Tối ưu Schema | Template Organization/Author "Tại đây" + item person/localbusiness/contactpage | Nhóm J (EO-36) + EO-08/EO-18/EO-26 — template cũ bỏ toàn bộ, route `schema-markup-generator` |

## Delta — bỏ / thêm / sửa so với legacy (và vì sao)

**BỎ:**
1. **Sheet "Triển khai IFTTT" ra khỏi phạm vi onsite** — syndication là offsite (EN-11/EN-12); riêng IFTTT/Zapier bị bỏ với tư cách tool theo chỉ đạo Vincent 07/2026 (tactic syndication vẫn giữ, bằng manual/n8n/native scheduler).
2. **Toàn bộ template schema cũ** ("Tại đây", "format schema GTV") — link chết + chuẩn cũ; thay bằng route skill `schema-markup-generator`, checklist chỉ verify CÓ/ĐÚNG LOẠI/@id graph.
3. **Mọi hướng dẫn fake** — legacy cho phép "hạn chế fake", "trường hợp bắt buộc phải fake thì làm content unique", gợi ý lấy ảnh ít view trên TikTok/Pinterest làm profile: nay **cấm tuyệt đối** (thông tin + ảnh phải thật 100%) — fake định danh phá Knowledge-Based Trust, rủi ro pháp lý, và dễ bị reverse-search bắt.
4. **Field person nhạy cảm** (tuổi, giới tính, địa chỉ sống, SĐT cá nhân) — không có giá trị entity nghề nghiệp, rủi ro privacy.
5. **Thước đo word count** ("đối thủ 500 chữ mình 700 chữ") — thay bằng mật độ facts E-A-V + benchmark coverage.

**THÊM (2023 chưa có):**
1. **Entity Home theo Koray** (EO-09) — chỉ định 1 URL canonical làm nhà của Central Entity; legacy chỉ có "tối ưu trang giới thiệu" như một trang đơn lẻ.
2. **Absolute facts cross-page** (EO-13) — quét mâu thuẫn số liệu giữa các trang (Pegasus/REALM).
3. **sameAs graph 3-nguồn-1-bộ** (EO-34 + EO-36) — footer links = sameAs schema = info pack.
4. **Consistency với GBP** (EO-16, EO-29) — map embed đúng listing, NAP per chi nhánh khớp GBP; local sâu route `local-seo-audit`.
5. **Định danh pháp lý sitewide** (EO-35) — ĐKKD/MST/đăng ký Bộ Công Thương.
6. **Trang chủ định danh entity** (EO-05) + liên kết bộ trang entity (EO-07, EO-21) — chống trust page mồ côi.
7. **P0 gate 7 items** + map từng item về EN-xx — legacy không có cơ chế gate.

**SỬA:**
1. FAQ: giữ trang, thêm chuẩn answer-first; ghi rõ FAQ rich result đã chấm dứt (05/2026) — không hứa rich result.
2. Ảnh person: giữ quy trình verify reverse image search của legacy (điểm mạnh hiếm có của bản gốc), nhưng đảo mục đích — từ "kiểm tra ảnh fake đủ an toàn" thành "chứng minh ảnh thật chính chủ".
3. Schema guardrail: bổ sung cảnh báo schema ≠ AI-citation lever (DiD Ahrefs) khi trao đổi với khách.
