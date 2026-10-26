---
name: textlink-analyzer
description: "Lọc URL + gợi ý anchor text cho chiến dịch textlink PR quy mô lớn (1.000-5.000 links/đợt, đặt sidebar trên bài báo đã tồn tại). Use when: (1) 'lọc URL đặt textlink', 'phân bổ anchor text', 'plan textlink cho [domain]'."
metadata:
  version: "1.2.0"
---

# Textlink Analyzer & Suggest

Vận hành hóa chiến dịch textlink PR (case chuẩn: Rạng Đông Mall / Elmall): **lọc URL từ export khổng lồ bằng slug-only** → **phân bổ quota per trang đích** → **anchor plan theo tỷ lệ an toàn**. Quy mô vài chục nghìn URL → bắt buộc chạy **script**, không đọc tay từng dòng.

## Phân vai

| Việc | Skill |
|---|---|
| Lọc URL báo + anchor plan cho chiến dịch textlink của MÌNH | ✅ Skill này |
| Phân tích backlink profile ĐỐI THỦ (link gap, linkable assets) | `backlink-research` |
| Lập kế hoạch backlink tổng (target/anchor/method/velocity) | `backlink-plan` — skill này nhận handoff từ đó |
| Internal link trong site | [[Internal Linking Rules and Strategy]] + P17 |

## Input

**Required:**
- `$TARGETS` — danh sách trang đích: URL + keyword chính (+ volume nếu có) + **quota link** (vd case chuẩn: homepage ~400 · category tầng 1 ~90/trang · trang đặc thù ~150). Thiếu quota → dùng tỷ lệ case chuẩn theo loại trang, flag.
- `$URL_EXPORT` — file/paste danh sách URL bài báo (CSV/TXT; mỗi domain có thể vài chục nghìn URL).
- `$BRAND` — tên brand + biến thể (vd: "Rạng Đông Mall", "rạng đông mall", "rangdongmall", "rangdongmall.com").

**Optional:**
- `$RATIO` — tỷ lệ anchor chỉ định; không có → dùng **tỷ lệ an toàn mặc định** (bên dưới).
- `$BACKLINK_DATA` — export "pages by backlinks / best by links" của các domain báo (Ahrefs) → cộng điểm URL có backlink. Không có → đề xuất pull qua Ahrefs MCP (top N, cost-aware) hoặc bỏ tiêu chí này, flag rõ.
- `$DOFOLLOW` (default 1) · `$CAP_PER_DOMAIN` (default: không dồn >30-35% tổng link 1 đợt vào 1 domain).

**Công cụ:** `scripts/textlink.py` (thư viện chuẩn) có 3 lệnh `filter`, `enrich`, `allocate`. Test: `tests/test_textlink.py`.

## Workflow 6 bước

### Bước 1 — Bộ từ khóa lọc 3 tầng (LLM sinh, Vincent duyệt nhanh)
Từ `$TARGETS` sinh term-set để match trên slug, mỗi tầng gồm **cả dạng có dấu, không dấu, và dạng-gạch-nối** (slug tiếng Việt luôn không dấu: "den-led-nha-xuong"):
- **Tier A — trang đích:** keyword đích + synonyms + biến thể (vd đèn pha led → den-pha-led, den-pha, chieu-pha, den-led-chieu-pha…).
- **Tier B — topic/category:** nhóm chủ đề gần (chieu-sang, den-led, tiet-kiem-dien, nang-luong…).
- **Tier C — domain-level:** ngành rộng liên quan brand (dien, cong-nghe, xay-dung, do-thi, san-xuat…).
Kèm **negative terms** (chủ đề không nhận: chinh-tri, tai-nan, phap-luat hình sự… tùy brand safety). Thêm tên đối thủ cùng ngành vào negative: báo địa phương có nhiều bài PR của agency khác (lượt thử 19/10/2026: 6 bài PR dịch vụ SEO của đối thủ trên 1 báo).

Ghi term-set vào `terms.json`: `{"targets": [{"url", "quota", "A": [...], "B": [...]}, {"url", "quota", "home": true}], "C": [...], "neg": [...]}`. Viết term có dấu; script tự sinh dạng không dấu và dạng-gạch-nối.

### Bước 2 — Script lọc bulk (slug-only, KHÔNG crawl)
Chạy `python3 -I scripts/textlink.py filter --urls <file>... --terms terms.json --out <W>/candidates.csv`. File URL là TXT mỗi dòng 1 URL, CSV có cột `url`, hoặc kết quả Ahrefs đã lưu. Script làm các việc: (1) parse URL → bỏ domain, tách token slug theo `-`/`/`, bỏ số/id/đuôi .html; (2) match 3 tier term-set → score (A=3đ/term, B=2đ, C=1đ, negative = loại); (3) dedupe URL; (4) output CSV: `url | domain | tier | score | matched_terms`. Vài chục nghìn URL chạy trong giây — matched_terms giữ lại làm **evidence** để Vincent spot-check.
- Script cảnh báo term A/B từ 2 tiếng trở xuống. Bỏ dấu làm trùng nghĩa: "khóa học" và "khoa học" cùng slug `khoa-hoc`. Đọc `matched_terms` của các dòng khớp term ngắn, hoặc thay bằng term dài hơn.

### Bước 3 — Cộng điểm backlink (nếu có data)
Lấy số: Ahrefs `site-explorer-top-pages` của từng domain báo (select `url,sum_traffic,referring_domains`, where `url` isubstring theo chủ đề, tối đa 250 dòng), hoặc `batch-analysis` cho danh sách URL (100 URL/lần). Chạy `textlink.py enrich --candidates <W>/candidates.csv --ahrefs <file>... --out <W>/candidates_ahrefs.csv`.

Join `$BACKLINK_DATA` theo URL → cột `refdomains/backlinks`; URL có backlink trỏ tới được ưu tiên trong cùng tier (đúng tiêu chí 2 của quy trình). Không có data → xếp theo score + đa dạng domain.

### Bước 4 — Phân bổ URL đi link ↔ trang đích
- **Tier A URLs** → trang đích category/money tương ứng (relevance trang đích là ưu tiên 1).
- **Tier B URLs** → category tầng 1 / trang đích gần chủ đề.
- **Tier C URLs** → homepage/brand (nơi hấp thụ link chung chung an toàn nhất).
- Ràng buộc: đủ quota per target; cap per domain; 1 URL báo không gánh quá nhiều trang đích (mặc định 1-2).
- Chạy `textlink.py allocate --candidates <W>/candidates_ahrefs.csv --terms terms.json --cap-domain 0.33 --out <W>/plan.csv`. URL khớp nhiều target đi về target khớp nhiều term nhất. Script báo target còn thiếu quota: thiếu thì mở thêm domain báo, không nới cap.

### Bước 5 — Anchor plan theo tỷ lệ

**Tỷ lệ an toàn mặc định** (chuẩn hóa từ case Rạng Đông Mall — Vincent override bằng `$RATIO`). **Framework đầy đủ bundled tại [references/anchor-ratio-framework.md](references/anchor-ratio-framework.md)** (⭐ Lớp 1: mô hình 3 giai đoạn trust — bảng dưới ≈ giai đoạn 2; site giai đoạn ĐẦU → co nhóm từ khóa về ~30%, Exact ≈ 0-3%; + SERP-consensus + Authority-Aggression + footprint) — có xung đột thì framework thắng. *(Bản canonical gốc sống ở `backlink-plan/references/` — 2 bản sync md5.)*:

| Anchor Type | Homepage | Category/Money page | Ghi chú |
|---|---|---|---|
| Brand thuần | ~23% | ~10% | "Rạng Đông Mall", "rạng đông mall" |
| Khớp một phần (Partial) | ~23% | ~25% | keyword + từ mở rộng, không nguyên cụm exact |
| Link trần (Naked URL + URL Full) | ~17% | ~15% | domain.com / https://… |
| Brand + Keyword | ~14% | ~20% | "đèn led panel rạng đông" |
| Chính xác (Exact) | **≤8%** | **≤10%** | trần cứng — vượt = over-optimization |
| Chung chung (Generic) | ~8% | ~7% | "xem thêm", "tại đây" (+ mô tả trước/sau) |
| Anchor đồng nghĩa | ~4% | ~8% | synonym của keyword ("đèn tấm chiếu sáng led") |
| Title anchor | ~3% | ~5% | title bài đích |

- **Format anchor 3 phần** đúng sheet vận hành: `Mô tả trước + Từ khóa + Mô tả sau` (vd "đèn led panel" + "chính hãng") — tự nhiên hóa, tránh anchor cụt lặp hàng loạt.
- Mỗi keyword exact/partial phải **tồn tại trong content trang đích** (anchor rule); generic anchor luôn kèm mô tả ngữ cảnh.
- Đa dạng: không lặp 1 anchor y hệt quá ~10 lần/đợt trên cùng domain báo.

### Bước 5b — Gate QA 6 bước cho link đặt trong thân bài (SOP 10 §2 luật 6)

Áp cho mọi dòng plan đặt link **trong thân bài** (niche edit, guest post, textlink chèn vào đoạn văn). Chấm trên bản nháp hoặc đoạn văn sẽ chèn, trước khi gửi nhà cung cấp:

| # | Kiểm | Đạt khi |
|---|---|---|
| 1 | Vị trí | Link nằm ở một đỉnh "link desire": câu nêu nguồn, câu đưa claim, hoặc tên người đọc muốn tra |
| 2 | Link khác | Bài có link ra nguồn thật khác, không chỉ 1–3 link báo/gov đặt cho đủ công thức |
| 3 | Mục đích | Link phục vụ 1 trong 10 mục đích: ghi công, nguồn số liệu, giải nghĩa, đào sâu, chỉ rõ đối tượng, ví dụ, hành động, quan hệ, bằng chứng, quảng bá |
| 4 | Trang đích | Trang mạnh nhất cho vị trí đó (bài/trang dịch vụ cụ thể), không mặc định homepage |
| 5 | Anchor | Khớp cách host tự đặt anchor; không chèn từ khoá đích nếu host không viết như vậy |
| 6 | Phép thử mù | Người không biết khách là ai không đoán được link trả tiền |

- Ghi kết quả vào cột `Gate QA` dạng `6/6` hoặc `4/6 (thiếu 1, 6)`. Dòng chưa đạt 6/6 thì đề xuất sửa câu chèn, không đẩy sang nhà cung cấp.
- Link **sidebar**, footer, trang chủ, chuyên mục: không qua được bước 1 và 6 theo thiết kế. Ghi `Gate QA = n/a (sidebar)` và đưa rủi ro "Google có thể bỏ qua link không báo" vào mục Caveats. Không tự đổi dạng đặt link; dạng đặt link do plan quyết định.
- Bước 5 (anchor) của gate cộng thêm vào tỷ lệ anchor ở Bước 5, không thay thế. Nếu anchor theo tỷ lệ lệch cách host viết, ưu tiên cách host viết và ghi lệch tỷ lệ vào Caveats.
- Nguồn: Dejan Petrovic 2026 qua wiki `Knowledge/Semantic SEO A - Z/wiki/sources/link-building-outreach-ai-search-dejan-2026.md`.

### Bước 6 — Output đúng format vận hành

```markdown
# Textlink Plan — [brand] · đợt [n] · [tổng link]
## 1. Bảng plan chi tiết (CSV + markdown)
   Mô tả trước | Từ khóa | Mô tả sau | URL đích | Dofollow | Số link | Volume | Anchor Type | URL đi link (từ danh sách lọc) | Vị trí đặt (thân bài / sidebar) | Gate QA
## 2. Tổng phân bổ: bảng % per anchor type per trang đích — so với tỷ lệ target, lệch >2% → flag
## 3. Danh sách URL đi link đã lọc: theo tier + score + matched_terms (+backlinks nếu có)
## 4. Caveats: tiêu chí bỏ qua (không có backlink data?), domain cap, đề xuất velocity, số dòng chưa đạt gate QA, rủi ro link sidebar
```

### Tự phản biện trước khi trình

Bản tốt nhất phải có:

- [ ] Không URL nào là bài PR của đối thủ cùng ngành. Nguồn lỗi: lượt thử 19/10/2026 xếp bài "dịch vụ SEO Mona Media" vào tier A.
- [ ] Đã đọc `matched_terms` của dòng khớp term ngắn. Nguồn lỗi: bài Sở Khoa học và Công nghệ khớp "khóa học" (19/10/2026).
- [ ] URL khớp nhiều target nằm ở target khớp nhiều term nhất. Nguồn lỗi: bài khoá học SEO của bên khác vào trang dịch vụ SEO ở bản script đầu.
- [ ] Quota từng target khớp tổng; target thiếu quota được báo, không bù bằng nới cap.
- [ ] Tỷ lệ anchor qua `backlink-plan/scripts/plan_tools.py check`. Nguồn: `references/anchor-ratio-framework.md`.
- [ ] Dòng đặt trong thân bài có Gate QA 6/6.

## Phân việc model

| Năng lực | Việc | Quyết định |
|---|---|---|
| Code (`textlink.py`) | lọc slug, điểm tier, join số Ahrefs, phân bổ | dùng |
| Claude | sinh term-set, đọc ca term ngắn và bài PR, Gate QA | dùng |
| EmbeddingGemma | độ gần của tiêu đề bài báo với trang đích, thay term ngắn | chưa: slug đủ cho lọc thô; xét khi đợt có trên 1.000 URL |
| Jev | brand safety của tiêu đề bài | chưa: chưa có rubric và gold |
| GLM Flash | — | không cần |

## Behavior Gates

- **#1 Think Before:** confirm targets + quota + ratio + có/không backlink data trước khi chạy script.
- **#2 Evidence:** mỗi URL lọc kèm `matched_terms`; mỗi con số % truy được về bảng đếm — không áng chừng.
- **#3 Surgical:** output là plan + danh sách — KHÔNG tự đặt link, không crawl hàng loạt (slug-only theo đúng quy trình), không đề xuất mua thêm hạng mục ngoài yêu cầu.
- **#4 Goal-driven:** đủ 4 section output; quota per target khớp tổng; tỷ lệ trong ngưỡng; mọi dòng đặt trong thân bài có điểm gate QA.

## Risk note (1 lần, không rao giảng)

Textlink số lượng lớn là chiến thuật có rủi ro theo Google guideline — skill vận hành theo quyết định chiến dịch của Vincent, kèm giảm thiểu: exact ≤ trần, rải velocity theo tuần (không bung 5.000 link 1 ngày), track theo đợt trong sheet, giữ danh sách domain để disavow được khi cần.

## Anti-patterns

- Exact-match vượt trần (footprint over-optimization rõ nhất).
- Lọc bằng crawl toàn bộ URL (chậm + thừa — yêu cầu gốc là đọc slug).
- Quên biến thể **không dấu** khi match slug tiếng Việt → sót gần hết.
- Không dedupe / không cap per domain → dồn link 1 báo.
- Anchor generic đứng trơ ("tại đây") không có mô tả trước/sau.
- Bảng plan thiếu cột Anchor Type / Số link → sheet vận hành không dùng được.
- Đẩy link trong thân bài sang nhà cung cấp khi gate QA chưa đạt 6/6.
- Đặt link trên bài PR của đối thủ cùng ngành → thêm tên đối thủ vào negative.

## Wiki cross-ref

[[Internal Linking Rules and Strategy]] (anchor principles — nhiều rule áp được cho external) · [[Entity Home]] (brand anchor = entity signal) · [[Source Authority]] · `backlink-research` (đối thủ lấy link ở đâu → nguồn URL export mới) · `backlink-plan` (plan tổng, giữ bản canonical anchor framework)

## Changelog

- **v1.2.0 (2026-10-19):** `scripts/textlink.py` (filter, enrich, allocate) và test offline; lấy số trang báo qua Ahrefs top-pages; negative gồm tên đối thủ; cảnh báo term ngắn; tự phản biện; phân việc model. Lượt thử 73 URL baodanang.vn cho gtvseo.com và theaigrowth.io.
- **v1.1.1 (2026-10-19):** `anchor-ratio-framework.md` đổi nhãn "LSI" thành "đồng nghĩa/biến thể".
- **v1.1.0 (2026-10-13):** thêm Bước 5b gate QA 6 bước cho link đặt trong thân bài (SOP 10 v1.3 §2 luật 6, Vincent duyệt 13/10/2026); bảng plan thêm cột `Vị trí đặt` và `Gate QA`; link sidebar ghi n/a và đưa rủi ro vào Caveats.
- **v1.0.3 (2026-07-04):** STANDALONE — bundle `anchor-ratio-framework.md` vào references/ của chính skill (trước trỏ `../backlink-plan/` → gãy khi tách folder); sync rule 2 chiều với canonical.
- v1.0.2 (2026-07-04): note mô hình 3 giai đoạn trust trước bảng ratio.
- v1.0.1 / v1.0 (2026-07-04): bản đầu + fix refs sau rename backlink-research.
