---
name: runtime-handoff
description: "Bàn giao giữa phiên chat, runtime, tài khoản Claude và lượt chạy đêm: HANDOFF.md có giờ máy, prompt phiên mới, bản có hash, PLAN đêm. Use when: 'prompt qua chat khác', 'bàn giao sang Codex', 'đổi tài khoản', 'sắp hết usage', 'tạm stop', 'tổng kết rồi đóng phiên', 'chạy đêm'."
metadata:
  version: "1.3.1"
---

# runtime-handoff — tiếp tục từ trạng thái đã xác minh

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

## Khi nào dùng

Đổi runtime, đổi máy, đổi tài khoản, sắp hết usage, tạm dừng, đóng phiên hoặc tiếp tục task dài sau gián đoạn. Không dùng cho status một câu. Không nhập cả session history vào shared memory.

| Chế độ | Khi nào | Lệnh |
|---|---|---|
| Bàn giao có hash | đổi runtime hoặc máy, cần ghim nguồn | `create`, `verify` |
| Phiên mới | phiên chat dài, vừa compact, "prompt qua chat khác", "tổng kết rồi đóng phiên" | `stamp`, `check`, `prompt` |
| Đổi tài khoản | "sắp hết usage", "đổi tài khoản", "tạm stop" khi còn run đang chạy | `limit`, `switch` |
| Tra lại sau compact | cần lời Lead hoặc lệnh đã chạy trước compact (chỉ Claude Code) | `transcript_recall.py` |
| Chạy đêm | Lead giao việc chạy khi vắng mặt | `night init`, `night check`, `night report` |

Lệnh chạy từ folder skill: `python3 -B scripts/handoff.py <lệnh>`. Test: `python3 -B tests/test_handoff.py` và `python3 -B tests/test_transcript_recall.py`. Biến `HANDOFF_NOW="YYYY-MM-DD HH:MM"` cố định giờ máy, chỉ dùng khi test.

## Input

| Trường | Nguồn | Thiếu thì |
|---|---|---|
| Mục tiêu, entity, runtime nhận | Task hiện tại | Hỏi nếu đoán sai làm đổi mục tiêu |
| Nguồn chuẩn và output đã có | File thực sự đã đọc/kiểm tra | Ghi thiếu; không bịa evidence |
| Việc đã xong, quyết định, bước tiếp | Lịch sử task hiện tại | Phân biệt đã làm với dự kiến |
| Thư mục trả kết quả | Repo hoặc thư mục user đã chọn | Trả chat nếu chưa được phép ghi |
| Tài khoản đích, URL artifact kèm version | Lead, sổ artifact của workspace (nếu có) | Hỏi tài khoản đích; không đoán URL |

## Quy trình

1. Đọc luật của repo nhận; chỉ chọn nguồn liên quan đến bước tiếp theo. Không đưa raw, journal, secret hoặc nội dung ngoài quyền runtime nhận vào bản bàn giao.
2. Điền JSON theo `references/handoff-contract.md`: trạng thái công việc tách khỏi preference bền vững. Quyết định có nguồn; sự đồng ý cũ chỉ là lịch sử, không tự cấp quyền gửi/publish mới.
3. Chạy `python3 scripts/handoff.py create --spec <spec.json> --out <task_handoff_vN.md>` từ folder skill. Script kiểm file tồn tại, ghi hash, từ chối ghi đè. Nguồn thiếu → sửa danh sách hoặc ghi vào blockers, không đánh dấu đã xác minh.
4. Runtime nhận chạy `python3 scripts/handoff.py verify <task_handoff_vN.json>`. Nguồn đổi → đọc lại đúng file đổi và kiểm evidence bị ảnh hưởng; không chạy lại phần đã PASS chỉ vì đổi runtime.
5. Thực hiện bước tiếp theo theo quyền hiện tại và luật runtime nhận; gặp blocker thật thì nêu rõ. Render Markdown bằng công cụ của repo nếu có.

### Chế độ phiên mới

1. Sửa đè `HANDOFF.md` của workstream theo luật `_REFERENCE/luat-duyet-dieu-phoi.md`: 5 mục, dưới 60 dòng, `Trạng thái` có ngày. `Trạng thái` là một đoạn: mỗi phiên sửa đè đoạn đó, không thêm dòng trạng thái mới.
2. Ghi `Trạng thái` bằng `handoff.py stamp <HANDOFF.md> --note "<tối đa 3 câu>"`. Lệnh lấy giờ máy, thay cả mục bằng một dòng `dd/mm/yyyy HH:MM: <câu>` và giữ các dòng `Lane: …` của lane đang chạy. Khi đóng đợt, thêm `--drop-lanes` để bỏ các dòng đó. Mặc định lệnh chỉ in. Xem bản in, rồi chạy lại với `--write`. Không gõ giờ tay. Không chép giờ từ ngữ cảnh chat.
3. Liệt kê lịch hẹn trong phiên (Claude Code: CronCreate, ScheduleWakeup; runtime khác: capability tương đương). Lịch loại này chỉ sống trong phiên tạo ra nó và mất khi phiên đóng. Mỗi lịch còn cần thì ghi vào `Bước tiếp` kèm giờ, điều kiện chạy và file lệnh. Huỷ lịch không còn cần.
4. Chạy `handoff.py check <HANDOFF.md>`. Sửa mọi lỗi. Lỗi mới của v1.3: mốc giờ trong `Trạng thái` thiếu năm, hoặc sau giờ máy hơn 2 phút. `check` chỉ bắt mốc có ngày, nên ghi giờ dự kiến ở `Bước tiếp`, không ghi ở `Trạng thái`.
5. Xử lý cảnh báo của `check`:
   - "không thấy file": đường dẫn viết tắt thì viết đủ từ root.
   - `Trạng thái` dài hơn 3 câu: rút còn một đoạn ngắn.
   - HANDOFF ghi resume `wf_` hoặc `resumeFromRunId`: resume chỉ chạy trong cùng phiên. Thay bằng đường dẫn script workflow đã chép vào repo và bước chạy lại.
   - Nếu file quá 60 dòng, sao bản hiện tại vào `Archive/HANDOFF_<YYYYMMDD-HHMM>.md` cùng thư mục workstream, rồi viết lại bản gọn.
6. Chạy `handoff.py prompt <HANDOFF.md> --runtime <claude|codex|antigravity|hermes> [--extra "<dặn thêm của Lead>"]`. Prompt in giờ máy lúc tạo và nhắc trả lời tiếng Việt có dấu sau compact.
7. Nếu đã gửi prompt cho cùng việc, thêm `--supersedes "dd/mm/yyyy HH:MM"` với giờ của prompt cũ (dòng "Giờ máy lúc tạo prompt"). Dòng đầu prompt mới báo thay bản cũ. Prompt mới luôn là bản đầy đủ, không phải phần bổ sung.
8. Đưa prompt cho Lead dán sang phiên mới. Prompt trỏ tới HANDOFF và chép trạng thái, bước tiếp, các việc chờ Lead và lịch phải tạo lại kèm giờ. Prompt không chép transcript. Không viết prompt bàn giao bằng tay khi lệnh `prompt` chạy được.

Mục `Quyết định đã chốt` trong HANDOFF là tuỳ chọn. Nếu có mục này, `prompt` chép vào prompt với nhãn "không hỏi lại". Nếu cạnh HANDOFF có `decisions.md` hoặc `_tools/RECIPES.md`, `prompt` thêm đường dẫn. Cách lập hai file: `references/so-quyet-dinh-va-lenh.md` mục 2 và 3.

### Chế độ đổi tài khoản

Dùng khi Lead báo sắp hết usage, sắp đổi tài khoản hoặc cần reload phiên.

1. Chạy `handoff.py limit <HANDOFF.md> --session-dir <thư mục session> --lane <thư mục lane>`. Với Claude Code, thư mục session là `~/.claude/projects/<project>/<id phiên>/`. Lặp `--lane` cho mỗi lane.
2. Đọc kết quả. Lệnh kiểm HANDOFF, liệt kê run workflow sống (journal hoặc `agent-*.jsonl` sửa trong 10 phút, chỉ đọc mtime), và báo lane sẽ nhận lệnh checkpoint.
3. Chạy lại với `--write`. Lệnh thêm khối "Lệnh checkpoint" vào `inbox.md` của từng lane. Lệnh không ghi thêm khi khối trước chưa có dòng "Đã checkpoint lúc HH:MM". Không dùng SendMessage vào agent đang chạy.
4. Chờ lane ghi `CHECKPOINT.md`. Dừng run chưa ghi production (Claude Code: TaskStop). Run đã ghi production thì chờ xong, hoặc ghi vào HANDOFF. Dò agent đang chạy bằng `python3 tools/wf-status.py slots <thư mục session>` từ root repo. Luật lane và chủ run: skill `web-lane-orchestration`.
5. Chép script workflow đang dùng vào thư mục workstream trong repo. Script ở scratchpad hoặc ngoài repo mất khi đổi tài khoản.
6. Sửa đè HANDOFF bằng `stamp`, rồi chạy `check`.
7. Chạy `handoff.py switch <HANDOFF.md> --account <tài khoản đích> --artifact <URL>@<version> --script <script trong repo>`. Lặp `--artifact` và `--script` khi có nhiều. Lệnh trả mã 1 khi HANDOFF còn lỗi, URL artifact sai dạng, script không tồn tại hoặc nằm ngoài repo. Sửa rồi chạy lại.
8. Đưa prompt cho Lead. Ở tài khoản mới, dựng lại artifact theo skill `artifact-account-migration` (nếu repo có skill đó), hoặc publish lại từng bản local và ghi URL mới vào HANDOFF. Không chép bước của skill đó vào đây.

### Tra lại sau compact (chỉ Claude Code)

1. Trả lời tiếng Việt có dấu. Đọc `HANDOFF.md`, `decisions.md`, `_tools/RECIPES.md` theo `references/so-quyet-dinh-va-lenh.md` mục 4.
2. Nếu cần lời Lead hoặc lệnh đã chạy trước compact, chạy `transcript_recall.py`. Không grep hay đọc thẳng file transcript `.jsonl`.
3. Chạy lệnh từ thư mục mở phiên Claude Code, vì script chọn thư mục transcript theo thư mục hiện tại. Nếu chạy chỗ khác, thêm `--projects-dir ~/.claude/projects/<thư mục project>`.

```bash
python3 -B skills/runtime-handoff/scripts/transcript_recall.py sessions --limit 10
python3 -B skills/runtime-handoff/scripts/transcript_recall.py user <id> --grep "duyệt|chốt" --since "2026-10-19 18:00"
python3 -B skills/runtime-handoff/scripts/transcript_recall.py assistant <id> --last 5
python3 -B skills/runtime-handoff/scripts/transcript_recall.py tools <id> --name "Bash" --results 150
```

Script chỉ đọc. Script che key, token, JWT, IP, mật khẩu sau `-u`, và ẩn mọi đoạn nhắc BRAIN/journal. Tool result lớn chỉ in kích thước. Để che host staging hoặc slug riêng, đặt biến `STG_HOST` hoặc dùng `--needle-file <file>`. Không lưu file needle trong repo. Script in giờ dạng `dd/mm HH:MM`, nên thêm năm khi chép vào HANDOFF hoặc `decisions.md`.

### Chế độ chạy đêm

1. Chạy `handoff.py night init <thư mục workstream> --goal "<mục tiêu>"` để tạo `PLAN.md`.
2. Điền cùng Lead các mục sau:
   - `Được làm`, `Không được làm`, `Điều kiện dừng`.
   - `Hàng việc`: mỗi việc có tiêu chí xong.
   - `Việc local-only`: ít nhất 1 việc chạy được khi mọi tool hỏi quyền bị chặn.
   - `Giờ kiểm kế tiếp`: mốc `dd/mm/yyyy HH:MM`.
   - `Lịch đang sống`: mỗi lịch kèm giờ, hoặc ghi "không có".
   - `Heartbeat`: đường dẫn file mà agent ghi giờ sau mỗi việc.
3. Chạy `night check`. Nếu còn lỗi, không bắt đầu. PLAN cũ thiếu 4 mục mới sẽ báo lỗi: bổ sung trước khi chạy.
4. Không đưa vào `Hàng việc` các tool hỏi quyền: ArtifactData, Artifact publish, Monitor có `$(`, launch Workflow. Đêm không ai bấm duyệt, nên phiên treo. Chuyển các việc đó vào `Chờ Lead`. Ngoại lệ: PLAN có dòng "Đã thử lúc HH:MM khi Lead còn thức", ghi sau khi chạy thử thật mà không bị hỏi quyền. `Việc local-only` không có ngoại lệ. Hook `tools/hooks/artifact_away_guard.py` (chỉ có ở workspace của master) cũng chặn ArtifactData và Artifact publish khi Lead không nhắn 10 phút.
5. Trong đêm: chỉ làm việc trong `Được làm`. Xong việc nào thì đánh `[x]`, ghi giờ vào file heartbeat, và thêm một dòng `Nhật ký đêm`: giờ, tên việc, kết quả, đường dẫn bằng chứng. Việc ngoài phạm vi thì ghi vào `Chờ Lead` rồi làm việc kế.
6. Sáng: chạy `night report` và gửi bản báo cáo trong chat. Lệnh trả mã 1 khi có việc đánh `[x]` mà thiếu dòng nhật ký.

### Tự phản biện trước khi trình

Bản tốt nhất phải có:
- [ ] `check` không còn lỗi, HANDOFF dưới 60 dòng, `Trạng thái` là một đoạn sửa đè. Nguồn lỗi: HANDOFF site agency mẫu phình tới 88 dòng ngày 24/10/2026 vì nhiều phiên cùng thêm dòng trạng thái.
- [ ] Mọi mốc giờ trong HANDOFF lấy bằng `stamp`, có năm, không ở tương lai. Nguồn lỗi: phiên d61dfcca ngày 17/10/2026 ghi "chạy từ 13:20" lúc máy 13:09; HANDOFF GTV-Website ghi "24/10 12:35" thiếu năm.
- [ ] Prompt sinh bằng `prompt` hoặc `switch`, không viết tay; bản thay thế có `--supersedes`. Nguồn lỗi: phiên 6cae27d5 (20/10), e297d7d3 (21/10), 106e7e1d (22/10/2026) tự viết bàn giao, skill không được gọi.
- [ ] Prompt có bước tiếp làm được ngay, việc chờ Lead, và lịch phải tạo lại kèm giờ. Nguồn lỗi: phiên site agency mẫu đóng 24/10/2026, lịch V1-8 lúc 01:07 bị huỷ theo phiên và phải ghi tay vào prompt phiên mới.
- [ ] HANDOFF không ghi resume `wf_`; script workflow nằm trong repo. Nguồn lỗi: phiên e297d7d3 ngày 21/10/2026, HANDOFF ghi resume `wf_`, phiên mới không resume được.
- [ ] Lời chốt của Lead nằm nguyên văn trong `decisions.md` kèm giờ; HANDOFF chỉ trỏ tới file. Nguồn lỗi: agent hỏi lại điều đã chốt 8 lần trong 17–19/10/2026.
- [ ] Đổi tài khoản: `limit` chạy trước, `switch` trả mã 0, artifact có URL kèm version. Nguồn lỗi: 3 lần đổi tài khoản ngày 19/10/2026 tốn hơn 100 phút agent và khoảng 1,58 triệu token republish.
- [ ] PLAN chạy đêm qua `night check`: `Không được làm` gồm gửi, publish, ghi production, xoá; `Hàng việc` không có tool hỏi quyền; có việc local-only và heartbeat. Nguồn lỗi: đêm 18 sang 19/10/2026 phiên trống 500 phút sau khi PSI resume xong.

## Output

- Bàn giao có hash: `<task>_handoff_vN.md` + `.json` trong thư mục được chọn.
- Phiên mới và đổi tài khoản: prompt trong chat. `HANDOFF.md` sửa đè tại chỗ. `inbox.md` của lane khi chạy `limit --write`.
- Sổ quyết định và sổ lệnh: `<workstream>/decisions.md`, `<workstream>/_tools/RECIPES.md`.
- Chạy đêm: `PLAN.md` trong thư mục workstream và báo cáo sáng trong chat.

Bản bàn giao có hash có mục tiêu, entity, completed, decisions, pending, blockers, sources/hash và runtime đích. Không gửi sang task/bot khác nếu user chưa yêu cầu.

## Gate / tự kiểm

- Hash nguồn còn đúng; completed có bằng chứng, pending không bị ghi thành kết quả.
- Entity không lẫn; không có credential, journal, số nhạy cảm ngoài scope. File `RECIPES.md` qua `tools/leak_scan.sh`.
- Mốc giờ lấy từ giờ máy; `check` không còn lỗi trước khi sinh prompt.
- Bước tiếp cụ thể; kiểm quyền của runtime nhận trước hành động hướng ngoài.

## Anti-patterns

Chép cả transcript · grep cả file transcript sau compact · viết prompt bàn giao bằng tay · gõ giờ theo trí nhớ · ghi resume `wf_` làm bước tiếp · ghi “đã test” khi mới đọc code · đánh `[x]` mà không có dòng nhật ký · coi handoff là permission token · dùng hash thay cho đọc input chất lượng · chạy đêm khi `night check` còn lỗi · mở rộng `Được làm` trong đêm.

## Changelog

- v1.3.1 (2026-10-27): `stamp` giữ dòng `Lane:` trong mục Trạng thái, thêm `--drop-lanes` cho lúc đóng đợt; test ca hỏng thật. Nguồn: phiên 06e8cc9a ngày 26/10, stamp xoá dòng `Lane:` ít nhất 4 lần (`Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-skill-review_tong-ket-phien-2610_v1.md` mục 5).
- v1.3 (2026-10-25): lệnh `stamp`, `prompt --supersedes`, chế độ đổi tài khoản (`limit`, `switch`), `check` bắt mốc giờ thiếu năm hoặc ở tương lai và resume `wf_`, lint `night check` cho tool hỏi quyền và 4 mục mới, `transcript_recall.py`, reference `so-quyet-dinh-va-lenh.md`, description mới. Đề xuất coord-4, coord-5, ops2-5, hs-5, hs-6 (báo cáo `Deliverables/AI-Internal/Web-Skill-Review-2026-10/web-skill-review_bao-cao_v1.md` mục 6).
- v1.2 (2026-10-24): chế độ phiên mới thêm bước liệt kê lịch hẹn (lịch CronCreate mất khi phiên đóng), `Trạng thái` một đoạn sửa đè, HANDOFF quá 60 dòng thì sao `Archive/` rồi viết lại. Thêm 2 mục tự phản biện. Nguồn: phiên f00d80af site agency mẫu (`Deliverables/GTV-Brand/GTV-Website/gtv-website_tong-ket-phien-2410_v1.md` mục 2–3, `Archive/HANDOFF_20261024-1232.md`).
- v1.1 (2026-10-19): thêm chế độ phiên mới (`check`, `prompt`) và chạy đêm (`night init|check|report`). Lượt thử `check` trên 16 HANDOFF.md thật: 3 file vi phạm luật `_REFERENCE/luat-duyet-dieu-phoi.md` (2 file quá 60 dòng, 1 file quá 60 dòng và thiếu mục "Đã xong").
- v1.0 (2026-09-05): bản bàn giao có hash, verify và ranh giới quyền giữa runtime.
