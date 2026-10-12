# Schema qp-project/1: file JSON dựng deck

> Nạp ở pha F của skill (viết JSON). Mỗi lần chẩn đoán có một file JSON. `scripts/qp_render.py` dựng file này thành deck 15–17 slide. Không viết HTML tay. Sửa nội dung thì sửa JSON rồi dựng lại.

## 1. Luật nội dung

1. **Mỗi con số có nguồn.** Số tính từ dữ liệu hạng thì tính bằng `qp_ranks.py` hoặc script lưu trong thư mục `_work`. Không ước lượng. Mỗi slide ghi nguồn trong trường `src`: công cụ, project hoặc bộ keyword, engine, ngày.
2. **Đếm hạng theo một engine:** engine ghi trong hợp đồng. Nếu team đang đo bằng engine khác, ghi rõ trong `measure_slide.src` và `flags`.
3. **Độ sâu quét.** Đặt `measure.depth` theo dữ liệu thật (50 hoặc 100). Hạng `null` nghĩa là ngoài độ sâu, không phải hạng 101.
4. **Phát hiện chưa kiểm chéo** thì đặt `"new": true` ở dòng đó và ghi vào `flags`. Viết "giả thuyết", "cần GSC", "chưa xác nhận". Renderer tự tô đỏ câu chứa các cụm này. Muốn tô đỏ chủ động thì bọc bằng `<r>…</r>`.
5. **Khối `kpi` là phần nội bộ.** Chỉ tiêu, mốc nghiệm thu, khoảng cách tới chỉ tiêu, rủi ro và trạng thái hợp đồng chỉ nằm trong `kpi`. Thẻ kế hoạch nhắc chỉ tiêu hay hợp đồng đặt `internal: true`. Cờ `--web` bỏ cả hai khi deck đi ra ngoài nhóm dự án.
6. **Không bao giờ ghi** giá dịch vụ, phí, giá trị hợp đồng, điều khoản thanh toán, email cá nhân. Tên người phía khách viết tắt. `check` chặn một số chữ cấm.
7. **Văn phong:** tiếng Việt, câu ngắn có chủ ngữ và vị ngữ, mỗi câu một ý. Không viết cụm cụt kiểu ghi chú ("Head lật URL", "77 sp từ 24 in"). Chữ bị giới hạn độ dài thì thêm `tip` (chữ đầy đủ khi rê chuột), đừng nén câu thành mã. Thuật ngữ SEO giữ tiếng Anh. Keyword giữ nguyên ngôn ngữ gốc.
8. **Chỉ topic đẩy keyword cam kết.** Không đề xuất blog chỉ kéo traffic. Không scale trang /x-vs-y hay trang địa điểm bằng AI. Không so sánh chê đối thủ. Không nhân một khung H2 sang nhiều trang.
9. **Trước kỳ đo, trang đang giữ Top 3/5 chỉ thêm, không rút.** Trang vừa sửa chờ 14 ngày mới đọc. Đọc hạng bằng median các lần chạy hợp lệ.
10. **Luôn nói vì sao.** SERP có `so` ("Vì vậy: …"). Pipeline có `why` cho từng chấm và `fix`. Ưu tiên có `why`. Đo lường có `why`. Thêm `guides` cho các slide khó đọc (serp, matrix, priority, measure).
11. **Ngoài chữ:** khối `levers` trả lời internal link, hình ảnh, chức năng, schema bằng dữ kiện kiểm trên trang thật (GET). Gắn nhãn Ranking, Kỹ thuật, Shopping, UX. Không hứa hạng cho slideshow, FAQPage, link sitewide.
12. **Markup cho phép trong chữ tự do:** `<b>`, `<i>`, `<br>`, `<g>…</g>` (chữ gradient, một lần trong tiêu đề slide), `<r>…</r>` (chữ đỏ cần kiểm tay). Không dùng thẻ khác. Không viết dấu `<` trơn.

## 2. Các khối

Giới hạn độ dài và số mục nằm trong `LIM` của `qp_render.py`. `check` báo khi vượt. Giới hạn lấy từ bố cục 1920×1080 đã chụp kiểm.

| Khối | Slide | Nội dung |
|---|---|---|
| `schema`, `slug`, `name`, `name_lines`, `domain`, `lead`, `order`, `market` | — | Định danh. `schema` = "qp-project/1". `slug` kebab-case không dấu. `name_lines` 1–2 dòng cho slide mở dự án. `order` chỉ cần khi gộp nhiều dự án. |
| `measure` | mọi slide | `has_rank` (false khi chưa có số đo hợp lệ, ví dụ site chưa live), `tool`, `project` (id hoặc tên bộ), `engine` (GM1, G1…), `engine_label`, `date` (dd/mm/yyyy, lần chạy mới nhất dùng cho số hiện tại), `compare_date` (một ngày trong nhóm lần chạy của mốc so sánh; để trống khi bảng hạng chạy `--no-compare`), `depth`. |
| `status_row` | bảng tổng quan | `set` (bộ keyword và engine), `now` (Top 3/5/10 hiện tại). |
| `kpi` | bảng tổng quan, slide mở dự án | **Nội bộ, tuỳ chọn.** `target` (mốc gần nhất), `gap`, `risk` (Cao/Vừa), `beat_stats` (0–2 cặp [số, nhãn]). |
| `headline` | bảng tổng quan | `template` đáng đẩy nhất, `fact` một câu bằng chứng. |
| `cover` | 1 | `query` khách gõ thật (thuộc bộ cam kết), `tokens` 2–4 mảnh {`t`, `r` vai trò, `k` = known/op/new}, `rep` query đại diện, `rep_sub` (bao nhiêu keyword cam kết đi theo query đại diện này). |
| `idea` | 2 | `n_kw`, `n_tpl`, `hub_url`, `hub_n`, `hub_top10` (URL giữ nhiều keyword cam kết nhất; lấy từ `hub_urls` của `qp_ranks.py`), `mechanism`, `effect`, `src`. Có thể thay câu mặc định bằng `n_kw_text`, `hub_text`. |
| `beat_stats` | slide mở dự án | 2–3 cặp [số, nhãn]: số keyword, Top 3/5/10 hiện tại. |
| `templates` | Template | `title`, `items[]` 5–16 template xếp theo mức đáng đẩy: `id`, `label` dạng "base [biến]", `n`, `now`/`ago` = số keyword theo nhóm `t3`, `t10`, `t20`, `t50`, `out` (tổng = `n`; lấy thẳng từ `templates` của `qp_ranks.py`; `ago` = null khi không có mốc so sánh), `status` ok/up/mid/no (`up` cần mốc so sánh), `status_label`, `note` (số Top 10 trong note phải khớp bảng hạng), `tip`. Tổng `n` của mọi template = số keyword của bảng hạng. |
| `grid` | Lưới hạng | `tabs[]` 3–6 template tiêu biểu: `id`, `base`, `slot`, `chips[]` 4–16 {`label` ngắn, `kw` đầy đủ, `now`, `ago` int hoặc null, `gap` true = site có trang nhưng keyword chưa vào độ sâu}, `read`, `act`, `topic` (mã topic · ưu tiên · công sức). |
| `canonical` | Canonical | `rows[]` 3–6 {`query`, `google` (URL/hạng Google đang chọn), `problem`, `decision`, `tag` (mã topic, "giữ", "đề xuất mới"), `new`, `tip`}. `rules[]` 2–4. `flip` {`label`, `steps[]` 2–5, `tip`}: quy trình khi Google lật URL. |
| `serp` | SERP | `cards[]` đúng 3 query đại diện của 3 intent: `query`, `meta` (nguồn · thị trường · ngày), `rows[]` 6–10 {`p` vị trí hoặc "—", `type`, `cls` ∈ cat, home, list, guide, aio, vid, prod, local, forum, news, other, `domain` ≤26 ký tự, `dr` tuỳ chọn, `me` true cho dòng của site (tối đa 1)}, `verdict`, `so` ≤120 ("Vì vậy: …"), `so_tip`. |
| `matrix` | Pipeline | `rows[]` 5–12 cụm {`name`, `topic`, `stages` {B2…B8: 0/1/2; tối đa 2 trạm chính, 1 trạm phụ}, `stat`, `diag` (chẩn đoán từ trang thật), `why` {trạm: lý do}, `fix` ≤200, `new`}. |
| `aug` | Augmentation | Tuỳ chọn. Trang đang rank: `title`, `url`, `components[]` 3–6 {`short`, `desc`, `kws[]` 1–5 {`kw`, `now`, `vol` (lấy từ `hang.json`; nguồn khác thì ghi ở `src`)}, `tip`}. Không có trang phù hợp thì bỏ khối và ghi lý do vào `flags`. |
| `pairs` | So sánh | Tuỳ chọn. Query "X và/hay/vs Y": `items[]` 2–6 {`a`, `b`, `op`, `kws[]`}, `why` {label, text}, `action` {label, text}, `note`. |
| `levers` | Ngoài chữ | Tuỳ chọn, nên có. `title`, `cols[]` 3–4 (Internal link, Hình ảnh, Chức năng, Schema), mỗi cột `items[]` 2–5 {`k` ∈ Ranking/Kỹ thuật/Shopping/UX, `text` ≤150, `tip`}; `dont[]` 0–5; `src`. |
| `retrieve` | Retrieve | Tuỳ chọn. Trang có trên site mà keyword không có hạng, hoặc lỗi retrieve khác (noindex, trang chờ, chưa go-live): `rows[]` 2–6 {`url`, `kws[]`, `note`, `tip`}, `checked`, `hypothesis`, `check_label`, `hyp_label`. |
| `qa` | Hỏi đáp | Tuỳ chọn. `items[]` 2–4 {`q`, `a`, `ev` (bằng chứng), `act`, `tip`}. Dùng cho câu team hay hỏi: PDP hay category, URL lật, click depth, chức năng, schema. |
| `priority` | Ưu tiên | `rows[]` 4–9 topic {`id` (T1…, hoặc "mới"), `template`, `evidence`, `why` ≤115, `n_kw` (số keyword cam kết topic đẩy, không trùng giữa topic), `stages`, `pri` P0/P1/P2, `when`, `tip`}. |
| `measure_slide` | Đo lường | `intro`, `why` ≤210, `regex[]` 3–6 {`name`, `rx` (chạy được trong GSC), `tip`}, `timeline[]` 2–4 {`d`, `t`, `tip`}, `rule` {label, text, tip}, `src`. |
| `plan` | Kế hoạch | `who` (Lead), `period` ("12–23/10"), `title`, `rows[]` 5–12 {`when`, `task` ≤150, `who`, `done` ≤110, `tip`} (hoặc `items[]` 5–8 chuỗi), `cards[]` 1–3 {label, text, internal}. |
| `flags` | — | Danh sách {slide, text}: điểm chưa kiểm chéo, khối bị bỏ, số cần xác minh. |
| `guides` | mọi slide | Tuỳ chọn. {khoá slide: chữ} nối vào nút "Cách đọc slide". Khoá hợp lệ: idea, templates, grid, canonical, serp, matrix, aug, levers, retrieve, qa, priority, measure, plan. |
| `gloss` | mọi slide | Tuỳ chọn. {thuật ngữ: giải thích} riêng của dự án. Thuật ngữ chung và mã topic T1… renderer tự thêm. Khi một mã topic còn mang nghĩa khác trên slide (ví dụ "T5" là kỳ đo), viết ngày cụ thể thay cho mã. |

## 3. Khung tối thiểu

```json
{
  "schema": "qp-project/1", "slug": "ten-khach", "name": "Tên khách", "name_lines": ["Tên khách"], "domain": "example.vn", "lead": "Tên Lead",
  "measure": {"has_rank": true, "tool": "SpySERP", "project": "123456", "engine": "GM1", "engine_label": "Google Mobile, Hà Nội", "date": "09/10/2026", "compare_date": "12/09/2026", "depth": 50},
  "status_row": {"set": "390 kw (GM1)", "now": "Top 3/5/10 = 16/35/90"},
  "kpi": {"target": "…", "gap": "…", "risk": "Vừa", "beat_stats": []},
  "headline": {"template": "…", "fact": "…"},
  "cover": {"query": "…", "tokens": [{"t": "…", "r": "…", "k": "known"}, {"t": "…", "r": "…", "k": "op"}], "rep": "…", "rep_sub": "…"},
  "idea": {"n_kw": 390, "n_tpl": 14, "hub_url": "/…/", "hub_n": 40, "hub_top10": 25, "mechanism": "Google gom các cách gõ thành cụm. Tâm cụm là query đại diện (US8645407B2). Giả thuyết: …", "effect": "…", "src": "…"},
  "beat_stats": [["390", "keyword cam kết"], ["16/35/90", "Top 3/5/10 (median 3 lần)"]],
  "templates": {"title": "…", "src": "…", "items": []},
  "grid": {"title": "…", "src": "…", "tabs": []},
  "canonical": {"rows": [], "rules": [], "flip": {"label": "Khi Google lật URL", "steps": []}, "src": "…"},
  "serp": {"cards": [], "src": "…"},
  "matrix": {"rows": [], "src": "…"},
  "levers": {"cols": [], "dont": [], "src": "…"},
  "retrieve": {"title": "…", "rows": [], "checked": "…", "hypothesis": "…"},
  "qa": {"items": []},
  "priority": {"rows": [], "src": "…"},
  "measure_slide": {"intro": "…", "why": "…", "regex": [], "timeline": [], "rule": {"label": "…", "text": "…"}, "src": "…"},
  "plan": {"who": "…", "period": "…", "title": "Kế hoạch hành động", "rows": [], "cards": [], "src": "…"},
  "flags": [], "guides": {}, "gloss": {}
}
```

Khối tuỳ chọn (`aug`, `pairs`, `levers`, `retrieve`, `qa`) không có dữ liệu thì xoá hẳn khỏi file, đừng để mảng rỗng.
