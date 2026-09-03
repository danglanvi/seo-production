# Cluster map — template output + quy tắc gom + chấm ổn định + verdict coverage

> Reference cho Bước 3-4-6 của `geo-fanout-research`.

## 1. Quy tắc gom cluster (≤4/query)

1. Gom theo **facet của intent** user (họ muốn *hiểu · chọn · làm · tin* điều gì), không theo từ trùng nhau. Hai sub-query dùng từ khác nhau nhưng cùng facet → cùng cluster.
2. Trần **4 cluster/query**. Nếu >4: (a) gộp cluster có <2 sub-query vào cluster gần nhất; (b) cluster chỉ toàn sub-query `volatile`/`seed` → hạ thành "quan sát thêm"; (c) cluster **ngoài Central Search Intent** của topic → chuyển sang mục "cluster lân cận" (ứng viên page khác), không tính vào 4.
3. Mỗi cluster đặt **1 câu hỏi đại diện** bằng ngôn ngữ user — đây là ứng viên heading (K2Q) cho outline.
4. Nhiều query cùng topic → cluster có thể dùng chung; ghi cluster chung 1 lần, liệt kê query nào tách ra nó.

## 2. Chấm ổn định (khi có Path A/B ≥3 lần chạy)

| Nhãn | Định nghĩa | Dùng để |
|---|---|---|
| ● **stable** | xuất hiện ≥2/3 lần chạy (khác phiên/ngày/wording) hoặc có trong cả PAA lẫn AI answer | Ưu tiên heading + passage |
| ○ **volatile** | 1/3 lần | Cover bằng câu/đoạn trong passage stable, không mở heading riêng |
| ◌ **seed** | chỉ từ lens, chưa có evidence | Chờ evidence; không tính coverage |
| ⚑ **simulated** | toàn bộ map từ Path C | Chỉ tìm gap sơ bộ; không đưa vào báo cáo khách |

Tỷ lệ stable/tổng của một query = "độ chắc" của map; <30% stable → ghi "fan-out topic này biến động, đo lại sau 2-4 tuần" thay vì kết luận.

## 3. Verdict coverage (Bước 4)

| Verdict | Điều kiện | Việc kế tiếp |
|---|---|---|
| **COVERED** | Có page phụ trách + heading khớp/gần + passage tự đứng (câu đầu sau heading = answer, không hồi chỉ) | Giữ; kiểm AX7 title/meta chứa từ vựng cluster |
| **GAP-HEADING** | Page đúng CSI nhưng thiếu heading/passage cho cluster | Đề xuất heading K2Q + Subordinate Text (40-75 từ) → outline/AM hoặc `geo-content-optimization` rewrite |
| **GAP-PAGE** | Không page nào trong network phụ trách | Đề xuất mức theo QDP (page nếu ≥3/4 tiêu chí: entity khác · demand · pattern query rõ · similarity thấp; heading nếu 2/4; sentence nếu ≤1/4) — rubric `keyword-topic-url-mapping/references/qdp-gate.md`; quyết định thuộc topical map |
| **OUT-OF-SCOPE** | Cluster lân cận ngoài CSI | Ghi vào topical map backlog, không nhồi vào page hiện có |

## 4. Template file output

```markdown
# Fan-out Cluster Map — <topic>
> Queries: <q1; q2; …> · Market/ngôn ngữ: <VN/EN> · Engine: <AI Mode / AIO / ChatGPT> · Evidence: <Path A/B/C; simulated?> · Ngày đo + model version: <dd/mm/yyyy · gpt-x / AI Mode> · Số lần chạy: <n> · Tỷ lệ stable: <x%>

## 1. Cluster map
| # | Cluster (facet) | Câu hỏi đại diện | Sub-query (●/○/◌) | Query tách ra | Nguồn AI đang cite |
|---|---|---|---|---|---|
| C1 | Hiểu | … | ● …; ● …; ○ … | q1, q2 | domain-a, domain-b |
| C2 | Chọn & giá | … | … | … | … |
| C3 | Làm | … | … | … | … |
| C4 | Tin | … | … | … | … |

## 2. Cluster lân cận (ngoài CSI)
| Cluster | Câu hỏi đại diện | Ứng viên page (QDP đề xuất) |

## 3. Coverage map (khi có $PAGES)
| Cluster | Page phụ trách | Heading khớp (khớp/gần/lệch) | Passage tự đứng? | Title/meta có từ vựng cluster? (AX7) | Verdict |

## 4. Gap + đề xuất
- GAP-HEADING: <cluster → heading K2Q đề xuất + Subordinate Text>
- GAP-PAGE: <cluster → mức QDP đề xuất + lý do>
- AX7: <page → title/meta/slug cần thêm từ vựng cluster nào>

## 5. AIO counter-positioning seed (nếu có $AI_ANSWERS)
| Fact AI đang nêu | Nguồn được cite | Fact bỏ sót (nguồn đáng tin + năm) | Format AI ưa |

## 6. Bàn giao
- → `semantic-outline-methodology` v2.1 Step 2 (cluster → heading; cluster ngoài CSI → QDP)
- → `geo-content-optimization` v1.2 Bước 3-4 (audit + rewrite theo cluster; seed counter-positioning)
- → `topical-map-creation` v2.2 Step 10b (gap theo cluster)
- Đo lại: 2-4 tuần hoặc khi model đổi phiên bản

## Nguồn số liệu + hạn dùng
- ~90% fan-out gom ≤4 cluster · ~27% sub-query ổn định — Batch 40 wiki 08/2026 (A cơ chế Google AI Mode; tỷ lệ = quan sát)
- Coverage ở cấp network, 26-50% subtopic thắng 100% — Indig × AirOps 04/2026, 815k cặp (B)
- `site:` 64% fan-out branded — Nectiv 13/08/2026, n≈4K (B/C)
- Cổng lọc title+meta+URL — McSweeney/QueryBurst 12/2025 (≈ ước tính đơn nguồn)
- Hạn dùng: 31/10/2026 (register v2026.08)
```

## 5. Luật phát hành

Deliverable gửi khách: chỉ bảng cluster + coverage + gap; **không** in số fan-out tuyệt đối, không in cosine, không in "simulated" map như số đo. Mọi số kèm nguồn + tháng theo whitelist `wiki/syntheses/geo-evidence-register-2026-08`.
