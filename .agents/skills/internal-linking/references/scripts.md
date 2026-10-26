# Script của internal-linking: sửa link trong thẻ, kiểm kê dạng mã, tìm đoạn cầu nối, chọn anchor từ GSC

Bốn script trong `scripts/` chỉ dùng Python stdlib. Script không gọi mạng và không sửa site. Chạy lệnh từ root repo, với `IL=skills/internal-linking/scripts`.

| Script | Bước | Việc | Ghi file |
|---|---|---|---|
| `the_link.py` | 4d | Gỡ link, đổi anchor, chuyển link xuống SC trong thẻ duyệt hoặc bản nháp, rồi đếm lại luật | Chỉ khi có `--write` (kèm `.bak`) hoặc `--out` |
| `link_code_audit.py` | 4c | Kiểm kê dạng mã mọi phần tử bấm được trên HTML đã lưu, so trước và sau khi sửa template | Chỉ khi có `--out` |
| `bridge_candidates.py` | 4b | Lọc đoạn ứng viên cầu nối từ output của `site-vector-index`, xuất input Jev `link-bridge`, ghép điểm | `--out` |
| `anchor_gsc.py` | 4 | Liệt kê query GSC của trang đích kèm cờ luật anchor | Chỉ khi có `--out` |

Mã thoát: 0 đạt, 1 lỗi đầu vào hoặc thao tác, 2 sai tham số, 3 vi phạm luật. Không script nào ghi đè file output đã có nếu thiếu `--force`.

Test offline: `python3 -B "$IL/tests/test_internal_linking.py"` và `python3 -B "$IL/tests/test_bridge_anchor.py"`.

## 1. the_link.py: sửa link trong thẻ

Dùng khi sửa link trong thẻ before/after, bản nháp markdown hoặc HTML. Không sửa link bằng regex tay hoặc `assert count == 1`.

```bash
python3 "$IL/the_link.py" unlink the.md --target /dich-vu-seo/ --host <domain> [--anchor "chữ"] [--nth N | --all]
python3 "$IL/the_link.py" reanchor the.md --target /dich-vu-seo/ --host <domain> --old "chữ cũ" --new "chữ mới"
python3 "$IL/the_link.py" to-sc the.md --target /bang-gia/ --host <domain> --anchor "bảng giá" --to-h2 "câu hỏi"
python3 "$IL/the_link.py" check the_moi.md --base the_cu.md --host <domain> [--site-anchors anchors.json]
```

1. Chạy lệnh không có `--write`. Script in diff và kết quả đếm luật.
2. Đọc diff. Nếu diff đúng, chạy lại với `--write`. Script tạo bản `.bak-<giờ>`.
3. Nếu script thoát 3, đọc vi phạm và sửa thẻ. Không thêm `--allow-violations` khi plan chưa ghi lý do.
4. Nếu link cần sửa đã không còn, script thoát 1. Thêm `--missing-ok` khi chạy lại một lô đã sửa một phần.

Luật script đếm lại ([link-placement.md](link-placement.md) §1, [anchor-rules.md](anchor-rules.md) §2):

- R1: mỗi đích có tối đa 1 link trong một tài liệu. Link mảnh `#...` tính cùng đích. Nếu plan ghi lý do riêng cho link thứ hai, thêm `--allow-multi <đích>`.
- R2: mỗi mục H2 thuộc MC nhận tối đa 1 link mới. Lệnh `check --base` so với bản trước để biết link nào mới.
- R3: một anchor xuất hiện tối đa 3 lần. Đưa nhiều file vào `check` để đếm chung, hoặc truyền `--site-anchors` (JSON `{anchor: số lần}`).
- Cảnh báo: link mới nằm ở mở bài, trước H2 đầu.

Script chặn ghi khi lần sửa sinh vi phạm mới. Vi phạm có sẵn từ trước không chặn ghi. Script xử lý `&amp;`, NBSP, chữ Việt NFC và NFD, `<span>` lồng trong `<a>`, href tuyệt đối hoặc tương đối, nháy đơn hoặc kép.

Script xếp mục H2 vào SC khi tên mục khớp `--sc-h2` (FAQ, câu hỏi, kết luận, giới thiệu công ty, liên hệ) hoặc khi mục thuộc 2 H2 cuối (`--sc-last`). Đây là luật tất định ở [link-placement.md](link-placement.md) §4 bước 1. Claude vẫn đọc mục trộn nhiều loại nội dung.

Giới hạn:

- Thẻ dạng JSON (ví dụ trường `proposed` trong `cards.json`): import `unlink_text`, `reanchor_text`, `to_sc_text`, `analyze` từ script và áp trên từng trường. Script chưa có cờ đọc trường JSON.
- Script không xử lý link markdown kiểu tham chiếu (`[chữ][1]`) và link tự động `<https://...>`.

## 2. link_code_audit.py: kiểm kê dạng mã

Dùng ở [link-js.md](link-js.md) §6 bước 1–2 và §3 luật 8. Đầu vào là HTML đã lưu (`.html` hoặc `.html.gz`). Script không tải trang.

```bash
python3 "$IL/link_code_audit.py" scan html/ --host <domain> --noindex noindex.txt --sitemap sitemap.xml --out audit_truoc/
python3 "$IL/link_code_audit.py" compare audit_truoc/summary.json audit_sau/summary.json
```

- Lệnh `scan` gắn mỗi phần tử bấm được vào một vùng: header, footer, nav, sidebar, popup, breadcrumb, toc, body (MC hoặc SC).
- Lệnh `scan` gắn dạng hiện tại: D1–D5, `lai`, `loi`, `UI`. Template lặp gộp thành một dòng trong `templates.tsv`.
- Nếu theme có vùng riêng, thêm `--region "ten=REGEX"` khớp class hoặc id của thẻ tổ tiên.
- Cờ theo [link-js.md](link-js.md) §3: `lai` (luật 3), `thieu_ban_phim` và `thieu_noopener` (luật 6), `link_that_toi_noindex` (luật 5), `doch_chi_co_link_js` và `doch_khong_trong_sitemap` (luật 2).
- Cột dạng mã là hiện trạng, chưa phải đề xuất. Đề xuất D1–D6 vẫn theo [link-js.md](link-js.md) §6 bước 3–5.
- Lệnh `compare` thoát 3 khi số link thật ở body giảm. Chỉ thêm `--allow-body-drop` khi Vincent đã duyệt việc bỏ link đó.
- Cờ `doch_chi_co_link_js` chỉ đủ bằng chứng khi tập HTML phủ phần lớn site. Với tập nhỏ, kiểm thêm bằng sitemap hoặc crawl.

Chạy thử 25/10/2026 trên 343 trang HTML đã lưu của một site WordPress (chỉ đọc): số phần tử theo từng dạng khớp kiểm kê tay ngày 19/10.

## 3. bridge_candidates.py: tìm đoạn đặt contextual bridge

Dùng ở Bước 4b, khi cần nối một trang tiền mới hoặc khi link phải chuyển xuống SC. Script là wrapper mỏng. Skill `site-vector-index` làm phần embedding. Jev `link-bridge` chấm độ hợp.

Chuẩn bị: dựng store của site bằng `site-vector-index` (`extract.py`, rồi `svi.py build --levels page,passage`). Giữ `rows.jsonl` và `pages.jsonl` của cùng lần extract. File `rows.jsonl` phải còn dòng `anchor` để script biết trang nào đã link tới đích.

```bash
python3 "$IL/bridge_candidates.py" queries --targets dich.txt --pages pages.jsonl --out q.jsonl
<venv>/bin/python -I skills/site-vector-index/scripts/svi.py query --store store/ --in q.jsonl \
  --level passage --per-url --k 40 --out hits.jsonl
python3 "$IL/bridge_candidates.py" build --targets dich.txt --hits hits.jsonl --rows rows.jsonl --pages pages.jsonl \
  --out cau-noi/ [--sc-only]
/usr/bin/python3 -I tools/ai-assist/jev.py --task tools/ai-assist/tasks/link-bridge.json \
  --in cau-noi/jev_in.jsonl --out cau-noi/jev_out.jsonl --budget 0.1
python3 "$IL/bridge_candidates.py" merge --candidates cau-noi/candidates.jsonl --jev cau-noi/jev_out.jsonl --out cau-noi/bang.tsv
```

- File trang đích: file văn bản mỗi dòng một URL, hoặc `.jsonl` có trường `keywords`. Đoạn chứa một cụm trong `keywords` vào danh sách, dù đoạn đó nằm ngoài top-K của embedding.
- Lệnh `svi.py query` nạp model một lần cho mọi trang đích. Không chia lô rồi nạp lại model.
- Lệnh `build` bỏ đoạn theo 7 lý do: `cung_trang`, `mo_bai`, `h2_cam` (`--skip-h2`), `lap_template` (cùng chữ trên từ 3 trang), `trang_da_link`, `mc` (`--sc-only`), `duoi_cos` (`--min-cos`). File `summary.json` ghi số đoạn bỏ theo từng lý do.
- `--min-cos` không có mặc định. Hiệu chuẩn ngưỡng theo site bằng skill `model-calibration` trước khi dùng.
- File `jev_in.jsonl` dùng khoá state của lượt hiệu chuẩn `link-bridge`: source {title, heading, paragraph}, target {url, title, summary, headings}.
- Chạy `jev.py` với `--dry-run` trước để kiểm input.

Đọc kết quả `merge`:

1. Bảng xếp theo xác suất `natural_bridge`. Cột `dat` bật khi xác suất từ 0,85 ([link-placement.md](link-placement.md) §5 bước 4).
2. Claude đọc mọi dòng đạt. Mỗi trang nguồn nhận tối đa 1 đoạn cho một đích. Câu mới theo [anchor-rules.md](anchor-rules.md).
3. Dòng có cờ `loi_jev` hoặc `chua_cham`: Claude đọc tay, hoặc chạy lại Jev cho các dòng đó.

Bằng chứng: ngày 17/10 và 18/10/2026, agent dựng pipeline cầu nối trên một site WordPress bằng script ad hoc 2 lần, Gemma nạp lại model mỗi khối. Chạy thử 25/10/2026 trên store của site đó với 2 trang đích: script bỏ 54/80 ứng viên, phần lớn là khối template và đoạn trên trang đã link tới đích.

## 4. anchor_gsc.py: chọn anchor từ query GSC

Dùng ở Bước 4, khi trang đích đã có dữ liệu GSC. Script đọc file. Script không gọi API.

Lấy file GSC theo một trong 2 cách:

- Chạy `tools/gsc/gsc.sh query <property> 90 page,query > gsc.json` từ root repo.
- Xuất CSV từ giao diện GSC sau khi lọc theo trang đích. File này không có cột trang.

```bash
python3 "$IL/anchor_gsc.py" gsc.json --page /dich-vu-seo/ --target-file dich.html --source-file the.md \
  --section "câu hỏi" --site-anchors anchors.json --exclude "<tên thương hiệu>" --out anchor.tsv
```

| Cờ | Luật | Chặn `dat` |
|---|---|---|
| `trang_khac` | Trang khác nhận nhiều click hơn cho query: query chưa phải seed query của đích | Có |
| `khong_co_trong_dich` | Luật 6: chữ query không có trong nội dung trang đích | Có |
| `mo_bai_dich` | Luật 1: chữ query nằm trong đoạn đầu của trang đích | Không, chỉ cảnh báo |
| `khong_co_trong_nguon` | Luật 6: chữ query không có trong mục nguồn | Có |
| `chi_o_dau_doan` | Luật 2: chữ query chỉ có ở đầu đoạn của mục nguồn | Có |
| `du_3_lan` | Anchor đã dùng 3 lần trên site | Có |

Dòng đầu của output ghi cờ đã kiểm và cờ chưa kiểm. Cờ cần file đi kèm: `--target-file`, `--source-file`, `--site-anchors`.

Đọc kết quả:

1. Script không chọn anchor. Claude chọn từ dòng `dat` theo [anchor-rules.md](anchor-rules.md) §6 (intent đích) và luật 5 (dùng từ đồng nghĩa).
2. Không dùng query có cờ `trang_khac` làm anchor tới trang này. Nếu hai trang cùng nhận query đó, ghi vào cột Flag của plan.
3. Seed query thường nằm trong đoạn đầu trang đích, nên luật 1 có thể va với luật "anchor = seed query". Khi dùng query có cờ `mo_bai_dich`, Claude ghi lý do trong cột Lý do.
4. Query không dấu hoặc gõ sai thường mang cờ `khong_co_trong_dich`. Không dùng các query đó làm anchor.
5. Nếu file GSC không có cột trang, script không kiểm được `trang_khac`. Ghi giới hạn này trong plan.

Chạy thử 25/10/2026 trên file GSC 90 ngày của một site WordPress, một trang dịch vụ: 419/434 query không có trong nội dung trang đích, 196 query thuộc trang khác.
