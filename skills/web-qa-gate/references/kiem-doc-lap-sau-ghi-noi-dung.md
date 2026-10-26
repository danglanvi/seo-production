# Tiêu chí kiểm độc lập sau khi ghi nội dung

File này ghi các tiêu chí đo mà người kiểm dùng để kết luận một lần ghi nội dung đạt hay không. Người kiểm không phải người đã ghi. File chỉ ghi tiêu chí đo. Luồng giao việc và vòng kiểm của lane không thuộc file này.

Lỗi đã gặp: site agency mẫu 20/10/2026, một lane sửa khối chuyển đổi tự báo đạt. Lượt kiểm độc lập kết luận chưa đạt vì 4 lỗi: tràn ngang do tooltip, lưới 3+2 có ô trống, chữ 14 px do CSS toàn cục có `!important`, và 2 nút cùng trỏ một trang. Lượt sửa thêm tốn khoảng 322k token, và lỗi lưới vẫn còn khi bàn giao.

## Trước khi ghi

1. Chạy `qa_gate.py run` trên các trang sẽ ghi, với khối `interact` có `grids.selectors` của khu vực sẽ ghi. Lưu ra `<ev>/truoc`.
2. Ghi số thẻ dự kiến của từng lưới sau khi ghi, theo bản đã duyệt.

## Sau khi ghi

Chạy lại cùng config, lưu ra `<ev>/sau`, rồi so:

```bash
python3 -E skills/web-qa-gate/scripts/truoc_production.py diff <ev>/truoc <ev>/sau --labels truoc,sau
```

| # | Tiêu chí | Đo bằng | Đạt khi |
|---|---|---|---|
| 1 | Tràn ngang | Hạng mục 1, `--cache both`, đủ bề rộng của lần ghi | 0 lượt tràn. Phần tử ẩn bằng `visibility:hidden` (tooltip) vẫn tính vào vùng cuộn. |
| 2 | Số thẻ trước và sau | Dòng "số thẻ trong lưới đổi" của `diff` | Khớp số thẻ dự kiến ở bước "Trước khi ghi". |
| 3 | Lưới không ô trống | Hạng mục 14a | Không có ô trống, không có hàng giữa thiếu ô. Hàng cuối thiếu ô chỉ được phép khi bản duyệt có. |
| 4 | Cỡ chữ tính | `skills/wp-ui-fix/scripts/type_probe.mjs` rồi `type_check.py` theo thang chữ của site | Chữ thân không nhỏ hơn thang. CSS toàn cục có `!important` hay đè cỡ chữ của khối mới. |
| 5 | Số trong heading | Hạng mục 14b, khi heading có số | Số trong heading khớp số thẻ. |
| 6 | CTA và nút | Hạng mục 14c, 13d | Không có 2 CTA cùng href ngoài chủ ý. Nút mới dùng đúng màu kit. |
| 7 | Chữ dễ đọc | Hạng mục 12 | Đạt bảng ngưỡng của mục 12. |

## Kết luận

- Kết luận "đạt" chỉ khi mọi tiêu chí đạt, hoặc tiêu chí lệch có trong bản đã duyệt.
- Chạy script tất định trước. Người kiểm đọc kết quả, rồi xem ảnh của từng dòng WARN.
- Báo kết luận kèm đường dẫn report của lượt "sau" và output của `diff`.
