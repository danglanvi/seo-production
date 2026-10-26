# Đo mốc và đo lại GEO qua API

Đọc file này ở bước "Đo mốc và đo lại" của SKILL.md. Gốc đường dẫn là root repo. Bước thu câu trả lời và lớp regex dùng script của skill `geo-answer-lab`. Skill này thêm bước tính KPI và so các lần đo.

## 1. Chuẩn bị

- `prompts.tsv`: cột `id`, `funnel`, `branded`, `topic`, `prompt` (tab). Chốt chữ của prompt trước khi đo. Giữ nguyên ID qua mọi lần đo.
- `brands.json` theo định dạng của `geo-answer-lab`: `own`, `own_domains`, `brands` (tên → regex chữ thường, alias). Giữ cố định tập brand qua các lần đo, vì SoV tính trên tập này.
- Thư mục `<W>` = `08-geo-ai-visibility/<CLIENT>_geo-answer_<YYYY-MM-DD>/`. Mỗi lần đo một thư mục.

## 2. Chạy một lần đo

```bash
python3 -I skills/geo-answer-lab/scripts/collect.py --prompts <W>/prompts.tsv --out <W>/raw.jsonl --runs 3 --budget 8
python3 -I skills/geo-answer-lab/scripts/prepare.py --raw <W>/raw.jsonl --prompts <W>/prompts.tsv \
  --brands <W>/brands.json --out-dir <W>
python3 -I skills/geo-tracking-prompt-selection/scripts/geo_kpi.py kpi --raw <W>/raw.jsonl --det <W>/det.jsonl \
  --citations <W>/citations.jsonl --prompts <W>/prompts.tsv --brands <W>/brands.json --out-dir <W>/kpi
```

- Nếu `collect.py` báo lượt lỗi (`http_429`, timeout), chạy lại cùng lệnh. Script bỏ qua lượt đã có `ok=true`.
- Đặt `--budget` theo số lượt. `collect.py` mặc định dừng ở 5 USD. Bộ 30 prompt × 3 engine × 3 lượt của site mẫu 18/10 tốn 6,6 USD: ChatGPT 4,1 USD, Gemini 2,0 USD, Perplexity 0,5 USD.
- `geo_kpi.py kpi` ghi `kpi/kpi.json` và `kpi/by_prompt.tsv`. Mỗi engine có các số sau:
  - Tỷ lệ nhắc brand, tỷ lệ nhắc ở BOFU, tỷ lệ trích domain, SoV. Mẫu số là câu trả lời hợp lệ của prompt không mang tên brand.
  - Số câu trả lời lỗi và model thật đã trả lời (`models_served`).
  - URL của brand chính được trích. Mỗi câu trả lời đếm mỗi URL một lần.
  - Chênh giữa các lượt chạy (`run_spread`). Số này chỉ mô tả. Không dùng số này làm ngưỡng nhiễu (xem mục 4).

## 3. Bẫy của từng engine

Đo thật qua OpenRouter ngày 18/10/2026.

| Engine | Model 18/10 | Bẫy | Cách xử lý |
|---|---|---|---|
| ChatGPT | `openai/gpt-6.1-sol`, plugin web `native`, reasoning effort low | Chiếm 62% chi phí lượt đo | Giữ đủ 3 lượt. Không cắt lượt của ChatGPT để giảm chi phí |
| Perplexity | `perplexity/sonar` | Sonar không nhận plugin web `native`. Sonar tự tìm web | `collect.py` gọi Sonar ở chế độ `builtin`, không gửi `plugins` |
| Gemini | `google/gemini-3.8-flash`, plugin web `native` (Google grounding) | Link trích dẫn có dạng `vertexaisearch.cloud.google.com/grounding-api-redirect/…`. Domain thật nằm ở `title` | `prepare.py` lấy domain từ `title`. `geo_kpi.py` chỉ đếm domain của Gemini, không đếm URL. Muốn biết trang nào được trích, đọc ChatGPT và Perplexity |
| Mọi engine | API trả lời khác app | Số đo qua API không bằng số người dùng thấy trong app | Chỉ so xu hướng giữa các lần đo cùng cách đo |
| AI Overview, AI Mode | Không có API | Không đo được qua OpenRouter | Ghi UNKNOWN, hoặc chụp tay 10 prompt BOFU ở cùng ngày đo |
| Mọi engine | Model đổi bản theo thời gian | Chênh có thể do model đổi | Ghi `model_served`. Khi cần so chặt, ghim model bằng `--engine-models` của `collect.py` |

## 4. Lịch đo lại: ngày 14, 30, 60

Ngày gốc là ngày ghi đợt sửa lên site, không phải ngày đo mốc. Nếu mốc đo cũ hơn 7 ngày so với ngày ghi, đo mốc mới ngay trước khi ghi.

| Mốc | Việc | Cách đọc |
|---|---|---|
| Ngày 0 | Đo mốc đủ 3 lượt, trước khi ghi đợt sửa | Đây là mốc so |
| Ngày 14 | Đo lại với cùng prompt, cùng engine, cùng số lượt | Tín hiệu sớm. Chưa kết luận |
| Ngày 30 | Đo lại | Kết luận tăng hoặc giảm khi ngày 14 và ngày 30 cùng chiều, và cả hai nằm ngoài nhiễu |
| Ngày 60 | Đo lại | Xác nhận kết luận. Quyết định đợt sửa tiếp theo |

- Không mở đợt sửa mới trên cùng nhóm trang trước ngày 60. Nếu mở sớm, số đo trộn tác dụng của 2 đợt.
- Prompt mới thêm sau mốc vào cohort riêng. Không thay prompt cũ chỉ vì brand đang thua.

Lệnh so:

```bash
python3 -I skills/geo-tracking-prompt-selection/scripts/geo_kpi.py compare --base <W ngày 0>/kpi/kpi.json \
  --new <W ngày 14>/kpi/kpi.json --change-date <ngày ghi> --out <W ngày 14>/kpi/compare.md
```

`compare.md` có các phần sau:

- Số ngày từ đợt sửa và mốc gần nhất (14, 30 hoặc 60). Script cảnh báo khi ngày đo lệch lịch hơn 3 ngày.
- Bảng theo engine: mốc, đo lại, chênh, khoảng 95% của chênh, cách đọc.
  - Script tính khoảng này bằng bootstrap theo prompt, ghép cặp 2 lần đo.
  - Nếu khoảng chứa 0, script ghi "trong nhiễu".
- Cảnh báo:
  - Model đổi.
  - Ít hơn 3 lượt chạy.
  - Prompt đổi chữ: script bỏ prompt đó khỏi phép so.
- Prompt đổi từ 2/3 lượt trở lên: đọc câu trả lời gốc của các prompt này trước khi viết nhận định.

Thử A/A trên site mẫu 18/10, cùng ngày, không có thay đổi thật:

- Nếu dùng chênh giữa các lượt làm nhiễu, script báo sai "tăng" hoặc "giảm" ở 6/9 ô.
- Bootstrap ghi "trong nhiễu" ở 35/36 ô. Ô còn lại sát biên (cận trên −0,4 điểm).
- Với bộ 27 prompt không mang tên brand, khoảng 95% rộng 10–25 điểm %. Chênh dưới khoảng 10 điểm thường không đọc được. Muốn đọc chênh nhỏ hơn, tăng số prompt hoặc số lượt từ lần đo mốc.

## 5. Ghi kết quả

- Mỗi số ghi ngày đo, engine, model và cách đo (API, web search). Số là directional.
- Báo cáo khách dùng bảng của `compare.md` và câu: "số liệu là ảnh chụp ngày <ngày>, câu trả lời AI đổi theo lần chạy".
- Đọc vai trò của brand (được gợi ý hay chỉ được nhắc), bằng chứng và phản đối bằng skill `geo-answer-lab`.
