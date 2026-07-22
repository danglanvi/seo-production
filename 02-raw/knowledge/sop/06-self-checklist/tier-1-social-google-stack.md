---
type: sop
tier: 1
phase: entity-offsite
last_updated: 2026-07-19
source_file:
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình Social Entity - GTV SEO.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/6. Quản lý outsource/SEO Outsource/Phân loại Social - Social Stack - bản PSP.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/List web social, forum triển khai link.xlsx
  - raw/_ingested/Quy trình SEO PSP - All In One/2. QUY TRÌNH SEO Project/9. Entity/Quy trình triển khai GMB Post - GMB Post Silo.xlsx
items_count: 13
tags: [sop, tier-1, social, google-stack, entity-offsite, self-checklist]
---

# Tier 1 — Checklist triển khai Social & Google Stack

> **Khi dùng:** Triển khai entity offsite (con của EN-07/EN-08 trong `tier-1-entity.md`) — người làm entity/outsource tự check, SEO EX verify.
> **Số items:** 13 (SGS-01…SGS-13) = 1 chuẩn bị + 3 platform tier + 3 chuẩn profile + 3 Google Stack + 1 nhịp duy trì + 2 verify.
> **Scoring:** Self Score /13 → Self %. P0 = 5 items: SGS-01, SGS-02, SGS-05, SGS-07, SGS-12.
> **Chỉ đạo Vincent:** social stacking GIỮ (cross-link profile là tactic hợp lệ). Bỏ định mức máy móc "200 social" của legacy — chất lượng + nhất quán + sống được > số lượng. Platform list legacy (DR cao 2021-2023) đã chắt lọc còn platform **còn sống & đáng làm 2026**.

## Map item → wiki concept

| ID | Label | Wiki ref |
|---|---|---|
| SGS-01 | Brand Info Pack áp dụng | [[Entity Identity Management]] + [[Brand Identity]] |
| SGS-02 | Platform Tier 1 (bắt buộc) | [[Brand Entitization Playbook]] |
| SGS-03 | Platform Tier 2 (khuyến nghị) | [[Brand Entitization Playbook]] |
| SGS-04 | Platform Tier 3 (theo ngành) | [[Source Context]] |
| SGS-05 | NAP + brand assets per profile | [[Entity Identity Management]] |
| SGS-06 | Bio / mô tả E-A-V nhất quán | [[E-A-V Framework]] |
| SGS-07 | Link về Entity Home + cross-link (stacking) | [[Entity Home]] |
| SGS-08 | Tạo bộ Google Stack | [[Brand Entitization Playbook]] |
| SGS-09 | Liên kết chéo + embed trong stack | [[Knowledge Graph]] |
| SGS-10 | Stack trỏ về Entity Home / URL target | [[Entity Home]] |
| SGS-11 | Nhịp duy trì post (social + GBP) | [[Web Entity]] |
| SGS-12 | Verify index | [[Web Entity]] |
| SGS-13 | File quản lý profile & credential | [[Entity Identity Management]] |

---

## Nhóm A — Chuẩn bị

### SGS-01 — Brand Info Pack áp dụng thống nhất 🔒P0

**Nguồn legacy:** GIỮ — block info của sheet "Social stack brand"/"Social stack author" (`Quy trình Social Entity`): tên công ty/thương hiệu, mã số thuế, địa chỉ, zipcode, phone, ngày thành lập, email, logo 500×500, background 1200×800, map, NAP, username, tên profile dài/ngắn, bio ngắn <200, bio dài <1000, hashtags, code chèn bio.

**Tóm tắt:** Dùng đúng Brand Info Pack đã chốt ở EN-01 — không tự chế bio/username per kênh. Chuẩn bị trước: 1 email brand riêng cho bộ social (không dùng email cá nhân nhân sự), username convention thống nhất (1 chính + 1 fallback khi trùng), 2+ hình ảnh dịch vụ/sản phẩm đã tối ưu (filename/alt/geo-tag nếu local), logo/avatar + cover đúng brand hiện hành.

**Chuẩn đạt:** ✅ Mọi profile tạo sau đây đều truy về info pack; fallback username được ghi lại. ❌ Mỗi platform một bio tự viết → fail.

## Nhóm B — Chọn platform theo tier

### SGS-02 — Tier 1: bắt buộc mọi dự án 🔒P0

**Nguồn legacy:** GIỮ+CHẮT LỌC từ top DR list ("Mẫu (final)", "Tổng hợp Social stack").

**Danh sách bắt buộc:**

| Platform | Ghi chú |
|---|---|
| Google Maps / GBP | Nếu doanh nghiệp local — theo `local-seo-audit/references/gbp-checklist.md` |
| Facebook Page | Kênh brand VN mặc định; NAP + tab About đầy đủ |
| LinkedIn Company Page (+ profile founder) | B2B trust + entity signal mạnh |
| YouTube channel | Tab About = bio dài + link; video = nguyên liệu syndication |

**Chuẩn đạt:** ✅ 4 kênh (hoặc 3 nếu không local) tạo xong, verify được (badge/quyền quản trị), đầy đủ theo SGS-05/06/07. ❌ Thiếu bất kỳ kênh Tier 1 áp dụng nào → fail P0.

### SGS-03 — Tier 2: bộ khuyến nghị mặc định (chắt lọc 2026)

**Nguồn legacy:** CHẮT LỌC — từ list DR cao legacy (~200 domain), giữ platform còn sống, tự đăng ký được, còn giá trị profile công khai:

| Giữ (2026) | Vai trò |
|---|---|
| X/Twitter | Bio + pinned; stack qua post |
| Instagram | Brand visual; bio NAP (không stack được link trong post — legacy đã note) |
| Pinterest | Đăng tối thiểu 2 hình + stack link |
| TikTok | MỚI so với legacy list — thêm vì là kênh brand search 2026 |
| Medium | Đăng full bài syndication + bio |
| Tumblr, Blogger, WordPress.com | Web 2.0 cho syndication content |
| Reddit, Quora | Profile + bio (không spam link trong answer) |
| Vimeo, SoundCloud / Spotify for Creators (podcast) | Media assets |
| Behance / Dribbble | Nếu có asset design |
| Crunchbase | Company profile — entity signal tốt |
| About.me, Gravatar, Linktr.ee | Hub bio + gom link |
| GitHub | Chỉ brand tech/SaaS |

**Bỏ (platform chết / hết giá trị / rủi ro brand):** Google+ (đã chết), Myspace, Mix.com, 8tracks, StockTwits, Storeboard, Quia, idea.informer, blog.b92.net, forum.index.hu, OnlyFans (sai ngữ cảnh brand — legacy từng list vì DR), KnowYourMeme/Comicvine/Polygon-comment-profile (spam-profile không còn index giá trị), raovat.vnexpress (đóng).

**Chuẩn đạt:** ✅ Chọn 10-15 platform Tier 2 phù hợp brand (không cần tất cả), lý do chọn/bỏ ghi trong file quản lý. ❌ Đăng ký hàng loạt platform chết theo list cũ → fail.

### SGS-04 — Tier 3: platform theo ngành

**Nguồn legacy:** GIỮ — pattern legacy đã dùng đúng cách (Houzz cho nội thất, TripAdvisor cho du lịch, Zillow BĐS…) + sheet "Xác thực doanh nghiệp" (trang vàng, job sites — đã tách về EN-09).

**Tóm tắt:** Mỗi ngành thêm 3-5 platform đặc thù nơi khách hàng thật hiện diện: F&B/du lịch → TripAdvisor, Foody; nội thất/xây dựng → Houzz; giáo dục → Goodreads (xuất bản), edu portals; y tế → hellobacsi-class directories; tech → Product Hunt, Stack Overflow company. Nguyên tắc chọn: platform có trang profile công khai + index được + đúng Source Context của brand.

**Chuẩn đạt:** ✅ 3-5 platform ngành có hồ sơ đầy đủ; N/A nếu ngành không có platform đáng làm (ghi rõ). ❌ Bỏ qua platform ngành hiển nhiên (khách sạn không có TripAdvisor) → fail.

## Nhóm C — Chuẩn profile per platform

### SGS-05 — NAP + brand assets đầy đủ trên từng profile 🔒P0

**Nguồn legacy:** GIỮ — công đoạn 2.0-4.0 sheet "Update tháng 6.2021 - social stack": tối ưu tên/địa chỉ/phone/mô tả/title/website; đăng logo + tối thiểu 2 hình; hoàn tất mọi mục setting platform cho phép.

**Tóm tắt:** Mỗi profile: đúng NAP info pack; title/tên profile chứa tên thương hiệu (brand profile) hoặc tên author (author profile); avatar = logo chuẩn, cover = background chuẩn; điền HẾT field mà platform cho (website, giờ làm việc, khu vực, category…) — "dùng toàn bộ tính năng trong cài đặt profile cho phép" (nguyên văn chuẩn legacy, vẫn đúng).

**Chuẩn đạt:** ✅ Spot-check 5 profile bất kỳ: không field trống mà platform hỗ trợ, hình đúng brand. ❌ Profile chỉ có username + avatar → fail.

### SGS-06 — Bio / mô tả E-A-V nhất quán

**Nguồn legacy:** SỬA — legacy chỉ yêu cầu "mô tả ngắn + title chứa keyword/brand". Nâng theo chuẩn wiki: bio là câu định nghĩa entity.

**Tóm tắt:** Bio ngắn và bio dài viết theo E-A-V: [Brand] (E) là [type/category] (A=is-a) cung cấp [dịch vụ chính] (A=offers) tại [khu vực] (A=areaServed), thành lập [năm]. Cùng một bộ facts trên MỌI kênh (absolute facts — không kênh nói "từ 2017", kênh nói "hơn 10 năm"). Keyword dịch vụ xuất hiện tự nhiên, không nhồi.

**Chuẩn đạt:** ✅ Bio mọi kênh = đúng 2 bản trong info pack (ngắn/dài), facts khớp nhau 100%. ❌ Facts lệch nhau giữa các kênh → fail.

### SGS-07 — Link về Entity Home + cross-link giữa profiles (stacking) 🔒P0

**Nguồn legacy:** GIỮ+SỬA ĐỊNH MỨC — công đoạn 5.0 "Stacking" legacy (60 social lớn stack ≥10 link về social khác, mỗi social ≥1 link về site, mỗi social được stack ≥5 lần). Giữ tactic, hạ định mức máy móc.

**Tóm tắt:** (1) Mỗi profile có link về website — ưu tiên Entity Home/trang chủ; (2) profile nào có field đa link (About, Linktr.ee, YouTube links, Google Site) → liệt kê các profile chính còn lại = cross-link stacking; (3) mỗi profile chính được ÍT NHẤT 2-3 profile khác trỏ tới (thay mức "≥5 lần" cũ — đủ để crawler đi hết vòng); (4) danh sách link trong profile khớp mảng `sameAs` của Organization schema (EN-06) — social và schema phải kể cùng một câu chuyện.

**Chuẩn đạt:** ✅ Vẽ/lập bảng ma trận stack: mọi profile chính đều có inbound từ profile khác + outbound về Entity Home; sameAs sync. ❌ Profiles rời rạc không link nhau, schema sameAs liệt kê kênh không tồn tại → fail P0.

## Nhóm D — Google Stack

### SGS-08 — Tạo bộ tài sản Google Stack

**Nguồn legacy:** GIỮ — "Google stack brand" + cấu phần GG stack trong quy trình @id loop (siteview, blogger…) + công đoạn 7.0 sheet social (stack tài sản GG: Google Site, My Maps, business site; embed Sheet/Calendar/Slide/Form).

**Tóm tắt:** Bộ tối thiểu: **Google Site** (mini-site brand: giới thiệu, NAP, dịch vụ, link profiles), **Google Docs** (bản giới thiệu công ty public), **Google Sheets** (bảng thông tin/danh mục public), **Google Slides** (company profile deck), **Google My Maps** (map địa điểm/khu vực phục vụ), **YouTube** (đã có ở Tier 1), Drive folder public chứa cả bộ. Mọi tài sản dùng chung 1 tài khoản Google brand, đặt tên chứa brand.

**Chuẩn đạt:** ✅ Đủ bộ tài sản, share "anyone with link can view", nội dung = info pack. ❌ Tài sản nằm rải trên tài khoản cá nhân nhân sự → fail.

> ⚠ **Ranh giới gate:** SGS-08/09 là Google Stack HỢP LỆ (info pack + liên kết chéo trong hệ Google). Bước sang **@id loop / trang trung gian noindex+iframe / sửa `@id` schema trỏ chéo** là tactic risk-controlled KHÁC — bắt buộc qua gate EN-13 của `tier-1-entity.md` (Lead/Director duyệt), không tự triển khai từ checklist này.

### SGS-09 — Liên kết chéo + embed trong stack

**Nguồn legacy:** GIỮ — chuẩn legacy: web 2.0/tài sản trong stack "phải có iframe/embed của các tài sản còn lại", stack vòng 1 → vòng 2.

**Tóm tắt:** Google Site làm hub: embed Docs/Sheets/Slides/My Maps/YouTube video ngay trong page; Docs/Slides chèn link tới nhau + tới Site; My Maps description có link Site + website. Một crawler vào bất kỳ tài sản nào phải đi tới được toàn bộ stack (vòng khép kín — đúng tinh thần "stack vòng 1/vòng 2" cũ, không cần iframe hack ngoài hệ Google).

**Chuẩn đạt:** ✅ Test click-through: từ Google Site tới được mọi tài sản và ngược lại. ❌ Các tài sản tồn tại nhưng không link nhau → fail.

### SGS-10 — Stack trỏ về Entity Home / URL target

**Nguồn legacy:** GIỮ — mục đích gốc của GG stack (đẩy entity brand hoặc URL SEO cụ thể; phân loại "trang chủ → stack brand & entity, URL SEO → stack cho URL" — công đoạn 1.0 legacy).

**Tóm tắt:** Xác định target của stack: mặc định = Entity Home + trang chủ (stack brand). Nếu Lead chỉ định stack cho URL SEO cụ thể (pillar/money page) → mỗi tài sản có link contextual về URL đó, anchor tự nhiên (brand/URL/topic — không exact-match dày đặc). Stack cho URL đi xa hơn (@id loop) → PHẢI qua gate EN-13.

**Chuẩn đạt:** ✅ Mỗi tài sản ≥1 link về target đã chỉ định; anchor plan ghi trong file quản lý. ❌ Stack không trỏ về đâu, hoặc tự ý chạy @id loop không gate → fail.

## Nhóm E — Nhịp duy trì

### SGS-11 — Nhịp post duy trì (social + GBP Post)

**Nguồn legacy:** GIỮ+SỬA — legacy: GMB Post cơ bản (title bài ở đầu content, 1-2 link về web + 2-3 link Tier-1 social, xuất bản, cập nhật file quản lý) + GMB Post Silo (post mô phỏng internal link topic cluster) + social hoạt động qua syndication. Sửa: tần suất theo baseline gbp-checklist hiện hành, không copy 100% content bài viết vào post.

**Tóm tắt:** Sau khi lập xong không được để profile "chết": (1) social chính (Tier 1 + Medium/X): tối thiểu 2-4 post/tháng — nguồn content lấy từ luồng syndication EN-11; (2) GBP: post ≤30 ngày/lần, đứt nhịp >90 ngày = cờ đỏ (baseline `gbp-checklist.md` mục 5); (3) GBP Post Silo cho URL pillar/cluster khi dự án cần đẩy topic — giữ mô hình legacy: post liên kết về URL SEO + link chéo các post/tài sản Google khác; (4) phân công PIC + lịch trong file quản lý.

**Chuẩn đạt:** ✅ Lịch post tồn tại + 4 tuần gần nhất đúng nhịp. ❌ Toàn bộ profile im lặng từ lúc tạo → fail.

## Nhóm F — Verify

### SGS-12 — Verify index 🔒P0

**Nguồn legacy:** GIỮ+SỬA — công đoạn "Index" trong mọi sheet legacy (blog comment/lazindex) + sheet "khó index" (danh sách domain khó index đã biết). Sửa: phương pháp index dùng bộ hiện hành (mục `11. Các phương pháp index link`), không mặc định blog-comment spam.

**Tóm tắt:** Profile/tài sản không index thì không đóng góp entity signal. Kiểm `site:` hoặc search URL trực tiếp cho: toàn bộ profile Tier 1, các profile Tier 2 quan trọng, Google Site + tài sản stack chính. Kênh nằm trong nhóm khó index đã biết (scholar, twitch, trello, academia…) → ghi nhận, không đốt effort ép index.

**Chuẩn đạt:** ✅ Bảng index status per URL: indexed / chờ / khó-index-chấp-nhận; kênh Tier 1 + Google Site phải indexed. ❌ Không kiểm tra index trước khi báo hoàn thành → fail P0.

### SGS-13 — File quản lý profile & credential

**Nguồn legacy:** GIỮ+SỬA BẢO MẬT — template legacy có cột STT/Domain/Link triển khai/Username/Note (giữ) và cột "Pass email, Social" ngay trong sheet (bỏ).

**Tóm tắt:** File quản lý cuối: mỗi dòng = 1 profile/tài sản (platform, URL, username, ngày tạo, trạng thái index, PIC, note stack). **Credential tách khỏi sheet** — lưu password manager/kênh secret của công ty, sheet chỉ ghi "credential: vault/[tên entry]". Bàn giao được cho người mới hoặc trả khách cuối hợp đồng.

**Chuẩn đạt:** ✅ File đủ cột, mọi URL sống, credential không plaintext. ❌ Pass nằm trong sheet share link → fail.
