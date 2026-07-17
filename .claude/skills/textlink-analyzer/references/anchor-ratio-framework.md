# Anchor Ratio Framework — Canonical (07/2026)

> **Bản canonical duy nhất** cho anchor text của bộ skill backlink (`backlink-plan`, `textlink-analyzer` trỏ về đây — không tự khai bảng riêng). Nguồn: mô hình 3 giai đoạn Vincent 07/2026 + case vận hành GTV (Rạng Đông Mall) + bài public [[sources/anchor-text-guide-gtv]] + research 07/2026 ([[sources/research-2026-07-backlink-methods]]).
>
> **Sync rule (07/2026):** file này tồn tại 2 nơi — `backlink-plan/references/` (canonical) và `textlink-analyzer/references/` (bundled để skill standalone). **Sửa 1 nơi → sync nơi kia ngay** (md5 phải khớp).

> 🔴 **Guardrail chính sách (2026-07-13):** Mọi ratio trong file này = `internal_benchmark` — heuristic giám sát footprint, KHÔNG phải safe harbor hay compliance guarantee. Theo [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies): mua/bán link pass ranking credit = link spam trừ khi link được qualify `rel="sponsored"`/`rel="nofollow"`; Google không dùng bất kỳ anchor ratio nào làm chuẩn hợp lệ, và anchor mix không làm paid placement thành hợp lệ. Nhãn "Nhóm AN TOÀN" dưới đây = nhóm anchor **không mang keyword** (giảm footprint over-optimization), không hàm ý "an toàn với Google". Tách bạch khi tư vấn: earned editorial/digital PR (compliant) vs paid/manipulative (textlink, guest post trả phí, tiered — risk-managed, có rủi ro neutralization/manual action).

## Thứ tự áp dụng (4 lớp)

```
Lớp 1 — GIAI ĐOẠN TRUST của site  → chốt tổng phân bổ AN TOÀN vs TỪ KHÓA
Lớp 2 — SERP consensus            → tinh chỉnh theo "Mimic the winners"
Lớp 3 — GTV prior per page type   → phân bổ chi tiết 8 loại trong từng nhóm
Lớp 4 — Authority-Aggression      → anchor nào đặt ở nguồn nào
```

## Nguyên tắc 0 — Mô hình 3 giai đoạn trust (Vincent, 07/2026) ⭐ LỚP QUYẾT ĐỊNH TRƯỚC TIÊN

Định nghĩa 2 nhóm:
- **Nhóm AN TOÀN**: Brand thuần · Naked/URL · Generic · Image (alt) — không mang keyword chủ đích.
- **Nhóm TỪ KHÓA (+biến thể)**: Exact · Partial · LSI/Đồng nghĩa · Brand+KW · Niche/lĩnh vực · Long-tail · Title anchor.

| Giai đoạn | Nhận diện site | Nhóm AN TOÀN | Nhóm TỪ KHÓA |
|---|---|---|---|
| **1. Đầu** | backlinks còn ít, DR thấp, trust thấp | **~70%** | ~30% |
| **2. Ổn định** | nền backlink + ranking đã ổn | 40-50% | **50-60%** |
| **3. Có trust** | domain đã được tin cậy | 35-45% | **55-65%** (từ khóa + biến thể) |

- **Trần Exact ≤8-10% giữ nguyên MỌI giai đoạn** — phần "từ khóa" tăng theo giai đoạn bằng Partial/LSI/Brand+KW/Long, KHÔNG bằng Exact.
- Bảng public gtvseo.com/anchor-text/ (Brand & Naked ~70%) ≈ guidance giai đoạn 1; mô hình 3 giai đoạn là bản tinh, dùng bản này.
- Xác định giai đoạn từ data `backlink-research` §1 (RD, rank, spam, tuổi profile) — nghi ngờ giữa 2 giai đoạn → chọn giai đoạn thấp hơn (an toàn hơn).

## Nguyên tắc 1 — SERP consensus tinh chỉnh, ratio là prior

Mọi nguồn active 2025-2026 (Floate, Diggity, FatJoe, Ahrefs) đồng thuận: **không có universal ratio**. Quy trình đúng:

1. Pull anchor profile của **top 5-10 SERP** cho keyword target (`backlink-research` §4 — DataForSEO `anchors/live`).
2. Phân loại 8 nhóm → tính consensus ("top 5 đang 60% brand-family / 4% exact").
3. **Mimic the winners**: lệch consensus mới là vấn đề — "If top 5 are 80% branded and you're at 40%? Spam. If they're 50/50 and you're 95% branded? Weak." (Floate, X 09/2025).
4. Không có data consensus → dùng **GTV prior** bên dưới.

## Nguyên tắc 2 — GTV prior theo page type (fallback đã kiểm chứng vận hành)

> Bảng dưới là phân bổ chi tiết 8 loại — tổng nhóm của nó (AN TOÀN ~51% / TỪ KHÓA ~49%) tương ứng **giai đoạn 2**. Ở giai đoạn 1: co nhóm từ khóa về ~30% (ưu tiên giữ Partial + Brand+KW, Exact ≈ 0-3%); giai đoạn 3: nới nhóm từ khóa lên 55-65% bằng Partial/LSI/biến thể.

| Anchor Type | Homepage | Category/Money page | Ghi chú |
|---|---|---|---|
| Brand thuần | ~23% | ~10% | "Rạng Đông Mall" |
| Khớp một phần (Partial) | ~23% | ~25% | workhorse |
| Link trần (Naked/URL Full) | ~17% | ~15% | domain.com / https://… |
| Brand + Keyword (Compound) | ~14% | ~20% | "đèn led panel rạng đông" — Floate: "most underrated" |
| Chính xác (Exact) | **≤8%** | **≤10%** | TRẦN CỨNG; Floate cap <5% monthly placements — chọn ngưỡng thấp hơn khi nghi ngờ |
| Chung chung (Generic) | ~8% | ~7% | "xem thêm", "tại đây" + mô tả trước/sau |
| Anchor đồng nghĩa (Semantic) | ~4% | ~8% | synonym của keyword |
| Title anchor | ~3% | ~5% | title bài đích — ưu tiên cho link vào supporting content |

Đối chiếu ngành: prior này nằm trong vùng an toàn mọi nguồn đã publish (gần LinkBuilder.io inner-page 30/20/20/10/10/5/5 nhất; HOTH homepage 80-95% brand-family; Ahrefs guidance exact 1-5%).

## Nguyên tắc 3 — Authority-Aggression Scale (Floate 02/2026 ≡ rule Vincent 2021)

Phân bổ anchor theo **sức nguồn**, không rải đều:

| DR nguồn / chất lượng | Anchor được phép |
|---|---|
| **<DR40** / nguồn yếu / bài không chủ đích | CHỈ branded · generic · naked (≡ Vincent 2021: "nguồn yếu → link trần/brand/xem thêm") |
| DR40-60 đúng theme | + partial · brand+KW · title |
| DR60-85+ editorial đúng theme, Title+URL có keyword | + exact (đây là chỗ DUY NHẤT đặt exact) |

## Nguyên tắc 4 — Footprint rules

- **Không lặp anchor non-brand trong cùng tháng** trên cùng chiến dịch ("Repetition kills" — Floate); textlink số lớn: không lặp 1 anchor y hệt quá ~10 lần/đợt/domain.
- **Anchor map 20-30 variations per target page**, rotate.
- Anchor 3 phần "Mô tả trước + Từ khóa + Mô tả sau" (format sheet GTV) — tự nhiên hóa, generic anchor luôn kèm ngữ cảnh.
- Keyword exact/partial phải **tồn tại trong content trang đích**; lowercase cho non-brand; surrounding text relevant.
- Image anchor (alt) hợp lệ và nên có (Floate: 5-25% profile; alt <125 chars, keyword đầu).

## Nguyên tắc 4b — Xuất hiện đồng thời (co-occurrence — bắt buộc mọi loại anchor)

Từ khóa mục tiêu/liên quan phải xuất hiện **GẦN anchor** trong bài nguồn (câu chứa anchor + lân cận): "sự liên quan của bài viết với Anchor Text càng cao, sức mạnh backlink càng mạnh, giảm phụ thuộc exact" ([[sources/anchor-text-guide-gtv]]). Generic anchor ("tại đây") không có ngữ cảnh quanh = link gần vô dụng. Đây là lý do format 3 phần "Mô tả trước + Từ khóa + Mô tả sau" tồn tại.

## Nguyên tắc 5 — Chẩn đoán & sửa

- Audit: so anchor profile mình vs 3-5 đối thủ (`backlink-research` §4). Red flag: "top 3 đều ~3% exact, mình 15%".
- Over-optimized → **dilute bằng branded/generic/naked pillow wave** (không disavow trừ khi negative impact rõ).
- Review theo quý cùng lint.
