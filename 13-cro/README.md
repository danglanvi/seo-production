# 13 — CRO (WS CRO)

1. **Mục đích**: Biến traffic SEO thành chuyển đổi đo được — đo trước, phát hiện có bằng chứng, brief dev khách làm được, rollout có theo dõi. CRO là phần tăng giá trị hợp đồng SEO (khách thấy phát hiện · việc đã sửa · số đúng nhãn mỗi tháng). Tách khỏi WS 04 (cấu trúc lock 1 lần ≤15 ngày đầu T2; CRO chạy lặp T2→T9). v2026.09.4.
2. **Công đoạn phụ trách**: #34 (conversion path + measurement plan + tracking QA, T2→T3), #35 (research → evidence-backlog → UX/UI feature brief + heatmap đợt 1, T4→T6), #36 (sửa lỗi / rollout có theo dõi / A/B khi đủ mẫu, T7→T9).
3. **Deliverable chuẩn**: `<CLIENT>_conversion-path_v<N>.md` · `<CLIENT>_measurement-plan_v<N>.md` + `<CLIENT>_tracking-qa_v<N>.md` (nhúng vào conversion-path §1 khi ≤5 event) · `<CLIENT>_evidence-backlog_v<N>.md` (khi >5 finding) · `<CLIENT>_ux-feature-brief-<section>_v<N>.md` · `<CLIENT>_heatmap-review-<kỳ>_v<N>.md`.
4. **Template**: `_TEMPLATES/conversion-path.md` · `measurement-plan.md` · `tracking-qa.md` · `evidence-backlog.md` · `ux-feature-brief.md` · `heatmap-recording-review.md`.
5. **Checklist QC**: `02-raw/knowledge/sop/06-self-checklist/tier-1-cro-conversion.md` (CR-01…19; G1 tracking ≤T3 — chưa PASS vẫn làm research/blocker/brief sửa lỗi, không công bố CR/A/B · G2 1 outcome ưu tiên có thứ bậc CTA · G3 funnel đo được, ghi "pending" khi G1 chưa pass hoặc offsite không callback) + `tier-1-ux-ui.md` (UX-01…18).
6. **Skill gọi**: `skills/cro-audit/` (v2: readiness router, pattern có mức nặng, scorecard, brief 10 mục, experiment-lite, report hook) · `skills/cro-measurement-plan/` (event contract, spec GTM, QA, đối soát) · `skills/internal-linking/` (CR-18) · `skills/visual-semantic-seo/` chỉ khi cần quay lại trạm 04. Dữ liệu: GA4 (MCP/SA), GSC, Clarity/Hotjar, hub PSP.
7. **Done-criteria**: measurement plan bàn giao ≤T3 và tracking QA PASS theo cơ chế primary (ca không áp dụng ghi N/A); mọi finding có nhãn P/R/E, blocker P0 báo bất kể ranking, E1 không vào report; mỗi cụm intent có 1 outcome ưu tiên với thứ bậc CTA và không dead-end (≤3 click là diagnostic, vượt khai lý do); mỗi brief đủ 10 mục component với metric theo dõi; QA chức năng ngay sau deploy, đọc số sau ≥4 tuần trọn nhãn "quan sát"; A/B chỉ khi feasibility có số, một giả thuyết = một treatment, đủ mẫu + SRM PASS mới kết luận.

Ghi chú:

- Không đụng cấu trúc đã lock (#11). Cần đổi cấu trúc → structure brief version mới ở trạm 04, không patch ở đây. Bảng chuyển việc WS13/WS04/technical/copywriting: `skills/cro-audit/references/readiness-router.md` §4b.
- Tối ưu P1/P2 chỉ trên landing có traffic + ranking (CR-08); **blocker P0 site-wide** (form không gửi, nút gọi không mở dialer, checkout lỗi, `purchase` không bắn) báo và brief sửa bất kể rank.
- Chưa có Clarity/Hotjar → làm #34 + phần A + technical/VOC; ghi rõ "chưa có heatmap", không đoán hành vi.
- P0 tồn luôn hiện đầu báo cáo tháng (khối 3d) với tuổi lỗi, owner, follow-up cho tới khi GTV QA PASS; trạng thái brief tách "đã brief / dev đã deploy / GTV QA PASS".
