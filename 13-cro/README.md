# 13 — CRO (WS CRO)

1. **Mục đích**: Biến traffic SEO thành chuyển đổi đo được — conversion path theo cụm intent, tính năng/UX-UI per section, đọc heatmap-recording → action. Tách khỏi WS 04 (cấu trúc lock 1 lần ≤15 ngày đầu T2; CRO chạy lặp T2→T9).
2. **Công đoạn phụ trách**: #34 (conversion path + tracking, T2→T3), #35 (UX/UI feature brief + heatmap đợt 1, T4→T6), #36 (tối ưu landing + A/B, T7→T9).
3. **Deliverable chuẩn**: `<CLIENT>_conversion-path_v<N>.md` · `<CLIENT>_ux-feature-brief-<section>_v<N>.md` · `<CLIENT>_heatmap-review-<kỳ>_v<N>.md`.
4. **Template**: `_TEMPLATES/conversion-path.md` · `_TEMPLATES/ux-feature-brief.md` · `_TEMPLATES/heatmap-recording-review.md`.
5. **Checklist QC**: `02-raw/knowledge/sop/06-self-checklist/tier-1-cro-conversion.md` (CR-01…19, gate G1 tracking ≤T3 · G2 1 CTA chính · G3 funnel đo được) + `tier-1-ux-ui.md` (UX-01…18).
6. **Skill gọi**: `skills/cro-audit/` · `skills/internal-linking/` (CR-18) · `skills/visual-semantic-seo/` chỉ khi cần quay lại trạm 04. Dữ liệu: GA4 (MCP/SA), GSC, Clarity/Hotjar, hub PSP.
7. **Done-criteria**: tracking verify ≤T3; mỗi cụm intent có path ≤3 click + 1 CTA chính; mỗi action CRO có số trước/sau và mốc đọc lại; A/B 1 biến/lần đủ mẫu.

Ghi chú:

- Không đụng cấu trúc đã lock (#11). Cần đổi cấu trúc → structure brief version mới ở trạm 04, không patch ở đây.
- Chỉ tối ưu landing đã có traffic + ranking (CR-08). Trang chưa ai vào → về trạm 05/06 trước.
- Chưa có Clarity/Hotjar → làm #34 + phần A; ghi rõ "chưa có heatmap" trong deliverable, không đoán hành vi.
