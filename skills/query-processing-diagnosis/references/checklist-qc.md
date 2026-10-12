# Checklist QC: chẩn đoán Query Processing bộ keyword cam kết

> Dùng cho QC role self, verify, lead (`CLAUDE.md` §7). Chấm từng item bằng bằng chứng trích từ deliverable (JSON, hồ sơ, `_work`). Item không kiểm được ghi `CANNOT-VERIFY` và không tính pass.

## Ngưỡng

- **PASS:** đạt đủ 8 item P0 và ít nhất 8/10 item thường.
- **FAIL:** rớt bất kỳ item P0 nào, hoặc dưới 8/10 item thường.
- `CONDITIONAL-PASS` chỉ Lead quyết (`CLAUDE.md` §7.3).

## P0 (chặn)

| ID | Item | Bằng chứng cần có |
|---|---|---|
| QP-01 | Bộ keyword phân tích đúng bộ cam kết trong `kpi-commitments.md`. Keyword lệch (`not_in_export`, keyword ngoài bộ) đã ghi vào `flags` | Số keyword trong JSON = số trong hợp đồng, hoặc có dòng flags giải thích lệch |
| QP-02 | Engine đo là engine trong hợp đồng, hoặc lệch đã ghi rõ ở `measure_slide.src` và `flags` | `measure.engine`, `engine_label` khớp hợp đồng |
| QP-03 | Hạng đọc bằng median các lần chạy hợp lệ. Lần chạy bị loại có lý do. Độ sâu quét ghi đúng (50/100). Mốc so sánh nằm trong ±7 ngày của mốc 4 tuần, hoặc deck chạy `--no-compare` và không có template "Đang lan" | Output `qp_ranks.py runs` lưu trong `_work`; `measure.depth`, `measure.compare_date` |
| QP-04 | Mọi con số trên deck có nguồn trong bảng "con số → nguồn → cách tính" của hồ sơ (dán từ `--numbers`, thêm dòng cho số tự viết). Số đến từ `qp_ranks.py` và scaffold, verify 0 lỗi. Lệnh chạy lại được | Hồ sơ mục 2 và 4; thư mục `_work` |
| QP-05 | Giả thuyết không trình bày như sự thật. Câu phụ thuộc GSC, URL Inspection hay chưa kiểm chéo có chữ "giả thuyết", "cần GSC" (renderer tô đỏ) | Đọc các khối `idea`, `matrix`, `retrieve`, `qa` |
| QP-06 | Mỗi topic ghi keyword cam kết nó đẩy. Không keyword nào thuộc hai topic. `n_kw` khớp danh sách | `_work/topics.json` + `qp_build.py --topics` (verify 0 lỗi) |
| QP-07 | Không có topic chỉ kéo traffic, scale trang bằng AI, so sánh chê đối thủ, hay nhân một khung H2 sang nhiều trang | Bảng `priority`, `plan` |
| QP-08 | Trang đang giữ Top 3/5 không bị rút nội dung trước kỳ đo. Việc chạm ngày đo xếp sau ngày đo | `plan.rows`, `measure_slide.timeline` |

## Item thường

| ID | Item | Bằng chứng cần có |
|---|---|---|
| QP-09 | Mọi keyword thuộc đúng một template. Tổng 5 nhóm hạng = `n` (check đã kiểm). Template "khác" dưới khoảng 10% bộ | `templates.items`, `unmatched` rỗng |
| QP-10 | Canonical lấy URL Google đang trả từ dữ liệu, không lấy URL site muốn. Có quy trình khi Google lật URL | `canonical.rows[].google`, `canonical.flip` |
| QP-11 | SERP đúng 3 query đại diện của 3 intent, có nguồn và ngày, có dòng "Vì vậy" | `serp.cards[].meta`, `so` |
| QP-12 | Mọi URL đại diện trong bảng ưu tiên đã kiểm trang thật bằng GET (title, H1, robots, canonical, JSON-LD, link nội bộ, alt) | Output `site_check.py` trong `_work` |
| QP-13 | Ma trận trạm có `why` cho từng chấm và `fix` cho từng cụm, ghi đủ URL. Mỗi chẩn đoán có điều kiện bác bỏ trong hồ sơ. Lỗi Retrieve xếp trước việc nội dung | `matrix.rows`, `priority`, hồ sơ mục Chẩn đoán |
| QP-14 | Khối `levers` trả lời internal link, hình ảnh, chức năng, schema bằng dữ kiện trang thật, có nhãn tác động. Không hứa hạng cho slideshow, FAQPage, link sitewide | `levers.cols`, `levers.dont` |
| QP-15 | Bảng ưu tiên có `why`, mức P0/P1/P2 theo luật xếp ở `buoc-phan-tich.md` mục 9 | `priority.rows` |
| QP-16 | Regex đo dán được vào GSC (RE2: không lookaround, không backreference). Timeline có chờ 14 ngày và đọc median | `measure_slide` |
| QP-17 | Kế hoạch có Khi nào · Việc · Ai làm · Xong khi. "Ai làm" là người thật. "Xong khi" kiểm được | `plan.rows` |
| QP-18 | `qp_build.py` qua check và verify (0 lỗi). Audit 0 slide tràn (hoặc ghi lý do không chạy được audit). Đã chụp và xem slide bảng dài. Không có giá, phí, email cá nhân. Deck đưa ra ngoài nhóm dự án dùng `--web`, mọi chỗ trúng của lệnh quét bản web đã đọc lại. File bàn giao content sinh cùng version | Log lệnh trong hồ sơ mục 4 |
