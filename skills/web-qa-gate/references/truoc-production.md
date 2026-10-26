# Cổng trước production

File này ghi các bước chạy trước khi báo "staging xong, chờ đưa lên production". Một lượt cổng trả lời đủ các câu người duyệt hay hỏi: skeleton theme, PageSpeed, bảo mật, form, tracking. Đọc file khi chạy chế độ "cổng trước production" ở SKILL.md.

Lỗi đã gặp: site agency mẫu 17/10/2026, Claude báo 2 trang đã lên staging và chỉ chờ duyệt nội dung. Người duyệt phải hỏi lại: "đã kiểm skeleton chung theme? PageSpeed? bảo mật? test form?". Phần làm bù mất 34 phút.

Cổng chỉ đọc. Không ghi gì lên staging hay production trong lúc chạy cổng.

## Thứ tự

| # | Việc | Lệnh hoặc nơi làm | Đạt khi |
|---|---|---|---|
| 1 | Đủ 14 hạng mục trên staging | `qa_gate.py run ... --cache both`, danh sách URL có 1 URL mỗi template (trang chủ, page, post, chuyên mục, trang có form) | Report không còn FAIL. Mọi WARN đã xem và có kết luận. |
| 2 | Skeleton theme | `truoc_production.py skeleton <out>` | Không FAIL header hoặc footer. CSS và JS chặn render không lệch giữa template. |
| 3 | Bảo mật phía khách | `skills/wp-security-hardening/scripts/exposure_check.sh` cho mã HTTP của đường dẫn nhạy cảm; `truoc_production.py headers <out>` cho header bảo mật | `exposure_check.sh` exit 0, mã mong đợi theo quyết định bảo mật của site trong skill đó. Header thiếu có lý do. |
| 4 | Form và đường đi của lead | `hang-muc.md` mục 4, phần "Đường đi của lead"; gửi thử trên staging theo `form-gui-that.md` | Đủ 5 chặng đạt. Hộp thư nhận mail có token. |
| 5 | Tracking production và staging | Lượt `run` trên production cùng danh sách URL, rồi `truoc_production.py diff`; đọc trigger GTM theo mục dưới | Không thẻ nào mất. Mọi điều kiện trigger phụ thuộc DOM vẫn khớp trên staging. |
| 6 | Mã HTTP 3 môi trường | Chỉ khi đổi theme, theo mục dưới | Mọi dòng lệch có lý do. |
| 7 | Smoke trước và sau deploy | Theo mục dưới | Không trang nào đổi từ 2xx sang mã lỗi. |
| 8 | PageSpeed | Skill `wp-pagespeed` | Theo cổng của skill đó. Cổng này không đo tốc độ. |

Lệnh mẫu cho bước 1 đến 3 (staging qua Basic Auth: export `WEB_QA_AUTH` cho `qa_gate.py`, và đặt `EXPOSURE_CURL_CONFIG` là file cấu hình curl cho `exposure_check.sh`; không in giá trị ra chat hay file):

```bash
python3 -E skills/web-qa-gate/scripts/qa_gate.py run --config <ev>/qa.json --out <ev>/qa-stg-<YYYYMMDD-HHMM> --cache both --tabs 3
python3 -E skills/web-qa-gate/scripts/truoc_production.py skeleton <ev>/qa-stg-<YYYYMMDD-HHMM> [--ignore <class nút đổi ngôn ngữ>]
bash skills/wp-security-hardening/scripts/exposure_check.sh https://stg.example.vn
python3 -E skills/web-qa-gate/scripts/truoc_production.py headers <ev>/qa-stg-<YYYYMMDD-HHMM>
```

Lệnh `headers` đọc file `.hdr` đã lưu, không gọi mạng. Lệnh báo WARN khi thiếu HSTS (trang https), `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, hoặc cả `X-Frame-Options` lẫn CSP `frame-ancestors`. Header có thể do CDN thêm, nên chạy thêm trên lượt production. Lượt thử 25/10 trên header đã lưu của site agency mẫu: bộ 19/10 thiếu HSTS trên 6/6 trang, bộ 23/10 đủ cả 5 loại.

Đọc kết quả skeleton:

- Script chỉ so trang cùng `<html lang>`. Bản EN có menu khác bản VI là chủ ý.
- FAIL nghĩa là cấu trúc thẻ của header hoặc footer khác nhóm chính: một template đang dùng header hoặc footer khác.
- WARN nghĩa là cùng cấu trúc nhưng khác chữ hoặc thuộc tính. Mở 2 file HTML trong `raw/html/` và so phần header.
- Vùng được phép khác giữa trang, ví dụ nút đổi ngôn ngữ chỉ hiện ở trang có bản dịch: khai `--ignore` với chuỗi con của class hoặc id. Ghi lý do vào báo cáo.
- H1 kiểm ở hạng mục 14e. Canonical kiểm ở hạng mục 9. Script skeleton không chấm lại hai phần này.

## Tracking production và staging (bước 5)

1. Chạy `run` trên production với cùng danh sách URL, thêm `--skip browser,interact,og,jev`. Lượt này chỉ tải HTML.
2. So: `truoc_production.py diff <ev>/qa-prod-<giờ> <ev>/qa-stg-<giờ> --labels prod,stg`. Thẻ có ở production mà không có ở staging là FAIL.
3. Lấy mã container GTM từ dòng "Thẻ thấy trong HTML" của report.
4. Đọc trigger của container:
   - Có quyền GTM: xuất container và đọc trigger.
   - Không có quyền: tải `https://www.googletagmanager.com/gtm.js?id=<GTM-ID>` một lần bằng curl, rồi tìm chuỗi điều kiện trong file.
5. Liệt kê điều kiện phụ thuộc DOM: class hoặc id của nút gửi form, link dạng `m.me`, link `tel:`, selector của CTA.
6. Tìm từng điều kiện trong HTML staging (`raw/html/`). Theme mới đổi class của nút gửi là lỗi im lặng: thẻ vẫn tải, nhưng sự kiện không bắn.

Script chưa so sự kiện `dataLayer` giữa hai môi trường. Phần này kiểm tay theo bước 4 đến 6.

## Mã HTTP 3 môi trường (bước 6)

Dùng khi đổi theme, để tách lỗi do theme với lỗi do dữ liệu.

1. Chuẩn bị 3 lượt `run` cùng danh sách URL: production, staging theme mới, staging theme cũ cùng DB. Đổi theme trên staging là việc ghi: làm theo skill `wp-staging-deploy`, không làm trong cổng.
2. So: `truoc_production.py diff <prod> <stg-moi> <stg-cu> --labels prod,stg-moi,stg-cu`.
3. Đọc cột kết luận:

| prod | stg-moi | stg-cu | Script ghi | Nghĩa |
|---|---|---|---|---|
| 200 | 404 | 200 | lệch chỉ ở stg-moi | Nghi do theme hoặc bản mới |
| 200 | 404 | 404 | stg-moi và stg-cu cùng lệch | Nghi do dữ liệu staging |

## Smoke trước và sau deploy (bước 7)

1. Lấy danh sách URL bằng WP-CLI theo hồ sơ server: `wp post list --post_type=page,post --post_status=publish --field=url > urls.txt`. Không lấy từ sitemap: sitemap bỏ trang noindex và có thể còn URL cũ.
2. Đổi sang urls.tsv có tham số bỏ cache: `python3 -E skills/web-qa-gate/scripts/truoc_production.py urls urls.txt --base https://example.vn --nc > urls.tsv`.
3. Trước deploy, chạy lượt chỉ tải HTML: `python3 -E skills/web-qa-gate/scripts/qa_gate.py run --base https://example.vn --urls urls.tsv --out <ev>/smoke-truoc --skip browser,interact,og,jev`.
4. Sau deploy, tạo lại urls.tsv bằng lệnh ở bước 2 rồi chạy lại bước 3 với `--out <ev>/smoke-sau`. Tên URL giữ nguyên, chỉ chuỗi `nc=` đổi.
5. So: `truoc_production.py diff <ev>/smoke-truoc <ev>/smoke-sau --labels truoc,sau`. Script bỏ tham số `nc=` khi ghép đường dẫn.
6. FAIL khi trang đổi từ 2xx sang mã khác, hoặc trả 5xx hay `000`. Bỏ qua kết luận canonical trong report của lượt smoke, vì URL có tham số `nc=`.

## Báo xong

- Báo kết luận của từng bước, đường dẫn `report.md` và file JSON của `truoc_production.py`, giờ chạy.
- Bước không chạy ghi lý do và việc cần làm để chạy được.
- Báo "sẵn sàng lên production" chỉ khi bước 1 đến 5 đạt, và bước 6 đến 8 đạt hoặc có lý do không áp dụng.
