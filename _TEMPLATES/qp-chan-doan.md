---
type: qp-chan-doan
client: {{CLIENT}}
version: v{{N}}
date: {{YYYY-MM-DD}}
cong_doan: {{22 | 24 | 29 | lẻ}}
pic: {{Lead}}
status: draft
---

# {{CLIENT}} — Chẩn đoán Query Processing bộ keyword cam kết v{{N}}

> Hồ sơ đi kèm deck `{{CLIENT}}_qp-chan-doan_v{{N}}.html` (dựng từ `{{CLIENT}}_qp-chan-doan_v{{N}}.json`). Skill: `query-processing-diagnosis`. Naming: `{{CLIENT}}_qp-chan-doan_v{{N}}.md` → `03-audits/ranking/`. Thư mục làm việc: `03-audits/ranking/_work/{{CLIENT}}_qp-chan-doan_v{{N}}/`.

## 1. Tóm tắt (5–7 câu)

- Bộ cam kết: {{số keyword}} keyword · engine hợp đồng {{engine}} · engine đang đo {{engine}} {{khớp | lệch: ...}}.
- Hạng hiện tại (median {{k}} lần hợp lệ {{ngày}}): Top 3/5/10 = {{…}}. 4 tuần trước ({{ngày}}): {{…}}.
- Kỳ đo nghiệm thu tới: {{ngày}}. Chỉ tiêu gần nhất: {{…}} (nội bộ).
- Template đáng đẩy nhất: {{template}}, vì {{bằng chứng}}.
- Trạm hỏng chính: {{B7 Retrieve ở …, B4 Canonical ở …}}.
- Việc P0: {{…}}.
- Đề xuất cho gate #22 (Lead chốt): {{như kỳ vọng | dưới kỳ vọng — lý do}}.

## 2. Con số → nguồn → cách tính

> Dán bảng từ `$W/con-so-nguon.md` (sinh bằng `qp_build.py --numbers`), rồi thêm dòng cho số tự viết trong chữ.

| Con số trên deck | Slide | Nguồn (file, project, engine, ngày) | Cách tính (lệnh, script) |
|---|---|---|---|
| {{12/30/75}} | {{Template, mở dự án}} | {{02-raw/seo-data/keywords/…csv · GM1 · 06–09/10}} | {{qp_ranks.py table … --k 3}} |
| | | | |

## 2b. Chẩn đoán chính (mỗi dòng là một finding)

| # | Cụm / template | Trạm | Bằng chứng | Điều gì xảy ra thì chẩn đoán này sai | Việc + URL đầy đủ (liệt kê đủ, không ghi "và các trang tương tự") | Ai làm · hạn |
|---|---|---|---|---|---|---|
| 1 | {{giá [sản phẩm]}} | {{B4}} | {{2 URL cùng đứng 11–30 cho 9 keyword}} | {{sau 14 ngày dồn anchor, median Top 10 của họ không tăng}} | {{https://… → https://…}} | {{Lead · 25/10}} |

## 3. Lần chạy và độ sâu

- Lần chạy bị loại: {{ngày — lý do}}.
- Độ sâu quét: {{50 | 100}} từ {{ngày}}.
- Lần chạy dùng cho "hiện tại": {{…}}; cho mốc so sánh: {{… | không có, chạy --no-compare vì …}}.

## 4. Lệnh đã chạy

```
S=skills/query-processing-diagnosis/scripts; W=03-audits/ranking/_work/{{CLIENT}}_qp-chan-doan_v{{N}}
python3 $S/qp_ranks.py bo    {{file bộ cam kết}} --col … [--where …] -o $W/bo-cam-ket.txt
python3 $S/qp_ranks.py runs  {{các file csv}} --domain {{domain}} --engine {{engine}}
python3 $S/qp_ranks.py table {{các file csv}} --domain … --engine … --keywords $W/bo-cam-ket.txt --rules $W/rules.json [--targets …] -o $W/hang.json --tsv $W/hang.tsv
python3 $S/site_check.py $W/pages home=… cate=…
python3 $S/qp_scaffold.py $W/hang.json --slug … --name … --domain … --lead … -o {{file.json}}
python3 $S/qp_build.py {{file.json}} --ranks $W/hang.json --topics $W/topics.json --web-out {{file_web.html}} \
        --handoff 03-audits/ranking/{{CLIENT}}_qp-handoff-content_v{{N}}.md --numbers $W/con-so-nguon.md --shots $W/shots
   → check OK · verify 0 lỗi, {{n}} cảnh báo (đã đọc) · {{n}} slide · bản web {{n}} chỗ đã đọc lại · audit 0 slide tràn
```

## 5. Flags: điểm chưa chắc, cần kiểm tay

| # | Slide | Nội dung | Cần gì để chốt | Ai kiểm |
|---|---|---|---|---|
| 1 | | | {{GSC page × query · URL Inspection · SERP tay}} | |

## 6. Khác biệt với lần chẩn đoán trước (nếu có)

- {{v{{N-1}} → v{{N}}: …}}

## 7. Tự chấm checklist (`references/checklist-qc.md`)

| ID | Kết quả | Bằng chứng |
|---|---|---|
| QP-01 … QP-08 (P0) | {{PASS / FAIL / CANNOT-VERIFY}} | |
| QP-09 … QP-18 | | |
| **Tổng** | P0 {{x}}/8 · thường {{y}}/10 → {{PASS | FAIL}} | |

## DoD

- [ ] JSON qua `check`; deck dựng xong; audit 0 slide tràn hoặc ghi lý do.
- [ ] Mục 2 có dòng cho mọi con số trên deck. Mục 2b: mỗi finding có điều kiện bác bỏ, URL đầy đủ, người làm và hạn.
- [ ] File bàn giao content `{{CLIENT}}_qp-handoff-content_v{{N}}.md` đã sinh cùng version.
- [ ] Flags ghi đủ điểm cần GSC, cần kiểm chéo.
- [ ] Tự chấm đạt ngưỡng PASS.
- [ ] `index.md` bảng D có dòng cho JSON, HTML, hồ sơ; `log.md` có entry.
