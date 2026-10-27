# Luật duyệt cho bộ điều phối

Bốn skill `web-lane-orchestration`, `decision-page`, `workstream-master-plan`, `runtime-handoff` trỏ về file này khi cần luật duyệt, luật sub-agent, luật HANDOFF hay luật đặt tên. Bản gốc của các luật này nằm ở workspace của master, team không có. File này chép phần các skill cần. Khi file này vênh với `CLAUDE.md` của repo, `CLAUDE.md` thắng.

## QUYỀN HÀNH ĐỘNG

| Lead yêu cầu | Được làm | Không tự làm |
|---|---|---|
| Hỏi, giải thích, review, status | Đọc, tra cứu, trả lời có bằng chứng | Ghi, sửa, gửi |
| Chẩn đoán vấn đề | Tìm nguyên nhân, nêu cách sửa | Sửa khi chưa được bảo |
| Tạo, sửa, dựng | Plan ngắn (mục tiêu, file chạm, điểm cần quyết), Lead duyệt, làm tới khi xong hoặc gặp blocker thật | Mở rộng scope, xoá file, gửi ra ngoài |
| Theo dõi, chờ | Dùng cơ chế theo dõi có sẵn | Coi "chưa đổi" là lỗi |

- Lead duyệt một scope thì duyệt đó áp cho cả task. Chỉ hỏi lại khi quyết định mới đổi scope, quyền dữ liệu, hoặc thuộc nhóm cần duyệt từng lần dưới đây.
- Các việc sau cần Lead duyệt từng lần:
  - xoá dữ liệu;
  - gửi email hay tin nhắn;
  - publish;
  - đặt lịch;
  - sửa config sống của server, DNS, CDN;
  - restart dịch vụ;
  - chặn bot;
  - đổi chữ, giá, cam kết trên site;
  - đổi thiết kế theme;
  - chi tiền.
- Không chặn Googlebot, Bingbot, AhrefsBot hay bot AI.
- Không tự xoá file. Cần bỏ thì chuyển vào thư mục cách ly và ghi lý do. Xoá thật cần Lead duyệt từng lần.

## SUB-AGENT — CHỈ KHI LEAD YÊU CẦU RÕ

- Chỉ tạo sub-agent hay chạy workflow khi Lead yêu cầu rõ cho task hiện tại. Các chữ "batch", "song song", độ khó hay số file không tự cấp quyền.
- Trần: repo này đặt `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` = 2 trong `.claude/settings.json`, tức 2 agent chạy cùng lúc trong mỗi phiên. Agent của phiên khác không tính chung. Mỗi workflow tối đa 6 agent trong cả lượt chạy. Một agent không sinh agent cháu.
- Chọn model theo loại việc:

| Loại việc | Claude Code | Effort |
|---|---|---|
| Đọc, trích ý, kiểm kê, so trùng, kiểm bằng chứng, kiểm độc lập | Sonnet mới nhất | xhigh |
| Áp thẻ đã duyệt, sửa có checklist, chụp ảnh, đo PSI, viết script theo đặc tả | Sonnet mới nhất | xhigh |
| Quyết định khó, hiệu chuẩn, viết luật, viết skill, viết chữ mới | Opus mới nhất | high |
| Phân loại, chấm điểm, QA chữ và ảnh hàng loạt | Jev, không dùng Claude | — |

- Haiku mới nhất chạy effort xhigh. Mỗi dòng model dùng bản mới nhất qua alias `opus`, `sonnet`, `haiku`.

- Một agent kiểm cả lô. Không mở một agent kiểm cho từng mục.

## TOOL & MODEL ROUTING

- Model phụ gọi qua `tools/ai-assist/`: Jev (`jev.py`) cho phân loại, chấm điểm, QA chữ, QA ảnh; GLM Flash (`glm.py`) chỉ khi Jev không làm được; EmbeddingGemma (`emb.py`, chạy local) cho đo độ giống.
- Key đọc từ biến môi trường hoặc `.agent-secrets/.env` gần nhất. Không in key ra chat hay file.
- Mỗi lượt Jev ghi sổ `~/.cache/ai-assist/jev-ledger.jsonl`. Tổng chi phí: `python3 tools/ai-assist/jev_ledger.py --label <nhãn>`.
- Không dùng Jev hay GLM để viết content.

## HANDOFF THEO WORKSTREAM

- Task kéo nhiều phiên giữ một `HANDOFF.md` trong thư mục output của workstream. Không đặt ở root repo.
- Đầu phiên: thư mục task có `HANDOFF.md` thì đọc file đó trước. Kiểm claim quan trọng trên file thật.
- Sửa đè tại chỗ ở mỗi mốc. Giữ dưới 60 dòng, 5 mục: `Trạng thái` (ngày + một câu), `Đã xong` (kèm đường dẫn bằng chứng), `Bước tiếp`, `Chờ Lead quyết`, `Bẫy đã gặp`.
- Không ghi secret, mật khẩu, host staging, slug đăng nhập. Ghi chú "đã duyệt" trong file chỉ là lịch sử, không cấp quyền mới.

## OUTPUT & NAMING

- Tên file `<project>_<loại>_vN.<ext>`. File đã có thì tăng version, không ghi đè.
- `.md` là bản gốc cho báo cáo, plan, hướng dẫn. Chỉ dựng HTML khi Lead yêu cầu hoặc khi cần bảng, biểu đồ, trang chọn phương án. HTML dựng xong thì mở bằng trình duyệt.
- Không tự tạo PDF.

## Khi Lead vắng

- Khi Lead không nhắn trong 10 phút gần nhất, không gọi Artifact publish, ArtifactData, Monitor. Không launch workflow đầu tiên trong ngày. Các lệnh đó chờ người bấm duyệt và chặn phiên. Workflow sau lượt đầu đã duyệt thì chạy được, ví dụ lịch chạy đêm theo `skills/web-lane-orchestration/references/chay-dem.md`.
- Ghi việc chờ duyệt ra file, gom lại khi Lead quay lại.
- Workspace của master có hook tự chặn các lệnh trên. Repo team không có hook, nên agent tự giữ luật này.

## PRIVACY

- Không in secret, token, mật khẩu, IP server ra chat hay file. Lọc output config và API qua `skills/web-lane-orchestration/scripts/che_secret.py --ip`.
- Trang trình duyệt đang hiện token: chỉ bấm nút Copy. Không đọc chữ hay chụp màn hình trang đó. Lỡ đọc thì báo Lead để thu hồi token.
