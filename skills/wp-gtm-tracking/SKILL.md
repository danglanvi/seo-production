---
name: wp-gtm-tracking
description: "Sửa tracking GA4, Google Ads qua GTM trên site WordPress có quyền server: kiểm hit thật có chặn, dựng container bằng API, dataLayer tiền tố ga4_, hoãn GTM có trần, publish có backup, theo dõi 7 ngày. Dùng khi đổi container, sự kiện thiếu hoặc đôi, hoãn GTM vì tốc độ."
metadata:
  version: "1.1.0"
---

# wp-gtm-tracking — GTM, GA4 và Ads trên site WordPress

Skill này là lớp thi công của đo lường. `cro-measurement-plan` quyết đo sự kiện nào và vì sao. Skill này kiểm hit thật trên site, dựng container, áp có backup, và theo dõi sau áp. Lớp 7 của `wp-pagespeed` (hoãn GTM) trỏ sang skill này.

Kết quả chạy thật trên site bán lẻ mẫu (WooCommerce, plugin Google Listings & Ads), 28–30/10/2026: GA4 nhận 0 sự kiện thương mại trong 5 tháng vì container không có tag cho dataLayer. Container mới có 10 tag, 8 trigger, 9 biến. Kiểm preview trên site sống: 9/9 ca đạt, 509 hit bị chặn, 0 hit lọt. Conversion Ads bỏ đơn chưa trả và đơn sandbox (9/9 ca thử). Hoãn GTM 2 s sau `load`: trang sản phẩm 76,5 → 85 điểm so với 1 s.

Đường dẫn: đặt `GT` bằng thư mục chứa file SKILL.md này. Trong repo SEO Production, đứng ở root repo thì `GT="skills/wp-gtm-tracking"`.

## Khi nào dùng

- GA4 thiếu sự kiện (thương mại, lead, click gọi, Zalo) hoặc đếm đôi `page_view`, `add_to_cart`.
- Đổi container GTM, gỡ gtag gắn thẳng, hoặc đổi cách đo Google Ads.
- Hoãn GTM để tăng điểm PSI đã được duyệt (lớp 7 của `wp-pagespeed`).
- Không dùng khi: chưa có measurement plan (chạy `cro-measurement-plan` trước); không có quyền server hoặc quyền GTM API (giao spec cho dev theo `cro-measurement-plan`).

## Đọc trước

- `00-client-context/wp-server.md`: SSH, WP-CLI, plugin chèn code, plugin cache, luật riêng về tracking của site.
- Measurement plan của site (`_TEMPLATES/measurement-plan.md` hoặc output của `cro-measurement-plan`).
- `references/kiem-va-ap.md`: Bước 1, 3, 5, 6.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Container đang chạy, GA4 measurement ID, Ads ID | HTML trang, `gtm_inventory.py` của `wp-pagespeed` | Đọc từ trang |
| Token GTM API (file JSON 0600, biến `GTM_TOKEN_FILE`), quyền Publish | Người vận hành | Chỉ đọc `gtm.js` công khai, dựng bằng giao diện GTM |
| Quyền GA4 Data API | `wp-server.md` hoặc tài khoản Google của team | Ghi giới hạn: không đo được sự kiện theo ngày |
| Nơi chèn snippet (option plugin chèn code, theme) | WP-CLI `option get`, code theme | Hỏi |
| Trần hoãn GTM | Người duyệt | Không hoãn |
| Phạm vi duyệt: publish, đổi snippet, sửa mu-plugin, đổi cài đặt GA4 | Người duyệt | Chỉ dựng workspace và kiểm preview |

## Phân việc model

| Model | Việc | Quyết định |
|---|---|---|
| Script | Backup và dựng container (`gtm_api.py`), test loader (`tests/run.sh`), kiểm hit có chặn, PSI A/B | Dùng. Cổng giao là kết quả tất định |
| Jev | Phân loại hit | Không dùng. Số hit mỗi ca đếm bằng code, không có việc chấm chữ |
| EmbeddingGemma 2 | Gom URL theo template | Không dùng. Loại trang lấy từ `page_type` và cây URL |
| Claude | Thiết kế container, đọc hit, trang quyết, áp, báo cáo | Dùng |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,node,chrome,ssh,wp-cli,pagespeed-api?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

Kiểm thêm: `php -v` có PHP CLI (test loader cần), và `bash "$GT/tests/run.sh"` trả mã 0.

1. **Hiện trạng (chỉ đọc).** Thư mục làm việc `03-audits/technical/gtm-<YYYY-MM-DD>/`.
   - Backup container live: `GTM_TOKEN_FILE=<file> python3 -I "$GT/scripts/gtm_api.py" inventory --container GTM-… --backup-dir ~/Backups/<site>/<ngày>/gtm-pre`.
   - Đếm hit thật trên mỗi loại trang theo `kiem-va-ap.md` mục 1: số `page_view` mỗi lượt tải, tag nạp 2 lần, tham số lạ (`em`).
   - GA4 Data API 90 ngày theo tên sự kiện. Đối soát conversion Ads với đơn theo trạng thái và cổng thanh toán.
   - Ghi `hien-trang.md`: bảng lỗi L1… có bằng chứng, mức P0–P2 và cách sửa.
2. **Thiết kế container** theo `kiem-va-ap.md` mục 2–4. Ghi `thiet-ke.md`: bảng tag, trigger, biến, phần khác measurement plan và lý do. Dựng trong workspace mới bằng API, `quick_preview` không lỗi. Không publish.
3. **Kiểm preview trên site sống** với hit bị chặn (`kiem-va-ap.md` mục 1). Đạt khi mọi ca đúng số hit và 0 hit lọt. Lỗi ở preview thì sửa thiết kế rồi chạy lại cả bảng ca.
4. **Hoãn GTM** (chỉ khi người duyệt cho phép và đặt trần).
   - Site chèn snippet bằng option plugin (Insert Headers and Footers): dùng `templates/gtm-delay-loader-option.php`. Site chèn ở theme: dùng `templates/gtm-delay-loader.php` của `wp-pagespeed`.
   - Loader nạp ngay ở giỏ, checkout, trang cảm ơn và URL có `utm_`, `gclid`, `fbclid`. Loader bỏ gtag G gắn thẳng khi container có Google tag, hoãn thẻ AW của plugin Ads, tái phát tối đa 5 click link, tắt bằng đuôi `.off`.
   - Loader nạp thẻ AW của plugin cùng mốc với GTM, `async=false` để AW thực thi trước, nên Google tag không nạp lại `AW…&cx=c` (`kiem-va-ap.md` mục 8). Không nạp AW sớm hơn GTM. Kiểm bằng danh sách request: mỗi trang chỉ một thư viện `gtag/js?id=AW-…`.
   - Chọn N bằng A/B có ngưỡng ghi trước, trong trần (`kiem-va-ap.md` mục 5). Đây là trường hợp "tham số chọn bằng số đo" của `wp-pagespeed`, `luot-lon.md` mục 1.
   - Đổi hằng số trong bản cài thì chạy `LOADER=<bản cài> bash "$GT/tests/run.sh"`. Bản cài đổi tiền tố (ví dụ `site_gtm_`, `site-defer-src`) thì thêm `PREFIX=site`. Thiếu `PREFIX`, harness báo lỗi giả ở mọi bản cài.
5. **Trang quyết.** Dựng bằng `decision-page`: mỗi câu có ảnh hoặc ví dụ hit, đề xuất và lý do. Câu cần chọn rõ: publish và đổi snippet, lọc conversion Ads, cài đặt GA4 (tự phát hiện email, loại trừ referral), N giây và mốc tính.
6. **Áp một lượt** theo `kiem-va-ap.md` mục 6, sau khi người duyệt chọn. Mu-plugin đổi tên sự kiện lên trước, publish sau. Purge theo URL, lô tối đa 12.
7. **Kiểm sau áp và theo dõi 7 ngày** theo `kiem-va-ap.md` mục 1 (chế độ LIVE) và mục 7. Chép bảng kiểm sang `13-cro/<CLIENT>_tracking-qa_v<N>.md` và trace công đoạn #34.

### Tự phản biện trước khi trình
Chấm plan theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của agent khác cho cùng site, so từng mục trước khi trình.

Bản tốt nhất phải có:
- [ ] Hiện trạng đếm bằng hit thật có chặn, không chỉ đọc cấu hình container. Bộ chặn có `www.google.com/g/collect` và `/rmkt/collect`. Nguồn lỗi: site bán lẻ mẫu 30/10/2026, thiếu 2 đường dẫn này nên 48 `page_view` và 26 hit remarketing giả lọt ra Google.
- [ ] Sự kiện thương mại trong dataLayer có tiền tố `ga4_` khi site có plugin gọi `gtag('event', …)` cùng tên. Nguồn lỗi: site bán lẻ mẫu 30/10/2026, preview lượt 1 đạt 7/9 ca, `view_item` và `add_to_cart` đôi.
- [ ] Plan ghi thứ tự: mu-plugin đổi tên trước, publish sau, rollback ngược lại. Nguồn: thiết kế đã kiểm ở site bán lẻ mẫu 30/10/2026.
- [ ] Conversion Ads chỉ tính đơn đạt luật `purchase`; không thêm tag Ads trong GTM khi plugin còn bắn. Nguồn lỗi: site bán lẻ mẫu, 13 đơn có cờ conversion trong 7 ngày, 8 đơn sandbox.
- [ ] N giây chọn bằng A/B PSI có ngưỡng ghi trước, trong trần người duyệt đặt, ghi mốc tính từ `load`. Mỗi thư viện tag nạp 1 lần (đếm `gtag/js?id=` theo ID). Mọi đổi thứ tự hay mốc nạp tag có PSI cả 2 thiết bị trước khi áp, xem TBT và LCP. Nguồn: site bán lẻ mẫu 30/10/2026, 1,5 s đo kém hơn 2 s ở 2 đợt nên người duyệt chọn lại 2 s. Ngày 31/10: thư viện AW nạp 2 lần; bản sửa v1.3 làm TBT desktop tăng khoảng 60 ms; v1.4 nạp AW sớm 600 ms làm LCP mobile 2,2 → 3,7 s ở 3/6 lượt.
- [ ] Bản loader sẽ cài đạt `tests/run.sh`, gồm ca option không còn gtag G (`nog`) và listener `{once:true}`. Nguồn lỗi: site bán lẻ mẫu 30/10/2026 09:02, loader v1.1 để thẻ AW tải thẳng; plugin đánh giá phát lại `DOMContentLoaded` làm `add_to_cart` đôi.
- [ ] Loader tái phát click link đến trước khi GTM nạp, và bảng "hoãn GTM có mất gì" nêu 2 giới hạn còn lại. Nguồn lỗi: site agency mẫu 22/10/2026, mất click Zalo đầu tiên.
- [ ] Trang quyết có minh hoạ và đề xuất cho từng câu. Nguồn lỗi: người duyệt 30/10/2026 12:02 nói trang quyết khó hiểu.
## Output

- Thư mục làm việc: `hien-trang.md`, `thiet-ke.md`, `de-xuat.md`, `decisions.md`, bảng kết quả kiểm preview và kiểm sau áp, `theo-doi-7-ngay.md`, trang quyết.
- Backup ngoài repo: JSON container live, option snippet, option plugin Ads, mu-plugin cũ, kèm sha256.
- Trên site: mu-plugin dataLayer, loader (nếu hoãn), snippet container mới.

## Gate

- [ ] `tests/run.sh` trả mã 0 với đúng bản loader sẽ cài. `php -l` đạt trên server.
- [ ] Backup container live và option có sha256 trước lần ghi đầu.
- [ ] Preview: mọi ca đạt, selftest chặn đủ 10 hit, 0 hit lọt.
- [ ] Sau áp: mỗi trang 1 `page_view`, mỗi hành động 1 sự kiện, transient verify có `ok=1`, 0 dòng lỗi loader trong `error_log`.
- [ ] Purge theo URL, lô tối đa 12. 5xx = 0 sau áp.
- [ ] Annotation GA4 có mốc áp và khung giờ hit lọt (nếu có).
- [ ] Không in token, `gtm_auth`, email, số điện thoại hay mã đơn ra chat hoặc file.

## Anti-patterns

- Publish container trước khi mu-plugin đổi tên sự kiện.
- Kiểm tracking trên site sống mà không chặn hit.
- Thêm tag Ads conversion trong GTM khi plugin Ads vẫn gửi conversion.
- Hoãn GTM ở giỏ, checkout, trang cảm ơn, hoặc ở URL quảng cáo.
- Đổi N giây mà không đo, hoặc vượt trần người duyệt đặt.
- Dùng `requestIdleCallback` làm mốc nạp. Callback chạy ngay sau `load`, vẫn trong trace của Lighthouse.
- Sửa cài đặt GA4 (tự phát hiện email, loại trừ referral, key event) khi người duyệt chưa chọn.
- Purge All sau khi đổi snippet.

## Changelog

- v1.1.0 (2026-10-31): mẫu loader nạp thẻ AW của plugin và GTM cùng mốc, `async=false` để AW thực thi trước, dự phòng 4 s qua `google_tag_manager`; harness thêm 1 ca và biến `PREFIX` cho bản cài đổi tiền tố; `kiem-va-ap.md` mục 8 thêm bẫy AW nạp 2 lần, bẫy nạp AW sớm hơn GTM (LCP mobile) và bẫy A/B bằng `setBlockedURLs`; tự phản biện mục N giây thêm kiểm mỗi thư viện tag nạp 1 lần và PSI cả TBT lẫn LCP. Nguồn: site bán lẻ mẫu 31/10/2026 (instance của site, `03-audits/technical/gtm-3010/aw-mot-noi-3110/ket-qua.md`), loader v1.3, v1.4 rồi v1.5 trên production. Đã thử: Chrome có chặn hit trên 4 trang sống, AW 1 lần, hit như cũ, 0 hit lọt; harness đạt với mẫu và bản cài, bản v1.4 rớt đúng ca.
- v1.0.0 (2026-10-30): tạo mới từ site agency mẫu 22/10/2026 (loader tái phát click link) và site bán lẻ mẫu 28–30/10/2026 (container 10 tag dựng bằng API, preview 9/9 ca có chặn hit, tiền tố `ga4_`, lọc conversion plugin Ads, A/B N giây, thứ tự áp, theo dõi 7 ngày). Mẫu `gtm-delay-loader-option.php` là bản v1.2 đang chạy ở site bán lẻ mẫu, đã ẩn tên và ID. Harness PHP 11 kịch bản, 49 ca. `gtm_api.py` gồm inventory, preview-url, version, publish; publish chưa chạy qua script này (site mẫu publish bằng script riêng cùng lời gọi API).
