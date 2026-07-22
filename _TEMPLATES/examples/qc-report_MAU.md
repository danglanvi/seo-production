> ⚠️ MẪU MINH HỌA — client hư cấu "Công ty Ví Dụ / vidu.vn", số liệu giả định để agent noi theo CẤU TRÚC + ĐỘ SÂU + GIỌNG.
> Không copy số vào deliverable thật. Mẫu thật của dự án tích lũy trong instance qua vòng feedback → lesson → promote.

---
deliverable: 04-structure-ux-cro/VIDU_Wireframe-Structure_v1.md
cong_doan: 11
ws: 04
checklist: 02-raw/knowledge/sop/07-visual-semantic.md
tier: 1
role: self
scorer: Claude (AI, role self) + An (SEO Lead Project — chờ xác nhận verdict)
score: 6/9
verdict: CONDITIONAL-PASS
date: 2026-04-08
---

# QC report — công đoạn #11 · VIDU_Wireframe-Structure_v1 (wireframe + HTML template 3 page type)

> Path thật khi dùng: `03-audits/qc/QC-11-wireframe-structure-20260408.md`. Chấm theo `sop/07-visual-semantic.md` (B0-B8 + RACI), Tier 1 (kick-off #12 chưa bật Tier 2), role `self`. Evidence trích từ deliverable + verify trực tiếp 3 file `VIDU_Template-*.html` cùng folder. Chế độ SOP: **Design-in** (trang mới — deliverable khai báo ở mục 1). Chuẩn chấm: từng item theo ID, có evidence trích được; không có evidence = không có kết quả.

## Kết quả theo item

| ID | Check (rút gọn) | Kết quả | Evidence | Ghi chú |
|---|---|---|---|---|
| B0 | Input Gate: Topical Map + Outline AM + entity/attribute + page type + Central Search Intent | PASS | Mục 1 spec dẫn `05-content-plan/VIDU_topical-map_v1.md` (index #10 ✅) + Outline AM 3 page type; CSI ghi per trang, vd money page: "chọn đúng máy lọc nước theo nguồn nước + ngân sách" | Đúng luật vào cửa "Không có Outline AM → không vào process" |
| B1 | Query Augmentation: bảng variation → page type/layout/function + prune/merge | PASS | Bảng 8 biến thể ở mục 2 spec: "máy lọc nước giá rẻ" → merge vào PLP (filter giá); "máy lọc nước nào tốt" → page so sánh riêng; 2 prune + 1 merge, mỗi dòng có lý do | Không sinh page trùng intent — PageRank cô đặc |
| B2 | Function & Centerpiece: Function Statement + Centerpiece spec 1 câu + above-fold elements + ~400 ký tự đầu sau H1 | PASS | Đủ 4 khối per trang. Money page: "Trang phải deliver bảng so sánh 3 dòng máy + giá ngay viewport đầu"; đoạn ~400 ký tự sau H1 viết nháp sẵn, flow liền mạch không inject | Mixed intent → đủ cả 2 bộ elements above-fold (giá + công dụng) |
| B3 | SERP & Attribute Benchmark: chụp top 5-10 đúng geo/device + đọc ngược SERP features → attribute + category thắng + archetype | FAIL | Có 10 ảnh SERP trong `02-raw/screenshots/serp-ai/` (vd `20260405_q-may-loc-nuoc_desktop.png`) + archetype note. THIẾU: bảng đọc ngược SERP features → attribute ưu tiên; chưa chốt "category thắng SERP" bằng văn bản cho 3 target query | Không-blocking: wireframe đã match archetype qua quan sát, nhưng output B3 theo SOP phải là BẢNG kiểm chứng được, không phải trí nhớ người làm |
| B4 | Block Architecture: attribute = section riêng · card skeleton ≥3 lần · block đủ 5 slots · zone weight · CTA interleave | PASS | Card "product-card" đủ sub-attribute cố định (tên · giá · công suất lọc · số cấp lọc · CTA), instantiate 12 lần ở PLP; kiểm 6/6 block money page đủ 5 slots; zone weight gán Centerpiece 100% / Supporting 60-80%; CTA per card — không dồn 1 CTA cuối trang | Bảng `Attribute \| Value` có thật ở money page (7 dòng thông số) |
| B5 | Visual Asset Layer: visual spec per block + filename ≤3 từ + alt = verbalized expansion + ImageObject | FAIL | Mỗi key block có ≥1 visual đặt cạnh text liên quan (map đủ trong mục 5 spec). THIẾU: chuẩn filename ≤3 từ + alt verbalized cho 12 ảnh card; chưa spec `ImageObject`/`primaryImageOfPage` cho bản bàn giao dev | Không-blocking: bổ 1 mục "Chuẩn ảnh bàn giao" là đủ output B5 — không phải làm lại layer |
| B6 | Design Implementation: typography hierarchy · DOM order = visual order · semantic HTML thật · không giấu critical info | PASS | Verify 3 file HTML: mỗi file đúng 1×`<h1>`, 1×`<main>`, section theo attribute, không div-soup ở khối chính; H1 40px above-fold; thông số phụ trong `<details>` — giá + CTA không nằm trong accordion | DOM order khớp visual order desktop + mobile (đọc source theo thứ tự render) |
| B7 | Technical Verification (HARD GATE): HTML <2MB · ảnh width/height · metadata initial HTML · JSON-LD đúng page type | PASS | 3 file: 1,2MB / 0,8MB / 0,6MB — đều <2MB; 100% `<img>` có width+height+alt; title/canonical/JSON-LD nằm trong initial HTML: Product+Offer (money), ItemList+BreadcrumbList (PLP), Organization (home); TTFB staging 0,8s <2s | Không dùng FAQPage/HowTo làm rich-result lever — đúng guardrail SOP |
| B8 | Validation Loop: extraction test · Blur Test · effort review · chunk test per H2 · SERP/AI-surface · function test | CANNOT-VERIFY | Deliverable là wireframe + template tĩnh, chưa deploy; spec mục 7 đã đặt lịch chạy đủ 6 test sau khi dev build (dự kiến cuối T2) — tại thời điểm QC chưa có record test nào để đối chiếu | KHÔNG tính pass. Điều kiện kèm ở verdict: chạy B8 + file-back kết quả trước 05/05 |
| RACI | RACI đúng vai + mốc structure lock ≤15 ngày đầu T2 | PASS (không tính điểm /9) | Bảng A `index.md`: PIC #11 = An (SEO Lead) + anh Tú (dev khách) — khớp RACI B6-B7; QC ngày 08/04, còn trước mốc lock 15/04; lịch Lead duyệt đặt 10/04 | Mốc cứng §6.2 chưa vỡ — khác với FAIL, đây là item theo dõi tiến độ |

**Score: 6/9** (B0, B1, B2, B4, B6, B7 pass · B3, B5 fail · B8 CANNOT-VERIFY không tính pass · RACI ngoài thang điểm).

## Việc phải sửa (item FAIL, sắp theo impact)

| ID | Sửa gì | Owner | Deadline |
|---|---|---|---|
| B3 | Lập bảng đọc ngược SERP features → attribute ưu tiên cho 3 target query (từ 10 ảnh đã chụp) + chốt category thắng SERP per query; append vào mục 3 của spec | An (SEO Lead) | 11/04 |
| B5 | Thêm mục "Chuẩn ảnh bàn giao" vào spec: filename ≤3 từ + alt = verbalized expansion cho 12 ảnh card + figcaption lặp số liệu + `ImageObject`/`primaryImageOfPage` | Chi (Content Leader) | 12/04 |

## Verdict & điều kiện

- **Verdict: CONDITIONAL-PASS (đề xuất — Lead quyết theo §7.4, Claude không tự chốt).** Ngưỡng của chính checklist đang chấm: SOP 07 yêu cầu mỗi bước B0-B8 có output đúng spec, B7 là hard gate. B7 PASS toàn bộ ô; 2 item fail (B3, B5) đều không-blocking — thiếu VĂN BẢN HÓA output, không sai kiến trúc — và có deadline sửa cụ thể. Khớp điều kiện CONDITIONAL-PASS: fail ≤2 item không-blocking + deadline.
- **Điều kiện kèm:** (1) B3 xong 11/04, B5 xong 12/04 — An xác nhận đã sửa TRƯỚC khi trình Lead duyệt structure lock 14/04; (2) B8 chạy đủ 6 test + file-back kết quả vào `04-structure-ux-cro/` trước 05/05 — chưa có kết quả B8 thì #11 chỉ được mở content lô 1, KHÔNG mở content hàng loạt.
- **Đọc kết quả cho đúng:** phần lõi khó nhất (B4 block architecture, B6 semantic HTML, B7 hard gate) pass với evidence thật — nền vững. Hai FAIL là lỗi kỷ luật văn bản hóa, sửa được trong 2 ngày. Chấm không nương tay với thiếu sót, nhưng không phóng đại thiếu sót thành lỗi kiến trúc.
- **Nếu Lead không đồng ý CONDITIONAL-PASS** → verdict rơi về FAIL: dòng #11 giữ status `qc`, sửa xong QC lại thành report MỚI — không sửa report này.
- **Giới hạn của lần chấm:** role `self` do AI hỗ trợ chấm — verdict chỉ là ĐỀ XUẤT cho tới khi An (Lead) đối chất evidence và ký xác nhận; TTFB đo trên staging, số production có thể khác — ghi nhận, không suy ra pass sớm.
- **Liên thông 3-Level Review (§7):** deliverable này thuộc diện Lead có thể gọi random 25-30% — report role `self` phải đủ sâu để lần chấm `lead` chỉ verify, không chấm lại từ đầu.

## Done-criteria

- [x] Frontmatter đủ 10 field; score khớp tổng bảng item.
- [x] 100% item checklist (B0-B8 + RACI) có mặt trong bảng, mỗi item có kết quả + evidence trích được.
- [x] Mọi item FAIL có dòng "Việc phải sửa" với owner + deadline.
- [x] `index.md` update: cột QC #11 ghi `CONDITIONAL-PASS (đề xuất) 6/9 → [QC-11-...]` + status `qc` + bảng D.
- [x] Append `log.md` op `qc`; chưa có item fail ≥2 lần QC → chưa trigger đề xuất feedback-log.
