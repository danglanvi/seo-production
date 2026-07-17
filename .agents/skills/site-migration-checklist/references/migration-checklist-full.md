# Migration Checklist — 3 giai đoạn chi tiết

Checklist thao tác đầy đủ cho site migration. Mỗi item có `[owner: SEO/Dev]` + `[blocker: yes/no]` — blocker = chưa xong thì KHÔNG launch. Dùng kèm [SKILL.md](../SKILL.md) (workflow + gates) và [redirect-mapping-method.md](redirect-mapping-method.md) (mapping chi tiết).

## Mục lục (TOC)

- [0. Scoping](#0-scoping)
  - [0.1 Bảng migration type → items áp dụng](#01-bảng-migration-type--items-áp-dụng)
  - [0.2 Gate items](#02-gate-items)
- [1. PRE](#1-pre)
  - [1.1 Benchmark](#11-benchmark)
  - [1.2 Full crawl site cũ](#12-full-crawl-site-cũ)
  - [1.3 Dọn index pollution](#13-dọn-index-pollution)
  - [1.4 Redirect mapping](#14-redirect-mapping)
  - [1.5 Staging audit](#15-staging-audit)
  - [1.6 Server capacity](#16-server-capacity)
- [2. DURING — launch day](#2-during--launch-day)
- [3. POST](#3-post)
  - [3.1 Tuần 1](#31-tuần-1--cửa-sổ-cứu-redirect-sót)
  - [3.2 Tuần 2-6](#32-tuần-2-6--coverage--transfer)
  - [3.3 Tháng 2-6](#33-tháng-2-6--historical-data-lens)
  - [3.4 Triage matrix + 6 nguyên nhân drop](#34-triage-matrix--6-nguyên-nhân-drop)
  - [3.5 Rollback decision tree](#35-rollback-decision-tree-convention-gtv)
  - [3.6 Recovery timeline tham khảo](#36-recovery-timeline-tham-khảo-ước-lượng-có-label)

---

## 0. Scoping

### 0.1 Bảng migration type → items áp dụng

| Item | Domain move | HTTP→HTTPS | URL structure | Redesign giữ URL | Merge sites | CMS change |
|---|---|---|---|---|---|---|
| Change of Address (GSC) | 🔴 Có — mọi variant www/non-www, subdomain | Không (Google xác nhận không cần) | Không | Không | Per-domain nguồn | Không (trừ khi kèm domain) |
| Redirect map 1-1 | Có | Có (rule đơn giản host-level) | Có — map từng URL | Không (URL giữ nguyên) | Có — per-site nguồn | Thường có (CMS hay đổi URL pattern) |
| Staging audit | Có | Có | Có | Có | Có | Có |
| Content parity check | Có | Không | Có | 🔴 Trọng tâm chính | Có | Có |
| Speed parity check | Có | Có | Có | 🔴 Trọng tâm chính | Có | 🔴 Trọng tâm chính |
| Hreflang update | Có (nếu multi-lang) | Có | Có | Không | Có | Có |

⚠️ Site lớn: Google cho phép move theo section để dễ monitor/fix — chọn section ít biến động làm test trước (Google site-move doc).

### 0.2 Gate items

- [ ] Xác nhận `$MIGRATION_TYPE` duy nhất — 🔴 **"Change only one thing at a time"** (Google site-move doc): không gộp domain + CMS + redesign 1 đợt. Nếu buộc gộp → liệt kê từng thay đổi cộng dồn vào Findings, mỗi cái là 1 dòng rủi ro riêng. [owner: SEO] [blocker: yes]
- [ ] **Rollback criteria** viết ra giấy TRƯỚC launch (xem 3.5) + được stakeholder duyệt. [owner: SEO+Dev] [blocker: yes]
- [ ] Timeline kỳ vọng khai báo với stakeholder dạng **range có nguồn** (xem 3.6) — không hứa con số cứng. [owner: SEO] [blocker: yes]
- [ ] Freeze content: không rewrite/restructure content trong đợt migration (rủi ro cộng dồn — SKILL.md Anti-patterns). Nhu cầu refresh → xếp lịch SAU khi migration ổn định, route `content-refresh`. [owner: SEO] [blocker: no]

---

## 1. PRE

### 1.1 Benchmark

Snapshot có NGÀY — đây là baseline cho crawl parity + triage POST. Nguồn theo Path A/B/C (SKILL.md Input).

- [ ] Rankings: export rank tracker toàn bộ keyword đang track (position + URL). [owner: SEO] [blocker: yes]
- [ ] Traffic theo page: GSC Performance 3-12 tháng (clicks/impressions per page) + GA sessions. [owner: SEO] [blocker: yes]
- [ ] Backlinks theo page: Ahrefs Best by links / `site-explorer-pages-by-backlinks` — cột quyết định priority redirect map. [owner: SEO] [blocker: yes]
- [ ] Indexed count: GSC Coverage + sitemap indexed count. [owner: SEO] [blocker: yes]
- [ ] CWV baseline: LCP/CLS/INP field data (CrUX/GSC) — để so speed parity sau launch. [owner: SEO] [blocker: no]
- [ ] Conversions theo page (GA/CRM) nếu có — tier priority thứ 3 trong mapping. [owner: SEO] [blocker: no]

### 1.2 Full crawl site cũ

Theo Screaming Frog migration tutorial:

- [ ] Crawl full site cũ, bật integration: XML sitemap + GA + GSC → bắt **orphan pages** (page có traffic nhưng không có internal link). [owner: SEO] [blocker: yes]
- [ ] Bật crawl hreflang + structured data. [owner: SEO] [blocker: no]
- [ ] Lưu crawl bằng **database storage mode** — để dùng Compare mode sau launch. [owner: SEO] [blocker: yes]
- [ ] Export Internal tab (HTML, status 200, indexable) → base cho redirect map. [owner: SEO] [blocker: yes]

### 1.3 Dọn index pollution

Migration là cơ hội dọn index pollution — nhưng dọn bằng 410/noindex, KHÔNG dọn bằng redirect rác:

- [ ] Lọc pages zero-CTR / zero organic keywords nhiều tháng liên tục → đánh dấu KHÔNG map 1-1. [owner: SEO] [blocker: no]
- [ ] Quyết định per-page theo 4 methods (Ranking Signal Consolidation): (1) 301 với simple rules; (2) **410** cho page gone permanently; (3) 404 để SE tự kết luận; (4) 301 trước khi delete → delete → clean internal links → validate qua GSC. [owner: SEO] [blocker: no]
- [ ] ⚠️ Page có Historical Data quan trọng: Koray — delete page có HD để đổi tên+URL sẽ affect relevance + confidence (Google coi như page mới hoàn toàn). Nếu có thể: giữ URL, chỉ đổi content + name. [owner: SEO] [blocker: no]

### 1.4 Redirect mapping

Chi tiết đầy đủ (priority tiers, method theo scale, QA, template sheet): [redirect-mapping-method.md](redirect-mapping-method.md).

- [ ] Map 1-1 theo relevance — ❌ cấm bulk redirect về homepage (Google coi soft-404). [owner: SEO] [blocker: yes]
- [ ] Priority: pages có organic traffic → backlinks → conversions → còn lại (Aleyda checklist). [owner: SEO] [blocker: yes]
- [ ] Check backlinks trỏ về pages CHƯA có trong redirect map (Aleyda) — mọi page có backlink phải có dòng map. [owner: SEO] [blocker: yes]
- [ ] QA map trước launch: no chain, no loop, target 200 + indexable (xem redirect-mapping-method.md mục QA). [owner: SEO+Dev] [blocker: yes]

### 1.5 Staging audit

Có thể gọi `technical-seo-audit` làm bước con cho crawl health. Riêng migration-specific:

- [ ] Crawl staging: bypass robots.txt / HTTP auth / IP restriction (SF config). [owner: SEO] [blocker: yes]
- [ ] Check noindex/nofollow mà staging thường mang — lập danh sách để GỠ ngày launch. [owner: SEO+Dev] [blocker: yes]
- [ ] **URL Mapping trong SF Compare mode** (regex) map staging vs live → segment Added / New / Removed / Missing — Missing = pages sắp biến mất không chủ đích. [owner: SEO] [blocker: yes]
- [ ] Verify tracking (GA4/GTM) fire trên staging. [owner: Dev] [blocker: yes]
- [ ] Speed parity: staging không chậm hơn live đáng kể (CMS/design mới chậm hơn = nguyên nhân drop #5 SEJ). [owner: Dev] [blocker: no]
- [ ] Self-referencing canonical trên mọi template staging. [owner: Dev] [blocker: yes]

### 1.6 Server capacity

- [ ] ⚠️ Google crawl **NẶNG HƠN tạm thời** trong lúc move (Google site-move doc) → confirm server mới chịu được crawl spike + traffic thật cùng lúc. [owner: Dev] [blocker: yes]
- [ ] Log access sẵn sàng (để check 404/410 hits POST). [owner: Dev] [blocker: no]

---

## 2. DURING — launch day

- [ ] Deploy redirect rules: **301/308 server-side** — ❌ không 302/307, không JS redirect. Phát hiện 302 → convert ngay (Koray case: >1.500 redirects convert). [owner: Dev] [blocker: yes]
- [ ] 🔴 Gỡ MỌI staging block: noindex, robots.txt disallow, HTTP auth — lỗi phổ biến nhất Google liệt kê. [owner: Dev] [blocker: yes]
- [ ] ❌ KHÔNG block URL cũ bằng robots.txt — chặn signal transfer (Ranking Signal Consolidation). [owner: Dev] [blocker: yes]
- [ ] Verify **self-referencing canonical** trên mọi URL mới (spot-check per template) — canonical trỏ về URL CŨ = nguyên nhân drop #3 SEJ. [owner: SEO] [blocker: yes]
- [ ] Update hreflang annotations sang URL mới (nếu multi-lang). [owner: Dev] [blocker: yes nếu multi-lang]
- [ ] Submit **sitemap MỚI** sau khi redirects active; ưu tiên `sitemap_index.xml` phân theo category. [owner: SEO] [blocker: yes]
- [ ] **GIỮ sitemap cũ trong GSC** — theo dõi indexed count giảm dần về 0, KHÔNG gỡ sớm (Google site-move doc). [owner: SEO] [blocker: yes]
- [ ] **Change of Address** trong GSC — chỉ domain move; submit cho MỌI variant (www/non-www, subdomain). Không cần cho HTTP→HTTPS. [owner: SEO] [blocker: yes nếu domain move]
- [ ] Verify tracking fires trên production — SF custom search "does not contain" tracking tag. [owner: SEO+Dev] [blocker: yes]
- [ ] Spot-check **top-100 URL cũ** (theo traffic benchmark) bằng SF list mode: 301 → đúng target, 1 hop, target 200. [owner: SEO] [blocker: yes]
- [ ] Internal links trên site mới trỏ thẳng URL mới (không đi qua redirect). [owner: Dev] [blocker: no]

---

## 3. POST

### 3.1 Tuần 1 — cửa sổ cứu redirect sót

⚠️ Gary Illyes (Google): sau khi URL cũ chết không redirect, "you typically have a few weeks before most signals are lost" — cửa sổ cứu vãn là VÀI TUẦN, không vô hạn (Glenn Gabe, gsqi.com/marketing-blog/image-migrations-lost-signals/). Toàn bộ mục này chạy trong tuần 1.

- [ ] SF **list mode** upload TOÀN BỘ URL cũ + config "Always Follow Redirects" → export "All Redirects" report: chain (flatten về 1 hop — chain mất PageRank + crawl budget), loop, final status phải 200 + indexable. [owner: SEO] [blocker: yes]
- [ ] Crawl full site mới, verify indexability: không noindex sót, không robots block — nguyên nhân drop #2 SEJ. [owner: SEO] [blocker: yes]
- [ ] **Crawl parity**: SF Compare mode site mới vs baseline crawl cũ (1.2) — pages Missing, title/H1/content đổi ngoài chủ đích. [owner: SEO] [blocker: yes]
- [ ] 404/410 log check — target: **<50 hits/tháng cho 404, zero cho 410** (Status Codes wiki). [owner: SEO] [blocker: no]
- [ ] GSC: crawl errors mới, Coverage anomalies. [owner: SEO] [blocker: no]

### 3.2 Tuần 2-6 — coverage & transfer

- [ ] GSC Coverage: indexed count site mới tăng, sitemap cũ indexed count giảm dần → 0. Chỉ gỡ sitemap cũ khi về 0. [owner: SEO] [blocker: no]
- [ ] Impressions transfer: GSC Performance old property giảm ↔ new property tăng tương ứng. [owner: SEO] [blocker: no]
- [ ] "Indexed, though blocked by robots.txt" trong GSC phải = 0 (Robots.txt wiki). [owner: SEO] [blocker: no]
- [ ] Ranking key keywords vs benchmark 1.1 — đối chiếu triage matrix 3.4 trước khi kết luận. [owner: SEO] [blocker: no]
- [ ] CWV field data vs baseline — speed regression là nguyên nhân drop #5. [owner: SEO+Dev] [blocker: no]

### 3.3 Tháng 2-6 — Historical Data lens

- [ ] Giữ redirects **≥ 1 năm** — Google: "as long as possible, generally at least 1 year". Không ai được gỡ rule sớm. [owner: Dev] [blocker: yes]
- [ ] Đánh giá hiệu ứng đầy đủ của migration sau **~6 tháng** — 6-month lag rule (Koray verbatim: "If you lose your rankings today, it is because of the historical data from 6 months ago"). Ranking hôm nay sau migration phản ánh HD cũ; hậu quả migration lỗi cũng kéo dài ≥6 tháng. [owner: SEO] [blocker: no]
- [ ] Khung kỳ vọng nội bộ (SOP v1 Vincent — Historical Data wiki): Topical Coverage 1-3 tháng; HD accumulate 6-12 tháng; full Topical Authority 9-18 tháng — dùng khi nói chuyện client về kỳ vọng sau migration. [owner: SEO] [blocker: no]

### 3.4 Triage matrix + 6 nguyên nhân drop

🔴 **Bước 0 của mọi triage:** check ngày Google core update (Ahrefs traffic-drop SOP: ahrefs.com/blog/analyze-sudden-traffic-drop/) — drop trùng ngày core update ≠ drop do migration. Không check bước này thì mọi kết luận sau vô nghĩa.

Nguồn "SEJ migration-hangover" trong mục này: searchenginejournal.com/what-is-a-migration-hangover-traffic-drop-how-do-you-avoid-it/575102/ (Sophie Brannon, 06/2026). ⚠️ Các ngưỡng % và khung tuần là kinh nghiệm tác giả ("in my experience"), không phải study — dùng làm khung tham khảo, chỉnh theo dự án. Riêng dòng ">50% overnight = sự cố hệ thống" là convention GTV suy ra từ ngưỡng hangover ≥50% của bài, không phải verbatim SEJ.

| Drop % | Thời gian | GSC | Kết luận | Action |
|---|---|---|---|---|
| 10-20% | Ổn định, hồi trong 2-6 tuần | Sạch lỗi mới | **Normal** (SEJ migration-hangover) | Monitor weekly, không can thiệp |
| >30% | Bất kỳ | Crawl errors/404 mới, indexed giảm | **Migration hangover** (SEJ) | Điều tra ngay theo 6 nguyên nhân dưới; fix highest-traffic pages first |
| >50% | Overnight | Bất kỳ | Sự cố hệ thống | Escalate + chạy rollback decision tree 3.5 |
| Bất kỳ mức nào | >4 tuần không dấu hiệu ổn định | Bất kỳ | Hangover kéo dài (SEJ) | Full re-audit tuần-1 checklist + xét rollback criteria |

**6 nguyên nhân drop phổ biến nhất (SEJ, thứ tự check):**
1. 301 thiếu/gãy, dùng 302, chain, hoặc redirect về trang không liên quan.
2. **noindex sót từ staging.**
3. Canonical trỏ về URL cũ.
4. Content bị rewrite/mất element khi migrate (so crawl parity 3.1).
5. Page speed regression (CMS/design mới chậm hơn).
6. Đổi URL structure không cần thiết.

**Recovery steps ưu tiên (SEJ):** crawl site mới tìm lỗi → **fix highest-traffic pages first** → verify canonical + resubmit sitemap → confirm noindex không chặn key pages → restore content bị đổi nhiều.

### 3.5 Rollback decision tree (convention GTV)

⚠️ **Đây là khung quyết định GTV tự định — không có ngưỡng rollback chuẩn ngành.** Phải được định nghĩa + duyệt TRƯỚC launch (gate 0.2). Ngưỡng dưới là default, chỉnh theo dự án.

```
Drop >50% giữ nguyên sau 1 tuần?
├─ KHÔNG → tiếp tục fix theo 3.4, không rollback
└─ CÓ → Lỗi root-cause đã xác định được chưa?
    ├─ CÓ, vá được trong 48-72h → vá + monitor, không rollback
    └─ KHÔNG xác định được / lỗi hệ thống không vá nổi
        → Họp rollback: cân nhắc
          • Cost rollback = DOUBLE migration dưới mắt Google
            (đi rồi quay lại = 2 lần đổi signal)
          • Cửa sổ signal ~vài tuần (Gary Illyes) — quyết nhanh,
            để lâu rollback cũng không cứu được signal đã mất
          • Rollback chỉ hợp lệ khi hạ tầng cũ còn nguyên vẹn
```

### 3.6 Recovery timeline tham khảo (ước lượng — CÓ LABEL)

🔴 Bảng này là **range tham khảo, KHÔNG cam kết**. Mọi lần dùng phải kèm câu: *"phụ thuộc loại migration, chất lượng redirect map, và Historical Data hiện có."* Điều duy nhất nói chắc: Google xác nhận "temporary fluctuation là bình thường; site trung bình mất vài tuần để phần lớn pages chuyển index, site lớn lâu hơn" (Google site-move doc).

| Loại migration | Recovery ước lượng | Drop tạm ước lượng | Nguồn + độ tin |
|---|---|---|---|
| HTTP→HTTPS | 2-4 tuần | 5-15% | Whitehat SEO (whitehat-seo.co.uk/blog/web-migration-seo) — ⚠️ secondhand, độ tin thấp, chỉ dùng làm range có label |
| Design refresh giữ URL | 1-2 tuần | thấp | Whitehat SEO — như trên |
| CMS change | 4-8 tuần | 10-30% | Whitehat SEO — như trên |
| Domain migration | 6-18 tháng | 40-70% tạm thời | Whitehat SEO — như trên; nhất quán với 6-month lag rule (Historical Data wiki) |

⚠️ Con số "SEJ 2024 study: 892 domain migrations, average recovery 523 days, 17% never recover" chỉ thấy qua trích dẫn secondhand (Whitehat SEO), **chưa verify primary source** — chỉ dùng minh họa rủi ro, không bao giờ dùng làm fact cứng hay cam kết với client.
