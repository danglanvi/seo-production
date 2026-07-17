---
status: stub
file: kpi-commitments
client: "{{CLIENT}}"
hop_dong: "{{SO_HD}}"
updated: "{{NGAY_CAP_NHAT}}"
---

# {{CLIENT}} — KPI cam kết theo hợp đồng

> Trích từ HĐ trong `02-raw/contracts-proposals/` theo schema `_TEMPLATES/hop-dong-cam-ket.md` — bản chưng cất đầy đủ nằm ở `hop-dong-cam-ket.md` cùng folder. Đây là nguồn duy nhất WS 09 Reporting được phép báo cáo. Điền xong đổi `status: stable`.

## 1. KPI cam kết theo HĐ

| # | KPI | Giá trị cam kết | Trọng số | Mốc thời gian | Điều kiện kèm |
|---|---|---|---|---|---|
| 1 | {{KPI_1}} | {{GIA_TRI_1}} | {{TRONG_SO_1}} | {{MOC_1}} | {{DIEU_KIEN_1}} |
| 2 | {{KPI_2}} | {{GIA_TRI_2}} | {{TRONG_SO_2}} | {{MOC_2}} | {{DIEU_KIEN_2}} |

- Phạm vi / loại trừ: {{PHAM_VI_LOAI_TRU}}
- Điều khoản khi KPI không đạt: {{DIEU_KHOAN_KPI_KHONG_DAT}}
- Mô hình: {{THUC_THI_HAY_ADVISORY}} — trách nhiệm KPI phân chia: {{PHAN_CHIA_TRACH_NHIEM}}

## 2. Công thức đo

| KPI | Công thức | Nguồn số liệu | Kỳ đo | Baseline |
|---|---|---|---|---|
| {{KPI_1}} | {{CONG_THUC_1}} | {{NGUON_SO_LIEU_1}} | {{KY_DO_1}} | {{BASELINE_1}} |
| {{KPI_2}} | {{CONG_THUC_2}} | {{NGUON_SO_LIEU_2}} | {{KY_DO_2}} | {{BASELINE_2}} |

## 3. Mốc nghiệm thu

| Đợt | Mốc thời gian | Điều kiện nghiệm thu | Thanh toán gắn kèm |
|---|---|---|---|
| 1 | {{MOC_NGHIEM_THU_1}} | {{DIEU_KIEN_NGHIEM_THU_1}} | {{THANH_TOAN_1}} |
| 2 | {{MOC_NGHIEM_THU_2}} | {{DIEU_KIEN_NGHIEM_THU_2}} | {{THANH_TOAN_2}} |

- Quy trình nghiệm thu: theo `_TEMPLATES/account/` (BBNT, auto-accept 7 ngày, bảo hành 30 ngày).

## Done-criteria

- [ ] Sạch placeholder; frontmatter `status: stable`.
- [ ] Mỗi KPI có công thức đo + nguồn số liệu + baseline.
- [ ] Mốc nghiệm thu khớp điều khoản thanh toán trong HĐ.
