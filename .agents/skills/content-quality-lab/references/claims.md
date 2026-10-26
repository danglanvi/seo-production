# Nhánh claims: chặn cam kết, tự xếp hạng, số không nguồn, số lệch bảng fact

Nạp file này ở bước chạy `quality.py claims`. Gốc đường dẫn là root repo.

## 1. Ba lớp

| Lớp | Bắt gì | Cách bắt | Cần model |
|---|---|---|---|
| 1. Regex | Hoàn phí, hoàn tiền, money-back; cam kết, bảo đảm, bảo hành kết quả, KPI, top, thứ hạng; "#1", "số 1", "top 1"; "hàng đầu"; "tốt nhất" | `L1` trong `quality.py`. Cụm có "không, chưa, never..." đứng trước trong 4 từ thì ghi phủ định, không tính | Không |
| 2. Jev `claim-guard` | Bảo đảm ngầm (không dùng chữ "cam kết"), tự xếp hạng, số liệu không nguồn, chủ thể của câu | `tasks/claim-guard.json`: 3 câu `noul` và câu `subject` dạng choice | Jev |
| 3a. Cụm cấm của bảng fact | Câu chạm "cách viết cấm" của fact cùng entity | `banned` trong `facts.json`, so tất định | Không |
| 3b. FactChecking | Câu có số nói cùng chỉ số với một fact nhưng số khác | EmbeddingGemma lấy 5 fact ứng viên, Jev `fact-match` chọn fact cùng chỉ số, code so số và entity | Gemma + Jev |

- Câu chỉ được gửi Jev khi chạm `TRIGGER` (số %, số có dấu "+", từ so sánh nhất, cam kết...) hoặc chạm lớp 1. Câu không chạm dấu hiệu nào thì Jev không đọc. Đây là giới hạn recall có chủ ý.
- Câu dài hơn 40 từ (bảng giá, ô liền nhau) được cắt thành cửa sổ ±12 từ quanh mỗi chỗ chạm dấu hiệu.
- Ô đếm tách 2 khối ("80" ở khối trước, "Chuyên gia" ở khối sau) được ghép lại trước khi so fact.

## 2. Bảng fact

- Schema dùng chung với `site-fact-consistency`: list `{"id", "entity", "metric", "value", "canon", "allowed", "banned", "decided", "decided_by", "quote", "source"}`. Truyền bằng `--facts`.
- Khai entity bằng `--entity "<MÃ>=<tên 1>|<tên 2>"`, lặp cho từng thương hiệu. Câu không nêu tên nào thì nhận `--site-entity`.
- Chỉ entity khai bằng `--entity` mới xét lệch entity. Câu nêu thương hiệu B mà fact gần nhất là của thương hiệu A thì ghi "lệch entity" và để người đọc. Không sửa số của B theo fact của A.
- Lớp 3a chỉ bắt được cụm có trong `banned`. Một fact có quy tắc theo thời gian (ví dụ "hơn N năm" chỉ đúng từ một ngày) phải ghi cụm đó vào `banned` tới ngày đó. Thiếu cụm thì câu khớp số sẽ ra "giữ".

## 3. Lệnh

```bash
A=(--rows <rows hoặc blocks.jsonl> --pages <pages.jsonl> --out-dir <W>/claims --owner "<tên chủ site>" \
   --facts <facts.json> --entity "<MÃ>=<tên>|<mã>" --site-entity <MÃ> \
   --registry 00-client-context/model-calibration.json --site <domain>)
python3 -I skills/content-quality-lab/scripts/quality.py claims "${A[@]}"
python3 -I tools/ai-assist/jev.py --task skills/content-quality-lab/tasks/claim-guard.json --in <W>/claims/jev_in.jsonl --out <W>/claims/jev_out.jsonl --budget 0.1
<venv>/bin/python -I tools/ai-assist/emb.py nn --query <W>/claims/fact_q.jsonl --docs <W>/claims/fact_d.jsonl --k 5 --qprompt SentenceSimilarity --dprompt SentenceSimilarity --out <W>/claims/fact_nn.jsonl
python3 -I skills/content-quality-lab/scripts/quality.py claims "${A[@]}" --jev-out <W>/claims/jev_out.jsonl --fact-nn <W>/claims/fact_nn.jsonl
python3 -I tools/ai-assist/jev.py --task skills/content-quality-lab/tasks/fact-match.json --in <W>/claims/fact_jev_in.jsonl --out <W>/claims/fact_jev_out.jsonl --budget 0.05
python3 -I skills/content-quality-lab/scripts/quality.py claims "${A[@]}" --jev-out <W>/claims/jev_out.jsonl --fact-nn <W>/claims/fact_nn.jsonl --fact-jev-out <W>/claims/fact_jev_out.jsonl
```

- `pages.jsonl` có thể là cả site. Lệnh chỉ lấy title, meta, h1 của trang có trong rows.
- Chạy lại sau khi sửa rows: chỉ gửi Jev câu có id mới, rồi nối vào `jev_out.jsonl`. Id câu là sha1 của chữ câu, nên câu không đổi giữ id cũ.
- Lệnh dừng khi registry thiếu cổng `claim-guard`, sàn `fact-check` hay cổng `fact-match` của đúng version. Hiệu chuẩn bằng skill `model-calibration` trước.
- Văn bản không phải trang web (copy nháp): dùng `--text <file> --url <URL dự kiến>`. Luật gửi Jev phụ thuộc chủ của site:
  - Bản nháp site khách (không có `--own-site`): lệnh không gửi Jev. `jev_in.jsonl` và `fact_jev_in.jsonl` rỗng, và lệnh dừng khi ghép `--jev-out` hay `--fact-jev-out`. Lệnh chỉ chạy regex, cụm cấm và Gemma trên máy. Claude đọc mọi câu chạm dấu hiệu, và `report.md` ghi rõ "không gửi Jev".
  - Bản nháp chưa đăng của site của chính đơn vị vận hành: thêm `--own-site`. Lệnh gửi Jev như trang đã đăng và chạy đủ chuỗi lệnh ở trên.

## 4. Đề xuất cho mỗi câu

`decide()` xét theo thứ tự. Câu khớp luật trước thì không xét luật sau.

| # | Điều kiện | Đề xuất |
|---|---|---|
| 1 | Regex hoàn tiền hay cam kết kết quả, hoặc Jev `guarantee` = yes | người đọc: chủ site quyết. Ngoại lệ: Jev chắc câu nói về bên khác và Jev `guarantee` = no thì giữ |
| 1b | Jev `guarantee` dưới cổng | người đọc: "Jev dưới cổng: guarantee" |
| 2 | Fact lệch ở dải "cụm cấm" hoặc "nhận", cùng entity | sửa theo fact |
| 3 | Jev `self_superlative` = yes và chủ thể là chủ site | xoá cụm so sánh nhất hoặc dẫn nguồn bên thứ ba |
| 3b | `self_superlative` = yes, chủ thể chưa rõ; hoặc regex so sánh nhất mà Jev chưa chạy hay dưới cổng | người đọc |
| 4 | Jev `unsourced_stat` = yes | thêm nguồn hoặc bỏ số |
| 5 | Dưới cổng `unsourced_stat`, lệch entity, fact lệch ở dải xám | người đọc |
| 6 | Còn lại | giữ |

`claims.tsv` xếp theo đề xuất, rồi câu chắc chắn (regex, nhãn yes, fact nhận) lên trước câu dưới cổng, rồi câu lặp nhiều trang lên trước.

## 5. Hiệu chuẩn trên site mẫu (19/10/2026, agency SEO, tiếng Việt)

Gold gán mù trước lượt model đầu, có sha256 và giờ. Holdout h4 lấy từ câu của lượt thử 1, chưa dùng ở bộ nào khác.

| Rubric, câu | Cổng | Dev | Holdout | Holdout h4 | Trạng thái |
|---|---|---|---|---|---|
| claim-guard `guarantee` | 0,75 | 0,962 (n 130) | 0,962 (n 53) | 0,979 (n 47) | dùng |
| claim-guard `subject` | 0,85 | chưa có gold | 1,0 (n 28) | 0,970 (n 33) | dùng |
| claim-guard `self_superlative` | 0,85 | 0,985 (n 131) | 1,0 (n 52) | 0,977 (n 44) | bản nháp |
| claim-guard `unsourced_stat` | 0,8 | 0,976 (n 125) | 0,976 (n 41) | 1,0 (n 34) | bản nháp |
| fact-check cosine, sàn | 0,82 | giữ 30/30 câu dương | giữ 20/20 | — | dùng |
| fact-match, ngưỡng none | 0,35 | precision 1,0 (n 19) | 0,976 (n 42) | 0,977 (n 43) | dùng |
| fact-match, cổng chọn fact | 0,8 | — | 0,975 (n 40) | 2 câu qua cổng | bản nháp |

- Số trong ngoặc là số câu có nhãn qua cổng. Độ đúng tính trên nhãn qua cổng.
- `self_superlative` và `unsourced_stat`: cổng chọn trên dev (0,6 và 0,65) đạt holdout cũ nhưng trượt h4 (0,931 và 0,865). Cổng hiện tại chặt hơn và đạt cả 3 bộ, nhưng được chọn sau khi xem h4. Cần holdout h5 để chốt.
- Câu dưới cổng vẫn chứa câu dương thật: `guarantee` dev 4/27, h4 3/13. Không bỏ qua dòng "Jev dưới cổng".
- Regex đơn lẻ không đủ: trên holdout 60 câu, regex `guarantee` bắt 2/5 câu dương và báo sai 2; regex so sánh nhất báo sai 19 câu trên 21 câu chạm.
- Cặp prompt EmbeddingGemma: SentenceSimilarity cả 2 phía tách tốt nhất trên 58 câu gold (câu dương thấp nhất 0,867). FactChecking/Document cho 0,772. SearchQuery/Document cho 0,755. `emb.py nn` nhận cả 3 qua `--qprompt`, `--dprompt`.
- Gemma có thể bỏ sót fact khi chữ của câu khác tên chỉ số. Ví dụ "80 Chuyên gia SEO" không có fact `staff` trong top 5. Câu số liệu công ty ra "giữ" thì Claude soát lại theo bảng fact.
- Chi phí lượt thử 25 trang: 1.100 câu `claim-guard` khoảng 0,06 USD, 948 câu `fact-match` khoảng 0,03 USD.

## 6. Đọc kết quả

- Cam kết, hoàn phí, bảo hành: chỉ ghi điểm lệch và nguồn đối chiếu (hợp đồng mẫu, trang điều khoản). Chủ site quyết bỏ câu hay giữ câu. Agent không viết câu cam kết mới.
- Câu lặp nhiều trang (cột `so_trang`): đọc một lần, sửa ở template hoặc khối dùng chung.
- "Sửa theo fact": ghi giá trị chuẩn, ngày chốt và câu gốc của fact. Lan truyền thay đổi bằng `site-fact-consistency`.
- "Xoá": bỏ cụm so sánh nhất hoặc thay bằng nguồn bên thứ ba có tên. Không thay bằng một cụm so sánh nhất khác.
- Lượt thử 25 trang ra 735 dòng, trong đó 568 dòng "người đọc" và 338 dòng là nhãn Jev dưới cổng. Gom theo trang và theo câu lặp trước khi đọc.
