# Chương trình chạy đêm

Đọc file này khi Lead giao việc để agent tự chạy nhiều giờ lúc anh vắng, thường là ban đêm. Nguồn: chương trình đêm 26–27/10/2026 trên site agency mẫu (`Deliverables/GTV-Brand/GTV-Website/perf-20261020/crawl-speed-2610/dem-2610/`): 23:44 → 08:21, 24 workflow, 102 agent, 22,12 triệu token của agent.

## 1. Chạy từ phiên mới

Lead chốt 27/10/2026: chương trình đêm chạy từ một phiên mới có ngữ cảnh gọn.

- Lý do: mỗi lượt lịch đọc lại toàn bộ ngữ cảnh của phiên. Đêm 26–27/10 chạy trong một phiên bắt đầu từ 10:05 hôm trước. Phiên đó có 1.538 lượt gọi API, 495,5 triệu token đọc cache và 10 lần compact.
- Trước khi Lead đi ngủ, phiên ngày làm 3 việc:
  1. Ghi `HANDOFF.md` bằng `handoff.py stamp` và ghi `<đợt>/TIEN-DO.md` (mục 2).
  2. Ghi việc đã duyệt vào `plan.json` của `workstream-master-plan`, kèm lời duyệt nguyên văn và giờ.
  3. Sinh prompt cho phiên mới bằng `python3 -B skills/runtime-handoff/scripts/handoff.py prompt ...`. Không viết prompt tay.
- Phiên mới làm 3 việc: đọc HANDOFF và TIEN-DO, tạo lịch (mục 3), launch workflow đầu tiên. Launch khi Lead còn thức, vì lần launch workflow đầu tiên trong ngày có thể bật hộp duyệt quyền.

## 2. TIEN-DO.md

Mỗi đêm có một file, đặt ở `<workstream>/<đợt>/TIEN-DO.md`. Lịch đọc file này đầu mỗi lượt.

- Đầu file ghi: lời giao nguyên văn kèm giờ, id và cron của lịch, trần agent, khung yên lặng.
- Mục "Đang chạy (cập nhật HH:MM)": run id, tên workflow, lane, đường dẫn script; lệnh nền kèm task id và file log.
- Mục "Đã xong đêm nay": mỗi dòng có giờ, việc, số trước và sau, đường dẫn bằng chứng, file `rollback.md`.
- Mục "Vấn đề mở": việc chặn, việc chờ phiên khác, việc chờ Lead.
- Mỗi lượt lịch thêm một dòng `HH:MM Cron: <việc đã kiểm, việc vừa mở>`. Lấy giờ bằng lệnh `date`.

## 3. Prompt lịch

Đặt lịch CronCreate hai lần mỗi giờ trong khung giờ đêm. Tránh phút 0 và 30. Ví dụ `13,53 0-8 <ngày> <tháng> *` chạy ở phút 13 và 53 của mỗi giờ từ 00 đến 08. Mẫu prompt (thay phần trong `<…>`):

```text
Lịch tự chạy tiếp chương trình đêm <ngày> (phiên <id>; Lead giao <giờ>: "<lời giao nguyên văn>"). Trả lời tiếng Việt. Bước:
1) Đọc <đợt>/TIEN-DO.md: bước kế, việc đang chạy, khoá.
2) Có workflow hay lệnh nền đang chạy (TIEN-DO, /workflows, ps): chỉ kiểm kết quả mới và làm bước kế. Không chạy lại việc đã xong.
3) Khung yên lặng <giờ bắt đầu>–<giờ kết thúc> (<lý do, ví dụ đợt bảo trì>): không giữ khoá production, không restart, không đo hiệu năng.
4) Chạy tối đa <N> agent cùng lúc. Mỗi workflow tối đa 6 agent.
5) Việc cần duyệt (xoá, tiền, CDN/DNS/Cloudflare, chặn bot, nội dung/giá) thì ghi vào master plan mục chờ Lead duyệt, không làm.
6) Sau <giờ đóng> không mở việc ghi mới: đóng buổi sáng theo chay-dem.md mục 6, rồi CronDelete lịch này.
Nếu không còn việc: ghi 1 dòng vào TIEN-DO.md và dừng.
```

- Lịch CronCreate chỉ sống trong phiên tạo ra nó. Việc phải chạy sau khi phiên đóng dùng cron trên server hoặc launchd trên máy luôn bật, ghi vào HANDOFF.
- Lượt lịch không gọi ArtifactData, Artifact publish, Monitor (`references/luat-lane.md`, khối "Phiên chính và lịch khi Lead vắng"). Workflow đầu tiên trong ngày đã launch lúc Lead còn thức, nên lượt lịch launch workflow sau được.

## 4. Hai trần agent

- Mỗi workflow tối đa 6 agent, tính cả agent kiểm và sửa.
- Số agent chạy cùng lúc trong phiên chạy đêm không vượt `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (repo này đặt 2 trong `.claude/settings.json`). Trần tính theo từng phiên. Đếm bằng `wf-status.py slots <thư mục session>` của chính phiên đó.
- Khi Lead nói "tối đa N agent", hiểu là trần chạy cùng lúc. Mỗi workflow vẫn tối đa 6. Đêm 26–27/10 có 2 workflow 8 và 7 agent vì agent hiểu N là trần mỗi workflow.

## 5. Hết hạn mức giữa đêm

- Agent chết khi tài khoản chạm hạn mức (đêm 26–27/10: 00:3x). Lane đã ghi `CHECKPOINT.md` thì làm tiếp được.
- Khi hạn mức mở lại, dựng workflow mới chỉ gồm lane còn lại, task mở bằng câu "Tiếp từ CHECKPOINT.md, không đo lại phần đã có" (`theo-doi-va-cuu.md` §3).
- Ghi giờ hạn mức mở lại vào TIEN-DO. Lượt lịch trước giờ đó chỉ ghi một dòng.

## 6. Đóng buổi sáng

Sau giờ đóng đã ghi trong prompt lịch, không mở việc ghi mới lên production. Làm theo thứ tự:

1. Chờ lane đang chạy xong, hoặc ghi lane còn chạy vào HANDOFF với run id.
2. Viết `<đợt>/tong-ket-sang.md`. Câu đầu là dòng tiến độ của `plan.py progress`. Sau đó ghi theo thứ tự:
   - kết luận;
   - số trước → sau;
   - QA sau thay đổi cuối;
   - việc đã làm;
   - sự cố;
   - việc không áp và lý do;
   - việc chờ Lead quyết;
   - mốc theo dõi;
   - danh sách file.
3. Dựng lại master plan (`build.py --apply`) và dựng trang chờ quyết bằng `decision-page`. Publish artifact khi Lead đã nhắn lại.
4. Ghi `<đợt>/lich-con-lai.md` gồm: lịch phiên cần tạo lại (kèm prompt nguyên văn), cron trên server, mốc đo.
5. Đóng đợt theo `theo-doi-va-cuu.md` §4: khoá, watchdog, `mark_applied`, chi phí thật, HANDOFF bằng `handoff.py stamp`.
6. CronDelete lịch đêm.

## 7. Ghi nhanh từ đêm 26–27/10

- Cửa sổ bảo trì server chạy giữa đêm (02:30–03:40) cần khung yên lặng trong prompt lịch. Khoá `_server-maint.lockdir` báo cửa sổ đó đang chạy.
- Job tái tạo map UCSS giao một map hỏng lúc 05:49, vì bước kiểm bỏ qua 124 cặp file CSS gộp và CSS gọn. Lane ghi production chạy theo lịch phải có cổng dừng tự động trước khi giao (`wp-ucss` `map_diff.py`).
- Báo cáo sáng ghi số sai 2 lần vì chép từ ghi chú cũ. Lấy số từ file kết quả của lane, không từ trí nhớ của phiên.
