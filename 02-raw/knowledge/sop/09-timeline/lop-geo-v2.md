---
type: sop
sop: 09-project-timeline
version: "2.0"
last_updated: 2026-08-23
data_version: "v2026.08 — số liệu tính đến 23/08/2026 (Batch 40); refresh_due 2026-10"
master: "sop/06-self-checklist/tier-1-geo.md v2.0.2 (GE-01…GE-37)"
related:
  - "[[GEO]]"
  - "[[AI Visibility Measurement]]"
  - "[[Entity Home]]"
  - "[[Query Fan-Out]]"
  - "[[Core Source]]"
tags: [sop, geo, project-timeline, guideline, 6-diem-cham]
---
> Bản đóng gói cho SEO Production — sync từ `Knowledge/Semantic SEO A - Z/sop/09-project-timeline/lop-geo-v2.md` ngày 2026-09-02 (copy nguyên).
> Wikilink [[...]] trong file = tri thức nội bộ sâu (wiki Semantic SEO, không đóng gói theo dự án). Link `khung-duy-tri.md` / `10-thang-thuc-day.md` = file cùng folder.
> Gặp wikilink cần đào sâu → hỏi SEO Lead / Vincent, hoặc tra kho gốc trên máy master.


# Lớp GEO v2 trong quy trình 10 tháng — 6 điểm chạm

> **File này là guideline canonical** cho việc *đặt GEO vào đâu trong dự án*. Checklist chi tiết từng item nằm ở master `sop/06-self-checklist/tier-1-geo.md` (GE-01…GE-37) — file này **không lặp lại nội dung item**, chỉ quy định **mốc · vai · gate · cách nói với khách · luật phát hành 3 lớp**.
>
> Thay cho: lớp GEO v1 (9 hàng gantt rời rạc, có `llm.txt T3→T8`). Xem §7 Changelog để biết cái gì đổi và vì sao.

---

## 1. Nguyên tắc nền — đọc trước khi làm

1. **Không có "dự án GEO riêng".** Cùng một semantic content phục vụ cả ranking Google lẫn AI citation. GEO là **lăng kính** áp lên công đoạn đã có, không phải chuỗi task song song thứ hai. Hệ quả vận hành: mức **Tối thiểu** (xem G0) gần như **không phát sinh chi phí** vì trùng việc content semantic vẫn phải làm.
2. **Chưa rank thì chưa có vé dự thi.** Retrieval rank là predictor mạnh nhất của citation (position 0 = 58% vs position 10 = 14% — Ahrefs/Indig 04/2026). Site chưa có nền SEO mà mua "gói GEO" là bán sai thứ.
3. **Đầu tư theo Readiness, không theo mặc định.** Vertical có AIO trigger thấp (Shopping 3,2%) thì GEO ở mức Tối thiểu là đúng, không phải thiếu sót. Quyết định bằng scorecard G0, ghi vào proposal.
4. **Mọi con số GEO là moving target.** Fan-out tăng ~3 lần qua **một** phiên bản model (2026). Mọi số đưa vào deliverable khách phải kèm **nguồn + tháng + model version + kênh đo**. Số hết hạn → không dùng, không "làm tròn cho đẹp".
5. **Đo được mới cam kết.** Cam kết ở mức **aggregate SoV theo topic** + mục tiêu [[Core Source]]. Không cam kết per-prompt, không cam kết deterministic.

**5 guardrail bắt buộc nói với khách** (nguyên văn: master §GUARDRAIL): llms.txt ≠ lever · schema ≠ citation lever · không cam kết deterministic · không cite tên bịa ("Gecko Score"/"Jetstream" không tồn tại) · không nhồi chữ "official".

---

## 2. Sáu điểm chạm — bảng canonical

| Điểm chạm | Mốc | Công đoạn | Bộ chấm | PIC | Ra khỏi điểm chạm khi |
|---|---|---|---|---|---|
| **G0 · Readiness & Baseline** | T1 | 14 | Bộ NỀN (phần A) | SEO Lead Project | Có verdict Tối thiểu/Chuẩn hoá + baseline prompt set đã chạy, date-stamp |
| **G1 · Retrieval hygiene** | T1→T3 · verify T7 | 14 · 27 | Bộ NỀN (phần B) | SEO + Coder | Bot access là **quyết định chủ đích** (không phải mặc định) + trang đọc được bằng máy |
| **G2 · Source of truth & Entity** 🔺 | cuối T1→T3 | 13 | Bộ NỀN (phần C) | Content + SEO | `site:domain` trả lời được 5-10 câu hỏi thương mại cơ bản |
| **G3 · Passage architecture** | design-in T2→T9 · audit đợt 1 T4-T5 · đợt 2 T7-T9 | 15 · 21 · 23 · 28 · 29 | Bộ BÀI /12 | Content + SEO | Mỗi bài pass 4 item G-BÀI trước khi sang onpage |
| **G4 · Off-site consensus** | T4→T7 · duy trì | 20 · 26 (+ topical map 10) | Bộ OFFSITE /5 | SEO + Content | Đợt link/PR có lăng kính consensus, không chỉ DR |
| **G5 · Measurement → Báo cáo → Handover** | weekly nội bộ từ T2 · T6 · T10 · quý | 24 · 32 · 33 | Bộ ĐO /5 | SEO Lead Project | Báo cáo kép T10 + bàn giao prompt set/baseline/register |

**3 gate chặn** (fail = dừng, không đi tiếp):

| Gate | Ở đâu | Items | Fail thì làm gì |
|---|---|---|---|
| **G-T1** | T1, cuối G0 | GE-01 · GE-02 · GE-03 | Chưa rank → **dừng lớp GEO**, quay về nền SEO; báo Lead + ghi lý do vào proposal |
| **G-ENT** | ≤T3, cuối G2 | GE-11 | Chưa xong entity home → **chưa được tính "nền GEO xong"**, không mở đợt FS/AIO |
| **G-BÀI** | mỗi bài | GE-16 · GE-17 · GE-18 · GE-19 | Trả bài về Content, không đưa sang onpage |
| **G-KH** | mọi deliverable | GE-05 · GE-35 | Không gửi khách |

---

## 3. Chi tiết từng điểm chạm

### G0 · Readiness & Baseline (T1 · công đoạn 14)

**Làm gì:** ① chấm GEO Readiness scorecard → verdict **Tối thiểu** hay **Chuẩn hoá** ② chốt + chạy prompt set baseline ③ ghi Information Accuracy (AI đang nói gì sai về brand) + branded-prompt defense ④ dựng competitor citation set ⑤ nói 5 guardrail tại kickoff và ghi vào SOW.

**Đầu vào scorecard:** AIO trigger share của vertical · hiện trạng rank của trang mục tiêu · competitor AI citation set · vertical có phải YMYL không.

| Verdict | Phạm vi | Nói với khách |
|---|---|---|
| **Tối thiểu** | G0 (baseline) + G1 (bot access, hygiene) + G3 (content rules — vốn đã nằm trong pipeline) | "Vertical của anh/chị AI ít can thiệp; ta làm phần nền không phát sinh chi phí, đo mỗi quý, khi thị trường đổi thì nâng cấp." |
| **Chuẩn hoá** | Đủ 6 điểm chạm | "Có đủ điều kiện để AI trở thành kênh khách hàng — làm đủ 6 điểm chạm, đo T1/T6/T10." |

⚠ **Rủi ro nếu trễ:** baseline **không hồi phục được**. Bỏ lỡ T1 = mất vĩnh viễn mốc so sánh cho T6/T10. Đây là dòng bắt buộc trong bản Account.

**Output file:** `_TEMPLATES/geo-baseline.md` (SEO Production, WS 08).

### G1 · Retrieval hygiene (T1→T3, verify T7 · công đoạn 14 + 27)

**Làm gì:** speed/TTFB nền · index & canonical hygiene (AX4) · trang đọc được bằng máy (HTML ≤2MB, DOM order = visual order, nội dung quan trọng in-flow) · **AI crawler access là quyết định chủ đích**.

**Bot-purpose matrix** — mở/chặn theo mục đích, không theo cảm tính:

| Nhóm | Bot | Mặc định khuyến nghị |
|---|---|---|
| Search / discovery | OAI-SearchBot · Claude-SearchBot · PerplexityBot · Googlebot | **Mở** — muốn được cite thì bắt buộc |
| User-triggered | ChatGPT-User · Claude-User · Perplexity-User | **Mở** — user đang chủ động hỏi về brand |
| Training | GPTBot · ClaudeBot · Google-Extended | **Quyết định của khách** — chặn không ảnh hưởng Google Search |

🔴 Hit của **training bot KHÔNG phải KPI AI-visibility**. Logfile T7 dùng để *xác nhận access còn đúng*, không phải chỉ số báo cáo.

⚠ **Đây là chỗ `llm.txt` từng nằm.** Đã gỡ — xem §7.

### G2 · Source of truth & Entity 🔺 (cuối T1→T3 · công đoạn 13)

**Vì sao nâng hạng 08/2026:** ba phương pháp độc lập cùng chỉ một hướng — ChatGPT đã dịch từ *keyword discovery* sang **verification tại entity home**. `site:` xuất hiện trong 64% fan-out queries (Nectiv 13/08/2026, n≈4K, đo qua API); domain slot điền từ memory (wire capture); citation share của truy vấn dạng `site:`/`pricing` đang tăng (Peec). Hệ quả: **nếu entity home không trả lời được, fan-out quét về tay không** — dù content marketing có tốt tới đâu.

**Làm gì:** chạy `site:yourdomain.com [câu hỏi thương mại]` cho 5-10 câu khách hay hỏi (giá · tính năng · so sánh · chính sách · ở đâu) → mỗi câu phải có trang trả lời được **bằng text trên site chính chủ**. Cộng: owned truth pages đủ (about/pricing/FAQ/docs/chính sách) · brand E-A-V nhất quán đa kênh · Entity Home + `sameAs` · named author với kinh nghiệm nằm trong nội dung.

⛔ **Anti-pattern:** nhồi chữ "official" vào trang. `site:`/`official` là **triệu chứng** brand đã nằm trong shortlist, không phải nguyên nhân vào được shortlist.

### G3 · Passage architecture (design-in T2→T9 · công đoạn 15·21·23·28·29)

**Nguyên tắc:** **design-in, không vá sau**. 12 item Bộ BÀI được cài từ Outline/AM (phase 2 pipeline) và Writing (phase 3), rồi verify ở phase 4 — không phải một đợt "tối ưu GEO" cuối dự án.

| Nhịp | Việc |
|---|---|
| Mỗi bài, T2→T9 | Content tự chấm Bộ BÀI /12 trước khi submit; 4 item G-BÀI fail = trả về |
| **Đợt 1 — T4-T5** | Audit retrievability lô bài URL SEO + core đã publish (sau khi onpage URL SEO chốt) |
| **T7 — research fan-out** | Map fan-out theo **cluster** (~90% gom vào ≤4 cluster; chỉ ~27% consistent giữa các lần chạy) — **không đuổi từng query** |
| **T8 — triển khai** | Content theo cluster đã research, gộp với news/information gain |
| **Đợt 2 — T7-T9** | Audit theo full audit T7: query có AIO chưa được cite |

**Ngưỡng chunk:** dùng bảng canonical "3 con số chunk" tại [[Audition Chunk]]. **Không neo con số trong tài liệu quy trình** — mỗi hệ thống một ngưỡng, trích sai là tạo tin đồn.

### G4 · Off-site consensus & mentions (T4→T7 · công đoạn 20 + 26)

**Nguyên tắc nền:** **mention ≠ link**. Off-page link authority tương quan ≈ 0 với AI citation; **brand mention** là nhóm tương quan mạnh nhất (YouTube ~0,737 · branded web mentions 0,66-0,71 — Ahrefs 75k brands 12/2025, correlational).

Chạy **chung chiến dịch offsite**, không tách ngân sách riêng: ưu tiên nguồn mà AI hay cite trong ngách · 1 video YouTube đúng chủ đề · bài trên blog/báo ngành đang rank · review platform · có mặt ở 1/3 đầu listicle bên thứ ba. Node off-site phải **nằm trong topical map** (§14b), không phải PR rời.

⚠ UGC/forum VN (Voz/Tinhte/nhóm Facebook) = **giả thuyết chưa có data** → chạy như thí nghiệm có đo, không bán như tactic đã chứng minh.

### G5 · Measurement → Báo cáo kép → Handover (T1 · weekly · T6 · T10 · quý)

| Mốc | Việc |
|---|---|
| T1 | Baseline (G0) |
| Weekly-2 tuần, nội bộ từ T2 | Polling: ≥3 lần/prompt (chuẩn GTV 5 lần/prompt/engine). Lý do: AI Mode đổi 56% nguồn/tuần, ChatGPT 74% |
| T6 (công đoạn 24) | Đo giữa kỳ **cùng prompt set** + OKRs Q3 |
| T10 (công đoạn 32) | **Báo cáo kép** = KPI ranking/traffic + AI visibility so baseline T1 |
| T10 (công đoạn 33) | Handover: prompt set + baseline + register số liệu + lịch đo quý |
| Duy trì | Đo mỗi quý (nhịp Quarterly) |

**Luật báo cáo:** báo cáo **theo topic**, không theo từng prompt · tách per-engine (AIO ≠ AI Mode ≠ Gemini app ≠ ChatGPT — chỉ 2,37% URL được cả 3 engine cùng cite) · mọi metric AI dán nhãn **directional**, đối chiếu referral thật (GA4/server log) trước khi tuyên bố thắng.

---

## 4. Biến thể 8 / 10 / 12 tháng

Nguyên tắc: **G0 baseline luôn ở T1**, không nén — mất mốc là mất vĩnh viễn. Các mốc còn lại trượt theo timeline chung.

| Điểm chạm | 8 tháng | 10 tháng (chuẩn) | 12 tháng |
|---|---|---|---|
| G0 Readiness & baseline | T1 | T1 | T1 |
| G1 Retrieval hygiene | T1→T2 · verify T6 | T1→T3 · verify T7 | T1→T3 · verify T8 |
| G2 Source of truth & entity | cuối T1→T2 | cuối T1→T3 | cuối T1→T4 |
| G3 audit đợt 1 (sau onpage URL SEO) | T3-T4 | T4-T5 | T5-T6 |
| G3 research fan-out → triển khai | T6 → T7 | T7 → T8 | T8 → T9 |
| G3 audit đợt 2 (sau full audit) | T6-T7 | T7-T9 | T8-T10 |
| G4 Off-site consensus | T3-T6 (chung backlink nền) | T4-T7 | T4-T9 |
| G5 đo giữa kỳ (~60% timeline) | T5 | T6 | T7 |
| G5 báo cáo kép + handover | T8 | T10 | T12 |

---

## 5. Luật derive 3 lớp phát hành

Master `tier-1-geo.md` gắn tag `L1/L2/L3` cho từng item. Bản dưới lớp **derive bằng filter**, không viết tay lại — sửa master một chỗ, ba lớp đồng bộ.

| | Lớp 1 — Quà sự kiện (public) | Lớp 2 — Học viên TAG | Lớp 3 — Nội bộ GTV |
|---|---|---|---|
| Filter | `tier ∈ {L1}` | `tier ∈ {L1, L2}` | tất cả |
| Giá trị | WHAT + what NOT — chẩn đoán & thứ tự | HOW tự làm, tự chấm | HOW ở quy mô, có QC & cam kết |
| Số liệu | chỉ **whitelist** register, kèm nguồn + tháng | whitelist | đầy đủ, có nhãn evidence tier |
| Cấm | mọi ngưỡng vận hành, prompt-set design, rubric, per-engine method | trọng số scorecard, công thức cam kết, script khách, register đầy đủ, data client | — |
| Ngôn ngữ | "tăng xác suất được nhắc" | "mục tiêu", không "cam kết" | "cam kết" (có KPI §D) |
| Version | `v2026.08 · hạn dùng 31/10/2026` | `v2026.08`, update qua community | `refresh_due 2026-10` nối lint quý |

**Luật an toàn cả 3 lớp:** case public chỉ nói ngành chung, không nêu brand (case enterprise VN: **không nói cả ngành**) · không tên client GTV trong tài liệu TAG · Lớp 2 đổi "cam kết" → "mục tiêu" · số thuộc **blacklist** register không xuất hiện ở Lớp 1/2.

**Kiểm tra trước khi phát hành:** grep các từ khoá blacklist (`Gecko Score`, `Jetstream`, `8-12 sub`, `7,61`, `llms.txt` ngoài mục NOT-a-lever, `115%`, `cosine 0,90`) → chỉ được xuất hiện ở mục đính chính/NOT-a-lever.

---

## 6. Refresh & version

- **data_version hiện tại:** `v2026.08` (Batch 40, 23/08/2026). **Hạn dùng: 31/10/2026.**
- **Nhịp refresh:** theo lint quý. 10/2026 → cập nhật `wiki/syntheses/geo-evidence-register-2026-08.md` → `v2026.11` → re-derive cả 3 lớp.
- **Nguồn số liệu duy nhất:** [[syntheses/geo-evidence-register-2026-08]] (whitelist/blacklist + nhãn + cỡ mẫu + tháng). Không lấy số từ trí nhớ, không lấy từ slide cũ.
- **Trigger refresh ngoài lịch:** engine đổi phiên bản lớn (fan-out đã tăng 3× qua một version) · Google công bố tài liệu mới · một số trong whitelist bị nguồn gốc rút lại.

---

## 7. Changelog — v1 → v2 (23/08/2026)

| Đổi | Cũ (v1) | Mới (v2) | Vì sao |
|---|---|---|---|
| **Cấu trúc** | 9 hàng gantt rời rạc | **6 điểm chạm** G0-G5, mỗi điểm 1 bộ chấm + PIC | Hàng rời không nói được "ai làm, xong khi nào, fail thì sao" |
| 🔴 **Gỡ `llm.txt T3→T8`** | Hạng mục chạy 6 tháng | **Xoá hẳn**, thay bằng G1 "AI crawler access & retrieval hygiene" (T1→T3, verify T7) | Không AI system nào dùng (Mueller nguyên văn); audit log: bot **không request** file; Ahrefs 100k domains không thấy lợi thế. Guardrail nội bộ đã cấm bán — quy trình vẫn còn task là **tự mâu thuẫn** |
| **Thêm G2** | (không có) | Source of truth & Entity, nâng lên ngay sau gate | `site:` 64% fan-out — 3 phương pháp độc lập hội tụ (Batch 40) |
| **Gate** | (không có) | G-T1 · G-ENT · G-BÀI · G-KH | Trước đây GEO chạy kể cả khi site chưa rank |
| **Readiness** | GEO mặc định "có làm" | Verdict Tối thiểu / Chuẩn hoá theo scorecard | Vertical Shopping AIO 3,2% mà làm full là đốt tiền khách |
| **Fan-out** | "8-12 sub-queries" | Map theo **cluster** ≤4, không neo số | Số đã hết hạn: fan-out tăng ~3× qua một model version; chỉ 27% query lặp lại |
| **Freshness** | re-stamp năm | Cập nhật **nội dung thật**; content năm cũ **không chết** | ChatGPT search song song "2026" và "2025" (multi-year, Batch 40) |
| **AX** | AX1-AX5 | **AX1-AX6** (+ passage verifiability) | Patent US11769017B1 + US20240289407A1 verified 21/08/2026 |
| **Đo lường** | "đo T6 · báo cáo T10" | Polling standard + per-engine + evidence bar + handover | 1 lần chạy/prompt không phải dữ liệu; variance 10-34% |

**Nơi đã đồng bộ theo v2 (hoàn tất 23/08/2026):** `10-thang-thuc-day.md` rev 3 · `quy-trinh-seo-10-thang.html` Rev 4 · `quy-trinh-seo-10-thang-account.html` (+mục 07 script GEO cho Account) · `khung-duy-tri.md` v2.1 · `quy-trinh-seo-duy-tri.html` · `README.md` · `github-repos-tich-hop.html` (gỡ đề xuất tích hợp llms.txt) · `SEO Production/CLAUDE.md` Ma trận M · `_TEMPLATES/geo-baseline.md` v2 · `sop/01` Gate #2 · `sop/07` B7 · `sop/08` AX6 · `sop/06/README.md` · `tracking-schema.md` (Sheet 6) · `monthly-project-review.md` MRQ-05 · `tier-1-gbp-local.md` · 3 bản học viên TAG.

---

## 8. Bốn bản phát hành — đều sinh từ 1 master

| Bản | Ở đâu | Sinh bằng |
|---|---|---|
| **Master (nguồn sự thật)** | `sop/06-self-checklist/tier-1-geo.md` v2.0.2 — 37 items, tag L1/L2/L3 | viết tay, **chỉ sửa ở đây** |
| Lớp 3 · HTML nội bộ | `sop/06-self-checklist/tier-1-geo.html` | `build-tier-1-geo-html.py` |
| Lớp 3 · Google Sheet | "GEO Checklist GE v2 — Tracking" · folder Drive **GTV SEO — GEO Checklist 2026** | `build-geo-sheet-payload.py` → `push-geo-sheet.py --reuse` |
| Lớp 2 · học viên TAG (= quà VVIP) | `TAG Ops/wiki/product/geo-checklist/geo-checklist-hoc-vien-v2026-08.html` — 32 items (lọc `L1`+`L2`) | `build-geo-checklist-hoc-vien.py` |
| Lớp 1 · quà sự kiện | `Deliverables/TAG-Brand/event-ai-marketing-seo-2026/07-tai-lieu-tang-kem/event-ai-mkt-seo_khung-geo-30-ngay_v1.html` | viết riêng theo lời hứa keynote, số liệu lấy từ whitelist register |

**Quy trình refresh (10/2026):** cập nhật `wiki/syntheses/geo-evidence-register-2026-08.md` → `v2026.11` → sửa master → **chạy lại 3 script** → 4 bản đồng bộ. Đừng vá tay từng bản: đó chính là cách 3 lớp bắt đầu lệch nhau.

---

## Cross-refs

- **Master checklist** → `sop/06-self-checklist/tier-1-geo.md` (GE-01…GE-37, 4 bộ chấm, tracking columns)
- **Register số liệu** → [[syntheses/geo-evidence-register-2026-08]]
- **Khái niệm** → [[GEO]] · [[AI Visibility Measurement]] · [[Entity Home]] · [[Query Fan-Out]] · [[Audition Chunk]] · [[Core Source]]
- **Skill** → `geo-tracking-prompt-selection` (đo) · `geo-content-optimization` (audit + rewrite 1 trang)
- **Timeline** → [10-thang-thuc-day.md](10-thang-thuc-day.md) · [khung-duy-tri.md](khung-duy-tri.md)
