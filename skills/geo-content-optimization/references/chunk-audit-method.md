# Chunk Audit Method — tách, chấm, rewrite

Reference cho Bước 1-2-5 của `geo-content-optimization`. Mọi con số kèm nguồn + ngày; số đơn nguồn label rõ.

## 1. Cách tách bài thành chunk

### Cách chính: theo H2/H3 (extraction boundary tự nhiên)

- Mỗi H2 (kèm H3 con nếu ngắn) = 1 chunk audit. H2/H3 là extraction boundary mà AI system dùng khi cắt passage (Dejan 2026, khuyến nghị nguyên văn: "front-load value, H2/H3 làm extraction boundary, mỗi section độc lập").
- Intro (đoạn trước H2 đầu tiên) = chunk #0 — ứng viên Audition Chunk số 1, chấm kỹ nhất.

### Cách stress-test: mô phỏng cắt thô ~128 tokens của ChatGPT

Chunking thực tế của ChatGPT THÔ: cắt giữa câu, dính navigation ([[Audition Chunk]]; tham số McSweeney — reverse-engineered estimate, đơn nguồn):
- Cắt bài thành cửa sổ ~128 tokens (~100 từ EN / ~80 từ VI) bất chấp câu.
- Hỏi mỗi cửa sổ: "đoạn này đứng riêng có còn nghĩa + còn Entity không?"
- Chunk nào chỉ có nghĩa nhờ đoạn trước → red flag phụ thuộc ngữ cảnh.
- ⚠ ~80 từ VI cho 128 tokens là suy ra từ tỷ lệ token hoá — penalty tiếng Việt chưa ai đo (Open Question trong [[Audition Chunk]]).

## 2. Bảng chunk size đa hệ (KHÔNG trộn số giữa các hệ)

| Hệ | Con số | Dùng làm gì | Nguồn |
|---|---|---|---|
| ChatGPT chunking | ~128 tokens (~100 từ EN / ~80 từ VI); sliding window 300 từ | Stress-test cắt thô | [[ChatGPT Pipeline]] — đơn nguồn McSweeney, label estimate |
| OpenAI file_search (official) | 800 tokens, overlap 400 | Tham chiếu RAG chuẩn | [[Audition Chunk]] mục Fact-fix |
| RAG research | 64-128 tokens tối ưu fact-retrieval | Lý do passage ngắn thắng | [[Audition Chunk]] mục Fact-fix |
| Chrome DocumentChunker | max 200 words/passage, max 30 passages/page | Trần passage phía Google | [[Audition Chunk]] mục Fact-fix |
| AIO cited passages | phổ biến 134-167 từ; 62% trong dải 100-300 từ | **Sweet spot khi REWRITE passage trả lời: 100-170 từ** | Wellows 12/2025, qua [[AI Overviews]] |
| Khối coherent extract được | 200-300 từ | Trần cho section cần dài | Dejan 2026 |
| **Chuẩn chunk GTV (29/08/2026)** | **Không cap số từ / H2 section.** Khối ý **<~200 từ** là con số vận hành duy nhất (`observational`, Chrome) | Ngưỡng vận hành khi audit + rewrite | Vincent chốt 29/08/2026 — thay cho "≤~375 từ" cũ (không có nguồn; 500 token là default cấu hình Vertex, không phải yêu cầu Google Search) |

**Vì sao bỏ 375 từ:** 4 con số chunk trong wiki thuộc 4 hệ khác nhau (ChatGPT ≈128 token · OpenAI file_search 800 · Vertex 500 · Chrome 200 từ) và **không hệ nào là yêu cầu của Google Search** (Google: *"no requirement to break your content into tiny pieces"*). Cap số từ section ép cắt ngắn → mất contextual coverage của facet. Cái máy cần là **ranh giới + tự đứng + heading tổ tiên**, không phải độ dài. Bảng canonical: [[Audition Chunk]] §"3 con số chunk".

## 3. Rubric self-containment per chunk (AX1 → GE-19)

Chấm mỗi chunk 5 tiêu chí — fail ≥2 tiêu chí → verdict REWRITE:

| # | Tiêu chí | Pass khi | Fail khi |
|---|---|---|---|
| a | **Tự đứng** | Cắt rời khỏi bài, chunk vẫn đủ Entity (tên đầy đủ, không viết tắt lần đầu) + context + claim để trả lời trọn 1 sub-query | Người đọc phải đọc section trước mới hiểu |
| b | **1 heading = 1 facet + khối ý** | Section trả lời trọn **1** sub-question/cluster; mỗi khối ý (đoạn/nhóm đoạn cùng 1 ý) **<~200 từ**; section nhiều facet → đã tách H3 | Section gánh ≥2 facet không tách; khối ý >200 từ không có heading/đoạn mới; hoặc bị cắt cụt để "cho ngắn" mà thiếu E-A-V |
| c | **Câu 1 = answer, 40-75 từ** | Câu đầu sau heading trả lời trực tiếp heading (Subordinate Text Match — mục 4), dài 40-75 từ, đủ E-A-V | Dính 1 trong 5 anti-patterns |
| d | **Không hồi chỉ** | Không "điều này", "như trên", "sản phẩm nói trên", đại từ mơ hồ | Có → chunk mất nghĩa khi bị cắt rời |
| e | **Heading tổ tiên có nghĩa** | H1/H2 cha của chunk đọc lên là biết chunk nói về entity/facet nào (`includeAncestorHeadings` — máy gắn heading cha vào chunk như metadata) | Heading cha rỗng nghĩa: "Tổng quan", "Phần 2", "Kết luận", "Thông tin thêm" |

Ngoài rubric: **mỗi câu trong chunk tự đứng S-V-O đủ E-A-V** (53% citation là câu giữa đoạn — Indig, B) — không chấm điểm riêng, nhưng là lý do rewrite ưu tiên câu quotable hơn nhồi thêm chữ.

Verdict thứ 3 — **TÁCH PAGE**: khi nhiều chunk lệch hẳn Central Search Intent của page (page đa chủ đề). Tín hiệu định lượng nếu đo được embedding: đoạn có cos với tâm trang thấp hẳn so với các đoạn khác của chính trang. Dejan 2026 đo representativeness bằng model tiếng Anh; mốc của nghiên cứu đó không dùng làm ngưỡng. Ngưỡng cho EmbeddingGemma đọc từ registry của skill `model-calibration`; chưa có thì ghi "chưa hiệu chuẩn, Claude đọc" và Claude đọc các đoạn đó. Đề xuất tách, KHÔNG đề xuất viết thêm cho "đủ coverage".

## 4. Subordinate Text Match — câu 1 sau heading

Nguồn: [[Subordinate Text Match]]. Nguyên tắc: câu đầu tiên dưới heading phải LÀ câu trả lời của heading, không phải dẫn nhập.

### 5 anti-patterns (❌)

1. **Pre-intro filler** — "Trước khi trả lời, hãy cùng tìm hiểu..." → xoá, trả lời luôn.
2. **Context-before-answer** — 2-3 câu bối cảnh rồi mới tới answer → đảo: answer trước, context sau.
3. **Rhetorical restart** — lặp lại heading thành câu hỏi tu từ ("Vậy X là gì?") → xoá.
4. **Offtopic hook** — mở bằng chuyện/khẩu hiệu không chứa Entity của heading → xoá hoặc chuyển xuống.
5. **Hedge words** — "có lẽ", "tùy trường hợp", "khá là" ngay câu 1 → viết absolute fact (Pegasus principle), điều kiện đưa xuống câu sau.

### Bảng heading-type → L0 pattern (câu 1 nên là gì)

| Heading type | L0 pattern câu 1 | Ví dụ khung |
|---|---|---|
| Definitional ("X là gì") | X là <class> + <thuộc tính phân biệt> | "Topical Authority là mức độ tin cậy chủ đề mà..." |
| How-to ("Cách làm X") | Kết quả + số bước: "Để X, thực hiện <n> bước: ..." | câu 1 nêu đủ khung, bước chi tiết theo sau |
| Comparison ("A vs B") | Verdict-first: khác biệt cốt lõi trong 1 câu | "A khác B ở chỗ: ..." |
| Boolean ("Có nên X?") | Yes/No + điều kiện chính | "Có — khi <điều kiện>; không khi <điều kiện>." |
| List ("Top n X") | Đếm + liệt kê tên ngay câu 1-2 | "Có <n> X đáng chọn: A, B, C..." |
| Cost/number ("Giá X") | Con số + dải + ngày cập nhật | "X có giá <dải số> (cập nhật <tháng/năm>)." |

⚠ Gates là SERP-intent-conditional: definition-first không universal — narrative niches (travel/lifestyle) và SERP không đòi definition thì không áp máy móc (memory: SERP-intent gates patterns; Open Question trong [[Subordinate Text Match]]).

## 5. Manual cosine proxy (khi không có embedding tool)

Các study dùng bge-base-en-v1.5 (AirOps) / embeddinggemma-300m (Dejan), đều trên tiếng Anh. Mốc cos của các study này không dùng làm ngưỡng. Có EmbeddingGemma 2 local: đo theo skill `geo-fanout-research` Bước 4a, đọc ngưỡng phủ (rubric `geo-fanout-coverage`) từ registry của skill `model-calibration`; chưa có thì ghi "chưa hiệu chuẩn, Claude đọc". Hiệu chuẩn 19/10/2026 chưa có ngưỡng phủ tuyệt đối; chỉ so tương đối trong cùng top 10 có tín hiệu. Fallback thủ công khi không có embedding ([[Audition Chunk]] In Practice — Manual audit):

1. Liệt kê 10 key terms của Semantic Query (Entity + attributes + intent verbs; nhớ weight ChatGPT ước lượng 80% intent / 20% topic — estimate đơn nguồn).
2. Đếm overlap trong đoạn đang chấm (heading + first 100-150 từ):
   - **≥5/10 = PASS** · 3-4/10 = borderline, cân nhắc · **<3/10 = REWRITE**.
3. Với heading: so heading với sub-query gần nhất từ fan-out simulation. Proxy thủ công: overlap ≥7 ≈ khớp tốt, 5-6 ≈ khớp, <3 ≈ lệch (quy ước nội bộ, label "estimate"). Không quy đổi proxy sang dải cos.

## 6. Front-load check (AX2) — ví dụ ĐÚNG/SAI

**Ngưỡng:** best content trong 30% đầu trang — 44,2% AI citations từ first-30% (Indig 02/2026; patent US9940367B1). First 100-150 từ = audition chunk target. Central Entity + keyword chính trong 100 chữ đầu (P16).

Ví dụ intro cho query "TTFB là gì" (minh hoạ theo dải cosine trong [[Audition Chunk]]):

| Intro mở đầu bằng | Cosine ước lượng (minh hoạ thứ tự, không phải ngưỡng) | Verdict |
|---|---|---|
| "Chào mừng bạn đến với blog của chúng tôi! Hôm nay chủ đề rất thú vị..." | ~0,1 | ❌ junk — page rớt trước Deep Reading |
| "Tốc độ website ảnh hưởng lớn đến trải nghiệm người dùng..." | ~0,25 | ❌ context-before-answer |
| "TTFB (Time To First Byte) là thời gian từ khi trình duyệt gửi request đến khi nhận byte đầu tiên từ server, thường đo bằng ms..." | ~0,85 | ✅ answer-first, Entity đầy đủ |

## 7. Retrievability Scorecard (tổng hợp per page)

Weighted theo thứ tự sức mạnh predictor:

| Trục | Trọng số | Cách chấm | Evidence thứ tự |
|---|---|---|---|
| **Rank status** | GATE (pass/fail, không cộng điểm) | Page-one của ≥1 sub-query = PASS | Predictor mạnh nhất: pos 0 = 58% citation vs pos 10 = 14%; median rank cited 2,5 vs never-cited 13 (Indig 04/2026). Page-one là đủ — snippet quality phẳng rank 1→10, drop ~2% (Dejan 2026) |
| **Heading↔query alignment** | 30% | % heading Claude xác nhận khớp cluster (cos Gemma chỉ xếp thứ tự đọc, ngưỡng theo registry) + title 0,656 benchmark + slug natural-language (89,78% vs 81,11%) | Content signal mạnh nhất theo nghiên cứu tiếng Anh: heading khớp sub-query được cite 41% so với 30% khi lệch; +19pp trong nhóm top-rank (Indig 04/2026; Ahrefs 04/2026). Mốc cos bge của nghiên cứu không dùng cho Gemma |
| **Chunk quality (AX1+AX2)** | 30% | % chunk PASS rubric mục 3 + front-load mục 6 | Audition Chunk gate; 44,2% citations first-30% |
| **Freshness** | 20% | Ngày update cuối ≤30 ngày = full điểm | 76,4% top cited pages update trong 30 ngày (GEO.md — giữ đúng số); `URL_freshness_score` (Yeşilyurt). Nuance: trong 1 retrieval set trang established thắng trang mới, trừ news |
| **Tactics KDD** | 20% | Có quote nguồn liên quan + statistics + cite nguồn sau claim trong các chunk chính; mỗi số truy được nguồn + ngày | KDD 2024 đọc primary: Quotation Addition top, "+41%/+28%" theo 2 metric proxy (GPT-3.5, 2023-24); đòn bẩy lớn nhất khi trang là nguồn yếu trong câu trả lời (Rank-5 +115,1% đi kèm Rank-1 −30,3%) — không viết "+40%"/"+115%" |

🔴 KHÔNG chấm vào scorecard: schema (causal test Ahrefs 1.885 pages ≈ 0 tác động citation), llms.txt (không phải lever), content volume (correlation ~0,194), độ dài (snippet length ↔ quality r=0,05; page length ↔ representativeness r=-0,07 — Dejan 2026), DR page-level ("DR does not matter much" — [[Core Source]]).

**Đọc điểm:** ≥8/10 = giữ + theo dõi; 5-7 = rewrite chunk fail; <5 = cân nhắc tách page / quay lại outline. Mục tiêu cuối không phải điểm — là thành Core Source (FCR 0,42 vs 0,23 uncited).

**ROI khi verdict REWRITE (bổ sung 29/08/2026):** chỉ **tái cấu trúc không đổi chữ** (đảo câu đầu lên, tách khối ý, gộp claim về 1 câu quotable đúng heading) đã cho **+17,3% citation trên 6 engine** (Yu et al., arXiv 2603.29979 — đọc qua Surfer, nhãn C→B, cần đọc primary) → thứ tự rewrite: cấu trúc trước → câu quotable → mới thêm facts/quote (KDD). Sau restructure, chấm thêm **AX6** (mục 8).

## 8. AX6 — Passage verifiability (GE-23)

Cơ chế linkify 2 pha (patent US11769017B1 + US20240289407A1, verified 21/08/2026): AI sinh summary từ nhiều SRD, rồi **verify từng đoạn của summary bằng khoảng cách embedding** với passage nguồn trước khi gắn link → **document nuôi summary ≠ document được cite**. Trang có claim đúng nhưng phát biểu rải ở 2-3 đoạn, hoặc nằm dưới heading lệch cluster, sẽ nuôi câu trả lời mà không được link.

Check per claim quan trọng (3-6 claim/bài, lấy từ Key-Facts table của intro nếu có):

| # | Câu hỏi | Pass | Fail → fix |
|---|---|---|---|
| 1 | Claim nằm dưới heading **khớp cluster** mà claim trả lời? (Bước 3) | ✅ | Chuyển claim về đúng section |
| 2 | Claim là **1 câu S-V-O hoàn chỉnh**, có số + nguồn + ngày ngay trong câu hoặc câu liền kề? | ✅ | Gộp 2-3 mảnh thành 1 câu quotable |
| 3 | Câu đó **tự đứng** khi cắt khỏi đoạn (không hồi chỉ, entity tên đầy đủ)? | ✅ | Thay đại từ bằng entity |

Output: `<n>/<m> claim PASS` + danh sách claim cần gộp — ghi vào report mục 3 (Alignment) dòng AX6.
