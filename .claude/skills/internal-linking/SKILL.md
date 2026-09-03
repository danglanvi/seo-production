---
name: internal-linking
description: "Executable hóa lý thuyết internal linking của wiki Semantic SEO thành link plan cụ thể — DECISION layer cho link NỘI BỘ trong site, nhận topical map làm input, executable hóa Bước 20 SOP 01 (signals flow to Core) + audit SOP 03. Use when: (1) 'lên internal link plan cho [site]'."
metadata:
  version: "1.1"
---

# Internal Linking — Link Plan theo Semantic SEO

Biến lý thuyết internal linking trong wiki (Koray + GTV Extensions Rule 59-60) thành **link plan dạng bảng** cho một site: audit hiện trạng → đề xuất link mới/sửa link sai → anchor + vị trí + lý do có citation.
**Upstream:** nhận topical map từ `topical-map-creation` / `/seo-topical-map` (skill này executable hóa Bước 20 của `sop/01-topical-map.md` + audit của `sop/03-internal-linking.md`). **Downstream:** implementer đặt link theo plan; `/seo-onpage` verify lại ở audit tổng thể.

## Phân vai

| Việc | Skill |
|---|---|
| Internal link plan + audit link trong site | ✅ Skill này |
| Lọc URL báo PR + anchor plan textlink external | `textlink-analyzer` — tỷ lệ anchor external KHÔNG áp cho internal |
| Phân tích backlink profile đối thủ (DATA layer) | `backlink-research` |
| Kế hoạch backlink tổng target/anchor/method/velocity (DECISION layer external) | `backlink-plan` — giữ canonical `anchor-ratio-framework.md`, framework đó là cho EXTERNAL anchor |
| Tạo topical map từ đầu | `topical-map-creation` / `/seo-topical-map` — skill này NHẬN topical map, không tạo |
| Luật internal link EXECUTION (anchor rules, position, threshold, link plan) | ✅ Skill này = **CANONICAL owner** — `topical-map-creation` chỉ dùng lớp planning (thiết kế link architecture trong map), không giữ luật execution |
| Onpage audit tổng thể (OP1-OP55) | `/seo-onpage` — skill này chỉ audit lớp link |

## Input

**Required:**
- `$TOPICAL_MAP` — topical map của site (file/paste): Core Section vs Outer Section, pillar page mỗi cluster, danh sách page theo cluster. Không có topical map chuẩn → chấp nhận `$URL_LIST` + cluster mapping (user gán mỗi URL vào cluster + đánh dấu pillar), flag "cluster mapping do user cung cấp, chưa verify với topical map".

**Optional:**
- `$DOMAIN` — domain để pull data hiện trạng (Path A/B).
- `$SCOPE` — giới hạn 1-vài cluster thay vì toàn site.
- `$INTENT_MAP` — nhãn intent per page (Info / Commercial / Transactional) — có thì bật check Intent Funnel; không có thì suy từ page type + flag.
- `$NEW_PAGES` — danh sách bài vừa publish (burst) cần nối link ngay theo checklist SOP 03.

**Path detection (data link hiện trạng):**
- **Path A (ưu tiên)** — Ahrefs MCP: `site-explorer-pages-by-internal-links` (inbound count per page) + `site-explorer-linked-anchors-internal` (anchor hiện trạng). ⚠️ Caveat: data là crawl của Ahrefs (không phải Site Audit project), độ phủ có thể thấp hơn full crawl Screaming Frog — ghi rõ trong output.
- **Path B** — user cung cấp Screaming Frog export (`all_inlinks.csv` hoặc tương đương): source, target, anchor, vị trí (content/navigation).
- **Path C (đường lùi cuối)** — chỉ có topical map, không có data link: skill vẫn chạy, output là **plan lý thuyết** (bỏ phần audit hiện trạng, mọi anchor là "candidate — verify khi content live").

## Workflow

### Bước 0 — Scope & gate
- Xác nhận: domain/scope, path data (A/B/C), có `$INTENT_MAP` không, deliverable trả về đâu.
- 🔴 Nếu dùng Ahrefs MCP: báo trước **số call dự kiến** (thường 2 call/scope: pages-by-internal-links + linked-anchors-internal; thêm call nếu chia nhỏ theo folder) — **chờ Vincent xác nhận** rồi mới gọi.
- Gate routing: nếu yêu cầu thật ra là textlink báo/external hoặc backlink → dừng, route theo bảng Phân vai.

### Bước 1 — Dựng bản đồ cluster / Contextual Border từ topical map
- Từ `$TOPICAL_MAP` xác định: **Core Section** (money/conversion) vs **Outer Section** (informational), pillar page mỗi cluster, cluster boundary = **Contextual Border**, page nào đóng vai **Contextual Bridge** giữa 2 cluster.
- Map sang cấu trúc SCN: **Root ↔ Homepage; Seeds ↔ Root; Nodes ↔ Seed; node-node cross-seed và seed-seed được phép** ([[Semantic Content Network]] §Types of Webpages). Ghi rõ page nào là Root/Seed/Node.
- Xác định **Quality Nodes** (3-5 page link trực tiếp từ main content homepage — `sop/01` Bước 13) và **Trending Nodes** (bắt buộc bridge về Core, không đứng riêng — Bước 14).
- ⚠️ Định nghĩa Contextual Border/Bridge lấy từ wiki page tương ứng ([[Contextual Border]], [[Contextual Bridge]]) — nếu wiki chưa có page đầy đủ, dùng mô tả trong `sop/03` và flag trong output.
- **Owned truth pages — lớp G2 GEO (bổ sung 29/08/2026):** đánh dấu trong map các trang là **nguồn sự thật của brand** — about/giới thiệu · pricing/báo giá · FAQ · docs/chính sách · đại lý/địa điểm · trang tác giả. AI engine verify brand bằng fan-out `site:domain [câu hỏi thương mại]` (64% fan-out có `site:`, Nectiv 08/2026) → các trang này phải (a) **được link từ main content của homepage/pillar** (không chỉ footer — footer là weak signal), (b) nhận anchor mô tả đúng câu hỏi ("bảng giá dịch vụ SEO 2026", không "xem thêm"), (c) không orphan. Test nhanh: 5-10 câu khách hay hỏi → mỗi câu có 1 trang trả lời được bằng text và trang đó có ≥1 inbound từ pillar liên quan. Thiếu trang → flag "G2 gap" cho content (`sop/04` lớp GEO), không phải việc của link plan.
- Output trung gian: bảng `cluster | pillar | pages | role SCN | border/bridge | truth page?` — show cho user duyệt trước khi sang Bước 2.

### Bước 2 — Audit hiện trạng (Path A/B; Path C bỏ qua, ghi chú)
Phát hiện theo đúng threshold có nguồn (citation map [references/link-plan-template.md](references/link-plan-template.md) §3):
- [ ] **Orphan pages** — định nghĩa operational: 0 inbound internal link từ main content. ⚠️ Đây là convention của skill (SOP 03 không cho ngưỡng số) — flag rõ trong output. Fix: inbound từ pillar (`sop/03` §Audit).
- [ ] **Over-linked pillar** — 🔴 đúng scope nguồn: **quá 50 inbound TỪ CÙNG CLUSTER** (per-cluster, KHÔNG phải tổng sitewide) → đề xuất consider sub-pillar (`sop/03` §Audit).
- [ ] **Cross-cluster link không qua bridge** — link vượt Contextual Border mà không đi qua Contextual Bridge → fix hoặc tạo bridge.
- [ ] **Page vượt <150 internal links** (mobile = desktop bắt buộc) — [[Internal Linking Rules and Strategy]] §Core Rules.
- [ ] **Mobile-desktop parity** — Path A/B có data thì verify; Path C ghi chú cho implementer.
- [ ] **First link + first anchor trong Main Content** mỗi page quan trọng — heaviest relevance signal, audit xem có trỏ đúng target quan trọng nhất không.
- [ ] **Link tồn dư sau delete/301** — link tới page đã xóa/redirect phải clean ([[Ranking Signal Consolidation]] §4 Methods (Bloating Fix) #4).
- [ ] `$NEW_PAGES` có → check checklist bài mới: ≥1 link tới pillar, 2-5 link tới siblings, pillar đã link ngược lại chưa ("Momentum without linking = wasted").

### Bước 3 — Đề xuất link plan (structure + direction)
Mọi link đề xuất phải tuân direction rules bất biến:
- 🔴 **Signals flow TO Core** (Golden Rule #4, `sop/01` Bước 20): Outer→Core, Trending→Core, Home→Quality→Core. Link flow target = trang quan trọng hơn; PageRank flow follow link flow ([[Link Flow]]).
- 🔴 **Pillar ↔ cluster pages: bidirectional. Cluster ↔ cluster: chỉ qua bridge page** (`sop/03` §Nguyên tắc).
- 🔴 **Intent Funnel forward-only**: Info → Commercial → Transactional, không skip layer (Info → Transactional trực tiếp = intent jump). Reverse chỉ cho breadcrumb / related widget. Exception: Hybrid Intent Page — main section link → page riêng cho secondary intent.
- **Rule 60 — Knowledge Domain Expansion Path**: mỗi outbound link cách source **tối đa 1 semantic step**; buộc link cross-domain xa → chèn annotation text giải thích bridge (chi tiết + ví dụ chain: [references/anchor-rules.md](references/anchor-rules.md)).
- **Chọn target theo Rule 59 — Semantic Distance**: ưu tiên page gần về semantic distance (shared process/attributes) hơn gần bề mặt topical/geographic — 3 phương pháp đo trong references.
- **Nesting vs Connecting** (SCN Rule 10): connecting = nối similar things theo contextual domain; nesting = gộp content cùng purpose vào cùng crawl path — phân loại mỗi link đề xuất thuộc kiểu nào.
- **Nhánh KHÔNG link (Link-less Connection — GTV)**: 2 page cùng site share entities + context → Contextual Vector tự connect. Để no-link khi ĐỦ 1 trong 4: (1) không có semantic lead-in tự nhiên, (2) distance đã min, (3) link phá reading flow, (4) contextual vector đã đủ. Chỉ link khi: user journey rõ + anchor có natural lead-in + target là quality/conversion node cần PageRank + vị trí post-answer/Supplementary. ⚠️ Quantifier "đủ cả 4"/"≥1" là convention của skill — wiki chỉ liệt kê điều kiện, không quy định số lượng. Output ghi recommendation `no-link, rely on contextual vector` cho các cặp này.

### Bước 4 — Anchor + vị trí gợi ý
Mỗi link đề xuất sinh anchor theo [references/anchor-rules.md](references/anchor-rules.md):
- ⚠️ Evidence note (2026-07-13): các position/count rules trong bước này = **GTV/Koray operating default** (`practitioner_framework`), không phải rule Google — override được khi có lý do, ghi chú trong plan (chi tiết: evidence note đầu references/anchor-rules.md).
- 🔴 Anchor phải pass **6/6 Anchor Text Rules** — đặc biệt rule 6: anchor tồn tại trong target page content + heading liên quan của source. Path C chưa có content → anchor chỉ là "candidate", flag `verify-anchor`; rule 4 (competitor anchors) không kiểm được ở Path C → flag `competitor-anchor-pending`, không tính vào 6/6.
- Anchor = **seed query của target page**; ≤3 lần cho 1 anchor text; có **semantic lead-in** ở đoạn trước; annotation text quanh anchor với N-gram variants; anchor match intent destination (Commercial = modifier "so sánh/top"; Transactional = action verb "mua/đăng ký").
- **Vị trí gợi ý** tôn trọng position rules:
  - ❌ Top-10 headings: 0 link — exception duy nhất: grouper page/hypernym có strong lexical relation, phải flag `grouper-exception`.
  - ❌ First paragraph, ❌ trước definition — link đặt **post-answer** (sau khi đã trả lời câu hỏi).
  - Max **1 link per heading section** (ngoại lệ: section dạng list entities cùng type → link từng page, flag `list-exception` — anchor-rules §3 #6 thắng #5); distance giữa 2 link **≥1 heading** trong Main Content (bottom/Supplementary được gần hơn).
  - Side-topic/khác context → chỉ link từ **last heading's paragraphs**; Supplementary Content đặt bottom + lower heading hierarchy để giảm prominence.
  - ❌ Không đề xuất link ở footer/sidebar/boilerplate (weak signal — [[Internal Linking Rules and Strategy]] §Core Rules; `sop/01` Bước 13 cho Quality Nodes homepage).
- Multi-link cùng target trong 1 doc: link thứ 1 pass PageRank + relevance, link thứ 2+ chỉ pass relevance → mặc định 1 link/target/doc, link thứ 2 phải có lý do riêng.

### Bước 5 — Render output + báo cáo
- Render theo schema [references/link-plan-template.md](references/link-plan-template.md): bảng link plan + audit findings + summary counts + rule-ID citation map.
- Báo cáo cho Vincent: số link đề xuất / số fix / số no-link candidate / các flag cần quyết định (grouper-exception, sub-pillar, tạo bridge mới).
- 🔴 Skill chỉ **output plan** — không tự sửa site, không tự đặt link, không sửa content.

> **Threshold có nguồn (KHÔNG chế thêm):** Koray verbatim — *"There is no specific, and optimum internal link count for a specific content piece"* — no magic number (paraphrase, [[Internal Linking Rules and Strategy]] §Internal Links & Initial Ranking). Mọi con số trong skill lấy DUY NHẤT từ Rule ID citation map: [references/link-plan-template.md](references/link-plan-template.md) §3.

## Output

Convention đặt tên file: `<project>_Internal-Link-Plan_v1.md` → trả về tài liệu nội bộ «<project>» (ngoài repo, hỏi Lead/Vincent) (tăng `_v2` nếu trùng). Skeleton deliverable:

```markdown
# Internal Link Plan — <domain> (<date>)
Data path: A Ahrefs MCP / B Screaming Frog / C theory-only · Scope: <clusters> · Data date: <date>
⚠️ Caveats: <Ahrefs coverage / cluster mapping user-provided / Path C anchor = candidate…>

## 1. Bản đồ cluster
| Cluster | Pillar | Pages | Role SCN | Border/Bridge |
|---|---|---|---|---|

## 2. Audit findings (Path A/B)
- Orphan pages (convention: 0 inbound main-content): …
- Over-linked pillar (>50 inbound từ cùng cluster): …
- Cross-cluster bypass bridge: … · Pages ≥150 links: … · Mobile-desktop mismatch: …
- First-anchor issues: … · Link tồn dư sau 301/delete: …

## 3. Link plan
| # | Source URL | Target URL | Vị trí gợi ý (section) | Anchor đề xuất | Direction type | Lý do (rule ID) | Flag |
|---|---|---|---|---|---|---|---|

## 4. No-link candidates (rely on contextual vector)
| Cặp page | Điều kiện Link-less thỏa | Ghi chú |
|---|---|---|

## 5. Summary
Links đề xuất: N · Fix: N · No-link: N · Flags chờ quyết định: …

## 6. Rule ID → citation
(theo references/link-plan-template.md)
```

## Behavior Gates

1. **🔴 Think Before** — chưa đủ topical map/cluster mapping hoặc mơ hồ Core vs Outer → hỏi, không tự gán. MCP call phải báo số call + chờ xác nhận.
2. **🔴 Evidence** — mọi con số trong plan truy được về rule ID + nguồn (citation map `references/link-plan-template.md` §3) + ngày data pull. Link không giải thích được connection = không đề xuất (Cautious/Reasonable Surfer principle). Không có dòng plan nào thiếu cột "Lý do".
3. **🔴 Surgical** — chỉ output plan; không tự sửa site/content, không đụng external anchor framework của `backlink-plan`, không sửa topical map (phát hiện topical map có vấn đề → note 1 dòng, không tự refactor).
4. **🔴 Goal-driven** — link phục vụ flow to Core + user journey + crawl path, không phục vụ số lượng. Quality + necessity > quantity; ưu tiên cluster/page theo business impact khi phải chọn scope.

## Anti-patterns

- ❌ Chế ngưỡng không nguồn ("tối ưu 20-30 link/bài", "mỗi bài 5 internal link") — Koray: no magic number.
- ❌ Đọc ">50 inbound" thành tổng sitewide — nguồn là **từ cùng cluster**.
- ❌ Anchor generic "xem tại đây", "click here", "tại đây".
- ❌ Link ở top-10 headings không flag grouper-exception; link ở first paragraph / trước definition.
- ❌ Đề xuất link footer/sidebar/boilerplate làm link chiến lược.
- ❌ Skip intent layer (Info → Transactional trực tiếp).
- ❌ Áp tỷ lệ anchor external (Brand/Partial/Exact…) của backlink-plan/textlink-analyzer cho internal.
- ❌ Force link khi Link-less Connection đủ điều kiện — internal alignment > internal linking.
- ❌ Tự trả lời Open Questions của wiki bằng số bịa (patent number Cautious Surfer, I-node vs C-node weight ratio, annotation text optimal length, link count per intent layer).
- ❌ Link tới research papers/studies bằng internal anchor chiến lược (Koray: đừng link research papers).

## References & wiki

- [references/anchor-rules.md](references/anchor-rules.md) — 6 Anchor Text Rules + anchor mechanics + Rule 59 + Rule 60 + intent-anchor mapping.
- [references/link-plan-template.md](references/link-plan-template.md) — schema bảng output + rule-ID citation map (nguồn threshold duy nhất, §3) + ghi chú 3 Path.
- `topical-map-creation/references/internal-linking-guide.md` — bản planning-time khi thiết kế map; luật execution canonical ở skill này.
- Wiki: [[Internal Linking Rules and Strategy]] (nguồn luật chính — status draft nhưng dày nhất) · [[Link Flow]] · [[Semantic Content Network]] · [[Pillar Cluster Page]] · [[Ranking Signal Consolidation]] · [[Contextual Bridge]] · [[Contextual Border]]
- SOP: `sop/01-topical-map.md` (Bước 13-14, 20 + Golden Rule #4) · `sop/03-internal-linking.md` (⚠️ status stub — chỉ dùng làm nguồn threshold pillar/cluster, luật chính theo wiki concept page).

## Changelog

- **v1.0.1 (2026-07-07):** vá theo spot-run trên topical map GTV thật — tuyên precedence 4 chỗ 2-luật-giao-nhau: LLC gate chỉ áp link tùy nghi (link cấu trúc sop/03 miễn gate); list entities cùng type = ngoại lệ hợp lệ của max-1-link/heading (flag `list-exception`); AR4 competitor anchors per path (Path C → `competitor-anchor-pending`); intent-anchor: ưu tiên seed query hơn ép modifier khi 2 luật kéo 2 hướng.
- **v1.0 (2026-07-07):** khởi tạo — executable hóa [[Internal Linking Rules and Strategy]] (Koray Core Rules + SCN Case Study Rules + GTV Extensions Rule 59-60 + Intent Funnel + Link-less Connection), `sop/01-topical-map.md` Bước 13-14/20, `sop/03-internal-linking.md` (pillar-cluster-bridge + audit thresholds), [[Link Flow]], [[Semantic Content Network]], [[Pillar Cluster Page]], [[Ranking Signal Consolidation]].
