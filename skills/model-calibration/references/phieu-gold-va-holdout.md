# Phiếu gold và holdout

Mục đích: dựng phiếu gán gold mù, ghép nhãn vào gold, tách holdout và đọc entry draft trong registry. Nạp ở bước 1, 2 và 5 của `model-calibration`. Gốc đường dẫn là root repo SEO Production. Đặt đường dẫn trong nháy kép khi đường dẫn có dấu cách.

## 1. Dựng phiếu bằng `gold-sheet`

Chọn một nguồn mẫu:

| Nguồn | Khi nào | Tầng lấy mẫu |
|---|---|---|
| `--pred jev_out.jsonl --question <câu hỏi>` | Đã chạy Jev | 6 dải confidence: 0,9–1,0 · 0,8–0,9 · 0,7–0,8 · 0,6–0,7 · 0,5–0,6 · dưới 0,5 |
| `--items items.jsonl` | Chưa có nhãn model: cặp cosine, mục của chuỗi, ảnh | Một tầng `all` |

- Đầu ra `jev.py` không mang nội dung. Thêm `--content jev_in.jsonl` để phiếu hiện `state` theo id. Thiếu cờ này thì phiếu chỉ có id.
- Câu yes/no tính confidence là max(p, 1 − p). Script bỏ dòng không có câu trả lời cho câu hỏi và đếm ở `skipped_no_answer`.
- Ghi id ca khó vào file `--hard`, mỗi dòng một id. Dòng nguồn có `"hard": true` cũng là ca khó.
- Script lấy ca khó trước, tối đa `--hard-share` của `--n`. Mặc định là 0,25.
- Script chia phần còn lại đều các dải. Script trộn thứ tự phiếu, nên vị trí không lộ dải.
- Cùng nguồn và cùng `--seed` thì script ra cùng phiếu.
- Phiếu không chứa nhãn hay confidence của model. Stdout chỉ in số mẫu theo tầng.
- `--labels a,b` ghi danh sách nhãn vào đầu phiếu. Nếu thiếu `--labels` mà có `--content`, script lấy nhãn từ `criteria` của câu hỏi.
- Script chọn nội dung phiếu theo thứ tự: `--field`, rồi trường đầu tiên có giá trị trong text, url, title, path, image, rồi `state`.
- `--format html` ghi contact sheet ảnh ở `--out` và phiếu todo cạnh nó (`<tên>.todo.txt`). Mỗi mục cần trường ảnh, mặc định `image` (đổi bằng `--image-field`).
- Mở contact sheet trong Chrome để xem ảnh. Điền nhãn vào phiếu todo.
- Script mặc định chạy thử. Thêm `--out <file> --write` để ghi.

```bash
S=skills/model-calibration/scripts/calibrate.py
python3 -E $S gold-sheet --pred <W>/jev_out.jsonl --question <câu hỏi> --content <W>/jev_in.jsonl \
  --n 60 --hard <W>/calibration/hard_ids.txt --out <W>/calibration/<rubric>_phieu-gold.txt --write
python3 -E $S gold-sheet --items <W>/images.jsonl --n 60 --labels pass,fail --format html \
  --out <W>/calibration/<rubric>_phieu-anh.html --write
```

## 2. Định dạng phiếu

```text
# Phiếu gán gold. Điền nhãn sau "LABEL:". Để trống nếu ca mơ hồ.
# Gán xong trước khi xem nhãn model.
# LABELS: yes|no

### id: 108975
  title: <nội dung mục>
LABEL: yes
```

- Điền nhãn sau `LABEL:`. Để trống hoặc ghi `?` khi ca mơ hồ.
- Không sửa dòng `### id:`. Không thêm khối.
- Gán xong cả phiếu rồi mới mở file đầu ra model.
- Câu yes/no của Jev dùng nhãn `yes`, `no`. Câu `choice` dùng tên lựa chọn trong `criteria`. Chế độ cosine dùng nhãn `1`, `0`.

## 3. Ghép gold bằng `gold-merge`

- Script ghép nhãn vào `gold.jsonl` dạng `{"id", "label"}`. Nếu file chưa có, script tạo file.
- Ca mơ hồ không vào gold. Script liệt kê các ca này ở `ambiguous_ids`. Đọc lại các ca này hoặc bỏ.
- Nhãn ngoài danh sách `# LABELS:` hoặc `--labels` làm lệnh dừng.
- id đã có gold với nhãn khác làm lệnh dừng.
- Chỉ sửa gold sau khi đọc ca lệch. Thêm `--overwrite --reason "<lý do>"`. Dòng gold nhận thêm trường `note`.
- Không sửa gold cho khớp model.
- Script cảnh báo khi gold dưới 40 mẫu hoặc có lớp dưới 5 mẫu. Cảnh báo không chặn lệnh.
- Script mặc định chạy thử. Thêm `--write` để ghi. Script ghi file tạm rồi đổi tên.

```bash
python3 -E $S gold-merge --todo <W>/calibration/<rubric>_phieu-gold.txt --gold <W>/calibration/gold.jsonl --write
```

## 4. Tách holdout

Holdout là gold thứ hai. Gán holdout mù như gold hiệu chuẩn. Không dùng holdout để chọn ngưỡng.

1. Chạy `gold-sheet` lần hai với `--exclude-gold <W>/calibration/gold.jsonl`. Script bỏ các id đã gán.
2. Gán phiếu, rồi chạy `gold-merge --gold <W>/calibration/holdout.jsonl --write`.
3. Thêm `--holdout <W>/calibration/holdout.jsonl` vào lệnh `jev`, `cosine` hoặc `pipeline`.

Holdout đạt khi đủ 4 điều kiện:

- Holdout có ≥ 40 mẫu.
- Mỗi lớp có ≥ 5 mẫu.
- Holdout không trùng id với gold hiệu chuẩn. Trùng id làm lệnh dừng, script không ghi registry.
- Ngưỡng hoặc `conf_gate` giữ tiêu chí lúc chọn: ≥ `--min-n` mục qua cổng, precision ≥ `--target`, cận dưới Wilson ≥ target − 0,1. Với `pipeline`, verdict trên holdout phải là "đạt".

| Chế độ | Holdout nằm ở đâu |
|---|---|
| `jev` | id nằm trong cùng file `--pred` |
| `cosine` có `--gold` | gold `{id, label}`; script lấy cos từ `--pairs` |
| `cosine` không có `--gold` | file cặp mới `{id, cos, label}` |
| `pipeline` | id nằm trong cùng file `--pred` của chuỗi |

## 5. Entry trong registry

Lệnh `jev`, `cosine`, `pipeline` có `--write` ghi entry theo trạng thái:

| Trạng thái | Khi nào | `threshold`, `conf_gate`, `reject_below` | Trường thêm |
|---|---|---|---|
| `ready` | Holdout đạt | Giá trị đã chọn | `holdout`: n, precision, Wilson |
| `draft` | Thiếu holdout hoặc holdout không đạt | null | `draft_values` (giá trị đề xuất), `draft_reason` |

- `proxy` và `auc` luôn ghi `ready`. Hai chế độ này có CI bootstrap theo nhóm và không có ngưỡng.
- Entry `pipeline` ghi thêm `recall` và `unit` (tên chuỗi, ví dụ `chuỗi jev>glm`).
- `show --registry <file>` in cột trạng thái và recall. Entry cũ không có trường `status` hiện là `ready`.
- Skill đọc registry phải bỏ qua entry `draft` và đọc tiếp defaults. Báo cáo dùng defaults ghi "bản nháp".
- `draft_values` chỉ dùng khi hiệu chuẩn tiếp. Không dùng `draft_values` làm cổng.
