---
name: acc-weekly-sync
description: "Sinh sync brief hằng tuần cho Account của dự án SEO GTV — nhịp TUẦN nội bộ giữa Account và SEO Lead Project: đọc SEO Production instance (index.md Bảng B 33 công đoạn + log.md) theo tháng dự án hiện tại (T1-T10), trả brief 5 phần: mốc cứng 2 tuần tới, công đoạn trễ >1 tuần kèm nguyên văn 'Rủi ro nếu trễ' (ngôn ngữ nói với khách), hạng mục KHÁCH đang giữ + số ngày giữ, red-flags check theo mục 06 tài liệu training (SLA quá 2 lần, coder >2 tuần, sau T6 traffic <70% lộ trình, đổi phạm vi, hỏi traffic users), và câu hỏi cho SEO Lead Project tuần này. Use when: (1) 'sync tuần [client]', 'chuẩn bị sync với SEO Lead', 'weekly brief Account cho [client]'; (2) 'dự án [X] đang trễ gì / khách đang giữ gì / có red flag không'; (3) 'tuần này hỏi SEO Lead cái gì', chuẩn bị nội dung nhắc khách về hạng mục đang giữ. KHÔNG dùng cho: báo cáo tháng/quý/nghiệm thu gửi khách (→ gtv-client-report — skill này là nhịp TUẦN nội bộ, không phải reporting), kick-off + checklist T1 (→ acc-kickoff-setup), audit/điều tra nguyên nhân SEO kỹ thuật khi KPI lệch (→ skill seo-*; skill này chỉ phát hiện + escalate)."
metadata:
  version: "1.0"
---

# Account Weekly Sync (T1-T10)

Nhịp lặp giá trị nhất của Account: **sync tuần với SEO Lead Project** — tiến độ vs mốc cứng, đang kẹt gì Ở PHÍA KHÁCH, phát hiện trễ sớm. Account không cần hiểu kỹ thuật sâu — chỉ cần thuộc **mốc nào, ai giữ, trễ thì mất gì**. Ground truth = tài liệu training `sop/09-project-timeline/quy-trinh-seo-10-thang-account.html` (mục 02-04, 06) + Bảng B `index.md` của instance.

🔒 **Sync brief là tài liệu nội bộ GTV** — không gửi khách nguyên bản. Riêng cột "Rủi ro nếu trễ" là ngôn ngữ đã được thiết kế để nói chuyện với khách; muốn dùng, Account trích + biên tập vào email/tin nhắn riêng.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Báo cáo tháng/quý/nghiệm thu cho khách (công đoạn #30/#32) | `gtv-client-report` | Skill này là nhịp TUẦN nội bộ — không render KPI vs cam kết, không đo số |
| Kick-off + checklist lấy từ khách T1 | `acc-kickoff-setup` | Skill này nhận bàn giao từ T1; checklist T1 còn thiếu → chỉ flag, không tự sinh lại |
| Điều tra nguyên nhân kỹ thuật khi KPI lệch | `technical-seo-audit` · `seo-onpage` · `content-refresh`… | Skill này chỉ phát hiện lệch + escalate đúng người, không chẩn đoán |
| Quyết định đổi phạm vi, plan lại traffic/timeline | SEO Lead Project + Director | Account KHÔNG tự hứa với khách — luật cứng |
| Cập nhật status Bảng B, chốt gate ◇ | Vận hành instance (SEO Lead / Executive) | Skill này CHỈ ĐỌC instance, không sửa index.md/log.md của dự án |

## Input

**Required:**
- `$INSTANCE` — path SEO Production instance của client (đọc `index.md` Bảng B + `log.md`, thêm `10-client-management/` + `12-feedback-lessons/` nếu có).
- `$MONTH` — tháng dự án hiện tại (T1-T10). Không rõ → suy từ bảng A (T1 = tháng dương lịch nào) + ngày hôm nay, xác nhận lại với user.

**Fallback (không có instance):** Account paste bảng tiến độ (công đoạn · tháng kế hoạch · status · ai giữ) + tháng dự án. Brief vẫn chạy đủ 5 phần, ghi rõ "data user cung cấp, không đối chiếu được log".

**Optional:**
- Ghi chú tuần của Account: khách vừa nói gì, lô content nào đang chờ duyệt từ ngày nào, coder đang giữ task gì, traffic hiện tại vs lộ trình (nếu Account có số từ báo cáo gần nhất).
- Gói timeline 8/12 tháng → đọc cột Tháng đã retiming trong Bảng B thay vì khung 10 tháng chuẩn.

## Workflow

### Bước 0 — Nạp trạng thái dự án

1. Xác nhận `$INSTANCE` + `$MONTH`. Đọc bảng A (gói, KPI, Lead/Account), Bảng B (cột Tháng · Status · Ghi chú · QC), `log.md` 10 op gần nhất, meeting note gần nhất nếu có.
2. Lệch giữa `$MONTH` user nói và suy ra từ bảng A → hỏi lại, không tự chọn.
3. Fallback paste → parse bảng user đưa, bỏ qua các check cần log.

### Bước 1 — Mốc cứng trong 2 tuần tới

Từ tháng hiện tại + bảng tháng (mục 04 training + Bảng B), liệt kê mốc cứng rơi vào ~2 tuần tới, mỗi mốc kèm: Account phải làm gì · khách phải chốt gì · deadline. Bảng mốc cứng chuẩn:

| Tháng | Mốc cứng Account phải giữ |
|---|---|
| T1 | Phân tích hợp đồng · kick-off (Account chủ trì) · lấy đủ access & thông tin trong 2 tuần đầu · chốt SLA duyệt + đầu mối duyệt |
| T2 | Push khách duyệt **cấu trúc + UX/UI trong 15 ngày đầu T2** · khởi động vòng duyệt content theo SLA · coder nhận template HTML và bắt đầu triển khai |
| T3 | Giữ SLA duyệt content — **khối lượng lớn nhất dự án T2-T4** · gửi báo cáo quý 1 + OKRs Q2 |
| T4 | Gửi initial ranking report + quản trị kỳ vọng · push coder xử lý technical audit Q2 |
| T5 | Nhịp báo cáo tháng · thu feedback content → đưa về PSP vá checklist ngành |
| T6 | Tổ chức **review giữa kỳ với khách** (kết quả T1-T6 + kế hoạch T7-T10) · gate mở → **chốt budget offpage ngay trong T6** |
| T7 | Push khách/coder xử lý FULL audit — technical sửa trước · **coder xử lý trong 2-3 tuần** · theo dõi hằng tuần |
| T8-T9 | Theo sát KPI vs cam kết · push duyệt CRO landing page · chuẩn bị dữ liệu chuyển đổi từ khách |
| T10 | Tổ chức **nghiệm thu** · báo cáo kép · xin case study · **đề xuất hợp đồng Duy trì** (Grow–Maintain–Decline) |

### Bước 2 — Công đoạn trễ >1 tuần

Đối chiếu cột Tháng (kế hoạch) vs Status thực tế Bảng B. Công đoạn trễ **>1 tuần so timeline** → liệt kê kèm: lý do (nếu log/ghi chú có) + phương án bù cần hỏi Lead + **nguyên văn "Rủi ro nếu trễ"** của tháng tương ứng (bảng mục 04 — dùng đúng câu này khi nói với khách):

| Tháng | Rủi ro nếu trễ (nguyên văn) |
|---|---|
| T1 | Thiếu access → audit + tracking chuyển đổi trễ (tracking bắt buộc xong ≤ T3) |
| T2 | Duyệt chậm cấu trúc → dây chuyền content → onpage → internal link trễ cả quý |
| T3 | Content URL SEO trượt mốc "hết T3" → initial ranking T4-T6 không có dữ liệu |
| T4 | Technical tồn → crawl/index kém, kéo lùi toàn bộ content đã đăng |
| T5 | Feedback dồn cục cuối dự án → sửa hàng loạt, tốn lực đôi bên |
| T6 | Chốt budget trễ → lỡ cửa sổ đỉnh backlink T6-T7, hiệu quả offpage giảm |
| T7 | Không sửa → 3 tháng cuối không còn thời gian cho hiệu quả kịp ngấm |
| T8-T9 | Thiếu dữ liệu chuyển đổi → báo cáo cuối chỉ có ranking/traffic, khó nghiệm thu giá trị |
| T10 | Không chốt duy trì → kết quả suy giảm sau 3-6 tháng, ảnh hưởng case study & tái ký |

### Bước 3 — Hạng mục KHÁCH đang giữ

Từ Bảng B (status `blocked`/ghi chú) + log + ghi chú tuần của Account: liệt kê từng hạng mục phía khách đang giữ + **số ngày đang giữ** (tính từ ngày gửi/giao) + SLA áp dụng:
- Duyệt content: lô nào, gửi ngày nào, quá SLA 3-5 ngày làm việc chưa, lần quá SLA thứ mấy.
- Coder: task technical nào (T2 cấu trúc / T4 audit Q2 / T7 full audit), giao ngày nào, quá 2 tuần chưa.
- Khác: duyệt cấu trúc/UX-UI, budget offpage, thông tin SP, dữ liệu chuyển đổi, duyệt CRO.
Không có ngày gốc trong data → hỏi Account, không ước lượng.

### Bước 4 — Red-flags check (mục 06 — escalate ngay, đừng đợi họp tháng)

Chạy đủ 5 cờ, mỗi cờ trả: TRIGGERED / CLEAR / THIẾU DATA (+ cách lấy):

1. **Khách duyệt content quá SLA 2 lần liên tiếp** → nhắc chính thức + escalate lên cấp trên phía khách; báo SEO Lead Project điều phối lại lịch content.
2. **Coder không xử lý technical >2 tuần** sau audit (T2 cấu trúc, T4 audit Q2, T7 full audit) → họp 3 bên Account + SEO + đầu mối khách, chốt lại deadline bằng văn bản.
3. **Sau T6 traffic <70% lộ trình cam kết** → chủ động yêu cầu review Manager/Director sớm (đừng đợi T8-T9), đồng thời chuẩn bị khách về kế hoạch điều chỉnh.
4. **Khách yêu cầu thay đổi phạm vi** (thêm nhóm sản phẩm, đổi domain/website, thêm thị trường) → KHÔNG tự cam kết; đưa về SEO Lead Project + Director đánh giá lại plan traffic và timeline.
5. **Khách hỏi về traffic users** → trả lời đúng bản chất: kỹ thuật rủi ro cao, chỉ triển khai khi SEO Director duyệt, không phải hạng mục mặc định của dự án.

### Bước 5 — Câu hỏi cho SEO Lead Project + render brief

1. Sinh 3-7 câu hỏi cụ thể cho buổi sync từ Bước 1-4, theo khung: task tuần này? mốc cứng nào sắp tới? đang kẹt gì ở phía khách? (+ câu riêng cho từng mốc trễ / cờ đỏ).
2. Render brief theo skeleton Output. Đặt tên `<client>_acc-weekly-sync_<YYYY-MM-DD>.md` → `10-client-management/` của instance (fallback: file rời). KHÔNG sửa `index.md`/`log.md` của instance — skill chỉ đọc.

## Output

```markdown
# <CLIENT> — Sync brief tuần <YYYY-Www> (T<n>/<gói>)
> Ngày: YYYY-MM-DD · Instance: <path | "data Account paste"> · 🔒 Nội bộ GTV — không gửi khách nguyên bản

## 1. Mốc cứng trong 2 tuần tới
| Mốc | Account làm | Khách phải chốt | Deadline |
|---|---|---|---|

## 2. Công đoạn trễ >1 tuần
| # | Công đoạn | Kế hoạch | Thực tế | Rủi ro nếu trễ (nguyên văn — dùng nói với khách) | Hỏi Lead phương án bù |
|---|---|---|---|---|---|

## 3. Khách đang giữ
| Hạng mục | Từ ngày | Số ngày giữ | SLA | Quá hạn? | Hành động tuần này |
|---|---|---|---|---|---|

## 4. Red-flags (mục 06)
| # | Cờ | Trạng thái | Evidence | Hành động escalate |
|---|---|---|---|---|
| 1 | Quá SLA 2 lần liên tiếp | TRIGGERED/CLEAR/THIẾU DATA | | |
| 2 | Coder >2 tuần | | | |
| 3 | Sau T6 traffic <70% lộ trình | | | |
| 4 | Đổi phạm vi | | | |
| 5 | Hỏi traffic users | | | |

## 5. Câu hỏi cho SEO Lead Project tuần này
1. <câu hỏi cụ thể, gắn mốc/công đoạn>

## Data còn thiếu
- <item THIẾU DATA + ai cung cấp>
```

## Behavior Gates

**#1 100 ngày mature** — Quản trị kỳ vọng luôn dùng nguyên tắc: content cần **~100 ngày để mature**; dây chuyền content → (+10-15 ngày) onpage → (+15-30 ngày) internal link → (~3 tháng) kết quả. Vì vậy **một mốc đầu dự án trễ 2 tuần = kết quả cuối dự án trễ cả tháng** — đây là lăng kính đánh giá mọi mốc trễ trong brief, và là câu giải thích với khách thay cho hứa hẹn.

**#2 Traffic users** — Không bao giờ mô tả traffic users là "chuẩn trắng" hay hạng mục mặc định; luôn trả lời đúng bản chất rủi ro cao, chỉ khi SEO Director duyệt.

**#3 Nội bộ** — Brief là nội bộ. Phần duy nhất mang đi nói với khách là nguyên văn "Rủi ro nếu trễ" + giải thích 100 ngày, qua biên tập của Account.

**#4 Evidence** — Số ngày giữ / lần quá SLA / % traffic phải truy được về ngày gốc trong log/ghi chú hoặc do Account cung cấp; không có → THIẾU DATA + cách lấy, không ước lượng.

**#5 Read-only + không tự hứa** — Không sửa instance. Mọi thay đổi phạm vi, cam kết mới, điều chỉnh timeline → route về SEO Lead Project + Director; brief chỉ ghi nhận + soạn câu hỏi.

## Anti-patterns

- ❌ Biến brief tuần thành báo cáo KPI cho khách — đó là `gtv-client-report`.
- ❌ Viết lại "Rủi ro nếu trễ" theo văn của mình — dùng nguyên văn bảng mục 04, đó là ngôn ngữ đã chuẩn hóa để nói với khách.
- ❌ Tự chẩn đoán nguyên nhân kỹ thuật ("chắc do onpage yếu") khi phát hiện KPI lệch — chỉ escalate + đặt câu hỏi cho Lead.
- ❌ Ước lượng số ngày khách giữ / số lần quá SLA khi không có ngày gốc.
- ❌ Bỏ qua red-flag vì "tuần này khách đang vui" — 5 cờ chạy đủ mọi tuần, cờ nào CLEAR ghi CLEAR.
- ❌ Hứa với khách về đổi phạm vi/timeline ngay trong tuần để "giữ quan hệ".
- ❌ Đợi họp tháng mới nêu cờ đỏ — mục 06 ghi rõ: escalate ngay.
- ❌ Sửa status/ghi chú Bảng B hoặc append log.md của instance khi chạy skill.
- ❌ Sync brief chỉ chép lại Bảng B — giá trị nằm ở phần 2-5 (trễ, khách giữ, cờ đỏ, câu hỏi), không phải liệt kê 33 dòng.

## References & wiki

- `SEO Knowledge/Semantic SEO A - Z/sop/09-project-timeline/quy-trinh-seo-10-thang-account.html` — ground truth: 3 nhiệm vụ (mục 02), lưu đồ (03), bảng tháng + rủi ro nguyên văn (04), red flags (06), nhịp tuần/tháng/quý.
- `SEO Production/index.md` — Bảng B 33 công đoạn (cột Tháng/Status/Ghi chú), Bảng C nhịp quý.
- `SEO Production/_TEMPLATES/meeting-note.md` — nếu buổi sync cần ghi note chính thức.
- Skill anh em: `acc-kickoff-setup` (T1, upstream) · `gtv-client-report` (báo cáo tháng/quý/nghiệm thu, downstream) · `technical-seo-audit`/`seo-onpage`/`content-refresh` (điều tra nguyên nhân khi Lead yêu cầu).

## Changelog

- **v1.0 (2026-07-19):** tạo mới — chưng cất nhịp sync tuần từ tài liệu training Account 10 tháng (mục 02-04, 06) + Bảng B SEO Production; brief 5 phần + 5 red-flags + gate 100 ngày mature.
