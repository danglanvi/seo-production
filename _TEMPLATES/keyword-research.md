---
client: "{{CLIENT}}"
cong_doan: 4
ws: 05-content-plan
folder: 05-content-plan/keyword-research/
pic: "{{SEO Lead Project}}"
status: draft
version: v1
---

# {{CLIENT}} — Keyword research — {{PHẠM VI: bộ cam kết | mở rộng topic X | refresh T6}}

> Naming: `{{CLIENT}}_keyword-research-{{pham-vi}}_v{{N}}.md` → `05-content-plan/keyword-research/`. Data export gốc (Ahrefs/GSC/SpySERP CSV) bất biến vào `02-raw/seo-data/keywords/<ngày>_<nguồn>_<mô tả>.csv`, file này chỉ ghi kết luận + link. Phương pháp: `02-raw/knowledge/cheat-sheets/keyword-research-methods.md`. Bước sau: `keyword-topic-url-mapping` → `_TEMPLATES/topical-map.md`.

## 1. Đầu vào

| Trường | Giá trị |
|---|---|
| Keyword cam kết / seed | {{link `00-client-context/kpi-commitments.md` hoặc danh sách}} |
| Central Entity · Source Context · persona | {{...}} |
| Đối thủ dùng research (3–6) | {{domain — lý do chọn; bỏ brand lớn rank nhờ uy tín}} |
| Nguồn data + ngày export | {{Ahrefs KE/Site Explorer dd/mm · GSC 16 tháng dd/mm · SpySERP · Google Suggest/PAA}} |

## 2. Phương pháp đã dùng (tick + ghi output)

| # | Phương pháp | Dùng? | Output (file trong 02-raw/seo-data/keywords/) |
|---|---|---|---|
| M1 | Seed → phrase match / having same terms / suggest / PAA (mở rộng) | ☐ | {{...}} |
| M2 | Organic keywords + Top pages đối thủ → pivot theo URL (URL = proxy topic) | ☐ | {{...}} |
| M3 | Content gap ≥3 đối thủ (topical gap) | ☐ | {{...}} |
| M4 | GSC query mining: query có impression, vị trí ngoài top 10, chưa có trong bài | ☐ | {{...}} |
| M5 | SERP overlap clustering (`serp-clustering`): ~4/10 kết quả trùng = cùng topic | ☐ | {{...}} |
| M6 | Internal link + `site:` đối thủ top 1–3 → cụm bổ trợ | ☐ | {{...}} |
| M7 | Entity/attribute từ Wikipedia + NLP (E-A-V coverage) | ☐ | {{...}} |
| M8 | Phantom keyword gate: `allintitle:` <1.000 tốt / <5.000 chấp nhận / <500 site mới | ☐ | {{...}} |
| M9 | Intent bằng SERP thật (tab ẩn danh) — không đoán từ mặt chữ | ☐ | {{...}} |

## 3. Kết quả — cluster

| Cluster / topic | Keyword đại diện | # kw | Volume tổng | Intent (SERP) | Page type | Đối thủ mạnh nhất | Phantom/KD ghi chú | Ưu tiên |
|---|---|---|---|---|---|---|---|---|
| {{...}} | {{...}} | {{n}} | {{v}} | {{info/comm/trans/nav}} | {{cate/product/blog/service}} | {{domain}} | {{allintitle n}} | {{P1/P2/P3}} |

Tổng: {{N}} cluster · {{n}} keyword · {{v}} volume. Keyword cam kết chưa vào cluster nào: {{liệt kê hoặc "không"}}.

## 4. Quyết định

- Cluster đưa vào topical map đợt này: {{...}} — lý do (cam kết · dễ · chuyển đổi · traffic).
- Cluster để sau / bỏ: {{...}} — lý do.
- Keyword hợp đồng gộp/tách theo SERP overlap: {{cặp nào gộp, cặp nào tách}}.
- Rủi ro: {{cannibalization với URL đang có · thị trường brand lớn · volume tool không tin cậy (VN)}}.

## 5. Bàn giao

- → #4 `keyword-topic-url-mapping`: bảng mục 3 là input. → #10 topical map. → `05-content-plan/content-tracking/` khi có bài.
- Ngày chốt · người duyệt: {{SEO Lead Project / Content Leader}}.

## Done-criteria

- [ ] Mọi keyword cam kết nằm trong ≥1 cluster hoặc có lý do loại.
- [ ] Cluster chốt bằng SERP overlap (M5/M9), không chỉ tool grouping.
- [ ] Data export gốc lưu `02-raw/seo-data/keywords/` với ngày + nguồn; file này chỉ link.
- [ ] Intent từng cluster có bằng chứng SERP; page type đề xuất khớp intent.
- [ ] Phantom gate ghi cho cluster P1.
