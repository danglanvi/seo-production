# Danh sách thuộc tính cho ma trận đồng thuận

Mục đích: viết `attrs.tsv` cho lệnh `ngram.py page --attrs`. Đọc file này ở bước 4 của quy trình.

## 1. Định dạng

- Một dòng một thuộc tính: `tên thuộc tính<TAB>regex`. Dòng đầu `thuoc_tinh<TAB>regex` là tuỳ chọn. Dòng bắt đầu bằng `#` bị bỏ qua.
- Script so regex với chữ thường, dạng NFC, của title + meta + heading + thân trang.
- Viết regex bằng chữ thường có dấu. Thêm biến thể không dấu khi đối thủ hay viết không dấu.
- Một thuộc tính là một thông tin người đọc cần, không phải một từ khoá. Viết "bảng giá có số tiền", không viết "giá".

## 2. Cách chấm

- Trang ở vị trí 1–3 (`--tier1`) tính trọng số 2. Trang khác tính 1.
- Mức theo phần trăm trọng số: MANDATORY từ 80%, RECOMMENDED 50–79%, OPTIONAL 20–49%, DIFFERENTIATOR dưới 20%.
- Thuộc tính MANDATORY hoặc RECOMMENDED mà trang mình ghi "KHÔNG" vào đề xuất, kèm section đích.
- Thuộc tính DIFFERENTIATOR mà trang mình có là điểm khác biệt. Giữ lại khi viết lại.

## 3. Mẫu cho trang dịch vụ

Thay `<dịch vụ>` bằng tên dịch vụ của khách, ví dụ `seo|geo` hoặc `thiết kế website`.

```tsv
thuoc_tinh	regex
định nghĩa dịch vụ	(<dịch vụ>)[^.\n]{0,40} là (gì|quá trình|phương pháp|dịch vụ)
vấn đề của khách hàng	(vấn đề|khó khăn|nỗi đau|đang gặp|dấu hiệu)
lợi ích	lợi ích|giá trị (gì|mang lại)|mang lại gì
quy trình triển khai	quy trình
lộ trình theo tháng	(tháng (thứ )?\d|\d+\s*[-–]\s*\d+\s*tháng|lộ trình)
bảng giá có số tiền	\d[\d.,]*\s*(triệu|tr|vnđ|đ)\b
yếu tố ảnh hưởng giá	(yếu tố|phụ thuộc)[^\n]{0,40}(giá|chi phí)
hợp đồng	hợp đồng
báo cáo định kỳ	báo cáo
case study có số liệu	(case stud|dự án)[^\n]{0,120}\d
đánh giá của khách hàng	(khách hàng nói|đánh giá|feedback|nhận xét)
đội ngũ chuyên gia	đội ngũ|chuyên gia
FAQ	câu hỏi (thường gặp|hay gặp)|faq
năm kinh nghiệm	\d+\+?\s*năm (kinh nghiệm|hoạt động)|từ (năm )?20\d\d
```

## 4. Thêm cho trang địa phương

```tsv
địa chỉ văn phòng tại thành phố	(địa chỉ|văn phòng|trụ sở)
quận hoặc khu vực	(quận|phường|huyện|khu vực)
hotline	hotline|\b0\d{2,3}[ .]?\d{3}[ .]?\d{3,4}\b
Google Business Profile hoặc Maps	google (business|maps?|my business)|gbp
gặp trực tiếp	(gặp trực tiếp|tận nơi|tại văn phòng)
```

## 5. Bài tiền dạng danh sách (top công ty, so sánh)

```tsv
tiêu chí chọn	tiêu chí
cách xếp hạng hoặc nguồn đánh giá	(tiêu chí xếp hạng|cách (chúng tôi )?(xếp hạng|đánh giá|chọn)|phương pháp (đánh giá|xếp hạng))
năm thành lập từng đơn vị	thành lập|(từ|năm) (năm )?20[01]\d
ưu điểm và nhược điểm	(ưu điểm|nhược điểm|điểm mạnh|hạn chế)
ngày cập nhật	cập nhật
bảng so sánh	bảng so sánh|so sánh
```

## 6. Thuộc tính cấm đề xuất

Ma trận có thể cho thấy đối thủ ghi "cam kết top", "hoàn tiền", "bảo hành thứ hạng". Ghi các dòng này vào báo cáo để biết thị trường. Không đề xuất trang mình thêm các thuộc tính này. Chỉ người quyết định của khách được quyết cam kết.
