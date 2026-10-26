# SOP 11 — Đăng bài WordPress (WS06 Onpage & IL)

> Bản đóng gói cho SEO Production — sync từ `SEO wiki nội bộ «Semantic» (ngoài repo) SEO A - Z/sop/11-publish-wp.md` ngày 2026-08-29 (copy nguyên).
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

> Phạm vi: khâu đưa bài mới lên WordPress (NEW) + sửa bài đã publish qua REST API (AUDIT). **Bạn SEO (trạm 06) đảm nhận** — bộ phận content KHÔNG public lên website; fork `Content Production - <client>/` dừng ở Google Doc (Phase 7 gdoc, quyết định Vincent 2026-08-29).
>
> Tool thực thi: **wp-publish-workflow-kit** — repo riêng của team, KHÔNG vendor vào master. SOP này là luật vận hành GTV chạy TRÊN kit.

---

## 0. Phân vai & 2 flow input

| Flow | Ai | Đường đi |
|---|---|---|
| **A — bài từ team content** | Content viết, SEO đăng | Bài hoàn thiện dạng Google Doc → link Doc đính vào Google Sheet đăng bài (cột `Nguồn content`) → bạn SEO lấy Doc về → gate pre-publish (§2) → đăng qua NEW route |
| **B — bạn SEO kiêm content** | SEO tự viết + tự đăng | Viết local (markdown/HTML), vẫn qua đủ gate content (P0 + W-series) → đăng thẳng qua NEW route, không bắt buộc vòng qua Google Doc |

- **Registry đăng bài = Google Sheet 11 cột** theo schema kit: `Row ID · Bài / Title · Loại bài (NEW/AUDIT) · Nguồn content · Slug / URL WP · Meta description · Ngày public dự kiến · Trạng thái · URL draft/live · Note · Cập nhật lúc`. Template: `templates/sheet-template.csv` trong kit + sheet mẫu "Template quản lý onpage" của Vincent (https://docs.google.com/spreadsheets/d/1-MHsmTqp5t-hif7rHNM4NfFIgJCRxIiLBYtCnf9FE98/ — đã đối chiếu 2026-08-29: 11 cột khớp 100% schema kit; dòng pilot `WP-DEMO-001` minh họa đúng trạng thái `Chờ đăng` + URL draft + Note ghi post ID/media ID). Mỗi client 1 tab; share sheet cho service account của người vận hành.
- Sheet quyết định route (NEW/AUDIT); WordPress chỉ verify. Không tự đổi route.

## 1. Tool — wp-publish-workflow-kit

- Repo: `https://github.com/LongDZ1204/wp-publish-workflow-kit` (MIT). Clone riêng theo `docs/setup.md` / `docs/huong-dan-nguoi-moi.md` của kit; project data + credential nằm ngoài Git.
- **NEW route**: Sheet → Doc/markdown → bundle → gate ảnh/HTML → **approval hash SHA-256** (operator gõ lại hash mới được ghi) → tạo đúng 1 draft WP → readback verify → ghi Sheet. NEW **không bao giờ tự public** — dừng ở draft, trạng thái `Chờ đăng`; người có quyền duyệt mới bấm Publish trong WP.
- **AUDIT route**: fetch bài live (backup trước) → `edits.json` string-replace tối thiểu trên đúng `content.raw` → duyệt diff → update → verify + ghi `REVISION <id>` để rollback. Dùng cho công đoạn **#7** (execute action audit content), **#23** (điều chỉnh content & onpage) và output của skill `content-refresh`.
- Credential: user WordPress role **Editor riêng từng người** + Application Password. Không dùng Administrator. Không commit credential, không gửi qua chat (SECURITY.md của kit).
- Mọi lỗi của kit đều fail-closed (17 error code, không có warning) — gặp STOP thì xử lý nguyên nhân, không ép chạy tiếp.

## 2. Gate TRƯỚC khi đăng (pre-publish — chấm role `self`, fail = không đăng)

1. **Content V-Pass**: P0 content quality gate (9 items, SOP 08) + P0 pháp lý (7 items, checklist pháp lý content). Fail bất kỳ → trả về content, KHÔNG đăng.
2. **Meta**: P1 slug 3-5 từ không dấu đúng folder topical map · P2 title 50-60 ký tự, keyword 3 từ đầu, khác H1 · P3 meta description 150-160 ký tự · P5 đúng 1 H1 (kit enforce 1 H1 và giữ H1 trong body — source phải có đúng 1 H1).
3. **Strong policy (chốt 2026-08-29)**: mọi bold trong bài = thẻ `<strong>`, `<b>` = 0. **KHÔNG chạy bước strong-to-b của kit** ([[Semantic Emphasis]], P14).
4. **Ảnh**: chạy skill `image-seo-optimize` (mode plan → duyệt) → bảng filename/alt/caption/metadata đổ vào `doc-image-map.json` của kit. Ngưỡng P19-P20 + tier: hero ≤100KB không lazy · inline ≤150KB, max 1200px · alt tả đúng ảnh (Entity+Attribute+Action) · **filename tự cấp ASCII không dấu** (slugify của kit chưa transliterate tiếng Việt — không để kit tự derive từ alt/heading).
5. **Internal link** theo SOP 03 mục "checklist khi publish": ≥1 link tới pillar · sibling khi có ngữ cảnh chung (không quota) · **pillar update link ngược lại bài mới** · anchor = seed query hoặc biến thể của trang đích. Kit chưa có module IL → đặt link trong content TRƯỚC khi đăng (skill `internal-linking`).
6. **Block đặc biệt — kiểm tay**: blockquote / video iframe / schema JSON-LD. Route NEW của kit hiện **drop im lặng** mọi block ngoài whitelist (p, heading, list, table, figure) → bài có các block này thì sau khi draft lên phải đối chiếu và chèn lại (qua WP editor hoặc AUDIT route).

## 3. SAU khi đăng

- **Verify kép** = điều kiện duy nhất để báo "đã đăng": WP readback (`context=edit`, content khớp byte) + Sheet readback. Không có verify → chưa xong (Evidence rule).
- Dây chuyền chuẩn: publish → **+10-15 ngày** onpage batch P-series đầy đủ (template onpage-batch) → **+15-30 ngày** internal link semantic toàn cluster.
- Theo dõi: GSC impressions sau 7-30 ngày; bài orphan sau 30 ngày = IL chưa chạy (red flag, SOP 05).
- Ghi `index.md` (bảng B + D) + append `log.md` op `work`. Nhịp publish **patternless** — không đăng theo lịch cố định máy móc (SOP 01 anti-pattern).

## 4. Giới hạn kit hiện tại (chờ nâng cấp — spec gửi team kit)

| Giới hạn | Cách bù thủ công |
|---|---|
| AUDIT route chưa có approval hash, chưa so `modified` trước push | Duyệt diff tay 100%; chạy push ngay sau fetch, không để cách phiên |
| `width`/`height` + `loading="lazy"` chưa được gate | Kiểm tay theo P20 / VS-13 sau khi draft lên |
| Backup audit bị ghi đè khi audit lại cùng bài | Tự đổi tên backup kèm timestamp trước lần audit sau |
| Env var `WP_URL/WP_USER/WP_APP_PASS` override âm thầm `--site` | `unset` cả 3 env var trước khi chạy máy có nhiều site |
| Bước strong-to-b ngược policy `<strong>` | Bỏ qua bước này (§2.3) cho tới khi kit có mode `preserve-strong` |

---

*SOP mới 2026-08-29 — lấp khoảng trống "quy trình đăng bài lên CMS" (trước đây wiki chưa có). Nguồn: phân tích tích hợp wp-publish-workflow-kit + đối chiếu P-series/SOP 03/07/Semantic Emphasis.*
