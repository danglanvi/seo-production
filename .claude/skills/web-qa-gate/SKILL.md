---
name: web-qa-gate
description: "Kiểm site WordPress sau mỗi lần ghi, trước khi lên production và đầu workstream web: tràn ngang có và không cache, axe, focus, form, tracking, plugin, HTTP, redirect, canonical, schema, OG, menu và slider bấm thật, bố cục, landmark, Jev ui-visual. Một lệnh ra PASS/FAIL."
metadata:
  version: "1.3.2"
---

# web-qa-gate — cổng kiểm sau mỗi lần ghi lên site

Một lần ghi lên site (theme, plugin, CSS, nội dung, redirect) có thể làm hỏng phần khác. Skill này chạy một lệnh kiểm 14 hạng mục có script và ra `report.json` cùng `report.md` có PASS/FAIL cho từng hạng mục. Hạng mục 12 (chữ dễ đọc) kiểm tay. Lượt kiểm chỉ đọc: script không gửi form, chặn mọi request tracking, và chỉ bấm nút giao diện (nút mở menu, mũi tên slider).

Skill chỉ kiểm. Việc sửa thuộc skill của việc ghi, ví dụ `wp-ui-fix` cho lỗi giao diện.

Gốc đường dẫn là root repo. Script nằm ở `skills/web-qa-gate/scripts/`. Jev nằm ở `tools/ai-assist/jev.py`. Skill gom từ các script QA của 2 site WordPress mẫu, đợt 15–24/10/2026.

## Khi nào dùng

| Chế độ | Khi nào | Đọc thêm |
|---|---|---|
| Kiểm sau ghi (mặc định) | Sau mỗi lần ghi lên staging hoặc production, trước khi báo xong. Sau khi đổi theme, plugin, CSS dùng chung hoặc template. | `references/hang-muc.md`, `references/hang-muc-13-15.md` |
| Cổng trước production | Trước khi báo "staging xong, chờ đưa lên production" | `references/truoc-production.md` |
| Audit đầu workstream | Mốc đầu của workstream web, trước khi sửa giao diện, theme hay nội dung hàng loạt | `references/audit-dau-workstream.md` |
| Kiểm độc lập sau ghi nội dung | Người kiểm kết luận một lần ghi nội dung do người khác làm | `references/kiem-doc-lap-sau-ghi-noi-dung.md` |

Không dùng khi: đo tốc độ (`wp-pagespeed`), audit technical SEO toàn site (`technical-seo-audit`), audit bố cục hay chuyển đổi để lập đề xuất (`visual-semantic-seo`, `cro-audit`), duyệt nội dung trước khi ghi (`wp-content-review-apply`), sửa lỗi giao diện (`wp-ui-fix`).

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Base URL và môi trường (`staging` hoặc `production`) | Người vận hành, `00-client-context/wp-server.md` | Hỏi. |
| Danh sách URL | Trang vừa ghi, 1 URL cho mỗi template bị chạm, trang có form | Hỏi. Không tự lấy cả sitemap. |
| Basic Auth của staging | Biến `WEB_QA_AUTH="user:pass"` lấy từ `.agent-secrets/.env` | Bỏ staging, ghi giới hạn. |
| Mã thẻ tracking mong đợi | Lượt chạy trước (dòng "Thẻ thấy trong HTML") hoặc người vận hành | Chỉ kiểm phần chặn. |
| 2 file `wp plugin list` | Lấy theo hồ sơ server, xem Bước 1 | Hạng mục plugin SKIP. Không SSH khi không có hồ sơ server. |
| Cổng `ui-visual` của site | Registry `00-client-context/model-calibration.json` | Báo "chưa hiệu chuẩn, chỉ báo cho người đọc". |
| Khối `interact` (selector menu, slider, màu kit, heading có số, cặp ngôn ngữ) | Người vận hành hoặc lượt đo trước của site, ghi trong `qa.json` | Hạng mục 13 và 14 SKIP. Báo việc cần khai. |
| Danh sách URL cho smoke trước và sau deploy | `wp post list` theo hồ sơ server | Bỏ bước smoke, ghi giới hạn. Không lấy từ sitemap. |

## Phân việc model

| Phần việc | Ai làm | Lý do |
|---|---|---|
| Tràn ngang, axe, focus, form, tracking, plugin, HTTP, redirect, canonical, schema, tương tác, bố cục, landmark, OG, skeleton | Code (luật tất định) | Số đo DOM, phép bấm thật, mã HTTP và parse HTML cho kết quả chính xác, không tốn tiền. |
| Soát ảnh màn hình (`ui-visual`) | Jev ảnh, đọc qua cổng của registry | Jev bắt lỗi nhìn thấy mà DOM không đo được: nút trống, ảnh vỡ, phần tử chồng nhau. |
| Đọc dòng WARN, xem ảnh, quyết định sửa | Claude | Model không tự đánh FAIL và không tự sửa site. |
| EmbeddingGemma | Không dùng | Cổng này so số đo và cấu trúc. Lỗi lặp giữa nhiều URL gom bằng selector. Không có việc nào cần đo độ giống ngữ nghĩa. |
| GLM Flash | Không dùng | Skill không trích câu. |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,axe,playwright?,jev?,pillow?,ssh?,wp-cli?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- `axe`: script tìm `axe.min.js` ở `AXE_JS`, `~/.cache/web-qa-gate/`, `node_modules/axe-core/` và cache `npx`. Thiếu thì tải một lần theo `references/hang-muc.md` mục 2.
- `playwright`: script gọi Chrome trực tiếp qua CDP, không cần thư viện Playwright. Máy không có Chrome thì script tự dùng Chromium do Playwright tải về.
- `jev`: thiếu key thì bỏ `--jev`. Hạng mục `ui-visual` SKIP.
- `ssh`, `wp-cli`: chỉ dùng để lấy file plugin, danh sách URL cho smoke và dữ liệu của checklist đường đi lead, theo hồ sơ server.

### Bước 1 — dựng config

1. Chép `skills/web-qa-gate/scripts/qa.example.json` vào thư mục evidence của đợt ghi.
2. Điền `site`, `env`, `base`, `widths` và `urls`. Giữ 3 bề rộng mặc định 360, 768, 1366 px, trừ khi site có breakpoint khác.
3. Đánh dấu trang có form bằng `"form": true`. Khai loại schema mong đợi bằng `"schema": [...]`.
4. Khai `http` cho đường dẫn đặc biệt và `redirects` cho redirect vừa tạo hoặc vừa đổi.
5. Lấy file plugin khi có hồ sơ server. Chạy `wp plugin list --format=json` trên staging và production, lưu 2 file cạnh config. Plugin lệch có chủ ý thì ghi vào `plugins.ignore`.
6. Viết `ui_visual.site_note` bằng tiếng Anh: thiết kế chính và phần tử cố định có chủ ý (header dính, nút liên hệ nổi, thanh dưới đáy). Khai thêm `ui_visual.hide_selectors` hoặc `hide_fixed: true` để ẩn nút nổi khi chụp.
7. Staging có Basic Auth: export `WEB_QA_AUTH` từ `.agent-secrets/.env`. Không in giá trị ra chat hay file. Staging qua tunnel: đặt `resolve` dạng `host=ip`.
8. Chép khối `interact` từ `scripts/qa.interact.example.json`, rồi thay selector, màu kit và cặp ngôn ngữ bằng giá trị của site. Đọc `references/hang-muc-13-15.md` mục "Bật hạng mục 13 và 14". Chỉ khai `count_claims` cho heading thật sự đếm thẻ bên dưới.

### Bước 2 — chạy một lệnh

```bash
python3 -E skills/web-qa-gate/scripts/qa_gate.py run --config <ev>/qa.json --out <ev>/qa-<YYYYMMDD-HHMM> --cache both [--tabs 3] [--jev --jev-budget 0.1]
```

- 6 URL × 3 bề rộng chạy khoảng 5 phút với 1 Chrome. 12 URL chạy khoảng 10 phút. `--cache both` gấp đôi số lượt đo tràn.
- Lệnh trả exit code 1 khi kết luận là FAIL.
- Thêm `--jev` khi trang không cần đăng nhập. Ảnh chụp không chứa dữ liệu khách, vì script không điền form.
- Dựng lại report từ dữ liệu đã thu, không gọi mạng: `qa_gate.py report --config <ev>/qa.json --out <thư mục>`.

Cờ cho lượt quét nhiều URL:

| Cờ | Tác dụng |
|---|---|
| `--plan` | In kế hoạch (URL, bề rộng, bản cache, số lượt đo). Không mở Chrome, không ghi file. Chạy trước lượt lớn. |
| `--tabs N` | Chạy N Chrome song song, tối đa 6. |
| `--resume` | Giữ dòng đã đo tốt trong `raw/browser.jsonl`, đo lại dòng lỗi, giữ đúng mẫu của lượt trước. |
| `--sample N` hoặc `--sample P%` `[--seed S]` | Đo N URL hoặc P% số URL. Cùng seed cho cùng mẫu. URL có `"always": true` luôn nằm trong mẫu. Report ghi "kết luận chỉ áp cho mẫu". |
| `--cache cached\|nc\|both` | Đo bản có cache, bản bỏ cache (`?nc=`) hoặc cả hai. Xem `references/hang-muc.md` mục 1. |
| `--page-timeout ms` | Trần giờ cho mỗi URL × bề rộng, mặc định 120000. Hết giờ thì script ghi lỗi và đo tiếp. |

Chrome treo hoặc lượt trước bị ngắt: chạy `node skills/web-qa-gate/scripts/chrome_cleanup.mjs` để liệt kê Chrome mồ côi, rồi thêm `--apply` để dọn. Không dùng `pkill`.

Chế độ cổng trước production, audit đầu workstream và kiểm độc lập dùng thêm `scripts/truoc_production.py` (skeleton theme, so lượt chạy, điều khiển trong HTML server, header bảo mật, dựng danh sách URL). Lệnh và cách đọc nằm trong reference của từng chế độ.

### Bước 3 — đọc report

1. Đọc bảng tổng của `report.md`. Khi cần biết luật chấm, đọc `references/hang-muc.md` (hạng mục 1–12) hoặc `references/hang-muc-13-15.md` (tương tác, bố cục, landmark, OG).
2. Với mỗi FAIL, tìm nguyên nhân trong lần ghi vừa rồi.
   - Nếu FAIL vì lần ghi đổi thiết kế (khối dời chỗ, thẻ đổi loại, thanh dính đổi vị trí), coi đó là thay đổi giao diện. Hỏi người duyệt kèm ảnh trước và sau. Không kết luận script sai tiền đề rồi bỏ qua. Ca thật 30/10/2026 ở site bán lẻ mẫu: check thanh mục lục sản phẩm rớt sau khi lô dời thanh, lane ghi "harness sai tiền đề". Người duyệt báo đúng lỗi đó sau deploy, nên phải sửa và purge lại 411 sản phẩm.
3. Với mỗi WARN, xem bằng chứng:
   - Dòng Jev: mở ảnh `raw/shots/<tên>_<bề rộng>_<số>.jpg`, xem hộp lỗi `box` trong `report.json`. Xem thêm 1 màn cho mỗi template ở mỗi bề rộng, kể cả màn Jev không gắn cờ.
   - Dòng focus FAIL: xem ảnh trước khi kết luận. Site có thể dùng chỉ báo mà script chưa đo.
   - Dòng form "không thấy honeypot": hỏi người vận hành site dùng cách chống spam nào.
   - Dòng 13a: mở ảnh menu lúc đóng và lúc mở trong `raw/shots/`. Dòng 13b: đọc điểm nào của mũi tên bị che, và tập thẻ nhìn thấy trước và sau khi chạm. Kết luận theo phần tử nhìn thấy, không theo class của thư viện.
   - Dòng 14a, 14c, 14d: xem ảnh trang ở bề rộng đó. Cột đệm rỗng hay lưới masonry là chủ ý thì ghi lý do.
4. Với mỗi SKIP, ghi lý do và việc cần làm để lần sau chạy được.

### Bước 4 — sửa và chạy lại

1. Sửa theo skill của việc ghi, ví dụ `wp-ui-fix`, `wp-pagespeed` hay `wp-content-review-apply`. Skill này không sửa site.
2. Chạy lại cả 14 hạng mục, không chỉ hạng mục vừa sửa. Bản vá một hạng mục hay làm hỏng hạng mục khác.
3. Lặp tới khi report không còn FAIL, hoặc tới khi FAIL còn lại cần người duyệt quyết.
4. Lần ghi thêm hoặc sửa chữ trên trang: kiểm thêm chữ dễ đọc theo `references/hang-muc.md` mục 12, ở 6 bề rộng 360, 390, 440, 768, 1024, 1366 px. Script chưa tự chấm mục này.
5. Lần ghi chạm form, plugin form, plugin SMTP hoặc plugin ghi Sheet: kiểm checklist "Đường đi của lead" ở `references/hang-muc.md` mục 4.

### Bước 5 — báo xong

Báo kết luận, đường dẫn `report.md`, giờ chạy, mọi WARN đã xem kèm kết luận của Claude, mọi SKIP kèm lý do. Lượt chạy bằng `--sample` chỉ kết luận cho mẫu: ghi rõ số URL đã đo trên tổng số URL.

### Gửi form thật (chỉ khi được giao)

- Đọc `references/form-gui-that.md` trước khi chạy.
- Lệnh gửi form thật gửi mail tới hộp thư thật. Mỗi lần chạy trên production cần Vincent duyệt. Staging thì chạy được.
- Cần cờ `--submit-live` và biến `WEB_QA_SUBMIT_LIVE=<host>`. Production cần thêm `--approved "<người duyệt, ngày giờ>"`.
- Kiểm hộp mail theo cách người vận hành cấp. Ghi kết quả bằng `report --mail-ok <token>` hoặc `--mail-missing <token>`.

### Chạy lại phân tích trên dữ liệu cũ

Lệnh `check` đọc file đã lưu và không gọi mạng. Dùng lệnh này để so lượt mới với lượt cũ, hoặc đọc lại output của script cũ:

```bash
python3 -E skills/web-qa-gate/scripts/qa_gate.py check overflow <ux.jsonl> --widths 360,390,768,1366
python3 -E skills/web-qa-gate/scripts/qa_gate.py check axe <thư mục hoặc file axe>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check focus <thư mục focus>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check http <output httpcheck.sh>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check plugins <staging> <production>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check html <thư mục html> --glob 'prod_*.html' --urls <tên-tab-url.tsv> --canonical-host <host>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check ui-visual <jev-out.jsonl> --registry <registry> --site <domain>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check interact <interact.jsonl> --config <ev>/qa.json
python3 -E skills/web-qa-gate/scripts/qa_gate.py check layout <interact.jsonl> --landmarks <landmarks.jsonl>
python3 -E skills/web-qa-gate/scripts/qa_gate.py check og <thư mục html> --images <og_images.jsonl> --canonical-host <host>
python3 -E skills/web-qa-gate/scripts/truoc_production.py diff <out lượt trước> <out lượt sau> --labels truoc,sau
```

## Output

- Thư mục: `03-audits/technical/web-qa-<YYYY-MM-DD-HHMM>/`, hoặc thư mục evidence của đợt ghi.
- `report.md`: bảng 14 hạng mục, chi tiết từng dòng, ghi chú, danh sách SKIP.
- `report.json`: cùng nội dung, đủ mọi dòng.
- `raw/`: `http.jsonl`, `html/` (HTML server, header, URL cuối), `browser.jsonl` (số đo DOM, axe, focus, tracking, form, bản cache), `interact.jsonl`, `landmarks.jsonl`, `og_images.jsonl`, `shots/` (gồm ảnh menu lúc đóng và mở), `job.json`, `interact_job.json`, `landmarks_job.json`, `sample.json` khi chạy mẫu, `jev-in.jsonl`, `jev-out.jsonl`, `form_live.json` khi có gửi thật.
- Cổng trước production và audit đầu workstream: thêm file JSON của `truoc_production.py` (`--out <file>`) cạnh report.
- Ảnh dùng làm bằng chứng trong deliverable thì chép sang `02-raw/screenshots/` theo `_REFERENCE/screenshots-protocol.md`.

## Hiệu chuẩn Jev ui-visual

Lượt hiệu chuẩn đầu chạy ngày 19/10/2026 trên một site mẫu. Bộ ảnh có 72 ảnh: 12 URL × 3 bề rộng × 2 màn. Claude gán gold mù trước lượt Jev. Bộ ảnh chia dev và holdout theo URL. Mục tiêu precision là 0,95.

| Câu | Mẫu dương | AUC | Kết quả |
|---|---|---|---|
| `fixed_covers` | 33 | 0,85 | Có tín hiệu. Từ 0,85 Jev đúng 9/9, nhưng chưa đủ 10 mẫu để chốt ngưỡng. |
| `overlap` | 6 | 0,68 | Quá ít mẫu dương. |
| `spacing` | 11 | 0,55 | Không có tín hiệu. |
| `empty_control` | 5 | 0,51 | Không có tín hiệu. |
| `cut_off` | 20 | 0,41 | Không có tín hiệu. Jev bỏ sót ô chọn ngôn ngữ bị cắt trong hộp của nó. |
| `media_problem` | 14 | 0,33 | Không có tín hiệu. Jev không thấy ảnh tác giả bị thiếu. |

Cách dùng kết quả:

- Không câu nào có ngưỡng. Report giữ dòng "chưa hiệu chuẩn, chỉ báo cho người đọc" cho cả 6 câu.
- Ở ngưỡng tạm 0,7, Jev gắn cờ 41/72 ảnh. 35 ảnh trong số đó có lỗi thật. Jev bỏ sót 22 trong 57 ảnh có lỗi.
- Claude xem mọi ảnh Jev gắn cờ. Claude xem thêm ít nhất 1 màn cho mỗi template ở mỗi bề rộng.
- Không dùng Jev để loại một ảnh khỏi danh sách xem.
- Đọc nhãn từng câu như gợi ý chỗ cần xem. Câu `fixed_covers` có tín hiệu tốt nhất.
- Lượt 72 ảnh tốn 0,015 USD.
- Site khác cần lượt hiệu chuẩn riêng theo skill `model-calibration`. Ghi entry vào registry của site đó.

## Trước khi trình

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:

1. Tràn ngang so với bề rộng đặt, có mốc 768 px, dùng viewport thật (không bật `isMobile`), UA Chrome thường, một lần tải mới cho mỗi bề rộng, và đo cả bản có cache lẫn bản bỏ cache. Lần ghi chạm CSS có media query thì thêm mốc quanh breakpoint. Lỗi đã gặp: so `scrollWidth` với `innerWidth` che lỗi tràn 10–35 px trên 18/19 trang; UA `HeadlessChrome` làm slick không khởi tạo, nên lane báo 0 trang tràn khi 11/48 trang tràn 15–16 px; lượt quét bỏ cache bỏ sót tràn ở 1099–1100 px của bản có cache.
2. Lượt chạy cuối sau bản vá có đủ 14 hạng mục, và cổng trước production đã chạy trước khi báo staging xong. Lỗi đã gặp: 2 vòng vá đầu gây 7 lỗi hồi quy mà lượt kiểm từng phần không thấy; báo 2 trang đã lên staging khi chưa kiểm skeleton, bảo mật, form, nên người duyệt phải hỏi lại và làm bù 34 phút.
3. Form được kiểm ở mọi bề rộng. Lần ghi chạm form, SMTP hoặc plugin Sheet có đủ 5 chặng của đường đi lead. Lỗi đã gặp: form không khởi tạo ở 768 px trở xuống, lượt kiểm desktop không thấy; một site mất mail và Sheet khoảng 4 tháng, lead không khôi phục được.
4. Lỗi tương tác được kiểm bằng phần tử nhìn thấy: menu mobile bấm thật, mũi tên slider chạm thật và so tập thẻ nhìn thấy. Lỗi đã gặp: hamburger vô hình trên production nhiều ngày qua nhiều vòng QA; vòng kiểm slider đọc `slick-current` nên báo đạt khi nút trên mobile không bấm được (268 phút sửa).
5. Report ghi số request tracking đã chặn và 0 lượt lọt. Lỗi đã gặp: lượt chụp production cuộn trang làm GTM chạy và gửi hit thật.
6. Plugin staging đã so với production, plugin lệch có chủ ý có lý do. Lỗi đã gặp: staging thiếu 5 plugin, lỗi chỉ hiện trên production.
7. Mỗi dòng Jev có kết luận của Claude sau khi xem ảnh, mỗi SKIP có lý do và việc cần làm, và số trong tin báo lấy từ `report.json` của lượt chạy cuối kèm giờ chạy. Lỗi đã gặp: Jev bỏ sót 22/57 ảnh có lỗi ở lượt hiệu chuẩn đầu, và gắn cờ `fixed_covers` nhầm 453/742 ảnh vì nút nổi khi chưa ẩn bằng `hide_selectors`.
8. Robots và canonical đã kiểm ở 5 biến thể cache bằng `cache_variants.py` khi lần ghi kèm purge, làm nóng hoặc PSI. Lỗi đã gặp: lượt PSI bằng `?utm_source=` ghi bản `noindex` vào cache URL sạch của trang chủ. Googlebot smartphone nhận `noindex` khoảng 50 phút, còn bản desktop vẫn đúng.

## Gate

- [ ] Không gửi form thật khi chưa có duyệt cho lượt đó (production) hoặc khi chưa biết mail tới hộp thư nào (staging).
- [ ] Tracking bị chặn trong mọi lượt; report có 0 lượt lọt.
- [ ] Jev chỉ nhận ảnh trang không cần đăng nhập. Không chụp wp-admin hay trang có dữ liệu khách.
- [ ] Không in mật khẩu Basic Auth, cookie đăng nhập, slug đăng nhập ra chat hay report.
- [ ] Báo PASS chỉ khi report ra PASS, hoặc khi mọi WARN đã được xem và có lý do.
- [ ] Không ghi gì lên site trong lúc chạy cổng. Script chỉ bấm nút mở menu và mũi tên slider, không bấm nút gửi form hay link sang trang khác.
- [ ] Không báo PASS cho cả site từ lượt chạy `--sample`. Tin báo ghi số URL đã đo trên tổng số URL.
- [ ] Checklist đường đi của lead chỉ đọc: che mật khẩu, API key, token của SMTP và nhà gửi mail; không tự đọc hộp thư.
- [ ] Audit đầu workstream trình vấn đề lớn kể cả khi việc sửa nằm ngoài giai đoạn hiện tại; vấn đề nhỏ có dòng trong backlog.

## Anti-patterns

- So `scrollWidth` với `innerWidth` ở giả lập mobile → so với bề rộng đặt. Chrome nới `innerWidth` theo phần tràn.
- Bật `isMobile` (cờ `mobile` của CDP) khi đo tràn → dùng viewport thật. Cờ này nới `innerWidth` (390 thành 421–481 px), nên phép đo ra 0 và JS dựng slider theo sai mốc.
- Để UA mặc định `HeadlessChrome` trong script tự viết → đặt UA Chrome thường. Slick không khởi tạo với UA mặc định.
- Tải trang một lần rồi đổi bề rộng → tải lại ở từng bề rộng. Slider dựng mũi tên theo cỡ lúc tải.
- Kết luận từ lượt quét chặn ảnh → đo lại ở chế độ tải đầy đủ. Thiếu ảnh làm `figure` đổi cỡ và tạo tràn giả.
- Kiểm canonical hay robots trên URL có query, hoặc chỉ trên bản desktop → kiểm URL sạch ở 5 biến thể bằng `cache_variants.py`.
- Đặt bề rộng dưới 500 px bằng `--window-size` → dùng `Emulation.setDeviceMetricsOverride`. Chrome headless ép tối thiểu 500 px.
- Chụp production mà không chặn tracking → chặn từ đầu phiên. Cuộn và rê chuột làm GTM hoãn chạy rồi gửi hit.
- Script Chrome tự viết cho lane chỉ chặn tracking bằng request interception → beacon gửi lúc đóng tab vẫn lọt. Dùng `dnsRules()` của `scripts/_cdp.mjs` để thêm `--host-resolver-rules` cho cùng danh sách host.
- Kết luận thiếu chỉ báo focus chỉ vì không có outline → so style lúc có và không có focus. Ô nhập hay dùng màu viền làm chỉ báo.
- Dùng nhãn từng câu của Jev làm kết luận → xem ảnh. Lượt hiệu chuẩn đầu: `cut_off`, `media_problem`, `spacing` không có tín hiệu. Không dùng điểm `polish` để loại.
- Chỉ xem ảnh Jev gắn cờ → xem thêm 1 màn mỗi template ở mỗi bề rộng. Jev bỏ sót 22/57 ảnh có lỗi ở lượt hiệu chuẩn đầu.
- Báo "staging đạt" khi plugin staging khác production → so 2 danh sách trước khi đưa lên production.
- Coi "không có canonical" trên staging là lỗi → staging `noindex` được phép thiếu canonical. Kiểm canonical trên production ngay sau khi deploy.
- Kiểm slider bằng class `slick-current` hay `swiper-slide-active` → chạm thật và so tập thẻ nhìn thấy. Class đổi được trong khi track đứng yên.
- Kết luận menu mobile từ ảnh tĩnh hay DOM → bấm thật và đếm link nhìn thấy. Nút trong suốt vẫn có kích thước, nên DOM báo "có nút".
- Kết luận tràn ngang chỉ từ bản `?nc=` → chạy `--cache both`. CSS đã gộp của plugin cache có lỗi riêng.
- Mô tả nút nổi trong `site_note` để giảm cờ Jev → ẩn bằng `hide_selectors` hoặc `hide_fixed`. Mô tả không giảm cờ (54 trước, 54 sau).
- Dừng Chrome treo bằng `pkill` → dùng `chrome_cleanup.mjs`. `pkill` giết cả Chrome của lượt khác.
- Lấy danh sách URL smoke từ sitemap → dùng `wp post list`. Sitemap bỏ trang noindex và có thể còn URL cũ.
- So header giữa bản VI và bản EN → `truoc_production.py skeleton` chỉ so trang cùng `<html lang>`. Menu bản dịch khác là chủ ý.
- Gom lỗi UX thấy trong lúc làm vào "giai đoạn sau" mà không báo → ghi vấn đề lớn vào tin trình, vấn đề nhỏ vào backlog.

## Changelog

- v1.3.2 (2026-10-31): Bước 3 thêm luật cho FAIL do lần ghi đổi thiết kế: hỏi người duyệt kèm ảnh, không bỏ qua vì "script sai tiền đề". Nguồn: đợt 2 tốc độ site bán lẻ mẫu 30/10/2026 (instance của site, `03-audits/technical/toi-uu-pagespeed/dot2-3010/luot2/deploy/2b-chuc-nang.md` mục 5.3, `decisions.md`). Eval thêm 1 ca. Không đổi script.
- v1.3.1 (2026-10-27): `_cdp.mjs` thêm `dnsRules()`: mọi host trong danh sách chặn tracking bị chặn thêm ở tầng DNS (`--host-resolver-rules ... ~NOTFOUND`), vì beacon gửi lúc đóng tab không đi qua `Network.setBlockedURLs`. Ca thật 26/10/2026: Chrome headless của một lane trên production lọt khoảng 12 page_view và 15 sự kiện thử vào GA4. Test `tests/test_dns_block.py` chạy Chrome thật (có luật: 0 lượt tới host chặn; không luật: 1 lượt). Eval thêm 1 ca.
- v1.3 (2026-10-25): ui-2, qa-2, qa-1, ui-5, hs-8. `references/hang-muc-13-15.md` mục 15 thêm dòng trỏ `featured-image-seo/references/og-trang.md` mục 8 (og:image, og:image:type, Scrape Again) khi chạy trong workspace của Vincent. Hạng mục 13 tương tác (`interact_probe.mjs`: menu bấm thật, slider chạm thật, `forcePseudoState`, màu kit hai chiều), 14 bố cục (lưới, số heading, CTA trùng, cặp VI/EN, landmark bằng `landmarks.mjs`), 15 OG; `--cache both`, `--tabs`, `--resume`, `--sample`, `--plan`, `--page-timeout`; chụp đủ màn, ẩn nút nổi, `chrome_cleanup.mjs`; checklist đường đi lead ở mục 4; chế độ cổng trước production, audit đầu workstream, kiểm độc lập (3 reference mới, `truoc_production.py`: skeleton, diff, controls, headers, urls); 14a, 14c, 14d về WARN theo đặc tả; checklist gộp còn 8 mục. Test 40/40 offline, `truoc_production.py` thử trên 22 trang HTML đã lưu của site mẫu.
- v1.2 (2026-10-24): `pad_image` thu ảnh gửi Jev về ≤ 0,8 MP và đệm ảnh dẹt lên tỉ lệ cao/rộng 0,3, vì Jev trả `http_400` với ảnh trên khoảng 1 MP hoặc dẹt hơn 0,3. Test thêm ca màn desktop 1366×768 và ô 1200×200. `hang-muc.md` mục 12 mới: chữ dễ đọc sau khi thêm copy (dòng chữ dính, line-height, đoạn dài căn giữa, tràn sau khi thêm chữ) ở 6 bề rộng; LiteSpeed hoãn JS tới tương tác nên rê chuột trước khi đo. Nguồn: `Deliverables/GTV-Brand/GTV-Website/ui-20261020/doc-de-2310/sua/CHECKPOINT.md` và `bao-cao.md` (line-height < 1,6 từ 1.122 xuống 339 ô, đoạn dài căn giữa từ 367 xuống 14).
- v1.1 (2026-10-21): `browser_probe.mjs` không bật cờ `mobile` của CDP. Fixture 390 px: bản cũ cho JS đọc `innerWidth` 421 lúc load và báo thủ phạm giả `button.slick-next`, bản mới đọc 390 và vẫn bắt tràn. `hang-muc.md` mục 1 thêm 6 bẫy: `isMobile`, UA `HeadlessChrome` làm slick không khởi tạo, tải một lần rồi đổi cỡ, chặn ảnh tạo tràn giả, bộ bề rộng thưa bỏ sót 800 và 900 px, `visibility:hidden` vẫn tính vùng cuộn. Mục 9: canonical chỉ đọc một bản cache, kiểm 5 biến thể bằng `wp-pagespeed/scripts/cache_variants.py`. Rút từ đợt gtvseo.com 20–21/10.
- v1.0 (2026-10-19): tạo mới. Gom `ux_probe.mjs`, `axe_run.mjs`, `focus.mjs`, `httpcheck.sh`, `tiles.mjs` thành `qa_gate.py` + `browser_probe.mjs`. Sửa lỗi so tràn ngang với `innerWidth`. Focus so style có và không có focus. Gửi form thật có 2 lớp chặn. Test offline `tests/test_qa_gate.py`. Hiệu chuẩn lượt đầu Jev `ui-visual` trên site mẫu (72 ảnh): chưa câu nào đạt ngưỡng.
