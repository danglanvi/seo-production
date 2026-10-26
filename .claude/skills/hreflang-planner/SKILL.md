---
name: hreflang-planner
description: "Audit và sinh hreflang cho site đa ngôn ngữ (VI/EN, SEA): mã ISO, self-reference, return tags, x-default, xung đột canonical, đích noindex hay redirect; EmbeddingGemma kiểm cặp trang 2 ngôn ngữ có tương đương không. Dùng khi audit, sinh hreflang hoặc SERP trả sai bản ngôn ngữ."
metadata:
  version: "1.2"
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

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code | Đọc thẻ hreflang, kiểm mã ISO, self-reference, return tags, đích HTTP, so cặp đã khai | dùng |
| EmbeddingGemma 2 | Xếp ứng viên bản tương đương bằng cosine cấp trang (prompt SentenceSimilarity). Đẩy cặp có độ phủ section 2 chiều `sec_cov` thấp (prompt Document) xuống cuối danh sách đọc | dùng, chạy local. Hiệu chuẩn 19/10 trên 50 cặp VI–EN: ứng viên hạng 1 đúng 8/9 trang có bản tương đương. Ngưỡng `sec_cov` < 0,82 là nháp, chưa holdout, và đã loại nhầm 1 cặp thật (0,812), nên cặp dưới ngưỡng không bị loại, chỉ xếp cuối kèm ghi chú "nháp, chưa holdout". Không có ngưỡng nhận: cặp âm cao nhất 0,887, cặp dương thấp nhất 0,812 |
| Jev | Chấm 2 trang có tương đương không | không dùng: chưa có rubric hiệu chuẩn; Gemma đã thu hẹp còn 21/50 cặp cho Claude đọc |
| GLM Flash | Trích câu | không dùng: không có việc trích câu |
| Claude | Gán gold, đọc mọi cặp ứng viên (cặp dưới ngưỡng nháp đọc cuối), gate chủ đích, viết finding và bộ tag | dùng |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,numpy?,gemma?,screaming-frog?,curl?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0b — Đọc references + xác định data tier & scope

1. Đọc `sop/06-self-checklist/tier-3-technical-advance.md` mục 10 (International — 9 item canonical) + [[syntheses/Multilingual SEO]] (4 nguyên tắc) + [[Hreflang PageRank Sharing]] (nuance gate) — khung chấm của skill này.
2. Xác định `$MODE`, tier data, `$MARKETS` (thiếu → hỏi: những thị trường nào là mục tiêu THẬT có content riêng? — hreflang cho bản dịch máy rỗng là phản tác dụng).
3. 🔴 **Gate chủ đích** ([[Hreflang PageRank Sharing]]): trước khi flag "thiếu hreflang" là lỗi, hỏi — bản ngôn ngữ kia đã đủ chất lượng/đủ content chưa? Chưa → thiếu hreflang có thể là chủ đích hợp lệ, ghi nhận là quyết định chứ không phải lỗi.
4. Audit site lớn Tier A cần crawl mới → báo scope + tốc độ, chờ xác nhận (server khách thật — theo quy ước technical-seo-audit).

### Bước 1 — Dựng inventory

Từ data tier: bảng mỗi hàng = 1 URL, cột = ngôn ngữ khai báo, hreflang set (cặp lang→href), canonical, meta robots, HTTP status, nơi đặt (head/header/sitemap). Generate mode: bảng cặp URL tương đương giữa các bản (equivalence map) — user xác nhận map trước khi sinh tag.

### Bước 1b — Kiểm cặp tương đương bằng EmbeddingGemma

Chạy khi site có ≥ 2 bản ngôn ngữ và có store của skill `site-vector-index` (mức page và section). Thiếu Gemma hoặc store thì Claude đọc từng cặp, ghi giới hạn.

1. Lấy cặp đã khai: `python3 -B skills/hreflang-planner/scripts/pair_check.py declared --html-dir <thư mục HTML đã tải> --out <W>/declared.jsonl`. Thư mục chứa cặp file `.html` + `.url` của `site-vector-index`.
2. Dựng cặp ứng viên: `<venv>/bin/python -B -I skills/hreflang-planner/scripts/pair_check.py pairs --store <store> --page-store <store page SentenceSimilarity> --b-prefix /en/ --declared <W>/declared.jsonl --k 5 --out <W>/pairs.jsonl`. Không có store SentenceSimilarity thì bỏ `--page-store`.
3. Ra kết luận: `<venv>/bin/python -B -I skills/hreflang-planner/scripts/pair_check.py report --pairs <W>/pairs.jsonl --registry 00-client-context/model-calibration.json --site <domain> --metric sec_cov --out-dir <W>`.
4. Site mới: Claude gán gold mù ≥ 40 cặp trước khi xem điểm, rồi chạy `calibrate.py cosine --pairs` (skill `model-calibration`) với rubric `hreflang-pair`, version `sec_cov`. Chưa có ngưỡng thì Claude đọc mọi cặp.
5. Claude đọc mọi cặp "Claude đọc", rồi đọc cặp "Claude đọc cuối" (dưới ngưỡng nháp, chưa holdout). Script không loại cặp nào. Kết luận đưa vào mục 3b của report:
   - Cặp đã khai mà không tương đương → finding ❌, sửa nội dung hoặc gỡ hreflang.
   - Trang chưa khai mà có bản tương đương → đề xuất cặp, qua gate chủ đích trước.
   - Bản dịch lệch vì một bên đã viết lại → ghi "cần dịch lại", không ghi "không có bản tương đương".
   - Trang khai `hreflang="en"` mà H1, H2 viết tiếng Việt → finding ❌ ngôn ngữ khai sai.

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

**3d. Nút chuyển ngôn ngữ và tự chuyển hướng** (khi audit hoặc thiết kế bộ chọn ngôn ngữ):

- Không tự chuyển giữa các bản ngôn ngữ theo IP hay `Accept-Language` khi trang gốc `/` không phải bản tiếng Anh. Googlebot thường crawl từ IP Mỹ với trình duyệt `en-US`, nên sẽ bị chuyển khỏi bản gốc. Khách Việt dùng trình duyệt tiếng Anh cũng bị đẩy sang bản EN.
- Thay bằng gợi ý không chặn, đọc `navigator.languages` ở trình duyệt. Gợi ý hiện khi trình duyệt không ưu tiên ngôn ngữ của trang, có nút chuyển và nút đóng. Lựa chọn lưu bằng cookie 1 năm. Cookie này không được đưa vào vary của cache.
- Dropdown trỏ đúng URL tương đương của từng trang theo cặp hreflang. Trang không có bản tương đương thì trỏ trang chủ của bản kia. Nhãn ghi tên ngôn ngữ, không dùng cờ quốc gia. Nút có `aria-expanded`, phím Esc đóng, vùng chạm từ 44 px.
- Ngoại lệ: trang gốc `/` là tiếng Anh và mỗi bản có URL riêng cùng hreflang, như openai.com (chỉ chuyển `/` sang `/vi-VN/`). Khi đó tự chuyển riêng trang gốc ít rủi ro hơn. Report vẫn ghi rủi ro và để khách quyết.

### Bước 4 — Render report / bộ tag

- Audit: `03-audits/<client>_Hreflang-Audit_<YYYY-MM-DD>.md` theo skeleton Output.
- Generate: bộ tag/sitemap trong report (fenced code, sẵn dán) + hướng dẫn verify sau deploy (GSC URL Inspection bản từng thị trường; re-audit sau 2-4 tuần).

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Trang khai `hreflang="en"` có H1, H2 bằng tiếng Anh; trang lẫn tiếng Việt thành finding. Nguồn lỗi: 19/10 hai trang /en/ của site mẫu có H1 và H2 tiếng Việt.
- [ ] Mọi trang chưa khai hreflang có kết luận về bản tương đương. Nguồn lỗi: 19/10 4/10 trang /en/ của site mẫu chưa khai cặp vi.
- [ ] Cặp lệch do một bên viết lại được ghi "cần dịch lại". Nguồn lỗi: 19/10 trang dịch vụ TP.HCM bản EN dịch từ bản VI cũ, `sec_cov` 0,81 dưới ngưỡng nháp.
- [ ] Không đề xuất trang tác giả, chuyên mục hay trang chủ làm cặp hreflang. Nguồn lỗi: 19/10 Gemma xếp trang tác giả hạng 1 cho trang đội ngũ /en/.
- [ ] Ngưỡng loại lấy từ registry của site, chỉ dùng để xếp cuối, và report ghi rõ không có ngưỡng nhận. Nguồn lỗi: hiệu chuẩn 19/10, cặp âm cao nhất 0,887 cao hơn cặp dương thấp nhất 0,812.
- [ ] Bộ chọn ngôn ngữ theo mục 3d: gợi ý theo `navigator.languages` và cookie, không tự chuyển theo IP khi trang gốc không phải tiếng Anh. Nguồn lỗi: 23/10 yêu cầu mặc định theo IP cho gtvseo.com; phép thử openai.com, notion.com, apple.com cho thấy chỉ site có gốc tiếng Anh mới tự chuyển an toàn.

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

## 3b. Cặp tương đương (EmbeddingGemma + Claude)
| Trang B | Đã khai | Ứng viên đầu | sec_cov | Kết luận của Claude |

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

- **v1.2 (2026-10-24):** thêm mục 3d nút chuyển ngôn ngữ: không tự chuyển theo IP hay `Accept-Language` khi gốc không phải tiếng Anh, gợi ý theo `navigator.languages`, cookie 1 năm ngoài vary cache, dropdown trỏ URL tương đương. Thêm 1 mục tự phản biện. Nguồn: lane `ngon-ngu` gtvseo.com 23/10 (`Deliverables/GTV-Brand/GTV-Website/ui-20261020/doc-de-2310/ngon-ngu/bao-cao.md` mục 3) và phép thử openai.com, notion.com, apple.com, stripe.com cùng ngày.
- **v1.1.1 (2026-10-19):** ngưỡng `sec_cov` < 0,82 về nháp (chưa holdout, loại nhầm 1 cặp thật 0,812): `pair_check.py report` không loại cặp dưới ngưỡng, chỉ xếp cuối với nhãn "Claude đọc cuối" và ghi chú "nháp, chưa holdout". Test cập nhật.
- **v1.1 (2026-10-19):** thêm Bước 1b: EmbeddingGemma kiểm cặp trang 2 ngôn ngữ (`scripts/pair_check.py`: declared, pairs, report). Hiệu chuẩn 50 cặp VI–EN thật: ngưỡng loại `sec_cov` < 0,82, không có ngưỡng nhận. Thêm Bước 0, phân việc model, tự phản biện, mục 3b. Test `tests/test_pair_check.py`.
- **v1.0 (2026-07-19):** tạo mới — 6 nhóm audit check (ISO validation với case `vn`→`vi`, self-ref, return tags, x-default, canonical conflict, đích sạch), generate 3 phương án đặt + bảng chọn theo quy mô, map cấu trúc ccTLD/subdomain/subfolder (default GTV: subfolder), gate chủ đích theo [[Hreflang PageRank Sharing]]; canonical checklist kế thừa tier-3 SOP mục 10.
