---
type: sop
phase: qc-editing
last_updated: 2026-07-19
source_file: raw/_ingested/Quy trình SEO PSP - All In One/3. Quy trình Content _ Production/AI Content checklist Topical Authority/3. Checklist đảm bảo chất lượng nội dung Content AI - Quality Content AI SEO Checklist.xlsx (Sheet 2 — 21 lỗi gốc)
supporting_sources:
  - skills/humanizer/SKILL.md (v3.1 — pattern catalog, detection landscape 2026)
  - skills/semantic-content-writing/SKILL.md (v2.0.2 — 60 rules, Language Discipline)
items_count: 28
related_wiki:
  - "[[Contextual Coverage]]"
  - "[[Information Density]]"
  - "[[Cost of Retrieval]]"
  - "[[Subordinate Text Match]]"
  - "[[Nuke Words]]"
  - "[[General Summary]]"
tags: [sop, self-checklist, ai-errors, qc, editing]
---

# Common AI Errors — Catalog lỗi AI content khi QC/Edit

> **Ai dùng / khi nào:** SEO EX / Lead khi QC hoặc edit bài do AI sinh (Phase 2-3 của `quality-content-ai.md`), và Writer khi self-edit trước submit.
> **Nguồn gốc:** Sheet 2 xlsx "Checklist các lỗi AI thường gặp" — 21 lỗi gốc (AE-01…AE-21, giữ nguyên tên gốc trong ngoặc kép) + 7 lỗi bổ sung quan sát từ skill `humanizer` v3.1 và convention AM v2.0 (AE-22…AE-28).
> **Cách dùng:** Mỗi lỗi có 4 cột thông tin — nhận diện (dấu hiệu cụ thể, grep-able khi có thể), cách sửa, route (skill / rule / tier-1 item xử lý triệt để). Cuối file: bảng map lỗi → phase pipeline hay phát sinh nhất.

---

## Nhóm A — Lỗi cấu trúc & coverage (AE-01 → AE-05)

### AE-01 — "Contextual Coverage Dillute (pha loãng contextual coverage)"
- **Nhận diện:** Đoạn dài dòng lệch khỏi hướng heading; nội dung lặp lại thứ đã/sẽ trả lời kỹ hơn ở heading khác hoặc bài khác trong SCN. Test: che heading, đọc đoạn — có đoán được heading không?
- **Cách sửa:** Cắt phần lệch trọng tâm; nếu cần nhắc chéo → 1 câu [[Contextual Bridge]] + internal link, không triển khai lại. Chỉ giữ khi nó làm heading SÂU hơn hoặc dẫn dắt chủ đề.
- **Route:** → O2 (predicate), O8 (allocation), W7 (macro/micro term); [[Contextual Coverage]].

### AE-02 — Word count sai trọng số Main/Supplemental
- **Nhận diện:** Supplemental heading dài hơn heading Main quan trọng; 9-10 heading đầu không phải phần nặng nhất bài; một heading phụ "phình" khiến Google/user tưởng đó là trọng tâm.
- **Cách sửa:** Xác định Main vs Supplemental trước, rồi phân bổ lại: heading HIGH viết sâu, heading LOW rút còn L0 + 1-2 câu. Có thể dùng AI nén lại cho cô đọng.
- **Route:** → O8 (Coverage & Allocation — tỷ lệ Main ~75%).

### AE-03 — Không quy định word count per section
- **Nhận diện:** AM/outline không có số từ mục tiêu per heading → AI sinh mỗi section một kiểu, chỗ 800 từ chỗ 50 từ.
- **Cách sửa:** Quy định word ladder ngay trong AM: H3 ~120-150 từ, H2 (lead) ~200 từ, YMYL +20-30% (AM v2.0 slim block).
- **Route:** Skill `semantic-outline-methodology` (word ladder); → O8.

### AE-04 — "Information density" thấp
- **Nhận diện:** Đoạn nhiều chữ nhưng ít fact — đếm EAV: dưới ~3 EAV đầy đủ / 100 từ ở Main Content là cờ đỏ. Câu generic kiểu "X mang lại nhiều lợi ích đáng kể".
- **Cách sửa:** Nén chữ, giữ fact: mỗi câu cõng ít nhất 1 thông tin đo được. Chữ càng ít mà vẫn thoả intent = vừa tối ưu [[Cost of Retrieval]] vừa tốt cho user.
- **Route:** → W6 (EAV Completeness); SCW information density ≥3 EAV/100 từ; [[Information Density]].

### AE-05 — "Contextual Layer + Preceding Question" không phù hợp
- **Nhận diện:** Bài dài nhưng nông — không xác định Representative Question, các đoạn không trả lời chuỗi PQ nào; hoặc PQ liệt kê robotic "Câu hỏi 1:… Câu hỏi 2:…".
- **Cách sửa:** Xác định RQ → chuỗi PQ per heading (L1 concept → L2 mechanism → L3 evidence → L4 process), nhúng tự nhiên trong paragraph. Chỉ thêm nội dung khi nó đào sâu heading mà không mất context.
- **Route:** → O9 (RQ Decision), O12 (Layers & PQ Depth); [[Contextual Layers]], [[Representative Question]].

---

## Nhóm B — Lỗi trình bày & trả lời (AE-06 → AE-11)

### AE-06 — "Bold/Highlight only the answer"
- **Nhận diện:** AI bôi đậm keyword semantic rải rác ("bạ đâu in đậm đó") thay vì bôi đậm CÂU TRẢ LỜI.
- **Cách sửa:** Chỉ bold phần trả lời/giá trị/định nghĩa ("Chim cánh cụt là **loài chim không bay sống ở biển**"), bỏ bold keyword lặp.
- **Route:** → W16 (Featured Snippet — bold answer, không bold keyword).

### AE-07 — "Tối ưu Subordinate heading text" sai
- **Nhận diện:** Heading và câu đầu không phải cặp Question-Answer tốt: "Cách chọn X" mà mở bằng định nghĩa; sai format, sai từ loại (heading hỏi danh từ, answer trả động từ), trả lời loãng.
- **Cách sửa:** Câu đầu sau heading match đúng format heading ('How to' → 'Để…', 'What is' → 'X là…'), cô đọng thông tin, đúng danh/động/tính từ cần trả lời.
- **Route:** → W2 (Subordinate Text & Modality); [[Subordinate Text Match]].

### AE-08 — "Hiểu và làm Content có Tâm với User / Target Audience Brand" — content không đặt mình vào user
- **Nhận diện:** Nội dung viết cho search engine, không trả lời được "user search keyword này cần gì, mình có đáp ứng nhanh - chính xác - trải nghiệm tốt không?".
- **Cách sửa:** Put yourself in the customer shoes: rà từng section theo insight của Search Query; phần không phục vụ user nào → cắt.
- **Route:** → O1 (intent), W9 (style per intent); mọi thứ tối ưu phải semantically.

### AE-09 — Content dài không cần thiết (short content đang ưu thế)
- **Nhận diện:** Bài phồng vì "cho đủ word count đối thủ"; đoạn giải thích vòng vo trước khi vào việc.
- **Cách sửa:** Ưu tiên giá trị + xúc tích; độ dài do coverage cần thiết quyết định, không do target word count.
- **Route:** → AE-04 (density) + QA-12 lưu ý; [[Cost of Retrieval]].

### AE-10 — Không có lý do tồn tại vs AI search / short video
- **Nhận diện:** Không trả lời được: "Tại sao user phải đọc content của bạn mà không hỏi AI hoặc coi short video?" — bài chỉ tổng hợp lại thứ đã có.
- **Cách sửa:** Bơm thứ AI answer không có: unique data, trải nghiệm thật, function tương tác, verdict rõ ràng.
- **Route:** → O16 (Information Gain), W15 (Experience), QA-05/QA-17 trong `quality-content-ai.md`; [[Information Gain Score]].

### AE-11 — Media không semantic
- **Nhận diện:** Chỗ user cần ảnh/video minh hoạ thì trống; ảnh có thì là stock generic không thể hiện nội dung.
- **Cách sửa:** Đặt mình vào user — chỗ nào đọc thấy "cần hình" thì chèn; ảnh phải semantically thể hiện nội dung (design Canva nếu cần), alt/caption cụ thể.
- **Route:** → O13 (Media & Format Justify), W8 (Semantic Media); [[Visual Semantic Weight]].

---

## Nhóm C — Lỗi văn phong & ngôn ngữ (AE-12 → AE-16)

### AE-12 — "Humanize content" chưa làm / làm hời hợt
- **Nhận diện:** Tone giảng bài đều đều; contextual bridge dài dòng trang trọng; câu AI dài dễ đoán; còn AI words.
- **Cách sửa:** Conversation tone nhiều hơn; bridge viết ngắn + khẩu ngữ; ngắt câu dài thành ngắn; loại AI words. Chạy humanize pass chuẩn (2-prompt audit + Humanness Score).
- **Route:** Skill `humanizer` (pattern catalog 1-38); → W10-W14; QA-14.

### AE-13 — "Coi cấu trúc câu, chính tả"
- **Nhận diện:** Sai dấu `:` `,` `.`; sai the/a/an (bài EN); lỗi chính tả VN thường gặp (chia sẽ/chia sẻ, sẩy ra/xảy ra); serial comma bất nhất.
- **Cách sửa:** Proofread pass riêng sau humanize; check serial comma nhất quán "A, B, và C".
- **Route:** → W4 (serial comma), W11 (câu đầy đủ); humanizer Vietnamese region rules.

### AE-14 — "Hiểu từ ngữ mình đang dùng" — sai register theo audience
- **Nhận diện:** Từ chuyên ngành cho audience phổ thông (hoặc ngược lại — giải thích vỡ lòng cho expert); cùng bài lúc "quý khách" lúc "bạn ơi".
- **Cách sửa:** Chốt audience tier trước (B2C Mass / B2B Expert / Premium / Children…) → chọn vốn từ + xưng hô theo tier, giữ nhất quán.
- **Route:** Humanizer D1-D4 + audience proximity matrix; → W21 (Tone & Brand Voice).

### AE-15 — Dùng sai bullet vs numbered list
- **Nhận diện:** Quy trình có thứ tự viết bullet; danh sách không thứ tự lại đánh số; list 5+ items cùng cấu trúc ngữ pháp đều tăm tắp (AI pattern).
- **Cách sửa:** Numbered = có trình tự/xếp hạng; bullet = ngang hàng. Break cấu trúc 1-2 items cho tự nhiên (burstiness cho list).
- **Route:** → W13 mục 3 (burstiness cho list); format spec trong AM (O13).

### AE-16 — Nội dung không ăn khớp promise (methods ≠ tips)
- **Nhận diện:** Heading/intro hứa "6 best methods" nhưng body liệt kê tips, action, lưu ý lẫn lộn; số lượng hứa ≠ số lượng giao (intro nói 5, body có 7).
- **Cách sửa:** Đọc hiểu mình đang viết gì — đã nói methods thì mọi item phải LÀ method; đồng bộ số lượng + từ loại giữa promise và delivery.
- **Route:** → W17 (nhất quán), W4 (qualify instances); SCW Q&A word-order consistency.

---

## Nhóm D — Lỗi retrieval & khung bài (AE-17 → AE-21)

### AE-17 — "Tối ưu cost of retrieval ở content" — định nghĩa mở bằng Root attribute
- **Nhận diện:** Câu định nghĩa đầu section mở bằng Root attribute generic mà class nào cũng có ("X là tập hợp kỹ thuật tối ưu…") thay vì thuộc tính Unique/Prominent; đoạn cần định nghĩa từ đầu thì lại không có.
- **Cách sửa:** Xác định đoạn nào cần định nghĩa ngay đầu; viết theo thứ tự Unique/Prominent → Root → Rare; phân tích SERP để định nghĩa tốt hơn đối thủ mà vẫn giữ contextual coverage.
- **Route:** SCW Unique-first intra-block (Step 2 + anti-pattern list); → O11 (L1 Definition Decision); [[Cost of Retrieval]], [[Audition Chunk]].

### AE-18 — "Outro / Conclusion hoặc TLDR" viết kiểu AI
- **Nhận diện:** Kết bài "Tóm lại,…" sáo rỗng do AI viết full; recap không đúng trọng điểm bài; hoặc viết conclusion cho có.
- **Cách sửa:** (1) Không bắt buộc phải có outro. (2) Nếu viết → extractive summary: recap highlight thật của bài. (3) Người tự đọc bài xong viết lại, hoặc ít nhất dùng prompt riêng cho conclusion — không lấy nguyên output AI.
- **Route:** → P24 (Conclusion & CTA — P0 gate tier-1); W10 (cấm "In conclusion/Tóm lại" mở kết).

### AE-19 — "Các câu chuyển nội dung, câu kết thúc mục heading" vô nghĩa
- **Nhận diện:** Cuối mỗi heading có 1-2 câu filler lặp ý hoặc dead-end ("Đó là những lợi ích của X."); không có bridge sang heading sau.
- **Cách sửa:** Edit cuối mỗi heading: xoá filler, thay bằng câu setup context cho section tiếp theo (Sentence Connection cấp 3).
- **Route:** → W12 (cấp 3 + Transition Repetition Check), O10 (transition pattern trong AM).

### AE-20 — "Introduction content" không phải General Summary
- **Nhận diện:** Intro mở bằng background/lịch sử/"Trong thời đại…"; không define Central Entity câu đầu; câu mở không match dạng H1 (H1 câu hỏi mà câu đầu không trả lời); thứ tự mention ≠ thứ tự H2.
- **Cách sửa:** Viết General Summary: Extractive (facts đắt nhất của bài) + Abstractive (câu tổng hợp), answer-first theo H1, Concordance với H2 order. Intro chính thức viết CUỐI, sau khi bài xong.
- **Route:** → W1; skill `general-summary-introduction`; [[General Summary]], [[Initial Contact Section]].

### AE-21 — "Website cần có tính năng phù hợp" nhưng trang chỉ có text
- **Nhận diện:** Query/intent đòi function (tính toán, so sánh, lọc, tra cứu) nhưng trang thuần văn bản; hoặc có function mà lỗi/không mobile.
- **Cách sửa:** Map function theo intent từ research, tích hợp interactive element đạt chuẩn chất lượng.
- **Route:** → QA-06, QA-17, QA-20 (`quality-content-ai.md`); [[Website Functions]].

---

## Nhóm E — Lỗi bổ sung 2026 (AE-22 → AE-28, chưa có trong 21 lỗi gốc)

### AE-22 — Planner language trong Ý chính AM
- **Nhận diện:** AI sinh AM mà mục "Ý chính" viết kiểu kế hoạch ("Phần này sẽ đề cập…", "Mục tiêu của section là…") hoặc ngược lại — viết sẵn content hoàn chỉnh thay writer.
- **Cách sửa:** Ý chính = MỘT flow đánh số 1., 2., 3. chỉ dẫn writer viết gì theo trình tự nào + facts gợi ý — không phải mô tả kế hoạch, không phải content thành phẩm.
- **Route:** AM v2.0 convention (skill `semantic-outline-methodology`); → O11, O12.

### AE-23 — Markdown table trong AM render
- **Nhận diện:** AI xuất block AM dạng bảng markdown (cột Format/Tone/Entities…) thay vì block 6 mục paragraph + list per heading.
- **Cách sửa:** Render lại đúng block 6 mục: Format / Subordinate Text / Ý chính (flow) / Media / Phrase / Lưu ý — paragraph + list, không table.
- **Route:** AM v2.0 (skill `semantic-outline-methodology` — Input Contract của `semantic-content-writing`).

### AE-24 — Code-switch tiếng Anh giữa câu tiếng Việt
- **Nhận diện:** Verb/noun tiếng Anh chen vào khi có từ Việt tương đương rõ ("leverage insight này để improve content"); mix Vietnamese verb + English noun vô cớ.
- **Cách sửa:** 2 phép thử: (1) người trong nghề hiểu bản Việt hoá không? Có → Việt hoá. (2) Term có trong whitelist technical của project không? Có → giữ EN, lần đầu kèm format bilingual `EN (nghĩa Việt)`.
- **Route:** SCW Language Discipline (áp cứng); whitelist ở brand skill / `source-context.md`.

### AE-25 — Hard artifacts sót lại từ AI/chatbot
- **Nhận diện:** Grep được ngay: `utm_source=chatgpt.com`, `oaicite`, `turn0search0`, ` :contentReference`, curly quotes lạc kiểu, câu chatbot ("Great question!", "Certainly! Here is…"), placeholder `[tên công ty]`.
- **Cách sửa:** Grep + xoá toàn bộ artifacts; đọc lại đoạn quanh vị trí xoá để vá flow.
- **Route:** Humanizer pattern catalog (hard artifacts) — bước scan bắt buộc trước publish.

### AE-26 — Cụm style AI: em-dash overuse, rule of three, negative parallelism, inflated symbolism
- **Nhận diện:** Mật độ "—" cao bất thường; bộ ba lặp khắp bài ("nhanh, gọn, và hiệu quả"); "Không chỉ X… mà còn Y"; "đánh dấu bước ngoặt", "minh chứng cho…". Từng cái đơn lẻ chưa kết luận được — mật độ + co-occurrence mới là tell.
- **Cách sửa:** Sửa theo mật độ: giảm em-dash, phá bộ ba (2 hoặc 4 items), viết thẳng claim thay vì negative parallelism, hạ symbolism về fact.
- **Route:** Humanizer patterns (1, 9, 10, 14 + meta-rules); → W13, W14.

### AE-27 — Vague attributions
- **Nhận diện:** "Các chuyên gia cho rằng…", "Nhiều nghiên cứu chỉ ra…", "Industry observers note…" — claim gắn nguồn mơ hồ không trace được.
- **Cách sửa:** Hoặc nêu nguồn thật (tên nghiên cứu, tổ chức, năm, n=) đặt SAU claim, hoặc bỏ lớp attribution và giữ claim ở mức chắc chắn phù hợp.
- **Route:** Humanizer pattern 5; → W3 (Citation After Claim); QA-10 (hallucination check).

### AE-28 — Humanize giả bằng synonym-swap
- **Nhận diện:** Bài "đã humanize" nhưng chỉ thay từ đồng nghĩa/đảo thứ tự câu — cấu trúc ngữ nghĩa y nguyên output AI; các bài cùng batch giống nhau về semantic dù khác chữ.
- **Cách sửa:** Humanize thật = thêm information gain + trải nghiệm thật + đa dạng cấu trúc ngữ nghĩa (S-CTS detect ở mức sentence embedding, diệt theo Generation Cluster — surface variation không thoát).
- **Route:** Humanizer "Detection Landscape 2026"; → QA-12, QA-15; [[sources/synthetic-slop-detection-lora-paper]].

---

## Bảng map: lỗi → phase pipeline hay phát sinh nhất

Phase theo `quality-content-ai.md` (P1 Research → P2 AI Generation → P3 Human Optimization → P4 Interactive → P5 Content Architecture → P6 Technical). Nhiều lỗi SINH ở P2 nhưng phải BẮT ở P3 — cột "Bắt ở" là chốt chặn QC.

| Lỗi | Sinh ra ở | Bắt ở |
|---|---|---|
| AE-01 Contextual Coverage Dillute | P2 (AI sinh thừa) | P3 edit + P5 architecture check |
| AE-02 Word count sai trọng số | P5 (outline/allocation) | Outline review (O8) trước khi viết |
| AE-03 Không quy định word count | P5 (AM thiếu spec) | Outline review (AM word ladder) |
| AE-04 Information density thấp | P2 | P3 edit (đếm EAV) |
| AE-05 Layer/PQ không phù hợp | P5 (AM) + P2 (AI bỏ qua AM) | Outline review + P3 |
| AE-06 Bold sai chỗ | P2 | P3 edit |
| AE-07 Subordinate text sai | P2 | P3 edit (W2 scan từng heading) |
| AE-08 Không đặt mình vào user | P1 (research nông) | P1 + P5 |
| AE-09 Dài không cần thiết | P2 | P3 edit |
| AE-10 Không có lý do tồn tại | P1 (thiếu unique data/gain) | P1 gate (QA-05) |
| AE-11 Media không semantic | P4/P5 | P3-P4 (W8/O13) |
| AE-12 Chưa humanize | P3 (bỏ bước) | P3 gate (QA-14) |
| AE-13 Câu/chính tả | P2 | P3 proofread cuối |
| AE-14 Sai register audience | P2 (prompt thiếu D1-D4) | P2 prompt hygiene + P3 |
| AE-15 Bullet vs numbered | P2 | P3 edit |
| AE-16 Không ăn khớp promise | P2 | P3 edit (đối chiếu intro-body) |
| AE-17 Root-first definition | P2 | P3 edit (L0 từng section) |
| AE-18 Outro kiểu AI | P2 | P3 edit |
| AE-19 Câu chuyển vô nghĩa | P2 | P3 edit (cuối mỗi heading) |
| AE-20 Intro không phải General Summary | P2 | P3 (viết intro CUỐI) |
| AE-21 Thiếu function | P1 (không map function) | P1 (QA-06) + P4 |
| AE-22 Planner language trong AM | P5 (AI sinh AM) | Outline review trước approve |
| AE-23 Table trong AM render | P5 (AI sinh AM) | Outline review trước approve |
| AE-24 Code-switch giữa câu | P2 | P3 edit (2 phép thử) |
| AE-25 Hard artifacts | P2 | P3 grep bắt buộc trước publish |
| AE-26 Cụm style AI | P2 | P3 humanize pass |
| AE-27 Vague attributions | P2 | P2 (QA-10) + P3 |
| AE-28 Humanize giả | P3 (làm sai cách) | P3 audit (Humanness Score + spot semantic) |

**Đọc nhanh cho QC:** 19/28 lỗi sinh ở P2 (AI Generation) — đầu tư vào prompt hygiene (QA-07/08) và pattern scan ngay khi nhận output (QA-11) rẻ hơn nhiều so với bắt hết ở editing. 5 lỗi thuộc outline/AM (AE-02/03/05/22/23) phải chặn ở outline review — sang tới draft là đã tốn một vòng viết lại.
