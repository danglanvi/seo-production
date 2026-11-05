---
name: wp-code-footprint
description: "Audit và dọn footprint AI trong site WordPress: comment quy trình lọt ra HTML, mu-plugin phân mảnh, inline JS/CSS lặp, code chết, semantic HTML thừa. Quét tất định + Jev, dọn theo lane có cổng md5 và rollback. Dùng sau đợt AI sửa site, trước khi bàn giao."
metadata:
  version: "1.1.0"
---

# wp-code-footprint — audit và dọn dấu vết AI trong code site WordPress

Nhiều phiên AI sửa một site để lại: comment giải thích trong chuỗi JS/CSS mà PHP echo ra trang (lộ tên người duyệt, ngày, tên lane), mỗi lane một mu-plugin (1 → 70 file trong 2 tuần), inline CSS/JS lặp trên mọi trang, code vá bằng regex thay vì sửa template, file chết. Skill này đo bằng số, gắn nhãn bằng Jev, rồi dọn theo lane có cổng md5, backup và rollback. Nguồn: site agency mẫu, audit và đợt dọn đêm 05/11/2026 (4 lane, 0 lỗi production).

## Khi nào dùng

- Sau một đợt nhiều phiên AI sửa theme, mu-plugin, CSS của site sống. Trước khi bàn giao site cho khách hoặc dev khác.
- Người duyệt xem view-source thấy comment nội bộ, hoặc hỏi "semantic HTML đã đúng chưa, thừa chỗ nào".
- Định kỳ mỗi tháng cho site có nhiều lane AI chạy.
- Không dùng khi: chỉ sửa chữ (dùng `wp-content-review-apply`), đo tốc độ (`wp-pagespeed`), kiểm sau một lần ghi nhỏ (`web-qa-gate` hạng mục 16 đã gọi script của skill này).

## Đọc trước

`references/do-dung-footprint.md` là cổng đếm, phân loại và chọn mức kiểm sau ghi. Dọn code chỉ dùng agent phụ khi người dùng yêu cầu rõ; các lane bên dưới là cách chia phạm vi, không tự cấp quyền spawn hoặc chỉ định model trái runtime hiện hành.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| SSH alias, docroot, theme, PHP bin, user web, access log, staging glob | `00-client-context/wp-server.md`, `site.json` của đợt (khoá `ssh`, `docroot`, `php_bin`, `wp_user`, `stg_docroot_glob`, thêm `theme`, `access_log`, `host`) | Hỏi người vận hành. Không có staging: chỉ audit, không dọn |
| Danh sách URL mẫu: 1 URL mỗi template + 3 bản mobile | Người vận hành hoặc sitemap | Lấy trang chủ, 1 trang dịch vụ, 1 bài, 1 category, 1 trang liên hệ |
| Bản theme trước khi AI sửa (tar backup) | Backup của site | Bỏ bước tách comment gốc của dev; ghi giới hạn |
| Người duyệt cho phép dọn | Lời duyệt có giờ | Chỉ audit |
| Token riêng của site: tên người duyệt, mã lane, mã bản (ví dụ `v8-ky-thuat`) | Biến môi trường `FOOTPRINT_EXTRA="Tên|lane-x|v8-ky-thuat"` khi chạy `footprint_count.py` và `scan_srv.py` | Script chỉ bắt từ quy trình chung (lane, phiên, đợt, lô, ngày, duyệt, axe); ghi giới hạn |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code | Quét HTML và code (`scan_html.py`, `scan_srv.py`, `footprint_count.py`), so token trước/sau, cổng md5 khi deploy | Dùng. Số đo tất định là bằng chứng chính |
| Jev | `code-comment-leak` (loại comment + mức lộ nội bộ), `inline-script-kind` (loại khối inline, nên ra file?), `semantic-wrap` (section/article/aside đúng nghĩa?) | Dùng, ngân sách 0,1 USD mỗi rubric. Ngưỡng: `process_note` ≥ 0,8 đọc tay (8/8 đúng ở lượt 05/11/2026); `p_yes` ≥ 0,7 cho "nên ra file"; `fit` confidence ≥ 0,6. Hiệu chuẩn lại bằng `model-calibration` khi đổi site lớn |
| EmbeddingGemma 2 | `nn` SentenceSimilarity giữa mu-plugin (header + hook + hàm), giữa khối inline và file JS theme | Chỉ khi được yêu cầu hoặc phạm vi semantic audit cần so nghĩa hàng loạt. ≥ 0,92 là ứng viên đọc tay, không phải bằng chứng nên gộp; so code, hook, dependency và rollback. Không đưa model local thành dependency của kit team |
| GLM Flash | Không dùng | Skill không trích câu |
| Model chính / agent được chỉ định | Viết rubric, đọc cờ, quyết định gộp, sửa code và kiểm bằng chứng | Theo routing hiện hành và model người dùng chọn. Chỉ dùng agent phụ khi được yêu cầu rõ; không spawn chỉ để kiểm lại việc của mình |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,ssh,wp-cli,curl,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Bộ quét JS cần Acorn: cài một lần bằng `npm install --prefix ~/.cache/wp-code-footprint acorn@8.19.0`, hoặc đặt `ACORN_PATH`; chạy fixture theo `references/do-dung-footprint.md`. Thiếu parser thì báo quét chưa hoàn tất, không báo sạch.

### A. Audit (chỉ đọc, khoảng 40 phút)

1. Tải HTML sống: 1 URL mỗi template desktop + 3 mobile, 1 request/giây, vào `<đợt>/html/d_*.html`, `m_*.html`. Tải thêm 2–3 trang với `Accept: image/webp` (`w_*.html`) vì cache tách biến thể theo Accept; bản không WebP thường là bản bot.
2. Chép code: `rsync` mu-plugins và theme (.php/.js/.css) về `<đợt>/srv/`, giữ mtime.
3. Quét: `python3 -I scripts/scan_html.py <đợt>/html <đợt>/work/out` và `python3 -I scripts/scan_srv.py <đợt>/srv <đợt>/work/out`. Đọc 2 file `.md` sinh ra: bảng mỗi trang (inline JS/CSS, comment VI trong code, landmark, section không heading, id trùng) và bảng mỗi mu-plugin (hook, `ob_start`, `preg_replace`, `!important`, từ quy trình).
3b. Quét DB theo nhóm có giới hạn: `custom_css`, bài publish, option autoload và revision; tách dữ liệu đang phục vụ với lịch sử/backup. Tìm marker HTML không phải `wp:` (ví dụ `<!--m:IMG-01-->`, `data-todo`). Đọc `robots.txt`, `llms.txt`, header. Không dump DB riêng tư vào deliverable hoặc gửi model phụ. Additional CSS: tìm selector trong CSS gộp/gọn, chạy đúng minifier trước/sau rồi so hash và 4 biến thể. Chỉ tái tạo map khi đầu ra/coverage đổi; comment bị minifier bỏ có thể không đổi byte công khai.
4. Jev: `python3 -I scripts/prep_jev.py <đợt>` khử trùng rồi chạy `jev.py` với 3 rubric trong `tasks/` (`--dry-run` trước, `--label <đợt>`). Đọc mọi `process_note` và mọi mục `fit` khác `correct`.
5. Gemma (nếu có): `emb.py nn --query work/out/emb_plugins.jsonl --docs work/out/emb_plugins.jsonl --k 5 --qprompt SentenceSimilarity --dprompt SentenceSimilarity`; liệt kê cặp ≥ 0,92. `emb.py nn` giữa `emb/q_inline_scripts.jsonl` và `emb/d_theme_js.jsonl`: cặp ≈ 1,00 là file theme bị nhúng nguyên văn.
6. Tách comment gốc của dev: nếu có tar theme cũ, diff theme hiện tại với tar; chỉ tính comment AI thêm. Không có tar thì ghi giới hạn.
7. Viết báo cáo theo `references/mau-bao-cao.md`: kết luận, nguyên nhân gốc, số liệu, phát hiện theo mức, semantic HTML đúng/thừa/sai, phần Jev và Gemma, phương án 6 bước, việc chờ người duyệt, giới hạn. Kèm prompt cho reviewer ngoài (mẫu ở cùng file).

### B. Dọn (trong phạm vi đã duyệt; chia tài nguyên theo lane)

8. Chia lane theo `references/lane-don.md`: `cmt-out` (gỡ comment khỏi output, Opus), `docblock-dead` (docblock + quarantine file chết, Sonnet), `theme-fix` (lỗi HTML mức thấp + comment theme, Sonnet), `merge-php` (gộp mu-plugin PHP thuần theo chức năng, Opus). Mỗi tài nguyên có đúng một lane chủ. Lane dùng `references/COMMON.md` làm luật cứng.
9. Hạ tầng deploy: chép `scripts/server-bin/*.sh` lên server (`/root/<site>-code-footprint/bin/`), đặt biến `DOCROOT`, `PHP_BIN`, `STG_GLOB`, `STG_HOST`, `HOST`, `THEME`, `WP_USER`, `ACCESS_LOG`, `ERROR_LOG`, `SITE_DOMAIN` từ cấu hình site. Dùng thư mục helper riêng từng site; không ghi đè helper site khác. Thử `prod_get.sh`, `stg_get.sh`, `md5.sh`, `health.sh` trước khi mở lane. `prod_deploy.sh` chỉ ghi khi md5 production khớp bản trong `srv/` (ai đó đổi file thì dừng mã 3), tự backup, chuyển file trong `MOVES.tsv` sang quarantine thay cho xoá, in lệnh ROLLBACK.
10. Mỗi lane: sửa trên bản chép `build/` → `php -l` → staging → kiểm → `make_expect.py` → khoá ghi chung → `prod_deploy.sh` → CHECKPOINT → kiểm bằng bản bỏ cache (`?nc=`) + `health.sh`. Lane so token code trước/sau (PHP `token_get_all`, JS acorn) để chứng minh chỉ comment đổi.
11. Phiên chính sau khi các phạm vi xong: vá chỗ sót, purge đúng phần output thay đổi. Nếu đổi output toàn site, dùng lô ≤12 path từ `site_paths.sh`, làm nóng và purge CDN theo `wp-staging-deploy`. Trường hợp comment-only output giống byte áp cổng tương đương, không purge toàn site vô ích.
12. Kiểm lại: tải lại cùng bộ URL vào `html-after/`, `python3 -I scripts/compare.py <đợt>/html <đợt>/html-after` ra bảng trước/sau; chạy lại Jev `code-comment-leak` trên HTML và mu-plugin sau; `health.sh` PASS với cửa sổ đủ log; robots và canonical bản cache không đổi.
13. Viết handoff cho reviewer ngoài: trước/sau theo số, danh sách file đổi, rollback, việc chưa làm, cách tự kiểm.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình người duyệt.

Bản tốt nhất phải có:
- [ ] Số "section không heading" đếm cả chữ trong `<span>`/`<strong>` của heading. Nguồn lỗi: scanner bản đầu báo 15/15 section thiếu heading ở trang HCM, số thật 2/15 (05/11/2026).
- [ ] Kết luận "file chết" có bằng chứng trên HTML sống của trang thí điểm, không chỉ grep selector. Nguồn lỗi: một file CSS riêng của bài bị gọi chết, nhưng 2/4 bài thí điểm vẫn in style (05/11/2026).
- [ ] Nhánh code "chết" chỉ cắt khi không còn đường rollback dùng nó (option tắt tính năng, trang EN, tham số `?x=0`). Nguồn lỗi: nhánh blog cũ là đường lùi của blog v2 (05/11/2026).
- [ ] Bản HTML audit ghi rõ biến thể cache (có/không WebP, mobile). Nguồn lỗi: bản bot nhúng 450–683 KB CSS, bản người dùng 92 KB; đọc nhầm sẽ báo sai tốc độ (05/11/2026).
- [ ] Kiểm bằng `?nc=` không so robots/canonical: site có thể noindex mọi URL có query. So bằng bản cache sau purge. Nguồn lỗi: 3 lane cùng báo "noindex" giả (05/11/2026).
- [ ] Gộp mu-plugin: liệt kê hook cùng tên với file ngoài tập gộp, vì thứ tự nạp theo tên file đổi; đặt priority tường minh khi thứ tự tương đối đổi. Nguồn: lane merge-php 05/11/2026.
- [ ] Mỗi lane chứng minh "chỉ comment đổi" bằng so token, không bằng diff mắt. Nguồn: 4 lane 05/11/2026, 45/45 và 9/10 file khớp token.

## Output

- `<đợt>/<site>_footprint-audit_v1.md` (+ bản HTML khi người duyệt cần), `agents/*.md` nếu dùng agent đọc.
- `<đợt>/fix-<ngày>/<lane>/`: BRIEF.md, CHECKPOINT.md, bao-cao.md, rollback.md, ket-qua.json, build/.
- `<đợt>/<site>_footprint-fix_handoff_v1.md`: trước/sau, file đổi, rollback, việc chưa làm.
- Rubric Jev: `tasks/` của skill, bản sao ở `tools/ai-assist/tasks/`.

## Gate / tự kiểm trước khi trả

- [ ] Bảng trước/sau từ `compare.py` trên cùng bộ URL và biến thể; `scan_complete=1`, `comment_quytrinh=0`, `htmlcomment_quytrinh=0`. Đọc tay cờ ngoài regex; ghi rõ coverage và dữ liệu chưa kiểm.
- [ ] `health.sh` PASS: 0 5xx, 0 PHP Fatal đúng domain từ giờ ghi đầu tiên, có request và không lỗi parser/thiếu log; robots và canonical bản cache không đổi ở URL mẫu.
- [ ] Mỗi lane có backup trên server, lệnh ROLLBACK đã in và đã ghi `rollback.md`; file bỏ đi nằm trong quarantine, không xoá.
- [ ] Purge/làm nóng đủ phạm vi output đổi, CDN không còn URL thất bại; kiểm mẫu cache tương ứng. Nếu không purge vì output giống byte, lưu bằng chứng minifier/hash/biến thể.
- [ ] Không file nào trong thư mục đợt chứa host staging, mật khẩu, key.
- [ ] Việc chưa làm (CSS inline ra file, link giả, jQuery CDN, nhúng CSS cho bot) ghi rõ kèm lý do và mức rủi ro.

## Luật cho mọi lane viết code web (chép vào `COMMON` của đợt)

1. Không comment trong chuỗi JS/CSS được echo hoặc trong file JS/CSS bị nhúng nguyên văn. Giải thích đặt ở comment PHP một dòng hoặc README của plugin.
2. Docblock mu-plugin ≤ 3 dòng: tên, chức năng, công tắc tắt. Không ngày, lane, phiên, tên người, lời duyệt, mã thẻ, md5, đường dẫn gói.
3. Không tạo mu-plugin mới theo lane. Sửa file đích theo chức năng (perf, seo, security, cache-purge, a11y-ui, semantic) qua khoá.
4. CSS/JS ra file enqueue có version. Inline chỉ critical CSS và config nhỏ. Không gắn `data-no-optimize` cho khối có comment.
5. Sửa gốc trong template trước khi vá bằng buffer, MutationObserver hay hàm giả. Vá tạm phải ghi ngày gỡ.
6. Cổng kiểm sau ghi chạy `footprint_count.py` trên HTML sống: quét hoàn tất, comment quy trình trong code và HTML bằng 0; lỗi parser không được bỏ qua.

## Anti-patterns

- Coi bản `?nc=` là bản chuẩn để so robots. So bản cache sau purge.
- Xoá file "chết" thay vì quarantine. Dùng `MOVES.tsv`.
- Lane tự viết lệnh ssh ghi riêng. Dùng `server-bin` có cổng md5.
- Gộp 5 nhóm việc vào một lane. Mỗi lane một tập file, một mục đích.
- Chạy Jev để viết lại comment. Jev chỉ gắn nhãn; Claude viết.
- Quy khối style hay script mới xuất hiện sau purge cho đợt dọn. So id khối trước/sau; khối mang id của plugin cache (`litespeed-ccss`) là tính năng đang chờ của plugin lộ ra khi purge. Chứng minh bằng md5 khớp file trên server và giờ sinh file trước lần ghi đầu tiên (`references/lane-don.md` mục 3).
- Tin `process_note` của Jev ở comment có ngày hoặc ID bài. Jev coi số là dấu vết quy trình; Claude đọc lại mọi mục trước khi xoá.
- Theme in nguyên văn file CSS vào `<style>` (bộ lọc `style_loader_tag` + `file_get_contents`) rồi chỉ sửa chữ comment ở file nguồn. Lần sửa CSS sau lại lọt. Thêm hàm bỏ comment lúc nhúng (xử lý chuỗi và `url()`, regex lỗi thì in bản gốc), rồi mới viết lại comment nguồn. Ca site đào tạo mẫu 05/11/2026: 1 hàm, 3 chỗ gọi, 219 → 0 comment quy trình trên 27 trang.
- Để bản chép `srv/` chứa slug đăng nhập ẩn trong workspace. Loại mu-plugin đổi URL đăng nhập khỏi `rsync` (`--exclude`), hoặc chuyển ra thư mục backup 0600 ngoài workspace ngay sau khi chép.
- Báo số `!important` hay byte CSS của trang mà không ghi biến thể cache. Cùng trang chủ site agency mẫu: 995 (desktop không WebP), 698 (mobile), 505 (WebP). `footprint_count.py` đếm byte UTF-8 từ 1.0.2; bản cũ đếm ký tự.
- Gọi comment còn lại là "comment dev gốc" rồi giữ. Comment tiếng Anh kiểu "Add this line", "Change from…" trong `<style>` của template vẫn lọt ra view-source: bỏ khỏi output như comment quy trình.
- Purge CDN một lượt rồi báo xong. Bunny trả 429 cho khoảng 1/3 URL mỗi lượt; chạy lại danh sách 429 tới khi 0.

## Changelog

- v1.1.0 (2026-11-05): parser Acorn thay regex JS ở cả hai bộ quét; tách script dữ liệu/external, byte UTF-8 và hash khử trùng; lỗi parser hoặc tập URL lệch trả INCOMPLETE. Sửa kết luận Additional CSS/hash và embedding, thêm giới hạn DB/history/backup. Fixture hồi quy và bộ HTML thật được kiểm trong đợt review độc lập. Kế thừa sửa lọc domain của reviewer, bổ sung health theo ngày/giờ/timezone, fail closed khi thiếu log/request hoặc lỗi parse; 6 ca hồi quy và phép đọc log live đạt. Helper tách theo site. Review chéo cùng ngày: thêm lệnh cài Acorn vào thư mục cache cố định để `js_comments.mjs` tự tìm (máy mới trước đó luôn ra INCOMPLETE); 17/17 test đạt khi không đặt `ACORN_PATH`.
- v1.0.2 (2026-11-05): rút từ review độc lập của ChatGPT cho site agency mẫu. Bước A3b quét DB (`custom_css`, marker trong bài, option, revision), `robots.txt`, `llms.txt`, header, và kiểm Additional CSS có vào file CSS gộp không. `footprint_count.py` đếm byte UTF-8 và `!important`. `prod_deploy.sh` in lệnh rollback an toàn: kiểm archive, chụp bản đang chạy, giải nén rồi mới xoá file mới, chown đúng file (thử trên sandbox server). 2 anti-pattern mới.
- v1.0.1 (2026-11-05): chạy lần 2 trên site đào tạo mẫu (theme tự viết, 7 mu-plugin, 2 lane). `server-bin/health.sh` đọc giờ và mã HTTP theo mẫu chứ không theo số cột (log site mẫu lệch 1 cột so với site agency, bản cũ báo 0 sai). `server-bin/stg_get.sh` gọi https qua `--resolve 127.0.0.1` và nhận `STG_AUTH` cho staging có Basic Auth (bản cũ gọi http, staging trả 301). Anti-pattern thêm 2 mục: chỉ sửa comment nguồn khi theme nhúng CSS nguyên văn; bản chép `srv/` có slug đăng nhập.
- v1.0 (2026-11-05): tạo mới từ audit và đợt dọn site agency mẫu đêm 05/11/2026: 70 → 57 mu-plugin, comment quy trình trong HTML 24/24 trang → 0, 4 lane, 0 lỗi production. Script quét, 3 rubric Jev (`code-comment-leak`, `inline-script-kind`, `semantic-wrap`, 995 lượt gọi, 0,038 USD), bộ deploy có cổng md5, `compare.py`.
