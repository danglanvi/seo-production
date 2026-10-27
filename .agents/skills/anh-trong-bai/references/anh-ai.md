# Ảnh AI trong thân bài

Ảnh AI là phương án cuối. Dùng khi khung cần một hình minh hoạ khái niệm, không có ảnh thật, ảnh chụp nguồn hay sơ đồ phù hợp.

## Không dùng ảnh AI khi

- Ảnh có người, đội ngũ, văn phòng, khách hàng, học viên. Dùng ảnh thật.
- Ảnh cần chữ. Chữ dựng bằng SVG hoặc code, đặt lên ảnh sau.
- Ảnh thay cho bằng chứng: kết quả công cụ, số liệu, giao diện thật. Dùng ảnh chụp.

## Công cụ

Chỉ dùng công cụ tạo ảnh mà dự án cho phép, qua runner có sổ credit và trần lượt gọi. Không tự đổi sang nhà cung cấp khác khi công cụ hết credit hoặc lỗi.

- Workspace có runner canonical (ví dụ workspace GTV và TAG: `skills/brand-image-gen-gtv-tag/scripts/kie_image.py`, model theo thứ tự trong runner): chạy dry-run trước, rồi thêm `--run`.

  ```bash
  python3 skills/brand-image-gen-gtv-tag/scripts/kie_image.py gen --prompts-dir <thư mục bài>/media/prompt --out <thư mục bài>/media/ai
  python3 skills/brand-image-gen-gtv-tag/scripts/kie_image.py gen --prompts-dir <thư mục bài>/media/prompt --out <thư mục bài>/media/ai --run
  ```

- Repo không có runner hoặc máy không có key: ghi prompt vào `media/prompt/<ten_file>.json`, đặt `trang_thai` là `ready_to_generate`, báo người có quyền tạo ảnh. Không chặn các khung khác.

## Prompt JSON

Viết prompt dạng JSON, càng chi tiết càng tốt. Text-to-image là chính. Chỉ dùng image-to-image khi cần giữ bố cục của ảnh gốc.

```json
{
 "subject": "<vật thể chính, gắn với ý của H2>",
 "scene": "<bối cảnh, không có người>",
 "camera": {"angle": "<góc máy>", "lens": "<ống kính>", "framing": "<khung hình>"},
 "props": ["<đạo cụ>"],
 "screen_orientation": "<màn hình quay về phía người xem, nếu có màn hình>",
 "palette": ["<màu chính của site>", "<màu phụ>", "<nền>"],
 "style": "<phong cách>",
 "negative": ["text", "letters", "logo", "watermark", "people", "hands"],
 "aspect_ratio": "16:9"
}
```

## Xem trước khi dùng

- Vật lý đúng: bóng, phản chiếu, phối cảnh.
- Màn hình quay về phía người xem. Không có chữ giả trên màn hình.
- Không có người, tay hay mặt lọt vào ảnh.
- Hình gắn với ý của H2, không chỉ là ảnh trang trí.

## Xử lý sau khi tạo

```bash
python3 skills/anh-trong-bai/scripts/anh_chu_thich.py <ảnh AI.png> --profile <profile> --nguon ai --alt "<alt>" --out <thư mục bài>/media/<ten_file>.webp
```

- Script ghép logo `media.logo` góc dưới phải (rộng 9%, mờ 0,55), thu về `media.rong_anh`, nén dưới `media.kb_anh_chup` KB.
- Metadata XMP ghi `DigitalSourceType` là ảnh tổng hợp bằng thuật toán.
- Ghi `src` vào plan, đặt `trang_thai` là `xong` sau khi xem ảnh cuối.
