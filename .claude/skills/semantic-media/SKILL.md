---
name: semantic-media
description: "Đặt media đúng mục của trang: kiểm kê video và ảnh thật, tìm slot theo heading, ghép video bằng EmbeddingGemma, dựng sơ đồ bằng code và so chữ với thân bài, nhúng YouTube facade kèm VideoObject. Dùng khi trang thiếu video, ảnh thật hoặc sơ đồ ở mục cần minh hoạ."
metadata:
  version: "1.1"
---

# semantic-media — media đúng ngữ cảnh cho từng mục của trang

Skill này đặt media vào đúng mục của trang: video giải thích đúng heading, ảnh thật của đúng người và đúng nơi, sơ đồ dựng từ chữ thật trên trang. Media sở hữu đứng trước ảnh AI. Mỗi slot có alt, caption, cách nhúng và schema.

Gốc đường dẫn là root repo. Script và mẫu ở `skills/semantic-media/`:

| File | Việc |
|---|---|
| `scripts/media_match.py nn` | EmbeddingGemma xếp video cho từng slot (top k). Dùng lại encoder của `site-vector-index` |
| `scripts/media_match.py check` | Kiểm luật của media plan: video tối đa 2 trang, đủ alt và caption, không dùng ảnh AI thay ảnh thật, entity người nói của lời chứng thực, ảnh trùng giữa trang (`--used`) |
| `scripts/diagram_render.mjs` | Render sơ đồ HTML thành PNG và WebP, kiểm chữ thiếu, chữ tràn, chữ đè logo, chữ chồng nhau, chữ nhỏ nhất |
| `scripts/diagram_checks.mjs` | Hàm đo chữ nhỏ nhất, dùng chung với `diagram_render.mjs`. Không đo được thì báo lỗi |
| `scripts/diagram_body_check.py` | So chữ của sơ đồ với thân bài trước khi chèn, xuất input cho Jev. Không gọi model |
| `scripts/watermark.py` | Ghép logo vào ảnh AI, thu về bề rộng đích, xuất WebP dưới giới hạn KB |
| `assets/media-facade.php` | Mẫu mu-plugin: YouTube facade (iframe chỉ tạo khi bấm) và JSON-LD VideoObject |

Test, chạy từ `skills/semantic-media/`: `python3 -B tests/test_media.py` và `python3 -B tests/test_diagram.py`. Hai test render của `test_diagram.py` cần node và Chrome.

## Khi nào dùng

- Trang tiền hoặc bài blog thiếu video, ảnh thật hay sơ đồ ở mục cần minh hoạ.
- Site nhúng iframe YouTube nặng hoặc video MP4 tự host.
- Cần sơ đồ có chữ tiếng Việt đúng chính tả.
- Cần kiểm sơ đồ, video lời chứng thực hoặc ảnh trùng giữa trang trước khi chèn.
- Không dùng để tối ưu tên file, alt và dung lượng của ảnh đã có. Dùng `image-seo-optimize`.
- Không dùng để chấm alt có tả đúng ảnh không. Dùng `visual-serp-lab`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Danh sách trang trong phạm vi | sitemap, danh sách trang tiền | hỏi |
| Video sở hữu: id, tiêu đề, mô tả, chương, thời lượng, trạng thái | YouTube Data API hoặc `yt-dlp --flat-playlist` của các kênh khách | bỏ phần video |
| Ảnh thật: người, nơi, sự kiện, quyền dùng | kho ảnh của khách | bỏ phần ảnh thật, đề xuất buổi chụp |
| Logo nền trong | brand guideline của khách | không xuất ảnh AI |
| Chữ thật trên trang (H2, H3, nhãn) | crawl chỉ đọc | crawl trước |
| Thân bài của trang có sơ đồ | file HTML, Markdown hoặc text của bài | không chèn sơ đồ |
| Entity của site và của từng trang | bảng A của `index.md`, người vận hành | hỏi, không đoán |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| EmbeddingGemma 2 (`media_match.py nn`) | xếp video cho từng slot, prompt `SearchQuery` cho slot và `Document` cho video | dùng làm danh sách ứng viên. Lượt thử 18/10: ở bài blog, 12/12 video đã chọn nằm trong top 3. Ở trang dịch vụ và trang thương hiệu, truy vấn quá chung nên Claude chọn lại |
| Code (`check`, `diagram_render.mjs`, `diagram_body_check.py`, `watermark.py`) | luật plan, kiểm chữ trên sơ đồ, so chữ sơ đồ với thân bài, watermark | dùng |
| Claude | liệt kê slot theo heading, đọc mô tả và chương video, nghe người nói trong video lời chứng thực, chọn ảnh thật, viết alt và caption, dựng HTML sơ đồ, đọc chuỗi `can_doc` và `mot_phan` | dùng |
| Jev `claim-faithful` | đọc chuỗi cần đọc trong `claims.jsonl` của `diagram_body_check.py` | chưa dùng: `tools/ai-assist/tasks/` chưa có rubric này. Claude đọc. Khi có rubric, hiệu chuẩn bằng `model-calibration` trước khi tin cổng |
| Jev `chu-dinh` | dấu tiếng Việt chạm dòng trên hoặc bị dải màu che trên sơ đồ | chưa dùng: repo chưa có rubric. Claude xem bản `@2x.png`. Khi có rubric: `lines_touch` từ 0,6 thì Claude xem vùng chữ phóng 2x (hiệu chuẩn 19/10 trên ảnh OG site theaigrowth: lỗi thật từ 0,62) |
| Jev `ui-visual` | gắn nhãn lỗi giao diện sau khi chèn | qua `web-qa-gate` |
| GLM Flash | trích câu nguyên văn | không dùng: `diagram_body_check.py` đã trích câu bằng chứng bằng code |

## Luật chọn media

1. Thứ tự ưu tiên: video sở hữu, ảnh thật, ảnh chụp màn hình, sơ đồ bằng code, ảnh AI.
2. Một video xuất hiện tối đa 2 trang trong phạm vi. Nếu chương video trùng heading, nhúng từ mốc chương đó.
3. Trang về một người chỉ dùng ảnh có người đó. Ảnh đội ngũ, văn phòng, khách hàng phải là ảnh thật.
4. Không dùng ảnh AI cho người, văn phòng, khách hàng hay ảnh đại diện lời chứng thực. Ảnh đó sẽ thành ảnh giả.
5. Sơ đồ có chữ dựng bằng HTML/SVG. Nhãn lấy từ H2, H3 và chữ thật trên trang. Model ảnh AI chỉ tạo hình minh hoạ không chữ.
6. Ảnh AI có watermark logo của site: góc dưới phải, rộng 9%, mờ 0,55.
7. Mỗi slot có alt tả nội dung ảnh hoặc video, và caption nói điều người đọc rút ra.
8. Video lời chứng thực chỉ nhúng khi người nói thuộc đúng entity của trang. Kiểm bằng lời nói trong video, không dựa vào tên file hay tiêu đề. Người nói là học viên hoặc khách của brand khác thì không dùng video đó.
9. Ảnh trong slot nội dung không lặp ảnh đã dùng ở trang khác trong phạm vi. Ảnh được phép lặp, ví dụ chân dung tác giả trong hộp tác giả, ghi `allow_reuse: true` kèm lý do.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,pillow,gemma?,chrome,node,ffmpeg?,bs4?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu thiếu `gemma`, bỏ bước xếp video tự động: Claude đọc danh sách video và chọn tay. Nếu thiếu `chrome` hoặc `node`, không render sơ đồ. Nếu thiếu `bs4`, lập danh sách ảnh đã dùng bằng tay (một dòng một src). Nếu thiếu `ffmpeg`, không có `ffprobe`: Claude hỏi thời lượng và dung lượng video.

### Bước 1 — kiểm kê và tìm slot

1. Liệt kê video của các kênh khách: id, tiêu đề, mô tả 400 ký tự đầu, chương, thời lượng, trạng thái (public, unlisted, private). Bỏ Shorts.
2. Liệt kê ảnh thật: lớp ảnh (chân dung, đội ngũ, văn phòng, sự kiện), người trong ảnh, tỉ lệ, độ phân giải, quyền dùng.
3. Đọc từng trang. Ghi slot sau heading cần minh hoạ: `slot_id`, trang, heading, loại media cần, mục đích, entity.
4. Liệt kê video đang nhúng trên site và trang chứa video đó.
5. Liệt kê ảnh đang hiển thị ở các trang trong phạm vi, trang chủ trước. Mỗi file `.html` đã crawl cần file `.url` cùng tên:

   ```bash
   python3 skills/visual-serp-lab/scripts/visual.py images --html-dir <thư mục HTML đã crawl> --out images.jsonl
   ```

   Mỗi dòng của `images.jsonl` có `page` và `src` của một ảnh trong vùng nội dung.

### Bước 2 — ghép và chọn

1. Viết `slots_q.jsonl` (tiêu đề trang + heading + entity + mục đích) và `videos_d.jsonl` (tiêu đề + mô tả + chương).
2. Chạy:

   ```bash
   ~/.venvs/embeddinggemma/bin/python -B skills/semantic-media/scripts/media_match.py nn --slots slots_q.jsonl --videos videos_d.jsonl --out slot_video_nn.jsonl
   ```

3. Claude đọc top 8 của từng slot và chọn theo luật. Ghi `media_plan.json`: media, alt, caption, vị trí, cách nhúng, schema, trạng thái (`ready`, `needs_upload`, `needs_consent`, `needs_capture`, `needs_shoot`, `needs_source`, `ready_to_generate`). Ghi `site_entity` ở đầu plan. Trang thuộc entity khác thì ghi `page_entity` cho slot.
4. Video lời chứng thực (`purpose: "testimonial"`): kiểm người nói trước khi chọn.
   - Đọc thời lượng và dung lượng: `ffprobe -v error -show_entries format=duration,size -of json <video>`. Nếu file tự host lớn, cắt clip theo Bước 3 mục 3 hoặc đưa lên YouTube và nhúng facade.
   - Nghe đoạn người nói tự giới thiệu, hoặc chép lời bằng công cụ chép lời có trên máy. Ghi `speaker`, `speaker_entity` và `speaker_evidence` (mốc giây + câu nguyên văn) vào slot.
   - Nếu người nói thuộc entity khác, bỏ video khỏi slot. Nếu chưa nghe được, đặt trạng thái `needs_source`.
5. Ảnh trùng giữa trang: ghi `media.src` cho mọi slot ảnh. Bước 6 so `src` với `images.jsonl` của Bước 1. Script bỏ host, query, hậu tố `-WxH` và `-scaled` trước khi so.
   - Script không bắt ảnh gần giống (crop, đổi cỡ, nén lại). Claude dựng contact sheet đánh số, ảnh mới cạnh ảnh đã dùng, rồi xem và ghi số ảnh trùng.
   - Ảnh trùng thì chọn ảnh khác, hoặc đặt trạng thái `needs_shoot`. Không ghi "không cần thêm ảnh" khi slot đang dùng lại ảnh của trang khác.
6. Chạy `media_match.py check --plan media_plan.json --nn slot_video_nn.jsonl --used images.jsonl`. Sửa mọi lỗi trước khi trình.

### Bước 3 — dựng media

1. Sơ đồ: mỗi sơ đồ một file HTML có `.canvas`, `.logo` và `window.__ready`. Khai chữ bắt buộc trong `specs.json`. Render:

   ```bash
   ROOT=<thư mục> SRC_SUB=src SPECS=specs.json OUT=out FONTS="<font chính>" node skills/semantic-media/scripts/diagram_render.mjs
   ```

   - Chỉ dùng sơ đồ có `.check.json` không lỗi và `min_font_measured: true`.
   - "Chữ nhỏ nhất không đo được" là lỗi, không phải đạt. Sơ đồ AI27 của site gtvseo ngày 19/10 từng in "chữ nhỏ nhất nullpx đạt". Từ v1.1, script đo cả chữ trong span inline.
   - Sơ đồ có chữ tiếng Việt: xem vùng chữ trên `<OUT>/<ID>@2x.png`. Nếu dấu chạm dòng trên hoặc bị dải màu che, nới line-height rồi render lại.

   Trước khi chèn, so chữ của sơ đồ với thân bài:

   ```bash
   python3 skills/semantic-media/scripts/diagram_body_check.py --specs specs.json --body <thân bài .html|.md|.txt> --out body_check.json --claims claims.jsonl --write
   ```

   - Nếu nhiều sơ đồ thuộc nhiều bài, thay `--body` bằng `--body-map map.json` (`{"<id sơ đồ>": "<file thân bài>"}`).
   - Thiếu `--write` thì script chỉ in kết quả, không ghi file.
   - `khong_thay`, `nguoc` và số không có trong thân bài là lỗi. Sửa chữ của sơ đồ theo thân bài, rồi render lại.
   - `can_doc` và `mot_phan` không làm script thoát khác 0. Claude đọc từng chuỗi với câu bằng chứng trong `claims.jsonl`. Câu ngược chiều đứng đầu. Chuỗi nói ngược thân bài thì sửa.
   - Script so từng chuỗi riêng, không đọc khung mà tiêu đề đặt cho chuỗi. Claude đọc tiêu đề cùng các nhãn.
   - Ví dụ site gtvseo, 19/10: sơ đồ AI19 ghi "Có schema" dưới tiêu đề "Yếu tố tương quan với thứ hạng Google". Script xếp `can_doc`. Câu bằng chứng đầu là "Không có sự kết nối nào giữa việc có schema và ranking cao trong Google". Claude sửa nhãn trước khi chèn.
   - Mã thoát khác 0 thì không chèn sơ đồ. Còn chuỗi `can_doc` chưa đọc thì cũng không chèn.
2. Ảnh AI (phương án cuối): tạo hình minh hoạ không chữ bằng công cụ ảnh mà dự án được phép dùng. Ghép logo bằng `watermark.py`.
3. Clip cho landing: cắt đoạn ngắn từ video sở hữu bằng ffmpeg, không âm thanh, có poster:

   ```bash
   ffmpeg -ss <giây bắt đầu> -t <số giây> -i <video gốc> -an -vf "scale=960:-2" -c:v libx264 -crf 28 -movflags +faststart clip.mp4
   ```

4. Video: dùng mẫu `assets/media-facade.php`. Ghi `videos.json` cạnh mu-plugin: tiêu đề, mô tả, ngày đăng, thời lượng, trạng thái, `@id` tác giả.

### Bước 4 — duyệt, ghi, kiểm

1. Trình bảng slot cho người duyệt: slot sẵn sàng, slot chờ việc bên ngoài (upload, khách đồng ý, chụp).
2. Ghi lên staging bằng `wp-content-review-apply` hoặc `wp-staging-deploy`.
3. Chạy `web-qa-gate`. Đo PageSpeed theo template bằng `wp-pagespeed`, cả mobile.
4. Kiểm Rich Results cho trang có VideoObject.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] Mỗi slot gắn với một heading thật trên trang.
- [ ] `media_match.py check --used images.jsonl` không còn lỗi, gồm ảnh trùng giữa trang. Nguồn lỗi: site theaigrowth 17/10, trang mới dùng lại 11 ảnh của trang chủ, sau đó phải thay 8/9 ô.
- [ ] Không có ảnh AI cho người, văn phòng hay khách hàng.
- [ ] Mọi sơ đồ có `.check.json` không lỗi với `min_font_measured: true`. `diagram_body_check.py` thoát 0 với thân bài, và Claude đã đọc mọi chuỗi `can_doc`. Nguồn lỗi: site gtvseo 19/10, AI27 "nullpx đạt", AI19 "Có schema" trái thân bài.
- [ ] Mọi video lời chứng thực có `speaker_entity` trùng entity của trang và `speaker_evidence` có mốc giây. Nguồn lỗi: site gtvseo 19/10, transcript cho thấy người nói trong video trang chủ là học viên của brand khác.
- [ ] Video nhúng bằng facade, có VideoObject cho video sở hữu public hoặc unlisted.
- [ ] Slot chờ việc bên ngoài ghi rõ ai làm và cần gì.

## Output

- `media_plan.json`, `slot_video_nn.jsonl`, `images.jsonl`, bảng slot cho người duyệt.
- Sơ đồ WebP và `.check.json`, `body_check.json`, `claims.jsonl`, ảnh AI đã watermark, clip MP4.
- mu-plugin media và `videos.json`.

## Gate

- Không chèn media lên production khi chưa có người duyệt.
- Không dùng ảnh hay lời chứng thực của khách khi chưa có đồng ý.
- Không dùng ảnh AI thay ảnh người thật.
- Không tạo ảnh qua nhà cung cấp mà dự án không cho phép.
- Không chèn sơ đồ khi `.check.json` hoặc `diagram_body_check.py` còn lỗi, hoặc còn chuỗi `can_doc` chưa đọc.
- Không nhúng video lời chứng thực khi chưa kiểm người nói thuộc đúng entity của trang.

## Anti-patterns

- Chọn video theo top 1 của embedding ở trang dịch vụ mà không đọc mô tả video.
- Một video lặp ở nhiều trang chỉ để lấp slot.
- Sơ đồ AI có chữ tiếng Việt sai dấu.
- Nhúng iframe YouTube trực tiếp ở màn hình đầu.
- Coi "nullpx" hoặc chữ nhỏ nhất không đo được là đạt.
- Chèn sơ đồ vì đủ chuỗi bắt buộc mà không so với thân bài.
- Chọn video lời chứng thực theo tên file hay tiêu đề mà không nghe người nói.
- Dựng trang mới bằng ảnh của trang chủ rồi ghi "không cần thêm ảnh".

## Changelog

- v1.1 (2026-10-25): media-7 và media-3 (mục ảnh trùng giữa trang). Sửa lỗi `minFont` null ở `diagram_render.mjs` (thêm `diagram_checks.mjs`). Thêm `diagram_body_check.py` so chữ sơ đồ với thân bài (chuỗi nguyên văn vẫn so chiều phủ định). Luật 8 kiểm entity người nói của video lời chứng thực, luật 9 và `check --used` chặn ảnh trùng giữa trang. Thêm `tests/test_diagram.py`, `evals/cases.yaml`.
- v1.0 (2026-10-19): bản đầu, gom từ kế hoạch media của một site nội bộ (18/10). Lượt thử 19/10: `media_match.py nn` tái tạo bảng top 8 cũ 83/83 slot (cosine lệch 0); `check` xác nhận không video nào quá 2 trang và bắt 1 slot thiếu caption; `diagram_render.mjs` render lại 3 sơ đồ cho cùng kết quả kiểm và cùng dung lượng.
