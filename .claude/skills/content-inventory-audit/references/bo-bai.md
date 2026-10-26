# Bỏ bài, gộp bài, bảng kiểm kê và chọn đích 301 hoặc 410

Mục đích: luật bỏ bài, cột của `inventory.tsv` cho lệnh `inventory.py decide`, và quy trình chọn đích 301 hoặc 410 của skill `content-inventory-audit`. Đọc mục 1 ở bước 9, mục 2 và mục 4 ở bước 10, mục 3 ở bước 12. Nhánh C và skill `technical-seo-audit` đọc mục 4. Đặt `$C` = `skills/content-inventory-audit/scripts`.

## 1. Cột của `inventory.tsv`

Mỗi dòng là một bài. Claude ghép bảng từ output của các bước trước. Cột trống nghĩa là "không có dấu hiệu".

| Cột | Giá trị | Nguồn |
|---|---|---|
| `url` | đường dẫn bài | `posts.json` hoặc sitemap |
| `loai` | `tin`, `huong-dan`, `quang-cao`, `trang-tien`, `bang-chung`, `khac` | chuyên mục tin tức → `tin`; danh sách trang tiền và case study của dự án → `trang-tien`, `bang-chung`; còn lại Claude đọc tiêu đề + đoạn mở |
| `clicks` | click trong kỳ GSC | GSC query × page, cộng local |
| `ban_sao_cua` | đường dẫn bài giữ lại (cùng site) hoặc URL đầy đủ (site khác) | cặp cosine rất cao và Claude đọc thấy cùng một bài |
| `dup_of` | đường dẫn bài sẽ nhận nội dung khi gộp | cặp trùng ý định của `dup`, Claude chọn bài giữ |
| `serp_chung` | số URL chung trên 10 | `semantic-content-network` lệnh `serp-overlap` |
| `kenh_ngung` | `1` khi bài thuộc kênh đã ngừng (newsletter, chuyên mục bỏ) | người duyệt chốt kênh |
| `dich_goi_y` | đích 301: bài publish cùng chủ đề, không dùng chuyên mục | Claude chọn |
| `outdated` | `1` khi Claude đọc hit của `scan` và xác nhận bài nói sai thời điểm | `scan_hits.tsv`, `scan_pages.tsv` |
| `effort` | `yes` hoặc `no` | `content-quality-lab` (Jev `content-effort` qua cổng registry) |

Chọn bài giữ trong cặp trùng: bài đang giữ Top 5 cho truy vấn chung, rồi bài nhiều click hơn, rồi bài có bằng chứng riêng.

## 2. Luật đề xuất

Lệnh `decide` áp luật theo thứ tự. Luật đầu tiên khớp thì dừng.

1. Trang tiền và trang bằng chứng (case study, trang dự án): giữ. Không xét bỏ.
2. Bản sao của bài khác (cùng site hoặc site khác): 410.
3. Cặp trùng ý định có SERP chung từ 6/10: gộp vào bài giữ, rồi 301.
4. Cặp trùng ý định có SERP chung 4–5/10: giữ cả hai, đo lại ở ngày 60.
5. Cặp trùng ý định có SERP chung dưới 4/10: giữ tách. Cặp chưa kiểm SERP: xem lại.
6. Bài của kênh đã ngừng: tin thời sự trả 410. Bài hướng dẫn và bài quảng cáo còn giá trị: 301 về bài cùng chủ đề. Không có bài phù hợp thì đưa vào danh sách bỏ và trả 410.
7. Tin thời sự không có click trong kỳ GSC: 410.
8. Bài có thông tin sai thời điểm: làm mới.
9. Bài chỉ có kiến thức chung: có click thì làm mới, không có click thì xem lại (gộp, làm mới hoặc 301).
10. Còn lại: giữ.

Mọi đề xuất 410, 301, gộp và xem lại chờ người duyệt. Nhãn Jev hoặc cosine cao không đủ để gộp: SERP quyết.

## 3. Cách bỏ một bài

Làm theo thứ tự. Backup trước bước 2. Mỗi bước phải trả lại được.

1. Backup: trạng thái bài, nội dung các bài có link tới bài bỏ, các rule redirect liên quan.
2. Chuyển bài về bản nháp. Không xoá bài.
3. Thêm rule cho đường dẫn của bài:
   - 410 cho tin thời sự, bản sao và bài trùng.
   - 301 về bài cùng chủ đề cho bài hướng dẫn còn giá trị. Không có bài phù hợp thì 410.
   - Kiểm rule định thêm bằng `chain_check.py --new` theo mục 4.6 trước khi ghi. Lúc này bài còn publish, nên cảnh báo `nguon_dang_song` là bình thường.
4. Sửa link nội bộ trỏ vào bài:
   - Bài 410: bỏ thẻ `<a>`, giữ chữ.
   - Bài 301: đổi link sang đích mới.
5. Sửa rule redirect cũ đang trỏ vào bài:
   - Bài 410 là bản sao của bài cùng site: đổi đích sang bài giữ lại.
   - Bài 410 khác: đổi rule thành 410. Không để 301 dẫn tới trang 410.
   - Bài 301: đổi đích sang đích mới. Không để chuỗi 301.
6. Kiểm lại: mọi URL bỏ trả đúng mã và đúng đích, sitemap không còn bài nháp, bài giữ lại vẫn trả 200. Xuất lại rule và chạy `chain_check.py` theo mục 4.7.

Ghi qua `wp-content-review-apply` sau khi người duyệt bấm duyệt. Skill này không ghi lên site.

Trước khi đổi bài trùng, đọc redirect cứng trong theme và mu-plugin. Redirect cứng có thể làm bài giữ lại mất khỏi sitemap.

## 4. Chọn đích 301 hoặc 410 cho URL chết

Dùng khi URL trả 404 nhưng có dấu hiệu từng là trang thật: click GSC, backlink, link nội bộ, bot crawl lặp lại. Dùng cả khi trang sản phẩm hoặc khoá học ngừng bán, và khi đổi slug hàng loạt. URL dò lỗ hổng và link hỏng do bot đọc sai thì không redirect.

### 4.1 Luật nền

- 410 chỉ dùng cho URL nằm trong danh sách bỏ đã duyệt. URL gõ sai, link hỏng, URL ngẫu nhiên và URL khác không tồn tại giữ 404. Luật cùng nguồn nằm ở dòng Status hygiene trong Bảng ngưỡng của `seo-logfile-analysis` 1.3. Nguồn: người duyệt chốt 19/10/2026 trên site agency mẫu và site khoá học mẫu.
- Dump DB phải truy vấn mọi `post_type` và mọi `post_status`. Lần dump đầu ở site agency mẫu bỏ sót custom post type (42/55 trang). `export_urls.php` làm đúng việc này: chạy bằng `wp eval-file` theo `references/cay-chuyen-muc.md` §2.
- Chạy `export_urls.php` không kèm `--skip-plugins`. Trường `path` lấy từ `get_permalink()`, nên cần plugin đăng ký custom post type và filter permalink. Nếu plugin làm WP-CLI lỗi, thêm `--skip-plugins` và dùng `pm_uri` thay `path`.
- Tra theo thứ tự: DB (mọi post_type, mọi post_status), slug cũ `_wp_old_slug`, Wayback. Chỉ đề xuất 410 sau 3 bước này.
- Nếu bài còn trong DB ở trạng thái nháp, chờ duyệt, riêng tư, hẹn giờ hoặc thùng rác, hỏi khôi phục trước khi 301. Nguồn: site agency mẫu (gtvseo) 17/10/2026, rule 301 cũ dẫn qua rule trung gian tới trang đang ở nháp.
- Attachment trùng slug không là đích. Attachment cũng không chứng minh bài còn tồn tại.
- Không 301 về trang chủ, trang chuyên mục, thẻ hoặc archive. Chỉ 301 về bài cùng chủ đề. Không có bài phù hợp thì đưa URL vào danh sách bỏ và trả 410. Lý do: ngày 19/10/2026, Google coi 301 về một trang chuyên mục của site agency mẫu là soft 404 (người duyệt chốt 26/10/2026).
- Đích phải là bài publish, trả 200 sau đúng một bước.

### 4.2 Input

| File | Nguồn |
|---|---|
| `urls.tsv`: cột `url`, `clicks`, `dich_goi_y`, `tam_dong`, `bo` | URL 404 từ GSC, crawl, log (`seo-logfile-analysis`), backlink tới trang 404. `clicks` = click GSC 90 ngày theo page. `bo` = 1 khi URL nằm trong danh sách bỏ đã duyệt |
| `urls.json`, `terms.json`, `rules.json`, `uris.json` | `export_urls.php` và `export_tax_redirects.php`, lệnh ở `references/cay-chuyen-muc.md` §2 |
| `wb.json` | `wayback_cdx.py` ở bước 4.3 |

Đặt `<U>` = `03-audits/technical/<CLIENT>_url-dich_<YYYY-MM-DD>/` khi chạy riêng, hoặc `<W>/url/` khi chạy trong kiểm kê.

### 4.3 Chạy

```bash
python3 $C/pick_target.py --urls <U>/urls.tsv --dump <U>/urls.json --terms <U>/terms.json --out <U>/ra1.tsv
python3 $C/wayback_cdx.py --in <U>/ra1.tsv --host <domain> --cache <U>/wb_cache --out <U>/wb.json
python3 $C/pick_target.py --urls <U>/urls.tsv --dump <U>/urls.json --terms <U>/terms.json --wayback <U>/wb.json --out <U>/ra.tsv
```

- Lượt 1 không có Wayback. `wayback_cdx.py` chỉ tra dòng `410_de_xuat` và `hoi`, để bớt số lần gọi.
- `wayback_cdx.py` gọi web.archive.org, nghỉ 1,5 giây giữa 2 lần gọi và lưu cache. Chạy lại với `--offline` để chỉ đọc cache.

### 4.4 Xử lý theo mã

| `ma` | Việc |
|---|---|
| `giu` | URL đang sống. Không redirect. Kiểm lại nguồn báo 404 (crawl cũ, cache) |
| `khoi_phuc` | Hỏi người duyệt khôi phục bài. Khôi phục xong thì không cần rule. Không khôi phục thì ghi đích vào `dich_goi_y` rồi chạy lại |
| `301` (nguồn `old_slug`) | Nhận đích nếu cùng chủ đề |
| `301` (nguồn `goi_y`) | Đích người hoặc Claude chọn, script đã kiểm loại bài |
| `doc_wayback` | Claude đọc bản lưu `https://web.archive.org/web/<timestamp>/<url>`, ghi chủ đề, chọn đích cùng ý định |
| `hoi` | Có click nhưng không có căn cứ. Người duyệt chọn đích hoặc giữ 404 |
| `410_de_xuat` | Giữ 404. Chỉ thành 410 khi người duyệt đưa URL vào danh sách bỏ (`bo` = 1) |
| `410` | URL nằm trong danh sách bỏ đã duyệt |
| `302` | Người duyệt chốt đóng tạm (`tam_dong` = 1). Ghi ngày xem lại vào báo cáo |
| `loi` | Đích gợi ý sai: trang chủ, bài nháp, thùng rác, attachment hoặc không có trong DB. Sửa `dich_goi_y` rồi chạy lại |

Khi nhiều URL cần đích, lấy ứng viên bằng `tools/ai-assist/emb.py nn --k 5`, rồi chạy Jev `redirect-pick`. Ngưỡng ở `tools/ai-assist/README.md` §4. Danh sách ứng viên phải có trang tĩnh ngoài WordPress. Không lấy top-1 của Gemma làm đích: lượt 17/10/2026 top-1 chỉ đúng 4/11 URL. Ghi đích vào `dich_goi_y`, rồi chạy lại `pick_target.py --strict`. Lệnh thoát 1 khi còn dòng `loi`.

### 4.5 Trang ngừng bán và đóng tạm

- Trang sản phẩm hoặc khoá học ngừng bán vẫn sống thì `pick_target.py` trả `giu`. Người duyệt chọn một trong 3 cách: giữ trang, 301 về trang thay thế cùng ý định, hoặc 302 đóng tạm.
- Đóng tạm: đặt `tam_dong` = 1 và `dich_goi_y`. Script đổi 301 thành 302.
- Skill chưa có luật chọn giữa 3 cách. Hỏi người duyệt và ghi quyết định vào báo cáo. Nguồn: một khoá học ngừng bán trên site khoá học mẫu mất 51 phút và 1,29 triệu token (rà skill 24/10/2026).

### 4.6 Kiểm trước khi ghi

```bash
python3 $C/pick_target.py --urls <U>/urls.tsv --dump <U>/urls.json --terms <U>/terms.json --wayback <U>/wb.json --out <U>/ra.tsv --rules-out <U>/moi.json --strict
python3 $C/chain_check.py --rules <U>/rules.json --new <U>/moi.json --dump <U>/urls.json --terms <U>/terms.json --uris <U>/uris.json --host <domain> --out <U>/findings.tsv
```

- `--rules-out` ghi rule cho dòng `301`, `302`, `410`. Rule bỏ bài ở mục 3 viết cùng dạng: `{id, from, comparison, to, code}`.
- `chain_check.py` phải thoát 0. Lệnh thoát 1 khi có lỗi: chuỗi, vòng, 301 dẫn vào rule 410, đích nháp, đích thùng rác, đích attachment, đích trang chủ, đích lệch URI Permalink Manager, nguồn trùng khác đích.
- Slug emoji: WordPress lưu dạng `%f0%9f…`. Script giải mã cả hai dạng trước khi so.
- Cảnh báo `nguon_co_rule_thung_rac`: rule mới trùng nguồn một rule trong thùng rác của Rank Math. Kiểm tay rule đó trước khi thêm.

### 4.7 Ghi và kiểm sau khi ghi

- Ghi rule qua `wp-content-review-apply`, theo `references/ghi-an-toan.md` §3 dòng Redirect, sau khi người duyệt bấm duyệt.
- Xuất lại `rules.json`, rồi chạy lại `chain_check.py` như mục 4.6 nhưng bỏ `--new`. Lệnh phải thoát 0.
- Kiểm từng URL: 301 và 302 qua đúng một bước tới trang 200, URL 410 trả 410. URL có slug emoji: kiểm cả dạng ký tự thật lẫn dạng `%f0%9f…`.

  ```bash
  curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://<domain><đường dẫn>
  ```

### 4.8 Checklist mục 4

- [ ] Không URL nào thành 410 khi chưa có `bo` = 1. Nguồn lỗi: người duyệt chốt 19/10/2026 sau khi theme của site agency mẫu ép mọi 404 thành 410.
- [ ] Mỗi dòng `khoi_phuc` có quyết định khôi phục của người duyệt trước khi 301. Nguồn lỗi: site agency mẫu (gtvseo) 17/10/2026.
- [ ] Mỗi dòng `doc_wayback` có chủ đề Claude đọc từ bản lưu trước khi chọn đích.
- [ ] `pick_target.py --strict` thoát 0 và `chain_check.py` thoát 0 trước và sau khi ghi. Nguồn lỗi: site khoá học mẫu (theaigrowth) 17/10/2026, 301 trỏ URI cũ của Permalink Manager.
- [ ] Không đích 301 nào là chuyên mục, thẻ hoặc archive. Nguồn lỗi: site agency mẫu 19/10/2026, 301 về trang chuyên mục thành soft 404.
