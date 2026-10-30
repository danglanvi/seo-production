---
name: image-seo-optimize
description: "Tối ưu SEO ảnh ĐÃ CÓ: tên file, alt, caption, metadata, performance từng ảnh (size tier, AVIF/WebP, lazy/LCP, CLS), đổi tên ảnh đã đăng kèm 301, nén lại theo SSIM, kiểm alt mọi biến thể. Use when: 'tối ưu ảnh cho bài [X]', 'đổi tên ảnh trên site', 'nén lại ảnh', 'sửa alt ảnh'."
metadata:
  version: "1.3"
---

# Image SEO Optimize — Semantic (bulk)

Tối ưu hàng loạt ảnh **đã có** cho 1 bài viết: filename + alt + caption + metadata keywords + technical, theo chuẩn semantic của wiki. Nối tiếp `media-brief` (brief → designer làm ảnh → **skill này tối ưu trước khi upload**).

## Phân vai

| Việc | Skill |
|---|---|
| Tối ưu ảnh đã có (tên, alt, caption, metadata, technical) | ✅ Skill này |
| Work order cho designer khi chưa có ảnh | `media-brief` |
| Chọn media cho từng mục (video sở hữu, ảnh thật, sơ đồ bằng code), media plan, YouTube facade | `semantic-media` |
| Đo alt có tả đúng ảnh, ảnh có khớp mục chứa nó, so màn đầu với trang được AI trích | `visual-serp-lab` |
| Generate ảnh brand | `brand-image-gen-gtv-tag` |
| Audit layout/visual toàn trang | `visual-semantic-seo` + `sop/07` |
| Chấm điểm onpage tổng (P19-P20 nằm trong đó) | `seo-onpage` |
| Performance tầng SITE (CWV toàn trang, cache/CDN, image sitemap) | `technical-seo-audit` — skill này chỉ lo performance PER-IMAGE (size tier, format, lazy/LCP, CLS attribute) |

## Input

**Mode A — Folder (chính):** `$FOLDER` — tên folder = tên/slug bài viết; ảnh nằm trong; có thể kèm file text bài viết (`.md/.docx/.txt`).
**Mode B — Folder + bài rời:** `$FOLDER` + `$ARTICLE_PATH` (draft trong pipeline hoặc file bất kỳ).
**Mode C — Google Docs URL (ít dùng):** đọc text bài qua URL; ảnh trong Docs KHÔNG tải tự động được → yêu cầu user tải ảnh về 1 folder rồi chạy Mode A. Nếu chỉ cần GỢI Ý (không đụng file) → làm việc trên mô tả vị trí ảnh trong docs.

**Mode D — Ảnh đã đăng trên site:** ảnh đã lên web với tên thiếu ngữ cảnh, cần đổi tên mà không vỡ link. Cần quyền server hoặc dev của site. Đọc `references/doi-ten-anh-da-dang.md` rồi chạy theo file đó. Bước 3 vẫn dùng để đặt tên mới.

**Optional:** `$KEYWORD` (target keyword — thiếu thì suy từ tên folder/H1, flag inferred) · `$SECONDARY_KEYWORDS` · `$APPLY` (`plan-only` default | `apply` — thực thi rename + ghi metadata).

## Quy trình 6 bước

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,cwebp,pillow?,numpy?,ssh?,wp-cli?,jev?,gemma?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

### Bước 0 — Context
1. Đọc bài viết (file trong folder / `$ARTICLE_PATH` / Docs URL): lấy **Central Entity, target keyword, heading tree, số liệu đắt**.
2. Xác định feature image candidate + bộ keyword phân bổ: feature = keyword volume cao nhất; ảnh sau = keyword phụ/semantic (P19) — **không 2 ảnh trùng keyword chính**.
3. Không có bài text → vẫn chạy được từ tên folder + nội dung ảnh, flag "context inferred — alt/caption cần Vincent review".

### Bước 1 — Inventory & đọc ảnh
`ls` folder → bảng inventory (tên cũ, định dạng, dung lượng, kích thước — dùng `sips -g pixelWidth -g pixelHeight`). **Read từng ảnh** để hiểu nội dung THẬT (không đoán từ tên cũ) — ảnh chụp gì, có chữ/số liệu gì trong ảnh (OCR), là diagram/screenshot/photo/infographic.

### Bước 2 — Map ảnh ↔ vị trí trong bài
Ảnh đặt CẠNH text liên quan (SOP07 B4): map từng ảnh vào heading phù hợp nhất theo nội dung ảnh. Ảnh không khớp heading nào → flag "thừa/lạc chủ đề" (đề xuất bỏ hoặc cần heading mới). How-to → ảnh step đánh số theo thứ tự bước.

### Bước 3 — Đặt tên + alt + caption + keywords (bảng chính)

Per ảnh, sinh đủ 5 trường theo chuẩn:

| Trường | Chuẩn | Nguồn |
|---|---|---|
| **Filename** | không dấu, chữ thường, gạch nối, **≤3-5 cụm** mô tả entity; tên riêng viết đủ, tính là một cụm (`logo-dai-hoc-lac-hong`, không `lac-hong`); ảnh feature tả chủ đề bài nên thường gần keyword chính; không đặt keyword mà ảnh không thể hiện; nhất quán chain Title→URL→Image URL | P19 · SOP07 B4 |
| **Alt text** | **Tả đúng nội dung ảnh**, công thức **Entity + Attribute + Action** ("Kỹ thuật viên lắp đèn led panel âm trần Rạng Đông 600x600"); độ dài theo nội dung ảnh, không có ngưỡng số từ (logo, icon ngắn hơn ảnh minh hoạ); feature alt = short-form H1; cụ thể — không generic, không nhồi keyword | P20 · L4 7.5 |
| **Caption** | **≠ Alt** — thông tin bổ sung/ngữ cảnh; số liệu xuất hiện trong ảnh phải lặp lại ở caption (OCR-legible principle) | P20 · SOP07 B4 |
| **Metadata keywords** | 5-10 term: entity chính + attribute + 2-3 semantic terms + brand (IPTC Keywords; Title/Description metadata = alt rút gọn + caption) | P8/P19 |
| **Placement** | heading đích + ghi chú (cạnh đoạn nào, trước/sau số liệu nào) | Bước 2 |

### Bước 4 — Technical pass
Per ảnh: định dạng (format ladder — Bước 4c; baseline `.webp` > jpg > png), dung lượng (baseline <150KB — ngưỡng chi tiết theo vị trí ở Bước 4c), kích thước (inline max 1200px; ảnh đại diện xem Discover — Bước 4c), `loading="lazy"` dưới fold (luật đầy đủ Bước 4c), width/height attribute khi nhúng (chống CLS + WRS không fetch ảnh khi có dimensions — Splitt). Đo bằng `sips`; convert/nén chỉ khi `$APPLY=apply` và tool có sẵn (kiểm `cwebp`, `sips`). Feature image: nhắc schema `ImageObject` + `primaryImageOfPage` cho dev/CMS.

### Bước 4b — Machine-gaze pass (bổ sung 16/07/2026 — nguồn: [[sources/image-seo-multimodal-ai-jessier]])
Multimodal models cắt ảnh thành visual tokens và OCR chữ trong ảnh — chất lượng pixel là điều kiện máy đọc đúng. Check per ảnh (label: benchmark tham khảo từ tài liệu OCR công nghiệp + papers, chưa có ngưỡng chính chủ Google):
- **Chữ trong ảnh**: cao ≥30px, contrast ≥40 giá trị grayscale, không font stylized dễ nhầm (l↔1, b↔8), không glare/bóng — fail thì flag "OCR risk" + đề xuất re-export.
- **Verbalization**: số liệu/claim quan trọng trong ảnh phải được lặp lại bằng text (caption/body) — không có thông tin chỉ-tồn-tại-trong-pixel.
- **Co-occurrence** (khi audit ảnh sản phẩm/lifestyle): object xung quanh chủ thể kể đúng câu chuyện persona/giá trị chưa? (Vision API `OBJECT_LOCALIZATION` trả object + MID Knowledge Graph khi cần audit sâu.)
- **Face/emotion** (ảnh có người, chủ đề cảm xúc): mặt rõ, đủ sáng, chính diện (Vision API: detectionConfidence ≥0.90 lý tưởng, <0.60 = sentiment thành noise; target emotion đạt LIKELY+).
- **Originality**: ảnh gốc > stock (WebDetection trả fullMatchingImages — ảnh xuất hiện sớm nhất được credit origin; label interpretation).

### Bước 4c — Performance pass (bổ sung 19/07/2026 — INTEGRATE từ gap-audit claude-seo)
Lớp PERFORMANCE per-image — không lấn semantic (Bước 3) và machine-gaze (Bước 4b). Performance tầng site (CWV toàn trang, cache/CDN) → route `technical-seo-audit`.

**1. File-size tiers theo vị trí ảnh** (label GTV baseline — điều chỉnh được theo dự án, ghi tier đã áp vào bảng output):

| Vị trí | Ngưỡng dung lượng | Ghi chú |
|---|---|---|
| Hero / above-fold (LCP candidate) | ≤100KB (lý tưởng ≤80KB AVIF/WebP) | Ảnh này quyết định LCP |
| Inline trong body | ≤150KB (= chuẩn P20 hiện hành) | |
| Thumbnail / icon / avatar | ≤30KB | |

Format ladder: **AVIF → WebP → JPEG fallback** (nhúng bằng `<picture>` + `<source type>`); PNG chỉ giữ cho screenshot/diagram cần lossless hoặc transparency. Đo bằng `sips`; convert/nén chỉ khi `$APPLY=apply` và có tool (`cwebp`, `avifenc`, `sips`).

**2. Lazy-load rules:** dưới fold → `loading="lazy"` + `decoding="async"`. Hero/above-fold → **KHÔNG lazy** (delay LCP) + `fetchpriority="high"` cho DUY NHẤT ảnh LCP (gắn nhiều ảnh = mất tác dụng ưu tiên). Ảnh sát fold không chắc trên/dưới → không lazy (an toàn LCP hơn tiết kiệm vài KB).

**3. CLS prevention:** width/height attribute BẮT BUỘC mọi ảnh nhúng (check ở Bước 4); layout responsive → thêm CSS `aspect-ratio` (hoặc `height:auto` đi cùng width/height attribute) để browser giữ chỗ trước khi ảnh load.

**4. Image-SERP / Discover:** ảnh đại diện (feature) xuất bản **≥1200px** chiều rộng — điều kiện Discover large preview, đi cùng `max-image-preview:large` (mặc định nếu robots meta không hạn chế); khi CMS hỗ trợ, giữ thêm variant tỷ lệ 16:9 / 4:3 / 1:1 cho `ImageObject` schema. Ngoại lệ ≥1200px CHỈ cho feature/hero — ảnh inline giữ max 1200px như Bước 4.

### Bước 4d — Nén lại ảnh đã đăng và kiểm alt ở mọi biến thể (bổ sung 27/10/2026)
Đọc `references/nen-lai-ssim-va-alt-bien-the.md` khi `$APPLY=apply` nén ảnh đã có trên site, hoặc khi sửa alt của ảnh trên trang đang chạy.
- Nén lại: giữ SSIM luma của bản mới so với file đang phục vụ từ 0,98 cho ảnh có chữ hoặc logo, từ 0,97 cho ảnh chụp thật. Dùng `scripts/webp_recompress.py`. Chỉ ghi khi file nhỏ hơn ít nhất 8%. Báo lợi ích là byte, không hứa điểm PSI.
- Ảnh có alpha: đo SSIM trên nền thật của trang bằng `scripts/ssim_luma.py --bg`. Nền đen hoặc trắng cho số thấp hơn.
- Bản ảnh theo cỡ hiển thị: không tạo bản rộng hơn nguồn. Cách đo cỡ và viết `srcset`, `sizes` nằm ở `wp-pagespeed` `references/checklist-theo-lop.md` lớp 3.
- Alt: tìm mọi nơi in alt (attachment và chuỗi cứng trong template), sửa hết, rồi chạy `scripts/alt_variants.py` cho khách desktop, khách mobile và Googlebot smartphone.

### Bước 5 — Apply hoặc Plan

- **`plan-only` (default):** xuất bảng mapping đầy đủ (tên cũ → tên mới | alt | caption | keywords | placement | technical note) dạng markdown + CSV để dán vào sheet/CMS. KHÔNG đụng file.
- **`apply` (cần Vincent confirm bảng trước):** rename file theo plan (`mv`), ghi metadata nếu có `exiftool` (máy hiện chưa cài — đề xuất `brew install exiftool`; không có thì chỉ rename + giao bảng metadata để CMS nhập). Ghi log old→new để revert được. Ảnh đã đăng trên site: sửa alt hoặc nén file xong thì chạy Bước 4d trước khi báo xong.
- **Mode D:** bảng old→new là bảng 301 JSON. Áp theo `references/doi-ten-anh-da-dang.md`: staging trước, 301 bằng `templates/mu-plugin-301-anh.php`, cách ly file cũ bằng `scripts/anh_cach_ly.sh`, kiểm URL cũ 301 → 200.

**Output report:**
```markdown
# Image SEO — [bài/slug]
**Mode:** A/B/C · **Ảnh:** n · **Keyword:** … (inferred?)
## Bảng tối ưu (per ảnh): cũ → mới | alt | caption | keywords | heading đích | technical | performance (size-tier ✅/❌ · format ladder · lazy/LCP · width-height/CLS · Discover ≥1200px)
## Cảnh báo: ảnh lạc chủ đề / trùng keyword / thiếu ảnh cho heading X (đề xuất bổ sung → media-brief)
## Apply log (nếu chạy apply)
```

## Behavior Gates

- **#1 Think Before:** báo mode + số ảnh + keyword + `$APPLY` mode trước khi chạy.
- **#2 Evidence:** alt/caption phải khớp nội dung THẬT của ảnh (đã Read) — không bịa nội dung ảnh chưa xem.
- **#3 Surgical:** default plan-only; `apply` chỉ sau khi Vincent duyệt bảng; không xóa ảnh, không sửa bài viết.
- **#4 Goal-driven:** mọi ảnh trong folder có mặt trong bảng (kể cả ảnh bị flag bỏ).

## Anti-patterns

- Alt nhồi keyword / alt = filename / alt generic ("hình ảnh minh họa").
- Caption copy nguyên alt (P20: caption = info bổ sung).
- Đặt tên ảnh theo keyword mà nội dung ảnh không thể hiện keyword đó (mismatch = nhiễu semantic).
- 2+ ảnh cùng bài trùng keyword chính trong filename (dilute — phân bổ keyword phụ).
- Rename mà quên xuất bảng old→new (vỡ reference nếu bài đã nhúng ảnh).
- Stock photo generic cho nội dung core (W8/T2-P5: original media = E-E-A-T signal).
- Lazy-load ảnh hero/LCP, hoặc gắn `fetchpriority="high"` cho nhiều ảnh cùng trang (mất tác dụng ưu tiên, delay LCP).
- Nén ảnh đạt size tier nhưng vỡ chữ/số liệu trong ảnh — performance không được phá machine-gaze (Bước 4b OCR risk). Đo SSIM theo loại ảnh (Bước 4d).
- Đo SSIM ảnh có alpha trên nền đen hoặc trắng khi trang dùng nền màu: cổng 0,97 cho kết quả khác nhau theo nền (Bước 4d).
- Sửa alt của attachment rồi báo xong: chuỗi cứng trong template vẫn in alt cũ ở một biến thể (Bước 4d).
- Đổi tên ảnh đã đăng mà không 301 URL cũ, hoặc xoá file tên cũ thay vì cách ly.
- Chỉ sửa tên ảnh trong DB khi trang dựng từ nguồn build: lần build sau đưa tên cũ trở lại.

## Reference

- Chuẩn: [[sources/onpage-checklist-final-gtv]] P19-P20 · [[Layer 4 Onpage]] 7.5 · `sop/07-visual-semantic` Bước 4 (chain Title→URL→Description→Image URL→Alt, featured image = short H1, ImageObject schema) · tier-1 W8/W19
- Upstream: `media-brief` (spec ảnh trước khi làm) · Downstream: `seo-onpage` (chấm P19-P20 sau khi lên trang)
- Performance ngưỡng: web.dev/articles/vitals (LCP/CLS) · developers.google.com/search/docs/appearance/google-discover (large image ≥1200px + max-image-preview:large) — ranh giới site-wide: `technical-seo-audit`

## Changelog

- **v1.3 (2026-10-27):** nguồn: hai lượt production trên một site WordPress agency mẫu (nén 35 banner case study; sửa ảnh hero và alt 3 trang dịch vụ), đều có kiểm độc lập. Thêm Bước 4d và `references/nen-lai-ssim-va-alt-bien-the.md`: ngưỡng SSIM luma theo loại ảnh (0,98 ảnh có chữ hoặc logo, 0,97 ảnh thật; 32/35 banner, -20,4% byte); ảnh có alpha đo trên nền thật (0,9737 so với 0,9616); không tạo bản rộng hơn nguồn; alt kiểm ở khách desktop, khách mobile và Googlebot smartphone vì alt đến từ attachment và chuỗi cứng trong template (9/9). Script mới `ssim_luma.py`, `webp_recompress.py`, `alt_variants.py`; test `scripts/tests/test_image_tools.py` chạy tại máy: đạt, gồm ca nền alpha và ca UA mobile in alt cũ. Bước 0 thêm `numpy?`. Rút `description` từ 373 xuống dưới 280 ký tự để qua ca cấu trúc. Chưa thử và chưa vào skill: đổi `sizes` của banner theo cỡ hiển thị (`chua-thu.md`).
- **v1.2.2 (2026-10-19):** bảng phân vai trỏ sang `semantic-media` (chọn media theo mục) và `visual-serp-lab` (đo alt khớp ảnh, ảnh khớp mục).
- **v1.2.1 (2026-10-19):** alt tả đúng nội dung ảnh, bỏ ngưỡng 8-15 từ; tên file ảnh feature tả chủ đề bài, không đặt keyword mà ảnh không thể hiện (khớp P19, P20 mới của `seo-onpage`).
- **v1.2 (2026-10-18):** thêm Mode D đổi tên ảnh đã đăng trên site, từ đợt đổi tên 271 ảnh trên một site WordPress (284 URL cũ 301, không link vỡ). Reference `doi-ten-anh-da-dang.md`, mẫu `templates/mu-plugin-301-anh.php`, script `scripts/anh_cach_ly.sh` (đã chạy thử cách ly và trả lại trên server). Luật tên: tên riêng viết đủ, tính là một cụm.
- **v1.1 (2026-07-19):** INTEGRATE từ gap-audit claude-seo (repo 11.7k★, đã phân loại INTEGRATE): thêm **PERFORMANCE layer per-image** (Bước 4c, không lấn semantic hiện có) — (1) file-size tiers theo vị trí: hero/above-fold ≤100KB · inline ≤150KB · thumbnail ≤30KB (label GTV baseline, điều chỉnh được) + format ladder AVIF→WebP→JPEG fallback qua `<picture>`; (2) lazy-load rules: below-fold lazy + `decoding=async`, hero KHÔNG lazy, `fetchpriority=high` duy nhất cho ảnh LCP; (3) CLS prevention: width/height bắt buộc + CSS `aspect-ratio`; (4) Discover/Image-SERP: feature image ≥1200px + variant 16:9/4:3/1:1 cho ImageObject. Output thêm cột performance cạnh cột semantic; Phân vai thêm ranh giới performance site-wide → `technical-seo-audit`; 2 anti-patterns mới (lazy hero/multi-fetchpriority, nén vỡ OCR).
- **v1.0:** khởi tạo semantic layer (P19-P20, L4 7.5, SOP07 B4) + machine-gaze pass 4b (16/07/2026).
