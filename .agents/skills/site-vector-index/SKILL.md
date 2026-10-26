---
name: site-vector-index
description: "Dựng và cập nhật index vector của một site (trang, section, passage, anchor) bằng EmbeddingGemma 2 chạy local, rồi truy vấn, tính tâm chủ đề, tìm cặp gần trùng, so với đối thủ. Dùng trước mọi việc cần đo độ giống ngữ nghĩa trên site hoặc SERP."
metadata:
  version: "1.1"
---

# site-vector-index — embed một lần, mọi skill dùng chung

Mỗi site có một index. Mỗi mục khoá theo hash nội dung, nên lượt sau chỉ embed phần đã đổi. Các skill retrieval, topical focus, content quality, link relevance đọc index này thay vì tự embed lại.

Gốc đường dẫn là root repo. Script nằm ở `skills/site-vector-index/scripts/`.

## Khi nào dùng

- Bắt đầu một việc đo ngữ nghĩa trên site: định tuyến query → URL, độ tập trung chủ đề, information gain, anchor, trang gần trùng, mô phỏng truy xuất passage.
- Site vừa đổi nội dung và skill khác cần số mới.
- Không dùng khi việc chỉ cần đếm hoặc so chuỗi. Khi đó dùng luật tất định.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Danh sách URL công khai, hoặc thư mục HTML đã tải | sitemap của site, crawl, hoặc người vận hành | lấy từ `sitemap_index.xml`; site không có sitemap thì hỏi |
| Domain của site | `00-client-context/` | hỏi |
| Máy có model | venv có `sentence-transformers` + EmbeddingGemma 2 trong cache | dừng, báo người vận hành; không gọi API embedding bên ngoài thay thế |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,bs4,numpy,gemma'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Các bước

1. Tách HTML thành dòng. Chạy bằng Python có beautifulsoup4:
   `python3 -E skills/site-vector-index/scripts/extract.py --urls urls.txt --cache <store>/html --site https://<domain> --out <store>/rows.jsonl --pages <store>/pages.jsonl`
   - Script chỉ lấy main content. Script bỏ nav, header, footer, aside, form, TOC, khối liên quan, khối chia sẻ.
   - Passage mang đường dẫn heading ("H2 > H3: đoạn").
   - Anchor chỉ lấy link nội bộ trong main content, kèm cả đoạn chứa link.
   - Đọc `pages.jsonl.failed.json` nếu có. Trang lỗi không được vào index.
2. Kiểm nhanh 3 trang mẫu, mỗi template một trang. So `pages.jsonl` (`h1`, `h2`, `words_main`, `main_selector`) với trang thật.
   - Nếu `main_selector` là `body`, theme đó cần selector riêng. Thêm selector vào `MAIN_SELECTORS` rồi chạy lại.
   - Lọc trang có `words_main` dưới 300. Trang dịch vụ hay bài viết nằm trong nhóm này là lỗi extract, không phải trang mỏng. Pilot 19/10: bản đầu mất chữ của 24 trang Elementor.
3. Build index bằng venv embedding:
   `<venv>/bin/python -I skills/site-vector-index/scripts/svi.py build --store <store> --in <store>/rows.jsonl --mode replace --max-tokens 2048`
   - `replace`: URL có trong input thay toàn bộ mục cũ của URL đó.
   - `upsert`: chỉ thêm hoặc đổi theo id.
   - `--levels page,passage`: chỉ embed các level cần. Section dài tới 2.048 token nên chậm nhất; bỏ section khi việc chỉ cần passage.
   - Script in tiến độ mỗi 512 mục. Mốc đo trên Mac mini: 16.038 mục mất 37 phút, lượt cập nhật 1.290 mục mất 2 phút.
4. Kiểm bằng `svi.py stats`. Số mục theo level phải khớp `rows.jsonl`. Script tự dừng nếu vector có NaN.
5. Đối thủ hoặc SERP: dựng store riêng cho từng truy vấn hoặc từng đối thủ. Dùng cùng model và cùng prompt `Document`.
6. Lượt cập nhật: chạy lại bước 1 cho URL đã đổi, rồi build `--mode replace`. Mục không đổi hash thì dùng lại vector.

## Lệnh cho skill khác

| Việc | Lệnh `svi.py` | Ghi chú |
|---|---|---|
| Truy vấn → passage hoặc trang gần nhất | `query --level passage --per-url --k 10` | Query dùng prompt `SearchQuery`, tài liệu dùng `Document` |
| So 2 store (mình với đối thủ) | `cross --against <store B> --level section --against-level passage` | Cosine Document–Document |
| Tâm chủ đề site, thư mục | `centroid --level page --group folder [--weight meta.clicks]` | Ra `cos_site`, `cos_group` và file `.summary.json` |
| Cặp gần trùng | `pairs --level section --min <ngưỡng> --cross-url` | Ngưỡng lấy từ registry; chưa có thì hiệu chuẩn trước |

Store trên 20.000 mục: `query` tự lọc thô ở 128 chiều (MRL), rồi xếp lại ở 768 chiều. Muốn tắt thì đặt `--coarse 768`.

## Output

- Store: `03-audits/_vector-index/<domain>/` (`manifest.json`, `items.jsonl`, `vec.npy`, `rows.jsonl`, `pages.jsonl`, `html/`). Store SERP: `03-audits/_vector-index/serp/<slug>/`. Thư mục này nằm trong `.gitignore`, vì vector và HTML lớn.
- Workspace nội bộ (GTV, TAG): đặt cạnh evidence của workstream nếu workstream chưa có instance.

## Gate

- [ ] `manifest.json` ghi đúng model `google/embeddinggemma-2`. Không trộn vector của 2 model trong một store.
- [ ] Không có trang lỗi lọt vào index. Đã soi tay 3 trang mẫu, mỗi template một trang.
- [ ] Ngưỡng cosine mà skill khác dùng phải có trong registry của skill `model-calibration`, đúng cặp prompt.
- [ ] Dữ liệu không rời máy. Index chỉ chứa nội dung công khai của site và đối thủ.

## Anti-patterns

- Dùng ngưỡng cosine của model khác, ví dụ 0,80/0,90 của bge, cho EmbeddingGemma → hiệu chuẩn lại.
- So query với tài liệu bằng cùng prompt `Document` → query phải dùng `SearchQuery`.
- Embed cả trang làm một vector rồi kết luận về từng đoạn → dùng level `passage` hoặc `section`.
- Chạy float16 → NaN. Script ép bfloat16.

## Changelog

- v1.1 (2026-10-19): extract chọn vùng main lớn nhất thay vì thẻ đầu tiên; bỏ `widget` khỏi regex nhiễu (Elementor); link ảnh lấy alt; bỏ dòng không có chữ. `build --levels`, log tiến độ. Test thêm ca Elementor.
- v1.0 (2026-10-19): tạo mới. Gom 4 bản embed rời của workstream site mẫu 18/10 thành một index dùng chung. Test offline `tests/test_svi.py`.
