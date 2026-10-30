# Giao CSS gọn lên site, purge, CDN, job tái tạo, trả lại

Đọc file này ở Bước 7–11 của SKILL.md. Số liệu và bẫy lấy từ lượt chạy thật trên một site WordPress (OpenLiteSpeed + LiteSpeed Cache 7.9.1 + Guest Mode, CDN Bunny chia vùng) ngày 26–27/10/2026.

## 1. Thành phần trên server

| Thành phần | Nơi | Vai trò |
|---|---|---|
| mu-plugin `ucss-swap.php` (mẫu ở `templates/`) | `wp-content/mu-plugins/` | Ở filter `litespeed_buffer_after`: tìm `<link … /wp-content/litespeed/css/<md5>.css>`, tra map, đổi `href` sang file gọn khi map có đúng md5 và đúng path. Thêm `onerror` quay về file gốc. Bỏ qua người đăng nhập, admin, feed, REST. Có file `OFF` thì không đổi gì |
| `map.php` | thư mục CSS gọn (mặc định `wp-content/ucss/`) | Mảng PHP `files[md5] = {f: tên file gọn, p: {path: 1}}`. OPcache giữ, không gọi `file_exists` mỗi request |
| File gọn `<md5 gộp>.<md5 gọn 8>.css` | cùng thư mục | Tên đổi theo nội dung. Không đặt trong `wp-content/litespeed/`, vì purge CSS của LiteSpeed xoá thư mục đó |
| Khối `context` vhost (`templates/vhost-ucss-block.txt`) | vhost OpenLiteSpeed | Cache trình duyệt 1 năm cho thư mục CSS gọn. Cần restart graceful |

Mu-plugin đổi HTML trước khi LiteSpeed lưu cache. Vì vậy mọi thay đổi map chỉ có hiệu lực ở trang đã purge.

## 2. Giao một bản map

1. `make_map.py <outDir> <stage>`: path chỉ vào map khi mọi biến thể của path đó có kết quả kiểm đạt (0 lệch style, không mất font, không lệch animation, không lệch chiều cao). Thiếu một biến thể thì path giữ file gốc.
2. `php -l <stage>/map.php`.
3. Chép stage lên server, chạy `deploy_ucss.sh` với `DRY=1`, đọc dòng tóm tắt (số file gọn, số path, số file mới, md5 map cũ và mới), rồi `DRY=0`.
   - Script không xoá file gọn cũ. Trang đã cache (ở LiteSpeed và CDN) còn trỏ tới file cũ tới khi hết hạn.
   - Map ghi bằng `mv` nguyên tử. Bản cũ giữ ở `backup-map-<giờ>.php`.
4. Purge LiteSpeed theo URL, mỗi lệnh tối đa 12 path (`purge_ucss.sh`, danh sách nhóm do `regen.sh` hoặc `make_map.py` sinh). Không purge toàn site.
5. Làm nóng ngay các path vừa purge, đủ biến thể: `lam_nong.sh` của `wp-pagespeed` với `-W both`. Site chặn `guest.vary.php` thì thêm `-V guest-d,guest-m`.
6. Có CDN: purge CDN theo URL rồi làm nóng CDN ngay (mục 3).
7. Kiểm sau giao:
   - 5xx từ giờ giao bằng `log_health.py` (không gán cột awk cứng).
   - HTML của 3–5 path có thuộc tính đánh dấu của mu-plugin và trỏ đúng file gọn.
   - `cache_variants.py` của `wp-pagespeed`: robots và canonical giống nhau ở 5 biến thể.
   - Mỗi file gọn trả 200, `content-type: text/css`, có header cache 1 năm.

Site mẫu 26/10: deploy 23:50, purge 6 nhóm, làm nóng 66 path × 4 biến thể (264 lượt, 0 lỗi), 5xx = 0.

### 2b. Sửa vài dòng map ngoài `regen.sh`

1. Lấy khoá `css_src_lockdir`.
2. Chép file gọn mới vào thư mục CSS gọn. Kiểm từng file có trên server và md5 khớp tên.
3. Sửa đúng các dòng cần đổi trong map live. Ghi bằng file tạm rồi `mv`.
4. Purge LiteSpeed các path đổi, làm nóng, purge và làm nóng CDN. Nhả khoá.

- Không ghi map trước khi chép file. Mu-plugin thấy file không có thì giữ link file gộp. Site agency mẫu 27/10/2026: vòng chép chạy với `IFS=' '` nên không chép file nào, 4 trang dùng CSS gộp khoảng 2 phút.
- Không dùng `deploy_ucss.sh` hay lệnh trả lại kiểu "chép đè map cũ" cho việc này. Hai cách đó thay cả `map.php`, nên xoá khoá `all` và bản sửa của lane khác. Lệnh trả lại của một lần sửa dòng chỉ trả đúng các dòng đó.

### 2c. Giao khoá `all`

1. Cài mu-plugin bản có nhánh `all` (`templates/ucss-swap.php`) trước hoặc cùng lượt với map có `all`. Bản mu-plugin cũ bỏ qua khoá này.
2. Giao map như mục 2.
3. Purge cả nhóm bài của md5 đó theo lô 12 path, làm nóng ngay sau mỗi lô, rồi purge và làm nóng CDN.

- Mu-plugin chỉ đổi HTML khi LiteSpeed dựng lại cache. Bài còn bản cache dựng trước lúc giao vẫn tải file gộp. Bài có bản cache dựng trước khi khoá `all` có hiệu lực cũng vậy (site agency mẫu 27/10/2026: một bài ở bản desktop, hết sau khi purge và làm nóng).
- Đo độ phủ kèm số hit và miss của cache. Site agency mẫu 27/10/2026: 86/231 bài tải CSS gọn lúc 18:13, 94/231 lúc 18:27, 230/231 lúc 18:52–18:59. Lúc đo lượt cuối, 216/231 bài trả `miss` vì một phiên khác vừa purge.
- Lượt giao ở site mẫu purge 30 bài mẫu theo nhóm ≤ 12 path: 30/30 bài × 5 biến thể tải CSS gọn sau khi làm nóng.

## 3. CDN đứng trước origin

- Kiểm CDN tách HTML theo gì trước khi giao. Bunny (27/10) chỉ tách HTML theo thiết bị. Vary WebP chỉ áp cho ảnh. Edge rule không ghi đè được header `Accept` (API trả 400, header dành cho nội bộ).
- Hệ quả: với mỗi path và mỗi thiết bị, edge giữ bản `Accept` của lượt đầu tiên sau purge, rồi trả bản đó cho mọi người, kể cả Googlebot.
- Cách xử lý, làm cả hai:
  1. Dựng CSS gọn cho cả bản `Accept: */*` (biến thể `p` desktop, `q` mobile). Googlebot smartphone dùng chung bản cache với `q` (site mẫu: 66/66 path cùng file gộp).
  2. Purge CDN từng URL rồi làm nóng ngay bằng Accept có `image/webp`, đủ UA desktop và mobile, để lượt đầu là bản WebP (ảnh WebP trong HTML).
- Purge Bunny: `POST /purge?url=<URL>&async=false`. Không thêm `exactPath=true`, vì tham số đó chỉ xoá bản desktop. URL kết thúc bằng `/` được thêm ký tự đại diện, nên purge `/muc/` có thể xoá cả bài con. Purge `/` không xoá cả zone.
- Kiểm sau purge: gọi lại vài path bằng cả 2 UA, header `cdn-cachedat` (giờ UTC, dạng `10/26/2026 17:15:55`) phải sau giờ purge. Site mẫu: một lần purge `/` không xoá bản mobile ở một trạm, chưa rõ nguyên nhân.
- Làm nóng đúng trạm khách dùng: tra IP trạm bằng `dig +subnet=<dải ECS>` rồi gọi `curl --resolve <host>:443:<IP>`. Googlebot của site mẫu vào trạm Chicago 100% (log Bunny 26/10). Không in IP trạm vào báo cáo.
- `bunny_purge.py <paths.txt> --site site.json --apply --warm` làm đủ 3 việc trên cho từng path, nhịp 1 request/giây. Cần `cdn_host` và `cdn_warm_ecs` trong `site.json`. `regen.sh` tự thêm `--warm` khi `site.json` có `cdn_host`.

## 4. Job tái tạo hằng ngày (`regen.sh`)

Chạy trên máy của người vận hành bằng launchd (mẫu plist ở `templates/`) hoặc cron. Chuỗi:

1. Dừng nếu khoá bảo trì server đang bị giữ.
2. Quét bộ URL đã chọn (`chon.tsv`) ở 4 biến thể, lấy md5 file gộp mỗi cặp.
3. Cặp chưa có kết quả hoặc md5 đổi: sinh lại, dựng lại, kiểm lại mọi cặp dùng file gộp vừa dựng lại.
4. `make_map.py`, so với map trên site. Map không đổi thì dừng.
5. `DRY=1` dừng ở đây và in số path sẽ purge.
6. Giao: deploy DRY rồi thật, purge LiteSpeed các path đổi, làm nóng, purge và làm nóng CDN.

- Lỗi ở bước nào thì dừng. Map trên site giữ nguyên, trang ngoài map dùng file gốc.
- Chạy thử `DRY=1` bằng môi trường tối giản như launchd: `env -i HOME="$HOME" PATH=<PATH của plist> DRY=1 bash regen.sh`. Site mẫu 27/10: lượt DRY đầu dừng an toàn vì khoá production đang bận 120 giây. Đặt thời gian chờ khoá 15 phút cho job đêm.
- Giờ chạy tránh cửa sổ bảo trì server và giờ purge của lane khác.

## 5. Trả lại

| Thay đổi | Trả lại |
|---|---|
| map.php | Chép `backup-map-<giờ>.php` về chỗ cũ, purge các path đổi, làm nóng |
| mu-plugin | Tắt nhanh: tạo file `OFF` trong thư mục CSS gọn, purge mọi path trong map (12 path mỗi lệnh), làm nóng. Gỡ hẳn: chuyển file mu-plugin vào thư mục quarantine, rồi purge như trên |
| File gọn | Để nguyên ít nhất 8 ngày sau khi tắt, vì trang đã cache còn trỏ tới. Sau đó chuyển cả thư mục vào quarantine. Không xoá |
| Khối vhost | Chép backup vhost về, restart graceful có khoá bảo trì |
| HTML ở CDN | Sau khi tắt và purge LiteSpeed: `bunny_purge.py <paths> --apply --warm` |
| Job tái tạo | `launchctl bootout gui/$(id -u)/<label>`, chuyển plist vào thư mục lưu trữ |

Ghi bảng trả lại vào `rollback.md` của đợt trước khi giao.

## 6. Critical CSS sau khi có CSS gọn

- Dựng critical CSS từ CSS gọn, không từ file gộp. Critical CSS kèm file gộp lớn nạp async làm TBT tăng (site mẫu 26/10: khoảng 244 ms với file 1,48 MB).
- Kiểm khoảng hở của critical CSS bằng `ccss_gap.mjs`: so khung phần tử trong 1,5 màn hình giữa bản "chỉ critical CSS" và bản "critical + CSS gọn", từ HTML lưu local.
  - Thiếu quy tắc ẩn `.screen-reader-text`: link "skip to content" hiện ra rồi biến mất, CLS 0,026–0,028.
  - Desktop thiếu quy tắc của menu thả xuống: menu con hiện ra trong lần vẽ đầu. Script bỏ phần tử trong menu con đang ẩn khỏi kết quả, trừ khi đặt `IN_MENU=1`.
- A/B critical CSS trên PSI bằng `psi_ab.py` của `wp-pagespeed`, ngưỡng ghi trước khi đo.
- Kết quả site agency mẫu 27/10/2026 (6 trang × 2 thiết bị, 96 lượt PSI): critical dựng từ CSS gọn nặng 85–113 KB mỗi trang. Bản critical inline cộng CSS gọn không chặn làm 5/6 trang có nhãn "xấu hơn" ở ít nhất một thiết bị. TBT trung vị từ 0–14 ms lên 7–178 ms. Bản đang chạy (CSS gọn chặn hiển thị) đạt 95,5–99 điểm mobile (trung vị 4 lượt). Lane không giao critical.

## 7. UCSS của QUIC.cloud chen vào

- LiteSpeed Cache có thể tạo file UCSS của QUIC.cloud trong `wp-content/litespeed/ucss/` và link file đó thay CSS gọn. Kiểm trước lần giao đầu: đếm file trong thư mục đó, tìm chuỗi `litespeed/ucss/` trong HTML của bộ URL.
- Chặn bằng mu-plugin riêng dùng filter `litespeed_ucss_exc`, kèm lệnh trả lại. Filter trả `/` thì áp cho mọi URL: lệnh trả lại phải purge mọi trang từng dùng file UCSS, không chỉ trang đã đo.
- Site agency mẫu 27/10/2026: thư mục có 1 file UCSS cho 1 trang. Sau khi áp mu-plugin 05:19: 0/274 HTML còn link `litespeed/ucss/`, không có file UCSS mới.
