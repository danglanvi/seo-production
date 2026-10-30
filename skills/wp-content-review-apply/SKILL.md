---
name: wp-content-review-apply
description: "Đưa thay đổi SEO title, meta, H1, slug, link, đoạn văn, trường ACF/Elementor của site WordPress qua trang duyệt có nút Duyệt/E, rồi ghi an toàn bằng WP-CLI: dựng dữ liệu, QA, plan, chạy thử, ghi, kiểm. Dùng trước mọi lần sửa nội dung trên site có quyền server."
metadata:
  version: "1.7.2"
---

# wp-content-review-apply — duyệt trước, ghi sau

Mọi thay đổi content hoặc meta phải qua trang duyệt có nút Duyệt/E trước khi ghi lên site. Skill này gói 2 lượt đã chạy thật ngày 17/10/2026:

- Chế độ **trường sống** trên một site agency: 148 meta Rank Math, 48 H1, link nội bộ ở 9 bài, 47 trường của một trang tiếng Anh.
- Chế độ **khối nguồn** trên một site khác: 327 khối chữ của 2 trang dựng từ HTML nguồn.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-content-review-apply/scripts/`. Mẫu trang duyệt: `templates/trang-duyet.html`. Test offline của mọi script: `python3 -B skills/wp-content-review-apply/tests/run_all.py` (cần python3, php CLI có intl, node).

Skill chỉ chạy trong Claude Code, vì trang duyệt là artifact claude.ai có database.

## Khi nào dùng

- Sửa SEO title, meta description, H1, slug, đoạn văn, link nội bộ, trường ACF hoặc widget Elementor trên site WordPress có quyền SSH + WP-CLI. Thường là bước ghi của công đoạn onpage (`seo-onpage`) và internal link (`internal-linking`).
- Viết lại một trang dựng từ HTML nguồn và cần người duyệt sửa chữ từng khối.
- Không dùng khi:
  - chỉ có quyền REST hoặc tài khoản wp-admin: dùng `wp-publish-workflow-kit` theo CLAUDE.md §11;
  - chỉ sửa CSS, JS, cấu hình kỹ thuật: dùng `wp-pagespeed`, `wp-security-hardening`;
  - viết bài mới chưa lên site: việc của repo content.

## Đọc trước

- `00-client-context/wp-server.md`: lệnh WP-CLI, plugin SEO (Rank Math, Yoast), plugin đa ngôn ngữ, plugin cache, link trang duyệt của site. Chưa có thì tạo từ `_TEMPLATES/wp-server.md`.
- `references/hop-dong-du-lieu.md`: collection, dạng tài liệu, trạng thái duyệt, bảng `target`. Đọc ở Bước 3.
- `references/ghi-an-toan.md`: luật ghi, lệnh chạy, đổi `lastmod` sitemap (mục 3b), rollback, bẫy WordPress. Đọc ở Bước 5.
- `references/thao-tac-ghi.md`: dạng op của `apply.php` (`text`, `fix`, `el_rm`, `el_restore`), `locate.php`, log. Đọc ở Bước 5 khi dựng op tay.
- `references/don-html-hang-loat.md`: chế độ dọn HTML thừa.
- Skill `artifact-capabilities` trước khi sửa code trang duyệt.
- `00-client-context/` và KB snapshot của khách (nếu có) để đối chiếu số liệu.

## Chọn chế độ

| Chế độ | Khi nào | Nguồn thật | Collection |
|---|---|---|---|
| Trường sống | Sửa dữ liệu đang nằm trong DB WordPress | DB production | `report`, `reviews` |
| Khối nguồn | Trang dựng từ file nguồn rồi mới ghi vào WordPress | File nguồn trong repo của site | `pages`, `edits` |
| Sửa trực tiếp | Người duyệt muốn sửa chữ ngay trên giao diện trang, không qua thẻ | Bản HTML của trang | file `edits` xuất từ `scripts/sua_truc_tiep.py` |
| Dọn HTML thừa | Bài có rác HTML (dán từ Google Docs, entity mã hoá 2 lần, thẻ rỗng), chữ hiển thị giữ nguyên | DB production | Không dùng thẻ. Người vận hành duyệt cả lô qua 5–6 URL mẫu |

Chế độ dọn HTML thừa: làm theo `references/don-html-hang-loat.md`, không đi qua Bước 2 đến Bước 4.

Chế độ sửa trực tiếp:

1. Lấy HTML đã render của trang (GET chỉ đọc) hoặc mảnh nội dung từ file nguồn.
2. Dựng file sửa: `python3 skills/wp-content-review-apply/scripts/sua_truc_tiep.py build --html <trang.html> --page <mã> --title "<tên>" --base https://<site>/ --out <file>`. Mở file bằng Chrome cho người duyệt. Người duyệt bấm E, sửa chữ, rồi bấm "Tải HTML" hoặc "Sao chép cho Claude".
3. Xuất bản sửa: `sua_truc_tiep.py apply <file đã tải> --out <thư mục>`. Mỗi khối thành một tài liệu dạng `edits`. Ghi chú của người duyệt in riêng để xử lý tay.
4. Tìm chữ cũ trong nguồn thật (DB hoặc file nguồn) rồi đi tiếp như chế độ khối nguồn. Khối có `dup` = `k#n` là lần thứ n của chữ đó trên trang. Sửa đúng lần thứ n, không thay mọi chỗ.
5. Viết lại câu cho mượt và chạy bước rà câu trước khi ghi. Sửa luôn FAQ và đoạn khác của trang có cùng ý. Báo lại người duyệt chỗ đã đổi so với chữ họ gõ, để họ duyệt lần cuối.

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Jev | `seo-text-qa` cho chuỗi mới ở Bước 2. `nbsp-intent` và `inline-style-residue` cho ca mơ hồ khi dọn HTML. `approved-applied` xếp thứ tự đọc các dòng `doc-tay` của `doi_chieu.py` | Dùng, luôn có `--budget`. Cả 4 rubric chưa có entry hiệu chuẩn trong `tools/ai-assist/calibration-defaults.json`, nên không rubric nào là cổng tự động. Claude đọc lại mọi nhãn dẫn tới ghi hoặc xoá |
| EmbeddingGemma | So chữ duyệt với live | Không dùng. Ghi và đối chiếu cần khớp đúng từng chữ (NFC, regex, cụm 6 chữ). Độ giống nghĩa không chứng minh chữ đã lên |
| GLM Flash | Trích câu | Không dùng. Skill không có việc trích câu tự do |
| Claude | Soạn đề xuất, đọc ghi chú, quyết rebase, dựng op, đọc nhãn Jev | Dùng |

Cách chạy Jev: `tools/ai-assist/README.md`.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,ssh,wp-cli,node?,jev?,pagespeed-api?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Sau đó làm Bước 1 đến Bước 6 bên dưới.

## Bước 1 — lấy giá trị hiện tại

1. Chạy `scripts/collect.php` qua `wp eval-file`. Script trả giá trị thô từ DB: title, slug, URL, meta Rank Math, robots, ngôn ngữ WPML, md5 nội dung. Site dùng Yoast: thêm key meta Yoast vào bước soạn theo `hop-dong-du-lieu.md` mục 3.
2. Lấy `raw` từ DB, không lấy từ HTML đã render. HTML render đã thay biến của plugin SEO và lọc ký tự.
3. Chế độ khối nguồn: tách khối từ file nguồn, giữ mã khối ổn định khi chỉ đổi chữ.

## Bước 2 — soạn đề xuất

1. Mỗi trường có `before`, `raw` và một hoặc hai phương án (`A`, `B`) hoặc `proposed`. Thẻ A/B có `options` ở mức thẻ hoặc phần (`references/hop-dong-du-lieu.md` mục 1).
2. Chạy mọi câu chữ mới qua skill `humanizer` nếu có trong runtime. Lô chữ ngắn (title, meta, mô tả chuyên mục, FAQ) chạy theo chế độ lô của humanizer (`references/chu-ngan-web.md` của skill đó). Không miễn vì chữ ngắn. Không có humanizer thì tự rà theo luật câu của AGENT.md. Ghi kết quả vào `qa.humanizer` của từng trường.
3. Năm trong title và meta: dùng biến năm của plugin SEO (Rank Math `%currentyear%`), trừ khi người duyệt chọn khác.
4. Kiểm độ dài: SEO title tối đa 65 ký tự, meta tối đa 160 ký tự, đếm sau khi thay biến năm.
5. Đối chiếu số liệu, chức danh, tên dịch vụ với `00-client-context/` và KB của khách. Số không có nguồn thì đưa vào phần "cần quyết", không tự viết. Gom các số có nguồn vào `facts.json` của đợt cho bước 7.
6. Chạy Jev `seo-text-qa` cho chuỗi mới (lỗi gõ, thiếu dấu), có `--budget`. Chạy sau humanizer, ở mọi vòng sửa. Đặt tên thương hiệu của site vào `state.brands`. Cách chạy: `tools/ai-assist/README.md`.
7. Chạy cổng QA thẻ. Chỉ nạp thẻ khi lệnh trả mã 0:
   `python3 -I skills/wp-content-review-apply/scripts/the_qa.py <thư mục report> --entity client --facts facts.json --site https://<site>`
   - Script kiểm: có `qa.humanizer`, chữ ở dạng NFC, độ dài (thêm px khi có `skills/seo-onpage/scripts/serp_pixel.py`), không mất link của `before`, mỗi số có trong `before` hoặc `facts.json`, `copy_guard`.
   - Instance website nội bộ dùng `--entity gtv`, `tag` hoặc `academy` theo entity ở bảng A của `index.md`.
   - Repo không có `copy_guard.py` (skill `website-conversion-copywriting`) thì thêm `--khong-copy-guard`. Khi đó rà chữ cấm và cam kết theo `00-client-context/` bằng tay.
   - Đạt thì chạy lại với `--ghi <thư mục ra>` để điền khối `qa` vào thẻ, rồi nạp bản trong thư mục ra.
8. Kiểm thẻ mới không đổi chữ đã duyệt. Dựng sổ từ thẻ đã có trên trang bằng lệnh `so_duyet.py build` ở Bước 5 bước 1, rồi chạy:
   `python3 -I skills/wp-content-review-apply/scripts/so_duyet.py the --so so-duyet.json --report <thư mục thẻ mới>`
   Mã 1 thì giữ chữ đã duyệt. Chỉ đổi khi có lý do kiểm được (vượt pixel, sai fact) và không mất từ khoá hay entity. Ghi lý do vào `doi_chu_duyet` của trường.

## Bước 3 — nạp trang duyệt

1. Site đã có trang duyệt (link trong `wp-server.md`): đọc artifact (`action: read`) trước khi publish lại.
2. Site chưa có: chép `templates/trang-duyet.html` vào thư mục đợt, sửa `SITE` ở đầu script, publish với capability `db` và `user`. Ghi link vào `wp-server.md`. Danh sách phần lấy từ `report/summary.sections`. `ORDER` chỉ là thứ tự mặc định.
3. Thẻ ảnh (ảnh trước/sau, ảnh chụp trang): publish file ảnh kèm trang bằng tham số `files` của Artifact, ghi đường dẫn tương đối vào `img` của thẻ.
4. Sửa code trang (status mới, truy vấn reviews, danh sách phần): kiểm số đếm offline trước khi publish. Số đếm trên trang phải khớp bản sao db:
   `node skills/wp-content-review-apply/scripts/kiem_trang_duyet.mjs <trang-duyet.html> <thư mục bản sao db>`
5. Lint thẻ trước mọi lần nạp. Mã 1 thì sửa builder rồi chạy lại:
   `python3 -I skills/wp-content-review-apply/scripts/check_cards.py <thư mục report> [--reviews <data/reviews>]`
   Script bắt: thiếu id, trùng id, hai trường cùng key mà builder không đặt `key#n`, A/B thiếu `options`, tài liệu quá 256 KiB.
6. Nạp tài liệu bằng ArtifactData `batch`, kèm `if_version` cho tài liệu đã có. Không ghi đè collection `reviews` hoặc `edits`, vì đó là dữ liệu người duyệt nhập.
   - Đợt lớn: dựng lô bằng `python3 -I skills/wp-content-review-apply/scripts/seed_batches.py --docs <thư mục report> --collection report --remote <kết quả list.json> --only-missing --ghi`. Mỗi `_writes_NN.json` là một `batch`.
   - Báo người vận hành số lô trước khi gửi. Mỗi lô là một lần bấm duyệt.
7. Mỗi mục cho sửa cả giá trị (nút E), không chỉ chọn A/B. Mở quyền sửa cho mọi trường định đổi (title, URL, H1, meta). Trường không đổi hiện "Giữ nguyên".
8. Gửi người duyệt link trang duyệt và số mục theo phần.

## Bước 4 — đọc kết quả duyệt

1. Khi người duyệt báo đã duyệt, đọc `reviews` (hoặc `edits`) bằng ArtifactData `list` với `out_dir` vào thư mục `data/` của đợt.
2. Đối chiếu với live sau mỗi lần xuất reviews. Script chỉ đọc, 1 request/giây, chỉ gọi host của `--site`:
   `python3 -I skills/wp-content-review-apply/scripts/doi_chieu.py <thư mục bản sao db> --out <thư mục> --site https://<site> [--khoa khoa.txt]`
   - Duyệt tới đâu áp tới đó. Thẻ `approved` hoặc `edited` có nhãn `chua-len` hoặc `mot-phan` nằm ở mục "Hàng ghi ngay" của `ket-qua.md`. Ghi các thẻ này trong lượt đang chạy.
   - Chỉ giữ lại thẻ có ghi chú hỏi lại (bước 3), thẻ có điều kiện ngày (bước 6) và thẻ đang có khoá của phiên khác (`--khoa`).
   - Nhãn `doc-tay`: Claude mở trang thật và đọc. Không gắn `applied` theo phỏng đoán.
3. Mục có ghi chú: đọc ghi chú trước. Ghi chú hỏi lại hoặc nhờ viết thêm thì đưa vào danh sách giữ lại, trả lời người duyệt, không ghi.
4. Mục `rejected` không ghi.
5. Mục `approved` hoặc `edited` cộng lời "xử lý" của người duyệt trong chat là đủ quyền ghi. Không trình thêm một vòng plan để xin duyệt lại.
6. Trước khi ghi, tìm id của mục trong mọi nguồn duyệt: đề xuất của trang duyệt, ghi chú, file quyết định của đợt. Nếu nguồn ghi điều kiện ngày ("chờ 18/11", "áp sau <ngày>") và chưa tới ngày, giữ mục lại. Ghi mục vào HANDOFF "Bước tiếp" kèm ngày. Người ghi không tự diễn giải lại điều kiện ngày.

Chữ người duyệt tự sửa:

| Nguồn | Cách xử lý |
|---|---|
| Thẻ `edited` trên trang duyệt | Ghi nguyên văn `values`, chỉ chuẩn hoá NFC và khoảng trắng. Thấy lỗi gõ hoặc sai fact thì hỏi lại hoặc tạo thẻ mới, không tự sửa |
| File sửa trực tiếp (`sua_truc_tiep.py`) | Viết lại cho mượt, chạy humanizer, sửa chỗ cùng ý (FAQ, meta). Báo lại chỗ đã đổi so với chữ người duyệt gõ |

## Bước 5 — plan, chạy thử, ghi

1. Dựng sổ giá trị đã duyệt từ toàn bộ thẻ của trang (không chỉ lô này), rồi sinh plan có kiểm sổ:
   `python3 -I skills/wp-content-review-apply/scripts/so_duyet.py build --report <dir> --reviews <dir> --out so-duyet.json [--cu <sổ cũ>]`
   `python3 -I skills/wp-content-review-apply/scripts/plan.py --reviews <dir> --report <dir> --out plan.json --so so-duyet.json [--hold hold.json]`
   - Plan dừng khi một trường có 2 giá trị đã duyệt khác nhau, và giữ lại mục duyệt để trống.
   - Op ghi đè giá trị đã duyệt mới hơn của thẻ khác, hoặc op không qua trang duyệt, vào `holds` kèm lý do. Không ghi các op này.
2. Trước mọi lần ghi production, tra reviews theo URL hoặc `post_id` sẽ chạm.
   - Đã có quyết định (`approved`, hoặc `rejected` kèm ghi chú) thì làm theo quyết định đó. Lệnh chung kiểu "sửa hết lỗi còn lại" không ghi đè quyết định cũ.
   - Chỉ ghi đúng trường của thẻ, không ghi thêm trường khác của cùng bài.
   - Ghi nhầm rồi hoàn tác: báo người duyệt ngay trong chat.
3. Thao tác `plan.py` không phủ (thay một câu trong đoạn, sửa đích danh, gỡ hay chèn lại widget Elementor): dựng `ops.json` theo `references/thao-tac-ghi.md`. Tìm nơi lưu chữ cũ bằng `scripts/locate.php` trước. Chạy `so_duyet.py check --so so-duyet.json --plan ops.json` trước khi ghi.
4. Backup trước khi ghi: export các dòng sẽ chạm (`mysqldump` theo bảng, hoặc dump theo ID bằng `eval-file`) và giữ log `before` của lượt chạy thử. Server tắt `proc_open` thì `wp db export` không chạy (`references/ghi-an-toan.md` mục 2).
5. Chạy thử với `DRY=1` và `OUT=<log-dry.json>`. Đặt biến sau `sudo -u www`, lệnh mẫu ở `references/ghi-an-toan.md` mục 2. Mọi dòng `skip` phải có lý do đã hiểu. `skip` do "giá trị hiện tại khác bản lúc soạn" nghĩa là site đã đổi sau lúc duyệt: xử lý theo luật rebase ở `references/ghi-an-toan.md` mục 4b.
6. Ghi: `DRY=0` với `OUT` mới. Script xoá object cache rồi mới purge toàn bộ cache trang một lần ở cuối. Nếu hồ sơ server cấm purge toàn site, chạy thêm `PURGE=0`, rồi purge theo URL của các trang đã ghi và làm nóng lại theo `references/ghi-an-toan.md` mục 1.
7. Thay đổi giao diện hoặc template thì ghi staging trước, gửi ảnh trước/sau, rồi mới ghi production. Chỉ đổi meta thì ghi thẳng production.
8. Cổng ghi hàng loạt không qua thẻ (dọn HTML, thay chuỗi trên nhiều bài): chạy thử so md5, so `the_content` render trên server trước và sau, chụp so 5–6 URL mẫu. Chỉ ghi production khi bố cục không đổi. Dọn HTML theo `references/don-html-hang-loat.md`.
9. Trang đã đổi chữ thật mà sitemap còn `lastmod` cũ: đổi `post_modified` bằng `scripts/set_post_modified.php` với TSV có giá trị cũ. Làm theo `references/ghi-an-toan.md` mục 3b, gồm xoá cache sitemap, purge và kiểm ở edge.

## Bước 6 — kiểm và đóng đợt

1. Tầng cache: đọc mục "Tầng cache sau khi ghi" của `wp-server.md`. CDN giữ HTML mà site chưa tự purge thì purge theo URL và kiểm giờ lưu của CDN. Site có CSS gọn theo path thì regen path có thay đổi thẻ hoặc class. Lệnh và bẫy: `references/ghi-an-toan.md` mục 1 bước 4b. Hồ sơ chưa có mục này thì hỏi người vận hành site có CDN giữ HTML không, rồi điền hồ sơ.
2. Kiểm bằng HTTP: `python3 -I skills/wp-content-review-apply/scripts/verify.py --plan plan.json --out verify.json`. Script kiểm mã 200, title, meta, H1, link, 301 khi đổi slug. Máy kiểm ở cùng vùng origin chỉ thấy bản origin. Site có CDN chia vùng thì kiểm thêm bản edge theo bước 1.
3. Kiểm robots và canonical ở 5 biến thể cache: `python3 -I skills/wp-pagespeed/scripts/cache_variants.py <url sạch> ...`. `verify.py` chỉ đọc một bản cache, còn bot và điện thoại có thể nhận bản khác.
4. Chạy lại `doi_chieu.py` trên bản sao db mới. Thẻ vừa ghi phải có nhãn `da-len`.
5. Cập nhật trang duyệt: gắn `applied` cho mục đã ghi. Chỉ gắn khi live có đúng chữ duyệt ở bản bỏ cache và bản có cache. Mục đã bị thẻ duyệt sau thay thế: không ghi chữ cũ, không gắn `applied`, ghi "thay bằng <id thẻ mới>" rồi đóng.
   - Ghi `mark_applied.json` (`[{"id", "status": "applied", "note": "[Claude hh:mm] <chỗ ghi, cách verify, rollback>"}]`) và `kiem-doc-lap.md` có mục "Kết luận" ghi đạt vào thư mục đợt. Thiếu kết luận đạt thì script bỏ cả đợt.
   - Query `reviews` một lần (`status in [approved, edited]`, `limit 1000`), lưu ra `versions.json`.
   - Chạy `python3 -I skills/wp-content-review-apply/scripts/mark_batch.py --lane <thư mục đợt> --versions versions.json --out <thư mục lô ngắn>` để xem kế hoạch và số lô. Đúng thì chạy lại với `--ghi`.
   - Gửi từng `_writes_NN.json` bằng ArtifactData `batch`, lúc người vận hành đang trực tuyến. Script giữ `note` cũ của người duyệt và nối id vào sổ `applied-ids.txt`. Lô bị từ chối thì xoá id của lô đó khỏi sổ trước khi chạy lại.
6. Lưu đợt ở `06-onpage-internal-link/apply-<YYYY-MM-DD>/`: plan, sổ duyệt, log chạy thử, log ghi, verify, kết quả đối chiếu. Thêm dòng bảng D `index.md`, append `log.md`, cập nhật `HANDOFF.md` nếu đợt kéo dài.

## Tự phản biện trước khi trình

Chấm lô thẻ trước khi nạp lên trang duyệt, và chấm plan trước khi ghi, theo checklist dưới. Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Có output của agent khác cho cùng lô thì so từng mục trước khi trình.

Bản tốt nhất phải có:
- [ ] Mỗi trường chữ mới có `qa.humanizer`, humanizer chạy trước Jev ở mọi vòng, và `the_qa.py` trả 0. Nguồn lỗi: 17/10 người duyệt nhắc 3 lần vì thẻ lên trang duyệt khi chữ chưa humanize; vòng sửa 4 và 5 chỉ chạy Jev.
- [ ] Không trường nào mất link nội bộ của `before`, không có số ngoài `before` và `facts.json`, không vượt độ dài sau khi thay biến năm. Nguồn lỗi: 18/10 thẻ `r7s-m1-hero` mất link nội bộ; 60 meta viết lại 3 vòng vì quá 160 ký tự.
- [ ] Builder đặt `key#n` cho trường trùng key, mỗi thẻ có id, thẻ A/B có `options`, và `check_cards.py` trả 0. Nguồn lỗi: 18/10 36 thẻ trùng key, 8 thẻ đã duyệt phải duyệt lại; 17/10 thẻ A/B chỉ hiện A.
- [ ] Không thẻ mới nào đổi chữ đã duyệt khi thiếu `doi_chu_duyet` (`so_duyet.py the` trả 0). Nguồn lỗi: 18/10 thẻ A1, A2, A4 viết lại chữ người duyệt đã duyệt, làm lại khoảng 25 phút.
- [ ] Trang duyệt mở quyền sửa mọi trường định đổi, và số đếm trên trang khớp bản sao db (`kiem_trang_duyet.mjs`). Nguồn lỗi: 17/10 trang bản đầu chỉ mở meta; 20/10 bộ đếm bỏ 117 thẻ đã áp.
- [ ] Plan chạy với `--so`, không có op ghi đè giá trị đã duyệt mới hơn. Nguồn lỗi: 19/10 lượt đêm ghi đè 37 thẻ title, meta người duyệt duyệt ngày 17/10.
- [ ] "Hàng ghi ngay" của `doi_chieu.py` rỗng sau lượt ghi, hoặc mỗi thẻ còn lại có lý do giữ. Nguồn lỗi: 19/10 23:15 người duyệt báo nhiều mục đã duyệt mà chưa được sửa.

## Gate

- [ ] Không ghi mục nào chưa có trạng thái `approved` hoặc `edited` trong trang duyệt.
- [ ] Mọi câu chữ mới đã qua bước rà câu. Số liệu khớp `00-client-context/` hoặc KB.
- [ ] Có backup và log `before` trước khi chạy `DRY=0`.
- [ ] Lượt chạy thử không có `skip` chưa giải thích.
- [ ] Đổi slug có 301 từ URL cũ, đã kiểm 1 bước nhảy.
- [ ] `verify.py` không còn dòng lệch, hoặc mỗi dòng lệch có lý do trong báo cáo.
- [ ] `cache_variants.py` đạt trên URL sạch đã ghi: robots và canonical giống nhau ở 5 biến thể.
- [ ] Site có CDN giữ HTML mà chưa tự purge: URL đã ghi được purge ở CDN, giờ lưu của CDN mới hơn giờ purge ở bản desktop và mobile. Site có CSS gọn theo path: path đổi thẻ hoặc class đã regen hoặc đã ghi vào file phối hợp. Lỗi đã gặp: từ 26/10 site mẫu GTV giữ HTML ở CDN 1 ngày cho khách ngoài châu Á, gồm Googlebot ở Mỹ.
- [ ] Khi nhiều phiên cùng ghi một site: đã đọc khoá của phiên khác, và việc phụ thuộc bước khác chỉ ghi production sau khi người kiểm độc lập của bước đó báo đạt (`references/ghi-an-toan.md` mục 4b).
- [ ] Không mục nào ghi trước ngày hẹn ghi trong nguồn duyệt. Lỗi đã gặp: thẻ `cm21-cp-backlink-3t` lên production 23/10 trong khi đề xuất đã duyệt ghi "chờ 18/11".
- [ ] Mục gắn `applied` đã kiểm live. Thẻ bị thẻ duyệt sau thay thế được đóng, không ghi. Lỗi đã gặp: thẻ cũ `v2-qp-titles` suýt ghi đè title và H1 của thẻ `m24` duyệt sau.
- [ ] Thẻ có chữ mới chỉ lên trang duyệt sau khi `the_qa.py`, `check_cards.py` và `so_duyet.py the` cùng trả 0.
- [ ] Plan chạy với `--so`, không ghi op nằm trong `holds`. `ops.json` tự dựng đã qua `so_duyet.py check`.
- [ ] Đã chạy `doi_chieu.py` sau lần xuất reviews cuối. Mọi thẻ đã duyệt mà chưa lên đều có lý do giữ.
- [ ] Ghi hàng loạt không qua thẻ: có file `BK`, 5–6 URL mẫu không đổi bố cục, và khi dọn HTML thì `compare_autop.php` ra `bad = 0`. Lỗi đã gặp: 19/10 ghi 130 bài, một bài đổi bố cục, phải rollback.
- [ ] Gắn `applied` bằng `mark_batch.py` sau khi có kết luận kiểm đạt. `note` cũ của người duyệt còn nguyên.

## Anti-patterns

- Ghi theo bản soạn trong chat khi người duyệt chưa duyệt trên trang.
- So `before` bằng HTML render. Biến của plugin SEO và entity HTML làm lệch.
- Ghi `post_title`, `post_content` bằng `wp_update_post` khi chỉ cần đổi chữ: hàm này đổi ngày cập nhật và lọc HTML khi WP-CLI không có `unfiltered_html`.
- Publish lại trang duyệt từ bản local cũ, làm mất bản người duyệt đã sửa.
- Gọi `litespeed_purge_post` hoặc bước purge của một gói có sẵn khi chưa đọc option `litespeed.conf.purge-post_all`. Nếu option bằng 1, purge một bài sẽ purge toàn site.
- Nạp file vào ArtifactData bằng đường dẫn tương đối. Dùng đường dẫn tuyệt đối cho `file_path` và `out_dir`.
- Đặt khoá thẻ theo chữ (`key`) khi một chữ lặp nhiều lần trên trang. Dùng `key#n` (lần thứ n) để mỗi chỗ có một khoá riêng.
- So chữ chưa chuẩn hoá Unicode. Chữ tiếng Việt từ trình duyệt, Word hay DB có thể ở dạng NFD. Chuẩn hoá NFC và gộp khoảng trắng trước khi so.
- Sửa nội dung thẻ người duyệt đã duyệt. Cần đổi thì tạo thẻ mới, giữ thẻ cũ làm lịch sử.
- Hai phiên cùng ghi một trang duyệt. Đọc tài liệu ngay trước khi ghi, ghi kèm `if_version`, và chỉ ghi collection của phiên mình.
- Ghi template hay giao diện thẳng lên production. Thay đổi giao diện đi qua staging bằng `wp-staging-deploy`.
- Lấy chuỗi cũ của `post_content` từ file đọc bằng Python `open()` text mode. Lệnh này đổi `\r\n` thành `\n`, nên DRY báo 0 vị trí. Lấy từ JSON đọc thẳng DB.
- Nối hai câu bằng xuống dòng. LiteSpeed minify xoá `\r\n`, nên hai câu dính nhau trên trang. Nối bằng dấu cách.
- Kết luận "đã lên site" chỉ từ máy ở cùng vùng origin khi site có CDN chia vùng. Máy đó đi thẳng origin, còn Googlebot ở vùng khác nhận bản ở edge.
- Verify hay bỏ cache bằng `?utm_*`, `fbclid`, `gclid`. Bản `noindex` của URL có query vào cache của URL sạch.
- Ghi staging khi staging là clone cũ. Chép từ production đúng bài và option sắp ghi trước khi DRY trên staging.
- Ghi SQL thô khi site bật object cache mà không xoá key, hoặc purge trang trước khi xoá object cache.
- Rollback bằng cách chép đè cả file hay cả bảng khi phiên khác có thể đã sửa sau mình. So md5 trước khi trả.
- Viết `apply*.php` riêng cho từng lô. Dựng `ops.json` rồi chạy `apply.php` (`references/thao-tac-ghi.md`).
- Đặt `PLAN`, `DRY`, `OUT` trước `sudo -u www`. sudo xoá các biến này.
- Lấy `version` để gắn `applied` bằng cách get từng thẻ hoặc query `__name__ in`. Dùng một query theo `status` rồi `mark_batch.py`.
- Sửa trang duyệt riêng của một site mà đọc reviews bằng một truy vấn `limit(1000)`, hoặc viết cứng danh sách phần. Trang hơn 1.000 thẻ mất số đếm, phần thêm sau không bấm được.
- Quét postmeta bằng `LIKE` trên production. `locate.php` trên production luôn chạy với `SKIP_META=1`.
- Đổi `post_modified` bằng `UPDATE` không có điều kiện giá trị cũ, hoặc không lưu giá trị cũ trước khi ghi. Dùng `set_post_modified.php` với TSV.

## Changelog

- v1.7.2 (2026-10-27): thêm `scripts/set_post_modified.php` (đổi `post_modified` theo TSV, điều kiện cả 2 cột giá trị cũ, `MODE` bắt buộc, `clean_post_cache`, không flush) và `tests/test_post_modified.py` 5/5; stub `$wpdb` thêm `get_row`, `query`. `ghi-an-toan.md` mục 3b, Bước 5 mục 9, 1 anti-pattern. Nguồn: lane đổi `lastmod` 4 trang site agency mẫu 27/10 trên production (DRY 4/4, ghi 4/4 `rows=1`, `lastmod` mới ở origin và edge, kiểm độc lập đạt). Bản port thêm `MODE` bắt buộc: bản gốc coi thiếu `MODE` là ghi thật.
- v1.7.1 (2026-10-27): `apply.php` thêm `FLUSH=0` (mặc định vẫn xoá object cache), test 2 ca. `ghi-an-toan.md` mục 1 bước 4 ghi điều kiện dùng. Hồ sơ server thêm dòng "Cache phụ thuộc nội dung". Lý do: đề xuất bỏ hẳn `wp_cache_flush()` sai trên site có cache mảnh bám `save_post`.
- v1.7 (2026-10-27): Bước 6 mục 1 "Tầng cache": purge CDN theo URL bằng lệnh trong hồ sơ server, kiểm giờ lưu ở edge, regen CSS gọn cho path đổi thẻ hoặc class. `ghi-an-toan.md` mục 1 bước 4b. Mục tầng cache mới trong mẫu `_TEMPLATES/wp-server.md`. Gate và anti-pattern thêm 1 mục. Nguồn: site agency mẫu chuyển apex sang CDN chia vùng 26/10; đợt semantic HTML 27/10 chuỗi ghi dừng ở bước CDN vì đường dẫn tương đối và phải phối hợp regen CSS gọn bằng tay.
- v1.6 (2026-10-25): nd-1 engine `apply.php` (vá `$has` trước khi lấy tham chiếu, op `text`, `fix`, `el_rm`, `el_restore`, field `usermeta`/`option`, log ra `OUT`, `FAIL_ON_SKIP`), `locate.php`, `references/thao-tac-ghi.md`. nd-2 `doi_chieu.py` và luật "duyệt tới đâu áp tới đó" ở Bước 4, `so_duyet.py` + `plan.py --so`. nd-3 `the_qa.py` và khối `qa` của trường, ma trận chữ người duyệt tự sửa, humanizer `references/chu-ngan-web.md`. wpr-1 trang duyệt lấy phần từ `summary.sections`, chia 3 truy vấn reviews, status `applied`; `check_cards.py`, `kiem_trang_duyet.mjs`, `so_duyet.py the`; tra quyết định cũ trước khi ghi; cổng ghi hàng loạt; WPForms, `proc_open`, marker JSON vào `ghi-an-toan.md`. wp-review-1 `fid` (`key#n`) trong trang. ops2-9 `mark_batch.py`, thẻ ảnh `img`. hs-10 `seed_batches.py --only-missing`, `status: applied` trong `hop-dong-du-lieu.md`. perf-10 `references/don-html-hang-loat.md` và 6 script dọn HTML có bất biến wpautop, rollback so md5. sec-5 biến sau `sudo`, `ssh -n`, base64, đếm backup vào `ghi-an-toan.md` mục 2. nd-5 bẫy Permalink Manager Pro và Rank Math vào `ghi-an-toan.md` mục 4. Thêm Phân việc model, Tự phản biện, 5 mục Gate. Test offline: `tests/run_all.py`.

- v1.5 (2026-10-24): Bước 4 kiểm điều kiện ngày trong nguồn duyệt trước khi ghi. Bước 6 chỉ gắn `appliedAt` sau khi kiểm live, đóng thẻ bị thẻ duyệt sau thay thế. `ghi-an-toan.md` mục 4b: luật rebase 4 trường hợp khi `raw_before` lệch live. Gate thêm 2 mục. Nguồn: lane `ap-the-cu-2310` site agency mẫu 23/10 (`Deliverables/GTV-Brand/GTV-Website/content-review-2026-10/ap-the-cu-2310/kiem-doc-lap.md` mục 1 và dòng `v2-qp-titles`).
- v1.4 (2026-10-21): rút từ đợt site agency mẫu 20–21/10. `apply.php`: xoá object cache trước khi purge trang; Elementor sinh lại CSS của từng tài liệu vừa ghi thay cho `files_manager->clear_cache()` (lệnh cũ xoá CSS Elementor toàn site). Bước 6 thêm `wp-pagespeed/scripts/cache_variants.py` (robots, canonical ở 5 biến thể cache). `ghi-an-toan.md`: thứ tự 7 bước có làm nóng, WP-CLI đúng bản PHP có `redis.so`, chạy theo lô tránh OOM, luật SQL thô khi bật object cache, bẫy CRLF và Python `open()`, LiteSpeed minify xoá `\r\n`, staging clone cũ, không verify bằng `utm_*`, mục 4b nhiều phiên cùng ghi, rollback so md5. Gate thêm 2 mục.
- v1.3 (2026-10-19): thêm chế độ sửa trực tiếp: `scripts/sua_truc_tiep.py` (dựng file HTML có nút E từ HTML bất kỳ, xuất `edits` chuẩn NFC, đánh `k#n` cho chữ lặp), `assets/edit-layer.*`. Kiểm đầu cuối trên trang thật trong Chrome headless: 176 khối, 0 khối báo sửa nhầm, 1 bản sửa xuất đúng. Anti-patterns: bẫy của mạng nội dung (`key#n`, NFC, thẻ đã duyệt, 2 phiên cùng ghi), giao diện đi qua `wp-staging-deploy`.
- v1.2 (2026-10-19): `apply.php` thêm `PURGE=0` để purge theo URL thay cho purge toàn site. Anti-patterns: bẫy `purge-post_all=1`, đường dẫn tuyệt đối khi nạp ArtifactData. Bước 4: duyệt trên trang cộng lời "xử lý" là đủ quyền ghi. Rút từ đợt ghi site agency mẫu 19/10.
- v1.1 (2026-10-17): chuyển bản gốc vào SEO Production, viết lại cho mọi site WordPress có quyền server. Thêm `templates/trang-duyet.html`, hồ sơ server, rubric `seo-text-qa`. `apply.php`: chặn đổi slug khi site không có bảng redirect Rank Math, purge theo plugin cache đang có.
- v1.0 (2026-10-17): tạo mới từ 2 lượt ghi thật 17/10. Chạy thử trên 221 review thật: `plan.py` khớp 189/196 thao tác của plan gốc, thêm luật giữ lại giá trị duyệt để trống; `apply.php` DRY=1 bắt đúng 1 mục site đã đổi sau lúc soạn; `verify.py` kiểm 139 URL, 3 lệch là lỗi thật.
