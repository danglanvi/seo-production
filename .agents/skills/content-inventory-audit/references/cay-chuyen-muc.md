# Đổi cây chuyên mục an toàn (nhánh B)

Mục đích: chẩn đoán cây chuyên mục WordPress, dựng plan và đổi cây qua DRY. File này thuộc skill `content-inventory-audit`. Đọc ở nhánh B. Gốc đường dẫn là root repo. Đặt `$C` = `skills/content-inventory-audit/scripts`. Đặt `<T>` = `03-audits/content/<CLIENT>_taxonomy_<YYYY-MM-DD>/`.

## 1. Khi nào chạy

- Người duyệt chê gốc cây chuyên mục, không chỉ chê danh mục của từng bài.
- Trước khi gán danh mục chính hàng loạt ở bước 2 của nhánh A.
- Trước khi đổi tên, slug hoặc cha của chuyên mục đang có click.

Nguồn lỗi:

- Site agency mẫu 18/10/2026: người duyệt viết "gốc rễ chưa đúng" sau khi agent đã sửa danh mục từng bài. Ba vòng sửa cây mất khoảng 35, 20 và 19 phút.
- Site khoá học mẫu 17/10/2026: script chuyên mục tạo 301 sai vì Permalink Manager còn giữ URI cũ. Script phải chạy lại 3 lần, mất 5–8 phút làm lại.
- Hai đợt trên có khoảng 5 phút trang 404 trên production.

## 2. Xuất dữ liệu (chỉ đọc)

Chạy trên server theo `00-client-context/wp-server.md`. Chép script và chạy WP-CLI theo `skills/wp-content-review-apply/references/ghi-an-toan.md` §2: user web, `cd /tmp`, biến đặt sau `sudo -u www`.

```bash
OUT=urls.json wp eval-file $C/export_urls.php
PART=cats  OUT=cats.json  wp eval-file $C/export_tax_redirects.php
PART=rules OUT=rules.json wp eval-file $C/export_tax_redirects.php
PART=uris  OUT=uris.json  wp eval-file $C/export_tax_redirects.php
PART=cpt   OUT=cpt.json   wp eval-file $C/export_tax_redirects.php
PART=terms OUT=terms.json wp eval-file $C/export_tax_redirects.php
tools/gsc/gsc.sh query <property> 180 page > <T>/gsc_page_180d.json
```

- Kéo các file JSON về `<T>/`.
- `rules` chỉ đọc bảng Rank Math. Site dùng plugin redirect khác: xuất tay theo dạng ghi ở `chain_check.py --help`.
- Không có quyền server: dừng nhánh B. Giao plan cho dev và ghi giới hạn vào báo cáo.

## 3. Chẩn đoán 5 dấu hiệu

```bash
python3 $C/build_tax_plan.py diagnose --cats <T>/cats.json --posts <T>/urls.json --cpt-archives <T>/cpt.json \
  --gsc <T>/gsc_page_180d.json --rules <T>/rules.json --out <T>/diagnose.json
```

| Khoá | Dấu hiệu | Cách đọc |
|---|---|---|
| `truc_tron` | Các trục chia trộn nhau | Script chỉ in cây cha → con. Claude đọc và ghi trục chia của từng cấp. Ví dụ: cùng cấp có chuyên mục theo chủ đề và chuyên mục theo loại bài |
| `trung_archive_cpt` | Chuyên mục trùng URL archive của post type | Đổi slug chuyên mục, hoặc chuyển bài sang post type (`cpt_moves`) |
| `slug_va_cham` | Slug chuyên mục trùng slug bài hoặc trang đang publish | Mở URL và đọc body class để biết WordPress trả trang nào |
| `click_chuyen_muc` | Click GSC 180 ngày theo danh mục chính | Chuyên mục nhiều click cần đích 301 cùng chủ đề khi đổi URL. `gsc_khong_khop` là số page GSC không khớp bài nào |
| `redirect_chiem_url` | Rule redirect đang bật khớp URL chuyên mục | Đưa id rule vào `deactivate_redirects` |

- `ket_luan` = `cay_sai` khi có dấu hiệu 2, 3 hoặc 5.
- Nếu cây sai, trình cây mới cho người duyệt trước. Chỉ gán bài sau khi người duyệt chốt cây.
- Chạy lại `diagnose` với `--spec <T>/spec.json` sau khi viết cây mới. Lệnh này kiểm cả URL của chuyên mục mới.

## 4. Viết `spec.json` và `map.tsv`

`spec.json` mô tả cây mới. Ví dụ dưới là site giả `mau.vn`:

```json
{"terms": [{"key": "seo", "term_id": 4, "name": "SEO", "slug": "seo", "parent": null},
           {"key": "tu-khoa", "term_id": 45, "name": "Nghiên cứu từ khoá", "slug": "tu-khoa", "parent": "seo"},
           {"key": "thuat-toan", "term_id": null, "name": "Thuật toán", "slug": "thuat-toan", "parent": "seo"}],
 "pm_remove": ["tax-130"], "noindex_terms": [39], "secondary": {"100": "seo"}, "cpt_moves": {"104": "khoa-hoc"}, "skip": [103],
 "redirects": [{"old": "seo/keyword-research", "to_key": "tu-khoa"}],
 "extra_redirects": [], "deactivate_redirects": [370]}
```

| Trường | Nghĩa |
|---|---|
| `terms` | Cây mới. `term_id` = null là chuyên mục mới. `parent` là `key` của cha |
| `pm_remove` | Khoá URI thừa của Permalink Manager cần xoá |
| `noindex_terms` | `term_id` cần noindex |
| `secondary` | Chuyên mục phụ của bài, tối đa 1 |
| `cpt_moves` | Bài chuyển sang post type khác |
| `skip` | Bài giữ nguyên |
| `redirects` | URL chuyên mục cũ → `key` chuyên mục đích. `trang` = `ve_trang_1` (mặc định) đưa URL phân trang cũ về trang 1 của đích. Chỉ đặt `giu` khi đích có ít nhất bằng số trang của chuyên mục cũ |
| `deactivate_redirects` | Id rule Rank Math cần đặt `inactive` |

- `map.tsv` có cột `id`, `primary`. `primary` là `key` trong `spec.json`. Đặt `key` bằng slug mới để dùng thẳng `primary_slug` của nhánh A.
- Lấy danh mục chính từ nhánh A: viết `scope.tsv` theo cây mới, chạy bước 2–5, rồi chép `id` và `primary_slug` của `apply.json` sang `map.tsv`.
- Tên và mô tả chuyên mục mới đi qua trang duyệt của `wp-content-review-apply`. Ghi bản đã duyệt vào `texts.json` dạng `{key: {name, desc}}`.

## 5. Dựng và kiểm plan

```bash
python3 $C/build_tax_plan.py build --spec <T>/spec.json --map <T>/map.tsv --posts <T>/urls.json
python3 $C/build_tax_plan.py build --spec <T>/spec.json --map <T>/map.tsv --posts <T>/urls.json --out <T>/plan.json
python3 $C/chain_check.py --rules <T>/rules.json --new <T>/plan.json --host <domain>
```

- Lệnh đầu chỉ in tóm tắt. Đọc mọi dòng "cảnh báo" ở stderr. Bài chưa có trong map giữ nguyên chuyên mục.
- `build` thoát 1 khi plan sai và không ghi file. Sửa spec hoặc map rồi chạy lại.
- `chain_check.py --new <plan.json>` kiểm redirect của plan với rule đang có: chuỗi, vòng, nguồn trùng. Không truyền `--dump` và `--terms` ở lượt này, vì URL chuyên mục mới chưa tồn tại.

## 6. Ghi: staging trước, production sau

Đọc `skills/wp-content-review-apply/references/ghi-an-toan.md` §3–§5 trước khi ghi. File đó giữ bẫy Permalink Manager Pro và Rank Math, cách backup và rollback.

1. Staging: chạy `PLAN=plan.json DRY=1 OUT=log-dry.json wp eval-file $C/taxonomy_rollout.php`. Thêm `ALLOW_CHANGED=1` khi dữ liệu staging lệch bản export. Thêm `TEXTS=texts.json` và `LANG_CODE=<mã>` nếu cần.
2. Đọc log: `terms`, `pm` (URI trước và sau), `posts`, `redirects`, `deactivated`. `errors` phải rỗng.
3. Staging: chạy `DRY=0`. Kiểm theo mục 7.
4. Production: xuất lại `urls.json` và dựng lại `plan.json`. Bài có thể đã đổi từ lúc lập plan.
5. Production: chạy `DRY=1` và so log với staging. Backup quan hệ chuyên mục, termmeta, option `permalink-manager-uris`, bảng redirect Rank Math, meta danh mục chính.
6. Production: chạy `DRY=0` khi người duyệt đã chốt. Kiểm theo mục 7.

`taxonomy_rollout.php` thoát 1 khi đích redirect lệch URI Permalink Manager. Không ghi tiếp khi log có lỗi.

## 7. Kiểm sau khi ghi

- `taxonomy_rollout.php` thoát 0. `errors` rỗng. `verify_posts_bad` = 0.
- Xuất lại `urls.json`, `rules.json`, `uris.json`, `terms.json`, rồi chạy lệnh dưới. Lệnh phải thoát 0.

  ```bash
  python3 $C/chain_check.py --rules <T>/rules.json --dump <T>/urls.json --terms <T>/terms.json --uris <T>/uris.json --host <domain>
  ```

- Mỗi URL chuyên mục cũ trả 301 một bước tới URL mới. URL mới trả 200. URL phân trang cũ không trả 404.

  ```bash
  curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://<domain>/<đường dẫn cũ>/
  ```

- Sitemap chuyên mục có URL mới và không còn URL cũ.

## 8. Checklist nhánh B

- [ ] `diagnose` chạy trước khi gán bài hàng loạt. Cây sai thì người duyệt chốt cây mới trước. Nguồn lỗi: site agency mẫu 18/10/2026.
- [ ] Mọi chuyên mục trong plan có `uri`. Log rollout không có `dich_lech_uri`. Nguồn lỗi: site khoá học mẫu 17/10/2026, chạy lại 3 lần.
- [ ] Rule đang chiếm URL chuyên mục mới nằm trong `deactivate_redirects`. Nguồn lỗi: site agency mẫu 18/10/2026.
- [ ] Mỗi lượt staging và production có log `DRY=1` đọc xong trước `DRY=0`. Nguồn lỗi: khoảng 5 phút trang 404 trên production ở đợt đổi cây 17–18/10/2026.
- [ ] Sau khi ghi, `chain_check.py` thoát 0 và URL cũ chỉ qua một bước 301.
- [ ] Tên và mô tả chuyên mục mới có trong `texts.json` đã duyệt.
