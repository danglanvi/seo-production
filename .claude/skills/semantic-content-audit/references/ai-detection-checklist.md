# AI-Pattern Detection Checklist — Phase 5 (Humanness)

> Reference cho `semantic-content-audit` **Phase 5**. Vai trò: **DETECT-only** — quét, chấm, chỉ điểm bằng evidence. KHÔNG sửa bài (việc của skill `humanizer` — FIX layer; taxonomy dưới đây distill từ humanizer v3.1 để audit standalone được; humanizer đổi pattern → cập nhật file này).
>
> **Nguyên tắc verdict:** output là **AI-likelihood: LOW / MEDIUM / HIGH** dựa trên evidence đếm được (pattern nào, bao nhiêu lần, quote dòng nào). **KHÔNG output "% AI probability"** — mọi con số % kiểu detector là giả định không kiểm chứng được; verdict theo evidence trung thực và actionable hơn.

## Cách chấm

1. Quét bài theo 4 nhóm dưới (mỗi nhóm có ngưỡng đếm cụ thể).
2. Mỗi hit ghi: `mã pattern · số lần · quote ngắn (≤15 từ) + vị trí`.
3. Tính điểm nhóm → verdict tổng (bảng cuối). Bài song ngữ: chỉ áp pattern đúng ngôn ngữ (vd A14 hyphen chỉ EN).
4. **Meta-rule (Wikipedia 2026):** pattern đơn lẻ KHÔNG kết luận — con người cũng viết được như vậy; kết luận đến từ **mật độ + đồng xuất hiện nhiều pattern**. Khi bài vốn formal (legal, academic) → nâng ngưỡng trước khi flag.

## Nhóm 1 — Vocabulary & cliché (weight ×1 mỗi hit, max 10)

| Mã | Pattern | Ngưỡng flag |
|---|---|---|
| V1 | Nuke words tier 1 (EN: delve, tapestry, landscape, realm, pivotal, crucial, foster, leverage, seamless, robust, comprehensive, holistic… VN: "tối ưu hóa toàn diện", "giải pháp toàn diện", "nâng tầm", "bứt phá"…) | ≥3 từ khác nhau HOẶC 1 từ ≥3 lần |
| V2 | Predictable opener/closer ("Trong thời đại số…", "In today's fast-paced world…", "Tóm lại…", "Hy vọng bài viết…") | ≥1 ở mở/kết bài hoặc mở/kết section |
| V3 | Signposting ("Let's dive in", "Hãy cùng tìm hiểu", "here's what you need to know") | ≥1 |
| V4 | Persuasive authority tropes ("The real question is", "At its core", "Về bản chất", "Cốt lõi vấn đề là") | ≥2 |
| V5 | Intensifier rỗng ("vô cùng quan trọng", "extremely important", "tuyệt đối an toàn") không kèm số liệu | ≥3 |

## Nhóm 2 — Grammar & structure (weight ×2 mỗi hit, max 12)

| Mã | Pattern | Ngưỡng flag |
|---|---|---|
| G1 | Transition repetition: cùng token đầu câu ("Với", "Ngoài ra", "Tuy nhiên", "Furthermore", "Moreover") | 1 token ≥4 lần/bài |
| G2 | Copula avoidance: "serves as / stands as / boasts / features / đóng vai trò là / được xem là" thay "is/has/là/có" | ≥3 |
| G3 | Negative parallelism ("It's not just X, it's Y", "Không chỉ… mà còn…") | ≥2 |
| G4 | Rule of Three lặp (3 item liệt kê kiểu "adjective, adjective, adjective") | ≥3 cụm |
| G5 | False ranges ("from X to Y" không cùng scale thật) | ≥2 |
| G6 | Em dash overuse | ≥3 em dash/paragraph bất kỳ |
| G7 | Cụm 3 câu liên tiếp cùng cấu trúc S-V-O cùng chủ ngữ | ≥2 cụm |
| G8 | Hedge chồng chất (≥2 hedge/câu: "một số nghiên cứu cho thấy có thể có khả năng…") | ≥2 câu |

## Nhóm 3 — Statistical / rhythm (weight ×2 mỗi hit, max 8)

| Mã | Pattern | Ngưỡng flag |
|---|---|---|
| S1 | Low burstiness: paragraph có ≥80% câu dài 10-15 từ, không câu <8 và không câu >20 | ≥2 paragraph |
| S2 | Uniform paragraph length: ≥5 paragraph liên tiếp lệch nhau <20% độ dài | có |
| S3 | Fragmented headers: heading + 1 câu restate rỗng rồi mới vào content | ≥2 |
| S4 | Elegant variation: xoay vòng synonym máy móc cho cùng entity (mỗi lần nhắc là 1 tên khác) | ≥1 entity |

## Nhóm 4 — Content & experience (weight ×3 mỗi hit, max 12) — nặng nhất vì khó fake

| Mã | Pattern | Ngưỡng flag |
|---|---|---|
| C1 | Dilute paragraph: đoạn 0 E-A-V, 0 fact, 0 value cho heading | ≥2 đoạn |
| C2 | Vague attribution / weasel ("nhiều chuyên gia cho rằng", "industry observers note") không nguồn cụ thể | ≥2 |
| C3 | Undue emphasis on significance/legacy ("đánh dấu bước ngoặt", "stands as a testament") | ≥2 |
| C4 | Zero first-hand experience: bài review/YMYL/service 2000+ từ có <3 instance trải nghiệm thật (temporal marker, số đo tự test, so sánh đã dùng, client voice) | có (chỉ áp bài cần E-E-A-T) |
| C5 | Generic "Challenges and Future Prospects" section outline-style | ≥1 |
| C6 | Repeat definition / số liệu mâu thuẫn giữa các section (10% ở đầu, 15% ở cuối cùng metric) | ≥1 |

## Verdict tổng

Tổng điểm = Σ(hit × weight từng nhóm, cap theo max nhóm). Max lý thuyết = 42.

| Verdict | Điểm | Đọc là |
|---|---|---|
| **LOW** | 0-9 | Không có cluster AI đáng kể — pass Humanness |
| **MEDIUM** | 10-19 | Có cluster pattern — cần humanize CÓ CHỌN LỌC (list top offenders) |
| **HIGH** | ≥20 hoặc ≥2 nhóm chạm max | Fingerprint AI dày đặc — route toàn bài qua skill `humanizer` |

**Report block chuẩn (chèn vào report audit):**

```markdown
## Phase 5 — Humanness (chấm riêng, không tính vào 66đ)
**Verdict: LOW / MEDIUM / HIGH** · điểm N/42 (V:x G:x S:x C:x)
Top offenders:
1. [mã] × [số lần] — "[quote]" (vị trí)
2. …
→ Route: MEDIUM/HIGH → chạy skill `humanizer` (mode phù hợp); LOW → không cần.
Lưu ý: verdict theo evidence pattern — KHÔNG phải "% AI"; bài formal tự nhiên có thể MEDIUM, đọc kèm context.
```

## Ranh giới với humanizer (phân vai cứng)

| Việc | Ở đâu |
|---|---|
| Phát hiện + chấm + chỉ điểm evidence | ✅ Phase 5 này (DETECT) |
| Sửa/rewrite từng pattern, giữ voice, Voice Fingerprint, nuke words tier 2, experience injection | `humanizer` (FIX) |
| Preserve personality markers (rhetorical question, direct address) khi sửa | `humanizer` — Phase 5 KHÔNG flag các marker này là lỗi (chúng là dấu hiệu NGƯỜI) |
