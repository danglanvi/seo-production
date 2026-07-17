---
type: sop
tier: 1
phase: outline-am
last_updated: 2026-04-20
source_file: raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx
items_count: 19
tags: [sop, tier-1, outline, article-methodology, self-checklist]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/tier-1-outline-am.md` ngày 2026-07-17.
> Bản chưng cất — đã lược evidence/theory; bản đầy đủ ở kho gốc.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# Tier 1 — Self-Checklist: Outline & AM

> **Khi dùng:** Sau khi Writer làm xong Outline & AM, trước khi bắt đầu viết.
> **Số items:** 19 (P0 + O1–O18) = 1 Quality Gate + 11 Outline + 6 AM + 2 Supplement
> **Tick ở đâu:** Tracking Sheet 4 — "Tracking Outline & AM", cột N-AE (Outline items), AF-AH (Tier 2 slots).
> **Scoring:** Self Score /19 → Self %
> **Vị trí trong hệ 3-Tier:** Tier 1 = self-checklist bắt buộc mọi bài. Tier 2 = slot bật theo kick-off dự án. Tier 3 = audit/configuration (file riêng).

## Map item → wiki concept

| ID | Label | Wiki ref |
|---|---|---|
| P0 | Template Quality Gate | [[Article Methodology]] |
| O1 | Search Intent | [[Central Search Intent]] |
| O2 | Flow Main Content | [[Main Content]] |
| O3 | Flow Open-Close | [[Contextual Flow]] |
| O4 | Contextual Vector | [[Contextual Vector]] |
| O5 | Contextual Hierarchy | [[Contextual Hierarchy]] |
| O6a | Authority + Source Ctx | [[Source Context]] + [[VIP Sources]] |
| O6b | Attribute Filtration (RPP Scoring) | [[E-A-V Framework]] + [[Attribute Taxonomies]] |
| O7 | K2Q (Keyword→Question) | [[Question Generation]] (K2Q stub) |
| O8 | Coverage & Allocation | [[Topical Coverage]] + [[Centerpiece Annotation]] |
| O9 | RQ Decision | [[Representative Question]] |
| O10 | Contextual Flow (Transitions) | [[Contextual Flow]] |
| O11 | Contextual Structure | [[Article Methodology]] + [[Document Template]] |
| O12 | Layers & PQ Depth | [[Contextual Layers]] + [[PQ Pathway]] |
| O13 | Media & Format Justify | [[Visual Semantic Weight]] + [[Semantic Annotation]] |
| O14 | EAV Granularity | [[E-A-V Framework]] (Extreme Granularity) |
| O15 | Contextual Phrase / N-gram | [[Collocation]] + [[Lexical Field]] |
| O16 | Information Gain | [[Information Gain Score]] |
| O17 | Bridge to Supplement | [[Contextual Bridge]] |
| O18 | Supplement Quality | [[Supplementary Content]] |

---

### P0 — Template Quality Gate (Confirm V-Pass CL Writing + 9 items Content Quality Gate)
**Cách tick:**

1. Content phải pass V-Pass CL Writing (đã check 2 lần: Writer + SEO EX Verify) TRƯỚC khi onpage.
2. Cùng SEO EX với người verify → confirm V-Pass → tick.
3. Khác SEO EX → quick scan 5 phút (intro, L0, flow) → có lỗi thì flag, trả về Writer.
4. 9 items 🔄 dưới đây PHẢI pass ở bước Content (CL Writing / CL Outline) trước khi onpage. Chưa pass → trả về Writer/Outline, KHÔNG tiếp tục onpage.
5. Confirm P0 = pass → tick 1 lần, KHÔNG tick lại từng item 🔄 riêng.

**9 items Content Quality Gate:**

| Item | Check | Trùng |
|---|---|---|
| P2 | Search Intent Verify — verify intent SERP top 10 trước publish, bổ sung format nếu thiếu | 🔄O — O1 |
| P7 | Heading Hierarchy, Flow & Same Predicate — H2 phản chiếu H1, Open-Close, Same Predicate xuyên suốt | 🔄O — O3/O4/O5 |
| P10 | Introduction / General Summary — define entity câu đầu, Extractive + Abstractive, KW trong 100 chữ đầu | 🔄W — W1 |
| P15 | First Sentence (L0 Answer-First) — câu đầu H2/H3 answer trực tiếp, format match, EAV câu đầu | 🔄W — W2 |
| P17 | Citation & Evidence — citation SAU claim, nguồn uy tín, YMYL detail | 🔄W — W3 |
| P18 | Paragraph Structure & Discourse — 2-4 dòng, topic sentence đầu, anchor segments | 🔄W — W12 |
| P24 | Conclusion & CTA — recap 2-3 điểm, CTA funnel, keyword cuối | 🔄W |
| P27 | FAQ Structure — Answer-First, 40-60 từ (FAQ Schema bỏ khỏi yêu cầu 2026-07-13; FAQ content trên trang vẫn giữ) | 🔄W |
| P32 | Follow Outline & AM — content bám sát Outline, L0 mọi H2/H3, đủ AM requirements | 🔄W — W18 |

Ghi chú: P16 EAV Completeness đã nâng cấp thành P9 "EAV Density & Semantic Writing Quality" và GIỮ Ở Onpage CL (không nằm trong P0) vì cần verify + bổ sung trên CMS thực tế.

**Pass/Fail:**
✅ V-Pass + 9 items đạt → tick → onpage.
❌ Chưa V-Pass → trả về, không onpage.

---

### O1 — Search Intent · Nhóm: Outline
**Cách tick:** Phân tích SERP top 10 (incognito) và trả lời đủ 4 câu: intent chính? intent phụ? tình huống intent? outline dạng gì?

1. Xác định intent chính theo 7 loại: Informational / Navigational / Commercial / Transactional / Local / Do / Media.
2. Áp Framework 3Cs trên top 10: Content Type (blog/product/category/landing/video), Content Format (how-to/listicle/comparison/definition/review), Content Angle — loại chiếm đa số = outline phải follow; angle chọn theo Source Context nhưng nằm trong vùng mong đợi của SERP.
3. Xác định tình huống intent:
   - Dominant: 8-10/10 cùng 1 intent → outline theo intent đó.
   - Fractured: top 10 chia 2-3 intent → viết cho intent đa số; intent phụ address trong 1 section nhỏ hoặc page riêng.
   - Hybrid: 1 trang phải serve 2 intent đồng thời → bước 4.
4. Xử lý Hybrid (thường Informational + Commercial): Main Content (~75%) thoả intent chính, không aggressive sell; intent phụ lồng qua Source Context (case study, CTA nhẹ cuối section, section "Tại sao chọn brand" ở Supplement); internal link từ heading info → trang commercial riêng. Test: bỏ hết commercial elements mà Main Content vẫn đứng độc lập được — nếu trống rỗng là commercial ngụy trang, fail.
5. Check SERP Features: Featured Snippet → heading + L0 answer-first density cao; PAA → FAQ vào Supplement trả đúng câu PAA; Video Pack → cân nhắc video/section hình ảnh; Local Pack → NAP + khu vực; Product Carousel → specs, giá, review; AI Overview → structure rõ, EAV đầy đủ, câu trả lời trực tiếp.

**Ví dụ Đạt / Không Đạt:**
✅ SERP top 10 toàn product pages → outline theo commercial intent, có so sánh + CTA.
❌ SERP toàn product pages nhưng outline viết kiểu informational dài dòng, không có buying signal.

---

### O2 — Flow Main Content · Nhóm: Outline
**Cách tick:** Main Content = 9-10 heading đầu (~75% bài), phải chứa nội dung quan trọng nhất, thoả macro context. Kiểm tra predicate: đọc 9-10 heading đầu, hỏi "tất cả heading này giúp reader làm gì / biết gì?" — câu trả lời = predicate. Heading nào không phục vụ predicate → đẩy xuống Supplement hoặc loại bỏ.

**Ví dụ Đạt / Không Đạt:**
✅ H1: "Rượu vang đỏ là gì" → H2: Phân loại → H2: Lợi ích → H2: Cách chọn (cùng predicate "biết/chọn rượu").
❌ H2: Phân loại → H2: Lịch sử rượu vang thế giới (lệch predicate, nên đẩy sang supplement nếu cần).

---

### O3 — Flow Open-Close · Nhóm: Outline
**Cách tick:** Heading đầu tiên (Main Content) và heading cuối cùng (Supplement) phải kết nối — đồng nghĩa hoặc trái nghĩa. Xuyên suốt bài từ trên xuống phải smooth, khép kín (Contextual Connection tạo closure).

**Ví dụ Đạt / Không Đạt:**
✅ H2 đầu: "Lợi ích của rượu vang đỏ" → H2 cuối: "Rượu vang đỏ có hại không?" (trái nghĩa, khép kín).
❌ H2 đầu: "Lợi ích" → H2 cuối: "Địa chỉ mua rượu" (không liên kết ngữ nghĩa).

---

### O4 — Contextual Vector · Nhóm: Outline
**Cách tick:**

1. Đọc headings đầu → cuối phải thấy direction rõ, không random: tổng quan → chi tiết, nguyên nhân → giải pháp, lý thuyết → thực hành, cơ bản → nâng cao (hoặc biết → hiểu → áp dụng → lưu ý).
2. Concordance Rule: thứ tự H2 = thứ tự Introduction nhắc các chủ đề. Đổi thứ tự heading → phải sửa Introduction theo. Verify trước khi chuyển sang viết.
3. Thứ tự heading quyết định bởi Attribute Filtration (Prominence × Popularity × Relevance — cùng bộ filter với O8 nhưng output là SEQUENCE): cả 3 ✅ → đặt ĐẦU Main Content; 2 tiêu chí → sau trong Main hoặc đầu Supplement; thấp → cuối Supplement / FAQ.
4. Stay in the same predicate xuyên suốt.

Phân biệt với O8: O4 = heading nào ĐI TRƯỚC/SAU. O8 = heading nào VIẾT SÂU/LƯỚT.

**Ví dụ Đạt / Không Đạt:**
✅ "Tim mạch" (3✅) H2 đầu → "Chống oxy hóa" (2✅) H2 thứ hai → "Tương tác thuốc" (thấp) Supplement/FAQ cuối. Vector: lợi ích core → lợi ích phụ → cách dùng → lưu ý.
❌ Attribute LOW đặt H2 thứ 2 trước attribute HIGH (ngược priority); hoặc headings random không có direction.

---

### O5 — Contextual Hierarchy · Nhóm: Outline
**Cách tick:**

1. H2 phản chiếu H1 — từ ngữ + tông giọng liên quan trực tiếp; H1 là câu hỏi thì mỗi H2 trả lời một khía cạnh. Reflection Rule test: che H1, đọc H2 có đoán được H1 không?
2. Scope Containment Rule: H3 phải nằm trong scope của H2 cha, không rộng hơn.
3. Mỗi heading thêm giá trị riêng — 2 heading trùng ý thì gộp hoặc bỏ 1.
4. Không nhảy cấp (H1 → thẳng H3 bỏ qua H2).

**Ví dụ Đạt / Không Đạt:**
✅ H2: Lợi ích sức khỏe → H3: Cải thiện tim mạch → H3: Hỗ trợ tiêu hóa (chi tiết hóa H2).
❌ H2: Lợi ích sức khỏe → H3: Tổng quan về rượu vang (H3 rộng hơn H2, sai hierarchy).

---

### O6a — Authority + Source Ctx · Nhóm: Outline
**Cách tick:** Trước khi outline, tham khảo authority site trong ngành + URL top 1 của target keyword: họ cover gì, hành văn ra sao. Outline phải reflect các nội dung quan trọng đó, đồng thời lồng ghép Source Context của website mình.

**Ví dụ Đạt / Không Đạt:**
✅ Cửa hàng rượu online → outline có "Cách chọn rượu theo dịp" + "Rượu bán chạy nhất" (lồng commercial intent từ source context).
❌ Cửa hàng rượu nhưng outline toàn thông tin y khoa, không có heading thương mại nào.

---

### O6b — Attribute Filtration (Query Analysis + RPP Scoring) · Nhóm: Outline
**Cách tick:** Bước kiểm tra cuối trước khi chốt outline — không bỏ sót attribute quan trọng.

1. Export organic keywords (tool keyword research) cho: (a) top 1 URL của target keyword, (b) authority site, (c) 2-3 đối thủ trực tiếp.
2. Tìm queries/attributes đối thủ đang rank mà outline mình chưa cover.
3. Chấm RPP từng attribute: Prominence (cần để define đầy đủ Central Entity?), Popularity (search demand cao?), Relevance (kết nối trực tiếp Source Context?).
4. Quyết định bổ sung: 3/3 ✅ → BẮT BUỘC vào Main Content; 2/3 ✅ có Relevance → giữa/sau Main Content (đôi khi Supplement tuỳ context); 2/3 ✅ khác → cân nhắc Main hoặc Supplement; 1/3 ✅ → bỏ qua hoặc Supplement; 0/3 → không bổ sung.

**Ví dụ Đạt / Không Đạt:**
✅ Export queries top 1 → phát hiện attribute volume cao + liên quan trực tiếp → RPP 3/3 → bổ sung heading vào outline.
❌ Chốt outline mà không kiểm tra query network → bỏ sót attribute quan trọng mà đối thủ đang rank.

---

### O7 — K2Q (Keyword→Question) · Nhóm: Outline
**Cách tick:** Chuyển heading thành câu hỏi ngữ nghĩa khi phù hợp (đặc biệt khi user query dạng question). Câu hỏi ngắn gọn, đủ ý, không rườm rà; không giả sử — dùng kết quả tìm kiếm làm ngữ cảnh. Dùng đúng 4 loại: Definitional, Grouping, Comparative (Main Content), Boolean (H4/H5, Supplement).

**Ví dụ Đạt / Không Đạt:**
✅ "lợi ích rượu vang đỏ" → "Rượu vang đỏ có những lợi ích gì cho sức khỏe?"
❌ "lợi ích rượu vang đỏ" → "Có bao nhiêu lợi ích của rượu vang đỏ mà bạn cần biết?" (rườm rà, giả sử).

---

### O8 — Coverage & Allocation · Nhóm: Outline
**Cách tick:** O-AF quyết định heading NÀO xuất hiện; O8 quyết định heading đó đi SÂU bao nhiêu. Nguyên tắc: "Don't Dilute Main Context" — đi quá sâu attribute phụ làm loãng macro context.

1. Phân bổ 3 cấp trong Main Content:
   - HIGH (RPP 3/3, hoặc attribute trực tiếp phục vụ Source Context, hoặc topic reader quan tâm nhất): H2 + nhiều H3 (có thể H4), AM chi tiết nhất, centerpiece, có table/infographic/media.
   - MEDIUM (RPP 2/3, quan trọng nhưng không trọng tâm): cần có để define entity, không quá deep.
   - LOW (RPP 1/3 nhưng vẫn cần mention): H2 ngắn gọn, không H3, AM tối giản — hoặc đẩy Supplement.
2. Tỷ lệ: Main ~75% word count, Supplement ~25%.
3. Coverage Balance Check: lấy L0 mỗi H2 đặt cạnh nhau, đọc liền mạch thành summary hoàn chỉnh → cân bằng. Attribute chiếm quá nhiều so với importance → giảm.

Phân biệt với O4: O4 = heading nào ĐI TRƯỚC. O8 = heading nào VIẾT SÂU NHẤT.

**Ví dụ Đạt / Không Đạt:**
✅ Attribute HIGH → H2 + 3 H3; MEDIUM → H2 + 1 H3; LOW → 1 câu FAQ + link SCN. Main 7 heading (75%), Supplement 3 heading (25%), L0 check đọc liền mạch lạc.
❌ Attribute HIGH chỉ 1 H2 ngắn còn attribute LOW được 3 H3 dài (coverage lệch, dilute); Supplement chiếm 40% phá tỷ lệ; không cross-check SCN gây duplicate coverage với bài riêng.

---

### O9 — RQ Decision (Representative Question) · Nhóm: Outline
**Cách tick:** RQ = heading dạng câu hỏi (H2/H3) đóng vai trò contextual border giữa các phần lớn.

1. Xác định loại bài: Single-layer (1 macro context xuyên suốt) → 1 RQ bridge Main → Supplement. Multi-layer (2-3 macro context — comprehensive guide, pillar page) → 2-3 RQ làm border giữa mỗi macro. Đa phần bài (70-80%) là single-layer → chỉ cần 1 RQ.
2. Vị trí RQ: luôn ở điểm chuyển giữa 2 phần lớn, không đặt giữa section; format câu hỏi ("How...?", "Tại sao...?", "Làm thế nào...?"); RQ phải tóm gọn macro context phía sau nó.

**Ví dụ Đạt / Không Đạt:**
✅ Single-layer "20 lợi ích uống nước": RQ duy nhất "Uống nước như thế nào cho đúng cách?" bridge sang Supplement.
✅ Multi-layer guide: RQ1 chuyển definitional → advantages, RQ2 chuyển advantages → disadvantages/Supplement.
❌ Bài single-layer nhét 3 RQ → phá flow, bài bị chia nhỏ không cần thiết.

---

### O10 — Contextual Flow (Transitions giữa headings) · Nhóm: Outline
**Cách tick:** Giữa mỗi cặp heading liên tiếp phải có logical transition — không "jump" đột ngột.

1. 3 loại transition pattern: Causal (vấn đề/nguyên nhân → giải pháp/kết quả), Progressive (cơ bản/khái quát → nâng cao/chi tiết), Contrastive (tích cực → mặt ngược lại).
2. AM ghi cho mỗi heading: "Transition từ heading trước: [pattern] — [gợi ý câu chuyển tiếp]."
3. Headings cùng cluster (list benefits liên tiếp) → transition implicit, không cần ghi. Chỉ ghi rõ khi chuyển giữa 2 cluster hoặc 2 macro context.

**Ví dụ Đạt / Không Đạt:**
✅ "Improves Physical Performance" → "Increases Energy": cùng cluster, AM ghi "Transition: Progressive — từ whole body performance → cellular energy."
❌ "Lowest-Cost SMM" → "Reliable Reseller Support": nhảy pricing sang support không có connection; nên sắp Cost → Scalability → Support.

---

### O11 — Contextual Structure · Nhóm: AM
**Cách tick:** AM = Contextual Structure viết chi tiết cho TỪNG heading. Mỗi heading AM phải ghi rõ 5 mục: (1) Format content: paragraph / list / table / kết hợp; (2) Tone: definitive / exploratory / cautious; (3) Entities cần define hoặc mention; (4) Measurement/số liệu cần có; (5) Evidence/nguồn trích dẫn yêu cầu.

L1 Definition Decision Rule — 3 cấp cho attribute/entity trong heading:

1. Define sâu (2-3 câu): attribute có nghĩa chuyên ngành, scope khác nghĩa thông thường, hoặc YMYL cần set context chính xác. AM ghi: "Define [attribute] trong [context]: scope bao gồm..., phân biệt với...".
2. Set context ngắn (1 câu/clause): attribute phổ biến nhưng scope trong bài rộng/hẹp hơn reader mặc định. AM ghi: "Clarify scope [attribute]: bao gồm [X, Y, Z], không bao gồm [A, B]".
3. Skip define: vocabulary quen thuộc với target audience, self-explanatory. AM ghi: "Đi thẳng L0 answer-first → mechanism/evidence".

Test nhanh: 10 người trong target audience đọc heading đều hiểu CÙNG scope → skip. 3+ người hiểu KHÁC nhau → set context hoặc define sâu.

**Ví dụ Đạt / Không Đạt:**
✅ AM heading "Lợi ích tim mạch" (YMYL): "Define sâu: Physical performance = whole body function... Format: Definition → Evidence → Application. Tone: Definitive. Must include: 2 citations, % cụ thể."
✅ AM heading "Cost Reduction" (audience CTO): "Skip define. L0 answer-first + mechanism + evidence số liệu."
❌ AM ghi "Viết về lợi ích tim mạch, khoảng 300 từ" — không rõ format, tone, entities, evidence, define hay skip.

---

### O12 — Layers & PQ Depth · Nhóm: AM
**Cách tick:** AM phải specify Contextual Layers cho TỪNG heading. Layers = CÁI GÌ cần viết (độ sâu); PQ Pathway = CÁCH triển khai layers mượt (nhúng Preceding Questions tự nhiên trong paragraph).

1. L0 (Answer-First): BẮT BUỘC mọi H2/H3, 2-3 câu trực tiếp. AM thiếu L0 instruction cho bất kỳ heading nào → AM chưa đạt (đây là gate của item này).
2. Layers theo query type: L1 Concept/Definition (definitional query) · L2 Mechanism/Relationship · L3 Evidence/Standards (YMYL, Boolean) · L4-L6 Process/Exceptions/Decision tuỳ content type.
3. Pathway thông thường: L1 concept → L2 mechanism → L3 evidence → L4 process → L5-L6 decision. Không phải heading nào cũng cần đủ layer — số PQ theo độ sâu coverage: heading HIGH → 3-4 PQ; MEDIUM → 1-2 PQ; LOW → 0-1 PQ.

**Ví dụ Đạt / Không Đạt:**
✅ AM heading HIGH: L0 + 4 PQ, mỗi PQ map đúng layer (concept → mechanism → evidence → process), nhúng tự nhiên.
❌ AM chỉ ghi "Viết về cơ chế" (không PQ, không layer); L0 thiếu; hoặc PQ liệt kê robotic "Câu hỏi 1:... Câu hỏi 2:..." không embedded.

---

### O13 — Media & Format Justify · Nhóm: AM
**Cách tick:** AM ghi rõ: (1) Format content mỗi heading — paragraph / list / table; (2) Media cần thiết: image gì, bao nhiêu, specs; (3) Justify — lý do dùng media đó trong ngữ cảnh + tối ưu text xung quanh (alt text semantic, caption bổ sung context). Không chèn media không có logic.

**Ví dụ Đạt / Không Đạt:**
✅ "H2 So sánh → Table 5 cột: Loại | Đặc điểm | Giá | Phù hợp | Rating. Image: infographic so sánh, alt: [entity + comparison context]. Caption giải thích tiêu chí."
❌ AM ghi "Thêm bảng so sánh" — không rõ cột nào, image gì, alt text gì.

---

### O14 — EAV Granularity · Nhóm: AM
**Cách tick:** Theo nguyên tắc Extreme Granularity: mỗi câu trong AM phải yêu cầu writer cung cấp ít nhất 1 bộ E-A-V (Entity - Attribute - Value) cụ thể. Specify rõ: Entity nào define, Attribute nào cover, Value dạng gì (số, phần trăm, thời gian, range, so sánh). AM không bao giờ viết generic — phải ép câu hỏi cụ thể: "Bao nhiêu %? Thời gian? Bằng chứng gì? Nguồn nào?". Thứ tự: Prominent Attributes viết trước, Relevant Attributes tạo depth, Popular Attributes weave tự nhiên, Minor Attributes gom vào table.

**Ví dụ Đạt / Không Đạt:**
✅ "Nói rõ: polyphenol [E] ảnh hưởng cholesterol [A] giảm 10-15% [V] theo nguồn [tên, năm, cỡ mẫu]."
❌ "Nói về lợi ích sức khỏe của rượu vang" (không có E-A-V cụ thể nào).

---

### O15 — Contextual Phrase / N-gram · Nhóm: AM
**Cách tick:** AM ghi rõ các phrase cần đưa vào để tối ưu N-gram: phrase variations (đồng nghĩa), context terms (thuật ngữ chuyên ngành), semantic entities liên quan. Expert dùng unique words + combinations chuẩn hơn non-expert — ghi vào AM để writer follow đúng (micro semantics: word proximity, co-occurrences).

**Ví dụ Đạt / Không Đạt:**
✅ AM ghi: Phrase variations: "cải thiện / tăng cường / hỗ trợ / nâng cao". Context terms: "polyphenol, resveratrol, antioxidant". Entity liên quan: "HDL cholesterol, LDL cholesterol".
❌ Không liệt kê phrase nào → writer tự chọn từ → thiếu nhất quán.

---

### O16 — Information Gain · Nhóm: AM
**Cách tick:** Outline & AM phải tốt hơn đối thủ đang rank. So sánh với authority site + top 1 theo 6 tiêu chí, mỗi tiêu chí trả lời "đối thủ có gì → mình hơn bằng gì":

| Tiêu chí | Câu hỏi so sánh |
|---|---|
| 1. Coverage | Đối thủ cover bao nhiêu attributes? Mình cover hơn bao nhiêu? |
| 2. Depth | Đối thủ có evidence/số liệu không? Mình có evidence tốt hơn? |
| 3. Format | Đối thủ paragraph hay table/list? Format nào clear hơn? |
| 4. Unique angle | Mình có first-hand experience / unique data / case study thực tế? |
| 5. Contextual Layers | Đối thủ có L0 answer-first, L3 evidence không? |
| 6. Contextual Flow | Đối thủ có flow mạch lạc giữa sections không? |

Phải có information gap mà top 10 chưa cover. Không copy structure đối thủ. Tốt hơn có thể qua: text, image, visual design, video, hoặc depth. Ghi vào AM per heading (1-2 dòng hoặc comment): "Đối thủ [X]. Mình better bằng cách [Y]."

**Ví dụ Đạt / Không Đạt:**
✅ "Đối thủ list 5 lợi ích chung chung, không số liệu. AM yêu cầu: 8 lợi ích + evidence từng lợi ích + comparison table + flow mạch lạc hơn."
❌ AM copy structure đối thủ mà không cải thiện gì → không có information gain.

---

### O17 — Bridge to Supplement / RQ
**Cách tick:** Có Contextual Bridge hoặc RQ rõ ràng để chuyển Main → Supplement. Thường dạng "How..." (Grouping question). Ranh giới rõ nhưng transition mượt.

**Ví dụ Đạt / Không Đạt:**
✅ Sau 8 heading lợi ích (Main) → H2: "Uống rượu vang đỏ như thế nào cho đúng cách?" (bridge) → FAQ + Lưu ý (Supplement).
❌ Hết lợi ích → nhảy thẳng sang FAQ, không heading chuyển tiếp.

---

### O18 — Supplement Quality
**Cách tick:** Supplemental Content phải expand / bổ trợ Main Content — không "thêm cho đủ". Supplement củng cố macro context, mở rộng qua Boolean questions (H4/H5), kết nối SCN qua internal links có contextual bridge. Heading cuối: antonym/synonym của H1 → closure.

**Ví dụ Đạt / Không Đạt:**
✅ Supplement: FAQ trả lời concerns thực tế ("Uống bao nhiêu là đủ?", "Ai không nên uống?") + link sang bài SCN liên quan.
❌ Supplement: 3 câu FAQ random + "Liên hệ chúng tôi" → không bổ trợ main content.

---
