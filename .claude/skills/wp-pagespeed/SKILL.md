---
name: wp-pagespeed
description: "Đo và tối ưu PageSpeed site WordPress theo template khi có quyền vào server: PSI trung vị 3 lượt, mô phỏng Chrome cho staging, sửa theo 7 lớp có A/B và rollback, phối hợp Jev + EmbeddingGemma. Dùng khi tăng điểm PageSpeed, Core Web Vitals hoặc so staging với production."
metadata:
  version: "1.14"
---

# wp-pagespeed — tối ưu PageSpeed WordPress theo template

Quy trình đã chạy thật trên 2 site WordPress (VPS, OpenLiteSpeed, LiteSpeed Cache) ngày 16–18/10/2026. Site thứ nhất có 13 template: điểm PSI trung vị tăng từ 63 lên 76 (mobile) và từ 87 lên 98 (desktop). Site thứ hai so staging với production trước khi đổi theme, rồi nghiệm thu sau khi đổi: trung vị mobile 11 template tăng từ 66 lên 88.

Đường dẫn script: đặt biến `WPS` bằng thư mục chứa file SKILL.md này. Runtime thường in thư mục này khi nạp skill (Claude Code: dòng "Base directory for this skill"). Trong repo SEO Production, đứng ở root repo thì `WPS="skills/wp-pagespeed"`. Mọi lệnh gọi `"$WPS/scripts/…"` và `"$WPS/templates/…"`, luôn đặt trong nháy vì đường dẫn có thể có dấu cách. Đường dẫn khác (`00-client-context/`, `03-audits/`, `tools/`) tính từ root repo. Bộ model nằm ở `tools/ai-assist/`.

## Khi nào dùng

- Đo và tăng điểm PageSpeed, Core Web Vitals của một site WordPress.
- So tốc độ bản staging với production trước khi đổi theme hoặc plugin.
- Kiểm lại tốc độ sau một đợt sửa giao diện.
- Không dùng khi: audit technical SEO toàn site (`technical-seo-audit`, khu vực 5 chỉ chấm CWV), sàng mã độc (`wp-security-hardening`), redesign giao diện.
- Không có quyền server: chỉ chạy Bước 1–3 bằng PSI và `shot.mjs`, giao plan cho dev của site.

## Đọc trước

- `references/tool-call-thua.md`: đọc trước lệnh đầu tiên. File liệt kê động tác thừa đã gặp và cách thay.
- `00-client-context/wp-server.md`: cách vào server, lệnh WP-CLI, staging, plugin cache, bẫy riêng của site. Chưa có thì tạo từ `_TEMPLATES/wp-server.md`.
- `references/do-dac.md`: đọc ở Bước 2.
- `references/checklist-theo-lop.md`: đọc ở Bước 3–4.
- `references/phoi-hop-model.md`: đọc trước khi gọi Jev, EmbeddingGemma hoặc model khác.
- `references/agentic-browsing.md`: đọc khi cần tối đa hạng mục "Duyệt web bằng tác nhân", Accessibility, SEO của PSI.
- `references/cls-chi-psi-thay.md`: đọc khi PSI báo CLS mà lab trên máy không tái hiện.
- `references/fcp-guest-mode.md`: đọc khi FCP mobile dồn một mốc ở site bật LiteSpeed Guest Mode.
- `references/ttfb-cache-trang.md`: đọc khi CrUX TTFB p75 trên 0,8 s hoặc lượt đầu của khách thường miss cache.

## Input

| Bắt buộc | Ví dụ | Thiếu thì |
|---|---|---|
| Domain production | `example.vn` | Hỏi. |
| SSH alias, web root, lệnh WP-CLI | Theo `wp-server.md` | Hỏi. Không tự dò credential. |
| Staging (nếu có) | Host, cách vào, tên biến Basic Auth trong `.agent-secrets/.env` | Bỏ phần staging, ghi giới hạn. |
| Phạm vi đã duyệt | Lớp 1–6 trên production, lớp 7 chưa duyệt | Chỉ đo và lập plan. |
| Thư mục evidence | `03-audits/technical/pagespeed-<YYYY-MM-DD>/` | Dùng mặc định này. |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,ssh,wp-cli,pagespeed-api,pillow,cwebp?,pngquant?,axe?,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Kiểm thêm dependency riêng của skill:

Chạy một lệnh gộp từ root repo. Nếu một dòng báo thiếu, bỏ phần dùng dependency đó và ghi vào báo cáo.

```bash
{ [ -n "$PAGESPEED_API_KEY" ] || grep -qsE '^\s*(export\s+)?PAGESPEED_API_KEY=' .agent-secrets/.env; } && echo "psi key: có"
node --version; python3 -c "import PIL; print('PIL: có')"; which cwebp pngquant
python3 tools/capabilities.py check --need 'fonttools?,lighthouse?'
ssh -o BatchMode=yes <alias> 'echo ssh: có'
```

- Chrome: macOS dùng bản cài sẵn. Máy khác đặt biến `CHROME_BIN`.
- Critical CSS cần `penthouse`, `puppeteer-core`, `clean-css`, `postcss`. Cài một lần theo dòng đầu của `"$WPS/scripts/ccss_gen.mjs"`.
- fontTools và brotli chỉ cần cho `fallback_faces.py` và `fa_subset/`. Thiếu thì bỏ hai script này.
- `lh_local.mjs` dùng module Lighthouse trong cache npx. Thiếu module thì script thoát mã 3. Khi đó bỏ bước dựng lại môi trường PSI và ghi giới hạn.
- Jev và EmbeddingGemma: kiểm theo `tools/ai-assist/README.md` mục 5.

### Bước 0b — bối cảnh của site

1. Đọc `HANDOFF.md` và lộ trình của workstream site trước khi đo. Nếu site sắp deploy lại (theme mới, cutover, đổi nền tảng), chỉ đo mốc và ghi checklist cho bản mới. Không sửa, không dọn trên bản sắp thay. Lỗi đã gặp 16/10/2026: agent tối ưu và gỡ một dịch vụ trên site sắp đổi bản, người duyệt huỷ sau khoảng 25 phút.
2. Nhiều lane cùng làm một site: theo luật điều phối của workstream. Tổng request PSI đồng thời lên một site không quá 2.

## Bước 1 — chọn URL đại diện theo template

1. Lấy danh sách template từ DB bằng một lệnh. Script trả số trang theo `_wp_page_template`, theo post type, số trang dùng Elementor, kèm một URL mẫu cho mỗi nhóm.

   ```bash
   scp "$WPS/scripts/templates.php" <alias>:/tmp/wps-templates.php
   ssh <alias> 'cd /tmp && <lệnh wp> --path=<root> eval-file /tmp/wps-templates.php; rm -f /tmp/wps-templates.php'
   ```

2. Chọn một URL cho mỗi template có traffic, tối đa 15 URL. Ưu tiên URL có click cao trong GSC nếu có quyền (`tools/gsc/gsc.sh`).
   - Site dùng CSS gộp LiteSpeed: nhóm theo md5 file gộp chính xác hơn nhóm theo `_wp_page_template`. `chon_url.py` của skill `wp-ucss` chọn một URL mỗi file gộp, cộng trang tiền, bài core và outer nhiều click, và mọi bài của chuyên mục ưu tiên. Người duyệt site agency mẫu 26/10/2026: đo và tối ưu trên URL template đại diện và bài có keyword tốt, ưu tiên chuyên mục chiến lược, không đo toàn bộ URL.
   - Template có trang con dựng khác nhau (landing khoá học kèm trang thanh toán, trang cảm ơn) thì đo mọi trang con, kể cả trang `noindex`. Blog: đo 3–5 bài có ảnh đại diện khác định dạng (PNG, JPG, WebP, AVIF). Site mẫu 2: một URL đại diện cho mỗi template bỏ sót 3 trang thanh toán 37–68 điểm và ảnh PNG 944 KB của một bài.
3. Ghi `urls.tsv` dạng `tên<TAB>url` vào thư mục evidence.
4. Chỉ gom HTML bằng EmbeddingGemma khi DB không cho biết template, ví dụ site HTML tĩnh hoặc headless.

## Bước 2 — đo baseline

1. Làm nóng cache và đo PSI 3 lượt cho mỗi URL, mỗi thiết bị. Xem ước tính trước, rồi chạy nền:

   ```bash
   python3 -I "$WPS/scripts/psi_run.py" --urls <ev>/urls.tsv --out <ev>/psi-base --runs 3 --dry-run
   python3 -I "$WPS/scripts/psi_run.py" --urls <ev>/urls.tsv --out <ev>/psi-base --runs 3 --detach
   cat <ev>/psi-base/PSI_STATE.txt
   python3 -I "$WPS/scripts/psi_table.py" <ev>/psi-base
   ```

   - Script chạy 2 lượt đồng thời (`--jobs 2`), xếp xen kẽ URL và thiết bị.
   - Script từ chối chạy tiền cảnh khi ước tính trên 8 phút (mã 5). Runtime có chế độ chạy nền báo khi xong thì chạy ở chế độ đó với `--fg-ok`. Không có thì dùng `--detach` và đọc `PSI_STATE.txt` sau thời gian ước tính. Không viết vòng chờ `sleep`.
2. Staging có Basic Auth: đo bằng `perf_probe.mjs`. Đo cả production bằng cùng script để so cùng điều kiện. So bằng `probe_table.py --detail`. Mọi lệnh `perf_probe.mjs` và `shot.mjs` truyền `--expect '<chuỗi trong title>'`. Script thoát mã 4 khi đo nhầm đích (`do-dac.md` mục 4).
3. Trước mỗi lượt thử trên staging, so theme và mu-plugins của staging với production: kéo bản production về thư mục tạm, chạy `diff -rq`, in ngày sửa của từng file lệch. Lệch thì đồng bộ có backup bằng `wp-staging-deploy`, giữ file chỉ dành cho staging. Sau khi ghi production, đồng bộ ngược về staging.
4. Chụp baseline chức năng: `node "$WPS/scripts/shot.mjs" --urls <ev>/urls.tsv --out <ev>/shot-base --label base --expect '<chuỗi trong title>'`.
5. Nếu lớp font nằm trong phạm vi, chạy `fontmap.mjs` trên 2–3 URL.
6. FCP observed dồn quanh một mốc ở mọi template, trong khi main thread rảnh: kiểm script nạp font trước (`checklist-theo-lop.md` lớp 4). Site bật Guest Mode và trang chưa có critical CSS: đọc `references/fcp-guest-mode.md`.
7. URL đo PSI là URL sạch, hoặc có tham số nằm trong `cache-exc_qs`. Không dùng `utm_*`, `fbclid`, `gclid` (`do-dac.md` mục 2). Sau đợt đo, chạy `python3 -I "$WPS/scripts/cache_variants.py" <url sạch> ...` để kiểm robots và canonical ở 5 biến thể cache.
8. Ghi `<ev>/BASELINE.md`: mỗi mốc một dòng gồm ngày giờ, công cụ, lệnh, thư mục kết quả, trung vị mobile và desktop (`do-dac.md` mục 7).

## Bước 3 — chẩn đoán và lập plan

0. Đọc field trước lab: `loadingExperience` (URL) và `originLoadingExperience` (origin) trong JSON PSI. Field p75 đạt (LCP ≤ 2,5 s, CLS ≤ 0,1, INP ≤ 200 ms) thì không mở vòng sửa riêng chỉ để đuổi CLS hoặc LCP lab. Ghi vào plan: lợi ích chỉ là điểm lab, chi phí ước tính. Chỉ làm khi người duyệt chọn tối đa điểm lab. Lỗi đã gặp 22/10/2026: một lane đuổi CLS lab 118 phút ở trang có field đã đạt.
1. Đọc `psi_table.py --detail` của từng template: phần tử LCP, 4 pha LCP, tài nguyên chặn hiển thị, byte theo loại, bên thứ ba. Với staging, đọc `probe_table.py --detail`: phần tử LCP và nguồn layout shift. Lập bảng chi phí theo nguyên nhân: `python3 -I "$WPS/scripts/psi_con_tru.py" <ev>/psi-base --mt`.
2. Xếp nguyên nhân vào 7 lớp của `references/checklist-theo-lop.md`. Tách nguyên nhân chung với nguyên nhân riêng của template. Rà đủ câu hỏi của lớp 5b (chi phí render của theme), kể cả khi điểm đã cao.
3. Phân loại script bằng Jev `asset-delay` nếu cần cấu hình delay JS.
4. Trình plan theo CLAUDE.md §0: việc, tác động ước tính, rủi ro, rollback. Đánh dấu việc có thể thay plugin bằng code tự viết. Việc thử trên production ghi thêm ngưỡng trả về đặt trước (Bước 4).
5. Plan có lớp 7: chạy `gtm_inventory.py`, rồi trình bảng đánh đổi ở `checklist-theo-lop.md` lớp 7.
6. CLS từ 0,1 mà PSI ghi nguyên nhân là "Phông chữ web": Lighthouse chỉ gán theo thời điểm font tải. Kiểm 2 nguyên nhân khác trước khi sửa font:
   - JS đổi bố cục sau lần vẽ đầu theo dữ liệu (sessionStorage, query). Đo từng nhánh bằng `node "$WPS/scripts/cls_trace.mjs" --url <trang> --session '<json>'`, xem toạ độ trước và sau (lớp 6).
   - Stack `font-family` riêng của trang rơi thẳng xuống `system-ui`, không có face dự phòng. Mac đo CLS nhỏ, máy Linux của PSI đo lớn (lớp 4).
   - Lab trên máy không tái hiện CLS của PSI: làm theo `references/cls-chi-psi-thay.md` trước khi viết bản sửa.
7. CrUX TTFB p75 trên 0,8 s: chạy nhánh chỉ đọc ở `references/ttfb-cache-trang.md`.
8. File CSS gộp từ 100 KB brotli, hoặc critical CSS kèm file gộp làm TBT tăng: dùng skill `wp-ucss` (CSS gọn theo trang, kiểm computed style trước khi đổi link). Site đã có CSS gọn: mọi thay đổi có purge phải so md5 file gộp ở cả 4 biến thể `m`, `d`, `p`, `q` trước và sau, không chỉ `m`, `d`. Bản `Accept: */*` có thể dựng lại bằng file gộp khác mà map chưa có (site mẫu 27/10/2026); khi đó chạy job tái tạo của `wp-ucss`.
9. KPI crawl hoặc thời gian phản hồi Googlebot nằm trong phạm vi: 404 của bot dò quét dựng qua PHP thì đọc `references/ttfb-cache-trang.md` mục 4b.
10. Site có CDN (skill `cdn-speed-setup`):
   - Biết PSI đi đường nào trước khi kết luận. Site VN ngày 26/10/2026 chia vùng: PSI chạy từ châu Á, đi thẳng origin, không qua CDN. Điểm PSI và LCP lab không đổi sau khi bật CDN.
   - CrUX là cửa sổ 28 ngày. Field data chỉ phản ánh CDN khoảng 28 ngày sau ngày đổi.
   - Đo TTFB theo vùng bằng `geo_verify.py` của `cdn-speed-setup`. Không dùng PSI để chứng minh CDN giảm TTFB cho khách nước ngoài.
   - CDN có thể không tách HTML theo `Accept`. Thay đổi HTML theo biến thể WebP phải áp cả cho bản `Accept: */*`, rồi purge CDN theo URL và làm nóng ngay (`checklist-theo-lop.md` lớp 1).
11. Trước khi đề xuất critical CSS, face font dự phòng, preload font ưu tiên thấp, tách script inline hay beacon RUM: đọc bảng "Đã A/B và không áp" cuối `checklist-theo-lop.md`. Ghi số của bảng vào plan.
12. Site bật Guest Mode và khách mới tải trang 2 lần (gọi `guest.vary.php` rồi reload): đọc mục "Khách mới bị tải lại trang" ở `references/fcp-guest-mode.md`. Cách sửa có mẫu `templates/guest-tap.php` cho lần chạm menu đầu.

### Tự phản biện trước khi trình

Chấm plan theo checklist dưới. Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của agent khác cho cùng site, so từng mục trước khi trình.

Bản tốt nhất phải có:
- [ ] Đo mọi trang con của template (thanh toán, cảm ơn) và 3–5 bài blog khác định dạng ảnh. Nguồn lỗi: site mẫu 2, 18/10/2026, người duyệt tự đo thấy trang thanh toán 37–68 điểm.
- [ ] Đã đọc field CrUX trước khi đề xuất đuổi chỉ số lab. Nguồn lỗi: lane CLS lab 118 phút, 22/10/2026.
- [ ] Đã rà lớp 5b và đủ 5 hạng mục PSI. Mỗi phần còn trừ điểm có lý do giữ. Nguồn lỗi: nghiệm thu ở 85 điểm, người duyệt phản hồi 3 lượt, 18/10/2026.
- [ ] Mỗi việc ghi production có backup, lệnh rollback về `v0`, ngưỡng trả về đặt trước và kết quả staging. Nguồn lỗi: lane chạy production 4 giờ dù staging đã cho kết quả xấu, 23/10/2026.
- [ ] Config cấp site có lượt A/B trên 4 URL mẫu trước khi áp toàn site. Nguồn lỗi: một lane đo khoảng 80 lượt PSI cho một URL rồi vẫn không áp, 23/10/2026.
- [ ] Việc lớp 7 tách riêng, có bảng "hoãn GTM có mất gì" và giữ tái phát click link. Nguồn lỗi: mất click Zalo đầu tiên khi hoãn GTM, 22/10/2026.
- [ ] Site sắp deploy lại thì plan chỉ có đo mốc và checklist cho bản mới. Nguồn lỗi: tối ưu site sắp đổi bản, bị huỷ sau 25 phút, 16/10/2026.
- [ ] Trước khi kết luận "phải trả phí" hay "không làm được", đã xét phương án tự build và mã nguồn mở. Nguồn lỗi: site agency mẫu 26/10/2026, người duyệt nhắc 2 lần (12:07, 22:26); cả 2 lần phương án sau tốt hơn (CDN chia vùng, CSS gọn tự build).

## Bước 4 — sửa theo lớp

Mỗi đợt sửa một lớp, theo vòng sau:

1. Backup trạng thái sẽ đổi: option, file, meta. Ghi lệnh rollback trước khi sửa. Backup theo phiên bản (`v0` gốc, `v1`, `v2`…). Lệnh rollback trỏ về `v0`. File mới thêm (mu-plugin, ảnh) trả lại bằng cách chuyển vào quarantine. Sau vòng sửa, thử lệnh rollback ở chế độ DRY hoặc trên staging.
   - Thử trên production: ghi ngưỡng trả về vào plan trước khi chạy. Ngưỡng gồm chỉ số, mức chênh (mặc định của `psi_decide.py`), số lượt tối đa và thời gian tối đa. Chạm một ngưỡng thì dừng và rollback.
   - Staging đã cho nhãn "xấu hơn" hoặc "không đổi" thì không chạy bản đó trên production. Ngoại lệ: thay đổi phụ thuộc thứ staging không có (Guest Mode, page cache). Ghi lý do ngoại lệ vào plan.
2. Sửa. Chép file theme lẻ bằng `"$WPS/scripts/deploy_theme_files.sh"` (biến môi trường ghi ở đầu script). Gói sửa nhiều file theme hoặc mu-plugin làm trên staging thì lên production bằng gộp 3 phía của `wp-staging-deploy`. Đổi ảnh đại diện PNG/JPG nặng sang WebP bằng `"$WPS/scripts/featured_webp.sh"`. Purge cache một lần sau cả đợt, theo thứ tự:
   - Xoá object cache trước (nếu site bật Redis hoặc Memcached), rồi purge theo URL.
   - Làm nóng đúng các path vừa purge: `bash "$WPS/scripts/lam_nong.sh" --host https://<domain> <path> ... -W both`. Script làm nóng 4 bản cache bằng header Chrome thật và bản plain cho bot (`checklist-theo-lop.md` lớp 1).
   - Chạy `cache_variants.py` trên URL vừa purge.
3. Đo template bị ảnh hưởng bằng `perf_probe.mjs` 3 lượt, so với baseline bằng `probe_table.py`. Không chạy lại PSI toàn bộ URL.
4. Chụp lại và so: `python3 "$WPS/scripts/shot_cmp.py" <ev>/shot-base base <ev>/shot-<đợt> <đợt>`.
5. Giữ thay đổi khi chỉ số tốt hơn và `shot_cmp` không báo lỗi chức năng mới. Nếu không đạt, rollback ngay và ghi lý do.

Critical CSS phải A/B từng template trước khi giữ. Config cấp site (option LiteSpeed, font, mu-plugin dùng chung) phải A/B trên 4 URL mẫu thuộc 4 template trước khi áp toàn site (`do-dac.md` mục 3). Lớp 7 (tracking, bên thứ ba) chỉ làm khi người duyệt đã đồng ý riêng.

Hiện tượng chỉ PSI thấy, `perf_probe.mjs` không tái hiện: A/B trên PSI theo `do-dac.md` mục 3. `psi_ab.py build` tự gắn `noindex` và canonical tự trỏ vào mọi bản tĩnh. `upload` và `quarantine` chỉ chạy thật khi có `--apply`. Quyết định bằng `psi_decide.py`, dừng đo khi có nhãn.

Đổi font: làm đủ 4 bước "đổi font hoặc cỡ chữ toàn site" ở lớp 4, so hiển thị bằng `font_same.mjs` trước khi lên production.

Hoãn GTM đã được duyệt: cài `"$WPS/templates/gtm-delay-loader.php"`. Mẫu từ v1.12 tái phát `gtm.linkClick` cho click link đến trước khi `gtm.js` chạy. Kiểm bằng `"$WPS/scripts/gtm_delay_check.mjs"` và `ls_exclusions_check.py`, rồi kiểm event thật theo lớp 7.

## Bước 5 — nghiệm thu

1. Chạy PSI 3 lượt cho mọi URL ở `urls.tsv`. Mặc định thêm một lượt đủ 5 hạng mục cho mọi URL, cả 2 thiết bị:

   ```bash
   python3 -I "$WPS/scripts/psi_run.py" --urls <ev>/urls.tsv --out <ev>/psi-final --runs 3 --detach
   python3 -I "$WPS/scripts/psi_run.py" --urls <ev>/urls.tsv --out <ev>/psi-final-5hm --runs 1 --categories performance,accessibility,best-practices,seo,agentic-browsing --detach
   ```

   Chạy lệnh thứ hai khi `psi-final/PSI_STATE.txt` đã ghi `DONE`. Hai lệnh chạy cùng lúc sẽ gửi 4 request đồng thời lên site.

2. So baseline và kết quả: `psi_table.py <ev>/psi-base <ev>/psi-final`.
3. Lập bảng "Phần còn trừ điểm": `python3 -I "$WPS/scripts/psi_con_tru.py" <ev>/psi-final <ev>/psi-final-5hm --urls <ev>/urls.tsv --mt`. Dòng cuối `CON_TRU ... thieu_hang_muc=0` mới đủ để nghiệm thu. Điền lý do chưa sửa cho từng dòng.
4. Chạy `shot.mjs` lần cuối và `shot_cmp.py` với baseline. Mỗi dòng `!!` phải có giải thích.
5. Ghi CrUX hiện tại. Hẹn ngày xem lại field data, khoảng 28 ngày sau thay đổi.

## Bước 6 — báo cáo

- File `<CLIENT>_pagespeed-theo-template_v<N>.md` trong thư mục evidence. Cấu trúc: kết luận, template và URL, số liệu trước và sau, điểm 5 hạng mục, bảng "Phần còn trừ điểm" (template, audit dưới 0,9, lý do chưa sửa), nguyên nhân chung, nguyên nhân riêng, plan, thay đổi đã làm kèm rollback, cách đo lại, lỗi sẵn có, việc không làm, chi phí Jev.
- Báo cáo nghiệm thu sau đổi theme hoặc nhiều đợt sửa: bảng điểm có một cột cho mỗi mốc đo, ghi rõ cột nào 1 lượt, cột nào trung vị 3 lượt. Có URL đối chứng. Ghi trạng thái từng mục checklist của báo cáo trước, kèm bằng chứng.
- Cập nhật `HANDOFF.md` của đợt sau mỗi lớp. Thêm dòng bảng D `index.md`, append `log.md`.
- Không cam kết điểm PSI. Ghi rõ số lab với số field.

## Gate

- [ ] Mỗi số so sánh là trung vị của ít nhất 3 lượt.
- [ ] Staging được so với production bằng cùng script và cùng điều kiện.
- [ ] Mỗi thay đổi có backup, lệnh rollback, số đo trước và sau, kết quả `shot_cmp`.
- [ ] Lệnh rollback trả về bản gốc `v0`, không về bản trung gian, và đã thử sau vòng sửa cuối. Lỗi đã gặp: lane ảnh LCP gtvseo.com 24/10, `rollback.md` cài lại mu-plugin v1 thay vì tắt.
- [ ] Critical CSS chỉ giữ ở template đã A/B và đo tốt hơn.
- [ ] Không đổi cách nạp GTM, Pixel, Hotjar, chat khi chưa được duyệt.
- [ ] Không in key, mật khẩu Basic Auth, slug đăng nhập ra chat hay file ngoài `.agent-secrets`.
- [ ] Báo cáo có tổng chi phí Jev và danh sách nhãn Claude đã tự xếp lại.
- [ ] Sau mỗi đợt PSI, purge hoặc làm nóng, `cache_variants.py` đạt trên URL sạch: robots và canonical giống nhau ở 5 biến thể.
- [ ] Khi nhiều phiên hoặc agent cùng sửa một site: việc phụ thuộc kết quả của bước khác chỉ ghi production sau khi người kiểm độc lập của bước đó báo đạt. Lỗi đã gặp: object cache bật trên production 3 phút trước khi lượt kiểm staging xong.
- [ ] Mọi lượt `perf_probe.mjs`, `shot.mjs`, `lh_local.mjs` có `--expect` và dòng `GUARD` đạt. Số đo của lượt thoát mã 4 không vào báo cáo.
- [ ] Bản HTML tĩnh A/B trên production đạt `psi_ab.py verify` (noindex, canonical tự trỏ) trước khi upload, và trả 404 hoặc 410 sau quarantine. Lỗi đã gặp 22/10: 6 bản tĩnh để index khoảng 30 phút.
- [ ] Mỗi quyết định A/B có ngưỡng ghi trước khi đo và nhãn của `psi_decide.py`. Thử trên production có ngưỡng trả về trong plan.
- [ ] Báo cáo nghiệm thu có điểm 5 hạng mục cho mọi URL, cả 2 thiết bị (`psi_con_tru.py` báo `thieu_hang_muc=0`), và bảng "Phần còn trừ điểm" có lý do cho từng dòng.

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Jev | Phân loại script cho delay JS (`asset-delay`), soát ảnh chụp (`ui-visual`) | Dùng theo ngưỡng ở `references/phoi-hop-model.md` |
| EmbeddingGemma 2 | Gom URL theo template, gom vấn đề lặp trên 30 URL | Chỉ khi DB không cho biết template |
| Script | Trung vị PSI, quyết định A/B (`psi_decide.py`), bảng còn trừ điểm, ảnh LCP, thư viện trùng | Không dùng model. Script chính xác hơn và không tốn tiền |
| Claude | Chẩn đoán theo lớp, viết plan, đọc mục dưới ngưỡng, viết bản sửa | Dùng. Mọi thay đổi trên server cần plan đã duyệt |

## Anti-patterns

- Kết luận từ một lượt PSI hoặc từ điểm tổng mà không xem chỉ số observed.
- Đổi `sizes` khi chưa đo bề rộng hiển thị ở 360–1920 px, hoặc khi CSS không đặt kích thước cho ảnh (lớp 3).
- Nạp CSS gộp bằng `rel="preload"` sau critical CSS. Dùng `media="print"` và `onload`.
- Để model tự quyết thay đổi trên server. Model chỉ gán nhãn và so khớp.
- Gọi `document.fonts.load()` hoặc preload font trong `<head>` trước frame đầu.
- A/B trên PSI bằng nhiều lượt liên tiếp của cùng một URL.
- Purge bằng `litespeed_purge_post` hoặc bước purge của một gói có sẵn khi chưa đọc option `litespeed.conf.purge-post_all`. Nếu option bằng 1, purge một bài sẽ purge toàn site và mọi trang mất cache. Purge theo URL.
- Đo PSI hay làm nóng bằng URL có `utm_*`, `fbclid`, `gclid`. LiteSpeed bỏ các tham số này khỏi khoá cache, nên bản `noindex` của URL có query vào cache của URL sạch.
- Làm nóng bằng curl mặc định (`Accept: */*`). Lượt này chỉ làm nóng bản plain cho bot. Khách thật vào bản webp và vẫn miss.
- Restart graceful OpenLiteSpeed rồi coi cấu hình lsphp mới đã chạy. Tiến trình mẹ lsphp cũ vẫn giữ socket tới khi bị TERM lúc rảnh.
- Ghi SQL thô khi site bật object cache mà không xoá key. Trang hiện dữ liệu cũ tới khi flush.
- Chạy nhiều tiến trình WP-CLI nặng cùng lúc trên VPS ít RAM. Kernel OOM giết WP-CLI hoặc mysqld.
- Dùng `font-display: optional` cho font thân bài mà chưa A/B trên PSI mobile. Lantern coi font `optional` là chặn vẽ chữ.
- A/B trên PSI bằng công tắc tham số trong mu-plugin đang chạy production (ví dụ `?ab=` đổi CSS). Cách này sửa code production chỉ để đo. Nếu tham số nằm trong `cache-drop_qs`, bản thử ghi đè cache của URL sạch. Dùng `psi_ab.py` với HTML tĩnh (`do-dac.md` mục 3).
- Kết luận từ hai nhóm lượt PSI đo khác giờ mà không xem `benchmarkIndex` (`do-dac.md` mục 2).
- Chạy `psi_run.py` tiền cảnh khi ước tính trên 8 phút, hoặc chờ bằng vòng `sleep`. Dùng chạy nền có báo xong hoặc `--detach`.
- Gọi PSI cùng URL + thiết bị liên tiếp mà không cách lượt. PSI trả lại kết quả đã lưu: 3 file cùng `fetchTime`, lượt 2 và 3 mất khoảng 1 giây (site agency mẫu 27/10/2026). `psi_run.py` từ 1.13.1 chạy cặp đó lần lượt, cách `--min-gap` (mặc định 60 giây), và đo lại lượt trùng `fetchTime`. Số "trung vị 3 lượt" từ script khác: kiểm `fetchTime` trước khi tin.
- Chép script của skill vào thư mục lane rồi sửa. Gọi bản `"$WPS/scripts/…"`.
- Deploy bản sửa CLS khi lab chưa tái hiện được nguyên nhân (`references/cls-chi-psi-thay.md`).
- Đo A/B thêm vòng sau khi `psi_decide.py` đã có nhãn, hoặc đổi ngưỡng sau khi thấy số.

## Changelog

- v1.14 (2026-10-27): `fcp-guest-mode.md` thêm mục khách mới bị tải lại trang: rewrite `guest.vary.php` sang file `[]` trừ UA làm nóng, mẫu `templates/guest-tap.php` bấm lại lần chạm menu đầu, QA và kiểm sau áp. Đã chạy production site agency mẫu 26/10 (CS-26): mỗi URL tải 1 lần thay vì 2, 5xx 0. Test Chrome `test_guest_tap.py` 5 ca, bắt được bản bỏ bước bấm lại. `checklist-theo-lop.md` thêm bảng "Đã A/B và không áp" (critical CSS khi CSS gộp lớn, face dự phòng, font ưu tiên thấp, tách script inline, beacon RUM). Bước 3 mục 11–12. Checklist tự phản biện thêm mục phương án tự build. Eval thêm 4 ca.
- v1.13.2 (2026-10-27): Bước 3 mục 8: site có CSS gọn thì so md5 file gộp ở cả 4 biến thể khi purge (QA cuối đêm site mẫu: lane chỉ so `m`, `d`, bản `p`, `q` của 2 bài đổi sang file gộp ngoài map).
- v1.13.1 (2026-10-27): `psi_run.py` thêm `--min-gap` (60 giây giữa hai lượt cùng URL + thiết bị, không chạy đồng thời cùng cặp) và bỏ lượt trùng `fetchTime` rồi đo lại. Nguồn: kiểm độc lập lane config 27/10 03:2x, "PSI 3 lượt" thật ra là 1 lượt. Test mới: `test_cached_result_is_retried_not_saved`, `test_min_gap_spaces_same_url`; 162 ca đạt.
- v1.13 (2026-10-27): rút từ đợt site agency mẫu 26–27/10. Bước 1 chọn URL theo md5 file gộp (`chon_url.py` của `wp-ucss`). Bước 3 trỏ sang skill mới `wp-ucss` và mục 404 dò quét. Lớp 1: Googlebot dùng chung bản cache `Accept: */*`, CDN không tách HTML theo Accept, purge Bunny không `exactPath`, `lam_nong.sh -V` khi chặn `guest.vary.php`. Lớp 5: CSS gọn trước critical CSS, bẫy TBT của file gộp lớn, bẫy `.screen-reader-text`. `ttfb-cache-trang.md` mục 4b: khối `.htaccess` trả 404 trước PHP (1,1–2,8 s còn 13–21 ms), `speculationrules`.
- v1.12.1 (2026-10-26): Bước 3 mục 8: site có CDN, PSI có thể đi thẳng origin (site VN chia vùng, PSI chạy từ châu Á), CrUX trễ 28 ngày, đo TTFB theo vùng bằng `cdn-speed-setup`. Nguồn: đợt CDN site VN 26/10/2026.
- v1.12 (2026-10-25): rút từ rà soát web 16–24/10 (perf-1 đến perf-8, hs-7, media-10, trk-1). Biến `WPS` cho đường dẫn script. Bước 0b đọc lộ trình site, parity staging bằng `diff -rq`, `BASELINE.md`. Script mới: `psi_decide.py`, `psi_cls_dump.py`, `lh_local.mjs`, `lam_nong.sh`, `ls_exclusions_check.py`, `psi_con_tru.py`, `fallback_faces.py`, `fa_subset/`, `img_variants.py`, `img_display_width.mjs`, `img_width_report.py`. `psi_run.py` chạy song song `--jobs 2`, từ chối tiền cảnh quá 8 phút, `--detach`. `perf_probe.mjs`, `shot.mjs` có guard `--expect`. `psi_ab.py` tự gắn noindex, khoá ngưỡng, `--split-bench`, `--apply`. Mẫu loader GTM tái phát `gtm.linkClick`. Bước 3 đọc field trước lab, checklist tự phản biện. Bước 5 mặc định 5 hạng mục và bảng "Phần còn trừ điểm". Reference mới `cls-chi-psi-thay.md`, `fcp-guest-mode.md`, `ttfb-cache-trang.md`. Lớp 5b chi phí render của theme. Test offline 160 ca, chạy thật chỉ đọc `psi_con_tru.py` trên JSON PSI cũ của site mẫu 2. Chưa làm kho psi-cache chung của hs-7.

- v1.11 (2026-10-24): rút từ lane tối gtvseo.com 23–24/10. Bước 4 và Gate: backup theo phiên bản, rollback về `v0`, thử rollback sau vòng sửa. `do-dac.md` mục 2: tách lượt theo `benchmarkIndex`, đối chứng cùng khung giờ (bản A 94,5 so với bản C 88,5 do máy PSI). Mục 3: cấm công tắc tham số trong mu-plugin production. `checklist-theo-lop.md` lớp 2: bản sao hero cho desktop làm mobile tải 2 file. Lớp 4: preload font `/website/` làm FCP lab chậm 0,4–0,7 s. Nguồn: `Deliverables/GTV-Brand/GTV-Website/perf-20261020/toi-2310/lcp-anh/kiem-doc-lap.md`, `toi-2310/font/kiem-doc-lap.md`, `ui-20261020/doc-de-2310/sua/kiem-doc-lap.md`.
- v1.10 (2026-10-21): rút từ đợt gtvseo.com 20–21/10. Script mới `cache_variants.py`: robots, canonical, nhãn cache ở 5 biến thể của URL sạch. Chạy thật chỉ đọc trên 2 URL production: 10/10 `hit`, index, canonical tự trỏ. Server giả bắt đúng ca `noindex` chỉ ở bản plain và bot. `psi_run.py` từ chối URL có `utm_*`, `fbclid`, `gclid`, `_ga`. `shot.mjs` không bật cờ `mobile` của CDP và ghi `vw`; `shot_cmp.py` so `scrollWidth` với `vw` (fixture 390 px: bản cũ không báo tràn, bản mới báo `390→420`). Chụp lại baseline bằng bản mới trước khi so. `checklist-theo-lop.md` lớp 1: 8 biến thể cache, làm nóng bằng `Accept` có `image/webp` và bản plain cho bot, số liệu `purge-post_all`, object cache Redis, restart graceful không thay mẹ lsphp, OOM và RAM. Lớp 4: kết quả `font-display: optional` trên production (CLS desktop tốt, mobile tụt, đã rollback), LiteSpeed `optm-css_font_display` ép `swap`. `do-dac.md` mục 2: luật URL đo PSI. Gate thêm kiểm 5 biến thể và thứ tự kiểm độc lập.
- v1.9.1 (2026-10-19): Bước 4 trỏ sang `wp-staging-deploy` cho gói sửa nhiều file.
- v1.9 (2026-10-19): Anti-patterns thêm bẫy `purge-post_all=1`. `do-dac.md`: staging không có cache LiteSpeed nên không đo được thay đổi FCP do Guest Mode. Lớp 7: ảnh xám YouTube trả 404 nhưng vẫn chạy `onload`, kiểm `naturalWidth`. Rút từ đợt gtvseo.com 19/10.
- v1.8 (2026-10-19): lớp 5 thêm 2 bẫy critical CSS (LiteSpeed gom `<style>` có `@font-face` vào file async, dựng lại critical CSS sau khi đổi font). Lớp 6 thêm mục lục Fixed TOC chờ JS và cách thử CSS sửa CLS bằng CDP `Fetch`. Đã chạy thật trên production site mẫu: CLS desktop bài viết 0,53 → 0, trung vị 6 template lỗi CLS mobile 86,5 → 90,5, desktop 96,5 → 98,5.
- v1.7 (2026-10-18): `psi_ab.py build` gộp trang của nhiều spec vào `spec.json`. `do-dac.md` mục 3: đọc CLS từ JSON khi A/B, kiểm tính năng máy PSI bằng `console.error`. `checklist-theo-lop.md` lớp 4: kết quả A/B font trên PSI (tên `local()` bold khớp, chia face theo độ đậm không giảm CLS, preload đổi CLS lấy LCP, `font-display: optional`), bỏ câu "chưa có A/B" về preload. Lớp 7: ảnh thumbnail YouTube dùng bản WebP.
- v1.6 (2026-10-18): thêm từ đợt tối đa điểm trang khoá học và blog của site mẫu 2. Bước 1: đo mọi trang con của template, kể cả trang thanh toán `noindex`. Bước 3: CLS mà PSI gán cho font cần kiểm JS đổi bố cục và stack font trước. Lớp 3: bản 720w cho hero, logo dải chạy ngang, `sizes` ảnh thân bài theo cột chữ, ảnh đại diện PNG sang attachment WebP mà giữ ảnh OG. Lớp 4: stack font riêng của landing thiếu face dự phòng (Mac 0,03, PSI 0,28). Lớp 6: quyết định trạng thái trang trong `<head>` (CLS 0,92 → 0,03), forced reflow bằng `ResizeObserver`. Lớp 7: TBT trang chuyển đổi đến hoàn toàn từ tracking. Script mới: `cls_trace.mjs`, `featured_webp.sh`, `psi_ab.py`, `gtm_delay_check.mjs`; mẫu `templates/gtm-delay-loader.php`. Đã chạy thật trên production: 3 trang thanh toán mobile từ 37–68 lên 81–94 điểm, ảnh hero bài blog 944 KB PNG còn 48,6 KB WebP.

- v1.5 (2026-10-18): thêm từ đợt tối đa điểm PSI của site mẫu 2. Lớp 7: hoãn GTM 2 s không có tác dụng (12/12 lượt vẫn tính TBT), cách chọn mốc hẹn giờ theo lúc Lighthouse dừng ghi trace (site mẫu 2 chọn 5 s, TBT = 0), nạp ngay cho URL quảng cáo và trang chuyển đổi, bẫy `cdp.mjs` tự cuộn. File mới `references/agentic-browsing.md`: cách tính phân số, điều kiện đạt của từng audit, `llms.txt` tĩnh có charset, axe với `content-visibility`, màu đủ tương phản. `psi_run.py` thêm `--categories`. Đã chạy thật: 11/11 template đạt Accessibility, Best Practices, SEO 100 và Agentic 3/3.
- v1.4 (2026-10-18): thêm từ lượt nghiệm thu đợt 2 của site mẫu 2. `do-dac.md`: lượt chậm có thể dồn cả 3 lượt vào một URL nên phải đo lại trước khi kết luận lùi, so trước và sau trong cùng buổi, mỗi cột báo cáo một công cụ, grep key trong evidence. Script mới `deploy_theme_files.sh` (chép file theme lẻ có backup, lint, owner, purge), đã chạy thật trên staging site mẫu 2: file 644 `www:www`, trang 200. `tool-call-thua.md` thêm 2 dòng.
- v1.3 (2026-10-18): thêm từ đợt tốc độ thứ hai của site mẫu 2 (`references/checklist-theo-lop.md`). Lớp 1: cache trình duyệt 1 năm và luật đổi tên ảnh. Lớp 3: bản 640w cho ảnh màn hình đầu, bẫy lightbox đọc `currentSrc`. Lớp 4: `local()` nào khớp trên máy PSI (Arial có khớp), họ dự phòng Roboto cho Android, CLS do chữ đổi dòng, thứ tự `unicode-range` vi sau latin-ext. Lớp 5: `content-visibility` cho trang dài, chiều cao ước tính đo thật, tắt khi nhảy `#mục`. Lớp 6: forced reflow của thanh tiến độ cuộn, vá JS dùng chung ở bước build.
- v1.2 (2026-10-18): thêm bài học từ đợt nghiệm thu site thứ hai sau khi đổi theme. Lớp 4: bỏ luật preload font, thêm bẫy `document.fonts.load()` trong `<head>`, bẫy font dự phòng `local('Arial')` trên PSI, quy trình tự host Google Fonts. Lớp 7: bảng đánh đổi khi hoãn GTM. `do-dac.md`: mục 3 A/B trên PSI, cách đọc LCP mô phỏng có GTM, lượt chậm ngẫu nhiên. Script mới: `gfonts_selfhost.py`, `font_same.mjs`, `gtm_inventory.py`, đã chạy thử trên production site thứ hai (file font tải về trùng từng byte với bản đang chạy).
- v1.1 (2026-10-17): chuyển bản gốc vào SEO Production, viết lại cho mọi site WordPress có quyền server. Thêm hồ sơ server `00-client-context/wp-server.md`, evidence mặc định `03-audits/technical/`, bộ model `tools/ai-assist/`, nhánh không có quyền server.
- v1.0 (2026-10-17): tạo mới từ đợt tối ưu 16–17/10. Chạy thử chỉ đọc trên một site production và staging của nó: PSI 36 lượt không lỗi, mô phỏng 72 lượt, `shot_cmp` 2 lượt staging lệch 0,0%. Sửa sau lượt thử: thêm `probe_table.py`, KB tiết kiệm của audit insight, nhận theme cha + con, cờ boolean của script, bẫy Guest Mode.
