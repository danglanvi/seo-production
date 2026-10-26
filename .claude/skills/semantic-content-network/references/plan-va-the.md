# Plan SCN, thẻ duyệt và lô

Mục đích: cấu trúc file plan, luật viết thẻ, luật gom lô và lịch đo của skill `semantic-content-network`. Đọc mục 1 ở bước 12, mục 2 ở bước 10, mục 3 ở bước 11.

## 1. Cấu trúc file plan

Viết file `04-structure-ux-cro/<CLIENT>_scn-plan_v<N>.md` theo thứ tự sau. Bản sau chỉ ghi phần đổi và trỏ về bản trước.

1. Đầu file: entity, trạng thái ("đề xuất, chưa ghi lên site"), dữ liệu dùng (nguồn, ngày kéo, số dòng), skill đã dùng.
2. Kết luận: tối đa 10 ý, mỗi ý có số.
3. Foundation và SCN map: Source Context, Central Entity, Central Search Intent, Root, Core, Outer. Bảng theo cụm: seed, số node, depth ngữ cảnh.
4. Click depth và PageRank: bảng trang tiền (depth mọi link, depth ngữ cảnh, số trang link ngữ cảnh vào, hạng PR), mục tiêu depth, kết quả mô phỏng `--add`.
5. Trang còn thiếu: bảng ứng viên, nhu cầu, SERP, QDP, kết luận, thẻ.
6. Bằng chứng riêng: số case, năm số liệu, trang tiền đang link tới case, việc nối.
7. Gộp trang: bảng cặp, bằng chứng đề cử, số URL chung, đề xuất, thẻ.
8. Mốc GEO: cách đo, bảng theo engine, prompt GTV vắng mặt, câu AI mô tả sai, lịch đo lại.
9. Query Processing: bảng template (lượt hiển thị, URL Google chọn, cờ), quyết định URL, luật anchor, lịch đo ngày 14, 30, 60.
10. Duyệt theo lô: bảng lô (nội dung, số thẻ, ghi chú) và danh sách thẻ duyệt riêng.
11. Lộ trình theo đợt, việc cần người duyệt quyết (xếp theo mức ảnh hưởng), chỗ chưa làm được kèm lý do.
12. File và chi phí (API, credit).
13. Bảng tự phản biện 6 mục: mục, bản nháp đạt chưa, bằng chứng, việc sửa.

## 2. Luật viết thẻ

- Thẻ theo hợp đồng dữ liệu của `wp-content-review-apply` (`references/hop-dong-du-lieu.md` của skill đó).
- Mỗi thẻ có `before` lấy từ DB hoặc trang live. Chuẩn hoá NFC trước khi so, vì có bài lưu chữ dạng NFD.
- Mỗi trường trong một thẻ có key riêng. Nếu một thẻ cần 2 trường cùng key, đặt `key#2`, `key#3`. Key trùng làm trang duyệt lưu đè values.
- Thẻ đã duyệt không sửa tại chỗ. Tạo id mới, ghi id cũ trong `note`, rồi báo người duyệt.
- Thẻ phụ thuộc thẻ khác: ghi điều kiện trong `note`, ví dụ "chỉ ghi khi chọn B ở thẻ X".
- Chữ mới qua `humanizer` và luật claim của `content-quality-lab` trước khi nạp.
- Chạy `scn.py guard` trước mỗi lần nạp. Đọc lại doc trang duyệt ngay trước khi ghi, vì phiên khác có thể ghi cùng trang.

## 3. Luật gom lô

- Một lô gồm các thẻ cùng một luật, ví dụ "gỡ link quảng cáo đặt sai chỗ trong bài thông tin".
- Lô chỉ nhận thẻ rủi ro thấp: link, anchor, kết bài, lỗi gõ, nhãn, alt, cấp heading, schema, số thiếu nguồn.
- Thẻ title, H1, meta, đoạn mở, FAQ, giá, mục địa phương của trang tiền duyệt riêng. Quyết định lớn (mở trang, gộp, đổi vai) duyệt riêng.
- Lô cần ít nhất 2 thẻ. Thẻ đã duyệt hoặc đã ghi bị loại khỏi lô.
- Duyệt lô bằng duyệt mọi thẻ còn trong danh sách, theo phương án chọn sẵn. Thẻ đã bấm riêng giữ quyết định riêng. Người duyệt loại thẻ khỏi lô bằng cách xoá dòng ở ô E.
- Bước ghi đọc danh sách thành viên từ `values.members` nếu người duyệt đã sửa.

File `lots.json`:

```json
[{"id": "l1", "title": "Gỡ link quảng cáo trong bài thông tin", "rule": "Luật chung: ...", "members": ["id-the-1", "id-the-2"], "note": "điều kiện phụ thuộc, nếu có"}]
```

## 4. Lịch đo sau khi ghi

| Mốc | Đo gì | Công cụ |
|---|---|---|
| Ngay sau đợt 1 | Request indexing trang tiền, crawl lại, chạy lại `scn.py graph` | Search Console, Screaming Frog |
| Ngày 14, 30, 60 | Lượt hiển thị, click, URL Google chọn, vị trí theo template | `baseline.tsv` (regex dán vào GSC) |
| Hằng tháng | Mốc GEO cùng bộ prompt | `geo-answer-lab` |
| Ngày 30 | Điều kiện bác bỏ của từng quyết định URL | bảng QP của plan |
| Ngày 60 | Cặp vùng xám 4–5/10, mở đợt 2 | `scn.py serp-overlap` |

Trước ngày 30 sau đợt 1, không ghi thẻ xoá khối trên trang tiền, trừ sửa số sai, lỗi gõ, link chết.
