---
name: cro-measurement-plan
description: "Lập kế hoạch đo chuyển đổi website: outcome + mẫu số, bộ event GA4 theo cơ chế (gọi/Zalo · form · báo giá · giỏ hàng · apply), spec GTM cho dev, kênh AI Assistant, đối soát CRM/Sheet và ca QA. Dùng khi kickoff #34, audit tracking, gate G1, hoặc trước khi đọc số CRO/A/B."
---

# cro-measurement-plan — đo đúng trước khi tối ưu

Website nào cũng có click; ít website đo được **outcome** (lead đạt chuẩn, đơn hợp lệ, hồ sơ hoàn tất). Skill này ra một bản kế hoạch đo mà dev/khách làm được không hỏi lại, và một bộ ca QA để biết số có tin được không. Kết quả QA chưa chạy thì ghi "plan", không ghi PASS.

## Khi nào dùng

- Kickoff #34 / gate G1 (CR-06, CR-07): client chưa có tracking hoặc tracking chỉ có `page_view`.
- Audit tracking đang có: số GA4 lệch CRM, `purchase` bắn sai, click Zalo/gọi không đo, event tạo trong giao diện GA4.
- Trước khi đọc số CRO, trước A/B, hoặc khi report cần hàng "Conversion từ AI Assistant".
- Không dùng cho: tín hiệu tối ưu quảng cáo (offline conversion import, CAPI) — wiki `conversion-signal-architecture`; sửa tag sống trên GTM/GA4 của khách (skill chỉ ra spec, người có quyền làm).

## Input

| Bắt buộc | Nguồn | Thiếu thì |
|---|---|---|
| Loại website + cơ chế chuyển đổi chính/phụ | Brief, quan sát site | Tự inventory nút/form trên site rồi xác nhận với client |
| Định nghĩa outcome và "đạt chuẩn" | Client / sale / HR | Đề xuất rubric, đánh dấu "chờ client chốt" |
| Quyền truy cập GA4/GTM (mức xem) | Client | Viết spec theo DOM quan sát được, ghi "chưa kiểm DebugView" |
| Nơi outcome được ghi (CRM, Sheet, ATS, backend đơn) | Client | Đề xuất Sheet lead tối thiểu; không hứa đối soát |
| Có GEO trong hợp đồng hay không | Hợp đồng / Account | Vẫn cấu hình kênh AI (chi phí thấp), report nhãn directional |

## Quy trình

1. **Chốt outcome, mẫu số, đơn vị.** Mỗi cơ chế một dòng: outcome · micro-event · guardrail · mẫu số (người đủ điều kiện) · đơn vị (user / candidate–job / đơn). Ecommerce có COD: tách "đơn tạo" và "đơn hợp lệ". Đọc `references/event-contracts.md` §1.
2. **Chọn bộ event theo cơ chế.** Bảng router ở `references/event-contracts.md` §2–§6: dùng GA4 recommended event khi có (`generate_lead`, `purchase`, `add_to_cart`…), custom cho gọi/Zalo/Messenger/apply. Mỗi event khai: tên · trigger · nguồn xác nhận · tham số · chống trùng · điều kiện consent · owner.
3. **Viết spec GTM cho dev/khách.** Inventory DOM (nút `tel:`, dạng nút Zalo, form native/iframe, trang cảm ơn, cổng thanh toán quay về) → trigger/tag/biến theo `references/gtm-spec.md`. `purchase` và `application_complete` chỉ từ dataLayer sau khi backend xác nhận. Không tạo event trong giao diện GA4 cho `tel:`/`mailto:`.
4. **Kênh AI (nếu có session AI hoặc GEO).** Custom channel group: `Source matches regex` OR `Medium = ai-assistant`, đặt trên Referral; ghi 4 điểm mù vào plan. `references/event-contracts.md` §7.
5. **Đối soát outcome.** Chốt nguồn (CRM/Sheet/ATS/backend), cửa sổ, cột tối thiểu của Sheet lead, ngưỡng lệch chấp nhận **theo dự án**. `references/reconciliation-qa.md` §1–§2.
6. **Ca QA + bàn giao.** Lập bảng ca theo `references/reconciliation-qa.md` §3 (thành công / lỗi / retry / double click / reload / SPA / cổng thanh toán / offsite). Ai chạy, ngày chạy, kết quả. Chưa chạy → cột kết quả ghi "plan". Điền output theo `references/output-template.md`, tự kiểm Gate, trả.

## Output

- Path: `13-cro/<CLIENT>_measurement-plan_v<N>.md`; khi đã chạy QA: `13-cro/<CLIENT>_tracking-qa_v<N>.md`. Ngoài repo SEO Production (site nội bộ, deal chưa có instance): `Deliverables/<project>/<client>_measurement-plan_v<N>.md`.
- Site chỉ có 1 cơ chế và ≤5 event → nhúng vào §1 của `<CLIENT>_conversion-path_v<N>.md` thay vì tách file; ghi chú "measurement plan nhúng".
- Format bắt buộc theo `references/output-template.md`: A. Outcome & mẫu số · B. Event contract · C. Spec GTM · D. Kênh AI · E. Đối soát · F. Ca QA · G. Trạng thái & owner.

## Gate / tự kiểm trước khi trả

- [ ] Mỗi outcome có nguồn xác nhận ngoài GA4 (CRM/Sheet/ATS/backend) hoặc ghi rõ "chưa có → chỉ báo micro".
- [ ] Không có click nào được đặt tên như outcome (`click_zalo` ≠ lead; click-out ≠ hồ sơ; `purchase` COD = đơn tạo).
- [ ] `generate_lead`/`purchase`/`application_complete` bắn từ dataLayer sau **kết quả nghiệp vụ thành công** (`success:true`/ID xác nhận), không phải HTTP 200; `transaction_id` ổn định; lớp dedup và chủ sở hữu (backend/client) ghi rõ, không dựa vào localStorage.
- [ ] Mỗi metric ghi đủ tử số · mẫu số · đơn vị · population · cửa sổ · dedup; outcome offline không join được → hai số riêng.
- [ ] Có bảng `parameter → scope → cần đăng ký? → quota còn lại`; `form_start` chỉ một nguồn phát; regex kênh AI là allowlist hostname có neo (full match) đã test positive/negative.
- [ ] Ca QA không thuộc cơ chế của site ghi N/A + lý do; gate G1 PASS = mọi ca P0 của cơ chế primary PASS.
- [ ] Không parameter nào chứa SĐT, email, tên, nội dung field, CV.
- [ ] Kết quả QA chưa chạy ghi "plan"; đã chạy ghi ngày, người, môi trường, PASS/FAIL từng ca.
- [ ] Không hứa độ chính xác %; ngưỡng lệch là quyết định của dự án, có lý do.
- [ ] Nếu là fork trong SEO Production: đúng path `13-cro/`, naming `<CLIENT>_…_v<N>.md`, item CR-06/CR-07 được trace.

## Anti-patterns

- Gắn `form_submit` ở click nút "Gửi" → đếm cả lần gửi lỗi. Làm đúng: bắn sau kết quả nghiệp vụ thành công (callback plugin / `success:true` / `lead_id`); HTTP 200 không đủ.
- Listener native `addEventListener` cho sự kiện plugin phát bằng jQuery `.trigger` (WPForms) → không bao giờ bắn. Làm đúng: `jQuery(document).on(...)`, đọc `form_id` từ payload, không gán ID mặc định.
- Trigger `purchase` theo URL `/cam-on` dùng chung cho mọi form. Làm đúng: dataLayer `event: purchase` + `transaction_id`.
- Tạo event `tel:` trong giao diện GA4. Làm đúng: GTM Just Links `Click URL starts with tel:`.
- Nút Zalo là plugin không có `<a>` → trigger Click URL không bắt. Làm đúng: inspect DOM, dùng Click Classes/ID hoặc All Elements có điều kiện.
- Báo "CVR kênh AI gấp 4×" từ 30 session. Làm đúng: nhãn directional, so cùng cửa sổ, ghi điểm mù.
- Đòi ngưỡng lệch GA4–CRM ≤5% cho mọi site. Làm đúng: ngưỡng theo dự án, ghi nguyên nhân lệch (consent, dedup, window, attribution).

## Changelog

- v1.1 (2026-09-13): vá theo review Astra F01–F05/F08/F09 — thành công = nghiệp vụ (không HTTP 200), listener WPForms jQuery, metric tử/mẫu/đơn vị tường minh, regex kênh AI full match + allowlist có neo, quota GA4, dedup không dựa localStorage, QA có N/A + gate theo cơ chế primary, kênh AI 13/05/2026 + điểm mù đúng phạm vi.
- v1.0 (2026-09-13): tạo mới từ wiki Inbound Marketing (measurement, patterns, ai-referral) theo plan CRO add-on đã duyệt 12/09.
