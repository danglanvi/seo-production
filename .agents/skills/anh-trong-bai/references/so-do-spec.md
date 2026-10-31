# Spec sơ đồ SVG (khối so_do)

`svg_dung.py` đọc khối `so_do` của mỗi mục `loai: "so-do"` trong `media_plan.json`. Mỗi sơ đồ ra 2 file: `<ten_file>.svg` (khung 760, desktop) và `<ten_file>-m.svg` (khung 320, điện thoại). `chen_media.py` chèn cả 2 bản. CSS trong `<head>` hiện bản điện thoại khi màn hình dưới 640 px.

## 10 kiểu

| `kieu` | Trường | Bản điện thoại |
|---|---|---|
| `luong` | `buoc[{tieu_de, mo_ta}]`, `to[chỉ số]`, `nhom[{tu, den, nhan}]`, `mot_hang` | Cột dọc, nhãn nhóm đặt trước bước đầu của nhóm |
| `quyet-dinh` | `dau`, `hoi`, `co{nhan, ket_qua, tiep}`, `khong{nhan, ket_qua, tiep}` | Cột dọc, hai nhánh cạnh nhau, nhãn cạnh mũi tên |
| `khoi` | `khoi[{tieu_de, mo_ta, to}]`, `noi[{tu, den, nhan, net: "lien"\|"dut"}]` | Cột dọc, mũi tên có nhãn giữa các khối |
| `so-sanh` | `cot[{tieu_de, dong[], to}]` | Mỗi cột thành một thẻ |
| `moc` | `moc[{thoi_gian, tieu_de, mo_ta}]` | Trục dọc |
| `cot` | `du_lieu[{nhan, gia_tri, to}]`, `don_vi`, `nguon` (bắt buộc) | Thanh ngang, giữ nguyên |
| `danh-sach` | `muc[{tieu_de, mo_ta}]`, `cot` (2 hoặc 3) | 1 cột |
| `lan` | `lan[tên]`, `buoc[{tieu_de, mo_ta, lan, cot, hoi, to}]`, `noi[{tu, den, nhan, loai}]`, `vong[{tu, den, nhan, loai}]` | Cột dọc theo thứ tự bước, mỗi thẻ ghi tên làn; cạnh nhảy cóc đi rãnh phải, vòng lùi đi rãnh trái |
| `vong-lap` | `buoc[{tieu_de, mo_ta, to}]`, `vong[{tu, den, nhan, loai}]` | Như `lan`, không có tên làn |
| `so-lieu` | `so[{gia_tri, nhan, truoc, don_vi, to}]`, `cot`, `nguon` (bắt buộc) | 2 cột khi số ngắn, không thì 1 cột |

`to` tô gradient cho khối cần nhấn. `luong` có từ 5 bước thì xuống hàng. `mot_hang: true` ép một hàng, dùng cho chuỗi 6–7 bước ngắn có `nhom`.

### Làn và vòng lặp

- Dùng `lan` khi quy trình có từ 2 vai trở lên: người, AI, công cụ. Dùng `vong-lap` khi quy trình một hàng có bước quay lại.
- `cot` mặc định là chỉ số bước. Đặt `cot` trùng nhau khi 2 bước ở 2 làn xảy ra cùng lúc, ví dụ AI chỉnh và Sheet cập nhật.
- `hoi: true` vẽ hình thoi cho câu hỏi rẽ nhánh. Nhãn nhánh đặt ở `nhan` của cạnh đi ra ("Có", "Không").
- `noi` thiếu thì script nối bước liền nhau. Khi có nhánh, khai đủ mọi cạnh tiến trong `noi`.
- `loai`: `tien` nét liền màu `phu`; `sua` nét đứt màu `canh_bao` cho vòng sửa; `hoc` nét đứt màu `chinh` cho vòng học. Caption nói nghĩa của màu.
- Script đi mũi tên theo trục và thử lần lượt: thẳng, gấp một lần, gấp hai lần qua khe giữa cột, kênh trên hoặc kênh dưới. Đường không được cắt hộp hay tên làn. Vòng ngắn nằm kênh gần hộp, vòng dài nằm kênh xa.
- Tối đa 6 cột ở bản desktop. Nhiều hơn thì tách sơ đồ hoặc dồn bước cùng lúc vào một cột.

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

Quy trình 3 vai có vòng sửa, kiểu `lan` (bài tài liệu nội bộ, 31/10/2026):

```json
{"kieu": "lan", "lan": ["Bạn (SEO)", "AI · Claude Code", "Google Sheet"],
 "buoc": [{"tieu_de": "1. Giao việc", "lan": 0}, {"tieu_de": "2. Lập outline", "lan": 1}, {"tieu_de": "3. Ghi lên Sheet", "lan": 2},
          {"tieu_de": "4. Review", "lan": 0}, {"tieu_de": "Còn Chặn?", "lan": 0, "hoi": true},
          {"tieu_de": "5. AI chỉnh", "lan": 1, "cot": 4}, {"tieu_de": "Sheet cập nhật", "lan": 2, "cot": 4}, {"tieu_de": "6. Chốt", "lan": 0, "cot": 5}],
 "noi": [{"tu": 0, "den": 1}, {"tu": 1, "den": 2}, {"tu": 2, "den": 3}, {"tu": 3, "den": 4},
         {"tu": 4, "den": 5, "nhan": "Có"}, {"tu": 5, "den": 6}, {"tu": 4, "den": 7, "nhan": "Không"}],
 "vong": [{"tu": 6, "den": 3, "nhan": "Vòng sửa", "loai": "sua"}]}
```

Ô số liệu trước → sau, kiểu `so-lieu`:

```json
{"kieu": "so-lieu", "nguon": "Outline mẫu, đo 31/10/2026",
 "so": [{"truoc": "29.934", "gia_tri": "15.997", "nhan": "Ký tự cột AM của cả outline", "to": true},
        {"gia_tri": "47", "don_vi": "%", "nhan": "Giảm ký tự"}]}
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

## Lỗi đã gặp ngày 31/10/2026

| Lỗi | Sửa trong script |
|---|---|
| Sơ đồ làn vẽ tay bằng toạ độ có mũi tên chéo qua hộp | Kiểu `lan`: bộ định tuyến theo trục, kiểm đường không cắt hộp |
| Mũi tên dọc đi qua tên làn | Tên làn là vật cản khi định tuyến |
| Nhãn "Không" trên mũi tên ngắn đè chữ của hộp | Mũi tên ngắn: nhãn đặt ở dải trên mép hộp nguồn |
| Hai vòng vào cùng một hộp: đầu mũi tên chồng nhau, vòng dài cắt vòng ngắn | Điểm ra, điểm vào lệch 18 px theo hướng vòng; vòng ngắn đi kênh gần |
| Nhãn nằm trên nét mũi tên khó đọc | Mọi nhãn mũi tên có viền màu nền (`paint-order="stroke"`) |

## Lỗi Vincent chỉ ra tối 31/10/2026 ("mũi tên chưa rõ ràng và đẹp")

| Lỗi | Sửa trong script |
|---|---|
| Đầu mũi tên phóng theo độ dày nét, to khoảng 15 px, trông thô | Đầu mũi tên cỡ cố định 10 px (`markerUnits="userSpaceOnUse"`), dạng nhọn có khía |
| Góc gấp vuông cứng | Góc bo 8 px, nét 2 px, nét đứt 6/4 |
| Vòng giữa 2 hộp cùng cột có hộp khác ở giữa đi xuyên 2 hộp | Đường ra cạnh bên, đi dọc trong khe cạnh cột, vào cạnh bên; ra và vào ở nửa hộp hướng về nhau |
| Vòng vào hộp đầu làn đè tên làn | Tên làn dời sang khoảng trống đầu tiên không có nét, cách nét 14 px |
| Nhãn "Không" của mũi tên ngắn giữa 2 cột trôi lên đỉnh làn | Khe giữa 2 cột liền nhau giãn đủ chỗ cho nhãn của mũi tên ngang cùng làn |
| Nhãn có viền trắng lộ trên nền làn | Viền chữ lấy màu nền tại chỗ (`nen_nhat` trong dải làn) |
| Nhãn cạnh nét dọc đè chữ trong hộp | Nhãn chọn bên trái hoặc phải của nét, bên không đè hộp |
| Bản điện thoại: 2 vòng cùng rãnh trái cắt nhau | Mỗi cạnh nhảy cóc chọn rãnh trái hoặc phải để các vòng lồng nhau, không cắt chéo |
| Bản điện thoại: nhãn mũi tên giữa đè nhãn rãnh phải cùng nguồn | Nhãn mũi tên giữa sang trái khi cùng nguồn có nhãn rãnh phải |

Luật soạn spec rút ra: sơ đồ `lan` 6 cột ở khung 760 làm hộp hẹp, chữ xuống 4–5 dòng. Giữ tối đa 5 cột: thay hình thoi bằng 2 cạnh có nhãn đi ra từ bước review ("Còn Chặn", "Hết Chặn"). Thứ tự bước trong `buoc` là thứ tự đọc của bản điện thoại: đặt bước kết thúc ("Đạt") ngay sau bước dẫn tới nó, nhánh phụ đặt sau.

