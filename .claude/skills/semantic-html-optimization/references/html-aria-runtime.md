# Kiểm HTML nguồn, DOM và ARIA sau tương tác

## Phân loại trước khi sửa

- HTML validator kiểm mô hình nội dung: `span` không chứa heading `h3`; đổi wrapper phù hợp và giữ selector/giao diện. Thẻ `<b>`/`<i>` có ngữ nghĩa riêng, không phải HTML lỗi; `<strong>` là mức quan trọng, `<em>` là nhấn ngữ điệu. [HTML Living Standard](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-b-element).
- `<aside>` có thể nằm trong bài; `<nav>` có thể nằm trong aside. `<article>` dùng khi khối có thể đứng độc lập, không tự bọc mọi card/FAQ. Thiếu heading là tín hiệu biên tập cần đọc ngữ cảnh, không tự động là lỗi cú pháp.
- Quét HTML thô để bắt thuộc tính lặp; DOM parser thường chỉ giữ một giá trị. Kiểm ID trùng và mọi `href`, `for`, `aria-controls`, `aria-labelledby` liên quan trước khi đổi ID.
- Phân biệt lỗi nguồn, lỗi plugin tạo lúc render và lỗi JS sau khởi tạo. Sửa nơi tạo lỗi; không sửa plugin vendor trực tiếp khi có hook phù hợp. Ghi giới hạn nếu chỉ có thể dùng adapter tại hook.

## Hợp đồng tương tác

| Widget | Kiểm bắt buộc |
|---|---|
| Tabs | `tablist` chứa các `tab`; panel là `tabpanel`, liên kết ID đúng; chỉ tab đang chọn có `aria-selected=true`; focus/tabindex, phím mũi tên, Home/End theo pattern |
| Accordion | Nút có tên, `aria-expanded`, `aria-controls` đúng panel; Enter/Space đổi trạng thái, heading và vùng ẩn thống nhất |
| Carousel dots | Mỗi nút có tên riêng theo vị trí/đích; trạng thái đang chọn cập nhật sau click, phím và autoplay khi có |
| Skip link | Tab thấy link, Enter chuyển focus đúng main; giữ `tabindex=-1` nếu cần nhận focus bằng code |
| Forms | Label liên kết đúng input, không phá honeypot/validation; ID của hai form không trùng; không gửi form thật chỉ để kiểm label |

Tabs chuyển thành accordion trên mobile phải kiểm cả hai breakpoint và khi resize: role, state, focus, panel không còn giữ thuộc tính của pattern cũ. `aria-selected` trên `role=button` không phải cách sửa tab. Đọc [WAI tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) và [WAI accordion](https://www.w3.org/WAI/ARIA/apg/patterns/accordion/).

## Sau sửa

- So chữ/ảnh/anchor/form, số widget và hình học trước/sau. Kiểm console và dependency runtime: số thẻ script ít hơn chưa chứng minh jQuery/slider/form chạy đúng.
- Axe là một nguồn bằng chứng; kiểm keyboard thật và tên accessible trong runtime. Cảnh báo chữ 0px của nút slider có thể là nhãn ẩn với icon hiển thị; đọc computed style và accessible name trước khi đổi CSS.
- Giữ dữ liệu nội dung sẵn cho render khi dùng tab/accordion. Có trong DOM giúp Google truy cập nội dung nhưng không bảo đảm được index hay “full weight”; Google không tương tác để tải nội dung phụ thuộc click. [Google mobile-first guidance](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing).
