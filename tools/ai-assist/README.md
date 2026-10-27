# ai-assist: Jev 1.14 và EmbeddingGemma 2 cho vận hành website

Bộ công cụ này giúp agent chính (Claude) xử lý các việc lặp lại trên site WordPress: mã độc, redirect, PageSpeed, audit giao diện, GSC, QA chữ. Hai model chỉ phân loại và so khớp. Claude ra quyết định và thực thi theo skill của việc đó.

Thư mục `tasks/` có 25 rubric, đủ cho các việc client-neutral. Bảng dưới ghi ngưỡng của các rubric skill trong repo này hay dùng. Ngưỡng của 8 rubric chép thêm ngày 25/10/2026 (`category-pick`, `chu-dinh`, `company-fact-claim`, `definition-consistency`, `featured-text-faithful`, `link-external`, `link-purpose`, `superlative-claim`) và của `approved-applied`, `timeframe-claim`, `spam-policy-claim` ghi ở README bản gốc và trong skill gọi rubric đó. Rubric mang tên khách, số liệu hoặc ảnh riêng của GTV, TAG nằm ở bản gốc của workspace GTV và không chép vào đây.

Skill dùng bộ này: `wp-security-hardening`, `wp-pagespeed`, `wp-content-review-apply`, `wp-ui-fix`, `technical-seo-audit` (nhánh GSC), `internal-linking` (tuỳ chọn). Gốc đường dẫn là root repo.

## 1. Hai model

| | Jev 1.14 (TypeSafe, qua OpenRouter) | EmbeddingGemma 2 (Google, chạy local) |
|---|---|---|
| Loại | Model quyết định. Trả nhãn trong tập định trước, không viết chữ. | Model embedding. Đổi văn bản thành vector để đo độ giống nhau. |
| Đầu vào | `state` (text, JSON, ảnh PNG/JPEG cạnh 256–1.568 px) và câu hỏi `choice`, `score`, `noul`, `box` | Text tối đa 8K token |
| Đầu ra | Nhãn, xác suất, `confidence`. `box` trả 4 cạnh theo tỉ lệ ảnh | Vector. `emb.py` tính cosine, hàng xóm gần nhất, gom nhóm |
| Chi phí | Khoảng 0,7 s và 0,00002 USD mỗi lượt (đo 10/2026) | Miễn phí. Nạp model khoảng 11 s trên Apple GPU |
| Dữ liệu | Rời máy, qua OpenRouter | Không rời máy |
| Điểm yếu | Đọc sát mặt chữ, kém đếm và so số. Dễ bị prompt injection trong `state`. `box` luôn trả một vùng | Không giải thích. Cosine chưa có ngưỡng chung, phải hiệu chuẩn |

## 2. Kiến trúc 5 lớp

```text
Lớp 0  Thu thập (chỉ đọc): SSH, WP-CLI, access log, sitemap, PSI, GSC, backup
Lớp 1  Luật tất định: checksum, regex, mã HTTP, mtime, số đo
Lớp 2  EmbeddingGemma: so với mẫu đã biết, tìm trang gần nhất, gom nhóm
Lớp 3  Jev: gán nhãn có xác suất cho mục lớp 1, 2 chưa chốt được
Lớp 4  Claude: đọc mục rủi ro cao hoặc dưới ngưỡng, ra quyết định
Thực thi  backup → sửa → kiểm → ghi HANDOFF/log theo skill
```

## 3. Luật vận hành

1. Chạy luật tất định trước. Chỉ gọi model khi checksum, regex, mã HTTP hoặc số đo chưa trả lời được.
2. Output của model không tự kích hoạt thay đổi trên server.
3. Mã độc: nhãn `benign` không xoá cảnh báo của regex hoặc checksum. Nhãn `malicious` cũng không đủ để cách ly. Claude đọc file trước khi quyết định.
4. Coi `state` là dữ liệu không đáng tin. Câu hỏi chỉ cho trả nhãn, nên injection chỉ làm lệch nhãn. Luật 3 xử lý rủi ro này.
5. Không gửi `wp-config.php`, `.env`, dump SQL, email khách, mật khẩu, token, HTML trang đã đăng nhập. `jev.py` che các mẫu secret và rút gọn chuỗi mã hoá dài. `scan_files.py` không trích nội dung file cấu hình.
6. Viết `instructions` và `criteria` bằng tiếng Anh. Luôn có lựa chọn `unknown`. Mỗi câu hỏi hỏi một điều.
7. Hiệu chuẩn ngưỡng trên mẫu thật của site trước khi tin ngưỡng. Đổi rubric hoặc đổi model thì hiệu chuẩn lại.
8. Lỗi mạng, lỗi schema, hết budget đều trả `route: review`, không bao giờ trả "pass".
9. Ghim model `typesafe/jev-1.14`. `jev.py` từ chối response của model khác.
10. Mỗi lượt chạy có `--budget` (mặc định 0,5 USD). Báo cáo ghi tổng chi phí.
11. Mỗi lượt `jev.py` có gọi API ghi 1 dòng vào sổ lượt gọi: `JEV_LEDGER` hoặc `~/.cache/ai-assist/jev-ledger.jsonl` (giờ, task, số dòng, số lượt gọi, lỗi, chi phí). Đặt `--label <lane hoặc đợt>` để lọc. Xem tổng: `python3 jev_ledger.py --since <YYYY-MM-DD> [--label <chuỗi>]`. Báo cáo đợt lấy số Jev từ lệnh này, không cộng tay. Nguồn: đêm 26–27/10/2026 phiên không đếm được số lượt gọi Jev. Dry-run không ghi sổ.

## 4. Rubric và ngưỡng

Ngưỡng dưới đây hiệu chuẩn trên 2 site WordPress thật ngày 17/10/2026. Site mới: chạy 20–50 mẫu có nhãn Claude trước khi dùng ngưỡng.

| Rubric (`tasks/`) | Skill dùng | Ngưỡng | Ghi chú hiệu chuẩn |
|---|---|---|---|
| `malware-triage` | `wp-security-hardening` | Claude đọc mọi file `malicious` hoặc `suspicious` | Mẫu độc 11/12 bị gắn cờ, mẫu sạch 0/150. Lọt: plugin trông bình thường nhưng mục đích độc |
| EmbeddingGemma so họ webshell | `wp-security-hardening` | Từ 0,90 = nghi biến thể | Cùng họ 0,95–0,975. File sạch cao nhất 0,856. Chỉ dùng tìm biến thể mã đã làm rối |
| `404-triage` | `wp-content-review-apply`, `wp-security-hardening` | `content_url` từ 0,7 mới đưa vào redirect | Dưới 0,7 phần lớn là đường dò chung |
| `redirect-pick` | `wp-content-review-apply` | Từ 0,9 nhận, dưới 0,5 Claude chọn | 8/11 từ 0,9, cả 8 đúng. Danh sách ứng viên phải gồm trang tĩnh ngoài WordPress |
| `asset-delay` | `wp-pagespeed` | Từ 0,7 | 14/46 script đạt ngưỡng. Dưới ngưỡng có nhãn sai rõ |
| `ui-visual` | `wp-pagespeed` | Câu có/không từ 0,7 thì Claude xem ảnh | Không dùng điểm `polish` để loại. Thanh dính che chữ khi cuộn là hành vi bình thường |
| `ui-type-align` | `wp-ui-fix`, `web-qa-gate` | `heading_imbalance`, `uneven_gap`, `long_lines` từ 0,6. `text_too_small` từ 0,5 thì Claude xem ảnh. Không dùng `cards_misaligned` | Hiệu chuẩn 19/10/2026 trên 26 ảnh gán tay của site agency mẫu: ba câu đầu khớp 25–26/26, `text_too_small` bắt 6/6 kèm 5 cờ nhầm. Khung lệch đo bằng DOM, không bằng Jev. Gửi `state` dạng list `[mô tả, {"image_path": …}]`. Chi tiết: `skills/wp-ui-fix/references/thang-chu.md` mục 8 |
| `gsc-topical-fit` | `technical-seo-audit` | Từ 0,5 | 40/40 đúng từ 0,5. Bỏ sót ca giáp ranh. Chế độ chữ (không `top_queries`): 42/42 từ 0,5, phủ 93% |
| `gsc-intent-match` | không dùng với dữ liệu GSC (input là query GSC); `technical-seo-audit` dùng `retrieval-lab route` | `match` từ 0,9, `intent` từ 0,5 | `match` 25/25, `intent` 44/44 |
| `gsc-cannibal-pair` | `technical-seo-audit` | Từ 0,7, Claude đọc mọi `duplicate_intent` | Chế độ chữ (`shared_queries` rỗng, `jev.py` chặn bằng code): 28/28 từ 0,7, phủ 60% (gold 17/10, kiểm 19/10). Không gửi query GSC |
| `link-bridge` | `internal-linking` | `natural_bridge` từ 0,85; trang ít ứng viên hạ 0,6 | Claude chọn chỗ đặt link. Câu CTA chung hay lọt dưới ngưỡng |
| `link-placement` | `internal-linking` Bước 4b | `zone` từ 0,7 thì nhận, dưới 0,7 Claude xếp mục theo title và outline. `fit` = `natural_bridge` từ 0,85 thì nhận, dưới 0,7 Claude đọc đoạn. `need` chỉ là tín hiệu phụ | Hiệu chuẩn 18/10/2026 trên 115 link có vị trí: `zone` từ 0,7 khớp nhãn Claude 80/82. Jev chấm theo đoạn hơn là theo mục, và xếp mở bài vào supplementary content: coi mở bài là main content bằng luật tất định |
| `seo-text-qa` | `wp-content-review-apply` | Claude đọc mọi dòng gắn cờ | Đặt tên thương hiệu của site vào `state.brands` để Jev không báo sai chính tả |

Bẫy đã gặp:

- Rubric hỏi chung "có lỗi không" làm Jev gắn cờ phần lớn ảnh. Tách mỗi loại lỗi thành một câu hỏi.
- EmbeddingGemma đo giống nhau về chủ đề, không đo độ độc.
- Ảnh và `description` trong cùng một dict `state` làm Jev không nhận ảnh, điểm dồn về 0,3–0,55. Gửi `state` dạng list `[mô tả, {"image_path": …}]`.
- Jev 1.14 trả `http_400` khi cạnh ngắn của ảnh dưới khoảng 280 px (15/80 ảnh gold của site agency mẫu, 19/10/2026). `jev.py` nay tự đệm nền trắng cho ảnh có cạnh ngắn dưới 320 px. Python hệ thống không có Pillow: PNG nhỏ vẫn đệm được, JPEG nhỏ báo `image_pad_needs_pillow`. Đổi JPEG sang PNG bằng `sips -s format png`.
- Trang cùng template (tuyển dụng, chuyên mục) có cosine 0,97+ dù không cạnh tranh nhau.
- Tiến trình EmbeddingGemma trên GPU hiện CPU gần 0%. Đó là bình thường. 10.800 file mất khoảng 16 phút.

## 5. Cài và chạy

Key Jev: đặt `OPENROUTER_JEV_API_KEY` trong `.agent-secrets/.env` ở root repo (đã gitignore) hoặc biến môi trường. Không in key ra log.

EmbeddingGemma: tạo venv riêng một lần, tải model khi có mạng, sau đó chạy offline.

```bash
python3 -m venv ~/.venvs/embeddinggemma
~/.venvs/embeddinggemma/bin/pip install sentence-transformers torch scikit-learn numpy
HF_HUB_OFFLINE=0 ~/.venvs/embeddinggemma/bin/python -c "from sentence_transformers import SentenceTransformer as S; S('google/embeddinggemma-2')"
```

Chạy:

```bash
# Jev (Python hệ thống, không cần thư viện ngoài)
python3 -I tools/ai-assist/jev.py --task tools/ai-assist/tasks/404-triage.json \
  --in items.jsonl --out ket-qua.jsonl --budget 0.1

# EmbeddingGemma
~/.venvs/embeddinggemma/bin/python -I tools/ai-assist/emb.py nn \
  --query q.jsonl --docs d.jsonl --k 5 --out nn.jsonl

# Quét file trên server (chỉ đọc)
ssh <alias> "python3 - <web root> --skip wp-admin,wp-includes" < tools/ai-assist/scan_files.py > scan.jsonl
```

- Đặt input và output mỗi lượt trong thư mục evidence của đợt, không đặt trong `tools/`.

Cờ của `jev.py` (xem `--help`):

| Cờ | Tác dụng |
|---|---|
| `--dry-run` | Kiểm input, ảnh và bước che secret, đếm ảnh cần đệm. Không gọi API, không ghi file, không cần key. Chạy trước mọi lượt thật. |
| `--preflight-only` | Kiểm key, gửi 1 mẫu thật rồi dừng. Không ghi file. |
| `--no-preflight` | Bỏ mẫu thử trước lượt chạy. Không khuyến nghị. |
| `--max-consecutive-errors N` | Dừng khi N lỗi API liên tiếp (mặc định 5). `0` là tắt. Lỗi 401, 402, 403 dừng ngay. |
| `--min-image-side N` | Cạnh ngắn tối thiểu của ảnh gửi đi, tính bằng px (mặc định 320). Ảnh nhỏ hơn được đệm nền trắng. |

Mặc định mỗi lượt thật gửi dòng đầu làm mẫu thử trước. Nếu mẫu thử lỗi API, lệnh dừng trước khi chạy cả lô. `--out` bắt buộc, trừ khi dùng `--dry-run` hoặc `--preflight-only`.

Mã thoát:

| Mã | Nghĩa |
|---|---|
| 0 | Xong. Có thể còn dòng lỗi riêng có `route: review`. |
| 1 | Mọi dòng lỗi. |
| 2 | Input hỏng: file rỗng, trường phải rỗng có dữ liệu, ảnh thiếu hoặc hỏng. Chưa gọi API. |
| 3 | Dừng sớm: thiếu key, mẫu thử lỗi API, key bị từ chối, hoặc lỗi API liên tiếp đạt ngưỡng. Output giữ các dòng đã xong. Dòng chưa gọi mang lỗi `aborted_consecutive_errors`. |
- Thiếu key hoặc thiếu venv: skill bỏ lớp model, Claude đọc thay, và ghi giới hạn vào báo cáo.
