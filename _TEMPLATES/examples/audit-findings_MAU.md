> ⚠️ MẪU MINH HỌA — client hư cấu "Công ty Ví Dụ / vidu.vn", số liệu giả định để agent noi theo CẤU TRÚC + ĐỘ SÂU + GIỌNG.
> Không copy số vào deliverable thật. Mẫu thật của dự án tích lũy trong instance qua vòng feedback → lesson → promote.

---
client: "Công ty Ví Dụ"
cong_doan: 5
ws: 03-audits
pic: An (SEO Lead Project)
status: final
version: v1
---

# Công ty Ví Dụ — Trích đoạn audit toàn diện T1 — chuẩn finding của trạm 03

> TRÍCH ĐOẠN dạy chuẩn từ bản đầy đủ `VIDU_audit-toan-dien_v1.md` (bản đầy đủ theo `_TEMPLATES/audit-toan-dien.md`: đủ 6 hạng mục, hạng mục sạch ghi PASS, không để trống). Mẫu giữ 8 finding tiêu biểu: mỗi finding PHẢI đủ **evidence trích được + phản chứng (falsifiability) + priority + owner + action gắn URL**. Thang mức độ: CRITICAL / MAJOR (≈ HIGH của template) / MINOR (≈ MEDIUM-LOW).

## 0. Scope (rút gọn)

| Trường | Giá trị |
|---|---|
| Domain | vidu.vn — crawl 400 URL, có JS-render (export 18/03/2026) |
| Kỳ audit | T1 toàn diện (công đoạn #5) |
| Data nguồn | GSC + Ahrefs + crawl — cùng ngày export 18/03; ảnh evidence lưu `02-raw/screenshots/` theo naming §8 |
| Baseline so sánh | n/a — audit đầu dự án |

## 1. CRITICAL (2)

### F1 · CRITICAL · Technical — robots.txt chặn toàn bộ nhóm URL money
- **Phạm vi:** 40 URL `/may-loc-nuoc/*` (toàn bộ danh mục + trang sản phẩm chủ lực).
- **Evidence:** `robots.txt` dòng 12: `Disallow: /may-loc-nuoc/` (ảnh `20260318_robots-vidu_full.png`); GSC Coverage 18/03: 40 URL "Bị chặn bởi robots.txt"; 0/40 URL có impression trong 90 ngày.
- **Phản chứng:** nếu URL Inspection trả "Đã lập chỉ mục" cho nhóm này thì finding SAI — đã test 5 URL mẫu, 5/5 báo bị chặn.
- **Priority:** P0 · **Owner:** anh Tú (dev khách) — An gửi spec sửa + verify.
- **Action:** xóa dòng Disallow → submit lại sitemap → verify 40/40 URL được index trong 14 ngày. Deadline 25/03.

### F2 · CRITICAL · Technical — index bloat: 200 URL parameter bị index, thiếu canonical
- **Phạm vi:** ~200 URL dạng `/may-loc-nuoc/?sort=...&page=...`.
- **Evidence:** GSC "Đã lập chỉ mục" 800 URL vs sitemap 400 URL; `site:vidu.vn inurl:sort=` ≈ 200 kết quả (ảnh `20260318_site-inurl-sort_serp.png`); crawl: nhóm parameter không có canonical về URL gốc.
- **Phản chứng:** nếu GSC báo nhóm này "Trang thay thế có thẻ canonical phù hợp" thì hạ mức MINOR — hiện GSC báo "Đã lập chỉ mục", tức Google đang coi là trang độc lập.
- **Priority:** P0 · **Owner:** anh Tú (dev) — An verify sau deploy.
- **Action:** canonical về URL gốc cho toàn nhóm sort/filter + xử lý phân trang theo chuẩn; theo dõi GSC Coverage 30 ngày, mục tiêu index về ~400 URL. Deadline 30/03.

## 2. MAJOR (3)

### F3 · MAJOR · Cấu trúc & internal link — 30 URL orphan, trong đó 10 URL SEO target
- **Evidence:** crawl 18/03: 30 URL có inlinks = 0 (chỉ xuất hiện trong sitemap), depth từ trang chủ ≥5; 10/30 thuộc cụm target "lõi lọc nước"; danh sách full trong phụ lục bản đầy đủ.
- **Phản chứng:** nếu crawl JS-render tìm thấy link từ mega menu thì không phải orphan — đã crawl JS-render, vẫn 0 inlink.
- **Priority:** P1 (sau khi P0 xong) · **Owner:** An (plan IL) + anh Tú (implement block).
- **Action:** thêm block "Sản phẩm cùng cụm" + breadcrumb 2 chiều cho 30 URL, nhập vào IL plan #18; tiêu chí đóng: orphan = 0 sau 30 ngày (log crawler). Deadline 10/04.

### F4 · MAJOR · Content — cannibalization query "máy lọc nước RO"
- **Evidence:** GSC 90 ngày: `/may-loc-nuoc-ro/` và `/blog/may-loc-nuoc-ro-la-gi/` cùng nhận impression một query (tỷ lệ 60/40), position dao động 8↔15 kiểu thay phiên; SERP check 18/03: bài blog đang outrank trang money.
- **Phản chứng:** nếu SERP hiển thị ỔN ĐỊNH cả 2 URL cùng lúc cho 2 intent khác nhau thì không phải cannibalization — thực tế mỗi thời điểm chỉ 1 URL xuất hiện.
- **Priority:** P1 · **Owner:** Chi (Content Leader).
- **Action:** refocus bài blog sang intent informational "cách chọn" + internal link về money page; money page giữ target query; theo dõi SERP 30 ngày sau sửa. Deadline 15/04.

### F5 · MAJOR · Entity — NAP không nhất quán + schema Organization thiếu
- **Evidence:** 3 biến thể tên công ty giữa footer web / hồ sơ doanh nghiệp trên Google / Facebook (bảng đối chiếu + 3 ảnh chụp trong phụ lục); JSON-LD Organization thiếu `sameAs` + `logo`.
- **Phản chứng:** nếu các hồ sơ đã verify cùng entity và tên rút gọn là tên đăng ký hợp lệ thì hạ mức — ĐKKD khách gửi chỉ có 1 tên chuẩn duy nhất.
- **Priority:** P1 · **Owner:** An + anh Tú.
- **Action:** thống nhất 1 biến thể tên trên 4 điểm chạm + bổ sung schema Organization đủ `sameAs`/`logo`; nhập vào #13 entity. Deadline 20/04.

## 3. MINOR (3)

### F6 · MINOR · Toppage — title trang chủ bị cắt trên SERP, H1 trùng title ở 15 trang danh mục
- **Evidence:** title trang chủ 75 ký tự, SERP desktop cắt mất vế giá trị cuối (ảnh `20260318_home-title_serp.png`); crawl: 15 trang danh mục có H1 = title 100%.
- **Phản chứng:** nếu Google rewrite title hiển thị đủ ý chính thì hạ ưu tiên thêm — hiện chưa thấy rewrite trên query brand.
- **Priority:** P2 · **Owner:** Chi · **Action:** viết lại title ≤65 ký tự cho 16 URL trong batch onpage #7. Deadline 30/04.

### F7 · MINOR · Content — 20 bài blog decay
- **Evidence:** GA4: nhóm 20 bài giảm từ ~1.000 còn ~200 sessions/tháng trong 6 tháng; so YoY cùng kỳ -60% (đã loại yếu tố mùa vụ); 5 bài trùng chủ đề mức thin.
- **Phản chứng:** nếu YoY cùng kỳ đi ngang thì chỉ là mùa vụ, loại khỏi decay — YoY xác nhận giảm thật.
- **Priority:** P2 · **Owner:** Chi · **Action:** KHÔNG refresh ngay — vào hàng chờ content-refresh kỳ audit T6 (#24) sau khi nền sạch; 5 bài thin đánh giá merge. Mốc: chốt plan trong audit T6.

### F8 · MINOR · Backlink — 15 referring domain rác trỏ về trang chủ
- **Evidence:** Ahrefs export 18/03: 15 RD nội dung cờ bạc/phim lậu, DR 0-5, anchor spam — chiếm 15/100 RD toàn profile.
- **Phản chứng:** nếu live-check các link đã chết thì bỏ finding — live-check: 12/15 còn sống.
- **Priority:** P2 · **Owner:** An · **Action:** THEO DÕI, chưa disavow (tỷ trọng nhỏ, không dấu hiệu manual action — disavow vội rủi ro hơn để yên); tái đánh giá kỳ audit T3-T4.

## 4. Bảng action tổng — sắp theo nguyên tắc SỬA NỀN TRƯỚC

| # | Action | URL / scope | Finding | Mức độ | Owner | Deadline | Status |
|---|---|---|---|---|---|---|---|
| 1 | Gỡ Disallow + submit sitemap + verify index | `/may-loc-nuoc/*` — 40 URL | F1 | CRITICAL | anh Tú | 25/03 | todo |
| 2 | Canonical nhóm parameter + chuẩn phân trang | `?sort=`/`?page=` — ~200 URL | F2 | CRITICAL | anh Tú | 30/03 | todo |
| 3 | Block "Sản phẩm cùng cụm" + breadcrumb 2 chiều | 30 URL orphan | F3 | MAJOR | An + anh Tú | 10/04 | todo |
| 4 | Thống nhất NAP + schema Organization đủ sameAs/logo | 4 điểm chạm entity | F5 | MAJOR | An + anh Tú | 20/04 | todo |
| 5 | Refocus bài blog + IL về money page | 2 URL cụm RO | F4 | MAJOR | Chi | 15/04 | todo |
| 6 | Viết lại title ≤65 ký tự (batch onpage #7) | 16 URL | F6 | MINOR | Chi | 30/04 | todo |
| 7 | Hàng chờ refresh 20 bài decay + merge 5 bài thin | 20 URL blog | F7 | MINOR | Chi | plan T6 | todo |
| 8 | Theo dõi 15 RD rác, tái đánh giá | profile backlink | F8 | MINOR | An | audit T3-T4 | todo |

Thứ tự tuân template §4: technical chặn crawl/index (F1, F2) sửa TRƯỚC mọi tối ưu → cấu trúc + internal link (F3) → entity (F5) → content/onpage từng URL (F4, F6, F7) → offpage đứng cuối và ở đây CHỈ theo dõi (F8). Còn CRITICAL mở → không mở chiến dịch offpage — gate #25 ở T6 sẽ soi lại đúng điều này.

## 5. Chuẩn một finding đạt (tự kiểm trước khi nộp)

- Evidence trích được: URL, con số, ảnh có naming §8 — cấm viết "nhiều URL bị lỗi".
- Có phản chứng: người khác biết cách chứng minh finding SAI → finding mới kiểm chứng được; phản chứng đã test thì ghi kết quả test.
- Action làm lại được: URL/scope + owner 1 người + deadline + tiêu chí đóng. Cấm action chung chung kiểu "tối ưu content".
- Mức độ chấm theo tác động tới crawl/index/doanh thu — không theo cảm giác.
