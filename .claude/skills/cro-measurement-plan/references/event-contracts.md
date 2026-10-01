# Event contracts theo cơ chế chuyển đổi

Mục đích: bảng tra để chọn bộ event, tham số, nguồn xác nhận và điều kiện cho từng cơ chế. Tên GA4 recommended lấy từ tài liệu Google (`developers.google.com/analytics/devguides/collection/ga4/reference/events`); tên custom là quy ước GTV. Nguồn: wiki Inbound Marketing (`concepts/cro/measurement`, `patterns/*`, `ai-referral`), tóm tắt để skill chạy standalone. v1.1 (13/09/2026, sau review Astra F02/F03/F05/F08/F09): định nghĩa metric tường minh, "thành công" = nghiệp vụ, regex full match, quota GA4, dedup không dựa localStorage.

## §1. Outcome, mẫu số, đơn vị — định nghĩa metric bắt buộc

Mỗi metric trong plan phải ghi đủ: **tử số · mẫu số · đơn vị · điều kiện vào cohort · cửa sổ · cách dedup**. Ba dạng chuẩn (theo cách GA4 tính key event rate):

| Metric | Tử số | Mẫu số | Ghi chú |
|---|---|---|---|
| **User CVR** | user đủ điều kiện có ≥1 outcome trong cửa sổ | user đủ điều kiện | Không dùng `event_count / users` |
| **Session CVR** | session đủ điều kiện có ≥1 event/outcome đã chọn | session đủ điều kiện | Không cộng nhiều key event rồi chia session |
| **Volume / per-user** | số event, số đơn/user, revenue/user | — | Tách khỏi rate, báo riêng |

"Đủ điều kiện" (population) phải cùng định nghĩa ở tử và mẫu: form đặt ở home nhưng mẫu số chỉ đếm người vào trang dịch vụ → hoặc tính cả home vào cả hai, hoặc loại khỏi cả hai. Outcome offline (cuộc gọi, chat) chỉ có tổng từ nhật ký/Sheet, không nối được với user web → báo **hai số riêng** (click web; lead đối soát) và ghi giới hạn attribution, không công bố "qualified-user CVR" như đã đo trực tiếp. Metric kênh AI dùng một outcome đã chốt, cùng population với Organic Search.

| Mô hình | Primary (đề xuất, client chốt) | Population | Đơn vị | Guardrail |
|---|---|---|---|---|
| Dịch vụ local (gọi/Zalo) | Lead đạt chuẩn (Sheet) — báo riêng cạnh click CVR | User/session có ≥1 trang dịch vụ/liên hệ | user (click) + đếm (lead) | Spam, ngoài giờ không bắt máy, không liên lạc được |
| Dịch vụ B2B (form) | User CVR `generate_lead`; lead đạt chuẩn theo cohort | Như trên | user | Spam, trùng, sai SĐT, thời gian phản hồi đầu |
| Báo giá | Yêu cầu hợp lệ → báo giá đã gửi → phản hồi | Yêu cầu hợp lệ | yêu cầu | Thiếu thông tin phải hỏi lại, ngoài năng lực, SLA |
| Ecommerce | User CVR `purchase` (đơn tạo) + đơn hợp lệ theo cohort | User vào PDP hoặc giỏ | user | Huỷ/hoàn, bom COD, lỗi thanh toán, đơn trùng |
| Job site — ứng viên | Completion = `application_complete` / `apply_start` | candidate–job đã bắt đầu | candidate–job | Trùng, trống, lỗi upload, không phản hồi |
| Job site — nhà tuyển dụng | Tin đăng hợp lệ / doanh nghiệp đăng ký | doanh nghiệp | account | Tin giả, chưa xác minh, support load |

Cửa sổ, timezone (Asia/Ho_Chi_Minh) và định nghĩa population ghi trong plan, giữ nguyên qua các kỳ.

## §2. Gọi · Zalo · Messenger

| Event | Trigger | Tham số | Nguồn xác nhận outcome | Ghi chú |
|---|---|---|---|---|
| `click_to_call` | Just Links, `Click URL starts with tel:` | `page_type`, `position` (header/inline/sticky/footer) | Nhật ký cuộc gọi / tổng đài / Sheet lead | Event đo **thao tác click**, không xác nhận OS mở dialer hay cuộc gọi kết nối; QA click và hành vi gọi riêng (desktop huỷ mở app vẫn có event) |
| `click_zalo` | Just Links `Click URL matches RegEx ^https?://(oa\.)?zalo\.me/` hoặc Click Classes/ID cho nút plugin | `page_type`, `position`, `zalo_target` = oa/personal | Hộp thư Zalo OA, Sheet lead | Kiểm hostname thật, không `contains zalo` (bắt nhầm URL khác chứa chuỗi) |
| `click_messenger` | Just Links `Click URL matches RegEx ^https?://m\.me/` hoặc listener plugin FB | `page_type`, `position` | Inbox fanpage | Plugin FB chat không luôn có DOM click bắt được |
| `contact_click` (gộp, tuỳ chọn) | Regex hostname/protocol | `contact_channel` | — | Chỉ khi client muốn 1 key event chung; khi đó **không** cộng thêm 3 event riêng vào tổng key event (đếm trùng) |

Không đặt SĐT hoặc nội dung chat vào parameter. Key event: `click_to_call`, `click_zalo` với counting method "once per session" — đây là cách đếm key event, không làm giảm `event_count`.

## §3. Form lead

| Event | Trigger | Tham số | Điều kiện |
|---|---|---|---|
| `form_start` | **Quyết định một nguồn phát**: Enhanced Measurement "Form interactions" (tự thu, tên reserved `form_start`/`form_submit`) HOẶC listener riêng — không cả hai. Nếu cần định nghĩa focus riêng, dùng tên khác (`form_focus`) | `form_id`, `page_type` | Một lần mỗi form mỗi trang |
| `form_error` | dataLayer từ form hoặc Element Visibility trên phần tử lỗi | `form_id`, `field`, `error_type` | Không gửi giá trị field |
| `generate_lead` (recommended) | dataLayer **sau kết quả nghiệp vụ thành công** của plugin/backend (`success:true`, `lead_id`, hoặc callback thành công như WPForms `wpformsAjaxSubmitSuccess`, CF7 `wpcf7mailsent`) | `form_id`, `lead_type` (consult/quote/register), `page_type`, `value`/`currency` nếu client định giá lead | **HTTP 200 không đủ** (200 có thể kèm `success:false`/validation error/action_required). Không bắn ở click nút. Form iframe → callback/redirect; không đo được thì ghi rõ |
| `qualify_lead`, `close_convert_lead` (recommended) | Từ CRM, không từ web | `lead_type` | Thường đối soát bằng Sheet; Measurement Protocol chỉ khi có ID chung |

## §4. Báo giá

Như §3 với `lead_type=quote`, thêm `product_type`, `quantity_band` (không số chính xác nếu nhạy cảm), `has_file` (true/false). Micro thêm: `view_pricing`, `calc_use` (`calc_step`). Outcome ở Sheet báo giá: nhận → đã báo giá (giờ) → phản hồi → chốt.

## §5. Giỏ hàng · checkout (GA4 recommended)

| Event | Điều kiện bắn | Bắt buộc |
|---|---|---|
| `view_item_list`, `select_item`, `view_item` | Từ dataLayer của theme/plugin ecommerce | `items[]` có `item_id`, `item_name`, `price`, `item_variant`, `currency=VND`. Sản phẩm không có giá công khai: vẫn bắn hành vi với dữ liệu có thật, **không bịa `price`/`value`**; ghi giới hạn: thiếu tham số bắt buộc thì ecommerce report có thể xử lý event như custom |
| `add_to_cart`, `view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info` | dataLayer | `value` = tổng của items; `shipping_tier`, `payment_type` |
| `purchase` | **dataLayer sau khi backend tạo đơn** (trạng thái nghiệp vụ, không phải HTTP 200), ở trang xác nhận đơn hoặc server-side; trigger theo dataLayer, không theo URL | `transaction_id` duy nhất và ổn định, `value`, `currency`, `items`, `payment_type` (cod/bank_qr/vnpay/momo/card), `shipping`, `tax` |
| `refund` | Khi phát sinh, từ backend | `transaction_id` |

**Dedup:** khai rõ lớp và chủ sở hữu. (1) `transaction_id` ổn định là nền: GA4 xử lý `purchase` trùng `transaction_id` theo luật của Google, **không** mặc định mọi custom event được dedup như vậy. (2) Server-side/backend idempotency là lớp chính khi có. (3) Cờ client (`sessionStorage`/`localStorage`) chỉ là lớp phụ: storage không tự hết hạn, ghi cờ khi push chưa chứng minh tag đã gửi (tag bị chặn → mất số), nhiều tab/storage không khả dụng là ca QA riêng. Cổng thanh toán redirect: trang quay về phải nạp GTM và đọc trạng thái đơn từ backend, không từ query string. COD: `payment_type=cod`; report tách "đơn tạo" và "đơn hợp lệ".

## §6. Apply · ATS (custom)

| Event | Trigger | Tham số |
|---|---|---|
| `view_job` | Page view trang job detail | `job_id`, `employer_id`, `salary_shown` (true/false), `apply_type` (onsite/offsite) |
| `apply_click` | Click nút ứng tuyển | `job_id`, `apply_type`, `position` |
| `apply_start` | Mở form (onsite) hoặc rời sang ATS (offsite; Just Links outbound kèm `job_id`) | `job_id`, `apply_type` |
| `application_submit` | Client-side sau khi gửi form | `job_id` |
| `application_complete` | dataLayer sau khi backend/ATS trả `application_id` (kết quả nghiệp vụ) | `job_id`, `apply_type`; `application_id` **không đăng ký thành custom dimension** (cardinality cao) — chỉ giữ ở backend để đối soát |
| `application_qualified` | Từ ATS/HR, ngoài GA4 → đối soát cohort | `job_id` |

Offsite không có callback → plan ghi "đo tới apply_start (click-out)". Không gửi CV/SĐT/email vào bất kỳ parameter nào. Employer funnel: `employer_signup_start` → `employer_verified` → `job_post_published` → `job_post_paid`.

## §7. Kênh AI Assistant

- GA4 từ **13/05/2026**: medium `ai-assistant`, campaign `(ai-assistant)`, kênh "AI Assistant" khi referrer khớp AI được nhận diện (ví dụ ChatGPT, Gemini, Claude; danh sách đầy đủ chưa công bố). Không referrer → Direct. **AI Overviews/AI Mode thuộc Organic Search.** Không hồi tố phân loại mặc định.
- Custom channel group (phủ nguồn Google chưa nhận + dữ liệu cũ còn source): kênh "AI Traffic" = `Source matches regex <allowlist>` **OR** `Medium exactly matches ai-assistant`; **đặt trên Referral**. **GA4 "matches regex" là full match** — dùng allowlist hostname có neo, ví dụ minh hoạ (bổ sung sau khi xác minh source thật trong property): `^(.*\.)?(chatgpt\.com|chat\.openai\.com|claude\.ai|perplexity\.ai|gemini\.google\.com|copilot\.microsoft\.com|you\.com|chat\.deepseek\.com|grok\.com)$`. Không dùng token ngắn với full match (under-match) và không thêm `.*` bừa (over-match `chatgpt.example.org`, `notyou.com`); `bing.com/chat` là path, không phải source. Test positive/negative, chữ hoa, subdomain thật, medium mới, referral cũ. Review theo quý, ghi ngày.
- Điểm mù ghi trong plan: một số link in-content ở ChatGPT trả phí không gửi referrer (Ahrefs quan sát; không phải mọi paid/mọi link) → Direct nếu không có UTM; app mobile không referrer; AI Overviews/AI Mode lẫn Organic; khách hỏi AI rồi search brand → branded organic. Ghi "phần AI referral nhận diện được, có điểm mù attribution"; không gọi là "sàn".
- Điểm dữ liệu thứ hai: thêm "ChatGPT / AI" vào câu "biết chúng tôi từ đâu" ở form và script sale (tuỳ client duyệt).
- Report: session · CVR một outcome đã chốt (cùng population với Organic) · top landing AI vs Organic, theo loại trang; nhãn **directional, không nghiệm thu**; hàng AI là phân đoạn của các cơ chế, không cộng vào tổng conversion lần nữa.

## §8. Tham số, quota GA4 và privacy

Tham số nội bộ nên có: `page_type`, `intent_cluster` (nếu có topical map), `position`, `form_id`, `experiment_id`/`variant` (khi test). Cấm: SĐT, email, tên, địa chỉ, nội dung field, tên file CV, `search_term` chứa PII, ID ứng viên/đơn ở dạng dimension.

**Bảng quota bắt buộc trong plan** (`parameter → scope → cần đăng ký custom dimension? → quota còn lại`), theo giới hạn Google hiện hành (kiểm 13/09/2026): tên event ≤40 ký tự, ≤25 event parameter/event, tên/giá trị parameter có giới hạn ký tự; custom dimension **event-scoped 50 (Standard property)**, user-scoped 25, item-scoped 10. Chỉ đăng ký dimension cần report; dùng dimension có sẵn khi có; tránh cardinality cao. Tên custom trong bộ này (`click_zalo`, `apply_start`, `application_complete`, `quote_start`…) không nằm trong danh sách reserved tại thời điểm kiểm; `form_start`/`form_submit` là tên tự thu của Enhanced Measurement → xử lý theo §3.

Consent: "không thấy banner" ≠ đã biết consent state. Ghi cấu hình thật (không consent mode / basic / advanced); tỷ lệ từ chối chỉ là nguyên nhân lệch khi đã kiểm cấu hình.
