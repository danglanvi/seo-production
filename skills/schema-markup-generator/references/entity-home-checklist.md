# Entity Home Checklist — On-site + Off-site + Verification

Checklist triển khai Entity Home + Author entity, bám `sop/04-entity-optimization.md` + [[Brand Entitization Playbook]] + [[Entity Home]] (Jason Barnard). Dùng ở Bước 6 của SKILL.md khi scope là Entity Home / Author entity.

**Entity Home là gì:** web page nơi search engine học identity + attributes + values của entity — centroid của cluster pages định nghĩa entity. Nếu tồn tại nhiều "entity homes" conflict (About page, LinkedIn, Crunchbase nói khác nhau) → authority/centrality/expertise quyết định trang nào thắng (Corroboration of Web Answers). Multi-language entity homes tăng SE confidence.

**Kỳ vọng đúng:** Knowledge Panel có thể mất **3-6 tháng** sau entity optimization, phụ thuộc corroboration off-site. Schema chỉ là 1 trong các feeds vào Knowledge Graph (cùng Entity Home, Wikipedia, Wikidata, SERP consensus — [[Knowledge Graph]]). 🔴 Không hứa Knowledge Panel như deliverable chắc chắn, không hứa timeline sớm hơn.

---

## 1. Entity Home page tồn tại + canonical

- [ ] Có 1 page duy nhất đóng vai Entity Home (thường About page cho Organization, author bio page cho Person).
- [ ] URL canonical, self-referencing, không bị duplicate qua parameters/www-non-www.
- [ ] Page index được (không noindex, không chặn robots.txt).
- [ ] Nội dung page nhất quán với mọi profile ngoài (LinkedIn, GBP, Crunchbase…) — tránh conflict giữa các "entity homes".
- [ ] (Nâng cao) Site đa ngôn ngữ → entity home mỗi ngôn ngữ, hreflang nối nhau, facts nhất quán cross-language.

## 2. Schema đúng type cho Central Entity

- [ ] Central Entity là Organization → Organization JSON-LD (template mục 1 của jsonld-templates.md), `@id = {domain}/#organization`, khai đầy đủ tại **Entity Home** (About page nếu có, homepage nếu không) — homepage khi đó chỉ reference `@id`.
- [ ] Central Entity là Person → Person + ProfilePage (template mục 3), `@id = {url}/#person`.
- [ ] Central Entity là Product/Place → Product/LocalBusiness type tương ứng.
- [ ] Không có block Organization/Person đầy đủ thứ hai ở page khác — mọi nơi khác reference qua `@id`.

## 3. sameAs — Wikipedia / Wikidata / socials

**Wikipedia Verify trước (bắt buộc — [[Central Entity]], SOP v1 Bước 3):** search `"[Central Entity] Wikipedia"`.
- Có trang Wikipedia riêng → high probability entity đã trong Knowledge Graph → đưa Wikipedia URL + Wikidata QID vào sameAs.
- Không có → sameAs CHỈ gồm social profiles chính thức. 🔴 Không bịa Wikipedia URL/QID — bịa = phá entity reconciliation. ⚠️ Không tự đề xuất tự-submit Wikidata item cho brand nhỏ (notability risk, chưa có SOP — cần Vincent duyệt).

- [ ] Wikipedia URL (nếu THẬT có trang).
- [ ] Wikidata URI dạng `https://www.wikidata.org/wiki/Qxxx` (nếu THẬT có item).
- [ ] Social profiles chính thức: LinkedIn, Facebook, X, YouTube (Google đọc social links trong Organization schema → feed Knowledge Panel — [[Brand Entitization Playbook]]).
- [ ] LocalBusiness → GBP URL trong sameAs/hasMap.
- [ ] Mọi URL trong sameAs đã click-verify là profile của đúng entity (không nhầm brand trùng tên).

## 4. NAP consistent

- [ ] Name-Address-Phone trong schema = footer site = GBP = mọi directory citation, khớp từng ký tự.
- [ ] Đổi địa chỉ/số điện thoại → update đồng loạt schema + GBP + citations, không để lệch.

## 5. Author bio + Person schema (Author entity)

- [ ] Mỗi author có bio page riêng với ProfilePage + mainEntity Person (template mục 3).
- [ ] Person có `@id` ổn định; mọi Article.author trên site reference đúng `@id` đó.
- [ ] sameAs của author: LinkedIn, X, Google Scholar, Wikidata (nếu thật) — càng quan trọng khi author có nhiều tên/cách phát âm (reconciliation khó — [[Authorship]]).
- [ ] `worksFor` → `#organization` (nối Author Graph vào brand entity).
- [ ] Byline trên bài = tên trong Person schema, chính tả nhất quán 100% mọi bài.
- [ ] `knowsAbout` khớp topical footprint thật (bài đã publish), không nhồi.

## 6. E-A-V coverage trên Entity Home

Google KG lưu entity dạng triples Entity-Attribute-Value; Entity Home phải cung cấp/củng cố triples đó bằng text — schema không thay được visible content ([[E-A-V Framework]]).

- [ ] **Identity:** entity là ai/là gì — có definitive answer hiển thị trên page, không nước đôi.
- [ ] **Type/category:** thuộc loại nào (agency? SaaS? cá nhân chuyên môn gì?).
- [ ] **Key attributes:** mỗi attribute quan trọng có definitive answer trên page, consistent cross-page. Tiêu chí viết/chấm nội dung + cách chọn attribute (RPP Score) → xem `semantic-content-writing` / [[E-A-V Framework]] — skill này chỉ verify presence, không lặp công thức/writing rules ở đây.
- [ ] **Relations:** founder, parent company, brands, key people — mỗi relation là 1 triple rõ.
- [ ] **Authority signals:** giải thưởng, chứng nhận, khách hàng tiêu biểu (đúng entity — không mix GTV/TAG), press mentions.
- [ ] Mọi giá trị trong schema (foundingDate, legalName, address…) xuất hiện dạng text hiển thị trên page — schema khớp visible content 1:1.

## 7. @id graph nối các node

- [ ] `{domain}/#organization` khai 1 lần (tại Entity Home) ← referenced by: homepage, Article.publisher, Service.provider, Product.brand, Person.worksFor.
- [ ] `{author-url}/#person` per author ← referenced by: Article.author, ProfilePage.mainEntity.
- [ ] Chạy validator.schema.org trên các page mẫu: references resolve, không duplicate entity node.
- [ ] Không có 2 `@id` khác nhau trỏ cùng 1 entity thật (vd `/#org` và `/#organization` song song).

## 8. Off-site corroboration

Schema + Entity Home cần được corroborate từ ngoài — KG feeds từ nhiều nguồn:

- [ ] Wikipedia/Wikidata mention (nếu đủ notability — không ép).
- [ ] GBP/GMB đầy đủ + active (LocalBusiness/Organization có địa điểm).
- [ ] Citations trên nguồn authoritative của ngành (báo, directory ngành, hiệp hội).
- [ ] Author footprint off-site: bài guest, podcast, hồ sơ speaker — byline nhất quán.
- [ ] Profiles social active, thông tin bio khớp Entity Home (không để LinkedIn nói khác About page).
- [ ] Mentions tracking đã setup (Ahrefs alerts hoặc tương đương).
- [ ] Pre-launch check ([[Brand Entitization Playbook]]): entity identifier đã có chưa (Wikipedia ID / Wikidata QID / Knowledge Panel URL)?

## 9. Verification & theo dõi

- [ ] Mốc kỳ vọng: Knowledge Panel **3-6 tháng** sau khi hoàn tất on-site + off-site (sop/04) — ghi rõ trong deliverable client, không cam kết.
- [ ] Brand SERP check định kỳ (search tên brand): Knowledge Panel? site links? social profiles đúng?
- [ ] `site:` + search `"[Entity] Wikipedia"` định kỳ quý — trạng thái entity trong KG có chuyển biến.
- [ ] GSC Enhancements: Organization/Profile page features không lỗi.
- [ ] Ahrefs mention tracking chạy — mentions mới có nhất quán NAP/facts không.
- [ ] Ghi log ngày hoàn tất từng mục để đối chiếu timeline 3-6 tháng.

---

## Definition of Done (Entity Home scope)

- [ ] Mục 1-7 on-site: 100% checked.
- [ ] Mục 8 off-site: đã xuất checklist + sameAs slots cho client/team — skill KHÔNG thực thi off-site (→ Brand Entitization Playbook).
- [ ] Deliverable có mục "Giới hạn hiệu quả" (schema ✗ AI-citation lever — DiD Ahrefs 05/2026) + mốc 3-6 tháng Knowledge Panel.
