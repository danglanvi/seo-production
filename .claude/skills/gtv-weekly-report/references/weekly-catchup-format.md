# Hai format deck: TUẦN (weekly catchup) vs THÁNG (deep dive)

> Vincent chốt 23/07/2026 (từ yêu cầu thực tế của client CareerViet + đối chiếu mẫu agency đối tác). Nguyên tắc Drucker: đo lường vẫn chạy đủ hằng tuần — chỉ TRÌNH BÀY đúng liều theo nhịp họp. Nạp file này ở Pha 0 (chọn format) và Pha 3 (render).

## Chọn format nào

| | TUẦN — weekly catchup | THÁNG — deep dive |
|---|---|---|
| Mục đích | Buổi catchup ~15 phút với client, theo agenda client yêu cầu | Review sâu khi khép tháng + đối chiếu OKR |
| Độ dài | **~11 slide LEAN** | **~26 slide đầy đủ** |
| Nhịp build | Hằng tuần (pipeline FETCH/ANALYZE giữ nguyên 100% — chỉ content.yaml là bản lean) | Ngày 2–4 tháng kế tiếp, khi data tháng khép |
| Vị thế cạnh tranh | Impact-first: mở bằng run-rate KPI + chẩn đoán (agency khác thường chỉ báo % task done) | Chứng minh chiều sâu phân tích + pattern |

## Format TUẦN — map 11 slide (theo agenda client 5 mục)

| # | Slide | Type builder | Nguồn data |
|---|---|---|---|
| 1 | Cover | `cover` | meta |
| 2 | Agenda — đúng 5 mục client | `agenda` | cố định |
| 3 | Run-rate / KPI snapshot | `runrate` | `digest:runrate_tuan` |
| 4 | What works — 2-3 điểm sáng, MỖI ĐIỂM KÈM SỐ | `nhanxet_2col` | insights (KPI chính / chất lượng traffic) |
| 5 | What fails → next solution — mỗi fail: số → nguyên nhân khả dĩ → giải pháp → **người làm + deadline** | `diagnose` | insights (rubric chẩn đoán) |
| 6 | Task done this week | `sow` | sheet «[Mới] Report tuần» section tuần hiện hành |
| 7 | Task to do next week | `next_week` (rows) | RULE CARRY-OVER (dưới) |
| 8 | Blockers — need support, kèm SỐ NGÀY CHỜ (aging) | `support` | task Trễ hạn/Tạm ngưng PIC=KH/Dev + tab việc phối hợp |
| 9 | New initiatives from GTV — slot cố định mỗi tuần | `nhanxet_2col` | OKRs quý (sáng kiến ngoài SOW thường nhật) |
| 10-11 | Q&A + Thanks | `qna`/`thanks` | cố định |

Điều làm client thấy chuyên nghiệp: cấu trúc tuần nào cũng y hệt · số đỏ luôn đứng cạnh giải pháp + owner · action tuần trước tuần này có status (vòng lặp khép kín) · task nối với số ("refresh X bài → nhóm +Y%").

## Bảng công việc 5 cột (chuẩn Vincent 23/07/2026 — slide Task done + Task next week)

`build_deck.py` (render `sow`/`next_week`) nhận rows dạng `{hangmuc, task, pic, deadline, status}` → tự render bảng 5 cột: **Hạng mục** (nhóm việc liên quan, gộp ô rowspan) | **Task cụ thể** | **PIC** (tên người GTV hoặc «CRV»/«Dev CRV» khi việc thuộc khách) | **Deadline** | **Tiến độ**. Row chỉ có `{task, status}` → fallback bảng 2 cột (deck cũ không vỡ).

- Hạng mục lấy đúng cột «Hạng mục» của sheet «[Mới] Report tuần»; xếp các row cùng hạng mục LIỀN NHAU để rowspan gộp được.
- Task text giữ 1 dòng trên slide (≤~70 ký tự) — dài quá thì rút gọn, chi tiết để trong sheet; quá nhiều row thì tách slide (luật chống đè `.data-meta`).
- Tiến độ dùng đúng vocabulary sheet (Done / Đang làm / Trễ hạn / Tạm ngưng — chips tự đếm) hoặc nhãn plan (Chuyển tiếp / Mới / Điều chỉnh target).

## RULE CARRY-OVER (Vincent 23/07/2026 — áp mọi đợt plan tuần)

Task chưa done ở timeline OKRs / sheet tuần **TỰ ĐỘNG chuyển sang plan tuần kế**, trừ khi Vincent điều chỉnh hay có feedback. Build slide 7:

1. Lấy mọi task status ≠ Done của tuần hiện hành + task Trễ hạn/Tạm ngưng còn hiệu lực → status **«Chuyển tiếp»**.
2. Thêm task mới từ action insights + mốc OKR sắp đến hạn → status **«Mới»**; Vincent đổi target thì ghi **«Điều chỉnh target»**.
3. Mỗi task kèm **PIC in đậm** ngay trong text. Trình Vincent chốt cả danh sách — KHÔNG hỏi từng dòng.
4. Sau khi chốt: team dán section tuần mới vào sheet «[Mới] Report tuần»; lần render kế AI đổ lại từ sheet (sheet là nguồn chính thức).

## Format THÁNG — khung 26 slide + lớp tháng

Dùng nguyên khung slide-map đầy đủ (`references/slide-map.md`: movers, intent, ngành nghề, khu vực, blog groups, apply pivot, SOW…) và THÊM lớp tháng:

1. **MoM**: tháng này vs tháng trước (PV/Apply per nhóm trang) + YoY nếu run-rate tháng có cột.
2. **Tiến độ OKRs quý**: bảng Objectives/KR + status (Done/Đang làm/Trễ) từ sheet «OKRs Quý» — tháng cuối quý thì kèm chấm điểm KR + danh sách carry-over sang quý mới.
3. **Run-rate lũy kế** vs kế hoạch năm.
4. **Pattern 4 tuần**: tổng hợp từ các file insights tuần trong tháng (flags mở/đóng, nhóm giảm liên tiếp, action đã làm → kết quả).

## Luật output (cả 2 format)

- **CHỈ tạo HTML** — tuyệt đối không tự export PDF, kể cả report định kỳ (Vincent siết 23/07/2026). PDF chỉ khi Vincent yêu cầu rõ trong phiên.
- Tự kiểm chống tràn: Playwright screenshot từng slide HTML (`#n`), không qua PDF.
- Mọi luật cứng khác giữ nguyên: `.data-meta` mỗi slide data, số truy vết được về sheet, action dạng ul từng dòng.
