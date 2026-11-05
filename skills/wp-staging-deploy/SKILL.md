---
name: wp-staging-deploy
description: "Làm mới staging WordPress từ production, vào staging qua tunnel SSH, rồi deploy theme và mu-plugins lên production bằng gộp 3 phía có backup và rollback. Sinh lại CSS Elementor từng tài liệu, purge LiteSpeed theo URL. Các skill wp-* gọi skill này trước khi ghi production."
metadata:
  version: "1.5.0"
---

# wp-staging-deploy — staging, gộp 3 phía, deploy có rollback

Skill này là đường ghi chung cho site WordPress có quyền SSH và WP-CLI. Mọi thay đổi theme, mu-plugin hay CSS đi qua staging trước. Sau đó skill gộp thay đổi lên production bằng 3 phía và giữ bản backup để rollback.

Trước khi ghi, đọc `references/bang-chung-sau-ghi.md`: backup + hash, staging lệch nguồn, xác minh DB/object cache/HTML và mức kiểm phù hợp thay đổi. Mã thoát 0 chưa đủ; comment-only có đầu ra minify giống byte không cần thêm preview plugin hay đổi cache config.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-staging-deploy/scripts/`:

| Script | Việc |
|---|---|
| `stg_refresh.sh` | Làm mới DB staging từ production, search-replace URL, chụp `base` cho bước gộp, mount `uploads/elementor` ghi được |
| `merge3.py` | Gộp 3 phía (base, staging, production). Mặc định chỉ in plan. `--apply` nén bản production trước khi chép |
| `regen_elementor_css.php` | Sinh lại CSS Elementor theo từng tài liệu |
| `purge_urls.php` | Purge LiteSpeed theo danh sách URL, không purge toàn site |
| `site_paths.sh` | Dựng danh sách path toàn site (sitemap + trang phân trang + path thêm) để purge và làm nóng sau khi đổi phần dùng chung |
| `zz-staging-safety.php` | mu-plugin cho staging: chặn email, noindex, tắt cache |
| `stg_env.sh` | `source` được trên Mac (bash, zsh). `stg_load` nạp host staging, `stg_mask` che đúng chuỗi host, `SSH` giữ mã thoát qua pipe |
| `stg_tunnel.sh` | `up`, `down`, `status` tunnel theo `--lane` và `--port`. Tự nối lại tunnel treo hoặc rớt |
| `stg_get.sh` | GET một đường dẫn staging qua tunnel. Host và mật khẩu không vào tham số lệnh. Output đã che host |
| `stg_leak_check.sh` | Quét thư mục đợt tìm host staging, mật khẩu và mẫu secret. Không in giá trị tìm |
| `theme_preview_fill.py` | Điền mẫu `templates/theme-preview.php.tpl` thành mu-plugin xem trước theme cho site không có staging. Sinh mã vào file 0600, không in mã |
| `wpx.sh` | Chạy một file PHP bằng `wp eval-file` trên production hoặc staging. Đọc alias, docroot, binary PHP, user web, mẫu thư mục staging từ `site.json`. Giữ khe WP-CLI bằng `flock`, đặt biến sau `sudo`, che host và thư mục staging. `--dry` chỉ in lệnh |

Test offline: `python3 -B skills/wp-staging-deploy/tests/test_stg_helpers.py`, `test_merge3.py`, `test_wpx.py` và `test_theme_preview.py` trong cùng thư mục.

Tạo staging lần đầu: `references/tao-staging.md`. Site không có staging: `references/khong-co-staging.md`. Hồ sơ server của site: `00-client-context/wp-server.md`.

## Khi nào dùng

- Trước khi ghi theme, mu-plugin hay CSS lên production.
- Khi staging đã cũ và cần dữ liệu mới của production.
- Khi deploy một gói sửa đã kiểm trên staging.
- Khi cần rollback một lần deploy.
- Site không có staging, hoặc staging không có LiteSpeed nên không kiểm được CSS và JS gộp: dùng nhánh theme xem trước trên production (`references/khong-co-staging.md`) thay cho Bước 1–3.
- Không dùng để sửa chữ, meta hay link trong bài. Dùng `wp-content-review-apply`.
- Không dùng để kiểm sau khi ghi. Dùng `web-qa-gate`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| SSH alias, thư mục site, DB, theme | `00-client-context/wp-server.md` | hỏi người vận hành |
| URL staging | `/root/.stg_home` trên server | tạo staging theo `references/tao-staging.md`. Không tạo được (shared hosting, hết dung lượng, người duyệt không cho): nhánh `references/khong-co-staging.md` |
| File Basic Auth của staging | file quyền 600 trên máy người vận hành | hỏi người vận hành. Không `source` file `.env` để lấy mật khẩu |
| Cổng tunnel, khi nhiều phiên chạy song song | người điều phối các phiên | dùng `--lane` và `--port` riêng, không dùng chung cổng mặc định |
| Gói sửa (file theme, mu-plugin) | thư mục làm việc của đợt | dừng |
| Người duyệt ghi production | người vận hành | không ghi production |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code (script trong `scripts/`) | refresh, gộp 3 phía, backup, regen CSS, purge, tunnel, GET staging, chạy `eval-file`, che host, quét lộ | dùng: lượt thử 19/10 cho plan và số tài liệu trùng script cũ trên server thật. Helper staging có test offline |
| Claude | đọc plan gộp, xử lý xung đột, quyết định thứ tự chạy, đọc kết quả `web-qa-gate` | dùng |
| Jev | không dùng ở skill này | kiểm giao diện sau deploy nằm ở `web-qa-gate` (Jev `ui-visual`) |
| EmbeddingGemma | không dùng | skill không đo độ giống |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'ssh,wp-cli,python3,curl'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu thiếu `ssh` hoặc `wp-cli`, dừng skill. Báo người vận hành cần quyền server.

### Bước 1 — làm mới staging (khi cần)

1. Đọc `wp-server.md`. Ghi các biến `PROD`, `STG`, `DB_PROD`, `DB_STG`, `PROD_URL`, `THEME`.
2. Chạy:

   ```bash
   ssh <alias> 'PROD=... STG=... DB_PROD=... DB_STG=... PROD_URL=... THEME=... bash -s' < skills/wp-staging-deploy/scripts/stg_refresh.sh
   ```

3. Ghi đường dẫn `base` mà script in ra. Bước gộp cần thư mục này.
4. Nếu script báo `siteurl staging: LỆCH` hoặc `có mount dưới production`, dừng và xử lý trước.

### Bước 2 — vào staging qua tunnel

Dùng các helper dưới cho mọi lệnh staging. Không tự viết lại lệnh tunnel hay curl.

1. Nạp helper và host staging từ root repo (bash hoặc zsh):

   ```bash
   export STG_ALIAS=<alias>
   source skills/wp-staging-deploy/scripts/stg_env.sh && stg_load
   ```

   `stg_load` đọc `/root/.stg_home` qua ssh một lần, bỏ scheme và đường dẫn, rồi export `STG_HOST`. Hàm không in host. Dùng `export`, không viết `STG_ALIAS=<alias> source …`: dạng gán trước lệnh `source` không giữ biến cho `stg_load` và các script con.
2. Mở tunnel: `bash skills/wp-staging-deploy/scripts/stg_tunnel.sh up --port 18094`. Khi nhiều phiên chạy song song, mỗi phiên thêm `--lane <tên>` và cổng riêng.
3. Gọi staging:

   ```bash
   bash skills/wp-staging-deploy/scripts/stg_get.sh --port 18094 --auth-file <file Basic Auth> --out <thư mục đợt>/trang.html /duong-dan/
   ```

   Script gửi Host qua `--connect-to` cổng 80 và dùng UA trình duyệt. Script che host trong body, header và lỗi. File Basic Auth nhận dạng `user:pass`, `user=`/`password=` hoặc `STG_BASIC_USER=`/`STG_BASIC_PASS=`.
4. Nếu `stg_get.sh` trả mã 3, chạy lại `stg_tunnel.sh up` với cùng `--lane` và `--port`. Lệnh này kiểm tunnel, rồi nối lại tunnel treo hoặc rớt.
5. Pipe mọi lệnh staging tự viết qua `stg_mask`, cả stdout và stderr: `SSH <alias> '<lệnh>' 2>&1 | stg_mask`. Chạy `set -o pipefail` trước để giữ mã thoát của `SSH`. Lệnh cần stdin (`bash -s < file`) dùng `ssh` thường, vẫn thêm `2>&1 | stg_mask`.
6. Lấy binary PHP và user chạy WP-CLI trên staging từ `wp-server.md`. Không cứng đường dẫn `lsphp` hay user `www`.
7. Chạy file PHP trên server bằng `wpx.sh`. Không chép script này vào thư mục đợt rồi sửa tay alias hay docroot.
   - Dùng lại `site.json` của `wp-ucss` nếu đợt đã có. Chưa có thì tạo file với các khoá `ssh`, `docroot`, `php_bin`, `wp_bin`, `wp_user`, lấy giá trị từ `wp-server.md`.
   - Thêm khoá `stg_docroot_glob` khi chạy staging. Mẫu glob phải khớp đúng 1 thư mục trên server. Khớp 0 hoặc nhiều thư mục thì script dừng.
   - Đặt `site.json` trong thư mục đợt. Không đặt trong repo master.

   ```bash
   bash skills/wp-staging-deploy/scripts/wpx.sh --site <site.json> --dry stg job.php DRY=1
   bash skills/wp-staging-deploy/scripts/wpx.sh --site <site.json> --slot 2 --tag <lane> stg job.php DRY=1
   ```

   Khi 2 phiên cùng chạy WP-CLI trên một server, mỗi phiên dùng một `--slot` và một `--tag` riêng. Server cho tối đa 2 khe.
8. Xong việc trên staging: chạy `stg_tunnel.sh down` với cùng `--lane` và `--port`.

### Bước 3 — chép gói sửa lên staging và kiểm

1. Chép file vào staging. Lint PHP bằng `php -l` trên server trước khi chép.
   - Nếu gói có mu-plugin hay file PHP khai báo hàm toàn cục, chạy `wp eval 'var_dump(function_exists("<tên_hàm>"));'` trên staging cho từng hàm mới trước khi chép. Kết quả `true` là trùng tên: đổi tiền tố riêng của đợt. `php -l` không bắt lỗi trùng tên hàm.
2. Nếu gói sửa output widget Elementor, xoá `_elementor_element_cache` của tài liệu đó.
3. Sinh lại CSS Elementor: chạy `regen_elementor_css.php` với `DRY=1`, đọc số tài liệu, rồi chạy `DRY=0`.
4. Chạy `web-qa-gate` trên staging. Chỉ đi tiếp khi report PASS.

### Bước 4 — deploy lên production

Thời điểm deploy: người duyệt duyệt gói sửa kèm ngưỡng đạt ghi trước. Khi staging đạt ngưỡng đó, deploy production ngay trong ngày. Không chờ giờ thấp điểm ban đêm. Hoãn chỉ trong 2 trường hợp:
- Phiên khác còn giữ khoá `*-no-restart.lock` (`web-lane-orchestration`, `references/theo-doi-va-cuu.md`).
- Gói sửa cần restart dịch vụ trong giờ cao điểm.

1. Chạy `merge3.py` ở chế độ dry:

   ```bash
   ssh <alias> 'python3 -I - --base <base> --stg <STG>/wp-content --prod <PROD>/wp-content --roots themes/<THEME>,mu-plugins --skip mu-plugins/zz-staging-safety.php' < skills/wp-staging-deploy/scripts/merge3.py
   ```

2. Đọc plan. Mỗi dòng là `stg` (lấy bản staging) hoặc `merged` (gộp bằng diff3). Nếu script in `DỪNG`, xử lý từng file trong danh sách rồi chạy lại.
3. Trình plan cho người duyệt. Chỉ chạy `--apply` khi người duyệt đồng ý ghi production.
4. Chạy lại lệnh với `--apply --backup-dir /root/deploy-<ngày>`. Ghi lại lệnh rollback mà script in ra.
5. Sinh lại CSS Elementor trên production cho các tài liệu bị ảnh hưởng (`IDS=...`).
6. Purge theo URL: `purge_urls.php` với `URLS=...`, chạy `DRY=1` rồi `DRY=0`. Gọi 1 request không cache để LiteSpeed gửi hàng đợi. Nếu gói sửa đổi phần hiện trên mọi trang, làm mục "Đổi phần dùng chung toàn site" bên dưới thay cho bước này.
7. Chạy `web-qa-gate` trên production.

### Đổi phần dùng chung toàn site

Áp dụng khi gói sửa đổi phần hiện trên mọi trang: nút liên hệ nổi, header, footer, menu, CSS hay JS inline do mu-plugin in ra. Mỗi trang có bản HTML cache riêng. Nếu chỉ purge vài trang chính, khách vào bài viết vẫn thấy bản cũ cho tới khi cache hết hạn. Nguồn: site agency mẫu 28/10/2026. Đợt đầu chỉ purge 33 trang chính, nên 260 bài blog còn nút cũ và người vận hành báo lỗi.

1. Dựng danh sách path toàn site:

   ```bash
   bash skills/wp-staging-deploy/scripts/site_paths.sh --host https://<domain> --out work/paths.txt --archive /blog/ --extra work/ngoai-sitemap.txt
   ```

   Thêm `--archive` cho mỗi trang lưu trữ không nằm trong sitemap chuyên mục, ví dụ trang blog hay trang lưu trữ CPT. Ghi trang noindex có header, footer chung (trang cảm ơn, trang chính sách) vào file `--extra`.
2. Chia lô ≤12 path. Purge từng lô bằng `wpx.sh --site <site.json> prod scripts/purge_urls.php URLS=<lô> DRY=0`. Sau mỗi lô, gọi 1 request không cache và nghỉ 2 giây.
3. Làm nóng page cache bằng `wp-pagespeed/scripts/lam_nong.sh --host https://<domain> -f work/paths.txt -V guest-d,guest-m -s 1`. Bước này chạy khoảng 15 phút cho 370 path.
4. Nếu site có CDN lưu HTML ở edge (site.json có `cdn_host`), purge CDN cho cùng danh sách bằng `wp-ucss/scripts/bunny_purge.py <paths> --apply --warm`. Hook purge LiteSpeed chạy qua WP-CLI không đẩy URL sang CDN. Sau đợt purge LiteSpeed ngày 28/10/2026, edge Bunny còn 60/370 bản cũ. Cách purge và kiểm `cdn-cachedat`: `cdn-speed-setup/references/origin-sau-cdn.md` §3.
5. Kiểm ngẫu nhiên ≥12 path bằng URL thường, không thêm tham số: HTML phải chứa dấu của bản mới (id thẻ `<style>`, tên keyframe hoặc class mới). Kiểm cả UA desktop và UA mobile.

Cách này không phải "purge toàn site" mà Gate cấm. Mỗi lệnh vẫn purge theo URL, theo lô, và sau đó làm nóng lại cache.

### Bước 5 — rollback (khi QA production FAIL)

1. Chạy lệnh rollback đã ghi ở Bước 4: giải nén bản backup và xoá các file mới.
2. Sinh lại CSS Elementor và purge lại các URL.
3. Chạy `web-qa-gate` để xác nhận site về trạng thái cũ.

### Bước 6 — quét lộ trước khi báo xong

Chạy bước này trước khi báo xong đợt và trước khi mở file HTML evidence.

1. Quét thư mục làm việc của đợt bằng script trong repo:

   ```bash
   bash skills/wp-staging-deploy/scripts/stg_leak_check.sh <thư mục đợt> --auth-file <file Basic Auth>
   ```

   Script cần `STG_HOST` hoặc `STG_ALIAS`. Thêm `--env-file <bản sao file secret staging>` để tìm cả mật khẩu DB. Thêm `--needle-file <file>` cho chuỗi khác như slug đăng nhập.
2. Tuỳ chọn: nếu repo nằm trong workspace có kho secret chung và có `tools/leak_scan.sh` ở root workspace, chạy thêm `bash <root workspace>/tools/leak_scan.sh <thư mục đợt>`. Không có công cụ này thì bỏ qua mục 2.
3. Nếu lệnh trả mã 1, xoá hoặc che chỗ lộ bằng `stg_mask`, rồi chạy lại. Nếu file lộ đã gửi đi hoặc đã hiện trong chat, báo người vận hành để đổi secret.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] Plan gộp đã đọc từng dòng, không còn dòng `DỪNG`. File chỉ dùng cho staging nằm trong `--skip`.
- [ ] Site không có staging: lô chạy trên theme xem trước bằng mu-plugin mẫu 1.3, kiểm có mã và không mã, giữ `Version` của `style.css`, dọn `.off` và quarantine ngay sau deploy. Nguồn lỗi: site bán lẻ mẫu 29/10/2026, 3 bản mu-plugin đầu làm mất tối ưu LiteSpeed hoặc để trang xem trước vào cache.
- [ ] `web-qa-gate` PASS trên staging trước khi ghi production.
- [ ] Có thư mục backup và lệnh rollback trước khi `--apply`.
- [ ] Purge theo URL, không purge toàn site. Gói đổi phần dùng chung: đã purge đủ danh sách `site_paths.sh` theo lô, làm nóng, purge CDN nếu có, và kiểm ngẫu nhiên ≥12 path ở 2 UA.
- [ ] Người duyệt đã đồng ý ghi production cho lần này.
- [ ] Mỗi hàm toàn cục mới trong mu-plugin đã kiểm `function_exists` trên staging trước khi chép. Nguồn lỗi: 17/10, site agency mẫu, mu-plugin trùng tên hàm làm staging báo critical error, `php -l` không bắt.
- [ ] `stg_leak_check.sh` trả 0 trên thư mục đợt. Log, file và chat không chứa host staging, mật khẩu DB hay mật khẩu Basic Auth. Mọi lệnh `eval-file` chạy qua `wpx.sh`, không qua bản chép tay. Nguồn lỗi: 18/10, site agency mẫu, host staging lộ ≥8 lần vì lệnh không pipe qua bộ che hoặc regex chung `stg-…` để lọt; 23–27/10, 26 bản `wpx.sh` chép tay với 19 md5 khác nhau, đều che host bằng regex chung.

## Đọc kết quả cho đúng

- `merged` nghĩa là diff3 gộp được thay đổi của cả 2 phía. Kiểm 1–2 file `merged` bằng mắt trước khi apply.
- Xung đột diff3 chỉ được nhận bản staging khi staging đã chứa mọi dòng production thêm. Ngoài trường hợp đó, script dừng.
- `staging thiếu <file>`: production có file mà staging không có. Thường là plugin hay file production thêm sau lần refresh. Chép file đó về staging rồi chạy lại.
- Site đặt `purge-post_all=1` thì purge theo post sẽ purge toàn site. Script purge chỉ dùng `litespeed_purge_url`.
- Staging không có cache LiteSpeed. Phần sửa tốc độ cần kiểm thêm trên production.
- CSS theme, CSS trong `uploads` hay template có URL tuyệt đối về production (font icon, ảnh nền) làm staging mất icon, vì trình duyệt chặn font khác origin. Ảnh so sánh staging khi đó báo lỗi giả. Sửa chỉ trên staging bằng mu-plugin viết lại URL, và thêm file đó vào `--skip`.
- Opcache có thể giữ bản cũ của file PHP vừa chép khoảng 1 phút. Chờ 1 phút rồi mới kết luận bản sửa không chạy. `opcache_reset` qua WP-CLI chỉ xoá opcache của PHP CLI, không xoá opcache của web server.

## Output

- Plan gộp (dry) và log apply, lưu trong thư mục làm việc của đợt.
- Thư mục backup trên server: `prod-before-<giờ>.tgz` và `prod-new-files-<giờ>.txt`.
- Report `web-qa-gate` của staging và production.
- Dòng `KẾT QUẢ` của `stg_leak_check.sh` trên thư mục đợt, mã 0.

## Gate

- Không ghi production khi chưa có người duyệt cho lần ghi đó.
- Không `--apply` khi không có `--backup-dir`.
- Không xoá cache CSS Elementor toàn site. Sinh lại từng tài liệu.
- Không purge toàn site khi chỉ đổi vài URL.
- Không báo xong gói đổi phần dùng chung khi mới purge một phần danh sách path hoặc chưa purge CDN lưu HTML.
- Không in secret, host staging hay mật khẩu ra terminal, log hoặc file.
- Không chạy lệnh staging tự viết mà không pipe qua `stg_mask`.
- Không báo xong đợt khi `stg_leak_check.sh` chưa trả 0 trên thư mục đợt.
- Không ghi comment chứa tên người, lane, đợt, lô, ngày, số bản hay lời duyệt vào file PHP, JS, CSS đưa lên site. Docblock mu-plugin tối đa 3 dòng: tên, việc, công tắc tắt.
- Không ghi comment trong chuỗi JS/CSS mà PHP echo ra HTML, trong heredoc, hay trong file JS/CSS bị nhúng nguyên văn. Không đặt `data-no-optimize` để tránh minify. Comment ở đó lọt ra view-source.
- Không tạo mu-plugin mới cho mỗi lane hay mỗi đợt. Hook mới vào file chủ đề theo chức năng; file mới chỉ khi plan ghi tên file. Sau deploy chạy `wp-code-footprint/scripts/footprint_count.py` trên HTML production: `comment_quytrinh=0`.

## Anti-patterns

- Chép đè cả thư mục theme từ staging lên production. Cách này xoá thay đổi production làm sau lần refresh.
- Mount con dưới `uploads` của staging khi chưa `--make-private`.
- Gọi `litespeed_purge_post` trên site có `purge-post_all=1`.
- Báo deploy xong khi chưa chạy `web-qa-gate` trên production.
- Che host bằng regex chung kiểu `stg-[a-z0-9-]+`. Regex đó để lọt host thật (18/10). Dùng `stg_mask`, hàm này thay đúng chuỗi host.
- `source` file `.env` để lấy mật khẩu. Giá trị có ký tự shell sẽ chạy như lệnh và in một phần ra lỗi (17/10).
- Chép script chạy `eval-file` vào từng thư mục đợt rồi sửa tay alias, docroot, khe khoá. Các bản lệch nhau và giữ lỗi cũ. Dùng `wpx.sh` với `site.json`.
- Chờ tới đêm mới deploy gói đã đạt ngưỡng trên staging. Ngưỡng đạt và lệnh rollback đã có trước khi ghi, nên giờ ghi không đổi cách xử lý khi lỗi.

## Changelog

- v1.5.0 (2026-11-05): thêm hợp đồng bằng chứng sau ghi: hash/backup hai nơi, postcondition có cấu trúc, getter mới và object cache web, kiểm minifier thực tế trước regen CSS, health có cửa sổ thời gian; đọc cấu hình theo whitelist, không lộ secret.
- v1.4.1 (2026-11-05): Gate thêm 3 luật code sạch: không comment quy trình trong file lên site, không comment trong chuỗi echo hay `data-no-optimize`, không mu-plugin theo lane; kiểm bằng `footprint_count.py` sau deploy. Nguồn: audit footprint site agency mẫu 05/11/2026 (70 mu-plugin do 8 đợt lane tạo, comment quy trình lọt ra view-source), skill `wp-code-footprint`. Không đổi script.
- v1.4 (2026-10-30): nhánh site không có staging: reference `khong-co-staging.md`, mẫu `templates/theme-preview.php.tpl` (bản 1.3 đã chạy trên production site bán lẻ mẫu, đã ẩn tên theme), `scripts/theme_preview_fill.py` sinh mã 0600 và điền mẫu, `tests/test_theme_preview.py` 2/2 kèm `php -l`. Nguồn: site bán lẻ mẫu 29–30/10/2026, theme xem trước 16/16 URL đạt có mã và không mã, rồi deploy lô 40 file; người duyệt yêu cầu sửa theo template ở tầng theme (29/10/2026 21:45). Tự phản biện gộp 2 mục plan gộp thành 1, thêm 1 mục nhánh không staging.

- v1.3 (2026-10-28): thêm mục "Đổi phần dùng chung toàn site" và `scripts/site_paths.sh` (sitemap + dò `/page/N/` + `--extra`). Gate và tự phản biện thêm mục purge đủ danh sách và purge CDN. Nguồn: site agency mẫu 28/10/2026, đổi nút liên hệ nổi. Lượt đầu chỉ purge 33 trang chính, lượt sau purge 370 path theo 31 lô. Edge CDN còn 60/370 bản cũ tới khi purge riêng. Chạy thử `site_paths.sh` trên site thật: 346 path sitemap, 17 trang phân trang; 7 path ngoài sitemap cần `--extra` và `--archive`.
- v1.2 (2026-10-27): thêm `scripts/wpx.sh` (chạy `eval-file` trên production hoặc staging, đọc giá trị server từ `site.json`, khe `flock`, biến sau `sudo`, `ssh -n`, che đúng host và thư mục staging) và `tests/test_wpx.py` 6/6. Bước 2 mục 7 hướng dẫn dùng. Bước 4 thêm luật thời điểm deploy. Nguồn: 26 bản `wpx.sh` chép tay trong đợt tốc độ và semantic HTML site agency mẫu 23–27/10, bản gốc là bản chạy thật 27/10 (DRY production 72/72 op, ghi staging 72 op); quyết định của người vận hành 26/10 và 27/10, áp cho các lane đêm 26/10 và ngày 27/10.
- v1.1 (2026-10-25): sec-3 thêm `stg_env.sh`, `stg_tunnel.sh`, `stg_get.sh` (che đúng chuỗi host, tunnel tự nối lại, `SSH` giữ mã thoát); sec-2 thêm Bước 6 quét lộ bằng `stg_leak_check.sh`; sec-5 kiểm trùng tên hàm ở Bước 3; ui-6 thêm bẫy URL tuyệt đối và opcache. Test offline 36/36 và `test_merge3.py` 3/3.
- v1.0 (2026-10-19): bản đầu. Gom script deploy, refresh staging, regen CSS và purge của 2 site nội bộ thành script dùng chung, có tham số. `merge3.py` thêm backup và lệnh rollback trước khi chép. Lượt thử 19/10 trên server thật, chế độ dry: plan gộp trùng script cũ (15 file), regen đếm 88 tài liệu như script cũ.
