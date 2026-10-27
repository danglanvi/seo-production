# Theo dõi, cứu workflow treo, đóng đợt

Mục đích: cách theo dõi workflow đang chạy, dò và cứu lane treo, đổi phạm vi lane, việc phải làm khi đóng đợt. Đọc ở bước 10–12 của skill. Nguồn: phiên f00d80af (23–24/10/2026) và đợt rà transcript 16–24/10 (mục hs-1, hs-2, ops2-6, ops2-7).

## 0. Chủ run và lane khi nhiều phiên cùng chạy

Nguồn: coord-5 và ops2-5 của đợt rà 16–24/10. `runtime-handoff` trỏ phần này về skill này.

- Phiên launch workflow là phiên chủ. Phiên chủ ghi `<đợt>/OWNER.md`: 8 ký tự đầu của session id, task id, run id, giờ launch, danh sách lane và phạm vi của từng lane.
- Phiên chủ thêm một dòng cho mỗi lane đang sống vào mục Trạng thái của HANDOFF workstream: `Lane: <tên> giữ <phạm vi> · phiên <id> · run <id>`. Xoá dòng khi lane xong.
- Phiên khác đọc `OWNER.md` và các dòng `Lane:` trước khi dựng workflow chạm cùng site. Chỉ phiên chủ được TaskStop, ghi `inbox.md` và đóng đợt.
- Phiên khác đang đổi DNS, CDN hay cấu hình server: phiên đó tạo `~/.cm/locks/cdn-no-restart.lock` (hoặc khoá cùng loại). Khi khoá còn, phiên này không restart dịch vụ và không đo hiệu năng.
- Khoá dạng flock (file rỗng luôn tồn tại, ví dụ `prod-http.lock`) không cho biết ai giữ qua nội dung file. Kiểm người giữ bằng `lsof <file>`. Chạy request production qua `plock.sh` với thời gian chờ ngắn; hết giờ chờ thì làm việc khác, không tranh khoá.
- Hai phiên trao đổi bằng file trả lời trong thư mục đợt, ví dụ `<đợt>/<chủ đề>-reply.md`. Mỗi tin có số thứ tự, giờ lấy bằng `date` và tên phiên gửi. Phiên nhận ghi "đã đọc tin N" và việc sẽ làm. Không chép secret hay IP vào file này.
- Trước khi purge, restart hay ghi một tài nguyên, đọc dòng `Lane:` trong HANDOFF của mọi workstream cùng site. Tài nguyên có lane của phiên khác giữ thì ghi việc vào file trả lời, không tự làm.
- Dò run còn sống của mọi phiên: `find ~/.claude/projects/<slug>/*/subagents/workflows -name journal.jsonl -mmin -30`, rồi chạy `python3 tools/wf-status.py slots <thư mục session>` cho từng session tìm thấy.

## 1. Theo dõi bằng watchdog chạy ngoài model

Lịch LLM 30 phút phát hiện treo sau 23–97 phút và tốn một lượt model cho mỗi lần kiểm không có gì mới. Từ v1.1, phiên chính dùng `scripts/wf_watchdog.py`. Script đọc journal và đuôi transcript agent, không gọi model.

1. Ngay sau khi launch workflow, chạy bằng tham số `run_in_background: true` của Bash. Không thêm `&` cuối lệnh: lệnh thoát ngay và harness không báo khi watchdog thoát (đêm 26–27/10/2026, phải đọc log tay):

   ```text
   python3 skills/web-lane-orchestration/scripts/wf_watchdog.py <thư mục session> --minutes 12 --idle-minutes 20 --max-hours 10 --out <thư mục đợt>/watchdog.log
   ```

   Thư mục session: `~/.claude/projects/<slug>/<session id>/`. Khi đã biết run id và thư mục run đã có, truyền thẳng `<thư mục session>/subagents/workflows/<run id>`. Với thư mục session, script bỏ qua run đã xong trước lúc nó chạy và chờ run mới tối đa `--wait-new` phút (mặc định 15).
2. Harness báo phiên chính khi script thoát. Script chỉ thoát khi có việc cần xem:
   - exit 1: có dòng `TREO` (tool_use chờ kết quả quá 12 phút) hoặc `IM` (file agent không ghi 20 phút). Làm theo §2.
   - exit 0 với dòng `XONG run=<id>`: run kết thúc (`wf_<run id>.json` có status `completed`, `killed` hoặc `failed`). Đóng đợt theo §4.
   - exit 2 với dòng `KHONG-CO-RUN`: chưa thấy run mới sau `--wait-new` phút. Kiểm workflow đã launch chưa.
   - exit 3: quá `--max-hours`. Kiểm run bằng `wf-status.py stale`, rồi chạy lại watchdog nếu run còn sống.
3. Không dùng Monitor và không tự poll giữa chừng. Không đặt lịch LLM 30 phút cho việc dò treo.

Lịch CronCreate chỉ còn dùng cho việc cần model đọc và quyết định, ví dụ gom `mark_applied.json` hoặc cập nhật HANDOFF theo mốc. Giữ phút lệch 0 và 30 (`13,43 * * * *`). Prompt ghi rõ task id, run id và việc không được kiểm, ví dụ "KHÔNG kiểm M23 (Lead publish sau 10/11)". Lịch chỉ sống trong phiên tạo ra nó. Việc cần chạy sau khi đóng phiên phải nằm trong HANDOFF mục "Bước tiếp", kèm giờ. Khi Lead vắng quá 10 phút, lịch cũng theo khối "Phiên chính và lịch khi Lead vắng" ở `luat-lane.md`.

## 2. Dò lane treo

Lệnh nhanh, chỉ đọc:

```text
python3 tools/wf-status.py stale <thư mục run hoặc run id> --minutes 15
python3 tools/wf-status.py slots <thư mục session>
```

Phân loại theo dòng báo của watchdog:

| Dòng báo | Nghĩa thường gặp | Việc làm |
|---|---|---|
| `TREO … [hop-duyet?]` (Monitor, ArtifactData, Artifact, Bash có `$(` hoặc backtick) | Tool đang chờ hộp duyệt quyền. Agent không làm gì cho tới khi có người bấm | Nếu Lead đang thức, báo Lead bấm. Nếu Lead vắng, cứu theo §3 và bỏ tool đó khỏi task mới |
| `TREO` ở Bash khác | Lệnh chờ không có trần, hoặc lệnh dài chạy tiền cảnh | Xem lệnh trong dòng báo. Lệnh chờ log hay vòng chờ: treo thật, cứu theo §3 |
| `TREO` ở tool Agent hoặc lệnh đo dài có chủ đích | Có thể đang chạy việc thật | Kiểm tiến trình con và file log. Còn ghi thì chạy lại watchdog |
| `IM` | Agent không ghi transcript, không có tool đang chờ | Thường là đang sinh câu trả lời dài hoặc chết vì hạn mức. Kiểm lại sau 10 phút bằng `stale` |

Ca thật:

- 20–21/10: agent `kiem-ap1701-ui-2` chờ 2 lệnh Monitor có `$(wc -l …)` từ 00:50 tới 03:25 và từ 03:38 tới 09:03, vì hộp duyệt quyền. Lịch LLM không phân biệt được ca này với lane đang làm.
- 24/10: lane font treo lúc 01:38 ở lệnh Monitor có `until [ $(grep -c …) ]` chờ log PSI. Nguyên nhân là hộp duyệt quyền của Monitor, không phải vòng until. Phiên chính phát hiện và dừng lúc 02:28.

## 3. Cứu và đổi phạm vi

Không resume workflow đã chết. Không SendMessage vào agent đang chạy trong workflow: mỗi tin sinh một bản chạy trùng dùng chung transcript, và hai bản ghi đè cùng một CHECKPOINT (lô L4, 20/10, khoảng 35 phút).

Đổi phạm vi lane đang chạy: ghi chỉ thị vào `<lane>/inbox.md`. Lane đọc file này ở mỗi mốc CHECKPOINT. Việc mới ngoài phạm vi lane: dựng workflow mới.

Dừng: TaskStop cả task workflow, không dừng từng agent. Agent bị TaskStop vẫn có thể trả kết quả, và bước phụ thuộc phía sau vẫn chạy (20/10 01:39). Vì vậy bước phụ thuộc trong script luôn kiểm điều kiện thật trên file (`ket-qua.json`, `kiem-doc-lap.md`) trước khi ghi.

Cứu lane treo:

1. TaskStop task workflow. Đổi khoá lane treo thành `.lock.stopped-HHMM`. Nhả `staging.lockdir` và `_server-maint.lockdir` nếu lane treo đang giữ.
2. Đọc `CHECKPOINT.md` và `ket-qua.json` (nếu có) của lane treo. Ghi lại phần đã xong: số đã đo, file đã ghi lên staging hoặc production kèm md5.
3. Lấy script đã lưu của workflow cũ. Giữ `COMMON`, schema và các lane chưa xong. Bỏ lane đã đạt.
4. Thêm khối `EXTRA` vào task của từng lane còn lại:
   - Giờ treo, lệnh treo, luật để không treo lại.
   - Việc đã xong của cả đợt.
   - Trạng thái của lane treo: production đã đổi chưa, staging đang chạy bản nào (md5), số đo nào đã có và nằm ở file nào.
   - Câu "Tiếp từ CHECKPOINT.md, không đo lại phần đã có".
   - Khoá đã nhả và việc phải tạo lại khoá.
   - Mốc giờ phải xong, nếu đợt sau đang chờ khoá của lane này.
5. Kiểm lại script mới bằng `wf-status.py lint-script`, rồi chạy watchdog cho run mới.

Ví dụ thật: workflow lane tối 23/10 bị dừng sau 666 phút, đã tốn 2,3 triệu token. Lúc 02:3x ngày 24/10, script `gtv-web-ban7-tiep-2` chạy lại font → ảnh LCP → ACF production (10 agent, 1,9 triệu token; trước trần 6 agent, nay tách 2 workflow). Kết quả: font trả lại theo ngưỡng, ACF production đạt, ảnh LCP không đạt lượt kiểm 2 và phiên chính sửa tiếp.

Lane trả `status: held`: không phải lỗi. Ghi `held_until` vào HANDOFF mục "Bước tiếp". Khi điều kiện mở, chạy lane đó trong workflow sau.

## 4. Đóng đợt

1. Lập bảng lane → `status`, `pass` của lượt kiểm cuối, số `loi_production` và `loi_bao_cao`, file `ket-qua.json`, việc chờ Lead. Lane không đạt ghi lý do và lệnh trả lại. Đọc kết quả bằng `python3 tools/wf-status.py result <label> <run>`, không parse `tasks/<id>.output`.
2. Phiên chính sửa các mục `loi_bao_cao` bằng Edit. Không mở agent mới cho lỗi báo cáo. Gom `for_lead` của mọi lane, dựng trang chờ quyết bằng skill `decision-page` (`gen_decision.py`). Câu trả lời của Lead đổi thành việc bằng `parse_answer.py` của skill đó.
3. Gom id từ `mark_applied.json` của mọi lane, trừ id đã có trong file id đã đánh dấu.
   - Lead đã nhắn trong 10 phút gần nhất: ghi một batch ArtifactData, rồi thêm id vào file id đã đánh dấu.
   - Lead vắng: ghi vào `~/.cm/ma/cho-sang-<ngày>/`. Sáng hôm sau mới ghi batch.
4. Kiểm `~/.cm/locks/`: mọi khoá lane đã `.lock.done-HHMM` hoặc `.lock.stopped-HHMM`. `staging.lockdir` và `_server-maint.lockdir` rảnh.
5. Kiểm watchdog đã thoát. Chạy CronList, huỷ lịch của đợt. Lịch còn cần thì ghi vào HANDOFF mục "Bước tiếp", kèm giờ.
6. Ghi chi phí thật vào báo cáo đợt bằng `python3 tools/wf-status.py tokens <run id>`: số agent, token theo model, so với ước tính trong plan.
7. Ghi đoạn Trạng thái của HANDOFF bằng `python3 -B skills/runtime-handoff/scripts/handoff.py stamp --note "<một câu>" --write <HANDOFF.md>`, không sửa tay. Xoá các dòng `Lane:` của đợt và đánh dấu `OWNER.md` là đã đóng. Chạy `runtime-handoff` chế độ `check`. HANDOFF quá 60 dòng thì sao bản cũ vào `Archive/HANDOFF_<ngày-giờ>.md` rồi viết lại.

Báo cáo đợt dài hoặc cần đọc nhiều file: phiên chính làm, hoặc chạy một workflow tổng kết riêng (Sonnet high, chỉ đọc). Không nối bước tổng kết vào cuối workflow ghi. Đợt có lane `core`: workflow tổng kết thêm một agent Opus high kiểm cuối đợt, chỉ đọc, đo lại site sau khi mọi lane xong.
