# Tái hiện lỗi và trình ảnh trước/sau

Mục đích: tái hiện lỗi đúng như người báo thấy, rồi trình bản sửa bằng ảnh để người duyệt quyết. Đọc ở Bước 1 và Bước 6 của `SKILL.md`. Gốc đường dẫn là root repo. `$UIF` là `skills/wp-ui-fix/scripts`.

## 1. Tái hiện

1. Dùng đúng bề rộng, thiết bị và engine của người báo.
2. Nếu lỗi chạm trên iPhone, chạy cả WebKit (Playwright) và Chromium ở 320–767 px. Nếu máy không có WebKit, ghi giới hạn "chưa tái hiện trên WebKit".
3. Lưu ảnh người báo gửi vào `<lane>/bao-loi/`. Đọc manh mối trong ảnh, ví dụ thẻ clone của slider hoặc vị trí lệch.
4. Kết luận bằng phần tử nhìn thấy trong viewport: khung `getBoundingClientRect` giao với viewport, `elementFromPoint` ở tâm và 4 mép nút. Không kết luận bằng class nội bộ như `slick-current` hay `aria-current`.
5. Lỗi tương tác (menu mobile, slider, trạng thái hover, focus, visited, màu nút kit): chạy hạng mục "Tương tác và trạng thái" của `web-qa-gate` (`interact_probe.mjs`). Lỗi lưới, số trong heading, CTA trùng link: hạng mục "Toàn vẹn bố cục". Không viết probe tương tác mới trong skill này.
6. Chạy phép đo trên bản chưa sửa trước. Phép đo phải ra FAIL ở đó (đối chứng dương). Nếu bản chưa sửa vẫn ra PASS, phép đo sai, không dùng để báo đạt.

Ca thật (site mẫu gtvseo, 22/10/2026): người duyệt báo nút slider mobile bấm không được. Vòng 1 đo bằng `slick-current` nên ra dương tính giả. Lane chạy 268 phút, 823k token.

## 2. Chụp trước và sau

Production là lượt `truoc`. Staging (hoặc CSS thử) là lượt `sau`. Hai lượt dùng cùng tên trang, cùng selector, cùng `--dpr`.

```bash
# Lượt trước, trên production
node "$UIF/shot_el.mjs" home=https://example.vn/ dv=https://example.vn/dich-vu/ --sel '.hero' --widths 390,1366 --out <lane>/shots --label truoc
# Lượt sau, trên staging. STG_HOST lấy từ stg_load (wp-staging-deploy Bước 2), không in ra.
# Basic Auth (WEB_QA_AUTH) và resolve qua tunnel đặt như web-qa-gate Bước 1 mục 7.
node "$UIF/shot_el.mjs" home="https://$STG_HOST/" dv="https://$STG_HOST/dich-vu/" \
  --resolve "$STG_HOST=<ip của tunnel>" --sel '.hero' --widths 390,1366 --out <lane>/shots --label sau
# Hoặc lượt sau bằng CSS thử, chưa deploy
node "$UIF/shot_el.mjs" home=https://example.vn/ --sel '.hero' --css <lane>/thu.css --out <lane>/shots --label sau
```

- Có `--sel`: script cuộn tới phần tử, ẩn phần tử fixed bằng `opacity:0`, giữ sticky, chụp khung phần tử cộng lề `--pad`.
- Không `--sel`: script chụp màn đầu như người dùng thấy, giữ header và nút fixed. Dùng cho lỗi hero, menu, header.
- Bề rộng: 390 và 1366 px, cộng các mốc `@media` của theme mà `match.mjs` in ra. Thay đổi thang chữ chụp thêm 1440 và 1920 px.
- `shots_<nhãn>.json` chỉ ghi đường dẫn trang, không ghi host. Output lượt staging vẫn chạy qua `stg_mask` khi in ra chat.
- Mã thoát: 0 xong, 1 có URL lỗi (HTTP từ 400) hoặc selector không khớp, 2 sai cú pháp.

## 3. Trang so sánh

```bash
python3 "$UIF/so_sanh.py" --dir <lane>/shots --title "Thang chữ pilot: trang chủ và dịch vụ" \
  --so-lieu <lane>/psi.json --cau-hoi <lane>/cau-hoi.json
```

- Trang có: cặp ảnh, khung đỏ quanh vùng đổi, bảng số liệu, lựa chọn có đánh dấu đề xuất, ô ghi chú, nút "Chép câu trả lời".
- `psi.json`: `[{"muc": "PSI mobile trang chủ", "truoc": 90, "sau": 93}]`. Lấy số từ `wp-pagespeed`, không chép từ trí nhớ.
- `cau-hoi.json`: `{"cau_hoi": [{"id": "thang", "hoi": "...", "boi_canh": "...", "lua_chon": [{"id": "a", "nhan": "...", "de_xuat": true}, {"id": "b", "nhan": "..."}]}]}`. Mỗi câu có tối đa 1 lựa chọn đề xuất.
- Script đặt tên `so-sanh_v<N>.html`, N tự tăng. Mỗi đợt câu hỏi mới là một bản mới.
- Cặp "không đổi" in "CẢNH BÁO". Nguyên nhân thường gặp: bản sửa chưa lên, cache cũ, chụp nhầm host. Nếu đó là trang đối chứng, ghi rõ trong bối cảnh câu hỏi.
- Mở trang bằng trình duyệt. Trên macOS: `open -a "Google Chrome" <lane>/shots/so-sanh_v1.html`.
- Người duyệt chọn, bấm "Chép câu trả lời", dán lại vào chat. Câu để trống được tính theo đề xuất, trừ việc xoá.

## 4. Luật trình

1. Quyết định thị giác (font, thang chữ, menu, header, màu) chỉ trình bằng ảnh. Không trình bằng chữ. Ca thật: người duyệt chưa hiểu đề xuất font viết bằng chữ và xin chụp hình (site mẫu gtvseo, 20/10/2026).
2. Mỗi thay đổi nhìn thấy trên toàn site có một dòng trong tin chat, kèm ảnh.
3. Không đổi UX người duyệt quen dùng khi chưa hỏi. Ca thật: menu bị gỡ phần mô tả quanh mục mà chưa hỏi, người duyệt hỏi lại lý do (site mẫu gtvseo, 19/10/2026).
4. Bản ngôn ngữ phụ dùng chung template, CSS, menu và cỡ chữ với bản chính, chỉ khác chữ. Chụp cặp ngôn ngữ cùng tên trang với hai nhãn, ví dụ `--label vi` và `--label en`, rồi chạy `so_sanh.py --truoc vi --sau en`. Khung đỏ chỉ được nằm ở vùng chữ. Ca thật: người duyệt nhận xét nhiều chỗ chỉnh riêng ở bản EN làm giao diện xấu đi (site mẫu gtvseo, 20/10/2026).
