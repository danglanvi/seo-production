# Spam Filter Criteria — Đánh giá backlink GIỮ hay LOẠI (07/2026)

> Reference cho skill `backlink-research` (Bước 3 Link gap screening + Bước 5 quality RDs count) và tái dùng ở `backlink-plan` (chọn nguồn). Trả lời câu hỏi vận hành: **"Tool flag link là spam/toxic nhưng thực tế link vẫn tốt — tiêu chí đúng là gì?"**
>
> Evidence đầy đủ + verbatim quotes: wiki [[sources/research-2026-07-spam-link-criteria]].

## Nguyên tắc nền (3 câu chốt)

1. **"Toxic link score" là metric do tool tự chế — không phải khái niệm của Google.** Mueller 05/2024: *"The concept of toxic links is made up by SEO tools so that you pay them regularly."* Ahrefs cố tình KHÔNG có spam score. Google từ Penguin 4.0 + SpamBrain (Link Spam Update 12/2022): link spam bị **neutralize** (mất giá trị, về 0) chứ không âm điểm; Illyes: *"we disable insane numbers of links"*.
2. **Không có toxic LINK, chỉ có toxic PROFILE** (Danny Richman). Link rác lẻ tẻ = Google tự bỏ qua, không cần làm gì. Pattern lớn + chủ động mua/build ở quy mô → Mueller thừa nhận "lost trust… drop in visibility". → Đơn vị đánh giá rủi ro là **pattern toàn profile**, không phải từng link.
3. **Chi phí loại nhầm link tốt > chi phí giữ nhầm link rác.** Bằng chứng thực nghiệm: Ahrefs disavow toàn bộ link bị tool flag "toxic" của 3 bài blog → traffic **giảm 7,1%** (link bị flag đang thực sự giúp rank); case Reddit −60%. Marie Haynes: link thật sự độc *"rarely returned by an SEO tool"*. → **Mặc định: nghi ngờ → GIỮ + đánh dấu review.**

## Vì sao tool flag sai (hiểu để không tin mù)

- **DataForSEO spam score = 18 tín hiệu THUẦN technical/on-page** của trang nguồn (HTTP thay HTTPS +30%, title ngoài 30-65 ký tự +5%, không nhúng script Google/FB +20%, TLD lạ +20%, >100 external links +20%…). **KHÔNG có tín hiệu nào đo organic traffic, relevance, hay editorial** → site thật nhưng code cũ dễ bị điểm cao; PBN kỹ tính dễ được điểm thấp. Bands: 0-30 low / 31-60 medium / 61-100 high; score domain = **trung bình cộng** score từng page.
- **Semrush Toxicity (45+ markers)**: có markers flag cả **guest post hợp lệ, footer link, author bio link (chuẩn E-E-A-T), sitewide, link từ geo khác** → false positive cấu trúc. Chính Semrush yêu cầu *"manually review with the utmost care"* trước khi hành động.

→ **Spam score chỉ là PRIOR yếu (tín hiệu nghi vấn), không bao giờ là verdict.**

## Tầng 1 — Máy LOẠI CHẮC (auto-reject, cần ≥2 tín hiệu ĐỒNG THỜI)

Chỉ auto-loại khi dính **từ 2 trở lên** trong các tín hiệu sau (1 tín hiệu đơn lẻ → đẩy xuống Tầng 2 review):

| # | Tín hiệu | Cách check (DataForSEO / Ahrefs) |
|---|---|---|
| M1 | Spam score **high band** (DFS ≥61 / hoặc bands tool tương đương) | `bulk_spam_score` |
| M2 | **Zero organic**: site không rank nổi keyword nào kể cả brand của chính nó | `ranked_keywords` ≈ 0 / Ahrefs organic traffic ≈ 0 |
| M3 | **Outbound farm pattern**: link ra casino/pharma/adult/crypto-scam xen lẫn mọi chủ đề; OBL >100/trang; external/internal >3 | Xem outbound của domain (`domain_pages_summary`, spot-check) |
| M4 | **De-indexed / non-indexed domain** | `site:` operator |
| M5 | **Traffic trajectory sập vực**: mất phần lớn traffic sau core/spam update và không hồi ("traffic graphs that look like the 2008 financial crisis" — Floate) | Ahrefs/Semrush traffic history |
| M6 | **Link farm ratio**: phần lớn bài trên site là guest post/niche edit thương mại (site tồn tại để bán link) | Floate Link Vetting; spot-check 10 bài mới nhất |

## Tầng 2 — Người/LLM XÉT (giữ hay loại, theo thứ tự trọng số)

1. **Theme relevance** (quan trọng nhất — khớp 3T của GTV: Theme > User signal > Trust; Illyes: Google tự disable link lệch chủ đề hoàn toàn kiểu "casino → trang hoa"). Relevance là **phổ 4 mức**: domain-level → article-level → paragraph-level → sentence-level; "tangentially related" vẫn chấp nhận được, không đòi 100% hyper-relevant.
2. **Organic traffic thật + trend** — site có rank keywords thật, traffic ổn định/tăng (không bot, không spike seasonal giả — Floate: "traffic authenticity").
3. **Content thật + editorial standard** — bài có tác giả, có cấu trúc, không spun; site có real audience.
4. **Vị trí link**: in-content editorial > author bio > sidebar/footer (footer/sidebar không tự động xấu — chỉ không được chiếm tỷ trọng lớn).
5. **Outbound profile sạch** — trang nguồn link ra ai? Lẫn casino/pharma → hạ điểm mạnh.
6. **DR/rank chỉ là baseline lọc thô** — không bao giờ quyết một mình ("metrics có thể mua trên Fiverr $100 để bơm DR 50+" — Floate; "show me the domain" khi mua qua vendor).
7. **Sliding scale (Holy Trinity)**: Relevance × Authority × Power — thiếu yếu tố này thì yếu tố kia phải cao hơn; không đòi mọi link max cả 3 (profile tự nhiên có phân bố).

## Disavow policy (đặt đúng chỗ, tránh lạm)

- **CHỈ disavow khi:** (a) có **manual action** unnatural links trong GSC, hoặc (b) profile có số lượng LỚN link manipulative do chính mình chủ động build và "likely will cause a manual action" (guidance Google verbatim). 69% SEOs không còn dùng disavow; Bing đã bỏ hẳn tool 2023.
- **KHÔNG disavow** theo danh sách toxic của tool (Mueller: "billable waste of time"; thực nghiệm cho thấy có thể tự bắn vào chân −7% traffic).
- Negative SEO attack: gần như không bao giờ là nguyên nhân thật (Illyes: hàng trăm case chỉ 1 đáng chuyển webspam team) — nhưng nếu traffic drop TRÙNG THỜI ĐIỂM với influx link lạ quy mô lớn → điều tra thêm trước, disavow là bước cuối.

## Áp vào output của backlink-research

- Bảng link gap / quality RDs: mỗi domain có cột `verdict = KEEP / REVIEW / REJECT` + cột `lý do` (tín hiệu nào). REJECT phải ghi rõ ≥2 tín hiệu Tầng 1. REVIEW = mặc định cho mọi ca lưng chừng.
- Đếm "quality RDs" (money-page link-gap test): chỉ loại REJECT; REVIEW vẫn đếm (kèm dấu *).
- Không dùng chữ "toxic" trong report — dùng "REJECT theo tiêu chí M#" để truy nguyên được.
