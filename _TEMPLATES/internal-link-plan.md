---
template: internal-link-plan
ws: 06-onpage-internal-link
cong_doan: 18
checklist: 02-raw/knowledge/sop/03-internal-linking.md
skill: internal-linking
data_path: "{{A-AHREFS | B-SCREAMING-FROG | C-TOPICAL-MAP}}"
client: "{{CLIENT}}"
status: draft
date: "{{YYYY-MM-DD}}"
---

# Internal Link Plan — {{CLIENT}}

> Checklist gốc: `02-raw/knowledge/sop/03-internal-linking.md` + skill `internal-linking` (canonical owner luật execution).
> Khi instantiate: lưu thành `06-onpage-internal-link/{{CLIENT}}_internal-link-plan_v1.md`.

## 1. Scope & data source

| Trường | Giá trị |
|---|---|
| Scope | {{TOAN_SITE | CLUSTER}} |
| Data path | A = Ahrefs MCP (caveat: crawl Ahrefs, độ phủ có thể thấp hơn Screaming Frog) · B = Screaming Frog `all_inlinks.csv` · C = chỉ topical map — plan lý thuyết, mọi anchor là candidate, flag `verify-anchor` |
| Nguồn data | {{FILE_HOAC_CALL}} — ngày lấy: {{NGAY}} |

## 2. Nguyên tắc (đánh số — vi phạm = FAIL khi QC)

1. Link theo **contextual relevance**, không theo anchor keyword.
2. Cluster có **Contextual Border**; cluster ↔ cluster CHỈ qua **Contextual Bridge**. Pillar ↔ cluster: bidirectional.
3. **Signals flow TO Core**: Outer→Core, Trending→Core, Home→Quality→Core — link flow target = trang quan trọng hơn.
4. Anchor = **seed query của target page**; ≤3 lần cho 1 anchor text; có semantic lead-in ở đoạn trước; pass **6/6 Anchor Text Rules**.
5. Max 1 link per heading section (ngoại lệ list entities cùng type → flag `list-exception`); khoảng cách 2 link ≥1 heading trong Main Content. Không quota số link mỗi bài.
6. **Rule 59** — chọn target theo semantic distance (shared process/attributes), không chỉ gần bề mặt topical.
7. **Rule 60** — mỗi outbound link cách source tối đa 1 semantic step; link xa hơn → chèn annotation text giải thích bridge.
8. **Link-less Connection**: contextual vector đã đủ / không có lead-in tự nhiên / link phá reading flow → ghi `no-link, rely on contextual vector`, không ép link.
9. First link + first anchor trong Main Content của page quan trọng phải trỏ đúng target quan trọng nhất.

## 3. Orphan list (0 inbound internal link từ main content)

| URL | Cluster | Fix (inbound từ pillar/sibling) | Owner | Deadline | Status |
|---|---|---|---|---|---|
| {{URL}} | {{CLUSTER}} | {{FIX}} | {{OWNER}} | {{NGAY}} | ☐ |

## 4. Bridge plan (cross-cluster)

Cross-cluster link không qua bridge phát hiện khi audit → fix hoặc tạo bridge, liệt kê tại đây.

| Cluster nguồn | Cluster đích | Bridge page | Anchor (contextual) | Status |
|---|---|---|---|---|
| {{CLUSTER_A}} | {{CLUSTER_B}} | {{BRIDGE_URL}} | {{ANCHOR}} | ☐ |

## 5. Anchor plan per target

| Source URL | Target URL | Anchor | Vị trí (sau section nào) | 6/6 rules | Flag |
|---|---|---|---|---|---|
| {{SOURCE}} | {{TARGET}} | {{ANCHOR}} | {{VI_TRI}} | ☐ | {{verify-anchor | list-exception | no-link | —}} |

## 6. Flow-to-core check

| Core / target page | Inbound từ Outer (số link) | First anchor main content đúng target? | Ghi chú |
|---|---|---|---|
| {{CORE_URL}} | {{N}} | ☐ | {{GHI_CHU}} |

## 7. Lịch cuốn chiếu (theo sau content + onpage 15-30 ngày)

| Cụm content | Content + onpage xong | Cửa sổ IL | Status |
|---|---|---|---|
| Cụm URL SEO | Hết T4 | T4 → 15 ngày đầu T5 (mốc cứng) | ☐ |
| {{CUM_KHAC}} | {{NGAY}} | Cuốn chiếu T5 → T9 theo timeline từng loại content | ☐ |

## 8. Done-criteria

- [ ] Orphan sau thực thi = 0 (mọi dòng mục 3 status done).
- [ ] Cross-cluster link không qua bridge = 0.
- [ ] 100% anchor pass 6/6 rules hoặc có flag rõ (`verify-anchor` / `list-exception` / `no-link`).
- [ ] Flow-to-core check pass cho toàn bộ Core pages.
- [ ] Lịch cuốn chiếu khớp timeline; IL cụm URL SEO chốt ≤15 ngày đầu T5.
- [ ] Cập nhật index.md (công đoạn 18) + log.md op `work`.
