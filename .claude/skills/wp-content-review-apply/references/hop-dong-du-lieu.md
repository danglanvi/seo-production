# Hợp đồng dữ liệu của trang duyệt

Đọc file này ở Bước 3. Trang duyệt là artifact có capability `db`. Agent nạp đề xuất. Người duyệt ghi kết quả qua trang. Hai bên không ghi vào collection của nhau.

## 1. Chế độ trường sống

Trang mẫu: `templates/trang-duyet.html`. Biến `SITE` (tên, host, chữ cái favicon, nhãn bản nháp) và mảng `ORDER` ở đầu script. Publish với capability `db` và `user`.

Danh sách phần trên trang lấy theo thứ tự: `summary.sections`, rồi `ORDER`, rồi mọi tài liệu `report` có `items`. `ORDER` chỉ là thứ tự mặc định. Phần thêm sau vẫn hiện và bấm được dù không có trong `ORDER`. Lỗi đã gặp 17/10: `ORDER` viết cứng, phần thêm sau không bấm được nút E.

### Collection `report` (agent ghi)

Mỗi phần là một tài liệu, mã tài liệu là tên phần (`meta`, `year`, `links`…). Tài liệu `summary` chứa phần giới thiệu chung và `sections: [{"key", "title", "state", "count"}]`.

```json
{
  "intro": "Một đoạn mô tả phần này cho người duyệt.",
  "options": [{"key": "A", "label": "Giữ từ khoá chính", "desc": "Mô tả ngắn phương án A"},
              {"key": "B", "label": "Nhấn câu hỏi", "desc": "Mô tả ngắn phương án B"}],
  "items": [{
    "id": "meta-101633",
    "post_id": 101633,
    "url": "https://example.vn/en/seo-service/",
    "label": "Tên trang hiện tại",
    "kind": "Trang", "lang": "en", "imp": 6015, "clicks": 12,
    "note": "Lý do đề xuất, ngắn.",
    "default_option": "A",
    "fields": [
      {"key": "seo_title", "name": "SEO title (thẻ title)", "max": 65,
       "before": "Giá trị hiển thị", "raw": "Giá trị thô trong DB", "A": "Phương án A", "B": "Phương án B"},
      {"key": "slug", "name": "URL (đường dẫn)", "editable": true, "before": "/cu/", "proposed": "/cu/"}
    ]
  }]
}
```

- `before` là chữ hiển thị cho người duyệt. Trường trống ghi `(trống)` kèm `before_hint`.
- `raw` là giá trị thô dùng để so lúc ghi. Thiếu `raw` thì `plan.py` dùng `before`, và coi `before` trong ngoặc đơn là chuỗi rỗng.
- Một trường dùng `A`/`B` hoặc `proposed`. Trường không định đổi đặt `A` = `B` = `before`, trang hiện "Giữ nguyên".
- Thẻ có `A`/`B` phải có `options` ở mức thẻ (`item.options`) hoặc mức phần. Thiếu cả hai thì trang chỉ hiện A. `check_cards.py` báo lỗi.
- Hai trường cùng `key` trong một thẻ: builder đặt khoá riêng ngay trong thẻ, theo thứ tự xuất hiện (`text`, `text#2`, `text#3`). `values` lưu theo khoá đó. `check_cards.py` báo lỗi khi còn hai trường cùng key. Hàm `fid()` của trang đặt `key#n` cùng thứ tự cho thẻ cũ, nên đổi khoá theo thứ tự này không làm lệch `values` đã lưu. Lỗi đã gặp 18/10: 36 thẻ trùng key, mọi ô hiện cùng một chữ.
- `target` (tuỳ chọn) chỉ nơi ghi. Thiếu `target` thì dùng bảng mặc định ở mục 3.
- Trường `action` (đề xuất kỹ thuật dạng chữ) không có `target`. Agent ghi tay theo kết quả duyệt.
- `doi_chu_duyet` (tuỳ chọn): lý do đổi một chữ đã duyệt, ví dụ "vượt 688 px". Thiếu lý do thì `so_duyet.py the` chặn thẻ.
- Thẻ ảnh: `img` là đường dẫn tương đối của file ảnh publish kèm trang (tham số `files` của Artifact) hoặc URL asset. Thêm `img_alt`, `img_w`, `img_h`, `img_cap` nếu có. Publish lại trang kèm `files` mỗi khi thêm ảnh mới.

Mỗi trường có chữ mới mang khối `qa`. Agent điền `humanizer` và `jev_text_qa`. `the_qa.py --ghi` điền phần còn lại:

```json
"qa": {"humanizer": "3.2.1 | đã rà", "jev_text_qa": "ok", "copy_guard": "ok", "nfc": true,
       "links": {"mat": [], "them": ["/geo/"]}, "do_dai": {"A": {"ky_tu": 58, "px": 540}, "B": {"ky_tu": 61, "px": 566}}}
```

Trường một phương án (`proposed`) dùng `do_dai: {"ky_tu", "px"}`. Không có humanizer trong runtime thì ghi `"humanizer": "tự rà | <ngày>"`.

### Collection `reviews` (người duyệt ghi qua trang)

Mã tài liệu là `item.id`.

```json
{"section": "meta", "item_id": "meta-101633", "url": "…", "label": "…",
 "status": "approved", "option": "A", "values": {"seo_title": "…", "meta": "…", "slug": "/…/"},
 "note": "", "updatedAt": "2026-10-17T07:02:11.000Z"}
```

- `status`: `approved` (giữ phương án), `edited` (người duyệt sửa chữ), `rejected` (không làm), `applied` (agent gắn sau khi kiểm live).
- Agent chỉ đổi `status` sang `applied` qua `mark_batch.py`: thêm `appliedAt`, nối dòng `[Claude hh:mm] <chỗ ghi, cách verify, rollback>` vào sau `note` cũ, không đè `note` của người duyệt.
- `values` chứa giá trị cuối cùng của từng trường. Với `edited`, `values` là bản người duyệt gõ.
- Mọi tài liệu phải có `item_id` bằng mã tài liệu. Trang đọc reviews bằng 3 truy vấn theo khoảng `item_id`, mỗi truy vấn tối đa 1.000 tài liệu. Tài liệu thiếu `item_id` không hiện khi trang có hơn 300 thẻ. Trang cảnh báo khi một khoảng đạt 800 tài liệu.
- Nút "Đặt lại" xoá tài liệu. Mục không có tài liệu là chưa duyệt.

## 2. Chế độ khối nguồn

Dùng khi trang dựng từ file HTML hoặc template trong repo của site, rồi mới đưa vào WordPress. Cần 2 script trong repo đó: một script tách khối chữ từ file nguồn, một script áp bản sửa vào file nguồn. Trang duyệt hiện từng khối kèm nút E.

- Collection `pages` (agent ghi): một tài liệu mỗi trang, gồm danh sách khối `{id, text, role, section}`. Mã khối dạng `<trang>-<mục>-<số>`, giữ nguyên khi chỉ đổi chữ.
- Collection `edits` (người duyệt ghi): `{page, block, section, role, before, text, note, status, updatedAt}`. `status` là `edited` hoặc `note`. Agent đổi thành `applied` kèm `appliedAt` sau khi áp.
- Áp bản sửa vào file nguồn, build lại, deploy staging, rồi tách khối và nạp lại `pages`.
- Khối lặp ở trang khác: script áp bản sửa in "chữ cũ còn ở" để agent sửa tay.

## 3. Bảng `target` mặc định

| `key` của trường | `target` | Ghi vào |
|---|---|---|
| `seo_title` | `meta:rank_math_title` | Post meta Rank Math |
| `meta` | `meta:rank_math_description` | Post meta Rank Math |
| `h1` | `post_title` | Cột `post_title` |
| `slug` | `post_name` | Cột `post_name`, kèm redirect 301 Rank Math từ URL cũ |

Site dùng Yoast: đặt `target` rõ là `meta:_yoast_wpseo_title`, `meta:_yoast_wpseo_metadesc`. Biến năm của Yoast là `%%currentyear%%`. Redirect khi đổi slug: tạo bằng plugin redirect của site trước, vì `apply.php` chỉ ghi bảng redirect của Rank Math.

Target khác phải ghi rõ trong trường:

- `meta:<key>`: post meta bất kỳ.
- `acf:<field_name>`: trường ACF qua `update_field`.
- `elementor:<widget_id>:<đường dẫn settings>`: ví dụ `elementor:b435907:editor` hoặc `elementor:a67e445:list.0.list_title`.

## 4. Nạp và đọc

- Nạp: ArtifactData `batch` gồm các lệnh `set` cho tài liệu `report/<phần>`. Tài liệu đã có thì kèm `if_version` lấy từ lần đọc gần nhất. Đợt lớn dùng `seed_batches.py --only-missing` để chỉ nạp tài liệu còn thiếu. Mỗi file `_writes_NN.json` là một `batch`.
- Đọc: ArtifactData `list` collection `reviews` với `out_dir` vào `data/reviews/`. Mỗi tài liệu thành một file `<mã>.json`.
- Sau khi ghi: gắn `applied` bằng `mark_batch.py`. Lấy `version` bằng một lần query `reviews` có `status in [approved, edited]`, `limit 1000`, lưu ra file. Không `get` từng thẻ, không query `__name__ in`. Lỗi đã gặp 20/10: query `__name__ in` trả 0, thêm khoảng 10 lệnh thừa.
- Mỗi `batch` là một lần người vận hành bấm duyệt. Hai script in trước số lô, báo số này cho người vận hành.
- Ghi version hiện tại của từng tài liệu vào HANDOFF (ví dụ "summary 4, meta 3") để phiên sau đặt đúng `if_version`.
