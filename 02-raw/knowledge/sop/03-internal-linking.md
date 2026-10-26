---
type: sop
status: stub
last_updated: 2026-04-20
related:
  - "[[Internal Linking Rules and Strategy]]"
  - "[[Contextual Bridge]]"
  - "[[Contextual Flow]]"
  - "[[Contextual Border]]"
---

> Bản đóng gói cho SEO Production — sync từ `SEO wiki nội bộ «Semantic» (ngoài repo) SEO A - Z/sop/03-internal-linking.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# SOP 03 — Internal Linking

## Nguyên tắc (Koray)
- Link dựa trên **contextual relevance**, không dựa trên anchor keyword.
- Mỗi cluster có **boundary** (Contextual Border) — link out khỏi boundary chỉ qua **Contextual Bridge**.
- Pillar ↔ cluster pages: bidirectional.
- Cluster ↔ cluster: chỉ qua bridge page.

## Checklist khi publish bài mới
1. Bài link TỚI pillar của cluster (≥1 link).
2. Bài link TỚI sibling cùng cluster khi đoạn có ngữ cảnh chung (Rule 59). Số link theo entity và ngữ cảnh, không quota.
3. Pillar page đã được update để link NGƯỢC lại bài mới.
4. Nếu bài là bridge → link sang cluster đích với anchor contextual.
5. Anchor text: descriptive, không keyword-stuff, khớp với intent destination page.

## Audit định kỳ (tháng)
- Orphan pages trong cluster → cần inbound link từ pillar.
- Over-linked pillar (quá 50 inbound từ cùng cluster) → consider sub-pillar.
- Cross-cluster links không qua bridge → fix (hoặc tạo bridge).

## Tools
- Ahrefs Site Audit → Internal links section.
- Screaming Frog → list all internal links.
- Obsidian graph view (cho wiki này).
