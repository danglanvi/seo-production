---
client: "{{CLIENT}}"
cong_doan: 10
ws: 05-content-plan
pic: "{{PIC}}"
status: draft
version: v1
---

# {{CLIENT}} — Topical Map + SCN

> Checklist QC: `02-raw/knowledge/sop/01-topical-map.md` (DoD 15 mục). Skill: `skills/topical-map-creation`.
> Input: 9 câu client discovery (Business/Audience/Competition) + gap-analysis.md + GSC/Ahrefs access.
> Naming: `{{CLIENT}}_topical-map_v{{N}}.md`. Delivery target: 5-10 ngày làm việc theo niche size.

## 1. Nền tảng semantic

| Trường | Giá trị |
|---|---|
| Source Context | {{1 câu định nghĩa}} |
| Central Entity | {{...}} — Wikipedia-verified: {{link}} — {{single \| type \| multiple}} |
| Central Search Intent | {{Source Context × Central Entity + predicate expansion}} |
| Buyer Personas | {{2-3 persona — link `00-client-context/marketing-foundation.md`}} |

## 2. Core Section

Main attribute + ≥3 derived attributes. URL Core flat.

| Attribute | Loại (main/derived) | Node/URL dự kiến |
|---|---|---|
| {{...}} | main | {{...}} |
| {{...}} | derived | {{...}} |

## 3. Outer Section

Minor attributes. Luật: mọi Outer node internal link về Core — signals flow to Core.

| Attribute | Contextual domain | Node/URL dự kiến | Link về Core node |
|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} |

## 4. Semantic Content Network (SCN)

| Thành phần | Yêu cầu | Danh sách |
|---|---|---|
| Quality Nodes | ≥3, link từ homepage, ưu tiên speed (TTFB <2s) | {{...}} |
| Trending Nodes | ≥2, nối vào Core Section | {{...}} |
| Internal link map | Sơ đồ Core ↔ Outer, signals flow về Core | {{link file/graph}} |

## 5. Bảng Processed Topical Map

Golden Rule: ONE Macro Context per page. L0 (Answer-First) mandatory mọi H2/H3 khi brief.

| # | Topic | Section | Node type | Title | H1 | URL slug | Meta description | Image URL/Alt | Tháng publish |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {{...}} | {{Core/Outer}} | {{quality/trending/standard}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

## 6. Publication strategy

1. Momentum mandatory — không Momentum, không Topical Authority.
2. Patternless + 5-phase: bulk 20-30 → weekly rhythm → 3-5/ngày scale-up → full coverage → Config.
3. Publishing order matters: ghi rõ thứ tự trong calendar.
4. Benchmark momentum đối thủ: {{số bài/tháng của đối thủ mạnh nhất}}.

## Done-criteria (DoD 15 mục — sop/01)

- [ ] 2-3 Buyer Personas documented với goals + challenges + search behavior.
- [ ] Source Context + Central Entity (Wikipedia-verified) + Central Search Intent locked.
- [ ] Core Section với main attribute + ≥3 derived attributes.
- [ ] Outer Section với minor attributes + internal link plan về Core.
- [ ] Deep research artifacts: Ontology diagram + Lexical Semantics table (10 relations × ≥5 items) + Query Semantics patterns.
- [ ] Token Insertion queries ≥500 raw → filter RPP ≥50 final topics.
- [ ] Topic groups đã cluster theo SERP similarity.
- [ ] V-D-M assessment matrix — 2/3 mandatory, Momentum mandatory.
- [ ] Raw TM → Processed TM: đủ Title + URL + Meta + Image URL + Alt per page.
- [ ] ≥3 Quality Nodes + ≥2 Trending Nodes identified.
- [ ] Core ↔ Outer internal link map — signals flow về Core.
- [ ] Publication calendar (5-phase) + competitor momentum benchmark.
- [ ] Document Design Template per page type.
- [ ] Content Briefs top 20 pages (L0 mandatory + E-A-V).
- [ ] GEO audit: Gate #1 Title/Meta + Gate #2 Speed <2s + Gate #3 Chunk/L0 PASS cho Quality Nodes.
