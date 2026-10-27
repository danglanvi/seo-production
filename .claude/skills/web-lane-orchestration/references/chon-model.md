# Chọn model cho lane và agent kiểm

Mục đích: gán model và effort cho từng agent trong script. Đọc ở bước 5 của skill. Luật gốc nằm ở `_REFERENCE/luat-duyet-dieu-phoi.md` mục SUB-AGENT. File này chỉ ánh xạ vai trong skill sang loại việc của luật gốc. Khi hai file vênh nhau, theo luật gốc.

Nguồn lỗi: đợt rà 16–24/10, 99,7% lượt trả lời của agent chạy Opus, kể cả 113 agent cơ học. Ở t-106e, 96/96 agent đặt effort xhigh.

Cập nhật 27/10/2026 (Lead): Opus chạy effort high; Sonnet và Haiku chạy xhigh. Mỗi dòng dùng bản mới nhất qua alias `opus`, `sonnet`, `haiku`.

## Vai → loại việc trong luật gốc

| Vai trong workflow | Loại việc (luật gốc) | Đặt trong script |
|---|---|---|
| Lane chỉ đọc, chỉ đo (mốc, PSI, kiểm kê, audit mẫu C) | Đọc, kiểm kê, đo | `model: 'sonnet', effort: 'xhigh'` |
| Lane áp thẻ đã duyệt, sửa có checklist, chụp ảnh | Áp thẻ, sửa có checklist | `model: 'sonnet', effort: 'xhigh'` |
| Lane hạ tầng, theme, template, mu-plugin, config sống, quyết định theo ngưỡng, viết chữ mới | Quyết định khó, viết chữ mới | `model: 'opus', effort: 'high'`, `core: true` |
| Agent kiểm lane thường | Kiểm độc lập | `checkOpts`: Sonnet xhigh |
| Agent kiểm lane `core: true` và bước kiểm cuối đợt | Kiểm độc lập. Luật gốc xếp việc này vào Sonnet; mục 11 Lead duyệt 24/10 giữ Opus cho lane lõi | `checkOpts`: Opus high |
| Plan và phản biện plan (mẫu C) | Quyết định khó | Opus high cho plan và phản biện |
| QA chữ, QA ảnh, phân loại hàng loạt trong lane | Jev | Lệnh Jev trong task, không mở agent Claude |

Lint `tools/wf-status.py lint-script` báo ERROR khi một lời gọi `agent()` hoặc `goi()` thiếu `model` hay `effort`.

## Model phụ trong BRIEF

Mỗi lane có một dòng "Model phụ" trong `plan.json` (trường `model_phu`). `make_brief.py` báo lỗi khi thiếu dòng này. Dòng ghi phần giao Jev (rubric, ngân sách USD), phần dùng EmbeddingGemma 2, và lý do khi không dùng. Mẫu:

```text
Jev: <rubric theo bảng hiệu chuẩn trong tools/ai-assist/README.md>, ngân sách <USD>, chạy --preflight-only trước lượt đầu. EmbeddingGemma: <việc, hoặc "không dùng: lý do">. Claude: <phần còn lại, và đọc lại mục Jev gắn cờ>.
``` Luật gốc: `_REFERENCE/luat-duyet-dieu-phoi.md` mục TOOL & MODEL ROUTING, cách gọi ở `tools/ai-assist/README.md`.

## Trần agent

Trần số agent chạy cùng lúc và số agent mỗi workflow nằm ở luật gốc. Script đặt `SLOTS` không quá số slot còn trống. Trước khi launch, chạy `python3 tools/wf-status.py slots <thư mục session> --cap <CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS>`. Lệnh in số agent đang chạy; slot còn trống bằng cap trừ số đó. Đổi trần trong settings là việc Lead duyệt.
