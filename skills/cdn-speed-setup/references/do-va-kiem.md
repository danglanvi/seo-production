# Đo và kiểm: nền, trước đổi, sau đổi, hẹn kiểm

Nạp ở bước 1, 3, 6 của SKILL.md. Mỗi số ghi (đo) hoặc (ước). Production: tối đa 2 request đồng thời, 1 request/giây.

## 1. Đo nền

1. **Cơ cấu file Googlebot tải.** Lấy từ log origin 7–21 ngày (`seo-logfile-analysis`). Chia theo nhóm: HTML 200, HTML 3xx, HTML 4xx, ảnh, CSS/JS, file tĩnh 4xx, xml/txt. Ghi tỉ lệ request từng nhóm. Site VN ngày 26/10/2026: ảnh chiếm 57% lượt Googlebot.
2. **GSC Crawl Stats.** Lead xuất average response time theo loại file, 90 ngày. Nếu chưa có, ghi "chưa có mốc GSC".
3. **TTFB không tính DNS** (tcp + tls + firstByte) theo vùng, bằng `scripts/geo_verify.py --groups VN,US,EU`:
   - Mỹ: Ashburn, Dallas, Los Angeles, Chicago, San Jose.
   - Châu Âu.
   - VN: từng nhà mạng (AS7552 Viettel, AS45899 VNPT, AS18403 FPT, AS45903 CMC, AS24086).
4. **RTT origin → Mỹ.** Site VN: khoảng 200 ms mỗi vòng. Đây là M trong mô hình GSC.
5. **PageSpeed và CrUX.** PSI cho site VN chạy từ châu Á, nên đi thẳng origin ở nhánh B. CrUX là cửa sổ 28 ngày. Không dùng hai số này để chứng minh CDN cải thiện LCP của khách VN.

## 2. Kiểm trên tên thử (trước khi đổi apex)

- **SEO trùng:** ≥ 20 URL × 2 UA (Googlebot smartphone, desktop). So mã, canonical, hreflang, meta robots, X-Robots-Tag, title, JSON-LD. robots.txt và sitemap phải trùng byte. Redirect và 410 phải trùng. Bản cache không có Set-Cookie.
- **Cookie bypass:** request có cookie `wordpress_logged_in_x=1` phải BYPASS.
- **File tĩnh có query:** CSS/JS `?ver=` phải HIT ở lượt 2.
- **TTFB lượt đầu và lượt lặp** từ Mỹ, n ≥ 20. Site VN (Bunny, Origin Shield ở Mỹ): lượt đầu 67,5 ms, lượt lặp 20,5 ms.

## 3. Sau khi đổi apex

1. `geo_verify.py` ngay sau khi đổi, sau đó sau 30 phút.
2. **Mẫu DNS khách VN (nhánh B):**
   - `dns_sample.py local`: ≥ 50 vòng, mỗi vòng 10 giây. Hỏi qua resolver hệ thống, 1.1.1.1, 8.8.8.8 và NS Cloudflare.
   - `dns_sample.py globalping --country VN`: ≥ 10 vòng.
   - Gate: ≥ 95% lượt nhận origin, trên ≥ 4 nhà mạng × 3 loại resolver × ≥ 2 vòng.
   - Ghi giờ từng lượt, để tách mẫu trước và sau một lần sửa script.
   - Một vòng 12/12 không đủ. Site VN: mẫu 1 vòng đạt 12/12, nhưng mẫu 50 vòng qua 8.8.8.8 thấy 10% lượt nhận CDN.
3. **Tỉ lệ trúng cache:**
   - Lấy từ log CDN hoặc API thống kê (Bunny `/statistics`), theo nhóm file.
   - Không lấy từ vài request thử. Site VN: ước GSC 332 ms dùng tỉ lệ trúng ảnh 0,33 từ 3 request. Log cho 0,018, tính lại được 417 ms.
4. **Ước GSC:**
   - Viết `mix.json` gồm share (log Googlebot) và hit (log CDN) theo nhóm.
   - Chạy `scripts/rt_model.py --mix mix.json`. Script in h, RT (ước), ngưỡng h cho 250 và 200 ms, và 3 nhóm kéo RT nhiều nhất.
5. **5xx:** chạy `log_health.py` của `seo-logfile-analysis` trên log origin từ giờ đổi. Mã thoát 0 là đạt.
6. **Log origin sau CDN:** lượt Googlebot trúng cache ở edge không vào log origin. KPI crawl đọc từ log origin sẽ thiếu. Kéo log CDN về cùng chỗ (`seo-logfile-analysis`).

## 4. Hẹn kiểm sau 5–7 ngày

- Đặt lịch khi đổi apex. Ghi lịch vào HANDOFF.
- Việc cần làm:
  - Đọc GSC Crawl Stats: average response time theo loại file, từ ngày đổi.
  - Đổi các số (ước) thành (đo).
  - Chạy lại mẫu DNS VN.
  - Đọc tỉ lệ trúng cache 7 ngày.
  - Kiểm số dư nhà CDN, hạn chứng chỉ, và kết quả cron làm nóng.
- Nếu GSC chưa đạt KPI: xem nhóm file nào kéo RT (`rt_model.py`), làm nóng nhóm đó, hoặc nâng thời gian lưu edge.

## 5. Globalping

- Quota: 250 probe mỗi giờ cho mỗi IP. Mỗi probe trong một phép đo tính 1: một phép đo DNS với 8 probe tốn 8. Quota dùng chung cho mọi lane trên cùng máy.
- `geo_verify.py` và `dns_sample.py globalping` đọc `/v1/limits` trước khi đo, và dừng nếu thiếu quota. Site VN 26/10/2026: 10 vòng mẫu DNS VN tốn 240 probe, lượt kiểm Mỹ ngay sau đó trả file rỗng.
- Khi hết quota, kiểm phía Mỹ bằng log origin: Googlebot thật (dải IP Google) không được gọi thẳng origin sau khi đổi apex. Lượt trúng cache ở CDN không vào log origin.
- Không đặt được User-Agent. Muốn đo theo UA Googlebot, dùng `curl --resolve` tới IP trạm CDN (`warm.py` làm cách này).
- Query string đặt ở trường `query`, không đặt trong `path`.
- Nếu hết quota: chờ đầu giờ sau. Không đổi IP để lách quota.
