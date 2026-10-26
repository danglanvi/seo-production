---
name: wp-ui-fix
description: "Sửa lỗi giao diện site WordPress đang chạy theo báo lỗi hoặc audit: cỡ chữ và thang chữ, menu, slider, nút, tràn, tương phản, khung ảnh, hero. Dùng trước khi đổi CSS, template hoặc mu-plugin của site có quyền server. Dựng theme mới thì dùng wp-theme-build."
metadata:
  version: "1.0"
---

# wp-ui-fix — quy trình sửa giao diện site đang chạy

Một bản vá CSS trên site đang chạy dễ thua specificity, sót bản sao ở critical CSS, hoặc lan sang trang khác. Skill này giữ cách sửa: truy nguồn CSS trước khi viết rule, sửa có scope, pilot 2 trang, trình ảnh trước/sau, trả về bằng quarantine. Phép đo bằng code là bằng chứng chính. Ảnh dùng để người duyệt quyết.

Gốc đường dẫn là root repo. Script nằm ở `skills/wp-ui-fix/scripts/`, gọi tắt `$UIF` (`UIF=skills/wp-ui-fix/scripts`). `match.mjs`, `type_probe.mjs`, `shot_el.mjs` dùng `skills/web-qa-gate/scripts/_cdp.mjs`, nên skill `web-qa-gate` phải nằm cạnh.

## Khi nào dùng

- Người duyệt báo lỗi giao diện trên site đang chạy: chữ nhỏ, heading lệch, menu, slider, nút, tràn ngang, tương phản, khung ảnh, hero.
- Audit giao diện (Jev `ui-visual`, `web-qa-gate`) trả lỗi cần sửa CSS, template hoặc mu-plugin.
- Đổi thang chữ của một hay nhiều template.

Không dùng khi:

| Việc | Skill |
|---|---|
| Dựng theme mới | `wp-theme-build` |
| Tốc độ, Core Web Vitals | `wp-pagespeed` |
| Kiểm sau khi ghi (tràn, axe, form, tương tác, bố cục) | `web-qa-gate` |
| Sửa chữ, meta, title, link, trường ACF/Elementor | `wp-content-review-apply` |
| Làm mới staging, deploy theme và mu-plugins | `wp-staging-deploy` |

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| URL lỗi, bề rộng, thiết bị hoặc engine, ảnh người báo | Người báo hoặc file audit | Hỏi. Không đoán bề rộng |
| Quyền server: SSH alias, web root, lệnh WP-CLI, binary PHP | `00-client-context/wp-server.md` | Chỉ chẩn đoán từ ngoài, giao bảng nguồn và spec cho dev. Không ghi |
| Staging và tunnel | `wp-staging-deploy` Bước 2 | Không ghi production. Hỏi người giao việc |
| Luật giao diện riêng của site: component đặc biệt, thang đã duyệt, site mẫu | `00-client-context/ui-rules.md` | Dùng thang mặc định (`references/thang-chu.md` mục 1). Hỏi danh sách component đặc biệt trước khi áp thang chữ |
| Người duyệt | Người giao việc, `index.md` bảng A | Hỏi |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Code | Đo rule thắng, bản sao CSS, cỡ chữ, khung ảnh, vùng đổi | Dùng. Đây là bằng chứng chính |
| Jev | `ui-visual` và `ui-type-align` xếp ảnh cho Claude đọc | Dùng. Ngưỡng `ui-visual` ở `tools/ai-assist/README.md` mục 4, ngưỡng `ui-type-align` ở `references/thang-chu.md` mục 8. Jev không bắt mục lục đảo cấp, nên không thay phép đo DOM |
| EmbeddingGemma 2 | Đo độ giống | Không dùng. Skill sửa CSS, không có bài toán độ giống. Các lane thang chữ 21/10/2026 ghi cùng kết luận |
| GLM Flash | Trích câu | Không dùng. Skill không có việc trích câu |
| Claude | Truy nguồn, viết CSS, đọc ảnh Jev gắn cờ, quyết định giữ hay trả về | Dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,pillow,ssh,wp-cli,playwright?,jev?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

`playwright` chỉ cần khi tái hiện lỗi chạm trên WebKit (cài thêm `npx playwright install webkit`). Thiếu thì ghi giới hạn "chưa tái hiện trên WebKit".

1. **Tái hiện.** Đọc `references/trinh-anh.md` mục 1.
   - Dùng đúng bề rộng và engine của người báo. Lỗi chạm trên iPhone: chạy WebKit và Chromium ở 320–767 px.
   - Kết luận bằng phần tử nhìn thấy trong viewport, không bằng class nội bộ như `slick-current`.
   - Lỗi tương tác và bố cục: chạy `web-qa-gate` (`interact_probe.mjs`). Không viết probe mới.
   - Phép đo phải ra FAIL trên bản chưa sửa trước khi dùng để báo đạt.
2. **Truy nguồn CSS.** Đọc `references/truy-nguon-css.md` mục 1–3.
   - Rule thắng cho từng thuộc tính:

     ```bash
     node "$UIF/match.mjs" <url> '<selector>' --widths 390,1366 --props font-size,line-height --out <lane>/match.json
     ```

   - Mọi bản sao trong 7 nguồn (theme, critical CSS, Customizer, mu-plugins, Elementor, plugin, file gộp cache):

     ```bash
     bash "$UIF/css_sources.sh" --wp <web root> --wp-cmd '<lệnh wp-cli theo wp-server.md>' --tsv '<chuỗi CSS>'
     ```

   - Ghi bảng `<lane>/nguon-css.md`: nguồn, file và dòng, selector, giá trị, cách sửa. Rule có nhiều bản sao thì sửa mọi bản sao.
3. **Sửa có scope.** Đọc `references/truy-nguon-css.md` mục 4–7.
   - Mọi rule có scope theo template, section hoặc body class. Không viết rule toàn cục trên `h1`–`h6`, `p`, `nav`, `button`.
   - Selector đổi font hoặc cỡ chữ loại sẵn icon (`i`, `[class*=fa-]`, `[class*=icon]`, `svg`) và component đặc biệt trong `ui-rules.md`.
   - Mỗi việc một mu-plugin riêng, tên theo việc, có `<style id>` và marker version.
   - Thay chuỗi trong theme bằng `theme_patch.py` (chạy thử, `--apply`, chạy lại phải ra `already`).
   - Thử rule mới có thắng không trước khi deploy: `node "$UIF/match.mjs" <url> '<selector>' --css <lane>/thu.css`. Mã thoát 3 là CSS thử thua.
   - Đổi `div onclick` sang `a` hoặc `button`: reset style nút của kit builder, rồi chạy hạng mục tương tác của `web-qa-gate`.
   - Vòng sửa chỉ chạy trên trang lỗi. Lượt cuối chạy đủ mọi trang của template.
4. **Thang chữ** (khi việc chạm cỡ chữ, heading, độ rộng đoạn). Đọc `references/thang-chu.md`.

   ```bash
   node "$UIF/type_probe.mjs" home=<url trang chủ> dv=<url trang dịch vụ> --widths 390,1366 --out <lane>/type-truoc
   python3 "$UIF/type_check.py" <lane>/type-truoc/type_probe.json --rules 00-client-context/ui-rules.md --list
   ```

   Liệt kê component đặc biệt và đặt cỡ riêng cho từng loại trước khi áp. `type_check.py` không còn lỗi mức fail thì mới trình.
5. **Pilot 2 trang.** Thay đổi toàn site (thang chữ, menu, header, footer, màu) áp trước trên staging cho trang chủ và 1 trang tiền. Mở rộng toàn site chỉ khi người duyệt chọn trên trang so sánh.
6. **Trình ảnh.** Đọc `references/trinh-anh.md` mục 2–4.

   ```bash
   node "$UIF/shot_el.mjs" home=<url production> --sel '<selector>' --widths 390,1366 --out <lane>/shots --label truoc
   node "$UIF/shot_el.mjs" home=<url staging> --resolve '<host>=<ip>' --sel '<selector>' --widths 390,1366 --out <lane>/shots --label sau
   python3 "$UIF/so_sanh.py" --dir <lane>/shots --title '<việc>' --so-lieu <lane>/psi.json --cau-hoi <lane>/cau-hoi.json
   ```

   Mở trang so sánh bằng trình duyệt. Quyết định thị giác (font, thang chữ, menu) chỉ trình bằng ảnh.
7. **Ghi.** Chạy `web-qa-gate` (gồm hạng mục 13 tương tác và 14 bố cục) sau mỗi bản sửa trên staging, rồi deploy bằng `wp-staging-deploy`, rồi chạy `web-qa-gate` trên production có kiểm bản có cache. Purge theo URL bằng `purge_urls.php` của `wp-staging-deploy`. Không purge toàn site.
8. **Trả về khi hỏng.** Chuyển mu-plugin vào quarantine hoặc `theme_patch.py restore` từ backup, rồi purge theo URL. Ghi lệnh trả về vào `<lane>/rollback.md` trước khi ghi production.
9. Tự phản biện theo mục dưới, rồi tự kiểm theo Gate, rồi trả.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Bảng nguồn có rule thắng của mọi thuộc tính cần đổi, lấy từ `match.mjs`, trước khi viết rule mới. Rule mới qua `match.mjs --css` với mã thoát 0. Nguồn lỗi: CSS form thua specificity, lane đẩy staging 3 lượt, site mẫu gtvseo 18/10/2026 21:00.
- [ ] `css_sources.sh` chạy lại sau khi sửa: nguồn 1–6 còn 0 bản sao giá trị cũ, hoặc dòng còn lại có lý do giữ. Nguồn lỗi: 5 file critical CSS còn `height:350px` sau lần sửa 19/10, ngày 20/10 làm lại 1 lane.
- [ ] Thẻ hoặc nút vừa đổi có số đo `:hover`, `:focus`, `:visited` (`match.mjs --state`, `web-qa-gate`). Nguồn lỗi: `:visited` cộng `:hover` ra chữ trắng trên nền trắng, 18/10/2026 17:33.
- [ ] Phép đo nghiệm thu dựa trên phần tử nhìn thấy trong viewport và đã ra FAIL trên bản chưa sửa. Nguồn lỗi: slider 22/10/2026 đo bằng `slick-current` ra dương tính giả, 268 phút.
- [ ] `ui-rules.md` có danh sách component đặc biệt, và CSS loại chúng trước khi áp thang chữ. Nguồn lỗi: thang chữ đè công cụ trong bài ở 8 URL, mục lục con to hơn cha ở 181/186 bài, 21/10/2026.
- [ ] Thay đổi toàn site có pilot 2 trang và trang so sánh đã được chọn trước khi mở rộng. Nguồn lỗi: H1 56 px và menu mất mô tả, người duyệt phải hỏi lại, 19/10/2026.
- [ ] Mỗi việc là một mu-plugin có id và marker riêng, lệnh trả về ghi trong `rollback.md`. Nguồn lỗi: review đối kháng 18/10/2026 phải gỡ 3 rule gây hồi quy nằm chung bản vá vòng 1–2 (H1 toàn cục, flex menu, 13 px diện rộng).

## Output

Thư mục đợt do người giao việc chỉ định. Mặc định: `04-structure-ux-cro/ui-fix/<YYYY-MM-DD>-<việc>/` của instance.

| File | Nội dung |
|---|---|
| `nguon-css.md` | Bảng nguồn → selector → giá trị → cách sửa → bản sao còn lại |
| `match*.json`, `css_sources.tsv` | Số đo gốc của Bước 2 |
| `spec.json`, `backup/`, `quarantine/MANIFEST.tsv` | Spec của `theme_patch.py`, bản gốc, file đã chuyển ra |
| `type-truoc/`, `type-sau/` | `type_probe.json`, ảnh, kết quả `type_check.py` (khi chạm chữ) |
| `shots/` | Ảnh hai lượt, `shots_<nhãn>.json`, `so-sanh_v<N>.html` |
| `rollback.md`, `bao-cao.md` | Lệnh trả về; kết luận, số đo, bằng chứng sau khi ghi |

## Gate

- [ ] Thay đổi nhìn thấy trên toàn site có một dòng trong tin chat, kèm ảnh.
- [ ] Không đổi UX người duyệt quen dùng khi chưa hỏi.
- [ ] Bản ngôn ngữ phụ dùng chung template, CSS, menu và cỡ chữ với bản chính. Cặp ảnh hai ngôn ngữ chỉ khác vùng chữ.
- [ ] Không ghi production khi pilot chưa được duyệt.
- [ ] `css_sources.sh` sau khi sửa không còn bản sao giá trị cũ ở nguồn 1–6 (trừ dòng có lý do).
- [ ] Khi chạm chữ: `type_check.py` không còn lỗi mức fail trên trang pilot.
- [ ] `web-qa-gate` PASS trên staging và production, có bản có cache.
- [ ] Khối style có marker version ở bản có cache và bản bỏ cache.
- [ ] Output in ra chat và file không chứa host staging: chạy `skills/wp-staging-deploy/scripts/stg_leak_check.sh` trên thư mục đợt trước khi báo xong.
- [ ] Không bịa số. Phần chưa đo (WebKit, CrUX) ghi rõ là chưa đo.

## Anti-patterns

- Viết rule rồi mới truy nguồn → chạy `match.mjs` và `css_sources.sh` trước.
- Sửa file gộp cache hoặc CSS Elementor sinh ra → sửa bản nguồn rồi purge theo URL.
- Thêm `!important` để thắng mà không đọc dòng "muốn đè" → đè bằng specificity có scope. Chỉ dùng `!important` khi rule gốc đã có `!important`.
- Ẩn cả phần tử sticky khi chụp → chỉ ẩn fixed. Ca thật: `measure.mjs` cũ làm mất ảnh hero mobile, Jev báo lỗi giả.
- Viết lại script đo đã có trong skill này, `web-qa-gate` hoặc `wp-pagespeed` → gọi script có sẵn theo `$UIF`.
- Trình phương án font hay thang chữ bằng chữ → trình bằng trang so sánh.

## Changelog

- v1.0 (2026-10-25): tạo mới từ đề xuất ui-1 và ui-3 (rà skill web 16–24/10/2026). `truy-nguon-css.md` thêm bẫy `widget_text` của Max Mega Menu và bẫy panel mega menu không mở bằng hover khi headless (ui-5); Bước 7 trỏ hạng mục 13–14 của `web-qa-gate` sau mỗi bản sửa. Script `match.mjs` (`--css` thử rule), `css_sources.sh`, `theme_patch.py`, `type_probe.mjs`, `type_check.py`, `shot_el.mjs`, `so_sanh.py`; 3 reference; test offline 47 ca.
