---
name: wp-staging-deploy
description: "Làm mới staging WordPress từ production, vào staging qua tunnel SSH, rồi deploy theme và mu-plugins lên production bằng gộp 3 phía có backup và rollback. Sinh lại CSS Elementor từng tài liệu, purge LiteSpeed theo URL. Các skill wp-* gọi skill này trước khi ghi production."
metadata:
  version: "1.1"
---

# wp-staging-deploy — staging, gộp 3 phía, deploy có rollback

Skill này là đường ghi chung cho site WordPress có quyền SSH và WP-CLI. Mọi thay đổi theme, mu-plugin hay CSS đi qua staging trước. Sau đó skill gộp thay đổi lên production bằng 3 phía và giữ bản backup để rollback.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-staging-deploy/scripts/`:

| Script | Việc |
|---|---|
| `stg_refresh.sh` | Làm mới DB staging từ production, search-replace URL, chụp `base` cho bước gộp, mount `uploads/elementor` ghi được |
| `merge3.py` | Gộp 3 phía (base, staging, production). Mặc định chỉ in plan. `--apply` nén bản production trước khi chép |
| `regen_elementor_css.php` | Sinh lại CSS Elementor theo từng tài liệu |
| `purge_urls.php` | Purge LiteSpeed theo danh sách URL, không purge toàn site |
| `zz-staging-safety.php` | mu-plugin cho staging: chặn email, noindex, tắt cache |
| `stg_env.sh` | `source` được trên Mac (bash, zsh). `stg_load` nạp host staging, `stg_mask` che đúng chuỗi host, `SSH` giữ mã thoát qua pipe |
| `stg_tunnel.sh` | `up`, `down`, `status` tunnel theo `--lane` và `--port`. Tự nối lại tunnel treo hoặc rớt |
| `stg_get.sh` | GET một đường dẫn staging qua tunnel. Host và mật khẩu không vào tham số lệnh. Output đã che host |
| `stg_leak_check.sh` | Quét thư mục đợt tìm host staging, mật khẩu và mẫu secret. Không in giá trị tìm |

Test offline: `python3 -B skills/wp-staging-deploy/tests/test_stg_helpers.py` và `python3 -B skills/wp-staging-deploy/tests/test_merge3.py`.

Tạo staging lần đầu: `references/tao-staging.md`. Hồ sơ server của site: `00-client-context/wp-server.md`.

## Khi nào dùng

- Trước khi ghi theme, mu-plugin hay CSS lên production.
- Khi staging đã cũ và cần dữ liệu mới của production.
- Khi deploy một gói sửa đã kiểm trên staging.
- Khi cần rollback một lần deploy.
- Không dùng để sửa chữ, meta hay link trong bài. Dùng `wp-content-review-apply`.
- Không dùng để kiểm sau khi ghi. Dùng `web-qa-gate`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| SSH alias, thư mục site, DB, theme | `00-client-context/wp-server.md` | hỏi người vận hành |
| URL staging | `/root/.stg_home` trên server | tạo staging theo `references/tao-staging.md` |
| File Basic Auth của staging | file quyền 600 trên máy người vận hành | hỏi người vận hành. Không `source` file `.env` để lấy mật khẩu |
| Cổng tunnel, khi nhiều phiên chạy song song | người điều phối các phiên | dùng `--lane` và `--port` riêng, không dùng chung cổng mặc định |
| Gói sửa (file theme, mu-plugin) | thư mục làm việc của đợt | dừng |
| Người duyệt ghi production | người vận hành | không ghi production |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Code (script trong `scripts/`) | refresh, gộp 3 phía, backup, regen CSS, purge, tunnel, GET staging, che host, quét lộ | dùng: lượt thử 19/10 cho plan và số tài liệu trùng script cũ trên server thật. Helper staging có test offline |
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
7. Xong việc trên staging: chạy `stg_tunnel.sh down` với cùng `--lane` và `--port`.

### Bước 3 — chép gói sửa lên staging và kiểm

1. Chép file vào staging. Lint PHP bằng `php -l` trên server trước khi chép.
   - Nếu gói có mu-plugin hay file PHP khai báo hàm toàn cục, chạy `wp eval 'var_dump(function_exists("<tên_hàm>"));'` trên staging cho từng hàm mới trước khi chép. Kết quả `true` là trùng tên: đổi tiền tố riêng của đợt. `php -l` không bắt lỗi trùng tên hàm.
2. Nếu gói sửa output widget Elementor, xoá `_elementor_element_cache` của tài liệu đó.
3. Sinh lại CSS Elementor: chạy `regen_elementor_css.php` với `DRY=1`, đọc số tài liệu, rồi chạy `DRY=0`.
4. Chạy `web-qa-gate` trên staging. Chỉ đi tiếp khi report PASS.

### Bước 4 — deploy lên production

1. Chạy `merge3.py` ở chế độ dry:

   ```bash
   ssh <alias> 'python3 -I - --base <base> --stg <STG>/wp-content --prod <PROD>/wp-content --roots themes/<THEME>,mu-plugins --skip mu-plugins/zz-staging-safety.php' < skills/wp-staging-deploy/scripts/merge3.py
   ```

2. Đọc plan. Mỗi dòng là `stg` (lấy bản staging) hoặc `merged` (gộp bằng diff3). Nếu script in `DỪNG`, xử lý từng file trong danh sách rồi chạy lại.
3. Trình plan cho người duyệt. Chỉ chạy `--apply` khi người duyệt đồng ý ghi production.
4. Chạy lại lệnh với `--apply --backup-dir /root/deploy-<ngày>`. Ghi lại lệnh rollback mà script in ra.
5. Sinh lại CSS Elementor trên production cho các tài liệu bị ảnh hưởng (`IDS=...`).
6. Purge theo URL: `purge_urls.php` với `URLS=...`, chạy `DRY=1` rồi `DRY=0`. Gọi 1 request không cache để LiteSpeed gửi hàng đợi.
7. Chạy `web-qa-gate` trên production.

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
- [ ] Plan gộp đã đọc từng dòng. Không còn dòng `DỪNG`.
- [ ] File chỉ dùng cho staging nằm trong `--skip`.
- [ ] `web-qa-gate` PASS trên staging trước khi ghi production.
- [ ] Có thư mục backup và lệnh rollback trước khi `--apply`.
- [ ] Purge theo URL, không purge toàn site.
- [ ] Người duyệt đã đồng ý ghi production cho lần này.
- [ ] Mỗi hàm toàn cục mới trong mu-plugin đã kiểm `function_exists` trên staging trước khi chép. Nguồn lỗi: 17/10, site agency mẫu, mu-plugin trùng tên hàm làm staging báo critical error, `php -l` không bắt.
- [ ] `stg_leak_check.sh` trả 0 trên thư mục đợt. Log, file và chat không chứa host staging, mật khẩu DB hay mật khẩu Basic Auth. Nguồn lỗi: 18/10, site agency mẫu, host staging lộ ≥8 lần vì lệnh không pipe qua bộ che hoặc regex chung `stg-…` để lọt.

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
- Không in secret, host staging hay mật khẩu ra terminal, log hoặc file.
- Không chạy lệnh staging tự viết mà không pipe qua `stg_mask`.
- Không báo xong đợt khi `stg_leak_check.sh` chưa trả 0 trên thư mục đợt.

## Anti-patterns

- Chép đè cả thư mục theme từ staging lên production. Cách này xoá thay đổi production làm sau lần refresh.
- Mount con dưới `uploads` của staging khi chưa `--make-private`.
- Gọi `litespeed_purge_post` trên site có `purge-post_all=1`.
- Báo deploy xong khi chưa chạy `web-qa-gate` trên production.
- Che host bằng regex chung kiểu `stg-[a-z0-9-]+`. Regex đó để lọt host thật (18/10). Dùng `stg_mask`, hàm này thay đúng chuỗi host.
- `source` file `.env` để lấy mật khẩu. Giá trị có ký tự shell sẽ chạy như lệnh và in một phần ra lỗi (17/10).

## Changelog

- v1.1 (2026-10-25): sec-3 thêm `stg_env.sh`, `stg_tunnel.sh`, `stg_get.sh` (che đúng chuỗi host, tunnel tự nối lại, `SSH` giữ mã thoát); sec-2 thêm Bước 6 quét lộ bằng `stg_leak_check.sh`; sec-5 kiểm trùng tên hàm ở Bước 3; ui-6 thêm bẫy URL tuyệt đối và opcache. Test offline 36/36 và `test_merge3.py` 3/3.
- v1.0 (2026-10-19): bản đầu. Gom script deploy, refresh staging, regen CSS và purge của 2 site nội bộ thành script dùng chung, có tham số. `merge3.py` thêm backup và lệnh rollback trước khi chép. Lượt thử 19/10 trên server thật, chế độ dry: plan gộp trùng script cũ (15 file), regen đếm 88 tài liệu như script cũ.
