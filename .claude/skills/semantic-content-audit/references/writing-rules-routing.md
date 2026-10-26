# Phân luật viết cho code, Jev và Claude

File này chia 60 Semantic Writing Rules theo người chấm. Dùng ở Phase 3 khi chạy `scripts/rules_jev.py`. Số luật theo file 60 rules của skill.

## 1. Nguyên tắc chia

- Code chấm luật đếm được trên một đoạn hoặc heading.
- Jev chấm luật cần hiểu nghĩa nhưng chỉ cần một đoạn và heading của đoạn đó.
- Claude chấm luật cần cả trang, cả site, dữ liệu query hoặc kiến thức chuyên ngành.
- Jev không đếm và không viết lại câu. Đoạn vi phạm do Claude sửa theo `references/45-semantic-writing-rules.md`.

## 2. Code (`rules_jev.py code`)

| Luật | Cờ | Cách bắt |
|---|---|---|
| 21 Declare before citing | `R21` | Đoạn mở bằng "Theo …," hoặc "Dựa theo …," |
| 24 Don't start paragraphs with quotes | `R24` | Ký tự đầu đoạn là dấu ngoặc kép |
| 26 "and/or" not slashes in headings | `R26` | Heading có "/" (trừ URL và phân số) |
| 32 Paragraphs for readability | `R32` | Đoạn không có danh sách dài hơn 120 chữ |

## 3. Jev (`tasks/writing-rules.json` 2026-10-19.1)

| Câu hỏi | Luật | Trạng thái hiệu chuẩn 19/10 (site mẫu, 15 bài blog) |
|---|---|---|
| `answer_first` | 11, 17, 20 | Lọc: AUC 0,90 trên 70 đoạn đầu sau heading. Mốc đọc p ≥ 0,42: holdout bắt 15/18, đọc 50% |
| `fluff` | 2 | Lọc: AUC 0,90 trên 100 đoạn. Mốc p ≥ 0,25: holdout bắt 15/18, đọc 55% |
| `vague_quantity` | 3, 6, 8 | Lọc: AUC 0,83, chỉ 10 ca dương. Mốc p ≥ 0,29: holdout bắt 4/5, đọc 45% |
| `plural_no_example` | 9, 25 | Lọc: AUC 0,88. Mốc p ≥ 0,31: holdout bắt 8/8, đọc 68% |
| `hedging` | 1 | Chưa hiệu chuẩn: 1 ca dương trên 60 đoạn. Không đọc cột này |

Không câu hỏi nào đạt cổng tự chốt (precision 0,95). Mọi nhãn Jev chỉ dùng để xếp đoạn cho Claude đọc trước.

## 4. Claude

| Nhóm | Luật | Lý do không giao Jev hay code |
|---|---|---|
| Cần cả trang | 15, 35, 42, 43, 52, 53, 54, 56 | Dòng chảy, mâu thuẫn, phân bố thuật ngữ, thứ tự heading cần đọc cả bài |
| Cần cả site hoặc query | 13, 55, 57, 58, 59, 60 | Cần title trang đích, bài khác của site hoặc cụm query |
| Cần kiến thức chuyên ngành | 4, 5, 6 (số YMYL đúng sai), 28, 30, 36, 39, 41, 46–51 | Đúng sai của fact, E-A-V và entity cần đối chiếu nguồn |
| Đoạn, chưa có rubric | 7, 10, 12, 14, 16, 18, 19, 22, 23, 27, 33, 34, 37, 38, 40, 44, 45 | Chưa hiệu chuẩn; Claude đọc khi audit đầy đủ |
| Không áp tiếng Việt | 31 (viết hoa mỗi từ trong heading) | Quy ước tiếng Anh; chỉ chấm trang tiếng Anh |
| Cần HTML ảnh | 29 (alt text) | Chấm ở `seo-onpage` hoặc `image-seo-optimize` |

## 5. Information gain

Không đo information gain bằng độ khác embedding. Pilot 10/2026 của lớp model: độ mới passage so với pool có AUC 0,52–0,55 với trích dẫn AI, CI chứa 0,5. Dùng dấu hiệu effort của skill `content-quality-lab` (`original_data`, `first_hand`, AUC 0,73 và 0,71) cho mục "Original value added" và "First-hand usage evidence".
