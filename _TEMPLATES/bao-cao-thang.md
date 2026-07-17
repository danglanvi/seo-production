---
client: "{{CLIENT}}"
cong_doan: "{{30 | 32}}"
ws: 09-reporting
che_do: "{{thang | quy | nghiem-thu}}"
thang: "T{{N}}"
ky_du_lieu: "{{dd/mm}}–{{dd/mm/yyyy}}"
ngay_tracking: "{{dd/mm/yyyy}}"
pic: "{{ACCOUNT}}"
status: draft
version: v1
---

# {{CLIENT}} — Báo cáo {{tháng | quý | nghiệm thu}} T{{N}}

> Skill: `gtv-client-report` (⚠ chỉ Claude Code; runtime khác điền tay template này + `_TEMPLATES/account/`). Naming: `{{CLIENT}}_bao-cao-thang-T{{N}}_v{{N}}.md` → `09-reporting/`.
> Luật gốc: tên hạng mục chép NGUYÊN VĂN SOW MAPPING (PL01 hợp đồng) — cấm tên nội bộ/tên tool trong bản gửi khách; cần chú thích kỹ thuật thì để trong ngoặc sau tên hợp đồng.

## 1. KPI vs cam kết

| Loại KPI | Hạng mục (nguyên văn HĐ) | Cam kết | Kết quả | Tỷ lệ hoàn thành thực tế | Tỷ lệ để nghiệm thu (cap 100%) | Trọng số |
|---|---|---|---|---|---|---|
| {{TOP/TRAFFIC/KPI theo HĐ}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{— nếu HĐ không quy định}} |
| **KẾT QUẢ KPI KỲ** | | | | | **{{%}}** | |

Luật chấm — không thương lượng:

1. Cap 100%/hạng mục, không bù chéo giữa các hạng mục.
2. HĐ có trọng số → Kết quả KPI kỳ = bình quân CÓ trọng số.
3. Nguồn đo + cách đo dẫn đúng Tài liệu kỹ thuật HĐ: SpySERP `{{google.com | google.com.vn — theo HĐ}}`, GA4 filter theo SOW MAPPING, quy tắc TOP lồng nhau nếu HĐ quy định.
4. Ghi rõ kỳ dữ liệu + ngày tracking ngay dưới bảng. Số lệch dashboard >2% → dừng, truy nguồn trước khi gửi.

## 2. Việc đã triển khai theo công đoạn

| # công đoạn | Hạng mục (tên SOW) | Thời hạn | Trạng thái | Kết quả (link bằng chứng) | Public/Nội bộ |
|---|---|---|---|---|---|
| {{#n}} | {{...}} | {{...}} | {{Hoàn thành \| Đang triển khai \| Chưa bắt đầu}} | {{link khách mở được}} | {{Public \| Nội bộ}} |

Trạng thái chỉ 3 giá trị (+lý do nếu trễ). "Hoàn thành" bắt buộc có link bằng chứng. Dòng Nội bộ không đưa vào bản gửi khách. Việc ngoài SOW → khu riêng, không trộn vào bảng nghiệm thu.

## 3. Kế hoạch tháng sau

| Việc (tên SOW) | Công đoạn | Owner | Mốc |
|---|---|---|---|

## 4. Risk & việc cần khách làm

| Risk / việc | Ảnh hưởng | Đề xuất | Owner | Deadline |
|---|---|---|---|---|

## 5. Khối bổ sung chế độ QUÝ (T3 / T6 / T9 — xóa nếu chế độ tháng)

1. **Lũy kế quý vs timeline PL01** — bảng runrate 3 tháng: | Hạng mục (tên SOW) | Kế hoạch | Thực tế | % lũy kế |.
2. **OKRs quý sau** — mục tiêu viết theo hạng mục SOW (không viết bằng tên nội bộ); link `01-strategy-okrs/`.
3. **Kết quả audit định kỳ + action** — action chia "GTV làm / Khách làm" kèm deadline.

Riêng T6: báo cáo quý 2 = tài liệu review giữa kỳ trực tiếp với khách (kết quả T1–T6 + kế hoạch T7–T10 + budget offpage nếu gate #25 mở).

## 6. Khối chế độ NGHIỆM THU (tháng cuối — xóa nếu không phải)

1. **Báo cáo kép**: kết quả SEO toàn dự án + kết quả AI visibility (GEO prompt set + baseline từ `08-geo-ai-visibility/`).
2. **Hồ sơ thanh toán 4 giấy tờ** theo thứ tự — thiếu 1 là khách có quyền chưa thanh toán: (1) báo cáo KPI khách xác nhận qua email → (2) BBNT ký 2 bên (`_TEMPLATES/account/`) → (3) phiếu đề nghị thanh toán → (4) hóa đơn GTGT (chỉ xuất SAU khi BBNT ký).
3. **Họp nghiệm thu** với khách; khách không phản hồi sau `{{07}}` ngày kể từ ngày gửi báo cáo = auto-accept theo điều khoản HĐ (dẫn đúng điều/khoản).
4. **Bảo hành**: duy trì tối thiểu `{{90%}}` kết quả nghiệm thu trong `{{30}}` ngày kể từ ký BBNT thanh lý.
5. **Bàn giao**: theo `11-handover-maintenance/` (template `handover-checklist.md`) — dẫn link văn bản bàn giao vào BBNT mục 3.4.

## Done-criteria

- [ ] Mọi dòng KPI + hạng mục dùng tên nguyên văn SOW MAPPING; phép thử: đặt cạnh PL01, không dòng nào lạc tên.
- [ ] Bảng KPI đúng luật cap 100% / không bù chéo / trọng số; kỳ dữ liệu + ngày tracking ghi rõ.
- [ ] Số khớp `00-client-context/kpi-commitments.md` + nguồn đo của HĐ; dòng Hoàn thành có link bằng chứng.
- [ ] Đúng chế độ: quý có đủ 3 khối bổ sung; nghiệm thu có đủ 5 mục khối 6.
- [ ] Gửi đúng hạn; update `index.md` (#30/#32) + append `log.md` op `report`.
