---
name: image-seo-optimize
description: "Tối ưu SEO hình ảnh theo semantic (bulk) — đặt tên file, alt text, caption, metadata keywords cho ảnh ĐÃ CÓ + performance layer per-image (file-size tier theo vị trí, format ladder AVIF→WebP→JPEG, lazy-load/LCP, CLS, Discover ≥1200px). Use when: (1) 'tối ưu ảnh cho bài [X]', 'tối ưu bulk hình ảnh', 'đặt tên + alt cho folder ảnh'; (2) user đưa folder ảnh (tên folder = tên bài viết, có thể kèm file text bài trong folder); (3) user đưa Google Docs URL chứa bài + ảnh; (4) cần gợi ý alt text/filename/metadata chuẩn semantic cho ảnh trước khi upload CMS. Chuẩn áp dụng: P19-P20 (onpage checklist GTV), Layer 4 7.5 (Entity+Attribute+Action), SOP 07 Visual Semantic B4. KHÔNG dùng cho: brief ảnh cho designer khi CHƯA có ảnh (→ media-brief), generate ảnh (→ brand-image-gen-gtv-tag), audit layout tổng thể (→ visual-semantic-seo), audit CWV/performance tầng site (→ technical-seo-audit)."
metadata:
  version: "1.1"
---

# Image SEO Optimize — Semantic (bulk)

Tối ưu hàng loạt ảnh **đã có** cho 1 bài viết: filename + alt + caption + metadata keywords + technical, theo chuẩn semantic của wiki. Nối tiếp `media-brief` (brief → designer làm ảnh → **skill này tối ưu trước khi upload**).

## Phân vai

| Việc | Skill |
|---|---|
| Tối ưu ảnh đã có (tên, alt, caption, metadata, technical) | ✅ Skill này |
| Work order cho designer khi chưa có ảnh | `media-brief` |
| Generate ảnh brand | `brand-image-gen-gtv-tag` |
| Audit layout/visual toàn trang | `visual-semantic-seo` + `sop/07` |
| Chấm điểm onpage tổng (P19-P20 nằm trong đó) | `seo-onpage` |
| Performance tầng SITE (CWV toàn trang, cache/CDN, image sitemap) | `technical-seo-audit` — skill này chỉ lo performance PER-IMAGE (size tier, format, lazy/LCP, CLS attribute) |

## Input

**Mode A — Folder (chính):** `$FOLDER` — tên folder = tên/slug bài viết; ảnh nằm trong; có thể kèm file text bài viết (`.md/.docx/.txt`).
**Mode B — Folder + bài rời:** `$FOLDER` + `$ARTICLE_PATH` (draft trong pipeline hoặc file bất kỳ).
**Mode C — Google Docs URL (ít dùng):** đọc text bài qua URL; ảnh trong Docs KHÔNG tải tự động được → yêu cầu user tải ảnh về 1 folder rồi chạy Mode A. Nếu chỉ cần GỢI Ý (không đụng file) → làm việc trên mô tả vị trí ảnh trong docs.

**Optional:** `$KEYWORD` (target keyword — thiếu thì suy từ tên folder/H1, flag inferred) · `$SECONDARY_KEYWORDS` · `$APPLY` (`plan-only` default | `apply` — thực thi rename + ghi metadata).

## Workflow 6 bước

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
| **Filename** | không dấu, chữ thường, gạch nối, **≤3-5 từ** mô tả entity; feature = keyword chính; ảnh sau = keyword phụ/semantic; nhất quán chain Title→URL→Image URL | P19 · SOP07 B4 |
| **Alt text** | **8-15 từ**, công thức **Entity + Attribute + Action** ("Kỹ thuật viên lắp đèn led panel âm trần Rạng Đông 600x600"); feature alt = short-form H1; cụ thể — không generic, không nhồi keyword | P20 · L4 7.5 |
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

### Bước 5 — Apply hoặc Plan

- **`plan-only` (default):** xuất bảng mapping đầy đủ (tên cũ → tên mới | alt | caption | keywords | placement | technical note) dạng markdown + CSV để dán vào sheet/CMS. KHÔNG đụng file.
- **`apply` (cần Vincent confirm bảng trước):** rename file theo plan (`mv`), ghi metadata nếu có `exiftool` (máy hiện chưa cài — đề xuất `brew install exiftool`; không có thì chỉ rename + giao bảng metadata để CMS nhập). Ghi log old→new để revert được.

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
- Nén ảnh đạt size tier nhưng vỡ chữ/số liệu trong ảnh — performance không được phá machine-gaze (Bước 4b OCR risk).

## Reference

- Chuẩn: [[sources/onpage-checklist-final-gtv]] P19-P20 · [[Layer 4 Onpage]] 7.5 · `sop/07-visual-semantic` Bước 4 (chain Title→URL→Description→Image URL→Alt, featured image = short H1, ImageObject schema) · tier-1 W8/W19
- Upstream: `media-brief` (spec ảnh trước khi làm) · Downstream: `seo-onpage` (chấm P19-P20 sau khi lên trang)
- Performance ngưỡng: web.dev/articles/vitals (LCP/CLS) · developers.google.com/search/docs/appearance/google-discover (large image ≥1200px + max-image-preview:large) — ranh giới site-wide: `technical-seo-audit`

## Changelog

- **v1.1 (2026-07-19):** INTEGRATE từ gap-audit claude-seo (repo 11.7k★, đã phân loại INTEGRATE): thêm **PERFORMANCE layer per-image** (Bước 4c, không lấn semantic hiện có) — (1) file-size tiers theo vị trí: hero/above-fold ≤100KB · inline ≤150KB · thumbnail ≤30KB (label GTV baseline, điều chỉnh được) + format ladder AVIF→WebP→JPEG fallback qua `<picture>`; (2) lazy-load rules: below-fold lazy + `decoding=async`, hero KHÔNG lazy, `fetchpriority=high` duy nhất cho ảnh LCP; (3) CLS prevention: width/height bắt buộc + CSS `aspect-ratio`; (4) Discover/Image-SERP: feature image ≥1200px + variant 16:9/4:3/1:1 cho ImageObject. Output thêm cột performance cạnh cột semantic; Phân vai thêm ranh giới performance site-wide → `technical-seo-audit`; 2 anti-patterns mới (lazy hero/multi-fetchpriority, nén vỡ OCR).
- **v1.0:** khởi tạo semantic layer (P19-P20, L4 7.5, SOP07 B4) + machine-gaze pass 4b (16/07/2026).
