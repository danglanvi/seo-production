# Cách làm từng bước

> Lệnh và ngân sách tool call của từng pha nằm ở bảng "Quy trình chuẩn" trong SKILL.md; file này ghi cách ra quyết định ở từng bước. Chỉ đọc mục của pha đang làm: mục 1–2 cho pha A–B, mục 3–4 cho pha C, mục 5–6 cho pha D, mục 7 cho pha E, mục 8–11 cho pha F, mục 12 cho pha G–H. Đường dẫn tính từ root repo SEO Production (instance của khách). Chạy ở workspace GTV gộp nhiều dự án thì xem mục 13.

## 1. Thu dữ liệu

| Dữ liệu | Lấy ở đâu | Lưu ở đâu |
|---|---|---|
| Phiếu đầu vào (đọc đầu tiên) | `$W/intake.md` theo `_TEMPLATES/qp-intake.md` | Lead điền trước khi gọi agent |
| Bộ keyword cam kết, engine đo, mốc nghiệm thu | `00-client-context/kpi-commitments.md`, bản chưng cất hợp đồng, hoặc sheet KPI (tải tab thành CSV) | `qp_ranks.py bo <file> --col "<cột keyword>" [--where "<cột nhóm>=<giá trị>"] -o $W/bo-cam-ket.txt`. File markdown thì chép bảng keyword ra CSV trước. Không gõ lại từng keyword |
| Hạng | SpySERP: export CSV của project đo bộ cam kết, đủ ít nhất 35 ngày gần nhất. Project có bản so sánh đối thủ (nhiều domain) thì export bản đó. SpySERP chia lần chạy theo trang (dòng meta "Schedules Page"): export đủ các trang, hoặc chọn khoảng ngày ≥35 ngày | `02-raw/seo-data/keywords/<YYYY-MM-DD>_spyserp_<bo>[_p<N>].csv` (chỉ thêm, không sửa). Nhiều file thì truyền tất cả vào cùng lệnh |
| Hạng khi phiên SpySERP hết hạn | Tab hạng trong sheet của Lead (dán từ SpySERP), tải thành CSV. Script đọc được dấu phẩy | Như trên, tên file ghi `_sheet` |
| URL target theo kế hoạch | Topical map, content plan hoặc sheet URL của dự án: hai cột keyword và URL | `$W/url-target.csv`, truyền `--targets` |
| Volume | Cột Volume của SpySERP (đã đọc vào `hang.json`). SpySERP ghi 0 khi chưa lấy volume | Dùng nguồn khác (Ahrefs, sheet) thì ghi nguồn ở `src` của slide |
| SERP top 10 | Ahrefs SERP overview, Firecrawl search có tham số quốc gia, hoặc tab ẩn danh có ảnh chụp | Ghi nguồn và ngày vào `serp.cards[].meta`; ảnh chụp vào `02-raw/screenshots/` |
| Trang thật | `scripts/site_check.py` (chỉ GET) | HTML tải về nằm trong `$W/pages/` |
| GSC (nếu có quyền) | Performance theo page và query, URL Inspection | Export vào `02-raw/seo-data/keywords/`; thiếu quyền thì ghi "cần GSC" ở kết luận phụ thuộc GSC |

Engine đo phải là engine trong hợp đồng (thiết bị, vị trí, ngôn ngữ). Team đang đo bằng engine khác thì vẫn làm, nhưng ghi lệch vào `flags` và `measure_slide.src`.

## 2. Lọc lần chạy, tính hạng

1. Pha A: `python3 scripts/qp_ranks.py runs <các file> --domain <domain> --engine <engine>`. Đọc dòng "Nguồn": số lần chạy, khoảng ngày, cảnh báo dưới 35 ngày. Đọc từng dòng lần chạy: lần nào bị loại, vì sao, độ sâu quét 50 hay 100. Đưa các điểm này vào báo cáo ở điểm dừng.
2. Project một domain không phân biệt được ô thiếu với ngoài độ sâu. Script loại lần chạy có số keyword có hạng dưới 70% median. Lần bị loại nằm trong 3 lần mới nhất thì có thể site rơi thật: hỏi Lead ở điểm dừng. Lead kiểm trên SpySERP rồi chọn `--keep-recent` (rơi thật) hoặc `--drop "<ngày>"` (thiếu dữ liệu). Lệnh `table` dừng mã 3 nếu chưa có quyết định.
3. Pha B: `python3 scripts/qp_ranks.py table <các file> --domain … --engine … --keywords $W/bo-cam-ket.txt [--targets $W/url-target.csv] -o $W/hang.json --tsv $W/hang.tsv`.
4. Mốc so sánh mặc định là lần mới nhất trừ 28 ngày, chỉ nhận lần chạy hợp lệ trong ±7 ngày quanh mốc. Không có lần nào thì lệnh dừng mã 2. Xin Lead export thêm; không được thì `--no-compare` và ghi lý do vào flags. Mốc khác (ví dụ ngày bắt đầu kế hoạch trước) thì `--compare dd.mm.yyyy`.
5. `not_in_export` khác rỗng nghĩa là bộ đang đo lệch bộ hợp đồng. Ghi số keyword lệch vào `flags`. Không tự thay keyword.
6. Số hiện tại dùng median 3 lần chạy hợp lệ mới nhất. Số giá trị chẵn (một ô thiếu) thì lấy giá trị cao hơn (median_high), nên hạng luôn là số nguyên có thật. Muốn so với số team đã báo cáo một ngày thì chạy thêm `--k 1` và ghi cả hai cách đọc trong notes.

## 3. Gom template

1. `qp_ranks.py terms` in các cụm lặp nhiều nhất (bỏ phần đầu chung) kèm số keyword và số Top 10 của mỗi cụm. Đọc output này, không đọc cả `hang.tsv`. Cấu trúc hay gặp: "[sản phẩm] [hãng]", "[sản phẩm] [size]", "giá [sản phẩm]", "[A] và [B]", "mua [sản phẩm] ở đâu", câu hỏi "là gì / bao nhiêu / loại nào".
2. Viết `$W/rules.json`: `[{"id": "gia", "label": "đèn học [mức giá]", "rx": "\\d+\\s*(k|nghìn|triệu)"}, …]`. Rule hẹp đặt trước, rule rộng đặt sau. Rule cuối là `{"id": "khac", "label": "khác", "rx": "."}`.
3. Chạy lại `table … --rules $W/rules.json`. Lệnh in 25 keyword đầu chưa có template, cảnh báo khi "khác" vượt 10% và khi quá 16 template. Còn keyword lẻ thì chạy `terms --rules $W/rules.json`: lệnh chỉ xét keyword chưa khớp rule nào. Lặp tới khi hết keyword chưa có template.
4. Giữ 5–16 template. Template dưới 3 keyword thì gộp vào template gần nhất. Quá 16 thì gộp trong `rules.json`: scaffold dừng chứ không cắt bớt.
5. Scaffold gợi ý `status` theo bảng trong `qp-ly-thuyet.md` mục 2. Đổi trạng thái khác gợi ý thì ghi lý do vào `tip`. Xếp template theo mức đáng đẩy: nhiều keyword ở 4–20, đã có biến thể Top 3, URL đại diện rõ.

## 4. Lưới hạng

- Chọn 3–6 template tiêu biểu: template đã mở (có Top 3), template đang kẹt nhiều keyword nhất, template chưa có hạng nhưng site đã có trang.
- Mỗi tab 4–16 chip. `gap: true` khi site có trang đúng biến thể nhưng keyword chưa vào độ sâu: ứng viên lỗi Retrieve hoặc Canonical.
- `read` nói lưới cho thấy gì; `act` nói làm gì; `topic` ghi mã topic, ưu tiên, công sức ("T2 · P1 · công sức vừa").

## 5. Canonical

- `hub_urls` trong `hang.json` là danh sách URL giữ nhiều keyword cam kết nhất. Đây là ứng viên URL đại diện.
- Có `--targets`: mục `targets` trong `hang.json` đếm keyword Google trả URL khác URL kế hoạch, theo từng URL target. URL target có nhiều keyword lệch là ứng viên dòng canonical. Scaffold tự thêm flag cho các URL này.
- URL lật: export SpySERP chỉ giữ URL của lần chạy mới nhất. Muốn thấy lật thì so URL giữa các file export của các ngày khác nhau, hoặc dùng GSC (page theo query). Không có hai nguồn đó thì ghi "cần GSC" cho dòng này.
- Mỗi dòng canonical: query đại diện → URL Google đang chọn kèm hạng → vấn đề → quyết định → mã topic. Luật và quy trình lật URL: `qp-ly-thuyet.md` mục 4.

## 6. SERP

- Chọn đúng 3 query đại diện của 3 intent khác nhau (thương mại, so sánh hoặc chọn mua, thông tin).
- Đọc 6–10 kết quả đầu. Ghi loại trang, domain, dòng của site nếu có.
- `verdict` = intent + loại trang Google muốn. `so` = việc rút ra cho URL của site.
- Query địa phương: kết quả Firecrawl có thể lẫn video, tin tức và không đúng vị trí đo. Ghi giới hạn vào `meta`, hoặc xin Lead chụp SERP đúng vị trí.

## 7. Trang thật

1. `python3 scripts/site_check.py $W/pages home=https://… cate=https://… pdp=https://…`. Kiểm mọi URL đại diện có trong bảng ưu tiên và trang chủ.
2. Đọc: title, H1, H2 có đúng mảnh query không; robots, canonical; JSON-LD parse được không, có loại nào (Product, ProductGroup, BreadcrumbList); breadcrumb đúng tên chưa; link nội bộ theo vùng (menu, body, footer); trang nào link tới URL đại diện, bằng anchor gì; ảnh thiếu alt; phân trang.
3. Lỗi retrieve hay gặp: title là trang chờ ("One moment, please…", "Just a moment"), noindex, canonical trỏ trang khác, 404, site chưa go-live. Nghi trang chờ thì thử thêm `curl -A "Googlebot"` và ghi kết quả.
4. Dữ kiện trang thật ghi vào `matrix.rows[].diag`, khối `levers` và `retrieve.checked`.

## 8. Ma trận 8 trạm, augmentation, cặp so sánh

- 5–12 cụm. Mỗi cụm tối đa 2 trạm chính, 1 trạm phụ. Mỗi chấm có `why` dựa trên dữ kiện (hạng, URL, trang thật). `fix` là việc làm cụ thể, ghi đủ URL.
- Mỗi chẩn đoán có điều kiện bác bỏ: "điều gì xảy ra thì chẩn đoán này sai" (ví dụ "sau 14 ngày sửa title, median Top 10 của họ không đổi thì B2 không phải trạm chính"). Ghi vào hồ sơ mục Chẩn đoán, không cần lên deck.
- Augmentation map chỉ làm cho trang đang rank Top 10 cho một biến thể. Sắp khối có sẵn trước khi thêm khối mới.
- Cặp "X và Y" chỉ làm khi bộ cam kết có query so sánh.

## 9. Topic ưu tiên

1. Mỗi topic là một gói việc trên một URL hoặc một nhóm URL. Ghi keyword cam kết topic đẩy vào `$W/topics.json` dạng `{"T1": ["kw", …]}`. `qp_build.py --topics` kiểm: không keyword nào thuộc hai topic; `n_kw` = độ dài danh sách.
2. Thứ tự xếp:
   - **P0:** lỗi chặn hoặc lỗi làm rơi nhiều keyword cùng lúc (Retrieve, Canonical lật, JSON-LD hỏng trên template).
   - **P1:** việc nhỏ cho keyword đã ở hạng 4–10, và phủ biến thể trên trang đã thắng.
   - **P2:** việc nội dung lớn, hoặc việc trên trang đang giữ Top 3 (làm sau khi chụp baseline và sau kỳ đo).
3. Bộ cam kết có nhiều nhóm với trọng số nghiệm thu khác nhau thì ghi quy đổi vào `kpi` (nội bộ) và dùng nó khi xếp. Không xếp theo số keyword thô, không xếp theo volume.
4. Không đề xuất: blog chỉ kéo traffic; scale trang bằng AI; so sánh chê đối thủ; topic trùng intent với money page đang rank; nhân một khung H2 sang nhiều trang.

## 10. Đo lường

- Một regex cho mỗi template quan trọng, dán được vào bộ lọc query của GSC. GSC dùng cú pháp RE2: không dùng lookahead, lookbehind hay backreference. Viết `(?i)` ở đầu nếu cần.
- Timeline mẫu: chụp baseline trước khi sửa → giữ nhật ký thay đổi theo URL → chờ 14 ngày → đọc median các lần chạy hợp lệ → quyết mở rộng, dừng hay hoàn lại.
- Trước kỳ đo: trang đang giữ Top 3/5 chỉ thêm, không rút. Trên deck viết "kỳ đo" kèm ngày; chữ "nghiệm thu", "chỉ tiêu" chỉ nằm trong khối `kpi` hoặc thẻ `internal`.

## 11. Kế hoạch 2 tuần

- 5–12 dòng: Khi nào · Việc · Ai làm · Xong khi. "Ai làm" là người thật (Lead, dev, content). "Xong khi" kiểm được (URL đã sửa, regex đã lưu, ảnh chụp baseline).
- Việc chạm ngày đo thì xếp sau ngày đo.
- Thẻ nhắc chỉ tiêu, nghiệm thu hay hợp đồng đặt `internal: true`.

## 12. Dựng, kiểm, lưu

1. `qp_scaffold.py` dựng `<CLIENT>_qp-chan-doan_v<N>.json` với mọi số đã điền: measure, status_row, beat_stats, idea, templates (trạng thái gợi ý), lưới hạng (chip lấy hạng median của bảng hạng), URL hub ở canonical, tên cụm và số liệu ở ma trận, regex nháp, flags. Kiểm lại trạng thái template gợi ý và các tab lưới (`--tabs` để chọn tab khác).
2. Viết các ô `TODO` theo `schema-qp-project.md`, trong một lần ghi file. Xoá khối tuỳ chọn không dùng. Thêm `aug`, `pairs`, `retrieve`, `qa`, `guides` khi có dữ liệu. Keyword, hạng và volume trong các khối này phải lấy từ `hang.json`.
3. `qp_build.py <file.json> --ranks … --topics … --web-out … --handoff … --numbers … --shots …` chạy check (schema, độ dài, TODO, RE2), verify (số khớp bảng hạng, trạng thái, ghi chú, ngày đo, topic không trùng), dựng bản nội bộ và bản web, quét chữ dễ lộ điều khoản trên bản web, sinh file bàn giao content và bảng con số → nguồn, audit, chụp slide Template, Ưu tiên, Kế hoạch. Audit không bắt chữ chồng nhau: xem ảnh các slide đó.
4. Viết hồ sơ theo `_TEMPLATES/qp-chan-doan.md`: mục 2 dán từ `$W/con-so-nguon.md` rồi thêm dòng cho số tự viết; mục Chẩn đoán có điều kiện bác bỏ và đủ URL; flags, điểm cần kiểm tay, tự chấm checklist.
5. Tự chấm `checklist-qc.md`. Cập nhật `index.md` (bảng D, Ghi chú công đoạn) và `log.md`.

## 13. Chạy ở workspace GTV (gộp nhiều dự án)

Bản clone của team bỏ qua mục này.
- Hạng: skill `spyserp-rank-pull` kéo JSON chuẩn hoá về `Deliverables/GTV-Brand/PSP-Performance-Hub/spyserp/`. `qp_ranks.py` đọc thẳng file JSON đó (`--project <id>`).
- Hợp đồng và email: chỉ đọc qua `gws`. Không gửi, sửa, xoá, share.
- Đầu ra: `Deliverables/GTV-Brand/QP-<chủ đề>-<YYYY-MM>/` gồm `projects/<slug>.json`, `projects/<slug>_notes.md`, `projects/<slug>_work/`, deck từng dự án và deck tổng quan (`qp_render.py overview|all`).
- Đăng lên site đào tạo nội bộ chỉ khi Vincent yêu cầu, dùng `--web` và theo luật của site đó.
