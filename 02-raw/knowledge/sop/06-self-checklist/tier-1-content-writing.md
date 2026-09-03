---
type: sop
tier: 1
phase: content-writing
last_updated: 2026-08-29
source_file: raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx
items_count: 21
tags: [sop, tier-1, content-writing, semantic-writing, anti-ai, self-checklist]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/tier-1-content-writing.md` ngày 2026-07-17.
> Bản chưng cất — đã lược evidence/theory; bản đầy đủ ở kho gốc.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# Tier 1 — Self-Checklist: Content Writing & Editing

> **Khi dùng:** Sau khi Writer viết xong draft, trước khi submit cho SEO EX Verify.
> **Số items:** 21 (W1–W21) = 7 Semantic + 6 Anti-AI + 4 QA + 1 Depth + 1 Tone (+ W20 Parent Heading, W21 Tone)
> **Tick ở đâu:** Tracking Sheet 5 — "Tracking Content Writing", cột L-AE.
> **Scoring:** Self Score /23 → Self %

## Map item → wiki concept

| ID | Label | Wiki ref |
|---|---|---|
| W1 | General Summary (Intro) — Extractive + Abstractive | [[Initial Contact Section]] + [[sources/general-summary-training-gtv]] |
| W2 | Subordinate Text & Modality | [[Subordinate Text Match]] + [[Modality]] |
| W3 | Dẫn chứng & Be Certain | [[Pegasus]] + [[VIP Sources]] |
| W4 | Số liệu & Ví dụ cụ thể | [[E-A-V Framework]] |
| W5 | Define Entity & Set Context | [[Central Entity]] + [[Context Sharpening]] |
| W6 | EAV Completeness | [[E-A-V Framework]] |
| W7 | Ngữ cảnh & Phrase Variation | [[Collocation]] + [[Synonym]] |
| W8 | Semantic Media & Visual Context | [[Visual Semantic Weight]] + [[Semantic Annotation]] |
| W9 | Writing Style per Intent | [[Central Search Intent]] |
| **W10** | **Nuke Words Filter** | **[[Nuke Words]]** |
| W11 | Câu đầy đủ & Natural Prose | [[Semantic HTML]] prose rules |
| W12 | Sentence Connection & Flow | [[Contextual Flow]] |
| **W13** | **Burstiness & Transitions** | **[[Burstiness]]** |
| W14 | Personality & Voice | [[Algorithmic Authorship]] + [[Authorship]] |
| W15 | Experience & Human Touch | [[Algorithmic Authorship]] (E-E-A-T Experience) |
| W16 | Featured Snippet | [[Featured Snippet]] + [[Information Density]] |
| W17 | Không lặp & Nhất quán | [[Pegasus]] (no conflict) |
| W18 | Follow Outline & AM | [[Article Methodology]] |
| W19 | Human Effort: Media & Evidence | [[VIP Sources]] |
| W20 | Parent Heading = General Summary | [[Initial Contact Section]] |
| W21 | Tone & Brand Voice | [[Brand Identity]] |

**Anti-AI cluster (W10–W15):** signature phân biệt content người viết vs AI-generated — Nuke Words Filter, Natural Prose, Burstiness, Personality, Experience.

---

## 🔴 G-BÀI — gate GEO per bài (bổ sung 2026-08-29)

Bốn item **kiến trúc passage** của `tier-1-geo.md` v2.0 (GE-16 · GE-17 · GE-18 · GE-19) là **gate cứng mỗi bài publish/refresh**: fail bất kỳ 1 item = trả về Writer, **không đưa sang onpage** — ngang hàng P0 gate L0 của W18. Không tạo checklist mới: mỗi GE map vào W-item sẵn có, chỉ thêm tiêu chí GEO. Chấm Bộ BÀI /12 đầy đủ (GE-16…GE-27) ở Tracking Sheet "GEO Checklist GE v2"; ở đây chỉ 4 item gate.

| GE | Tiêu chí ĐẠT (lăng kính GEO) | Map W | Ev |
|---|---|---|---|
| **GE-16** Mở đầu trang = câu trả lời | 100-150 từ đầu main content trả lời thẳng câu hỏi chính, **không storytelling intro** (ngoại lệ narrative niche — SERP-intent-conditional); Extractive + Abstractive, Concordance với H2; bài informational chính có **Key-Facts table** (3-6 fact quan trọng nhất) trên trang. Evidence: 38% citation AIO trích từ 100 từ đầu (Surfer 06/2026, C) · 44,2% từ 30% đầu trang (Indig 02/2026, B) | W1 (+ W20) | B |
| **GE-17** Heading = câu hỏi thật, 1 trang 1 câu hỏi | Heading bám đúng outline đã qua O7/O8 (K2Q khi query dạng câu hỏi; map fan-out theo **cluster ≤4**, không đuổi từng query); bài không phình ra ngoài outline "cho đủ coverage" — bài cover quá rộng → flag về Phase 2 đề xuất **tách page** (26-50% subtopic thắng 100%, B); **không chấm độ dài / số heading theo dải cố định** — độ dài theo loại node (quality node/pillar dài hơn leaf) + benchmark đối thủ (Vincent 29/08) | W18 | B |
| **GE-18** Câu đầu sau heading = câu trả lời | Subordinate Text theo 4 pattern (định nghĩa → "X là…" · how-to → "Để X, làm N bước…" · so sánh → verdict trước · yes/no → trả lời rồi mới điều kiện); câu trả lời trực tiếp **40-75 từ**, đủ E-A-V, không modality ở câu answer | W2 (+ W16) | B |
| **GE-19** Chunk tự đứng + heading hierarchy mạch lạc | Mỗi H2 cắt rời vẫn đủ Entity + context + claim; **không đại từ hồi chỉ xuyên section** ("như đã nói ở trên", "phương pháp này" mà antecedent ở section trước); mỗi khối ý <~200 từ (observational — Chrome), **không cap số từ section**; heading tổ tiên có nghĩa (không "Tổng quan"/"Kết luận" rỗng — máy gắn heading cha vào chunk như metadata, `includeAncestorHeadings`); mỗi câu tự đứng S-V-O | W12 + W17 + W11 | A/B |

**Chuẩn chunk GTV (chốt 29/08/2026, thay mọi ngưỡng "≤375 từ" cũ):** 1 heading = 1 facet · L0 40-75 từ · khối ý <~200 từ · mỗi câu tự đứng. Con số chunk theo token (128/800/500) thuộc 3 hệ khác nhau, chỉ để hiểu cơ chế — bảng canonical [[Audition Chunk]] §"3 con số chunk".

**Cách tick:** Writer tự chấm 4 GE cùng lúc với W-item map; SEO EX verify V-Pass kiểm lại 4 dòng này trước. Skill hỗ trợ: `semantic-content-writing` (quick gate G-BÀI) · `general-summary-introduction` (GE-16) · audit sâu 1 trang → `geo-content-optimization`.

---

### W1 — General Summary (Intro)

**Nhóm:** Semantic

1. Intro gồm 2 phần: Extractive (trích fact/definition chính xác từ bài) + Abstractive (tổng hợp thành summary bằng câu của mình, không copy nguyên).
2. H1 là câu hỏi → câu đầu tiên trả lời ngay (Answer-First). H1 không phải câu hỏi → vẫn ưu tiên định nghĩa Central Entity ngay câu đầu. KHÔNG mở đầu bằng lịch sử/background/'Trong thời đại...'.
3. YMYL → Safe Answer: trả lời thận trọng nhưng vẫn trực tiếp, kèm nguồn.
4. Define Central Entity ngay trong intro (hoặc recap ngắn nếu SCN đã define ở bài khác) + EAV đầy đủ.
5. Concordance: thứ tự mention chủ đề/attribute trong intro = thứ tự H2 trong bài; core attributes xuất hiện đủ trong intro.

Skill: `general-summary-introduction`.

---

### W2 — Subordinate Text & Modality

**Nhóm:** Semantic

1. Subordinate Text: câu đầu ngay sau mỗi heading phải match format heading — 'How to X' → 'Để X, bạn cần...'; 'What is X' → 'X là...'; 'Benefits of X' → 'X mang lại [số] lợi ích bao gồm...'; 'Why X' → 'X vì/bởi...'; heading số → trả lời đúng đề. KHÔNG mở bằng background/definition sai dạng (vi phạm L0 Answer-First).
2. Modality: present tense = fact có consensus; can/could/may = findings từ nghiên cứu; should = gợi ý cá nhân.
3. 'If' clause đặt SAU mệnh đề chính (Rule 12): action/answer trước, điều kiện sau.
4. Proper Word Sequence (Rule 33): thuộc tính quan trọng và context đặt đầu câu.

---

### W3 — Dẫn chứng & Be Certain

**Nhóm:** Semantic

1. Citation luôn đặt SAU claim: '[Claim cụ thể], theo [Source].' — không đặt trước, không đặt đầu đoạn.
2. Nguồn YMYL ghi đầy đủ: tên nghiên cứu (ngoặc kép), nhà nghiên cứu, tổ chức, năm, số mẫu (n=).
3. Be Certain: fact consensus → present tense dứt khoát; research-based → can/may/could kèm nguồn; gợi ý → should.
4. Loại bỏ hedge words ('có thể có khả năng', 'có lẽ', 'dường như', 'arguably', 'potentially') và fluff ('basically', 'essentially', 'in order to' → 'to', 'due to the fact that' → 'because'). Test: bỏ 1 từ mà câu vẫn đúng nghĩa → bỏ từ đó.

---

### W4 — Số liệu & Ví dụ cụ thể

**Nhóm:** Semantic

1. Số chính xác, không 'khoảng/xấp xỉ/ước chừng'. Dấu thập phân dùng dấu chấm (3.7). Dual measurement khi audience đa quốc gia ('70 lbs (31.75 kg)').
2. Danh từ số nhiều ('các loại', 'nhiều phương pháp') → BẮT BUỘC kèm ngay ≥3 ví dụ cụ thể.
3. Qualify instances: thêm bổ nghĩa ('5 triệu chứng nghiêm trọng', '3 phương pháp cho người mới') — không chỉ 'một số triệu chứng'.
4. Serial comma nhất quán từ list 3 items: VN 'A, B, và C' / EN 'A, B, and C'.

---

### W5 — Define Entity & Set Context

**Nhóm:** Semantic

Entity/attribute mới xuất hiện lần đầu → xử lý theo 3 cấp (nhất quán với L1 Definition Decision Rule trong AM — O9), không giả định reader biết sẵn:

1. Define sâu (2-3 câu): entity chuyên ngành, YMYL, scope khác nghĩa thông thường.
2. Set context ngắn (1 clause inline): entity phổ biến nhưng scope trong bài rộng/hẹp hơn reader nghĩ.
3. Mention + internal link: entity đã define đầy đủ trong bài khác thuộc SCN.

Từ nhiều nghĩa/nhiều ngữ cảnh → Narrow Down Context ngay đầu section (nền tảng nào, thời lượng, mục đích...).

---

### W6 — EAV Completeness

**Nhóm:** Semantic

1. EAV = Entity + Attribute + Value (đo lường được). Value phải lấy từ nguồn thật — không bịa số để "đủ EAV".
2. Mỗi paragraph chính (không tính câu chuyển tiếp/bridge) chứa ≥1 câu EAV đủ 3 thành phần.
3. L0 của mỗi H2/H3 có ≥1 câu EAV để Google/AI trích xuất được.

---

### W7 — Ngữ cảnh & Phrase Variation

**Nhóm:** Semantic

1. Mỗi câu đạt 5C: Concise, Coherent, Confident, Contextual, Clear.
2. Word Proximity: thuật ngữ liên quan về nghĩa xuất hiện trong cùng 2-3 câu, không tách xa.
3. Phrase Variation: không dùng cùng 1 từ lặp >3 lần liên tiếp — dùng đồng nghĩa.
4. Central Entity xuất hiện đều mỗi 2-3 paragraph. Micro terms (thuật ngữ riêng của section) giữ local trong section đó, không rải khắp bài. (Tối ưu N-gram/semantic keywords → team SEO Onpage.)

---

### W8 — Semantic Media & Visual Context

**Nhóm:** Semantic

1. Hình ảnh/video minh họa ĐÚNG nội dung heading, không phải ảnh trang trí.
2. Theo dạng content: how-to → ảnh step-by-step đánh số + note text từng bước; comparison → side-by-side/bảng visual; process → diagram/flowchart có label; số liệu → infographic/chart; đoạn khó hiểu → BẮT BUỘC infographic hoặc diagram.
3. Chất lượng: tự tạo hoặc AI generate đúng ngữ cảnh — KHÔNG stock photo generic; resolution rõ; screenshot phải highlight/annotate.
4. Metadata: alt text mô tả cụ thể (không 'hình ảnh minh họa'); caption bổ sung context; file name semantic ('quy-trinh-audit-seo-5-buoc.webp').
5. Heading cần custom visual mà writer không tự tạo → ghi note rõ cho team SEO/Design, không để heading trống media không note.

---

### W9 — Writing Style per Intent

**Nhóm:** Semantic

Văn phong theo DẠNG content/search intent của từng bài (KHÁC W21 Brand Voice toàn website):

1. How-to → expert instructive: câu ngắn, từ hướng dẫn ('bạn cần', 'bước tiếp theo', 'tránh làm...').
2. Review → giọng trải nghiệm cá nhân, có cảm xúc và quan điểm.
3. Listicle → scannable: bullet rõ, headword bold, item gọn.
4. Informational → progressive: đơn giản → phức tạp, có analogy.
5. Comparison → neutral, data-driven, có bảng + verdict rõ cuối bài.

Quy trình: xác định intent (AM chỉ định) → AI draft → edit câu cú theo intent → read aloud test (nghe giống expert hay giống AI đọc bài?).

---

### W10 — Nuke Words Filter

**Nhóm:** Anti-AI

1. Tier 1 (CẤM tuyệt đối — 0 lần/bài): EN 'delve into', 'at its core', 'innovative', 'cutting-edge', 'leverage', 'plays a crucial role', 'revolutionize', 'seamless integration', 'game-changing', 'transformative'; VN 'đóng vai trò quan trọng', 'đi sâu vào', 'cách mạng hóa', 'tận dụng', 'tích hợp liền mạch'.
2. CẤM mở đầu 'In today's...' / 'Trong thời đại số...'. CẤM kết bài 'In conclusion...' / 'Tóm lại...'.
3. Tier 2 (tối đa 1 lần/từ/bài): 'crucial', 'essential', 'comprehensive', 'robust', 'furthermore', 'moreover', 'however', 'therefore', 'significantly'.
4. Thay bằng từ tự nhiên, không chỉ xóa: 'innovative' → 'mới', 'leverage' → 'dùng', 'comprehensive' → 'chi tiết'. Từ nghe như 'AI viết' → thay bằng từ đời thường.

Danh sách đầy đủ Nuke Words EN + VN: xem Checklist [LINK Nuke Words List].

---

### W11 — Câu đầy đủ & Natural Prose

**Nhóm:** Anti-AI

1. Mọi câu đủ chủ ngữ - vị ngữ - bổ ngữ; đọc riêng 1 câu phải hiểu được nghĩa, không cần câu trước/sau.
2. KHÔNG fragment cộc lốc ('Nước. Quan trọng. Uống đủ.') — pattern AI rõ nhất.
3. Không hy sinh sự rõ ràng vì ngắn gọn: ý cần 25 từ thì viết đủ 25 từ; câu ngắn thiếu ngữ cảnh tệ hơn câu dài rõ ràng.
4. Test: đọc to từng câu riêng lẻ — câu nào cộc lốc/thiếu ý → viết lại. Áp dụng cả cho mô tả trong checklist, AM, tài liệu nội bộ.

---

### W12 — Sentence Connection & Flow

**Nhóm:** Anti-AI

1. Kết nối 3 cấp:
   - Cấp 1 — trong paragraph: câu A setup → câu B build on A → câu C kết luận/dẫn tiếp. Không đặt câu cạnh nhau không liên quan.
   - Cấp 2 — giữa paragraph trong section: paragraph sau build on hoặc phản biện paragraph trước.
   - Cấp 3 — giữa section: paragraph cuối section setup context cho section sau (hint topic tiếp theo), HOẶC heading sau naturally follows. Không kết bằng dead-end statement.
2. Transition Repetition Check: Ctrl+F đếm transition đầu câu ('Với', 'Về', 'Ngoài ra', 'Tuy nhiên', 'Đối với'...) — từ nào xuất hiện ≥4 lần/bài → đa dạng hóa. Thay thế: entity-first ('EB-5 cho phép...'), contrast ('Khác với EB-5,...'), câu hỏi ngầm, hoặc xóa transition khi câu tự đứng được.

---

### W13 — Burstiness & Transitions

**Nhóm:** Anti-AI

1. Burstiness: mix 3 loại câu mỗi paragraph — ngắn (3-8 từ, nhấn mạnh), trung bình (10-15 từ), dài (20-30 từ, giải thích). Mỗi paragraph ≥1 câu ≥20 từ + 1-2 câu ngắn. KHÔNG để mọi câu cùng độ dài 12-15 từ.
2. Transitions: tối đa 1 formal transition mỗi 2-3 câu. Thay formal → tự nhiên: EN Furthermore → Also/Plus, However → But/Still, Therefore → So; VN Hơn nữa → Và/Cũng, Tuy nhiên → Nhưng/Dù vậy, Tóm lại → Vậy nên. Paragraph có 'Furthermore... Moreover... Additionally...' → viết lại ngay.
3. Burstiness cho list: 5+ items cùng cấu trúc ngữ pháp + cùng độ dài → break 1-2 items (đảo cấu trúc, dash/parenthetical, 1 item ngắn/dài hẳn).

---

### W14 — Personality & Voice

**Nhóm:** Anti-AI

1. Contractions tự nhiên (EN: don't, it's; VN: từ rút gọn khẩu ngữ phù hợp tone).
2. Direct address: 'bạn'/'you'; 'tôi'/'I' cho kinh nghiệm cá nhân; tránh 'chúng tôi' trừ khi đại diện tổ chức.
3. 1-2 câu hỏi tu từ mỗi section để tạo engagement và break pattern.
4. Không lặp cấu trúc câu liên tiếp ('Nước giúp... Nước hỗ trợ... Nước cải thiện...') — đổi chủ ngữ, cấu trúc, độ dài.
5. Paragraph lengths đa dạng (1-2 câu nhấn mạnh / 3-4 câu giải thích / 5-6 câu chi tiết). Specific examples thay generic claims.

---

### W15 — Experience & Human Touch

**Nhóm:** Anti-AI

1. First-Hand Experience Signals (5 patterns review): (1) Temporal Markers ('Sau 45 ngày sử dụng...'); (2) Specific Observations ngoài specs chính thức; (3) Test Methodology (mô tả cách test); (4) Comparative Experience (so với sản phẩm đã dùng); (5) Usage Context (điều kiện cụ thể).
2. Transparent Limitations: thành thật về hạn chế ('không phù hợp nếu...', 'chưa test trong điều kiện...').
3. Service page / YMYL thêm 3 patterns: (6) Practitioner Insight ('Trong X năm tư vấn, chúng tôi nhận thấy...'); (7) Client Voice ('Câu hỏi phổ biến nhất từ khách hàng...'); (8) Behind-the-scenes (context không có trên Google: timeline thực tế, rủi ro ít ai đề cập, so sánh insider).
4. Ngưỡng YMYL/service: bài 2,000+ từ phải có ≥3 instances dạng (6)/(7)/(8). Nếu = 0 → FAIL W15.

---

### W16 — Featured Snippet

**Nhóm:** QA

1. Check SERP target keyword TRƯỚC khi viết: FS hiện tại dạng gì (paragraph/list/table), độ dài, information density. L0 phải có density bằng hoặc cao hơn FS.
2. So sánh với top 1 (chỉ Main Content, không áp cho Supplement): mỗi heading cần nhiều EAV hơn, evidence cụ thể hơn, format rõ hơn nội dung tương ứng ở top 1.
3. Format theo dạng FS: paragraph = 40 words / 320 characters; list = 3-8 items numbered/bullet; table = headers rõ + data cụ thể.
4. Bold phần TRẢ LỜI (giá trị/định nghĩa), KHÔNG bold keyword.
5. Sibling Context: câu trước/sau L0 hỗ trợ ngữ cảnh cho câu trả lời.

---

### W17 — Không lặp & Nhất quán

**Nhóm:** QA

1. Entity/concept đã define ở section trước → không define lại, chỉ recap 1 câu ('Như đã đề cập,...'). SCN đã define ở bài khác → recap ngắn + internal link.
2. Số liệu nhất quán: cùng metric giữ cùng giá trị trong bài VÀ xuyên các bài trong SCN.
3. Không mâu thuẫn nội bộ: intro nói '5 lợi ích' → body đúng 5; section A và B không nói ngược nhau về cùng claim (trừ khi context khác được giải thích rõ). (Rule 35.)

---

### W18 — Follow Outline & AM

**Nhóm:** QA

1. Follow đúng heading structure (H1-H2-H3-H4) từ Outline. KHÔNG tự thêm/bỏ heading.
2. **L0 là P0 gate:** mọi H2/H3 bắt đầu bằng L0 (2-3 câu trả lời trực tiếp, 40-60 words). Bất kỳ heading nào thiếu L0 → bài KHÔNG pass W18 dù đúng mọi thứ khác. Check nhanh: đọc 2-3 câu đầu sau mỗi heading — chưa thấy answer trực tiếp → fail.
3. Viết đúng layers AM specify (L0-L6). PQ nhúng đúng vị trí, đúng pathway (concept → mechanism → application → comparison → action). AM yêu cầu table 5 cột → có table đúng 5 cột; AM cần 3 PQ → có 3 PQ.
4. Meta-check: đọc lướt toàn bài lần cuối — heading order logic, không thiếu section, không thừa nội dung ngoài AM.

---

### W19 — Human Effort: Media & Evidence

**Nhóm:** QA

1. Media effort: image/video semantic relevant — không stock generic; alt text cụ thể; caption bổ sung.
2. Evidence effort: số liệu tự research, screenshots thực; mỗi claim quan trọng traceable.
3. Contextual effort: mỗi section add unique value, không chỉ tóm tắt nguồn khác.
4. Experience: có trải nghiệm/kinh nghiệm/nhận xét từ người viết thêm vào.
5. Note cho SEO team nếu cần custom visual (infographic, diagram) hoặc function (calculator, quiz).

---

### W20 — Parent Heading = General Summary

**Nhóm:** Depth

1. H2 có nhiều H3 → đoạn ngay sau H2 (trước H3 đầu tiên) PHẢI là general summary của các child headings. Tương tự H3 có nhiều H4.
2. Cấu trúc: L0 của parent heading (2-3 câu trả lời trực tiếp) + 1-2 câu preview sub-topics đúng thứ tự child headings (concordance).
3. KHÔNG nhảy thẳng vào H3/H4 đầu tiên khi chưa có nội dung tổng quan. KHÔNG viết quá dài ở parent — chi tiết để child headings.
4. Test: đọc đoạn ngay sau H2 — reader biết section nói về gì và có bao nhiêu phần không? Không → thiếu general summary.

---

### W21 — Tone & Brand Voice

**Nhóm:** Brand

1. Đọc brand guideline của client (hoặc nội bộ) TRƯỚC khi viết: audience (B2B/B2C, expert/beginner), tone (formal/casual/casual expert), xưng hô ('bạn', 'mình', 'quý khách'). Có style profile → bật và follow.
2. Nhất quán xuyên suốt: xưng hô, mức chuyên môn, độ thân thiện đồng bộ từ đầu đến cuối — không đoạn 1 formal 'quý khách', đoạn 3 casual 'bạn ơi'.
3. Test: đọc 3 đoạn bất kỳ (intro, giữa, cuối) — cảm giác như cùng 1 người viết. Đoạn 'khác giọng' → chỉnh. Chú ý section do nhiều người viết hoặc AI hỗ trợ.

---
