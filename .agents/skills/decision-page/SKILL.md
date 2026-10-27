---
name: decision-page
description: "Dựng trang HTML chờ Lead quyết từ cau-hoi.json: bản local có nút Chép, bản artifact lưu câu trả lời vào db; rồi đổi câu trả lời thành danh sách việc. Dùng khi có việc lớn cần Lead chọn, thay cho file .md hay danh sách câu hỏi trong chat."
metadata:
  version: "1.0.1"
---

# decision-page — trang chờ Lead quyết, dựng từ JSON

> Bản SEO Production, sinh từ bản gốc của master bằng công cụ port. Không sửa tay: đề xuất sửa theo `_REFERENCE/self-improving.md`. Luật duyệt dùng chung: `_REFERENCE/luat-duyet-dieu-phoi.md`. Đường dẫn `Deliverables/…` trong phần nguồn lỗi là bằng chứng ở workspace của master, team không cần mở.

Lead không đọc được file `.md` và hay bỏ sót câu hỏi rải trong chat. Skill này dựng trang HTML từ một file JSON. Mỗi thẻ có đủ 4 ý và đúng một phương án đề xuất. Câu Lead để trống tính là theo đề xuất, trừ việc xoá và việc chạm config sống.

## Khi nào dùng

- Có việc lớn cần Lead chọn, nhất là khi việc cần ảnh, bảng hoặc số liệu để chọn.
- Lane web có mục chờ Lead quyết. Skill `web-lane-orchestration` trỏ sang skill này.
- Đọc câu trả lời của trang đã dựng: doc db của artifact hoặc chữ Lead dán từ nút Chép.
- Không dùng khi:
  - Việc là duyệt từng trường nội dung WordPress (title, meta, đoạn văn). Dùng `wp-content-review-apply`.
  - Chỉ có một câu hỏi nhanh và Lead đang chat. Hỏi thẳng trong chat.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Danh sách việc ứng viên | Phiên hiện tại, lane, audit, mục "Chờ Lead quyết" của `HANDOFF.md` | Không dựng trang |
| Cổng "vấn đề lớn" của workstream | File luật của workstream. Nếu workstream có file luật riêng, dùng cổng ghi trong file đó | Dùng mục QUYỀN HÀNH ĐỘNG của `_REFERENCE/luat-duyet-dieu-phoi.md`. Ghi trong `intro` rằng workstream chưa có cổng riêng |
| Quyết định đã chốt | `decisions.md` của workstream, `HANDOFF.md`, các file `*_cho-anh-quyet_v*.cau-hoi.json` cũ | Ghi "chưa có file quyết định" trong báo cáo. Bước 11 tạo file |
| Thư mục trả file | Thư mục output của workstream, ví dụ `<WS folder>/` theo `_REFERENCE/folder-map.md` | Hỏi. Không đặt file ở root repo |
| Ảnh trước và sau (khi cần) | File local cho bản local. URL `https://` hoặc `data:` cho bản artifact | Bỏ ảnh, ghi số đo vào `context` |

Mẫu đã duyệt, chỉ mở khi sửa script: `scripts/tests/fixtures/web-skill-review.json`. Bộ test dựng lại trang từ file này.

## Luật

- Câu để trống tính là theo đề xuất. Có hai ngoại lệ:
  - Thẻ có `touches_live: true`: việc sửa site, server hoặc config đang chạy.
  - Phương án đề xuất có `destructive: true`: xoá, gửi ra ngoài, tiền, pháp lý.
- Hai ngoại lệ trên hiện nhãn "Phải chọn". Agent chỉ làm khi Lead chọn rõ.
- Gửi Lead trang HTML. Không gửi file `.md`. Không thay trang bằng danh sách câu hỏi trong chat. Nguồn: Lead ngày 20/10/2026, "file md không thấy được".
- Không viết hoặc sửa HTML tay. Sửa `cau-hoi.json`, rồi dựng bản mới. Mỗi đợt câu hỏi là một bản mới.
- Cổng "vấn đề lớn" nằm ở file luật của workstream. Trỏ tới file đó. Không chép cổng vào skill hay vào trang.
- Khi Lead vắng, không để lượt Artifact hoặc ArtifactData chặn việc khác. Mọi lượt ArtifactData đều chờ người bấm duyệt, kể cả khi settings đã cho phép. Nguồn: đêm 20/10/2026, workflow đứng 03:14–08:35.

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | Phân loại ứng viên lớn hay nhỏ theo cổng. QA chữ của thẻ | Không dùng ở v1.0. Chưa có rubric "vấn đề lớn" đã hiệu chuẩn. Mỗi trang có 5–15 thẻ, nên Claude đọc lại nhanh hơn một lượt gọi. Khi một đợt có trên 30 ứng viên và lặp lại, hiệu chuẩn rubric bằng `model-calibration` rồi mới giao Jev |
| EmbeddingGemma 2 | So câu mới với quyết định đã chốt | Không dùng. File quyết định của một workstream ngắn. Claude tra theo nhãn thẻ và từ khoá |
| GLM Flash | Trích câu | Không dùng. Skill không có việc trích câu |
| Claude | Lọc theo cổng, viết thẻ, đọc câu trả lời, làm việc | Dùng |
| Script | Kiểm schema, dựng HTML, test Chrome, quét secret, đổi câu trả lời thành việc | Dùng `gen_decision.py`, `parse_answer.py` |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,chrome'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Chạy script từ root repo. Mỗi lệnh Bash mở shell mới, nên đặt biến ở đầu mỗi lệnh. Đặt đường dẫn trong nháy kép, vì tên workspace có hai dấu cách.

```bash
G="skills/decision-page/scripts/gen_decision.py"
P="skills/decision-page/scripts/parse_answer.py"
python3 -B "$G" --help
```

- Hai script dùng Python stdlib, chạy được trên Python 3.9. Script không gọi mạng và không gọi Artifact tool.
- `gen_decision.py` chạy thử theo mặc định. Thêm `--write` để ghi file.
- Mã thoát của hai script: `references/schema-cau-hoi.md` §8.

| Nhánh | Khi nào | Bước |
|---|---|---|
| A. Dựng trang | Có việc cần Lead quyết | 1–8 |
| B. Đọc câu trả lời | Lead báo đã trả lời, hoặc dán chữ từ nút Chép | 9–12 |

### Nhánh A — dựng trang

1. Gom việc ứng viên từ phiên, lane, audit và mục "Chờ Lead quyết" của `HANDOFF.md`.
2. Lọc theo cổng "vấn đề lớn" của workstream. Lấy cổng từ file luật ở bảng Input.
   - Việc nhỏ có đề xuất rõ, đảo ngược được, không phải xoá: tự làm theo đề xuất. Liệt kê việc đó trong một thẻ `done`.
   - Lỗi nhỏ tìm thấy khi audit: ghi vào backlog của workstream. Không soạn thẻ.
3. Bỏ câu đã chốt. Tra `decisions.md`, `HANDOFF.md` và các file `.cau-hoi.json` cũ. Nếu trang cũ còn chờ trả lời, đưa link trang đó vào `mo_tu_ban_cu`.
4. Viết `cau-hoi.json`. Đọc `references/viet-muc-cho-quyet.md` để viết thẻ. Đọc `references/schema-cau-hoi.md` để tra trường. Đặt file nháp trong `_data/` của workstream hoặc trong scratchpad.
5. Chạy thử, rồi sửa JSON tới khi mã thoát là 0:

   ```bash
   G="skills/decision-page/scripts/gen_decision.py"
   python3 -B "$G" "<cau-hoi.json>" --out "<thư mục workstream>" --both
   ```

6. Ghi, test và mở. Nếu runtime không phải Claude Code, bỏ `--both` để chỉ dựng bản local.

   ```bash
   G="skills/decision-page/scripts/gen_decision.py"
   python3 -B "$G" "<cau-hoi.json>" --out "<thư mục workstream>" --both --chrome-test --write --open
   ```

   - `--chrome-test` bấm Chép trong Chrome headless, nạp lại trang và ghi vào db giả. Lệnh so kết quả với dữ liệu. Nếu một ghi chú mất, lệnh trả mã 3.
   - `--open` mở bản local bằng Chrome thường. Sau đó lệnh kiểm có Chrome không headless đang chạy. Nếu lệnh trả mã 5, gửi Lead dòng "file URL" mà script đã in.
7. Publish bản artifact. Chỉ Claude Code làm bước này.
   - Nạp skill `artifact-capabilities` trước khi truyền `capabilities`. Artifact tool yêu cầu bước này.
   - Publish file `<project>_cho-anh-quyet_vN_artifact.html` bằng Artifact tool với `capabilities: {"db": {}}`, `icon: "checklist"` và description một câu.
   - Mỗi bản publish thành một URL mới. Không publish bản mới vào URL cũ. Doc `answers/lead` ở URL cũ còn câu trả lời của bản cũ, nên trang mới sẽ nạp lựa chọn cũ.
   - Nếu Lead có mặt, chạy ArtifactData `list` collection `answers` một lần. Kết quả rỗng là đúng.
   - Ghi URL vào `HANDOFF.md` mục "Chờ Lead quyết" và vào file `_khoi-phuc.md` của bản đó. Nếu trang dùng lâu hơn một phiên, đăng ký URL vào sổ artifact của workspace (nếu có).
   - Nếu Lead vắng và lượt publish chờ duyệt, làm việc khác trước. Publish khi Lead có mặt.
8. Báo Lead trong một tin: link artifact, file URL của bản local, số câu, số câu "Phải chọn" và luật để trống.

### Nhánh B — đọc câu trả lời

9. Lấy câu trả lời và lưu nguyên văn vào `_data/` của workstream:
   - Bản artifact: khi Lead báo đã trả lời, gọi ArtifactData `get` collection `answers`, doc `lead` trên URL của bản đó. Lưu JSON vào `<project>_tra-loi_vN.json`.
   - Chữ Lead dán từ nút Chép: lưu vào `<project>_tra-loi_vN.txt`.
10. Đổi câu trả lời thành danh sách việc. Dùng file `.cau-hoi.json` của đúng bản làm `--spec`:

    ```bash
    P="skills/decision-page/scripts/parse_answer.py"
    W="<thư mục workstream>"
    S="$W/<project>_cho-anh-quyet_vN.cau-hoi.json"
    python3 -B "$P" --spec "$S" --db "$W/_data/<project>_tra-loi_vN.json" --require-done
    python3 -B "$P" --spec "$S" --text "$W/_data/<project>_tra-loi_vN.txt"
    ```

    - Mã 3: chỉ hỏi Lead các dòng ở mục "Không khớp phương án" và "Cảnh báo".
    - Nếu chữ dán thiếu dòng của một thẻ, script đưa thẻ đó vào "Chờ chọn rõ". Nút Chép luôn in mọi thẻ hỏi, nên dòng thiếu nghĩa là chữ bị cắt. Nhờ Lead bấm Chép rồi dán lại.
    - Mã 4: Lead chưa bấm "Lưu, tôi trả lời xong". Hỏi một câu, hoặc đọc lại sau.
11. Ghi mục "Quyết định" vào `decisions.md` của workstream. Thêm `--into "<thư mục workstream>/decisions.md"`, chạy thử, rồi thêm `--write`. Lệnh thay mục cũ của cùng bản, nên chạy lại không nhân đôi. Không ghi mục này vào `HANDOFF.md`, vì HANDOFF giới hạn 60 dòng. HANDOFF chỉ giữ một dòng trỏ tới `decisions.md`.
12. Làm các việc ở mục "Làm". Không làm mục "Chờ chọn rõ". Giữ mục đó ở `HANDOFF.md` mục "Chờ Lead quyết". Nếu việc vẫn cần, đưa lại vào trang của đợt sau.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Mỗi thẻ hỏi có đủ 4 ý: bối cảnh, nếu bỏ qua, cờ config sống, hậu quả từng phương án. Mỗi câu có đúng 1 đề xuất. Nguồn lỗi: 19/10/2026 19:53, Lead "các phần còn lại tôi không hiểu ý bạn lắm".
- [ ] Trang chỉ có vấn đề qua cổng của workstream. Việc nhỏ đã tự làm nằm trong thẻ `done` hoặc backlog. Nguồn lỗi: 20/10/2026 21:0x, Lead "đưa tôi duyệt nhiều cái nhưng toàn mấy cái nhỏ".
- [ ] Không câu nào hỏi lại điều đã chốt trong `decisions.md` hay trang cũ. Nguồn lỗi: 8 lần Lead phải nhắc việc đã chốt, 17–19/10/2026 (báo cáo rà skill web mục 4).
- [ ] `--chrome-test` đạt: nút Chép giữ mọi ghi chú, nạp lại trang giữ lựa chọn. Nguồn lỗi: một bản dựng tay tháng 10/2026 làm mất ghi chú, Lead chờ khoảng 6 phút.
- [ ] Lead nhận link artifact và file URL, không nhận `.md` hay danh sách trong chat. Bản artifact có URL mới, đã ghi vào `HANDOFF.md` và `_khoi-phuc.md`. Nguồn lỗi: 20/10/2026 10:13 và 15:58, "file md không thấy được"; 19/10/2026 đổi tài khoản Claude làm mất trang duyệt site agency mẫu và trang plan SCN.
- [ ] Mỗi số trong thẻ lấy từ file dữ liệu bằng code, và đã so lại với file đó trước khi dựng trang. Script thay chữ trong JSON kiểm hết mọi chỗ thay rồi mới ghi file. Nguồn lỗi: trang quyết GTM bản 1 ngày 26/10/2026 sai số trung bình; lệnh Python thay chữ dừng giữa chừng vì assert nhưng file đã ghi một phần (bản sai ở `exec-2610/gtm-audit/backup/trang-v1-sai-so/`).
- [ ] Câu trả lời đi qua `parse_answer.py`. Câu trống ở thẻ "Phải chọn" không bị làm. Nguồn lỗi: HANDOFF đợt rà skill web 24/10/2026, hook và `~/.zshenv` chỉ làm khi Lead chọn rõ.
- [ ] Không có lượt ArtifactData chặn việc khi Lead vắng. Nguồn lỗi: đêm 20/10/2026 workflow đứng 03:14–08:35. Ngày 21/10/2026 một lượt query chặn phiên chính 182 phút.

## Output

- Trang: `<thư mục workstream>/<project>_cho-anh-quyet_vN.html`, kèm `_artifact.html`, `_khoi-phuc.md` và `.cau-hoi.json` cùng số bản. Script tự tăng N và không ghi đè.
- Artifact: một URL mới mỗi bản, `capabilities: {"db": {}}`. Câu trả lời nằm ở collection `answers`, doc `lead`.
- Câu trả lời: `_data/<project>_tra-loi_vN.json` hoặc `.txt`. Mục "Quyết định" trong `decisions.md` của workstream.
- Tin cho Lead: link artifact, file URL, số câu, số câu "Phải chọn".

## Gate trước khi trả

- [ ] `gen_decision.py` trả mã 0 với `--chrome-test --write`.
- [ ] Mọi thẻ hỏi qua cổng "vấn đề lớn". Thẻ không trùng quyết định đã chốt.
- [ ] Lead nhận link hoặc file URL. Trang local đã mở bằng Chrome.
- [ ] Trang không chứa secret, IP, host staging, slug đăng nhập. Không dùng `--allow-sensitive`.
- [ ] Câu trả lời đã qua `parse_answer.py`. Mục "Chờ chọn rõ" nằm ở HANDOFF, không nằm trong việc đã làm.
- [ ] Không bịa số liệu trong thẻ. Số chưa đo ghi "ước tính". Số đã đo khớp file dữ liệu ghi trong `context` của thẻ.

## Anti-patterns

- Sửa file HTML đã dựng để thêm câu. Sửa JSON, rồi dựng bản mới.
- Ép `--version` để ghi lại số bản cũ. Script từ chối. Để script tự tăng số bản.
- Chép cổng vào trang hoặc vào skill. Trỏ tới file luật của workstream.
- Gộp nhiều quyết định trong một câu hỏi. Tách mỗi quyết định thành một câu.
- Dùng mã nội bộ làm tiêu đề thẻ, ví dụ "M16" hay "scn-a1". Viết tác dụng của việc.
- Đặt ảnh cục bộ vào bản artifact. Dùng URL `https://` hoặc `data:`.
- Ghi mục "Quyết định" vào `HANDOFF.md`. Ghi vào `decisions.md`.

## Kiểm thử

- Test offline: chạy `python3 -B scripts/tests/test_decision.py` từ folder skill. Bộ test có 48 ca, dùng Chrome headless local và fixture trong `scripts/tests/fixtures/`.
- Ca thật trong bộ test: dựng lại trang đợt rà skill web 24/10/2026 từ `web-skill-review.json`, rồi so với `web-skill-review_cho-anh-quyet_v2.html`.
- Ca hành vi: `evals/cases.yaml`. Chỉ đọc khi kiểm thử hoặc bảo trì.

## Changelog

- v1.0.1 (2026-10-27): checklist gộp 2 mục link và URL artifact; thêm mục số trong thẻ lấy từ file dữ liệu bằng code, kiểm hết rồi mới ghi. Gate: số đã đo khớp file dữ liệu. Eval thêm 1 ca. Nguồn: trang quyết GTM bản 1 ngày 26/10/2026.

- v1.0 (2026-10-25): tạo mới từ mã coord-3 và ops2-1 (đợt rà skill web 16–24/10, Lead duyệt 24/10). Script `gen_decision.py` (local, artifact có db, Chrome test, kiểm cửa sổ Chrome) và `parse_answer.py` (trống = theo đề xuất, trừ xoá, config sống và chữ dán bị cắt).
