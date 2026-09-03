---
name: gtv-project-okrs
description: "Lập / điều chỉnh / đối chiếu OKRs QUÝ của một dự án SEO client trong instance. Use when: (1) 'lên OKRs quý [N] cho [client]', 'chỉnh OKRs quý này', 'OKRs quý 2 nên như thế nào'; (2) 'đối chiếu OKRs với sheet team' sau khi team sửa sheet; (3) khép quý cần chấm điểm + carry-over."
---

# gtv-project-okrs — OKRs quý của dự án SEO

OKRs dự án sống ở **hai nơi cùng lúc** và đó là nguồn gốc của mọi rắc rối:

| Nơi | Ai sửa | Vai trò |
|---|---|---|
| **Google Sheet «OKRs Quý N»** của team | Team vận hành hằng ngày | Bản team thực sự dùng để chạy việc |
| `01-strategy-okrs/<CLIENT>_okrs-q<N>_v<N>.md` trong instance | GTV / Claude | Bản canonical đóng công đoạn #8, có baseline + backup plan + đã qua self-check |

Skill này giữ hai bản **không trôi khỏi nhau**: mỗi lần chạm OKRs đều bắt đầu bằng đọc sheet, kết thúc bằng ghi rõ đã đối chiếu tới ngày nào. **Bản .md không bao giờ được nói như thể nó là bản team đang chạy** khi chưa đối chiếu.

## Dependency check

| Cần | Kiểm | Thiếu thì |
|---|---|---|
| Sheet OKRs khai trong config | range OKRs trong `09-reporting/report-config.yaml` | Hỏi URL tab, thêm range rồi chạy lại |

> ⚠ **Tab OKRs đổi chỗ là chuyện thường.** CareerViet: Q1 dùng «OKRs Quý 1» trong *Kế hoạch tổng*, tới 04/08/2026 team chuyển Q2 sang tab **«3.1 OKRs Quý II» trong *Báo Cáo Kết Quả*** (bản client-facing). Hai nơi có tab nội dung như nhau — **hỏi team đang duy trì bản nào** rồi mới chốt `--range-key`/`--workbook`, đừng mặc định workbook cũ.
| Credentials service account | file `credentials` trong config | Không có → làm thủ công từ ảnh chụp sheet, ghi rõ giới hạn |
| Kết quả phân tích kỳ vừa khép | `09-reporting/analysis/<kỳ>-insights.md` | OKRs mới sẽ chỉ là bản chép lại nháp — nói thẳng điều đó, đừng giả vờ có căn cứ |

## Workflow 5 bước

### B1 — ĐỌC bản team đang dùng (không bao giờ bỏ)

```bash
python3 skills/gtv-project-okrs/scripts/okrs_sheet_diff.py \
    --config 09-reporting/report-config.yaml \
    --range-key okrs_quy_2_bckq --workbook bao_cao_ket_qua \
    --snapshot 02-raw/seo-data/okrs/<YYYY-MM-DD>/okrs-quy2-sheet.csv \
    [--compare 01-strategy-okrs/<CLIENT>_okrs-q2_v<N>.md]
```

- Snapshot CSV vào `02-raw/` (immutable, ngày trong tên folder) — đây là **nền đối chiếu**, ghi ngày vào frontmatter bản .md.
- Có `--compare` thì script in ra: Objective/KR **chỉ có trên sheet** · **chỉ có trong file** · **khác PIC/deadline**. Đây chính là việc «fact-check lại sheet của team».
- Sheet là bản team chạy → sheet nói khác thì **hỏi**, đừng mặc định file đúng.

### B2 — ĐỐI CHIẾU với kết quả kỳ vừa khép

Đọc `09-reporting/analysis/<kỳ>-insights.md` + điểm OKRs kỳ trước (`okrs_score.py` của skill `gtv-weekly-report`). Mỗi Objective phải trả lời được: **phát hiện nào của kỳ vừa rồi khiến Objective này tồn tại?** Không trả lời được = Objective đang chạy theo quán tính.

### B3 — RA DANH SÁCH QUYẾT ĐỊNH (đây là sản phẩm thật của bước phân tích)

Đừng nhảy thẳng vào viết OKRs mới. Ra một danh sách quyết định đánh số, mỗi quyết định một loại:

| Loại | Nghĩa | Ví dụ thật (CareerViet Q2) |
|---|---|---|
| **sửa** | Số/baseline cũ không còn đúng | O4 «chưa triển khai» → thực tế 3/26 hạng mục đã live |
| **chỉnh** | Cách đo / target / gộp KR | CR: target trung bình quý → target từng tháng, so nền cùng kỳ |
| **thêm** | KR mới mà kỳ vừa rồi chứng minh là cần | KR chuẩn hoá hệ đo (KR chặn) |

Trình danh sách này cho người quyết **trước khi** dựng bản mới. Người duyệt cần thấy *vì sao đổi*, không phải chỉ *đổi thành gì*. Chi tiết cách viết: `references/okrs-review-lenses.md`.

### B4 — DỰNG BẢN MỚI (hai file, một nội dung)

| File | Vai trò |
|---|---|
| `01-strategy-okrs/<CLIENT>_okrs-q<N>_v<N>.md` | **Canonical** — theo `_TEMPLATES/okrs.md`: ngữ cảnh quý · O/KR đủ baseline+target+owner+deadline · KPI cam kết vs stretch · backup plan có ngưỡng kích hoạt · nhịp theo dõi · ô chấm điểm |
| `01-strategy-okrs/<CLIENT>_okrs-q<N>_v<N>.html` | **Bản review** — mirror đúng cột của sheet team, tô màu 5 mức thay đổi + tô sáng phần chữ đã đổi. Để người duyệt nhìn 30 giây là biết đổi gì |

Luật cứng khi dựng:

1. **Trần KR mỗi Objective.** Chuẩn mặc định của trạm (`01-strategy-okrs/CLAUDE.md`) là **3–4 O × 3–4 KR**. Dự án nào chạy trần khác (CareerViet: **5 O × ≤5 KR**, Vincent chốt 04/08/2026 để giữ nguyên cấu trúc nháp của team) thì **ghi nhận chỗ lệch đó ngay trong deliverable**, không im lặng vượt. Vượt trần thì **gộp KR cùng theme** (cùng dây chuyền thực thi, cùng PIC, cùng cách nghiệm thu) — không cắt bừa KR đang có giá trị.
2. **Chưa có forecast thì chưa đặt số.** Ghi rõ «chốt số sau khi có forecast — hạn <ngày>», không đặt số đẹp rồi sửa sau (luật trạm `01-strategy-okrs/CLAUDE.md`).
3. **KR chặn phải đánh dấu là KR chặn** và nói rõ nó chặn cái gì.
4. **Không cam kết phần không lấy lại được.** Mất do cầu tìm kiếm biến mất thì ghi «không cam kết», đừng gói chung vào target khôi phục.
5. Không tự phát ngôn «đạt/không đạt KPI cam kết» khi `kpi-commitments.md` còn `draft`.

### B5 — CHỐT

1. Tự chấm **22 mục KO-01 → KO-22** trong `02-raw/knowledge/sop/06-self-checklist/checklist-kpi-okrs-planning.md` (5 mục P0: KO-01, KO-05, KO-10, KO-14, KO-19).
2. Chạy lại B1 với `--compare` sau khi team chỉnh sheet → cập nhật `fact_check:` trong frontmatter.
3. Trình **SEO Director** duyệt (KO-19). Claude **không** tự duyệt OKRs.
4. File-back: `index.md` bảng B dòng #8 (status + link) + bảng D (2 file) + `log.md` op `work`; khi Director duyệt thì thêm op `gate` kèm ngày duyệt.

## Ranh giới

- **Chỉ đọc** sheet của team — không ghi ngược lên Google Sheets.
- Không tự hạ target để OKRs dễ đạt; muốn đổi target phải nêu lý do bằng số và để người duyệt quyết.
- Framework OKRs (định nghĩa O/KR, SMART, cascade, thang điểm) là canonical ở skill `okrs-gtv-tag-framework` — skill này KHÔNG chép lại, chỉ áp dụng.
- Plan traffic chi tiết theo topic là canonical ở skill `traffic-plan` (KO-14: T1 không hoạch định traffic chi tiết).

## References

- `references/okrs-review-lenses.md` — 6 lăng kính rà OKRs nháp + cách viết danh sách quyết định + luật gộp KR + format bản HTML tô màu (nạp ở B2–B4).
- `02-raw/knowledge/sop/06-self-checklist/checklist-kpi-okrs-planning.md` — 22 mục self-check (nạp ở B5). Đây là file knowledge read-only, không chép lại vào skill.
- `_TEMPLATES/okrs.md` — khung bản .md canonical.
- `skills/okrs-gtv-tag-framework/` — framework lý thuyết (nạp khi cần định nghĩa/cascade/scoring).
- `skills/gtv-weekly-report/scripts/okrs_score.py` — chấm điểm kỳ khép + carry-over.
