# Ghi an toàn lên WordPress

Đọc file này ở Bước 5. Các luật dưới đến từ 2 lượt ghi thật 17/10/2026 (263 thao tác trên một site, nhiều lượt ghi trang trên site khác).

## 1. Thứ tự một lượt ghi

1. Backup: DB đầy đủ hoặc các bảng sẽ chạm. Lưu ở `~/Backups/<host>/<YYYY-MM-DD>/<đợt>-pre/` kèm `SHA256SUMS`.
2. Chạy thử `apply.php` với `DRY=1`. Lưu log JSON vào thư mục backup (`before_values.json`). Log này đủ để rollback từng trường.
3. Đọc mọi dòng `skip`. Mỗi dòng phải có lý do đã hiểu trước khi ghi thật.
4. Chạy `DRY=0`. Script sinh lại CSS Elementor của từng tài liệu vừa ghi, xoá cache sitemap Rank Math, xoá object cache, rồi mới purge cache trang (LiteSpeed, WP Rocket, W3 Total Cache hoặc WP Super Cache, theo plugin đang có). Với `PURGE=0`, người chạy purge theo URL sau khi script xong.
5. Làm nóng các URL vừa purge theo `wp-pagespeed` (`references/checklist-theo-lop.md` lớp 1): header Chrome thật có `image/webp`, cả desktop lẫn mobile, thêm bản plain cho bot.
6. Chạy `verify.py`. Sửa hoặc ghi lý do cho từng dòng lệch.
7. Chạy `python3 -I skills/wp-pagespeed/scripts/cache_variants.py <url sạch> ...` cho URL đã ghi. Robots và canonical phải giống nhau ở 5 biến thể cache.

## 2. Lệnh chạy

```bash
scp skills/wp-content-review-apply/scripts/apply.php plan.json <alias>:/tmp/<phiên>/
ssh -n <alias> 'cd /tmp && sudo -u www PLAN=/tmp/<phiên>/plan.json DRY=1 OUT=/tmp/<phiên>/log-dry.json HOME=/tmp/wpcli-home <php> <wp> --path=<root> eval-file /tmp/<phiên>/apply.php'
scp <alias>:/tmp/<phiên>/log-dry.json .
# Đọc log rồi mới chạy DRY=0 với OUT mới. Xoá thư mục tạm của phiên trên server sau lượt ghi.
```

- `<php>` và `<wp>` lấy từ `wp-server.md`. Ví dụ aaPanel + OpenLiteSpeed: `/usr/local/lsws/lsphp83/bin/php /usr/local/bin/wp`. Thư mục `/tmp/<phiên>/` phải cho user `www` ghi được.
- Đặt mọi biến (`PLAN`, `DRY`, `OUT`, `NEEDLES`, `CHANGES`, `BK`) sau `sudo -u www`. sudo xoá biến đặt trước nó, nên lệnh mất `DRY=1`. Script cũ coi thiếu `DRY` là ghi thật. `apply.php` và `apply_cruft.php` coi thiếu `DRY` là chạy thử. Lỗi đã gặp 20/10.
- Chạy WP-CLI bằng user web (`www`), không chạy bằng root.
- Luôn `cd /tmp` trước. Plugin có thể nạp nhầm file của theme khi chạy từ thư mục theme.
- Bản PHP của web có thể tắt `proc_open` và `exec`. Khi đó `wp db query` và `wp db export` không chạy. Dùng `wp eval-file` với `$wpdb`, hoặc `mysqldump` cho backup. Lint PHP bằng `php -l` ngoài WP-CLI.
- Script `eval-file` tự viết: ghi kết quả ra file `OUT` như `apply.php`. Nếu phải in ra stdout, in JSON giữa hai marker cố định và chạy với `-d display_errors=0`. Lý do: LiteSpeed in dòng "Success:" và plugin in warning PHP lẫn vào stdout. Dùng `json_encode` với `JSON_INVALID_UTF8_SUBSTITUTE`, lỗi thì in `json_last_error_msg()`.
- Không nhúng chuỗi `base64_decode` dài vào file `eval-file`. Bộ quét của server chặn im lặng, lệnh không in gì. Lỗi đã gặp 17/10.
- Lệnh `ssh` trong vòng lặp luôn có `-n`. Thiếu `-n` thì vòng lặp treo (17/10: 120 giây).
- Không viết python hay sed lồng nhiều tầng nháy qua `ssh` từ zsh. Viết file script rồi `scp` lên, hoặc chạy `ssh <alias> bash -s < file`.
- Chạy WP-CLI bằng đúng bản PHP của web. Site bật Redis mà PHP CLI thiếu `redis.so` thì drop-in object cache tự tắt, và lệnh ghi không xoá key trong Redis.
- WP-CLI quét DB lớn chiếm 1,9–2,2 GB mỗi tiến trình. Chạy theo lô với `-d memory_limit=512M` và `ulimit -v`, mỗi lúc một tiến trình nặng. Site agency mẫu 19/10: kernel OOM giết 8 tiến trình WP-CLI chạy song song.
- Script ghi DB phải kiểm số file backup không nhỏ hơn số tài liệu sẽ ghi, trước khi ghi. Lỗi đã gặp 18/10: thư mục backup trống vì lệnh không truyền biến `BK`.

## 3. Luật ghi theo loại

| Loại | Cách ghi | Lý do |
|---|---|---|
| Post meta, Rank Math | `update_post_meta` với `wp_slash` | Giữ dấu `\` trong chuỗi |
| `post_title`, `post_content` | `$wpdb->update` rồi `clean_post_cache` | Không đổi ngày cập nhật. WP-CLI không có `unfiltered_html`, `wp_update_post` lọc HTML |
| `post_name` (slug) | `$wpdb->update` rồi thêm redirect 301 Rank Math từ đường dẫn cũ | Giữ link cũ và tín hiệu SEO |
| ACF | `update_field` | ACF giữ meta tham chiếu `_field` |
| Elementor | Sửa mảng `_elementor_data`, lưu bằng `wp_slash(wp_json_encode())`, `clean_post_cache` | Sai escape làm hỏng trang |
| Redirect | Chèn dòng vào `wp_rank_math_redirections`, 2 mẫu nguồn có và không có `/` cuối, rồi xoá option `rank_math_redirections_cache` | Rank Math khớp lỏng nếu thiếu mẫu exact |
| Form WPForms | `$wpdb->update` cột `post_content` bằng `wpforms_encode($form)`, rồi `clean_post_cache` | `wp_update_post` chạy kses lên JSON của form và làm hỏng form |

- Kiểm API theo phiên bản plugin trước khi gọi. Ví dụ: WPForms 1.9.0.3 không có `wpforms()->obj()`.
- Script ghi tự viết phải chạy lại được: mục đã áp báo "đã đúng" và không áp lần hai, như `apply.php`.

- Site bật object cache (Redis, Memcached): mọi lệnh SQL thô tự viết thêm ngoài `apply.php` phải kèm `clean_post_cache($id)` cho bài, hoặc `wp_cache_delete($tên, 'options')` cho option. Không có cách khác thì `wp cache flush`. Thiếu bước này thì trang hiện dữ liệu cũ tới khi flush. Xoá object cache trước, purge URL sau. Chỉ `FLUSHDB` đúng DB của site, không `FLUSHALL`.
- Gọi `kses_remove_filters()` trước khi ghi nội dung có HTML.
- So khớp trước khi ghi: giá trị hiện tại phải bằng `before` lúc soạn (sau khi chuẩn hoá NFC, bỏ thẻ, gộp khoảng trắng). Khác thì bỏ qua và báo.
- Nội dung bài: so `md5` của `post_content` lúc tính và lúc ghi.
- Mỗi thay đổi chữ trong đoạn văn phải khớp đúng một vị trí. Khớp 0 hoặc nhiều vị trí thì dừng mục đó.

## 4. Bẫy đã gặp

- WPML: trang EN có thể là bản nhân đôi (`_icl_lang_duplicate_of`). Ghi vào bản nhân đôi bị WPML ghi đè lại. Tách bản nhân đôi trước khi ghi. Lấy URL EN bằng filter `wpml_permalink`.
- Trang EN dùng chung template với bản VI nhưng không có ACF: template in chuỗi VI mặc định.
- Theme có thể đẩy trang đính kèm không có bài cha về trang chủ bằng 302. Khi đó redirect 410 của Rank Math cho URL đính kèm không chạy: cần mu-plugin trả 410 trước bước redirect của theme.
- `wp_strip_all_tags` xoá cả nội dung thẻ `script`. Khi so chữ, bỏ thẻ bằng regex.
- `url_to_postid()` có thể trả bản nháp trùng slug. Kiểm `post_status` của ID tìm được.
- Permalink Manager Pro tự ghi URI `category/…` cho chuyên mục chưa có URI riêng, mỗi khi chuyên mục đổi tên, slug hay cha. Đổi chuyên mục trước. Sau đó mới đọc option `permalink-manager-uris`, đặt URI cho từng khoá `tax-<term_id>` và xoá khoá thừa. Site khoá học mẫu 17/10: script chuyên mục tạo 301 sai vì Permalink Manager còn giữ URI cũ, phải chạy lại 3 lần.
- Redirect URL chuyên mục cũ bằng Rank Math: dùng mẫu regex phủ cả tiền tố `category/` và phân trang, ví dụ `^(?:category/)?seo/keyword-research(/page/[0-9]+)?$`. Mẫu exact bỏ sót `/page/N/`.
- Redirect cũ đang chiếm URL mới (URL mới đang 301 về URL cũ): đặt dòng đó `inactive` trước khi thêm 301 mới. Giữ cả hai thì tạo vòng lặp.
- Robots của chuyên mục nằm ở termmeta `rank_math_robots`, dạng mảng (`['noindex']`). Tên chuyên mục lưu `&` thành `&amp;`: giải entity trước khi so.
- Bài so sánh hoặc bài top nhà cung cấp mô tả cả đối thủ. Không tự thay số trong đoạn nói về công ty khác.
- `post_content` có thể chứa `\r\n` và `\xa0`. Python `open()` ở text mode đổi `\r\n` thành `\n`, nên chuỗi cũ lấy từ file đã ghi lại không khớp DB và DRY báo 0 vị trí. Lấy chuỗi cũ từ JSON đọc thẳng DB, hoặc mở file với `newline=''`.
- LiteSpeed minify HTML xoá `\r\n` cùng dấu cách quanh nó. Hai câu chỉ cách nhau bằng xuống dòng sẽ dính nhau trên trang ("hình.Meta"). Nối câu mới bằng dấu cách. Khi verify, so chữ đã chuẩn hoá khoảng trắng.
- Staging có thể là bản clone cũ (site agency mẫu: clone 01/2026). Trước khi ghi staging, chép từ production đúng các bài và option sắp ghi, rồi DRY trên staging. Không chép lại cả DB khi phiên khác đang thử trên staging: lệnh đó ghi đè trạng thái của phiên khác.
- Không verify bằng URL có `utm_*`, `fbclid`, `gclid`. LiteSpeed bỏ các tham số này khỏi khoá cache, còn theme hoặc plugin SEO trả `noindex` cho URL có query, nên bản `noindex` vào cache của URL sạch. Bỏ cache bằng tham số nằm trong `cache-exc_qs`, hoặc cookie `_lscache_vary` ngẫu nhiên. Cookie ngẫu nhiên giữ đúng robots và canonical nhưng tạo thêm bản cache. Kiểm robots và canonical chỉ trên URL sạch.

## 4b. Nhiều phiên cùng ghi một site

- Mỗi phiên giữ khoá theo tên phiên. Đọc khoá của phiên khác trước khi ghi một bài, file theme hay mu-plugin. Không ghi chỗ đang có khoá của phiên khác.
- Việc phụ thuộc kết quả của bước khác chỉ ghi production sau khi người kiểm độc lập của bước đó báo đạt. Lỗi đã gặp: object cache bật trên production 3 phút trước khi lượt kiểm staging xong.
- File tạm trên server đặt trong thư mục riêng của phiên. Không ghi đè file của phiên khác.
- Luật rebase khi DRY báo `raw_before` không còn khớp live:
  1. Live đã bằng chữ duyệt: mục đã xong. Không ghi. Gắn `appliedAt` sau khi kiểm cả bản cache.
  2. Live là chữ của một thẻ duyệt sau (so ngày duyệt): thẻ cũ bị thay. Không ghi. Đóng thẻ với ghi chú "thay bằng <id>".
  3. Phần khác của cùng trường đã đổi, còn chuỗi cũ của ô vẫn xuất hiện đúng một lần: đọc lại giá trị live, dựng lại `raw_after` bằng cách chỉ thay đúng chuỗi cũ đó. Ghi cả `raw_before` cũ lẫn bản rebase vào báo cáo.
  4. Chuỗi cũ không còn, hoặc còn nhiều hơn một lần: dừng ô đó, đưa vào danh sách giữ lại cho người duyệt.
- Lấy chuỗi cũ từ DB, không lấy từ file thẻ: file thẻ có thể dùng `\n` trong khi DB dùng `\r\n` (mục 4).

## 5. Rollback

- Một trường: lấy giá trị trong `before` của log chạy thử, ghi lại bằng cùng loại lệnh.
- Redirect: đặt `status` của dòng trong `wp_rank_math_redirections` thành `inactive`, không xoá dòng.
- Cả đợt: nhập lại các bảng từ backup, rồi purge. Ghi lệnh rollback vào báo cáo trước khi chạy `DRY=0`. Nhập lại bảng cũng xoá mọi thay đổi phiên khác ghi sau mốc backup: chỉ dùng khi không phiên nào khác ghi cùng bảng.
- Rollback khi phiên khác có thể đã sửa cùng bài hay cùng file: chép backup đè lên sẽ xoá thay đổi của họ. Ghi md5 của giá trị hoặc file ngay sau khi ghi xong. Trước khi trả, so md5 hiện tại với md5 đó. Khớp thì trả. Khác thì không chép đè: sửa tay từ giá trị `before` và giữ phần của phiên khác. Ghi trong `rollback.md` bài và file nào đã có phiên khác sửa sau mình.
