# Link Plan Template — schema output + citation map

Template deliverable của skill `internal-linking`. File output: `<project>_Internal-Link-Plan_v1.md` → tài liệu nội bộ «<project>» (ngoài repo, hỏi Lead/Vincent).

---

## 1. Schema bảng link plan (section 3 của deliverable)

```markdown
| # | Source URL | Target URL | Vị trí gợi ý (section) | Anchor đề xuất | Direction type | Lý do (rule ID) | Flag |
|---|---|---|---|---|---|---|---|
| 1 | /outer/bai-a | /core/dich-vu-x | H2 "…" — paragraph post-answer | "dịch vụ X cho …" | Outer→Core | GR4, AR6, POS-2 | — |
| 2 | /cluster-a/pillar | /cluster-a/bai-moi | Section liên quan cuối pillar | "…" | pillar↔cluster | SOP03-C3 | — |
| 3 | /cluster-a/bai-b | /cluster-b/bai-c | — | — | bridge required | SOP03-N1 | cần tạo/đi qua bridge |
| 4 | /info/bai-d | /commercial/so-sanh-y | Last heading section | "so sánh Y" | funnel-forward | IF-1, AR3 | — |
| 5 | /bai-e | /bai-f | — | — | no-link | LLC (điều kiện 1+4) | no-link candidate |
```

**Giá trị hợp lệ cột `Direction type`:** `Outer→Core` · `pillar↔cluster` · `cluster→pillar` · `bridge` · `funnel-forward` · `home→quality-node` · `trending→core` · `sibling` · `no-link`.

**Giá trị hợp lệ cột `Flag`:** `no-link candidate` · `verify-anchor` (Path C — anchor chưa verify trong target content) · `grouper-exception` (link ở top-10 heading, cần Vincent duyệt) · `annotation-bridge` (cross-domain xa theo Rule 60, cần annotation text) · `sub-pillar?` · `cần tạo bridge`.

**Quy tắc điền:**
- Cột "Vị trí gợi ý" luôn ghi heading section cụ thể + vị trí trong section (post-answer / last paragraph). Không ghi chung chung "trong bài".
- Cột "Lý do" bắt buộc ≥1 rule ID (bảng mục 3) — dòng nào không giải thích được connection thì KHÔNG có trong plan.
- 1 link/target/doc mặc định; dòng multi-link phải ghi lý do riêng (RL-11).

## 2. Section audit findings (section 2 của deliverable)

```markdown
## 2. Audit findings
Data path: <A/B/C> · Data date: <YYYY-MM-DD> · Coverage caveat: <Ahrefs crawl ≠ full crawl / SF crawl date…>

### Orphan pages (convention: 0 inbound internal từ main content — không phải rule có nguồn)
| Page | Cluster | Fix đề xuất |

### Over-linked pillar (>50 inbound TỪ CÙNG CLUSTER — SOP03-A2)
| Pillar | Cluster | Inbound từ cluster | Đề xuất sub-pillar |

### Cross-cluster bypass bridge (SOP03-N1)
| Source | Target | Bridge đề xuất |

### Pages vi phạm <150 links (RL-1) · Mobile-desktop mismatch (RL-1) · First-anchor issues (KV-1) · Link tồn dư sau 301/delete (RSC-1)
(bảng tương ứng, chỉ render mục có finding)

### Summary counts
Orphans: N · Over-linked pillars: N · Bypass bridge: N · ≥150 links: N · Links đề xuất mới: N · Fix: N · No-link: N
```

## 3. Rule ID → citation map (Evidence gate — mỗi dòng plan truy được nguồn)

**Đây là nguồn threshold DUY NHẤT của skill** — mọi con số (150, 50, 3, 1, 2-5, 3-5…) nằm trong cột Nội dung, đúng số + đúng nguồn, không chế thêm. Koray verbatim: *"There is no specific, and optimum internal link count for a specific content piece"* — no magic number (paraphrase).

| Rule ID | Nội dung | Nguồn |
|---|---|---|
| GR4 | Signals flow TO Core (Outer→Core, Trending→Core, Home→Quality→Core) | `sop/01-topical-map.md` §Golden Rules #4 + Bước 20; [[Link Flow]] |
| SOP03-P1 | Pillar ↔ cluster bidirectional; cluster ↔ cluster chỉ qua bridge | `sop/03-internal-linking.md` §Nguyên tắc |
| SOP03-C1..C5 | Checklist bài mới: ≥1 link tới pillar (C1) · 2-5 siblings (C2) · pillar link ngược (C3) · bridge anchor contextual (C4) · anchor descriptive khớp intent (C5) | `sop/03` §Checklist |
| SOP03-A2 | Over-linked pillar: >50 inbound từ cùng cluster → sub-pillar | `sop/03` §Audit định kỳ |
| SOP03-N1 | Cross-cluster không qua bridge → fix hoặc tạo bridge | `sop/03` §Audit định kỳ |
| RL-1 | <150 internal links/page, mobile = desktop | [[Internal Linking Rules and Strategy]] §Core Rules; [[Semantic Content Network]] 14 Rules #4 |
| RL-3 | ≤3 lần/anchor text | §Core Rules |
| RL-4 | Max 1 link per heading section | §Determining Link Count #5 |
| RL-5 | Distance giữa 2 links ≥1 heading (Main Content) | §Core Rules |
| RL-6 | Top-10 headings: 0 link (exception grouper/hypernym) | §Core Rules |
| RL-11 | Multi-link cùng target: link 1 = PageRank + relevance; 2+ = relevance only | §Core Rules |
| KV-1 | First link + first anchor Main Content = heaviest relevance signal | §Core Rules + §In Practice #1 |
| POS-1 | Link most important first; Supplementary → bottom + lower hierarchy | §Core Rules |
| POS-2 | Link post-answer; không first paragraph, không trước definition | §Core Rules |
| POS-3 | Side-topic → chỉ link từ last heading's paragraphs | §Core Rules |
| QN-1 | 3-5 Quality Nodes từ homepage main content (không boilerplate) | §SOP v1; `sop/01` Bước 13 |
| TN-1 | Trending Nodes bắt buộc bridge về Core | §SOP v1; `sop/01` Bước 14 |
| AR1..AR6 | 6 Anchor Text Rules | §6 Anchor Text Rules → [references/anchor-rules.md](anchor-rules.md) §1 |
| R59 | Semantic Distance-Based Internal Linking (3 phương pháp đo) | §GTV Extensions Rule 59 → anchor-rules.md §4 |
| R60 | Knowledge Domain Expansion Path — max 1 semantic step; cross-domain xa → annotation bridge | §GTV Extensions Rule 60 → anchor-rules.md §5 |
| IF-1 | Intent Funnel forward-only Info→Commercial→Transactional, không skip layer | §Intent Funnel → anchor-rules.md §6 |
| LLC | Link-less Connection — 4 điều kiện no-link | §Contextual Connection & Link-less Connection → anchor-rules.md §7 |
| SCN-6 | Sub-section connect về central section của Topical Map (contextual bridge) | [[Semantic Content Network]] 14 Rules #6 |
| SCN-10 | Nesting vs Connecting | [[Semantic Content Network]] 14 Rules #10 |
| RSC-1 | Clean internal links sau delete/301; không link different pages without context | [[Ranking Signal Consolidation]] §Consolidation Methodologies (link without context) + §4 Methods (Bloating Fix) #4 (clean links sau delete/301) |
| MOM-1 | Burst 20-30 bài → fix internal links ngay ("Momentum without linking = wasted") | §SOP v1 Additions |
| PCP-1 | Pillar 5-10k từ · Cluster 1.5-3k từ | [[Pillar Cluster Page]] |

## 4. Ghi chú 3 Path — cột nào có data ở path nào

| Cột / Section | Path A (Ahrefs MCP) | Path B (Screaming Frog) | Path C (topical map only) |
|---|---|---|---|
| Inbound count per page (orphan, >50, ≥150) | ✅ `site-explorer-pages-by-internal-links` — ⚠️ crawl Ahrefs, coverage có thể < full crawl | ✅ all_inlinks đầy đủ nhất | ❌ bỏ audit, ghi chú |
| Anchor hiện trạng (≤3 lần, first anchor) | ✅ `site-explorer-linked-anchors-internal` | ✅ cột anchor trong export | ❌ |
| Vị trí link (content vs boilerplate) | ⚠️ hạn chế | ✅ SF phân biệt content/navigation | ❌ |
| Mobile-desktop parity | ⚠️ verify được một phần | ✅ nếu crawl 2 user-agent | ❌ ghi chú cho implementer |
| Link plan đề xuất + anchor | ✅ | ✅ | ✅ nhưng mọi anchor flag `verify-anchor` |
| No-link candidates | ✅ | ✅ | ✅ (dựa topical map + entity overlap) |

**Path C disclaimer bắt buộc in đầu deliverable:** "Plan lý thuyết từ topical map — chưa audit hiện trạng; mọi anchor là candidate, verify khi content live; vị trí gợi ý theo position rules, implementer tự xác định heading cụ thể."
