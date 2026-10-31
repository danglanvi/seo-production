# Brief video giao repo video

Dùng khi một mục của trang cần video giải thích mà site chưa có video sở hữu phù hợp. Brief này là input cho skill `video-explainer` của repo Video Production. Repo đó dựng video có giọng đọc tiếng Việt và phụ đề, rồi trả MP4 bản web, ảnh poster và transcript.

## Khi nào lập brief

- Mục có quy trình nhiều bước, nhiều vai (người, AI, công cụ), hoặc cơ chế khó hình dung bằng chữ và sơ đồ tĩnh.
- Không có video sở hữu nào khớp heading của mục (Bước 2 của `semantic-media`).
- Tối đa 2 video cho một trang. Mục còn lại dùng sơ đồ.

## Mẫu

Ghi file `brief-video-<slug>.md` cạnh media plan:

```markdown
# Brief video: <slug>

| Trường | Giá trị |
|---|---|
| Brand | GTV · TAG · khách: <tên>, profile `<đường dẫn web-profile.json>` |
| Ý chính (1 câu) | <điều người xem hiểu sau một lần xem> |
| Người xem | <ai, đang làm gì> |
| Đặt ở | <URL hoặc file bài> · mục "<heading>" · đầu mục, trước sơ đồ |
| Tỷ lệ | 16:9 nhúng bài · 9:16 Reels · 1:1 feed |
| Độ dài ước lượng | 40–60 giây |
| Giọng | Alice (ElevenLabs) · giọng máy cho bản nháp |
| Phụ đề | bật |

## Khung

| # | Read (điều người xem phải hiểu) | Chữ trên hình | Lời đọc nháp |
|---|---|---|---|
| 1 | | | |

## Số liệu và nguồn

- <số> — <file:dòng hoặc mã fact KB>

## Bàn giao

Repo Video Production: `bash tools/new_video.sh <slug> --brand <gtv|tag|client> [--profile <file>] --source brief-video-<slug>.md`.
Video xong trả: MP4 bản web (H.264, `+faststart`), poster JPG, transcript, VideoObject (tên, mô tả, thời lượng, poster).
```

## Luật

1. Lời đọc nháp lấy từ chữ của mục. Câu đủ chủ ngữ và vị ngữ, đọc thành tiếng được. Mỗi khung một read.
2. Mỗi số trong lời đọc hoặc chữ trên hình có dòng nguồn. Không có nguồn thì ghi `[cần nguồn]`.
3. Không đưa cam kết hoàn tiền hay bảo đảm kết quả vào lời đọc.
4. Brand theo entity của trang. Video cho khách dùng màu, logo, chữ ký của khách (`--brand client`). Logo khách chỉ dùng khi khách cho phép.
5. Chữ trên hình không lặp lời đọc: chỉ số, thuật ngữ, nhãn sơ đồ.
6. Dữ liệu chưa công khai của khách không gửi model ngoài (Jev, GLM).

Ca gốc: ngày 31/10/2026, bài tài liệu nội bộ về chuẩn outline cần 2 video có lời ở đầu 2 mục (chấm chất lượng 3 lớp 56 giây, làm outline cùng AI 46 giây). Brief, lời đọc và khung phải viết tay từ thân bài trước khi repo video dựng được. Mẫu trên gom các trường của lần đó.
