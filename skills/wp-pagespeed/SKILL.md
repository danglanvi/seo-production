---
name: wp-pagespeed
description: "Đo và tối ưu PageSpeed site WordPress theo template khi có quyền vào server: PSI trung vị 3 lượt, mô phỏng Chrome cho staging, sửa theo 7 lớp có A/B và rollback, phối hợp Jev + EmbeddingGemma. Dùng khi tăng điểm PageSpeed, Core Web Vitals hoặc so staging với production."
metadata:
  version: "1.20"
---

# wp-pagespeed — tối ưu PageSpeed WordPress theo template

Quy trình đã chạy thật trên 2 site WordPress (VPS, OpenLiteSpeed, LiteSpeed Cache) ngày 16–18/10/2026. Site thứ nhất có 13 template: điểm PSI trung vị tăng từ 63 lên 76 (mobile) và từ 87 lên 98 (desktop). Site thứ hai so staging với production trước khi đổi theme, rồi nghiệm thu sau khi đổi: trung vị mobile 11 template tăng từ 66 lên 88. Site bán lẻ thứ ba (WooCommerce, shared hosting) 29–30/10/2026: một lô sửa ở theme theo template đưa mobile trung bình 16 URL từ 56,4 lên 90,4. Trước đó, cả ngày A/B từng việc chỉ đưa điểm lên 57,2.

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
- `references/luot-lon.md`: đọc ở Bước 3–4. File này mô tả cách sửa mặc định: gom việc theo lô ở cấp template, kiểm không cần PSI, deploy rồi mới đo PSI.
- `references/phoi-hop-model.md`: đọc trước khi gọi Jev, EmbeddingGemma hoặc model khác.
- `references/agentic-browsing.md`: đọc khi cần tối đa hạng mục "Duyệt web bằng tác nhân", Accessibility, SEO của PSI.
- `references/cls-chi-psi-thay.md`: đọc khi PSI báo CLS mà lab trên máy không tái hiện.
- `references/fcp-guest-mode.md`: đọc khi FCP mobile dồn một mốc ở site bật LiteSpeed Guest Mode.
- `references/ttfb-cache-trang.md`: đọc khi CrUX TTFB p75 trên 0,8 s hoặc lượt đầu của khách thường miss cache.
- `references/plugin-chong-cheo.md`: đọc ở Bước 3 khi site bật từ 2 plugin tối ưu trở lên (LiteSpeed, Perfmatters, plugin của host, Cloudflare APO), dùng theme đa năng có WooCommerce, hoặc GSC báo lỗi INP.

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
- `lh_local.mjs` dùng module Lighthouse trong cache npx. Thiếu module thì script thoát mã 3. Nếu mục tiêu mobile từ 97, hoặc cần chẩn đoán CLS hay vẽ đầu muộn chỉ PSI thấy, cài module trước khi giao việc chẩn đoán (lệnh ở đầu `lh_local.mjs`). Lỗi đã gặp ở site agency mẫu 27/10/2026: lane chẩn đoán trang trắng tới 2,4 s dừng vì thiếu module, `perf_probe.mjs` không tái hiện. Các trường hợp khác: bỏ bước dựng lại môi trường PSI và ghi giới hạn.
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
11. Trước khi đề xuất critical CSS, face font dự phòng, preload font, nạp font sau FCP, `font-display: optional`, cắt trục font, gộp JS, `content-visibility`, preload ảnh nền, tắt gộp CSS, tách script inline hay beacon RUM: đọc bảng "Đã A/B và không áp" cuối `checklist-theo-lop.md`. Ghi số của bảng vào plan.
12. Site bật Guest Mode và khách mới tải trang 2 lần (gọi `guest.vary.php` rồi reload): đọc mục "Khách mới bị tải lại trang" ở `references/fcp-guest-mode.md`. Cách sửa có mẫu `templates/guest-tap.php` cho lần chạm menu đầu.
13. TBT cao: chạy `trace_fn.mjs` trên template đó trước khi đề xuất sửa JS (`checklist-theo-lop.md` lớp 6). Chỉ đưa file JS có lệnh gọi trong long task vào plan.
14. Lập plan theo lô (`references/luot-lon.md` mục 1–3). Sửa ở phần dùng chung và từng template, không chỉ URL mẫu. Xếp việc theo số KB cắt được trước LCP. Nếu mobile trung vị dưới 75 hoặc cách mục tiêu từ 15 điểm, xin quyền sửa theme hoặc child theme ngay trong plan. Việc đổi giao diện (UI gọn cho màn đầu) đi kèm mockup để người duyệt chọn.

### Tự phản biện trước khi trình

Chấm plan theo checklist dưới. Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của agent khác cho cùng site, so từng mục trước khi trình.

Bản tốt nhất phải có:
- [ ] Đo mọi trang con của template (thanh toán, cảm ơn) và 3–5 bài blog khác định dạng ảnh. Nguồn lỗi: site mẫu 2, 18/10/2026, người duyệt tự đo thấy trang thanh toán 37–68 điểm.
- [ ] Đã đọc field CrUX trước khi đề xuất đuổi chỉ số lab. Nguồn lỗi: lane CLS lab 118 phút, 22/10/2026.
- [ ] Đã rà lớp 5b và đủ 5 hạng mục PSI. Mỗi phần còn trừ điểm có lý do giữ. Nguồn lỗi: nghiệm thu ở 85 điểm, người duyệt phản hồi 3 lượt, 18/10/2026.
- [ ] Mỗi việc ghi production có backup, lệnh rollback về `v0`, ngưỡng trả về đặt trước và kết quả staging. Nguồn lỗi: lane chạy production 4 giờ dù staging đã cho kết quả xấu, 23/10/2026.
- [ ] Plan gom thay đổi thành lô theo template: sửa phần dùng chung và từng template ở theme, không chỉ URL mẫu. Mỗi lô chạy PSI một lần, sau khi purge và kiểm không cần PSI. A/B riêng chỉ dùng ở 4 trường hợp của `luot-lon.md` mục 1. Nguồn: site bán lẻ mẫu 29/10/2026, ban ngày A/B từng việc chỉ từ 56,4 lên 57,2, lô lớn đêm đó lên 90,4. Người duyệt nhắc 29/10 21:45, 22:31, 30/10 09:02, rồi chốt lúc 13:07 ("fix một bulk rồi mới chạy PSI test lại, hạn chế cái nào cũng a/b testing"). Lỗi cũ: một lane đo khoảng 80 lượt PSI cho một URL rồi vẫn không áp, 23/10/2026.
- [ ] Việc lớp 7 tách riêng, có bảng "hoãn GTM có mất gì" và giữ tái phát click link. Nguồn lỗi: mất click Zalo đầu tiên khi hoãn GTM, 22/10/2026.
- [ ] Site sắp deploy lại thì plan chỉ có đo mốc và checklist cho bản mới. Nguồn lỗi: tối ưu site sắp đổi bản, bị huỷ sau 25 phút, 16/10/2026.
- [ ] Trước khi kết luận "phải trả phí" hay "không làm được", đã xét phương án tự build và mã nguồn mở. Nguồn lỗi: site agency mẫu 26/10/2026, người duyệt nhắc 2 lần (12:07, 22:26); cả 2 lần phương án sau tốt hơn (CDN chia vùng, CSS gọn tự build).

## Bước 4 — sửa theo lô

Sửa theo lô (người duyệt chốt 30/10/2026 13:07, luật đầy đủ ở `references/luot-lon.md`). Một lô gồm mọi thay đổi đã duyệt có thể ghi cùng lúc, kể cả khi thuộc nhiều lớp. Mỗi lô đi theo vòng sau:

1. Backup trạng thái sẽ đổi: option, file, meta. Ghi lệnh rollback trước khi sửa. Backup theo phiên bản (`v0` gốc, `v1`, `v2`…). Lệnh rollback trỏ về `v0`. File mới thêm (mu-plugin, ảnh) trả lại bằng cách chuyển vào quarantine. Sau vòng sửa, thử lệnh rollback ở chế độ DRY hoặc trên staging.
   - Thử trên production: ghi ngưỡng trả về vào plan trước khi chạy. Ngưỡng gồm chỉ số, mức chênh (mặc định của `psi_decide.py`), số lượt tối đa và thời gian tối đa. Chạm một ngưỡng thì dừng và rollback.
   - Staging đã cho nhãn "xấu hơn" hoặc "không đổi" thì không chạy bản đó trên production. Ngoại lệ: thay đổi phụ thuộc thứ staging không có (Guest Mode, page cache). Ghi lý do ngoại lệ vào plan.
2. Sửa. Chép file theme lẻ bằng `"$WPS/scripts/deploy_theme_files.sh"` (biến môi trường ghi ở đầu script). Gói sửa nhiều file theme hoặc mu-plugin làm trên staging thì lên production bằng gộp 3 phía của `wp-staging-deploy`. Đổi ảnh đại diện PNG/JPG nặng sang WebP bằng `"$WPS/scripts/featured_webp.sh"`. Purge cache một lần sau cả đợt, theo thứ tự:
   - Xoá object cache trước (nếu site bật Redis hoặc Memcached), rồi purge theo URL.
   - Làm nóng đúng các path vừa purge: `bash "$WPS/scripts/lam_nong.sh" --host https://<domain> <path> ... -W both`. Script làm nóng 4 bản cache bằng header Chrome thật và bản plain cho bot (`checklist-theo-lop.md` lớp 1).
   - Chạy `cache_variants.py` trên URL vừa purge.
3. Kiểm cả lô không cần PSI theo `luot-lon.md` mục 5 (K-HTML, K-CHUC, K-TRACK, K-HINH). Đạt thì đo PSI bộ URL đại diện một lần. Lô nhỏ chỉ chạm vài template: đo các template đó bằng `perf_probe.mjs` 3 lượt, so với baseline bằng `probe_table.py`.
4. Chụp lại và so: `python3 "$WPS/scripts/shot_cmp.py" <ev>/shot-base base <ev>/shot-<đợt> <đợt>`.
5. Giữ lô khi chỉ số không xấu hơn và `shot_cmp` không báo lỗi chức năng mới. Lô làm điểm tụt: làm theo `luot-lon.md` mục 7 (chia lô làm đôi, trả lại một nửa, đo lại để tìm thay đổi gây tụt). Lỗi chức năng: rollback tầng gây lỗi ngay và ghi lý do.

Không A/B từng thay đổi. A/B PSI riêng chỉ dùng ở 4 trường hợp của `luot-lon.md` mục 1: đổi giao diện, tham số chọn theo số đo, thay đổi khó trả lại nhanh, lô đo xấu hơn.

Critical CSS và config cấp site (option LiteSpeed, font, mu-plugin dùng chung): kiểm chức năng và ảnh trên 4 URL mẫu thuộc 4 template trước khi áp toàn site, đo PSI cùng lô. Lớp 7 (tracking, bên thứ ba) chỉ làm khi người duyệt đã đồng ý riêng.

Hiện tượng chỉ PSI thấy, `perf_probe.mjs` không tái hiện: gỡ cùng lúc mọi nguyên nhân ứng viên trong lô kế rồi đo một lần (`luot-lon.md` mục 7). Nếu vẫn còn, A/B trên PSI theo `do-dac.md` mục 3. `psi_ab.py build` tự gắn `noindex` và canonical tự trỏ vào mọi bản tĩnh. `upload` và `quarantine` chỉ chạy thật khi có `--apply`. Ghi đủ ngưỡng, kể cả số lượt, bằng `psi_ab.py build --min-runs --max-runs --bench-gap`. Quyết định bằng `psi_decide.py <psi> --spec <thư mục psi_ab>`, dừng đo khi có nhãn. Thiếu `--spec`, script gộp mọi trang cùng tên biến thể trong thư mục PSI. Nguồn: site bán lẻ mẫu 29/10/2026, trang post của spec khác lọt vào nhãn chung của spec 4 trang (instance của site, `03-audits/technical/toi-uu-pagespeed/dot-2910/anh-lcp/bao-cao.md`).

Đổi font: làm đủ 4 bước "đổi font hoặc cỡ chữ toàn site" ở lớp 4, so hiển thị bằng `font_same.mjs` trước khi lên production.

Hoãn GTM đã được duyệt: làm theo skill `wp-gtm-tracking` (kiểm hit có chặn, chọn N giây, thứ tự áp, theo dõi 7 ngày). Site chèn snippet bằng option plugin dùng mẫu `gtm-delay-loader-option.php` của skill đó. Site chèn ở theme cài `"$WPS/templates/gtm-delay-loader.php"`. Mẫu từ v1.12 tái phát `gtm.linkClick` cho click link đến trước khi `gtm.js` chạy. Kiểm bằng `"$WPS/scripts/gtm_delay_check.mjs"` và `ls_exclusions_check.py`, rồi kiểm event thật theo lớp 7.

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
- [ ] Mỗi lô có backup, lệnh rollback cho từng tầng, số đo trước và sau lô, kết quả `shot_cmp` và kết quả bộ kiểm không cần PSI (`luot-lon.md` mục 5).
- [ ] Mọi lượt kiểm tracking chặn cả `www.google.com/g/collect` và `www.google.com/rmkt/collect`, và báo cáo ghi 0 hit lọt. Lỗi đã gặp 30/10/2026: khoảng 48 `page_view` GA4 và 26 hit remarketing tới Google thật.
- [ ] Lệnh rollback trả về bản gốc `v0`, không về bản trung gian, và đã thử sau vòng sửa cuối. Lỗi đã gặp: lane ảnh LCP site agency mẫu 24/10, `rollback.md` cài lại mu-plugin v1 thay vì tắt.
- [ ] Critical CSS chỉ giữ ở template mà lô chứa nó đo không xấu hơn.
- [ ] Không đổi cách nạp GTM, Pixel, Hotjar, chat khi chưa được duyệt.
- [ ] Không in key, mật khẩu Basic Auth, slug đăng nhập ra chat hay file ngoài `.agent-secrets`.
- [ ] Báo cáo có tổng chi phí Jev và danh sách nhãn Claude đã tự xếp lại.
- [ ] Sau mỗi đợt PSI, purge hoặc làm nóng, `cache_variants.py` đạt trên URL sạch: robots và canonical giống nhau ở 5 biến thể.
- [ ] Khi nhiều phiên hoặc agent cùng sửa một site: việc phụ thuộc kết quả của bước khác chỉ ghi production sau khi người kiểm độc lập của bước đó báo đạt. Lỗi đã gặp: object cache bật trên production 3 phút trước khi lượt kiểm staging xong.
- [ ] Mọi lượt `perf_probe.mjs`, `shot.mjs`, `lh_local.mjs`, `trace_fn.mjs` có `--expect` và dòng `GUARD` đạt. Số đo của lượt thoát mã 4 không vào báo cáo. Vòng lặp nhiều trang có `--expect` riêng từng trang, và path thật của mọi lượt đã đếm trước khi tính trung vị (`do-dac.md` mục 4). Lỗi đã gặp 27/10/2026: 75 lượt lab đo cùng một trang.
- [ ] Bản HTML tĩnh A/B trên production đạt `psi_ab.py verify` (noindex, canonical tự trỏ) trước khi upload, và trả 404 hoặc 410 sau quarantine. Lỗi đã gặp 22/10: 6 bản tĩnh để index khoảng 30 phút.
- [ ] Mỗi quyết định A/B có ngưỡng ghi trước khi đo và nhãn của `psi_decide.py`. Thử trên production có ngưỡng trả về trong plan. Thư mục PSI chứa trang của nhiều spec thì nhãn lấy bằng `--spec`, và dòng "Bỏ trang ngoài spec" khớp danh sách trang ngoài spec. Lỗi đã gặp 29/10/2026: trang post lọt vào nhãn chung của spec khác.
- [ ] Báo cáo nghiệm thu có điểm 5 hạng mục cho mọi URL, cả 2 thiết bị (`psi_con_tru.py` báo `thieu_hang_muc=0`), và bảng "Phần còn trừ điểm" có lý do cho từng dòng.

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Jev | Phân loại script cho delay JS (`asset-delay`), soát ảnh chụp (`ui-visual`) | Dùng theo ngưỡng ở `references/phoi-hop-model.md` |
| EmbeddingGemma 2 | Gom URL theo template, gom vấn đề lặp trên 30 URL | Chỉ khi DB không cho biết template |
| Script | Trung vị PSI, quyết định A/B (`psi_decide.py`), bảng còn trừ điểm, ảnh LCP, thư viện trùng, long task theo hàm (`trace_fn.mjs`) | Không dùng model. Script chính xác hơn và không tốn tiền |
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
- Tự trả lại một thay đổi vì 1 trang tụt khi chưa đọc `benchmarkIndex` và `parseHTML` của lượt tụt (`do-dac.md` mục 2).
- Lấy số PSI của URL có tham số không cache (ví dụ `?nc=`) làm số của trang. Bản đó là HTML khác bản cache (`do-dac.md` mục 2).
- Sửa JS khi chưa trace long task theo hàm. Long task có thể chỉ là layout của HTML và CSS (lớp 6).
- Để 2 plugin cùng xử lý CSS, JS hoặc lazyload ảnh. Hai plugin triệt tiêu nhau hoặc tải trùng file (`plugin-chong-cheo.md` mục 1).
- Bật Defer JavaScript mà không bật kèm Include Inline Scripts (lỗi `jQuery is not defined`).
- Đo PSI lại sau mỗi chỉnh nhỏ, hoặc A/B từng thay đổi. Sửa xong cả lô, purge một lần, kiểm chức năng, rồi mới chạy lại PSI. Người duyệt nhắc ngày 29/10/2026 lúc 22:31 rằng đo quá dày tốn thời gian và token. Ngày 30/10/2026 lúc 13:07, người duyệt chốt: hạn chế A/B (`luot-lon.md`).
- Chỉ sửa URL mẫu trong ảnh PSI. URL mẫu là minh hoạ của template. Sửa ở nguồn chung và ở từng template (người duyệt 29/10/2026 21:45).
- Đổi `Version` trong `style.css` của theme khi deploy. LiteSpeed sẽ purge toàn site.

## Changelog

- v1.20 (2026-10-30): Bước 4 và lớp 7 trỏ sang skill mới `wp-gtm-tracking` cho việc hoãn GTM và sửa tracking. Mẫu mới từ nhật ký tối ưu site TMĐT mẫu (SEO Lead dự án, 30/10/2026): `templates/menu-image-lazy.php` (ảnh mega menu lazy, bỏ `fetchpriority`, src bản nhỏ; `php -l` đạt) và `templates/a11y-ten-phan-tu.js` (gắn tên link, nút, select, MutationObserver, nhãn vi hoặc en; thử Chrome headless 9/9 phần tử đúng). `ttfb-cache-trang.md` thêm mục 4c: average response time GSC dưới 300 ms cần cache HTML ở edge, ca TMĐT mẫu 1.000–1.500 → 250–500 ms và ca bán lẻ mẫu shared hosting 1.360 ms, cách đo trên shared hosting. `luot-lon.md` trỏ tới `wp-staging-deploy/references/khong-co-staging.md`. Không đổi script.
- v1.19 (2026-10-30): sửa theo lô thành cách mặc định, người duyệt chốt 30/10/2026 13:07 ("fix một bulk rồi mới chạy PSI test lại, hạn chế cái nào cũng a/b testing"). Reference mới `luot-lon.md`: khi nào dùng, sửa theo template (người duyệt 29/10 21:45), xin quyền sửa theme ngay trong plan, chọn việc theo byte trước LCP, UI gọn kèm mockup, dựng lô bằng git, bộ kiểm không cần PSI (K-HTML, K-CHUC, K-TRACK, K-HINH), deploy theo tầng, xử lý lô đo xấu hơn, 7 bẫy. Bước 3 thêm mục 14. Bước 4 đổi tên thành "sửa theo lô". Phần mở đầu và mục 5 do phiên training soạn lúc 13:09 (đã gộp). Mục 3 dùng bộ kiểm không cần PSI. Đoạn A/B gộp về 4 trường hợp ở `luot-lon.md` mục 1 (2 của phiên training, 2 của phiên này). Config cấp site không còn A/B PSI trên 4 URL, chỉ kiểm chức năng và ảnh. Tự phản biện gộp thành 1 mục lô theo template. Gate thêm mục chặn `g/collect` và `rmkt/collect`. Anti-patterns thêm 2 dòng. `do-dac.md` mục 3 trỏ về 4 trường hợp. Ca thật: site bán lẻ mẫu 29–30/10/2026, mobile trung bình 16 URL tăng từ 56,4 lên 90,4 sau một lô. Ban ngày 29/10, A/B từng việc chỉ lên 57,2. Không đổi script.
- v1.18 (2026-10-30): reference mới `plugin-chong-cheo.md`, rút từ nhật ký tối ưu của SEO Lead dự án trên site TMĐT mẫu (theme đa năng + WooCommerce, 27–30/10/2026: PSI mobile trang chủ 61 → 96, LCP 10,1 s → 1,5 s, INP lab nhóm danh mục 448 → 104–128 ms). Nội dung: mỗi việc một plugin, used CSS theo loại trang, Defer cần Include Inline Scripts, consent `requestAnimationFrame` → `setTimeout`, ảnh mega menu và `fetchpriority` tự gắn, Localize Resources lưu hỏng file, đo cả có và không cache, 3 kết luận rút lại sau đo lặp, Validate Fix 28 ngày, bẫy chú thích CSS trong wp-admin, tăng `ver` theme con, preload font cần `crossorigin`, hỗ trợ tiếp cận. Anti-patterns thêm 3 dòng (plugin chồng chéo, Defer thiếu inline, đo PSI sau mỗi chỉnh nhỏ hoặc A/B từng thay đổi). Bước 4 đổi sang sửa theo lô: một lô chạy PSI một lần; A/B chỉ khi lô làm điểm tụt (chia đôi lô) hoặc thay đổi khó trả lại. Tự phản biện và Gate sửa theo luật này (người duyệt chốt 30/10/2026 13:09). Không đổi script. Ca thật: site của nhật ký, đã đo PSI và GSC trên production.
- v1.17 (2026-10-29): rút từ đợt tốc độ site bán lẻ mẫu đêm 28→29/10 (instance của site, `03-audits/technical/toi-uu-pagespeed/dot-2910/anh-lcp/bao-cao.md`, `font-chu/bao-cao.md` mục 7); người duyệt chọn "Vá hôm nay" lúc 09:15. `psi_decide.py --spec`: chỉ xét trang của spec, lấy ngưỡng và `--a`, `--b` từ `spec.json`, dòng lệnh thắng spec; thiếu `--spec` mà thư mục có nhiều trang thì in cảnh báo. `psi_ab.py build` nhận `--min-runs`, `--max-runs`, `--bench-gap` và khoá chúng vào `decision`. `psi_ab.py table` đọc đủ 6 ngưỡng (cả khoá ở gốc spec), chỉ in nhãn cho trang của spec, tách tên file bằng regex nên nhận tên trang có dấu gạch dưới. Hàm `load_spec`, `spec_thr` ở `psi_lib.py`. 4 test mới, 31 test `test_psi_ab`, `test_psi_decide` đạt; bản cũ trượt cả 3 test hồi quy. Chạy thật chỉ đọc trên thư mục PSI của 2 lane: nhãn khớp nhãn lane quyết tay (#239: xấu hơn, chỉ 4 trang; font: 4 trang, không lỗi `product_cat`). Chưa vá: `psi_ab.py upload` gọi `ssh` không có `-F` (`dot-2910/css-font-js/bao-cao.md` mục 4).
- v1.16.1 (2026-10-28): `lh_local.mjs` tìm puppeteer-core ở cả `lib/esm/` (≤24) và `lib/puppeteer/` (25), vì cache npx mới làm script thoát lỗi `ERR_MODULE_NOT_FOUND`. `cls-chi-psi-thay.md` bước 2 thêm 2 cách truy: tính ngược khoảng dịch từ điểm CLS và rect, so filmstrip với lượt CLS 0 trước khi kết luận do font. Nguồn: CLS 0,323 ở 3/6 lượt PSI trang dịch vụ site agency mẫu 28/10, field 0,00, lab 8/8 lượt CLS 0, không sửa.
- v1.16 (2026-10-28): lớp 6 thêm bẫy link neo dừng sai đích khi Delay JS làm slider khác của theme co trang, cách đo 5 mốc bấm và hàm cuộn lại đích (production site agency mẫu 28/10: 12/24 → 17/17 lượt đạt). Bảng "Đã A/B và không áp" thêm hàng hoãn khởi tạo slider (−11,8 ms TBT ở 1 trang, link neo và CLS xấu hơn). Nguồn: lane slider-fix, kiểm độc lập đạt.
- v1.15.1 (2026-10-27): gỡ tên miền site mẫu khỏi Changelog v1.9–v1.11 và `checklist-theo-lop.md` lớp 7, ghi "site agency mẫu". Không đổi luật hay script.
- v1.15 (2026-10-27): rút từ đợt tốc độ site agency mẫu 26–27/10 (đợt rà skill speed 27/10, đã qua phản biện). Script mới `trace_fn.mjs`: long task theo hàm JS hay layout, không thêm tham số vào URL; port từ lane TBT đã chạy 6 trang × 2 thiết bị. `_guard.mjs` kiểm path thật và `--expect-path` (`lh_local.mjs`, `trace_fn.mjs`); ca lỗi: 75 lượt lab đo một trang. Test mới `test_trace_fn.py` 6 ca, `test_guard.py` thêm 2 ca. `do-dac.md`: sửa luật `?nc=` (bản không cache là HTML khác, 91 so với 98), vẽ đầu muộn 35–45% lượt, 8 lượt khi quyết trả lại, ảnh PSI 1 lượt, kiểm lô đo, `parseHTML` trước khi trả lại. `cls-chi-psi-thay.md`: không có face khớp cả Mac lẫn máy PSI (−4,1%, +5,6%), mọi thay đổi font A/B PSI. `checklist-theo-lop.md`: lớp 1 cache `private`, làm nóng phân trang và trong 5 phút, sitemap, `optm-css_exc` (37 → 15 file); lớp 2 chọn ảnh ưu tiên theo y (4/136 bài sai); lớp 3 cỡ hiển thị và công thức nén của PSI (37,4 → 4,2 KiB); lớp 5b preconnect; lớp 6 trace theo hàm; bảng "Đã A/B và không áp" tách 2 hàng critical CSS (sửa hàng cũ gộp nhầm số) và thêm 8 hàng. `ttfb-cache-trang.md` 4b: `ads.txt`, `assetlinks.json`, `/page/N/` (1,0–1,2 s → 15–16 ms). Bước 0: module Lighthouse bắt buộc khi mục tiêu từ 97. Đã chạy: production và A/B PSI site agency mẫu 26–27/10; nhật ký vá kèm file bằng chứng nằm ngoài repo, ở thư mục của đợt rà. Chưa vào skill: hoãn nạp slider (chờ kiểm độc lập), font tranh băng thông ảnh LCP, thay icon base64.
- v1.14 (2026-10-27): `fcp-guest-mode.md` thêm mục khách mới bị tải lại trang: rewrite `guest.vary.php` sang file `[]` trừ UA làm nóng, mẫu `templates/guest-tap.php` bấm lại lần chạm menu đầu, QA và kiểm sau áp. Đã chạy production site agency mẫu 26/10 (CS-26): mỗi URL tải 1 lần thay vì 2, 5xx 0. Test Chrome `test_guest_tap.py` 5 ca, bắt được bản bỏ bước bấm lại. `checklist-theo-lop.md` thêm bảng "Đã A/B và không áp" (critical CSS khi CSS gộp lớn, face dự phòng, font ưu tiên thấp, tách script inline, beacon RUM). Bước 3 mục 11–12. Checklist tự phản biện thêm mục phương án tự build. Eval thêm 4 ca.
- v1.13.2 (2026-10-27): Bước 3 mục 8: site có CSS gọn thì so md5 file gộp ở cả 4 biến thể khi purge (QA cuối đêm site mẫu: lane chỉ so `m`, `d`, bản `p`, `q` của 2 bài đổi sang file gộp ngoài map).
- v1.13.1 (2026-10-27): `psi_run.py` thêm `--min-gap` (60 giây giữa hai lượt cùng URL + thiết bị, không chạy đồng thời cùng cặp) và bỏ lượt trùng `fetchTime` rồi đo lại. Nguồn: kiểm độc lập lane config 27/10 03:2x, "PSI 3 lượt" thật ra là 1 lượt. Test mới: `test_cached_result_is_retried_not_saved`, `test_min_gap_spaces_same_url`; 162 ca đạt.
- v1.13 (2026-10-27): rút từ đợt site agency mẫu 26–27/10. Bước 1 chọn URL theo md5 file gộp (`chon_url.py` của `wp-ucss`). Bước 3 trỏ sang skill mới `wp-ucss` và mục 404 dò quét. Lớp 1: Googlebot dùng chung bản cache `Accept: */*`, CDN không tách HTML theo Accept, purge Bunny không `exactPath`, `lam_nong.sh -V` khi chặn `guest.vary.php`. Lớp 5: CSS gọn trước critical CSS, bẫy TBT của file gộp lớn, bẫy `.screen-reader-text`. `ttfb-cache-trang.md` mục 4b: khối `.htaccess` trả 404 trước PHP (1,1–2,8 s còn 13–21 ms), `speculationrules`.
- v1.12.1 (2026-10-26): Bước 3 mục 8: site có CDN, PSI có thể đi thẳng origin (site VN chia vùng, PSI chạy từ châu Á), CrUX trễ 28 ngày, đo TTFB theo vùng bằng `cdn-speed-setup`. Nguồn: đợt CDN site VN 26/10/2026.
- v1.12 (2026-10-25): rút từ rà soát web 16–24/10 (perf-1 đến perf-8, hs-7, media-10, trk-1). Biến `WPS` cho đường dẫn script. Bước 0b đọc lộ trình site, parity staging bằng `diff -rq`, `BASELINE.md`. Script mới: `psi_decide.py`, `psi_cls_dump.py`, `lh_local.mjs`, `lam_nong.sh`, `ls_exclusions_check.py`, `psi_con_tru.py`, `fallback_faces.py`, `fa_subset/`, `img_variants.py`, `img_display_width.mjs`, `img_width_report.py`. `psi_run.py` chạy song song `--jobs 2`, từ chối tiền cảnh quá 8 phút, `--detach`. `perf_probe.mjs`, `shot.mjs` có guard `--expect`. `psi_ab.py` tự gắn noindex, khoá ngưỡng, `--split-bench`, `--apply`. Mẫu loader GTM tái phát `gtm.linkClick`. Bước 3 đọc field trước lab, checklist tự phản biện. Bước 5 mặc định 5 hạng mục và bảng "Phần còn trừ điểm". Reference mới `cls-chi-psi-thay.md`, `fcp-guest-mode.md`, `ttfb-cache-trang.md`. Lớp 5b chi phí render của theme. Test offline 160 ca, chạy thật chỉ đọc `psi_con_tru.py` trên JSON PSI cũ của site mẫu 2. Chưa làm kho psi-cache chung của hs-7.

- v1.11 (2026-10-24): rút từ lane tối site agency mẫu 23–24/10. Bước 4 và Gate: backup theo phiên bản, rollback về `v0`, thử rollback sau vòng sửa. `do-dac.md` mục 2: tách lượt theo `benchmarkIndex`, đối chứng cùng khung giờ (bản A 94,5 so với bản C 88,5 do máy PSI). Mục 3: cấm công tắc tham số trong mu-plugin production. `checklist-theo-lop.md` lớp 2: bản sao hero cho desktop làm mobile tải 2 file. Lớp 4: preload font `/website/` làm FCP lab chậm 0,4–0,7 s. Nguồn: `Deliverables/GTV-Brand/GTV-Website/perf-20261020/toi-2310/lcp-anh/kiem-doc-lap.md`, `toi-2310/font/kiem-doc-lap.md`, `ui-20261020/doc-de-2310/sua/kiem-doc-lap.md`.
- v1.10 (2026-10-21): rút từ đợt site agency mẫu 20–21/10. Script mới `cache_variants.py`: robots, canonical, nhãn cache ở 5 biến thể của URL sạch. Chạy thật chỉ đọc trên 2 URL production: 10/10 `hit`, index, canonical tự trỏ. Server giả bắt đúng ca `noindex` chỉ ở bản plain và bot. `psi_run.py` từ chối URL có `utm_*`, `fbclid`, `gclid`, `_ga`. `shot.mjs` không bật cờ `mobile` của CDP và ghi `vw`; `shot_cmp.py` so `scrollWidth` với `vw` (fixture 390 px: bản cũ không báo tràn, bản mới báo `390→420`). Chụp lại baseline bằng bản mới trước khi so. `checklist-theo-lop.md` lớp 1: 8 biến thể cache, làm nóng bằng `Accept` có `image/webp` và bản plain cho bot, số liệu `purge-post_all`, object cache Redis, restart graceful không thay mẹ lsphp, OOM và RAM. Lớp 4: kết quả `font-display: optional` trên production (CLS desktop tốt, mobile tụt, đã rollback), LiteSpeed `optm-css_font_display` ép `swap`. `do-dac.md` mục 2: luật URL đo PSI. Gate thêm kiểm 5 biến thể và thứ tự kiểm độc lập.
- v1.9.1 (2026-10-19): Bước 4 trỏ sang `wp-staging-deploy` cho gói sửa nhiều file.
- v1.9 (2026-10-19): Anti-patterns thêm bẫy `purge-post_all=1`. `do-dac.md`: staging không có cache LiteSpeed nên không đo được thay đổi FCP do Guest Mode. Lớp 7: ảnh xám YouTube trả 404 nhưng vẫn chạy `onload`, kiểm `naturalWidth`. Rút từ đợt site agency mẫu 19/10.
- v1.8 (2026-10-19): lớp 5 thêm 2 bẫy critical CSS (LiteSpeed gom `<style>` có `@font-face` vào file async, dựng lại critical CSS sau khi đổi font). Lớp 6 thêm mục lục Fixed TOC chờ JS và cách thử CSS sửa CLS bằng CDP `Fetch`. Đã chạy thật trên production site mẫu: CLS desktop bài viết 0,53 → 0, trung vị 6 template lỗi CLS mobile 86,5 → 90,5, desktop 96,5 → 98,5.
- v1.7 (2026-10-18): `psi_ab.py build` gộp trang của nhiều spec vào `spec.json`. `do-dac.md` mục 3: đọc CLS từ JSON khi A/B, kiểm tính năng máy PSI bằng `console.error`. `checklist-theo-lop.md` lớp 4: kết quả A/B font trên PSI (tên `local()` bold khớp, chia face theo độ đậm không giảm CLS, preload đổi CLS lấy LCP, `font-display: optional`), bỏ câu "chưa có A/B" về preload. Lớp 7: ảnh thumbnail YouTube dùng bản WebP.
- v1.6 (2026-10-18): thêm từ đợt tối đa điểm trang khoá học và blog của site mẫu 2. Bước 1: đo mọi trang con của template, kể cả trang thanh toán `noindex`. Bước 3: CLS mà PSI gán cho font cần kiểm JS đổi bố cục và stack font trước. Lớp 3: bản 720w cho hero, logo dải chạy ngang, `sizes` ảnh thân bài theo cột chữ, ảnh đại diện PNG sang attachment WebP mà giữ ảnh OG. Lớp 4: stack font riêng của landing thiếu face dự phòng (Mac 0,03, PSI 0,28). Lớp 6: quyết định trạng thái trang trong `<head>` (CLS 0,92 → 0,03), forced reflow bằng `ResizeObserver`. Lớp 7: TBT trang chuyển đổi đến hoàn toàn từ tracking. Script mới: `cls_trace.mjs`, `featured_webp.sh`, `psi_ab.py`, `gtm_delay_check.mjs`; mẫu `templates/gtm-delay-loader.php`. Đã chạy thật trên production: 3 trang thanh toán mobile từ 37–68 lên 81–94 điểm, ảnh hero bài blog 944 KB PNG còn 48,6 KB WebP.

- v1.5 (2026-10-18): thêm từ đợt tối đa điểm PSI của site mẫu 2. Lớp 7: hoãn GTM 2 s không có tác dụng (12/12 lượt vẫn tính TBT), cách chọn mốc hẹn giờ theo lúc Lighthouse dừng ghi trace (site mẫu 2 chọn 5 s, TBT = 0), nạp ngay cho URL quảng cáo và trang chuyển đổi, bẫy `cdp.mjs` tự cuộn. File mới `references/agentic-browsing.md`: cách tính phân số, điều kiện đạt của từng audit, `llms.txt` tĩnh có charset, axe với `content-visibility`, màu đủ tương phản. `psi_run.py` thêm `--categories`. Đã chạy thật: 11/11 template đạt Accessibility, Best Practices, SEO 100 và Agentic 3/3.
- v1.4 (2026-10-18): thêm từ lượt nghiệm thu đợt 2 của site mẫu 2. `do-dac.md`: lượt chậm có thể dồn cả 3 lượt vào một URL nên phải đo lại trước khi kết luận lùi, so trước và sau trong cùng buổi, mỗi cột báo cáo một công cụ, grep key trong evidence. Script mới `deploy_theme_files.sh` (chép file theme lẻ có backup, lint, owner, purge), đã chạy thật trên staging site mẫu 2: file 644 `www:www`, trang 200. `tool-call-thua.md` thêm 2 dòng.
- v1.3 (2026-10-18): thêm từ đợt tốc độ thứ hai của site mẫu 2 (`references/checklist-theo-lop.md`). Lớp 1: cache trình duyệt 1 năm và luật đổi tên ảnh. Lớp 3: bản 640w cho ảnh màn hình đầu, bẫy lightbox đọc `currentSrc`. Lớp 4: `local()` nào khớp trên máy PSI (Arial có khớp), họ dự phòng Roboto cho Android, CLS do chữ đổi dòng, thứ tự `unicode-range` vi sau latin-ext. Lớp 5: `content-visibility` cho trang dài, chiều cao ước tính đo thật, tắt khi nhảy `#mục`. Lớp 6: forced reflow của thanh tiến độ cuộn, vá JS dùng chung ở bước build.
- v1.2 (2026-10-18): thêm bài học từ đợt nghiệm thu site thứ hai sau khi đổi theme. Lớp 4: bỏ luật preload font, thêm bẫy `document.fonts.load()` trong `<head>`, bẫy font dự phòng `local('Arial')` trên PSI, quy trình tự host Google Fonts. Lớp 7: bảng đánh đổi khi hoãn GTM. `do-dac.md`: mục 3 A/B trên PSI, cách đọc LCP mô phỏng có GTM, lượt chậm ngẫu nhiên. Script mới: `gfonts_selfhost.py`, `font_same.mjs`, `gtm_inventory.py`, đã chạy thử trên production site thứ hai (file font tải về trùng từng byte với bản đang chạy).
- v1.1 (2026-10-17): chuyển bản gốc vào SEO Production, viết lại cho mọi site WordPress có quyền server. Thêm hồ sơ server `00-client-context/wp-server.md`, evidence mặc định `03-audits/technical/`, bộ model `tools/ai-assist/`, nhánh không có quyền server.
- v1.0 (2026-10-17): tạo mới từ đợt tối ưu 16–17/10. Chạy thử chỉ đọc trên một site production và staging của nó: PSI 36 lượt không lỗi, mô phỏng 72 lượt, `shot_cmp` 2 lượt staging lệch 0,0%. Sửa sau lượt thử: thêm `probe_table.py`, KB tiết kiệm của audit insight, nhận theme cha + con, cờ boolean của script, bẫy Guest Mode.
