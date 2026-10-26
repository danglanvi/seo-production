# Động tác thừa đã gặp và cách thay

Đọc file này trước lệnh đầu tiên. Danh sách lấy từ các đợt thật 16–24/10/2026. Mỗi dòng ghi động tác thừa, cách thay và lượng việc tiết kiệm được.

## 1. Đo

| Động tác thừa | Cách thay | Tiết kiệm |
|---|---|---|
| Kết luận từ 1 lượt PSI, rồi đo lại khi số nhảy | Đo 3 lượt ngay từ đầu, so trung vị và cột observed | Một vòng đo lại 15–30 phút |
| Chạy PSI cho mọi URL sau mỗi thay đổi nhỏ | `perf_probe.mjs` 3 lượt cho template bị ảnh hưởng. PSI toàn bộ chỉ ở cuối đợt | Khoảng 30 phút mỗi đợt, quota PSI |
| Hỏi tiến độ PSI nhiều lần trong lúc chờ | Chạy nền, chờ thông báo khi xong | Nhiều tool call đọc log |
| Đo staging bằng PSI | PSI không qua Basic Auth. Dùng `perf_probe.mjs` | Một lượt lỗi và một lần đổi hướng |
| So staging (mô phỏng) với production (PSI) | Đo cả 2 bằng `perf_probe.mjs` | Kết luận sai do khác công cụ |
| Dựng nhiều script Chrome trên máy để tái hiện độ trễ chỉ PSI thấy | A/B trên PSI bằng bản HTML tĩnh (`do-dac.md` mục 3) | 5–8 lượt chạy probe không ra kết quả |
| Đo một URL 3–4 lượt liên tiếp để A/B | Xen kẽ nhiều URL, `--runs 1`. File tĩnh A/B: mỗi dòng một `?r=<số>`. Trang WordPress thật: URL sạch, hoặc tham số nằm trong `cache-exc_qs`, không dùng `utm_*` (`do-dac.md` mục 2) | Một đợt đo hỏng vì PSI trả kết quả cache, hoặc bản `noindex` vào cache URL sạch |
| Đọc log PSI định kỳ trong lúc chờ | Chờ thông báo của lệnh chạy nền. Cần chặn đến khi xong thì dùng `caffeinate -w <pid>` (macOS) | Nhiều tool call đọc log |
| Đo một URL đại diện cho mỗi template, người duyệt tự đo trang con và thấy điểm thấp | Đo mọi trang con của template (thanh toán, cảm ơn) và 3–5 bài blog khác định dạng ảnh đại diện ngay từ baseline | Một vòng phản hồi và một đợt sửa thứ hai |
| Tin nguyên nhân "Phông chữ web" của PSI, sửa font trước | Đo `cls_trace.mjs` từng nhánh dữ liệu, xem toạ độ shift | Một đợt sửa font không trúng |
| Chặn mọi domain ngoài khi đo CLS | Chỉ chặn tracking. Ảnh chức năng (mã QR) bị chặn thì JS ẩn ảnh, tạo shift giả | Một kết luận sai về CLS |
| Gõ `skills/wp-pagespeed/scripts/…` từ root workspace, lỗi "No such file" | Đặt `WPS` bằng thư mục của skill, gọi `"$WPS/scripts/…"` | 5 lần đường dẫn sai, khoảng 5 phút |
| Chạy `psi_run.py` tiền cảnh 30–45 phút, lệnh bị cắt hoặc phiên treo | `--dry-run` xem ước tính. Trên 8 phút thì chạy nền có báo xong (`--fg-ok`), hoặc `--detach` rồi đọc `PSI_STATE.txt` | Một đợt đo hỏng, một phiên treo |
| Chép `psi_run.py` vào thư mục lane rồi sửa | Gọi bản `$WPS/scripts/`, dùng chung thư mục kết quả của mốc | Bản sao thiếu luật mới (song song, guard) |
| Đo staging khi tunnel đã tắt hoặc URL trả 404, rồi tin số rất nhanh | `--expect '<title>'`, đọc dòng `GUARD`, mã 4 là dừng | Một kết luận sai, 2 lần trong 10/2026 |
| Đo A/B 7 đợt, khoảng 80 lượt mobile cho một URL | `psi_decide.py` với ngưỡng đặt trước, dừng ở nhãn đầu tiên | Khoảng 100 phút mỗi lane |
| Mở lane đuổi CLS hoặc LCP lab khi field đã đạt | Đọc `loadingExperience` trước (SKILL.md Bước 3 mục 0) | 118 phút một lane |
| Chạy lab CLS nhiều lượt trên Mac khi lab không tái hiện PSI | `psi_cls_dump.py`, rồi `lh_local.mjs --block-vary` (`cls-chi-psi-thay.md`) | 25–120 phút mỗi ca |
| Làm nóng toàn site sau khi purge vài URL | `lam_nong.sh` với đúng path vừa purge | 150 phút làm nóng thừa |
| Viết tay bảng điểm còn trừ hoặc script trung vị theo template | `psi_con_tru.py [--mt]` | Một vòng phản hồi của người duyệt |

## 2. Critical CSS

| Động tác thừa | Cách thay | Tiết kiệm |
|---|---|---|
| Bật critical CSS cho mọi template rồi tắt 5/11 | A/B từng template trước khi bật | Một vòng bật, đo, rollback |
| Nạp file gộp bằng `preload`, đo thấy FCP xấu, rồi đổi | Dùng `media="print"` + `onload` ngay từ đầu | Một vòng sửa và đo |
| Sinh critical CSS từ text CSS gốc, gặp lỗi bố cục, sinh lại | Lấy CSS từ CSSOM (`ccss_gen.mjs` đã làm) | Một vòng sinh và chụp |

## 3. Ảnh và font

| Động tác thừa | Cách thay | Tiết kiệm |
|---|---|---|
| Đổi `sizes` của logo, header vỡ, sửa lại | Chỉ bỏ cỡ lớn khỏi `srcset` | Một vòng sửa và chụp |
| Chạy `fontmap` 4 lần: sai chế độ đo, sai cascade, sai ảnh cắt | `fontmap.mjs` mặc định đo chế độ thường, xét `!important`, cắt phần tử chữ lớn nhất | 3 lượt chạy và dựng lại báo cáo |
| Đọc `before_optm` rồi kết luận font của khách | Kết luận bằng chế độ thường. `--src` chỉ để tìm file gốc | Một kết luận sai |
| Viết tay `@font-face` cho font Google Fonts, sai subset hoặc độ đậm | `gfonts_selfhost.py` | Một vòng sửa và đo |
| So font tự host với bản cũ bằng mắt trên ảnh chụp | `font_same.mjs` so số đo, in GIỐNG hoặc KHÁC | Một vòng chụp và soi |
| Viết lại script font dự phòng, cắt Font Awesome, sinh bản ảnh nhẹ cho site mới | `fallback_faces.py`, `fa_subset/`, `img_variants.py`, `img_display_width.mjs` | Khoảng 20 phút mỗi site. Script fallback đã bị viết tay 4 lần |

## 4. Server và shell

| Động tác thừa | Cách thay | Tiết kiệm |
|---|---|---|
| Nhiều lệnh `wp eval` nhỏ, mỗi lệnh một SSH | Gom vào một file PHP: scp, `wp eval-file`, xoá file tạm | Mỗi truy vấn 1 SSH và 1 tool call |
| Restart OpenLiteSpeed sau từng thay đổi `.htaccess` | Gom thay đổi cần restart vào một lần | Thời gian site chập chờn |
| Purge cache sau từng lệnh | Purge một lần sau cả đợt | Lượt MISS thừa, đo nhiễu |
| Chạy WP-CLI từ thư mục theme | `cd /tmp` trước. Plugin có thể nạp nhầm file của theme | Một lỗi fatal giả |
| Dùng `timeout` trên macOS | macOS không có `timeout`. Dùng timeout trong script | Một lệnh lỗi |
| `xargs` với danh sách dài | Vòng lặp shell theo lô | Lỗi "command line too long" |
| `rm -rf` thư mục thử | Ghi ra thư mục mới (bị chặn quyền và trái luật không xoá) | Một lệnh bị từ chối |
| Để WP-CLI in cảnh báo SSH vào output | Lọc bằng `2>/dev/null \| grep -v -E "post-quantum\|store now\|upgraded\|WARNING"` | Context bị nhiễu |
| `for u in $urls` trong zsh | zsh không tách biến theo dòng. Dùng `while read -r u; do …; done < urls.txt` | Một vòng đo ra kết quả giả "000" |
| `echo =====` trong zsh | zsh hiểu `=` đầu từ là tên lệnh. Đặt chuỗi trong nháy | Một lệnh lỗi |
| `set -- $x` trong zsh để tách "slug MÃ" | zsh không tách biến không nháy. Dùng `${=x}` hoặc ghép `slug:MÃ` rồi `${c%%:*}`, `${c##*:}` | Một lượt đo nhầm trang: URL có dấu cách, WordPress đoán sang trang khác |
| `python3 -I` cho script cần Pillow (`shot_cmp.py`) | `-I` bỏ qua site-packages của user nên không thấy Pillow. Chạy script đọc file của mình không cần `-I` | Một lệnh lỗi `No module named 'PIL'` |
| Chép từng file theme bằng `scp`, rồi `chown`, `chmod`, purge bằng tay | `scripts/deploy_theme_files.sh`: backup bản trên server, lint PHP, chép, sửa owner và quyền, purge trong một lệnh | 4–5 lệnh mỗi lần chép, một lần quên backup |
| Đọc kết quả qua `\| tail` rồi tin mã thoát 0 | Mã thoát của pipe là của lệnh cuối. Dùng `set -o pipefail` hoặc đọc output lỗi | Một lần tưởng xong (rsync chưa cài trên server) |

## 5. Phân tích

| Động tác thừa | Cách thay | Tiết kiệm |
|---|---|---|
| Gom template bằng embedding khi DB có `_wp_page_template` | `templates.php` qua `wp eval-file` | Một lượt EmbeddingGemma và hiệu chuẩn |
| Gọi Jev cho thư viện trùng hoặc ảnh LCP | Regex trên HTML và JSON Lighthouse | Chi phí Jev, một lớp kiểm |
| Đọc toàn bộ báo cáo dài để tìm một mục | `grep -n "^## \|^### "` rồi đọc đúng đoạn | Hàng nghìn dòng context |
| Đọc lại JSON PSI bằng tay | `psi_table.py --detail` | Nhiều lượt đọc file 300–600 KB |
| Viết code tạm để so 2 file JSONL của `perf_probe.mjs`, rồi đọc từng lượt tìm nguồn CLS | `probe_table.py --detail` | 2–3 tool call mỗi lần so |
| Mở trình duyệt để tìm phần tử gây CLS | Đọc `shifts` trong kết quả `perf_probe.mjs` | Một vòng chụp và soi |
| Gọi GSC API khi scope chưa có quyền | Kiểm quyền một lần, nếu 403 thì ghi giới hạn | Nhiều lượt lỗi lặp |
