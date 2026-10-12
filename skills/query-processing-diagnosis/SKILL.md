---
name: query-processing-diagnosis
description: "Chẩn đoán bộ keyword cam kết đã có hạng bằng Query Processing (gom template, URL Google chọn, SERP, trang thật, 8 trạm), ra topic ưu tiên, việc 2 tuần, deck HTML và file bàn giao cho team content. Dùng khi: 'phân tích QP [client]', 'vì sao keyword cam kết chưa lên', gate #22, refresh #24/#29."
metadata:
  version: "1.2"
---

# Query Processing Diagnosis: chẩn đoán bộ keyword cam kết

Hợp đồng đếm từng keyword, còn Google xử lý theo query đại diện của cả họ keyword. Skill này gom bộ keyword cam kết thành query template, đọc hạng theo họ, tìm trạm hỏng trong chuỗi 8 trạm xử lý query, rồi ra topic ưu tiên, kế hoạch 2 tuần, một deck HTML cho Lead và một file bàn giao cho team content. Quy trình rút từ đợt chẩn đoán 10 dự án GTV (10/2026, đã kiểm chéo).

## Khi nào dùng

- Bộ keyword cam kết đã có dữ liệu hạng: gate #22 "Initial ranking như kỳ vọng?", audit #24, #29, hoặc khi keyword cam kết đứng hạng hay rơi theo cụm.
- Không dùng khi:
  - Dự án mới, chưa có hạng: dùng `keyword-topic-url-mapping` (#4).
  - Chỉ cần gom cụm theo SERP: dùng `serp-clustering`.
  - Rơi diện rộng nghi do update, hack hay lỗi toàn site: chạy `tier-3-ranking-drop-runbook.md` của WS03 trước.
- Kết quả là bằng chứng cho gate #22. Verdict gate do Lead chốt.
- Team content không chạy skill này. Repo content đọc file bàn giao qua snapshot SEO (mục Output).

## Input

Lead điền phiếu `_TEMPLATES/qp-intake.md` (hướng dẫn cho team: `03-audits/ranking/README.md`). Phần A của phiếu là bắt buộc: khách và domain, người làm, file chứa bộ cam kết, engine hợp đồng, file export SpySERP (một hay nhiều file, đủ 35 ngày), project SpySERP, kỳ đo tới, ngày bắt đầu kế hoạch. Thiếu phần A thì dừng và hỏi đúng ô thiếu. Thiếu phần B thì làm tiếp, ghi "cần kiểm tay" (renderer tô đỏ).

Công cụ: Python 3 (thư viện chuẩn), curl. Audit deck cần Node ≥22 và Chrome; thiếu thì bỏ audit và ghi lý do.

## Quy trình chuẩn

`$S` = `skills/query-processing-diagnosis/scripts`. `$W` = `03-audits/ranking/_work/<CLIENT>_qp-chan-doan_v<N>`. Cách ra quyết định ở từng bước: `references/buoc-phan-tich.md`. Ngân sách là số tool call mục tiêu. Vượt gấp đôi ngân sách thì dừng lại xem đang làm thừa gì.

| Pha | Việc | Lệnh / thao tác | Nạp reference | Ngân sách |
|---|---|---|---|---|
| A. Nạp | Đọc song song: phiếu, `AGENT.md`, `03-audits/CLAUDE.md` (nội quy trạm), cheat-sheet `02-raw/knowledge/cheat-sheets/ws03-audit.md`, `kpi-commitments.md`, dòng công đoạn trong `index.md`, lessons WS03 nếu có. Rồi trong một lệnh: `qp_ranks.py bo <file bộ cam kết> [--col …] [--where …] -o $W/bo-cam-ket.txt` và `qp_ranks.py runs <các file export> --domain … --engine …` | đọc song song + 1 lệnh | `bay-da-gap.md` (Dữ liệu hạng) | 2–3 |
| **Điểm dừng** | Báo 3–5 câu: bộ keyword, engine, kỳ đo, khoảng ngày của export và lần chạy bị loại, dữ liệu thiếu, rủi ro. Export dưới 35 ngày, hoặc lần chạy mới bị nghi thiếu (project một domain) thì hỏi Lead ngay ở đây. Chờ Lead "ok" | — | — | 0 |
| B. Hạng | `qp_ranks.py table <các file export> --domain … --engine … --keywords $W/bo-cam-ket.txt [--targets …] -o $W/hang.json --tsv $W/hang.tsv`. Lệnh dừng mã 2 hoặc 3 thì làm theo mục "Khi lệnh table dừng" | 1 lệnh | — | 1 |
| C. Template | `qp_ranks.py terms … --keywords …` → viết `$W/rules.json` → `table --rules` (lặp tới khi hết keyword chưa có template, "khác" dưới 10%, tối đa 16 template) | terms + ghi + 1–3 lần table | `qp-ly-thuyet.md` mục 2 | 3–5 |
| D. SERP | 3 query đại diện của 3 intent, gọi song song trong một lượt | 1 lượt | `qp-ly-thuyet.md` mục 5 | 1–3 |
| E. Trang thật | `python3 $S/site_check.py $W/pages home=… cate=… …` cho mọi URL hub (`hub_urls` trong `hang.json`) và trang chủ, một lệnh | 1 lệnh | `bay-da-gap.md` (Trang thật) | 1–2 |
| F. Viết | `qp_scaffold.py $W/hang.json --slug … --name … --domain … --lead … --period … -o <file>.json` (tự điền mọi số) → viết các ô TODO trong **một lần ghi file**; ghi `$W/topics.json` | scaffold + 2 lần ghi | `schema-qp-project.md`, `qp-ly-thuyet.md` mục 3–8 | 3–5 |
| G. Dựng | `qp_build.py <file>.json --ranks $W/hang.json --topics $W/topics.json --web-out <file>_web.html --handoff 03-audits/ranking/<CLIENT>_qp-handoff-content_v<N>.md --numbers $W/con-so-nguon.md --shots $W/shots`. Sửa **mọi** lỗi in ra trong một lần sửa, rồi chạy lại. Đọc từng chỗ trúng của lệnh quét bản web | 1 lệnh, lặp 1–3 lần | — | 2–5 |
| H. Đóng | Xem ảnh slide Template, Ưu tiên, Kế hoạch (lệnh G tự chụp). Viết hồ sơ theo `_TEMPLATES/qp-chan-doan.md` (mục 2 dán từ `con-so-nguon.md`), tự chấm `references/checklist-qc.md`. Thêm dòng bảng D trong `index.md` và entry `log.md` | xem ảnh + 3 lần ghi | `checklist-qc.md` | 4–6 |

Tổng mục tiêu: 25–35 tool call cho một dự án (đợt 10/2026 dùng hàng trăm call và 11–32 script riêng cho mỗi dự án).

## Khi lệnh table dừng

- **Mã 2, không có mốc so sánh:** export không có lần chạy hợp lệ nào trong ±7 ngày quanh mốc 4 tuần trước. Thường do SpySERP chia lần chạy theo trang ("Schedules Page") hoặc export ngắn hơn 35 ngày. Xin Lead export thêm rồi truyền mọi file vào cùng lệnh. Lead không export thêm được thì chạy `--no-compare`: deck bỏ cột so sánh, không gắn "Đang lan", và ghi lý do vào flags. Không tự đặt mốc so sánh quá xa chỉ để có số.
- **Mã 3, gate nghiệp vụ:** project một domain có lần chạy mới bị nghi thiếu dữ liệu. Script không phân biệt được thiếu dữ liệu với rơi hạng thật. Hỏi Lead: site rơi thật thì chạy `--keep-recent`, SpySERP thiếu dữ liệu thì `--drop "<ngày>"`. Không tự chọn.

## Luật chống làm thừa

1. **Không viết script đếm riêng.** Số hạng, Top N, template, URL hub, keyword lệch URL target lấy từ `qp_ranks.py`. Số trên deck kiểm bằng `qp_build.py` (verify). Bảng "con số → nguồn" lấy từ `--numbers`. Chỉ viết script mới khi câu hỏi nằm ngoài các công cụ này; lưu vào `$W` và ghi vào hồ sơ.
2. **Không đọc file thô.** Không mở CSV SpySERP, HTML trang tải về hay deck đã dựng. Đọc output tóm tắt của script. `hang.tsv` chỉ mở khi cần xem keyword của một template, và chỉ đọc phần đó.
3. **Không gõ số hay keyword bằng tay.** Bộ cam kết trích bằng `qp_ranks.py bo`. Mọi số trong JSON đến từ scaffold. Volume lấy từ cột Volume của SpySERP trong `hang.json`. Sửa số thì chạy lại `qp_ranks.py` và scaffold sang version mới, không vá tay.
4. **Gom lỗi rồi sửa một lần.** `qp_build.py` in hết lỗi của khâu đang chạy. Sửa tất cả trong một lần ghi rồi chạy lại. Không sửa từng lỗi rồi chạy lại từng lần.
5. **Gọi song song** các việc độc lập: đọc nhiều file đầu vào, 3 lượt SERP.
6. **Không sub-agent, không kiểm chéo bằng agent.** Kiểm chéo bằng verify và checklist. Mỗi dự án một phiên; gộp nhiều dự án thì chạy lần lượt.
7. **Không mở trình duyệt để xem deck.** Audit đo tràn chữ. Chụp ảnh chỉ các slide bảng dài, một lần ở pha G cuối.
8. **Chỉ có một điểm dừng hỏi Lead** (sau pha A), trừ khi gặp gate nghiệp vụ thật: dữ liệu mâu thuẫn hợp đồng, site chưa live, hoặc lệnh table dừng mã 3.

## Output

Trong `03-audits/ranking/`:
- `<CLIENT>_qp-chan-doan_v<N>.json`: dữ liệu deck, nguồn duy nhất để sửa.
- `<CLIENT>_qp-chan-doan_v<N>.html`: deck nội bộ (có khối `kpi`). `_web.html`: bản bỏ phần nội bộ, dùng khi đưa ra ngoài nhóm dự án.
- `<CLIENT>_qp-chan-doan_v<N>.md`: hồ sơ theo template.
- `<CLIENT>_qp-handoff-content_v<N>.md`: bàn giao cho team content (template và URL Google chọn, topic và keyword mỗi topic đẩy, canonical, trạm hỏng ghi rõ phần nào team content làm, SERP, regex, bảng tra keyword). Sinh bằng `--handoff`, không sửa tay. Repo content kéo về bằng `project_sync.py pull` và dùng theo `_REFERENCE/query-processing.md` của repo content.
- `$W/`: `intake.md`, `bo-cam-ket.txt`, `rules.json`, `topics.json`, `hang.json`, `hang.tsv`, `con-so-nguon.md`, `pages/`, `shots/`.

File đã tồn tại thì tăng version. Chạy ở workspace GTV gộp nhiều dự án: `buoc-phan-tich.md` mục 13.

**Sửa theo feedback** ("sửa QP <CLIENT>: slide …"): sửa JSON → `qp_build.py` (cùng cờ `--handoff`) → báo lại. Ngân sách 3–5 call. Không chạy lại pha B–E nếu feedback không đổi dữ liệu.

## Gate trước khi trả

- [ ] `qp_build.py` qua cả check và verify (0 lỗi). Cảnh báo còn lại đã đọc và ghi lý do giữ. Audit 0 slide tràn, hoặc đã ghi lý do không chạy.
- [ ] 8 item P0 của `checklist-qc.md` đạt; tổng điểm đạt ngưỡng PASS.
- [ ] Giả thuyết và việc cần GSC hiện chữ đỏ, không viết như sự thật.
- [ ] Không có giá, phí, giá trị hợp đồng, email cá nhân. Deck đưa ra ngoài nhóm dự án dùng bản `_web`, và mọi chỗ trúng của lệnh quét bản web đã đọc lại.
- [ ] File bàn giao content đã sinh cùng version với deck.

## Anti-patterns

- Đọc hạng một ngày rồi kết luận → đọc median các lần chạy hợp lệ.
- Gắn "Đang lan" khi không có mốc so sánh → chạy `--no-compare`, trạng thái chỉ dựa vào hạng hiện tại.
- Đề xuất URL site "muốn" rank → lấy URL Google đang trả. Chỉ đổi khi có bằng chứng hai URL tranh nhau.
- Thêm nội dung cho cụm đang hỏng ở Retrieve hay Canonical → sửa trạm đó trước.
- Viết topic kéo traffic không gắn keyword cam kết → mỗi topic ghi keyword cam kết nó đẩy.
- Sửa HTML hay file bàn giao đã dựng → sửa JSON rồi dựng lại.

## Bảo trì

Sửa script thì chạy `python3 evals/test_scripts.py` (offline, phải in "Tất cả ca PASS"). `examples/mau-du-an.json` là dữ liệu minh hoạ cho test, không nạp khi chạy production. Ca hành vi: `evals/cases.yaml`.

## Changelog

- v1.2 (2026-10-12): sửa theo review 12/10. `table` dừng mã 2 khi không có lần chạy quanh mốc so sánh (trước đây ra "Đang lan" giả "0 → X"), thêm `--no-compare`; dừng mã 3 khi project một domain có lần chạy mới bị nghi thiếu (`--keep-recent` / `--drop`). Đọc CSV dấu `;`, `,` hoặc tab; gộp nhiều file export; đọc cột Volume; `--targets` đếm keyword lệch URL kế hoạch; lệnh `bo` trích bộ cam kết; median_high. Scaffold không cắt template âm thầm, không gắn "Đang lan" khi thiếu mốc. Verify thêm: tổng n template, trạng thái, ghi chú Top 10, ngày đo, hạng ghi trong chữ, volume; hạng một lần chạy chỉ còn là cảnh báo. `qp_build.py` thêm quét chữ dễ lộ điều khoản trên bản web, `--handoff` (bàn giao content), `--numbers` (bảng con số → nguồn), tự chọn slide để chụp. Pha A đọc thêm `AGENT.md`, nội quy trạm, cheat-sheet và chạy `runs` trước điểm dừng.
- v1.1 (2026-10-12): quy trình chuẩn 8 pha có ngân sách tool call; thêm `qp_ranks.py terms`, `qp_scaffold.py`, `qp_build.py` (verify), phiếu `_TEMPLATES/qp-intake.md`, README team ở `03-audits/ranking/`.
- v1.0 (2026-10-12): tạo mới từ đợt chẩn đoán 10 dự án GTV; renderer, `qp_ranks.py`, `site_check.py` đóng gói trong skill.
