---
type: sop
tier: 3
phase: [content-audit, content-configuration]
last_updated: 2026-04-20
source_file: raw/guidelines/Full Semantic Content Checklist - Verion 2 - update 16.4.2026.xlsx
items_count: 8
activation: Senior / audit mode / high-competition niche
tags: [sop, tier-3, audit, content-configuration, information-gain, helpful-content]
---

> Bản đóng gói cho SEO Production — sync từ `SEO Knowledge/Semantic SEO A - Z/sop/06-self-checklist/tier-3-audit-configuration.md` ngày 2026-07-17.
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án).
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.

# Tier 3 — Advanced / Content Audit & Configuration

> **Khi dùng:** Senior nhân sự + dự án cạnh tranh cao, HOẶC khi content audit / content configuration.  
> **Số items:** 8 (T3-O1..O3 Outline + T3-W1..W5 Writing)  
> **Pattern:** Advanced scoring & audit-mode items. Không dùng cho bài viết mới thông thường.  
> **Tick ở đâu:** Extra columns trên Tracking Sheet (add khi senior dùng), hoặc audit report riêng.

## Khi nào dùng Tier 3

1. **Content Audit mode** — review bài cũ để quyết định: rewrite / rework / giữ nguyên / consolidate / delete.
2. **Content Configuration** cho niche cạnh tranh cao — set chuẩn pre-emptive cho cả series bài.
3. **Senior calibration** — senior dùng để audit work của mid-level.
4. **Full Semantic Audit (66pt)** — T3-W3 là audit-mode comprehensive, áp dụng cho pillar pages / revenue-critical pages.

## Items breakdown

### Outline-side (T3-O)
- **T3-O1 — Information Gain Scoring** → Lượng hoá information gain vs đối thủ theo thang điểm. [[Information Gain Score]].
- **T3-O2 — Topical Map Integration** → Bài này vị trí nào trên Topical Map? Có cover gap không? [[Topical Map]] + [[Topical Gap]].
- **T3-O3 — Featured Snippet Strategy in AM** → Target FS position 0 chủ động trong AM. [[Featured Snippet]] + [[Information Density]].

### Writing-side (T3-W)
- **T3-W1 — Information Density Scoring** → Đo độ dày thông tin của content (facts/EAV per 100 words). [[Information Density]] + relates to AI Overview / GEO citation rate.
- **T3-W2 — People-first / Helpful Content assessment** → Audit bài theo people-first content guidance hiện hành (helpful content classifier đã tích hợp core systems 03/2024 — không còn "Helpful Content System" standalone; đổi wording 2026-07-13, LINT-2026-018). [[Google Helpful Content]] (stub).
- **T3-W3 — Full Semantic Audit (66pt)** → Comprehensive 66-point audit combining all Tier 1 + Tier 2 items với scoring rubric.
- **T3-W4 — Modality Transitions** → Tinh chỉnh modality (present/can/should) across sentences. [[Modality]] (stub).
- **T3-W5 — Cross-SCN Quality Gate** → Kiểm tra consistency qua nhiều bài trong cùng SCN. [[Semantic Content Network]].

---

### T3-O1 — Information Gain Scoring

**Tier:** Tier 3  
**Phase:** Outline/AM  
**Bật khi nào:** Dự án cạnh tranh cao  


**Tóm tắt:** Xác định vị trí bài trong Topical Map: Root/Seed/Node, upstream/downstream links, predicate chain. Nhìn toàn cảnh SCN để bài mới đúng vị trí. Áp dụng khi xây topical map từ đầu.

**Mô tả đầy đủ:**

Xác định rõ vị trí bài viết trong Topical Map: (1) Loại bài — Root (bài gốc, cover rộng), Seed (bài hạt giống, mid-level), hay Node (bài chi tiết, niche). (2) Upstream/downstream — bài nào link ĐẾN bài này (upstream), bài này link ĐI bài nào (downstream). (3) Predicate chain xuyên SCN — bài nằm ở đâu trong chuỗi predicate (biết → hiểu → áp dụng → đánh giá). Áp dụng khi xây topical map từ đầu, cần nhìn toàn cảnh SCN.

---

### T3-O2 — Topical Map Integration

**Tier:** Tier 3  
**Phase:** Outline/AM  
**Bật khi nào:** Xây topical map từ đầu  


**Tóm tắt:** Check SERP Featured Snippet hiện tại: dạng gì (para/list/table), độ dài, density. AM ghi rõ target FS format, L0 phải beat FS đang có. Bold answer (không bold keyword). Dành cho keyword có FS opportunity.

**Mô tả đầy đủ:**

Trước khi viết AM, check SERP để xem Featured Snippet (FS) hiện tại: (1) Dạng FS — paragraph, list, hay table. (2) Nội dung FS hiện tại — độ dài, information density, format. (3) AM ghi rõ target FS format + yêu cầu content phải beat FS hiện tại — VD: FS đang 35 words → L0 phải 38-40 words, density cao hơn. (4) Bold answer (không bold keyword) để tối ưu khả năng được chọn làm FS. Áp dụng cho keywords có FS opportunity rõ ràng.

---

### T3-O3 — Featured Snippet Strategy in AM

**Tier:** Tier 3  
**Phase:** Outline/AM  
**Bật khi nào:** Keyword có FS opportunity  

---

### T3-W1 — Information Density Scoring

**Tier:** Tier 3  
**Phase:** Writing  
**Bật khi nào:** Dự án cạnh tranh cao  


**Tóm tắt:** Audit theo Google Helpful Content: Who-How-Why transparent, không warning signs (mass-production, trending-only), ít nhất 1 unique insight/data point mà top 10 chưa có. Dùng Skill `semantic-content-audit`.

**Mô tả đầy đủ:**

Audit toàn diện theo Google Helpful Content guidelines: (1) Who-How-Why transparent — ai viết (credentials), viết bằng cách nào (methodology), viết để làm gì (mục đích giúp reader). (2) Không có warning signs — không viết theo trending mà thiếu expertise, reader không cần search lại, không mass-production feel. (3) Original value — ít nhất 1 unique insight/data point/angle mà top 10 SERP chưa có. Dùng Skill `semantic-content-audit` để audit chi tiết.

---

### T3-W2 — People-first / Helpful Content assessment

> (Đổi tên từ "Google Helpful Content Audit" 2026-07-13 — classifier đã vào core systems 03/2024, đánh giá theo people-first guidance hiện hành: developers.google.com/search/docs/fundamentals/creating-helpful-content.)

**Tier:** Tier 3  
**Phase:** Writing  
**Bật khi nào:** Audit chất lượng cao  


**Tóm tắt:** Audit đầy đủ theo thang 66 điểm: Structural (12đ), Semantic (12đ), Writing Quality (16đ), E-E-A-T (16đ), Google Helpful Content (10đ). Target ≥50/66 cho dự án flagship. Dùng Skill `semantic-content-audit`.

**Mô tả đầy đủ:**

Audit đầy đủ theo thang 66 điểm của Semantic Content Audit framework: Structural (12đ) — heading hierarchy, main/supplement ratio, contextual bridge. Semantic (12đ) — macro/micro terms, L0 answer-first, general summary. Writing Quality (16đ) — subordinate text, modality, citations, precision. E-E-A-T (16đ) — first-hand experience, evidence media, specific observations. People-first/Helpful Content (10đ) — people-first, original value, WHO-HOW-WHY (guidance hiện hành, không phải "HCU system" riêng). Target ≥50/66 cho dự án flagship. Dùng Skill `semantic-content-audit`.

---

### T3-W3 — Full Semantic Audit (66pt)

**Tier:** Tier 3  
**Phase:** Writing  
**Bật khi nào:** Dự án flagship  


**Tóm tắt:** Modality flow tự nhiên trong section: definitive (fact) → cautious (can/may, research) → recommendation (should, gợi ý). Chuyển modality dùng transitional phrases không đột ngột. Dành cho senior fine-tune chất lượng.

**Mô tả đầy đủ:**

Trong 1 section, dòng chảy modality phải tự nhiên và có mục đích: bắt đầu definitive (present tense — nêu fact dứt khoát) → chuyển cautious (can/may — findings từ nghiên cứu, chưa có consensus) → kết thúc recommendation (should — gợi ý hành động cho reader). Flow chuyển modality không đột ngột: dùng transitional phrases để bridge giữa các modality ('Nghiên cứu cho thấy... vì vậy bạn nên...'). Dành cho senior content writer cần fine-tune chất lượng câu văn.

---

### T3-W4 — Modality Transitions

**Tier:** Tier 3  
**Phase:** Writing  
**Bật khi nào:** Senior content  


**Tóm tắt:** Kiểm tra chất lượng xuyên SCN: L0 của Root + Seed đọc liền thành 'super summary' mạch lạc, không mâu thuẫn, không lặp. Central Search Intent và predicate nhất quán. Dành cho SCN mature cần quality gate.

**Mô tả đầy đủ:**

Kiểm tra chất lượng xuyên SCN bằng cách: (1) Lấy L0 (câu trả lời trực tiếp đầu mỗi H2) của bài Root + tất cả bài Seed, đọc liền — phải tạo thành 'super summary' mạch lạc, không mâu thuẫn, không lặp. (2) Central Search Intent phải được reflected nhất quán — mọi bài đều hướng về cùng mục đích. (3) Predicate nhất quán — không bài nào lệch predicate chain. Áp dụng cho dự án SCN mature (đã publish nhiều bài), cần quality gate trước khi tiếp tục scale.

---

### T3-W5 — Cross-SCN Quality Gate

**Tier:** Tier 3  
**Phase:** Writing  
**Bật khi nào:** Dự án SCN mature  

**Mô tả đầy đủ:**

L0 Root + Seed đọc liền phải tạo super summary mạch lạc. Central Search Intent reflected nhất quán. Predicate không lệch. Quality gate cho SCN mature trước khi scale tiếp.

---
