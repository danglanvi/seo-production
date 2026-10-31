---
name: anh-trong-bai
description: "Dựng media trong thân bài trước khi đăng: media plan từ khung [IMG-NN], sơ đồ SVG 2 bản desktop và điện thoại theo màu site, ảnh chụp trang nguồn có tô câu, ảnh AI có watermark, khối tương tác; kiểm chữ, alt, caption, dung lượng rồi chèn vào HTML. Dùng khi bài mới cần hình."
metadata:
  version: "1.1.0"
---

# anh-trong-bai — media trong thân bài

Skill này biến các khung `[IMG-NN]` của bài thành media thật, đúng ngữ cảnh của từng H2. Sơ đồ có chữ dựng bằng SVG inline, nên chữ là text thật mà máy tìm kiếm đọc được và không vỡ dấu tiếng Việt. Màu, font, logo, trần dung lượng lấy từ `web-profile.json` của site (schema: `wp-xuat-ban-bai/references/web-profile.md`).

Gốc đường dẫn là root repo. Script ở `skills/anh-trong-bai/scripts/`:

| File | Việc |
|---|---|
| `media_plan.py tu-md` | Lập `media_plan.json` từ bảng `## Image placeholders` của bài và hộp media brief |
| `media_plan.py kiem` | Kiểm plan: loại, alt, caption, tên file, file có thật, trần KB, ảnh AI không tả người, ảnh không lặp. `--html` đối chiếu khung chờ trong bài |
| `media_plan.py chu-so-do` | Gom chữ của sơ đồ để so với thân bài bằng `diagram_body_check.py` của `semantic-media` |
| `svg_dung.py` | Dựng sơ đồ SVG từ khối `so_do`: 7 kiểu, mỗi sơ đồ 2 bản (khung 760 và 320) |
| `svg_kiem.mjs` | Đo sơ đồ bằng Chrome với font thật: chữ tràn khung, chữ đè chữ, chữ dưới 12 px. Chụp PNG 2x để xem |
| `chup_trang.mjs` | Chụp một vùng trang nguồn: tìm khối chứa đoạn chữ, mở khối thu gọn, tô vàng câu cần nhấn |
| `anh_chu_thich.py` | Ghép, cắt, che, khoanh, ghim số; logo cho ảnh AI; WebP dưới trần KB, metadata nguồn ảnh |
| `chen_media.py` | Thay khung chờ bằng media: SVG 2 bản, `<img>` có kích thước, khối tương tác, YouTube facade |
| `_cdp.mjs` | Hàm Chrome headless dùng chung |

Test, chạy từ `skills/anh-trong-bai/`: `python3 -B tests/test_media_bai.py`. Ca đánh giá: `evals/cases.yaml` (không nạp lúc chạy thật).

## Khi nào dùng

- Bài mới đã humanize, có khung `[IMG-NN]`, cần media trước khi xuất bản bằng `wp-xuat-ban-bai`.
- Bài cũ đăng lại cần sơ đồ, ảnh chụp nguồn hoặc khối tương tác.
- Không dùng để đặt media cho nhiều trang đang chạy, ghép video kênh, kiểm ảnh trùng giữa trang. Dùng `semantic-media`.
- Không dùng để đổi tên, alt, dung lượng ảnh đã đăng. Dùng `image-seo-optimize`.
- Ảnh đại diện: xem `references/anh-dai-dien.md`. Ảnh đại diện không phải media trong thân bài.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Bài `.md` humanize có bảng `## Image placeholders` | repo content `08-humanized/` | lập plan tay theo `references/chon-media.md` |
| Bài HTML có khung chờ | `wp-xuat-ban-bai` Bước 2 | chạy Bước 2 trước |
| Media brief | `07-media-brief/<cluster>/<slug>.md` | dùng cột Mô tả của bảng placeholder |
| `web-profile.json` | `00-context/` hoặc `00-client-context/` | dừng, dựng profile trước |
| URL trang nguồn cho ảnh chụp | nguồn trích trong bài | đổi mục đó sang sơ đồ hoặc bảng |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Script | Dựng SVG, đo chữ bằng Chrome, chụp trang, nén ảnh, kiểm plan, chèn | Dùng. Script là cổng chặn |
| Script `diagram_body_check.py` (`semantic-media`) | So chữ sơ đồ với thân bài | Repo SEO dùng. Repo content không có script này: Claude đọc nhãn với thân bài |
| Jev `chu-dinh` | Dấu tiếng Việt chạm dòng hoặc bị che trên PNG 2x của sơ đồ và ảnh đại diện | Khi `lines_touch` từ 0,6 thì Claude xem vùng chữ phóng 2x |
| Jev `ui-visual` | Soát ảnh chụp trang nguồn: chữ bị cắt, khối che | Claude xem ảnh khi nhãn khác "không" |
| EmbeddingGemma 2 | Ghép video kênh với H2 | Qua `semantic-media` khi bài cần video sở hữu |
| Claude | Chọn loại media cho từng khung, viết spec sơ đồ, chọn câu cần chụp, viết alt và caption, xem mọi ảnh trước khi chèn | Dùng |

Repo content không có `tools/ai-assist/`. Ở đó Claude xem PNG thay cho Jev.

## Luật media

1. Thứ tự ưu tiên: video sở hữu, ảnh chụp nguồn thật, ảnh thật, sơ đồ bằng code, ảnh AI.
2. Sơ đồ có chữ dựng bằng SVG. Nhãn lấy từ chữ thật của bài. Ảnh AI không chứa chữ.
3. Không dùng ảnh AI cho người, đội ngũ, văn phòng, khách hàng. `media_plan.py kiem` báo LOI.
4. Ảnh AI có logo watermark của site: góc dưới phải, rộng 9%, mờ 0,55.
5. Ảnh chụp trang nguồn ghi tên trang và ngày chụp trong caption. Che tên khách, domain, email bằng khối màu đặc khi luật site yêu cầu.
6. Alt tả nội dung ảnh, không mở bằng "ảnh", "hình". Caption nói điều người đọc rút ra, không lặp alt.
7. Mỗi khung một media. Một ảnh dùng ở 2 chỗ phải có `allow_reuse` kèm lý do.
8. Đồ hoạ dưới `media.kb_do_hoa` KB, ảnh chụp và ảnh AI dưới `media.kb_anh_chup` KB.
9. Media quan trọng có thực thể là brand, sản phẩm hoặc công cụ phải có logo thật hoặc linh vật chính thức của brand đó. Media quan trọng gồm ảnh mở bài, sơ đồ tổng quan, infographic. Ví dụ: nút "Claude" trong sơ đồ mang logo Claude. Lấy logo theo `featured-image-seo` luật 11b, không vẽ lại.
10. Ảnh chụp màn hình và khung cắt từ video:
    - Cắt sát vùng cần nhìn. Chữ trong ảnh phải cao từ 11 px khi ảnh hiện ở cột bài 680 px.
    - Khoanh hoặc ghim số đúng chỗ người đọc cần nhìn bằng `anh_chu_thich.py`. Caption gọi đúng số ghim.
    - Có ảnh chụp lại được ở độ phân giải cao hơn thì chụp lại, không dùng khung video mờ.
    - Kết quả trước và sau đặt cạnh nhau, cùng khung, cùng điều kiện đo, ghi ngày của mỗi bên.

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,pillow,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Nếu repo không có `tools/capabilities.py` (repo content), kiểm tay: `python3 -c "import PIL"`, `node --version` (từ 22), Chrome có trong `/Applications/Google Chrome.app` hoặc biến `CHROME`. Thiếu Chrome thì không chụp trang, không đo sơ đồ: dừng và báo người vận hành.

1. Lập plan:

   ```bash
   python3 skills/anh-trong-bai/scripts/media_plan.py tu-md <bai.md> --out <thư mục bài>/media_plan.json --brief <media brief.md>
   ```

   Script không ghi đè plan đã có. Bảng placeholder của bài humanize mới hơn brief, nên alt của bảng được giữ, alt của brief chỉ lưu ở `alt_brief`.
2. Với từng mục, chọn loại và viết spec theo `references/chon-media.md`. Viết `caption` cho mọi mục.
3. Dựng sơ đồ theo `references/so-do-spec.md`:

   ```bash
   python3 skills/anh-trong-bai/scripts/svg_dung.py <plan> --profile <profile> --out <thư mục bài>/media
   node skills/anh-trong-bai/scripts/svg_kiem.mjs <plan> --profile <profile>
   ```

   - `svg_kiem.mjs` thoát 1 thì sửa spec (rút chữ, đổi kiểu, `mot_hang`) rồi dựng lại.
   - Mở mọi PNG trong `media/_kiem/`, cả bản `-m`.
   - So chữ với thân bài. Repo SEO chạy `media_plan.py chu-so-do <plan> --out specs-chu.json`, rồi `python3 skills/semantic-media/scripts/diagram_body_check.py --specs specs-chu.json --body <bai.html>`. Đọc mọi dòng `nguoc` và `can_doc`.
4. Chụp trang nguồn:

   ```bash
   node skills/anh-trong-bai/scripts/chup_trang.mjs --url <URL> --chua "<đoạn chữ trong khối>" --to "<câu cần tô>" --rong 640 --out <thư mục bài>/media/goc/<tên>.png
   python3 skills/anh-trong-bai/scripts/anh_chu_thich.py <thư mục bài>/media/goc/<tên>.png --le 24 --profile <profile> --alt "<alt>" --nguon chup-man-hinh --out <thư mục bài>/media/<ten_file>.webp
   ```

   - Chụp ở `--rong 640`. Chụp 1000 px thì chữ quá nhỏ khi thu về khung điện thoại.
   - Trang có bản dịch tự chuyển: thêm `?hl=en` hoặc tham số ngôn ngữ vào URL.
   - Nhiều ảnh nguồn cho một khung: truyền nhiều file vào `anh_chu_thich.py`, script ghép dọc.
   - Ghi `src` vào plan.
5. Ảnh AI (phương án cuối): theo `references/anh-ai.md`. Ghép logo bằng `anh_chu_thich.py --nguon ai`.
6. Khối tương tác: viết HTML theo `wp-xuat-ban-bai/references/khoi-doc-kit.md` vào `media/<tên>.html`, CSS vào `media/<tên>.css`. Ghi `html` và `css` vào plan.
7. Kiểm plan:

   ```bash
   python3 skills/anh-trong-bai/scripts/media_plan.py kiem <plan> --profile <profile>
   ```

8. Chèn vào bài và kiểm khung chờ:

   ```bash
   python3 skills/anh-trong-bai/scripts/chen_media.py <bai.html> <plan>
   python3 skills/anh-trong-bai/scripts/media_plan.py kiem <plan> --profile <profile> --html <bai.html>
   ```

   Chèn lại được nhiều lần: khối đã chèn có comment `<!--m:IMG-NN-->`.
9. Trả bài cho `wp-xuat-ban-bai` Bước 4.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] `svg_kiem.mjs` thoát 0 ở cả bản desktop và bản điện thoại, và đã xem mọi PNG. Nguồn lỗi: pilot 27/10, mũi tên chéo khi đổi hàng, nhãn nhánh đè mũi tên, bản điện thoại thiếu nhãn nhóm.
- [ ] Chữ trên sơ đồ khớp thân bài; mọi dòng `nguoc`, `can_doc` đã đọc. Nguồn lỗi: pilot 27/10, hai nhãn bị xếp `nguoc` vì câu trích tiếng Anh có "no matter how"; đọc câu bằng chứng thì nhãn đúng.
- [ ] Ảnh chụp nguồn đúng khối, có câu được tô, đọc được trên điện thoại. Nguồn lỗi: pilot 27/10, trang devsite tự chuyển bản dịch và giấu đoạn trong khối thu gọn; trang hexdocs ở chế độ tối chụp ra sai cột; ảnh chụp 1000 px không đọc được trên điện thoại.
- [ ] Màu sơ đồ đủ tương phản với chữ trắng. Nguồn lỗi: pilot 27/10, gradient cyan của brand guideline quá sáng, đổi sang màu chính của site.
- [ ] Không có ảnh AI tả người, văn phòng, khách hàng; ảnh AI có logo. Nguồn: luật media của workspace, `media_plan.py kiem` chặn.
- [ ] Alt tả media đã dựng, caption nói điều người đọc rút ra, ảnh chụp ghi nguồn và ngày chụp. Nguồn lỗi: pilot 27/10, alt IMG-04 còn tả "thang bốn tầng" của brief cũ, alt IMG-05 tả "clip" cho sơ đồ tĩnh; bản nháp đã lên site với alt sai.
- [ ] Media quan trọng có brand là thực thể chính mang logo hoặc linh vật thật của brand đó (luật 9). Nguồn lỗi: 31/10/2026, ảnh đại diện và sơ đồ 2 bài Claude Code không có logo Claude; người duyệt yêu cầu bổ sung.
- [ ] Ảnh chụp và khung video cắt sát, chữ đọc được ở cột 680 px, có khoanh hoặc ghim chỗ cần nhìn; ảnh trước và sau đặt cạnh nhau (luật 10). Nguồn lỗi: 31/10/2026, 8 khung video cả màn hình VS Code trong 2 bài tài liệu nội bộ, chữ mờ, người đọc không biết nhìn vào đâu.
- [ ] `media_plan.py kiem --html` thoát 0: bài không còn khung chờ. Nguồn: pilot 27/10, `kiem_bai.py` coi khung chờ còn sót là chuỗi giữ chỗ và chặn đăng.

## Output

- `media_plan.json` đủ trường, `media/*.svg` và `*-m.svg`, `media/*.webp`, `media/goc/` (ảnh chụp gốc), `media/_kiem/` (PNG soát), `svg_kiem.json`.
- Bài HTML đã chèn media, CSS khối tương tác trong `<head>`.

## Gate

- Không chèn sơ đồ khi `svg_kiem.mjs` còn lỗi hoặc chưa xem PNG.
- Không chèn ảnh AI có người, hoặc ảnh AI thiếu logo.
- Không gọi công cụ tạo ảnh ngoài công cụ dự án cho phép. Không có công cụ thì ghi prompt, đặt `trang_thai` là `ready_to_generate`.
- Không chụp trang đang hiện token, key, mật khẩu hay dữ liệu đăng nhập.

## Anti-patterns

- Sơ đồ PNG có chữ thay cho SVG: chữ vỡ dấu, nặng, không đọc được trên điện thoại.
- Dùng chung một SVG cho desktop và điện thoại: khung 760 thu về 390 px làm chữ còn khoảng 8 px.
- Chụp cả trang rồi để người đọc tự tìm câu. Chụp đúng khối và tô câu.
- Ảnh AI minh hoạ cho có, không gắn với ý của H2.
- Caption lặp alt.

## Changelog

- v1.1.0 (2026-10-31): luật media 9 (logo hoặc linh vật của brand trong media quan trọng) và 10 (ảnh chụp, khung video: cắt sát, khoanh hoặc ghim, trước và sau cạnh nhau); 2 dòng tự phản biện. Người duyệt yêu cầu sau vòng góp ý 2 bài tài liệu nội bộ về Claude Code.
- v1.0.1 (2026-10-27): `evals/cases.yaml` 7 ca từ pilot (alt tả brief cũ, nhãn `nguoc` bắt nhầm, chụp trang devsite và hexdocs, ảnh AI có người, thiếu Kie). Kiểu `danh-sach` căn giữa tiêu đề khi thẻ không có mô tả.
- v1.0 (2026-10-27): tạo mới. Pilot bài content-effort trên site mẫu GTV: 4 sơ đồ SVG (khoi, luong 2 kiểu, quyet-dinh) đạt `svg_kiem.mjs` ở 760 và 320 px, 2 ảnh chụp nguồn (Google devsite, hexdocs) có tô câu, 1 khối tự chấm `.calc`, chèn đủ 7 khung.
