# Bằng chứng trước và sau khi ghi

Đọc trước khi sửa DB, cache hoặc CSS dùng chung. Nguồn: kiểm chéo một đợt dọn comment trên site agency mẫu 05/11/2026. Đây là cổng kỹ thuật; quyền áp dụng lấy từ yêu cầu hiện hành, không tự xin lại quyền cùng phạm vi.

## 1. Đúng tài nguyên, đúng bản

- Ghi rõ entity, URL, bảng/ID hoặc file nguồn. Ảnh chụp site khác chỉ là mẫu lỗi, không chứng minh site đang audit còn lỗi.
- Chụp hash bản sống ngay trước sửa. Backup trên server ngoài webroot và thêm một bản local có quyền hạn chế; ghi lệnh rollback. Dump DB chứa dữ liệu riêng nằm ngoài thư mục deliverable được đồng bộ/chia sẻ; báo cáo chỉ giữ pointer và hash.
- Hash dùng byte gốc, không đọc text rồi chuẩn hoá CRLF/LF trước CAS. Một lần kiểm hash sai từng do `read_text()` đổi newline.
- Backup local đặt ở `~/Backups/<site>/<ngày>/<đợt>/`: thư mục 0700, file 0600. Báo cáo chỉ giữ pointer/hash.
- Rollback: kiểm archive và danh sách entry, chụp bản hiện tại, khôi phục đúng đường dẫn/owner/mode. Chỉ gỡ file mới do lô này thêm; không quét xoá theo glob rộng.
- Staging lệch production: ghi phần lệch và áp bản vá theo đúng đoạn/hash; không chép cả bản ghi cũ lên production. Backup mới không ghi đè backup trước.
- Trước khi sửa file staging, kiểm realpath và inode để loại symlink/hardlink sang production. Fixture tạm phải có backup và trả đúng byte cũ; ưu tiên override response trong trình duyệt nếu chỉ cần chuẩn hoá môi trường thử.
- Một người/agent sở hữu một tài nguyên. Tôn trọng khoá nguồn CSS, khoá HTTP và khe WP-CLI hiện có. Không chạy benchmark trong lúc agent khác đang purge hoặc sửa cấu hình cùng site.

## 2. Kết quả lệnh không thay cho trạng thái thật

- `exit 0`, `Success` hoặc output rỗng chưa chứng minh đã ghi. Script phải trả ID, hash trước/sau, số mục khớp/đổi/bỏ qua; dừng nếu thiếu hoặc sai số dự kiến.
- Chạy WP-CLI bằng user web server. Chỉ thao tác filesystem cần quyền mới dùng root; `--allow-root` không phải cách chạy mặc định.
- WP-CLI có thể không dùng cùng object cache với web. Sau ghi DB, xoá đúng key/group theo API và drop-in đang dùng; kiểm lại bằng getter WordPress trong tiến trình mới, trạng thái object cache và HTML origin mới. Không dùng `flushall` để chữa một bản ghi cũ.
- Payload dài: dùng file đầu vào hoặc chia dòng trong `eval-file`; không nhét một dòng base64 cực dài. Lượt mẫu từng trả mã 0 kèm giá trị `null`, bản ghi không đổi. Không đổi cấu hình PHP toàn server chỉ để vượt lỗi truyền input.
- Chỉ đưa tên khoá và kết quả đã che vào output. Không `cat`/`grep` cả `wp-config.php`, `.env` hay dump cấu hình. Chọn trường cần đọc trong code, giữ secret trong bộ nhớ.
- Che hostname staging trong cả trường JSON lồng nhau trước khi ghi file hoặc in output. Chỉ che chuỗi console chưa đủ nếu `href`, stack hoặc network record còn URL gốc. Leakcheck chỉ trả số lượng và đường dẫn đã che.

## 3. Chọn kiểm chứng theo tác động

| Thay đổi | Bằng chứng cần có |
|---|---|
| Chỉ comment PHP/JS/CSS | So token bằng parser tương ứng; giữ chuỗi, license, directive có chức năng. Staging đọc lại đúng nguồn; so output qua pipeline thực tế |
| Comment trong Additional CSS | Chạy đúng minifier đang dùng với hai bản, so byte/hash đầu ra. Kiểm selector trong CSS đang phục vụ và map ở 4 biến thể cache |
| DOM, CSS hiệu lực, JS hoặc ARIA | Staging có bản nguồn tương ứng; ảnh/hình học và tương tác, keyboard, console. CSS async/font/CLS cần A/B ở điều kiện tái hiện lỗi |
| Config cache cấp site | Lưu giá trị cũ, thử phạm vi đã chọn, kiểm nhiều template/biến thể và ngưỡng rollback trước production |

Đổi `id` hoặc thuộc tính của thẻ style có thể đổi cách optimizer gom và khử trùng CSS, dù nội dung CSS giữ nguyên. Chạy cả bước thu thập nguồn CSS của plugin, không chỉ minifier của một chuỗi. Style trong noscript phải giữ đúng hành vi khi bật/tắt JavaScript sau pipeline production.

Sửa jQuery trùng cần kiểm dependency WordPress và hook delay thật của phiên bản cache đang chạy. Một hook được đăng ký nhưng plugin không gọi vẫn không có hiệu lực. Loader chạy sớm có thể nạp fallback trước core; xoá thẻ CDN riêng lẻ chưa đủ. Kiểm số thư viện, version trước/sau tương tác và slider sau resize.

Exclude khỏi Delay JS có thể đưa script về trạng thái chặn hiển thị. Kiểm FCP/LCP và render-blocking sau optimizer, cùng click đầu và tương tác sau khi chờ lâu. Không coi “một jQuery, không lỗi console” là đủ để kết luận bản sửa đạt tốc độ.

Kiểm thời điểm plugin đọc hook. Conditional tag như `is_page()` không đáng tin trước main query. Không ép `defer` khi WordPress từ chối vì dependency hoặc inline-after; phải hiểu chuỗi thực thi trước.

Staging có thể rewrite HTML nhưng không rewrite URL trong CSS tĩnh. Khi kiểm preload, so URL chuẩn hoá gồm scheme, host, port, path và định dạng ảnh. Giữ URL trình duyệt chuẩn, đặt tunnel ở lớp kết nối. Sai lệch fixture không phải lỗi production; không dùng lượt thiếu asset hoặc bị chặn DNS làm bằng chứng đạt. Smoke một URL trước khi chạy ma trận.

Nếu chỉ comment đổi, đầu ra minify giống từng byte, hash CSS gộp và map không đổi ở các biến thể: không cần dựng thêm mu-plugin preview, đổi cache config hay chờ job CSS đêm. Vẫn xác minh nguồn DB mới và HTML origin. Byte nguồn giảm không đồng nghĩa byte mạng giảm.

Nếu đầu ra thay đổi hoặc chưa chứng minh được tương đương: giữ cổng staging/A-B và tái tạo CSS cần thiết. Không suy từ riêng chữ “comment” rằng mọi pipeline đều bỏ qua nó.

## 4. Đóng lượt ghi

- Asset đổi byte phải có URL/version mới theo cơ chế site. Purge CDN không xoá cache trình duyệt đã nhận; kiểm URL cuối sau các filter bỏ version và xác minh nội dung ở CDN.
- Purge đúng phạm vi output thay đổi, kiểm trạng thái từng URL/retry lỗi CDN, rồi lấy bản cache URL sạch để so robots/canonical. Query bỏ cache có thể tự noindex; không dùng nó để kết luận lỗi SEO.
- Kiểm origin mới cùng cache đang phục vụ. Site có CSS gọn: lưu hash file gộp/map trước và sau, số cặp path × biến thể đang phủ và số cặp bị mất mới. Chi tiết ở `wp-ucss`.
- Nếu cửa sổ health đi qua log rotation, đọc cả file xoay vòng. Helper chỉ đọc file hiện tại không chứng minh cả cửa sổ.
- Health ghi giờ bắt đầu, giờ kết thúc, timezone, file log và số request thực sự đọc được. Parser lỗi, file thiếu hoặc không có dữ liệu phải báo chưa xác minh; không biến thành “0 lỗi”.
- Ghi rõ phần đã kiểm và chưa kiểm. Không lấy một trang đạt để tuyên bố toàn database/site sạch.
