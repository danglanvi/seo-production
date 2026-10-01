# Feature brief theo component — để dev khách làm không hỏi lại

Mục đích: bước 4 của cro-audit, điền vào template `ux-feature-brief.md` (#35). Brief tốt = dev đọc xong biết chính xác DOM, hành vi từng trạng thái, event và điều kiện nghiệm thu; không còn chỗ để đoán. Nguồn: wiki `concepts/cro/ux-ui` §"Chuẩn brief", `patterns/*` §"Spec sửa mẫu".

## §1. Mười mục bắt buộc của một component

| # | Mục | Ghi gì |
|---|---|---|
| 1 | Task người dùng | Một câu: khách đang cố làm gì ở đây |
| 2 | Vấn đề có bằng chứng | Finding ID + nhãn P/R/E + số/ảnh |
| 3 | Nội dung | Chữ thật (copy do client duyệt nếu là giá/cam kết/SLA), số field, lựa chọn của select |
| 4 | Vị trí và DOM order | Block trong structure brief (không đổi block map); thẻ semantic (`section > h2 > …`); `data-*` để đo |
| 5 | Hành vi desktop / mobile | Sticky? Thu gọn? Điểm ngắt? Kích thước chạm ≥44px (chuẩn nội bộ, không phải WCAG AA 24px) |
| 6 | Trạng thái | loading · success · error · empty · disabled — mỗi trạng thái nói gì, khách làm gì tiếp |
| 7 | Keyboard, label, focus | Label hiện cố định + `for/id`; focus không bị sticky che; tab order |
| 8 | Event | Tên, trigger, tham số (không PII) — khớp measurement plan |
| 9 | Acceptance | Điều kiện PASS đo được: "trên 390px thấy H1 + CTA không cuộn", "20/20 đơn thử khớp backend", "gửi thành công 3 môi trường" |
| 10 | Rollback | Cách quay lại bản cũ trong ≤1 giờ; điều kiện rollback (lỗi P0 mới, outcome giảm rõ sau 2 tuần) |

Thiếu mục nào → brief chưa xong. Figma/screenshot không thay được mục 6–10.

## §2. Ba ví dụ ngắn (điền theo bối cảnh client)

**cta-call (gọi):** `<a href="tel:+84…" data-cta-position="hero">` hiện số dạng `0901 234 567`; desktop hiện thêm Zalo/QR cạnh số; ≥44px; event `click_to_call{position}`. Acceptance: iOS/Android mở dialer đúng số; 1 event/1 click; desktop không lỗi JS.

**form-lead-short (form):** 3 field Họ tên · SĐT (`type=tel`, nhận `0…`/`+84…`, có dấu chấm) · Nhu cầu (select 4–6, client chốt); label cố định; lỗi inline giữ dữ liệu; nút theo outcome; success = khối/URL riêng nêu ai gọi lại, khi nào, có Zalo; event `generate_lead{form_id, lead_type}` sau 200. Acceptance: gửi OK 3 môi trường; lead tới đích ≤10 phút; không PII trong event.

**buy-box (PDP):** giá áp dụng + gạch giá gốc có hạn · swatch variant còn/hết · tồn kho + ước ngày nhận theo tỉnh · Thêm vào giỏ / Mua ngay / Hỏi Zalo · 3 dòng chính sách; sticky mobile thu gọn (giá + Thêm vào giỏ). Acceptance: thiếu variant → lỗi inline + cuộn tới; `add_to_cart` đủ `items[].item_variant/price`; sticky không che nội dung ở 360/390/430.

## §3. Điền vào template `ux-feature-brief.md`

- §1 Bối cảnh: số liệu có mẫu số + cửa sổ; "vấn đề người dùng" = finding có nhãn E≥2.
- §2 Tính năng: cột "Vì sao" = finding ID + pattern § + item CR/UX; cột "Kỳ vọng đo được" ghi **metric theo dõi + cửa sổ ≥4 tuần, nhãn quan sát** — không ghi "CR +x%".
- §3 Spec cho Coder: bảng theo 10 mục ở §1 (gộp cột nếu cần), một dòng mỗi component.
- §4 Đo sau triển khai: ngày deploy (annotation GA4) · đọc sau 14 ngày (kiểm lỗi) và ≥4 tuần trọn (đọc số) · điều kiện rollback.
- Trạng thái brief: đề xuất → khách duyệt → đã sửa (ngày) → chờ khách (ngày brief). Cột này đi vào report tháng khối 3.

## §4. Không làm

- Không thay heading hierarchy, URL, internal link đã duyệt trong brief CRO; cần đổi → ghi "route trạm 04".
- Không viết copy giá, SLA, cam kết mà client chưa duyệt; đánh dấu `{{client chốt}}`.
- Không brief "làm gọn hơn/đẹp hơn/nổi bật hơn" — phải ra kích thước, vị trí, nội dung, trạng thái.
- Không gộp 6 component vào một brief không có thứ tự ưu tiên; mỗi brief nêu P0 trước.
