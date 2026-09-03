---
name: cro-audit
description: "CRO cho website SEO (WS 13): conversion path theo cụm intent, brief tính năng/UX-UI per section, đọc heatmap-recording (Clarity/Hotjar) → action đo được; chấm CR-01…19. Use when: 'làm công đoạn 34/35/36', 'conversion path <client>', 'đọc heatmap', 'landing có traffic mà không ra lead', 'A/B CTA'."
---

# CRO Audit — traffic SEO phải thành chuyển đổi đo được

Ba deliverable trong `13-cro/`: `<CLIENT>_conversion-path_v<N>.md` (#34, template `conversion-path.md`) · `<CLIENT>_ux-feature-brief-<section>_v<N>.md` (#35, `ux-feature-brief.md`) · `<CLIENT>_heatmap-review-<kỳ>_v<N>.md` (#35/#36, `heatmap-recording-review.md`). Checklist: `02-raw/knowledge/sop/06-self-checklist/tier-1-cro-conversion.md` (CR-01…19, 3 gate) + `tier-1-ux-ui.md` (UX-01…18).

## Luật cứng

1. **Không có tracking = không có CRO.** Gate G1: GA4 events theo loại web (`form_submit`, `click_to_call`, `zalo`, `messenger`; e-commerce thêm `add_to_cart`, `purchase`) gắn xong + verify DebugView **≤ T3** (CR-06/07). Chưa pass → chỉ làm phần A site-wide, không mở B/C.
2. **Chỉ tối ưu trang có traffic + ranking** (CR-08): danh sách landing ưu tiên = traffic cao × ranking tốt × ngách ROI cao — lấy từ GSC/GA4 + hub PSP, duyệt trước khi làm.
3. **1 CTA chính/trang** (CR-10), khớp hành vi tệp khách (Zalo/gọi/form/mua). Mọi đề xuất phải trace về item CR-xx/UX-xx — "cho đẹp", "theo trend" bị cấm (giống luật trạm 04).
4. **Không đụng cấu trúc đã lock** (#11): CRO thay đổi block/CTA/form/trust trong khung structure brief đã duyệt; muốn đổi cấu trúc → quay lại trạm 04, không patch ở đây.
5. **Đọc recording trước khi kết luận**: heatmap cho biết *ở đâu*, recording cho biết *vì sao*. Mỗi finding ≥3 recording hoặc ≥100 session heatmap; ít hơn → ghi "mẫu chưa đủ".

## Ba việc

### #34 Conversion path theo cụm intent (T2→T3)
Từ topical map: mỗi cụm intent (Core thương mại / Outer blog / so sánh-giá / hỗ trợ) → landing vào → bước giữa → điểm chuyển đổi, **≤3 click** (CR-16), không dead-end (CR-17), blog → thương mại đúng ngữ cảnh (CR-18 → `internal-linking`). Kèm sơ đồ tracking (CR-06) và funnel GA4 (CR-19) sẽ dựng. Output: bảng cụm × path × CTA × event.

### #35 UX/UI feature brief + heatmap đợt 1 (T4→T6)
Per section hoặc cụm intent: tính năng/thành phần cần thêm-sửa (bộ lọc, bảng giá, calculator, so sánh, form ngắn, trust block…) với **lý do từ dữ liệu** (heatmap/recording/GA4/GSC) + item CR/UX + spec đo được cho Coder (DOM order, kích thước, vị trí, event). Đợt 1 heatmap: cài Clarity/Hotjar trên landing ưu tiên, đọc sau ≥2 tuần.

### #36 Tối ưu landing + A/B (T7→T9)
CR-08→15 trên landing ưu tiên: above-fold value prop, CTA, trust, form, FAQ mua hàng, tốc độ mobile. A/B 1 biến số/lần, đủ cửa sổ mẫu (CR-15), ưu tiên theo điểm rơi funnel (CR-19). Log mỗi test: giả thuyết · biến · mẫu · kết quả · quyết định.

## Nguồn dữ liệu

GA4 (MCP `ga4-mcp` / SA) · GSC · Microsoft Clarity hoặc Hotjar (Vincent/khách cấp) · hub PSP `data/ranking.csv` để chọn landing có ranking · `spyserp-rank-pull` khi cần keyword-level. Không có Clarity/Hotjar → làm #34 + phần A, ghi rõ "chưa có heatmap".

## Output chuẩn mỗi finding

`Trang/cụm · quan sát (số + nguồn + ngày) · giả thuyết · action · item CR/UX · owner · deadline · cách đo sau 14–30 ngày`. Kết: verdict gate G1/G2/G3 + 3 việc tuần này.
