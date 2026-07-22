---
type: sop
tier: 1
phase: entity
last_updated: 2026-07-19
source_file:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Checklist triển khai - Entity.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình Entity Onsite Web - GTV SEO.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình Social Entity - GTV SEO.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/@id loop page/@id loop page & 301 Redirect spam- quy trình.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình triển khai Syndication Content - IFTTT - Zappier.docx
items_count: 16
tags: [sop, tier-1, entity, self-checklist, quality-gate]
---

# Tier 1 — Self-Checklist: Entity (Onsite + Offsite)

> **Khi dùng:** Người làm entity (SEO Executive/Technician) tự check ở **công đoạn 13**. Hai mốc gate: **cuối T1** (nhóm Onsite + chuẩn bị) và **cuối T3** (nhóm Offsite + Verify).
> **Số items:** 16 (EN-01…EN-16) = 6 Onsite + 4 Offsite + 2 Syndication + 2 Tactic-có-gate + 2 Verify.
> **Scoring:** Self Score /16 → Self %. Cơ chế 3-level review giống README (Self → SEO EX Verify → Lead random 25-30%).
> **Chỉ đạo Vincent (07/2026):** GIỮ syndication, social stacking, @id loop, 301 redirect trong checklist — không xóa như "grey-hat". Chỉ bỏ **IFTTT/Zapier với tư cách tool** (syndication vẫn làm, bằng manual/n8n/tool hiện hành). Tactic rủi ro cao giữ item nhưng gắn gate **⚠ SEO Lead/Director duyệt trước khi chạy**.

## P0 Gate — 6 items PHẢI pass

| Mốc | Items | Điều kiện |
|---|---|---|
| **Cuối T1** | EN-01, EN-02, EN-05, EN-06 | Fail bất kỳ item nào → chưa được chuyển sang offsite/T2 |
| **Cuối T3** | EN-13/EN-14 (gate compliance — nếu có triển khai), EN-15 | Tactic gate chạy mà KHÔNG có approval = vi phạm quy trình, dừng ngay; EN-15 fail → lập kế hoạch bổ sung entity signals trước khi close công đoạn 13 |

## Map item → wiki concept

| ID | Label | Wiki ref |
|---|---|---|
| EN-01 | Brand Info Pack & Entity Audit | [[Central Entity]] + [[Entity Identity Management]] |
| EN-02 | Entity Home (trang chủ + giới thiệu) | [[Entity Home]] + [[E-A-V Framework]] |
| EN-03 | Bộ trang entity cần thiết | [[Entity Home]] + [[Knowledge-Based Trust]] |
| EN-04 | Trang Author / Founder (Person) | [[Authorship]] + [[Algorithmic Authorship]] |
| EN-05 | NAP Consistency | [[Entity Identity Management]] + [[Brand Identity]] |
| EN-06 | Schema Organization / Person / @id graph | [[Structured Data]] + [[Knowledge Graph]] |
| EN-07 | Social Profiles đồng bộ | [[Brand Entitization Playbook]] |
| EN-08 | Google Stack brand | [[Brand Entitization Playbook]] |
| EN-09 | Xác thực doanh nghiệp (directory/citation VN) | [[Knowledge-Based Trust]] |
| EN-10 | GBP Optimization (nếu local) | [[Entity Home]] (local surface) |
| EN-11 | Content Syndication (không IFTTT/Zapier) | [[Brand Entitization Playbook]] + [[Source Context]] |
| EN-12 | Index & Maintain syndication | [[Web Entity]] |
| EN-13 | ⚠ @id loop page (gated) | [[Structured Data]] |
| EN-14 | ⚠ 301 redirect spam (gated) | [[Web Entity]] |
| EN-15 | Verify entity recognition | [[Knowledge Graph]] + [[Entity Salience]] |
| EN-16 | Tracking & bàn giao file quản lý | [[Entity Identity Management]] |

---

## Nhóm A — Entity Onsite (gate cuối T1)

### EN-01 — Brand Info Pack & Entity Audit 🔒P0-T1

**Nhóm:** Onsite — chuẩn bị
**Nguồn legacy:** GIỮ+GỘP — `Checklist triển khai - Entity.xlsx` (Audit: chuẩn bị thông tin, audit NAP, kiểm tra cạnh tranh/nhận diện thương hiệu) + block info sheet "Social stack brand".

**Tóm tắt:** Trước khi tối ưu bất kỳ trang nào, phải có 1 file Brand Info Pack duy nhất làm source of truth cho mọi kênh: tên công ty đúng ĐKKD, tên thương hiệu, mã số thuế, địa chỉ, zipcode, phone, email, ngày thành lập, map embed, logo 500×500, background 1200×800, bio ngắn (<200 ký tự), bio dài (<1000 ký tự), username convention, hashtag set. Đồng thời audit hiện trạng: NAP đang lệch ở đâu (web / GBP / social / directory), thương hiệu có bị cạnh tranh tên (brand SERP có đối thủ/entity trùng tên) không.

**Chuẩn đạt:**
- ✅ File info pack đầy đủ field trên, thông tin THẬT (legacy note: "hạn chế fake" — nay là bắt buộc chính xác, không fake), khách đã confirm.
- ✅ Có bảng audit chênh lệch NAP hiện trạng + hướng xử lý per kênh.
- ❌ Mỗi người giữ một bản info riêng, bio mỗi kênh một kiểu → fail.

### EN-02 — Entity Home: trang chủ + trang giới thiệu 🔒P0-T1

**Nhóm:** Onsite
**Nguồn legacy:** GIỮ+NÂNG — sheet "Tối ưu trang giới thiệu" (`Quy trình Entity Onsite Web`): sứ mệnh, tầm nhìn, ban lãnh đạo, hình ảnh/video công ty, sản phẩm/dịch vụ chính. Nâng: content phải đủ E-A-V theo chuẩn wiki, không chỉ "dài hơn đối thủ 200 chữ".

**Tóm tắt:** Website phải có 1 URL được chỉ định là [[Entity Home]] cho Central Entity (thường là trang giới thiệu; site nhỏ → trang chủ). Content trang này define entity bằng E-A-V đầy đủ: Identity (tên đầy đủ, alias), Type/category, Key attributes (ngành, sản phẩm/dịch vụ chính, năm thành lập, quy mô), Relations (công ty mẹ/con, đối tác), Authority signals (chứng nhận, giải thưởng, dự án/khách hàng tiêu biểu). Mỗi attribute có câu trả lời definitive — không nước đôi, không conflict giữa các trang (REALM principle, theo `sop/04-entity-optimization.md`).

**Chuẩn đạt:**
- ✅ Trang giới thiệu đủ các block: sứ mệnh & tầm nhìn, tổng quan công ty, sản phẩm/dịch vụ chính, ban lãnh đạo & đội ngũ, hình ảnh unique (không stock), keyword dịch vụ chính được chèn tự nhiên; onpage cơ bản (title/meta/H1-H4) như một URL SEO; tạo dạng page không phải post.
- ✅ URL Entity Home là canonical, mọi schema Organization trên site reference về nó (xem EN-06).
- ❌ Trang giới thiệu 3 đoạn generic "công ty chúng tôi uy tín hàng đầu", không có attribute cụ thể nào → fail.

### EN-03 — Bộ trang entity cần thiết theo mô hình doanh nghiệp

**Nhóm:** Onsite
**Nguồn legacy:** GIỮ — sheet "Entity Onsite Checklist" (14 trang: trang chủ, giới thiệu, founder, author 1-2, liên hệ, chính sách bảo mật/thanh toán/bảo hành/vận chuyển/đổi trả, tuyển dụng, dự án đã thi công, FAQ) + sheet "Tạo lập các Trang Entity cần thiết".

**Tóm tắt:** Phân loại mô hình doanh nghiệp (cá nhân / SME / ecommerce / dịch vụ / chuỗi có đại lý) rồi tạo đủ bộ trang trust tương ứng. Ecommerce: chính sách mua hàng, đổi trả, giao hàng, bảo hành, thanh toán. Dịch vụ: liên hệ, đăng ký dịch vụ, dự án đã thi công. Có hệ thống đại lý/chi nhánh → trang đại lý/hệ thống cửa hàng với NAP per điểm. Mỗi thị trường có trang đặc thù riêng (vd tour du lịch cần trang giấy phép lữ hành) — benchmark theo đối thủ top và mô hình tương đồng.

**Chuẩn đạt:**
- ✅ Bảng tracking đủ cột Page / URL hiện tại / URL target / Action / PIC / Deadline / Tiến độ cho toàn bộ trang trong danh sách áp dụng; trang nào không áp dụng ghi rõ N/A + lý do.
- ✅ Mỗi trang: content chính xác (không fake), tối ưu onpage cơ bản, format cân đối, là page không phải post.
- ❌ Thiếu trang chính sách với site ecommerce, hoặc trang liên hệ không có NAP/map → fail.

### EN-04 — Trang Author / Founder (Person)

**Nhóm:** Onsite
**Nguồn legacy:** GIỮ+NÂNG — sheet "Tối ưu trang person": outline tên, học vấn, thành tựu, lĩnh vực chuyên môn, công ty; ảnh unique (verify bằng Google Image search); entity link về danh mục bài đã viết. Nâng: gắn chuẩn [[Authorship]] hiện hành (author bio + byline nhất quán cross-site).

**Tóm tắt:** Founder + mỗi author có trang riêng dạng page: đầy đủ E-A-V cá nhân (tên, chuyên môn, quá trình, thành tựu, tổ chức trực thuộc), ảnh chân dung unique, link tới danh sách bài viết của author trên site (mẫu: `gtvseo.com/vincent-do/`), sameAs về social cá nhân. Tùy quy mô site — site lớn nhiều giảng viên/chuyên gia thì làm trang danh sách đội ngũ + trang per person.

**Chuẩn đạt:**
- ✅ Trang person đứng được như một entity page độc lập; byline bài viết link về đúng trang này; Person schema (EN-06).
- ❌ Author chỉ có box 2 dòng cuối bài, không có URL riêng → fail (trừ khi scope dự án đã loại author entity — ghi note).

### EN-05 — NAP Consistency toàn hệ thống 🔒P0-T1

**Nhóm:** Onsite (kiểm cả offsite khi đến T3)
**Nguồn legacy:** GIỮ — "Audit đồng nhất NAP Social, website, trang entity khác" (`Checklist triển khai - Entity.xlsx`).

**Tóm tắt:** Name / Address / Phone (+ email, website) đồng nhất tuyệt đối theo Brand Info Pack (EN-01) trên: footer site, trang liên hệ, trang đại lý, schema, GBP, mọi social profile, mọi directory. Một cách viết địa chỉ duy nhất (thống nhất viết tắt, dấu câu). Đổi NAP → cập nhật đồng loạt, không để version cũ sống rải rác.

**Chuẩn đạt:**
- ✅ Checklist đối chiếu NAP per kênh = 100% khớp info pack; sai lệch được ghi ticket xử lý trước khi tick.
- ❌ Web ghi "Số 15 Đông Quan" còn GBP ghi "Lô C4, 15 đường Đông Quan" → fail (đây đúng là loại lệch legacy audit từng bắt).

### EN-06 — Schema Organization / Person / Entity Home 🔒P0-T1

**Nhóm:** Onsite
**Nguồn legacy:** SỬA — sheet "Tối ưu Schema" (template Organization/Author cũ dạng "Tại đây") + item "Schema person, local business, contactpage". Thay toàn bộ template cũ bằng route sang skill hiện hành.

**Tóm tắt:** KHÔNG tự viết schema theo template legacy. Route sang skill **`schema-markup-generator`**: Organization đầy đủ đặt tại Entity Home (`{domain}/#organization`), mọi trang khác chỉ reference qua `@id`; Person + ProfilePage cho author (`{author-url}/#person`); LocalBusiness nếu local; sameAs chỉ chứa profile THẬT đã verify (không bịa Wikipedia/Wikidata QID). Checklist này chỉ verify **deliverable đã deploy**: block tồn tại, validate pass, khớp visible content 1:1, `@id` graph nối đúng.

**Chuẩn đạt:**
- ✅ Rich Results Test / Schema validator pass, không lỗi required field; Organization đầy đủ CHỈ ở Entity Home; NAP trong schema = EN-01.
- ✅ ⚠ Ghi nhớ guardrail của skill: schema ≠ AI-citation lever — giá trị là rich results + entity understanding/Knowledge Graph. Không hứa với khách quá mức.
- ❌ Mỗi trang nhân bản một Organization đầy đủ khác nhau, sameAs chứa profile chưa tạo → fail.

---

## Nhóm B — Entity Offsite (gate cuối T3)

### EN-07 — Social Profiles đồng bộ brand info

**Nhóm:** Offsite
**Nguồn legacy:** GIỮ+SỬA — `Quy trình Social Entity - GTV SEO.xlsx` (tạo lập & tối ưu NAP, đăng logo + tối thiểu 2 hình, dùng hết tính năng setting, stacking). Sửa: bỏ định mức "tối thiểu 200 social" — chạy theo tier platform của checklist SGS; social stacking GIỮ theo chỉ đạo Vincent.

**Tóm tắt:** Triển khai bộ social profile brand (+ author/CEO nếu scope) theo checklist chi tiết **`tier-1-social-google-stack.md`** (SGS-01…SGS-13): platform theo tier, chuẩn profile per platform, cross-link/stacking, link về Entity Home. Item này là con trỏ tổng — tick khi bộ SGS đạt P0 của nó.

**Chuẩn đạt:** ✅ Checklist SGS pass toàn bộ P0; file quản lý profile bàn giao đủ. ❌ Chỉ tạo tài khoản rồi bỏ trống bio/không stack → fail.

### EN-08 — Google Stack brand

**Nhóm:** Offsite
**Nguồn legacy:** GIỮ — "Google stack brand" (`Checklist triển khai - Entity.xlsx`, Tháng 3) + phần GG stack trong quy trình @id loop. Chi tiết triển khai ở SGS-08…SGS-10.

**Tóm tắt:** Bộ tài sản Google (Sites, Docs, Sheets, Slides, My Maps, YouTube, Drive folder public) mang brand info nhất quán, liên kết chéo với nhau + embed lẫn nhau, link về Entity Home. Đây là lớp tài sản Google-owned củng cố entity recognition — theo dõi chi tiết ở checklist SGS.

**Chuẩn đạt:** ✅ Stack đủ tài sản theo SGS, cross-link 2 chiều, index được (SGS-12). ❌ Tạo Google Site 1 trang trống không link gì → fail.

### EN-09 — Xác thực doanh nghiệp (directory / citation VN)

**Nhóm:** Offsite
**Nguồn legacy:** GIỮ+CHẮT LỌC — sheet "Xác thực doanh nghiệp" (`Phân loại Social - Social Stack - bản PSP.xlsx`): trang vàng (trangvangvietnam, yellowpages.vn…), job sites (topcv, careerbuilder, vieclam24h…). Chắt lọc: chỉ giữ directory còn sống, có trang doanh nghiệp public.

**Tóm tắt:** Đăng ký hồ sơ doanh nghiệp trên các directory xác thực: nhóm trang vàng/danh bạ doanh nghiệp + nhóm tuyển dụng (hồ sơ company page — đồng thời phục vụ trang tuyển dụng EN-03). NAP đúng info pack, mô tả dùng bio chuẩn, link về website.

**Chuẩn đạt:** ✅ Tối thiểu 5-10 citation sống, đúng NAP, có link; ghi vào file quản lý. ❌ Đăng 30 directory chết/không duyệt hồ sơ → không tính.

### EN-10 — GBP Optimization (nếu doanh nghiệp local)

**Nhóm:** Offsite
**Nguồn legacy:** SỬA — "Audit GMB" + "Tối ưu GMB" + sheet "Tối ưu GMB" (`GMB Post Silo.xlsx`). Không duplicate nội dung: reuse checklist hiện hành.

**Tóm tắt:** Doanh nghiệp có địa điểm/khu vực phục vụ → chạy GBP theo checklist chuẩn của skill **`local-seo-audit`** (`references/gbp-checklist.md`): categories, attributes, mô tả ≤750 ký tự (250 đầu chứa Central Entity + dịch vụ + khu vực), photos, posts cadence, Q&A seeding, products/services, booking links, cross-branch consistency nếu chuỗi. GMB Post thường + Post Silo (mô phỏng internal link) xử lý ở SGS-11.

**Chuẩn đạt:** ✅ GBP checklist pass các mục áp dụng; không local → ghi N/A. ❌ GBP tồn tại nhưng category sai/mô tả trống → fail.

---

## Nhóm C — Syndication (GIỮ theo chỉ đạo — không IFTTT/Zapier)

### EN-11 — Content Syndication từ moneysite

**Nhóm:** Syndication
**Nguồn legacy:** GIỮ+SỬA TOOL — `Quy trình triển khai Syndication Content - IFTTT - Zappier.docx` + sheet "Triển khai IFTTT". **Giữ nguyên tactic syndication** (phân phối content moneysite → social, trích nguồn về bài gốc). **Bỏ IFTTT/Zapier với tư cách tool** (nền tảng cũ, applet không còn tin cậy) — thay bằng manual repost / n8n workflow / native scheduler (Meta Business Suite, LinkedIn schedule, Buffer-class tool hiện hành).

**Tóm tắt:** Thiết lập luồng syndication: (1) nguồn = RSS feed moneysite (verify feed sống) hoặc queue bài thủ công; (2) đích = social profiles đã lập ở SGS (ưu tiên platform cho đăng full content: Medium, LinkedIn Article, Tumblr, Blogger, WordPress.com); (3) mỗi bản sao PHẢI trích dẫn nguồn/link canonical về bài gốc trên moneysite; (4) share cả video YouTube và tài sản Google Stack lên social (giữ mô hình 4 phần của quy trình cũ); (5) tier-2 syndication chỉ cho URL quan trọng.

**Chuẩn đạt:**
- ✅ Luồng chạy được lặp lại (documented: ai đăng, kênh nào, tool gì, tần suất); bản sao có canonical/trích nguồn; không duplicate-spam (chọn lọc bài, không bơm 100% feed lên mọi kênh).
- ❌ Setup IFTTT/Zapier theo tài liệu cũ → fail item (sai tool). ❌ Syndication không dẫn nguồn về bài gốc → fail.

### EN-12 — Index & maintain bản syndication

**Nhóm:** Syndication
**Nguồn legacy:** GIỮ+SỬA — giai đoạn 3-4 của quy trình syndication (stack bản sao + index bằng blog comment/lazindex). Sửa: bỏ blog-comment-spam làm phương pháp index mặc định — dùng phương pháp index hiện hành của mục `11. Các phương pháp index link`; stacking bản sao chỉ cho URL quan trọng.

**Tóm tắt:** Bản syndication không index = công sức bỏ đi. Kiểm index các bản sao trên kênh quan trọng; kênh khó index (tham chiếu sheet "khó index" legacy) chấp nhận bỏ qua hoặc dùng cách index hiện hành. Duy trì social hoạt động đều nhờ luồng syndication (điểm cộng entity: profile "sống").

**Chuẩn đạt:** ✅ Có bảng theo dõi index status per kênh chính; tỷ lệ index kênh ưu tiên ≥ mức Lead chốt cho dự án. ❌ Không ai biết bản sao có index hay không → fail.

---

## Nhóm D — Tactic rủi ro cao — ⚠ GATE: SEO Lead/Director duyệt TRƯỚC khi chạy

> Hai item dưới GIỮ trong quy trình theo chỉ đạo Vincent, nhưng là tactic thao túng tín hiệu có rủi ro penalty. **Điều kiện chung để được duyệt:** (1) site KHÔNG phải YMYL/client rủi ro pháp lý cao; (2) đã hết lever an toàn (content, internal link, entity chuẩn) cho URL target; (3) có văn bản approval của SEO Lead/Director ghi rõ URL, phạm vi, thời hạn theo dõi, điều kiện rollback; (4) không chạy trên tài sản chính của client khi hợp đồng không cho phép tactic này. Chạy không có approval = vi phạm P0-T3.

### EN-13 — ⚠ @id loop page 🔒P0-T3 (gate compliance)

**Nhóm:** Tactic gated
**Nguồn legacy:** GIỮ+GATE — `@id loop page & 301 Redirect spam- quy trình.xlsx` (sheet "File Tiêu chuẩn @id loop"): hoàn thành GG stack trước; tạo page slug `url-target-1`, noindex+follow, canonical về URL target, nhúng iframe vòng 1-2 GG stack + Buffer Page + Umbrella Cloudstack; iframe looping trên web 2.0 DR/DA >85 với schema copy từ page @id loop.

**Tóm tắt:** Triển khai đúng file tiêu chuẩn legacy khi VÀ CHỈ KHI có approval theo gate ở trên. Yêu cầu kỹ thuật giữ nguyên: GG stack cho URL target xong trước (tối thiểu 2 vòng nếu gấp); trang @id loop noindex+follow + canonical đúng; `@id` trong schema khai báo đúng (lỗi phổ biến legacy: "khai báo chưa đúng @id"). Phần "bắn link GSA" của quy trình cũ: **mặc định KHÔNG chạy** — muốn chạy phải nằm rõ trong văn bản approval (rủi ro cao nhất chuỗi này).

**Chuẩn đạt:** ✅ Approval tồn tại + đúng file tiêu chuẩn + có tracking thứ hạng trước/sau và điều kiện rollback. ❌ Chạy "cho đủ quy trình" trên mọi URL, không approval → fail P0, dừng và báo cáo.

### EN-14 — ⚠ 301 redirect spam 🔒P0-T3 (gate compliance)

**Nhóm:** Tactic gated
**Nguồn legacy:** GIỮ+GATE — sheet "301 redirect spam" cùng file: iframe looping noindex+follow nhúng GG stack vòng 1-2, tài sản DR/DA >85, GSA link bẩn bắn vào URL iframe (không bắn trực tiếp moneysite).

**Tóm tắt:** Tactic hấp thụ link bẩn qua trang đệm rồi chuyển hướng — chỉ tồn tại trong playbook như phương án đặc biệt. Gate NGHIÊM hơn EN-13: bắt buộc Director duyệt (không chỉ Lead), chỉ cân nhắc trên tài sản test/site tự sở hữu, KHÔNG chạy trên site client trừ khi client ký nhận rủi ro bằng văn bản. Trang đệm phải noindex+follow, cách ly khỏi moneysite (không cùng GSC/analytics footprint khi có thể).

**Chuẩn đạt:** ✅ Approval Director + phạm vi cách ly rõ + kế hoạch tháo dỡ. ❌ Bất kỳ triển khai nào thiếu 1 trong 3 điều trên → fail P0, dừng ngay.

---

## Nhóm E — Verify (gate cuối T3)

### EN-15 — Verify entity recognition 🔒P0-T3

**Nhóm:** Verify
**Nguồn legacy:** GIỮ+NÂNG — "Kiểm tra độ nhận diện thương hiệu" + mục Verification của `sop/04-entity-optimization.md`.

**Tóm tắt:** Search brand (ẩn danh + logged-out) và ghi nhận entity signals: (1) Knowledge Panel / knowledge card xuất hiện chưa (có thể mất 3-6 tháng — chưa có không tự động fail, nhưng phải ghi baseline); (2) brand SERP: site chiếm top 1 + sitelinks, social profiles của mình phủ trang 1; (3) Google gợi ý đúng entity (autocomplete, related searches, "brand + dịch vụ" ra đúng site); (4) không có entity nhầm lẫn/đối thủ chiếm brand SERP; (5) brand mention tracking (Ahrefs) đã bật.

**Chuẩn đạt:** ✅ Báo cáo verify có screenshot + so sánh baseline T1 vs T3; các gap ghi thành action item cho quý sau. ❌ Tick mà không có bằng chứng SERP → fail.

### EN-16 — Tracking & bàn giao file quản lý

**Nhóm:** Verify
**Nguồn legacy:** GIỮ — cột PIC/Deadline/Tiến độ của các sheet legacy + file quản lý GMB Post.

**Tóm tắt:** Toàn bộ đầu ra entity nằm trong file quản lý bàn giao được: danh sách trang onsite (EN-03), profile social + credential (lưu đúng kênh secret, không plaintext trong sheet), Google Stack assets, citation, luồng syndication, approval các tactic gated, báo cáo verify. Người mới nhận dự án đọc file là chạy tiếp được.

**Chuẩn đạt:** ✅ File đủ mục, link sống, credential tách riêng an toàn. ❌ Pass/email nằm công khai trong sheet chia sẻ rộng → fail (đây là điểm phải SỬA so với template legacy vốn để cột "Pass email, Social" ngay trong sheet).
