---
client: "{{CLIENT}}"
cong_doan: "{{34 | 35}}"
ws: 13-cro
pic: "{{CRO}}"
duyet: "{{SEO Lead Project}}"
status: draft
version: v1
---

# {{CLIENT}} — Evidence backlog CRO

> Naming `{{CLIENT}}_evidence-backlog_v{{N}}.md` → `13-cro/`. Dùng khi >5 finding; ≤5 thì để trong `conversion-path` §3. Skill `cro-audit` → `references/research-evidence.md` (format) + `patterns-condensed.md` (mức mặc định). Nhãn: **P** P0 chặn / P1 cản / P2 cải thiện · **R** R3 site-wide / R2 landing ưu tiên / R1 một trang · **E** E3 lỗi tái hiện / số có mẫu số · E2 ≥3 recording / ≥100 session / VOC lặp · E1 heuristic. Xếp: P0 (E≥2) trước theo R3→R1; còn lại theo (P, R, E); hoà → effort thấp trước. E1 chỉ ở mục "Cần kiểm".

Readiness: {{A | B}} · Cơ chế: {{…}} · Loại trang soi: {{…}} · Tracking: {{chưa có / đang gắn / PASS ngày …}}

## 1. Backlog (E ≥ 2)

| ID | Trang/template | Cơ chế | Quan sát (số + mẫu số + cửa sổ + nguồn / bước tái hiện + thiết bị) | P | R | E | Diễn giải khác | Giả thuyết | Action (component) | Metric theo dõi (≥4 tuần, "quan sát") | Item SOP · Pattern § | Owner | Deadline | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F-01 | {{…}} | {{…}} | {{…}} | P0 | R3 | E3 | {{…}} | {{…}} | {{…}} | {{…}} | {{CR-xx · §n}} | {{Dev khách}} | {{dd/mm}} | {{đề xuất / khách duyệt / đã sửa / chờ khách}} |

## 2. Cần kiểm (E1)

| ID | Trang | Nghi ngờ (pattern §) | Cách kiểm | Người kiểm | Hạn |
|---|---|---|---|---|---|

## 3. Đã đóng

| ID | Ngày | Kết quả | Số quan sát trước/sau (cùng mẫu số, cùng cửa sổ) |
|---|---|---|---|

## Done-criteria

- [ ] Mọi dòng mục 1 có đủ 3 nhãn + nguồn/ngày; không PII.
- [ ] P0 xếp đầu bất kể ranking; không có "impact score" tự đoán.
- [ ] Trạng thái brief cập nhật trước mỗi kỳ report (khối 3 "chờ khách").
