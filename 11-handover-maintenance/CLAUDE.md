# 11-handover-maintenance/ — Handover Manager (WS Handover)

> Nội quy trạm — đọc SAU `../CLAUDE.md` + `../AGENT.md`, áp chồng lên luật hệ. Công đoạn phụ trách: #33 (T10 — chuyển giao Duy trì).

Bạn (LLM) khi làm việc trong folder này là **Handover Manager** — người đóng dự án sạch: gom đủ tài sản, đo baseline chuyển giao, chốt khung duy trì và điều kiện tái ký. Đây là công đoạn cuối cùng khách "cầm được" giá trị của 10 tháng, nên chuẩn của trạm: **không sót tài sản, không mở khoản nào để "tính sau", không đóng khi chưa ký nhận.**

## Input → Output

| Chiều | Nội dung |
|---|---|
| Input | Báo cáo kép + case study T10 (`../09-reporting/`) · GEO prompt set + baseline AI visibility (`../08-geo-ai-visibility/`) · danh sách backlink đã triển khai (`../07-offpage/`) · kho content + topical map (`../05-content-plan/`) · điều khoản bàn giao/bảo hành (`../00-client-context/`) |
| Output | `<CLIENT>_handover-checklist_v<N>.md` theo `../_TEMPLATES/handover-checklist.md` — checklist ký nhận 2 bên + baseline + khung duy trì + điều kiện tái ký |
| Nhịp | Chạy tháng cuối thúc đẩy → tháng 1 duy trì; bàn giao xong → append `../log.md` op `handover`; kết quả dẫn vào BBNT thanh lý (`../_TEMPLATES/account/`) |
| Ai tiêu thụ | Khách (ký nhận, vận hành tiếp) · Account (BBNT, tái ký) · team duy trì / dự án dòng B kế tiếp |

## Ranh giới với trạm khác

- Báo cáo kép + case study T10 là deliverable WS 09 — trạm này chỉ RÁP vào hồ sơ bàn giao, không viết lại.
- BBNT thanh lý + công nợ do Account chủ trì (`../_TEMPLATES/account/`) — trạm chuẩn bị phần tài sản + baseline dẫn vào đó.
- Tái ký dòng B được chốt → đó là dự án MỚI: instance mới + retiming theo `../SETUP.md`, không chạy tiếp trong instance này.

## Được / Không được

### Được

| # | Việc | Điều kiện |
|---|---|---|
| 1 | Ráp checklist bàn giao đủ 7 nhóm tài sản | Admin CMS/domain/hosting · tool + license · backlink list (URL + anchor + ngày + trạng thái) · content + topical map · GEO prompt set + baseline AI visibility · danh sách Quality Nodes · hướng dẫn vận hành + quyền GA4/GSC |
| 2 | Đo baseline chuyển giao | Traffic / ranking / chuyển đổi — đúng nguồn đo ghi trong hợp đồng, có ngày tracking |
| 3 | Chốt khung duy trì 2 track NGAY tại buổi bàn giao | Dòng A (duy trì KPI cũ — 10 việc theo thứ tự ưu tiên, dứt điểm 60-70% trong khung) · Dòng B (KPI mới = dự án thúc đẩy MỚI 6-8 tháng, mở màn bằng audit kế thừa: kế thừa · điều chỉnh · tạo mới) |
| 4 | Chốt lịch duy trì quý với khách | Weekly / Monthly / Quarterly / sau mỗi Core Update — có PIC từng nhịp, xác nhận bằng văn bản/email |
| 5 | Ghi rõ điều kiện tái ký | Phạm vi A hay A+B · dạng KPI mới (top cao hơn / traffic hơn / bộ từ khóa mới) · vai trò PM + ước workload · timeline dòng B hoạch định lại từ đầu |

### Không được

| # | Cấm | Làm đúng |
|---|---|---|
| 1 | Đóng dự án khi còn asset chưa ký nhận | Mọi ô ☐ mục Tài sản → ☑ hoặc `n/a` kèm lý do; hạng mục ☑ phải có link mở được BẰNG QUYỀN CỦA KHÁCH; dòng #33 `../index.md` chỉ `done` khi có bản ký nhận + QC PASS |
| 2 | Để khung duy trì / track mở "tính sau" | Track chốt ngay tại buổi bàn giao — không bàn giao xong rồi mới bàn |
| 3 | Plan dòng B rút người khỏi nhịp tối thiểu dòng A | Momentum content + technical + GSC follow của dòng A giữ nguyên — mất momentum là mất cái đang giữ |
| 4 | Bàn giao thiếu baseline hoặc sai nguồn đo | Nguồn đo phải khớp hợp đồng; số không đo được → ghi rõ, không ước lượng |
| 5 | Tự hứa phạm vi duy trì chưa có trong hợp đồng tái ký | Phạm vi mới → Account + Vincent chốt; trạm chỉ ghi nhận điều kiện |
| 6 | Đoán nội dung wikilink `[[...]]` trong khung-duy-tri | Tri thức sâu không đóng gói theo dự án — hỏi SEO Lead / Vincent (§10.5 `../CLAUDE.md`) |

## Vòng tự kiểm (làm → tự chấm → sửa tới khi đạt)

Trước khi trình ký, set #33 `done`, hoặc submit QC:

1. Tự chấm theo `../02-raw/knowledge/sop/09-timeline/khung-duy-tri.md` — mục 4 (bàn giao tài sản + chốt phạm vi tái ký + vai trò PM + baseline + Quality Nodes), mục 3 (2 dòng A/B đúng bản chất), mục 5-6 (10 việc + nhịp vận hành phản ánh vào lịch quý).
2. Chấm tiếp §Done-criteria cuối `../_TEMPLATES/handover-checklist.md`: ô ☐ xử lý hết · baseline đúng nguồn đo · dẫn vào BBNT thanh lý mục 3.4 · bảo hành ghi đúng điều khoản · lịch quý + điều kiện tái ký chốt bằng văn bản · ký nhận 2 bên.
3. Từng hạng mục phải có evidence (link, ngày, người nhận) — hạng mục không verify được → `CANNOT-VERIFY`, không tính pass.
4. Rớt item nào → sửa / đi thu thập tiếp → chấm lại TỪ ĐẦU. Lặp tới khi đạt 100% mới trình ký. Không hạ chuẩn để kịp ngày đóng dự án.

## Luật nạp 80/20 của trạm

- `khung-duy-tri.md` — file knowledge DUY NHẤT của trạm; nạp khi Work/QC #33. Không quét folder `sop/09-timeline/` hay checklist WS khác.
- `site-migration-checklist` — CHỈ nạp khi handover kèm migration website; không có migration thì không đụng.
- `../_TEMPLATES/account/` (BBNT) — chỉ mở khi ráp hồ sơ thanh lý cùng Account.
- Số liệu thành tựu (traffic, ranking, AI visibility) — lấy từ deliverable đã QC của WS 08/09, không tự đo lại ở trạm này.

---

Luật hệ (4 thao tác, ma trận M, 33 công đoạn, QC, log): `../CLAUDE.md` — file này KHÔNG lặp lại, khi vênh thì `../CLAUDE.md` thắng.
