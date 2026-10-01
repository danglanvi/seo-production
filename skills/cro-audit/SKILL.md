---
name: cro-audit
description: "CRO cho website SEO (WS 13, #34–36): chọn cơ chế chuyển đổi + loại trang, audit theo pattern có mức nặng P0/P1/P2, evidence-backlog, UX feature brief dev làm được, đọc heatmap/recording, rollout có theo dõi hoặc A/B khi đủ mẫu. Dùng khi: 'conversion path [client]', 'audit chuyển đổi', 'có traffic mà không ra lead/đơn', 'đọc heatmap'."
---

# CRO Audit — traffic SEO phải thành lead/đơn/hồ sơ đo được

CRO ở GTV là phần tăng giá trị của hợp đồng SEO: mỗi kỳ khách thấy phát hiện có bằng chứng, việc đã sửa và số trước/sau đúng nhãn. GTV đề xuất và viết brief; dev của khách triển khai. Vì vậy hai thứ quyết định: **finding đúng bằng chứng** và **brief làm được không hỏi lại**. Mặc định làm theo mức "research + sửa lỗi + rollout có theo dõi"; A/B chỉ khi đủ điều kiện ở `references/experiment-lite.md`.

## Luật cứng

1. **Đo trước (G1, CR-06/07).** Tracking theo skill `cro-measurement-plan` (hoặc nhúng §1 conversion-path). Chưa pass → vẫn làm research, báo blocker P0 và brief sửa lỗi; **không** công bố CR/uplift, **không** A/B.
2. **Blocker P0 site-wide báo bất kể ranking.** Form không gửi, nút gọi không `tel:`, checkout lỗi mobile, `purchase` không bắn: báo ngay, xếp đầu. CR-08 (traffic × ranking × ROI) chỉ áp cho **tối ưu** P1/P2.
3. **Một outcome ưu tiên mỗi trang, có thứ bậc CTA** (CR-10). Không xoá navigation/đường phụ để "một CTA"; khách gọi/Zalo thì gọi là primary.
4. **Không đụng cấu trúc đã lock (#11).** Đổi block map/heading/URL → về trạm 04, không patch ở đây.
5. **Bằng chứng theo scorecard.** E3 = lỗi tái hiện được hoặc số có mẫu số (xác nhận hiện tượng/tỷ lệ, không tự xác nhận nhân quả); E2 = ≥3 recording / ≥100 session heatmap / VOC lặp ≥3; E1 = heuristic → chỉ vào backlog "cần kiểm", không vào report. Một lỗi tái hiện được là đủ, không cần 3 recording. Không suy rộng tỷ lệ từ vài recording. **Mức nặng dự kiến tách khỏi bằng chứng:** nghi P0 mới E1 → giữ P0, trạng thái "cần xác minh", xác minh trước; thứ tự xếp tường minh P0→P1→P2, cùng P: R3→R2→R1, cùng R: E3→E2. Thiếu một thuộc tính (`tel:`, redirect, validation) là dấu hiệu để kiểm, không tự là P0 — mức theo task thực.
6. **≤3 click là diagnostic** (CR-16): vượt phải khai lý do, không tự động là lỗi.
7. **Deadline triển khai (14–30 ngày) ≠ cửa sổ đọc số (≥4 tuần trọn).** Không phải A/B hợp lệ → ghi "quan sát trước/sau", không "uplift". Không hứa "A/B 14 ngày".
8. Mọi đề xuất trace về pattern + item CR-xx/UX-xx; "cho đẹp", "theo trend", "best practice nói vậy" bị loại.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Loại website, cơ chế chuyển đổi chính/phụ | Brief, quan sát site | Inventory site rồi xác nhận |
| Topical map (#10) + structure brief lock (#11) | Instance | Làm site-wide + blocker, ghi "chưa có structure lock" |
| Outcome definition + trạng thái tracking | `cro-measurement-plan` / conversion-path §1 | Mức research-only, ghi rõ |
| GA4/GSC/hub PSP (landing có traffic) | Instance, MCP/SA khi có quyền | Chọn trang theo cấu trúc + intent, đánh dấu "chưa có số" |
| Heatmap/recording (Clarity/Hotjar) | Khách cấp | Bỏ phần recording, không đoán hành vi |

## Quy trình

0. **Phân loại readiness và chọn pattern** — `references/readiness-router.md`: mức (research+fix+rollout | có A/B), cơ chế (gọi/Zalo · form · báo giá · giỏ hàng · apply), 2–4 loại trang; việc rơi sang WS04/technical/copywriting chuyển theo bảng §4b. Ghi vào đầu conversion-path.
1. **#34 Conversion path + measurement** (T2→T3): cụm intent → landing → bước giữa → điểm chuyển đổi → CTA chính/phụ → event; site-wide CR-01…05; blocker P0 phát hiện ngay ở bước này. Tracking: gọi `cro-measurement-plan`.
2. **Research** — `references/research-evidence.md`: technical (tái hiện trên iOS/Android/desktop), analytics (funnel có mẫu số, phân đoạn), heuristic theo pattern, recording/heatmap (ở đâu vs vì sao), VOC (sale/support/Zalo). Mỗi finding theo format scorecard.
3. **Audit theo pattern** — `references/patterns-condensed.md` đúng mục đã chọn; gán P/R/E mặc định, đổi khi bằng chứng client khác. Ra `evidence-backlog` (>5 finding) hoặc bảng trong conversion-path.
4. **Chọn và brief** (#35, T4→T6) — xếp theo scorecard; mỗi finding được chọn → component brief theo `references/feature-brief.md` (task → vấn đề → nội dung → DOM/vị trí → hành vi → states → keyboard/label → event → acceptance → rollback). Heatmap đợt 1 đọc sau ≥2 tuần.
5. **Triển khai và đọc số** (#36, T7→T9) — `references/experiment-lite.md`: sửa lỗi + QA; rollout có theo dõi (annotation ngày, cùng mẫu số, ≥4 tuần); A/B chỉ khi feasibility đạt. Cập nhật trạng thái brief: đề xuất → khách duyệt → đã sửa → chờ khách.
6. **Report hook** — `references/report-hook.md`: bảng 3a (từ measurement plan) + 3 khối WS13 (3b phát hiện · 3c đã sửa QA PASS + số quan sát · 3d chờ khách gồm mọi P0 còn mở), nối bằng finding ID. Tự kiểm Gate → trả.

## Output

Trong `13-cro/` của instance (naming `<CLIENT>_<slug>_v<N>.md`, template `_TEMPLATES/`):
- `conversion-path` (#34) — thêm dòng readiness + cơ chế + pattern đã chọn ở đầu.
- `measurement-plan` / `tracking-qa` — từ skill `cro-measurement-plan` (hoặc nhúng §1 conversion-path khi ≤5 event).
- `evidence-backlog` — khi >5 finding; format scorecard; trạng thái từng dòng.
- `ux-feature-brief-<section>` (#35) — mỗi section/cụm 1 brief, spec theo component.
- `heatmap-review-<kỳ>` (#35/#36) — phát hiện + action + log rollout/A/B.
Ngoài repo SEO Production: `Deliverables/<project>/<client>_<slug>_v<N>.md`.

## Gate / tự kiểm trước khi trả

- [ ] Readiness + cơ chế + pattern ghi rõ; mức A/B chỉ khi feasibility có số.
- [ ] Mọi finding có nhãn P/R/E; E1 không vào report; blocker P0 xếp đầu bất kể rank.
- [ ] Mỗi brief đủ 10 mục component, dev đọc là làm; không có "cho đẹp".
- [ ] Không gán nhân quả từ heatmap/before–after; không benchmark ngoài làm KPI; không cam kết tài chính.
- [ ] Không đổi structure lock; đổi thì có ghi chú route trạm 04.
- [ ] Số trong report cùng mẫu số, cùng cửa sổ, đúng nhãn ("click" ≠ "lead", "đơn tạo" ≠ "doanh thu", "quan sát" ≠ "uplift").
- [ ] Không PII trong backlog/brief/report.
- [ ] Trạng thái brief tách "đã brief / dev đã deploy / GTV QA PASS"; chỉ QA PASS vào "đã sửa"; mọi P0 còn mở có mặt ở 3d với tuổi lỗi và owner.
- [ ] Tình huống "web VN" trong pattern là giả thuyết cần kiểm, không dùng làm E2/E3.

## Anti-patterns

- Bắt đầu bằng màu CTA. Làm đúng: bước 1–2 trước, blocker và đo lường trước.
- Chấm 10 pattern cho site chỉ có form. Làm đúng: 1–2 cơ chế + 2–4 loại trang.
- "3 recording cho thấy 70% khách bỏ form". Làm đúng: 3 recording = giả thuyết; tỷ lệ lấy từ funnel có mẫu số.
- Brief "làm form gọn hơn". Làm đúng: field inventory + lý do từng field + spec component + acceptance.
- Chờ tracking pass mới làm gì. Làm đúng: research + blocker + brief sửa lỗi song song với measurement plan.
- Kết luận winner sau 5 ngày vì p<0,05. Làm đúng: `experiment-lite.md` §3.

## Changelog

- v2.1 (2026-09-13): vá theo review Astra (F04/F06/F07/F09/F10/S01/Q5) — thứ tự xếp tường minh, severity tách evidence, P0 tồn hiện đầu report + 3 mốc trạng thái brief, bảng chuyển việc WS13/WS04/technical/copywriting, "lỗi web VN" thành giả thuyết cần kiểm, sửa claim kỹ thuật (tel:/redirect/query/value/noindex), 5 ca eval mới.
- v2.0 (2026-09-13): tái cấu trúc theo plan CRO add-on (Vincent duyệt 12/09): 2 mức readiness, router cơ chế × loại trang, scorecard P/R/E, blocker P0 tách khỏi CR-08, ≤3 click thành diagnostic, deadline ≠ cửa sổ đọc số, experiment thành reference, report hook; 6 references + evals. Nguồn: wiki Inbound Marketing (concepts/cro, patterns, ai-referral).
- v1.0 (2026-09-03): tạo mới cùng WS 13 (#34–36), 3 template, CR-01…19.
