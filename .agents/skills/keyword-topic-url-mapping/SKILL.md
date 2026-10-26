---
name: keyword-topic-url-mapping
description: "Gom bộ keyword CAM KẾT hợp đồng thành topic → xác định URL SEO tương ứng — công đoạn (4) T1 của quy trình 10 tháng GTV, MAPPING layer đứng trước topical map và traffic plan. Use when: (1) 'nhóm keyword cam kết thành topic cho [client]', 'mapping keyword → URL SEO'."
metadata:
  version: "1.3.1"
---

# Keyword → Topic → URL SEO Mapping

Thực thi công đoạn (4) T1 quy trình 10 tháng: **"Nhóm keyword cam kết thành topic → URL SEO tương ứng"** (`sop/09-project-timeline/10-thang-thuc-day.md`, bảng Tháng 1). Input là bộ từ khóa CAM KẾT trong hợp đồng — output là bảng mapping keyword ↔ topic ↔ [[URL SEO]] ↔ intent ↔ Core/Outer ↔ % keyword + % volume, làm nền cho `topical-map-creation` (T1-T2) và `traffic-plan` (T2-T4).

🔴 Phạm vi CHỈ là bộ keyword cam kết (thường vài chục đến vài trăm keyword) — không phải toàn bộ query space của niche. Toàn bộ query space là việc của topical map.

## Phân vai (không lấn sân)

| Việc | Skill phụ trách | Ranh giới cụ thể |
|---|---|---|
| Gom nhóm keyword bằng SERP-overlap (ma trận overlap, ngưỡng, chain-merge, tier data) | `serp-clustering` | DATA layer — skill này CONSUME bảng cụm của serp-clustering rồi ra quyết định URL/intent/Core-Outer; không tự chạy clustering. Fallback thủ công (Tầng 2) chỉ khi serp-clustering không chạy được |
| SCN / topical map đầy đủ toàn site (Source Context, Central Entity, 23 bước) | `topical-map-creation` | Skill này CHỈ mapping bộ keyword cam kết; output là 1 input của topical map, không thay thế map. Topic Outer phát sinh thêm ngoài bộ cam kết → ghi chú gợi ý, không tự mở rộng |
| Research sâu 1 bài / 1 SERP (Layer A/B, consensus) | `seo-research` | Skill này chỉ nhìn SERP ở mức overlap URL để cluster, không phân tích content đối thủ |
| Forecast traffic per topic/URL | `traffic-plan` | Skill này không gắn số traffic dự phóng — chỉ % keyword + % volume phân bổ |
| Audit cannibalization site đang chạy | `technical-seo-audit` + `content-refresh` | Skill này CHỐNG cannibalization từ khâu plan (1 topic = 1 URL chính), không audit hiện trạng |
| Wireframe / cấu trúc website từ URL list | `visual-semantic-seo` + `semantic-html-optimization` | Skill này dừng ở đề xuất page type, không thiết kế trang |

## Input

**Required:**
- `$CLIENT` — tên client/instance SEO Production.
- Bộ keyword cam kết: đọc từ `00-client-context/kpi-commitments.md` của instance, hoặc user paste (keyword + volume nếu có + vị trí hiện tại nếu có).

**Optional:**
- `$SITE` — domain client (để nhận diện URL đã tồn tại có thể nhận topic thay vì tạo URL mới).
- `$SERP_DATA` — export SERP top-10 per keyword (Ahrefs/DataForSEO/user tự chạy).
- `$OVERLAP_THRESHOLD` — ngưỡng cluster, mặc định **≥4/10 URL top-10 chung → cùng topic** (điều chỉnh được: niche SERP đồng nhất cao có thể nâng 5-6; lưu ý `topical-map-creation` Step 10 dùng threshold 3 — khác biệt là chủ đích: bộ cam kết cần cluster chặt hơn để không thiếu URL money).
  - Vai trò 2 ngưỡng: 4/10 URL chung là ngưỡng xếp keyword vào cùng cụm khi lập plan. 6/10 là điều kiện gộp 2 URL đang có. Lý do: cùng một keyword kéo lại SERP trong ngày chỉ chung 5–10/10 URL với chính nó, nên 4–5/10 nằm trong biên dao động của SERP. Topic map vào URL `EXISTING` đang là 2 trang riêng thì chỉ gộp 2 trang khi SERP ≥ 6/10.

**Data ladder (v1.1 — Tier 1-2 chạy BÊN TRONG `serp-clustering`, ladder chi tiết + cost gate xem skill đó; khai báo DATA TIER trong output):**

| Tier | Nguồn | Ghi chú |
|---|---|---|
| Tier 1-2 | Skill `serp-clustering` (Ahrefs MCP `serp-overview` → DataForSEO SERP → search tay mẫu đại diện) | Gọi serp-clustering với bộ keyword + `$OVERLAP_THRESHOLD` → nhận bảng cụm kèm overlap evidence + tier data; cost gate (số call = số keyword) do serp-clustering báo |
| Tier 3 | Semantic/intent grouping thủ công theo [[Central Search Intent]] | Fallback khi không chạy được serp-clustering — luôn chạy được: cluster bằng phân tích intent + lexical, ghi rõ "cluster chưa verify bằng SERP" |

## Phân việc model

| Model | Việc trong skill | Quyết định |
|---|---|---|
| EmbeddingGemma 2 | Định tuyến keyword cam kết → URL đang có (`retrieval-lab route`), so với URL Google chọn | dùng ở Bước 2b khi có store `site-vector-index`. Danh sách để đọc, không tự gán URL: top-1 trùng Google 75,5% trên mọi query, 29,3% trên query trang tiền (lượt thử 19/10/2026). Trên trang tiền, kết quả định tuyến chỉ là danh sách cần đọc. Không đưa con số 29,3% vào deck khách |
| Code (`gsc_route.py`) | Gộp query GSC, URL Google chọn, `share` | dùng: GSC chỉ xử lý local |
| Jev | Gán intent I/N/C/T | không dùng: bộ cam kết vài chục tới vài trăm keyword, Claude gán nhanh hơn hiệu chuẩn một rubric. Query GSC không gửi vào Jev |
| GLM Flash | Trích câu | không dùng: skill không trích câu |
| Claude | Gán intent, chấm QDP gate, quyết URL, Core/Outer, page type | dùng |

## Workflow

### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need 'python3,gemma?,gsc?,dataforseo?,ahrefs?'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".

- Thiếu `gemma`, `gsc` hoặc chưa có store của site: bỏ Bước 2b, ghi lý do ở header output.

### Bước 0b — Đọc references + xác nhận scope

1. Đọc `sop/09-project-timeline/10-thang-thuc-day.md` (công đoạn 4, T1) + `00-client-context/kpi-commitments.md` của instance.
2. Xác nhận: bộ keyword đủ chưa (đúng bản cam kết hợp đồng, không phải wishlist), có volume kèm không, `$SITE` có content sẵn không.
3. Chốt DATA TIER; Tier 1-2 → gọi `serp-clustering` (cost gate + báo số call do skill đó thực hiện).

### Bước 1 — Chuẩn hóa bộ keyword

1. Dedupe, tách biến thể chính tả/dấu, gắn volume (thiếu volume → lấy qua Ahrefs `keywords-explorer-overview` hoặc để trống ghi chú).
2. Gắn nhãn intent sơ bộ per keyword: **I** (Informational) / **N** (Navigational) / **C** (Commercial) / **T** (Transactional) — theo [[User Intent]]; keyword mơ hồ → đánh dấu xử lý ở Bước 2 theo [[Mixed Intent]].

### Bước 2 — Clustering 2 tầng

**Tầng 1 — SERP-overlap clustering qua `serp-clustering` (ưu tiên khi có data):**
1. Gọi skill `serp-clustering` với bộ keyword đã chuẩn hóa (Bước 1), truyền `$OVERLAP_THRESHOLD` nếu khác mặc định → nhận **bảng cụm**: members, volume, overlap evidence (min-max URL chung), verdict GỘP/TÁCH/BORDERLINE, tier data, ngày chụp SERP.
2. Skill này KHÔNG tự chạy ma trận overlap nữa — CONSUME bảng cụm rồi ra quyết định URL / intent / Core-Outer ở Bước 3.
3. Cụm BORDERLINE hoặc flag `chain-merge` từ serp-clustering → quyết định tại đây theo intent + monetization, ghi lý do vào mục 3 của output.

**Tầng 2 — Semantic/intent grouping (fallback khi không chạy được serp-clustering, hoặc bổ trợ cho keyword thiếu SERP data):**
1. Nhóm theo [[Central Search Intent]]: cùng entity + cùng nhu cầu người dùng + cùng loại kết quả kỳ vọng → cùng topic.
2. Keyword khác intent (I vs T) KHÔNG gộp dù chung entity — "mua X" và "X là gì" là 2 topic/URL khác nhau.
3. Cluster từ tầng 2 đánh dấu `⚠️ chưa verify SERP` — đề xuất verify lại khi có data.

### Bước 2b — Định tuyến keyword → URL đang có (khi `$SITE` có store và GSC)

Đọc `skills/query-processing-diagnosis/references/dinh-tuyen.md`. Bước này chỉ chạy local. Không đặt ngưỡng cosine mới.

1. Ghi bộ cam kết vào `<W>/route/keywords.txt`, mỗi dòng một keyword.
2. Chạy `python3 skills/query-processing-diagnosis/scripts/gsc_route.py prep --gsc <GSC query × page 90 ngày> --keywords <W>/route/keywords.txt --candidates <URL cùng ngôn ngữ> --keep-missing --out <W>/route/queries.jsonl`.
3. Chạy `~/.venvs/embeddinggemma/bin/python -I skills/retrieval-lab/scripts/retrieval.py route --store <store của $SITE> --in <W>/route/queries.jsonl --out <W>/route/routing.jsonl --level page`.
4. Chạy `python3 skills/query-processing-diagnosis/scripts/gsc_route.py summary --routing <W>/route/routing.jsonl --out <W>/route/tom-tat`.
5. Dùng `tom-tat.tsv` ở Bước 3:
   - Keyword có URL Google chọn: URL đó là ứng viên `EXISTING` đầu tiên.
   - Verdict "Google chia query": ghi vào mục 3 của output là ứng viên cannibalization.
   - Verdict "chưa có dữ liệu GSC": đọc trang `gemma_top` trước khi đề xuất URL `NEW`.

### Bước 3 — Topic → URL SEO

Per topic:
1. **1 topic = 1 URL chính** — chống cannibalization từ khâu plan. Keyword phụ trong topic = biến thể/secondary keyword của cùng URL.
1b. **QDP Gate (v1.2)** — trước khi chốt "topic này xứng 1 URL": chấm 4 tiêu chí `references/qdp-gate.md` (CANONICAL — high demand / different entities / low similarity WEIGHTED / pattern; ≥3/4 → URL riêng). Không đạt → topic hạ cấp thành **QDH** (heading trong URL cha) / **QDS** (sentence) / **component** (table/calculator/filter) — ghi vào mục 3 output "Keyword chưa xếp được / cần quyết định" kèm URL cha đề xuất. Tiêu chí #3 low-similarity dùng chính SERP-overlap của serp-clustering làm proxy (cụm GỘP = similarity cao). Đặc biệt bắt buộc với topic [service]+[location] (local) và mọi đề xuất mở URL NEW.
2. Phân loại **Core / Outer Section**: topic mang monetization + gần Central Search Intent → [[Core Section]]; topic bổ trợ/informational nuôi [[Historical Data]] → [[Outer Section]] (chuẩn phân loại theo `sop/01-topical-map.md` Bước 5-6).
3. Intent chủ đạo của topic (I/N/C/T) — topic hybrid ghi chú theo [[Mixed Intent]] (default tách, exception khi SERP ≥7/10 hybrid).
4. **Page type đề xuất**: category / product / blog / landing (theo intent + SERP top-10 đang rank page type gì — [[Page Types]]).
5. URL: dùng URL sẵn có của `$SITE` nếu match topic (ghi `EXISTING`), không thì đề xuất slug mới (`NEW`) — Core flat, Outer sâu hơn theo convention topical map. Có Bước 2b thì đọc `tom-tat.tsv` trước khi chọn. Gemma top-1 khác URL Google chọn không đủ để đổi URL.

### Bước 4 — Tính % phân bổ

- **% keyword per topic** = số keyword trong topic / tổng bộ cam kết.
- **% search volume per topic** = tổng volume topic / tổng volume bộ cam kết (chỉ khi có volume; thiếu → ghi N/A).
- Sanity check: topic chiếm >40% volume → flag "topic quá nặng, xem xét tách" ; keyword lẻ loi không cluster được → topic đơn hoặc gán làm secondary cho topic gần nhất (ghi chú lý do).

### Bước 5 — Render output & lưu

1. Render bảng theo skeleton Output.
2. Lưu `05-content-plan/` của instance, naming `{{CLIENT}}_keyword-topic-url-mapping_v{{N}}.md`.
3. Ghi trạng thái **CHỜ DUYỆT: SEO Lead Project** (cột Duyệt công đoạn 4, T1).
4. Nhắc bước kế tiếp: bảng này là input cho `topical-map-creation` (chốt SCN đầu T2) + `traffic-plan`.
5. Tự phản biện theo mục dưới, rồi kiểm Behavior Gates.

### Tự phản biện trước khi trình
Chấm bản nháp theo checklist "Bản tốt nhất phải có". Mục chưa đạt thì sửa, hoặc ghi lý do bỏ. Nếu có output của Codex hay agent khác cho cùng việc, so từng mục và lấy phần tốt hơn trước khi trình Vincent.

Bản tốt nhất phải có:
- [ ] Mỗi keyword cam kết có đúng 1 URL. Keyword có verdict "Google chia query" nằm ở mục 3 kèm 2 URL đang tranh. Nguồn lỗi: pilot định tuyến 19/10/2026, 229 query và 149 cặp URL là ứng viên cannibalization trên site mẫu; một nhóm có 4 URL cùng nhận query.
- [ ] URL `EXISTING` là URL Google đang trả hoặc trang đã đọc, không chỉ là Gemma top-1. Nguồn lỗi: lượt thử 19/10, template "dịch vụ seo" chỉ 2,5% hiển thị có Gemma top-1 trùng URL Google chọn.
- [ ] Topic gộp có bảng cụm của `serp-clustering` hoặc SERP overlap, không gộp theo cosine. Gộp 2 URL đang có cần SERP ≥ 6/10. Nguồn lỗi: audit GSC 17/10 đề xuất gộp 5 cặp trang, SERP 18/10 cho 4 cặp tách.
- [ ] Topic [dịch vụ] + [địa phương] có kết quả QDP gate trước khi gộp vào trang chung hay mở URL `NEW`. Nguồn lỗi: SERP 18/10, "công ty seo hà nội" và "công ty seo" chung 0/10 URL.
- [ ] % volume ghi nguồn volume. Nguồn lỗi: đợt chẩn đoán 10 dự án 10/2026, một keyword có volume 2.400 / 60.500 / 39.000 giữa SpySERP, sheet và Ahrefs.
- [ ] Query GSC chỉ xử lý local bằng code và EmbeddingGemma. Nguồn lỗi: `jev.py` thêm chặn `must_be_empty` ngày 19/10/2026 để query GSC không vào Jev.

## Output

```markdown
# <CLIENT> — Keyword → Topic → URL SEO Mapping (công đoạn 4, T1)
> Ngày lập: YYYY-MM-DD · DATA TIER: <1/2/3 — nguồn SERP + ngày> · Overlap threshold: <4/10>
> Bộ keyword cam kết: <N> keywords · Tổng volume: <N | N/A>
> Định tuyến (retrieval-lab route): <n khớp / n lệch / n chưa có GSC | không chạy + lý do>
> Trạng thái: **CHỜ DUYỆT — SEO Lead Project**

## 1. Bảng mapping
| # | Topic | URL SEO (EXISTING/NEW) | Core/Outer | Intent | Page type | Keywords trong topic | % keyword | % volume | Verify SERP |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | kw1 (vol) · kw2 (vol)… | | | ✅ / ⚠️ chưa verify |

## 2. Tổng hợp phân bổ
| Chỉ số | Giá trị |
|---|---|
| Số topic | |
| Số URL (EXISTING / NEW) | |
| Tỷ lệ Core : Outer (theo URL) | |
| Topic nặng nhất (% volume) | |

## 3. Keyword chưa xếp được / cần quyết định
- <keyword mơ hồ intent, cluster mâu thuẫn SERP vs semantic — kèm đề xuất>

## 4. Ghi chú cho bước sau
- Input cho: topical-map-creation (chốt SCN đầu T2) · traffic-plan (forecast)
- Gợi ý topic Outer phát sinh ngoài bộ cam kết (nếu thấy): <liệt kê — KHÔNG tự triển khai>
```

## Behavior Gates

**#1 Think Before** — Xác nhận bộ keyword đúng là bản CAM KẾT hợp đồng trước khi cluster. Trước khi gọi MCP: báo số call (= số keyword ở Tier 1), chờ xác nhận; bộ >100 keyword → đề xuất phương án mẫu đại diện.

**#2 Evidence** — Cluster nào từ SERP-overlap ghi số overlap thực (vd "6/10"); cluster nào từ semantic grouping đánh dấu `⚠️ chưa verify SERP`. Output khai báo DATA TIER. Không hard-fail thiếu MCP — Tier 3 luôn chạy được.

**#3 Surgical** — Chỉ mapping bộ cam kết. Không mở rộng sang toàn niche, không viết brief, không forecast traffic, không thiết kế page. Topic phát sinh ngoài bộ cam kết → mục "Gợi ý" rồi dừng.

**#4 Goal-driven** — Deliverable trả lời được: "bộ cam kết cần bao nhiêu URL, URL nào Core URL nào Outer, keyword nào về URL nào, sức nặng volume nằm ở đâu" — mỗi keyword cam kết phải có đúng 1 URL phụ trách, không keyword nào 2 URL (cannibalization) và không keyword nào 0 URL (bỏ sót cam kết).

## Anti-patterns

- ❌ Gộp keyword khác intent (I vs T) vào 1 URL vì chung entity.
- ❌ 1 topic nhiều URL chính — cannibalization từ khâu plan.
- ❌ Cluster chỉ bằng lexical similarity (chung chữ) khi có SERP data — SERP overlap là bằng chứng mạnh hơn ([[syntheses/Lexical-vs-Intent Rule]]).
- ❌ Tự mở rộng sang topic ngoài bộ cam kết rồi trình như một topical map — lấn sân `topical-map-creation`.
- ❌ Bỏ keyword cam kết ra khỏi bảng vì "khó cluster" — mọi keyword cam kết phải có URL phụ trách.
- ❌ Đề xuất URL NEW khi site đã có URL EXISTING match topic — kiểm tra `$SITE` trước.
- ❌ Trình % volume khi một nửa bộ keyword không có volume mà không ghi N/A/caveat.
- ❌ Trình bảng như bản chốt khi chưa có duyệt SEO Lead Project.

## References & wiki

**Nguồn quy trình:**
- `sop/09-project-timeline/10-thang-thuc-day.md` — công đoạn (4) T1: "Nhóm keyword cam kết thành topic → URL SEO tương ứng + % keyword theo topic".
- `sop/01-topical-map.md` — chuẩn Core/Outer Section (Bước 5-6), Central Search Intent (Bước 4).
- `SEO Production/00-client-context/kpi-commitments.md` (per instance) — nguồn bộ keyword cam kết.

**Wiki Semantic SEO (lớp WHY):** [[URL SEO]] · [[Central Search Intent]] · [[User Intent]] · [[Mixed Intent]] · [[Core Section]] · [[Outer Section]] · [[Query Network]] · [[Canonical Query]] · [[Page Types]] · [[syntheses/Lexical-vs-Intent Rule]]

**Skill anh em:** `topical-map-creation` (downstream — SCN đầy đủ) · `traffic-plan` (downstream — forecast) · `seo-research` (research 1 bài) · `competitor-seo-gap-analysis`

## Changelog

- **2026-10-19 v1.3.1** — ghi rõ vai trò 2 ngưỡng SERP: 4/10 xếp keyword vào cùng cụm khi lập plan, 6/10 là điều kiện gộp 2 URL đang có. Định tuyến Gemma trên trang tiền chỉ là danh sách cần đọc (top-1 trùng URL Google 29,3%), không đưa con số này vào deck khách.
- **2026-10-19 v1.3** — Bước 0 kiểm tool. Thêm Bước 2b định tuyến keyword → URL đang có bằng `retrieval-lab route` và `gsc_route.py` của `query-processing-diagnosis` (GSC chỉ xử lý local, dùng cổng `share` 0,6 có sẵn). Thêm phân việc model và tự phản biện.

- **2026-07-19 v1.1** — tách SERP-overlap clustering ra skill `serp-clustering` (DATA layer), skill này giữ DECISION layer: Bước 2 Tầng 1 = gọi serp-clustering → nhận bảng cụm → quyết định URL/intent/Core-Outer; giữ Tầng 2 fallback thủ công khi không chạy được serp-clustering; thêm dòng Phân vai + cập nhật data ladder.
- **2026-07-19 v1.0** — tạo mới: thực thi công đoạn (4) T1 sop/09; clustering 2 tầng (SERP-overlap ≥4/10 ưu tiên → semantic/intent fallback), 1 topic = 1 URL chính, phân loại Core/Outer + intent I/N/C/T + page type + % keyword/% volume; data ladder Ahrefs serp-overview → DataForSEO → thủ công; gate duyệt SEO Lead Project.
