---
name: internal-linking
description: "Executable hóa lý thuyết internal linking của wiki Semantic SEO thành link plan cụ thể — DECISION layer cho link NỘI BỘ trong site, nhận topical map làm input, executable hóa Bước 20 SOP 01 (signals flow to Core) + audit SOP 03. Use when: (1) 'lên internal link plan cho [site]'."
metadata:
  version: "1.4.2"
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
| Ghi link plan đã duyệt lên WordPress có quyền server | `wp-content-review-apply` (qua trang duyệt). Chọn đoạn đặt link hàng loạt: tuỳ chọn Jev `link-bridge` theo `tools/ai-assist/README.md`, Claude chọn chỗ đặt |
| Kiểm vị trí link hàng loạt (MC hay SC, đúng ngữ cảnh) | ✅ Skill này, theo [references/link-placement.md](references/link-placement.md). Rubric Jev `link-placement`, `link-bridge` chạy qua `tools/ai-assist/` (`tools/ai-assist/README.md` §4) |
| Chọn dạng mã của link: link thật `<a href>` hay link JS (onclick) cho nút chuyển đổi, menu, footer, link ngoài làm bằng chứng, filter trang danh mục ecommerce | ✅ Skill này, theo [references/link-js.md](references/link-js.md). Rubric Jev `link-purpose` gắn mục đích (`tools/ai-assist/tasks/link-purpose.json`) |
| Sửa link trong thẻ duyệt hoặc bản nháp, kiểm kê dạng mã, tìm đoạn cầu nối, chọn anchor từ query GSC | ✅ Skill này, bằng 4 script trong `scripts/` theo [references/scripts.md](references/scripts.md). Embedding đoạn do `site-vector-index` làm |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | `link-placement` (vùng, độ hợp, nhu cầu), `link-bridge` (đoạn ứng viên cầu nối), `link-purpose` và `link-external` (mục đích phần tử bấm được) qua `tools/ai-assist/` | Dùng. Ngưỡng ở `link-placement.md` §5 và `link-js.md` §6 |
| EmbeddingGemma 2 | Tìm đoạn gần trang đích nhất trên toàn site, qua `svi.py query --level passage --per-url` của `site-vector-index` | Dùng ở Bước 4b. Không dùng cho dạng mã (`link-js.md` §6 ghi lý do). Không dùng chọn anchor: luật 6 cần chữ có thật trong trang, script khớp chuỗi |
| GLM Flash | Trích câu, diễn giải tự do | Không dùng. Skill không có việc mà Jev không làm được |
| Script tất định | Đếm R1–R3, kiểm kê dạng mã, lọc đoạn ứng viên, khớp query GSC với chữ trang | Dùng 4 script trong `scripts/`. Script không gọi Jev hay Gemma |
| Claude | Chọn đích và vùng, chọn anchor, đọc dòng Jev dưới ngưỡng, quyết dạng mã, viết câu cầu nối | Dùng |

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

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,screaming-frog?,jev?,gemma?,gsc?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Bốn script trong `scripts/` chỉ cần Python stdlib. `gemma` chỉ cần khi tìm đoạn cầu nối ở Bước 4b. `gsc` chỉ cần khi chưa có file GSC cho Bước 4.

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
- [ ] `$NEW_PAGES` có → check checklist bài mới: ≥1 link tới pillar, link tới sibling cùng seed khi có ngữ cảnh chung (không quota), pillar đã link ngược lại chưa ("Momentum without linking = wasted").

### Bước 3 — Đề xuất link plan (structure + direction)
Mọi link đề xuất phải tuân direction rules bất biến:
- 🔴 **Vị trí theo topical map** (Vincent chốt 18/10/2026): trục root → seed → node (topic cluster: pillar ↔ cluster page) được đặt ở MC. Link khác cụm, link Outer → Core và link thương mại đặt ở SC. Bảng quan hệ → vùng: [references/link-placement.md](references/link-placement.md) §3.
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
- Trang đích có dữ liệu GSC: lấy query ứng viên bằng `python3 skills/internal-linking/scripts/anchor_gsc.py gsc.json --page <đích> --target-file <trang đích> --source-file <bài nguồn> --section "<H2>"`. Script gắn cờ luật 1, 2, 6, ≤3 lần và query thuộc trang khác. Claude chọn anchor từ dòng `dat` ([references/scripts.md](references/scripts.md) §4).
- **Vị trí gợi ý** tôn trọng position rules:
  - 🔴 Mặc định đặt ở Supplementary Content. Main Content chỉ nhận 5 trường hợp MC1–MC5 ([references/link-placement.md](references/link-placement.md) §2), ghi mã vào cột `Vùng`. Đoạn chứa link phải nói về chủ đề chính của trang đích. Link sai ở MC thì bỏ, không đổi đích sang trang dịch vụ.
  - Trang chuyên mục: đoạn dưới mô tả chỉ link xuống seed của chuyên mục; link khác cụm và link dịch vụ đặt ở khối cuối trang.
  - ❌ Top-10 headings: 0 link — exception duy nhất: grouper page/hypernym có strong lexical relation, phải flag `grouper-exception`.
  - ❌ First paragraph, ❌ trước definition — link đặt **post-answer** (sau khi đã trả lời câu hỏi).
  - Max **1 link per heading section** (ngoại lệ: section dạng list entities cùng type → link từng page, flag `list-exception` — anchor-rules §3 #6 thắng #5); distance giữa 2 link **≥1 heading** trong Main Content (bottom/Supplementary được gần hơn).
  - Side-topic/khác context → chỉ link từ **last heading's paragraphs**; Supplementary Content đặt bottom + lower heading hierarchy để giảm prominence.
  - ❌ Không đề xuất link ở footer/sidebar/boilerplate (weak signal — [[Internal Linking Rules and Strategy]] §Core Rules; `sop/01` Bước 13 cho Quality Nodes homepage).
- Multi-link cùng target trong 1 doc: link thứ 1 pass PageRank + relevance, link thứ 2+ chỉ pass relevance → mặc định 1 link/target/doc, link thứ 2 phải có lý do riêng.

### Bước 4c — Chọn dạng mã: link thật hay link JS
- Kiểm kê hiện trạng bằng `python3 skills/internal-linking/scripts/link_code_audit.py scan <thư mục HTML> --host <domain> --out <dir>`, không kiểm kê tay. Sau khi sửa template trên staging, chạy `compare` trước và sau. Lệnh thoát 3 khi link thật ở body giảm ([references/scripts.md](references/scripts.md) §2).
- Mỗi link và mỗi nút bấm được nhận một mã D1–D6 theo [references/link-js.md](references/link-js.md) §2. Ghi mã vào cột `Dạng mã`.
- Ngữ cảnh quyết định dạng mã. Link hợp ngữ cảnh giữ `<a href>` (D1), kể cả CTA. Link JS chỉ dùng cho link giữ lại để tăng chuyển đổi ở vị trí ngữ cảnh không cần link (D3), link phụ lặp ở header và footer (D4), link ngoài làm bằng chứng và mạng xã hội (D5). Trích nguồn trong thân bài (D6) nêu tên nguồn bằng chữ, không đặt link.
- Trước khi đề xuất link JS, kiểm trang đích còn link thật từ trang mẹ cùng chủ đề và còn trong XML sitemap (§3 luật 2).
- Trang danh mục ecommerce: filter có search demand làm trang đích riêng và nhận link thật. Filter không có demand và nút sắp xếp dùng checkbox hoặc button, không sinh URL mà Google thấy. Link sản phẩm, phân trang và breadcrumb giữ link thật ([references/link-js.md](references/link-js.md) §7, theo phân tích faceted navigation của Koray).
- Ưu tiên sửa template lặp toàn site (§4). Không đổi link lẻ trong bài chỉ để đổi dạng mã.
- Ghi trong plan: đây là khung thực hành của Koray, không phải luật Google. Không hứa tăng thứ hạng.

### Bước 4b — Kiểm vị trí bằng Jev (plan hoặc đợt thẻ từ 20 link)
- Chạy rubric `link-placement`, rồi `link-bridge` cho link cần chuyển xuống SC, theo [references/link-placement.md](references/link-placement.md) §5. Claude đọc mọi dòng dưới ngưỡng.
- Thiếu key Jev (`tools/ai-assist/README.md` §5): Claude đọc từng link theo §1–4 của reference và ghi giới hạn trong output.
- Tìm đoạn đặt contextual bridge (trang tiền mới, hoặc link phải chuyển xuống SC): chạy `bridge_candidates.py queries`, rồi `svi.py query --level passage --per-url` của `site-vector-index`, rồi `bridge_candidates.py build` (thêm `--sc-only` khi chuyển xuống SC), Jev `link-bridge`, `bridge_candidates.py merge`. Claude chọn trong các dòng `dat` ([references/scripts.md](references/scripts.md) §3).
- Không có store của `site-vector-index`: Claude đọc các đoạn SC của trang nguồn theo `link-placement.md` §5 bước 4 và ghi giới hạn.

### Bước 4d — Sửa link trong thẻ duyệt hoặc bản nháp
- Gỡ link, đổi anchor hoặc chuyển link xuống SC bằng `python3 skills/internal-linking/scripts/the_link.py unlink|reanchor|to-sc`, rồi `check --base <bản trước>` ([references/scripts.md](references/scripts.md) §1).
- Chạy không có `--write` trước và đọc diff. Ghi bằng `--write`, script tạo bản `.bak`.
- Nếu script thoát 3, lần sửa sinh vi phạm R1–R3 mới và script không ghi. Sửa thẻ, không ép ghi.
- Script chỉ sửa file thẻ hoặc bản nháp. Ghi lên site vẫn qua `wp-content-review-apply`.

### Bước 5 — Render output + báo cáo
- Render theo schema [references/link-plan-template.md](references/link-plan-template.md): bảng link plan + audit findings + summary counts + rule-ID citation map.
- Báo cáo cho Vincent: số link đề xuất / số fix / số no-link candidate / các flag cần quyết định (grouper-exception, sub-pillar, tạo bridge mới).
- 🔴 Skill chỉ **output plan** — không tự sửa site, không tự đặt link, không sửa content.

> **Threshold có nguồn (KHÔNG chế thêm):** Koray verbatim — *"There is no specific, and optimum internal link count for a specific content piece"* — no magic number (paraphrase, [[Internal Linking Rules and Strategy]] §Internal Links & Initial Ranking). Mọi con số trong skill lấy DUY NHẤT từ Rule ID citation map: [references/link-plan-template.md](references/link-plan-template.md) §3.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Mọi link ở MC có mã MC1–MC5. Link sai ở MC bị bỏ hoặc chuyển xuống SC, không đổi đích sang trang dịch vụ. Nguồn lỗi: audit 161 link trên một site WordPress, 18/10/2026.
- [ ] Link sửa trong thẻ đã qua `the_link.py check` và không sinh vi phạm R1–R3 mới. Nguồn lỗi: helper sửa link ad hoc gãy vì `&amp;`, `<span>` lồng trong `<a>`, href tuyệt đối, 18/10/2026.
- [ ] Bảng dạng mã lấy từ `link_code_audit.py scan`. Lần sửa template có `compare` trước và sau, link thật ở body không giảm. Nguồn lỗi: kiểm kê tay 19/10/2026 phải dò lại dạng lai, `href="#"` mở menu, span thiếu role.
- [ ] Mỗi CTA được xét theo ngữ cảnh. CTA hợp ngữ cảnh giữ link thật (D1). Nguồn lỗi: Vincent sửa luật chiều 19/10/2026 (v1.3.2), sau bản chọn dạng mã theo loại phần tử.
- [ ] Đoạn cầu nối gửi Jev đã bỏ mở bài, khối template và trang đã link tới đích. Gemma chạy một tiến trình qua `svi.py query`. Nguồn lỗi: 17/10 và 18/10/2026 dựng pipeline cầu nối 2 lần, nạp lại model mỗi khối.
- [ ] Plan không đặt quota số link. Bài link tới sibling chỉ khi đoạn có ngữ cảnh chung. Nguồn lỗi: v1.3.1, 19/10/2026 bỏ quota 2–5 link tới sibling.

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
| # | Source URL | Target URL | Vị trí gợi ý (section) | Vùng (SC / MC1–MC5) | Quan hệ map | Dạng mã (D1–D6) | Anchor đề xuất | Direction type | Lý do (rule ID) | Flag |
|---|---|---|---|---|---|---|---|---|---|---|

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
- ❌ Link thương mại hoặc link khác cụm ở MC chỉ vì đoạn có cụm từ trùng anchor.
- ❌ Đổi đích link sai ở MC sang trang dịch vụ để giữ link. Bỏ link, hoặc chuyển xuống SC.
- ❌ Đoạn dưới mô tả chuyên mục link sang cụm khác.
- ❌ Giấu link chủ đề trong thân bài bằng onclick, hoặc giấu đường crawl duy nhất tới một trang index.
- ❌ Dùng dạng lai `<a href="…" onclick="…">`, `<a href="javascript:…">`, hoặc dùng nofollow để giữ PageRank.
- ❌ Đổi link JS hàng loạt trên site đang chạy mà không qua staging và không kiểm sự kiện đo lường.
- ❌ Sửa link trong thẻ bằng regex thô hoặc `assert count == 1`. Ghi thẻ khi `the_link.py` thoát 3.
- ❌ Kiểm kê dạng mã bằng tay, hoặc sửa template mà không `compare` số link thật trước và sau.
- ❌ Chia lô và nạp lại Gemma cho từng lô khi tìm đoạn cầu nối. Gửi Jev đoạn mở bài hoặc đoạn trên trang đã link tới đích.
- ❌ Lấy query GSC có nhiều click nhất làm anchor mà không kiểm chữ có trong trang đích và query có thuộc trang khác không.

## References & wiki

- [references/anchor-rules.md](references/anchor-rules.md) — 6 Anchor Text Rules + anchor mechanics + Rule 59 + Rule 60 + intent-anchor mapping.
- [references/link-plan-template.md](references/link-plan-template.md) — schema bảng output + rule-ID citation map (nguồn threshold duy nhất, §3) + ghi chú 3 Path.
- [references/link-placement.md](references/link-placement.md) — vị trí link: 5 trường hợp được đặt ở MC, quan hệ topical map → vùng, cách xác định MC/SC, kiểm hàng loạt bằng Jev.
- [references/link-js.md](references/link-js.md) — dạng mã: link thật hay link JS theo ngữ cảnh (D1–D6), link ngoài, luật đường crawl, bàn phím, đo lường, mẫu từ site Koray.
- [references/scripts.md](references/scripts.md) — lệnh, cờ, mã thoát và giới hạn của 4 script: `the_link.py`, `link_code_audit.py`, `bridge_candidates.py`, `anchor_gsc.py`.
- `topical-map-creation/references/internal-linking-guide.md` — bản planning-time khi thiết kế map; luật execution canonical ở skill này.
- Wiki: [[Internal Linking Rules and Strategy]] (nguồn luật chính — status draft nhưng dày nhất) · [[Link Flow]] · [[Semantic Content Network]] · [[Pillar Cluster Page]] · [[Ranking Signal Consolidation]] · [[Contextual Bridge]] · [[Contextual Border]]
- SOP: `sop/01-topical-map.md` (Bước 13-14, 20 + Golden Rule #4) · `sop/03-internal-linking.md` (⚠️ status stub — chỉ dùng làm nguồn threshold pillar/cluster, luật chính theo wiki concept page).

## Changelog

- **v1.4.2 (2026-10-29):** `link-js.md` §2: bước 1 đổi "bỏ link" thành "đổi sang D3 nếu có ích cho người đọc, chỉ bỏ link trùng và vô ích"; bước 2 thêm đổi anchor kém sang query GSC; D2 dùng `<button data-scroll-to>`, nút giữa câu dùng `<span role="button">`. Nguồn: ghi chú Excel duyệt link site agency mẫu 28/10/2026, Q2 trang quyết, lane /dao-tao-seo/ 29/10 (button giữa câu làm câu ngắt dòng khác).

- **v1.4.1 (2026-10-27):** hợp nhất bản root 27/10/2026: khôi phục rubric Jev `link-purpose`, `link-external` ở bảng Phân vai, bảng Phân việc model và `link-js.md` §6 (2 rubric đã có trong `tools/ai-assist/tasks/`); chép `evals/cases.yaml` 13 ca, tên site thật đổi thành "site agency mẫu".
- **v1.4 (2026-10-25):** đề xuất nd-10. Thêm 4 script stdlib có test offline (`the_link.py`, `link_code_audit.py`, `bridge_candidates.py`, `anchor_gsc.py`), `references/scripts.md`, Bước 4d, bảng Phân việc model, mục Tự phản biện, 4 anti-pattern; trỏ script ở Bước 4, 4b, 4c và trong `link-js.md`, `link-placement.md`, `anchor-rules.md`.
- **v1.3.3 (2026-10-19):** thêm `link-js.md` §7 cho trang danh mục ecommerce theo phân tích faceted navigation của Koray (case 3 triệu URL → 47 URL): filter có demand làm trang đích, link thật; filter không demand, sắp xếp dùng checkbox/button, không sinh URL Google thấy; link sản phẩm, phân trang giữ link thật; 7 luật (không `onclick` chứa URL, không robots.txt + noindex cùng URL, gộp 301/410 trước khi chặn).
- **v1.3.2 (2026-10-19):** Vincent chốt chiều 19/10: ngữ cảnh quyết định dạng mã. CTA hợp ngữ cảnh giữ link thật (D1). Link JS chỉ cho link giữ lại để tăng chuyển đổi ở vị trí ngữ cảnh không cần link, link phụ lặp, link ngoài làm bằng chứng và đích noindex. `link-js.md` §2 thêm 3 bước chọn, sửa dòng D1, D3, luật 1, §4, §6; `link-placement.md` sửa dòng MC4.
- **v1.3.1 (2026-10-19):** bỏ quota 2-5 link tới sibling ở Bước 2, `anchor-rules.md` và citation map; bài link tới sibling khi đoạn có ngữ cảnh chung. `link-js.md` ghi P18 của `seo-onpage` đã theo D6.
- **v1.3 (2026-10-19):** Vincent chốt luật dạng mã của link sau khi agent đọc mã nguồn morethanpanel.com và sutliffstout.com của Koray. Thêm `references/link-js.md` (D1–D6: link thật cho link chủ đề và trang cần xếp hạng; link JS cho nút chuyển đổi tới trang không cần xếp hạng, link phụ ở header/footer, link ngoài làm bằng chứng; trích nguồn bằng chữ, không link), Bước 4c, cột `Dạng mã`, 3 anti-pattern.
- **v1.2 (2026-10-18):** Vincent chốt nguyên tắc vị trí link: đúng ngữ cảnh, ưu tiên SC, MC chỉ 5 trường hợp, bám topical map và topic cluster. Thêm `references/link-placement.md`, Bước 4b kiểm bằng Jev `link-placement` (`tools/ai-assist/tasks/`), 2 cột `Vùng` và `Quan hệ map` trong link plan. Ca chạy thật: audit 161 link trên một site WordPress.
- **v1.1.1 (2026-10-17):** bảng phân vai thêm bước ghi link lên WordPress qua `wp-content-review-apply` và rubric Jev `link-bridge` (tuỳ chọn).
- **v1.0.1 (2026-07-07):** vá theo spot-run trên topical map GTV thật — tuyên precedence 4 chỗ 2-luật-giao-nhau: LLC gate chỉ áp link tùy nghi (link cấu trúc sop/03 miễn gate); list entities cùng type = ngoại lệ hợp lệ của max-1-link/heading (flag `list-exception`); AR4 competitor anchors per path (Path C → `competitor-anchor-pending`); intent-anchor: ưu tiên seed query hơn ép modifier khi 2 luật kéo 2 hướng.
- **v1.0 (2026-07-07):** khởi tạo — executable hóa [[Internal Linking Rules and Strategy]] (Koray Core Rules + SCN Case Study Rules + GTV Extensions Rule 59-60 + Intent Funnel + Link-less Connection), `sop/01-topical-map.md` Bước 13-14/20, `sop/03-internal-linking.md` (pillar-cluster-bridge + audit thresholds), [[Link Flow]], [[Semantic Content Network]], [[Pillar Cluster Page]], [[Ranking Signal Consolidation]].
