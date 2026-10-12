# 03-audits/ranking/ — Chẩn đoán Query Processing bộ keyword cam kết

Hướng dẫn cho Lead: cần chuẩn bị gì, đưa agent thông tin gì, nhận lại gì. Agent làm theo skill `query-processing-diagnosis`.

## 1. Khi nào chạy

- Gate #22 "Initial ranking như kỳ vọng?" (T4–T6), audit định kỳ #24, #29.
- Khi keyword cam kết đứng hạng nhiều tuần, hoặc rơi theo cụm.
- Không chạy cho dự án chưa có hạng: dự án mới dùng `keyword-topic-url-mapping` (#4). Rơi diện rộng nghi do update, hack hay lỗi toàn site: chạy `02-raw/knowledge/sop/06-self-checklist/tier-3-ranking-drop-runbook.md` trước.

## 2. Chuẩn bị (Lead, khoảng 20 phút)

**Máy:** Python 3 và curl (đã có nếu `python3 _SETUP/setup_doctor.py --json` trả `ok: true`). Audit tràn chữ của deck cần thêm Node ≥22 và Google Chrome. Thiếu hai thứ này thì agent bỏ audit và ghi lý do.

**Export hạng từ SpySERP:**
1. Mở project đo bộ keyword cam kết. Nếu có bản theo dõi cả domain đối thủ, chọn bản đó: agent cần nó để phân biệt "ngoài Top" với "lần chạy thiếu dữ liệu".
2. Chọn đúng engine của hợp đồng (thiết bị, vị trí).
3. Chọn khoảng ngày ít nhất **35 ngày** gần nhất. Agent so hạng hiện tại với mốc 4 tuần trước, nên thiếu ngày thì không có cột so sánh.
4. Bấm **Export** trên thanh công cụ. Định dạng **CSV**, phạm vi **All** (bỏ filter). Không dùng bản export tự động theo lịch, vì bản đó hay bị lọc theo view.
5. Vào tab **Exports** của project. Chờ file chạy xong rồi tải về.
6. SpySERP chia lần chạy thành nhiều trang. Mở file bằng trình soạn chữ, xem dòng `Schedules Page`. Nếu file chỉ có khoảng 10 ngày gần nhất, export thêm các trang lịch cũ hơn cho đủ 35 ngày. Lưu mỗi trang một file.
7. Lưu vào `02-raw/seo-data/keywords/<YYYY-MM-DD>_spyserp_<tên-bộ>[_p2].csv`. Không sửa file. Đợt sau lưu file mới.
8. Kiểm nhanh: các file cộng lại có ít nhất 35 ngày đo, và số keyword bằng số trong project.

Không vào được SpySERP (phiên hết hạn): tải tab hạng trong sheet của dự án thành CSV (File → Tải xuống → CSV) và ghi vào phiếu ô A5. Agent đọc được file dấu phẩy.

**Bộ keyword cam kết:** cần một file có cột keyword: sheet KPI tải thành CSV, hoặc file trong `00-client-context/`. Bộ có nhiều nhóm (Duy trì, Thúc đẩy) thì ghi tên cột nhóm và nhóm cần chẩn đoán vào phiếu ô A3. Agent tự trích, không cần Lead chép lại.

**URL target theo kế hoạch (nên có):** file hai cột keyword và URL (topical map, content plan hoặc sheet URL). Agent dùng file này để đếm keyword mà Google đang trả về URL khác kế hoạch.

**Điền phiếu:** copy `_TEMPLATES/qp-intake.md` vào `03-audits/ranking/_work/<CLIENT>_qp-chan-doan_v<N>/intake.md` rồi điền. Phần A bắt buộc. Phần B giúp agent bớt chữ đỏ.

**GSC (nếu có quyền):** export Performance theo page × query 3 tháng vào `02-raw/seo-data/keywords/`. Không có thì agent ghi "cần GSC" ở các kết luận phụ thuộc GSC.

## 3. Gọi agent

```
chẩn đoán QP <CLIENT> theo phiếu 03-audits/ranking/_work/<CLIENT>_qp-chan-doan_v<N>/intake.md
```

Agent dừng hỏi **một lần**, ở bước Pre-work: báo bộ keyword, engine, khoảng ngày của export, lần chạy bị loại, dữ liệu còn thiếu. Lead trả lời "ok" hoặc sửa. Hai trường hợp agent hỏi thêm:
- Export dưới 35 ngày: Lead export thêm trang lịch, hoặc đồng ý chạy không có cột so sánh.
- Project chỉ theo dõi domain của khách và lần chạy mới có ít keyword có hạng hơn hẳn: Lead mở SpySERP xem đó là rơi hạng thật hay SpySERP thiếu dữ liệu.
 Sau đó agent chạy liền tới khi có deck. Một dự án chạy trong một phiên. Nhiều dự án thì chạy lần lượt, mỗi dự án một phiên.

## 4. Nhận lại gì

| File | Dùng làm gì |
|---|---|
| `<CLIENT>_qp-chan-doan_v<N>.html` | Deck nội bộ 15–17 slide: template, lưới hạng, canonical, SERP, 8 trạm, ngoài chữ, ưu tiên, đo lường, kế hoạch 2 tuần. Rê chuột để xem giải thích, chữ đỏ là chỗ cần kiểm tay |
| `<CLIENT>_qp-chan-doan_v<N>.md` | Hồ sơ: tóm tắt, đề xuất cho gate #22, bảng con số → nguồn, flags, tự chấm checklist |
| `<CLIENT>_qp-chan-doan_v<N>.json` | Dữ liệu deck. Muốn sửa nội dung thì sửa file này |
| `<CLIENT>_qp-handoff-content_v<N>.md` | Bàn giao cho team content: template và URL Google chọn, topic và keyword mỗi topic đẩy, trạm hỏng (ghi rõ việc nào team content làm), SERP, bảng tra keyword. Repo content kéo về bằng `project_sync.py pull` |
| `_work/<CLIENT>_qp-chan-doan_v<N>/` | Phiếu, bộ keyword, luật gom template, bảng hạng, topic, trang đã tải, ảnh slide. Giữ lại để chạy lại ra cùng số |

Deck gửi cho người ngoài nhóm dự án thì xin bản `--web`: bản này bỏ chỉ tiêu, mốc nghiệm thu và các thẻ nội bộ.

## 5. Sau khi nhận

1. Đọc chữ đỏ và mục Flags của hồ sơ. Kiểm tay những chỗ đó (GSC, URL Inspection, SERP).
2. Chốt gate #22 (nếu đang ở gate): Lead ghi verdict vào `index.md`. Agent chỉ đề xuất.
3. Muốn sửa deck: gõ "sửa QP <CLIENT>: slide <số>: <nội dung>". Agent sửa JSON rồi dựng lại bằng một lệnh, link file giữ nguyên. File bàn giao content dựng lại cùng lệnh.
4. Commit và push repo SEO để team content kéo được file bàn giao mới (`python3 contracts/scripts/project_sync.py pull` ở repo content).
5. Sau 14 ngày làm kế hoạch: export SpySERP mới, chạy lại chẩn đoán (version mới) để so.

## 6. Quy ước lưu

- Mỗi lần chẩn đoán có 4 file cùng version (JSON, HTML, hồ sơ, bàn giao content) và một thư mục `_work`. Không đè version cũ.
- Data gốc (export SpySERP, GSC) nằm ở `02-raw/seo-data/keywords/`, không để ở đây.
- Checklist QC: `skills/query-processing-diagnosis/references/checklist-qc.md` (QP-01…QP-18).
