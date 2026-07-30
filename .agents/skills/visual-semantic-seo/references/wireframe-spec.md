# Wireframe Spec — "PAGE LAYOUT SEMANTICS" format (v3.7)

> Spec cho Wireframe Mode (BUILD / ANALYZE / COMPARE). Format chuẩn theo 7 wireframe mẫu tại `SEO Knowledge/Semantic SEO A - Z/raw/assets/local-seo-sel-2026/` (page-layout-semantic*.png/webp) — Vincent duyệt làm target format 24/07/2026. Output = 1 file HTML tự chứa (inline CSS, không external font/img) hoặc render PNG.

## Anatomy — 3 cột + legend

```
┌────────────────────────────────────────────────────────────────────┐
│ PAGE LAYOUT SEMANTICS - {PAGE NAME}            ← title, UPPERCASE  │
│ {1 dòng subtitle: các cơ chế chính của trang}                      │
│                                                                    │
│ [parent node]  [transactional child node]   ← context nodes (dashed│
│        │              │                       boxes, trên canvas)  │
│ ┌─────────┐  ┌─────────────────────┐  ┌──────────────────────────┐ │
│ │ RAIL    │  │ PAGE BLOCKS (giữa)  │  │ CALLOUTS (phải)          │ │
│ │ TRÁI    │  │ block 1  ───────(1)─┼──│ (1) TÊN CƠ CHẾ           │ │
│ │ MACRO   │  │ block 2  ───────(2)─┼──│  giải thích 2-4 dòng     │ │
│ │ CONTEXT │  │ …                   │  │ (2) …                    │ │
│ │ ─ ─ ─ ─ │  │                     │  │                          │ │
│ │ MICRO   │  │                     │  │                          │ │
│ │ CONTEXTS│  │                     │  │                          │ │
│ │ ─ ─ ─ ─ │  │                     │  │                          │ │
│ │ CONTEXT │  │                     │  │                          │ │
│ │ CLOSURE │  │                     │  │                          │ │
│ └─────────┘  └─────────────────────┘  └──────────────────────────┘ │
│ ┌ LEGEND ─────────────────────────────────────────────────────────┐│
│ │ ■ Macro Context: …   ■ Transaction/Closure: …                   ││
│ │ ■ Micro Contexts: …  ■ Neutral: …   ■ Evidence: …               ││
│ │ (dòng cuối: "All names … are illustrative example content")     ││
│ └─────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
```

- **Rail trái**: 2-3 hộp dashed dọc — MACRO CONTEXT / MICRO CONTEXTS / CONTEXT CLOSURE — mỗi hộp 1 dòng mô tả vai trò ("Central entity and central search intent declared and proven before first scroll depth"). Rail ôm đúng dải block nó phủ.
- **Cột giữa**: block page theo DOM order = visual order, mỗi block có: eyebrow label (UPPERCASE, letter-spacing) + nội dung minh họa + số callout ở góc. Component thật vẽ thật: tab row, accordion (+/−), form field + button, card grid, calendar matrix, map pin, carousel.
- **Cột phải**: callout cards đánh số tròn khớp block, nối bằng đường dashed. Title = TÊN CƠ CHẾ SEMANTIC (không phải tên UI): "CENTRALITY AND PROMINENCE", "NAP CONSISTENCY = GBP CONSENSUS", "SEASONALITY EAV MATRIX". Body 2-4 dòng: block phục vụ augmented queries nào, cơ chế gì.
- **Context nodes trên đầu** (khi trang thuộc topical map): PARENT NODE / TRANSACTIONAL CHILD NODE / SIBLING NODES / EXTERNAL NODE (GBP) — hộp dashed, nối mũi tên.

## Palette cố định (đừng đổi giữa các wireframe)

| Zone | Border/accent | Dùng cho |
|---|---|---|
| Nền canvas | `#0d1117` (near-black), text `#e6edf3` | toàn trang |
| **Macro Context** | teal `#2dd4bf` | H1, definitional block, hero, NAP, tool definition |
| **Micro Contexts** | vàng `#facc15` | attribute expansion, card grids, tabs, taxonomy, EAV matrix |
| **Transaction / Closure** | tím `#a78bfa` | CTA bands, form, FAQ closure, UGC, booking |
| **Evidence** | vàng nhạt `#fde68a` | accreditation strips, review consensus, certification |
| **Neutral** | xám `#6b7280` | nav, breadcrumb, parent hub nodes |
| Callout number chip | nền = màu zone tương ứng, chữ đen | |

Block = nền tối hơn zone màu 1 bậc + border 1.5px màu zone + border-radius 8-10px. Đường nối callout: dashed 1px màu zone, opacity 0.6.

## Quy ước nội dung

1. **Placeholder hóa tên thật**: `{Brand}`, `{Rehab Name}`, `{Doctor Name}`, `Dr. A. Example` — trừ khi user yêu cầu đích danh. Footer legend luôn có "All names, reviews and snippets shown are illustrative example content".
2. **Text minh họa phải ĐÚNG cơ chế**: H1 viết đúng H1 đề xuất; definitional sentence viết subject-first thật ("{Rehab Name} is a luxury rehab centre in {City}, Thailand…"); đừng lorem.
3. **≤12 block + ≤12 callout / wireframe** — quá thì tách trang 2 hoặc gộp callout (9-10 chung 1 card).
4. **Mỗi callout nói VÌ SAO, không tả lại UI**: "Accordion order mirrors the real treatment sequence — the order carries information; it is not decorative."
5. Responsive không cần — wireframe là artifact đọc desktop; width cố định ~1400-2000px.

## Mode COMPARE — diff matrix

Format theo mẫu `image-321` ("2 Store Pages, 2 Local Entity Models"):

- Header: title + subtitle nêu 2 business model.
- 2 cột page A (accent xanh) / page B (accent tím) + cột DIFF phải.
- Mỗi hàng = 1 dimension: HUB ARCHITECTURE / H1 NAMING / SPATIAL PROOF / NAP + HOURS / COMMERCE FUSION / FRANCHISE LINK GRAPH / REVIEW LAYER / CONVERSION MODES (chọn dimension theo page type).
- Verdict per hàng: **A≠B** (cam — chiến lược khác nhau có chủ đích) · **A=B** (xanh lá — shared skeleton) · **A!** / **B!** (đỏ — chỉ 1 bên có).
- Cuối: **CONVERGENCE VERDICT** (hộp teal) — 2-4 câu: phần skeleton chung là gì, khác biệt đi theo business model hay theo taste, bài học.

## HTML skeleton (copy làm starting point)

```html
<style>
  .wf{background:#0d1117;color:#e6edf3;font:14px/1.5 ui-sans-serif,system-ui;padding:40px;max-width:2000px}
  .wf h1{font-size:34px;letter-spacing:.5px;margin:0 0 6px;text-transform:uppercase}
  .wf .sub{color:#9ca3af;margin-bottom:28px}
  .wf .grid{display:grid;grid-template-columns:190px minmax(560px,1fr) 480px;gap:28px;align-items:start}
  .rail{border:2px dashed;border-radius:10px;padding:18px 12px;text-align:center;position:sticky;top:20px}
  .rail h2{font-size:17px;margin:0 0 8px;letter-spacing:1px}
  .rail p{font-size:12px;color:#9ca3af}
  .macro{border-color:#2dd4bf;color:#2dd4bf}.micro{border-color:#facc15;color:#facc15}.closure{border-color:#a78bfa;color:#a78bfa}
  .blk{border:1.5px solid;border-radius:10px;padding:14px 16px;margin-bottom:14px;position:relative;background:#111827}
  .blk .eyebrow{font-size:11px;letter-spacing:2px;text-transform:uppercase;opacity:.75;margin-bottom:6px}
  .blk .num,.co .num{position:absolute;top:10px;right:10px;width:22px;height:22px;border-radius:50%;color:#0d1117;font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center}
  .z-macro{border-color:#2dd4bf}.z-macro .num{background:#2dd4bf}
  .z-micro{border-color:#facc15}.z-micro .num{background:#facc15}
  .z-clo{border-color:#a78bfa}.z-clo .num{background:#a78bfa}
  .z-evi{border-color:#fde68a}.z-evi .num{background:#fde68a}
  .z-neu{border-color:#6b7280}.z-neu .num{background:#6b7280;color:#fff}
  .co{border:1.5px solid;border-radius:10px;padding:12px 14px 12px 40px;margin-bottom:12px;position:relative}
  .co .num{left:10px;right:auto}
  .co h3{font-size:13px;letter-spacing:1px;text-transform:uppercase;margin:0 0 4px}
  .co p{font-size:12.5px;color:#cbd5e1;margin:0}
  .legend{border:1px solid #374151;border-radius:10px;padding:16px 20px;margin-top:24px;font-size:12.5px}
  .legend .sw{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:-1px}
</style>
<div class="wf">
  <h1>Page Layout Semantics — {Page Name}</h1>
  <div class="sub">{subtitle: cơ chế chính}</div>
  <div class="grid">
    <div><div class="rail macro"><h2>Macro Context</h2><p>{vai trò}</p></div></div>
    <div><!-- blocks: <div class="blk z-macro"><div class="eyebrow">H1 - …</div>…<span class="num">2</span></div> --></div>
    <div><!-- callouts: <div class="co z-macro"><span class="num">2</span><h3>{Cơ chế}</h3><p>{vì sao}</p></div> --></div>
  </div>
  <div class="legend"><b>LEGEND</b><br>
    <span class="sw" style="background:#2dd4bf"></span>Macro Context: … &nbsp;
    <span class="sw" style="background:#facc15"></span>Micro Contexts: … &nbsp;
    <span class="sw" style="background:#a78bfa"></span>Transaction/Closure: … &nbsp;
    <span class="sw" style="background:#6b7280"></span>Neutral: …<br>
    <i style="color:#6b7280">All names, reviews and snippets shown are illustrative example content</i>
  </div>
</div>
```

(Rail micro/closure đặt bằng cách lặp `.rail` trong cột trái ở vị trí dọc tương ứng — hoặc dùng nhiều `.grid` section liên tiếp, mỗi section 1 rail.)

## Checklist trước khi trả wireframe

- [ ] Mỗi block có số callout + callout tương ứng tồn tại (không số mồ côi).
- [ ] Zone màu khớp legend; legend liệt kê đúng các zone CÓ trên trang.
- [ ] DOM order của block = thứ tự đọc thật của trang đề xuất.
- [ ] Callout giải thích cơ chế semantic (queries phục vụ / triples / patent-leak khi có), không tả UI.
- [ ] Placeholder hóa tên; footer "illustrative example content".
- [ ] ANALYZE mode: có mục GAP cuối (block thiếu / query chưa có component / function giả).
