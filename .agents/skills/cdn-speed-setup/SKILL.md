---
name: cdn-speed-setup
description: "Chọn, dựng và kiểm CDN cho site WordPress để giảm thời gian phản hồi Googlebot (GSC Crawl Stats) và TTFB khách: nhánh Global (proxy Cloudflare) hoặc nhánh VN (chia vùng, khách VN đi thẳng origin). Dùng khi site chậm với Googlebot hoặc cần CDN."
metadata:
  version: "1.3.2"
---

# cdn-speed-setup — CDN theo vị trí origin và khách

Googlebot crawl chủ yếu từ Mỹ. Origin đặt ở VN cách Mỹ khoảng 200 ms mỗi vòng, nên average response time trong GSC khó xuống dưới 250 ms nếu không có CDN. Proxy Cloudflare gói Free lại đưa khách VN sang trạm Singapore, Hồng Kông hoặc châu Âu, làm khách VN chậm hơn đi thẳng. Skill chọn nhánh theo vị trí origin và khách, dựng có lệnh trả lại, rồi đo bằng số.

## Khi nào dùng

- GSC Crawl Stats báo average response time cao, hoặc Lead muốn CDN cho site WordPress.
- Đổi nhà CDN, đổi cách chia vùng, hoặc kiểm lại CDN đang chạy (hẹn kiểm sau 5–7 ngày).
- Không dùng khi: chỉ tối ưu origin (cache trang, PHP, CSS, ảnh) → `wp-pagespeed`; chỉ phân tích log crawl → `seo-logfile-analysis`.

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Domain, vị trí origin (nước, nhà cung cấp), web server (OLS/LiteSpeed, Nginx, Apache) | `PROJECTS/<site>/00-client-context/wp-server.md` | Hỏi |
| Khách chính ở đâu (VN, châu Á, toàn cầu), KPI (average response time GSC, TTFB khách) | Lead | Hỏi. Không đoán KPI |
| Ngân sách CDN/tháng | Lead | Hỏi trước khi trình phương án có phí |
| Quyền: token Cloudflare (DNS Edit, Cache Rules, Zone Settings), key Bunny (nhánh B), SSH origin (chỉ đọc) | `.agent-secrets/.env` hoặc biến môi trường | Dừng, ghi việc Lead cấp quyền |
| Mốc trước: GSC Crawl Stats (theo loại file), log origin 7–21 ngày | Lead xuất GSC; log qua SSH | Ghi "chưa có mốc GSC", vẫn đo TTFB |

## Quyền hành động trên Cloudflare

Mặc định dưới đây do người duyệt chốt 26/10/2026 cho 2 site nội bộ. Site khách: hỏi Lead dùng mặc định này hay luật riêng, rồi ghi vào `wp-server.md`.

| Việc | Cách làm |
|---|---|
| Đọc DNS và cấu hình; tạo hoặc xoá bản ghi tên thử; purge cache theo URL | Tự làm |
| Bật proxy cho apex hoặc www, kể cả bật thử vài phút | Lead duyệt một lần mỗi zone, sau checklist: rà Worker, route, token theo `wp-security-hardening/references/ra-tai-khoan-cdn.md` và so trang qua edge với UA trình duyệt và UA Googlebot; SSL Full (strict), IP thật ở origin, Bot Fight Mode tắt, Browser Cache TTL theo origin, giới hạn của gói (Free: 100 MB mỗi request, 100 giây) |
| Tắt proxy để cứu khi 5xx tăng, lỗi SSL, Googlebot bị chặn | Tự làm ngay, báo sau |
| Chỉnh cache, bot, HTTP/3 sau khi đã bật proxy | Tự làm, ghi lệnh trả lại, báo sau |
| Sửa bản ghi đang chạy khác (MX, TXT), firewall | Hỏi Lead từng lần |
| Xoá tài nguyên, thành viên, token, 2FA trong tài khoản | Lead tự bấm. Agent đọc và đề xuất |

- Kiểm quyền token bằng một lệnh đọc trước khi dùng. Token thiếu quyền trả 403 (site VN 26/10/2026: Load Balancers, Workers Routes).
- Đọc token từ file secret bằng code, không in ra chat hay file.
- Chọn CDN: xét giải pháp trên Cloudflare trước. CDN khác là phương án khi Cloudflare không đạt KPI theo số đo. Bảng phương án nói rõ CDN mới là thêm hay thay.

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| Jev | QA số liệu trong báo cáo tổng kết với file nguồn (rubric `claim-evidence`); phân loại user-agent lạ trong log khi số lượng lớn | Dùng cho QA tổng kết (thử 26/10/2026: 41 câu, 0,002 USD, 0 mâu thuẫn, Claude đọc lại 18 câu "not_in_evidence"). Phân loại UA: chỉ khi > 200 UA lạ |
| EmbeddingGemma 2 | Không có việc so ngữ nghĩa | Không dùng |
| GLM Flash | Không có việc trích câu | Không dùng |
| Claude | Chọn nhánh, viết cấu hình, đọc số, kết luận, đọc lại mục Jev gắn cờ | Dùng |
| Script | Đổi DNS nguyên khối, gửi script DNS chia vùng, đo Globalping, lấy mẫu DNS, làm nóng cache, mô hình GSC | `scripts/` |

## Quy trình

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,ssh,jev?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

1. **Đo nền** theo `references/do-va-kiem.md` §1: cơ cấu file Googlebot tải (HTML, ảnh, CSS/JS, 3xx, 4xx), TTFB không DNS theo vùng (Mỹ, châu Âu, châu Á, từng nhà mạng VN), RTT origin → Mỹ. Ghi mỗi số (đo) hoặc (ước).
2. **Chọn nhánh** theo `references/chon-phuong-an.md`:
   - Nhánh A (Global): khách chủ yếu ngoài VN, hoặc origin ở Mỹ/châu Âu → proxy Cloudflare toàn site. Đọc `references/nhanh-a-cloudflare-proxy.md`.
   - Nhánh B (VN): origin và khách ở VN → chia vùng: châu Á đi thẳng origin, vùng khác đi CDN. Đọc `references/nhanh-b-chia-vung.md`.
   - Trình bảng phương án có giá/tháng, rủi ro và số đo, đánh dấu phương án rẻ nhất đạt KPI. Chờ Lead chọn.
3. **Dựng không chạm apex**: cấu hình CDN trên tên thử (`*.b-cdn.net`, tên phụ proxy), so HTML qua CDN với đi thẳng, kiểm cookie bypass, đo TTFB lượt đầu và lượt lặp. Origin của CDN phải là IP, Host là domain (tránh vòng lặp sau khi đổi apex). Nhánh B: gửi script DNS bằng `scripts/bunny_geo_script.py` (dựng từ `templates/geo-dns-script.js`).
4. **Đổi apex** chỉ khi Lead duyệt riêng, giờ thấp điểm: `scripts/cdn_dns_switch.py backup` → `switch --apply` (batch nguyên khối) → kiểm ngay bằng `scripts/geo_verify.py`. Trả lại: `unswitch --apply`.
5. **Sau khi đổi** theo `references/origin-sau-cdn.md`: IP thật ở origin, làm nóng cache (`scripts/warm.py`, có ảnh), purge khi sửa bài, đồng bộ chứng chỉ, giám sát (`scripts/cdn_monitor.py`), nạp tiền nhà CDN.
6. **Đo sau và hẹn kiểm** theo `references/do-va-kiem.md` §3–4: TTFB theo vùng, mẫu DNS khách VN (`scripts/dns_sample.py`, Globalping), tỉ lệ trúng cache, ước GSC bằng `scripts/rt_model.py`. Đặt lịch kiểm lại GSC sau 5–7 ngày.
7. Tự phản biện theo mục dưới, chạy Gate, rồi viết tổng kết. QA số liệu tổng kết bằng Jev `claim-evidence`.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Lead.

Bản tốt nhất phải có:
- [ ] Bảng phương án có giá/tháng, rủi ro, số đo, nói rõ nhà CDN thêm hay thay, và có phương án tự build hoặc mã nguồn mở. Nguồn lỗi: site VN 26/10/2026, người duyệt chọn rồi bỏ Load Balancing vì 15 USD/tháng chỉ thấy ở bước mua; người duyệt nhắc 12:07 "suy nghĩ kỹ… thêm các giải pháp", phương án chia vùng ra sau lần nhắc.
- [ ] Khách VN được đo theo từng nhà mạng và từng loại resolver (DNS nhà mạng, 1.1.1.1, 8.8.8.8), nhiều vòng. Nguồn lỗi: site VN 26/10/2026, mẫu 1 vòng đạt 12/12 nhưng mẫu 50 vòng qua 8.8.8.8 thấy 10% lượt bị đưa sang CDN Mỹ.
- [ ] Origin của CDN là IP + Host header, www được xử lý riêng, bản ghi đổi bằng batch. Nguồn lỗi: site VN 26/10/2026, origin `https://<domain>` sẽ lặp về CDN sau khi đổi apex; www CNAME về apex đi theo CDN.
- [ ] Rule bypass query không bắt file tĩnh. Nguồn lỗi: site VN 26/10/2026, CSS/JS `?ver=` BYPASS 80,8% lượt.
- [ ] Ảnh và HTML được làm nóng, có lịch hằng ngày. Nguồn lỗi: site VN 26/10/2026, ảnh chiếm 57% lượt Googlebot, trúng cache 1,6–1,8%.
- [ ] Mã vùng trong script DNS lấy từ danh sách vùng chính thức của nhà CDN, test với mã trạm Mỹ. Nguồn lỗi: site VN 26/10/2026, mã trạm Los Angeles "LA" trùng mã Lào, Googlebot bờ Tây bị đưa về origin 2 phút.
- [ ] Rủi ro điểm hỏng đơn lẻ có cách xử lý: số dư nhà CDN, giám sát, lệnh trả lại. Nguồn lỗi: site VN 26/10/2026, Bunny trả DNS cho cả khách VN trong khi số dư 0.
- [ ] Số GSC ghi (ước) cho tới khi có Crawl Stats thật; tỉ lệ trúng cache lấy từ log CDN, không từ vài request. Nguồn lỗi: site VN 26/10/2026, ước 332 ms dùng h ảnh 0,33 từ 3 request; log cho 0,018, tính lại 417 ms.

## Output

- Thư mục việc: `PROJECTS/<site>/<thư mục đợt>/cdn/`: `bao-cao-nen.md`, `phuong-an.md`, `rollback.md` (mỗi thay đổi một lệnh trả lại), `backup/v1..`, `work/` (JSON đo, che IP), `tong-ket_v1.md`.
- Tổng kết: bảng yêu cầu → trạng thái → bằng chứng; số trước/sau (TTFB theo vùng, GSC ước/đo, LCP lab và CrUX); việc còn lại theo mức; việc chờ Lead quyết.

## Gate / tự kiểm trước khi trả

- [ ] SEO qua CDN trùng đi thẳng: mã, canonical, hreflang, meta robots, X-Robots-Tag, title, JSON-LD trên ≥ 20 URL × 2 UA; robots.txt và sitemap trùng byte; redirect và 410 trùng.
- [ ] Khách VN: ≥ 95% lượt DNS nhận origin trên ≥ 4 nhà mạng × 3 loại resolver × ≥ 2 vòng (nhánh B). Tỉ lệ còn lại ghi rõ.
- [ ] Googlebot vùng Mỹ: 100% lượt DNS nhận CDN, TTFB lượt đầu sau khi làm nóng ≤ 260 ms.
- [ ] 0 lỗi 5xx mới ở origin (`log_health.py` của `seo-logfile-analysis`, mã thoát 0).
- [ ] CDN lưu mã lỗi (Bunny `CacheErrorResponses` bật): mọi edge rule thời gian cache có điều kiện mã; rule chặn dùng danh sách mã được lưu. Kiểm theo `references/nhanh-b-chia-vung.md` §2b.
- [ ] `rollback.md` có lệnh trả lại đã chạy DRY. Không file nào chứa IP origin, token, key.
- [ ] Phần chưa thử thật ghi "chưa thử".

## Anti-patterns

- Bật proxy Cloudflare toàn site cho site VN có khách VN → khách VN bị đưa ra trạm nước ngoài. Dùng nhánh B.
- Xoá bản ghi A rồi mới tạo CNAME → khoảng NODATA bị resolver cache tới 30 phút. Dùng batch.
- Tin GeoIP của IP resolver Cloudflare để định vị khách → lệch vùng. Kết hợp mã trạm DNS nhận câu hỏi.
- Gộp IP CDN thành /24 khi khai IP tin cậy ở origin → máy khác cùng dải được giả IP. Khai đúng IP.
- Đo PageSpeed rồi kết luận CDN cải thiện LCP cho site VN → PSI chạy từ châu Á, đi thẳng origin.
- Đo TTFB của Googlebot từ máy ở VN tới trạm CDN ở Mỹ → đường VN–Mỹ cộng vào cả lượt HIT. Đo từ Mỹ theo `references/do-va-kiem.md` §3 mục 7.
- Viết "CDN cho Googlebot" trong tài liệu hướng ra ngoài → người duyệt bác cách nói này (26/10/2026). Nói lợi ích tốc độ cho khách ở xa origin.

## Kiểm thử

- Test offline: chạy `python3 -B scripts/tests/test_cdn.py` (23 ca) và `python3 -B scripts/tests/test_monitor.py` (35 ca) từ folder skill. Không gọi mạng.
- `test_monitor.py` giữ các ca từ rà soát đối kháng giám sát ngày 26/10/2026: gửi tin lỗi phải gửi lại ở vòng sau, lỗi chập chờn phải được báo, lỗi origin không kèm lệnh trả DNS, state hỏng được cách ly.
- Ca thật trong bộ test: mã trạm Bunny "LA" (Los Angeles) trùng mã quốc gia Lào; hai danh sách vùng của template phải trùng `scripts/geo_rule.py`.
- Chạy lại test sau mỗi lần sửa danh sách vùng trong template.

## Changelog

- v1.3.2 (2026-11-02): `cdn_monitor.py` gọi lại trang qua HTTP từ 3 probe Globalping ở Mỹ (`confirm_far`) khi máy giám sát nhận mã 0 từ trạm CDN, thêm 4 test. Nguồn: site VN 28/10–02/11/2026 có 20 vòng báo giả. `origin-sau-cdn.md` §3: làm nóng mọi ảnh mỗi ngày (Bunny xoá ảnh ít dùng sau 1–4 ngày). §5: ghi bước gọi lại qua probe Mỹ.
- v1.3.1 (2026-10-30): `nhanh-a-cloudflare-proxy.md` bước 2 thêm cách tách rule cache HTML và rule Bypass (thứ tự rule, cookie thử thách `cf_clearance`, `__cf_bm`, header `s-maxage` + `stale-while-revalidate`); bước 7 ghi ca APO chạy cùng LiteSpeed Cache khi tắt Guest Mode; mục 3 thêm kiểm `cf-cache-status` giỏ hàng. Nguồn: nhật ký tối ưu site TMĐT mẫu của SEO Lead dự án, 30/10/2026.
- v1.3 (2026-10-27): `nhanh-b-chia-vung.md` §2b mới: edge rule theo mã khi Bunny lưu mã lỗi, sitemap 1 ngày, edge rule không đặt được `Accept-Encoding`; §2 bước 4 sửa rule ảnh và sitemap cho khớp. `origin-sau-cdn.md` §2 biến thể cache theo loại file, §3 bỏ nhãn "chưa thử" và thêm chờ 30 giây sau purge, §8 mới về Brotli ở Bunny. `do-va-kiem.md` §3 mục 7 đo Googlebot từ Mỹ theo bảng lớp × cache (từ VN, lượt HIT vẫn 738–802 ms). Quyền bật proxy dẫn sang `ra-tai-khoan-cdn.md`. Gate thêm 1 mục, Anti-pattern thêm 2 mục, eval thêm 2 ca. Đã chạy thật trên production site agency mẫu 27/10/2026, 2 lane đạt kiểm độc lập: 301 từ Mỹ 678–713 → 4–14 ms, 410 663–708 → 3–6 ms, sitemap HIT 2–9 ms; rule ảnh 30 ngày giữ 167 URL ảnh 404 trong 63 phút trước khi thêm điều kiện mã; Brotli 10/10 URL HTML, nhỏ hơn gzip 8,9%. Phần ước GSC và tác động lên Googlebot thật chờ lượt kiểm 31/10/2026.
- v1.2 (2026-10-27): `warm.py` gửi HTML với Accept có `image/webp` (`--accept`), test `test_warm_html_accept_webp`; bản trước dùng `*/*` của curl, trái với `origin-sau-cdn.md` §2. §2 thêm cách làm nóng đúng trạm bot dùng bằng ECS (site VN: 85/85 lượt Googlebot vào một trạm). Mục mới "Quyền hành động trên Cloudflare" chép từ luật người duyệt chốt 26/10 (trước chỉ nằm trong memory của một runtime). Checklist mục 1 thêm phương án tự build. `evals/cases.yaml` 5 ca. Phần ngưỡng theo số GSC sau đổi apex: phiên CDN cập nhật sau lượt kiểm 31/10.
- v1.1.1 (2026-10-26): `nhanh-b-chia-vung.md` bước 5 sửa cache trình duyệt. Thiết lập zone 600 giây làm CSS/JS md5 mất max-age 1 năm (phiên tối ưu crawl phát hiện). Thêm edge rule 16 giá trị -1 (theo origin) cho file tĩnh. Điều kiện Request URL không xét query string. `origin-sau-cdn.md` §2–§3: HTML đổi theo Accept mà Bunny không tách được, cách purge Bunny xoá cả bản mobile.
- v1.1 (2026-10-26): thêm giám sát `scripts/cdn_monitor.py` (launchd, báo Telegram qua `hermes send`, chỉ báo), mẫu cấu hình `templates/cdn-monitor.example.json`, 31 test. Chạy thật trên site VN từ 26/10/2026. Trước khi cài: 3 agent rà soát đối kháng: 35 phát hiện, 11 mức cao, gộp trùng còn 6 lỗi (ví dụ kiểm hỏng làm mất cả vòng, gửi tin lỗi bị tính là đã báo, máy ngủ thì giám sát chết im lặng). 1 phát hiện sai (trường API tài khoản Bunny), đã đối chiếu bằng lượt gọi thật. Đã sửa rồi rà lại. `origin-sau-cdn.md` §5 viết lại.
- v1.0 (2026-10-26): tạo mới từ đợt CDN site VN (WordPress, OLS, VPS ở VN), 26/10/2026: Cloudflare edge, Bunny thử, chia vùng bằng Bunny DNS + CNAME flattening. Nhánh A, O4, cron làm nóng ảnh, mu-plugin purge: chưa thử thật. Hẹn cập nhật sau lượt kiểm GSC 31/10/2026.
