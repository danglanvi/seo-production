# Anchor Rules cho Internal Linking

Nguồn luật: [[Internal Linking Rules and Strategy]] (`wiki/concepts/core/onpage/`) — Koray Core Rules + §6 Anchor Text Rules + §GTV Extensions (Rule 59-60, trích từ `raw/guidelines/6. Semantic writing rules explain & note when writing with AI.md`) + §Intent Funnel. Mọi con số giữ nguyên từ nguồn — không chế thêm.

> ⚠️ **Evidence note (2026-07-13, LINT-2026-017):** Toàn bộ rule set = **GTV/Koray operating default** (`practitioner_framework`) — KHÔNG phải rule Google công bố. Official core chỉ gồm: link contextual hữu ích, anchor mô tả rõ, `<a href>` crawl được, hierarchy logic, tránh stuffing. Các ngưỡng cứng (≤3 anchor, 1 link/section, quotation-mark boost, đừng link research) dùng như default vận hành — được phép override khi có lý do; riêng "quotation marks tăng weight" = `hypothesis` chưa có nguồn xác nhận, và "đừng link research" cân nhắc ngược lại cho YMYL (cite nguồn uy tín = trust signal). Cách trích nguồn từ 19/10/2026: nêu tên nguồn bằng chữ, không đặt link ngoài (`references/link-js.md` D6).

---

## 1. 6 Anchor Text Rules (bắt buộc pass 6/6)

Cột "Giải thích" là **interpretation — không có trong nguồn**; wiki §6 Anchor Text Rules chỉ nêu rule, không nêu lý do. 6 rule ở cột "Rule" khớp verbatim.

| # | Rule | Giải thích (interpretation) |
|---|---|---|
| 1 | **Không dùng text từ first paragraph của target page** làm anchor | First paragraph là phần định nghĩa/answer của target — lấy nó làm anchor tạo duplication signal thay vì complementary signal. |
| 2 | **Không dùng first word của bất kỳ paragraph nào** làm anchor | First word mang vai trò mở context của đoạn — biến nó thành anchor phá cấu trúc discourse. |
| 3 | **Side-topic / khác context → anchor lấy từ last heading's paragraphs** | Link ra ngoài context chính chỉ được đặt ở phần cuối (last heading section) để giảm prominence, anchor cũng lấy từ vùng đó. |
| 4 | **Check competitor anchors** — cả internal lẫn external | Xem đối thủ top SERP dùng anchor gì cho cùng target concept → align với vocabulary consensus. ⚠️ Chỉ kiểm được khi có SERP data: Path A/B → check khi tiện; **Path C → skip + flag `competitor-anchor-pending`**, không tính vào 6/6. |
| 5 | **Dùng synonyms** | Không lặp 1 anchor y hệt — biến thể synonym để mở rộng relevance signal. |
| 6 | 🔴 **Anchor phải tồn tại trong target page content + heading liên quan của source** | Anchor = cầu nối 2 văn bản: phải xuất hiện thật trong target content (và ăn khớp heading section của source). Path C (chưa có content) → anchor chỉ là candidate, flag `verify-anchor`. |

## 2. Anchor mechanics (Koray Core Rules + SCN Case Study Rules)

- **≤3 lần cho 1 anchor text** — quá 3 lần lặp cùng anchor trong site → giảm weight/nghi ngờ pattern.
- **Anchor = seed query của target page** — seed query đó phải tồn tại trong target content kèm Q-A pairs. Có dữ liệu GSC: `scripts/anchor_gsc.py` liệt kê query của trang đích, gắn cờ luật 1, 2, 6, ≤3 lần và query thuộc trang khác ([scripts.md](scripts.md) §4).
- **Semantic lead-in bắt buộc**: đoạn văn TRƯỚC anchor phải nhắc khái niệm liên quan. Ví dụ GTV: muốn link "Chi phí du học Đức" → đoạn trước phải nhắc "chi phí"/"ngân sách". Không có lead-in tự nhiên → ứng viên no-link (Link-less Connection).
- **Quotation marks quanh anchor → tăng weight** — dùng chọn lọc cho anchor quan trọng.
- **Annotation text quanh anchor** với N-gram variants của target concept — tăng contextual relevance của link. (⚠️ Optimal length của annotation text = Open Question trong wiki, không bịa số.)
- **Anchor variation theo vị trí**: header → ngắn + prominent; footer → dài hơn; main content → kèm annotation text ([[Semantic Content Network]] 14 Rules #3).
- **Đừng link research papers/studies** bằng anchor chiến lược.
- **Multi-link cùng target trong 1 doc**: link thứ 1 pass PageRank + relevance; link thứ 2+ chỉ pass relevance → mặc định 1 link/target/doc.

## 3. Xác định số link/trang — 6 tiêu chí Koray (§Determining Link Count)

1. Industry standards min/max (quan sát SERP cùng ngành).
2. Số Named Entities trong document.
3. Số contexts của các Named Entities đó.
4. Granularity của content.
5. 🔴 **Max 1 link per heading section** (ngoại lệ hợp lệ: #6 bên dưới).
6. Entities cùng type dạng list → link về các page tương ứng. **Precedence: #6 thắng #5** — section dạng list entities cùng type (vd danh sách ngành/dịch vụ) được link từng page trong cùng section, flag `list-exception` trong plan.

Koray verbatim: **"There is no specific, and optimum internal link count"** — excessive links có thể bị ignore; no-logic links bị Cautious/Reasonable Surfer loại. (Patent number = Open Question, không bịa.)

## 4. Rule 59 — Semantic Distance-Based Internal Linking (GTV Extension)

**Nguyên tắc:** semantic distance vượt trội geographic/topical proximity bề mặt khi chọn target link.

**Ví dụ canonical (Visa Đức):**

| Cặp link | Đánh giá | Lý do |
|---|---|---|
| "Visa Đức" → "Visa Pháp" | ❌ | Láng giềng địa lý nhưng visa requirements khác nhau — proximity bề mặt |
| "Visa Đức" → "Visa Bulgaria" | ✅ | Cùng Schengen process — semantic distance gần dù địa lý xa |

**3 phương pháp xác định semantic distance:**
1. **User Search Behavior Analysis** — 2 topic có được search cùng session không.
2. **Co-occurrence Analysis** — 2 entity có xuất hiện cùng document/corpus không.
3. **Shared Entity Attributes matrix** — đếm overlap attributes giữa 2 entity (nhiều attribute chung → distance gần).

**Áp dụng trong skill:** khi 1 source page có nhiều target ứng viên, xếp hạng theo semantic distance (dùng 1-3 phương pháp trên, ghi phương pháp vào cột Lý do), không xếp theo "cùng category" bề mặt.

## 5. Rule 60 — Knowledge Domain Expansion Path (GTV Extension)

**Nguyên tắc:** không nhảy link trực tiếp giữa 2 knowledge domain xa nhau — phải bridge qua intermediate domains.

**Chain ví dụ:**
- Protein Whey → Muscle Recovery → Training → Competition → Sports Psychology (5 bước).
- GTV: SEO Services → Organic Traffic → Lead Generation → Customer Acquisition → Revenue → Business Growth (6 bước).

**Luật áp dụng:**
- 🔴 Mỗi outbound link cách source **tối đa 1 semantic step** trên expansion path.
- Dùng pattern này thiết kế hierarchy pillar → cluster → supporting.
- Buộc phải link cross-domain xa (business cần) → **chèn annotation text giải thích bridge** ngay quanh anchor, và flag trong plan.

## 6. Intent-anchor mapping (§Intent Funnel)

Direction: **Info → Commercial → Transactional, forward only** — không skip layer. Reverse chỉ cho breadcrumb / related article / related products widget. Exception: Hybrid Intent Page — main section (primary intent) link → page riêng cho secondary intent.

| Layer đích | Anchor style | Ví dụ |
|---|---|---|
| Info → Info | Seed query / concept của target | "cấu trúc silo là gì" |
| Info → Commercial | Modifier so sánh/lựa chọn | "so sánh dịch vụ SEO", "top công cụ audit" |
| Commercial → Transactional | Action verb | "mua", "đăng ký tư vấn", "nhận báo giá" |

⚠️ **Khi 2 luật kéo 2 hướng** (anchor = seed query của target §2 vs modifier theo layer): **ưu tiên seed query** — target Commercial thường đã mang commercial intent ngay trong seed query; chỉ thêm modifier khi seed query chưa thể hiện intent đích.

**Anti-patterns (từ §Intent Funnel):**
- ❌ Anchor generic "xem tại đây" / "click here" — không mang intent signal.
- ❌ Info → Transactional trực tiếp — intent jump → bounce; phải qua Commercial nurturing layer.
- ❌ Anchor action verb cho target Info page (mismatch intent destination).
- ❌ Reverse link (Transactional → Info) trong main content — chỉ được ở breadcrumb/widget.

## 7. Decision nhanh: Link hay No-link (Link-less Connection — GTV)

2 page cùng site share entities + context → Contextual Vector tự connect, không cần force link.

🔴 **Phạm vi gate:** gate "đủ cả 4" dưới đây CHỈ áp cho **link tùy nghi / cross-context**. Link cấu trúc bắt buộc theo `sop/03` (pillar ↔ cluster bidirectional; bài mới → pillar + sibling có ngữ cảnh chung; pillar link ngược lại) **MIỄN gate** — không đem 4 điều kiện này ra chặn link cấu trúc.

**CHỈ link (tùy nghi) khi đủ cả 4:** user journey rõ · anchor có natural lead-in · target là quality/conversion node cần PageRank · vị trí post-answer hoặc Supplementary.

**Để no-link khi có ≥1:** không có lead-in tự nhiên · distance đã min · link phá reading flow · contextual vector đã đủ.

⚠️ Quantifier "đủ cả 4" / "≥1" là **convention của skill** — wiki [[Internal Linking Rules and Strategy]] §Contextual Connection & Link-less Connection chỉ liệt kê 4 điều kiện mỗi chiều, không quy định số lượng.

→ Ghi vào plan dạng `no-link, rely on contextual vector` — đây là output hợp lệ, không phải thiếu sót.
