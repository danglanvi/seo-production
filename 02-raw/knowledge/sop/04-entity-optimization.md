---
type: sop
status: stub
last_updated: 2026-04-20
related:
  - "[[Entity]]"
  - "[[Entity Home]]"
  - "[[EAV]]"
  - "[[Authorship]]"
---

> Bản đóng gói cho SEO Production — sync từ `SEO wiki nội bộ «Semantic» (ngoài repo) SEO A - Z/sop/04-entity-optimization.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# SOP 04 — Entity Optimization

## Mục tiêu
Đảm bảo website trở thành **Entity Home** cho Central Entity, được Google recognize qua KELM/entity extraction.

## Checklist

### On-site
- [ ] Schema.org markup đúng type cho Central Entity (Organization / Person / Product / Place).
- [ ] About page / Entity home page tồn tại, có URL canonical.
- [ ] SameAs link tới Wikipedia / Wikidata / social profiles chính thức.
- [ ] Author bio với `Person` schema + sameAs.
- [ ] Consistent NAP (Name / Address / Phone nếu applicable).

### Off-site
- [ ] Mentioned trên Wikipedia (nếu notability đủ) hoặc Wikidata.
- [ ] Citations từ authoritative sources trong niche.
- [ ] Author có footprint trên các site uy tín.

### EAV (Entity-Attribute-Value)
Với mỗi Central Entity, đảm bảo các attribute sau có answer rõ trên site:
- Identity (tên đầy đủ, alias)
- Type / category
- Key attributes (ngành, sản phẩm, founded, v.v.)
- Relations (sibling entities, competitors)
- Authority signals (certification, awards, published work)

### Responsiveness (REALM)
- Mỗi attribute → có **long-form definitive answer** trên site.
- Không nước đôi, không conflicting statement giữa các page.

## Verification
- Google Knowledge Panel xuất hiện? (có thể mất 3-6 tháng).
- Brand mention trong Google SERP cho các query liên quan.
- Ahrefs → brand mention tracking.
