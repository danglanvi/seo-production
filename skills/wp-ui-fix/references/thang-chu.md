# Thang chữ cho site đang chạy

Mục đích: đo và sửa cỡ chữ, tỉ lệ heading, độ dài dòng theo template, có thang mặc định kèm nguồn. Đọc ở Bước 4 của `SKILL.md`, khi việc chạm cỡ chữ, line-height, heading hoặc độ rộng đoạn. Gốc đường dẫn là root repo. `$UIF` là `skills/wp-ui-fix/scripts`.

Phạm vi: file này đo cỡ chữ và tỉ lệ heading. Chữ dính dòng, đoạn dài căn giữa và chữ tràn sau khi thêm copy thuộc hạng mục 12 "Chữ dễ đọc" của `web-qa-gate`.

## 1. Thang mặc định của master

Số dưới khớp `DEFAULTS` và `SOURCES` trong `type_check.py`. In bản đang chạy bằng `python3 "$UIF/type_check.py" --print-defaults`.

| Mục | Ngưỡng | Nguồn |
|---|---|---|
| Chữ thân | desktop ≥ 16 px, mobile ≥ 15 px | Đợt ux-type-audit site mẫu gtvseo 19–20/10/2026. Không phải luật của Google |
| Tỉ lệ chữ đọc dưới ngưỡng | ≤ 5% số ký tự chữ thân | Pilot site mẫu gtvseo: sau sửa còn 1,6–5,6%, phần còn lại là nhãn đã chốt. Chưa hiệu chuẩn thêm |
| Độ dài dòng | ≤ 80 ký tự | WCAG 2.2 tiêu chí 1.4.8 (mức AAA) |
| Line-height chữ thân | ≥ 1,5 | WCAG 2.2 tiêu chí 1.4.8 (mức AAA). `type_check.py` không chấm. `web-qa-gate` hạng mục 12 đo |
| H2 và H3 so với chữ thân | lớn hơn ít nhất 2 px, H2 lớn hơn H3 | ux-type-audit site mẫu gtvseo |
| H1 giữa các template | lệch ≤ 4 px | Ước lượng, chưa có nguồn. Site mẫu: 56 so với 32 px là lỗi, 40 so với 36 px được chấp nhận |
| Số cỡ của một cấp heading | ≤ 2 cỡ H2 và ≤ 2 cỡ H3 trên một trang | Ước lượng, chưa có nguồn |
| Khoảng đáy header tới H1 | desktop ≥ 32 px, mobile ≥ 24 px | Ước lượng, chưa có nguồn. Site mẫu: 64 và 56 px đạt |

Script loại khỏi phép tính: vùng header, footer, nav, phần tử fixed, icon font, khối dưới 25 ký tự (nhãn, nút).

## 2. Số riêng của site: `ui-rules.md`

1. Đặt file ở `00-client-context/ui-rules.md` của instance.
2. Ghi số riêng trong khối ```json đầu tiên có khoá `"type_rules"`. `type_check.py --rules` đọc khối này. Script từ chối khoá lạ.
3. Chỉ ghi số người duyệt đã chốt trên production. Mỗi số có ngày duyệt và nguồn.
4. Nếu chưa có file: dùng thang mặc định. Hỏi người duyệt danh sách component đặc biệt trước khi áp.

Khoá dùng nhiều:

| Khoá | Dạng | Ví dụ |
|---|---|---|
| `components` | `[{name, sel_regex, min_px}]`. `min_px` là số, `{desktop, mobile}`, hoặc `0` để loại hẳn | `{"name": "công cụ trong bài", "sel_regex": "tool-", "min_px": 0}` |
| `h_scale` | `{"h2": {"desktop": [..], "mobile": [..]}, "h3": {...}, "tolerance_px": 1}` | `{"h2": {"desktop": [30, 32], "mobile": [24, 26]}}` |
| `exclude` | `{regions, sel_regex, text_regex}` | thêm regex class quảng cáo |
| `severity` | ghi đè mức `fail` hoặc `warn` của từng mã lỗi | `{"long_line": "fail"}` |

`sel_regex` khớp với đường dẫn tối đa 4 cấp cha mà `type_probe.mjs` ghi, cộng class của khối. Nếu component lồng sâu hơn 4 cấp, khai thêm class con. Class kiểu BEM (`.tool__label`) đã chứa tên khối cha.

## 3. Liệt kê component đặc biệt trước khi áp

Trước khi viết CSS thang chữ, lập danh sách component có cỡ riêng:

- mục lục bài, mục lục con;
- công cụ tương tác trong bài;
- hero số liệu, thẻ thống kê;
- CTA, nút mobile;
- FAQ, accordion;
- nhãn, chức danh, chú thích ảnh.

Cách tìm:

1. Chạy `type_probe.mjs` trên một trang mẫu của mỗi template.
2. Chạy `type_check.py --list`. Lệnh in khối dưới ngưỡng kèm selector.
3. Quét class của component trên toàn site, ví dụ bằng sitemap và DOM. Ca thật site mẫu gtvseo: chỉ 8 URL có công cụ trong bài.
4. Ghi mỗi component vào `ui-rules.md`: cỡ riêng, hoặc `min_px: 0` để loại. Trong CSS, loại bằng `:not(:where(...) *)` (`truy-nguon-css.md` mục 4).

Ca thật (site mẫu gtvseo, 21/10/2026): luật chữ thân đè 8 công cụ trong bài (nhãn 12 → 18 px). Mục lục con to hơn mục cha ở 181/186 bài. Hai lỗi cần 2 vòng sửa.

## 4. Đo

```bash
node "$UIF/type_probe.mjs" home=https://example.vn/ dv=https://example.vn/dich-vu/ blog=https://example.vn/bai-mau/ \
  --widths 390,1366 --out <lane>/type-truoc
python3 "$UIF/type_check.py" <lane>/type-truoc/type_probe.json --rules 00-client-context/ui-rules.md --list --out <lane>/type-truoc/check.json
```

- Tên trước dấu `=` gom H1 giữa các template. Dùng cùng tên cho lượt đo sau.
- Ảnh hero giữ header. Ảnh từng màn ẩn phần tử fixed, giữ sticky. Ca thật: `measure.mjs` cũ ẩn cả sticky, nên ảnh hero mobile mất và Jev báo `uneven_gap` 0,87 cho lỗi không có thật.
- Mã thoát của `type_check.py`: 0 không có lỗi mức fail, 1 có lỗi mức fail, 2 file hoặc luật sai.
- Staging qua tunnel: đặt `--resolve` và `WEB_QA_AUTH` như `web-qa-gate` Bước 1 mục 7.

## 5. Pilot 2 trang

1. Áp thang trên staging cho 2 trang: trang chủ và 1 trang tiền (trang dịch vụ chính).
2. Đo lại bằng mục 4 ở 390, 1366, 1440, 1920 px. `type_check.py` không còn lỗi mức fail.
3. Chụp trước và sau bằng `shot_el.mjs`, dựng trang so sánh bằng `so_sanh.py` (`trinh-anh.md`). Đưa PSI trước và sau của `wp-pagespeed` vào `--so-lieu`.
4. Mở rộng toàn site chỉ khi người duyệt chọn phương án trên trang so sánh.

Ca thật (site mẫu gtvseo, 19/10/2026): trang chủ 1366 px có chữ thân 14 px, 99,5% chữ đọc dưới ngưỡng, H1 56 px. Người duyệt nhắn: "có thể là headline ngay home page bự quá" và "size chữ nói chung nhiều chỗ tôi thấy hơi nhỏ trên desktop".

## 6. Site mẫu thẩm mỹ

Nếu `ui-rules.md` khai một site mẫu người duyệt đã khen, chụp cùng khối trên site mẫu và site đang sửa, kèm PSI, trước khi đề xuất cỡ chữ hay font. Đặt thẩm mỹ người đọc ngang với số đo.

## 7. Quyết font bằng A/B có tiêu chí đặt trước

1. Ghi tiêu chí trước khi đo. Ví dụ site mẫu gtvseo (20/10/2026): chọn cách tải font mới nếu CLS desktop của bài nặng không cao hơn phương án B và LCP không tăng quá 0,1 s.
2. Đo bằng `wp-pagespeed` (`psi_ab.py`, `cls_trace.mjs`), xen kẽ lượt.
3. Chọn theo tiêu chí đã ghi. Không đổi tiêu chí sau khi thấy số.

## 8. Jev `ui-type-align`

- Rubric: `tools/ai-assist/tasks/ui-type-align.json`.
- Ngưỡng hiệu chuẩn 19/10/2026 (26 ảnh gán tay, site mẫu gtvseo): `heading_imbalance`, `uneven_gap`, `long_lines` từ 0,6. `text_too_small` từ 0,5 chỉ để Claude xem ảnh. Không dùng `cards_misaligned`: đo khung lệch bằng DOM.
- Gửi `state` dạng list `[mô tả, {"image_path": ...}]`. Nếu đặt `image_path` cạnh `description` trong cùng một dict, Jev không nhận ảnh.
- Jev không bắt mục lục đảo cấp. Phép đo DOM là bằng chứng chính cho thang chữ.
