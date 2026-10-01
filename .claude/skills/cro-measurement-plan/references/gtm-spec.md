# Spec GTM cho dev/khách — viết sao để làm được không hỏi lại

Mục đích: khung viết phần C của measurement plan. GTV không sửa container của khách; GTV giao spec, người có quyền làm, GTV kiểm bằng Preview/DebugView (khi được cấp quyền xem). Kỹ thuật tham chiếu: Analytics Mania (GTM click tracking), Nimbata/KRM (tel:/mailto qua GTM), trangwebvang (dạng nút Zalo VN), tài liệu WPForms/CF7; tóm tắt trong wiki `patterns/call-zalo-messenger`, `patterns/form-lead`. v1.1 (13/09/2026, sau review Astra F01/F03/F05/F09).

## §1. Inventory DOM trước khi viết trigger

Mở site trên mobile + desktop, DevTools → Inspect từng điểm chuyển đổi. Ghi bảng:

| Điểm | Vị trí | Dạng DOM | Bắt bằng | Ghi chú |
|---|---|---|---|---|
| Nút gọi header | header | `<a href="tel:+84…">` | Click URL starts with `tel:` | OK |
| Nút gọi hero | hero | `<button onclick="…">` không href | Click ID / Click Classes; đề xuất đổi sang `<a href="tel:">` | Kiểm task thực: JS có mở dialer không |
| Zalo | nút nổi | `<div class="fcta-zalo">` (plugin) | Click Classes contains `fcta-zalo` | Không có `<a>` |
| Zalo | footer | `<a href="https://zalo.me/09…">` | Click URL matches RegEx `^https?://(oa\.)?zalo\.me/` | Số cá nhân — ghi rủi ro vận hành |
| Form tư vấn | trang dịch vụ | Contact Form 7 (AJAX) | Listener `wpcf7mailsent` → dataLayer | Không dùng Form Submission trigger |
| Form tư vấn | landing | WPForms AJAX (`.wpforms-ajax-form`) | Listener jQuery `wpformsAjaxSubmitSuccess` → dataLayer (xem §5) | Sự kiện phát bằng jQuery `.trigger`, native `addEventListener` không nhận |
| Form đăng ký | landing | iframe HubSpot | Callback `onFormSubmitted` → dataLayer, hoặc redirect thank-you | Không có → ghi "không đo được" |
| Trang cảm ơn | `/cam-on` | Dùng chung cho 3 form | Cần `?form=<id>` hoặc dataLayer từ form | Không dùng URL trần |
| Checkout | WooCommerce | dataLayer plugin (GTM4WP) | `event: purchase` | Kiểm bắn ở trang order-received, không ở checkout |
| Cổng thanh toán | VNPay/MoMo | Redirect ra ngoài, quay về `/order-received/<id>?vnp_…` | Trang quay về đọc trạng thái đơn từ backend | Tham số URL không phải bằng chứng thành công; Page Path không chứa query — inspect biến thực trước khi kết luận trigger |

Dạng nút Zalo trên web VN: `zalo.me/<sđt>`, `oa.zalo.me/<oa>`, nút nổi plugin (WordPress "Floating Contact", "Button Contact VR"), nút trong landing builder (Ladipage). Mỗi dạng một trigger. Ghi thêm: script có bị trì hoãn tải (LiteSpeed/WP Rocket delay JS) → thời điểm bind listener phải sau khi dependency có mặt.

## §2. Biến GTM cần bật

Built-in: Click Element, Click Classes, Click ID, Click URL, Click Text, Page Path, Page URL, Form ID/Classes (ít dùng). User-defined: `GA4 Measurement ID` (constant), `page_type` (Lookup Table theo Page Path hoặc dataLayer từ theme), `position` (Lookup theo Click Classes/ID hoặc `data-cta-position` — đề xuất dev thêm attribute vào nút).

## §3. Trigger mẫu

| Tên trigger | Loại | Điều kiện |
|---|---|---|
| `Click – Tel` | Click – Just Links (Wait for tags 500ms, Check validation) | Click URL starts with `tel:` |
| `Click – Zalo link` | Just Links | Click URL matches RegEx `^https?://(oa\.)?zalo\.me/` |
| `Click – Zalo plugin` | Click – All Elements | Click Classes contains `<class plugin>` OR Click Element matches CSS selector `.<class> *` |
| `Click – Messenger` | Just Links | Click URL matches RegEx `^https?://m\.me/` |
| `CE – generate_lead` | Custom Event | Event name `generate_lead` (dataLayer push từ form success nghiệp vụ) |
| `CE – purchase` | Custom Event | Event name `purchase` |
| `CE – application_complete` | Custom Event | Event name `application_complete` |
| `Vis – form error` | Element Visibility | CSS `.wpcf7-not-valid-tip, .wpforms-error, .error-message`; once per element |

Không dùng: GA4 "Create event" trong giao diện cho `tel:`/`mailto:` (không ổn định); "Form Submission" trigger cho form AJAX (bắn cả lần lỗi); trigger theo Page Path/URL cho `purchase`; `contains zalo`/`contains m.me` trên toàn URL (bắt nhầm chuỗi). GA4 và GTM regex: kiểm chế độ khớp (full/partial) của từng nơi trước khi viết.

## §4. Tag mẫu (GA4 Event)

| Tag | Event name | Parameters |
|---|---|---|
| `GA4 – click_to_call` | `click_to_call` | `page_type={{page_type}}`, `position={{position}}` |
| `GA4 – click_zalo` | `click_zalo` | `page_type`, `position`, `zalo_target={{lookup oa/personal}}` |
| `GA4 – generate_lead` | `generate_lead` | `form_id={{dlv – form_id}}`, `lead_type={{dlv – lead_type}}`, `page_type` |
| `GA4 – purchase` | `purchase` | `transaction_id`, `value`, `currency`, `items`, `payment_type` — đọc từ dataLayer, không nhập tay |

Gộp thành một tag "GA4 – contact_click" chỉ khi client muốn một key event chung; khi đó không cộng thêm 3 event riêng vào tổng key event.

## §5. dataLayer push mẫu cho dev

```js
// WPForms (AJAX): sự kiện được phát bằng jQuery .trigger(...) sau khi response.success === true
// → phải dùng jQuery .on, không dùng document.addEventListener. Bind sau khi jQuery + wpforms sẵn sàng (delay JS).
jQuery(document).on('wpformsAjaxSubmitSuccess', function (event, data) {
  var formId = data && data.data && data.data.form_id;          // đọc từ payload thật
  if (!formId || formId !== '124208') { return; }              // chỉ form trong plan; thiếu payload → không phát, không gán mặc định
  window.dataLayer = window.dataLayer || [];
  dataLayer.push({ event: 'generate_lead', form_id: String(formId), lead_type: 'consult' });
});

// Contact Form 7: sự kiện DOM native
document.addEventListener('wpcf7mailsent', function (e) {
  dataLayer.push({ event: 'generate_lead', form_id: String(e.detail.contactFormId), lead_type: 'consult' });
});

// Đơn hàng — chỉ ở trang xác nhận, sau khi backend tạo đơn (trạng thái nghiệp vụ); render từ server
dataLayer.push({
  event: 'purchase',
  ecommerce: { transaction_id: 'ORD-10231', value: 1290000, currency: 'VND',
    shipping: 30000, tax: 0, payment_type: 'cod',
    items: [{ item_id: 'SKU-1', item_name: 'Máy lọc nước A', price: 1290000, quantity: 1, item_variant: 'trắng' }] }
});

// Apply hoàn tất — sau khi ATS trả application_id (ID chỉ giữ backend, không đẩy thành dimension)
dataLayer.push({ event: 'application_complete', job_id: 'J-8842', apply_type: 'onsite' });
```

Dedup `purchase`: `transaction_id` ổn định là nền (GA4 xử lý purchase trùng ID theo luật Google); backend/server-side idempotency là lớp chính; cờ client (`sessionStorage`) chỉ là lớp phụ và phải ghi rõ: storage không tự hết hạn, ghi cờ khi push chưa chứng minh tag đã gửi. Không mô tả localStorage 24h như cơ chế đảm bảo.

## §6. Quy trình kiểm

1. GTM Preview → thao tác từng điểm trên mobile thật (iOS Safari + Android Chrome) và desktop; ghi event, tham số, số lần bắn.
2. GA4 DebugView cùng lúc; xác nhận tên và tham số khớp plan.
3. Ca lỗi bắt buộc: gửi form thiếu field; **HTTP 200 nhưng nghiệp vụ thất bại** (`success:false`/`action_required`); double click nút gửi; reload trang cảm ơn; nhiều tab; storage không khả dụng; quay lại từ cổng thanh toán bằng Back; huỷ ở cổng; tag bị chặn (ad-block) để thấy lead backend vẫn có nhưng GA4 không.
4. Publish container có ghi version note "measurement-plan v<N> <ngày>".
5. **QA chức năng ngay sau deploy** (cùng ngày); sau 48 giờ kiểm Realtime/Reports thấy event thật; sau 7 ngày đối soát theo `reconciliation-qa.md`. Cửa sổ ≥4 tuần chỉ áp cho đọc số kết quả kinh doanh, không phải cho QA.

## §7. Khi thiếu quyền

Không có quyền GTM/GA4: viết spec đầy đủ, đánh dấu từng dòng "chờ dev", kiểm bằng cách bấm thật trên site + xem Network (request `collect?v=2` tới google-analytics.com) — thấy `en=click_to_call` là bắn. Ghi rõ "chưa kiểm DebugView" trong trạng thái; không gọi là PASS.
