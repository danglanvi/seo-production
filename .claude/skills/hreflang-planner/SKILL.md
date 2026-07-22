---
name: hreflang-planner
description: "Audit + generate hreflang cho site đa ngôn ngữ / đa thị trường (khách GTV thường VN/EN, một số khách khu vực SEA) — 2 chế độ: AUDIT (self-referencing, return tags 2 chiều, x-default, validate mã ISO 639-1 + ISO 3166-1 — lỗi phổ biến nhất ở khách VN: 'vn' SAI vì vn là mã quốc gia, mã ngôn ngữ phải là 'vi'; conflict canonical×hreflang; hreflang trỏ tới URL noindex/redirect/non-200) và GENERATE (sinh bộ tag sẵn dán theo 1 trong 3 phương án đặt: HTML head / HTTP header / XML sitemap, kèm khuyến nghị chọn phương án theo quy mô site — site lớn nhiều template → sitemap; map với chiến lược cấu trúc ccTLD/subdomain/subfolder). Use when: (1) 'audit hreflang [domain]', 'vì sao Google trả bản EN cho user VN', 'check return tags'; (2) 'site sắp mở bản EN/thị trường mới — set up hreflang thế nào'; (3) 'generate hreflang sitemap/tags cho [danh sách URL cặp ngôn ngữ]'. Data priority: crawl export Screaming Frog Hreflang:All → curl/fetch từng URL đại diện → user paste head/sitemap. KHÔNG dùng cho: audit technical site tổng (→ technical-seo-audit — khu vực 8 chỉ là spot-check, skill này là deep-dive), đổi cấu trúc thị trường/domain đang có traffic (→ site-migration-checklist), sửa cấu trúc HTML head tổng thể (→ semantic-html-optimization)."
metadata:
  version: "1.0"
---

# Hreflang Planner

Deep-dive **hreflang** cho site đa ngôn ngữ/đa thị trường: audit bộ annotation hiện có hoặc generate bộ mới sẵn dán. Nguyên lý gốc: hreflang là **cặp tín hiệu 2 chiều** — thiếu 1 chiều là cả cặp bị Google bỏ qua; và hreflang có mặt trái chia sẻ signal ([[Hreflang PageRank Sharing]]) — nên "chưa gắn hreflang" đôi khi là chủ đích hợp lệ, không auto-flag lỗi.

**Upstream:** crawl export (Screaming Frog `Hreflang:All`) hoặc fetch trực tiếp. **Downstream:** findings giao dev kèm bộ tag/sitemap sửa sẵn; quyết định cấu trúc thị trường lớn (đổi ccTLD↔subfolder) route sang migration.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Audit technical site tổng (7+1 khu vực) | `technical-seo-audit` | Khu vực 8 của skill đó = spot-check khi tiện audit tổng; cần soi hreflang đủ sâu (return tags matrix, ISO, x-default) → gọi skill này |
| Đổi cấu trúc thị trường trên site đang có traffic (ccTLD→subfolder, gộp site quốc gia) | `site-migration-checklist` | Skill này *khuyến nghị* cấu trúc cho bản mới + generate hreflang; thực thi chuyển đổi = sự kiện migration có PRE/DURING/POST riêng |
| Cấu trúc HTML head tổng thể (thứ tự thẻ, semantic head) | `semantic-html-optimization` | Skill này chỉ đụng block hreflang trong head; head bừa bộn/nặng → route |
| Regression hreflang sau deploy | `seo-drift-tracker` | Skill này audit 1 thời điểm; theo dõi hreflang ĐỔI giữa 2 thời điểm → drift-tracker (element #7) |
| Content chất lượng bản dịch, không trộn ngôn ngữ trong 1 URL | `seo-onpage` + [[syntheses/Multilingual SEO]] | Skill này chỉ check annotation, không đánh giá chất lượng bản ngữ |

## Input

**Required:**
- `$MODE` — `audit` / `generate`.
- `$TARGET` — domain (audit) hoặc bảng cặp URL tương đương giữa các bản ngôn ngữ (generate; thiếu → skill giúp dựng từ URL pattern + user xác nhận).

**Optional:**
- `$MARKETS` — danh sách ngôn ngữ-thị trường mục tiêu (vd `vi-VN, en, en-SG`) + thị trường mặc định cho x-default.
- `$STRUCTURE` — cấu trúc hiện tại/dự kiến: ccTLD / subdomain / subfolder / parameter (parameter → khuyến cáo đổi ngay, xem bảng cấu trúc).
- `$CRAWL_EXPORT` — Screaming Frog `Hreflang:All` (+ `Canonicals:All`, `Directives:All` để check conflict) — đường data tốt nhất cho audit site lớn.
- `$SIZE` — số URL/bản ngôn ngữ — quyết định phương án đặt (bảng Bước 3).

**Data ladder (khai báo TIER trong report):**

| Tier | Điều kiện | Data |
|---|---|---|
| **A — Crawl export** | Có SF export (hoặc chạy được SF CLI theo `technical-seo-audit/references/data-paths.md` Path B) | Full matrix return tags toàn site + đối chiếu canonical/directives |
| **B — Fetch đại diện** | Chỉ có URL | curl/fetch 2-3 URL đại diện MỖI template (home, category, bài) × MỖI bản ngôn ngữ + fetch sitemap — kết luận theo template, ghi rõ "chưa quét toàn site" |
| **C — User paste** | Không fetch được (staging chặn IP…) | User paste `<head>` + sitemap entry của bộ URL đại diện — coverage thấp nhất, ghi rõ giới hạn |

## Workflow

### Bước 0 — Đọc references + xác định data tier & scope

1. Đọc `sop/06-self-checklist/tier-3-technical-advance.md` mục 10 (International — 9 item canonical) + [[syntheses/Multilingual SEO]] (4 nguyên tắc) + [[Hreflang PageRank Sharing]] (nuance gate) — khung chấm của skill này.
2. Xác định `$MODE`, tier data, `$MARKETS` (thiếu → hỏi: những thị trường nào là mục tiêu THẬT có content riêng? — hreflang cho bản dịch máy rỗng là phản tác dụng).
3. 🔴 **Gate chủ đích** ([[Hreflang PageRank Sharing]]): trước khi flag "thiếu hreflang" là lỗi, hỏi — bản ngôn ngữ kia đã đủ chất lượng/đủ content chưa? Chưa → thiếu hreflang có thể là chủ đích hợp lệ, ghi nhận là quyết định chứ không phải lỗi.
4. Audit site lớn Tier A cần crawl mới → báo scope + tốc độ, chờ xác nhận (server khách thật — theo quy ước technical-seo-audit).

### Bước 1 — Dựng inventory

Từ data tier: bảng mỗi hàng = 1 URL, cột = ngôn ngữ khai báo, hreflang set (cặp lang→href), canonical, meta robots, HTTP status, nơi đặt (head/header/sitemap). Generate mode: bảng cặp URL tương đương giữa các bản (equivalence map) — user xác nhận map trước khi sinh tag.

### Bước 2 — Audit 6 nhóm check (`$MODE = audit`)

| # | Check | Tiêu chí ĐẠT | Lỗi phổ biến |
|---|---|---|---|
| 2.1 | **ISO code validation** | Ngôn ngữ = ISO 639-1 (`vi`, `en`, `zh`); region (optional) = ISO 3166-1 alpha-2 (`VN`, `US`, `SG`); format `lang` hoặc `lang-REGION` | 🔴 `vn` SAI (vn = quốc gia, ngôn ngữ phải `vi`); `en-UK` sai (phải `en-GB`); region đứng một mình (`VN`) sai; dùng `_` thay `-` |
| 2.2 | **Self-referencing** | Mỗi URL có hreflang trỏ về chính nó trong set | Set chỉ liệt kê "các bản khác" — thiếu self → Google bỏ qua set (tier-3 mục 10.4) |
| 2.3 | **Return tags (2 chiều)** | A trỏ B thì B phải trỏ lại A — matrix đối xứng trên MỌI cặp | Gắn 1 chiều từ bản chính; template bản dịch thiếu block; 1 URL lệch làm hỏng cặp đó |
| 2.4 | **x-default** | Có 1 x-default duy nhất / set, trỏ trang cho user ngoài mọi thị trường khai báo (thường bản chính hoặc language selector) | Thiếu hẳn; nhiều x-default; x-default trỏ trang redirect |
| 2.5 | **Conflict canonical × hreflang** | Mỗi bản canonical self-referential; hreflang trỏ đúng URL canonical | Bản EN canonical về bản VI → mâu thuẫn tín hiệu, Google chọn 1 và thường bỏ hreflang (tier-3 mục 10.2; [[Ranking Signal Consolidation]]) |
| 2.6 | **Đích đến sạch** | Mọi URL trong hreflang: HTTP 200, indexable (không noindex), không redirect, HTTPS | hreflang trỏ URL noindex/301/404 — chiếm phần lớn hreflang bị Google ignore thực tế (tier-3 mục 10.6; [[Status Codes]]) |

Mỗi finding ❌/⚠️ ghi: evidence (URL + giá trị + nguồn tier) → fix cụ thể → **Falsifiability** (Gates #3).

### Bước 3 — Generate (`$MODE = generate`, hoặc output fix của audit)

**3a. Chọn phương án đặt** (chọn MỘT — không trộn 2 phương án cho cùng bộ URL, trộn dễ lệch nhau thành conflict):

| Phương án | Khi nào chọn | Trade-off |
|---|---|---|
| **HTML head** (`<link rel="alternate" hreflang>`) | Site nhỏ-vừa (≤ ~10 ngôn ngữ, template kiểm soát được); cần dev thấy tag trực tiếp | Mỗi URL phải chứa FULL set → n ngôn ngữ = n×n dòng toàn site; head phình + sửa 1 bản phải deploy mọi bản |
| **XML sitemap** (`xhtml:link`) | 🔴 Mặc định cho site lớn / nhiều ngôn ngữ / e-com nhiều URL; hoặc không đụng được template | Quản lý tập trung 1 file, không phình HTML; đổi chỉ resubmit sitemap; dev ít quen format hơn |
| **HTTP header** (`Link:`) | File không-HTML cần hreflang (PDF…) — gần như chỉ dùng cho case này | Khó debug, ít tool đọc; không dùng cho HTML thường |

**3b. Sinh bộ tag sẵn dán** từ equivalence map đã xác nhận: block head per template HOẶC sitemap `xhtml:link` hoàn chỉnh (kèm namespace `xmlns:xhtml`) — full set + self-reference + x-default, URL absolute HTTPS. Sinh xong tự chạy lại 6 check Bước 2 trên chính output (validate output như audit input).

**3c. Map với chiến lược cấu trúc** (khuyến nghị khi user đang chọn cấu trúc cho thị trường mới):

| Cấu trúc | Hợp khi | Ghi chú GTV |
|---|---|---|
| Subfolder (`site.com/en/`) | 🔴 Default khuyến nghị cho đa số khách GTV VN/EN — gom authority 1 domain, vận hành rẻ | Topical authority dồn 1 host; hreflang vẫn bắt buộc giữa các folder |
| Subdomain (`en.site.com`) | Hạ tầng/team tách biệt bắt buộc | Google có thể coi như host tách — authority chia |
| ccTLD (`site.sg`) | Thị trường lớn cần geo-signal mạnh nhất + có nguồn lực build authority riêng từng domain | Đắt nhất; mỗi domain tự gánh backlink |
| URL parameter (`?lang=en`) | ❌ Không khuyến nghị | Khó target, dễ duplicate — nếu đang dùng → kế hoạch đổi (site có traffic → `site-migration-checklist`) |

Đổi cấu trúc trên site đang chạy = sự kiện migration → route, skill này chỉ khuyến nghị đích đến.

### Bước 4 — Render report / bộ tag

- Audit: `03-audits/<client>_Hreflang-Audit_<YYYY-MM-DD>.md` theo skeleton Output.
- Generate: bộ tag/sitemap trong report (fenced code, sẵn dán) + hướng dẫn verify sau deploy (GSC URL Inspection bản từng thị trường; re-audit sau 2-4 tuần).

## Output

```markdown
# Hreflang Audit — <domain>
> Ngày: YYYY-MM-DD · DATA TIER: <A/B/C — nguồn + coverage> · Markets: <vi-VN, en, …> · Nơi đặt hiện tại: <head/header/sitemap/mixed>

## 1. Verdict
- <2-4 câu> · Set hợp lệ: <n>/<m> URL · Lỗi nặng nhất: <…>
- Gate chủ đích: <bản nào thiếu hreflang là chủ đích hợp lệ (đã hỏi user) vs lỗi thật>

## 2. Findings theo 6 nhóm check
| # | Check | Status (✅/⚠️/❌/⬜) | Evidence (URL + giá trị + nguồn) | Fix | Falsifiability + leading indicator |

## 3. Return tags matrix (URL đại diện per template)
| URL | vi-VN | en | x-default | Self | Canonical OK |

## 4. Bộ tag sửa / generate (sẵn dán)
```html hoặc ```xml — full set + self + x-default```

## 5. Khuyến nghị phương án đặt + cấu trúc
- Phương án: <head/sitemap/header> vì <quy mô/lý do> · Cấu trúc: <giữ/đổi — nếu đổi trên site có traffic → site-migration-checklist>

## 6. Data thiếu & verify sau deploy
- Item ⬜ + cách lấy · Lịch re-audit: 2-4 tuần sau deploy
```

## Behavior Gates

**#1 Data tier declare** — Report ghi rõ TIER (A/B/C) + coverage (toàn site / per template / URL paste). Tier B/C không phát biểu "toàn site sạch" — chỉ "trên các template đã kiểm".

**#2 No hard-fail** — Không SF/crawl → Tier B fetch đại diện; không fetch được → Tier C user paste. Luôn có đường chạy, ghi giới hạn.

**#3 Falsifiability** — Mỗi finding kèm "làm sao biết nếu khuyến nghị này sai?" + leading indicator. Vd fix return tags → leading indicator: GSC bản EN tăng impressions từ thị trường EN trong 4-8 tuần; nếu return tags đã đối xứng mà SERP vẫn trả sai bản → nguyên nhân khác (canonical, chất lượng bản dịch, geo-signal) — khuyến nghị hreflang không phải thuốc đúng, điều tra tiếp thay vì gắn thêm tag.

**#4 Chủ đích trước, flag sau** — Không auto-flag "thiếu hreflang" khi chưa qua gate chủ đích ([[Hreflang PageRank Sharing]]) — hreflang share signal 2 chiều; nối bản yếu vào bản mạnh có thể kéo bản mạnh xuống.

**#5 Không hứa geo-fix tuyệt đối** — hreflang là hint, không phải directive: Google có thể bỏ qua khi tín hiệu khác mạnh hơn. Không cam kết "gắn xong là hết trả sai bản" — chỉ cam kết annotation hợp lệ + đo bằng leading indicator.

## Anti-patterns

- ❌ Dùng `vn` làm mã ngôn ngữ (phải `vi`); `en-UK` (phải `en-GB`); region đứng một mình; `_` thay `-`.
- ❌ Bộ hreflang thiếu self-reference hoặc thiếu return tags — 1 chiều = cả cặp vô hiệu.
- ❌ hreflang trỏ URL noindex / redirect / 404 / non-canonical — annotation bị ignore.
- ❌ Canonical cross-language (bản EN canonical về VI) song song với hreflang — mâu thuẫn tín hiệu.
- ❌ Trộn 2 phương án đặt (head + sitemap) cho cùng bộ URL — 2 nguồn lệch nhau thành conflict khó debug.
- ❌ Flag "thiếu hreflang" thành lỗi mặc định khi alternates chưa đủ chất lượng — hỏi gate chủ đích trước.
- ❌ Gắn hreflang cho bản dịch máy rỗng/chưa có content thật — mời Google index bản kém.
- ❌ Khuyến nghị đổi ccTLD↔subfolder rồi "tiện tay" lập kế hoạch chuyển — sự kiện migration, route `site-migration-checklist`.
- ❌ Generate tag bằng URL relative hoặc HTTP — phải absolute + HTTPS.
- ❌ Kết luận "toàn site sạch" từ Tier B/C (fetch đại diện / paste) — chỉ kết luận theo coverage đã kiểm.

## References & wiki

**References nội bộ (cross-ref, không copy):**
- `sop/06-self-checklist/tier-3-technical-advance.md` — mục 10 (International, 9 item) + mục 7.9 (hreflang HTTPS) — canonical checklist.
- `skills/technical-seo-audit/SKILL.md` — khu vực 8 (ranh giới spot-check vs deep-dive) + `references/data-paths.md` (SF CLI cho Tier A, export `Hreflang:All`).
- `skills/site-migration-checklist/SKILL.md` — khi đổi cấu trúc thị trường trên site có traffic.

**Wiki Semantic SEO (lớp WHY):** [[Hreflang PageRank Sharing]] · [[syntheses/Multilingual SEO]] · [[Ranking Signal Consolidation]] · [[Status Codes]] · [[Meta Tags]] · [[Cost of Retrieval]]

**Google docs hiện hành:** developers.google.com/search/docs/specialty/international/localized-versions · developers.google.com/search/docs/specialty/international/managing-multi-regional-sites

## Changelog

- **v1.0 (2026-07-19):** tạo mới — 6 nhóm audit check (ISO validation với case `vn`→`vi`, self-ref, return tags, x-default, canonical conflict, đích sạch), generate 3 phương án đặt + bảng chọn theo quy mô, map cấu trúc ccTLD/subdomain/subfolder (default GTV: subfolder), gate chủ đích theo [[Hreflang PageRank Sharing]]; canonical checklist kế thừa tier-3 SOP mục 10.
