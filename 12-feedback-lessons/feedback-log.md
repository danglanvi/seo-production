# Feedback log — {{CLIENT}}

Append-only. Entry mới nhất ở TRÊN CÙNG. Mỗi feedback = 1 entry theo `_TEMPLATES/feedback-entry.md`, kèm `log.md` op `feedback`.

## Format entry

- ID: `FB-<YYYYMMDD>-<alias>-<nn>` — `<alias>` = người ghi nhận, `<nn>` = số thứ tự trong ngày của người đó (01, 02...).
- Trường bắt buộc: Nguồn (client | internal | QC) · Workstream (WS <XX>) · Công đoạn (#n, nếu có) · Nội dung · Đề xuất xử lý · Scope (project | system | company) · Trạng thái distill (new | distilled | promoted | dropped).
- Pattern lặp ≥2 lần → đề xuất promote thành `lessons/lessons-ws<XX>.md` (1 câu, chờ duyệt).
- Item QC fail ≥2 lần tự động thành entry với Nguồn: QC.

<!-- BLOCK MẪU — giữ nguyên comment này; copy cấu trúc ra ngoài khi ghi entry thật:

## FB-20260717-vincent-01

- Nguồn: client
- Workstream: WS 05
- Công đoạn: #17
- Nội dung: Traffic plan chưa tách brand vs non-brand nên client khó đối chiếu với KPI cam kết.
- Đề xuất xử lý: Thêm cột phân loại brand/non-brand vào bảng traffic plan; đối chiếu công thức đo trong 00-client-context/kpi-commitments.md.
- Scope: project
- Trạng thái distill: new

-->
