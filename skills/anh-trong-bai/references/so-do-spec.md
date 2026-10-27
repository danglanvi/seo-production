# Spec sơ đồ SVG (khối so_do)

`svg_dung.py` đọc khối `so_do` của mỗi mục `loai: "so-do"` trong `media_plan.json`. Mỗi sơ đồ ra 2 file: `<ten_file>.svg` (khung 760, desktop) và `<ten_file>-m.svg` (khung 320, điện thoại). `chen_media.py` chèn cả 2 bản. CSS trong `<head>` hiện bản điện thoại khi màn hình dưới 640 px.

## 7 kiểu

| `kieu` | Trường | Bản điện thoại |
|---|---|---|
| `luong` | `buoc[{tieu_de, mo_ta}]`, `to[chỉ số]`, `nhom[{tu, den, nhan}]`, `mot_hang` | Cột dọc, nhãn nhóm đặt trước bước đầu của nhóm |
| `quyet-dinh` | `dau`, `hoi`, `co{nhan, ket_qua, tiep}`, `khong{nhan, ket_qua, tiep}` | Cột dọc, hai nhánh cạnh nhau, nhãn cạnh mũi tên |
| `khoi` | `khoi[{tieu_de, mo_ta, to}]`, `noi[{tu, den, nhan, net: "lien"\|"dut"}]` | Cột dọc, mũi tên có nhãn giữa các khối |
| `so-sanh` | `cot[{tieu_de, dong[], to}]` | Mỗi cột thành một thẻ |
| `moc` | `moc[{thoi_gian, tieu_de, mo_ta}]` | Trục dọc |
| `cot` | `du_lieu[{nhan, gia_tri, to}]`, `don_vi`, `nguon` (bắt buộc) | Thanh ngang, giữ nguyên |
| `danh-sach` | `muc[{tieu_de, mo_ta}]`, `cot` (2 hoặc 3) | 1 cột |

`to` tô gradient cho khối cần nhấn. `luong` có từ 5 bước thì xuống hàng. `mot_hang: true` ép một hàng, dùng cho chuỗi 6–7 bước ngắn có `nhom`.

## Ví dụ (pilot 27/10/2026)

Khái niệm dễ lẫn, kiểu `khoi`:

```json
{"kieu": "khoi",
 "khoi": [{"tieu_de": "Effort", "mo_ta": "Thuộc tính Google định nghĩa; rater chấm"},
          {"tieu_de": "Content Effort", "mo_ta": "Tên cộng đồng SEO đặt cho thuộc tính Effort"},
          {"tieu_de": "contentEffort", "mo_ta": "Attribute trong leak 2024", "to": true}],
 "noi": [{"tu": 1, "den": 0, "nhan": "tên gọi", "net": "lien"},
         {"tu": 0, "den": 2, "nhan": "chưa chứng minh là cùng phép đo", "net": "dut"}]}
```

Quy trình 7 khâu chia 2 nhóm, kiểu `luong`:

```json
{"kieu": "luong", "mot_hang": true, "to": [0, 1, 2],
 "nhom": [{"tu": 0, "den": 2, "nhan": "Tạo effort"}, {"tu": 3, "den": 6, "nhan": "Kiểm hoặc giữ effort"}],
 "buoc": [{"tieu_de": "Research", "mo_ta": "Kiểm kê dữ liệu, case, test"}, {"tieu_de": "Outline", "mo_ta": "Mỗi H2 gắn một đầu vào"}]}
```

Câu hỏi rẽ hai nhánh, kiểu `quyet-dinh`:

```json
{"kieu": "quyet-dinh", "dau": "Từng khối nội dung của trang", "hoi": "Writer có SERP và LLM dựng lại được không?",
 "co": {"nhan": "Có", "ket_qua": "Commodity", "tiep": "Trang không có khối effort: thêm đầu vào trước khi viết tiếp"},
 "khong": {"nhan": "Không", "ket_qua": "Effort", "tiep": "Cần dữ liệu riêng, phép đo gốc hoặc phán đoán chuyên gia"}}
```

## Luật chữ

- `tieu_de` từ 1 đến 5 từ. `mo_ta` dưới 70 ký tự. Chữ dài làm thẻ cao và lệch nhau.
- Chữ lấy từ thân bài. Không thêm số hay khẳng định mà bài không có.
- Thuật ngữ giữ như trong bài (tiếng Anh giữ tiếng Anh).
- Một sơ đồ trả lời một ý của H2. Ý thứ hai dùng sơ đồ thứ hai hoặc bảng.

## Đo và soát

- `svg_kiem.mjs` mở từng SVG trong Chrome với font thật (Google Fonts hoặc `media.font_css`). Script báo lỗi khi chữ tràn khung chứa, chữ đè chữ, hoặc chữ dưới 12 px.
- Bản điện thoại dựng ở khung 320 để chữ 13 px còn khoảng 12 px trên máy 390 px. `kiem_render.mjs` đo lại trên theme thật và báo chữ SVG dưới 11 px.
- Mở PNG trong `media/_kiem/`. Script không thấy mũi tên đi sai hướng, nhãn đặt sai nhánh, hay màu quá nhạt.
- Màu lấy từ `media.mau` của profile. Gradient phải đủ tương phản cho chữ trắng (từ 4,5:1 với màu sáng nhất của gradient).

## Lỗi đã gặp ở pilot 27/10/2026

| Lỗi | Sửa trong script |
|---|---|
| Mũi tên chéo khi `luong` xuống hàng | Mũi tên gấp khúc: xuống, ngang, xuống |
| Nhãn "Có", "Không" đè mũi tên ở `quyet-dinh` | Desktop: nhánh gấp khúc, nhãn trên đoạn ngang. Điện thoại: nhãn cạnh mũi tên |
| Bản điện thoại mất nhãn nhóm | Nhãn nhóm đặt trước bước đầu của nhóm |
| Chữ bản điện thoại quá nhỏ ở khung 360 | Khung điện thoại 320 |
| Trùng `id` giữa bản desktop và bản điện thoại trong cùng trang | Tiền tố id riêng theo mục và bản (`img01d-`, `img01m-`) |
