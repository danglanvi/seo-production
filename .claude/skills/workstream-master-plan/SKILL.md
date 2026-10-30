---
name: workstream-master-plan
description: "Giữ sổ yêu cầu và master plan của workstream dài trong plan.json, dựng trang HTML và báo cáo phiên có tiến độ đếm từ file, rà tin chưa vào sổ. Dùng khi workstream kéo nhiều phiên hoặc Lead giao nhiều việc nối tiếp."
metadata:
  version: "1.0.2"
---

# workstream-master-plan — mọi yêu cầu vào plan.json trước khi làm

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

Workstream dài làm rơi việc khi yêu cầu chỉ nằm trong chat. Compact hoặc đổi phiên làm mất phần đó. Skill này giữ một `plan.json` cho mỗi workstream. Script ghi giờ, kiểm schema, đếm tiến độ và dựng trang. Agent không tự gõ giờ và không báo tiến độ theo trí nhớ.

## Khi nào dùng

- Workstream dự kiến kéo nhiều phiên, hoặc Lead giao từ 5 việc nối tiếp trở lên.
- Lead hỏi "còn việc gì", "xong chưa", hoặc nhắc việc bị quên.
- Mở lại workstream đã có `plan.json`.
- Không dùng khi task xong trong một phiên. Không dùng thay `HANDOFF.md`: HANDOFF giữ trạng thái phiên theo luật `_REFERENCE/luat-duyet-dieu-phoi.md` mục HANDOFF THEO WORKSTREAM, còn plan giữ toàn bộ việc.
- Trang cho Lead chọn phương án: dùng skill `decision-page`. Bàn giao sang runtime khác: dùng skill `runtime-handoff`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Thư mục workstream | Thư mục output chính, ví dụ `<WS folder>/master-plan/` (WS folder theo `_REFERENCE/folder-map.md`) | Hỏi. Không đặt ở root repo |
| Tin của Lead | Transcript Claude Code `~/.claude/projects/<thư mục dự án>/<session-id>.jsonl`, hoặc file text tin nhắn của runtime khác | Nhờ Lead dán tin vào file text. Ghi giới hạn "chưa rà transcript" trong báo cáo |
| Export thẻ duyệt (tuỳ chọn) | JSON thẻ của trang duyệt và `mark_applied.json` | Bỏ phần rà thẻ, ghi giới hạn |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | Phân loại tin "có việc" hay "không có việc" | Không dùng ở v1.0. Chưa có rubric hiệu chuẩn. `audit_open.py` so chuỗi tất định trong khoảng 1 giây trên transcript 397 MB. Nếu một lượt rà có trên 100 tin mở và việc này lặp lại, hiệu chuẩn rubric bằng `model-calibration` rồi mới giao Jev |
| EmbeddingGemma 2 | Khớp tin với ask theo nghĩa | Không dùng. Chưa có số đo. Claude đọc danh sách tin mở để bù phần khớp chuỗi bỏ sót |
| GLM Flash | Trích câu | Không dùng. Claude trích ask khi đọc tin |
| Claude | Đọc tin mở, viết ask, chia việc, gắn phụ thuộc, kiểm duyệt | Dùng |
| Script | Giờ, schema, lint, tiến độ, dựng HTML và MD, rà tin | `plan.py`, `build.py`, `audit_open.py` |

## Quy trình

Chạy lệnh từ root repo. Đặt `S="skills/workstream-master-plan/scripts"` và `PL="<thư mục>/plan.json"`, luôn bọc trong nháy kép. Lệnh ghi mặc định là dry-run. Thêm `--apply` để ghi. Schema, lint và mã thoát: `references/plan-schema.md`.

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. **Mở hoặc tạo plan.** Nếu thư mục đã có `plan.json`, chạy `python3 "$S/plan.py" lint --plan "$PL"` và `progress --plan "$PL"` trước khi làm. Nếu chưa có, chạy `python3 "$S/plan.py" init "<thư mục>" --title "Master plan <tên>" --apply`. Plan cũ chưa qua lint: đọc `references/plan-schema.md` §8.
2. **Nhận yêu cầu.** Ghi mỗi tin mới của Lead vào sổ trước khi làm. Tính cả tin gửi giữa lượt, ghi chú trên thẻ duyệt và lời Lead do phiên khác chuyển.
   - Thêm việc trước: `python3 "$S/plan.py" add-item --plan "$PL" --title "<việc>" --phase P1 --source "Tin 25/10 09:12: <ý chính>" --program "<chương trình>" --deps "<ID>" --apply`.
   - Ghi yêu cầu sau: `python3 "$S/plan.py" add-request --plan "$PL" --ask "<trích nguyên văn, tối đa 200 ký tự>" --items "<ID1>,<ID2>" --apply`.
   - Nếu tin dài hơn 200 ký tự, chọn các đoạn nguyên văn từ 15 ký tự và nối bằng `…`. Không diễn đạt lại, kể cả khi script báo lỗi độ dài. Ca thật: 27/10/2026 22:25, ask 210 ký tự của tin 22:24 bị từ chối, lượt ghi lại dùng câu diễn đạt lại. Test: `test_tin_dai_noi_doan_nguyen_van_van_khop`.
   - Nếu tin là luật chung hoặc câu hỏi, dùng `--no-items-reason "<lý do>"` thay cho `--items`.
   - Không gõ giờ. Script lấy giờ máy.
3. **Kiểm duyệt trước khi đặt `need`.** Tra trạng thái thẻ, chat và ủy quyền chung của workstream. Nếu Lead đã duyệt, làm việc đó và không đặt `need`. Nếu chưa, chạy `python3 "$S/plan.py" set-status --plan "$PL" "<ID>" need --checked "<đã tra ở đâu>" --apply`. Gom việc `need` vào trang chờ quyết bằng skill `decision-page`.
4. **Làm và đóng việc.** Khi xong một việc, chạy `python3 "$S/plan.py" set-status --plan "$PL" "<ID>" done --evidence "<đường dẫn file, log hoặc số đo>" --apply`. Dùng `doing`, `wait`, `other` cho trạng thái khác.
5. **Rà việc sót ở mỗi mốc.** Chạy bước này trước mỗi lần ghi `Trạng thái` của HANDOFF bằng `handoff.py stamp`, trước báo cáo và trước khi đóng phiên. Ca thật: ngày 27/10/2026 phiên chỉ rà cuối ngày; lượt rà thấy 11/21 tin chưa vào sổ, gồm 5 luật vận hành. Chạy `python3 "$S/audit_open.py" --plan "$PL" --source "<transcript.jsonl hoặc tin.txt>" --since "<mốc phiên trước>"`. Nếu workstream có trang duyệt, thêm `--cards "<export.json>" --applied "<mark_applied.json>"`. Nếu mã thoát là 1, đọc từng tin mở, làm lại bước 2, rồi chạy lại tới khi mã 0.
6. **Dựng plan và báo cáo phiên.** Chạy `python3 "$S/build.py" --plan "$PL" --slug <project> --session-report --since "<mốc đầu phiên>"`. Lệnh này dựng trong bộ nhớ và chạy assert. Nếu mã 0, chạy lại với `--apply`. Mở file HTML theo luật `_REFERENCE/luat-duyet-dieu-phoi.md` mục OUTPUT & NAMING.
7. **Báo cáo cuối lượt.** Viết câu đầu bằng dòng `Tiến độ chương trình x/y` lấy từ build hoặc `plan.py progress`. Liệt kê việc xong trong phiên, việc đang làm và việc cần Lead quyết. Cập nhật `HANDOFF.md`: trỏ tới `plan.json` và dòng tiến độ, không chép danh sách việc.
8. Tự phản biện theo mục dưới, rồi kiểm Gate → trả.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] `audit_open.py` trả mã 0, hoặc mỗi tin còn mở đã có yêu cầu với `--no-items-reason`. Nguồn lỗi: ca thật 19–24/10 (workstream web), nhiều việc bị sót, Lead nói "ít ra cũng phải tạo một master plan".
- [ ] Câu đầu báo cáo là dòng "Tiến độ chương trình x/y" đếm từ file. Nguồn lỗi: ca thật 19–24/10 (workstream web), báo cáo chỉ ghi bước tiếp, Lead phải hỏi "các phần còn lại bạn đã làm xong chưa".
- [ ] Trang HTML và MD hiện đủ mọi ngày có yêu cầu, build không báo assert. Nguồn lỗi: ca thật 19–24/10 (workstream web), báo cáo bản đầu chỉ mở ngày cuối.
- [ ] Mọi mốc giờ do script ghi, không có lượt Edit sửa giờ trong `plan.json`. Nguồn lỗi: ca thật 19–24/10 (workstream web), agent gõ giờ tay và ghi sai nhiều lần.
- [ ] Không việc đã duyệt nào nằm ở "Cần Lead quyết", và mỗi việc `need` có `need_checked`. Nguồn lỗi: ca thật 19–24/10 (workstream web), việc đã duyệt bị ghi nhầm "chờ anh".
- [ ] Mỗi việc `done` có evidence kiểm được. Nguồn lỗi: ca thật 19–24/10 (workstream web), nhiều việc `done` không ghi evidence, lint chỉ bắt được khi chuyển plan sang script của skill.
- [ ] Kế hoạch đã duyệt nằm trong `plan.json`, không chỉ nằm trong chat. Nguồn lỗi: ca thật 19–24/10 (workstream web), kế hoạch chỉ nằm trong chat nên phiên mới không đọc được.

## Output

- `<thư mục>/plan.json`: nguồn duy nhất của sổ yêu cầu và danh sách việc.
- `<thư mục>/<project>_master-plan.html` và `.md`: build dựng lại và ghi đè bản dựng cũ.
- `<thư mục>/<project>_bao-cao-phien_vN.md`: N tự tăng, không ghi đè.
- Truyền `<project>` bằng `--slug` theo luật `_REFERENCE/luat-duyet-dieu-phoi.md` mục OUTPUT & NAMING. Không có `--slug` thì script lấy tên từ title.

## Gate trước khi trả

- [ ] `plan.py lint` báo 0 lỗi.
- [ ] `build.py` trả mã 0, và số đếm "ok {...}" khớp `plan.py progress`.
- [ ] `audit_open.py` trả mã 0, hoặc báo cáo nêu tin còn mở kèm lý do.
- [ ] `plan.json`, HTML và MD không chứa secret, host staging, slug đăng nhập hay mật khẩu. Script che token ở đầu ra của `audit_open.py`. Agent tự kiểm ask và detail do mình viết.
- [ ] Báo cáo ghi rõ nguồn chưa rà, ví dụ không có transcript.

## Anti-patterns

- Làm xong rồi mới ghi việc vào plan → ghi trước, đổi trạng thái sau.
- Sửa giờ hoặc trạng thái bằng Edit → dùng `plan.py`. Chỉ dùng Edit cho trường không có lệnh, rồi chạy lint.
- Báo "xong hết" theo trí nhớ → chạy `plan.py progress`.
- Dán cả tin dài vào ask → nối các đoạn nguyên văn bằng `…`, đặt chi tiết vào `--detail` của `add-item`.
- Viết lại ask bằng câu tóm tắt sau lỗi độ dài → cắt bớt đoạn trích, giữ nguyên văn.
- Sửa tay file HTML đã dựng → sửa `plan.json` rồi build lại.

## Kiểm thử

Chạy `python3 -m unittest discover -s "skills/workstream-master-plan/scripts/tests" -p "test_*.py"`: 52 test offline, gồm các ca hỏng thật. Ca eval ở `evals/cases.yaml`, chỉ đọc khi kiểm thử hoặc bảo trì.

## Changelog

- v1.0.2 (2026-10-27): Bước 5 chạy `audit_open.py` ở mỗi mốc `stamp` HANDOFF, trước báo cáo và trước khi đóng phiên. Bước 2: tin dài hơn 200 ký tự thì nối đoạn nguyên văn bằng `…`, không diễn đạt lại; thêm 1 test với tin thật. Nguồn: đợt rà skill speed 27/10 (`de-xuat_v1.md` mục 2.8, CP-32), lỗi `add-request` 22:25. Đã thử: `audit_open.py` trên master plan site agency mẫu và transcript phiên 486fd1fa (26 tin, 12 chưa vào sổ lúc 22:5x).
- v1.0.1 (2026-10-25): rút số và mã việc riêng của một workstream khỏi SKILL.md và `references/plan-schema.md`. Lệnh mẫu dùng `<ID>`. Nguồn lỗi của checklist ghi dạng "ca thật 19–24/10 (workstream web)".
- v1.0 (2026-10-25): tạo mới từ coord-1 và ops2-2: `plan.py`, `build.py`, `audit_open.py`, giờ do code ghi, dòng tiến độ chương trình, rà tin chưa vào sổ.
