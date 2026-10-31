---
name: wp-ucss
description: "Dựng CSS gọn theo trang cho site WordPress dùng CSS gộp LiteSpeed: render mọi trạng thái giao diện, kiểm computed style, đổi link bằng mu-plugin theo map md5, purge và làm nóng cả CDN, tái tạo hằng ngày. Dùng khi CSS gộp lớn làm chậm FCP, LCP hoặc tốn lượt crawl."
metadata:
  version: "1.2.2"
---

# wp-ucss — CSS gọn theo trang, kiểm trước khi đổi link

LiteSpeed gộp CSS của theme và plugin thành một file mỗi nhóm trang. File gộp thường nặng 1–1,5 MB, chặn hiển thị và làm Googlebot tải lại nhiều lần. Skill này giữ đúng rule mà trang dùng ở mọi trạng thái giao diện, kiểm computed style từng phần tử trước khi giao, và chỉ đổi link ở cặp (file gộp, path) đã kiểm. File gộp đổi md5 thì trang tự về file gốc tới lần tái tạo sau.

Kết quả chạy thật trên một site WordPress (OpenLiteSpeed + LiteSpeed Cache 7.9.1 + Guest Mode), 26–27/10/2026: 66 path × 4 biến thể, file gộp 110–174 KB brotli còn 26–50 KB. PSI mobile trung vị 3 lượt của 7 template từ 94 lên 98. Trang chủ LCP 2,9 → 2,3 s, FCP 2,0 → 1,4 s. 5xx = 0.

Đường dẫn script: đặt `WU` bằng thư mục chứa file SKILL.md này. Trong repo SEO Production, đứng ở root repo thì `WU="skills/wp-ucss"`. Mọi lệnh gọi `"$WU/scripts/…"`, luôn đặt trong nháy. Script cần `--site <site.json>` hoặc biến `UCSS_SITE`.

## Khi nào dùng

- PSI báo "Reduce unused CSS" hoặc "Eliminate render-blocking resources" với file `wp-content/litespeed/css/<md5>.css` lớn.
- Log server cho thấy Googlebot tải nhiều file CSS gộp (skill `seo-logfile-analysis`).
- Critical CSS kèm file gộp lớn làm TBT tăng.
- Không dùng khi: site không bật CSS combine của LiteSpeed; không có quyền server (giao plan cho dev); site sắp đổi theme (chỉ đo mốc). Tối ưu tốc độ nói chung: `wp-pagespeed`.

## Đọc trước

- `00-client-context/wp-server.md`: SSH, WP-CLI, staging, plugin cache, bẫy riêng của site.
- `references/thuat-toan.md`: Bước 3–6.
- `references/giao-cdn-tai-tao.md`: Bước 7–10.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Domain, SSH alias, docroot, lệnh WP-CLI | `wp-server.md` | Hỏi. Không tự dò credential |
| `site.json` | Chép `templates/site.example.json`, điền theo site | Tạo ở Bước 1 |
| Phạm vi đã duyệt: thêm mu-plugin, thư mục CSS gọn, khối vhost cache 1 năm, job tái tạo | Người duyệt | Chỉ sinh và kiểm offline, trình plan |
| GSC 90 ngày theo trang | `tools/gsc/gsc.sh` | Chọn URL theo template và sitemap, ghi giới hạn |
| CDN đứng trước origin (có/không, loại, cách purge) | `wp-server.md`, skill `cdn-speed-setup` | Hỏi. Sai bước này thì khách ngoài vùng nhận bản không có CSS gọn |
| Thư mục làm việc | `03-audits/technical/ucss-<YYYY-MM-DD>/` | Dùng mặc định này |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Script | Chọn URL, model selector, dựng, kiểm computed style, map, deploy, purge | Dùng. Cổng giao là kết quả tất định của `verify.mjs` |
| Jev | Xếp ảnh vùng lệch còn lại theo khả năng thấy được (rubric `ucss-diff`) | Chỉ xếp thứ tự cho người đọc. Rubric chưa hiệu chuẩn, không dùng làm cổng (`thuat-toan.md` §6) |
| EmbeddingGemma 2 | Gom URL theo template | Không dùng. md5 file gộp đã chia nhóm chính xác |
| Claude | Chọn phạm vi, đọc lệch còn lại, sửa safelist, plan, giao, báo cáo | Dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,ssh,wp-cli,php?,jev?,pagespeed-api?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Kiểm thêm:

```bash
ls ~/.cache/wp-ucss/node_modules/{puppeteer-core,postcss,css-tree} >/dev/null && echo "module: có"
bash "$WU/scripts/tests/run.sh"
```

Thiếu module thì cài theo dòng đầu của `"$WU/scripts/lib-ucss.mjs"`. Test offline phải trả mã 0 trước khi chạm site.

1. **Cấu hình.** Tạo thư mục làm việc. Chép `site.example.json` → `site.json`, `safelist.example.json` → `safelist.json`, `chon.example.json` → `chon/chon.json`. Điền host, SSH, docroot, selector trạng thái của theme (`states`), trường `cdn`. CDN là Bunny thì điền `cdn_host` và `cdn_warm_ecs` để `bunny_purge.py --warm` làm nóng đúng trạm.
   - Khoá: `plock.sh` dùng file `lock_file` (mặc định `~/.cm/locks/prod-http.lock`) để mọi job gọi production chạy lần lượt. Job tái tạo dừng khi `maint_lockdir` tồn tại. Hai đường dẫn này là quy ước của máy vận hành. Đổi trong `site.json` nếu nhóm dùng quy ước khác, và cho mọi job gọi production trên site dùng chung một file khoá.
   - Khoá `css_src_lockdir`: lấy khoá này trước khi đổi nguồn CSS gộp (theme, plugin, gộp font) và trước mỗi lần ghi map tay. Nhả khoá sau khi purge và làm nóng xong. Hiện chưa script nào tự kiểm khoá này.
   - `templates/ucss-swap.php` đặt cứng thư mục `$sub = 'ucss'` và regex link CSS gộp của LiteSpeed (`/wp-content/litespeed/css/<md5>.css`). Đổi `ucss_dir` hoặc plugin cache thì sửa hai chỗ này trong bản cài, rồi chạy test PHP.
2. **Chọn URL đại diện.** Không quét toàn site.
   - Lấy dữ liệu bài: `ds.php` qua WP-CLI `eval-file` → `ds.json`. GSC 90 ngày theo trang → `gsc.json`. Quét md5 file gộp biến thể `m`: `inventory.py`.
   - `python3 -I "$WU/scripts/chon_url.py" ds.json gsc.json inv.jsonl chon/chon.tsv --cfg chon/chon.json`.
   - Luật: mỗi file gộp lấy URL có click cao nhất nếu đạt ngưỡng; thêm danh sách bắt buộc (trang chủ, trang dịch vụ, bảng giá, liên hệ, lưu trữ blog); thêm mọi bài của chuyên mục ưu tiên; thêm bài core và outer nhiều click; thêm bài nhiều hiển thị ở vị trí tốt.
   - Site mẫu 26/10: 66 URL. Người duyệt chốt: đo trên URL template đại diện và bài có keyword tốt, ưu tiên chuyên mục chiến lược.
3. **Quét 4 biến thể.** `inventory.py` với `m,d,p,q`: khách mobile và desktop gửi Accept có WebP (`m`, `d`), và gửi `*/*` (`q`, `p`). Googlebot smartphone dùng chung bản cache với `q`. Lập `jobs.txt` (`path biến_thể` mỗi dòng) cho cặp có đúng 1 file gộp. Chạy trong `plock.sh`.
4. **Sinh và dựng.** `node "$WU/scripts/gen.mjs" --site site.json jobs.txt out 4`, rồi `node "$WU/scripts/build.mjs" --site site.json out`. Đọc dòng tóm tắt của build: số rule giữ, byte brotli, `parseFail`, `nestRules`, `scope` (`thuat-toan.md` §2).
5. **Kiểm.** `node "$WU/scripts/verify.mjs" --site site.json jobs.txt out 4`. Mỗi cặp một file `out/verify/<v>_<slug>.json`. Lệch còn lại sau lượt xác nhận: đọc ảnh vùng lệch trong `out/shots/`, debug bằng `dbg_el.mjs`, sửa safelist, dựng và kiểm lại cặp đó. Có Jev thì xếp thứ tự bằng `jev_ucss.py prep` và `read` (`thuat-toan.md` §5–6).
   - Path có carousel hoặc slider (Owl, slick, Swiper, carousel Elementor) phải qua thêm `verify_init.mjs`. Script khởi tạo trang dưới CSS gộp và dưới CSS gọn từ đầu, cùng HTML, rồi so chiều cao trang và chiều cao widget. `verify.mjs` không bắt lỗi này, vì JS đã khởi tạo dưới CSS gộp (`thuat-toan.md` §5).

     ```bash
     bash "$WU/scripts/plock.sh" 60 900 node "$WU/scripts/verify_init.mjs" --site site.json jobs_widget.txt out/reduced out/init
     ```

   - Mã 1 khi có cặp LỆCH hoặc LỖI. Đọc `out/init/tom_tat.tsv`.
6. **Map.** `python3 -I "$WU/scripts/make_map.py" out stage-<giờ>`. Chỉ path có mọi biến thể đạt mới vào map.
   - Phủ cả nhóm bài viết theo md5 file gộp (khoá `all`): dựng holdout trong thư mục `out-ho` cạnh `out` rồi chạy lại `make_map.py`. Script chỉ ghi `all` khi holdout đạt đủ điều kiện ở `thuat-toan.md` §8. Không có thư mục holdout thì map không có `all`.
7. **A/B trên PSI trước lần giao đầu.** Dựng bản tĩnh của 4 template (trang chủ, trang dịch vụ, lưu trữ blog, bài) với CSS gọn bằng `psi_ab.py` của `wp-pagespeed`. Ghi ngưỡng trước khi đo, quyết bằng `psi_decide.py`. Site mẫu 26/10: trang chủ 93 → 97, lưu trữ blog 92 → 95, trang dịch vụ 95 → 96, bài GEO 99 → 99.
8. **Giao.** Ghi `rollback.md` trước. Rồi làm theo `giao-cdn-tai-tao.md` §2: deploy DRY rồi thật, cài mu-plugin `ucss-swap.php` (lần đầu), khối vhost cache 1 năm (lần đầu, restart graceful có khoá bảo trì), purge LiteSpeed theo nhóm 12 path, làm nóng, purge và làm nóng CDN (§3).
   - Chép file gọn và kiểm file có trên server trước khi ghi map. Sửa vài dòng map thì sửa đúng dòng trong map live (`giao-cdn-tai-tao.md` §2b).
   - Map mới có khoá `all`: purge cả nhóm bài theo lô 12 path rồi làm nóng. Bài còn cache cũ giữ file gộp tới khi cache dựng lại (`giao-cdn-tai-tao.md` §2c).
9. **Kiểm sau giao.** Chạy `qa_sau_giao.py` trong `plock.sh`: mỗi path trong map × biến thể, trang 200, link file gộp có trong map đã đổi sang CSS gọn, robots và canonical so với lượt trước.

   ```bash
   bash "$WU/scripts/plock.sh" 60 900 python3 -I "$WU/scripts/qa_sau_giao.py" --site site.json stage-<giờ>/map.php qa-<giờ>.json m,d,p,q,g --baseline qa-<lượt trước>.json
   ```

   - Mã 1 khi có cặp SAI hoặc robots/canonical đổi. Đọc từng dòng SAI và CẢNH BÁO trước khi báo xong. Lượt đầu chưa có baseline: ghi giới hạn này trong báo cáo.
   - Sau lượt tái tạo, thêm `--paths <thư mục run>/purge_paths.txt` để chỉ kiểm path vừa đổi.
   - Kiểm thêm: 5xx từ giờ giao, header file gọn, PSI 3 lượt của bộ URL đo (`psi_run.py`, `psi_table.py`).
10. **Job tái tạo.** Chạy `regen.sh` với `DRY=1` bằng môi trường tối giản như launchd. Đạt thì cài plist mẫu. Ghi giờ chạy tránh cửa sổ bảo trì (`giao-cdn-tai-tao.md` §4).
    - `regen.sh` gọi `map_diff.py`: so map trên site với map mới, dừng trước khi giao nếu map mới mất quá `MAX_LOST` path (mặc định 3), rồi ghi `purge_paths.txt` và `purge-groups.txt` (12 path mỗi nhóm).
    - `map_diff.py --inv <inv.jsonl>` đếm thêm theo cặp (path, biến thể) và file gộp trang đang phục vụ. Script dừng khi map mới mất CSS gọn ở quá `MAX_LOST_PAIRS` cặp (mặc định 0) mà path vẫn còn trong map. Cặp mất dưới ngưỡng, cặp chưa có CSS gọn ở cả hai map và map bỏ khoá `all` đều in dòng CẢNH BÁO.
    - `regen.sh` đặt `MAX_LOST_PAIRS` mặc định 100000, nên job đêm chỉ cảnh báo cặp mất và ghi `map_diff.txt`. Lý do: cổng này chưa có ca dừng thật, và dừng nhầm lúc đêm làm map không cập nhật. Đọc `map_diff.txt` sáng hôm sau.
    - Giao map tay ngoài `regen.sh`: chạy `map_diff.py --inv` với inventory live vừa quét. Chỉ giao khi 0 cặp mất và 0 dòng CẢNH BÁO chưa có CSS gọn.
    - Nếu một việc khác purge path có CSS gọn, chạy job tái tạo sau đợt purge đó: bản `p`, `q`, `g` có thể dựng lại bằng file gộp khác mà map chưa có (site mẫu 27/10/2026).
11. **Critical CSS (tuỳ chọn).** Dựng từ CSS gọn, kiểm khoảng hở bằng `node "$WU/scripts/ccss_gap.mjs" --site site.json <file.html> <m|d>` (mã 0 khi 0 phần tử lệch), rồi A/B (`giao-cdn-tai-tao.md` §6). Site mẫu đã có CSS gọn và điểm mobile 95–99: critical inline làm TBT tăng ở 5/6 trang. Chỉ giao khi A/B không có nhãn "xấu hơn" ở cả hai thiết bị.

### Tự phản biện trước khi trình
Chấm plan theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của agent khác cho cùng site, so từng mục trước khi trình.

Bản tốt nhất phải có:
- [ ] Bộ URL chọn bằng `chon_url.py`: mỗi file gộp một URL, cộng trang tiền và bài keyword tốt, ưu tiên chuyên mục chiến lược. Nguồn lỗi: người duyệt 26/10/2026 23:25 yêu cầu đo trên URL đại diện thay vì toàn bộ URL.
- [ ] Đủ 4 biến thể `m`, `d`, `p`, `q` khi site có CDN hoặc có Googlebot trong KPI. Nguồn lỗi: 27/10/2026 00:02, CDN giữ bản `Accept: */*` của lượt đầu sau purge, bản đó chưa có CSS gọn.
- [ ] Test offline đạt trên đúng bản script, gồm ca U+00A0 và ca `}` thừa. Nguồn lỗi: 26/10/2026, build dừng vì `CssSyntaxError: Unexpected }` ở một file gộp.
- [ ] Kiểm có lượt xác nhận; mọi lệch còn lại có ảnh vùng và kết luận của người đọc. Path có carousel hoặc slider đã qua `verify_init.mjs`. Nguồn lỗi: 26/10/2026, 3/132 cặp báo lệch giả ở lượt 1; site agency mẫu 27/10/2026, `verify.mjs` báo 0 lệch nhưng Owl Carousel xếp lưới ở 4 path trên production.
- [ ] A/B PSI 4 template với ngưỡng ghi trước lần giao đầu. Nguồn lỗi: đợt 23/10/2026, một lane chạy production 4 giờ dù staging đã xấu hơn (`wp-pagespeed` Gate).
- [ ] Thứ tự giao có chép file gọn → kiểm file có → ghi map → purge LiteSpeed → làm nóng → purge CDN → làm nóng CDN bằng Accept WebP → kiểm `cdn-cachedat`. Nguồn lỗi: 26/10/2026 23:51, purge `/` ở CDN không xoá bản mobile, edge giữ bản cũ; site agency mẫu 27/10/2026, script ghi map trước khi chép file, 4 trang dùng CSS gộp khoảng 2 phút.
- [ ] `rollback.md` có lệnh tắt nhanh (file `OFF`), trả map, gỡ khối vhost, purge CDN, gỡ job; file gọn cũ giữ ít nhất 8 ngày. Nguồn lỗi: lane ảnh LCP 24/10/2026, rollback cài lại bản trung gian thay vì tắt.
- [ ] Critical CSS (nếu có) dựng từ CSS gọn và đã kiểm khoảng hở. Nguồn lỗi: 26/10/2026, critical CSS kèm file gộp 1,48 MB làm TBT tăng khoảng 244 ms; critical thiếu `.screen-reader-text` làm CLS 0,026.

## Output

- Thư mục làm việc: `site.json`, `safelist.json`, `chon/`, `out-chon/` (`pages/`, `model/`, `reduced/`, `verify/`, `shots/`, `jev/`), `stage-<giờ>/` (`map.php`, `map.json`, file gọn), `runs/<giờ>/regen.log`, `purge_paths.txt`, `qa-<giờ>.json`.
- `rollback.md`, `bao-cao.md` (kết luận trước; bảng URL × biến thể × kết quả kiểm; byte trước và sau; PSI trước và sau; việc còn lại).
- Trên server: mu-plugin, thư mục CSS gọn có `map.php`, khối vhost.

## Gate

- [ ] `scripts/tests/run.sh` trả mã 0.
- [ ] Số file `verify/` bằng số cặp đã sinh. Mọi path trong map có mọi biến thể đạt.
- [ ] Path có carousel hoặc slider: `verify_init.mjs` trả mã 0.
- [ ] Nếu một path lệch do thiếu rule, đã quét mọi file gọn trong map tìm cùng rule. Không kết luận từ một trang.
- [ ] Giao map tay: `map_diff.py --inv` trả mã 0 với `MAX_LOST_PAIRS` mặc định 0. Job đêm: đã đọc `map_diff.txt`, mọi dòng CẢNH BÁO mất CSS gọn có lý do.
- [ ] Deploy DRY đã in tóm tắt khớp map trước khi chạy thật.
- [ ] `qa_sau_giao.py` trả mã 0. Mọi dòng CẢNH BÁO có lý do trong báo cáo.
- [ ] 5xx = 0 sau giao. Robots và canonical không đổi ở 5 biến thể.
- [ ] HTML ở CDN (nếu có) là bản mới: `cdn-cachedat` sau giờ purge ở cả 2 UA.
- [ ] PSI sau giao là trung vị 3 lượt, so cùng bộ URL với trước giao.
- [ ] Không in key, IP, host staging, slug đăng nhập ra chat hay file.

## Anti-patterns

- Quét và sinh cho toàn bộ URL của site. Chọn URL đại diện.
- Lấy text CSS từ CSSOM hoặc minify lại bản gọn. Lọc tại chỗ trên cây PostCSS của text gốc.
- Dùng Chrome coverage làm nguồn xoá rule.
- Ghi khoá `all` cho một md5 khi chưa có holdout đạt (`thuat-toan.md` §8).
- Đổi nguồn CSS gộp (gộp font, sửa CSS theme hoặc popup) khi map chưa có bản gọn cho md5 mới, hoặc khi chưa lấy khoá `css_src_lockdir`. Nguồn lỗi: site agency mẫu 27/10/2026, sau khi gộp Font Awesome, 66 path về file gộp khoảng 45 phút.
- Chèn CSS bằng `<style>` ở `wp_head` (shim cho thẻ mới, mu-plugin của lane khác) mà không gắn `data-no-optimize="1"`. Bộ gộp CSS gom khối đó vào file gộp, md5 đổi, nên map và khoá `all` của md5 cũ mất hiệu lực. Nguồn lỗi: site agency mẫu 28/10/2026, shim 2 rule của mu-plugin semantic làm 29/76 path và 21 bài holdout về file gộp từ 03:10 tới khi regen giao map 05:38. Phiên đổi DOM hay CSS phải báo lane CSS gọn trước khi giao, kèm danh sách path và md5 mới.
- Dựng lại cả `map.php` từ một thư mục khác để sửa vài dòng. Cách đó xoá khoá `all` và bản sửa của lane khác.
- Purge toàn site sau khi giao. Purge theo nhóm 12 path rồi làm nóng ngay.
- Làm nóng HTML qua CDN bằng `Accept: */*` trước bản WebP.
- Xoá file gọn cũ ngay sau khi đổi map.
- Dùng Jev làm cổng khi rubric chưa hiệu chuẩn.
- Giao map mới khi lượt kiểm có nhiều cặp "bỏ qua". Đọc `verify.log` trước, và giữ cổng `MAX_LOST` của `regen.sh`.
- Sinh lại CSS gọn của một trang khi khối có thể quay lại đang ẩn: khuyến mãi hết hạn, thẻ gọn có công tắc trả về thẻ đầy đủ. Bản mới mất rule của khối đó, nên khi khối hiện lại thì không có kiểu. Giữ bản sinh lúc khối còn hiện, hoặc thêm selector của khối vào safelist rồi mới sinh lại. Nguồn: site bán lẻ mẫu 31/10/2026, trang chủ ẩn Flash Deal hết hạn và bỏ nút, nhãn thông số của thẻ sản phẩm; CSS gọn giữ bản cũ, vẫn còn rule `sale-timer-banner`, `product-card__actions`, `product-card__specs`.

## Changelog

- v1.2.2 (2026-10-31): Anti-patterns thêm bẫy sinh lại CSS gọn khi khối có thể quay lại đang ẩn. Đã kiểm trên production site bán lẻ mẫu 31/10: trang chủ sau đợt gọn DOM vẫn nạp CSS gọn cũ có đủ rule của khối ẩn. Không đổi script.
- v1.2.1 (2026-10-28): Anti-patterns thêm bẫy CSS chèn ở `wp_head` bị gộp vào file gộp, làm map và khoá `all` mất hiệu lực. Đã xảy ra và đã sửa trên production site agency mẫu 28/10: lane regen dựng holdout mới, giao map lúc 05:38, kiểm độc lập đạt (105/105 bản bài holdout tải CSS gọn). Không đổi script.
- v1.2.0 (2026-10-27): nguồn người duyệt 27/10 22:24 "nâng cấp skills speed … khi có trải nghiệm và chạy thực tế rồi", đề xuất và phản biện của đợt rà speed 27/10. Đã thử trên production site agency mẫu 27/10/2026: safelist `^owl-…` (giao 18:14, kiểm live 20/20 lượt, 8/8 carousel trùng bản gộp); `verify_init.mjs` port từ script A/B khởi tạo của lane (16/16 cặp khớp sau sửa), test fixture Owl trên Chrome; khoá `all` trong `make_map.py` và mu-plugin mẫu (ma trận staging, giao 17:52, holdout 48/48, 230/231 bài), bỏ qua bài có iframe YouTube tải ngay (giao 18:20, PSI 3 lượt), test 7 ca make_map và 6 ca mu-plugin; thứ tự giao chép file trước khi ghi map (lỗi 2 phút 18:14); A/B critical CSS 96 lượt; QUIC.cloud UCSS (0/274 HTML sau 05:19). `map_diff.py --inv` port cổng theo cặp đã chạy làm cổng giao 2 lần, 0 cặp mất; chưa có ca dừng thật, test bằng dữ liệu giả lập, nên `regen.sh` chỉ cảnh báo cặp mất (`MAX_LOST_PAIRS` mặc định 100000), giao tay vẫn chặn. Khoá `css_src_lockdir` thay tên khoá riêng của workstream. Bài chưa thử ghi ở `chua-thu.md` của đợt.

- v1.1.0 (2026-10-27): `map_diff.py` thay heredoc trong `regen.sh` (cổng `MAX_LOST`, `purge_paths.txt`), test bằng map thật của sự cố 05:49 đã ẩn path. `qa_sau_giao.py` thay lượt QA bằng 2 agent: path × biến thể, link đã đổi, robots/canonical so baseline, `--paths`. Chạy thật chỉ đọc trên site mẫu 27/10 09:32: 6 path × 2 biến thể, 0 SAI; bản `g` báo CẢNH BÁO đúng vì một lane đang thử CSS inline cho bản không WebP. `test_combined_href.mjs` kiểm `combinedHref()` trên Chrome headless thật. `evals/cases.yaml` 7 ca. Mẫu `site.json` ghi `swap_attr`.
- v1.0.2 (2026-10-27): `verify.mjs` có cùng lỗi với `gen.mjs` 1.0.0. Ở site mẫu 27/10/2026, một lượt tái tạo bỏ qua 124 cặp đã đổi link, nên map mới mất 30 path và vẫn được giao (khôi phục sau 8 phút). Hàm chung `combinedHref()` trong `lib-ucss.mjs` cho `gen.mjs` và `verify.mjs` đọc URL gốc trong `onerror`. `regen.sh` có cổng `MAX_LOST`: chạy trên dữ liệu sự cố thì dừng. Bước 10 ghi bài học purge ngoài job.
- v1.0.1 (2026-10-27): `gen.mjs` đọc URL file gộp gốc trong `onerror` khi trang đã đổi sang CSS gọn, trả link về file gộp rồi đo. Bản 1.0.0 ghi hash null ở các trang này, nên `regen.sh` sinh lại các cặp đó ở mọi lượt (site mẫu: 3 cặp mỗi lượt). Kiểm thật trên một cặp đã đổi link: hash khớp kiểm kê. `tests/run.sh` thêm phần "gen.mjs".
- v1.0.0 (2026-10-27): tạo mới từ đợt CSS gọn tự build trên một site WordPress OLS + LiteSpeed Cache 26–27/10/2026: chọn URL đại diện, 4 biến thể, `fixCss` (U+00A0, `}` thừa), kiểm A/B/A2 có lượt xác nhận, map theo (md5, path), CDN không tách HTML theo Accept, job tái tạo. Bài học thuật toán từ 11 repo mã nguồn mở.
