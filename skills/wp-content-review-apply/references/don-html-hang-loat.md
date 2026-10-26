# Dọn HTML thừa hàng loạt

Mục đích: làm sạch rác HTML trong `post_content`, `_elementor_data`, meta ACF và widget mà chữ hiển thị không đổi. Rác thường gặp: entity mã hoá 2 lần (`&amp;nbsp;`), `<span style="font-weight:400">` dán từ Google Docs, `docs-internal-guid`, `aria-level`, `dir="ltr"`, bookmark TinyMCE (`mce_SELRES`), BOM, `<p>&nbsp;</p>`, thẻ rỗng. Đọc file này khi chọn chế độ "Dọn HTML thừa". Gốc đường dẫn là root repo, script ở `skills/wp-content-review-apply/scripts/`.

Việc này không đổi chữ, nên không đi qua thẻ duyệt. Người vận hành duyệt cả lô sau khi xem kết quả trên URL mẫu (bước 7).

Số đo thật, site agency mẫu 19/10/2026: HTML 377 trang giảm 226 KB, 1.218 thẻ `<p></p>` rỗng về 0. Lần ghi đầu áp 130 bài khi chưa có cổng wpautop: một bài đổi bố cục từ y≈4876, phải rollback. Sau khi thêm cổng, `compare_autop.php` báo 55/130 bài khác cấu trúc, sửa luật còn 0/126.

## 1. Hai bất biến

Mỗi mục ghi phải giữ cả hai. Mục không giữ được thì bỏ khỏi lô, không sửa tay cho qua.

1. Chữ hiển thị không đổi: bỏ thẻ inline, entity, BOM, NBSP, khoảng trắng rồi so.
2. Cấu trúc sau `wpautop` và `do_blocks` không đổi: đoạn, xuống dòng, khối. Cổng thật là `compare_autop.php` chạy trên site bằng `wpautop` của WordPress, phải ra 0 khác biệt. Bản port wpautop trong `cruft_clean.py` chỉ kiểm sơ bộ.

Lỗi bố cục 19/10 đến từ việc gỡ `<span>` chỉ chứa xuống dòng. `wpautop` đổi xuống dòng đó thành `<br>` hoặc đoạn mới, nên bố cục lệch dù chữ giữ nguyên.

## 2. Quy trình

1. Đo trước (chỉ đọc). Chỉ gọi site khi người vận hành cho phép đo trang thật, dùng URL sạch không `utm_*`:
   `python3 -I skills/wp-content-review-apply/scripts/cruft_scan.py urls.txt --out scan_truoc.jsonl --workers 6`
2. Xuất dữ liệu (chỉ đọc DB). Thử nhỏ trước bằng `LIMIT=20`. Chạy một tiến trình nặng mỗi lúc (`ghi-an-toan.md` mục 2):
   `OUT=/tmp/<phiên>/export.json <lệnh wp> --path=<root> eval-file /tmp/<phiên>/export_cruft.php`
   File ra có md5 của từng giá trị thô. `apply_cruft.php` so md5 này trước khi ghi.
3. Làm sạch offline, tách ca mơ hồ cho Jev:
   `python3 -I skills/wp-content-review-apply/scripts/cruft_clean.py export.json out/ --emit-jev`
4. Chạy Jev cho ca mơ hồ, mỗi lượt có `--budget`:
   `python3 -I tools/ai-assist/jev.py --task tools/ai-assist/tasks/nbsp-intent.json --in out/jev_nbsp_in.jsonl --out nbsp_out.jsonl --budget 0.2`
   `python3 -I tools/ai-assist/jev.py --task tools/ai-assist/tasks/inline-style-residue.json --in out/jev_style_in.jsonl --out style_out.jsonl --budget 0.2`
   Hai rubric này chưa hiệu chuẩn. Claude đọc lại mọi nhãn `plain_space` và `paste_residue`, vì hai nhãn này làm script xoá.
5. Áp quyết định Jev: chạy lại bước 3 với `--jev-nbsp nbsp_out.jsonl --jev-style style_out.jsonl --force`. Đọc `rejected.json`: mục phá bất biến đã bị loại.
6. Cổng wpautop trên site (chỉ đọc DB):
   `CHANGES=/tmp/<phiên>/changes.json OUT=/tmp/<phiên>/cmp.json <lệnh wp> --path=<root> eval-file /tmp/<phiên>/compare_autop.php`
   Kết quả phải có `bad = 0`. Còn khác biệt thì sửa luật trong `cruft_clean.py` hoặc bỏ mục đó, rồi chạy lại từ bước 3.
7. Duyệt lô: chụp desktop và mobile 5–6 URL mẫu trên staging hoặc bản xem trước, gồm bài dài và bài Elementor. Gửi người vận hành số mục, byte giảm dự kiến và ảnh. Chỉ ghi production khi người vận hành đồng ý.
8. Chạy thử rồi ghi. `BK` là file backup giá trị gốc. Khi `DRY=0`, script từ chối chạy nếu thiếu `BK` hoặc thiếu `CMP` có `bad = 0`:
   `CHANGES=… CMP=/tmp/<phiên>/cmp.json BK=/tmp/<phiên>/bk.json OUT=/tmp/<phiên>/log-dry.json <lệnh wp> --path=<root> eval-file /tmp/<phiên>/apply_cruft.php`
   Đọc mọi dòng skip. Skip do md5 lệch nghĩa là bài đã đổi sau lúc xuất. Rồi chạy lại với `DRY=0` và `OUT` mới.
9. Purge và làm nóng URL đã ghi theo `ghi-an-toan.md` mục 1, bước 4 và 5.
10. Đo sau và so: `cruft_scan.py urls.txt --out scan_sau.jsonl`, rồi `cruft_scan.py --diff scan_truoc.jsonl scan_sau.jsonl`. Chụp lại 5–6 URL mẫu, so với ảnh bước 7.

Đặt mọi biến môi trường sau `sudo -u www` (`ghi-an-toan.md` mục 2). Chép file tạm vào thư mục riêng của phiên trên server, xoá sau lượt ghi.

## 3. Rollback

`rollback_cruft.php` chỉ trả mục mà giá trị hiện tại còn bằng `md5_after` trong log ghi. Mục đã đổi sau lượt ghi là thay đổi của phiên khác: script in "đã đổi sau khi ghi" và không chép đè.

```bash
BK=/tmp/<phiên>/bk.json LOG=/tmp/<phiên>/log-ghi.json <lệnh wp> --path=<root> eval-file /tmp/<phiên>/rollback_cruft.php          # chạy thử
BK=/tmp/<phiên>/bk.json LOG=/tmp/<phiên>/log-ghi.json DRY=0 <lệnh wp> --path=<root> eval-file /tmp/<phiên>/rollback_cruft.php    # trả thật
```

Mục còn lại sửa tay từ giá trị gốc trong `BK`, theo `ghi-an-toan.md` mục 5. Ghi lệnh rollback vào báo cáo đợt trước khi chạy `DRY=0`.

## 4. Không thuộc phạm vi

- Rác trong file theme hoặc template: sửa theme qua `wp-staging-deploy`, không sửa bằng script này.
- Danh sách rác riêng của từng site (ví dụ ảnh placeholder trong template): ghi ở hồ sơ dự án, không ghi vào skill.

## 5. Test offline

`python3 -B skills/wp-content-review-apply/tests/test_cruft.py` chạy cả 6 script với WordPress giả. Ca hỏng thật trong test: span chỉ chứa xuống dòng (19/10), bài đổi sau lúc xuất, rollback gặp bài phiên khác đã sửa.
