# Upgrade spec — wp-publish-workflow-kit (gửi team kit)

> Đối chiếu kit `github.com/LongDZ1204/wp-publish-workflow-kit` với chuẩn wiki Semantic SEO A-Z + P-series GTV, ngày 2026-08-29. Người quyết policy: Vincent. Mỗi mục dưới đây có thể mở thành 1 GitHub issue. Kit giữ nguyên triết lý fail-closed / approval hash / verify kép — các nâng cấp KHÔNG được nới lỏng 3 contract đó.

## A. Policy — BLOCKING (chốt 2026-08-29)

| # | Việc | Chi tiết |
|---|---|---|
| A1 | **Đảo chiều strong-to-b** | Policy GTV: mọi nhấn mạnh dùng `<strong>`, `<b>` = 0. Sửa `tools/strong-to-b` + `wp_strong.py` thành transform có policy: `preserve-strong` (mặc định — không đổi gì, chỉ report count) và thêm mode `b-to-strong` (normalize ngược cho site cũ). Bỏ mode `strong-to-b` hoặc giữ sau flag tường minh cho site ngoài GTV. Đồng thời sửa mâu thuẫn docs: `CLAUDE.md` P3 bắt chạy blanket cả AUDIT nhưng `wp-rest-notes.md` cấm — chốt: AUDIT không bao giờ transform blanket. |
| A2 | **Slugify tiếng Việt** | `slugify()` trong `image_prepare.py` không transliterate: "hình ảnh" → `h-nh-nh`. Thêm bước bỏ dấu (NFD strip + đ→d) trước khi thay ký tự. Có test case tiếng Việt. |

## B. Enforce rule SEO đang chỉ nằm trên giấy (standards.md có, code không)

| # | Việc | Chuẩn GTV đối chiếu |
|---|---|---|
| B1 | Gate `width`/`height` attribute trên mọi `<img>` trong `wp_gate.py`; `wp_doc_export.py` ghi kích thước thật từ manifest vào tag | P20, VS-13 (CLS) |
| B2 | Gate `loading="lazy"` cho ảnh body + CẤM lazy ảnh đầu tiên/hero; hero thêm `fetchpriority="high"` (đúng 1 ảnh) | P20 + tier ảnh GTV |
| B3 | Tier file-size theo vị trí thay vì 1 ngưỡng 150KB: hero ≤100KB · inline ≤150KB · thumbnail ≤30KB (config trong `publish-context.json`) | image-seo-optimize skill v1.1 |
| B4 | Validate alt 8-15 từ (warning-level trong gate report, vẫn fail-closed nếu thiếu alt như hiện tại) | P20 |
| B5 | Check độ dài SEO title 50-60 ký tự + meta description 150-160 ký tự trước push (Yoast/RankMath field) | P2, P3 |
| B6 | PNG: thêm đường nén thật (quantize/palette) hoặc auto-fallback WebP khi vượt ngưỡng, thay vì fail cứng `IMG-SIZE` không lối thoát | thực dụng vận hành |

## C. Sửa bất đối xứng & bug kỹ thuật

| # | Việc | Chi tiết |
|---|---|---|
| C1 | **AUDIT route: thêm approval hash** — hash trên (`edits.json` + snapshot raw + meta.json), `wp_push_verify.py` nhận `--approval-hash` như NEW | Hiện approval AUDIT chỉ là "gật bằng lời" |
| C2 | **So `modified` trước push** — `wp_push_verify.py` đọc `.meta.json`, fresh fetch, lệch `modified` → STOP (race condition người khác sửa bài giữa fetch và push) | CLAUDE.md P5 đã yêu cầu nhưng chưa có code |
| C3 | **Backup immutable** — `wp_fetch.py` tự thêm timestamp vào tên backup, không ghi đè `_audit-snapshots/` | project-folders.md tự nhận "immutable" |
| C4 | **Env var override** — `load_credential()` khi có `WP_URL` env + `--site` được truyền: assert domain env khớp site_key, lệch → STOP thay vì ghi nhầm site | fail-closed đúng nghĩa |
| C5 | `wp_doc_export.py` **đừng drop im lặng** block ngoài whitelist (blockquote, iframe, hr, ld+json...) — tối thiểu đếm + báo `DROPPED n block: <tags>` trong output để gate/operator thấy; tốt hơn: whitelist mở rộng blockquote + figure/iframe có approve | P18 (Blockquote chuẩn), SOP 07 B7 |
| C6 | `image_prepare.py` idempotent: chạy lại cùng `--output-dir` → skip file đã có cùng SHA thay vì `IMG-DUP` fail | khớp triết lý resume của kit |
| C7 | Frozen check trong `wp_apply_edits.py`: so **số lần xuất hiện** trước/sau, không chỉ `count >= 1`; structural counts (table/img/iframe) thành assertion so trước/sau | chống edit nhân đôi vùng frozen |

## D. Tích hợp hệ GTV (nice-to-have, sau A-C)

- D1: Hook `internal-link-insertion` đang khai báo trong CLAUDE.md kit nhưng không tồn tại — định nghĩa contract input (link plan JSON: target URL + anchor + vị trí) để skill `internal-linking` của SEO Production đổ vào.
- D2: Nhận `doc-image-map.json` sinh từ bảng output của skill `image-seo-optimize` (filename/alt/caption/metadata đã duyệt) — thống nhất field name 2 bên.
- D3: Cho phép giữ `<script type="application/ld+json">` trong body khi site cần schema per-bài (whitelist có cờ).

## Trạng thái

- [x] Gửi spec cho team kit (Long) — Vincent đã báo 2026-08-29; Long mở issues theo bảng
- [ ] A1-A2 xong → gỡ dòng "bù thủ công" tương ứng trong `02-raw/knowledge/sop/11-publish-wp.md` §4 (vá ở kho gốc wiki trước, re-sync)
